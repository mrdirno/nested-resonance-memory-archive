/**
 * ANSWER-BACK TAP-NOTE — the buttons and the instructions are one vocabulary.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * The answer page's tap-cycle rungs come from TOOLKIT_ANSWER.answers (or the
 * engine's default four), but the "Tap a row to answer it. Once for X, again
 * for Y…" instruction is BAKED PROSE in each trade's page copy. Two sources,
 * no coupling — and flooring shipped the proof: a lede and a registry desc
 * promising "mine and done · mine but it needs material · not mine · that's
 * damage and it needs a ticket" over buttons that said "Will do / In already /
 * Can't / Need to know", for eleven days, because nothing asserted the pair.
 * Same class as the hand-kept `watch` list on the order pages (2026-08-14):
 * a second copy of a vocabulary, kept by hand, drifting silently.
 *
 * RULE: for every trade page riding the answer engine, every rung the config
 * ships (all four, or the default four when no override) must appear verbatim
 * in that page's tap-note. Static check — no browser, runs anywhere node runs.
 *
 *   node tools/toolkit-gates/answer-tapnote.mjs
 */
import { readdirSync, readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { join } from 'path';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const DEFAULT = ['Will do', 'In already', 'Can’t', 'Need to know'];
const PAGES = ['answer-back.html', 'notes-back.html'];

function normalize(html) {
  return html
    .replace(/&rsquo;|&#8217;/g, '’')
    .replace(/&mdash;|&#8212;/g, '—')
    .replace(/&amp;/g, '&')
    .replace(/<[^>]+>/g, '');
}

function answersOf(itemsSrc) {
  // The override is a flat literal array of four strings on one config line.
  const blk = itemsSrc.match(/window\.TOOLKIT_ANSWER\s*=\s*\{[\s\S]*?\n\};/);
  if (!blk) return null; // trade has the page but no config — page falls back wholesale
  const m = blk[0].match(/["']?answers["']?\s*:\s*\[([\s\S]*?)\]/);
  if (!m) return DEFAULT;
  const words = [...m[1].matchAll(/"((?:[^"\\]|\\.)*)"/g)].map(x => x[1].replace(/\\"/g, '"'));
  return words.length === 4 ? words : { bad: words.length };
}

const fails = [];
const trades = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
  .map(d => d.name).sort();

let checked = 0;
for (const t of trades) {
  for (const p of PAGES) {
    const pagePath = join(ROOT, t, p);
    if (!existsSync(pagePath)) continue;
    checked++;
    const rel = `${t}/${p}`;
    const itemsPath = join(ROOT, t, 'items.js');
    const answers = existsSync(itemsPath) ? answersOf(readFileSync(itemsPath, 'utf8')) : null;
    if (answers && answers.bad !== undefined) {
      fails.push(`${rel}  answers[] has ${answers.bad} entries — the engine requires exactly 4 (positions are meaning)`);
      continue;
    }
    const rungs = answers || DEFAULT;
    const page = normalize(readFileSync(pagePath, 'utf8'));
    const noteM = page.match(/Tap a (?:row|note|line) to answer it\.[\s\S]{0,400}?once more clears it/i);
    if (!noteM) { fails.push(`${rel}  no tap-note found — the instruction line is how a first-timer learns the cycle`); continue; }
    const note = noteM[0].toLowerCase().replace(/'/g, '’');
    for (const r of rungs) {
      const needle = r.toLowerCase().replace(/'/g, '’').replace(/\s*—\s*/g, ' — ');
      if (!note.includes(needle)) {
        fails.push(`${rel}  tap-note never says “${r}” — the buttons say it and the instructions teach something else`);
      }
    }
  }
}

if (fails.length) {
  console.error(`ANSWER TAP-NOTE — ${fails.length} defect(s) across ${checked} page(s):`);
  for (const f of fails) console.error('  ' + f);
  process.exit(1);
}
console.log(`ANSWER TAP-NOTE — ${checked} page(s) clean: every rung the config ships is in the instructions that teach it.`);
