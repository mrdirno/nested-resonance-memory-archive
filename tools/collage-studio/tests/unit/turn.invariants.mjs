// =============================================================================
// THE TURN — invariant sweep.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// Transpiles the REAL modules with esbuild and asserts against them — never a
// re-implementation, because a sweep that re-implements the thing it is testing
// only proves the two copies agree.
//
// THE ONE THAT MATTERS IS I2: every state THE TURN can reach is a PERMUTATION.
// The app's oldest promise about what a collage is — source-first and
// duplicate-free (lib/fill.ts) — is a STATIC guarantee, and a time axis is
// exactly the kind of feature that voids one quietly. So this file proves the
// property directly, over every mode, at every fragment count from 1 to 64, for
// forty consecutive turns, across seeds.
//
//   node tests/unit/turn.invariants.mjs
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

const {
  TURN_IDS, TURNS, TURN_FADE_SEC, MAX_TURN_INDEX, NO_TURN,
  turnAt, assignmentAt, isTurning, turnHoldSec, scatterStride,
} = await load('src/lib/turn.ts', 'turn');

const { encodeRoll, decodeRoll, rollDice, MINTED_GROUP_MAX } = await load('src/lib/diceRoll.ts', 'dice');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};

const ACTIVE = TURN_IDS.filter((t) => t !== 'hold');

/** Deterministic PRNG so a failure is reproducible. */
const rngOf = (seed) => {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
};

// ---------------------------------------------------------------------------
// I1 — REST IS THE SHARED OBJECT, and rest covers everything before turn 1.
// ---------------------------------------------------------------------------
{
  let bad = null;
  // `hold` never turns, at any time this app can reach.
  for (const t of [0, 0.001, 1, 5, 12, 60, 600, 86_400]) {
    if (turnAt('hold', t) !== NO_TURN) bad = `hold@${t}`;
  }
  // Every active mode is at rest for its whole first hold, and at t=0 exactly.
  for (const id of ACTIVE) {
    const hold = turnHoldSec(id);
    for (const f of [0, 0.01, 0.25, 0.5, 0.9, 0.999]) {
      if (turnAt(id, hold * f) !== NO_TURN) bad = `${id}@${(hold * f).toFixed(3)}`;
    }
  }
  // Junk in, rest out — by reference, never a fabricated frame.
  for (const junk of [undefined, null, NaN, -1, -0.0001, 'still', {}, Infinity, -Infinity]) {
    if (turnAt('march', junk) !== NO_TURN) bad = `march@junk:${String(junk)}`;
    if (turnAt(junk, 12) !== NO_TURN) bad = `junkId:${String(junk)}`;
  }
  ok('I1  rest is the shared NO_TURN object, by reference', bad === null, bad ?? 'hold, first hold, and every junk input');
}

// ---------------------------------------------------------------------------
// I2 — EVERY STATE IS A PERMUTATION. The load-bearing one.
// ---------------------------------------------------------------------------
{
  let bad = null;
  let checked = 0;
  for (const id of TURN_IDS) {
    for (let n = 1; n <= 64 && !bad; n++) {
      for (const seed of [0, 1, 7, 12345, 2 ** 31 - 1]) {
        for (let k = 0; k <= 40; k++) {
          const a = assignmentAt(id, k, n, seed);
          checked++;
          if (a.length !== n) { bad = `${id} n=${n} k=${k}: length ${a.length}`; break; }
          const seen = new Uint8Array(n);
          for (let j = 0; j < n; j++) {
            const v = a[j];
            if (!(v >= 0 && v < n)) { bad = `${id} n=${n} k=${k}: out of range ${v}`; break; }
            if (seen[v]) { bad = `${id} n=${n} k=${k}: DUPLICATE picture ${v}`; break; }
            seen[v] = 1;
          }
          if (bad) break;
        }
        if (bad) break;
      }
    }
  }
  ok('I2  every assignment is a permutation — no two fragments share a picture',
    bad === null, bad ?? `${checked.toLocaleString()} assignments, 5 modes x n=1..64 x 5 seeds x k=0..40`);
}

