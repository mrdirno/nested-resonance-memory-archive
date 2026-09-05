// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only, as the host project.
import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import { ArtRoomSession, MAX_ART_HTML_BYTES, validateArtPng, type ArtCanvas } from '../lib/artRoom';
import { ART_ROOM_STARTER_HTML, ART_ROOM_STARTER_NAME } from '../lib/artRoomStarter';

export interface ArtRoomProps {
  open: boolean;
  onClose: () => void;
  onTemplates?: () => void;
  onImport: (file: File, isCurrent: () => boolean) => Promise<void>;
  busy?: boolean;
}
const control = 'min-h-[44px] rounded-lg border border-white/20 bg-[#1c272c] px-3 py-2 text-sm text-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300 disabled:cursor-not-allowed disabled:opacity-40';
const button = `${control} hover:bg-white/10`;

export const ArtRoom: React.FC<ArtRoomProps> = ({open,onClose,onImport,busy=false,onTemplates}) => {
  const titleId = useId(), dialogRef = useRef<HTMLDialogElement>(null), mountRef = useRef<HTMLDivElement>(null), fileRef = useRef<HTMLInputElement>(null);
  const sessionRef = useRef<ArtRoomSession | null>(null), generationRef = useRef(0), readRef = useRef(0), capturingRef = useRef(false), refreshingRef = useRef(false);
  const openRef = useRef(open), busyRef = useRef(busy), onImportRef = useRef(onImport), onCloseRef = useRef(onClose);
  openRef.current=open;busyRef.current=busy;onImportRef.current=onImport;onCloseRef.current=onClose;
  const [name,setName]=useState(ART_ROOM_STARTER_NAME),[ready,setReady]=useState(false),[canvases,setCanvases]=useState<ArtCanvas[]>([]),[selected,setSelected]=useState('');
  const [pending,setPending]=useState(false),[reading,setReading]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');

  const retire = useCallback(() => {
    generationRef.current++;readRef.current++;capturingRef.current=false;refreshingRef.current=false;
    sessionRef.current?.dispose();sessionRef.current=null;
  },[]);

  const refresh = useCallback(async (session = sessionRef.current) => {
    if (!session?.connected || refreshingRef.current) return;
    refreshingRef.current=true;
    try {
      const rows=await session.list();
      if (!openRef.current || sessionRef.current!==session || !session.active) return;
      setCanvases(rows);setSelected(previous=>rows.some(row=>row.id===previous)?previous:(rows[0]?.id||''));
    } catch (err) {
      if (openRef.current && sessionRef.current===session) setError(err instanceof Error?err.message:'Could not read the instrument canvases.');
    } finally { if(sessionRef.current===session)refreshingRef.current=false; }
  },[]);

  const launch = useCallback((source:string,filename:string) => {
    if(!mountRef.current)return;
    retire();setReady(false);setCanvases([]);setSelected('');setPending(false);setReading(false);setError('');setNotice('');setName(filename);
    try {
      const session=new ArtRoomSession(mountRef.current,source,filename,()=>{
        if(!openRef.current||sessionRef.current!==session)return;
        setReady(true);void refresh(session);
      },message=>{
        if(!openRef.current||sessionRef.current!==session)return;
        generationRef.current++;setReady(false);setCanvases([]);setError(message);setPending(false);capturingRef.current=false;
      });
      sessionRef.current=session;
    } catch(err){setError(err instanceof Error?err.message:'This instrument could not open.');}
  },[retire,refresh]);

  useEffect(()=>{
    const dialog=dialogRef.current;
    if(open){if(dialog&&!dialog.open)dialog.showModal();launch(ART_ROOM_STARTER_HTML,ART_ROOM_STARTER_NAME);}
    else {retire();if(dialog?.open)dialog.close();}
    return ()=>retire();
  },[open,launch,retire]);

  useEffect(()=>{
    if(!open||!ready)return;
    const timer=setInterval(()=>{if(!capturingRef.current)void refresh();},1800);
    return()=>clearInterval(timer);
  },[open,ready,refresh]);

  const close=()=>{openRef.current=false;retire();dialogRef.current?.close();onCloseRef.current();};
  const importArtwork=async()=>{
    const session=sessionRef.current;
    if(!session?.connected||!selected||capturingRef.current||busyRef.current)return;
    const generation=++generationRef.current;
    const isCurrent=()=>openRef.current&&generationRef.current===generation&&sessionRef.current===session&&session.active;
    capturingRef.current=true;setPending(true);setError('');setNotice('');
    try {
      const result=await session.capture(selected);
      if(!isCurrent())return;
      const dimensions=await validateArtPng(result.blob);
      if(!isCurrent())return;
      if(dimensions.width!==result.width||dimensions.height!==result.height)throw new Error('The canvas changed size during capture. Try again.');
      if(busyRef.current)throw new Error('Finish the current GenArt operation, then capture this artwork again.');
      await onImportRef.current(new File([result.blob],result.name,{type:'image/png'}),isCurrent);
      if(isCurrent())setNotice(`Added ${dimensions.width} × ${dimensions.height} pixels to your composition. Close Art Room to arrange them.`);
    } catch(err){if(isCurrent())setError(err instanceof Error?err.message:'Could not add this artwork.');}
    finally{if(isCurrent()){capturingRef.current=false;setPending(false);}}
  };

  return <dialog ref={dialogRef} aria-labelledby={titleId} onCancel={event=>{event.preventDefault();close();}} onKeyDown={event=>{
    // Safari's native undo can reach the page behind a top-layer dialog even
    // when propagation stops. These are host-editor shortcuts, not room edits.
    if((event.metaKey||event.ctrlKey)&&['z','y','s','e','o'].includes(event.key.toLowerCase()))event.preventDefault();
    event.stopPropagation();
  }}
    className="m-auto h-[min(94dvh,900px)] max-h-[94dvh] w-[min(96vw,1000px)] max-w-none overflow-hidden rounded-2xl border border-white/20 bg-[#111a1e] p-0 text-gray-200 shadow-2xl backdrop:bg-black/80" data-testid="art-room">
    <div className="flex h-full min-h-0 flex-col">
      <header className="flex shrink-0 items-center justify-between gap-3 border-b border-white/10 px-4 py-3">
        <div><h2 id={titleId} className="text-lg font-medium text-white">Art Room</h2><p className="text-xs text-gray-400">Play an instrument. Keep a moment.</p></div>
        <div className="flex gap-2">{onTemplates&&<button type="button" className={button} onClick={()=>{openRef.current=false;retire();dialogRef.current?.close();onTemplates();}}>Templates</button>}<button type="button" className={button} onClick={close} aria-label="Close Art Room">Close</button></div>
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain p-3 sm:p-4">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <button type="button" className={button} disabled={busy||reading} onClick={()=>launch(ART_ROOM_STARTER_HTML,ART_ROOM_STARTER_NAME)}>Original instrument</button>
          <button type="button" className={button} disabled={busy||reading} onClick={()=>fileRef.current?.click()}>{reading?'Opening HTML…':'Open HTML instrument'}</button>
          <span className="min-w-0 break-all text-xs text-gray-400">{name}</span>
          <input ref={fileRef} type="file" className="hidden" accept=".html,.htm,text/html" aria-label="Open local art HTML" onChange={async event=>{
            const file=event.currentTarget.files?.[0];event.currentTarget.value='';if(!file)return;
            const read=++readRef.current;setReading(true);setError('');
            try {
              if(!/\.html?$/i.test(file.name))throw new Error('Choose an .html or .htm instrument file.');
              if(file.size<1||file.size>MAX_ART_HTML_BYTES)throw new Error('Choose a nonempty HTML instrument smaller than 8 MiB.');
              const source=await file.text();
              if(!openRef.current||readRef.current!==read)return;
              if(busyRef.current)throw new Error('Finish the current GenArt operation before opening another instrument.');
              launch(source,file.name);
            }catch(err){if(openRef.current&&readRef.current===read)setError(err instanceof Error?err.message:'Could not read this instrument.');}
            finally{if(openRef.current&&readRef.current===read)setReading(false);}
          }}/>
        </div>
        <p className="mb-3 text-xs leading-relaxed text-gray-400">Open self-contained HTML you own or trust, up to 8 MiB. Instruments run in a separate sandbox; external assets are disabled. This player does not make arbitrary code trustworthy.</p>
        <div ref={mountRef} className="h-[min(62dvh,580px)] min-h-[340px] overflow-hidden rounded-xl border border-white/15 bg-[#101619]" data-testid="art-room-player"/>
        <details className="mt-3 rounded-lg border border-white/10 text-xs text-gray-400">
          <summary className="min-h-[44px] cursor-pointer px-3 py-3 text-gray-300">Bring Bifurcata and other art instruments</summary>
          <div className="space-y-2 px-3 pb-3 leading-relaxed">
            <p>A local, self-contained Bifurcata HTML file can run here. Use Show artwork to bring its first world into view and start drawing. Wait for the whole world, then choose its canvas below. Other HTML instruments need a visible, readable canvas.</p>
            <p>For the public version, <a href="https://persona500.com/bifurcata" target="_blank" rel="noopener noreferrer" className="inline-flex min-h-[44px] items-center underline text-amber-200">open Bifurcata</a>, export a PNG, and add that file in GenArt. Its website does not currently connect directly to this room.</p>
            <p>Capture keeps a still at the canvas’s current resolution. Rendered pixels travel with your saved composition; the editable HTML, seed controls and live instrument do not. SVG-only or DOM-only artwork needs its own image export.</p>
          </div>
        </details>
      </div>
      <footer className="shrink-0 space-y-2 border-t border-white/10 bg-[#111a1e] px-3 py-3 sm:px-4">
        {error&&<p role="alert" className="rounded-lg bg-red-950/60 px-3 py-2 text-xs text-red-200">{error}</p>}
        {notice&&<p role="status" className="text-xs text-amber-100">{notice}</p>}
        <div className="flex flex-wrap items-end gap-2">
          <label className="min-w-[150px] flex-1 text-xs text-gray-400">Artwork canvas<select aria-label="Artwork canvas" value={selected} disabled={!canvases.length||pending} onChange={e=>setSelected(e.target.value)} className={`${control} mt-1 w-full`} style={{height:44,appearance:'none',WebkitAppearance:'none'}}>
            {!canvases.length&&<option value="">{ready?'Waiting for a finished canvas…':'Connecting instrument…'}</option>}
            {canvases.map(canvas=><option key={canvas.id} value={canvas.id}>{canvas.label} · {canvas.width} × {canvas.height}</option>)}
          </select></label>
          <button type="button" className={button} disabled={!ready||pending||reading} onClick={async()=>{
            const session=sessionRef.current;if(!session?.connected)return;
            setError('');mountRef.current?.scrollIntoView({block:'start',behavior:'auto'});
            try{await session.showArtwork(selected||undefined);if(openRef.current&&sessionRef.current===session)await refresh(session);}
            catch(err){if(openRef.current&&sessionRef.current===session)setError(err instanceof Error?err.message:'Could not bring the artwork into view.');}
          }}>Show artwork</button>
          <button type="button" className={`${button} border-amber-300/40 bg-amber-300/15 text-amber-100`} disabled={!ready||!selected||pending||busy||reading} onClick={()=>void importArtwork()}>{pending?'Adding artwork…':'Use this artwork'}</button>
        </div>
        <p className="text-[11px] leading-relaxed text-gray-400">Still PNG · current canvas resolution · up to 4096 pixels per side and 16 MP. {busy?'GenArt is busy; capture will be available when it finishes.':''}</p>
      </footer>
    </div>
  </dialog>;
};
