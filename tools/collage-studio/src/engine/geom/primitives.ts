import { LayoutItem, Point } from '../../types';

export const generateRects = (
    width: number, height: number, count: number, 
    gutter: number, rng: () => number
): LayoutItem[] => {
    const g = gutter * width;
    let nodes = [{ x: 0, y: 0, w: width, h: height }];
    let safety = 0;
    while (nodes.length < count && safety < 1000) {
      safety++;
      let idx = -1; let maxScore = -1;
      for(let i=0; i<nodes.length; i++) {
        const score = nodes[i].w * nodes[i].h * (0.5 + rng()); 
        if(score > maxScore) { maxScore=score; idx=i; }
      }
      if(idx === -1) break;
      const p = nodes[idx];
      nodes.splice(idx, 1);
      const isVert = p.w > p.h * (0.8 + rng()*0.4); 
      const split = 0.3 + (rng() * 0.4); 
      if(isVert) {
        const w1 = Math.floor(p.w * split);
        nodes.push({x:p.x, y:p.y, w:w1, h:p.h}, {x:p.x+w1, y:p.y, w:p.w-w1, h:p.h});
      } else {
        const h1 = Math.floor(p.h * split);
        nodes.push({x:p.x, y:p.y, w:p.w, h:h1}, {x:p.x, y:p.y+h1, w:p.w, h:p.h-h1});
      }
    }
    
    return nodes.map((n, i) => ({
      id: `cell-${i}`,
      path: [{x:n.x+g, y:n.y+g}, {x:n.x+n.w-g, y:n.y+g}, {x:n.x+n.w-g, y:n.y+n.h-g}, {x:n.x+g, y:n.y+n.h-g}],
      bounds: {x:n.x+g, y:n.y+g, w:n.w-g*2, h:n.h-g*2}
    }));
};

export const generateTris = (
    width: number, height: number, count: number, 
    gutter: number, rng: () => number
): LayoutItem[] => {
    interface Tri { p1: Point; p2: Point; p3: Point; area: number; }
    const p1 = {x:0, y:0}; const p2 = {x:width, y:0}; const p3 = {x:width, y:height}; const p4 = {x:0, y:height};
    let tris: Tri[] = [{ p1:p1, p2:p2, p3:p3, area: (width*height)/2 }, { p1:p1, p2:p3, p3:p4, area: (width*height)/2 }];
    
    let safety = 0;
    while(tris.length < count && safety < 1000) {
        safety++;
        let idx = -1; let maxA = -1;
        for(let i=0; i<tris.length; i++) { if(tris[i].area * rng() > maxA) { maxA=tris[i].area; idx=i; } }
        if(idx === -1) break;
        const t = tris[idx];
        tris.splice(idx, 1);
        const d12 = (t.p1.x-t.p2.x)**2 + (t.p1.y-t.p2.y)**2;
        const d23 = (t.p2.x-t.p3.x)**2 + (t.p2.y-t.p3.y)**2;
        const d31 = (t.p3.x-t.p1.x)**2 + (t.p3.y-t.p1.y)**2;
        let a, b, c; 
        if(d12 >= d23 && d12 >= d31) { a=t.p1; b=t.p2; c=t.p3; }
        else if(d23 >= d12 && d23 >= d31) { a=t.p2; b=t.p3; c=t.p1; }
        else { a=t.p3; b=t.p1; c=t.p2; }
        const tSplit = 0.4 + rng()*0.2;
        const mid = { x: a.x + (b.x-a.x)*tSplit, y: a.y + (b.y-a.y)*tSplit };
        tris.push({ p1:a, p2:mid, p3:c, area: t.area/2 }, { p1:mid, p2:b, p3:c, area: t.area/2 });
    }
    
    return tris.map((t, i) => {
        const cx = (t.p1.x+t.p2.x+t.p3.x)/3; const cy = (t.p1.y+t.p2.y+t.p3.y)/3;
        const s = 1.0 - (gutter * 4);
        const path = [t.p1, t.p2, t.p3].map(p => ({ x: cx + (p.x-cx)*s, y: cy + (p.y-cy)*s }));
        const xs = path.map(p=>p.x); const ys = path.map(p=>p.y);
        return { id: `cell-${i}`, path, bounds: { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs)-Math.min(...xs), h: Math.max(...ys)-Math.min(...ys) } };
    });
};

