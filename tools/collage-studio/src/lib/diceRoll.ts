// src/lib/diceRoll.ts
// -----------------------------------------------------------------------------
// THE DICE ROLL.
//
// WHY IT IS NOT `Math.random()` OVER EVERY SLIDER
//   Uniform random over the parameter space is mostly garbage, and a generative
//   tool that hands you garbage three times in a row teaches you to stop
//   pressing the button. The parameters are not independent: a 400-cell Golden
//   subdivision is mush, a 6-cell Sunflower is not a sunflower, and high entropy
//   on a sacred construction destroys the exact symmetry that made it worth
//   having. So a roll samples a CONSTRAINED space — every generator carries its
//   own sane count range, and entropy is drawn conditioned on the family.
//
// WHERE THE "ENDLESS" FEELING ACTUALLY COMES FROM
//   Not from the number of generators. Twenty fixed presets feel finite after
//   twenty presses; twenty generators x a continuous parameter space x a seed
//   feels bottomless, because the SECOND roll of the same recipe is visibly a
//   sibling of the first rather than a repeat. Recipes give the roll a point of
//   view; the seed and the jitter keep it from being a menu.
//
// REPRODUCIBLE AND SHAREABLE
//   Every roll encodes to a short code. Same code, same collage, on any device
//   — which is what makes a good roll worth sending to somebody.
// -----------------------------------------------------------------------------

import type { LayoutMode, PrimitiveType } from '../types';
import { GENERATORS, GENERATOR_BY_ID } from '../engine/geom/generators';
import {
  ARRANGEMENT_IDS, FOCUS_IDS, TWIST_IDS, type ArrangementId, type FocusId, type TwistId,
} from './composition';

// =============================================================================
// SHAPE
// =============================================================================

export interface Roll {
  layout: LayoutMode;
  primitive: PrimitiveType;
  count: number;
  /** 0..1 */
  entropy: number;
  /** width / height */
  aspect: number;
  /** the app's gutter fraction */
  gutter: number;
  zoom: number;
  bg: string;
  seed: number;
  /** Which photo goes in which fragment — see composition.ts. */
  arrangement: ArrangementId;
  /** What each fragment centres on inside its photo — see composition.ts. */
  focus: FocusId;
  /** How far the picture leans inside its fragment — see composition.ts. */
  twist: TwistId;
  /** Name of the recipe this came from, when it came from one. */
  recipe?: string;
}

/** Parameters the user can PIN before re-rolling — the slot-machine hold. */
export type RollLock = keyof Pick<Roll, 'layout' | 'count' | 'entropy' | 'aspect' | 'gutter' | 'bg'>;

export const ROLL_LOCKS: RollLock[] = ['layout', 'count', 'entropy', 'aspect', 'gutter', 'bg'];

// =============================================================================
// PALETTE
// =============================================================================

/**
 * Backgrounds, not colours-of-the-art. The background is what the gutter shows,
 * so it is doing the job a mount board does in a frame shop: near-black recedes
 * and makes fragments glow; warm paper reads as printed collage; a deep tone
 * reads as stained glass. Mid greys are absent on purpose — they fight the
 * photograph for attention and win.
 */
const BACKGROUNDS = {
  void: '#050505',
  ink: '#0b0d12',
  slate: '#141922',
  paper: '#f2ece1',
  bone: '#e8e2d6',
  oxblood: '#2a0f14',
  indigo: '#0d1330',
  moss: '#101c15',
} as const;

type BgKey = keyof typeof BACKGROUNDS;
const BG_KEYS = Object.keys(BACKGROUNDS) as BgKey[];
const DARK_BGS: BgKey[] = ['void', 'ink', 'slate', 'oxblood', 'indigo', 'moss'];
const LIGHT_BGS: BgKey[] = ['paper', 'bone'];

const ASPECTS = [1, 0.6667, 1.5, 0.8, 1.25, 1.7778, 0.5625] as const;

// =============================================================================
// RECIPES
// =============================================================================

/**
 * Known-great pairings. A recipe fixes the things that must be right and leaves
 * the rest to the dice, so two rolls of "Cathedral" are recognisably the same
 * idea and never the same picture.
 *
 * `count` and `entropy` are RANGES; the roll samples inside them.
 */
interface Recipe {
  name: string;
  layout: LayoutMode;
  count: [number, number];
  entropy: [number, number];
  bg: BgKey[];
  aspect?: number[];
  gutter?: [number, number];
  zoom?: [number, number];
  /** Arrangements this recipe insists on, when the pairing IS the idea. */
  arrange?: ArrangementId[];
  /** Needs moving pictures to make sense. */
  video?: boolean;
}

