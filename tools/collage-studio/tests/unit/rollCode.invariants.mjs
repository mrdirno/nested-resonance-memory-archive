/**
 * Invariant sweep for THE COMPOSITION CODE — the roll you can keep and send.
 *
 * Run: node tests/unit/rollCode.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * it proves the shipped `rollCode.encodeState` / `decodeState` and the shipped
 * `diceRoll.encodeRoll` / `decodeRoll` / `snapRoll` — not a re-implementation.
 *
 * THE INVARIANT THAT MATTERS:
 *
 *   For every composition the UI can reach,  decodeState(encodeState(s)) === s.
 *   Exactly. Not "within a slider detent".
 *
 *   A share code is the one feature where "close enough" is indistinguishable
 *   from broken: you send somebody a code precisely because you want THAT
 *   picture, and a frame shape two thousandths off or a background that fell
 *   back to the nearest roster colour is a different picture arriving under
 *   your name. So the assertion is hard equality on every field.
 *
 * WHY THE REACHABLE SET IS BUILT HERE FROM THE UI'S OWN NUMBERS
 *
 *   SCAR (carried in COLLAGE_EVOLUTION.md): "a test that defines the boundary
 *   the way the code defines it cannot see the boundary being wrong." If this
 *   file asked the codec which frame shapes exist, it would agree with the codec
 *   by construction and could never catch the codec disagreeing with the UI —
 *   which is the exact bug this cycle found (four ratio chips, two of them off
 *   the roster the codec indexes into). So the reachable set below is stated in
 *   the UI's terms: the slider MIN/MAX/STEP attributes, the density chips, the
 *   shape roster, and the frame ratios by their NAMES (2:3, 1:1, 16:9, 9:16),
 *   with an independent check that each named ratio is really that ratio.
 *
 * THE RED PROOF at the end runs the PREVIOUS encoder against the same set and
 * counts what it got wrong, so "this fixes something" is a number rather than a
 * claim.
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
  encodeState, decodeState, codeFromUrl, rollFromState, stateFromRoll,
  zoomForDensity, densityForZoom,
} = await load('src/lib/rollCode.ts', 'rollcode');
const { encodeRoll, decodeRoll, rollDice, snapRoll, ASPECT_ROSTER, PRIMITIVE_ORDER, BACKGROUND_SWATCHES } =
  await load('src/lib/diceRoll.ts', 'dice');
const { ARRANGEMENT_IDS, FOCUS_IDS, TWIST_IDS } = await load('src/lib/composition.ts', 'composition');
const { GENERATORS } = await load('src/engine/geom/generators/index.ts', 'generators');

let checks = 0, failures = 0;
const check = (cond, msg) => {
  checks++;
  if (!cond) { failures++; if (failures <= 25) console.error(`  ✗ ${msg}`); }
};

const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

// =============================================================================
// THE REACHABLE SET — stated in the UI's terms, not the codec's.
// =============================================================================

/** SimpleControls: the two classic modes + every generator. The three retired
 *  ids still arrive from saved projects, so they are reachable too. */
const LAYOUTS = [
  'minimal', 'balanced', 'complex', 'field', 'stencil',
  ...GENERATORS.map((g) => g.id),
];

/** SimpleControls SHAPES — retyped here on purpose (see the header). */
const SHAPES = ['rect', 'tri', 'circle', 'octagon', 'random'];

/** SimpleControls density chips: `{[1, 2, 3, 4].map(...)}`. */
const DENSITIES = [1, 2, 3, 4];

/** AdvancedControls frame chips, BY NAME. The numbers come from the roster the
 *  codec indexes; that the roster really holds these ratios is checked below. */
const NAMED_RATIOS = [
  { label: '2:3',  nominal: 2 / 3,   v: ASPECT_ROSTER[1] },
  { label: '1:1',  nominal: 1,       v: ASPECT_ROSTER[0] },
  { label: '16:9', nominal: 16 / 9,  v: ASPECT_ROSTER[5] },
  { label: '9:16', nominal: 9 / 16,  v: ASPECT_ROSTER[6] },
];

