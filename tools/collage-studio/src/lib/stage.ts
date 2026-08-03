// src/lib/stage.ts
// -----------------------------------------------------------------------------
// LIVE STAGE — the moving sibling of `renderCanvas`.
//
// MASTER: John Carmack's frame-budget workflow. Nothing is allocated, decoded,
// awaited or parsed inside the draw loop. Every per-frame cost is precomputed
// into a flat draw list at `setScene` time, and the loop is DEMAND-DRIVEN: with
// no clip advancing it does not run at all.
//
// WHAT THIS IS
//   A framework-free compositor that paints the SAME composition `renderCanvas`
//   paints — same clip paths, same `calculateSmartCrop` (imported, not re-typed),
//   same 'complex' hairline — except video fragments keep moving while photo
//   fragments stay still, and the whole surface can be handed to MediaRecorder.
//
// WHAT THIS IS NOT
//   It is not a replacement for the static preview. A photos-only pool never
//   needs a Stage: `createStage` + `setScene` with zero clips draws exactly once
//   and then idles at zero CPU. The integrator is expected to keep the existing
//   `renderCanvas` -> toBlob -> <img> path as the only pixel producer when no
//   clip is live, and to swap in the Stage canvas only when it is.
//
// THE FOUR THINGS HOISTED OUT OF THE FRAME (each one is fatal in a rAF loop):
//   H1  the per-call `document.createElement('canvas')` (8.6 MB/frame) -> ONE
//       canvas, owned by the caller, context captured once.
//   H2  `new Image()` + `await onload` PER FRAGMENT -> a decode cache filled in
//       `setScene`; the loop reads a hoisted element reference.
//   H3  `canvas.toBlob()` per frame -> deleted; the live canvas IS the pixels.
//   H5  per-frame `beginPath` + N `lineTo` (6,000-13,000 points/frame in
//       'field'/'stencil', which are marching-squares contours) -> ONE `Path2D`
//       per layout item, cached by item identity so a shuffle never rebuilds it.
//   H6  the object literal returned by `calculateSmartCrop` -> flattened into 8
//       numbers on a preallocated draw record.
//
// DECODER ECONOMY: ONE <video> per CLIP, shared by every fragment showing any
// frame of that clip. Thirty fragments of one clip cost ONE decoder. Admission
// is by on-screen area, capped by count AND by summed source pixels, and any
// clip that does not make the cut renders its extracted still — REPORTED through
// `onStatus`, never silently frozen (an over-cap <video> on iOS is paused by the
// system with no error and no console output, which is indistinguishable from a
// rendering bug).
// -----------------------------------------------------------------------------

import { calculateSmartCrop } from './renderer';
import type { LayoutItem } from '../types';

// -----------------------------------------------------------------------------
// PUBLIC TYPES
// -----------------------------------------------------------------------------

/**
 * The shape the Stage needs from a pool asset. `ImageAsset` satisfies this
 * structurally — the interface is declared locally (rather than importing
 * `ImageAsset`) so this module keeps compiling while `types.ts` grows the
 * `clipId` field, and so a caller can drive the Stage with anything crop-shaped.
 */
export interface StageAssetLike {
  id: string;
  src: string;
  /** The <=1024px thumbnail. Drawn in preference to `src`, exactly as the static preview does. */
  previewSrc?: string;
  width: number;
  height: number;
  /** `AnalysisResult`. Normalised 0..1 anchors, so it is valid against ANY rescaling of the source. */
  analysis: unknown;
  /** Set by the integrator when this asset is a frame of a live clip. */
  clipId?: string;
  sourceKind?: string;
  /** Filename of the clip this frame came from — the fallback binding key when `clipId` is absent. */
  sourceName?: string;
  sourceTime?: number;
}

/** A clip the Stage may bring to life. One decoder per entry, not per fragment. */
export interface StageClipInput {
  /** Stable id. Fragments bind to it through `StageAssetLike.clipId`. */
  id: string;
  /** Usually a `blob:` object URL minted from the source File. */
  src: string;
  /** Original filename — also the fallback binding key against `asset.sourceName`. */
  name?: string;
  /** True if the Stage should `URL.revokeObjectURL(src)` when the clip is dropped or the Stage destroyed. */
  ownsUrl?: boolean;
  /** Default true. */
  loop?: boolean;
  /** Seconds; where playback starts on admission. */
  startTime?: number;
  /** Playback speed multiplier. Default 1. Video-length sync uses it so several
   *  clips can share one length — rate<1 slows a clip, rate>1 speeds it up — in
   *  the live preview AND, via `seekClipTo`, in the offline export. */
  playbackRate?: number;
  /** Per-clip mute. Default true — sound needs a user gesture (see `setSound`). */
  muted?: boolean;
  /** Intrinsic size hint used for pixel-budget admission BEFORE `loadedmetadata`. */
  width?: number;
  height?: number;
}

export interface StageSceneInput {
  /** Layout in 1200-space (or whatever `logicalWidth` you configured). */
  layoutItems: LayoutItem[];
  /** Parallel to `layoutItems` — `shuffledIndices.map(i => images[i])`. */
  orderedAssets: (StageAssetLike | null | undefined)[];
  /** Every clip currently available. Omit or pass [] for a photos-only scene. */
  clips?: StageClipInput[];
  /** `layoutMode`. Only 'complex' strokes the hairline, exactly as `renderCanvas`. */
  mode: string;
  aspect: number;
  zoom?: number;
  bgColor?: string;
  /** Accepted for call-site parity with `renderCanvas`; the draw is deterministic without it. */
  seed?: number;
  /** Override the per-scene caps (defaults come from `StageOptions` / `detectStageCaps`). */
  maxLiveClips?: number;
  maxLivePixels?: number;
  /**
   * Custom asset -> clipId binding. Defaults to `asset.clipId`, then to matching
   * `asset.sourceName` against `clip.name` for video-sourced assets.
   */
  resolveClipId?: (asset: StageAssetLike) => string | null | undefined;
}

export type StageClipState =
  | 'live'            // admitted and decoding
  | 'over-clip-cap'   // deferred: too many simultaneous decoders for this device
  | 'over-pixel-cap'  // deferred: summed source pixels would blow the budget
  | 'unused'          // no fragment in the current layout shows this clip
  | 'error';          // the element reported a MediaError; showing stills for good

export interface StageClipStatus {
  id: string;
  name: string;
  state: StageClipState;
  /** Admitted (has a decoder). */
  live: boolean;
  /** Admitted AND actually advancing. */
  playing: boolean;
  /** The per-clip mute FLAG (what `setClipMuted` sets). */
  muted: boolean;
  /**
   * THE USER'S INTENT: "this clip's sound is part of the piece" — `!muted`,
   * and nothing else.
   *
   * Distinct from `audible` on purpose. `audible` is a fact about the SPEAKERS
   * RIGHT NOW and is therefore gated by things the user did not choose: the
   * global monitor switch, and `live`, which is the realtime decoder-admission
   * budget. A clip deferred by that budget is inaudible no matter what the user
   * wants — so a control wired to `audible` reads back "still muted" after every
   * click and looks broken, and an EXPORT wired to it silently drops the sound
   * of every clip the device could not also play at the same time.
   *
   * Intent survives both. It is what the offline mixer renders.
   */
  wantsAudio: boolean;
  /** What you can actually hear right now: `soundOn && !muted && live`. */
  audible: boolean;
  /** Metadata seen and at least one frame decoded. */
  ready: boolean;
  /** How many fragments of the current layout show this clip. */
  fragments: number;
  /** Summed on-screen area of those fragments, in logical px^2. */
  area: number;
  width: number;
  height: number;
  error: string | null;
}

export interface StageStatus {
  running: boolean;
  /** True while a rAF is scheduled — i.e. the loop is NOT idle. */
  animating: boolean;
  liveCount: number;
  deferredCount: number;
  maxLiveClips: number;
  maxLivePixels: number;
  clips: StageClipStatus[];
  /**
   * Playback was refused or never advanced (iOS Low Power Mode blocks even MUTED
   * autoplay, sometimes without rejecting the promise). Surface a TAP TO PLAY
   * affordance and call `resumeFromGesture()` synchronously from its handler.
   */
  needsGesture: boolean;
  soundOn: boolean;
  audioAvailable: boolean;
  capturing: boolean;
  /** Human-readable one-liner for the UI. Null when there is nothing to say. */
  message: string | null;
}

export interface StageOptions {
  /** Simultaneous decoders. Default from `detectStageCaps()`. */
  maxLiveClips?: number;
  /** Summed source pixels (vw*vh) across live clips. Default from `detectStageCaps()`. */
  maxLivePixels?: number;
  /** Logical coordinate width. MUST stay 1200 to match the SVG lock overlay. */
  logicalWidth?: number;
  /** Ceiling on the canvas backing width. 1200 -> 900 is the second frame-budget lever. */
  maxBackingWidth?: number;
  /** Backing width used while capturing (frozen for the whole take). */
  captureBackingWidth?: number;
  /** Build the WebAudio graph at element creation. Default true — see `captureStream`. */
  audio?: boolean;
  /** Pause rendering (and clips) when the document is hidden. Default true. */
  pauseWhenHidden?: boolean;
  /** Pause rendering (and clips) when the canvas scrolls out of view. Default true. */
  pauseWhenOffscreen?: boolean;
  /** Frame rate hint handed to `canvas.captureStream`. Default 30. */
  captureFps?: number;
  /** Forced redraw interval while capturing, so a static composition still emits frames. */
  captureHeartbeatMs?: number;
  /** Fired on state changes only — never per frame. Deduped against its own last value. */
  onStatus?: (status: StageStatus) => void;
}

export interface StageCaps {
  maxLiveClips: number;
  maxLivePixels: number;
  captureBackingWidth: number;
  mobile: boolean;
}

// -----------------------------------------------------------------------------
// CONSTANTS
// -----------------------------------------------------------------------------

const DEFAULT_LOGICAL_W = 1200;
const STROKE_COLOR = '#000';
/** `renderCanvas` line 104: `ctx.lineWidth = width * 0.001`, in LOGICAL space. */
const STROKE_RATIO = 0.001;
/** How long after `play()` we check that `currentTime` actually moved. */
const PLAY_PROBE_MS = 600;
/** Longest edge of the per-clip poster canvas (the "last good frame" safety net). */
const POSTER_MAX_DIM = 480;
/** Sub-frame tolerance for an offline seek — under half a 120 Hz frame. */
const OFFLINE_SEEK_EPSILON = 0.004;