export const RECIPES: Recipe[] = [
  { name: 'Cathedral',    layout: 'kaleidoscope',   count: [90, 220], entropy: [0.02, 0.18], bg: ['ink', 'indigo', 'void'], gutter: [0.002, 0.005], arrange: ['wheel', 'drift', 'natural'] },
  { name: 'Rose Window',  layout: 'rosette',        count: [40, 110], entropy: [0.0, 0.15],  bg: ['oxblood', 'ink', 'indigo'], arrange: ['wheel', 'vivid'] },
  { name: 'Sunflower',    layout: 'phyllotaxis',    count: [80, 260], entropy: [0.0, 0.2],   bg: ['void', 'moss'], gutter: [0.002, 0.006], arrange: ['drift', 'spotlight'] },
  { name: 'Broken Glass', layout: 'delaunay',       count: [70, 190], entropy: [0.55, 1.0],  bg: ['void', 'ink'], gutter: [0.004, 0.011] },
  { name: 'Dry Lakebed',  layout: 'mud-crack',      count: [40, 130], entropy: [0.3, 0.7],   bg: ['bone', 'paper', 'void'], gutter: [0.005, 0.012] },
  { name: 'Deep Field',   layout: 'apollonian',     count: [60, 200], entropy: [0.2, 0.6],   bg: ['void', 'indigo'], arrange: ['spotlight', 'eclipse'] },
  { name: 'Riverstone',   layout: 'circle-pack',    count: [50, 180], entropy: [0.45, 0.95], bg: ['slate', 'moss', 'bone'] },
  { name: 'Silk',         layout: 'flow',           count: [60, 200], entropy: [0.35, 0.8],  bg: ['ink', 'indigo'] },
  { name: 'Temple Floor', layout: 'penrose',        count: [70, 240], entropy: [0.0, 0.25],  bg: ['paper', 'bone', 'ink'], arrange: ['checker', 'flow'] },
  { name: 'Vertigo',      layout: 'droste',         count: [50, 160], entropy: [0.1, 0.5],   bg: ['void', 'oxblood'] },
  { name: 'Sacred Bloom', layout: 'flower-of-life', count: [40, 140], entropy: [0.0, 0.1],   bg: ['ink', 'oxblood', 'bone'] },
  { name: 'Time Smear',   layout: 'slit-scan',      count: [60, 190], entropy: [0.4, 1.0],   bg: ['void'], gutter: [0.0, 0.003], video: true },
  { name: 'Coral Reef',   layout: 'reaction',       count: [40, 130], entropy: [0.3, 0.8],   bg: ['void', 'moss'] },
  { name: 'Manuscript',   layout: 'golden',         count: [8, 34],   entropy: [0.0, 0.3],   bg: ['paper', 'bone'], gutter: [0.008, 0.018], arrange: ['hero', 'natural'] },
  { name: 'Snake Charm',  layout: 'hilbert',        count: [30, 120], entropy: [0.2, 0.7],   bg: ['ink', 'slate'] },
  { name: 'Star Chart',   layout: 'metatron',       count: [40, 140], entropy: [0.0, 0.3],   bg: ['indigo', 'void'] },
  { name: 'Ice Crystal',  layout: 'quasicrystal',   count: [70, 220], entropy: [0.1, 0.5],   bg: ['ink', 'slate'] },
  { name: 'Kufic',        layout: 'truchet',        count: [50, 180], entropy: [0.15, 0.6],  bg: ['paper', 'bone', 'oxblood'] },
  { name: 'Yantra',       layout: 'sri-yantra',     count: [30, 90],  entropy: [0.0, 0.2],   bg: ['oxblood', 'void'] },
  { name: 'Buckminster',  layout: 'geodesic',       count: [40, 160], entropy: [0.05, 0.45], bg: ['ink', 'indigo', 'slate'] },
  { name: 'Riot',         layout: 'shards',         count: [30, 120], entropy: [0.6, 1.0],   bg: ['void', 'paper'], gutter: [0.006, 0.016] },
  { name: 'Tide Pool',    layout: 'voronoi',        count: [60, 200], entropy: [0.25, 0.7],  bg: ['moss', 'slate', 'ink'] },
  { name: 'Mandalay',     layout: 'mandala',        count: [70, 240], entropy: [0.0, 0.25],  bg: ['oxblood', 'indigo', 'void'], arrange: ['wheel', 'eclipse'] },
];

// =============================================================================
// SAMPLING
// =============================================================================

