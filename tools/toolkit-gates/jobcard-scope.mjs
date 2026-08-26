/**
 * THE JOB CARD KEEPS ITS JOBS APART — a gate for shared/jobcard.js.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * shared/jobcard.js exists because six order pages hand-copied a sticky header
 * keyed to the PAGE while its own comment claimed the values belonged to the
 * JOB. The redesign makes every job a chip and the picker the guard. That buys
 * exactly one thing — a foreman on two jobs stops sending the warehouse's gate
 * code to the downtown supplier — and it is worth nothing if the separation is
 * not real. A card that leaks is strictly worse than the sticky header it
 * replaced, because it LOOKS job-aware.
 *
 * So this drives the real page and asserts the separation as OUTPUT, off the
 * clipboard, not off the DOM:
 *
 *  · A NEW JOB STARTS EMPTY. The safety property, and the whole reason "+ New
 *    job" is a deliberate tap rather than something inferred from him editing
 *    the name box. Every per-job field is asserted blank after the tap.
 *  · JOB A'S ANSWERS NEVER REACH JOB B'S DOCUMENT. The per-job values that
 *    actually print are collected from job A's real copied text, then looked for
 *    in job B's — and finding any one of them is the failure this module was
 *    built to stop.
 *  · SWITCHING BACK RESTORES. A picker that forgets on the way back is a picker
 *    that costs him the gate code every time he checks the other job.
 *  · THE DEVICE FIELDS DO NOT MOVE. "Requested by" is him on every job; blanking
 *    it with the rest would make the card feel broken on the second tap.
 *  · IT SURVIVES A RELOAD. Sticky that does not come back is worse than not
 *    sticky at all — he stops trusting it (the reason dropoff-block.mjs asserts
 *    the same thing three files away).
 *  · NOBODY LOSES A GATE CODE ON THE WAY IN. The old per-page key is seeded in a
 *    clean profile and the values are asserted to arrive on job #1. A migration
 *    that drops a foreman's saved access note is a data-loss bug shipped to a
 *    live page.
 *  · NO `fresh:` SCOPE EVER COMES BACK. It existed for about an hour and
 *    order-live-header.mjs killed it: a field printed in the document has to
 *    survive a reload, and blanking it on load loses a delivery method the man
 *    picked twenty minutes ago without losing anything he would notice. The
 *    reasoning is in shared/jobcard.js; this is the assertion, so the next page
 *    cannot re-invent it.
 *
 * WHAT IT DERIVES vs WHAT IT READS. The scopes are learned from the module's own
 * BEHAVIOUR — fill the header, then read which ids landed under `jobs[].f`
 * (per-job) and which under `device` in its store. Only `legacyKey` is read from
 * the page source, because the name of a key that no longer gets written cannot
 * be observed by driving the page.
 *
 *   node tools/toolkit-gates/jobcard-scope.mjs [--only=electrical/pull-list.html]
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const ONLY = (process.argv.slice(2).find(a => a.startsWith('--only=')) || '').slice(7);

function pages() {
  const out = [];
  const trades = readdirSync(ROOT, { withFileTypes: true })
    .filter(d => d.isDirectory() && !d.name.startsWith('.') && existsSync(join(ROOT, d.name, 'tools.js')))
    .map(d => d.name).sort();
  for (const t of trades) {
    for (const f of readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html')).sort()) {
      const src = readFileSync(join(ROOT, t, f), 'utf8');
      /* A MENTION IS NOT A MOUNT, and this gate learned that by enrolling a page
       * on the strength of a COMMENT. hvac/truck-stock.html deliberately has no
       * job card — a van is restocked at the shop, there is no job to pick — and
       * the day its header was fixed the fix was explained in a comment naming
       * shared/jobcard.js, which is all the old test looked for. It then failed
       * the page for not rendering a chip it was never supposed to have. So the
       * script has to be LOADED and the module has to be CALLED. */
      if (src.includes('shared/jobcard.js') && src.includes('JobCard.mount')) {
        out.push({ rel: `${t}/${f}`, trade: t, src });
      }
    }
  }
  return ONLY ? out.filter(p => p.rel === ONLY) : out;
}

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.png': 'image/png' };
function serve() {
  return new Promise(res => {
    const s = createServer((req, rq) => {
      const rel = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
      const p = join(ROOT, rel);
      if (!p.startsWith(ROOT) || !existsSync(p) || statSync(p).isDirectory()) { rq.writeHead(404); return rq.end('no'); }
      rq.writeHead(200, { 'content-type': MIME[extname(p)] || 'application/octet-stream' });
      rq.end(readFileSync(p));
    });
    s.listen(0, '127.0.0.1', () => res({ s, port: s.address().port }));
  });
}

