/**
 * THE START-OVER GATE — one action returns the write-up page to how it opened,
 * driven through the real page on every trade that ships the engine.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * WHY THIS EXISTS. Collage C3718 served the wish "no way to reset canvas": a
 * clear existed, three taps deep under the wrong word. The BACKPORT sweep that
 * cycle found the same class here in its purest form — every other tool page on
 * every trade carries a Clear, and shared/docspec.js carried none, so a setup
 * typed for the last company stuck to the phone until each field was emptied by
 * hand. This gate is the control's contract, so the fix cannot rot silently:
 *
 *   · pick a document, type a name, choose Claude   → a real setup on the phone
 *   · Start over is on screen, 44px, inside the viewport
 *   · ONE tap wipes nothing: the block, the name and the pick all stay, and the
 *     button says so ("Tap again to wipe it")
 *   · the SECOND tap returns the page to how it opened: no pick, no details, the
 *     library open — and the stored state agrees (doc null, more [], me "")
 *   · the AI he pastes into is kept (a preference, not a setup)
 *   · a reload after it comes back clean — the wipe reached storage, not just
 *     the screen
 *
 * TRADES COME FROM DISK, never from a list here.
 *
 *   node tools/toolkit-gates/docspec-startover.mjs [base-url] [--only=<trade>]
 *
 * Default base is the working tree (file://). Pass the live URL after a deploy.
 */
import { createRequire } from 'module';
import { readdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';

const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const args = process.argv.slice(2);
const only = (args.find(a => a.startsWith('--only=')) || '').slice(7);
const BASE = (args.find(a => !a.startsWith('--')) || 'file://' + ROOT).replace(/\/$/, '');

const TRADES = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(ROOT + d.name + '/trade.js')
                              && existsSync(ROOT + d.name + '/write-up.html'))
  .map(d => d.name)
  .filter(t => !only || t === only)
  .sort();

const W = 390, H = 844;
const browser = await chromium.launch();
let fails = 0, checks = 0;
const ok = (cond, msg) => { checks++; if (!cond) { fails++; console.log('  FAIL ' + msg); } };

for (const trade of TRADES) {
  const ctx = await browser.newContext({ viewport: { width: W, height: H } });
  const page = await ctx.newPage();
  const url = `${BASE}/${trade}/write-up.html`;
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForSelector('.lib button', { timeout: 15000 }).catch(() => null);
  const rows = await page.locator('.lib button').count();
  if (!rows) { fails++; console.log(`${trade}: FAIL no library rendered at ${url}`); await ctx.close(); continue; }

  // A real setup: a pick, a name, an AI.
  await page.locator('.lib button').first().click();
  await page.waitForSelector('pre.block', { timeout: 10000 });
  const name = page.locator('.f').filter({ has: page.locator('label', { hasText: /^Your name$/ }) }).locator('input');
  await name.fill('Test Tech');
  await page.locator('.seg button', { hasText: /^Claude$/ }).first().click();
  const stored = async () => page.evaluate(() => {
    const k = Object.keys(localStorage).find(x => /^docspec:[^:]+$/.test(x));
    return k ? JSON.parse(localStorage.getItem(k)) : null;
  });
  let s = await stored();
  ok(s && s.doc && s.me === 'Test Tech' && s.platform === 'claude', `${trade}: the setup did not reach storage (${JSON.stringify(s && { doc: s.doc, me: s.me, platform: s.platform })})`);

  // On screen, a thumb, inside the phone.
  const btn = page.getByRole('button', { name: 'Start over', exact: true });
  const n = await btn.count();
  ok(n === 1, `${trade}: Start over is not on the page (count ${n})`);
  // A page without the control fails HERE and the run goes on to the next
  // trade: a gate that dies on one trade tells you nothing about the other
  // sixteen. (Against the engine before C3718 every trade lands here.)
  if (n !== 1) { console.log(`${trade}: FAIL`); await ctx.close(); continue; }
  await btn.scrollIntoViewIfNeeded();
  const b = await btn.boundingBox();
  ok(b && b.height >= 43.5, `${trade}: Start over is ${b && b.height}px tall`);
  ok(b && b.x >= -0.5 && b.x + b.width <= W + 0.5, `${trade}: Start over leaves the viewport sideways (${b && JSON.stringify(b)})`);
  ok((await btn.textContent() || '').indexOf('Start over') === 0, `${trade}: the button does not say Start over`);

  // One tap wipes nothing.
  await btn.click();
  ok(/tap again/i.test(await btn.textContent() || ''), `${trade}: the first tap did not arm the button`);
  ok(await page.locator('pre.block').count() === 1, `${trade}: one tap removed the block`);
  ok(await name.inputValue() === 'Test Tech', `${trade}: one tap emptied the name`);
  s = await stored();
  ok(s && s.doc && s.me === 'Test Tech', `${trade}: one tap changed storage`);

  // The second tap returns the page to how it opened, and keeps the AI.
  await btn.click();
  await page.waitForTimeout(150);
  ok(await page.locator('pre.block:visible').count() === 0, `${trade}: the block is still showing after Start over`);
  ok(await page.locator('.startover:visible').count() === 0, `${trade}: the tune card is still showing after Start over`);
  const libOpen = await page.locator('.card').first().evaluate(el => getComputedStyle(el).display !== 'none');
  ok(libOpen, `${trade}: the library did not reopen after Start over`);
  s = await stored();
  ok(s && s.doc === null && Array.isArray(s.more) && s.more.length === 0 && s.me === '' && s.company === '', `${trade}: storage kept the setup (${JSON.stringify(s && { doc: s.doc, more: s.more, me: s.me })})`);
  ok(s && s.platform === 'claude', `${trade}: Start over dropped the AI preference (${s && s.platform})`);

  // And a reload agrees.
  await page.reload({ waitUntil: 'load' });
  await page.waitForSelector('.lib button', { timeout: 15000 });
  ok(await page.locator('pre.block:visible').count() === 0, `${trade}: the old setup came back on reload`);
  ok(await page.locator('.f input:visible').count() === 0, `${trade}: the details card came back on reload`);
  await ctx.close();
  console.log(`${trade}: ok`);
}
await browser.close();
console.log(`${TRADES.length} trade(s), ${checks} checks, ${fails} failed`);
process.exit(fails ? 1 : 0);
