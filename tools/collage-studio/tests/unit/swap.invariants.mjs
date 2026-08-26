/**
 * Invariant sweep for THE SWAP — two fragments trading pictures.
 *
 * Run: node tests/unit/swap.invariants.mjs
 *
 * It transpiles the REAL `src/lib/swap.ts` (esbuild, types stripped), so the
 * plan measured here is the plan the click handler performs.
 *
 * WHY A SWEEP AND NOT A COUPLE OF EXAMPLES. A swap writes TWO pieces of live
 * state that must agree — the assignment and the pin table — and the failure
 * that matters is not "it crashed", it is "the trade came undone forty seconds
 * later when the gutter moved". That shape is invisible to a happy-path test:
 * it only appears when you re-run the deal, which is what I9 does.
 *
 * I1  THE MULTISET IS PRESERVED. `sorted(out) === sorted(in)`, always. A swap is
 *     a transposition, so it can neither create nor destroy a placed picture —
 *     this is what keeps `assignSources`' duplicate-free guarantee intact.
 * I2  EXACTLY TWO POSITIONS MOVE, and they move into each other. Every other
 *     slot is `Object.is`-identical to the input, holes and `-1`s included.
 * I3  ORDER-INDEPENDENT. `planSwap(…, a, b)` is deep-equal to
 *     `planSwap(…, b, a)` — field for field, including the order of the two
 *     rewritten pins. Which fragment you tapped first is not a decision.
 * I4  SELF-INVERSE ON THE ASSIGNMENT. Swap, swap back, and the indices are the
 *     array you started with. (The PINS are deliberately not self-inverse:
 *     they gain two entries the first time. I4b measures that they return to
 *     naming the original pictures.)
 * I5  A PIN AGREES WITH WHAT ITS CELL HOLDS. After the plan,
 *     `locks[a] === images[out[a]].id` and the same for b. This is the
 *     invariant the whole feature rests on.
 * I6  NO COLLATERAL IN THE PIN TABLE. Every well-formed pin on a cell outside
 *     {a,b} survives verbatim and in order; no pin is invented for a third cell.
 * I6b EVERY RETURNED PIN IS AN ARRAY, so the caller's very next line —
 *     `setLockedCells(new Map(plan.locks))` — can neither throw (`new Map([null])`
 *     does) nor invent a pin out of a string (`new Map(['ab'])` yields
 *     `{'a' => 'b'}`). Found BY this sweep, which is why it is written down.
 * I7  A PIN NEVER NAMES AN ABSENT ASSET — every id written is really in the pool.
 * I8  REFUSALS ARE INERT. On any refusal the returned indices and locks are
 *     equal by value to the inputs, so a caller that applies a refused plan
 *     changes nothing. And every refusal is either SAID or is a stale-index
 *     case the hand cannot reach.
 * I9  THE REDEAL INVARIANT — THE ONE THAT MATTERS. Re-run the assignment pass's
 *     lock step (a faithful transcription of App.tsx's `lockedCells.forEach`)
 *     against the post-swap pins, and the two cells come back holding the
 *     SWAPPED pictures. This is the difference between a swap and a swap that
 *     survives a gutter nudge, and it is the assertion that kills the
 *     indices-only implementation.
 * I10 TOTAL. Null pools, holes, `-1`s, non-integer slots, duplicate ids, a
 *     malformed pin table: a refusal, never a throw.
 * I11 AN EMPTY FRAGMENT IS NOT A DESTINATION, in BOTH directions (DECISION 4).
 * I12 THE SAME PICTURE IN BOTH CELLS IS A NO-OP AND SAYS SO — because focus and
 *     twist are keyed on the SLOT, so nothing on screen would have moved.
 * I13 THE BUTTON APPEARS EXACTLY WHEN THE TRADE IS AVAILABLE. `canSwapFrom`
 *     decides whether the puck offers a third verb at all, and it must agree
 *     with `planSwap` on every assignment — a Swap button over a fragment with
 *     no possible partner is the inert-control defect, and a MISSING one over a
 *     fragment that could trade is worse.
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
    target: 'es2020',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const S = await load('src/lib/swap.ts', 'swap');

let checks = 0;
let fails = 0;
const ok = (cond, msg) => {
  checks++;
  if (!cond) { fails++; console.error(`  FAIL: ${msg}`); }
};

// A tiny deterministic PRNG so a failure is reproducible from the seed alone.
const mulberry = (s) => () => {
  s |= 0; s = (s + 0x6D2B79F5) | 0;
  let t = Math.imul(s ^ (s >>> 15), 1 | s);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const eq = (x, y) => JSON.stringify(x) === JSON.stringify(y);

/**
 * THE REDEAL MODEL — a faithful transcription of the assignment effect's lock
 * step in src/App.tsx:
 *
 *     const imageIdToIndex = new Map(images.map((img, i) => [img.id, i]));
 *     lockedCells.forEach((imgId, cellIdx) => {
 *       const currentImgIdx = imageIdToIndex.get(imgId);
 *       if (cellIdx < slotCount && currentImgIdx !== undefined) {
 *         newIndices[cellIdx] = currentImgIdx;
 *       }
 *     });
 *
 * Everything not pinned is re-dealt by the seeded bag, which is exactly what a
 * swap must NOT depend on — so the model only has to answer for the pinned
 * cells, and that is the whole claim being measured.
 */
