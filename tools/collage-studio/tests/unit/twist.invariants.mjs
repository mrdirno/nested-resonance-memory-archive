/**
 * Invariant sweep for TWIST — the per-fragment lean.
 *
 * Run: node tests/unit/twist.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * it proves the shipped `composition.twistAngle` / `renderer.twistedDest` /
 * `renderer.calculateSmartCrop` — not a re-implementation of them.
 *
 * THE INVARIANT THAT MATTERS — COVERAGE:
 *
 *   The fragments TILE the canvas. Rotating a CELL opens wedges of background
 *   between it and its neighbours, so the rotation is applied to the SAMPLING
 *   inside an untouched clip path instead. That trade only pays if the rotated
 *   drawn rectangle still CONTAINS the axis-aligned cell — otherwise the very
 *   same gap appears, four pixels further in, where it is harder to see and
 *   easier to ship. Every other check here is secondary to that one.
 *
 *   It is asserted geometrically rather than by rendering: map each corner of
 *   the cell back through the inverse of the canvas transform the draw paths
 *   actually apply (translate/rotate/translate about the pivot) and require it
 *   to land inside the destination rectangle those paths actually pass to
 *   drawImage. If the arithmetic in `twistedDest` is wrong in any direction,
 *   some corner escapes.
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

const { TWIST_MODES, TWIST_IDS, MAX_TWIST_RAD, twistAngle, withTwist } =
  await load('src/lib/composition.ts', 'composition');

const { calculateSmartCrop, twistedDest, twistOf } =
  await load('src/lib/renderer.ts', 'renderer');

const { encodeRoll, decodeRoll, rollDice } = await load('src/lib/diceRoll.ts', 'dice');

const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

let fails = 0;
const check = (ok, msg) => { if (!ok) { fails++; console.error(`  ✗ ${msg}`); } };

// --- fixtures ----------------------------------------------------------------

/** Cell boxes across the shapes a generator actually produces: wide, tall, square, tiny. */
const boxes = (rnd) => [
  { x: 0, y: 0, w: 1000, h: 1500 },
  { x: 120, y: 40, w: 300, h: 90 },
  { x: 700, y: 900, w: 64, h: 480 },
  { x: 12.5, y: 33.25, w: 211.75, h: 211.75 },
  { x: rnd() * 800, y: rnd() * 800, w: 8 + rnd() * 400, h: 8 + rnd() * 400 },
];

const cellAt = (cx, cy, area = 0.04) => ({ cx, cy, area });

/** The canvas transform the draw paths apply, INVERTED: screen point -> pre-rotation space. */
const unrotate = (px, py, t, cx, cy) => {
  const c = Math.cos(-t), s = Math.sin(-t);
  const dx = px - cx, dy = py - cy;
  return { x: cx + dx * c - dy * s, y: cy + dx * s + dy * c };
};

// =============================================================================
console.log('1. COVERAGE — the rotated draw still contains the cell');
// The whole feature is only legitimate if this holds for every angle it can
// produce. Swept at the extremes AND at the modes' own peaks.
{
  const EPS = 1e-6;
  let checked = 0;
  const angles = [];
  for (let d = -22; d <= 22; d += 0.5) angles.push((d * Math.PI) / 180);
  for (const m of TWIST_MODES) { angles.push((m.deg * Math.PI) / 180, (-m.deg * Math.PI) / 180); }

  for (let seed = 0; seed < 40; seed++) {
    const rnd = rngOf(seed * 31 + 5);
    for (const box of boxes(rnd)) {
      for (const t of angles) {
        const d = twistedDest(box, t);
        const corners = [
          [box.x, box.y], [box.x + box.w, box.y],
          [box.x + box.w, box.y + box.h], [box.x, box.y + box.h],
        ];
        for (const [px, py] of corners) {
          const q = unrotate(px, py, d.twist, d.tcx, d.tcy);
          const inside =
            q.x >= d.dx - EPS && q.x <= d.dx + d.dw + EPS &&
            q.y >= d.dy - EPS && q.y <= d.dy + d.dh + EPS;
          check(inside,
            `corner (${px},${py}) of ${box.w}x${box.h} escapes the drawn rect at ` +
            `${((t * 180) / Math.PI).toFixed(1)}deg — background would show through`);
          checked++;
        }
      }
    }
  }
  console.log(`   ${checked} corner containments verified`);
}

