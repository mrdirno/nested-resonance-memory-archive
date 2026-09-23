/**
 * Invariant sweep for THE GRAB — press any fragment, drag its picture, let go.
 *
 * Run: node tests/unit/grab.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so
 * every claim below is about the shipped `grab.stepGrab` — never a copy of it.
 *
 * THE CLAIMS THAT MATTER.
 *   G1 A TAP STAYS A TAP. A press whose every move stays inside its kind's slop
 *      never moves the picture and never eats the click that follows — the pin,
 *      the arm and the trade keep their shipped meaning.
 *   G2 THE PICTURE FOLLOWS THE FINGER FROM THE PRESS POINT. Once past the slop,
 *      every move hands back EXACTLY the total displacement since the press, so
 *      the spot under the finger stays under it.
 *   G3 ONE FINGER OWNS THE GESTURE. Events from any other pointer change nothing,
 *      by reference.
 *   G4 THE HOLD IS ANNOUNCED AT MOST ONCE, and never before `holdMs`.
 *   G5 THE CLICK AFTER A DRAG IS EATEN BY TIME. Only a drag that ENDED IN AN UP
 *      can own a click, and only inside the window; a cancel owns none; a
 *      touch drag (which ends in no click) cannot bank a swallow that lands on
 *      the next genuine tap — the bug measured on the build before this module.
 *   G6 A SCROLLING SURFACE'S GRAMMAR STILL WORKS. Under rules where touch needs
 *      the hold, a touch that moves before it is REFUSED for good, one that is
 *      held (by the timer OR by the clock, when the timer is late) drags.
 *   G7 DETERMINISM AND HYGIENE. Same script, same answer; a finished gesture is
 *      null; non-finite input never produces a non-finite drag.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');

const load = async (rel, tag) => {
  const out = join(mkdtempSync(join(tmpdir(), `${tag}-`)), `${tag}.mjs`);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: out, bundle: true, format: 'esm', platform: 'neutral', logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const { GRAB, stepGrab, pressGrab, pointerKind, clickBelongsToDrag } = await load('src/lib/grab.ts', 'grab');

let failures = 0;
let checks = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  checks++;
  if (!pass) {
    failures++;
    if (results.length < 40) results.push(`FAIL  ${name}${detail ? `  — ${detail}` : ''}`);
  }
};

// ------------------------------------------------------------- generators --
const mulberry32 = (a) => () => {
  a |= 0; a = (a + 0x6D2B79F5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const KINDS = ['mouse', 'pen', 'touch'];
const NEEDS_HOLD_TOUCH = { ...GRAB, needsHold: { mouse: false, pen: false, touch: true } };
const RULESETS = [['default', GRAB], ['touch-needs-hold', NEEDS_HOLD_TOUCH]];

/**
 * A GESTURE SCRIPT: one press, then a stream of moves / hold ticks / foreign
 * pointer events, then an up or a cancel. The shape is drawn from the seed:
 * a tap (tremble inside the slop), a drag from the start, a hold-then-drag,
 * a hold-then-release, or a late-timer hold.
 */
