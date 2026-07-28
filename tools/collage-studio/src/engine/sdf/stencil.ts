import { LayoutItem, Point } from '../../lib/layout';
import { ImageAsset } from '../../types';

// Helper: Gaussian Blur kernel (simplified)
const blur = (data: Uint8ClampedArray, w: number, h: number) => {
    // Single pass box blur for speed
    const d2 = new Uint8ClampedArray(data);
    for(let y=1; y<h-1; y++) {
        for(let x=1; x<w-1; x++) {
            const i = (y*w + x)*4;
            let sum = 0;
            // Neighborhood
            sum += data[i] + data[i-4] + data[i+4] + data[i-w*4] + data[i+w*4];
            d2[i] = sum / 5;
        }
    }
    return d2;
};

export const computeStencilLayout = async (
    width: number,
    height: number,
    images: ImageAsset[],
    count: number,
    seed: number
): Promise<LayoutItem[]> => {
    const items: LayoutItem[] = [];
    
    // Canvas for processing
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return [];

    // Process up to 'count' images
    for (let i = 0; i < Math.min(count, images.length); i++) {
        const imgAsset = images[i];
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = imgAsset.previewSrc || imgAsset.src; // Use thumb for speed
        // onerror TOO, or one unreadable image hangs computeStencilLayout
        // forever: setLayoutItems is never called, the Stencil tile lights up
        // and the canvas freezes with nothing logged.
        await new Promise<void>(r => {
            img.onload = () => r();
            img.onerror = () => r();
        });
        if (!img.width) continue;   // decoded nothing — skip, do not divide by 0
        
        // Resize to small processing grid
        const procW = 100;
        const procH = Math.floor(procW * (img.height / img.width));
        
        canvas.width = procW;
        canvas.height = procH;
        ctx.drawImage(img, 0, 0, procW, procH);
        
        const imageData = ctx.getImageData(0, 0, procW, procH);
        const data = imageData.data;
        
        // 1. Luminance Map
        const grid = new Float32Array(procW * procH);
        let minL = 255, maxL = 0;
        for(let j=0; j<data.length; j+=4) {
            const l = (data[j] + data[j+1] + data[j+2]) / 3;
            grid[j/4] = l;
            if(l<minL) minL=l;
            if(l>maxL) maxL=l;
        }
        
        // 2. Threshold (Auto - Midpoint)
        const thresh = (minL + maxL) / 2;
        
        // 3. Marching Squares (Vectorize Blob)
        const path: Point[] = [];
        const segments: [Point, Point][] = [];
        
        for(let y=0; y<procH-1; y++) {
            for(let x=0; x<procW-1; x++) {
                // Invert logic: Bright = Subject? Or Dark?
                // Let's assume Subject is different from Background.
                // Simple variance: Subject is usually "not the edges".
                // Let's stick to Luminance > Threshold.
                const v0 = grid[y*procW+x] > thresh ? 1 : 0;
                const v1 = grid[y*procW+x+1] > thresh ? 1 : 0;
                const v2 = grid[(y+1)*procW+x+1] > thresh ? 1 : 0;
                const v3 = grid[(y+1)*procW+x] > thresh ? 1 : 0;
                
                const caseIdx = (v0<<3) | (v1<<2) | (v2<<1) | v3;
                if(caseIdx === 0 || caseIdx === 15) continue;
                
                // Scale back to Layout Coords
                const sx = width / procW;
                const sy = height / procH; // Wait, height depends on aspect?
                // We want the shape to fit in the container but maintain aspect.
                // The container is 'width' x 'height'.
                // 'procW' x 'procH' is image aspect.
                // We need to map [0..procW] -> [0..width]? No, that stretches.
                // We map [0..procW] -> [targetW]
                
                // Let's normalize points to 0..1 first
                const nx = x / procW;
                const ny = y / procH;
                const nRes = 1 / procW; // approximate step
                
                // Simplified segments (midpoints)
                const t = {x: nx+nRes/2, y: ny};
                const r = {x: nx+nRes, y: ny+nRes/2};
                const b = {x: nx+nRes/2, y: ny+nRes};
                const l = {x: nx, y: ny+nRes/2};
                
                // ... (Marching Squares switch - same as sdfLayout) ...
                // Reusing generic logic:
                switch(caseIdx) {
                    case 1: segments.push([l, b]); break;
                    case 2: segments.push([b, r]); break;
                    case 3: segments.push([l, r]); break;
                    case 4: segments.push([r, t]); break;
                    case 5: segments.push([l, t], [b, r]); break; 
                    case 6: segments.push([b, t]); break;
                    case 7: segments.push([l, t]); break;
                    case 8: segments.push([t, l]); break;
                    case 9: segments.push([t, b]); break;
                    case 10: segments.push([t, r], [l, b]); break; 
                    case 11: segments.push([t, r]); break;
                    case 12: segments.push([r, l]); break;
                    case 13: segments.push([r, b]); break;
                    case 14: segments.push([b, l]); break;
                }
            }
        }
        
        // Chain
        if(segments.length > 0) {
            let current = segments.pop();
            const poly: Point[] = [];
            if(current) {
                poly.push(current[0]);
                let tail = current[1];
                let iters = 0;
                while(segments.length > 0 && iters < 1000) {
                    iters++;
                    const idx = segments.findIndex(s => Math.abs(s[0].x - tail.x) < 0.01 && Math.abs(s[0].y - tail.y) < 0.01);
                    if(idx !== -1) {
                        const seg = segments.splice(idx, 1)[0];
                        poly.push(seg[0]);
                        tail = seg[1];
                    } else break;
                }
                poly.push(tail);
            }
            
            // Map 0..1 poly to Screen Space
            // We stack them or grid them?
            // "Cycle through... using vector shapes".
            // Let's grid them like Balanced mode but with the shape Mask.
            
            // Calculate grid slot
            const cols = Math.ceil(Math.sqrt(count));
            const rows = Math.ceil(count/cols);
            const r = Math.floor(i / cols);
            const c = i % cols;
            
            const cellW = width / cols;
            const cellH = height / rows;
            const cellX = c * cellW;
            const cellY = r * cellH;
            
            // Scale shape to fit cell
            const scaledPoly = poly.map(p => ({
                x: cellX + p.x * cellW,
                y: cellY + p.y * cellH
            }));
            
            // Bounds
            let minX=width, maxX=0, minY=height, maxY=0;
            scaledPoly.forEach(p => {
                if(p.x < minX) minX = p.x;
                if(p.x > maxX) maxX = p.x;
                if(p.y < minY) minY = p.y;
                if(p.y > maxY) maxY = p.y;
            });
            
            items.push({
                id: `cell-${i}`,
                path: scaledPoly,
                bounds: { x: minX, y: minY, w: maxX-minX, h: maxY-minY }
            });
        } else {
            // Fallback if no shape found: Rect
            // ...
        }
    }
    
    return items;
};
