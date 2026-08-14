// =============================================================================
// Invariant sweep for THE STRIP — what is IN the take, on the ruler that
// already measures it.
//
//   node tests/unit/takeMap.invariants.mjs
//
// Transpiles the REAL modules with esbuild (`bundle: true` — SCAR-C150-A: a
// sweep that transforms ONE file dies the day its module grows an import, and
// `takeMap.ts` imports four) and asserts against them, never against a copy.
//
// THE ONE THAT MATTERS IS I1+I2: the marks this module draws are turn
// boundaries ACCORDING TO `turnAt` ITSELF, and there is no boundary it misses.
// A ruler is a claim about the file; the only way that claim can be checked is
// against the function the compositor actually reads, so `turnAt` is imported
// and interrogated rather than restated. Every other invariant here is about
// not lying in some smaller way.
//
// I1  EVERY MARK IS A CUT. At each mark the compositor is starting turn k: the
//     instant before belongs to k-1, the instant after is mid-dissolve INTO k.
// I2  EVERY CUT IS A MARK. The complement, and the half a "draw the first one
//     and stop" defect would survive: walk the take on a fine grid, collect
//     every instant `turnAt`'s incoming index increments, and assert the two
//     sets are the same size and agree to within the walk's own resolution.
// I3  THE BAND IS THE DISSOLVE. `cuts.fade` is asserted against `mix`: still
//     fading at 99% of it, done at 101%.
// I4  A PACE SCALES THE CLOCK, SO fade/hold IS INVARIANT. `lib/pace.ts`'s own
//     property, read from the strip's side — and the reason the roster branch
//     divides the fade as well as the hold.
// I5  PASSES TILE THE TAKE. Contiguous, ascending, [0,1], no gap, no overlap,
//     exactly one partial and only ever the last.
// I6  A SEAM IS WHERE THE SOURCE RESTARTS, according to `sourceTimeAt`. The
//     lane's period is `effectiveLength`, so the assertion is made against the
//     formula the live element, the offline seek and the offline mixer all read
//     — not against `length / rate` written out a second time here.
// I7  NOTHING THROWS AND EVERY NUMBER IS FINITE AND ON THE BAR. Fractions feed
//     `left:` and `width:` in percent; one NaN is an invisible lane.
// I8  NO SILENT CAPS. A dense lane still reports its exact lap count, hidden
//     cuts are counted, and a source with no length is counted separately from
//     one there was no room for.
// I9  A SYNCED PLAN IS THE GRID, UNPACED. The one decision the beat feature
//     turns on at the compositor (`stage.ts`), asserted here so a strip cannot
//     draw a paced grid the wall is not cutting on.
//
// WHAT MUTATION TESTING SAID — see the block at the foot of this file.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// =============================================================================

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

const {
  cutPlan, cutMarks, driftPlan, driftLabel, lapSegments, takeMap, laneLabel,
  MAX_LANE_SEGMENTS, MAX_LANES, MAX_STRIP_CUTS, EMPTY_MAP,
} = await load('src/lib/takeMap.ts', 'takemap');
const {
  sampleMove, isMoving, NO_MOVE, MOVE_IDS, MOVE_CYCLE_SEC,
} = await load('src/lib/motion.ts', 'motion');
const { turnAt, turnHoldSec, TURN_IDS, TURN_FADE_SEC } = await load('src/lib/turn.ts', 'turn');
const { paceTime, paceRate, PACE_IDS } = await load('src/lib/pace.ts', 'pace');
const { beatSchedule } = await load('src/lib/beat.ts', 'beat');
const { normaliseWindow, sourceTimeAt, effectiveLength } = await load('src/lib/clipWindow.ts', 'clipwindow');
const { computeClipPlayback } = await load('src/lib/videoSync.ts', 'videosync');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};

/** Deterministic PRNG so a failure is reproducible. */
const rng = (seed) => {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
};

const TAKES = [3, 5, 8, 10, 15, 20, 30, 4.3, 7.7, 12.5];
const BPMS = [60, 90, 100, 120, 128, 140, 174, 180];

// -----------------------------------------------------------------------------
// I1 — EVERY MARK IS A CUT, according to `turnAt`.
// -----------------------------------------------------------------------------
{
  let checked = 0;
  let bad = 0;
  let worst = '';
  for (const turn of TURN_IDS) {
    for (const pace of PACE_IDS) {
      for (const synced of [false, true]) {
        for (const take of TAKES) {
          for (const bpm of synced ? BPMS : [0]) {
            const grid = synced ? { bpm, periodSec: 60 / bpm, offsetSec: 0.13, confidence: 0.9 } : null;
            const hold = turnHoldSec(turn);
            const sched = synced && hold > 0
              ? beatSchedule(grid, hold / (paceRate(pace) || 1), 0)
              : null;
            if (synced && !sched) continue;
            const plan = cutPlan(turn, pace, sched);
            const marks = cutMarks(plan, take);
            if (!plan) {
              if (marks.at.length !== 0) { bad++; worst = `${turn}/${pace}: no plan but ${marks.at.length} marks`; }
              continue;
            }
            // The clock the compositor reads: a synced grid is NOT paced.
            const clock = (t) => (sched ? t : paceTime(pace, t));
            const eps = Math.min(1e-4, plan.hold / 1000);
            marks.at.forEach((f, i) => {
              const k = i + 1;
              const t = f * take;
              const before = turnAt(turn, clock(t - eps), sched);
              const after = turnAt(turn, clock(t + eps), sched);
              checked++;
              // Before the mark the wall is still on turn k-1 (mix 0 or fading
              // INTO k-1, i.e. its incoming index is k-1).
              const okBefore = before.b === k - 1;
              // At the mark the dissolve into k has started.
              const okAfter = after.a === k - 1 && after.b === k && after.mix > 0;
              if (!okBefore || !okAfter) {
                bad++;
                if (!worst) {
                  worst = `${turn}/${pace}${sched ? `/${bpm}bpm` : ''} take=${take} mark#${k}@${t.toFixed(4)} `
                    + `before=${JSON.stringify(before)} after=${JSON.stringify(after)}`;
                }
              }
            });
          }
        }
      }
    }
  }
  ok('I1 every mark is a turn boundary per turnAt', bad === 0 && checked > 500,
    `${checked} marks checked, ${bad} wrong${worst ? ` (${worst})` : ''}`);
}

