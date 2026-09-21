// Author: Aldrin Payopay · GPL-3.0-only
// Real still-preview pixels, an actual worker JPG download, and SVG are three
// separate witnesses. This is the >=3:1 solid sRGB LARGE-title contract, not a
// claim about antialiased edges or small text. Stage/MP4 have their own test.
import { test, expect, type Page } from '@playwright/test';
import fs from 'node:fs/promises';
import zlib from 'node:zlib';
import JSZip from 'jszip';

test.setTimeout(150_000);
const URL = process.env.COLLAGE_BASE_URL || '/';
const TITLE = 'HHHH'; // thick, straight interiors survive JPEG chroma subsampling
const SANS = '"Helvetica Neue", Helvetica, Arial, sans-serif';
const SERIF = 'Georgia, "Times New Roman", Times, serif';
const COLORS = [
  { name: 'yellow', ink: '#ffd400', rgb: [255, 212, 0], alpha: .53 },
  { name: 'red', ink: '#ff453a', rgb: [255, 69, 58], alpha: .75 },
  { name: 'blue', ink: '#0a84ff', rgb: [10, 132, 255], alpha: .77 },
  { name: 'pink', ink: '#ff375f', rgb: [255, 55, 95], alpha: .76 },
] as const;
type Color = typeof COLORS[number];
type TitleGeometry = {
  width: number; height: number; x: number; y: number; w: number; h: number; r: number;
  ink: string; scrim: string; family: string; fontPx: number; text: string;
};

function whitePng(): Buffer {
  const chunk = (type: string, data: Buffer) => {
    const body = Buffer.concat([Buffer.from(type), data]);
    let crc = 0xffffffff;
    for (const byte of body) {
      crc ^= byte;
      for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
    const length = Buffer.alloc(4), checksum = Buffer.alloc(4);
    length.writeUInt32BE(data.length); checksum.writeUInt32BE((crc ^ 0xffffffff) >>> 0);
    return Buffer.concat([length, body, checksum]);
  };
  const header = Buffer.alloc(13); header.writeUInt32BE(96, 0); header.writeUInt32BE(96, 4); header[8] = 8; header[9] = 2;
  const pixels = Buffer.alloc(96 * 289, 255);
  for (let y = 0; y < 96; y++) pixels[y * 289] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', header), chunk('IDAT', zlib.deflateSync(pixels)), chunk('IEND', Buffer.alloc(0))]);
}

async function openTitle(page: Page) {
  if (await page.getByTestId('title-input').isVisible()) return;
  await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Text', exact: true }).click();
  await page.getByRole('button', { name: 'Title', exact: true }).click();
}
async function boot(page: Page) {
  await page.goto(URL);
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles({ name: 'bright-original.png', mimeType: 'image/png', buffer: whitePng() });
  await expect(page.getByTestId('studio-artwork')).toBeVisible({ timeout: 60_000 });
  await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Motion', exact: true }).click();
  await page.getByTestId('move-still').click();
  await expect(page.getByTestId('move-still')).toHaveAttribute('aria-pressed', 'true');
  await openTitle(page);
  await page.getByTestId('title-input').fill(TITLE);
  await page.getByTestId('title-size-lg').click();
  await page.getByTestId('title-place-bl').click();
  await expect(page.getByTestId('studio-artwork').locator('img')).toBeVisible();
  await expect(page.getByTestId('studio-artwork').locator('canvas')).toHaveCount(0);
}
async function svg(page: Page, file: string): Promise<TitleGeometry> {
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: /Vector SVG/ }).click();
  await (await download).saveAs(file);
  const content = await fs.readFile(file, 'utf8');
  return page.evaluate(content => {
    const document = new DOMParser().parseFromString(content, 'image/svg+xml');
    if (document.querySelector('parsererror')) throw Error('Downloaded SVG is not valid XML');
    const title = document.querySelector('g#Title'), rect = title?.querySelector('rect'), text = title?.querySelector('text');
    if (!rect || !text) throw Error('Downloaded SVG is missing its title');
    const number = (el: Element, key: string) => Number(el.getAttribute(key));
    const view = document.documentElement.getAttribute('viewBox')!.split(/\s+/).map(Number);
    return { width: view[2], height: view[3], x: number(rect, 'x'), y: number(rect, 'y'), w: number(rect, 'width'), h: number(rect, 'height'), r: number(rect, 'rx'),
      ink: text.getAttribute('fill')!, scrim: rect.getAttribute('fill')!, family: text.getAttribute('font-family')!, fontPx: number(text, 'font-size'), text: text.textContent || '' };
  }, content);
}

