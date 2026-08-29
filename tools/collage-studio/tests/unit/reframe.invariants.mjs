/**
 * Invariant sweep for THE REFRAME — the picture moves inside its fragment.
 *
 * Run: node tests/unit/reframe.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * every claim below is about the shipped `reframe.dragToFrame` composed with the
 * shipped `renderer.calculateSmartCrop` — never a re-implementation of either.
 *
 * THE CLAIM THAT MATTERS — THE PICTURE FOLLOWS THE FINGER.
 *   Direct manipulation is not "it moves in roughly the right direction". It is
 *   that the photograph's displacement ON SCREEN equals the drag, exactly, for
 *   every fragment shape, every image shape, every zoom and every lean — until
 *   it runs out of photograph, at which point it stops and reverses on the very
 *   next pixel rather than banking invisible travel.
 *
 * THE SECOND ONE — THE FRAGMENT NEVER MOVES. A reframe re-points the SAMPLING
 *   and nothing else. The cell, its grown destination box, its angle and its
 *   pivot come back `Object.is`-identical, which is what keeps the wall a tiling.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

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

const { dragToFrame, frameOfCrop, frameBand, clampFrame, withReframe, isMeaningful } =
  await load('src/lib/reframe.ts', 'reframe');
const { calculateSmartCrop } = await load('src/lib/renderer.ts', 'renderer');

let failures = 0;
const results = [];
const ok = (name, pass, detail = '') => {
  results.push(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
  if (!pass) failures++;
};

// ---------------------------------------------------------------- the sweep --
const BOXES = [
  { x: 0, y: 0, w: 400, h: 300 },      // landscape cell
  { x: 120, y: 60, w: 200, h: 500 },   // portrait cell
  { x: 40, y: 40, w: 260, h: 260 },    // square cell
  { x: 0, y: 700, w: 1200, h: 180 },   // letterbox band
  { x: 900, y: 0, w: 90, h: 700 },     // sliver
];
const IMAGES = [
  { width: 4000, height: 3000 },  // 4:3
  { width: 3000, height: 4000 },  // 3:4
  { width: 2000, height: 2000 },  // 1:1
  { width: 6000, height: 1200 },  // panorama
  { width: 800, height: 1600 },   // tall phone shot
];
const ZOOMS = [1.0, 1.15, 1.6, 2.4];
const TWISTS = [0, (7 * Math.PI) / 180, (-13 * Math.PI) / 180, (22 * Math.PI) / 180];
const ANCHORS = [null, { x: 0.5, y: 0.5 }, { x: 0.18, y: 0.72 }, { x: 0.86, y: 0.31 }];
const DRAGS = [
  [12, 0], [0, 12], [-30, 18], [45, -60], [3, 3], [-7, 2],
  [400, 400], [-900, 250], [0, -1000],
];

const an = (face, twist, frame) => ({
  face, energy: { x: 0.5, y: 0.5 }, color: null,
  ...(twist ? { twist } : {}),
  ...(frame ? { frame } : {}),
});

const cropFor = (box, img, zoom, twist, frame, face) =>
  calculateSmartCrop(box, { width: img.width, height: img.height, analysis: an(face, twist, frame) }, zoom);

// I2 / I3 / I7 in one pass over the cross product.
let follows = 0, followBad = 0, worstFollow = 0;
let inside = 0, insideBad = 0;
let frozen = 0, frozenBad = 0;
let clamped = 0;
let noRoom = 0, noRoomBad = 0;
let reversible = 0, reversibleBad = 0, worstReverse = 0;
let idem = 0, idemBad = 0;
let naiveWorstOffAxis = 0;

for (const box of BOXES) {
  for (const img of IMAGES) {
    for (const zoom of ZOOMS) {
      for (const twist of TWISTS) {
        for (const face of ANCHORS) {
          const c0 = cropFor(box, img, zoom, twist, null, face);
          const band = frameBand(c0, img);
          for (const [dx, dy] of DRAGS) {
            const f1 = dragToFrame(c0, img, dx, dy);
            const c1 = cropFor(box, img, zoom, twist, f1, face);

            // --- I7 THE FRAGMENT NEVER MOVES -------------------------------
            const still = Object.is(c1.dx, c0.dx) && Object.is(c1.dy, c0.dy)
              && Object.is(c1.dw, c0.dw) && Object.is(c1.dh, c0.dh)
              && Object.is(c1.twist, c0.twist) && Object.is(c1.tcx, c0.tcx)
              && Object.is(c1.tcy, c0.tcy)
              && Object.is(c1.sw, c0.sw) && Object.is(c1.sh, c0.sh);
            frozen++; if (!still) frozenBad++;

            // --- I3 THE CROP NEVER LEAVES THE PHOTOGRAPH -------------------
            const within = c1.sx >= -1e-9 && c1.sy >= -1e-9
              && c1.sx + c1.sw <= img.width + 1e-9
              && c1.sy + c1.sh <= img.height + 1e-9;
            inside++; if (!within) insideBad++;

            // Did the clamp bite? Strictly-interior means it did not.
            const eps = 1e-9;
            const free = f1.x > band.minX + eps && f1.x < band.maxX - eps
              && f1.y > band.minY + eps && f1.y < band.maxY - eps;

            // --- I5 NO ROOM, NO TRAVEL -------------------------------------
            if (band.maxX - band.minX <= 0) {
              noRoom++;
              if (Math.abs(c1.sx - c0.sx) > 1e-6) noRoomBad++;
            }
            if (band.maxY - band.minY <= 0) {
              noRoom++;
              if (Math.abs(c1.sy - c0.sy) > 1e-6) noRoomBad++;
            }

            // --- I2 THE PICTURE FOLLOWS THE FINGER (unclamped only) --------
            if (free) {
              const dsx = (c1.sx + c1.sw / 2) - (c0.sx + c0.sw / 2);
              const dsy = (c1.sy + c1.sh / 2) - (c0.sy + c0.sh / 2);
              const px = -dsx * (c0.dw / c0.sw);
              const py = -dsy * (c0.dh / c0.sh);
              const ct = Math.cos(twist), st = Math.sin(twist);
              const sx = px * ct - py * st;
              const sy = px * st + py * ct;
              const err = Math.hypot(sx - dx, sy - dy);
              follows++;
              worstFollow = Math.max(worstFollow, err);
              if (err > 1e-6) followBad++;

              // What the REJECTED design (no -twist rotation) would have done:
              // how far off the finger's line the picture would have travelled.
              if (twist !== 0) {
                const kx = c0.sw / c0.dw, ky = c0.sh / c0.dh;
                const nf = clampFrame({
                  x: frameOfCrop(c0, img).x - (dx * kx) / img.width,
                  y: frameOfCrop(c0, img).y - (dy * ky) / img.height,
                }, c0, img);
                const nc = cropFor(box, img, zoom, twist, nf, face);
                const ndsx = (nc.sx + nc.sw / 2) - (c0.sx + c0.sw / 2);
                const ndsy = (nc.sy + nc.sh / 2) - (c0.sy + c0.sh / 2);
                const npx = -ndsx * (c0.dw / c0.sw), npy = -ndsy * (c0.dh / c0.sh);
                const nsx = npx * ct - npy * st, nsy = npx * st + npy * ct;
                const len = Math.hypot(dx, dy) || 1;
                // component of the error perpendicular to the intended drag
                const ux = dx / len, uy = dy / len;
                const ex = nsx - dx, ey = nsy - dy;
                const perp = Math.abs(ex * -uy + ey * ux) / len;
                naiveWorstOffAxis = Math.max(naiveWorstOffAxis, perp);
              }

              // --- I4 REVERSIBLE -------------------------------------------
              const back = dragToFrame(c1, img, -dx, -dy);
              const bandBack = frameBand(c1, img);
              const backFree = back.x > bandBack.minX + eps && back.x < bandBack.maxX - eps
                && back.y > bandBack.minY + eps && back.y < bandBack.maxY - eps;
              if (backFree) {
                const here0 = frameOfCrop(c0, img);
                const e = Math.max(Math.abs(back.x - here0.x), Math.abs(back.y - here0.y));
                reversible++;
                worstReverse = Math.max(worstReverse, e);
                if (e > 1e-9) reversibleBad++;
              }
            } else {
              clamped++;
              // --- I6 NO ACCUMULATION AT THE EDGE --------------------------
              // PER AXIS, because a drag can run out of photograph sideways
              // while it still has room vertically: the axis that hit its edge
              // must not move again, and the axis that did not must keep going.
              // Asserting both together was this sweep's own first bug.
              const again = dragToFrame(c1, img, dx, dy);
              const atX = Math.abs(f1.x - band.minX) <= eps || Math.abs(f1.x - band.maxX) <= eps;
              const atY = Math.abs(f1.y - band.minY) <= eps || Math.abs(f1.y - band.maxY) <= eps;
              idem++;
              if ((atX && Math.abs(again.x - f1.x) > 1e-12)
                || (atY && Math.abs(again.y - f1.y) > 1e-12)) idemBad++;
            }
          }
        }
      }
    }
  }
}

ok('I2 the picture follows the finger, exactly', followBad === 0,
  `${follows} unclamped drags, worst error ${worstFollow.toExponential(2)} canvas units`);
ok('I3 the crop never leaves the photograph', insideBad === 0, `${inside} crops`);
ok('I4 a drag and its reverse return to the start', reversibleBad === 0,
  `${reversible} round trips, worst ${worstReverse.toExponential(2)}`);
ok('I5 an axis with no room does not travel', noRoomBad === 0, `${noRoom} zero-slack axes`);
ok('I6 an axis at its edge banks nothing when dragged again', idemBad === 0, `${idem} clamped drags re-dragged`);
ok('I7 the fragment never moves', frozenBad === 0, `${frozen} reframes`);
ok('the rejected design (no -twist rotation) is measurably wrong',
  naiveWorstOffAxis > 0.3,
  `worst off-axis travel ${(naiveWorstOffAxis * 100).toFixed(1)}% of the drag`);

// --- I1 IDENTITY BY REFERENCE ------------------------------------------------
{
  const photo = { id: 'a', analysis: an({ x: 0.4, y: 0.4 }, 0.1, null) };
  const same = withReframe(photo, undefined) === photo
    && withReframe(photo, null) === photo
    && withReframe(photo, { x: NaN, y: 0.5 }) === photo
    && withReframe(photo, { x: 0.5, y: Infinity }) === photo;
  ok('I1 no frame hands the same object back (Object.is)', same);
  const wrapped = withReframe(photo, { x: 0.3, y: 0.7 });
  ok('I1b a frame is a copy that keeps every other analysis field',
    wrapped !== photo && wrapped.analysis.frame.x === 0.3
    && wrapped.analysis.twist === 0.1 && wrapped.analysis.face.x === 0.4);
}

// --- I8 REFRAMING TO WHERE YOU ALREADY ARE CHANGES NOTHING -------------------
{
  let n = 0, bad = 0, worst = 0;
  for (const box of BOXES) for (const img of IMAGES) for (const zoom of ZOOMS) for (const twist of TWISTS) {
    const c0 = cropFor(box, img, zoom, twist, null, { x: 0.42, y: 0.61 });
    const c1 = cropFor(box, img, zoom, twist, frameOfCrop(c0, img), { x: 0.42, y: 0.61 });
    const e = Math.max(Math.abs(c1.sx - c0.sx), Math.abs(c1.sy - c0.sy));
    n++; worst = Math.max(worst, e);
    if (e > 1e-6) bad++;
  }
  ok('I8 a zero-length drag is a no-op on the drawn rect', bad === 0,
    `${n} setups, worst ${worst.toExponential(2)} source px`);
}

// --- I9 A FRAME OVERRIDES THE FOCUS ROSTER'S RE-POINTED FACE -----------------
{
  const img = { width: 4000, height: 3000 };
  const box = { x: 0, y: 0, w: 300, h: 600 };
  const withFace = cropFor(box, img, 1, 0, null, { x: 0.9, y: 0.5 });
  const withBoth = cropFor(box, img, 1, 0, { x: 0.2, y: 0.5 }, { x: 0.9, y: 0.5 });
  ok('I9 a hand-set frame beats the detector and the focus roster',
    Math.abs(withBoth.sx - withFace.sx) > 1,
    `sx ${withFace.sx.toFixed(1)} -> ${withBoth.sx.toFixed(1)}`);
}

// --- I10 isMeaningful is a half source pixel ---------------------------------
{
  const img = { width: 4000, height: 3000 };
  const tiny = 0.5 / 3000 / 2;
  ok('I10 a sub-pixel drag is not a reframe',
    !isMeaningful({ x: 0.5 + tiny, y: 0.5 }, { x: 0.5, y: 0.5 }, img)
    && isMeaningful({ x: 0.5 + 0.01, y: 0.5 }, { x: 0.5, y: 0.5 }, img));
}

console.log(results.join('\n'));
console.log(`\n${results.length - failures}/${results.length} invariants hold`);
process.exit(failures ? 1 : 0);
