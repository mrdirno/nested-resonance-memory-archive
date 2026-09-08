// Author: Aldrin Payopay · GPL-3.0-only
// Portable originals are proved through real downloaded archives and reopened sound.
// Run serially with --project=chromium --project="Mobile Chrome". The project
// config supplies --mute-audio: tests must never play tones through the speakers.
import { test, expect, type Page, type Download } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import JSZip from 'jszip';
import { measureTones, toneEnvelope, HZ_CONTROL } from './tone-measure';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const URL = process.env.COLLAGE_BASE_URL || '/';
const MUSIC = 'music_thirds.m4a', VIDEO_MUSIC = 'tone_a.mp4';
const MEMBER = 'soundtrack/original';
const fixture = (name: string) => path.join(ROOT, 'tests/fixtures', name);
const musicInput = (page: Page) => page.locator('input[type=file][accept*="audio"]');
const errors = new WeakMap<Page, string[]>();
const hash = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex');
type Archive = { bytes: Buffer; zip: JSZip; manifest: any };

test.setTimeout(180_000);
test.beforeEach(async ({ page, browserName }) => {
  test.skip(browserName !== 'chromium', 'Audio fixtures run only in Chromium with --mute-audio.');
  const observed: string[] = []; errors.set(page, observed);
  page.on('pageerror', e => observed.push(e.message));
  await page.route('**/cdn.jsdelivr.net/**', route => route.abort());
});
test.afterEach(async ({ page }) => {
  expect((errors.get(page) || []).filter(message => !/service ?worker/i.test(message))).toEqual([]);
});

async function boot(page: Page) {
  await page.goto(URL);
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles([fixture('img_a.jpg'), fixture('img_b.jpg')]);
  await expect(page.getByTestId('studio-artwork')).toBeVisible({ timeout: 60_000 });
}
async function details(page: Page) {
  const toggle = page.getByRole('button', { name: 'Details', exact: true });
  await expect(toggle).toBeVisible();
  if (await toggle.getAttribute('aria-expanded') !== 'true') await toggle.click();
}
async function addMusic(page: Page, name = MUSIC) {
  await musicInput(page).setInputFiles(fixture(name));
  await details(page);
  await expect(page.getByRole('button', { name: `Trim ${name}`, exact: true })).toBeEnabled({ timeout: 30_000 });
}
async function chooseStill(page: Page) {
  await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Motion', exact: true }).click();
  await page.getByTestId('move-still').click();
  await expect(page.getByTestId('move-still')).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: 'Close editing panel', exact: true }).click();
}
async function setMusicEdit(page: Page, name = MUSIC, end = 4, start = 2, level = 'quarter', fade = '0.5') {
  await details(page);
  await page.getByRole('button', { name: `Trim ${name}`, exact: true }).click();
  const sheet = page.getByRole('dialog', { name: `Trim ${name}`, exact: true });
  await sheet.getByLabel(`Out point for ${name}`, { exact: true }).fill(String(end));
  await sheet.getByLabel(`In point for ${name}`, { exact: true }).fill(String(start));
  await sheet.getByTestId(`level-${level}`).click();
  await sheet.getByTestId(`window-fade-${fade}`).click();
  await sheet.getByRole('button', { name: 'Close trim', exact: true }).click();
}
async function downloadBytes(download: Download) {
  const stream = await download.createReadStream();
  if (!stream) throw Error('Save produced no readable download');
  const chunks: Buffer[] = []; for await (const chunk of stream) chunks.push(chunk as Buffer);
  return Buffer.concat(chunks);
}
async function save(page: Page): Promise<Archive> {
  // Focus a button so editable controls cannot consume the save shortcut.
  await page.getByRole('button', { name: 'Open', exact: true }).focus();
  const downloaded = page.waitForEvent('download', { timeout: 30_000 });
  await page.keyboard.press('Control+s');
  const bytes = await downloadBytes(await downloaded), zip = await JSZip.loadAsync(bytes);
  return { bytes, zip, manifest: JSON.parse(await zip.file('manifest.json')!.async('text')) };
}
async function open(page: Page, bytes: Buffer, name = 'portable-music.collage') {
  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Open', exact: true }).click();
  await (await chooser).setFiles({ name, mimeType: 'application/zip', buffer: bytes });
}
async function originalImages(a: Archive) {
  return Promise.all(a.manifest.images.map(async (image: any) => ({
    id: image.id, name: image.originalName,
    hash: hash(await a.zip.file('images/' + image.storageFilename)!.async('nodebuffer')),
  })));
}
async function editedArchive(a: Archive, change: (manifest: any, zip: JSZip) => void) {
  const zip = await JSZip.loadAsync(a.bytes), manifest = JSON.parse(await zip.file('manifest.json')!.async('text'));
  change(manifest, zip); zip.file('manifest.json', JSON.stringify(manifest));
  return zip.generateAsync({ type: 'nodebuffer' });
}
async function trackIdentity(page: Page) {
  return page.locator('audio').first().evaluate(async (audio: HTMLAudioElement) => {
    const bytes = await (await fetch(audio.src)).arrayBuffer();
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))).map(x => x.toString(16).padStart(2, '0')).join('');
    return { url: audio.src, hash: digest, paused: audio.paused, muted: audio.muted, time: audio.currentTime };
  });
}
async function expectTrackAdvancing(page: Page, url: string) {
  let previous: number | null = null, advanced = 0, movingSamples = 0;
  await expect.poll(async () => {
    const state = await page.evaluate(() => {
      const audio = document.querySelector('audio');
      return audio ? { url: audio.src, paused: audio.paused, muted: audio.muted, time: audio.currentTime } : null;
    });
    if (!state || state.url !== url || state.paused || state.muted) {
      previous = null; advanced = 0; movingSamples = 0; return false;
    }
    // Samples across an ordinary source-window wrap may move backwards. Only
    // real forward clock movement counts; the seek itself cannot pass this.
    const delta = previous === null ? 0 : state.time - previous;
    previous = state.time;
    if (delta > .005 && delta < .75) { advanced += delta; movingSamples++; }
    return movingSamples >= 2 && advanced > .15;
  }, { timeout: 8_000, intervals: [100, 100, 150, 200], message: 'the same unmuted source must resume and advance without another Play gesture' }).toBe(true);
}

