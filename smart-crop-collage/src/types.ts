import { AnalysisResult } from './lib/analysis';

export type LayoutMode = 'minimal' | 'balanced' | 'complex';

export interface ImageAsset {
  id: string;
  src: string; // Blob URL usually
  originalName?: string;
  width: number;
  height: number;
  analysis: AnalysisResult;
}

export interface AppState {
  version: string;
  mode: 'simple' | 'advanced';
  layout: {
    mode: LayoutMode;
    count: number;
    seed: number;
    aspect: number;
    gutter: number; // 0.0 to 0.05
  };
  style: {
    background: string;
    // Future: borders, shadows
  };
  // Images are stored separately in the ZIP but referenced here if needed, 
  // though typically we just reconstruct the image pool.
  // For the project file manifest, we might store metadata about images.
}

export interface ProjectManifest extends AppState {
  images: {
    id: string;
    filename: string;
    analysis: AnalysisResult;
  }[];
}
