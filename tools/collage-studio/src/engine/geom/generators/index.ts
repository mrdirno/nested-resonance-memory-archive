// src/engine/geom/generators/index.ts
// -----------------------------------------------------------------------------
// THE ROSTER.
//
// One registry, keyed by id. The picker renders it, the dice roll samples it,
// `computeLayout` dispatches through it, and a saved project stores an id from
// it. Adding a generator is one entry here and nothing else — which is the
// property the old `switch (primitive)` chain in layout.ts did not have (it
// named every shape three times, so `random` re-implemented the whole switch).
//
// BLURBS ARE HONEST. The previous roster shipped "Angular voronoi shards, edge
// to edge" over an algorithm that was neither Voronoi nor especially angular.
// A blurb that describes a different algorithm than the code is a bug with a
// long half-life: it outlived three rewrites of the thing it described.
// -----------------------------------------------------------------------------

import type { GeneratorSpec } from './types';
import {
  kaleidoscope, geodesic, flowerOfLife, metatron, sriYantra,
  phyllotaxis, mandala, rosette, quasicrystal, golden,
} from './sacred';
import {
  voronoi, delaunay, apollonian, circlePack, mudCrack, flowField, reactionDiffusion,
} from './organic';
import { penrose, truchet, droste, hilbert, shards, slitScan } from './recursive';

export * from './types';

