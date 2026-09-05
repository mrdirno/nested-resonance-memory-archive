// Author: Aldrin Payopay · GPL-3.0-only
// Real UI, saved artifacts and decoded video: no application internals are stubbed.
import { test, expect, type Page } from '@playwright/test';
import zlib from 'node:zlib';
import fs from 'node:fs/promises';
import path from 'node:path';
import JSZip from 'jszip';
import { measureTones, HZ_CONTROL } from './tone-measure';
import { encodeState } from '../../src/lib/rollCode';

const SRT = '1\n00:00:00,000 --> 00:00:01,000\nFIRST LIGHT\n\n2\n00:00:02,000 --> 00:00:03,000\nWE MAKE OUR OWN\n';
// Node 20 is the site's CI runtime; zlib.crc32 only exists on newer Node.
function pngCrc32(bytes: Buffer): number {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function whitePng() {
  const chunk = (kind: string, data: Buffer) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const body = Buffer.concat([Buffer.from(kind), data]);
    const crc = Buffer.alloc(4); crc.writeUInt32BE(pngCrc32(body));
    return Buffer.concat([len, body, crc]);
  };
  const head = Buffer.alloc(13); head.writeUInt32BE(96, 0); head.writeUInt32BE(96, 4); head[8] = 8; head[9] = 2;
  const pixels = Buffer.alloc(96 * (1 + 96 * 3), 245);
  for (let y = 0; y < 96; y++) pixels[y * 289] = 0;
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), chunk('IHDR', head), chunk('IDAT', zlib.deflateSync(pixels)), chunk('IEND', Buffer.alloc(0))]);
}
async function boot(page: Page) {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.locator('input[type=file]').first().setInputFiles({ name: 'owned-art.png', mimeType: 'image/png', buffer: whitePng() });
  await page.getByRole('button', { name: 'Lyrics & captions', exact: true }).click();
  await expect(page.getByTestId('caption-editor')).toBeVisible({ timeout: 60_000 });
}
async function importCues(page: Page, buffer = SRT) {
  await page.getByLabel('Import caption file', { exact: true }).setInputFiles({ name: 'lyrics.srt', mimeType: 'application/x-subrip', buffer: Buffer.from(buffer) });
  await expect(page.getByRole('button', { name: /Edit caption 1:/ })).toBeVisible();
}
async function seek(page: Page, t: number) {
  await page.getByLabel(/^Playhead/).fill(String(t));
  await expect.poll(() => page.getByLabel(/^Playhead/).inputValue()).toBe(String(t));
  await page.waitForTimeout(180);
}
async function ink(page: Page, movieTime?: number) {
  return page.evaluate(async (time) => {
    let source: HTMLCanvasElement | HTMLVideoElement;
    if (time !== undefined) {
      const v = document.querySelector('video[controls]') as HTMLVideoElement;
      v.pause(); v.loop = false;
      if (Math.abs(v.currentTime - time) > 0.005) {
        await new Promise<void>((resolve, reject) => {
          const timer = setTimeout(() => reject(new Error('recorded video did not seek')), 10000);
          v.addEventListener('seeked', () => { clearTimeout(timer); resolve(); }, { once: true });
          v.currentTime = time;
        });
      }
      source = v;
    } else {
      source = [...document.querySelectorAll('canvas')].sort((a,b) => b.width*b.height-a.width*a.height)[0];
    }
    const cv = document.createElement('canvas'); cv.width = 240; cv.height = 240;
    const ctx = cv.getContext('2d')!; ctx.drawImage(source, 0, 0, 240, 240);
    const data = ctx.getImageData(24, 175, 192, 56).data;
    let dark = 0, hash = 2166136261;
    for (let i=0;i<data.length;i+=4) {
      if(data[i] < 210 && data[i+1] < 210 && data[i+2] < 210) dark++;
      hash = Math.imul(hash ^ data[i], 16777619) >>> 0;
    }
    return { dark: dark / (data.length/4), hash };
  }, movieTime);
}

