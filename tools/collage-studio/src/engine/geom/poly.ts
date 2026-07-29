// src/engine/geom/poly.ts
// -----------------------------------------------------------------------------
// POLYGON WORKHORSES — the shared substrate every generator in ./generators
// stands on. No dependencies: the repo has no geometry library and is not
// getting one.
//
// WHY A TRUE INSET MATTERS (and why the old gutter looked cheap)
//   `primitives.ts` insets a cell by scaling its ring toward the centroid:
//       p' = c + (p - c) * (1 - gutter*4)
//   That is a SIMILARITY, so the gap it opens is PROPORTIONAL TO CELL SIZE. A
//   layout with a 4x scale hierarchy therefore gets 4x-wider gutters around its
//   big cells than its small ones, and the eye reads inconsistent gutters as
//   sloppy long before it can name why. Every printed collage, every magazine
//   grid, every mosaic uses a CONSTANT gutter.
//
//   `insetPolygon` below offsets each EDGE inward by a fixed pixel distance
//   along its own normal and re-intersects the half-planes. For a convex ring
//   that is exact. For a concave one it is a good approximation that never
//   self-intersects, because clipping is monotone: the result is always a
//   subset of the input. Cells that would vanish return null and the caller
//   drops them, which is the correct behaviour — a cell thinner than the gutter
//   is not a cell.
// -----------------------------------------------------------------------------

import type { LayoutItem, Point, Rect } from '../../types';

export const TAU = Math.PI * 2;
/** The golden ratio. Used by phyllotaxis, Penrose deflation and golden subdivision. */
export const PHI = (1 + Math.sqrt(5)) / 2;
/** 137.50776405003785° in radians — the golden angle. The sunflower constant. */
export const GOLDEN_ANGLE = TAU / (PHI * PHI);

// =============================================================================
// BASIC MEASURES
// =============================================================================

/** Signed area (shoelace). Positive when the ring winds counter-clockwise in a
 *  y-down screen space... which is CLOCKWISE to a human. Sign is only used for
 *  orientation normalisation, so the convention just has to be consistent. */
export const signedArea = (poly: Point[]): number => {
  let a = 0;
  for (let i = 0, n = poly.length; i < n; i++) {
    const p = poly[i];
    const q = poly[(i + 1) % n];
    a += p.x * q.y - q.x * p.y;
  }
  return a / 2;
};

export const polygonArea = (poly: Point[]): number => Math.abs(signedArea(poly));

/** Area-weighted centroid — NOT the vertex mean. For an L-shape or a long thin
 *  shard the vertex mean can sit outside the polygon entirely, which puts the
 *  smart-crop anchor in the wrong place and insets the ring lopsidedly. */
export const centroid = (poly: Point[]): Point => {
  const a = signedArea(poly);
  if (Math.abs(a) < 1e-9) {
    // Degenerate (collinear) ring: fall back to the vertex mean.
    let sx = 0, sy = 0;
    for (const p of poly) { sx += p.x; sy += p.y; }
    return { x: sx / poly.length, y: sy / poly.length };
  }
  let cx = 0, cy = 0;
  for (let i = 0, n = poly.length; i < n; i++) {
    const p = poly[i];
    const q = poly[(i + 1) % n];
    const cross = p.x * q.y - q.x * p.y;
    cx += (p.x + q.x) * cross;
    cy += (p.y + q.y) * cross;
  }
  return { x: cx / (6 * a), y: cy / (6 * a) };
};

export const boundsOf = (poly: Point[]): Rect => {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const p of poly) {
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
  }
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
};

/** Ensure a consistent winding so edge normals all point the same way. */
export const orient = (poly: Point[]): Point[] =>
  signedArea(poly) < 0 ? poly.slice().reverse() : poly;

// =============================================================================
// HALF-PLANE CLIPPING — the single most load-bearing routine here
// =============================================================================

/**
 * Sutherland–Hodgman clip of `poly` against the half-plane
 *   { p : (p - a) · n <= 0 }
 * `n` need not be normalised for the INSIDE test, but `clipToHalfPlane` is also
 * used with an offset distance, so callers that care pass a unit normal.
 *
 * Convex clip regions compose: intersecting N half-planes in sequence yields the
 * exact intersection, which is how Voronoi cells and polygon insets are built.
 */
