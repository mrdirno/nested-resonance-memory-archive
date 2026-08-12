import type { ArrangementId, FocusId, TwistId } from './lib/composition';
import type { TitleSpec } from './lib/title';
import type { LookId } from './lib/grade';
import type { MoveId } from './lib/motion';
import type { TurnId } from './lib/turn';
import { AnalysisResult } from './lib/analysis';

/**
 * The five original modes. Kept as-is so every saved `.collage` project, every
 * template in localStorage and every deep link still opens exactly as it did.
 */
export type LegacyLayoutMode = 'minimal' | 'balanced' | 'complex' | 'field' | 'stencil';

/**
 * The generative roster (`src/engine/geom/generators`). These ids are the
 * registry keys, and they travel into saved projects — so they are literals
 * here rather than a bare `string`, and renaming one is a breaking change to
 * every project that used it.
 */
export type GeneratorLayoutMode =
  | 'shards' | 'golden' | 'hilbert' | 'slit-scan'
  | 'voronoi' | 'delaunay' | 'mud-crack' | 'apollonian' | 'circle-pack' | 'flow' | 'reaction'
  | 'kaleidoscope' | 'geodesic' | 'flower-of-life' | 'metatron' | 'sri-yantra'
  | 'phyllotaxis' | 'mandala' | 'rosette' | 'quasicrystal'
  | 'penrose' | 'truchet' | 'droste';

export type LayoutMode = LegacyLayoutMode | GeneratorLayoutMode;

/** Fragment shape. Only the two grid-based legacy modes read it — every
 *  generator defines its own cell shape, which is the point of having them. */
export type PrimitiveType = 'rect' | 'tri' | 'circle' | 'octagon' | 'random';

export interface Point { x: number; y: number; }
export interface Rect { x: number; y: number; w: number; h: number; }
export interface LayoutItem { path: Point[]; bounds: Rect; id?: string; }

/** Where an asset came from. Absent on an asset means 'image' (the historical default). */
export type AssetSource = 'image' | 'video';

export interface ImageAsset {
  id: string;
  src: string;
  previewSrc: string;
  originalName?: string;
  width: number;
  height: number;
  analysis: AnalysisResult;
  // --- provenance (optional; every consumer must tolerate their absence) -----
  // NOTE: ProjectManifest below persists only id/storageFilename/originalName/
  // analysis, so these three do NOT survive a .collage save/load round-trip.
  /** 'video' for a frame extracted from a clip. */
  sourceKind?: AssetSource;
  /** Filename of the clip a video frame came from. */
  sourceName?: string;
  /** Seconds into that clip. */
  sourceTime?: number;
  /**
   * Id of the LIVE clip this frame came from — the binding key `Stage` uses to
   * replace this still with moving video. Absent means "this fragment is a
   * photograph and stays still", which is the correct default for every asset
   * the app has ever produced.
   */
  clipId?: string;
}

/**
 * A video the user imported that is still available to PLAY, as opposed to the
 * stills already extracted from it.
 *
 * The object URL is minted and owned by the app (not by the import sheet, which
 * revokes everything it makes): it must outlive the sheet, because the sheet
 * closes the moment frames are committed and the clip has to keep playing for
 * the rest of the session.
 */
export interface LiveClip {
  id: string;
  /** Durable `blob:` URL over the original File. Revoked only by the owner. */
  url: string;
  name: string;
  /** Intrinsic size, used for Stage's decoder pixel-budget admission. */
  width: number;
  height: number;
  durationSec: number;
  /** How many stills were extracted from it — shown in the clip list. */
  frameCount: number;
}

export interface AppState {
  version: string;
  mode: 'simple' | 'advanced';
  layout: {
    mode: LayoutMode;
    primitive: PrimitiveType; 
    count: number;
    /**
     * THE MULTIPLIER on `count`, and the source of `zoom`.
     *
     * `effectiveCount = count * density` and `zoom = 1 + (density - 1) * 0.5`,
     * so a project that saved `count` alone described neither the number of
     * fragments nor the crop it was looking at. It was never persisted — the
     * composition code has always carried it — which meant a saved project at
     * any density but 1 reopened as a different collage. Absent means 1, which
     * is what every project saved before this had no way to say.
     */
    density?: number;
    /**
     * Is `count` a DECISION or a DEFAULT? The app derives the fragment count
     * from the number of sources until somebody takes it over, and the two are
     * indistinguishable once serialised. The composition code has carried this
     * bit since it shipped; a saved project never did, so every project reopened
     * as though its count had been chosen by hand — which then refused to get
     * out of the way of the next import. Absent means "chosen", which is what
     * loading a project has always assumed.
     */
    countOwned?: boolean;
    /**
     * THE RE-DEAL, and the field a byte-identical round trip could not see.
     *
     * `shuffleTrigger` seeds WHICH photograph lands in WHICH fragment, twice
     * over — `createRng(seed + shuffleTrigger)` feeds `assignSources`, and it is
     * passed again as `arrangeBag({ shuffle })`. The composition CODE has always
     * carried it (`rollCode.ts`, folded into the checksum); the project file
     * carried neither direction of it, so pressing Shuffle once before an export
     * produced a file that reopened as a different pairing of the same
     * photographs — the exact silent-wrong-answer this format fails closed to
     * prevent, arriving through the one door nothing was watching.
     * Absent means 0, which is the untouched deal every older project has.
     */
    shuffle?: number;
    seed: number;
    aspect: number;
    gutter: number;
    entropy?: number;
    /** Pre-2026-08 projects: the binary hue sort, stored as a 0..1 slider. */
    resonance?: number; 
    /** Which photo lands in which fragment — see lib/composition.ts. */
    arrangement?: ArrangementId;
    /** What each fragment centres on inside its photo. */
    focus?: FocusId;
    /** How far the picture leans inside its fragment. Absent = square. */
    twist?: TwistId;
    /**
     * THE MOVE — how the picture drifts inside its fragment over time (see
     * lib/motion.ts). Under `layout` rather than `style` because it is
     * geometry: it moves the CROP, exactly as `twist` rotates it and `focus`
     * re-points it. Absent on every project saved before it existed, and absent
     * means `still`, which is what those projects were.
     */
    move?: MoveId;
    /**
     * THE TURN — how often the pictures re-cut to different fragments over the
     * take (see lib/turn.ts). Under `layout` beside `move` because it is the
     * DEAL over time: it re-points which photograph fills which fragment,
     * exactly as `arrangement` decides that at rest. Absent on every project
     * saved before it existed, and absent means `hold`, which is what those
     * projects were — one deal, held.
     */
    turn?: TurnId;
  };
  style: {
    background: string;
    /**
     * THE LOOK — the colour grade over every fragment (see lib/grade.ts). Here
     * rather than under `layout` because it is a colour operation and
     * `background` is its sibling; absent on every project saved before it
     * existed, and absent means `none`, which is what those projects were.
     */
    look?: LookId;
  };
  /**
   * THE TITLE — the caption drawn over the finished collage. Absent on every
   * project saved before it existed, and absent means "no caption", which is
   * exactly what those projects had.
   */
  title?: TitleSpec;
}

export interface ProjectManifest extends AppState {
  images: {
    id: string;
    storageFilename: string;
    originalName: string;
    /** Intrinsic size. Optional: archives written before 2026-08-09 lack it and
     *  `loadProject` falls back to decoding. Present, it skips the decode. */
    width?: number;
    height?: number;
    analysis: AnalysisResult;
  }[];
}