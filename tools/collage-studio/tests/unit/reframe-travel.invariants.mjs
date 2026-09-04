/**
 * Invariant sweep for THE FRAME TRAVELS — the commit that puts a hand-set crop
 * into every file this app writes.
 *
 * Run: node tests/unit/reframe-travel.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * every claim is about the shipped `reframe.commitFrame` composed with the
 * shipped `renderer.calculateSmartCrop` and the shipped `composition.arrangeBag`
 * — never a re-implementation of any of them.
 *
 * THE CLAIM THAT MATTERS — I6, AND IT IS THE QUESTION THE LADDER LEFT OPEN.
 *   The ladder's entry ("A REFRAME DOES NOT TRAVEL") named the pool write as the
 *   fix and refused it, because `images` is a dependency of the layout effect
 *   and of the assignment effect: "mutating the pool per drag frame would
 *   RE-DEAL THE WHOLE WALL". The commit is once per GESTURE, so the question
 *   narrows to whether ONE re-run lands on the same collage — and that is a
 *   measurement, not an argument. `arrangeBag` is the whole of what the deal
 *   reads out of the pool, and it reads `analysis.color`. I6 sweeps it over
 *   every arrangement, every shuffle and hole-y cell lists and asserts the
 *   placement is deep-equal before and after a frame is written.
 *
 * THE SECOND ONE — I7. The crop drawn from a Map entry and the crop drawn from a
 *   pool asset carrying the same frame are the same rect, to the bit, for every
 *   fragment shape, image shape, zoom and lean. That is what makes the file a
 *   faithful record rather than an approximation of one.
 *
 * THE THIRD — I9/I10/I11, THE FIXPOINT. `poolWithFrames` (on the way out) and
 *   `framesFromPool` + `poolWithoutFrames` (on the way in) are inverses, and the
 *   composition save -> open -> save is the IDENTITY ON THE SERIALISED BYTES.
 *   That is the unit-level statement of what reframe.spec T4 measures at the
 *   artifact, and it is why a file this app reopens re-exports byte for byte.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');

const load = async (rel, tag) => {
  const out = join(mkdtempSync(join(tmpdir(), `${tag}-`)), `${tag}.mjs`);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: out, bundle: true, format: 'esm', platform: 'neutral', logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const { commitFrame, frameOf, withReframe, dragToFrame, poolWithFrames, framesFromPool, poolWithoutFrames } =
  await load('src/lib/reframe.ts', 'reframe');
const { calculateSmartCrop } = await load('src/lib/renderer.ts', 'renderer');
const { arrangeBag, ARRANGEMENTS } = await load('src/lib/composition.ts', 'composition');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);

/** An analysis with the frame removed, for "only the frame moved" comparisons. */
const withoutFrameJSON = (a) => {
  const { frame: _drop, ...rest } = a?.analysis ?? {};
  return { ...a, analysis: rest };
};

// ------------------------------------------------------------------ fixtures --
/** A pool shaped exactly like the app's: an id, a size, a full analysis. */
const pool = (n, seedish = 1) =>
  Array.from({ length: n }, (_, i) => {
    const t = ((i * 2654435761 + seedish * 40503) >>> 0) / 4294967296;
    return {
      id: `img-${seedish}-${i}`,
      width: 3000 + i * 137,
      height: 2000 + ((i * 311) % 900),
      analysis: {
        face: i % 3 === 0 ? { x: 0.3 + t * 0.4, y: 0.2 + t * 0.5 } : null,
        energy: { x: 0.2 + t * 0.6, y: 0.15 + t * 0.7 },
        color: {
          r: Math.round(t * 255), g: Math.round((1 - t) * 255), b: (i * 37) % 256,
          h: t, s: 0.2 + t * 0.7, l: 0.15 + t * 0.7,
        },
      },
    };
  });