// -----------------------------------------------------------------------------
// I2 — EVERY CUT IS A MARK. Walk the take and collect what the compositor does.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  let cases = 0;
  let worst = '';
  const STEP = 1 / 240; // finer than a frame at any rate this app renders
  for (const turn of TURN_IDS) {
    for (const pace of PACE_IDS) {
      for (const synced of [false, true]) {
        for (const take of [5, 10, 20, 7.7]) {
          const bpm = 128;
          const grid = { bpm, periodSec: 60 / bpm, offsetSec: 0.31, confidence: 0.8 };
          const hold = turnHoldSec(turn);
          const sched = synced && hold > 0 ? beatSchedule(grid, hold / (paceRate(pace) || 1), 0) : null;
          if (synced && !sched) continue;
          const plan = cutPlan(turn, pace, sched);
          const marks = cutMarks(plan, take);
          const clock = (t) => (sched ? t : paceTime(pace, t));
          // Every instant the incoming turn index increments IS a cut.
          const observed = [];
          let prev = turnAt(turn, clock(0), sched).b;
          for (let t = STEP; t < take; t += STEP) {
            const b = turnAt(turn, clock(t), sched).b;
            if (b > prev) observed.push(t);
            prev = b;
          }
          cases++;
          if (observed.length !== marks.at.length) {
            bad++;
            if (!worst) {
              worst = `${turn}/${pace}${sched ? '/synced' : ''} take=${take}: `
                + `${observed.length} cuts observed vs ${marks.at.length} marks`;
            }
            continue;
          }
          for (let i = 0; i < observed.length; i++) {
            const drawn = marks.at[i] * take;
            if (Math.abs(observed[i] - drawn) > STEP * 1.5) {
              bad++;
              if (!worst) worst = `${turn}/${pace} take=${take} cut#${i + 1}: observed ${observed[i].toFixed(4)} drawn ${drawn.toFixed(4)}`;
              break;
            }
          }
        }
      }
    }
  }
  ok('I2 no cut is missing from the strip', bad === 0 && cases > 40,
    `${cases} schedules walked at 240Hz, ${bad} disagreed${worst ? ` (${worst})` : ''}`);
}

// -----------------------------------------------------------------------------
// I3 — THE BAND IS THE DISSOLVE.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  let checked = 0;
  let worst = '';
  for (const turn of TURN_IDS) {
    for (const pace of PACE_IDS) {
      for (const take of [10, 20, 7.7]) {
        const plan = cutPlan(turn, pace, null);
        if (!plan) continue;
        const marks = cutMarks(plan, take);
        if (marks.at.length === 0) continue;
        const fadeSec = marks.fade * take;
        const t = marks.at[0] * take;
        const mid = turnAt(turn, paceTime(pace, t + fadeSec * 0.99), null);
        const done = turnAt(turn, paceTime(pace, t + fadeSec * 1.01), null);
        checked++;
        if (!(mid.mix > 0) || done.mix !== 0 || done.a !== done.b) {
          bad++;
          if (!worst) worst = `${turn}/${pace}: fade=${fadeSec.toFixed(4)} mid=${JSON.stringify(mid)} done=${JSON.stringify(done)}`;
        }
      }
    }
  }
  ok('I3 the drawn band is exactly the dissolve', bad === 0 && checked > 20,
    `${checked} bands, ${bad} wrong${worst ? ` (${worst})` : ''}`);
}

// -----------------------------------------------------------------------------
// I4 — fade/hold IS INVARIANT UNDER THE PACE.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  let worst = '';
  for (const turn of TURN_IDS) {
    const ratios = [];
    for (const pace of PACE_IDS) {
      const plan = cutPlan(turn, pace, null);
      if (!plan) continue;
      ratios.push(plan.fade / plan.hold);
    }
    if (ratios.length === 0) continue;
    const spread = Math.max(...ratios) - Math.min(...ratios);
    if (spread > 1e-12) { bad++; if (!worst) worst = `${turn}: ratios ${ratios.map((r) => r.toFixed(6)).join(',')}`; }
    // And the ratio is the roster's own: TURN_FADE_SEC over the mode's hold.
    const want = TURN_FADE_SEC / turnHoldSec(turn);
    if (Math.abs(ratios[0] - want) > 1e-12) {
      bad++;
      if (!worst) worst = `${turn}: ratio ${ratios[0]} want ${want}`;
    }
  }
  ok('I4 a pace scales the clock, so fade/hold does not move', bad === 0, worst);
}

