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

import { calculateSmartCrop, twistedDest, twistOf } from './renderer';
import { isMoving } from './motion';
import { titlePlanFor, drawTitlePlan, type TitlePlan } from './title';
import { cssFilterFor, type LookId } from './grade';
import {
  normaliseWindow, sourceTimeAt, liveWrapTarget,
  type ClipWindow, type WindowedPlayback,
} from './clipWindow';
import { soundtrackSource, soundtrackAudible } from './soundtrack';
import {
  rasterBudgetPx, readDeviceSignals, createRasterLedger, scaleForBudget, rasterDims,
} from './rasterBudget';
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
  /** Seconds; where playback starts on admission. Legacy alias for `inSec` —
   *  it is only read when `inSec` is absent, so there is one meaning and not two. */
  startTime?: number;
  /**
   * TRIM — the IN point, seconds into the source. Absent means 0.
   *
   * The window reaches the live element, the offline video seek and the offline
   * audio mix through ONE function (`lib/clipWindow.ts`), and an untrimmed clip
   * takes a bit-identical path to the code that had no window at all.
   */
  inSec?: number;
  /** TRIM — the OUT point, seconds into the source. Absent means the end. */
  outSec?: number;
  /** Playback speed multiplier. Default 1. Video-length sync uses it so several
   *  clips can share one length — rate<1 slows a clip, rate>1 speeds it up — in
   *  the live preview AND, via `seekClipTo`, in the offline export. */
  playbackRate?: number;
  /** Per-clip mute. Default true — sound needs a user gesture (see `setSound`). */
  muted?: boolean;
  /** Intrinsic size hint used for pixel-budget admission BEFORE `loadedmetadata`. */
  width?: number;
  height?: number;
  /** The caller's own measured duration. Used ONLY when the element cannot
   *  report one — a MediaRecorder WebM has no Duration element and reads
   *  `Infinity` until playback reaches the end. Without it a trimmed clip of
   *  that shape plays untrimmed for the length of the file. */
  durationSec?: number;
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
  /**
   * THE TITLE, as a finished plan in `TITLE_BASIS` space (see `lib/title.ts`).
   * The Stage's logical space IS that basis, so it is drawn at k=1 — and the
   * Stage is what both video exporters record, so this is also the caption on
   * the delivered MP4.
   */
  titlePlan?: TitlePlan | null;
  /**
   * THE LOOK — the colour grade, as a roster id (see `lib/grade.ts`). The Stage
   * is what both video recorders capture, so this is also the grade on the
   * delivered MP4/WebM.
   */
  look?: LookId | null;
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
  /**
   * THE SOUNDTRACK, or null when there is none. `wantsAudio` and `audible` mean
   * exactly what they mean on a clip — intent vs the speakers — and a chip wired
   * to the wrong one is the bug written up on `StageClipStatus.wantsAudio`.
   */
  soundtrack: { name: string; muted: boolean; wantsAudio: boolean; audible: boolean; broken: boolean } | null;
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

/**
 * A clip admitted only for an offline render has to LOAD before it can be
 * seeked. Blob-URL metadata lands in milliseconds, so this ceiling is only ever
 * paid on the first frame and only by a source that is slow or broken — after
 * which the wait is a no-op. Generous, because it is a one-shot cost against the
 * whole render, not a per-frame one.
 */
const OFFLINE_READY_TIMEOUT_MS = 4000;

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
  /** RAW trim points as the caller stated them. The playable window is resolved
   *  from these against `el.duration` on demand (`windowOf`) — never cached,
   *  because the duration arrives asynchronously and a cached window computed
   *  before `loadedmetadata` would be a window against a span of zero. */
  inSec: number | undefined;
  outSec: number | undefined;
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
  /** The app's own measured duration, used only when `el.duration` is not yet
   *  (or never) resolvable. See `spanOf`. */
  hintDur: number;
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
  still: StillSource | null;
  stillKey: string;
  /**
   * THE TWO KEYS THIS FRAGMENT COULD DRAW, both resolved at scene time.
   *
   * `stillKey` is one of these; which one depends on `offlineFullRes`. Keeping
   * both on the item is what lets an offline render swap the whole scene from
   * thumbnails to originals — and back — without a `setScene`, which the Stage
   * could not do anyway: it never stores the scene it was handed.
   */
  previewKey: string;
  fullKey: string;
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
  /**
   * Destination box, shared by every source. `item.bounds` when the slot is
   * square, and the GROWN box from `twistedDest` when it leans — the growth
   * depends only on the cell and the angle, never on which source is drawn, so
   * it is resolved once here instead of three times in the crop helpers.
   */
  dx: number; dy: number; dw: number; dh: number;
  /**
   * Twist, hoisted out of the frame like everything else: radians and the pivot,
   * precomputed at setScene. `tw === 0` is the default and the loop branches on
   * it, so an untwisted composition executes the identical instruction stream it
   * did before twist existed — no save, no translate, no rotate.
   */
  tw: number; tcx: number; tcy: number;
  /** Kept so a late decode / late metadata can recompute without a rescan of the scene. */
  bx: number; by: number; bw: number; bh: number;
  analysis: unknown;
}

/**
 * WHAT A FRAGMENT DRAWS FROM.
 *
 * An `<img>` for the ordinary preview path, and a CANVAS for an offline render
 * that upgraded to the original: the full-resolution decode is rasterised down
 * to the pixels the fragment will really consume and then released, so peak
 * memory is one decode rather than the whole pool. `drawImage` takes either,
 * and `naturalWidth || width` reads either.
 */
type StillSource = HTMLImageElement | HTMLCanvasElement;

/** Intrinsic size of either kind of still source. A canvas has no `natural*`. */
const stillW = (s: StillSource): number =>
  (s as HTMLImageElement).naturalWidth || s.width;
const stillH = (s: StillSource): number =>
  (s as HTMLImageElement).naturalHeight || s.height;

interface StillRecord {
  img: StillSource | null;
  state: 'loading' | 'ready' | 'error';
}

/**
 * WHAT THE ORIGINALS PASS ACTUALLY DID — the offline render's own account of the
 * memory it spent, so "it stayed inside the budget" is a number a test can read
 * rather than a claim a comment makes.
 *
 * `requested = full + fellBack` always: every source the scene asked for either
 * got a raster or kept the thumbnail it was already drawing. There is no third
 * outcome, and that is the property that makes a tight budget safe.
 */
export interface OfflineStillReport {
  /** Distinct originals the scene asked to upgrade. */
  requested: number;
  /** Originals that got a raster of their own. */
  full: number;
  /** Originals still drawing their thumbnail — refused, failed, or out of time. */
  fellBack: number;
  /** Raster pixels the pool was allowed to hold for this take. */
  budgetPx: number;
  /** Raster pixels it actually allocated. Never above `budgetPx`. */
  usedPx: number;
  /** Of `full`, how many were sized by the BUDGET rather than by their geometry. */
  clamped: number;
}

const EMPTY_STILL_REPORT: OfflineStillReport = Object.freeze({
  requested: 0, full: 0, fellBack: 0, budgetPx: 0, usedPx: 0, clamped: 0,
});

/**
 * The device signals, read once per realm. `deviceMemory` never changes and
 * MAX_TEXTURE_SIZE costs a WebGL context to ask for — probing it on every take
 * would spend a context per export for an answer that cannot have moved.
 */
