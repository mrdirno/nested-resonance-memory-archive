// tests/e2e/video-audio-export.spec.ts
// -----------------------------------------------------------------------------
// THE EXPORT CARRIES THE SOUND YOU SELECTED — PROVEN BY DECODING THE FILE.
//
// The offline audio mixer has been present and correct for a while, and exports
// were still silent, because `describeAudioSources()` reported each clip's gain
// from `audible` — a fact about the SPEAKERS — instead of from the user's
// intent. `audible` is additionally gated by the global monitor switch (which
// starts false, since browsers only autoplay muted media) and by `live`, the
// REALTIME decoder-admission budget. Neither has any meaning for a file being
// written offline, and either one alone was enough to hand the mixer nothing.
//
// Nothing about that is visible from the outside. The render succeeds, the take
// is smooth, the MP4 opens and plays, the frame count is exactly right, and the
// only thing wrong is that it is quiet. Every existing assertion in this suite
// passed throughout — which is precisely why the proof here has to be
// DECODED AUDIO, not a status pill, a warning string or an element property.
//
// So the fixtures are two clips carrying DIFFERENT PURE TONES — 440 Hz and
// 1200 Hz. After the export, the produced MP4 is decoded back to samples and a
// Goertzel filter measures the energy at each tone. Both must be present:
//   - only 440  => the second clip was dropped (the old exclusive-mute model,
//                  where unmuting one clip muted the other, caps every export
//                  at a single track)
//   - neither   => the mixer got no sources at all (the `audible` bug)
//   - both      => two independently-selected clips genuinely mixed
// A third, unused frequency is measured as a control, so "the file is loud"
// cannot masquerade as "the file contains these tones".
// -----------------------------------------------------------------------------

import { test, expect, type Page } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { demuxAacTrack } from '../../src/lib/mp4AudioDemux';

const HERE = dirname(fileURLToPath(import.meta.url));

const APP_URL = process.env.COLLAGE_BASE_URL || '/';

/**
 * H.264 + AAC, 4s, one pure sine each, small enough that BOTH are admitted as
 * live decoders on any device — so a deferral can never be mistaken for the bug
 * under test.
 *
 * THE CONTAINERS ARE PART OF THE TEST. These were WebM/VP9/Opus, and there was
 * not one .mp4 or .mov anywhere in the project — while the owner imports from a
 * phone. That single fact made the suite structurally incapable of catching the
 * defect it was written for, twice over:
 *
 *   1. WebKit cannot PLAY VP9, so on the only engine that shares a lineage with
 *      iOS the clips never went live and every test died in setup, having
 *      asserted nothing about audio.
 *   2. WebKit's `decodeAudioData` REFUSES a .mov outright (EncodingError) —
 *      measured — which is the failure the owner actually hit. A WebM-only
 *      fixture set cannot express it.
 *
 * So tone_a is .mp4 and tone_b is .mov: the pair covers the plain ISO container
 * AND QuickTime's `mp4a > wave > esds` nesting, which is the shape the
 * hand-rolled demuxer in `mp4AudioDemux.ts` exists to read.
 */
const TONE_A = join(HERE, '..', 'fixtures', 'tone_a.mp4');   // 440 Hz
const TONE_B = join(HERE, '..', 'fixtures', 'tone_b.mov');   // 1200 Hz
const TONE_C = join(HERE, '..', 'fixtures', 'tone_c.mp4');   // 700 Hz
const TONE_D = join(HERE, '..', 'fixtures', 'tone_d.mp4');   // 2000 Hz
const TONE_E = join(HERE, '..', 'fixtures', 'tone_e.mp4');   // 3000 Hz

// No tone is a harmonic of another, so one clip's overtones can never be read
// as a second clip being present.
const HZ_A = 440;
const HZ_B = 1200;
const HZ_C = 700;
const HZ_D = 2000;
const HZ_E = 3000;
/** No clip emits anything here. Measures the noise floor of the same file with
 *  the same window, so every tone assertion is a RATIO — encoder gain, take
 *  length and normalisation cannot flatter it. */
