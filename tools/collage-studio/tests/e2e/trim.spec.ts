// tests/e2e/trim.spec.ts
// -----------------------------------------------------------------------------
// TRIM — THE ARTIFACT PROOF: the clip plays the part you chose, on screen AND
// in the file, in picture AND in sound.
//
// WHY THE FIXTURE LOOKS LIKE THAT
//   `ramp_rgb.mp4` is six seconds in three flat thirds, and each third carries
//   BOTH a colour and a tone:
//
//       0–2s   RED     440 Hz
//       2–4s   GREEN  1200 Hz
//       4–6s   BLUE   3000 Hz
//
//   So one file discriminates every path this capability touches. The colour
//   says where the PICTURE is; the tone says where the SOUND is; and because
//   the thirds are flat, "which third is showing" is a dominant-channel test
//   with a 222-vs-16 margin rather than a similarity score with a threshold to
//   argue about. Trim to the MIDDLE third and every wrong answer is loud: red on
//   screen means the live window wrapped past IN, blue means it ran past OUT,
//   red in the file means the export ignored the trim, and 440 Hz in the file
//   means the audio mixer did.
//
// WHY IT IS NOT ENOUGH TO WATCH THE PREVIEW
//   This project's scar list is explicit that a preview-only suite cannot see an
//   export defect — the crop-focus split passed 4/4 pixel-level preview tests
//   while the downloaded file was cropped the old way. Trim reaches three
//   independent timelines (the live <video>, the offline frame seek, the offline
//   audio mix), so the proof reads all three: canvas pixels for the live path,
//   DECODED FRAMES of the produced MP4 for the export's picture, and DECODED
//   SAMPLES of the same MP4 for its sound.
//
//   npx playwright test --config playwright.trim.config.ts
// -----------------------------------------------------------------------------

import { test, expect, type Page } from '@playwright/test';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP_URL = process.env.COLLAGE_BASE_URL || '/';
const RAMP = join(HERE, '..', 'fixtures', 'ramp_rgb.mp4');
const CLIP_NAME = 'ramp_rgb.mp4';

/**
 * The trim window used throughout: strictly inside the MIDDLE (green) third,
 * with room at both ends so a frame of decoder overshoot cannot reach a
 * neighbour.
 *
 * THE MIDDLE THIRD IS THE WHOLE POINT, and picking an end one would have made
 * this suite green on the easy half — the same trap twist's T4 and ONE LAYOUT's
 * generator choice both fell into. A window inside the LAST third cannot see a
 * broken OUT point: run past 5.6 and the clip is still blue all the way to the
 * end, so the pixels never say anything went wrong. From the middle, overrunning
 * OUT shows BLUE and wrapping past IN (which is what the element's own native
 * loop does — it returns to 0, not to the IN point) shows RED. Every way of
 * getting trim wrong now has a colour.
 */
const IN_SEC = 2.3;
const OUT_SEC = 3.6;

const HZ_RED = 440;
const HZ_GREEN = 1200;
const HZ_BLUE = 3000;
/** Carries no tone and is a harmonic of none of them, so every claim about a
 *  tone is a RATIO against this file's own noise floor. */
const HZ_CONTROL = 5500;

type Channel = 'r' | 'g' | 'b' | '?';

/**
 * Which third of the clip is on screen, read off the LIVE Stage canvas.
 *
 * The app renders exactly one <canvas> in its DOM (the Stage's; every other
 * surface is created off-document), so there is no ambiguity to resolve here.
 * A margin of 1.6x between the winning channel and the runner-up rejects a
 * half-decoded or blended frame instead of scoring it as a colour.
 */
const stageChannel = async (page: Page): Promise<Channel> =>
  page.evaluate(() => {
    const cv = document.querySelector('canvas') as HTMLCanvasElement | null;
    if (!cv || !cv.width || !cv.height) return '?';
    const s = document.createElement('canvas');
    s.width = 8; s.height = 8;
    const ctx = s.getContext('2d');
    if (!ctx) return '?';
    try { ctx.drawImage(cv, 0, 0, 8, 8); } catch { return '?'; }
    const d = ctx.getImageData(0, 0, 8, 8).data;
    let r = 0, g = 0, b = 0;
    for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
    const max = Math.max(r, g, b);
    const rest = [r, g, b].filter((v) => v !== max);
    if (max < 8 * 8 * 40) return '?';                 // nothing bright enough yet
    if (max < Math.max(...rest) * 1.6) return '?';    // no clear winner
    return (max === r ? 'r' : max === g ? 'g' : 'b') as 'r' | 'g' | 'b';
  });

/**
 * Sample the live canvas for `ms`. Returns both the tally and the ORDER, because
 * a tally cannot express "it looped" — and the untrimmed path looping is exactly
 * the compatibility clause this cycle must not break. Measured: with every clip
 * forced onto the trimmed code path, the tally still showed all three thirds
 * (the clip simply played once through and stopped on blue) and a set-based
 * assertion passed. The sequence is what caught it.
 */
const watchStage = async (page: Page, ms: number): Promise<{
  counts: Record<Channel, number>; seq: Channel[];
}> => {
  const counts: Record<Channel, number> = { r: 0, g: 0, b: 0, '?': 0 };
  const seq: Channel[] = [];
  const until = Date.now() + ms;
  while (Date.now() < until) {
    const c = await stageChannel(page);
    counts[c]++;
    seq.push(c);
    await page.waitForTimeout(90);
  }
  return { counts, seq };
};

/**
 * PER-rAF TRACING — the instrument that can actually see a one-frame defect.
 *
 * `watchStage` samples from node every ~90 ms, and that is fine for "which
 * thirds did this clip show". It is USELESS for a stray FRAME: a wrap flash
 * lasts one compositor frame (~16 ms), so a 90 ms sampler sees it only by luck
 * and reports it as flake. An adversarial audit traced this same window per-rAF
 * and found 15 out-of-window frames in 2401 — spaced exactly one per wrap, i.e.
 * 100% of wraps, every one carrying `readyState:1 seeking:true`, while the
 * element's own currentTime never once left the window. Deterministic, not
 * flaky; the DRAW was disowning a live clip mid-seek and falling through to the
 * import still, which holds a frame from before the IN point.
 *
 * So the loop runs INSIDE the page, on the same clock the compositor does.
 */
