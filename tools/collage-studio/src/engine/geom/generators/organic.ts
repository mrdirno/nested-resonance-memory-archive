// src/engine/geom/generators/organic.ts
// -----------------------------------------------------------------------------
// ORGANIC STRUCTURE — layouts with no grid anywhere in them.
//
// THE DIAGNOSIS THESE EXIST TO FIX
//   The generators these replace (`generateCircles`, `generateOctagons`) were
//   literally `c = i % cols; r = floor(i / cols)` — a grid loop, twice, differing
//   only in how many segments the ring had. Uniform cell size, uniform spacing,
//   no focal point, and dead margins wherever count did not divide evenly.
//
//   Every generator here is built around SCALE HIERARCHY: one or a few dominant
//   cells, a middle band, and a long tail of small ones. That distribution is
//   what the eye reads as composed rather than tiled, and it is the single
//   biggest reason a collage looks expensive.
// -----------------------------------------------------------------------------

import type { LayoutItem, Point } from '../../../types';
import {
  TAU, emit, clipToHalfPlane, circleRing, voronoiCells, lloydRelax,
  poissonCount, centroid, polygonArea, boundsOf, coverRadius,
} from '../poly';
import type { GenContext } from './types';

// =============================================================================
// VORONOI — the real one
// =============================================================================

/**
 * Blue-noise sites, Lloyd-relaxed a little, then exact Voronoi.
 *
 * `relax` is the expressive dial and it is deliberately kept LOW. Lloyd
 * converges toward a hexagonal lattice, so 6+ iterations would hand back the
 * regularity we are trying to escape. 1-2 passes removes the clumps that make
 * cells wildly uneven while keeping the structure irregular.
 *
 * Density weighting: sites are biased toward a focal point by pulling a share
 * of them inward, so cells near the focus are small and detailed and cells at
 * the edge are large — an automatic centre of interest.
 */
export const voronoi = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const n = Math.max(3, Math.min(400, count));
  let sites = poissonCount(W, H, n, rng);

  // Focal bias: the higher the entropy the more the field is pulled toward one
  // point, producing a strong scale gradient instead of an even mesh.
  const fx = W * (0.28 + rng() * 0.44);
  const fy = H * (0.28 + rng() * 0.44);
  const bias = 0.12 + entropy * 0.42;
  sites = sites.map((p) => {
    const dx = p.x - fx;
    const dy = p.y - fy;
    const d = Math.hypot(dx, dy);
    const cover = coverRadius(W, H, fx, fy);
    // Points closer to the focus get pulled closer still: r' = r * (r/R)^bias
    const k = Math.pow(Math.max(1e-3, d / cover), bias);
    return { x: fx + dx * k, y: fy + dy * k };
  });

  sites = lloydRelax(sites, W, H, entropy < 0.35 ? 2 : 1);
  return emit(voronoiCells(sites, W, H), W, H, gutter, 'vor');
};

// =============================================================================
// DELAUNAY SHATTER
// =============================================================================

/**
 * Real Delaunay triangulation by Bowyer–Watson over a blue-noise point set.
 *
 * Why not the old "shatter"? That one recursively cut a rectangle with random
 * half-planes, so every shard was convex, roughly rectangular and roughly the
 * same size — it looked like a subdivided page, not broken glass. Real breakage
 * makes TRIANGLES that meet at shared vertices, with a long tail of slivers near
 * impact points. Delaunay over density-varied points gives exactly that.
 */
