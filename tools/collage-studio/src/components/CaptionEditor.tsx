// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
import React, { useRef, useState } from 'react';
import { LyricImportHelp } from './LyricImportHelp';
import { EMPTY_CAPTION_TRACK, cleanCaptionText, draftCaptions, normalizeCaptionTrack, parseCaptions, serializeSrt, serializeVtt, type CaptionCue, type CaptionTrack } from '../lib/captions';

export interface CaptionEditorProps {
  track?: CaptionTrack | null;
  onChange: (track: CaptionTrack) => void;
  take: number;
  getTime: () => number;
  onSeek: (time: number) => void | Promise<void>;
  disabled?: boolean;
  defaultOpen?: boolean;
}
const control = 'min-h-[44px] rounded-lg border border-white/15 bg-black/25 px-3 py-2 text-sm text-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300 disabled:opacity-40';
const button = `${control} hover:bg-white/10 disabled:cursor-not-allowed`;

export const CaptionEditor: React.FC<CaptionEditorProps> = ({ track, onChange, take, getTime, onSeek, disabled = false, defaultOpen = false }) => {
  const current = track ?? EMPTY_CAPTION_TRACK;
  const [lyrics, setLyrics] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [editing, setEditing] = useState<CaptionCue | null>(null);
  const [start, setStart] = useState('0');
  const [end, setEnd] = useState('1');
  const [text, setText] = useState('');
  const [undo, setUndo] = useState<CaptionTrack | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const currentRef = useRef(current);
  currentRef.current = current;
  const disabledRef = useRef(disabled);
  disabledRef.current = disabled;

  const attempt = (action: () => void) => {
    setError(''); setNotice('');
    try { action(); } catch (e) { setError(e instanceof Error ? e.message : 'Could not update captions. Your existing cues are unchanged.'); }
  };
  const commit = (next: CaptionTrack) => { const valid = normalizeCaptionTrack(next); setUndo(normalizeCaptionTrack(current)); onChange(valid); };
  const edit = (cue: CaptionCue) => { setEditing(cue); setText(cue.text); setStart(String(cue.start)); setEnd(String(cue.end)); setError(''); setNotice(''); };
  const preview = (at: number) => {
    setError('');
    try { void Promise.resolve(onSeek(at)).catch(() => setError('Preview could not seek to this cue. Try again.')); }
    catch { setError('Preview could not seek to this cue. Try again.'); }
  };
  const download = (kind: 'srt' | 'vtt') => attempt(() => {
    const blob = new Blob([kind === 'srt' ? serializeSrt(current) : serializeVtt(current)], { type: kind === 'vtt' ? 'text/vtt;charset=utf-8' : 'application/x-subrip;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a'); link.href = url; link.download = `collage-captions.${kind}`;
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  const outside = current.cues.filter((cue) => cue.end > take).length;

  return <details open={defaultOpen || undefined} className="w-full basis-full min-w-0 rounded-xl border border-white/10 bg-black/15 text-gray-200" data-testid="caption-editor" style={{ maxHeight: 'var(--dock-max)', overflowY: 'auto' }}>
    <summary className="min-h-[44px] cursor-pointer px-3 py-3 text-sm font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
      Lyrics &amp; captions <span className="ml-2 text-gray-400 font-normal">{current.cues.length ? `${current.cues.length} timed cues` : 'Give the take a voice'}</span>
    </summary>
    <fieldset disabled={disabled} className="min-w-0 space-y-4 border-t border-white/10 p-3">
      <p className="text-xs leading-relaxed text-gray-400">Paste your lyrics or import plain SRT / VTT subtitles. Captions appear in the preview and recorded video.</p>
      <p className="text-xs leading-relaxed text-gray-400">A timed cue takes the title’s place while it is on screen; the title returns in the gaps. Long cues use smaller type to keep every word.</p>
      {error && <p role="alert" className="rounded-lg bg-red-950/60 p-3 text-sm text-red-200">{error}</p>}
      {notice && <p role="status" className="text-sm text-amber-200">{notice}</p>}
      {outside > 0 && <p role="status" className="text-xs text-amber-200">{outside} cue{outside === 1 ? ' extends' : 's extend'} beyond this {take.toFixed(2)}s take. Those parts will not appear in the video. Adjust the cue times or lengthen the take.</p>}
      <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="block text-xs text-gray-300">Position<select style={{ height: 44, appearance: 'none', WebkitAppearance: 'none' }} value={current.place} onChange={(e) => attempt(() => commit({ ...current, place: e.target.value as CaptionTrack['place'] }))} className={`${control} mt-1 w-full`}><option value="bc">Bottom center</option><option value="tc">Top center</option></select></label>
        <label className="block text-xs text-gray-300">Font size<select style={{ height: 44, appearance: 'none', WebkitAppearance: 'none' }} value={current.size} onChange={(e) => attempt(() => commit({ ...current, size: e.target.value as CaptionTrack['size'] }))} className={`${control} mt-1 w-full`}><option value="sm">Small</option><option value="md">Medium</option><option value="lg">Large</option></select></label>
      </div>
      <LyricImportHelp />
      <label className="block text-xs text-gray-300">Lyrics, one line per cue<textarea value={lyrics} onChange={(e) => setLyrics(e.target.value)} rows={3} placeholder="Paste the lines you want in this take" className={`${control} mt-1 w-full resize-y`} /></label>
      <div className="flex flex-wrap gap-2">
        <button type="button" className={button} onClick={() => attempt(() => { commit({ ...current, cues: draftCaptions(lyrics, take) }); setEditing(null); setNotice('Evenly spaced draft created. Preview each cue and adjust the timing to your song.'); })}>{current.cues.length ? 'Replace with evenly spaced draft' : 'Create evenly spaced draft'}</button>
        <button type="button" className={button} onClick={() => fileRef.current?.click()}>{current.cues.length ? 'Replace from SRT / VTT' : 'Import SRT / VTT'}</button>
        <input ref={fileRef} type="file" accept=".srt,.vtt,text/vtt,application/x-subrip" className="hidden" aria-label="Import caption file" onChange={async (e) => {
          const file = e.currentTarget.files?.[0]; e.currentTarget.value = ''; if (!file) return;
          setError(''); setNotice('');
          const before = currentRef.current;
          try {
            if (file.size > 256_000) throw new Error('Choose a subtitle file smaller than 256 KB.');
            const extension = file.name.split('.').pop()?.toLowerCase();
            if (extension !== 'srt' && extension !== 'vtt') throw new Error('Choose an .srt or .vtt subtitle file.');
            const cues = parseCaptions(await file.text(), extension);
            if (disabledRef.current) throw new Error('Finish recording, then import your captions again.');
            if (currentRef.current !== before) throw new Error('The track changed while this file was loading. Import again to replace the current cues.');
            commit({ ...before, cues }); setEditing(null); setNotice(`Imported ${cues.length} timed captions.`);
          } catch (err) { setError(err instanceof Error ? err.message : 'Could not read this subtitle file.'); }
        }} />
      </div>
      <p className="text-xs leading-relaxed text-gray-400">Even spacing is a starting point you can edit. It does not transcribe or automatically sync your song. Imports accept plain text; styling and karaoke tags need a plain-text export first.</p>
      {current.cues.length > 0 && <ol className="space-y-1" aria-label="Timed caption cues">
        {current.cues.map((cue, i) => <li key={cue.id} className="flex min-w-0 items-center gap-2 rounded-lg bg-white/[0.03] p-1">
          <button type="button" className={`${button} min-w-0 flex-1 text-left`} onClick={() => edit(cue)} aria-label={`Edit caption ${i + 1}: ${cue.text}`} aria-pressed={editing?.id === cue.id}><span className="block text-xs tabular-nums text-amber-200">{cue.start.toFixed(2)} – {cue.end.toFixed(2)}s</span><span className="block truncate">{cue.text}</span></button>
          <button type="button" className={button} aria-label={`Preview caption ${i + 1}`} onClick={() => preview(cue.start)}>Preview</button>
        </li>)}
      </ol>}
      <button type="button" className={button} disabled={current.cues.length >= 200} onClick={() => attempt(() => {
        const position = getTime();
        const at = Math.max(0, Math.min(3599.95, Number.isFinite(position) ? position : 0));
        const after = current.cues.find((cue) => cue.end > at);
        const from = after && after.start <= at ? after.end : at;
        const next = current.cues.find((cue) => cue.start >= from);
        const until = Math.min(from + 2, next?.start ?? Math.max(take, from + 2), 3600);
        if (until - from < 0.05) throw new Error('No room for a cue here. Seek to a gap or adjust existing cue times.');
        let id = `caption-${Date.now()}`; while (current.cues.some((cue) => cue.id === id)) id += '-new';
        edit({ id, start: Math.round(from * 1000) / 1000, end: Math.round(until * 1000) / 1000, text: '' });
      })}>Add cue at playhead</button>
      {editing && <div className="space-y-3 rounded-lg border border-amber-300/25 p-3" data-testid="caption-cue-form">
        <label className="block text-xs text-gray-300">Caption text<textarea aria-label="Caption text" value={text} onChange={(e) => setText(e.target.value)} rows={2} className={`${control} mt-1 w-full resize-y`} /><span className={text.length > 240 ? 'text-red-300' : 'text-gray-400'}>{text.length} / 240 characters</span></label>
        <div className="grid min-w-0 grid-cols-2 gap-2">
          <label className="text-xs">Start (seconds)<input type="number" inputMode="decimal" min="0" max="3600" step="0.01" value={start} onChange={(e) => setStart(e.target.value)} className={`${control} mt-1 w-full min-w-0`} /></label>
          <label className="text-xs">End (seconds)<input type="number" inputMode="decimal" min="0" max="3600" step="0.01" value={end} onChange={(e) => setEnd(e.target.value)} className={`${control} mt-1 w-full min-w-0`} /></label>
        </div>
        <div className="flex flex-wrap gap-2">
          <button type="button" className={button} onClick={() => attempt(() => { const at = getTime(); if (!Number.isFinite(at) || at < 0 || at > 3600) throw new Error('The playhead has no valid time yet.'); setStart(String(Math.round(at * 1000) / 1000)); })}>Stamp start at playhead</button>
          <button type="button" className={`${button} border-amber-300/40 text-amber-100`} onClick={() => attempt(() => {
            if (!start.trim() || !end.trim()) throw new Error('Enter both a start and an end time.');
            const cue = { ...editing, text: cleanCaptionText(text), start: Number(start), end: Number(end) };
            const cues = current.cues.filter((item) => item.id !== cue.id); cues.push(cue);
            commit({ ...current, cues }); setEditing(null); setNotice('Cue saved.');
          })}>Save cue</button>
          {current.cues.some((cue) => cue.id === editing.id) && <button type="button" className={`${button} text-red-200`} onClick={() => attempt(() => { commit({ ...current, cues: current.cues.filter((cue) => cue.id !== editing.id) }); setEditing(null); })}>Delete cue</button>}
          <button type="button" className={button} onClick={() => { setEditing(null); setError(''); }}>Cancel edit</button>
        </div>
      </div>}
      <div className="flex flex-wrap gap-2 border-t border-white/10 pt-3">
        <button type="button" className={button} disabled={!current.cues.length} onClick={() => download('srt')}>Export SRT</button>
        <button type="button" className={button} disabled={!current.cues.length} onClick={() => download('vtt')}>Export VTT</button>
        <button type="button" className={button} disabled={!current.cues.length} onClick={() => attempt(() => { commit({ ...current, cues: [] }); setEditing(null); setNotice('Captions cleared. Undo restores the previous track.'); })}>Clear captions</button>
        <button type="button" className={button} disabled={!undo} onClick={() => attempt(() => { if (undo) { onChange(normalizeCaptionTrack(undo)); setUndo(null); setEditing(null); setNotice('Previous caption track restored.'); } })}>Undo last track change</button>
      </div>
    </fieldset>
  </details>;
};