const traceStage = async (page: Page, ms: number): Promise<{
  frames: number; tally: Record<string, number>; bad: unknown[]; playheadOutside: number;
}> =>
  page.evaluate(({ ms, lo, hi }) => new Promise((resolve) => {
    const cv = document.querySelector('canvas') as HTMLCanvasElement;
    const vid = document.querySelector('video:not([controls])') as HTMLVideoElement | null;
    const s = document.createElement('canvas'); s.width = 8; s.height = 8;
    const ctx = s.getContext('2d')!;
    const tally: Record<string, number> = {};
    const bad: unknown[] = [];
    let frames = 0, playheadOutside = 0;
    const t0 = performance.now();
    const step = () => {
      try { ctx.drawImage(cv, 0, 0, 8, 8); } catch { /* not ready */ }
      const d = ctx.getImageData(0, 0, 8, 8).data;
      let r = 0, g = 0, b = 0;
      for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
      const max = Math.max(r, g, b);
      const rest = [r, g, b].filter((v) => v !== max);
      const c = (max < 8 * 8 * 40 || max < Math.max(...rest) * 1.6)
        ? '?' : (max === r ? 'r' : max === g ? 'g' : 'b');
      tally[c] = (tally[c] || 0) + 1;
      frames++;
      if (c === 'r' || c === 'b') {
        if (bad.length < 12 && vid) {
          bad.push({ c, t: +vid.currentTime.toFixed(3), rs: vid.readyState, seek: vid.seeking, i: frames });
        } else if (bad.length < 12) bad.push({ c, i: frames });
      }
      // Is the PLAYHEAD outside the window, or only the picture? They are
      // different defects and conflating them sent the first diagnosis wrong.
      if (vid && (vid.currentTime < lo - 0.05 || vid.currentTime > hi + 0.05)) playheadOutside++;
      if (performance.now() - t0 < ms) requestAnimationFrame(step);
      else resolve({ frames, tally, bad, playheadOutside });
    };
    requestAnimationFrame(step);
  }), { ms, lo: IN_SEC, hi: OUT_SEC }) as Promise<{
    frames: number; tally: Record<string, number>; bad: unknown[]; playheadOutside: number;
  }>;

/** True if the strip ever goes back to an EARLIER third — i.e. the clip wrapped. */
const wrapped = (seq: Channel[]): boolean => {
  const rank: Record<string, number> = { r: 0, g: 1, b: 2 };
  let high = -1;
  for (const c of seq) {
    if (!(c in rank)) continue;
    if (rank[c] < high) return true;
    high = Math.max(high, rank[c]);
  }
  return false;
};

/**
 * The EXPORTED FILE's picture: decode the produced MP4 in the page's own decoder
 * and read the pixels of real frames. A frame count, a duration and a "no
 * warnings" pill were all true of every export this project has shipped a
 * picture bug in.
 */
const exportedChannels = async (page: Page, at: number[]): Promise<Channel[]> =>
  page.evaluate(async (times) => {
    const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
    if (!el || !el.src) return times.map(() => '?' as const);
    const v = document.createElement('video');
    v.src = el.src; v.muted = true; (v as HTMLVideoElement).playsInline = true;
    await new Promise<void>((res) => {
      if (v.readyState >= 1) return res();
      v.addEventListener('loadedmetadata', () => res(), { once: true });
      v.addEventListener('error', () => res(), { once: true });
      setTimeout(res, 8000);
    });
    const s = document.createElement('canvas');
    s.width = 8; s.height = 8;
    const ctx = s.getContext('2d');
    const out: string[] = [];
    for (const t of times) {
      if (!ctx || !Number.isFinite(v.duration) || v.duration <= 0) { out.push('?'); continue; }
      await new Promise<void>((res) => {
        const done = () => res();
        v.addEventListener('seeked', done, { once: true });
        v.addEventListener('error', done, { once: true });
        setTimeout(done, 5000);
        try { v.currentTime = Math.min(t, Math.max(0, v.duration - 0.05)); } catch { done(); }
      });
      try { ctx.drawImage(v, 0, 0, 8, 8); } catch { out.push('?'); continue; }
      const d = ctx.getImageData(0, 0, 8, 8).data;
      let r = 0, g = 0, b = 0;
      for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
      const max = Math.max(r, g, b);
      const rest = [r, g, b].filter((x) => x !== max);
      if (max < 8 * 8 * 40 || max < Math.max(...rest) * 1.6) out.push('?');
      else out.push(max === r ? 'r' : max === g ? 'g' : 'b');
    }
    return out;
  }, at) as Promise<Channel[]>;

/**
 * The EXPORTED FILE's sound: decode it and measure energy at each tone with a
 * Goertzel filter. The instrument is lifted from `video-audio-export.spec.ts`,
 * which established that nothing cheaper can see an audio defect — the render
 * succeeds, the MP4 opens, the frame count is exactly right, and the only thing
 * wrong is what is in it.
 *
 * WHAT IS DIFFERENT HERE, AND WHY IT HAD TO BE.
 *   That spec measures ONE window from the middle of the take, which is right
 *   for its question ("is this clip's tone in the file at all"). It is wrong for
 *   this one, and provably so: with the audio mixer deliberately ignoring the
 *   trim window, the first version of this test PASSED. A five-second take of
 *   the untrimmed clip is red, then green, then blue — and the midpoint lands in
 *   the green third, which is exactly the third the trim was supposed to isolate.
 *   The measurement agreed with the correct answer for the wrong reason.
 *
 *   So the sweep runs FIVE windows across the whole file and keeps the LOUDEST
 *   reading per frequency. The question a trim test has to ask is not "is the
 *   right tone in the middle" but "is a wrong tone ANYWHERE", and only a
 *   measurement that looks everywhere can answer it.
 */
const TONE_PROBES = [0.12, 0.3, 0.5, 0.7, 0.86];