/** `<input type="range" min="0" max="1" step="0.01">` — the chaos slider. */
const ENTROPY_STEPS = Array.from({ length: 101 }, (_, k) => k / 100);
/** `<input type="range" min="0" max="0.05" step="0.001">` — the padding slider. */
const GUTTER_STEPS = Array.from({ length: 51 }, (_, k) => k / 1000);

/** Every background the app can hold: two fixed swatches, the eight roster
 *  colours, and anything the three ADAPTIVE swatches derive from a photograph. */
const FIXED_BGS = ['#050505', '#f5f5f5', ...Object.values(BACKGROUND_SWATCHES)];
const hexOf = (r, g, b) =>
  `#${[r, g, b].map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('')}`;

const FIELDS = ['layoutMode', 'primitive', 'count', 'density', 'entropy', 'aspect',
                'gutter', 'bgColor', 'seed', 'arrangement', 'focus', 'twist', 'shuffle',
                'countOwned'];

const sameState = (a, b) => FIELDS.every((k) => Object.is(a[k], b[k]));
const diffOf = (a, b) => FIELDS.filter((k) => !Object.is(a[k], b[k]))
  .map((k) => `${k}: ${JSON.stringify(a[k])} -> ${JSON.stringify(b[k])}`).join(', ');

const pick = (arr, rnd) => arr[Math.floor(rnd() * arr.length) % arr.length];

/** One composition the app could actually be in. */
const reachableState = (rnd) => ({
  layoutMode: pick(LAYOUTS, rnd),
  primitive: pick(SHAPES, rnd),
  // The count slider bottoms out at 1 and the codec floors at 2; the app's own
  // "one fragment per source" rule never goes below 2 sources in practice.
  // The stepper's own floor is 1 — `Math.max(1, prev + step)` — so 1 is a
  // composition somebody can ask for, and its code has to say 1.
  count: 1 + Math.floor(rnd() * 400),
  density: pick(DENSITIES, rnd),
  entropy: pick(ENTROPY_STEPS, rnd),
  aspect: pick(NAMED_RATIOS, rnd).v,
  gutter: pick(GUTTER_STEPS, rnd),
  bgColor: rnd() < 0.5
    ? pick(FIXED_BGS, rnd)
    : hexOf(rnd() * 255, rnd() * 255, rnd() * 255),
  // Both seed regimes the app produces: `Date.now()` at boot, and the roll's
  // own 24-bit draw.
  seed: rnd() < 0.5 ? Math.floor(rnd() * 0xffffff) : 1_700_000_000_000 + Math.floor(rnd() * 1e11),
  arrangement: pick(ARRANGEMENT_IDS, rnd),
  focus: pick(FOCUS_IDS, rnd),
  twist: pick(TWIST_IDS, rnd),
  shuffle: rnd() < 0.55 ? 0 : Math.floor(rnd() * 500),
  // Both sides of the one bit that decides whether a recipient's pool may
  // override the count: a decision, or the source total the app derived.
  countOwned: rnd() < 0.5,
});

// =============================================================================
console.log('0. the named frame ratios really are those ratios');
{
  for (const r of NAMED_RATIOS) {
    check(typeof r.v === 'number' && Math.abs(r.v - r.nominal) < 0.001,
      `the chip labelled ${r.label} carries ${r.v}, which is not ${r.label} (${r.nominal.toFixed(5)})`);
  }
  check(new Set(NAMED_RATIOS.map((r) => r.v)).size === NAMED_RATIOS.length,
    'two frame chips carry the same number');
  check(PRIMITIVE_ORDER.length === SHAPES.length && SHAPES.every((s, i) => PRIMITIVE_ORDER[i] === s),
    `the codec's shape order ${JSON.stringify(PRIMITIVE_ORDER)} is not the UI's ${JSON.stringify(SHAPES)}`);
}