// -----------------------------------------------------------------------------
// I5 — PASSES TILE THE TAKE.
// -----------------------------------------------------------------------------
{
  const rand = rng(20260812);
  let bad = 0;
  let checked = 0;
  let worst = '';
  for (let i = 0; i < 4000; i++) {
    const take = 1 + rand() * 40;
    const lap = 0.05 + rand() * 45;
    const p = lapSegments(lap, take);
    checked++;
    const wantLaps = Math.max(1, Math.ceil(take / lap - 1e-9));
    if (p.laps !== wantLaps) { bad++; if (!worst) worst = `lap=${lap} take=${take}: laps ${p.laps} want ${wantLaps}`; continue; }
    if (p.dense) {
      if (p.segments.length !== 0 || p.laps <= MAX_LANE_SEGMENTS) { bad++; if (!worst) worst = 'dense lane malformed'; }
      continue;
    }
    if (p.segments.length !== p.laps) { bad++; if (!worst) worst = 'segment count != laps'; continue; }
    let prevEnd = 0;
    let partials = 0;
    for (let j = 0; j < p.segments.length; j++) {
      const s = p.segments[j];
      if (!(s.start >= 0 && s.end <= 1 && s.end > s.start)) { bad++; if (!worst) worst = `bad segment ${JSON.stringify(s)}`; break; }
      if (Math.abs(s.start - prevEnd) > 1e-9) { bad++; if (!worst) worst = `gap/overlap at ${j}: ${s.start} vs ${prevEnd}`; break; }
      prevEnd = s.end;
      if (!s.whole) {
        partials++;
        if (j !== p.segments.length - 1) { bad++; if (!worst) worst = 'a partial pass that is not the last'; break; }
      }
    }
    if (Math.abs(prevEnd - 1) > 1e-9) { bad++; if (!worst) worst = `passes stop at ${prevEnd}`; }
    if (partials > 1) { bad++; if (!worst) worst = 'more than one partial pass'; }
    // AND THE LAST FLAG IS THE ARITHMETIC TRUTH, not merely "at most one is
    // false". A mutation that marks every pass whole leaves the count check
    // above green — measured — because zero partials is not more than one.
    const wantWhole = p.laps * lap <= take + 1e-9;
    if (p.segments[p.segments.length - 1].whole !== wantWhole) {
      bad++;
      if (!worst) worst = `lap=${lap.toFixed(4)} take=${take.toFixed(4)}: last whole=${!wantWhole}`;
    }
  }
  ok('I5 passes tile the take, exactly one partial and only at the end', bad === 0,
    `${checked} lap/take pairs, ${bad} malformed${worst ? ` (${worst})` : ''}`);
}

// -----------------------------------------------------------------------------
// I5b — A LAP THAT DIVIDES THE TAKE EXACTLY DRAWS EXACTLY THAT MANY PASSES.
//
// I5 sweeps 4,000 RANDOM pairs and cannot see this: an exact division is a
// measure-zero event under a uniform sample, so the epsilon that makes it come
// out right was asserted by nothing. Mutation testing caught it — deleting
// `MAX_LANE_SEGMENTS`'s sibling `MAX_EPSILON` from the `ceil` was the one defect
// of fourteen that SURVIVED the first pass. It is the same shape as
// SCAR-C147 ("an invariant that quantifies over a SYMMETRY of the thing it is
// testing cannot see a defect that lives in the choice of representative"), and
// it is not hypothetical arithmetic: `4.3 / (4.3/7)` is 7.000000000000001, so
// without the epsilon a clip whose window is exactly a seventh of the take
// draws an EIGHTH pass one nanosecond wide at the right-hand edge of the bar.
// Measured: 12 such pairs among the 390 exact divisions swept below.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  let checked = 0;
  let above = 0;
  let worst = '';
  for (const take of TAKES) {
    for (let n = 1; n <= 40; n++) {
      const lap = take / n;
      if (take / lap > n) above++;
      const p = lapSegments(lap, take);
      checked++;
      if (p.laps !== n) {
        bad++;
        if (!worst) worst = `take=${take} lap=take/${n}: laps=${p.laps}`;
        continue;
      }
      if (!p.dense) {
        if (p.segments.length !== n) { bad++; if (!worst) worst = `take=${take}/${n}: ${p.segments.length} segments`; continue; }
        if (!p.segments[n - 1].whole) { bad++; if (!worst) worst = `take=${take}/${n}: last pass drawn partial`; }
      }
    }
  }
  ok('I5b an exact division draws exactly that many passes', bad === 0,
    `${checked} exact divisions, ${above} of them float-high, ${bad} wrong${worst ? ` (${worst})` : ''}`);
}

