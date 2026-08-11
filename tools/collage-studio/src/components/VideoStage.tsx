// src/components/VideoStage.tsx
// -----------------------------------------------------------------------------
// THE MOVING COLLAGE — the live sibling of the static <img> preview.
//
// WHAT IT REPLACES
//   The still path is `renderCanvas -> toBlob -> <img src={objectURL}>`: one
//   frame, produced once per state change. That is exactly right for a pool of
//   photographs and it stays the default. The moment a fragment is backed by a
//   LIVE CLIP, a JPEG cannot express the composition any more, so the same
//   composition is painted by `Stage` onto a real canvas that keeps moving.
//
// WHY THIS COMPONENT EXISTS AT ALL (rather than more effects in App)
//   `Stage` owns imperative, non-React resources with strict lifetimes — one
//   <video> decoder per clip, a WeakMap of Path2D contours, an AudioContext, a
//   rAF loop, a ResizeObserver and an IntersectionObserver. Those want ONE
//   owner with ONE mount/unmount pair. Fanning them across App's existing
//   effects is how you get two Stages, two AudioContexts, and a decoder that
//   is never released.
//
// THE THREE THINGS THAT ARE NOT NEGOTIABLE
//   1. iOS GRANTS A GESTURE ONLY TO THE TASK IT FIRED IN. Every call that needs
//      one — `resumeFromGesture`, `setSound(true)`, `captureStream` — runs
//      SYNCHRONOUSLY in the click handler, before the first `await`. Recording
//      is started from that same tap for exactly this reason.
//   2. STAGE OWNS THE AUDIO. It calls `createMediaElementSource` once per
//      <video> at element creation, and that call may never happen twice for an
//      element. So the recorder is handed Stage's finished stream
//      (`RecordOptions.stream`) instead of Stage's elements — see the long note
//      on that option in videoExport.ts.
//   3. THE CALLER MUST KEEP THE CANVAS DIRTY FOR THE WHOLE TAKE. That is what
//      `setCaptureActive(true)` buys: it freezes the backing size and forces
//      heartbeat repaints so a momentarily static composition still emits
//      frames instead of recording a zero-frame track.
// -----------------------------------------------------------------------------

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import {
  Play, Pause, Volume2, VolumeX, Video, Square, Download, Share2, X,
  AlertTriangle, Loader2, Scissors, RotateCcw, Music,
} from 'lucide-react';

import { createStage, type Stage, type StageStatus, type StageClipInput } from '../lib/stage';
import {
  record, probeVideoExportSupport, downloadRecording, revokeRecording,
  getRecordingProfile, remainingSeconds,
  type RecordProgress, type RecordSuccess, type VideoExportSupport,
} from '../lib/videoExport';
import {
  recordFrames, renderOffline, probeFrameExportSupport, probeVideoSizes,
  type FrameExportSupport, type VideoSizeOption,
} from '../lib/frameExport';
import type { ImageAsset, LayoutItem, LayoutMode, LiveClip } from '../types';
import { computeClipPlayback, CLIP_LENGTH_MODES, type ClipLengthMode } from '../lib/videoSync';
import { normaliseWindow, MIN_WINDOW_SEC } from '../lib/clipWindow';
import {
  soundtrackLength, soundtrackClock, soundtrackWindow, soundtrackRangeLabel, SOUNDTRACK_ID,
} from '../lib/soundtrack';
import { fadeLabel, nextFade, fadeSpan } from '../lib/fade';
import type { TitlePlan } from '../lib/title';
import type { LookId } from '../lib/grade';

/** The user's raw trim points for one clip. Absent = the whole clip. */
type TrimMap = Record<string, { inSec: number; outSec: number } | undefined>;

/** Seconds, one decimal, no trailing noise — the field readout, not a timecode. */
const secs = (n: number): string => `${n.toFixed(1)}s`;

/** Button copy for the video-length-sync control (shown with 2+ clips). */
const CLIP_LENGTH_LABEL: Record<ClipLengthMode, { short: string; aria: string; title: string }> = {
  'loop':            { short: 'LOOP',    aria: 'Loop clips at natural speed',  title: 'Each clip plays at its own speed and loops. The longest clip sets the visible period; shorter clips repeat within it. Nothing is sped up or slowed down.' },
  'stretch-longest': { short: 'STRETCH', aria: 'Stretch clips to the longest', title: 'Slow every clip to the LONGEST clip’s length so they share one period, in phase. Shorter clips run in slow motion.' },
  'speed-shortest':  { short: 'SPEED',   aria: 'Speed clips to the shortest',  title: 'Speed every clip up to the SHORTEST clip’s length. The whole collage turns over on the shortest clip’s clock.' },
};

export interface VideoStageProps {
  layoutItems: LayoutItem[];
  /** `shuffledIndices.map(i => images[i])` — memoise it, or every render rebuilds the draw list. */
  orderedAssets: (ImageAsset | undefined)[];
  clips: LiveClip[];
  mode: LayoutMode;
  aspect: number;
  zoom: number;
  bgColor: string;
  /**
   * THE TITLE, as a finished plan (see `lib/title.ts`). Passed through to the
   * Stage untouched — it is also what both video exporters record, so this is
   * the caption that ends up in the file.
   */
  titlePlan?: TitlePlan | null;
  /**
   * THE LOOK — the colour grade, passed straight through to the Stage. This is
   * the surface both video recorders capture, so it is also the grade on the
   * delivered file rather than only on the picture on screen.
   */
  look?: LookId | null;
  /** Surfaced so the parent can show one consistent notice strip. */
  onNotice?: (msg: string) => void;
  /**
   * The compositor could not start on this device (no 2D context). The parent
   * must fall back to the still preview — a live mode that paints nothing is
   * strictly worse than the JPEG it replaced.
   */
  onUnavailable?: () => void;
  /**
   * DOM node in the control dock to render the transport into. The stage's
   * chrome is portalled OUT of the canvas box on purpose: a persistent bar
   * floating over the collage covers the artwork, which is the one thing the
   * screen exists to show. Null renders no transport at all (the canvas still
   * plays) rather than silently falling back to an overlay.
   */
  controlsHost?: HTMLElement | null;
  /** Drop a clip back to its stills. Rendered in the dock beside its sound toggle. */
  onRemoveClip?: (id: string) => void;
  /**
   * THE SOUNDTRACK — music under the collage, handed straight to the Stage,
   * which holds it as a clip with no picture. Null means no music.
   */
  soundtrack?: { url: string; name: string; durationSec: number; muted?: boolean; inSec?: number; outSec?: number } | null;
  /**
   * THE MUSIC'S RANGE moved. `undefined` means the whole track — the same
   * "absent is the default" the clip trims and `normaliseWindow` both use, so
   * "All" is one call and not a special case anywhere downstream.
   *
   * It lives in App state rather than in this component's `trims` map because the
   * soundtrack is App's to own (App holds the blob url and revokes it), and a
   * range held here would silently reset every time the dock unmounted.
   */
  onSoundtrackWindow?: (v: { inSec: number; outSec: number } | undefined) => void;
  /** Remove the music. The URL belongs to the parent, which revokes it. */
  onRemoveSoundtrack?: () => void;
  /** The music's INTENT changed. The parent owns it; the Stage is re-fed from
   *  it whenever a Stage is (re)built. */
  onSoundtrackMuted?: (muted: boolean) => void;
  /**
   * The WHOLE asset pool, used for one thing: the trim sheet's filmstrip.
   *
   * Deliberately not `orderedAssets` — that is the DRAW list, and with a locked
   * fragment count it is a subset, so a trimmed clip's strip would silently lose
   * frames as the layout changed. Every frame this clip ever gave us is already
   * in memory with its `sourceTime` on it; the strip costs no decoder and no
   * network, which is the only reason it can exist on a phone at all.
   */
  poolAssets?: ImageAsset[];
  /**
   * Filled with a handle so the Export sheet can start a take. It has to be
   * IMPERATIVE: iOS grants a gesture only to the task it fired in, so the export
   * button must reach `startRecording` synchronously inside its own onClick — a
   * prop change routed through an effect arrives a task too late and records
   * silently, or not at all.
   */
  recorderRef?: React.MutableRefObject<StageRecorder | null>;
}

export interface StageRecorder {
  start: (seconds?: number, renderWidth?: number) => void;
  canRecord: boolean;
  isRecording: boolean;
  maxSeconds: number;
  /**
   * THE SIZES THIS DEVICE WILL ACTUALLY ENCODE at the current composition's
   * shape, probed rung by rung. Empty until the probe lands — the sheet renders
   * the row only once there is something true to put in it.
   */
  sizes: VideoSizeOption[];
  /**
   * True when the take will be RENDERED offline rather than captured live. Only
   * the offline path can spend pixels, so it is the only one the ladder applies
   * to, and the sheet should not offer a choice it cannot honour.
   */
  canChooseSize: boolean;
}

