// src/engine/geom/generators/recursive.ts
// -----------------------------------------------------------------------------
// RECURSIVE, APERIODIC AND SPACE-FILLING LAYOUTS.
//
// The common thread: structure at more than one scale AT ONCE. A grid has
// exactly one scale, which is why it reads flat no matter how good the source
// images are. Everything here carries at least two, and Penrose and Droste
// carry unboundedly many.
// -----------------------------------------------------------------------------

import type { LayoutItem, Point } from '../../../types';
import {
  TAU, PHI, emit, coverRadius, polygonArea, boundsOf, centroid,
  clipToHalfPlane as clipHalf,
} from '../poly';
import type { GenContext } from './types';

// =============================================================================
// PENROSE P3 (thick / thin rhombi)
// =============================================================================

/**
 * Robinson triangle DEFLATION — the standard and only reliable way to build a
 * Penrose tiling. Two triangle types:
 *   - "fat"  (36-72-72), half of a thick rhomb
 *   - "thin" (108-36-36), half of a thin rhomb
 * and the substitution rules, with phi the golden ratio:
 *   fat(A,B,C)  -> fat(D,C,A) + thin(D,B,C)     where D = B + (A-B)/phi
 *   thin(A,B,C) -> fat(C,D,B)                   where D = A + (B-A)/phi
 *
 * THE SUBTLETY the naive version gets wrong: vertex ORDER carries the tile's
 * chirality. Emit the triangles in the wrong winding and the tiling still looks
 * plausible at a glance but the rhombi stop matching edge-to-edge and the
 * five-fold symmetry never closes. The orders below are the ones that close.
 *
 * Pairs of triangles are merged back into rhombi so the fragments are the
 * recognisable Penrose kites and darts rather than half-tiles.
 */
export const penrose = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const R = coverRadius(W, H, cx, cy) * 1.08;

  type T = { fat: boolean; a: Point; b: Point; c: Point };
  let tris: T[] = [];

  // Seed: 10 fat triangles around the centre — the "sun" configuration, whose
  // deflation limit has exact five-fold symmetry.
  const spin = rng() * TAU;
  for (let i = 0; i < 10; i++) {
    const a0 = spin + ((2 * i - 1) * Math.PI) / 10;
    const a1 = spin + ((2 * i + 1) * Math.PI) / 10;
    let b = { x: cx + Math.cos(a0) * R, y: cy + Math.sin(a0) * R };
    let c = { x: cx + Math.cos(a1) * R, y: cy + Math.sin(a1) * R };
    if (i % 2 === 0) { const t = b; b = c; c = t; }        // alternate chirality
    tris.push({ fat: true, a: { x: cx, y: cy }, b, c });
  }

  const lerp = (p: Point, q: Point, s: number): Point =>
    ({ x: p.x + (q.x - p.x) * s, y: p.y + (q.y - p.y) * s });

  // Each deflation multiplies the tile count by phi^2 ~ 2.618, starting from the
  // 10 seed triangles. Solve for the depth that LANDS on the request instead of
  // over-deflating and trimming: the previous formula reached depth 6 for a
  // request of 48 (~4,000 tiles), then kept the 57 largest — which were all
  // microscopic and scattered, covering 18% of the frame.
  // Merging mirror-pairs into rhombi roughly halves the emitted count, so aim
  // the deflation at 2x the request.
  const depth = Math.max(0, Math.min(8,
    Math.round(Math.log(Math.max(8, count * 2) / 10) / Math.log(PHI * PHI))));
  for (let d = 0; d < depth; d++) {
    const next: T[] = [];
    for (const t of tris) {
      if (t.fat) {
        const p = lerp(t.a, t.b, 1 / PHI);
        next.push({ fat: true, a: t.c, b: p, c: t.b });
        next.push({ fat: false, a: p, b: t.c, c: t.a });
      } else {
        const p = lerp(t.b, t.a, 1 / PHI);
        next.push({ fat: false, a: t.c, b: p, c: t.a });
        next.push({ fat: true, a: t.b, b: t.c, c: p });
      }
    }
    tris = next;
    if (tris.length > 4000) break;
  }

  // Merge mirror-pairs back into rhombi: two triangles sharing the a-c edge.
  const rings: Point[][] = [];
  const used = new Set<number>();
  const k = (p: Point) => `${p.x.toFixed(2)}:${p.y.toFixed(2)}`;
  const index = new Map<string, number[]>();
  tris.forEach((t, i) => {
    const key = `${t.fat ? 'F' : 'T'}|${[k(t.a), k(t.c)].sort().join('|')}`;
    const arr = index.get(key);
    if (arr) arr.push(i); else index.set(key, [i]);
  });
  for (const ids of index.values()) {
    if (ids.length === 2 && !used.has(ids[0]) && !used.has(ids[1])) {
      const [i, j] = ids;
      used.add(i); used.add(j);
      rings.push([tris[i].a, tris[i].b, tris[i].c, tris[j].b]);
    }
  }
  tris.forEach((t, i) => { if (!used.has(i)) rings.push([t.a, t.b, t.c]); });

  // Deflation gives geometric counts (x phi^2 per level); trim toward request.
  const target = Math.max(4, count);
  if (rings.length > target * 1.6) {
    rings.sort((a, b) => polygonArea(b) - polygonArea(a));
    rings.length = Math.round(target * 1.2);
  }
  return emit(rings, W, H, gutter, 'pen');
};

