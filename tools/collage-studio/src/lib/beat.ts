// =============================================================================
// THE BEAT — the collage cuts ON THE MUSIC.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// WHAT WAS MISSING. Four cycles built a time axis and a sound: THE SOUNDTRACK
//   put music under the collage, THE TURN made the pictures re-cut, THE FADE
//   ended the take honestly and THE PACE gave the cuts a tempo. Every one of
//   those clocks was INDEPENDENT of the music. A collage with a 128 BPM track
//   under it cut every 5.000 s because `march` says 5.000 s, so the wall and
//   the song walked past each other for the whole take and met by accident.
//   Cutting on the beat is the single most recognisable thing an editor does
//   to a wall of pictures, and it was unaskable.
//
// THE DESIGN, IN ONE SENTENCE: A BEAT SYNC IS NOT A NEW RATE DIAL, IT IS A
// QUANTISER ON THE RATE THE COLLAGE ALREADY ASKED FOR.
//   The obvious first cut is a roster — cut every beat / half bar / bar / two
//   bars — and it is wrong twice over. It puts a FIFTH chip row in a dock that
//   already carries look, move, turn and pace on a phone; and it makes the two
//   controls that already answer "how often" (the turn's mode and THE PACE)
//   into dead weight the moment it is switched on, which is the exact defect
//   the ladder files against the pace itself ("a control that does nothing and
//   nothing says so"). So instead: the mode still says how often it WANTS to
//   cut (`march` 5 s, `ripple` 3.5 s), the pace still scales that want, and
//   this module SNAPS the result to the nearest musical multiple of the beat.
//   One toggle, no new vocabulary, and every existing control keeps its meaning
//   — `ripple` at 2x on a 128 BPM track is still the fastest thing in the app,
//   it just lands where the drums are.
//
// THE SNAP IS TO A POWER OF TWO, NEVER TO THE NEAREST INTEGER BEAT.
//   Rounding `target / period` to the nearest whole beat is one character
//   cheaper and musically wrong: at 128 BPM a 5 s target is 10.67 beats, and
//   11 beats is a hold that drifts across the bar line and lands on a different
//   part of the phrase every single time. `BEAT_MULTIPLES` is {1,2,4,8,16} —
//   the groupings 4/4 music is actually built out of — so a snapped hold is
//   always a whole number of half-bars and the wall cuts where a listener is
//   already expecting something to happen.
//
// THE FADE IS A FRACTION OF THE HOLD HERE, AND THAT IS `lib/pace.ts`'s
// ARGUMENT ARRIVING FROM THE OTHER SIDE.
//   `TURN_FADE_SEC` is a CONSTANT (0.7 s). The pace could leave it alone
//   because it scales the CLOCK, so `fade / hold` is invariant by construction.
//   A beat sync cannot: it sets an ABSOLUTE hold from something outside the
//   roster, and a 150 BPM track snapped to one bar gives a 1.6 s hold with a
//   0.7 s dissolve — 44% of the take soft, which is the smear the pace's header
//   proves the rejected design degenerates into. So the schedule carries its
//   own fade, `turnFadeFor(hold)` in lib/turn.ts, which keeps the roster's own
//   worst ratio (ripple: 0.7/3.5 = 20%) as a ceiling. Same invariant, reached
//   by clamping instead of by scaling, because here the hold is the given.
//
// DETECTION IS A COMB, NOT A BEAT TRACKER.
//   We do not need to know where every beat is; we need ONE period and ONE
//   phase, because the schedule is `first + k * hold` and nothing else. So:
//   an onset envelope (positive rectified RMS difference at an 8 ms hop),
//   autocorrelation over 60..180 BPM for a coarse period, then a fine search
//   over (period, phase) maximising the envelope sampled on the comb. The fine
//   pass is what makes it usable — the coarse ACF's resolution is one hop, and
//   at 180 BPM one hop of period error is 2.4% and drifts a whole beat away
//   inside twenty seconds.
//
// OCTAVE ERRORS ARE ABSORBED BY THE SNAP, AND THAT IS WHY THIS IS HONEST TO
//   SHIP. A tempo detector's classic failure is hearing 140 where a human hears
//   70, and for a beat TRACKER that is a wrong answer. Here it is not: the snap
//   picks the multiple nearest the target hold, so a doubled period picks half
//   the multiple and lands on the SAME instants. What the octave changes is the
//   number printed on the chip, not where the wall cuts.
//
// WHAT IT REFUSES. Music with no steady pulse (ambient, speech, a field
//   recording) has no comb that beats the flat one, and this returns NULL
//   rather than a plausible number. A collage that cuts confidently on a beat
//   that is not there is worse than one that does not sync at all, because the
//   user cannot tell which of the two they are looking at.
// =============================================================================

