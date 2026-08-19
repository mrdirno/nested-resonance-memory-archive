// src/lib/admission.ts
// -----------------------------------------------------------------------------
// ADMISSION — WHICH CLIPS GET A REALTIME DECODER, AND HOW A STALL IS JUDGED.
//
// Pure. No DOM, no element, no clock. `stage.ts` owns the elements and calls
// in here with numbers; the unit sweep (tests/unit/admission.invariants.mjs)
// transpiles THIS file, so the plan measured there is the plan the Stage runs.
//
// THE WISH THIS EXISTS FOR (collage well, anonymous):
//   "Multiple videos should play back at the same time. Concurrency not just one."
//
// WHAT WAS TRUE BEFORE. Two guards decided who plays: a decoder COUNT cap and a
// summed-source-PIXEL cap of `count × 1080p`. The pixel cap was a constant — a
// guess about hardware, never a measurement — and on a phone it was 6.2 Mpx.
// A phone-shot 4K clip is 8.3 Mpx. So the first 4K clip was admitted (the
// first one is always let in) and EVERY further clip was refused — a 1080p one
// too, since 8.3 + 2.1 is also over — on every phone, with the notice "1 of 2
// clips playing (these clips are too high-resolution to decode together)".
// Two videos from the same phone the page was open on, and the app played one
// of them. That is the wish.
//
// WHAT IS TRUE NOW. Two guards still, with different jobs:
//   · The COUNT cap is unchanged (`capsForSignals`): decoder SESSIONS are the
//     limit iOS actually enforces, and 3-4 on a phone is what survives Low Power
//     Mode with sound on one of them. It has no measured counterpart, so it is
//     not raised.
//   · The PIXEL guard is a SANITY CEILING: the count cap, FILLED — a few seats
//     at DCI 4K (4096 × 2160, the largest frame a camera labels "4K", so any 4K
//     shape fits a seat) and the rest at 1080p. It exists to refuse an 8K stack
//     or a third phone 4K a-priori, not to ration 1080p. Behind it sits a
//     MEASURED ceiling: the lowest summed-pixel load at which a decoder was
//     SEEN to stall this session. With two or more clips live, admission never
//     reaches a load that has already failed; the first-ranked clip is admitted
//     regardless, because a budget that admits nothing is a broken page.
//
// HOW A STALL IS SEEN (`judgeStall`). A gesture block and iOS Low Power Mode stop
// EVERY clip at once; a decode-budget overrun leaves SOME decoders running and
// starves the rest — and a starved decoder is NOT PAUSED: the element reports
// `paused === false` while presenting no frames. So a clip that is not advancing
// is a gesture / power / permission problem when it is paused, or when nobody
// else is advancing either; it is the budget only when it is un-paused, frozen,
// and a sibling is moving. Before this, every stall was reported as "Tap to
// start playback", which is the wrong sentence for a decoder the OS starved.
// -----------------------------------------------------------------------------

/** One 1080p frame — the unit the OLD budget was denominated in (kept for the record). */
export const HD_STREAM_PIXELS = 1920 * 1080;    // 2,073,600
/** One UHD (3840 × 2160) frame — what a phone calls 4K. */
export const UHD_STREAM_PIXELS = 3840 * 2160;   // 8,294,400
/**
 * One DCI 4K (4096 × 2160) frame — the unit the sanity ceiling is denominated
 * in. Two UHD clips sum to 16.59 Mpx, two DCI to 17.69 Mpx; a ceiling of
 * `2 × UHD` let the first pair through on the boundary and refused the second
 * with the wish's exact sentence. Two of ANY 4K shape fit under `2 × DCI`.
 */
export const DCI_4K_STREAM_PIXELS = 4096 * 2160; // 8,847,360

/**
 * Pixels charged for a clip whose real dimensions have not landed yet. Larger
 * than 720p and smaller than 1080p on purpose: it holds the budget open for a
 * typical phone clip without pretending to know it is 4K. Also the charge for
 * a candidate whose stated pixels are nonsense (≤ 0, NaN) — a zero would make
 * a clip free and let a stack of them through the pixel guard.
 */
export const UNKNOWN_SOURCE_PIXELS = 1_280_000;

