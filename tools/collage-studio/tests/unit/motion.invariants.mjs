/**
 * Invariant sweep for THE MOVE — the per-fragment drift over time.
 *
 * Run: node tests/unit/motion.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * it proves the shipped `motion.sampleMove` / `motion.movePhase` /
 * `renderer.calculateSmartCrop` / `diceRoll.encodeRoll|decodeRoll` — not a
 * re-implementation of them.
 *
 * THE INVARIANT THAT MATTERS — IDENTITY AT REST:
 *
 *   Four surfaces produce pixels in this app and only ONE of them has a clock.
 *   The still preview, the full-resolution raster export and the SVG each draw
 *   a single frame and pass no time at all. If a move could perturb them by so
 *   much as a float, this feature would have silently changed every export in
 *   the app to buy motion in one of them.
 *
 *   So the claim is not "close enough at t=0". It is that `calculateSmartCrop`
 *   returns geometry that is `Object.is`-identical, field by field, with a move
 *   attached and without one — over every roster entry, every phase, every
 *   zoom, every twist and a wide spread of box and image shapes. Everything
 *   else here is secondary to that.
 *
 * THE SECOND ONE — A PAN NEVER CLAMPS:
 *
 *   `calculateSmartCrop` clamps the source rect inside the image. A pan larger
 *   than the crop's slack does not pan, it CLAMPS — and a clamped fragment sits
 *   still while its neighbours move, which reads as a bug in the one place the
 *   eye is already looking. `sampleMove` derives its reach FROM that slack, so
 *   the failure is meant to be unrepresentable rather than merely absent. This
 *   sweep re-derives the unclamped rect independently and requires the shipped
 *   one to equal it, then measures how far a naive fixed pan would have missed.
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
  MOVE_IDS, MOVES, MOVE_CYCLE_SEC, MAX_MOVE_ZOOM,
  NO_MOVE, sampleMove, movePhase, isMoving, withMove,
} = await load('src/lib/motion.ts', 'motion');

const { calculateSmartCrop } = await load('src/lib/renderer.ts', 'renderer');
const { encodeRoll, decodeRoll, rollDice, snapRoll } = await load('src/lib/diceRoll.ts', 'dice');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};

const ACTIVE = MOVE_IDS.filter((m) => m !== 'still');

// -----------------------------------------------------------------------------
// The sweep space. Deliberately awkward: extreme aspect ratios in both
// directions, a portrait image in a landscape cell and back, zooms either side
// of 1, and twists that grow the destination.
// -----------------------------------------------------------------------------
const BOXES = [
  { x: 0, y: 0, w: 400, h: 300 },
  { x: 137, y: 41, w: 91, h: 620 },
  { x: 12, y: 900, w: 1180, h: 60 },
  { x: 600, y: 300, w: 300, h: 300 },
  { x: 3, y: 7, w: 11, h: 9 },
];
const IMAGES = [
  { width: 4032, height: 3024 },
  { width: 1080, height: 1920 },
  { width: 800, height: 800 },
  { width: 6000, height: 1000 },
  { width: 240, height: 3200 },
];
const ZOOMS = [1, 1.5, 2.25, 0.5, 4];
const TWISTS = [0, 0.05, -0.21, 0.38];
const PHASES = [0, 0.07, 0.25, 0.4999, 0.5, 0.5001, 0.75, 0.9999, 1];
const CELLS = [
  null, {},
  { cx: 0, cy: 0 }, { cx: 0.5, cy: 0.5 }, { cx: 1, cy: 1 },
  { cx: 0.13, cy: 0.87 }, { cx: 0.62, cy: 0.31 }, { cx: 0.999999, cy: 0.000001 },
];

const anaFor = (twist, moveSpec) => ({
  face: null, energy: null, color: null,
  ...(twist ? { twist } : {}),
  ...(moveSpec ? { move: moveSpec } : {}),
});

// =============================================================================
// I1  IDENTITY AT REST — the whole safety argument for shipping this.
// =============================================================================
{
  let n = 0;
  let bad = null;
  for (const id of MOVE_IDS) {
    for (const ph of PHASES) {
      for (const box of BOXES) {
        for (const img of IMAGES) {
          for (const zoom of ZOOMS) {
            for (const twist of TWISTS) {
              const withM = calculateSmartCrop(
                box, { ...img, analysis: anaFor(twist, { id, ph }) }, zoom, 0,
              );
              const without = calculateSmartCrop(
                box, { ...img, analysis: anaFor(twist, null) }, zoom,
              );
              n++;
              for (const k of ['sx', 'sy', 'sw', 'sh', 'dx', 'dy', 'dw', 'dh', 'twist', 'tcx', 'tcy']) {
                if (!Object.is(withM[k], without[k])) {
                  bad ??= `${id}@ph=${ph} ${k}: ${withM[k]} vs ${without[k]}`;
                }
              }
            }
          }
        }
      }
    }
  }
  ok('I1  a move at t=0 is Object.is-identical to no move at all', !bad, bad ?? `${n} setups`);
}

{
  // The mechanism behind I1, asserted directly: REST IS A SHARED OBJECT, so the
  // caller's guard is reference identity and not arithmetic that happens to be
  // a no-op. A fresh {zoom:1,ax:0,ay:0} would pass I1 today and stop passing it
  // the moment anyone multiplies by it in a different order.
  let bad = null;
  for (const id of MOVE_IDS) {
    for (const ph of PHASES) {
      if (sampleMove({ id, ph }, 0) !== NO_MOVE) bad ??= `${id}@${ph}`;
      // Every cycle boundary is rest too, exactly, not approximately.
      for (const k of [1, 2, 7]) {
        if (sampleMove({ id, ph }, k * MOVE_CYCLE_SEC) !== NO_MOVE) bad ??= `${id}@${ph} t=${k}cyc`;
      }
    }
  }
  ok('I1b rest is the SHARED NO_MOVE object, at t=0 and at every cycle boundary', !bad, bad ?? '');
}

// =============================================================================
// I2  BOUNDED — nothing escapes the roster's own ceiling.
// =============================================================================
{
  let bad = null;
  let peakZoom = 1;
  let peakPan = 0;
  for (const id of ACTIVE) {
    for (const ph of PHASES) {
      for (let i = 0; i <= 400; i++) {
        const t = (i / 400) * 3 * MOVE_CYCLE_SEC;
        const m = sampleMove({ id, ph }, t);
        if (!Number.isFinite(m.zoom) || !Number.isFinite(m.ax) || !Number.isFinite(m.ay)) bad ??= `nonfinite ${id}`;
        if (m.zoom < 1 || m.zoom > MAX_MOVE_ZOOM) bad ??= `zoom ${m.zoom} ${id}`;
        if (Math.abs(m.ax) > 0.5 || Math.abs(m.ay) > 0.5) bad ??= `pan ${m.ax},${m.ay} ${id}`;
        peakZoom = Math.max(peakZoom, m.zoom);
        peakPan = Math.max(peakPan, Math.abs(m.ax), Math.abs(m.ay));
      }
    }
  }
  ok('I2  zoom in [1, MAX] and pan bounded, always finite', !bad,
    bad ?? `peak zoom ${peakZoom.toFixed(4)} <= ${MAX_MOVE_ZOOM}, peak pan ${peakPan.toFixed(4)}`);
}

// =============================================================================
// I3  PAN IMPLIES ROOM — the failure is unrepresentable, not merely absent.
// =============================================================================
{
  let bad = null;
  let worst = 0;
  for (const id of ACTIVE) {
    for (const ph of PHASES) {
      for (let i = 1; i < 400; i++) {
        const t = (i / 400) * MOVE_CYCLE_SEC;
        const m = sampleMove({ id, ph }, t);
        const room = (1 - 1 / m.zoom) / 2;
        if ((Math.abs(m.ax) > 0 || Math.abs(m.ay) > 0) && !(m.zoom > 1)) bad ??= `pan without zoom ${id}`;
        const used = Math.hypot(m.ax, m.ay);
        if (used > room + 1e-12) bad ??= `${id}@${ph} t=${t.toFixed(2)}: |pan| ${used} > room ${room}`;
        if (room > 0) worst = Math.max(worst, used / room);
      }
    }
  }
  ok('I3  every pan fits the slack its own zoom creates', !bad,
    bad ?? `worst use of available room: ${(worst * 100).toFixed(1)}%`);
}

// =============================================================================
// I4  AND SO THE CROP NEVER CLAMPS — the same claim, at the real call site.
// =============================================================================
{
  let bad = null;
  let clamped = 0;
  let n = 0;
  for (const id of ACTIVE) {
    for (const cell of CELLS) {
      const ph = movePhase(id, cell);
      for (const box of BOXES) {
        for (const img of IMAGES) {
          for (const zoom of [1, 1.5, 2.25]) {
            for (let i = 1; i < 24; i++) {
              const t = (i / 24) * MOVE_CYCLE_SEC;
              const c = calculateSmartCrop(box, { ...img, analysis: anaFor(0, { id, ph }) }, zoom, t);
              const m = sampleMove({ id, ph }, t);
              // Re-derive the UNCLAMPED source origin independently.
              const wantX = (0.5 + m.ax) * img.width - c.sw / 2;
              const wantY = (0.5 + m.ay) * img.height - c.sh / 2;
              n++;
              if (Math.abs(c.sx - wantX) > 1e-9 || Math.abs(c.sy - wantY) > 1e-9) {
                clamped++;
                bad ??= `${id} box${box.w}x${box.h} img${img.width}x${img.height} z${zoom} t${t.toFixed(1)}: `
                  + `sx ${c.sx} vs ${wantX}, sy ${c.sy} vs ${wantY}`;
              }
              if (c.sx < -1e-9 || c.sy < -1e-9
                || c.sx + c.sw > img.width + 1e-9 || c.sy + c.sh > img.height + 1e-9) {
                bad ??= `${id}: crop escaped the image`;
              }
            }
          }
        }
      }
    }
  }
  ok('I4  a centred anchor never hits the clamp, and never leaves the image', !bad,
    bad ?? `${n} crops, ${clamped} clamped`);
}

{
  // THE RED PROOF, measured rather than asserted: what a naive fixed pan costs.
  // Same call sites, same times, with the reach replaced by a flat 0.25 of the
  // source instead of a fraction of the room the zoom leaves.
  let hits = 0;
  let n = 0;
  let worstPx = 0;
  for (const id of ACTIVE) {
    for (const cell of CELLS) {
      const ph = movePhase(id, cell);
      for (const box of BOXES) {
        for (const img of IMAGES) {
          for (let i = 1; i < 24; i++) {
            const t = (i / 24) * MOVE_CYCLE_SEC;
            const m = sampleMove({ id, ph }, t);
            if (m === NO_MOVE) continue;
            const c = calculateSmartCrop(box, { ...img, analysis: anaFor(0, { id, ph }) }, 1, t);
            const dirX = m.ax === 0 && m.ay === 0 ? 1 : m.ax / (Math.hypot(m.ax, m.ay) || 1);
            const naiveX = (0.5 + 0.25 * dirX) * img.width - c.sw / 2;
            const lo = 0;
            const hi = img.width - c.sw;
            n++;
            if (naiveX < lo - 1e-9 || naiveX > hi + 1e-9) {
              hits++;
              worstPx = Math.max(worstPx, Math.max(lo - naiveX, naiveX - hi));
            }
          }
        }
      }
    }
  }
  ok('I4b (measured) a naive fixed 0.25 pan WOULD clamp — the defect this design removes',
    hits > 0, `${hits}/${n} setups clamp, worst overshoot ${worstPx.toFixed(0)} source px`);
}

// =============================================================================
// I5  PERIODIC AND CONTINUOUS — a loop with no visible snap.
// =============================================================================
{
  let bad = null;
  let worstPeriod = 0;
  for (const id of ACTIVE) {
    for (const ph of PHASES) {
      for (let i = 0; i <= 60; i++) {
        const t = (i / 60) * MOVE_CYCLE_SEC;
        const a = sampleMove({ id, ph }, t);
        const b = sampleMove({ id, ph }, t + 3 * MOVE_CYCLE_SEC);
        const d = Math.max(Math.abs(a.zoom - b.zoom), Math.abs(a.ax - b.ax), Math.abs(a.ay - b.ay));
        worstPeriod = Math.max(worstPeriod, d);
        if (d > 1e-9) bad ??= `${id}@${ph} t=${t}: ${d}`;
      }
    }
  }
  ok('I5  the move is periodic on MOVE_CYCLE_SEC', !bad,
    bad ?? `max drift over 3 cycles ${worstPeriod.toExponential(1)}`);
}

{
  // CONTINUITY, including across the wrap. A 60 Hz step may not move the zoom
  // by more than the envelope's own maximum slope allows.
  const dt = 1 / 60;
  const slopeCap = (Math.PI * 2 * 2) / MOVE_CYCLE_SEC * (MAX_MOVE_ZOOM - 1) / 2 * dt * 1.6;
  let bad = null;
  let worst = 0;
  for (const id of ACTIVE) {
    for (const ph of PHASES) {
      let prev = sampleMove({ id, ph }, 0);
      for (let t = dt; t <= 2 * MOVE_CYCLE_SEC + dt; t += dt) {
        const cur = sampleMove({ id, ph }, t);
        const dz = Math.abs(cur.zoom - prev.zoom);
        worst = Math.max(worst, dz);
        if (dz > slopeCap) bad ??= `${id}@${ph} t=${t.toFixed(3)}: dzoom ${dz} > ${slopeCap}`;
        prev = cur;
      }
    }
  }
  ok('I5b no jump at the turnaround or the loop point', !bad,
    bad ?? `max |dzoom| per frame ${worst.toExponential(2)} <= ${slopeCap.toExponential(2)}`);
}

// =============================================================================
// I6  THE PHASE IS A PROPERTY OF THE FRAGMENT, NOT OF THE RENDER WIDTH.
//     The scar `twistAngle` paid for, re-proved here: a cell's normalised
//     centre is the same real number at every width and NOT the same float.
// =============================================================================
{
  const WIDTHS = [1200, 4094, 2048, 900];
  let bad = null;
  let n = 0;
  for (const id of ACTIVE) {
    for (const [bx, bw] of [[0, 400], [137, 91], [12, 1180], [600, 300]]) {
      for (const [by, bh] of [[0, 300], [41, 620], [900, 60]]) {
        const phases = new Set();
        for (const W of WIDTHS) {
          const H = W / 1.5;
          const k = W / 1200;
          const cell = { cx: (bx * k + (bw * k) / 2) / W, cy: (by * (H / 800) + (bh * (H / 800)) / 2) / H };
          phases.add(movePhase(id, cell));
          n++;
        }
        if (phases.size !== 1) bad ??= `${id} box ${bx},${by}: ${[...phases].join(' / ')}`;
      }
    }
  }
  ok('I6  the same fragment gets the same phase at every render width', !bad,
    bad ?? `${n} samples, all agreeing`);
}

{
  // DETERMINISM and SLOT DISTINCTNESS. A move whose every fragment agrees is
  // one rigid block, which is a camera move on the canvas and not a collage.
  let bad = null;
  const spread = {};
  for (const id of ACTIVE) {
    const seen = new Set();
    for (const cell of CELLS) {
      const p1 = movePhase(id, cell);
      const p2 = movePhase(id, cell);
      if (!Object.is(p1, p2)) bad ??= `${id} not deterministic`;
      seen.add(sampleMove({ id, ph: p1 }, MOVE_CYCLE_SEC * 0.37))
    }
    const sigs = new Set();
    for (const cell of CELLS) {
      const m = sampleMove({ id, ph: movePhase(id, cell) }, MOVE_CYCLE_SEC * 0.37);
      sigs.add(`${m.zoom.toFixed(6)}|${m.ax.toFixed(6)}|${m.ay.toFixed(6)}`);
    }
    spread[id] = sigs.size;
    if (id !== 'push' && sigs.size < 2) bad ??= `${id} moves every fragment identically`;
  }
  ok('I6b every move but PUSH distinguishes fragments; PUSH is one body on purpose', !bad,
    bad ?? Object.entries(spread).map(([k, v]) => `${k}:${v}`).join(' '));
}

// =============================================================================
// I7  SANITISED — the spec arrives off an analysis, which comes back from
//     project files and share codes.
// =============================================================================
{
  const JUNK = [
    undefined, null, 0, 1, '', 'drift', [], {}, { id: 'nope', ph: 0.5 },
    { id: 'drift' }, { id: 'drift', ph: NaN }, { id: 'drift', ph: Infinity },
    { id: 'drift', ph: -7 }, { id: 'drift', ph: 400 }, { id: 'drift', ph: '0.5' },
    { id: null, ph: null }, { id: 'still', ph: 0.5 },
  ];
  const TIMES = [0, 1, -1, NaN, Infinity, -Infinity, 1e9, 0.001, MOVE_CYCLE_SEC / 3];
  let bad = null;
  for (const spec of JUNK) {
    for (const t of TIMES) {
      let m;
      try { m = sampleMove(spec, t); } catch (e) { bad ??= `threw on ${JSON.stringify(spec)} @${t}: ${e.message}`; continue; }
      if (!m || !Number.isFinite(m.zoom) || !Number.isFinite(m.ax) || !Number.isFinite(m.ay)) {
        bad ??= `${JSON.stringify(spec)} @${t} -> ${JSON.stringify(m)}`;
      }
      if (m.zoom < 1 || m.zoom > MAX_MOVE_ZOOM) bad ??= `${JSON.stringify(spec)} @${t} zoom ${m.zoom}`;
    }
  }
  // And the crop built from junk is still a drawable rectangle.
  for (const spec of JUNK) {
    const c = calculateSmartCrop(BOXES[0], { ...IMAGES[0], analysis: anaFor(0, spec) }, 1, 3.1);
    if (!(c.sw > 0) || !(c.sh > 0) || !Number.isFinite(c.sx) || !Number.isFinite(c.sy)) {
      bad ??= `crop from junk spec ${JSON.stringify(spec)}: ${JSON.stringify(c)}`;
    }
  }
  ok('I7  every corrupt spec and every corrupt time yields usable geometry', !bad, bad ?? `${JUNK.length}x${TIMES.length} combinations`);
}

{
  let bad = null;
  if (isMoving({ id: 'still', ph: 0.4 })) bad ??= 'still counted as moving';
  if (isMoving(null) || isMoving(undefined) || isMoving({ id: 'nope' })) bad ??= 'junk counted as moving';
  for (const id of ACTIVE) if (!isMoving({ id, ph: 0.1 })) bad ??= `${id} not counted as moving`;
  // `withMove` hands back the SAME OBJECT on the no-op path.
  const photo = { id: 'p', analysis: { face: null, energy: null, color: null } };
  if (withMove(photo, 'still', { cx: 0.2, cy: 0.3 }) !== photo) bad ??= 'withMove copied on still';
  const moved = withMove(photo, 'drift', { cx: 0.2, cy: 0.3 });
  if (moved === photo || !moved.analysis.move || moved.analysis.move.id !== 'drift') bad ??= 'withMove did not attach';
  if (photo.analysis.move !== undefined) bad ??= 'withMove mutated its input';
  ok('I7b isMoving/withMove: still is a true no-op and never mutates the photo', !bad, bad ?? '');
}

// =============================================================================
// I8  THE CODE CARRIES IT — round trip, backwards compatibility, and the
//     over-long-group scar this feature made load-bearing.
// =============================================================================
{
  let bad = null;
  const base = snapRoll(rollDice(12345, 8));
  for (const id of MOVE_IDS) {
    const code = encodeRoll({ ...base, move: id });
    const back = decodeRoll(code);
    if (!back) { bad ??= `${id}: refused its own code ${code}`; continue; }
    if (back.move !== id) bad ??= `${id} -> ${back.move} (${code})`;
  }
  ok('I8  every move survives encode -> decode', !bad, bad ?? `${MOVE_IDS.length} ids`);
}

{
  // A code minted with a shuffle group folds it into the checksum; the move
  // must survive that path too, because that is the one the app actually mints.
  let bad = null;
  const base = snapRoll(rollDice(777, 5));
  for (const id of MOVE_IDS) {
    const code = encodeRoll({ ...base, move: id }, 'a3');
    const back = decodeRoll(code, 'a3');
    if (!back || back.move !== id) bad ??= `${id}: ${code} -> ${back ? back.move : 'null'}`;
    if (decodeRoll(code, 'a4') !== null) bad ??= `${id}: wrong shuffle group accepted`;
  }
  ok('I8b the move survives the checksummed shuffle-group path', !bad, bad ?? '');
}

{
  // BACKWARDS COMPATIBILITY. A pre-move code is the current one with the move
  // character removed and its checksum recomputed over the shorter body — which
  // is exactly what the previous build emitted. It must still open, as `still`.
  const base = snapRoll(rollDice(4242, 9));
  const cur = encodeRoll({ ...base, move: 'wander' });
  const [a, b, c] = cur.split('-');
  let bad = null;
  if (b.length !== 20) bad ??= `expected a 20-character middle group, got ${b.length}`;

  // Rebuild the 19-character (pre-move) form by re-deriving its checksum the
  // way the old encoder did: over head + the 17 body characters + seed.
  const legacyBody = b.slice(0, 17);
  const checksumOf = (body) => {
    let h = 7;
    for (let i = 0; i < body.length; i++) h = (h * 31 + parseInt(body[i], 36) + 1) % 1679616;
    return (h % 36 ** 2).toString(36).padStart(2, '0');
  };
  const legacy = `${a}-${(legacyBody + checksumOf((a + legacyBody + c).toLowerCase())).toUpperCase()}-${c}`;
  const back = decodeRoll(legacy);
  if (!back) bad ??= `a pre-move code was refused: ${legacy}`;
  else if (back.move !== 'still') bad ??= `pre-move code opened as ${back.move}`;
  else if (back.look !== base.look || back.twist !== base.twist || back.seed !== base.seed) {
    bad ??= 'a pre-move code opened as a different composition';
  }
  ok('I8c a code minted before the move still opens, as STILL', !bad, bad ?? `19-char group, look ${back?.look}`);
}

{
  // THE SCAR, CLOSED. The middle group is read by LENGTH and the checksum was
  // then sliced at a FIXED offset, so trailing junk was ignored. That was
  // untidy while there was one checksummed length above the flag form; it stops
  // being untidy now that a LONGER form is legal.
  const base = snapRoll(rollDice(90210, 7));
  const code = encodeRoll({ ...base, move: 'sway' });
  const [a, b, c] = code.split('-');
  let bad = null;
  let refused = 0;
  const junk = ['X', 'Z9', '00', 'QQQ', '1'];
  for (const j of junk) {
    if (decodeRoll(`${a}-${b}${j}-${c}`) !== null) bad ??= `accepted an over-long group: +${j}`;
    else refused++;
  }
  if (decodeRoll(code) === null) bad ??= 'the exact-length check refused a legitimate code';
  ok('I8d a group longer than any form this build mints is REFUSED', !bad,
    bad ?? `${refused}/${junk.length} appended-junk codes rejected`);
}

{
  // And an unknown move index is refused rather than defaulted to `still` —
  // same treatment as the look and the layout, for the same reason: opening a
  // moving collage as a still one is a substitution the recipient cannot see.
  const base = snapRoll(rollDice(31337, 6));
  const code = encodeRoll({ ...base, move: 'push' });
  const [a, b, c] = code.split('-');
  const hi = MOVE_IDS.length.toString(36); // one past the roster
  const forged = `${a}-${(b.slice(0, 17) + hi + b.slice(18)).toUpperCase()}-${c}`;
  ok('I8e a move index this build does not know is refused, not defaulted',
    decodeRoll(forged) === null, `forged index ${hi}`);
}

{
  // The dice reaches the whole roster, and reaches `still` most of the time.
  const counts = Object.fromEntries(MOVE_IDS.map((m) => [m, 0]));
  const N = 4000;
  for (let i = 0; i < N; i++) counts[rollDice(i * 7919 + 3, 10).move ?? 'still']++;
  const missing = MOVE_IDS.filter((m) => counts[m] === 0);
  const stillPct = (counts.still / N) * 100;
  ok('I8f the dice reaches every move, and leaves the collage still most of the time',
    missing.length === 0 && stillPct > 55 && stillPct < 80,
    `still ${stillPct.toFixed(1)}%  ${MOVE_IDS.filter(m => m !== 'still').map(m => `${m}:${counts[m]}`).join(' ')}`);
}

// =============================================================================
{
  // The roster and the code index must not drift apart.
  const bad = MOVES.length !== MOVE_IDS.length
    || MOVES.some((m, i) => m.id !== MOVE_IDS[i])
    || MOVE_IDS[0] !== 'still'
    || MOVE_IDS.length > 36;
  ok('I9  the chip roster and the code roster are the same list, still at index 0', !bad,
    `${MOVE_IDS.length} moves, ${MOVE_IDS.length} <= 36 (one base-36 character)`);
}

console.log('\nMOTION — invariant sweep\n');
for (const line of results) console.log('  ' + line);
console.log(`\n${results.length - failures}/${results.length} invariants hold\n`);
process.exit(failures ? 1 : 0);