import { turnFadeFor, type TurnSchedule } from './turn';

/**
 * THE SWITCH, as a roster of two — because the code's alphabet is indexed and
 * "off" has to be index 0 for the same reason `still`, `hold` and `even` are:
 * an absent character in a legacy composition code decodes as 0.
 *
 * Two entries and not five. The division roster this could have been (every
 * beat / half bar / bar / two bars) is what the header argues against; leaving
 * it as an APPEND-ONLY list means a later cycle can add one without breaking a
 * single code already in somebody's chat log.
 */
export type SyncId = 'off' | 'beat';

export const SYNC_IDS: SyncId[] = ['off', 'beat'];

/** The row the chips render. Same list, same order, as `SYNC_IDS`. */
export const SYNCS: { id: SyncId; label: string; title: string }[] = [
  { id: 'off', label: 'OFF', title: 'The cuts run on their own clock — the TURN says how often, the PACE says how fast.' },
  { id: 'beat', label: 'ON THE BEAT', title: 'Snap the cuts to the music: the hold you asked for, rounded to the nearest bar.' },
];

export const isSynced = (id: unknown): boolean => id === 'beat';

/** Bars, when the count is whole bars of 4/4; otherwise beats. What the caption says. */
export const beatsLabel = (beats: number): string => {
  if (!(beats > 0)) return '';
  if (beats % 4 === 0) {
    const bars = beats / 4;
    return bars === 1 ? 'every bar' : `every ${bars} bars`;
  }
  if (beats === 1) return 'every beat';
  if (beats === 2) return 'every half bar';
  return `every ${beats} beats`;
};

/** The tempo band searched. Outside it, everything is somebody's half or double. */
export const BEAT_MIN_BPM = 60;
export const BEAT_MAX_BPM = 180;

/** Analysis hop. 8 ms: fine enough that a 180 BPM beat is 41 frames apart. */
export const BEAT_HOP_SEC = 0.008;

/**
 * How much of the track is listened to. Tempo is a property of a song, not of
 * its length, and decoding plus sweeping ten minutes on a phone to learn the
 * same number twice is a cost with no answer attached.
 */
export const BEAT_ANALYSE_SEC = 120;

/** Musical groupings, in beats. See the header: NOT "the nearest integer". */
export const BEAT_MULTIPLES = [1, 2, 4, 8, 16];

/**
 * The floor a comb must clear to be called a beat.
 *
 * `confidence` is the sharpness of the comb: how much more onset energy lands
 * ON the grid than lands anywhere, mapped so this floor means an energy ratio
 * of about 3.4. Measured in the sweep: a click track reads 1.00, drums under a
 * pad 1.00, a backbeat pattern 0.63 — and WHITE NOISE 0, which is the number
 * this constant exists for.
 */
export const BEAT_CONFIDENCE_FLOOR = 0.15;

export interface BeatGrid {
  /** Beats per minute, in [BEAT_MIN_BPM, BEAT_MAX_BPM]. */
  bpm: number;
  /** 60 / bpm. Carried rather than re-derived, because the schedule uses it. */
  periodSec: number;
  /** Where the first beat lands, seconds into the DECODED track. */
  offsetSec: number;
  /** 0..1. See BEAT_CONFIDENCE_FLOOR. */
  confidence: number;
}

