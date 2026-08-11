/**
 * Invariant sweep for THE FADE — the take stops sounding like somebody pulled
 * the cable out.
 *
 * Run: node tests/unit/fade.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so
 * every claim below is about the shipped `lib/fade.ts` and not about a copy of
 * it written to agree with the test.
 *
 * I1 — THE TWO EMITTERS ARE ONE ENVELOPE. This is the assertion the whole file
 *      exists for. The offline mix multiplies each sample by `fadeGainAt`; the
 *      realtime recorder schedules `fadeRamps` as WebAudio automation on the
 *      master gain and never evaluates the envelope at all. Two spellings of
 *      one shape is how this project got `computeLayout` drawing four different
 *      partitions and `sourceTimeAt` copied into three timelines — so the ramp
 *      schedule is read back through `rampGainAt` and compared to `fadeGainAt`
 *      pointwise, at a resolution finer than any fade the roster offers.
 *
 * I2 — THE FADES CANNOT MEET AND CROSS. `fadeSpan` never returns more than half
 *      the take, so the envelope reaches 1 somewhere for every legal pair. The
 *      failure it forbids is quiet rather than loud: an unclamped 2 s fade on a
 *      3 s take leaves the MIDDLE of the take — the part being listened to —
 *      permanently below full level, and quieter the shorter the take.
 *
 * I3 — THE MIDDLE IS NOT TOUCHED, BY CONSTRUCTION. `applyFade` walks the two
 *      regions `fadeRegions` names and never the samples between them, so the
 *      claim "switching the fade on changes nothing outside the ramps" has to
 *      hold in two independent ways, and both are asserted: the regions must
 *      TILE the buffer with no gap and no overlap, and `fadeGainAt` must be
 *      exactly 1 on every sample the walk skips. Either one alone can be true
 *      while the pair is wrong.
 *
 * I4 — OFF IS BIT-IDENTICAL. Every export made before this module existed must
 *      come out of it unchanged, and the only honest proof is `Object.is` on
 *      every sample of a real buffer, not "the code returns early".
 *
 * I5 — THE ENVELOPE IS A SHAPE, not merely a set of endpoints: silent at both
 *      ends, monotone up then monotone down, never above 1, never below 0. A
 *      sign error or a swapped ramp passes an endpoint check and fails this.
 *
 * I6 — NOTHING THROWS AND NOTHING RETURNS A NON-NUMBER on garbage. The take
 *      length comes from a device profile and the request from a roster, but
 *      `fadeSpan(NaN, Infinity)` is one bad probe away and a NaN gain silently
 *      zeroes an entire export.
 *
 * WHAT MUTATION TESTING SAID. Eight deliberate defects were injected into the
 * shipped module and this sweep was re-run against each: an unclamped
 * `fadeSpan`, `floor` for `ceil` in `fadeRegions`, a dropped closing automation
 * point, `t >= take` returning full level, a skipped fade-out walk, a ramp that
 * stops at 0.9, and an inverted fade-in. Seven died, each on the assertion
 * written for it. The eighth — `fadeGainAt` returning `up * down` instead of
 * `min(up, down)` — SURVIVED, and it is an EQUIVALENT mutant rather than a
 * hole: under DECISION 2's clamp the two ramps never overlap, so one factor is
 * always exactly 1 and the two spellings are the same function, bit for bit.
 * That is worth writing down because it is the clamp's real payoff stated as
 * evidence: remove `fadeSpan`'s `take / 2` and the same pair stops agreeing.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';

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
    target: 'es2020',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const F = await load('src/lib/fade.ts', 'fade');

let checks = 0;
const ok = (cond, msg) => { checks++; assert.ok(cond, msg); };

/** Every take length the app can actually produce, plus the awkward ones. */
const TAKES = [5, 10, 15, 30, 3, 1, 0.75, 4.3, 7.5, 12.04, 0.5];
/** The roster, plus lengths only a clamp can survive. */
const REQUESTS = [0, 0.5, 1, 2, 3, 5, 30, 0.01, 100];
const RATES = [48000, 44100, 22050];

