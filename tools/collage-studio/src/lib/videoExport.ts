// src/lib/videoExport.ts
// -----------------------------------------------------------------------------
// CANVAS -> VIDEO FILE
//
// Records a LIVE canvas (the moving collage) plus the audio of the clips playing
// on it into a downloadable video file. Nothing here draws: the caller owns the
// draw loop and keeps the canvas dirty; this module only taps it.
//
// Why the code looks the way it does — every one of these is a real, shipped bug
// class, not a hypothetical:
//
//   * SUPPORT CANNOT BE READ OFF A CONSTANT. MDN's compat data says iOS Safari
//     supports canvas capture (via an INFERRED "mirror" value, not a tested one);
//     caniuse marks iOS unsupported at every version. Neither is authoritative,
//     and WebKit's own bug history (229611 blank video, 181663 freeze-on-stop,
//     iOS 15 reports of onstop/ondataavailable never firing) says "sometimes".
//     So we never trust a version, a UA string, or `typeof MediaRecorder`. We run
//     a 400 ms dry-run take on a 32x32 throwaway canvas and let the DEVICE answer.
//     Trusting a constant here is the same bug that broke MAX still-export.
//
//   * EVERY WAIT IS DEADLINED. An oversized/unsupported media operation does not
//     reliably throw — it hangs. `stop()` is raced against a grace period and the
//     blob is assembled from accumulated chunks regardless of whether `onstop`
//     ever fires.
//
//   * TIMESLICE IS MANDATORY. Without `start(ms)` the UA buffers the whole take
//     internally and iOS dies exactly at final Blob assembly (Apple forum 694867
//     pins the crash on `new Blob(blobs)`). With a timeslice we hold bounded,
//     countable chunks and can stop early when memory says so.
//
//   * DURATION IS CAPPED, HARD. iOS reliably crashes/reloads at >= 1 minute. The
//     cap auto-stops on a timer — an unbounded operation that does not throw is
//     the same failure class as the MAX-export hang.
//
//   * createMediaElementSource STEALS THE SPEAKERS. Creating the node re-routes
//     the element's audio into the graph; if the graph does not reach
//     ctx.destination the user hears SILENCE while the recording sounds perfect.
//     Nothing throws. The fix is to fan one gain out to BOTH sinks, and it is
//     structurally unavoidable here: `attachSource` has a single code path and it
//     always wires the monitor leg. `getAudioLevels()` measures both legs so the
//     invariant is observable at runtime, not merely asserted in a comment.
//
//   * THE NODE IS PERMANENT. A second createMediaElementSource on one element
//     throws InvalidStateError and there is no detach API — React StrictMode's
//     double-invoke hits this on the first try. The WeakMap cache is a
//     CORRECTNESS requirement, not an optimisation. For the same reason the
//     shared AudioContext is never closed once an element has been attached.
//
//   * `.muted` / `.volume` STILL SILENCE THE GRAPH. Once an element is attached,
//     level lives EXCLUSIVELY in its GainNode. We unmute once at attach time
//     (inside the user gesture) and never touch those properties again.
//
//   * WEBM IS A DEAD END ON APPLE PLATFORMS. It plays in-browser but will not
//     open in QuickTime and will not import to Photos. We ask for MP4 first at
//     every tier and, when we did not get it, we SAY SO (`appleNative:false` +
//     a warning string) instead of handing over a file that will not open.
//
// NOTHING IN HERE THROWS AT THE UI. `record()` always resolves to a typed
// discriminated union; a DOMException is converted into a code + human message +
// advice. The only exception that can escape is one the caller caused by passing
// a non-canvas.
// -----------------------------------------------------------------------------

import { probeVideo } from './video';

// =============================================================================
// TYPES
// =============================================================================

export type ContainerKind = 'mp4' | 'webm' | 'mkv' | 'mov' | 'unknown';

export interface ContainerInfo {
  /** The mime the recorder actually used (may differ from the one requested). */
  mime: string;
  kind: ContainerKind;
  /** File extension WITHOUT the dot. */
  extension: string;
  /** e.g. 'H.264 + AAC'. Best effort from the codecs= parameter. */
  codecLabel: string;
  /** Short UI label, e.g. 'MP4 - H.264 + AAC'. */
  label: string;
  /** Opens in QuickTime / imports to Photos on macOS + iOS. */
  appleNative: boolean;
  /** Non-null when the file will not open outside a browser. Show it verbatim. */
  warning: string | null;
}

export interface RecordingProfile {
  /** Budget heuristic ONLY — never gates a feature. */
  isPhone: boolean;
  /** SAFETY heuristic ONLY — can lower limits, never enable/disable anything. */
  appleMobile: boolean;
  fps: number;
  /** Hard duration ceiling in seconds. */
  maxSeconds: number;
  /** Longest edge of the RECORDING canvas. Separate budget from still export. */
  maxEdge: number;
  videoBitsPerSecond: number;
  audioBitsPerSecond: number;
  /** How many fragments may be LIVE video; the rest fall back to still frames. */
  maxLiveVideos: number;
  /** Auto-stop when accumulated chunks pass this, so the heap cannot run away. */
  maxBytes: number;
  timesliceMs: number;
}

export type RecordSupportLevel = 'ready' | 'likely' | 'unsupported';

export interface VideoExportSupport {
  /** 'likely' = APIs present but the dry run has not been done yet. */
  level: RecordSupportLevel;
  supported: boolean;
  /** True once the dry-run take has actually been performed on this device. */
  probed: boolean;
  apis: {
    mediaRecorder: boolean;
    isTypeSupported: boolean;
    canvasCapture: boolean;
    audioContext: boolean;
    streamDestination: boolean;
  };
  /** '' means "let the UA choose" — legal, and the last-resort tier. */
  mimeType: string;
  container: ContainerInfo;
  audio: { supported: boolean; reason: string | null };
  profile: RecordingProfile;
  /** Why it is unsupported / what was observed. Null when fine. */
  reason: string | null;
  /** What the user can do instead. Show verbatim. */
  advice: string | null;
  /** One-line UI summary, e.g. 'MP4 - H.264 + AAC, up to 30s with sound'. */
  label: string;
}

export interface RecordSource {
  el: HTMLVideoElement;
  /** 0..1, applied to this clip's GainNode. Default 1. */
  volume?: number;
  /** For error reporting only. */
  id?: string;
}

export type RecordPhase =
  | 'preparing'
  | 'probing'
  | 'arming'
  | 'recording'
  | 'finalizing'
  | 'validating'
  | 'done'
  | 'cancelled'
  | 'failed';

export interface RecordProgress {
  phase: RecordPhase;
  /** Monotonic 0..1 across the whole run. Never goes backwards. */
  ratio: number;
  elapsedMs: number;
  remainingMs: number;
  /** Bytes banked so far — real evidence the encoder is alive. */
  bytes: number;
  chunks: number;
  label: string;
  fps: number;
  withAudio: boolean;
}

/** Why a take ended. Internal, but it decides the verdict below. */
type StopReason = 'complete' | 'aborted' | 'error' | 'memory' | 'track-ended';

export type RecordFailureCode =
  | 'unsupported'      // no MediaRecorder / no canvas capture / dry run failed
  | 'no-mime'          // nothing in the candidate list is supported
  | 'bad-canvas'       // zero-sized canvas, or not a canvas
  | 'no-track'         // captureStream() gave us no video track
  | 'start-failed'     // constructor or start() threw
  | 'recorder-error'   // onerror fired mid-take
  | 'track-ended'      // the canvas track died under us
  | 'empty'            // zero chunks / zero bytes
  | 'too-small'        // below the plausible-size floor for the duration
  | 'undecodable'      // the produced file will not even report metadata
  | 'aborted'          // caller cancelled
  | 'internal';        // anything unforeseen, converted rather than thrown

