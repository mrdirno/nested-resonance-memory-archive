// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
// Original bounded geometry. A scene is a value of (kind, seed, sampled form),
// never an accumulated simulation or an imported instrument's animation clock.
import { createArtRandom, type ArtLayerSample } from './artRack';

export const DIMENSIONAL_KINDS = ['torus-knot', 'crystal-vault', 'star-tunnel', 'wave-surface'] as const;
export type DimensionalKind = typeof DIMENSIONAL_KINDS[number];
export type Vec3 = { x: number; y: number; z: number };
export type Point2 = { x: number; y: number };
export interface DimensionalFace { points: Vec3[]; ink: number; gloss: number; }
export interface DimensionalLine { points: Vec3[]; ink: number; alpha: number; width: number; }
export interface DimensionalStar { point: Vec3; tail: Vec3; radius: number; ink: number; alpha: number; }
export interface DimensionalScene {
  camera: number; focal: number; form: number;
  faces: DimensionalFace[]; lines: DimensionalLine[]; stars: DimensionalStar[];
  shadow: { y: number; width: number; height: number; alpha: number } | null;
}
export interface ProjectedFace {
  points: Point2[]; depth: number; normal: Vec3; ink: number;
  light: number; specular: number; rim: number;
}
const TAU = 2 * Math.PI;
const clamp = (n: number, low: number, high: number) => Math.min(high, Math.max(low, n));
const add = (a: Vec3, b: Vec3): Vec3 => ({ x: a.x + b.x, y: a.y + b.y, z: a.z + b.z });
const sub = (a: Vec3, b: Vec3): Vec3 => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z });
const mul = (a: Vec3, s: number): Vec3 => ({ x: a.x * s, y: a.y * s, z: a.z * s });
const dot = (a: Vec3, b: Vec3) => a.x * b.x + a.y * b.y + a.z * b.z;
const cross = (a: Vec3, b: Vec3): Vec3 => ({ x: a.y * b.z - a.z * b.y, y: a.z * b.x - a.x * b.z, z: a.x * b.y - a.y * b.x });
const unit = (v: Vec3): Vec3 => mul(v, 1 / (Math.hypot(v.x, v.y, v.z) || 1));
const fract = (n: number) => n - Math.floor(n);
const ease = (n: number) => { const t = clamp(n, 0, 1); return t * t * (3 - 2 * t); };

function rotate(v: Vec3, ax: number, ay: number, az = 0): Vec3 {
  const cx = Math.cos(ax), sx = Math.sin(ax), cy = Math.cos(ay), sy = Math.sin(ay), cz = Math.cos(az), sz = Math.sin(az);
  const y = v.y * cx - v.z * sx, z = v.y * sx + v.z * cx;
  const x1 = v.x * cy + z * sy, z1 = -v.x * sy + z * cy;
  return { x: x1 * cz - y * sz, y: x1 * sz + y * cz, z: z1 };
}

/** Camera looks down -Z; all geometry stays behind its near plane. */
export function projectDimensionPoint(point: Vec3, scene: Pick<DimensionalScene, 'camera' | 'focal'>): Point2 {
  const denominator = scene.camera - point.z;
  if (!(denominator > .05)) throw new Error('Dimensional art crossed its camera plane.');
  const scale = scene.focal / denominator;
  return { x: point.x * scale, y: point.y * scale };
}

function knot(scene: DimensionalScene, sample: ArtLayerSample, seed: number): void {
  const random = createArtRandom(seed), winding = random() > .65 ? 3 : 2, lobes = winding + 1;
  const phase = random() * TAU, major = .23, minor = .082 + random() * .012;
  const sections = 64 + Math.round(sample.density * 48), sides = 6 + Math.round(sample.density * 4);
  const tube = .034 + sample.density * .014;
  const ax = .55 + sample.form * .45, ay = .35 + Math.sin(phase) * .4 + sample.form * .6;
  const rings: Vec3[][] = [];
  for (let i = 0; i < sections; i++) {
    const t = i / sections * TAU, a = winding * t, b = lobes * t + phase;
    const radius = major + minor * Math.cos(b);
    const center = { x: radius * Math.cos(a), y: radius * Math.sin(a), z: minor * Math.sin(b) * 1.2 };
    const tangent = unit({
      x: -minor * lobes * Math.sin(b) * Math.cos(a) - winding * radius * Math.sin(a),
      y: -minor * lobes * Math.sin(b) * Math.sin(a) + winding * radius * Math.cos(a),
      z: minor * lobes * Math.cos(b) * 1.2,
    });
    // The winding's XY tangent cannot vanish, so this frame has no pole flip.
    const normal = unit(cross(tangent, { x: 0, y: 0, z: 1 })), binormal = unit(cross(tangent, normal));
    const thickness = tube * (1 + .1 * Math.sin(3 * t + phase + sample.form));
    rings.push(Array.from({ length: sides }, (_, j) => {
      const angle = j / sides * TAU;
      return rotate(add(center, add(mul(normal, Math.cos(angle) * thickness), mul(binormal, Math.sin(angle) * thickness))), ax, ay, -.18);
    }));
  }
  for (let i = 0; i < sections; i++) for (let j = 0; j < sides; j++) {
    scene.faces.push({ points: [rings[i][j], rings[(i + 1) % sections][j], rings[(i + 1) % sections][(j + 1) % sides], rings[i][(j + 1) % sides]],
      ink: 1.1 + .95 * Math.sin(i / sections * TAU + phase), gloss: .92 });
  }
  scene.shadow = { y: .38, width: .29, height: .042, alpha: .24 };
}

