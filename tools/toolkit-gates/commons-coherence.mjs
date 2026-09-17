/**
 * THE ACCESSORY-HOST COHERENCE GATE — a gear row that names a consumable or an
 * insert must sit on a trade whose bag also holds the tool that drives it.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 *   node tools/toolkit-gates/commons-coherence.mjs [--root=DIR] [--selftest]
 *
 * Data only. No browser, no base url — the defect is in the gear list and it is
 * on the page the moment it is in the file. Same --root shape as commons-scope,
 * so the DEPLOY asserts HELIOS-BRIDGE/dist and not the source it was copied from.
 *
 * WHY THIS EXISTS. 2026-09-09 (C3725) a door installer's whole bag on the live
 * page was seventeen rows that included "self-centering bits, in every screw
 * size you actually drive" and "taps in the machine screw sizes" — and no drill
 * to turn either. commons-scope, which counts the rows a trade OWNS, was green:
 * doors cleared its floor, so nothing fired. That cycle widened the drill onto
 * doors by hand. The panel that ranked it named the GENERAL rung and did not
 * build it — an accessory whose HOST is absent is a class, not one row, and it
 * is the shape of both prior commons scars (framing 2026-08-09, roofing
 * 2026-08-13, each a list that existed and was never told a thing had changed).
 *
 * WHY A CURATED TABLE AND NOT A REGEX. This was measured once, 2026-09-09, with
 * a throwaway seven-pair regex probe, and it got the answer wrong in both
 * directions — which is the whole argument for this file. It MISSED the one real
 * orphan, sitework's "Laser receiver and a pocket of batteries" on a bag with no
 * laser to read, because its host token was the bare word "laser" and so the
 * receiver row hosted itself. And it FLAGGED two rows that are correct: masonry
 * "Mason's line, blocks and pins" (line pins, not powder-actuated pins) and
 * sitework "Gasket lube, spare gaskets and a rag" (read as needing a pipe tool).
 * A loose pattern over prose false-fires on words that collide and goes blind on
 * a host it did not spell out. So here the accessory is matched on the row's
 * NAME by whole word — never its why-line, where "a bit that catches will twist
 * your wrist" lives on the drill itself — and the host is a curated list of the
 * tools that actually drive that accessory, spelled out enough that a "laser
 * receiver" is not itself a laser.
 *
 * AND THE ERROR IS THE REVIEW. Failing names the trade, the row, the accessory
 * and the host that is missing, in a sentence a person who does the work can
 * agree or disagree with. Clearing it means either widening a host onto the
 * trade — as C3725 did for doors — or deciding the accessory does not ride on
 * that bag. A count is one keystroke; a named missing tool is a claim.
 */
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';

const args = process.argv.slice(2);
const argRoot = args.find((a) => a.startsWith('--root='));
const ROOT = argRoot
  ? argRoot.slice(7).replace(/\/?$/, '/')
  : fileURLToPath(new URL('../../', import.meta.url));
const SELFTEST_ONLY = args.includes('--selftest');

/* THE CURATED PAIRS. `acc` are whole-word tokens that mark the row's NAME as
 * this accessory; `not` are tokens that take it back (a "multi-bit screwdriver"
 * IS the host, not a bag of bits). `host` are substrings looked for across the
 * trade's whole inventory of NAMES — multi-word on purpose, so "laser receiver"
 * does not answer the receiver's own need. `verb`/`need` write the review line.
 * The three the C3725 panel named are bits→driver, blades→saw, receiver→laser;
 * taps rides with bits because that cycle paired them (a machine-screw tap into
 * sheet steel is turned by the drill or a tap wrench, and doors carried taps
 * with neither). */
const PAIRS = [
  { key: 'bits', acc: ['bit', 'bits'], not: ['driver', 'screwdriver'],
    host: ['drill', 'impact', 'screw gun', 'screwgun', 'powder-actuated'],
    verb: 'turn', need: 'drill', synth: 'Self-centering bits, a full set' },
  { key: 'taps', acc: ['tap', 'taps'], not: ['tape', 'tapping', 'taping', 'tack'],
    host: ['drill', 'impact', 'tap wrench'],
    verb: 'turn', need: 'drill or tap wrench', synth: 'Taps in the machine screw sizes' },
  { key: 'blades', acc: ['blade', 'blades'], not: [],
    host: ['knife', 'saw', 'grinder', 'lute', 'hatchet', 'shear', 'shears', 'snips', 'plane', 'cutter'],
    verb: 'hold', need: 'knife or saw', synth: 'Reciprocating blades, a fresh pack' },
  { key: 'receiver', acc: ['receiver'], not: [],
    host: ['rotary laser', 'laser level', 'pipe laser', 'laser transmitter', 'transit',
           'optical level', "builder's level", 'dumpy level', 'total station'],
    verb: 'read', need: 'laser', synth: 'Grade receiver and a pocket of batteries' },
];

const words = (s) => String(s).toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
const hay = (s) => String(s).toLowerCase();

/* is this row THIS accessory? — a whole-word hit in `acc`, no word in `not`. */
function isAccessory(pair, name) {
  const w = new Set(words(name));
  if (!pair.acc.some((t) => w.has(t))) return false;
  if (pair.not.some((t) => w.has(t))) return false;
  return true;
}
/* does any name in this inventory provide the host? (the row itself counts, so
 * a "circular saw ... and the blade that lives in it" hosts its own blade.) */
