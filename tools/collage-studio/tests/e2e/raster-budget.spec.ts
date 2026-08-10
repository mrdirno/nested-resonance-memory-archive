// tests/e2e/raster-budget.spec.ts
// -----------------------------------------------------------------------------
// THE OFFLINE RENDER STAYS INSIDE ITS MEMORY BUDGET — GRADED ON THE REAL STAGE,
// WITH REAL DECODED IMAGES, READING THE NUMBER THE RENDER ITSELF REPORTS.
//
// Wish (bug, collage/export): "The video export crashes when rendering higher
// than 2k", and alongside it "once it reaches a recursive threshold you
// shouldn't be trying to load the high resolution in each frame ... fallbacks
// ... so that higher resolutions don't crash but allow for the chance to render
// highest quality images in each layout in every photo".
//
// WHY THIS EXISTS WHEN tests/unit/rasterBudget.invariants.mjs ALREADY SWEEPS IT.
// The unit sweep grades the ARITHMETIC: given a cap, is the raster inside it.
// It cannot see the WIRING, and the wiring is where a budget of this shape
// actually fails — `Stage.prepareOfflineStills` has to commit against the
// ledger exactly once per source, on the success path AND on every refusal,
// failure, abort and timeout break. Miss one commit and the arithmetic stays
// perfect while the pool quietly runs over, because every source behind the
// missed one is dividing a budget it thinks is smaller than it is. So this
// asks the REAL loop, over REAL decodes, and reads the report back.
//
// THE TWO FAILURES IT IS BUILT TO CATCH, and they pull in opposite directions:
//
//   TOO LOOSE — the pool is exceeded and the tab dies. That is the reported
//     bug. Asserted directly against `usedPx <= budgetPx`, and asserted again
//     at four times the source count, because the old path was LINEAR in
//     sources with no ceiling: a bound that holds at n=8 and drifts at n=32
//     has not fixed the crash, it has moved it.
//
//   TOO TIGHT — nothing crashes and every fragment quietly comes back softer
//     than the preview the user was already looking at, or missing. That is
//     the same bug wearing a quieter coat, and it is the one a memory test
//     passes with flying colours. So the frame is MEASURED: a starved render
//     must still be a picture, and must be no worse than the thumbnail render
//     it degrades to.
//
// Run (dev):  npx playwright test tests/e2e/raster-budget.spec.ts --project=chromium
//   NOTE: the in-page `import('/src/lib/stage.ts')` is a DEV-SERVER path. Against
//   a built deploy the specifier does not exist, so these skip themselves rather
//   than pass vacuously — the same rule video-resolution.spec.ts follows.
// -----------------------------------------------------------------------------

import { test, expect, type Page } from '@playwright/test';

const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const STAGE_MOD = '/src/lib/stage.ts';

const devModules = async (page: Page): Promise<boolean> =>
  page.evaluate(async (m) => {
    try { await import(/* @vite-ignore */ m); return true; } catch { return false; }
  }, STAGE_MOD);

interface Report {
  requested: number; full: number; fellBack: number;
  budgetPx: number; usedPx: number; clamped: number;
}
interface Take { report: Report; ink: number; w: number; h: number; cells: number; fullImgLoads: number }

/**
 * Build a scene of `n` distinct large photographs, run the offline still pass,
 * and return both the render's own account of what it spent and a measurement
 * of what actually landed on the canvas.
 *
 * The sources are DELIBERATELY LARGER THAN THEIR FRAGMENTS and cropped by the
 * grid, which is the whole point: a fragment shows a CROP, so the raster the
 * old code asked for was the crop factor SQUARED times the destination area.
 * A scene of small sources cannot reproduce the bug at any source count.
 */
