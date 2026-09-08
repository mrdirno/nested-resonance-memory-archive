// Author: Aldrin Payopay
// SPDX-License-Identifier: GPL-3.0-only
// Local browser acceptance checks. Time and storage failures are injected only
// into isolated test contexts. No production services or external links are used.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { DEFAULT_RECIPE, validateRecipe } from './engine.mjs';

const folder = path.dirname(fileURLToPath(import.meta.url));
// Reuse an installed Playwright dependency; no package installation is performed.
// Accept a package root or package.json path. A copied experiment defaults to
// the checkout's existing tools/collage-studio package.
const dependencyRoot = path.resolve(process.env.PAGE_STUDY_PLAYWRIGHT_ROOT || path.join(folder, '../../tools/collage-studio'));
const require = createRequire(dependencyRoot.endsWith('.json') ? dependencyRoot : path.join(dependencyRoot, 'package.json'));
const { chromium } = require('playwright');
const { expect } = require('playwright/test');
const BASE = process.env.PAGE_STUDY_URL || 'http://127.0.0.1:8768';
const origin = new URL(BASE).origin;
assert.ok(['127.0.0.1', 'localhost'].includes(new URL(BASE).hostname), 'Local server required');
const evidence = path.join(folder, 'evidence');
const started = new Date();
const runId = started.toISOString().replace(/[:.]/g, '-');
await mkdir(evidence, { recursive: true });
const sourceNames = ['index.html', 'app.mjs', 'style.css', 'engine.mjs', 'browser.test.mjs'];
async function hashSources() {
  return Object.fromEntries(await Promise.all(sourceNames.map(async name => [
    name, createHash('sha256').update(await readFile(path.join(folder, name))).digest('hex'),
  ])));
}
const startingHashes = await hashSources();
const observations = { externalRequests: [], pageErrors: [], screenshots: [], tests: [], geometry: [], contrasts: [] };
const contexts = new Set();
const browser = await chromium.launch({ headless: true });
const theme = page => page.locator('html');
async function currentRecipe(page) {
  await expect(page.locator('#recipe-json')).toContainText('branch-study-v1');
  return JSON.parse(await page.locator('#recipe-json').textContent());
}
async function art(page) {
  await currentRecipe(page);
  return page.locator('#art-shapes').innerHTML();
}

async function context(options = {}) {
  const value = await browser.newContext({
    viewport: { width: 1280, height: 900 }, timezoneId: 'America/Los_Angeles',
    colorScheme: 'light', reducedMotion: 'reduce', acceptDownloads: true, ...options,
  });
  contexts.add(value);
  await value.route('**/*', async route => {
    const url = route.request().url();
    if (new URL(url).origin === origin) await route.continue();
    else {
      observations.externalRequests.push({ url, method: route.request().method(), blocked: true });
      await route.abort('blockedbyclient');
    }
  });
  value.on('page', page => page.on('pageerror', error => observations.pageErrors.push(String(error))));
  return value;
}

async function open(value, query = '') {
  const page = await value.newPage();
  await page.goto(`${BASE}/${query}`, { waitUntil: 'networkidle' });
  await expect(page.locator('#recipe-json')).toContainText('branch-study-v1');
  return page;
}

async function screenshot(page, label) {
  const name = `${runId}-${label}.png`;
  await page.screenshot({ path: path.join(evidence, name), fullPage: true, animations: 'disabled' });
  observations.screenshots.push(name);
  return name;
}

async function check(name, fn) {
  const start = Date.now();
  const entry = { name, status: 'running' };
  observations.tests.push(entry);
  try {
    await fn();
    entry.status = 'passed';
    console.log(`PASS ${name}`);
  } catch (error) {
    entry.status = 'failed';
    entry.error = String(error.stack || error);
    console.error(`FAIL ${name}\n${entry.error}`);
    for (const value of contexts) {
      for (const [index, page] of value.pages().entries()) {
        try { entry.screenshot = await screenshot(page, `failure-${observations.tests.length}-${index}`); }
        catch { /* Keep the original failure if its page is unavailable. */ }
      }
    }
  } finally {
    entry.durationMs = Date.now() - start;
    for (const value of contexts) await value.close();
    contexts.clear();
  }
}