const measureTones = async (page: Page, freqs: number[], controlHz: number) =>
  page.evaluate(async ({ freqs, controlHz, probes }) => {
    const fail = (reason: string) => ({ ok: false, reason, bins: [] as number[], control: 0, rms: 0 });
    const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
    if (!el || !el.src) return fail('no result preview element');
    const bytes = await (await fetch(el.src)).arrayBuffer();
    const Ctx: typeof AudioContext =
      (window as unknown as { AudioContext: typeof AudioContext }).AudioContext
      || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = new Ctx();
    let buf: AudioBuffer;
    try { buf = await ctx.decodeAudioData(bytes.slice(0)); } catch (e) {
      await ctx.close().catch(() => {});
      return fail(`no decodable audio track (${(e as Error)?.message || e})`);
    }
    const rate = buf.sampleRate;
    const ch = buf.getChannelData(0);
    const goertzel = (data: Float32Array, freq: number): number => {
      const n = data.length;
      const k = Math.round((n * freq) / rate);
      const w = (2 * Math.PI * k) / n;
      const cw = Math.cos(w), sw = Math.sin(w), coeff = 2 * cw;
      let s0 = 0, s1 = 0, s2 = 0;
      for (let i = 0; i < n; i++) { s0 = data[i] + coeff * s1 - s2; s2 = s1; s1 = s0; }
      const re = s1 - s2 * cw, im = s2 * sw;
      return Math.sqrt(re * re + im * im) / (n / 2);
    };
    // FIVE windows across the file, LOUDEST reading kept per frequency. The
    // probe fractions avoid the very head (encoder priming) and the very tail
    // (truncated to the frame count) without ever leaving a stretch unmeasured.
    const n = Math.min(16384, ch.length);
    const bins = freqs.map(() => 0);
    let control = 0;
    let rms = 0;
    for (const p of probes) {
      const start = Math.max(0, Math.min(ch.length - n, Math.floor(ch.length * p) - Math.floor(n / 2)));
      const win = ch.slice(start, start + n);
      if (!win.length) continue;
      freqs.forEach((f, i) => { bins[i] = Math.max(bins[i], goertzel(win, f)); });
      control = Math.max(control, goertzel(win, controlHz));
      let r = 0;
      for (let i = 0; i < win.length; i++) r += win[i] * win[i];
      rms = Math.max(rms, Math.sqrt(r / win.length));
    }
    await ctx.close().catch(() => {});
    return { ok: true, reason: '', bins, control, rms };
  }, { freqs, controlHz, probes: TONE_PROBES });

/**
 * The exported sound's ENVELOPE — energy at one tone, slice by slice, across the
 * whole file.
 *
 * `measureTones` above asks "is this tone anywhere in the file", which is the
 * right question for a trim and the WRONG one for a period. The lap defect puts
 * exactly the right tone in the file — 440 Hz is genuinely part of this clip —
 * and gets it wrong only in WHEN: the sound should be there for one second of
 * every three-second lap and it is there for all three. A measurement with no
 * time axis cannot see that, and every existing assertion in this file passed
 * while it was happening.
 */
const toneEnvelope = async (page: Page, hz: number, sliceSec: number) =>
  page.evaluate(async ({ hz, sliceSec }) => {
    const fail = (reason: string) =>
      ({ ok: false, reason, dur: 0, slices: [] as { t: number; e: number; rms: number }[] });
    const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
    if (!el || !el.src) return fail('no result preview element');
    const bytes = await (await fetch(el.src)).arrayBuffer();
    const Ctx: typeof AudioContext =
      (window as unknown as { AudioContext: typeof AudioContext }).AudioContext
      || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = new Ctx();
    let buf: AudioBuffer;
    try { buf = await ctx.decodeAudioData(bytes.slice(0)); } catch (e) {
      await ctx.close().catch(() => {});
      return fail(`no decodable audio track (${(e as Error)?.message || e})`);
    }
    const rate = buf.sampleRate;
    const ch = buf.getChannelData(0);
    const goertzel = (data: Float32Array, freq: number): number => {
      const n = data.length;
      const k = Math.round((n * freq) / rate);
      const w = (2 * Math.PI * k) / n;
      const cw = Math.cos(w), sw = Math.sin(w), coeff = 2 * cw;
      let s0 = 0, s1 = 0, s2 = 0;
      for (let i = 0; i < n; i++) { s0 = data[i] + coeff * s1 - s2; s2 = s1; s1 = s0; }
      const re = s1 - s2 * cw, im = s2 * sw;
      return Math.sqrt(re * re + im * im) / (n / 2);
    };
    const n = Math.floor(rate * sliceSec);
    const slices: { t: number; e: number; rms: number }[] = [];
    for (let start = 0; start + n <= ch.length; start += n) {
      const win = ch.slice(start, start + n);
      let r = 0;
      for (let i = 0; i < win.length; i++) r += win[i] * win[i];
      slices.push({ t: start / rate, e: goertzel(win, hz), rms: Math.sqrt(r / win.length) });
    }
    await ctx.close().catch(() => {});
    return { ok: true, reason: '', dur: ch.length / rate, slices };
  }, { hz, sliceSec });

const startPlaybackIfGated = async (page: Page) => {
  const tap = page.getByRole('button', { name: /tap to play/i });
  if (await tap.count()) await tap.first().click().catch(() => { /* raced with autoplay */ });
};

/** Import the ramp and wait until it is genuinely a live, playing clip. */
const importRamp = async (page: Page) => {
  await page.locator('input[type="file"]').first().setInputFiles([RAMP]);
  await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
  await expect(page.getByRole('button', { name: `Stop playing ${CLIP_NAME}` }))
    .toBeVisible({ timeout: 200_000 });
  await startPlaybackIfGated(page);
  await expect.poll(
    () => page.evaluate(() => {
      const v = document.querySelector('video:not([controls])') as HTMLVideoElement | null;
      return !!v && v.readyState >= 2;
    }),
    { timeout: 60_000 },
  ).toBe(true);
};

