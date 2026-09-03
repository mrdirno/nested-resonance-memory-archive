/**
 * SEND IS COPY — the share sheet gets, byte for byte, what the clipboard gets.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 *   node tools/toolkit-gates/send-is-copy.mjs [base-url] [--only <trade/page.html>] [--prove]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 *
 * WHY THIS GATE EXISTS. shared/toolkit.js mounts a Send button on every document
 * surface (C3698) — beside Copy where Copy is in the flow, in-flow under the
 * preview where Copy lives in a fixed bar: one tap hands the document to the OS
 * share sheet instead of the clipboard. The panel that scored it (av/AV_SOCIETY.md
 * §THE PANEL, 7 / 3 / 7) named the ways it goes wrong, and every one of them is
 * invisible on the page:
 *
 *   · the sheet gets a DIFFERENT text than Copy would (a provider that is not
 *     the copy function, or one that drifted) — the block on the glass is right,
 *     the message he sent is not;
 *   · the payload grows a `title` or `url` "for completeness" — a Subject on mail
 *     targets, a link chip on iOS, gone on SMS: the document changed and no
 *     question changed;
 *   · share() is called after an await — activation gone, NotAllowedError on
 *     iOS, and a fallback that hides it forever;
 *   · Cancel writes the clipboard he did not ask for, or a failure says nothing;
 *   · a page with a Copy button and no Send, with nobody having decided that;
 *   · the button is CSS-hidden where the API is absent instead of absent — a
 *     phantom tap target and a screen-reader ghost.
 *
 * WHAT IT DOES, per page, in a 390px mobile context with `navigator.share` and
 * the clipboard both STUBBED to record what they were handed:
 *
 *   1. classifies the page from its own source — which shared engines it loads,
 *      whether it registers Send by hand — into EXPECTED (must mount Send),
 *      EXCLUDED (must NOT: the named list below), or NEITHER (no Copy at all);
 *   2. asserts the button exists exactly where it should — paired to a BUTTON by
 *      the stamped data-for, beside it when Copy is in the flow, in a .tk-sendrow
 *      under the preview when Copy is fixed, never inside anything fixed — reads
 *      "Send", and mirrors Copy's disabled state;
 *   3. PARITY, empty then filled: clicks Copy, clicks Send, and requires the
 *      share payload to be exactly { text } with text === the clipboard text.
 *      "Filled" perturbs the page generically (first field, first tick, the
 *      add button) so the equality is not just two empty headers; how many
 *      pages actually moved is printed, never assumed;
 *   4. SYNCHRONY: a capture-phase click listener arms a setTimeout(0) sentinel;
 *      share() must be called before it fires — no await between tap and sheet;
 *   5. CANCEL: with share() rejecting AbortError, zero clipboard writes, no
 *      message, button re-enabled; FAILURE: with share() rejecting anything
 *      else, zero clipboard writes and the button reads "Tap Copy" for ~2s,
 *      then "Send" again; RE-ENTRANCY: with share() hanging, a second tap does
 *      not call it again and the button is disabled until the first settles;
 *   6. LANGUAGE: <html lang="es"> relabels it "Enviar"; back to "Send" on "en";
 *   7. ABSENT: a second context with NO share stub (headless Chromium's own
 *      state) — no `.tk-send` in the DOM, and Copy still writes;
 *   8. no page errors in either context.
 *
 * THE NAMED EXCLUSION. Pages whose receiver is an AI chat box, not a person:
 * the write-up shelves (shared/docspec.js) and av/report-builder.html. Their
 * Copy hands the man a prompt to paste into an AI; the share sheet is the wrong
 * door for that, and the write-up bar already sits at its 320px limit (§SCARS
 * 2026-08-14). A page with a Copy path that is neither EXPECTED nor on this list
 * FAILS — the exclusion is a decision, and it is written here so it stays one.
 *
 * --prove is the negative control: the stub hands the sheet the copy text plus
 * one character, and the parity assertion must go RED on every page.
 */
