import type { ImageAsset } from '../types';

/**
 * THE SOURCE IS THE UNIT — not the asset.
 *
 * A photograph is one source. A video is ALSO one source, however many stills
 * were extracted from it: every extracted frame carries the same `clipId`, and
 * the live compositor binds ONE decoder per clip, so a dozen frames of one clip
 * are a dozen views of a SINGLE thing to look at. Counting, filling and the
 * "no duplicates" rule therefore all reckon in sources, never in raw assets —
 * which is what stops one imported video from multiplying into a field of
 * look-alike fragments and crowding the photographs off the canvas.
 *
 * This is the ONE definition of "same source" in the app; both the fragment
 * count on import and the slot assignment below read it, so the two can never
 * drift apart (the classic two-guards-different-units bug).
 */
export const sourceKeyOf = (a: ImageAsset | undefined, i: number): string => {
  if (!a) return `#${i}`;
  // `clipId` is the live-binding key, so it is the truest "same video".
  // `sourceName` covers frames minted before clipId existed, and frames whose
  // clip was dropped back to stills (removeClip clears clipId but keeps the
  // name), so those still collapse to one source. Anything else is its own
  // source: one photograph, one voice.
  if (a.clipId) return `clip:${a.clipId}`;
  if (a.sourceKind === 'video' && a.sourceName) return `name:${a.sourceName}`;
  return `img:${a.id}`;
};

/**
 * How many distinct photos/videos are in the pool — the number the user thinks
 * of as "what I uploaded", and the fragment count a fresh import snaps to.
 */
export const distinctSourceCount = (images: ImageAsset[]): number => {
  const keys = new Set<string>();
  for (let i = 0; i < images.length; i++) keys.add(sourceKeyOf(images[i], i));
  return keys.size;
};

/** Group asset indices by source, preserving pool order within each source. */
export const groupBySource = (images: ImageAsset[]): Map<string, number[]> => {
  const groups = new Map<string, number[]>();
  for (let i = 0; i < images.length; i++) {
    const k = sourceKeyOf(images[i], i);
    const arr = groups.get(k);
    if (arr) arr.push(i);
    else groups.set(k, [i]);
  }
  return groups;
};

export interface AssignOptions {
  /** How many fill positions need an asset. */
  slotCount: number;
  /** The whole pool. Indices returned are indices INTO this array. */
  images: ImageAsset[];
  /**
   * Asset indices already committed to the layout (locked cells). They are not
   * placed again, and — the point — the source each belongs to counts as already
   * on screen, so an unshown source is preferred over repeating a locked one.
   */
  used?: Set<number>;
  /** Deterministic PRNG; the same seed reproduces the same arrangement. */
  rng: () => number;
}

const makeShuffle = (rng: () => number) => <T,>(arr: T[]): T[] => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

/**
 * Assign an asset index to each of `slotCount` fill positions — SOURCE-FIRST and
 * DUPLICATE-FREE until the distinct sources are genuinely exhausted.
 *
 * The mechanism is a balanced round-robin over sources: at every step the source
 * that has appeared the FEWEST times so far (counting locked appearances) takes
 * the next slot, ties broken by a fresh shuffle, and each appearance hands back
 * an UNSEEN moment of that source before it ever reuses one. The consequences
 * are the whole specification, and each is exactly what the operator asked for:
 *
 *   - slotCount === sources           -> every source once, ZERO duplicates.
 *   - slotCount  <  sources           -> a shuffled subset, each once, ZERO dupes.
 *   - slotCount  >  sources           -> appearances balanced to within one, and
 *                                        every repeat is a DIFFERENT moment first.
 *
 * A video is one source, so at the default count (= number of uploads) it takes
 * exactly one slot, and the fragment holding it carries a `clipId` and plays the
 * live clip. Repetition is what happens only when you have run out of material —
 * never a way to reach a fragment count, and never before the pool is spent.
 *
 * Returns exactly `slotCount` indices (padded with 0 only if the pool is empty,
 * so a caller can never read `undefined` out of it).
 */
export const assignSources = ({ slotCount, images, used, rng }: AssignOptions): number[] => {
  const bag: number[] = [];
  if (slotCount <= 0) return bag;

  const shuffle = makeShuffle(rng);
  const usedSet = used ?? new Set<number>();
  const groups = groupBySource(images);

  const sources = [...groups.keys()]
    .map((k) => {
      const own = groups.get(k) as number[];
      return {
        // Never-placed moments, spent before anything repeats.
        fresh: shuffle(own.filter((i) => !usedSet.has(i))),
        // Every moment, walked by a cursor once fresh is gone.
        all: shuffle([...own]),
        cursor: 0,
        // Seed appearances from the locked cells so a source already on screen
        // starts "ahead" and is skipped until the others catch up.
        shown: own.reduce((n, i) => n + (usedSet.has(i) ? 1 : 0), 0),
      };
    })
    .filter((s) => s.all.length > 0);

  if (sources.length === 0) {
    // No usable assets at all — pad rather than spin forever. `renderCanvas`
    // and `setScene` both tolerate a repeated index; a hang they do not.
    while (bag.length < slotCount) bag.push(0);
    return bag;
  }

  const draw = (s: (typeof sources)[number]): number => {
    s.shown++;
    if (s.fresh.length) return s.fresh.shift() as number;
    const idx = s.all[s.cursor % s.all.length];
    s.cursor++;
    return idx;
  };

  while (bag.length < slotCount) {
    // The frontier: every source tied for the fewest appearances so far. Giving
    // a slot to anything outside it would repeat a source before another had its
    // first turn — the duplicate the whole routine exists to prevent.
    let min = Infinity;
    for (const s of sources) if (s.shown < min) min = s.shown;
    const frontier = shuffle(sources.filter((s) => s.shown === min));
    for (const s of frontier) {
      if (bag.length >= slotCount) break;
      bag.push(draw(s));
    }
  }
  return bag;
};