export type AdmissionVerdict =
  | 'live'               // admitted and decoding
  | 'over-clip-cap'      // deferred: too many simultaneous decoders for this device
  | 'over-pixel-cap'     // deferred: summed source pixels would pass the a-priori sanity ceiling
  | 'over-measured-cap'  // deferred: summed source pixels would reach a load SEEN to stall this session
  | 'unused';            // liveEnabled is off (offline / capture-only), or nothing to admit

export interface AdmissionCandidate {
  id: string;
  /** On-screen area this clip covers (its fragments summed). Larger goes first. */
  area: number;
  /** Import order; the tiebreak so equal areas rank deterministically. */
  index: number;
  /** Source pixels — `pixelCost()` — always > 0. */
  pixels: number;
}

export interface AdmissionCaps {
  /** Maximum simultaneous decoders. Clamped to ≥ 1 while admission is enabled. */
  maxClips: number;
  /** A-priori sanity ceiling on summed source pixels. 0 disables it. */
  maxPixels: number;
  /**
   * MEASURED ceiling: the lowest summed-pixel load at which a decoder was seen to
   * stall this session (`settleStall`). 0 = nothing measured. Admission never
   * reaches this load again while more than one clip is live.
   */
  measuredCeiling: number;
}

export interface AdmissionRow {
  id: string;
  verdict: AdmissionVerdict;
}

export interface AdmissionPlan {
  /** Every candidate, in RANKED order (area desc, index asc). */
  rows: AdmissionRow[];
  /** The admitted ids, ranked. */
  liveIds: string[];
  /** Summed source pixels of the admitted set. */
  livePixels: number;
}

/**
 * What a clip costs the decode budget: its real frame, else the intake hint,
 * else the unknown-source charge. Never 0 — a zero would make a clip free and
 * let a stack of them through the pixel guard.
 */
export const pixelCost = (vw: number, vh: number, hintW: number, hintH: number): number => {
  if (vw > 0 && vh > 0) return vw * vh;
  if (hintW > 0 && hintH > 0) return hintW * hintH;
  return UNKNOWN_SOURCE_PIXELS;
};

const num = (n: unknown, fallback: number): number =>
  typeof n === 'number' && Number.isFinite(n) ? n : fallback;

/**
 * THE PLAN. Ranking is by on-screen area (the biggest picture gets a decoder
 * first), ties by import order. The FIRST ranked clip is always admitted when
 * admission is enabled — a budget that admits nothing is not a budget, it is a
 * broken page, so a count cap of 0 (or NaN) reads as 1 — and every later clip
 * is checked against, in order: the count cap, the MEASURED ceiling, the
 * a-priori sanity ceiling.
 *
 * The measured ceiling is checked BEFORE the sanity ceiling so the verdict names
 * the guard that actually knows something: "this device could not decode them
 * all at once" is a fact about this session; "too high-resolution" is a rule.
 */
export const planAdmission = (
  candidates: readonly AdmissionCandidate[],
  caps: AdmissionCaps,
  liveEnabled: boolean,
): AdmissionPlan => {
  const maxClips = Math.max(liveEnabled ? 1 : 0, Math.floor(num(caps?.maxClips, 0)));
  const maxPixels = Math.max(0, num(caps?.maxPixels, 0));
  const measured = Math.max(0, num(caps?.measuredCeiling, 0));

  const ranked = (candidates || [])
    .filter((c): c is AdmissionCandidate => !!c && typeof c.id === 'string')
    .map((c) => {
      const px = num(c.pixels, 0);
      return {
        id: c.id,
        area: num(c.area, 0),
        index: num(c.index, 0),
        pixels: px > 0 ? px : UNKNOWN_SOURCE_PIXELS,
      };
    })
    .sort((a, b) => (b.area - a.area) || (a.index - b.index));

  const rows: AdmissionRow[] = [];
  const liveIds: string[] = [];
  let count = 0;
  let pixels = 0;

  for (const c of ranked) {
    let verdict: AdmissionVerdict = 'live';
    if (!liveEnabled) {
      verdict = 'unused';
    } else if (count >= maxClips) {
      verdict = 'over-clip-cap';
    } else if (measured > 0 && count > 0 && pixels + c.pixels >= measured) {
      verdict = 'over-measured-cap';
    } else if (maxPixels > 0 && count > 0 && pixels + c.pixels > maxPixels) {
      verdict = 'over-pixel-cap';
    }
    rows.push({ id: c.id, verdict });
    if (verdict === 'live') {
      count++;
      pixels += c.pixels;
      liveIds.push(c.id);
    }
  }
  return { rows, liveIds, livePixels: pixels };
};