const pick = <T,>(arr: readonly T[], rnd: () => number): T => arr[Math.floor(rnd() * arr.length)];
const between = (lo: number, hi: number, rnd: () => number): number => lo + rnd() * (hi - lo);

/**
 * Log-uniform count. Uniform over [8, 300] puts three quarters of every roll
 * above 80 fragments, so the sparse, large-fragment compositions — often the
 * best ones — effectively never come up. Sampling in log space gives each
 * ORDER OF MAGNITUDE equal weight, which is how the range is actually read.
 */
const logCount = (lo: number, hi: number, rnd: () => number): number =>
  Math.round(Math.exp(between(Math.log(Math.max(2, lo)), Math.log(Math.max(3, hi)), rnd)));

/**
 * Entropy conditioned on family. This is the single most important constraint
 * in the whole roll: a sacred construction at entropy 0.9 is not "a wilder
 * mandala", it is a broken one — the exactness IS the subject. Organic
 * constructions are the opposite and look mechanical when it is too low.
 */
const entropyFor = (layout: LayoutMode, rnd: () => number): number => {
  const fam = GENERATOR_BY_ID[layout]?.family;
  if (fam === 'sacred') return between(0, 0.3, rnd) ** 1.4;
  if (fam === 'organic') return between(0.25, 0.95, rnd);
  if (fam === 'recursive') return between(0.05, 0.55, rnd);
  return between(0.15, 0.9, rnd);
};

/**
 * Arrangement conditioned on the layout family — the same idea as `entropyFor`,
 * for the same reason: the pairing that makes a construction sing depends on
 * whether it has a CENTRE. A colour wheel around a mandala is the figure doing
 * what it was drawn to do; the same wheel over a rectilinear grid is a wheel
 * nobody can see, because the grid has no angle to read it against.
 *
 * `natural` keeps a fifth of rolls: the source-first order is a real answer, and
 * a dice that never leaves it alone would make every collage look sorted.
 */
const RADIAL_ARRANGEMENTS: ArrangementId[] = ['wheel', 'spotlight', 'eclipse', 'vivid', 'drift'];
const LINEAR_ARRANGEMENTS: ArrangementId[] = ['flow', 'horizon', 'heat', 'checker', 'hero'];

const arrangementFor = (layout: LayoutMode, rnd: () => number): ArrangementId => {
  if (rnd() < 0.2) return 'natural';
  const fam = GENERATOR_BY_ID[layout]?.family;
  // A LEAN, not a rule. Nine of the twenty-four generators are sacred and only
  // four are rectilinear, so hard-gating by family would have starved the linear
  // arrangements down to a rounding error of all rolls — a chip in the picker
  // the dice effectively never reaches is a chip that may as well not exist.
  const radialBias = fam === 'sacred' || fam === 'recursive' ? 0.8 : fam === 'structure' ? 0.2 : 0.5;
  return pick(rnd() < radialBias ? RADIAL_ARRANGEMENTS : LINEAR_ARRANGEMENTS, rnd);
};

/**
 * Focus is NOT conditioned on the layout — it is a property of the photographs,
 * not of the figure. Weighted rather than uniform because `auto` is right most
 * of the time (it finds the face), and the other four are looks you reach for.
 */
const focusFor = (rnd: () => number): FocusId => {
  const r = rnd();
  if (r < 0.52) return 'auto';
  if (r < 0.70) return 'wander';
  if (r < 0.83) return 'thirds';
  if (r < 0.93) return 'energy';
  return 'centre';
};

/**
 * Twist IS conditioned on the family, for the reason arrangement is: two of the
 * four modes are RADIAL FIELDS. `pinwheel` swings around a centre and `cascade`
 * ramps out from one, so both need a figure that HAS a centre to be read
 * against; `tilt`'s checkerboard alternation needs a grid regular enough for the
 * alternation to be visible as a pattern.
 *
 * A LEAN, never a gate — the same scar as `arrangementFor`. Hard-gating by
 * family sent half a roster to a rounding error of all rolls, and a chip the
 * dice never reaches may as well not exist. At 0.75/0.25 the rarest mode still
 * lands on ~5% of rolls, which the roster-spread sweep asserts.
 *
 * `none` keeps well over half of rolls, and that is not timidity: a twist costs
 * a crop-in of |cos|+|sin| — real picture thrown away — so it has to be the
 * exception that means something rather than the house style.
 */
const RADIAL_TWISTS: TwistId[] = ['pinwheel', 'cascade'];
const LINEAR_TWISTS: TwistId[] = ['tilt', 'scatter'];

