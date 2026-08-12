// =============================================================================
// THE TURN — the collage CUTS.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// WHAT IT IS, AND WHY IT IS THE RUNG IT IS.
//   Everything this app has shipped on the time axis so far moves the CROP (THE
//   MOVE), the SOUND (the soundtrack, the trim, the lap schedule, the fade) or
//   the CLOCK (the playhead). Not one of them changes WHICH PICTURE IS WHERE.
//   So a twenty-second export is one deal of photographs held for twenty
//   seconds, breathing. The fundamental verb of an editor — the CUT, one shot
//   becoming another — did not exist here at all.
//
//   THE TURN is that verb, in the grammar a collage actually has. Every few
//   seconds the pictures move to different fragments and cross-dissolve on the
//   way. It is simultaneously the cut, the cross-dissolve and (in `ripple`) the
//   wipe, because in a mosaic those three are the same event seen at different
//   granularities.
//
// THE ONE INVARIANT, AND IT IS WHAT THE WHOLE DESIGN IS FOR: EVERY STATE IS A
// PERMUTATION OF THE DEAL.
//   The fill is source-first and duplicate-free — that is the app's oldest
//   promise about what a collage IS (`lib/fill.ts`), and a time axis is exactly
//   the sort of thing that quietly breaks a static guarantee. So the turn is
//   defined as a permutation and nothing else: `assignmentAt` composes STEP
//   permutations, and a composition of permutations is a permutation, by
//   induction, at every k. Two fragments can therefore never hold the same
//   photograph — not at rest, not mid-dissolve, not after a thousand turns.
//
//   That constraint is also what rules out the obvious first design. "Stagger
//   the turns so the wall does not blink all at once" reads as pure upside
//   until you write the injectivity condition down: with slot j showing
//   `base[(j + k_j) mod n]` and k_j drawn from {k, k+1}, the map is injective
//   iff the turned set is closed under +1 — which, cyclically, forces it to be
//   ALL of them or NONE. A stagger over a global rotation is duplicate-free
//   only in the two cases where it is not a stagger. `ripple` gets its stagger
//   the way that survives the proof instead: it rotates a SUBSET among itself,
//   which is a permutation on the nose and leaves the rest of the wall alone.
//
// WHAT A TURN NEVER MOVES: THE FRAGMENT.
//   A turn changes WHICH PICTURE, never WHERE. The cell, its clip path, its
//   twist angle and its grown destination box are properties of the FRAGMENT
//   and are computed once per scene; only the source, its crop and its analysis
//   are re-pointed. That is what keeps the whole feature off the layout, off
//   `computeLayout`, off the SVG geometry and out of `refreshAdmission`.
//
// REST IS THE SHARED OBJECT, FOR THE REASON `NO_MOVE` IS.
//   `turnAt` returns the frozen `NO_TURN` BY REFERENCE at t=0, on `hold`, and
//   for the whole first hold of every mode — so the three surfaces that produce
//   a single frame (the still preview, the raster export, the SVG) pass no time
//   and are bit-identical to a build without this file, and the video opens on
//   the picture the preview was showing.
//
// PERIODIC ON A FIXED HOLD, NEVER ON THE TAKE — the argument THE MOVE settled.
//   A duration-keyed schedule would make the same collage cut differently at
//   10 s and at 30 s, and differently again when the device cap clips the take.
//   The hold is a property of the mode. The consequence is the honest one and
//   it is filed as a scar: the live preview's clock WRAPS at the take length,
//   so at a lap the wall snaps back to its base deal without a dissolve. The
//   exported file walks 0..L monotonically and never sees it.
//
// TIMING SHAPE. Turn k lands at t = k*hold, and the dissolve is the raised
//   cosine over the FADE_SEC after it — the same envelope family `motion.ts`
//   uses, chosen for the same reason: an eased blend reads as a breath and a
//   linear one reads as a machine.
// =============================================================================