async function measure(page: Page, geometry: TitleGeometry, color: Color, downloaded?: Buffer, source: 'preview' | 'stage' | 'recorded' = 'preview') {
  return page.evaluate(async ({ geometry: g, rgb, dataUrl, source }) => {
    const selector = source === 'stage' ? '[data-testid="studio-artwork"] canvas[aria-hidden=true]'
      : source === 'recorded' ? 'video[controls]' : '[data-testid="studio-artwork"] img';
    const image = dataUrl ? new Image() : document.querySelector<HTMLImageElement | HTMLCanvasElement | HTMLVideoElement>(selector)!;
    if (!image) throw Error(`Missing actual ${source} surface`);
    if (image instanceof HTMLImageElement) { if (dataUrl) image.src = dataUrl; await image.decode(); }
    const width = image instanceof HTMLImageElement ? image.naturalWidth : image instanceof HTMLVideoElement ? image.videoWidth : image.width;
    const height = image instanceof HTMLImageElement ? image.naturalHeight : image instanceof HTMLVideoElement ? image.videoHeight : image.height;
    const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
    const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
    ctx.drawImage(image, 0, 0);
    const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height), k = canvas.width / g.width, ky = canvas.height / g.height;
    const pixel = (x: number, y: number) => { const i = (y * canvas.width + x) * 4; return [data[i], data[i + 1], data[i + 2]]; };
    const close = (p: number[], target: readonly number[], tolerance: number) => p.every((v, i) => Math.abs(v - target[i]) <= tolerance);
    const inks: number[][] = [], plates: number[][] = [];
    const x0 = Math.ceil(g.x * k) + 3, x1 = Math.floor((g.x + g.w) * k) - 3;
    // Stage fits integer raster dimensions independently in each axis.
    const y0 = Math.ceil(g.y * ky) + 3, y1 = Math.floor((g.y + g.h) * ky) - 3;
    // Erode by two pixels at export sizes, one pixel at small Stage rasters:
    // a 31px bold glyph has solid strokes narrower than a 5×5 neighborhood.
    // Both exclude antialiased edges; broad tolerances select interiors, but
    // measured medians, not the requested hex, determine the reported contrast.
    const erosionRadius = g.fontPx * k >= 48 ? 2 : 1;
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
      let interior = true;
      for (let dy = -erosionRadius; dy <= erosionRadius && interior; dy++) for (let dx = -erosionRadius; dx <= erosionRadius; dx++) {
        if (!close(pixel(x + dx, y + dy), rgb, 10)) { interior = false; break; }
      }
      if (interior) inks.push(pixel(x, y));
    }
    // The top padding inside the rounded rectangle contains plate only. Stay
    // beyond its corner radius and below its antialiased top border.
    for (let y = Math.ceil(g.y * ky) + 2; y < Math.floor((g.y + g.h * .12) * ky); y++) {
      for (let x = Math.ceil((g.x + g.r) * k) + 3; x < Math.floor((g.x + g.w - g.r) * k) - 3; x++) {
        const p = pixel(x, y);
        if (Math.max(...p) - Math.min(...p) <= 3) plates.push(p);
      }
    }
    // A dark grid gutter must not supply the favorable plate sample. Choose
    // the brightest substantial neutral cluster, independently of the expected
    // alpha. Tiny JPEG ringing clusters cannot qualify as the photo backdrop.
    const bins = new Map<number, number[][]>();
    for (const p of plates) {
      const bin = Math.round((p[0] + p[1] + p[2]) / 12) * 4;
      const group = bins.get(bin);
      if (group) group.push(p); else bins.set(bin, [p]);
    }
    const substantial = Math.max(100, plates.length * .1);
    const brightest = [...bins.keys()].sort((a, b) => b - a).find(bin => bins.get(bin)!.length >= substantial);
    const backdrop = brightest === undefined ? [] : plates.filter(p => Math.abs((p[0] + p[1] + p[2]) / 3 - brightest) <= 4);
    const median = (values: number[][]) => [0, 1, 2].map(i => values.map(p => p[i]).sort((a, b) => a - b)[Math.floor(values.length / 2)] ?? -1);
    const ink = median(inks), plate = median(backdrop);
    let inkSearch: { count: number; left: number; top: number; right: number; bottom: number } | null = null;
    if (inks.length < 100) {
      inkSearch = { count: 0, left: canvas.width, top: canvas.height, right: 0, bottom: 0 };
      for (let y = 0; y < canvas.height; y++) for (let x = 0; x < canvas.width; x++) if (close(pixel(x, y), rgb, 10)) {
        inkSearch.count++; inkSearch.left = Math.min(inkSearch.left, x); inkSearch.top = Math.min(inkSearch.top, y);
        inkSearch.right = Math.max(inkSearch.right, x); inkSearch.bottom = Math.max(inkSearch.bottom, y);
      }
    }
    const luminance = (p: number[]) => p.map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
      .reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
    const a = luminance(ink), b = luminance(plate);
    return { width: canvas.width, height: canvas.height, ink, plate, inkSamples: inks.length, plateSamples: backdrop.length,
      neutralCandidates: plates.length, brightestPlateCluster: brightest ?? null,
      erosionRadius, nativeFontPx: g.fontPx * k, inkSearch,
      contrast: (Math.max(a, b) + .05) / (Math.min(a, b) + .05) };
  }, { geometry, rgb: [...color.rgb], dataUrl: downloaded ? `data:image/jpeg;base64,${downloaded.toString('base64')}` : null, source });
}
type Measurement = Awaited<ReturnType<typeof measure>>;

