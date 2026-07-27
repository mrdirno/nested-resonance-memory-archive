import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Film, X, Loader2, AlertTriangle, Check, Sparkles, Rows, RotateCcw, Scissors,
} from 'lucide-react';

import {
  probeVideo, extractFrames, revokeFrames, formatTimecode, inspectSupport,
  MAX_FRAMES,
  type ExtractedFrame, type ExtractProgress, type ExtractResult,
  type FrameStrategy, type VideoProbe,
} from '../lib/video';

export interface VideoImportProps {
  /** The clip to import. Mount with a key derived from the file so state resets. */
  file: File;
  isMobile?: boolean;
  /**
   * Frames the user accepted. The sheet disposes their URLs once this resolves.
   *
   * `source.file` is the ORIGINAL clip, handed up so the app can keep it alive
   * for live playback. The sheet deliberately does not mint a durable URL for
   * it: everything this component creates, it revokes on unmount, and a URL the
   * clip needs for the rest of the session must not be on that hook.
   */
  onCommit: (
    frames: ExtractedFrame[],
    source: { file: File; name: string; duration: number; width: number; height: number },
  ) => Promise<void> | void;
  /** Dismiss. Always called after a commit, and on cancel. */
  onClose: () => void;
  /** Shown in the corner when more clips are queued behind this one. */
  queued?: number;
}

type Phase = 'probing' | 'ready' | 'extracting' | 'review' | 'committing' | 'error';

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

const formatDurationMs = (ms: number): string => {
  const s = Math.max(0, Math.round(ms / 1000));
  if (s < 60) return `${s}s`;
  return `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, '0')}s`;
};

const formatBytes = (bytes: number): string => {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const Label: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span className="text-[9px] font-bold tracking-[0.2em] text-gray-500 uppercase">{children}</span>
);

