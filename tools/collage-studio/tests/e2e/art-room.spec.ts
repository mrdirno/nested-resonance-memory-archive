// Author: Aldrin Payopay · GPL-3.0-only
// Real sandbox, PNG pixels, media intake and downloaded project archives.
import { test, expect, type Page } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import JSZip from 'jszip';

const ownedInstrument = `<!doctype html><html><body style="margin:0;background:#101528;color:white">
<canvas width="240" height="160" aria-label="Owned test artwork"></canvas>
<script>const c=document.querySelector('canvas'),x=c.getContext('2d');x.fillStyle='#ff3355';x.fillRect(0,0,120,160);x.fillStyle='#22dd99';x.fillRect(120,0,120,160);</script></body></html>`;

async function openNativeRoom(page: Page) {
  const entry=page.getByRole('button',{name:'Art Room',exact:true});
  if(!await entry.isVisible())await page.getByRole('button',{name:'Add',exact:true}).click();
  await entry.click();
}
async function openRoom(page: Page) {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await openNativeRoom(page);
  await page.getByTestId('art-rack').locator('details.art-project-settings > summary').click();
  await page.getByRole('button', { name: 'Open an HTML instrument →', exact: true }).click();
  return page.getByRole('dialog', { name: 'Art Room', exact: true });
}
async function loadHTML(page: Page, html = ownedInstrument, name = 'owned-art.html') {
  await page.getByLabel('Open local art HTML', { exact: true }).setInputFiles({ name, mimeType: 'text/html', buffer: Buffer.from(html) });
}
async function saveArchive(page: Page, filename: string) {
  await page.getByRole('button',{name:'Open',exact:true}).focus();
  const download = page.waitForEvent('download');
  await page.keyboard.press('Control+s');
  await (await download).saveAs(filename);
  const zip = await JSZip.loadAsync(await fs.readFile(filename));
  const manifest = JSON.parse(await zip.file('manifest.json')!.async('text'));
  return { zip, manifest };
}

test('Art Room captures owned HTML pixels and preserves them in a reopened project', async ({ page }, info) => {
  test.setTimeout(90_000);
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  const room = await openRoom(page);
  await loadHTML(page);
  const use = room.getByRole('button', { name: 'Use this artwork', exact: true });
  await expect(use).toBeEnabled();
  await expect(room).toContainText('240');
  const iframe = page.frameLocator('iframe[title$=" — Art Room instrument"]');
  const expectedPNG = await iframe.locator('canvas').evaluate((canvas: HTMLCanvasElement) => canvas.toDataURL('image/png'));
  await use.click();
  await expect(room).toContainText(/added/i);
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
  await expect(page.locator('iframe[title$=" — Art Room instrument"]')).toHaveCount(0);
  const filename = info.outputPath('art-room.collage');
  const first = await saveArchive(page, filename);
  expect(first.manifest.images).toHaveLength(1);
  expect(first.manifest.images[0]).toMatchObject({ width: 240, height: 160 });
  const source = await first.zip.file('images/' + first.manifest.images[0].storageFilename)!.async('nodebuffer');
  expect(source.equals(Buffer.from(expectedPNG.split(',')[1], 'base64'))).toBe(true);
  const choose = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Open', exact: true }).click();
  await (await choose).setFiles(filename);
  await expect(page.getByRole('button', { name: 'Export', exact: true })).toBeVisible();
  const second = await saveArchive(page, info.outputPath('art-room-reopened.collage'));
  expect(second.manifest.images).toHaveLength(1);
  const reopened = await second.zip.file('images/' + second.manifest.images[0].storageFilename)!.async('nodebuffer');
  expect(reopened.equals(source)).toBe(true);
  await page.screenshot({ path: info.outputPath('art-room-imported.png') });
  expect(errors).toEqual([]);
});