test.afterEach(async ({ page }, info) => {
  if (info.status !== info.expectedStatus) {
    await page.screenshot({ path: info.outputPath('title-contrast-failure.png') });
    const stage = page.getByTestId('studio-artwork').locator('canvas[aria-hidden=true]');
    if (await stage.count()) {
      const png = await stage.evaluate((canvas: HTMLCanvasElement) => canvas.toDataURL('image/png').split(',')[1]);
      await fs.writeFile(info.outputPath('stage-failure.png'), Buffer.from(png, 'base64'));
    }
  }
});

function assertPixels(actual: Measurement, color: Color, surface: string) {
  expect(actual.inkSamples, `${color.name} ${surface}: solid ink interiors`).toBeGreaterThan(100);
  expect(actual.plateSamples, `${color.name} ${surface}: actual plate padding`).toBeGreaterThan(100);
  for (let i = 0; i < 3; i++) {
    expect.soft(Math.abs(actual.ink[i] - color.rgb[i]), `${color.name} ${surface}: measured ink channel ${i}`).toBeLessThanOrEqual(5);
    expect.soft(Math.abs(actual.plate[i] - 255 * (1 - color.alpha)), `${color.name} ${surface}: plate composited over the bright original`).toBeLessThanOrEqual(3);
  }
  expect.soft(actual.contrast, `${color.name} ${surface}: measured solid ink ${actual.ink} against actual plate ${actual.plate}`).toBeGreaterThanOrEqual(3);
}

async function workerJpg(page: Page, file: string) {
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  await page.getByRole('radio', { name: /^2K/ }).click();
  const worker = page.waitForEvent('worker', { predicate: worker => /render\.worker/.test(worker.url()) });
  await page.getByRole('button', { name: /^Render 2K JPG/ }).click();
  const workerUrl = (await worker).url();
  const result = page.getByRole('dialog').filter({ has: page.getByAltText('Rendered collage', { exact: true }) });
  await expect(result.getByText('Render complete', { exact: true })).toBeVisible({ timeout: 60_000 });
  const download = page.waitForEvent('download');
  await result.getByRole('button', { name: 'Download', exact: true }).click();
  await (await download).saveAs(file);
  await result.getByRole('button', { name: 'Close', exact: true }).click();
  return { bytes: await fs.readFile(file), workerUrl };
}

