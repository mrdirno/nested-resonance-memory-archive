/**
 * LOCAL-ONLY compositor seam. Imports the real Vite-served modules and reads
 * actual canvas pixels, without adding a test hook to the shipped application.
 * The production caption UI and recorded-file proof is a separate suite.
 *
 * Run against an already running :5199 dev server:
 *   npx playwright test --config playwright.caption-stage.config.ts
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */
import { test, expect } from '@playwright/test';

const APP_URL = process.env.COLLAGE_BASE_URL || 'http://localhost:5199/';
const local = ['localhost', '127.0.0.1', '[::1]'].includes(new URL(APP_URL).hostname);
test.skip(!local, 'Local compositor seam imports source modules; use the caption UI suite for production.');

test('caption pixels obey output time, parked edits and a seek beyond page uptime', async ({ page }) => {
  await page.goto(APP_URL);
  const evidence = await page.evaluate(async () => {
    const { createStage } = await import('/src/lib/stage.ts');
    const { planCaptions } = await import('/src/lib/captions.ts');
    const { planTitle, measureWith } = await import('/src/lib/title.ts');
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:fixed;inset:0;width:600px;height:600px;z-index:99999';
    document.body.appendChild(canvas);
    // A non-default logical width proves the plans scale before the draw loop.
    const stage = createStage(canvas, {
      logicalWidth: 600, maxBackingWidth: 600, audio: false,
      pauseWhenHidden: false, pauseWhenOffscreen: false,
    });
    try {
      const measure = measureWith(canvas.getContext('2d')!);
      const track = {
        place: 'bc', size: 'md',
        cues: [
          { id: 'first', start: 1, end: 2, text: 'FIRST CUE' },
          { id: 'second', start: 3, end: 4, text: 'SECOND CUE' },
        ],
      };
      stage.setScene({
        layoutItems: [], orderedAssets: [], clips: [], mode: 'minimal', aspect: 1,
        bgColor: '#153040', pace: 'rush',
        titlePlan: planTitle({ text: 'PERSISTENT TITLE', place: 'tc', size: 'md' }, 1, measure),
        captionPlans: planCaptions(track, 1, measure),
      });
      stage.setTake(10);
      // Let ResizeObserver establish the aspect before comparing glyph regions.
      await new Promise((resolve) => setTimeout(resolve, 100));
      const sample = () => {
        const pixels = canvas.getContext('2d')!.getImageData(0, 0, canvas.width, canvas.height).data;
        let top = 0, bottom = 0, hash = 2166136261;
        for (let i = 0; i < pixels.length; i += 4) {
          hash = Math.imul(hash ^ pixels[i], 16777619);
          if (pixels[i] > 230 && pixels[i + 1] > 230 && pixels[i + 2] > 230) {
            if (i / (canvas.width * 4) < canvas.height / 2) top++;
            else bottom++;
          }
        }
        return { top, bottom, hash: hash >>> 0, time: stage.takePosition };
      };
      await stage.renderAtTime(0);
      const opening = sample();
      await stage.renderAtTime(1.25);
      const first = sample();
      await stage.renderAtTime(2);
      const gap = sample();
      await stage.scrubTo(3.5);
      const beforeEdit = sample();
      stage.start();
      stage.setCaptionPlans(planCaptions({
        ...track, cues: [track.cues[0], { ...track.cues[1], text: 'EDITED WHILE PAUSED' }],
      }, 1, measure));
      await new Promise((resolve) => setTimeout(resolve, 120));
      const afterEdit = sample();

      // Cross a boundary on a still canvas with no video, move, turn or music.
      stage.setCaptionPlans(planCaptions({
        ...track, cues: [{ id: 'live', start: 1, end: 9, text: 'LIVE CAPTION' }],
      }, 1, measure));
      await stage.scrubTo(0.8);
      stage.resumeFromGesture({ sound: false });
      const waitForClock = async (at: number) => {
        const deadline = performance.now() + 5000;
        while (stage.takePosition < at && performance.now() < deadline) {
          await new Promise((resolve) => setTimeout(resolve, 30));
        }
        // Let the compositor paint the derived position the getter just returned.
        await new Promise((resolve) => requestAnimationFrame(resolve));
        return sample();
      };
      const playing = await waitForClock(1.1);

      // resumeOriginMs legitimately becomes negative. A '< 0 = uninitialized'
      // sentinel previously restarted the clock on every following frame.
      const future = Math.ceil(performance.now() / 1000) + 40;
      stage.setTake(future + 10);
      await stage.scrubTo(future);
      stage.resumeFromGesture({ sound: false });
      const futureSeek = await waitForClock(future + 0.12);
      return { opening, first, gap, beforeEdit, afterEdit, playing, future, futureSeek };
    } finally {
      stage.destroy();
      canvas.remove();
    }
  });

  expect(evidence.opening.top).toBeGreaterThan(0);
  expect(evidence.opening.bottom).toBe(0);
  expect(evidence.first.top).toBe(0);
  expect(evidence.first.bottom).toBeGreaterThan(0);
  expect(evidence.gap.top).toBe(evidence.opening.top);
  expect(evidence.gap.bottom).toBe(0);
  expect(evidence.beforeEdit.time).toBe(3.5);
  expect(evidence.afterEdit.time).toBe(3.5);
  expect(evidence.afterEdit.hash).not.toBe(evidence.beforeEdit.hash);
  expect(evidence.playing.time).toBeGreaterThanOrEqual(1.1);
  expect(evidence.playing.time).toBeLessThan(9);
  expect(evidence.playing.top).toBe(0);
  expect(evidence.playing.bottom).toBeGreaterThan(0);
  expect(evidence.futureSeek.time).toBeGreaterThanOrEqual(evidence.future + 0.1);
  expect(evidence.futureSeek.time).toBeLessThan(evidence.future + 5);
});