for (const name of [MUSIC, VIDEO_MUSIC]) {
  test(`portable original and edits round trip: ${name}`, async ({ page }, info) => {
    await boot(page); const photos = await originalImages(await save(page));
    await chooseStill(page);
    await addMusic(page, name);
    await setMusicEdit(page, name, name === MUSIC ? 4 : 1.6, name === MUSIC ? 2 : .4);
    if (name === VIDEO_MUSIC) {
      // Capture BOTH source mute intents, separately from the monitor state.
      const hear = page.getByRole('button', { name: /^Hear the music,/ });
      if (await hear.count()) await hear.click();
      await page.getByRole('button', { name: /^Mute the music,/ }).click();
    }
    const first = await save(page);
    // Written before the assertion: the expected red baseline leaves a small,
    // sanitized receipt proving exactly what the real public writer omitted.
    await fs.writeFile(info.outputPath('archive-receipt.json'), JSON.stringify({
      source: name, expectedOriginalHash: hash(await fs.readFile(fixture(name))),
      members: Object.keys(first.zip.files), soundtrack: first.manifest.soundtrack ?? null,
    }, null, 2));
    expect(first.manifest.soundtrack, 'manual project must carry the selected music original and authored edits').toBeDefined();
    const meta = first.manifest.soundtrack;
    expect(meta).toMatchObject({ version: 1, storageFilename: 'original', originalName: name, level: .25,
      inSec: name === MUSIC ? 2 : .4, outSec: name === MUSIC ? 4 : 1.6, fadeSec: .5, muted: name === VIDEO_MUSIC });
    expect(first.manifest.layout.move).toBe('still');
    expect(hash(await first.zip.file(MEMBER)!.async('nodebuffer'))).toBe(hash(await fs.readFile(fixture(name))));
    expect(meta.sha256).toBe(hash(await fs.readFile(fixture(name))));
    expect(JSON.stringify(meta)).not.toMatch(/blob:|soundOn|soloId/);
    await page.reload(); await expect(page.getByRole('button', { name: 'Open', exact: true })).toBeVisible();
    // The shell has loaded. This proves reopening embedded media requires no
    // network; it deliberately makes no claim about a cold offline installation.
    await page.context().setOffline(true);
    try {
      expect(await page.evaluate(() => navigator.onLine)).toBe(false);
      await open(page, first.bytes);
      await expect(page.getByTestId('studio-artwork')).toBeVisible(); await details(page);
      await expect(page.getByRole('button', { name: `Trim ${name}`, exact: true })).toBeEnabled();
      await expect(page.getByRole('button', { name: 'Unmute preview', exact: true })).toBeVisible();
      await expect(page.getByTestId('solo-banner')).toHaveCount(0);
      expect((await trackIdentity(page)).muted, 'Open keeps saved intent but starts the monitor off').toBe(true);
      const second = await save(page);
      expect(second.manifest.soundtrack).toEqual(meta);
      expect(second.manifest.layout.move).toBe('still');
      expect(await originalImages(second)).toEqual(photos);
      expect(hash(await second.zip.file(MEMBER)!.async('nodebuffer'))).toBe(meta.sha256);
      expect((await trackIdentity(page)).hash).toBe(meta.sha256);
      if (name === MUSIC) await page.screenshot({ path: info.outputPath('reopened-project.png') });
    } finally { await page.context().setOffline(false); }
  });
}

