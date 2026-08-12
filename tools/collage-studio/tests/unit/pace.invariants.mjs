// =============================================================================
// THE PACE — invariant sweep.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// Transpiles the REAL modules with esbuild and asserts against them — never a
// re-implementation, because a sweep that re-implements the thing it is testing
// only proves the two copies agree. The ONE re-implementation in this file is
// deliberate and is the REJECTED design (I5b): the alternative that divides each
// mode's hold by the rate instead of scaling the clock. It exists to be refuted.
//
// THE ONE THAT MATTERS IS I5: `TURN_FADE_SEC / hold` is INVARIANT under every
// rate. That is the whole argument for scaling the clock rather than the
// periods — the fade is a constant that does not divide with them, so the
// rejected design makes the fastest mode dissolve continuously instead of
// cutting faster. I5b measures exactly that failure so the choice is a number
// rather than an opinion.
//
//   node tests/unit/pace.invariants.mjs
// =============================================================================

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

const { PACE_IDS, PACES, paceRate, isPaced, paceTime } = await load('src/lib/pace.ts', 'pace');
const { TURN_IDS, TURN_FADE_SEC, NO_TURN, turnAt, turnHoldSec } = await load('src/lib/turn.ts', 'turn');
const { MOVE_IDS, MOVE_CYCLE_SEC, NO_MOVE, sampleMove } = await load('src/lib/motion.ts', 'motion');
const { encodeRoll, decodeRoll, rollDice, MINTED_GROUP_MAX } = await load('src/lib/diceRoll.ts', 'dice');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};

const PACED = PACE_IDS.filter((p) => p !== 'even');
const TURNING = TURN_IDS.filter((t) => t !== 'hold');

/** Deterministic PRNG so a failure is reproducible. */
const rngOf = (seed) => {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
};

// ---------------------------------------------------------------------------
// I1 — THE ROSTER. Index 0 is the no-op (an absent code character decodes to
//      it), the display row is the same set sorted by rate, and every rate is a
//      DYADIC rational so the scaling is exact in binary.
// ---------------------------------------------------------------------------
{
  const rates = PACE_IDS.map(paceRate);
  const dyadic = rates.every((r) => r > 0 && Number.isInteger(r * 4));
  const labels = new Set(PACES.map((p) => p.label));
  const displayIds = PACES.map((p) => p.id);
  const sameSet = displayIds.length === PACE_IDS.length
    && PACE_IDS.every((id) => displayIds.includes(id));
  let ascending = true;
  for (let i = 1; i < PACES.length; i++) {
    if (!(paceRate(PACES[i].id) > paceRate(PACES[i - 1].id))) ascending = false;
  }
  ok('I1  index 0 is `even` at rate 1, rates are dyadic, the row is the same set ascending',
    PACE_IDS[0] === 'even' && paceRate('even') === 1 && dyadic
    && labels.size === PACES.length && sameSet && ascending,
    `rates ${rates.join('/')}, row ${displayIds.join('>')}`);
}

// ---------------------------------------------------------------------------
// I2 — NEUTRAL IS IDENTITY, and junk is neutral. `Object.is`, not `===`: the
//      claim is that a build with an unset pace is the build that never had
//      one, which has to hold for -0 and for NaN as well as for 7.5.
// ---------------------------------------------------------------------------
{
  const TIMES = [0, -0, 1, -1, 0.1, 7.5, 12, 1e-9, 1e9, Number.MAX_SAFE_INTEGER,
    NaN, Infinity, -Infinity];
  const rnd = rngOf(11);
  for (let i = 0; i < 4000; i++) TIMES.push(rnd() * 600 - 60);
  const JUNK = ['even', undefined, null, '', 'nope', 5, {}, [], true];
  let bad = null;
  for (const id of JUNK) {
    for (const t of TIMES) {
      if (!Object.is(paceTime(id, t), t)) { bad = `${String(id)} @ ${t}`; break; }
      if (paceRate(id) !== 1 || isPaced(id)) { bad = `${String(id)} is not neutral`; break; }
    }
    if (bad) break;
  }
  ok('I2  an unset, unknown or `even` pace returns the clock UNCHANGED (Object.is)',
    bad === null, bad ?? `${JUNK.length} ids x ${TIMES.length} instants`);
}