/** The roster. Index order is the composition code's alphabet — APPEND ONLY.
 *  Reordering this array silently repoints every code ever minted. */
export type TurnId = 'hold' | 'march' | 'scatter' | 'ripple' | 'swap';

/** Index 0 is the no-op and must stay index 0: an absent character in a legacy
 *  composition code decodes as 0, and `TURN_IDS[0]` is what it becomes. */
export const TURN_IDS: TurnId[] = ['hold', 'march', 'scatter', 'ripple', 'swap'];

/** How long one cross-dissolve takes, shared by every mode. */
export const TURN_FADE_SEC = 0.7;

/**
 * THE SOFT SHARE — the largest fraction of a hold this app will spend
 * dissolving, and it is the roster's own worst case rather than a new number:
 * `ripple` holds 3.5 s and fades 0.7 s of it.
 *
 * The roster does not need it (every hold is long enough that 0.7 s is under
 * this), and THE PACE does not need it either — a pace scales the CLOCK, so
 * `fade / hold` is invariant by construction and the constant can stay a
 * constant. A schedule handed in from OUTSIDE the roster is the case that does:
 * `lib/beat.ts` snaps the hold to a musical multiple, and a 150 BPM track at one
 * bar is a 1.6 s hold, where a fixed 0.7 s dissolve is 44% of the take soft —
 * the exact smear `lib/pace.ts` proves the rejected design degenerates into.
 */
export const TURN_FADE_RATIO = 0.2;

/**
 * The dissolve for a hold that was not chosen by the roster. A ceiling, never a
 * floor: a LONG hold keeps the roster's own 0.7 s rather than growing a
 * two-second cross-fade nobody asked for.
 */
export const turnFadeFor = (holdSec: number): number =>
  !(holdSec > 0) || !Number.isFinite(holdSec)
    ? TURN_FADE_SEC
    : Math.min(TURN_FADE_SEC, holdSec * TURN_FADE_RATIO);

/**
 * A SCHEDULE HANDED IN FROM OUTSIDE THE ROSTER — today only `lib/beat.ts`.
 *
 * Three numbers rather than a rate, because the point of a beat sync is that
 * the cuts land at ABSOLUTE instants the music decides, and a rate cannot
 * express a phase: a track whose first downbeat is 310 ms in needs the whole
 * grid shifted, not scaled.
 */
export interface TurnSchedule {
  /** Seconds between cuts. */
  hold: number;
  /** When the FIRST cut lands, seconds into the take. */
  first: number;
  /** Seconds the cross-dissolve takes. */
  fade: number;
}

/** Sanity ceiling on the turn counter, so a runaway clock cannot ask
 *  `assignmentAt` to compose an unbounded number of steps. 4096 turns is over
 *  three hours at the fastest hold. */
export const MAX_TURN_INDEX = 4096;

interface TurnDef {
  id: TurnId;
  label: string;
  title: string;
  /** Seconds the wall holds between turns. */
  hold: number;
  /** Which step permutation this mode applies. */
  kind: 'still' | 'rotate' | 'ripple' | 'swap';
  /** `rotate` only: 0 means "derive a stride coprime to n from the seed". */
  step: number;
}

const DEFS: Record<TurnId, TurnDef> = {
  hold:    { id: 'hold',    label: 'HOLD',    title: 'One deal, held. The collage never re-cuts.',                   hold: 0,   kind: 'still',  step: 0 },
  march:   { id: 'march',   label: 'MARCH',   title: 'Every 5s the pictures step one fragment along.',                hold: 5.0, kind: 'rotate', step: 1 },
  scatter: { id: 'scatter', label: 'SCATTER', title: 'Every 6.5s the whole wall re-deals itself.',                    hold: 6.5, kind: 'rotate', step: 0 },
  ripple:  { id: 'ripple',  label: 'RIPPLE',  title: 'Every 3.5s half the wall turns and the rest holds.',            hold: 3.5, kind: 'ripple', step: 0 },
  swap:    { id: 'swap',    label: 'SWAP',    title: 'Every 4s neighbouring fragments trade pictures.',               hold: 4.0, kind: 'swap',   step: 0 },
};