test('caption boundaries, paused edits and malformed imports preserve the actual picture', async ({ page }) => {
  const errors: string[] = []; page.on('pageerror', e => errors.push(e.message));
  await boot(page); await importCues(page);
  await seek(page, 0.5); const first = await ink(page);
  await seek(page, 1); const gap = await ink(page);
  await seek(page, 2); const second = await ink(page);
  expect(first.dark).toBeGreaterThan(gap.dark + 0.025);
  expect(second.dark).toBeGreaterThan(gap.dark + 0.025);
  expect(first.hash).not.toBe(second.hash);
  await seek(page, 2.5);
  await page.getByRole('button', { name: /Edit caption 2:/ }).click();
  await page.getByLabel('Caption text', { exact: true }).fill('REVISED AT THIS MOMENT');
  await page.getByRole('button', { name: 'Save cue', exact: true }).click();
  await expect(page.getByLabel(/^Playhead/)).toHaveValue('2.5');
  await expect.poll(async () => (await ink(page)).hash).not.toBe(second.hash);
  await page.getByLabel('Import caption file', { exact: true }).setInputFiles({ name: 'bad.srt', mimeType: 'application/x-subrip', buffer: Buffer.from('1\n00:00:04,000 --> 00:00:01,000\nBroken') });
  await expect(page.getByRole('alert')).toBeVisible();
  await expect(page.getByRole('button', { name: /Edit caption 2: REVISED AT THIS MOMENT/ })).toBeVisible();
  expect(errors).toEqual([]);
});

test('lyrics survive project, SVG, subtitle and crash-recovery round trips', async ({ page }, info) => {
  await boot(page); await importCues(page);
  const d = page.waitForEvent('download'); await page.keyboard.press('Control+s');
  const file = await d; const saved = info.outputPath('lyrics.collage'); await file.saveAs(saved);
  const zip = await JSZip.loadAsync(await fs.readFile(saved));
  const manifest = JSON.parse(await zip.file('manifest.json')!.async('text'));
  expect(manifest.captions.cues.map((c:any) => c.text)).toEqual(['FIRST LIGHT', 'WE MAKE OUR OWN']);
  const subtitle = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export VTT', exact: true }).click();
  const vtt = await subtitle; expect(await fs.readFile((await vtt.path())!, 'utf8')).toContain('00:00:02.000 --> 00:00:03.000');
  await page.getByRole('button', { name: /Export/i, exact: true }).first().click();
  const vector = page.waitForEvent('download'); await page.getByRole('button', { name: /Vector SVG/ }).click();
  const svg = await vector; const svgPath = info.outputPath('lyrics.svg'); await svg.saveAs(svgPath);
  const xml = await fs.readFile(svgPath, 'utf8');
  expect(xml).toContain('collage-project');
  const openingText = xml.match(/<g id="Title">([\s\S]*?)<\/g>/)?.[1];
  expect(openingText).toContain('FIRST LIGHT');
  expect(openingText).not.toContain('WE MAKE OUR OWN');
  // Read the actual IndexedDB state, not the serialization function that wrote it.
  await expect.poll(async () => page.evaluate(async () => {
    const names = await indexedDB.databases();
    for (const { name } of names) {
      if (!name) continue;
      const db = await new Promise<IDBDatabase>((r,j) => { const q = indexedDB.open(name); q.onsuccess=()=>r(q.result); q.onerror=()=>j(q.error); });
      for (const store of [...db.objectStoreNames]) {
        const rows = await new Promise<any[]>((r,j) => { const q=db.transaction(store).objectStore(store).getAll();q.onsuccess=()=>r(q.result);q.onerror=()=>j(q.error); });
        if (JSON.stringify(rows).includes('WE MAKE OUR OWN')) { db.close(); return true; }
      }
      db.close();
    }
    return false;
  }), { timeout: 20000 }).toBe(true);
  await page.reload();
  await page.getByRole('button', { name: 'Restore', exact: true }).click();
  await expect(page.getByTestId('caption-editor')).toContainText('2 timed cues');
  const chooser = page.waitForEvent('filechooser'); await page.getByRole('button', { name: 'Open', exact: true }).first().click();
  await (await chooser).setFiles(saved);
  await expect(page.getByTestId('caption-editor')).toContainText('2 timed cues');
  await page.getByRole('button', { name: 'Lyrics & captions', exact: true }).click();
  await expect(page.getByRole('button', { name: /Edit caption 2: WE MAKE OUR OWN/ })).toBeVisible();
  const chooserSvg = page.waitForEvent('filechooser'); await page.getByRole('button', { name: 'Open', exact: true }).first().click();
  await (await chooserSvg).setFiles(svgPath);
  await expect(page.getByTestId('caption-editor')).toContainText('2 timed cues');
});

