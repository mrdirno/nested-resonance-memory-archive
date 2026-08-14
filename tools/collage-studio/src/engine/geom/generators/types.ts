// src/engine/geom/generators/types.ts
// -----------------------------------------------------------------------------
// The one contract every generative layout in this folder obeys.
//
// A generator is a PURE function of its context. Same context in, same rings
// out — which is what makes a seed shareable, a dice roll reproducible, and a
// video frame at time t renderable offline without replaying the session.
// -----------------------------------------------------------------------------

import type { ImageAsset, LayoutItem } from '../../../types';

export interface GenContext {
  /** Frame size in pixels. Generators fill it edge to edge. */
  W: number;
  H: number;
  /** Requested fragment count. A TARGET, not a guarantee — several
   *  constructions (Penrose deflation, geodesic frequency, golden recursion)
   *  only produce certain counts, and forcing an exact number would break the
   *  construction. Landing within ~20% is the contract. */
  count: number;
  /** Seeded PRNG. The ONLY source of randomness a generator may use —
   *  `Math.random()` here would break seed reproducibility and offline render. */
  rng: () => number;
  /** Constant gutter in PIXELS (already resolved from the app's percent).
   *  Applied by `emit`, so generators emit raw rings and never inset. */
  gutter: number;
  /** 0..1 — how far the construction is allowed to depart from its ideal form.
   *  0 is the textbook figure; 1 is hand-cut and loose. */
  entropy: number;
  /** Normalised time for animated layouts, 0..1 over the take. Still exports
   *  pass 0. Only motion-aware generators read it. */
  t?: number;
  /** Source assets, for the saliency-aware generators. Most ignore them. */
  images?: ImageAsset[];
  /** Per-generator knobs. Absent means "choose from the seed". */
  opts?: {
    folds?: number;
    depth?: number;
    ratio?: number;
    [k: string]: number | string | boolean | undefined;
  };
}

export type Generator = (ctx: GenContext) => LayoutItem[] | Promise<LayoutItem[]>;

/** What a generator advertises about itself to the UI, the dice roll and the
 *  registry. Blurbs are HONEST about the algorithm: a previous blurb called
 *  recursive half-plane splitting "voronoi shards" and the lie outlived the
 *  code it described. */
export interface GeneratorSpec {
  id: string;
  name: string;
  blurb: string;
  /** Grouping for the picker. */
  family: 'structure' | 'sacred' | 'organic' | 'recursive' | 'motion';
  run: Generator;
  /** Cells this construction looks best at. The dice roll samples inside it. */
  countRange: [number, number];
  /** True when the layout changes with `ctx.t` and must be recomputed per frame
   *  during a video render. Costs a relayout per frame, so it is opt-in. */
  animated?: boolean;
  /** Rough cost at count=60, for the dice roll to avoid stacking two heavy
   *  choices on a phone. */
  cost: 'low' | 'medium' | 'high';
  /**
   * Multiplier on the global gutter, default 1.
   *
   * A constant gutter costs a cell in proportion to its PERIMETER, so a figure
   * made of long thin slivers pays far more of itself than one made of compact
   * cells. Measured: at gutter 0 the Metatron arrangement covers 100% of the
   * frame; at the shared 5px gutter it covers 78%, because its chords produce
   * many high-perimeter triangles. The line-arrangement figures also do not
   * NEED much gutter — their own chords already read as the separation.
   *
   * This is a per-construction correction, not a fudge factor: it exists
   * because "constant gutter" is the right rule and this is where its cost is
   * genuinely uneven.
   */
  gutterScale?: number;
  /**
   * Lowest frame coverage this construction is EXPECTED to reach, default 0.85.
   *
   * Most layouts tile and should paint essentially the whole frame; a hole in
   * one is a bug, and measuring coverage is how several were caught. But two
   * families legitimately do not tile, and forcing them to would destroy the
   * thing that makes them what they are:
   *   - circle packings — equal discs cap at 90.7% of the plane and a
   *     size-varied packing sits far below that; the gaps ARE the packing.
   *   - curve ribbons — the background showing between the band's turns is
   *     what makes the path legible as a path.
   * Declaring the floor keeps the check meaningful for everything else instead
   * of training the eye to ignore two permanent warnings.
   */
  coverageFloor?: number;
  /**
   * True when the construction can only produce CERTAIN cell counts.
   *
   * Penrose deflation multiplies by phi^2 per level, geodesic frequency is an
   * integer so faces go 20/80/180/320, an Apollonian gasket adds circles in
   * tangency generations, and golden subdivision halves. Between two admissible
   * counts there is nothing — so "give me 150" can only be answered with the
   * nearest rung, and forcing the exact number would mean truncating the figure
   * (which is what made Penrose cover 18% of the frame in an earlier build).
   *
   * Declared here so the count contract can be judged against what the
   * construction can actually do, instead of quietly missing by 2x and looking
   * like a bug.
   */
  quantisedCount?: boolean;
  /**
   * The fewest cells this construction can produce AT ANY REQUEST — measured,
   * not declared.
   *
   * Present only where it disagrees with `countRange[0]`, and it disagrees for
   * seven of the twenty-three: a Flower of Life emits seven cells per lattice
   * centre and the smallest lattice worth drawing is already 39, whatever you
   * ask for. `countRange[0]` says 12. That number was written as "cells this
   * construction looks best at" and has been read ever since as "cells this
   * construction can do", which are different claims, and the second one is
   * false. Anything reasoning about whether a figure FITS a budget has to read
   * this; anything choosing a pleasing count still reads `countRange`.
   *
   * Measured by `tests/unit/diceRollCount.invariants.mjs` against the real
   * generator over 7 aspects x 4 seeds x 3 entropies, which re-measures these
   * numbers on every run and fails if one has drifted — so this cannot become
   * another comment that outlives the code it describes.
   */
  deliveredFloor?: number;
  /**
   * Delivered cells divided by requested count, median, over the low band — the
   * region a small photo pool forces the dice into.
   *
   * Present only where it exceeds 1. A request is a target (see
   * `quantisedCount`), and for these figures the miss is systematic and upward:
   * ask a circle packing for 20 and get 36. Anything imposing a CEILING on what
   * ends up on the canvas has to aim below it by this much, or it is a ceiling
   * on a number nobody is looking at. Under-delivering figures are deliberately
   * absent rather than recorded as < 1: inflating a request to hit a target is
   * a different decision, and not one anything currently makes.
   */
  overshoot?: number;
}
