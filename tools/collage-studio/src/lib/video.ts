// src/lib/video.ts
// -----------------------------------------------------------------------------
// VIDEO FRAME EXTRACTION
//
// Turns a video file into a pool of still frames that feed the same smart-crop
// collage pipeline images use. Everything here runs against a plain <video>
// element + canvas, because that is the only decode path available on every
// browser we care about (WebCodecs is Chromium-only and needs a demuxer).
//
// The hard parts, and why the code looks the way it does:
//
//   * `duration` is Infinity/NaN for fragmented MP4 and many WebM recordings
//     until you force the demuxer to scan. `probeVideo` does the seek-to-huge
//     trick and waits for `durationchange`.
//   * `seeked` is NOT a promise that a frame has been *painted*. Drawing right
//     after `seeked` yields the previous frame — or pure black — on Safari.
//     Where `requestVideoFrameCallback` exists we wait for a real presented
//     frame AND take its `mediaTime` as the honest timestamp; where it does not
//     we settle for `seeked` + a rAF pair that is ALSO timer-guarded, because
//     rAF never fires in a background tab and an un-guarded rAF wait is an
//     unrecoverable hang.
//   * iOS refuses to decode until the element has been "activated". A muted,
//     playsInline `play()`/`pause()` pair primes it — and the reset seek that
//     follows is AWAITED, because an in-flight seek satisfies the *next* seek's
//     `seeked` listener and silently hands you the wrong frame.
//   * A seek past the last keyframe, or exactly to `duration`, can never fire
//     `seeked`. Every wait is therefore timeout-guarded, every target time is
//     clamped inside the playable interior, and a timed-out seek arms a drain
//     so its late event cannot resolve the following one.
//   * Blank frames happen (fades, letterboxed intros, decoder not ready). We
//     detect near-uniform frames, retry once at a nudged timestamp (nudging
//     BACKWARD at the tail, where forward is a no-op), and report what we had
//     to drop instead of silently shipping black.
//
// MEMORY DOCTRINE: a candidate frame is encoded to JPEG and its canvas released
// inside the sampling loop. Nothing here ever holds more than one full-size
// canvas at a time, so a 60-frame smart pass costs ~25 MB of blobs instead of
// ~1 GB of retained canvases. Object URLs are minted ONLY for frames that are
// actually returned, and `revokeFrames` disposes of them.
// -----------------------------------------------------------------------------

export interface VideoProbe {
  duration: number;
  width: number;
  height: number;
  /** Fired by the element rather than inferred; null when the browser can decode. */
  error: string | null;
}

export type FrameStrategy = 'uniform' | 'smart';

export interface ExtractProgress {
  phase: 'metadata' | 'scan' | 'select' | 'encode' | 'done';
  /** Monotonic 0..1 across the whole run. Never goes backwards. */
  ratio: number;
  done: number;
  total: number;
  label: string;
  /** Frames banked so far — a real partial-success signal for the UI. */
  framesReady: number;
  elapsedMs: number;
  etaMs: number | null;
}

export interface ExtractOptions {
  /** How many frames to keep. Clamped to [1, MAX_FRAMES]. */
  frameCount: number;
  strategy: FrameStrategy;
  /** Longest edge of an extracted frame, px. Keeps memory sane on 4K sources. */
  maxDim?: number;
  /** JPEG quality for the encoded frames. Default 0.9. */
  quality?: number;
  /** Sample only this slice of the clip (seconds). Defaults to the whole interior. */
  startTime?: number;
  endTime?: number;
  /** Skip the duration re-probe when the caller already ran `probeVideo`. */
  knownDuration?: number;
  /** Hard wall-clock ceiling for the whole run. Default 120 s. */
  timeBudgetMs?: number;
  /** Upper bound on decoded candidates (smart mode oversamples). Default 96. */
  maxSamples?: number;
  signal?: AbortSignal;
  onProgress?: (p: ExtractProgress) => void;
}

export interface ExtractedFrame {
  blob: Blob;
  /** blob: URL, already created. Dispose with `revokeFrames`. */
  url: string;
  width: number;
  height: number;
  /** Seconds into the source video (the PRESENTED frame's time where available). */
  time: number;
  index: number;
  /** True when this frame tripped the near-uniform test but was kept anyway. */
  blank: boolean;
}

export interface ExtractResult {
  frames: ExtractedFrame[];
  /** Timestamps we attempted. */
  sampled: number;
  /** Timestamps that could not be decoded at all. */
  failed: number;
  /** Near-uniform frames discarded because better candidates existed. */
  blankDropped: number;
  /** Near-uniform frames shipped anyway (nothing better was available). */
  blankKept: number;
  /** True when the wall-clock budget or the failure breaker cut sampling short. */
  truncated: boolean;
  duration: number;
  sourceWidth: number;
  sourceHeight: number;
}

export const MAX_FRAMES = 60;
const SEEK_TIMEOUT_MS = 8000;
const LOAD_TIMEOUT_MS = 30000;
/** The Infinity-duration trick gets its own short leash: it is a best-effort probe. */
const DURATION_PROBE_MS = 8000;
/** How long we will wait for a *presented* frame after `seeked` resolves. */
const PAINT_TIMEOUT_MS = 1200;
/**
 * Leash on the priming `play()`. HTMLMediaElement.play() resolves only when
 * playback ACTUALLY starts: an element that accepts the call but never reaches
 * HAVE_FUTURE_DATA and never fires `error` leaves that promise pending forever.
 * Awaiting it bare wedged the whole run at "Priming decoder…" with no way out —
 * the AbortController could not reach it, so Cancel did nothing.
 */
