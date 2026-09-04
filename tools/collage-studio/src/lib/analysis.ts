// --- ROBUST SCRIPT LOADER ---
export const loadScriptSafe = (src: string): Promise<boolean> => {
  return new Promise((resolve) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve(true); 
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.crossOrigin = 'anonymous'; 
    script.onload = () => resolve(true);
    script.onerror = () => {
      console.warn(`Blocked or failed to load: ${src}`);
      resolve(false); 
    };
    document.body.appendChild(script);
  });
};

// --- DUAL ANALYSIS KERNEL ---
export interface AnalysisResult {
  face: { x: number; y: number } | null;
  energy: { x: number; y: number };
  color: { r: number; g: number; b: number; h: number; s: number; l: number }; // New Color Data
  /**
   * THE REFRAME, COMMITTED — a hand-set anchor in the photograph's own
   * normalised coordinates (lib/reframe.ts), read by `calculateSmartCrop` at
   * the FRONT of the anchor chain. Absent on everything the detector was left
   * to decide, which is why it is optional.
   *
   * DECLARED HERE AND NOT ONLY ON `PhotoLike` because this is the type the
   * three writers serialise: `ProjectManifest.images[].analysis`,
   * `SessionAssetEntry.analysis` and `SvgImageMeta.analysis` are all this
   * interface. An undeclared field would round-trip anyway — `JSON.stringify`
   * does not read types — and that is exactly the problem: the manifest would
   * be carrying something no reader of the type could know was there.
   */
  frame?: { x: number; y: number } | null;
}

export const analyzeImage = async (img: HTMLImageElement, model: any): Promise<AnalysisResult> => {
  const result: AnalysisResult = {
    face: null,
    energy: { x: 0.5, y: 0.5 },
    color: { r: 128, g: 128, b: 128, h: 0, s: 0, l: 0.5 }
  };

  try {
    const MAX_SIZE = 512;
    let scale = 1;
    if (img.width > MAX_SIZE || img.height > MAX_SIZE) {
      scale = Math.min(MAX_SIZE / img.width, MAX_SIZE / img.height);
    }
    const w = Math.floor(img.width * scale);
    const h = Math.floor(img.height * scale);
    
    const canvas = document.createElement('canvas');
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    if (!ctx) return result;
    
    ctx.drawImage(img, 0, 0, w, h);
    
    // 1. AI FACE DETECT
    if (model) {
      try {
        const predictions = await model.estimateFaces(canvas, false);
        if (predictions && predictions.length > 0) {
          const best = predictions.sort((a: any, b: any) => {
            const areaA = (a.bottomRight[0] - a.topLeft[0]) * (a.bottomRight[1] - a.topLeft[1]);
            const areaB = (b.bottomRight[0] - b.topLeft[0]) * (b.bottomRight[1] - b.topLeft[1]);
            return areaB - areaA;
          })[0];
          const cx = (best.topLeft[0] + best.bottomRight[0]) / 2;
          const cy = (best.topLeft[1] + best.bottomRight[1]) / 2;
          result.face = { x: cx / w, y: cy / h };
        }
      } catch (err) {
        console.warn("AI Inference hiccup:", err);
      }
    }

    // 2. ENERGY & COLOR DETECT
    const imgData = ctx.getImageData(0, 0, w, h);
    const data = imgData.data;
    let totalX = 0, totalY = 0, totalE = 0;
    
    let sumR = 0, sumG = 0, sumB = 0, count = 0;
    
    for (let y = 0; y < h; y+=4) {
      for (let x = 0; x < w; x+=4) {
        const i = (y * w + x) * 4;
        const r = data[i]; const g = data[i+1]; const b = data[i+2];
        const bri = (r + g + b) / 3;
        
        // Color Avg
        sumR += r; sumG += g; sumB += b; count++;
        
        // Energy
        const nextI = i + 16; 
        const nextBri = (x < w-4) ? (data[nextI] + data[nextI+1] + data[nextI+2]) / 3 : bri;
        let energy = Math.abs(bri - nextBri);

        const maxC = Math.max(r, g, b);
        const minC = Math.min(r, g, b);
        if (maxC - minC > 40) energy *= 1.5;

        const dx = x - w/2; const dy = y - h/2;
        const dist = Math.sqrt(dx*dx + dy*dy) / (w/1.5);
        energy *= (1.2 - Math.min(1, dist));

        totalX += x * energy;
        totalY += y * energy;
        totalE += energy;
      }
    }
    
    if (totalE > 0) {
      result.energy = { x: (totalX / totalE) / w, y: (totalY / totalE) / h };
    }
    
    // Process Average Color
    if (count > 0) {
        const r = sumR / count;
        const g = sumG / count;
        const b = sumB / count;
        
        // RGB to HSL
        const rNorm = r/255, gNorm = g/255, bNorm = b/255;
        const max = Math.max(rNorm, gNorm, bNorm), min = Math.min(rNorm, gNorm, bNorm);
        let hVal = 0, sVal = 0, lVal = (max + min) / 2;

        if (max !== min) {
            const d = max - min;
            sVal = lVal > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case rNorm: hVal = (gNorm - bNorm) / d + (gNorm < bNorm ? 6 : 0); break;
                case gNorm: hVal = (bNorm - rNorm) / d + 2; break;
                case bNorm: hVal = (rNorm - gNorm) / d + 4; break;
            }
            hVal /= 6;
        }
        
        result.color = { r, g, b, h: hVal, s: sVal, l: lVal };
    }

    return result;

  } catch (e) {
    console.error("Analysis Failed", e);
    return result; 
  }
};