/** The roster the chips render. Same list, same order, as `TURN_IDS`. */
export const TURNS: { id: TurnId; label: string; title: string }[] =
  TURN_IDS.map((id) => ({ id, label: DEFS[id].label, title: DEFS[id].title }));

/** What a caller draws right now: assignment `a` solid, assignment `b` over it
 *  at `mix`. `mix === 0` means `b` is not being drawn at all. */
export interface TurnFrame {
  /** Turn index of the outgoing assignment. */
  a: number;
  /** Turn index of the incoming assignment. Equals `a` when nothing is fading. */
  b: number;
  /** 0..1. Alpha the incoming assignment is drawn at. */
  mix: number;
}

/** REST, by reference — callers branch on identity, never on arithmetic that
 *  happens to be a no-op. */
export const NO_TURN: TurnFrame = Object.freeze({ a: 0, b: 0, mix: 0 });

const isTurnId = (id: unknown): id is TurnId =>
  typeof id === 'string' && Object.prototype.hasOwnProperty.call(DEFS, id);

/** Does this id change the picture over time? `hold`, junk and undefined: no. */
export const isTurning = (id: unknown): boolean => isTurnId(id) && DEFS[id].kind !== 'still';

/** Seconds between turns for a mode; 0 for anything that does not turn. */
export const turnHoldSec = (id: unknown): number => (isTurning(id) ? DEFS[id as TurnId].hold : 0);

/** The raised cosine. 0 at u=0, 1 at u=1, flat at both ends. */
const envelope = (u: number): number => 0.5 - 0.5 * Math.cos(Math.PI * u);

/**
 * WHERE THE TAKE IS IN ITS TURN SCHEDULE.
 *
 * Every rest case returns `NO_TURN` by reference: an unknown id, a `hold`, a
 * non-finite or negative time, and — the one that matters for the opening frame
 * — every instant before the first turn lands.
 *
 * `sched` is the beat sync's grid (`lib/beat.ts`) and is READ ON ITS OWN BRANCH
 * rather than folded into the roster path by defaulting `first` to `hold`. The
 * two expressions are algebraically the same and NUMERICALLY are not:
 * `floor((t - hold)/hold) + 1` and `floor(t/hold)` disagree on the boundary
 * cases where a double rounds the subtraction, and this function's whole
 * contract is that the roster path is the byte-identical thing it was before
 * the beat existed. The sweep asserts that against an oracle copy of it.
 */
export const turnAt = (id: unknown, timeSec: unknown, sched?: TurnSchedule | null): TurnFrame => {
  if (!isTurning(id)) return NO_TURN;
  if (sched) return scheduledTurnAt(sched, timeSec);
  const hold = DEFS[id as TurnId].hold;
  if (!(hold > 0)) return NO_TURN;
  const t = typeof timeSec === 'number' && Number.isFinite(timeSec) ? timeSec : 0;
  if (!(t > 0)) return NO_TURN;

  const k = Math.min(MAX_TURN_INDEX, Math.floor(t / hold));
  if (k <= 0) return NO_TURN;

  const elapsed = t - k * hold;
  // A clamped k (a runaway clock) has an elapsed that no longer means anything,
  // so it parks on the last assignment rather than fading forever.
  if (k >= MAX_TURN_INDEX || !(elapsed < TURN_FADE_SEC)) return { a: k, b: k, mix: 0 };
  return { a: k - 1, b: k, mix: envelope(Math.max(0, elapsed) / TURN_FADE_SEC) };
};