// =============================================================================
console.log('2. the grown rect is MINIMAL — no gratuitous crop-in');
// Coverage alone is satisfied by growing without limit, which would throw away
// picture for nothing. The expansion must be exactly |cos|+|sin|, i.e. shrinking
// it by even a hair must BREAK containment.
{
  const box = { x: 40, y: 60, w: 400, h: 260 };
  for (let d = 1; d <= 22; d += 1) {
    const t = (d * Math.PI) / 180;
    const g = twistedDest(box, t);
    const shrunk = { dx: g.tcx - (g.dw * 0.995) / 2, dy: g.tcy - (g.dh * 0.995) / 2,
                     dw: g.dw * 0.995, dh: g.dh * 0.995 };
    let escaped = false;
    for (const [px, py] of [[box.x, box.y], [box.x + box.w, box.y],
                            [box.x + box.w, box.y + box.h], [box.x, box.y + box.h]]) {
      const q = unrotate(px, py, t, g.tcx, g.tcy);
      if (q.x < shrunk.dx || q.x > shrunk.dx + shrunk.dw ||
          q.y < shrunk.dy || q.y > shrunk.dy + shrunk.dh) escaped = true;
    }
    check(escaped, `a 0.5% smaller rect still covers at ${d}deg — the expansion is larger than it needs to be`);
  }
}

// =============================================================================
console.log('3. the untwisted path is BIT-IDENTICAL to a build without twist');
// The default is `none`, so the overwhelming majority of renders go down this
// path. It must not shift by one float — an existing project reopening
// re-cropped by a rounding error is a regression nobody would report but
// everybody would see.
{
  const img = { width: 1600, height: 1200, analysis: { face: { x: 0.3, y: 0.7 }, energy: { x: 0.5, y: 0.5 } } };
  for (let seed = 0; seed < 60; seed++) {
    const rnd = rngOf(seed * 17 + 3);
    for (const box of boxes(rnd)) {
      for (const zoom of [1, 1.15, 1.5, 2.5]) {
        const got = calculateSmartCrop(box, img, zoom);

        // The historical formula, as a MEASURING STICK (not a re-implementation
        // of the new behaviour): this is exactly what the function computed
        // before twist existed.
        const boxAsp = box.w / box.h;
        const imgAsp = img.width / img.height;
        const drawW = imgAsp > boxAsp ? (img.height * boxAsp) : img.width;
        const drawH = imgAsp > boxAsp ? img.height : (img.width / boxAsp);
        const cropW = drawW / zoom, cropH = drawH / zoom;
        const ax = img.analysis.face.x * img.width, ay = img.analysis.face.y * img.height;
        const sx = Math.max(0, Math.min(img.width - cropW, ax - cropW / 2));
        const sy = Math.max(0, Math.min(img.height - cropH, ay - cropH / 2));

        check(got.sx === sx && got.sy === sy && got.sw === cropW && got.sh === cropH,
          `untwisted source rect moved for ${box.w}x${box.h} @${zoom}`);
        check(got.dx === box.x && got.dy === box.y && got.dw === box.w && got.dh === box.h,
          `untwisted destination is no longer the cell bounds for ${box.w}x${box.h}`);
        check(got.twist === 0, 'untwisted crop must report twist 0');
      }
    }
  }
}

// =============================================================================
console.log('4. no STRETCH — the source aspect matches the destination aspect');
// A twist grows the destination, and its aspect changes with it. Fitting the
// cover crop against the CELL aspect instead of the grown one would draw every
// twisted fragment subtly squashed — a defect that looks like bad photography.
{
  const img = { width: 900, height: 1600, analysis: { face: null, energy: { x: 0.5, y: 0.4 } } };
  for (const box of [{ x: 0, y: 0, w: 500, h: 200 }, { x: 5, y: 5, w: 120, h: 700 }, { x: 0, y: 0, w: 300, h: 300 }]) {
    for (let d = -22; d <= 22; d += 2) {
      const t = (d * Math.PI) / 180;
      const c = calculateSmartCrop(box, { ...img, analysis: { ...img.analysis, twist: t } }, 1.2);
      const rel = Math.abs((c.sw / c.sh) - (c.dw / c.dh)) / (c.dw / c.dh);
      check(rel < 1e-9, `aspect drift ${rel.toExponential(2)} at ${d}deg on ${box.w}x${box.h} — the picture would draw stretched`);
      check(c.sx >= 0 && c.sy >= 0 && c.sx + c.sw <= img.width + 1e-9 && c.sy + c.sh <= img.height + 1e-9,
        `source rect leaves the image at ${d}deg on ${box.w}x${box.h}`);
    }
  }
}