const PLAY_TIMEOUT_MS = 2500;
/** Window in which a late `seeked` from a timed-out seek is swallowed. */
const DRAIN_MS = 350;
/** Smart mode probes this multiple of the requested frames, then selects. */
const SMART_OVERSAMPLE = 3;
/** Absolute ceiling on decoded candidates regardless of oversample math. */
const DEFAULT_MAX_SAMPLES = 96;
const DEFAULT_TIME_BUDGET_MS = 120000;
/** Consecutive unreadable timestamps that mean the decoder has wedged. */
const MAX_CONSECUTIVE_FAILURES = 3;
/** Downscaled width used for the cheap distinctness/energy/blankness pass. */
const SCORE_W = 96;

export class VideoDecodeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'VideoDecodeError';
  }
}

const abortError = () => new DOMException('Aborted', 'AbortError');

const isAbortError = (e: unknown): boolean =>
  !!e && typeof e === 'object' && (e as { name?: string }).name === 'AbortError';

const throwIfAborted = (signal?: AbortSignal) => {
  if (signal?.aborted) throw abortError();
};

const nowMs = (): number =>
  typeof performance !== 'undefined' && typeof performance.now === 'function'
    ? performance.now()
    : Date.now();

/** Human-readable reason from a MediaError, which has no useful `message`. */
const mediaErrorText = (el: HTMLVideoElement): string => {
  const e = el.error;
  if (!e) return 'Unknown video error';
  switch (e.code) {
    case 1: return 'Video loading was aborted';
    case 2: return 'Network error while reading the video';
    case 3: return 'Video is corrupt or uses an unsupported codec';
    case 4:
      return 'This browser cannot decode that video (iPhone .mov/HEVC often ' +
             'needs Safari — try exporting as H.264 MP4)';
    default: return 'Unknown video error';
  }
};

// -----------------------------------------------------------------------------
// SESSION — one <video> element + its object URL + a PERSISTENT error listener.
// The persistent listener matters: a MediaError raised while no wait is pending
// used to be invisible, so the next wait burned its full timeout and then lied
// about the cause.
// -----------------------------------------------------------------------------

interface VideoSession {
  v: HTMLVideoElement;
  url: string;
  /** Last element-level error text, observed even between waits. */
  lastError: string | null;
  /** A seek timed out; its late `seeked` must be drained before the next one. */
  staleSeek: boolean;
  /** Time of the last frame we actually saw painted, or null if unknown. */
  paintedTime: number | null;
  dispose: () => void;
}

const openVideo = (file: File): VideoSession => {
  const url = URL.createObjectURL(file);
  const v = document.createElement('video');
  v.preload = 'auto';
  v.muted = true;
  v.defaultMuted = true;
  v.volume = 0;
  v.playsInline = true;
  v.setAttribute('playsinline', '');
  v.setAttribute('webkit-playsinline', '');
  v.setAttribute('aria-hidden', 'true');
  // NOTE: no crossOrigin. The source is always a same-origin blob: URL, so it
  // buys nothing, and setting it has historically broken loads on Safari.
  v.style.cssText =
    'position:fixed;left:-9999px;top:0;width:1px;height:1px;opacity:0;pointer-events:none';

  const session: VideoSession = {
    v,
    url,
    lastError: null,
    staleSeek: false,
    paintedTime: null,
    dispose: () => {
      try {
        v.removeEventListener('error', onError);
        v.pause();
        v.removeAttribute('src');
        v.srcObject = null;
        v.load(); // releases the decoder; without this Safari leaks it for minutes
      } catch {
        /* teardown must never throw */
      }
      v.remove();
      URL.revokeObjectURL(url);
    },
  };

  function onError() { session.lastError = mediaErrorText(v); }
  v.addEventListener('error', onError);

  v.src = url;
  // Safari will not decode a video element that was never in the document.
  document.body.appendChild(v);
  return session;
};

/** Resolve on the first of several events, or reject on timeout / element error. */
const waitForEvent = (
  s: VideoSession,
  events: string[],
  timeoutMs: number,
  what: string,
  signal?: AbortSignal,
): Promise<void> =>
  new Promise((resolve, reject) => {
    // An already-aborted signal never fires 'abort' again — check synchronously.
    if (signal?.aborted) { reject(abortError()); return; }
    if (s.lastError) { reject(new VideoDecodeError(s.lastError)); return; }

    const el = s.v;
    let settled = false;
    const cleanup = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      events.forEach((ev) => el.removeEventListener(ev, onOk));
      el.removeEventListener('error', onErr);
      signal?.removeEventListener('abort', onAbort);
    };
    const onOk = () => { cleanup(); resolve(); };
    const onErr = () => { cleanup(); reject(new VideoDecodeError(mediaErrorText(el))); };
    const onAbort = () => { cleanup(); reject(abortError()); };
    const timer = setTimeout(() => {
      cleanup();
      // Prefer the real element error over a generic timeout message.
      reject(new VideoDecodeError(s.lastError || `Timed out waiting for ${what}`));
    }, timeoutMs);

    events.forEach((ev) => el.addEventListener(ev, onOk, { once: true }));
    el.addEventListener('error', onErr, { once: true });
    signal?.addEventListener('abort', onAbort, { once: true });
  });