const redealPinned = (images, locks, slotCount) => {
  const byId = new Map(images.map((im, i) => [im.id, i]));
  const out = new Array(slotCount).fill(-1);
  // `new Map(entries)` is what the app builds from `plan.locks`, so LAST wins on
  // a duplicated cell — modelled here rather than assumed.
  const asMap = new Map(locks);
  asMap.forEach((imgId, cellIdx) => {
    const i = byId.get(imgId);
    if (cellIdx < slotCount && i !== undefined) out[cellIdx] = i;
  });
  return out;
};

// ---------------------------------------------------------------------------
// THE SWEEP — random pools, random assignments (holes, -1s, repeats and all),
// random pre-existing pin tables, every ordered pair of slots.
// ---------------------------------------------------------------------------
let cases = 0;
let okPlans = 0;
let refusals = { 'same-cell': 0, 'out-of-range': 0, 'empty-cell': 0, 'same-picture': 0 };
let sawRepeatPlacement = 0;
let sawPrePinned = 0;
let sawHole = 0;

for (let seed = 1; seed <= 900; seed++) {
  const rng = mulberry(seed * 7919);
  const nImages = 1 + Math.floor(rng() * 9);           // 1..9 pool entries
  const images = Array.from({ length: nImages }, (_, i) => {
    const isClipFrame = rng() < 0.35;
    return {
      id: `a${i}`,
      ...(isClipFrame ? { sourceName: `clip${i % 3}.mov` } : {}),
      ...(rng() < 0.75 ? { originalName: `IMG_${i}.jpg` } : {}),
    };
  });

  const nSlots = 1 + Math.floor(rng() * 12);           // 1..12 fragments
  const indices = Array.from({ length: nSlots }, () => {
    const r = rng();
    if (r < 0.10) { sawHole++; return -1; }             // an unfilled slot
    if (r < 0.14) return undefined;                     // a slot the bag never reached
    return Math.floor(rng() * nImages);                 // may repeat: pool < slots
  });
  // Repeats are the interesting case for I12 and they must actually occur.
  const placed = indices.filter((v) => typeof v === 'number' && v >= 0);
  if (new Set(placed).size < placed.length) sawRepeatPlacement++;

  // A pre-existing pin table over random cells, sometimes naming a departed id.
  const locks = [];
  for (let c = 0; c < nSlots; c++) {
    if (rng() < 0.25) {
      const i = indices[c];
      const id = (typeof i === 'number' && i >= 0 && images[i]) ? images[i].id : `a${nImages + 1}`;
      locks.push([c, id]);
    }
  }
  if (locks.length) sawPrePinned++;

  for (let a = 0; a < nSlots; a++) {
    for (let b = 0; b < nSlots; b++) {
      cases++;
      const plan = S.planSwap(images, indices, locks, a, b);
      const lo = Math.min(a, b), hi = Math.max(a, b);

      ok(Array.isArray(plan.indices) && Array.isArray(plan.locks), 'always a plan with both tables');
      ok(plan.a === lo && plan.b === hi, 'the plan reports the pair in a fixed order');

      // --- I3 ORDER-INDEPENDENT -------------------------------------------
      const mirror = S.planSwap(images, indices, locks, b, a);
      ok(eq(plan, mirror), `I3 seed ${seed}: planSwap(${a},${b}) must equal planSwap(${b},${a})`);

      if (!plan.ok) {
        refusals[plan.why] = (refusals[plan.why] ?? 0) + 1;
        // --- I8 REFUSALS ARE INERT --------------------------------------
        ok(eq(plan.indices, indices.map((v) => (v === undefined ? null : v))) || eq(plan.indices, indices),
          `I8 seed ${seed}: a refused plan returns the assignment unchanged`);
        ok(eq(plan.locks, locks.filter(Array.isArray)),
          `I8 seed ${seed}: a refused plan writes no pin and rewrites none`);
        ok(plan.pinned === false, 'I8: a refusal pins nothing');
        // A refusal is either SAID, or is one of the two the hand cannot reach.
        const said = S.describeSwap(plan);
        if (plan.why === 'same-picture' || plan.why === 'empty-cell') {
          ok(said.length > 0, `I8 seed ${seed}: refusal "${plan.why}" must say something`);
        } else {
          ok(said === '', `I8: refusal "${plan.why}" is a stale-index case and stays silent`);
        }
        continue;
      }

      okPlans++;
      const A = indices[lo], B = indices[hi];

      // --- I2 EXACTLY TWO POSITIONS MOVE ----------------------------------
      ok(plan.indices.length === indices.length, 'I2: the assignment keeps its length');
      ok(Object.is(plan.indices[lo], B) && Object.is(plan.indices[hi], A),
        `I2 seed ${seed}: slots ${lo}/${hi} must hold each other's picture`);
      let moved = 0;
      for (let k = 0; k < indices.length; k++) {
        if (k === lo || k === hi) continue;
        if (!Object.is(plan.indices[k], indices[k])) moved++;
      }
      ok(moved === 0, `I2 seed ${seed}: ${moved} slot(s) outside the pair moved`);

      // --- I1 THE MULTISET IS PRESERVED -----------------------------------
      const key = (arr) => arr.map((v) => (v === undefined ? 'u' : String(v))).sort().join(',');
      ok(key(plan.indices) === key(indices), `I1 seed ${seed}: the swap changed WHICH pictures are placed`);

      // --- I5 A PIN AGREES WITH WHAT ITS CELL HOLDS -----------------------
      const m = new Map(plan.locks);
      ok(m.get(lo) === images[plan.indices[lo]].id, `I5 seed ${seed}: cell ${lo}'s pin must name what it now holds`);
      ok(m.get(hi) === images[plan.indices[hi]].id, `I5 seed ${seed}: cell ${hi}'s pin must name what it now holds`);

      // --- I6 NO COLLATERAL IN THE PIN TABLE ------------------------------
      const before = locks.filter(Array.isArray).filter(([c]) => c !== lo && c !== hi);
      const after = plan.locks.filter(([c]) => c !== lo && c !== hi);
      ok(eq(before, after), `I6 seed ${seed}: pins on other cells must survive verbatim and in order`);
      ok(plan.locks.length === before.length + 2, 'I6: exactly two pins are written');

      // --- I7 A PIN NEVER NAMES AN ABSENT ASSET (for the two we wrote) ----
      ok(images.some((im) => im.id === m.get(lo)), 'I7: the pin written at a is a real asset');
      ok(images.some((im) => im.id === m.get(hi)), 'I7: the pin written at b is a real asset');

      // --- I9 THE REDEAL INVARIANT ----------------------------------------
      // Pool ids are unique by construction here, which is what makes
      // `imageIdToIndex` unambiguous — the duplicate-id case is I10's, where a
      // refusal or a total answer is all that is claimed.
      const redealt = redealPinned(images, plan.locks, indices.length);
      ok(redealt[lo] === plan.indices[lo],
        `I9 seed ${seed}: cell ${lo} must come back holding the swapped picture after a re-deal`);
      ok(redealt[hi] === plan.indices[hi],
        `I9 seed ${seed}: cell ${hi} must come back holding the swapped picture after a re-deal`);

      // --- I4 SELF-INVERSE ON THE ASSIGNMENT ------------------------------
      const back = S.planSwap(images, plan.indices, plan.locks, lo, hi);
      ok(back.ok, 'I4: swapping back is always available');
      ok(eq(back.indices, indices.map((v) => (v === undefined ? null : v))) || eq(back.indices, indices),
        `I4 seed ${seed}: swap then swap back must restore the assignment`);
      // I4b — the pins return to naming the ORIGINAL pictures, even though the
      // table itself has grown by up to two entries.
      const bm = new Map(back.locks);
      ok(bm.get(lo) === images[A].id && bm.get(hi) === images[B].id,
        `I4b seed ${seed}: swapping back re-pins the original pictures`);

      // --- the notice ------------------------------------------------------
      const said = S.describeSwap(plan);
      ok(typeof said === 'string' && said.length > 0, 'a successful swap always says something');
      if (plan.pinned) ok(/pinned/.test(said), 'the first trade discloses that both cells are now pinned');
    }
  }
}