/** Open the sheet, set the window, close it. */
const applyTrim = async (page: Page, inSec: number, outSec: number) => {
  await page.getByRole('button', { name: `Trim ${CLIP_NAME}` }).click();
  const sheet = page.getByRole('dialog', { name: `Trim ${CLIP_NAME}` });
  await expect(sheet).toBeVisible({ timeout: 15_000 });
  // OUT first: pulling IN up past the current OUT is repaired by the window's
  // own floor, and setting the far edge first keeps the intermediate states
  // legal rather than relying on that repair.
  await sheet.getByLabel(`Out point for ${CLIP_NAME}`).fill(String(outSec));
  await sheet.getByLabel(`In point for ${CLIP_NAME}`).fill(String(inSec));
  await expect(sheet.getByTestId('trim-readout')).toContainText(`${inSec.toFixed(1)}s→${outSec.toFixed(1)}s`);
  await sheet.getByRole('button', { name: 'Close trim' }).click();
  await expect(sheet).toBeHidden({ timeout: 10_000 });
};

test.describe('trim — a clip plays the part you chose', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
      if (typeof caches !== 'undefined') for (const k of await caches.keys()) await caches.delete(k);
    }).catch(() => { /* no SW in this context is fine */ });
  });

  /**
   * T1 — THE CONTROL, AND IT COMES FIRST.
   *
   * An untrimmed clip must still show its WHOLE self. This is the compatibility
   * clause the pure module asserts bit-for-bit (I2), asserted here as behaviour:
   * if this test ever goes red, trim broke every clip nobody trimmed, which is
   * strictly worse than trim not working.
   */
  test('untrimmed, the clip still plays all three thirds', async ({ page }) => {
    test.setTimeout(180_000);
    await importRamp(page);
    const { counts, seq } = await watchStage(page, 11_000);   // ~1.8 laps of a 6s clip
    console.log('[trim] untrimmed thirds seen:', JSON.stringify(counts), seq.join(''));
    expect(counts.r, `RED third never appeared — ${JSON.stringify(counts)}`).toBeGreaterThan(0);
    expect(counts.g, `GREEN third never appeared — ${JSON.stringify(counts)}`).toBeGreaterThan(0);
    expect(counts.b, `BLUE third never appeared — ${JSON.stringify(counts)}`).toBeGreaterThan(0);
    // AND IT MUST STILL LOOP. An untrimmed clip keeps the element's own native
    // loop; nothing about trim may turn that into a play-once-and-freeze.
    expect(wrapped(seq),
      `an untrimmed clip must keep looping — it played through once and stopped (${seq.join('')})`)
      .toBe(true);
  });

  /**
   * T2 — THE LIVE PATH. Trim to the blue third and the other two must never be
   * on screen again, across several laps of a 1.3s window.
   */
  test('a trimmed clip only ever shows its window, lap after lap', async ({ page }) => {
    test.setTimeout(180_000);
    await importRamp(page);
    await applyTrim(page, IN_SEC, OUT_SEC);

    // The chip must SAY it is trimmed — a window nobody can see is a window
    // nobody will trust.
    await expect(page.getByRole('button', { name: `Trim ${CLIP_NAME}` }))
      .toContainText('1.3s', { timeout: 10_000 });

    await page.waitForTimeout(1_200);              // let the first wrap settle
    const { counts, seq } = await watchStage(page, 8_000);   // ~6 laps of a 1.3s window
    console.log('[trim] trimmed-to-GREEN thirds seen:', JSON.stringify(counts), seq.join(''));

    expect(counts.g, `the GREEN window must be on screen — ${JSON.stringify(counts)}`).toBeGreaterThan(20);

    /**
     * ZERO OUT-OF-WINDOW FRAMES, traced per-rAF.
     *
     * The first version of this assertion tolerated a stray sample and explained
     * it as compositor starvation. That explanation was WRONG, and an
     * adversarial audit proved it: the stray was one flash of the trimmed-out
     * head on EVERY wrap, caused by the draw gate demoting a mid-seek clip to
     * its import still. With that fixed the correct claim is the strict one, and
     * a tolerance would only hide the same bug coming back.
     */
    const tr = await traceStage(page, 8_000);   // ~6 laps of a 1.3s window
    console.log(`[trim] per-rAF: frames=${tr.frames} tally=${JSON.stringify(tr.tally)} `
      + `playheadOutside=${tr.playheadOutside} bad=${JSON.stringify(tr.bad).slice(0, 300)}`);

    expect(tr.frames, 'the tracer must have seen real frames').toBeGreaterThan(200);
    expect(tr.playheadOutside,
      `the playhead left the window on ${tr.playheadOutside} frames — the watchdog is late`).toBe(0);
    expect((tr.tally.r || 0) + (tr.tally.b || 0),
      `${(tr.tally.r || 0) + (tr.tally.b || 0)} of ${tr.frames} frames painted material outside `
      + `the trim window — ${JSON.stringify(tr.bad)}`).toBe(0);
  });

  /**
   * T3 + T4 — THE FILE. One take, both proofs: the exported MP4's PICTURE is the
   * trimmed third, and its SOUND is that third's tone and not the others'.
   *
   * These are separate assertions on purpose. Trim reaches the picture through
   * `Stage.seekClipTo` and the sound through `offlineAudio.mixSources`, and
   * before this cycle those were two independent copies of one formula — so a
   * fix landing on one and not the other is exactly the failure to guard.
   */
  test('the exported FILE carries the trim, in picture and in sound', async ({ page }) => {
    test.setTimeout(420_000);
    await importRamp(page);
    await applyTrim(page, IN_SEC, OUT_SEC);

    // Sound is ON by default for an imported clip; assert it rather than set it,
    // so this test cannot silently re-encode the import default.
    await expect(page.getByRole('button', { name: `Mute ${CLIP_NAME}` })).toBeVisible({ timeout: 30_000 });

    const five = page.getByRole('button', { name: '5s', exact: true });
    if (await five.count()) await five.first().click();

    await page.getByRole('button', { name: 'Record video' }).click();
    await expect(page.locator('p.tabular-nums').filter({ hasText: /frames/ }))
      .toBeVisible({ timeout: 360_000 });

    // ---- T3: THE PICTURE --------------------------------------------------
    const frames = await exportedChannels(page, [0.3, 1.1, 2.0, 2.9, 3.8, 4.5]);
    console.log('[trim] exported frame channels:', JSON.stringify(frames));
    expect(frames.filter((c) => c === 'g').length,
      `the export must show the GREEN window — got ${JSON.stringify(frames)}`).toBeGreaterThanOrEqual(4);
    expect(frames.includes('r'),
      `RED is before IN and must not be in the file — got ${JSON.stringify(frames)}`).toBe(false);
    expect(frames.includes('b'),
      `BLUE is past OUT and must not be in the file — got ${JSON.stringify(frames)}`).toBe(false);

    // ---- T4: THE SOUND ----------------------------------------------------
    const t = await measureTones(page, [HZ_GREEN, HZ_RED, HZ_BLUE], HZ_CONTROL);
    expect(t.ok, `the export must contain audio — ${t.reason}`).toBe(true);
    expect(t.rms, 'the audio track must not be digital silence').toBeGreaterThan(0.001);
    const [green, red, blue] = t.bins;
    console.log(`[trim] tones 1200=${green.toFixed(5)} 440=${red.toFixed(5)} `
      + `3000=${blue.toFixed(5)} control=${t.control.toFixed(5)} rms=${t.rms.toFixed(4)}`);
    expect(green, `1200 Hz (the trimmed-TO third) must be present — ${green} vs control ${t.control}`)
      .toBeGreaterThan(t.control * 8);
    // The discriminator: the tones the user cut out must be at this file's own
    // noise floor, not merely quieter.
    expect(red, `440 Hz is before IN and must be at the noise floor — ${red} vs green ${green}`)
      .toBeLessThan(green / 8);
    expect(blue, `3000 Hz is past OUT and must be at the noise floor — ${blue} vs green ${green}`)
      .toBeLessThan(green / 8);
  });
});

