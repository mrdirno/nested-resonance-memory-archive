/**
 * Invariant sweep for UNDO — the roll you liked, brought back.
 *
 * Run: node tests/unit/compositionHistory.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so it
 * proves the shipped `commit` / `undo` / `redo` — not a re-implementation.
 *
 * THE INVARIANT THAT MATTERS, AND WHY IT IS AN ORACLE RATHER THAN A LIST
 *
 *   SCAR carried in COLLAGE_EVOLUTION.md, earned twice: "a test suite inherits
 *   its author's hypothesis." A list of hand-written cases about a history
 *   stack proves the cases I thought of, and the way undo/redo actually breaks
 *   is a sequence nobody wrote down — undo, undo, commit, redo, undo.
 *
 *   So the centre of this file is section 3: a REFERENCE MODEL of the obvious
 *   shape (one linear tape of states plus a cursor, six lines, obviously
 *   correct, far too memory-hungry to ship) is driven through thousands of
 *   RANDOM operation sequences alongside the real past/future implementation,
 *   and after every single operation both are asked the same question — what is
 *   on screen now, and which buttons are live. Any disagreement is a bug in the
 *   shipped module, and the sequences are seeded so a failure replays exactly.
 *
 *   The tape and the past/future pair are different data structures reaching
 *   the same answer, which is the only reason the comparison proves anything.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
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

const {
  emptyHistory, commit, undo, redo, canUndo, canRedo, sameSnapshot, HISTORY_LIMIT,
} = await load('src/lib/compositionHistory.ts', 'composition-history');

let checks = 0;
let failures = 0;
const check = (cond, msg) => {
  checks++;
  if (!cond) { failures++; console.error(`  ✗ ${msg}`); }
};

/** Deterministic RNG so a failure replays exactly. */
const rngOf = (seed) => {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
};

/** A snapshot is opaque to this module; give each one a distinct, checkable identity. */
const snapOf = (n, locks = [], recipe = undefined) => ({
  code: `C${n.toString(36).toUpperCase().padStart(4, '0')}`,
  locks,
  recipe,
});
const idOf = (s) => (s ? `${s.code}/${s.recipe ?? '-'}/${s.locks.map((l) => l.join(':')).sort().join(',')}` : 'NONE');

// =============================================================================
console.log('\n1. THE SHAPE — empty, bounds, and the doors that must stay shut');
// =============================================================================
{
  const h0 = emptyHistory();
  check(!canUndo(h0), 'a fresh history claims something to undo');
  check(!canRedo(h0), 'a fresh history claims something to redo');
  check(undo(h0, snapOf(1)) === null, 'undo on an empty past did not refuse');
  check(redo(h0, snapOf(1)) === null, 'redo on an empty future did not refuse');

  // The cap binds from the OLD end: the newest steps are the ones worth keeping.
  let h = emptyHistory();
  for (let i = 0; i < HISTORY_LIMIT * 3; i++) h = commit(h, snapOf(i));
  check(h.past.length === HISTORY_LIMIT, `past ran to ${h.past.length}, cap is ${HISTORY_LIMIT}`);
  check(h.past[h.past.length - 1].code === snapOf(HISTORY_LIMIT * 3 - 1).code,
    'the cap dropped the NEWEST step instead of the oldest');
  check(h.past[0].code === snapOf(HISTORY_LIMIT * 2).code,
    'the surviving window is not the last HISTORY_LIMIT steps');

  // Walk the whole capped stack back out: every step must be reachable, in order.
  let present = snapOf(HISTORY_LIMIT * 3);
  for (let i = 0; i < HISTORY_LIMIT; i++) {
    const r = undo(h, present);
    check(r !== null, `undo refused at depth ${i} with a full stack`);
    if (!r) break;
    const want = snapOf(HISTORY_LIMIT * 3 - 1 - i);
    check(r.restore.code === want.code, `undo depth ${i}: got ${r.restore.code}, want ${want.code}`);
    h = r.history; present = r.restore;
  }
  check(!canUndo(h), 'the stack did not empty after exactly HISTORY_LIMIT undos');
  check(h.future.length <= HISTORY_LIMIT, `future ran to ${h.future.length}, cap is ${HISTORY_LIMIT}`);
}