// =============================================================================
// TRUCHET
// =============================================================================

/**
 * Truchet tiles: a square whose contents have no symmetry, placed in a grid at
 * a RANDOM ROTATION. The grid is present but invisible, because the contents
 * connect across tile boundaries into long continuous paths — the eye follows
 * the paths, not the lattice.
 *
 * MULTI-SCALE Truchet is the upgrade that makes it not-a-grid at all: tiles are
 * recursively quartered with some probability before being filled, so the same
 * motif appears at several sizes. That is what breaks the single-scale flatness.
 */
export const truchet = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const rings: Point[][] = [];

  // Each tile emits 3 rings, and every split replaces one tile with four — so
  // the naive `sqrt(count/3)` overshot by an order of magnitude once recursion
  // was in play (594 cells for a request of 48). Account for the expected
  // subdivision multiplier, m = 1/(1 - 3p) for p < 1/3, capped for stability.
  const splitP = Math.min(0.30, 0.14 + entropy * 0.20);
  const mult = 1 / Math.max(0.25, 1 - 3 * splitP);
  // SIZE THE TILE FROM THE AREA, NOT THE LONG EDGE.
  //
  // `max(W, H) / base` gives a tile as wide as the LONGEST side divided by the
  // count — so a 16:9 frame got only two or three rows and delivered a quarter
  // of the requested fragments. The tile count wanted is count/(3 * mult) (three
  // rings per tile, times the expected subdivision), and a square tile covering
  // that many over W x H has side sqrt(W*H / tiles).
  const tiles = Math.max(4, Math.max(4, count) / (3 * mult));
  const cell0 = Math.max(Math.min(W, H) / 12, Math.sqrt((W * H) / tiles));

  /** Points along an arc centred at (ox,oy), inclusive of both ends. */
  const arc = (ox: number, oy: number, r: number, a0: number, a1: number): Point[] => {
    const pts: Point[] = [];
    const N = 14;
    for (let i = 0; i <= N; i++) {
      const a = a0 + (a1 - a0) * (i / N);
      pts.push({ x: ox + Math.cos(a) * r, y: oy + Math.sin(a) * r });
    }
    return pts;
  };

  /**
   * The tile is cut by two quarter-arcs of radius s/2 centred on OPPOSITE
   * corners, giving exactly three regions: two quarter-discs and the band
   * between them. The band is concave and its boundary must be walked in order
   * — corner, arc, corner, edge, corner, arc, corner, edge — or the ring
   * self-intersects and clipping returns rubbish (measured: 34% coverage).
   */
  // Bound the recursion by the BUDGET, not by dropping rings afterwards:
  // every tile emitted is part of the tiling, so removing one leaves a hole
  // (measured: capping the ring list took coverage from 89% to 72%). Refusing
  // to split once the budget is spent keeps the surface complete.
  const ringBudget = Math.round(Math.max(6, count) * 1.6);
  const tile = (x: number, y: number, s: number, depth: number) => {
    if (depth < 3 && rings.length < ringBudget && rng() < splitP && s > Math.min(W, H) * 0.06) {
      const h = s / 2;
      tile(x, y, h, depth + 1); tile(x + h, y, h, depth + 1);
      tile(x, y + h, h, depth + 1); tile(x + h, y + h, h, depth + 1);
      return;
    }
    const r = s / 2;
    const x1 = x + s, y1 = y + s;

    if (rng() < 0.5) {
      // Arcs centred at the top-left and the bottom-right corners.
      const A = arc(x, y, r, 0, Math.PI / 2);            // (x+r,y) -> (x,y+r)
      const B = arc(x1, y1, r, Math.PI, Math.PI * 1.5);  // (x1-r,y1) -> (x1,y1-r)
      rings.push([{ x, y }, ...A]);                       // quarter disc at TL
      rings.push([{ x: x1, y: y1 }, ...B]);               // quarter disc at BR
      // Band: (x+r,y) -> along top -> (x1,y) -> down right -> (x1,y1-r)
      //       -> arc B reversed -> (x1-r,y1) -> along bottom -> (x,y1)
      //       -> up left -> (x,y+r) -> arc A reversed -> back.
      rings.push([
        ...A.slice().reverse(),        // (x,y+r) ... (x+r,y)
        { x: x1, y },
        { x: x1, y: y1 - r },
        ...B.slice().reverse(),        // (x1,y1-r) ... (x1-r,y1)
        { x, y: y1 },
      ]);
    } else {
      // Mirrored: arcs at the top-right and bottom-left corners.
      const A = arc(x1, y, r, Math.PI / 2, Math.PI);      // (x1,y+r) -> (x1-r,y)
      const B = arc(x, y1, r, Math.PI * 1.5, Math.PI * 2); // (x,y1-r) -> (x+r,y1)
      rings.push([{ x: x1, y }, ...A]);
      rings.push([{ x, y: y1 }, ...B]);
      rings.push([
        ...A.slice().reverse(),        // (x1-r,y) ... (x1,y+r)
        { x: x1, y: y1 },
        { x: x + r, y: y1 },
        ...B.slice().reverse(),        // (x+r,y1) ... (x,y1-r)
        { x, y },
      ]);
    }
  };

  for (let y = 0; y < H; y += cell0) {
    for (let x = 0; x < W; x += cell0) tile(x, y, cell0, 0);
  }

  return emit(rings, W, H, gutter, 'tru');
};