// ---------------------------------------------------------------------------
// I3 — ONE MULTIPLICATION, DETERMINISTIC, ORDER-PRESERVING.
//
//      THIS ARM CORRECTED THE MODULE'S OWN HEADER. It first asserted that every
//      rate is exactly reversible because every rate is dyadic, and it failed
//      on the spot: 3/4 and 3/2 carry a factor of three, so `0.1*0.75/0.75` is
//      0.10000000000000002. Reversibility is a property NOTHING needs — no
//      caller divides by the rate. What the preview and the exporter actually
//      need is that the same clock gives the same instant, every time, and that
//      the order of instants is preserved so a schedule never runs backwards.
//      Exactness is asserted only where it is real: the powers of two.
// ---------------------------------------------------------------------------
{
  const rnd = rngOf(22);
  let bad = null;
  let checked = 0;
  for (const id of PACED) {
    const r = paceRate(id);
    const exact = Number.isInteger(Math.log2(r));   // 1/2 and 2, never 3/4 or 3/2
    let prevT = -1;
    let prevP = -Infinity;
    for (let i = 0; i < 20000; i++) {
      const t = i % 3 === 0 ? i / 30 : rnd() * 3600;
      const p = paceTime(id, t);
      checked++;
      if (p !== t * r) { bad = `${id} @ ${t}: ${p} !== ${t * r}`; break; }
      if (!Object.is(p, paceTime(id, t))) { bad = `${id} @ ${t} is not deterministic`; break; }
      if (exact && p / r !== t) { bad = `${id} @ ${t} lost a power-of-two round trip`; break; }
      if (Math.abs(p / r - t) > Number.EPSILON * Math.abs(t)) { bad = `${id} @ ${t} drifted > 1 ulp`; break; }
      if (t > prevT && !(p > prevP)) { bad = `${id} @ ${t} did not preserve order`; break; }
      prevT = t; prevP = p;
    }
    if (bad) break;
  }
  ok('I3  paceTime is exactly t*rate, deterministic, order-preserving, exact on the powers of two',
    bad === null, bad ?? `${checked} instants x ${PACED.length} rates`);
}

// ---------------------------------------------------------------------------
// I4 — REST AT ZERO SURVIVES EVERY RATE, BY REFERENCE. 0*r is 0, so the three
//      surfaces that pass no time (still preview, raster export, SVG) are
//      bit-identical to a build with no pace in it.
// ---------------------------------------------------------------------------
{
  let bad = null;
  for (const p of PACE_IDS) {
    const t0 = paceTime(p, 0);
    for (const id of TURN_IDS) {
      if (turnAt(id, t0) !== NO_TURN) { bad = `turn ${id} @ pace ${p}`; break; }
    }
    for (const id of MOVE_IDS) {
      for (const ph of [0, 0.25, 0.5, 0.9]) {
        if (sampleMove({ id, ph }, t0) !== NO_MOVE) { bad = `move ${id}/${ph} @ pace ${p}`; break; }
      }
    }
    if (bad) break;
  }
  ok('I4  t=0 is NO_TURN and NO_MOVE by REFERENCE at every pace', bad === null,
    bad ?? `${PACE_IDS.length} paces x ${TURN_IDS.length} turns x ${MOVE_IDS.length} moves`);
}

// ---------------------------------------------------------------------------
// I5 — THE ONE THAT MATTERS. The share of the take spent DISSOLVING is the same
//      at every rate, because the fade and the hold are read off the same
//      scaled clock. Measured by walking a long window at 1 ms and counting
//      samples with mix > 0.
// ---------------------------------------------------------------------------
const duty = (id, rate, at) => {
  const hold = turnHoldSec(id);
  // FORTY HOLDS AT EVERY RATE, NOT FORTY SECONDS. A fixed window covers half as
  // many holds at 0.5x, and the first hold of any window carries no dissolve —
  // so the boundary is a larger share of a shorter count and the duty reads
  // 16.6% against 17.1% for a feature that is behaving perfectly. Measured, and
  // it is an artefact of the instrument rather than of the thing measured: the
  // window has to be scale-free before the statistic means anything.
  const window = (hold * 40) / paceRate(rate);
  const step = 0.001;
  let soft = 0;
  let n = 0;
  for (let t = 0; t < window; t += step) {
    n++;
    if (at(id, t, rate).mix > 0) soft++;
  }
  return soft / n;
};
const realAt = (id, t, rate) => turnAt(id, paceTime(rate, t));
{
  let bad = null;
  const rows = [];
  for (const id of TURNING) {
    const base = duty(id, 'even', realAt);
    for (const p of PACED) {
      const d = duty(id, p, realAt);
      if (Math.abs(d - base) > 0.004) bad = `${id} @ ${p}: ${(d * 100).toFixed(2)}% vs ${(base * 100).toFixed(2)}%`;
    }
    rows.push(`${id} ${(base * 100).toFixed(1)}%`);
  }
  ok('I5  the dissolve is the same FRACTION of the take at every rate', bad === null,
    bad ?? rows.join(', '));
}

