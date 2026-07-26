import React, { useEffect } from 'react';
import {
  Download, Check, AlertCircle, Loader2, ScanFace, Ruler, FolderOpen, RefreshCw
} from 'lucide-react';

interface HeaderProps {
  aiState: string;
  exportStatus: string;
  exportMsg: string;
  onExport: () => void;
  hasImages: boolean;
  onSaveProject: () => void;
  onLoadProject: () => void;
}

/**
 * Instrument chrome: one row, 44px targets, top safe-area honoured.
 *
 * Deliberately still in normal flow rather than overlaid on the canvas — the
 * canvas layer owns an absolutely-positioned button cluster in its top-right
 * corner, and floating this bar would land on top of it. The canvas wins its
 * space back from the capped control dock instead (see .ui-dock).
 */
export const Header: React.FC<HeaderProps> = ({
  aiState, exportStatus, exportMsg, onExport, hasImages,
  onSaveProject, onLoadProject
}) => {

  // Desktop shortcuts. Costs no layout space, and gives onSaveProject a home
  // that does not push a third button into a 375px-wide bar.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!(e.metaKey || e.ctrlKey)) return;
      const t = e.target as HTMLElement | null;
      if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
      const k = e.key.toLowerCase();
      if (k === 's' && hasImages) { e.preventDefault(); onSaveProject(); }
      if (k === 'e' && hasImages) { e.preventDefault(); onExport(); }
      if (k === 'o') { e.preventDefault(); onLoadProject(); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [hasImages, onSaveProject, onExport, onLoadProject]);

  const ai = {
    loading:  { tone: 'warn', icon: <Loader2 size={11} className="ui-spin" />, text: 'Loading face model' },
    ready:    { tone: 'ok',   icon: <ScanFace size={11} />,                    text: 'Face-aware crop' },
    failed:   { tone: 'idle', icon: <Ruler size={11} />,                       text: 'Geometry crop' },
    inactive: { tone: 'idle', icon: <span className="ui-dot" />,               text: 'Starting' },
  }[aiState] ?? { tone: 'idle', icon: <span className="ui-dot" />, text: 'Starting' };

  const aiTitle =
    aiState === 'ready'  ? 'Faces are detected and kept inside each fragment when cropping.'
  : aiState === 'failed' ? 'Face model unavailable — fragments are anchored on the busiest region of each image instead.'
  : aiState === 'loading'? 'Fetching the face-detection model. Cropping falls back to geometry if it fails.'
  : 'Booting the crop engine.';

  const exporting = exportStatus === 'processing';

  return (
    <header className="ui-topbar">
      <div className="min-w-0 overflow-hidden flex flex-col gap-1.5">
        <div className="ui-mark">GEN<b>ART</b></div>
        <span className="ui-status" data-tone={ai.tone} title={aiTitle}>
          {ai.icon}
          {ai.text}
        </span>
      </div>

      <div className="ui-topbar__actions">
        <button
          onClick={onLoadProject}
          className="ui-btn ui-btn--quiet ui-btn--compact"
          title="Open a saved .collage project or an exported SVG layout (⌘O)"
        >
          <FolderOpen size={15} />
          <span>Open</span>
        </button>

        {hasImages && (
          <button
            onClick={onExport}
            disabled={exporting}
            className={`ui-btn ui-btn--compact ${
              exportStatus === 'error' ? 'ui-btn--bad'
            : exporting                ? 'ui-btn--warn'
            : 'ui-btn--primary'
            }`}
            title={
              exportStatus === 'error'
                ? 'The last render failed. Open the export sheet and try a smaller size.'
                : 'Render and save the collage (⌘E)'
            }
          >
            {exporting ? (
              <><RefreshCw size={15} className="ui-spin" /><span className="ui-btn__msg">{exportMsg || 'Rendering'}</span></>
            ) : exportStatus === 'done' ? (
              <><Check size={15} /><span>Saved</span></>
            ) : exportStatus === 'error' ? (
              <><AlertCircle size={15} /><span>Retry</span></>
            ) : (
              <><Download size={15} /><span>Export</span></>
            )}
          </button>
        )}
      </div>
    </header>
  );
};
