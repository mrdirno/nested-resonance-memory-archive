import { LayoutItem, Point } from '../../types';

const createRng = (s: number) => {
  let t = s + 0x6D2B79F5;
  return () => {
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

const noise2D = (x: number, y: number, seed: number) => {
    const X = Math.floor(x);
    const Y = Math.floor(y);
    const fx = x - X;
    const fy = y - Y;
    const hash = (i: number, j: number) => {
        let h = Math.sin(i * 12.9898 + j * 78.233 + seed) * 43758.5453;
        return h - Math.floor(h);
    };
    const a = hash(X, Y);
    const b = hash(X + 1, Y);
    const c = hash(X, Y + 1);
    const d = hash(X + 1, Y + 1);
    const ux = fx * fx * (3 - 2 * fx);
    const uy = fy * fy * (3 - 2 * fy);
    return a * (1 - ux) + b * ux + (c - a) * uy * (1 - ux) + (d - b) * ux * uy;
};

// Smoother, larger warping with Dynamic Frequency
const getWarpedPos = (x: number, y: number, seed: number, distortion: number, density: number) => {
    // Dynamic Frequency based on Density (Count) + Distortion (Entropy)
    // Base freq 0.003 is good for ~12 items.
    // If we have 50 items, we want tighter waves -> freq 0.01
    // If distortion is high, we want more turbulence -> freq * 2
    
    const freq = 0.003 * Math.sqrt(density) * (1 + distortion * 0.5); 
    
    const n1 = noise2D(x * freq, y * freq, seed);
    
    const angle = n1 * Math.PI * 2; 
    const strength = distortion * 300; 
    
    return {
        x: x + Math.cos(angle) * strength,
        y: y + Math.sin(angle) * strength
    };
};

const getArea = (path: Point[]) => {
    let area = 0;
    for (let i = 0; i < path.length; i++) {
        let j = (i + 1) % path.length;
        area += path[i].x * path[j].y;
        area -= path[j].x * path[i].y;
    }
    return Math.abs(area / 2);
};

export const computeFieldLayout = (
    width: number, 
    height: number, 
    count: number, 
    seed: number, 
    distortion: number
): LayoutItem[] => {
    const rng = createRng(seed);
    const seeds: Point[] = [];
    
    // Use Entropy/Distortion to affect Seed Distribution too
    // High distortion = more clumping/randomness
    // Low distortion = more uniform grid
    
    const cols = Math.ceil(Math.sqrt(count * (width/height)));
    const rows = Math.ceil(count / cols);
    const cw = width / cols;
    const ch = height / rows;
    
    const jitter = 0.5 + (distortion * 0.5); // 0.5 to 1.0 jitter
    
    for(let r=0; r<rows; r++) {
        for(let c=0; c<cols; c++) {
            if(seeds.length >= count) break;
            seeds.push({
                x: (c + 0.5) * cw + (rng()-0.5) * cw * jitter, 
                y: (r + 0.5) * ch + (rng()-0.5) * ch * jitter
            });
        }
    }

    const RES = 4; 
    const gridW = Math.ceil(width/RES) + 1;
    const gridH = Math.ceil(height/RES) + 1;
    const grid = new Int32Array(gridW * gridH);
    
    // Density factor for Noise Scaling
    // Normalize count relative to a "Standard" of 12
    const densityFactor = count / 12;

    for(let y=0; y<gridH; y++) {
        for(let x=0; x<gridW; x++) {
            const px = x * RES;
            const py = y * RES;
            
            // Pass density factor to noise
            const warped = getWarpedPos(px, py, seed, distortion, densityFactor);
            
            let closest = -1;
            let minD = Number.MAX_VALUE;
            
            for(let i=0; i<count; i++) {
                const s = seeds[i];
                const d = (warped.x-s.x)**2 + (warped.y-s.y)**2;
                if(d < minD) { minD = d; closest = i; }
            }
            grid[y*gridW + x] = closest;
        }
    }

    const items: LayoutItem[] = [];
    const minArea = (width * height) / (count * 6); // Relaxed filter to allow smaller flow details

    for(let id=0; id<count; id++) {
        const segments: [Point, Point][] = [];
        for(let y=0; y<gridH-1; y++) {
            for(let x=0; x<gridW-1; x++) {
                const v0 = grid[y*gridW + x] === id ? 1 : 0;
                const v1 = grid[y*gridW + (x+1)] === id ? 1 : 0;
                const v2 = grid[(y+1)*gridW + (x+1)] === id ? 1 : 0;
                const v3 = grid[(y+1)*gridW + x] === id ? 1 : 0;
                
                const caseIdx = (v0<<3) | (v1<<2) | (v2<<1) | v3;
                if(caseIdx === 0 || caseIdx === 15) continue;
                
                const mx = x * RES + RES/2;
                const my = y * RES + RES/2;
                const t = {x: mx, y: y*RES};
                const r = {x: (x+1)*RES, y: my};
                const b = {x: mx, y: (y+1)*RES};
                const l = {x: x*RES, y: my};
                
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
        
        if(segments.length === 0) continue;
        
        const poly: Point[] = [];
        let current = segments.pop();
        if(current) {
            poly.push(current[0]);
            let tail = current[1];
            let iters = 0;
            const maxIters = segments.length + 500;
            while(segments.length > 0 && iters < maxIters) {
                iters++;
                const idx = segments.findIndex(s => Math.abs(s[0].x - tail.x) < 0.1 && Math.abs(s[0].y - tail.y) < 0.1);
                if(idx !== -1) {
                    const seg = segments.splice(idx, 1)[0];
                    poly.push(seg[0]);
                    tail = seg[1];
                } else break;
            }
            poly.push(tail);
        }
        
        const area = getArea(poly);
        if (area < minArea) continue; 
        
        let minX=width, maxX=0, minY=height, maxY=0;
        poly.forEach(p => {
            if(p.x < minX) minX = p.x;
            if(p.x > maxX) maxX = p.x;
            if(p.y < minY) minY = p.y;
            if(p.y > maxY) maxY = p.y;
        });
        
        items.push({
            id: `cell-${id}`,
            path: poly,
            bounds: { x: minX, y: minY, w: maxX-minX, h: maxY-minY }
        });
    }
    
    return items;
};