// -----------------------------------------------------------------------------
// I6 — A SEAM IS WHERE `sourceTimeAt` RESTARTS.
// -----------------------------------------------------------------------------
{
  const rand = rng(77777);
  let bad = 0;
  let checked = 0;
  let worst = '';
  for (let i = 0; i < 1500; i++) {
    const span = 1 + rand() * 30;
    const inSec = rand() < 0.5 ? 0 : rand() * span * 0.4;
    const outSec = inSec + Math.max(0.3, rand() * (span - inSec));
    const speed = [0.25, 0.5, 1, 2, 4][Math.floor(rand() * 5)];
    const mode = ['loop', 'stretch-longest', 'speed-shortest'][Math.floor(rand() * 3)];
    const window = normaliseWindow(span, inSec, outSec);
    const [pb] = computeClipPlayback([{ id: 'a', durationSec: window.length, speed }], mode);
    const playback = { window, loop: true, rate: pb.playbackRate };
    const take = 2 + rand() * 30;
    const lapSec = effectiveLength(playback);
    const p = lapSegments(lapSec, take);
    if (p.dense || p.segments.length < 2) continue;
    checked++;
    // The seam between pass 0 and pass 1: the source is at its OUT point just
    // before and back at its IN point just after.
    const seam = p.segments[1].start * take;
    const eps = Math.min(1e-3, lapSec / 100);
    const beforeSrc = sourceTimeAt(playback, seam - eps);
    const afterSrc = sourceTimeAt(playback, seam + eps);
    const nearOut = Math.abs(beforeSrc - window.outSec) <= eps * playback.rate * 1.5 + 1e-9;
    const nearIn = Math.abs(afterSrc - window.inSec) <= eps * playback.rate * 1.5 + 1e-9;
    if (!nearOut || !nearIn) {
      bad++;
      if (!worst) {
        worst = `seam@${seam.toFixed(4)} lap=${lapSec.toFixed(4)} rate=${playback.rate.toFixed(4)} `
          + `before=${beforeSrc.toFixed(4)} (out ${window.outSec.toFixed(4)}) after=${afterSrc.toFixed(4)} (in ${window.inSec.toFixed(4)})`;
      }
    }
  }
  ok('I6 a seam is where sourceTimeAt wraps the window', bad === 0 && checked > 300,
    `${checked} seams, ${bad} misplaced${worst ? ` (${worst})` : ''}`);
}

// -----------------------------------------------------------------------------
// I7 — GARBAGE IN, A DRAWABLE MAP OUT (or nothing), never a throw or a NaN.
// -----------------------------------------------------------------------------
{
  const junk = [undefined, null, NaN, Infinity, -Infinity, 0, -1, '', 'x', {}, [], 1e308, -0];
  let bad = 0;
  let worst = '';
  const finiteFraction = (n) => Number.isFinite(n) && n >= 0 && n <= 1;
  for (const a of junk) {
    for (const b of junk) {
      for (const c of junk) {
        try {
          const plan = cutPlan(a, b, c);
          if (plan && !(plan.hold > 0 && Number.isFinite(plan.first) && plan.fade > 0)) {
            bad++; if (!worst) worst = `cutPlan(${String(a)},${String(b)},${String(c)}) = ${JSON.stringify(plan)}`;
          }
          const m = cutMarks(plan, a);
          if (!m.at.every(finiteFraction) || !Number.isFinite(m.fade) || !Number.isFinite(m.hidden)) {
            bad++; if (!worst) worst = `cutMarks junk: ${JSON.stringify(m).slice(0, 120)}`;
          }
          const p = lapSegments(a, b);
          if (!p.segments.every((s) => finiteFraction(s.start) && finiteFraction(s.end))) {
            bad++; if (!worst) worst = 'lapSegments junk fractions';
          }
          const mp = takeMap(a, [{ id: 'x', kind: 'clip', label: b, playback: c }], plan);
          if (!Number.isFinite(mp.hiddenLanes) || !Number.isFinite(mp.unknownLanes)) {
            bad++; if (!worst) worst = 'takeMap junk counters';
          }
          if (mp.lanes.some((l) => !Number.isFinite(l.lapSec) || l.lapSec <= 0)) {
            bad++; if (!worst) worst = 'takeMap junk lane length';
          }
        } catch (e) {
          bad++;
          if (!worst) worst = `threw on (${String(a)},${String(b)},${String(c)}): ${e.message}`;
        }
      }
    }
  }
  // And the empty map is genuinely empty.
  if (!EMPTY_MAP.empty || EMPTY_MAP.lanes.length !== 0) { bad++; if (!worst) worst = 'EMPTY_MAP is not empty'; }
  ok('I7 junk never throws and never puts a NaN on the bar', bad === 0, `${junk.length ** 3} triples${worst ? ` — ${worst}` : ''}`);
}