/**
 * Swallow the late `seeked` left behind by a timed-out seek. Without this the
 * abandoned event resolves the NEXT seek instantly and the frame we grab does
 * not match the timestamp we report.
 */
const drainStaleSeek = (s: VideoSession): Promise<void> =>
  new Promise((resolve) => {
    const el = s.v;
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      el.removeEventListener('seeked', finish);
      resolve();
    };
    const timer = setTimeout(finish, DRAIN_MS);
    el.addEventListener('seeked', finish, { once: true });
  });

/**
 * rAF pair, but ALWAYS timer-guarded and abort-aware.
 * rAF is frozen in a hidden tab; the un-guarded version of this function was an
 * unrecoverable hang (Firefox has no requestVideoFrameCallback, so it is the
 * only paint signal there). Timers still fire when throttled, so this resolves.
 */
const settleWithin = <T,>(p: Promise<T>, timeoutMs: number, signal?: AbortSignal): Promise<void> =>
  new Promise((resolve) => {
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      signal?.removeEventListener('abort', finish);
      resolve();
    };
    const timer = setTimeout(finish, timeoutMs);
    signal?.addEventListener('abort', finish, { once: true });
    // Never rethrows: the caller decides what a refusal means. A rejected
    // play() (autoplay policy) and a never-settling one look identical here,
    // which is exactly right — both mean "carry on with the seek path".
    p.then(finish, finish);
  });

const nextPaint = (timeoutMs: number, signal?: AbortSignal): Promise<void> =>
  new Promise((resolve) => {
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      signal?.removeEventListener('abort', finish);
      resolve();
    };
    const timer = setTimeout(finish, timeoutMs);
    signal?.addEventListener('abort', finish, { once: true });
    if (typeof requestAnimationFrame === 'function') {
      requestAnimationFrame(() => requestAnimationFrame(finish));
    }
  });

interface FrameCallbackMeta { mediaTime?: number }
type FrameCallback = (now: number, meta: FrameCallbackMeta) => void;
type RvfcVideo = HTMLVideoElement & {
  requestVideoFrameCallback?: (cb: FrameCallback) => number;
};

/**
 * Wait for a frame to actually be PRESENTED and return its media timestamp.
 * `mediaTime` is the honest answer to "what is on screen"; `currentTime` is
 * updated synchronously on assignment and therefore lies during a seek.
 */
const waitForPaintedFrame = (
  s: VideoSession,
  signal?: AbortSignal,
): Promise<number | null> => {
  const v = s.v as RvfcVideo;
  const rvfc = v.requestVideoFrameCallback;
  if (typeof rvfc !== 'function') {
    return nextPaint(PAINT_TIMEOUT_MS, signal).then(() => null);
  }
  return new Promise<number | null>((resolve) => {
    let done = false;
    const finish = (t: number | null) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      signal?.removeEventListener('abort', onAbort);
      resolve(t);
    };
    const onAbort = () => finish(null);
    const timer = setTimeout(() => finish(null), PAINT_TIMEOUT_MS);
    signal?.addEventListener('abort', onAbort, { once: true });
    try {
      rvfc.call(v, (_now: number, meta: FrameCallbackMeta) =>
        finish(typeof meta?.mediaTime === 'number' ? meta.mediaTime : null));
    } catch {
      finish(null);
    }
  });
};

/**
 * Read duration + intrinsic size. Handles the Infinity-duration case that
 * fragmented MP4 / MediaRecorder WebM files hit.
 */
export const probeVideo = async (file: File, signal?: AbortSignal): Promise<VideoProbe> => {
  if (signal?.aborted) throw abortError();
  const s = openVideo(file);
  try {
    await waitForEvent(s, ['loadedmetadata'], LOAD_TIMEOUT_MS, 'video metadata', signal);

    const duration = await resolveDuration(s, signal);
    return {
      duration: Number.isFinite(duration) && duration > 0 ? duration : 0,
      width: s.v.videoWidth,
      height: s.v.videoHeight,
      error: duration > 0 ? null : 'Could not determine the video length',
    };
  } catch (e: unknown) {
    if (isAbortError(e)) throw e;
    const msg = e instanceof Error ? e.message : 'Could not read video';
    return { duration: 0, width: 0, height: 0, error: s.lastError || msg };
  } finally {
    s.dispose();
  }
};

/**
 * Duration, the hard way. Assumes `loadedmetadata` already fired.
 * The seek-to-huge trick gets a SHORT leash and never swallows an abort.
 */
const resolveDuration = async (s: VideoSession, signal?: AbortSignal): Promise<number> => {
  const v = s.v;
  let duration = v.duration;
  if (Number.isFinite(duration) && duration > 0) return duration;

  const known = waitForEvent(s, ['durationchange'], DURATION_PROBE_MS, 'video duration', signal)
    .catch((e: unknown) => {
      if (isAbortError(e)) throw e; // a cancel here must NOT be swallowed
      return undefined;
    });
  try { v.currentTime = 1e101; } catch { /* readyState guards this, but never trust it */ }
  await known;

  duration = v.duration;
  if (!Number.isFinite(duration) || duration <= 0) {
    try {
      if (v.seekable.length) duration = v.seekable.end(v.seekable.length - 1);
    } catch { /* seekable can throw on a torn-down element */ }
  }
  // Walk the element back to the head; awaited so it cannot race the first seek.
  await resetToHead(s, signal);
  return Number.isFinite(duration) && duration > 0 ? duration : 0;
};

