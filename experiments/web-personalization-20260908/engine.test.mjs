// Author: Aldrin Payopay
// SPDX-License-Identifier: GPL-3.0-only
import test from 'node:test';
import assert from 'node:assert/strict';
import { DEFAULT_RECIPE, deriveRecipe, validateRecipe, resolveTheme, generateBranches } from './engine.mjs';

const answers = { palette: 'tide', density: 'comfortable', typeScale: 'standard', motif: 'branch' };
const recipe = overrides => ({ ...DEFAULT_RECIPE, ...overrides });

test('frozen seed vectors preserve canonical answer encoding across releases', () => {
  // FNV vectors independently recomputed with Python integer arithmetic.
  assert.equal(deriveRecipe(answers).seed, 1120952958);
  assert.equal(deriveRecipe({ palette: 'orchard', density: 'compact', typeScale: 'large', motif: 'orbit' }).seed, 260223298);
  assert.equal(deriveRecipe({ motif: 'branch', typeScale: 'standard', density: 'comfortable', palette: 'tide' }).seed, 1120952958);
  assert.deepEqual(DEFAULT_RECIPE, {
    version: 1, engine: 'branch-study-v1', seed: 1120952958,
    palette: 'tide', density: 'comfortable', typeScale: 'standard', motif: 'branch', mode: 'time',
  });
});

test('every explicit answer combination is stable and has a distinct seed in the current vocabulary', () => {
  const seeds = new Set();
  for (const palette of ['tide', 'orchard', 'mineral']) {
    for (const density of ['comfortable', 'compact']) {
      for (const typeScale of ['standard', 'large']) {
        for (const motif of ['branch', 'orbit', 'quiet']) {
          const value = { palette, density, typeScale, motif };
          const first = deriveRecipe(value);
          assert.deepEqual(first, deriveRecipe(value));
          assert.deepEqual(validateRecipe(first), first);
          seeds.add(first.seed);
        }
      }
    }
  }
  assert.equal(seeds.size, 36);
});

test('mode is independent of seed and accepts all four explicit strategies', () => {
  for (const mode of ['time', 'system', 'light', 'dark']) {
    const value = validateRecipe(recipe({ mode }));
    assert.equal(value.seed, DEFAULT_RECIPE.seed);
    assert.equal(value.mode, mode);
  }
  assert.throws(() => deriveRecipe({ ...answers, mode: 'dark' }), TypeError);
});

test('validation copies and freezes input without changing the caller record', () => {
  const input = recipe();
  const output = validateRecipe(input);
  assert.notEqual(input, output);
  assert.equal(Object.isFrozen(input), false);
  assert.equal(Object.isFrozen(output), true);
  assert.equal(Object.isFrozen(DEFAULT_RECIPE), true);
  input.palette = 'mineral';
  assert.equal(output.palette, 'tide');
  assert.throws(() => { output.seed = 6; }, TypeError);
  assert.deepEqual(validateRecipe(Object.assign(Object.create(null), recipe())), DEFAULT_RECIPE);
});

test('strict recipes reject missing, unknown and unsupported fields', () => {
  for (const key of Object.keys(DEFAULT_RECIPE)) {
    const input = recipe();
    delete input[key];
    assert.throws(() => validateRecipe(input), TypeError, `missing ${key}`);
  }
  for (const key of ['css', 'script', 'url', 'userId', 'profile', 'constructor', '__proto__']) {
    const input = recipe();
    Object.defineProperty(input, key, { value: 'untrusted', enumerable: true });
    assert.throws(() => validateRecipe(input), TypeError, `unknown ${key}`);
  }
  for (const override of [
    { version: '1' }, { version: 2 }, { engine: 'bifurcata' },
    { palette: 'Tide' }, { density: 'tiny' }, { typeScale: 'huge' },
    { motif: '<script>' }, { mode: 'automatic' }, { palette: ['tide'] },
  ]) assert.throws(() => validateRecipe(recipe(override)), TypeError);
});

test('non-record values and inherited recipe fields are rejected', () => {
  class Recipe { constructor() { Object.assign(this, DEFAULT_RECIPE); } }
  for (const value of [null, undefined, false, 1, 'recipe', [], new Date(), new Recipe(), Object.create(DEFAULT_RECIPE)]) {
    assert.throws(() => validateRecipe(value), TypeError);
    assert.throws(() => deriveRecipe(value), TypeError);
  }
});

test('validation rejects accessors, symbols and hidden fields without running a getter', () => {
  let getterCalls = 0;
  const input = recipe();
  Object.defineProperty(input, 'seed', { enumerable: true, get() { getterCalls += 1; return 1; } });
  assert.throws(() => validateRecipe(input), TypeError);
  assert.equal(getterCalls, 0);
  const withSymbol = recipe();
  withSymbol[Symbol('extension')] = 'hidden';
  assert.throws(() => validateRecipe(withSymbol), TypeError);
  const hidden = recipe();
  Object.defineProperty(hidden, 'mode', { enumerable: false, value: 'time' });
  assert.throws(() => validateRecipe(hidden), TypeError);
});

