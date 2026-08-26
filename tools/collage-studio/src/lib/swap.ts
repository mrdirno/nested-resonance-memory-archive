// src/lib/swap.ts
// -----------------------------------------------------------------------------
// THE SWAP — two fragments trade pictures, and the one copy of the rule that
// makes the trade SURVIVE the next deal.
//
// WHY THIS FILE EXISTS
//   Every composition control in this app is GENERATIVE. The dice roll, the
//   arrangement ranks, the bag is dealt by seed. That is the whole point and it
//   is also the whole gap: after twenty rolls the wall is right except for two
//   fragments, and there has never been a way to say *"no — that one goes
//   THERE."* The ladder has named it since the timeline rung was opened
//   ("drag-reorder … direct manipulation of the SOURCES rather than of the
//   clock"), and a collage has no timeline to drag along — the sources sit in
//   fragments, so reordering them IS trading two fragments' pictures.
//
//   The fragment already has two verbs on the armed puck — PIN ("keep this
//   one") and REMOVE ("lose this one"). This is the missing third: MOVE.
//
// DECISION 1 — A SWAP IS A TRANSPOSITION OF THE ASSIGNMENT, NOT OF THE LAYOUT.
//   `shuffledIndices` maps slot -> pool index and is the single seam every
//   render path already reads (`orderedAssets` -> preview, Stage, video export,
//   raster export, SVG). Transposing two of its entries therefore reaches all
//   five for free, and — because a transposition is a permutation — the
//   multiset of placed pictures is bit-identical, so `assignSources`'
//   duplicate-free guarantee survives untouched. Nothing about the PARTITION
//   moves: the fragment keeps its shape, its focus, its twist and its lean,
//   because those are properties of the fragment and not of the photograph
//   (the same split `turnResolve` already makes).
//
// DECISION 2 — AND IT MUST PIN BOTH CELLS, OR IT IS A LIE WITH A SHELF LIFE.
//   This is the load-bearing half and it was not obvious. `shuffledIndices` is
//   DERIVED: an effect recomputes it from (images, count, layoutItems, aspect,
//   seed, shuffleTrigger, arrangement), and `layoutItems` alone re-runs on a
//   gutter nudge, an entropy nudge, a mode change, an aspect change. So a swap
//   written only into the indices would be silently undone by the next touch of
//   any of nine controls — and WORSE than undone: the assignment pass honours
//   `lockedCells` FIRST, so a pin already sitting on one of the two cells would
//   drag its old picture back and leave the other half of the trade standing.
//   Half a swap is a duplicate on screen.
//
//   The only state the re-deal honours is the pin table, and it is exactly the
//   right shape — `Map<cell, assetId>`, "this fragment keeps this picture".
//   So the plan rewrites BOTH cells' pins to the pictures they now hold. The
//   consequence is deliberate and is disclosed by machinery that already
//   exists: both fragments come back wearing the yellow pin badge, and the
//   pin button un-does it. `describeSwap` says so out loud the first time.
//
// DECISION 3 — IT PLANS, IT DOES NOT ACT (the shape `lib/evict.ts` settled).
//   A swap touches two pieces of live state that must move together or not at
//   all. Computing WHICH here, as data, swept over thousands of adversarial
//   assignments, is what stops the rule being spelled a second time at the call
//   site and drifting from the rule the tests measure — the bug this repo has
//   already written down three times (`lib/level.ts` I5, `lib/intake.ts`,
//   `lib/evict.ts`).
//
// DECISION 4 — AN EMPTY FRAGMENT IS NOT A DESTINATION.
//   `shuffledIndices` legitimately carries `-1` and `undefined` (the fill bag
//   is shorter than the partition, or a re-layout is mid-flight). Trading with
//   one would move a picture OUT of a fragment that renders and INTO one that
//   may not — leaving a black hole where a photograph was. Refused, and SAID:
//   a control that silently does nothing is the inert-control defect this repo
//   has already been filed for.
//
// DECISION 5 — IT IS TOTAL. Nonsense slots, a null pool, holes, duplicate ids,
//   a malformed pin table: every one returns a refusal rather than throwing. A
//   click handler on a canvas is the last place allowed to take the app down,
//   and a stale cell index is precisely the input that arrives during a
//   re-layout.
//
// DECISION 6 — A CARRIED PIN MUST SURVIVE `new Map()`, and this one was found by
//   the sweep rather than reasoned out. The caller's very next line is
//   `setLockedCells(new Map(plan.locks))`, and that constructor is not total:
//   `new Map([null])` THROWS, and `new Map(['ab'])` silently yields
//   `{'a' => 'b'}` — a pin invented out of a string. So a non-array entry is
//   dropped rather than carried through verbatim. Nothing is lost by it: the
//   assignment pass reads pins as `cellIdx < slotCount` and
//   `imageIdToIndex.get(imgId)`, so a malformed entry is ALREADY inert there.
//   Dropping an inert entry that would otherwise take the app down at the call
//   site is strictly better than honouring the word "verbatim".
// -----------------------------------------------------------------------------