const runPass = (page: Page, n: number, maxWidth: number, budgetPx?: number) =>
  page.evaluate(async ({ modUrl, n, maxWidth, budgetPx }) => {
    const mod = await import(/* @vite-ignore */ modUrl);

    const SRC = 2400;   // each source: 5.8 MP, a modest phone photo
    const THUMB = 1024; // what the app really binds for the preview

    // A photograph, not a flat fill: flat colour survives ANY downsample, so a
    // scene made of it could not tell a full raster from a thumbnail. Fine
    // structure is what makes the ink measurement below mean something.
    const photo = (i: number, size: number): string => {
      const c = document.createElement('canvas');
      c.width = size; c.height = size;
      const x = c.getContext('2d')!;
      x.fillStyle = `hsl(${(i * 47) % 360} 70% 45%)`;
      x.fillRect(0, 0, size, size);
      x.fillStyle = `hsl(${(i * 47 + 180) % 360} 80% 70%)`;
      const period = Math.max(4, Math.round(size / 150));
      for (let p = 0; p < size; p += period * 2) x.fillRect(p, 0, period, size);
      return c.toDataURL('image/png');
    };
    const downscale = async (dataUrl: string, to: number): Promise<string> => {
      const img = new Image(); img.src = dataUrl; await img.decode();
      const c = document.createElement('canvas');
      c.width = to; c.height = to;
      c.getContext('2d')!.drawImage(img, 0, 0, img.width, img.height, 0, 0, to, to);
      return c.toDataURL('image/png');
    };

    const assets = [];
    for (let i = 0; i < n; i++) {
      const full = photo(i, SRC);
      assets.push({
        id: `a${i}`, src: full, previewSrc: await downscale(full, THUMB),
        width: SRC, height: SRC,
        analysis: { color: { r: 128, g: 128, b: 128 } },
      });
    }

    // A square grid, so every fragment is a CROP of a square source at a
    // different aspect — an ordinary cover-fit, exactly the k > 1 case.
    const L = 1200;
    const cols = Math.ceil(Math.sqrt(n));
    const rows = Math.ceil(n / cols);
    const cw = L / cols, ch = L / rows;
    const layoutItems = assets.map((_, i) => {
      const cx = (i % cols) * cw, cy = Math.floor(i / cols) * ch;
      return {
        id: `i${i}`,
        path: [{ x: cx, y: cy }, { x: cx + cw, y: cy }, { x: cx + cw, y: cy + ch }, { x: cx, y: cy + ch }],
        bounds: { x: cx, y: cy, w: cw, h: ch },
      };
    });

    const cv = document.createElement('canvas');
    cv.style.width = '600px'; cv.style.height = '600px';
    document.body.appendChild(cv);
    const stage = mod.createStage(cv, {});
    stage.setScene({ layoutItems, orderedAssets: assets, mode: 'simple', aspect: 1, bgColor: '#000' });
    // Let the previews bind, so a fallback really is "keep the thumbnail" and
    // not "there was never anything there".
    await new Promise((r) => setTimeout(r, 1200));

    // COUNT THE FULL-RESOLUTION <img> DECODES THE OFFLINE PASS STARTS.
    //
    // The pool bounds the RASTERS. It cannot see an allocation made upstream of
    // it, and there was one: pointing every fragment's stillKey at its original
    // made `ensureStills` start an <img> per source, ALL AT ONCE, each decode
    // retained for the whole take. That peak is linear in source count and in
    // source area, it happened before the budget ran, and it dwarfed everything
    // the budget did control — the budget was doing careful arithmetic
    // downstream of the allocation that actually killed the tab.
    //
    // Counting STARTS rather than concurrent liveness on purpose: every one of
    // those decodes is kept in `this.stills`, so a start IS a resident decode.
    const fullSrcs = new Set(assets.map((a) => a.src));
    const desc = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src')!;
    let fullImgLoads = 0;
    const RealImage = window.Image;
    (window as unknown as { Image: unknown }).Image = function PatchedImage(this: unknown) {
      const img = new RealImage();
      Object.defineProperty(img, 'src', {
        configurable: true,
        get() { return desc.get!.call(img); },
        set(v: string) { if (fullSrcs.has(v)) fullImgLoads++; desc.set!.call(img, v); },
      });
      return img;
    };

    stage.beginOfflineRender({ maxWidth, fullRes: true });
    const report = await stage.prepareOfflineStills(
      budgetPx === undefined ? { timeoutMs: 30000 } : { timeoutMs: 30000, budgetPx },
    );
    await stage.renderAtTime(0);
    (window as unknown as { Image: unknown }).Image = RealImage;

    // INK: the share of sampled pixels carrying picture rather than background.
    // A hole, a black frame or a half-drawn scene all collapse this; softness
    // does not. It is the "never a hole" half of the claim, measured.
    const x = cv.getContext('2d')!;
    const S = 64;
    const t = document.createElement('canvas'); t.width = S; t.height = S;
    t.getContext('2d')!.drawImage(cv, 0, 0, S, S);
    const d = t.getContext('2d')!.getImageData(0, 0, S, S).data;
    let lit = 0;
    for (let i = 0; i < d.length; i += 4) {
      if (d[i] > 12 || d[i + 1] > 12 || d[i + 2] > 12) lit++;
    }
    // `cells` is reported so the caller can DERIVE the coverage it should see
    // instead of guessing one: n photos in a cols x rows grid leave cols*rows-n
    // cells legitimately empty, and a hardcoded threshold would read those as a
    // hole in the render. The test must know its own fixture's geometry.
    const out = { report, ink: lit / (S * S), w: cv.width, h: cv.height, cells: cols * rows, fullImgLoads };

    stage.endOfflineRender();
    stage.destroy();
    cv.remove();
    return out;
  }, { modUrl: STAGE_MOD, n, maxWidth, budgetPx });