/**
 * HOW MANY HOPS ONE ANALYSIS WINDOW SPANS. 2 = a 16 ms window stepped by 8 ms,
 * i.e. 50% overlap — and it is not a smoothing preference, it is the fix for a
 * measured bias. See `onsetEnvelope`.
 */
const WINDOW_HOPS = 2;

/**
 * THE ONSET ENVELOPE — positive rectified RMS difference, one value per hop,
 * measured over OVERLAPPING windows.
 *
 * Rectified because a beat is where energy ARRIVES; the decay between hits is
 * not an event and a signed difference would cancel the hit against it. RMS
 * rather than a spectral flux because the whole job is a period, and a period
 * survives the loss of every frequency detail: this runs on a mono 8 kHz decode
 * where a spectral method would cost an FFT per frame for a number this already
 * answers.
 *
 * THE OVERLAP IS THE LOAD-BEARING PART, AND IT COST THREE SWEEP FAILURES TO
 * FIND. With windows laid end to end, WHERE INSIDE A WINDOW an onset lands
 * changes how big it measures — and not by splitting it in two, which a wider
 * comb tooth would have recovered. RMS is a square ROOT of a mean: an impulse
 * divided between two windows raises each of their roots by less than it would
 * have raised one, so the total flux a straddling onset produces is genuinely
 * SMALLER. Measured on a 180 BPM click track at an 8 ms hop, where the beat is
 * 41.67 frames and every third click therefore lands well-aligned: the
 * well-aligned clicks read 0.405 and the straddling ones 0.311, so a comb at
 * ONE THIRD the true tempo — sampling only the aligned copies — scored 11%
 * higher than the truth and the detector called a 180 BPM track 60 BPM.
 *
 * A window twice the hop, stepped by the hop, means every onset lands fully
 * inside at least one window whatever its phase. Same measurement, same cost to
 * within a factor of two, and the alignment bias goes from 10.3% to 0.8% — far
 * under the 10% margin the octave rule needs to see past.
 */
export const onsetEnvelope = (
  samples: Float32Array,
  sampleRate: number,
  hopSec: number = BEAT_HOP_SEC,
): Float32Array => {
  const hop = Math.max(1, Math.round(sampleRate * hopSec));
  const win = hop * WINDOW_HOPS;
  const frames = Math.floor((samples.length - win) / hop);
  if (frames < 4) return new Float32Array(0);
  const env = new Float32Array(frames);
  let prev = 0;
  for (let f = 0; f < frames; f++) {
    let sum = 0;
    const base = f * hop;
    for (let i = 0; i < win; i++) {
      const v = samples[base + i];
      sum += v * v;
    }
    const rms = Math.sqrt(sum / win);
    env[f] = Math.max(0, rms - prev);
    prev = rms;
  }
  return env;
};

/**
 * HOW WIDE A TOOTH IS, in frames either side. One hop is 8 ms, so a tooth
 * gathers what arrived within about 12 ms of it — an order of magnitude inside
 * the ~50 ms window a listener will call "on the beat", and wide enough that
 * WHERE INSIDE A FRAME an onset landed stops mattering.
 */
const TOOTH_HALF = 1;
const TOOTH_FRAMES = 2 * TOOTH_HALF + 1;

/**
 * WHAT A TOOTH FINDS AT `x` — the onset energy WITHIN A TOLERANCE of it, as a
 * SUM over the frames it covers. Not a sample, and not their maximum.
 *
 * This is the difference between a working detector and a random-multiple one,
 * and it cost two sweep failures to get right. A click that starts 12% into a
 * frame puts nearly all its flux in that frame; the same click starting 79% in
 * splits it across two. Read pointwise — by interpolation OR by taking the
 * larger of the pair — the split click measures smaller, so a comb whose period
 * is a WHOLE NUMBER OF HOPS samples only the well-aligned copies and beats the
 * true period on an artefact of the grid. Measured: at an 8 ms hop, 180 BPM is
 * 41.67 frames and 60 BPM is exactly 125, and the true comb scored 0.352
 * against its own TRIPLE's 0.405 — so a 180 BPM track measured as 60.
 *
 * A SUM fixes it because flux is CONSERVED: however a click's energy is divided
 * between two frames, a window covering both recovers all of it. Every
 * candidate period is then measuring the same thing, which is what the
 * "shortest period that explains every hit" rule below assumes.
 */