/**
 * RECORD A STALL at summed load `stalledPixels`. The ceiling only ever comes
 * DOWN: a second stall at a lower load is a tighter fact; a stall at a higher
 * load than one already recorded says nothing new. A stall with the load at 0
 * (nothing admitted) is noise and leaves the ceiling alone.
 */
export const noteStall = (measuredCeiling: number, stalledPixels: number): number => {
  const cur = Math.max(0, num(measuredCeiling, 0));
  const at = Math.max(0, num(stalledPixels, 0));
  if (at <= 0) return cur;
  return cur > 0 ? Math.min(cur, at) : at;
};

/**
 * HOW MANY STALL ROUNDS AN EPISODE MAY SPEND EXPLORING. Every stall lowers the
 * ceiling to the load that failed, and the next plan may swap a smaller clip IN
 * for the refused big one — a load nobody has measured. On a phone that is two
 * rounds; on a desktop with eight clips of mixed sizes the greedy plan can in
 * principle try more. Each round costs the viewer a confirmed probe (two
 * windows) and a cooldown — two to three seconds of a picture re-settling — so
 * past this many the exploration ends: the ceiling snaps to one decoder
 * (`settleStall`), which is the seat the old budget usually gave such a device
 * anyway, and it is honest — every larger load was tried. The Stage counts
 * rounds per EPISODE (a plan that held for a while ends one), never per session.
 */
export const MAX_STALL_ROUNDS = 4;

/**
 * THE STALL RESPONSE, whole: the new ceiling after a stall at `stalledPixels`
 * on round `round` (1-based count of stalls this episode), given the pixels of
 * the top-ranked clip. Rounds up to the bound lower the ceiling to the failed
 * load; the round past it collapses to `topPixels + 1`, i.e. exactly one
 * decoder (the first is always admitted; a second would need `pixels + px <
 * top + 1`, impossible for any px ≥ 1).
 *
 * THE FLOOR. The result is never below `topPixels + 1`. A ceiling under that is
 * the same plan as the collapse — one decoder — so a mis-measurement (a stale
 * load, a probe that raced a re-plan) can cost at most the collapse state, never
 * a ceiling the top clip alone could not clear.
 */
export const settleStall = (
  measuredCeiling: number,
  stalledPixels: number,
  round: number,
  topPixels: number,
): number => {
  const top = Math.max(1, Math.floor(num(topPixels, 1)));
  const lowered = noteStall(measuredCeiling, stalledPixels);
  const r = Math.max(1, Math.floor(num(round, 1)));
  const settled = r <= MAX_STALL_ROUNDS ? lowered : noteStall(lowered, top + 1);
  return settled > 0 ? Math.max(settled, top + 1) : settled;
};

export interface StallObservation {
  id: string;
  /** The clip is admitted, seated (has presented a frame, or is past its grace), AND the caller wants it playing. */
  wantsPlay: boolean;
  /** It presented frames (or, without a frame counter, its clock moved) over the probe window. */
  advanced: boolean;
  /**
   * The element reports `paused`. A starved decoder is NOT paused — it is
   * un-paused and frozen — so a paused non-advancer is permission / power /
   * end-of-media, never a budget verdict. Optional for callers that cannot
   * read it; absent means un-paused.
   */
  paused?: boolean;
}

export type StallKind =
  | 'fine'      // the subject advanced
  | 'blocked'   // the subject is paused, or NOBODY who wanted to play advanced: a gesture / Low Power / OS-wide pause
  | 'stalled';  // un-paused, frozen, while others advanced: a decode-budget verdict, local

export interface StallJudgement {
  kind: StallKind;
  /** Every wanted, un-paused clip that did not advance — the ones a budget verdict is about. */
  stalled: string[];
}

