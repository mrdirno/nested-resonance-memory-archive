/**
 * INVARIANT SWEEP for src/lib/clipWindow.ts — the trim window and the one
 * output-time -> source-time formula the three timelines share.
 *
 *   node tests/unit/clipWindow.invariants.mjs
 *
 * Transpiles and imports the REAL modules (clipWindow + videoSync). No
 * re-implementation — a sweep against a copy grades the copy.
 *
 * THE TWO THAT CARRY THE CYCLE
 *   I2  the untrimmed path is BIT-IDENTICAL to the formula this replaced, so
 *       every existing project renders exactly as it did. `Object.is`, not
 *       `approx`: "close enough" is how a scale bug hides (see the ONE LAYOUT
 *       scar, where two doubles apart changed the cell COUNT).
 *   I7  the audio plan and the video seek put the clip at the SAME source time.
 *       Asserted against a model of `AudioBufferSourceNode` rather than against
 *       a second copy of the algebra, because the previous version of this
 *       agreement lived in a comment and a comment cannot go red.
 */
import esbuild from 'esbuild';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');
const dir = mkdtempSync(join(tmpdir(), 'clipwin-'));

const load = async (rel, out) => {
  const src = readFileSync(join(root, rel), 'utf8');
  const { code } = await esbuild.transform(src, { loader: 'ts', format: 'esm' });
  const tmp = join(dir, out);
  writeFileSync(tmp, code);
  return import(pathToFileURL(tmp).href);
};

const CW = await load('src/lib/clipWindow.ts', 'clipWindow.mjs');
const VS = await load('src/lib/videoSync.ts', 'videoSync.mjs');

const {
  normaliseWindow, sourceTimeAt, effectiveLength, audioPlan, audioPositionAt,
  audioSchedule, schedulePositionAt, MAX_AUDIO_LAPS,
  liveWrapTarget, safeRate, MIN_WINDOW_SEC, LIVE_WINDOW_SLOP_SEC,
} = CW;
const { computeClipPlayback } = VS;

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };
const approx = (a, b, eps = 1e-9) =>
  Math.abs(a - b) <= eps * Math.max(1, Math.abs(a), Math.abs(b));
/** Distance on a circle of circumference len — the honest metric for a wrapped
 *  timeline, where 1e-16 before the wrap and 1e-16 after it are NEIGHBOURS. */
const circDist = (a, b, len) => {
  const d = Math.abs(a - b) % len;
  return Math.min(d, len - d);
};

// -----------------------------------------------------------------------------
// THE SUBJECT SPACE — spans the app really sees, plus the hostile ones.
// -----------------------------------------------------------------------------
const SPANS = [0.05, 0.14, 0.15, 0.6, 1.6, 3.996, 4.0, 8.4, 27.3, 120, 600];
const RATES = [1, 0.4127, 0.0625, 2.4390, 16, 0.9999999, 3];
const WINDOWS = (span) => [
  [undefined, undefined],                     // untrimmed — the default path
  [0, span],                                  // untrimmed, stated explicitly
  [0, span / 2],                              // head
  [span / 2, span],                           // tail
  [span / 3, (2 * span) / 3],                 // middle third
  [0.01, span - 0.01],                        // a hair off both ends
  [span * 0.9, span],                         // short tail
  [span - 0.02, span],                        // below the floor -> repaired
  [span, 0],                                  // inverted
  [-5, span * 2],                             // out of range both sides
  [NaN, span / 2],                            // half-known
  [span / 4, Infinity],                       // half-known the other way
  [1, 1],                                     // degenerate
];

// =============================================================================
// I1 — normaliseWindow is TOTAL. No input produces a window a consumer must
//      re-check, because a consumer that re-checks is a fourth copy of it.
// =============================================================================
const HOSTILE = [
  undefined, null, NaN, Infinity, -Infinity, 0, -1, -0.0001, 1e-12, 1e12,
  0.15, 0.1499999, 5,
];
for (const span of [...SPANS, ...HOSTILE]) {
  for (const a of HOSTILE) {
    for (const b of HOSTILE) {
      const w = normaliseWindow(span, a, b);
      ok();
      if (!Number.isFinite(w.inSec) || !Number.isFinite(w.outSec) || !Number.isFinite(w.length)) {
        fail(`I1 non-finite window from span=${span} in=${a} out=${b} -> ${JSON.stringify(w)}`);
        continue;
      }
      ok(); if (w.inSec < 0) fail(`I1 negative IN ${w.inSec} (span=${span} ${a}/${b})`);
      ok(); if (w.length < 0) fail(`I1 negative length ${w.length} (span=${span} ${a}/${b})`);
      ok(); if (w.outSec < w.inSec) fail(`I1 inverted ${w.inSec}..${w.outSec} (span=${span} ${a}/${b})`);
      ok(); if (!approx(w.length, w.outSec - w.inSec, 1e-12)) fail(`I1 length != out-in (span=${span})`);
      if (Number.isFinite(span) && span > 0) {
        ok(); if (w.outSec > span + 1e-12) fail(`I1 OUT ${w.outSec} past span ${span} (${a}/${b})`);
        // The floor holds unless the clip itself is shorter than one window.
        const floor = Math.min(MIN_WINDOW_SEC, span);
        ok(); if (w.length + 1e-12 < floor) fail(`I1 window ${w.length} under floor ${floor} (span=${span} ${a}/${b})`);
      }
      ok(); if (w.full !== (w.inSec === 0 && Number.isFinite(span) && span > 0 ? w.outSec === span : w.full)) {
        fail(`I1 full flag disagrees with the window (span=${span} ${a}/${b})`);
      }
    }
  }
}

