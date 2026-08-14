/**
 * Invariant sweep for the POOL CEILING on the dice — src/lib/diceRoll.ts
 * `poolCeiling` / `countBandFor`, and `rollDice` end to end.
 *
 * Run: node tests/unit/diceRollCount.invariants.mjs
 *
 * WISHED FOR (wishing well, kind=bug): *"You should make randomize the same
 * count as the images uploaded — why everytime I hit random it does over 100 it
 * should be within range of the number of images sent."*
 *
 * It BUNDLES the REAL module (esbuild walks the real import graph, so the recipe
 * table and the generator roster swept here are the shipped ones, never a stub)
 * and drives every pool size x every recipe x thousands of seeds.
 *
 * THE INVARIANTS
 *   I1  NEVER RAISES        — a pool can only ever LOWER a roll. The band is
 *                             never higher at the top or at the bottom than the
 *                             one it was given, so nothing anybody liked before
 *                             became unreachable. This is the whole safety case.
 *   I2  ZERO IS UNTOUCHED   — with no pool the band IS the curated band, exactly,
 *                             for all 23 recipes and all 23 generators. Every
 *                             call site written before `sources` existed is
 *                             bit-for-bit unchanged.
 *   I3  CEILING HONOURED    — a rolled count never exceeds max(3n, 24).
 *   I4  DENSITY COUNTED     — and neither does count x density, which is the
 *                             number the readout actually prints.
 *   I5  STILL A DICE        — a count pins only where the figure's own minimum
 *                             has met the budget, never because a band was
 *                             squeezed onto its own low end.
 *   I6  ROSTER INTACT       — a name goes missing at a pool size only when its
 *                             FIGURE cannot physically be drawn under that
 *                             ceiling. Admission by physics, never by taste —
 *                             the panel's loudest attack, pinned as a test.
 *   I7  FIGURE FLOOR        — a count is never under the construction's own
 *                             minimum, unless the ceiling itself is under it.
 *   I8  RECIPES FIT FIGURES — no recipe asks for fewer cells than its generator
 *                             declares it can draw. This is WHY I2 holds by
 *                             construction rather than by luck.
 *   I9  DETERMINISTIC       — same stream, same opts, same roll.
 *   I10 BAND SANE           — 1 <= lo <= hi < Infinity for every input, including
 *                             the degenerate ones.
 *   I11 THE DATA IS TRUE    — `deliveredFloor` and `overshoot` are re-measured
 *                             against the real generators every run, so neither
 *                             can become a comment that outlives its code.
 *   I12 RESIDUE BANDED      — the request is a target the constructions may
 *                             miss, so the promise is a BOUNDED miss on
 *                             delivered cells, and the bound is asserted.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

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

const { rollDice, countBandFor, poolCeiling, deliveredFloorOf, overshootOf, RECIPES, MAX_REPEATS, MIN_FIGURE, MIN_SPREAD } =
  await load('src/lib/diceRoll.ts', 'dicecount');
const { GENERATORS, GENERATOR_BY_ID } = await load('src/engine/geom/generators/index.ts', 'generators');
const { computeLayout, createRng } = await load('src/lib/layout.ts', 'layout');

// mulberry32 — a small deterministic PRNG so each seed is a distinct fixture.
const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

let fails = 0;
const check = (ok, msg) => { if (!ok) { fails++; if (fails <= 25) console.error(`  ✗ ${msg}`); } };

/** Pool sizes that matter: one photo, a handful, the wisher's twelve, a shoot. */
const POOLS = [0, 1, 2, 3, 5, 8, 12, 20, 24, 30, 40, 60, 80, 120, 200, 500];
const DENSITIES = [1, 2, 3, 4];
const SEEDS = 900;

console.log(`dice pool-ceiling sweep — ${POOLS.length} pools x ${SEEDS} seeds, MAX_REPEATS=${MAX_REPEATS} MIN_FIGURE=${MIN_FIGURE}`);