test('reopened export contains only the middle tone at the saved level and fades each lap', async ({ page }, info) => {
  test.setTimeout(360_000);
  await boot(page); await addMusic(page); await setMusicEdit(page);
  const archive = await save(page); await page.reload(); await open(page, archive.bytes);
  await details(page); await expect(page.getByRole('button', { name: `Trim ${MUSIC}`, exact: true })).toBeEnabled();
  const originalRms = await page.locator('audio').first().evaluate(async (audio: HTMLAudioElement) => {
    const bytes = await (await fetch(audio.src)).arrayBuffer();
    const context = new OfflineAudioContext(1, 1, 48_000), decoded = await context.decodeAudioData(bytes);
    const samples = decoded.getChannelData(0).subarray(Math.round(3 * decoded.sampleRate), Math.round(3.06 * decoded.sampleRate));
    return Math.sqrt(samples.reduce((sum, v) => sum + v * v, 0) / samples.length);
  });
  expect(originalRms).toBeGreaterThan(.01);
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Export', exact: true });
  // This is an audio proof: the smallest supported video avoids an irrelevant 4K load.
  const supported = dialog.locator('[role=radio]:not([disabled])');
  if (await supported.count()) await supported.first().click();
  await dialog.getByRole('button', { name: '5s', exact: true }).click();
  await dialog.getByRole('button', { name: 'Record 5s video', exact: true }).click();
  await expect(page.locator('video[controls]')).toBeVisible({ timeout: 240_000 });
  const recorded = page.getByRole('dialog', { name: 'Recorded take', exact: true });
  const artifactDownload = page.waitForEvent('download');
  await recorded.getByRole('button', { name: /^(Download|Save)$/ }).click();
  const artifact = await artifactDownload;
  const artifactPath = info.outputPath('reopened-music' + path.extname(artifact.suggestedFilename()));
  await artifact.saveAs(artifactPath);
  await info.attach('reopened music video', { path: artifactPath, contentType: artifact.suggestedFilename().endsWith('.mp4') ? 'video/mp4' : 'video/webm' });
  const tone = await measureTones(page, [900, 1500, 2300], HZ_CONTROL);
  expect(tone.ok, tone.reason).toBe(true); expect(tone.durationSec).toBeGreaterThan(4.7);
  expect(tone.bins[1]).toBeGreaterThan(Math.max(tone.control, tone.bins[0], tone.bins[2], 1e-7) * 10);
  const envelope = await toneEnvelope(page, 1500, .06);
  expect(envelope.ok, envelope.reason).toBe(true);
  const at = (t: number) => envelope.slices.reduce((best, slice) => Math.abs(slice.t + .03 - t) < Math.abs(best.t + .03 - t) ? slice : best);
  const plateau = (at(1).rms + at(3).rms) / 2;
  const gain = plateau / originalRms;
  expect(gain, '25% must reach the reopened export exactly once').toBeGreaterThan(.18);
  expect(gain).toBeLessThan(.33);
  for (const join of [2, 4]) expect(at(join).rms / plateau, `saved fade must close the lap at ${join}s`).toBeLessThan(.3);
  expect(at(2.8).rms / plateau).toBeGreaterThan(.8);
  await fs.writeFile(info.outputPath('reopened-audio-measurement.json'), JSON.stringify({ tone, originalRms, gain, envelope }, null, 2));
});