function crystals(scene: DimensionalScene, sample: ArtLayerSample, seed: number): void {
  const random = createArtRandom(seed), count = 4 + Math.round(sample.density * 7), phase = random() * TAU;
  const pose = (v: Vec3) => rotate(v, -.16 + sample.form * .15, -.3 + sample.form * .65, .08 * Math.sin(phase));
  for (let shard = 0; shard < count; shard++) {
    const angle = shard * 2.399963229728653 + phase, orbit = shard === 0 ? 0 : .1 + Math.sqrt(random()) * .16;
    const base = { x: Math.cos(angle) * orbit, y: .22 + random() * .045, z: Math.sin(angle) * orbit * .65 };
    const height = shard === 0 ? .58 : .18 + random() * .28, radius = shard === 0 ? .085 : .035 + random() * .039;
    const lean = { x: (random() - .5) * .12, y: 0, z: (random() - .5) * .075 };
    const sides = 5 + Math.floor(random() * 3), twist = random() * TAU, ink = shard === 0 ? 0 : .6 + random() * 2.5;
    const rings = [0, .7].map((level, ring) => Array.from({ length: sides }, (_, j) => {
      const a = twist + j / sides * TAU + ring * .13;
      const r = radius * (ring ? 1 : .65);
      return pose({ x: base.x + Math.cos(a) * r + lean.x * level,
        y: base.y - height * level, z: base.z + Math.sin(a) * r + lean.z * level });
    }));
    const tip = pose({ x: base.x + lean.x, y: base.y - height, z: base.z + lean.z });
    const bottom = pose({ x: base.x, y: base.y + .025, z: base.z });
    for (let j = 0; j < sides; j++) {
      const next = (j + 1) % sides;
      scene.faces.push({ points: [rings[0][j], rings[0][next], rings[1][next], rings[1][j]], ink, gloss: .72 });
      scene.faces.push({ points: [rings[1][j], rings[1][next], tip], ink: ink + .22, gloss: 1 });
      scene.faces.push({ points: [bottom, rings[0][next], rings[0][j]], ink: ink + .4, gloss: .45 });
    }
  }
  scene.shadow = { y: .31, width: .32, height: .063, alpha: .27 };
}

function surface(scene: DimensionalScene, sample: ArtLayerSample, seed: number): void {
  const random = createArtRandom(seed), phase = random() * TAU, crossPhase = random() * TAU;
  const columns = 16 + Math.round(sample.density * 18), rows = 14 + Math.round(sample.density * 16);
  const points: Vec3[][] = [], heights: number[][] = [];
  for (let row = 0; row <= rows; row++) {
    points[row] = []; heights[row] = [];
    for (let col = 0; col <= columns; col++) {
      const x = (col / columns - .5) * .82, z = (row / rows - .5) * .72;
      const radius = Math.hypot(x * 1.05, z);
      const height = .073 * Math.sin(x * 10 + phase + sample.form * 2.1) * Math.cos(z * 8 + crossPhase - sample.form)
        + .045 * Math.sin(radius * 16 - phase + sample.form * 1.5);
      heights[row][col] = height;
      points[row][col] = rotate({ x, y: height - .015, z }, .82 + sample.form * .1, -.3 + .12 * Math.sin(phase), -.08);
    }
  }
  for (let row = 0; row < rows; row++) for (let col = 0; col < columns; col++) {
    const height = (heights[row][col] + heights[row + 1][col + 1]) / 2;
    scene.faces.push({ points: [points[row][col], points[row][col + 1], points[row + 1][col + 1], points[row + 1][col]],
      ink: clamp(1.6 + height * 13 + .35 * Math.sin(col / columns * TAU), 0, 3.7), gloss: .85 });
  }
  scene.shadow = { y: .33, width: .35, height: .052, alpha: .23 };
}

