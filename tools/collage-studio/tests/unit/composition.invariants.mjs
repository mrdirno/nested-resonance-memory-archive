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

/**
 * The metric each arrangement ranks on, recomputed here as a MEASURING STICK for
 * the module's output — not as a second implementation of its behaviour. Used
 * only to ask "did the picture stay a sibling", never to predict a placement.
 */
const metric = (p, m) => {
  const c = p?.analysis?.color ?? {};
  const l = c.l ?? 0.5, s = c.s ?? 0;
  if (m === 'hue') return c.h ?? 0;
  if (m === 'lum') return l;
  if (m === 'chroma') return s;
  if (m === 'warm') return ((c.r ?? 128) - (c.b ?? 128) + 255) / 510;
  return s * (1 - Math.abs(l - 0.5) * 2);           // punch
};

/** Pearson correlation; 1 = identical shape, 0 = unrelated. */
const corr = (a, b) => {
  const n = a.length;
  const ma = a.reduce((x, y) => x + y, 0) / n;
  const mb = b.reduce((x, y) => x + y, 0) / n;
  let num = 0, da = 0, db = 0;
  for (let i = 0; i < n; i++) {
    const x = a[i] - ma, y = b[i] - mb;
    num += x * y; da += x * x; db += y * y;
  }
  return da > 0 && db > 0 ? num / Math.sqrt(da * db) : 1;
};

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

// --- 3b. SHUFFLE RE-DEALS INSIDE THE ARRANGEMENT ------------------------------
// The defect this exists to prevent: an arrangement's output is a function of
// the SET of photos and the geometry, so re-ordering the bag (which is all
// Shuffle does) changed nothing at the default count — a dead button, silently,
// on ~80% of dice rolls. The re-deal must (a) still be a permutation, (b)
// actually move things, and (c) NOT destroy the ramp the arrangement builds.

console.log('3b. shuffle re-deals within the arrangement without destroying it');
{
  const rnd = rngOf(2026);
  const images = makePool(40, rnd);
  const cells = Array.from({ length: 40 }, (_, i) => ({
    cx: ((i % 8) + 0.5) / 8, cy: (Math.floor(i / 8) + 0.5) / 5, area: 1 / 40,
  }));
  for (const a of ARRANGEMENT_IDS.filter((x) => x !== 'natural')) {
    const base = arrangeBag({ bag: [...Array(40).keys()], cells, images, arrangement: a });
    const seen = new Set([base.join(',')]);
    for (let t = 1; t <= 6; t++) {
      const out = arrangeBag({ bag: [...Array(40).keys()], cells, images, arrangement: a, shuffle: t });
      check(multiset(out) === multiset(base), `${a} shuffle=${t}: re-deal broke the permutation`);
      seen.add(out.join(','));
      const twice = arrangeBag({ bag: [...Array(40).keys()], cells, images, arrangement: a, shuffle: t });
      check(twice.join(',') === out.join(','), `${a} shuffle=${t}: re-deal is not deterministic`);
    }
    check(seen.size === 7, `${a}: 6 shuffles gave only ${seen.size - 1} distinct pictures — Shuffle is a dead button`);

    // THE RAMP MUST SURVIVE — measured where it is visible, not in slot indices.
    //
    // Slot-index distance is the wrong ruler: adjacent RANKS map to spatially
    // adjacent CELLS, whose bag positions can be at opposite ends of the array,
    // so a one-rank nudge reads as a 34-slot "move" while changing almost
    // nothing on screen. What has to hold is that the picture stays a SIBLING of
    // the exact ranking — so compare, slot by slot, the metric of the photo that
    // landed there. A windowed re-deal keeps that correlated; a full shuffle
    // drops it to noise, and Spotlight stops being Spotlight.
    const spec = ARRANGEMENTS.find((x) => x.id === a);
    const shuffled = arrangeBag({ bag: [...Array(40).keys()], cells, images, arrangement: a, shuffle: 3 });
    const r = corr(base.map((v) => metric(images[v], spec.metric)),
                   shuffled.map((v) => metric(images[v], spec.metric)));
    check(r >= 0.6, `${a}: slot-by-slot metric correlation with the exact ranking is only ${r.toFixed(2)} — the re-deal is a full shuffle, not a window`);
  }
  // shuffle=0 must be byte-identical to not passing it at all.
  for (const a of ARRANGEMENT_IDS) {
    const x = arrangeBag({ bag: [...Array(40).keys()], cells, images, arrangement: a }).join(',');
    const y = arrangeBag({ bag: [...Array(40).keys()], cells, images, arrangement: a, shuffle: 0 }).join(',');
    check(x === y, `${a}: shuffle=0 must be the exact ranking`);
  }
}