/**
 * T4b — THE TWO HANDLES STOP AT EACH OTHER.
 *
 * `setOut` always clamped against IN. `setIn` clamped only against the end of
 * the clip, so an IN dragged past OUT reached `normaliseWindow`, whose
 * minimum-window repair grows OUT FORWARD — and the user's chosen OUT ratcheted
 * along behind the thumb and was gone for good. Dragging the IN thumb rightwards
 * to find its limit is the single most natural thing to do with this control,
 * and it is trivially easy with a thumb on a phone.
 */
test.describe('the trim handles', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
  });

  test('dragging IN past OUT does not destroy the OUT point', async ({ page }) => {
    test.setTimeout(180_000);
    await importRamp(page);
    await page.getByRole('button', { name: `Trim ${CLIP_NAME}` }).click();
    const sheet = page.getByRole('dialog', { name: `Trim ${CLIP_NAME}` });
    await expect(sheet).toBeVisible({ timeout: 15_000 });

    const inSlider = sheet.getByLabel(`In point for ${CLIP_NAME}`);
    const outSlider = sheet.getByLabel(`Out point for ${CLIP_NAME}`);
    const readout = sheet.getByTestId('trim-readout');

    // NOTE '2', not '2.0'. Playwright's range fill writes the string and then
    // compares it against `input.value`, which the DOM has normalised — so a
    // trailing zero fails as "Malformed value" while meaning the same number.
    await outSlider.fill('2');
    await expect(readout).toContainText('0.0s→2.0s');

    // Now shove IN well past OUT, the way a thumb does.
    for (const v of ['1.5', '1.9', '2.1', '2.5', '4']) {
      await inSlider.fill(v);
      const out = await outSlider.inputValue();
      expect(Number(out),
        `dragging IN to ${v} moved the user's OUT point to ${out} — it must stay at 2.0`)
        .toBeCloseTo(2.0, 5);
    }
    // The window is pinned at the floor BELOW the OUT point, not dragged past it.
    await expect(readout).toContainText('1.9s→2.0s');

    // And walking IN back to the left restores the original selection intact.
    await inSlider.fill('0');
    await expect(readout).toContainText('0.0s→2.0s');
  });

  /**
   * T3b — THE HANDLES SURVIVE MORE THAN ONE KEYSTROKE.
   *
   * A drag cannot see this and neither can `fill()`: a range input keeps pointer
   * capture, so it goes on receiving the drag even after something steals focus,
   * and `fill()` writes the value in one shot. Only a real ArrowRight run can
   * tell you whether the control is still focused for the SECOND press.
   *
   * It was not. The sheet's modal effect depended on `[onClose]` — an inline
   * arrow rebuilt on every VideoStage render — so every value change re-ran it
   * and re-focused the Close button. The handle moved exactly one step and went
   * dead, and Enter, the natural "confirm", dismissed the sheet. Found by an
   * adversarial audit driving the keyboard, not by any assertion in this file.
   */
  test('the IN handle keeps focus across repeated arrow presses', async ({ page }) => {
    test.setTimeout(180_000);
    await importRamp(page);
    await page.getByRole('button', { name: `Trim ${CLIP_NAME}` }).click();
    const sheet = page.getByRole('dialog', { name: `Trim ${CLIP_NAME}` });
    await expect(sheet).toBeVisible({ timeout: 15_000 });

    const inSlider = sheet.getByLabel(`In point for ${CLIP_NAME}`);
    await inSlider.focus();
    const step = Number(await inSlider.getAttribute('step'));
    const PRESSES = 5;
    for (let i = 0; i < PRESSES; i++) await page.keyboard.press('ArrowRight');

    const focused = await page.evaluate(() =>
      (document.activeElement as HTMLElement | null)?.getAttribute('aria-label') || '(none)');
    expect(focused, 'the arrow keys must not hand focus to another control')
      .toBe(`In point for ${CLIP_NAME}`);

    const value = Number(await inSlider.inputValue());
    expect(value,
      `${PRESSES} presses of ArrowRight must move IN by ${PRESSES} steps, not one — it read ${value}`)
      .toBeCloseTo(step * PRESSES, 5);

    // And the sheet is still open: Enter must not be routed into a Close button
    // the user never focused.
    await page.keyboard.press('Enter');
    await expect(sheet).toBeVisible();
  });
});