test.describe('the offline render stays inside its memory budget', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await page.waitForLoadState('domcontentloaded');
  });

  test('B1: the pool is never exceeded, and every source is accounted for', async ({ page }) => {
    test.skip(!(await devModules(page)), 'Stage module needs the dev server');
    const take = (await runPass(page, 12, 4096)) as Take;
    const r = take.report;
    console.log('B1 report:', JSON.stringify(r));

    expect(r.requested).toBe(12);
    // No source may vanish between "asked for" and "resolved" — a source that
    // is neither upgraded nor explicitly fallen back is one drawing nothing.
    expect(r.full + r.fellBack).toBe(r.requested);
    expect(r.budgetPx).toBeGreaterThan(0);
    // THE CRASH, MEASURED THROUGH THE REAL LOOP.
    expect(r.usedPx).toBeLessThanOrEqual(r.budgetPx);
    // And the render is a picture, not a black rectangle. The bar is the grid's
    // OWN coverage — every cell that has a photo must be carrying one.
    expect(take.ink).toBeGreaterThan((12 / take.cells) * 0.97);
  });

  test('B2: four times the photos does NOT cost four times the memory', async ({ page }) => {
    test.skip(!(await devModules(page)), 'Stage module needs the dev server');
    const small = (await runPass(page, 8, 4096)) as Take;
    const big = (await runPass(page, 32, 4096)) as Take;
    console.log('B2 small:', JSON.stringify(small.report));
    console.log('B2 big:  ', JSON.stringify(big.report));

    expect(small.report.usedPx).toBeLessThanOrEqual(small.report.budgetPx);
    expect(big.report.usedPx).toBeLessThanOrEqual(big.report.budgetPx);
    // Same canvas, same device => the same pool, whatever the photo count. This
    // is the property the old geometry-only path did not have and the reason
    // the report reads "crashes above 2K" rather than "crashes at n=37".
    expect(big.report.budgetPx).toBe(small.report.budgetPx);
    // 4x the sources must not buy 4x the resident raster.
    expect(big.report.usedPx).toBeLessThan(small.report.usedPx * 2);
    expect(big.report.full + big.report.fellBack).toBe(32);
    expect(big.ink).toBeGreaterThan((32 / big.cells) * 0.97);
  });

  test('B4: the pass never puts every original in memory at once', async ({ page }) => {
    test.skip(!(await devModules(page)), 'Stage module needs the dev server');
    const small = (await runPass(page, 8, 4096)) as Take;
    const big = (await runPass(page, 32, 4096)) as Take;
    console.log(`B4 full-res <img> decodes started: n=8 -> ${small.fullImgLoads}, n=32 -> ${big.fullImgLoads}`);

    // THE ALLOCATION THE POOL COULD NOT SEE. beginOfflineRender repointed every
    // stillKey at its original and let ensureStills start them ALL in parallel,
    // each decode retained for the take — n full-resolution images resident
    // before the budget had counted anything. It is the crash the pool was
    // written to stop, sitting upstream of the pool.
    //
    // Asserted as "does not scale with source count" rather than a fixed
    // number, because the number is not the property: 8 would be as wrong as
    // 32 if it were 8 originals held at once.
    expect(big.fullImgLoads).toBeLessThanOrEqual(small.fullImgLoads);
    expect(big.fullImgLoads).toBeLessThan(32);
    // And the render still resolved every source, so the fetching that moved
    // out of beginOfflineRender really happens somewhere.
    expect(big.report.full + big.report.fellBack).toBe(32);
    expect(big.ink).toBeGreaterThan((32 / big.cells) * 0.97);
  });

  test('B3: a starved budget degrades to the preview — never to a hole', async ({ page }) => {
    test.skip(!(await devModules(page)), 'Stage module needs the dev server');
    // One pixel of pool. Nothing can be lifted, so this is the worst case the
    // budget can ever produce, and it must still be a complete picture.
    const starved = (await runPass(page, 12, 4096, 1)) as Take;
    console.log('B3 starved:', JSON.stringify(starved.report));

    expect(starved.report.requested).toBe(12);
    expect(starved.report.usedPx).toBeLessThanOrEqual(1);
    // Every source kept what it already had — that is the floor doing its job.
    expect(starved.report.fellBack).toBe(12);
    expect(starved.report.full).toBe(0);
    // THE QUIET FAILURE, RULED OUT: an unlifted fragment still draws its
    // thumbnail, so the frame is whole even when the pool bought nothing.
    expect(starved.ink).toBeGreaterThan((12 / starved.cells) * 0.97);
    expect(starved.w).toBeGreaterThan(2000);
  });
});