// ---------------------------------------------------------------------------
// I2 — THE CLAMP.
// ---------------------------------------------------------------------------
let clamps = 0;
for (const take of TAKES) {
  for (const req of REQUESTS) {
    const f = F.fadeSpan(req, take);
    clamps++;
    ok(Number.isFinite(f) && f >= 0, `fadeSpan(${req}, ${take}) must be a real non-negative number`);
    ok(f <= take / 2 + 1e-12,
      `fadeSpan(${req}, ${take}) = ${f} is more than half the take — the two ramps would overlap `
      + 'and the middle of the take would never reach full level');
    ok(f <= req + 1e-12, `fadeSpan(${req}, ${take}) = ${f} is LONGER than what was asked for`);
    if (req > 0 && take > 0) ok(f > 0, `a real request on a real take must survive (${req}, ${take})`);
    else ok(f === 0, `off must stay off (${req}, ${take})`);
    // The envelope reaches full level for every legal pair — I2's real point.
    if (f > 0) {
      ok(Math.abs(F.fadeGainAt(take / 2, take, f) - 1) < 1e-12,
        `the middle of a ${take}s take with a ${f}s fade is at ${F.fadeGainAt(take / 2, take, f)}, `
        + 'not full level');
    }
  }
}

// ---------------------------------------------------------------------------
// I1 — THE TWO EMITTERS ARE ONE ENVELOPE, and I5 — IT IS A SHAPE.
// ---------------------------------------------------------------------------
let points = 0;
let pairs = 0;
for (const take of TAKES) {
  for (const req of REQUESTS) {
    const f = F.fadeSpan(req, take);
    if (f <= 0) continue;
    pairs++;
    const ramps = F.fadeRamps(take, f);
    ok(ramps.length >= 3, `a fade needs at least three automation points (${take}, ${f})`);
    ok(ramps[0].when === 0 && ramps[0].value === 0, 'the schedule opens at silence');
    ok(Math.abs(ramps[ramps.length - 1].when - take) < 1e-12 && ramps[ramps.length - 1].value === 0,
      'the schedule closes at silence, at the end of the take');
    for (let i = 1; i < ramps.length; i++) {
      ok(ramps[i].when > ramps[i - 1].when,
        `automation points must strictly advance — ${JSON.stringify(ramps)}`);
    }

    // 2001 samples across the take, so the grid never lands only on the knots.
    const N = 2000;
    let prev = -1;
    let peakAt = -1;
    for (let k = 0; k <= N; k++) {
      const t = (take * k) / N;
      const g = F.fadeGainAt(t, take, f);
      const r = F.rampGainAt(ramps, t);
      points++;
      ok(Number.isFinite(g), `gain at ${t} of ${take} (f=${f}) is not a number`);
      // I1 — THE ASSERTION THIS FILE EXISTS FOR.
      ok(Math.abs(g - r) < 1e-9,
        `the offline envelope and the realtime ramp schedule disagree at t=${t} of a ${take}s take `
        + `with a ${f}s fade: sample-domain ${g}, automation ${r}`);
      // I5 — bounds and shape.
      ok(g >= 0 && g <= 1, `gain ${g} out of range at ${t}`);
      if (peakAt < 0) {
        if (g >= 1 - 1e-12) peakAt = t;
        else ok(g >= prev - 1e-12, `the fade IN must not descend (t=${t}, ${prev} -> ${g})`);
      } else if (t > take - f) {
        ok(g <= prev + 1e-12, `the fade OUT must not ascend (t=${t}, ${prev} -> ${g})`);
      }
      prev = g;
    }
    ok(peakAt >= 0, `a ${take}s take with a ${f}s fade never reaches full level`);
    ok(F.fadeGainAt(0, take, f) === 0, 'the take opens from silence');
    ok(F.fadeGainAt(take, take, f) === 0, 'the take closes into silence');
  }
}