// ---------------------------------------------------------------------------
// I2b — TURN 0 IS THE DEAL. What the still preview, the raster export and the
//       SVG draw has to be the identity, or the video opens on a different
//       collage than the picture the user was looking at.
// ---------------------------------------------------------------------------
{
  let bad = null;
  for (const id of TURN_IDS) {
    for (let n = 0; n <= 40; n++) {
      const a = assignmentAt(id, 0, n, 999);
      for (let j = 0; j < n; j++) if (a[j] !== j) bad = `${id} n=${n} slot ${j} -> ${a[j]}`;
      // Negative / junk turn indices are turn 0, never a fabricated state.
      for (const k of [-1, -99, NaN, undefined, null, 'x']) {
        const b = assignmentAt(id, k, n, 999);
        for (let j = 0; j < n; j++) if (b[j] !== j) bad = `${id} n=${n} k=${String(k)}`;
      }
    }
  }
  // `hold` is the identity forever, not merely at 0.
  for (let k = 0; k <= 200; k++) {
    const a = assignmentAt('hold', k, 24, 5);
    for (let j = 0; j < 24; j++) if (a[j] !== j) bad = `hold k=${k}`;
  }
  ok('I2c turn 0 is the identity deal, and `hold` is the identity forever', bad === null, bad ?? '');
}

// ---------------------------------------------------------------------------
// I3 — A TURN ACTUALLY TURNS. A chip that does nothing is a lie about the
//      roster, and `ripple` degenerates below n=4 unless it falls back.
// ---------------------------------------------------------------------------
{
  let bad = null;
  for (const id of ACTIVE) {
    for (let n = 2; n <= 40; n++) {
      let moved = false;
      for (let k = 1; k <= 2 && !moved; k++) {
        const a = assignmentAt(id, k, n, 4242);
        for (let j = 0; j < n; j++) if (a[j] !== j) { moved = true; break; }
      }
      if (!moved) bad = `${id} n=${n} is the identity through k=2`;
    }
  }
  ok('I3  every active mode moves at least one picture within 2 turns, n>=2', bad === null, bad ?? '');
}

// ---------------------------------------------------------------------------
// I4 — THE DISSOLVE IS CONTINUOUS AND BOUNDED. `a` and `b` are consecutive so
//      one step permutation separates them; mix walks 0..1 and comes back.
// ---------------------------------------------------------------------------
{
  let bad = null;
  let sawFade = 0;
  for (const id of ACTIVE) {
    const hold = turnHoldSec(id);
    let prev = turnAt(id, 0);
    for (let t = 0; t <= hold * 12; t += 0.01) {
      const f = turnAt(id, t);
      if (!(f.mix >= 0 && f.mix <= 1)) { bad = `${id}@${t.toFixed(2)} mix=${f.mix}`; break; }
      if (f.b !== f.a && f.b !== f.a + 1) { bad = `${id}@${t.toFixed(2)} a=${f.a} b=${f.b}`; break; }
      if (f.mix > 0) sawFade++;
      if (f.a < prev.a) { bad = `${id}@${t.toFixed(2)} a went backwards`; break; }
      // NO VISIBLE JUMP. The fully-painted deal is `a`; the only instant it may
      // advance is one where the outgoing picture had already faded to nothing,
      // so the wall never hard-cuts between two deals.
      if (f.a > prev.a && !(prev.mix > 0.98)) {
        bad = `${id}@${t.toFixed(2)} deal advanced from a mix of ${prev.mix.toFixed(4)}`;
        break;
      }
      prev = f;
    }
    if (bad) break;
    // Landing exactly on a turn instant starts the fade from zero, and the
    // instant before the fade ends is (almost) fully the incoming assignment.
    const at = turnAt(id, hold);
    if (!(at.a === 0 && at.b === 1 && at.mix === 0)) bad = `${id} first turn instant: ${JSON.stringify(at)}`;
    const late = turnAt(id, hold + TURN_FADE_SEC * 0.999);
    if (!(late.b === 1 && late.mix > 0.999)) bad = `${id} end of fade: ${JSON.stringify(late)}`;
    const after = turnAt(id, hold + TURN_FADE_SEC);
    if (!(after.a === 1 && after.b === 1 && after.mix === 0)) bad = `${id} after fade: ${JSON.stringify(after)}`;
  }
  ok('I4  the dissolve is consecutive, bounded, monotone and closes on the incoming deal',
    bad === null, bad ?? `${sawFade} fading samples across 4 modes`);
}