/** Seek back to the head and WAIT for it, so no seek is ever left in flight. */
const resetToHead = async (s: VideoSession, signal?: AbortSignal): Promise<void> => {
  const v = s.v;
  if (!(v.currentTime > 0.001)) { s.paintedTime = null; return; }
  const seeked = waitForEvent(s, ['seeked'], SEEK_TIMEOUT_MS, 'decoder reset', signal)
    .catch((e: unknown) => {
      if (isAbortError(e)) throw e;
      s.staleSeek = true;   // its late event must not resolve the next seek
      return undefined;
    });
  try { v.currentTime = 0; } catch { /* ignore */ }
  await seeked;
  s.paintedTime = null;
};

/** Prime the decoder so the very first grab is not a black frame. */
const primeDecoder = async (s: VideoSession, signal?: AbortSignal) => {
  throwIfAborted(signal);
  try {
    const p = s.v.play();
    // DEADLINED, not awaited bare. Priming is an OPTIMISATION (it stops the
    // first grab being black); the seek path works without it. A play() that
    // never settles must therefore cost 2.5 s, not the whole session.
    if (p && typeof p.then === 'function') await settleWithin(p, PLAY_TIMEOUT_MS, signal);
  } catch {
    // Autoplay refusal is fine — muted+playsInline is usually allowed, and when
    // it is not, the seek path still works.
  }
  try { s.v.pause(); } catch { /* ignore */ }
  throwIfAborted(signal);
  await resetToHead(s, signal);
};

/**
 * Seek and wait until a frame for that position is actually presented.
 * Returns the timestamp of the PRESENTED frame where the browser tells us
 * (requestVideoFrameCallback), else the element's currentTime.
 */
const seekTo = async (s: VideoSession, t: number, signal?: AbortSignal): Promise<number> => {
  const v = s.v;
  throwIfAborted(signal);
  const dur = Number.isFinite(v.duration) && v.duration > 0 ? v.duration : t + 1;
  // Never seek to exactly 0 or exactly duration: both can fail to fire `seeked`.
  const target = Math.min(Math.max(t, 0.01), Math.max(0.01, dur - 0.05));

  if (s.staleSeek) {
    await drainStaleSeek(s);
    s.staleSeek = false;
  }

  // Early-out ONLY if we have already SEEN a painted frame at this position.
  // (`currentTime` alone is not enough: it is updated synchronously on
  // assignment while the decoder is still seeking, so trusting it skips the
  // paint wait and hands back whatever was last drawn — usually black leader.)
  if (s.paintedTime !== null && Math.abs(s.paintedTime - target) < 0.016 && v.readyState >= 2) {
    return s.paintedTime;
  }

  const seeked = waitForEvent(s, ['seeked'], SEEK_TIMEOUT_MS, `seek to ${target.toFixed(2)}s`, signal);
  try {
    v.currentTime = target;
  } catch {
    // Consume the pending waiter so it cannot leak a rejection.
    s.staleSeek = true;
    await seeked.catch(() => undefined);
    throw new VideoDecodeError('This video refused to seek');
  }
  try {
    await seeked;
  } catch (e: unknown) {
    if (!isAbortError(e)) s.staleSeek = true;
    s.paintedTime = null;
    throw e;
  }

  const painted = await waitForPaintedFrame(s, signal);
  throwIfAborted(signal);
  s.paintedTime = painted !== null ? painted : v.currentTime;
  return s.paintedTime;
};

// -----------------------------------------------------------------------------
// CANVAS
// -----------------------------------------------------------------------------

/** Free a canvas backing store immediately; iOS is aggressive about canvas memory. */
const releaseCanvas = (c: HTMLCanvasElement | null | undefined) => {
  if (!c) return;
  try { c.width = 0; c.height = 0; } catch { /* ignore */ }
};

interface Grab { canvas: HTMLCanvasElement; time: number; }

/** Draw the current video frame into a fresh canvas at the capped size. */
const grabFrame = (s: VideoSession, maxDim: number, atTime: number): Grab => {
  const v = s.v;
  const vw = v.videoWidth || 1;
  const vh = v.videoHeight || 1;
  const scale = Math.min(1, maxDim / Math.max(vw, vh));
  const w = Math.max(1, Math.round(vw * scale));
  const h = Math.max(1, Math.round(vh * scale));
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    releaseCanvas(canvas);
    throw new VideoDecodeError('Canvas 2D is unavailable');
  }
  // NOTE: rotation. Browsers apply the container display matrix to
  // videoWidth/videoHeight, so a portrait iPhone clip reports portrait dims and
  // draws upright. If a device is ever found that does not, the fix belongs
  // here (read the transform and rotate the destination canvas).
  ctx.drawImage(v, 0, 0, w, h);
  return { canvas, time: atTime };
};

interface FrameStats {
  sig: Float32Array;
  energy: number;
  blank: boolean;
}

/**
 * ONE downscaled readback per frame gives us distinctness, energy AND blankness.
 * (The old code read the entire full-size canvas back just to sample a 32x32
 * grid — ~5.8 MB of throwaway allocation per candidate.)
 */