test('unreadable music refuses Save without a partial download and permits retry', async ({ page }) => {
  await boot(page); await addMusic(page); await setMusicEdit(page);
  const before = await trackIdentity(page); let downloads = 0;
  page.on('download', () => downloads++);
  await page.evaluate(url => {
    const w = window as any; w.projectMusicFetch = window.fetch;
    window.fetch = (input, init) => input === url ? Promise.reject(Error('Injected soundtrack read failure')) : w.projectMusicFetch(input, init);
  }, before.url);
  try {
    await page.getByRole('button', { name: 'Open', exact: true }).focus(); await page.keyboard.press('Control+s');
    await expect(page.locator('[role=status]').filter({ hasText: /could not save|could not be read/i }).first()).toBeVisible();
    expect(downloads).toBe(0);
  } finally {
    await page.evaluate(() => { window.fetch = (window as any).projectMusicFetch; delete (window as any).projectMusicFetch; });
  }
  const after = await trackIdentity(page); expect(after.url).toBe(before.url); expect(after.hash).toBe(before.hash);
  const saved = await save(page); expect(saved.manifest.soundtrack).toMatchObject({ inSec: 2, outSec: 4, level: .25, fadeSec: .5 });
  expect(hash(await saved.zip.file(MEMBER)!.async('nodebuffer'))).toBe(before.hash);
});

