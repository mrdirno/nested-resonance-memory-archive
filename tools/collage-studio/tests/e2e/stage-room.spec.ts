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
  art: { w: number; h: number; pct: number } | null;
  dockPct: number | null;
  videos: number; ct: number[]; paused: boolean[];
};

/** Everything this file judges, read off the REAL page in one pass. */
const readStage = () => {
  const c = document.querySelector('canvas');
  const r = c?.getBoundingClientRect();
  const vids = Array.from(document.querySelectorAll('video'));
  const shell = document.querySelector('div.fixed.inset-0');
  const dock = shell
    ? Array.from(shell.children).find(
        (k) => k.className.includes('border-t') && k.className.includes('shrink-0'),
      )
    : null;
  const dr = dock?.getBoundingClientRect();
  const vis = dock ? getComputedStyle(dock as Element).display !== 'none' : false;
  return {
    vw: window.innerWidth,
    vh: window.innerHeight,
    overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    art: r
      ? {
          w: Math.round(r.width),
          h: Math.round(r.height),
          pct: +(((r.width * r.height) / (window.innerWidth * window.innerHeight)) * 100).toFixed(1),
        }
      : null,
    dockPct: dr && vis ? +((dr.height / window.innerHeight) * 100).toFixed(1) : null,
    videos: vids.length,
    ct: vids.map((v) => +v.currentTime.toFixed(2)),
    paused: vids.map((v) => v.paused),
    // How many nested scrollers the dock contains, and whether its sticky
    // primary action bar (fragment count / Shuffle / Remix) is on screen.
    scrollers: dock
      ? Array.from(dock.querySelectorAll('*')).concat([dock]).filter((e) => {
          const s = getComputedStyle(e);
          return (s.overflowY === 'auto' || s.overflowY === 'scroll') && e.scrollHeight > e.clientHeight + 1;
        }).length
      : null,
    stickyInView: (() => {
      const ud = dock?.querySelector('.ui-dock');
      if (!ud) return null;
      const st = Array.from(ud.querySelectorAll('*')).filter((e) => getComputedStyle(e).position === 'sticky');
      if (!st.length) return null;
      const r2 = st[st.length - 1].getBoundingClientRect();
      return r2.top >= 0 && r2.bottom <= window.innerHeight + 0.5;
    })(),
    // The stage rail must be wholly on the band and never sit on the picture.
    rail: (() => {
      const btn = document.querySelector('button[aria-label="Maximize the shot"]');
      const rail = btn?.parentElement;
      const band = rail?.parentElement;
      if (!rail || !band || !r) return null;
      const rr = rail.getBoundingClientRect();
      const br = band.getBoundingClientRect();
      return {
        clippedBy: Math.max(0, Math.round(rr.bottom - br.bottom), Math.round(rr.right - br.right)),
        overArt: rr.left < r.right && rr.right > r.left && rr.top < r.bottom && rr.bottom > r.top,
      };
    })(),
  };
};

async function loadClip(page: Page) {
  await page.goto(APP_URL);
  await page.locator('input[type="file"]').first().setInputFiles([CLIP]);
  await page.locator('canvas').first().waitFor({ timeout: 120_000 });
  // The band is measured by a ResizeObserver, so let the first fit land.
  await page.waitForTimeout(1200);
}

const snap = (page: Page) => page.evaluate(readStage) as Promise<Shot>;

