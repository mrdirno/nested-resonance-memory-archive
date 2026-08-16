/**
 * Invariant sweep for THE RANGE FADE — the cut you chose stops arriving as a
 * click.
 *
 * Run: node tests/unit/windowFade.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * every claim below is about the shipped `lib/windowFade.ts` + `lib/clipWindow.ts`
 * and not about a copy written to agree with the test.
 *
 * I1 — THE TWO EMITTERS ARE ONE ENVELOPE, AND THE ENVELOPE IS A FUNCTION OF
 *      SOURCE POSITION. This is the assertion the file exists for. The mixer
 *      schedules `mixWindowRamps` on a gain node and never evaluates the
 *      envelope; the monitor schedules `liveWindowRamps` from the element's own
 *      clock and never sees the mix. Both are read back through `fade.rampGainAt`
 *      and compared to `windowFadeGainAt` composed with `schedulePositionAt` —
 *      the model of the nodes the mixer actually builds. Two spellings of one
 *      shape is how this project got `sourceTimeAt` copied into three timelines.
 *
 * I2 — THE CLAMP IS A QUARTER, NOT A HALF. `fadeSpan`'s half is safe for a take
 *      that plays ONCE; a WINDOW laps, so the same clamp makes a short loop a
 *      triangle wave. The assertion is the consequence rather than the number:
 *      at least half of every lap must sit at exactly full level.
 *
 * I3 — OFF IS NOTHING AT ALL. Not "an envelope of ones" — no ramps, so the mixer
 *      builds no node and the graph is the one that shipped. Swept over garbage
 *      too, because the exported API can be handed anything.
 *
 * I4 — THE OUT EDGE IS `audibleEnd`, NEVER `outSec`. When a container's audio is
 *      shorter than its video the sound stops BEFORE the OUT point, and a ramp
 *      scheduled at OUT never runs — the control would do nothing on exactly the
 *      clips whose splice is harshest. Asserted where it bites: the straddle case.
 *
 * I5 — `lapEdges` IS `audioSchedule`'S OWN ARITHMETIC, not a second copy of it.
 *      The lap boundaries the fade walks must be the `when`s of the schedule's
 *      own entries, and `phase` must be `sourceTimeAt` minus the IN point. If
 *      these two ever disagree the fade sits beside the splice instead of on it.
 *
 * I6 — THE SCHEDULE IS SCHEDULABLE. Strictly advancing `when`s (a ramp over a
 *      zero-length span is the degenerate event `fade.ts` refuses to emit),
 *      values inside [0,1], nothing non-finite — a NaN reaching an `AudioParam`
 *      silences a whole source.
 *
 * I7 — IT IS BOUNDED. A source lapping thousands of times in a take cannot emit
 *      an unbounded automation list, and past the cap it must degrade to FULL
 *      LEVEL (what shipped) rather than to silence.
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

const W = await load('src/lib/windowFade.ts', 'windowfade');
const C = await load('src/lib/clipWindow.ts', 'clipwindow');
const F = await load('src/lib/fade.ts', 'fade');

let checks = 0;
const ok = (cond, msg) => { checks++; assert.ok(cond, msg); };

/** Real files, real cuts. `spanLimit` is the DECODED audio length, which is
 *  shorter than the picture on the straddle rows — the case that produced the
 *  lap defect and the case this fade must still land on. */
const CASES = [];
for (const span of [6, 30, 180, 0.6, 2.5]) {
  for (const cut of [[0, 1], [0.25, 0.75], [0.5, 1], [0, 0.34]]) {
    for (const loop of [true, false]) {
      for (const rate of [1, 2, 0.5, 4]) {
        for (const limit of [undefined, span, span * 0.45]) {
          CASES.push({
            span,
            inSec: span * cut[0],
            outSec: span * cut[1],
            loop,
            rate,
            spanLimit: limit,
          });
        }
      }
    }
  }
}
const REQUESTS = [0, 0.1, 0.5, 1, 2, 30, 0.001, -1, NaN, Infinity, undefined];
const TAKES = [5, 15, 30];

const playbackOf = (c) => ({
  window: C.normaliseWindow(c.span, c.inSec, c.outSec),
  loop: c.loop,
  rate: c.rate,
});

// ---------------------------------------------------------------------------
// I2 — THE CLAMP IS A QUARTER.
// ---------------------------------------------------------------------------
let clamps = 0;
for (const c of CASES) {
  const p = playbackOf(c);
  const lenA = W.audibleLength(p.window, c.spanLimit);
  for (const req of REQUESTS) {
    const f = W.windowFadeSpan(req, lenA);
    clamps++;
    ok(Number.isFinite(f) && f >= 0, `windowFadeSpan(${req}, ${lenA}) must be real and non-negative`);
    ok(f <= lenA / 4 + 1e-12,
      `windowFadeSpan(${req}, ${lenA}) = ${f} is more than a QUARTER of the lap — on a looping `
      + 'window that is tremolo, not a fade');
    const asked = W.safeFade(req);
    ok(f <= asked + 1e-12, `windowFadeSpan(${req}, ${lenA}) = ${f} is longer than what was asked for`);
    if (asked > 0 && lenA > 0) ok(f > 0, `a real request on real audio must survive (${req}, ${lenA})`);
    else ok(f === 0, `off must stay off (${req}, ${lenA})`);
    if (f > 0) {
      // THE POINT of the quarter: the middle HALF of every lap is untouched.
      for (const frac of [0.25, 0.4, 0.5, 0.6, 0.75]) {
        const pos = p.window.inSec + lenA * frac;
        ok(Math.abs(W.windowFadeGainAt(pos, p.window.inSec, lenA, f) - 1) < 1e-12,
          `the middle of a ${lenA}s lap with a ${f}s fade is not at full level at ${frac}`);
      }
    }
  }
}