test('answer validation rejects malformed values and ambient metadata', () => {
  for (const value of [
    { ...answers, palette: 'sea' }, { ...answers, density: null },
    { ...answers, typeScale: 1 }, { ...answers, motif: {} },
    { ...answers, timezone: 'UTC' }, { ...answers, userAgent: 'browser' },
    { palette: 'tide', density: 'comfortable', typeScale: 'standard' },
  ]) assert.throws(() => deriveRecipe(value), TypeError);
});

test('uint32 endpoints are accepted and invalid seed representations are rejected', () => {
  for (const seed of [0, 1, 2147483648, 4294967295]) {
    assert.equal(validateRecipe(recipe({ seed })).seed, seed);
    assert.equal(generateBranches(seed).length, 31);
  }
  for (const seed of [-0, -1, 4294967296, 1.5, NaN, Infinity, -Infinity, '1', 1n, null, undefined]) {
    assert.throws(() => validateRecipe(recipe({ seed })), TypeError);
    assert.throws(() => generateBranches(seed), TypeError);
  }
});

test('frozen branch geometry vectors catch PRNG, ordering and arithmetic drift', () => {
  assert.deepEqual(generateBranches(0).slice(0, 3), [
    { d: 'M 50 96 Q 52.237 81.797 47.625 72.329', width: 1.8, opacity: 0.9 },
    { d: 'M 47.625 72.329 Q 45.647 63.93 35.753 58.33', width: 1.296, opacity: 0.8 },
    { d: 'M 35.753 58.33 Q 33.915 51.9 25.693 47.614', width: 0.933, opacity: 0.7 },
  ]);
  assert.deepEqual(generateBranches(4294967295)[0], {
    d: 'M 50 96 Q 47.444 82.124 47.621 72.873', width: 1.8, opacity: 0.9,
  });
});

test('held-out seeds reproduce geometry independently and diverge from each other', () => {
  const heldOut = [7, 17, 65537, 987654321, 2147483648, 4026531841];
  const outputs = heldOut.map(seed => generateBranches(seed));
  for (let i = heldOut.length - 1; i >= 0; i -= 1) {
    assert.deepEqual(outputs[i], generateBranches(heldOut[i]));
  }
  assert.equal(new Set(outputs.map(value => JSON.stringify(value))).size, heldOut.length);
});

test('generated SVG coordinates and style values remain bounded and immutable', () => {
  for (const seed of [0, 7, 17, 65537, 987654321, 2147483648, 4026531841, 4294967295]) {
    const paths = generateBranches(seed);
    assert.equal(Object.isFrozen(paths), true);
    assert.equal(paths.length, 31);
    for (const path of paths) {
      assert.equal(Object.isFrozen(path), true);
      assert.match(path.d, /^M [\d.]+ [\d.]+ Q [\d.]+ [\d.]+ [\d.]+ [\d.]+$/);
      const coordinates = path.d.match(/[\d.]+/g).map(Number);
      assert.equal(coordinates.length, 6);
      assert.ok(coordinates.every(number => number >= 3 && number <= 97));
      assert.ok(path.width > 0 && path.width <= 1.8);
      assert.ok(path.opacity >= 0.5 && path.opacity <= 0.9);
    }
  }
});

test('time mode changes at the exact local 07:00 and 19:00 boundaries', () => {
  const cases = [
    [0, 0, 0, 0, 'dark'], [6, 59, 59, 999, 'dark'],
    [7, 0, 0, 0, 'light'], [12, 0, 0, 0, 'light'],
    [18, 59, 59, 999, 'light'], [19, 0, 0, 0, 'dark'], [23, 59, 59, 999, 'dark'],
  ];
  for (const [hour, minute, second, ms, expected] of cases) {
    const date = new Date(2026, 8, 8, hour, minute, second, ms);
    assert.equal(resolveTheme('time', date, true), expected);
    assert.equal(resolveTheme('time', date, false), expected);
  }
});

test('system and explicit modes ignore irrelevant clock observations', () => {
  assert.equal(resolveTheme('system', undefined, true), 'dark');
  assert.equal(resolveTheme('system', undefined, false), 'light');
  assert.equal(resolveTheme('dark', undefined, undefined), 'dark');
  assert.equal(resolveTheme('light', new Date('invalid'), true), 'light');
});

test('invalid theme modes and required observations fail explicitly', () => {
  for (const mode of [undefined, null, 'auto', '', 1]) {
    assert.throws(() => resolveTheme(mode, new Date(2026, 8, 8, 12), false), TypeError);
  }
  for (const date of [undefined, null, '2026-09-08', 0, new Date('invalid')]) {
    assert.throws(() => resolveTheme('time', date, false), TypeError);
  }
  for (const systemDark of [undefined, null, 0, 1, 'false']) {
    assert.throws(() => resolveTheme('system', undefined, systemDark), TypeError);
  }
});