const envWindow = (env: Float32Array, x: number): number => {
  const c = Math.round(x);
  if (!(c >= 0) || c >= env.length) return 0;
  let sum = 0;
  for (let i = c - TOOTH_HALF; i <= c + TOOTH_HALF; i++) {
    if (i >= 0 && i < env.length) sum += env[i];
  }
  return sum;
};

/**
 * THE COMB SCORE — mean tooth energy on a grid.
 *
 * A mean rather than a sum, because a sum grows with the number of teeth and
 * would prefer the fastest period in the band for no musical reason at all.
 */
const combScore = (env: Float32Array, periodFrames: number, phaseFrames: number): number => {
  if (!(periodFrames > 1)) return 0;
  let sum = 0;
  let n = 0;
  for (let x = phaseFrames; x < env.length - 1; x += periodFrames) {
    sum += envWindow(env, x);
    n++;
  }
  return n > 0 ? sum / n : 0;
};

/**
 * THE GRID, OR NULL.
 *
 * `samples` is one channel of the decoded track — mono is enough and is what
 * the app hands over, because a beat is not a stereo property.
 */
export const detectBeat = (
  samples: Float32Array | null | undefined,
  sampleRate: number,
  hopSec: number = BEAT_HOP_SEC,
): BeatGrid | null => {
  if (!samples || !(sampleRate > 0) || samples.length < sampleRate) return null;
  const env = onsetEnvelope(samples, sampleRate, hopSec);
  if (env.length < 64) return null;

  // The floor the comb is measured against. A track with no onsets at all has
  // nothing to find and every candidate scores zero.
  let mean = 0;
  for (let i = 0; i < env.length; i++) mean += env[i];
  mean /= env.length;
  if (!(mean > 0)) return null;

  const lagMin = Math.max(2, Math.floor((60 / BEAT_MAX_BPM) / hopSec));
  const lagMax = Math.min(env.length - 2, Math.ceil((60 / BEAT_MIN_BPM) / hopSec));
  if (lagMax <= lagMin) return null;

  // COARSE — autocorrelation, normalised by overlap so a long lag is not
  // penalised for having fewer terms to add up.
  let bestLag = lagMin;
  let bestAcf = -1;
  const acf = new Float64Array(lagMax + 1);
  for (let lag = lagMin; lag <= lagMax; lag++) {
    let sum = 0;
    const n = env.length - lag;
    for (let i = 0; i < n; i++) sum += env[i] * env[i + lag];
    acf[lag] = sum / n;
    if (acf[lag] > bestAcf) { bestAcf = acf[lag]; bestLag = lag; }
  }
  if (!(bestAcf > 0)) return null;

  // PARABOLIC REFINEMENT on the ACF peak — one hop of resolution is 2.4% of the
  // period at 180 BPM, which drifts a whole beat inside twenty seconds.
  let coarse = bestLag;
  if (bestLag > lagMin && bestLag < lagMax) {
    const a = acf[bestLag - 1];
    const b = acf[bestLag];
    const c = acf[bestLag + 1];
    const denom = a - 2 * b + c;
    if (denom !== 0) {
      const shift = (0.5 * (a - c)) / denom;
      if (Math.abs(shift) <= 1) coarse = bestLag + shift;
    }
  }

  /**
   * WHICH MULTIPLE OF WHAT IT FOUND — the step that decides whether this is a
   * tempo detector or a random-multiple detector.
   *
   * An autocorrelation cannot tell a period from its own multiples: on a click
   * track the normalised ACF at p, 2p and 3p are EQUAL, because every one of
   * them lines clicks up with clicks. Measured before this step existed, the
   * coarse peak came back at 2x on 120/128/140/150 BPM and 3x on 180.
   *
   * The comb can tell them apart, and by a property the ACF does not have: it
   * scores the MEAN ENERGY UNDER ITS OWN TEETH, so a comb whose teeth all land
   * on real hits scores full marks while one that alternates between a hit and
   * a gap scores the average of the two. That is exactly the difference between
   * the true beat and 1.5 beats on material with off-beats — and it is NOT the
   * difference between p and 3p, which both score full marks. So the rule needs
   * both halves: take the best-scoring candidate, then among everything within
   * `OCTAVE_KEEP` of it take the SHORTEST, because the shortest period that
   * explains every hit is the pulse and the rest are its multiples.
   *
   * The ratios are the ones a 4/4 grid actually produces — halves, thirds and
   * quarters of what the ACF locked onto, plus the 3/2 and 4/3 that a
   * half-beat backbeat generates. Anything landing outside the BPM band is
   * dropped, which is what stops the "shortest" rule from chasing hi-hats.
   */
  const OCTAVE_KEEP = 0.9;
  const RATIOS = [1 / 4, 1 / 3, 1 / 2, 2 / 3, 3 / 4, 1, 4 / 3, 3 / 2, 2, 3, 4];
  const cands: { p: number; ph: number; score: number }[] = [];
  for (const ratio of RATIOS) {
    const p = coarse * ratio;
    if (p < lagMin || p > lagMax) continue;
    // Phase only, at the candidate's own period: this pass is choosing WHICH
    // multiple, and refining every candidate's period first would cost eleven
    // fine searches to answer a question none of them is asked.
    let sc = -1;
    let ph0 = 0;
    const limit = Math.ceil(p);
    for (let ph = 0; ph < limit; ph++) {
      const s = combScore(env, p, ph);
      if (s > sc) { sc = s; ph0 = ph; }
    }
    if (sc > 0) cands.push({ p, ph: ph0, score: sc });
  }
  if (!cands.length) return null;
  const topScore = cands.reduce((m, c) => Math.max(m, c.score), 0);
  let chosen = cands[0];
  for (const c of cands) {
    if (c.score >= OCTAVE_KEEP * topScore && c.p < chosen.p) chosen = c;
    else if (chosen.score < OCTAVE_KEEP * topScore && c.score > chosen.score) chosen = c;
  }

  // FINE — the period AND the phase together, maximising the comb. The two are
  // not separable: the phase that fits a period 1% too short is not the phase
  // that fits the true one, so searching them in sequence finds the best phase
  // for the wrong period and stops.
  let bestScore = chosen.score;
  let bestPeriod = chosen.p;
  let bestPhase = chosen.ph;
  const span = Math.max(0.02, 1.5 / chosen.p);    // ±1.5 frames, as a fraction
  const STEPS = 24;
  for (let s = -STEPS; s <= STEPS; s++) {
    const p = chosen.p * (1 + (span * s) / STEPS);
    if (p < lagMin || p > lagMax) continue;
    // Whole-frame phases only: the envelope has no information between hops,
    // and interpolating the search grid finer than the data is arithmetic
    // pretending to be resolution.
    const limit = Math.ceil(p);
    for (let ph = 0; ph < limit; ph++) {
      const sc = combScore(env, p, ph);
      if (sc > bestScore) { bestScore = sc; bestPeriod = p; bestPhase = ph; }
    }
  }
  if (!(bestScore > 0)) return null;

  const periodSec = bestPeriod * hopSec;
  const bpm = 60 / periodSec;
  if (!(bpm >= BEAT_MIN_BPM - 0.5) || !(bpm <= BEAT_MAX_BPM + 0.5)) return null;

  /**
   * CONFIDENCE — ONE GATE, AND THE SECOND ONE WAS DROPPED AFTER MEASURING IT.
   *
   * The statistic is how much more onset energy the winning grid carries than
   * the same teeth dropped anywhere: `best / (TOOTH_FRAMES * mean)`. Measured
   * over the sweep's material — white noise 2.23, a slow tonal swell 6.75, a
   * backbeat pattern 6.29, drums under a pad 16.2, a bare click track 20.6 —
   * so the floor sits between noise and music with room on both sides.
   *
   * A SECOND GATE WAS BUILT AND REMOVED, which is worth recording because it
   * looked obviously necessary. It asked whether the winning PHASE was special
   * (the chosen comb against the average comb at the same period), on the
   * theory that a lottery winner among a hundred noisy phases would not be. It
   * is not an independent question: an average comb catches the average energy
   * density, so `phaseMean` is `TOOTH_FRAMES * mean` to two significant figures
   * on every signal tried — 2.25 against 2.23 on noise, 6.29 against 6.29 on
   * the backbeat. It cost a second full phase sweep to compute the number the
   * first gate already had.
   *
   * WHAT THIS DOES NOT CATCH, said plainly: a TONAL source with no percussion.
   * The swell above is accepted at 0.71 because its RMS really does rise and
   * fall periodically — there is a pulse, it is simply not one anybody would
   * tap to. The mitigations are the ones the design already has rather than a
   * cleverer number: the BPM is on the chip where it can be disbelieved, and
   * the sync is a switch nobody is holding down.
   */
  const energyRatio = bestScore / (TOOTH_FRAMES * mean);
  const confidence = Math.max(0, Math.min(1, (energyRatio - 2.5) / 6));
  if (confidence < BEAT_CONFIDENCE_FLOOR) return null;

  return {
    bpm: Math.round(bpm * 10) / 10,
    periodSec,
    /**
     * ONE HOP OF BIAS, PUT BACK. An onset at time t first raises the RMS of the
     * window that STARTS one hop before the frame containing it — that is what
     * an overlapping window is — so the flux peaks a frame early and every
     * measured phase came back ~9 ms ahead of the truth. Adding the overlap
     * back leaves a residual under one hop, which is 8 ms against a 33 ms video
     * frame: the schedule cannot express a finer phase than this even in
     * principle.
     */
    offsetSec: (bestPhase + (WINDOW_HOPS - 1)) * hopSec,
    confidence: Math.round(confidence * 1000) / 1000,
  };
};

