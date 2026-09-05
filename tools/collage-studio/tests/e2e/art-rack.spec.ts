// Author: Aldrin Payopay · GPL-3.0-only
// Public Art Room UI, real Canvas pixels, downloads and durable browser storage.
// COLLAGE_BASE_URL can point the same checks at the deployed application.
import { test, expect, type Locator, type Page } from '@playwright/test';
import fs from 'node:fs/promises';
import { createHash } from 'node:crypto';
import JSZip from 'jszip';

test.use({ actionTimeout: 15_000 });
const names = ['Contour Atlas', 'Petal Engine', 'Orbit Press', 'Ribbon Choir', 'Branch Fans', 'Prism Garden', 'Woven Circuit', 'Satellite Dust'];
const sha = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex');
async function showRoom(page: Page) {
  const entry=page.getByRole('button', { name: /^Art Room(?:$| )/ });
  if(!await entry.isVisible())await page.getByRole('button',{name:'Add',exact:true}).click();
  await entry.click();
  const room = page.getByTestId('art-rack');
  await expect(room).toBeVisible();
  return room;
}
async function bootRoom(page: Page) {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  return showRoom(page);
}
async function settings(room: Locator) {
  const details = room.locator('details.art-project-settings');
  if (await details.getAttribute('open') === null) await details.locator('summary').click();
}
async function saveRecipe(page: Page, room: Locator) {
  await settings(room);
  const download = page.waitForEvent('download');
  await room.getByRole('button', { name: 'Save recipe', exact: true }).click();
  return JSON.parse(await fs.readFile((await (await download).path())!, 'utf8'));
}
async function saveArchive(page: Page, filename: string) {
  // A range/select can retain focus after an edit; the host deliberately ignores
  // shortcuts from inputs. Focus a real non-input host control before saving.
  await page.getByRole('button', { name: 'Open', exact: true }).focus();
  const download = page.waitForEvent('download');
  await page.keyboard.press('Control+s');
  await (await download).saveAs(filename);
  const zip = await JSZip.loadAsync(await fs.readFile(filename));
  const manifest = JSON.parse(await zip.file('manifest.json')!.async('text'));
  return { zip, manifest };
}
async function seek(room: Locator, time: number) {
  const pause = room.getByRole('button', { name: 'Pause art preview', exact: true });
  if (await pause.isVisible()) await pause.click();
  const playhead = room.getByLabel('Art playhead', { exact: true });
  await playhead.evaluate((element: HTMLInputElement, value) => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(element, String(value));
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }, time);
  await expect(playhead).toHaveValue(String(time));
  await expect(room.locator('.art-transport output')).toHaveText(`${time.toFixed(1)} / 8s`);
  await room.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
}
async function pixels(canvas: Locator) {
  return canvas.evaluate((c: HTMLCanvasElement) => {
    const bytes = c.getContext('2d')!.getImageData(0, 0, c.width, c.height).data;
    let hash = 2166136261;
    const colors = new Set<number>();
    for (let i = 0; i < bytes.length; i += 4) {
      const value = ((bytes[i] << 24) | (bytes[i + 1] << 16) | (bytes[i + 2] << 8) | bytes[i + 3]) >>> 0;
      hash = Math.imul(hash ^ value, 16777619);
      if (i % 128 === 0) colors.add(value);
    }
    return { hash: hash >>> 0, colors: colors.size, width: c.width, height: c.height };
  });
}
async function sessionSnapshot(page: Page): Promise<any> {
  return page.evaluate(async () => {
    const db = await new Promise<IDBDatabase>((resolve, reject) => {
      const q = indexedDB.open('collage-session'); q.onsuccess = () => resolve(q.result); q.onerror = () => reject(q.error);
    });
    try {
      if (!db.objectStoreNames.contains('project') || !db.objectStoreNames.contains('assets')) return null;
      const row = await new Promise<any>((resolve, reject) => {
        const q = db.transaction('project').objectStore('project').get('current');
        q.onsuccess = () => resolve(q.result); q.onerror = () => reject(q.error);
      });
      const image = row?.manifest?.images?.[0]; if (!image) return null;
      const assets = await new Promise<{ keys: IDBValidKey[]; asset: any }>((resolve, reject) => {
        const tx = db.transaction('assets'), store = tx.objectStore('assets');
        const keys = store.getAllKeys(), asset = store.get(image.id);
        tx.oncomplete = () => resolve({ keys: keys.result, asset: asset.result }); tx.onerror = () => reject(tx.error);
      });
      if (!assets.asset?.full) return null;
      const bytes = assets.asset.full instanceof Blob ? await assets.asset.full.arrayBuffer() : assets.asset.full;
      const digest = await crypto.subtle.digest('SHA-256', bytes);
      return { manifest: row.manifest, keys: assets.keys, posterHash: [...new Uint8Array(digest)].map(n => n.toString(16).padStart(2, '0')).join('') };
    } finally { db.close(); }
  });
}