// =============================================================================
// I2 — THE COMPATIBILITY CLAUSE. Untrimmed is BIT-IDENTICAL to the pre-trim
//      formula, for every span, rate, loop flag and output time. This is what
//      lets trim ship without moving a single frame of anybody's existing work.
// =============================================================================
/** The expression that lived in `Stage.seekClipTo` before this module existed. */
const legacyTarget = (span, loop, rate, t) => {
  const r = rate > 0 ? rate : 1;
  const scaled = t * r;
  return loop ? scaled % span : Math.min(scaled, span);
};
for (const span of SPANS) {
  const w = normaliseWindow(span);            // absent in/out = the whole clip
  ok(); if (!w.full) fail(`I2 an absent window must be full (span=${span})`);
  ok(); if (w.inSec !== 0) fail(`I2 default IN must be exactly 0, got ${w.inSec}`);
  for (const rate of RATES) {
    for (const loop of [true, false]) {
      const p = { window: w, loop, rate };
      for (let i = 0; i <= 400; i++) {
        // Real output times: frame index / fps, plus a few awkward ones.
        const t = i / 30 + (i % 7) * 1e-3;
        const mine = sourceTimeAt(p, t);
        const old = legacyTarget(span, loop, rate, t);
        ok();
        if (!Object.is(mine, old)) {
          fail(`I2 NOT bit-identical span=${span} rate=${rate} loop=${loop} t=${t}: ${mine} vs ${old}`);
        }
      }
    }
  }
}

// =============================================================================
// I3/I4/I5/I6/I8 — the formula itself, over the whole subject space.
// =============================================================================
for (const span of SPANS) {
  for (const [a, b] of WINDOWS(span)) {
    const w = normaliseWindow(span, a, b);
    if (!(w.length > 0)) continue;
    for (const rate of RATES) {
      for (const loop of [true, false]) {
        const p = { window: w, loop, rate };
        const r = safeRate(rate);

        // --- I3 CONTAINMENT: never outside the window the user chose. --------
        let minSeen = Infinity, maxSeen = -Infinity;
        const N = 900;
        // Sweep several laps of the window in output time, so a looping clip
        // genuinely wraps rather than being measured on its first pass only.
        const horizon = (w.length / r) * 3.7 + 1;
        for (let i = 0; i <= N; i++) {
          const t = (i / N) * horizon;
          const s = sourceTimeAt(p, t);
          ok();
          if (!(s >= w.inSec - 1e-9 && s <= w.outSec + 1e-9)) {
            fail(`I3 outside window span=${span} w=[${w.inSec},${w.outSec}] rate=${rate} loop=${loop} t=${t} -> ${s}`);
          }
          if (s < minSeen) minSeen = s;
          if (s > maxSeen) maxSeen = s;
        }

        // --- I6 COVERAGE: a looping window must actually USE its window ------
        // (a wrap that silently pins to one end is containment-clean and wrong).
        if (loop) {
          ok();
          if (Math.abs(minSeen - w.inSec) > w.length * 0.05) {
            fail(`I6 loop never reaches IN: min=${minSeen} in=${w.inSec} (span=${span} rate=${rate})`);
          }
          ok();
          if (w.outSec - maxSeen > w.length * 0.05) {
            fail(`I6 loop never reaches OUT: max=${maxSeen} out=${w.outSec} (span=${span} rate=${rate})`);
          }
        }

        // --- I4 MONOTONE WITHIN A LAP ----------------------------------------
        const lap = w.length / r;
        let prev = -Infinity;
        for (let i = 0; i <= 200; i++) {
          const t = (i / 201) * lap;          // strictly inside the first lap
          const s = sourceTimeAt(p, t);
          ok();
          if (s < prev - 1e-12) fail(`I4 non-monotone within a lap: ${prev} -> ${s} (span=${span} rate=${rate} loop=${loop})`);
          prev = s;
        }

        // --- I5 PERIODICITY (loop) -------------------------------------------
        if (loop) {
          for (let i = 0; i < 40; i++) {
            const t = (i / 40) * lap;
            const s0 = sourceTimeAt(p, t);
            const s1 = sourceTimeAt(p, t + lap);
            ok();
            if (circDist(s0, s1, w.length) > 1e-6) {
              fail(`I5 not periodic at t=${t} lap=${lap}: ${s0} vs ${s1} (span=${span} rate=${rate})`);
            }
          }
        }

        // --- I8 NON-LOOP CLAMPS AT OUT AND STAYS ------------------------------
        if (!loop) {
          const far = sourceTimeAt(p, lap * 9 + 100);
          ok();
          if (!approx(far, w.outSec, 1e-12)) fail(`I8 non-loop did not hold at OUT: ${far} vs ${w.outSec}`);
          const farther = sourceTimeAt(p, lap * 90 + 1e5);
          ok();
          if (!Object.is(far, farther)) fail(`I8 non-loop kept moving past OUT: ${far} -> ${farther}`);
        }
      }
    }
  }
}

