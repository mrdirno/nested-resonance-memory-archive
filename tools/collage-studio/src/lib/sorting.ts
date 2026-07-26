import { ImageAsset } from '../types';

export const sortImagesByResonance = (
    images: ImageAsset[], 
    resonance: number // 0.0 to 1.0
): ImageAsset[] => {
    // If resonance is low, we assume the caller wants random/shuffled.
    // But if we are sorting, we sort.
    
    const sorted = [...images].sort((a, b) => {
        const cA = a.analysis?.color || { h: 0, s: 0, l: 0 };
        const cB = b.analysis?.color || { h: 0, s: 0, l: 0 };
        
        // Sort by Hue primarily, then Luminance
        if (Math.abs(cA.h - cB.h) > 0.1) {
            return cA.h - cB.h;
        }
        return cA.l - cB.l;
    });
    
    return sorted;
};