export const clipToHalfPlane = (poly: Point[], a: Point, n: Point): Point[] => {
  if (poly.length < 3) return [];
  const out: Point[] = [];
  const side = (p: Point) => (p.x - a.x) * n.x + (p.y - a.y) * n.y;

  for (let i = 0, len = poly.length; i < len; i++) {
    const cur = poly[i];
    const nxt = poly[(i + 1) % len];
    const dc = side(cur);
    const dn = side(nxt);
    const curIn = dc <= 0;
    const nxtIn = dn <= 0;

    if (curIn) out.push(cur);
    if (curIn !== nxtIn) {
      const denom = dc - dn;
      // Parallel-to-plane edges have denom ~ 0; skipping them is correct
      // because both endpoints are then effectively on the boundary.
      if (Math.abs(denom) > 1e-12) {
        const t = dc / denom;
        out.push({ x: cur.x + (nxt.x - cur.x) * t, y: cur.y + (nxt.y - cur.y) * t });
      }
    }
  }
  return out.length >= 3 ? out : [];
};

/** Clip to the axis-aligned frame. Generators are allowed to overshoot the
 *  canvas deliberately (that is how you get edge-to-edge bleed with no dead
 *  corners); this is what brings them back. */
export const clipToRect = (poly: Point[], W: number, H: number, pad = 0): Point[] => {
  let p = poly;
  p = clipToHalfPlane(p, { x: -pad, y: 0 }, { x: -1, y: 0 });
  p = clipToHalfPlane(p, { x: W + pad, y: 0 }, { x: 1, y: 0 });
  p = clipToHalfPlane(p, { x: 0, y: -pad }, { x: 0, y: -1 });
  p = clipToHalfPlane(p, { x: 0, y: H + pad }, { x: 0, y: 1 });
  return p;
};

/**
 * TRUE INWARD OFFSET by a constant distance `d` in pixels.
 *
 * IMPLEMENTED AS A VERTEX BISECTOR OFFSET, NOT AS A HALF-PLANE INTERSECTION.
 *
 * The intersect-every-edge-half-plane version is exact — for CONVEX rings, and
 * only those. Feed it a concave ring and it silently returns the inset of a
 * shape the caller never asked for, or nothing at all: each edge of a concave
 * arc contributes a half-plane that slices away the far side of the polygon, so
 * an annular sector (kaleidoscope, mandala, lotus petals) or an arc band
 * (Truchet) collapses to a sliver or to empty.
 *
 * That defect was invisible in the cell COUNT — the generators still returned
 * ~48 cells — and only showed up once coverage was measured: kaleidoscope 58%,
 * mandala 52%, Truchet 34% of the frame painted, with black annuli where the
 * concave cells used to be.
 *
 * Moving each vertex along its own angle bisector by d/sin(θ/2) is the standard
 * offset and is correct for reflex vertices too (they move outward relative to
 * the ring, which is what keeps a concave boundary parallel to itself). It can
 * self-intersect when d approaches the feature size, so the caller clamps d
 * against the cell's own thickness and the area check below rejects anything
 * that inverted.
 */