export const GENERATORS: GeneratorSpec[] = [
  // ---- structure ----------------------------------------------------------
  {
    id: 'shards', name: 'Shards', family: 'structure', run: shards,
    blurb: 'Lopsided fracture splits — big pieces beside small.',
    countRange: [6, 160], cost: 'low',
  },
  {
    id: 'golden', name: 'Golden', family: 'structure', run: golden,
    blurb: 'Squares cut off a 1:φ rectangle, spiralling inward.',
    countRange: [4, 80], cost: 'low',
    quantisedCount: true,
  },
  {
    id: 'hilbert', name: 'Hilbert', family: 'structure', run: hilbert,
    blurb: 'A ribbon on a space-filling curve — neighbours stay near.',
    countRange: [8, 200], cost: 'low',
    deliveredFloor: 15, overshoot: 1.5,
    gutterScale: 0.6,
    coverageFloor: 0.68,
  },
  {
    id: 'slit-scan', name: 'Slit Scan', family: 'motion', run: slitScan,
    blurb: 'Strips that each hold a different moment of the clip.',
    countRange: [8, 200], cost: 'low',
    gutterScale: 0.45,
    coverageFloor: 0.72,
  },

  // ---- organic ------------------------------------------------------------
  {
    id: 'voronoi', name: 'Voronoi', family: 'organic', run: voronoi,
    blurb: 'True Voronoi over blue noise, pulled toward one focus.',
    countRange: [6, 300], cost: 'medium',
  },
  {
    id: 'delaunay', name: 'Delaunay', family: 'organic', run: delaunay,
    blurb: 'Real triangulation, dense at the points of impact.',
    countRange: [10, 240], cost: 'medium',
    deliveredFloor: 14, overshoot: 1.4,
  },
  {
    id: 'mud-crack', name: 'Craze', family: 'organic', run: mudCrack,
    blurb: 'Cracks that stop where they meet — mud, glaze, old paint.',
    countRange: [6, 200], cost: 'low',
  },
  {
    id: 'apollonian', name: 'Gasket', family: 'organic', run: apollonian,
    blurb: 'Tangent circles by Descartes’ theorem, every scale at once.',
    countRange: [10, 220], cost: 'medium',
    quantisedCount: true,
  },
  {
    id: 'circle-pack', name: 'Packing', family: 'organic', run: circlePack,
    blurb: 'Discs dropped largest-first — a real packing, not a grid.',
    countRange: [8, 300], cost: 'medium',
    overshoot: 1.8,
    coverageFloor: 0.60,
  },
  {
    id: 'flow', name: 'Flow', family: 'organic', run: flowField,
    blurb: 'Cells sheared along a divergence-free curl-noise current.',
    countRange: [8, 260], cost: 'medium', animated: true,
  },
  {
    id: 'reaction', name: 'Coral', family: 'organic', run: reactionDiffusion,
    blurb: 'Gray–Scott reaction–diffusion blobs, then tessellated.',
    countRange: [10, 200], cost: 'high',
  },

  // ---- sacred / symmetry --------------------------------------------------
  {
    id: 'kaleidoscope', name: 'Kaleidoscope', family: 'sacred', run: kaleidoscope,
    blurb: 'One wedge, mirrored through Dₙ — real kaleidoscope optics.',
    countRange: [12, 400], cost: 'low', animated: true,
    overshoot: 2.2,
    quantisedCount: true,
  },
  {
    id: 'geodesic', name: 'Geodesic', family: 'sacred', run: geodesic,
    blurb: 'Icosahedron subdivided and re-projected onto a sphere.',
    countRange: [10, 320], cost: 'medium',
    overshoot: 1.05,
    quantisedCount: true,
  },
  {
    id: 'flower-of-life', name: 'Flower of Life', family: 'sacred', run: flowerOfLife,
    blurb: 'Circles at spacing exactly r — the petals close.',
    countRange: [12, 300], cost: 'medium',
    deliveredFloor: 39, overshoot: 3.95,
    quantisedCount: true,
  },
  {
    id: 'metatron', name: 'Metatron', family: 'sacred', run: metatron,
    blurb: '13 centres, every pair joined — the cube’s 78 chords.',
    countRange: [12, 250], cost: 'medium',
    overshoot: 1.55,
    gutterScale: 0.18,
  },
  {
    id: 'sri-yantra', name: 'Sri Yantra', family: 'sacred', run: sriYantra,
    blurb: 'Nine interlocking triangles and the lotus rings.',
    countRange: [16, 200], cost: 'medium',
    overshoot: 1.85,
    gutterScale: 0.5,
  },
  {
    id: 'phyllotaxis', name: 'Sunflower', family: 'sacred', run: phyllotaxis,
    blurb: 'The golden angle, 137.508° — florets that never line up.',
    countRange: [12, 320], cost: 'medium',
  },
  {
    id: 'mandala', name: 'Mandala', family: 'sacred', run: mandala,
    blurb: 'Rings with their own divisors, offset so no spokes form.',
    countRange: [12, 350], cost: 'low',
    deliveredFloor: 20, overshoot: 2.25,
    quantisedCount: true,
  },
  {
    id: 'rosette', name: 'Rosette', family: 'sacred', run: rosette,
    blurb: 'Islamic star chords, extended until they meet.',
    countRange: [12, 250], cost: 'medium',
    deliveredFloor: 15, overshoot: 1.35,
    gutterScale: 0.5,
    quantisedCount: true,
  },
  {
    id: 'quasicrystal', name: 'Quasicrystal', family: 'sacred', run: quasicrystal,
    blurb: 'Odd-numbered plane waves — a pattern that never repeats.',
    countRange: [12, 280], cost: 'medium',
    overshoot: 1.15,
  },

  // ---- recursive / aperiodic ---------------------------------------------
  {
    id: 'penrose', name: 'Penrose', family: 'recursive', run: penrose,
    blurb: 'Robinson deflation by 1/φ — aperiodic, five-fold.',
    countRange: [16, 300], cost: 'medium',
    quantisedCount: true,
  },
  {
    id: 'truchet', name: 'Truchet', family: 'recursive', run: truchet,
    blurb: 'Rotated arc tiles at several scales; paths, not a lattice.',
    countRange: [12, 300], cost: 'low',
    deliveredFloor: 15, overshoot: 3.25,
    quantisedCount: true,
  },
  {
    id: 'droste', name: 'Droste', family: 'recursive', run: droste,
    blurb: 'A logarithmic spiral that maps onto itself — endless zoom.',
    countRange: [12, 260], cost: 'low', animated: true,
    deliveredFloor: 20, overshoot: 2.2,
  },
];

export const GENERATOR_BY_ID: Record<string, GeneratorSpec> =
  Object.fromEntries(GENERATORS.map((g) => [g.id, g]));

export const FAMILY_LABEL: Record<GeneratorSpec['family'], string> = {
  structure: 'Structure',
  organic: 'Organic',
  sacred: 'Sacred',
  recursive: 'Recursive',
  motion: 'Motion',
};

/** Ordered families for the picker. */
export const FAMILIES: GeneratorSpec['family'][] =
  ['structure', 'organic', 'sacred', 'recursive', 'motion'];

export const generatorsInFamily = (f: GeneratorSpec['family']): GeneratorSpec[] =>
  GENERATORS.filter((g) => g.family === f);