// =============================================================================
console.log('5. hostile angles are CLAMPED, never propagated');
// A corrupt project file, a hand-edited share code or an NaN out of a partial
// analysis must not reach the geometry. Un-clamped, a 40-radian twist produces a
// destination the size of the canvas and a crop of one pixel.
{
  for (const bad of [NaN, Infinity, -Infinity, 40, -40, 1e9, '0.3', null, undefined, {}]) {
    const t = twistOf({ twist: bad });
    check(Number.isFinite(t) && Math.abs(t) <= MAX_TWIST_RAD + 1e-12,
      `twistOf(${String(bad)}) returned ${t}`);
  }
  const wild = calculateSmartCrop({ x: 0, y: 0, w: 400, h: 300 }, { width: 800, height: 600, analysis: { face: null, energy: null, twist: 999 } }, 1);
  check(Number.isFinite(wild.sw) && wild.sw > 0 && Number.isFinite(wild.dw) && wild.dw > 0,
    'a wild twist produced non-finite geometry');
  // ...and a MISSING analysis must not throw at all (it used to: the old code
  // dereferenced `.face` unguarded and every caller carried its own workaround).
  let threw = false;
  try { calculateSmartCrop({ x: 0, y: 0, w: 10, h: 10 }, { width: 20, height: 20, analysis: null }, 1); }
  catch { threw = true; }
  check(!threw, 'a null analysis still throws out of calculateSmartCrop');
}

// =============================================================================
console.log('6. every mode is DETERMINISTIC and stays inside its own budget');
{
  for (const m of TWIST_MODES) {
    const cap = (m.deg * Math.PI) / 180 + 1e-12;
    for (let i = 0; i < 300; i++) {
      const rnd = rngOf(i * 13 + 1);
      const cell = cellAt(rnd(), rnd());
      const slot = (i * 2654435761) | 0;
      const a = twistAngle(m.id, slot, cell);
      const b = twistAngle(m.id, slot, cell);
      check(a === b, `${m.id} is not deterministic`);
      check(Number.isFinite(a) && Math.abs(a) <= cap,
        `${m.id} produced ${((a * 180) / Math.PI).toFixed(2)}deg, over its ${m.deg}deg budget`);
    }
    check(twistAngle(m.id, 7, null) !== undefined, `${m.id} threw on missing geometry`);
  }
  check(twistAngle('none', 12, cellAt(0.3, 0.8)) === 0, "'none' must be exactly zero");
}

// =============================================================================
console.log('7. the modes are actually DIFFERENT from each other');
// A picker whose entries render the same picture is a lie in the UI — the same
// scar the arrangement roster carries. Compared as FIELDS over a grid of cells,
// which is what a viewer sees, not as one sampled angle.
{
  const grid = [];
  for (let i = 0; i < 6; i++) for (let j = 0; j < 6; j++) grid.push(cellAt((i + 0.5) / 6, (j + 0.5) / 6));
  const field = (id) => grid.map((c, k) => twistAngle(id, (k * 2654435761) | 0, c));
  const fields = Object.fromEntries(TWIST_IDS.map((id) => [id, field(id)]));

  for (const id of TWIST_IDS) {
    if (id === 'none') continue;
    const nonzero = fields[id].filter((v) => Math.abs(v) > 1e-9).length;
    check(nonzero >= grid.length * 0.75, `'${id}' left ${grid.length - nonzero}/${grid.length} fragments square — it barely does anything`);
  }
  for (let i = 0; i < TWIST_IDS.length; i++) {
    for (let j = i + 1; j < TWIST_IDS.length; j++) {
      const a = fields[TWIST_IDS[i]], b = fields[TWIST_IDS[j]];
      const same = a.every((v, k) => Math.abs(v - b[k]) < 1e-9);
      check(!same, `'${TWIST_IDS[i]}' and '${TWIST_IDS[j]}' produce the identical field — one of them is a dead chip`);
    }
  }

  // The field modes must genuinely READ as fields: neighbouring fragments differ
  // smoothly, which is what separates them from `scatter`.
  const ring = (n) => Array.from({ length: n }, (_, k) => {
    const th = (k / n) * Math.PI * 2;
    return cellAt(0.5 + 0.35 * Math.cos(th), 0.5 + 0.35 * Math.sin(th));
  });
  const N = 64, r = ring(N);
  const jump = (id) => {
    const v = r.map((c, k) => twistAngle(id, (k * 2654435761) | 0, c));
    let worst = 0;
    for (let k = 0; k < N; k++) worst = Math.max(worst, Math.abs(v[(k + 1) % N] - v[k]));
    return worst;
  };
  const pinMax = (TWIST_MODES.find((m) => m.id === 'pinwheel').deg * Math.PI) / 180;
  // THE SEAM. A raw theta ramp is discontinuous at +-pi: two fragments touching
  // across the 9 o'clock line would differ by 2*max — a visible tear straight
  // through the swirl. sin() closes the field on itself, so the largest
  // step around a full ring stays small.
  check(jump('pinwheel') < pinMax * 0.25,
    `pinwheel jumps ${((jump('pinwheel') * 180) / Math.PI).toFixed(1)}deg between neighbouring fragments — there is a tear in the field`);
  check(jump('scatter') > pinMax * 0.5, 'scatter is not scattering — neighbours barely differ');
}

