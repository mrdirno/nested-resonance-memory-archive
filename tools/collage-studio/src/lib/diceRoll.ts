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
  /** Needs moving pictures to make sense. */
  video?: boolean;
}

export const RECIPES: Recipe[] = [
  { name: 'Cathedral',    layout: 'kaleidoscope',   count: [90, 220], entropy: [0.02, 0.18], bg: ['ink', 'indigo', 'void'], gutter: [0.002, 0.005] },
  { name: 'Rose Window',  layout: 'rosette',        count: [40, 110], entropy: [0.0, 0.15],  bg: ['oxblood', 'ink', 'indigo'] },
  { name: 'Sunflower',    layout: 'phyllotaxis',    count: [80, 260], entropy: [0.0, 0.2],   bg: ['void', 'moss'], gutter: [0.002, 0.006] },
  { name: 'Broken Glass', layout: 'delaunay',       count: [70, 190], entropy: [0.55, 1.0],  bg: ['void', 'ink'], gutter: [0.004, 0.011] },
  { name: 'Dry Lakebed',  layout: 'mud-crack',      count: [40, 130], entropy: [0.3, 0.7],   bg: ['bone', 'paper', 'void'], gutter: [0.005, 0.012] },
  { name: 'Deep Field',   layout: 'apollonian',     count: [60, 200], entropy: [0.2, 0.6],   bg: ['void', 'indigo'] },
  { name: 'Riverstone',   layout: 'circle-pack',    count: [50, 180], entropy: [0.45, 0.95], bg: ['slate', 'moss', 'bone'] },
  { name: 'Silk',         layout: 'flow',           count: [60, 200], entropy: [0.35, 0.8],  bg: ['ink', 'indigo'] },
  { name: 'Temple Floor', layout: 'penrose',        count: [70, 240], entropy: [0.0, 0.25],  bg: ['paper', 'bone', 'ink'] },
  { name: 'Vertigo',      layout: 'droste',         count: [50, 160], entropy: [0.1, 0.5],   bg: ['void', 'oxblood'] },
  { name: 'Sacred Bloom', layout: 'flower-of-life', count: [40, 140], entropy: [0.0, 0.1],   bg: ['ink', 'oxblood', 'bone'] },
  { name: 'Time Smear',   layout: 'slit-scan',      count: [60, 190], entropy: [0.4, 1.0],   bg: ['void'], gutter: [0.0, 0.003], video: true },
  { name: 'Coral Reef',   layout: 'reaction',       count: [40, 130], entropy: [0.3, 0.8],   bg: ['void', 'moss'] },
  { name: 'Manuscript',   layout: 'golden',         count: [8, 34],   entropy: [0.0, 0.3],   bg: ['paper', 'bone'], gutter: [0.008, 0.018] },
  { name: 'Snake Charm',  layout: 'hilbert',        count: [30, 120], entropy: [0.2, 0.7],   bg: ['ink', 'slate'] },
  { name: 'Star Chart',   layout: 'metatron',       count: [40, 140], entropy: [0.0, 0.3],   bg: ['indigo', 'void'] },
  { name: 'Ice Crystal',  layout: 'quasicrystal',   count: [70, 220], entropy: [0.1, 0.5],   bg: ['ink', 'slate'] },
  { name: 'Kufic',        layout: 'truchet',        count: [50, 180], entropy: [0.15, 0.6],  bg: ['paper', 'bone', 'oxblood'] },
  { name: 'Yantra',       layout: 'sri-yantra',     count: [30, 90],  entropy: [0.0, 0.2],   bg: ['oxblood', 'void'] },
  { name: 'Buckminster',  layout: 'geodesic',       count: [40, 160], entropy: [0.05, 0.45], bg: ['ink', 'indigo', 'slate'] },
  { name: 'Riot',         layout: 'shards',         count: [30, 120], entropy: [0.6, 1.0],   bg: ['void', 'paper'], gutter: [0.006, 0.016] },
  { name: 'Tide Pool',    layout: 'voronoi',        count: [60, 200], entropy: [0.25, 0.7],  bg: ['moss', 'slate', 'ink'] },
  { name: 'Mandalay',     layout: 'mandala',        count: [70, 240], entropy: [0.0, 0.25],  bg: ['oxblood', 'indigo', 'void'] },
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
    seed: Math.floor(rnd() * 0xffffff),
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
 * Six base-36 fields, dash-separated in two groups so it survives being read
 * aloud, retyped, or wrapped by a chat client. The seed is the long one because
 * it is the only field that genuinely needs the range; everything else is
 * quantised to the precision the eye can actually distinguish (entropy to 1/64,
 * gutter to 1/2000, zoom to 1/100) — quantising is what keeps the code short
 * AND makes a shared roll reproduce EXACTLY rather than approximately.
 */
export const encodeRoll = (r: Roll): string => {
  const li = Math.max(0, LAYOUT_ORDER.indexOf(r.layout));
  const ai = Math.max(0, (ASPECTS as readonly number[]).findIndex((a) => Math.abs(a - r.aspect) < 0.01));
  const e = Math.round(Math.min(1, Math.max(0, r.entropy)) * 63);
  const g = Math.round(Math.min(0.03, Math.max(0, r.gutter)) * 2000);
  const z = Math.round(Math.min(4, Math.max(0.5, r.zoom)) * 100);
  const bgi = Math.max(0, BG_KEYS.findIndex((k) => BACKGROUNDS[k] === r.bg));
  const f = (n: number, w = 1) => Math.max(0, Math.round(n)).toString(36).padStart(w, '0');
  return `${f(li, 2)}${f(r.count, 3)}${f(e, 2)}-${f(ai)}${f(g, 2)}${f(z, 2)}${f(bgi)}-${f(r.seed, 4)}`
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
    const seed = n(c);
    const layout = LAYOUT_ORDER[li];
    if (!layout || ![count, e, ai, g, z, bgi, seed].every(Number.isFinite)) return null;
    return {
      layout,
      primitive: 'rect',
      count: Math.max(2, count),
      entropy: e / 63,
      aspect: ASPECTS[ai] ?? 1,
      gutter: g / 2000,
      zoom: z / 100,
      bg: BACKGROUNDS[BG_KEYS[bgi] ?? 'void'],
      seed,
    };
  } catch {
    return null;
  }
};

export const BACKGROUND_SWATCHES = BACKGROUNDS;