export const delaunay = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;

  // Impact points: density spikes that produce the fine shards of a real break.
  const impacts = 1 + Math.floor(rng() * 3);
  const centres: Point[] = [];
  for (let i = 0; i < impacts; i++) centres.push({ x: rng() * W, y: rng() * H });

  const n = Math.max(6, Math.min(260, Math.round(count * 0.62)));
  const pts: Point[] = poissonCount(W, H, n, rng).map((p) => {
    let best = Infinity;
    let c = centres[0];
    for (const q of centres) {
      const d = Math.hypot(q.x - p.x, q.y - p.y);
      if (d < best) { best = d; c = q; }
    }
    const cover = coverRadius(W, H, c.x, c.y);
    const k = Math.pow(Math.max(1e-3, best / cover), 0.25 + entropy * 0.5);
    return { x: c.x + (p.x - c.x) * k, y: c.y + (p.y - c.y) * k };
  });
  // Corners, so the triangulation actually reaches the frame edges.
  pts.push({ x: 0, y: 0 }, { x: W, y: 0 }, { x: W, y: H }, { x: 0, y: H });

  // ---- Bowyer–Watson ------------------------------------------------------
  type Tri = { a: number; b: number; c: number; cx: number; cy: number; r2: number };
  const P = pts.slice();
  const big = Math.max(W, H) * 12;
  P.push({ x: W / 2 - big, y: H / 2 - big }, { x: W / 2 + big, y: H / 2 - big }, { x: W / 2, y: H / 2 + big });
  const s0 = P.length - 3, s1 = P.length - 2, s2 = P.length - 1;

  const circum = (a: number, b: number, c: number): Tri => {
    const A = P[a], B = P[b], C = P[c];
    const d = 2 * (A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y));
    if (Math.abs(d) < 1e-12) return { a, b, c, cx: 0, cy: 0, r2: Infinity };
    const a2 = A.x * A.x + A.y * A.y;
    const b2 = B.x * B.x + B.y * B.y;
    const c2 = C.x * C.x + C.y * C.y;
    const cx = (a2 * (B.y - C.y) + b2 * (C.y - A.y) + c2 * (A.y - B.y)) / d;
    const cy = (a2 * (C.x - B.x) + b2 * (A.x - C.x) + c2 * (B.x - A.x)) / d;
    return { a, b, c, cx, cy, r2: (A.x - cx) ** 2 + (A.y - cy) ** 2 };
  };

  let tris: Tri[] = [circum(s0, s1, s2)];
  for (let i = 0; i < P.length - 3; i++) {
    const p = P[i];
    const bad: Tri[] = [];
    const keep: Tri[] = [];
    for (const t of tris) {
      if ((p.x - t.cx) ** 2 + (p.y - t.cy) ** 2 < t.r2) bad.push(t); else keep.push(t);
    }
    // The cavity boundary: edges belonging to exactly one bad triangle.
    const edges: [number, number][] = [];
    for (const t of bad) {
      for (const e of [[t.a, t.b], [t.b, t.c], [t.c, t.a]] as [number, number][]) {
        const k = edges.findIndex((f) => (f[0] === e[1] && f[1] === e[0]) || (f[0] === e[0] && f[1] === e[1]));
        if (k >= 0) edges.splice(k, 1); else edges.push(e);
      }
    }
    tris = keep;
    for (const [u, v] of edges) tris.push(circum(u, v, i));
  }

  const rings: Point[][] = [];
  for (const t of tris) {
    if (t.a >= s0 || t.b >= s0 || t.c >= s0) continue;     // touches the super-triangle
    rings.push([P[t.a], P[t.b], P[t.c]]);
  }
  return emit(rings, W, H, gutter, 'dln');
};

// =============================================================================
// APOLLONIAN GASKET
// =============================================================================

/**
 * Recursive tangent-circle packing via Descartes' Circle Theorem:
 *   (k1+k2+k3+k4)^2 = 2(k1^2+k2^2+k3^2+k4^2),  k = 1/r  (curvature)
 * solved for the fourth curvature:
 *   k4 = k1+k2+k3 +- 2*sqrt(k1k2 + k2k3 + k3k1)
 * and the centre from the same identity over COMPLEX co-ordinates z*k.
 *
 * This is the most extreme scale hierarchy available in a plane packing — the
 * circle sizes follow a power law with no upper or lower plateau — which is
 * exactly what makes it striking. A grid of circles is the opposite of this.
 */
