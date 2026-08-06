/**
 * Invariant sweep for ONE LAYOUT — the preview's partition IS the export's.
 *
 * Run: node tests/unit/oneLayout.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * it proves the shipped `lib/layout.computeLayout` and `lib/layoutScale` — not a
 * re-implementation of them.
 *
 * THE INVARIANT THAT MATTERS — SCALE INVARIANCE:
 *
 *   Every render path asks for the same composition at a different size: the
 *   preview at 1200, the live Stage in 1200-space, the raster export at its tier
 *   width (2727, 5455, …), the SVG export at 1000. They all pair POSITIONALLY —
 *   slot i draws into cell i — so if the cells at one width are not the cells at
 *   another, scaled, then the photo, the crop focus and the twist that were
 *   chosen for a rectangle on screen are applied to a different rectangle in the
 *   file. Everything else in this sweep is secondary to I1.
 *
 * THE ORACLE IS THE OLD CODE ITSELF. `computeAtBasis` is the whole of what
 * `computeLayout` used to be, exported unchanged, so I3 measures the real
 * historical divergence rate rather than a story about it — and then measures
 * the same thing through the wrapper and requires zero.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

const load = async (rel, tag) => {
  const out = join(mkdtempSync(join(tmpdir(), `${tag}-`)), `${tag}.mjs`);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: out,
    bundle: true,
    format: 'esm',
    platform: 'neutral',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const { computeLayout, computeAtBasis, createRng } = await load('src/lib/layout.ts', 'layout');
const { LAYOUT_BASIS_W, basisFor, scaleLayout } = await load('src/lib/layoutScale.ts', 'layoutScale');
const { GENERATORS } = await load('src/engine/geom/generators/index.ts', 'generators');
const { dimsForTier, DEFAULT_TIER_PRESETS } = await load('src/lib/exportLimits.ts', 'exportLimits');

// --- assertions --------------------------------------------------------------

let pass = 0;
const failures = [];
const ok = (name, cond, detail) => {
  if (cond) { pass++; return; }
  failures.push(`${name}${detail !== undefined ? ` — ${JSON.stringify(detail)}` : ''}`);
};

// --- the sizes the app actually renders at -----------------------------------
//
// Not round numbers picked for the test: 1200 is PREVIEW_W and the Stage's
// DEFAULT_LOGICAL_W, 1000 is the SVG export's hardcoded width, and the rest come
// from exportLimits.dimsForTier at aspect 0.666 (2048/4096/8192 tiers). A sweep
// over widths the app never uses would prove a weaker thing.
const ASPECTS = [0.666, 1, 1.7778, 0.5625];

/**
 * THE SIZES THE APP ACTUALLY RENDERS AT, taken from the app rather than invented:
 * 1200 is PREVIEW_W and the Stage's DEFAULT_LOGICAL_W, 1000x(1000/aspect) is the
 * SVG export, and the rest come straight out of `exportLimits.dimsForTier` —
 * WHOLE-PIXEL dimensions whose aspect is therefore NOT the preview's (the 4096
 * tier at 0.666 is 2727x4094 = 0.66610). Sweeping only over `W/aspect` would
 * miss exactly the case that broke the first version of this fix.
 */
const sizesFor = (aspect) => {
  const out = [
    { W: LAYOUT_BASIS_W, H: LAYOUT_BASIS_W / aspect, label: 'preview 1200' },
    { W: 1000, H: 1000 / aspect, label: 'svg 1000' },
  ];
  for (const tier of DEFAULT_TIER_PRESETS) {
    const d = dimsForTier(tier, aspect);
    if (d && d.w > 0 && d.h > 0 && d.w <= 9000) out.push({ W: d.w, H: d.h, label: `tier ${tier} -> ${d.w}x${d.h}` });
  }
  return out;
};

const modesUnderTest = () => {
  const gens = GENERATORS.map((g) => ({ mode: g.id, primitive: 'rect', label: g.id }));
  // The five pre-roster modes still reachable from a saved project. `stencil`
  // needs decoded image data and a canvas, so it cannot run here — NAMED, not
  // silently dropped (it is layout-derived-from-content and gets its coverage
  // from the e2e, which drives the real app).
  const legacy = [
    { mode: 'minimal', primitive: 'rect', label: 'legacy:minimal/rect' },
    { mode: 'minimal', primitive: 'tri', label: 'legacy:minimal/tri' },
    { mode: 'minimal', primitive: 'circle', label: 'legacy:minimal/circle' },
    { mode: 'minimal', primitive: 'octagon', label: 'legacy:minimal/octagon' },
    { mode: 'balanced', primitive: 'rect', label: 'legacy:balanced/rect' },
    { mode: 'complex', primitive: 'rect', label: 'legacy:complex' },
    { mode: 'field', primitive: 'rect', label: 'legacy:field' },
  ];
  return [...gens, ...legacy];
};