const twistFor = (layout: LayoutMode, rnd: () => number): TwistId => {
  if (rnd() < 0.58) return 'none';
  const fam = GENERATOR_BY_ID[layout]?.family;
  const radialBias = fam === 'sacred' || fam === 'recursive' ? 0.75 : fam === 'structure' ? 0.25 : 0.5;
  return pick(rnd() < radialBias ? RADIAL_TWISTS : LINEAR_TWISTS, rnd);
};

const bgFor = (layout: LayoutMode, rnd: () => number): BgKey => {
  const fam = GENERATOR_BY_ID[layout]?.family;
  // Radial and sacred figures glow out of the dark and go flat on paper; the
  // rectilinear structure family is the one that reads as print.
  if (fam === 'sacred') return pick(DARK_BGS, rnd);
  if (fam === 'structure') return rnd() < 0.55 ? pick(LIGHT_BGS, rnd) : pick(DARK_BGS, rnd);
  return rnd() < 0.82 ? pick(DARK_BGS, rnd) : pick(LIGHT_BGS, rnd);
};

export interface RollOptions {
  /** Keep these values from `previous` instead of re-rolling them. */
  locks?: RollLock[];
  previous?: Roll;
  /** True when the project has video clips — unlocks the motion recipes. */
  hasVideo?: boolean;
  /** Force a specific recipe by name. */
  recipe?: string;
  /** Injectable for tests / reproduction. Defaults to Math.random. */
  rnd?: () => number;
}

/**
 * Roll the dice.
 *
 * ~62% of rolls come from a recipe and ~38% free-roll across the whole roster.
 * The split matters: all-recipe would make the tool feel like a preset list
 * with a shuffle button, and all-free would lose the curated pairings that make
 * the good rolls good.
 */
export const rollDice = (opts: RollOptions = {}): Roll => {
  const rnd = opts.rnd ?? Math.random;
  const locks = new Set(opts.locks ?? []);
  const prev = opts.previous;

  const pool = RECIPES.filter((r) => opts.hasVideo || !r.video);
  const named = opts.recipe ? RECIPES.find((r) => r.name === opts.recipe) : undefined;
  const recipe = named ?? (rnd() < 0.62 ? pick(pool, rnd) : undefined);

  let layout: LayoutMode;
  if (locks.has('layout') && prev) layout = prev.layout;
  else if (recipe) layout = recipe.layout;
  else {
    const usable = GENERATORS.filter((g) => opts.hasVideo || g.family !== 'motion');
    layout = pick(usable, rnd).id as LayoutMode;
  }

  const spec = GENERATOR_BY_ID[layout];
  const range: [number, number] = recipe?.count ?? spec?.countRange ?? [8, 120];

  const count = locks.has('count') && prev ? prev.count : logCount(range[0], range[1], rnd);
  const entropy = locks.has('entropy') && prev
    ? prev.entropy
    : recipe ? between(recipe.entropy[0], recipe.entropy[1], rnd) : entropyFor(layout, rnd);

  const aspect = locks.has('aspect') && prev
    ? prev.aspect
    : pick(recipe?.aspect ?? ASPECTS, rnd);

  const gutter = locks.has('gutter') && prev
    ? prev.gutter
    : recipe?.gutter ? between(recipe.gutter[0], recipe.gutter[1], rnd)
    // Skewed low: a fine gutter lets the photographs carry the frame, and a
    // chunky one is a deliberate choice rather than the average case.
    : between(0.001, 0.014, rnd) ** 1.5 * 8;

  const bg = locks.has('bg') && prev
    ? prev.bg
    : BACKGROUNDS[recipe ? pick(recipe.bg, rnd) : bgFor(layout, rnd)];

  return {
    layout,
    // Every generator defines its own cell shape; `primitive` only reaches the
    // two legacy grid modes, so the roll leaves it alone rather than pretending
    // it did something.
    primitive: prev?.primitive ?? 'rect',
    count,
    entropy,
    aspect,
    gutter: Math.max(0, Math.min(0.03, gutter)),
    zoom: recipe?.zoom ? between(recipe.zoom[0], recipe.zoom[1], rnd) : between(1, 1.35, rnd),
    bg,
    // A recipe may INSIST on an arrangement where the pairing is the whole idea
    // (a rose window wants the colour wheel); otherwise the family decides.
    arrangement: recipe?.arrange ? pick(recipe.arrange, rnd) : arrangementFor(layout, rnd),
    focus: focusFor(rnd),
    seed: Math.floor(rnd() * 0xffffff),
    // Drawn AFTER the seed on purpose: appending here leaves every earlier draw
    // in the stream untouched, so a build with twist rolls the same layout,
    // count, chaos, aspect, gutter, zoom, background, arrangement, focus and
    // seed from a given rng as the build before it did.
    twist: twistFor(layout, rnd),
    recipe: recipe?.name,
  };
};

