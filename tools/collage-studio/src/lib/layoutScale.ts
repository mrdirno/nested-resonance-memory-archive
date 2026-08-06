import { LayoutItem } from '../types';

/**
 * ONE LAYOUT — the canonical basis every render path shares.
 *
 * THE DEFECT THIS CLOSES. `computeLayout` used to be called at whatever width
 * the caller happened to be drawing at: the preview at 1200, the raster export
 * at its tier width (2727, 5455, …), the SVG export at a hardcoded 1000. The
 * generators are NOT scale-invariant — `generateRects` argmaxes over
 * `w * h * (0.5 + rng())` on FLOORED rectangles, so a near-tie in that argmax
 * resolves differently at a different width and the split lands on a different
 * node. From there the two partitions have nothing to do with each other.
 * MEASURED IN THIS REPO, reproducibly — `tests/unit/oneLayout.invariants.mjs`
 * I3 keeps the pre-fix function as its oracle and runs 200 seeds from the
 * preview's 1200 against the 4096 tier's real 2727x4094: **10.5% of seeds at
 * count=24 and 24.5% at count=40** came back as a genuinely different
 * partition, worst-case normalised centroid drift **1.18** — a slot
 * re-addressed clean across the frame. (The book's earlier 11.3% / 27.7% / 0.87
 * are the same defect measured on a different seed set; cite the sweep, it is
 * the one anybody can re-run.)
 *
 * Everything downstream pairs POSITIONALLY against the preview's cells — the
 * arrangement's photo placement (`arrangeBag`, which has done this since the day
 * arrangement shipped), the crop focus, the twist field — so on those seeds slot
 * *i* addressed one rectangle on screen and a different one in the file.
 *
 * THE FIX. Compute the layout ONCE at a canonical width and scale the result.
 * A uniform scale is exactly the transform the divergence was pretending to be,
 * so after this the export IS the preview, larger.
 *
 * WHY 1200, AND WHY THAT IS THE COMPATIBILITY DECISION. 1200 is `PREVIEW_W`
 * (App.tsx) and `DEFAULT_LOGICAL_W` (stage.ts) — the space the live Stage and
 * the video export already draw in. Pinning the basis there means:
 *
 *   - `s === 1` on the preview path, and `scaleLayout` short-circuits, so the
 *     preview calls the untouched generator with the untouched arguments and
 *     every seed and share code renders BIT-IDENTICALLY to what it rendered
 *     before this change. Nobody's saved project moves.
 *   - the exports move — onto the picture the user was already looking at,
 *     which is the whole point.
 *
 * The alternative (normalise the generators to a unit square and scale up)
 * changes what every existing seed looks like everywhere. Both fix the split;
 * only this one keeps the promise the preview already made.
 */
export const LAYOUT_BASIS_W = 1200;

export interface LayoutBasis {
  /** Width to run the generators at. */
  W0: number;
  /** Height to run them at — `LAYOUT_BASIS_W / aspect`, the preview's own float. */
  H0: number;
  /** Multiply generated x by this to land at the requested width. */
  sx: number;
  /** Multiply generated y by this to land at the requested height. */
  sy: number;
}

/**
 * The basis for a requested render size.
 *
 * TAKE THE ASPECT, DO NOT INFER IT — and the reason is measured, not stylistic:
 *
 *   - Inferring the basis height as `H / (W / 1200)` is off by ULPs. At W=1364
 *     the recovered height is 1801.8018018018015 where the preview's is
 *     ...017. Two doubles apart, geometrically the same number — and `metatron`
 *     returned 45 cells at one and 39 at the other. That is the SAME class of
 *     defect this module exists to remove, reintroduced by the fix, and the
 *     sweep caught it on the first run.
 *   - No quantisation of `W/H` rescues it either, because the raster export does
 *     not render at the preview's aspect at all: `dimsForTier` rounds to whole
 *     pixels, so the 4096 tier at 0.666 is 2727x4094 — an aspect of 0.66610,
 *     0.015% off. Any grid coarse enough to bucket that together with 0.666 is
 *     coarse enough to bucket genuinely different aspects together too.
 *
 * So the caller passes the `aspect` it already has (App.tsx state — the same
 * number the preview divided by), the basis is `1200 x 1200/aspect` for every
 * render path, and the residual 0.015% is absorbed by scaling x and y
 * INDEPENDENTLY. The partition is then identical everywhere and each canvas is
 * still filled exactly to its own edges; the only cost is cell aspect ratios
 * distorted by the amount the export's pixel rounding distorted the canvas —
 * 1.5 parts in ten thousand.
 *
 * Without an aspect (a caller that has not been updated) it falls back to
 * deriving one from `W/H` and quantising to 1e-3. BEST EFFORT ONLY, and the
 * limit is measured, not hedged: at aspect 1.7778 the app's own render sizes
 * straddle a bucket edge once `dimsForTier` floors — 1200/1000/8192-tier land
 * on H0 674.9156, the 4096- and 2048-tiers on 674.5362 — and that is a
 * different partition again. No grid fixes it, because the whole-pixel export
 * canvases genuinely do not share the preview's aspect. The fallback keeps a
 * stray caller from being WORSE than the old code; only passing the aspect
 * makes it right. Every production call site passes it.
 *
 * A degenerate size (non-finite, zero, negative) is passed straight through
 * unscaled. Such a call is already broken; inventing a basis for it would only
 * change WHICH way it is broken.
 */
export const basisFor = (W: number, H: number, aspect?: number): LayoutBasis => {
  const identity = { W0: W, H0: H, sx: 1, sy: 1 };
  if (!Number.isFinite(W) || W <= 0 || !Number.isFinite(H) || H <= 0) return identity;

  const a = Number.isFinite(aspect as number) && (aspect as number) > 0
    ? (aspect as number)
    : Math.round((W / H) * 1e3) / 1e3;
  if (!Number.isFinite(a) || a <= 0) return identity;

  const W0 = LAYOUT_BASIS_W;
  const H0 = W0 / a;
  if (!Number.isFinite(H0) || H0 <= 0) return identity;

  const sx = W / W0;
  const sy = H / H0;
  if (!Number.isFinite(sx) || sx <= 0 || !Number.isFinite(sy) || sy <= 0) return identity;
  return { W0, H0, sx, sy };
};

/**
 * Scale generated geometry onto the requested canvas.
 *
 * Returns the input ARRAY UNTOUCHED when both factors are exactly 1 — not a
 * copy. That is the preview path, it runs on every keystroke, and an identity
 * that allocates a new object graph per fragment is a cost paid forever for
 * nothing. It is also what makes the preview BIT-IDENTICAL to the pre-fix build.
 *
 * `...it` carries `id` and anything added later. NOTE FOR WHOEVER ADDS A FIELD:
 * a new field holding GEOMETRY (a radius, a centre, a control point) must be
 * scaled here or it silently keeps preview-space units at export size. The sweep
 * asserts the key set, so adding one turns the suite red instead of shipping a
 * fragment that draws in the wrong place.
 */
export const scaleLayout = (items: LayoutItem[], sx: number, sy: number): LayoutItem[] => {
  if (sx === 1 && sy === 1) return items;
  return items.map((it) => ({
    ...it,
    path: Array.isArray(it.path) ? it.path.map((p) => ({ x: p.x * sx, y: p.y * sy })) : it.path,
    bounds: it.bounds
      ? { x: it.bounds.x * sx, y: it.bounds.y * sy, w: it.bounds.w * sx, h: it.bounds.h * sy }
      : it.bounds,
  }));
};
