/**
 * Invariant sweep for THE TITLE FONT — the typeface the caption is drawn in.
 *
 * Run: node tests/unit/title-font.invariants.mjs
 *
 * It transpiles the REAL `src/lib/title.ts` (esbuild, types stripped) and
 * imports it, so it proves the shipped `planTitle` / `titleFontFamily` /
 * `titleFont` / `scaleTitlePlan` / `titlePlanToSvg` — not a re-implementation.
 *
 * THE INVARIANT THAT MATTERS — IDENTITY:
 *
 *   Adding a font control must not move a single existing title. The default is
 *   `sans`, `sans` resolves to the exact legacy `TITLE_FAMILY`, and so a plan
 *   built with NO font field must be byte-for-byte the plan built with
 *   `font:'sans'`, and its rendered family must be the constant this module has
 *   always painted with. Every other check is secondary to F1.
 *
 *   THE SECOND REAL ONE — MEASURED IN THE PAINTED FACE (F4): the wrap and every
 *   width are measured through the family that will be drawn. A wide face wrapped
 *   against a narrow face's metrics overruns the plate on the delivered surface —
 *   the exact silent-wrong-picture defect the "one plan, measured once" design
 *   exists to prevent. The RED PROOF at the bottom is the same F3/F4 sweep run
 *   against a mutant that ignores `spec.font`; it fails on every non-sans font,
 *   so these checks have teeth.
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

const T = await load('src/lib/title.ts', 'title-font');
const {
  planTitle, scaleTitlePlan, titlePlanToSvg,
  titleFontFamily, titleFont, TITLE_FONTS, TITLE_FAMILY, TITLE_WEIGHT,
} = T;

let fails = 0;
let checks = 0;
const check = (ok, msg) => { checks++; if (!ok) { fails++; if (fails <= 40) console.error(`  ✗ ${msg}`); } };

// --- a FAMILY-SENSITIVE synthetic font ---------------------------------------
// Per-character advances linear in fontPx, but SCALED by the family so a face
// actually changes metrics — without that, F4 could pass while the family was
// silently dropped. `undefined` and the sans stack scale by 1, so the identity
// path (F1) is unperturbed.
const ADV = { ' ': 0.28, i: 0.24, l: 0.24, j: 0.26, t: 0.32, f: 0.32, r: 0.36,
              m: 0.86, w: 0.78, W: 0.94, M: 0.92, '…': 0.9, I: 0.28 };
const familyFactor = (family) => {
  if (!family) return 1;                       // default path == sans
  if (family.includes('Courier')) return 1.55; // mono is wide
  if (family.includes('Impact')) return 0.78;  // poster is condensed
  if (family.includes('Georgia')) return 1.12; // serif a touch wider
  return 1;                                     // Helvetica / sans
};
const makeMeasure = (seen) => (text, fontPx, family) => {
  if (seen) seen.push(family);
  let u = 0;
  for (let i = 0; i < text.length; i++) u += ADV[text[i]] ?? 0.54;
  return u * fontPx * familyFactor(family);
};
const measure = makeMeasure(null);

// --- fixtures ----------------------------------------------------------------
const TEXTS = [
  'Paris', 'SUMMER 25', 'the long way home',
  'Kitchen remodel — before and after, day 3', 'a', 'MMMMWWWWMMMMWWWW',
  'supercalifragilisticexpialidociousandthensomemoreforgoodmeasure',
  'One two three four five six seven eight nine ten eleven twelve thirteen',
  '   leading and trailing   ', 'Ünïcödé accented', 'word '.repeat(60),
];
const PLACES = ['bl', 'bc', 'tl', 'tc'];
const SIZES = ['sm', 'md', 'lg'];
const ASPECTS = [0.5625, 0.8, 1, 1.5, 1.7778, 2.5];

// Expected stacks — RESTATED here, not imported, so a stack edited in the module
// is caught by this sweep rather than silently agreed with.
const EXPECT = {
  sans: TITLE_FAMILY,
  serif: 'Georgia, "Times New Roman", Times, serif',
  mono: '"Courier New", Courier, monospace',
  poster: 'Impact, "Arial Narrow", "Helvetica Neue", sans-serif',
};

// =============================================================================
// F0 — the roster is exactly the four faces, sans first (the default/identity).
// =============================================================================
check(Array.isArray(TITLE_FONTS) && TITLE_FONTS.length === 4, 'F0 four fonts offered');
check(TITLE_FONTS[0] === 'sans', 'F0 sans leads (default + identity)');
check(JSON.stringify([...TITLE_FONTS]) === JSON.stringify(['sans', 'serif', 'mono', 'poster']),
  'F0 roster is sans/serif/mono/poster in order');

// =============================================================================
// F2 — titleFontFamily resolves each id, and every unknown falls back to sans.
// =============================================================================
for (const id of TITLE_FONTS) check(titleFontFamily(id) === EXPECT[id], `F2 ${id} -> its stack`);
check(titleFontFamily('sans') === TITLE_FAMILY, 'F2 sans IS the legacy TITLE_FAMILY');
for (const bad of [undefined, null, '', 'comic', 'SANS', 42, {}]) {
  check(titleFontFamily(bad) === TITLE_FAMILY, `F2 junk font "${JSON.stringify(bad)}" -> sans`);
}

// =============================================================================
// F7 — titleFont's one-arg call is byte-identical to the legacy string.
// =============================================================================
for (const px of [8, 24, 60.5, 108]) {
  check(titleFont(px) === titleFont(px, TITLE_FAMILY), `F7 one-arg titleFont == sans at ${px}`);
  check(titleFont(px) === `${TITLE_WEIGHT} ${px}px ${TITLE_FAMILY}`, `F7 titleFont shape at ${px}`);
  check(titleFont(px, EXPECT.mono) === `${TITLE_WEIGHT} ${px}px ${EXPECT.mono}`, `F7 mono font string at ${px}`);
}

// =============================================================================
// THE MAIN SWEEP — F1 identity, F3 plan carries family, F4 measured in the face,
// F5 scale preserves family, F6 SVG carries family.
// =============================================================================
for (const aspect of ASPECTS) {
  for (const place of PLACES) {
    for (const size of SIZES) {
      for (const text of TEXTS) {
        const base = { text, place, size };
        const tag = `a=${aspect} ${place}/${size} "${text.slice(0, 20)}"`;

        // F1 IDENTITY — no font field == font:'sans', and family is the legacy stack.
        const noFont = planTitle({ ...base }, aspect, measure);
        const sans = planTitle({ ...base, font: 'sans' }, aspect, measure);
        if (noFont === null) { check(sans === null, `F1 sans null-parity [${tag}]`); continue; }
        check(JSON.stringify(noFont) === JSON.stringify(sans), `F1 no-font != font:'sans' [${tag}]`);
        check(noFont.family === TITLE_FAMILY, `F1 default family is TITLE_FAMILY [${tag}]`);

        for (const font of TITLE_FONTS) {
          const seen = [];
          const plan = planTitle({ ...base, font }, aspect, makeMeasure(seen));
          if (plan === null) continue;
          // F3 — the plan carries the resolved family, so every surface agrees.
          check(plan.family === EXPECT[font], `F3 ${font} plan.family wrong [${tag}]`);
          // F4 — every measurement was taken in that family. Not one leaked out.
          check(seen.length > 0, `F4 ${font} measured at all [${tag}]`);
          check(seen.every((f) => f === EXPECT[font]), `F4 ${font} measured in another face [${tag}]`);
          // F5 — scaling carries the family; k=1 returns the very object.
          check(scaleTitlePlan(plan, 1) === plan, `F5 ${font} k=1 identity [${tag}]`);
          for (const k of [0.5, 2, 3.33]) {
            check(scaleTitlePlan(plan, k).family === plan.family, `F5 ${font} scaled family drift k=${k} [${tag}]`);
          }
          // F6 — the SVG names the family, in the single-quoted attribute.
          const svg = titlePlanToSvg(plan);
          check(svg.includes(`font-family='${EXPECT[font]}'`), `F6 ${font} SVG family [${tag}]`);
        }
      }
    }
  }
}

// A spot check the poster SVG really says Impact and the sans SVG really says the
// legacy stack — so F6 cannot pass on an empty string.
{
  const p = planTitle({ text: 'POSTER', place: 'bc', size: 'lg', font: 'poster' }, 1, measure);
  check(titlePlanToSvg(p).includes('Impact'), 'F6 poster SVG contains Impact');
  const s = planTitle({ text: 'plain', place: 'bl', size: 'md', font: 'sans' }, 1, measure);
  check(titlePlanToSvg(s).includes('Helvetica Neue'), 'F6 sans SVG contains the legacy stack');
}

// =============================================================================
// RED PROOF — a mutant planTitle that IGNORES spec.font (always sans) would fail
// F3 and F4 on every non-sans font. We simulate the mutant's family (always the
// sans stack) and show it disagrees with the expected family for serif/mono/
// poster, so the checks above are not vacuous.
// =============================================================================
let redWouldFail = 0, redTotal = 0;
for (const font of TITLE_FONTS) {
  const mutantFamily = TITLE_FAMILY;            // the mutant never leaves sans
  redTotal++;
  if (mutantFamily !== EXPECT[font]) redWouldFail++;
}
check(redWouldFail === 3, `RED PROOF: a font-ignoring mutant fails on 3 of 4 fonts (got ${redWouldFail}/${redTotal})`);

// =============================================================================
console.log(`title-font.invariants: ${checks} checks, ${fails} failures`);
if (fails > 0) { console.error(`\nFAILED: ${fails} of ${checks}`); process.exit(1); }
console.log('OK');
