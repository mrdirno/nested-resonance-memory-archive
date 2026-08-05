// src/lib/composition.ts
// -----------------------------------------------------------------------------
// COMPOSITION — WHICH PHOTO GOES IN WHICH FRAGMENT, AND WHAT IT CENTRES ON.
//
// The layout decides the SHAPES. The fill decides WHICH photos get used (source
// -first, duplicate-free — see fill.ts). This module decides the last two things,
// and they are the two that actually make a collage read as composed rather than
// dealt:
//
//   ARRANGEMENT — the pairing of a photo ORDER against a cell ORDER. Not a sort.
//     A plain `bag.sort(byHue)` throws away half the information, because the
//     cells are not a list — they have positions, angles and areas. Ranking the
//     photos by a metric and the cells by a SPATIAL key, then zipping the two,
//     is what turns "sorted by colour" into "the colour wheel wrapped around the
//     canvas" or "the strongest photo in the biggest fragment".
//
//   FOCUS — where inside each photo the crop centres. The crop is a `cover` fit,
//     so most of a photo is thrown away in a small fragment; WHICH part survives
//     is a compositional choice, and until now it was one fixed rule (the face,
//     else the energy centroid). It is per-SLOT, not per-photo, which is the
//     point: the same photo landing in three fragments can show three different
//     parts of itself instead of the same crop three times.
//
// EVERYTHING HERE IS PURE AND DETERMINISTIC. No canvas, no DOM, no clock, no
// stateful rng — `wander` derives its offset by hashing the slot index, so the
// result depends only on (seed, slot) and never on the order calls were made in.
// That is what makes a shared roll reproduce EXACTLY on someone else's phone.
//
// The invariant everything else depends on: an arrangement is a PERMUTATION.
// The same multiset of photos comes out that went in — never one dropped, never
// one duplicated. `tests/unit/composition.invariants.mjs` sweeps it.
// -----------------------------------------------------------------------------

// =============================================================================
// SHAPE
// =============================================================================

/** The only thing this module needs to know about a photo. */
export interface PhotoLike {
  analysis?: {
    face?: { x: number; y: number } | null;
    energy?: { x: number; y: number } | null;
    color?: { r: number; g: number; b: number; h: number; s: number; l: number } | null;
  } | null;
}

/** The only thing this module needs to know about a fragment — normalised 0..1. */
export interface CellGeom {
  /** Centroid x, as a fraction of canvas width. */
  cx: number;
  /** Centroid y, as a fraction of canvas height. */
  cy: number;
  /** Bounding-box area, as a fraction of canvas area. */
  area: number;
}

export type ArrangementId =
  | 'natural' | 'flow' | 'wheel' | 'spotlight' | 'eclipse' | 'horizon'
  | 'heat' | 'vivid' | 'hero' | 'checker' | 'drift';

export type FocusId = 'auto' | 'energy' | 'centre' | 'thirds' | 'wander';

type Metric = 'hue' | 'lum' | 'chroma' | 'warm' | 'punch';
type CellKey = 'reading' | 'serpentine' | 'radial' | 'angular' | 'size' | 'x' | 'y' | 'checker' | 'spiral';

export interface ArrangementSpec {
  id: ArrangementId;
  label: string;
  blurb: string;
  /** How the photos are ranked. Absent = keep the fill order untouched. */
  metric?: Metric;
  /** How the fragments are ranked. */
  cell?: CellKey;
  /** Rank the photos high-to-low instead of low-to-high. */
  flip?: boolean;
}

// =============================================================================
// THE ROSTER
// =============================================================================

/**
 * Eleven ways to lay the same photos into the same fragments.
 *
 * `natural` is first and is the default on purpose: the source-first fill is
 * already a considered order (every distinct upload once, before any repeat),
 * and an arrangement necessarily re-clumps a video's frames because they share a
 * palette. Choosing one is a deliberate act, not the price of using the app.
 */