// ---------------------------------------------------------------------------
// I5b — THE RED PROOF. The rejected design — divide each mode's hold by the
//       rate and leave TURN_FADE_SEC alone — is re-implemented here ONLY so it
//       can be measured failing. It has to diverge, or I5 is asserting nothing.
// ---------------------------------------------------------------------------
{
  // The rejected alternative, faithfully: same schedule, hold scaled, fade not.
  const rejectedAt = (id, t, rate) => {
    const hold = turnHoldSec(id) / paceRate(rate);
    if (!(hold > 0) || !(t > 0)) return NO_TURN;
    const k = Math.floor(t / hold);
    if (k <= 0) return NO_TURN;
    const elapsed = t - k * hold;
    if (!(elapsed < TURN_FADE_SEC)) return { a: k, b: k, mix: 0 };
    return { a: k - 1, b: k, mix: 0.5 - 0.5 * Math.cos(Math.PI * (elapsed / TURN_FADE_SEC)) };
  };
  const worst = { id: null, base: 0, got: 0 };
  for (const id of TURNING) {
    const base = duty(id, 'even', rejectedAt);
    for (const p of PACED) {
      const d = duty(id, p, rejectedAt);
      if (d - base > worst.got - worst.base) { worst.id = `${id}@${p}`; worst.base = base; worst.got = d; }
    }
  }
  // The fastest mode is the one that degenerates first: `ripple` holds 3.5s and
  // dissolves 0.7s of it, so at 2x it is soft 40% of the time instead of 20%.
  const ripple2 = duty('ripple', 'rush', rejectedAt);
  ok('I5b the REJECTED design (divide the hold) doubles the dissolve share — refuted',
    ripple2 > 0.35 && worst.got - worst.base > 0.15,
    `ripple 20.0% -> ${(ripple2 * 100).toFixed(1)}% soft at 2x; worst ${worst.id} `
    + `${(worst.base * 100).toFixed(1)}% -> ${(worst.got * 100).toFixed(1)}%`);
}

// ---------------------------------------------------------------------------
// I6 — THE SCHEDULE IS THE SAME SCHEDULE, READ SOONER. The turn indices reached
//      in [0, T] at rate r are exactly those reached in [0, T*r] at 1x.
// ---------------------------------------------------------------------------
{
  let bad = null;
  let checked = 0;
  for (const id of TURNING) {
    for (const p of PACED) {
      const r = paceRate(p);
      const T = 120;
      const paced = [];
      const plain = [];
      for (let i = 0; i <= 2400; i++) {
        const t = (i / 2400) * T;
        paced.push(turnAt(id, paceTime(p, t)).a);
        plain.push(turnAt(id, t * r).a);
      }
      checked += paced.length;
      if (paced.join() !== plain.join()) { bad = `${id} @ ${p}`; break; }
      const cuts = new Set(paced).size;
      const at1x = new Set(Array.from({ length: 2401 }, (_, i) => turnAt(id, (i / 2400) * T).a)).size;
      // Not exactly r x the count (the window ends mid-hold), but it must move
      // in the right direction and by the right order of magnitude.
      if (r > 1 && !(cuts > at1x)) { bad = `${id} @ ${p} did not cut more often (${cuts} vs ${at1x})`; break; }
      if (r < 1 && !(cuts < at1x)) { bad = `${id} @ ${p} did not cut less often (${cuts} vs ${at1x})`; break; }
    }
    if (bad) break;
  }
  ok('I6  a paced schedule is the plain schedule at a scaled instant, and cuts more/less often',
    bad === null, bad ?? `${checked} instants`);
}

// ---------------------------------------------------------------------------
// I7 — THE MOVE'S PERIOD SCALES EXACTLY. One full cycle at the paced period
//      lands on rest BY REFERENCE — 12/r is exact for every rate in the roster,
//      which is the dyadic property doing real work.
// ---------------------------------------------------------------------------
{
  let bad = null;
  for (const p of PACE_IDS) {
    const period = MOVE_CYCLE_SEC / paceRate(p);
    for (const id of MOVE_IDS) {
      for (const ph of [0, 0.13, 0.5, 0.77]) {
        for (const k of [1, 2, 5]) {
          if (sampleMove({ id, ph }, paceTime(p, k * period)) !== NO_MOVE) {
            bad = `${id}/${ph} @ ${p} after ${k} cycles`;
          }
        }
      }
    }
  }
  ok('I7  a full cycle at the PACED period is rest, by reference', bad === null,
    bad ?? PACE_IDS.map((p) => `${p}:${MOVE_CYCLE_SEC / paceRate(p)}s`).join(' '));
}