test('all four colored large titles retain >=3:1 actual preview and worker-JPG contrast on a bright image', async ({ page }, info) => {
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  await boot(page);
  const receipt: unknown[] = [];
  for (const color of COLORS) {
    const old = await page.getByTestId('studio-artwork').locator('img').getAttribute('src');
    await page.getByTestId(`title-color-${color.name}`).click();
    await expect(page.getByTestId(`title-color-${color.name}`)).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('studio-artwork').locator('img')).not.toHaveAttribute('src', old!);
    const plan = await svg(page, info.outputPath(`${color.name}.svg`));
    expect(plan.text).toBe(TITLE); expect(plan.family).toBe(SANS);
    expect(plan.ink).toBe(color.ink);
    expect.soft(plan.scrim).toBe(`rgba(0,0,0,${color.alpha})`);
    await expect.poll(async () => (await measure(page, plan, color)).inkSamples).toBeGreaterThan(100);
    const preview = await measure(page, plan, color);
    assertPixels(preview, color, 'still preview');
    const jpg = await workerJpg(page, info.outputPath(`${color.name}-worker.jpg`));
    const exported = await measure(page, plan, color, jpg.bytes);
    await fs.writeFile(info.outputPath(`${color.name}-contrast.json`), JSON.stringify({ preview, exported, plan }, null, 2));
    await info.attach(`${color.name}-contrast.json`, { body: JSON.stringify({ preview, exported, plan }, null, 2), contentType: 'application/json' });
    // Existing aspect/integer quantization may make a 2K long edge 2047px.
    expect(Math.abs(Math.max(exported.width, exported.height) - 2048)).toBeLessThanOrEqual(1);
    assertPixels(exported, color, 'downloaded worker JPG');
    for (let i = 0; i < 3; i++) expect.soft(Math.abs(preview.plate[i] - exported.plate[i]), `${color.name}: preview/worker plate agreement`).toBeLessThanOrEqual(3);
    receipt.push({ color: color.name, svg: plan, preview, exported, workerUrl: jpg.workerUrl });
    if (color.name === 'red') await page.screenshot({ path: info.outputPath('red-title-still-preview.png') });
  }
  await info.attach('rendered-title-contrast.json', { body: JSON.stringify(receipt, null, 2), contentType: 'application/json' });
  expect(errors).toEqual([]);
});

test('saved title color and font reopen with the same rendered palette', async ({ page }, info) => {
  await boot(page);
  const red = COLORS.find(color => color.name === 'red')!;
  await page.getByTestId('title-color-red').click();
  await page.getByTestId('title-font-serif').click();
  const before = await svg(page, info.outputPath('before-project.svg'));
  await page.getByRole('button', { name: 'Open', exact: true }).focus();
  const saved = page.waitForEvent('download');
  await page.keyboard.press('Control+s');
  const file = info.outputPath('red-serif.collage');
  await (await saved).saveAs(file);
  const zip = await JSZip.loadAsync(await fs.readFile(file));
  const manifest = JSON.parse(await zip.file('manifest.json')!.async('text'));
  expect(manifest.title).toEqual({ text: TITLE, place: 'bl', size: 'lg', color: 'red', font: 'serif' });
  await page.reload();
  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Open', exact: true }).click();
  await (await chooser).setFiles(file);
  await expect(page.getByTestId('studio-artwork')).toBeVisible({ timeout: 60_000 });
  await openTitle(page);
  await expect(page.getByTestId('title-input')).toHaveValue(TITLE);
  await expect(page.getByTestId('title-color-red')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByTestId('title-font-serif')).toHaveAttribute('aria-pressed', 'true');
  const reopened = await svg(page, info.outputPath('reopened-project.svg'));
  expect(reopened).toEqual(before);
  expect(reopened.family).toBe(SERIF);
  expect(reopened.scrim).toBe('rgba(0,0,0,0.75)');
  await expect.poll(async () => (await measure(page, reopened, red)).inkSamples).toBeGreaterThan(100);
  const pixels = await measure(page, reopened, red);
  await fs.writeFile(info.outputPath('reopened-title-contrast.json'), JSON.stringify(pixels, null, 2));
  assertPixels(pixels, red, 'reopened still preview');
  await info.attach('reopened-title-contrast.json', { body: JSON.stringify(pixels, null, 2), contentType: 'application/json' });
});