export const ARRANGEMENTS: ArrangementSpec[] = [
  { id: 'natural',   label: 'Natural',   blurb: 'As uploaded — every photo once before any repeat.' },
  { id: 'flow',      label: 'Colour flow', metric: 'hue',    cell: 'serpentine', blurb: 'Hue runs across the frame and back, row by row, with no jump at the turn.' },
  { id: 'wheel',     label: 'Colour wheel', metric: 'hue',   cell: 'angular',    blurb: 'The colour wheel, wrapped around the centre of the canvas.' },
  { id: 'spotlight', label: 'Spotlight', metric: 'lum',      cell: 'radial', flip: true, blurb: 'Brightest photos at the centre, falling away into the dark.' },
  { id: 'eclipse',   label: 'Eclipse',   metric: 'lum',      cell: 'radial',     blurb: 'Dark core, bright rim — the spotlight inverted.' },
  { id: 'horizon',   label: 'Horizon',   metric: 'lum',      cell: 'y',   flip: true, blurb: 'Light at the top, dark at the bottom. A landscape out of anything.' },
  { id: 'heat',      label: 'Heat',      metric: 'warm',     cell: 'x',          blurb: 'Cool on one side, warm on the other.' },
  { id: 'vivid',     label: 'Vivid core', metric: 'chroma',  cell: 'radial', flip: true, blurb: 'Saturated colour at the centre, greys pushed to the edges.' },
  { id: 'hero',      label: 'Hero',      metric: 'punch',    cell: 'size', flip: true, blurb: 'The strongest photo gets the biggest fragment.' },
  { id: 'checker',   label: 'Checker',   metric: 'lum',      cell: 'checker',    blurb: 'Light, dark, light, dark — maximum contrast between neighbours.' },
  { id: 'drift',     label: 'Drift',     metric: 'hue',      cell: 'spiral',     blurb: 'Colour spiralling out from the middle.' },
];

export const ARRANGEMENT_BY_ID: Record<string, ArrangementSpec> =
  Object.fromEntries(ARRANGEMENTS.map((a) => [a.id, a]));

/** Stable order — the share code stores an INDEX into this, so only append. */
export const ARRANGEMENT_IDS: ArrangementId[] = ARRANGEMENTS.map((a) => a.id);

export interface FocusSpec {
  id: FocusId;
  label: string;
  blurb: string;
}

export const FOCUS_MODES: FocusSpec[] = [
  { id: 'auto',   label: 'Auto',   blurb: 'The face if there is one, otherwise the busiest part of the picture.' },
  { id: 'energy', label: 'Detail', blurb: 'Always the busiest part — ignores faces.' },
  { id: 'centre', label: 'Centre', blurb: 'Dead centre of every photo. Predictable, and sometimes that is the point.' },
  { id: 'thirds', label: 'Thirds', blurb: 'Snaps the subject onto a rule-of-thirds line.' },
  { id: 'wander', label: 'Wander', blurb: 'A different part of the picture in every fragment it lands in.' },
];

export const FOCUS_BY_ID: Record<string, FocusSpec> =
  Object.fromEntries(FOCUS_MODES.map((f) => [f.id, f]));

/** Stable order — the share code stores an INDEX into this, so only append. */
export const FOCUS_IDS: FocusId[] = FOCUS_MODES.map((f) => f.id);

// =============================================================================
// METRICS
// =============================================================================

const num = (v: unknown, fallback: number): number =>
  typeof v === 'number' && Number.isFinite(v) ? v : fallback;

/** Every metric returns 0..1, and a photo with no analysis lands mid-scale. */
const metricOf = (p: PhotoLike | undefined, m: Metric): number => {
  const c = p?.analysis?.color;
  const h = num(c?.h, 0);
  const s = num(c?.s, 0);
  const l = num(c?.l, 0.5);
  switch (m) {
    case 'hue': return h;
    case 'lum': return l;
    case 'chroma': return s;
    // Warm/cool on the red-vs-blue axis, which is what the eye actually reads as
    // temperature — a hue sort puts magenta next to red and calls it warm.
    case 'warm': return (num(c?.r, 128) - num(c?.b, 128) + 255) / 510;
    // "Punch": saturated AND mid-toned. A blown-out white and a crushed black
    // are both weak in a collage however vivid their average hue claims to be.
    case 'punch': return s * (1 - Math.abs(l - 0.5) * 2);
  }
};

/**
 * Hue is a CIRCLE, so a plain ascending sort always leaves one seam — and puts
 * it at red, the most conspicuous place it could be. Ranking instead starts the
 * run at the widest empty stretch of the wheel, so the seam falls where this
 * particular set of photos has no colour anyway and the run reads continuous.
 */
