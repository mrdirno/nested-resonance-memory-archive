/**
 * Invariant sweep for THE LOOK — the colour grade (src/lib/grade.ts).
 *
 * Run: node tests/unit/grade.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, bundled, types stripped) and imports
 * them, so it proves the shipped `cssFilterFor` / `svgFilterFor` and the shipped
 * codec — not a re-implementation.
 *
 * WHAT ONLY A SWEEP CAN PROVE HERE
 *
 *   The module emits two DESCRIPTIONS of one grade: a CSS filter string for the
 *   three canvas paths and SVG `<filter>` primitives for the vector export.
 *   Structural agreement — "same order, same numbers" — is necessary and is
 *   asserted below, but it is not the thing that matters. What matters is that
 *   the two descriptions denote the SAME COLOUR TRANSFORM, and that is a claim
 *   about arithmetic nobody can read off a string.
 *
 *   So this file PARSES what the module emitted (never the roster it emitted it
 *   from) into an independent evaluator built from the CSS Filter Effects spec,
 *   runs both descriptions over a dense colour sweep, and asserts they agree to
 *   the float. A drift in either emitter — a slope written where an intercept
 *   belongs, a sepia matrix row transposed, a hue angle in radians — shows up as
 *   a colour difference rather than as a string difference nobody would read.
 *
 * THE RED PROOF (I9) is the sRGB decision, priced.
 *   SVG filters default to `color-interpolation-filters: linearRGB`; canvas
 *   evaluates the identical functions in sRGB. The emitted `<filter>` therefore
 *   says `sRGB` explicitly. Deleting that one attribute is not a subtle
 *   regression, and the number below is what it costs.
 *
 * SCAR OBEYED (COLLAGE_EVOLUTION.md): a test that defines the space the way the
 * code defines it cannot see the code being wrong. The colour maths here is
 * written from the SPEC, and the per-look predictions are stated as INTENT
 * ("warm is warmer") rather than read back off the roster's own numbers.
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
    outfile: out, bundle: true, format: 'esm', platform: 'neutral', logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const G = await load('src/lib/grade.ts', 'grade');
const RC = await load('src/lib/rollCode.ts', 'rollcode');
const {
  LOOKS, LOOK_IDS, NO_GRADE, gradeFor, gradeSteps, stepsForLook,
  cssFilterFor, svgFilterFor, svgFilterAttrFor, isNoOp, SVG_FILTER_ID, GRADE_GRID,
} = G;

let checks = 0, failures = 0;
const fail = (id, msg) => { failures++; console.error(`  ✗ [${id}] ${msg}`); };
const ok = (id, cond, msg) => { checks++; if (!cond) fail(id, msg); };
const near = (id, a, b, tol, msg) => {
  checks++;
  if (!(Math.abs(a - b) <= tol)) fail(id, `${msg} — |${a} - ${b}| = ${Math.abs(a - b)} > ${tol}`);
};

// =============================================================================
// THE EVALUATOR — CSS Filter Effects Level 1, written from the spec.
// =============================================================================

const clamp = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/** feColorMatrix type="saturate" — the spec's matrix. */
const satM = (s) => [
  0.213 + 0.787 * s, 0.715 - 0.715 * s, 0.072 - 0.072 * s,
  0.213 - 0.213 * s, 0.715 + 0.285 * s, 0.072 - 0.072 * s,
  0.213 - 0.213 * s, 0.715 - 0.715 * s, 0.072 + 0.928 * s,
];

/** feColorMatrix type="hueRotate" — the spec's matrix, degrees. */
const hueM = (deg) => {
  const r = (deg * Math.PI) / 180, c = Math.cos(r), s = Math.sin(r);
  return [
    0.213 + c * 0.787 - s * 0.213, 0.715 - c * 0.715 - s * 0.715, 0.072 - c * 0.072 + s * 0.928,
    0.213 - c * 0.213 + s * 0.143, 0.715 + c * 0.285 + s * 0.140, 0.072 - c * 0.072 - s * 0.283,
    0.213 - c * 0.213 - s * 0.787, 0.715 - c * 0.715 + s * 0.715, 0.072 + c * 0.928 + s * 0.072,
  ];
};