/**
 * THE SAME SCHEDULE, ON A GRID SOMEBODY ELSE OWNS.
 *
 * Turn k lands at `first + (k-1)*hold`, so turn 1 is at `first` — which
 * `beatSchedule` sets one hold past the phase, exactly where the roster path
 * puts its own first cut. Rest before that instant is `NO_TURN` BY REFERENCE,
 * so a synced collage still opens on the picture the still preview is showing
 * and the three surfaces that pass no time are untouched.
 *
 * A malformed schedule is REST, not an exception and not a fallback to the
 * mode's own hold: this is reached from `refreshTurn`, sixty times a second,
 * and a fallback would make a bad grid look like a working feature that is
 * simply ignoring the music.
 */
const scheduledTurnAt = (sched: TurnSchedule, timeSec: unknown): TurnFrame => {
  const { hold, first, fade } = sched;
  if (!(hold > 0) || !Number.isFinite(hold) || !Number.isFinite(first) || !(fade > 0)) return NO_TURN;
  const t = typeof timeSec === 'number' && Number.isFinite(timeSec) ? timeSec : 0;
  if (!(t >= first)) return NO_TURN;

  const rel = t - first;
  const raw = rel / hold;
  /**
   * AN INSTANT THAT IS A BOUNDARY MUST READ AS ONE.
   *
   * `(first + 3*hold - first) / hold` is 2.9999999999999996 for some grids and
   * 3.0000000000000004 for others — which way it rounds is a property of the
   * bits, not of the music. Left alone, the cut at that instant happens on the
   * path that rounds up and is one frame late on the path that rounds down, and
   * the two paths here are THE PREVIEW AND THE EXPORTED FILE: `renderAtTime`
   * walks a fixed frame grid that lands exactly on these instants far more
   * often than rAF does. This project has a name for that class of divergence
   * and a whole rung (ONE LAYOUT) about not shipping it.
   *
   * The roster branch above needs no such snap and does not get one: its
   * boundaries are `k * hold` read back through the same division, so the
   * expression is exact wherever the arithmetic is, and the sweep pins it
   * byte-for-byte against the build that had no schedules at all.
   */
  const snapped = Math.round(raw);
  const k = Math.min(MAX_TURN_INDEX, Math.floor(Math.abs(raw - snapped) < 1e-9 ? snapped : raw) + 1);
  if (k <= 0) return NO_TURN;

  const elapsed = Math.max(0, rel - (k - 1) * hold);
  if (k >= MAX_TURN_INDEX || !(elapsed < fade)) return { a: k, b: k, mix: 0 };
  return { a: k - 1, b: k, mix: envelope(Math.max(0, elapsed) / fade) };
};

/** Deterministic 32-bit scramble of the seed, so `scatter`'s stride does not
 *  track the seed's low bits. */
const hash32 = (seed: number): number => {
  let h = (Number.isFinite(seed) ? Math.floor(seed) : 0) | 0;
  h = Math.imul(h ^ (h >>> 16), 2246822507);
  h = Math.imul(h ^ (h >>> 13), 3266489909);
  return (h ^ (h >>> 16)) >>> 0;
};

const gcd = (a: number, b: number): number => {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y) { const t = x % y; x = y; y = t; }
  return x;
};

/**
 * SCATTER'S STRIDE — a step coprime to `n`, so one picture's orbit visits every
 * fragment instead of circling a short sub-cycle. Coprimality is not needed for
 * the permutation property (any fixed shift is a permutation); it is what makes
 * `scatter` read as a re-deal rather than as several small carousels.
 */
export const scatterStride = (n: number, seed: number): number => {
  if (!(n > 2)) return 1;
  const start = 1 + (hash32(seed) % (n - 1));
  for (let d = 0; d < n; d++) {
    const s = 1 + ((start - 1 + d) % (n - 1));
    if (gcd(s, n) === 1) return s;
  }
  return 1;
};

/**
 * THE STEP PERMUTATION applied AT turn `k`, written into `out`.
 *
 * `out[j]` is the position whose picture MOVES INTO position `j` at this step.
 * Every branch writes a genuine permutation of [0, n) — that is the property
 * `assignmentAt` inducts on and the sweep asserts directly.
 */