// =============================================================================
console.log('2. NOTHING IS MUTATED — a history handed in comes back untouched');
// =============================================================================
{
  // React state that is edited in place does not re-render, and a stack that is
  // edited in place makes the previous render's copy lie. Both are silent.
  let h = emptyHistory();
  for (let i = 0; i < 5; i++) h = commit(h, snapOf(i));
  const r1 = undo(h, snapOf(99));
  const frozen = { past: h.past.map(idOf).join('|'), future: h.future.map(idOf).join('|') };

  undo(h, snapOf(100));
  redo(r1.history, snapOf(101));
  commit(h, snapOf(102));

  check(h.past.map(idOf).join('|') === frozen.past, 'commit/undo/redo mutated the past it was handed');
  check(h.future.map(idOf).join('|') === frozen.future, 'commit/undo/redo mutated the future it was handed');
  check(r1.history !== h, 'undo returned the same object it was handed');
}

// =============================================================================
console.log('3. THE ORACLE — a tape with a cursor, driven through random sequences');
// =============================================================================
{
  // The reference model. Obviously correct, obviously not shippable: it keeps
  // every state forever, including the present, which is exactly what the real
  // module refuses to do (see its header).
  const makeTape = (s0) => ({ tape: [s0], i: 0 });
  const tapeCommit = (m, next) => { m.tape = m.tape.slice(0, m.i + 1).concat([next]); m.i = m.tape.length - 1; };
  const tapeUndo = (m) => { if (m.i > 0) { m.i--; return true; } return false; };
  const tapeRedo = (m) => { if (m.i < m.tape.length - 1) { m.i++; return true; } return false; };
  const tapeNow = (m) => m.tape[m.i];

  const SEQUENCES = 4000;
  const OPS_PER = 40;
  // No cap in this section: the oracle keeps everything, so a binding cap would
  // be a DIFFERENCE by design rather than a bug. The cap is proven in section 1.
  const NO_CAP = 1e9;
  let opsRun = 0;
  let sawCommit = 0; let sawUndo = 0; let sawRedo = 0; let sawRefusedUndo = 0; let sawRefusedRedo = 0;

  for (let seq = 0; seq < SEQUENCES; seq++) {
    const rnd = rngOf(seq * 2654435761 + 11);
    let n = 0;
    const s0 = snapOf(n++);
    let h = emptyHistory();
    let present = s0;
    const model = makeTape(s0);

    for (let step = 0; step < OPS_PER; step++) {
      const roll = rnd();
      opsRun++;
      if (roll < 0.45) {
        // A destructive composition event: snapshot what is on screen, then the
        // app's fifteen setState calls land and the present becomes something new.
        const next = snapOf(n++, rnd() < 0.3 ? [[Math.floor(rnd() * 6), `img-${Math.floor(rnd() * 4)}`]] : [],
          rnd() < 0.3 ? `recipe-${Math.floor(rnd() * 3)}` : undefined);
        h = commit(h, present, NO_CAP);
        present = next;
        tapeCommit(model, next);
        sawCommit++;
      } else if (roll < 0.78) {
        const r = undo(h, present, NO_CAP);
        const modelMoved = tapeUndo(model);
        check((r !== null) === modelMoved,
          `seq ${seq} step ${step}: undo ${r ? 'moved' : 'refused'} but the tape ${modelMoved ? 'moved' : 'refused'}`);
        if (r) { h = r.history; present = r.restore; sawUndo++; } else sawRefusedUndo++;
      } else {
        const r = redo(h, present, NO_CAP);
        const modelMoved = tapeRedo(model);
        check((r !== null) === modelMoved,
          `seq ${seq} step ${step}: redo ${r ? 'moved' : 'refused'} but the tape ${modelMoved ? 'moved' : 'refused'}`);
        if (r) { h = r.history; present = r.restore; sawRedo++; } else sawRefusedRedo++;
      }

      // After EVERY operation, both structures answer the same three questions.
      check(idOf(present) === idOf(tapeNow(model)),
        `seq ${seq} step ${step}: on screen ${idOf(present)}, tape says ${idOf(tapeNow(model))}`);
      check(canUndo(h) === (model.i > 0),
        `seq ${seq} step ${step}: canUndo=${canUndo(h)}, tape depth behind=${model.i}`);
      check(canRedo(h) === (model.i < model.tape.length - 1),
        `seq ${seq} step ${step}: canRedo=${canRedo(h)}, tape depth ahead=${model.tape.length - 1 - model.i}`);
    }
  }
  console.log(`   ${opsRun.toLocaleString()} operations over ${SEQUENCES.toLocaleString()} sequences ` +
    `(commit ${sawCommit.toLocaleString()} · undo ${sawUndo.toLocaleString()} · redo ${sawRedo.toLocaleString()})`);
  // A sweep that never reached the interesting states proves nothing about them.
  check(sawRefusedUndo > 100, `only ${sawRefusedUndo} undos hit the back wall — the sweep never tested the empty past`);
  check(sawRefusedRedo > 100, `only ${sawRefusedRedo} redos hit the front wall — the sweep never tested the empty future`);
  check(sawRedo > 1000, `only ${sawRedo} redos actually moved — the sweep barely exercised redo`);
}