// -----------------------------------------------------------------------------
// I8 — NO SILENT CAPS.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  const detail = [];
  // A lane that laps more times than it can draw keeps the exact count.
  const dense = lapSegments(0.1, 30); // 300 laps
  if (!dense.dense || dense.laps !== 300 || dense.segments.length !== 0) { bad++; detail.push(`dense=${JSON.stringify({ d: dense.dense, l: dense.laps, s: dense.segments.length })}`); }
  // A lane right on the cap still draws.
  const atCap = lapSegments(1, MAX_LANE_SEGMENTS);
  if (atCap.dense || atCap.segments.length !== MAX_LANE_SEGMENTS) { bad++; detail.push('at-cap lane went dense'); }
  // More sources than lanes: the rest are COUNTED, not dropped.
  const src = (i) => ({
    id: `s${i}`, kind: 'clip', label: `c${i}`,
    playback: { window: normaliseWindow(4, 0, 4), loop: true, rate: 1 },
  });
  const many = takeMap(10, Array.from({ length: MAX_LANES + 5 }, (_, i) => src(i)), null);
  if (many.lanes.length !== MAX_LANES || many.hiddenLanes !== 5) { bad++; detail.push(`lanes=${many.lanes.length} hidden=${many.hiddenLanes}`); }
  // A source with no usable length is counted apart from one there was no room for.
  const unknown = takeMap(10, [
    { id: 'u', kind: 'clip', label: 'u', playback: { window: normaliseWindow(0), loop: true, rate: 1 } },
    src(1),
  ], null);
  if (unknown.unknownLanes !== 1 || unknown.lanes.length !== 1 || unknown.hiddenLanes !== 0) {
    bad++; detail.push(`unknown=${unknown.unknownLanes} lanes=${unknown.lanes.length}`);
  }
  // Hidden cuts are counted rather than dropped: a hold far below the cap's reach.
  const busy = cutMarks({ hold: 0.01, first: 0.01, fade: 0.002 }, 10);
  if (busy.at.length !== MAX_STRIP_CUTS || busy.hidden <= 0) { bad++; detail.push(`cuts=${busy.at.length} hidden=${busy.hidden}`); }
  // Nothing to draw is EMPTY, and a still collage under nothing draws no strip.
  const still = takeMap(10, [], null);
  if (!still.empty) { bad++; detail.push('a still take is not empty'); }
  ok('I8 every cap reports what it dropped', bad === 0, detail.join(' · '));
}

// -----------------------------------------------------------------------------
// I9 — A SYNCED PLAN IS THE GRID, UNPACED.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  let worst = '';
  for (const bpm of BPMS) {
    for (const turn of TURN_IDS) {
      const hold = turnHoldSec(turn);
      if (!(hold > 0)) continue;
      for (const pace of PACE_IDS) {
        const grid = { bpm, periodSec: 60 / bpm, offsetSec: 0.07, confidence: 0.9 };
        const sched = beatSchedule(grid, hold / (paceRate(pace) || 1), 0);
        if (!sched) continue;
        const plan = cutPlan(turn, pace, sched);
        if (!plan) { bad++; if (!worst) worst = `${turn}/${pace}/${bpm}: no plan from a valid grid`; continue; }
        // Verbatim the grid, NOT scaled by the pace a second time.
        if (plan.hold !== sched.hold || plan.first !== sched.first || plan.fade !== sched.fade) {
          bad++;
          if (!worst) worst = `${turn}/${pace}/${bpm}: plan ${JSON.stringify(plan)} vs grid ${JSON.stringify(sched)}`;
        }
        // The hold is a whole number of beats — the whole point of a sync.
        const beats = plan.hold / grid.periodSec;
        if (Math.abs(beats - Math.round(beats)) > 1e-9) {
          bad++; if (!worst) worst = `${turn}/${pace}/${bpm}: hold is ${beats} beats`;
        }
      }
    }
  }
  // A beat grid under a mode that does not cut draws nothing.
  const held = cutPlan('hold', 'even', { hold: 2, first: 2, fade: 0.4 });
  if (held !== null) { bad++; if (!worst) worst = 'a grid under HOLD produced a plan'; }
  ok('I9 a synced plan is the grid verbatim, never paced twice', bad === 0, worst);
}

// -----------------------------------------------------------------------------
// I10 — THE LABEL AGREES WITH THE SHAPES, AT EVERY PERIOD AND NOT ONLY AT THE
//       ROUND ONES.
//
// The first version of this arm tested 5/10, 3/10 and 30/10 and passed while
// the label was rounding away the very fact its docstring says it exists to
// state: `Math.round(times*10)/10` snapped anything within 0.05 of an integer,
// so a 10.4 s source in a 10 s take read "x1" — plays through once — beside a
// bar drawn as a single PARTIAL pass. Found by the adversarial audit, which
// measured the bands (9.524-10.000 s all read x1 on a 10 s take). The three
// original cases sit outside every band, which is exactly why they held.
//
// So the arm now sweeps periods CONTINUOUSLY and asserts the label against the
// segments the component draws, which is the only agreement that matters.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  let checked = 0;
  let worst = '';
  const detail = [];
  const laneFor = (lapSec, take) => {
    const p = lapSegments(lapSec, take);
    return { id: 'a', kind: 'clip', label: 'clip.mp4', lapSec, ...p };
  };
  for (const take of [10, 15, 5, 7.7]) {
    for (let lapSec = 0.4; lapSec <= take * 1.6; lapSec += 0.017) {
      const lane = laneFor(lapSec, take);
      const label = laneLabel(lane, take);
      checked++;
      const last = lane.segments[lane.segments.length - 1];
      const partial = lane.dense ? true : !!last && !last.whole;
      // A WHOLE-NUMBER label is a claim that nothing is cut off. Read the
      // passes TOKEN, not the whole string: the label carries a filename and a
      // duration, both full of dots, and a naive `includes('.')` calls every
      // label fractional (this arm's own first draft did exactly that).
      const token = /x(\d+(?:\.\d+)?)$/.exec(label);
      const saysWhole = !!token && !token[1].includes('.');
      if (partial && saysWhole) {
        bad++;
        if (!worst) worst = `lap=${lapSec.toFixed(4)} take=${take}: "${label}" over ${lane.laps} passes, last partial`;
      }
      if (!partial && !saysWhole && !label.includes('cut off')) {
        bad++;
        if (!worst) worst = `lap=${lapSec.toFixed(4)} take=${take}: "${label}" but every pass is whole`;
      }
    }
  }
  // And the shapes the original arm pinned still hold.
  if (!laneLabel(laneFor(5, 10), 10).includes('x2')) { bad++; detail.push('5/10 no longer x2'); }
  if (!laneLabel(laneFor(3, 10), 10).includes('x3.3')) { bad++; detail.push('3/10 no longer x3.3'); }
  if (!laneLabel(laneFor(30, 10), 10).includes('cut off')) { bad++; detail.push('30/10 no longer cut off'); }
  // The exact case the audit measured.
  const audit = laneLabel(laneFor(10.4, 10), 10);
  if (!audit.includes('cut off')) { bad++; detail.push(`10.4/10: ${audit}`); }
  const audit2 = laneLabel(laneFor(4.9, 10), 10);
  if (audit2.includes('x2 ') || /x2$/.test(audit2)) { bad++; detail.push(`4.9/10: ${audit2} (3 passes drawn)`); }
  ok('I10 the label agrees with the segments at every period', bad === 0,
    `${checked} periods swept${worst ? ` — ${worst}` : ''}${detail.length ? ` · ${detail.join(' · ')}` : ''}`);
}