/**
 * T4c — A CLIP WHOSE CONTAINER CARRIES NO DURATION.
 *
 * `nodur.webm` has no Duration element — the shape a screen recorder, a
 * MediaRecorder capture, and this app's OWN realtime fallback export all
 * produce. The app resolves the real length itself at import (`probeVideo`), so
 * the sheet reports a perfectly normal trim; the Stage's `<video>`, which does
 * no such trick, reads `duration === Infinity` until playback reaches the end.
 *
 * With the span taken from the element alone, `spanOf` returned 0, the window
 * resolved to "whole clip", the native loop stayed ON, and the clip played
 * everything the user had cut — measured at 21.6 s of un-enforced playback on a
 * 24 s recording, scaling with the length of the file. The UI promised a trim
 * the Stage was ignoring.
 */
test.describe('a clip with no duration in its container', () => {
  test('is trimmed anyway, from the first frame', async ({ page }) => {
    test.setTimeout(240_000);
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);

    const NAME = 'nodur.webm';
    await page.locator('input[type="file"]').first()
      .setInputFiles([join(HERE, '..', 'fixtures', NAME)]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: `Stop playing ${NAME}` }))
      .toBeVisible({ timeout: 200_000 });
    const tap = page.getByRole('button', { name: /tap to play/i });
    if (await tap.count()) await tap.first().click().catch(() => { /* raced */ });

    // THE PRECONDITION: the element really must not know its own length, or this
    // test is just another pass over the normal path.
    const elDur = await page.evaluate(() => {
      const v = document.querySelector('video:not([controls])') as HTMLVideoElement | null;
      return v ? v.duration : null;
    });
    console.log('[trim/nodur] element duration at import:', elDur);
    expect(Number.isFinite(elDur as number),
      `the fixture must have an unresolvable duration, got ${elDur}`).toBe(false);

    await page.getByRole('button', { name: `Trim ${NAME}` }).click();
    const sheet = page.getByRole('dialog', { name: `Trim ${NAME}` });
    await expect(sheet).toBeVisible({ timeout: 15_000 });
    await sheet.getByLabel(`Out point for ${NAME}`).fill(String(OUT_SEC));
    await sheet.getByLabel(`In point for ${NAME}`).fill(String(IN_SEC));
    await sheet.getByRole('button', { name: 'Close trim' }).click();

    await page.waitForTimeout(1_200);
    const tr = await traceStage(page, 6_000);
    console.log(`[trim/nodur] per-rAF: frames=${tr.frames} tally=${JSON.stringify(tr.tally)} `
      + `playheadOutside=${tr.playheadOutside}`);
    expect(tr.frames, 'the tracer must have seen real frames').toBeGreaterThan(150);
    expect(tr.playheadOutside,
      `the window was not enforced — the playhead left it on ${tr.playheadOutside} frames`).toBe(0);
    expect((tr.tally.r || 0) + (tr.tally.b || 0),
      `the UI promised a trim the Stage ignored: ${JSON.stringify(tr.tally)}`).toBe(0);
  });
});

/**
 * T5 — THE AUDIT'S MEDIUM, AS A REGRESSION.
 *
 * `shortaudio.mp4` is six seconds of picture over three seconds of sound — a mic
 * that cut out, a music bed that ran short, footage a tool assembled without
 * padding the audio. Trim to the BLUE third (4→6) and the window lands entirely
 * past the end of the audio track.
 *
 * What shipped in this cycle's first cut: `audioPlan` re-ran `normaliseWindow`
 * against the decoded BUFFER's span, and that function's minimum-window repair
 * MOVES THE IN POINT — so a window of [4, 6] clamped to [2.99998, 2.99998],
 * "repaired" to [2.85, 3.00], and the export looped the last 150 ms of the audio
 * roughly thirty-three times across a five-second take. The picture was correct
 * the whole way through, and every assertion in this file passed. An adversarial
 * audit driving the real app found it.
 *
 * The correct behaviour is SILENCE: the user trimmed to a part of the clip that
 * has no sound, and inventing a fragment to loop is worse than saying so.
 */
test.describe('a trim past the end of a short audio track', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
  });

  test('exports silence, not a fragment of the audio looped', async ({ page }) => {
    test.setTimeout(420_000);
    const NAME = 'shortaudio.mp4';
    await page.locator('input[type="file"]').first()
      .setInputFiles([join(HERE, '..', 'fixtures', NAME)]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: `Stop playing ${NAME}` }))
      .toBeVisible({ timeout: 200_000 });
    const tap = page.getByRole('button', { name: /tap to play/i });
    if (await tap.count()) await tap.first().click().catch(() => { /* raced */ });

    await page.getByRole('button', { name: `Trim ${NAME}` }).click();
    const sheet = page.getByRole('dialog', { name: `Trim ${NAME}` });
    await expect(sheet).toBeVisible({ timeout: 15_000 });
    await sheet.getByLabel(`In point for ${NAME}`).fill('4.2');
    await sheet.getByRole('button', { name: 'Close trim' }).click();

    const five = page.getByRole('button', { name: '5s', exact: true });
    if (await five.count()) await five.first().click();
    await page.getByRole('button', { name: 'Record video' }).click();
    await expect(page.locator('p.tabular-nums').filter({ hasText: /frames/ }))
      .toBeVisible({ timeout: 360_000 });

    // The PICTURE still has to be right — the defect never touched it, and a
    // regression that "fixed" the sound by breaking the picture must not pass.
    const frames = await exportedChannels(page, [0.3, 1.5, 3.0, 4.5]);
    console.log('[trim/shortaudio] exported frame channels:', JSON.stringify(frames));
    expect(frames.includes('r'), `RED is outside the window — got ${JSON.stringify(frames)}`).toBe(false);
    expect(frames.filter((c) => c === 'b').length,
      `the export must show the BLUE window — got ${JSON.stringify(frames)}`).toBeGreaterThanOrEqual(3);

    // The SOUND must be silence. Either there is no audio track at all (the
    // mixer wired nothing, which is the honest outcome) or it is at the noise
    // floor — what must NOT be there is 440 Hz, the tone the user trimmed past.
    const t = await measureTones(page, [HZ_RED], HZ_CONTROL);
    console.log(`[trim/shortaudio] ok=${t.ok} rms=${t.rms} 440=${t.bins[0]} control=${t.control}`);
    if (t.ok) {
      expect(t.bins[0],
        `440 Hz is past the OUT point and must not be in the file — 440=${t.bins[0]} control=${t.control}`)
        .toBeLessThan(Math.max(t.control * 4, 0.002));
      expect(t.rms,
        `the exported audio must be silence, not a looped fragment — rms=${t.rms}`)
        .toBeLessThan(0.01);
    }
  });
});