const stepPerm = (id: TurnId, k: number, n: number, seed: number, out: Int32Array): void => {
  for (let j = 0; j < n; j++) out[j] = j;
  if (n < 2) return;
  const def = DEFS[id];

  if (def.kind === 'rotate') {
    const s = def.step > 0 ? def.step % n : scatterStride(n, seed);
    for (let j = 0; j < n; j++) out[j] = (j + s) % n;
    return;
  }

  if (def.kind === 'ripple') {
    // HALF THE WALL, ROTATED AMONG ITSELF. The parity alternates with k, so
    // consecutive turns move disjoint halves and the picture never goes fully
    // soft at once. A subset rotation is a permutation on the nose, which is
    // how this mode gets its stagger without the injectivity failure a shifted
    // global rotation runs into (see the header).
    const parity = ((k % 2) + 2) % 2;
    let count = 0;
    for (let j = 0; j < n; j++) if (j % 2 === parity) count++;
    // A HALF OF ONE CANNOT ROTATE, and a chip that does nothing is a lie about
    // what the roster offers. Below n=4 the parity halves degenerate (n=2 gives
    // {0} and {1}; n=3 gives {1} alone on odd turns), so those turns fall back
    // to the full rotation — still a permutation, and still a turn.
    if (count < 2) {
      for (let j = 0; j < n; j++) out[j] = (j + 1) % n;
      return;
    }
    // Walk the subset in order; each member takes the NEXT member's picture.
    let firstIdx = -1;
    let prevIdx = -1;
    for (let j = 0; j < n; j++) {
      if (j % 2 !== parity) continue;
      if (firstIdx < 0) firstIdx = j;
      else out[prevIdx] = j;
      prevIdx = j;
    }
    if (prevIdx >= 0 && firstIdx >= 0) out[prevIdx] = firstIdx;
    return;
  }

  // SWAP — disjoint transpositions of neighbours, offset by k so a pair that
  // traded last time holds while its other neighbour trades now. A trailing
  // unpaired position is a fixed point, which keeps it a permutation for odd n.
  const off = ((k % 2) + 2) % 2;
  for (let j = off; j + 1 < n; j += 2) {
    out[j] = j + 1;
    out[j + 1] = j;
  }
};

const identity = (n: number): Int32Array => {
  const a = new Int32Array(Math.max(0, n));
  for (let j = 0; j < a.length; j++) a[j] = j;
  return a;
};

/**
 * WHICH PICTURE EACH POSITION HOLDS AT TURN `k`.
 *
 * `assignmentAt(...)[j] === p` reads "position j shows the picture that BELONGS
 * to position p in the base deal". `k <= 0` is the identity, which is what
 * makes turn 0 the deal the still preview, the raster export and the SVG all
 * draw.
 *
 * Composed rather than closed-form because `ripple` and `swap` are not shifts,
 * and one composition loop that every mode goes through is one thing to get
 * right instead of four. It runs at a turn BOUNDARY, never per frame.
 */
export const assignmentAt = (id: unknown, k: unknown, n: unknown, seed: unknown): Int32Array => {
  const len = typeof n === 'number' && Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
  if (!isTurning(id) || len < 2) return identity(len);
  const turns = typeof k === 'number' && Number.isFinite(k)
    ? Math.min(MAX_TURN_INDEX, Math.max(0, Math.floor(k)))
    : 0;
  if (turns <= 0) return identity(len);
  const sd = typeof seed === 'number' && Number.isFinite(seed) ? seed : 0;

  let cur = identity(len);
  const next = new Int32Array(len);
  const step = new Int32Array(len);
  for (let t = 1; t <= turns; t++) {
    stepPerm(id as TurnId, t, len, sd, step);
    // cur' = cur ∘ step: position j takes step[j]'s picture, and step[j] was
    // already holding cur[step[j]].
    for (let j = 0; j < len; j++) next[j] = cur[step[j]];
    cur.set(next);
  }
  return cur;
};
