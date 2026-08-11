// tests/e2e/tone-measure.ts
// -----------------------------------------------------------------------------
// THE INSTRUMENT — decode a produced MP4 back to samples and measure the energy
// at named frequencies with a Goertzel filter.
//
// It lives in its own module because TWO suites now read the same file the same
// way: `video-audio-export.spec.ts` (do the CLIPS you selected land in the mix)
// and `soundtrack.spec.ts` (does the MUSIC). Two copies of one measurement is
// how two suites end up disagreeing about what the same MP4 contains — the same
// reason `clipWindow.sourceTimeAt` exists once rather than three times.
//
// NOT a `.spec.ts`: every config here matches on a spec filename, so this file
// is imported and never collected as a test.
// -----------------------------------------------------------------------------

import { type Page } from '@playwright/test';
import { demuxAacTrack } from '../../src/lib/mp4AudioDemux';

/** No fixture emits anything here. Measures the noise floor of the same file
 *  with the same window, so every tone assertion is a RATIO — encoder gain,
 *  take length and normalisation cannot flatter it. */
export const HZ_CONTROL = 5000;

/**
 * Decode the produced MP4 back to samples in the browser's own decoder and
 * measure the energy at each frequency with a Goertzel filter.
 *
 * Reading the file is the whole point. Every cheaper signal — a status pill,
 * `progress.withAudio`, the absence of a warning, even a muxed-chunk count —
 * was true while the shipped exports were silent.
 */
export type ToneReading = {
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

export const measureTones = async (
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

/**
 * The exported sound's ENVELOPE — energy at one tone, slice by slice, across the
 * whole file.
 *
 * `measureTones` above asks "is this tone anywhere in the file", which is the
 * right question for a trim and the WRONG one for anything with a time axis.
 * The lap defect put exactly the right tone in the file and got only the WHEN
 * wrong; a fade gets neither the tone nor the total energy wrong and changes
 * only the SHAPE. Neither is visible to a measurement without a clock.
 *
 * MOVED HERE FROM `trim.spec.ts` ON ITS SECOND CALLER (`fade.spec.ts`), which
 * is the house rule: two suites reading the same file the same way is how two
 * suites end up disagreeing about what one MP4 contains. The implementation is
 * that file's, verbatim — including the fact that it decodes in ONE call and
 * therefore, unlike `measureTones`, has no WebKit demuxer fallback. Both
 * callers are chromium-only configs today; the day one is not, this is the
 * function that needs the ladder.
 */
export type ToneEnvelope = {
  ok: boolean; reason: string; dur: number; slices: { t: number; e: number; rms: number }[];
};

export const toneEnvelope = async (
  page: Page, hz: number, sliceSec: number,
): Promise<ToneEnvelope> =>
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
