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
import {
  Play, Pause, Volume2, VolumeX, Video, Square, Download, Share2, X,
  AlertTriangle, Loader2,
} from 'lucide-react';

import { createStage, type Stage, type StageStatus, type StageClipInput } from '../lib/stage';
import {
  record, probeVideoExportSupport, downloadRecording, revokeRecording,
  getRecordingProfile, remainingSeconds,
  type RecordProgress, type RecordSuccess, type VideoExportSupport,
} from '../lib/videoExport';
import type { ImageAsset, LayoutItem, LayoutMode, LiveClip } from '../types';

export interface VideoStageProps {
  layoutItems: LayoutItem[];
  /** `shuffledIndices.map(i => images[i])` — memoise it, or every render rebuilds the draw list. */
  orderedAssets: (ImageAsset | undefined)[];
  clips: LiveClip[];
  mode: LayoutMode;
  aspect: number;
  zoom: number;
  bgColor: string;
  /** Surfaced so the parent can show one consistent notice strip. */
  onNotice?: (msg: string) => void;
  /**
   * The compositor could not start on this device (no 2D context). The parent
   * must fall back to the still preview — a live mode that paints nothing is
   * strictly worse than the JPEG it replaced.
   */
  onUnavailable?: () => void;
}

/** Offered take lengths. Clamped to the device cap, so a phone never sees 30s. */
const DURATION_CHOICES = [5, 10, 15, 30] as const;

const fmtBytes = (b: number): string =>
  b < 1024 * 1024 ? `${Math.max(1, Math.round(b / 1024))} KB` : `${(b / (1024 * 1024)).toFixed(1)} MB`;

type RecPhase = 'idle' | 'running' | 'saving';