export interface RecordSuccess {
  ok: true;
  blob: Blob;
  /** Object URL for the blob. Dispose with `revokeRecording`. */
  url: string;
  filename: string;
  container: ContainerInfo;
  mimeType: string;
  /** Wall-clock length of the take. NOT read from the file (fMP4 has none). */
  durationMs: number;
  sizeBytes: number;
  chunks: number;
  fps: number;
  audio: {
    requested: boolean;
    /** True only if an audio track was actually in the recorded stream. */
    recorded: boolean;
    tracks: number;
    /** Elements successfully wired into the mix. */
    sources: number;
    /** The speaker leg was connected for every attached element. */
    monitorConnected: boolean;
  };
  /** 'pass' = decoded back. 'unverified' = check timed out; file was KEPT. */
  validated: 'pass' | 'unverified' | 'skipped';
  /** True when the requested duration was clipped by the device cap. */
  capped: boolean;
  /** Human strings, already user-safe. Show them. */
  warnings: string[];
}

export interface RecordFailure {
  ok: false;
  code: RecordFailureCode;
  /** User-facing, never a raw DOMException string. */
  message: string;
  advice: string | null;
  /** The underlying error text, for logs. */
  cause: string | null;
  /** Whatever was captured before the failure, when the caller asked to keep it. */
  partial: { blob: Blob; sizeBytes: number; chunks: number; mimeType: string } | null;
  warnings: string[];
}

export type RecordResult = RecordSuccess | RecordFailure;

export interface RecordOptions {
  /** Requested length. Clamped to the device cap; the clamp is reported. */
  seconds?: number;
  fps?: number;
  /** Ask for sound. Falls back to a silent take rather than failing. */
  withAudio?: boolean;
  sources?: Array<HTMLVideoElement | RecordSource>;
  /** Force a container. Ignored when the UA says it is unsupported. */
  mimeType?: string;
  videoBitsPerSecond?: number;
  audioBitsPerSecond?: number;
  timesliceMs?: number;
  maxBytes?: number;
  signal?: AbortSignal;
  onProgress?: (p: RecordProgress) => void;
  /** Base name for the saved file. Default 'collage'. */
  filenameBase?: string;
  /** Decode the result back before calling it a success. Default true. */
  validate?: boolean;
  validateTimeoutMs?: number;
  /** Attach whatever was captured to a failure result. Default false. */
  keepPartialOnFailure?: boolean;
  /** Skip the one-time dry run (only when you have already probed). */
  skipProbe?: boolean;
  /**
   * RECORD A STREAM THE CALLER ALREADY OWNS, instead of calling
   * `canvas.captureStream()` here and building an audio graph over `sources`.
   *
   * This exists for ONE structural reason: `createMediaElementSource` may be
   * called ONCE PER ELEMENT EVER and there is no detach API. A caller that has
   * already wired its own <video> elements into its own AudioContext — `Stage`
   * does exactly this, at element creation, because bolting the graph on later
   * would mean recreating every element and dropping every decoder mid-take —
   * CANNOT also hand those elements to us as `sources`: the second
   * createMediaElementSource throws InvalidStateError and the clip goes
   * permanently silent. So such a caller passes its finished stream (video
   * track + its own mixed audio track) and we take it verbatim.
   *
   * When set: `sources`, `withAudio` and the internal audio graph are all
   * IGNORED, and the stream's tracks are left running at the end of the take —
   * they belong to the caller, who must release them (`Stage.releaseStream()`).
   * Everything else — the dry run, the duration cap, the mandatory timeslice,
   * the memory ceiling, the deadlines, validation and container reporting —
   * applies exactly as it does to a stream we captured ourselves.
   */
  stream?: MediaStream;
}

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * MP4 FIRST at every tier: it is the only thing WebKit writes, and Chrome 126+
 * (June 2024) can write it too — so asking for it gets an Apple-openable file on
 * both a Mac and an iPhone. WebM only when MP4 is genuinely unavailable.
 * '' is legal and means "UA default"; it is the last resort, never the first.
 */
export const RECORDER_MIME_CANDIDATES: readonly string[] = [
  'video/mp4;codecs=avc1.42E01E,mp4a.40.2',
  'video/mp4;codecs=avc1,mp4a.40.2',
  'video/mp4;codecs=avc1.42E01E',
  'video/mp4',
  'video/webm;codecs=vp9,opus',
  'video/webm;codecs=vp8,opus',
  'video/webm;codecs=vp9',
  'video/webm',
  '',
];

const PHONE_MAX_SECONDS = 30;      // iOS reliably crashes/reloads at >= 60 s
const DESKTOP_MAX_SECONDS = 120;
const DEFAULT_TIMESLICE_MS = 1000; // MANDATORY — see header
const STOP_GRACE_MS = 3000;        // iOS 15 sometimes never fires onstop
const PROBE_RECORD_MS = 420;
const PROBE_STOP_MS = 1500;
const PROBE_TIMESLICE_MS = 100;
const PROBE_DRAW_MS = 50;
const DEFAULT_VALIDATE_TIMEOUT_MS = 6000;
/** Matches video.ts: a play() that never settles must cost 2.5 s, not the take. */
const PLAY_TIMEOUT_MS = 2500;
const RESUME_TIMEOUT_MS = 2000;
const PROGRESS_TICK_MS = 200;
/** Plausible-size floor: a real take carries at least this per second. */
const MIN_BYTES_PER_SECOND = 1024;

const WEBM_WARNING =
  'Saved as .webm — plays in Chrome and Firefox, but not in QuickTime or ' +
  'Photos. For a file Apple devices can open, record in Safari or in ' +
  'Chrome 126+.';

const UNSUPPORTED_MESSAGE =
  "This browser can't record the canvas to a video file.";

const UNSUPPORTED_ADVICE =
  'Everything else still works — export a still, or open the studio in Chrome ' +
  'on a computer to record the moving collage.';

const NO_DURATION_WARNING =
  'The file carries no duration metadata (every browser recorder does this), so ' +
  'some players show no seekbar. It still plays, and re-importing it here works.';

// =============================================================================
// SMALL UTILITIES
// =============================================================================

const nowMs = (): number =>
  typeof performance !== 'undefined' && typeof performance.now === 'function'
    ? performance.now()
    : Date.now();

const sleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

const errText = (e: unknown): string => {
  if (!e) return 'Unknown error';
  if (e instanceof Error) return e.name ? `${e.name}: ${e.message}` : e.message;
  if (typeof e === 'string') return e;
  try { return String(e); } catch { return 'Unknown error'; }
};

const isAbortError = (e: unknown): boolean =>
  !!e && typeof e === 'object' && (e as { name?: string }).name === 'AbortError';

type Settled = { kind: 'ok' } | { kind: 'error'; reason: string } | { kind: 'timeout' };

/**
 * DEADLINE ANY MEDIA PROMISE. `HTMLMediaElement.play()` resolves only when
 * playback ACTUALLY starts: an element that accepts the call, never reaches
 * HAVE_FUTURE_DATA and never fires `error` leaves that promise pending FOREVER.
 * `AudioContext.resume()` can do the same outside a gesture. Awaiting either one
 * bare is the unbounded-operation bug that hangs instead of throwing.
 */
const settleWithin = (p: Promise<unknown>, ms: number): Promise<Settled> =>
  new Promise((resolve) => {
    let done = false;
    const finish = (s: Settled) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      resolve(s);
    };
    const timer = setTimeout(() => finish({ kind: 'timeout' }), ms);
    p.then(() => finish({ kind: 'ok' }), (e) => finish({ kind: 'error', reason: errText(e) }));
  });

const clamp = (v: number, lo: number, hi: number): number =>
  Math.min(hi, Math.max(lo, v));

const media = (q: string): boolean => {
  try {
    return typeof window !== 'undefined' &&
      typeof window.matchMedia === 'function' &&
      window.matchMedia(q).matches;
  } catch {
    return false;
  }
};

const hasDom = (): boolean =>
  typeof window !== 'undefined' && typeof document !== 'undefined';

// =============================================================================
// DEVICE PROFILE
//
// These are BUDGETS (fps, seconds, pixels, live-clip count), never capability
// gates. Getting the heuristic wrong costs a smaller recording, never a broken
// feature — which is exactly why a heuristic is allowed here and forbidden in
// `inspectVideoExportSupport`.
// =============================================================================