// =============================================================================
console.log('8. withTwist is a per-slot COPY, and free when it is off');
{
  const photo = { id: 'p', analysis: { face: { x: 0.2, y: 0.2 }, energy: { x: 0.4, y: 0.4 }, color: { r: 1, g: 2, b: 3, h: 0.1, s: 0.2, l: 0.3 } } };
  check(withTwist(photo, 'none', 1, cellAt(0.2, 0.2)) === photo,
    "'none' must hand back the SAME object — the default path may not allocate");

  const out = withTwist(photo, 'scatter', 99, cellAt(0.6, 0.3));
  check(out !== photo, 'scatter must not mutate in place');
  check(photo.analysis.twist === undefined, 'withTwist mutated the source photo');
  check(out.analysis.face === photo.analysis.face && out.analysis.energy === photo.analysis.energy,
    'withTwist disturbed the focus anchors it must leave alone');
  check(out.analysis.color !== null && out.analysis.color.h === 0.1, 'withTwist dropped the colour analysis');
  check(twistOf(out.analysis) !== 0, 'withTwist wrote no usable angle');

  // Chains with withFocus without either clobbering the other.
  const noAnalysis = { id: 'q' };
  const safe = withTwist(noAnalysis, 'tilt', 3, cellAt(0.1, 0.9));
  let threw = false;
  try { calculateSmartCrop({ x: 0, y: 0, w: 100, h: 80 }, { width: 200, height: 200, analysis: safe.analysis }, 1); }
  catch { threw = true; }
  check(!threw, 'a twisted photo with no analysis throws in the crop path');
}

// =============================================================================
console.log('9. share codes carry the twist, and legacy codes still open');
{
  for (let seed = 0; seed < 500; seed++) {
    const r = rollDice({ rnd: rngOf(seed * 11 + 2), hasVideo: seed % 4 === 0 });
    const back = decodeRoll(encodeRoll(r));
    check(back !== null, `roll ${seed} failed to decode`);
    if (back) check(back.twist === r.twist, `twist did not survive the share code (${r.twist} -> ${back?.twist})`);
  }
  // A code minted before twist existed described a square collage; it must still
  // open, and open as one.
  const modern = encodeRoll(rollDice({ rnd: rngOf(4242), hasVideo: false }));
  const [a, b, c] = modern.split('-');
  const legacy = `${a}-${b.slice(0, 8)}-${c}`;         // composition-era, 8 chars
  const ancient = `${a}-${b.slice(0, 6)}-${c}`;        // pre-composition, 6 chars
  for (const [name, code] of [['composition-era', legacy], ['pre-composition', ancient]]) {
    const d = decodeRoll(code);
    check(d !== null, `a ${name} share code no longer decodes`);
    if (d) check(d.twist === 'none', `a ${name} code opened with twist '${d.twist}' — it described a square collage`);
  }
}

// =============================================================================
console.log('10. the dice reaches every twist, and leaves most rolls square');
// Family-gating starved the arrangement roster once already; this is a LEAN.
{
  const tw = new Map();
  for (let seed = 0; seed < 4000; seed++) {
    const r = rollDice({ rnd: rngOf(seed * 7 + 1), hasVideo: seed % 3 === 0 });
    tw.set(r.twist, (tw.get(r.twist) ?? 0) + 1);
  }
  for (const id of TWIST_IDS) {
    const share = (tw.get(id) ?? 0) / 4000;
    check(share > 0.02, `the dice rolls '${id}' on only ${(share * 100).toFixed(1)}% of rolls — a chip nobody reaches`);
  }
  const none = (tw.get('none') ?? 0) / 4000;
  check(none > 0.45 && none < 0.75,
    `'none' came up ${(none * 100).toFixed(1)}% — a twist costs real picture, so square must stay the common outcome`);
  console.log(`   spread ${[...tw.entries()].sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}:${((v / 4000) * 100).toFixed(0)}%`).join(' ')}`);
}

if (fails) { console.error(`\n${fails} INVARIANT FAILURE(S)`); process.exit(1); }
console.log('\nAll twist invariants hold.');