/**
 * T7 — A TRIM THAT STRADDLES THE END OF THE AUDIO TRACK.
 *
 * T5 above covers the window landing ENTIRELY past the sound, which is why it is
 * green and why it never saw this. Put the window ACROSS the boundary instead —
 * `shortaudio.mp4` is 6 s of picture over 3 s of 440 Hz, so a trim to 2->5 has
 * sound for its first second and none for its remaining two — and the two
 * timelines have different periods for the first time:
 *
 *     the picture laps every 3 s          (the window)
 *     the node looped every 1 s           (the window CLAMPED into the buffer)
 *
 * so from one second in they walk apart and never meet. What that sounds like is
 * an unbroken 440 Hz drone under a picture the file has no sound for — the right
 * tone, in the wrong place, for two thirds of the take. Every existing assertion
 * in this file passes while it happens, because they all ask WHETHER a tone is
 * in the file and this defect gets only the WHEN wrong.
 *
 * So the measurement here has a time axis. A correct render is loud for one
 * second of every three:
 *
 *     t 0–1  loud   t 1–3  silent   t 3–4  loud   t 4–5  silent   = 40% duty
 *
 * and the defect is ~100%. The assertion is the DUTY CYCLE plus the existence of
 * a long unbroken silence, which brackets the answer from both sides: a drone
 * fails the first, and muting the clip outright fails both.
 */
test.describe('a trim that straddles the end of a short audio track', () => {
  const NAME = 'shortaudio.mp4';
  const T_IN = 2;
  const T_OUT = 5;
  const TAKE = 5;
  /** Source seconds of sound the file actually has inside the window. */
  const LAP = T_OUT - T_IN;          // 3 s of picture per lap
  const SOUND = 3 - T_IN;            // ~1 s of it has audio

  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
  });

  test('the sound laps with the PICTURE, not with the audio track', async ({ page }) => {
    test.setTimeout(420_000);
    await page.locator('input[type="file"]').first()
      .setInputFiles([join(HERE, '..', 'fixtures', NAME)]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: `Stop playing ${NAME}` }))
      .toBeVisible({ timeout: 200_000 });
    await startPlaybackIfGated(page);

    await page.getByRole('button', { name: `Trim ${NAME}` }).click();
    const sheet = page.getByRole('dialog', { name: `Trim ${NAME}` });
    await expect(sheet).toBeVisible({ timeout: 15_000 });
    await sheet.getByLabel(`Out point for ${NAME}`).fill(String(T_OUT));
    await sheet.getByLabel(`In point for ${NAME}`).fill(String(T_IN));
    await sheet.getByRole('button', { name: 'Close trim' }).click();

    const five = page.getByRole('button', { name: `${TAKE}s`, exact: true });
    if (await five.count()) await five.first().click();
    await page.getByRole('button', { name: 'Record video' }).click();
    await expect(page.locator('p.tabular-nums').filter({ hasText: /frames/ }))
      .toBeVisible({ timeout: 360_000 });

    // The PICTURE first — the defect never touched it, and a "fix" that quiets
    // the sound by breaking the window must not pass. [2,5] of an R/G/B sixth
    // is green then blue; RED is before IN and cannot legitimately appear.
    const frames = await exportedChannels(page, [0.4, 1.4, 2.6, 3.4, 4.4]);
    console.log('[trim/straddle] exported frame channels:', JSON.stringify(frames));
    expect(frames.includes('r'),
      `RED is before the IN point and must not be in the file — got ${JSON.stringify(frames)}`).toBe(false);
    expect(frames.filter((c) => c === 'g' || c === 'b').length,
      `the export must show the trimmed window — got ${JSON.stringify(frames)}`).toBeGreaterThanOrEqual(4);

    // ---- THE SOUND, WITH A TIME AXIS -------------------------------------
    const env = await toneEnvelope(page, HZ_RED, 0.25);
    expect(env.ok, `the export must contain audio — ${env.reason}`).toBe(true);
    expect(env.slices.length, 'the envelope must have real slices').toBeGreaterThan(8);

    const peak = Math.max(...env.slices.map((s) => s.e));
    expect(peak, 'the 440 Hz tone must be in the file at all — the clip is not muted')
      .toBeGreaterThan(0.005);
    // Loud/quiet against THIS file's own peak, so the claim survives any encoder
    // level. The tone is either fully present or at the noise floor; measured,
    // the two populations sit three orders of magnitude apart.
    const loud = env.slices.map((s) => s.e > peak * 0.35);
    console.log(`[trim/straddle] dur=${env.dur.toFixed(2)}s peak=${peak.toFixed(5)} `
      + `envelope=${env.slices.map((s) => (s.e > peak * 0.35 ? '#' : '.')).join('')}`);
    console.log('[trim/straddle] slice energies: '
      + env.slices.map((s) => `${s.t.toFixed(2)}:${s.e.toFixed(4)}`).join(' '));

    const duty = loud.filter(Boolean).length / loud.length;
    const expected = SOUND / LAP;                       // ~0.333 of every lap
    expect(duty,
      `the sound must be present for about ${(expected * 100).toFixed(0)}% of the take and is `
      + `${(duty * 100).toFixed(0)}% — 100% is the audio track looping at ITS period instead of `
      + 'the picture\'s, which is the defect this test exists for')
      .toBeLessThan(0.55);
    expect(duty,
      `the sound is present for only ${(duty * 100).toFixed(0)}% of the take — the clip has been `
      + 'silenced rather than re-timed')
      .toBeGreaterThan(0.25);

    /**
     * THE PHASE ANCHOR — and it is the assertion that carries this test.
     *
     * The two statistics above are both invariant under TRANSLATION. An
     * adversarial audit built this exact measurement over the real fixture and
     * showed it: a render whose every lap is one second LATE — a full second of
     * audible desync, sound playing under a picture the file is silent for —
     * scores duty 40%, longest silence 2.00 s, peak 0.1247. Digit for digit the
     * correct render's numbers. So do "only the first lap was wired" (20% /
     * 3.00 s) and "each lap plays half its sound" (20% / 2.50 s). Every one of
     * those passes a duty band and a longest-run rail, because those two say HOW
     * MUCH sound and HOW LONG the biggest gap, and never WHERE.
     *
     * The picture's position has to appear in the assertion, so here it is: the
     * file has sound at output `t` exactly when the picture's source time there
     * is before the end of the audio track, i.e. when `t % LAP < SOUND`. Slices
     * that straddle a transition are genuinely part-loud and are skipped by name
     * rather than fudged with a threshold.
     */
    const EDGE = 0.02;
    let anchored = 0;
    const wrong: string[] = [];
    env.slices.forEach((s, i) => {
      const ph = s.t % LAP;
      const wholeSliceLoud = ph + 0.25 <= SOUND + EDGE;
      const wholeSliceQuiet = ph >= SOUND - EDGE && ph + 0.25 <= LAP + EDGE;
      if (!wholeSliceLoud && !wholeSliceQuiet) return;       // straddles a transition
      anchored++;
      const want = wholeSliceLoud;
      if (loud[i] !== want) {
        wrong.push(`t=${s.t.toFixed(2)} (source ${(T_IN + ph).toFixed(2)}) want=`
          + `${want ? 'SOUND' : 'silence'} got=${loud[i] ? 'SOUND' : 'silence'} e=${s.e.toFixed(4)}`);
      }
    });
    expect(anchored,
      'the phase anchor must classify most slices, or it is asserting nothing').toBeGreaterThan(12);
    expect(wrong,
      `${wrong.length} slice(s) have sound where the picture says they must not, or silence where `
      + 'it says they must — the sound is not lapping with the picture')
      .toEqual([]);
  });
});