// =============================================================================
console.log('0b. EVERY FIELD STILL FITS ITS WIDTH — the slice-shift guard');
{
  /**
   * A fixed-width field that overflows does not clip; it lengthens its group and
   * shifts every later slice by a character, and the code then decodes CLEANLY
   * into a different composition. `count` at 36^3 did exactly that before this
   * cycle clamped it. The clamp stops corruption; THIS stops the clamp from
   * quietly becoming the thing that loses your composition, by failing the
   * moment a roster grows past the field that carries it.
   */
  const cap = (w) => 36 ** w - 1;
  const fields = [
    ['layout roster', LAYOUTS.length - 1, 2],
    ['aspect roster', ASPECT_ROSTER.length - 1, 1],
    ['background roster', Object.keys(BACKGROUND_SWATCHES).length - 1, 1],
    ['arrangements', ARRANGEMENT_IDS.length - 1, 1],
    ['focus modes', FOCUS_IDS.length - 1, 1],
    ['twist modes', TWIST_IDS.length - 1, 1],
    ['fragment shapes', PRIMITIVE_ORDER.length - 1, 1],
    ['chaos (x100)', 100, 2],
    ['padding (x2000, max 0.05)', 100, 2],
    ['zoom (x100, max 4)', 400, 2],
    ['background rgb', 0xffffff, 5],
  ];
  for (const [what, max, width] of fields) {
    check(max <= cap(width),
      `${what} needs ${max} but its ${width}-character field holds ${cap(width)} — ` +
      'every code minted from here would shift its own slices');
    // And a HEADROOM warning long before it breaks, because the failure is silent
    // in production and only loud here.
    if (max > cap(width) * 0.8) {
      console.warn(`   ! ${what} is at ${((max / cap(width)) * 100).toFixed(0)}% of its field`);
    }
  }
  // The count clamp is a real ceiling, so it is pinned from BOTH sides: the
  // largest allowed count round-trips, and one more does not silently become
  // something else — it saturates.
  const big = { ...reachableState(rngOf(1)), count: 36 ** 3 - 1 };
  check(decodeState(encodeState(big)).count === 36 ** 3 - 1, 'the largest allowed count did not survive');
  const over = { ...big, count: 36 ** 3 };
  const overCode = encodeState(over);
  check(overCode.split('-')[0].length === 7,
    `a count past the ceiling lengthened its group to ${overCode.split('-')[0].length} characters`);
  check(decodeState(overCode).count === 36 ** 3 - 1,
    'a count past the ceiling did not saturate at the ceiling');
}

// =============================================================================
console.log('1. THE PROMISE — every reachable composition survives its own code, exactly');
const SAMPLES = 60_000;
{
  let worst = null;
  for (let i = 0; i < SAMPLES; i++) {
    const rnd = rngOf(i * 2654435761 + 7);
    const s = reachableState(rnd);
    const code = encodeState(s);
    const back = decodeState(code);
    check(back !== null, `sample ${i}: its own code did not decode (${code})`);
    if (!back) continue;
    const ok = sameState(s, back);
    if (!ok && !worst) worst = `sample ${i} (${code}): ${diffOf(s, back)}`;
    check(ok, `sample ${i}: ${diffOf(s, back)} — code ${code}`);
  }
  if (worst) console.error(`  first divergence: ${worst}`);
}

// =============================================================================
console.log('2. the code is IDEMPOTENT — a code you copy is the code you get back');
{
  for (let i = 0; i < 8000; i++) {
    const s = reachableState(rngOf(i * 40503 + 11));
    const c1 = encodeState(s);
    const c2 = encodeState(decodeState(c1));
    check(c1 === c2, `sample ${i}: encode(decode(encode(s))) drifted ${c1} -> ${c2}`);
  }
}