/** The two fields a swap reads off a pool asset, plus the two it may name it by. */
export interface SwappableAsset {
  id: string;
  /** Filename of the clip a video frame came from. */
  sourceName?: string;
  /** Filename of the picture itself. */
  originalName?: string;
}

/** A pin, in the entry form `Array.from(lockedCells.entries())` already produces. */
export type LockEntry = readonly [number, string];

export type SwapRefusal =
  | 'ok'
  /** Both taps landed on the same fragment — the UI treats this as cancel. */
  | 'same-cell'
  /** A slot index that is not a position in this assignment (stale arming). */
  | 'out-of-range'
  /** One of the two fragments is holding nothing (DECISION 4). */
  | 'empty-cell'
  /** Both fragments are showing the SAME pool entry — the trade is a no-op. */
  | 'same-picture';

export interface SwapPlan {
  ok: boolean;
  why: SwapRefusal;
  /** The lower slot index, so a plan does not depend on which was tapped first. */
  a: number;
  /** The higher slot index. */
  b: number;
  /**
   * The WHOLE new assignment, ready for `setShuffledIndices`. On a refusal this
   * is a copy of the input, so a caller that applies it anyway changes nothing.
   */
  indices: number[];
  /**
   * The WHOLE new pin table, ready for `new Map(plan.locks)` — and every entry
   * is an ARRAY, so that constructor can neither throw nor invent a pin out of
   * a string (DECISION 6). Well-formed entries for cells other than `a` and `b`
   * are carried through verbatim and in order; the two rewritten pins are
   * appended LAST so they win a hand-built table that names the same cell twice.
   */
  locks: LockEntry[];
  /** What the picture now leaving `a` is called. `''` when the pool has no name. */
  labelA: string;
  /** What the picture now leaving `b` is called. */
  labelB: string;
  /** True when neither cell carried a pin before — the first time it surprises. */
  pinned: boolean;
}

const nameOf = (a: SwappableAsset | undefined): string =>
  (a && (a.originalName || a.sourceName)) || '';

/** A slot index is a position in THIS assignment, and nothing else. */
const isSlot = (v: unknown, len: number): v is number =>
  typeof v === 'number' && Number.isInteger(v) && v >= 0 && v < len;

/** Reading a pool index out of an assignment: `-1`, `undefined` and junk all mean "empty". */
const assetAt = (
  images: readonly SwappableAsset[],
  indices: readonly number[],
  slot: number,
): { i: number; asset: SwappableAsset } | null => {
  const i = indices[slot];
  if (typeof i !== 'number' || !Number.isInteger(i) || i < 0 || i >= images.length) return null;
  const asset = images[i];
  if (!asset || typeof asset.id !== 'string' || asset.id.length === 0) return null;
  return { i, asset };
};

/**
 * The only entries `new Map()` reads as a PAIR. `null` throws there and a bare
 * string is split into a key and a value, so both are dropped (DECISION 6).
 */
const isEntry = (e: unknown): e is LockEntry => Array.isArray(e);

/** Every pin table this module hands back has been through here. */
const cleanLocks = (locks: unknown): LockEntry[] =>
  (Array.isArray(locks) ? locks : []).filter(isEntry);

const refuse = (
  why: SwapRefusal,
  indices: readonly number[],
  locks: readonly LockEntry[],
  a: number,
  b: number,
): SwapPlan => ({
  ok: false,
  why,
  a: Math.min(a, b),
  b: Math.max(a, b),
  indices: Array.isArray(indices) ? [...indices] : [],
  locks: cleanLocks(locks),
  labelA: '',
  labelB: '',
  pinned: false,
});

/**
 * WHAT MOVES when two fragments trade pictures.
 *
 * Pure and total. `a` and `b` are slot indices into `indices` — the same
 * `shuffledIndices` the click handler reads, which is allowed to be stale,
 * short, or holding `-1`.
 *
 * The caller applies the result exactly once:
 *
 *   setShuffledIndices(plan.indices);
 *   setLockedCells(new Map(plan.locks));
 */