// --- geometry helpers --------------------------------------------------------

/** Normalised vertices: geometry expressed as a fraction of the canvas. */
const norm = (items, W, H) =>
  items.map((it) => ({
    path: (it.path || []).map((p) => [p.x / W, p.y / H]),
    bounds: it.bounds ? [it.bounds.x / W, it.bounds.y / H, it.bounds.w / W, it.bounds.h / H] : null,
  }));

const centroid = (poly) => {
  if (!poly.length) return [0, 0];
  let x = 0, y = 0;
  for (const p of poly) { x += p[0]; y += p[1]; }
  return [x / poly.length, y / poly.length];
};

/** Largest normalised vertex disagreement between two layouts. Infinity if shaped differently. */
const maxVertexDelta = (a, b) => {
  if (a.length !== b.length) return Infinity;
  let worst = 0;
  for (let i = 0; i < a.length; i++) {
    if (a[i].path.length !== b[i].path.length) return Infinity;
    for (let k = 0; k < a[i].path.length; k++) {
      worst = Math.max(worst, Math.abs(a[i].path[k][0] - b[i].path[k][0]),
                              Math.abs(a[i].path[k][1] - b[i].path[k][1]));
    }
  }
  return worst;
};

/** Largest normalised centroid movement — "does slot i address the same rectangle". */
const maxCentroidDrift = (a, b) => {
  const n = Math.min(a.length, b.length);
  let worst = a.length === b.length ? 0 : 1;
  for (let i = 0; i < n; i++) {
    const [ax, ay] = centroid(a[i].path);
    const [bx, by] = centroid(b[i].path);
    worst = Math.max(worst, Math.hypot(ax - bx, ay - by));
  }
  return worst;
};

const polyArea = (poly) => {
  let s = 0;
  for (let i = 0, n = poly.length; i < n; i++) {
    const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % n];
    s += x1 * y2 - x2 * y1;
  }
  return Math.abs(s) / 2;
};

const coverage = (items) => items.reduce((s, it) => s + polyArea(it.path), 0);

const run = (mode, primitive, W, H, count, seed, viaWrapper = true, aspect = undefined) => {
  const fn = viaWrapper ? computeLayout : computeAtBasis;
  return fn(W, H, count, createRng(seed), mode, 0.005, 0.5, [], primitive, 0, aspect);
};

/** Geometry only. `id` is excluded on purpose — see I2b. */
const geom = (items) => JSON.stringify(items.map((it) => [it.path, it.bounds]));

// =============================================================================
// I1  SCALE INVARIANCE — the rung itself.
//     The layout at any render width is the basis layout, scaled. Asserted on
//     NORMALISED vertices at 1e-12, which is ~9 orders of magnitude tighter than
//     the drift the old code produced and still far above double rounding.
// =============================================================================
{
  const SEEDS = [1, 7, 12345, 99991, 2026080601];
  const COUNTS = [12, 24, 40];
  let checked = 0, worstOverall = 0, worstWhere = null;
  const skipped = [];

  for (const spec of modesUnderTest()) {
    for (const aspect of ASPECTS) {
      const sizes = sizesFor(aspect);
      for (const count of COUNTS) {
        for (const seed of SEEDS) {
          let base;
          try {
            base = await run(spec.mode, spec.primitive, LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect, count, seed, true, aspect);
          } catch (e) {
            skipped.push(`${spec.label}@${aspect}: ${e.message}`);
            continue;
          }
          const nb = norm(base, LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect);
          for (const sz of sizes) {
            const at = await run(spec.mode, spec.primitive, sz.W, sz.H, count, seed, true, aspect);
            const d = maxVertexDelta(nb, norm(at, sz.W, sz.H));
            checked++;
            if (d > worstOverall) { worstOverall = d; worstWhere = `${spec.label} a=${aspect} n=${count} s=${seed} ${sz.label}`; }
          }
        }
      }
    }
  }
  ok('I1 scale invariance: every render size is the basis layout scaled',
      worstOverall <= 1e-12, { checked, worstOverall: String(worstOverall), worstWhere });
  ok('I1b the sweep actually ran the whole roster at every real size', checked >= 3000, { checked });
  if (skipped.length) console.log(`  note: ${skipped.length} generator/aspect pairs threw and were skipped:\n   - ${skipped.slice(0, 6).join('\n   - ')}`);
}