/**
 * THE SNAP — the hold the collage asked for, as a musical number of beats.
 *
 * Returns the multiple from `BEAT_MULTIPLES` whose duration is nearest the
 * target IN LOG SPACE, because "nearest" on raw seconds is not the question a
 * listener asks. With a 0.5 s beat and a 3 s target, 4 beats (2 s) and 8 beats
 * (4 s) sit exactly 1 s away on either side — a dead tie on the difference, and
 * not a tie at all on tempo: the 2 s hold cuts 1.50x more often than asked, the
 * 4 s hold 1.33x less. A ratio sees that and picks the 4 s; a subtraction has
 * to break the tie on the sign of the error, which is arbitrary.
 */
export const snapHold = (
  targetSec: number,
  periodSec: number,
): { beats: number; holdSec: number } | null => {
  if (!(targetSec > 0) || !(periodSec > 0) || !Number.isFinite(targetSec) || !Number.isFinite(periodSec)) {
    return null;
  }
  let best = BEAT_MULTIPLES[0];
  let bestErr = Infinity;
  for (const m of BEAT_MULTIPLES) {
    const err = Math.abs(Math.log((m * periodSec) / targetSec));
    if (err < bestErr) { bestErr = err; best = m; }
  }
  return { beats: best, holdSec: best * periodSec };
};