import { createRequire } from 'module';
import { readdirSync, readFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..') + '/';
const args = process.argv.slice(2);
const PROVE = args.includes('--prove');
const onlyIx = args.indexOf('--only');
const ONLY = onlyIx >= 0 ? args[onlyIx + 1] : null;
const BASE = (args.find(a => /^https?:\/\//.test(a)) || 'file://' + ROOT).replace(/\/*$/, '/');

/* ── discovery: a trade is a dir with trade.js + index.html; a page is any other .html ── */
const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(join(ROOT, d.name, 'trade.js')) && existsSync(join(ROOT, d.name, 'index.html')))
  .map(d => d.name).sort();
const PAGES = ONLY ? [ONLY] : TRADES.flatMap(t =>
  readdirSync(join(ROOT, t)).filter(f => f.endsWith('.html') && f !== 'index.html' && f !== 'credits.html').sort().map(f => `${t}/${f}`));

/* Engines that register Send where they bind Copy (shared/toolkit.js header). */
const REGISTERING = ['checklist-request', 'note', 'rowlog', 'package', 'holdtest', 'whatcameback'];
/* The receiver is an AI, not a person — no Send, by decision. */
const EXCLUDED = [
  { test: src => /shared\/docspec\.js/.test(src), why: 'write-up shelf: the receiver is an AI chat box' },
  { test: (src, page) => page === 'av/report-builder.html', why: 'report builder: the receiver is an AI chat box' },
];

function classify(page) {
  const src = readFileSync(join(ROOT, page), 'utf8');
  const engines = REGISTERING.filter(e => new RegExp('shared/' + e.replace('-', '\\-') + '\\.js').test(src));
  const byHand = /ToolkitSend\(/.test(src);
  const ex = EXCLUDED.find(x => x.test(src, page));
  const hasCopyPath = engines.length > 0 || byHand || /clipboard\.writeText/.test(src) || /shared\/docspec\.js/.test(src);
  if (ex) return { kind: 'excluded', why: ex.why, engines, byHand, hasCopyPath };
  if (engines.length || byHand) return { kind: 'expected', engines, byHand, hasCopyPath };
  return { kind: hasCopyPath ? 'unlisted' : 'none', engines, byHand, hasCopyPath };
}

/* ── the stubs ────────────────────────────────────────────────────────────── */
const STUB_PRESENT = ({ prove }) => {
  window.__gate = { share: [], clip: [], mode: 'resolve', taskRan: true, prove, release: null };
  document.addEventListener('click', () => {
    window.__gate.taskRan = false;
    setTimeout(() => { window.__gate.taskRan = true; }, 0);
  }, true);
  navigator.share = function (d) {
    const rec = { keys: Object.keys(d || {}), text: d && d.text, taskRan: window.__gate.taskRan };
    if (window.__gate.prove && typeof rec.text === 'string') rec.text = rec.text + '!';
    window.__gate.share.push(rec);
    const m = window.__gate.mode;
    if (m === 'abort') { const e = new Error('cancelled'); e.name = 'AbortError'; return Promise.reject(e); }
    if (m === 'fail') { const e = new Error('no'); e.name = 'NotAllowedError'; return Promise.reject(e); }
    if (m === 'hang') return new Promise(res => { window.__gate.release = res; });
    return Promise.resolve();
  };
  const clip = { writeText: t => { window.__gate.clip.push(String(t)); return Promise.resolve(); } };
  try { Object.defineProperty(navigator, 'clipboard', { value: clip, configurable: true }); } catch (e) { try { navigator.clipboard = clip; } catch (e2) {} }
  const ec = document.execCommand ? document.execCommand.bind(document) : null;
  document.execCommand = function (cmd) {
    if (cmd === 'copy') { const a = document.activeElement; if (a && 'value' in a) window.__gate.clip.push(String(a.value)); return true; }
    return ec ? ec.apply(document, arguments) : false;
  };
};
const STUB_ABSENT = () => {
  window.__gate = { clip: [] };
  const clip = { writeText: t => { window.__gate.clip.push(String(t)); return Promise.resolve(); } };
  try { Object.defineProperty(navigator, 'clipboard', { value: clip, configurable: true }); } catch (e) { try { navigator.clipboard = clip; } catch (e2) {} }
  const ec = document.execCommand ? document.execCommand.bind(document) : null;
  document.execCommand = function (cmd) {
    if (cmd === 'copy') { const a = document.activeElement; if (a && 'value' in a) window.__gate.clip.push(String(a.value)); return true; }
    return ec ? ec.apply(document, arguments) : false;
  };
};

/* ── generic perturbation: make the document move without knowing the page ── */
const PERTURB = () => {
  const out = { filled: 0, ticked: 0, added: 0 };
  const skip = el => el.closest('.av-bar, .av-modal, .av-sheet, .fb-wrap, .tk-send') || el.disabled || el.readOnly || el.type === 'hidden';
  const fields = [...document.querySelectorAll('input, textarea')].filter(el => !skip(el) && !['checkbox', 'radio', 'button', 'submit', 'file', 'range'].includes(el.type));
  for (const el of fields.slice(0, 2)) {
    const v = (el.type === 'number' || el.inputMode === 'decimal' || el.inputMode === 'numeric') ? '12' : 'GATE C3698';
    el.focus(); el.value = v;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    out.filled++;
  }
  const tick = [...document.querySelectorAll('#list input[type=checkbox], .list input[type=checkbox], input[type=checkbox]')].find(el => !skip(el) && !el.checked);
  if (tick) { tick.click(); out.ticked++; }
  const add = [...document.querySelectorAll('#bar button, .rl-bar button, [data-add], button.add, #add, #addFind, #addRow')]
    .find(b => !skip(b) && /^\s*(\+|add|log|save|put it)/i.test(b.textContent || ''));
  if (add) { add.click(); out.added++; }
  return out;
};

/* ── the run ──────────────────────────────────────────────────────────────── */
const browser = await chromium.launch();
const fails = [];
let mounted = 0, excluded = 0, none = 0, checks = 0, moved = 0, parityPairs = 0;
const placements = { beside: 0, underPreview: 0 };
const fail = (page, msg) => { fails.push(`${page}: ${msg}`); };
const check = (page, ok, msg) => { checks++; if (!ok) fail(page, msg); return ok; };
const sleep = ms => new Promise(r => setTimeout(r, ms));

for (const page of PAGES) {
  const cls = classify(page);
  const url = BASE + page;
  if (cls.kind === 'none') { none++; continue; }
  if (cls.kind === 'unlisted') { checks++; fail(page, 'has a Copy path, mounts no Send, and is not on the named exclusion list'); continue; }

  /* PRESENT: the state every phone is in. */
  const ctx = await browser.newContext({ viewport: { width: 390, height: 780 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e).split('\n')[0]));
  p.on('dialog', d => d.dismiss().catch(() => {}));
  await p.addInitScript(STUB_PRESENT, { prove: PROVE });
  try {
    await p.goto(url, { waitUntil: 'load', timeout: 30000 });
  } catch (e) { fail(page, 'could not load: ' + e.message.split('\n')[0]); await ctx.close(); continue; }
  await p.waitForTimeout(450);

  const sends = await p.$$('.tk-send');
  if (cls.kind === 'excluded') {
    excluded++;
    check(page, sends.length === 0, `EXCLUDED (${cls.why}) but mounted ${sends.length} Send button(s)`);
    check(page, errs.length === 0, 'page error(s): ' + errs.join(' | '));
    await ctx.close();
    console.log(`  skip  ${page} — ${cls.why}`);
    continue;
  }
  if (!check(page, sends.length >= 1, `EXPECTED (${[...cls.engines, cls.byHand ? 'by hand' : ''].filter(Boolean).join(', ')}) but no .tk-send mounted`)) {
    await ctx.close(); continue;
  }
  mounted++;

  for (let i = 0; i < sends.length; i++) {
    const tag = `${page} [send #${i + 1}]`;
    /* PAIRING is stamped by the runtime (data-for = the Copy button's id), because
       Send no longer has to be Copy's neighbour: a Copy in a FIXED bar gets its
       Send in-flow under the preview (§SCARS C3698 — the bar was measured at its
       limit), a Copy in the flow gets it beside. Both placements are asserted. */
    const state = await p.evaluate(i => {
      const s = document.querySelectorAll('.tk-send')[i];
      const c = document.getElementById(s.getAttribute('data-for') || '');
      const r = s.getBoundingClientRect();
      /* fixed-ness is READ off computed style up the tree, exactly as the runtime
         reads it — av/consumables keeps Copy in a fixed `.dock`, not a `.bar` */
      const inFixed = el => { for (let a = el; a && a !== document.body; a = a.parentElement) if (getComputedStyle(a).position === 'fixed') return true; return false; };
      const copyFixed = !!c && inFixed(c);
      const sendFixed = inFixed(s);
      const row = s.parentElement && s.parentElement.classList.contains('tk-sendrow') ? s.parentElement : null;
      const prev = row ? row.previousElementSibling : null;
      return {
        copyTag: c && c.tagName, copyDisabled: !!(c && c.disabled), sendDisabled: s.disabled, label: s.textContent, h: r.height, w: r.width,
        copyFixed, sendFixed, beside: c && c.nextElementSibling === s,
        underPreview: !!(row && prev && /preview/i.test((prev.id || '') + ' ' + (prev.className || ''))),
      };
    }, i);
    check(tag, state.copyTag === 'BUTTON', `Send is not paired with a BUTTON (data-for resolves to: ${state.copyTag})`);
    check(tag, !state.sendFixed, 'Send sits inside a FIXED bar — the placement the measurement killed');
    if (state.copyFixed) check(tag, state.underPreview, 'Copy is in a fixed bar, so Send must sit in a .tk-sendrow directly under the preview — it does not');
    else check(tag, state.beside, 'Copy is in the flow, so Send must be its next sibling — it is not');
    check(tag, state.label === 'Send', `label reads "${state.label}", not "Send"`);
    check(tag, state.sendDisabled === state.copyDisabled, `disabled mismatch: Copy ${state.copyDisabled}, Send ${state.sendDisabled}`);
    check(tag, state.h >= 44 - 0.5 && state.w >= 44 - 0.5, `tap target ${Math.round(state.w)}×${Math.round(state.h)}px, under 44`);
    placements[state.copyFixed ? 'underPreview' : 'beside']++;
    /* one PARITY round: Copy, then Send, compare */
    const round = async name => {
      const before = await p.evaluate(() => ({ c: window.__gate.clip.length, s: window.__gate.share.length }));
      const disabled = await p.evaluate(i => { const s = document.querySelectorAll('.tk-send')[i]; return s.disabled || document.getElementById(s.getAttribute('data-for')).disabled; }, i);
      if (disabled) return { skipped: true };
      await p.evaluate((i, sel) => { const c = document.getElementById(document.querySelectorAll('.tk-send')[i].getAttribute('data-for')); c.scrollIntoView({ block: 'center' }); c.click(); }, i);
      await sleep(120);
      await p.evaluate(i => { const s = document.querySelectorAll('.tk-send')[i]; s.scrollIntoView({ block: 'center' }); s.click(); }, i);
      await sleep(120);
      const g = await p.evaluate(() => window.__gate);
      const clipText = g.clip[g.clip.length - 1];
      const share = g.share[g.share.length - 1];
      parityPairs++;
      check(tag, g.clip.length === before.c + 1, `${name}: Copy wrote ${g.clip.length - before.c} time(s), expected 1`);
      if (!check(tag, g.share.length === before.s + 1, `${name}: Send called share() ${g.share.length - before.s} time(s), expected 1`)) return { skipped: true };
      check(tag, JSON.stringify(share.keys) === '["text"]', `${name}: payload keys ${JSON.stringify(share.keys)}, expected ["text"]`);
      check(tag, typeof share.text === 'string' && share.text === clipText, `${name}: share text ≠ clipboard text (${(share.text || '').length} vs ${(clipText || '').length} chars)`);
      check(tag, share.taskRan === false, `${name}: share() was called after the tap's task ended — an await sits between the tap and the sheet`);
      check(tag, typeof clipText === 'string' && clipText.trim().length > 0, `${name}: the document is empty`);
      return { clipText };
    };

    const r0 = await round('empty');
    const pert = await p.evaluate(PERTURB);
    await sleep(350);
    const r1 = await round('filled');
    if (r1.skipped && r0.skipped) fail(tag, `Copy stayed disabled through the perturbation (${JSON.stringify(pert)}) — parity never measured`);
    if (!r0.skipped && !r1.skipped && r0.clipText !== r1.clipText) moved++;

    /* CANCEL */
    await p.evaluate(() => { window.__gate.mode = 'abort'; });
    let b = await p.evaluate(() => window.__gate.clip.length);
    await p.evaluate(i => document.querySelectorAll('.tk-send')[i].click(), i);
    await sleep(150);
    let after = await p.evaluate(i => { const s = document.querySelectorAll('.tk-send')[i]; return { clip: window.__gate.clip.length, label: s.textContent, disabled: s.disabled, copyDisabled: document.getElementById(s.getAttribute('data-for')).disabled }; }, i);
    check(tag, after.clip === b, 'CANCEL wrote the clipboard');
    check(tag, after.label === 'Send', `CANCEL changed the label to "${after.label}"`);
    check(tag, after.disabled === after.copyDisabled, 'CANCEL left Send disabled');

    /* FAILURE */
    await p.evaluate(() => { window.__gate.mode = 'fail'; });
    b = await p.evaluate(() => window.__gate.clip.length);
    await p.evaluate(i => document.querySelectorAll('.tk-send')[i].click(), i);
    await sleep(150);
    after = await p.evaluate(i => { const s = document.querySelectorAll('.tk-send')[i]; return { clip: window.__gate.clip.length, label: s.textContent, disabled: s.disabled, copyDisabled: document.getElementById(s.getAttribute('data-for')).disabled }; }, i);
    check(tag, after.clip === b, 'FAILURE wrote the clipboard');
    check(tag, after.label === 'Tap Copy', `FAILURE label reads "${after.label}", expected "Tap Copy"`);
    check(tag, after.disabled === after.copyDisabled, 'FAILURE left Send disabled');
    await sleep(2150);
    after = await p.evaluate(i => document.querySelectorAll('.tk-send')[i].textContent, i);
    check(tag, after === 'Send', `FAILURE label did not return to "Send" (reads "${after}")`);

    /* RE-ENTRANCY */
    await p.evaluate(() => { window.__gate.mode = 'hang'; });
    const s0 = await p.evaluate(() => window.__gate.share.length);
    await p.evaluate(i => { const s = document.querySelectorAll('.tk-send')[i]; s.click(); s.click(); }, i);
    await sleep(80);
    const mid = await p.evaluate(i => ({ n: window.__gate.share.length, disabled: document.querySelectorAll('.tk-send')[i].disabled }), i);
    check(tag, mid.n === s0 + 1, `RE-ENTRANCY: two taps called share() ${mid.n - s0} time(s)`);
    check(tag, mid.disabled === true, 'RE-ENTRANCY: Send not disabled while the sheet is up');
    await p.evaluate(() => { if (window.__gate.release) window.__gate.release(); window.__gate.mode = 'resolve'; });
    await sleep(80);
    const rel = await p.evaluate(i => { const s = document.querySelectorAll('.tk-send')[i]; return { disabled: s.disabled, copyDisabled: document.getElementById(s.getAttribute('data-for')).disabled }; }, i);
    check(tag, rel.disabled === rel.copyDisabled, 'RE-ENTRANCY: Send stayed disabled after the sheet settled');

    /* LANGUAGE */
    await p.evaluate(() => { document.documentElement.lang = 'es'; });
    await sleep(60);
    let lab = await p.evaluate(i => document.querySelectorAll('.tk-send')[i].textContent, i);
    check(tag, lab === 'Enviar', `lang=es label reads "${lab}", expected "Enviar"`);
    await p.evaluate(() => { document.documentElement.lang = 'en'; });
    await sleep(60);
    lab = await p.evaluate(i => document.querySelectorAll('.tk-send')[i].textContent, i);
    check(tag, lab === 'Send', `lang=en label reads "${lab}", expected "Send"`);
  }
  check(page, errs.length === 0, 'page error(s) with share present: ' + errs.join(' | '));
  await ctx.close();

  /* ABSENT: headless Chromium's own state — the desktop-Firefox phone. */
  const ctx2 = await browser.newContext({ viewport: { width: 390, height: 780 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p2 = await ctx2.newPage();
  const errs2 = [];
  p2.on('pageerror', e => errs2.push(String(e).split('\n')[0]));
  p2.on('dialog', d => d.dismiss().catch(() => {}));
  await p2.addInitScript(STUB_ABSENT);
  await p2.goto(url, { waitUntil: 'load', timeout: 30000 });
  await p2.waitForTimeout(450);
  const absent = await p2.evaluate(() => ({ hasShare: typeof navigator.share === 'function', sends: document.querySelectorAll('.tk-send').length }));
  if (absent.hasShare) {
    fail(page, 'ABSENT: this browser has navigator.share natively; the absent state could not be measured here');
  } else {
    check(page, absent.sends === 0, `ABSENT: ${absent.sends} .tk-send in the DOM with no navigator.share`);
    const copied = await p2.evaluate(() => {
      const c = document.querySelector('#copy, #copyBtn, #wcbCopy') || [...document.querySelectorAll('button')].find(b => /copy/i.test(b.textContent || ''));
      if (!c) return { found: false };
      if (c.disabled) return { found: true, disabled: true };
      c.click(); return { found: true, disabled: false };
    });
    await sleep(120);
    const n = await p2.evaluate(() => window.__gate.clip.length);
    check(page, copied.found, 'ABSENT: no Copy button found');
    if (copied.found && !copied.disabled) check(page, n >= 1, 'ABSENT: Copy wrote nothing');
  }
  check(page, errs2.length === 0, 'page error(s) with share absent: ' + errs2.join(' | '));
  await ctx2.close();

  console.log(`  ${fails.some(f => f.startsWith(page)) ? 'FAIL ' : 'ok   '} ${page} — ${sends.length} Send · engines: ${cls.engines.join(',') || (cls.byHand ? 'by hand' : '—')}`);
}
await browser.close();

console.log('');
for (const f of fails) console.log('  FAIL  ' + f);
console.log(`SEND IS COPY${PROVE ? ' (--prove: the sheet was handed copy text + "!", this MUST be red)' : ''} — ${mounted} page(s) mount Send · ${excluded} excluded by name · ${none} with no Copy · ${parityPairs} parity pairs, document moved on ${moved} · placed beside Copy on ${placements.beside}, under the preview on ${placements.underPreview} · ${checks} checks · ${fails.length} failing`);
process.exit(fails.length ? 1 : 0);
