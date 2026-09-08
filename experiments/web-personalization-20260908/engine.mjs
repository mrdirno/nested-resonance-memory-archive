// Author: Aldrin Payopay
// SPDX-License-Identifier: GPL-3.0-only
// Original presentation study. No Bifurcata source or production APIs are used.

const ENGINE = 'branch-study-v1';
const UINT32_MAX = 0xffffffff;
const ANSWER_KEYS = ['palette', 'density', 'typeScale', 'motif'];
const RECIPE_KEYS = ['version', 'engine', 'seed', ...ANSWER_KEYS, 'mode'];
const OPTIONS = Object.freeze({
  palette: Object.freeze(['tide', 'orchard', 'mineral']),
  density: Object.freeze(['comfortable', 'compact']),
  typeScale: Object.freeze(['standard', 'large']),
  motif: Object.freeze(['branch', 'orbit', 'quiet']),
  mode: Object.freeze(['time', 'system', 'light', 'dark']),
});

// Accept only JSON-style records. Descriptors are checked before reading values:
// getters, symbols, extra keys, inherited data and hidden keys are not a recipe.
function readRecord(value, keys, name) {
  if (value === null || typeof value !== 'object') {
    throw new TypeError(`${name} must be a plain object`);
  }
  const prototype = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) {
    throw new TypeError(`${name} must be a plain object`);
  }
  const ownKeys = Reflect.ownKeys(value);
  if (ownKeys.length !== keys.length || ownKeys.some(key => !keys.includes(key))) {
    throw new TypeError(`${name} must contain exactly: ${keys.join(', ')}`);
  }
  const record = {};
  for (const key of keys) {
    const descriptor = Object.getOwnPropertyDescriptor(value, key);
    if (!descriptor || !('value' in descriptor) || !descriptor.enumerable) {
      throw new TypeError(`${name}.${key} must be an enumerable data property`);
    }
    record[key] = descriptor.value;
  }
  return record;
}

function requireOption(key, value) {
  if (!OPTIONS[key].includes(value)) {
    throw new TypeError(`${key} must be one of: ${OPTIONS[key].join(', ')}`);
  }
}

function requireSeed(seed) {
  if (!Number.isInteger(seed) || Object.is(seed, -0) || seed < 0 || seed > UINT32_MAX) {
    throw new TypeError('seed must be a uint32 integer');
  }
}

/** Validate a complete v1 recipe, returning an independent frozen record. */
export function validateRecipe(value) {
  const recipe = readRecord(value, RECIPE_KEYS, 'recipe');
  if (recipe.version !== 1 || recipe.engine !== ENGINE) {
    throw new TypeError('Unsupported recipe version or engine');
  }
  requireSeed(recipe.seed);
  for (const key of [...ANSWER_KEYS, 'mode']) requireOption(key, recipe[key]);
  return Object.freeze(recipe);
}

/**
 * The only seed inputs are the four explicit enumerated presentation answers.
 * Canonical ASCII: branch-study-v1|palette=...|density=...|typeScale=...|motif=...
 * Hash: FNV-1a, offset 2166136261, xor byte then multiply 16777619 modulo 2^32.
 * This is a reproducible visual identifier, not a secret or an identity hash.
 */
export function deriveRecipe(value) {
  const answers = readRecord(value, ANSWER_KEYS, 'answers');
  for (const key of ANSWER_KEYS) requireOption(key, answers[key]);
  const canonical = `${ENGINE}|${ANSWER_KEYS.map(key => `${key}=${answers[key]}`).join('|')}`;
  let seed = 2166136261;
  for (let i = 0; i < canonical.length; i += 1) {
    seed = Math.imul(seed ^ canonical.charCodeAt(i), 16777619) >>> 0;
  }
  return validateRecipe({ version: 1, engine: ENGINE, seed, ...answers, mode: 'time' });
}

export const DEFAULT_RECIPE = deriveRecipe({
  palette: 'tide', density: 'comfortable', typeScale: 'standard', motif: 'branch',
});

/**
 * Time means the supplied Date's local clock: [07:00, 19:00) is light.
 * Callers supply clock/system observations; this module never reads global time.
 * Irrelevant observations are deliberately ignored in explicit light/dark modes.
 */
export function resolveTheme(mode, date, systemDark) {
  requireOption('mode', mode);
  if (mode === 'light' || mode === 'dark') return mode;
  if (mode === 'system') {
    if (typeof systemDark !== 'boolean') throw new TypeError('systemDark must be boolean');
    return systemDark ? 'dark' : 'light';
  }
  if (!(date instanceof Date) || !Number.isFinite(Date.prototype.getTime.call(date))) {
    throw new TypeError('time mode requires a valid Date');
  }
  const hour = Date.prototype.getHours.call(date);
  return hour >= 7 && hour < 19 ? 'light' : 'dark';
}

/**
 * Return 31 frozen SVG path records {d, width, opacity}, viewBox="0 0 100 100".
 * Coordinates are bounded 3..97; use stroke="currentColor" and fill="none".
 * PRNG: unsigned LCG x=(1664525*x+1013904223) mod 2^32, output x/2^32.
 * The explicit seed starts a fresh generator on every call, including seed 0.
 * Geometry uses arithmetic only, avoiding platform-dependent trigonometry.
 */
export function generateBranches(seed) {
  requireSeed(seed);
  let state = seed;
  const random = () => {
    state = (Math.imul(1664525, state) + 1013904223) >>> 0;
    return state / 4294967296;
  };
  const number = value => Math.round(value * 1000) / 1000;
  const coordinate = value => number(Math.min(97, Math.max(3, value)));
  const paths = [];
  function branch(x, y, direction, depth, scale) {
    const spread = depth === 0 ? 0 : direction * 18 * scale;
    const endX = coordinate(x + spread + (random() - 0.5) * 9 * scale);
    const endY = coordinate(y - (depth === 0 ? 25 : 20 * scale) * (0.88 + random() * 0.24));
    const controlX = coordinate(x + spread * 0.2 + (random() - 0.5) * 7 * scale);
    const controlY = coordinate(y - (y - endY) * 0.6);
    paths.push(Object.freeze({
      d: `M ${x} ${y} Q ${controlX} ${controlY} ${endX} ${endY}`,
      width: number(1.8 * scale),
      opacity: number(0.9 - depth * 0.1),
    }));
    if (depth < 4) {
      branch(endX, endY, -1, depth + 1, scale * 0.72);
      branch(endX, endY, 1, depth + 1, scale * 0.72);
    }
  }
  branch(50, 96, 0, 0, 1);
  return Object.freeze(paths);
}
