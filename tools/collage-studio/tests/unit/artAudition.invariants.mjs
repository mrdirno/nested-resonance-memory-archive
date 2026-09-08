// Author: Aldrin Payopay · GPL-3.0-only
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import esbuild from 'esbuild';
const temp=mkdtempSync(join(tmpdir(),'art-audition-'));
try {
 await esbuild.build({entryPoints:['src/lib/artAudition.ts'],bundle:true,format:'esm',outfile:join(temp,'audition.mjs')});
 await esbuild.build({entryPoints:['src/lib/artRack.ts'],bundle:true,format:'esm',outfile:join(temp,'rack.mjs')});
 const {previewArtRecipe,keepArtAudition}=await import(pathToFileURL(join(temp,'audition.mjs')));
 const {createDefaultArtRecipe,createArtLayer,normalizeArtRecipe}=await import(pathToFileURL(join(temp,'rack.mjs')));
 const base=createDefaultArtRecipe();base.layers[0].locked=true;base.layers[1].enabled=false;base.soloId=base.layers[0].id;
 const original=structuredClone(base),candidate={layer:createArtLayer('torus-knot',987,'candidate'),placement:'add',targetId:base.layers[0].id};
 Object.freeze(base.layers);Object.freeze(base);
 assert.equal(previewArtRecipe(base,null),base);
 const preview=previewArtRecipe(base,candidate),kept=keepArtAudition(base,candidate);
 assert.deepEqual(preview,kept);assert.deepEqual(base,original);assert.equal(kept.soloId,null);assert.deepEqual(kept.layers.at(-1),candidate.layer);
 assert.deepEqual(kept.layers.slice(0,3),base.layers);assert.deepEqual(previewArtRecipe(base,candidate,true).layers,[candidate.layer]);
 const replace={...candidate,placement:'replace'};const replacement=keepArtAudition(base,replace);
 assert.deepEqual(replacement.layers,[candidate.layer,...base.layers.slice(1)]);assert.deepEqual(previewArtRecipe(base,replace),replacement);
 assert.throws(()=>keepArtAudition(base,{...replace,targetId:'missing'}),/Select a kept layer/);
 const full={...base,layers:Array.from({length:8},(_,i)=>createArtLayer('rings',i,'slot-'+i)),soloId:'slot-3'};
 const ninth=previewArtRecipe(full,candidate);assert.equal(ninth.layers.length,9);assert.throws(()=>normalizeArtRecipe(ninth));assert.throws(()=>keepArtAudition(full,candidate),/eight layers/);
 const replacedFull=keepArtAudition(full,{...replace,targetId:'slot-3'});assert.equal(replacedFull.layers.length,8);assert.deepEqual(replacedFull.layers[3],candidate.layer);
 const start=keepArtAudition(full,candidate,true);assert.deepEqual(start.layers,[candidate.layer]);for(const key of ['size','background','duration'])assert.equal(start[key],full[key]);
 candidate.layer.opacity=.23;assert.notEqual(kept.layers.at(-1).opacity,.23);
 console.log('PASS audition isolation, exact preview/keep, sibling preservation, solo, comparison, replace, full-capacity refusal, explicit start, immutable snapshot');
}finally{rmSync(temp,{recursive:true,force:true});}