// =============================================================================
// I7 — THE AUDIO AND THE PICTURE ARE AT THE SAME PLACE.
//      `audioPlan` configures the node; `audioPositionAt` models what the node
//      then does; `sourceTimeAt` is where the picture is. The first two must
//      reproduce the third for every output time the render walks.
//
//      NOTE the metric. A looping timeline is a CIRCLE: `(startAt+u)*r` and
//      `startAt*r + u*r` are the same number in exact arithmetic and differ in
//      the last bits in floating point, so near a wrap one lands at 1e-16 and
//      the other at len-1e-16. Those are adjacent, not `len` apart, and a naive
//      |a-b| would report a catastrophic failure for a one-ULP difference.
// =============================================================================
for (const span of SPANS) {
  for (const [a, b] of WINDOWS(span)) {
    const w = normaliseWindow(span, a, b);
    if (!(w.length > 0)) continue;
    for (const rate of RATES) {
      for (const loop of [true, false]) {
        const p = { window: w, loop, rate };
        const r = safeRate(rate);
        for (const startAt of [0, 0.0333, 1, 2.5, w.length / r / 2, 13.7]) {
          const plan = audioPlan(p, startAt);

          // The offset IS the picture's position at the output's start time —
          // by construction, and now by assertion.
          ok();
          if (!Object.is(plan.offset, sourceTimeAt(p, startAt))) {
            fail(`I7a offset != sourceTimeAt(startAt): ${plan.offset} vs ${sourceTimeAt(p, startAt)}`);
          }
          // The node must never be told to loop OUTSIDE the window.
          if (plan.loop) {
            ok(); if (plan.loopStart !== w.inSec) fail(`I7b loopStart ${plan.loopStart} != IN ${w.inSec}`);
            ok(); if (plan.loopEnd !== w.outSec) fail(`I7b loopEnd ${plan.loopEnd} != OUT ${w.outSec}`);
          }
          ok(); if (plan.playbackRate !== r) fail(`I7b rate ${plan.playbackRate} != ${r}`);

          for (let i = 0; i <= 240; i++) {
            const u = (i / 240) * ((w.length / r) * 3.3 + 2);
            const pic = sourceTimeAt(p, startAt + u);
            const snd = audioPositionAt(plan, u);
            if (loop && plan.loop) {
              ok();
              if (circDist(pic, snd, w.length) > 1e-6) {
                fail(`I7 A/V drift ${circDist(pic, snd, w.length).toExponential(2)}s `
                  + `span=${span} w=[${w.inSec.toFixed(3)},${w.outSec.toFixed(3)}] rate=${rate} `
                  + `startAt=${startAt} u=${u}: pic=${pic} snd=${snd}`);
              }
            } else {
              // NON-LOOPING. They must agree while the picture is still moving —
              // AND the sound must be SILENT once the picture reaches OUT.
              //
              // The first version of this branch simply SKIPPED the comparison
              // past OUT, and that gate was written for the untrimmed case where
              // "past OUT" means "past the end of the file" and there is nothing
              // left to play. With a window, past OUT is the material the user
              // deliberately CUT, and an unbounded BufferSource plays it happily
              // under a frozen frame. An invariant that excuses the interesting
              // half is not an invariant.
              if ((startAt + u) * r < w.length) {
                ok();
                if (snd === null) fail(`I7 non-loop went silent while the picture was still moving (u=${u})`);
                else if (!approx(pic, snd, 1e-9)) {
                  fail(`I7 non-loop A/V drift span=${span} rate=${rate} startAt=${startAt} u=${u}: ${pic} vs ${snd}`);
                }
              } else if ((startAt + u) * r > w.length + 1e-6) {
                ok();
                if (snd !== null) {
                  fail(`I7 non-loop still sounding at source ${snd} after the picture froze at OUT ${w.outSec} `
                    + `(span=${span} rate=${rate} startAt=${startAt} u=${u})`);
                }
              }
            }
          }
        }
      }
    }
  }
}

