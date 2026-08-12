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
import { MOVE_IDS, type MoveId } from './motion';
import { TURN_IDS, type TurnId } from './turn';
import { PACE_IDS, type PaceId } from './pace';
import { SYNC_IDS, type SyncId } from './beat';

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
  /**
   * THE MOVE — how the picture drifts inside its fragment over time. See
   * lib/motion.ts.
   *
   * Optional for the same reason `look` is: every Roll built before this field
   * existed is still a valid Roll, and absent means `still`, which is exactly
   * the picture those rolls described.
   */
  move?: MoveId;
  /**
   * THE TURN — how often the pictures move to different fragments, and how.
   * See lib/turn.ts.
   *
   * Optional for the reason `look` and `move` are: every Roll built before this
   * field existed is still a valid Roll, and absent means `hold`, which is
   * exactly the picture those rolls described — one deal, held.
   */
  turn?: TurnId;
  /**
   * THE PACE — how fast the clock the move and the turn are read against runs.
   * See lib/pace.ts.
   *
   * Optional for the reason `look`, `move` and `turn` are: every Roll built
   * before this field existed is still a valid Roll, and absent means `even`,
   * which is the tempo those rolls were written at.
   */
  pace?: PaceId;
  /**
   * THE BEAT — whether the cuts snap to the music's grid. See lib/beat.ts.
   *
   * IN THE CODE, AND NOT IN THE DICE, which is the one place this field breaks
   * step with the four above. It belongs in a code because "these fragments,
   * dealt this way, re-cutting like this, ON THE BEAT" is a picture somebody
   * can rebuild with their own photographs AND THEIR OWN TRACK — the recipe
   * carries the relationship, never the tempo, which is a fact about a file.
   * It is not in `rollDice` because the dice re-deals what the collage LOOKS
   * like, and a roll that silently unsyncs a wall somebody just locked to their
   * music would be changing a relationship to a file the dice cannot see.
   *
   * Optional for the reason the four above are: absent means `off`, which is
   * what every Roll built before this field existed described.
   */
  sync?: SyncId;
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

/**
 * EXPORTED for `lib/dealRoll.ts` — the colour dice draws its arrangement from
 * this same family table rather than carrying a second copy of the lean. It
 * passes `naturalChance: 0`, because a dice whose whole job is colour sorting
 * has no business handing back the unsorted order.
 *
 * The gate still DRAWS at `naturalChance: 0` instead of skipping the branch, so
 * the number of values taken off the stream does not depend on the caller — the
 * seeded-reproduction hazard `lookFor` records, avoided the same way.
 */
