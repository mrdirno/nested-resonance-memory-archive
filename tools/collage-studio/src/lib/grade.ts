// src/lib/grade.ts
// -----------------------------------------------------------------------------
// THE LOOK — a colour grade on the collage, applied by every render path from
// ONE ordered pipeline.
//
// WHY A PIPELINE AND NOT A FILTER STRING
//   Four surfaces produce final pixels here: the still preview
//   (`renderer.renderCanvas`), the live Stage (which is also what both video
//   exporters record), the full-resolution export worker (`render.worker.ts`,
//   an OffscreenCanvas on another THREAD) and the vector export
//   (`engine/color/vectorExport.ts`, which emits SVG and has no canvas at all).
//   Three of those speak CSS filter functions. The fourth cannot: an SVG file
//   that has to open in Inkscape or Illustrator wants real `<filter>`
//   primitives, not a shorthand a browser happens to accept on an element.
//
//   So the grade is not a string. It is an ORDERED LIST OF STEPS, and the two
//   emitters below are both pure functions of that one list. `cssFilter` joins
//   it into a filter string; `svgFilter` maps each step to the primitive the
//   Filter Effects spec defines as its exact equivalent, in the same order,
//   through the same number formatter. There is no second roster, no second
//   ordering and no second rounding — which is the only structural reason to
//   believe the SVG and the JPEG carry the same picture.
//
// THE ORDER IS PART OF THE GRADE
//   CSS filter functions compose left to right, and colour operations do not
//   commute: saturate-then-sepia is a toned photograph, sepia-then-saturate is
//   a loud brown one. The order below is fixed once, here, and both emitters
//   walk it:
//
//       brightness -> contrast -> saturate -> sepia -> hue-rotate
//
//   It reads as a grading desk: set exposure, set the curve, set how much
//   colour there is, tone it, then turn the tone. `cool` is the reason sepia
//   sits after saturate and hue-rotate sits last — the only way to reach a
//   clean cool cast with functions that have no per-channel control is to pull
//   the colour down, tone the near-grey, and rotate the tone across the wheel.
//   Rotating first would take the photograph's own hues with it.
//
// THE sRGB DECISION, WHICH IS THE LOAD-BEARING ONE
//   Canvas evaluates CSS filter functions in sRGB. SVG filters default to
//   `color-interpolation-filters: linearRGB`, so the IDENTICAL primitives with
//   the IDENTICAL numbers produce a visibly different picture in the exported
//   SVG — mid-tones diverge most, which is where photographs live. The emitted
//   `<filter>` therefore carries `color-interpolation-filters="sRGB"`
//   explicitly. That one attribute is what makes the vector export the same
//   grade as the raster rather than a cousin of it; the cost of omitting it is
//   measured as a red proof in tests/unit/grade.invariants.mjs.
//
// THE NO-OP RULE
//   `gradeSteps` drops every step that is an identity, so the `none` look
//   yields ZERO steps, `cssFilter` returns `'none'` and `svgFilter` returns the
//   empty string. Every caller is guarded on that, so an ungraded render runs
//   the instruction stream it always ran, bit for bit — the same guarantee
//   `scaleLayout` gives at k=1, `twistedDest` gives at angle 0 and `planTitle`
//   gives on an empty caption.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------

/**
 * THE ROSTER KEYS.
 *
 * These ids travel: into saved `.collage` projects, into the SVG's
 * JSON_MANIFEST and into the composition code as an INDEX (see
 * `LOOK_IDS`). Renaming one is a breaking change to every project that used
 * it, and REORDERING `LOOK_IDS` silently repoints every code ever minted.
 */
export type LookId =
  | 'none' | 'punch' | 'faded' | 'mono' | 'noir' | 'warm' | 'cool' | 'bleach';

/**
 * A grade, as the five quantities the pipeline understands.
 *
 * Deliberately not "any CSS filter string": a free-form string cannot be
 * mapped to SVG primitives, cannot be swept, and cannot be carried in a code.
 * Five numbers can do all three.
 */
export interface Grade {
  /** Exposure. 1 = unchanged. */
  brightness: number;
  /** The curve. 1 = unchanged. */
  contrast: number;
  /** How much colour there is. 1 = unchanged, 0 = grey. */
  saturate: number;
  /** Tone, 0..1. 0 = untoned. */
  sepia: number;
  /** Degrees around the wheel. 0 = unturned. */
  hue: number;
}