const HZ_CONTROL = 5000;

/**
 * Decode the produced MP4 back to samples in the browser's own decoder and
 * measure the energy at each frequency with a Goertzel filter.
 *
 * Reading the file is the whole point. Every cheaper signal — a status pill,
 * `progress.withAudio`, the absence of a warning, even a muxed-chunk count —
 * was true while the shipped exports were silent.
 */
type ToneReading = {
  ok: boolean; reason: string; bins: number[]; control: number; rms: number; durationSec: number;
};

/**
 * THE INSTRUMENT NEEDS THE SAME FALLBACK THE APP DID.
 *
 * `decodeAudioData` is how this file measures the export — and on WebKit it
 * refuses a multi-track MP4, which is exactly what a finished take IS. So the
 * measurement failed on WebKit with `EncodingError: Decoding failed` while the
 * artifact under test was perfect: an AAC stereo track, verified with ffprobe.
 * A harness that reports the engine's demuxer limits as a product defect grades
 * the wrong thing, and would have sent the next person hunting a bug that is
 * not there.
 *
 * So when the one-call path fails, demux the produced file HERE (in node, with
 * the app's own `mp4AudioDemux`) and decode the elementary stream in-page with
 * WebCodecs — the same ladder `offlineAudio.ts` walks.
 */
const measureTonesFallback = async (
  page: Page, freqs: number[], controlHz: number,
): Promise<ToneReading | null> => {
  const b64 = await page.evaluate(async () => {
    const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
    if (!el || !el.src) return null;
    const u = new Uint8Array(await (await fetch(el.src)).arrayBuffer());
    let s = '';
    for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode(...u.subarray(i, i + 8192));
    return btoa(s);
  });
  if (!b64) return null;

  const bytes = Buffer.from(b64, 'base64');
  const ab = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
  const track = demuxAacTrack(ab);
  if (!track) return null;

  return page.evaluate(async ({ t, freqs, controlHz }) => {
    const W = window as unknown as { AudioDecoder?: typeof AudioDecoder; EncodedAudioChunk?: typeof EncodedAudioChunk };
    if (!W.AudioDecoder || !W.EncodedAudioChunk) return null;
    const blocks: Float32Array[] = [];
    let rate = t.sampleRate;
    const dec = new W.AudioDecoder({
      output: (d: AudioData) => {
        rate = d.sampleRate || rate;
        const o = { planeIndex: 0, format: 'f32-planar' as const };
        const p = new Float32Array(d.allocationSize(o) / 4);
        d.copyTo(p, o);
        blocks.push(p);
        d.close();
      },
      error: () => { /* a dropped frame costs precision, never the run */ },
    });
    dec.configure({
      codec: t.codec, sampleRate: t.sampleRate, numberOfChannels: t.numberOfChannels,
      description: new Uint8Array(t.description),
    });
    for (const s of t.samples) {
      dec.decode(new W.EncodedAudioChunk({
        type: 'key', timestamp: s.timestamp, duration: s.duration, data: new Uint8Array(s.data),
      }));
    }
    await dec.flush();
    dec.close();

    const total = blocks.reduce((a, b) => a + b.length, 0);
    if (!total) return null;
    const all = new Float32Array(total);
    let at = 0;
    for (const b of blocks) { all.set(b, at); at += b.length; }

    const n = Math.min(16384, all.length);
    const start = Math.max(0, Math.floor(all.length / 2) - Math.floor(n / 2));
    const win = all.slice(start, start + n);
    let rms = 0;
    for (let i = 0; i < win.length; i++) rms += win[i] * win[i];
    rms = Math.sqrt(rms / win.length);
    const goertzel = (data: Float32Array, freq: number): number => {
      const N = data.length;
      const k = Math.round((N * freq) / rate);
      const w = (2 * Math.PI * k) / N;
      const cw = Math.cos(w), sw = Math.sin(w), coeff = 2 * cw;
      let s0 = 0, s1 = 0, s2 = 0;
      for (let i = 0; i < N; i++) { s0 = data[i] + coeff * s1 - s2; s2 = s1; s1 = s0; }
      const re = s1 - s2 * cw, im = s2 * sw;
      return Math.sqrt(re * re + im * im) / (N / 2);
    };
    return {
      ok: true,
      reason: 'measured via WebCodecs (this engine cannot decodeAudioData an MP4 with a video track)',
      bins: freqs.map((f) => goertzel(win, f)),
      control: goertzel(win, controlHz),
      rms,
      durationSec: all.length / rate,
    };
  }, {
    t: {
      codec: track.codec,
      sampleRate: track.sampleRate,
      numberOfChannels: track.numberOfChannels,
      description: Array.from(track.description),
      samples: track.samples.map((s) => ({
        data: Array.from(s.data), timestamp: s.timestamp, duration: s.duration,
      })),
    },
    freqs,
    controlHz,
  });
};