/** The spec's parameterised sepia, as a 3x3 (alpha is untouched by all of these). */
const sepiaM = (amount) => {
  const a = 1 - amount;
  return [
    0.393 + 0.607 * a, 0.769 - 0.769 * a, 0.189 - 0.189 * a,
    0.349 - 0.349 * a, 0.686 + 0.314 * a, 0.168 - 0.168 * a,
    0.272 - 0.272 * a, 0.534 - 0.534 * a, 0.131 + 0.869 * a,
  ];
};

const applyOp = (op, [r, g, b]) => {
  if (op.kind === 'linear') {
    return [r, g, b].map((v) => clamp(v * op.slope + op.intercept));
  }
  const m = op.m;
  return [
    clamp(m[0] * r + m[1] * g + m[2] * b),
    clamp(m[3] * r + m[4] * g + m[5] * b),
    clamp(m[6] * r + m[7] * g + m[8] * b),
  ];
};

const runOps = (ops, px) => ops.reduce((p, op) => applyOp(op, p), px.map(clamp));

// --- the two PARSERS. Both read what the module emitted, not the roster. -----

const parseCss = (css) => {
  if (css === 'none') return [];
  const ops = [];
  const re = /([a-z-]+)\(([^)]*)\)/g;
  let m;
  while ((m = re.exec(css)) !== null) {
    const name = m[1];
    const arg = parseFloat(m[2]);
    if (!Number.isFinite(arg)) throw new Error(`unparseable arg in ${css}`);
    if (name === 'brightness') ops.push({ kind: 'linear', slope: arg, intercept: 0, name });
    else if (name === 'contrast') ops.push({ kind: 'linear', slope: arg, intercept: -(0.5 * arg) + 0.5, name });
    else if (name === 'saturate') ops.push({ kind: 'matrix', m: satM(arg), name });
    else if (name === 'sepia') ops.push({ kind: 'matrix', m: sepiaM(arg), name });
    else if (name === 'hue-rotate') ops.push({ kind: 'matrix', m: hueM(arg), name });
    else throw new Error(`unknown css filter function: ${name}`);
  }
  return ops;
};

const parseSvg = (svg) => {
  if (!svg) return [];
  const ops = [];
  const re = /<feComponentTransfer>.*?<\/feComponentTransfer>|<feColorMatrix\b[^>]*\/>/g;
  const chunks = svg.match(re) || [];
  for (const c of chunks) {
    if (c.startsWith('<feComponentTransfer')) {
      // Every channel must carry the same transfer — assert it here rather than
      // trusting the first one, because a per-channel slip is exactly the shape
      // a hand-written emitter gets wrong.
      const funcs = c.match(/<feFunc[RGB][^>]*\/>/g) || [];
      if (funcs.length !== 3) throw new Error(`feComponentTransfer with ${funcs.length} channels`);
      const read = (f) => {
        const t = /type="([^"]+)"/.exec(f);
        const s = /slope="([-\d.]+)"/.exec(f);
        const i = /intercept="([-\d.]+)"/.exec(f);
        if (!t || t[1] !== 'linear') throw new Error(`non-linear transfer: ${f}`);
        return { slope: s ? parseFloat(s[1]) : 1, intercept: i ? parseFloat(i[1]) : 0 };
      };
      const [a, b, d] = funcs.map(read);
      if (a.slope !== b.slope || a.slope !== d.slope || a.intercept !== b.intercept || a.intercept !== d.intercept) {
        throw new Error(`feComponentTransfer channels disagree in ${c}`);
      }
      ops.push({ kind: 'linear', slope: a.slope, intercept: a.intercept, name: 'transfer' });
    } else {
      const t = /type="([^"]+)"/.exec(c);
      const v = /values="([^"]*)"/.exec(c);
      if (!t || !v) throw new Error(`feColorMatrix without type/values: ${c}`);
      const nums = v[1].trim().split(/\s+/).map(parseFloat);
      if (t[1] === 'saturate') ops.push({ kind: 'matrix', m: satM(nums[0]), name: 'saturate' });
      else if (t[1] === 'hueRotate') ops.push({ kind: 'matrix', m: hueM(nums[0]), name: 'hueRotate' });
      else if (t[1] === 'matrix') {
        if (nums.length !== 20) throw new Error(`feColorMatrix matrix has ${nums.length} values`);
        ops.push({
          kind: 'matrix',
          m: [nums[0], nums[1], nums[2], nums[5], nums[6], nums[7], nums[10], nums[11], nums[12]],
          name: 'matrix',
        });
      } else throw new Error(`unknown feColorMatrix type: ${t[1]}`);
    }
  }
  return ops;
};