export const apollonian = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  // Reach the corners: a gasket inscribed in the safe circle leaves four black
  // corners, which on a collage reads as a mistake rather than as negative space.
  const R = coverRadius(W, H, cx, cy) * 1.02;

  /** `out` = the enclosing circle (negative curvature, everything is inside it). */
  interface C { x: number; y: number; r: number; out?: boolean }

  // THE CANONICAL SEED (-1, 2, 2, 3), scaled by R.
  //   outer  r = R          (enclosing)
  //   two    r = R/2        side by side, each internally tangent to outer
  //   two    r = R/3        above and below, tangent to all three
  // Descartes confirms it: k4 = -1 + 2 + 2 ± 2*sqrt(-2 + 4 - 2) = 3, exactly.
  // Hand-rolling an asymmetric seed (the previous attempt) makes a gasket that
  // is valid for two levels and then starves — which is why it drew 21 circles
  // for a request of 48 and left most of the frame empty.
  const spin = rng() * TAU;
  const rot = (x: number, y: number): C => {
    const c = Math.cos(spin), s = Math.sin(spin);
    return { x: cx + x * c - y * s, y: cy + x * s + y * c, r: 0 };
  };
  const at = (x: number, y: number, r: number): C => ({ ...rot(x, y), r });

  const outer: C = { x: cx, y: cy, r: R, out: true };
  const seeds: C[] = [
    at(-R / 2, 0, R / 2),
    at(R / 2, 0, R / 2),
    at(0, (2 * R) / 3, R / 3),
    at(0, -(2 * R) / 3, R / 3),
  ];

  /**
   * Given three mutually tangent circles, find the fourth.
   * Descartes gives the RADIUS; the CENTRE is then pure trilateration — the new
   * centre is a known distance from each of the three, and two distance
   * constraints already pin it to two candidate points. Picking between them by
   * checking the third constraint is exact and, unlike the complex-square-root
   * form of Descartes, has no branch-cut sign to get wrong.
   */
  const fourth = (a: C, b: C, c: C): C | null => {
    const k = (z: C) => (z.out ? -1 : 1) / z.r;
    const ka = k(a), kb = k(b), kc = k(c);
    const disc = ka * kb + kb * kc + kc * ka;
    if (disc < -1e-12) return null;
    const k4 = ka + kb + kc + 2 * Math.sqrt(Math.max(0, disc));
    if (!isFinite(k4) || k4 <= 1e-9) return null;
    const r4 = 1 / k4;
    if (r4 < Math.min(W, H) * 0.004) return null;

    // Required centre distance to each parent, by tangency type.
    const dist = (z: C) => (z.out ? Math.abs(z.r - r4) : z.r + r4);
    const da = dist(a), db = dist(b), dc = dist(c);

    // Two-circle intersection about a and b.
    const ex = b.x - a.x, ey = b.y - a.y;
    const d = Math.hypot(ex, ey);
    if (d < 1e-9 || d > da + db || d < Math.abs(da - db)) return null;
    const m = (da * da - db * db + d * d) / (2 * d);
    const h2 = da * da - m * m;
    if (h2 < 0) return null;
    const h = Math.sqrt(h2);
    const mx = a.x + (ex * m) / d, my = a.y + (ey * m) / d;
    const rx = -(ey / d) * h, ry = (ex / d) * h;

    let best: C | null = null;
    let bestErr = Infinity;
    for (const s of [1, -1]) {
      const p: C = { x: mx + s * rx, y: my + s * ry, r: r4 };
      const err = Math.abs(Math.hypot(p.x - c.x, p.y - c.y) - dc);
      if (err < bestErr) { bestErr = err; best = p; }
    }
    // Reject if the third tangency is not actually satisfied — that means this
    // triple has no valid mutually-tangent fourth on this branch.
    return best && bestErr < Math.max(0.6, r4 * 0.06) ? best : null;
  };

  const circles: C[] = [...seeds];
  const seen = new Set<string>();
  const key = (c: C) => `${c.x.toFixed(1)}:${c.y.toFixed(1)}:${c.r.toFixed(1)}`;
  for (const c of circles) seen.add(key(c));

  // BREADTH-first, so the gasket fills evenly at each scale instead of driving
  // one branch down to invisibility while the rest of the frame stays empty.
  let frontier: [C, C, C][] = [
    [outer, seeds[0], seeds[2]], [outer, seeds[0], seeds[3]],
    [outer, seeds[1], seeds[2]], [outer, seeds[1], seeds[3]],
    [seeds[0], seeds[1], seeds[2]], [seeds[0], seeds[1], seeds[3]],
  ];
  // Overshoot the request: the gasket's tail is tiny circles that the gutter
  // will drop anyway, so stopping exactly at `count` under-delivers.
  const target = Math.max(8, Math.min(700, Math.round(count * 1.5)));
  let guard = 0;
  while (frontier.length && circles.length < target && guard++ < 40) {
    const next: [C, C, C][] = [];
    for (const [a, b, c] of frontier) {
      if (circles.length >= target) break;
      const n = fourth(a, b, c);
      if (!n) continue;
      const kk = key(n);
      if (seen.has(kk)) continue;
      if (Math.hypot(n.x - cx, n.y - cy) + n.r > R * 1.03) continue;
      seen.add(kk);
      circles.push(n);
      next.push([a, b, n], [b, c, n], [c, a, n]);
    }
    frontier = next;
  }

  const rings = circles
    .sort((p, q) => q.r - p.r)
    .slice(0, Math.max(4, count))
    .map((c) => circleRing(c.x, c.y, c.r));
  return emit(rings, W, H, gutter, 'apo');
};