const isPhoneLike = (): boolean => {
  if (!hasDom()) return false;
  const coarse = media('(pointer: coarse)') || media('(hover: none)');
  const touch = (navigator.maxTouchPoints ?? 0) > 0;
  let shortEdge = 0;
  try {
    shortEdge = Math.min(window.screen?.width ?? 0, window.screen?.height ?? 0);
  } catch { /* screen can throw in exotic embeds */ }
  const small = shortEdge > 0 && shortEdge <= 820;
  return (coarse || touch) && small;
};

/**
 * SAFETY-ONLY. Used to LOWER the duration cap (iOS crashes at >= 1 min) and for
 * nothing else. It can never turn a feature on or off — that is the dry run's
 * job. iPadOS ships a Macintosh UA, hence the touch-point tell.
 */
const isAppleMobileLike = (): boolean => {
  if (!hasDom()) return false;
  const ua = navigator.userAgent || '';
  const classic = /iP(hone|ad|od)/.test(ua);
  const iPadOS = /Macintosh/.test(ua) && (navigator.maxTouchPoints ?? 0) > 1;
  return classic || iPadOS;
};

export const getRecordingProfile = (
  overrides?: Partial<RecordingProfile>,
): RecordingProfile => {
  const phone = isPhoneLike();
  const apple = isAppleMobileLike();
  const lean = phone || apple;
  const base: RecordingProfile = {
    isPhone: phone,
    appleMobile: apple,
    fps: lean ? 24 : 30,
    maxSeconds: lean ? PHONE_MAX_SECONDS : DESKTOP_MAX_SECONDS,
    maxEdge: lean ? 1280 : 1920,
    videoBitsPerSecond: lean ? 4_000_000 : 8_000_000,
    audioBitsPerSecond: 128_000,
    maxLiveVideos: lean ? 4 : 8,
    // Heap ceiling for accumulated chunks. 1080p30 @ 8 Mbps is ~60 MB/min and
    // final assembly briefly doubles it, so keep the phone well under a crash.
    maxBytes: lean ? 48 * 1024 * 1024 : 320 * 1024 * 1024,
    timesliceMs: DEFAULT_TIMESLICE_MS,
  };
  return overrides ? { ...base, ...overrides } : base;
};

/**
 * Clamp a composition size into the RECORDING budget and force EVEN dimensions.
 * H.264 encoders reject (or silently fudge) odd dimensions; a 1281px canvas is a
 * corrupt-file bug waiting to happen.
 */
export const fitRecordingSize = (
  width: number,
  height: number,
  profile: RecordingProfile = getRecordingProfile(),
): { width: number; height: number; scale: number } => {
  const w = Math.max(2, Math.round(width) || 2);
  const h = Math.max(2, Math.round(height) || 2);
  const longEdge = Math.max(w, h);
  const scale = longEdge > profile.maxEdge ? profile.maxEdge / longEdge : 1;
  const even = (n: number) => Math.max(2, Math.floor(n / 2) * 2);
  return { width: even(w * scale), height: even(h * scale), scale };
};

/** Rough file size for a take, for a UI hint and the memory warning. */
export const estimateRecordingBytes = (
  seconds: number,
  profile: RecordingProfile = getRecordingProfile(),
  withAudio = false,
): number => {
  const bps = profile.videoBitsPerSecond + (withAudio ? profile.audioBitsPerSecond : 0);
  return Math.round((bps / 8) * Math.max(0, seconds));
};

// =============================================================================
// CONTAINER / MIME
// =============================================================================

const codecLabelFor = (mime: string): string => {
  const m = /codecs\s*=\s*"?([^";]+)"?/i.exec(mime);
  const raw = (m?.[1] ?? '').toLowerCase();
  const has = (s: string) => raw.includes(s);
  const video =
    has('avc1') || has('h264') ? 'H.264'
      : has('hvc1') || has('hev1') ? 'HEVC'
        : has('vp9') ? 'VP9'
          : has('vp8') ? 'VP8'
            : has('av01') ? 'AV1'
              : '';
  const audio =
    has('mp4a') || has('aac') ? 'AAC'
      : has('opus') ? 'Opus'
        : has('vorbis') ? 'Vorbis'
          : '';
  if (video && audio) return `${video} + ${audio}`;
  if (video) return video;
  if (audio) return audio;
  // No codecs= parameter: infer the container's default pairing.
  if (/mp4|quicktime/i.test(mime)) return 'H.264 + AAC';
  if (/webm/i.test(mime)) return 'VP8/VP9 + Opus';
  return 'browser default';
};

/**
 * What the user is actually getting, and whether their OS will open it.
 * Call this with `recorder.mimeType` AFTER the take — the UA is allowed to pick
 * something other than what you asked for, and it usually does when you pass ''.
 */
export const describeContainer = (mimeType: string | null | undefined): ContainerInfo => {
  const mime = (mimeType || '').trim();
  const lower = mime.toLowerCase();
  let kind: ContainerKind = 'unknown';
  if (lower.includes('mp4')) kind = 'mp4';
  else if (lower.includes('matroska') || lower.includes('x-matroska')) kind = 'mkv';
  else if (lower.includes('webm')) kind = 'webm';
  else if (lower.includes('quicktime')) kind = 'mov';

  const codecLabel = codecLabelFor(mime);
  const appleNative = kind === 'mp4' || kind === 'mov';
  const extension =
    kind === 'mp4' ? 'mp4'
      : kind === 'webm' ? 'webm'
        : kind === 'mkv' ? 'mkv'
          : kind === 'mov' ? 'mov'
            : 'webm'; // UA default in practice; corrected after the take

  const warning =
    kind === 'webm' || kind === 'mkv' ? WEBM_WARNING
      : kind === 'unknown'
        ? 'The browser chose the container itself; if the file will not open, ' +
          'try recording in Safari or Chrome 126+ for an MP4.'
        : null;

  const label =
    kind === 'unknown'
      ? 'Browser default'
      : `${kind.toUpperCase()} - ${codecLabel}`;

  return { mime, kind, extension, codecLabel, label, appleNative, warning };
};

const canUseMediaRecorder = (): boolean =>
  hasDom() && typeof (window as unknown as { MediaRecorder?: unknown }).MediaRecorder === 'function';

const canTypeCheck = (): boolean =>
  canUseMediaRecorder() && typeof MediaRecorder.isTypeSupported === 'function';

const canCaptureCanvas = (): boolean =>
  hasDom() &&
  typeof HTMLCanvasElement !== 'undefined' &&
  typeof HTMLCanvasElement.prototype.captureStream === 'function';

/** First candidate this UA admits to supporting. '' is always acceptable. */
export const pickRecorderMime = (preferred?: string): string => {
  if (!canUseMediaRecorder()) return '';
  const list = preferred
    ? [preferred, ...RECORDER_MIME_CANDIDATES]
    : RECORDER_MIME_CANDIDATES;
  if (!canTypeCheck()) return '';
  for (const t of list) {
    if (t === '') return '';
    try {
      if (MediaRecorder.isTypeSupported(t)) return t;
    } catch { /* isTypeSupported is allowed to throw on junk input */ }
  }
  return '';
};

// =============================================================================
// AUDIO GRAPH
//
//   element -> [MediaElementSource] -> clipGain -\
//                                                 masterGain -> monitorGain ->
//                                                    monitorAnalyser -> speakers
//                                                             \
//                                                              -> recordGain ->
//                                                    recordAnalyser -> dest(s)
//
// The fan-out at masterGain IS the fix for the speaker-stealing trap. Both legs
// carry an analyser so `getAudioLevels()` can PROVE, at runtime, that signal is
// reaching the speakers and the recorder at the same instant.
// =============================================================================

interface ClipNodes {
  src: MediaElementAudioSourceNode;
  gain: GainNode;
}

/**
 * Derived from the method rather than written out, so this compiles on both the
 * pre-5.7 `Uint8Array` and the 5.7+ `Uint8Array<ArrayBuffer>` lib shapes.
 */
type TimeDomainBuffer = Parameters<AnalyserNode['getByteTimeDomainData']>[0];

