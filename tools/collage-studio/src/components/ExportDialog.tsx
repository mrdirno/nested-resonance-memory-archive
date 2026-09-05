import React, { useEffect, useState } from 'react';
import { X, FileJson, FileCode, Zap, Share, Download, Image, Video } from 'lucide-react';
import type { VideoSizeOption } from '../lib/frameExport';

interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (size: number) => void; // Unified handler
  onExportSVG: () => void;
  onExportProject: () => void;
  canShare: boolean;
  onShare: () => void;
  /** True when a live clip is on the canvas — the only case where video means anything. */
  canExportVideo?: boolean;
  /**
   * Record the MOVING collage. Must be invoked straight from this button's own
   * click: starting a capture is gesture-bound, so anything that defers it by a
   * task records silence, or nothing.
   */
  onExportVideo?: (seconds: number, renderWidth?: number) => void;
  /** Device ceiling, so the offered lengths are ones that will actually survive. */
  videoMaxSeconds?: number;
  /** One exact loop when all native artwork sources share a duration. */
  artLoopSeconds?: number;
  /**
   * The frame sizes THIS device accepted at THIS composition's shape, already
   * probed. Empty renders no row at all — an unprobed ladder is a guess, and a
   * guess here costs somebody a whole render.
   */
  videoSizes?: VideoSizeOption[];
  /** False when the take will be captured live, where the size cannot be chosen. */
  canChooseVideoSize?: boolean;
}

const PRESETS = [
  { val: 2048,  label: '2K',  desc: 'Screens and social. Fast, always works.' },
  { val: 4096,  label: '4K',  desc: 'Prints to roughly A3 at 300 dpi.' },
  { val: 8192,  label: '8K',  desc: 'Big print. About as far as a phone gets.' },
  { val: 16384, label: '16K', desc: 'Gallery print. Desktop browsers only.' },
  { val: 30000, label: 'MAX', desc: 'Starts at 30 000 px and steps down until your device copes.' },
];