// =============================================================================
// I2  THE PREVIEW DOES NOT MOVE — the compatibility decision, proved.
//     At the preview width the wrapper must be a literal no-op: same generator,
//     same arguments, same floats. If this fails, every saved project and every
//     share code in a chat log opens on a different composition.
// =============================================================================
{
  let checked = 0, mismatch = null, idsDiffered = 0;
  for (const spec of modesUnderTest()) {
    for (const aspect of ASPECTS) {
      for (const seed of [3, 777, 20260806]) {
        const H = LAYOUT_BASIS_W / aspect;
        let viaWrapper, viaLegacy;
        try {
          viaWrapper = await run(spec.mode, spec.primitive, LAYOUT_BASIS_W, H, 24, seed, true, aspect);
          viaLegacy  = await run(spec.mode, spec.primitive, LAYOUT_BASIS_W, H, 24, seed, false);
        } catch { continue; }
        checked++;
        if (geom(viaWrapper) !== geom(viaLegacy) && !mismatch) mismatch = `${spec.label} a=${aspect} s=${seed}`;
        if (JSON.stringify(viaWrapper) !== JSON.stringify(viaLegacy)) idsDiffered++;
      }
    }
  }
  ok('I2 at PREVIEW_W the wrapper is bit-identical to the pre-fix geometry',
      mismatch === null && checked > 100, { checked, mismatch });

  // I2b — A PRE-EXISTING FINDING, RECORDED RATHER THAN HIDDEN.
  //   Some generators (`shards`, and anything else minting ids from a
  //   module-level counter) return `shd-0…` on one call and `shd-24…` on the
  //   next, for identical geometry. Nothing keys off `LayoutItem.id` today —
  //   every consumer and the React key use the ARRAY INDEX — so it is inert,
  //   and it is asserted here so that the day something does key off it, this
  //   line is already on the record instead of being rediscovered as a bug.
  ok('I2b LayoutItem.id is a counter, not a function of the layout (inert today)',
      idsDiffered > 0, { idsDiffered, checked });
}

// =============================================================================
// I3  THE DEFECT WAS REAL, AND IT IS CLOSED.
//     Measure the historical divergence with the historical function, then the
//     same measurement through the wrapper. A fix that cannot show the bug it
//     fixed is a story.
// =============================================================================
{
  const SEEDS = Array.from({ length: 200 }, (_, i) => 1000 + i * 7);
  const aspect = 0.666;
  const EXPORT_W = 2727;            // the 4096 tier at the default aspect
  const DIVERGED = 0.02;            // 2% of the canvas — visible, not rounding

  const EXPORT_H = dimsForTier(4096, aspect).h;   // 4094 — whole pixels, so NOT 2727/0.666

  const rate = async (count, viaWrapper) => {
    let bad = 0, worst = 0;
    for (const seed of SEEDS) {
      const base = await run('minimal', 'rect', LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect, count, seed, viaWrapper, aspect);
      const at = await run('minimal', 'rect', EXPORT_W, EXPORT_H, count, seed, viaWrapper, aspect);
      const d = maxCentroidDrift(norm(base, LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect), norm(at, EXPORT_W, EXPORT_H));
      if (d > DIVERGED) bad++;
      worst = Math.max(worst, d);
    }
    return { rate: bad / SEEDS.length, worst };
  };

  const old24 = await rate(24, false);
  const old40 = await rate(40, false);
  const new24 = await rate(24, true);
  const new40 = await rate(40, true);

  console.log(`  I3 divergence, preview(1200) vs export(${EXPORT_W}), 200 seeds:`);
  console.log(`     pre-fix  count=24 ${(old24.rate * 100).toFixed(1)}% (worst drift ${old24.worst.toFixed(3)})`);
  console.log(`     pre-fix  count=40 ${(old40.rate * 100).toFixed(1)}% (worst drift ${old40.worst.toFixed(3)})`);
  console.log(`     post-fix count=24 ${(new24.rate * 100).toFixed(1)}% (worst drift ${new24.worst.toExponential(2)})`);
  console.log(`     post-fix count=40 ${(new40.rate * 100).toFixed(1)}% (worst drift ${new40.worst.toExponential(2)})`);

  ok('I3a the pre-fix divergence is real and substantial at count=24', old24.rate > 0.05, old24);
  ok('I3b the pre-fix divergence is worse at count=40', old40.rate > old24.rate, { old24: old24.rate, old40: old40.rate });
  ok('I3c pre-fix, some seed re-pairs a slot across the canvas', old40.worst > 0.3, old40);
  ok('I3d post-fix the divergence is GONE at count=24', new24.rate === 0 && new24.worst < 1e-12, new24);
  ok('I3e post-fix the divergence is GONE at count=40', new40.rate === 0 && new40.worst < 1e-12, new40);
}

