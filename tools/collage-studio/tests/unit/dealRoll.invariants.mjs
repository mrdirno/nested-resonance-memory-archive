/**
 * Invariant sweep for src/lib/dealRoll.ts — THE COLOUR DICE.
 *
 * Run: node tests/unit/dealRoll.invariants.mjs
 *
 * It BUNDLES the REAL module (esbuild walks the real import graph, so the
 * arrangement/twist family tables imported here are the shipped ones, not a
 * stub), and sweeps every generator in the roster x 400 seeds x 120 CHAINED
 * rolls each.
 *
 * CHAINED, not independent — because that is how the button is actually
 * pressed. The field presses it repeatedly to compare, feeding each result
 * straight back in as `previous`, and the failure this sweep exists to catch is
 * exactly the one an independent-draw test cannot see: a roll that hands back
 * the picture already on screen. A dice that changes nothing is a broken
 * button, and one press in a few hundred landing on a no-op is frequent enough
 * to be noticed and rare enough to survive a spot check.
 *
 * THE INVARIANTS
 *   1. NEVER `natural`         — the un-sorted order is not a colour sort.
 *   2. ALWAYS DIFFERENT        — never returns its own `previous`, ever.
 *   3. VALID                   — every id is a member of its shipped roster.
 *   4. BOUNDED                 — a fixed ceiling of rng draws, so it cannot spin.
 *   5. DETERMINISTIC           — same stream in, same deal out.
 *   6. NOTHING UNREACHABLE     — every sorted arrangement, every focus and every
 *                                twist actually comes up.
 *   7. STRAIGHT IN BAND        — the crop leans often enough to be a feature and
 *                                rarely enough to still cost something.
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

const { rollDeal, SORTED_ARRANGEMENT_IDS, DEAL_STRAIGHT_CHANCE } =
  await load('src/lib/dealRoll.ts', 'dealroll');
const { ARRANGEMENT_IDS, FOCUS_IDS, TWIST_IDS } = await load('src/lib/composition.ts', 'composition');
const { GENERATORS } = await load('src/engine/geom/generators/index.ts', 'generators');

// mulberry32 — a small deterministic PRNG so each seed is a distinct fixture.
const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

let fails = 0;
const check = (ok, msg) => { if (!ok) { fails++; if (fails <= 20) console.error(`  ✗ ${msg}`); } };

const key = (d) => `${d.arrangement}|${d.focus}|${d.twist}`;

// =============================================================================
// 0. THE ROSTER THE DICE DRAWS FROM
// =============================================================================
console.log('— roster —');
check(SORTED_ARRANGEMENT_IDS.length === ARRANGEMENT_IDS.length - 1,
  `sorted roster should be the arrangement roster minus one, got ${SORTED_ARRANGEMENT_IDS.length} of ${ARRANGEMENT_IDS.length}`);
check(!SORTED_ARRANGEMENT_IDS.includes('natural'), 'sorted roster must not contain `natural`');
check(SORTED_ARRANGEMENT_IDS.every((id) => ARRANGEMENT_IDS.includes(id)),
  'every sorted arrangement must be a real arrangement');
check(DEAL_STRAIGHT_CHANCE > 0 && DEAL_STRAIGHT_CHANCE < 1,
  `straight chance must leave both outcomes reachable, got ${DEAL_STRAIGHT_CHANCE}`);
console.log(`  ${SORTED_ARRANGEMENT_IDS.length} sorted arrangements, straight chance ${DEAL_STRAIGHT_CHANCE}`);

// =============================================================================
// 1-4, 6-7. THE CHAINED SWEEP — every generator, 400 seeds, 120 presses each
// =============================================================================
console.log('— chained rolls: every generator x 400 seeds x 120 presses —');

const layouts = GENERATORS.map((g) => g.id);
const seenArrangement = new Set();
const seenFocus = new Set();
const seenTwist = new Set();
let rolls = 0;
let straight = 0;
let maxDraws = 0;
let collisions = 0;   // how often the step-forward path was actually needed

for (const layout of layouts) {
  for (let s = 0; s < 400; s++) {
    const base = rngOf(s * 7919 + layout.length * 31);
    let draws = 0;
    const rnd = () => { draws++; return base(); };

    // Start from the app's own default deal — natural/auto/none — which is what
    // the button is pressed against the first time.
    let prev = { arrangement: 'natural', focus: 'auto', twist: 'none' };

    for (let p = 0; p < 120; p++) {
      draws = 0;
      const d = rollDeal({ layout, previous: prev, rnd });
      rolls++;
      maxDraws = Math.max(maxDraws, draws);

      // 3. VALID
      check(ARRANGEMENT_IDS.includes(d.arrangement), `${layout}/${s}/${p}: bogus arrangement ${d.arrangement}`);
      check(FOCUS_IDS.includes(d.focus), `${layout}/${s}/${p}: bogus focus ${d.focus}`);
      check(TWIST_IDS.includes(d.twist), `${layout}/${s}/${p}: bogus twist ${d.twist}`);
      // 1. NEVER natural
      check(d.arrangement !== 'natural', `${layout}/${s}/${p}: colour dice returned the unsorted order`);
      // 2. ALWAYS DIFFERENT
      check(key(d) !== key(prev), `${layout}/${s}/${p}: roll returned the deal already on screen (${key(d)})`);

      seenArrangement.add(d.arrangement);
      seenFocus.add(d.focus);
      seenTwist.add(d.twist);
      if (d.twist === 'none') straight++;
      prev = d;
    }
  }
}

// 4. BOUNDED — the ceiling is arrangement(3) + focus(1) + twist(3).
check(maxDraws <= 7, `a roll took ${maxDraws} rng draws; the bound is 7 (no retry loop is allowed)`);
console.log(`  ${rolls.toLocaleString()} chained rolls, max ${maxDraws} rng draws per roll`);

// 6. NOTHING UNREACHABLE
for (const id of SORTED_ARRANGEMENT_IDS) check(seenArrangement.has(id), `arrangement \`${id}\` is unreachable by the colour dice`);
for (const id of FOCUS_IDS) check(seenFocus.has(id), `focus \`${id}\` is unreachable by the colour dice`);
for (const id of TWIST_IDS) check(seenTwist.has(id), `twist \`${id}\` is unreachable by the colour dice`);
console.log(`  reached ${seenArrangement.size}/${SORTED_ARRANGEMENT_IDS.length} arrangements, ${seenFocus.size}/${FOCUS_IDS.length} focus modes, ${seenTwist.size}/${TWIST_IDS.length} twists`);

// 7. STRAIGHT IN BAND
const straightShare = straight / rolls;
check(straightShare > 0.30 && straightShare < 0.60,
  `straight share ${(straightShare * 100).toFixed(1)}% is outside the 30-60% band`);
console.log(`  straight ${(straightShare * 100).toFixed(1)}% of rolls`);

// =============================================================================
// 2b. THE COLLISION PATH IS REACHABLE AND CORRECT
//
// The step-forward branch is the whole guarantee behind "always different", and
// a branch no test ever enters is a branch nobody has proved. Force it: hand
// the roll a `previous` equal to the deal it is about to draw.
// =============================================================================
console.log('— the collision path —');
for (const layout of layouts.slice(0, 6)) {
  for (let s = 0; s < 300; s++) {
    // Draw once to learn what this stream produces...
    const drawn = rollDeal({ layout, rnd: rngOf(s) });
    // ...then replay the SAME stream with that as `previous`. The roll must
    // notice and move.
    const again = rollDeal({ layout, previous: drawn, rnd: rngOf(s) });
    collisions++;
    check(key(again) !== key(drawn), `${layout}/${s}: forced collision returned the same deal ${key(drawn)}`);
    check(again.arrangement !== 'natural', `${layout}/${s}: collision step landed on the unsorted order`);
    check(SORTED_ARRANGEMENT_IDS.includes(again.arrangement), `${layout}/${s}: collision step left the roster (${again.arrangement})`);
    check(again.focus === drawn.focus && again.twist === drawn.twist,
      `${layout}/${s}: collision step should move the arrangement only`);
  }
}
console.log(`  ${collisions} forced collisions, all stepped to a different sorted arrangement`);

// =============================================================================
// 5. DETERMINISTIC — same stream in, same deal out
// =============================================================================
console.log('— determinism —');
let detChecks = 0;
for (const layout of layouts) {
  for (let s = 0; s < 40; s++) {
    const a = rollDeal({ layout, rnd: rngOf(s) });
    const b = rollDeal({ layout, rnd: rngOf(s) });
    check(key(a) === key(b), `${layout}/${s}: same stream produced ${key(a)} then ${key(b)}`);
    detChecks++;
  }
}
console.log(`  ${detChecks} replays, all identical`);

// =============================================================================
console.log('');
if (fails) { console.error(`FAILED — ${fails} assertion(s)`); process.exit(1); }
console.log(`PASSED — ${rolls.toLocaleString()} chained rolls + ${collisions} forced collisions + ${detChecks} replays, 0 failures`);
