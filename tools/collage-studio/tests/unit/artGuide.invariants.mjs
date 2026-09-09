// Author: Aldrin Payopay · GPL-3.0-only
// C3724: the REAL artGuide module, transpiled, swept across kinds × seeds × lock/enable masks.
import assert from 'node:assert/strict';
import esbuild from 'esbuild';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const temp=mkdtempSync(join(tmpdir(),'art-guide-'));
try {
 const root=join(dirname(fileURLToPath(import.meta.url)),'../..');
 const modules={};
 for(const name of ['artGuide','artRack','artIntent']){await esbuild.build({entryPoints:[join(root,`src/lib/${name}.ts`)],outfile:join(temp,`${name}.mjs`),bundle:true,platform:'neutral',format:'esm',logLevel:'silent'});modules[name]=await import(pathToFileURL(join(temp,`${name}.mjs`)).href);}
 const {artDiceTargets,artInstrumentNote,artTemplateName,artUndoNotice,ART_ROOM_GUIDE,ART_ROOM_SHORTCUTS}=modules.artGuide;
 const {createDefaultArtRecipe,createArtLayer,ART_TEMPLATES}=modules.artRack;
 const {artSelection}=modules.artIntent;
 let checks=0;const ok=(cond,msg)=>{assert.ok(cond,msg);checks++;};

 // THE GUIDE: four lines, each a sentence in the room's own vocabulary.
 ok(ART_ROOM_GUIDE.length===4,'the help card is four lines, not a manual');
 for(const line of ART_ROOM_GUIDE){ok(typeof line==='string'&&line.length>=20&&line.length<=110&&line.endsWith('.'),`guide line is a short sentence: ${line}`);}
 for(const word of ['Dice art','Dice layer','Undo','Use in Studio','top bar'])ok(ART_ROOM_GUIDE.some(l=>l.includes(word)),`guide names the control the room renders: ${word}`);
 ok(ART_ROOM_SHORTCUTS.length===4&&ART_ROOM_SHORTCUTS.every(([k,a])=>k&&a),'four shortcuts, each with keys and an action');
 ok(new Set(ART_ROOM_SHORTCUTS.map(([,a])=>a)).size===4,'shortcut actions are distinct');

 // EVERY INSTRUMENT has a written description that the stage can show, and it is not its name.
 for(const t of ART_TEMPLATES){
  ok(t.description&&t.description.length>=20&&t.description.endsWith('.'),`${t.id} carries a description sentence`);
  ok(t.description!==t.name&&artTemplateName(t.id)===t.name,`${t.id} description differs from its name`);
  const r=createDefaultArtRecipe();r.layers=[createArtLayer(t.id,7,'only')];r.soloId=null;
  const preview=artInstrumentNote(r,{selectedId:'',scope:'composition'},t.id);
  ok(preview&&preview.state==='preview'&&preview.text===t.description&&preview.name===t.name&&preview.kind===t.id,'a preview shows the previewed instrument, whatever is selected');
  const selected=artInstrumentNote(r,{selectedId:'only',scope:'layer'},null);
  ok(selected&&selected.state==='layer'&&selected.text===t.description,'a selected live layer shows its description');
  ok(artInstrumentNote(r,{selectedId:'only',scope:'composition'},null)===null,'the whole composition says nothing');
  ok(artInstrumentNote(r,{selectedId:'missing',scope:'layer'},null)===null,'a missing selection says nothing');
  r.layers[0].locked=true;const held=artInstrumentNote(r,{selectedId:'only',scope:'layer'},null);
  ok(held.state==='held'&&held.text.includes(t.name)&&held.text.includes('unlock'),'a held layer says why Dice layer is dark, and how to fix it');
  r.layers[0].enabled=false;const off=artInstrumentNote(r,{selectedId:'only',scope:'layer'},null);
  ok(off.state==='off'&&off.text.includes(t.name)&&off.text.includes('Turn it on'),'an off layer says so, and off beats held');
  ok(artInstrumentNote(r,{selectedId:'only',scope:'layer'},t.id).state==='preview','a preview beats everything');
 }
 ok(artTemplateName('not-a-kind')==='not-a-kind','an unknown kind falls back to its id rather than throwing');

 // DICE TARGETS across seeds × layer counts × lock/enable masks, against a reference computed the long way.
 for(let seed=0;seed<24;seed++)for(let count=0;count<=8;count++){
  const r=createDefaultArtRecipe();
  r.layers=ART_TEMPLATES.slice(0,count).map((t,i)=>({...createArtLayer(t.id,seed,'item-'+i),locked:((seed>>i)&1)===1,enabled:((seed>>(i+3))&1)===0}));
  r.soloId=count?'item-0':null;
  const frozen=structuredClone(r);
  for(let pick=-1;pick<count;pick++){
   const sel=artSelection(r,{selectedId:pick<0?'nothing':'item-'+pick,scope:'layer'});
   const chosen=r.layers.find(l=>l.id===sel.selectedId);
   const expectArt=r.layers.some(l=>l.enabled&&!l.locked);
   const expectLayer=!!chosen&&chosen.enabled&&!chosen.locked;
   const t=artDiceTargets(r,sel);
   ok(t.art===expectArt&&t.layer===expectLayer,`targets match the mask (seed ${seed}, count ${count}, pick ${pick})`);
   ok(t.layerName===(chosen?artTemplateName(chosen.kind):''),'the accessible name carries the selected instrument');
   const a=artDiceTargets(r,sel,true);ok(a.art===false&&a.layer===false&&a.layerName===t.layerName,'a preview owns the dice');
   if(!t.layer&&chosen&&sel.scope==='layer'){const n=artInstrumentNote(r,sel,null);ok(n&&(n.state==='held'||n.state==='off'),'every dark Dice layer has a stage line explaining it');}
   if(t.layer&&sel.scope==='layer'){const n=artInstrumentNote(r,sel,null);ok(n&&n.state==='layer','a live Dice layer shows the instrument, not a warning');}
   if(sel.scope==='composition')ok(artInstrumentNote(r,sel,null)===null,'the composition readout carries no instrument line even with a layer selected');
  }
  ok(count===0?!artDiceTargets(r,{selectedId:'',scope:'composition'}).art:true,'an empty canvas dices nothing');
  assert.deepEqual(r,frozen,'nothing here mutates the recipe');
 }

 // UNDO SPEAKS: the label of the step, or the old wording when a step has none.
 ok(artUndoNotice('Keep Knot Foundry as layer 4',false)==='Undid: Keep Knot Foundry as layer 4.','undo names the step');
 ok(artUndoNotice('Dice art',true)==='Redid: Dice art.','redo names the step');
 ok(artUndoNotice(undefined,false)==='Change undone.'&&artUndoNotice('',true)==='Change restored.','unlabelled steps keep the old words');

 console.log(`ART GUIDE invariants PASS: ${checks} checks — four-line guide, twelve descriptions at the decision point, one-tap dice targets across 24 seeds × 9 stacks × every pick, undo that names its step`);
} finally {rmSync(temp,{recursive:true,force:true});}
