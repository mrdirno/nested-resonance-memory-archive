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
  AlertTriangle, Loader2,
} from 'lucide-react';

import { createStage, type Stage, type StageStatus, type StageClipInput } from '../lib/stage';
import {
  record, probeVideoExportSupport, downloadRecording, revokeRecording,
  getRecordingProfile, remainingSeconds,
  type RecordProgress, type RecordSuccess, type VideoExportSupport,
} from '../lib/videoExport';
import {
  recordFrames, renderOffline, probeFrameExportSupport,
  type FrameExportSupport,
} from '../lib/frameExport';
import type { ImageAsset, LayoutItem, LayoutMode, LiveClip } from '../types';
import { computeClipPlayback, CLIP_LENGTH_MODES, type ClipLengthMode } from '../lib/videoSync';

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
   * Filled with a handle so the Export sheet can start a take. It has to be
   * IMPERATIVE: iOS grants a gesture only to the task it fired in, so the export
   * button must reach `startRecording` synchronously inside its own onClick — a
   * prop change routed through an effect arrives a task too late and records
   * silently, or not at all.
   */
  recorderRef?: React.MutableRefObject<StageRecorder | null>;
}

export interface StageRecorder {
  start: (seconds?: number) => void;
  canRecord: boolean;
  isRecording: boolean;
  maxSeconds: number;
}

/** Offered take lengths. Clamped to the device cap, so a phone never sees 30s. */
const DURATION_CHOICES = [5, 10, 15, 30] as const;

const fmtBytes = (b: number): string =>
  b < 1024 * 1024 ? `${Math.max(1, Math.round(b / 1024))} KB` : `${(b / (1024 * 1024)).toFixed(1)} MB`;

type RecPhase = 'idle' | 'running' | 'saving';

