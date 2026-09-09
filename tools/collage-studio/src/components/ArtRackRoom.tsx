// Original visual instruments. Author: Aldrin Payopay · GPL-3.0-only
import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import { ART_TEMPLATES, ART_PALETTES, ART_SIZES, createArtLayer, createDefaultArtRecipe, normalizeArtRecipe, rollArtRecipe, type ArtRecipe, type ArtLayer, type ArtKind } from '../lib/artRack';
import { drawArt } from '../lib/artRackRenderer';
import { artSelection, artHistoryEntry, ART_PARAMETER_UI, ART_INSTRUMENT_UI, type ArtSelection, type ArtHistoryEntry, type ArtDiceScope } from '../lib/artIntent';
import { previewArtRecipe, keepArtAudition, type ArtAudition } from '../lib/artAudition';
import { artDiceTargets, artInstrumentNote, artUndoNotice, ART_ROOM_GUIDE, ART_ROOM_SHORTCUTS, type ArtDiceTarget } from '../lib/artGuide';
import { HelpCircle, Redo2, Undo2, X } from 'lucide-react';
import './ArtRackRoom.css';

/**
 * C3724 — THE WISH (collage well, bug, about_tool=layout, anonymous):
 *   *"Missing undo — Missing info button in art room also prolly get rid of the
 *   which part drop down less clicks better."*
 * Before: Undo and Redo lived inside the collapsed "Canvas & recipe" disclosure
 * at the foot of the desk pane, below the fold on every phone, while the Keep
 * notice promised "Undo restores the previous stack"; the twelve instruments'
 * written descriptions were rendered nowhere; and the footer asked WHICH PART to
 * dice through a <select> before every roll. After: Undo · Redo · Help sit in
 * the top bar (icon-only 44px at phone widths, never under 44); the preview
 * sheet and the selected layer's heading carry the instrument's own sentence at
 * zero taps (the stage is fixed-height on phones — the C3722 gate measured the
 * line costing the artwork 24px there, so it does not live on the stage); Dice art and
 * Dice layer are two buttons, one tap each; Undo names the step it took back.
 * Judged by three independent lenses (9 / 9 / 8) before a line was written; the
 * pure half is src/lib/artGuide.ts with its invariant sweep.
 */
type Step = ArtHistoryEntry & { label?: string };

type Props = {
  recipe: ArtRecipe; onChange: (recipe: ArtRecipe) => void;
  sources: {id:string; name:string; recipe:ArtRecipe}[]; sourceId:string|null;
  onSource: (id:string|null) => void;
  onApply: (recipe:ArtRecipe, isCurrent:()=>boolean) => Promise<void>;
  onClose:()=>void; onHtml:()=>void; busy:boolean;
};
const clone = (recipe:ArtRecipe) => normalizeArtRecipe(recipe);
const rangeStyle=(value:number,min=0,max=1)=>({'--fill':`${Math.max(0,Math.min(100,(value-min)/(max-min)*100))}%`,'--slider-accent':'var(--art-accent)'} as React.CSSProperties);
const freshSeed = () => crypto.getRandomValues(new Uint32Array(1))[0];
const nameOf = (kind:ArtKind) => ART_TEMPLATES.find(t=>t.id===kind)?.name || kind;

function Thumbnail({kind}: {kind:ArtKind}) {
  const ref=useRef<HTMLCanvasElement>(null);
  useEffect(()=>{const ctx=ref.current?.getContext('2d');if(!ctx)return;
    const recipe=createDefaultArtRecipe();recipe.layers=[createArtLayer(kind,500,'thumbnail')];recipe.soloId=null;
    drawArt(ctx,240,150,recipe,0);
  },[kind]);
  return <canvas ref={ref} width={240} height={150} aria-hidden="true"/>;
}