// =============================================================================
console.log('3. NO FIELD IS SILENTLY DROPPED — changing any one of them changes the code');
{
  // This is the assertion that catches an un-encoded field. It is stated over
  // the FIELD LIST, so a field added to the state later and forgotten in the
  // codec fails here without anybody remembering to add a case.
  const alternatives = {
    layoutMode: LAYOUTS, primitive: SHAPES, density: DENSITIES,
    entropy: ENTROPY_STEPS, aspect: NAMED_RATIOS.map((r) => r.v),
    gutter: GUTTER_STEPS, bgColor: FIXED_BGS,
    arrangement: ARRANGEMENT_IDS, focus: FOCUS_IDS, twist: TWIST_IDS,
    count: [1, 2, 3, 17, 60, 400], seed: [0, 1, 99, 123456, 1_700_000_000_000],
    shuffle: [0, 1, 2, 77, 499], countOwned: [true, false],
  };
  for (let i = 0; i < 900; i++) {
    const rnd = rngOf(i * 7919 + 5);
    const base = reachableState(rnd);
    const baseCode = encodeState(base);
    for (const field of FIELDS) {
      const other = alternatives[field].find((v) => !Object.is(v, base[field]));
      if (other === undefined) continue;
      const moved = { ...base, [field]: other };
      check(encodeState(moved) !== baseCode,
        `moving ${field} from ${JSON.stringify(base[field])} to ${JSON.stringify(other)} left the code unchanged (${baseCode})`);
    }
  }
}

// =============================================================================
console.log('4. rollDice lands ON the grid, so a fresh roll is exactly its own code');
{
  for (let seed = 0; seed < 4000; seed++) {
    const r = rollDice({ rnd: rngOf(seed * 13 + 1), hasVideo: seed % 3 === 0 });
    const back = decodeRoll(encodeRoll(r));
    check(back !== null, `roll ${seed}: did not decode`);
    if (!back) continue;
    for (const k of ['layout', 'primitive', 'count', 'entropy', 'aspect', 'gutter', 'zoom',
                     'bg', 'seed', 'arrangement', 'focus', 'twist', 'countOwned']) {
      check(Object.is(r[k], back[k]),
        `roll ${seed}: ${k} ${JSON.stringify(r[k])} -> ${JSON.stringify(back[k])}`);
    }
    check(Object.is(snapRoll(r).entropy, r.entropy) && Object.is(snapRoll(r).gutter, r.gutter),
      `roll ${seed}: rollDice returned a roll that is not on the grid`);
  }
}

// =============================================================================
console.log('5. density <-> zoom is a bijection on the chips the UI offers');
{
  for (const d of DENSITIES) {
    check(densityForZoom(zoomForDensity(d)) === d, `density ${d} did not survive the zoom derivation`);
  }
  for (let i = 0; i < 2000; i++) {
    const rnd = rngOf(i * 31 + 3);
    const s = reachableState(rnd);
    const r = rollFromState(s);
    check(stateFromRoll(r, s.shuffle).density === s.density,
      `density ${s.density} did not survive the Roll (zoom ${r.zoom})`);
  }
}

