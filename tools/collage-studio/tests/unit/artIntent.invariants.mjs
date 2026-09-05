// Author: Aldrin Payopay · GPL-3.0-only
import assert from 'node:assert/strict';
import esbuild from 'esbuild';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const temp=mkdtempSync(join(tmpdir(),'art-intent-'));
try {
 const root=join(dirname(fileURLToPath(import.meta.url)),'../..');
 const modules={};
 for(const name of ['artIntent','artRack']){await esbuild.build({entryPoints:[join(root,`src/lib/${name}.ts`)],outfile:join(temp,`${name}.mjs`),bundle:true,platform:'neutral',format:'esm',logLevel:'silent'});modules[name]=await import(pathToFileURL(join(temp,`${name}.mjs`)).href);}
 const {artTemplateIntent,artHistoryEntry,artSelection}=modules.artIntent;
 const {createDefaultArtRecipe,createArtLayer,ART_TEMPLATES,normalizeArtRecipe}=modules.artRack;
 const full=createDefaultArtRecipe();full.layers=ART_TEMPLATES.map((t,i)=>createArtLayer(t.id,i+1,'original-'+i));full.soloId=full.layers[2].id;full.layers[2].locked=true;full.size='square';full.duration=12;
 const before=structuredClone(full),selection={selectedId:full.layers[2].id,scope:'layer'};
 const snapshot=artHistoryEntry(full,selection),newLayer=createArtLayer('facets',42,'replacement');
 assert.throws(()=>artTemplateIntent(full,newLayer,'add'),/Eight layers/);
 const replacement=normalizeArtRecipe(artTemplateIntent(full,newLayer,'use'));
 assert.deepEqual(replacement.layers,[newLayer]);assert.equal(replacement.soloId,null);assert.equal(replacement.size,'square');assert.equal(replacement.duration,12);assert.equal(replacement.background,full.background);
 assert.deepEqual(full,before,'replacement and failed Add do not mutate old project');
 replacement.layers[0].opacity=.12;full.layers[2].opacity=.34;selection.scope='composition';
 assert.deepEqual(snapshot.recipe,before,'history owns a deep recipe snapshot');assert.deepEqual(snapshot.selection,{selectedId:'original-2',scope:'layer'},'history owns selection');
 assert.deepEqual(artSelection(before,{selectedId:'stale',scope:'layer'}),{selectedId:'original-7',scope:'composition'},'missing selection never retains layer dice');
 assert.deepEqual(artSelection({...before,layers:[],soloId:null},{selectedId:'stale',scope:'layer'}),{selectedId:'',scope:'composition'});
 assert.throws(()=>artHistoryEntry({...before,uiContext:{}},selection),'UI metadata never becomes saved recipe data');
 const one={...before,layers:[before.layers[2]]};const added=artTemplateIntent(one,newLayer,'add');assert.equal(added.layers[0],one.layers[0]);assert.equal(added.soloId,one.soloId);
 for(let seed=0;seed<32;seed++)for(let count=0;count<=8;count++){
  const r=createDefaultArtRecipe();r.layers=ART_TEMPLATES.slice(0,count).map((t,i)=>({...createArtLayer(t.id,seed,'item-'+i),locked:i%2===0,enabled:i%3!==0}));r.soloId=count?'item-0':null;
  const frozen=structuredClone(r),fresh=createArtLayer(ART_TEMPLATES[seed%8].id,seed+100,'fresh-'+seed);
  const used=normalizeArtRecipe(artTemplateIntent(r,fresh,'use'));assert.deepEqual(used.layers,[fresh]);assert.equal(used.soloId,null);assert.deepEqual(r,frozen);
  if(count<8){const added=normalizeArtRecipe(artTemplateIntent(r,fresh,'add'));assert.deepEqual(added.layers.slice(0,-1),r.layers);assert.equal(added.soloId,r.soloId);}else assert.throws(()=>artTemplateIntent(r,fresh,'add'));
 }
 console.log('ART INTENT invariants PASS: capacity replacement, immutable originals/history, selection scope and strict recipe boundary');
} finally {rmSync(temp,{recursive:true,force:true});}