// ---------------------------------------------------------------------------
// I4b — A RUNAWAY CLOCK PARKS, it does not fade forever or ask `assignmentAt`
//       to compose an unbounded number of steps.
// ---------------------------------------------------------------------------
{
  const far = turnAt('march', turnHoldSec('march') * (MAX_TURN_INDEX + 5000));
  const parked = far.a === MAX_TURN_INDEX && far.b === MAX_TURN_INDEX && far.mix === 0;
  const t0 = Date.now();
  assignmentAt('ripple', MAX_TURN_INDEX, 64, 3);
  const ms = Date.now() - t0;
  ok('I4b a runaway clock parks at MAX_TURN_INDEX and stays cheap', parked && ms < 2000,
    `${parked ? 'parked' : 'NOT parked'}, worst-case compose ${ms}ms`);
}

// ---------------------------------------------------------------------------
// I5 — SCATTER'S STRIDE is in range and coprime to n, so one picture's orbit
//      reaches every fragment instead of circling a sub-cycle.
// ---------------------------------------------------------------------------
{
  let bad = null;
  const gcd = (a, b) => { while (b) { const t = a % b; a = b; b = t; } return a; };
  for (let n = 3; n <= 200; n++) {
    for (const seed of [0, 1, 5, 77, 1234567]) {
      const s = scatterStride(n, seed);
      if (!(s >= 1 && s <= n - 1)) bad = `n=${n} seed=${seed} stride ${s} out of range`;
      else if (gcd(s, n) !== 1) bad = `n=${n} seed=${seed} stride ${s} shares a factor`;
    }
  }
  // And it really does visit every fragment: n turns of scatter is the identity.
  for (const n of [7, 12, 24, 33]) {
    const a = assignmentAt('scatter', n, n, 12345);
    for (let j = 0; j < n; j++) if (a[j] !== j) bad = `scatter n=${n} did not close its orbit`;
  }
  ok('I5  scatter strides are in range, coprime to n, and close their orbit', bad === null, bad ?? 'n=3..200 x 5 seeds');
}

// ---------------------------------------------------------------------------
// I6 — RIPPLE HOLDS PART OF THE WALL. That is the whole point of the mode: if
//      it turned everything it would be `march` with a different hold.
// ---------------------------------------------------------------------------
{
  let bad = null;
  for (let n = 4; n <= 40; n++) {
    // One STEP of ripple must leave at least a third of the wall untouched.
    const a = assignmentAt('ripple', 1, n, 7);
    let held = 0;
    for (let j = 0; j < n; j++) if (a[j] === j) held++;
    if (held < Math.floor(n / 3)) bad = `n=${n}: only ${held}/${n} held`;
  }
  ok('I6  ripple holds at least a third of the wall on a turn', bad === null, bad ?? 'n=4..40');
}

// ---------------------------------------------------------------------------
// I7 — THE ROSTER AND THE CODE AGREE. The chips render `TURNS`; the code
//      indexes `TURN_IDS`. They are the same list or a chip mints a code the
//      decoder reads as a different mode.
// ---------------------------------------------------------------------------
{
  const sameOrder = TURNS.length === TURN_IDS.length && TURNS.every((t, i) => t.id === TURN_IDS[i]);
  const zeroIsNoop = TURN_IDS[0] === 'hold' && !isTurning('hold') && ACTIVE.every(isTurning);
  const fitsOneChar = TURN_IDS.length <= 36;
  const labelled = TURNS.every((t) => typeof t.label === 'string' && t.label.length > 0
    && typeof t.title === 'string' && t.title.length > 8);
  ok('I7  TURNS === TURN_IDS, index 0 is the no-op, roster fits one base-36 character',
    sameOrder && zeroIsNoop && fitsOneChar && labelled,
    `${TURN_IDS.length} ids`);
}

// ---------------------------------------------------------------------------
// I8 — EVERY TURN SURVIVES THE COMPOSITION CODE, including through the
//      checksummed shuffle group.
// ---------------------------------------------------------------------------
{
  const base = rollDice({ rnd: rngOf(20260812) });
  let bad = null;
  for (const turn of TURN_IDS) {
    const code = encodeRoll({ ...base, turn }, '');
    const back = decodeRoll(code, '');
    if (!back) bad = `${turn}: refused its own code`;
    else if (back.turn !== turn) bad = `${turn} -> ${back.turn}`;
    const withGroup = encodeRoll({ ...base, turn }, 'a3');
    const back2 = decodeRoll(withGroup, 'a3');
    if (!back2 || back2.turn !== turn) bad = `${turn}: lost through the shuffle group`;
    // The shuffle group is inside the checksum body: a different group is a
    // different code and must be refused, not silently opened.
    if (decodeRoll(withGroup, 'a4') !== null) bad = `${turn}: wrong shuffle group accepted`;
  }
  ok('I8  every turn round-trips through the code, bare and with a shuffle group', bad === null, bad ?? `${TURN_IDS.length} ids`);
}

