/**
 * Invariant sweep for THE POST — the exported SVG as the project file.
 *
 * Run: node tests/unit/svgProject.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so it
 * proves the shipped `svgProject.projectMetadata` / `readProject` /
 * `readImageSources` — not a re-implementation of them.
 *
 * THE INVARIANT THAT MATTERS — THE CAPTION CANNOT BREAK THE FILE:
 *
 *   The manifest used to ride in `<!-- JSON_MANIFEST: {...} -->`, and the title
 *   is free text that lands in it verbatim. XML forbids `--` anywhere inside a
 *   comment and `-->` closes one early, so a caption as ordinary as
 *   "well-shot -- or so I thought" produced an SVG that is not well-formed XML:
 *   not a degraded picture, a parse error. Arm B below MEASURES that on the old
 *   construction rather than asserting it, and then requires the new one to be
 *   clean on the identical input.
 *
 * The second invariant is POOL FIDELITY. `arrangeBag` deals from the pool's
 * ORDER and its LENGTH, so a pool that comes back short, reordered, or with one
 * analysis rounded is a different collage wearing the same code. Every arm here
 * demands exact equality, and every malformed input is required to REFUSE
 * rather than return the part it could read.
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
  projectMetadata, readProject, readImageSources, metaForAsset, srcIdAttr,
  escapeXmlText, unescapeXmlText, PROJECT_EL, PROJECT_ID, SRC_ID_ATTR,
} = await load('src/lib/svgProject.ts', 'svgproject');

let failures = 0;
let checks = 0;
const check = (cond, msg) => {
  checks++;
  if (!cond) { failures++; console.error(`  FAIL  ${msg}`); }
};

const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const deepEq = (a, b, path = '$') => {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null) return a === b;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  if (typeof a !== 'object') return Object.is(a, b);
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  for (const k of ka) if (!deepEq(a[k], b[k], `${path}.${k}`)) return false;
  return true;
};

// -----------------------------------------------------------------------------
// The hostile strings. Every one is something a person could plausibly type into
// the caption box, plus the ones that specifically attack the container.
// -----------------------------------------------------------------------------
const HOSTILE = [
  'plain caption',
  'well-shot -- or so I thought',        // `--`  : illegal inside an XML comment
  'end of the road --> next',            // `-->` : closes a comment early
  'a < b & b > c',                       // the three characters text must escape
  '"quoted" & \'single\'',
  '<script>alert(1)</script>',
  '<!-- nested comment -->',
  ']]> and <![CDATA[',
  'emoji 🎬🔥 and ümlauts',
  'newline\nand\ttab',
  '<metadata id="collage-project">fake</metadata>',
  '\\u003c escaped-looking',
  '&amp; already an entity',
  '-'.repeat(40),
];

const LOOKS = ['none', 'punch', 'faded', 'mono', 'noir', 'warm', 'cool', 'bleach'];
const TWISTS = ['none', 'tilt', 'scatter', 'pinwheel', 'cascade'];
const MODES = ['minimal', 'balanced', 'shards', 'voronoi', 'phyllotaxis', 'droste'];

const stateFor = (rnd, title) => ({
  version: '1.0',
  mode: rnd() < 0.5 ? 'simple' : 'advanced',
  layout: {
    mode: MODES[Math.floor(rnd() * MODES.length)],
    primitive: 'rect',
    count: 1 + Math.floor(rnd() * 40),
    seed: Math.floor(rnd() * 0xffffff),
    aspect: [1, 1.7778, 0.5625, 1.3333][Math.floor(rnd() * 4)],
    gutter: rnd() * 0.05,
    entropy: rnd(),
    arrangement: 'natural',
    focus: 'auto',
    twist: TWISTS[Math.floor(rnd() * TWISTS.length)],
  },
  style: {
    background: `#${Math.floor(rnd() * 0xffffff).toString(16).padStart(6, '0')}`,
    look: LOOKS[Math.floor(rnd() * LOOKS.length)],
  },
  ...(title === null ? {} : { title: { text: title, place: 'bl', size: 'md' } }),
});

const poolFor = (rnd, n, idSalt = '') =>
  Array.from({ length: n }, (_, i) => ({
    id: `img${idSalt}-${i}-${Math.floor(rnd() * 1e9)}`,
    originalName: `photo ${i} & "friends" <2026>.jpg`,
    analysis: {
      face: rnd() < 0.4 ? { x: rnd(), y: rnd() } : null,
      energy: { x: rnd(), y: rnd() },
      color: {
        r: Math.floor(rnd() * 256), g: Math.floor(rnd() * 256), b: Math.floor(rnd() * 256),
        h: rnd() * 360, s: rnd(), l: rnd(),
      },
    },
  }));

/** The document skeleton the manifest actually ships inside. */
const docWith = (metaBlock, images = []) => {
  let s = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n`;
  s += `<svg width="1000px" height="1000px" viewBox="0 0 1000 1000" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n`;
  s += `  <desc>Smart Crop GenArt Export</desc>\n`;
  s += metaBlock;
  s += `  <defs>\n    <clipPath id="clip-0"><path d="M 0 0 L 1 1 Z" /></clipPath>\n  </defs>\n`;
  s += `  <g id="CollageLayer">\n`;
  for (const im of images) {
    s += `    <g clip-path="url(#clip-0)">\n      <g>\n        <image${srcIdAttr(im.id)}\n          xlink:href="${im.href}"\n          x="0.00"\n          y="0.00"\n          width="10.00"\n          height="10.00"\n          preserveAspectRatio="none"\n        />\n      </g>\n    </g>\n`;
  }
  s += `  </g>\n</svg>`;
  return s;
};

// =============================================================================
// A. ROUND TRIP — state and pool come back byte-exact, across seeds x captions
// =============================================================================
console.log('A. round trip: manifest -> document -> manifest');
{
  let cases = 0;
  for (let seed = 0; seed < 60; seed++) {
    const rnd = rngOf(seed * 7919 + 13);
    for (const title of HOSTILE) {
      const state = stateFor(rnd, title);
      const pool = poolFor(rnd, 1 + Math.floor(rnd() * 6));
      const metas = pool.map(metaForAsset);

      const doc = docWith(projectMetadata(state, metas));
      const back = readProject(doc);
      cases++;

      if (!back) { check(false, `seed ${seed} / "${title.slice(0, 24)}": readProject returned null`); continue; }
      check(deepEq(back.state, state), `seed ${seed} / "${title.slice(0, 24)}": state survived`);
      check(deepEq(back.images, metas), `seed ${seed} / "${title.slice(0, 24)}": pool survived exactly`);
    }
  }
  // Untitled projects must round-trip too — `title` absent, not `undefined`.
  for (let seed = 0; seed < 20; seed++) {
    const rnd = rngOf(seed + 991);
    const state = stateFor(rnd, null);
    const metas = poolFor(rnd, 3).map(metaForAsset);
    const back = readProject(docWith(projectMetadata(state, metas)));
    check(!!back && deepEq(back.state, state), `untitled seed ${seed}: state survived`);
    cases++;
  }
  console.log(`   ${cases} round trips`);
}

// =============================================================================
// B. THE DEFECT THAT MOVED THE MANIFEST — measured on the old construction
// =============================================================================
console.log('B. the XML-comment container, measured');
{
  let brokenOld = 0;
  for (const title of HOSTILE) {
    const rnd = rngOf(4242);
    const state = stateFor(rnd, title);
    const metas = poolFor(rnd, 2).map(metaForAsset);

    // The OLD construction, verbatim: vectorExport.ts before this change.
    //
    // XML 1.0 §2.5:  Comment ::= '<!--' ((Char - '-') | ('-' (Char - '-')))* '-->'
    // so the body may not CONTAIN `--` and may not END in `-`. A lone `>` is
    // perfectly legal inside a comment — an earlier draft of this arm counted
    // those too and reported 8/14 instead of the true figure. The number is the
    // claim, so it gets the exact rule, not a conservative-looking superset.
    const oldComment = `<!-- JSON_MANIFEST: ${JSON.stringify(state)} -->`;
    const body = oldComment.slice(4, -3);          // between `<!--` and `-->`
    const oldIsIllegalXml = body.includes('--') || body.endsWith('-');
    if (oldIsIllegalXml) brokenOld++;

    // `-->` is the worse half: it does not merely make the comment illegal, it
    // ENDS it, leaving the tail of the manifest in the document as bare text
    // before the root element.
    if (title.includes('-->')) {
      check(oldComment.indexOf('-->') < oldComment.length - 3,
        `"${title.slice(0, 24)}": the old comment is closed early by the caption`);
    }

    // The NEW one, on the identical input, must be clean text content: after
    // every entity is removed, nothing that needs escaping may remain.
    const block = projectMetadata(state, metas);
    const gt = block.indexOf('>');
    const close = block.indexOf(`</${PROJECT_EL}>`);
    const payload = block.slice(gt + 1, close);
    const stripped = payload.replace(/&(amp|lt|gt|quot|apos);/g, '');
    check(!stripped.includes('<'), `"${title.slice(0, 24)}": no raw < in metadata text`);
    check(!stripped.includes('>'), `"${title.slice(0, 24)}": no raw > in metadata text`);
    check(!stripped.includes('&'), `"${title.slice(0, 24)}": no stray & in metadata text`);
    check(!payload.includes(`</${PROJECT_EL}>`), `"${title.slice(0, 24)}": payload cannot close its own element`);

    // And it must still be the same project.
    const back = readProject(docWith(block));
    check(!!back && deepEq(back.state, state), `"${title.slice(0, 24)}": reads back through the new container`);
  }
  check(brokenOld >= 3, `the old comment container is broken by real captions (measured ${brokenOld}/${HOSTILE.length})`);
  console.log(`   ${brokenOld}/${HOSTILE.length} captions produced an ILL-FORMED XML comment under the old construction`);
}

// =============================================================================
// C. ESCAPE / UNESCAPE are exact inverses, including on already-escaped text
// =============================================================================
console.log('C. escaping is an exact inverse');
{
  const corpus = [...HOSTILE, '&amp;lt;', '&&&', '<<<', '>>>', '', '&lt;&gt;&amp;'];
  for (const s of corpus) {
    check(unescapeXmlText(escapeXmlText(s)) === s, `inverse holds for ${JSON.stringify(s.slice(0, 28))}`);
  }
  // The ordering trap: escaping `<` before `&` would double-escape the ampersand.
  check(escapeXmlText('<') === '&lt;', 'escape(<) is &lt;');
  check(escapeXmlText('&lt;') === '&amp;lt;', 'escape(&lt;) is &amp;lt; — & goes first');
  check(unescapeXmlText('&amp;lt;') === '&lt;', 'unescape(&amp;lt;) is &lt; — &amp; goes last');
}

// =============================================================================
// D. IMAGE RECOVERY — every id written is found, with its exact href
// =============================================================================
console.log('D. image source recovery');
{
  for (let seed = 0; seed < 40; seed++) {
    const rnd = rngOf(seed * 31 + 7);
    const n = 1 + Math.floor(rnd() * 8);
    const pool = poolFor(rnd, n, seed % 3 === 0 ? ' &"<x>"' : '');
    const withHref = pool.map((p, i) => ({
      ...p,
      href: `data:image/png;base64,${'A'.repeat(64 + i * 17)}=`,
    }));
    const doc = docWith(projectMetadata(stateFor(rnd, 'x'), pool.map(metaForAsset)), withHref);
    const found = readImageSources(doc);

    check(found.size === n, `seed ${seed}: found all ${n} sources (got ${found.size})`);
    for (const im of withHref) {
      check(found.get(im.id) === im.href, `seed ${seed}: href exact for ${im.id}`);
    }
  }

  // A source drawn into two fragments is written twice and resolves to one entry.
  const rnd = rngOf(5150);
  const one = poolFor(rnd, 1)[0];
  const href = 'data:image/jpeg;base64,ZZZZ=';
  const dup = docWith(projectMetadata(stateFor(rnd, 'x'), [metaForAsset(one)]),
    [{ ...one, href }, { ...one, href }]);
  const dupFound = readImageSources(dup);
  check(dupFound.size === 1 && dupFound.get(one.id) === href, 'a repeated source collapses to one entry');

  // A big href must not be quadratic or wrong. 4 MB in one attribute.
  const big = { ...one, href: `data:image/png;base64,${'Q'.repeat(4 * 1024 * 1024)}=` };
  const t0 = Date.now();
  const bigFound = readImageSources(docWith(projectMetadata(stateFor(rnd, 'x'), [metaForAsset(one)]), [big]));
  const ms = Date.now() - t0;
  check(bigFound.get(one.id) === big.href, 'a 4 MB data URI is recovered exactly');
  check(ms < 3000, `a 4 MB data URI scans in linear time (${ms} ms)`);
  console.log(`   4 MB href scanned in ${ms} ms`);
}

// =============================================================================
// E. REFUSALS — malformed input returns null, and never throws
// =============================================================================
console.log('E. refusals');
{
  const rnd = rngOf(31337);
  const state = stateFor(rnd, 'ok');
  const metas = poolFor(rnd, 3).map(metaForAsset);
  const good = docWith(projectMetadata(state, metas));

  const bad = [
    ['empty string', ''],
    ['not svg at all', 'hello world'],
    ['svg with no manifest', docWith('')],
    ['legacy comment form', `<!-- JSON_MANIFEST: ${JSON.stringify(state)} -->\n<svg></svg>`],
    ['truncated mid-manifest', good.slice(0, good.indexOf(`</${PROJECT_EL}>`) - 20)],
    ['manifest is not JSON', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">not json at all</${PROJECT_EL}>\n`)],
    ['manifest is an array', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">[1,2,3]</${PROJECT_EL}>\n`)],
    ['manifest is null', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">null</${PROJECT_EL}>\n`)],
    ['no state', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">{"format":1,"images":[]}</${PROJECT_EL}>\n`)],
    ['state without layout', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">{"format":1,"state":{"version":"1.0"},"images":[]}</${PROJECT_EL}>\n`)],
    ['images not an array', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">{"format":1,"state":{"layout":{}},"images":{}}</${PROJECT_EL}>\n`)],
    ['an image with no id', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">{"format":1,"state":{"layout":{}},"images":[{"originalName":"a.png"}]}</${PROJECT_EL}>\n`)],
    ['an image with an empty id', docWith(`  <${PROJECT_EL} id="${PROJECT_ID}">{"format":1,"state":{"layout":{}},"images":[{"id":""}]}</${PROJECT_EL}>\n`)],
    ['someone else\'s metadata', docWith(`  <${PROJECT_EL} id="other-tool">{"state":{"layout":{}},"images":[]}</${PROJECT_EL}>\n`)],
  ];

  for (const [label, text] of bad) {
    let threw = false, got;
    try { got = readProject(text); } catch (e) { threw = true; }
    check(!threw, `${label}: does not throw`);
    check(got === null, `${label}: refused (returned null)`);
  }

  // Non-strings must not throw either — this runs on whatever a file handed us.
  for (const junk of [null, undefined, 42, {}, []]) {
    let threw = false;
    try { readProject(junk); readImageSources(junk); } catch { threw = true; }
    check(!threw, `junk input ${JSON.stringify(junk) ?? 'undefined'}: does not throw`);
  }

  // The good document must still pass, or the refusals above prove nothing.
  const back = readProject(good);
  check(!!back && deepEq(back.images, metas), 'the control document still opens');
}

// =============================================================================
// F. NO STATE, NO MANIFEST — an export without one is unchanged
// =============================================================================
console.log('F. absent state emits nothing');
{
  check(projectMetadata(null, []) === '', 'null state emits an empty string');
  check(projectMetadata(undefined, undefined) === '', 'undefined state emits an empty string');
  check(srcIdAttr('') === '', 'an empty id emits no attribute');
  check(srcIdAttr(undefined) === '', 'a missing id emits no attribute');
  check(srcIdAttr('a"b') === ` ${SRC_ID_ATTR}="a&quot;b"`, 'an id with a quote is attribute-escaped');
}

console.log('');
if (failures) {
  console.error(`FAILED — ${failures} of ${checks} checks`);
  process.exit(1);
}
console.log(`PASS — ${checks} checks`);