test('a recorded MP4 contains timed lyrics and the imported soundtrack', async ({ page }, info) => {
  await boot(page); await importCues(page);
  await page.locator('input[data-intake="music"]').setInputFiles(path.resolve('tests/fixtures/music_1500.m4a'));
  await expect(page.getByRole('button', { name: /Remove the music/ })).toBeVisible({ timeout: 60000 });
  await page.getByRole('button', { name: '5s', exact: true }).click();
  await page.getByRole('button', { name: 'Record video', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Recorded take' })).toBeVisible({ timeout: 120000 });
  const a = await ink(page, 0.5), gap = await ink(page, 1.5), b = await ink(page, 2.5);
  expect(a.dark).toBeGreaterThan(gap.dark + 0.025);
  expect(b.dark).toBeGreaterThan(gap.dark + 0.025);
  expect(a.hash).not.toBe(b.hash);
  const tone = await measureTones(page, [1500], HZ_CONTROL);
  expect(tone.ok, tone.reason).toBe(true); expect(tone.rms).toBeGreaterThan(.001);
  expect(tone.bins[0]).toBeGreaterThan(tone.control * 8);
  const result = await page.evaluate(async () => {
    const v = document.querySelector('video[controls]') as HTMLVideoElement;
    const bytes = new Uint8Array(await (await fetch(v.src)).arrayBuffer());
    let raw=''; for(let i=0;i<bytes.length;i+=8192) raw+=String.fromCharCode(...bytes.subarray(i,i+8192));
    return { data:btoa(raw), duration:v.duration, width:v.videoWidth,height:v.videoHeight };
  });
  expect(result.duration).toBeGreaterThan(4.8); expect(result.duration).toBeLessThan(5.2);
  await fs.writeFile(info.outputPath('captioned-take.mp4'), Buffer.from(result.data,'base64'));
});

test('caption controls fit 320, 360, 390 and 430 pixel screens', async ({ page }) => {
  await boot(page); await importCues(page);
  await page.getByRole('button', { name: /Edit caption 1:/ }).click();
  for (const width of [320,360,390,430]) {
    await page.setViewportSize({ width, height:844 });
    const result = await page.getByTestId('caption-editor').evaluate(root => {
      const controls=[...root.querySelectorAll('button,input:not([type=file]),textarea,select,summary')].filter(e=>(e as HTMLElement).getClientRects().length);
      return { overflow: document.documentElement.scrollWidth > innerWidth + 1, narrow: controls.filter(e=>{const r=e.getBoundingClientRect();return r.height < 43.5 || r.width < 43.5;}).map(e=>e.textContent), right:Math.max(...controls.map(e=>e.getBoundingClientRect().right)) };
    });
    expect(result.overflow, JSON.stringify(result)).toBe(false); expect(result.narrow).toEqual([]); expect(result.right).toBeLessThanOrEqual(width+1);
  }
});

// This starter is real local media entering the same upload/render/save paths.
test('the empty canvas offers an editable original lyric film', async ({ page }, info) => {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.getByRole('button', { name: 'Try a lyric film', exact: true }).click();
  await expect(page.getByTestId('caption-editor')).toContainText('3 timed cues', { timeout: 60000 });
  await page.getByRole('button', { name: 'Preview caption 2', exact: true }).click();
  await expect(page.getByLabel(/^Playhead/)).toHaveValue('3.3');
  await expect(page.getByRole('button', { name: 'Record video', exact: true })).toBeEnabled();
  const size = await page.locator('canvas').first().boundingBox();
  expect(size?.height).toBeGreaterThan(80);
  await page.getByRole('button', { name: /Edit caption 2: ONLY YOU/ }).click();
  await expect(page.getByLabel('Caption text', { exact: true })).toHaveValue('ONLY YOU');
  if (info.project.name === 'chromium') {
    await page.getByRole('button', { name: 'Record video', exact: true }).click();
    await expect(page.getByRole('dialog', { name: 'Recorded take' })).toBeVisible({ timeout: 120000 });
    const data = await page.evaluate(async () => {
      const v = document.querySelector('video[controls]') as HTMLVideoElement;
      const bytes = new Uint8Array(await (await fetch(v.src)).arrayBuffer());
      let raw=''; for(let i=0;i<bytes.length;i+=8192) raw+=String.fromCharCode(...bytes.subarray(i,i+8192));
      return btoa(raw);
    });
    await fs.writeFile(info.outputPath('original-lyric-film.mp4'), Buffer.from(data, 'base64'));
  }
});

/** Hold a real image decode at its browser boundary. The actual PNG bytes,
 * decoder, import pipeline and project writer all run after release. */
async function holdImageSources(page: Page, prefix: string) {
  await page.route('**/cdn.jsdelivr.net/**', route => route.abort());
  await page.addInitScript((prefix) => {
    const target = window as typeof window & { heldImageSources: number; releaseImageSources: () => void };
    const sourceUrls = new Set<string>();
    const create = URL.createObjectURL;
    URL.createObjectURL = (blob) => {
      const url = create.call(URL, blob);
      if (blob instanceof File && blob.name.startsWith(prefix)) sourceUrls.add(url);
      return url;
    };
    let held = true;
    const pending: Array<() => void> = [];
    target.heldImageSources = 0;
    target.releaseImageSources = () => { held = false; for (const resume of pending.splice(0)) resume(); };
    const descriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src')!;
    Object.defineProperty(HTMLImageElement.prototype, 'src', {
      configurable: true, enumerable: descriptor.enumerable, get: descriptor.get,
      set(value: string) {
        if (held && sourceUrls.has(value)) {
          target.heldImageSources++;
          pending.push(() => descriptor.set!.call(this, value));
        } else descriptor.set!.call(this, value);
      },
    });
  }, prefix);
}

async function savedManifest(page: Page) {
  const download = page.waitForEvent('download');
  await page.keyboard.press('Control+s');
  const zip = await JSZip.loadAsync(await fs.readFile((await (await download).path())!));
  return JSON.parse(await zip.file('manifest.json')!.async('text'));
}

test('starter blocks racing intake and chooses its own recipe instead of the URL', async ({ page }) => {
  await holdImageSources(page, 'original-shapes-');
  const previous = encodeState({ layoutMode: 'balanced', primitive: 'circle', count: 1, density: 4,
    entropy: 0.9, aspect: 1, gutter: 0.03, bgColor: '#ffffff', seed: 47, arrangement: 'wheel',
    focus: 'wander', twist: 'scatter', look: 'mono', adjust: null, move: 'still', turn: 'march',
    pace: 'rush', sync: 'off', shuffle: 8, countOwned: true });
  await page.goto(`${process.env.COLLAGE_BASE_URL || '/'}?c=${previous}`);
  await page.getByRole('button', { name: 'Try a lyric film', exact: true }).click();
  await expect.poll(() => page.evaluate(() => (window as any).heldImageSources)).toBeGreaterThan(0);
  const intake = page.locator('input[type=file][accept="image/*,video/*"]');
  await intake.setInputFiles({ name: 'racing-photo.png', mimeType: 'image/png', buffer: whitePng() });
  await expect(page.getByText('The sample is still loading. Try that action again when it appears.')).toBeVisible();
  let choosers = 0;
  page.on('filechooser', () => { choosers++; });
  await page.getByRole('button', { name: 'Open', exact: true }).click();
  expect(choosers).toBe(0);
  await page.evaluate(() => (window as any).releaseImageSources());
  await expect(page.getByTestId('caption-editor')).toContainText('3 timed cues', { timeout: 60_000 });
  const manifest = await savedManifest(page);
  expect(manifest.images.map((image: any) => image.originalName)).toEqual([
    'original-shapes-1.png', 'original-shapes-2.png', 'original-shapes-3.png', 'original-shapes-4.png',
  ]);
  expect(manifest.layout).toMatchObject({ mode: 'kaleidoscope', primitive: 'rect', count: 4, countOwned: true,
    density: 1, shuffle: 0, entropy: 0.5, arrangement: 'natural', focus: 'auto', twist: 'none',
    turn: 'hold', pace: 'even', move: 'drift', seed: 500, aspect: 9 / 16 });
  expect(manifest.style.look).toBe('none');
  // The delayed action is available again after the sample, with its file intact.
  await intake.setInputFiles({ name: 'racing-photo.png', mimeType: 'image/png', buffer: whitePng() });
  await expect(page.locator('.animate-spin')).toHaveCount(0, { timeout: 60_000 });
  await expect.poll(async () => (await savedManifest(page)).images.length, { timeout: 20_000 }).toBe(5);
});

test('an existing import finishes before the starter can claim an empty canvas', async ({ page }) => {
  await holdImageSources(page, 'already-opening');
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles({
    name: 'already-opening.png', mimeType: 'image/png', buffer: whitePng(),
  });
  await expect.poll(() => page.evaluate(() => (window as any).heldImageSources)).toBeGreaterThan(0);
  await page.getByRole('button', { name: 'Try a lyric film', exact: true }).click();
  await expect(page.getByText('Your media is still opening. Let it finish before starting a sample.')).toBeVisible();
  await page.evaluate(() => (window as any).releaseImageSources());
  await expect(page.locator('svg[viewBox^="0 0 1200 "] > g')).toHaveCount(1, { timeout: 60_000 });
  const manifest = await savedManifest(page);
  expect(manifest.images.map((image: any) => image.originalName)).toEqual(['already-opening.png']);
  expect(manifest.captions).toBeUndefined();
});

// A canvas pixel check cannot see DOM controls painted over the artwork.
// This checks the actual composition bounds and hit-testing above the rail.
test('full bleed tools leave bottom captions and static titles visible', async ({ page }, info) => {
  await boot(page);
  await importCues(page);
  await seek(page, 0.5);
  const reading = await ink(page);
  expect(reading.dark, 'the caption must actually be painted before checking its visibility').toBeGreaterThan(0.01);
  await page.getByRole('button', { name: 'Maximize the shot', exact: true }).click();

  const geometry = () => page.evaluate(() => {
    const source = document.querySelector('canvas') ?? document.querySelector('img[src^="blob:"]');
    const rail = document.querySelector('[role="toolbar"][aria-label="Full bleed tools"]');
    if (!source || !rail) throw new Error('The artwork or its full-bleed controls are absent');
    const art = source.getBoundingClientRect(), tools = rail.getBoundingClientRect();
    const hit = document.elementFromPoint(art.x + art.width / 2, art.y + art.height * 0.94);
    return {
      clearance: tools.top - art.bottom,
      artworkOwnsHit: !!hit && !!source.parentElement?.contains(hit),
      art: art.toJSON(), rail: tools.toJSON(),
      controls: [...rail.querySelectorAll('button')].map(button => {
        const box = button.getBoundingClientRect();
        const landed = document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2);
        return { width: box.width, height: box.height, ownsHit: !!landed && button.contains(landed) };
      }),
    };
  });
  const verify = async (label: string) => {
    await expect.poll(async () => (await geometry()).clearance, `${label}: artwork must end above the rail`).toBeGreaterThanOrEqual(7);
    const g = await geometry();
    expect(g.artworkOwnsHit, `${label}: a control covers the caption's part of the artwork`).toBe(true);
    for (const button of g.controls) {
      expect(button.width).toBeGreaterThanOrEqual(43.5);
      expect(button.height).toBeGreaterThanOrEqual(43.5);
      expect(button.ownsHit).toBe(true);
    }
    await page.screenshot({ path: info.outputPath(`${label}.png`) });
  };
  for (const [width, height] of [[1280, 720], [390, 664], [320, 664]]) {
    await page.setViewportSize({ width, height });
    await verify(`captions-${width}`);
    if (width === 1280) {
      // Negative control: remove the reserved band from this page only. The
      // same measurement must then expose the original collision.
      const padding = await page.locator('canvas').first().evaluate(canvas => {
        const band = canvas.parentElement!.parentElement!;
        const saved = band.style.paddingBottom;
        band.style.paddingBottom = '0px';
        return saved;
      });
      await expect.poll(async () => (await geometry()).clearance).toBeLessThan(0);
      await page.locator('canvas').first().evaluate((canvas, value) => {
        canvas.parentElement!.parentElement!.style.paddingBottom = value;
      }, padding);
      await verify('captions-restored');
    }
  }

  // The persistent title uses the same bottom plate and needs the same space.
  await page.getByRole('button', { name: 'Exit full bleed', exact: true }).click();
  await page.getByRole('button', { name: 'Clear captions', exact: true }).click();
  await page.getByRole('button', { name: 'Layout', exact: true }).click();
  await page.getByLabel('Title drawn on the collage', { exact: true }).fill('MY OWN FILM');
  await page.getByRole('button', { name: 'Maximize the shot', exact: true }).click();
  for (const [width, height] of [[1280, 720], [390, 664], [320, 664]]) {
    await page.setViewportSize({ width, height });
    await verify(`static-title-${width}`);
  }
});
