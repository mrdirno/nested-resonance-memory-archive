// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
// node tests/unit/artDimension.invariants.mjs
// Real geometry and Canvas command path. Pixel appearance remains a browser gate.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import esbuild from 'esbuild';

const root = join(dirname(fileURLToPath(import.meta.url)), '../..');
const temp = mkdtempSync(join(tmpdir(), 'art-dimension-'));
const digest = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
let groups = 0;
const check = (name, fn) => { fn(); groups++; console.log(`PASS ${name}`); };

// This recorder supports only the common Canvas2D calls used by both browser and
// OffscreenCanvas exports. It checks finite geometry and exact caller restoration.
function trace(draw, recipe, time, width = 640, height = 400) {
  const commands = [], state = { globalAlpha: .37, filter: 'blur(2px)' }, original = { ...state }, stack = [];
  const methods = new Set(['setTransform', 'translate', 'rotate', 'scale', 'clearRect', 'fillRect', 'setLineDash',
    'beginPath', 'moveTo', 'lineTo', 'closePath', 'fill', 'stroke', 'arc', 'ellipse', 'quadraticCurveTo']);
  const ctx = new Proxy(state, {
    set(obj, key, value) { obj[key] = value; commands.push(['set', key, typeof value === 'object' ? 'gradient' : value]); return true; },
    get(obj, key) {
      if (key in obj) return obj[key];
      if (key === 'createLinearGradient') return (...args) => {
        commands.push([key, ...args]); return { addColorStop(...stops) { commands.push(['stop', ...stops]); } };
      };
      if (key === 'save') return () => { stack.push({ ...obj }); commands.push(['save']); };
      if (key === 'restore') return () => {
        const before = stack.pop(); assert(before); for (const name of Object.keys(obj)) delete obj[name]; Object.assign(obj, before); commands.push(['restore']);
      };
      assert(methods.has(key), `unsupported Canvas call: ${String(key)}`);
      return (...args) => {
        for (const value of args) if (typeof value === 'number') assert(Number.isFinite(value), `${key} finite`);
        if (key === 'arc') assert(args[2] >= 0);
        if (key === 'ellipse') assert(args[2] >= 0 && args[3] >= 0);
        commands.push([key, ...args]);
      };
    },
  });
  draw(ctx, width, height, recipe, time);
  assert.equal(stack.length, 0); assert.deepEqual(state, original); return commands;
}