async function assertGeometry(page, label) {
  await page.waitForLoadState('load');
  await currentRecipe(page);
  const geometry = await page.evaluate(() => {
    const rect = document.querySelector('#wish-open').getBoundingClientRect();
    return {
      viewport: innerWidth, documentWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth, wish: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    };
  });
  observations.geometry.push({ label, ...geometry });
  assert.ok(geometry.documentWidth <= geometry.viewport, `${label}: document overflow`);
  assert.ok(geometry.bodyWidth <= geometry.viewport, `${label}: body overflow`);
  assert.ok(geometry.wish.width >= 44 && geometry.wish.height >= 44, `${label}: Wish target under 44px`);
  assert.ok(geometry.wish.x >= 0 && geometry.wish.x + geometry.wish.width <= geometry.viewport, `${label}: Wish offscreen`);
  assert.ok(geometry.wish.y >= 0, `${label}: sticky Wish clipped`);
}

function contrastRatio(first, second) {
  const luminance = value => {
    const channels = value.match(/[\d.]+/g).slice(0, 3).map(Number).map(channel => {
      const normalized = channel / 255;
      return normalized <= 0.04045 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
    });
    return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
  };
  const a = luminance(first), b = luminance(second);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

async function measureContrast(page, palette, mode) {
  const pairs = await page.evaluate(() => {
    const style = selector => getComputedStyle(document.querySelector(selector));
    const paper = style('body').backgroundColor;
    const panel = style('#writing').backgroundColor;
    return [
      ['body text', style('body').color, paper, 4.5],
      ['secondary text on paper', style('#theme-explanation').color, paper, 4.5],
      ['hero text', style('.hero-copy').color, style('.hero').backgroundColor, 4.5],
      ['Wish text', style('#wish-open').color, style('#wish-open').backgroundColor, 4.5],
      ['dialog text', style('#wish-dialog').color, style('#wish-dialog').backgroundColor, 4.5],
      ['dialog secondary text', style('#wish-dialog > p').color, style('#wish-dialog').backgroundColor, 4.5],
      ['writing text', style('#writing').color, panel, 4.5],
      ['field boundary against paper', style('#writing').borderTopColor, paper, 3],
      ['field boundary against fill', style('#writing').borderTopColor, panel, 3],
    ];
  });
  for (const [name, foreground, background, minimum] of pairs) {
    observations.contrasts.push({ palette, mode, name, foreground, background, minimum, ratio: contrastRatio(foreground, background) });
  }
}

await check('explicit choices change recipe and art; recipe and SVG persist through pages and reload', async () => {
  const ctx = await context();
  const page = await open(ctx);
  const original = await currentRecipe(page);
  const originalArt = await art(page);
  await page.selectOption('#palette', 'orchard');
  const firstChange = await currentRecipe(page);
  assert.notEqual(firstChange.seed, original.seed);
  assert.notEqual(await art(page), originalArt);
  await page.selectOption('#density', 'compact');
  await page.selectOption('#typeScale', 'large');
  await page.selectOption('#motif', 'orbit');
  const changed = await currentRecipe(page);
  const changedArt = await art(page);
  assert.equal(changed.palette, 'orchard');
  assert.equal(changed.density, 'compact');
  assert.equal(changed.typeScale, 'large');
  assert.equal(changed.motif, 'orbit');
  assert.equal(await page.locator('#art-shapes ellipse').count(), 11);
  await page.reload();
  assert.deepEqual(await currentRecipe(page), changed);
  assert.equal(await art(page), changedArt);
  await page.locator('[data-view=desk]').click();
  await expect(page.locator('#desk-view')).toBeVisible();
  assert.deepEqual(await currentRecipe(page), changed);
  await page.reload();
  assert.deepEqual(await currentRecipe(page), changed);
  await page.locator('[data-view=explore]').click();
  assert.equal(await art(page), changedArt);
  await page.selectOption('#motif', 'quiet');
  await expect(page.locator('#art')).toBeHidden();
  assert.equal(await page.locator('#art-shapes').evaluate(node => node.children.length), 0);
});

await check('explicit and system appearance obey choice while preserving seed and geometry', async () => {
  const ctx = await context();
  const page = await open(ctx);
  const seed = (await currentRecipe(page)).seed;
  const before = await art(page);
  await page.selectOption('#mode', 'dark');
  await expect(theme(page)).toHaveAttribute('data-theme', 'dark');
  await page.emulateMedia({ colorScheme: 'light' });
  await expect(theme(page)).toHaveAttribute('data-theme', 'dark');
  await page.selectOption('#mode', 'light');
  await page.emulateMedia({ colorScheme: 'dark' });
  await expect(theme(page)).toHaveAttribute('data-theme', 'light');
  await page.selectOption('#mode', 'system');
  await expect(theme(page)).toHaveAttribute('data-theme', 'dark');
  await page.emulateMedia({ colorScheme: 'light' });
  await expect(theme(page)).toHaveAttribute('data-theme', 'light');
  assert.equal((await currentRecipe(page)).seed, seed);
  assert.equal(await art(page), before);
});

await check('time appearance transitions at 07:00 and 19:00 without reloading', async () => {
  for (const boundary of ['07:00:00', '19:00:00']) {
    const ctx = await context();
    const page = await ctx.newPage();
    const instant = Date.parse(`2026-09-08T${boundary}-07:00`);
    await page.clock.install({ time: instant - 10000 });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.clock.pauseAt(instant - 1);
    const before = boundary === '07:00:00' ? 'dark' : 'light';
    const after = before === 'dark' ? 'light' : 'dark';
    await expect(theme(page)).toHaveAttribute('data-theme', before);
    const beforeArt = await art(page);
    let navigations = 0;
    page.on('framenavigated', () => { navigations += 1; });
    await page.clock.runFor(1);
    await expect(theme(page)).toHaveAttribute('data-theme', after);
    assert.equal(await art(page), beforeArt);
    assert.equal(navigations, 0, 'Boundary must update without document navigation');
  }
});

for (const width of [320, 390, 1280]) {
  await check(`Wish keyboard and modal behavior, draft persistence, and layout at ${width}px`, async () => {
    const ctx = await context({ viewport: { width, height: 900 } });
    const page = await open(ctx);
    let reached = false;
    for (let step = 0; step < 8; step += 1) {
      await page.keyboard.press('Tab');
      reached = await page.locator('#wish-open').evaluate(node => node === document.activeElement);
      if (reached) break;
    }
    assert.ok(reached, 'Wish must be reachable from the start by keyboard');
    await page.keyboard.press('Enter');
    await expect(page.locator('#wish-dialog')).toBeVisible();
    await expect(page.locator('#wish-text')).toBeFocused();
    const draft = `Please keep my useful controls familiar at ${width}px.`;
    await page.locator('#wish-text').fill(draft);
    await expect(page.locator('#wish-status')).toContainText('Draft saved on this device. Not sent.');
    for (let i = 0; i < 9; i += 1) {
      await page.keyboard.press('Tab');
      // Native modal dialogs may send Tab focus through browser chrome, exposed
      // as body; no background page control may receive focus while modal.
      assert.ok(await page.evaluate(() =>
        document.querySelector('#wish-dialog').matches(':modal') &&
        (document.activeElement === document.body || document.activeElement.closest('#wish-dialog') !== null)
      ), 'Modal must prevent focus on background page controls');
    }
    await screenshot(page, `wish-${width}`);
    await page.keyboard.press('Escape');
    await expect(page.locator('#wish-open')).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(page.locator('#wish-text')).toHaveValue(draft);
    await page.keyboard.press('Escape');
    await page.locator('[data-view=desk]').click();
    await page.reload();
    await page.locator('#wish-open').click();
    await expect(page.locator('#wish-text')).toHaveValue(draft);
    await expect(page.locator('#wish-title')).toContainText('Explore');
    await page.keyboard.press('Escape');
    await page.locator('#writing').fill('One thought becomes another.\nMake room for it.');
    await expect(page.locator('#word-count')).toHaveText('8 words · 46 characters');
    await expect(page.locator('#desk-status')).toHaveText('Saved on this device.');
    await page.reload();
    await expect(page.locator('#writing')).toHaveValue('One thought becomes another.\nMake room for it.');
    await expect(page.locator('#word-count')).toHaveText('8 words · 46 characters');
    await screenshot(page, `writing-${width}`);
    for (const palette of ['tide', 'orchard', 'mineral']) {
      await page.selectOption('#palette', palette);
      for (const mode of ['light', 'dark']) {
        await page.selectOption('#mode', mode);
        await assertGeometry(page, `${width}-${palette}-${mode}-desk`);
        await expect(page.locator('#palette')).toHaveValue(palette);
        await expect(theme(page)).toHaveAttribute('data-theme', mode);
        if (width === 1280) await measureContrast(page, palette, mode);
        await page.locator('[data-view=explore]').click();
        await assertGeometry(page, `${width}-${palette}-${mode}-explore`);
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await assertGeometry(page, `${width}-${palette}-${mode}-scrolled`);
        if (palette === 'tide') await screenshot(page, `explore-${mode}-${width}`);
        await page.locator('[data-view=desk]').click();
        await page.waitForLoadState('load');
        await currentRecipe(page);
      }
    }
  });
}

await check('computed ordinary text and Wish contrast reach 4.5; input boundaries reach 3', async () => {
  assert.equal(observations.contrasts.length, 54, 'All 3 palettes × 2 themes × 9 pairs must be measured');
  const failures = observations.contrasts.filter(value => value.ratio < value.minimum);
  assert.deepEqual(failures.map(({ palette, mode, name, ratio, minimum }) => ({ palette, mode, name, ratio: Number(ratio.toFixed(3)), minimum })), []);
});

await check('malformed and unknown imports leave recipe intact; exported recipe contains JSON only', async () => {
  const ctx = await context();
  const page = await open(ctx);
  await page.selectOption('#palette', 'mineral');
  await page.locator('.recipe-details summary').click();
  const before = await currentRecipe(page);
  const beforeArt = await art(page);
  for (const [name, content] of [
    ['malformed.json', '{'], ['array.json', '[]'],
    ['unknown.json', JSON.stringify({ ...before, script: 'document.body.remove()' })],
    ['version.json', JSON.stringify({ ...before, version: 9 })],
    ['seed.json', JSON.stringify({ ...before, seed: -1 })],
  ]) {
    await page.locator('#import-file').setInputFiles({ name, mimeType: 'application/json', buffer: Buffer.from(content) });
    await expect(page.locator('#save-status')).toContainText('not a supported page recipe');
    assert.deepEqual(await currentRecipe(page), before);
    assert.equal(await art(page), beforeArt);
    assert.deepEqual(await page.evaluate(() => JSON.parse(localStorage.getItem('page-study.recipe.v1'))), before);
  }
  await page.locator('#import-file').setInputFiles({ name: 'large.json', mimeType: 'application/json', buffer: Buffer.alloc(16385, 32) });
  await expect(page.locator('#save-status')).toContainText('smaller than 16 KB');
  const [download] = await Promise.all([page.waitForEvent('download'), page.locator('#export').click()]);
  assert.equal(download.suggestedFilename(), 'my-page-recipe.json');
  const contents = await readFile(await download.path(), 'utf8');
  const exported = JSON.parse(contents);
  assert.deepEqual(validateRecipe(exported), before);
  assert.equal(contents, JSON.stringify(before, null, 2));
  assert.ok(!contents.includes('<script'));
  await page.locator('#import-file').setInputFiles({ name: 'valid.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify({ ...DEFAULT_RECIPE, seed: 65537 })) });
  await expect(page.locator('#save-status')).toContainText('Recipe opened and saved');
  assert.equal((await currentRecipe(page)).seed, 65537);
});

await check('storage failures preserve working controls and never claim a successful save', async () => {
  const ctx = await context();
  await ctx.addInitScript(() => {
    Storage.prototype.getItem = function () { throw new DOMException('Test storage denied', 'SecurityError'); };
    Storage.prototype.setItem = function () { throw new DOMException('Test storage denied', 'QuotaExceededError'); };
  });
  const page = await open(ctx);
  await expect(page.locator('#save-status')).toContainText('could not be read');
  await page.selectOption('#palette', 'orchard');
  assert.equal((await currentRecipe(page)).palette, 'orchard');
  await expect(page.locator('#save-status')).toHaveText('Storage is unavailable. You can still save a file.');
  await page.locator('#wish-open').click();
  await page.locator('#wish-text').fill('Still usable while storage is unavailable.');
  await expect(page.locator('#wish-status')).toHaveText('Storage is unavailable. You can still save a file.');
  await page.keyboard.press('Escape');
  await page.locator('[data-view=desk]').click();
  await page.locator('#writing').fill('Keep this thought.');
  await expect(page.locator('#desk-status')).toHaveText('Storage is unavailable. You can still save a file.');
  await expect(page.locator('#word-count')).toContainText('3 words');
  const [download] = await Promise.all([page.waitForEvent('download'), page.locator('#download-writing').click()]);
  assert.equal(await readFile(await download.path(), 'utf8'), 'Keep this thought.');
  await screenshot(page, 'storage-unavailable');
});

await check('cross-tab changes update existing tabs and reject unsupported recipes', async () => {
  const ctx = await context();
  const first = await open(ctx);
  const second = await open(ctx, '?view=desk');
  await first.selectOption('#palette', 'orchard');
  await first.selectOption('#mode', 'dark');
  await expect(second.locator('#palette')).toHaveValue('orchard');
  await expect(theme(second)).toHaveAttribute('data-theme', 'dark');
  assert.deepEqual(await currentRecipe(second), await currentRecipe(first));
  await expect(second.locator('#save-status')).toContainText('updated from another tab');
  const before = await currentRecipe(second);
  await first.evaluate(() => localStorage.setItem('page-study.recipe.v1', JSON.stringify({ version: 666, css: '*' })));
  await expect(second.locator('#save-status')).toContainText('unsupported recipe');
  assert.deepEqual(await currentRecipe(second), before);
  await first.evaluate(() => localStorage.removeItem('page-study.recipe.v1'));
  await expect(second.locator('#palette')).toHaveValue(DEFAULT_RECIPE.palette);
  assert.deepEqual(await currentRecipe(second), DEFAULT_RECIPE);
});

await check('no unexpected external network or uncaught browser errors occurred', async () => {
  assert.deepEqual(observations.externalRequests, []);
  assert.deepEqual(observations.pageErrors, []);
});

const hashes = await hashSources();
await check('source files remained unchanged throughout the browser run', async () => {
  assert.deepEqual(hashes, startingHashes);
});
const receipt = {
  schema: 'page-study-browser-evidence/v1', author: 'Aldrin Payopay', license: 'GPL-3.0-only',
  runId, startedAt: started.toISOString(), finishedAt: new Date().toISOString(),
  url: BASE, browser: browser.version(), playwright: require('playwright/package.json').version,
  environment: { timezone: 'America/Los_Angeles', headless: true, reducedMotion: true },
  scope: 'Local preview only. Does not establish production deployment, account sync, AI service integration, or customer adoption.',
  injections: ['Playwright clock for exact boundaries', 'Storage getItem/setItem exceptions in an isolated context', 'Invalid local recipe input'],
  passed: observations.tests.filter(test => test.status === 'passed').length,
  failed: observations.tests.filter(test => test.status === 'failed').length,
  sourceSHA256: startingHashes, endingSourceSHA256: hashes,
  sourceStable: JSON.stringify(hashes) === JSON.stringify(startingHashes), ...observations,
};
await writeFile(path.join(evidence, `receipt-${runId}.json`), `${JSON.stringify(receipt, null, 2)}\n`);
await writeFile(path.join(evidence, 'receipt.json'), `${JSON.stringify(receipt, null, 2)}\n`);
await browser.close();
console.log(JSON.stringify({ passed: receipt.passed, failed: receipt.failed, evidence: path.join(evidence, 'receipt.json') }));
process.exitCode = receipt.failed ? 1 : 0;