test('Art Rack opens eight real templates and preserves layer controls, dice locks and invalid-file refusal', async ({ page }) => {
  test.setTimeout(90_000);
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  const room = await bootRoom(page);
  await expect(room.getByRole('tab', { name: /^Templates/ })).toHaveAttribute('aria-selected', 'true');
  const hashes: number[] = [];
  for (const name of names) {
    const tile = room.getByRole('button', { name: `Add ${name}`, exact: true });
    await expect(tile).toBeAttached();
    const image = await pixels(tile.locator('canvas'));
    expect(image.colors, `${name} draws actual non-flat pixels`).toBeGreaterThan(5);
    hashes.push(image.hash);
  }
  expect(new Set(hashes).size, 'eight visually distinct template previews').toBe(8);
  await room.getByRole('button', { name: 'Add Orbit Press', exact: true }).click();
  await expect(room.getByRole('tabpanel', { name: 'Layers', exact: true })).toBeVisible();
  const initial = await saveRecipe(page, room);
  expect(initial.layers).toHaveLength(4);
  const orbitId = initial.layers.find((layer: any) => layer.kind === 'rings').id;
  const contourId = initial.layers.find((layer: any) => layer.kind === 'contour').id;
  await room.getByRole('button', { name: 'Disable Contour Atlas layer', exact: true }).click();
  await room.locator('details.art-layer-options > summary').click();
  await room.getByRole('button', { name: 'Lock Orbit Press dice', exact: true }).click();
  await room.getByRole('button', { name: 'Solo Orbit Press layer', exact: true }).click();
  await room.getByRole('button', { name: 'Move layer down', exact: true }).click();
  const held = await saveRecipe(page, room);
  expect(held.soloId).toBe(orbitId);
  expect(held.layers.findIndex((layer: any) => layer.id === orbitId)).toBe(2);
  expect(held.layers.find((layer: any) => layer.id === contourId).enabled).toBe(false);
  expect(held.layers.find((layer: any) => layer.id === orbitId).locked).toBe(true);
  await room.getByRole('button', { name: 'Dice rack', exact: true }).click();
  const rolled = await saveRecipe(page, room);
  expect(rolled.layers.find((layer: any) => layer.id === orbitId)).toEqual(held.layers.find((layer: any) => layer.id === orbitId));
  expect(rolled.layers.find((layer: any) => layer.id === contourId)).toEqual(held.layers.find((layer: any) => layer.id === contourId));
  expect(rolled.layers.filter((layer: any) => layer.enabled && !layer.locked)).not.toEqual(held.layers.filter((layer: any) => layer.enabled && !layer.locked));
  await room.getByRole('button', { name: 'Undo art edit', exact: true }).click();
  expect(await saveRecipe(page, room)).toEqual(held);
  await room.getByRole('button', { name: 'Redo art edit', exact: true }).click();
  expect(await saveRecipe(page, room)).toEqual(rolled);
  await room.getByLabel('Open art recipe', { exact: true }).setInputFiles({ name: 'broken.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify({ ...rolled, layers: [...rolled.layers, { kind: 'unsupported' }] })) });
  await expect(room.getByRole('alert')).toBeVisible();
  expect(await saveRecipe(page, room), 'bad JSON cannot replace the working recipe').toEqual(rolled);
  expect(errors).toEqual([]);
});

test('Art Rack paused pixels repeat exactly after out-of-order scrubbing and animate across time', async ({ page }) => {
  const room = await bootRoom(page);
  const preview = room.getByLabel('Animated art preview', { exact: true });
  // Warm the readback path before comparing: Chromium can switch raster
  // backends after repeated getImageData calls. Compare one backend consistently.
  await seek(room, 0.01); await pixels(preview);
  await seek(room, 0.02); await pixels(preview);
  await seek(room, 1.25); const first = await pixels(preview);
  expect(first.colors).toBeGreaterThan(100);
  await seek(room, 3.25); const second = await pixels(preview);
  expect(second.hash).not.toBe(first.hash);
  await seek(room, 7.37);
  await seek(room, 1.25); expect(await pixels(preview)).toEqual(first);
  await seek(room, 0); const start = await pixels(preview);
  await seek(room, 8); expect(await pixels(preview)).toEqual(start);
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
});

test('editable Art Rack survives save, reopen, asset replacement and real crash recovery with the current poster', async ({ page }, info) => {
  test.setTimeout(120_000);
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  let room = await bootRoom(page);
  const originalRecipe = await saveRecipe(page, room);
  await room.getByRole('button', { name: 'Add artwork', exact: true }).click();
  await expect(room.locator('.art-footer p[role="status"]')).toContainText('Editable artwork applied', { timeout: 30_000 });
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
  const originalFile = info.outputPath('art-rack-original.collage');
  const first = await saveArchive(page, originalFile);
  expect(first.manifest.images).toHaveLength(1);
  expect(first.manifest.images[0].art).toEqual(originalRecipe);
  const oldId = first.manifest.images[0].id;
  const oldPoster = await first.zip.file('images/' + first.manifest.images[0].storageFilename)!.async('nodebuffer');
  // Reopen into a fresh editor; no already-open recipe can make this pass.
  await page.reload();
  const chooser = page.waitForEvent('filechooser');
  await page.getByRole('button', { name: 'Open', exact: true }).click();
  await (await chooser).setFiles(originalFile);
  await expect(page.getByRole('button', { name: 'Export', exact: true })).toBeVisible();
  room = await showRoom(page);
  await settings(room);
  await room.getByLabel('Editing artwork', { exact: true }).selectOption(oldId);
  expect(await saveRecipe(page, room)).toEqual(originalRecipe);
  await room.getByRole('tab', { name: /^Layers/ }).click();
  await room.getByRole('button', { name: 'Select Petal Engine layer', exact: true }).click();
  await room.getByLabel('Layer palette', { exact: true }).selectOption('ember');
  const updatedRecipe = await saveRecipe(page, room);
  expect(updatedRecipe).not.toEqual(originalRecipe);
  await room.getByRole('button', { name: 'Update artwork', exact: true }).click();
  await expect(room.locator('.art-footer p[role="status"]')).toContainText('Editable artwork applied', { timeout: 30_000 });
  await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
  const second = await saveArchive(page, info.outputPath('art-rack-updated.collage'));
  expect(second.manifest.images).toHaveLength(1);
  const current = second.manifest.images[0];
  expect(current.id, 'a new immutable asset ID makes autosave write current poster bytes').not.toBe(oldId);
  expect(current.art).toEqual(updatedRecipe);
  const poster = await second.zip.file('images/' + current.storageFilename)!.async('nodebuffer');
  expect(poster.equals(oldPoster)).toBe(false);
  await expect.poll(async () => (await sessionSnapshot(page))?.manifest.images[0].id, { timeout: 20_000 }).toBe(current.id);
  const durable = await sessionSnapshot(page);
  expect(durable.manifest.images[0].art).toEqual(updatedRecipe);
  expect(durable.keys).toEqual([current.id]);
  expect(durable.posterHash).toBe(sha(poster));
  await page.reload();
  await page.getByRole('button', { name: 'Restore', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Export', exact: true })).toBeVisible();
  const recovered = await saveArchive(page, info.outputPath('art-rack-recovered.collage'));
  expect(recovered.manifest.images).toHaveLength(1);
  expect(recovered.manifest.images[0].art).toEqual(updatedRecipe);
  const restoredPoster = await recovered.zip.file('images/' + recovered.manifest.images[0].storageFilename)!.async('nodebuffer');
  expect(restoredPoster.equals(poster)).toBe(true);
  room = await showRoom(page);
  await settings(room);
  await room.getByLabel('Editing artwork', { exact: true }).selectOption(current.id);
  expect(await saveRecipe(page, room)).toEqual(updatedRecipe);
  expect(errors).toEqual([]);
});

test('Art Rack controls remain real 44px targets at 320px, 390px and a short phone viewport', async ({ page }, info) => {
  test.setTimeout(120_000);
  for (const viewport of [{ width: 320, height: 664 }, { width: 390, height: 664 }, { width: 320, height: 448 }]) {
    await page.setViewportSize(viewport);
    const room = await bootRoom(page);
    const box = await room.boundingBox();
    expect(box!.x).toBeGreaterThanOrEqual(0); expect(box!.y).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(viewport.width + 1);
    expect(box!.y + box!.height).toBeLessThanOrEqual(viewport.height + 1);
    expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
    const previewBox = await room.getByLabel('Animated art preview', { exact: true }).boundingBox();
    expect(previewBox!.height, 'the artwork remains large enough to inspect').toBeGreaterThanOrEqual(viewport.height < 530 ? 60 : 140);
    for (const name of ['Close Art Room', 'Add artwork']) {
      const button = room.getByRole('button', { name, exact: true });
      const geometry = await button.evaluate(e => {
        const b = e.getBoundingClientRect(), hit = document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2);
        return { x: b.x, y: b.y, right: b.right, bottom: b.bottom, w: b.width, h: b.height, hit: hit === e || e.contains(hit) };
      });
      expect(geometry.w, name).toBeGreaterThanOrEqual(43.5); expect(geometry.h, name).toBeGreaterThanOrEqual(43.5);
      expect(geometry.x).toBeGreaterThanOrEqual(0); expect(geometry.y).toBeGreaterThanOrEqual(0);
      expect(geometry.right).toBeLessThanOrEqual(viewport.width + 1); expect(geometry.bottom).toBeLessThanOrEqual(viewport.height + 1);
      expect(geometry.hit, `${name} is actually hittable at ${viewport.width} × ${viewport.height}`).toBe(true);
    }
    const tile = room.getByRole('button', { name: 'Add Woven Circuit', exact: true });
    await tile.click();
    await expect(room.getByRole('button', { name: 'Select Woven Circuit layer', exact: true })).toBeVisible();
    await room.getByRole('button', { name: 'Add artwork', exact: true }).click();
    await expect(room.locator('.art-footer p[role="status"]')).toContainText('Editable artwork applied', { timeout: 30_000 });
    await page.screenshot({ path: info.outputPath(`art-rack-${viewport.width}-${viewport.height}.png`) });
    await room.getByRole('button', { name: 'Close Art Room', exact: true }).click();
    await expect(page.getByTestId('art-rack')).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Add', exact: true })).toBeFocused();
  }
});

test('switching recipe sources keeps the next edit undoable and mixed media clears a stale loop choice', async ({ page }) => {
  test.setTimeout(60_000);
  const room=await bootRoom(page);
  const png=await room.getByLabel('Animated art preview',{exact:true}).evaluate((c:HTMLCanvasElement)=>c.toDataURL());
  await room.getByRole('button',{name:'Add artwork',exact:true}).click();
  await expect(room.locator('.art-footer p[role="status"]')).toContainText('Editable artwork applied');
  await room.getByRole('tab',{name:/^Layers/}).click();
  await room.getByLabel('Opacity',{exact:true}).fill('0.3');
  await settings(room);
  await room.getByLabel('Editing artwork',{exact:true}).selectOption('');
  await room.getByLabel('Opacity',{exact:true}).fill('0.55');
  await expect(room.getByRole('button',{name:'Undo art edit',exact:true})).toBeEnabled();
  await room.getByRole('button',{name:'Undo art edit',exact:true}).click();
  await expect(room.getByLabel('Opacity',{exact:true})).toHaveValue('0.8');
  await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
  await page.getByRole('button',{name:'Export',exact:true}).click();
  let sheet=page.getByRole('dialog',{name:'Export',exact:true});
  await expect(sheet.getByRole('button',{name:'Loop 8s',exact:true})).toHaveAttribute('aria-pressed','true');
  await sheet.getByRole('button',{name:'Close',exact:true}).click();
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles({name:'frozen-owned-art.png',mimeType:'image/png',buffer:Buffer.from(png.split(',')[1],'base64')});
  await page.getByRole('button',{name:'Export',exact:true}).click();
  sheet=page.getByRole('dialog',{name:'Export',exact:true});
  await expect(sheet.getByRole('button',{name:'Loop 8s',exact:true})).toHaveCount(0,{timeout:30_000});
  await expect(sheet.getByRole('button',{name:'10s',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(sheet.getByRole('button',{name:'Record 10s video',exact:true})).toBeVisible();
});