// --- the colour sweep --------------------------------------------------------

const SWATCHES = [];
for (let r = 0; r <= 255; r += 15) {
  for (let g = 0; g <= 255; g += 15) {
    for (let b = 0; b <= 255; b += 15) SWATCHES.push([r / 255, g / 255, b / 255]);
  }
}
const GREYS = [];
for (let v = 8; v <= 248; v += 4) GREYS.push([v / 255, v / 255, v / 255]);
const chroma = ([r, g, b]) => Math.max(r, g, b) - Math.min(r, g, b);
const luma = ([r, g, b]) => 0.213 * r + 0.715 * g + 0.072 * b;
const mean = (xs) => xs.reduce((a, x) => a + x, 0) / xs.length;

console.log(`sweep: ${SWATCHES.length} swatches x ${LOOK_IDS.length} looks`);

// =============================================================================
// I1 — THE NO-OP RULE
// =============================================================================
ok('I1a', gradeSteps(NO_GRADE).length === 0, 'the identity grade must produce zero steps');
ok('I1b', cssFilterFor('none') === 'none', `cssFilterFor('none') = ${cssFilterFor('none')}`);
ok('I1c', svgFilterFor('none') === '', `svgFilterFor('none') = ${JSON.stringify(svgFilterFor('none'))}`);
ok('I1d', svgFilterAttrFor('none') === '', 'the no-op must hang no filter attribute');
ok('I1e', isNoOp('none') && isNoOp(null) && isNoOp(undefined), 'none/null/undefined are all no-ops');
// A look this build has never heard of must be a NO-OP, not a crash and not a
// substituted neighbour.
ok('I1f', cssFilterFor('vaporwave-2049') === 'none', 'an unknown look must grade nothing');
ok('I1g', svgFilterFor('vaporwave-2049') === '', 'an unknown look must emit no filter');
// A grade whose numbers are individually identities must also be a no-op, even
// though it is not the `none` OBJECT — this is what makes the guard exact rather
// than an identity check on a reference.
ok('I1h', gradeSteps({ brightness: 1, contrast: 1, saturate: 1, sepia: 0, hue: 0 }).length === 0,
  'an identity-valued grade must produce zero steps');
// Non-finite values must be dropped, not printed into a filter string.
for (const bad of [NaN, Infinity, -Infinity, undefined, null, 'x']) {
  ok('I1i', gradeSteps({ ...NO_GRADE, contrast: bad }).length === 0,
    `contrast=${String(bad)} must be dropped, got ${JSON.stringify(gradeSteps({ ...NO_GRADE, contrast: bad }))}`);
}

// =============================================================================
// I2 — ROSTER SHAPE (the index space a composition code spends a character on)
// =============================================================================
ok('I2a', LOOK_IDS[0] === 'none', `index 0 must be 'none', got ${LOOK_IDS[0]}`);
ok('I2b', new Set(LOOK_IDS).size === LOOK_IDS.length, 'look ids must be unique');
ok('I2c', LOOK_IDS.length <= 36, `${LOOK_IDS.length} looks exceeds one base-36 character`);
ok('I2d', LOOKS.every((l, i) => l.id === LOOK_IDS[i]), 'LOOKS and LOOK_IDS must be one list in one order');
ok('I2e', LOOKS.every((l) => l.label && l.title), 'every look needs a label and a description');
ok('I2f', gradeFor('none') === NO_GRADE || gradeSteps(gradeFor('none')).length === 0,
  "the 'none' entry must be the identity grade");