// =============================================================================
console.log('6. legacy codes still open, as the composition they described');
{
  const modern = encodeState(reachableState(rngOf(4242)));
  const [a, b, c] = modern.split('-');
  const cases = [
    ['pre-composition (6)', 6, { arrangement: 'natural', focus: 'auto', twist: 'none', primitive: 'rect', countOwned: false }],
    ['composition-era (8)', 8, { twist: 'none', primitive: 'rect', countOwned: false }],
    ['twist-era (9)', 9, { primitive: 'rect', countOwned: false }],
    ['shape-era (10)', 10, { countOwned: false }],
    ['colour-era (15)', 15, { countOwned: false }],
  ];
  for (const [name, len, expect] of cases) {
    const legacy = `${a}-${b.slice(0, len)}-${c}`;
    const d = decodeState(legacy);
    check(d !== null, `a ${name} code no longer decodes (${legacy})`);
    if (!d) continue;
    for (const [k, v] of Object.entries(expect)) {
      check(d[k] === v, `a ${name} code opened with ${k}='${d[k]}', it described '${v}'`);
    }
    const full = decodeState(modern);
    check(d.layoutMode === full.layoutMode && d.count === full.count && d.seed === full.seed
      && d.entropy === full.entropy,
      `truncating the middle group of a ${name} code moved a field that is not in it`);
  }
  // A background off every roster survives only in a modern code; a truncated
  // one must degrade to a roster colour, never to nothing.
  const custom = { ...reachableState(rngOf(99)), bgColor: '#7a3d16' };
  check(decodeState(encodeState(custom)).bgColor === '#7a3d16', 'an off-roster background did not survive');
  // And it must degrade to the NEAREST roster colour, which is what the codec's
  // docstring claims — stated here independently, by measuring the distance
  // rather than by asking the codec which one it picked.
  const bits = (h) => parseInt(h.slice(1), 16);
  const chDist = (a, b) => Math.abs((a >> 16) - (b >> 16))
    + Math.abs(((a >> 8) & 255) - ((b >> 8) & 255)) + Math.abs((a & 255) - (b & 255));
  for (const probe of ['#7a3d16', '#ffffff', '#000000', '#f2ece1', '#0d1330', '#20ff20']) {
    const st = { ...reachableState(rngOf(123)), bgColor: probe };
    const [ta, tb, tc] = encodeState(st).split('-');
    const degraded = decodeState(`${ta}-${tb.slice(0, 10)}-${tc}`);
    check(degraded !== null && /^#[0-9a-f]{6}$/.test(degraded.bgColor),
      `a truncated code produced no background at all for ${probe}`);
    if (!degraded) continue;
    const roster = Object.values(BACKGROUND_SWATCHES).map(bits);
    const best = Math.min(...roster.map((r) => chDist(r, bits(probe))));
    check(chDist(bits(degraded.bgColor), bits(probe)) === best,
      `${probe} degraded to ${degraded.bgColor}, which is not the nearest roster colour`);
  }
}

// =============================================================================
console.log('7. a colour spelled `rgb(...)` reads as the same colour (old saved projects)');
{
  for (let i = 0; i < 400; i++) {
    const rnd = rngOf(i * 977 + 13);
    const [r, g, b] = [rnd(), rnd(), rnd()].map((v) => Math.floor(v * 256));
    const s = { ...reachableState(rnd), bgColor: `rgb(${r},${g},${b})` };
    const back = decodeState(encodeState(s));
    check(back !== null && back.bgColor === hexOf(r, g, b),
      `rgb(${r},${g},${b}) came back as ${back && back.bgColor}`);
  }
}

// =============================================================================
console.log('8. HOSTILE INPUT — a refusal, never half a composition, never a throw');
{
  const good = encodeState(reachableState(rngOf(7)));
  const [ga, gb, gc] = good.split('-');
  const hostile = [
    '', ' ', '-', '--', '---', 'nonsense', 'not-a-code', 'a-b-c',
    good.slice(0, 5), good.slice(1), `${good}-`, `-${good}`, `${good}--1`,
    `${ga}-${gb}`, `${ga}-${gb}-${gc}-1-2`, `${ga}-${gb.slice(0, 5)}-${gc}`,
    `${ga.slice(0, 6)}-${gb}-${gc}`, `${ga}-${gb}-`,
    'ZZZZZZZ-ZZZZZZZZZZZZZZZ-ZZZZZZZZ', '!!!!!!!-!!!!!!-!!!!', '🎲🎲🎲-🎲🎲🎲-🎲',
    `${ga}-${gb}-${'z'.repeat(300)}`, `${'9'.repeat(400)}-${gb}-${gc}`,
    `${ga}-${gb}-${gc}-${'z'.repeat(9)}`, `${ga}-${gb}-${gc}-!!`,
    ' - - ', `${ga}​-${gb}-${gc}`,
    null, undefined, 42, {}, [],
  ];
  for (const h of hostile) {
    let out, threw = false;
    try { out = decodeState(h); } catch { threw = true; }
    check(!threw, `decodeState(${JSON.stringify(h)}) threw`);
    if (out !== null && out !== undefined) {
      // If it decoded at all it must be a WHOLE composition, not a partial one.
      check(FIELDS.every((k) => out[k] !== undefined && out[k] !== null
        && (typeof out[k] !== 'number' || Number.isFinite(out[k]))),
        `decodeState(${JSON.stringify(h)}) returned a half-composition: ${JSON.stringify(out)}`);
    }
  }
  // Whitespace and case are the two things a chat client will do to a code.
  const s = reachableState(rngOf(31));
  const code = encodeState(s);
  for (const mangled of [` ${code} `, code.toLowerCase(), code.split('').join(''), `${code}\n`,
                         code.replace(/-/g, ' - ')]) {
    const back = decodeState(mangled);
    check(back !== null && sameState(s, back), `a code survived being written "${mangled}"? ${back && diffOf(s, back)}`);
  }
}