export const insetPolygon = (poly: Point[], d: number): Point[] | null => {
  if (d <= 0) return poly.length >= 3 ? poly : null;

  // DEDUPE FIRST — this is not hygiene, it is the correctness fix.
  //
  // `clipToHalfPlane` emits a duplicate vertex whenever an edge lies on the
  // clip plane, which happens constantly in a line-arrangement figure. The
  // offset loop skipped any vertex whose adjacent edge had zero length — and
  // for a duplicated PAIR that skipped BOTH, so the ring lost real corners and
  // folded through itself. The folded ring's shoelake area partially cancels,
  // so it came out SMALLER and passed the "it shrank" check below while being
  // garbage: measured on a Metatron cell of thickness 378px, a 0.756px inset
  // removed 83% of the area.
  const ring0 = orient(poly);
  const ring: Point[] = [];
  for (let i = 0; i < ring0.length; i++) {
    const p = ring0[i];
    const q = ring[ring.length - 1];
    if (!q || Math.hypot(p.x - q.x, p.y - q.y) > 1e-7) ring.push(p);
  }
  // The wrap-around pair can be duplicated too.
  while (ring.length > 1
    && Math.hypot(ring[0].x - ring[ring.length - 1].x, ring[0].y - ring[ring.length - 1].y) <= 1e-7) {
    ring.pop();
  }

  const n = ring.length;
  if (n < 3) return null;
  const before = polygonArea(ring);
  if (before <= 0) return null;

  let perimeter = 0;
  for (let i = 0; i < n; i++) {
    const p = ring[i], q = ring[(i + 1) % n];
    perimeter += Math.hypot(q.x - p.x, q.y - p.y);
  }

  const out: Point[] = [];
  for (let i = 0; i < n; i++) {
    const prev = ring[(i - 1 + n) % n];
    const cur = ring[i];
    const next = ring[(i + 1) % n];

    let e1x = cur.x - prev.x, e1y = cur.y - prev.y;
    let e2x = next.x - cur.x, e2y = next.y - cur.y;
    const l1 = Math.hypot(e1x, e1y);
    const l2 = Math.hypot(e2x, e2y);
    if (l1 < 1e-9 || l2 < 1e-9) continue;      // cannot happen post-dedupe
    e1x /= l1; e1y /= l1; e2x /= l2; e2y /= l2;

    // Inward normals for this winding (`orient` fixes the sign convention).
    const n1x = -e1y, n1y = e1x;
    const n2x = -e2y, n2y = e2x;
    let bx = n1x + n2x, by = n1y + n2y;
    const bl = Math.hypot(bx, by);
    if (bl < 1e-9) {
      // A perfect 180° spike — offset along one normal and move on.
      out.push({ x: cur.x + n1x * d, y: cur.y + n1y * d });
      continue;
    }
    bx /= bl; by /= bl;
    // d / cos(half-angle). Clamped so a needle-sharp corner does not shoot the
    // vertex off to infinity.
    const cosHalf = bx * n1x + by * n1y;
    const step = d / Math.max(0.28, Math.abs(cosHalf));
    out.push({ x: cur.x + bx * step, y: cur.y + by * step });
  }

  if (out.length < 3) return null;
  const after = polygonArea(out);
  if (after <= 0 || after >= before || signedArea(out) * signedArea(ring) < 0) return null;

  // AREA LOSS MUST BE ABOUT d x PERIMETER.
  //
  // To first order an inward offset by d removes exactly a band of width d
  // around the boundary, so `before - after ~ d * P`. A result that loses far
  // more than that has folded through itself — and a folded ring still reports
  // a smaller positive shoelace area, so the checks above cannot see it. This
  // is the assertion that would have caught the duplicate-vertex collapse on
  // its own, rather than it surviving as a 39% hole in the frame.
  const slack = 3 * d * perimeter + 4 * d * d + 1;
  if (before - after > slack) return null;
  return out;
};

/** Does this ring enclose enough pixels to be worth drawing an image into? */
export const isViable = (poly: Point[] | null, minArea: number): poly is Point[] =>
  !!poly && poly.length >= 3 && polygonArea(poly) >= minArea;

// =============================================================================
// CURVES → RINGS
// =============================================================================

/** A circle as a closed polyline. `segments` scales with radius so a large disc
 *  never shows facets and a tiny one never wastes points. */
export const circleRing = (cx: number, cy: number, r: number, segments?: number): Point[] => {
  const n = segments ?? Math.max(12, Math.min(96, Math.round(r * 0.7)));
  const out: Point[] = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * TAU;
    out.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }
  return out;
};

/** Regular n-gon, `rot` in radians. */
export const ngonRing = (cx: number, cy: number, r: number, n: number, rot = 0): Point[] => {
  const out: Point[] = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * TAU + rot;
    out.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }
  return out;
};

