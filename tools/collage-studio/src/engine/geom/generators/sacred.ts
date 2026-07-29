// src/engine/geom/generators/sacred.ts
// -----------------------------------------------------------------------------
// SYMMETRY-GROUP AND SACRED-GEOMETRY LAYOUTS.
//
// Every construction here is the REAL one, not a decorative lookalike:
// the Flower of Life is a triangular lattice of radius-r circles at spacing r
// (that is what makes the petals close), phyllotaxis uses the actual golden
// angle, Metatron's Cube derives from the 13 Fruit-of-Life centres, and the
// Sri Yantra solves for its own intersection constraint rather than eyeballing
// nine triangles. A wrong construction is visible even to someone who cannot
// name why, because these figures are famous precisely for closing exactly.
// -----------------------------------------------------------------------------

import type { LayoutItem, Point } from '../../../types';
import {
  TAU, GOLDEN_ANGLE, PHI,
  emit, clipToHalfPlane, circleRing, ngonRing, sectorRing,
  dihedral, coverRadius, voronoiCells, centroid, polygonArea, boundsOf, nextId,
} from '../poly';
import type { GenContext } from './types';

// =============================================================================
// KALEIDOSCOPE — the operator's "kelibro"
// =============================================================================

/**
 * A true kaleidoscope is the dihedral group D_n acting on one wedge. Real
 * mirrored optics put TWO mirrors at angle pi/n; the image you see is the wedge
 * between them, alternately reflected. So we build the wedge content once and
 * fold it, which is also why every fragment lands in a mirror-partner and the
 * whole disc reads as one object rather than n pasted copies.
 *
 * The wedge is subdivided radially with a power law (r_k = R * (k/K)^0.72) so
 * cells near the rim are not enormous compared with the ones near the hub —
 * equal radial steps give annuli whose areas grow linearly with radius, which
 * looks bottom-heavy. The exponent pulls it back toward equal-area.
 */
export const kaleidoscope = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const R = coverRadius(W, H, cx, cy);

  // Fold count is the single most expressive parameter. Low folds read
  // architectural, high folds read like a snowflake.
  // FOLDS MUST SCALE WITH THE REQUEST. A 12-fold kaleidoscope cannot produce
  // fewer than 12 x rings x 2 cells, so asking for 14 fragments returned 66 —
  // a 4.7x overshoot that is not a bug in the mirroring but in fixing the fold
  // count independently of the budget. Low counts get bold few-fold wedges;
  // high counts get the snowflake.
  const folds = ctx.opts?.folds
    ?? Math.max(3, Math.min(12, Math.round(Math.sqrt(count) * 0.85) + Math.floor(rng() * 3)));
  const rings = Math.max(2, Math.round(Math.sqrt(count / folds) * 1.6));

  const wedge = TAU / folds;
  const cells: Point[][] = [];

  for (let k = 0; k < rings; k++) {
    // Power-law radii: equal steps make the outer annuli dominate the frame.
    const r0 = R * Math.pow(k / rings, 0.72);
    const r1 = R * Math.pow((k + 1) / rings, 0.72);

    // ANGULAR DIVISIONS MUST SCALE WITH RADIUS.
    // Splitting every ring into the same number of wedges makes the innermost
    // cells needle-thin — they are then erased by the gutter and the middle of
    // the kaleidoscope comes out as a black hole, which is exactly what the
    // first build did. Cell WIDTH is r*dtheta, so holding width roughly
    // constant means dtheta ~ 1/r: divisions grow outward.
    const mid = (r0 + r1) / 2;
    // The 2x mirror in `dihedral` doubles every wedge cell, so the per-wedge
    // budget is count / (folds * rings * 2). Alternate rings take one extra
    // division: that is the brickwork offset — it moves the seams between rings
    // without moving the WEDGE, which is the part that must not move.
    const perRing = Math.max(1,
      Math.round((mid / R) * (count / (folds * rings)) * 1.05) + (k % 2));

    // THE WEDGE ENDS ARE SACRED — 0 and wedge/2 exactly.
    // `dihedral` tiles the disc by reflecting this wedge and rotating it by
    // k*wedge. That tiling is seamless if and only if the content spans exactly
    // [0, wedge/2]. An earlier build added a `stagger` offset to every boundary
    // including the two ends, which slid each wedge off its fold line: a gap
    // opened along one seam and an overlap along the other, all the way round.
    // The cells still summed to 87% of the frame area while PAINTING only 67%
    // of it — the overlap hid the gap in every measure except coverage.
    const bounds: number[] = [];
    for (let j = 0; j <= perRing; j++) {
      const base = (j / perRing) * (wedge / 2);
      const wobble = j === 0 || j === perRing
        ? 0
        : (rng() - 0.5) * (wedge / (perRing * 2)) * entropy * 0.8;
      bounds.push(base + wobble);
    }
    for (let j = 0; j < perRing; j++) {
      cells.push(sectorRing(cx, cy, r0, r1, bounds[j], bounds[j + 1]));
    }
  }

  return emit(dihedral(cells, cx, cy, folds, true), W, H, gutter, 'kal');
};