// -----------------------------------------------------------------------------
// I11 — A GRID THE COMPOSITOR REPAIRS IS A GRID THE STRIP DRAWS.
//
// `scheduledTurnAt` refuses a non-positive fade, but nothing hands it one:
// `setScene` replaces it with `turnFadeFor(hold)` first. Mirroring the stricter
// function meant the strip drew NOTHING on a schedule the wall was cutting on.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  const detail = [];
  for (const fade of [0, -1, NaN, undefined]) {
    const plan = cutPlan('march', 'even', { hold: 2, first: 2, fade });
    if (!plan || !(plan.fade > 0)) { bad++; detail.push(`fade=${String(fade)} -> ${JSON.stringify(plan)}`); continue; }
    // Repaired to the same number the Stage would have used.
    if (plan.fade !== 0.4 && plan.fade !== Math.min(0.7, 2 * 0.2)) { bad++; detail.push(`fade=${String(fade)} repaired to ${plan.fade}`); }
    const marks = cutMarks(plan, 10);
    if (marks.at.length !== 4) { bad++; detail.push(`fade=${String(fade)} drew ${marks.at.length} marks`); }
  }
  // A hold that is genuinely unusable is still refused.
  for (const bad2 of [{ hold: 0, first: 1, fade: 0.5 }, { hold: NaN, first: 1, fade: 0.5 }, { hold: 2, first: NaN, fade: 0.5 }]) {
    if (cutPlan('march', 'even', bad2) !== null) { bad++; detail.push(`accepted ${JSON.stringify(bad2)}`); }
  }
  ok('I11 a repaired fade draws, an unusable hold still refuses', bad === 0, detail.join(' · '));
}

// -----------------------------------------------------------------------------
// I12 — THE MUSIC IS NEVER THE LANE THAT GETS DROPPED, and an admission is
//       never silenced by having nothing beside it.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  const detail = [];
  const clip = (i) => ({
    id: `c${i}`, kind: 'clip', label: `c${i}`,
    playback: { window: normaliseWindow(4, 0, 4), loop: true, rate: 1 },
  });
  const music = {
    id: '__soundtrack__', kind: 'music', label: 'song.mp3',
    playback: { window: normaliseWindow(12, 0, 12), loop: true, rate: 1 },
  };
  // Music arrives LAST, exactly as the caller pushes it, with every slot taken.
  const full = takeMap(15, [...Array.from({ length: MAX_LANES + 1 }, (_, i) => clip(i)), music], null);
  const musicLane = full.lanes.find((l) => l.kind === 'music');
  if (!musicLane) { bad++; detail.push('music dropped when nine clips filled the slots'); }
  if (full.lanes.length !== MAX_LANES) { bad++; detail.push(`lanes=${full.lanes.length}`); }
  if (full.hiddenLanes !== 2) { bad++; detail.push(`hidden=${full.hiddenLanes} (one clip over + one evicted)`); }
  // A clip past the cap is still just counted — no eviction for its own kind.
  const clipsOnly = takeMap(15, Array.from({ length: MAX_LANES + 3 }, (_, i) => clip(i)), null);
  if (clipsOnly.lanes.length !== MAX_LANES || clipsOnly.hiddenLanes !== 3) {
    bad++; detail.push(`clips-only lanes=${clipsOnly.lanes.length} hidden=${clipsOnly.hiddenLanes}`);
  }
  // An unmeasured source with nothing else in the take must NOT come back empty:
  // `empty` renders no strip at all and would take its own diagnostic with it.
  const unmeasured = takeMap(10, [{
    id: 'm', kind: 'music', label: 'song.mp3',
    playback: { window: normaliseWindow(0), loop: true, rate: 1 },
  }], null);
  if (unmeasured.empty || unmeasured.unknownLanes !== 1) {
    bad++; detail.push(`unmeasured-only: empty=${unmeasured.empty} unknown=${unmeasured.unknownLanes}`);
  }
  // And a genuinely empty take is still empty.
  if (!takeMap(10, [], null).empty) { bad++; detail.push('a still take is no longer empty'); }
  ok('I12 music keeps its lane and an admission is never silenced', bad === 0, detail.join(' · '));
}