const STUB = () => {
  window.__copied = null;
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    value: { writeText: t => { window.__copied = String(t); return Promise.resolve(); } },
  });
};
async function copied(page) {
  await page.evaluate(() => { window.__copied = null; });
  await page.click('#copy');
  await page.waitForFunction(() => window.__copied !== null, null, { timeout: 4000 });
  return page.evaluate(() => window.__copied);
}

/* Fill every header control the house convention names (id `f` + a capital,
 * outside the ticked list) with a value that cannot occur by accident. Dates and
 * checkboxes are left alone — a marker string is not a datetime, and this gate
 * is about text the counter reads. */
async function fillHeader(page, tag) {
  return page.evaluate(t => {
    const list = document.getElementById('list');
    const put = {};
    document.querySelectorAll('input[id^="f"],select[id^="f"],textarea[id^="f"]').forEach(el => {
      if (!/^f[A-Z]/.test(el.id) || el.type === 'hidden') return;
      if (list && list.contains(el)) return;
      if (el.tagName === 'SELECT') return;
      if (['date', 'datetime-local', 'time', 'checkbox', 'radio', 'number'].includes(el.type)) return;
      const v = `Z${t}_${el.id}Z`;
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      put[el.id] = v;
    });
    return put;
  }, tag);
}

/* THE ANSWERS THAT ARE NOT `f`-FIELDS, and on one page they are the only ones
 * that matter. shared/dropoff.js renders its own block under its own `do-` ids
 * and prints the GATE CODE — the most job-specific thing this program ever
 * holds, and the reason the module exists. Those ids are not in the card's
 * store, so scope-derivation cannot see them: a leak check that reads only the
 * house `f` convention would call the page clean while last month's gate code
 * rides out on today's order to a different address. So anything the page
 * renders that reaches job A's document is looked for in job B's, whoever
 * rendered it. A page with no such block returns nothing and asserts nothing. */
async function reveal(page) {
  const on = () => page.evaluate(() => {
    const h = document.getElementById('dropoff');
    return !!(h && h.classList.contains('on'));
  });
  if (!(await page.$('#dropoff'))) return false;
  if (await on()) return true;
  for (const b of await page.$$('.seg button, .seg [data-v]')) {
    try { await b.click(); } catch (e) { continue; }
    if (await on()) return true;
  }
  /* the engine-driven order pages reveal it off a header <select> (`fHow`) */
  const sels = await page.$$eval('select[id^="f"]', els => els.filter(e => /^f[A-Z]/.test(e.id)).map(e => ({ id: e.id, opts: [...e.options].map(o => o.value) })));
  for (const sel of sels) {
    for (const v of sel.opts) {
      try { await page.selectOption('#' + sel.id, v); } catch (e) { continue; }
      if (await on()) return true;
    }
  }
  return on();
}
async function fillBlocks(page, tag) {
  return page.evaluate(t => {
    const put = {};
    document.querySelectorAll('#dropoff input[type="text"], #dropoff textarea').forEach(el => {
      if (!el.id) return;
      const v = `Z${t}_${el.id.replace(/[^A-Za-z0-9]/g, '')}Z`;
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      put[el.id] = v;
    });
    return put;
  }, tag);
}

const fails = [];
const fail = (p, m) => fails.push(`${p}  ${m}`);

const { s, port } = await serve();
const browser = await chromium.launch();
/* Per-page notes for the SELECT class this gate grew on 2026-08-26 — see the
 * block that fills them, and §SCARS: fillHeader() skips selects on purpose
 * (a marker string is not an option value), so the per-job selects were outside
 * every assertion here while the summary line claimed otherwise. */
const selNote = [];
const list = pages();
if (!list.length) { console.error('no page mounts shared/jobcard.js'); process.exit(1); }