test('Art Room starter and host controls fit narrow screens and close disposes the instrument', async ({ page }, info) => {
  test.setTimeout(60_000);
  for (const width of [320, 390, 430]) {
    await page.setViewportSize({ width, height: 664 });
    const room = await openRoom(page);
    const use = room.getByRole('button', { name: 'Use this artwork', exact: true });
    await expect(use).toBeEnabled();
    const box = await room.boundingBox();
    expect(box!.x).toBeGreaterThanOrEqual(0); expect(box!.y).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(width + 1);
    expect(box!.y + box!.height).toBeLessThanOrEqual(665);
    const canvas = page.frameLocator('iframe[title$=" — Art Room instrument"]').locator('canvas').first();
    await expect.poll(() => canvas.evaluate((c: HTMLCanvasElement) => {
      const data = c.getContext('2d')!.getImageData(0, 0, c.width, c.height).data;
      let lit = 0; for (let i = 0; i < data.length; i += 40) if (data[i] + data[i + 1] + data[i + 2] > 80) lit++;
      return lit;
    })).toBeGreaterThan(100);
    for (const control of await room.locator('button, select, a').all()) {
      if (!(await control.isVisible())) continue;
      await control.scrollIntoViewIfNeeded();
      const geometry = await control.evaluate(e => {
        const b = e.getBoundingClientRect(), hit = document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2);
        return { x: b.x, right: b.right, w: b.width, h: b.height, hit: hit === e || e.contains(hit) };
      });
      expect(geometry.w).toBeGreaterThanOrEqual(43.5); expect(geometry.h).toBeGreaterThanOrEqual(43.5);
      expect(geometry.x).toBeGreaterThanOrEqual(0); expect(geometry.right).toBeLessThanOrEqual(width + 1);
      expect(geometry.hit).toBe(true);
    }
    await page.screenshot({ path: info.outputPath(`art-room-${width}.png`) });
    await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
    await expect(page.locator('iframe[title$=" — Art Room instrument"]')).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Art Room', exact: true })).toBeFocused();
  }
});

test('Art Room blocks parent access and network resources while preserving local canvas execution', async ({ page }) => {
  test.setTimeout(60_000);
  const requests: string[] = [];
  // A request event can describe a CSP-blocked attempt. The route callback
  // records attempts admitted to networking; the policy must stop them first.
  await page.route('https://art-room-boundary.invalid/**', route => { requests.push(route.request().url()); return route.abort(); });
  const room = await openRoom(page);
  await loadHTML(page, ownedInstrument.replace('</body>', `<script>
    let result=[];try{parent.document.body.dataset.artEscape='yes';result.push('escaped')}catch(e){result.push('parent blocked')}
    try{localStorage.setItem('artEscape','yes');result.push('stored')}catch(e){result.push('storage blocked')}
    let violations=[];document.addEventListener('securitypolicyviolation',e=>{violations.push(e.effectiveDirective);document.body.dataset.violations=violations.join(',')});
    fetch('https://art-room-boundary.invalid/fetch').catch(()=>{});
    const image=new Image();image.src='https://art-room-boundary.invalid/pixel.png';
    document.body.dataset.boundary=result.join(',');
  </script></body>`));
  const frame = page.frameLocator('iframe[title$=" — Art Room instrument"]');
  await expect(frame.locator('body')).toHaveAttribute('data-boundary', 'parent blocked,storage blocked');
  await expect(frame.locator('body')).toHaveAttribute('data-violations', /connect-src/);
  await expect(frame.locator('body')).toHaveAttribute('data-violations', /img-src/);
  await expect(room.getByRole('button', { name: 'Use this artwork', exact: true })).toBeEnabled();
  expect(await page.locator('body').getAttribute('data-art-escape')).toBeNull();
  expect(requests).toEqual([]);
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
});

test('Art Room rejects malformed PNG and retires captures when the instrument is replaced', async ({ page }, info) => {
  test.setTimeout(60_000);
  const room = await openRoom(page);
  await loadHTML(page, ownedInstrument.replace('</body>', `<script>document.querySelector('canvas').toBlob=cb=>cb(new Blob(['invalid PNG'],{type:'image/png'}));</script></body>`));
  await room.getByRole('button', { name: 'Use this artwork', exact: true }).click();
  await expect(room.getByRole('alert')).toContainText(/PNG/);
  await loadHTML(page, ownedInstrument.replace('</body>', `<script>const nativeBlob=HTMLCanvasElement.prototype.toBlob;document.querySelector('canvas').toBlob=function(cb,type){const self=this;setTimeout(()=>nativeBlob.call(self,cb,type),900);};</script></body>`));
  await room.getByRole('button', { name: 'Use this artwork', exact: true }).click();
  await expect(room.getByRole('button', { name: 'Adding artwork…', exact: true })).toBeVisible();
  await room.getByRole('button', { name: 'Original instrument', exact: true }).click();
  await expect(room.getByRole('button', { name: 'Use this artwork', exact: true })).toBeEnabled();
  await page.waitForTimeout(1100); // Cross the retired child's encode deadline.
  await expect(room.getByRole('status')).toHaveCount(0);
  await loadHTML(page);
  await room.getByRole('button', { name: 'Use this artwork', exact: true }).click();
  await expect(room).toContainText(/added/i);
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
  const { manifest } = await saveArchive(page, info.outputPath('only-current-art.collage'));
  expect(manifest.images).toHaveLength(1);
  expect(manifest.images[0]).toMatchObject({ width: 240, height: 160 });
});