/** Frames worth storing, including the values a clamp actually produces. */
const FRAMES = [
  { x: 0.5, y: 0.5 },
  { x: 0, y: 1 },
  { x: 1, y: 0 },
  { x: 0.1234567890123456, y: 0.9876543210987654 },
  { x: 1 / 3, y: 2 / 3 },
  { x: Number.EPSILON, y: 1 - Number.EPSILON },
];

// --------------------------------------------- I1 — one photograph, no more --
{
  let bad = 0, wrote = 0;
  for (let n = 1; n <= 12; n++) {
    const p = pool(n, n);
    for (let i = 0; i < n; i++) for (const f of FRAMES) {
      const next = commitFrame(p, p[i].id, f);
      if (next === p) { bad++; continue; }
      wrote++;
      if (!eq(frameOf(next[i]), f)) bad++;
      for (let j = 0; j < n; j++) {
        if (j === i) continue;
        if (!Object.is(next[j], p[j])) bad++;              // every other element BY REFERENCE
      }
      // and the pool it came from is untouched
      if (frameOf(p[i]) !== null) bad++;
      if (next.length !== p.length) bad++;
    }
  }
  ok('I1 commit writes exactly the named photograph, by reference elsewhere', bad === 0 && wrote > 0,
     `${wrote} writes, ${bad} violations`);
}

// -------------------------------------- I2 — identity when nothing to say ----
{
  let bad = 0, checked = 0;
  for (let n = 1; n <= 8; n++) {
    const p = pool(n, 100 + n);
    for (const f of FRAMES) {
      // clearing a frame nobody set
      if (commitFrame(p, p[0].id, null) !== p) bad++;
      if (commitFrame(p, p[0].id, undefined) !== p) bad++;
      // an id that is not in this pool
      if (commitFrame(p, 'img-not-here', f) !== p) bad++;
      // a non-finite frame is not a correction
      if (commitFrame(p, p[0].id, { x: NaN, y: 0.5 }) !== p) bad++;
      if (commitFrame(p, p[0].id, { x: 0.5, y: Infinity }) !== p) bad++;
      // committing the frame already there
      const once = commitFrame(p, p[0].id, f);
      if (commitFrame(once, p[0].id, { ...f }) !== once) bad++;
      checked += 6;
    }
  }
  ok('I2 identity by reference when the pool already says it', bad === 0, `${checked} checks, ${bad} violations`);
}

// ----------------------------------- I3 — the round trip the manifest makes --
{
  // What all three writers do: JSON.stringify the analysis, JSON.parse it back.
  let bad = 0, n = 0;
  for (const f of FRAMES) {
    const p = commitFrame(pool(4, 7), 'img-7-2', f);
    const back = JSON.parse(JSON.stringify(p));
    const got = frameOf(back[2]);
    if (!got || !Object.is(got.x, f.x) || !Object.is(got.y, f.y)) bad++;
    // and every other analysis field survived beside it
    if (!eq(back[2].analysis.color, p[2].analysis.color)) bad++;
    if (!eq(back[2].analysis.energy, p[2].analysis.energy)) bad++;
    n++;
  }
  ok('I3 the frame survives the manifest round trip, bit-exact', bad === 0, `${n} frames, ${bad} violations`);
}

// ------------------------------- I4 — the fold is an identity once committed --
{
  let bad = 0, n = 0;
  for (const f of FRAMES) {
    const p = commitFrame(pool(3, 9), 'img-9-1', f);
    if (!Object.is(withReframe(p[1], { ...f }), p[1])) bad++;   // same value -> same object
    if (Object.is(withReframe(p[1], { x: f.x, y: f.y === 0 ? 0.25 : 0 }), p[1])) bad++; // different -> new
    n += 2;
  }
  ok('I4 withReframe answers by reference when the pool already carries it', bad === 0,
     `${n} checks, ${bad} violations`);
}

