import { test, expect } from '@playwright/test';

/**
 * THE POSTER STILL HAS TO BE A REAL MOMENT.
 *
 * `openClip` took the old three-seek "smart" oversample down to ONE seek, which
 * is where 3 s of the 3.5 s wait before a clip reached the collage was going.
 * The oversample was not decoration though — it existed to dodge black leader by
 * keeping the most energetic of three candidates. What replaces it is cheaper
 * and has to be shown to work: sample the trimmed INTERIOR (mid-clip), and give
 * a blank grab one nudge-and-retry.
 *
 * These drive the REAL module off the dev server — not a copy, not a
 * reimplementation — with a fixture that is deliberately black for its first
 * 1.5 s. A poster that comes back black is a regression the collage would show
 * in every static export.
 */

const modUrl = '/src/lib/video.ts';

/** Mean luminance 0..255 of the poster the intake handed back. */
const posterLuma = async (page: import('@playwright/test').Page, fixture: string) =>
  page.evaluate(async ({ modUrl, fixture }) => {
    const mod = await import(/* @vite-ignore */ modUrl);
    const buf = await (await fetch(fixture)).arrayBuffer();
    const name = fixture.split('/').pop() as string;
    const file = new File([buf], name, { type: 'video/mp4' });

    const clip = await mod.openClip(file, { maxDim: 640 });
    if (!clip.poster) return { ok: false, luma: -1, error: clip.error, w: clip.width, h: clip.height, dur: clip.duration, t: -1 };

    const img = new Image();
    img.src = clip.poster.url;
    await img.decode();
    const c = document.createElement('canvas');
    c.width = 32; c.height = 32;
    const ctx = c.getContext('2d')!;
    ctx.drawImage(img, 0, 0, 32, 32);
    const d = ctx.getImageData(0, 0, 32, 32).data;
    let sum = 0;
    for (let i = 0; i < d.length; i += 4) sum += (d[i] * 0.299 + d[i + 1] * 0.587 + d[i + 2] * 0.114);
    const luma = sum / (d.length / 4);
    const out = { ok: true, luma, error: clip.error, w: clip.width, h: clip.height, dur: clip.duration, t: clip.poster.time };
    mod.revokeFrames([clip.poster]);
    return out;
  }, { modUrl, fixture });

test.describe('clip intake', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', e => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', r => r.abort());
    await page.goto(process.env.COLLAGE_BASE_URL || '/');
  });

  test('the poster skips black leader instead of framing it', async ({ page }) => {
    test.setTimeout(120_000);
    const r = await posterLuma(page, '/tests/fixtures/blackleader.mp4');
    console.log('blackleader poster:', JSON.stringify(r));
    expect(r.ok, `no poster came back: ${r.error}`).toBe(true);
    expect(r.w).toBe(640);
    expect(r.h).toBe(480);
    // The clip is pure black for its first 1.5s of 5s. A midpoint sample lands
    // well past that; anything near-black here means the intake framed leader.
    expect(r.luma, 'the poster is black — it framed the leader').toBeGreaterThan(16);
    expect(r.t, 'the poster was taken from the leader').toBeGreaterThan(1.5);
  });

  test('a normal clip yields one poster with the clip shape and duration', async ({ page }) => {
    test.setTimeout(120_000);
    const r = await posterLuma(page, '/tests/fixtures/tone_a.mp4');
    console.log('tone_a poster:', JSON.stringify(r));
    expect(r.ok, `no poster came back: ${r.error}`).toBe(true);
    expect(r.dur).toBeGreaterThan(0);
    expect(r.w).toBeGreaterThan(0);
    expect(r.luma).toBeGreaterThan(4);
    // Interior, not the head: the first frames of a clip are the least useful
    // poster and the most likely to be a fade.
    expect(r.t).toBeGreaterThan(0);
    expect(r.t).toBeLessThan(r.dur);
  });

  test('a file with no visual track is reported, not crashed on', async ({ page }) => {
    test.setTimeout(120_000);
    const r = await page.evaluate(async ({ modUrl }) => {
      const mod = await import(/* @vite-ignore */ modUrl);
      const file = new File([new Uint8Array(0)], 'empty.mp4', { type: 'video/mp4' });
      const clip = await mod.openClip(file);
      return { error: clip.error, poster: !!clip.poster, dur: clip.duration };
    }, { modUrl });
    console.log('empty file:', JSON.stringify(r));
    expect(r.poster).toBe(false);
    expect(r.error).toBeTruthy();
    expect(r.dur).toBe(0);
  });
});
