import { AnalysisResult } from './lib/analysis';

export type LayoutMode = 'minimal' | 'balanced' | 'complex' | 'field' | 'stencil';
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
    seed: number;
    aspect: number;
    gutter: number; 
    entropy?: number; 
    resonance?: number; 
  };
  style: {
    background: string;
  };
}

export interface ProjectManifest extends AppState {
  images: {
    id: string;
    storageFilename: string; 
    originalName: string;
    analysis: AnalysisResult;
  }[];
}