/** An annular sector (ring wedge) — the atom of mandalas and kaleidoscopes. */
export const sectorRing = (
  cx: number, cy: number, r0: number, r1: number, a0: number, a1: number,
  steps = Math.max(3, Math.ceil((Math.abs(a1 - a0) / TAU) * 48)),
): Point[] => {
  const out: Point[] = [];
  for (let i = 0; i <= steps; i++) {
    const a = a0 + ((a1 - a0) * i) / steps;
    out.push({ x: cx + Math.cos(a) * r1, y: cy + Math.sin(a) * r1 });
  }
  // r0 === 0 is a pie slice: one apex point, not a degenerate zero-radius arc.
  if (r0 <= 1e-6) {
    out.push({ x: cx, y: cy });
  } else {
    for (let i = steps; i >= 0; i--) {
      const a = a0 + ((a1 - a0) * i) / steps;
      out.push({ x: cx + Math.cos(a) * r0, y: cy + Math.sin(a) * r0 });
    }
  }
  return out;
};

// =============================================================================
// POINT SETS
// =============================================================================

/**
 * Bridson Poisson-disk sampling — blue noise. The reason this exists rather
 * than `rng()` scatter: uniform random points CLUMP (that is what "random"
 * means), and clumped seeds make Voronoi cells with wild area variance and
 * ugly slivers. Blue noise gives the even-but-unstructured spacing that reads
 * as "organic" instead of "noisy".
 */
export const poissonDisk = (
  W: number, H: number, minDist: number, rng: () => number, k = 24,
): Point[] => {
  const cell = minDist / Math.SQRT2;
  const gw = Math.ceil(W / cell);
  const gh = Math.ceil(H / cell);
  const grid: (Point | null)[] = new Array(gw * gh).fill(null);
  const pts: Point[] = [];
  const active: Point[] = [];

  const gridInsert = (p: Point) => {
    const gx = Math.min(gw - 1, Math.max(0, Math.floor(p.x / cell)));
    const gy = Math.min(gh - 1, Math.max(0, Math.floor(p.y / cell)));
    grid[gy * gw + gx] = p;
  };
  const farEnough = (p: Point): boolean => {
    if (p.x < 0 || p.y < 0 || p.x >= W || p.y >= H) return false;
    const gx = Math.floor(p.x / cell);
    const gy = Math.floor(p.y / cell);
    for (let y = Math.max(0, gy - 2); y <= Math.min(gh - 1, gy + 2); y++) {
      for (let x = Math.max(0, gx - 2); x <= Math.min(gw - 1, gx + 2); x++) {
        const q = grid[y * gw + x];
        if (q && Math.hypot(q.x - p.x, q.y - p.y) < minDist) return false;
      }
    }
    return true;
  };

  const seed = { x: rng() * W, y: rng() * H };
  pts.push(seed); active.push(seed); gridInsert(seed);

  while (active.length) {
    const idx = Math.floor(rng() * active.length);
    const p = active[idx];
    let placed = false;
    for (let i = 0; i < k; i++) {
      const a = rng() * TAU;
      const r = minDist * (1 + rng());
      const c = { x: p.x + Math.cos(a) * r, y: p.y + Math.sin(a) * r };
      if (farEnough(c)) {
        pts.push(c); active.push(c); gridInsert(c);
        placed = true;
        break;
      }
    }
    if (!placed) active.splice(idx, 1);
  }
  return pts;
};

/**
 * Poisson-disk targeted at a COUNT rather than a radius. Bridson takes a
 * spacing, but every generator here is driven by "how many fragments" — so
 * bisect on the radius. 12 iterations lands within a few percent, which is
 * closer than the eye can tell.
 */
export const poissonCount = (
  W: number, H: number, count: number, rng: () => number, seedRng?: () => number,
): Point[] => {
  const target = Math.max(1, count);
  // Area per point, times the packing efficiency Bridson actually achieves.
  let lo = 0.25 * Math.sqrt((W * H) / target);
  let hi = 2.5 * Math.sqrt((W * H) / target);
  let best: Point[] = [];
  for (let i = 0; i < 12; i++) {
    const mid = (lo + hi) / 2;
    // Re-seeding per probe keeps the search deterministic given the same rng
    // stream, instead of consuming a variable number of draws.
    const r = seedRng ?? rng;
    const pts = poissonDisk(W, H, mid, r);
    if (!best.length || Math.abs(pts.length - target) < Math.abs(best.length - target)) best = pts;
    if (pts.length > target) lo = mid; else hi = mid;
    if (pts.length === target) break;
  }
  return best;
};