// ---------------------------------------------------------------------------
// I8b — BACK COMPATIBILITY, the assertion this whole change stands on.
//       A pre-turn (20-character) group must still open, as `hold`, with every
//       other field unmoved. It cannot be built by truncation — lopping the
//       21st character leaves the wrong checksum — so it is rebuilt the way the
//       old encoder built it and re-checksummed.
// ---------------------------------------------------------------------------
{
  const checksum = (body) => {
    let h = 7;
    for (let i = 0; i < body.length; i++) h = (h * 31 + parseInt(body[i], 36) + 1) % 1679616;
    return (h % 36 ** 2).toString(36).padStart(2, '0');
  };
  let bad = null;
  let checked = 0;
  for (let i = 0; i < 40; i++) {
    const r = rollDice({ rnd: rngOf(1000 + i) });
    const code = encodeRoll({ ...r, turn: 'scatter' }, '');
    const [a, b, c] = code.toLowerCase().split('-');
    // DERIVED from the codec, never a literal — see the same note in
    // motion.invariants.mjs. THE PACE broke this line and its two siblings at
    // once, which is what a shared constant is for.
    if (b.length !== MINTED_GROUP_MAX) { bad = `minted group length ${b.length}, expected ${MINTED_GROUP_MAX}`; break; }
    const legacyBody = b.slice(0, 18);              // 15 fixed + owned + look + move
    const legacy = `${a}-${legacyBody}${checksum(a + legacyBody + c)}-${c}`.toUpperCase();
    const back = decodeRoll(legacy, '');
    checked++;
    if (!back) { bad = `pre-turn code refused: ${legacy}`; break; }
    if (back.turn !== 'hold') { bad = `pre-turn code opened as ${back.turn}`; break; }
    const now = decodeRoll(code, '');
    for (const k of ['layout', 'primitive', 'count', 'countOwned', 'entropy', 'aspect',
                     'gutter', 'zoom', 'bg', 'arrangement', 'focus', 'twist', 'look', 'move', 'seed']) {
      if (JSON.stringify(back[k]) !== JSON.stringify(now[k])) { bad = `field ${k} moved: ${back[k]} vs ${now[k]}`; break; }
    }
    if (bad) break;
  }
  ok('I8b a pre-turn 20-character code still opens, as `hold`, every other field unmoved',
    bad === null, bad ?? `${checked} rebuilt legacy codes`);
}

// ---------------------------------------------------------------------------
// I8c — THE DOORS STAY SHUT. An over-long group and an out-of-roster index are
//       refused rather than defaulted — the scar this codec already carries.
// ---------------------------------------------------------------------------
{
  let bad = null;
  const r = rollDice({ rnd: rngOf(31337) });
  const code = encodeRoll({ ...r, turn: 'march' }, '');
  const [a, b, c] = code.toLowerCase().split('-');
  if (decodeRoll(`${a}-${b}x-${c}`, '') !== null) bad = 'a 22-character group was accepted';
  if (decodeRoll(`${a}-${b}zz-${c}`, '') !== null) bad = 'a 23-character group was accepted';
  // A turn index this build has no entry for: forge it in place, keeping length.
  const hi = (TURN_IDS.length + 3).toString(36);
  const forged = `${a}-${b.slice(0, 18)}${hi}${b.slice(19)}-${c}`;
  if (decodeRoll(forged, '') !== null) bad = 'an out-of-roster turn index was accepted';
  // Truncating into the un-minted band must still be refused.
  for (const len of [16, 17, 19, 20]) {
    if (decodeRoll(`${a}-${b.slice(0, len)}-${c}`, '') !== null) bad = `a truncated ${len}-character group was accepted`;
  }
  ok('I8c over-long, forged and truncated groups are refused, never defaulted', bad === null, bad ?? '');
}

