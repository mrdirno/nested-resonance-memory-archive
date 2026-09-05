/**
 * THE ARTWORK GETS THE ROOM — the gate every other gate was missing.
 *
 * `mobile-watertight` asserts the canvas is *visible*, never that it is big
 * enough to look at, so the app shipped a stage that had been collapsing for
 * months without a single red test. Measured on production before this spec
 * existed: the collage rendered 219x328 in a 1280x900 window (6.2% of screen),
 * 148x222 on a 390px phone, and at 320x568 the stage band fell to 52px inside
 * which `p-6` left the artwork at THREE BY FOUR PIXELS. Two causes, one symptom:
 *   1. the controls dock was `shrink-0` with no ceiling, so it took its space
 *      out of the picture;
 *   2. the art frame was content-sized against a canvas that sizes itself from
 *      the frame, a circular definition that resolves at Stage.resize's 240px
 *      floor — so the artwork was ~240-300 CSS px wide on ANY screen, and
 *      `maxHeight: 100%` could only ever shrink it further.
 *
 * So this file asserts SIZE, not visibility, and it asserts the clip survives
 * the full-bleed toggle — hiding the header/dock with `display:none` keeps the
 * Stage mounted, and an unmount would cost the clip its decoder and playhead.
 *
 * Run against the live dev server:
 *   npx playwright test --config playwright.stage-room.config.ts
 * or a deployed release:
 *   COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ \
 *     npx playwright test --config playwright.stage-room.config.ts
 */
import { test, expect, type Page } from '@playwright/test';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
// VP9: the codec every Chromium build decodes, so a red test means the feature
// broke, never that the fixture was unplayable.
const CLIP = join(HERE, '..', 'fixtures', 'motion.webm');

const PHONES = [320, 360, 390, 430];

type Shot = {
  vw: number; vh: number; overflowX: number;
  art: { w: number; h: number; pct: number; fitPct: number } | null;
  dockPct: number | null; scrollers: number | null;
  controls: { name: string; clippedBy: number; overArt: boolean; overBand: boolean }[];
  videos: number; ct: number[]; paused: boolean[];
};

/** Measure the actual composition, never the empty-state template thumbnail. */
const readStage = () => {
  const c = document.querySelector('[data-testid="studio-artwork"] canvas');
  const r = c?.getBoundingClientRect();
  const vids = Array.from(document.querySelectorAll('video'));
  const bandElement=document.querySelector('[data-testid="studio-art-band"]');
  const band=bandElement?.getBoundingClientRect();
  const padding=bandElement?getComputedStyle(bandElement):null;
  const usableWidth=band&&padding?band.width-parseFloat(padding.paddingLeft)-parseFloat(padding.paddingRight):0;
  const usableHeight=band&&padding?band.height-parseFloat(padding.paddingTop)-parseFloat(padding.paddingBottom):0;
  const fittedWidth=r?Math.min(usableWidth,usableHeight*r.width/r.height):0;
  const fittedHeight=r?fittedWidth*r.height/r.width:0;
  const dock = document.querySelector('.studio-inspector');
  const dr = dock?.getBoundingClientRect();
  const vis = !!dock?.getClientRects().length;
  const overlaps=(a:DOMRect,b:DOMRect)=>a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top;
  return {
    vw:innerWidth,vh:innerHeight,
    overflowX:document.documentElement.scrollWidth-document.documentElement.clientWidth,
    art:r?{w:Math.round(r.width),h:Math.round(r.height),pct:+((r.width*r.height/(innerWidth*innerHeight))*100).toFixed(1),fitPct:r.width*r.height/(fittedWidth*fittedHeight)*100}:null,
    dockPct:dr&&vis?+(dr.height/innerHeight*100).toFixed(1):null,
    videos:vids.length,ct:vids.map(v=>+v.currentTime.toFixed(2)),paused:vids.map(v=>v.paused),
    scrollers:vis&&dock?Array.from(dock.querySelectorAll('*')).concat([dock]).filter(e=>{
      const style=getComputedStyle(e);
      return e.getClientRects().length>0&&(style.overflowY==='auto'||style.overflowY==='scroll')&&e.scrollHeight>e.clientHeight+1;
    }).length:null,
    controls:Array.from(document.querySelectorAll('.ui-topbar,.studio-playback,.studio-preview-tools,.studio-taskbar,.studio-inspector'))
      .filter(e=>e.getClientRects().length>0).map(e=>{const box=e.getBoundingClientRect();return {
        name:e.className,clippedBy:Math.max(0,Math.round(-box.left),Math.round(-box.top),Math.round(box.right-innerWidth),Math.round(box.bottom-innerHeight)),
        overArt:r?overlaps(box,r):false,overBand:band?overlaps(box,band):false,
      };}),
  };
};