const measureTones = async (
  page: Page, freqs: number[], controlHz: number,
): Promise<ToneReading> => {
  const direct = await measureTonesDirect(page, freqs, controlHz);
  if (direct.ok) return direct;
  const viaCodecs = await measureTonesFallback(page, freqs, controlHz);
  return viaCodecs ?? direct;
};

const measureTonesDirect = async (
  page: Page,
  freqs: number[],
  controlHz: number,
): Promise<ToneReading> =>
  page.evaluate(async ({ freqs, controlHz }) => {
    const fail = (reason: string) =>
      ({ ok: false, reason, bins: [] as number[], control: 0, rms: 0, durationSec: 0 });

    // MUST be the RESULT preview. A `video[src^="blob:"]` query returns a
    // source FIXTURE — the Stage mints one hidden element per live clip — and
    // would silently grade the input instead of the output. `controls` is
    // unique to the result element.
    const el = document.querySelector('video[controls]') as HTMLVideoElement | null;
    if (!el || !el.src) return fail('no result preview element');

    const bytes = await (await fetch(el.src)).arrayBuffer();
    const Ctx: typeof AudioContext =
      (window as unknown as { AudioContext: typeof AudioContext }).AudioContext
      || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = new Ctx();
    let buf: AudioBuffer;
    try {
      buf = await ctx.decodeAudioData(bytes.slice(0));
    } catch (e) {
      // The honest failure: an MP4 with no audio track cannot be decoded. This
      // is exactly the shipped bug, and it must read as one.
      await ctx.close().catch(() => {});
      return fail(`no decodable audio track (${(e as Error)?.message || e})`);
    }
    const rate = buf.sampleRate;
    const ch = buf.getChannelData(0);

    /** Energy at one frequency, normalised — a single-bin DFT. */
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

    // A window from the MIDDLE of the take: the head carries encoder priming
    // and the tail can be truncated to the frame count.
    const n = Math.min(16384, ch.length);
    const start = Math.max(0, Math.floor(ch.length / 2) - Math.floor(n / 2));
    const win = ch.slice(start, start + n);

    let rms = 0;
    for (let i = 0; i < win.length; i++) rms += win[i] * win[i];
    rms = Math.sqrt(rms / win.length);

    await ctx.close().catch(() => {});
    return {
      ok: true,
      reason: '',
      bins: freqs.map((f) => goertzel(win, f)),
      control: goertzel(win, controlHz),
      rms,
      durationSec: buf.duration,
    };
  }, { freqs, controlHz });

/** iOS Low Power Mode and desktop autoplay policy both land here: the stage
 *  asks for a tap before it will advance. Give it one if it is asking. */
const startPlaybackIfGated = async (page: Page) => {
  const tap = page.getByRole('button', { name: /tap to play/i });
  if (await tap.count()) await tap.first().click().catch(() => { /* raced with autoplay */ });
};

/**
 * Leave `name`'s sound ON, whatever it was.
 *
 * Written this way ON PURPOSE: these tests are about what the EXPORT contains,
 * and they must not silently re-encode the import default. They were originally
 * written against clips that imported MUTED, so every one of them opened by
 * clicking "Unmute" — and when the default flipped (importing a video is a
 * statement that you want the video, sound included) all three failed at setup
 * with the fix working perfectly underneath. A test that breaks when a default
 * moves was testing the default, not the behaviour.
 *
 * The default itself is asserted ONCE, deliberately, in its own test below.
 */