interface AudioGraph {
  ctx: AudioContext;
  master: GainNode;
  monitor: GainNode;
  record: GainNode;
  monitorAnalyser: AnalyserNode;
  recordAnalyser: AnalyserNode;
  monitorBuf: TimeDomainBuffer;
  recordBuf: TimeDomainBuffer;
  /** Every element ever attached. Attachment is IRREVERSIBLE — see header. */
  clips: WeakMap<HTMLMediaElement, ClipNodes>;
  attachedCount: number;
  /** Every attach wired the speaker leg. False here is a bug, and visible. */
  monitorConnected: boolean;
}

let graph: AudioGraph | null = null;
let resumeHooked = false;

const audioCtor = (): (new (options?: AudioContextOptions) => AudioContext) | null => {
  if (!hasDom()) return null;
  const w = window as unknown as {
    AudioContext?: new (options?: AudioContextOptions) => AudioContext;
    webkitAudioContext?: new (options?: AudioContextOptions) => AudioContext;
  };
  // Unprefixed since Safari 14.1; the prefix is still needed for 6..14.
  return w.AudioContext || w.webkitAudioContext || null;
};

export const isAudioMixingSupported = (): boolean => {
  const Ctor = audioCtor();
  if (!Ctor) return false;
  return typeof Ctor.prototype.createMediaStreamDestination === 'function' &&
    typeof Ctor.prototype.createMediaElementSource === 'function';
};

/**
 * iOS suspends the context on backgrounding, phone calls and Siri, and never
 * resumes it by itself. Hooked once, globally.
 */
const hookAutoResume = (g: AudioGraph) => {
  if (resumeHooked || !hasDom()) return;
  resumeHooked = true;
  const kick = () => { void g.ctx.resume().catch(() => { /* needs a gesture */ }); };
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) kick();
  });
  try { g.ctx.onstatechange = () => { if (g.ctx.state === 'suspended') kick(); }; }
  catch { /* onstatechange is optional */ }
};

const ensureGraph = (): AudioGraph | null => {
  if (graph) return graph;
  const Ctor = audioCtor();
  if (!Ctor) return null;
  try {
    const ctx = new Ctor();
    const master = ctx.createGain();
    const monitor = ctx.createGain();
    const record = ctx.createGain();
    const monitorAnalyser = ctx.createAnalyser();
    const recordAnalyser = ctx.createAnalyser();
    monitorAnalyser.fftSize = 256;
    recordAnalyser.fftSize = 256;

    // THE FAN-OUT. One node legally drives many outputs; this is the whole fix.
    master.connect(monitor);
    master.connect(record);
    monitor.connect(monitorAnalyser);
    monitorAnalyser.connect(ctx.destination); // <- SPEAKERS. Never remove.
    record.connect(recordAnalyser);           // -> per-take destinations

    graph = {
      ctx,
      master,
      monitor,
      record,
      monitorAnalyser,
      recordAnalyser,
      monitorBuf: new Uint8Array(monitorAnalyser.fftSize),
      recordBuf: new Uint8Array(recordAnalyser.fftSize),
      clips: new WeakMap<HTMLMediaElement, ClipNodes>(),
      attachedCount: 0,
      monitorConnected: true,
    };
    hookAutoResume(graph);
    return graph;
  } catch {
    graph = null;
    return null;
  }
};

const normalizeSources = (
  sources: Array<HTMLVideoElement | RecordSource> | undefined,
): RecordSource[] => {
  if (!sources || !sources.length) return [];
  const out: RecordSource[] = [];
  const seen = new Set<HTMLMediaElement>();
  for (const s of sources) {
    if (!s) continue;
    const rec: RecordSource = 'el' in (s as RecordSource)
      ? (s as RecordSource)
      : { el: s as HTMLVideoElement };
    if (!rec.el || typeof (rec.el as HTMLMediaElement).play !== 'function') continue;
    if (seen.has(rec.el)) continue; // a duplicate would hit the InvalidStateError path
    seen.add(rec.el);
    out.push(rec);
  }
  return out;
};

/**
 * Wire ONE element into the mix. Idempotent by WeakMap: calling it twice is safe,
 * calling createMediaElementSource twice is not (InvalidStateError, no detach).
 */
const attachSource = (g: AudioGraph, source: RecordSource): string | null => {
  const el = source.el;
  let nodes = g.clips.get(el);
  if (!nodes) {
    try {
      const src = g.ctx.createMediaElementSource(el);
      const gain = g.ctx.createGain();
      src.connect(gain);
      gain.connect(g.master); // master fans out to speakers AND recorder
      nodes = { src, gain };
      g.clips.set(el, nodes);
      g.attachedCount += 1;
    } catch (e) {
      return errText(e);
    }
  }
  // Once in the graph, `.muted`/`.volume` cut the GRAPH feed too — so they are
  // pinned open HERE (inside the gesture) and never used as a volume control
  // again; from now on level lives exclusively in `gain`. Re-asserting on every
  // enable is deliberate: it self-heals an element something else muted.
  el.muted = false;
  el.defaultMuted = false;
  el.volume = 1;
  const vol = clamp(source.volume ?? 1, 0, 1);
  try { nodes.gain.gain.value = vol; } catch { /* value is always settable */ }
  return null;
};

export interface EnableSoundResult {
  ok: boolean;
  attached: number;
  played: number;
  failed: Array<{ id: string; reason: string }>;
  contextState: AudioContextState | 'unavailable';
  /** The speaker leg is wired. Always true for a live graph; surfaced anyway. */
  monitorConnected: boolean;
  reason: string | null;
  advice: string | null;
}

/**
 * THE GESTURE ENTRY POINT. Call this synchronously from a click/tap handler —
 * iOS requires the AudioContext be created or resumed inside a real gesture, and
 * audible playback needs one too. One tap grants sound AND starts the clips.
 */
export const enableSound = async (
  sources: Array<HTMLVideoElement | RecordSource>,
  opts?: { play?: boolean; masterVolume?: number },
): Promise<EnableSoundResult> => {
  const list = normalizeSources(sources);
  // LAZY BY CONTRACT: never construct an AudioContext for nothing. On iOS a live
  // context takes over the audio session and can duck whatever else is playing.
  if (list.length === 0) {
    return {
      ok: false, attached: 0, played: 0, failed: [],
      contextState: graph ? graph.ctx.state : 'unavailable',
      monitorConnected: !!graph,
      reason: 'No video clips to take sound from.',
      advice: 'Add a clip to the collage, then turn sound on.',
    };
  }
  const g = ensureGraph();
  if (!g) {
    return {
      ok: false, attached: 0, played: 0, failed: [],
      contextState: 'unavailable', monitorConnected: false,
      reason: 'Web Audio is not available in this browser.',
      advice: 'The collage still records and plays without sound.',
    };
  }

  // resume() FIRST and inside the gesture: a context created 'suspended' that is
  // resumed later, outside a gesture, silently produces nothing on iOS.
  // Deadlined — a denied resume can simply never settle.
  try {
    const r = g.ctx.resume();
    if (r && typeof r.then === 'function') await settleWithin(r, RESUME_TIMEOUT_MS);
  } catch { /* may already be running */ }

  const failed: Array<{ id: string; reason: string }> = [];
  let attached = 0;
  for (let i = 0; i < list.length; i++) {
    const reason = attachSource(g, list[i]);
    if (reason) failed.push({ id: list[i].id ?? `clip-${i}`, reason });
    else attached += 1;
  }

  try { g.master.gain.value = clamp(opts?.masterVolume ?? 1, 0, 1); } catch { /* ignore */ }
  try { g.monitor.gain.value = 1; } catch { /* ignore */ }
  try { g.record.gain.value = 1; } catch { /* ignore */ }

  let played = 0;
  if (opts?.play !== false) {
    // In PARALLEL and each DEADLINED, so N clips cost one timeout, not N — and a
    // clip whose play() never settles cannot wedge the take before it starts.
    const outcomes = await Promise.all(list.map(async (s, i) => {
      const id = s.id ?? `clip-${i}`;
      try {
        const p = s.el.play();
        // ALWAYS check the promise: a rejection is how autoplay denial surfaces.
        if (!p || typeof p.then !== 'function') return { id, res: { kind: 'ok' } as Settled };
        return { id, res: await settleWithin(p, PLAY_TIMEOUT_MS) };
      } catch (e) {
        return { id, res: { kind: 'error', reason: errText(e) } as Settled };
      }
    }));
    for (const o of outcomes) {
      if (o.res.kind === 'ok') played += 1;
      else if (o.res.kind === 'error') failed.push({ id: o.id, reason: o.res.reason });
      else failed.push({ id: o.id, reason: 'Playback did not start in time.' });
    }
  }

  const state: AudioContextState = g.ctx.state;
  const ok = attached > 0 && state === 'running';
  return {
    ok,
    attached,
    played,
    failed,
    contextState: state,
    monitorConnected: g.monitorConnected,
    reason: ok
      ? null
      : state !== 'running'
        ? 'The browser kept audio suspended — tap the sound button again.'
        : list.length === 0
          ? 'No video clips to take sound from.'
          : 'None of the clips could be wired for sound.',
    advice: ok ? null : 'You can still record; the take will be silent.',
  };
};