// =============================================================================
// VORONOI — real ones, by half-plane intersection
// =============================================================================

/**
 * The cell of site i is the intersection of the half-planes bounded by the
 * perpendicular bisector of (site_i, site_j) for every other j. O(n^2) with a
 * tiny constant: at n = 120 that is 14,400 clips of a ~6-gon, roughly a
 * millisecond. A Fortune sweepline would be asymptotically better and far more
 * code, and n here is bounded by "how many fragments fit on a screen".
 *
 * Correct by construction, including at the frame edge — the initial ring IS
 * the frame, so cells are clipped to it for free.
 */
export const voronoiCells = (sites: Point[], W: number, H: number): Point[][] => {
  const frame: Point[] = [{ x: 0, y: 0 }, { x: W, y: 0 }, { x: W, y: H }, { x: 0, y: H }];
  return sites.map((s) => {
    let cell = frame;
    for (const o of sites) {
      if (o === s) continue;
      const dx = o.x - s.x;
      const dy = o.y - s.y;
      const d2 = dx * dx + dy * dy;
      if (d2 < 1e-12) continue;              // coincident sites: skip, not divide by zero
      const mid = { x: (s.x + o.x) / 2, y: (s.y + o.y) / 2 };
      const len = Math.sqrt(d2);
      cell = clipToHalfPlane(cell, mid, { x: dx / len, y: dy / len });
      if (cell.length < 3) break;
    }
    return cell;
  });
};

/**
 * Lloyd relaxation — move each site to its cell's centroid and re-tessellate.
 * This is what turns a blue-noise scatter into the even, honeycomb-tending
 * cells that read as CRAFTED. 1-2 passes keeps organic variety; 6+ converges
 * toward a hexagonal grid, which is the very regularity we are escaping, so
 * callers should stay low.
 */
export const lloydRelax = (
  sites: Point[], W: number, H: number, iterations: number,
): Point[] => {
  let pts = sites;
  for (let i = 0; i < iterations; i++) {
    const cells = voronoiCells(pts, W, H);
    pts = pts.map((p, idx) => {
      const c = cells[idx];
      return c.length >= 3 ? centroid(c) : p;
    });
  }
  return pts;
};

// =============================================================================
// EMISSION
// =============================================================================

let uid = 0;
/** Ids must be unique per layout, and STABLE is not required — Stage caches
 *  Path2D by object identity (a WeakMap), not by id. */
export const nextId = (prefix: string): string => `${prefix}-${uid++}`;

/**
 * The single exit point every generator funnels through: clip to frame, apply
 * the constant-width gutter, drop anything that collapsed, and attach bounds.
 *
 * Callers pass RAW rings in pixel space and never think about gutters again.
 */
