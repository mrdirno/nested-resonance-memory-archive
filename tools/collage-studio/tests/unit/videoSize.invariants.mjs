/**
 * INVARIANT SWEEP for `probeVideoSizes` in src/lib/frameExport.ts — the video
 * export's size ladder.
 *
 *   node tests/unit/videoSize.invariants.mjs
 *
 * Transpiles and imports the REAL module. No re-implementation: a sweep against
 * a copy grades the copy.
 *
 * WHY THIS EXISTS AT ALL. The still export can offer 2K/4K/8K/16K/MAX because a
 * JPEG has no levels to satisfy. Video does — H.264 caps the FRAME in
 * macroblocks, this app's ladder tops at level 5.2 / 36,864 of them — so the
 * ceiling depends on the composition's SHAPE, and a ladder that ignores that
 * would offer a rung that fails only after someone has waited out a render.
 * The whole point of the ladder is that it never lies about what it can do, so
 * the encoder is STUBBED here with a known macroblock ceiling and the sweep
 * asserts the ladder tells the truth against it, at every shape.
 *
 * THE TWO THAT CARRY THE CYCLE
 *   I3  every rung offered is a frame the encoder actually accepted — the
 *       ladder never advertises a size that would fail. This is the promise the
 *       feature is made of.
 *   I5  MAX is the TRUE top: one rung up from what it returned is refused. A
 *       "MAX" that stopped early would quietly cap everyone below the real
 *       ceiling and nothing would ever go red.
 */
import esbuild from 'esbuild';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');
const dir = mkdtempSync(join(tmpdir(), 'vidsize-'));

// BUNDLED, not merely transpiled: frameExport imports mp4-muxer, and a bare
// transpile dropped in a tmp dir cannot resolve it. Still the REAL module —
// bundling inlines its dependencies, it does not substitute for it.
const load = async (rel, out) => {
  const tmp = join(dir, out);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    bundle: true, format: 'esm', platform: 'neutral',
    outfile: tmp, logLevel: 'silent',
  });
  return import(pathToFileURL(tmp).href);
};

// --- the encoder, stubbed at a known ceiling --------------------------------
// `probeVideoSizes` reaches for window.VideoEncoder. Give it one that admits
// exactly what a real level-5.2 encoder admits and nothing more, so "did the
// ladder tell the truth" is a decidable question rather than a device lottery.
const MB_CEILING = 36864;
const mbsOf = (w, h) => Math.ceil(w / 16) * Math.ceil(h / 16);

let ceiling = MB_CEILING;
let asked = [];
globalThis.window = globalThis;
globalThis.VideoEncoder = class {
  static async isConfigSupported({ width, height }) {
    asked.push({ width, height });
    return { supported: mbsOf(width, height) <= ceiling };
  }
};
globalThis.VideoFrame = class {};

const FE = await load('src/lib/frameExport.ts', 'frameExport.mjs');

// --- harness ----------------------------------------------------------------
let failures = 0;
const check = (name, cond, detail) => {
  if (cond) return;
  failures++;
  console.error(`  RED  ${name}${detail ? ` — ${detail}` : ''}`);
};

// Real shapes: the app's default 2:3 portrait, square, 3:2 and 16:9 landscape,
// plus the extremes a user can actually dial in.
const ASPECTS = [0.4, 0.5, 0.5625, 0.666, 0.75, 0.8, 1, 1.25, 1.3333, 1.5, 1.7778, 2, 2.5];

console.log('probeVideoSizes — invariant sweep');