const ensureClipSoundOn = async (page: Page, name: string) => {
  const off = page.getByRole('button', { name: `Unmute ${name}` });
  if (await off.count()) await off.first().click();
  await expect(page.getByRole('button', { name: `Mute ${name}` }))
    .toBeVisible({ timeout: 10_000 });
};

test.describe('the exported video carries the selected clips’ sound', () => {
  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    // The AI face model is a CDN script the export does not need; blocking it
    // keeps the run off the network and out of a 30s stall.
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
    await page.evaluate(async () => {
      const regs = await navigator.serviceWorker?.getRegistrations?.();
      if (regs?.length) await Promise.all(regs.map((r) => r.unregister()));
      if (typeof caches !== 'undefined') {
        for (const k of await caches.keys()) await caches.delete(k);
      }
    }).catch(() => { /* no SW in this context is fine */ });
  });

  /**
   * THE OWNER'S REPORT, VERBATIM: "make sure audio is saved with the selected
   * videos... it says no audio detected in video but I know for sure there's
   * audio."
   *
   * Import a video. Export. Touch NOTHING else. That is the entire path a
   * person actually walks, and it produced an MP4 with no audio track at all —
   * because a clip imported muted, the monitor started off, and BOTH of those
   * were ANDed into the export's gain. Every other test in this file selects
   * sound explicitly first, so not one of them could see it.
   */
  test('a video imported and exported with NO other interaction keeps its sound', async ({ page }) => {
    test.setTimeout(300_000);

    await page.locator('input[type="file"]').first().setInputFiles([TONE_A]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing tone_a\.mp4/ }))
      .toBeVisible({ timeout: 200_000 });
    await startPlaybackIfGated(page);

    // The default IS the assertion here: sound is part of the piece on import.
    await expect(
      page.getByRole('button', { name: 'Mute tone_a.mp4' }),
      'an imported clip’s sound must start ON — it is the only state the export can honour without a hunt for a switch',
    ).toBeVisible({ timeout: 30_000 });

    await page.getByRole('button', { name: 'Record video' }).click();
    await expect(page.locator('p.tabular-nums').filter({ hasText: /frames/ }))
      .toBeVisible({ timeout: 240_000 });

    const t = await measureTones(page, [HZ_A], HZ_CONTROL);
    expect(t.ok, `the export must contain audio — ${t.reason}`).toBe(true);
    expect(t.rms, 'the audio track must not be digital silence').toBeGreaterThan(0.001);
    expect(t.bins[0], `440 Hz (tone_a) must be present — a=${t.bins[0]} control=${t.control}`)
      .toBeGreaterThan(t.control * 8);
  });

  test('two clips, both unmuted independently, BOTH tones land in the MP4', async ({ page }) => {
    test.setTimeout(300_000);

    await page.locator('input[type="file"]').first().setInputFiles([TONE_A, TONE_B]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing tone_a\.mp4/ }))
      .toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing tone_b\.mov/ }))
      .toBeVisible({ timeout: 200_000 });

    await startPlaybackIfGated(page);

    // ---- INDEPENDENCE ------------------------------------------------------
    // Toggle A OFF and back ON while B is on, and require B to be untouched
    // throughout. Under the old exclusive model this is the assertion that
    // fails first: setting one clip's sound re-muted every other clip behind
    // the user's back, so the two-clip state was unreachable and the export
    // could never contain more than one track.
    await ensureClipSoundOn(page, 'tone_a.mp4');
    await ensureClipSoundOn(page, 'tone_b.mov');

    await page.getByRole('button', { name: 'Mute tone_a.mp4' }).click();
    await expect(page.getByRole('button', { name: 'Unmute tone_a.mp4' }))
      .toBeVisible({ timeout: 10_000 });
    await expect(
      page.getByRole('button', { name: 'Mute tone_b.mov' }),
      'changing one clip’s sound must not change another’s',
    ).toBeVisible();

    await page.getByRole('button', { name: 'Unmute tone_a.mp4' }).click();
    await expect(page.getByRole('button', { name: 'Mute tone_a.mp4' }))
      .toBeVisible({ timeout: 10_000 });
    await expect(
      page.getByRole('button', { name: 'Mute tone_b.mov' }),
      'unmuting the second clip must not silence the first',
    ).toBeVisible();

    // ---- THE TAKE ----------------------------------------------------------
    await page.getByRole('button', { name: 'Record video' }).click();
    const stat = page.locator('p.tabular-nums').filter({ hasText: /frames/ });
    await expect(stat).toBeVisible({ timeout: 240_000 });

    // ---- DECODE THE ARTIFACT ----------------------------------------------
    const t = await measureTones(page, [HZ_A, HZ_B], HZ_CONTROL);
    expect(t.ok, `the export must contain audio — ${t.reason}`).toBe(true);

    // There must be signal at all, before asking what is in it.
    expect(t.rms, 'the audio track must not be digital silence').toBeGreaterThan(0.001);

    // BOTH clips, each well clear of the same file's noise floor at an unused
    // frequency. The ratio is the assertion, so encoder gain cannot flatter it.
    expect(t.bins[0], `440 Hz (tone_a) must be present — a=${t.bins[0]} control=${t.control}`)
      .toBeGreaterThan(t.control * 8);
    expect(t.bins[1], `1200 Hz (tone_b) must be present — b=${t.bins[1]} control=${t.control}`)
      .toBeGreaterThan(t.control * 8);

    console.log(
      `[audio] ${t.durationSec.toFixed(2)}s rms=${t.rms.toFixed(4)} `
      + `440Hz=${t.bins[0].toFixed(5)} 1200Hz=${t.bins[1].toFixed(5)} 5kHz(control)=${t.control.toFixed(5)}`,
    );
  });

  /**
   * MUTING YOUR OWN SPEAKERS IS NOT AN EDIT.
   *
   * `soundOn` is the MONITOR switch. Exports used to read it, so working in
   * silence — the single most ordinary thing to do while composing — produced a
   * silent file, with the selection still lit on every clip chip. Select both
   * clips, mute the preview, export: the file must be unchanged.
   */
  test('muting the PREVIEW does not silence the export', async ({ page }) => {
    test.setTimeout(300_000);

    await page.locator('input[type="file"]').first().setInputFiles([TONE_A, TONE_B]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 200_000 });
    await expect(page.getByRole('button', { name: /Stop playing tone_b\.mov/ }))
      .toBeVisible({ timeout: 200_000 });
    await startPlaybackIfGated(page);

    await ensureClipSoundOn(page, 'tone_a.mp4');
    await ensureClipSoundOn(page, 'tone_b.mov');

    // Turn the monitor ON first — it starts off (importing a video must not
    // make noise), and you cannot test that muting it is harmless until it is
    // unmuted. This step used to happen by accident: the clip-unmute handler
    // also flips `soundOn`, so the old setup left the monitor on as a side
    // effect. With clips already sounding, nothing flips it, and the assertion
    // has to arrange its own precondition instead of inheriting one.
    const monitorOff = page.getByRole('button', { name: 'Unmute preview' });
    if (await monitorOff.count()) await monitorOff.click();
    await expect(page.getByRole('button', { name: 'Mute preview' }))
      .toBeVisible({ timeout: 10_000 });

    // Now silence the monitor. The per-clip selection must NOT change.
    await page.getByRole('button', { name: 'Mute preview' }).click();
    await expect(page.getByRole('button', { name: 'Unmute preview' })).toBeVisible({ timeout: 10_000 });
    await expect(
      page.getByRole('button', { name: 'Mute tone_a.mp4' }),
      'muting the preview must not clear a clip’s sound selection',
    ).toBeVisible();

    await page.getByRole('button', { name: 'Record video' }).click();
    await expect(page.locator('p.tabular-nums').filter({ hasText: /frames/ }))
      .toBeVisible({ timeout: 240_000 });

    const t = await measureTones(page, [HZ_A, HZ_B], HZ_CONTROL);
    expect(t.ok, `the export must contain audio — ${t.reason}`).toBe(true);
    expect(t.bins[0], `440 Hz must survive a muted preview (got ${t.bins[0]})`)
      .toBeGreaterThan(t.control * 8);
    expect(t.bins[1], `1200 Hz must survive a muted preview (got ${t.bins[1]})`)
      .toBeGreaterThan(t.control * 8);
  });
});

