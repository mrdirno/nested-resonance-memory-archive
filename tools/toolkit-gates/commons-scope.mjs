/**
 * THE SHARED-ROW SCOPE GATE — a row that several trades share must have been
 * looked at since the last trade joined.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 *   node tools/toolkit-gates/commons-scope.mjs
 *
 * Data only. No browser, no base url — the defect this catches is in the tag
 * list, and it is on the page the moment it is in the file.
 *
 * WHY THIS EXISTS. Twice before, a trade joined the program and a list that
 * already existed was never told. 2026-08-09 framing shipped a toolkit and the
 * commons trade list did not have it, so a framer opened a page calling itself
 * "every trade" and found seven chips, none of them his. 2026-08-13 roofing had
 * a chip on two surfaces and not one row written for it. Both fixes count rows
 * a trade OWNS — a chip must exist, and a floor of rows must be written for it.
 *
 * Both are blind to the third instance, which is what this file is for. A row
 * SHARED by several trades carries a tag list that was true on the day it was
 * written and is never revisited, because nothing goes wrong: every trade still
 * clears its own floor on its own narrow rows, so every existing gate is green.
 * Measured 2026-09-09: the nine trades that joined after 2026-08-09 held ZERO
 * shared rows across all three surfaces, 27 of 27 cells, while the founding
 * eight held 3-11 each. A door-hardware installer's whole bag on the live page
 * was seventeen rows that included self-centering bits and taps and no drill to
 * turn them, and no level, on a page whose own tip tells him to set every frame
 * off the level line.
 *
 * WHY NOT DETECT THE SHAPE. The first design flagged any wide row whose tag set
 * was exactly the roster as of some past moment. A review killed it and was
 * right, on two arguments this file exists to remember. It FALSE-FIRES, because
 * join order correlates with content: the first five trades are the MEP+AV
 * family, so `fixture-cutsheet` and three siblings are that family by meaning
 * and a roster prefix by accident — the gate would have demanded an excuse for
 * correct data, which teaches reviewers to write excuses. And it goes BLIND
 * after one touch: eight-minus-roofing is equally unreviewed and is not a
 * prefix, so a single cosmetic tag edit exempts a row forever.
 *
 * Shape is the wrong signal. TIME is the right one. `rv` on a row is the size of
 * the roster the last time somebody actually decided who shares it. It cannot
 * false-fire on content, one cosmetic edit does not launder it, and the day an
 * eighteenth trade joins every shared row in the commons comes back up for
 * review at once — which is the ratchet, not a side effect.
 *
 * AND THE ERROR MESSAGE IS THE REVIEW. A number is one keystroke, so the way
 * this stays honest is that failing prints every trade the row leaves out, by
 * name. Bumping `rv` means reading that list. An author who widens is done; an
 * author who does not has read the names of the people he is leaving off.
 */
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';

/* --root= so the DEPLOY can assert the ARTIFACT rather than the source it was
 * copied from. They are a straight cp today; this book's longest-running scar is
 * a fix that reached the repo and not the page, so the gate points at whatever
 * actually ships. Same flag shape as build-docsindex.mjs. */
const argRoot = process.argv.slice(2).find((a) => a.startsWith('--root='));
const ROOT = argRoot
  ? argRoot.slice(7).replace(/\/?$/, '/')
  : fileURLToPath(new URL('../../', import.meta.url));

/* WIDE is where a tag list stops being the argument. At three or fewer the row
 * is written FOR those trades and the existing NARROW rule already governs it;
 * at four the list has started to claim a family, and a claim is reviewable. */
const WIDE = 4;

const fails = [];
let checked = 0;
const fail = (m) => fails.push(m);
const ok = () => { checked++; };