// =============================================================================
// CIRCLE PACKING (front-advancing, varied radii)
// =============================================================================

/**
 * Random-insert packing with a POWER-LAW radius distribution: try large first,
 * shrink on failure. That order is what produces the "few big, many small" look
 * — try-small-first fills the plane evenly and you are back to a grid with
 * rounded corners.
 */
export const circlePack = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const target = Math.max(4, Math.min(500, count));

  // A TANGENT packing, not a scatter of discs.
  //
  // Random-insert-and-reject (the obvious implementation, and the one this
  // replaces) leaves large gaps between circles because nothing ever grows to
  // meet its neighbour — it drew 40 circles for a request of 48 and the frame
  // read as mostly background. The fix is to decouple the two problems: choose
  // WHERE first (blue noise), then choose HOW BIG by growing each circle until
  // it touches. Every circle then kisses at least one other, which is what
  // makes a packing look like a packing.
  const sites = poissonCount(W, H, target, rng);

  // Per-site growth weight: a power-law spread so the sizes are not all equal.
  // Low entropy -> a few dominant discs; high entropy -> an even foam.
  const power = 2.4 - entropy * 1.6;
  const weight = sites.map(() => 0.45 + Math.pow(rng(), power) * 1.55);

  const radii = sites.map((p, i) => {
    // NO WALL LIMIT. Clamping radius to the distance from the frame edge shrank
    // every border circle to nothing and ringed the collage in dead space —
    // measured at 35% coverage. `emit` clips to the frame anyway, so letting
    // circles run off the edge is both free and correct: it is what gives the
    // packing edge-to-edge bleed instead of a polite inset margin.
    let r = Infinity;
    for (let j = 0; j < sites.length; j++) {
      if (j === i) continue;
      const q = sites[j];
      const d = Math.hypot(q.x - p.x, q.y - p.y);
      // Split the gap in proportion to the two weights, so a "heavy" site wins
      // room from a light neighbour instead of both settling at exactly d/2
      // (which is a Voronoi-like even foam and, again, one single scale).
      const share = weight[i] / (weight[i] + weight[j]);
      r = Math.min(r, d * share);
    }
    return r;
  });

  // A LITTLE OVERLAP. Tangent discs are mathematically tidy and, on a collage,
  // read as a sparse scatter — even a perfect packing leaves ~10% of the plane
  // between circles and a varied one leaves far more. Letting each disc grow
  // past tangency turns the layout into overlapping paper cut-outs, which is
  // both a real collage idiom and how the frame actually gets covered. Later
  // cells paint over earlier ones, so the overlap reads as layering.
  const overlap = 1.10 + entropy * 0.28;
  const placed = sites
    .map((p, i) => ({ x: p.x, y: p.y, r: radii[i] * overlap }))
    .filter((c) => c.r > Math.min(W, H) * 0.006);

  // FILL THE GAPS. Even a perfect tangent packing of equal discs tops out near
  // 90% coverage, and one with varied radii sits far below that — measured at
  // 44%, which on a collage reads as a sparse scatter on black rather than as a
  // packing. Dropping progressively smaller discs into the interstices is what
  // every real packing (and every Apollonian gasket) does, and it is also where
  // the scale hierarchy comes from.
  const minR = Math.min(W, H) * 0.006;
  const cap = Math.round(target * 1.8);
  let tries = 0;
  while (placed.length < cap && tries++ < cap * 60) {
    const x = rng() * W;
    const y = rng() * H;
    // Largest disc that fits here without overlapping anything already placed.
    let r = Math.min(W, H) * 0.5;
    for (const c of placed) {
      r = Math.min(r, Math.hypot(c.x - x, c.y - y) - c.r);
      if (r <= minR) break;
    }
    if (r > minR) placed.push({ x, y, r: r * (0.94 + rng() * 0.06) });
  }

  return emit(placed.map((c) => circleRing(c.x, c.y, c.r)), W, H, gutter, 'pak');
};