export const planSwap = (
  images: readonly SwappableAsset[] | null | undefined,
  indices: readonly number[] | null | undefined,
  locks: readonly LockEntry[] | null | undefined,
  a: number,
  b: number,
): SwapPlan => {
  const pool: readonly SwappableAsset[] = Array.isArray(images) ? images : [];
  const idx: readonly number[] = Array.isArray(indices) ? indices : [];
  const pins: readonly LockEntry[] = Array.isArray(locks) ? locks : [];

  if (!isSlot(a, idx.length) || !isSlot(b, idx.length)) return refuse('out-of-range', idx, pins, a, b);
  // Order-independence is settled HERE, once, so every field below — including
  // the order of the two appended pins — is the same whichever way round the
  // two fragments were tapped.
  const lo = Math.min(a, b);
  const hi = Math.max(a, b);
  if (lo === hi) return refuse('same-cell', idx, pins, lo, hi);

  const A = assetAt(pool, idx, lo);
  const B = assetAt(pool, idx, hi);
  if (!A || !B) return refuse('empty-cell', idx, pins, lo, hi);
  // The SAME pool entry in both fragments is a genuine no-op: focus and twist
  // are keyed on the SLOT and stay put, so nothing on screen would move. Saying
  // so beats reporting a swap that did not happen.
  if (A.i === B.i) return refuse('same-picture', idx, pins, lo, hi);

  const next = [...idx];
  next[lo] = B.i;
  next[hi] = A.i;

  // DECISION 2. Every other pin is carried through untouched and in order; the
  // two cells in the trade are re-pinned to what they now hold, which is the
  // exact invariant the assignment pass reads back (`newIndices[cell] =
  // imageIdToIndex.get(imgId)`).
  const carried = cleanLocks(pins).filter((e) => e[0] !== lo && e[0] !== hi);
  const wasPinned = cleanLocks(pins).some((e) => e[0] === lo || e[0] === hi);

  return {
    ok: true,
    why: 'ok',
    a: lo,
    b: hi,
    indices: next,
    locks: [...carried, [lo, B.asset.id] as LockEntry, [hi, A.asset.id] as LockEntry],
    labelA: nameOf(A.asset),
    labelB: nameOf(B.asset),
    pinned: !wasPinned,
  };
};

/**
 * THE NOTICE, in one place so the wording cannot drift between the call sites
 * this will have.
 *
 * It names both files, because a trade you cannot identify is indistinguishable
 * from a re-roll — and on the trade that pins for the first time it says so,
 * because two new pin badges appearing is the one thing here that will surprise
 * someone (DECISION 2).
 */
export const describeSwap = (plan: SwapPlan): string => {
  if (!plan.ok) {
    if (plan.why === 'same-picture') return 'Those two fragments are showing the same picture.';
    if (plan.why === 'empty-cell') return 'That fragment is empty — nothing to trade.';
    // `same-cell` is the UI's cancel gesture and `out-of-range` only arrives
    // from an assignment that has already been replaced. Both are silence.
    return '';
  }
  const A = plan.labelA || 'that picture';
  const B = plan.labelB || 'that picture';
  const both = plan.labelA && plan.labelB && plan.labelA !== plan.labelB
    ? `Swapped ${A} and ${B}.`
    : 'Swapped those two fragments.';
  return plan.pinned ? `${both} Both are pinned now, so a remix keeps them.` : both;
};

/**
 * IS THERE ANYBODY TO TRADE WITH — the one copy of the rule the Swap BUTTON
 * needs, asked of the same function that performs the trade.
 *
 * A collage of one fragment has no partner, and neither does one where every
 * other fragment is empty or is showing the same pool entry. Offering Swap
 * there would be the inert-control defect this repo has already been filed for
 * — and answering it with a hand-written scan at the call site is the OTHER
 * defect this repo has already been filed for three times (a rule spelled twice
 * drifts from the rule the tests measure). So it asks `planSwap`.
 *
 * Cheap where it is used: it runs only while a fragment is armed, over a
 * partition of at most a few hundred cells, and stops at the first partner.
 */
export const canSwapFrom = (
  images: readonly SwappableAsset[] | null | undefined,
  indices: readonly number[] | null | undefined,
  slot: number,
): boolean => {
  const idx: readonly number[] = Array.isArray(indices) ? indices : [];
  for (let j = 0; j < idx.length; j++) {
    if (j === slot) continue;
    if (planSwap(images, idx, [], slot, j).ok) return true;
  }
  return false;
};