// -----------------------------------------------------------------------------
// I13 — EVERY DRIFT SEAM IS REST, AND NOTHING BETWEEN TWO SEAMS IS.
//
// The same oracle as I1/I2, for the row DECISION 5 added: a seam is drawn where
// the whole wall comes back to the picture the still preview shows, and the
// only authority on that is `sampleMove` — which returns `NO_MOVE` BY REFERENCE
// at t=0 and at every cycle boundary and a fresh object everywhere else. So the
// assertion is an IDENTITY check against the compositor's own function, sampled
// through `paceTime` because that is the clock the Stage reads the move against
// (stage.ts: `sampleMove(spec, paceTime(this.pace, this.outTime))`).
//
// The interior probe is at a QUARTER of the cycle, never the half: `envelope`
// is exactly 0 at mid-cycle for a k=2 fragment (`stagger` with ph >= 0.5), so a
// midpoint probe would assert that a legitimately-resting fragment is moving.
// -----------------------------------------------------------------------------
{
  let checked = 0;
  let bad = 0;
  const detail = [];
  const PHASES = [0, 0.13, 0.5, 0.77, 0.99];
  for (const move of MOVE_IDS.filter((id) => isMoving({ id }))) {
    for (const pace of PACE_IDS) {
      for (const take of TAKES) {
        const lapSec = driftPlan(move, pace);
        if (!(lapSec > 0)) { bad++; detail.push(`${move}/${pace} planned 0`); continue; }
        const map = takeMap(take, [], null, lapSec);
        if (!map.drift) { bad++; detail.push(`${move}/${pace}/${take} drew no drift row`); continue; }
        for (const seg of map.drift.segments) {
          const t = seg.start * take;
          for (const ph of PHASES) {
            checked++;
            // THE SEAM IS REST — by reference, which is the contract the still
            // preview, the raster export and the SVG all rely on.
            if (sampleMove({ id: move, ph }, paceTime(pace, t)) !== NO_MOVE) {
              bad++;
              if (detail.length < 4) detail.push(`${move}/${pace}/${take}s: seam ${t.toFixed(6)} ph${ph} not at rest`);
            }
          }
          // A QUARTER INTO THE PASS the collage is provably moving — but only
          // where the take actually reaches, because the last pass is short.
          const probe = t + lapSec / 4;
          if (probe < take - 1e-9) {
            for (const ph of PHASES) {
              checked++;
              if (sampleMove({ id: move, ph }, paceTime(pace, probe)) === NO_MOVE) {
                bad++;
                if (detail.length < 8) detail.push(`${move}/${pace}/${take}s: ${probe.toFixed(3)} ph${ph} at rest mid-pass`);
              }
            }
          }
        }
      }
    }
  }
  ok('I13 every drift seam is rest and nothing between two seams is', bad === 0,
    `${checked} instants swept${detail.length ? ` · ${detail.join(' · ')}` : ''}`);
}

// -----------------------------------------------------------------------------
// I14 — A PACE SCALES THE DRIFT EXACTLY AS IT SCALES THE HOLD, and a collage
//       that is not moving has no row at all.
//
// `lib/pace.ts`'s own property read from the strip's side, the same way I4
// reads it for the cut: the roster's 12 s is in PACED seconds, so the row's
// period in output seconds times the rate is the constant, at every tempo.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  const detail = [];
  for (const pace of PACE_IDS) {
    for (const move of MOVE_IDS.filter((id) => isMoving({ id }))) {
      const p = driftPlan(move, pace);
      if (Math.abs(p * paceRate(pace) - MOVE_CYCLE_SEC) > 1e-9) {
        bad++; detail.push(`${move}/${pace}: ${p} * ${paceRate(pace)} != ${MOVE_CYCLE_SEC}`);
      }
    }
    // STILL, AND EVERY WAY OF NOT BEING A MOVE, ANSWER ZERO — through
    // `isMoving`, so a roster entry that stops moving stops drawing a row
    // without this module being edited.
    for (const id of ['still', 'nope', '', null, undefined, 42, {}]) {
      if (driftPlan(id, pace) !== 0) { bad++; detail.push(`${String(id)} planned ${driftPlan(id, pace)}`); }
    }
  }
  // A junk pace is the neutral rate, never a NaN period.
  for (const junk of [null, undefined, 'nope', 7]) {
    if (driftPlan('push', junk) !== MOVE_CYCLE_SEC) { bad++; detail.push(`pace=${String(junk)} -> ${driftPlan('push', junk)}`); }
  }
  ok('I14 a pace scales the drift and a still collage has no row', bad === 0, detail.join(' · '));
}