let deviceSignals: ReturnType<typeof readDeviceSignals> | null = null;
const signalsOnce = (): ReturnType<typeof readDeviceSignals> =>
  (deviceSignals ??= readDeviceSignals());

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
  /** THE TITLE, already at this Stage's logical scale. Null draws nothing. */
  private title: TitlePlan | null = null;
  /**
   * THE LOOK, resolved to a CSS filter string ONCE per scene.
   *
   * Resolved here rather than in the draw because `drawFrame` is the frame
   * budget: it builds no strings, allocates nothing and looks nothing up. A
   * cached string assigned to `ctx.filter` is a property write; calling
   * `cssFilterFor` per frame would be a roster lookup and a join, sixty times a
   * second, for a value that only changes when the scene does.
   */
  private gradeCss = 'none';
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

  // --- the move --------------------------------------------------------------
  //
  // THE ONLY CLOCK THE PICTURE ITSELF READS. Every other time in this file is a
  // clip's own playhead; this one is the OUTPUT timeline, which is what
  // `lib/motion.ts` samples a move at.
  //
  //   live    — `tick` advances it from the rAF timestamp, anchored so the
  //             preview starts at rest on the frame the still preview shows.
  //   offline — `renderAtTime` SETS it, exactly as it sets every clip's seek, so
  //             a frame's motion comes from the frame INDEX and not from a
  //             clock. That is the same reason the offline path exists at all.
  //
  /** Output seconds. 0 is rest, and rest is bit-identical to no motion. */
  private outTime = 0;
  /** rAF timestamp of the first frame of this scene; -1 until one has run. */
  private moveOriginMs = -1;
  /** Does ANY fragment in this scene move? False keeps every cost at zero. */
  private moving = false;

  // --- offline render --------------------------------------------------------
  private offline = false;
  private offlineWasRunning = false;
  private offlineWantPlay: string[] = [];
  /** The realtime decoder caps, parked while an offline render lifts them to
   *  admit every clip; restored in `endOfflineRender`. */
  private savedCapsClips = 0;
  private savedCapsPixels = 0;
  /** Was the SOUNDTRACK rolling when the render took the stage? `pauseAll`
   *  stops it like everything else, and only clips have replay bookkeeping. */
  private offlineTrackPlaying = false;
  /**
   * THE BACKING WIDTH FOR THIS RENDER, or 0 for "whatever the Stage was built
   * with". `maxBackingW` is welded to `logicalW` (1200) because nothing ever
   * passed `maxBackingWidth` — which pinned every exported file at 1200px wide
   * no matter what the sources held or the device could encode. An offline
   * render pays no frame-rate budget, so it is the one path that can spend
   * pixels. Frozen for the whole take by `setCaptureActive`; cleared on the way
   * out, so the live preview's own clamp is never touched.
   */
  private offlineMaxW = 0;
  /**
   * DRAW THE ORIGINALS, not the thumbnails, for this render.
   *
   * The Stage draws `previewSrc` — a <=1024px JPEG — everywhere, which is right
   * for a preview and wrong for a file you keep. The STILL export already draws
   * the originals and says why (render.worker.ts: "TWO SOURCES, IN ORDER OF
   * QUALITY"), so the video export drawing thumbnails was the asymmetry: an 8K
   * JPG and a 1200px MP4 out of the same composition. Raising `offlineMaxW`
   * WITHOUT this would be worse than not raising it — a 4K container full of
   * upscaled 1024px thumbnails is a bigger file that is not a better picture.
   */
  private offlineFullRes = false;
  /**
   * ORIGINALS THAT WOULD NOT DECODE, so we stop asking for them.
   *
   * Straight from the still exporter's rule — "a softer fragment beats a hole,
   * every time": an original whose object URL has been revoked renders fine in
   * the preview (that is a different, always-live blob) and fails here. Those
   * fragments fall back to the thumbnail rather than dropping out of the frame.
   */
  private deadOriginals = new Set<string>();

  // --- media -----------------------------------------------------------------
  private host: HTMLElement | null = null;
  /**
   * THE SOUNDTRACK — music under the collage, held as A CLIP WITH NO PICTURE.
   * It owns exactly what a clip owns on the audio side (an element, a
   * MediaElementSource, a gain into `masterGain`, an intent flag) and nothing on
   * the picture side, so every audio seam below treats it as one more source.
   * The URL belongs to the caller and is never revoked here.
   */
  private track: {
    url: string;
    name: string;
    el: HTMLAudioElement | null;
    source: MediaElementAudioSourceNode | null;
    gain: GainNode | null;
    muted: boolean;
    broken: boolean;
  } | null = null;
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
    this.title = titlePlanFor(scene.titlePlan ?? null, this.logicalW);
    this.gradeCss = cssFilterFor(scene.look ?? null);
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
    // THE MOVE, decided ONCE per scene rather than per frame. Everything this
    // flag gates — the per-frame crop refresh, the loop staying alive on a
    // photos-only composition — costs exactly nothing while it is false, which
    // is the state every collage is in until somebody picks a move.
    let moving = false;

    for (let i = 0; i < layout.length; i++) {
      const li = layout[i];
      const asset = ordered[i];
      if (!li || !asset) continue;                       // renderer.ts:73 — same skip

      const path = this.pathFor(li);
      if (!path) continue;

      const b = li.bounds;
      // The grown destination and the pivot, from the SHARED helper in
      // renderer.ts — never a second copy of the |cos|+|sin| arithmetic.
      const d = twistedDest(b, twistOf(asset.analysis));
      if (!moving && isMoving((asset.analysis as { move?: unknown } | null)?.move)) moving = true;
      const clip = this.bindClip(asset, resolve);
      // BOTH KEYS, ALWAYS. The preview is what the live path draws (App.tsx:209
      // draws previewSrc, and so do we); the original is what an offline render
      // asks for. Resolving both here rather than one is what makes
      // `setFullResStills` a swap instead of a re-layout.
      const previewKey = asset.previewSrc || asset.src || '';
      const fullKey = asset.src || asset.previewSrc || '';
      const stillKey = this.stillKeyFor(previewKey, fullKey);
      if (stillKey) wanted.add(stillKey);

      const it: DrawItem = {
        path,
        stroke,
        still: null,
        stillKey,
        previewKey,
        fullKey,
        sok: false,
        isx: 0, isy: 0, isw: 0, ish: 0,
        clip,
        vok: false,
        vsx: 0, vsy: 0, vsw: 0, vsh: 0,
        pok: false,
        psx: 0, psy: 0, psw: 0, psh: 0,
        dx: d.dx, dy: d.dy, dw: d.dw, dh: d.dh,
        tw: d.twist, tcx: d.tcx, tcy: d.tcy,
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
        this.computeStillCrop(it, stillW(rec.img), stillH(rec.img));
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
    // A scene that stops moving must go back to REST, not freeze wherever the
    // last frame left it — the still preview it hands back to is drawn at t=0,
    // and a Stage parked at t=4.2 would hold a visibly different crop.
    if (!moving && this.moving) this.outTime = 0;
    this.moving = moving;
    this.moveOriginMs = -1;
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
  beginOfflineRender(opts: { maxWidth?: number; fullRes?: boolean } = {}): void {
    if (this.destroyed || this.offline) return;
    this.offline = true;
    // BEFORE `setCaptureActive` at the bottom of this method, which is what
    // calls `applySize` and freezes the backing store for the whole take. Set
    // after it and the render would size itself from the OLD value and then
    // never be allowed to change — a mid-stream resize is what corrupts H.264.
    const want = Math.floor(opts.maxWidth ?? 0);
    this.offlineMaxW = Number.isFinite(want) && want >= 240 ? want : 0;
    // Default ON: every caller that asks for an offline render wants the file
    // to hold what the sources hold. `false` is the explicit opt-out (the
    // realtime paths, and any caller that would rather have speed).
    this.offlineFullRes = opts.fullRes !== false;
    // REPOINT, DO NOT FETCH. See `applyStillKeys` — fetching here put every
    // original in memory at once, ahead of the budget that exists to stop
    // exactly that.
    if (this.offlineFullRes) this.applyStillKeys(false);
    this.offlineWasRunning = this.running;
    this.offlineWantPlay = [];
    this.clips.forEach((c) => { if (c.wantPlay) this.offlineWantPlay.push(c.id); });

    // ADMIT EVERY CLIP FOR THE RENDER. The decoder caps exist so REALTIME
    // compositing keeps up with a clock; an offline render has no clock — it
    // seeks, draws and encodes one frame at a time, and `applySize` already
    // lifts the realtime BACKING-WIDTH cap here for exactly that reason. The
    // count/pixel caps are the last realtime budget still leaking into the file:
    // a clip past the cap renders a FROZEN STILL, while its SOUND is mixed in
    // regardless (`describeAudioSources` never respected the cap), so the export
    // plays audio over a picture that never moves. Lift both caps and re-run
    // admission so the deferred clips get a decoder; `endOfflineRender` restores
    // them. A seek on an over-budget decoder degrades to its last frame (the
    // 400 ms `seekClipTo` timeout), never a crash — nothing here PLAYS them.
    this.savedCapsClips = this.capsClips;
    this.savedCapsPixels = this.capsPixels;
    this.capsClips = Number.MAX_SAFE_INTEGER;
    this.capsPixels = 0;                 // 0 disables the pixel guard (refreshAdmission)
    this.refreshAdmission();

    // WHAT WAS ROLLING, BEFORE ANYTHING IS PAUSED. Clips are remembered by
    // `wantPlay` two lines up; the soundtrack has no such flag, and `pauseAll`
    // stops it just the same.
    this.offlineTrackPlaying = !!(this.track && this.track.el && !this.track.el.paused);
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
    // BOTH RENDER LEVERS GO BACK, and they go back HERE rather than being left
    // to the next `beginOfflineRender` to overwrite. `applySize` reads
    // `offlineMaxW` only while `offline` is true, but `offlineFullRes` is read
    // by `stillKeyFor` on every LAYOUT — a leak would leave the live preview
    // decoding full-resolution originals for the rest of the session, which is
    // exactly the frame-rate budget this stays out of.
    this.offlineMaxW = 0;
    const wasFullRes = this.offlineFullRes;
    this.offlineFullRes = false;
    if (wasFullRes) {
      // DROP THE RENDER'S RASTERS, EXPLICITLY.
      //
      // `ensureStills` prunes only when the cache exceeds `wanted.size + 32`,
      // and after a render the map holds one preview key AND one full key per
      // source: a twenty-photo collage sits at 40 entries against a threshold
      // of 52, so nothing would ever be pruned and every raster this take built
      // would outlive it — for the whole session, growing again on the next
      // export at a different size. The eviction rule is right for the live
      // path; it simply cannot see that these entries are a take's scaffolding.
      const items = this.items;
      const live = new Set<string>();
      for (let i = 0; i < items.length; i++) if (items[i].previewKey) live.add(items[i].previewKey);
      const dead: string[] = [];
      this.stills.forEach((_v, k) => { if (!live.has(k)) dead.push(k); });
      for (let i = 0; i < dead.length; i++) this.stills.delete(dead[i]);
      // Originals that failed once are worth trying again next take: a revoked
      // URL is the usual cause, and the pool may well have been reloaded since.
      this.deadOriginals.clear();
      this.applyStillKeys();
    }
    // Put the MOVE back to rest and re-anchor. The render left `outTime` at the
    // last frame it encoded; resuming the live preview from there would drop it
    // mid-cycle for no reason the viewer can see.
    this.outTime = 0;
    this.moveOriginMs = -1;
    // Restore the realtime decoder budget and RELEASE the extra decoders the
    // render admitted, BEFORE replaying: refreshAdmission evicts everything back
    // over the cap, so only clips inside the realtime budget come back live and
    // the replay below (which `tryPlay`-guards on `c.live`) skips the rest.
    this.capsClips = this.savedCapsClips;
    this.capsPixels = this.savedCapsPixels;
    this.refreshAdmission();
    this.setCaptureActive(false);
    const want = new Set(this.offlineWantPlay);
    this.offlineWantPlay = [];
    this.clips.forEach((c) => {
      if (!want.has(c.id)) return;
      c.wantPlay = true;
      this.tryPlay(c);
    });
    // AND GIVE THE MUSIC BACK. `beginOfflineRender` pauses everything and this
    // method replayed only the CLIPS, because clips were the only thing that
    // could be playing when it was written — so the first export left the live
    // soundtrack stopped for good, with no control that revives it (the chip
    // toggles INTENT, and the intent never changed). It needs no gesture: the
    // element was already rolling, which is proof the page had one.
    const tel = this.track?.el;
    if (tel && this.offlineTrackPlaying) {
      try { const p = tel.play(); if (p && typeof p.then === 'function') p.then(() => { /* rolling */ }, () => { /* the tap comes back */ }); } catch { /* ignore */ }
    }
    this.offlineTrackPlaying = false;
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
      // A clip admitted only for this render may not have loaded yet; without
      // metadata its video crop is invalid and the seek has no span, so it would
      // draw a still. Wait for the first frame's worth of metadata (bounded),
      // then seek. A no-op on every later frame — `videoWidth` is known by then.
      await Promise.all(targets.map((c) => this.ensureClipReady(c, opts.signal)));
      await Promise.all(targets.map((c) => this.seekClipTo(c, timeSec, opts.signal)));
    }
    if (this.destroyed) return;
    // THE MOVE, on the OFFLINE timeline — the frame INDEX, never a clock. The
    // whole point of this mode is that a render may take 10 ms or 400 ms per
    // frame and still emit a perfectly even timeline; a move read off
    // `performance.now()` here would put the judder straight back in, encoded
    // into the file, where no amount of re-recording removes it.
    if (this.moving) {
      this.outTime = Number.isFinite(timeSec) ? Math.max(0, timeSec) : 0;
      this.refreshMoveCrops();
    }
    this.dirty = false;
    this.lastDrawAt = -1e9;      // never let the tick's skip-heuristic apply here
    this.drawFrame(0);
    this.frames++;
  }

  /**
   * The clip's PLAYABLE span — `max(EPS, duration - EPS)`, or 0 while the
   * duration is still unknown.
   *
   * Landing strictly inside the media matters: seeking to exactly `duration` is
   * a no-op on some engines and fires `ended` on others, and both paint a frame
   * that was not asked for. Because the trim window is resolved AGAINST this
   * span, that guard now covers a trimmed OUT point for free.
   */
  private spanOf(clip: ClipRecord): number {
    const dur = clip.el?.duration;
    if (Number.isFinite(dur) && (dur as number) > 0) {
      return Math.max(OFFLINE_SEEK_EPSILON, (dur as number) - OFFLINE_SEEK_EPSILON);
    }
    // THE ELEMENT DOES NOT ALWAYS KNOW HOW LONG THE MEDIA IS. A MediaRecorder
    // WebM — a screen recording, or this app's own realtime fallback export —
    // carries no Duration element, so `el.duration` is Infinity until playback
    // walks to the end. The APP already knows the real length (`probeVideo`
    // resolves it with the seek-to-1e101 trick and stores it on `LiveClip`), and
    // without this hint the two disagreed in the worst possible direction: the
    // sheet happily reported "0.6s of 24.0s", while `spanOf` returned 0, the
    // window resolved to `full`, the native loop stayed on and the clip played
    // all 24 seconds — every second the user had cut — until the duration
    // finally resolved. Measured at 21.6 s of un-enforced playback on a 24 s
    // recording; the window scales with the file.
    const hint = clip.hintDur;
    if (Number.isFinite(hint) && hint > 0) {
      return Math.max(OFFLINE_SEEK_EPSILON, hint - OFFLINE_SEEK_EPSILON);
    }
    return 0;
  }

  /**
   * The clip's trim window, resolved NOW. Never cached: `duration` arrives
   * asynchronously, so a window computed at construction would be a window
   * against a span of zero.
   */
  private windowOf(clip: ClipRecord): ClipWindow {
    return normaliseWindow(this.spanOf(clip), clip.inSec, clip.outSec);
  }

  /** Everything `lib/clipWindow.ts` needs to place this clip at an output time. */
  private playbackOf(clip: ClipRecord): WindowedPlayback {
    return { window: this.windowOf(clip), loop: clip.loop, rate: clip.playbackRate };
  }

  /**
   * A trimmed clip cannot use the element's NATIVE loop: that wraps to 0, which
   * is outside the window, so the viewer sees the head of the clip they cut off
   * for however long it takes the watchdog to notice. Untrimmed clips keep the
   * native loop exactly as before and gain nothing to go wrong.
   */
  private applyLoopMode(clip: ClipRecord): void {
    const el = clip.el;
    if (!el) return;
    const windowed = !this.windowOf(clip).full;
    try { el.loop = windowed ? false : clip.loop; } catch { /* re-applied on admission */ }
  }

  /**
   * THE LIVE WATCHDOG. `<video>` has no in/out points, so the window is held by
   * checking the position on frames the compositor is already drawing. The
   * decision itself is `liveWrapTarget` — the same module the offline seek and
   * the audio mix ask — so there is no second opinion about where the clip
   * should be. Returns true if it moved the playhead.
   */
  private enforceWindow(clip: ClipRecord): boolean {
    const el = clip.el;
    if (!el) return false;
    if (this.spanOf(clip) <= 0) return false;          // duration not known yet
    const target = liveWrapTarget(this.playbackOf(clip), el.currentTime);
    if (target === null) return false;
    try { el.currentTime = target; } catch { return false; }
    clip.lastTime = -1;                                 // force a repaint
    return true;
  }

  /**
   * WAIT FOR A JUST-ADMITTED CLIP TO BECOME SEEKABLE. Resolves at once when the
   * dimensions are already known (every frame after the first, and the whole
   * realtime path), and otherwise on the first metadata event or the bounded
   * timeout — so an offline render never encodes a still where the clip should
   * be moving, and a broken source costs one wait, not the render.
   *
   * `videoWidth > 0` is the real gate, not `spanOf`: `spanOf` can be non-zero
   * from the app-supplied `hintDur` before the element has any dimensions, and
   * the video crop (`it.vok`) needs the dimensions.
   */
  private ensureClipReady(clip: ClipRecord, signal?: AbortSignal): Promise<void> {
    const el = clip.el;
    if (!el || clip.broken) return Promise.resolve();
    if (el.videoWidth > 0 && el.readyState >= 1) return Promise.resolve();
    return new Promise<void>((resolve) => {
      let settled = false;
      const done = () => {
        if (settled) return;
        settled = true;
        this.view.clearTimeout(timer);
        el.removeEventListener('loadedmetadata', done);
        el.removeEventListener('loadeddata', done);
        el.removeEventListener('error', done);
        signal?.removeEventListener('abort', done);
        resolve();
      };
      // `onClipEvent` is registered on this element first (in `createVideo`), so
      // on `loadedmetadata` it sets vw/vh and the video crop BEFORE this resolves.
      const timer = this.view.setTimeout(done, OFFLINE_READY_TIMEOUT_MS);
      el.addEventListener('loadedmetadata', done, { once: true });
      el.addEventListener('loadeddata', done, { once: true });
      el.addEventListener('error', done, { once: true });
      signal?.addEventListener('abort', done, { once: true });
    });
  }

  /**
   * One clip, one exact position. Never rejects: a decoder that will not seek
   * costs this frame its motion, not the whole render.
   */
  private seekClipTo(clip: ClipRecord, timeSec: number, signal?: AbortSignal): Promise<void> {
    const el = clip.el;
    if (!el) return Promise.resolve();
    if (this.spanOf(clip) <= 0) return Promise.resolve();

    // ONE FORMULA, THREE TIMELINES. The offline seek, the offline audio mix and
    // the live element all ask `lib/clipWindow.ts` where this clip should be at
    // output time t — including the video-length-sync rate (at rate r a clip
    // advances r seconds of content per composition second) and the trim window.
    // An untrimmed clip resolves to bit-identically the expression that was
    // written inline here before the window existed.
    const target = sourceTimeAt(this.playbackOf(clip), timeSec);

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
      // TRIM. Two float compares per live clip per frame, and only for clips
      // that are actually trimmed — `liveWrapTarget` returns null immediately on
      // a full window, so the untrimmed path costs one branch and no seeks.
      if (this.enforceWindow(c)) needDraw = true;
      if (!el.paused && !el.ended) playing++;
      if (c.frameDirty) { c.frameDirty = false; needDraw = true; }
      else if (el.currentTime !== c.lastTime) needDraw = true;
    }
    if (this.capturing && ts - this.lastDrawAt >= this.captureHeartbeatMs) needDraw = true;

    // THE MOVE, on the LIVE timeline.
    //
    // Anchored to the FIRST tick of this scene rather than read straight off
    // the rAF timestamp, which is monotonic from page load: unanchored, opening
    // the app would drop you at an arbitrary point in the cycle and the preview
    // would not agree with the exported file's opening frame. Anchored, both
    // start at rest, on the picture the still preview is already showing.
    //
    // This is also what keeps a photos-only composition alive. The tick is
    // demand-driven — "nothing playing and nothing dirty -> NO rAF is
    // rescheduled" — which is exactly right for a static collage and exactly
    // wrong for one that is supposed to move, so `moving` joins the conditions
    // that force a frame and the condition that reschedules the loop below.
    if (this.moving && !this.offline) {
      if (this.moveOriginMs < 0) this.moveOriginMs = ts;
      this.outTime = Math.max(0, (ts - this.moveOriginMs) / 1000);
      this.refreshMoveCrops();
      needDraw = true;
    }

    if (needDraw) this.drawFrame(ts);
    if (this.admissionPending) { this.admissionPending = false; this.refreshAdmission(); }
    if (this.statusPending) { this.statusPending = false; this.emitStatus(); }

    if (playing > 0 || this.capturing || this.dirty || (this.moving && !this.offline)) {
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

    // THE LOOK — one property write, after the background and before the
    // fragments, exactly where `renderer.renderCanvas` and the export worker put
    // it. Every item below does save()/clip()/draw/restore(), and restore()
    // returns to THIS state, so one assignment grades the whole frame. Skipped
    // entirely at `'none'`, which is what keeps an ungraded frame the frame it
    // has always been — and keeps the frame budget untouched for everyone who
    // never opens the row.
    const grade = this.gradeCss;
    if (grade !== 'none') ctx.filter = grade;

    const lw = this.lineWidth;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      let painted = false;

      // 1. LIVE VIDEO — the only source that changes between frames.
      const clip = it.clip;
      if (clip !== null && it.vok && !clip.broken && clip.live) {
        const el = clip.el;
        // `clip.ready || readyState >= 2` — NOT `readyState >= 2` alone.
        //
        // A trim wrap is a SEEK, and a seeking element drops to readyState 1 for
        // a frame. Gated on readyState alone the clip then fell through to the
        // extracted-still layer, which holds an import frame from source ~0 —
        // i.e. content strictly BEFORE the IN point the user cut away. Measured
        // per-rAF on the project's own [2.3, 3.6] window: 15 stray frames in
        // 2401, every one red, every one `readyState:1 seeking:true`, spaced
        // exactly one per wrap — 100% of wraps, ~0.8 Hz on a 1.3 s window and up
        // to 6 Hz on a short one, and it reaches a delivered FILE on the realtime
        // recorders. The playhead itself never left the window (0/2401), so this
        // was never a late watchdog; it was the DRAW disowning a live clip
        // mid-seek. `drawImage` on a seeking element still yields the last
        // decoded frame, which is in-window and is the honest thing to hold.
        if (el !== null && (el.readyState >= 2 || clip.ready) && el.videoWidth > 0) {
          ctx.save();
          ctx.clip(it.path);
          // TWIST. The push is OUTSIDE the try and the pop is outside the catch,
          // deliberately: a decoder that throws mid-drawImage must not leave a
          // save on the stack, or every later fragment inherits this fragment's
          // rotation and the whole surface shears one frame at a time.
          if (it.tw !== 0) {
            ctx.save();
            ctx.translate(it.tcx, it.tcy);
            ctx.rotate(it.tw);
            ctx.translate(-it.tcx, -it.tcy);
          }
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
          if (it.tw !== 0) ctx.restore();   // back to cell space; the stroke needs it
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
        if (it.tw !== 0) {
          ctx.save();
          ctx.translate(it.tcx, it.tcy);
          ctx.rotate(it.tw);
          ctx.translate(-it.tcx, -it.tcy);
        }
        ctx.drawImage(it.still, it.isx, it.isy, it.isw, it.ish, it.dx, it.dy, it.dw, it.dh);
        if (it.tw !== 0) ctx.restore();
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
        if (it.tw !== 0) {
          ctx.save();
          ctx.translate(it.tcx, it.tcy);
          ctx.rotate(it.tw);
          ctx.translate(-it.tcx, -it.tcy);
        }
        ctx.drawImage(clip.poster, it.psx, it.psy, it.psw, it.psh, it.dx, it.dy, it.dw, it.dh);
        if (it.tw !== 0) ctx.restore();
        if (it.stroke) {
          ctx.strokeStyle = STROKE_COLOR;
          ctx.lineWidth = lw;
          ctx.stroke(it.path);
        }
        ctx.restore();
      }
    }

    // The grade comes off before the caption — a title is written ON the
    // picture, not in it.
    if (grade !== 'none') ctx.filter = 'none';

    // THE TITLE — after every fragment, before the bookkeeping. One plan, drawn
    // at k=1 because the Stage's logical space IS the plan's basis; `null` costs
    // one branch, which is what keeps an untitled frame the frame it always was.
    if (this.title !== null) drawTitlePlan(ctx, this.title);

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
      // `offlineMaxW` is the size the CALLER asked this render for — it has
      // probed the encoder and knows what this device will accept. 0 means it
      // did not ask, which keeps the old behaviour exactly.
      target = this.offline ? (this.offlineMaxW || this.maxBackingW) : this.captureBackingW;
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
        this.outTime,
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

  /**
   * RE-CROP EVERY FRAGMENT AT THE CURRENT `outTime`.
   *
   * A move makes the source rect a function of time, and the source rect is
   * CACHED on the draw item as eight flat numbers. So somebody has to recompute
   * it, and the choice of where is the whole design:
   *
   *   NOT in `drawFrame`. That loop's contract, written at the top of it, is
   *   "fully synchronous, zero allocation, no promises, no closures, no map
   *   lookups, no string building" — and `calculateSmartCrop` returns an object
   *   literal. Recomputing inside the draw would trade a documented invariant
   *   for a few saved lines, on the one path where the frame budget is the
   *   product.
   *
   *   HERE instead, off the draw, called from `tick` and from `renderAtTime`
   *   immediately before the draw. `drawFrame` is then byte-for-byte the loop
   *   it already was, and the allocation — one small object per fragment per
   *   frame, a few dozen objects, young-generation garbage — is paid only by
   *   compositions that actually move.
   *
   * The still and the video are refreshed SEPARATELY and from their own source
   * dimensions, for the reason `computeVideoCrop` records: a 4K clip's extracted
   * still is 1600 wide while its `videoWidth` is 3840, and one set of numbers
   * cannot address both pixel spaces.
   */
  private refreshMoveCrops(): void {
    const items = this.items;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      if (it.still !== null) {
        const img = it.still;
        this.computeStillCrop(it, stillW(img), stillH(img));
      }
      const clip = it.clip;
      if (clip !== null && clip.vw > 0 && clip.vh > 0) {
        this.computeVideoCrop(it, clip.vw, clip.vh);
        if (clip.poster) this.computePosterCrop(it, clip);
      }
    }
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

  /**
   * WHICH OF THE TWO KEYS THIS FRAGMENT DRAWS RIGHT NOW.
   *
   * Preview everywhere, except inside an offline render that asked for the
   * originals — and even then, an original already known not to decode falls
   * straight back to the thumbnail rather than leaving a hole.
   */
  private stillKeyFor(previewKey: string, fullKey: string): string {
    if (this.offlineFullRes && fullKey && !this.deadOriginals.has(fullKey)) return fullKey;
    return previewKey || fullKey;
  }

  /**
   * SWAP THE WHOLE SCENE BETWEEN THUMBNAILS AND ORIGINALS, in place.
   *
   * Not a `setScene`: the Stage is handed a scene and keeps no copy of it, so
   * there is nothing to re-run. Both keys already live on every DrawItem, so
   * this is a re-point plus a re-bind against the decode cache — the crop is
   * recomputed from the NEW source's intrinsic size, which matters because the
   * thumbnail and the original agree on aspect but not on pixels.
   */
  private applyStillKeys(fetchNow = true): void {
    const wanted = new Set<string>();
    const items = this.items;
    for (let i = 0; i < items.length; i++) {
      const it = items[i];
      const key = this.stillKeyFor(it.previewKey, it.fullKey);
      if (key) wanted.add(key);
      if (key === it.stillKey) continue;
      it.stillKey = key;
      const rec = this.stills.get(key);
      if (rec && rec.state === 'ready' && rec.img) {
        it.still = rec.img;
        this.computeStillCrop(it, stillW(rec.img), stillH(rec.img));
      }
      // Deliberately NOT clearing `it.still` when the new key has not landed:
      // the fragment keeps drawing the thumbnail it already had until the
      // original arrives. A momentarily soft fragment beats a blank one, and
      // `adoptStill` patches the pointer in the instant the decode resolves.
    }
    // `fetchNow: false` REPOINTS WITHOUT FETCHING, and that distinction is the
    // difference between a budget and a decoration.
    //
    // `ensureStills` starts every missing key AT ONCE — `new Image()` per key,
    // all in flight, each decode retained in `this.stills` for the whole take.
    // On the offline path the keys it is handed are the ORIGINALS, so calling
    // it from `beginOfflineRender` launched N full-resolution decodes in
    // parallel BEFORE `prepareOfflineStills` had ranked, budgeted or even
    // counted anything. Thirty 12 MP photos is ~1.4 GB of RGBA resident at
    // once, which is the dead tab this function's own doc comment warns about
    // twenty lines up — the budgeted, one-at-a-time upgrade below was doing
    // careful arithmetic downstream of an allocation that had already happened.
    //
    // So the offline path repoints the keys (which is what makes `adoptStill`
    // land a budgeted raster on the right fragments) and leaves the FETCHING to
    // `prepareOfflineStills`, which does it sequentially, inside the pool, and
    // releases each decode before asking for the next. Fragments keep drawing
    // the thumbnails they already had in the meantime — the same "a softer
    // fragment beats a blank one" rule the loop above relies on.
    if (fetchNow) this.ensureStills(wanted);
    this.markDirty();
  }

  /**
   * FETCH THE ORIGINALS FOR THIS RENDER — one at a time, downsampled to the
   * pixels the frame will really use, and released as we go.
   *
   * THE TRAP THIS AVOIDS, WHICH IS THE REAL REASON THE SIZE AND THE SOURCE ARE
   * ONE CHANGE. The still exporter can draw originals cheaply because it draws
   * ONE, then calls `close()` on it (render.worker.ts). The Stage cannot: an
   * animated frame draws EVERY fragment on every frame, so anything it draws
   * from has to stay resident for the whole take. Pointing `stillKey` at the
   * originals and letting `ensureStills` fetch them would therefore hold N
   * full-resolution decodes at once — twenty 12 MP phone photos is about 975 MB
   * of RGBA, on the same call stack that has just lifted the decoder caps to
   * admit every clip and is about to reallocate the canvas several times
   * larger. That is not a slow export, it is a dead tab.
   *
   * So the upgrade is BUDGETED BY GEOMETRY. A fragment that covers 400x600
   * device pixels cannot show more than about 400x600 pixels of its source no
   * matter how large that source is, so each original is rasterised to the
   * scale its own fragments actually consume at THIS render's width, and the
   * full-resolution decode is dropped immediately.
   *
   * GEOMETRY ALONE IS NOT A CEILING, WHICH IS THE CRASH ABOVE 2K. This comment
   * used to end "and the rasters together are bounded by the canvas area". That
   * is only true for a fragment showing its WHOLE source. A fragment shows a
   * CROP, and asking for `dwPx / isw` of a source that is `k` crops wide
   * rasterises `k * dwPx` — so the raster is k^2 times the destination area,
   * and k = 2 is an ordinary cover-fit. Thirty sources at the 4096 rung with a
   * mean k of 2 is ~180 MB of resident RGBA beside the canvas, the encoder
   * queue and every clip's decoder; at k = 3 it is 400 MB. Nothing bounded the
   * total, so the better the device and the more photos in the collage, the
   * harder it fell over.
   *
   * So there is now a POOL BUDGET on top of the geometry (lib/rasterBudget.ts):
   * a device-derived total, divided fair-share-with-roll-forward, so a greedy
   * source is capped instead of eating the budget and abandoning the tail at
   * preview quality. Degradation bottoms out at the thumbnail that is already
   * bound, so an over-tight budget means "no upgrade happened" — never a frame
   * softer than the preview, never a hole.
   *
   * Sequential on purpose: parallel decodes would put every original in memory
   * at once, which is the thing being avoided.
   *
   * Never throws. Anything that fails, times out, or is cancelled keeps its
   * thumbnail — the still exporter's rule, verbatim: a softer fragment beats a
   * hole, and only a source with neither is a failure.
   */
  async prepareOfflineStills(
    opts: { signal?: AbortSignal; timeoutMs?: number; budgetPx?: number } = {},
  ): Promise<OfflineStillReport> {
    if (this.destroyed || !this.offlineFullRes) return EMPTY_STILL_REPORT;
    const budget = Math.max(0, opts.timeoutMs ?? 20_000);
    const clock = (): number =>
      typeof performance !== 'undefined' && typeof performance.now === 'function'
        ? performance.now() : Date.now();
    const started = clock();

    // HOW MANY DEVICE PIXELS ONE UNIT OF LOGICAL SPACE IS WORTH IN THIS RENDER.
    // The crop maths lives in 1200-space; the canvas is whatever the ladder
    // chose. This is the number that turns "this fragment is 300 logical units
    // wide" into "this fragment is 627 real pixels wide".
    const backingScale = (this.cv.width || this.logicalW) / this.logicalW;

    // The largest scale any fragment needs from each original. Fragments SHARE
    // sources, and two fragments of the same photo can want very different
    // amounts of it, so the raster has to satisfy the hungriest one.
    const need = new Map<string, number>();
    // What each source is drawing RIGHT NOW, in source pixels across. It is the
    // floor a budgeted raster may not go under: the render must never be softer
    // than the preview the user was already looking at.
    const floor = new Map<string, number>();
    for (let i = 0; i < this.items.length; i++) {
      const it = this.items[i];
      if (!it.fullKey || this.deadOriginals.has(it.fullKey)) continue;
      if (it.still) {
        const have = stillW(it.still);
        if (have > (floor.get(it.fullKey) ?? 0)) floor.set(it.fullKey, have);
      }
      // `isw`/`ish` are this fragment's crop in SOURCE pixels, measured against
      // whatever source was bound when the crop was computed. The RATIO of
      // destination pixels to crop pixels is what decides how much source
      // resolution is worth keeping — and it is scale-free, so the thumbnail
      // currently bound is a perfectly good yardstick for the original.
      const dwPx = Math.abs(it.dw) * backingScale;
      const dhPx = Math.abs(it.dh) * backingScale;
      const want = it.sok && it.isw > 0 && it.ish > 0
        ? Math.max(dwPx / it.isw, dhPx / it.ish)
        : 1;
      const prev = need.get(it.fullKey) ?? 0;
      if (want > prev) need.set(it.fullKey, want);
    }

    const requested = need.size;
    if (!requested) return EMPTY_STILL_REPORT;

    // THE POOL. Everything above decided what each source WANTS; this decides
    // what the device can afford to hold at once, and the ledger divides it so
    // no source can eat it and leave the tail on thumbnails.
    const canvasPx = Math.max(0, (this.cv.width || 0) * (this.cv.height || 0));
    const sig = signalsOnce();
    const budgetPx = opts.budgetPx !== undefined && Number.isFinite(opts.budgetPx)
      ? Math.max(0, Math.floor(opts.budgetPx))
      : rasterBudgetPx({
        canvasPx,
        deviceMemoryGb: sig.deviceMemoryGb,
        gpuMaxTextureSize: sig.gpuMaxTextureSize,
      });
    const ledger = createRasterLedger(budgetPx, requested);

    let full = 0;
    let clamped = 0;
    for (const [key, want] of need) {
      if (this.destroyed || opts.signal?.aborted) break;
      if (clock() - started > budget) break;
      const got = await this.upgradeStill(key, want, ledger.capFor(), floor.get(key) ?? 0, opts.signal);
      // Committed for EVERY source, including the ones that took nothing — a
      // missed commit shrinks every later source's share of a budget that was
      // never actually spent.
      ledger.commit(got.px);
      if (got.px > 0) { full++; if (got.clamped) clamped++; }
      else this.deadOriginals.add(key);
    }
    // Anything the budget or an abort never reached keeps its thumbnail too.
    need.forEach((_v, k) => {
      const rec = this.stills.get(k);
      if (!rec || rec.state !== 'ready' || !rec.img) this.deadOriginals.add(k);
    });

    this.applyStillKeys();
    const fellBack = requested - full;
    return { requested, full, fellBack, budgetPx, usedPx: ledger.usedPx, clamped };
  }

  /**
   * DECODE ONE ORIGINAL, KEEP ONLY WHAT WILL BE SEEN, DROP THE REST.
   *
   * `createImageBitmap` where it exists (it decodes off the main thread and
   * `close()` frees deterministically); an `<img>` otherwise, because Safari has
   * shipped both `createImageBitmap` gaps and `decode()` rejections on blob URLs.
   * Either way what lands in the cache is a canvas no larger than the fragments
   * that draw it, so the whole point survives on both paths.
   *
   * `capPx` is this source's slice of the pool and `floorW` the thumbnail it is
   * already drawing. Returns the pixels it actually took — 0 meaning "nothing
   * was allocated, keep the preview", which is a legitimate outcome and never a
   * failure. The caller commits that number against the ledger either way.
   */
  private async upgradeStill(
    key: string,
    wantScale: number,
    capPx: number,
    floorW: number,
    signal?: AbortSignal,
  ): Promise<{ px: number; clamped: boolean }> {
    const NONE = { px: 0, clamped: false };
    if (!key || typeof document === 'undefined') return NONE;
    let bmp: ImageBitmap | null = null;
    let el: HTMLImageElement | null = null;
    try {
      let srcW = 0, srcH = 0;
      let draw: CanvasImageSource | null = null;

      if (typeof createImageBitmap === 'function' && typeof fetch === 'function') {
        const res = await fetch(key);
        if (!res.ok) return NONE;
        const blob = await res.blob();
        if (signal?.aborted || this.destroyed) return NONE;
        bmp = await createImageBitmap(blob);
        srcW = bmp.width; srcH = bmp.height; draw = bmp;
      } else {
        el = await new Promise<HTMLImageElement | null>((resolve) => {
          const img = new Image();
          img.crossOrigin = 'anonymous';
          let settled = false;
          const done = (okay: boolean): void => {
            if (settled) return; settled = true; resolve(okay ? img : null);
          };
          img.onload = () => done(!!(img.naturalWidth || img.width));
          img.onerror = () => done(false);
          img.src = key;
        });
        if (!el) return NONE;
        srcW = el.naturalWidth || el.width; srcH = el.naturalHeight || el.height; draw = el;
      }
      if (!srcW || !srcH || !draw) return NONE;
      if (signal?.aborted || this.destroyed) return NONE;

      // TWO CEILINGS, THE TIGHTER ONE WINS. Geometry says how much of this
      // source a fragment can possibly show; the pool says how much this device
      // can afford to hold while thirty of these sit resident together. Asking
      // geometry alone is what allocated k^2 x the destination area per source
      // and killed the tab above 2K.
      //
      // NEVER UPSCALE — a raster larger than the source is bytes with no
      // picture in them. And never at or below the thumbnail already bound:
      // that would spend a whole allocation to make the fragment no sharper, or
      // softer than the preview the user is looking at. `rasterDims` refuses
      // both, and refusing is the safe outcome — the fragment keeps drawing
      // what it has.
      const scale = scaleForBudget(srcW * srcH, wantScale, capPx);
      const dims = rasterDims(srcW, srcH, scale, floorW, wantScale, capPx);
      if (!dims) return NONE;
      // An original no bigger than what it would be downsampled to is simply
      // used as-is; drawing it through a canvas would only cost a copy.
      const c = document.createElement('canvas');
      c.width = dims.w; c.height = dims.h;
      const cx = c.getContext('2d');
      if (!cx) return NONE;
      cx.drawImage(draw, 0, 0, srcW, srcH, 0, 0, dims.w, dims.h);

      const rec = this.stills.get(key);
      if (rec) { rec.img = c; rec.state = 'ready'; }
      else this.stills.set(key, { img: c, state: 'ready' });
      this.adoptStill(key, c);
      return { px: dims.px, clamped: dims.clamped };
    } catch {
      return NONE;
    } finally {
      // DETERMINISTIC RELEASE. The whole budget argument rests on the
      // full-resolution decode being gone before the next one is asked for.
      if (bmp) { try { bmp.close(); } catch { /* already gone */ } }
      if (el) { el.onload = null; el.onerror = null; el.src = ''; }
    }
  }

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

  private adoptStill(key: string, img: StillSource): void {
    const w = stillW(img);
    const h = stillH(img);
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
          // TRIM IS A LIVE EDIT, not a reason to rebuild the clip. Dragging a
          // handle must not drop the decoder — recreating the element here would
          // also destroy its MediaElementAudioSourceNode, which may be created
          // only ONCE per element, so the clip would come back permanently mute.
          existing.inSec = c.inSec;
          existing.outSec = c.outSec;
          existing.hintW = finiteOr(c.width, existing.hintW);
          existing.hintH = finiteOr(c.height, existing.hintH);
          existing.hintDur = finiteOr(c.durationSec, existing.hintDur);
          if (existing.el) {
            this.applyLoopMode(existing);
            // Guard the assignment: some engines throw if the element is mid-load.
            try { existing.el.playbackRate = existing.playbackRate; } catch { /* re-applied on (re)admission */ }
            // A new IN point that the playhead is already past takes effect on
            // THIS frame, not on the next lap — otherwise moving the handle looks
            // like it did nothing for however long the old window had left.
            this.enforceWindow(existing);
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
      // `startTime` STAYS what it always was: a one-shot seek at admission, read
      // by nothing else. Folding it into `inSec` was the tidier-looking move and
      // it broke the compatibility clause — a caller passing `{startTime: 1.5}`
      // and no trim went from an untrimmed clip that seeks once to a TRIMMED one:
      // native loop off, watchdog engaged, the offline seek rendering [1.5, span]
      // on a loop and the mixer told loopStart 1.5. Nothing in this app passes it
      // (measured), so nothing shipped broken — but "untrimmed behaves
      // bit-identically" has to hold for every input of the exported API, not
      // just the ones the app happens to use.
      inSec: input.inSec,
      outSec: input.outSec,
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
      hintDur: finiteOr(input.durationSec, 0),
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
    // Native loop for an untrimmed clip; the watchdog owns the wrap for a
    // trimmed one. This is set again on `loadedmetadata`, because `duration` —
    // and therefore whether the window is FULL — is not known yet at this line.
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
    // The duration can arrive LONG after metadata (or change), and it is what
    // decides whether the window is real — so it gets the same treatment.
    v.addEventListener('durationchange', onEvent);
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
    // A best-effort jump before metadata. It usually throws (there is nothing to
    // seek in yet), which is why `loadedmetadata` resolves the window again
    // against a span it can actually compute. `startTime` keeps its original
    // meaning here and nowhere else: a one-shot seek at admission.
    const openAt = clip.inSec !== undefined ? clip.inSec : clip.startTime;
    if (openAt > 0) { try { v.currentTime = openAt; } catch { /* pre-metadata */ } }
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
      case 'durationchange':
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
        // THE DURATION IS THE FIRST MOMENT THE WINDOW IS REAL. Everything about
        // trim is resolved against the span, so both decisions that depend on it
        // — which loop mode the element runs in, and whether the playhead is
        // already outside the window — are made here rather than guessed earlier.
        this.applyLoopMode(clip);
        this.enforceWindow(clip);
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
        // A CLIP TRIMMED ONLY AT THE HEAD STILL REACHES THE FILE'S END, and a
        // trimmed clip has the element's native loop turned OFF (it would wrap
        // to 0, outside the window). So `ended` is the trimmed clip's wrap
        // point, and without this it stops dead on the first lap — the one
        // trim shape that the per-frame watchdog alone cannot rescue, because
        // an ended element stops advancing and the tick stops being scheduled.
        if (e.type === 'ended' && clip.live && clip.loop && !this.windowOf(clip).full) {
          if (this.enforceWindow(clip) && clip.wantPlay) this.tryPlay(clip);
        }
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
      // TRIM, ON THE VIDEO'S OWN CLOCK. The window is also held in `tick`, but
      // the tick is the COMPOSITOR's clock and a busy main thread can starve it
      // — measured as a clip running ~0.4s past its OUT point before the next
      // frame was drawn. This callback fires per PRESENTED VIDEO FRAME, which
      // is precisely when a clip can newly be outside its window, so the wrap
      // happens at the earliest moment the fact exists. `liveWrapTarget` returns
      // null instantly for an untrimmed clip, so the default path pays one
      // predictable branch and nothing else.
      this.enforceWindow(clip);
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
    const tel = this.track?.el;
    if (tel) {
      try { const p = tel.play(); if (p && typeof p.then === 'function') p.then(() => { /* rolling */ }, () => { /* still blocked */ }); } catch { /* ignore */ }
    }
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
    const tel = this.track?.el;
    if (tel) { try { tel.pause(); } catch { /* ignore */ } }
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
   * THE SOUNDTRACK — music under the collage. Pass null to remove it.
   *
   * A soundtrack is A CLIP WITH NO PICTURE: it gets the same element → source →
   * gain → `masterGain` chain every clip gets, which is the only path by which a
   * realtime recording can have sound, and it emits the same
   * `describeAudioSources` row the offline mixer already knows how to render.
   *
   * SAME URL MEANS SAME TRACK. Only `muted` is updated then — rebuilding the
   * element would restart the music every time React re-rendered the dock, and
   * `createMediaElementSource` may be called ONCE PER ELEMENT EVER, so a rebuild
   * is also the one operation that cannot be undone cheaply.
   */
  setSoundtrack(spec: { url: string; name?: string; muted?: boolean } | null): void {
    if (this.destroyed) return;
    const url = spec?.url || '';
    if (!url) { this.disposeSoundtrack(); this.emitStatus(); return; }

    if (this.track && this.track.url === url) {
      this.track.name = spec?.name || this.track.name;
      this.track.muted = !!spec?.muted;
      this.applyMutes();
      this.emitStatus();
      return;
    }

    this.disposeSoundtrack();
    this.track = {
      url, name: spec?.name || 'music', el: null, source: null, gain: null,
      muted: !!spec?.muted, broken: false,
    };
    const doc = this.doc;
    const host = this.ensureHost();
    if (!doc || !host) return;

    const el = doc.createElement('audio');
    // Muted FIRST, exactly as `createVideo` does: browsers autoplay muted media
    // and nothing else, and `applyMutes` below is what opens it once the monitor
    // is on inside a gesture.
    el.muted = true;
    el.volume = 0;
    el.setAttribute('muted', '');
    el.loop = true;                 // music laps under a take that outruns it
    el.preload = 'auto';
    el.autoplay = true;
    el.setAttribute('aria-hidden', 'true');
    el.style.cssText = 'position:fixed;left:-9999px;width:1px;height:1px;opacity:0.01;pointer-events:none;z-index:-1;';
    el.addEventListener('error', () => {
      if (this.track && this.track.el === el) { this.track.broken = true; this.emitStatus(); }
    });
    el.addEventListener('canplay', () => this.emitStatus());

    // The graph is built at element creation for the same reason clips build
    // theirs here: `captureStream` taps `masterGain`, and bolting a source on
    // after a take has started is not a thing WebAudio allows.
    if (this.audioEnabled && this.ensureAudio() && this.audioCtx && this.masterGain) {
      try {
        const src = this.audioCtx.createMediaElementSource(el);
        const gain = this.audioCtx.createGain();
        gain.gain.value = 0;
        src.connect(gain);
        gain.connect(this.masterGain);
        this.track.source = src;
        this.track.gain = gain;
      } catch {
        this.track.source = null;
        this.track.gain = null;
      }
    }

    el.src = url;
    host.appendChild(el);
    this.track.el = el;
    try { const p = el.play(); if (p && typeof p.then === 'function') p.then(() => { /* rolling */ }, () => { /* gesture needed */ }); } catch { /* ignore */ }
    this.applyMutes();
    this.emitStatus();
  }

  /**
   * The music's INTENT — "this track is part of the piece". Same contract as
   * `setClipMuted`: it is what the EXPORT renders, and unmuting must happen
   * inside a user gesture for the monitor to follow.
   */
  setSoundtrackMuted(muted: boolean): void {
    if (!this.track) return;
    this.track.muted = muted;
    if (!muted) this.soundOn = true;
    if (this.audioCtx && this.audioCtx.state === 'suspended') { try { void this.audioCtx.resume(); } catch { /* ignore */ } }
    if (!muted) { const el = this.track.el; if (el) { try { const p = el.play(); if (p && typeof p.then === 'function') p.then(() => {}, () => {}); } catch { /* ignore */ } } }
    this.applyMutes();
    this.emitStatus();
  }

  private disposeSoundtrack(): void {
    const t = this.track;
    this.track = null;
    if (!t) return;
    const el = t.el;
    if (el) {
      try { el.pause(); } catch { /* ignore */ }
      // `removeAttribute('src')` + `load()` is what actually releases the
      // decoder; setting `src = ''` re-resolves against the document URL and
      // fires a spurious `error`.
      try { el.removeAttribute('src'); el.load(); } catch { /* ignore */ }
      try { el.remove(); } catch { /* ignore */ }
    }
    try { t.gain?.disconnect(); } catch { /* ignore */ }
    try { t.source?.disconnect(); } catch { /* ignore */ }
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
    // AN UNMUTED SOUNDTRACK ALREADY PRODUCES SOUND, so "sound on" has done its
    // job and there is nothing to rescue. Without this clause, pressing the
    // speaker over a photo collage with music would ALSO unmute a video clip the
    // user had deliberately left silent — this method's whole purpose is that
    // the switch not be a no-op, and music is the switch not being a no-op.
    if (this.track && !this.track.muted && !this.track.broken) return;
    let any = false;
    this.clips.forEach((c) => { if (c.live && !c.muted) any = true; });
    if (any) return;
    const first = this.liveClips[0];
    if (first) first.muted = false;
  }

  private applyMutes(): void {
    const t = this.track;
    if (t) {
      // No `live` term: a soundtrack holds no VIDEO decoder, so the realtime
      // admission budget has nothing to say about it.
      const audible = this.soundOn && !t.muted && !t.broken;
      if (t.gain) { try { t.gain.gain.value = audible ? 1 : 0; } catch { /* ignore */ } }
      const el = t.el;
      if (el) {
        el.muted = !audible;
        el.volume = audible ? 1 : 0;
      }
    }
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
   * The TRIM WINDOW travels as the RAW in/out the user set, not as a resolved
   * window, because the mixer knows something this side does not: the decoded
   * audio buffer's real length. A container does not promise its audio and video
   * streams are the same duration, so the window is resolved once, over there,
   * against the span the sound actually has — through the same
   * `lib/clipWindow.ts` the picture uses.
   *
   * `startTime` is still deliberately absent, exactly as before: it is a one-shot
   * seek at element creation and `seekClipTo` does not apply it either, so a
   * mixer that "helpfully" honoured it would desync the whole export by that
   * offset with nothing on screen to show for it. The TRIM WINDOW is a different
   * thing and IS applied — by both timelines, together.
   */
  describeAudioSources(): {
    id: string; url: string; span: number; loop: boolean; gain: number; rate: number;
    inSec?: number; outSec?: number;
  }[] {
    const out: {
      id: string; url: string; span: number; loop: boolean; gain: number; rate: number;
      inSec?: number; outSec?: number;
    }[] = [];
    this.clips.forEach((c) => {
      if (!c.url) return;
      // 0 when this clip holds no decoder (the realtime admission budget defers
      // it, and it renders as a still) — the mixer then falls back to the
      // decoded buffer's own duration, which is the only span that clip has.
      const span = this.spanOf(c);
      const wanted = !c.muted && !c.broken;
      // rate mirrors seekClipTo's video scaling so the export's sound tracks the
      // rate-scaled picture (video-length sync); 1 in LOOP mode leaves it unchanged.
      out.push({
        id: c.id, url: c.url, span, loop: c.loop, gain: wanted ? 1 : 0,
        rate: c.playbackRate > 0 ? c.playbackRate : 1,
        inSec: c.inSec, outSec: c.outSec,
      });
    });
    // THE SOUNDTRACK IS ONE MORE SOURCE, and the only row here whose `span` is
    // deliberately 0. Every number in it is decided by `lib/soundtrack.ts`,
    // which is also where the reason is written down: music has no picture to
    // agree with, so its window must come from the DECODED buffer rather than
    // from a container duration that differs by an encoder's padding — a
    // difference `audioSchedule` would read as "the sound ends inside the
    // picture's window" and answer with the LAPPED plan.
    const trackRow = soundtrackSource(
      this.track && !this.track.broken
        ? { url: this.track.url, name: this.track.name, durationSec: 0, muted: this.track.muted }
        : null,
    );
    if (trackRow) out.push(trackRow);
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
      // THE MOVE RESTARTS WHEN THE TAKE DOES, so the two recorders agree.
      //
      // The offline render sets `outTime` from the frame INDEX and therefore
      // opens at rest, at t=0. The realtime fallback records the LIVE canvas,
      // whose `outTime` is anchored to the first tick of the scene — so without
      // this the same collage recorded the two ways would open at two different
      // points in the cycle, and which one you got would depend on how long the
      // preview had been on screen before you pressed record.
      this.outTime = 0;
      this.moveOriginMs = -1;
      // AND SO DOES THE MUSIC, for exactly the same reason and it is the same
      // bug. The offline mixer starts the soundtrack at output time 0, i.e. at
      // the top of the track. The realtime recorder captures the LIVE element,
      // which has been looping since the moment it was created — so without this
      // the same collage recorded the two ways opens on two different bars, and
      // which one you get depends on how long the preview sat on screen before
      // the take. `moveOriginMs` above is this same reset for the picture.
      const tel = this.track?.el;
      if (tel) {
        try { tel.currentTime = 0; } catch { /* pre-metadata; it starts at 0 anyway */ }
      }
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
      soundtrack: this.track
        ? {
            name: this.track.name,
            muted: this.track.muted,
            wantsAudio: !this.track.muted && !this.track.broken,
            audible: soundtrackAudible(
              { url: this.track.url, name: this.track.name, durationSec: 0, muted: this.track.muted || this.track.broken },
              this.soundOn,
            ),
            broken: this.track.broken,
          }
        : null,
      capturing: this.capturing,
      message,
    };
  }

  /** Emitted on change only, deduped, and never from inside the draw. */
  private emitStatus(): void {
    if (!this.onStatus || this.destroyed) return;
    const s = this.getStatus();
    let sig = s.running + '|' + s.liveCount + '|' + s.deferredCount + '|' + s.needsGesture + '|' +
      s.soundOn + '|' + s.capturing + '|' + s.audioAvailable + '|' + (s.message || '') + '|' +
      (s.soundtrack ? s.soundtrack.name + ':' + s.soundtrack.muted + ':' + s.soundtrack.broken : '-');
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

    this.disposeSoundtrack();
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
