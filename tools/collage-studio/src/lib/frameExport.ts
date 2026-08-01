// src/lib/frameExport.ts
// -----------------------------------------------------------------------------
// THE iPHONE PATH — record the collage WITHOUT MediaRecorder or captureStream.
//
// WHY THIS EXISTS
//   `videoExport.ts` records by pointing MediaRecorder at `canvas.captureStream()`.
//   That is the right tool where it works: it is realtime, it carries audio for
//   free, and it is one API call. On iOS Safari it is also the exact pair of
//   APIs with the worst history in the whole platform — caniuse marks canvas
//   capture unsupported on iOS at every version, MDN's "supported" is an
//   INFERRED mirror value rather than a tested one, and WebKit's own bug list
//   (229611 blank video, 181663 freeze-on-stop, iOS 15 `onstop`/`ondataavailable`
//   never firing) says "sometimes" even where it is present. `videoExport`
//   already refuses to guess and runs a dry-run take to let the device answer;
//   this module is what we do when that answer is NO.
//
// THE APPROACH
//   WebCodecs. We hand `VideoEncoder` each frame ourselves and mux the H.264 it
//   returns into an MP4 in memory. Neither flaky API is involved: no stream is
//   captured, no recorder is constructed. VideoEncoder shipped in Safari 17 and
//   is the same encoder the system uses, so the output is a normal MP4 that
//   opens in QuickTime and imports to Photos.
//
//   It is also, on its own merits, the better recorder: nothing is dropped under
//   load, the duration is exact rather than wall-clock, and the file carries real
//   timing metadata instead of the header-less fragmented stream every browser
//   MediaRecorder emits.
//
// SOUND
//   `recordFrames` is silent, and says so: `audio.recorded` is false and a
//   warning names it. It never pretends.
//
//   `renderOffline` CARRIES SOUND. It cannot capture any — nothing is playing,
//   it seeks decoders — so it MAKES some: `offlineAudio.ts` decodes each clip,
//   mixes it on an OfflineAudioContext along the same timeline the frame loop
//   walks, encodes AAC-LC, and the chunks are muxed into this same MP4. The
//   ladder is AAC or silence with no Opus rung, because an Opus-in-MP4 file
//   will not open in QuickTime or Photos and a file that does not open is worse
//   than one that is quiet. Every failure rung degrades to a silent, valid
//   video and reports its own reason.
//
// CONTRACT
//   Deliberately identical to `videoExport.record()` — same `RecordResult` union,
//   same progress shape, same never-throws rule — so the caller picks a strategy
//   and nothing downstream has to care which one ran.
// -----------------------------------------------------------------------------

import { Muxer, ArrayBufferTarget } from 'mp4-muxer';
import {
  prepareOfflineAudio, truncateAudio,
  type OfflineAudioSource, type OfflineAudioTrack,
} from './offlineAudio';
import {
  describeContainer, suggestFilename, getRecordingProfile,
  type RecordResult, type RecordFailure, type RecordProgress,
  type RecordPhase, type RecordingProfile,
} from './videoExport';

// =============================================================================
// TYPES
// =============================================================================

export interface FrameExportSupport {
  supported: boolean;
  apis: { videoEncoder: boolean; videoFrame: boolean };
  /** Null until `probeFrameExportSupport` has actually asked the encoder. */
  configSupported: boolean | null;
  reason: string | null;
  advice: string | null;
  label: string;
}