// =============================================================================
// I8 — recipes fit inside the figures they name (checked first: I2 rests on it)
// =============================================================================
for (const r of RECIPES) {
  const spec = GENERATOR_BY_ID[r.layout];
  check(!!spec, `I8: recipe "${r.name}" names a generator that is not in the roster (${r.layout})`);
  if (!spec) continue;
  check(r.count[0] >= spec.countRange[0],
    `I8: recipe "${r.name}" asks for ${r.count[0]} cells but ${r.layout} declares a minimum of ${spec.countRange[0]}`);
  check(r.count[0] < r.count[1], `I8: recipe "${r.name}" has an empty band ${r.count}`);
}

// =============================================================================
// I1 / I2 / I7 / I10 — the pure band, over every curated band there is
// =============================================================================
const BANDS = [
  ...RECIPES.map((r) => ({ what: `recipe ${r.name}`, wanted: r.count, figureMin: GENERATOR_BY_ID[r.layout].countRange[0], overshoot: GENERATOR_BY_ID[r.layout].overshoot ?? 1 })),
  ...GENERATORS.map((g) => ({ what: `generator ${g.id}`, wanted: g.countRange, figureMin: g.countRange[0], overshoot: g.overshoot ?? 1 })),
  { what: 'the [8,120] fallback', wanted: [8, 120], figureMin: 8, overshoot: 1 },
];

for (const b of BANDS) {
  for (const n of POOLS) {
    for (const d of DENSITIES) {
      const [lo, hi] = countBandFor(b.wanted, b.figureMin, n, d, b.overshoot);

      // I10 — sane, always.
      check(Number.isFinite(lo) && Number.isFinite(hi), `I10: ${b.what} n=${n} d=${d} band not finite: [${lo}, ${hi}]`);
      check(lo >= 1, `I10: ${b.what} n=${n} d=${d} low end under 1: ${lo}`);
      check(lo <= hi, `I10: ${b.what} n=${n} d=${d} inverted band [${lo}, ${hi}]`);

      // I1 — a pool never RAISES a roll. Both ends, no exceptions.
      check(hi <= b.wanted[1], `I1: ${b.what} n=${n} d=${d} raised the ceiling ${b.wanted[1]} -> ${hi}`);
      check(lo <= Math.max(b.wanted[0], Math.min(b.figureMin, hi)),
        `I1: ${b.what} n=${n} d=${d} raised the floor ${b.wanted[0]} -> ${lo}`);

      // I7 — never under what the construction needs, unless the ceiling is.
      check(lo >= Math.min(b.figureMin, hi),
        `I7: ${b.what} n=${n} d=${d} low ${lo} is under the figure minimum ${b.figureMin}`);

      // I2 — no pool means no change, exactly.
      if (n === 0) {
        check(lo === b.wanted[0] && hi === b.wanted[1],
          `I2: ${b.what} d=${d} changed with NO pool: [${b.wanted}] -> [${lo}, ${hi}]`);
      }

      // The ceiling itself, on the band.
      if (n > 0) {
        const cap = poolCeiling(n, d) / b.overshoot;
        check(hi <= cap + 1e-9, `I3: ${b.what} n=${n} d=${d} ceiling ${cap.toFixed(1)} breached by ${hi}`);
      }
    }
  }
}

// =============================================================================
// I3 / I4 / I5 / I6 — the whole roll, driven the way the button is pressed
// =============================================================================
const reachedAt = new Map();   // pool -> { recipes:Set, generators:Set }
const countsAt = new Map();    // `${pool}|${recipeOrGen}` -> Set of counts