// =============================================================================
// I4  THE CELL COUNT DOES NOT DEPEND ON THE RENDER WIDTH.
//     A generator with any absolute pixel threshold emits a different NUMBER of
//     cells at 2727 than at 1200. Slots are allocated against the preview's
//     count, so a shorter export layout drops fragments off the end of the
//     collage and a longer one paints them background.
// =============================================================================
{
  let checked = 0, bad = [];
  for (const spec of modesUnderTest()) {
    for (const seed of [5, 4242]) {
      for (const count of [24, 40]) {
        const aspect = 0.666;
        let base;
        try { base = await run(spec.mode, spec.primitive, LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect, count, seed, true, aspect); }
        catch { continue; }
        for (const sz of sizesFor(aspect)) {
          const at = await run(spec.mode, spec.primitive, sz.W, sz.H, count, seed, true, aspect);
          checked++;
          if (at.length !== base.length && bad.length < 5) bad.push(`${spec.label} s=${seed} n=${count} ${sz.label}: ${base.length} -> ${at.length}`);
        }
      }
    }
  }
  ok('I4 cell count is render-size-independent', bad.length === 0 && checked > 400, { checked, bad });
}

// =============================================================================
// I5  NOTHING DEGENERATES UNDER THE SCALE.
//     In bounds, positive extents, finite coordinates, coverage preserved.
// =============================================================================
{
  let checked = 0, oob = 0, degenerate = 0, nonFinite = 0, coverageDrift = 0;
  const aspect = 1.7778;
  for (const spec of modesUnderTest()) {
    for (const seed of [11, 8080]) {
      let base;
      try { base = await run(spec.mode, spec.primitive, LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect, 24, seed, true, aspect); }
      catch { continue; }
      const baseCov = coverage(norm(base, LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect));
      for (const sz of sizesFor(aspect)) {
        const at = await run(spec.mode, spec.primitive, sz.W, sz.H, 24, seed, true, aspect);
        checked++;
        coverageDrift = Math.max(coverageDrift, Math.abs(coverage(norm(at, sz.W, sz.H)) - baseCov));
        for (const it of at) {
          for (const p of it.path || []) {
            if (!Number.isFinite(p.x) || !Number.isFinite(p.y)) nonFinite++;
            // Generators are allowed to bleed slightly past the frame (the
            // canvas clips); 2% is the historical slack, not a new licence.
            else if (p.x < -0.02 * sz.W || p.x > 1.02 * sz.W || p.y < -0.02 * sz.H || p.y > 1.02 * sz.H) oob++;
          }
          if (it.bounds && (!(it.bounds.w > 0) || !(it.bounds.h > 0))) degenerate++;
        }
      }
    }
  }
  ok('I5a every scaled vertex is finite', nonFinite === 0, { nonFinite });
  ok('I5b nothing escapes the frame that did not escape it at basis', oob === 0, { oob, checked });
  ok('I5c no cell collapses to zero extent', degenerate === 0, { degenerate });
  // Whole-pixel export dims mean the target aspect differs from the basis by up
  // to ~1.5e-4, so normalised coverage moves by about that much. It is asserted
  // TIGHT (1e-3) rather than exact, because claiming exactness here would be a
  // lie about what non-uniform scaling does.
  ok('I5d normalised coverage is preserved to the pixel-rounding of the canvas', coverageDrift < 1e-3, { coverageDrift });
}

