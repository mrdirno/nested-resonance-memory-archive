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
}