test('red title contrast reaches the live Stage and actual decoded MP4 frames', async ({ page, browserName }, info) => {
  test.skip(browserName !== 'chromium', 'Recorded-media QA uses the Chromium profiles with device output muted.');
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  await boot(page);
  const red = COLORS.find(color => color.name === 'red')!;
  await page.getByTestId('title-color-red').click();
  const plan = await svg(page, info.outputPath('recorded-title.svg'));
  await page.getByRole('navigation', { name: 'Studio tools' }).getByRole('button', { name: 'Motion', exact: true }).click();
  await page.getByTestId('move-push').click();
  await page.getByRole('button', { name: 'Close editing panel', exact: true }).click();
  await expect(page.getByTestId('studio-artwork').locator('canvas[aria-hidden=true]')).toBeVisible();
  let stage = await measure(page, plan, red, undefined, 'stage');
  try {
    await expect.poll(async () => { stage = await measure(page, plan, red, undefined, 'stage'); return stage.inkSamples; }).toBeGreaterThan(100);
  } finally {
    await fs.writeFile(info.outputPath('stage-title-contrast.json'), JSON.stringify({ stage, plan }, null, 2));
    await info.attach('stage-title-contrast.json', { body: JSON.stringify({ stage, plan }, null, 2), contentType: 'application/json' });
    await page.screenshot({ path: info.outputPath('red-title-live-stage.png') });
  }
  assertPixels(stage, red, 'live Stage');
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  const sheet = page.getByRole('dialog', { name: 'Export', exact: true });
  const sizes = sheet.getByRole('radiogroup', { name: 'Video size', exact: true });
  if (await sizes.count()) await sizes.locator('[role=radio]:not(:disabled)').first().click();
  await sheet.getByRole('button', { name: '5s', exact: true }).click();
  await sheet.getByRole('button', { name: 'Record 5s video', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Recorded take', exact: true })).toBeVisible({ timeout: 120_000 });
  const recorded = page.locator('video[controls]');
  await expect.poll(() => recorded.evaluate((video: HTMLVideoElement) => video.readyState >= 2 && Number.isFinite(video.duration))).toBe(true);
  const duration = await recorded.evaluate((video: HTMLVideoElement) => { video.pause(); video.loop = false; return video.duration; });
  const media = await recorded.evaluate(async (video: HTMLVideoElement) => {
    const blob = await (await fetch(video.currentSrc || video.src)).blob();
    const bytes = new Uint8Array(await blob.arrayBuffer()); let binary = '';
    for (let i = 0; i < bytes.length; i += 8192) binary += String.fromCharCode(...bytes.subarray(i, i + 8192));
    return { type: blob.type, width: video.videoWidth, height: video.videoHeight, base64: btoa(binary) };
  });
  await fs.writeFile(info.outputPath(media.type.includes('mp4') ? 'red-title.mp4' : 'red-title.webm'), Buffer.from(media.base64, 'base64'));
  const frames = [];
  for (const time of [.5, duration / 2]) {
    await recorded.evaluate(async (video: HTMLVideoElement, time: number) => {
      await new Promise<void>((resolve, reject) => {
        const timer = setTimeout(() => reject(Error('Recorded title frame did not seek')), 10_000);
        video.addEventListener('seeked', () => { clearTimeout(timer); resolve(); }, { once: true });
        video.currentTime = time;
      });
      await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
    }, time);
    const frame = await measure(page, plan, red, undefined, 'recorded');
    await fs.writeFile(info.outputPath(`recorded-frame-${time.toFixed(2)}.json`), JSON.stringify(frame, null, 2));
    assertPixels(frame, red, `decoded MP4 frame ${time.toFixed(2)}s`);
    frames.push({ time, ...frame });
  }
  await fs.writeFile(info.outputPath('recorded-title-contrast.json'), JSON.stringify({ stage, frames, duration, type: media.type, width: media.width, height: media.height }, null, 2));
  await info.attach('recorded-title-contrast.json', { body: JSON.stringify({ stage, frames, duration, type: media.type, width: media.width, height: media.height }, null, 2), contentType: 'application/json' });
  expect(media.type).toContain('mp4');
  expect(duration).toBeGreaterThan(4.8); expect(duration).toBeLessThan(5.2);
  expect(errors).toEqual([]);
});