// --- 3b-SMALL. SHUFFLE MUST MOVE AT THE SIZES PEOPLE ACTUALLY UPLOAD ----------
// The scar this section is: 3b swept the re-deal at n=40 only, and the re-deal
// was the IDENTITY for n <= 6 on every seed (jitter amplitude ±0.5 at the
// window floor can never cross two adjacent ranks) — measured 0/200 presses
// changing the picture at n=3..6 and 12/200 at n=8, on the shipped module,
// under every colour arrangement. A sweep that avoids the sizes a phone
// uploads proves the wrong pool. This holds the re-deal contract where the
// wish lived: 2..13 photos, plus 24 and 40 so the bound scales.

console.log('3b-small. shuffle moves the deal at every pool size, boundedly');
{
  const rnd = rngOf(4242);
  for (const n of [2, 3, 4, 5, 6, 7, 8, 10, 13, 24, 40]) {
    const images = makePool(n, rnd);
    // ONE ROW, keys monotone in the slot index. 3b's own comment is the law
    // here: slot distance is the wrong ruler for rank distance, because
    // adjacent ranks land in spatially adjacent CELLS at arbitrary slot
    // indices. On a single row with cx and area both ascending, the cell key
    // for `heat` (x), `flow` (serpentine, one even row) and `hero` (size) is
    // the identity — so the slot a photo sits in IS its rank, and the
    // displacement contract becomes measurable at the artifact without
    // re-implementing the ranking.
    const row = Array.from({ length: n }, (_, i) => ({
      cx: (i + 0.5) / n, cy: 0.5, area: (i + 1) / (n * n),
    }));
    const grid = Array.from({ length: n }, (_, i) => ({
      cx: (i % 5 + 0.5) / 5, cy: (Math.floor(i / 5) + 0.5) / Math.max(1, Math.ceil(n / 5)), area: 1 / n,
    }));
    for (const a of ['flow', 'spotlight', 'heat', 'hero']) {
      const rulered = a !== 'spotlight'; // radial key is not monotone on a row
      const cells = rulered ? row : grid;
      const bag = [...Array(n).keys()];
      const base = arrangeBag({ bag, cells, images, arrangement: a });
      const slotOf = new Map(base.map((v, i) => [v, i]));
      const bound = Math.ceil(Math.max(2, n * 0.15)) + 2;
      const outs = new Set();
      let prev = null, consecSame = 0;
      for (let seed = 1; seed <= 40; seed++) {
        const out = arrangeBag({ bag, cells, images, arrangement: a, shuffle: seed });
        const tag = `${a} n=${n} shuffle=${seed}`;
        check(multiset(out) === multiset(base), `${tag}: re-deal broke the permutation`);
        // (3) never the exact ranking — n=2 alternates instead, asserted below.
        if (n >= 3) check(out.join(',') !== base.join(','), `${tag}: press changed NOTHING — the dead button is back`);
        // (4) the displacement contract, per photo, not on average — held in
        // rank space via the monotone fixture, where slot == rank.
        if (rulered) out.forEach((v, slot) => {
          const d = Math.abs((slotOf.get(v) ?? 0) - slot);
          check(d <= bound, `${tag}: a photo moved ${d} ranks, contract says <= ${bound}`);
        });
        const j = out.join(',');
        if (prev !== null && j === prev) consecSame++;
        prev = j;
        outs.add(j);
      }
      if (n === 2) {
        // Two photos, two deals: parity alternation means EVERY press changes
        // the picture, and both deals stay reachable.
        check(consecSame === 0, `${a} n=2: a press repeated the previous deal`);
        check(outs.size === 2, `${a} n=2: expected both deals, saw ${outs.size}`);
      } else {
        // Variety floors, measured on the fixed seed list so this never flakes:
        // the deal space under a displacement bound is small at small n, but 40
        // presses repeating the immediately previous deal more than a handful
        // of times is the A/B toggle the wisher would notice.
        const varietyFloor = n <= 3 ? 4 : n <= 5 ? 10 : 18;
        check(outs.size >= varietyFloor, `${a} n=${n}: only ${outs.size} distinct deals in 40 presses (floor ${varietyFloor})`);
        // Three photos have only 5 deals inside the displacement bound, so
        // consecutive repeats are combinatorially forced there — the floor
        // loosens for n=3 and bites from 4 up, where the wish lived.
        check(consecSame <= (n === 3 ? 16 : 6), `${a} n=${n}: ${consecSame}/39 presses repeated the previous deal`);
      }
    }
  }

  // (5) EXHAUSTIVE over the trigger stream the app actually produces.
  // `handleShuffle` counts 1, 2, 3, … — so the guarantee has to hold on every
  // consecutive integer, not on a sampled handful: two independently-seeded
  // bounded permutations CAN compose towards identity, and a seed list that
  // dodges the bad trigger proves nothing. 2000 consecutive presses per size,
  // sizes 2..16 (the phone range, and where the old code was the identity),
  // on the monotone fixture so slot == rank. The moved-count floors are the
  // measured minima over 5000 triggers, asserted so they can never regress.
  console.log('3b-small-exhaustive. 2000 consecutive presses per size, sizes 2..16');
  {
    const rnd = rngOf(60309);
    for (let n = 2; n <= 16; n++) {
      const images = makePool(n, rnd);
      const row = Array.from({ length: n }, (_, i) => ({
        cx: (i + 0.5) / n, cy: 0.5, area: (i + 1) / (n * n),
      }));
      const bag = [...Array(n).keys()];
      const base = arrangeBag({ bag, cells: row, images, arrangement: 'heat' });
      const slotOf = new Map(base.map((v, i) => [v, i]));
      const bound = Math.ceil(Math.max(2, n * 0.15)) + 2;
      const movedFloor = n < 3 ? 0 : n < 8 ? 2 : 4;
      let prev = null;
      const deals = new Set();
      for (let t = 1; t <= 2000; t++) {
        const out = arrangeBag({ bag, cells: row, images, arrangement: 'heat', shuffle: t });
        const j = out.join(',');
        if (n === 2) {
          // Two deals exist; every press must flip to the other one.
          if (prev !== null) check(j !== prev, `n=2 trigger=${t}: press did not flip the deal`);
        } else {
          check(j !== base.join(','), `n=${n} trigger=${t}: the exact ranking came back — dead press`);
          let moved = 0, worst = 0;
          out.forEach((v, slot) => {
            const d = Math.abs((slotOf.get(v) ?? 0) - slot);
            if (d > 0) moved++;
            worst = Math.max(worst, d);
          });
          check(moved >= movedFloor, `n=${n} trigger=${t}: only ${moved} photos moved (floor ${movedFloor})`);
          check(worst <= bound, `n=${n} trigger=${t}: a photo moved ${worst} ranks (bound ${bound})`);
        }
        prev = j;
        deals.add(j);
      }
      if (n === 2) check(deals.size === 2, `n=2: expected both deals over 2000 presses, saw ${deals.size}`);
    }
  }
}