export const VideoStage: React.FC<VideoStageProps> = ({
  layoutItems, orderedAssets, clips, mode, aspect, zoom, bgColor, onNotice, onUnavailable,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stageRef = useRef<Stage | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  /** Kept in a ref as well as state: the click handler must read it synchronously. */
  const soundRef = useRef(false);

  const [status, setStatus] = useState<StageStatus | null>(null);
  const [support, setSupport] = useState<VideoExportSupport | null>(null);
  const [recPhase, setRecPhase] = useState<RecPhase>('idle');
  const [progress, setProgress] = useState<RecordProgress | null>(null);
  const [result, setResult] = useState<RecordSuccess | null>(null);
  const [recError, setRecError] = useState<{ message: string; advice: string | null } | null>(null);
  const [seconds, setSeconds] = useState(10);

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
    probeVideoExportSupport().then((s) => { if (alive) setSupport(s); });
    return () => { alive = false; };
  }, []);

  // --- scene: everything expensive happens here, never in the draw loop ------
  const stageClips: StageClipInput[] = useMemo(
    () => clips.map((c) => ({
      id: c.id,
      src: c.url,
      name: c.name,
      // The APP owns these URLs and revokes them when a clip is dropped; Stage
      // must not also revoke, or a re-mount races a already-freed blob.
      ownsUrl: false,
      loop: true,
      muted: true,
      width: c.width,
      height: c.height,
    })),
    [clips],
  );

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
    });
  }, [layoutItems, orderedAssets, stageClips, mode, aspect, zoom, bgColor]);

  // --- transport -------------------------------------------------------------

  const anyPlaying = !!status?.clips.some((c) => c.playing);
  const liveCount = status?.liveCount ?? 0;

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

  const startRecording = useCallback(() => {
    const stage = stageRef.current;
    if (!stage || recPhase !== 'idle') return;

    setRecError(null);
    setProgress(null);

    // ---- inside the gesture ----------------------------------------------
    // Play, sound and the capture stream are all claimed here, synchronously.
    stage.resumeFromGesture({ sound: soundRef.current });
    stage.setCaptureActive(true);

    let stream: MediaStream;
    try {
      stream = stage.captureStream({ fps: profile.fps, audio: true });
    } catch (e) {
      stage.setCaptureActive(false);
      setRecError({
        message: "This browser can't record the collage canvas.",
        advice: 'Export a still instead, or open the studio in Chrome on a computer.',
      });
      return;
    }
    // ---- gesture spent; everything below may await -------------------------

    const ac = new AbortController();
    abortRef.current = ac;
    setRecPhase('running');

    const take = Math.min(seconds, profile.maxSeconds);

    record(stage.canvas, {
      stream,
      seconds: take,
      fps: profile.fps,
      signal: ac.signal,
      filenameBase: 'collage',
      onProgress: setProgress,
    })
      .then((res) => {
        if (res.ok) {
          setResult(res);
          if (res.warnings.length) onNotice?.(res.warnings[0]);
        } else if (res.code !== 'aborted') {
          setRecError({ message: res.message, advice: res.advice });
        }
      })
      .finally(() => {
        // Release the take's surface no matter how it ended, so the next take
        // gets a fresh stream and the stage un-freezes its backing size.
        const s = stageRef.current;
        if (s) { s.setCaptureActive(false); s.releaseStream(); }
        abortRef.current = null;
        setRecPhase('idle');
        setProgress(null);
      });
  }, [recPhase, seconds, profile.fps, profile.maxSeconds, onNotice]);

  const closeResult = useCallback(() => {
    setResult((r) => { revokeRecording(r); return null; });
  }, []);

  // A finished take holds an object URL; free it if the component goes away first.
  useEffect(() => () => { revokeRecording(result); }, [result]);

  const shareResult = useCallback(async () => {
    if (!result) return;
    try {
      const file = new File([result.blob], result.filename, { type: result.mimeType || 'video/mp4' });
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], title: 'Collage', text: 'Video collage' });
        return;
      }
    } catch { /* user dismissed, or the platform refused the type */ }
    downloadRecording(result);
  }, [result]);

  const canRecord = support ? support.supported : true; // 'likely' until probed
  const busy = recPhase !== 'idle';

  return (
    <>
      <canvas
        ref={canvasRef}
        className="w-full h-full block"
        // The composition is decorative; the clip list below carries the words.
        aria-hidden="true"
      />

      {/* TAP TO PLAY — iOS Low Power Mode blocks even muted autoplay, and does
          not always reject the promise. Stage detects it behaviourally. */}
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

      {/* RECORDING SCRIM — the canvas must stay visible and on-screen for the
          whole take (an off-screen Stage pauses itself), so this never covers it. */}
      {recPhase === 'running' && progress && (
        <div className="absolute top-3 left-1/2 -translate-x-1/2 z-40 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/80 border border-red-500/40 shadow-xl">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-[10px] font-black tracking-[0.2em] text-white tabular-nums">
            {remainingSeconds(progress)}s
          </span>
          <span className="text-[9px] tracking-widest text-gray-400 tabular-nums">
            {fmtBytes(progress.bytes)}
          </span>
          {progress.withAudio && <Volume2 size={11} className="text-emerald-400" />}
        </div>
      )}

      {/* TRANSPORT */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-40 flex items-center gap-1 px-1.5 py-1.5 rounded-xl bg-black/75 backdrop-blur border border-white/10 shadow-2xl">
        <button
          onClick={togglePlay}
          disabled={busy || liveCount === 0}
          title={anyPlaying ? 'Pause clips' : 'Play clips'}
          aria-label={anyPlaying ? 'Pause clips' : 'Play clips'}
          className="w-9 h-9 rounded-lg text-gray-200 flex items-center justify-center hover:bg-white/10 disabled:opacity-30 transition-colors"
        >
          {anyPlaying ? <Pause size={16} /> : <Play size={16} />}
        </button>

        <button
          onClick={toggleSound}
          disabled={liveCount === 0 || !status?.audioAvailable}
          title={status?.soundOn ? 'Mute' : 'Unmute the largest clip'}
          aria-label={status?.soundOn ? 'Mute' : 'Unmute'}
          className={`w-9 h-9 rounded-lg flex items-center justify-center hover:bg-white/10 disabled:opacity-30 transition-colors ${
            status?.soundOn ? 'text-emerald-400' : 'text-gray-400'
          }`}
        >
          {status?.soundOn ? <Volume2 size={16} /> : <VolumeX size={16} />}
        </button>

        <span className="w-px h-5 bg-white/10 mx-0.5" />

        {/* Take length. Only lengths this device can actually survive are offered. */}
        <div className="flex items-center rounded-lg overflow-hidden border border-white/10">
          {durations.map((d) => (
            <button
              key={d}
              onClick={() => setSeconds(d)}
              disabled={busy}
              className={`px-2 py-1.5 text-[9px] font-black tracking-widest transition-colors disabled:opacity-30 ${
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
            className="w-9 h-9 rounded-lg bg-red-600/90 text-white flex items-center justify-center hover:bg-red-500 transition-colors"
          ><Square size={13} fill="currentColor" /></button>
        ) : (
          <button
            onClick={startRecording}
            disabled={!canRecord || liveCount === 0 || busy}
            title={canRecord ? `Record ${Math.min(seconds, profile.maxSeconds)}s of video` : 'Recording unavailable in this browser'}
            aria-label="Record video"
            className="w-9 h-9 rounded-lg text-red-400 flex items-center justify-center hover:bg-red-500/15 disabled:opacity-30 transition-colors"
          >{recPhase === 'saving' ? <Loader2 size={15} className="animate-spin" /> : <Video size={16} />}</button>
        )}
      </div>

      {/* WHAT THE DEVICE COULD NOT DO — deferred clips render their still frame
          rather than freezing, and the user is told which, and why. */}
      {status?.message && !busy && (
        <div className="absolute top-3 left-3 right-3 z-30 pointer-events-none flex justify-center">
          <span className="max-w-full px-2.5 py-1 rounded-lg bg-black/70 border border-white/10 text-[9px] tracking-wide text-gray-300 truncate">
            {status.message}
          </span>
        </div>
      )}

      {recError && (
        <div className="absolute inset-x-3 bottom-16 z-50 p-3 rounded-xl bg-[#161616] border border-red-500/40 shadow-2xl">
          <div className="flex items-start gap-2">
            <AlertTriangle size={14} className="text-red-400 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-[10px] text-white leading-relaxed">{recError.message}</p>
              {recError.advice && <p className="text-[9px] text-gray-400 mt-1 leading-relaxed">{recError.advice}</p>}
            </div>
            <button onClick={() => setRecError(null)} aria-label="Dismiss" className="text-gray-500 hover:text-white"><X size={13} /></button>
          </div>
        </div>
      )}

      {/* THE TAKE — previewed with a real <video> so "it plays" is proven here,
          not assumed. The file is only worth offering if this element renders it. */}
      {result && (
        <div className="fixed inset-0 z-[300] bg-black/90 backdrop-blur flex flex-col items-center justify-center p-5 gap-4">
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
            <p className="text-[9px] tracking-widest text-gray-500 mt-1 tabular-nums">
              {(result.durationMs / 1000).toFixed(1)}s · {fmtBytes(result.sizeBytes)} · {result.fps}fps
              {result.audio.recorded ? ' · sound' : ' · silent'}
            </p>
            {result.warnings.length > 0 && (
              <p className="text-[9px] text-yellow-400/90 mt-2 max-w-xs mx-auto leading-relaxed">{result.warnings[0]}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => downloadRecording(result)}
              className="px-4 py-2.5 rounded-xl bg-white text-black text-[10px] font-black tracking-[0.2em] uppercase flex items-center gap-2 hover:bg-gray-200 transition-colors"
            ><Download size={13} /> Save</button>
            {!!navigator.share && (
              <button
                onClick={shareResult}
                className="px-4 py-2.5 rounded-xl bg-[#1a1a1a] border border-white/15 text-white text-[10px] font-black tracking-[0.2em] uppercase flex items-center gap-2 hover:bg-white/10 transition-colors"
              ><Share2 size={13} /> Share</button>
            )}
            <button
              onClick={closeResult}
              aria-label="Close"
              className="w-10 h-10 rounded-xl bg-[#1a1a1a] border border-white/15 text-gray-400 flex items-center justify-center hover:text-white transition-colors"
            ><X size={16} /></button>
          </div>
        </div>
      )}
    </>
  );
};

export default VideoStage;