test.describe('the artwork gets the room', () => {
  for (const width of PHONES) {
    test(`R1: the collage is big enough to see at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: width < 360 ? 568 : 844 });
      await loadClip(page);
      const s = await snap(page);
      expect(s.art, 'no canvas on screen at all').not.toBeNull();
      /**
       * HONEST FLOORS. 320x568 with a clip loaded is CHROME-BOUND, not layout-
       * bound: 61px of header plus a transport row that wraps to 157px plus a
       * 47px tab bar is 265px of things the app needs before any panel opens.
       * The normal view there goes 3x4 -> 16x24 and no amount of capping fixes
       * it — FULL BLEED does (312x467, 80% of the screen, asserted in R1b), and
       * pretending otherwise with a floor this size cannot meet is how a gate
       * starts lying. Everywhere else the floor is a real one.
       */
      const floor = width < 360 ? { w: 14, h: 20 } : { w: 150, h: 220 };
      expect(s.art!.w, `artwork only ${s.art!.w}px wide at ${width}px`).toBeGreaterThanOrEqual(floor.w);
      expect(s.art!.h, `artwork only ${s.art!.h}px tall at ${width}px`).toBeGreaterThanOrEqual(floor.h);
      expect(s.overflowX, 'horizontal overflow').toBeLessThanOrEqual(0);
      // The rail must be wholly on the band and never on the picture.
      expect(s.rail!.clippedBy, `the stage rail hangs ${s.rail!.clippedBy}px off the band`).toBe(0);
      expect(s.rail!.overArt, 'the stage rail is sitting on the artwork').toBe(false);
    });
  }

  test('R1b: full bleed is the answer on every phone, including the cramped one', async ({ page }) => {
    for (const width of PHONES) {
      await page.setViewportSize({ width, height: width < 360 ? 568 : 844 });
      await loadClip(page);
      await page.getByRole('button', { name: 'Maximize the shot' }).click();
      await page.waitForTimeout(700);
      const s = await snap(page);
      expect(s.art!.pct, `full bleed only reached ${s.art!.pct}% of the screen at ${width}px`)
        .toBeGreaterThan(60);
      expect(s.overflowX, `full bleed overflows sideways at ${width}px`).toBeLessThanOrEqual(0);
      await page.keyboard.press('Escape');
    }
  });

  test('R11: the dock keeps ONE scroller and its primary actions stay on screen', async ({ page }) => {
    /**
     * The first version of this change wrapped the dock in a second capped
     * scroller. `.ui-dock` is ALREADY a capped scroller whose primary action bar
     * — fragment count, Shuffle, Remix — is `position: sticky` against its
     * bottom, so nesting pinned that bar to the bottom of an inner box pushed
     * below the outer scrollport and the most-used controls in the app went off
     * screen (measured 778..832 in an 844px viewport, to 869..923). An
     * adversarial audit caught it; the cap moved onto `--dock-max` instead.
     */
    for (const [width, height] of [[320, 568], [390, 844], [1280, 900]] as const) {
      await page.setViewportSize({ width, height });
      await loadClip(page);
      const s = await snap(page);
      expect(s.scrollers, `the dock has ${s.scrollers} nested scrollers at ${width}px`).toBeLessThanOrEqual(1);
      expect(s.stickyInView, `the sticky primary action bar is off screen at ${width}px`).toBe(true);
      // And the panel itself is genuinely capped, which is where the height
      // now comes from.
      const capped = await page.evaluate(() => {
        const ud = document.querySelector('.ui-dock');
        return ud ? parseFloat(getComputedStyle(ud).maxHeight) : null;
      });
      expect(capped, `the control panel is uncapped at ${width}px`).not.toBeNull();
      expect(capped!, `the control panel cap is ${capped}px at ${width}px`).toBeLessThanOrEqual(300);
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

    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    await page.waitForTimeout(700);
    const max = await snap(page);

    expect(max.art!.pct, `full bleed only reached ${max.art!.pct}% of the screen`)
      .toBeGreaterThan(35);
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
      const c = document.querySelector('canvas') as (HTMLCanvasElement & { __room?: number }) | null;
      if (v) v.__room = 1234;
      if (c) c.__room = 5678;
      return { v: !!v, c: !!c };
    });
    const stamped = () => page.evaluate(() => {
      const v = document.querySelector('video') as (HTMLVideoElement & { __room?: number }) | null;
      const c = document.querySelector('canvas') as (HTMLCanvasElement & { __room?: number }) | null;
      return { video: v?.__room === 1234, canvas: c?.__room === 5678 };
    });
    expect(await stamp()).toEqual({ v: true, c: true });

    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    await page.waitForTimeout(900);
    const max = await snap(page);
    expect(max.videos, 'maximizing built a second decoder').toBe(1);
    expect(max.paused[0], 'maximizing stopped the clip').toBe(false);
    expect(await stamped(), 'maximizing REMOUNTED the stage').toEqual({ video: true, canvas: true });

    await page.getByRole('button', { name: 'Exit full bleed' }).click();
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

  test('R6: the stage rail stays on screen on a phone held landscape', async ({ page }) => {
    // 844x390 leaves a ~118px band. A 200px column of buttons does not fit in
    // it, and the band clips, so `Clear all` was off the bottom with nothing to
    // scroll to reach it.
    await page.setViewportSize({ width: 844, height: 390 });
    await loadClip(page);
    const clipped = await page.evaluate(() => {
      const btn = document.querySelector('button[aria-label="Maximize the shot"]');
      const rail = btn?.parentElement;
      const band = rail?.parentElement;
      if (!rail || !band) return null;
      const rr = rail.getBoundingClientRect();
      const br = band.getBoundingClientRect();
      return { below: Math.round(rr.bottom - br.bottom), right: Math.round(rr.right - br.right) };
    });
    expect(clipped, 'no stage rail found').not.toBeNull();
    expect(clipped!.below, `the rail hangs ${clipped!.below}px past the bottom of the stage`)
      .toBeLessThanOrEqual(0);
    expect(clipped!.right, `the rail hangs ${clipped!.right}px past the right of the stage`)
      .toBeLessThanOrEqual(0);
    // Every button in it is still reachable, including the last one.
    for (const name of ['Maximize the shot', 'Add more images or video', 'Clear all']) {
      await expect(page.getByRole('button', { name })).toBeVisible();
    }
  });

  test('R7: F toggles full bleed, and typing an f never does', async ({ page }) => {
    // The shortcut listens on `window`, so the ONLY thing standing between it
    // and every text field in the app is its target guard. A title containing
    // the letter f is the cheapest way to prove that guard is really there.
    await page.setViewportSize({ width: 1280, height: 900 });
    await loadClip(page);
    const isMax = () => page.evaluate(() =>
      !document.querySelector('button[aria-label="Maximize the shot"]')
      && !!document.querySelector('button[aria-label="Exit full bleed"]'));

    expect(await isMax()).toBe(false);
    await page.keyboard.press('f');
    await page.waitForTimeout(500);
    expect(await isMax(), 'F did not enter full bleed').toBe(true);
    await page.keyboard.press('f');
    await page.waitForTimeout(500);
    expect(await isMax(), 'F did not leave full bleed').toBe(false);

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
    const src = readFileSync(join(HERE, '..', '..', '..', '..', 'shared', 'feedback.js'), 'utf8');
    await page.addScriptTag({ content: src });
    await page.waitForTimeout(400);
    expect(await page.evaluate(() => !!(window as unknown as { Feedback?: unknown }).Feedback),
      'the shared wishing well did not load').toBe(true);

    const isMax = () => page.evaluate(() =>
      !document.querySelector('button[aria-label="Maximize the shot"]')
      && !!document.querySelector('button[aria-label="Exit full bleed"]'));

    // While it is genuinely open, the shortcut must stay out of the way.
    await page.evaluate(() => (window as unknown as { Feedback: { open: (k: string) => void } }).Feedback.open('bug'));
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
    await expect(page.getByText('LOAD SOURCE')).toBeVisible({ timeout: 60_000 });
    // There is nothing to maximize. F used to hide the header and the dock and
    // leave the drop target alone on a black page, and the strand-guard could
    // not fire because pressing F does not change images.length.
    await page.keyboard.press('f');
    await page.waitForTimeout(500);
    await expect(page.getByText('LOAD SOURCE')).toBeVisible();
    expect((await snap(page)).dockPct, 'F hid the whole UI with nothing loaded').not.toBeNull();

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

    await page.getByRole('button', { name: 'Maximize the shot' }).click();
    await page.waitForTimeout(600);
    expect(await focused(), 'maximizing dropped focus to the body').toBe('Exit full bleed');

    await page.getByRole('button', { name: 'Exit full bleed' }).click();
    await page.waitForTimeout(600);
    expect(await focused(), 'restoring dropped focus to the body').toBe('Maximize the shot');
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
        const fr = document.querySelector('div.relative.shadow-2xl');
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
      await page.getByRole('button', { name: 'Maximize the shot' }).click();
      await page.waitForTimeout(400);
      await page.getByRole('button', { name: 'Exit full bleed' }).click();
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
    await page.getByRole('button', { name: 'Maximize the shot' }).click();
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
    for (const name of ['Roll the dice', 'Shuffle images', 'Remix shapes', 'Exit full bleed']) {
      await expect(page.getByRole('button', { name })).toBeVisible();
    }
  });
});