export const NO_GRADE: Grade = { brightness: 1, contrast: 1, saturate: 1, sepia: 0, hue: 0 };

/**
 * THE LOOKS.
 *
 * Eight, not eighty. A grade roster is a taste control, and a picker you have
 * to scroll is a settings screen — the bar here is a single row of chips a
 * thumb can cross in one swipe. Labels are the field's own words (a bleach
 * bypass is a real lab process, not a marketing name), because the people who
 * reach for this know them.
 *
 * `none` is index 0 and must stay there: it is the boot state, the no-op, and
 * what every code minted before this feature existed decodes to.
 */
export const LOOKS: { id: LookId; label: string; title: string; grade: Grade }[] = [
  {
    id: 'none', label: 'NONE',
    title: 'No grade. The photographs as they are.',
    grade: NO_GRADE,
  },
  {
    id: 'punch', label: 'PUNCH',
    title: 'More contrast, more colour. The everyday lift.',
    grade: { brightness: 1.00, contrast: 1.18, saturate: 1.30, sepia: 0, hue: 0 },
  },
  {
    id: 'faded', label: 'FADED',
    title: 'Lifted blacks, low contrast, colour pulled back. A washed print.',
    grade: { brightness: 1.06, contrast: 0.82, saturate: 0.85, sepia: 0.06, hue: 0 },
  },
  {
    id: 'mono', label: 'MONO',
    title: 'Black and white, straight.',
    grade: { brightness: 1.02, contrast: 1.12, saturate: 0, sepia: 0, hue: 0 },
  },
  {
    id: 'noir', label: 'NOIR',
    title: 'Black and white, hard. Deep blacks and a steep curve.',
    grade: { brightness: 0.94, contrast: 1.45, saturate: 0, sepia: 0, hue: 0 },
  },
  {
    id: 'warm', label: 'WARM',
    title: 'Toned warm. Golden hour without the hour.',
    grade: { brightness: 1.03, contrast: 1.05, saturate: 1.35, sepia: 0.30, hue: 0 },
  },
  {
    id: 'cool', label: 'COOL',
    title: 'Toned cool. Blue shadows, night-shoot cast.',
    grade: { brightness: 1.02, contrast: 1.08, saturate: 0.30, sepia: 0.70, hue: 190 },
  },
  {
    id: 'bleach', label: 'BLEACH',
    title: 'Bleach bypass. Colour stripped back, contrast pushed up.',
    grade: { brightness: 1.05, contrast: 1.38, saturate: 0.55, sepia: 0, hue: 0 },
  },
];

/**
 * THE INDEX SPACE, and the ONE list the UI, the dice and the codec all read.
 *
 * Derived from `LOOKS` rather than typed out again: two lists of the same
 * things drift, and this one is load-bearing in a way a UI list is not — the
 * position IS what a composition code carries. APPEND ONLY. The codec spends
 * one base-36 character on it, so the ceiling is 36 entries and the sweep
 * asserts it (a roster that outgrows its field does not clip, it lengthens the
 * group and shifts every later slice — see the `padStart` scar).
 */
export const LOOK_IDS: LookId[] = LOOKS.map((l) => l.id);

const BY_ID: Record<string, Grade> = LOOKS.reduce(
  (acc, l) => { acc[l.id] = l.grade; return acc; },
  {} as Record<string, Grade>,
);

/**
 * The grade for a look, tolerant of a look this build does not have.
 *
 * A project file, a template or a newer code can all name an unknown look, and
 * the honest answer for a grade specifically is NO GRADE: a look is ADDITIVE,
 * so its absence is a real state rather than a plausible-looking neighbour.
 * (Contrast the layout index, where element zero is a completely different
 * construction and substituting it is the scar.)
 */
export const gradeFor = (look: LookRef | null | undefined): Grade => {
  if (look && typeof look === 'object') return snapGrade(look);
  return (look && BY_ID[look]) || NO_GRADE;
};

/**
 * WHAT A SURFACE IS HANDED — a roster id, or the five numbers themselves.
 *
 * THE DESK (below) makes a grade that is not on the roster, so the thing that
 * travels to the four surfaces can no longer be an INDEX into a list of eight.
 * It is either a name they can look up or the grade itself; both are
 * structured-cloneable, which is what lets the second kind cross to the export
 * worker's thread unchanged.
 */