// =============================================================================
// I3/I4 — ONE ORDER, TWO EMITTERS (structure)
// =============================================================================
const CSS_TO_KIND = {
  brightness: 'brightness', contrast: 'contrast', saturate: 'saturate',
  sepia: 'sepia', 'hue-rotate': 'hueRotate',
};
const SVG_TO_KIND = { transfer: 'linear', saturate: 'saturate', hueRotate: 'hueRotate', matrix: 'sepia' };

for (const id of LOOK_IDS) {
  const steps = stepsForLook(id);
  const css = cssFilterFor(id);
  const svg = svgFilterFor(id);
  const cssOps = parseCss(css);
  const svgOps = parseSvg(svg);

  ok('I3a', cssOps.length === steps.length,
    `${id}: css emitted ${cssOps.length} functions for ${steps.length} steps`);
  ok('I3b', svgOps.length === steps.length,
    `${id}: svg emitted ${svgOps.length} primitives for ${steps.length} steps`);
  // The CSS function names, in order, must BE the pipeline's kinds in order.
  ok('I3c', cssOps.every((o, i) => CSS_TO_KIND[o.name] === steps[i].kind),
    `${id}: css order ${cssOps.map((o) => o.name).join(',')} != pipeline ${steps.map((s) => s.kind).join(',')}`);
  // And the SVG primitives, in the same order. `matrix` is only ever sepia here.
  ok('I3d', svgOps.every((o, i) => {
    const k = steps[i].kind;
    if (k === 'brightness' || k === 'contrast') return o.kind === 'linear';
    return SVG_TO_KIND[o.name] === k;
  }), `${id}: svg order ${svgOps.map((o) => o.name).join(',')} != pipeline ${steps.map((s) => s.kind).join(',')}`);

  // The numbers, through the SHARED formatter.
  for (let i = 0; i < steps.length; i++) {
    const s = steps[i], c = cssOps[i];
    if (s.kind === 'brightness') {
      near('I4a', c.slope, s.v, 1e-9, `${id}: css brightness`);
      near('I4b', c.intercept, 0, 1e-12, `${id}: brightness must not carry an intercept`);
    }
    if (s.kind === 'contrast') {
      near('I4c', c.slope, s.v, 1e-9, `${id}: css contrast slope`);
      // The CSS spec's own intercept, restated here from the spec.
      near('I4d', c.intercept, -(0.5 * s.v) + 0.5, 1e-9, `${id}: css contrast intercept`);
    }
  }

  // The `sRGB` decision must be ON the element, and only when there is one.
  if (steps.length > 0) {
    ok('I4e', svg.includes('color-interpolation-filters="sRGB"'),
      `${id}: the emitted filter must pin sRGB or it is a different grade from the canvas`);
    ok('I4f', svgFilterAttrFor(id) === ` filter="url(#${SVG_FILTER_ID})"`,
      `${id}: the attribute must reference the emitted filter`);
    ok('I4g', svg.includes(`id="${SVG_FILTER_ID}"`), `${id}: filter id must match the attribute`);
  }
}