/**
 * THE DEFERRED CLIP.
 *
 * `live` is the REALTIME decoder-admission budget: on a phone only three or
 * four clips can hold a decoder at once, and the rest render as stills. That
 * budget used to gate export audio as well, so a clip the device could not
 * also PLAY contributed nothing to the file — even though the offline mixer
 * opens its OWN decoder from the clip's URL and never touches the live element.
 *
 * Five clips against a mobile budget guarantees at least one deferral. Every
 * tone must still be in the file.
 */
test.describe('deferred clips still sound', () => {
  const IPHONE_UA =
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 '
    + '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
  test.use({ userAgent: IPHONE_UA, viewport: { width: 390, height: 844 } });

  test.beforeEach(async ({ page }) => {
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    await page.route('**/cdn.jsdelivr.net/**', (r) => r.abort());
    await page.goto(APP_URL);
  });

  test('every selected clip is in the mix, including the ones showing stills', async ({ page }) => {
    test.setTimeout(400_000);

    await page.locator('input[type="file"]').first()
      .setInputFiles([TONE_A, TONE_B, TONE_C, TONE_D, TONE_E]);
    await expect(page.locator('canvas')).toBeVisible({ timeout: 300_000 });
    const NAMES = ['tone_a.mp4', 'tone_b.mov', 'tone_c.mp4', 'tone_d.mp4', 'tone_e.mp4'];
    for (const n of NAMES) {
      await expect(page.getByRole('button', { name: new RegExp(`Stop playing ${n.replace('.', '\\.')}`) }))
        .toBeVisible({ timeout: 300_000 });
    }
    await startPlaybackIfGated(page);

    // Select all five. Independent switches make this reachable at all.
    for (const n of NAMES) {
      await ensureClipSoundOn(page, n);
    }

    // THE PRECONDITION: the budget must actually be biting, or this test proves
    // nothing. An evicted clip has had its src removed, so counting elements
    // that still hold a decoder is the honest measure.
    // `currentSrc` is NOT the measure here: a deferred clip keeps its src and
    // simply never decodes, so it reads as live. `readyState >= 2` — metadata
    // plus at least one decoded frame — is what actually separates a clip that
    // owns a working decoder from one showing its still.
    const liveDecoders = await page.evaluate(() =>
      Array.from(document.querySelectorAll('video'))
        .filter((v) => v.currentSrc && v.readyState >= 2).length);
    expect(liveDecoders, 'the mobile budget must defer at least one of the five clips')
      .toBeLessThan(5);
    // And the stage must be SAYING so, so the precondition cannot rot silently.
    await expect(page.getByText(/of 5 clips playing/)).toBeVisible({ timeout: 30_000 });

    await page.getByRole('button', { name: 'Record video' }).click();
    await expect(page.locator('p.tabular-nums').filter({ hasText: /frames/ }))
      .toBeVisible({ timeout: 360_000 });

    const t = await measureTones(page, [HZ_A, HZ_B, HZ_C, HZ_D, HZ_E], HZ_CONTROL);
    expect(t.ok, `the export must contain audio — ${t.reason}`).toBe(true);
    const names = ['440 (a)', '1200 (b)', '700 (c)', '2000 (d)', '3000 (e)'];
    t.bins.forEach((v, i) => {
      expect(v, `${names[i]} Hz missing — bins=${JSON.stringify(t.bins)} control=${t.control}`)
        .toBeGreaterThan(t.control * 6);
    });
    console.log(`[audio/deferred] liveDecoders=${liveDecoders}/5 bins=${JSON.stringify(t.bins)} control=${t.control}`);
  });
});