// -----------------------------------------------------------------------------
// I15 — THE DRIFT IS NOT A SOURCE — DECISION 5.
//
// It never enters `lanes`, never takes a `MAX_LANES` slot from a clip, is never
// counted as hidden or unknown, and it is what makes a moving collage of
// photographs stop coming back `empty` — which is the whole defect: the one
// composition this app is named for drew no strip at all.
// -----------------------------------------------------------------------------
{
  let bad = 0;
  const detail = [];
  const clip = (i) => ({
    id: `c${i}`, kind: 'clip', label: `c${i}`,
    playback: { window: normaliseWindow(4, 0, 4), loop: true, rate: 1 },
  });
  const music = {
    id: '__soundtrack__', kind: 'music', label: 'song.mp3',
    playback: { window: normaliseWindow(12, 0, 12), loop: true, rate: 1 },
  };
  const drift = driftPlan('push', 'even');

  // THE HEADLINE: photographs, a move, no music, no cuts.
  const photos = takeMap(10, [], null, drift);
  if (photos.empty) { bad++; detail.push('a moving photo collage still comes back empty'); }
  if (!photos.drift || photos.drift.laps !== 1) { bad++; detail.push(`laps=${photos.drift?.laps}`); }
  if (photos.lanes.length !== 0) { bad++; detail.push(`drift leaked into lanes (${photos.lanes.length})`); }
  // 12 s in a 10 s take never finishes: one pass, NOT whole.
  if (photos.drift && photos.drift.segments[0].whole) { bad++; detail.push('a 12s cycle claimed to finish in 10s'); }
  if (photos.drift && !driftLabel(photos.drift, 10).includes('cut off')) {
    bad++; detail.push(`label: ${driftLabel(photos.drift, 10)}`);
  }
  // And where it does finish, it says so through the same arithmetic a lane does.
  const long = takeMap(24, [], null, drift);
  if (!long.drift || driftLabel(long.drift, 24) !== 'drift — 12s x2') {
    bad++; detail.push(`24s: ${long.drift ? driftLabel(long.drift, 24) : 'no row'}`);
  }
  // IT TAKES NO SLOT. Nine clips + music + a drift: the lanes are unchanged
  // from I12's answer and the drift is still drawn.
  const full = takeMap(15, [...Array.from({ length: MAX_LANES + 1 }, (_, i) => clip(i)), music], null, drift);
  if (full.lanes.length !== MAX_LANES) { bad++; detail.push(`crowded lanes=${full.lanes.length}`); }
  if (full.hiddenLanes !== 2) { bad++; detail.push(`crowded hidden=${full.hiddenLanes}`); }
  if (full.unknownLanes !== 0) { bad++; detail.push(`crowded unknown=${full.unknownLanes}`); }
  if (!full.drift) { bad++; detail.push('the drift row was evicted by nine clips'); }
  // A STILL TAKE IS STILL EMPTY, and so is a take with no length to draw on.
  if (!takeMap(10, [], null, 0).empty) { bad++; detail.push('a still take is no longer empty'); }
  if (!takeMap(10, [], null).empty) { bad++; detail.push('an absent drift argument is no longer still'); }
  if (takeMap(0, [], null, drift) !== EMPTY_MAP) { bad++; detail.push('a zero take is no longer EMPTY_MAP'); }
  for (const junk of [NaN, Infinity, -3, '12', null]) {
    if (takeMap(10, [], null, junk).drift !== null) { bad++; detail.push(`drift=${String(junk)} drew a row`); }
  }
  ok('I15 the drift is a row and never a source', bad === 0, detail.join(' · '));
}

// -----------------------------------------------------------------------------
console.log(results.join('\n'));
console.log(failures === 0 ? '\nALL INVARIANTS HOLD' : `\n${failures} INVARIANT(S) FAILED`);
process.exit(failures === 0 ? 0 : 1);

// =============================================================================
// WHAT MUTATION TESTING SAID — the block line 44 has been pointing at since
// this file was written, finally here.
//
// THE DRIFT ROW (DECISION 5), nine edits to `src/lib/takeMap.ts`, each applied
// alone to the REAL module with this sweep as the only judge:
//
//   KILL   M1  `driftPlan` drops the `isMoving` guard            -> I14
//   KILL   M2  `MOVE_CYCLE_SEC * rate` instead of `/ rate`       -> I13, I14
//   KILL   M3  `driftPlan` ignores the pace entirely             -> I13, I14
//   KILL   M4  `empty` forgets the drift                         -> I15
//   EQUIV  M5  `driftPasses` drops the `> 0` half of its guard
//   KILL   M6  `driftLabel` names the row `clip`                 -> I15
//   KILL   M7  the row's period is the TAKE, not the cycle       -> I8, I12, I15
//   KILL   M8  `passesLabel` reads the FIRST pass for `partial`  -> I10
//   KILL   M9  `driftPasses` marks every pass whole              -> I15
//
// M5 IS EQUIVALENT, NOT A HOLE, and the difference is worth writing down.
// `lapSegments` already refuses a non-positive period and answers `laps: 0`,
// which the very next line turns into `null` — so the `> 0` test in
// `driftPasses` cannot change an output. It is kept because the redundancy is
// with a DIFFERENT module's contract: the day `lapSegments` grows a branch that
// answers something else for 0, this guard is what stops a row being drawn for
// a collage that does not move. A mutation surviving because two functions
// agree is not the same fact as one surviving because nothing is watching.
//
// M8 is the interesting kill: `passesLabel` was EXTRACTED this cycle so the
// drift and a source share one arithmetic, and the mutation confirms the
// extraction is load-bearing — breaking it fails I10, an invariant written for
// the lane label two cycles before the drift existed.
//
// Harness: apply one edit, run this file, restore FROM A SAVED COPY. Restoring
// with `git checkout --` throws away the uncommitted work being tested — it did
// exactly that on the first run, and the remaining eight mutations then ran
// against a module with no drift in it and reported nothing.
// =============================================================================