function hasHost(pair, names) {
  const blob = names.map(hay).join('  ');
  return pair.host.some((h) => blob.includes(h));
}
/* the orphans in one inventory (a flat list of row {id,n}). */
function orphansIn(rows) {
  const names = rows.map((r) => r.n);
  const out = [];
  for (const r of rows) {
    for (const pair of PAIRS) {
      if (isAccessory(pair, r.n) && !hasHost(pair, names)) {
        out.push({ id: r.id, n: r.n, pair });
      }
    }
  }
  return out;
}

/* ---- the self-test: a gate wired into a deploy that has silently stopped ----
 * firing is this book's oldest scar, so the gate proves it can fire before it
 * is trusted to say a thing is clean. Runs on every invocation. */
function selftest() {
  const problems = [];
  // (a) each pair fires on its own lone synthetic accessory with no host.
  for (const pair of PAIRS) {
    const o = orphansIn([{ id: `synth-${pair.key}`, n: pair.synth }]);
    if (!o.some((x) => x.pair.key === pair.key)) {
      problems.push(`pair "${pair.key}" did not fire on its synthetic "${pair.synth}"`);
    }
  }
  // (b) a host present makes the same synthetic pass — no pair fires on nothing.
  for (const pair of PAIRS) {
    const hostRow = { id: 'host', n: pair.host[0] === 'rotary laser' ? 'Rotary laser and tripod'
                       : pair.host[0] === 'drill' ? 'Cordless drill/driver'
                       : 'Utility knife and a hacksaw' };
    const o = orphansIn([{ id: `synth-${pair.key}`, n: pair.synth }, hostRow]);
    if (o.some((x) => x.pair.key === pair.key)) {
      problems.push(`pair "${pair.key}" still fired with host "${hostRow.n}" present`);
    }
  }
  // (c) the two known FALSE POSITIVES of the throwaway probe must stay silent.
  const fp = orphansIn([
    { id: 'mason-line-blocks', n: "Mason's line, blocks and pins" },
    { id: 'gasket-lube', n: 'Gasket lube, spare gaskets and a clean rag' },
    { id: 'tapping-block', n: 'Tapping block, pull bar and spacers' },
    { id: 'taping-knives', n: 'Taping knives & mud pan' },
  ]);
  if (fp.length) problems.push(`false-positive rows fired: ${fp.map((x) => x.id + '/' + x.pair.key).join(', ')}`);
  return problems;
}

/* ---- the pre-C3725 doors fixture: strip the drill back off doors and the ----
 * bits and the taps must both surface. This is the real regression the whole
 * rung is named after. */
function preC3725Doors(gear) {
  const eff = gear.filter((r) => r.t.includes('universal') || r.t.includes('doors'));
  // pre-C3725 doors carried no drill; remove any host that turns a bit.
  const stripped = eff.filter((r) => !['drill', 'impact', 'screw gun', 'screwgun', 'powder-actuated']
    .some((h) => hay(r.n).includes(h)));
  return orphansIn(stripped);
}

// ---------------------------------------------------------------------------
const stProblems = selftest();
if (stProblems.length) {
  console.error('FAIL — the coherence gate cannot be trusted, its own self-test failed:');
  stProblems.forEach((p) => console.error('  ✗ ' + p));
  process.exit(1);
}

// load the shipped gear the way the browser reads it
const gear = new Function('window', readFileSync(ROOT + 'commons/gear.js', 'utf8')
  + '\nreturn window.COMMONS_GEAR;')({});
const wc = {};
new Function('window', readFileSync(ROOT + 'commons/commons.js', 'utf8'))(wc);
const TRADES = (wc.COMMONS_TRADES || []).map((t) => t.slug).filter((s) => s !== 'universal');
const NAMEOF = new Map((wc.COMMONS_TRADES || []).map((t) => [t.slug, t.name]));
if (!TRADES.length) { console.error('FAIL: commons.js exports no trades'); process.exit(1); }

// the pre-C3725 doors fixture (part of trust, runs every time)
const preDoors = preC3725Doors(gear);
const hasBits = preDoors.some((o) => o.pair.key === 'bits');
const hasTaps = preDoors.some((o) => o.pair.key === 'taps');
if (!(preDoors.length >= 2 && hasBits && hasTaps)) {
  console.error(`FAIL: the pre-C3725 doors fixture found ${preDoors.length} orphan(s) `
    + `(bits:${hasBits} taps:${hasTaps}) — the gate no longer catches the scar it is named for.`);
  process.exit(1);
}

if (SELFTEST_ONLY) {
  console.log(`commons-coherence self-test: ${PAIRS.length} pairs fire and clear, `
    + `2 known false positives stay silent, pre-C3725 doors surfaces `
    + `${preDoors.length} orphans (bits + taps). PASS`);
  process.exit(0);
}

// the live sweep: every trade's whole bag.
const fails = [];
let checked = 0;
for (const slug of TRADES) {
  const eff = gear.filter((r) => r.t.includes('universal') || r.t.includes(slug));
  checked += eff.length;
  for (const o of orphansIn(eff)) {
    fails.push(`${slug}: "${o.id}" (${o.n}) names ${o.pair.key === 'receiver' ? 'a receiver' : o.pair.key}`
      + ` but ${NAMEOF.get(slug) || slug}'s bag has no ${o.pair.need} to ${o.pair.verb} it`);
  }
}

console.log(`${checked} row-checks across ${TRADES.length} trades · ${PAIRS.length} curated pairs · `
  + `pre-C3725 doors fixture green — every list read from the shipped data`);
if (fails.length) {
  console.error(`\nFAIL — ${fails.length} accessory with no host:`);
  fails.forEach((f) => console.error('  ✗ ' + f));
  process.exit(1);
}
console.log('commons-coherence: PASS');