/**
 * Master mute. NOTE: we deliberately do NOT touch `el.muted` — on an attached
 * element that would also cut the graph feed, silencing the recording as well.
 */
export const setMasterVolume = (v: number): boolean => {
  if (!graph) return false;
  try { graph.master.gain.value = clamp(v, 0, 1); return true; } catch { return false; }
};

/** Silence the speakers WITHOUT silencing the recording. */
export const setMonitorMuted = (muted: boolean): boolean => {
  if (!graph) return false;
  try { graph.monitor.gain.value = muted ? 0 : 1; return true; } catch { return false; }
};

/** Record silence while still monitoring. */
export const setRecordMuted = (muted: boolean): boolean => {
  if (!graph) return false;
  try { graph.record.gain.value = muted ? 0 : 1; return true; } catch { return false; }
};

/** Per-clip level. The ONLY legal way to change one clip's loudness. */
export const setClipVolume = (el: HTMLMediaElement, v: number): boolean => {
  if (!graph) return false;
  const nodes = graph.clips.get(el);
  if (!nodes) return false;
  try { nodes.gain.gain.value = clamp(v, 0, 1); return true; } catch { return false; }
};

const rms = (analyser: AnalyserNode, buf: TimeDomainBuffer): number => {
  try {
    // Preallocated buffer: this is safe to call from a rAF/meter loop.
    analyser.getByteTimeDomainData(buf);
    let sum = 0;
    for (let i = 0; i < buf.length; i++) {
      const d = (buf[i] - 128) / 128;
      sum += d * d;
    }
    return Math.sqrt(sum / buf.length);
  } catch {
    return 0;
  }
};

/**
 * Live RMS on BOTH legs. This is the runtime proof that the speaker-stealing
 * trap is fixed: during a take with sound, `monitor` and `record` are both > 0.
 * A monitor of 0 while record is > 0 is exactly the silent-speakers bug.
 */
export const getAudioLevels = (): { monitor: number; record: number; attached: number } => {
  if (!graph) return { monitor: 0, record: 0, attached: 0 };
  return {
    monitor: rms(graph.monitorAnalyser, graph.monitorBuf),
    record: rms(graph.recordAnalyser, graph.recordBuf),
    attached: graph.attachedCount,
  };
};

/** Inspectable wiring facts, for a dev panel or an assertion in a test. */
export const describeAudioGraph = (): {
  live: boolean;
  state: AudioContextState | 'unavailable';
  attached: number;
  monitorConnected: boolean;
  masterVolume: number;
  monitorVolume: number;
  recordVolume: number;
} => {
  if (!graph) {
    return {
      live: false, state: 'unavailable', attached: 0, monitorConnected: false,
      masterVolume: 0, monitorVolume: 0, recordVolume: 0,
    };
  }
  return {
    live: true,
    state: graph.ctx.state,
    attached: graph.attachedCount,
    monitorConnected: graph.monitorConnected,
    masterVolume: graph.master.gain.value,
    monitorVolume: graph.monitor.gain.value,
    recordVolume: graph.record.gain.value,
  };
};

/**
 * Wind the graph down. It does NOT close the context once anything has been
 * attached: a MediaElementSourceNode binds its element FOREVER, so closing the
 * context would leave those clips permanently unable to make sound (a second
 * createMediaElementSource, even on a new context, throws InvalidStateError).
 * Muting is the only safe teardown.
 */
export const releaseAudioGraph = (): void => {
  if (!graph) return;
  try { graph.master.gain.value = 0; } catch { /* ignore */ }
  if (graph.attachedCount === 0) {
    try { void graph.ctx.close(); } catch { /* ignore */ }
    graph = null;
  }
};

interface RecordingSink {
  tracks: MediaStreamTrack[];
  release: () => void;
}

/**
 * A FRESH MediaStreamAudioDestinationNode per take. Deliberate: stopping a track
 * ends it permanently, so a shared destination would work exactly once.
 */
const openRecordingSink = (): RecordingSink | null => {
  const g = graph;
  if (!g || g.attachedCount === 0) return null;
  try {
    const dest = g.ctx.createMediaStreamDestination();
    g.recordAnalyser.connect(dest);
    const tracks = dest.stream.getAudioTracks();
    return {
      tracks,
      release: () => {
        try { g.recordAnalyser.disconnect(dest); } catch { /* already gone */ }
        for (const t of tracks) { try { t.stop(); } catch { /* ignore */ } }
      },
    };
  } catch {
    return null;
  }
};

// =============================================================================
// CAPABILITY DETECTION
// =============================================================================

interface DryRun {
  pass: boolean;
  reason: string | null;
  mime: string;
  bytes: number;
  chunks: number;
  ms: number;
}

let dryRunCache: DryRun | null = null;
let dryRunInFlight: Promise<DryRun> | null = null;

/**
 * The 400 ms take that answers the iOS question no compat table can. Draws a
 * changing 32x32 canvas (a static canvas may emit no frames at all), records it,
 * and demands BOTH >= 1 `dataavailable` AND a non-empty assembled blob.
 * Every wait is deadlined, because the failure mode we are hunting is a hang.
 */
const runDryRun = async (): Promise<DryRun> => {
  const t0 = nowMs();
  const fail = (reason: string, mime = ''): DryRun =>
    ({ pass: false, reason, mime, bytes: 0, chunks: 0, ms: nowMs() - t0 });

  if (!canUseMediaRecorder()) return fail('MediaRecorder is not available.');
  if (!canCaptureCanvas()) return fail('This browser cannot capture a canvas as video.');

  const canvas = document.createElement('canvas');
  canvas.width = 32;
  canvas.height = 32;
  const ctx2d = canvas.getContext('2d');
  if (!ctx2d) return fail('No 2D canvas context.');

  const mime = pickRecorderMime();
  let stream: MediaStream | null = null;
  let rec: MediaRecorder | null = null;
  let painter: ReturnType<typeof setInterval> | null = null;

  try {
    stream = canvas.captureStream(10);
    const vTrack = stream.getVideoTracks()[0];
    if (!vTrack) return fail('Canvas capture produced no video track.', mime);

    try {
      rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
    } catch (e) {
      return fail(`The recorder rejected every format (${errText(e)}).`, mime);
    }

    const chunks: Blob[] = [];
    let fired = 0;
    rec.ondataavailable = (e: BlobEvent) => {
      if (e.data && e.data.size > 0) { chunks.push(e.data); fired += 1; }
    };
    let recError: string | null = null;
    rec.onerror = (e: ErrorEvent) => {
      recError = errText((e as ErrorEvent & { error?: unknown }).error ?? e);
    };
    const stopped = new Promise<void>((resolve) => { rec!.onstop = () => resolve(); });

    try { rec.start(PROBE_TIMESLICE_MS); }
    catch (e) { return fail(`The recorder would not start (${errText(e)}).`, mime); }

    // Keep the canvas DIRTY: an unchanged canvas can legally emit zero frames.
    let flip = 0;
    painter = setInterval(() => {
      flip ^= 1;
      ctx2d.fillStyle = flip ? '#ffffff' : '#101010';
      ctx2d.fillRect(0, 0, 32, 32);
    }, PROBE_DRAW_MS);

    await sleep(PROBE_RECORD_MS);
    clearInterval(painter);
    painter = null;

    try { rec.requestData(); } catch { /* not all states allow it */ }
    try { rec.stop(); } catch { /* already inactive */ }
    // iOS 15 sometimes never fires onstop — do not wait forever for it.
    await Promise.race([stopped, sleep(PROBE_STOP_MS)]);

    const type = rec.mimeType || mime || '';
    const blob = new Blob(chunks, type ? { type } : undefined);
    if (recError) return fail(`The recorder failed: ${recError}`, type);
    if (fired === 0) return fail('The recorder produced no data.', type);
    if (blob.size === 0) return fail('The recorder produced an empty file.', type);

    return { pass: true, reason: null, mime: type, bytes: blob.size, chunks: fired, ms: nowMs() - t0 };
  } catch (e) {
    return fail(errText(e), mime);
  } finally {
    if (painter) clearInterval(painter);
    try { rec?.stream?.getTracks().forEach((t) => t.stop()); } catch { /* ignore */ }
    try { stream?.getTracks().forEach((t) => t.stop()); } catch { /* ignore */ }
    canvas.width = 0;
    canvas.height = 0;
  }
};