// =============================================================================
// MUD CRACK / CRAZE
// =============================================================================

/**
 * Sequential crack propagation. A real drying crack does NOT branch at random —
 * it propagates until it meets an existing crack and stops there, forming a
 * T-JUNCTION. That single rule is why mud, glaze and old paint all produce the
 * same distinctive irregular-but-not-chaotic cell structure, and it is exactly
 * what recursive random splitting cannot imitate.
 *
 * Implemented by splitting the CELL a crack starts in, always along a line
 * through a point inside it — so the new edge terminates on the cell walls,
 * which IS the T-junction rule, expressed in polygon terms.
 */
export const mudCrack = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  let cells: Point[][] = [[{ x: 0, y: 0 }, { x: W, y: 0 }, { x: W, y: H }, { x: 0, y: H }]];
  const target = Math.max(2, Math.min(400, count));

  let guard = 0;
  let stuck = 0;
  while (cells.length < target && guard++ < target * 30) {
    // Crack the LARGEST cell — drying stress concentrates in the biggest
    // unrelieved area, which is why mud cells trend toward equal size while
    // staying irregular in shape.
    let bi = 0, ba = -1;
    for (let i = 0; i < cells.length; i++) {
      const a = polygonArea(cells[i]) * (0.75 + rng() * 0.5);
      if (a > ba) { ba = a; bi = i; }
    }
    const cell = cells[bi];
    const c = centroid(cell);
    const b = boundsOf(cell);
    // Skip, never abandon — see `shards`. Landing on an unsplittable cell says
    // nothing about the cells that are still splittable.
    if (b.w < 8 || b.h < 8) { if (++stuck > 40) break; continue; }
    stuck = 0;

    // The crack passes near the centroid, perpendicular-ish to the long axis:
    // cracks relieve the greatest stress, which runs across the widest span.
    const longAxis = b.w >= b.h ? 0 : Math.PI / 2;
    const ang = longAxis + Math.PI / 2 + (rng() - 0.5) * (0.5 + entropy * 1.6);
    const off = (rng() - 0.5) * Math.min(b.w, b.h) * 0.34 * (0.4 + entropy);
    const a = { x: c.x + Math.cos(ang + Math.PI / 2) * off, y: c.y + Math.sin(ang + Math.PI / 2) * off };
    const n = { x: Math.cos(ang), y: Math.sin(ang) };

    const p = clipToHalfPlane(cell, a, n);
    const q = clipToHalfPlane(cell, a, { x: -n.x, y: -n.y });
    if (p.length >= 3 && q.length >= 3) cells.splice(bi, 1, p, q);
    else if (++stuck > 40) break;
  }
  return emit(cells, W, H, gutter, 'mud');
};

// =============================================================================
// FLOW FIELD — the rebuilt "Flow"
// =============================================================================

/**
 * The old `field` mode drifted fragments along a vector field but kept them as
 * separate blobs, so it read as scattered rather than composed. This version
 * ADVECTS the Voronoi SITES through a curl-noise field and re-tessellates, so
 * the cells themselves stretch and shear along the flow — the whole frame moves
 * as one fabric.
 *
 * Curl noise (the perpendicular of a scalar potential's gradient) is
 * divergence-free, which means the flow neither piles points up nor tears holes
 * — the property that makes it look like a fluid instead of a wind.
 */
export const flowField = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy, t = 0 } = ctx;
  const n = Math.max(4, Math.min(400, count));
  const sites = poissonCount(W, H, n, rng);

  // A few octaves of cheap value noise as the potential.
  const seed = rng() * 1000;
  const hash = (x: number, y: number): number => {
    const s = Math.sin(x * 127.1 + y * 311.7 + seed) * 43758.5453;
    return s - Math.floor(s);
  };
  const smooth = (x: number, y: number): number => {
    const xi = Math.floor(x), yi = Math.floor(y);
    const xf = x - xi, yf = y - yi;
    const u = xf * xf * (3 - 2 * xf);
    const v = yf * yf * (3 - 2 * yf);
    const a = hash(xi, yi), b = hash(xi + 1, yi);
    const c = hash(xi, yi + 1), d = hash(xi + 1, yi + 1);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  };
  const potential = (x: number, y: number): number => {
    const s = 3.2 / Math.min(W, H) * 100;
    return smooth(x * s * 0.01, y * s * 0.01 + t * 2) * 1.0
         + smooth(x * s * 0.021, y * s * 0.021) * 0.5;
  };

  const strength = Math.min(W, H) * (0.08 + entropy * 0.30);
  const steps = 14;
  const advected = sites.map((p) => {
    let x = p.x, y = p.y;
    const h = Math.min(W, H) * 0.01;
    for (let i = 0; i < steps; i++) {
      // curl of a 2D scalar potential = (dP/dy, -dP/dx): divergence free.
      const dx = (potential(x, y + h) - potential(x, y - h)) / (2 * h);
      const dy = -(potential(x + h, y) - potential(x - h, y)) / (2 * h);
      const m = Math.hypot(dx, dy) || 1;
      x += (dx / m) * (strength / steps);
      y += (dy / m) * (strength / steps);
    }
    return { x, y };
  });
  return emit(voronoiCells(advected, W, H), W, H, gutter, 'flw');
};