export const arrangementFor = (
  layout: LayoutMode,
  rnd: () => number,
  naturalChance = 0.2,
): ArrangementId => {
  if (rnd() < naturalChance) return 'natural';
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
export const focusFor = (rnd: () => number): FocusId => {
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

/**
 * EXPORTED for `lib/dealRoll.ts`, same reason as `arrangementFor`: one family
 * table, two dice. The colour dice lowers `straightChance` because a roll you
 * pressed FOR the crop that comes back straight three times running has not
 * shown you the row — but it does not drop it to zero, because the crop-in cost
 * in the doc comment above is real whichever button asked for the lean.
 */
export const twistFor = (
  layout: LayoutMode,
  rnd: () => number,
  straightChance = 0.58,
): TwistId => {
  if (rnd() < straightChance) return 'none';
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

/**
 * THE MOVE the dice picks.
 *
 * Still most of the time, and by a wider margin than the look is ungraded. A
 * move is the only thing in the roster that changes what the collage IS rather
 * than how it looks — a still becomes a clip — so a dice that animated two
 * rolls in three would stop being a composition roll. 68% still; the rest flat
 * across the five, which over a handful of presses is enough to show the row
 * exists without ever being what you did not ask for.
 */
const moveFor = (rnd: () => number): MoveId => {
  if (rnd() < 0.68) return 'still';
  // Slice past `still` rather than re-rolling, for the reason `lookFor` records:
  // a re-roll draws a variable number of values from the stream and makes the
  // roll depend on how many times it happened to land on index 0.
  return pick(MOVE_IDS.slice(1), rnd);
};

/**
 * THE TURN the dice picks.
 *
 * Held most of the time, and by the widest margin in the roster. A turn is the
 * only thing here that re-cuts the collage — the deal you are looking at stops
 * being the deal — so a dice that turned half its rolls would stop handing back
 * compositions and start handing back sequences. 74% hold; the rest flat across
 * the four, which over a handful of presses shows the row exists without ever
 * being what you did not ask for.
 */
const turnFor = (rnd: () => number): TurnId => {
  if (rnd() < 0.74) return 'hold';
  // Slice past `hold` rather than re-rolling, for the reason `lookFor` records:
  // a re-roll draws a variable number of values from the stream and makes the
  // roll depend on how many times it happened to land on index 0.
  return pick(TURN_IDS.slice(1), rnd);
};

/**
 * THE PACE the dice picks — and the ONLY field in the roster with a gate that
 * depends on what the roll already chose.
 *
 * A pace is not like its neighbours. It cannot change what the collage IS, only
 * how fast it gets there, so it gets the LOOSEST gate here: once the roll has
 * put something on the clock, the tempo is a legitimate part of the surprise.
 * The gates in this file tighten with how much a field changes the picture —
 * 55% none for the look, 68% still for the move, 74% hold for the turn — and
 * this one sits at the other end at 55% even, for the same reason read
 * backwards.
 *
 * AND IT IS NOT ROLLED AT ALL WHEN NOTHING MOVES. A still collage that never
 * re-cuts has no clock to run fast, so a rolled `2x` would be a value in the
 * code that no pixel can express — the dice appearing to have done something it
 * did not. Drawing nothing in that branch is safe here and nowhere else: the
 * pace is drawn LAST, so a branch that skips the stream leaves every earlier
 * draw exactly where it was.
 */
const paceFor = (rnd: () => number, move: MoveId, turn: TurnId): PaceId => {
  if (move === 'still' && turn === 'hold') return 'even';
  if (rnd() < 0.55) return 'even';
  // Slice past `even` rather than re-rolling, for the reason `lookFor` records:
  // a re-roll draws a variable number of values from the stream and makes the
  // roll depend on how many times it happened to land on index 0.
  return pick(PACE_IDS.slice(1), rnd);
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
  const rolled = snapRoll({
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
    // Drawn LAST, after the look, for the third time and the same reason:
    // appending to the end of the stream leaves every earlier draw untouched, so
    // a build with the move rolls the same layout, count, chaos, aspect, gutter,
    // zoom, background, arrangement, focus, seed, twist and look from a given
    // rng as the build before it did.
    move: moveFor(rnd),
    // Drawn LAST, after the move, for the fourth time and the same reason:
    // appending to the end of the stream leaves every earlier draw untouched, so
    // a build with the turn rolls the same layout, count, chaos, aspect, gutter,
    // zoom, background, arrangement, focus, seed, twist, look and move from a
    // given rng as the build before it did.
    turn: turnFor(rnd),
    recipe: recipe?.name,
    // The dice picks a fragment count on purpose, out of the generator's own
    // sane range. That is a decision, so a code minted from it must not be
    // overridden by however many photographs the recipient happens to have.
    countOwned: true,
  });
  // THE PACE, drawn last of all and OUTSIDE the literal, because it is the one
  // field whose gate reads what the roll already decided (`paceFor`) and a
  // property initialiser cannot see its own siblings. Same stream discipline as
  // every field above: appending to the end leaves every earlier draw untouched,
  // so a build with the pace rolls the same everything-else from a given rng as
  // the build before it did.
  return { ...rolled, pace: paceFor(rnd, rolled.move ?? 'still', rolled.turn ?? 'hold') };
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
  /** THE MOVE, as an index. Same honest-element-zero reading as the look: index
   *  zero is `still`, and a move this build does not know about is no move. */
  const mvIdx = MOVE_IDS.indexOf((r.move ?? 'still') as MoveId);
  const move = fw(mvIdx < 0 ? 0 : mvIdx, 1);
  /** THE TURN, as an index. Same honest-element-zero reading as the look and the
   *  move: index zero is `hold`, and a turn this build does not know about is no
   *  turn at all. */
  const tuIdx = TURN_IDS.indexOf((r.turn ?? 'hold') as TurnId);
  const turn = fw(tuIdx < 0 ? 0 : tuIdx, 1);
  /** THE PACE, as an index. Same honest-element-zero reading as the three above:
   *  index zero is `even`, and a pace this build does not know is the tempo the
   *  roster was written at. */
  const paIdx = PACE_IDS.indexOf((r.pace ?? 'even') as PaceId);
  const pace = fw(paIdx < 0 ? 0 : paIdx, 1);
  /** THE BEAT, as an index. Same honest-element-zero reading as the four above:
   *  index zero is `off`, and a sync this build does not know about is a collage
   *  that cuts on its own clock — which is what it will do anyway without the
   *  track the code cannot carry. */
  const syIdx = SYNC_IDS.indexOf((r.sync ?? 'off') as SyncId);
  const sync = fw(syIdx < 0 ? 0 : syIdx, 1);
  // `extra` is whatever a LAYER ABOVE has appended to the code — today that is
  // rollCode's optional shuffle group. It is folded into the checksum but not
  // into the code, because the guard has to cover the whole thing: the first cut
  // checksummed only the three groups this function emits, and a mangling that
  // landed in the shuffle group sailed through it. Measured: every escape in the
  // sweep was exactly that.
  const body = mid + owned + look + move + turn + pace + sync;
  return `${head}-${body}${checksum(head + body + seed + extra)}-${seed}`.toUpperCase();
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

/**
 * EVERY MIDDLE-GROUP LENGTH THIS PROJECT HAS EVER MINTED WITH A CHECKSUM.
 *
 * 15 fixed fields, then one character per generation: `countOwned` (18), THE
 * LOOK (19), THE MOVE (20), THE TURN (21), THE PACE (22). Add a field, ADD its
 * length here — never replace, because every earlier length is a code somebody
 * already has — and the sweeps in tests/unit/{motion,turn,pace}.invariants.mjs
 * will tell you if you forget, because the codec would then refuse its own
 * output.
 */
export const MINTED_GROUP_LENGTHS = new Set([
  16 + CHECK_LEN, 17 + CHECK_LEN, 18 + CHECK_LEN, 19 + CHECK_LEN, 20 + CHECK_LEN,
  21 + CHECK_LEN,
]);

/**
 * THE LENGTH THIS BUILD MINTS — the newest generation, derived rather than
 * written down.
 *
 * Exported because three sibling sweeps (grade, motion, turn) each carried
 * their own literal for it, and adding THE PACE broke all three at once with
 * the same message. A test that pins "the current group is 21 characters" is
 * asserting the right property through the wrong constant: what it means is
 * "one character longer than the generation I am about to rebuild", and that
 * is a fact the codec owns. Add a field, add its length to the set above, and
 * every sweep follows.
 */
export const MINTED_GROUP_MAX = Math.max(...MINTED_GROUP_LENGTHS);
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
    // THE MOVE sits after the look and before the checksum, and is told apart
    // by LENGTH exactly as the look is: 19 is the pre-move form, 20 carries a
    // move. Absent means `still` — a code minted before this feature existed
    // described a collage that did not move, and it still opens as one.
    const hasMove = b.length >= 18 + CHECK_LEN;
    const mvi = hasMove ? n(b.slice(17, 18)) : 0;
    // THE TURN sits after the move and before the checksum, told apart by LENGTH
    // exactly as the move is: 20 is the pre-turn form, 21 carries a turn. The
    // comparison is `>=`, which is the whole back-compatibility rule — an
    // 18/19/20-length group leaves this false, `tui` reads 0, `bodyLen` is
    // unchanged and the checksum is sliced at exactly the offset it always was,
    // so every code ever minted decodes byte-identically.
    const hasTurn = b.length >= 19 + CHECK_LEN;
    const tui = hasTurn ? n(b.slice(18, 19)) : 0;
    // THE PACE sits after the turn and before the checksum, told apart by
    // LENGTH exactly as the turn is, and entering the band by `>=` for exactly
    // the same reason: a 18/19/20/21-length group leaves this false, `pai`
    // reads 0, `bodyLen` is unchanged and the checksum is sliced at the offset
    // it always was — so every code ever minted still decodes byte-identically.
    const hasPace = b.length >= 20 + CHECK_LEN;
    const pai = hasPace ? n(b.slice(19, 20)) : 0;
    // THE BEAT sits after the pace and before the checksum, entering the band by
    // `>=` for exactly the reason the three fields above it do: an
    // 18/19/20/21-length group leaves this false, `syi` reads 0, `bodyLen` is
    // unchanged and the checksum is sliced at the offset it always was — so
    // every code ever minted still decodes byte-identically.
    const hasSync = b.length >= 21 + CHECK_LEN;
    const syi = hasSync ? n(b.slice(20, 21)) : 0;
    const bodyLen = hasSync ? 21 : hasPace ? 20 : hasTurn ? 19 : hasMove ? 18 : hasLook ? 17 : 16;
    if (b.length >= 16) {
      /**
       * A CHECKSUMMED GROUP IS ONE OF THE LENGTHS THIS PROJECT HAS MINTED, OR
       * IT IS REFUSED. Two holes, closed by one comparison.
       *
       * TOO LONG was the scar: the group is read by LENGTH, the checksum is
       * then sliced at a FIXED offset, and every character beyond it was simply
       * ignored — so a code with junk appended validated cleanly. Untidy while
       * there was one checksummed length above the flag form; genuinely
       * dangerous now that there are two and a later field makes a third, at
       * which point "ignore the tail" and "read the next generation" are the
       * same bytes.
       *
       * TOO SHORT is the one the move's own sweep turned up, and it is the
       * worse of the two. `hasLook`/`hasMove` enter the checksummed band BY
       * LENGTH, so lopping two or three characters off a real code drops it
       * BELOW the band — 16 and 17 — where the guard did not run at all and the
       * code opened on trust as somebody else's collage. That is precisely the
       * failure the checksum was added to prevent, arriving through the door
       * that decides whether to look.
       *
       * 16 and 17 are safe to refuse because NO BUILD EVER MINTED THEM. This
       * codec was written long before anything called it — `encodeRoll` and
       * `decodeRoll` were wired to nothing until 2026-08-07 — so the only
       * groups that exist in the wild are the three that shipped with a UI
       * behind them: 18 (the count-provenance flag), 19 (THE LOOK), 20 (THE
       * MOVE). Everything between the trust band and 18 is a truncation.
       *
       * Pre-checksum groups (under 16) are untouched: they were minted with no
       * guard at all and are read exactly as they always have been.
       */
      if (!MINTED_GROUP_LENGTHS.has(b.length)) return null;
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
    // Same treatment as the look and the layout: a move index this build has no
    // entry for means the code was minted by a build that knows something this
    // one does not, and opening it as a still collage would be a silent
    // substitution the recipient cannot see.
    const move = MOVE_IDS[mvi];
    // Same treatment again: a turn index this build has no entry for means the
    // sender knows something this build does not, and opening it as a held deal
    // would substitute a still collage for a moving one, invisibly.
    const turn = TURN_IDS[tui];
    // And again: a pace index this build has no entry for means the sender's
    // build knows a tempo this one does not. Opening it at the roster's own
    // tempo would substitute a different rhythm for the one they sent, which is
    // invisible in a still frame and wrong in every exported second.
    const pace = PACE_IDS[pai];
    // And again, with the sharpest version of the reason: a sync index this
    // build has no entry for means the sender's build knows a way of relating
    // the cuts to the music that this one does not, and the whole point of the
    // field is WHERE the cuts land.
    const sync = SYNC_IDS[syi];
    const nums = [count, e, ai, g, z, bgi, ari, foi, twi, pri, loi, mvi, tui, pai, syi, seed];
    if (!layout || !look || !move || !turn || !pace || !sync
        || !nums.every(Number.isFinite) || !Number.isFinite(rgb)) return null;
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
      move,
      turn,
      pace,
      sync,
      seed,
    };
  } catch {
    return null;
  }
};

/** The 24-bit reading of a CSS colour the app can hold; -1 when unreadable. */
export const colourBits = rgb24;

export const BACKGROUND_SWATCHES = BACKGROUNDS;