/**
 * THE TURN'S SCHEDULE, IN THE TAKE'S OWN TIME.
 *
 * `inSec` is where the music was trimmed to start, and it is the whole reason
 * this is not just `grid.offsetSec`: output time 0 plays source time `inSec`,
 * so a beat at 0.31 s into the file is at 0.31 - inSec into the TAKE, modulo a
 * period.
 *
 * THE FIRST CUT LANDS ONE HOLD IN, exactly as the unsynced schedule's does
 * (`turnAt` puts turn 1 at t = hold), to within HALF A BEAT either way. Not
 * snapping the first cut at all would put it wherever
 * the song's first beat happens to fall — 40 ms in, on a track that starts on
 * the downbeat — and the take would open by blinking.
 *
 * A LAP IS NOT RE-PHASED, and that is inherited rather than chosen: the music
 * loops when the take outruns its window (`clipWindow`), and unless that window
 * is a whole number of beats the song's own downbeat moves on the second pass
 * while this grid does not. It is the same class as the turn's existing "a cut
 * at a lap is a hard cut" and is filed with it, not fixed here.
 */
export const beatSchedule = (
  grid: BeatGrid | null | undefined,
  targetHoldSec: number,
  inSec: number = 0,
): (TurnSchedule & { beats: number }) | null => {
  if (!grid || !(grid.periodSec > 0)) return null;
  const snapped = snapHold(targetHoldSec, grid.periodSec);
  if (!snapped) return null;
  const start = Number.isFinite(inSec) ? inSec : 0;
  const hold = snapped.holdSec;
  const rel = grid.offsetSec - start;
  /**
   * THE PHASE IS REDUCED MODULO THE BEAT, NOT MODULO THE HOLD — and the
   * difference is up to a whole hold of dead air at the top of every take.
   *
   * Both land on a beat (the hold is a whole number of beats, so the two grids
   * differ by a shift along the same beats), which is why the arithmetic sweep
   * could not tell them apart and the browser could. Measured at the artifact
   * with a 120 BPM track and `march` snapped to 4 s: the detector reported the
   * beat at 0.5 s rather than the one at 0.0 — both true — and reducing modulo
   * the HOLD made that a 0.5 s phase, so the first cut sat at 4.5 s where the
   * unsynced build cuts at 4.0. Worst case is a phase just under the hold, i.e.
   * a collage that waits nearly TWICE its own hold before it does anything.
   *
   * Modulo the beat, the phase is under one beat by construction and the first
   * cut lands one hold in plus at most one beat — which is what "the first cut
   * lands where the unsynced one does, on the nearest beat" actually means.
   */
  const period = grid.periodSec;
  // Positive modulo: a beat before the in-point is still a beat.
  let phase = ((rel % period) + period) % period;
  /**
   * AND THEN TO THE NEAREST BEAT, NOT THE NEXT ONE — the second half of the
   * same lesson, and the artifact caught this one too.
   *
   * A detector's phase is quantised to a hop, so the beat at 0.500 s comes back
   * as 0.496 — the same beat, measured 4 ms early. Reduced into [0, period) that
   * reads as a phase of 0.496, i.e. almost a WHOLE BEAT of delay, and the first
   * cut of a 4 s hold sat at 4.496 s where the unsynced build cuts at 4.000.
   * Measured in the browser, on the real decode: `offsetSec 0.496`, `first
   * 4.496`, and the wall was still dissolving at 4.8 s.
   *
   * Taking the representative nearest ZERO — a phase over half a beat becomes a
   * small NEGATIVE one — shifts the grid by exactly one period, which lands on
   * exactly the same beats, and puts the first cut within half a beat of where
   * the roster's own schedule would have put it. That is what "snap" means: the
   * nearest beat, in both directions.
   */
  if (phase > period / 2) phase -= period;
  return { hold, first: phase + hold, fade: turnFadeFor(hold), beats: snapped.beats };
};

/** What the chip says. Short, because it sits beside a roster on a phone. */
export const beatLabel = (grid: BeatGrid | null | undefined): string =>
  grid ? `${Math.round(grid.bpm)} BPM` : '';