const buildSupport = (probe: DryRun | null, profile: RecordingProfile): VideoExportSupport => {
  const apis = {
    mediaRecorder: canUseMediaRecorder(),
    isTypeSupported: canTypeCheck(),
    canvasCapture: canCaptureCanvas(),
    audioContext: !!audioCtor(),
    streamDestination: isAudioMixingSupported(),
  };
  const apisPresent = apis.mediaRecorder && apis.canvasCapture;
  // After a probe, believe the FILE the device produced over anything we asked for.
  const mimeType = probe?.pass && probe.mime ? probe.mime : pickRecorderMime();
  const container = describeContainer(mimeType);

  let level: RecordSupportLevel;
  let reason: string | null;
  if (!apisPresent) {
    level = 'unsupported';
    reason = !apis.mediaRecorder
      ? 'This browser has no MediaRecorder.'
      : 'This browser cannot capture a canvas as video.';
  } else if (probe && !probe.pass) {
    level = 'unsupported';
    reason = probe.reason;
  } else if (probe && probe.pass) {
    level = 'ready';
    reason = null;
  } else {
    level = 'likely';
    reason = null;
  }

  const supported = level !== 'unsupported';
  const audioSupported = supported && apis.streamDestination;
  const seconds = profile.maxSeconds;
  const label = !supported
    ? 'Video recording unavailable'
    : `${container.label}, up to ${seconds}s${audioSupported ? ' with sound' : ' (no sound)'}`;

  return {
    level,
    supported,
    probed: !!probe,
    apis,
    mimeType,
    container,
    audio: {
      supported: audioSupported,
      reason: audioSupported ? null : 'This browser cannot mix clip audio into a recording.',
    },
    profile,
    reason,
    advice: supported ? container.warning : UNSUPPORTED_ADVICE,
    label,
  };
};

/**
 * SYNCHRONOUS, no side effects — safe on first paint. Returns level 'likely'
 * when the APIs exist but the device has not proved itself yet. Do not ship a
 * record button on 'likely' alone if you can afford the half-second probe.
 */
export const inspectVideoExportSupport = (
  profile: RecordingProfile = getRecordingProfile(),
): VideoExportSupport => buildSupport(dryRunCache, profile);

/**
 * Runs the dry-run take ONCE per session and caches it. ~0.5 s. This is the only
 * honest answer to "does iOS Safari support this" — see the header.
 */
export const probeVideoExportSupport = async (
  opts?: { force?: boolean; profile?: RecordingProfile },
): Promise<VideoExportSupport> => {
  const profile = opts?.profile ?? getRecordingProfile();
  if (opts?.force) { dryRunCache = null; dryRunInFlight = null; }
  if (!dryRunCache) {
    if (!dryRunInFlight) {
      dryRunInFlight = runDryRun().then((r) => { dryRunCache = r; dryRunInFlight = null; return r; });
    }
    try { await dryRunInFlight; }
    catch (e) { dryRunCache = { pass: false, reason: errText(e), mime: '', bytes: 0, chunks: 0, ms: 0 }; }
  }
  return buildSupport(dryRunCache, profile);
};

// =============================================================================
// VALIDATION
// =============================================================================

type Validation = { verdict: 'pass' | 'fail' | 'unverified'; reason: string | null; hasDuration: boolean };

/**
 * Decode the take back before calling it a success. Reuses `probeVideo`, which
 * already carries the Safari-safe element setup and the fMP4 Infinity-duration
 * recovery.
 *
 * KEYED ON DIMENSIONS, NOT DURATION. Every browser recorder writes a fragmented
 * container with no duration in the header, so `probe.error` is routinely
 * "could not determine the video length" on a perfectly good file. Failing on
 * that would throw away every take.
 */
const validateRecording = async (
  blob: Blob,
  mime: string,
  extension: string,
  timeoutMs: number,
): Promise<Validation> => {
  if (typeof File !== 'function') {
    return { verdict: 'unverified', reason: 'No File constructor to test with.', hasDuration: false };
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), Math.max(500, timeoutMs));
  try {
    const file = new File([blob], `take.${extension}`, { type: mime || blob.type || 'video/mp4' });
    const probe = await probeVideo(file, controller.signal);
    if (probe.width > 0 && probe.height > 0) {
      return { verdict: 'pass', reason: null, hasDuration: probe.duration > 0 };
    }
    return {
      verdict: 'fail',
      reason: probe.error || 'The recorded file has no readable video track.',
      hasDuration: false,
    };
  } catch (e) {
    // A timeout is NOT a failure: never discard the user's take because our
    // check was slow. Say "unverified" and hand the file over anyway.
    if (isAbortError(e)) {
      return { verdict: 'unverified', reason: 'The playback check timed out.', hasDuration: false };
    }
    return { verdict: 'unverified', reason: errText(e), hasDuration: false };
  } finally {
    clearTimeout(timer);
  }
};

// =============================================================================
// FILENAME / DOWNLOAD
// =============================================================================

const stamp = (): string => {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
};

/** A name the OS will accept and an extension it will actually open. */
export const suggestFilename = (base: string, mimeType: string): string => {
  const safe = (base || 'collage')
    .replace(/[^\w.-]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 48) || 'collage';
  return `${safe}-${stamp()}.${describeContainer(mimeType).extension}`;
};

/** Save a finished take. Revoking too early breaks the download on Safari. */
export const downloadRecording = (result: RecordSuccess): void => {
  if (!hasDom() || !result?.url) return;
  const a = document.createElement('a');
  a.href = result.url;
  a.download = result.filename;
  a.rel = 'noopener';
  a.style.cssText = 'position:fixed;left:-9999px;top:0';
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { try { a.remove(); } catch { /* ignore */ } }, 1000);
};

/** Give back the object URL when the UI is done previewing the take. */
export const revokeRecording = (result: RecordSuccess | null | undefined): void => {
  if (!result?.url) return;
  try { URL.revokeObjectURL(result.url); } catch { /* already gone */ }
};

// =============================================================================
// RECORD
// =============================================================================

const failure = (
  code: RecordFailureCode,
  message: string,
  advice: string | null,
  cause: string | null,
  warnings: string[],
  partial: RecordFailure['partial'] = null,
): RecordFailure => ({ ok: false, code, message, advice, cause, partial, warnings });

/**
 * Record `canvas` for up to `seconds`, mixing in the audio of `sources`.
 *
 * NEVER THROWS: every outcome is a typed `RecordResult`.
 *
 * THE CALLER MUST KEEP DRAWING. `captureStream` samples a canvas that changes;
 * a canvas nobody paints can legally emit a single frame or none at all. Keep
 * the live draw loop running for the whole take.
 *
 * Call it from a user gesture when `withAudio` is true — one tap then both
 * grants audio and starts the take.
 */