// =============================================================================
console.log('8b. THE CHECKSUM — a mangled code is REFUSED, not opened as somebody else');
{
  /**
   * The reason this character exists: almost every mangling of a valid code used
   * to be another VALID code. The seed is the last field of the last group and
   * the only one free to vary in length, so lopping characters off the end just
   * read as a smaller number and the code opened, cleanly, as a different
   * collage. Measured below both ways round.
   */
  let openedAsSomethingElse = 0, refused = 0, total = 0;
  for (let i = 0; i < 3000; i++) {
    const st = reachableState(rngOf(i * 61 + 9));
    const code = encodeState(st);
    const [ga, gb, gc] = code.split('-');
    const manglings = [
      code.slice(0, -1),                                    // one character lost off the tail
      code.slice(0, -4),                                    // a chat client ate the end
      `${ga}-${gb}-${gc.slice(1)}`,                         // the seed lost its head
      gc.length > 1 ? `${ga}-${gb}-${gc[1]}${gc[0]}${gc.slice(2)}` : null,  // transposed, retyped
      `${ga}-${gb.slice(0, 3)}Z${gb.slice(4)}-${gc}`,       // one character corrupted
      `${ga.slice(0, 2)}Z${ga.slice(3)}-${gb}-${gc}`,       // ...in the first group
    ].filter(Boolean).filter((m) => m !== code);
    for (const m of manglings) {
      total++;
      const back = decodeState(m);
      if (back === null) refused++;
      else if (!sameState(st, back)) openedAsSomethingElse++;
    }
  }
  const caught = ((refused / total) * 100).toFixed(1);
  console.log(`   ${refused}/${total} manglings refused (${caught}%), ${openedAsSomethingElse} still opened as a different collage`);
  // Two base-36 characters is an accident detector, not a signature: ~1/1296 of
  // manglings survive by chance. Pinned from BOTH sides, so a checksum that
  // stopped working and one that started refusing everything both fail here —
  // and the floor is set well above the 88.9% the first (mod-36, weighted-sum)
  // cut actually managed, so a regression to it is caught rather than tolerated.
  check(refused / total > 0.985, `the checksum only caught ${caught}% of manglings`);
  check(openedAsSomethingElse / total < 0.005,
    `${openedAsSomethingElse}/${total} manglings still opened as a different collage`);
  // ...and it must never refuse a code that IS whole.
  for (let i = 0; i < 3000; i++) {
    const st = reachableState(rngOf(i * 61 + 9));
    check(decodeState(encodeState(st)) !== null, `sample ${i}: the checksum refused a code it minted`);
  }
  // A code minted before the checksum existed has a 15-character middle group
  // and is taken on trust, exactly as it was when it was sent.
  const [la, lb, lc] = encodeState(reachableState(rngOf(3))).split('-');
  for (const L of [6, 8, 9, 10, 15, 16]) {
    check(decodeState(`${la}-${lb.slice(0, L)}-${lc}`) !== null,
      `a pre-checksum code with a ${L}-character middle group was refused`);
  }
}