const analyzeFrame = (src: HTMLCanvasElement, scratch: HTMLCanvasElement): FrameStats => {
  const w = SCORE_W;
  const h = Math.max(1, Math.round((src.height / Math.max(1, src.width)) * SCORE_W));
  if (scratch.width !== w || scratch.height !== h) {
    scratch.width = w;
    scratch.height = h;
  }
  const ctx = scratch.getContext('2d', { willReadFrequently: true });
  if (!ctx) throw new VideoDecodeError('Canvas 2D is unavailable');
  ctx.drawImage(src, 0, 0, w, h);

  let d: Uint8ClampedArray;
  try {
    d = ctx.getImageData(0, 0, w, h).data;
  } catch {
    // Real cause of a SecurityError here is a tainted canvas — say so instead of
    // failing 96 frames in a row and blaming the codec.
    throw new VideoDecodeError('Frames could not be read back (the canvas was tainted)');
  }

  const sig = new Float32Array(w * h);
  let min = 1, max = 0, sum = 0;
  for (let i = 0, p = 0; p < sig.length; i += 4, p++) {
    const lum = (d[i] * 299 + d[i + 1] * 587 + d[i + 2] * 114) / 255000; // 0..1
    sig[p] = lum;
    if (lum < min) min = lum;
    if (lum > max) max = lum;
    sum += lum;
  }
  const mean = sum / sig.length;

  // Energy = mean local gradient. Busy frames beat flat ones.
  let energy = 0;
  for (let y = 0; y < h - 1; y++) {
    for (let x = 0; x < w - 1; x++) {
      const p = y * w + x;
      energy += Math.abs(sig[p] - sig[p + 1]) + Math.abs(sig[p] - sig[p + w]);
    }
  }

  // Flat contrast, or crushed to black / blown to white. Thresholds in 0..1.
  const blank = (max - min) < (6 / 255) || mean < (4 / 255) || mean > (251 / 255);
  return { sig, energy: energy / (w * h), blank };
};

const sigDistance = (a: Float32Array, b: Float32Array): number => {
  const n = Math.min(a.length, b.length);
  if (!n) return 0;
  let s = 0;
  for (let i = 0; i < n; i++) s += Math.abs(a[i] - b[i]);
  return s / n;
};

/** toBlob, but abortable and timeout-guarded — a wedged encoder must not hang. */
const toBlobSafe = (
  canvas: HTMLCanvasElement,
  quality: number,
  signal?: AbortSignal,
): Promise<Blob> =>
  new Promise((resolve, reject) => {
    if (signal?.aborted) { reject(abortError()); return; }
    let done = false;
    const finish = (fn: () => void) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      signal?.removeEventListener('abort', onAbort);
      fn();
    };
    const onAbort = () => finish(() => reject(abortError()));
    const timer = setTimeout(
      () => finish(() => reject(new VideoDecodeError('Frame encoding timed out'))),
      SEEK_TIMEOUT_MS,
    );
    signal?.addEventListener('abort', onAbort, { once: true });
    try {
      canvas.toBlob(
        (b) => finish(() => (b ? resolve(b) : reject(new VideoDecodeError('Frame encoding failed')))),
        'image/jpeg',
        quality,
      );
    } catch (e) {
      finish(() => reject(e instanceof Error ? e : new VideoDecodeError('Frame encoding failed')));
    }
  });

const yieldToUi = () => new Promise<void>((r) => setTimeout(r, 0));

// -----------------------------------------------------------------------------
// EXTRACTION
// -----------------------------------------------------------------------------

interface Candidate {
  blob: Blob;
  width: number;
  height: number;
  time: number;
  sig: Float32Array;
  energy: number;
  blank: boolean;
}

/**
 * Extract frames from a video file.
 *
 * `uniform` spreads them evenly across the sampled interval.
 * `smart` oversamples, scores each candidate on visual energy, then greedily
 * keeps the ones most different from what it already picked — so a mostly-static
 * clip yields varied frames instead of N copies of the same shot.
 *
 * Frames come back in chronological order. Every returned frame owns an object
 * URL: dispose of the whole batch with `revokeFrames`.
 */