// ---------------------------------------------------------------------------
// I9 — THE DICE reaches every turn and holds most of the time.
// ---------------------------------------------------------------------------
{
  const seen = new Map();
  const N = 4000;
  const rnd = rngOf(777);
  for (let i = 0; i < N; i++) {
    const t = rollDice({ rnd }).turn ?? 'hold';
    seen.set(t, (seen.get(t) ?? 0) + 1);
  }
  const holdPct = ((seen.get('hold') ?? 0) / N) * 100;
  const reachedAll = TURN_IDS.every((t) => (seen.get(t) ?? 0) > 0);
  ok('I9  the dice reaches every turn, and holds 60-88% of rolls',
    reachedAll && holdPct > 60 && holdPct < 88,
    `hold ${holdPct.toFixed(1)}%, ${seen.size}/${TURN_IDS.length} ids reached`);
}

// ---------------------------------------------------------------------------
// I10 — THE CONSUMER CONTRACT, and the invariant that was NOT here when the
//       bug it describes shipped for ten minutes.
//
//       `turnAt` was correct; the loop that CONSUMES it was not. `refreshTurn`
//       ended a fade by testing `turnBoundB !== turnBoundA` — already false,
//       because the branch above advances `turnBoundA` to the same index in the
//       same call — so the cleanup never ran, `mix` stuck at 0.9944 for the
//       rest of the take and, under a move, a frozen copy covered the moving
//       picture. Three independent audit lenses found it; nothing in this file
//       could have.
//
//       So the state machine is replayed here, driven by the REAL `turnAt` at a
//       real frame rate. It is deliberately a MODEL of stage.ts's loop rather
//       than the loop itself (that one needs a canvas, and the e2e drives it) —
//       what it pins is the SHAPE the loop must have: a fade must be able to
//       END, and it cannot be ended by comparing two indices that the same call
//       has just made equal.
// ---------------------------------------------------------------------------
{
  let bad = null;
  for (const id of ACTIVE) {
    for (const fps of [24, 30, 60]) {
      // The shipped shape: a FLAG, not an index comparison.
      let boundA = 0; let boundB = -1; let fading = false;
      let mix = 0; let cleanups = 0; let fades = 0;
      const seconds = turnHoldSec(id) * 4 + 1;
      for (let f = 0; f <= Math.round(seconds * fps); f++) {
        const fr = turnAt(id, f / fps);
        if (fr.a !== boundA) boundA = fr.a;
        if (fr.mix > 0) {
          if (fr.b !== boundB) { boundB = fr.b; fades++; }
          fading = true;
          mix = fr.mix;
        } else if (fading) {
          mix = 0; boundB = -1; fading = false; cleanups++;
        }
      }
      if (mix !== 0) bad = `${id}@${fps}fps: mix left at ${mix.toFixed(4)} — the fade never ended`;
      else if (fading) bad = `${id}@${fps}fps: still marked fading at rest`;
      else if (cleanups !== fades) bad = `${id}@${fps}fps: ${fades} fades but ${cleanups} cleanups`;
      else if (fades < 3) bad = `${id}@${fps}fps: only ${fades} fades in ${seconds}s — the schedule stalled`;

      // AND THE BROKEN SHAPE MUST FAIL, or this arm proves nothing. Same replay,
      // ending the fade by the index comparison the first cut used.
      let bA = 0; let bB = 0; let m = 0; let c = 0;
      for (let f = 0; f <= Math.round(seconds * fps); f++) {
        const fr = turnAt(id, f / fps);
        if (fr.a !== bA) bA = fr.a;
        if (fr.mix > 0) { if (fr.b !== bB) bB = fr.b; m = fr.mix; }
        else if (bB !== bA) { m = 0; bB = bA; c++; }
      }
      if (m === 0 && c > 0) bad = `${id}@${fps}fps: the RED PROOF passed — the index-comparison shape is not actually broken`;
    }
  }
  ok('I10 a fade can END: the consumer replay returns mix to 0, and the shape that could not is proved broken',
    bad === null, bad ?? '4 modes x 3 frame rates, with a red proof on each');
}

console.log('\nTHE TURN — invariant sweep\n');
for (const line of results) console.log('  ' + line);
console.log(`\n${results.length - failures}/${results.length} invariants hold\n`);
process.exit(failures ? 1 : 0);
