// src/engine/color/colorManager.ts

export type ColorProfile = 'sRGB' | 'Display P3' | 'Adobe RGB';
export type SoftProofProfile = 'None' | 'FOGRA39' | 'SWOP' | 'GRACOL' | 'Japan Color';

export interface ColorState {
  inputProfile: ColorProfile;
  displayProfile: ColorProfile;
  softProof: SoftProofProfile;
}

// Simple Matrix-based CMYK simulation for Soft Proofing
// (Real implementation would use LittleCMS WASM with ICC profiles)
const SIMULATION_MATRICES: Record<SoftProofProfile, (r:number, g:number, b:number) => [number, number, number]> = {
  'None': (r, g, b) => [r, g, b],
  
  // Simulated FOGRA39 (Standard Coated) - slightly desaturated, warmer
  'FOGRA39': (r, g, b) => {
    // Naive CMYK conversion and back with gamut clipping simulation
    const k = 1 - Math.max(r/255, g/255, b/255);
    // Simulate ink density limits
    const density = 0.95; 
    return [r * density, g * density * 0.98, b * density * 0.95]; 
  },

  // US Web Coated SWOP v2 - standard magazine print
  'SWOP': (r, g, b) => {
    return [r * 0.92, g * 0.92, b * 0.9];
  },

  'GRACOL': (r, g, b) => {
     return [r * 0.94, g * 0.93, b * 0.91];
  },

  'Japan Color': (r, g, b) => {
     return [r * 0.95, g * 0.90, b * 0.92];
  }
};

export const applySoftProof = (
  ctx: CanvasRenderingContext2D, 
  width: number, 
  height: number, 
  profile: SoftProofProfile
) => {
  if (profile === 'None') return;

  const imgData = ctx.getImageData(0, 0, width, height);
  const data = imgData.data;
  const transform = SIMULATION_MATRICES[profile];

  for (let i = 0; i < data.length; i += 4) {
    const [r, g, b] = transform(data[i], data[i+1], data[i+2]);
    data[i] = r;
    data[i+1] = g;
    data[i+2] = b;
    // Alpha remains same
  }
  
  ctx.putImageData(imgData, 0, 0);
};
