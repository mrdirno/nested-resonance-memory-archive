// src/lib/solo.ts
// -----------------------------------------------------------------------------
// SOLO — HEARING ONE SOURCE SO YOU CAN DECIDE ABOUT ALL OF THEM.
//
// From the well, verbatim intent: "When adding audio — Should start the added
// audio then take immediately to the details to see all audio playing that way
// user can solo the audio to determine what to keep enabled or muted should be
// intuitive."
//
// Read the second half carefully, because it is the whole design: solo is not a
// decision, it is how you MAKE one. The decision is the speaker button next to
// each source — "is this sound part of the piece" — and that is what the export
// renders. Solo only changes which of them reaches your ears while you are
// deciding. So this module computes AUDIBILITY and nothing else, and every
// function in it is pure: nothing here can write a mute.
//
// THAT SPLIT IS NOT NEW AND IT IS NOT OPTIONAL. `StageClipStatus.wantsAudio`
// (intent, exported) and `.audible` (speakers, right now) exist because a
// previous cut of this app derived the export from audibility and shipped
// silent files. Solo is a third thing pulling on audibility, so it gets the same
// treatment or it becomes the same bug.
//
// FOUR RULES, and each one is an invariant in tests/unit/solo.invariants.mjs:
//
//   1. ONE AT A TIME. Solo is exclusive — tapping a second source moves the
//      solo, tapping the soloed one releases it. Not a multi-select: the job is
//      "which one is that noise", asked of a six-chip row on a phone, and a
//      set-valued solo turns a two-tap answer into bookkeeping. Hearing two
//      sources TOGETHER is what releasing solo already does.
//
//   2. YOU CAN SOLO A MUTED SOURCE. It reads backwards until you remember what
//      the wish asked for — you are auditioning to decide what to KEEP, so the
//      candidate you most need to hear is the one currently switched off. Solo
//      therefore ignores the soloed source's own intent, and leaves it untouched.
//
//   3. SOLO DOES NOT OUTRANK THE MONITOR SWITCH. If the speaker in the transport
//      bar is off, soloing plays nothing — muting your own monitor means the room
//      is quiet, and a feature that shouted through it would be a bug with a
//      friendly name. (The act of tapping solo DOES turn the monitor on; that
//      happens in the setter, the same way unmuting a clip already does. Once on,
//      turning it back off wins.)
//
//   4. A TAKE IS NEVER SOLOED. The realtime capture path taps the same WebAudio
//      gains this plan writes — so a take started while soloing would RECORD the
//      solo, and the person would find out after the export. `capturing` is an
//      input to the plan rather than a caller's duty to remember: while a take
//      runs, the plan is exactly the plan with no solo at all.
//
// THE CUT AUDITION IS THE SAME SHAPE and is folded in here rather than beside
// it. Dragging a trim handle already made every other source step out of the
// room (`stage.applyMutes`: "AUDITION IS SOLO"), which is this rule with a
// different trigger and two deliberate differences — an audition outranks the
// monitor switch (the sound IS the control; a silent trim handle is a dead one)
// and plays at unity (a solo audition has no rest of the mix to sit against).
// Two exclusivity rules recomputed in two places is the drift this repo has
// already filed scars about, so there is one rule with a `kind`.
// -----------------------------------------------------------------------------

/** Unity — what an audition plays at, whatever the source's own level says. */
export const AUDITION_LEVEL = 1;

/**
 * WHO OWNS THE ROOM.
 *
 * `audition` and `solo` are both "only this one sounds"; they differ in the two
 * ways rule 3 and the header describe, and nothing else.
 */
export type Exclusive =
  | { kind: 'none' }
  | { kind: 'audition'; id: string }
  | { kind: 'solo'; id: string };

export const NO_EXCLUSIVE: Exclusive = { kind: 'none' };

/** One thing that can make a sound: a clip's own audio, or the music track. */
export interface SoundSource {
  id: string;
  /**
   * INTENT — "this source's sound is part of the piece". What the export
   * renders. Read here, never written; see rule 2.
   */
  wantsAudio: boolean;
  /** Its media errored. Nothing can make it audible, solo included. */
  broken?: boolean;
  /**
   * The REALTIME DECODER ADMISSION BUDGET holds a decoder for this source. A
   * clip the budget deferred renders as stills and cannot sound in the room no
   * matter what is asked of it — which is a fact about this device, not about
   * the piece, and never reaches the offline mix. `undefined` means the source
   * is not subject to the budget at all (the music track holds no video
   * decoder), and is therefore always live.
   */
  live?: boolean;
  /** How loud it sits in the mix, 0..1. `undefined` is unity. */
  level?: number;
}

