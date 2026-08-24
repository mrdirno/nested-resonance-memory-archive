/**
 * INVARIANT SWEEP for src/lib/audition.ts — the cut-audition sub-window and its
 * wrap decision.
 *
 *   node tests/unit/audition.invariants.mjs
 *
 * Transpiles and imports the REAL modules (audition + clipWindow). No
 * re-implementation — a sweep against a copy grades the copy.
 *
 * THE TWO THAT CARRY THE FEATURE
 *   A3  the cut edge is PINNED, `Object.is`-exact: the IN audition starts AT
 *       `w.inSec` and the OUT audition ends AT `w.outSec`. "Near the cut" is a
 *       different feature — the whole point is hearing the exact sample the
 *       range will open with / land on.
 *   A6  the wrap decision IS `liveWrapTarget` over the sub-window, including on
 *       a FULL trim window (untrimmed track, audition still loops) — which is
 *       exactly what `full: false` exists to force, and what a well-meaning
 *       "reuse normaliseWindow" refactor would silently break.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');
const dir = mkdtempSync(join(tmpdir(), 'audition-'));

/** BUNDLE, DO NOT TRANSFORM — the C150 scar: a transform dies the day the
 *  module under test grows an import, and audition.ts imports clipWindow. */
const load = async (rel, out) => {
  const tmp = join(dir, out);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: tmp,
    bundle: true,
    format: 'esm',
    platform: 'neutral',
    logLevel: 'silent',
  });
  return import(pathToFileURL(tmp).href);
};

const AU = await load('src/lib/audition.ts', 'audition.mjs');
const CW = await load('src/lib/clipWindow.ts', 'clipWindow.mjs');

const { auditionWindow, auditionWrap, AUDITION_TAIL_SEC, AUDITION_RESEEK_GAP_MS } = AU;
const { normaliseWindow, liveWrapTarget, LIVE_WINDOW_SLOP_SEC, MIN_WINDOW_SEC } = CW;

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };
const assert = (cond, m) => (cond ? ok() : fail(m));
const approx = (a, b, eps = 1e-9) =>
  Math.abs(a - b) <= eps * Math.max(1, Math.abs(a), Math.abs(b));

/** Deterministic PRNG — a sweep that rolls differently each run is a sweep
 *  whose red you cannot reproduce. */