// =============================================================================
// DROSTE / LOGARITHMIC SPIRAL
// =============================================================================

/**
 * A logarithmic spiral has the defining property r = a*e^(b*theta), so scaling
 * by e^(2*pi*b) and rotating by 2*pi maps the figure onto itself. Cells laid on
 * that lattice therefore repeat at EVERY scale — the infinite-zoom Droste look.
 *
 * It also animates for free and beautifully: advancing `t` by one period is
 * indistinguishable from a continuous zoom, so a loop is seamless by
 * construction rather than by cross-fade.
 */
export const droste = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, t = 0 } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const R = coverRadius(W, H, cx, cy) * 1.06;
  const rMin = Math.min(W, H) * 0.018;

  // BUILT AS A SHEARED GRID IN LOG-POLAR SPACE, which is the honest way to say
  // "the image of a rectangular grid under z -> exp(z)".
  //
  // A point on spiral arm u is  r(theta, u) = rMin * s^(theta/2pi + u).
  // A cell is the quad between (theta_i, theta_i+1) x (u, u + 1/J). Because one
  // full turn in theta advances u by exactly 1, the cells JOIN where the spiral
  // closes on itself — so the tiling has no seam and no gaps.
  //
  // The first attempt drew independent quads of width 0.62r floating on the
  // arms, which left most of the plane between them empty (35% coverage).
  const s = 1.9 + rng() * 1.1;            // radial scale per full turn
  const lnS = Math.log(s);
  const turns = Math.log(R / rMin) / lnS;
  // Cells ~ N * J * turns, so solve for the per-turn budget rather than for the
  // total — ignoring the turn count is what produced 235 cells on a request of
  // 48. Skew toward angular divisions: long thin spiral cells read better than
  // square ones because they follow the arm.
  const perTurn = Math.max(4, count / Math.max(1, turns));
  const N = Math.max(5, Math.round(Math.sqrt(perTurn) * 1.9));
  const J = Math.max(1, Math.round(perTurn / N));

  const rAt = (theta: number, u: number) => rMin * Math.exp((theta / TAU + u) * lnS);
  const pt = (theta: number, u: number) => ({
    x: cx + Math.cos(theta) * rAt(theta, u),
    y: cy + Math.sin(theta) * rAt(theta, u),
  });

  const rings: Point[][] = [];
  // `t` slides the whole lattice by a fraction of one self-similar period —
  // which IS a continuous zoom, so a loop of length 1 is seamless by
  // construction rather than by cross-fade.
  const shift = t % 1;
  for (let m = 0; m <= Math.ceil(turns) + 1; m++) {
    for (let j = 0; j < J; j++) {
      const u0 = m + j / J + shift;
      const u1 = m + (j + 1) / J + shift;
      for (let i = 0; i < N; i++) {
        const th0 = (i / N) * TAU;
        const th1 = ((i + 1) / N) * TAU;
        if (rAt(th0, u0) > R * 1.3) continue;
        if (rAt(th1, u1) < rMin * 0.6) continue;
        rings.push([pt(th0, u0), pt(th1, u0), pt(th1, u1), pt(th0, u1)]);
      }
    }
  }
  return emit(rings, W, H, gutter, 'dro');
};