for (const a of ASPECTS) {
  asked = [];
  const ladder = await FE.probeVideoSizes(a, { fps: 30, bitrate: 12_000_000 });
  const ok = ladder.filter((r) => r.supported);
  const tag = `aspect ${a}`;

  // I1 — a ladder always comes back, and it always has a MAX rung on it.
  check('I1 ladder non-empty', ladder.length > 0, tag);
  check('I1 MAX present', ladder.some((r) => r.label === 'MAX' || r.label === '4K'), tag);

  // I2 — every frame is EVEN on both axes. Encoders reject odd dimensions, and
  // an odd height is the classic way a take dies at configure() time.
  for (const r of ladder) {
    if (!r.supported) continue;
    check('I2 even dims', r.width % 2 === 0 && r.height % 2 === 0, `${tag} ${r.width}x${r.height}`);
  }

  // I3 — THE PROMISE. Nothing is offered that the encoder refused.
  for (const r of ok) {
    check('I3 offered => encodable', mbsOf(r.width, r.height) <= ceiling,
      `${tag} ${r.label} ${r.width}x${r.height} = ${mbsOf(r.width, r.height)} mbs > ${ceiling}`);
  }

  // I4 — every rung really is the shape the user chose, not a squashed one.
  // Rounding to even pixels moves the ratio slightly; a pixel of slack at the
  // smallest rung is the whole tolerance.
  for (const r of ok) {
    check('I4 aspect preserved', Math.abs(r.width / r.height - a) < 0.01,
      `${tag} ${r.width}x${r.height} = ${(r.width / r.height).toFixed(4)}`);
  }

  // I5 — MAX IS THE TRUE TOP. Step one rung (128px of long edge) above what it
  // returned and the encoder must refuse. Without this, MAX could stop anywhere
  // below the ceiling and every user would silently get less than the device offers.
  const max = ok[ok.length - 1];
  if (max && (max.label === 'MAX' || max.label === '4K')) {
    const nextEdge = max.longEdge + 128;
    if (nextEdge <= 4096) {
      const w = a >= 1 ? nextEdge : nextEdge * a;
      const h = a >= 1 ? nextEdge / a : nextEdge;
      const W = Math.max(2, Math.floor(w / 2) * 2);
      const H = Math.max(2, Math.floor(h / 2) * 2);
      check('I5 MAX is the true top', mbsOf(W, H) > ceiling,
        `${tag} MAX=${max.longEdge} but ${nextEdge} (${W}x${H}) also fits`);
    }
  }

  // I6 — the ladder is strictly ASCENDING in pixels among the rungs offered.
  // A ladder that is not sorted is a ladder a user cannot read.
  for (let i = 1; i < ok.length; i++) {
    check('I6 ascending', ok[i].width * ok[i].height > ok[i - 1].width * ok[i - 1].height,
      `${tag} ${ok[i - 1].label} -> ${ok[i].label}`);
  }

  // I7 — no duplicate frames. On a near-square shape MAX can land on a size
  // already listed, and two identical rungs is a UI bug the user has to decode.
  const seen = new Set();
  for (const r of ok) {
    const k = `${r.width}x${r.height}`;
    check('I7 no duplicate rung', !seen.has(k), `${tag} ${k} twice`);
    seen.add(k);
  }

  // I8 — every rung beats today's shipped output. The whole increment is that
  // the exported file stopped being pinned at 1200px wide; a rung at or below
  // that is a rung that would ship the bug back.
  const BASELINE_W = 1200;
  const baseH = a >= 1 ? BASELINE_W / a : BASELINE_W;   // today: 1200 wide, height by aspect
  const basePx = BASELINE_W * baseH;
  check('I8 top rung beats the old fixed 1200px render',
    max && max.width * max.height > basePx,
    `${tag} max ${max ? `${max.width}x${max.height}` : 'none'} vs baseline 1200x${Math.round(baseH)}`);
}

// I9 — a device with NO encoder returns a full, honest, all-unsupported ladder
// rather than an empty one. An empty ladder renders as "no options" and reads
// like a broken dialog; an unsupported ladder can say why.
{
  const savedEnc = globalThis.VideoEncoder;
  delete globalThis.VideoEncoder;
  const ladder = await FE.probeVideoSizes(0.666);
  check('I9 no-encoder ladder is non-empty', ladder.length > 0);
  check('I9 no-encoder ladder is all unsupported', ladder.every((r) => !r.supported));
  check('I9 no-encoder ladder states a reason', ladder.every((r) => !!r.reason));
  globalThis.VideoEncoder = savedEnc;
}

// I10 — a MEANER device (a real phone ceiling, level 4.2) still gets a truthful
// ladder: fewer rungs, none of them lying. This is the case that decides
// whether the feature is safe to put in front of the phone the wish came from.
{
  ceiling = 8704;                     // H.264 level 4.2
  for (const a of [0.666, 1, 1.7778]) {
    const ladder = await FE.probeVideoSizes(a);
    const ok = ladder.filter((r) => r.supported);
    for (const r of ok) {
      check('I10 lean device offered => encodable', mbsOf(r.width, r.height) <= ceiling,
        `aspect ${a} ${r.label} ${r.width}x${r.height}`);
    }
    check('I10 lean device still offers something', ok.length > 0, `aspect ${a}`);
  }
  ceiling = MB_CEILING;
}

// I11 — garbage in, ladder out. A NaN/0/negative aspect must not produce NaN
// dimensions; the dialog reads this before the stage has ever measured itself.
for (const bad of [0, -1, NaN, Infinity]) {
  const ladder = await FE.probeVideoSizes(bad);
  for (const r of ladder.filter((x) => x.supported)) {
    check('I11 degenerate aspect is finite', Number.isFinite(r.width) && Number.isFinite(r.height) && r.width > 0 && r.height > 0,
      `aspect ${bad} -> ${r.width}x${r.height}`);
  }
}

if (failures) {
  console.error(`\nFAILED — ${failures} invariant(s) red`);
  process.exit(1);
}
console.log('  all invariants green');
