// src/lib/evict.ts
// -----------------------------------------------------------------------------
// WHAT LEAVES THE POOL WHEN YOU THROW ONE FRAGMENT OUT — the one copy of that rule.
//
// WHY THIS FILE EXISTS
//   From the field: *"when full mode is active if I click a box or segment there
//   should be ability to remove that from the group of images displayed or
//   videos."*
//
//   You maximize to COMPARE — that is what the whole full-bleed rail is for, and
//   two wishes have already landed on it (the colour dice, then Undo). But
//   comparing is how you find the one photograph that is wrecking every roll,
//   and at that moment the only way to get rid of it was to leave full bleed,
//   Clear the whole pool, and import everything again minus one. The app had a
//   button for throwing away EVERYTHING and no button for throwing away ONE.
//
// DECISION 1 — A SOURCE LEAVES, NOT A TILE.
//   `assignSources` (lib/fill.ts) already states this app's definition: *"a video
//   is one source however many frames were extracted from it"*. The person
//   pointing at a fragment of a clip is pointing at THE CLIP — "remove that …
//   or videos", in their words. Evicting only the poster they happened to tap
//   would leave the same clip's other frames in the pool, and the next roll
//   would put the thing they just deleted straight back on screen wearing a
//   different second. So the unit of eviction is the SOURCE: every asset
//   carrying the target's `clipId` leaves together, and the live clip goes with
//   them.
//
// DECISION 2 — AN EMPTY `clipId` IS ABSENT, NOT A GROUP.
//   `removeClip` writes `clipId: undefined` when a clip is dropped back to
//   stills, but a manifest round-trip and a hand-written project can both hand
//   back `''`. Grouping on a falsy key would make every plain photograph in the
//   pool a frame of one enormous shared "video", and tapping one would delete
//   the lot. The key must be a NON-EMPTY string to group anything, and this is
//   swept rather than asserted in prose (I11).
//
// DECISION 3 — IT PLANS, IT DOES NOT ACT.
//   Removing a source touches four pieces of live state (the pool, the clips,
//   the object URLs those clips hold, and any lock pinned to a departing id) and
//   one of them is not reversible: `URL.revokeObjectURL` cannot be taken back.
//   So the decision — WHICH ids leave — is computed here as data, swept over
//   thousands of adversarial pools, and the caller performs it exactly once.
//   The bug this shape forecloses is the one this repo has already written down
//   twice: a rule spelled a second time at the call site drifts from the rule
//   the tests measure (`lib/level.ts` I5, `lib/intake.ts`).
//
// DECISION 4 — IT IS TOTAL. An id that is not in the pool, a pool with duplicate
//   ids, an asset with no fields at all: every one of those returns an EMPTY
//   plan rather than throwing. A click handler on a canvas is the last place
//   that should be able to take the app down, and the cell under a stale
//   `shuffledIndices` entry is exactly the input that arrives during a re-layout.
// -----------------------------------------------------------------------------

/** The two fields eviction reads off a pool asset, plus the two it may name it by. */
export interface EvictableAsset {
  id: string;
  clipId?: string;
  /** Filename of the clip a video frame came from. */
  sourceName?: string;
  /** Filename of the picture itself. */
  originalName?: string;
}

/** The live clip is only ever asked for its id here; the caller owns its url. */
export interface EvictableClip {
  id: string;
}

export interface EvictionPlan {
  /** Pool asset ids that leave. Empty means "nothing to do", never "everything". */
  imageIds: string[];
  /** Live clips to stop and free. Always a subset of the clips handed in. */
  clipIds: string[];
  /** How many pool tiles leave — what the notice counts. */
  count: number;
  /** True when a whole video is going, so the caller can say so. */
  isClip: boolean;
  /** What to call it out loud. `''` when the pool never recorded a name. */
  label: string;
}

const EMPTY: EvictionPlan = { imageIds: [], clipIds: [], count: 0, isClip: false, label: '' };

/** A clip id groups only when it is a real, non-empty string (DECISION 2). */
const groupKey = (a: EvictableAsset | undefined): string =>
  typeof a?.clipId === 'string' && a.clipId.length > 0 ? a.clipId : '';

/**
 * WHICH IDS LEAVE when the person throws out the source sitting in one fragment.
 *
 * Pure and total. `targetId` is the id of the asset the tapped cell is holding —
 * `images[shuffledIndices[cell]].id` at the call site, which is allowed to be
 * stale, missing or nonsense.
 */
export const planEviction = (
  images: readonly EvictableAsset[],
  clips: readonly EvictableClip[],
  targetId: string | undefined | null,
): EvictionPlan => {
  if (!targetId) return { ...EMPTY };
  const pool = Array.isArray(images) ? images : [];
  const target = pool.find((a) => a && a.id === targetId);
  if (!target) return { ...EMPTY };

  const key = groupKey(target);

  // A PLAIN PHOTOGRAPH IS ITSELF AND NOTHING ELSE. Two assets can legitimately
  // share a filename (the same photo picked from two folders), so the identity
  // that decides this is the id, never the name.
  if (!key) {
    return {
      imageIds: [target.id],
      clipIds: [],
      count: 1,
      isClip: false,
      label: target.originalName || target.sourceName || '',
    };
  }

  // A FRAME OF A CLIP TAKES THE CLIP WITH IT (DECISION 1). Deduped by id: a pool
  // that somehow carries the same asset twice must not ask the caller to revoke
  // and drop it twice.
  const seen = new Set<string>();
  const imageIds: string[] = [];
  for (const a of pool) {
    if (!a || groupKey(a) !== key) continue;
    if (seen.has(a.id)) continue;
    seen.add(a.id);
    imageIds.push(a.id);
  }

  // The live clip may already be gone — `removeClip` cuts the binding and leaves
  // the stills, and the frames of a clip dropped that way still carry the id.
  // An orphaned poster is still evictable; there is simply nothing to revoke.
  const live = (Array.isArray(clips) ? clips : []).some((c) => c && c.id === key);

  return {
    imageIds,
    clipIds: live ? [key] : [],
    count: imageIds.length,
    isClip: true,
    label: target.sourceName || target.originalName || '',
  };
};

/**
 * THE NOTICE, in one place so the wording cannot drift between the two call
 * sites this will have (a tapped fragment, and — one day — a pool manager).
 *
 * It names the file because a removal you cannot identify is indistinguishable
 * from a bug, and it says how many tiles went when a clip took several with it,
 * because THAT is the number that will surprise someone.
 */
export const describeEviction = (plan: EvictionPlan): string => {
  if (plan.count <= 0) return '';
  const what = plan.label || (plan.isClip ? 'that clip' : 'that picture');
  if (plan.isClip && plan.count > 1) return `Removed ${what} — ${plan.count} frames.`;
  return `Removed ${what}.`;
};