for (const n of POOLS) {
  const seen = { recipes: new Set(), generators: new Set() };
  for (let s = 0; s < SEEDS; s++) {
    const roll = rollDice({ rnd: rngOf(s * 7919 + n * 104729), sources: n, hasVideo: true });
    seen.recipes.add(roll.recipe ?? '(free roll)');
    seen.generators.add(roll.layout);

    const key = `${n}|${roll.recipe ?? roll.layout}`;
    if (!countsAt.has(key)) countsAt.set(key, new Set());
    countsAt.get(key).add(roll.count);

    if (n > 0) {
      const cap = poolCeiling(n, 1) / overshootOf(roll.layout);
      // I3 — the ceiling, on the number the roll actually chose, aimed below the
      // budget by what this figure is known to overshoot.
      check(roll.count <= cap,
        `I3: n=${n} seed=${s} rolled ${roll.count} fragments, ceiling is ${cap.toFixed(1)} (${roll.recipe ?? roll.layout})`);
      check(roll.count >= 1, `I3: n=${n} seed=${s} rolled a non-positive count ${roll.count}`);
    }
  }
  reachedAt.set(n, seen);
}

// I4 — density is inside the ceiling, because the readout prints count x density.
for (const n of [1, 3, 12, 40]) {
  for (const d of DENSITIES) {
    for (let s = 0; s < 300; s++) {
      const roll = rollDice({ rnd: rngOf(s * 31337 + n + d * 7), sources: n, density: d, hasVideo: true });
      const onScreen = roll.count * d;
      const budget = Math.max(n * MAX_REPEATS, MIN_FIGURE) / overshootOf(roll.layout);
      check(onScreen <= budget + 1e-9,
        `I4: n=${n} density=${d} seed=${s} put ${onScreen} fragments on screen (${roll.count} x ${d}), budget ${budget.toFixed(1)}`);
    }
  }
}

// I6 — the roster does not collapse. This is the attack the panel pressed
// hardest: a fix that filters recipes by their curated count band trades the
// wisher's bug for "the dice always says Manuscript". The only name allowed to
// go missing at a pool size is one whose FIGURE cannot physically be drawn under
// that ceiling — admission by physics, never by taste — and this asserts the
// distinction rather than trusting it.
const base = reachedAt.get(0);
const layoutOfRecipe = new Map(RECIPES.map((r) => [r.name, r.layout]));
for (const n of POOLS) {
  if (n === 0) continue;
  const seen = reachedAt.get(n);
  const cap = poolCeiling(n, 1);
  for (const r of base.recipes) {
    if (seen.recipes.has(r)) continue;
    const layout = layoutOfRecipe.get(r);
    check(!!layout && deliveredFloorOf(layout) > cap,
      `I6: recipe "${r}" vanished at n=${n} and its figure CAN be drawn under ${cap} — that is a taste filter`);
  }
  for (const g of base.generators) {
    if (seen.generators.has(g)) continue;
    check(deliveredFloorOf(g) > cap,
      `I6: generator "${g}" vanished at n=${n} and its floor (${deliveredFloorOf(g)}) fits under ${cap}`);
  }
  // ...and the roster stays broad in absolute terms, whatever the reason.
  check(seen.recipes.size >= base.recipes.size - 2,
    `I6: n=${n} reaches only ${seen.recipes.size} of ${base.recipes.size} recipe names`);
  check(seen.generators.size >= base.generators.size - 2,
    `I6: n=${n} reaches only ${seen.generators.size} of ${base.generators.size} generators`);
}