/** A decoder that will not answer a seek costs this frame, never the render. */
const OFFLINE_SEEK_TIMEOUT_MS = 400;

/** A poster refresh is an event-driven drawImage; never more often than this. */
const POSTER_REFRESH_MS = 1500;

/**
 * `calculateSmartCrop` dereferences `img.analysis.face` unguarded (renderer.ts:30),
 * so a missing analysis throws and would kill the whole frame. Stills without an
 * analysis get a centred anchor instead of vanishing. Shared, never mutated.
 */
const FALLBACK_ANALYSIS: { face: null; energy: { x: number; y: number } } =
  { face: null, energy: { x: 0.5, y: 0.5 } };

// -----------------------------------------------------------------------------
// INTERNAL SHAPES
// -----------------------------------------------------------------------------

type FrameCallbackMeta = { mediaTime?: number };
type RvfcVideo = HTMLVideoElement & {
  requestVideoFrameCallback?: (cb: (now: number, meta: FrameCallbackMeta) => void) => number;
  cancelVideoFrameCallback?: (handle: number) => void;
};

type CaptureCanvas = HTMLCanvasElement & {
  captureStream?: (frameRequestRate?: number) => MediaStream;
};

/**
 * Observers are globals, not members of the `Window` interface, but we resolve
 * them off the CANVAS's own window first so a Stage inside an iframe observes in
 * the right realm (and degrades quietly where they do not exist at all).
 */
type ObserverWindow = Window & {
  ResizeObserver?: typeof ResizeObserver;
  IntersectionObserver?: typeof IntersectionObserver;
};

interface ClipRecord {
  id: string;
  name: string;
  url: string;
  ownsUrl: boolean;
  loop: boolean;
  startTime: number;
  playbackRate: number;
  muted: boolean;
  /** The one element, created on admission and reused forever after. */
  el: HTMLVideoElement | null;
  /** Admitted (owns a decoder). */
  live: boolean;
  /** Caller intent, independent of admission. */
  wantPlay: boolean;
  /** Metadata + at least one decoded frame. */
  ready: boolean;
  broken: boolean;
  error: string | null;
  state: StageClipState;
  vw: number;
  vh: number;
  hintW: number;
  hintH: number;
  fragments: number;
  area: number;
  /** Change detection: `currentTime` at the last painted frame. */
  lastTime: number;
  /** Set by requestVideoFrameCallback; means "a new frame was presented". */
  frameDirty: boolean;
  rvfc: number;
  probe: number;
  /** Last good frame, kept so an evicted/errored clip never leaves a hole. */
  poster: HTMLCanvasElement | null;
  posterAt: number;
  posterScale: number;
  source: MediaElementAudioSourceNode | null;
  gain: GainNode | null;
  onEvent: ((e: Event) => void) | null;
  index: number;
}

/**
 * ONE flat record per fragment. The draw loop touches nothing else: no map
 * lookups, no property chains into React state, no allocation.
 */
interface DrawItem {
  path: Path2D;
  stroke: boolean;
  /** Decoded thumbnail element (the static preview draws previewSrc; so do we). */
  still: HTMLImageElement | null;
  stillKey: string;
  /** Still crop is valid (source dimensions were known when it was computed). */
  sok: boolean;
  isx: number; isy: number; isw: number; ish: number;
  clip: ClipRecord | null;
  /** Video crop is valid (loadedmetadata seen). */
  vok: boolean;
  vsx: number; vsy: number; vsw: number; vsh: number;
  /** Poster crop — the video crop scaled into the poster canvas. */
  pok: boolean;
  psx: number; psy: number; psw: number; psh: number;
  /** Destination box: `item.bounds`, shared by every source. */
  dx: number; dy: number; dw: number; dh: number;
  /** Kept so a late decode / late metadata can recompute without a rescan of the scene. */
  bx: number; by: number; bw: number; bh: number;
  analysis: unknown;
}

interface StillRecord {
  img: HTMLImageElement | null;
  state: 'loading' | 'ready' | 'error';
}

// -----------------------------------------------------------------------------
// CAPABILITY PROBE
// -----------------------------------------------------------------------------

/**
 * ONE 1080p STREAM. The unit the decode budget is denominated in.
 *
 * The pixel cap is a SECOND guard behind `maxLiveClips`, and its only job is to
 * stop a handful of oversized sources (4K, 8K) from costing what the clip count
 * alone says is affordable. Denominating it in streams rather than in a bare
 * pixel constant is what keeps the two guards from contradicting each other —
 * see the SCAR note in `detectStageCaps`.
 */
const HD_STREAM_PIXELS = 1920 * 1080;   // 2,073,600

/**
 * Measure the device rather than trusting a constant.
 *
 * The real constraint is hardware DECODE SESSIONS, not elements: iOS Safari
 * shares one H.264 pipeline per page and silently pauses the least-recently
 * touched element past ~3-4 concurrent 1080p streams; Android's MediaCodec pool
 * is system-wide and shared with every other app. There is no API that reports
 * either number, so this combines the only signals a page actually gets —
 * coarse pointer + UA family, core count, and device memory — and stays
 * deliberately pessimistic on mobile, because exceeding the cap fails SILENTLY.
 *
 * SCAR — "only one video ever plays". `maxLivePixels` used to be a flat
 * 2_500_000 on mobile while `maxLiveClips` said 3. A 1080p clip is 2,073,600
 * pixels, so clip #1 was admitted (the `count > 0` escape in refreshAdmission
 * lets the first one in free) and clip #2 pushed the sum to 4,147,200 — over
 * the cap. EVERY second clip was deferred, on every phone, forever: the pixel
 * guard silently overrode the clip guard and pinned the real limit at ONE.
 * Desktop had the same shape with 4K sources (2 x 8,294,400 > 12,000,000).
 *
 * The cap now says what the comment above always claimed: N concurrent 1080p
 * streams. A 4K clip legitimately costs four of them and still degrades to
 * fewer simultaneous clips — that is a real hardware limit, not an accident.
 */
export const detectStageCaps = (view?: Window): StageCaps => {
  const w: Window | undefined = view ?? (typeof window !== 'undefined' ? window : undefined);
  if (!w) {
    return {
      maxLiveClips: 3,
      maxLivePixels: 3 * HD_STREAM_PIXELS,
      captureBackingWidth: 720,
      mobile: true,
    };
  }

  const nav = w.navigator as Navigator & { deviceMemory?: number; maxTouchPoints?: number };
  const ua = nav?.userAgent || '';
  const iOS = /iPad|iPhone|iPod/.test(ua) ||
    // iPadOS 13+ reports as a Mac; the touch points give it away.
    (/Macintosh/.test(ua) && (nav?.maxTouchPoints ?? 0) > 1);
  const android = /Android/i.test(ua);
  const coarse = typeof w.matchMedia === 'function' && w.matchMedia('(pointer: coarse)').matches;
  const mobile = iOS || android || coarse;

  const cores = typeof nav?.hardwareConcurrency === 'number' ? nav.hardwareConcurrency : 4;
  const mem = typeof nav?.deviceMemory === 'number' ? nav.deviceMemory : mobile ? 3 : 8;

  if (mobile) {
    // 3 is the largest number that decodes on an iPhone in Low Power Mode with
    // audio live on one of them. 4+ is a coin flip that fails without an error.
    const maxLiveClips = cores >= 8 && mem >= 6 ? 4 : 3;
    return {
      maxLiveClips,
      maxLivePixels: maxLiveClips * HD_STREAM_PIXELS,
      captureBackingWidth: 720,
      mobile: true,
    };
  }
  const maxLiveClips = cores >= 8 ? 8 : cores >= 4 ? 6 : 4;
  // Memory, not cores, is what a wall of decoded 4K frames actually exhausts —
  // so a low-RAM desktop keeps its clip count and gives up pixel headroom.
  const budgetStreams = mem >= 8 ? maxLiveClips : Math.min(maxLiveClips, 4);
  return {
    maxLiveClips,
    maxLivePixels: budgetStreams * HD_STREAM_PIXELS,
    captureBackingWidth: 1080,
    mobile: false,
  };
};

// -----------------------------------------------------------------------------
// SMALL HELPERS (none of these are reachable from the draw loop)
// -----------------------------------------------------------------------------

/** Encoders reject odd dimensions on several platforms; keep every backing size even. */
const even = (n: number): number => {
  const v = Math.max(2, Math.round(n));
  return v % 2 === 0 ? v : v + 1;
};

const finiteOr = (n: number | undefined, fallback: number): number =>
  typeof n === 'number' && Number.isFinite(n) ? n : fallback;

const mediaErrorText = (el: HTMLVideoElement): string => {
  const e = el.error;
  if (!e) return 'Unknown video error';
  switch (e.code) {
    case 1: return 'Playback was aborted';
    case 2: return 'Network error while reading the clip';
    case 3: return 'The clip is corrupt or uses an unsupported codec';
    case 4: return 'This browser cannot decode that clip (try H.264 MP4)';
    default: return 'Unknown video error';
  }
};

// -----------------------------------------------------------------------------
// STAGE
// -----------------------------------------------------------------------------

export class Stage {
  // --- surface ---------------------------------------------------------------
  private readonly cv: HTMLCanvasElement;
  private readonly ctx: CanvasRenderingContext2D;
  private readonly doc: Document;
  private readonly view: Window;

  // --- configuration ---------------------------------------------------------
  private readonly logicalW: number;
  private readonly maxBackingW: number;
  private readonly captureBackingW: number;
  private readonly captureFps: number;
  private readonly captureHeartbeatMs: number;
  private readonly audioEnabled: boolean;
  private readonly pauseWhenHidden: boolean;
  private readonly pauseWhenOffscreen: boolean;
  private readonly onStatus: ((s: StageStatus) => void) | null;
  private capsClips: number;
  private capsPixels: number;

  // --- scene -----------------------------------------------------------------
  private items: DrawItem[] = [];
  private clips = new Map<string, ClipRecord>();
  private liveClips: ClipRecord[] = [];
  private stills = new Map<string, StillRecord>();
  /** Path2D cache keyed by LayoutItem identity: a shuffle never rebuilds a contour. */
  private paths = new WeakMap<object, Path2D>();
  private logicalH = DEFAULT_LOGICAL_W / 0.666;
  private aspect = 0.666;
  private zoom = 1;
  private bg = '#050505';
  private lineWidth = DEFAULT_LOGICAL_W * STROKE_RATIO;