export interface FrameRecordOptions {
  seconds?: number;
  fps?: number;
  /** Bits per second for the video track. Defaults to the device profile. */
  videoBitsPerSecond?: number;
  signal?: AbortSignal;
  onProgress?: (p: RecordProgress) => void;
  filenameBase?: string;
  /** Auto-stop if the muxed buffer passes this. Defaults to the device profile. */
  maxBytes?: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * H.264 CODEC STRING, DERIVED FROM THE FRAME — never a constant.
 *
 * Baseline profile (`4200`) is deliberate: it is the one profile every Apple
 * device back to the iPhone 4 decodes in hardware, so the file plays on the
 * phone that made it. The LEVEL, though, cannot be fixed. A level caps the frame
 * in MACROBLOCKS, and the collage is whatever shape the user chose — a 2:3
 * portrait at the desktop capture width is 1080x1622, which is 6,936 macroblocks
 * against level 3.1's ceiling of 3,600.
 *
 * Hardcoding 3.1 was exactly that bug: `isConfigSupported` answered a flat "this
 * device cannot encode H.264 at that size", which reads like a device limitation
 * and is really a string we chose. So compute the macroblocks, take every level
 * that fits, and let the encoder pick the first one it will actually accept.
 *
 * level_idc is level x 10, in hex — 3.1 -> 31 -> 0x1f, 4.0 -> 40 -> 0x28.
 */
const H264_LEVELS: ReadonlyArray<{ idc: number; maxMbs: number }> = [
  { idc: 31, maxMbs: 3600 },    // 3.1  — 1280x720
  { idc: 32, maxMbs: 5120 },    // 3.2
  { idc: 40, maxMbs: 8192 },    // 4.0  — 2048x1024
  { idc: 41, maxMbs: 8192 },    // 4.1
  { idc: 42, maxMbs: 8704 },    // 4.2
  { idc: 50, maxMbs: 22080 },   // 5.0
  { idc: 51, maxMbs: 36864 },   // 5.1  — 4096x2304
  { idc: 52, maxMbs: 36864 },   // 5.2
];

const codecsFor = (width: number, height: number): string[] => {
  const mbs = Math.ceil(width / 16) * Math.ceil(height / 16);
  const fits = H264_LEVELS.filter((l) => l.maxMbs >= mbs);
  // Highest level last as a longshot: some encoders under-report and accept it.
  const ladder = fits.length ? fits : [H264_LEVELS[H264_LEVELS.length - 1]];
  return ladder.map((l) => `avc1.4200${l.idc.toString(16).padStart(2, '0')}`);
};

/** Keyframe cadence. Two seconds is the usual seekability/size compromise. */
const KEYFRAME_EVERY_SEC = 2;

/**
 * Encoder backpressure ceiling. `encode()` is fire-and-forget, so a slow device
 * will happily let the queue grow until it dies. Past this we DROP the frame
 * rather than the tab — a recording that skips a frame is a recording; one that
 * runs the phone out of memory is a crash report.
 */
const MAX_QUEUE = 8;

const PROGRESS_TICK_MS = 200;
const FLUSH_TIMEOUT_MS = 15_000;

const nowMs = (): number =>
  typeof performance !== 'undefined' && typeof performance.now === 'function'
    ? performance.now()
    : Date.now();

const errText = (e: unknown): string => {
  if (!e) return 'Unknown error';
  if (e instanceof Error) return e.name ? `${e.name}: ${e.message}` : e.message;
  if (typeof e === 'string') return e;
  try { return String(e); } catch { return 'Unknown error'; }
};

const clamp = (v: number, lo: number, hi: number): number => Math.min(hi, Math.max(lo, v));

/** Encoders reject odd dimensions; H.264 in particular wants even ones. */
const even = (n: number): number => Math.max(2, Math.floor(n / 2) * 2);

type EncoderCtor = typeof VideoEncoder;
type FrameCtor = typeof VideoFrame;

const encoderCtor = (): EncoderCtor | null =>
  typeof window !== 'undefined' && typeof (window as unknown as { VideoEncoder?: EncoderCtor }).VideoEncoder === 'function'
    ? (window as unknown as { VideoEncoder: EncoderCtor }).VideoEncoder
    : null;

const frameCtor = (): FrameCtor | null =>
  typeof window !== 'undefined' && typeof (window as unknown as { VideoFrame?: FrameCtor }).VideoFrame === 'function'
    ? (window as unknown as { VideoFrame: FrameCtor }).VideoFrame
    : null;

// =============================================================================
// CAPABILITY
// =============================================================================

/** First codec string on the ladder this encoder actually admits to, or null. */
const pickCodec = async (
  Enc: EncoderCtor, width: number, height: number, bitrate: number, framerate: number,
): Promise<string | null> => {
  for (const codec of codecsFor(width, height)) {
    try {
      const res = await Enc.isConfigSupported({ codec, width, height, bitrate, framerate });
      if (res.supported) return codec;
    } catch { /* a malformed string is a no, not a crash */ }
  }
  return null;
};

/** SYNCHRONOUS, no side effects. `configSupported` stays null until probed. */
export const inspectFrameExportSupport = (): FrameExportSupport => {
  const apis = { videoEncoder: !!encoderCtor(), videoFrame: !!frameCtor() };
  const present = apis.videoEncoder && apis.videoFrame;
  return {
    supported: present,
    apis,
    configSupported: null,
    reason: present ? null : 'This browser has no WebCodecs video encoder.',
    advice: present ? null : 'Export a still instead, or open the studio in a newer browser.',
    label: present ? 'MP4 — H.264, no sound' : 'Video recording unavailable',
  };
};

let probeCache: FrameExportSupport | null = null;

/**
 * Ask the ENCODER, not a version table. `isConfigSupported` is cheap (it does
 * not allocate an encoder) and it is the only authority on whether this exact
 * codec/size will actually encode here.
 */
export const probeFrameExportSupport = async (
  size?: { width: number; height: number },
): Promise<FrameExportSupport> => {
  const base = inspectFrameExportSupport();
  if (!base.supported) return base;
  if (probeCache && !size) return probeCache;

  const Enc = encoderCtor();
  if (!Enc) return base;
  const width = even(size?.width ?? 1280);
  const height = even(size?.height ?? 720);
  try {
    const ok = !!(await pickCodec(Enc, width, height, 4_000_000, 30));
    const out: FrameExportSupport = {
      ...base,
      supported: ok,
      configSupported: ok,
      reason: ok ? null : `This device cannot encode H.264 at ${width}x${height}.`,
      advice: ok ? null : 'Export a still instead.',
      label: ok ? 'MP4 — H.264, no sound' : 'Video recording unavailable',
    };
    if (!size) probeCache = out;
    return out;
  } catch (e) {
    return { ...base, supported: false, configSupported: false, reason: errText(e), advice: base.advice };
  }
};

// =============================================================================
// RECORD
// =============================================================================

const failure = (
  code: RecordFailure['code'],
  message: string,
  advice: string | null,
  cause: string | null,
  warnings: string[],
): RecordFailure => ({ ok: false, code, message, advice, cause, partial: null, warnings });

/**
 * Record `canvas` for up to `seconds` by encoding its frames directly.
 *
 * NEVER THROWS — every outcome is a typed `RecordResult`, exactly as
 * `videoExport.record()`.
 *
 * THE CALLER MUST KEEP DRAWING, same as the MediaRecorder path: we sample the
 * canvas on a rAF cadence, so a canvas nobody repaints yields N copies of one
 * frame. `Stage.setCaptureActive(true)` is what guarantees that.
 */
export const recordFrames = async (
  canvas: HTMLCanvasElement,
  options: FrameRecordOptions = {},
): Promise<RecordResult> => {
  const warnings: string[] = [];
  const profile: RecordingProfile = getRecordingProfile();
  const onProgress = options.onProgress;

  let phase: RecordPhase = 'preparing';
  let bytes = 0;
  let frames = 0;
  let startedAt = 0;

  const fps = Math.round(clamp(options.fps ?? profile.fps, 1, 60));
  const seconds = clamp(options.seconds ?? profile.maxSeconds, 1, profile.maxSeconds);
  const totalMs = Math.round(seconds * 1000);
  const capped = seconds < (options.seconds ?? seconds);
  const maxBytes = options.maxBytes ?? profile.maxBytes;

  const emit = (label: string, ratioOverride?: number) => {
    if (!onProgress) return;
    const elapsed = startedAt ? nowMs() - startedAt : 0;
    const ratio = ratioOverride !== undefined
      ? clamp(ratioOverride, 0, 1)
      : totalMs > 0 ? clamp(elapsed / totalMs, 0, 1) : 0;
    try {
      onProgress({
        phase, ratio,
        elapsedMs: Math.round(elapsed),
        remainingMs: Math.max(0, Math.round(totalMs - elapsed)),
        bytes, chunks: frames, label, fps, withAudio: false,
      });
    } catch { /* a UI callback must never break a take */ }
  };

  try {
    if (!canvas || typeof canvas.getContext !== 'function' || !canvas.width || !canvas.height) {
      return failure('bad-canvas', 'There is nothing to record yet.',
        'Add some images or clips, then try again.', `size ${canvas?.width}x${canvas?.height}`, warnings);
    }

    const Enc = encoderCtor();
    const Frame = frameCtor();
    if (!Enc || !Frame) {
      return failure('unsupported', "This browser can't encode video.",
        'Export a still instead.', 'no WebCodecs', warnings);
    }

    // Encode at the canvas's own backing size, forced even. Stage freezes this
    // for the whole take via setCaptureActive, so it cannot change under us —
    // which matters, because a mid-stream resolution change is exactly what
    // corrupts an H.264 stream.
    const width = even(canvas.width);
    const height = even(canvas.height);

    phase = 'probing';
    emit('Checking this device…', 0);
    const support = await probeFrameExportSupport({ width, height });
    if (!support.supported) {
      phase = 'failed';
      emit('Not supported', 0);
      return failure('unsupported', "This device can't encode video.",
        support.advice, support.reason, warnings);
    }

    if (options.signal?.aborted) {
      return failure('aborted', 'Recording cancelled.', null, null, warnings);
    }

    phase = 'arming';
    emit('Getting ready…', 0);

    const bitrate = options.videoBitsPerSecond ?? profile.videoBitsPerSecond;
    const codec = await pickCodec(Enc, width, height, bitrate, fps);
    if (!codec) {
      phase = 'failed';
      emit('Not supported', 0);
      return failure('unsupported', "This device can't encode video at that size.",
        'Try a smaller aspect, or export a still.', `no H.264 level accepted ${width}x${height}`, warnings);
    }

    const muxer = new Muxer({
      target: new ArrayBufferTarget(),
      video: { codec: 'avc', width, height },
      // The whole file is assembled in memory and the index written at the
      // front, so the result is a normal, seekable MP4 rather than the
      // header-less fragmented stream a browser recorder emits.
      fastStart: 'in-memory',
      // MANDATORY HERE. The default 'strict' requires the first chunk to carry
      // timestamp 0, and ours cannot: the first frame is sampled on the first
      // animation frame after the take starts, which is ~10ms in. Under 'strict'
      // every addVideoChunk threw, no decoderConfig was ever stored, and the
      // failure only surfaced at finalize() as a null-property TypeError with
      // nothing pointing at the cause. 'offset' rebases the track on its own
      // first timestamp, which is exactly the intent.
      firstTimestampBehavior: 'offset',
    });

    let encoderError: string | null = null;
    /**
     * Nominal frame duration, in microseconds. Needed because `duration` on an
     * EncodedVideoChunk is OPTIONAL and WebKit does not set it — the muxer then
     * rejects the chunk with "duration must be a non-negative real number",
     * which surfaces far from the cause. Chromium does set it, so this only
     * ever bites on the platform the whole module exists to serve.
     */
    const nominalDurationUs = Math.max(1, Math.round(1_000_000 / fps));

    const encoder = new Enc({
      output: (chunk, meta) => {
        try {
          if (chunk.duration == null) {
            // No duration on the chunk: hand the muxer the raw bytes and supply
            // one. `addVideoChunk` has no duration override, `addVideoChunkRaw` does.
            const data = new Uint8Array(chunk.byteLength);
            chunk.copyTo(data);
            muxer.addVideoChunkRaw(data, chunk.type, chunk.timestamp, nominalDurationUs, meta);
          } else {
            muxer.addVideoChunk(chunk, meta);
          }
          bytes += chunk.byteLength;
        } catch (e) {
          encoderError = encoderError ?? errText(e);
        }
      },
      error: (e: DOMException) => { encoderError = encoderError ?? errText(e); },
    });

    try {
      encoder.configure({
        codec, width, height,
        bitrate,
        framerate: fps,
        // Annex-B would need converting before muxing; 'avc' is what mp4 wants.
        avc: { format: 'avc' },
      });
    } catch (e) {
      return failure('start-failed', "This browser wouldn't start encoding.",
        'Export a still instead.', errText(e), warnings);
    }

    // ---- the take ---------------------------------------------------------
    phase = 'recording';
    startedAt = nowMs();
    emit('Recording…', 0);

    const frameInterval = 1000 / fps;
    const keyEvery = Math.max(1, Math.round(fps * KEYFRAME_EVERY_SEC));
    let nextFrameAt = startedAt;
    let dropped = 0;
    // Held on an object, not in a `let`: the assignments happen inside the rAF
    // closure, so control-flow analysis would otherwise narrow the variable to
    // its initializer and call every later comparison unreachable.
    const run: { stop: 'complete' | 'aborted' | 'memory' | 'error' } = { stop: 'complete' };

    const ticker = setInterval(() => { if (phase === 'recording') emit('Recording…'); }, PROGRESS_TICK_MS);

    await new Promise<void>((resolve) => {
      let raf = 0;
      let finished = false;
      const finish = (why: typeof run.stop) => {
        if (finished) return;
        finished = true;
        run.stop = why;
        if (raf) cancelAnimationFrame(raf);
        if (options.signal) options.signal.removeEventListener('abort', onAbort);
        resolve();
      };
      const onAbort = () => finish('aborted');
      if (options.signal) options.signal.addEventListener('abort', onAbort, { once: true });

      const step = () => {
        raf = 0;
        if (finished) return;
        const t = nowMs();
        const elapsed = t - startedAt;

        if (encoderError) return finish('error');
        if (bytes >= maxBytes) return finish('memory');
        if (elapsed >= totalMs) return finish('complete');

        if (t >= nextFrameAt) {
          // Pace to the requested fps rather than the display's refresh rate: a
          // 120 Hz panel would otherwise encode 4x the frames for no gain.
          nextFrameAt = Math.max(t, nextFrameAt + frameInterval);
          if (encoder.encodeQueueSize > MAX_QUEUE) {
            dropped++;                       // backpressure — see MAX_QUEUE
          } else {
            try {
              const vf = new Frame(canvas, { timestamp: Math.round(elapsed * 1000) });
              encoder.encode(vf, { keyFrame: frames % keyEvery === 0 });
              vf.close();                    // MUST close, or the pool starves
              frames++;
            } catch (e) {
              encoderError = encoderError ?? errText(e);
              return finish('error');
            }
          }
        }
        raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    });

    clearInterval(ticker);
    const durationMs = Math.max(0, Math.round(nowMs() - startedAt));

    phase = 'finalizing';
    emit('Finishing…', 1);

    if (run.stop === 'aborted') {
      try { encoder.close(); } catch { /* ignore */ }
      phase = 'cancelled';
      emit('Cancelled', 1);
      return failure('aborted', 'Recording cancelled.', null, null, warnings);
    }

    // Flush is deadlined for the same reason every wait in videoExport is: an
    // encoder that wedges must cost a bounded amount of time, not the session.
    let flushed = true;
    try {
      await Promise.race([
        encoder.flush(),
        new Promise<void>((_, rej) => setTimeout(() => rej(new Error('flush timed out')), FLUSH_TIMEOUT_MS)),
      ]);
    } catch (e) {
      flushed = false;
      warnings.push('The encoder did not finish cleanly; the file may be a little short.');
      encoderError = encoderError ?? errText(e);
    }
    try { encoder.close(); } catch { /* ignore */ }

    if (frames === 0) {
      return failure('empty', 'The recording came out empty.',
        'Keep the collage visible while it records.',
        encoderError ?? 'no frames encoded', warnings);
    }

    // Muxing errors were being collected and then ignored — finalize would fail
    // later with a message about a null property instead of the real reason.
    if (encoderError && bytes === 0) {
      return failure('internal', 'The video could not be encoded.',
        'Try a shorter recording, or export a still.', encoderError, warnings);
    }

    try { muxer.finalize(); } catch (e) {
      return failure('internal', 'The video file could not be assembled.',
        'Try a shorter recording.', errText(e), warnings);
    }

    const buffer = (muxer.target as ArrayBufferTarget).buffer;
    if (!buffer || buffer.byteLength === 0) {
      return failure('empty', 'The recording came out empty.',
        'Try a shorter recording.', encoderError ?? 'empty muxer output', warnings);
    }

    const blob = new Blob([buffer], { type: 'video/mp4' });

    if (run.stop === 'memory') {
      warnings.push('Recording stopped early to stay inside this device’s memory budget.');
    }
    if (dropped > 0) {
      warnings.push(`${dropped} frame${dropped === 1 ? '' : 's'} dropped to keep up — the motion may stutter slightly.`);
    }
    if (capped) {
      warnings.push(`Recording is capped at ${profile.maxSeconds}s on this device.`);
    }
    warnings.push('Recorded without sound — this device needs the frame-by-frame encoder, which cannot capture audio.');

    phase = 'done';
    emit('Done', 1);

    const mimeType = 'video/mp4';
    return {
      ok: true,
      blob,
      url: URL.createObjectURL(blob),
      filename: suggestFilename(options.filenameBase ?? 'collage', mimeType),
      container: describeContainer(mimeType),
      mimeType,
      durationMs,
      sizeBytes: blob.size,
      chunks: frames,
      fps,
      audio: { requested: false, recorded: false, tracks: 0, sources: 0, monitorConnected: false },
      // The bytes came back through the muxer and the index is written, which is
      // a stronger statement than the MediaRecorder path's decode-check can make
      // about a fragmented stream — but it is still not a playback proof, so it
      // is reported honestly rather than as 'pass'.
      validated: flushed ? 'unverified' : 'skipped',
      capped,
      warnings,
    };
  } catch (e) {
    phase = 'failed';
    emit('Failed', 1);
    return failure('internal', 'Something went wrong while recording.',
      'Export a still instead.', errText(e), warnings);
  }
};

// =============================================================================
// OFFLINE RENDER — the one path that cannot be choppy
// =============================================================================

/**
 * Anything that can be stepped to an exact time and drawn. `Stage` implements
 * it; the type is structural so a test can drive the encoder with a fake.
 */
export interface OfflineRenderSource {
  readonly canvas: HTMLCanvasElement;
  beginOfflineRender(): void;
  endOfflineRender(): void;
  renderAtTime(timeSec: number, opts?: { signal?: AbortSignal }): Promise<void>;
  /** The clips' sound, for the offline mixer. OPTIONAL so every existing
   *  structural implementer — and every test fake — stays valid; its absence is
   *  a legitimate silent render, honestly reported. */
  describeAudioSources?(): OfflineAudioSource[];
}

export interface OfflineRenderOptions extends FrameRecordOptions {
  /** Where on the clips' timeline the take starts. Defaults to 0. */
  startTimeSec?: number;
  /** Mix the clips' sound into the file. Default true. `false` is an explicit
   *  opt-out and reports `requested: false` rather than a failure. */
  audio?: boolean;
  audioBitsPerSecond?: number;
}

/**
 * RENDER the collage to MP4, frame by frame, with no clock anywhere.
 *
 * THE DIFFERENCE FROM `recordFrames`, WHICH IS THE WHOLE POINT.
 *   `recordFrames` samples a canvas that is playing in real time: it schedules
 *   on rAF, snaps `nextFrameAt` forward when it falls behind, drops frames
 *   under encoder backpressure, and stamps each frame with WALL-CLOCK elapsed
 *   time. Every one of those is a way for a stall to become permanent judder in
 *   the file. Re-recording cannot fix it, because the stall is the recording.
 *
 *   This renders instead. Frame n is defined as "the composition at t = n/fps":
 *   every clip is SEEKED there, the frame is drawn, and it is stamped
 *   `n * 1e6/fps` — from the INDEX, never the clock. Backpressure is WAITED on
 *   rather than dropped. A frame that takes 300ms to assemble is still exactly
 *   one frame-interval long in the output. The result is mathematically even
 *   motion on any device, at the cost of taking longer than realtime to
 *   produce — which is the correct trade for an artifact you keep.
 *
 * NEVER THROWS — same typed `RecordResult` as every other path here.
 *
 * CARRIES SOUND, and this comment used to say the opposite. `renderOffline`
 * shipped silent, then gained a mixer (`prepareOfflineAudio`, called below) —
 * and the "SILENT" note stayed, alongside a "(silent)" button tooltip in
 * VideoStage. Two pieces of documentation kept asserting a limitation the code
 * had already removed, which is how a genuinely broken export read as intended
 * behaviour for as long as it did. No audio graph is involved (there is no
 * clock to tap); the audio is DECODED AND MIXED independently, and every path
 * that ends up without it says which rung failed.
 */
export const renderOffline = async (
  source: OfflineRenderSource,
  options: OfflineRenderOptions = {},
): Promise<RecordResult> => {
  const warnings: string[] = [];
  const profile: RecordingProfile = getRecordingProfile();
  const onProgress = options.onProgress;
  const canvas = source?.canvas;

  let phase: RecordPhase = 'preparing';
  let bytes = 0;
  let frames = 0;
  let startedAt = 0;

  const fps = Math.round(clamp(options.fps ?? profile.fps, 1, 60));
  const seconds = clamp(options.seconds ?? profile.maxSeconds, 1, profile.maxSeconds);
  const capped = seconds < (options.seconds ?? seconds);
  const maxBytes = options.maxBytes ?? profile.maxBytes;
  const totalFrames = Math.max(1, Math.round(seconds * fps));
  const startAt = Math.max(0, options.startTimeSec ?? 0);
  /** Exact, integral frame duration in microseconds — the timeline's only unit. */
  const frameDurUs = Math.max(1, Math.round(1_000_000 / fps));

  const wantsAudio = options.audio !== false;
  let audioTrack: OfflineAudioTrack | null = null;
  let audioReason: string | null = null;
  let audioMuxed = 0;

  const emit = (label: string, ratio: number) => {
    if (!onProgress) return;
    const elapsed = startedAt ? nowMs() - startedAt : 0;
    try {
      onProgress({
        phase,
        ratio: clamp(ratio, 0, 1),
        // The honest numbers for a render are about the OUTPUT, not the wall
        // clock: "how much of the video exists" and "how much longer at the
        // rate we are actually managing".
        elapsedMs: Math.round(elapsed),
        remainingMs: frames > 0
          ? Math.max(0, Math.round((elapsed / frames) * (totalFrames - frames)))
          : 0,
        bytes,
        chunks: frames,
        label,
        fps,
        withAudio: !!audioTrack,
      });
    } catch { /* a UI callback must never break a take */ }
  };

  let started = false;
  try {
    if (!source || typeof source.renderAtTime !== 'function') {
      return failure('internal', 'There is nothing to render.', null, 'no offline source', warnings);
    }
    if (!canvas || typeof canvas.getContext !== 'function') {
      return failure('bad-canvas', 'There is nothing to render yet.',
        'Add some images or clips, then try again.', 'no canvas', warnings);
    }

    const Enc = encoderCtor();
    const Frame = frameCtor();
    if (!Enc || !Frame) {
      return failure('unsupported', "This browser can't encode video.",
        'Export a still instead.', 'no WebCodecs', warnings);
    }

    // Park the stage BEFORE measuring: setCaptureActive freezes the backing
    // size, and the encoder must be configured for the size it will actually
    // receive for every single frame.
    source.beginOfflineRender();
    started = true;

    const width = even(canvas.width);
    const height = even(canvas.height);
    if (!width || !height) {
      return failure('bad-canvas', 'There is nothing to render yet.',
        'Add some images or clips, then try again.', `size ${canvas.width}x${canvas.height}`, warnings);
    }

    phase = 'probing';
    emit('Checking this device…', 0);
    const support = await probeFrameExportSupport({ width, height });
    if (!support.supported) {
      phase = 'failed';
      emit('Not supported', 0);
      return failure('unsupported', "This device can't encode video.",
        support.advice, support.reason, warnings);
    }
    if (options.signal?.aborted) {
      return failure('aborted', 'Render cancelled.', null, null, warnings);
    }

    phase = 'arming';
    emit('Getting ready…', 0);

    const bitrate = options.videoBitsPerSecond ?? profile.videoBitsPerSecond;
    const codec = await pickCodec(Enc, width, height, bitrate, fps);
    if (!codec) {
      phase = 'failed';
      emit('Not supported', 0);
      return failure('unsupported', "This device can't encode video at that size.",
        'Try a smaller aspect, or export a still.', `no H.264 level accepted ${width}x${height}`, warnings);
    }

    // ---- sound ------------------------------------------------------------
    // Runs HERE: after the video encoder is known to work, before the Muxer is
    // constructed (the track must be declared at construction), and before the
    // frame loop starts. It therefore cannot stall the loop — which is the one
    // property this whole module exists to protect. It costs a second or two of
    // "Mixing sound…" up front, the correct trade for a render that is already
    // slower than realtime by design.
    if (wantsAudio) {
      if (typeof source.describeAudioSources !== 'function') {
        audioReason = 'This view cannot supply the clips’ sound.';
      } else {
        emit('Mixing sound…', 0);
        try {
          const prepared = await prepareOfflineAudio(source.describeAudioSources(), {
            startAt,
            seconds,
            signal: options.signal,
            bitrate: options.audioBitsPerSecond ?? profile.audioBitsPerSecond,
          });
          audioTrack = prepared.track;
          audioReason = prepared.reason;
          if (prepared.track?.warnings.length) warnings.push(...prepared.track.warnings);
        } catch (e) {
          // A thrown mixer must never cost the video. Silent, and say why.
          audioTrack = null;
          audioReason = `Sound could not be prepared (${errText(e)}).`;
        }
      }
      if (options.signal?.aborted) {
        return failure('aborted', 'Render cancelled.', null, null, warnings);
      }
    }

    const muxer = new Muxer({
      target: new ArrayBufferTarget(),
      video: { codec: 'avc', width, height },
      // Declared only when chunks genuinely exist. `MuxerOptions.audio` is
      // optional, so one construction site covers both cases — and encoding
      // BEFORE this point is what guarantees a declared track is never empty.
      audio: audioTrack
        ? {
            codec: audioTrack.codec,
            numberOfChannels: audioTrack.numberOfChannels,
            sampleRate: audioTrack.sampleRate,
          }
        : undefined,
      fastStart: 'in-memory',
      // Unlike the realtime path this track genuinely DOES start at timestamp 0
      // — the first frame is index 0 by construction — but 'offset' is a no-op
      // in that case and keeps the two paths behaving identically.
      firstTimestampBehavior: 'offset',
    });

    let encoderError: string | null = null;
    const encoder = new Enc({
      output: (chunk, meta) => {
        try {
          if (chunk.duration == null) {
            const data = new Uint8Array(chunk.byteLength);
            chunk.copyTo(data);
            muxer.addVideoChunkRaw(data, chunk.type, chunk.timestamp, frameDurUs, meta);
          } else {
            muxer.addVideoChunk(chunk, meta);
          }
          bytes += chunk.byteLength;
        } catch (e) {
          encoderError = encoderError ?? errText(e);
        }
      },
      error: (e: DOMException) => { encoderError = encoderError ?? errText(e); },
    });

    try {
      encoder.configure({ codec, width, height, bitrate, framerate: fps, avc: { format: 'avc' } });
    } catch (e) {
      return failure('start-failed', "This browser wouldn't start encoding.",
        'Export a still instead.', errText(e), warnings);
    }

    // ---- the render -------------------------------------------------------
    phase = 'recording';
    startedAt = nowMs();
    emit('Rendering…', 0);

    const keyEvery = Math.max(1, Math.round(fps * KEYFRAME_EVERY_SEC));
    let stop: 'complete' | 'aborted' | 'memory' | 'error' = 'complete';

    for (let n = 0; n < totalFrames; n++) {
      if (options.signal?.aborted) { stop = 'aborted'; break; }
      if (encoderError) { stop = 'error'; break; }
      if (bytes >= maxBytes) { stop = 'memory'; break; }

      // WAIT for the encoder, never drop. Dropping is what the realtime path
      // does and it is exactly the defect this function exists to remove: the
      // output timeline is defined by n, so a slow encoder makes the render
      // take longer and changes NOTHING about the file.
      let guard = 0;
      while (encoder.encodeQueueSize > MAX_QUEUE && !options.signal?.aborted && !encoderError) {
        await new Promise<void>((r) => setTimeout(r, 4));
        if (++guard > 5_000) break;      // ~20s: a wedged encoder is an error, not a wait
      }
      if (encoderError) { stop = 'error'; break; }
      if (options.signal?.aborted) { stop = 'aborted'; break; }

      await source.renderAtTime(startAt + n / fps, { signal: options.signal });
      if (options.signal?.aborted) { stop = 'aborted'; break; }

      try {
        const vf = new Frame(canvas, {
          timestamp: n * frameDurUs,     // FROM THE INDEX. Never the clock.
          duration: frameDurUs,
        });
        encoder.encode(vf, { keyFrame: n % keyEvery === 0 });
        vf.close();                      // MUST close, or the pool starves
        frames++;
      } catch (e) {
        encoderError = encoderError ?? errText(e);
        stop = 'error';
        break;
      }

      if ((n & 3) === 0 || n === totalFrames - 1) {
        emit(`Rendering frame ${n + 1} of ${totalFrames}…`, (n + 1) / totalFrames);
      }
    }

    // Duration is EXACT — it is a frame count times a frame interval, not a
    // measurement of how long the machine took to get there.
    const durationMs = Math.round((frames * frameDurUs) / 1000);

    phase = 'finalizing';
    emit('Finishing…', 1);

    if (stop === 'aborted') {
      try { encoder.close(); } catch { /* ignore */ }
      phase = 'cancelled';
      emit('Cancelled', 1);
      return failure('aborted', 'Render cancelled.', null, null, warnings);
    }

    let flushed = true;
    try {
      await Promise.race([
        encoder.flush(),
        new Promise<void>((_, rej) => setTimeout(() => rej(new Error('flush timed out')), FLUSH_TIMEOUT_MS)),
      ]);
    } catch (e) {
      flushed = false;
      warnings.push('The encoder did not finish cleanly; the file may be a little short.');
      encoderError = encoderError ?? errText(e);
    }
    try { encoder.close(); } catch { /* ignore */ }

    if (frames === 0) {
      return failure('empty', 'The render came out empty.',
        'Add some images or clips, then try again.',
        encoderError ?? 'no frames encoded', warnings);
    }
    if (encoderError && bytes === 0) {
      return failure('internal', 'The video could not be encoded.',
        'Try a shorter render, or export a still.', encoderError, warnings);
    }

    // ---- mux the sound ----------------------------------------------------
    // AFTER the video, BEFORE finalize. With `fastStart: 'in-memory'` each
    // track keeps its own sample array and no interleaving is required, so
    // adding all video then all audio is correct and produces a properly
    // chunked, seekable file.
    //
    // `addAudioChunkRaw`, never `addAudioChunk`: the latter forwards
    // `chunk.duration` straight through and mp4-muxer THROWS on a null one —
    // and `EncodedAudioChunk.duration` is spec-nullable. Same trap the video
    // path above already works around.
    if (audioTrack) {
      try {
        const trimmed = truncateAudio(audioTrack.chunks, frames * frameDurUs);
        for (const c of trimmed) {
          muxer.addAudioChunkRaw(c.data, c.type, c.timestamp, c.duration, c.meta);
          audioMuxed++;
        }
      } catch (e) {
        // The video is already complete and muxed. Losing the sound at this
        // point must not lose the file with it.
        audioTrack = null;
        audioMuxed = 0;
        audioReason = `Sound could not be written into the file (${errText(e)}).`;
      }
    }

    try { muxer.finalize(); } catch (e) {
      return failure('internal', 'The video file could not be assembled.',
        'Try a shorter render.', errText(e), warnings);
    }

    const buffer = (muxer.target as ArrayBufferTarget).buffer;
    if (!buffer || buffer.byteLength === 0) {
      return failure('empty', 'The render came out empty.',
        'Try a shorter render.', encoderError ?? 'empty muxer output', warnings);
    }

    const blob = new Blob([buffer], { type: 'video/mp4' });

    if (stop === 'memory') {
      warnings.push('Render stopped early to stay inside this device’s memory budget.');
    }
    if (capped) {
      warnings.push(`Renders are capped at ${profile.maxSeconds}s on this device.`);
    }
    // A silent file always names WHY it is silent — never a blanket claim that
    // the renderer cannot carry sound, which stopped being true.
    if (!audioMuxed && wantsAudio && audioReason) warnings.push(audioReason);

    phase = 'done';
    emit('Done', 1);

    const mimeType = 'video/mp4';
    return {
      ok: true,
      blob,
      url: URL.createObjectURL(blob),
      filename: suggestFilename(options.filenameBase ?? 'collage', mimeType),
      container: describeContainer(mimeType),
      mimeType,
      durationMs,
      sizeBytes: blob.size,
      chunks: frames,
      fps,
      audio: {
        requested: wantsAudio,
        // `recorded` means SAMPLES ARE IN THE FILE — not that a track was
        // declared, and not that the encoder said yes. Only the mux count can
        // honestly answer that, which is why it is what is read here.
        recorded: audioMuxed > 0,
        tracks: audioMuxed > 0 ? 1 : 0,
        sources: audioMuxed > 0 ? (audioTrack?.sources ?? 0) : 0,
        // Always false: there are no speakers in an offline render. The field
        // means "the monitor leg was wired", and claiming it here would be the
        // exact silent-playback lie the realtime path built its analysers to
        // make observable.
        monitorConnected: false,
      },
      validated: flushed ? 'unverified' : 'skipped',
      capped,
      warnings,
    };
  } catch (e) {
    phase = 'failed';
    emit('Failed', 1);
    return failure('internal', 'Something went wrong while rendering.',
      'Export a still instead.', errText(e), warnings);
  } finally {
    // The stage MUST come back, on every path, or the collage stays frozen and
    // silent for the rest of the session with no way back short of a reload.
    if (started) { try { source.endOfflineRender(); } catch { /* ignore */ } }
  }
};