/**
 * T6 — THE SHEET ON A PHONE. The trim control is the first thing this app has
 * shipped that is a DRAG, and a drag target is exactly what a 390px screen and a
 * thumb break. Zero horizontal overflow, and every control in the sheet at 44px.
 */
test.describe('the trim sheet on a phone', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  /**
   * THE MOBILE SHIP GATE, at every width the law names — 320 / 360 / 390 / 430
   * AND zoomed out. The trim control is the first thing this app has shipped
   * that is a DRAG, and a drag target is exactly what a narrow screen and a
   * thumb break. 320 is the real floor (an iPhone SE in landscape-split, and
   * the width at which a two-column row of labels, slider and readout is
   * genuinely tight), so testing 390 alone would have graded the comfortable
   * case.
   */
  const WIDTHS = [320, 360, 390, 430];

  test('opens without overflow and with real tap targets at 320/360/390/430', async ({ page }) => {
    test.setTimeout(240_000);
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await importRamp(page);

    await page.getByRole('button', { name: `Trim ${CLIP_NAME}` }).click();
    const sheet = page.getByRole('dialog', { name: `Trim ${CLIP_NAME}` });
    await expect(sheet).toBeVisible({ timeout: 15_000 });
    await sheet.getByLabel(`Out point for ${CLIP_NAME}`).fill(String(OUT_SEC));
    await sheet.getByLabel(`In point for ${CLIP_NAME}`).fill(String(IN_SEC));

    for (const width of WIDTHS) {
      await page.setViewportSize({ width, height: 844 });
      await page.waitForTimeout(250);
      await expect(sheet, `the sheet must survive a resize to ${width}px`).toBeVisible();

      const overflow = await page.evaluate(() => ({
        sw: document.documentElement.scrollWidth,
        cw: document.documentElement.clientWidth,
      }));
      expect(overflow.sw,
        `the trim sheet widened the page at ${width}px (${overflow.sw} > ${overflow.cw})`)
        .toBeLessThanOrEqual(overflow.cw);

      const small: string[] = [];
      for (const el of await sheet.locator('button, input[type="range"]').all()) {
        const box = await el.boundingBox();
        const name = (await el.getAttribute('aria-label')) || (await el.textContent())?.trim() || '?';
        if (box && (box.height < 44 || box.width < 24)) small.push(`${name} ${box.width}x${box.height}`);
      }
      expect(small, `every control needs a 44px tap target at ${width}px — ${small.join(', ')}`)
        .toEqual([]);

      // The readout must still be READABLE, not merely present: a truncated
      // "3.6s of 6.0s" is a control that stopped telling you what it did.
      await expect(sheet.getByTestId('trim-readout')).toContainText('of 6.0s');
    }

    // ZOOMED OUT — the law names this explicitly, and it is a different failure
    // mode from a narrow viewport: a layout pinned in px stops scaling with the
    // page and pushes past the edge only once the scale factor moves.
    await page.setViewportSize({ width: 390, height: 844 });
    for (const zoom of [0.8, 0.6, 0.5]) {
      await page.evaluate((z) => {
        (document.documentElement.style as CSSStyleDeclaration & { zoom?: string }).zoom = String(z);
      }, zoom);
      await page.waitForTimeout(200);
      const o = await page.evaluate(() => ({
        sw: document.documentElement.scrollWidth,
        cw: document.documentElement.clientWidth,
      }));
      expect(o.sw, `zoomed to ${zoom} the page scrolls sideways (${o.sw} > ${o.cw})`)
        .toBeLessThanOrEqual(o.cw + 1);
    }
    await page.evaluate(() => {
      (document.documentElement.style as CSSStyleDeclaration & { zoom?: string }).zoom = '';
    });
  });
});