const circularOrder = (vals: number[]): number[] => {
  const idx = vals.map((_, i) => i).sort((a, b) => vals[a] - vals[b] || a - b);
  if (idx.length < 3) return idx;
  let cut = 0;
  let widest = -1;
  for (let i = 0; i < idx.length; i++) {
    const cur = vals[idx[i]];
    const last = i === idx.length - 1;
    const next = vals[idx[last ? 0 : i + 1]] + (last ? 1 : 0);
    const gap = next - cur;
    if (gap > widest) { widest = gap; cut = last ? 0 : i + 1; }
  }
  return idx.slice(cut).concat(idx.slice(0, cut));
};

// =============================================================================
// CELL KEYS
// =============================================================================

const TAU = Math.PI * 2;
/** How many rings `drift` walks before it reaches the corner. */
const SPIRAL_TURNS = 3;

/**
 * A key per SLOT — `n` of them, always, however few cells the layout handed us.
 *
 * The length is taken from the slot count and never from `cells.length`, because
 * the two genuinely differ: the fill allocates `max(count, layout.length)` slots,
 * so the tail can have no geometry at all. Keying off the cells instead produced
 * a short rank list, and `out[slotOrder[i]]` then wrote to `out[undefined]` —
 * which does not throw, it just silently drops a photo out of the collage and
 * leaves a hole. Missing geometry is treated as dead centre; it still gets a key.
 */
const cellKeys = (cells: (CellGeom | null | undefined)[], n: number, key: CellKey): number[] => {
  // CLAMPED, not just defaulted. The assignment pass is synchronous and the
  // layout is debounced 50ms behind it, so on an aspect change one pass runs the
  // NEW normalisation over the OLD bounds and cy can reach 3.x. Unclamped, that
  // silently degrades every radial key to a plain y-sort for a frame — visible
  // in live mode, which repaints with no debounce of its own.
  const cx = (i: number) => clamp(num(cells[i]?.cx, 0.5), 0, 1);
  const cy = (i: number) => clamp(num(cells[i]?.cy, 0.5), 0, 1);
  const out = new Array<number>(n);

  // `reading`, `serpentine` and `checker` all need a row bucketing.
  //
  // Derived from the mean cell AREA, not from n: `n` counts only the fragments
  // still being filled, so locking 8 of 24 would bucket 16 cells into 4 rows
  // over a grid that visibly has 5, and the colour ramp reads mis-banded. The
  // area of the surviving cells still reports the FULL grid's density, which is
  // what "how many rows does this look like" actually means.
  let areaSum = 0, areaN = 0;
  for (let i = 0; i < n; i++) {
    const a = num(cells[i]?.area, 0);
    if (a > 0) { areaSum += a; areaN++; }
  }
  const rows = areaN > 0
    ? Math.max(1, Math.min(64, Math.round(1 / Math.sqrt(areaSum / areaN))))
    : Math.max(1, Math.round(Math.sqrt(n)));
  const rowOf = (i: number) => Math.min(rows - 1, Math.max(0, Math.floor(cy(i) * rows)));

  for (let i = 0; i < n; i++) {
    switch (key) {
      case 'x': out[i] = cx(i); break;
      case 'y': out[i] = cy(i); break;
      case 'reading': out[i] = rowOf(i) + cx(i) * 0.999; break;
      // Boustrophedon: every other row is read right-to-left, so a ramp laid
      // along it never snaps back to the left margin mid-gradient.
      case 'serpentine': {
        const r = rowOf(i);
        out[i] = r + (r % 2 === 0 ? cx(i) : 1 - cx(i)) * 0.999;
        break;
      }
      case 'radial': out[i] = Math.hypot(cx(i) - 0.5, cy(i) - 0.5); break;
      case 'angular': out[i] = Math.atan2(cy(i) - 0.5, cx(i) - 0.5) + Math.PI; break;
      case 'size': out[i] = num(cells[i]?.area, 0); break;
      case 'spiral': {
        const r = Math.hypot(cx(i) - 0.5, cy(i) - 0.5);
        const th = Math.atan2(cy(i) - 0.5, cx(i) - 0.5) + Math.PI;
        // Radius BANDS with the angle inside each: a continuous r + theta key
        // is dominated by whichever term has the larger range and stops being
        // a spiral at all.
        out[i] = Math.floor(Math.min(0.999, r / 0.71) * SPIRAL_TURNS) * TAU + th;
        break;
      }
      case 'checker': out[i] = 0; break;
    }
  }

  if (key === 'checker') {
    // Two passes: rank in reading order, then split odds from evens. Every even
    // position sorts before every odd one, so zipping a luminance ramp against
    // it puts the dark half on one colour of the board and the light half on
    // the other — neighbours land maximally far apart on the ramp.
    const reading = out.map((_, i) => rowOf(i) + cx(i) * 0.999);
    const order = reading.map((_, i) => i).sort((a, b) => reading[a] - reading[b] || a - b);
    order.forEach((cell, rank) => { out[cell] = (rank % 2) + rank / (2 * Math.max(1, n)); });
  }

  return out;
};