export type LookRef = LookId | Grade;

// =============================================================================
// THE PIPELINE
// =============================================================================

export type StepKind = 'brightness' | 'contrast' | 'saturate' | 'sepia' | 'hueRotate';

export interface GradeStep { kind: StepKind; v: number; }

/** Identity values, per step kind — the thing a step is dropped for being. */
const IDENTITY: Record<StepKind, number> = {
  brightness: 1, contrast: 1, saturate: 1, sepia: 0, hueRotate: 0,
};

/**
 * THE ONE ORDERED PIPELINE. Both emitters are pure functions of this array.
 *
 * Identity steps are dropped rather than emitted as no-ops, which is what makes
 * `none` produce an empty pipeline and every caller's guard exact — and it also
 * keeps a `mono` grade from paying for a sepia matrix it does not use.
 *
 * A non-finite value (NaN from a hand-edited project, Infinity from a corrupt
 * template) is dropped too: an unusable number must not reach a filter string,
 * because `ctx.filter = 'contrast(NaN)'` is silently IGNORED by the canvas and
 * silently APPLIED-as-garbage by nothing — the two paths would disagree, which
 * is the one thing this file exists to prevent.
 */
export const gradeSteps = (g: Grade | null | undefined): GradeStep[] => {
  const src = g || NO_GRADE;
  const out: GradeStep[] = [];
  const push = (kind: StepKind, raw: number) => {
    const v = typeof raw === 'number' && Number.isFinite(raw) ? raw : IDENTITY[kind];
    if (v === IDENTITY[kind]) return;
    out.push({ kind, v });
  };
  push('brightness', src.brightness);
  push('contrast', src.contrast);
  push('saturate', src.saturate);
  push('sepia', src.sepia);
  push('hueRotate', src.hue);
  return out;
};

export const stepsForLook = (look: LookRef | null | undefined): GradeStep[] =>
  gradeSteps(gradeFor(look));

/**
 * ONE number formatter, used by BOTH emitters — and SIX decimal places, which
 * is a correctness decision rather than a taste one.
 *
 * The two emitters do not print the same KIND of number. The CSS string prints
 * the grade's own PARAMETERS (`sepia(0.06)`) and lets the browser derive the
 * matrix at full precision; the SVG prints the DERIVED MATRIX TERMS, because a
 * file that has to open in Inkscape cannot ask a browser for anything. So the
 * formatter's precision only ever bites on the SVG side, and at four decimals
 * it bit: `0.769 - 0.769 * 0.94 = 0.04614` printed as `0.0461`, and the sweep
 * measured the exported SVG landing 5.4e-6 away from the exported JPEG of the
 * same collage. Invisible, and still two different pictures.
 *
 * Six decimals makes it exact rather than close, for a stated reason: every
 * sepia term is a three-decimal constant times the amount, plus a three-decimal
 * constant, so an amount on a two-decimal grid produces a term with at most
 * five decimals. `GRADE_GRID` below is what keeps the roster on that grid, and
 * the sweep asserts both halves — the same shape of argument as the composition
 * code's `snapRoll`: quantising is only lossless if the state is on the grid,
 * so put the state on the grid.
 */
const num = (n: number): string => {
  const r = Math.round(n * 1e6) / 1e6;
  return Object.is(r, -0) ? '0' : String(r);
};

/**
 * The decimal grid every roster grade must sit on for `num` to be lossless.
 * Exported so the sweep can hold the roster to it instead of trusting it.
 */
export const GRADE_GRID = 100;

