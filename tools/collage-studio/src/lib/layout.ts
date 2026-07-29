import { computeFieldLayout } from '../engine/sdf/sdfLayout';
import { computeStencilLayout } from '../engine/sdf/stencil';
import { 
    generateRects, generateTris, generateVoronoi, generateCircles, generateOctagons 
} from '../engine/geom/primitives';
import { ImageAsset, PrimitiveType, LayoutItem, LayoutMode } from '../types';
import { GENERATOR_BY_ID } from '../engine/geom/generators';
import { gutterPx } from '../engine/geom/poly';

// Four modules (stencil, sandbox, vectorExport, templates) import these THROUGH
// this file. It never re-exported them, so all four were type-errors and
// vectorExport's path builder silently degraded to `any` — on the one export
// path with no test coverage.
export type { LayoutItem, Point } from '../types';

export const createRng = (s: number) => {
  let t = s + 0x6D2B79F5;
  return () => {
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

const jitter = (item: LayoutItem, amount: number, rng: () => number): LayoutItem => {
    const path = item.path.map(p => ({
        x: p.x + (rng() - 0.5) * item.bounds.w * amount * 0.2,
        y: p.y + (rng() - 0.5) * item.bounds.h * amount * 0.2
    }));
    return { ...item, path };
}

export const computeLayout = async (
  W: number,
  H: number,
  count: number,
  rng: () => number,
  mode: LayoutMode,
  gutterPercent: number = 0.005,
  entropy: number = 0.5,
  images: ImageAsset[] = [],
  primitive: PrimitiveType = 'rect',
  t: number = 0,
): Promise<LayoutItem[]> => {

  // THE ROSTER FIRST. A generator id dispatches straight through to
  // `src/engine/geom/generators`; anything else falls through to the five
  // original modes below, unchanged, so every saved project still opens.
  //
  // Dispatching on a REGISTRY rather than extending the switch is deliberate:
  // the old switch named every shape three times (once per branch plus again
  // inside `random`, which re-implemented the whole thing), and adding a mode
  // meant editing four places and forgetting one.
  const spec = GENERATOR_BY_ID[mode];
  if (spec) {
    return spec.run({
      W, H, count, rng,
      gutter: gutterPx(W, H, gutterPercent) * (spec.gutterScale ?? 1),
      entropy, images, t,
    });
  }

  if (mode === 'field') {
      const seedVal = Math.floor(rng() * 100000);
      return computeFieldLayout(W, H, count, seedVal, entropy * 2.0);
  }

  if (mode === 'stencil') {
      const seedVal = Math.floor(rng() * 100000);
      return await computeStencilLayout(W, H, images, count, seedVal);
  }

  let items: LayoutItem[] = [];
  
  if (mode === 'complex') {
      return generateVoronoi(W, H, count, gutterPercent, rng, entropy);
  }
  
  switch (primitive) {
      case 'rect': items = generateRects(W, H, count, gutterPercent, rng); break;
      case 'tri': items = generateTris(W, H, count, gutterPercent, rng); break;
      case 'circle': items = generateCircles(W, H, count, gutterPercent, rng); break;
      case 'octagon': items = generateOctagons(W, H, count, gutterPercent, rng); break;
      case 'random':
          const p = ['rect', 'tri', 'circle', 'octagon'][Math.floor(rng()*4)] as PrimitiveType;
          if(p==='rect') items = generateRects(W, H, count, gutterPercent, rng);
          else if(p==='tri') items = generateTris(W, H, count, gutterPercent, rng);
          else if(p==='circle') items = generateCircles(W, H, count, gutterPercent, rng);
          else items = generateOctagons(W, H, count, gutterPercent, rng);
          break;
      default: items = generateRects(W, H, count, gutterPercent, rng);
  }
  
  if (mode === 'balanced') {
      items = items.map(item => jitter(item, entropy, rng));
  }
  
  return items;
};