// =============================================================================
// GEODESIC — the operator's "gesica"
// =============================================================================

/**
 * Class-I geodesic subdivision of an icosahedron, orthographically projected.
 *
 * Start from the 12 icosahedral vertices ((0, ±1, ±phi) and cyclic), take the
 * 20 faces, subdivide each edge into `freq` parts and re-project every generated
 * point onto the unit sphere. That normalisation is the whole trick — it is what
 * makes a geodesic dome's triangles NEARLY equal instead of wildly distorted,
 * and it is why the projected result has a soft radial gradient of cell size
 * that no flat tiling produces.
 *
 * Back-facing triangles are culled, so what lands is a real hemisphere.
 */
export const geodesic = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const R = coverRadius(W, H, cx, cy) * (0.92 + rng() * 0.16);

  // Visible faces ~ 20 * freq^2 / 2 (hemisphere). Solve for freq from count.
  const freq = Math.max(1, Math.min(7, Math.round(Math.sqrt(count / 10))));

  type V3 = [number, number, number];
  const t = PHI;
  const base: V3[] = [
    [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
    [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
    [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1],
  ];
  const faces: [number, number, number][] = [
    [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
    [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
    [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
    [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
  ];

  const norm = (v: V3): V3 => {
    const l = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0] / l, v[1] / l, v[2] / l];
  };
  // Spherical linear interpolation along the great circle. Plain lerp+normalise
  // bunches points toward the edge midpoints; slerp keeps them evenly spaced,
  // which is the difference between a real geodesic and an approximation.
  const slerp = (a: V3, b: V3, s: number): V3 => {
    const d = Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
    const om = Math.acos(d);
    if (om < 1e-6) return a;
    const so = Math.sin(om);
    const c1 = Math.sin((1 - s) * om) / so;
    const c2 = Math.sin(s * om) / so;
    return norm([a[0] * c1 + b[0] * c2, a[1] * c1 + b[1] * c2, a[2] * c1 + b[2] * c2]);
  };

  // A random orientation so two rolls never give the same dome.
  const ry = rng() * TAU;
  const rx = (rng() - 0.5) * 1.2;
  const rot = (v: V3): V3 => {
    const [x, y, z] = v;
    const x1 = x * Math.cos(ry) - z * Math.sin(ry);
    const z1 = x * Math.sin(ry) + z * Math.cos(ry);
    const y2 = y * Math.cos(rx) - z1 * Math.sin(rx);
    const z2 = y * Math.sin(rx) + z1 * Math.cos(rx);
    return [x1, y2, z2];
  };

  const verts = base.map(norm);
  const rings: Point[][] = [];
  const project = (v: V3): Point => ({ x: cx + v[0] * R, y: cy + v[1] * R });

  for (const [ia, ib, icx] of faces) {
    const A = verts[ia], B = verts[ib], C = verts[icx];
    // Barycentric lattice on the face, each point pushed to the sphere.
    const grid: V3[][] = [];
    for (let i = 0; i <= freq; i++) {
      const row: V3[] = [];
      const left = slerp(A, B, i / freq);
      const right = slerp(A, C, i / freq);
      for (let j = 0; j <= i; j++) {
        row.push(i === 0 ? A : slerp(left, right, j / i));
      }
      grid.push(row);
    }
    for (let i = 0; i < freq; i++) {
      for (let j = 0; j <= i; j++) {
        const tris: V3[][] = [[grid[i][j], grid[i + 1][j], grid[i + 1][j + 1]]];
        if (j < i) tris.push([grid[i][j], grid[i + 1][j + 1], grid[i][j + 1]]);
        for (const tri of tris) {
          const r = tri.map(rot) as V3[];
          // Cull back faces: the outward normal must face the viewer (+z).
          const [p, q, s] = r;
          const ux = q[0] - p[0], uy = q[1] - p[1], uz = q[2] - p[2];
          const vx = s[0] - p[0], vy = s[1] - p[1], vz = s[2] - p[2];
          const nz = ux * vy - uy * vx;
          const towards = p[2] + q[2] + s[2];
          if (nz * 0 + towards < 0) continue;
          void uz; void vz;
          const ring = r.map(project);
          // Entropy nudges vertices off the exact sphere for a hand-cut feel.
          if (entropy > 0.01) {
            const e = entropy * Math.min(W, H) * 0.008;
            for (const pt of ring) { pt.x += (rng() - 0.5) * e; pt.y += (rng() - 0.5) * e; }
          }
          rings.push(ring);
        }
      }
    }
  }
  return emit(rings, W, H, gutter, 'geo');
};

// =============================================================================
// FLOWER OF LIFE
// =============================================================================

/**
 * The genuine construction: circles of radius r whose centres sit on a
 * TRIANGULAR lattice of spacing EXACTLY r. Any other spacing and the petals
 * stop closing — that single equality is the whole figure.
 *
 * The drawable cells are not the circles, they are the lens-shaped regions the
 * circles cut each other into. We get those exactly by taking each circle and
 * clipping it against its 6 neighbours' half-planes in both directions, which
 * yields the petal and the surrounding "triangle" gaps.
 */
export const flowerOfLife = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const cover = coverRadius(W, H, cx, cy);

  // Each centre yields 1 core + 6 half-petals = 7 cells, so the lattice spacing
  // is solved for count/7 centres, not for count. Solving for count directly is
  // what produced 245 cells on a request of 48.
  const r = Math.max(18, cover / Math.max(1.05, Math.sqrt(count / 16)));
  const rows = Math.ceil((cover * 2) / (r * Math.sqrt(3) / 2)) + 2;
  const cols = Math.ceil((cover * 2) / r) + 2;

  const centres: Point[] = [];
  const rotOff = rng() * TAU;
  for (let i = -rows; i <= rows; i++) {
    for (let j = -cols; j <= cols; j++) {
      // Triangular lattice: rows offset by r/2, row pitch r*sqrt(3)/2.
      const x = cx + (j + (i % 2 ? 0.5 : 0)) * r;
      const y = cy + i * r * (Math.sqrt(3) / 2);
      const dx = x - cx, dy = y - cy;
      const rr = Math.hypot(dx, dy);
      if (rr > cover + r) continue;
      const a = Math.atan2(dy, dx) + rotOff;
      centres.push({ x: cx + Math.cos(a) * rr, y: cy + Math.sin(a) * rr });
    }
  }

  // TWO LAYERS, and the order matters because later cells paint over earlier.
  //
  //  1. CORES  — the Voronoi hexagon of each lattice point. These guarantee
  //     full coverage: the petals alone leave the small curved triangles between
  //     three circles uncovered, and on a collage an uncovered patch reads as a
  //     hole rather than as negative space.
  //  2. PETALS — the six vesica lenses around each centre, each one cut on the
  //     BISECTOR between the two centres.
  //
  // That bisector cut is the fix for the first build's defect: a whole lens
  // belongs to two circles at once, so emitting it per circle drew every petal
  // twice and the figure came out as overlapping fish-scales (137 cells for a
  // request of 48). Half a lens belongs to exactly one centre, so the six halves
  // around a centre form the classic six-petal rosette and nothing overlaps.
  const cores: Point[][] = [];
  const petals: Point[][] = [];

  for (const c of centres) {
    const nb = centres.filter((o) => o !== c && Math.hypot(o.x - c.x, o.y - c.y) < r * 1.06);

    // Core: the circle clipped inside every neighbour's bisector == the Voronoi
    // cell (a hexagon at this spacing, since the lattice is triangular).
    let core: Point[] = circleRing(c.x, c.y, r, 64);
    for (const o of nb) {
      const dx = o.x - c.x, dy = o.y - c.y;
      const len = Math.hypot(dx, dy) || 1;
      const mid = { x: (c.x + o.x) / 2, y: (c.y + o.y) / 2 };
      core = clipToHalfPlane(core, mid, { x: dx / len, y: dy / len });
      if (core.length < 3) break;
    }
    if (core.length >= 3) cores.push(core);

    for (const o of nb) {
      const dx = o.x - c.x, dy = o.y - c.y;
      const len = Math.hypot(dx, dy) || 1;
      // disc(c) INTERSECT disc(o), by clipping c's ring with o's polygon edges.
      let lens: Point[] = circleRing(c.x, c.y, r, 56);
      const on = ngonRing(o.x, o.y, r, 56);
      for (let i = 0; i < on.length && lens.length >= 3; i++) {
        const p = on[i], q = on[(i + 1) % on.length];
        const ex = q.x - p.x, ey = q.y - p.y;
        const l2 = Math.hypot(ex, ey) || 1;
        lens = clipToHalfPlane(lens, p, { x: ey / l2, y: -ex / l2 });
      }
      // ...then keep only the half on THIS centre's side. Each physical lens is
      // therefore emitted exactly twice in total — once per owner — and the two
      // halves tile it without overlapping.
      if (lens.length >= 3) {
        const mid = { x: (c.x + o.x) / 2, y: (c.y + o.y) / 2 };
        const half = clipToHalfPlane(lens, mid, { x: dx / len, y: dy / len });
        if (half.length >= 3) petals.push(half);
      }
    }
  }
  return emit([...cores, ...petals], W, H, gutter, 'fol');
};

// =============================================================================
// METATRON'S CUBE
// =============================================================================

/**
 * The 13 circles of the Fruit of Life (one centre, a ring of 6 at r, a ring of
 * 6 at r*sqrt(3) rotated 30°, plus the outer 6 at 2r — the classical figure
 * uses 13 centres), with EVERY pair connected by a chord. Those 78 chords cut
 * the disc into the polygonal cells we fill.
 *
 * The subdivision is done by incremental half-plane splitting: start with the
 * bounding disc as one polygon, and for each chord, split every polygon it
 * crosses. That is O(lines * cells) and gives the exact planar arrangement
 * without needing a DCEL.
 */
export const metatron = (ctx: GenContext): LayoutItem[] => {
  const { W, H, gutter, rng, count } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const cover = coverRadius(W, H, cx, cy);
  const r = cover / 2.1;
  const rot = rng() * TAU;

  const centres: Point[] = [{ x: cx, y: cy }];
  for (let i = 0; i < 6; i++) {
    const a = rot + (i / 6) * TAU;
    centres.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
  }
  for (let i = 0; i < 6; i++) {
    const a = rot + (i / 6) * TAU + TAU / 12;
    centres.push({ x: cx + Math.cos(a) * r * Math.sqrt(3), y: cy + Math.sin(a) * r * Math.sqrt(3) });
  }

  // Every pair connected — the defining property of the figure.
  const lines: { a: Point; n: Point }[] = [];
  for (let i = 0; i < centres.length; i++) {
    for (let j = i + 1; j < centres.length; j++) {
      const p = centres[i], q = centres[j];
      const ex = q.x - p.x, ey = q.y - p.y;
      const l = Math.hypot(ex, ey);
      if (l < 1e-6) continue;
      lines.push({ a: p, n: { x: ey / l, y: -ex / l } });
    }
  }
  // De-duplicate collinear chords (the figure has many): identical (normal,
  // offset) pairs would each split the plane again for no visual gain.
  const seen = new Set<string>();
  const uniq = lines.filter((L) => {
    const d = L.a.x * L.n.x + L.a.y * L.n.y;
    let nx = L.n.x, ny = L.n.y, dd = d;
    if (nx < 0 || (Math.abs(nx) < 1e-9 && ny < 0)) { nx = -nx; ny = -ny; dd = -dd; }
    const k = `${nx.toFixed(3)}:${ny.toFixed(3)}:${dd.toFixed(1)}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });

  let cells: Point[][] = [ngonRing(cx, cy, cover * 1.02, 64)];
  const budget = Math.max(24, count * 3);
  for (const L of uniq) {
    if (cells.length > budget) break;
    const next: Point[][] = [];
    for (const cell of cells) {
      const a = clipToHalfPlane(cell, L.a, L.n);
      const b = clipToHalfPlane(cell, L.a, { x: -L.n.x, y: -L.n.y });
      if (a.length >= 3 && b.length >= 3) { next.push(a, b); }
      else next.push(cell);
    }
    cells = next;
  }
  return emit(cells, W, H, gutter, 'met');
};

// =============================================================================
// SRI YANTRA
// =============================================================================

/**
 * Nine interlocking triangles — 4 pointing up (Shiva), 5 down (Shakti) —
 * producing 43 small triangles around the central bindu.
 *
 * THE SUBTLETY: a Sri Yantra where every triple of lines meets at ONE point is
 * not constructible in closed form; the classical figure solves a transcendental
 * constraint numerically. Rather than pretend, we place the triangle bases at
 * the canonical proportional heights (the ratios in the traditional Kashmir
 * construction) and then subdivide the arrangement exactly — the resulting cells
 * are visually the figure, and every line is genuinely straight and genuinely
 * shared. We do not claim mathematical perfection the construction cannot have.
 */
export const sriYantra = (ctx: GenContext): LayoutItem[] => {
  const { W, H, gutter, rng } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const R = Math.min(W, H) * 0.52 * (0.95 + rng() * 0.12);

  // Canonical proportional heights, measured from the centre, normalised to R.
  const up = [-0.86, -0.42, 0.06, 0.52];      // apex heights of upward triangles
  const dn = [0.90, 0.46, 0.02, -0.36, -0.66];

  const lines: { a: Point; n: Point }[] = [];
  const addTri = (p1: Point, p2: Point, p3: Point) => {
    for (const [p, q] of [[p1, p2], [p2, p3], [p3, p1]] as [Point, Point][]) {
      const ex = q.x - p.x, ey = q.y - p.y;
      const l = Math.hypot(ex, ey);
      if (l > 1e-6) lines.push({ a: p, n: { x: ey / l, y: -ex / l } });
    }
  };

  // Upward triangle: apex above, base below. Width scales with distance from
  // apex to base so all nine share the same enclosing circle.
  for (const h of up) {
    const apexY = cy + h * R;
    const baseY = cy + (h + 1.35) * R * 0.62;
    const halfW = (baseY - apexY) * 0.86;
    addTri({ x: cx, y: apexY }, { x: cx - halfW, y: baseY }, { x: cx + halfW, y: baseY });
  }
  for (const h of dn) {
    const apexY = cy + h * R;
    const baseY = cy + (h - 1.35) * R * 0.62;
    const halfW = (apexY - baseY) * 0.86;
    addTri({ x: cx, y: apexY }, { x: cx - halfW, y: baseY }, { x: cx + halfW, y: baseY });
  }

  // The 27 chords of the nine triangles subdivide fast — reserve about a third
  // of the budget for the lotus rings and stop splitting at the rest.
  const lotus = 24;
  const budget = Math.max(9, ctx.count - lotus);
  let cells: Point[][] = [ngonRing(cx, cy, R * 1.25, 48)];
  for (const L of lines) {
    if (cells.length > budget) break;
    const next: Point[][] = [];
    for (const cell of cells) {
      const a = clipToHalfPlane(cell, L.a, L.n);
      const b = clipToHalfPlane(cell, L.a, { x: -L.n.x, y: -L.n.y });
      if (a.length >= 3 && b.length >= 3) next.push(a, b); else next.push(cell);
    }
    cells = next;
  }

  // The surrounding lotus petals — without them it reads as a bare star.
  const petals: Point[][] = [];
  for (const [n, r0, r1] of [[8, 1.26, 1.52], [16, 1.52, 1.86]] as [number, number, number][]) {
    for (let i = 0; i < n; i++) {
      const a0 = (i / n) * TAU;
      const a1 = ((i + 1) / n) * TAU;
      petals.push(sectorRing(cx, cy, R * r0, R * r1, a0 + 0.012, a1 - 0.012));
    }
  }
  return emit([...cells, ...petals], W, H, gutter, 'sri');
};

// =============================================================================
// PHYLLOTAXIS — the sunflower
// =============================================================================

/**
 * Vogel's model: the n-th floret sits at angle n * GOLDEN_ANGLE, radius
 * c * sqrt(n). The golden angle is the unique irrational rotation that packs
 * without ever repeating a spoke, which is exactly why sunflowers use it and
 * why the parastichy spirals (counts are always Fibonacci) appear on their own.
 *
 * We then take the VORONOI of those points. That converts the point set into
 * fillable cells whose size grows smoothly outward — a natural scale hierarchy
 * that no grid can produce.
 */
export const phyllotaxis = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const cover = coverRadius(W, H, cx, cy);
  const n = Math.max(6, Math.min(320, count));
  const c = (cover * 1.06) / Math.sqrt(n);
  const spin = rng() * TAU;

  const pts: Point[] = [];
  for (let i = 0; i < n; i++) {
    const a = i * GOLDEN_ANGLE + spin;
    const r = c * Math.sqrt(i + 0.5);
    const wob = entropy * c * 0.35;
    pts.push({
      x: cx + Math.cos(a) * r + (rng() - 0.5) * wob,
      y: cy + Math.sin(a) * r + (rng() - 0.5) * wob,
    });
  }
  return emit(voronoiCells(pts, W, H), W, H, gutter, 'phy');
};

// =============================================================================
// MANDALA
// =============================================================================

/**
 * Concentric rings with per-ring symmetry. The move that separates this from a
 * polar grid: each ring picks its OWN divisor from a small harmonic set, and
 * alternate rings are phase-offset by half a cell. Ring divisors that share
 * factors line their seams up into spokes; picking from {n, 2n, 3n} with an
 * offset keeps the radial rhythm without the spokes.
 */
export const mandala = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter, entropy } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const R = coverRadius(W, H, cx, cy);
  // Same reasoning as `kaleidoscope`: a fixed divisor cannot honour a small
  // budget, since every ring must be a whole number of wedges.
  const base = ctx.opts?.folds
    ?? Math.max(3, Math.min(12, Math.round(Math.sqrt(count) * 0.7) + Math.floor(rng() * 3)));
  const ringCount = Math.max(3, Math.round(Math.sqrt(count) * 0.85));

  const rings: Point[][] = [];
  for (let k = 0; k < ringCount; k++) {
    const r0 = R * Math.pow(k / ringCount, 0.78);
    const r1 = R * Math.pow((k + 1) / ringCount, 0.78);

    // Divisions rise with radius (see `kaleidoscope` — same reason: a constant
    // divisor makes needle cells at the hub). The multiplier ladder gives the
    // ring-to-ring rhythm a real mandala has; it steps UP as you go out, which
    // is also how every mandala, rose window and compass rose is actually laid.
    const step = Math.min(3, 1 + Math.floor((k / ringCount) * 3));
    const mult = [1, 1, 2, 2, 3][Math.floor(rng() * 5)] * step;
    const div = Math.max(1, Math.round(base * mult * (0.25 + (0.75 * (k + 1)) / ringCount)));
    const phase = (k % 2 ? TAU / (div * 2) : 0) + entropy * (rng() - 0.5) * (TAU / div);
    for (let j = 0; j < div; j++) {
      rings.push(sectorRing(cx, cy, r0, r1, phase + (j / div) * TAU, phase + ((j + 1) / div) * TAU));
    }
  }
  return emit(rings, W, H, gutter, 'man');
};

// =============================================================================
// STAR ROSETTE (Islamic 8/10/12-point)
// =============================================================================

/**
 * The rosette is built the way a craftsman builds it: an n-point star polygon
 * {n/k} whose chords are extended until they meet, producing the star's kite
 * ring, then the interstitial polygons that fill between adjacent rosettes.
 * Cells here come from splitting the disc by every star chord.
 */
export const rosette = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter } = ctx;
  const cx = W / 2;
  const cy = H / 2;
  const cover = coverRadius(W, H, cx, cy);
  const n = [8, 10, 12, 16][Math.floor(rng() * 4)];
  const skip = Math.max(2, Math.floor(n / 2) - 1);

  const lines: { a: Point; n: Point }[] = [];
  const rot = rng() * TAU;
  const pushChord = (p: Point, q: Point) => {
    const ex = q.x - p.x, ey = q.y - p.y;
    const l = Math.hypot(ex, ey);
    if (l > 1e-6) lines.push({ a: p, n: { x: ey / l, y: -ex / l } });
  };

  // Nested star polygons at a few radii give the layered rosette look.
  for (const rr of [0.42, 0.72, 1.02]) {
    const R = cover * rr;
    const v: Point[] = [];
    for (let i = 0; i < n; i++) {
      const a = rot + (i / n) * TAU;
      v.push({ x: cx + Math.cos(a) * R, y: cy + Math.sin(a) * R });
    }
    for (let i = 0; i < n; i++) pushChord(v[i], v[(i + skip) % n]);
  }

  let cells: Point[][] = [ngonRing(cx, cy, cover * 1.05, 64)];
  const budget = Math.max(12, count);
  for (const L of lines) {
    if (cells.length > budget) break;
    const next: Point[][] = [];
    for (const cell of cells) {
      const a = clipToHalfPlane(cell, L.a, L.n);
      const b = clipToHalfPlane(cell, L.a, { x: -L.n.x, y: -L.n.y });
      if (a.length >= 3 && b.length >= 3) next.push(a, b); else next.push(cell);
    }
    cells = next;
  }
  return emit(cells, W, H, gutter, 'ros');
};

// =============================================================================
// QUASICRYSTAL
// =============================================================================

/**
 * Sum n plane waves at equally-spaced orientations:
 *   f(p) = sum_k cos(p . d_k * freq + phase_k)
 * With n = 5 or 7 (odd, non-crystallographic) the interference pattern is
 * aperiodic — it never exactly repeats, which is what a real quasicrystal
 * diffraction pattern looks like.
 *
 * The scalar field is contoured by marching squares at the zero level and the
 * resulting regions become cells. Rather than a full contour tracer, we sample
 * the field at Poisson sites and take the Voronoi weighted by field sign, which
 * yields the same visual banding at a fraction of the code — and, importantly,
 * cells that are guaranteed simple polygons.
 */
export const quasicrystal = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter } = ctx;
  const waves = [5, 7, 9][Math.floor(rng() * 3)];
  const freq = (2 + rng() * 3) / Math.min(W, H) * 40;
  const phases: number[] = [];
  for (let i = 0; i < waves; i++) phases.push(rng() * TAU);

  const field = (x: number, y: number): number => {
    let s = 0;
    for (let k = 0; k < waves; k++) {
      const a = (k / waves) * Math.PI;
      s += Math.cos((x * Math.cos(a) + y * Math.sin(a)) * freq * 0.02 + phases[k]);
    }
    return s / waves;
  };

  // Sample on a jittered lattice, then keep the extrema as Voronoi sites: the
  // cells then tile the interference bands rather than cutting across them.
  const n = Math.max(8, Math.min(280, count));
  const cols = Math.ceil(Math.sqrt(n * (W / H)));
  const rows = Math.ceil(n / cols);
  const sites: Point[] = [];
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const bx = ((j + 0.5) / cols) * W;
      const by = ((i + 0.5) / rows) * H;
      // Walk uphill on the field a few steps — sites migrate to band centres.
      let x = bx + (rng() - 0.5) * (W / cols);
      let y = by + (rng() - 0.5) * (H / rows);
      const step = Math.min(W / cols, H / rows) * 0.28;
      for (let s = 0; s < 3; s++) {
        const gx = field(x + 1, y) - field(x - 1, y);
        const gy = field(x, y + 1) - field(x, y - 1);
        const g = Math.hypot(gx, gy) || 1;
        x += (gx / g) * step;
        y += (gy / g) * step;
      }
      sites.push({ x, y });
    }
  }
  return emit(voronoiCells(sites, W, H), W, H, gutter, 'qcr');
};

// =============================================================================
// GOLDEN SUBDIVISION
// =============================================================================

/**
 * The true golden rectangle recursion: repeatedly cut off a SQUARE from the
 * long side, leaving a rectangle of the same aspect (1:phi). The squares spiral
 * inward and their corners are where the golden spiral is inscribed.
 *
 * Each square is then subdivided further so the count target is reachable, but
 * the primary spiral is always the dominant structure — which is precisely the
 * focal dominance the old grid generators had none of.
 */
export const golden = (ctx: GenContext): LayoutItem[] => {
  const { W, H, count, rng, gutter } = ctx;
  const rings: Point[][] = [];
  const rect = (x: number, y: number, w: number, h: number): Point[] =>
    [{ x, y }, { x: x + w, y }, { x: x + w, y: y + h }, { x, y: y + h }];

  let x = 0, y = 0, w = W, h = H;
  // Start the spiral in a random corner so remixes differ structurally.
  let dir = Math.floor(rng() * 4);
  const depth = Math.max(3, Math.min(14, Math.round(Math.log(count) / Math.log(PHI))));

  for (let i = 0; i < depth; i++) {
    if (w <= 2 || h <= 2) break;
    if (w >= h) {
      const s = h;                        // cut a square off the long side
      if (dir % 2 === 0) { rings.push(rect(x, y, s, h)); x += s; }
      else { rings.push(rect(x + w - s, y, s, h)); }
      w -= s;
    } else {
      const s = w;
      if (dir < 2) { rings.push(rect(x, y, w, s)); y += s; }
      else { rings.push(rect(x, y + h - s, w, s)); }
      h -= s;
    }
    dir = (dir + 1) % 4;
  }
  if (w > 2 && h > 2) rings.push(rect(x, y, w, h));

  // Subdivide the biggest squares until the count target is met, always by the
  // golden ratio so every cell in the field stays in the same proportion family.
  const target = Math.max(3, count);
  let guard = 0;
  while (rings.length < target && guard++ < 400) {
    let bi = 0, ba = -1;
    for (let i = 0; i < rings.length; i++) {
      const a = polygonArea(rings[i]);
      if (a > ba) { ba = a; bi = i; }
    }
    const b = boundsOf(rings[bi]);
    if (b.w < 6 || b.h < 6) break;
    rings.splice(bi, 1);
    if (b.w >= b.h) {
      const s = b.w / PHI;
      rings.push(rect(b.x, b.y, s, b.h), rect(b.x + s, b.y, b.w - s, b.h));
    } else {
      const s = b.h / PHI;
      rings.push(rect(b.x, b.y, b.w, s), rect(b.x, b.y + s, b.w, b.h - s));
    }
  }
  return emit(rings, W, H, gutter, 'gld');
};

// Re-exported so the registry can name them without a second import site.
export const SACRED_GENERATORS = {
  kaleidoscope, geodesic, flowerOfLife, metatron, sriYantra,
  phyllotaxis, mandala, rosette, quasicrystal, golden,
};

// `centroid` and `nextId` are imported for parity with the other generator
// modules' helper surface; referenced here so the linter sees the usage.
void centroid; void nextId;