async function loadClip(page: Page) {
  await page.goto(APP_URL);
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles([CLIP]);
  await page.getByTestId('studio-artwork').locator('canvas').waitFor({ timeout: 120_000 });
  // The band is measured by a ResizeObserver, so let the first fit land.
  await page.waitForTimeout(1200);
}

const snap = (page: Page) => page.evaluate(readStage) as Promise<Shot>;

test.describe('the artwork gets the room', () => {
  test.setTimeout(180_000);
  for (const width of PHONES) {
    test(`R1: the collage is big enough to see at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: width < 360 ? 568 : 844 });
      await loadClip(page);
      const s = await snap(page);
      expect(s.art, 'no canvas on screen at all').not.toBeNull();
      // C3712 no longer needs a near-zero exception for the smallest phone.
      const floor = { w: 200, h: 300 };
      expect(s.art!.w, `artwork only ${s.art!.w}px wide at ${width}px`).toBeGreaterThanOrEqual(floor.w);
      expect(s.art!.h, `artwork only ${s.art!.h}px tall at ${width}px`).toBeGreaterThanOrEqual(floor.h);
      expect(s.overflowX, 'horizontal overflow').toBeLessThanOrEqual(0);
      // Playback, navigation and editors occupy their own layout regions.
      expect(s.controls.length).toBeGreaterThan(1);
      for(const control of s.controls){
        expect(control.clippedBy, `${control.name} leaves the viewport`).toBe(0);
        expect(control.overArt, `${control.name} covers the artwork`).toBe(false);
        expect(control.overBand, `${control.name} enters the measured artwork band`).toBe(false);
      }
    });
  }

  test('R1b: full bleed is the answer on every phone, including the cramped one', async ({ page }) => {
    for (const width of PHONES) {
      await page.setViewportSize({ width, height: width < 360 ? 568 : 844 });
      await loadClip(page);
      await page.getByRole('button', { name: 'Expand preview' }).click();
      await page.waitForTimeout(700);
      const s = await snap(page);
      expect(s.art!.fitPct, `focus uses only ${s.art!.fitPct}% of the largest uncropped fit at ${width}px`)
        .toBeGreaterThanOrEqual(99);
      expect(s.overflowX, `full bleed overflows sideways at ${width}px`).toBeLessThanOrEqual(0);
      await page.keyboard.press('Escape');
    }
  });

  test('R11: each editing panel has one bounded scroller and its close action stays available', async ({ page }) => {
    for (const [width, height] of [[320,568],[390,844],[1280,900]] as const) {
      await page.setViewportSize({width,height});await loadClip(page);
      await page.getByRole('button',{name:'Layout',exact:true}).click();
      const s=await snap(page);
      expect(s.dockPct,'the requested inspector is missing').not.toBeNull();
      expect(s.scrollers,`nested inspector scrollers at ${width}px`).toBeLessThanOrEqual(1);
      const geometry=await page.locator('.studio-inspector').evaluate(e=>{
        const box=e.getBoundingClientRect(),dock=e.querySelector('.ui-dock')!,scroll=dock.getBoundingClientRect();
        const close=e.querySelector('button[aria-label="Close editing panel"]')!,button=close.getBoundingClientRect();
        const hit=document.elementFromPoint(button.x+button.width/2,button.y+button.height/2);
        return {top:box.top,bottom:box.bottom,height:box.height,scrollTop:scroll.top,scrollBottom:scroll.bottom,
          closeHit:hit===close||close.contains(hit),closeHeight:button.height};
      });
      expect(geometry.top).toBeGreaterThanOrEqual(0);expect(geometry.bottom).toBeLessThanOrEqual(height+1);
      if(width<1000)expect(geometry.height).toBeLessThanOrEqual(height*.43);
      expect(geometry.scrollTop).toBeGreaterThanOrEqual(geometry.top);
      expect(geometry.scrollBottom).toBeLessThanOrEqual(geometry.bottom+1);
      expect(geometry.closeHit).toBe(true);expect(geometry.closeHeight).toBeGreaterThanOrEqual(43.5);
      await page.getByRole('button',{name:'Close editing panel',exact:true}).click();
      await expect(page.getByRole('button',{name:'Layout',exact:true})).toBeFocused();
    }
  });

  test('R2: the artwork grows with the window instead of pinning at ~240px', async ({ page }) => {
    await page.setViewportSize({ width: 1900, height: 1300 });
    await loadClip(page);
    const s = await snap(page);
    // Before: 300x450 in a 1900x776 band, because the frame sized to the canvas
    // and the canvas sized to the frame. The band is >700px tall here, so a
    // frame that fits it is >600px tall; 450 is the number that must not return.
    expect(s.art!.h, `artwork only ${s.art!.h}px tall in a 1300px window`).toBeGreaterThan(600);
  });

  test('R3: full bleed hands the artwork most of the screen, Esc hands it back', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await loadClip(page);
    const before = await snap(page);

    await page.getByRole('button', { name: 'Expand preview' }).click();
    await page.waitForTimeout(700);
    const max = await snap(page);

    expect(max.art!.fitPct, `focus uses only ${max.art!.fitPct}% of the available uncropped fit`)
      .toBeGreaterThanOrEqual(99);
    expect(max.art!.h).toBeGreaterThan(before.art!.h);
    expect(max.dockPct, 'the dock is still taking space while maximized').toBeNull();
    expect(max.overflowX, 'full bleed overflows sideways').toBeLessThanOrEqual(0);

    await page.keyboard.press('Escape');
    await page.waitForTimeout(700);
    const back = await snap(page);
    expect(Math.abs(back.art!.pct - before.art!.pct), 'Escape did not restore the layout')
      .toBeLessThan(1);
  });

  test('R4: the clip keeps its decoder across the toggle', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await loadClip(page);
    await page.waitForTimeout(800);
    const before = await snap(page);
    expect(before.videos, 'expected exactly one <video> for one clip').toBe(1);
    expect(before.paused[0], 'the clip was not playing to begin with').toBe(false);

    /**
     * IDENTITY, not currentTime. The clip LOOPS, so a playhead that reads lower
     * after the toggle proves nothing — it may simply have wrapped, which is
     * how the first draft of this test failed on a working build. What actually
     * has to hold is that the Stage was never unmounted: stamp the live
     * elements, and if React tore the subtree down the stamps come back gone
     * because the replacements are different objects.
     */
    const stamp = () => page.evaluate(() => {
      const v = document.querySelector('video') as (HTMLVideoElement & { __room?: number }) | null;
      const c = document.querySelector('[data-testid="studio-artwork"] canvas') as (HTMLCanvasElement & { __room?: number }) | null;
      if (v) v.__room = 1234;
      if (c) c.__room = 5678;
      return { v: !!v, c: !!c };
    });
    const stamped = () => page.evaluate(() => {
      const v = document.querySelector('video') as (HTMLVideoElement & { __room?: number }) | null;
      const c = document.querySelector('[data-testid="studio-artwork"] canvas') as (HTMLCanvasElement & { __room?: number }) | null;
      return { video: v?.__room === 1234, canvas: c?.__room === 5678 };
    });
    expect(await stamp()).toEqual({ v: true, c: true });

    await page.getByRole('button', { name: 'Expand preview' }).click();
    await page.waitForTimeout(900);
    const max = await snap(page);
    expect(max.videos, 'maximizing built a second decoder').toBe(1);
    expect(max.paused[0], 'maximizing stopped the clip').toBe(false);
    expect(await stamped(), 'maximizing REMOUNTED the stage').toEqual({ video: true, canvas: true });

    await page.getByRole('button', { name: 'Back to editing' }).click();
    await page.waitForTimeout(900);
    const back = await snap(page);
    expect(back.videos, 'restoring built a second decoder').toBe(1);
    expect(back.paused[0], 'restoring stopped the clip').toBe(false);
    expect(await stamped(), 'restoring REMOUNTED the stage').toEqual({ video: true, canvas: true });

    // And it is genuinely still running, not merely un-paused.
    const t1 = (await snap(page)).ct[0];
    await page.waitForTimeout(700);
    const t2 = (await snap(page)).ct[0];
    expect(t1 === t2, `playhead frozen at ${t1}s after the toggle`).toBe(false);
  });

  test('R6: landscape keeps playback outside the artwork and project actions reachable', async ({ page }) => {
    await page.setViewportSize({width:844,height:390});await loadClip(page);
    const s=await snap(page);
    for(const control of s.controls){expect(control.clippedBy,control.name).toBe(0);expect(control.overBand,control.name).toBe(false);}
    await expect(page.getByRole('button',{name:'Expand preview',exact:true})).toBeVisible();
    await page.getByRole('button',{name:'Add',exact:true}).click();
    await expect(page.getByRole('button',{name:'Add more images or video',exact:true})).toBeVisible();
    await page.getByText('Project actions',{exact:true}).click();
    const clear=page.getByRole('button',{name:'Clear all',exact:true});
    await clear.scrollIntoViewIfNeeded();
    const hit=await clear.evaluate(e=>{const b=e.getBoundingClientRect(),h=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return {hit:h===e||e.contains(h),bottom:b.bottom,height:b.height};});
    expect(hit.hit).toBe(true);expect(hit.bottom).toBeLessThanOrEqual(390);expect(hit.height).toBeGreaterThanOrEqual(43.5);
  });

  test('R7: F toggles full bleed, and typing an f never does', async ({ page }) => {
    // The shortcut listens on `window`, so the ONLY thing standing between it
    // and every text field in the app is its target guard. A title containing
    // the letter f is the cheapest way to prove that guard is really there.
    await page.setViewportSize({ width: 1280, height: 900 });
    await loadClip(page);
    const isMax = () => page.evaluate(() =>
      document.querySelector('.studio-workspace')?.getAttribute('data-focus') === 'true');

    expect(await isMax()).toBe(false);
    await page.keyboard.press('f');
    await page.waitForTimeout(500);
    expect(await isMax(), 'F did not enter full bleed').toBe(true);
    await page.keyboard.press('f');
    await page.waitForTimeout(500);
    expect(await isMax(), 'F did not leave full bleed').toBe(false);

    await page.getByRole('button',{name:'Text',exact:true}).click();
    await page.getByRole('button',{name:'Title',exact:true}).click();
    const title = page.getByPlaceholder('Say what it is');
    await title.click();
    await title.fill('');
    await title.type('off the floor', { delay: 30 });
    await page.waitForTimeout(400);
    expect(await isMax(), 'typing a title with an f in it maximized the app').toBe(false);
    await expect(title).toHaveValue('off the floor');

    // Escape, likewise, must not fire while a field has focus and must not
    // fight the dialogs that already own it.
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
    expect(await isMax()).toBe(false);
  });

  test('R8: opening Feedback once does not kill the shortcut forever', async ({ page }) => {
    /**
     * THE GATE HAS TO SEE THE THING IT IS GRADING. In local dev the shared
     * wishing well 404s by design, so every other test in this file runs in an
     * app that HAS no feedback modal — which is exactly how the first version of
     * the shortcut guard shipped green while being broken in production. So load
     * the real shared/feedback.js into the page and drive it.
     *
     * The well closes with `classList.remove("on")` against `.fb-wrap{display:
     * none}`: its sheet is built once and never leaves the document. A guard
     * that asks whether [role="dialog"] EXISTS is therefore permanently true
     * after the first Feedback click, and F/Escape die for the session.
     */
    await page.setViewportSize({ width: 1280, height: 900 });
    await loadClip(page);
    const src = readFileSync(process.env.COLLAGE_FEEDBACK_SCRIPT || join(HERE, '..', '..', '..', '..', 'shared', 'feedback.js'), 'utf8');
    await page.addScriptTag({ content: src });
    await page.waitForTimeout(400);
    expect(await page.evaluate(() => !!(window as unknown as { Feedback?: unknown }).Feedback),
      'the shared wishing well did not load').toBe(true);

    const isMax = () => page.evaluate(() =>
      document.querySelector('.studio-workspace')?.getAttribute('data-focus') === 'true');

    // While it is genuinely open, the shortcut must stay out of the way.
    await page.getByRole('button',{name:'Add',exact:true}).click();
    await page.getByRole('button',{name:'Feedback',exact:true}).click();
    await page.waitForTimeout(400);
    await page.keyboard.press('f');
    await page.waitForTimeout(400);
    expect(await isMax(), 'F fired while the wishing well was open').toBe(false);

    // Closed. The sheet is still in the DOM — that must not matter.
    await page.evaluate(() => (window as unknown as { Feedback: { close: () => void } }).Feedback.close());
    await page.waitForTimeout(400);
    const stillThere = await page.evaluate(() =>
      Array.from(document.querySelectorAll('[role="dialog"]'))
        .map((d) => ({ inDom: true, rendered: d.getClientRects().length > 0 })));
    expect(stillThere.some((d) => d.inDom && !d.rendered),
      'the well no longer leaves a closed dialog behind — this test is now moot, delete it').toBe(true);

    await page.keyboard.press('f');
    await page.waitForTimeout(500);
    expect(await isMax(), 'a closed Feedback sheet permanently disabled the shortcut').toBe(true);
    await page.keyboard.press('Escape');
    await page.waitForTimeout(400);
    expect(await isMax()).toBe(false);
  });

  test('R9: F does nothing with an empty pool, and every full-screen sheet says it is one', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(APP_URL);
    await expect(page.getByRole('heading',{name:'Start a new piece',exact:true})).toBeVisible({ timeout: 60_000 });
    // There is nothing to maximize. F used to hide the header and the dock and
    // leave the drop target alone on a black page, and the strand-guard could
    // not fire because pressing F does not change images.length.
    await page.keyboard.press('f');
    await page.waitForTimeout(500);
    await expect(page.getByRole('heading',{name:'Start a new piece',exact:true})).toBeVisible();
    await expect(page.getByRole('button',{name:'Art Room',exact:true})).toBeVisible();
    await expect(page.getByRole('button',{name:'Open',exact:true})).toBeVisible();
    await expect(page.getByRole('button',{name:'Back to editing',exact:true})).toHaveCount(0);

    // Every sheet that covers the screen must be findable as a dialog, or the
    // shortcut guard acts BEHIND it. The recorded-take preview was the one that
    // was not, and it is reachable while maximized because the Header keeps its
    // shortcuts under display:none.
    await loadClip(page);
    const undeclared = await page.evaluate(() =>
      Array.from(document.querySelectorAll('div'))
        .filter((d) => {
          const cs = getComputedStyle(d);
          if (cs.position !== 'fixed' || d.getClientRects().length === 0) return false;
          const r = d.getBoundingClientRect();
          const coversScreen = r.width >= window.innerWidth - 2 && r.height >= window.innerHeight - 2;
          return coversScreen && +cs.zIndex >= 100 && d.getAttribute('role') !== 'dialog';
        })
        .map((d) => d.className.slice(0, 70)));
    expect(undeclared, `full-screen sheet(s) not declared role="dialog": ${JSON.stringify(undeclared)}`)
      .toEqual([]);
  });

  test('R10: the toggle hands focus to the control that replaced the one it removed', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await loadClip(page);
    const focused = () => page.evaluate(() =>
      (document.activeElement?.getAttribute('aria-label') || document.activeElement?.tagName || '?'));

    await page.getByRole('button', { name: 'Expand preview' }).click();
    await page.waitForTimeout(600);
    expect(await focused(), 'maximizing dropped focus to the body').toBe('Back to editing');

    await page.getByRole('button', { name: 'Back to editing' }).click();
    await page.waitForTimeout(600);
    expect(await focused(), 'restoring dropped focus to the body').toBe('Expand preview');
  });

  test('R12: the frame never overshoots its band while entering or leaving full bleed', async ({ page }) => {
    /**
     * A ResizeObserver reports AFTER layout, so on a discontinuous band change
     * the frame keeps its old explicit pixels for one paint — and the band is
     * `overflow-hidden`, so that paint is CLIPPED, not letterboxed. An
     * adversarial verifier caught it in real composited pixels (CDP screencast,
     * frames stamped and decoded): leaving full bleed at 1280x900 painted the
     * collage at 589x884 inside a 1248x459 band with the header and dock already
     * restored, top and bottom sliced off, on 8 of 8 exits.
     *
     * TWO mechanisms now prevent it and EITHER ONE suffices, so this gate is
     * red only when BOTH are gone — which is exactly what was checked, and it
     * reports the same numbers the verifier did (589x884 in a 1248x400 band).
     * Do not read a green here as cover for deleting one of them: (a) the
     * `maxWidth/maxHeight: 100%` clamp, which is synchronous CSS and also covers
     * the size changes we do NOT drive (rotation, URL-bar collapse); (b) the
     * layout effect on `maximized`, which measures our own toggle before paint.
     * This asserts the outcome, not either implementation.
     */
    await page.setViewportSize({ width: 1280, height: 900 });
    await loadClip(page);
    await page.evaluate(() => {
      const w = window as unknown as { __over: string[]; __n: number };
      w.__over = []; w.__n = 0;
      const tick = () => {
        w.__n++;
        const fr = document.querySelector('[data-testid="studio-artwork"]');
        const band = fr?.parentElement;
        if (fr && band) {
          const a = fr.getBoundingClientRect();
          const cs = getComputedStyle(band);
          const bw = band.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
          const bh = band.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
          if (a.width > bw + 1 || a.height > bh + 1) {
            w.__over.push(`${Math.round(a.width)}x${Math.round(a.height)} in ${Math.round(bw)}x${Math.round(bh)}`);
          }
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });

    for (let i = 0; i < 5; i++) {
      await page.getByRole('button', { name: 'Expand preview' }).click();
      await page.waitForTimeout(400);
      await page.getByRole('button', { name: 'Back to editing' }).click();
      await page.waitForTimeout(400);
    }

    const r = await page.evaluate(() => {
      const w = window as unknown as { __over: string[]; __n: number };
      return { frames: w.__n, over: w.__over };
    });
    expect(r.frames, 'no animation frames were sampled').toBeGreaterThan(100);
    expect(r.over, `the frame overshot its band on ${r.over.length} sampled frames: ${JSON.stringify(r.over.slice(0, 3))}`)
      .toEqual([]);
  });

  test('R5: full bleed is watertight and thumb-sized on a phone', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await loadClip(page);
    await page.getByRole('button', { name: 'Expand preview' }).click();
    await page.waitForTimeout(700);

    const s = await snap(page);
    expect(s.overflowX, 'full bleed overflows sideways on a phone').toBeLessThanOrEqual(0);
    expect(s.art!.pct, `full bleed only reached ${s.art!.pct}% of a phone screen`)
      .toBeGreaterThan(45);

    const small = await page.evaluate(() =>
      Array.from(document.querySelectorAll('button'))
        .filter((el) => {
          const r = el.getBoundingClientRect();
          const cs = getComputedStyle(el);
          if (cs.display === 'none' || cs.visibility === 'hidden' || r.width === 0) return false;
          return r.height < 43.5 || r.width < 43.5;
        })
        .map((el) => (el.getAttribute('aria-label') || el.textContent || '?').trim().slice(0, 30)),
    );
    expect(small, `full-bleed controls under 44px: ${JSON.stringify(small)}`).toEqual([]);

    // Every action you are maximized in order to reach has to be there.
    for (const name of ['Roll the dice', 'Undo the last composition change', 'Back to editing']) {
      await expect(page.getByRole('button', { name })).toBeVisible();
    }
    // The more specific composition operations remain reachable in Layout.
    await page.getByRole('button',{name:'Back to editing',exact:true}).click();
    await page.getByRole('button',{name:'Layout',exact:true}).click();
    for(const name of ['Shuffle images','Remix shapes']){
      const control=page.getByRole('button',{name,exact:true});
      await control.scrollIntoViewIfNeeded();
      const target=await control.evaluate(e=>{const b=e.getBoundingClientRect(),hit=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return {height:b.height,width:b.width,hit:hit===e||e.contains(hit)};});
      expect(target.height).toBeGreaterThanOrEqual(43.5);expect(target.width).toBeGreaterThanOrEqual(43.5);expect(target.hit).toBe(true);
    }
  });
});