// =============================================================================
// HILBERT
// =============================================================================

/**
 * Cells laid along a Hilbert curve. The curve's defining property is LOCALITY:
 * points adjacent along the curve are adjacent in the plane. So consecutive
 * source images land next to each other spatially — a collage laid on a Hilbert
 * curve keeps a photo sequence's narrative order while filling the frame, which
 * a raster order emphatically does not.
 *
 * Cells are widened into ribbons following the curve, so the path reads.
 */
export const hilbert = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;

  // One fragment per curve STEP, so the ribbon is continuous and the curve's
  // own turning is the structure. Oversampling and then striding (the first
  // attempt) skipped most of the curve and painted 10% of the frame.
  const order = Math.max(2, Math.min(7, Math.round(Math.log2(Math.sqrt(Math.max(4, count))))));
  const n = 1 << order;

  // Standard d -> (x,y) Hilbert mapping.
  const d2xy = (d: number): Point => {
    let rx = 0, ry = 0, x = 0, y = 0, tt = d;
    for (let s = 1; s < n; s *= 2) {
      rx = 1 & (tt / 2);
      ry = 1 & (tt ^ rx);
      if (ry === 0) {
        if (rx === 1) { x = s - 1 - x; y = s - 1 - y; }
        const tmp = x; x = y; y = tmp;
      }
      x += s * rx;
      y += s * ry;
      tt = Math.floor(tt / 4);
    }
    return { x, y };
  };

  const cw = W / n;
  const ch = H / n;
  const pts: Point[] = [];
  for (let d = 0; d < n * n; d++) {
    const p = d2xy(d);
    pts.push({ x: (p.x + 0.5) * cw, y: (p.y + 0.5) * ch });
  }

  // ONE QUAD PER CURVE STEP, not one polygon per run.
  //
  // The first build offset a whole 21-point run to both sides and joined the
  // two offsets into a single ring. A Hilbert curve turns a corner every two or
  // three steps, so those rings SELF-INTERSECTED — and Sutherland-Hodgman on a
  // self-intersecting ring returns nonsense, which is why the generator emitted
  // 0 cells for a request of 48 while looking perfectly reasonable in source.
  //
  // A quad spanning one step is convex by construction and cannot fold. The
  // quads share their end edges, so consecutive fragments still form one
  // continuous serpentine band — the ribbon is now made OF the cells rather
  // than sliced INTO them.
  const rings: Point[][] = [];
  // WIDTH MUST MATCH THE PERPENDICULAR PITCH, NOT THE SMALLER OF THE TWO.
  //
  // The curve steps between lattice neighbours, so a step is either horizontal
  // (and the band's width runs along y, pitch `ch`) or vertical (width along x,
  // pitch `cw`). Using `min(cw, ch)` for both is only correct on a square
  // frame; at 16:9 it made the band 56% of the pitch on the long axis and
  // coverage fell to 55%. Choosing per step is exact at every aspect.

  // Width breathes along the path, so the band is not a uniform noodle. Centred
  // slightly ABOVE 1 so the swell overlaps rather than opens gaps — the gutter
  // is what should separate fragments, not an accident of the width curve.
  const phase = rng() * TAU;
  /** Swell factor only — the pitch is supplied per step by the caller. */
  const swell = (i: number): number =>
    0.86 + 0.30 * (0.5 + 0.5 * Math.sin(i * 0.2137 + phase)) ** (1 + entropy * 1.4);

  const stride = 1;
  for (let i = 0; i + stride < pts.length; i += stride) {
    const a = pts[i];
    const b = pts[i + stride];
    const dx = b.x - a.x, dy = b.y - a.y;
    const l = Math.hypot(dx, dy);
    if (l < 1e-6) continue;
    const nx = -dy / l, ny = dx / l;
    // Horizontal step => the band is as wide as one ROW; vertical => one COLUMN.
    const pitch = Math.abs(dx) >= Math.abs(dy) ? ch : cw;
    const half = pitch * 0.5;
    const wa = half * swell(i);
    const wb = half * swell(i + stride);
    rings.push([
      { x: a.x + nx * wa, y: a.y + ny * wa },
      { x: b.x + nx * wb, y: b.y + ny * wb },
      { x: b.x - nx * wb, y: b.y - ny * wb },
      { x: a.x - nx * wa, y: a.y - ny * wa },
    ]);
  }
  return emit(rings, W, H, gutter, 'hil');
};