// --- 3c. LOCKED CELLS MUST NOT SKEW THE ROW BUCKETING -------------------------
// `rows` is derived from the mean cell AREA, not from how many slots are still
// being filled — locking two thirds of a grid must not re-band the ramp.

console.log('3c. row bucketing survives locked cells');
{
  const rnd = rngOf(31337);
  const images = makePool(36, rnd);
  const all = Array.from({ length: 36 }, (_, i) => ({
    cx: ((i % 6) + 0.5) / 6, cy: (Math.floor(i / 6) + 0.5) / 6, area: 1 / 36,
  }));
  // `flow`, not `checker`: checker alternates parity over the cells being
  // FILLED, so on a different subset "every other one" legitimately picks
  // different cells. Serpentine is the one whose banding must follow the grid.
  for (const a of ['flow']) {
    // Full grid vs the same grid with 24 cells locked away: the surviving cells
    // must still be banded as a 6-row layout, so their relative order is a
    // subsequence of the full-grid order.
    const full = arrangeBag({ bag: [...Array(36).keys()], cells: all, images, arrangement: a });
    const keep = all.filter((_, i) => i % 3 === 0);
    const keepIdx = all.map((_, i) => i).filter((i) => i % 3 === 0);
    const part = arrangeBag({ bag: keepIdx, cells: keep, images, arrangement: a });
    check(multiset(part) === multiset(keepIdx), `${a}: partial grid broke the permutation`);
    check(part.length === keepIdx.length, `${a}: partial grid changed length`);
    // Same photos, same rows: the rank of each surviving photo relative to the
    // others must not invert wholesale (a mis-banded row count inverts many).
    const fullRank = new Map(full.filter((v) => keepIdx.includes(v)).map((v, i) => [v, i]));
    let inversions = 0;
    for (let i = 0; i < part.length; i++)
      for (let j = i + 1; j < part.length; j++)
        if ((fullRank.get(part[i]) ?? 0) > (fullRank.get(part[j]) ?? 0)) inversions++;
    const pairs = (part.length * (part.length - 1)) / 2;
    check(inversions / pairs < 0.3,
      `${a}: ${((inversions / pairs) * 100).toFixed(0)}% of pairs inverted when cells were locked — the row bucketing is following the FILL count, not the grid`);
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