  // --- loop ------------------------------------------------------------------
  private running = false;
  private rafId = 0;
  private dirty = true;
  private lastDrawAt = -1e9;
  private liveEnabled = true;
  private visible = true;
  private onScreen = true;
  private destroyed = false;
  private frames = 0;

  // --- offline render --------------------------------------------------------
  private offline = false;
  private offlineWasRunning = false;
  private offlineWantPlay: string[] = [];

  // --- media -----------------------------------------------------------------
  private host: HTMLElement | null = null;
  private soundOn = false;
  private needsGesture = false;
  private audioCtx: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private streamDest: MediaStreamAudioDestinationNode | null = null;
  private audioAvailable = false;
  private stream: MediaStream | null = null;
  private capturing = false;

  // --- status ----------------------------------------------------------------
  private statusSig = '';
  private statusPending = false;
  /** Set from inside the draw (which must not allocate); serviced on the next tick. */
  private admissionPending = false;

  // --- observers -------------------------------------------------------------
  private ro: ResizeObserver | null = null;
  private io: IntersectionObserver | null = null;

  constructor(canvas: HTMLCanvasElement, opts: StageOptions = {}) {
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Stage: canvas 2D context is unavailable');
    // NOTE: default context attributes on purpose. `{alpha:false}` or
    // `{desynchronized:true}` would diverge from `renderCanvas`.
    this.cv = canvas;
    this.ctx = ctx;
    this.doc = canvas.ownerDocument ?? (typeof document !== 'undefined' ? document : (null as unknown as Document));
    this.view = this.doc?.defaultView ?? (typeof window !== 'undefined' ? window : (null as unknown as Window));

    const caps = detectStageCaps(this.view);
    this.capsClips = Math.max(0, finiteOr(opts.maxLiveClips, caps.maxLiveClips));
    this.capsPixels = Math.max(0, finiteOr(opts.maxLivePixels, caps.maxLivePixels));
    this.logicalW = Math.max(64, finiteOr(opts.logicalWidth, DEFAULT_LOGICAL_W));
    this.maxBackingW = Math.max(240, finiteOr(opts.maxBackingWidth, this.logicalW));
    this.captureBackingW = Math.max(
      240,
      Math.min(this.maxBackingW, finiteOr(opts.captureBackingWidth, caps.captureBackingWidth)),
    );
    this.captureFps = Math.max(1, finiteOr(opts.captureFps, 30));
    this.captureHeartbeatMs = Math.max(16, finiteOr(opts.captureHeartbeatMs, 100));
    this.audioEnabled = opts.audio !== false;
    this.pauseWhenHidden = opts.pauseWhenHidden !== false;
    this.pauseWhenOffscreen = opts.pauseWhenOffscreen !== false;
    this.onStatus = opts.onStatus ?? null;
    this.lineWidth = this.logicalW * STROKE_RATIO;
    this.logicalH = this.logicalW / this.aspect;

    this.attachObservers();
    this.applySize(true);
  }

  // ===========================================================================
  // SCENE
  // ===========================================================================

  /**
   * Rebuild the draw list. Call it whenever layout / order / zoom / bg / clips
   * change — i.e. exactly where the static render effect already re-runs.
   * Everything expensive (Path2D construction, crop math, image decoding,
   * clip admission) happens HERE so the frame stays a flat memcpy of draw calls.
   */
  setScene(scene: StageSceneInput): void {
    if (this.destroyed) return;

    const aspect = finiteOr(scene.aspect, this.aspect) || 1;
    const zoom = Number.isFinite(scene.zoom) && (scene.zoom as number) > 0 ? (scene.zoom as number) : 1;
    this.aspect = aspect;
    this.zoom = zoom;
    this.bg = scene.bgColor || '#050505';
    this.logicalH = this.logicalW / aspect;
    this.lineWidth = this.logicalW * STROKE_RATIO;
    if (typeof scene.maxLiveClips === 'number') this.capsClips = Math.max(0, scene.maxLiveClips);
    if (typeof scene.maxLivePixels === 'number') this.capsPixels = Math.max(0, scene.maxLivePixels);

    this.syncClips(scene.clips ?? []);

    const stroke = scene.mode === 'complex';
    const layout = scene.layoutItems || [];
    const ordered = scene.orderedAssets || [];
    const resolve = scene.resolveClipId ?? null;

    // Fragment counts / areas are recomputed from scratch every scene.
    this.clips.forEach((c) => { c.fragments = 0; c.area = 0; });

    const items: DrawItem[] = [];
    const wanted = new Set<string>();

    for (let i = 0; i < layout.length; i++) {
      const li = layout[i];
      const asset = ordered[i];
      if (!li || !asset) continue;                       // renderer.ts:73 — same skip

      const path = this.pathFor(li);
      if (!path) continue;

      const b = li.bounds;
      const clip = this.bindClip(asset, resolve);
      const stillKey = asset.previewSrc || asset.src;    // App.tsx:209 draws previewSrc
      if (stillKey) wanted.add(stillKey);

      const it: DrawItem = {
        path,
        stroke,
        still: null,
        stillKey,
        sok: false,
        isx: 0, isy: 0, isw: 0, ish: 0,
        clip,
        vok: false,
        vsx: 0, vsy: 0, vsw: 0, vsh: 0,
        pok: false,
        psx: 0, psy: 0, psw: 0, psh: 0,
        dx: b.x, dy: b.y, dw: b.w, dh: b.h,
        bx: b.x, by: b.y, bw: b.w, bh: b.h,
        analysis: asset.analysis,
      };

      // Still: use the cached decode if it is already resident; otherwise the
      // asset's own intrinsic size is a correct stand-in for the crop math (the
      // thumbnail preserves aspect), and the element pointer is patched in when
      // the decode lands.
      const rec = this.stills.get(stillKey);
      if (rec && rec.state === 'ready' && rec.img) {
        it.still = rec.img;
        this.computeStillCrop(it, rec.img.naturalWidth || rec.img.width, rec.img.naturalHeight || rec.img.height);
      }

      if (clip) {
        clip.fragments++;
        clip.area += Math.max(0, b.w) * Math.max(0, b.h);
        if (clip.vw > 0 && clip.vh > 0) this.computeVideoCrop(it, clip.vw, clip.vh);
        if (clip.poster) this.computePosterCrop(it, clip);
      }

      items.push(it);
    }

    this.items = items;
    this.ensureStills(wanted);
    this.refreshAdmission();
    this.markDirty();
    this.emitStatus();
  }

  /** Background only — cheaper than a whole `setScene` when just the colour moves. */
  setBackground(color: string): void {
    if (!color || color === this.bg) return;
    this.bg = color;
    this.markDirty();
  }

  /** Master switch: false renders every fragment as its still (used by exports/tests). */
  setLive(on: boolean): void {
    if (this.liveEnabled === on) return;
    this.liveEnabled = on;
    this.refreshAdmission();
    this.markDirty();
    this.emitStatus();
  }

  // ===========================================================================
  // LOOP
  // ===========================================================================

  /** Begin driving requestAnimationFrame. Idempotent. */
  start(): void {
    if (this.destroyed || this.running) return;
    this.running = true;
    this.markDirty();
    this.emitStatus();
  }

  /** Stop rendering. Media keeps its play state (use `pauseAll` for that). */
  stop(): void {
    if (!this.running) return;
    this.running = false;
    if (this.rafId) { this.view.cancelAnimationFrame(this.rafId); this.rafId = 0; }
    this.emitStatus();
  }

  /** Force exactly one repaint on the next frame. */
  requestFrame(): void {
    this.markDirty();
  }

  // ===========================================================================
  // OFFLINE RENDER
  // ===========================================================================
  //
  // WHY THIS EXISTS. Both recorders sample a canvas that is playing in REAL
  // TIME: MediaRecorder pulls from `captureStream`, and `frameExport` samples
  // on a rAF cadence and snaps its schedule forward when it falls behind. Under
  // the load this app is FOR — several 1080p decoders composited into clipped
  // paths every frame — falling behind is the normal case, not the edge case.
  // Frames are dropped and the wall-clock timestamps record the stall, so the
  // judder is encoded into the file and no amount of re-recording removes it.
  //
  // The fix is to stop treating the take as a performance to be witnessed. In
  // offline mode nothing advances on its own: the loop is stopped, every clip
  // is parked, and the ONLY thing that moves the canvas is `renderAtTime`. The
  // render can then take as long as it needs per frame — 10ms or 400ms — and
  // still emit a perfectly even timeline, because the timestamps come from the
  // FRAME INDEX and not from the clock.

  /**
   * ENTER DETERMINISTIC MODE. Idempotent.
   *
   * Order is load-bearing: the play set is captured BEFORE `pauseAll` clears
   * it, and `setCaptureActive` runs AFTER, because it restarts anything still
   * marked `wantPlay` — which is exactly what this mode must not have.
   */
  beginOfflineRender(): void {
    if (this.destroyed || this.offline) return;
    this.offline = true;
    this.offlineWasRunning = this.running;
    this.offlineWantPlay = [];
    this.clips.forEach((c) => { if (c.wantPlay) this.offlineWantPlay.push(c.id); });
    this.pauseAll();
    // Freezes the backing size for the whole take. A mid-stream resolution
    // change is what corrupts an H.264 stream.
    this.setCaptureActive(true);
    // AND RE-APPLY IT, because `setCaptureActive` is a NO-OP when the caller
    // already armed capture — VideoStage does, synchronously inside the tap,
    // since iOS grants a gesture only to the task it fired in. The size that
    // applied was therefore the REALTIME one, chosen before `offline` was set.
    // Depending on call order here is what kept the render at 720/1080.
    this.applySize(true);
    this.stop();
  }

  /** Leave deterministic mode and put playback back exactly as it was. */
  endOfflineRender(): void {
    if (!this.offline) return;
    this.offline = false;
    this.setCaptureActive(false);
    const want = new Set(this.offlineWantPlay);
    this.offlineWantPlay = [];
    this.clips.forEach((c) => {
      if (!want.has(c.id)) return;
      c.wantPlay = true;
      this.tryPlay(c);
    });
    if (this.offlineWasRunning) this.start();
    this.markDirty();
    this.emitStatus();
  }

  get isOfflineRendering(): boolean { return this.offline; }