function tunnel(scene: DimensionalScene, sample: ArtLayerSample, seed: number, hx: number, hy: number): void {
  const random = createArtRandom(seed), phase = random() * TAU;
  scene.camera = 3.25; scene.focal = 1.28;
  const aspectX = Math.max(1, hx * 1.65), aspectY = Math.max(1, hy * 1.65);
  const point = (progress: number, angle: number, radius: number): Vec3 => ({
    x: (Math.cos(angle) * radius + .15 * Math.sin(progress * 3 + phase)) * aspectX,
    y: (Math.sin(angle) * radius + .13 * Math.cos(progress * 4 + phase)) * aspectY,
    z: -3.8 + progress * 6.45,
  });
  const visibility = (progress: number) => ease(progress / .13) * ease((1 - progress) / .12);
  const rings = 13 + Math.round(sample.density * 8);
  for (let ring = 0; ring < rings; ring++) {
    const progress = fract(ring / rings + sample.form * .22);
    const twist = phase + progress * 1.4 + sample.form * .18;
    const points = Array.from({ length: 49 }, (_, i) => {
      const angle = i / 48 * TAU + twist;
      return point(progress, angle, .56 + .035 * Math.cos(6 * angle + phase));
    });
    scene.lines.push({ points, ink: ring % 3 + 1, alpha: visibility(progress) * (.15 + progress * .55), width: .002 + progress * .001 });
  }
  const count = 90 + Math.round(sample.density * 230);
  for (let i = 0; i < count; i++) {
    const progress = fract(random() + sample.form * .25), angle = random() * TAU + progress * .35;
    const radius = .18 + Math.sqrt(random()) * .7, size = .0015 + Math.pow(random(), 3) * .004;
    scene.stars.push({ point: point(progress, angle, radius), tail: point(Math.max(0, progress - .035), angle, radius),
      radius: size, ink: i % 5, alpha: visibility(progress) * (.3 + progress * .7) });
  }
  scene.lines.sort((a, b) => a.points[0].z - b.points[0].z);
  scene.stars.sort((a, b) => a.point.z - b.point.z);
}

export function buildDimensionalScene(kind: DimensionalKind, sample: ArtLayerSample, seed: number, hx = .5, hy = .5): DimensionalScene {
  const scene: DimensionalScene = { camera: 3.5, focal: 3.2, form: sample.form, faces: [], lines: [], stars: [], shadow: null };
  switch (kind) {
    case 'torus-knot': knot(scene, sample, seed); break;
    case 'crystal-vault': crystals(scene, sample, seed); break;
    case 'wave-surface': surface(scene, sample, seed); break;
    case 'star-tunnel': tunnel(scene, sample, seed, hx, hy); break;
  }
  return scene;
}

/** Flat surface normals, perspective, a fixed camera and a moving light. Sorting
 * faces back-to-front approximates occlusion between opaque surfaces. */
export function projectDimensionalFaces(scene: DimensionalScene): ProjectedFace[] {
  const lightDirection = unit({ x: -.48 + scene.form * .2, y: -.72, z: 1.1 });
  return scene.faces.map(face => {
    const center = mul(face.points.reduce(add, { x: 0, y: 0, z: 0 }), 1 / face.points.length);
    let normal = unit(cross(sub(face.points[1], face.points[0]), sub(face.points[2], face.points[0])));
    const view = unit({ x: -center.x, y: -center.y, z: scene.camera - center.z });
    if (dot(normal, view) < 0) normal = mul(normal, -1); // closed solids and a two-sided sheet
    const diffuse = Math.max(0, dot(normal, lightDirection));
    const highlight = Math.pow(Math.max(0, dot(normal, unit(add(lightDirection, view)))), 34);
    return {
      points: face.points.map(point => projectDimensionPoint(point, scene)), depth: center.z, normal, ink: face.ink,
      light: (.16 + .78 * diffuse) * clamp(.95 + center.z * .3, .7, 1.12),
      specular: highlight * face.gloss * .85,
      rim: Math.pow(1 - Math.max(0, dot(normal, view)), 3) * .22,
    };
  }).sort((a, b) => a.depth - b.depth);
}