/* the data, read the way the browser reads it */
const w = {};
for (const f of ['commons/commons.js', 'commons/gear.js', 'commons/tips.js', 'commons/names.js']) {
  new Function('window', readFileSync(ROOT + f, 'utf8'))(w);
}
const TRADES = (w.COMMONS_TRADES || []).filter((t) => t.slug !== 'universal');
const SLUGS = TRADES.map((t) => t.slug);
const NAMEOF = new Map(TRADES.map((t) => [t.slug, t.name]));
const N = SLUGS.length;

/* The surface list is parsed out of the shipped engine, never typed here — a
 * hand-written copy of a list that already exists is a scar with a date on it,
 * and this book has three of them. */
const SURFACES = (w.COMMONS_SURFACES || []).filter((s) => s.data && s.rows);
if (SURFACES.length < 2) { console.error('FAIL: commons.js exports no surface list'); process.exit(1); }
if (!N) { console.error('FAIL: commons.js exports no trades'); process.exit(1); }

let wide = 0;
for (const { data: file, rows: key, noun } of SURFACES) {
  const rows = w[key] || [];
  if (!rows.length) { fail(`${file} defined no rows`); continue; }

  for (const r of rows) {
    const tags = r.t || [];
    const universal = tags.includes('universal');

    /* 1. the back door. A row that names every trade is `universal` wearing a
     *    list — same claim, but with its negative space hidden, so no reviewer
     *    can see whether the omissions were reasoned about or just missed. */
    if (!universal && SLUGS.every((s) => tags.includes(s))) {
      fail(`${file}: "${r.id}" is tagged to all ${N} trades — that is t:["universal"] with the honesty removed. Say universal, or lose a tag.`);
      continue;
    }
    if (universal) { ok(); continue; }
    if (tags.length < WIDE) { ok(); continue; }

    wide++;
    const missing = SLUGS.filter((s) => !tags.includes(s));
    const who = missing.map((s) => NAMEOF.get(s)).join(', ');

    /* 2. an unknown tag means a trade was renamed and this row kept the old
     *    slug — it renders under nobody and reads as a deliberate omission. */
    const bogus = tags.filter((s) => !SLUGS.includes(s));
    if (bogus.length) fail(`${file}: "${r.id}" is tagged ${bogus.join(', ')}, which is not a trade on the roster`);

    /* 3. the gate. */
    if (typeof r.rv !== 'number' || !Number.isInteger(r.rv)) {
      fail(`${file}: "${r.id}" is shared by ${tags.length} trades and carries no rv — nobody has recorded when its scope was last decided. It leaves out ${missing.length}: ${who}. Widen it, or set rv:${N} and leave them off on purpose.`);
    } else if (r.rv > N) {
      fail(`${file}: "${r.id}" has rv:${r.rv} against a roster of ${N} — a review cannot have happened at a roster that never existed`);
    } else if (r.rv < N) {
      const joined = SLUGS.slice(r.rv).map((s) => NAMEOF.get(s)).join(', ');
      fail(`${file}: "${r.id}" was last scoped at ${r.rv} trades and there are now ${N}. Joined since: ${joined}. It leaves out ${missing.length}: ${who}. Decide, then set rv:${N}.`);
    } else ok();
  }
}

/* 4. rv is only meaningful where a scope is claimed. On a narrow row it is a
 *    number nothing reads, and a field that means nothing somewhere means less
 *    everywhere. */
for (const { data: file, rows: key } of SURFACES) {
  for (const r of (w[key] || [])) {
    const tags = r.t || [];
    if ('rv' in r && (tags.includes('universal') || tags.length < WIDE)) {
      fail(`${file}: "${r.id}" carries rv but is not a shared row (${tags.length} tag(s)) — rv belongs only where a scope is claimed`);
    }
  }
}

console.log(`${checked} checks · ${wide} shared row(s) of ${SURFACES.length} surface(s) · roster ${N} trades — every list read from the shipped data`);
if (fails.length) {
  console.error(`\nFAIL — ${fails.length}:`);
  fails.forEach((f) => console.error('  ✗ ' + f));
  process.exit(1);
}
console.log('commons-scope: PASS');