// =============================================================================
// THE DESK — the eight looks, as four axes anybody can move
// =============================================================================
//
// WHY FOUR AXES AND NOT FIVE SLIDERS
//   `Grade` is five numbers, and the naive desk is five sliders. Two of them —
//   `sepia` and `hue` — are not independent quantities a person has an opinion
//   about; they are the two halves of ONE tonal decision, and the roster already
//   proves it: `warm` is sepia 0.30 with no rotation and `cool` is sepia 0.70
//   rotated to 190deg, which are two points on a single axis running through
//   untoned. A slider marked "hue rotate" over a photograph is a party trick; a
//   slider running COOL -> WARM is the control people actually reach for, and it
//   is the one the roster was already using. So the desk is EXPOSURE, CONTRAST,
//   COLOUR and WARMTH, and `warmth` is bipolar.
//
// THE PROOF THAT THE DESK IS A GENERALISATION AND NOT A REPLACEMENT
//   Every one of the eight roster looks is exactly representable on these four
//   axes, and `gradeFromDesk(deskFromGrade(g))` returns g field-for-field for
//   all eight (`Object.is`, not "close"). That is the invariant that makes the
//   desk safe to open on a graded collage: the first thing a user does is drag
//   ONE axis, and every other axis must leave the picture exactly where the
//   preset put it. A desk that only approximated the roster would silently
//   restate your look the moment you touched it — the same class of defect as
//   `Math.max(0, indexOf(...))` turning "not representable" into element zero.
//
// WHY EVERY DERIVED NUMBER IS SNAPPED, AND WHY THAT IS CORRECTNESS
//   `num` above is exact at six decimals for a stated reason: a sepia term is a
//   three-decimal constant times the amount plus a three-decimal constant, so an
//   amount on the two-decimal `GRADE_GRID` yields at most five decimals. That
//   argument is a property of the ROSTER being hand-written on the grid. The
//   moment a desk computes an amount (warmth 0.1 x 0.6 is 0.06000000000000001
//   in binary floating point) the guarantee is gone, and the cost is not
//   cosmetic: it lands as a difference between the exported SVG and the exported
//   JPEG of the same collage, which is the one thing this file exists to
//   prevent. So the grid is enforced on the way IN — exactly as `snapRoll` does
//   for the composition sliders, and for exactly the same reason: quantising is
//   only lossless if the state is already on the grid.

/** The four axes, as the quantities a person has an opinion about. */
export interface Desk {
  /** Exposure. 1 = as shot. -> `brightness` */
  exposure: number;
  /** The curve. 1 = as shot. -> `contrast` */
  contrast: number;
  /** How much colour there is. 1 = as shot, 0 = grey. -> `saturate` */
  colour: number;
  /** Bipolar tone. 0 = untoned, +1 = fully warm, -1 = fully cool. -> `sepia` + `hue` */
  warmth: number;
}

/** The desk at rest. `gradeFromDesk(NO_DESK)` is `NO_GRADE`, so it is a no-op. */
export const NO_DESK: Desk = { exposure: 1, contrast: 1, colour: 1, warmth: 0 };

/**
 * The two ends of the warmth axis, taken from the roster rather than invented:
 * `warm` IS sepia 0.30 (warmth +0.5) and `cool` IS sepia 0.70 at 190deg
 * (warmth -1). Changing either constant moves two shipped looks, which is why
 * the round-trip invariant is swept rather than assumed.
 */
const WARM_SEPIA = 0.6;
const COOL_SEPIA = 0.7;
const COOL_HUE = 190;

/**
 * THE ROSTER OF AXES — the one list the UI, the codec and the sweep all read.
 *
 * `min`/`max` are the reachable range and `mid` is the value that means "as
 * shot"; the codec's field width is derived from the range (see `diceRoll.ts`),
 * so widening a range here is a change to the code format and the sweep says so.
 */
export const DESK_AXES: { key: keyof Desk; label: string; min: number; max: number; mid: number; hint: string }[] = [
  { key: 'exposure', label: 'EXPOSURE', min: 0.6, max: 1.6, mid: 1, hint: 'Brighter or darker, overall.' },
  { key: 'contrast', label: 'CONTRAST', min: 0.6, max: 1.6, mid: 1, hint: 'How far the darks and lights pull apart.' },
  { key: 'colour',   label: 'COLOUR',   min: 0,   max: 2,   mid: 1, hint: 'All the way down is black and white.' },
  { key: 'warmth',   label: 'WARMTH',   min: -1,  max: 1,   mid: 0, hint: 'Cool blue one way, golden the other.' },
];

const AXIS_BY_KEY = DESK_AXES.reduce((a, x) => { a[x.key] = x; return a; },
  {} as Record<keyof Desk, typeof DESK_AXES[number]>);

/** One value, clamped into its axis and put on the grid. */
const snapAxis = (key: keyof Desk, v: number): number => {
  const ax = AXIS_BY_KEY[key];
  const n = typeof v === 'number' && Number.isFinite(v) ? v : ax.mid;
  const c = Math.max(ax.min, Math.min(ax.max, n));
  return Math.round(c * GRADE_GRID) / GRADE_GRID;
};

