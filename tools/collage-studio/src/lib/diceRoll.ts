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
import { LOOK_IDS, type LookId } from './grade';

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
  /**
   * THE LOOK — the colour grade over every fragment. See lib/grade.ts.
   *
   * Optional because every Roll built before this field existed is still a
   * valid Roll, and absent means `none`, which is exactly the picture those
   * rolls described.
   */
  look?: LookId;
  /** Name of the recipe this came from, when it came from one. */
  recipe?: string;
  /**
   * Is `count` a DECISION or a DEFAULT?
   *
   * The app derives the fragment count from the number of sources until somebody
   * takes it over (the stepper, the dice, a project, a code) — `countTouchedRef`
   * in App.tsx. The two are indistinguishable once serialised, and they must not
   * be: a code carrying a CHOSEN 3 has to survive being opened next to twenty
   * photographs, and a code carrying a DERIVED 6 has to get out of the way of
   * them. Without this bit a plain refresh — which now replays the address bar's
   * own code — would pin a derived count onto the next import forever.
   */
  countOwned?: boolean;
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

/**
 * THE LOOK the dice picks.
 *
 * Ungraded most of the time, on purpose. A grade is the loudest thing in the
 * roster — it changes every pixel of every fragment — so a dice that ALWAYS
 * graded would make the button feel like a filter shuffle rather than a
 * composition roll, and the honest default for a photograph is the photograph.
 * 55% none, the rest spread flat across the seven, which is often enough that a
 * few presses will show you the row exists.
 */
const lookFor = (rnd: () => number): LookId => {
  if (rnd() < 0.55) return 'none';
  // Slice past `none` rather than re-rolling: a re-roll would draw a variable
  // number of values from the stream and make the roll depend on how many times
  // it happened to land on index 0, which is the sort of thing that quietly
  // breaks seeded reproduction.
  return pick(LOOK_IDS.slice(1), rnd);
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

  // SNAPPED ON THE WAY OUT — see `snapRoll`. The roll draws entropy, gutter and
  // zoom from continuous ranges; the share code quantises them. Snapping here
  // is what makes those two facts agree, so a rolled composition is exactly
  // representable by its own code instead of nearly.
  return snapRoll({
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
    // Drawn LAST, after the twist, for the same reason the twist was drawn
    // after the seed: appending to the end of the stream leaves every earlier
    // draw untouched, so a build with the look rolls the same layout, count,
    // chaos, aspect, gutter, zoom, background, arrangement, focus, seed and
    // twist from a given rng as the build before it did.
    look: lookFor(rnd),
    recipe: recipe?.name,
    // The dice picks a fragment count on purpose, out of the generator's own
    // sane range. That is a decision, so a code minted from it must not be
    // overridden by however many photographs the recipient happens to have.
    countOwned: true,
  });
};

// =============================================================================
// SHARE CODES
// =============================================================================

/**
 * THE INDEX SPACE OF LAYOUTS, and why the legacy five are APPENDED.
 *
 * This used to be `GENERATORS.map(...)` alone — the 23 generative constructions
 * and nothing else. The five legacy modes were therefore not in the space at
 * all, and `indexOf` returned -1 for every one of them, which `Math.max(0, …)`
 * turned into index 0. The app BOOTS on `minimal`: the very first code anybody
 * could copy described a completely different construction, silently. Appending
 * rather than prepending is what keeps every index already minted stable.
 */
const LAYOUT_ORDER: LayoutMode[] = [
  ...GENERATORS.map((g) => g.id as LayoutMode),
  'minimal', 'balanced', 'complex', 'field', 'stencil',
];

/** Fragment shape, in a fixed order because the index travels in share codes. */
export const PRIMITIVE_ORDER: PrimitiveType[] = ['rect', 'tri', 'circle', 'octagon', 'random'];

/** The roster of frame shapes — the ONE list the UI and the codec both read. */
export const ASPECT_ROSTER: readonly number[] = ASPECTS;

/**
 * THE GRID.
 *
 * The code quantises, and quantising is only lossless if the STATE is on the
 * grid too. `rollDice` used to draw entropy, gutter and zoom from continuous
 * ranges, so the very first encode of a fresh roll already lost something and
 * the "same code, same collage" promise in this file's header was false by a
 * fraction of a slider detent. `snapRoll` puts the roll on the grid at the
 * moment it is made, which is what makes the promise true rather than
 * approximately true — and the grid is chosen to CONTAIN the UI's own slider
 * steps (chaos 0.01, padding 0.001), so a hand-tuned composition is on it too.
 */