export const record = async (
  canvas: HTMLCanvasElement,
  options: RecordOptions = {},
): Promise<RecordResult> => {
  const warnings: string[] = [];
  const profile = getRecordingProfile();
  const onProgress = options.onProgress;

  let phase: RecordPhase = 'preparing';
  let bytes = 0;
  let chunkCount = 0;
  let startedAt = 0;
  let totalMs = Math.round(clamp(options.seconds ?? profile.maxSeconds, 1, profile.maxSeconds) * 1000);
  const withAudioRequested = options.withAudio === true;
  const fps = Math.round(clamp(options.fps ?? profile.fps, 1, 60));
  let audioTrackCount = 0;

  const emit = (label: string, ratioOverride?: number) => {
    if (!onProgress) return;
    const elapsed = startedAt ? nowMs() - startedAt : 0;
    const ratio = ratioOverride !== undefined
      ? clamp(ratioOverride, 0, 1)
      : totalMs > 0 ? clamp(elapsed / totalMs, 0, 1) : 0;
    try {
      onProgress({
        phase,
        ratio,
        elapsedMs: Math.round(elapsed),
        remainingMs: Math.max(0, Math.round(totalMs - elapsed)),
        bytes,
        chunks: chunkCount,
        label,
        fps,
        withAudio: audioTrackCount > 0,
      });
    } catch { /* a UI callback must never break a take */ }
  };

  // The caller's own stream, when it owns the media graph. See RecordOptions.stream.
  const externalStream = options.stream ?? null;

  try {
    // --- 0. canvas sanity -----------------------------------------------------
    // With an external stream the canvas is only a size reference — the frames
    // are already flowing through a track we did not create, so this browser's
    // captureStream support is no longer our question to ask.
    if (!canvas || typeof canvas.getContext !== 'function' ||
        (!externalStream && typeof (canvas as HTMLCanvasElement).captureStream !== 'function')) {
      return failure('bad-canvas', 'There is nothing to record yet.',
        'Add some images or clips, then try again.', 'canvas missing captureStream', warnings);
    }
    if (!canvas.width || !canvas.height) {
      return failure('bad-canvas', 'The collage canvas is empty.',
        'Add some images or clips, then try again.', `size ${canvas.width}x${canvas.height}`, warnings);
    }
    if (canvas.width % 2 || canvas.height % 2) {
      // H.264 wants even dimensions; encoders fudge or refuse otherwise.
      warnings.push('The canvas has an odd pixel dimension — some encoders round it, ' +
        'which can shift the frame by a pixel.');
    }

    // --- 1. capability --------------------------------------------------------
    phase = options.skipProbe ? 'preparing' : 'probing';
    emit(options.skipProbe ? 'Preparing…' : 'Checking this device…', 0);
    const support = options.skipProbe
      ? inspectVideoExportSupport(profile)
      : await probeVideoExportSupport({ profile });
    if (!support.supported) {
      phase = 'failed';
      emit('Not supported', 0);
      return failure('unsupported', UNSUPPORTED_MESSAGE, UNSUPPORTED_ADVICE,
        support.reason, warnings);
    }

    if (options.signal?.aborted) {
      phase = 'cancelled';
      emit('Cancelled', 0);
      return failure('aborted', 'Recording cancelled.', null, null, warnings);
    }

    // --- 2. duration cap ------------------------------------------------------
    const requestedSeconds = options.seconds ?? profile.maxSeconds;
    const cappedSeconds = clamp(requestedSeconds, 1, profile.maxSeconds);
    const capped = cappedSeconds < requestedSeconds;
    totalMs = Math.round(cappedSeconds * 1000);
    if (capped) {
      warnings.push(
        `Recording is capped at ${profile.maxSeconds}s on this device` +
        (profile.appleMobile || profile.isPhone
          ? ' — longer takes crash mobile browsers mid-save.'
          : '.'),
      );
    }

    // --- 3. audio (lazily; a silent take never builds the graph) --------------
    phase = 'arming';
    emit('Getting ready…', 0);
    const sources = normalizeSources(options.sources);
    let sink: RecordingSink | null = null;
    let attachedSources = 0;
    let monitorConnected = false;

    if (externalStream) {
      // The caller already mixed its own audio into the stream. Touching
      // `sources` here would call createMediaElementSource a SECOND time on
      // elements the caller has already attached — InvalidStateError, and the
      // clip is silenced for the rest of the session. Do nothing.
      if (sources.length > 0) {
        warnings.push('Ignoring the clip list: the caller supplied its own recording stream.');
      }
    } else if (withAudioRequested && sources.length > 0) {
      if (!support.audio.supported) {
        warnings.push('This browser cannot mix clip audio into a recording — the take will be silent.');
      } else {
        const sound = await enableSound(sources, { play: true });
        attachedSources = sound.attached;
        monitorConnected = sound.monitorConnected;
        if (!sound.ok && sound.reason) {
          warnings.push(`${sound.reason} The take will be silent.`);
        } else {
          sink = openRecordingSink();
          if (!sink || sink.tracks.length === 0) {
            sink?.release();
            sink = null;
            warnings.push('Audio could not be routed into the recording — the take will be silent.');
          }
        }
        if (sound.failed.length) {
          warnings.push(`${sound.failed.length} clip(s) could not contribute sound.`);
        }
      }
    } else if (withAudioRequested && sources.length === 0) {
      warnings.push('No playing clips to take sound from — the take will be silent.');
    }

    // --- 4. streams -----------------------------------------------------------
    let stream: MediaStream;
    if (externalStream) {
      stream = externalStream;
    } else {
      try {
        stream = canvas.captureStream(fps);
      } catch (e) {
        sink?.release();
        phase = 'failed';
        emit('Failed', 0);
        return failure('unsupported', UNSUPPORTED_MESSAGE, UNSUPPORTED_ADVICE, errText(e), warnings);
      }
    }
    const vTrack = stream.getVideoTracks()[0];
    if (!vTrack) {
      sink?.release();
      phase = 'failed';
      emit('Failed', 0);
      return failure('no-track', UNSUPPORTED_MESSAGE, UNSUPPORTED_ADVICE,
        externalStream
          ? 'the supplied stream carries no video track'
          : 'captureStream returned no video track', warnings);
    }

    const audioTracks = externalStream ? externalStream.getAudioTracks() : (sink?.tracks ?? []);
    audioTrackCount = audioTracks.length;
    // CONSTRUCTOR, not addTrack(): Firefox < 58 silently omitted addTrack'd
    // tracks from the recording, and the constructor form has no such history.
    const mixed = new MediaStream([vTrack, ...audioTracks]);

    /**
     * Stop ONLY what we created. An external stream's tracks belong to the
     * caller, which caches and reuses them (`Stage.captureStream()` hands back
     * the same MediaStream on every call) — stopping a track here would end it
     * PERMANENTLY and the caller's second take would record a dead surface.
     */
    const releaseOwnTracks = (): void => {
      if (!externalStream) {
        try { vTrack.stop(); } catch { /* ignore */ }
        try { stream.getVideoTracks().forEach((t) => t.stop()); } catch { /* ignore */ }
      }
      sink?.release();
    };

    // --- 5. recorder ----------------------------------------------------------
    const wanted = options.mimeType ? pickRecorderMime(options.mimeType) : support.mimeType;
    const recOpts: MediaRecorderOptions = {
      videoBitsPerSecond: options.videoBitsPerSecond ?? profile.videoBitsPerSecond,
      audioBitsPerSecond: options.audioBitsPerSecond ?? profile.audioBitsPerSecond,
    };
    let rec: MediaRecorder;
    try {
      rec = new MediaRecorder(mixed, wanted ? { ...recOpts, mimeType: wanted } : recOpts);
    } catch (firstErr) {
      // One retry with no constraints at all before giving up.
      try {
        rec = new MediaRecorder(mixed);
        warnings.push('This browser refused the requested video format and chose its own.');
      } catch (e) {
        releaseOwnTracks();
        phase = 'failed';
        emit('Failed', 0);
        return failure('no-mime',
          "This browser can't write a video file from the canvas.",
          UNSUPPORTED_ADVICE, `${errText(firstErr)} / ${errText(e)}`, warnings);
      }
    }

    // --- 6. wiring ------------------------------------------------------------
    const chunks: Blob[] = [];
    const maxBytes = options.maxBytes ?? profile.maxBytes;
    let recorderError: string | null = null;

    let ticker: ReturnType<typeof setInterval> | null = null;
    let capTimer: ReturnType<typeof setTimeout> | null = null;

    // The take resolves WITH its reason rather than writing a shared flag: the
    // outcome is a value, so no code path can read a stale one.
    const done = new Promise<StopReason>((resolve) => {
      let reason: StopReason = 'complete';
      let settled = false;
      let stopping = false;

      const settle = () => {
        if (settled) return;
        settled = true;
        resolve(reason);
      };

      const requestStop = (r: StopReason) => {
        if (stopping) return;
        stopping = true;
        reason = r;
        try { rec.requestData(); } catch { /* not every state allows it */ }
        try {
          if (rec.state !== 'inactive') rec.stop();
          else settle();
        } catch {
          settle(); // stop() threw: assemble from whatever we have
        }
        // iOS can freeze or simply never fire onstop. Never wait forever.
        setTimeout(settle, STOP_GRACE_MS);
      };

      rec.ondataavailable = (e: BlobEvent) => {
        if (e.data && e.data.size > 0) {
          chunks.push(e.data);
          chunkCount += 1;
          bytes += e.data.size;
          if (bytes >= maxBytes) requestStop('memory');
        }
      };
      rec.onstop = () => settle();
      rec.onerror = (e: ErrorEvent) => {
        recorderError = errText((e as ErrorEvent & { error?: unknown }).error ?? e);
        requestStop('error');
      };
      vTrack.addEventListener('ended', () => requestStop('track-ended'), { once: true });

      const onAbort = () => requestStop('aborted');
      if (options.signal) {
        if (options.signal.aborted) { setTimeout(onAbort, 0); }
        else options.signal.addEventListener('abort', onAbort, { once: true });
      }

      // HARD auto-stop. Never rely on the user to stop in time; an unbounded
      // media operation is the same failure class as the MAX-export hang.
      capTimer = setTimeout(() => requestStop('complete'), totalMs);
    });

    // --- 7. go ----------------------------------------------------------------
    try {
      rec.start(options.timesliceMs ?? profile.timesliceMs); // TIMESLICE MANDATORY
    } catch (e) {
      if (capTimer) clearTimeout(capTimer);
      releaseOwnTracks();
      phase = 'failed';
      emit('Failed', 0);
      return failure('start-failed', "This browser wouldn't start recording.",
        UNSUPPORTED_ADVICE, errText(e), warnings);
    }

    startedAt = nowMs();
    phase = 'recording';
    emit('Recording…', 0);
    ticker = setInterval(() => {
      if (phase === 'recording') emit('Recording…');
    }, PROGRESS_TICK_MS);

    const stopReason: StopReason = await done;

    if (ticker) clearInterval(ticker);
    if (capTimer) clearTimeout(capTimer);
    phase = 'finalizing';
    emit('Finishing…', 1);

    const durationMs = Math.max(0, Math.round(nowMs() - startedAt));

    // --- 8. teardown ----------------------------------------------------------
    // Stop the CANVAS track only; the audio tracks belong to the per-take sink,
    // which releases (and stops) them itself. An external stream is left intact
    // for its owner — see releaseOwnTracks.
    releaseOwnTracks();

    const actualMime = rec.mimeType || wanted || '';
    const container = describeContainer(actualMime);

    // --- 9. verdicts ----------------------------------------------------------
    if (stopReason === 'aborted') {
      phase = 'cancelled';
      emit('Cancelled', 1);
      const partial = options.keepPartialOnFailure && chunks.length
        ? { blob: new Blob(chunks, actualMime ? { type: actualMime } : undefined), sizeBytes: bytes, chunks: chunkCount, mimeType: actualMime }
        : null;
      chunks.length = 0;
      return failure('aborted', 'Recording cancelled.', null, null, warnings, partial);
    }

    if (stopReason === 'memory') {
      warnings.push('Recording stopped early to stay inside this device’s memory budget.');
    }
    if (stopReason === 'track-ended') {
      warnings.push('The canvas stopped feeding frames, so the take ended early.');
    }

    if (chunks.length === 0 || bytes === 0) {
      phase = 'failed';
      emit('Failed', 1);
      return failure('empty',
        'The recording came out empty.',
        recorderError
          ? UNSUPPORTED_ADVICE
          : 'Keep the collage visible while recording — a hidden or paused canvas produces no frames.',
        recorderError ?? `stopReason=${stopReason}`, warnings);
    }

    const blob = new Blob(chunks, actualMime ? { type: actualMime } : undefined);
    chunks.length = 0; // let the heap reclaim the fragments immediately

    if (recorderError) {
      warnings.push('The recorder reported a problem partway through; the file may be short.');
    }

    const floor = MIN_BYTES_PER_SECOND * Math.max(1, durationMs / 1000);
    if (blob.size < floor) {
      phase = 'failed';
      emit('Failed', 1);
      return failure('too-small',
        'The recording came out too small to be a real video.',
        UNSUPPORTED_ADVICE,
        `size=${blob.size} floor=${Math.round(floor)}`,
        warnings,
        options.keepPartialOnFailure
          ? { blob, sizeBytes: blob.size, chunks: chunkCount, mimeType: actualMime }
          : null);
    }

    // --- 10. prove it plays ---------------------------------------------------
    let validated: RecordSuccess['validated'] = 'skipped';
    if (options.validate !== false) {
      phase = 'validating';
      emit('Checking playback…', 1);
      const v = await validateRecording(
        blob, actualMime, container.extension,
        options.validateTimeoutMs ?? DEFAULT_VALIDATE_TIMEOUT_MS,
      );
      if (v.verdict === 'fail') {
        phase = 'failed';
        emit('Failed', 1);
        return failure('undecodable',
          "The recording finished but this browser can't play it back.",
          UNSUPPORTED_ADVICE, v.reason, warnings,
          options.keepPartialOnFailure
            ? { blob, sizeBytes: blob.size, chunks: chunkCount, mimeType: actualMime }
            : null);
      }
      validated = v.verdict === 'pass' ? 'pass' : 'unverified';
      if (v.verdict === 'pass' && !v.hasDuration) warnings.push(NO_DURATION_WARNING);
      if (v.verdict === 'unverified' && v.reason) {
        warnings.push(`Playback check did not finish (${v.reason}) — the file was kept anyway.`);
      }
    }

    if (container.warning) warnings.push(container.warning);

    phase = 'done';
    emit('Done', 1);

    return {
      ok: true,
      blob,
      url: URL.createObjectURL(blob),
      filename: suggestFilename(options.filenameBase ?? 'collage', actualMime),
      container,
      mimeType: actualMime,
      durationMs,
      sizeBytes: blob.size,
      chunks: chunkCount,
      fps,
      audio: {
        requested: withAudioRequested,
        recorded: audioTrackCount > 0,
        tracks: audioTrackCount,
        sources: attachedSources,
        monitorConnected,
      },
      validated,
      capped,
      warnings,
    };
  } catch (e) {
    // Absolutely nothing reaches the UI as a raw DOMException.
    phase = 'failed';
    emit('Failed', 1);
    if (isAbortError(e)) return failure('aborted', 'Recording cancelled.', null, null, warnings);
    return failure('internal', 'Something went wrong while recording.',
      UNSUPPORTED_ADVICE, errText(e), warnings);
  }
};

/**
 * Convenience for a UI that just wants a countdown: the remaining seconds of a
 * take, given its progress. Kept here so the cap lives in ONE place.
 */
export const remainingSeconds = (p: RecordProgress): number =>
  Math.max(0, Math.ceil(p.remainingMs / 1000));