// ---------------------------------------------------------------------------
// I13 — the button's rule and the trade's rule are the same rule.
// ---------------------------------------------------------------------------
{
  let offered = 0, withheld = 0;
  for (let seed = 1; seed <= 300; seed++) {
    const rng = mulberry(seed * 104729);
    const nImages = 1 + Math.floor(rng() * 5);
    const images = Array.from({ length: nImages }, (_, i) => ({ id: `a${i}`, originalName: `IMG_${i}.jpg` }));
    const nSlots = 1 + Math.floor(rng() * 6);
    const indices = Array.from({ length: nSlots }, () => {
      const r = rng();
      if (r < 0.25) return -1;
      if (r < 0.30) return undefined;
      return Math.floor(rng() * nImages);
    });
    for (let slot = 0; slot < nSlots; slot++) {
      const offeredHere = S.canSwapFrom(images, indices, slot);
      let anyPartner = false;
      for (let j = 0; j < nSlots && !anyPartner; j++) {
        if (j !== slot && S.planSwap(images, indices, [], slot, j).ok) anyPartner = true;
      }
      ok(offeredHere === anyPartner,
        `I13 seed ${seed}: the Swap button at slot ${slot} must appear iff a trade is possible`);
      if (offeredHere) offered++; else withheld++;
    }
  }
  ok(offered > 0 && withheld > 0, 'I13: both the offered and the withheld case were reached');
  // The degenerate collages, named rather than left to the draw.
  ok(S.canSwapFrom([{ id: 'a0' }], [0], 0) === false, 'I13: one fragment has nobody to trade with');
  ok(S.canSwapFrom([{ id: 'a0' }], [0, 0, 0], 0) === false, 'I13: a wall of the same picture has nobody either');
  ok(S.canSwapFrom([{ id: 'a0' }, { id: 'a1' }], [0, -1], 0) === false, 'I13: an empty partner is no partner');
  ok(S.canSwapFrom([{ id: 'a0' }, { id: 'a1' }], [0, 1], 0) === true, 'I13: two different pictures can trade');
  ok(S.canSwapFrom(null, null, 0) === false, 'I13: total — nothing to trade with in an empty app');
}

