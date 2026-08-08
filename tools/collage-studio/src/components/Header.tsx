import React, { useEffect } from 'react';
import {
  Download, Check, AlertCircle, Loader2, ScanFace, Ruler, FolderOpen, RefreshCw, MessageSquarePlus
} from 'lucide-react';

interface HeaderProps {
  aiState: string;
  exportStatus: string;
  exportMsg: string;
  onExport: () => void;
  hasImages: boolean;
  onSaveProject: () => void;
  onLoadProject: () => void;
  /**
   * WHY THE LAST OPEN DID NOTHING. `loadProject` fails closed — a file it cannot
   * reopen EXACTLY is refused rather than half-opened — and a refusal that shows
   * nothing is indistinguishable from a hang. It belongs on the Open button and
   * not on Export: the export button's error state says "Retry", which would
   * retry a render the user never ran.
   */
  openError?: string | null;
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
  onSaveProject, onLoadProject, openError = null
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
        {/* FEEDBACK — the universal wishing well (operator 2026-08-04: "there's a
            lot of bugs still and people should be able to send the feedback so the
            loop cycles can address them").

            The well itself is shared/feedback.js, loaded by index.html and shared
            byte-for-byte with every other surface we ship — this app owns only WHERE
            the trigger sits. It lives here rather than as the script's own floating
            button because the canvas layer already owns the top-right corner and the
            control dock owns the bottom (up to min(44vh, 356px)), so a fixed FAB
            would sit on top of one of them. The topbar is the only chrome rendered on
            every screen, including the empty state.

            Guarded on the global: in local dev the sibling ../shared/feedback.js
            404s, so the button simply does nothing rather than throwing. */}
        <button
          onClick={() => (window as any).Feedback?.open('bug')}
          className="ui-btn ui-btn--quiet ui-btn--compact"
          title="Report a bug, wish it better, or ask for a feature — it goes straight to the loop that builds this"
        >
          <MessageSquarePlus size={15} />
          <span>Feedback</span>
        </button>

        <button
          onClick={onLoadProject}
          className={`ui-btn ui-btn--compact ${openError ? 'ui-btn--bad' : 'ui-btn--quiet'}`}
          title={openError
            ? `${openError} — a .collage archive, or an SVG exported by this app.`
            : 'Open a saved .collage project or an exported SVG (⌘O)'}
        >
          {/* THE LABEL DOES NOT CHANGE WIDTH, and that is the whole point.
              The first version of this swapped "Open" (4 characters) for
              "COULDN'T OPEN THAT FILE" (23) inside `.ui-topbar__actions`, which
              has no wrap, no `min-width: 0` and no `overflow-x` — so the row's
              min-content width went 317px -> 390px and simply grew past the
              viewport, shoving the EXPORT button off the right edge: 94px of it
              gone at 320, 54px at 360, 24px at 390, leaving the primary action a
              6.6px sliver. Nothing caught it, because the app sits inside a
              `fixed inset-0` with `overflow: hidden`, so those pixels are
              DESTROYED rather than scrolled and `documentElement.scrollWidth`
              stays exactly equal to `clientWidth` — the mobile gate reads clean
              while the button is off-screen. `getBoundingClientRect().width`
              lies the same way: 100.6px for a button 94px outside the viewport.
              The message itself was never readable here anyway — `.ui-btn__msg`
              caps at 108px and the string measures 174px, so it rendered as
              "COULDN'T OPEN…" at EVERY width, desktop included, with the rest
              reachable only through a `title` attribute no touch device can
              surface. So the sentence goes where this app already puts its
              failures — the notice toast — and the button only changes COLOUR
              and ICON, both of which cost exactly zero pixels. */}
          {openError ? <AlertCircle size={15} /> : <FolderOpen size={15} />}
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