// =============================================================================
// I9 — ULP ROBUSTNESS. The scar this project has twice: "a normalised coordinate
//      is the same NUMBER at every width and not the same FLOAT". Asserting
//      f(x) === f(x) proves nothing; the real question is whether an input that
//      SHOULD be the same but arrives a hair different answers the same.
// =============================================================================
const nextUp = (x) => {
  const buf = new DataView(new ArrayBuffer(8));
  buf.setFloat64(0, x);
  const hi = buf.getUint32(0), lo = buf.getUint32(4);
  if (lo === 0xffffffff) { buf.setUint32(0, hi + 1); buf.setUint32(4, 0); }
  else { buf.setUint32(4, lo + 1); }
  return buf.getFloat64(0);
};
for (const span of [4.0, 8.4, 27.3]) {
  for (const [a, b] of [[0, span], [span / 3, (2 * span) / 3], [span * 0.7, span]]) {
    const w = normaliseWindow(span, a, b);
    for (const rate of [1, 0.4127, 2.439]) {
      const p = { window: w, loop: true, rate };
      const r = safeRate(rate);
      const lap = w.length / r;
      for (let i = 1; i < 300; i++) {
        const t = (i / 300) * lap * 2.5;
        // Skip the immediate neighbourhood of a lap boundary: the wrap is a
        // genuine discontinuity there, by design, and the honest claim is that
        // there is no OTHER one.
        const phase = (t * r) % w.length;
        if (phase < 1e-4 || w.length - phase < 1e-4) continue;
        const t2 = nextUp(t);
        const d = Math.abs(sourceTimeAt(p, t2) - sourceTimeAt(p, t));
        ok();
        if (d > 1e-9) fail(`I9 one ULP of t moved the source time by ${d.toExponential(3)}s (span=${span} rate=${rate} t=${t})`);
        // And Lipschitz with constant r away from the wrap: no hidden step.
        const dt = 1e-7;
        const dd = Math.abs(sourceTimeAt(p, t + dt) - sourceTimeAt(p, t));
        ok();
        if (dd > r * dt * 1.000001 + 1e-12) {
          fail(`I9 step of ${dd.toExponential(3)} for dt=${dt} at rate ${r} (span=${span} t=${t})`);
        }
      }
    }
  }
}

// =============================================================================
// I10 — TRIM AND VIDEO-LENGTH SYNC COMPOSE. "Match the shortest clip" has to
//       mean the shortest thing the viewer SEES. Feed videoSync the WINDOW
//       lengths and every clip's on-screen period must come out equal.
// =============================================================================
const CLIP_SETS = [
  [[4.0, 1.0, 3.0], [1.6, 0, 1.6], [27.3, 10, 14]],
  [[120, 0, 120], [8.4, 2, 4], [3.996, 0.5, 3.9]],
  [[600, 599, 600], [0.6, 0, 0.6]],
];
for (const set of CLIP_SETS) {
  for (const mode of ['loop', 'stretch-longest', 'speed-shortest']) {
    const wins = set.map(([span, a, b]) => normaliseWindow(span, a, b));
    const timings = wins.map((w, i) => ({ id: `c${i}`, durationSec: w.length }));
    const playback = computeClipPlayback(timings, mode);
    const eff = wins.map((w, i) => effectiveLength({ window: w, loop: true, rate: playback[i].playbackRate }));

    ok();
    if (!eff.every((e) => Number.isFinite(e) && e > 0)) fail(`I10 non-positive effective length (${mode}) ${JSON.stringify(eff)}`);

    if (mode !== 'loop') {
      // Up to rate clamping, every clip now turns over on the same clock.
      const clamped = playback.some((p) => p.playbackRate <= 0.0625 + 1e-9 || p.playbackRate >= 16 - 1e-9);
      if (!clamped) {
        const target = eff[0];
        for (let i = 1; i < eff.length; i++) {
          ok();
          if (!approx(eff[i], target, 1e-6)) {
            fail(`I10 ${mode}: clip ${i} shows for ${eff[i]}s, clip 0 for ${target}s`);
          }
        }
      }
      // And it is the TRIMMED reference, not the file's duration — the whole
      // reason this invariant exists.
      const lens = wins.map((w) => w.length);
      const want = mode === 'stretch-longest' ? Math.max(...lens) : Math.min(...lens);
      ok();
      if (!clamped && !approx(eff[0], want, 1e-6)) {
        fail(`I10 ${mode} synced to ${eff[0]}s, expected the trimmed ${want}s (spans were ${set.map((s) => s[0])})`);
      }
    }
  }
}

// =============================================================================
// I11 — THE LIVE WATCHDOG. An untrimmed clip must never be touched (that is
//       what keeps the default path free of new seeks); a trimmed one must be
//       pulled back into its window and nowhere else.
// =============================================================================
for (const span of SPANS) {
  const full = normaliseWindow(span);
  for (const loop of [true, false]) {
    for (let i = 0; i <= 50; i++) {
      const ct = (i / 50) * (span * 1.4) - span * 0.2;
      ok();
      if (liveWrapTarget({ window: full, loop, rate: 1 }, ct) !== null) {
        fail(`I11 untrimmed clip was seeked at currentTime=${ct} (span=${span})`);
      }
    }
  }
  if (span <= MIN_WINDOW_SEC * 2) continue;
  const w = normaliseWindow(span, span * 0.25, span * 0.75);
  for (const loop of [true, false]) {
    const p = { window: w, loop, rate: 1 };
    ok(); if (liveWrapTarget(p, NaN) !== null) fail('I11 NaN currentTime must be ignored');
    // Inside the window: leave it alone.
    for (let i = 1; i < 20; i++) {
      const ct = w.inSec + (i / 20) * w.length;
      ok(); if (liveWrapTarget(p, ct) !== null) fail(`I11 seeked from INSIDE the window at ${ct} ([${w.inSec},${w.outSec}])`);
    }
    // Past OUT: loop goes back to IN, non-loop holds.
    for (const ct of [w.outSec, w.outSec + 1e-6, w.outSec + 5, span]) {
      const target = liveWrapTarget(p, ct);
      ok();
      if (loop && target !== w.inSec) fail(`I11 past OUT (${ct}) must wrap to IN, got ${target}`);
      ok();
      if (!loop && target !== null) fail(`I11 past OUT (${ct}) on a non-looping clip must hold, got ${target}`);
    }
    // Before IN — a native loop wrap to 0 lands here.
    for (const ct of [0, w.inSec - LIVE_WINDOW_SLOP_SEC - 1e-6]) {
      ok();
      if (liveWrapTarget(p, ct) !== w.inSec) fail(`I11 before IN (${ct}) must pull to IN ${w.inSec}, got ${liveWrapTarget(p, ct)}`);
    }
    // ...but not within one frame of it, or an ordinary decode jitter re-seeks
    // every single frame and the clip never advances.
    ok();
    if (liveWrapTarget(p, w.inSec - LIVE_WINDOW_SLOP_SEC / 2) !== null) {
      fail('I11 re-seeked on sub-frame jitter just before IN');
    }
  }
}