// ---------------------------------------------------------------------------
// I8 — THE CODE CARRIES IT. Round trip over every pace, and the group is the
//      generation this build actually mints.
//
//      NOT A LITERAL. This assertion carried `22` and broke the moment THE BEAT
//      appended its own character — which is the SECOND time this exact line
//      has broken in a sibling sweep for the same reason (C144 filed it after
//      grade/motion/turn all pinned `21`). The property is "one character longer
//      than the generation I am about to rebuild in I9", and that is a fact the
//      codec owns and exports.
// ---------------------------------------------------------------------------
{
  let bad = null;
  let checked = 0;
  const rnd = rngOf(4242);
  for (let i = 0; i < 300; i++) {
    const r = rollDice({ rnd });
    for (const p of PACE_IDS) {
      const code = encodeRoll({ ...r, pace: p }, '');
      const back = decodeRoll(code, '');
      checked++;
      if (!back) { bad = `refused its own output: ${code}`; break; }
      if (back.pace !== p) { bad = `${p} came back as ${back.pace}`; break; }
      if (code.split('-')[1].length !== MINTED_GROUP_MAX) { bad = `group is ${code.split('-')[1].length} characters, expected ${MINTED_GROUP_MAX}`; break; }
      for (const k of ['layout', 'primitive', 'count', 'countOwned', 'entropy', 'aspect',
                       'gutter', 'zoom', 'bg', 'arrangement', 'focus', 'twist', 'look', 'move', 'turn', 'seed']) {
        if (JSON.stringify(back[k]) !== JSON.stringify(r[k] ?? back[k])) { bad = `field ${k} moved`; break; }
      }
      if (bad) break;
    }
    if (bad) break;
  }
  ok(`I8  every pace survives the round trip in a ${MINTED_GROUP_MAX}-character group`, bad === null,
    bad ?? `${checked} codes`);
}

// ---------------------------------------------------------------------------
// I9 — EVERY EARLIER GENERATION STILL OPENS. Rebuild the 18/19/20/21-character
//      forms from a real code, re-derive each checksum, and assert they decode
//      with the fields they had and no-ops for the ones they did not. This is
//      the back-compatibility rule (`>=`, never `===`) proved rather than
//      asserted in a comment.
// ---------------------------------------------------------------------------
{
  // The codec's own checksum, re-derived here because it is not exported. If
  // this drifts from diceRoll.ts every arm below fails loudly, which is the
  // behaviour we want from a duplicated constant.
  const checksum = (body) => {
    let h = 7;
    for (let i = 0; i < body.length; i++) h = (h * 31 + parseInt(body[i], 36) + 1) % 1679616;
    return (h % 36 ** 2).toString(36).padStart(2, '0');
  };
  // body length -> the fields that generation carried, and what the ones after
  // it must decode to.
  const GENERATIONS = [
    { len: 16, absent: { look: 'none', move: 'still', turn: 'hold', pace: 'even' } },
    { len: 17, absent: { move: 'still', turn: 'hold', pace: 'even' } },
    { len: 18, absent: { turn: 'hold', pace: 'even' } },
    { len: 19, absent: { pace: 'even' } },
  ];
  let bad = null;
  let checked = 0;
  const rnd = rngOf(909);
  for (let i = 0; i < 12 && !bad; i++) {
    const r = { ...rollDice({ rnd }), look: 'noir', move: 'sway', turn: 'march', pace: 'rush' };
    const code = encodeRoll(r, '');
    const [a, b, c] = code.toLowerCase().split('-');
    const now = decodeRoll(code, '');
    for (const g of GENERATIONS) {
      const body = b.slice(0, g.len);
      const legacy = `${a}-${body}${checksum(a + body + c)}-${c}`.toUpperCase();
      const back = decodeRoll(legacy, '');
      checked++;
      if (!back) { bad = `a ${g.len + 2}-character group was refused: ${legacy}`; break; }
      for (const [k, v] of Object.entries(g.absent)) {
        if (back[k] !== v) { bad = `${g.len + 2}: absent ${k} opened as ${back[k]}, not ${v}`; break; }
      }
      if (bad) break;
      const carried = ['layout', 'primitive', 'count', 'countOwned', 'entropy', 'aspect',
        'gutter', 'zoom', 'bg', 'arrangement', 'focus', 'twist', 'seed']
        .concat(g.len >= 17 ? ['look'] : [])
        .concat(g.len >= 18 ? ['move'] : [])
        .concat(g.len >= 19 ? ['turn'] : []);
      for (const k of carried) {
        if (JSON.stringify(back[k]) !== JSON.stringify(now[k])) {
          bad = `${g.len + 2}: field ${k} moved (${back[k]} vs ${now[k]})`; break;
        }
      }
      if (bad) break;
    }
  }
  ok('I9  the 18/19/20/21-character generations still open, unmoved, as no-ops',
    bad === null, bad ?? `${checked} rebuilt legacy codes`);
}