export const extractFrames = async (
  file: File,
  opts: ExtractOptions,
): Promise<ExtractResult> => {
  const { strategy, signal, onProgress } = opts;
  const maxDim = Math.max(160, opts.maxDim ?? 1600);
  const quality = Math.min(1, Math.max(0.4, opts.quality ?? 0.9));
  const want = Math.max(1, Math.min(MAX_FRAMES, Math.floor(opts.frameCount) || 1));
  const budgetMs = Math.max(5000, opts.timeBudgetMs ?? DEFAULT_TIME_BUDGET_MS);
  const maxSamples = Math.max(want, Math.min(MAX_FRAMES * SMART_OVERSAMPLE, opts.maxSamples ?? DEFAULT_MAX_SAMPLES));

  throwIfAborted(signal);
  if (file.size === 0) throw new VideoDecodeError('That file is empty');

  const startedAt = nowMs();
  let ratioSeen = 0;
  let framesReady = 0;
  const report = (phase: ExtractProgress['phase'], ratio: number, done: number, total: number, label: string) => {
    if (!onProgress) return;
    ratioSeen = Math.max(ratioSeen, Math.min(1, Math.max(0, ratio)));
    const elapsedMs = nowMs() - startedAt;
    const etaMs = ratioSeen > 0.02 && ratioSeen < 1
      ? Math.max(0, (elapsedMs / ratioSeen) - elapsedMs)
      : null;
    onProgress({ phase, ratio: ratioSeen, done, total, label, framesReady, elapsedMs, etaMs });
  };

  const s = openVideo(file);
  const created: string[] = [];
  const scratch = document.createElement('canvas');
  let candidates: Candidate[] = [];

  try {
    report('metadata', 0.01, 0, 1, 'Reading video…');
    await waitForEvent(s, ['loadedmetadata'], LOAD_TIMEOUT_MS, 'video metadata', signal);

    let duration = opts.knownDuration && opts.knownDuration > 0 ? opts.knownDuration : s.v.duration;
    if (!Number.isFinite(duration) || duration <= 0) {
      report('metadata', 0.03, 0, 1, 'Measuring length…');
      duration = await resolveDuration(s, signal);
    }
    if (!Number.isFinite(duration) || duration <= 0) {
      throw new VideoDecodeError('Could not determine the video length');
    }
    if (!s.v.videoWidth || !s.v.videoHeight) {
      throw new VideoDecodeError('This file has no visual track (audio-only?)');
    }
    const sourceWidth = s.v.videoWidth;
    const sourceHeight = s.v.videoHeight;

    report('metadata', 0.05, 0, 1, 'Priming decoder…');
    await primeDecoder(s, signal);
    throwIfAborted(signal);

    // Candidate timestamps. Default to the interior: the first and last
    // fractions of a clip are usually black leader or a fade.
    const trim = Math.min(duration * 0.02, 0.25);
    const reqStart = Number.isFinite(opts.startTime ?? NaN) ? Math.max(0, opts.startTime as number) : trim;
    const reqEnd = Number.isFinite(opts.endTime ?? NaN) ? Math.min(duration, opts.endTime as number) : duration - trim;
    const lo = Math.max(0, Math.min(reqStart, Math.max(0, duration - 0.05)));
    const hi = Math.max(lo + 0.01, Math.min(reqEnd, duration));

    const nSamples = strategy === 'smart'
      ? Math.min(maxSamples, Math.max(want, want * SMART_OVERSAMPLE))
      : want;

    const times: number[] = [];
    for (let i = 0; i < nSamples; i++) {
      // Midpoint sampling: for n=1 this lands mid-clip rather than at the head.
      const f = (i + 0.5) / nSamples;
      times.push(lo + (hi - lo) * f);
    }

    const SCAN_FLOOR = 0.06;
    const SCAN_CEIL = 0.94;
    let failed = 0;
    let consecutiveFailures = 0;
    let truncated = false;

    for (let i = 0; i < times.length; i++) {
      throwIfAborted(signal);
      if (nowMs() - startedAt > budgetMs) { truncated = true; break; }

      report(
        'scan',
        SCAN_FLOOR + (SCAN_CEIL - SCAN_FLOOR) * (i / times.length),
        i,
        times.length,
        `Decoding frame ${i + 1} of ${times.length}`,
      );

      let grab: Grab | null = null;
      let retry: Grab | null = null;
      try {
        const landed = await seekTo(s, times[i], signal);
        grab = grabFrame(s, maxDim, landed);
        let stats = analyzeFrame(grab.canvas, scratch);

        if (stats.blank) {
          // A blank grab usually means the decoder had not caught up. Nudge and
          // retry once — BACKWARD when we are at the tail, where a forward nudge
          // clamps onto the same timestamp and re-reads the identical frame.
          const step = Math.max(0.12, duration * 0.01);
          const nudge = landed + step <= hi ? landed + step : Math.max(lo, landed - step);
          if (Math.abs(nudge - landed) > 0.016) {
            const landed2 = await seekTo(s, nudge, signal);
            retry = grabFrame(s, maxDim, landed2);
            const stats2 = analyzeFrame(retry.canvas, scratch);
            if (!stats2.blank) {
              releaseCanvas(grab.canvas);
              grab = retry;
              retry = null;
              stats = stats2;
            }
          }
        }

        // Encode NOW and drop the canvas. This is the whole memory doctrine:
        // a 96-candidate smart pass costs ~25 MB of JPEG instead of ~1 GB of
        // retained canvases.
        const blob = await toBlobSafe(grab.canvas, quality, signal);
        candidates.push({
          blob,
          width: grab.canvas.width,
          height: grab.canvas.height,
          time: grab.time,
          sig: stats.sig,
          energy: stats.energy,
          blank: stats.blank,
        });
        framesReady = Math.min(candidates.length, want);
        consecutiveFailures = 0;
      } catch (e: unknown) {
        if (isAbortError(e)) throw e;
        failed++;
        consecutiveFailures++;
        const msg = e instanceof Error ? e.message : String(e);
        console.warn(`[video] frame at ${times[i].toFixed(2)}s failed:`, msg);
        if (consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
          // The decoder has wedged. Asking it 90 more times just burns 12 minutes.
          truncated = true;
          break;
        }
      } finally {
        releaseCanvas(grab?.canvas);
        releaseCanvas(retry?.canvas);
      }

      // Let React paint the progress bar; a frozen UI reads as a crash.
      if ((i & 1) === 1) await yieldToUi();
    }

    if (!candidates.length) {
      throw new VideoDecodeError(
        s.lastError ||
        'No frames could be read from this video. If it came from an iPhone, ' +
        'export it as H.264 MP4 and try again.',
      );
    }

    // --- SELECT ---------------------------------------------------------------
    report('select', 0.95, candidates.length, candidates.length, 'Choosing frames…');
    await yieldToUi();

    const usable = candidates.filter((c) => !c.blank);
    const usedBlanks = usable.length === 0;
    const pool = usedBlanks ? candidates : usable;
    const blankDropped = usedBlanks ? 0 : candidates.length - usable.length;

    let chosen: Candidate[];
    if (strategy === 'smart' && pool.length > want) {
      chosen = selectDiverse(pool, want);
    } else if (pool.length > want) {
      // Spread evenly over the survivors rather than taking the first N, which
      // would bunch every frame at the head once anything got dropped.
      chosen = [];
      for (let i = 0; i < want; i++) {
        chosen.push(pool[Math.min(pool.length - 1, Math.round((i + 0.5) * pool.length / want - 0.5))]);
      }
      chosen = Array.from(new Set(chosen));
    } else {
      chosen = [...pool];
    }

    chosen.sort((a, b) => a.time - b.time);

    // --- PUBLISH --------------------------------------------------------------
    const frames: ExtractedFrame[] = chosen.map((c, i) => {
      const frameUrl = URL.createObjectURL(c.blob);
      created.push(frameUrl);
      return {
        blob: c.blob,
        url: frameUrl,
        width: c.width,
        height: c.height,
        time: c.time,
        index: i,
        blank: c.blank,
      };
    });
    framesReady = frames.length;

    report('done', 1, frames.length, frames.length, 'Done');
    return {
      frames,
      sampled: times.length,
      failed,
      blankDropped,
      blankKept: chosen.filter((c) => c.blank).length,
      truncated,
      duration,
      sourceWidth,
      sourceHeight,
    };
  } catch (e) {
    created.forEach((u) => URL.revokeObjectURL(u));
    throw e;
  } finally {
    candidates = [];
    releaseCanvas(scratch);
    s.dispose();
  }
};