// ---------------------------------------------------------------------------
// I3 — OFF IS NOTHING AT ALL.
// ---------------------------------------------------------------------------
let offs = 0;
for (const c of CASES) {
  const p = playbackOf(c);
  for (const req of [0, -1, NaN, Infinity, undefined, null]) {
    for (const take of TAKES) {
      offs++;
      const ramps = W.mixWindowRamps(p, 0, take, c.spanLimit, W.safeFade(req));
      ok(ramps.length === 0,
        `OFF must emit NO automation (got ${ramps.length}) — the mixer builds no node at all, `
        + 'which is what makes an export with the fade off the one that shipped');
      const live = W.liveWindowRamps(p.window.inSec, p.window.inSec, 10, W.safeFade(req), c.rate);
      ok(live.length === 0, 'OFF must emit no live automation either');
    }
  }
}

// ---------------------------------------------------------------------------
// I5 — `lapEdges` IS `audioSchedule`'S OWN ARITHMETIC.
// ---------------------------------------------------------------------------
let edgeChecks = 0;
let strad = 0;
for (const c of CASES) {
  const p = playbackOf(c);
  for (const at of [0, 1.7, 40]) {
    const e = C.lapEdges(p, at);
    edgeChecks++;
    // phase is `sourceTimeAt` minus IN — the formula this project keeps exactly
    // one of.
    const fromFormula = C.sourceTimeAt(p, at) - p.window.inSec;
    ok(Math.abs(e.phase - fromFormula) < 1e-9,
      `lapEdges.phase (${e.phase}) disagrees with sourceTimeAt (${fromFormula}) — `
      + `${JSON.stringify(c)} at ${at}`);
    if (e.loops) {
      ok(e.period > 0 && Number.isFinite(e.period), 'a looping source has a real period');
      ok(e.first > 0 && Number.isFinite(e.first), 'the first boundary is ahead of the mix start');
    }
  }
  // And the boundaries are the ones the LAPPED schedule actually starts nodes on.
  for (const take of TAKES) {
    const sched = C.audioSchedule(p, 0, take, c.spanLimit);
    if (!sched.lapped) continue;
    strad++;
    const e = C.lapEdges(p, 0);
    const later = sched.starts.filter((s) => s.when > 0);
    later.forEach((s, k) => {
      edgeChecks++;
      ok(Math.abs(s.when - (e.first + k * e.period)) < 1e-9,
        `lap ${k} starts at ${s.when} but lapEdges says ${e.first + k * e.period} — the fade would `
        + 'sit beside the splice instead of on it');
    });
  }
}
ok(strad > 0, 'the sweep must actually reach the straddle case');