// ---------------------------------------------------------------------------
// I10 — THE DOORS STAY SHUT. An over-long group, an out-of-roster pace index
//       and a truncation are refused rather than defaulted.
// ---------------------------------------------------------------------------
{
  let bad = null;
  const r = { ...rollDice({ rnd: rngOf(31337) }), pace: 'brisk' };
  const code = encodeRoll(r, '');
  const [a, b, c] = code.toLowerCase().split('-');
  if (decodeRoll(`${a}-${b}x-${c}`, '') !== null) bad = 'a 23-character group was accepted';
  if (decodeRoll(`${a}-${b}zz-${c}`, '') !== null) bad = 'a 24-character group was accepted';
  const hi = (PACE_IDS.length + 3).toString(36);
  const forged = `${a}-${b.slice(0, 19)}${hi}${b.slice(20)}-${c}`;
  if (decodeRoll(forged, '') !== null) bad = 'an out-of-roster pace index was accepted';
  for (const len of [16, 17, 19, 20, 21]) {
    if (decodeRoll(`${a}-${b.slice(0, len)}-${c}`, '') !== null) bad = `a truncated ${len}-character group was accepted`;
  }
  ok('I10 over-long, forged and truncated groups are refused, never defaulted', bad === null, bad ?? '');
}

// ---------------------------------------------------------------------------
// I11 — THE DICE. It never rolls a tempo for a collage with no clock, it
//       reaches every rate when there is one, and it is deterministic.
// ---------------------------------------------------------------------------
{
  const seen = new Map();
  let onClock = 0;
  let evenOnClock = 0;
  let paceWithoutClock = 0;
  const N = 6000;
  const rnd = rngOf(777);
  for (let i = 0; i < N; i++) {
    const r = rollDice({ rnd });
    const live = (r.move ?? 'still') !== 'still' || (r.turn ?? 'hold') !== 'hold';
    const p = r.pace ?? 'even';
    if (live) {
      onClock++;
      if (p === 'even') evenOnClock++;
      seen.set(p, (seen.get(p) ?? 0) + 1);
    } else if (p !== 'even') paceWithoutClock++;
  }
  const evenPct = (evenOnClock / Math.max(1, onClock)) * 100;
  const reachedAll = PACE_IDS.every((p) => (seen.get(p) ?? 0) > 0);
  const a = rollDice({ rnd: rngOf(5150) });
  const b = rollDice({ rnd: rngOf(5150) });
  ok('I11 the dice rolls no tempo without a clock, reaches every rate with one, and repeats',
    paceWithoutClock === 0 && reachedAll && evenPct > 42 && evenPct < 70
    && JSON.stringify(a) === JSON.stringify(b),
    `${paceWithoutClock} tempos on still collages, ${onClock} on the clock, `
    + `${evenPct.toFixed(1)}% even, ${seen.size}/${PACE_IDS.length} reached`);
}

// ---------------------------------------------------------------------------
// I12 — THE SEAM IS MONOTONE. A faster pace is never behind a slower one on the
//       same clock: the whole promise of the control in one line.
// ---------------------------------------------------------------------------
{
  let bad = null;
  const order = PACES.map((p) => p.id);
  for (let t = 0.5; t <= 300; t += 0.5) {
    for (let i = 1; i < order.length; i++) {
      if (!(paceTime(order[i], t) > paceTime(order[i - 1], t))) {
        bad = `${order[i]} not ahead of ${order[i - 1]} at t=${t}`; break;
      }
    }
    if (bad) break;
  }
  ok('I12 a faster pace is strictly ahead on the clock at every instant', bad === null, bad ?? '600 instants');
}

console.log('\nTHE PACE — invariant sweep\n' + '='.repeat(66));
for (const line of results) console.log(line);
console.log('='.repeat(66));
console.log(failures === 0 ? `ALL ${results.length} INVARIANTS HOLD` : `${failures} FAILED`);
process.exit(failures === 0 ? 0 : 1);