/** What the collage needs from a clip: its shape, and ONE raster to sit under it. */
export interface ClipIntake extends VideoProbe {
  /** The single poster. Owns an object URL — dispose with `revokeFrames([poster])`. */
  poster: ExtractedFrame | null;
}

/**
 * OPEN A CLIP IN ONE PASS — the intake the app actually uses.
 *
 * The old intake was `probeVideo` followed by `extractFrames`, and that is THREE
 * decoder set-ups for one file: probe opens a video element and throws it away,
 * extract opens a second one, primes it and seeks it three times (smart@1
 * oversamples by 3 to dodge black leader), and only then does the stage open the
 * third one it will actually play. Measured on the live build against a 25 s
 * 1080p H.264 clip: the decoder was ADVANCING at 256 ms and the clip did not
 * reach the collage until 3,517 ms. Thirteen fourteenths of that wait is the app
 * pulling a frame out of a video it had already decoded — which is exactly what
 * the owner has been describing: "you're still asking for how many frames to
 * pull instead of just loading the video."
 *
 * So: one session, one metadata wait, one prime, ONE seek. The poster still
 * comes from the clip's interior (`trim` skips the fade/black leader at both
 * ends) and a blank grab still gets its one nudge-and-retry, so the frame is a
 * real moment rather than the head of a fade. What is gone is the oversampling —
 * choosing the *most distinct* of three candidates only matters when you are
 * keeping several, and we keep one.
 *
 * `extractFrames` is untouched and still exports the multi-frame path; nothing
 * in the app calls it with `frameCount > 1` any more, and no UI asks for one.
 */
export const openClip = async (
  file: File,
  opts: {
    maxDim?: number;
    quality?: number;
    signal?: AbortSignal;
    onProgress?: (ratio: number) => void;
  } = {},
): Promise<ClipIntake> => {
  const { signal, onProgress } = opts;
  const maxDim = Math.max(160, opts.maxDim ?? 1600);
  const quality = Math.min(1, Math.max(0.4, opts.quality ?? 0.9));
  if (signal?.aborted) throw abortError();
  if (file.size === 0) return { duration: 0, width: 0, height: 0, error: 'That file is empty', poster: null };

  const s = openVideo(file);
  const scratch = document.createElement('canvas');
  let grab: Grab | null = null;
  let retry: Grab | null = null;

  try {
    onProgress?.(0.05);
    await waitForEvent(s, ['loadedmetadata'], LOAD_TIMEOUT_MS, 'video metadata', signal);

    const duration = await resolveDuration(s, signal);
    const width = s.v.videoWidth;
    const height = s.v.videoHeight;
    // Shape first, and reported even when the poster later fails: the caller's
    // "audio only" / "could not be read" messages key off exactly these.
    if (!Number.isFinite(duration) || duration <= 0) {
      return { duration: 0, width, height, error: 'Could not determine the video length', poster: null };
    }
    if (!width || !height) {
      return { duration, width, height, error: null, poster: null };
    }

    onProgress?.(0.25);
    await primeDecoder(s, signal);
    throwIfAborted(signal);

    // Mid-clip, inside the trimmed interior — the same window the old smart pass
    // sampled, minus the two extra seeks.
    const trim = Math.min(duration * 0.02, 0.25);
    const lo = Math.max(0, Math.min(trim, Math.max(0, duration - 0.05)));
    const hi = Math.max(lo + 0.01, duration - trim);
    const at = lo + (hi - lo) * 0.5;

    onProgress?.(0.5);
    const landed = await seekTo(s, at, signal);
    grab = grabFrame(s, maxDim, landed);
    let stats = analyzeFrame(grab.canvas, scratch);

    if (stats.blank) {
      // Same nudge the multi-frame path uses: a blank grab is usually a decoder
      // that had not caught up, not a black clip. Backward at the tail, where a
      // forward nudge clamps and re-reads the identical frame.
      const step = Math.max(0.12, duration * 0.01);
      const nudge = landed + step <= hi ? landed + step : Math.max(lo, landed - step);
      if (Math.abs(nudge - landed) > 0.016) {
        const landed2 = await seekTo(s, nudge, signal);
        retry = grabFrame(s, maxDim, landed2);
        const stats2 = analyzeFrame(retry.canvas, scratch);
        if (!stats2.blank) {
          releaseCanvas(grab.canvas);
          grab = retry;
          retry = null;
          stats = stats2;
        }
      }
    }

    onProgress?.(0.85);
    const blob = await toBlobSafe(grab.canvas, quality, signal);
    const poster: ExtractedFrame = {
      blob,
      url: URL.createObjectURL(blob),
      width: grab.canvas.width,
      height: grab.canvas.height,
      time: grab.time,
      index: 0,
      blank: stats.blank,
    };
    onProgress?.(1);
    return { duration, width, height, error: null, poster };
  } catch (e: unknown) {
    if (isAbortError(e)) throw e;
    const msg = e instanceof Error ? e.message : 'Could not read video';
    return { duration: 0, width: 0, height: 0, error: s.lastError || msg, poster: null };
  } finally {
    releaseCanvas(grab?.canvas);
    releaseCanvas(retry?.canvas);
    releaseCanvas(scratch);
    s.dispose();
  }
};