// =============================================================================
// REACTION–DIFFUSION
// =============================================================================

/**
 * Gray–Scott on a coarse grid, then the cells are the Voronoi of the local
 * maxima of the V concentration. Running RD to a real pattern needs thousands
 * of steps on a fine grid, which is far too slow here — but a coarse grid run
 * for a few hundred steps already produces the characteristic coral/spot
 * topology, and it is the TOPOLOGY (irregular blobs of similar size with
 * organic spacing) that the layout consumes.
 */
export const reactionDiffusion = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const gw = 96;
  const gh = Math.max(24, Math.round((gw * H) / W));
  const size = gw * gh;
  const U = new Float32Array(size).fill(1);
  const V = new Float32Array(size).fill(0);

  // Seeds of V start the instability; without them the system stays uniform.
  for (let i = 0; i < 24; i++) {
    const x = Math.floor(rng() * gw);
    const y = Math.floor(rng() * gh);
    for (let dy = -2; dy <= 2; dy++) {
      for (let dx = -2; dx <= 2; dx++) {
        const xx = (x + dx + gw) % gw;
        const yy = (y + dy + gh) % gh;
        V[yy * gw + xx] = 1;
      }
    }
  }

  // Feed/kill in the "coral / mitosis" band — the regime with round blobs.
  const F = 0.030 + entropy * 0.020;
  const K = 0.060 + entropy * 0.003;
  const dU = 0.16, dV = 0.08;
  const U2 = new Float32Array(size);
  const V2 = new Float32Array(size);

  for (let step = 0; step < 340; step++) {
    for (let y = 0; y < gh; y++) {
      for (let x = 0; x < gw; x++) {
        const i = y * gw + x;
        const l = y * gw + ((x - 1 + gw) % gw);
        const r = y * gw + ((x + 1) % gw);
        const u = ((y - 1 + gh) % gh) * gw + x;
        const d = ((y + 1) % gh) * gw + x;
        const lapU = U[l] + U[r] + U[u] + U[d] - 4 * U[i];
        const lapV = V[l] + V[r] + V[u] + V[d] - 4 * V[i];
        const uvv = U[i] * V[i] * V[i];
        U2[i] = U[i] + dU * lapU - uvv + F * (1 - U[i]);
        V2[i] = V[i] + dV * lapV + uvv - (F + K) * V[i];
      }
    }
    U.set(U2); V.set(V2);
  }

  // Local maxima of V become the sites.
  const sites: Point[] = [];
  for (let y = 1; y < gh - 1; y++) {
    for (let x = 1; x < gw - 1; x++) {
      const i = y * gw + x;
      const v = V[i];
      if (v < 0.18) continue;
      if (v >= V[i - 1] && v >= V[i + 1] && v >= V[i - gw] && v >= V[i + gw]) {
        sites.push({ x: (x / gw) * W, y: (y / gh) * H });
      }
    }
  }
  // RD decides its own blob count; top up or thin out toward the request.
  const target = Math.max(4, Math.min(400, count));
  while (sites.length > target) sites.splice(Math.floor(rng() * sites.length), 1);
  while (sites.length < target) sites.push({ x: rng() * W, y: rng() * H });
  if (sites.length < 3) return voronoi(ctx);
  return emit(voronoiCells(sites, W, H), W, H, gutter, 'rxd');
};

export const ORGANIC_GENERATORS = {
  voronoi, delaunay, apollonian, circlePack, mudCrack, flowField, reactionDiffusion,
};