export const snapRoll = (r: Roll): Roll => ({
  ...r,
  entropy: Math.round(Math.min(1, Math.max(0, r.entropy)) * 100) / 100,
  gutter: Math.round(Math.min(0.05, Math.max(0, r.gutter)) * 2000) / 2000,
  zoom: Math.round(Math.min(4, Math.max(0.5, r.zoom)) * 100) / 100,
  // CEILINGS THAT MATCH THE FIELD, not ceilings that seem generous. Every field
  // below the LAST one in its group is read by fixed-width slicing, so a value
  // that outgrows its width does not clip — it lengthens the group and shifts
  // every later slice by a character, and the code then decodes CLEANLY into a
  // different composition. `count` at 46,656 (= 36^3) did exactly that: the
  // reader saw 1,296 fragments and read the chaos field out of the seed's
  // digits. Unreachable by hand, one keystroke away in a saved project file.
  count: Math.max(1, Math.min(MAX_COUNT, Math.round(r.count))),
  // The seed is the LAST field of the LAST group, so it is the one value that
  // may grow: `Date.now()` needs eight characters and MAX_SAFE_INTEGER ten.
  seed: Math.max(0, Math.round(r.seed)),
});

/** 36^3 - 1: the largest fragment count three base-36 characters can hold. */
export const MAX_COUNT = 36 ** 3 - 1;