// =============================================================================
// ARRANGE
// =============================================================================

export interface ArrangeInput {
  /** Asset indices, one per slot, as produced by `assignSources`. */
  bag: number[];
  /** Geometry of the fragment each bag position lands in. May be short or hole-y. */
  cells: (CellGeom | null | undefined)[];
  /** The pool the bag indexes into. */
  images: PhotoLike[];
  arrangement: ArrangementId;
  /**
   * Re-deal WITHIN the arrangement. 0 (the default) is the exact ranking.
   *
   * Why this has to exist: the arrangement's output is a function of the SET of
   * photos and the fragment geometry — the order they arrived in is discarded.
   * Shuffle changes only that order, so with one slot per upload (the default
   * count) pressing Shuffle under any arrangement produced the identical
   * picture, every time, with no feedback and no visible control explaining
   * why. Since the dice now picks an arrangement on ~80% of rolls, that turned
   * Shuffle into a dead button on the common path.
   *
   * The fix is not to abandon the ranking — it is the whole point — but to draw
   * a different sample from it, which is the same idea that makes two rolls of
   * one recipe siblings rather than repeats (see diceRoll.ts).
   */
  shuffle?: number;
}

/**
 * A BOUNDED re-deal: still a permutation, but nothing moves further than
 * `RE_DEAL_WINDOW` of the list from its rank. A full shuffle would destroy the
 * ramp the arrangement exists to build — Spotlight would stop being Spotlight —
 * so the displacement has to be provably capped, not merely usually small.
 *
 * JITTER-AND-RESORT, not a windowed Fisher-Yates. The obvious `for i = n-1
 * down to 1, swap with something in [i-w, i]` is NOT windowed: an element
 * swapped downward gets picked up again when the cursor reaches its new home,
 * and the displacement compounds — measured at 36/40 slots for a window that
 * was supposed to be 6. Adding jitter of at most w/2 to each rank and re-sorting
 * caps it honestly: rank r' can only overtake rank r when r' < r + w, so no
 * photo moves more than w places, by construction rather than by luck.
 */
const RE_DEAL_WINDOW = 0.15;

const reDeal = (order: number[], seed: number): number[] => {
  if (!seed) return order;
  const n = order.length;
  const w = Math.max(1, n * RE_DEAL_WINDOW);
  let s = seed | 0;
  const rnd = () => {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), s | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const keys = order.map((_, i) => i + (rnd() - 0.5) * w);
  return order
    .map((_, i) => i)
    .sort((a, b) => keys[a] - keys[b] || a - b)
    .map((i) => order[i]);
};

/**
 * Re-pair the photos with the fragments.
 *
 * Returns a PERMUTATION of `bag` — same length, same multiset, every time. A
 * missing spec, `natural`, or a bag shorter than 2 all return the input order
 * untouched, so the default path is bit-identical to having never called this.
 */