export const generateVoronoi = (
    width: number, height: number, count: number, 
    gutter: number, rng: () => number, entropy: number
): LayoutItem[] => {
    let polys: Point[][] = [[{x:0,y:0},{x:width,y:0},{x:width,y:height},{x:0,y:height}]];
    let s=0;
    while(polys.length < count && s < 1000){
      s++;
      const idx = Math.floor(rng()*polys.length);
      const poly = polys[idx];
      const xs=poly.map(p=>p.x); const ys=poly.map(p=>p.y);
      const minX=Math.min(...xs), maxX=Math.max(...xs), minY=Math.min(...ys), maxY=Math.max(...ys);
      const cx = minX + rng()*(maxX-minX); const cy = minY + rng()*(maxY-minY);
      let angle;
      if (entropy < 0.2) { angle = (Math.floor(rng()*2) * Math.PI/2); } else { angle = rng()*Math.PI*2; }
      const dx = Math.cos(angle); const dy = Math.sin(angle);
      const pA: Point[] = [], pB: Point[] = [];
      for(let i=0; i<poly.length; i++){
        const p1=poly[i]; const p2=poly[(i+1)%poly.length];
        const v1 = (p1.x-cx)*(-dy) + (p1.y-cy)*dx; const v2 = (p2.x-cx)*(-dy) + (p2.y-cy)*dx;
        if(v1 >= 0) pA.push(p1); else pB.push(p1);
        if((v1 >= 0 && v2 < 0) || (v1 < 0 && v2 >= 0)){
          const t = v1 / (v1 - v2);
          const mid = { x: p1.x + t*(p2.x-p1.x), y: p1.y + t*(p2.y-p1.y) };
          pA.push(mid); pB.push(mid);
        }
      }
      if(pA.length > 2 && pB.length > 2) { polys.splice(idx, 1, pA, pB); }
    }
    return polys.map((poly, i) => {
      let sx=0, sy=0; poly.forEach(p=>{sx+=p.x; sy+=p.y});
      const cx=sx/poly.length; const cy=sy/poly.length;
      const shrink = 1.0 - (gutter * 4);
      const path = poly.map(p => ({ x: cx + (p.x-cx)*shrink, y: cy + (p.y-cy)*shrink }));
      const xs=path.map(p=>p.x); const ys=path.map(p=>p.y);
      return { id: `cell-${i}`, path, bounds: {x:Math.min(...xs), y:Math.min(...ys), w:Math.max(...xs)-Math.min(...xs), h:Math.max(...ys)-Math.min(...ys)} };
    });
};

export const generateCircles = (
    width: number, height: number, count: number, 
    gutter: number, rng: () => number
): LayoutItem[] => {
    const aspect = width / height;
    const cols = Math.ceil(Math.sqrt(count * aspect));
    const rows = Math.ceil(count / cols);
    const cellW = width / cols;
    const cellH = height / rows;
    const r = Math.min(cellW, cellH) * 0.5 * (1.0 - gutter * 8);
    
    const items: LayoutItem[] = [];
    for (let i = 0; i < count; i++) {
        const c = i % cols;
        const rr = Math.floor(i / cols);
        const cx = (c + 0.5) * cellW;
        const cy = (rr + 0.5) * cellH;
        
        const path: Point[] = [];
        const segments = 32;
        for (let j = 0; j < segments; j++) {
            const angle = (j / segments) * Math.PI * 2;
            path.push({ x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r });
        }
        items.push({
            id: `circle-${i}`,
            path,
            bounds: { x: cx - r, y: cy - r, w: r * 2, h: r * 2 }
        });
    }
    return items;
};

export const generateOctagons = (
    width: number, height: number, count: number, 
    gutter: number, rng: () => number
): LayoutItem[] => {
    const aspect = width / height;
    const cols = Math.ceil(Math.sqrt(count * aspect));
    const rows = Math.ceil(count / cols);
    const cellW = width / cols;
    const cellH = height / rows;
    const r = Math.min(cellW, cellH) * 0.5 * (1.0 - gutter * 8);
    
    const items: LayoutItem[] = [];
    for (let i = 0; i < count; i++) {
        const c = i % cols;
        const rr = Math.floor(i / cols);
        const cx = (c + 0.5) * cellW;
        const cy = (rr + 0.5) * cellH;
        
        const path: Point[] = [];
        const segments = 8;
        const offset = Math.PI / 8;
        for (let j = 0; j < segments; j++) {
            const angle = (j / segments) * Math.PI * 2 + offset;
            path.push({ x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r });
        }
        items.push({
            id: `octagon-${i}`,
            path,
            bounds: { x: cx - r, y: cy - r, w: r * 2, h: r * 2 }
        });
    }
    return items;
};