// =============================================================================
// SHARE CODES
// =============================================================================

const LAYOUT_ORDER: LayoutMode[] = GENERATORS.map((g) => g.id as LayoutMode);

/**
 * A roll as a short code.
 *
 * Eight base-36 fields, dash-separated in three groups so it survives being read
 * aloud, retyped, or wrapped by a chat client. The seed is the long one because
 * it is the only field that genuinely needs the range; everything else is
 * quantised to the precision the eye can actually distinguish (entropy to 1/64,
 * gutter to 1/2000, zoom to 1/100) — quantising is what keeps the code short
 * AND makes a shared roll reproduce EXACTLY rather than approximately.
 *
 * Arrangement and focus were APPENDED to the middle group rather than given a
 * group of their own. A code minted before they existed has a 6-character middle
 * group instead of 8, and `decodeRoll` reads the two extra characters only when
 * they are there — so every code already sitting in somebody's chat log still
 * opens, as the composition it was when it was sent.
 */
export const encodeRoll = (r: Roll): string => {
  const li = Math.max(0, LAYOUT_ORDER.indexOf(r.layout));
  const ai = Math.max(0, (ASPECTS as readonly number[]).findIndex((a) => Math.abs(a - r.aspect) < 0.01));
  const e = Math.round(Math.min(1, Math.max(0, r.entropy)) * 63);
  const g = Math.round(Math.min(0.03, Math.max(0, r.gutter)) * 2000);
  const z = Math.round(Math.min(4, Math.max(0.5, r.zoom)) * 100);
  const bgi = Math.max(0, BG_KEYS.findIndex((k) => BACKGROUNDS[k] === r.bg));
  const ari = Math.max(0, ARRANGEMENT_IDS.indexOf(r.arrangement));
  const foi = Math.max(0, FOCUS_IDS.indexOf(r.focus));
  const twi = Math.max(0, TWIST_IDS.indexOf(r.twist));
  const f = (n: number, w = 1) => Math.max(0, Math.round(n)).toString(36).padStart(w, '0');
  return `${f(li, 2)}${f(r.count, 3)}${f(e, 2)}-${f(ai)}${f(g, 2)}${f(z, 2)}${f(bgi)}${f(ari)}${f(foi)}${f(twi)}-${f(r.seed, 4)}`
    .toUpperCase();
};

export const decodeRoll = (code: string): Roll | null => {
  const parts = code.trim().toLowerCase().replace(/\s+/g, '').split('-');
  if (parts.length !== 3) return null;
  const [a, b, c] = parts;
  if (a.length < 7 || b.length < 6 || c.length < 1) return null;
  const n = (s: string) => parseInt(s, 36);
  try {
    const li = n(a.slice(0, 2));
    const count = n(a.slice(2, 5));
    const e = n(a.slice(5, 7));
    const ai = n(b.slice(0, 1));
    const g = n(b.slice(1, 3));
    const z = n(b.slice(3, 5));
    const bgi = n(b.slice(5, 6));
    // Pre-composition codes stop at 6. Absent means the composition this code
    // was minted with: the untouched fill order and the historical crop rule.
    const ari = b.length >= 7 ? n(b.slice(6, 7)) : 0;
    const foi = b.length >= 8 ? n(b.slice(7, 8)) : 0;
    // Pre-twist codes stop at 8. Absent means `none` — a code minted before this
    // feature existed described a square collage, and it still opens as one.
    const twi = b.length >= 9 ? n(b.slice(8, 9)) : 0;
    const seed = n(c);
    const layout = LAYOUT_ORDER[li];
    if (!layout || ![count, e, ai, g, z, bgi, ari, foi, twi, seed].every(Number.isFinite)) return null;
    return {
      layout,
      primitive: 'rect',
      count: Math.max(2, count),
      entropy: e / 63,
      aspect: ASPECTS[ai] ?? 1,
      gutter: g / 2000,
      zoom: z / 100,
      bg: BACKGROUNDS[BG_KEYS[bgi] ?? 'void'],
      arrangement: ARRANGEMENT_IDS[ari] ?? 'natural',
      focus: FOCUS_IDS[foi] ?? 'auto',
      twist: TWIST_IDS[twi] ?? 'none',
      seed,
    };
  } catch {
    return null;
  }
};

export const BACKGROUND_SWATCHES = BACKGROUNDS;
