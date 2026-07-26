import React, { useEffect, useState } from 'react';
import { X, Share, Download, AlertCircle, Check, Loader2 } from 'lucide-react';

interface ResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  blobUrl: string | null;
  onShare: () => void;
  onDownload: () => void;
  isMobile: boolean;
}

export const ResultModal: React.FC<ResultModalProps> = ({
  isOpen, onClose, blobUrl, onShare, onDownload, isMobile
}) => {
  // Derive the decode state from the blob URL itself rather than resetting it
  // in an effect — a new render is a new URL, so the skeleton comes back with
  // no ordering race against the image's own load event.
  const [decoded, setDecoded] = useState<string | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const state: 'loading' | 'ready' | 'error' =
    failed === blobUrl ? 'error' : decoded === blobUrl ? 'ready' : 'loading';

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen || !blobUrl) return null;

  const canShare = isMobile && typeof navigator !== 'undefined' && !!navigator.share;

  return (
    <div className="fixed inset-0 z-[200] animate-in fade-in duration-200" role="dialog" aria-modal="true">
      <div className="ui-scrim ui-scrim--solid" />

      <div
        className="relative w-full h-full flex flex-col"
        style={{
          paddingTop: 'calc(var(--safe-t) + 12px)',
          paddingBottom: 'calc(var(--safe-b) + 12px)',
          paddingLeft: 'calc(var(--safe-l) + 12px)',
          paddingRight: 'calc(var(--safe-r) + 12px)',
        }}
      >
        {/* ---- header ---- */}
        <div className="flex items-center justify-between gap-3 shrink-0 mb-3">
          <span className="ui-status" data-tone={state === 'error' ? 'bad' : state === 'ready' ? 'ok' : 'warn'}>
            {state === 'loading' && <><Loader2 size={11} className="ui-spin" /> Decoding render</>}
            {state === 'ready'   && <><Check size={11} /> Render complete</>}
            {state === 'error'   && <><AlertCircle size={11} /> Preview failed</>}
          </span>
          <button onClick={onClose} className="ui-btn ui-btn--quiet ui-btn--icon" aria-label="Close">
            <X size={18} />
          </button>
        </div>

        {/* ---- the render ---- */}
        <div className="flex-1 min-h-0 relative rounded-[16px] overflow-hidden border border-[color:var(--line-1)] bg-[color:var(--void)] flex items-center justify-center">
          {state === 'loading' && (
            <div className="absolute inset-0 ui-skeleton" aria-hidden="true" />
          )}

          {state === 'error' ? (
            <div className="ui-empty max-w-[320px] m-4" style={{ borderStyle: 'solid' }}>
              <div className="ui-empty__icon" style={{ color: 'var(--danger)' }}><AlertCircle size={16} /></div>
              <div className="min-w-0">
                <div className="ui-label ui-label--on">The image could not be shown</div>
                <div className="ui-caption mt-1">
                  The file was still produced — download it and open it locally, or export again
                  at a smaller size.
                </div>
              </div>
            </div>
          ) : (
            <img
              src={blobUrl}
              alt="Rendered collage"
              onLoad={() => setDecoded(blobUrl)}
              onError={() => setFailed(blobUrl)}
              className="relative max-w-full max-h-full object-contain"
              style={{ opacity: state === 'ready' ? 1 : 0, transition: 'opacity var(--dur-3) var(--ease)' }}
            />
          )}

          {isMobile && state === 'ready' && (
            <div
              className="absolute inset-x-0 bottom-0 py-2 text-center pointer-events-none ui-caption"
              style={{ background: 'linear-gradient(to top, rgba(3,4,5,.88), rgba(3,4,5,0))', color: 'var(--ink-2)' }}
            >
              Press and hold the image to save it to Photos
            </div>
          )}
        </div>

        {/* ---- actions: never fewer than two ways out ---- */}
        <div className="shrink-0 flex gap-2 mt-3">
          {canShare && (
            <button onClick={onShare} className="ui-btn ui-btn--primary ui-btn--tall flex-1">
              <Share size={18} /><span>Share</span>
            </button>
          )}
          <button
            onClick={onDownload}
            className={`ui-btn ui-btn--tall ${canShare ? '' : 'ui-btn--primary flex-1'}`}
            style={canShare ? { width: 128 } : undefined}
          >
            <Download size={18} /><span>Download</span>
          </button>
        </div>
      </div>
    </div>
  );
};
