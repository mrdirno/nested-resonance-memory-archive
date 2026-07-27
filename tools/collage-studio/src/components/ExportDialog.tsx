import React, { useEffect, useState } from 'react';
import { X, FileJson, FileCode, Zap, Share, Download, Image, Video } from 'lucide-react';

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
  onExportVideo?: (seconds: number) => void;
  /** Device ceiling, so the offered lengths are ones that will actually survive. */
  videoMaxSeconds?: number;
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
  canExportVideo = false, onExportVideo, videoMaxSeconds = 30
}) => {
  const [resIndex, setResIndex] = useState(1); // 4K
  const current = PRESETS[resIndex];
  const videoLengths = [5, 10, 15, 30].filter(v => v <= videoMaxSeconds);
  const [vidSeconds, setVidSeconds] = useState(10);

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
                    <span className="block ui-caption mt-1">
                      Captures what is on screen, with the sound of any unmuted clip. MP4 where the
                      browser can write one.
                    </span>
                  </span>
                </div>
                <div className="flex gap-2 items-center">
                  <div className="flex items-center rounded-lg overflow-hidden border border-[color:var(--line-1)] shrink-0">
                    {videoLengths.map(v => (
                      <button
                        key={v}
                        onClick={() => setVidSeconds(v)}
                        data-active={vidSeconds === v}
                        aria-pressed={vidSeconds === v}
                        className={`px-2.5 py-2 text-[10px] font-black tracking-widest transition-colors ${
                          vidSeconds === v ? 'bg-white/15 text-white' : 'text-[color:var(--ink-3)] hover:text-white'
                        }`}
                      >{v}s</button>
                    ))}
                  </div>
                  <button
                    onClick={() => { onClose(); onExportVideo?.(Math.min(vidSeconds, videoMaxSeconds)); }}
                    className="ui-btn ui-btn--primary ui-btn--tall flex-1"
                  >
                    <Video size={17} />
                    <span>Record {Math.min(vidSeconds, videoMaxSeconds)}s video</span>
                  </button>
                </div>
                <p className="ui-caption">
                  Unlike the JPG, this is captured live from the preview — keep the collage on screen
                  while it records.
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
                <span className="block ui-caption mt-1">Fragment outlines with the images embedded — for plotters and editing.</span>
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