// =============================================================================
// I5 — SEPIA, AGAINST THE SPEC, AND THE GRID THAT MAKES THE EMITTER LOSSLESS
// =============================================================================
{
  // amount 0 must be the IDENTITY matrix, which is what makes "a dropped sepia
  // step" and "a sepia step of zero" the same picture rather than nearly one.
  const m0 = sepiaM(0);
  const I = [1, 0, 0, 0, 1, 0, 0, 0, 1];
  ok('I5a', m0.every((v, i) => Math.abs(v - I[i]) < 1e-12), 'spec sepia at 0 must be the identity');

  // Affine in the amount: sepia(0.5) is the midpoint of sepia(0) and sepia(1),
  // which is what "interpolate toward the sepia matrix" means.
  const mid = sepiaM(0.5), m1 = sepiaM(1);
  for (let k = 0; k < 9; k++) near('I5b', mid[k], (m0[k] + m1[k]) / 2, 1e-12, 'sepia must be affine in its amount');

  // The EMITTER's matrix, read back out of the string it printed, must be the
  // spec's matrix term for term — for every roster look that has a sepia step.
  for (const id of LOOK_IDS) {
    const step = stepsForLook(id).find((st) => st.kind === 'sepia');
    if (!step) continue;
    const emitted = parseSvg(svgFilterFor(id)).find((o) => o.name === 'matrix');
    ok('I5c', !!emitted, `${id}: a sepia step must emit an feColorMatrix`);
    if (!emitted) continue;
    const spec = sepiaM(step.v);
    for (let k = 0; k < 9; k++) {
      near('I5d', emitted.m[k], spec[k], 1e-9, `${id}: emitted sepia term ${k} != spec`);
    }
  }
}
{
  // THE GRID. `num` prints six decimals, and every sepia term is a
  // three-decimal constant times the amount plus a three-decimal constant — so
  // the printed matrix is EXACT for any grade on a two-decimal grid, and merely
  // close for one off it. That is a property of the ROSTER, so the roster is
  // held to it here rather than assumed. (Same argument as `snapRoll`: quantise
  // losslessly by putting the state on the grid, not by hoping it is there.)
  const onGrid = (v) => Math.abs(v * GRADE_GRID - Math.round(v * GRADE_GRID)) < 1e-9;
  for (const l of LOOKS) {
    for (const key of ['brightness', 'contrast', 'saturate', 'sepia']) {
      ok('I5e', onGrid(l.grade[key]),
        `${l.id}.${key} = ${l.grade[key]} is off the 1/${GRADE_GRID} grid the emitter is exact on`);
    }
    ok('I5f', Number.isInteger(l.grade.hue), `${l.id}.hue = ${l.grade.hue} must be a whole number of degrees`);
  }
}

// =============================================================================
// I6 — THE TWO DESCRIPTIONS DENOTE THE SAME COLOUR TRANSFORM
//      This is the one that matters. Not "same string", same PICTURE.
// =============================================================================
let worstEmitterDelta = 0, worstEmitterLook = '';
for (const id of LOOK_IDS) {
  const cssOps = parseCss(cssFilterFor(id));
  const svgOps = parseSvg(svgFilterFor(id));
  for (const px of SWATCHES) {
    const a = runOps(cssOps, px);
    const b = runOps(svgOps, px);
    const d = Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1]), Math.abs(a[2] - b[2]));
    if (d > worstEmitterDelta) { worstEmitterDelta = d; worstEmitterLook = id; }
    checks++;
    // 1e-9 is 2.6e-7 of one 0-255 step. The roster sits on the grid `num` is
    // exact on (I5e), so this is 'identical', measured — not 'close enough'.
    if (!(d <= 1e-9)) { fail('I6', `${id}: css and svg disagree by ${d} at ${px.map((v) => Math.round(v * 255))}`); break; }
  }
}

// =============================================================================
// I7 — EVERY LOOK DOES WHAT ITS NAME CLAIMS
//      Stated as INTENT, then measured off the emitted string. A roster entry
//      whose numbers stop matching its own label fails here.
// =============================================================================
const out = (id, set) => set.map((px) => runOps(parseCss(cssFilterFor(id)), px));
const baseCol = out('none', SWATCHES), baseGrey = out('none', GREYS);

ok('I7a', baseCol.every((o, i) => o.every((v, k) => v === SWATCHES[i][k])),
  "the 'none' look must return every colour untouched");