// --------------------------- I5 — commit then clear is the picture untouched --
{
  let bad = 0, n = 0;
  for (let k = 1; k <= 10; k++) {
    const p = pool(k, 200 + k);
    for (const f of FRAMES) {
      const on = commitFrame(p, p[k - 1].id, f);
      const off = commitFrame(on, p[k - 1].id, null);
      if (!eq(off, p)) bad++;                       // deep-equal, so the file is byte-identical
      if (frameOf(off[k - 1]) !== null) bad++;
      if ('frame' in (off[k - 1].analysis ?? {})) bad++;   // the KEY is gone, not nulled to null
      n++;
    }
  }
  ok('I5 commit then Recentre serialises as a picture nobody touched', bad === 0, `${n} pairs, ${bad} violations`);
}

// ============================================================================
// I6 — THE DEAL IS INVARIANT UNDER A COMMIT.  The ladder's open question.
// ============================================================================
{
  const cellsFor = (n, holes) => Array.from({ length: n }, (_, i) => {
    if (holes && i % 5 === 3) return null;
    const t = i / Math.max(1, n - 1);
    return { cx: 0.1 + 0.8 * t, cy: 0.15 + 0.7 * ((i * 7) % n) / Math.max(1, n), area: 0.02 + 0.05 * ((i * 3) % 4) };
  });
  let bad = 0, cases = 0, moved = 0;
  const ids = ARRANGEMENTS.map(a => a.id);
  for (const n of [2, 3, 7, 12, 24]) {
    const p = pool(n, n * 3);
    const bag = Array.from({ length: n }, (_, i) => (i * 5 + 1) % n);
    for (const holes of [false, true]) {
      const cells = cellsFor(n, holes);
      for (const arrangement of ids) {
        for (const shuffle of [0, 1, 2, 7]) {
          const before = arrangeBag({ bag, cells, images: p, arrangement, shuffle });
          // Commit a frame onto EVERY photograph — the worst case, not one.
          let q = p;
          for (let i = 0; i < n; i++) q = commitFrame(q, p[i].id, FRAMES[i % FRAMES.length]);
          if (q === p) bad++;                       // the sweep must actually have changed the pool
          const after = arrangeBag({ bag, cells, images: q, arrangement, shuffle });
          if (!eq(before, after)) { bad++; moved++; }
          cases++;
        }
      }
    }
  }
  ok('I6 THE DEAL IS INVARIANT UNDER A COMMIT — arrangeBag places identically',
     bad === 0, `${cases} deals swept, ${moved} moved`);
}

// ---------------- I7 — the hand-off is invisible: same crop, to the bit ------
{
  const BOXES = [
    { x: 0, y: 0, w: 400, h: 300 },
    { x: 120, y: 60, w: 200, h: 500 },
    { x: 40, y: 40, w: 260, h: 260 },
    { x: 0, y: 700, w: 1200, h: 180 },
    { x: 900, y: 0, w: 90, h: 700 },
  ];
  const TWISTS = [0, 0.157, -0.273, 0.384];
  let bad = 0, cases = 0;
  for (const box of BOXES) for (const zoom of [1, 1.35, 2.2]) for (const tw of TWISTS) {
    const p = pool(2, 55);
    const raw = { ...p[0], analysis: { ...p[0].analysis, twist: tw } };
    for (const f of FRAMES) {
      // (a) the frame arrives through the Map — what the drag does
      const viaMap = withReframe(raw, f);
      // (b) the frame arrives on the pool asset — what the commit does
      const viaPool = commitFrame([raw], raw.id, f)[0];
      const A = calculateSmartCrop(box, { width: raw.width, height: raw.height, analysis: viaMap.analysis }, zoom);
      const B = calculateSmartCrop(box, { width: raw.width, height: raw.height, analysis: viaPool.analysis }, zoom);
      for (const k of Object.keys(A)) if (!Object.is(A[k], B[k])) bad++;
      cases++;
    }
  }
  ok('I7 the commit draws the identical rect the drag was drawing', bad === 0,
     `${cases} crops, ${bad} differing fields`);
}

