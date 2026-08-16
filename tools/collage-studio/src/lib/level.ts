// =============================================================================
// THE LEVEL — how loud ONE SOURCE sits in the mix.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// THE RUNG. The Audio rung's own "still owed" list has read `volume per source,
// ducking` since THE SOUNDTRACK shipped, and until now every gain in this app
// was a BOOLEAN wearing a number's clothes: `describeAudioSources` emitted
// `gain: wanted ? 1 : 0`, `soundtrackSource` emitted `gain: t.muted ? 0 : 1`,
// and `applyMutes` wrote `audible ? 1 : 0` into every node. So the only two
// answers to "how loud is the music under the clips" were ALL and NOTHING —
// which is the one edit anybody makes after dropping a song onto footage.
//
// A LEVEL IS A RELATIVE STATEMENT, AND THAT IS WHAT MAKES IT MEASURABLE.
//   The quantity a person is setting is not "how loud is the music" but "how
//   loud is the music AGAINST everything else", and `offlineAudio.mixSources`
//   ends by scaling the whole mix to a -3 dBFS ceiling — one scalar over every
//   sample — so the absolute energy of any one source in a finished export is
//   partly the limiter's answer and not the user's. The RATIO between two
//   sources is the user's alone: the limiter's scalar cancels out of it exactly.
//   MEASURED at the artifact (`tests/e2e/level.spec.ts` L1), one 440 Hz clip
//   under a 1500 Hz song, the same collage exported twice: music/clip 1.2912 at
//   100% -> 0.3227 at 25% = 0.2499x, i.e. 12.0 dB down against a nominal 12.04.
//   The clip's own bin is 0.08502 in BOTH files — bit-for-bit the same number —
//   so the control moved the source it names and nothing else.
//   THE HONEST COROLLARY, said out loud because it surprises: on a collage with
//   ONE audible source there is nothing to be relative TO, and a level there is
//   just a quieter file. Volume is volume when there is only one of them.
//
// WHY A ROSTER OF FIVE AND NOT A SLIDER.
//   Every other per-source control in this app is a roster (`lib/speed.ts` is
//   the direct template) and a quantised index is quantised by construction —
//   the argument `lib/pace.ts` made when it needed no snapping arm at all. A
//   continuous fader on a phone is also the harder 44 px problem: five chips at
//   `flex-1` already fit the sheet the speed row lives on, measured.
//   THE STEPS ARE -6 dB EACH, i.e. exact halvings of AMPLITUDE — the one
//   interval every listener reads as a real change, and (like the speed roster's
//   powers of two, and for a weaker but real version of the same reason) exact
//   in binary, so a level applied in the live graph and the same level applied
//   in the offline mixer agree in the last bits rather than to within a rounding.
//
// THE LEVEL IS APPLIED EXACTLY ONCE — see `livePath`, which is the whole reason
// this module owns a function about the LIVE path at all rather than just a
// roster. A `MediaElementAudioSourceNode` taps its element AFTER the element's
// own `volume`, which `stage.applyMutes` already relies on ("the element's own
// `muted` still gates the signal entering the WebAudio graph"). So writing the
// level into both `el.volume` and the gain node squares it: 25% would render at
// 6%. One number, two places it could live, and a rule for which.
//
// WHAT IS NOT HERE, SAID PLAINLY.
//   - NO BOOST. The roster stops at 100% and `safeLevel` clamps above it. Makeup
//     gain is a different feature with a different answer to the clipping
//     question, and the limiter would take most of it back anyway.
//   - SILENCE IS NOT ON THE ROSTER. `muted` already owns 0 and is load-bearing
//     in four places (`applyMutes`, `describeAudioSources`, `ensurePrimaryAudible`,
//     the chip's own aria state). A sixth chip meaning "off" would be a second
//     control for one fact — the two-guards-on-one-resource defect this file's
//     neighbours are already scarred by — so the speaker button stays the mute
//     and this roster is what the sound does when it is NOT muted.
//   - A LEVEL DOES NOT RIDE THE DICE OR THE COMPOSITION CODE, for the reason the
//     trim, the speed and the music itself do not: a code is a RECIPE somebody
//     else opens with their own sources, and a level is a fact about a FILE the
//     code cannot see. `lib/rollCode.ts` owns that boundary and it does not move.
//   - NO AUTOMATIC DUCKING. Lowering the music only while a clip is talking is
//     the next rung and it is a different machine (it needs the clip's envelope,
//     which means analysing a decode the live path does not have).
// =============================================================================

/** One entry on the roster: what the chip says and what it multiplies. */
export interface LevelChoice {
  /** Stable id — the test hook and the React key. Never shown. */
  id: string;
  /** The amplitude multiplier itself. */
  level: number;
  /** The chip's face. */
  label: string;
  /** The chip's `title`, in the app's own voice. */
  title: string;
}

/** The level a source has when nobody has touched it. */
export const FULL_LEVEL = 1;

/**
 * The quietest the roster goes: -24 dB. Low enough to sit a song under speech,
 * high enough that the chip is never a synonym for the mute button beside it.
 */
export const LEVEL_MIN = 0.0625;

/**
 * THE ROSTER. Five, matching every other chip row in this app, running loud to
 * quiet — and NOT centred like the speed roster, because unlike a speed there is
 * nothing above the default to centre against.
 */