// =============================================================================
console.log('9. THE LINK — a code in a URL is the same code');
{
  const s = reachableState(rngOf(77));
  const code = encodeState(s);
  const bases = [
    'https://mrdirno.github.io/nested-resonance-memory-archive/collage/',
    'http://localhost:5199/',
    'https://example.test/a/b/index.html?x=1',
  ];
  for (const base of bases) {
    const u = new URL(base);
    u.searchParams.set('c', code);
    check(codeFromUrl(u.toString()) === code, `a query code was lost from ${u}`);
    const h = new URL(base);
    h.hash = `c=${code}`;
    check(codeFromUrl(h.toString()) === code, `a hash code was lost from ${h}`);
    const bare = new URL(base);
    bare.hash = code;
    check(codeFromUrl(bare.toString()) === code, `a bare-hash code was lost from ${bare}`);
    check(codeFromUrl(base) === null, `${base} has no code but one was found`);
  }
  check(codeFromUrl('not a url') === null, 'a non-URL produced a code');
  check(decodeState(codeFromUrl(`https://x.test/?c=${code}`)) !== null, 'a code from a URL did not decode');
}

// =============================================================================
console.log('10. RED PROOF — what the PREVIOUS encoder got wrong on the same set');
{
  // The encoder as it stood before this cycle, re-implemented here from the
  // shipped diff. It is not asked to be right; it is asked to show HOW MANY of
  // the compositions above it could not carry, so the fix is a number.
  const OLD_LAYOUT_ORDER = GENERATORS.map((g) => g.id);          // no legacy modes
  const BG_VALUES = Object.values(BACKGROUND_SWATCHES);
  const oldEncode = (s) => {
    const r = rollFromState(s);
    const li = Math.max(0, OLD_LAYOUT_ORDER.indexOf(r.layout));  // -> 0 for legacy modes
    const ai = Math.max(0, ASPECT_ROSTER.findIndex((a) => Math.abs(a - r.aspect) < 0.01));
    const e = Math.round(Math.min(1, Math.max(0, r.entropy)) * 63);
    const g = Math.round(Math.min(0.03, Math.max(0, r.gutter)) * 2000);
    const z = Math.round(Math.min(4, Math.max(0.5, r.zoom)) * 100);
    const bgi = Math.max(0, BG_VALUES.indexOf(r.bg));            // -> 0 for any other colour
    const f = (n, w = 1) => Math.max(0, Math.round(n)).toString(36).padStart(w, '0');
    const ari = Math.max(0, ARRANGEMENT_IDS.indexOf(r.arrangement));
    const foi = Math.max(0, FOCUS_IDS.indexOf(r.focus));
    const twi = Math.max(0, TWIST_IDS.indexOf(r.twist));
    return `${f(li, 2)}${f(r.count, 3)}${f(e, 2)}-${f(ai)}${f(g, 2)}${f(z, 2)}${f(bgi)}${f(ari)}${f(foi)}${f(twi)}-${f(r.seed, 4)}`
      .toUpperCase();
  };
  // Read back with the CURRENT reader, which is what an old code would meet.
  const tally = { total: 0, wrong: 0, byField: {} };
  for (let i = 0; i < SAMPLES; i++) {
    const s = reachableState(rngOf(i * 2654435761 + 7));   // the identical set as section 1
    tally.total++;
    const back = decodeState(oldEncode(s));
    if (!back) { tally.wrong++; tally.byField.undecodable = (tally.byField.undecodable || 0) + 1; continue; }
    const bad = FIELDS.filter((k) => !Object.is(s[k], back[k]));
    if (bad.length) {
      tally.wrong++;
      for (const k of bad) tally.byField[k] = (tally.byField[k] || 0) + 1;
    }
  }
  const pct = ((tally.wrong / tally.total) * 100).toFixed(1);
  console.log(`   the old encoder mis-carried ${tally.wrong}/${tally.total} (${pct}%) of the same compositions`);
  console.log(`   by field: ${Object.entries(tally.byField).sort((a, b) => b[1] - a[1])
    .map(([k, v]) => `${k}=${v}`).join(' ')}`);
  check(tally.wrong > tally.total * 0.5,
    `the red proof is not red: the old encoder only failed ${tally.wrong}/${tally.total}. ` +
    'Either the fix is not doing anything or this sweep cannot see it.');
}

// =============================================================================
console.log(`\n${checks.toLocaleString()} checks / ${failures} failures`);
if (failures) { console.error(`FAILED — ${failures} assertion(s)`); process.exit(1); }
console.log('all green');