// ---------------- I8 — a real drag survives the commit, end to end ----------
{
  // The whole gesture, as the app runs it: sample the crop at pointerdown, map a
  // total displacement, commit at pointerup, then draw from the POOL.
  let bad = 0, cases = 0;
  for (const box of [{ x: 0, y: 0, w: 400, h: 300 }, { x: 0, y: 0, w: 180, h: 620 }]) {
    for (const zoom of [1, 1.6]) {
      const p = pool(1, 77);
      const raw = p[0];
      const crop0 = calculateSmartCrop(box, { width: raw.width, height: raw.height, analysis: raw.analysis }, zoom);
      for (const [dx, dy] of [[0, 120], [0, -120], [90, 0], [-90, 60]]) {
        const landed = dragToFrame(crop0, { width: raw.width, height: raw.height }, dx, dy);
        const committed = commitFrame([raw], raw.id, landed)[0];
        const cropLive = calculateSmartCrop(box, { width: raw.width, height: raw.height, analysis: withReframe(raw, landed).analysis }, zoom);
        const cropSaved = calculateSmartCrop(box, { width: raw.width, height: raw.height, analysis: JSON.parse(JSON.stringify(committed)).analysis }, zoom);
        for (const k of Object.keys(cropLive)) if (!Object.is(cropLive[k], cropSaved[k])) bad++;
        cases++;
      }
    }
  }
  ok('I8 drag -> commit -> manifest -> reopen draws the same crop', bad === 0, `${cases} gestures, ${bad} differing fields`);
}

// ============================================================================
// I9/I10/I11 — THE FIXPOINT.  Merge on the way out, lift on the way in.
// ============================================================================
{
  const framesFor = (p, every) => {
    const m = new Map();
    p.forEach((a, i) => { if (every || i % 2 === 0) m.set(a.id, FRAMES[i % FRAMES.length]); });
    return m;
  };
  let bad = 0, cases = 0;
  for (const n of [1, 2, 5, 13]) {
    const p = pool(n, n * 11);
    for (const every of [false, true]) {
      const f = framesFor(p, every);
      const out = poolWithFrames(p, f);
      // the merge really wrote something, and only into `analysis.frame`
      if (out === p) bad++;
      for (let i = 0; i < n; i++) {
        const want = f.get(p[i].id) ?? null;
        if (!eq(frameOf(out[i]), want)) bad++;
        if (!eq(withoutFrameJSON(out[i]), withoutFrameJSON(p[i]))) bad++;
      }
      // I9 — the two directions are inverses
      const lifted = framesFromPool(out);
      if (lifted.size !== f.size) bad++;
      f.forEach((v, id) => { const g = lifted.get(id); if (!g || !Object.is(g.x, v.x) || !Object.is(g.y, v.y)) bad++; });
      if (!eq(poolWithoutFrames(out), p)) bad++;
      // I11 — save -> open -> save is the identity on the BYTES
      const reopened = JSON.parse(JSON.stringify(out));
      const again = poolWithFrames(poolWithoutFrames(reopened), framesFromPool(reopened));
      if (JSON.stringify(again) !== JSON.stringify(out)) bad++;
      cases++;
    }
    // I10 — a session in which nobody dragged anything hands the writers the
    // very array they were handed before this feature existed.
    if (poolWithFrames(p, new Map()) !== p) bad++;
    if (poolWithFrames(p, undefined) !== p) bad++;
    if (poolWithoutFrames(p) !== p) bad++;
    if (framesFromPool(p).size !== 0) bad++;
    cases++;
  }
  ok('I9/I10/I11 merge-out and lift-in are inverses, and save->open->save is the identity',
     bad === 0, `${cases} pools, ${bad} violations`);
}

// ------------------------------------------------------------------ report --
console.log('\nTHE FRAME TRAVELS — invariant sweep\n' + '-'.repeat(62));
for (const r of results) console.log(r);
console.log('-'.repeat(62));
console.log(failures === 0 ? `ALL ${results.length} INVARIANTS HOLD` : `${failures} FAILED`);
process.exit(failures === 0 ? 0 : 1);