function script(seed, kind, rules) {
  const r = mulberry32(seed);
  const pid = 1 + Math.floor(r() * 7);
  const other = pid + 1 + Math.floor(r() * 5);
  const x0 = 20 + r() * 360, y0 = 20 + r() * 700, t0 = 1000 + r() * 50000;
  const shape = ['tap', 'drag', 'holdDrag', 'holdRelease', 'lateTimer', 'foreign'][Math.floor(r() * 6)];
  const slop = rules.slop[kind];
  const ev = [];
  let t = t0;
  const tremble = () => {
    const a = r() * Math.PI * 2, d = r() * (slop - 0.01);
    return [x0 + Math.cos(a) * d, y0 + Math.sin(a) * d];
  };
  const n = 2 + Math.floor(r() * 10);
  if (shape === 'tap' || shape === 'holdRelease' || shape === 'foreign') {
    for (let i = 0; i < n; i++) {
      t += 5 + r() * (shape === 'holdRelease' ? 120 : 20);
      const [x, y] = tremble();
      ev.push({ type: 'move', pid, x, y, t });
      if (shape === 'foreign') ev.push({ type: 'move', pid: other, x: r() * 400, y: r() * 800, t });
    }
    if (shape === 'holdRelease') { t = Math.max(t, t0 + rules.holdMs + r() * 400); ev.push({ type: 'hold', pid, t }); }
  } else {
    if (shape === 'holdDrag') {
      const [x, y] = tremble();
      t += 10; ev.push({ type: 'move', pid, x, y, t });
      t = t0 + rules.holdMs + r() * 300; ev.push({ type: 'hold', pid, t });
    }
    if (shape === 'lateTimer') {
      // the timer never fires before the finger moves: the clock must vouch for the hold
      const [x, y] = tremble();
      t = t0 + rules.holdMs + 1 + r() * 300; ev.push({ type: 'move', pid, x, y, t });
    }
    const dirA = r() * Math.PI * 2, len = slop + 1 + r() * 400;
    for (let i = 1; i <= n; i++) {
      t += 8 + r() * 16;
      const f = i / n;
      ev.push({ type: 'move', pid, x: x0 + Math.cos(dirA) * len * f + (r() - 0.5) * 3, y: y0 + Math.sin(dirA) * len * f + (r() - 0.5) * 3, t });
      if (r() < 0.2) ev.push({ type: 'hold', pid, t: t + r() * 5 });        // a stray timer
      if (r() < 0.2) ev.push({ type: 'up', pid: other, t });                  // another finger lifting
    }
  }
  t += 5 + r() * 30;
  ev.push({ type: r() < 0.8 ? 'up' : 'cancel', pid, t });
  return { pid, other, kind, x0, y0, t0, shape, events: ev };
}

function run(sc, rules) {
  let g = pressGrab(sc.pid, sc.kind, sc.x0, sc.y0, sc.t0);
  const out = [];
  for (const e of sc.events) {
    const before = g;
    const s = stepGrab(g, e, rules);
    out.push({ e, before, s });
    g = s.grab;
  }
  return out;
}

// ----------------------------------------------------------------- the sweep --
const SEEDS = 4000;
let shapes = {};
for (const [rname, rules] of RULESETS) {
  for (const kind of KINDS) {
    for (let seed = 1; seed <= SEEDS; seed++) {
      const sc = script(seed * 7919 + kind.length * 31 + rname.length, kind, rules);
      shapes[sc.shape] = (shapes[sc.shape] || 0) + 1;
      const trace = run(sc, rules);
      const tag = `[${rname} ${kind} seed ${seed} ${sc.shape}]`;
      const slop = rules.slop[kind];

      // everything the owning pointer did
      const own = trace.filter(({ e }) => e.pid === sc.pid);
      const moves = own.filter(({ e }) => e.type === 'move');
      const leftSlop = moves.some(({ e }) => Math.hypot(e.x - sc.x0, e.y - sc.y0) >= slop);
      const last = trace[trace.length - 1];

      // G1 — a tap stays a tap
      if (!leftSlop) {
        ok(`G1 no drag inside the slop ${tag}`, trace.every(({ s }) => s.drag === null));
        ok(`G1 a tap eats no click ${tag}`, last.s.endedDrag === false);
      }

      // G3 — one finger owns the gesture (identity, and no signal)
      for (const { e, before, s } of trace) {
        if (e.pid !== sc.pid && before) {
          ok(`G3 foreign pointer changes nothing ${tag}`, Object.is(s.grab, before) && !s.drag && !s.heldNow && !s.endedDrag);
        }
      }

      // G4 — hold announced at most once, never early
      const helds = trace.filter(({ s }) => s.heldNow);
      ok(`G4 hold announced at most once ${tag}`, helds.length <= 1, `${helds.length}`);
      for (const { e } of helds) ok(`G4 hold never early ${tag}`, e.t - sc.t0 >= rules.holdMs, `${(e.t - sc.t0).toFixed(1)}ms`);

      // G2 — the picture follows the finger from the press point
      const drags = trace.filter(({ s }) => s.drag);
      for (const { e, s } of drags) {
        ok(`G2 drag is the total since the press ${tag}`, s.drag.dx === e.x - sc.x0 && s.drag.dy === e.y - sc.y0);
        ok(`G2 drag is finite ${tag}`, Number.isFinite(s.drag.dx) && Number.isFinite(s.drag.dy));
      }
      if (drags.length) {
        const first = drags[0];
        ok(`G2 the first drag is past the slop ${tag}`, Math.hypot(first.s.drag.dx, first.s.drag.dy) >= slop);
        // once dragging, every later own move is a drag
        const idx = trace.indexOf(first);
        const later = trace.slice(idx).filter(({ e }) => e.pid === sc.pid && e.type === 'move');
        ok(`G2 dragging never stops mid-gesture ${tag}`, later.every(({ s }) => s.drag !== null));
      }

      // G5 — only a drag that ends in an UP owns a click
      const ended = last.s;
      ok(`G5 the gesture is over after up/cancel ${tag}`, ended.grab === null);
      if (last.e.type === 'cancel') ok(`G5 a cancel owns no click ${tag}`, ended.endedDrag === false);
      if (last.e.type === 'up') ok(`G5 an up after a drag owns its click ${tag}`, ended.endedDrag === (drags.length > 0));

      // G6 — under the default rules nothing is ever refused and a slop exit drags;
      // under touch-needs-hold a touch that left the slop before holdMs never drags
      const firstOut = moves.find(({ e }) => Math.hypot(e.x - sc.x0, e.y - sc.y0) >= slop);
      if (firstOut) {
        const heldBefore = trace.slice(0, trace.indexOf(firstOut)).some(({ s }) => s.grab && s.grab.phase === 'held');
        const clockHeld = firstOut.e.t - sc.t0 >= rules.holdMs;
        const mustDrag = !rules.needsHold[kind] || heldBefore || clockHeld;
        ok(`G6 slop exit ${mustDrag ? 'drags' : 'is refused'} ${tag}`, mustDrag ? firstOut.s.drag !== null : firstOut.s.drag === null && firstOut.s.grab.phase === 'refused');
        if (!mustDrag) ok(`G6 refused stays refused ${tag}`, drags.length === 0);
      }
      if (!rules.needsHold[kind]) ok(`G6 default rules never refuse ${tag}`, trace.every(({ s }) => !s.grab || s.grab.phase !== 'refused'));

      // G7 — determinism
      const again = run(sc, rules);
      ok(`G7 same script same answer ${tag}`, JSON.stringify(again.map((x) => x.s)) === JSON.stringify(trace.map((x) => x.s)));
    }
  }
}