export const arrangeBag = ({ bag, cells, images, arrangement, shuffle }: ArrangeInput): number[] => {
  const spec = ARRANGEMENT_BY_ID[arrangement];
  if (!spec || !spec.metric || !spec.cell || bag.length < 2) return bag;

  const n = bag.length;
  const vals = bag.map((assetIdx) => metricOf(images[assetIdx], spec.metric as Metric));

  // Photo order. Hue is circular; everything else is a straight ramp. The index
  // tiebreak is what makes the whole thing deterministic without an rng.
  let photoOrder: number[];
  if (spec.metric === 'hue') {
    photoOrder = circularOrder(vals);
  } else {
    photoOrder = vals.map((_, i) => i).sort((a, b) => vals[a] - vals[b] || a - b);
  }
  if (spec.flip) photoOrder.reverse();
  // Shuffle re-deals inside the ranking rather than doing nothing at all.
  photoOrder = reDeal(photoOrder, shuffle ?? 0);

  // Fragment order — one key per slot, keyed off `n`, never off `cells.length`.
  const keys = cellKeys(cells, n, spec.cell as CellKey);
  const slotOrder = keys.map((_, i) => i).sort((a, b) => keys[a] - keys[b] || a - b);

  // Zip. `out` is filled exactly once at every index because both orders are
  // permutations of 0..n-1 — which is the invariant the sweep asserts.
  const out = new Array<number>(n);
  for (let i = 0; i < n; i++) out[slotOrder[i]] = bag[photoOrder[i]];
  return out;
};

// =============================================================================
// FOCUS
// =============================================================================

const CENTRE = { x: 0.5, y: 0.5 };

/** Deterministic 0..1 from an integer — no shared state, so no call-order coupling. */
const hash01 = (n: number): number => {
  let t = (n + 0x6d2b79f5) | 0;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const clamp = (v: number, lo: number, hi: number): number => Math.max(lo, Math.min(hi, v));

const sane = (p: { x: number; y: number } | null | undefined): { x: number; y: number } | null => {
  if (!p || !Number.isFinite(p.x) || !Number.isFinite(p.y)) return null;
  return { x: clamp(p.x, 0, 1), y: clamp(p.y, 0, 1) };
};

/**
 * Where the crop for ONE slot should centre.
 *
 * `auto` reproduces the historical rule exactly — face if the detector found
 * one, else the energy centroid — so a project made before this module existed
 * opens looking the way it was left.
 */
export const focusAnchor = (
  photo: PhotoLike | undefined,
  focus: FocusId,
  slotSeed: number,
): { x: number; y: number } => {
  const a = photo?.analysis;
  const face = sane(a?.face);
  const energy = sane(a?.energy);
  const auto = face ?? energy ?? CENTRE;

  switch (focus) {
    case 'energy': return energy ?? CENTRE;
    case 'centre': return CENTRE;
    case 'thirds': return {
      x: auto.x < 0.5 ? 1 / 3 : 2 / 3,
      y: auto.y < 0.5 ? 1 / 3 : 2 / 3,
    };
    case 'wander': {
      // Bounded so a wandered crop still lands inside the picture rather than
      // pinning to an edge, which `calculateSmartCrop` would clamp back anyway
      // and every fragment would look identical again.
      const dx = (hash01(slotSeed * 2 + 1) - 0.5) * 0.62;
      const dy = (hash01(slotSeed * 2 + 2) - 0.5) * 0.62;
      return { x: clamp(auto.x + dx, 0.14, 0.86), y: clamp(auto.y + dy, 0.14, 0.86) };
    }
    case 'auto':
    default:
      return auto;
  }
};

/**
 * The photo as it should be CROPPED in this one slot.
 *
 * The whole crop pipeline — the live Stage, the static renderer, the worker and
 * the vector export — reads its anchor from `analysis.face ?? analysis.energy`,
 * so re-pointing `face` on a per-slot COPY steers all four with no change to any
 * of them. On `auto` the original object is returned by reference: no clone, no
 * new identity, and therefore not one wasted crop recompute on the default path.
 *
 * Typed T -> T rather than `T | undefined`, deliberately: the caller maps over
 * indices into a pool TypeScript already types as always-present, and widening
 * here would push a phantom `undefined` through every consumer of the draw
 * order. The runtime guard stays, because the index really can miss.
 */
export const withFocus = <T extends PhotoLike>(
  photo: T,
  focus: FocusId,
  slotSeed: number,
): T => {
  if (!photo || focus === 'auto') return photo;
  const anchor = focusAnchor(photo, focus, slotSeed);
  const a = photo.analysis;
  return {
    ...photo,
    analysis: {
      ...(a ?? {}),
      face: anchor,
      energy: sane(a?.energy) ?? anchor,
      color: a?.color ?? null,
    },
  } as T;
};