test('bad music archives refuse atomically while the current project and source keep playing', async ({ page }) => {
  await boot(page); await addMusic(page); await setMusicEdit(page);
  const valid = await save(page);
  const variants: Array<[string, (manifest: any, zip: JSZip) => void]> = [
    ['missing-music', (_m, zip) => { zip.remove(MEMBER); }],
    ['corrupt-music', (_m, zip) => { zip.file(MEMBER, Buffer.from('not the saved original')); }],
    ['invalid-music-metadata', m => { m.soundtrack.inSec = -1; }],
    ['invalid-layout', m => { delete m.layout; m.captions = { cues: [], place: 'bc', size: 'md' }; }],
  ];
  for (const [name, corrupt] of variants) {
    // A fresh successful open clears the prior refusal; an old error cannot
    // satisfy the next check before that file has actually finished opening.
    await page.reload(); await open(page, valid.bytes); await details(page);
    await expect(page.getByRole('button', { name: `Trim ${MUSIC}`, exact: true })).toBeEnabled();
    await page.getByRole('button', { name: 'Unmute preview', exact: true }).click();
    const play = page.getByRole('button', { name: 'Play clips', exact: true }); if (await play.count()) await play.click();
    await expectTrackAdvancing(page, (await trackIdentity(page)).url);
    const before = await trackIdentity(page), beforeArchive = await save(page);
    await expect(page.getByText(/couldn't open|could not open/i).first()).toHaveCount(0);
    await open(page, await editedArchive(valid, corrupt), name + '.collage');
    await expect(page.getByText(/couldn't open|could not open/i).first()).toBeVisible();
    const after = await trackIdentity(page);
    expect(after.url, name).toBe(before.url); expect(after.hash, name).toBe(before.hash);
    await expect(page.getByRole('button', { name: 'Pause clips', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Mute preview', exact: true })).toBeVisible();
    await expectTrackAdvancing(page, before.url);
    const afterArchive = await save(page);
    expect(afterArchive.manifest, name).toEqual(beforeArchive.manifest);
    expect(await originalImages(afterArchive), name).toEqual(await originalImages(beforeArchive));
  }
});

test('legacy project without music clears the previous soundtrack and remains portable', async ({ page }) => {
  await boot(page); const legacy = await save(page), originals = await originalImages(legacy);
  expect(legacy.manifest.soundtrack).toBeUndefined();
  await addMusic(page); const previous = await trackIdentity(page);
  await open(page, legacy.bytes, 'legacy-without-music.collage');
  await expect(page.locator('audio')).toHaveCount(0);
  const saved = await save(page); expect(saved.manifest.soundtrack).toBeUndefined();
  expect(saved.zip.file(MEMBER)).toBeNull(); expect(await originalImages(saved)).toEqual(originals);
  expect(await page.evaluate(async url => { try { return (await fetch(url)).ok; } catch { return false; } }, previous.url)).toBe(false);
});

// Pause the actual file read handed to JSZip, never replace loadProject or
// application state. Both Blob APIs are covered because JSZip uses FileReader
// today; a future reader may use arrayBuffer. Auto-release bounds failed runs.
async function gateOpen(page: Page, name: string) {
  await page.evaluate(filename => {
    const w = window as any, originalReader = FileReader.prototype.readAsArrayBuffer, originalArray = Blob.prototype.arrayBuffer;
    let releaseRead = () => {}, gated = false;
    const gate = w.projectMusicGate = { hit: false, expired: false, released: false, completed: false, release: () => {} };
    const matches = (blob: Blob) => !gated && blob instanceof File && blob.name === filename;
    const timer = setTimeout(() => { gate.expired = true; gate.release(); }, 45_000);
    FileReader.prototype.readAsArrayBuffer = function(blob: Blob) {
      if (!matches(blob)) return originalReader.call(this, blob);
      gated = gate.hit = true;
      this.addEventListener('loadend', () => { gate.completed = true; }, { once: true });
      releaseRead = () => originalReader.call(this, blob);
    };
    Blob.prototype.arrayBuffer = function() {
      if (!matches(this)) return originalArray.call(this);
      gated = gate.hit = true;
      return new Promise<ArrayBuffer>((resolve, reject) => {
        releaseRead = () => { originalArray.call(this).then(resolve, reject).finally(() => { gate.completed = true; }); };
      });
    };
    gate.release = () => {
      if (gate.released) return; gate.released = true; clearTimeout(timer);
      FileReader.prototype.readAsArrayBuffer = originalReader; Blob.prototype.arrayBuffer = originalArray; releaseRead();
    };
  }, name);
}
async function waitGate(page: Page) {
  await expect.poll(() => page.evaluate(() => !!(window as any).projectMusicGate?.hit), { timeout: 10_000 }).toBe(true);
}
async function releaseGate(page: Page) {
  await page.evaluate(() => (window as any).projectMusicGate.release());
  await expect.poll(() => page.evaluate(() => !!(window as any).projectMusicGate?.completed)).toBe(true);
  expect(await page.evaluate(() => (window as any).projectMusicGate.expired)).toBe(false);
  // Let JSZip decompression and its digest settle. The fixture is tiny and this
  // wait is a bounded negative assertion window, not a substitute for readiness.
  await page.waitForTimeout(750);
}

test('a delayed older Open cannot replace a newer project or retain its music URL', async ({ page }) => {
  await boot(page); await addMusic(page); await setMusicEdit(page); const a = await save(page);
  await addMusic(page, VIDEO_MUSIC); const b = await save(page);
  const oldBUrl = (await trackIdentity(page)).url;
  await gateOpen(page, 'older-a.collage'); await open(page, a.bytes, 'older-a.collage'); await waitGate(page);
  await open(page, b.bytes, 'newer-b.collage'); await details(page);
  await expect(page.getByRole('button', { name: `Trim ${VIDEO_MUSIC}`, exact: true })).toBeEnabled();
  await expect.poll(async () => (await trackIdentity(page)).url).not.toBe(oldBUrl);
  // Wait for the committed identity, not the B song already present before Open.
  const bBefore = await save(page); expect(bBefore.manifest.soundtrack.sha256).toBe(b.manifest.soundtrack.sha256);
  const current = await trackIdentity(page);
  await releaseGate(page);
  expect((await trackIdentity(page)).url).toBe(current.url);
  expect((await save(page)).manifest.soundtrack).toEqual(b.manifest.soundtrack);
});

test('Clear and a new music selection each invalidate a delayed Open', async ({ page }) => {
  await boot(page); await addMusic(page); const a = await save(page);
  await gateOpen(page, 'before-clear.collage'); await open(page, a.bytes, 'before-clear.collage'); await waitGate(page);
  await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Add', exact: true }).click();
  await page.getByRole('button', { name: 'New canvas', exact: true }).click();
  await page.getByRole('button', { name: 'Start over', exact: true }).click();
  await expect(page.getByTestId('studio-artwork')).toHaveCount(0);
  await releaseGate(page);
  await expect(page.getByTestId('studio-artwork')).toHaveCount(0); await expect(page.locator('audio')).toHaveCount(0);
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles([fixture('img_a.jpg')]);
  await expect(page.getByTestId('studio-artwork')).toBeVisible();
  await gateOpen(page, 'before-replace.collage'); await open(page, a.bytes, 'before-replace.collage'); await waitGate(page);
  await addMusic(page, VIDEO_MUSIC); const current = await trackIdentity(page);
  await releaseGate(page);
  expect((await trackIdentity(page)).url).toBe(current.url);
  const saved = await save(page); expect(saved.manifest.images).toHaveLength(1);
  expect(saved.manifest.soundtrack.originalName).toBe(VIDEO_MUSIC); expect(saved.manifest.soundtrack.sha256).toBe(current.hash);
});

test('Open reprobes an unknown music duration and preserves authored Still when music is replaced', async ({ page }) => {
  await boot(page); await chooseStill(page); await addMusic(page); await setMusicEdit(page);
  const saved = await save(page);
  expect(saved.manifest.layout.move).toBe('still');
  const originalHash = hash(await saved.zip.file(MEMBER)!.async('nodebuffer'));
  // Duration is a label/probe hint, not the source's identity. A save made
  // before metadata arrives must reopen the same bytes and acquire its length.
  const unknownLength = await editedArchive(saved, manifest => { manifest.soundtrack.durationSec = 0; });
  await page.reload(); await open(page, unknownLength, 'unknown-duration.collage');
  await details(page);
  await expect(page.getByRole('button', { name: `Trim ${MUSIC}`, exact: true })).toBeEnabled({ timeout: 30_000 });
  const reprobed = await save(page);
  expect(reprobed.manifest.soundtrack.durationSec).toBeGreaterThan(5.8);
  expect(reprobed.manifest.soundtrack.durationSec).toBeLessThan(6.3);
  expect(hash(await reprobed.zip.file(MEMBER)!.async('nodebuffer'))).toBe(originalHash);
  expect(reprobed.manifest.soundtrack).toMatchObject({ inSec: 2, outSec: 4, level: .25, fadeSec: .5 });
  expect(reprobed.manifest.layout.move).toBe('still');
  await addMusic(page, VIDEO_MUSIC);
  const replacement = await save(page);
  expect(replacement.manifest.soundtrack.originalName).toBe(VIDEO_MUSIC);
  expect(replacement.manifest.layout.move, 'the saved Still choice remains owned after Open').toBe('still');
});