// =============================================================================
// SHARDS — the rebuilt "Shatter"
// =============================================================================

/**
 * The mode this replaces claimed "angular voronoi shards" and was recursive
 * random half-plane splitting of a rectangle — every piece convex, roughly
 * equal, roughly rectangular. Here the split is chosen the way a real fracture
 * chooses: a line through a point NEAR the cell's centroid, oriented across the
 * long axis, with the split point drawn from a beta-ish distribution so the two
 * pieces are usually UNEVEN. Uneven splits compound into a power-law size
 * distribution — the scale hierarchy the original never produced.
 */
export const shards = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  let cells: Point[][] = [[{ x: 0, y: 0 }, { x: W, y: 0 }, { x: W, y: H }, { x: 0, y: H }]];
  const target = Math.max(2, Math.min(400, count));

  // Split point: pushing rng() through a power makes lopsided cuts common.
  const lopsided = () => {
    const u = rng();
    const s = u < 0.5 ? Math.pow(u * 2, 1.9) / 2 : 1 - Math.pow((1 - u) * 2, 1.9) / 2;
    return 0.12 + s * 0.76;
  };

  let guard = 0;
  let stuck = 0;
  while (cells.length < target && guard++ < target * 30) {
    // Bias toward the biggest cell but not deterministically — pure
    // largest-first equalises sizes, which is what we are avoiding.
    let bi = 0, ba = -1;
    for (let i = 0; i < cells.length; i++) {
      const a = polygonArea(cells[i]) * Math.pow(rng(), 0.35);
      if (a > ba) { ba = a; bi = i; }
    }
    const cell = cells[bi];
    const b = boundsOf(cell);
    // A CELL TOO SMALL TO SPLIT IS NOT A REASON TO STOP SPLITTING.
    // The randomised pick can land on a tiny shard at any time, and `break`ing
    // there abandoned the whole subdivision: measured across 45 seed/count/
    // aspect combinations, this returned as few as 4% of the requested cells.
    // Skip it and try again; give up only when several picks in a row are all
    // unsplittable, which is the real "nothing left to cut" signal.
    if (b.w < 6 || b.h < 6) { if (++stuck > 40) break; continue; }
    stuck = 0;
    const c = centroid(cell);

    const across = b.w >= b.h ? 0 : Math.PI / 2;
    const ang = across + (rng() - 0.5) * (0.35 + entropy * 2.2);
    const s = lopsided();
    const a = {
      x: b.x + b.w * (b.w >= b.h ? s : 0.5) + (c.x - (b.x + b.w / 2)) * 0.3,
      y: b.y + b.h * (b.w >= b.h ? 0.5 : s) + (c.y - (b.y + b.h / 2)) * 0.3,
    };
    const n = { x: Math.cos(ang), y: Math.sin(ang) };
    const p = clipHalf(cell, a, n);
    const q = clipHalf(cell, a, { x: -n.x, y: -n.y });
    // Same reasoning as above: a cut that degenerates is this cell's problem.
    if (p.length >= 3 && q.length >= 3) cells.splice(bi, 1, p, q);
    else if (++stuck > 40) break;
  }
  return emit(cells, W, H, gutter, 'shd');
};