try {
  for (const name of ['artRack', 'artRackRenderer', 'artDimension']) {
    await esbuild.build({ entryPoints: [join(root, `src/lib/${name}.ts`)], outfile: join(temp, `${name}.mjs`),
      bundle: true, platform: 'neutral', format: 'esm', logLevel: 'silent' });
  }
  const A = await import(pathToFileURL(join(temp, 'artRack.mjs')).href);
  const D = await import(pathToFileURL(join(temp, 'artDimension.mjs')).href);
  const { drawArt } = await import(pathToFileURL(join(temp, 'artRackRenderer.mjs')).href);
  const fresh = kind => ({ version: 1, size: 'card', duration: 8, background: '#0B1722', soloId: null,
    layers: [A.createArtLayer(kind, 17, 'shape')] });
  const legacyKinds = ['contour', 'rosette', 'rings', 'ribbons', 'branches', 'facets', 'weave', 'particles'];

  check('four additive dimensional kinds preserve recipe-v1 fields and the eight-layer cap', () => {
    assert.deepEqual(A.ART_TEMPLATES.slice(0, 8).map(t => t.id), legacyKinds);
    assert.deepEqual(A.ART_TEMPLATES.slice(8).map(t => t.id), D.DIMENSIONAL_KINDS);
    for (const kind of D.DIMENSIONAL_KINDS) {
      assert.deepEqual(A.normalizeArtRecipe(fresh(kind)), fresh(kind));
      assert.equal(A.ART_TEMPLATES.find(t => t.id === kind).category, 'Dimensional');
      assert.deepEqual(Object.keys(fresh(kind).layers[0]), Object.keys(A.createArtLayer('contour', 17, 'shape')));
    }
    const all = { ...fresh('torus-knot'), layers: Array.from({ length: 8 }, (_, i) => A.createArtLayer(D.DIMENSIONAL_KINDS[i % 4], i, `layer-${i}`)) };
    assert.deepEqual(A.normalizeArtRecipe(all), all);
    assert.throws(() => A.normalizeArtRecipe({ ...all, layers: [...all.layers, A.createArtLayer('torus-knot', 9, 'ninth')] }));
  });
  check('existing family defaults and default composition remain unchanged', () => {
    for (const kind of legacyKinds) {
      const layer = A.createArtLayer(kind, 17, 'legacy');
      assert.equal(layer.palette, 'cobalt'); assert.equal(layer.opacity, .8); assert.equal(layer.density, .5);
      assert.equal(layer.scale, 1); assert.equal(layer.blend, 'source-over');
      assert.equal(layer.automation.target, 'form'); assert.equal(layer.automation.amount, .4);
    }
    assert.deepEqual(A.createDefaultArtRecipe().layers.map(l => l.kind), ['contour', 'rosette', 'particles']);
  });
  check('all eight original painters and the default composition match frozen pre-change Canvas commands', () => {
    // Generated from the actual e4e19604 artRack + artRackRenderer, using this
    // recorder at seed17, t=2.375, 640x400. These are command hashes, not pixels.
    const old = {
      contour: '6610402ccddea7989043abcf60196dd3070cd490d6b8a85825d3112df5665e26',
      rosette: '910480f97ed3d372506614874d644911b0b3416edc6809e74c1029e2c795d75e',
      rings: '04ae1609a218376f41d0b3895cc13b3efd9f6a55795b031871ee6d2b071b71d0',
      ribbons: 'a07004a5a1c08c24fa9a72b6c6f02c81d0ef33c21d685093cbd7df15ca80a22b',
      branches: '034b4468c260f131c1812d9333fb2839a3eeab4ef21d85ed8d06dca5080f6672',
      facets: 'a3adebac6ae76b2437dea40ad2cdcc6e7759ec4ee9be304933a3ecd5af7e911d',
      weave: 'e7751a550a22f8cb92ca76a06ff31a16c7e3ffdea63d80bc67b8ab923af29526',
      particles: '959966f928b7772ff7709b04e1a08cf7140b4c058e108d06a203614d2bb9e2b9',
    };
    for (const kind of legacyKinds) assert.equal(digest(trace(drawArt, fresh(kind), 2.375)), old[kind], kind);
    assert.equal(digest(trace(drawArt, A.createDefaultArtRecipe(), 2.375)), '54d02ba6e670c932518a57a51718cdc4509b8b5774e052476f726f3184237df5');
  });

  const maxima = { faces: 0, stars: 0, lines: 0 };
  check('seeded geometry has actual depth, finite projected coordinates and bounded work at every density', () => {
    for (const kind of D.DIMENSIONAL_KINDS) for (const seed of [0, 17, 0xffffffff]) for (const density of [0, .62, 1]) for (const form of [-1, 0, 1]) {
      const layer = { ...A.createArtLayer(kind, seed, 'shape'), density };
      const sample = { ...A.sampleArtLayer(layer, 0, 8), form };
      const scene = D.buildDimensionalScene(kind, sample, seed, .8, .5);
      assert(scene.faces.length <= 1200); assert(scene.stars.length <= 320); assert(scene.lines.length <= 21);
      maxima.faces = Math.max(maxima.faces, scene.faces.length); maxima.stars = Math.max(maxima.stars, scene.stars.length); maxima.lines = Math.max(maxima.lines, scene.lines.length);
      const points = [...scene.faces.flatMap(face => face.points), ...scene.lines.flatMap(line => line.points), ...scene.stars.map(star => star.point)];
      assert(points.length > 30, `${kind} has real geometry`);
      assert(Math.max(...points.map(p => p.z)) - Math.min(...points.map(p => p.z)) > .04, `${kind} occupies depth`);
      for (const point of points) {
        assert(Object.values(point).every(Number.isFinite));
        assert(point.z < scene.camera - .05, `${kind} stays behind camera plane`);
        const projected = D.projectDimensionPoint(point, scene);
        assert(Object.values(projected).every(Number.isFinite));
      }
      const faces = D.projectDimensionalFaces(scene);
      for (let i = 0; i < faces.length; i++) {
        const face = faces[i];
        assert(Math.abs(Math.hypot(face.normal.x, face.normal.y, face.normal.z) - 1) < 1e-9, `${kind} has a valid surface normal`);
        assert([face.light, face.specular, face.rim].every(Number.isFinite));
        assert(i === 0 || face.depth >= faces[i - 1].depth, 'far faces precede near faces');
      }
      if (kind !== 'star-tunnel') {
        assert(Math.max(...faces.map(face => face.light)) - Math.min(...faces.map(face => face.light)) > .12, `${kind} responds to surface normals`);
        for (const face of faces) for (const p of face.points) assert(Math.max(Math.abs(p.x), Math.abs(p.y)) < .5, `${kind} whole default model fits shortest canvas side`);
      }
    }
  });
  check('perspective enlarges nearer geometry and tunnel fog retires wrap endpoints', () => {
    const scene = D.buildDimensionalScene('star-tunnel', A.sampleArtLayer(fresh('star-tunnel').layers[0], 0, 8), 17);
    const far = D.projectDimensionPoint({ x: .2, y: .1, z: -2 }, scene), near = D.projectDimensionPoint({ x: .2, y: .1, z: 2 }, scene);
    assert(near.x > far.x * 3); assert(near.y > far.y * 3);
    for (const star of scene.stars) assert(star.alpha >= 0 && star.alpha <= 1);
    assert(scene.stars.some(star => star.alpha < .1)); assert(scene.stars.some(star => star.alpha > .5));
    assert.throws(() => D.projectDimensionPoint({ x: 1, y: 1, z: scene.camera }, scene));
  });
  check('families change topology, silhouette and lighting rather than sharing a recolored plane', () => {
    const scenes = D.DIMENSIONAL_KINDS.map(kind => D.buildDimensionalScene(kind, A.sampleArtLayer(fresh(kind).layers[0], 0, 8), 17));
    assert.equal(new Set(scenes.map(scene => `${scene.faces.length}:${scene.lines.length}:${scene.stars.length}`)).size, 4);
    for (const kind of D.DIMENSIONAL_KINDS) {
      const sample = A.sampleArtLayer(fresh(kind).layers[0], 0, 8);
      assert.notEqual(digest(D.buildDimensionalScene(kind, sample, 17)), digest(D.buildDimensionalScene(kind, sample, 18)), `${kind} seed matters`);
      assert.notEqual(digest(D.buildDimensionalScene(kind, { ...sample, form: -.7 }, 17)), digest(D.buildDimensionalScene(kind, { ...sample, form: .7 }, 17)), `${kind} form changes geometry`);
    }
  });

  const commandCounts = {};
  check('real Canvas commands are deterministic, loop exactly, restore caller state and remain bounded', () => {
    const random = Math.random; Math.random = () => { throw new Error('Ambient randomness entered rendering'); };
    try {
      for (const kind of D.DIMENSIONAL_KINDS) {
        const recipe = fresh(kind); recipe.layers[0].density = 1; recipe.layers[0].scale = .3;
        const before = JSON.stringify(recipe), zero = trace(drawArt, recipe, 0);
        assert.deepEqual(trace(drawArt, recipe, 8), zero); assert.deepEqual(trace(drawArt, recipe, -8), zero);
        const sought = digest(trace(drawArt, recipe, 3.25)); trace(drawArt, recipe, 6.75);
        assert.equal(digest(trace(drawArt, recipe, 3.25)), sought);
        assert.equal(JSON.stringify(recipe), before);
        assert(zero.length > 100); assert(zero.length < 20_000, `${kind} Canvas command ceiling`);
        commandCounts[kind] = zero.length;
      }
    } finally { Math.random = random; }
  });
  check('all automation targets and palette choices reuse the existing explicit-time renderer', () => {
    for (const kind of D.DIMENSIONAL_KINDS) {
      for (const target of ['none', 'form', 'scale', 'rotation', 'opacity', 'drift']) {
        const recipe = fresh(kind); recipe.layers[0].automation = { target, amount: .8, cycles: 2, phase: .125 };
        const at0 = digest(trace(drawArt, recipe, 0));
        assert.equal(digest(trace(drawArt, recipe, recipe.duration)), at0);
        if (target === 'none') assert.equal(digest(trace(drawArt, recipe, 1)), at0);
        else assert.notEqual(digest(trace(drawArt, recipe, .75)), at0, `${kind}/${target} makes its intended change`);
      }
      const fingerprints = Object.keys(A.ART_PALETTES).map(palette => {
        const recipe = fresh(kind); recipe.layers[0].palette = palette; return digest(trace(drawArt, recipe, .5));
      });
      assert.equal(new Set(fingerprints).size, fingerprints.length);
    }
  });
  check('disabled, solo and zero-opacity layers do not render hidden dimensional geometry', () => {
    const empty = { ...fresh('torus-knot'), layers: [] };
    for (const kind of D.DIMENSIONAL_KINDS) for (const patch of [{ enabled: false }, { opacity: 0 }]) {
      const recipe = fresh(kind); Object.assign(recipe.layers[0], patch);
      assert.deepEqual(trace(drawArt, recipe, 1), trace(drawArt, empty, 1));
    }
    const combined = fresh('torus-knot'); combined.layers.push(A.createArtLayer('wave-surface', 8, 'other'));
    combined.soloId = 'shape';
    assert.deepEqual(trace(drawArt, combined, 1), trace(drawArt, fresh('torus-knot'), 1));
  });
  console.log(`ART DIMENSION invariants PASS: ${groups} groups; geometry ceilings ${JSON.stringify(maxima)}; Canvas commands ${JSON.stringify(commandCounts)}`);
} finally { rmSync(temp, { recursive: true, force: true }); }
