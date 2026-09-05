import React, { useEffect, useRef } from 'react';
import { Upload, Film } from 'lucide-react';
import { createDefaultArtRecipe } from '../lib/artRack';
import { drawArt } from '../lib/artRackRenderer';

export function StudioStart({ busy, onArt, onImport, onSample, artTriggerRef }: {
  busy: boolean; onArt: () => void; onImport: () => void; onSample: () => void;
  artTriggerRef: React.RefObject<HTMLButtonElement>;
}) {
  const preview = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = preview.current, context = canvas?.getContext('2d');
    if (canvas && context) drawArt(context, canvas.width, canvas.height, createDefaultArtRecipe(), 0);
  }, []);
  return <div className="studio-start">
    <h1>Start a new piece</h1>
    <button className="studio-start-art" ref={artTriggerRef} type="button" aria-label="Art Room" onClick={onArt} disabled={busy}>
      <canvas ref={preview} width={600} height={360} aria-hidden="true"/>
      <span><b>Art Room</b><small>Start with animated templates</small></span>
    </button>
    <div className="studio-start-import">
      <button type="button" aria-label="Load source images or video" onClick={onImport} disabled={busy}>
        <span className="studio-start-icons"><Upload size={25}/><Film size={25}/></span>
        <b>Add images or video</b><small>Choose your files, or drop them here</small>
      </button>
      <button type="button" className="studio-sample" onClick={onSample} disabled={busy}>{busy ? 'Making your sample…' : 'Try a lyric film'}</button>
    </div>
  </div>;
}
