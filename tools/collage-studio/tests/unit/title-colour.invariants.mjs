// Author: Aldrin Payopay · GPL-3.0-only
// C3733 — THE TITLE COLOUR. The REAL title module, transpiled, swept across every
// named colour: the derived scrim always separates further than the other family
// and clears the large-text contrast floor; `white` is the byte-identical legacy
// pair; the ink and scrim the plan carries are the exact strings BOTH emitters
// paint, so the four surfaces cannot diverge.
import assert from 'node:assert/strict';
import esbuild from 'esbuild';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const temp = mkdtempSync(join(tmpdir(), 'title-'));
try {
  const root = join(dirname(fileURLToPath(import.meta.url)), '../..');
  await esbuild.build({
    entryPoints: [join(root, 'src/lib/title.ts')],
    outfile: join(temp, 'title.mjs'),
    bundle: true, platform: 'neutral', format: 'esm', logLevel: 'silent',
  });
  const T = await import(pathToFileURL(join(temp, 'title.mjs')).href);
  const {
    titlePalette, relLuminance, contrastRatio,
    planTitle, scaleTitlePlan, drawTitlePlan, titlePlanToSvg,
    TITLE_INK, TITLE_PLATE,
  } = T;

  let checks = 0;
  const ok = (cond, msg) => { assert.ok(cond, msg); checks++; };

  const COLORS = ['white', 'black', 'yellow', 'red', 'blue', 'pink'];
  const FLOOR = 3.0;               // WCAG AA for large text
  const LIGHT_SCRIM = 'rgba(255,255,255,0.60)';
  // The solid anchor each scrim family is a translucent skin of.
  const anchorOf = (scrim) => (scrim === TITLE_PLATE ? '#000000' : '#ffffff');

  // ---- THE CONTRAST MATHS: known anchors ----------------------------------
  ok(Math.abs(contrastRatio('#ffffff', '#000000') - 21) < 1e-9, 'white vs black is exactly 21:1');
  ok(Math.abs(contrastRatio('#123456', '#123456') - 1) < 1e-9, 'a colour against itself is 1:1');
  ok(contrastRatio('#ff453a', '#000000') === contrastRatio('#000000', '#ff453a'), 'contrast is symmetric');
  ok(relLuminance('#ffffff') > relLuminance('#808080') && relLuminance('#808080') > relLuminance('#000000'),
    'luminance is monotone white > grey > black');
  ok(Math.abs(relLuminance('#000000')) < 1e-12 && Math.abs(relLuminance('#ffffff') - 1) < 1e-9,
    'luminance is 0 at black and 1 at white');
  ok(relLuminance('#fff') === relLuminance('#ffffff') && relLuminance('#f00') === relLuminance('#ff0000'),
    '#rgb shorthand expands to #rrggbb');

  // ---- THE PALETTE: identity, argmax polarity, floor, determinism ---------
  const white = titlePalette('white');
  ok(white.ink === TITLE_INK && white.scrim === TITLE_PLATE, 'white IS the legacy pair, exactly');
  assert.deepEqual(titlePalette(undefined), white); checks++;      // absent colour == white
  assert.deepEqual(titlePalette('nonsense'), white); checks++;     // unknown colour == white

  const inkSeen = new Set();
  for (const c of COLORS) {
    const p = titlePalette(c);
    ok(/^#[0-9a-f]{6}$/i.test(p.ink), `${c}: ink is a #rrggbb hex`);
    ok(p.scrim === TITLE_PLATE || p.scrim === LIGHT_SCRIM, `${c}: scrim is one of the two families`);
    inkSeen.add(p.ink.toLowerCase());

    // THE POLARITY IS ARGMAX, not a guess: the chosen family separates at least
    // as far from the ink as the family we did not choose.
    const chosen = contrastRatio(p.ink, anchorOf(p.scrim));
    const other = contrastRatio(p.ink, anchorOf(p.scrim === TITLE_PLATE ? LIGHT_SCRIM : TITLE_PLATE));
    ok(chosen >= other, `${c}: the derived scrim separates further than the other family (${chosen.toFixed(2)} ≥ ${other.toFixed(2)})`);
    ok(chosen >= FLOOR, `${c}: ink clears the large-text floor against its scrim (${chosen.toFixed(2)} ≥ ${FLOOR})`);

    assert.deepEqual(titlePalette(c), p); checks++;                 // deterministic
  }
  ok(inkSeen.size === COLORS.length, 'every named colour has a distinct ink');
  // Only a DARK ink flips the scrim to the light family; every luminous colour
  // keeps the legacy dark plate. This is the whole visible promise.
  ok(titlePalette('black').scrim === LIGHT_SCRIM, 'a black title gets the light scrim');
  for (const c of ['white', 'yellow', 'red', 'blue', 'pink'])
    ok(titlePalette(c).scrim === TITLE_PLATE, `${c} keeps the legacy dark plate`);

  // ---- THE PLAN BAKES THE COLOUR, and the no-op rule survives -------------
  const measure = (text, px) => text.length * px * 0.5;   // deterministic, pure
  ok(planTitle({ text: '' }, 1, measure) === null, 'an empty title plans nothing');
  ok(planTitle({ text: '   ' }, 1, measure) === null, 'a whitespace title plans nothing');
  ok(planTitle(null, 1, measure) === null, 'no spec plans nothing');

  for (const c of COLORS) {
    const plan = planTitle({ text: 'Hello world', place: 'bl', size: 'md', color: c }, 1, measure);
    const pal = titlePalette(c);
    ok(plan && plan.ink === pal.ink && plan.scrim === pal.scrim, `${c}: the plan carries the resolved ink and scrim`);
    // The default (no colour on the spec) is the white plan, byte-for-byte.
    if (c === 'white') {
      const bare = planTitle({ text: 'Hello world', place: 'bl', size: 'md' }, 1, measure);
      assert.deepEqual(bare, plan); checks++;
    }
    // Scale preserves the colours (k=1 is identity; k≠1 rebuilds and must carry them).
    const same = scaleTitlePlan(plan, 1);
    ok(same === plan, `${c}: k=1 returns the very object`);
    const big = scaleTitlePlan(plan, 2);
    ok(big.ink === plan.ink && big.scrim === plan.scrim, `${c}: scaling keeps ink and scrim`);
    ok(big.fontPx === plan.fontPx * 2, `${c}: scaling still scales geometry`);
  }

  // ---- BOTH EMITTERS PAINT THE PLAN'S OWN STRINGS ------------------------
  // A fake 2D context that records every fillStyle it is handed, in order.
  const recorder = () => {
    const fills = [];
    let _fs = '';
    return {
      fills,
      ctx: {
        save() {}, restore() {}, beginPath() {}, moveTo() {}, arcTo() {},
        closePath() {}, fill() {}, fillText() {},
        set fillStyle(v) { _fs = v; fills.push(v); },
        get fillStyle() { return _fs; },
        set font(_v) {}, get font() { return ''; },
        set textAlign(_v) {}, set textBaseline(_v) {},
      },
    };
  };
  for (const c of COLORS) {
    const plan = planTitle({ text: 'One two three four', place: 'tc', size: 'lg', color: c }, 1.5, measure);
    const svg = titlePlanToSvg(plan);
    ok(svg.includes(`fill="${plan.scrim}"`), `${c}: the SVG plate fill is the plan's scrim`);
    ok(svg.includes(`fill="${plan.ink}"`), `${c}: the SVG text fill is the plan's ink`);

    const r = recorder();
    drawTitlePlan(r.ctx, plan);
    ok(r.fills[0] === plan.scrim, `${c}: the canvas paints the scrim first`);
    ok(r.fills[1] === plan.ink, `${c}: then the ink — the SAME strings the SVG used`);
  }
  // The one guarantee the module exists for: an UNTITLED render emits nothing.
  ok(titlePlanToSvg(null) === '', 'a null plan is an empty SVG string');
  const rNull = recorder();
  drawTitlePlan(rNull.ctx, null);
  ok(rNull.fills.length === 0, 'a null plan paints not one instruction on the canvas');

  // The legacy pair still appears verbatim for the default title, on both surfaces.
  const legacy = planTitle({ text: 'Legacy' }, 1, measure);
  ok(titlePlanToSvg(legacy).includes(`fill="${TITLE_INK}"`) && titlePlanToSvg(legacy).includes(`fill="${TITLE_PLATE}"`),
    'the default title still emits the exact legacy ink and plate');

  console.log(`TITLE COLOUR invariants PASS: ${checks} checks — 6 colours, argmax scrim polarity, WCAG floor, the plan's ink/scrim are the exact strings both emitters paint, white is byte-identical to legacy`);
} finally {
  rmSync(temp, { recursive: true, force: true });
}