  /**
   * PAINT THE COMPOSITION EXACTLY AS IT SHOULD LOOK AT `timeSec`.
   *
   * Seeks every live clip to its own position on that timeline, waits for the
   * decoders to land, then draws ONCE. Resolves when the canvas holds the frame
   * for that timestamp — so the caller can encode it and ask for the next one,
   * with no clock involved anywhere.
   */
  async renderAtTime(timeSec: number, opts: { signal?: AbortSignal } = {}): Promise<void> {
    if (this.destroyed) return;
    const targets: ClipRecord[] = [];
    this.clips.forEach((c) => { if (c.live && !c.broken && c.el) targets.push(c); });
    if (targets.length > 0) {
      await Promise.all(targets.map((c) => this.seekClipTo(c, timeSec, opts.signal)));
    }
    if (this.destroyed) return;
    this.dirty = false;
    this.lastDrawAt = -1e9;      // never let the tick's skip-heuristic apply here
    this.drawFrame(0);
    this.frames++;
  }

  /**
   * One clip, one exact position. Never rejects: a decoder that will not seek
   * costs this frame its motion, not the whole render.
   */
  private seekClipTo(clip: ClipRecord, timeSec: number, signal?: AbortSignal): Promise<void> {
    const el = clip.el;
    if (!el) return Promise.resolve();
    const dur = el.duration;
    if (!Number.isFinite(dur) || dur <= 0) return Promise.resolve();

    // Land strictly INSIDE the media. Seeking to exactly `duration` is a no-op
    // on some engines and fires `ended` on others, and both paint a frame that
    // is not the one asked for.
    const span = Math.max(OFFLINE_SEEK_EPSILON, dur - OFFLINE_SEEK_EPSILON);
    // Honour the video-length-sync speed in the OFFLINE render too: at rate r a
    // clip advances r seconds of content per composition second, so the frame the
    // export wants at `timeSec` is r*timeSec into the clip. Live playback gets
    // this from el.playbackRate; the offline path seeks by hand, so scale here.
    const rate = clip.playbackRate > 0 ? clip.playbackRate : 1;
    const scaled = timeSec * rate;
    const target = clip.loop
      ? scaled % span
      : Math.min(scaled, span);

    if (Math.abs(el.currentTime - target) < OFFLINE_SEEK_EPSILON) return Promise.resolve();

    return new Promise<void>((resolve) => {
      let settled = false;
      const done = () => {
        if (settled) return;
        settled = true;
        this.view.clearTimeout(timer);
        el.removeEventListener('seeked', done);
        el.removeEventListener('error', done);
        signal?.removeEventListener('abort', done);
        resolve();
      };
      // A seek that never reports back must not hang the render — draw whatever
      // the decoder last presented and move on.
      const timer = this.view.setTimeout(done, OFFLINE_SEEK_TIMEOUT_MS);
      el.addEventListener('seeked', done, { once: true });
      el.addEventListener('error', done, { once: true });
      signal?.addEventListener('abort', done, { once: true });
      try { el.currentTime = target; } catch { done(); }
    });
  }

  get isRunning(): boolean { return this.running; }
  get hasLiveClips(): boolean { return this.liveClips.length > 0; }
  /** The surface. Hand it to MediaRecorder via `captureStream()`, not directly. */
  get canvas(): HTMLCanvasElement { return this.cv; }

  private markDirty(): void {
    this.dirty = true;
    this.schedule();
  }

  private schedule(): void {
    if (!this.running || this.rafId || this.destroyed) return;
    if (!this.visible || !this.onScreen) return;
    this.rafId = this.view.requestAnimationFrame(this.tick);
  }

  /**
   * DEMAND-DRIVEN TICK.
   *
   *   * nothing playing and nothing dirty -> NO rAF is rescheduled. The loop
   *     genuinely idles at zero CPU; a photos-only scene draws once and stops.
   *   * playing -> we still SKIP the repaint unless a clip actually advanced
   *     (a 24 fps source on a 60 Hz display halves the work for free).
   *   * capturing -> a heartbeat forces frames so the recorded file is never a
   *     zero-frame track when the composition happens to be static.
   */
  private readonly tick = (ts: number): void => {
    this.rafId = 0;
    if (!this.running || this.destroyed) return;

    let needDraw = this.dirty;
    let playing = 0;
    const clips = this.liveClips;
    for (let i = 0; i < clips.length; i++) {
      const c = clips[i];
      const el = c.el;
      if (el === null) continue;
      if (!el.paused && !el.ended) playing++;
      if (c.frameDirty) { c.frameDirty = false; needDraw = true; }
      else if (el.currentTime !== c.lastTime) needDraw = true;
    }
    if (this.capturing && ts - this.lastDrawAt >= this.captureHeartbeatMs) needDraw = true;

    if (needDraw) this.drawFrame(ts);
    if (this.admissionPending) { this.admissionPending = false; this.refreshAdmission(); }
    if (this.statusPending) { this.statusPending = false; this.emitStatus(); }

    if (playing > 0 || this.capturing || this.dirty) {
      this.rafId = this.view.requestAnimationFrame(this.tick);
    }
  };

  /**
   * THE DRAW. Fully synchronous, zero allocation, no promises, no closures, no
   * map lookups, no string building. Mirrors renderer.ts:57-108 exactly:
   * fillRect clear -> per item: save, clip(path), drawImage(crop -> bounds),
   * optional 'complex' hairline stroked through the SAME path, restore.
   */
  private drawFrame(ts: number): void {
    const ctx = this.ctx;
    const items = this.items;

    ctx.fillStyle = this.bg;
    ctx.fillRect(0, 0, this.logicalW, this.logicalH);

    const lw = this.lineWidth;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      let painted = false;

      // 1. LIVE VIDEO — the only source that changes between frames.
      const clip = it.clip;
      if (clip !== null && it.vok && !clip.broken && clip.live) {
        const el = clip.el;
        if (el !== null && el.readyState >= 2 && el.videoWidth > 0) {
          ctx.save();
          ctx.clip(it.path);
          try {
            ctx.drawImage(el, it.vsx, it.vsy, it.vsw, it.vsh, it.dx, it.dy, it.dw, it.dh);
            painted = true;
          } catch {
            // A decoder that dies mid-draw must not kill the frame. Demote the
            // clip to its still for good; the status emit is deferred out of the
            // loop so this stays allocation-free.
            clip.broken = true;
            clip.error = 'The decoder dropped this clip';
            clip.state = 'error';
            this.statusPending = true;
            this.admissionPending = true;   // release the decoder AFTER the frame
          }
          if (painted && it.stroke) {
            ctx.strokeStyle = STROKE_COLOR;
            ctx.lineWidth = lw;
            ctx.stroke(it.path);
          }
          ctx.restore();
        }
      }

      // 2. STILL — the extracted frame / the photo. Identical to the static path.
      if (!painted && it.sok && it.still !== null) {
        ctx.save();
        ctx.clip(it.path);
        ctx.drawImage(it.still, it.isx, it.isy, it.isw, it.ish, it.dx, it.dy, it.dw, it.dh);
        if (it.stroke) {
          ctx.strokeStyle = STROKE_COLOR;
          ctx.lineWidth = lw;
          ctx.stroke(it.path);
        }
        ctx.restore();
        painted = true;
      }

      // 3. POSTER — last good frame of an evicted/errored clip. The hole-filler.
      if (!painted && clip !== null && it.pok && clip.poster !== null) {
        ctx.save();
        ctx.clip(it.path);
        ctx.drawImage(clip.poster, it.psx, it.psy, it.psw, it.psh, it.dx, it.dy, it.dw, it.dh);
        if (it.stroke) {
          ctx.strokeStyle = STROKE_COLOR;
          ctx.lineWidth = lw;
          ctx.stroke(it.path);
        }
        ctx.restore();
      }
    }

    const clips = this.liveClips;
    for (let i = 0; i < clips.length; i++) {
      const el = clips[i].el;
      if (el !== null) clips[i].lastTime = el.currentTime;
    }