/**
 * THE JUDGE. Given every live clip's observation over the same window and the
 * clip whose probe fired, say what the stall means. Empty or absent input, or a
 * subject that is not in the observations, is `fine` — the probe has nothing to
 * accuse and must not evict on it.
 */
export const judgeStall = (
  observations: readonly StallObservation[],
  subjectId: string,
): StallJudgement => {
  const obs = (observations || []).filter((o) => !!o && typeof o.id === 'string');
  const wanted = obs.filter((o) => o.wantsPlay);
  const subject = wanted.find((o) => o.id === subjectId);
  if (!subject) return { kind: 'fine', stalled: [] };
  if (subject.advanced) return { kind: 'fine', stalled: [] };
  const stalled = wanted.filter((o) => !o.advanced && !o.paused).map((o) => o.id);
  if (subject.paused) return { kind: 'blocked', stalled };
  const anyAdvanced = wanted.some((o) => o.advanced);
  if (!anyAdvanced) return { kind: 'blocked', stalled };
  return { kind: 'stalled', stalled };
};

// -----------------------------------------------------------------------------
// DEVICE CAPS
// -----------------------------------------------------------------------------

export interface DeviceSignals {
  /** iOS / Android / coarse pointer. */
  mobile: boolean;
  /** `navigator.hardwareConcurrency`, or the caller's default. */
  cores: number;
  /**
   * `navigator.deviceMemory` in GB; 0 (or absent) = NOT REPORTED. Chromium
   * reports it (quantised to …, 4, 8); iOS Safari, desktop Safari and Firefox
   * never do — so a phone that says nothing is never a flagship, and a desktop
   * that says nothing sits in the middle tier rather than the top one.
   */
  memGb: number;
}

export interface RealtimeCaps {
  maxLiveClips: number;
  maxLivePixels: number;
}

/**
 * The COUNT cap is exactly what it was: on a phone, 3 is the largest number that
 * decodes in Low Power Mode with audio live on one of them, 4 when the phone
 * REPORTS the cores AND memory of a flagship (iOS reports neither, so an iPhone
 * is 3 by construction — the 4-clip phone tier is Android-only); on a desktop,
 * cores decide.
 *
 * The PIXEL sanity ceiling is THE COUNT CAP, FILLED: `S` seats at DCI 4K and the
 * remaining `N − S` at 1080p, where `N` is the count cap and `S` the number of
 * 4K seats the device is trusted with a-priori —
 *   · phone: S = 2, flagship or not. Two phone-shot 4K clips of any 4K shape plus
 *     a 1080p one always fit, which is the wish; a third 4K is refused a-priori,
 *     and whether two actually decode together is MEASURED (`settleStall`),
 *     because past the hardware limit the failure is silent and a-priori
 *     optimism is paid in frozen pictures.
 *   · desktop: S = 4 with ≥ 8 GB reported, 3 when memory is NOT reported
 *     (Safari, Firefox — a 2017 Air and a Mac Studio look identical), 2 below
 *     6 GB — memory, not cores, is what a wall of decoded 4K frames exhausts.
 * Every stack of 1080p clips the count cap allows fits by construction, so the
 * three-1080p case is byte-identical to before.
 */
export const capsForSignals = (sig: DeviceSignals): RealtimeCaps => {
  const cores = Math.max(1, num(sig?.cores, 4));
  const mem = Math.max(0, num(sig?.memGb, 0));
  const reported = mem > 0;
  let maxLiveClips: number;
  let seats4k: number;
  if (sig?.mobile) {
    const flagship = reported && cores >= 8 && mem >= 6;
    maxLiveClips = flagship ? 4 : 3;
    seats4k = 2;
  } else {
    maxLiveClips = cores >= 8 ? 8 : cores >= 4 ? 6 : 4;
    seats4k = !reported ? 3 : mem >= 8 ? 4 : mem >= 6 ? 3 : 2;
  }
  const s = Math.min(seats4k, maxLiveClips);
  return {
    maxLiveClips,
    maxLivePixels: s * DCI_4K_STREAM_PIXELS + (maxLiveClips - s) * HD_STREAM_PIXELS,
  };
};