// =============================================================================
// I12 — A SHORTER AUDIO TRACK THAN VIDEO TRACK.
//
//       Containers do not promise the two streams are the same length, and
//       `loopEnd` past the decoded buffer is undefined behaviour. THE FIRST
//       VERSION OF THIS FAMILY ONLY CHECKED loopEnd, AND THAT IS EXACTLY WHY IT
//       MISSED THE REAL BUG: `audioPlan` re-ran `normaliseWindow` against the
//       BUFFER's span, whose minimum-window repair MOVED THE IN POINT. A 6 s
//       video with a 3 s audio track trimmed to 4→6 came back as [2.85, 3.00] —
//       loopEnd was inside the buffer, every old assertion held, and the export
//       looped the last 150 ms of the audio for the whole take with the clip's
//       real sound at exactly zero. Found by an adversarial audit driving the
//       real app; the assertions below are what should have found it.
// =============================================================================
for (const span of [0.6, 8.4, 27.3, 120]) {
  for (const [a, b] of WINDOWS(span)) {
    const w = normaliseWindow(span, a, b);
    if (!(w.length > 0)) continue;
    for (const bufDur of [span, span * 1.4, span * 0.999, span * 0.9, span * 0.55, span * 0.2, 0.05, 0]) {
      for (const loop of [true, false]) {
        for (const startAt of [0, 1.5, 40]) {
          const plan = audioPlan({ window: w, loop, rate: 1 }, startAt, bufDur);
          // A NON-POSITIVE buffer duration means "unknown", and `audioPlan`
          // correctly applies no limit at all — the same convention
          // `describeAudioSources` uses when a deferred clip has no decoder and
          // reports span 0. There is nothing to bound against in that case.
          const limit = bufDur > 0 ? bufDur : Infinity;

          // (a) THE IN POINT NEVER MOVES BECAUSE A DIFFERENT STREAM IS SHORT.
          //     This is the assertion that names the defect.
          if (!plan.silent) {
            ok();
            if (plan.loop && plan.loopStart !== w.inSec) {
              fail(`I12a loopStart ${plan.loopStart} != the user's IN ${w.inSec} (span=${span} buf=${bufDur})`);
            }
            ok();
            if (plan.offset < w.inSec - 1e-12) {
              fail(`I12a offset ${plan.offset} before the user's IN ${w.inSec} (span=${span} buf=${bufDur})`);
            }
          }

          // (b) A WINDOW ENTIRELY PAST THE AUDIO IS SILENCE, NOT A FRAGMENT.
          const overlap = Math.min(w.outSec, limit) - w.inSec;
          ok();
          if (overlap <= 0 && !plan.silent) {
            fail(`I12b window [${w.inSec},${w.outSec}] is past a ${bufDur}s buffer and the plan is NOT silent: ${JSON.stringify(plan)}`);
          }
          ok();
          if (overlap > 1e-9 && plan.silent) {
            fail(`I12b ${overlap}s of audio overlaps the window and the plan says silent (span=${span} buf=${bufDur})`);
          }
          if (plan.silent) {
            ok(); if (audioPositionAt(plan, 1) !== null) fail('I12b a silent plan must have no position');
            continue;
          }

          // (c) EVERYTHING THE NODE IS TOLD STAYS INSIDE THE BUFFER.
          ok(); if (plan.loopEnd > limit + 1e-9) fail(`I12c loopEnd ${plan.loopEnd} past buffer ${bufDur} (span=${span})`);
          ok(); if (plan.offset > limit + 1e-9) fail(`I12c offset ${plan.offset} past buffer ${bufDur}`);
          ok(); if (plan.loop && !(plan.loopEnd > plan.loopStart)) fail(`I12c empty loop region [${plan.loopStart},${plan.loopEnd}] (buf=${bufDur})`);
          ok(); if (!Number.isFinite(plan.offset)) fail(`I12c non-finite offset (buf=${bufDur})`);

          // (d) A NON-LOOPING NODE IS BOUNDED AT THE OUT POINT. Left unbounded a
          //     BufferSource plays to the END OF THE BUFFER — i.e. through
          //     everything the user trimmed away, under a frozen picture.
          if (!plan.loop) {
            ok();
            if (plan.stopAfter === null) fail(`I12d a non-looping plan must bound itself (span=${span} buf=${bufDur})`);
            else {
              ok();
              if (plan.offset + plan.stopAfter > Math.min(w.outSec, limit) + 1e-9) {
                fail(`I12d sound runs to ${plan.offset + plan.stopAfter}, past OUT ${w.outSec} / buffer ${bufDur}`);
              }
              ok();
              if (audioPositionAt(plan, (plan.stopAfter + 0.5)) !== null) {
                fail(`I12d the node is still sounding past its own stopAfter (span=${span} buf=${bufDur})`);
              }
            }
          } else {
            ok(); if (plan.stopAfter !== null) fail('I12d a looping plan is bounded by its loop region, not a stop');
          }
        }
      }
    }
  }
}