// I5 — still a dice, and every pinned count is EXPLAINED.
//
// The first draft pinned Cathedral to exactly 90 at a pool of 30, because the
// ceiling landed on the recipe's own low end — a squeeze with room either side
// of it, and MIN_SPREAD exists to reopen exactly that. But a pin is not always a
// defect: at two photographs the budget is 24 cells and a kaleidoscope needs 12
// before it is a kaleidoscope, so once the request is aimed below the 2.2x this
// figure overshoots by, there is genuinely one admissible number and no amount
// of rolling will find a second. So the assertion is not "never pins" — it is
// "pins only where the figure's own minimum has met the budget", which is a
// claim that can be false.
const layoutOfName = new Map([
  ...RECIPES.map((r) => [r.name, r.layout]),
  ...GENERATORS.map((g) => [g.id, g.id]),
]);
for (const [key, counts] of countsAt) {
  if (counts.size > 1) continue;
  const cut = key.indexOf('|');
  const n = Number(key.slice(0, cut));
  const label = key.slice(cut + 1);
  const layout = layoutOfName.get(label);
  const figureMin = layout ? (GENERATOR_BY_ID[layout]?.countRange?.[0] ?? 1) : 1;
  const capReq = poolCeiling(n, 1) / (layout ? overshootOf(layout) : 1);
  check(capReq < figureMin * MIN_SPREAD,
    `I5: at n=${n}, "${label}" returned the same count (${[...counts][0]}) on every roll, ` +
    `and its budget (${capReq.toFixed(1)}) had room above its minimum (${figureMin}) — that is a pinned band, not a physical squeeze`);
}
// The stronger form: across the whole roll at each pool, the count must take many
// values — a dice with three outcomes is a switch.
for (const n of POOLS) {
  const all = new Set();
  for (let s = 0; s < SEEDS; s++) all.add(rollDice({ rnd: rngOf(s * 7919 + n * 104729), sources: n, hasVideo: true }).count);
  check(all.size >= 8, `I5: n=${n} produced only ${all.size} distinct fragment counts across ${SEEDS} rolls`);
}

// I9 — deterministic.
for (const n of [0, 3, 12, 80]) {
  for (let s = 0; s < 60; s++) {
    const a = rollDice({ rnd: rngOf(s), sources: n, hasVideo: true });
    const b = rollDice({ rnd: rngOf(s), sources: n, hasVideo: true });
    check(JSON.stringify(a) === JSON.stringify(b), `I9: n=${n} seed=${s} two rolls off the same stream differ`);
  }
}

// =============================================================================
// I11 — THE SHIPPED DELIVERY FACTS ARE STILL TRUE
//
// `deliveredFloor` and `overshoot` are measurements living in a source file, and
// a measurement in a source file is a comment unless something re-takes it. This
// re-takes both against the REAL generator and fails on drift — the file's own
// scar, "a docstring is not a test", applied to the data this fix rests on.
// =============================================================================
const ASPECTS = [1, 0.6667, 1.5, 1.7778, 0.5625];
const pctl = (a, q) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length * q)]; };

for (const g of GENERATORS) {
  let floor = Infinity;
  const ratios = [];
  for (const a of ASPECTS) {
    for (const seed of [1, 99]) {
      for (const req of [1, 4, 8]) {
        const items = await computeLayout(1200, 1200 / a, req, createRng(seed), g.id, 0.005, 0.4, [], 'rect', 0, a);
        if (items.length > 0) floor = Math.min(floor, items.length);
      }
      // The SAME statistic the shipped number is — p75 over the LOW band. A
      // drift gate that measures a different statistic is not a drift gate, it
      // is a units mismatch that fails on day one and gets deleted on day two.
      for (const req of [8, 10, 12, 14, 16, 20, 24, 30, 36, 48]) {
        const items = await computeLayout(1200, 1200 / a, req, createRng(seed), g.id, 0.005, 0.4, [], 'rect', 0, a);
        if (items.length > 0) ratios.push(items.length / req);
      }
    }
  }
  const shippedFloor = deliveredFloorOf(g.id);
  const shippedOver = overshootOf(g.id);
  const measuredOver = Math.max(1, pctl(ratios, 0.75));
  // The floor must not be OPTIMISTIC — admitting a figure that cannot fit is the
  // failure this data exists to prevent. A pessimistic floor only costs variety,
  // so the tolerance is deliberately one-sided and generous the safe way.
  check(floor <= shippedFloor * 1.25 + 1,
    `I11: ${g.id} declares a delivered floor of ${shippedFloor} but could not go below ${floor}`);
  check(Math.abs(measuredOver - shippedOver) <= 0.45 + shippedOver * 0.25,
    `I11: ${g.id} overshoot drifted — shipped ${shippedOver}, measured ${measuredOver.toFixed(2)}`);
}