// ------------------------------------------------------ the named gestures --
// THE WISHER'S OWN GESTURE, verbatim: touch, hold, drag, release.
{
  let g = pressGrab(3, 'touch', 200, 150, 10_000);
  let s = stepGrab(g, { type: 'hold', pid: 3, t: 10_000 + GRAB.holdMs }); g = s.grab;
  ok('W1 the hold is announced', s.heldNow && g.phase === 'held');
  for (let i = 1; i <= 16; i++) { s = stepGrab(g, { type: 'move', pid: 3, x: 200, y: 150 + 10 * i, t: 10_600 + 16 * i }); g = s.grab; }
  ok('W1 the picture is dragged 160 px down', s.drag && s.drag.dx === 0 && s.drag.dy === 160);
  s = stepGrab(g, { type: 'up', pid: 3, t: 10_900 });
  ok('W1 the release ends a drag', s.grab === null && s.endedDrag === true);
}
// PRESS AND GO: a finger that moves at once is not made to wait.
{
  let g = pressGrab(1, 'touch', 50, 50, 0);
  const s = stepGrab(g, { type: 'move', pid: 1, x: 50, y: 50 + GRAB.slop.touch, t: 40 });
  ok('W2 press-and-go drags immediately under the default rules', s.drag && s.drag.dy === GRAB.slop.touch && !s.heldNow);
}
// A SLOW TAP IS STILL A TAP: held past the threshold, released without moving.
{
  let g = pressGrab(1, 'touch', 50, 50, 0);
  let s = stepGrab(g, { type: 'hold', pid: 1, t: GRAB.holdMs + 1 }); g = s.grab;
  s = stepGrab(g, { type: 'up', pid: 1, t: GRAB.holdMs + 300 });
  ok('W3 a slow tap lets its click through (pin / arm / trade)', s.endedDrag === false);
}
// A TREMBLING TAP ON GLASS: 8 px of wander is a tap for a finger (the panel's
// acceptance line: "a tap with 8 px of jitter pins and stores no frame") and a
// drag for a mouse.
{
  const t = pressGrab(1, 'touch', 0, 0, 0);
  const m = pressGrab(1, 'mouse', 0, 0, 0);
  ok('W4 8 px of jitter is a tap for touch', stepGrab(t, { type: 'move', pid: 1, x: 8, y: 0, t: 30 }).drag === null);
  ok('W4 8 px is a drag for a mouse', stepGrab(m, { type: 'move', pid: 1, x: 8, y: 0, t: 30 }).drag !== null);
  ok('W4 a finger gets 10 px, a mouse the shipped 5', GRAB.slop.touch === 10 && GRAB.slop.mouse === 5);
}
// A STALE TIMER after the gesture moved on, and one before its time.
{
  let g = pressGrab(1, 'mouse', 0, 0, 0);
  const early = stepGrab(g, { type: 'hold', pid: 1, t: GRAB.holdMs - 1 });
  ok('W5 an early timer announces nothing', !early.heldNow && early.grab.phase === 'pressed');
  g = stepGrab(g, { type: 'move', pid: 1, x: 40, y: 0, t: 20 }).grab;
  const stale = stepGrab(g, { type: 'hold', pid: 1, t: GRAB.holdMs + 5 });
  ok('W5 a timer after the drag began announces nothing', !stale.heldNow && stale.grab.phase === 'dragging');
  ok('W5 stepGrab(null, ...) is idle', stepGrab(null, { type: 'up', pid: 1, t: 1 }).grab === null);
}
// NON-FINITE INPUT
{
  const g = pressGrab(1, 'touch', NaN, Infinity, NaN);
  ok('W6 a non-finite press lands at a finite origin', Number.isFinite(g.ox) && Number.isFinite(g.oy) && Number.isFinite(g.t0));
  const s = stepGrab(pressGrab(1, 'touch', 0, 0, 0), { type: 'move', pid: 1, x: NaN, y: 400, t: 10 });
  ok('W6 a non-finite move is ignored', s.drag === null && s.grab.phase === 'pressed');
  const h = stepGrab(pressGrab(1, 'touch', 0, 0, 0), { type: 'hold', pid: 1, t: NaN });
  ok('W6 a non-finite clock announces nothing', !h.heldNow);
}
// POINTER KINDS
ok('W7 kinds', pointerKind('touch') === 'touch' && pointerKind('pen') === 'pen' && pointerKind('mouse') === 'mouse' && pointerKind('') === 'mouse' && pointerKind(undefined) === 'mouse');
// THE CLICK WINDOW (G5 by the clock) — the touch bug, measured before this module
{
  const W = GRAB.clickWindowMs;
  ok('W8 no drag, no swallow', !clickBelongsToDrag(null, 100));
  ok('W8 the drag\'s own click (same instant) is eaten', clickBelongsToDrag(1000, 1000));
  ok('W8 the drag\'s own click (inside the window) is eaten', clickBelongsToDrag(1000, 1000 + W));
  ok('W8 the next genuine tap after a TOUCH drag is not eaten', !clickBelongsToDrag(1000, 1000 + W + 1));
  ok('W8 a click from before the drag ended is not its click', !clickBelongsToDrag(1000, 999));
  ok('W8 non-finite times swallow nothing', !clickBelongsToDrag(NaN, 5) && !clickBelongsToDrag(5, NaN));
}
// THE RULES THEMSELVES — the numbers the page ships with
ok('R1 touch slop is wider than the mouse slop', GRAB.slop.touch > GRAB.slop.mouse);
ok('R1 the hold lights before the platform long-press (500 ms)', GRAB.holdMs < 500);
ok('R1 no kind needs a hold on this surface', !GRAB.needsHold.mouse && !GRAB.needsHold.pen && !GRAB.needsHold.touch);
ok('R1 the click window is shorter than a human re-tap', GRAB.clickWindowMs <= 300);

console.log(`shapes swept: ${JSON.stringify(shapes)}`);
for (const line of results) console.log(line);
console.log(`\n${checks - failures}/${checks} checks pass${failures ? ` — ${failures} FAIL` : ''}`);
process.exit(failures ? 1 : 0);