const mulberry32 = (seed) => () => {
  seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const EDGES = ['in', 'out'];

// -----------------------------------------------------------------------------
// THE CONSTANTS THEMSELVES — policy the controller builds on.
// -----------------------------------------------------------------------------
assert(Number.isFinite(AUDITION_TAIL_SEC) && AUDITION_TAIL_SEC > 0,
  'tail is a positive number');
assert(AUDITION_TAIL_SEC >= MIN_WINDOW_SEC,
  'tail is at least the minimum trim window — an audition shorter than the shortest range it serves is noise');
assert(Number.isFinite(AUDITION_RESEEK_GAP_MS) && AUDITION_RESEEK_GAP_MS > 16 && AUDITION_RESEEK_GAP_MS <= 500,
  'reseek gap sits between one frame and half a second');

// -----------------------------------------------------------------------------
// A1 — TOTALITY on hostile windows. Any window-shaped object resolves to
// finite, ordered, non-negative fields with `full === false`.
// -----------------------------------------------------------------------------
const HOSTILE = [
  { inSec: NaN, outSec: NaN, length: NaN, full: false },
  { inSec: Infinity, outSec: -Infinity, length: NaN, full: true },
  { inSec: -5, outSec: -1, length: 4, full: false },
  { inSec: 8, outSec: 2, length: -6, full: false },
  { inSec: 0, outSec: 0, length: 0, full: true },
  { inSec: undefined, outSec: undefined, length: undefined, full: undefined },
  { inSec: 1e308, outSec: 1e308, length: 0, full: false },
  { inSec: 3.2, outSec: NaN, length: NaN, full: false },
];
for (const w of HOSTILE) {
  for (const e of EDGES) {
    const a = auditionWindow(e, w);
    assert(Number.isFinite(a.inSec) && Number.isFinite(a.outSec) && Number.isFinite(a.length),
      `A1 finite fields for ${e} on ${JSON.stringify(w)}`);
    assert(a.inSec >= 0 && a.outSec >= a.inSec && a.length >= 0,
      `A1 ordered, non-negative for ${e} on ${JSON.stringify(w)}`);
    assert(approx(a.length, a.outSec - a.inSec),
      `A1 length agrees with its own bounds for ${e}`);
    assert(a.full === false, `A1 full is false for ${e} on hostile input`);
    // Degenerate audition never asks for a seek anywhere.
    if (!(a.length > 0)) {
      for (const t of [0, 0.5, 1, 100]) {
        assert(auditionWrap(e, w, t) === null,
          `A1 zero-length audition wraps nowhere (${e}, t=${t})`);
      }
    }
  }
}

// -----------------------------------------------------------------------------
// A2..A5 — THE VALID SPACE: windows normaliseWindow actually produces, over the
// spans the app really sees (clipWindow's own sweep goes down to 0.05 s), with
// the overlap band `length < 2 * tail` covered ON PURPOSE — an ordinary range,
// not an exotic one.
// -----------------------------------------------------------------------------
const SPANS = [0.05, 0.14, 0.15, 0.6, 1.6, 2.5, 3.996, 4.0, 5.0, 6.0, 8.4, 27.3, 120, 600];
const CUTS = (span) => [
  [undefined, undefined],           // untrimmed — the FULL window
  [0, span],
  [0, Math.min(span, 1.0)],         // shorter than the tail
  [0, Math.min(span, 4.0)],         // inside the overlap band (< 2 * tail)
  [span * 0.25, span * 0.75],
  [span * 0.5, span * 0.5 + 0.2],
  [Math.max(0, span - 0.3), span],
  [span * 0.1, span * 0.9],
];

for (const span of SPANS) {
  for (const [i, o] of CUTS(span)) {
    const w = normaliseWindow(span, i, o);
    for (const e of EDGES) {
      const a = auditionWindow(e, w);

      // A2 containment: the audition never plays material outside the range.
      assert(a.inSec >= w.inSec - 0 && a.outSec <= w.outSec + 0,
        `A2 contained (${e}, span=${span}, in=${i}, out=${o})`);

      // A3 the cut edge is pinned EXACTLY.
      if (e === 'in') {
        assert(Object.is(a.inSec, w.inSec), `A3 IN audition starts AT the cut (span=${span}, in=${i})`);
      } else {
        assert(Object.is(a.outSec, w.outSec), `A3 OUT audition ends AT the cut (span=${span}, out=${o})`);
      }

      // A4 length: the tail, or the whole range when the range is shorter.
      assert(approx(a.length, Math.min(AUDITION_TAIL_SEC, w.length)),
        `A4 length = min(tail, range) (${e}, span=${span}, len=${w.length})`);
      assert(a.length <= w.length + 1e-12,
        `A4 never longer than the range (${e}, span=${span})`);

      // A5 overlap band: on a short range both edges audition the SAME window.
      if (w.length <= AUDITION_TAIL_SEC && w.length > 0) {
        const other = auditionWindow(e === 'in' ? 'out' : 'in', w);
        assert(approx(a.inSec, other.inSec) && approx(a.outSec, other.outSec),
          `A5 sub-tail range: both edges audition the whole range (span=${span})`);
      }
    }
  }
}

// -----------------------------------------------------------------------------
// A6 — THE WRAP IS liveWrapTarget's, INCLUDING ON A FULL TRIM WINDOW.
// -----------------------------------------------------------------------------
const rand = mulberry32(0xC3652);
for (let k = 0; k < 4000; k++) {
  const span = 0.05 + rand() * 300;
  const untrimmed = rand() < 0.25;
  const lo = untrimmed ? undefined : rand() * span;
  const hi = untrimmed ? undefined : lo + rand() * (span - lo);
  const w = normaliseWindow(span, lo, hi);
  const e = rand() < 0.5 ? 'in' : 'out';
  const a = auditionWindow(e, w);
  const t = -1 + rand() * (span + 4);

  const got = auditionWrap(e, w, t);
  const want = liveWrapTarget({ window: a, loop: true, rate: 1 }, t);
  assert(Object.is(got, want),
    `A6 wrap == liveWrapTarget over the sub-window (span=${span.toFixed(3)}, e=${e}, t=${t.toFixed(3)})`);

  if (a.length > 0) {
    // Past the cut-side boundary: come round to the audition start, exactly.
    assert(Object.is(auditionWrap(e, w, a.outSec + 0.01), a.inSec),
      `A6 past the end -> audition start (${e})`);
    // Inside, clear of the slop: leave it playing.
    const mid = a.inSec + a.length / 2;
    if (mid >= a.inSec + LIVE_WINDOW_SLOP_SEC && mid < a.outSec) {
      assert(auditionWrap(e, w, mid) === null, `A6 inside -> no seek (${e})`);
    }
    // Stale position from before the handle moved: pull up to the start.
    if (a.inSec > LIVE_WINDOW_SLOP_SEC + 1e-6) {
      assert(Object.is(auditionWrap(e, w, a.inSec - LIVE_WINDOW_SLOP_SEC - 1e-4), a.inSec),
        `A6 before the start -> audition start (${e})`);
    }
  }
}

// The named case A6 exists for: an UNTRIMMED track (w.full === true) still
// audition-loops — liveWrapTarget on the RAW window would return null forever.
{
  const w = normaliseWindow(6, undefined, undefined);
  assert(w.full === true, 'A6 fixture: untrimmed window really is full');
  assert(liveWrapTarget({ window: w, loop: true, rate: 1 }, 7) === null,
    'A6 fixture: the raw full window never wraps — the trap being steered around');
  assert(Object.is(auditionWrap('in', w, AUDITION_TAIL_SEC + 0.01), 0),
    'A6 untrimmed IN audition wraps to 0');
  assert(Object.is(auditionWrap('out', w, 6.01), 6 - AUDITION_TAIL_SEC),
    'A6 untrimmed OUT audition wraps to span - tail');
}

console.log(`audition.invariants: ${checks} checks, ${fails} failures`);
process.exit(fails ? 1 : 0);