export const ExportDialog: React.FC<ExportDialogProps> = ({
  isOpen, onClose, onExport, onExportSVG, onExportProject, canShare, onShare,
  canExportVideo = false, onExportVideo, videoMaxSeconds = 30,
  videoSizes = [], canChooseVideoSize = false, artLoopSeconds,
}) => {
  const [resIndex, setResIndex] = useState(1); // 4K
  const current = PRESETS[resIndex];
  const videoLengths = [...new Set([5, 10, 15, 30, ...(artLoopSeconds ? [artLoopSeconds] : [])])].filter(v => v <= videoMaxSeconds).sort((a,b) => a-b);
  const [vidSeconds, setVidSeconds] = useState(10);
  useEffect(() => {
    if (!isOpen) return;
    if (artLoopSeconds && artLoopSeconds <= videoMaxSeconds) setVidSeconds(artLoopSeconds);
    else setVidSeconds(previous => videoLengths.includes(previous) ? previous : (videoLengths.includes(10) ? 10 : videoLengths[0] ?? 5));
  }, [isOpen, artLoopSeconds, videoMaxSeconds]);

  // THE SIZE ROW. Only rungs this device really accepted are selectable; the
  // refused ones stay visible with the reason, because "4K is missing" and "4K
  // is impossible at this shape" are different facts and only one of them is
  // ours to explain.
  const okSizes = videoSizes.filter(s => s.supported);
  const [vidSizeIdx, setVidSizeIdx] = useState(0);
  // Default to 2K where the device reaches it, else the top it does reach — a
  // real step up from the fixed 1200px this replaced, without defaulting
  // everyone onto the slowest render on the ladder.
  useEffect(() => {
    if (!okSizes.length) return;
    const twoK = okSizes.findIndex(s => s.longEdge >= 2048);
    setVidSizeIdx(twoK >= 0 ? twoK : okSizes.length - 1);
  }, [videoSizes]);   // eslint-disable-line react-hooks/exhaustive-deps
  const vidSize = okSizes[Math.min(vidSizeIdx, Math.max(0, okSizes.length - 1))];
  const showSizes = canChooseVideoSize && okSizes.length > 1;

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowDown') setResIndex(i => Math.min(PRESETS.length - 1, i + 1));
      if (e.key === 'ArrowUp') setResIndex(i => Math.max(0, i - 1));
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="export-title"
    >
      <button
        className="ui-scrim"
        aria-label="Close export sheet"
        onClick={onClose}
      />

      <div
        className="ui-sheet relative w-full sm:max-w-[440px] max-h-[88vh] overflow-y-auto
                   rounded-b-none sm:rounded-[20px] animate-in slide-in-from-bottom-4 duration-300"
        style={{ paddingBottom: 'var(--safe-b)' }}
      >
        {/* sheet grabber — tells a phone user this panel came up from the bottom */}
        <div className="sm:hidden flex justify-center pt-2.5 pb-1">
          <span className="block w-9 h-1 rounded-full bg-[color:var(--line-3)]" />
        </div>

        <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-[color:var(--line-1)]">
          <div className="min-w-0">
            <h2 id="export-title" className="ui-label ui-label--on" style={{ fontSize: 'var(--t-label)' }}>
              Export
            </h2>
            <p className="ui-caption mt-1">Renders the full-resolution collage from the originals.</p>
          </div>
          <button onClick={onClose} className="ui-btn ui-btn--ghost ui-btn--icon" aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className="p-4 flex flex-col gap-4">

          {/* ---- SIZE: discrete rows, not a slider you have to hit ---------- */}
          <div className="flex flex-col gap-1.5" role="radiogroup" aria-label="Export size">
            <span className="ui-label">Size — long edge</span>
            {PRESETS.map((p, i) => (
              <button
                key={p.val}
                role="radio"
                aria-checked={i === resIndex}
                onClick={() => setResIndex(i)}
                data-active={i === resIndex}
                className="ui-option"
              >
                <span className="ui-option__radio" />
                <span className="ui-option__key">{p.label}</span>
                <span className="min-w-0 flex-1">
                  <span className="block ui-caption" style={{ color: 'var(--ink-2)' }}>{p.desc}</span>
                </span>
                <span className="ui-num ui-caption whitespace-nowrap">
                  {p.val === 30000 ? 'auto' : `${p.val}px`}
                </span>
              </button>
            ))}
          </div>

          {/* ---- PRIMARY ---------------------------------------------------- */}
          <div className="flex gap-2">
            <button
              onClick={() => onExport(current.val)}
              className="ui-btn ui-btn--primary ui-btn--tall flex-1"
              autoFocus
            >
              {current.val === 30000 ? <Zap size={18} /> : <Download size={18} />}
              <span>Render {current.label} JPG</span>
            </button>

            {canShare && (
              <button
                onClick={onShare}
                className="ui-btn ui-btn--stack ui-btn--tall"
                style={{ width: 84 }}
                title="Render at 4K and hand it to the system share sheet"
              >
                <Share size={17} />
                <span>Share<br />4K</span>
              </button>
            )}
          </div>

          <p className="ui-caption -mt-2">
            Large sizes are rendered off the main thread. If a size fails, the studio
            reports it and you can drop a step.
          </p>

          <div className="h-px bg-[color:var(--line-1)]" />

          {/* ---- VIDEO ------------------------------------------------------ */}
          {canExportVideo && (
            <>
              <div className="flex flex-col gap-1.5">
                <span className="ui-label">Video</span>
                <div className="ui-option" style={{ cursor: 'default' }}>
                  <span className="ui-option__icon" style={{ color: '#ff6a6a' }}><Video size={16} /></span>
                  <span className="min-w-0 flex-1">
                    <span className="block ui-label ui-label--on">Record the moving collage</span>
                    {/* This said "captures what is on screen" while the row
                        directly beneath it said "drawn from your original
                        photos, not the previews" — two claims about one button,
                        and the screen one stopped being true when the render
                        started drawing the originals at its own size. */}
                    <span className="block ui-caption mt-1">
                      {canChooseVideoSize
                        ? 'Rendered from your sources at the size you pick, with the sound of any unmuted clip. MP4 where the browser can write one.'
                        : 'Captures what is on screen, with the sound of any unmuted clip. MP4 where the browser can write one.'}
                    </span>
                  </span>
                </div>
                {showSizes && (
                  <div className="flex flex-col gap-1.5" role="radiogroup" aria-label="Video size">
                    <span className="ui-label">Size — long edge</span>
                    {/* Wraps rather than scrolls: three rungs at 44px fit a 320px
                        screen in two rows, and a horizontally scrolling strip of
                        options is the thing you cannot find with a thumb. */}
                    <div className="flex flex-wrap gap-1.5">
                      {videoSizes.map((s, i) => {
                        const idx = okSizes.indexOf(s);
                        const on = s.supported && idx === Math.min(vidSizeIdx, okSizes.length - 1);
                        return (
                          <button
                            key={`${s.label}-${s.width}x${s.height}-${i}`}
                            role="radio"
                            aria-checked={on}
                            disabled={!s.supported}
                            onClick={() => { if (s.supported) setVidSizeIdx(idx); }}
                            title={s.supported ? `${s.width} × ${s.height}` : (s.reason ?? undefined)}
                            className={`min-h-[44px] px-3 py-1.5 rounded-lg border text-left transition-colors ${
                              on
                                ? 'border-white/40 bg-white/15 text-white'
                                : s.supported
                                ? 'border-[color:var(--line-1)] text-[color:var(--ink-3)] hover:text-white hover:border-white/25'
                                : 'border-[color:var(--line-1)] text-[color:var(--ink-3)] opacity-40 cursor-not-allowed'
                            }`}
                          >
                            <span className="block text-[11px] font-black tracking-widest">{s.label}</span>
                            <span className="block text-[9px] tabular-nums tracking-wide opacity-70">
                              {s.supported ? `${s.width}×${s.height}` : 'not on this device'}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                    <p className="ui-caption">
                      Drawn from your original photos, not the previews. Video tops out lower than the
                      JPG on purpose — H.264 caps the frame, and at this shape that ceiling is
                      {' '}{okSizes.length ? `${okSizes[okSizes.length - 1].width}×${okSizes[okSizes.length - 1].height}` : 'reached'}.
                      Bigger takes longer to render.
                    </p>
                    {/* CREDIT ON THE PAGE, not only in credits.json — and on the
                        control itself, so the person who asked finds it where
                        they asked. Both wishers stayed anonymous.

                        TWO wishes now sit behind this one control: the ladder
                        itself, and the memory budget that decides how much of
                        each original a take can actually hold. A second
                        identical credit line would be noise, and dropping the
                        second wisher to avoid it would be worse — so the line
                        names both. */}
                    <p className="ui-caption" style={{ opacity: 0.6 }}>
                      Wished for by anonymous Collage users — this ladder, and the quality
                      fallbacks behind it.
                    </p>
                  </div>
                )}
                <div className="flex flex-wrap gap-2 items-center">
                  <div className="flex items-center rounded-lg overflow-hidden border border-[color:var(--line-1)] shrink-0 max-w-full flex-wrap">
                    {videoLengths.map(v => (
                      <button
                        key={v}
                        onClick={() => setVidSeconds(v)}
                        data-active={vidSeconds === v}
                        aria-pressed={vidSeconds === v}
                        // 44px MINIMUM, both axes. These were px-2.5 py-2 —
                        // 43x30 — which is under a thumb on every phone this
                        // ships to, and they sit directly beside the take
                        // button in a sheet that is only ever opened on one.
                        // Found by the size row's own mobile gate; pre-existing.
                        className={`min-h-[44px] min-w-[44px] px-2.5 text-[10px] font-black tracking-widest transition-colors ${
                          vidSeconds === v ? 'bg-white/15 text-white' : 'text-[color:var(--ink-3)] hover:text-white'
                        }`}
                      >{v === artLoopSeconds ? `Loop ${v}s` : `${v}s`}</button>
                    ))}
                  </div>
                  <button
                    onClick={() => { onClose(); onExportVideo?.(Math.min(vidSeconds, videoMaxSeconds), vidSize?.width); }}
                    className="ui-btn ui-btn--primary ui-btn--tall flex-1"
                  >
                    <Video size={17} />
                    <span>Record {Math.min(vidSeconds, videoMaxSeconds)}s video</span>
                  </button>
                </div>
                <p className="ui-caption">
                  {canChooseVideoSize
                    ? 'Rendered frame by frame, so nothing drops — it takes longer than the clip is long.'
                    : 'Captured live from the preview — keep the collage on screen while it records.'}
                </p>
              </div>

              <div className="h-px bg-[color:var(--line-1)]" />
            </>
          )}

          {/* ---- OTHER FORMATS --------------------------------------------- */}
          <div className="flex flex-col gap-1.5">
            <span className="ui-label">Other formats</span>

            <button onClick={onExportSVG} className="ui-option">
              <span className="ui-option__icon" style={{ color: '#6aa9ff' }}><FileCode size={16} /></span>
              <span className="min-w-0 flex-1">
                <span className="block ui-label ui-label--on">Vector SVG</span>
                {/* "exactly as you left it" was the first draft of this line and
                    it is not true of a video project. The SVG carries the FRAMES
                    the collage drew — `metaForAsset` keeps id, name and analysis
                    and drops `clipId`/`sourceKind` — so a reopened clip is a
                    still, and this option is not gated on the video tab. Say the
                    limit here rather than let a man find it after he sends the
                    file to somebody. */}
                <span className="block ui-caption mt-1">The picture AND the project in one file. Every photo embedded, prints at any size, drops back into Open. Clips come back as the frames they drew, not as video.</span>
              </span>
            </button>

            <button onClick={onExportProject} className="ui-option">
              <span className="ui-option__icon" style={{ color: '#c08bff' }}><FileJson size={16} /></span>
              <span className="min-w-0 flex-1">
                <span className="block ui-label ui-label--on">Project file</span>
                <span className="block ui-caption mt-1">A .collage archive of the sources and every setting. Reopen with Open.</span>
              </span>
            </button>

            <div className="ui-empty mt-1">
              <div className="ui-empty__icon"><Image size={15} /></div>
              <p className="ui-caption">
                The JPG is rendered from your original files, not from the preview on screen —
                the preview is a fast proxy.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