// =============================================================================
// I14 — `full` IS PINNED FOR EVERY WINDOW, not just the ones starting at 0.
//       It is what decides whether the live element keeps its NATIVE loop, so a
//       `full` that drifts from "is this genuinely the whole clip" silently
//       changes playback for clips nobody trimmed.
// =============================================================================
for (const span of [...SPANS, 0.15, 0.1499]) {
  if (!Number.isFinite(span) || span <= 0) continue;
  for (const [a, b] of WINDOWS(span)) {
    const w = normaliseWindow(span, a, b);
    const genuinelyWhole = w.inSec === 0 && w.outSec === span;
    ok();
    if (w.full !== genuinelyWhole) {
      fail(`I14 full=${w.full} but the window is [${w.inSec},${w.outSec}] of ${span} (in=${a} out=${b})`);
    }
  }
}

// =============================================================================
// I15 — A TRIM THAT STRADDLES THE END OF A SHORT AUDIO TRACK.
//
//       The window has sound for part of each picture lap and none for the
//       rest. `audioPlan` can only offer the node ONE loop region, and clamping
//       it into the buffer makes that region the AUDIO's length — so the sound
//       laps at the audio's period while the picture laps at the window's, and
//       after the first lap they never meet again. Measured through real Web
//       Audio by an adversarial audit: `shortaudio.mp4` trimmed 2->5 played a
//       440 Hz tone on 16 of 24 sampled instants where the file has NO sound.
//
//       THE ASSERTION IS TWO-SIDED, and it has to be. "No wrong sound" alone is
//       satisfied by silence, and "sound wherever the file has it" alone is
//       satisfied by the drone this replaces. Only both together say the
//       schedule reproduces the picture.
//
//       THE RED PROOF is at the bottom: the OLD single-node plan is run through
//       the SAME assertion and must FAIL it. An invariant nobody has watched go
//       red is a hope, and this project has the scar to prove it (the twist
//       sweep asserted determinism by calling a pure function twice with the
//       same argument, and caught neither ULP defect).
// =============================================================================
{
  /** Every output instant where picture and sound must agree, for one setup. */
  const auditOne = (w, rate, loop, startAt, seconds, bufDur, positionAt) => {
    const p = { window: w, loop, rate };
    const r = safeRate(rate);
    const hiA = Math.min(w.outSec, bufDur);
    const bad = [];
    const STEPS = 200;
    for (let i = 0; i <= STEPS; i++) {
      const u = (i / STEPS) * seconds;
      const pic = sourceTimeAt(p, startAt + u);
      const snd = positionAt(u);
      // A boundary instant is neither side's business — the picture is AT the
      // audio's end, and half a sample either way decides it. Skip a hair.
      if (Math.abs(pic - hiA) < 1e-6) continue;
      if (pic < hiA) {
        // The file HAS sound here. It must be playing, at the picture's place.
        if (snd === null) { bad.push(`u=${u.toFixed(4)} pic=${pic.toFixed(5)} SILENT but the file has sound`); continue; }
        if (Math.abs(snd - pic) > 1e-6) {
          bad.push(`u=${u.toFixed(4)} pic=${pic.toFixed(5)} snd=${snd.toFixed(5)} drift=${(snd - pic).toExponential(2)}`);
        }
      } else if (snd !== null) {
        // The file has NO sound here. Anything playing is invented.
        bad.push(`u=${u.toFixed(4)} pic=${pic.toFixed(5)} past the audio end ${hiA.toFixed(5)} but snd=${snd.toFixed(5)}`);
      }
    }
    return bad;
  };

  let straddles = 0;
  let redSeen = 0;
  let sliver = 0;
  for (const span of [6, 8.4, 27.3]) {
    for (const [a, b] of WINDOWS(span)) {
      const w = normaliseWindow(span, a, b);
      if (!(w.length > 0)) continue;
      for (const bufDur of [
        span * 0.5, span * 0.34, 2.99998, span * 0.8,
        // THE SLIVER. An overlap UNDER the 10 ms loop-region floor: `audioPlan`
        // refuses to loop there, and reading the straddle off `plan.loop` used
        // to inherit that refusal into a path that never wraps — so the clip
        // played one blip for the whole take instead of one per lap. One
        // detent of the trim slider wide. These two rows are the regression.
        w.inSec + 0.005, w.inSec + 0.0099,
      ]) {
        // The straddle: audio ends strictly INSIDE the picture window.
        if (!(bufDur > w.inSec && bufDur < w.outSec)) continue;
        if ((bufDur - w.inSec) <= 0.01) sliver++;
        for (const rate of [1, 0.5, 2.4]) {
          for (const startAt of [0, 0.7, 3.3]) {
            const seconds = Math.min(30, (w.length / safeRate(rate)) * 3.4 + 1);
            const sched = audioSchedule({ window: w, loop: true, rate }, startAt, seconds, bufDur);
            straddles++;

            ok();
            if (!sched.lapped) fail(`I15 a straddle must lap: w=[${w.inSec},${w.outSec}] buf=${bufDur}`);
            ok();
            if (sched.truncated) fail(`I15 the cap must not bind on a real take (${sched.starts.length} laps)`);
            ok();
            if (sched.starts.some((s) => s.loop)) fail('I15 no lap may use the node\'s own loop');
            ok();
            if (sched.starts.some((s) => s.when < 0 || !Number.isFinite(s.when))) {
              fail(`I15 a start time is negative or non-finite: ${JSON.stringify(sched.starts.slice(0, 3))}`);
            }
            // Nothing may be told to read past the end of the decoded buffer.
            ok();
            for (const s of sched.starts) {
              if (s.offset + (s.duration ?? 0) > bufDur + 1e-9) {
                fail(`I15 a lap reads to ${s.offset + s.duration} past the ${bufDur}s buffer`);
                break;
              }
            }

            // NO TWO LAPS MAY SOUND AT ONCE. This needs its own assertion and
            // cannot be left to the audit below, because `schedulePositionAt`
            // returns the FIRST entry that covers an instant — so an overlap is
            // INVISIBLE to the model while the real graph SUMS the two nodes and
            // plays that stretch at double level. A model can only be trusted
            // where the thing it models is known not to do something else.
            ok();
            for (let i = 1; i < sched.starts.length; i++) {
              const prev = sched.starts[i - 1];
              const ends = prev.when + (prev.duration ?? 0) / safeRate(prev.playbackRate);
              if (ends > sched.starts[i].when + 1e-9) {
                fail(`I15 lap ${i - 1} sounds until ${ends} and lap ${i} starts at `
                  + `${sched.starts[i].when} — they overlap and will SUM `
                  + `(w=[${w.inSec},${w.outSec}] buf=${bufDur} rate=${rate})`);
                break;
              }
            }

            // THE ASSERTION.
            const bad = auditOne(w, rate, true, startAt, seconds, bufDur,
              (u) => schedulePositionAt(sched.starts, u));
            ok();
            if (bad.length) {
              fail(`I15 schedule disagrees with the picture on ${bad.length}/201 instants `
                + `(span=${span} w=[${w.inSec.toFixed(3)},${w.outSec.toFixed(3)}] buf=${bufDur} `
                + `rate=${rate} startAt=${startAt}): ${bad.slice(0, 2).join(' | ')}`);
            }

            // THE RED PROOF — the plan this replaces, through the same audit.
            const old = audioPlan({ window: w, loop: true, rate }, startAt, bufDur);
            const oldBad = auditOne(w, rate, true, startAt, seconds, bufDur,
              (u) => audioPositionAt(old, u));
            if (oldBad.length) redSeen++;
          }
        }
      }
    }
  }
  // THE CAP, ASSERTED IN THE DIRECTION THAT MATTERS. Every check above says the
  // cap must NOT bind, which is trivially satisfied by having no cap at all —
  // an audit confirmed that deleting the guard outright left this sweep green.
  // So drive a take long enough to reach it and assert it both BINDS and SAYS
  // it did, because `truncated` is a promise the interface makes and nothing in
  // production reads.
  {
    const w = normaliseWindow(6, 2, 5);
    const huge = MAX_AUDIO_LAPS * 3 * 2;          // laps of 3 s, twice the cap
    const s = audioSchedule({ window: w, loop: true, rate: 1 }, 0, huge, 2.99998);
    ok(); if (!s.truncated) fail(`I15 a ${huge}s take must exhaust the ${MAX_AUDIO_LAPS}-lap cap`);
    ok(); if (s.starts.length !== MAX_AUDIO_LAPS) fail(`I15 the cap must bound the list: ${s.starts.length}`);
    // Truncation must under-play, never mis-play: everything it DID schedule is
    // still exactly on the picture's laps.
    ok();
    for (let i = 1; i < s.starts.length; i++) {
      if (Math.abs((s.starts[i].when - s.starts[i - 1].when) - 3) > 1e-9) {
        fail(`I15 truncated schedule lost its period at lap ${i}`);
        break;
      }
    }
  }

  ok();
  if (straddles < 20) fail(`I15 the sweep only found ${straddles} straddles — it is not exercising the case`);
  ok();
  if (sliver < 10) fail(`I15 only ${sliver} sub-10ms-overlap straddles — the sliver is not covered`);
  // The bug must be REPRODUCIBLE by this instrument, or the instrument is not
  // measuring what it claims to measure.
  ok();
  if (redSeen < straddles * 0.5) {
    fail(`I15 RED PROOF: the OLD single-node plan failed the audit on only ${redSeen}/${straddles} `
      + 'setups — an assertion that cannot see the defect it was written for is decoration');
  }
  console.log(`  I15: ${straddles} straddling setups; the old plan fails ${redSeen} of them.`);
}