test('closing Art Room during the parent image decode never adds late pixels', async ({ page }) => {
  test.setTimeout(60_000);
  await page.addInitScript(() => {
    if (window !== window.top) return;
    const descriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src')!;
    let blobs = 0;
    (window as any).artParentDecodeHeld = false;
    Object.defineProperty(HTMLImageElement.prototype, 'src', {
      configurable: true, get: descriptor.get,
      set(value: string) {
        // The first decode validates PNG dimensions; the second is App intake.
        if (String(value).startsWith('blob:') && ++blobs === 2) {
          (window as any).artParentDecodeHeld = true;
          setTimeout(() => descriptor.set!.call(this, value), 900);
        } else descriptor.set!.call(this, value);
      },
    });
  });
  const room = await openRoom(page);
  await loadHTML(page);
  await room.getByRole('button', { name: 'Use this artwork', exact: true }).click();
  await expect.poll(() => page.evaluate(() => (window as any).artParentDecodeHeld)).toBe(true);
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
  await expect(page.locator('iframe[title$=" — Art Room instrument"]')).toHaveCount(0);
  await page.waitForTimeout(1300); // The actual delayed browser decode resolves.
  await expect(page.getByRole('button', { name: 'Load source images or video', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Export', exact: true })).toHaveCount(0);
  await expect(page.getByText('Adding artwork…', { exact: true })).toHaveCount(0);
});

test('Art Room host shortcuts preserve a lyric draft behind the dialog', async ({ page }) => {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.getByRole('button', { name: 'Try a lyric film', exact: true }).click();
  await page.getByRole('button',{name:'Text',exact:true}).click();
  const draft = page.locator('textarea[placeholder="Paste the lines you want in this take"]');
  await draft.fill('THE WORDS I AM STILL WRITING');
  await openNativeRoom(page);
  const room = page.getByRole('dialog', { name: 'Art Room', exact: true });
  const close = room.getByRole('button', { name: 'Close Art Room', exact: true });
  for (const key of ['Control+z', 'Meta+z', 'Control+Shift+z', 'Meta+s', 'Control+e', 'Control+o']) {
    await close.focus(); await page.keyboard.press(key);
    await expect(room).toBeVisible();
  }
  await close.click();
  await expect(page.getByRole('button', { name: 'Art Room', exact: true })).toBeFocused();
  await page.getByRole('button',{name:'Text',exact:true}).click();
  await expect(draft).toBeVisible();
  await expect(draft).toHaveValue('THE WORDS I AM STILL WRITING');
});

test('Art Room can capture a completed Bifurcata band from a local user-selected HTML file', async ({ page }, info) => {
  test.setTimeout(180_000);
  const bifurcata = process.env.ART_ROOM_BIFURCATA_HTML;
  test.skip(!bifurcata, 'Explicit local integration fixture; proprietary instrument is never bundled.');
  const room = await openRoom(page);
  await page.getByLabel('Open local art HTML', { exact: true }).setInputFiles(path.resolve(bifurcata!));
  await expect(page.locator('iframe[title$=" — Art Room instrument"]')).toHaveAttribute('title', /index\.html/);
  await room.getByRole('button', { name: 'Show artwork', exact: true }).click();
  const use = room.getByRole('button', { name: 'Use this artwork', exact: true });
  await expect(use).toBeEnabled({ timeout: 120_000 });
  const canvas = page.frameLocator('iframe[title$=" — Art Room instrument"]').locator('.band.ready > canvas').first();
  await expect(canvas).toBeVisible({ timeout: 120_000 });
  await page.screenshot({ path: info.outputPath('bifurcata-in-art-room.png'), timeout: 15000 });
  await use.click();
  await expect(room).toContainText(/added/i);
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
  const { manifest } = await saveArchive(page, info.outputPath('bifurcata-capture.collage'));
  expect(manifest.images).toHaveLength(1);
  expect(manifest.images[0].width).toBeGreaterThan(100);
  expect(manifest.images[0].height).toBeGreaterThan(100);
});