// =============================================================================
console.log('4. THE BRANCH RULE — a new roll after undoing abandons what you left');
// =============================================================================
{
  let h = emptyHistory();
  let present = snapOf(0);
  for (let i = 1; i <= 3; i++) { h = commit(h, present); present = snapOf(i); }   // 0,1,2 behind; 3 on screen
  for (let i = 0; i < 2; i++) { const r = undo(h, present); h = r.history; present = r.restore; }
  check(canRedo(h), 'two undos left nothing to redo');
  check(present.code === snapOf(1).code, `undo x2 landed on ${present.code}, want ${snapOf(1).code}`);

  h = commit(h, present); present = snapOf(9);                                     // a NEW roll from here
  check(!canRedo(h), 'a new roll after undoing left the abandoned branch redoable');
  const back = undo(h, present);
  check(back.restore.code === snapOf(1).code,
    `undo after the new roll landed on ${back.restore.code}, want ${snapOf(1).code}`);
}

// =============================================================================
console.log('5. THE DOUBLE PRESS — the same picture twice is one step, not two');
// =============================================================================
{
  // Two dice presses inside one React render push the SAME on-screen state
  // twice. Without the refusal the first undo would restore what is already
  // there, which reads as a dead button rather than a no-op.
  const s = snapOf(7, [[2, 'img-a']], 'Broadside');
  const dup = snapOf(7, [[2, 'img-a']], 'Broadside');
  check(sameSnapshot(s, dup), 'two identical snapshots did not compare equal');
  check(sameSnapshot(snapOf(7, [[1, 'a'], [2, 'b']]), snapOf(7, [[2, 'b'], [1, 'a']])),
    'equal lock sets in a different order compared unequal — Map iteration order is not identity');
  check(!sameSnapshot(snapOf(7, [[2, 'img-a']]), snapOf(7, [[2, 'img-b']])),
    'different locks on the same code compared equal');
  check(!sameSnapshot(snapOf(7, [], 'Broadside'), snapOf(7, [], 'Stack')),
    'different recipes on the same code compared equal');

  let h = commit(commit(emptyHistory(), s), dup);
  check(h.past.length === 1, `the duplicate press pushed ${h.past.length} steps, want 1`);

  // …but it is still a branch: a repeat press abandons the future like any commit.
  let h2 = emptyHistory();
  h2 = commit(h2, snapOf(1));
  const u = undo(h2, snapOf(2));
  check(canRedo(u.history), 'setup: the undo left nothing to redo');
  const after = commit(u.history, u.restore);   // commit the SAME snapshot that is now on screen
  check(!canRedo(after), 'a duplicate commit kept a redo alive on an abandoned branch');
}

// =============================================================================
console.log('6. THE ROUND TRIP — undo then redo puts back exactly what was there');
// =============================================================================
{
  const rnd = rngOf(20260810);
  let round = 0;
  for (let t = 0; t < 500; t++) {
    let h = emptyHistory();
    let present = snapOf(0);
    const depth = 1 + Math.floor(rnd() * 8);
    for (let i = 1; i <= depth; i++) { h = commit(h, present); present = snapOf(i); }
    const before = idOf(present);
    const beforePast = h.past.map(idOf).join('|');

    const u = undo(h, present);
    const r = redo(u.history, u.restore);
    check(idOf(r.restore) === before, `round trip lost the present: ${idOf(r.restore)} != ${before}`);
    check(r.history.past.map(idOf).join('|') === beforePast, 'round trip did not restore the past');
    check(r.history.future.length === 0, 'round trip left something dangling in the future');
    round++;
  }
  console.log(`   ${round} undo→redo round trips exact`);
}

// =============================================================================
console.log(`\n${checks.toLocaleString()} checks / ${failures} failures`);
if (failures) { console.error(`FAILED — ${failures} assertion(s)`); process.exit(1); }
console.log('all green');
