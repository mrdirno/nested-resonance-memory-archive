// Original visual instruments. Author: Aldrin Payopay · GPL-3.0-only
import React, { useEffect, useId, useRef, useState } from 'react';
import { ART_TEMPLATES, ART_PALETTES, ART_SIZES, createArtLayer, createDefaultArtRecipe, normalizeArtRecipe, rollArtRecipe, type ArtRecipe, type ArtLayer, type ArtKind } from '../lib/artRack';
import { drawArt } from '../lib/artRackRenderer';
import './ArtRackRoom.css';

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
  const title=useId();const alive=useRef(true),generation=useRef(0),current=useRef(recipe);current.current=recipe;
  const [panel,setPanel]=useState<'templates'|'layers'>('templates');
  const [selected,setSelected]=useState(recipe.layers.at(-1)?.id || '');
  const [playing,setPlaying]=useState(()=>!matchMedia('(prefers-reduced-motion: reduce)').matches);
  const playingRef=useRef(playing);playingRef.current=playing;
  const [time,setTime]=useState(0),[pending,setPending]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
  const timeRef=useRef(0),past=useRef<ArtRecipe[]>([]),future=useRef<ArtRecipe[]>([]),[historyVersion,setHistoryVersion]=useState(0);
  const coalesce=useRef<{key:string;at:number}|null>(null);
  const layer=recipe.layers.find(l=>l.id===selected) || recipe.layers.at(-1);
  useEffect(()=>{alive.current=true;dialog.current?.showModal();return()=>{alive.current=false;generation.current++;};},[]);
  useEffect(()=>{if(!recipe.layers.some(l=>l.id===selected))setSelected(recipe.layers.at(-1)?.id||'');},[recipe.layers,selected]);
  useEffect(()=>{
    let frame=0,previous=0,lastUI=0;
    const paint=(stamp:number)=>{
      if(playingRef.current&&previous)timeRef.current=(timeRef.current+(stamp-previous)/1000)%recipe.duration;
      previous=stamp;
      const c=canvas.current,ctx=c?.getContext('2d');if(c&&ctx)drawArt(ctx,c.width,c.height,recipe,timeRef.current);
      if(stamp-lastUI>80){setTime(timeRef.current);lastUI=stamp;}
      if(playingRef.current)frame=requestAnimationFrame(paint);
    };
    frame=requestAnimationFrame(paint);return()=>cancelAnimationFrame(frame);
  },[recipe,playing]);
  useEffect(()=>{if(!playing){const c=canvas.current,ctx=c?.getContext('2d');if(c&&ctx)drawArt(ctx,c.width,c.height,recipe,time);}},[time,recipe,playing]);
  // Render edits at the paused playhead; elapsed time is never part of the recipe.
  useEffect(()=>{timeRef.current %= recipe.duration;setTime(timeRef.current);},[recipe.duration]);
  const seek=(value:number)=>{playingRef.current=false;timeRef.current=value;setTime(value);setPlaying(false);};
  const togglePlayback=()=>{playingRef.current=!playingRef.current;setPlaying(playingRef.current);};
  const commit=(next:ArtRecipe,key?:string)=>{
    generation.current++;setNotice('');setError('');
    const now=performance.now();
    if(!key||coalesce.current?.key!==key||now-coalesce.current.at>650){past.current=[...past.current.slice(-39),clone(current.current)];}
    coalesce.current=key?{key,at:now}:null;future.current=[];onChange(clone(next));setHistoryVersion(v=>v+1);
  };
  const edit=(patch:Partial<ArtLayer>,key?:string)=>{if(!layer)return;commit({...recipe,layers:recipe.layers.map(l=>l.id===layer.id?{...l,...patch}:l)},key);};
  const undo=(redo=false)=>{
    const from=redo?future:past,to=redo?past:future;if(!from.current.length)return;
    to.current=[...to.current.slice(-39),clone(current.current)];const next=from.current.pop()!;coalesce.current=null;generation.current++;
    onChange(next);setHistoryVersion(v=>v+1);setNotice(redo?'Change restored.':'Change undone.');
  };
  const roll=(id?:string)=>{
    const next=rollArtRecipe(recipe,freshSeed(),id);
    if(JSON.stringify(next)===JSON.stringify(recipe)){setNotice('Nothing to roll: unlock and enable a layer first.');return;}
    commit(next);setNotice(id?'Layer variation rolled.':'Unlocked, enabled layers rolled.');
  };
  const add=(kind:ArtKind)=>{
    if(recipe.layers.length>=8){setNotice('Eight layers are in this rack. Remove one to add another.');setPanel('layers');return;}
    const layer=createArtLayer(kind,freshSeed(),crypto.randomUUID());commit({...recipe,layers:[...recipe.layers,layer]});setSelected(layer.id);setPanel('layers');
  };
  const move=(id:string,offset:number)=>{const layers=[...recipe.layers],i=layers.findIndex(l=>l.id===id),j=i+offset;if(j<0||j>=layers.length)return;[layers[i],layers[j]]=[layers[j],layers[i]];commit({...recipe,layers});};
  const close=()=>{alive.current=false;generation.current++;dialog.current?.close();onClose();};
  const apply=async()=>{
    if(pending||busy)return;setPending(true);setError('');const gen=++generation.current,snapshot=clone(recipe);
    const isCurrent=()=>alive.current&&generation.current===gen;
    try{await onApply(snapshot,isCurrent);if(isCurrent())setNotice('Editable artwork applied. Close Art Room to arrange it or export a video.');}
    catch(err){if(isCurrent())setError(err instanceof Error?err.message:'Could not apply artwork.');}
    finally{if(alive.current)setPending(false);}
  };
  const download=()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(recipe,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='Persona500-art-recipe.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    setNotice('Recipe saved. It includes every layer and automation setting.');
  };
  const size=ART_SIZES[recipe.size];
  const parameter=(label:string,key:'opacity'|'scale'|'density'|'rotation'|'x'|'y',min:number,max:number,step:number)=>layer&&<label className="art-range">{label}<output>{Number(layer[key].toFixed(2))}</output><input aria-label={label} type="range" style={rangeStyle(layer[key],min,max)} min={min} max={max} step={step} value={layer[key]} onChange={e=>edit({[key]:Number(e.target.value)},`${layer.id}-${key}`)}/></label>;
  return <dialog ref={dialog} aria-labelledby={title} className="art-rack" data-testid="art-rack" onCancel={e=>{e.preventDefault();close();}} onKeyDown={e=>{
    if((e.metaKey||e.ctrlKey)&&['z','y','s','e','o'].includes(e.key.toLowerCase())){e.preventDefault();if(!pending&&!busy){if(e.key.toLowerCase()==='z')undo(e.shiftKey);if(e.key.toLowerCase()==='y')undo(true);if(e.key.toLowerCase()==='s')download();}}
    e.stopPropagation();
  }}>
    <header className="art-header"><div><span className="art-eyebrow">PERSONA500 / VISUAL INSTRUMENTS</span><h2 id={title}>Art Room</h2></div><button onClick={close} aria-label="Close Art Room">Close</button></header>
    <div className="art-workspace">
      <section className="art-stage" aria-label="Artwork preview">
        <div className="art-stage-label"><span>{size.label} · {size.width} × {size.height}</span><span>{recipe.layers.length} / 8 layers</span></div>
        <div className="art-canvas-wrap"><canvas ref={canvas} width={Math.round(880*Math.min(1,size.width/size.height))} height={Math.round(880*Math.min(1,size.height/size.width))} aria-label="Animated art preview"/></div>
        <div className="art-transport"><button onClick={togglePlayback} aria-label={playing?'Pause art preview':'Play art preview'}>{playing?'Pause':'Play'}</button><input aria-label="Art playhead" type="range" style={rangeStyle(time,0,recipe.duration)} min={0} max={recipe.duration} step={0.01} value={time} onChange={e=>seek(Number(e.target.value))}/><output>{time.toFixed(1)} / {recipe.duration}s</output></div>
      </section>
      <section className="art-desk" aria-label="Art controls">
        <div className="art-tabs" role="tablist" aria-label="Art workspace"><button role="tab" aria-selected={panel==='templates'} onClick={()=>setPanel('templates')}>Templates <span>08</span></button><button role="tab" aria-selected={panel==='layers'} onClick={()=>setPanel('layers')}>Layers <span>{recipe.layers.length}</span></button></div>
        <div className="art-scroll">
          <fieldset disabled={pending||busy}>
          {panel==='templates'?<div role="tabpanel" aria-label="Templates">
            <div className="art-section-head"><h3>Start with a shape.</h3><p>Add instruments to build a layered look. Each one has its own seed, palette and motion.</p></div>
            <div className="art-gallery">{ART_TEMPLATES.map(t=><button key={t.id} className="art-template" aria-label={`Add ${t.name}`} onClick={()=>add(t.id)}><Thumbnail kind={t.id}/><span><strong>{t.name}</strong><small>{t.description}</small></span><b aria-hidden="true">＋</b></button>)}</div>
          </div>:<div role="tabpanel" aria-label="Layers">
            <div className="art-section-head"><h3>Your layer stack.</h3><p>Top draws over bottom. Locks protect dice; you can still edit a locked layer.</p></div>
            <div className="art-stack">{[...recipe.layers].reverse().map((l,index)=><div key={l.id} className={`art-layer ${layer?.id===l.id?'is-selected':''}`} data-layer-id={l.id}>
              <div className="art-layer-main"><button aria-label={`Select ${nameOf(l.kind)} layer`} aria-pressed={layer?.id===l.id} className="art-layer-name" onClick={()=>setSelected(l.id)}><span>{String(recipe.layers.length-index).padStart(2,'0')}</span>{nameOf(l.kind)}</button><button aria-label={`${l.enabled?'Disable':'Enable'} ${nameOf(l.kind)} layer`} aria-pressed={l.enabled} onClick={()=>commit({...recipe,layers:recipe.layers.map(x=>x.id===l.id?{...x,enabled:!x.enabled}:x)})}>{l.enabled?'On':'Off'}</button><button aria-label={`Solo ${nameOf(l.kind)} layer`} aria-pressed={recipe.soloId===l.id} onClick={()=>commit({...recipe,soloId:recipe.soloId===l.id?null:l.id})}>S</button><button aria-label={`${l.locked?'Unlock':'Lock'} ${nameOf(l.kind)} dice`} aria-pressed={l.locked} onClick={()=>commit({...recipe,layers:recipe.layers.map(x=>x.id===l.id?{...x,locked:!x.locked}:x)})}>{l.locked?'Held':'Lock'}</button></div>
              {layer?.id===l.id&&<div className="art-layer-tools"><button onClick={()=>roll(l.id)} disabled={l.locked||!l.enabled}>Dice layer</button><button aria-label="Move layer up" onClick={()=>move(l.id,1)} disabled={index===0}>↑</button><button aria-label="Move layer down" onClick={()=>move(l.id,-1)} disabled={index===recipe.layers.length-1}>↓</button><button aria-label="Remove selected layer" onClick={()=>commit({...recipe,soloId:recipe.soloId===l.id?null:recipe.soloId,layers:recipe.layers.filter(x=>x.id!==l.id)})}>Remove</button></div>}
            </div>)}</div>
            {!layer&&<p className="art-empty">An empty canvas. Add a template to begin.</p>}
            {layer&&<div className="art-properties"><div className="art-section-head"><h3>{nameOf(layer.kind)}</h3><span className="art-seed">Seed {layer.seed}</span></div>
              <div className="art-pair"><label>Palette<select aria-label="Layer palette" value={layer.palette} onChange={e=>edit({palette:e.target.value as ArtLayer['palette']})}>{Object.values(ART_PALETTES).map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><label>Blend<select aria-label="Layer blend" value={layer.blend} onChange={e=>edit({blend:e.target.value as ArtLayer['blend']})}><option value="source-over">Normal</option><option value="screen">Screen</option><option value="multiply">Multiply</option><option value="lighter">Add light</option></select></label></div>
              {parameter('Opacity','opacity',0,1,.01)}{parameter('Scale','scale',.3,2,.01)}{parameter('Density','density',0,1,.01)}
              <details><summary>Position & rotation</summary>{parameter('Rotation','rotation',-180,180,1)}{parameter('Horizontal position','x',-.75,.75,.01)}{parameter('Vertical position','y',-.75,.75,.01)}</details>
              <div className="art-section-head"><h3>Automation</h3><p>One seamless envelope, repeated through the loop.</p></div>
              <label>Animate<select aria-label="Automation target" value={layer.automation.target} onChange={e=>edit({automation:{...layer.automation,target:e.target.value as ArtLayer['automation']['target']}})}>{['none','form','scale','rotation','opacity','drift'].map(t=><option key={t} value={t}>{t==='none'?'Static':t[0].toUpperCase()+t.slice(1)}</option>)}</select></label>
              {layer.automation.target!=='none'&&<><label className="art-range">Amount<output>{Math.round(layer.automation.amount*100)}%</output><input aria-label="Automation amount" type="range" style={rangeStyle(layer.automation.amount)} min={0} max={1} step={.01} value={layer.automation.amount} onChange={e=>edit({automation:{...layer.automation,amount:Number(e.target.value)}},`${layer.id}-amount`)}/></label><div className="art-pair"><label>Cycles per loop<select aria-label="Automation cycles" value={layer.automation.cycles} onChange={e=>edit({automation:{...layer.automation,cycles:Number(e.target.value)}})}>{[1,2,3,4].map(n=><option key={n}>{n}</option>)}</select></label><label>Phase<input aria-label="Automation phase" type="number" min={0} max={1} step={.05} value={layer.automation.phase} onChange={e=>{const n=Number(e.target.value);if(n>=0&&n<=1)edit({automation:{...layer.automation,phase:n}},`${layer.id}-phase`);}}/></label></div></>}
            </div>}
          </div>}
          <details className="art-project-settings"><summary>Canvas & recipe</summary><div className="art-pair"><label>Canvas<select aria-label="Art canvas size" value={recipe.size} onChange={e=>commit({...recipe,size:e.target.value as ArtRecipe['size']})}>{Object.entries(ART_SIZES).map(([id,s])=><option key={id} value={id}>{s.label}</option>)}</select></label><label>Loop duration<select aria-label="Art loop duration" value={recipe.duration} onChange={e=>{timeRef.current=0;setTime(0);commit({...recipe,duration:Number(e.target.value)});}}>{!Number.isInteger(recipe.duration)&&<option value={recipe.duration}>{recipe.duration} seconds</option>}{Array.from({length:23},(_,i)=>i+2).map(n=><option key={n} value={n}>{n} seconds</option>)}</select></label></div><div className="art-pair"><label>Background<input aria-label="Art background" type="color" value={recipe.background==='transparent'?'#101820':recipe.background} onChange={e=>commit({...recipe,background:e.target.value},'background')}/></label><button aria-pressed={recipe.background==='transparent'} onClick={()=>commit({...recipe,background:recipe.background==='transparent'?'#101820':'transparent'})}>Transparent</button></div><div className="art-button-row"><button onClick={download}>Save recipe</button><button onClick={()=>file.current?.click()}>Open recipe</button></div><input ref={file} type="file" accept=".json,application/json" aria-label="Open art recipe" hidden onChange={async e=>{const f=e.target.files?.[0];e.target.value='';if(!f)return;const gen=++generation.current;try{if(f.size>128*1024)throw Error('Choose a recipe smaller than 128 KiB.');const parsed=normalizeArtRecipe(JSON.parse(await f.text()));if(!alive.current||generation.current!==gen)return;commit(parsed);setPanel('layers');setNotice('Recipe opened. Apply it to keep it in the composition.');}catch(err){if(alive.current&&generation.current===gen)setError(err instanceof Error?err.message:'Invalid recipe.');}}}/></details>
          <button className="art-html-link" onClick={()=>{alive.current=false;generation.current++;onHtml();}}>Open an HTML instrument →</button>
          </fieldset>
        </div>
      </section>
    </div>
    <footer className="art-footer">
      {(error||notice)&&<p role={error?'alert':'status'}>{error||notice}</p>}
      <div className="art-footer-tools"><div className="art-history" data-history-version={historyVersion}><button aria-label="Undo art edit" onClick={()=>undo()} disabled={!past.current.length||pending||busy}>↶</button><button aria-label="Redo art edit" onClick={()=>undo(true)} disabled={!future.current.length||pending||busy}>↷</button></div><button onClick={()=>roll()} disabled={pending||busy}>Dice rack</button><label className="art-source-label"><span className="sr-only">Editing artwork</span><select aria-label="Editing artwork" value={sourceId||''} disabled={pending||busy} onChange={e=>{generation.current++;coalesce.current=null;past.current=[];future.current=[];setHistoryVersion(v=>v+1);onSource(e.target.value||null);}}><option value="">New artwork</option>{sources.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label><button className="art-apply" onClick={()=>void apply()} disabled={pending||busy}>{pending?'Applying…':sourceId?'Update artwork':'Add artwork'}</button></div>
    </footer>
  </dialog>;
}