for (const id of ['mono', 'noir']) {
  const o = out(id, SWATCHES);
  ok('I7b', o.every((p) => chroma(p) < 1e-12), `${id} must be colourless at every input`);
}
{
  const punch = out('punch', SWATCHES);
  ok('I7c', mean(punch.map(chroma)) > mean(baseCol.map(chroma)), 'punch must add colour');
}
{
  const faded = out('faded', SWATCHES), fadedG = out('faded', GREYS);
  ok('I7d', mean(faded.map(chroma)) < mean(baseCol.map(chroma)), 'faded must pull colour back');
  ok('I7e', mean(fadedG.map(luma)) > mean(baseGrey.map(luma)), 'faded must lift the picture');
}
{
  const noirG = out('noir', GREYS);
  const spread = (xs) => { const m = mean(xs); return Math.sqrt(mean(xs.map((x) => (x - m) ** 2))); };
  ok('I7f', spread(noirG.map(luma)) > spread(baseGrey.map(luma)), 'noir must steepen the curve');
}
{
  const warm = out('warm', GREYS);
  ok('I7g', mean(warm.map((p) => p[0] - p[2])) > 0.02, 'warm must be warm (R above B on neutrals)');
}
{
  const cool = out('cool', GREYS);
  ok('I7h', mean(cool.map((p) => p[2] - p[0])) > 0.02, 'cool must be cool (B above R on neutrals)');
}
{
  const bl = out('bleach', SWATCHES), blG = out('bleach', GREYS);
  const spread = (xs) => { const m = mean(xs); return Math.sqrt(mean(xs.map((x) => (x - m) ** 2))); };
  ok('I7i', mean(bl.map(chroma)) < mean(baseCol.map(chroma)), 'bleach must strip colour');
  ok('I7j', spread(blG.map(luma)) > spread(baseGrey.map(luma)), 'bleach must push contrast');
}
// Nothing may leave the gamut: every look, every swatch, in [0,1].
for (const id of LOOK_IDS) {
  const o = out(id, SWATCHES);
  checks++;
  if (!o.every((p) => p.every((v) => v >= 0 && v <= 1 && Number.isFinite(v)))) {
    fail('I7k', `${id} produced a value outside [0,1]`);
  }
}

// =============================================================================
// I8 — THE CODE CARRIES IT (through the REAL codec)
// =============================================================================
const baseState = {
  layoutMode: 'shards', primitive: 'rect', count: 24, density: 2, entropy: 0.42,
  aspect: 0.6667, gutter: 0.004, bgColor: '#050505', seed: 91237,
  arrangement: 'natural', focus: 'auto', twist: 'none', look: 'none',
  shuffle: 0, countOwned: true,
};
for (const id of LOOK_IDS) {
  for (const seed of [0, 7, 4095, 999999]) {
    for (const shuffle of [0, 5]) {
      const s = { ...baseState, look: id, seed, shuffle };
      const code = RC.encodeState(s);
      const back = RC.decodeState(code);
      ok('I8a', back !== null, `${id}: a freshly minted code must decode (${code})`);
      if (back) ok('I8b', back.look === id, `${id}: round-tripped as ${back && back.look} via ${code}`);
    }
  }
}
{
  // A code from an EARLIER GENERATION must still open, and a code truncated
  // back to one must be REFUSED rather than re-read as a different collage.
  // Built by deleting a field and re-checksumming is not possible from out
  // here, so instead: mint a code and assert every legacy truncation of its
  // middle group is rejected. (The checksum's whole job.)
  //
  // THE LENGTH MOVES EVERY TIME A FIELD IS ADDED, and that is the point of
  // asserting it exactly rather than as a minimum. 18 was the flag form, 19
  // added THE LOOK, 20 added THE MOVE (lib/motion.ts) — each one read by length,
  // because a version character would have had to be present in the first code
  // ever minted to be of any use now, and it was not. When this fails after a
  // new field lands, the number is what changed; when it fails without one, the
  // group silently grew and every fixed-offset slice below it has moved.
  const LOOK_AT = 16;              // the look's own character, 0-indexed
  const GROUP_LEN = 20;            // what THIS build mints
  const code = RC.encodeState({ ...baseState, look: 'none' });
  const [a, b, c] = code.split('-');
  ok('I8c', b.length === GROUP_LEN, `the middle group must be ${GROUP_LEN} chars, got ${b.length}`);
  // INCLUDING the two lengths BELOW the checksummed band. 16 and 17 were never
  // minted by any build (this codec was wired to nothing until 2026-08-07), so
  // a group of that length is a truncation of a real code and must not open on
  // trust — which is what it used to do.
  let refusedTruncations = 0;
  for (const legacy of [16, 17, 18, 19]) {
    if (RC.decodeState(`${a}-${b.slice(0, legacy)}-${c}`) === null) refusedTruncations++;
  }
  ok('I8d', refusedTruncations === 4,
    `only ${refusedTruncations}/4 truncations back to a legacy length were refused`);
}
{
  // THE CHECKSUM MUST COVER THE LOOK CHARACTER. Without that, flipping one
  // character silently opens somebody else's grade — the exact class the
  // truncation scar is about, on the newest field.
  let caught = 0, tried = 0;
  for (const id of LOOK_IDS) {
    const code = RC.encodeState({ ...baseState, look: id });
    const [a, b, c] = code.split('-');
    for (const other of LOOK_IDS) {
      const oi = LOOK_IDS.indexOf(other);
      if (LOOK_IDS.indexOf(id) === oi) continue;
      // The look's character is at a FIXED offset from the START of the group,
      // so this keeps working as later fields extend the tail.
      const mangled = `${a}-${b.slice(0, 16)}${oi.toString(36).toUpperCase()}${b.slice(17)}-${c}`;
      tried++;
      if (RC.decodeState(mangled) === null) caught++;
    }
  }
  ok('I8e', caught === tried, `only ${caught}/${tried} look-character flips were caught by the checksum`);
  console.log(`  I8e: ${caught}/${tried} single-character look manglings refused`);
}
{
  // An out-of-roster look index must be REFUSED, not defaulted to element zero.
  const code = RC.encodeState({ ...baseState, look: 'none' });
  const [a, b, c] = code.split('-');
  const beyond = LOOK_IDS.length.toString(36).toUpperCase();
  const mangled = `${a}-${b.slice(0, 16)}${beyond}${b.slice(17)}-${c}`;
  ok('I8f', RC.decodeState(mangled) === null, 'a look index off the roster must be refused');
}