export function ArtRackRoom({recipe,onChange,sources,sourceId,onSource,onApply,onClose,onHtml,busy}:Props) {
  const dialog=useRef<HTMLDialogElement>(null), canvas=useRef<HTMLCanvasElement>(null), file=useRef<HTMLInputElement>(null);
  const title=useId(),workspaceId=useId(),propertiesId=useId(),helpId=useId();const alive=useRef(true),generation=useRef(0),current=useRef(recipe);current.current=recipe;
  const help=useRef<HTMLDialogElement>(null),helpHeading=useRef<HTMLHeadingElement>(null),helpButton=useRef<HTMLButtonElement>(null),undoButton=useRef<HTMLButtonElement>(null),redoButton=useRef<HTMLButtonElement>(null);
  const [audition,setAudition]=useState<ArtAudition|null>(null),[alone,setAlone]=useState(false);
  const [family,setFamily]=useState('All');
  const gallery=useRef<HTMLDivElement>(null),returnToTemplate=useRef<ArtKind|null>(null);
  const previewRecipe=useMemo(()=>previewArtRecipe(recipe,audition,alone),[recipe,audition,alone]);
  const discardPreview=()=>{generation.current++;setAudition(null);setAlone(false);};
  const [panel,setPanel]=useState<'templates'|'layers'>('templates');
  const [properties,setProperties]=useState<'look'|'motion'>('look'),[focused,setFocused]=useState(false);
  const expandButton=useRef<HTMLButtonElement>(null),backButton=useRef<HTMLButtonElement>(null),focusChanged=useRef(false);
  const setPreviewFocus=(value:boolean)=>{focusChanged.current=true;setFocused(value);};
  useEffect(()=>{
    if(audition||!returnToTemplate.current)return;
    const target=focused?backButton.current:gallery.current?.querySelector<HTMLButtonElement>(`[data-template-kind="${returnToTemplate.current}"]`)||dialog.current?.querySelector<HTMLSelectElement>('[aria-label="Template family"]');
    target?.focus();returnToTemplate.current=null;
  },[audition,focused]);
  useEffect(()=>{if(focusChanged.current)(focused?backButton:expandButton).current?.focus();},[focused]);
  const [selected,setSelected]=useState(recipe.layers.at(-1)?.id || '');
  const [scope,setScope]=useState<ArtDiceScope>('composition');
  const selection=useRef<ArtSelection>({selectedId:selected,scope});selection.current={selectedId:selected,scope};
  const [playing,setPlaying]=useState(()=>!matchMedia('(prefers-reduced-motion: reduce)').matches);
  const playingRef=useRef(playing);playingRef.current=playing;
  const [time,setTime]=useState(0),[pending,setPending]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const timeRef=useRef(0),past=useRef<Step[]>([]),future=useRef<Step[]>([]),[historyVersion,setHistoryVersion]=useState(0);
  const coalesce=useRef<{key:string;at:number}|null>(null);
  const selectedLayer=recipe.layers.find(l=>l.id===selected);
  const layer=selectedLayer || recipe.layers.at(-1);
  const instrumentUI=layer?ART_INSTRUMENT_UI[layer.kind]:null;
  const chooseSelection=(next:ArtSelection)=>{selection.current=next;setSelected(next.selectedId);setScope(next.scope);coalesce.current=null;};
  useEffect(()=>{alive.current=true;dialog.current?.showModal();return()=>{alive.current=false;generation.current++;};},[]);
  useEffect(()=>{const next=artSelection(recipe,selection.current);if(next.selectedId!==selected||next.scope!==scope)chooseSelection(next);},[recipe.layers,selected,scope]);
  useEffect(()=>{
    let frame=0,previous=0,lastUI=0;
    const paint=(stamp:number)=>{
      if(playingRef.current&&previous)timeRef.current=(timeRef.current+(stamp-previous)/1000)%recipe.duration;
      previous=stamp;
      const c=canvas.current,ctx=c?.getContext('2d');if(c&&ctx)drawArt(ctx,c.width,c.height,previewRecipe,timeRef.current);
      if(stamp-lastUI>80){setTime(timeRef.current);lastUI=stamp;}
      if(playingRef.current)frame=requestAnimationFrame(paint);
    };
    frame=requestAnimationFrame(paint);return()=>cancelAnimationFrame(frame);
  },[previewRecipe,playing]);
  useEffect(()=>{if(!playing){const c=canvas.current,ctx=c?.getContext('2d');if(c&&ctx)drawArt(ctx,c.width,c.height,previewRecipe,time);}},[time,previewRecipe,playing]);
  // Render edits at the paused playhead; elapsed time is never part of the recipe.
  useEffect(()=>{timeRef.current %= recipe.duration;setTime(timeRef.current);},[recipe.duration]);
  const seek=(value:number)=>{playingRef.current=false;timeRef.current=value;setTime(value);setPlaying(false);};
  const togglePlayback=()=>{playingRef.current=!playingRef.current;setPlaying(playingRef.current);};
  const commit=(next:ArtRecipe,key?:string,nextSelection=selection.current,label?:string)=>{
    // Reject an invalid intent before changing history or retiring an in-flight apply.
    const entry=artHistoryEntry(next,nextSelection),previous=artHistoryEntry(current.current,selection.current);
    discardPreview();setNotice('');setError('');
    const now=performance.now();
    if(!key||coalesce.current?.key!==key||now-coalesce.current.at>650){past.current=[...past.current.slice(-39),{...previous,label}];}
    chooseSelection(entry.selection);coalesce.current=key?{key,at:now}:null;future.current=[];
    current.current=entry.recipe;onChange(entry.recipe);setHistoryVersion(v=>v+1);
  };
  const edit=(patch:Partial<ArtLayer>,key?:string,label?:string)=>{if(!layer)return;commit({...recipe,layers:recipe.layers.map(l=>l.id===layer.id?{...l,...patch}:l)},key,{selectedId:layer.id,scope:'layer'},label);};
  const undo=(redo=false)=>{
    if(audition)returnToTemplate.current=audition.layer.kind;
    discardPreview();const from=redo?future:past,to=redo?past:future;if(!from.current.length)return;
    const step=from.current.pop()!;
    to.current=[...to.current.slice(-39),{...artHistoryEntry(current.current,selection.current),label:step.label}];generation.current++;
    chooseSelection(step.selection);current.current=step.recipe;onChange(step.recipe);setHistoryVersion(v=>v+1);setError('');setNotice(artUndoNotice(step.label,redo));
    // A button that disables itself under the finger drops focus on <body>; hand it to its partner.
    const used=(redo?redoButton:undoButton).current,partner=(redo?undoButton:redoButton).current;
    requestAnimationFrame(()=>{if(!from.current.length&&used&&(document.activeElement===used||document.activeElement===document.body))(partner&&!partner.disabled?partner:helpButton.current)?.focus();});
  };
  // ONE TAP PER TARGET. The footer used to arm a scope in a <select>, then Dice
  // read it back; a sticky scope is how a roll meant for one layer hits the whole
  // composition. Now the button IS the target, and the stage readout follows it.
  const roll=(target:ArtDiceTarget)=>{
    if(audition){generation.current++;const rolled=rollArtRecipe({...recipe,layers:[audition.layer],soloId:null},freshSeed());setAudition({...audition,layer:rolled.layers[0]});setNotice('Preview variation rolled. Kept layers are unchanged.');return;}
    const chosen=target==='layer'?selectedLayer:undefined;
    if(target==='layer'&&!chosen){setNotice('Select a layer to dice.');return;}
    chooseSelection(chosen?{selectedId:chosen.id,scope:'layer'}:{selectedId:layer?.id||'',scope:'composition'});
    const next=rollArtRecipe(recipe,freshSeed(),chosen?.id);
    if(JSON.stringify(next)===JSON.stringify(recipe)){setNotice('Nothing to roll: unlock and enable a layer first.');return;}
    commit(next,undefined,selection.current,chosen?`Dice layer ${nameOf(chosen.kind)}`:'Dice art');setNotice(chosen?`${nameOf(chosen.kind)} variation rolled.`:'Unlocked, enabled layers in this art composition rolled.');
  };
  const closeHelp=()=>{if(help.current?.open)help.current.close();};
  const openHelp=()=>{if(!help.current||help.current.open)return;help.current.showModal();helpHeading.current?.focus();};
  // The feedback sheet is a fixed overlay, not a top-layer dialog, so it would
  // render BEHIND this modal room: the report path leaves the room first. The
  // draft artwork lives in Studio state and survives the trip.
  const report=()=>{closeHelp();close();(window as any).Feedback?.open('bug');};
  const previewTemplate=(kind:ArtKind)=>{
    generation.current++;setNotice('');setError('');
    if(audition?.layer.kind===kind)return;
    setAudition({layer:createArtLayer(kind,freshSeed(),crypto.randomUUID()),placement:'add',targetId:layer?.id||null});setAlone(false);
  };
  const editPreview=(patch:Partial<ArtLayer>)=>{if(audition){generation.current++;setAudition({...audition,layer:{...audition.layer,...patch}});}};
  const keepPreview=(start=false)=>{
    if(!audition||pending||busy)return;
    try{const next=keepArtAudition(recipe,audition,start);returnToTemplate.current=audition.layer.kind;const name=nameOf(audition.layer.kind);
      const label=start?`${name} as starting template`:audition.placement==='replace'?`Replace layer ${recipe.layers.findIndex(l=>l.id===audition.targetId)+1} with ${name}`:`Keep ${name} as layer ${recipe.layers.length+1}`;
      commit(next,undefined,{selectedId:audition.layer.id,scope:start?'composition':'layer'},label);setProperties('look');setPanel('templates');
      setNotice(start?`${name} is the starting template. Undo in the top bar restores the previous stack.`:`${name} kept. Preview another look to build on it.`);
    }catch(err){setError(err instanceof Error?err.message:'Could not keep preview.');}
  };
  const selectKept=(id:string)=>{discardPreview();chooseSelection({selectedId:id,scope:'layer'});setProperties('look');setPanel('layers');};
  const move=(id:string,offset:number)=>{const layers=[...recipe.layers],i=layers.findIndex(l=>l.id===id),j=i+offset;if(j<0||j>=layers.length)return;[layers[i],layers[j]]=[layers[j],layers[i]];commit({...recipe,layers},undefined,selection.current,`Move ${nameOf(layers[j].kind)} ${offset>0?'up':'down'}`);};
  const close=()=>{closeHelp();alive.current=false;generation.current++;dialog.current?.close();onClose();};
  const apply=async()=>{
    if(pending||busy||audition)return;setPending(true);setError('');const gen=++generation.current,snapshot=clone(recipe);
    const isCurrent=()=>alive.current&&generation.current===gen;
    try{await onApply(snapshot,isCurrent);if(isCurrent())setNotice('Editable artwork applied. Keep layering here, or close to arrange and export in Studio.');}
    catch(err){if(isCurrent())setError(err instanceof Error?err.message:'Could not apply artwork.');}
    finally{if(alive.current)setPending(false);}
  };
  const download=()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(recipe,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='Persona500-art-recipe.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    setNotice(audition?'Recipe saved with kept layers only. Keep the preview to include it.':'Recipe saved. It includes every layer and automation setting.');
  };
  const size=ART_SIZES[recipe.size];
  const parameter=(key:keyof typeof ART_PARAMETER_UI)=>{
    if(!layer)return null;const {label,min,max,step}=ART_PARAMETER_UI[key];
    return <label className="art-range" key={key}>{label}<output>{Number(layer[key].toFixed(2))}</output><input aria-label={label} aria-describedby={key==='density'?`${propertiesId}-density`:undefined} type="range" style={rangeStyle(layer[key],min,max)} min={min} max={max} step={step} value={layer[key]} onChange={e=>edit({[key]:Number(e.target.value)},`${layer.id}-${key}`,`${label} on ${nameOf(layer.kind)}`)}/>{key==='density'&&<small id={`${propertiesId}-density`} className="art-control-help">{instrumentUI?.densityHelp}</small>}</label>;
  };
  const targets=artDiceTargets(recipe,{selectedId:selected,scope},!!audition),note=artInstrumentNote(recipe,{selectedId:selected,scope},audition?.layer.kind??null);
  const layerNote=layer?artInstrumentNote(recipe,{selectedId:layer.id,scope:'layer'},null):null;
  return <dialog ref={dialog} aria-labelledby={title} className={`art-rack${focused?' is-preview-focus':''}${audition?' has-audition':''} is-${panel}`} data-testid="art-rack" onCancel={e=>{e.preventDefault();if(help.current?.open)closeHelp();else if(focused)setPreviewFocus(false);else close();}} onKeyDown={e=>{
    if((e.metaKey||e.ctrlKey)&&['z','y','s','e','o'].includes(e.key.toLowerCase())){e.preventDefault();if(!pending&&!busy){if(e.key.toLowerCase()==='z')undo(e.shiftKey);if(e.key.toLowerCase()==='y')undo(true);if(e.key.toLowerCase()==='s')download();}}
    e.stopPropagation();
  }}>
    <header className="art-header">
      <h2 id={title}>Art Room</h2>
      {focused&&<button ref={backButton} className="art-back" onClick={()=>setPreviewFocus(false)}>Back to editing</button>}
      {!focused&&<div className="art-header-tools" data-history-version={historyVersion}>
        <button ref={undoButton} aria-label="Undo art edit" title="Undo" onClick={()=>undo()} disabled={pending||busy||!past.current.length}><Undo2 size={18} aria-hidden="true"/><span>Undo</span></button>
        <button ref={redoButton} aria-label="Redo art edit" title="Redo" onClick={()=>undo(true)} disabled={pending||busy||!future.current.length}><Redo2 size={18} aria-hidden="true"/><span>Redo</span></button>
        <button ref={helpButton} aria-label="Help and report" title="Help" aria-haspopup="dialog" onClick={openHelp}><HelpCircle size={18} aria-hidden="true"/><span>Help</span></button>
      </div>}
      <button className="art-close" onClick={close} aria-label="Close Art Room" title="Close"><X size={20} aria-hidden="true"/><span>Close</span></button>
    </header>
    <div className="art-workspace">
      <section className="art-stage" aria-label="Artwork preview">
        <div className="art-stage-label"><span className="art-scope-context" data-testid="art-scope-context">{audition?`Preview only${recipe.soloId?' · solo paused':''} · ${nameOf(audition.layer.kind)}`:scope==='layer'?(selectedLayer?`Layer: ${nameOf(selectedLayer.kind)}${note?.state==='off'?' · off':note?.state==='held'?' · held':''}`:'Choose a layer'):'Art composition'}<small>{size.label}</small></span><button ref={expandButton} onClick={()=>setPreviewFocus(true)} aria-label="Expand art preview">Expand preview</button></div>
        <div className="art-canvas-wrap"><canvas ref={canvas} width={Math.round(880*Math.min(1,size.width/size.height))} height={Math.round(880*Math.min(1,size.height/size.width))} aria-label="Animated art preview"/></div>
        <div className="art-transport"><button onClick={togglePlayback} aria-label={playing?'Pause art preview':'Play art preview'}>{playing?'Pause':'Play'}</button><input aria-label="Art playhead" type="range" style={rangeStyle(time,0,recipe.duration)} min={0} max={recipe.duration} step={0.01} value={time} onChange={e=>seek(Number(e.target.value))}/><output>{time.toFixed(1)} / {recipe.duration}s</output></div>
      </section>
      <section className="art-desk" aria-label="Art controls" hidden={focused}>
        <div className="art-kept-strip" role="region" aria-label="Kept layers">{Array.from({length:Math.max(5,recipe.layers.length)},(_,i)=>{
          const kept=recipe.layers[i];return kept?<button key={kept.id} className={kept.enabled?'':'is-off'} aria-label={`Layer ${i+1}: ${nameOf(kept.kind)}`} aria-pressed={!audition&&layer?.id===kept.id} disabled={pending||busy} onClick={()=>selectKept(kept.id)}><b>{i+1}</b><span>{nameOf(kept.kind)}</span></button>:<button key={`empty-${i}`} aria-label={`Browse for layer ${i+1}`} disabled={pending||busy} onClick={()=>setPanel('templates')}><b>{i+1}</b><span>＋</span></button>;
        })}</div>
        <div className="art-tabs" role="tablist" aria-label="Art workspace">
          <button id={`${workspaceId}-templates`} role="tab" disabled={pending||busy} aria-selected={panel==='templates'} aria-controls={`${workspaceId}-panel`} onClick={()=>setPanel('templates')}>Templates</button>
          <button id={`${workspaceId}-layers`} role="tab" disabled={pending||busy} aria-selected={panel==='layers'} aria-controls={`${workspaceId}-panel`} onClick={()=>{discardPreview();setPanel('layers');if(layer)chooseSelection({selectedId:layer.id,scope:'layer'});}}>Layers <span>{recipe.layers.length}</span></button>
        </div>
        <div className="art-scroll">
          <fieldset disabled={pending||busy}>
          {panel==='templates'?<div id={`${workspaceId}-panel`} role="tabpanel" aria-label="Templates">
            <div className="art-section-head"><h3>Browse. Preview. Keep.</h3><p>Try a look over your layers, then keep the variation you like.</p></div>
            <div className="art-library-nav"><label><span className="sr-only">Template family</span><select aria-label="Template family" value={family} onChange={e=>{setFamily(e.target.value);gallery.current?.scrollTo({left:0});}}>{['All',...new Set(ART_TEMPLATES.map(t=>t.category))].map(c=><option key={c} value={c}>{c==='All'?'All visual instruments':c}</option>)}</select></label><button aria-label="Previous templates" onClick={()=>gallery.current?.scrollBy({left:-240,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}>←</button><button aria-label="Next templates" onClick={()=>gallery.current?.scrollBy({left:240,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}>→</button></div>
            <div className="art-gallery" ref={gallery}>{ART_TEMPLATES.filter(t=>family==='All'||t.category===family).map(t=><div key={t.id} className="art-template"><button className="art-template-use" data-template-kind={t.id} aria-label={`Preview ${t.name}`} aria-pressed={audition?.layer.kind===t.id} onClick={()=>previewTemplate(t.id)}><Thumbnail kind={t.id}/><span><strong>{t.name}</strong><small>{t.category}</small></span></button></div>)}</div>

          </div>:<div id={`${workspaceId}-panel`} role="tabpanel" aria-label="Layers">
            <div className="art-stack-heading"><p>Top layer appears in front.</p><button onClick={()=>setPanel('templates')}>Browse templates</button></div>
            <div className="art-stack">{[...recipe.layers].reverse().map((l,index)=><div key={l.id} className={`art-layer ${layer?.id===l.id?'is-selected':''}`} data-layer-id={l.id}>
              <div className="art-layer-main"><button aria-label={`Select ${nameOf(l.kind)} layer`} aria-pressed={layer?.id===l.id} className="art-layer-name" onClick={()=>chooseSelection({selectedId:l.id,scope:'layer'})}><span aria-hidden="true">{String(recipe.layers.length-index).padStart(2,'0')}</span>{nameOf(l.kind)}{l.locked&&<small>Held</small>}{recipe.soloId===l.id&&<small>Solo</small>}</button><button aria-label={`${l.enabled?'Disable':'Enable'} ${nameOf(l.kind)} layer`} aria-pressed={l.enabled} onClick={()=>commit({...recipe,layers:recipe.layers.map(x=>x.id===l.id?{...x,enabled:!x.enabled}:x)},undefined,selection.current,`${nameOf(l.kind)} ${l.enabled?'off':'on'}`)}>{l.enabled?'On':'Off'}</button></div>
            </div>)}</div>
            {!layer&&<p className="art-empty">An empty canvas. Add a template to begin.</p>}
            {layer&&<div className="art-properties">
              <div className="art-selected-heading"><h3>{nameOf(layer.kind)}</h3></div>
              {layerNote&&<p className="art-instrument-note" data-testid="art-instrument-note" data-state={layerNote.state}>{layerNote.text}</p>}
              <details className="art-layer-options" key={`options-${layer.id}`}><summary>Layer options</summary>
                <div className="art-layer-tools">
                  <button aria-label={`Solo ${nameOf(layer.kind)} layer`} aria-pressed={recipe.soloId===layer.id} onClick={()=>commit({...recipe,soloId:recipe.soloId===layer.id?null:layer.id},undefined,selection.current,recipe.soloId===layer.id?'Solo off':`Solo ${nameOf(layer.kind)}`)}>Solo layer</button>
                  <button aria-label={`${layer.locked?'Unlock':'Lock'} ${nameOf(layer.kind)} dice`} aria-pressed={layer.locked} onClick={()=>edit({locked:!layer.locked},undefined,`${layer.locked?'Unlock':'Lock'} dice on ${nameOf(layer.kind)}`)}>{layer.locked?'Unlock dice':'Lock dice'}</button>
                  <button aria-label="Move layer up" onClick={()=>move(layer.id,1)} disabled={recipe.layers.at(-1)?.id===layer.id}>Move up</button>
                  <button aria-label="Move layer down" onClick={()=>move(layer.id,-1)} disabled={recipe.layers[0]?.id===layer.id}>Move down</button>
                  <button aria-label="Remove selected layer" onClick={()=>commit({...recipe,soloId:recipe.soloId===layer.id?null:recipe.soloId,layers:recipe.layers.filter(x=>x.id!==layer.id)},undefined,selection.current,`Remove ${nameOf(layer.kind)}`)}>Remove layer</button>
                </div><p className="art-options-note">Locks protect dice. You can still edit a locked layer.</p><span className="art-seed">Seed {layer.seed}</span>
              </details>
              <div className="art-tabs art-property-tabs" role="tablist" aria-label="Selected layer controls">
                <button id={`${propertiesId}-look`} role="tab" aria-selected={properties==='look'} aria-controls={`${propertiesId}-panel`} onClick={()=>setProperties('look')}>Look</button>
                <button id={`${propertiesId}-motion`} role="tab" aria-selected={properties==='motion'} aria-controls={`${propertiesId}-panel`} onClick={()=>setProperties('motion')}>Motion</button>
              </div>
              {properties==='look'?<div id={`${propertiesId}-panel`} role="tabpanel" aria-labelledby={`${propertiesId}-look`} className="art-property-content">
                <label>Palette<select aria-label="Layer palette" value={layer.palette} onChange={e=>edit({palette:e.target.value as ArtLayer['palette']},undefined,`Palette on ${nameOf(layer.kind)}`)}>{Object.values(ART_PALETTES).map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
                {instrumentUI?.controls.look.map(parameter)}
                <details><summary>Position & blend</summary><label>Blend<select aria-label="Layer blend" value={layer.blend} onChange={e=>edit({blend:e.target.value as ArtLayer['blend']},undefined,`Blend on ${nameOf(layer.kind)}`)}><option value="source-over">Normal</option><option value="screen">Screen</option><option value="multiply">Multiply</option><option value="lighter">Add light</option></select></label>{instrumentUI?.controls.position.map(parameter)}</details>
              </div>:<div id={`${propertiesId}-panel`} role="tabpanel" aria-labelledby={`${propertiesId}-motion`} className="art-property-content">
                <label>Animate<select aria-label="Automation target" value={layer.automation.target} onChange={e=>edit({automation:{...layer.automation,target:e.target.value as ArtLayer['automation']['target']}},undefined,`Motion on ${nameOf(layer.kind)}`)}>{instrumentUI?.controls.motion.map(t=><option key={t} value={t}>{t==='none'?'Static':t[0].toUpperCase()+t.slice(1)}</option>)}</select></label>
                {layer.automation.target!=='none'?<><label className="art-range">Amount<output>{Math.round(layer.automation.amount*100)}%</output><input aria-label="Automation amount" type="range" style={rangeStyle(layer.automation.amount)} min={0} max={1} step={.01} value={layer.automation.amount} onChange={e=>edit({automation:{...layer.automation,amount:Number(e.target.value)}},`${layer.id}-amount`,`Motion amount on ${nameOf(layer.kind)}`)}/></label><details><summary>Motion timing</summary><div className="art-pair"><label>Cycles per loop<select aria-label="Automation cycles" value={layer.automation.cycles} onChange={e=>edit({automation:{...layer.automation,cycles:Number(e.target.value)}},undefined,`Motion cycles on ${nameOf(layer.kind)}`)}>{[1,2,3,4].map(n=><option key={n}>{n}</option>)}</select></label><label>Phase<input aria-label="Automation phase" type="number" min={0} max={1} step={.05} value={layer.automation.phase} onChange={e=>{const n=Number(e.target.value);if(n>=0&&n<=1)edit({automation:{...layer.automation,phase:n}},`${layer.id}-phase`,`Motion phase on ${nameOf(layer.kind)}`);}}/></label></div></details><p className="art-options-note">Motion repeats seamlessly through each loop.</p></>:<p className="art-options-note">This layer stays still. Choose a motion above to animate it.</p>}
              </div>}
            </div>}
          </div>}
          <details className="art-project-settings"><summary>Canvas & recipe</summary>
            <label>Editing artwork<select aria-label="Editing artwork" value={sourceId||''} onChange={e=>{discardPreview();coalesce.current=null;past.current=[];future.current=[];setHistoryVersion(v=>v+1);chooseSelection({selectedId:'',scope:'composition'});onSource(e.target.value||null);}}><option value="">New artwork</option>{sources.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
            <div className="art-pair"><label>Canvas<select aria-label="Art canvas size" value={recipe.size} onChange={e=>commit({...recipe,size:e.target.value as ArtRecipe['size']},undefined,selection.current,'Canvas size')}>{Object.entries(ART_SIZES).map(([id,s])=><option key={id} value={id}>{s.label}</option>)}</select></label><label>Loop duration<select aria-label="Art loop duration" value={recipe.duration} onChange={e=>{timeRef.current=0;setTime(0);commit({...recipe,duration:Number(e.target.value)},undefined,selection.current,'Loop duration');}}>{!Number.isInteger(recipe.duration)&&<option value={recipe.duration}>{recipe.duration} seconds</option>}{Array.from({length:23},(_,i)=>i+2).map(n=><option key={n} value={n}>{n} seconds</option>)}</select></label></div><div className="art-pair"><label>Background<input aria-label="Art background" type="color" value={recipe.background==='transparent'?'#101820':recipe.background} onChange={e=>commit({...recipe,background:e.target.value},'background',selection.current,'Background')}/></label><button aria-pressed={recipe.background==='transparent'} onClick={()=>commit({...recipe,background:recipe.background==='transparent'?'#101820':'transparent'},undefined,selection.current,'Background')}>Transparent</button></div><div className="art-button-row"><button onClick={download}>Save recipe</button><button onClick={()=>file.current?.click()}>Open recipe</button></div><input ref={file} type="file" accept=".json,application/json" aria-label="Open art recipe" hidden onChange={async e=>{const f=e.target.files?.[0];e.target.value='';if(!f)return;discardPreview();const gen=++generation.current;try{if(f.size>128*1024)throw Error('Choose a recipe smaller than 128 KiB.');const parsed=normalizeArtRecipe(JSON.parse(await f.text()));if(!alive.current||generation.current!==gen)return;commit(parsed,undefined,{selectedId:parsed.layers.at(-1)?.id||'',scope:'composition'},'Open recipe');setPanel('layers');setNotice('Recipe opened. Apply it to keep it in the composition.');}catch(err){if(alive.current&&generation.current===gen)setError(err instanceof Error?err.message:'Invalid recipe.');}}}/>
            <button className="art-html-link" onClick={()=>{alive.current=false;generation.current++;onHtml();}}>Open an HTML instrument →</button>
          </details>
          </fieldset>
        </div>
        {audition&&<fieldset className="art-audition" data-testid="art-audition" disabled={pending||busy}>
          <button className="art-dismiss" aria-label="Dismiss preview" onClick={()=>{returnToTemplate.current=audition.layer.kind;discardPreview();setNotice('Preview dismissed. Kept layers are unchanged.');}}>×</button>
          {note?.state==='preview'&&<p className="art-instrument-note art-audition-note" data-testid="art-instrument-note" data-state="preview">{note.text}</p>}
          <details className="art-preview-options"><summary><strong>{nameOf(audition.layer.kind)}</strong><span>Preview settings</span></summary>
            <div className="art-audition-placement"><label><span className="sr-only">Preview placement</span><select aria-label="Preview placement" value={audition.placement} onChange={e=>{generation.current++;setAudition({...audition,placement:e.target.value as ArtAudition['placement'],targetId:layer?.id||null});}}><option value="add">Overlay · layer {recipe.layers.length+1}</option><option value="replace" disabled={!layer}>Replace layer {recipe.layers.findIndex(l=>l.id===layer?.id)+1}</option></select></label><button aria-pressed={alone} onClick={()=>setAlone(!alone)}>Preview alone</button></div>
            <label>Preview opacity<input aria-label="Preview opacity" type="range" min={0} max={1} step={.01} style={rangeStyle(audition.layer.opacity)} value={audition.layer.opacity} onChange={e=>editPreview({opacity:Number(e.target.value)})}/></label><label>Preview blend<select aria-label="Preview blend" value={audition.layer.blend} onChange={e=>editPreview({blend:e.target.value as ArtLayer['blend']})}><option value="source-over">Normal</option><option value="screen">Screen</option><option value="multiply">Multiply</option><option value="lighter">Add light</option></select></label><button onClick={()=>keepPreview(true)}>Use as starting template</button>
            {recipe.soloId&&<p className="art-preview-note">Solo paused for this preview. Keep shows the combined layers; Undo restores solo.</p>}
          </details>
          {audition.placement==='add'&&recipe.layers.length>=8&&<p className="art-preview-note">All eight layers are filled. Open preview settings and choose Replace.</p>}

        </fieldset>}
      </section>
    </div>
    <footer className="art-footer">
      {(error||notice)&&<p role={error?'alert':'status'}>{error||notice}</p>}
      <div className="art-footer-tools"><div className="art-dice-controls">{audition?<button aria-label="Dice preview" onClick={()=>roll('art')} disabled={pending||busy}>Dice preview</button>:<><button className="art-dice-art" onClick={()=>roll('art')} disabled={pending||busy||!targets.art}>Dice art</button><button className="art-dice-layer" aria-label={targets.layerName?`Dice layer: ${targets.layerName}`:'Dice layer'} onClick={()=>roll('layer')} disabled={pending||busy||!targets.layer}>Dice layer</button></>}</div>{audition?<div className="art-promote"><button className="art-apply" aria-label={audition.placement==='replace'?`Replace layer ${recipe.layers.findIndex(l=>l.id===audition.targetId)+1}`:'Keep layer'} onClick={()=>keepPreview()} disabled={pending||busy||(audition.placement==='add'&&recipe.layers.length>=8)}>{audition.placement==='replace'?`Replace layer ${recipe.layers.findIndex(l=>l.id===audition.targetId)+1}`:`Keep layer ${recipe.layers.length+1}`}</button><button className="art-studio-pending" disabled>Keep preview first</button></div>:<button className="art-apply" onClick={()=>void apply()} disabled={pending||busy}>{pending?'Applying…':sourceId?'Update in Studio':'Use in Studio'}</button>}</div>
    </footer>
    <dialog ref={help} className="art-help" aria-labelledby={helpId} onCancel={e=>{e.preventDefault();e.stopPropagation();closeHelp();}} onClick={e=>{if(e.target===help.current)closeHelp();}}>
      <div className="art-help-card">
        <header><h3 id={helpId} ref={helpHeading} tabIndex={-1}>How the Art Room works</h3><button aria-label="Close help" onClick={closeHelp}><X size={20} aria-hidden="true"/></button></header>
        <ol>{ART_ROOM_GUIDE.map(line=><li key={line}>{line}</li>)}</ol>
        <details className="art-help-keys"><summary>Keyboard</summary><dl>{ART_ROOM_SHORTCUTS.map(([keys,action])=><React.Fragment key={action}><dt>{keys}</dt><dd>{action}</dd></React.Fragment>)}</dl></details>
        <button className="art-help-report" onClick={report}>Something wrong? Report it<small>Leaves the room and opens the feedback sheet. Your artwork stays.</small></button>
        {/* CREDIT ON THE PAGE, not only in av/credits.json. Anonymous. */}
        <p className="art-help-credit">Undo in the top bar, this card and one-tap dice were wished for by an anonymous Collage user.</p>
      </div>
    </dialog>
  </dialog>;
}