for (const { rel, trade, src } of list) {
  /* ── the source-level regression guard ────────────────────────────────── */
  if (/\bfresh\s*:/.test(src.slice(src.indexOf('JobCard.mount')))) {
    fail(rel, 'JobCard.mount declares a `fresh:` scope — order-live-header.mjs killed that scope, see shared/jobcard.js');
  }
  const legacyKey = (src.match(/legacyKey:\s*"([^"]+)"/) || [])[1] || null;
  /* A PAGE BORN WITH A JOB CARD HAS NOTHING TO ADOPT, and until this it could not
   * say so — the branch at the bottom fails any page without a legacyKey, which
   * is the right default (silence is how a real migration goes missing) and the
   * wrong verdict for a page that never had a sticky header to lose. So the
   * escape is an EXPLICIT `legacyKey: null`, in the source, in the diff, where a
   * reviewer sees the claim being made. OMISSION still fails. */
  const noPredecessor = /legacyKey:\s*null\b/.test(src);

  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 } });
  await ctx.addInitScript(STUB);
  const page = await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
  await page.waitForSelector('#jobcard .jc-chip', { state: 'attached', timeout: 5000 })
    .catch(() => fail(rel, 'no job chip rendered — shared/jobcard.js did not mount'));

  /* ONE LINE ON THE LIST FIRST, and it is not incidental. Every one of these
   * pages short-circuits its own document when nothing is ticked — `if
   * (!ctx.count) return out + "(nothing on it yet)"` — which drops the whole
   * footer where the gate code, the signer and the PO are printed. Copying an
   * empty list and concluding the card guards nothing is the gate lying about
   * three live pages, which is exactly what it did the first time it ran. */
  const ticked = await page.evaluate(() => {
    const t = document.querySelector('#list .item .tick');
    if (!t) return false;
    t.checked = true;
    t.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  });
  if (!ticked) fail(rel, 'no tickable line in #list — the document cannot be exercised');

  const KEY = `toolkit.${trade}.jobcard.v1`;
  const putA = await fillHeader(page, 'A');
  const hasBlock = await reveal(page);
  const blockA = hasBlock ? await fillBlocks(page, 'A') : {};
  await page.waitForTimeout(60);

  const store = await page.evaluate(k => { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }, KEY);
  if (!store || !store.jobs || !store.jobs.length) { fail(rel, `nothing written to ${KEY} after filling the header`); await ctx.close(); continue; }
  const jobA = store.jobs.find(j => j.id === store.cur) || store.jobs[0];
  const PER = Object.keys(jobA.f || {}).filter(id => putA[id]);
  const DEV = Object.keys(store.device || {}).filter(id => putA[id]);
  if (!PER.length) { fail(rel, 'no per-job field was recorded — perJob is empty or the ids do not exist on the page'); await ctx.close(); continue; }
  for (const id of PER) if (DEV.includes(id)) fail(rel, `#${id} is declared BOTH per-job and device — one of them is a lie`);

  /* Which per-job answers actually reach the counter. Those are the ones a leak
   * would be measured in; a field that never prints cannot contaminate. */
  const docA = await copied(page);
  const visible = PER.filter(id => docA.includes(putA[id]));
  if (!visible.length) fail(rel, 'not one per-job field reaches the sent document — the card is guarding nothing');
  const blockVisible = Object.keys(blockA).filter(id => docA.includes(blockA[id]));
  if (hasBlock && !blockVisible.length) {
    fail(rel, 'the drop-off block is on the page and nothing typed into it reached the document — the leak test below would prove nothing');
  }

  /* ── THE PER-JOB SELECTS, WHICH THIS GATE COULD NOT SEE ─────────────────
   * `PER` is derived from the fields `fillHeader` typed into, and it types into
   * text boxes — so every per-job <select> on the rack was outside this gate
   * while its summary line said "a new job starts empty". It was not: a select
   * is checked below with `if (afterNew[id])`, and a correctly RESET select is
   * truthy ("Job"), so even inside PER that assertion could not have expressed
   * the right thing. Both halves are why `shared/jobcard.js`'s setVal() shipped
   * a leak on 9 pages — a new job kept the LAST job's charge code and printed it
   * as its own (§SCARS 2026-08-26).
   *
   * EMPTY FOR A SELECT IS ITS DEFAULT, not "". Pick a non-default option on job
   * A, start a new job, and the control must be back on the option the markup
   * marks selected — option zero where the markup names none. */
  const selPer = await page.evaluate(ids => ids.map(id => {
    const el = document.getElementById(id);
    if (!el || el.tagName !== 'SELECT') return null;
    const def = (el.querySelector('option[selected]') || el.options[0] || {}).value;
    const other = [...el.options].map(o => o.value).find(v => v !== def);
    if (other == null) return null;
    el.value = other;
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return { id, def, other };
  }).filter(Boolean), Object.keys(jobA.f || {}));
  await page.waitForTimeout(80);

  /* ── a new job starts EMPTY ───────────────────────────────────────────── */
  const newBtn = await page.$('#jobcard .jc-new');
  if (!newBtn) { fail(rel, 'no "+ New job" control — a second job cannot be started'); await ctx.close(); continue; }
  await newBtn.click();
  await page.waitForTimeout(60);

  const afterNew = await page.evaluate(ids => {
    const o = {};
    ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
    return o;
  }, PER.concat(DEV).concat(Object.keys(blockA)));
  for (const id of PER) {
    if (afterNew[id]) fail(rel, `#${id} still reads "${afterNew[id]}" on a brand-new job — a new job must start empty`);
  }
  for (const id of DEV) {
    if (afterNew[id] !== putA[id]) fail(rel, `#${id} is a device field and was cleared by starting a new job (now "${afterNew[id]}")`);
  }
  for (const id of Object.keys(blockA)) {
    if (afterNew[id]) fail(rel, `#${id} still reads "${afterNew[id]}" on a brand-new job — the drop-off block did not follow the chip, so the gate code belongs to the last job`);
  }
  if (selPer.length) {
    const nowSel = await page.evaluate(ids => {
      const o = {};
      ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
      return o;
    }, selPer.map(s => s.id));
    for (const s of selPer) {
      if (nowSel[s.id] === s.other) {
        fail(rel, `#${s.id} is a per-job SELECT and still reads "${s.other}" on a brand-new job — the last job's answer is on the glass and goes out as this job's own`);
      } else if (nowSel[s.id] !== s.def) {
        fail(rel, `#${s.id} landed on "${nowSel[s.id]}" on a brand-new job — a reset must be the option the markup marks selected ("${s.def}"), never a third value`);
      }
    }
    selNote.push(`${rel.padEnd(34)} ${selPer.length} per-job select(s) reset to default on a new job`);
  }

  /* ── and job A's answers never reach job B's document ─────────────────── */
  await reveal(page);
  const docB = await copied(page);
  for (const id of visible.concat(blockVisible)) {
    const v = putA[id] || blockA[id];
    if (docB.includes(v)) fail(rel, `#${id} from the first job is in the SECOND job's sent document — the cards leak`);
  }

  /* ── switching back restores ──────────────────────────────────────────── */
  await fillHeader(page, 'B');
  if (hasBlock) await fillBlocks(page, 'B');
  await page.waitForTimeout(60);
  const chips = await page.$$('#jobcard .jc-chip[data-j]');
  if (chips.length < 2) fail(rel, `only ${chips.length} job chip(s) after starting a second job`);
  else {
    await chips[0].click();
    await page.waitForTimeout(60);
    const want = Object.assign({}, putA, blockA);
    const back = await page.evaluate(ids => {
      const o = {};
      ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
      return o;
    }, PER.concat(Object.keys(blockA)));
    for (const id of PER.concat(Object.keys(blockA))) {
      if (back[id] !== want[id]) fail(rel, `#${id} came back as "${back[id]}" instead of "${want[id]}" after switching to the other job and back`);
    }

    /* ── AND HE CAN SEE WHICH ONE IS LIT ──────────────────────────────────
     * Every assertion above this one is about WHERE an answer is stored. This
     * one is about whether the man can tell which store he is writing into,
     * and until 2026-08-17 the answer on eleven of twelve trades was "barely".
     * `.jc-chip.on` drew its border and inset ring in `--flag`, the trade
     * ACCENT — a colour picked and measured against the DARK nav, therefore
     * light by construction, on a chip that is drawn on WHITE. Measured: 1.30:1
     * (sitework) to 2.28:1 (electrical) on eleven trades, and against the grey
     * it replaces the swap carried no luminance step at all. The whole lit
     * state was resting on bolder text. On the one control whose answers are a
     * gate code and a PO, that is a wrong-job write waiting to happen.
     * Asserted here against the UNLIT chip's own background rather than a
     * hardcoded white, so a trade that restyles the rack still has to clear it.
     * Verified by reverting the shared rule to `--flag`: 11 pages fail. */
    const litRead = await page.evaluate(() => {
      const on = document.querySelector('#jobcard .jc-chip.on');
      const off = document.querySelector('#jobcard .jc-chip:not(.on)');
      if (!on || !off) return null;
      const num = s => (s.match(/[\d.]+/g) || []).slice(0, 3).map(Number);
      const lum = ([r, g, b]) => {
        const c = [r, g, b].map(v => v / 255).map(v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
      };
      const cr = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
      const cs = getComputedStyle(on);
      return { border: cs.borderTopColor, ratio: cr(num(cs.borderTopColor), num(getComputedStyle(off).backgroundColor)) };
    });
    if (!litRead) fail(rel, 'could not find a lit and an unlit job chip side by side');
    else if (litRead.ratio < 3) {
      fail(rel, `the LIT job chip's border is ${litRead.border} — only ${litRead.ratio.toFixed(2)}:1 against the unlit chip beside it (bar 3:1). He cannot see which job he is writing a gate code into`);
    }
  }

  /* ── it survives a reload ─────────────────────────────────────────────── */
  await page.reload({ waitUntil: 'load' });
  await page.waitForSelector('#jobcard .jc-chip', { state: 'attached', timeout: 5000 }).catch(() => {});
  const reloaded = await page.evaluate(ids => {
    const o = {};
    ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
    return o;
  }, PER);
  for (const id of PER) {
    if (reloaded[id] !== putA[id]) fail(rel, `#${id} did not survive a reload (came back "${reloaded[id]}", expected "${putA[id]}")`);
  }
  await ctx.close();

  /* ── nobody loses a gate code on the way in ───────────────────────────── */
  if (legacyKey) {
    const seed = {};
    PER.concat(DEV).forEach(id => { seed[id] = `ZOLD_${id}Z`; });

    /* BOTH SHAPES THIS CODEBASE EVER WROTE A STICKY HEADER IN, and the second one
     * is here because seeding only the first is how this gate returned green over
     * a page that lost every saved answer. Six pages hand-rolled the flat bag —
     * localStorage.setItem(SKEY, JSON.stringify({fJob:"…"})). The pages that kept
     * the same header through shared/draft.js got its wrapper for free, because
     * Draft.keep's only writer stores {v, s} — so a flat read finds nothing, the
     * adoption quietly declines, and the man opens a blank card. The gate has to
     * write what the PAGE writes, and the page it was first written against
     * happened to be one of the six. */
    for (const [shape, record] of [['flat', seed], ['draft-wrapped', { v: 1, s: seed }]]) {
      const c2 = await browser.newContext({ viewport: { width: 390, height: 780 } });
      await c2.addInitScript(STUB);
      await c2.addInitScript(([k, v]) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }, [legacyKey, record]);
      const p2 = await c2.newPage();
      await p2.goto(`http://127.0.0.1:${port}/${rel}`, { waitUntil: 'load' });
      await p2.waitForSelector('#jobcard .jc-chip', { state: 'attached', timeout: 5000 }).catch(() => {});
      const got = await p2.evaluate(ids => {
        const o = {};
        ids.forEach(id => { const el = document.getElementById(id); o[id] = el ? el.value : null; });
        return o;
      }, PER.concat(DEV));
      for (const id of PER.concat(DEV)) {
        if (got[id] !== seed[id]) fail(rel, `a ${shape} record at the old key ${legacyKey} held #${id}="${seed[id]}" and the job card came up with "${got[id]}" — a migration that loses a saved answer`);
      }
      await c2.close();
    }
  } else if (noPredecessor) {
    console.log(` ${rel}  legacyKey: null — declared as a page with no sticky header to adopt`);
  } else {
    fail(rel, 'no legacyKey declared — a page that had a sticky header must adopt it or the foreman loses it. A page born with a card declares `legacyKey: null` and says so');
  }

  /* THE BLOCK COUNT IS PRINTED, not just asserted. An assertion that quietly
   * covers nothing reads exactly like an assertion that passed — and the block
   * ids are the ones a leak would actually be measured in on the one page that
   * has them, so "0 in the document" on a page with a drop-off block is the
   * gate telling you it is lying. */
  console.log(` ${rel}  ${PER.length} per-job, ${DEV.length} device, ${visible.length} of them in the document`
    + (hasBlock ? `  ·  drop-off block: ${Object.keys(blockA).length} field(s), ${blockVisible.length} in the document` : ''));
}

await browser.close();
s.close();

if (fails.length) {
  console.log(`\nFAIL — ${fails.length} defect(s):`);
  for (const f of fails) console.log('  ✗ ' + f);
  process.exit(1);
}
selNote.forEach(l => console.log(' ' + l));
console.log(`\nPASS — ${list.length} page(s): jobs stay apart, a new job starts empty (text AND selects), nothing is lost on the way in.`);