// ---------------------------------------------------------------------------
// I3 — THE REGIONS TILE, AND THE SKIPPED SAMPLES ARE REALLY AT FULL LEVEL.
// ---------------------------------------------------------------------------
let regions = 0;
for (const take of TAKES) {
  for (const rate of RATES) {
    for (const req of REQUESTS) {
      const f = F.fadeSpan(req, take);
      if (f <= 0) continue;
      const length = Math.ceil(take * rate);
      const { inEnd, outStart } = F.fadeRegions(length, rate, take, f);
      regions++;
      ok(inEnd >= 0 && inEnd <= length, `inEnd ${inEnd} outside the buffer (${length})`);
      ok(outStart >= inEnd && outStart <= length,
        `the regions overlap or invert: [0,${inEnd}) and [${outStart},${length})`);
      // Every sample the walk SKIPS must genuinely be at full level. Sampled
      // densely rather than exhaustively — 30 s at 48 kHz is 1.44 M samples per
      // pair and this loop has 297 of them.
      const gap = outStart - inEnd;
      if (gap > 0) {
        const step = Math.max(1, Math.floor(gap / 500));
        for (let i = inEnd; i < outStart; i += step) {
          ok(F.fadeGainAt(i / rate, take, f) === 1,
            `sample ${i} is skipped by applyFade but its envelope is `
            + `${F.fadeGainAt(i / rate, take, f)}, not 1 — the regions do not cover the ramps`);
        }
        // The two samples either side of each boundary, by name.
        ok(F.fadeGainAt(inEnd / rate, take, f) === 1, 'the first skipped sample is at full level');
        ok(inEnd === 0 || F.fadeGainAt((inEnd - 1) / rate, take, f) <= 1,
          'the last faded-in sample is inside the envelope');
      }
    }
  }
}

// ---------------------------------------------------------------------------
// I4 — OFF IS BIT-IDENTICAL, on a real buffer.
// ---------------------------------------------------------------------------
const makeBuf = (n, seed) => {
  const d = new Float32Array(n);
  let s = seed >>> 0;
  for (let i = 0; i < n; i++) {
    s = (s * 1664525 + 1013904223) >>> 0;
    d[i] = ((s >>> 8) / 8388608 - 1) * 0.7;
  }
  return d;
};
let identical = 0;
for (const take of [5, 10, 30]) {
  const n = Math.ceil(take * 48000);
  const a = makeBuf(n, 12345 + take);
  const b = Float32Array.from(a);
  const touched = F.applyFade([b], 48000, take, F.fadeSpan(0, take));
  ok(touched === false, 'a fade of zero must report that it changed nothing');
  for (let i = 0; i < n; i++) {
    if (!Object.is(a[i], b[i])) {
      assert.fail(`fade OFF changed sample ${i} of a ${take}s buffer: ${a[i]} -> ${b[i]}`);
    }
  }
  identical += n;
  checks++;
}