export const emit = (
  rings: Point[][],
  W: number,
  H: number,
  gutterPx: number,
  prefix = 'cell',
): LayoutItem[] => {
  const minArea = Math.max(4, (W * H) * 2e-5);
  const out: LayoutItem[] = [];
  for (const raw of rings) {
    if (!raw || raw.length < 3) continue;
    const clipped = clipToRect(raw, W, H);
    if (clipped.length < 3) continue;

    // A CONSTANT gutter is right for cells of similar size and catastrophic for
    // a layout with a wide size range: a 6px inset erases a 10px-wide slit-scan
    // strip, a mandala's inner wedges and a Sri Yantra sliver entirely. Those
    // are not junk cells — they are the fine end of a deliberate hierarchy, and
    // deleting them is how a construction silently loses two thirds of itself.
    //
    // So the gutter is constant UNTIL it would consume the cell, then it scales
    // with the cell. The eye reads the gutters as even everywhere they can be,
    // and thin fragments survive with a proportionally finer gap.
    // Clamp the gutter against the cell's own THICKNESS, measured as 2A/P — the
    // inradius of a shape with the same area-to-perimeter ratio. The bounding
    // box is the wrong measure here: an annular sector or a curve ribbon has a
    // large bbox and a small thickness, so a bbox-derived clamp lets the gutter
    // eat the whole cell. 2A/P is right for exactly those shapes.
    let per = 0;
    for (let i = 0, n = clipped.length; i < n; i++) {
      const p = clipped[i], q = clipped[(i + 1) % n];
      per += Math.hypot(q.x - p.x, q.y - p.y);
    }
    const thickness = per > 1e-6 ? (2 * polygonArea(clipped)) / per : 0;
    // 0.10 rather than 0.34: a slit-scan strip 25px wide loses 40% of itself to
    // a 5px gutter on each side, and the frame reads as a barcode of background.
    // At 0.14 a thin cell keeps a proportional hairline and everything at or
    // above normal cell size is unaffected (the constant gutter still wins).
    const g = Math.min(gutterPx, thickness * 0.10);
    const inset = g > 0.15 ? insetPolygon(clipped, g) : clipped;

    // A CELL TOO THIN TO GUTTER STILL HAS TO BE DRAWN.
    //
    // Dropping it leaves a HOLE in a tiling that was complete — and a hole is
    // far more visible than a missing hairline. Measured on the Metatron
    // arrangement: 100% coverage at gutter 0, but 61% once a sub-pixel gutter
    // erased its thinnest chord slivers. So an inset that fails to leave a
    // viable cell falls back to the un-inset one, and only a cell that is not
    // viable EVEN UNCLIPPED is discarded as genuine junk.
    const path = isViable(inset, minArea) ? inset
      : isViable(clipped, minArea) ? clipped
      : null;
    if (!path) continue;
    out.push({ id: nextId(prefix), path, bounds: boundsOf(path) });
  }
  return out;
};

/**
 * Gutter in pixels from the app's `gutterPercent`.
 *
 * The old code multiplied the percent by width and then by 4 again inside each
 * primitive, so the shipped default drew ~2.4% of every cell as black mortar
 * and the collage read as a leaded window rather than a photograph. Expressing
 * it once, here, at a weight that leaves the IMAGE dominant is the whole point.
 */
export const gutterPx = (W: number, H: number, gutterPercent: number): number =>
  Math.max(0, gutterPercent * Math.min(W, H) * 0.7);

// =============================================================================
// SYMMETRY
// =============================================================================

/**
 * Fold a set of rings through the dihedral group D_n about (cx, cy): n rotations
 * x an optional mirror. This is the machinery behind kaleidoscope, mandala and
 * rosette — design ONE wedge, get the whole disc.
 */
export const dihedral = (
  rings: Point[][], cx: number, cy: number, folds: number, mirror: boolean,
): Point[][] => {
  const out: Point[][] = [];
  for (let k = 0; k < folds; k++) {
    const a = (k / folds) * TAU;
    const ca = Math.cos(a);
    const sa = Math.sin(a);
    for (const ring of rings) {
      out.push(ring.map((p) => {
        const dx = p.x - cx;
        const dy = p.y - cy;
        return { x: cx + dx * ca - dy * sa, y: cy + dx * sa + dy * ca };
      }));
      if (mirror) {
        out.push(ring.map((p) => {
          // Reflect across the wedge bisector, THEN rotate into place.
          const dx = p.x - cx;
          const dy = -(p.y - cy);
          return { x: cx + dx * ca - dy * sa, y: cy + dx * sa + dy * ca };
        }));
      }
    }
  }
  return out;
};

export const rotateRing = (ring: Point[], cx: number, cy: number, a: number): Point[] => {
  const ca = Math.cos(a);
  const sa = Math.sin(a);
  return ring.map((p) => {
    const dx = p.x - cx;
    const dy = p.y - cy;
    return { x: cx + dx * ca - dy * sa, y: cy + dx * sa + dy * ca };
  });
};

/** The radius that reaches every corner from (cx,cy) — use it to guarantee a
 *  radial construction bleeds past the frame instead of leaving dead corners. */
export const coverRadius = (W: number, H: number, cx: number, cy: number): number =>
  Math.max(
    Math.hypot(cx, cy), Math.hypot(W - cx, cy),
    Math.hypot(cx, H - cy), Math.hypot(W - cx, H - cy),
  );