// =============================================================================
// I6  scaleLayout / basisFor — the pure surface, including the identity path
//     and the degenerate inputs a broken caller can hand it.
// =============================================================================
{
  const items = [{ id: 'c0', path: [{ x: 1, y: 2 }, { x: 3, y: 4 }], bounds: { x: 1, y: 2, w: 2, h: 2 } }];
  ok('I6a scaleLayout(1,1) returns the SAME array, no allocation', scaleLayout(items, 1, 1) === items);
  const two = scaleLayout(items, 2, 3);
  ok('I6b scaleLayout applies x and y independently to path and bounds',
      two[0].path[1].x === 6 && two[0].path[1].y === 12 && two[0].bounds.w === 4 && two[0].bounds.h === 6);
  ok('I6c scaleLayout carries id through', two[0].id === 'c0');
  ok('I6d scaleLayout does not mutate its input', items[0].path[1].x === 3 && items[0].bounds.h === 2);

  const aspect = 0.666;
  const b = basisFor(2727, 4094, aspect);   // the real 4096-tier canvas
  ok('I6e basisFor pins the basis width', b.W0 === LAYOUT_BASIS_W);
  ok('I6f the basis height is the PREVIEW\'s own float, not a re-derivation',
      Object.is(b.H0, LAYOUT_BASIS_W / aspect), { H0: b.H0, preview: LAYOUT_BASIS_W / aspect });
  ok('I6g both factors land the basis exactly on the requested canvas',
      Math.abs(b.W0 * b.sx - 2727) < 1e-9 && Math.abs(b.H0 * b.sy - 4094) < 1e-9, b);
  ok('I6h the two factors differ only by the canvas\'s pixel rounding',
      Math.abs(b.sx / b.sy - 1) < 5e-4, { sx: b.sx, sy: b.sy, ratio: b.sx / b.sy });

  const id = basisFor(LAYOUT_BASIS_W, LAYOUT_BASIS_W / aspect, aspect);
  ok('I6i at PREVIEW_W both scale factors are exactly 1',
      id.sx === 1 && id.sy === 1 && Object.is(id.H0, LAYOUT_BASIS_W / aspect));

  // THE ULP CASE THAT BROKE THE FIRST VERSION OF THIS FIX. Deriving the basis
  // height as H/(W/1200) gave 1801.8018018018015 at W=1364 where the preview
  // has ...017 — two doubles apart, and `metatron` answered 45 cells at one and
  // 39 at the other. With the aspect passed, every width yields ONE float.
  const heights = new Set([1000, 1200, 1364, 2727, 5455].map((W) => basisFor(W, W / aspect, aspect).H0));
  ok('I6j the basis height is ONE float at every render width', heights.size === 1, [...heights]);

  // The no-aspect fallback must at least be self-consistent across widths.
  const fb = new Set([1000, 1200, 2727].map((W) => basisFor(W, W / aspect).H0));
  ok('I6k without an aspect the quantised fallback is still one float', fb.size === 1, [...fb]);

  for (const [W, H] of [[0, 100], [-5, 100], [NaN, 100], [Infinity, 100], [100, 0], [100, NaN]]) {
    const d = basisFor(W, H, aspect);
    ok(`I6l degenerate basisFor(${W},${H}) passes through unscaled`, d.sx === 1 && d.sy === 1 && Object.is(d.W0, W));
  }
  for (const bad of [0, -1, NaN, Infinity]) {
    const d = basisFor(2727, 4094, bad);
    ok(`I6m a nonsense aspect (${bad}) falls back instead of throwing`, Number.isFinite(d.H0) && d.H0 > 0, d);
  }
}

// =============================================================================
// I7  THE KEY-SET GUARD.
//     scaleLayout scales `path` and `bounds`. A LayoutItem that grows a third
//     geometric field (a radius, a centre, a control point) would keep
//     preview-space units at export size and draw in the wrong place. This turns
//     that day's commit red instead of shipping it.
// =============================================================================
{
  const KNOWN = new Set(['path', 'bounds', 'id']);
  const strangers = new Set();
  for (const spec of modesUnderTest()) {
    let items;
    try { items = await run(spec.mode, spec.primitive, LAYOUT_BASIS_W, LAYOUT_BASIS_W / 0.666, 24, 909, true, 0.666); }
    catch { continue; }
    for (const it of items) for (const k of Object.keys(it)) if (!KNOWN.has(k)) strangers.add(`${spec.label}.${k}`);
  }
  ok('I7 no LayoutItem carries a field scaleLayout does not handle',
      strangers.size === 0, [...strangers].slice(0, 8));
}

// =============================================================================

console.log('');
if (failures.length) {
  console.log(`ONE LAYOUT sweep: ${pass} passed, ${failures.length} FAILED`);
  for (const f of failures) console.log(`  ✗ ${f}`);
  process.exit(1);
}
console.log(`ONE LAYOUT sweep: ${pass} invariants passed.`);