export const LEVELS: readonly LevelChoice[] = [
  { id: 'full', level: 1, label: '100%', title: 'As loud as the file is — 0 dB' },
  { id: 'half', level: 0.5, label: '50%', title: 'Half as loud — 6 dB down' },
  { id: 'quarter', level: 0.25, label: '25%', title: 'A quarter as loud — 12 dB down, the usual place for music under talking' },
  { id: 'eighth', level: 0.125, label: '12%', title: 'Well under everything else — 18 dB down' },
  { id: 'bed', level: LEVEL_MIN, label: '6%', title: 'A bed — 24 dB down, present but never in the way' },
];

const finite = (n: number | undefined | null): n is number =>
  typeof n === 'number' && Number.isFinite(n);

/**
 * Any input to a usable multiplier.
 *
 * ABSENT MEANS FULL, NEVER "KEEP WHAT IS THERE" — the same rule `normaliseWindow`
 * and `safeSpeed` state, and this project has a scar with that exact name.
 *
 * A FINITE OUT-OF-RANGE NUMBER IS CLAMPED; A NON-FINITE ONE IS NOT, which is
 * `safeSpeed`'s asymmetry verbatim because these two numbers get multiplied into
 * the same render and must not disagree about what a non-number means.
 *
 * THE ONE PLACE THIS DEPARTS FROM `safeSpeed` IS THE SIGN, and the departure is
 * the point. `safeSpeed` sends `<= 0` back to natural because a rate of 0 is a
 * STALLED `AudioBufferSourceNode` rather than a slow one — a hazard. A level has
 * no such hazard, so the two halves of "not positive" get the answer each one
 * actually deserves: 0 (and anything under the floor) is somebody asking for
 * QUIET and clamps UP to `LEVEL_MIN`, while a NEGATIVE amplitude is a phase flip
 * nobody can have meant and falls back to FULL with the other broken values.
 */
export const safeLevel = (level?: number | null): number => {
  if (!finite(level) || level < 0) return FULL_LEVEL;
  if (level > FULL_LEVEL) return FULL_LEVEL;
  return level < LEVEL_MIN ? LEVEL_MIN : level;
};

/** True when this source is not at the level its file is. The badge test. */
export const isQuieted = (level?: number | null): boolean => safeLevel(level) !== FULL_LEVEL;

/** The roster entry a value resolves to, or null when it sits between chips. */
export const levelChoice = (level?: number | null): LevelChoice | null => {
  const l = safeLevel(level);
  return LEVELS.find((c) => c.level === l) ?? null;
};

/**
 * `50%`, `12%`, `6%` — the chip's face for an arbitrary value, so a restored
 * state between two chips still reads as a number rather than as nothing.
 * TRUNCATED, NOT ROUNDED: 0.125 must print `12%` and match the roster's own
 * label, and rounding would print `13%` for the value the chip beside it holds.
 */
export const levelLabel = (level?: number | null): string =>
  `${Math.floor(safeLevel(level) * 100)}%`;

/**
 * How far down this level is, in dB, as a POSITIVE number of decibels of
 * attenuation — `0` at full, `6` at half, `24` at the bed. For the readout
 * sentence and the chip titles; nothing in the render reads it.
 */
export const levelDb = (level?: number | null): number => {
  const l = safeLevel(level);
  if (l >= FULL_LEVEL) return 0;
  return Math.round(-20 * Math.log10(l) * 10) / 10;
};

/**
 * WHAT THE OFFLINE MIXER IS TOLD — the one expression `describeAudioSources` and
 * `soundtrackSource` both emit, so a clip and the music can never disagree about
 * what a level means to a file being written.
 *
 * `wanted` is INTENT (`!muted`), never `audible`: that distinction is the bug
 * that made every export silent once already, and it is written up at length on
 * `StageClipStatus.wantsAudio`. A level multiplies intent; it does not replace
 * it, so a muted source at 100% is still 0 and an unmuted one at the bed is
 * still a source (`mixSources` admits anything `> 0`).
 */
export const mixGain = (wanted: boolean, level?: number | null): number =>
  wanted ? safeLevel(level) : 0;

/** The two numbers the LIVE path writes, and the one they must multiply to. */
export interface LivePath {
  /** `GainNode.gain.value`. Meaningless (and 1) when there is no graph. */
  node: number;
  /** `HTMLMediaElement.volume`. */
  element: number;
  /** What the listener actually gets: the product, by construction. */
  effective: number;
}

/**
 * HOW THE LIVE GRAPH CARRIES A LEVEL — and the invariant is `node * element ===
 * effective`, in every branch, which is what makes the squaring bug in this
 * module's header untestable rather than merely fixed.
 *
 * The level rides the GAIN NODE when there is one, because that node is what
 * `captureStream` taps through `masterGain` — so the realtime recorder gets the
 * mix the room hears, for free, exactly as it already did for mute.
 *
 * When `buildAudioChain` failed there IS no node (its catch leaves `gain: null`
 * and the clip "still plays through the element's own output"), and then the
 * element's `volume` is the only stage there is, so the level goes there
 * instead. `node` reads 1 in that branch — a don't-care chosen so the product
 * invariant holds in both, rather than a value anybody writes.
 *
 * COMPATIBILITY, and it is exact: at `FULL_LEVEL` this returns `{node: audible ?
 * 1 : 0, element: audible ? 1 : 0}` in the graph branch — character for
 * character what `applyMutes` wrote before this rung existed — so every source
 * nobody has quietened is bit-identical.
 */
export const livePath = (
  audible: boolean,
  level: number | null | undefined,
  hasGraph: boolean,
): LivePath => {
  const effective = audible ? safeLevel(level) : 0;
  return hasGraph
    ? { node: effective, element: audible ? 1 : 0, effective }
    : { node: 1, element: effective, effective };
};