/** A CSS colour the app can actually hold — `#rrggbb` or `rgb(r,g,b)` — as 24 bits. */
const rgb24 = (css: string): number => {
  const s = css.trim().toLowerCase();
  const hex = /^#([0-9a-f]{6})$/.exec(s);
  if (hex) return parseInt(hex[1], 16);
  const short = /^#([0-9a-f]{3})$/.exec(s);
  if (short) {
    const [r, g, b] = short[1].split('');
    return parseInt(`${r}${r}${g}${g}${b}${b}`, 16);
  }
  const fn = /^rgba?\(\s*([0-9.]+)[\s,]+([0-9.]+)[\s,]+([0-9.]+)/.exec(s);
  if (fn) {
    const ch = (v: string) => Math.max(0, Math.min(255, Math.round(parseFloat(v))));
    return (ch(fn[1]) << 16) | (ch(fn[2]) << 8) | ch(fn[3]);
  }
  return -1;
};

const hex6 = (n: number) => `#${Math.max(0, Math.min(0xffffff, n)).toString(16).padStart(6, '0')}`;

/**
 * A roll as a short code.
 *
 * Base-36 fields, dash-separated in groups so it survives being read aloud,
 * retyped, or wrapped by a chat client. The seed is the long one because it is
 * the only field that genuinely needs the range; everything else is quantised to
 * the precision the eye can actually distinguish (entropy to 1/100 = the chaos
 * slider's own step, gutter to 1/2000, zoom to 1/100) — quantising is what keeps
 * the code short AND makes a shared roll reproduce EXACTLY rather than
 * approximately, PROVIDED the state is on the same grid (see `snapRoll`).
 *
 * GROWTH IS APPEND-ONLY, AND THE READER SWITCHES ON LENGTH. Arrangement and
 * focus were appended to the middle group rather than given a group of their
 * own; then twist; now the fragment SHAPE and the exact background. A code
 * minted before a field existed is simply shorter, and `decodeRoll` reads each
 * extra character only when it is there — so a code already sitting in
 * somebody's chat log still opens, as the composition it was when it was sent.
 *
 * WHY THE BACKGROUND IS CARRIED TWICE. Position 5 is an index into the eight
 * roster backgrounds and is what old codes have. But the app can hold a colour
 * that is on no roster — the "Average" swatch derives one from your photographs
 * — and an index cannot express it, so it fell back to index 0 and turned a
 * paper-white collage near-black. Positions 10..14 carry the actual 24 bits and
 * WIN when present. The index is still emitted so a truncated code degrades to
 * the nearest roster colour instead of to nothing.
 *
 * WHAT IS DELIBERATELY NOT IN HERE: the images. A code is a RECIPE — the same
 * code with your photographs is your collage, which is the whole point of being
 * able to send one.
 */
export const encodeRoll = (r: Roll, extra = ''): string => {
  const li = Math.max(0, LAYOUT_ORDER.indexOf(r.layout));
  // NEAREST, not first-within-0.01. A frame shape off the roster — reachable by
  // loading an old project — used to hit `findIndex` = -1 and encode as SQUARE.
  let ai = 0;
  for (let i = 1; i < ASPECTS.length; i++) {
    if (Math.abs(ASPECTS[i] - r.aspect) < Math.abs(ASPECTS[ai] - r.aspect)) ai = i;
  }
  const e = Math.round(Math.min(1, Math.max(0, r.entropy)) * 100);
  // 0.05, matching the padding slider's maximum. It was 0.03 — the roll's own
  // ceiling — so a hand-set 5% gutter came back as 3%.
  const g = Math.round(Math.min(0.05, Math.max(0, r.gutter)) * 2000);
  const z = Math.round(Math.min(4, Math.max(0.5, r.zoom)) * 100);
  const rgb = rgb24(r.bg);
  // NEAREST roster colour, by channel distance — not `indexOf` with a fallback
  // to element zero. This index is only read by a code TRUNCATED below the exact
  // colour, and "the closest background we have" is a survivable degradation
  // where "near-black, always" turns a paper-white collage inside out.
  let bgi = 0;
  {
    const dist = (i: number) => {
      const c = rgb24(BACKGROUNDS[BG_KEYS[i]]);
      return Math.abs((c >> 16) - (rgb >> 16))
        + Math.abs(((c >> 8) & 255) - ((rgb >> 8) & 255))
        + Math.abs((c & 255) - (rgb & 255));
    };
    if (rgb >= 0) for (let i = 1; i < BG_KEYS.length; i++) if (dist(i) < dist(bgi)) bgi = i;
  }
  const ari = Math.max(0, ARRANGEMENT_IDS.indexOf(r.arrangement));
  const foi = Math.max(0, FOCUS_IDS.indexOf(r.focus));
  const twi = Math.max(0, TWIST_IDS.indexOf(r.twist));
  const pri = Math.max(0, PRIMITIVE_ORDER.indexOf(r.primitive));
  /**
   * A FIXED-WIDTH field, and it may not exceed its width.
   *
   * `padStart` sets a MINIMUM, not a maximum. Every field but the last one in
   * its group is read back by slicing at a fixed offset, so a value that needs
   * one more character does not clip — it lengthens the group and shifts every
   * later slice along, and the code then decodes cleanly into a DIFFERENT
   * composition. Clamping here makes that impossible for all of them at once
   * rather than one field at a time; `capacity` is asserted per roster in
   * tests/unit/rollCode.invariants.mjs so a roster that outgrows its field
   * fails a sweep instead of silently corrupting codes.
   */
  const fw = (n: number, w: number) => {
    const cap = 36 ** w - 1;
    return Math.max(0, Math.min(cap, Math.round(n))).toString(36).padStart(w, '0');
  };
  /** The seed is the last field of the last group, so it is free to grow. */
  const tail = (n: number, w: number) => Math.max(0, Math.round(n)).toString(36).padStart(w, '0');
  const mid = `${fw(ai, 1)}${fw(g, 2)}${fw(z, 2)}${fw(bgi, 1)}${fw(ari, 1)}${fw(foi, 1)}${fw(twi, 1)}${fw(pri, 1)}`
    + fw(rgb < 0 ? rgb24(BACKGROUNDS[BG_KEYS[bgi] ?? 'void']) : rgb, 5);
  const head = `${fw(li, 2)}${fw(r.count, 3)}${fw(e, 2)}`;
  const seed = tail(r.seed, 4);
  const owned = r.countOwned ? '1' : '0';
  /**
   * THE LOOK, as an index — and NOT via `Math.max(0, indexOf(…))`.
   *
   * That idiom is the scar on this file: it turns "not representable" into
   * "element zero", and for the layout roster element zero was a completely
   * different construction. Here the honest answer genuinely IS element zero,
   * because element zero is `none` and a grade is ADDITIVE — a look this build
   * does not know about is no look, not a plausible-looking neighbour. The
   * difference is written out rather than hidden behind the same three
   * characters, so the next reader can tell which case they are in.
   */
  const loIdx = LOOK_IDS.indexOf((r.look ?? 'none') as LookId);
  const look = fw(loIdx < 0 ? 0 : loIdx, 1);
  // `extra` is whatever a LAYER ABOVE has appended to the code — today that is
  // rollCode's optional shuffle group. It is folded into the checksum but not
  // into the code, because the guard has to cover the whole thing: the first cut
  // checksummed only the three groups this function emits, and a mangling that
  // landed in the shuffle group sailed through it. Measured: every escape in the
  // sweep was exactly that.
  return `${head}-${mid}${owned}${look}${checksum(head + mid + owned + look + seed + extra)}-${seed}`.toUpperCase();
};

/**
 * ONE CHARACTER THAT SAYS "THIS ARRIVED WHOLE".
 *
 * Without it a code cannot tell damage from a different composition, because
 * almost every mangling of one valid code is another valid code. Lop four
 * characters off the end and the seed field — the last field of the last group,
 * the only one allowed to vary in length — simply reads as a smaller number:
 * the code opens, cleanly, as somebody else's collage. That is the worst
 * possible failure for a thing whose entire job is to be sent through chat
 * clients that wrap, truncate and autocorrect.
 *
 * TWO characters, from a multiplicative rolling hash rather than a weighted sum.
 * The first cut was `sum += (i + 1) * digit`, mod 36, and it only caught 88.9%
 * of manglings — far worse than the 1-in-36 that "one base-36 character" sounds
 * like. The reason is that 36 is not prime: at any position whose weight shares
 * a factor with 36 (half of them), whole families of single-character changes
 * multiply to 0 and vanish. A multiply-and-mix chain has no such dead positions,
 * and two characters take the residual from 1-in-36 to 1-in-1296.
 *
 * This is an accident detector for chat clients that wrap, truncate and
 * autocorrect. It is not a signature and defends against nobody malicious.
 */
const CHECK_LEN = 2;
const checksum = (body: string): string => {
  let h = 7;
  for (let i = 0; i < body.length; i++) {
    // +1 so a leading run of zeros is not indistinguishable from a shorter body.
    h = (h * 31 + parseInt(body[i], 36) + 1) % 1679616;
  }
  return (h % 36 ** CHECK_LEN).toString(36).padStart(CHECK_LEN, '0');
};

export const decodeRoll = (code: string, extra = ''): Roll | null => {
  const parts = code.trim().toLowerCase().replace(/\s+/g, '').split('-');
  if (parts.length !== 3) return null;
  const [a, b, c] = parts;
  if (a.length < 7 || b.length < 6 || c.length < 1) return null;
  if (!/^[0-9a-z]+$/.test(a + b + c)) return null;
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
    // Pre-shape codes stop at 9; every one of them was drawn with rectangular
    // fragments, which is index 0.
    const pri = b.length >= 10 ? n(b.slice(9, 10)) : 0;
    // Pre-exact-colour codes stop at 10 and the roster index above is all there
    // is. -1 is the sentinel for "not carried", never a colour.
    const rgb = b.length >= 15 ? n(b.slice(10, 15)) : -1;
    // Pre-checksum codes stop at 15 and are taken on trust, exactly as they were
    // when they were minted. Beyond that the trailing characters of the middle
    // group are the guard, and a code that fails it is REFUSED — the whole point
    // is that a damaged code must not open as a different collage.
    // Pre-flag codes stop at 15. Absent means DERIVED, which is what every code
    // minted before this bit existed described: the app's default behaviour.
    const owned = b.length >= 16 ? b[15] === '1' : false;
    // THE LOOK sits between the count-provenance flag and the checksum, so the
    // two generations of this group are told apart by LENGTH: 18 is the
    // pre-look form (15 fields + flag + 2 check characters), 19 carries a look
    // between them. Read by length exactly like every earlier field here — a
    // version character would have had to be present from the first code ever
    // minted to be of any use now, and it was not.
    const hasLook = b.length >= 17 + CHECK_LEN;
    const loi = hasLook ? n(b.slice(16, 17)) : 0;
    const bodyLen = hasLook ? 17 : 16;
    if (b.length >= bodyLen + CHECK_LEN) {
      const body = a + b.slice(0, bodyLen) + c + extra.toLowerCase();
      if (checksum(body) !== b.slice(bodyLen, bodyLen + CHECK_LEN)) return null;
    }
    const seed = n(c);
    const layout = LAYOUT_ORDER[li];
    // A look index this build has no entry for is REFUSED, not defaulted. On
    // the encode side an unknown look is honestly `none`; on the decode side it
    // means the code was minted by a build that knows something this one does
    // not, and opening it as an ungraded collage would be the same silent
    // substitution the layout roster's scar is about — the picture would be
    // wrong in a way the recipient cannot see. Same treatment as `layout`.
    const look = LOOK_IDS[loi];
    const nums = [count, e, ai, g, z, bgi, ari, foi, twi, pri, loi, seed];
    if (!layout || !look || !nums.every(Number.isFinite) || !Number.isFinite(rgb)) return null;
    return {
      layout,
      primitive: PRIMITIVE_ORDER[pri] ?? 'rect',
      // ONE fragment is a composition somebody can actually ask for — the
      // stepper's own floor is 1 — and a floor of 2 here quietly told them their
      // own code said something else.
      count: Math.max(1, count),
      countOwned: owned,
      entropy: Math.min(1, e / 100),
      aspect: ASPECTS[ai] ?? 1,
      gutter: g / 2000,
      zoom: z / 100,
      bg: rgb >= 0 ? hex6(rgb) : BACKGROUNDS[BG_KEYS[bgi] ?? 'void'],
      arrangement: ARRANGEMENT_IDS[ari] ?? 'natural',
      focus: FOCUS_IDS[foi] ?? 'auto',
      twist: TWIST_IDS[twi] ?? 'none',
      look,
      seed,
    };
  } catch {
    return null;
  }
};

/** The 24-bit reading of a CSS colour the app can hold; -1 when unreadable. */
export const colourBits = rgb24;

export const BACKGROUND_SWATCHES = BACKGROUNDS;