// =============================================================================
// SLIT-SCAN — video-native
// =============================================================================

/**
 * Columns (or rows) that each sample a DIFFERENT moment of the clip. The layout
 * itself is simple strips; what makes it a signature effect is that the
 * renderer gives each strip its own time offset, which the offline renderer can
 * do because it SEEKS decoders to an arbitrary t rather than tapping a playing
 * stream. Realtime capture could never do this.
 *
 * The strips carry a per-cell `timeOffset` in their id suffix, which the stage
 * reads. Widths follow a gentle power law so the scan is not a barcode.
 */
export const slitScan = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const vertical = rng() < 0.72;
  const n = Math.max(4, Math.min(240, count));
  const rings: Point[][] = [];

  // Non-uniform widths: a barcode of identical strips reads as an error.
  const weights: number[] = [];
  let total = 0;
  for (let i = 0; i < n; i++) {
    const w = 1 + Math.pow(rng(), 2.2) * (0.4 + entropy * 2.6);
    weights.push(w); total += w;
  }
  let acc = 0;
  for (let i = 0; i < n; i++) {
    const f0 = acc / total;
    acc += weights[i];
    const f1 = acc / total;
    if (vertical) {
      rings.push([
        { x: f0 * W, y: 0 }, { x: f1 * W, y: 0 }, { x: f1 * W, y: H }, { x: f0 * W, y: H },
      ]);
    } else {
      rings.push([
        { x: 0, y: f0 * H }, { x: W, y: f0 * H }, { x: W, y: f1 * H }, { x: 0, y: f1 * H },
      ]);
    }
  }
  return emit(rings, W, H, gutter, 'slt');
};

export const RECURSIVE_GENERATORS = {
  penrose, truchet, droste, hilbert, shards, slitScan,
};
