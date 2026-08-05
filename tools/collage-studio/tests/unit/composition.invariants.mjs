/**
 * Invariant sweep for src/lib/composition.ts — arrangement + focus.
 *
 * Run: node tests/unit/composition.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so it
 * proves the shipped code — not a re-implementation. The matrix is
 * 11 arrangements × 5 focus modes × pool shape × fragment count × 40 seeds,
 * because a pairing algorithm can permute correctly on one seed and drop a photo
 * on the next (scar: a spot check says nothing about coverage — sweep, never one).
 *
 * THE INVARIANT THAT MATTERS: an arrangement is a PERMUTATION. The same multiset
 * of photos comes out that went in. If that ever fails, a photo silently vanishes
 * from the collage and another appears twice, which is exactly the class of bug
 * the source-first fill exists to prevent.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

/**
 * BUNDLE, don't just transpile. `diceRoll.ts` imports the generator roster, and a
 * bare `transform` writes a file whose relative imports resolve against the temp
 * directory — where nothing exists. Bundling from the real entry point walks the
 * real import graph, so what gets imported here is still the SHIPPED code and its
 * shipped dependencies, never a stub of them.
 */
const load = async (rel, tag) => {
  const out = join(mkdtempSync(join(tmpdir(), `${tag}-`)), `${tag}.mjs`);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: out,
    bundle: true,
    format: 'esm',
    platform: 'neutral',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const {
  ARRANGEMENTS, ARRANGEMENT_IDS, FOCUS_IDS, arrangeBag, focusAnchor, withFocus,
} = await load('src/lib/composition.ts', 'composition');

const { encodeRoll, decodeRoll, rollDice } = await load('src/lib/diceRoll.ts', 'dice');

// mulberry32 — a small deterministic PRNG so each seed is a distinct fixture.
const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

let fails = 0;
const check = (ok, msg) => { if (!ok) { fails++; console.error(`  ✗ ${msg}`); } };

// --- fixtures ----------------------------------------------------------------

const makePool = (n, rnd, { blank = 0 } = {}) =>
  Array.from({ length: n }, (_, i) => {
    if (i < blank) return {};                       // no analysis at all
    const h = rnd(), s = rnd(), l = rnd();
    return {
      analysis: {
        face: rnd() < 0.4 ? { x: rnd(), y: rnd() } : null,
        energy: { x: rnd(), y: rnd() },
        color: { r: rnd() * 255, g: rnd() * 255, b: rnd() * 255, h, s, l },
      },
    };
  });

const makeCells = (n, rnd, { holes = 0 } = {}) =>
  Array.from({ length: n }, (_, i) =>
    i < holes ? null : { cx: rnd(), cy: rnd(), area: rnd() * 0.2 });

const makeBag = (slots, poolSize, rnd) =>
  Array.from({ length: slots }, () => Math.floor(rnd() * poolSize));

const multiset = (a) => [...a].sort((x, y) => x - y).join(',');

// --- 1. PERMUTATION, over the whole matrix -----------------------------------

console.log('1. arrangement is a permutation (11 arrangements × shapes × 40 seeds)');
for (const arrangement of ARRANGEMENT_IDS) {
  for (const [slots, poolSize] of [[1, 1], [2, 2], [3, 7], [12, 12], [37, 9], [140, 140], [300, 24]]) {
    for (let seed = 0; seed < 40; seed++) {
      const rnd = rngOf(seed * 977 + slots);
      const images = makePool(poolSize, rnd, { blank: seed % 5 === 0 ? 2 : 0 });
      const bag = makeBag(slots, poolSize, rnd);
      // Cells deliberately go short and hole-y on some seeds: the layout can
      // return fewer cells than slots, and the caller must not have to guard.
      const cells = makeCells(seed % 3 === 0 ? Math.max(0, slots - 5) : slots, rnd,
        { holes: seed % 4 === 0 ? 3 : 0 });

      const out = arrangeBag({ bag, cells, images, arrangement });
      const tag = `${arrangement} slots=${slots} pool=${poolSize} seed=${seed}`;
      check(out.length === bag.length, `${tag}: length ${out.length} != ${bag.length}`);
      check(multiset(out) === multiset(bag), `${tag}: NOT a permutation — a photo was dropped or duplicated`);
      check(out.every((v) => Number.isInteger(v)), `${tag}: non-integer asset index leaked out`);
    }
  }
}

// --- 2. natural is identity; determinism -------------------------------------

console.log('2. `natural` is identity, and every arrangement is deterministic');
{
  const rnd = rngOf(7);
  const images = makePool(30, rnd);
  const bag = makeBag(60, 30, rnd);
  const cells = makeCells(60, rnd);
  check(arrangeBag({ bag, cells, images, arrangement: 'natural' }) === bag,
    '`natural` must return the input array untouched (identity, not a copy)');
  check(arrangeBag({ bag, cells, images, arrangement: 'not-a-real-id' }) === bag,
    'an unknown arrangement id must fall back to the input order, not throw');

  for (const a of ARRANGEMENT_IDS) {
    const one = arrangeBag({ bag, cells, images, arrangement: a }).join(',');
    const two = arrangeBag({ bag, cells, images, arrangement: a }).join(',');
    check(one === two, `${a}: not deterministic across two identical calls`);
  }
}

// --- 3. every arrangement actually DOES something ----------------------------
// A picker whose entries all render the same collage is a lie in the UI. Each
// arrangement must move the order on a pool with real colour variety, and each
// must differ from the others — otherwise two chips are one chip.

console.log('3. every arrangement is distinct and non-trivial');
{
  const rnd = rngOf(99);
  const images = makePool(64, rnd);
  const bag = Array.from({ length: 64 }, (_, i) => i);
  const cells = Array.from({ length: 64 }, (_, i) => ({
    cx: ((i % 8) + 0.5) / 8, cy: (Math.floor(i / 8) + 0.5) / 8, area: 1 / 64 + (i % 5) * 0.001,
  }));
  const seen = new Map();
  for (const a of ARRANGEMENT_IDS) {
    const out = arrangeBag({ bag, cells, images, arrangement: a }).join(',');
    if (a !== 'natural') check(out !== bag.join(','), `${a}: left the order untouched — it is a no-op`);
    const clash = seen.get(out);
    check(clash === undefined, `${a}: produces the identical order to '${clash}' — two chips, one behaviour`);
    seen.set(out, a);
  }
}

// --- 4. focus anchors ---------------------------------------------------------

console.log('4. focus anchors are in-frame, deterministic, and `auto` is the legacy rule');
{
  for (let seed = 0; seed < 40; seed++) {
    const rnd = rngOf(seed * 31 + 5);
    const images = makePool(20, rnd, { blank: 3 });
    for (const focus of FOCUS_IDS) {
      for (let slot = 0; slot < 20; slot++) {
        const p = images[slot];
        const a = focusAnchor(p, focus, seed * 1000 + slot);
        const tag = `${focus} seed=${seed} slot=${slot}`;
        check(Number.isFinite(a.x) && Number.isFinite(a.y), `${tag}: non-finite anchor`);
        check(a.x >= 0 && a.x <= 1 && a.y >= 0 && a.y <= 1, `${tag}: anchor outside the picture (${a.x},${a.y})`);
        const again = focusAnchor(p, focus, seed * 1000 + slot);
        check(again.x === a.x && again.y === a.y, `${tag}: not deterministic`);

        if (focus === 'auto') {
          const want = p.analysis?.face ?? p.analysis?.energy ?? { x: 0.5, y: 0.5 };
          check(Math.abs(a.x - want.x) < 1e-12 && Math.abs(a.y - want.y) < 1e-12,
            `${tag}: 'auto' must reproduce face ?? energy ?? centre EXACTLY (legacy behaviour)`);
        }
        if (focus === 'centre') check(a.x === 0.5 && a.y === 0.5, `${tag}: 'centre' must be dead centre`);
        if (focus === 'thirds') {
          const ok = (v) => Math.abs(v - 1 / 3) < 1e-9 || Math.abs(v - 2 / 3) < 1e-9;
          check(ok(a.x) && ok(a.y), `${tag}: 'thirds' must land on a third`);
        }
      }
    }
  }
  // `wander` must genuinely wander: the same photo in different slots gets
  // different crops. That is the entire reason the mode exists.
  const rnd = rngOf(4242);
  const [p] = makePool(1, rnd);
  const anchors = new Set(Array.from({ length: 24 }, (_, s) => {
    const a = focusAnchor(p, 'wander', 900 + s);
    return `${a.x.toFixed(6)},${a.y.toFixed(6)}`;
  }));
  check(anchors.size >= 20, `'wander' gave only ${anchors.size}/24 distinct crops — it is not wandering`);
}

// --- 5. withFocus: identity on auto, steers the crop otherwise ----------------

console.log('5. `withFocus` is reference-identical on auto and re-points the anchor otherwise');
{
  const rnd = rngOf(11);
  const images = makePool(8, rnd);
  const p = images[0];
  check(withFocus(p, 'auto', 3) === p, "'auto' must return the SAME object — no clone, no wasted crop recompute");
  check(withFocus(undefined, 'wander', 3) === undefined, 'a missing photo must pass straight through');
  for (const focus of FOCUS_IDS.filter((f) => f !== 'auto')) {
    const q = withFocus(p, focus, 3);
    check(q !== p, `${focus}: must not mutate or return the original`);
    check(p.analysis.face === images[0].analysis.face, `${focus}: MUTATED the source photo`);
    const want = focusAnchor(p, focus, 3);
    check(q.analysis.face.x === want.x && q.analysis.face.y === want.y,
      `${focus}: analysis.face must carry the focus anchor — that is what steers all four crop paths`);
    check(q.analysis.color === p.analysis.color, `${focus}: dropped the colour analysis the arrangement sorts on`);
  }
}

// --- 6. the share code carries arrangement + focus, and old codes still open --

console.log('6. share codes round-trip arrangement + focus, and legacy codes still decode');
{
  for (let seed = 0; seed < 200; seed++) {
    const rnd = rngOf(seed * 17 + 3);
    const roll = rollDice({ rnd, hasVideo: seed % 2 === 0 });
    const code = encodeRoll(roll);
    const back = decodeRoll(code);
    check(back !== null, `seed=${seed}: code ${code} failed to decode`);
    if (!back) continue;
    check(back.arrangement === roll.arrangement,
      `seed=${seed}: arrangement ${roll.arrangement} -> ${back.arrangement} (code ${code})`);
    check(back.focus === roll.focus, `seed=${seed}: focus ${roll.focus} -> ${back.focus} (code ${code})`);
    check(back.layout === roll.layout, `seed=${seed}: layout drifted through the code`);
    check(ARRANGEMENT_IDS.includes(roll.arrangement), `seed=${seed}: rolled an unknown arrangement`);
    check(FOCUS_IDS.includes(roll.focus), `seed=${seed}: rolled an unknown focus`);
  }
  // A code minted before this cycle has a 6-char middle group — built here by
  // TRUNCATING a current one, so this stays true if the format grows again.
  const [ga, gb, gc] = encodeRoll(rollDice({ rnd: rngOf(5) })).split('-');
  const legacy = decodeRoll([ga, gb.slice(0, 6), gc].join('-'));
  check(legacy !== null, 'a pre-composition code must still decode');
  if (legacy) {
    check(legacy.arrangement === 'natural', `legacy code must default to 'natural', got ${legacy.arrangement}`);
    check(legacy.focus === 'auto', `legacy code must default to 'auto', got ${legacy.focus}`);
    const modern = decodeRoll([ga, gb, gc].join('-'));
    check(modern.layout === legacy.layout && modern.count === legacy.count && modern.seed === legacy.seed,
      'truncating the composition fields must change ONLY the composition fields');
  }
  check(decodeRoll('nonsense') === null, 'garbage must decode to null, not a half-roll');
}

// --- 7. the roll spreads across the roster -----------------------------------
// A dice that reaches two of eleven arrangements has not widened anything.

console.log('7. the dice reaches the whole roster');
{
  const arr = new Map(), foc = new Map();
  for (let seed = 0; seed < 4000; seed++) {
    const r = rollDice({ rnd: rngOf(seed * 7 + 1), hasVideo: seed % 3 === 0 });
    arr.set(r.arrangement, (arr.get(r.arrangement) ?? 0) + 1);
    foc.set(r.focus, (foc.get(r.focus) ?? 0) + 1);
  }
  for (const id of ARRANGEMENT_IDS) check((arr.get(id) ?? 0) > 0, `the dice never rolled arrangement '${id}'`);
  for (const id of FOCUS_IDS) check((foc.get(id) ?? 0) > 0, `the dice never rolled focus '${id}'`);
  const natural = (arr.get('natural') ?? 0) / 4000;
  check(natural > 0.08 && natural < 0.45,
    `'natural' came up ${(natural * 100).toFixed(1)}% of rolls — it should stay a common, but not dominant, outcome`);
  console.log(`   arrangements: ${ARRANGEMENTS.length} · rolled spread ${[...arr.entries()]
    .sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}:${((v / 4000) * 100).toFixed(0)}%`).join(' ')}`);
}

if (fails) { console.error(`\n${fails} INVARIANT FAILURE(S)`); process.exit(1); }
console.log('\nAll composition invariants hold.');