export interface MonitorInput {
  sources: readonly SoundSource[];
  /** The transport bar's speaker: is this room making any sound at all. */
  soundOn: boolean;
  exclusive: Exclusive;
  /** A take is running. Rule 4: the plan ignores solo entirely while it is. */
  capturing?: boolean;
}

/** Why a source is, or is not, coming out of the speakers right now. */
export type MonitorReason =
  | 'audible'
  /** The transport speaker is off. */
  | 'monitor-off'
  /** Its own speaker button is off — the decision the user is here to make. */
  | 'muted'
  /** Something else is soloed. Intent is untouched; this is temporary. */
  | 'soloed-out'
  /** This device is not holding a decoder for it (it is showing as stills). */
  | 'deferred'
  /** Its media errored. */
  | 'broken';

export interface MonitorRow {
  id: string;
  audible: boolean;
  /** The level to play it at: its own, except an audition, which is unity. */
  level: number | undefined;
  reason: MonitorReason;
}

const owner = (x: Exclusive): string | null =>
  x.kind === 'none' ? null : x.id;

/**
 * WHAT EVERY SOURCE SHOULD BE DOING RIGHT NOW.
 *
 * Pure. Same length and same order as `sources` — a caller applies these rows
 * to elements positionally, and a plan that reordered would put one clip's gain
 * on another clip's decoder.
 */
export function monitorPlan(input: MonitorInput): MonitorRow[] {
  // RULE 4, applied before anything else reads it: a take erases the solo, but
  // NOT the audition — a trim handle cannot be held while a take runs (the
  // sheet is closed for the duration), so there is nothing to erase, and
  // pretending otherwise would only make this rule harder to read.
  const x: Exclusive =
    input.capturing && input.exclusive.kind === 'solo' ? NO_EXCLUSIVE : input.exclusive;
  const only = owner(x);

  return input.sources.map((s) => {
    const dead = !!s.broken;
    // `live !== false`: undefined means "not subject to the budget".
    const held = s.live !== false;

    if (x.kind === 'audition') {
      // Rule 3's exception: the sound IS the control being dragged.
      const audible = s.id === only && !dead && held;
      return {
        id: s.id,
        level: s.id === only ? AUDITION_LEVEL : s.level,
        audible,
        reason: audible
          ? 'audible'
          : s.id !== only
            ? 'soloed-out'
            : dead
              ? 'broken'
              : 'deferred',
      };
    }

    // The order of these tests is the order of the SENTENCE the UI says, so the
    // most actionable cause wins: a muted, deferred, monitor-off clip is
    // reported as `monitor-off` because that is the one tap that changes the
    // most. `broken` still outranks everything — no tap fixes it.
    let reason: MonitorReason;
    if (dead) reason = 'broken';
    else if (only !== null && s.id !== only) reason = 'soloed-out';
    else if (!input.soundOn) reason = 'monitor-off';
    else if (only === null && !s.wantsAudio) reason = 'muted';
    else if (!held) reason = 'deferred';
    else reason = 'audible';

    return { id: s.id, level: s.level, audible: reason === 'audible', reason };
  });
}

/**
 * THE EXCLUSIVE TOGGLE (rule 1). Tap a source: it takes the room. Tap it again:
 * the room goes back to the mix.
 */
export function nextSolo(current: string | null, id: string): string | null {
  return current === id ? null : id;
}

/**
 * DROP A SOLO WHOSE SOURCE IS GONE.
 *
 * Removing the clip you were soloing must not leave a solo pointing at nothing
 * — that state is silent for every remaining source, with no chip left to tap
 * to get out of it. Called on every roster change rather than on the remove
 * path alone, because a clip also leaves by being replaced, cleared, or dropped
 * on project load, and three call sites is three chances to forget one.
 */
export function pruneSolo(current: string | null, ids: readonly string[]): string | null {
  if (current === null) return null;
  return ids.includes(current) ? current : null;
}

/**
 * WHAT THE PANEL SAYS WHILE A SOLO IS HELD.
 *
 * It has to carry three facts in one line on a phone: that this is temporary,
 * that the export is untouched (the whole reason solo is safe to offer), and —
 * when the soloed source is turned down — WHY it is faint, because a source at
 * 15% soloed into an empty room sounds like a broken feature rather than like
 * the level the user themselves set.
 */
export function soloBanner(
  name: string,
  opts?: { level?: number; audible?: boolean },
): string {
  const level = opts?.level;
  const quiet =
    typeof level === 'number' && Number.isFinite(level) && level >= 0 && level < 0.995
      ? ` at ${Math.round(level * 100)}%`
      : '';
  const head = `Soloing ${name}${quiet}`;
  if (opts && opts.audible === false) {
    return `${head} — nothing is coming through; turn the preview sound on.`;
  }
  return `${head} — everything else is out of the room. Nothing about the export has changed.`;
}