export const VideoImport: React.FC<VideoImportProps> = ({
  file, isMobile = false, onCommit, onClose, queued = 0,
}) => {
  const [phase, setPhase] = useState<Phase>('probing');
  const [probe, setProbe] = useState<VideoProbe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<ExtractProgress | null>(null);
  const [result, setResult] = useState<ExtractResult | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());

  const [frameCount, setFrameCount] = useState(isMobile ? 8 : 12);
  const [strategy, setStrategy] = useState<FrameStrategy>('smart');
  const [range, setRange] = useState<{ start: number; end: number } | null>(null);
  const [trimOpen, setTrimOpen] = useState(false);

  const abortRef = useRef<AbortController | null>(null);
  const framesRef = useRef<ExtractedFrame[]>([]);
  const aliveRef = useRef(true);

  const support = inspectSupport(file);

  const dropFrames = useCallback(() => {
    revokeFrames(framesRef.current);
    framesRef.current = [];
  }, []);

  // --- lifecycle: probe on mount, and NEVER leak a blob or a decoder ---------
  useEffect(() => {
    aliveRef.current = true;
    const ac = new AbortController();
    abortRef.current = ac;
    (async () => {
      try {
        const p = await probeVideo(file, ac.signal);
        if (!aliveRef.current) return;
        setProbe(p);
        if (p.error || p.duration <= 0) {
          setError(p.error || 'This video could not be read.');
          setPhase('error');
          return;
        }
        if (p.width <= 0 || p.height <= 0) {
          // Audio-only file in a video container. Say so NOW rather than after
          // the user has picked settings and waited through a decode.
          setError('This file has no visual track — it looks like audio only.');
          setPhase('error');
          return;
        }
        const trim = Math.min(p.duration * 0.02, 0.25);
        setRange({ start: trim, end: Math.max(trim + 0.1, p.duration - trim) });
        setPhase('ready');
      } catch (e: unknown) {
        if (!aliveRef.current) return;
        if ((e as { name?: string })?.name === 'AbortError') return;
        setError(e instanceof Error ? e.message : 'This video could not be read.');
        setPhase('error');
      }
    })();
    return () => {
      aliveRef.current = false;
      ac.abort();
      dropFrames();
    };
  }, [file, dropFrames]);

  // --- escape closes, exactly like every other sheet in this app ------------
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return;
      if (phase === 'extracting') { abortRef.current?.abort(); return; }
      if (phase !== 'committing') handleClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  const handleClose = () => {
    abortRef.current?.abort();
    dropFrames();
    onClose();
  };

  const runExtract = async () => {
    if (!probe || !range) return;
    dropFrames();
    setResult(null);
    setSelected(new Set());
    setError(null);
    setProgress(null);
    setPhase('extracting');

    const ac = new AbortController();
    abortRef.current = ac;
    try {
      const res = await extractFrames(file, {
        frameCount,
        strategy,
        maxDim: isMobile ? 1280 : 1600,
        maxSamples: isMobile ? 48 : 96,
        startTime: range.start,
        endTime: range.end,
        knownDuration: probe.duration,
        signal: ac.signal,
        onProgress: (p) => { if (aliveRef.current) setProgress(p); },
      });
      if (!aliveRef.current) { revokeFrames(res.frames); return; }
      framesRef.current = res.frames;
      setResult(res);
      setSelected(new Set(res.frames.map((f) => f.index)));
      setPhase('review');
    } catch (e: unknown) {
      if (!aliveRef.current) return;
      if ((e as { name?: string })?.name === 'AbortError') { setPhase('ready'); setProgress(null); return; }
      const base = e instanceof Error ? e.message : 'Frame extraction failed.';
      setError(isMobile
        ? `${base} On iPhone, Photos exports are often HEVC — share the clip as “Most Compatible” (H.264) and retry.`
        : base);
      setPhase('error');
    }
  };

  const commit = async () => {
    const frames = framesRef.current.filter((f) => selected.has(f.index));
    if (!frames.length) return;
    setPhase('committing');
    try {
      await onCommit(frames, {
        file,
        name: file.name,
        duration: probe?.duration ?? 0,
        width: probe?.width ?? 0,
        height: probe?.height ?? 0,
      });
    } catch (e) {
      console.error('[video] commit failed', e);
    } finally {
      dropFrames();
      onClose();
    }
  };

  const toggleFrame = (index: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index); else next.add(index);
      return next;
    });
  };

  const frames = framesRef.current;
  const busy = phase === 'extracting' || phase === 'committing';

  // --- notes the run has to be honest about --------------------------------
  const notes: string[] = [];
  if (result) {
    if (result.failed > 0) notes.push(`${result.failed} timestamp${result.failed > 1 ? 's' : ''} could not be decoded`);
    if (result.blankDropped > 0) notes.push(`${result.blankDropped} blank frame${result.blankDropped > 1 ? 's' : ''} skipped`);
    if (result.blankKept > 0) notes.push(`${result.blankKept} near-blank frame${result.blankKept > 1 ? 's' : ''} kept — the clip is very dark`);
    if (result.truncated) notes.push('stopped early (time budget or decoder stall)');
    if (result.frames.length < frameCount) notes.push(`${result.frames.length} of ${frameCount} requested frames survived`);
  }

  return (
    <div
      className="fixed inset-0 z-[300] bg-black/90 backdrop-blur-md flex items-stretch sm:items-center justify-center sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-label="Import video frames"
    >
      <div
        className="relative w-full sm:max-w-3xl bg-[#0a0a0a] sm:border sm:border-white/10 sm:rounded-2xl flex flex-col overflow-hidden shadow-2xl"
        style={{ maxHeight: '100%' }}
      >
        {/* ---------- HEADER ---------- */}
        <div className="shrink-0 flex items-start gap-3 px-4 py-3 border-b border-white/10 bg-[#0e0e0e]">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shrink-0">
            <Film size={16} className="text-emerald-400" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-[11px] font-bold text-white truncate">{file.name}</div>
            <div className="text-[9px] tracking-widest text-gray-500 uppercase mt-0.5 flex flex-wrap gap-x-2">
              <span>{formatBytes(file.size)}</span>
              {probe && probe.duration > 0 && <span>· {formatTimecode(probe.duration)}</span>}
              {probe && probe.width > 0 && <span>· {probe.width}×{probe.height}</span>}
              {queued > 0 && <span className="text-emerald-500">· {queued} more queued</span>}
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={phase === 'committing'}
            aria-label="Close"
            className="w-9 h-9 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 flex items-center justify-center transition-colors disabled:opacity-30"
          >
            <X size={16} />
          </button>
        </div>

        {/* ---------- BODY ---------- */}
        <div className="flex-1 overflow-y-auto overscroll-contain">
          {phase === 'probing' && (
            <div className="py-16 flex flex-col items-center gap-3">
              <Loader2 size={28} className="animate-spin text-emerald-500" />
              <Label>Reading clip…</Label>
            </div>
          )}

          {phase === 'error' && (
            <div className="p-6 flex flex-col items-center text-center gap-4">
              <AlertTriangle size={30} className="text-red-500" />
              <p className="text-[12px] leading-relaxed text-gray-300 max-w-md">{error}</p>
              <div className="flex gap-2">
                {probe && probe.duration > 0 && (
                  <button
                    onClick={() => { setError(null); setPhase('ready'); }}
                    className="px-4 py-2.5 rounded-lg bg-[#1a1a1a] border border-white/10 text-[10px] font-bold tracking-widest text-white hover:bg-[#222]"
                  >
                    TRY AGAIN
                  </button>
                )}
                <button
                  onClick={handleClose}
                  className="px-4 py-2.5 rounded-lg bg-[#1a1a1a] border border-white/10 text-[10px] font-bold tracking-widest text-gray-400 hover:bg-[#222]"
                >
                  CLOSE
                </button>
              </div>
            </div>
          )}

          {(phase === 'ready' || phase === 'extracting') && probe && range && (
            <div className="p-4 space-y-5">
              {support.level === 'unlikely' && support.message && (
                <div className="flex gap-2 items-start text-[10px] leading-relaxed text-yellow-500/90 bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-3">
                  <AlertTriangle size={13} className="shrink-0 mt-px" />
                  <span>{support.message}</span>
                </div>
              )}

              {/* FRAME COUNT */}
              <div>
                <div className="flex items-baseline justify-between mb-2">
                  <Label>Frames</Label>
                  <span className="text-[13px] font-black text-white tabular-nums">{frameCount}</span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={MAX_FRAMES}
                  step={1}
                  value={frameCount}
                  disabled={busy}
                  onChange={(e) => setFrameCount(clamp(parseInt(e.target.value, 10) || 1, 1, MAX_FRAMES))}
                  className="w-full accent-emerald-500 h-6 cursor-pointer disabled:opacity-40"
                  aria-label="Number of frames to extract"
                />
                <div className="flex justify-between text-[8px] tracking-widest text-gray-600 uppercase">
                  <span>1</span><span>{MAX_FRAMES} max</span>
                </div>
              </div>

              {/* STRATEGY */}
              <div>
                <Label>Sampling</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {([
                    { id: 'uniform' as FrameStrategy, icon: Rows, name: 'EVEN', desc: 'Equal spacing' },
                    { id: 'smart' as FrameStrategy, icon: Sparkles, name: 'SMART', desc: 'Most distinct' },
                  ]).map(({ id, icon: Icon, name, desc }) => (
                    <button
                      key={id}
                      onClick={() => setStrategy(id)}
                      disabled={busy}
                      className={`p-3 rounded-xl border text-left transition-all active:scale-[0.98] disabled:opacity-40 ${
                        strategy === id
                          ? 'bg-emerald-500/10 border-emerald-500/60'
                          : 'bg-[#111] border-white/10 hover:border-white/25'
                      }`}
                    >
                      <Icon size={14} className={strategy === id ? 'text-emerald-400' : 'text-gray-500'} />
                      <div className={`text-[10px] font-black tracking-widest mt-1.5 ${strategy === id ? 'text-white' : 'text-gray-400'}`}>{name}</div>
                      <div className="text-[9px] text-gray-600 mt-0.5">{desc}</div>
                    </button>
                  ))}
                </div>
                {strategy === 'smart' && (
                  <p className="text-[9px] text-gray-600 mt-2 leading-relaxed">
                    Smart decodes up to 3× more frames, then keeps the ones least alike. Slower, better spread.
                  </p>
                )}
              </div>

              {/* RANGE */}
              <div>
                <button
                  onClick={() => setTrimOpen((v) => !v)}
                  disabled={busy}
                  className="flex items-center gap-2 disabled:opacity-40"
                >
                  <Scissors size={11} className="text-gray-500" />
                  <Label>Range</Label>
                  <span className="text-[10px] text-gray-400 tabular-nums">
                    {formatTimecode(range.start)} – {formatTimecode(range.end)}
                  </span>
                  <span className="text-[9px] text-emerald-600 tracking-widest">{trimOpen ? 'HIDE' : 'EDIT'}</span>
                </button>
                {trimOpen && (
                  <div className="mt-3 space-y-3">
                    {([
                      { key: 'start' as const, label: 'FROM' },
                      { key: 'end' as const, label: 'TO' },
                    ]).map(({ key, label }) => (
                      <div key={key}>
                        <div className="flex justify-between text-[9px] tracking-widest text-gray-500 mb-1">
                          <span>{label}</span>
                          <span className="text-gray-300 tabular-nums">{formatTimecode(range[key])}</span>
                        </div>
                        <input
                          type="range"
                          min={0}
                          max={Math.max(0.1, probe.duration)}
                          step={Math.max(0.01, probe.duration / 500)}
                          value={range[key]}
                          disabled={busy}
                          onChange={(e) => {
                            const v = parseFloat(e.target.value);
                            setRange((r) => {
                              if (!r) return r;
                              return key === 'start'
                                ? { start: Math.min(v, r.end - 0.2), end: r.end }
                                : { start: r.start, end: Math.max(v, r.start + 0.2) };
                            });
                          }}
                          className="w-full accent-emerald-500 h-6 cursor-pointer disabled:opacity-40"
                          aria-label={`${label} time`}
                        />
                      </div>
                    ))}
                    <button
                      onClick={() => {
                        const trim = Math.min(probe.duration * 0.02, 0.25);
                        setRange({ start: trim, end: Math.max(trim + 0.1, probe.duration - trim) });
                      }}
                      disabled={busy}
                      className="text-[9px] tracking-widest text-gray-500 hover:text-white flex items-center gap-1 disabled:opacity-40"
                    >
                      <RotateCcw size={10} /> RESET RANGE
                    </button>
                  </div>
                )}
              </div>

              {/* PROGRESS */}
              {phase === 'extracting' && (
                <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/5 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold tracking-widest text-white flex items-center gap-2">
                      <Loader2 size={11} className="animate-spin text-emerald-400" />
                      {progress?.label ?? 'Starting…'}
                    </span>
                    <span className="text-[10px] tabular-nums text-emerald-400">
                      {Math.round((progress?.ratio ?? 0) * 100)}%
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 transition-[width] duration-200"
                      style={{ width: `${Math.max(2, Math.round((progress?.ratio ?? 0) * 100))}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[9px] tracking-widest text-gray-500 mt-2 uppercase">
                    <span>{progress?.framesReady ?? 0} banked</span>
                    <span>
                      {progress?.etaMs != null ? `~${formatDurationMs(progress.etaMs)} left` : 'estimating…'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {(phase === 'review' || phase === 'committing') && result && (
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="text-[10px] tracking-widest text-gray-400 uppercase">
                  <span className="text-white font-black">{selected.size}</span> / {frames.length} selected
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelected(new Set(frames.map((f) => f.index)))}
                    className="text-[9px] tracking-widest text-gray-500 hover:text-white px-2 py-1"
                  >ALL</button>
                  <button
                    onClick={() => setSelected(new Set())}
                    className="text-[9px] tracking-widest text-gray-500 hover:text-white px-2 py-1"
                  >NONE</button>
                </div>
              </div>

              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                {frames.map((f) => {
                  const on = selected.has(f.index);
                  return (
                    <button
                      key={f.index}
                      onClick={() => toggleFrame(f.index)}
                      disabled={phase === 'committing'}
                      className={`relative aspect-square rounded-lg overflow-hidden border transition-all active:scale-95 ${
                        on ? 'border-emerald-500' : 'border-white/10 opacity-40 hover:opacity-70'
                      }`}
                      aria-pressed={on}
                      aria-label={`Frame at ${formatTimecode(f.time)}`}
                    >
                      <img
                        src={f.url}
                        loading="lazy"
                        decoding="async"
                        className="w-full h-full object-cover pointer-events-none"
                        alt=""
                      />
                      <span className="absolute bottom-0 left-0 right-0 bg-black/70 text-[8px] tabular-nums text-white px-1 py-0.5 text-left">
                        {formatTimecode(f.time)}
                      </span>
                      {on && (
                        <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center">
                          <Check size={10} className="text-black" strokeWidth={4} />
                        </span>
                      )}
                      {f.blank && (
                        <span className="absolute top-1 left-1 text-[7px] font-bold tracking-widest bg-yellow-500 text-black px-1 rounded">
                          FLAT
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              {notes.length > 0 && (
                <div className="mt-3 text-[9px] leading-relaxed text-gray-500 flex gap-2 items-start">
                  <AlertTriangle size={11} className="shrink-0 mt-px text-yellow-600" />
                  <span>{notes.join(' · ')}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ---------- FOOTER ---------- */}
        <div
          className="shrink-0 border-t border-white/10 bg-[#0e0e0e] p-3 flex gap-2"
          style={{ paddingBottom: 'max(0.75rem, env(safe-area-inset-bottom))' }}
        >
          {phase === 'extracting' ? (
            <button
              onClick={() => abortRef.current?.abort()}
              className="flex-1 py-3.5 rounded-xl bg-[#1a1a1a] border border-white/10 text-[11px] font-black tracking-widest text-red-400 hover:bg-red-950/40 transition-colors"
            >
              CANCEL
            </button>
          ) : phase === 'review' || phase === 'committing' ? (
            <>
              <button
                onClick={() => setPhase('ready')}
                disabled={phase === 'committing'}
                className="px-4 py-3.5 rounded-xl bg-[#1a1a1a] border border-white/10 text-[11px] font-black tracking-widest text-gray-400 hover:text-white disabled:opacity-40"
              >
                REDO
              </button>
              <button
                onClick={commit}
                disabled={phase === 'committing' || selected.size === 0}
                className="flex-1 py-3.5 rounded-xl bg-white text-black text-[11px] font-black tracking-widest hover:bg-emerald-400 transition-colors disabled:opacity-30 disabled:hover:bg-white flex items-center justify-center gap-2"
              >
                {phase === 'committing'
                  ? <><Loader2 size={13} className="animate-spin" /> ADDING…</>
                  : `ADD ${selected.size} FRAME${selected.size === 1 ? '' : 'S'}`}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleClose}
                className="px-4 py-3.5 rounded-xl bg-[#1a1a1a] border border-white/10 text-[11px] font-black tracking-widest text-gray-400 hover:text-white"
              >
                CANCEL
              </button>
              <button
                onClick={runExtract}
                disabled={phase !== 'ready'}
                className="flex-1 py-3.5 rounded-xl bg-white text-black text-[11px] font-black tracking-widest hover:bg-emerald-400 transition-colors disabled:opacity-30 disabled:hover:bg-white"
              >
                EXTRACT {frameCount} FRAME{frameCount === 1 ? '' : 'S'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoImport;