/**
 * Greedy max-min diversity pick, with the per-candidate minimum distance CACHED.
 * The naive version rescans the whole picked set on every round: for 60 picks
 * out of 96 candidates that is ~1.4e9 float ops on the main thread — seconds of
 * frozen UI. Caching makes it ~30x cheaper.
 */
const selectDiverse = (pool: Candidate[], want: number): Candidate[] => {
  const rest = [...pool].sort((a, b) => b.energy - a.energy);
  const first = rest.shift();
  if (!first) return [];
  const picked: Candidate[] = [first];
  const minD = rest.map((c) => sigDistance(c.sig, first.sig));

  while (picked.length < want && rest.length) {
    let bestIdx = 0;
    let bestScore = -Infinity;
    for (let i = 0; i < rest.length; i++) {
      const score = minD[i] * (0.35 + rest[i].energy);
      if (score > bestScore) { bestScore = score; bestIdx = i; }
    }
    const winner = rest.splice(bestIdx, 1)[0];
    minD.splice(bestIdx, 1);
    picked.push(winner);
    // Only the NEW pick can lower anyone's minimum distance.
    for (let i = 0; i < rest.length; i++) {
      const d = sigDistance(rest[i].sig, winner.sig);
      if (d < minD[i]) minD[i] = d;
    }
  }
  return picked;
};

/**
 * Dispose of a batch of frames. The API hands you N object URLs; this is how you
 * give them back. Safe to call twice, and safe on a partially consumed batch.
 */
export const revokeFrames = (frames: Iterable<ExtractedFrame> | null | undefined): void => {
  if (!frames) return;
  const seen = new Set<string>();
  for (const f of frames) {
    if (!f?.url || seen.has(f.url)) continue;
    seen.add(f.url);
    try { URL.revokeObjectURL(f.url); } catch { /* already gone */ }
  }
};

/** `mm:ss` (or `h:mm:ss`) for a timestamp badge. */
export const formatTimecode = (seconds: number): string => {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00';
  const total = Math.floor(seconds);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  return h > 0
    ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    : `${m}:${String(s).padStart(2, '0')}`;
};

const VIDEO_EXT = /\.(mp4|m4v|mov|qt|webm|mkv|avi|ogv|ogg|3gp|3g2|mpg|mpeg|ts|m2ts)$/i;

/**
 * Route a picked/dropped file. Some .mov arrive with an EMPTY MIME type.
 *
 * The parameter is STRUCTURAL rather than `File` — it reads two strings and a
 * `File` satisfies the shape, so nothing at any call site changes. It is widened
 * so `lib/intake.ts` (which owns the bucket ladder) and the sweeps can ask the
 * question about a `{ name, type }` pair without minting a blob, exactly as
 * `soundtrack.isAudioFile` already allows. The sweep was ALREADY doing this and
 * only got away with it because types are erased at runtime.
 */
export const isVideoFile = (file: { name: string; type: string }): boolean =>
  file.type.startsWith('video/') || (!file.type && VIDEO_EXT.test(file.name));

export interface DecodeHint {
  level: 'ok' | 'unsure' | 'unlikely';
  message: string | null;
}

/**
 * ADVISORY ONLY — never gate intake on this.
 * Chrome answers '' for `video/quicktime` yet decodes H.264 .mov files all day,
 * so '' is the LEAST reliable answer, not a reliable "no". We surface it as a
 * warning and let the decoder have the final word.
 */
export const inspectSupport = (file: File): DecodeHint => {
  if (!file.type) return { level: 'unsure', message: null };
  let verdict = '';
  try {
    verdict = document.createElement('video').canPlayType(file.type);
  } catch {
    return { level: 'unsure', message: null };
  }
  if (verdict === 'probably') return { level: 'ok', message: null };
  if (verdict === 'maybe') return { level: 'unsure', message: null };
  return {
    level: 'unlikely',
    message: `This browser is unsure about ${file.type}. It may still work — ` +
             'if it fails, export the clip as H.264 MP4.',
  };
};

/** Back-compat shim. Advisory: treat a `false` as a warning, never a block. */
export const canProbablyDecode = (file: File): boolean =>
  inspectSupport(file).level !== 'unlikely';