/** A desk, clamped and on the grid. Idempotent — the sweep holds it to that. */
export const snapDesk = (d: Desk | null | undefined): Desk => {
  const src = d || NO_DESK;
  return {
    exposure: snapAxis('exposure', src.exposure),
    contrast: snapAxis('contrast', src.contrast),
    colour: snapAxis('colour', src.colour),
    warmth: snapAxis('warmth', src.warmth),
  };
};

/** A grade on the grid. `hue` is whole degrees; the other four are 1/100ths. */
export const snapGrade = (g: Grade | null | undefined): Grade => {
  const src = g || NO_GRADE;
  const q = (n: number, id: number) =>
    (typeof n === 'number' && Number.isFinite(n) ? Math.round(n * GRADE_GRID) / GRADE_GRID : id);
  return {
    brightness: q(src.brightness, 1),
    contrast: q(src.contrast, 1),
    saturate: q(src.saturate, 1),
    sepia: q(src.sepia, 0),
    hue: Number.isFinite(src.hue) ? Math.round(src.hue) : 0,
  };
};

/** The four axes, as the five numbers the pipeline understands. */
export const gradeFromDesk = (d: Desk | null | undefined): Grade => {
  const s = snapDesk(d);
  const w = s.warmth;
  const sepia = w === 0 ? 0
    : Math.round(Math.abs(w) * (w > 0 ? WARM_SEPIA : COOL_SEPIA) * GRADE_GRID) / GRADE_GRID;
  return {
    brightness: s.exposure,
    contrast: s.contrast,
    saturate: s.colour,
    sepia,
    hue: w < 0 && sepia > 0 ? COOL_HUE : 0,
  };
};

/**
 * The five numbers, back to four axes — or `null` when they are not on them.
 *
 * `null` is the honest answer for a grade this desk cannot express (a
 * hand-edited project file toned at 45deg, say). It is NOT reachable from
 * anything this app mints: every grade in the app comes from the roster or from
 * `gradeFromDesk`, and both are total here. Callers seed a desk with
 * `deskForLook`, which falls back to `NO_DESK` rather than guessing.
 */
export const deskFromGrade = (g: Grade | null | undefined): Desk | null => {
  const s = snapGrade(g);
  let warmth: number;
  if (s.sepia <= 0) {
    // No tone at all. A rotation with nothing to rotate is off the axis.
    if (s.hue !== 0) return null;
    warmth = 0;
  } else if (s.hue === 0) {
    warmth = Math.round((s.sepia / WARM_SEPIA) * GRADE_GRID) / GRADE_GRID;
  } else if (s.hue === COOL_HUE) {
    warmth = -(Math.round((s.sepia / COOL_SEPIA) * GRADE_GRID) / GRADE_GRID);
  } else {
    return null;
  }
  const out = { exposure: s.brightness, contrast: s.contrast, colour: s.saturate, warmth };
  // Off-axis by RANGE is as unrepresentable as off-axis by shape: clamping here
  // would return a desk whose grade is a different picture from the one handed in.
  const back = snapDesk(out);
  return (back.exposure === out.exposure && back.contrast === out.contrast
    && back.colour === out.colour && back.warmth === out.warmth) ? back : null;
};

/** The desk a roster look sits at. Total for all eight — asserted in the sweep. */
export const deskForLook = (look: LookId | null | undefined): Desk =>
  deskFromGrade(gradeFor(look)) || NO_DESK;

/** Field-for-field equality, so "is this still the preset" is one call. */
export const sameDesk = (a: Desk | null | undefined, b: Desk | null | undefined): boolean => {
  if (!a || !b) return !a && !b;
  return a.exposure === b.exposure && a.contrast === b.contrast
    && a.colour === b.colour && a.warmth === b.warmth;
};

// =============================================================================
// EMITTER 1 — CANVAS (preview, Stage, export worker)
// =============================================================================

/** The CSS filter functions, in pipeline order. `'none'` for an empty grade. */
export const cssFilterForSteps = (steps: GradeStep[]): string => {
  if (steps.length === 0) return 'none';
  return steps.map((s) => {
    switch (s.kind) {
      case 'brightness': return `brightness(${num(s.v)})`;
      case 'contrast':   return `contrast(${num(s.v)})`;
      case 'saturate':   return `saturate(${num(s.v)})`;
      case 'sepia':      return `sepia(${num(s.v)})`;
      case 'hueRotate':  return `hue-rotate(${num(s.v)}deg)`;
    }
  }).join(' ');
};