ok(cases > 20_000, `swept ${cases} ordered slot pairs`);
ok(okPlans > 0, 'successful swaps were exercised');
ok(refusals['empty-cell'] > 0, 'I11: the empty-fragment trap was actually planted');
ok(refusals['same-picture'] > 0, 'I12: the same-picture no-op was actually reached');
ok(refusals['same-cell'] > 0, 'the a===b cancel path was reached');

// The out-of-range arm cannot be reached from the loop above (its slots are
// valid by construction), and an unreached trap is not a planted one. This is
// the stale-arming case: a cell index taken from a partition that has since
// been replaced by a shorter one.
{
  const images = [{ id: 'a0', originalName: 'one.jpg' }, { id: 'a1', originalName: 'two.jpg' }];
  const idx = [0, 1];
  const locks = [[0, 'a0']];
  for (const [a, b] of [[0, 2], [2, 0], [5, 9], [-1, 0], [0, -1], [1.5, 0], [NaN, 1], [0, Infinity]]) {
    const p = S.planSwap(images, idx, locks, a, b);
    ok(!p.ok && p.why === 'out-of-range', `a slot outside the assignment is refused (${a},${b})`);
    ok(eq(p.indices, idx) && eq(p.locks, locks), 'and a stale arming moves nothing');
    ok(S.describeSwap(p) === '', 'and stays silent — the hand cannot cause it');
    refusals['out-of-range']++;
  }
}
ok(refusals['out-of-range'] > 0, 'the stale-arming trap was actually planted');
ok(sawRepeatPlacement > 0, 'assignments with a repeated picture were generated');
ok(sawPrePinned > 0, 'pre-existing pin tables were generated');
ok(sawHole > 0, 'unfilled slots were generated');