export const VideoStage: React.FC<VideoStageProps> = ({
  layoutItems, orderedAssets, clips, mode, aspect, zoom, bgColor, onNotice, onUnavailable,
  controlsHost, onRemoveClip, recorderRef,
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
    // BOTH paths, because the answer decides which button the user even gets.
    probeVideoExportSupport().then((s) => { if (alive) setSupport(s); });
    probeFrameExportSupport().then((s) => { if (alive) setFrameSupport(s); });
    return () => { alive = false; };
  }, []);

  // Video-length sync mode. 'loop' (default) leaves every clip at its own speed;
  // the two stretch modes rescale so all clips share one length. See videoSync.ts.
  const [clipLengthMode, setClipLengthMode] = useState<ClipLengthMode>('loop');

  // --- scene: everything expensive happens here, never in the draw loop ------
  const stageClips: StageClipInput[] = useMemo(() => {
    // One playbackRate per clip so several clips can share a length. The maths is
    // pure and unit-swept (videoSync.ts); here we just attach the result.
    const playback = computeClipPlayback(
      clips.map((c) => ({ id: c.id, durationSec: c.durationSec })),
      clipLengthMode,
    );
    const rateById = new Map(playback.map((p) => [p.id, p.playbackRate]));
    return clips.map((c) => ({
      id: c.id,
      src: c.url,
      name: c.name,
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
    }));
  }, [clips, clipLengthMode]);

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

  const startRecording = useCallback((secondsOverride?: number) => {
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

    const run = useRender
      ? renderOffline(stage, {
          seconds: take,
          fps: profile.fps,
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
        if (s) { s.setCaptureActive(false); s.releaseStream(); }
        abortRef.current = null;
        setRecPhase('idle');
        setProgress(null);
      });
  }, [recPhase, seconds, profile.fps, profile.maxSeconds, onNotice, support, frameSupport, status]);

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
      canRecord: canRecord && liveCount > 0 && !busy,
      isRecording: recPhase === 'running',
      maxSeconds: profile.maxSeconds,
    };
    return () => { recorderRef.current = null; };
  }, [recorderRef, startRecording, canRecord, liveCount, busy, recPhase, profile.maxSeconds]);

  const clipRows = status?.clips ?? [];
  // What the EXPORT will carry — intent, exactly as `describeAudioSources`
  // reads it. Deliberately not `audible`: a clip the realtime budget deferred
  // is inaudible in the room and still lands in the file.
  const soundClipCount = clipRows.filter((r) => r.wantsAudio).length;

  const dock = (
    <div className="flex items-center gap-1 min-w-0 w-full">
      {/* ONE CHIP PER CLIP: what it is, whether its sound is in the piece, and
          a way out. Sound starts OFF for every clip — a collage that shouts on
          import is not a nice thing to build — but each switch is INDEPENDENT,
          so any combination of clips can be sounding, and that selection is
          exactly what the export renders. */}
      <div className="flex items-center gap-1.5 min-w-0 overflow-x-auto">
        {clips.map((c) => {
          const st = clipRows.find((r) => r.id === c.id);
          // INTENT drives the button; audibility only tints it. `wantsAudio` is
          // "this clip's sound is in the piece" and is what gets exported;
          // `audible` is "you can hear it through the speakers right now", which
          // the monitor switch and the decoder budget can both veto.
          const wantsAudio = !!st?.wantsAudio;
          const audible = !!st?.audible;
          const silentHere = wantsAudio && !audible;
          return (
            <div key={c.id} className="flex items-center gap-0.5 pl-2 pr-0.5 py-0.5 rounded-lg bg-[#161616] border border-white/10 shrink-0">
              <span className="text-[9px] tracking-wide text-gray-300 truncate max-w-[7rem]" title={c.name}>{c.name}</span>
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
                className={`w-7 h-7 rounded flex items-center justify-center transition-colors disabled:opacity-30 ${
                  audible
                    ? 'text-emerald-400 hover:bg-emerald-500/15'
                    : wantsAudio
                    ? 'text-emerald-400/45 hover:bg-emerald-500/10'
                    : 'text-gray-500 hover:text-white hover:bg-white/10'
                }`}
              >{wantsAudio ? <Volume2 size={13} /> : <VolumeX size={13} />}</button>
              {onRemoveClip && (
                <button
                  onClick={() => onRemoveClip(c.id)}
                  title={`Stop playing ${c.name} (keeps its ${c.frameCount} frames)`}
                  aria-label={`Stop playing ${c.name}`}
                  className="w-6 h-7 rounded flex items-center justify-center text-gray-600 hover:text-red-400 hover:bg-white/10 transition-colors"
                ><X size={11} /></button>
              )}
            </div>
          );
        })}
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
                  className={`px-2 h-7 rounded text-[9px] font-black tracking-wide transition-colors disabled:opacity-40 disabled:pointer-events-none ${
                    on ? 'bg-white/15 text-white' : 'text-gray-500 hover:text-white hover:bg-white/10'
                  }`}
                >{l.short}</button>
              );
            })}
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
        className="w-8 h-8 rounded-lg text-gray-200 flex items-center justify-center hover:bg-white/10 disabled:opacity-30 transition-colors shrink-0"
      >
        {anyPlaying ? <Pause size={15} /> : <Play size={15} />}
      </button>

      <button
        onClick={toggleSound}
        disabled={liveCount === 0 || !status?.audioAvailable}
        title={status?.soundOn
          ? 'Mute the preview (does not change what the export contains)'
          : 'Hear the preview'}
        aria-label={status?.soundOn ? 'Mute preview' : 'Unmute preview'}
        className={`w-8 h-8 rounded-lg flex items-center justify-center hover:bg-white/10 disabled:opacity-30 transition-colors shrink-0 ${
          status?.soundOn ? 'text-emerald-400' : 'text-gray-400'
        }`}
      >
        {status?.soundOn ? <Volume2 size={15} /> : <VolumeX size={15} />}
      </button>

      {/* Take length. Only lengths this device can actually survive are offered. */}
      <div className="flex items-center rounded-lg overflow-hidden border border-white/10 shrink-0">
        {durations.map((d) => (
          <button
            key={d}
            onClick={() => setSeconds(d)}
            disabled={busy}
            className={`px-1.5 py-1.5 text-[9px] font-black tracking-widest transition-colors disabled:opacity-30 ${
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
          className="w-8 h-8 rounded-lg bg-red-600/90 text-white flex items-center justify-center hover:bg-red-500 transition-colors shrink-0"
        ><Square size={12} fill="currentColor" /></button>
      ) : (
        <button
          onClick={() => startRecording()}
          disabled={!canRecord || liveCount === 0 || busy}
          // "(silent)" used to be hard-coded onto exactly this branch — which is
          // the branch that RENDERS SOUND. The offline renderer gained a mixer
          // and the label never moved, so the tool told you it was about to drop
          // your audio a moment before it kept it, and the owner had every
          // reason to read a silent file as expected behaviour. The label now
          // reads the same intent the export does.
          title={!canRecord
            ? 'Recording unavailable in this browser'
            : frameSupport?.supported
              ? `Render ${Math.min(seconds, profile.maxSeconds)}s — frame by frame, no dropped frames${
                  soundClipCount > 0
                    ? ` · sound from ${soundClipCount} clip${soundClipCount === 1 ? '' : 's'}`
                    : ' · silent (no clip has its sound on)'
                }`
              : `Record ${Math.min(seconds, profile.maxSeconds)}s in real time`}
          aria-label="Record video"
          className="w-8 h-8 rounded-lg text-red-400 flex items-center justify-center hover:bg-red-500/15 disabled:opacity-30 transition-colors shrink-0"
        >{recPhase === 'saving' ? <Loader2 size={14} className="animate-spin" /> : <Video size={15} />}</button>
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

      {/* THE TAKE — previewed with a real <video> so "it plays" is proven here,
          not assumed. The file is only worth offering if this element renders it.

          PORTALLED TO <body>, and that is load-bearing rather than tidy: this
          sheet lives inside a `relative z-10` wrapper, which IS a stacking
          context, so its own z-[300] was being resolved INSIDE that z-10 and the
          z-50 control dock painted over it. Save was genuinely unclickable —
          caught by a test click that kept being intercepted, not by looking. */}
      {result && createPortal((
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