    this.dirty = false;
    this.lastDrawAt = ts;
    this.frames++;
  }

  // ===========================================================================
  // SIZING
  // ===========================================================================

  /**
   * Backing store follows CSS size x DPR, capped. The LOGICAL space never
   * changes: every path point, bound, crop and the hairline stay in 1200-space,
   * which is what keeps the SVG lock overlay (viewBox `0 0 1200 1200/aspect`)
   * pinned to the pixels.
   */
  private applySize(force: boolean): void {
    const lw = this.logicalW;
    const lh = this.logicalH;
    let target: number;
    if (this.capturing) {
      // `captureBackingW` is a REALTIME budget — 720 on mobile, 1080 on desktop
      // — sized so a live take can composite fast enough to keep up with a
      // clock. An OFFLINE render pays none of that: it seeks, draws and encodes
      // one frame at a time and is bounded by patience, not by frame rate. It
      // inheriting the realtime cap made the exported file LOWER RESOLUTION
      // THAN THE PREVIEW ON THE SAME SCREEN — 720 wide from 1080p sources on
      // the one device that matters. Still frozen for the whole take either
      // way: a mid-stream resolution change is what corrupts an H.264 stream.
      target = this.offline ? this.maxBackingW : this.captureBackingW;
    } else {
      const cssW = this.cv.clientWidth || lw;
      const dpr = this.view?.devicePixelRatio || 1;
      target = Math.min(this.maxBackingW, Math.max(240, Math.ceil(cssW * dpr)));
    }
    const w = even(target);
    const h = even((lh / lw) * target);
    if (!force && this.cv.width === w && this.cv.height === h) return;

    // Assigning width/height REALLOCATES and CLEARS the backing store, so this
    // must never happen per frame — only from the ResizeObserver.
    this.cv.width = w;
    this.cv.height = h;
    this.ctx.setTransform(w / lw, 0, 0, h / lh, 0, 0);
    this.markDirty();
  }

  private attachObservers(): void {
    const view = this.view as ObserverWindow | null;
    if (!view) return;

    const RO = view.ResizeObserver ?? (typeof ResizeObserver !== 'undefined' ? ResizeObserver : undefined);
    if (typeof RO === 'function') {
      try {
        const ro = new RO(() => { if (!this.capturing) this.applySize(false); });
        ro.observe(this.cv);
        this.ro = ro;
      } catch { this.ro = null; }
    }

    const IO = view.IntersectionObserver ??
      (typeof IntersectionObserver !== 'undefined' ? IntersectionObserver : undefined);
    if (this.pauseWhenOffscreen && typeof IO === 'function') {
      try {
        const io = new IO((entries: IntersectionObserverEntry[]) => {
          const last = entries[entries.length - 1];
          if (!last) return;
          const on = last.isIntersecting;
          if (on === this.onScreen) return;
          this.onScreen = on;
          this.applyPowerState();
        }, { threshold: 0 });
        io.observe(this.cv);
        this.io = io;
      } catch { this.io = null; }
    }

    if (this.pauseWhenHidden && this.doc) {
      this.doc.addEventListener('visibilitychange', this.onVisibility);
      this.visible = !this.doc.hidden;
    }
  }

  private readonly onVisibility = (): void => {
    this.visible = !this.doc.hidden;
    this.applyPowerState();
  };

  /** Hidden tab / off-screen stage: stop painting AND release decode pressure. */
  private applyPowerState(): void {
    const awake = (this.visible && this.onScreen) || this.capturing;
    if (awake) {
      this.clips.forEach((c) => { if (c.live && c.wantPlay) this.tryPlay(c); });
      this.markDirty();
    } else {
      if (this.rafId) { this.view.cancelAnimationFrame(this.rafId); this.rafId = 0; }
      this.clips.forEach((c) => { const el = c.el; if (el && !el.paused) { try { el.pause(); } catch { /* ignore */ } } });
    }
  }

  // ===========================================================================
  // PATHS + CROPS  (all precomputed; none of this is reachable from the loop)
  // ===========================================================================

  private pathFor(li: LayoutItem): Path2D | null {
    const cached = this.paths.get(li as unknown as object);
    if (cached) return cached;
    const pts = li.path;
    if (!pts || pts.length < 2) return null;
    const p = new Path2D();
    // Same winding, same closePath as renderer.ts:86-90, so ctx.clip(p) uses the
    // identical nonzero region and ctx.stroke(p) traces the identical outline.
    for (let i = 0; i < pts.length; i++) {
      const pt = pts[i];
      if (i === 0) p.moveTo(pt.x, pt.y); else p.lineTo(pt.x, pt.y);
    }
    p.closePath();
    this.paths.set(li as unknown as object, p);
    return p;
  }

  /** The real `calculateSmartCrop`, imported from renderer.ts — never a copy. */
  private crop(it: DrawItem, srcW: number, srcH: number): { sx: number; sy: number; sw: number; sh: number } | null {
    if (!(srcW > 0) || !(srcH > 0) || !(it.bw > 0) || !(it.bh > 0)) return null;
    const analysis = (it.analysis as { energy?: unknown } | null | undefined) ? it.analysis : FALLBACK_ANALYSIS;
    try {
      const c = calculateSmartCrop(
        { x: it.bx, y: it.by, w: it.bw, h: it.bh },
        { width: srcW, height: srcH, analysis },
        this.zoom,
      );
      if (!Number.isFinite(c.sx) || !Number.isFinite(c.sy) || !(c.sw > 0) || !(c.sh > 0)) return null;
      return c;
    } catch {
      return null;
    }
  }

  private computeStillCrop(it: DrawItem, w: number, h: number): void {
    const c = this.crop(it, w, h);
    if (!c) { it.sok = false; return; }
    it.isx = c.sx; it.isy = c.sy; it.isw = c.sw; it.ish = c.sh;
    it.sok = true;
  }

  /**
   * VIDEO SUBSTITUTION — `videoWidth`/`videoHeight`, NEVER the asset's own dims.
   * `video.ts` caps an extracted frame at 1600px, so a 4K clip's ImageAsset is
   * 1600 wide while `videoWidth` is 3840: reusing the asset dims would land
   * sx/sy/sw/sh in the wrong pixel space and sample a top-left sub-region.
   */
  private computeVideoCrop(it: DrawItem, vw: number, vh: number): void {
    const c = this.crop(it, vw, vh);
    if (!c) { it.vok = false; return; }
    it.vsx = c.sx; it.vsy = c.sy; it.vsw = c.sw; it.vsh = c.sh;
    it.vok = true;
  }

  private computePosterCrop(it: DrawItem, clip: ClipRecord): void {
    if (!clip.poster || !it.vok) { it.pok = false; return; }
    const s = clip.posterScale;
    it.psx = it.vsx * s; it.psy = it.vsy * s; it.psw = it.vsw * s; it.psh = it.vsh * s;
    it.pok = it.psw > 0 && it.psh > 0;
  }

  // ===========================================================================
  // STILL DECODE CACHE
  // ===========================================================================

  private ensureStills(wanted: Set<string>): void {
    wanted.forEach((key) => {
      if (this.stills.has(key)) return;
      const rec: StillRecord = { img: null, state: 'loading' };
      this.stills.set(key, rec);
      const img = new Image();
      // Parity with renderer.ts:77 — and it keeps the canvas untainted, which
      // `captureStream()` requires.
      img.crossOrigin = 'anonymous';
      let settled = false;
      const done = (): void => {
        // decode() and onload BOTH fire on success; adopt exactly once.
        if (settled || this.destroyed) return;
        settled = true;
        const w = img.naturalWidth || img.width;
        if (!w) { rec.state = 'error'; return; }
        rec.img = img;
        rec.state = 'ready';
        this.adoptStill(key, img);
      };
      const fail = (): void => { rec.state = 'error'; };
      img.onload = done;
      img.onerror = fail;
      img.src = key;
      // decode() keeps the first paint off the main-thread rasteriser; onload is
      // still wired because Safari has shipped decode() rejections for blob URLs.
      if (typeof img.decode === 'function') img.decode().then(done, () => { /* onload/onerror decide */ });
    });

    // Drop cache entries no fragment references any more. The URLs belong to the
    // caller (previewSrc may ALIAS src — App.tsx:312), so we never revoke them.
    if (this.stills.size > wanted.size + 32) {
      const dead: string[] = [];
      this.stills.forEach((_v, k) => { if (!wanted.has(k)) dead.push(k); });
      for (let i = 0; i < dead.length; i++) this.stills.delete(dead[i]);
    }
  }

  private adoptStill(key: string, img: HTMLImageElement): void {
    const w = img.naturalWidth || img.width;
    const h = img.naturalHeight || img.height;
    const items = this.items;
    let touched = false;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      if (it.stillKey !== key) continue;
      it.still = img;
      this.computeStillCrop(it, w, h);
      touched = true;
    }
    if (touched) this.markDirty();
  }

  // ===========================================================================
  // CLIPS
  // ===========================================================================

  private bindClip(asset: StageAssetLike, resolve: ((a: StageAssetLike) => string | null | undefined) | null): ClipRecord | null {
    if (!this.liveEnabled) return null;
    let id = resolve ? resolve(asset) : asset.clipId;
    if (!id && asset.sourceName) {
      // Fallback binding for pools minted before `clipId` existed on ImageAsset.
      this.clips.forEach((c) => { if (!id && c.name && c.name === asset.sourceName) id = c.id; });
    }
    if (!id) return null;
    return this.clips.get(id) ?? null;
  }

  private syncClips(input: StageClipInput[]): void {
    const seen = new Set<string>();
    for (let i = 0; i < input.length; i++) {
      const c = input[i];
      if (!c || !c.id || !c.src) continue;
      seen.add(c.id);
      const existing = this.clips.get(c.id);
      if (existing) {
        // A changed URL means a genuinely different clip under the same id.
        if (existing.url !== c.src) {
          this.disposeClip(existing);
          this.clips.set(c.id, this.newClipRecord(c, existing.index));
        } else {
          existing.name = c.name ?? existing.name;
          existing.loop = c.loop !== false;
          existing.playbackRate = finiteOr(c.playbackRate, 1);
          existing.hintW = finiteOr(c.width, existing.hintW);
          existing.hintH = finiteOr(c.height, existing.hintH);
          if (existing.el) {
            existing.el.loop = existing.loop;
            // Guard the assignment: some engines throw if the element is mid-load.
            try { existing.el.playbackRate = existing.playbackRate; } catch { /* re-applied on (re)admission */ }
          }
        }
        continue;
      }
      this.clips.set(c.id, this.newClipRecord(c, this.clips.size));
    }
    const dead: ClipRecord[] = [];
    this.clips.forEach((c) => { if (!seen.has(c.id)) dead.push(c); });
    for (let i = 0; i < dead.length; i++) {
      this.disposeClip(dead[i]);
      this.clips.delete(dead[i].id);
    }
  }

  private newClipRecord(input: StageClipInput, index: number): ClipRecord {
    return {
      id: input.id,
      name: input.name || input.id,
      url: input.src,
      ownsUrl: input.ownsUrl === true,
      loop: input.loop !== false,
      startTime: finiteOr(input.startTime, 0),
      playbackRate: finiteOr(input.playbackRate, 1),
      muted: input.muted !== false,
      el: null,
      live: false,
      wantPlay: true,
      ready: false,
      broken: false,
      error: null,
      state: 'unused',
      vw: 0, vh: 0,
      hintW: finiteOr(input.width, 0),
      hintH: finiteOr(input.height, 0),
      fragments: 0,
      area: 0,
      lastTime: -1,
      frameDirty: false,
      rvfc: 0,
      probe: 0,
      poster: null,
      posterAt: 0,
      posterScale: 1,
      source: null,
      gain: null,
      onEvent: null,
      index,
    };
  }

  /**
   * ADMISSION — by on-screen area, capped by decoder count AND summed source
   * pixels. Counted per UNIQUE CLIP, never per fragment: 30 fragments of one
   * clip cost ONE decoder, and that economy is what makes a cap of 3 livable.
   * Runs on scene / metadata / error changes only — never per frame.
   */
  private refreshAdmission(): void {
    const ranked: ClipRecord[] = [];
    this.clips.forEach((c) => { if (c.fragments > 0 && !c.broken) ranked.push(c); });
    ranked.sort((a, b) => (b.area - a.area) || (a.index - b.index));

    let count = 0;
    let pixels = 0;
    const nextLive: ClipRecord[] = [];

    for (let i = 0; i < ranked.length; i++) {
      const c = ranked[i];
      const px = (c.vw > 0 ? c.vw * c.vh : (c.hintW > 0 ? c.hintW * c.hintH : 1_280_000));
      let admit = this.liveEnabled;
      let state: StageClipState = 'live';
      if (!admit) {
        state = 'unused';
      } else if (count >= this.capsClips) {
        admit = false; state = 'over-clip-cap';
      } else if (this.capsPixels > 0 && count > 0 && pixels + px > this.capsPixels) {
        admit = false; state = 'over-pixel-cap';
      }
      c.state = state;
      if (admit) {
        count++;
        pixels += px;
        nextLive.push(c);
        if (!c.live) this.admit(c);
      } else if (c.live) {
        this.evict(c);
      }
    }

    // Anything with no fragments in this layout, or already broken, is released.
    this.clips.forEach((c) => {
      if (c.broken) { c.state = 'error'; if (c.live) this.evict(c); return; }
      if (c.fragments === 0) { c.state = 'unused'; if (c.live) this.evict(c); }
    });

    this.liveClips = nextLive;
    this.applyMutes();
  }

  private admit(clip: ClipRecord): void {
    clip.live = true;
    if (!clip.el) {
      const el = this.createVideo(clip);
      if (!el) { clip.live = false; clip.broken = true; clip.error = 'Video element unavailable'; return; }
      clip.el = el;
    } else if (!clip.el.getAttribute('src')) {
      // Re-admission after an eviction: the ELEMENT (and therefore its
      // MediaElementAudioSourceNode, which may be created only ONCE per element
      // ever) survives; only the decoder was released.
      clip.el.src = clip.url;
      try { clip.el.load(); } catch { /* ignore */ }
    }
    this.armRvfc(clip);
    if (clip.wantPlay) this.tryPlay(clip);
    this.markDirty();
  }

  private evict(clip: ClipRecord): void {
    clip.live = false;
    clip.ready = false;
    this.capturePoster(clip, true);
    const el = clip.el;
    if (!el) return;
    this.cancelRvfc(clip);
    if (clip.probe) { this.view.clearTimeout(clip.probe); clip.probe = 0; }
    try {
      // Without the load() Safari holds the decoder for MINUTES and the next
      // admission silently fails (video.ts:220-232 learned this the hard way).
      el.pause();
      el.removeAttribute('src');
      el.srcObject = null;
      el.load();
    } catch { /* teardown must never throw */ }
    this.markDirty();
  }

  /**
   * HIDDEN BUT DECODING. Not `display:none` (WebKit stops scheduling frame
   * updates for an unrendered video and `drawImage` returns the same frame
   * forever), not off-DOM (Safari refuses to decode at all), not `opacity:0`
   * (a fully transparent layer can be culled from compositing): a 2px,
   * opacity 0.01, in-viewport, self-composited element.
   */
  private createVideo(clip: ClipRecord): HTMLVideoElement | null {
    const doc = this.doc;
    if (!doc) return null;
    const host = this.ensureHost();
    if (!host) return null;

    const v = doc.createElement('video');
    // EVERY autoplay-relevant property and attribute BEFORE src is assigned.
    v.muted = true;
    v.defaultMuted = true;
    v.volume = 0;
    v.setAttribute('muted', '');            // iOS reads the ATTRIBUTE for autoplay
    v.playsInline = true;
    v.setAttribute('playsinline', '');
    v.setAttribute('webkit-playsinline', '');
    v.loop = clip.loop;
    // Video-length sync speed. Set before src, and re-applied on loadedmetadata
    // below, because some engines reset playbackRate to 1 when a source loads.
    try { v.playbackRate = clip.playbackRate; } catch { /* set again after metadata */ }
    v.preload = 'auto';
    v.autoplay = true;
    v.disablePictureInPicture = true;
    v.setAttribute('disableremoteplayback', '');
    v.setAttribute('aria-hidden', 'true');
    v.tabIndex = -1;
    // NO crossOrigin: the source is a same-origin blob:, and setting it has
    // historically broken loads on Safari (video.ts:209-210).
    const offset = 2 + (clip.index % 8) * 3;
    v.style.cssText =
      'position:fixed;right:' + offset + 'px;bottom:0;' +
      'width:2px;height:2px;min-width:2px;min-height:2px;' +
      'opacity:0.01;pointer-events:none;z-index:-1;' +
      'transform:translateZ(0);contain:strict;background:transparent;';

    const onEvent = (e: Event): void => this.onClipEvent(clip, e);
    clip.onEvent = onEvent;
    v.addEventListener('loadedmetadata', onEvent);
    v.addEventListener('loadeddata', onEvent);
    v.addEventListener('canplay', onEvent);
    v.addEventListener('playing', onEvent);
    v.addEventListener('pause', onEvent);
    v.addEventListener('ended', onEvent);
    v.addEventListener('stalled', onEvent);
    v.addEventListener('waiting', onEvent);
    v.addEventListener('resize', onEvent);
    v.addEventListener('error', onEvent);

    // THE AUDIO GRAPH IS BUILT HERE, AT ELEMENT CREATION — NOT when recording
    // starts. `createMediaElementSource` may be called ONCE PER ELEMENT EVER and
    // it re-routes the element's output through the graph; bolting it on later
    // would mean destroying and recreating every <video>, which drops every
    // decoder mid-take. `canvas.captureStream()` carries no audio, so this graph
    // is the ONLY path by which a recording can have sound.
    this.buildAudioChain(clip, v);

    v.src = clip.url;
    if (clip.startTime > 0) { try { v.currentTime = clip.startTime; } catch { /* pre-metadata */ } }
    host.appendChild(v);
    return v;
  }

  private ensureHost(): HTMLElement | null {
    if (this.host) return this.host;
    const doc = this.doc;
    const parent: HTMLElement | null = doc?.body ?? doc?.documentElement ?? null;
    if (!parent) return null;
    const host = doc.createElement('div');
    host.setAttribute('aria-hidden', 'true');
    host.setAttribute('data-collage-stage', 'clips');
    // 0x0 and NOT contained: `contain:paint` here would make this a containing
    // block for the position:fixed children and clip them out of existence.
    host.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;pointer-events:none;z-index:-1;';
    parent.appendChild(host);
    this.host = host;
    return host;
  }

  private onClipEvent(clip: ClipRecord, e: Event): void {
    if (this.destroyed) return;
    const el = clip.el;
    if (!el) return;

    switch (e.type) {
      case 'error': {
        // An eviction (`removeAttribute('src')` + `load()`) can itself raise a
        // MediaError on some engines. `live` is cleared BEFORE that teardown, so
        // an error arriving on a non-live clip is our own doing, not the file's —
        // marking it broken there would permanently demote a healthy clip.
        if (!clip.live) return;
        clip.broken = true;
        clip.error = mediaErrorText(el);
        clip.state = 'error';
        clip.ready = false;
        this.refreshAdmission();
        this.markDirty();
        this.emitStatus();
        return;
      }
      case 'loadedmetadata':
      case 'resize': {
        // Loading a source resets playbackRate to 1 on some engines (WebKit) —
        // restore the video-length-sync speed now that the media is ready.
        try { el.playbackRate = clip.playbackRate; } catch { /* ignore */ }
        const vw = el.videoWidth, vh = el.videoHeight;
        if (vw > 0 && vh > 0 && (vw !== clip.vw || vh !== clip.vh)) {
          clip.vw = vw; clip.vh = vh;
          this.recomputeClipCrops(clip);
          // Real dimensions can change the pixel-budget verdict.
          this.refreshAdmission();
          this.emitStatus();
        }
        if (clip.startTime > 0 && el.currentTime < 0.001) {
          try { el.currentTime = Math.min(clip.startTime, Math.max(0, (el.duration || clip.startTime) - 0.05)); } catch { /* ignore */ }
        }
        this.markDirty();
        return;
      }
      case 'loadeddata':
      case 'canplay':
      case 'playing': {
        if (!clip.ready && el.readyState >= 2) {
          clip.ready = true;
          this.emitStatus();
        }
        this.capturePoster(clip, false);
        if (this.needsGesture && !el.paused) { this.needsGesture = false; this.emitStatus(); }
        this.markDirty();
        return;
      }
      case 'pause':
      case 'ended':
      case 'stalled':
      case 'waiting': {
        // A stalled/ended element still yields its LAST DECODED frame from
        // drawImage, so the composition never goes black. Bank it anyway.
        this.capturePoster(clip, false);
        this.markDirty();
        this.statusPending = true;
        return;
      }
      default:
        return;
    }
  }

  private recomputeClipCrops(clip: ClipRecord): void {
    const items = this.items;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      if (it.clip !== clip) continue;
      this.computeVideoCrop(it, clip.vw, clip.vh);
      this.computePosterCrop(it, clip);
    }
  }

  /** Bank the last good frame so an evicted or dead clip never leaves a hole. */
  private capturePoster(clip: ClipRecord, force: boolean): void {
    const el = clip.el;
    if (!el || el.readyState < 2 || !el.videoWidth) return;
    const now = this.view?.performance?.now ? this.view.performance.now() : Date.now();
    if (!force && clip.poster && now - clip.posterAt < POSTER_REFRESH_MS) return;

    const scale = Math.min(1, POSTER_MAX_DIM / Math.max(el.videoWidth, el.videoHeight));
    const w = Math.max(1, Math.round(el.videoWidth * scale));
    const h = Math.max(1, Math.round(el.videoHeight * scale));
    let cvs = clip.poster;
    if (!cvs) {
      cvs = this.doc.createElement('canvas');
      cvs.width = w; cvs.height = h;
    } else if (cvs.width !== w || cvs.height !== h) {
      cvs.width = w; cvs.height = h;
    }
    const c2 = cvs.getContext('2d');
    if (!c2) return;
    try {
      c2.drawImage(el, 0, 0, w, h);
    } catch {
      return;
    }
    const fresh = clip.poster !== cvs || clip.posterScale !== scale;
    clip.poster = cvs;
    clip.posterAt = now;
    clip.posterScale = scale;
    if (fresh) this.recomputeClipCrops(clip);
  }

  private armRvfc(clip: ClipRecord): void {
    const el = clip.el as RvfcVideo | null;
    if (!el || typeof el.requestVideoFrameCallback !== 'function') return;
    this.cancelRvfc(clip);
    const step = (): void => {
      clip.rvfc = 0;
      if (this.destroyed || !clip.live) return;
      // Cheapest possible signal: mark and re-arm. No draw happens here.
      clip.frameDirty = true;
      this.schedule();
      const v = clip.el as RvfcVideo | null;
      if (v && typeof v.requestVideoFrameCallback === 'function') {
        clip.rvfc = v.requestVideoFrameCallback(step);
      }
    };
    try { clip.rvfc = el.requestVideoFrameCallback(step); } catch { clip.rvfc = 0; }
  }

  private cancelRvfc(clip: ClipRecord): void {
    const el = clip.el as RvfcVideo | null;
    if (clip.rvfc && el && typeof el.cancelVideoFrameCallback === 'function') {
      try { el.cancelVideoFrameCallback(clip.rvfc); } catch { /* ignore */ }
    }
    clip.rvfc = 0;
  }

  // ===========================================================================
  // PLAYBACK + SOUND
  // ===========================================================================

  /**
   * `play()` on a muted, playsinline, in-DOM element autoplays on iOS Safari and
   * Android Chrome — EXCEPT in iOS Low Power Mode, which blocks even muted
   * autoplay and does not always reject the promise. Detection is therefore
   * BEHAVIOURAL: check that currentTime actually moved.
   */
  private tryPlay(clip: ClipRecord): void {
    const el = clip.el;
    if (!el || !clip.live || !clip.wantPlay || clip.broken) return;
    if (!this.visible || !this.onScreen) { if (!this.capturing) return; }
    let p: Promise<void> | undefined;
    try {
      p = el.play();
    } catch {
      this.flagGesture();
      return;
    }
    if (p && typeof p.then === 'function') {
      p.then(() => this.armPlayProbe(clip), () => this.flagGesture());
    } else {
      this.armPlayProbe(clip);
    }
  }

  private armPlayProbe(clip: ClipRecord): void {
    if (clip.probe) this.view.clearTimeout(clip.probe);
    const el = clip.el;
    if (!el) return;
    const t0 = el.currentTime;
    clip.probe = this.view.setTimeout(() => {
      clip.probe = 0;
      const v = clip.el;
      if (!v || !clip.live || !clip.wantPlay || this.destroyed) return;
      if (v.paused || v.currentTime === t0) this.flagGesture();
      else if (this.needsGesture) { this.needsGesture = false; this.emitStatus(); }
    }, PLAY_PROBE_MS);
  }

  private flagGesture(): void {
    if (this.needsGesture) return;
    this.needsGesture = true;
    this.emitStatus();
  }

  /**
   * MUST be called SYNCHRONOUSLY inside a user-gesture handler (no `await`
   * before it): iOS grants the gesture only to calls made in that same task.
   * Resumes the AudioContext, optionally turns sound on, and plays every
   * admitted clip.
   */
  resumeFromGesture(opts?: { sound?: boolean }): void {
    if (this.destroyed) return;
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      try { void this.audioCtx.resume(); } catch { /* ignore */ }
    }
    if (opts && typeof opts.sound === 'boolean') this.soundOn = opts.sound;
    if (this.soundOn) this.ensurePrimaryAudible();
    this.applyMutes();
    this.clips.forEach((clip) => {
      const el = clip.el;
      if (!el || !clip.live || clip.broken) return;
      clip.wantPlay = true;
      try {
        const p = el.play();
        if (p && typeof p.then === 'function') p.then(() => this.armPlayProbe(clip), () => { /* still blocked */ });
      } catch { /* ignore */ }
    });
    this.needsGesture = false;
    this.markDirty();
    this.emitStatus();
  }

  /** Per-clip transport. `wantPlay` survives eviction and re-admission. */
  playClip(clipId: string): void {
    const c = this.clips.get(clipId);
    if (!c) return;
    c.wantPlay = true;
    this.tryPlay(c);
    this.markDirty();
    this.emitStatus();
  }

  pauseClip(clipId: string): void {
    const c = this.clips.get(clipId);
    if (!c) return;
    c.wantPlay = false;
    const el = c.el;
    if (el) { try { el.pause(); } catch { /* ignore */ } }
    this.capturePoster(c, true);
    this.markDirty();
    this.emitStatus();
  }

  playAll(): void { this.clips.forEach((c) => { c.wantPlay = true; this.tryPlay(c); }); this.markDirty(); this.emitStatus(); }

  pauseAll(): void {
    this.clips.forEach((c) => {
      c.wantPlay = false;
      const el = c.el;
      if (el) { try { el.pause(); } catch { /* ignore */ } }
    });
    this.markDirty();
    this.emitStatus();
  }

  /**
   * Per-clip mute. INDEPENDENT by default: unmuting one clip leaves the others
   * exactly as they were.
   *
   * It used to default to `exclusive = true` on the theory that "mixing N
   * tracks is mud". That made per-clip sound a RADIO BUTTON — unmuting B muted
   * A, so two clips could never be heard together and the two-clip state was
   * simply unreachable through the UI. Worse, it is the mixer's own reason for
   * existing: the offline bounce mixes N clips onto one timeline, and a model
   * that permits at most one audible clip caps every export at one track.
   * Whether a mix is mud is the user's call to make and unmake; the control's
   * job is to let them make it.
   *
   * `exclusive` is kept as an opt-in for a caller that genuinely wants solo.
   * Unmuting must still happen inside a user gesture.
   */
  setClipMuted(clipId: string, muted: boolean, exclusive = false): void {
    const target = this.clips.get(clipId);
    if (!target) return;
    target.muted = muted;
    if (!muted && exclusive) this.clips.forEach((c) => { if (c !== target) c.muted = true; });
    if (!muted) this.soundOn = true;
    if (this.audioCtx && this.audioCtx.state === 'suspended') { try { void this.audioCtx.resume(); } catch { /* ignore */ } }
    this.applyMutes();
    this.emitStatus();
  }

  /**
   * GLOBAL sound switch. Turning it ON must happen synchronously inside a user
   * gesture — browsers only autoplay MUTED video, and `muted = false` is only
   * honoured from a gesture. With every clip muted, this unmutes the largest
   * live clip so "sound on" actually produces sound.
   */
  setSound(on: boolean): void {
    this.soundOn = on;
    if (on) {
      if (this.audioCtx && this.audioCtx.state === 'suspended') { try { void this.audioCtx.resume(); } catch { /* ignore */ } }
      this.ensurePrimaryAudible();
    }
    this.applyMutes();
    this.emitStatus();
  }

  get soundEnabled(): boolean { return this.soundOn; }

  private ensurePrimaryAudible(): void {
    let any = false;
    this.clips.forEach((c) => { if (c.live && !c.muted) any = true; });
    if (any) return;
    const first = this.liveClips[0];
    if (first) first.muted = false;
  }

  private applyMutes(): void {
    this.clips.forEach((c) => {
      const audible = this.soundOn && !c.muted && c.live && !c.broken;
      if (c.gain) {
        try { c.gain.gain.value = audible ? 1 : 0; } catch { /* ignore */ }
      }
      const el = c.el;
      if (!el) return;
      // The element's own `muted` still gates the signal entering the WebAudio
      // graph, so it is the real switch; the gain node is the mixer on top.
      el.muted = !audible;
      el.volume = audible ? 1 : 0;
      // The `muted` ATTRIBUTE is left in place on purpose: it is what iOS reads
      // for autoplay eligibility, and removing it buys nothing at runtime.
    });
  }

  private buildAudioChain(clip: ClipRecord, el: HTMLVideoElement): void {
    if (!this.audioEnabled) return;
    if (!this.ensureAudio() || !this.audioCtx || !this.masterGain) return;
    try {
      const src = this.audioCtx.createMediaElementSource(el);
      const gain = this.audioCtx.createGain();
      gain.gain.value = 0;
      src.connect(gain);
      gain.connect(this.masterGain);
      clip.source = src;
      clip.gain = gain;
    } catch {
      // No graph for this clip: it still plays through the element's own output,
      // it just cannot contribute audio to a recording.
      clip.source = null;
      clip.gain = null;
    }
  }

  private ensureAudio(): boolean {
    if (this.audioCtx) return true;
    if (!this.audioEnabled) return false;
    const w = this.view as unknown as { AudioContext?: typeof AudioContext; webkitAudioContext?: typeof AudioContext };
    const AC = w?.AudioContext || w?.webkitAudioContext;
    if (!AC) { this.audioAvailable = false; return false; }
    try {
      const ctx = new AC();
      const master = ctx.createGain();
      master.gain.value = 1;
      master.connect(ctx.destination);
      this.audioCtx = ctx;
      this.masterGain = master;
      this.audioAvailable = true;
      return true;
    } catch {
      this.audioAvailable = false;
      return false;
    }
  }

  // ===========================================================================
  // RECORDING SURFACE
  // ===========================================================================

  /**
   * The canvas + its MediaStream, ready for MediaRecorder.
   *
   * `canvas.captureStream()` carries NO audio, so the audio track comes from the
   * WebAudio graph that was built with each <video> element. Call
   * `setCaptureActive(true)` BEFORE `MediaRecorder.start()`: it freezes the
   * backing size for the whole take (a mid-recording resize changes the track
   * dimensions and wedges some encoders) and forces a heartbeat repaint so a
   * static composition still emits frames.
   */
  captureStream(opts?: { fps?: number; audio?: boolean }): MediaStream {
    if (this.destroyed) throw new Error('Stage: captureStream() after destroy()');
    if (this.stream) return this.stream;
    const cv = this.cv as CaptureCanvas;
    if (typeof cv.captureStream !== 'function') {
      throw new Error('Stage: canvas.captureStream() is not supported in this browser');
    }
    const fps = Math.max(1, finiteOr(opts?.fps, this.captureFps));
    const stream = cv.captureStream(fps);
    if (opts?.audio !== false && this.ensureAudio() && this.audioCtx && this.masterGain) {
      try {
        if (!this.streamDest) {
          this.streamDest = this.audioCtx.createMediaStreamDestination();
          this.masterGain.connect(this.streamDest);
        }
        const tracks = this.streamDest.stream.getAudioTracks();
        for (let i = 0; i < tracks.length; i++) stream.addTrack(tracks[i]);
      } catch { /* video-only recording is still a recording */ }
    }
    this.stream = stream;
    return stream;
  }

  /** True when `captureStream` produced a stream that carries an audio track. */
  get hasAudioTrack(): boolean {
    return !!this.stream && this.stream.getAudioTracks().length > 0;
  }

  /**
   * The clips, described so an OFFLINE render can mix their sound.
   *
   * `renderOffline` seeks decoders instead of playing them, so there is no
   * stream to tap and `captureStream` above is no help: sound has to be decoded
   * and mixed separately (see `offlineAudio.ts`). Everything that mixer needs
   * lives behind private state here, so this is the way out.
   *
   * TWO NUMBERS ARE LOAD-BEARING AND BOTH ARE COMPUTED HERE ON PURPOSE:
   *
   *  - `span` is `seekClipTo`'s own expression, verbatim. If the mixer
   *    recomputed it from `duration` the two timelines would each round the
   *    epsilon their own way and drift apart, and A/V drift is invisible in
   *    review — it only shows up in the finished file.
   *  - `gain` is the user's INTENT (`!muted`), NOT `applyMutes()`'s `audible`.
   *    It used to mirror `audible` exactly, and that was the bug that made
   *    exports silent. `audible` is a statement about the SPEAKERS, so it also
   *    carries two conditions that have no meaning for a file being written:
   *
   *      `soundOn` — the MONITOR switch. It starts false (browsers only
   *        autoplay muted media), so a user who never pressed the speaker
   *        exported silence; and a user who muted their monitor to work in
   *        peace exported silence too, which is the opposite of what muting
   *        your own speakers means.
   *
   *      `live` — the REALTIME DECODER ADMISSION BUDGET (`maxLiveClips` /
   *        `maxLivePixels`). This one is the real damage: the offline mixer
   *        opens its OWN decoder on `url` and never touches the live element,
   *        so it can render sound for a clip this device could not also PLAY.
   *        Gating it on `live` let a realtime resource limit silently decide
   *        what an offline render contains — on a phone, where the budget is 3
   *        clips, importing four videos dropped the fourth's audio with nothing
   *        said. Two guards on one resource, in different units, and the
   *        tighter one quietly became the real limit.
   *
   *    `broken` stays: a clip whose media errored has nothing to decode.
   *
   * `startTime` is deliberately absent: `seekClipTo` does not apply it either.
   */
  describeAudioSources(): {
    id: string; url: string; span: number; loop: boolean; gain: number; rate: number;
  }[] {
    const out: { id: string; url: string; span: number; loop: boolean; gain: number; rate: number }[] = [];
    this.clips.forEach((c) => {
      if (!c.url) return;
      const dur = c.el?.duration;
      const span = Number.isFinite(dur) && (dur as number) > 0
        ? Math.max(OFFLINE_SEEK_EPSILON, (dur as number) - OFFLINE_SEEK_EPSILON)
        : 0;
      const wanted = !c.muted && !c.broken;
      // rate mirrors seekClipTo's video scaling so the export's sound tracks the
      // rate-scaled picture (video-length sync); 1 in LOOP mode leaves it unchanged.
      out.push({ id: c.id, url: c.url, span, loop: c.loop, gain: wanted ? 1 : 0, rate: c.playbackRate > 0 ? c.playbackRate : 1 });
    });
    return out;
  }

  /** Stops the canvas video track. The WebAudio track is reusable and is only detached. */
  releaseStream(): void {
    const s = this.stream;
    if (!s) return;
    const vt = s.getVideoTracks();
    for (let i = 0; i < vt.length; i++) { try { vt[i].stop(); } catch { /* ignore */ } }
    const at = s.getAudioTracks();
    for (let i = 0; i < at.length; i++) { try { s.removeTrack(at[i]); } catch { /* ignore */ } }
    this.stream = null;
  }

  /** Recording gate: freezes the backing size, keeps the loop awake, forces heartbeat frames. */
  setCaptureActive(active: boolean): void {
    if (this.capturing === active || this.destroyed) return;
    this.capturing = active;
    this.applySize(true);
    if (active) {
      this.clips.forEach((c) => { if (c.live && c.wantPlay) this.tryPlay(c); });
      this.markDirty();
    }
    this.emitStatus();
  }

  get isCapturing(): boolean { return this.capturing; }
  /** Frames actually painted since construction — the honest "is it moving" counter. */
  get framesPainted(): number { return this.frames; }

  // ===========================================================================
  // STATUS
  // ===========================================================================

  getStatus(): StageStatus {
    const clips: StageClipStatus[] = [];
    let live = 0;
    let deferred = 0;
    this.clips.forEach((c) => {
      const el = c.el;
      const playing = !!el && c.live && !el.paused && !el.ended && el.readyState >= 2;
      if (c.live) live++;
      else if (c.fragments > 0 && c.state !== 'unused') deferred++;
      clips.push({
        id: c.id,
        name: c.name,
        state: c.state,
        live: c.live,
        playing,
        muted: c.muted,
        wantsAudio: !c.muted && !c.broken,
        audible: this.soundOn && !c.muted && c.live && !c.broken,
        ready: c.ready,
        fragments: c.fragments,
        area: c.area,
        width: c.vw || c.hintW,
        height: c.vh || c.hintH,
        error: c.error,
      });
    });
    clips.sort((a, b) => b.area - a.area);

    let message: string | null = null;
    if (deferred > 0) {
      // NAME THE GUARD THAT ACTUALLY FIRED. This line used to blame the clip
      // cap unconditionally, so a pixel-cap deferral read as "1 of 2 clips
      // playing (this device tops out at 3)" — a self-contradiction that sat
      // on screen while the real cause went unlooked-at. If the sources are
      // simply too big, say THAT, because the user's lever is different: a
      // smaller clip, not fewer of them.
      const byPixels = clips.some((c) => c.state === 'over-pixel-cap');
      const reason = byPixels
        ? 'these clips are too high-resolution to decode together'
        : 'this device tops out at ' + this.capsClips;
      message = live + ' of ' + (live + deferred) + ' clips playing (' + reason +
        ') — the rest show their still frame';
    } else if (this.needsGesture && live > 0) {
      message = 'Tap to start playback';
    }
    const broken = clips.find((c) => c.state === 'error');
    if (broken) message = (message ? message + '. ' : '') + broken.name + ': ' + (broken.error || 'clip failed');

    return {
      running: this.running,
      animating: this.rafId !== 0,
      liveCount: live,
      deferredCount: deferred,
      maxLiveClips: this.capsClips,
      maxLivePixels: this.capsPixels,
      clips,
      needsGesture: this.needsGesture,
      soundOn: this.soundOn,
      audioAvailable: this.audioAvailable,
      capturing: this.capturing,
      message,
    };
  }

  /** Emitted on change only, deduped, and never from inside the draw. */
  private emitStatus(): void {
    if (!this.onStatus || this.destroyed) return;
    const s = this.getStatus();
    let sig = s.running + '|' + s.liveCount + '|' + s.deferredCount + '|' + s.needsGesture + '|' +
      s.soundOn + '|' + s.capturing + '|' + s.audioAvailable + '|' + (s.message || '');
    for (let i = 0; i < s.clips.length; i++) {
      const c = s.clips[i];
      sig += '~' + c.id + ':' + c.state + ':' + c.playing + ':' + c.muted + ':' + c.ready + ':' + c.fragments;
    }
    if (sig === this.statusSig) return;
    this.statusSig = sig;
    this.onStatus(s);
  }

  // ===========================================================================
  // TEARDOWN
  // ===========================================================================

  /** Releases EVERY video element, decoder, object URL we own, observer and rAF. */
  destroy(): void {
    if (this.destroyed) return;
    this.destroyed = true;
    this.running = false;

    if (this.rafId) { try { this.view.cancelAnimationFrame(this.rafId); } catch { /* ignore */ } this.rafId = 0; }
    if (this.ro) { try { this.ro.disconnect(); } catch { /* ignore */ } this.ro = null; }
    if (this.io) { try { this.io.disconnect(); } catch { /* ignore */ } this.io = null; }
    if (this.doc) { try { this.doc.removeEventListener('visibilitychange', this.onVisibility); } catch { /* ignore */ } }

    const s = this.stream;
    if (s) {
      const tracks = s.getTracks();
      for (let i = 0; i < tracks.length; i++) { try { tracks[i].stop(); } catch { /* ignore */ } }
      this.stream = null;
    }

    this.clips.forEach((c) => this.disposeClip(c));
    this.clips.clear();
    this.liveClips = [];
    this.items = [];
    this.stills.clear();   // the URLs belong to the caller; never revoked here

    if (this.host) { try { this.host.remove(); } catch { /* ignore */ } this.host = null; }

    if (this.audioCtx) {
      try { this.masterGain?.disconnect(); } catch { /* ignore */ }
      try { void this.audioCtx.close(); } catch { /* ignore */ }
      this.audioCtx = null;
      this.masterGain = null;
      this.streamDest = null;
    }
  }

  private disposeClip(clip: ClipRecord): void {
    this.cancelRvfc(clip);
    if (clip.probe) { try { this.view.clearTimeout(clip.probe); } catch { /* ignore */ } clip.probe = 0; }
    const el = clip.el;
    if (el) {
      const h = clip.onEvent;
      if (h) {
        el.removeEventListener('loadedmetadata', h);
        el.removeEventListener('loadeddata', h);
        el.removeEventListener('canplay', h);
        el.removeEventListener('playing', h);
        el.removeEventListener('pause', h);
        el.removeEventListener('ended', h);
        el.removeEventListener('stalled', h);
        el.removeEventListener('waiting', h);
        el.removeEventListener('resize', h);
        el.removeEventListener('error', h);
      }
      try {
        el.pause();
        el.removeAttribute('src');
        el.srcObject = null;
        el.load();          // releases the decoder — Safari leaks it for minutes otherwise
      } catch { /* teardown must never throw */ }
      try { el.remove(); } catch { /* ignore */ }
    }
    try { clip.gain?.disconnect(); } catch { /* ignore */ }
    try { clip.source?.disconnect(); } catch { /* ignore */ }
    clip.gain = null;
    clip.source = null;
    clip.el = null;
    clip.onEvent = null;
    clip.live = false;
    clip.ready = false;
    if (clip.poster) { clip.poster.width = 0; clip.poster.height = 0; clip.poster = null; }
    if (clip.ownsUrl && clip.url) { try { URL.revokeObjectURL(clip.url); } catch { /* ignore */ } }
  }
}

/**
 * Create a Stage over a canvas you own.
 *
 * ```ts
 * const stage = createStage(canvasEl, { onStatus: setStageStatus });
 * stage.setScene({ layoutItems, orderedAssets, clips, mode, aspect, zoom, bgColor });
 * stage.start();                       // idles immediately if no clip is live
 * // recording:
 * stage.setCaptureActive(true);
 * const rec = new MediaRecorder(stage.captureStream({ fps: 30 }), { mimeType });
 * // teardown:
 * stage.destroy();
 * ```
 */
export const createStage = (canvas: HTMLCanvasElement, opts: StageOptions = {}): Stage =>
  new Stage(canvas, opts);

export default createStage;