/**
 * THE TRIM SHEET — pick the part of a clip that is actually good.
 *
 * SHAPE, and why it is this one. The CapCut idiom is two handles dragged along a
 * filmstrip, and a hand-rolled dual-handle track is exactly the control that
 * breaks on a phone, in a browser nobody tested, with a thumb instead of a
 * mouse. So: the FILMSTRIP is the picture (it shows what you are cutting, which
 * is the part a slider cannot say), and the two handles are ordinary
 * `<input type="range">` — native touch behaviour, native keyboard support, a
 * real accessible name, and no chance of a hit target that only works with a
 * pointer. The window is drawn ON the strip, so the control still reads as one
 * gesture rather than two numbers.
 *
 * The strip costs nothing: these are the frames the clip already handed over on
 * import, `sourceTime` and all. No second decoder — which is the difference
 * between a trim UI that works on a phone with three clips open and one that
 * evicts a live decoder to draw itself.
 *
 * IT TAKES A NAME AND A SPAN, NOT A CLIP, because the second thing that needed a
 * range was the MUSIC ("need a way to click it and select the range", from the
 * field) and a soundtrack is a clip with no picture. Everything this sheet was
 * already doing — the two native handles, the modal it had to become, the
 * focus trap, the both-handles-stop-at-each-other rule that a ratcheting OUT
 * point taught it — is the same work for a song, and the second instance of a
 * shape is where this project extracts the engine instead of forking a page.
 *
 * AND THE STRIP STAYS HONEST WHEN THERE IS NO PICTURE. The tempting move for
 * audio is a waveform, which means decoding the whole file to draw a control —
 * exactly the second decoder the paragraph above exists to refuse, and on the one
 * import most likely to be a 5 MB song on a phone. So a track with no frames gets
 * a RULER instead: minute marks against the same time axis, which is the actual
 * question you are asking a song ("where is 1:30?") and costs nothing to answer.
 */
const TrimSheet: React.FC<{
  /** What is being cut, for every label in here. */
  name: string;
  /** Its length in seconds — the x-axis of the strip and the max of both handles. */
  span: number;
  frames: ImageAsset[];
  value: { inSec: number; outSec: number } | undefined;
  onChange: (v: { inSec: number; outSec: number } | undefined) => void;
  onClose: () => void;
  /** CREDIT ON THE PAGE, where the thing they asked for is — not only in
   *  credits.json. Absent on the clip sheet, which nobody wished into being. */
  credit?: string;
}> = ({ name, span, frames, value, onChange, onClose, credit }) => {
  const closeRef = useRef<HTMLButtonElement>(null);
  const w = normaliseWindow(span, value?.inSec, value?.outSec);
  // A step fine enough to land on a beat, coarse enough that a thumb can hit it.
  const step = span > 60 ? 0.1 : 0.01;
  const pct = (t: number) => (span > 0 ? Math.max(0, Math.min(100, (t / span) * 100)) : 0);

  // BOTH HANDLES STOP AT EACH OTHER. `setOut` always clamped against IN;
  // `setIn` clamped only against the end of the clip, and that asymmetry was not
  // cosmetic — an IN dragged past OUT reached `normaliseWindow`, whose repair
  // grows OUT FORWARD, so OUT ratcheted along behind the thumb and the user's
  // chosen OUT was destroyed. Measured: select 0→2.0, drag IN rightwards, and
  // the window pins at the 0.15 s floor wherever you let go, with OUT following;
  // dragging back left does not restore it, because the ratcheted value is now
  // the stored one. `normaliseWindow`'s repair is a last resort for values the
  // UI did not author (a restored project, the exported API) — never the routine
  // path for an ordinary drag.
  const setIn = (v: number) => onChange({ inSec: Math.min(v, w.outSec - MIN_WINDOW_SEC), outSec: w.outSec });
  const setOut = (v: number) => onChange({ inSec: w.inSec, outSec: Math.max(v, w.inSec + MIN_WINDOW_SEC) });

  /**
   * A REAL MODAL, because this one is not decoration.
   *
   * The sheet started as `role="dialog"` and nothing else — no `aria-modal`, no
   * initial focus, no trap, no Escape, while the app's other three sheets all
   * close on Escape. Every Tab walked into the page behind it, INCLUDING the
   * take controls: measured 14/14 tab stops landing outside, one of them
   * "Record video". Reaching it defeats the `busy` guard that disables the trim
   * chip precisely so the window cannot change mid-render — a take was started
   * behind the open sheet and the sliders stayed live, baking TWO different
   * windows into one exported file (decoded: green, green, green, green, green,
   * RED). And the result modal is z-[300] under this sheet's z-[320], so the
   * finished video's Save button was then unreachable — the same covered-button
   * class already scarred into this file further down.
   */
  /**
   * MOUNT ONLY — and the empty dep list is the whole point, not a lint smell.
   *
   * The first version depended on `[onClose]`, which is an inline arrow rebuilt
   * on every VideoStage render, so every slider `onChange` re-ran the effect and
   * called `closeRef.current?.focus()` again — pulling focus OFF the handle the
   * user was operating. Measured on the real page with the keyboard only: the
   * IN handle moved 0 -> 0.01 on the first ArrowRight, focus jumped to "Close
   * trim", and the next four presses did nothing; Enter — the natural "confirm"
   * — then dismissed the sheet. A drag was unaffected (the range keeps pointer
   * capture through the steal), which is exactly why looking at it proves
   * nothing and only a keyboard run finds it. `onClose` is read through a ref so
   * Escape still calls the CURRENT handler without the effect having to re-run.
   */
  const closeFn = useRef(onClose);
  closeFn.current = onClose;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') closeFn.current(); };
    document.addEventListener('keydown', onKey);
    closeRef.current?.focus();
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  /** Keep Tab inside the dialog. Cheaper and more robust than `inert`, which
   *  needs a polyfill on the engines this app actually has to serve. */
  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key !== 'Tab') return;
    const focusable = Array.from(
      e.currentTarget.querySelectorAll<HTMLElement>('button, input, [href], select, textarea, [tabindex]:not([tabindex="-1"])'),
    ).filter((el) => !el.hasAttribute('disabled'));
    if (!focusable.length) return;
    const first = focusable[0], last = focusable[focusable.length - 1];
    const active = document.activeElement as HTMLElement | null;
    if (e.shiftKey && (active === first || !e.currentTarget.contains(active))) {
      e.preventDefault(); last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault(); first.focus();
    }
  };

  return createPortal((
    <div
      className="fixed inset-0 z-[320] bg-black/80 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-5"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={`Trim ${name}`}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={onKeyDown}
        className="w-full sm:max-w-lg bg-[#0e0e0e] border-t sm:border border-white/15 sm:rounded-2xl p-4 pb-6 sm:pb-4 flex flex-col gap-3"
      >
        <div className="flex items-center gap-2 min-w-0">
          <Scissors size={13} className="text-emerald-400 shrink-0" />
          <span className="text-[10px] font-black tracking-[0.2em] text-white uppercase shrink-0">Trim</span>
          <span className="text-[10px] text-gray-500 truncate min-w-0" title={name}>{name}</span>
          <div className="flex-1" />
          <button
            ref={closeRef}
            onClick={onClose}
            aria-label="Close trim"
            className="w-11 h-11 -mr-2 rounded-lg text-gray-400 flex items-center justify-center hover:text-white hover:bg-white/10 transition-colors shrink-0"
          ><X size={16} /></button>
        </div>

        {/* THE STRIP, AND ITS X-AXIS IS TIME.
            Laying the frames out with equal widths is the obvious move and it
            makes the control LIE: extraction is `strategy: 'smart'`, so the
            frames it hands back are clustered wherever the clip was
            interesting, and a six-second clip came back with nine frames from
            its first third. Spread equally, that third fills three quarters of
            the strip while the window bracket — which is positioned by TIME —
            sits somewhere else entirely, so the pictures under the handles are
            not the pictures you are about to cut to.
            Each frame therefore covers the stretch of the clip it is the
            NEAREST frame to: boundaries at the midpoints between adjacent
            `sourceTime`s, first frame back to 0, last frame out to the end. */}
        <div className="relative h-16 rounded-lg overflow-hidden bg-[#050505] border border-white/10">
          <div className="absolute inset-0" aria-hidden="true">
            {frames.length > 0 ? frames.map((f, i) => {
              const t = (k: number) => frames[k]?.sourceTime ?? ((k + 0.5) / frames.length) * span;
              const from = i === 0 ? 0 : (t(i - 1) + t(i)) / 2;
              const to = i === frames.length - 1 ? span : (t(i) + t(i + 1)) / 2;
              return (
                <img
                  key={f.id ?? i}
                  src={f.previewSrc || f.src}
                  alt=""
                  className="absolute inset-y-0 h-full object-cover"
                  style={{ left: `${pct(from)}%`, width: `${Math.max(0, pct(to) - pct(from))}%` }}
                  draggable={false}
                />
              );
            }) : (
              /* NO FRAMES — the soundtrack, and anything else with a length but
                 no picture. A flat gradient is a strip that says nothing, and a
                 range you cannot place in the song is barely a range at all. So
                 the axis gets marks: every minute on a long track, every ten
                 seconds on a short one, capped so a 40-minute mix does not draw
                 forty lines into a 16px-high box. */
              <div className="absolute inset-0 bg-gradient-to-r from-[#141414] to-[#1e1e1e]">
                {(() => {
                  const stepSec = span > 600 ? 300 : span > 120 ? 60 : span > 30 ? 10 : 5;
                  const marks: number[] = [];
                  for (let t = stepSec; t < span && marks.length < 24; t += stepSec) marks.push(t);
                  return marks.map((t) => (
                    <div
                      key={t}
                      className="absolute inset-y-0 w-px bg-white/15"
                      style={{ left: `${pct(t)}%` }}
                    >
                      <span className="absolute top-0.5 left-1 text-[8px] tabular-nums text-white/35">
                        {soundtrackClock(t)}
                      </span>
                    </div>
                  ));
                })()}
              </div>
            )}
          </div>
          {/* Everything OUTSIDE the window is dimmed — the cut is the thing you
              see, not a number you have to translate. The opacity is a STANDARD
              Tailwind step: `bg-black/72` is not one, generates no rule, and the
              dimming silently did not exist. Caught by looking at a screenshot,
              which is the only thing that can catch it. */}
          <div
            className="absolute inset-y-0 left-0 bg-black/70 pointer-events-none"
            style={{ width: `${pct(w.inSec)}%` }}
            aria-hidden="true"
          />
          <div
            className="absolute inset-y-0 right-0 bg-black/70 pointer-events-none"
            style={{ width: `${100 - pct(w.outSec)}%` }}
            aria-hidden="true"
          />
          <div
            className="absolute inset-y-0 border-x-2 border-emerald-400 pointer-events-none"
            style={{ left: `${pct(w.inSec)}%`, width: `${Math.max(0, pct(w.outSec) - pct(w.inSec))}%` }}
            aria-hidden="true"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="flex items-center gap-2">
            <span className="text-[9px] font-black tracking-[0.15em] text-emerald-400 w-8 shrink-0">IN</span>
            <input
              type="range" min={0} max={span} step={step} value={w.inSec}
              onChange={(e) => setIn(parseFloat(e.target.value))}
              aria-label={`In point for ${name}`}
              /* `--fill` IS NOT OPTIONAL: the app's global range track is a
                 gradient stopped at `var(--fill, 50%)`, so a slider that never
                 sets it paints exactly half green FOREVER. On an untrimmed clip
                 that put the OUT handle at the far right above a half-full bar
                 — the value indicator contradicting the handle it belongs to.
                 A default that renders is worse than one that does not. */
              style={{ ['--fill' as string]: `${pct(w.inSec)}%` } as React.CSSProperties}
              className="flex-1 min-w-0 h-11 accent-emerald-400 bg-transparent cursor-pointer"
            />
            <span className="text-[10px] text-gray-300 tabular-nums w-12 text-right shrink-0">{secs(w.inSec)}</span>
          </label>
          <label className="flex items-center gap-2">
            <span className="text-[9px] font-black tracking-[0.15em] text-emerald-400 w-8 shrink-0">OUT</span>
            <input
              type="range" min={0} max={span} step={step} value={w.outSec}
              onChange={(e) => setOut(parseFloat(e.target.value))}
              aria-label={`Out point for ${name}`}
              style={{ ['--fill' as string]: `${pct(w.outSec)}%` } as React.CSSProperties}
              className="flex-1 min-w-0 h-11 accent-emerald-400 bg-transparent cursor-pointer"
            />
            <span className="text-[10px] text-gray-300 tabular-nums w-12 text-right shrink-0">{secs(w.outSec)}</span>
          </label>
        </div>

        <div className="flex items-center gap-2">
          <span
            className="text-[10px] tracking-wide text-gray-400 tabular-nums min-w-0 truncate"
            data-testid="trim-readout"
          >
            <span className="text-white font-black">{secs(w.length)}</span> of {secs(span)}
            {w.full ? ' · all of it' : ` · ${secs(w.inSec)}→${secs(w.outSec)}`}
          </span>
          <div className="flex-1" />
          <button
            onClick={() => onChange(undefined)}
            disabled={w.full}
            aria-label={`Use all of ${name}`}
            className="h-11 px-3 rounded-lg text-[9px] font-black tracking-[0.15em] uppercase text-gray-400 border border-white/10 flex items-center gap-1.5 hover:text-white hover:bg-white/10 disabled:opacity-30 disabled:pointer-events-none transition-colors shrink-0"
          ><RotateCcw size={12} /> All</button>
          <button
            onClick={onClose}
            className="h-11 px-4 rounded-lg bg-white text-black text-[9px] font-black tracking-[0.2em] uppercase hover:bg-emerald-400 transition-colors shrink-0"
          >Done</button>
        </div>

        {/* CREDIT ON THE PAGE, next to the thing they asked for — the ledger in
            credits.json is permanent, but nobody reads a JSON file. */}
        {credit && (
          <p className="text-[9px] tracking-wide text-gray-600 leading-relaxed">{credit}</p>
        )}
      </div>
    </div>
  ), document.body);
};