// ---------------------------------------------------------------------------
// I11 — an empty fragment is not a destination, in BOTH directions, stated as
// examples rather than left to the random draw.
// ---------------------------------------------------------------------------
{
  const images = [{ id: 'a0', originalName: 'one.jpg' }, { id: 'a1', originalName: 'two.jpg' }];
  for (const empty of [-1, undefined, null, 99, 1.5, NaN, '0']) {
    const withHoleAtEnd = S.planSwap(images, [0, empty], [], 0, 1);
    ok(!withHoleAtEnd.ok && withHoleAtEnd.why === 'empty-cell', `I11: trading INTO ${String(empty)} is refused`);
    const withHoleAtStart = S.planSwap(images, [empty, 0], [], 0, 1);
    ok(!withHoleAtStart.ok && withHoleAtStart.why === 'empty-cell', `I11: trading FROM ${String(empty)} is refused`);
    ok(S.describeSwap(withHoleAtEnd) === 'That fragment is empty — nothing to trade.', 'I11: and it says so');
  }
  // A slot pointing past the end of the pool is empty, not a crash.
  ok(S.planSwap(images, [0, 7], [], 0, 1).why === 'empty-cell', 'I11: an index past the pool is empty');
  // An asset with no usable id is not a picture you can pin, so it is empty.
  ok(S.planSwap([{ id: 'a0' }, { id: '' }], [0, 1], [], 0, 1).why === 'empty-cell',
    'I11: an asset with a blank id cannot be pinned, so it cannot be traded');
  ok(S.planSwap([{ id: 'a0' }, null], [0, 1], [], 0, 1).why === 'empty-cell',
    'I11: a null pool entry is empty');
}

// ---------------------------------------------------------------------------
// I12 — the same picture in both cells changes nothing, and says so.
// ---------------------------------------------------------------------------
{
  const images = [{ id: 'a0', originalName: 'one.jpg' }];
  const p = S.planSwap(images, [0, 0, 0], [], 0, 2);
  ok(!p.ok && p.why === 'same-picture', 'I12: trading a picture with itself is refused');
  ok(S.describeSwap(p) === 'Those two fragments are showing the same picture.', 'I12: and it names the reason');
  ok(eq(p.indices, [0, 0, 0]), 'I12: and nothing moved');
}