// ---------------------------------------------------------------------------
// I1 — ONE ENVELOPE, and I4 — THE OUT EDGE IS `audibleEnd`, and I6 — SCHEDULABLE.
// ---------------------------------------------------------------------------
let samples = 0;
let schedules = 0;
let liveSchedules = 0;
let sawSilentGap = 0;
for (const c of CASES) {
  const p = playbackOf(c);
  const lenA = W.audibleLength(p.window, c.spanLimit);
  for (const take of TAKES) {
    for (const req of [0.1, 0.5, 1]) {
      const f = W.windowFadeSpan(req, lenA);
      if (!(f > 0)) continue;
      const ramps = W.mixWindowRamps(p, 0, take, c.spanLimit, req);
      if (!ramps.length) {
        // Only legal when there is nothing to fade.
        ok(!(lenA > 0), `a source with ${lenA}s of audio emitted no envelope`);
        continue;
      }
      schedules++;

      // I6 — schedulable.
      ok(ramps[0].when === 0, 'the mix schedule must open at output 0');
      for (let i = 0; i < ramps.length; i++) {
        ok(Number.isFinite(ramps[i].when) && Number.isFinite(ramps[i].value),
          `non-finite automation point ${JSON.stringify(ramps[i])} — a NaN on an AudioParam `
          + 'silences the whole source');
        ok(ramps[i].value >= 0 && ramps[i].value <= 1,
          `automation value ${ramps[i].value} is outside [0,1]`);
        if (i > 0) {
          ok(ramps[i].when > ramps[i - 1].when,
            `automation must strictly advance: ${ramps[i - 1].when} then ${ramps[i].when}`);
        }
      }
      ok(ramps.length <= 4 * C.MAX_AUDIO_LAPS + 8, `unbounded automation list: ${ramps.length}`);

      // I1 — the schedule reads back as the envelope of the modelled position.
      const sched = C.audioSchedule(p, 0, take, c.spanLimit);
      const N = 601;
      for (let i = 0; i < N; i++) {
        const u = (take * i) / (N - 1);
        const pos = C.schedulePositionAt(sched.starts, u);
        const read = F.rampGainAt(ramps, u);
        samples++;
        if (pos === null) {
          // No node is sounding: the envelope must be closed, not open.
          if (read > 1e-6) sawSilentGap++;
          ok(read <= 1e-6,
            `at output ${u.toFixed(4)} the mix has NO sound but the envelope reads ${read} — `
            + `${JSON.stringify(c)}`);
          continue;
        }
        const want = W.windowFadeGainAt(pos, p.window.inSec, lenA, f);
        ok(Math.abs(read - want) < 2e-5,
          `at output ${u.toFixed(4)} the scheduled envelope reads ${read} but the source is at `
          + `${pos.toFixed(5)}, where the envelope is ${want} — ${JSON.stringify(c)} f=${f}`);
      }

      // I4 — on a straddling source the fade-out lands where the SOUND ends.
      if (sched.lapped) {
        const e = C.lapEdges(p, 0);
        const lapStart = e.first;
        if (lapStart + e.period < take) {
          const outAt = lapStart + lenA / C.safeRate(c.rate);
          ok(F.rampGainAt(ramps, outAt) <= 1e-6,
            'the envelope must be closed where the audio actually ends, not at the OUT point');
          const mid = (outAt + lapStart + e.period) / 2;
          if (mid > outAt + 1e-6 && mid < lapStart + e.period - 1e-6) {
            ok(F.rampGainAt(ramps, mid) <= 1e-6,
              'past the end of the audio the envelope stays closed until the next lap');
          }
        }
      }

      // I1, live half — the monitor's schedule is the same envelope, read from
      // wherever the element happens to be.
      for (const frac of [0, 0.13, 0.5, 0.87, 0.999]) {
        const pos = p.window.inSec + lenA * frac;
        const live = W.liveWindowRamps(pos, p.window.inSec, lenA, f, c.rate);
        if (!live.length) continue;
        liveSchedules++;
        for (let i = 1; i < live.length; i++) {
          ok(live[i].when > live[i - 1].when, 'live automation must strictly advance');
        }
        const remaining = (lenA - lenA * frac) / C.safeRate(c.rate);
        for (let k = 0; k <= 40; k++) {
          const u = (remaining * k) / 40;
          const read = F.rampGainAt(live, u);
          const want = W.windowFadeGainAt(pos + u * C.safeRate(c.rate), p.window.inSec, lenA, f);
          samples++;
          ok(Math.abs(read - want) < 2e-5,
            `the LIVE schedule and the envelope disagree ${u.toFixed(4)}s after arming at `
            + `${pos.toFixed(4)}: ${read} vs ${want}`);
        }
      }
    }
  }
}

// ---------------------------------------------------------------------------
// I7 — THE CAP DEGRADES TO FULL LEVEL, NEVER TO SILENCE.
// ---------------------------------------------------------------------------
{
  // A 62 ms source in a long take — the cheapest real reproduction of the lap
  // cap, borrowed verbatim from `MAX_AUDIO_LAPS`' own docstring.
  const p = { window: C.normaliseWindow(0.062, 0, 0.062), loop: true, rate: 1 };
  const ramps = W.mixWindowRamps(p, 0, 170, undefined, 0.5);
  ok(ramps.length <= 4 * C.MAX_AUDIO_LAPS + 8,
    `a strobing source emitted ${ramps.length} automation points`);
  ok(ramps.length > 0, 'a strobing source still gets an envelope for the part it can');
  checks++;
}

// ---------------------------------------------------------------------------
// NOTHING THROWS ON GARBAGE.
// ---------------------------------------------------------------------------
for (const bad of [NaN, Infinity, -Infinity, -5, 0]) {
  const p = { window: C.normaliseWindow(bad, bad, bad), loop: true, rate: bad };
  const r = W.mixWindowRamps(p, bad, bad, bad, bad);
  ok(Array.isArray(r), 'mixWindowRamps must always return a list');
  const l = W.liveWindowRamps(bad, bad, bad, bad, bad);
  ok(Array.isArray(l), 'liveWindowRamps must always return a list');
  ok(Number.isFinite(W.windowFadeGainAt(bad, bad, bad, bad)), 'the envelope must never return NaN');
}

console.log(
  `windowFade invariants OK — ${checks} assertions | ${CASES.length} clip cases | `
  + `${clamps} clamps | ${offs} off-rows | ${edgeChecks} lap-edge checks (${strad} straddles) | `
  + `${schedules} mix schedules + ${liveSchedules} live schedules | ${samples} envelope samples`,
);