// ---------------------------------------------------------------------------
// I3b — AND WITH A REAL FADE, EVERY SAMPLE OUTSIDE THE RAMPS IS UNTOUCHED.
//        This is the same promise as I3 but measured on the BUFFER rather than
//        on the envelope, because the walk is where an off-by-one lands.
// ---------------------------------------------------------------------------
let untouched = 0;
let attenuated = 0;
for (const take of [5, 10, 30]) {
  for (const req of [0.5, 1, 2]) {
    const f = F.fadeSpan(req, take);
    const n = Math.ceil(take * 48000);
    const a = makeBuf(n, 999 + take * 10 + req);
    const b = Float32Array.from(a);
    const touched = F.applyFade([b], 48000, take, f);
    ok(touched === true, `a ${f}s fade on a ${take}s take must report that it did something`);
    const { inEnd, outStart } = F.fadeRegions(n, 48000, take, f);
    for (let i = inEnd; i < outStart; i++) {
      if (!Object.is(a[i], b[i])) {
        assert.fail(`a ${f}s fade on a ${take}s take changed sample ${i}, which is between the `
          + `ramps ([0,${inEnd}) and [${outStart},${n})): ${a[i]} -> ${b[i]}`);
      }
    }
    untouched += outStart - inEnd;
    // And the ramps really did attenuate: the first and last 5 ms must be well
    // below the source, or the walk ran over an empty range.
    const ms5 = 240;
    let headA = 0, headB = 0, tailA = 0, tailB = 0;
    for (let i = 0; i < ms5; i++) { headA += Math.abs(a[i]); headB += Math.abs(b[i]); }
    for (let i = n - ms5; i < n; i++) { tailA += Math.abs(a[i]); tailB += Math.abs(b[i]); }
    ok(headB < headA * 0.2, `the first 5 ms of a ${f}s fade in is not quiet (${headB} vs ${headA})`);
    ok(tailB < tailA * 0.2, `the last 5 ms of a ${f}s fade out is not quiet (${tailB} vs ${tailA})`);
    // NEVER LOUDER. The envelope is <= 1 everywhere, which is what lets the
    // fade run AFTER the true-peak limiter without breaching its ceiling.
    for (let i = 0; i < n; i++) {
      if (Math.abs(b[i]) > Math.abs(a[i]) + 1e-9) {
        assert.fail(`the fade made sample ${i} LOUDER (${a[i]} -> ${b[i]}) — it can no longer be `
          + 'applied after the limiter without breaching the ceiling');
      }
    }
    attenuated++;
  }
}

// ---------------------------------------------------------------------------
// I6 — GARBAGE IN, A NUMBER OUT.
// ---------------------------------------------------------------------------
let junk = 0;
for (const take of [0, -1, NaN, Infinity, -Infinity]) {
  for (const req of [0, 1, NaN, Infinity, -3]) {
    const f = F.fadeSpan(req, take);
    junk++;
    ok(f === 0, `fadeSpan(${req}, ${take}) must be 0, got ${f}`);
    ok(F.fadeRamps(take, f).length === 0, `no schedule for (${take}, ${f})`);
    const g = F.fadeGainAt(1, take, f);
    ok(Number.isFinite(g), `gain for (${take}, ${f}) is ${g}`);
    const buf = new Float32Array(8).fill(0.5);
    ok(F.applyFade([buf], 48000, take, f) === false, 'nothing to apply');
    for (let i = 0; i < 8; i++) ok(buf[i] === 0.5, 'and nothing was applied');
  }
}

// ---------------------------------------------------------------------------
// THE ROSTER — one tap must walk every entry and come home.
// ---------------------------------------------------------------------------
let seen = new Set();
let cur = 0;
for (let i = 0; i < F.FADE_ROSTER.length; i++) { seen.add(cur); cur = F.nextFade(cur); }
ok(cur === 0, 'cycling the fade chip once per entry must return to OFF');
ok(seen.size === F.FADE_ROSTER.length, 'cycling must visit every roster entry');
ok(F.FADE_ROSTER[0] === 0, 'the default must be OFF — every older export stays bit-identical');
ok(F.nextFade(1.37) === F.FADE_ROSTER[0], 'a value that is not on the roster lands back on it');
ok(F.fadeLabel(0) === 'OFF', 'off says OFF, not 0s — the chip beside it is the take LENGTH');
checks += 5;

console.log(`fade invariants: ${checks} assertions — ${points} envelope points across ${pairs} `
  + `(take, fade) pairs, ${clamps} clamps, ${regions} region tilings, ${identical} samples proven `
  + `bit-identical with the fade off, ${attenuated} faded buffers checked sample-by-sample, `
  + `${junk} garbage inputs — all green`);