/**
 * The canvas filter for a look — `'none'` when there is nothing to do.
 *
 * Callers set this ONCE per frame, after the background fill and before the
 * fragment loop, and put it back to `'none'` before the caption. The grade is a
 * property of the PHOTOGRAPHS, not of the frame around them: the background is
 * a colour the user picked and a caption is not part of the picture.
 */
export const cssFilterFor = (look: LookRef | null | undefined): string =>
  cssFilterForSteps(stepsForLook(look));

/** True when this look draws exactly what an ungraded build draws. */
export const isNoOp = (look: LookRef | null | undefined): boolean =>
  stepsForLook(look).length === 0;

// =============================================================================
// EMITTER 2 — SVG (the vector export)
// =============================================================================

/** The id the emitted filter is referenced by. One per document. */
export const SVG_FILTER_ID = 'look';

/**
 * The sepia matrix, exactly as CSS Filter Effects Level 1 parameterises it.
 *
 * At amount 0 this is the identity matrix by construction (a' = 1 collapses
 * every off-diagonal term to zero and every diagonal term to one), which is why
 * a dropped sepia step and a sepia step of 0 are the same picture rather than
 * nearly the same one. Asserted both ways in the sweep.
 */
const sepiaMatrix = (amount: number): number[] => {
  const a = 1 - amount;
  return [
    0.393 + 0.607 * a, 0.769 - 0.769 * a, 0.189 - 0.189 * a, 0, 0,
    0.349 - 0.349 * a, 0.686 + 0.314 * a, 0.168 - 0.168 * a, 0, 0,
    0.272 - 0.272 * a, 0.534 - 0.534 * a, 0.131 + 0.869 * a, 0, 0,
    0, 0, 0, 1, 0,
  ];
};

/** A linear transfer on the three colour channels, alpha untouched. */
const transfer = (slope: number, intercept: number): string => {
  const at = `type="linear" slope="${num(slope)}"`
    + (intercept === 0 ? '' : ` intercept="${num(intercept)}"`);
  return `<feComponentTransfer>`
    + `<feFuncR ${at}/><feFuncG ${at}/><feFuncB ${at}/>`
    + `</feComponentTransfer>`;
};

/**
 * One step as its spec-defined SVG primitive.
 *
 * No `in` / `result` attributes: an SVG filter primitive with no `in` takes the
 * previous primitive's result (and `SourceGraphic` when it is the first), which
 * is exactly the left-to-right chaining CSS filter functions have. Naming the
 * intermediates would be a second description of an order already fixed above.
 */
const svgPrimitive = (s: GradeStep): string => {
  switch (s.kind) {
    case 'brightness': return transfer(s.v, 0);
    // The CSS spec's own intercept for contrast. Written as the spec writes it.
    case 'contrast':   return transfer(s.v, -(0.5 * s.v) + 0.5);
    case 'saturate':   return `<feColorMatrix type="saturate" values="${num(s.v)}"/>`;
    case 'hueRotate':  return `<feColorMatrix type="hueRotate" values="${num(s.v)}"/>`;
    case 'sepia':      return `<feColorMatrix type="matrix" values="${sepiaMatrix(s.v).map(num).join(' ')}"/>`;
  }
};

/**
 * The `<filter>` element for a look, or `''` when there is nothing to do.
 *
 * `color-interpolation-filters="sRGB"` is the whole reason this agrees with the
 * canvas — see the header. Without it the browser evaluates these primitives in
 * linear light while `ctx.filter` evaluates the identical functions in sRGB,
 * and the exported SVG is a different grade from the exported JPEG of the same
 * collage.
 */
export const svgFilterFor = (look: LookRef | null | undefined, id = SVG_FILTER_ID): string => {
  const steps = stepsForLook(look);
  if (steps.length === 0) return '';
  return `<filter id="${id}" color-interpolation-filters="sRGB" `
    + `x="-10%" y="-10%" width="120%" height="120%">`
    + steps.map(svgPrimitive).join('')
    + `</filter>`;
};

/** The attribute that hangs the filter on the collage group. `''` for no-op. */
export const svgFilterAttrFor = (look: LookRef | null | undefined, id = SVG_FILTER_ID): string =>
  (stepsForLook(look).length === 0 ? '' : ` filter="url(#${id})"`);