/** Offered take lengths. Clamped to the device cap, so a phone never sees 30s. */
const DURATION_CHOICES = [5, 10, 15, 30] as const;

const fmtBytes = (b: number): string =>
  b < 1024 * 1024 ? `${Math.max(1, Math.round(b / 1024))} KB` : `${(b / (1024 * 1024)).toFixed(1)} MB`;

type RecPhase = 'idle' | 'running' | 'saving';

export const VideoStage: React.FC<VideoStageProps> = ({
  layoutItems, orderedAssets, clips, mode, aspect, zoom, bgColor, titlePlan, look, onNotice, onUnavailable,
  controlsHost, onRemoveClip, recorderRef, poolAssets, soundtrack, onRemoveSoundtrack, onSoundtrackMuted,
  onSoundtrackWindow,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stageRef = useRef<Stage | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  /** Kept in a ref as well as state: the click handler must read it synchronously. */
  const soundRef = useRef(false);

  const [status, setStatus] = useState<StageStatus | null>(null);
  const [support, setSupport] = useState<VideoExportSupport | null>(null);
  const [frameSupport, setFrameSupport] = useState<FrameExportSupport | null>(null);
  const [recPhase, setRecPhase] = useState<RecPhase>('idle');
  const [progress, setProgress] = useState<RecordProgress | null>(null);
  const [result, setResult] = useState<RecordSuccess | null>(null);
  const [seconds, setSeconds] = useState(10);
  /**
   * THE FADE, in seconds, as REQUESTED — `lib/fade` clamps it against whatever
   * take actually runs.
   *
   * It lives HERE, beside the take length, and that placement is the decision:
   * a fade is a property of the RENDER, exactly as the take length is, so it
   * shares its state, its bar and its lifetime and rides in no project file, no
   * dice roll and no composition code. Both entry points — this bar's record
   * button and the export sheet's — go through `startRecording`, so one piece
   * of state answers for both and neither can disagree with the other.
   *
   * Starts at 0 (OFF), which is what makes every export produced before this
   * existed reproducible today.
   */
  const [fadeSec, setFadeSec] = useState(0);

  const profile = useMemo(() => getRecordingProfile(), []);
  const durations = useMemo(
    () => DURATION_CHOICES.filter((d) => d <= profile.maxSeconds),
    [profile.maxSeconds],
  );

  // --- Stage lifetime: exactly one, for the life of the mount ----------------
  useEffect(() => {
    const cv = canvasRef.current;
    if (!cv) return;
    let stage: Stage;
    try {
      // Throws when the canvas has no 2D context — a locked-down or
      // out-of-memory realm. Falling back beats rendering an empty box.
      stage = createStage(cv, { onStatus: setStatus });
    } catch {
      onUnavailable?.();
      return;
    }
    stageRef.current = stage;
    stage.start();
    // A NEW STAGE KNOWS NOTHING. Every imperative thing handed to a Stage —
    // the scene, and now the music — is pushed by an effect keyed on the VALUE
    // pushed, so a Stage that is destroyed and rebuilt while those values sit
    // unchanged never receives them again. `setScene` gets away with it because
    // its inputs change on almost every render; a soundtrack does not change
    // for minutes at a time. Bumping a generation gives every such effect an
    // honest dependency on "which Stage is this".
    setStageGen((n) => n + 1);
    return () => {
      // Order matters: abort any take BEFORE destroy, or the recorder keeps
      // pulling frames from a canvas whose decoders have just been released.
      abortRef.current?.abort();
      stage.destroy();
      stageRef.current = null;
    };
  }, []);

  // --- capability: probe once, HERE ------------------------------------------
  // Not at app boot. This component only mounts once a clip exists, which is
  // also the first moment the answer can matter — and the ~0.5s dry-run take is
  // then already cached by the time the user reaches for Record.
  useEffect(() => {
    let alive = true;
    // BOTH paths, because the answer decides which button the user even gets.
    probeVideoExportSupport().then((s) => { if (alive) setSupport(s); });
    probeFrameExportSupport().then((s) => { if (alive) setFrameSupport(s); });
    return () => { alive = false; };
  }, []);

  // Video-length sync mode. 'loop' (default) leaves every clip at its own speed;
  // the two stretch modes rescale so all clips share one length. See videoSync.ts.
  const [clipLengthMode, setClipLengthMode] = useState<ClipLengthMode>('loop');

  /** Bumped every time a Stage is constructed — see the note in that effect. */
  const [stageGen, setStageGen] = useState(0);

  /**
   * TRIM — the user's in/out points, per clip. Session state, exactly like the
   * clips themselves: a `.collage` project stores photos and layout, and the
   * clips it was built from are re-imported by hand, so persisting a window for
   * a clip that will not be there is a promise the file cannot keep.
   */
  const [trims, setTrims] = useState<TrimMap>({});
  /** Which clip's trim sheet is open, or null. */
  const [trimming, setTrimming] = useState<string | null>(null);

  // A take must never run with the trim sheet open — the sliders write the
  // window straight into the Stage while `seekClipTo` is awaiting `seeked`.
  useEffect(() => { if (recPhase !== 'idle') setTrimming(null); }, [recPhase]);

  const setTrim = useCallback((id: string, next: { inSec: number; outSec: number } | undefined) => {
    setTrims((prev) => {
      if (!next) {
        if (!prev[id]) return prev;
        const { [id]: _drop, ...rest } = prev;
        return rest;
      }
      const cur = prev[id];
      if (cur && cur.inSec === next.inSec && cur.outSec === next.outSec) return prev;
      return { ...prev, [id]: next };
    });
  }, []);

  // A clip that has been removed must not leave its window behind: ids are
  // minted per import, so a stale entry is dead weight that a re-import can
  // never collide with — but it would still travel into every later `stageClips`.
  useEffect(() => {
    setTrims((prev) => {
      const live = new Set(clips.map((c) => c.id));
      const keys = Object.keys(prev);
      if (keys.every((k) => live.has(k))) return prev;
      const next: TrimMap = {};
      for (const k of keys) if (live.has(k)) next[k] = prev[k];
      return next;
    });
  }, [clips]);

  // --- scene: everything expensive happens here, never in the draw loop ------
  const stageClips: StageClipInput[] = useMemo(() => {
    /**
     * ONE PLAYBACK RATE PER CLIP so several clips can share a length — computed
     * from the WINDOW, not from the file.
     *
     * This is the whole coupling between trim and video-length sync, and getting
     * it backwards is invisible: "match the shortest clip" has to mean the
     * shortest thing the viewer SEES. Feed sync the untrimmed durations and a
     * clip cut to two seconds still drags the collage around on its original
     * sixty, with every rate correct and the result plainly wrong.
     * `clipWindow.effectiveLength` and invariant I10 pin this.
     */
    const playback = computeClipPlayback(
      clips.map((c) => {
        const t = trims[c.id];
        return {
          id: c.id,
          durationSec: normaliseWindow(c.durationSec, t?.inSec, t?.outSec).length,
        };
      }),
      clipLengthMode,
    );
    const rateById = new Map(playback.map((p) => [p.id, p.playbackRate]));
    return clips.map((c) => ({
      id: c.id,
      src: c.url,
      name: c.name,
      inSec: trims[c.id]?.inSec,
      outSec: trims[c.id]?.outSec,
      // The APP owns these URLs and revokes them when a clip is dropped; Stage
      // must not also revoke, or a re-mount races a already-freed blob.
      ownsUrl: false,
      loop: true,
      playbackRate: rateById.get(c.id) ?? 1,
      // `muted` is the clip's INTENT — "is this clip's sound part of the piece"
      // — and it seeds the export. It is NOT the speakers: what you hear is
      // `soundOn && !muted && live`, and `soundOn` starts false, so importing a
      // video is still silent in the room and still autoplay-eligible (browsers
      // only autoplay muted media, and `applyMutes` keeps the ELEMENT muted
      // while the monitor is off).
      //
      // It used to be `true`, which meant a video you imported and exported
      // without ever finding the per-clip speaker button produced a file with
      // no audio track at all — the owner's report. Importing a video is a
      // statement that you want the video; its sound comes with it, and one tap
      // takes it back out.
      muted: false,
      width: c.width,
      height: c.height,
      // The length `probeVideo` measured at import. The element cannot always
      // work it out for itself (a MediaRecorder WebM reads Infinity until
      // playback reaches the end), and the window is meaningless without it.
      durationSec: c.durationSec,
    }));
  }, [clips, clipLengthMode, trims]);

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;
    stage.setScene({
      layoutItems,
      orderedAssets,
      clips: stageClips,
      mode,
      aspect,
      zoom,
      bgColor,
      titlePlan,
      look,
    });
  }, [layoutItems, orderedAssets, stageClips, mode, aspect, zoom, bgColor, titlePlan, look]);

  /**
   * THE MUSIC, handed over on its own effect and keyed on the URL, never on the
   * object. The parent rebuilds this prop on every render that touches its
   * state; `setSoundtrack` is idempotent for the same url (it updates `muted`
   * and returns), so the element — and therefore the playhead — survives.
   */
  const trackUrl = soundtrack?.url ?? '';
  const trackName = soundtrack?.name ?? '';
  const trackMuted = !!soundtrack?.muted;
  /* THE RANGE JOINS THE DEPS AS TWO PRIMITIVES, not as the object it came in.
     `soundtrack` is rebuilt on every parent render, so depending on it would run
     this effect constantly; depending on neither would run it never, and a drag
     of the IN handle would reach the export and not the monitor. */
  const trackIn = soundtrack?.inSec;
  const trackOut = soundtrack?.outSec;
  useEffect(() => {
    const stage = stageRef.current;
    if (!stage) return;
    stage.setSoundtrack(trackUrl
      ? { url: trackUrl, name: trackName, muted: trackMuted, inSec: trackIn, outSec: trackOut }
      : null);
  }, [stageGen, trackUrl, trackName, trackMuted, trackIn, trackOut]);

  // --- transport -------------------------------------------------------------

  const anyPlaying = !!status?.clips.some((c) => c.playing);
  const liveCount = status?.liveCount ?? 0;
  const trackRow = status?.soundtrack ?? null;
  /**
   * IS THERE A TAKE TO MAKE? It used to be `liveCount > 0`, i.e. "are any video
   * clips decoding", and that stopped being the same question the moment the
   * Stage could record something that is not a clip. With music and no video the
   * monitor button was DISABLED, so the one thing the user had just added was
   * the one thing they could not hear.
   */
  const takeable = liveCount > 0 || !!trackRow;

  // STAGE OWNS `soundOn`, NOT US. It flips the flag itself in more places than
  // our toggle — `resumeFromGesture({sound})` sets it, and `setClipMuted(id,
  // false)` turns it on as a side effect. Mirroring the authoritative value back
  // into the ref keeps the next gesture from toggling against a stale local
  // belief and silently inverting the button.
  useEffect(() => {
    if (status) soundRef.current = status.soundOn;
  }, [status]);

  /** SYNCHRONOUS gesture entry point. No await may precede the Stage calls. */
  const handleTapToPlay = useCallback(() => {
    stageRef.current?.resumeFromGesture({ sound: soundRef.current });
  }, []);

  const togglePlay = useCallback(() => {
    const stage = stageRef.current;
    if (!stage) return;
    if (anyPlaying) stage.pauseAll();
    else stage.resumeFromGesture({ sound: soundRef.current }); // may need the gesture again
  }, [anyPlaying]);

  const toggleSound = useCallback(() => {
    const stage = stageRef.current;
    if (!stage) return;
    const next = !soundRef.current;
    soundRef.current = next;
    // setSound(true) is gesture-sensitive; this runs inside the click.
    stage.setSound(next);
  }, []);

  // --- recording -------------------------------------------------------------

  const stopRecording = useCallback(() => { abortRef.current?.abort(); }, []);

  const startRecording = useCallback((secondsOverride?: number, renderWidth?: number) => {
    const stage = stageRef.current;
    if (!stage || recPhase !== 'idle') return;

    setProgress(null);

    // ---- inside the gesture ----------------------------------------------
    // Play, sound and (if we are using it) the capture stream are all claimed
    // here, synchronously — iOS grants a gesture only to the task it fired in.
    stage.resumeFromGesture({ sound: soundRef.current });
    stage.setCaptureActive(true);

    // WHICH RECORDER — and this order is the whole answer to "why is it choppy".
    //
    // BOTH realtime paths sample a canvas that is playing: MediaRecorder pulls
    // from captureStream, and recordFrames samples on rAF, snaps its schedule
    // forward when late, drops frames under backpressure, and stamps wall-clock
    // time. Under this app's own load — several 1080p decoders composited into
    // clipped paths every frame — falling behind is the NORMAL case, so the
    // stutter gets encoded into the file and no re-take removes it.
    //
    // `renderOffline` steps the composition frame by frame and timestamps from
    // the frame INDEX, so the motion is mathematically even however slow the
    // device is. It is therefore the DEFAULT — and it NOW CARRIES SOUND: it
    // still cannot capture any (it draws frames, nothing is playing), so it
    // decodes the clips and mixes them on the same timeline instead. See
    // `offlineAudio.ts`. That removes the last reason the realtime path
    // existed: an unmuted clip no longer costs you the smooth render.
    const useRender = !!frameSupport?.supported;

    // ONE EXPORT PATH. The render was briefly conditional — realtime was kept
    // for a deliberately unmuted clip, since a renderer that draws frames has
    // no audio to capture. The first run of the Mobile Safari project (which
    // had never been able to launch) killed that idea: with sound on, the take
    // produced NOTHING AT ALL and sat there until the 240s timeout. Every
    // engine reports MediaRecorder + captureStream present, so the capability
    // probe says yes and the real take then never delivers — precisely the
    // WebKit failures frameExport's own header cites (229611 blank video,
    // 181663 freeze-on-stop, `onstop` never firing).
    //
    // Trading a path that ALWAYS works and is always smooth for one that hangs
    // on the owner's own engine family was the wrong trade — so the render
    // stayed, and sound came to IT rather than the other way round.
    //
    // The "Exports are silent" notice that used to sit here is gone because it
    // is no longer true. Nothing replaces it: the result carries its own
    // warnings, each naming the actual rung that failed, and those already
    // surface through `onNotice(res.warnings[0])` below. A blanket up-front
    // claim about sound is exactly the kind of stale promise that outlives the
    // code it describes.

    let stream: MediaStream | null = null;
    let useFrames = false;

    if (!useRender) {
      // No WebCodecs on this device — fall back to whatever CAN record.
      // The stream is only fetched on the MediaRecorder branch. Fetching it
      // first and bailing on the throw was a real bug: on a device with no
      // `canvas.captureStream` — exactly the device the fallback exists for —
      // it returned before the fallback could ever be reached.
      if (support?.supported ?? true) {
        try {
          stream = stage.captureStream({ fps: profile.fps, audio: true });
        } catch {
          // The dry run said yes and the real call disagreed. Believe the call.
          stream = null;
        }
      }
      useFrames = !stream;
      // We are already inside `!useRender`, i.e. the renderer is unavailable —
      // so if there is no stream either, nothing on this device can record.
      if (useFrames) {
        stage.setCaptureActive(false);
        onNotice?.("This browser can't record the collage — export a still instead, "
          + 'or open the studio in a newer browser.');
        return;
      }
    }
    // ---- gesture spent; everything below may await -------------------------

    const ac = new AbortController();
    abortRef.current = ac;
    setRecPhase('running');

    const take = Math.min(secondsOverride ?? seconds, profile.maxSeconds);

    /**
     * THE FADE REACHES THE FILE BY TWO DIFFERENT ROUTES, AND EXACTLY ONE OF
     * THEM RUNS PER TAKE.
     *
     * `renderOffline` holds the whole mixed buffer and multiplies through it in
     * the sample domain (`offlineAudio.mixSources`). `record()` encodes a LIVE
     * graph in real time and has no buffer to hold, so the same envelope is
     * scheduled as automation on the master gain instead (`Stage.applyTakeFade`).
     * `lib/fade.ts` owns the shape for both and its sweep proves the two
     * readings agree.
     *
     * Applying both would fade the take TWICE — quadratically, so a 1 s fade
     * would spend two seconds getting off the floor. The branch below is what
     * keeps them exclusive, which is why the master-gain call sits inside the
     * `record()` arm rather than beside `setCaptureActive(true)` at the top
     * where the other take-resets live. `recordFrames` gets nothing because it
     * carries no sound at all.
     */
    const run = useRender
      ? renderOffline(stage, {
          seconds: take,
          fps: profile.fps,
          // The size the sheet PROBED. Absent keeps the source's own width,
          // which is what every take did before the ladder existed.
          renderWidth,
          audioFadeSec: fadeSec,
          signal: ac.signal,
          filenameBase: 'collage',
          onProgress: setProgress,
        })
      : useFrames || !stream
      ? recordFrames(stage.canvas, {
          seconds: take,
          fps: profile.fps,
          signal: ac.signal,
          filenameBase: 'collage',
          onProgress: setProgress,
        })
      : record(stage.canvas, {
          stream: stream as MediaStream,
          seconds: take,
          fps: profile.fps,
          signal: ac.signal,
          filenameBase: 'collage',
          onProgress: setProgress,
          // ARMED FROM `onStart`, NOT FROM HERE, and the difference is the whole
          // take's tail. `record()` may await its one-time dry run (up to ~1.9s)
          // before `MediaRecorder.start()` ever runs, and the envelope is
          // anchored to `ctx.currentTime` at the moment it is scheduled — so
          // arming it at this call site put the ramp DOWN to zero ~1.9s before
          // the encoder stopped, and the file's tail recorded at gain 0 while
          // its head opened part-way up the fade-in. Found by an adversarial
          // audit; nothing in this suite could have caught it, because every
          // engine here has WebCodecs and never takes this branch.
          onStart: () => { stage.applyTakeFade(take, fadeSec); },
        });

    run
      .then((res) => {
        if (res.ok) {
          setResult(res);
          if (res.warnings.length) onNotice?.(res.warnings[0]);
        } else if (res.code !== 'aborted') {
          onNotice?.(res.advice ? `${res.message} ${res.advice}` : res.message);
        }
      })
      .catch((e: unknown) => {
        // Both recorders promise never to reject — but a promise with no catch
        // fails SILENTLY: no result, no message, the button just goes idle. If
        // that promise is ever broken, say so instead of vanishing.
        console.error('[collage] recorder rejected', e);
        onNotice?.(`Recording failed: ${e instanceof Error ? e.message : String(e)}`);
      })
      .finally(() => {
        // Release the take's surface no matter how it ended, so the next take
        // gets a fresh stream and the stage un-freezes its backing size.
        const s = stageRef.current;
        // `clearTakeFade` runs on a finished take, an aborted one and a thrown
        // one alike — a cancelled realtime take would otherwise leave the live
        // preview ramping down to silence with no control that brings it back.
        // A no-op on every take that never armed one, i.e. every offline render.
        if (s) { s.clearTakeFade(); s.setCaptureActive(false); s.releaseStream(); }
        abortRef.current = null;
        setRecPhase('idle');
        setProgress(null);
      });
  }, [recPhase, seconds, fadeSec, profile.fps, profile.maxSeconds, profile.videoBitsPerSecond, onNotice, support, frameSupport, status]);

  const closeResult = useCallback(() => {
    setResult((r) => { revokeRecording(r); return null; });
  }, []);

  // A finished take holds an object URL; free it if the component goes away first.
  useEffect(() => () => { revokeRecording(result); }, [result]);

  /**
   * CAN THIS DEVICE TAKE THE FILE AT ALL?
   *
   * `<a download>` — which is all `downloadRecording` can do — is ignored by
   * Safari on iOS for a blob: URL. The button appears to work and nothing
   * arrives, which is the worst possible outcome for a Save button. The share
   * sheet is the route that actually reaches Photos, so ASK, per file, with the
   * real type: `canShare` is the only honest answer and it is cheap.
   */
  const [shareable, setShareable] = useState(false);
  useEffect(() => {
    if (!result) { setShareable(false); return; }
    try {
      const f = new File([result.blob], result.filename, { type: result.mimeType || 'video/mp4' });
      setShareable(!!navigator.canShare?.({ files: [f] }));
    } catch { setShareable(false); }
  }, [result]);

  const shareResult = useCallback(async () => {
    if (!result) return;
    try {
      const file = new File([result.blob], result.filename, { type: result.mimeType || 'video/mp4' });
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], title: 'Collage', text: 'Video collage' });
        return;
      }
    } catch (e) {
      // A cancelled share is a CHOICE, not a failure — silently downloading the
      // file after the user backed out is not what they asked for.
      if ((e as { name?: string })?.name === 'AbortError') return;
    }
    downloadRecording(result);
  }, [result]);

  /**
   * PER-CLIP SOUND — INDEPENDENT. Each clip is its own switch; turning one on
   * leaves the others alone, so a mix of several clips is reachable (and is
   * what the offline bounce renders).
   *
   * It toggles INTENT (`wantsAudio`), not `audible`. Those differ whenever the
   * monitor is off or the clip was deferred by the realtime decoder budget, and
   * reading the button's state off `audible` is what made it look dead: a
   * deferred clip is never audible, so every click re-sent "unmute", the state
   * never changed on screen, and the clip's sound was excluded from the export
   * with no way for the user to include it.
   *
   * Runs synchronously in the click because turning sound ON is gesture-bound:
   * browsers only autoplay muted media, and `muted = false` is honoured only
   * from a real gesture.
   */
  const toggleClipSound = useCallback((clipId: string, currentlyWanted: boolean) => {
    const stage = stageRef.current;
    if (!stage) return;
    stage.setClipMuted(clipId, currentlyWanted, false);
    if (!currentlyWanted) stage.resumeFromGesture({ sound: true });
  }, []);

  /**
   * THE MUSIC'S OWN SWITCH — same contract as a clip's, one asymmetry.
   *
   * The FIRST press, when the track is already wanted but the monitor is off, is
   * read as "let me hear it" rather than "silence it". Music arrives UNMUTED
   * (adding it is an explicit act whose whole purpose is the sound), while the
   * monitor starts off because browsers only autoplay muted media — so without
   * this clause the one obvious control on the chip would, on its first press,
   * do the opposite of what a user who just added music wants, and they would
   * have to press it twice to hear anything.
   */
  const toggleTrackSound = useCallback((wanted: boolean, monitorOn: boolean) => {
    const stage = stageRef.current;
    if (!stage) return;
    if (wanted && !monitorOn) { soundRef.current = true; stage.resumeFromGesture({ sound: true }); return; }
    // BOTH, and in this order. The Stage call is SYNCHRONOUS inside the click
    // because unmuting is gesture-bound (iOS grants a gesture only to the task
    // it fired in), and a prop routed through an effect arrives a task too
    // late. The parent is told as well because the parent OWNS the track — a
    // Stage that is rebuilt is re-fed from that prop, and a mute that lived
    // only in the Stage would come back UNMUTED.
    stage.setSoundtrackMuted(wanted);
    if (!wanted) { soundRef.current = true; stage.resumeFromGesture({ sound: true }); }
    onSoundtrackMuted?.(wanted);
  }, [onSoundtrackMuted]);

  /**
   * THE SIZE LADDER, RE-PROBED WHEN THE SHAPE CHANGES.
   *
   * The H.264 ceiling is in MACROBLOCKS, so the top rung depends on the aspect:
   * a 3:2 landscape reaches 4096 on its long edge and the app's default 2:3
   * portrait runs out near 3,760. A ladder probed once at load would therefore
   * be wrong the moment anyone changes the shape — offering a size that fails
   * only after the render, which is the one thing this row must never do.
   *
   * Rounded to 3 decimals so a resize that nudges the aspect by a float's worth
   * does not re-run ~26 `isConfigSupported` calls for an identical answer.
   */
  const [sizes, setSizes] = useState<VideoSizeOption[]>([]);
  const aspectKey = Math.round((aspect || 1) * 1000) / 1000;
  useEffect(() => {
    let alive = true;
    probeVideoSizes(aspectKey, { fps: profile.fps, bitrate: profile.videoBitsPerSecond })
      .then((s) => { if (alive) setSizes(s); })
      .catch(() => { if (alive) setSizes([]); });
    return () => { alive = false; };
  }, [aspectKey, profile.fps, profile.videoBitsPerSecond]);

  /** Either strategy will do. Only when BOTH are out is recording really gone. */
  const canRecord = support === null && frameSupport === null
    ? true                                   // not probed yet; assume yes
    : !!support?.supported || !!frameSupport?.supported;
  const busy = recPhase !== 'idle';

  // Publish the handle the Export sheet calls into.
  useEffect(() => {
    if (!recorderRef) return;
    recorderRef.current = {
      start: startRecording,
      canRecord: canRecord && takeable && !busy,
      isRecording: recPhase === 'running',
      maxSeconds: profile.maxSeconds,
      sizes,
      // Only the offline renderer can spend pixels — the realtime paths sample
      // a canvas that has to keep up with a clock. Offering the row when the
      // take will be captured live would be a control that does nothing.
      canChooseSize: !!frameSupport?.supported,
    };
    return () => { recorderRef.current = null; };
  }, [recorderRef, startRecording, canRecord, takeable, busy, recPhase, profile.maxSeconds, sizes, frameSupport]);

  const clipRows = status?.clips ?? [];
  // What the EXPORT will carry — intent, exactly as `describeAudioSources`
  // reads it. Deliberately not `audible`: a clip the realtime budget deferred
  // is inaudible in the room and still lands in the file.
  const soundClipCount = clipRows.filter((r) => r.wantsAudio).length;
  /**
   * WHAT THE FILE WILL CARRY, IN WORDS — and the music has to be in this
   * sentence or the label repeats the exact mistake written up on the button
   * below: a hard-coded "silent" sitting on the branch that renders sound.
   * `describeAudioSources` appends the soundtrack row, so this counts it.
   */
  const trackWanted = !!trackRow?.wantsAudio;
  /**
   * The music chip's next ACTION, in words — the one string the title, the
   * accessible name and `toggleTrackSound`'s branch all read, so the button can
   * never say one thing and do another.
   */
  const trackAction = !trackWanted
    ? 'Put the music back in the piece'
    : trackRow?.audible ? 'Mute the music' : 'Hear the music';
  /** Will this take carry ANY sound? The fade chip is offered only when it
   *  will: a control that provably cannot change the file is the inert-control
   *  defect this component is already scarred by four times over. */
  const willCarrySound = soundClipCount > 0 || trackWanted;
  /** What the fade will ACTUALLY be on the take that is queued — clamped, not
   *  requested — so the words under the record button describe the file. */
  const fadeOnTake = fadeSpan(fadeSec, Math.min(seconds, profile.maxSeconds));
  const soundSummary = willCarrySound
    ? ' · sound from ' + [
        soundClipCount > 0 ? `${soundClipCount} clip${soundClipCount === 1 ? '' : 's'}` : '',
        trackWanted ? 'the music' : '',
      ].filter(Boolean).join(' + ')
      + (fadeOnTake > 0 ? `, fading in and out over ${fadeOnTake}s` : '')
    : ' · silent (nothing has its sound on)';

  const dock = (
    /* THE BAR WRAPS ON A PHONE, and that is what makes 44px controls possible.
       Every control in here used to be 24-32px, and the mobile gate could not
       see a single one of them because it imports no media, so this whole strip
       only exists once a video is loaded — measured at 390px: eleven controls
       under the law, including `Record video` at 32x32. Simply growing them
       overflows a 320px viewport (44*7 plus a clip chip does not fit on one
       line), so the clip row takes its own line below the phone breakpoint
       (`basis-full`) and the transport keeps its own. On sm+ it is one line
       exactly as before. */
    <div className="flex flex-wrap items-center gap-1 min-w-0 w-full">
      {/* ONE CHIP PER CLIP: what it is, whether its sound is in the piece, and
          a way out. Sound starts OFF for every clip — a collage that shouts on
          import is not a nice thing to build — but each switch is INDEPENDENT,
          so any combination of clips can be sounding, and that selection is
          exactly what the export renders. */}
      <div className="flex items-center gap-1.5 min-w-0 overflow-x-auto basis-full sm:basis-auto">
        {clips.map((c) => {
          const st = clipRows.find((r) => r.id === c.id);
          // INTENT drives the button; audibility only tints it. `wantsAudio` is
          // "this clip's sound is in the piece" and is what gets exported;
          // `audible` is "you can hear it through the speakers right now", which
          // the monitor switch and the decoder budget can both veto.
          const wantsAudio = !!st?.wantsAudio;
          const audible = !!st?.audible;
          const silentHere = wantsAudio && !audible;
          const t = trims[c.id];
          const win = normaliseWindow(c.durationSec, t?.inSec, t?.outSec);
          return (
            <div key={c.id} className="flex items-center gap-0.5 pl-2 pr-0.5 rounded-lg bg-[#161616] border border-white/10 shrink-0">
              <span className="text-[9px] tracking-wide text-gray-300 truncate max-w-[7rem]" title={c.name}>{c.name}</span>
              {/* TRIM. A trimmed clip SAYS SO on the chip — the window is the one
                  edit here that changes what a finished export contains while
                  leaving the collage looking broadly the same, so it must be
                  legible without opening anything. */}
              <button
                onClick={() => setTrimming(c.id)}
                disabled={busy || !(c.durationSec > MIN_WINDOW_SEC)}
                title={win.full
                  ? `Trim ${c.name} — pick the part that plays (${secs(c.durationSec)})`
                  : `${c.name}: playing ${secs(win.inSec)}→${secs(win.outSec)} of ${secs(c.durationSec)}`}
                aria-label={`Trim ${c.name}`}
                className={`h-11 min-w-[2.75rem] px-2 rounded flex items-center justify-center gap-1 transition-colors disabled:opacity-30 disabled:pointer-events-none ${
                  win.full
                    ? 'text-gray-500 hover:text-white hover:bg-white/10'
                    : 'text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20'
                }`}
              >
                <Scissors size={14} />
                {!win.full && (
                  <span className="text-[9px] font-black tabular-nums">{secs(win.length)}</span>
                )}
              </button>
              <button
                onClick={() => toggleClipSound(c.id, wantsAudio)}
                disabled={!status?.audioAvailable || st?.state === 'error'}
                title={
                  wantsAudio
                    ? silentHere
                      ? `${c.name}: sound is ON and will be in the export — you are not hearing it here because ${
                          status?.soundOn ? 'this clip is showing as stills' : 'the preview is muted'
                        }. Click to turn its sound off.`
                      : `Turn off ${c.name}'s sound`
                    : `Add ${c.name}'s sound to the piece`
                }
                // Short and conventional on PURPOSE: the rich explanation lives
                // in `title`, while the accessible name stays the two words a
                // screen reader (and the e2e suite) can act on.
                aria-label={wantsAudio ? `Mute ${c.name}` : `Unmute ${c.name}`}
                aria-pressed={wantsAudio}
                className={`w-11 h-11 rounded flex items-center justify-center transition-colors disabled:opacity-30 ${
                  audible
                    ? 'text-emerald-400 hover:bg-emerald-500/15'
                    : wantsAudio
                    ? 'text-emerald-400/45 hover:bg-emerald-500/10'
                    : 'text-gray-500 hover:text-white hover:bg-white/10'
                }`}
              >{wantsAudio ? <Volume2 size={15} /> : <VolumeX size={15} />}</button>
              {onRemoveClip && (
                <button
                  onClick={() => onRemoveClip(c.id)}
                  title={`Stop playing ${c.name} (keeps its ${c.frameCount === 1 ? 'poster' : `${c.frameCount} frames`})`}
                  aria-label={`Stop playing ${c.name}`}
                  className="w-11 h-11 rounded flex items-center justify-center text-gray-600 hover:text-red-400 hover:bg-white/10 transition-colors"
                ><X size={14} /></button>
              )}
            </div>
          );
        })}
        {/* THE MUSIC CHIP — the same chip a clip gets, because a soundtrack IS a
            clip with no picture: what it is, whether its sound is in the piece,
            and a way out. It sits in the same scroll row so a phone gets one
            horizontally-scrolling strip rather than a second line to find. */}
        {trackRow && (
          <div className="flex items-center gap-0.5 pl-2 pr-0.5 rounded-lg bg-[#161616] border border-emerald-500/25 shrink-0">
            <Music size={11} className={trackRow.audible ? 'text-emerald-400' : 'text-gray-500'} aria-hidden="true" />
            <span className="text-[9px] tracking-wide text-gray-300 truncate max-w-[7rem] ml-1" title={trackRow.name}>
              {trackRow.broken ? `${trackRow.name} — will not decode` : trackRow.name}
            </span>
            {/* THE LENGTH, from the prop rather than from the Stage: the Stage
                holds a url and an intent and has no reason to learn a duration
                the render never reads (lib/soundtrack.ts, DECISION 1). This is
                the ONE place that number is for — telling you which cut of the
                song you just dropped in. */}
            {!trackRow.broken && soundtrackLength(soundtrack?.durationSec ?? 0) && (
              <span className="text-[9px] tracking-wide text-gray-500 tabular-nums shrink-0 ml-1">
                {soundtrackLength(soundtrack?.durationSec ?? 0)}
              </span>
            )}
            {/* THE RANGE — "click it and select the range", from the field. The
                same button a clip gets, opening the same sheet, because a
                soundtrack is a clip with no picture and the part of a song you
                want is almost never the part that starts at 0:00.

                DISABLED UNTIL THE LENGTH LANDS, and that is not a nicety: the
                probe is asynchronous (lib/soundtrack.ts DECISION 1), and a sheet
                opened against `durationSec: 0` is two handles on a zero-width
                axis — every drag resolves to the same empty window and the
                control looks broken rather than pending. `MIN_WINDOW_SEC` is the
                same floor the clip chip uses, so a track too short to cut says
                so by being unavailable instead of by failing quietly. */}
            {onSoundtrackWindow && !trackRow.broken && (() => {
              const w = soundtrackWindow(soundtrack);
              const dur = soundtrack?.durationSec ?? 0;
              return (
                <button
                  onClick={() => setTrimming(SOUNDTRACK_ID)}
                  disabled={busy || !(dur > MIN_WINDOW_SEC)}
                  title={dur > MIN_WINDOW_SEC
                    ? (w.full
                        ? `Pick the part of ${trackRow.name} that plays (${soundtrackLength(dur)})`
                        : `${trackRow.name}: playing ${soundtrackRangeLabel(soundtrack)} of ${soundtrackLength(dur)}`)
                    : 'Waiting for the length of this track'}
                  aria-label={`Trim ${trackRow.name}`}
                  className={`h-11 min-w-[2.75rem] px-2 rounded flex items-center justify-center gap-1 transition-colors disabled:opacity-30 disabled:pointer-events-none ${
                    w.full
                      ? 'text-gray-500 hover:text-white hover:bg-white/10'
                      : 'text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20'
                  }`}
                >
                  <Scissors size={14} />
                  {!w.full && (
                    <span className="text-[9px] font-black tabular-nums" data-testid="track-range">
                      {soundtrackRangeLabel(soundtrack)}
                    </span>
                  )}
                </button>
              );
            })()}
            {/* THE NAME MUST NAME THE ACTION, and this button has three states
                rather than two. Music arrives IN the piece while the monitor is
                still off, so the first press means "let me hear it" — and an
                accessible name reading "Mute the music" while the press unmutes
                the monitor is the read-back-the-wrong-state defect this file is
                already scarred by, one layer up. `aria-pressed` therefore
                tracks INTENT (what the file will carry) and the NAME tracks the
                next action, which are genuinely two different facts here. */}
            <button
              onClick={() => toggleTrackSound(trackRow.wantsAudio, !!status?.soundOn)}
              disabled={trackRow.broken}
              aria-pressed={trackRow.wantsAudio}
              aria-label={`${trackAction}, ${trackRow.name}`}
              title={trackRow.broken ? 'This file did not decode in this browser' : trackAction}
              className={`w-11 h-11 rounded flex items-center justify-center transition-colors disabled:opacity-40 ${
                trackRow.audible
                  ? 'text-emerald-400 hover:bg-emerald-500/15'
                  : trackRow.wantsAudio
                    ? 'text-emerald-400/50 hover:bg-white/10'
                    : 'text-gray-500 hover:text-white hover:bg-white/10'
              }`}
            >{trackRow.wantsAudio ? <Volume2 size={15} /> : <VolumeX size={15} />}</button>
            {onRemoveSoundtrack && (
              <button
                onClick={onRemoveSoundtrack}
                title={`Remove ${trackRow.name}`}
                aria-label={`Remove the music, ${trackRow.name}`}
                className="w-11 h-11 rounded flex items-center justify-center text-gray-600 hover:text-red-400 hover:bg-white/10 transition-colors"
              ><X size={14} /></button>
            )}
          </div>
        )}
        {/* VIDEO-LENGTH SYNC — lives INSIDE the scroll row (shrink-0), so it scrolls
            with the clip chips and never steals width from the status readout that
            follows the spacer (which is `truncate min-w-0` and would collapse). */}
        {clips.length >= 2 && (
          <div className="flex items-center gap-0.5 shrink-0 pl-1" role="group" aria-label="Clip length sync">
            <span className="text-[9px] tracking-wide text-gray-500 hidden sm:inline mr-0.5">LENGTH</span>
            {CLIP_LENGTH_MODES.map((m) => {
              const l = CLIP_LENGTH_LABEL[m];
              const on = clipLengthMode === m;
              return (
                <button
                  key={m}
                  onClick={() => setClipLengthMode(m)}
                  disabled={busy}
                  aria-pressed={on}
                  aria-label={l.aria}
                  title={busy ? 'Finish the export before changing clip length.' : l.title}
                  className={`px-2.5 h-11 rounded text-[9px] font-black tracking-wide transition-colors disabled:opacity-40 disabled:pointer-events-none ${
                    on ? 'bg-white/15 text-white' : 'text-gray-500 hover:text-white hover:bg-white/10'
                  }`}
                >{l.short}</button>
              );
            })}
          </div>
        )}
        {/* THE FADE — ONE control, ONE tap, and it lives in the scroll row for
            the same reason clip-length sync does: the fixed region past the
            spacer is already play + sound + four take lengths + record, and a
            second four-chip group there is exactly the scar the colour dice
            left in the trades' rails (seven 44px targets, 295 of a 320px
            phone's 304). A cycling chip is four states in one target.

            Offered only when the take will carry sound at all — see
            `willCarrySound`. And it reads the CLAMPED length, so the chip can
            never advertise a 2s fade on a take that will only give it 1.5s. */}
        {willCarrySound && (
          <div className="flex items-center gap-0.5 shrink-0 pl-1">
            <span className="text-[9px] tracking-wide text-gray-500 hidden sm:inline mr-0.5">FADE</span>
            <button
              onClick={() => setFadeSec(nextFade(fadeSec))}
              disabled={busy}
              aria-label={`Fade ${fadeLabel(fadeSec)}, tap for ${fadeLabel(nextFade(fadeSec))}`}
              title={busy
                ? 'Finish the export before changing the fade.'
                : fadeSec > 0
                  ? `The sound fades up over ${fadeOnTake}s and back down over ${fadeOnTake}s. `
                    + `Tap for ${fadeLabel(nextFade(fadeSec))}.`
                  : 'The take currently starts and ends at full level. '
                    + `Tap to fade it in and out over ${fadeLabel(nextFade(fadeSec))}.`}
              className={`px-2.5 h-11 min-w-[2.75rem] rounded text-[9px] font-black tracking-wide transition-colors disabled:opacity-40 disabled:pointer-events-none ${
                fadeSec > 0
                  ? 'bg-white/15 text-white'
                  : 'text-gray-500 hover:text-white hover:bg-white/10'
              }`}
            >{fadeLabel(fadeSec)}</button>
          </div>
        )}
      </div>

      <div className="flex-1 min-w-0" />
      {/* WHAT THE DEVICE COULD NOT DO — deferred clips render their still frame
          rather than freezing, and the user is told which, and why. */}
      {status?.message && !busy && (
        <span className="text-[9px] tracking-wide text-gray-400 truncate mr-1 min-w-0" title={status.message}>
          {status.message}
        </span>
      )}

      {recPhase === 'running' && progress && (
        <span className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-red-950/50 border border-red-500/40 shrink-0">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
          <span className="text-[10px] font-black tracking-[0.15em] text-white tabular-nums">
            {remainingSeconds(progress)}s
          </span>
          <span className="text-[9px] tracking-widest text-gray-400 tabular-nums">
            {fmtBytes(progress.bytes)}
          </span>
          {progress.withAudio && <Volume2 size={10} className="text-emerald-400" />}
        </span>
      )}

      <button
        onClick={togglePlay}
        disabled={busy || liveCount === 0}
        title={anyPlaying ? 'Pause clips' : 'Play clips'}
        aria-label={anyPlaying ? 'Pause clips' : 'Play clips'}
        className="w-11 h-11 rounded-lg text-gray-200 flex items-center justify-center hover:bg-white/10 disabled:opacity-30 transition-colors shrink-0"
      >
        {anyPlaying ? <Pause size={17} /> : <Play size={17} />}
      </button>

      <button
        onClick={toggleSound}
        disabled={!takeable || !status?.audioAvailable}
        title={status?.soundOn
          ? 'Mute the preview (does not change what the export contains)'
          : 'Hear the preview'}
        aria-label={status?.soundOn ? 'Mute preview' : 'Unmute preview'}
        className={`w-11 h-11 rounded-lg flex items-center justify-center hover:bg-white/10 disabled:opacity-30 transition-colors shrink-0 ${
          status?.soundOn ? 'text-emerald-400' : 'text-gray-400'
        }`}
      >
        {status?.soundOn ? <Volume2 size={17} /> : <VolumeX size={17} />}
      </button>

      {/* Take length. Only lengths this device can actually survive are offered. */}
      <div className="flex items-center rounded-lg overflow-hidden border border-white/10 shrink-0">
        {durations.map((d) => (
          <button
            key={d}
            onClick={() => setSeconds(d)}
            disabled={busy}
            className={`px-2 h-11 min-w-[2.75rem] flex items-center justify-center text-[9px] font-black tracking-widest transition-colors disabled:opacity-30 ${
              seconds === d ? 'bg-white/15 text-white' : 'text-gray-500 hover:text-white'
            }`}
          >{d}s</button>
        ))}
      </div>

      {recPhase === 'running' ? (
        <button
          onClick={stopRecording}
          title="Stop recording"
          aria-label="Stop recording"
          className="w-11 h-11 rounded-lg bg-red-600/90 text-white flex items-center justify-center hover:bg-red-500 transition-colors shrink-0"
        ><Square size={14} fill="currentColor" /></button>
      ) : (
        <button
          onClick={() => startRecording()}
          disabled={!canRecord || !takeable || busy}
          // "(silent)" used to be hard-coded onto exactly this branch — which is
          // the branch that RENDERS SOUND. The offline renderer gained a mixer
          // and the label never moved, so the tool told you it was about to drop
          // your audio a moment before it kept it, and the owner had every
          // reason to read a silent file as expected behaviour. The label now
          // reads the same intent the export does.
          title={!canRecord
            ? 'Recording unavailable in this browser'
            : frameSupport?.supported
              ? `Render ${Math.min(seconds, profile.maxSeconds)}s — frame by frame, no dropped frames${soundSummary}`
              : `Record ${Math.min(seconds, profile.maxSeconds)}s in real time`}
          aria-label="Record video"
          className="w-11 h-11 rounded-lg text-red-400 flex items-center justify-center hover:bg-red-500/15 disabled:opacity-30 transition-colors shrink-0"
        >{recPhase === 'saving' ? <Loader2 size={16} className="animate-spin" /> : <Video size={17} />}</button>
      )}
    </div>
  );

  return (
    <>
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        // The composition is decorative; the clip list in the dock carries the words.
        aria-hidden="true"
      />

      {/* THE ONLY THING STILL ALLOWED ON TOP OF THE ARTWORK. It is a call to
          action that has to be ON the thing it starts, it is the sole route past
          an autoplay block, and it disappears on the first tap. */}
      {status?.needsGesture && liveCount > 0 && !busy && (
        <button
          onClick={handleTapToPlay}
          className="absolute inset-0 z-30 flex flex-col items-center justify-center gap-3 bg-black/45 backdrop-blur-[2px]"
        >
          <span className="w-16 h-16 rounded-full bg-white/10 border border-white/25 flex items-center justify-center">
            <Play size={26} className="text-white translate-x-[2px]" />
          </span>
          <span className="text-[9px] font-black tracking-[0.25em] text-white uppercase">Tap to play</span>
        </button>
      )}

      {/* Everything else lives in the control dock, OUTSIDE the canvas. */}
      {controlsHost && createPortal(dock, controlsHost)}

      {/* THE TRIM SHEET. Mounted from the clip list rather than living in it:
          the dock is a one-line scroll row on a phone and a range slider does
          not fit in it — and a control you cannot drag is not a trim control. */}
      {/* THE MUSIC'S RANGE, through the same sheet. `SOUNDTRACK_ID` is minted so
          it can never collide with a clip id (lib/soundtrack.ts), which is what
          lets one `trimming` slot hold either — and with it the invariant that
          only one of these sheets can ever be open. */}
      {trimming === SOUNDTRACK_ID && !busy && soundtrack && onSoundtrackWindow && (
        <TrimSheet
          name={soundtrack.name}
          span={soundtrack.durationSec}
          frames={[]}
          value={soundtrack.inSec !== undefined && soundtrack.outSec !== undefined
            ? { inSec: soundtrack.inSec, outSec: soundtrack.outSec }
            : undefined}
          onChange={onSoundtrackWindow}
          onClose={() => setTrimming(null)}
          credit="Picking the part of the song that plays was wished for by an anonymous Collage user."
        />
      )}

      {trimming && trimming !== SOUNDTRACK_ID && !busy && (() => {
        const c = clips.find((x) => x.id === trimming);
        if (!c) return null;
        // The frames this clip already gave us, in time order. `sourceTime` is
        // stamped on every extracted frame at import, so the strip reads left to
        // right as the clip actually runs.
        // BY `clipId` ONLY. `sourceName` is the raw FILE NAME, and matching on it
        // hands this clip every frame of every other clip that shares a name —
        // `IMG_0001.MOV`, `clip.mp4`, `screen-recording.mov` are exactly what
        // phones and screen recorders produce, and `removeClip` clears `clipId`
        // while leaving `sourceName`, so a DELETED clip kept feeding the strip.
        // Measured with two different videos both named `clip.mp4`: 12 of 24
        // frames in the strip belonged to the other clip, interleaved into a
        // zebra, with every frame's WIDTH wrong as well now that the strip is
        // laid out by time. The strip is the only picture of what you are
        // cutting; a strip showing another clip is worse than no strip.
        const frames = (poolAssets ?? [])
          .filter((a) => a.sourceKind === 'video' && !!a.clipId && a.clipId === c.id)
          .slice()
          .sort((a, b) => (a.sourceTime ?? 0) - (b.sourceTime ?? 0));
        return (
          <TrimSheet
            name={c.name}
            span={c.durationSec}
            frames={frames}
            value={trims[c.id]}
            onChange={(v) => setTrim(c.id, v)}
            onClose={() => setTrimming(null)}
          />
        );
      })()}

      {/* THE TAKE — previewed with a real <video> so "it plays" is proven here,
          not assumed. The file is only worth offering if this element renders it.

          PORTALLED TO <body>, and that is load-bearing rather than tidy: this
          sheet lives inside a `relative z-10` wrapper, which IS a stacking
          context, so its own z-[300] was being resolved INSIDE that z-10 and the
          z-50 control dock painted over it. Save was genuinely unclickable —
          caught by a test click that kept being intercepted, not by looking. */}
      {result && createPortal((
        // role/aria-modal are not decoration here: this was the ONE full-screen
        // sheet in the app that never declared itself a dialog, so anything
        // asking "is a modal open?" — including the full-bleed shortcut guard in
        // App.tsx — saw an empty screen and acted behind it.
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Recorded take"
          className="fixed inset-0 z-[300] bg-black/90 backdrop-blur flex flex-col items-center justify-center p-5 gap-4"
        >
          <video
            src={result.url}
            controls
            autoPlay
            loop
            playsInline
            className="max-w-full max-h-[60vh] rounded-xl shadow-2xl bg-black"
          />
          <div className="text-center">
            <p className="text-[10px] font-black tracking-[0.2em] text-white uppercase">{result.container.label}</p>
            {/* FRAME COUNT IS NOT TRIVIA. An offline render emits exactly
                duration x fps frames; a realtime take drops whatever the device
                could not keep up with, and this line is where that shows. */}
            <p className="text-[9px] tracking-widest text-gray-500 mt-1 tabular-nums">
              {(result.durationMs / 1000).toFixed(1)}s · {fmtBytes(result.sizeBytes)} · {result.fps}fps
              {' · '}{result.chunks} frames
              {result.audio.recorded ? ' · sound' : ' · silent'}
            </p>
            {result.warnings.length > 0 && (
              <p className="text-[9px] text-yellow-400/90 mt-2 max-w-xs mx-auto leading-relaxed">{result.warnings[0]}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* On a device that can share the FILE — every iPhone — the share
                sheet leads, because that is the one that reaches Photos. The
                plain download stays available, just not as the headline. */}
            {shareable ? (
              <>
                <button
                  onClick={shareResult}
                  className="px-4 py-2.5 rounded-xl bg-white text-black text-[10px] font-black tracking-[0.2em] uppercase flex items-center gap-2 hover:bg-emerald-400 transition-colors"
                ><Share2 size={13} /> Save video</button>
                <button
                  onClick={() => downloadRecording(result)}
                  title="Download the file directly instead of using the share sheet"
                  className="px-4 py-2.5 rounded-xl bg-[#1a1a1a] border border-white/15 text-white text-[10px] font-black tracking-[0.2em] uppercase flex items-center gap-2 hover:bg-white/10 transition-colors"
                ><Download size={13} /> Download</button>
              </>
            ) : (
              <button
                onClick={() => downloadRecording(result)}
                className="px-4 py-2.5 rounded-xl bg-white text-black text-[10px] font-black tracking-[0.2em] uppercase flex items-center gap-2 hover:bg-gray-200 transition-colors"
              ><Download size={13} /> Save</button>
            )}
            <button
              onClick={closeResult}
              aria-label="Close"
              className="w-10 h-10 rounded-xl bg-[#1a1a1a] border border-white/15 text-gray-400 flex items-center justify-center hover:text-white transition-colors"
            ><X size={16} /></button>
          </div>
        </div>
      ), document.body)}
    </>
  );
};

export default VideoStage;