// =============================================================================
// I12 — THE RESIDUE IS BANDED, AND STATED
//
// The request is a target the constructions are free to miss (App.tsx says so),
// so a ceiling on the request cannot be a promise about cells. What it CAN be is
// a bounded miss, and this pins the bound: the share of rolls whose DELIVERED
// cells exceed the ceiling, and how far the worst one goes. Both were 79% and
// 12x before the fix. If a future change re-widens either, this fails loudly
// instead of quietly.
// =============================================================================
// Bands set FROM the measurement (600 rolls per pool, delivered cells against
// the ceiling), with headroom for the smaller sample this runs. Measured:
//   n=1   10.7% over, p90 1.04x, worst 1.79x (truchet asked 7)
//   n=3   10.8% over, p90 1.04x, worst 2.00x (mandala asked 10)
//   n=12   2.8% over, p90 0.89x, worst 1.72x (mandala asked 15)
//   n=40   0.0% over, p90 0.73x, worst 1.00x
// Every outlier is a QUANTISED figure landing on its next admissible rung —
// mandala's ring counts, truchet's tiling, kaleidoscope's whole wedges — which
// no scalar aim can fix, only a filter that deleted them could. Before the fix
// the same measurement at n=12 read 79.3% over and 12x worst.
const RESIDUE = [
  { n: 3, maxShare: 0.18, maxRatio: 2.2 },
  { n: 12, maxShare: 0.08, maxRatio: 2.0 },
  { n: 40, maxShare: 0.03, maxRatio: 1.3 },
];
const residueReport = [];
for (const r of RESIDUE) {
  const cap = poolCeiling(r.n, 1);
  let over = 0, worst = 0;
  const K = 140;
  for (let s = 0; s < K; s++) {
    const roll = rollDice({ rnd: rngOf(s * 6151 + r.n), sources: r.n, hasVideo: true });
    const items = await computeLayout(1200, 1200 / roll.aspect, roll.count, createRng(roll.seed), roll.layout, roll.gutter, roll.entropy, [], 'rect', 0, roll.aspect);
    if (items.length > cap) over++;
    worst = Math.max(worst, items.length);
  }
  residueReport.push({ n: r.n, cap, share: over / K, worst });
  check(over / K <= r.maxShare,
    `I12: n=${r.n} — ${((over / K) * 100).toFixed(1)}% of rolls DELIVER over the ${cap}-cell ceiling (band is ${(r.maxShare * 100).toFixed(0)}%)`);
  check(worst <= cap * r.maxRatio,
    `I12: n=${r.n} — worst roll delivered ${worst} cells against a ${cap} ceiling (band is ${r.maxRatio}x)`);
}

// =============================================================================
// THE REPORT — the numbers the wish is about, printed so a reader can see the
// fix rather than trust it. `sources: 0` reproduces the pre-fix roll exactly.
// =============================================================================
const med = (a) => pctl(a, 0.5);
const p90 = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length * 0.9)]; };
console.log('\n  pool   before(med/p90/max)   after(med/p90/max)   ceiling   recipes reached');
for (const n of [1, 3, 12, 40, 80]) {
  const before = [], after = [];
  for (let s = 0; s < SEEDS; s++) {
    before.push(rollDice({ rnd: rngOf(s * 7919 + n * 104729), sources: 0, hasVideo: true }).count);
    after.push(rollDice({ rnd: rngOf(s * 7919 + n * 104729), sources: n, hasVideo: true }).count);
  }
  console.log(
    `  ${String(n).padStart(4)}   ${String(med(before)).padStart(4)}/${String(p90(before)).padStart(4)}/${String(Math.max(...before)).padStart(4)}` +
    `        ${String(med(after)).padStart(4)}/${String(p90(after)).padStart(4)}/${String(Math.max(...after)).padStart(4)}` +
    `        ${String(poolCeiling(n, 1)).padStart(4)}   ${reachedAt.get(n).recipes.size}/${base.recipes.size}`
  );
}

console.log(fails === 0 ? '\n✓ all invariants hold' : `\n✗ ${fails} failure(s)`);
process.exit(fails === 0 ? 0 : 1);