// ---------------------------------------------------------------------------
// I10 — TOTAL, against inputs no assignment should ever hold.
// ---------------------------------------------------------------------------
{
  const NASTY_POOLS = [
    null, undefined, [], [null, undefined],
    [{ id: 'x' }, { id: 'x' }],                    // the same id twice
    [{}, { id: '' }],
    [{ id: 'a' }, { id: 3 }],
    [{ id: 'a', originalName: null }, { id: 'b', sourceName: 7 }],
  ];
  const NASTY_INDICES = [
    null, undefined, [], [0], [0, 1], [-1, -1], [undefined, undefined],
    [0, '1'], [0, 1.5], [NaN, 0], [0, Infinity], [{}, []],
  ];
  const NASTY_LOCKS = [
    null, undefined, [], [[0, 'a']], [[0, 'a'], [0, 'b']], [[-3, 'a']],
    [null], [[]], [['0', 'a']], [[0, null]], [[0, 'ghost']],
  ];
  const NASTY_SLOTS = [0, 1, -1, 1.5, NaN, Infinity, '0', null, undefined, 99];

  for (const pool of NASTY_POOLS) {
    for (const idx of NASTY_INDICES) {
      for (const lk of NASTY_LOCKS) {
        for (const a of NASTY_SLOTS) {
          const p = S.planSwap(pool, idx, lk, a, 1);
          ok(typeof p.ok === 'boolean', 'I10: always a plan');
          ok(Array.isArray(p.indices) && Array.isArray(p.locks), 'I10: always both tables');
          // I6b — stated where the malformed tables actually live. This is the
          // assertion that caught the real defect: `new Map(plan.locks)` is the
          // caller's next line and it is not a total function.
          ok(p.locks.every(Array.isArray),
            'I6b: every returned pin is an array, so new Map(plan.locks) is safe');
          ok((() => { try { new Map(p.locks); return true; } catch { return false; } })(),
            'I6b: and new Map(plan.locks) really does not throw');
          ok(typeof S.describeSwap(p) === 'string', 'I10: always a sentence, even an empty one');
          if (p.ok) {
            // Whatever it accepted, the two structural promises still hold.
            ok(p.indices.length === (Array.isArray(idx) ? idx.length : 0), 'I10: length preserved even here');
            const m = new Map(p.locks);
            ok(typeof m.get(p.a) === 'string' && typeof m.get(p.b) === 'string',
              'I10: an accepted swap always writes two real pins');
          }
        }
      }
    }
  }
}

// ---------------------------------------------------------------------------
// THE SHAPE THE UI DEPENDS ON — a worked example, spelled out, so a reader can
// see the whole feature in twelve lines.
// ---------------------------------------------------------------------------
{
  const images = [
    { id: 'a0', originalName: 'dog.jpg' },
    { id: 'a1', originalName: 'beach.jpg' },
    { id: 'a2', sourceName: 'surf.mov' },
  ];
  const indices = [0, 1, 2];
  const p = S.planSwap(images, indices, [], 0, 2);
  ok(eq(p.indices, [2, 1, 0]), 'the worked example transposes the ends');
  ok(eq(p.locks, [[0, 'a2'], [2, 'a0']]), 'and pins both to what they now hold');
  ok(S.describeSwap(p) === 'Swapped dog.jpg and surf.mov. Both are pinned now, so a remix keeps them.',
    'and the sentence names both files and discloses the pins');
  // A second trade on an already-pinned pair does not repeat the disclosure.
  const q = S.planSwap(images, p.indices, p.locks, 0, 1);
  ok(q.pinned === false && S.describeSwap(q) === 'Swapped surf.mov and beach.jpg.',
    'a later trade on pinned cells says the short sentence');
  ok(eq(q.locks, [[2, 'a0'], [0, 'a1'], [1, 'a2']]), 'and the untouched pin at cell 2 rides through');
}

console.log(
  fails === 0
    ? `swap invariants: ${checks} assertions over ${cases} slot pairs — all green ` +
      `(${okPlans} swaps · refusals: ${JSON.stringify(refusals)})`
    : `swap invariants: ${fails} FAILURES out of ${checks} assertions`,
);
process.exit(fails === 0 ? 0 : 1);