// =============================================================================
// I16 — THE SCOPE OF THE CHANGE. Everything that is NOT a straddle must come
//       back as ONE entry carrying `audioPlan`'s own numbers, bit for bit, so
//       every export that was correct before this cycle is untouched by it.
//       `Object.is`, not `approx` — "close enough" is how a scale bug hides.
// =============================================================================
{
  let single = 0;
  for (const span of SPANS) {
    if (!Number.isFinite(span) || span <= 0) continue;
    for (const [a, b] of WINDOWS(span)) {
      const w = normaliseWindow(span, a, b);
      for (const bufDur of [undefined, 0, span, span * 1.4, span * 0.55, 0.05]) {
        for (const loop of [true, false]) {
          for (const rate of [1, 0.5, 2.4]) {
            for (const startAt of [0, 1.5]) {
              const plan = audioPlan({ window: w, loop, rate }, startAt, bufDur);
              const sched = audioSchedule({ window: w, loop, rate }, startAt, 12, bufDur);

              ok();
              if (plan.silent !== sched.silent) fail(`I16 silent disagrees: ${plan.silent} vs ${sched.silent}`);
              if (plan.silent) {
                ok(); if (sched.starts.length) fail('I16 a silent schedule must wire nothing');
                continue;
              }
              // The straddle is the ONE case allowed to differ, and it is
              // decided on the WINDOW: a looping clip whose audio ends INSIDE
              // its trim window, with a picture lap long enough to schedule.
              // Deliberately NOT read off `plan.loop` — that is what left the
              // sub-10 ms sliver on the single-node path, and a test that
              // defines the boundary the same way the code does cannot see the
              // boundary being wrong.
              const hiA = bufDur > 0 ? Math.min(w.outSec, bufDur) : w.outSec;
              const straddle = loop && (hiA - w.inSec) > 0 && hiA < w.outSec && w.length > 0.01;
              ok();
              if (sched.lapped !== straddle) {
                fail(`I16 lapped=${sched.lapped} but straddle=${straddle} `
                  + `(loop=${plan.loop} loopEnd=${plan.loopEnd} out=${w.outSec} buf=${bufDur})`);
              }
              if (straddle) continue;

              single++;
              ok();
              if (sched.starts.length !== 1) fail(`I16 expected ONE start, got ${sched.starts.length}`);
              const s = sched.starts[0];
              for (const [k, mine, theirs] of [
                ['when', s.when, 0],
                ['offset', s.offset, plan.offset],
                ['duration', s.duration, plan.stopAfter],
                ['loop', s.loop, plan.loop],
                ['loopStart', s.loopStart, plan.loopStart],
                ['loopEnd', s.loopEnd, plan.loopEnd],
                ['playbackRate', s.playbackRate, plan.playbackRate],
              ]) {
                ok();
                if (!Object.is(mine, theirs)) {
                  fail(`I16 ${k}: schedule ${mine} != plan ${theirs} (span=${span} buf=${bufDur} loop=${loop})`);
                }
              }
              // And the two MODELS must agree, so `schedulePositionAt` is an
              // extension of `audioPositionAt` rather than a second copy of it.
              for (const u of [0, 0.033, 1.1, 4.7, 19]) {
                ok();
                const m = schedulePositionAt(sched.starts, u);
                const n = audioPositionAt(plan, u);
                if (!(m === null && n === null) && !(m !== null && n !== null && Object.is(m, n))) {
                  fail(`I16 model split at u=${u}: schedule=${m} plan=${n}`);
                }
              }
            }
          }
        }
      }
    }
  }
  ok();
  if (single < 200) fail(`I16 only ${single} unchanged setups checked — too thin to call it compatibility`);
  console.log(`  I16: ${single} non-straddle setups are bit-identical to audioPlan.`);
}

// =============================================================================
// I13 — safeRate is total, and 1 is the only fallback.
// =============================================================================
for (const r of [undefined, null, NaN, Infinity, -Infinity, 0, -3, 1e-30]) {
  ok();
  const v = safeRate(r);
  if (!Number.isFinite(v) || v <= 0) fail(`I13 safeRate(${r}) -> ${v}`);
}
ok(); if (safeRate(0.5) !== 0.5) fail('I13 safeRate must pass a valid rate through unchanged');

// -----------------------------------------------------------------------------
console.log(`clipWindow invariants: ${checks} checks, ${fails} failures`);
process.exit(fails ? 1 : 0);