// =============================================================================
// I9 — THE RED PROOF: what `color-interpolation-filters="sRGB"` is worth.
//      Same primitives, same numbers, evaluated in linear light — which is what
//      an SVG filter does by DEFAULT. If that attribute is ever dropped, this is
//      the size of the divergence between the exported SVG and the exported JPEG.
// =============================================================================
const toLin = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const toSrgb = (l) => (l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055);
const runLinear = (ops, px) => {
  const lin = px.map((v) => clamp(toLin(clamp(v))));
  const outLin = ops.reduce((p, op) => applyOp(op, p), lin);
  return outLin.map((v) => clamp(toSrgb(v)));
};

let worstLinear = 0, worstLinearLook = '', sumLinear = 0, nLinear = 0;
const perLook = [];
for (const id of LOOK_IDS) {
  if (isNoOp(id)) continue;
  const ops = parseSvg(svgFilterFor(id));
  let worst = 0, sum = 0;
  for (const px of SWATCHES) {
    const a = runOps(ops, px);
    const b = runLinear(ops, px);
    const d = Math.max(Math.abs(a[0] - b[0]), Math.abs(a[1] - b[1]), Math.abs(a[2] - b[2]));
    if (d > worst) worst = d;
    sum += d; sumLinear += d; nLinear++;
    if (d > worstLinear) { worstLinear = d; worstLinearLook = id; }
  }
  perLook.push([id, worst * 255, (sum / SWATCHES.length) * 255]);
}
ok('I9a', worstLinear > 0.05,
  `the sRGB pin must be load-bearing; linear evaluation differed by only ${(worstLinear * 255).toFixed(1)}/255`);

// =============================================================================
// REPORT
// =============================================================================
console.log('');
console.log(`I6  css vs svg, ${LOOK_IDS.length * SWATCHES.length} evaluations: worst channel delta ` +
  `${worstEmitterDelta.toExponential(2)} (${worstEmitterLook || 'n/a'})`);
console.log('I9  RED PROOF — dropping color-interpolation-filters="sRGB" (linearRGB, the SVG default):');
for (const [id, w, m] of perLook) {
  console.log(`      ${id.padEnd(7)} worst ${w.toFixed(1).padStart(5)}/255   mean ${m.toFixed(1).padStart(5)}/255`);
}
console.log(`      overall worst ${(worstLinear * 255).toFixed(1)}/255 (${worstLinearLook}), ` +
  `mean ${((sumLinear / nLinear) * 255).toFixed(1)}/255 over ${nLinear} evaluations`);
console.log('');
console.log(failures === 0
  ? `✅ grade.ts — ${checks} checks, 0 failures`
  : `❌ grade.ts — ${checks} checks, ${failures} FAILURES`);
process.exit(failures === 0 ? 0 : 1);
