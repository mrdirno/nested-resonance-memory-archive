// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
import assert from 'node:assert/strict';
import esbuild from 'esbuild';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const temp=mkdtempSync(join(tmpdir(),'art-rack-invariants-'));
try{
  const root=join(dirname(fileURLToPath(import.meta.url)),'../..');
  for(const name of ['artRack','artRackRenderer'])await esbuild.build({entryPoints:[join(root,`src/lib/${name}.ts`)],outfile:join(temp,`${name}.mjs`),bundle:true,platform:'neutral',format:'esm',logLevel:'silent'});
  const A=await import(pathToFileURL(join(temp,'artRack.mjs')).href);
  const {drawArt}=await import(pathToFileURL(join(temp,'artRackRenderer.mjs')).href);
  const fresh=()=>A.createDefaultArtRecipe(),copy=value=>structuredClone(value);
  const rejectEdit=edit=>{const r=fresh();edit(r);assert.throws(()=>A.normalizeArtRecipe(r),A.ArtRecipeError);};
  assert.equal(A.ART_TEMPLATES.length,8);assert.equal(new Set(A.ART_TEMPLATES.map(t=>t.id)).size,8);
  assert.deepEqual(A.ART_SIZES.card,{width:2066,height:1319,label:'Vibe card'});
  assert.deepEqual(A.normalizeArtRecipe(fresh()),fresh());
  const immutable=fresh(),before=JSON.stringify(immutable);A.normalizeArtRecipe(immutable);assert.equal(JSON.stringify(immutable),before);
  for(const bad of [null,undefined,[],1,'recipe',{},false])assert.throws(()=>A.normalizeArtRecipe(bad),A.ArtRecipeError);
  for(const bad of [0,2,'1',NaN])rejectEdit(r=>r.version=bad);
  for(const bad of [0,1.99,24.001,NaN,Infinity,'8'])rejectEdit(r=>r.duration=bad);
  for(const bad of ['#FFF','#00000000','#GGGGGG','red','TRANSPARENT',null])rejectEdit(r=>r.background=bad);
  rejectEdit(r=>r.size='unknown');rejectEdit(r=>r.soloId='missing');rejectEdit(r=>delete r.soloId);
  rejectEdit(r=>r.extra=true);rejectEdit(r=>r.layers=null);rejectEdit(r=>r.layers=Array(9).fill(r.layers[0]));
  rejectEdit(r=>r.layers.push(copy(r.layers[0])));rejectEdit(r=>r.layers[0].extra=true);
  rejectEdit(r=>r.layers[0].automation.extra=true);rejectEdit(r=>r.layers[0].automation=[]);
  for(const field of ['id','kind','seed','palette','enabled','locked','opacity','blend','scale','density','rotation','x','y','automation'])
    rejectEdit(r=>delete r.layers[0][field]);
  const invalid={id:['','a/b','x'.repeat(81),5],kind:['unknown',null],seed:[-1,4294967296,.5,NaN,Infinity,'1'],palette:['unknown','__proto__'],
    enabled:[1,'true',null],locked:[1,'false',null],opacity:[-.001,1.001,NaN],blend:['overlay','copy'],scale:[.299,2.001],density:[-.001,1.001],rotation:[-180.01,180.01],x:[-.751,.751],y:[-.751,.751]};
  for(const [field,values]of Object.entries(invalid))for(const value of values)rejectEdit(r=>r.layers[0][field]=value);
  for(const [field,values]of Object.entries({target:['unknown'],amount:[-.001,1.001,NaN],cycles:[0,5,1.5,'1'],phase:[-.001,1.001,Infinity]}))
    for(const value of values)rejectEdit(r=>r.layers[0].automation[field]=value);
  for(const duration of [2,24]){
    const r=fresh();r.duration=duration;r.background='transparent';r.layers=[];assert.deepEqual(A.normalizeArtRecipe(r),r);
  }
  const bounds=fresh();bounds.layers=A.ART_TEMPLATES.map((t,i)=>({...A.createArtLayer(t.id,i%2?0:0xffffffff,'layer-'+i),scale:i%2?.3:2,density:i%2?0:1,opacity:i%2?0:1,rotation:i%2?-180:180,x:i%2?-.75:.75,y:i%2?-.75:.75}));
  assert.deepEqual(A.normalizeArtRecipe(bounds),bounds);

  const r=fresh();r.layers[0].locked=true;r.layers[1].enabled=false;
  const frozen=JSON.stringify(r),rolled=A.rollArtRecipe(r,123456);
  assert.equal(JSON.stringify(r),frozen,'dice never mutates input');
  for(const i of [0,1]){assert.equal(rolled.layers[i],r.layers[i]);assert.equal(JSON.stringify(rolled.layers[i]),JSON.stringify(r.layers[i]));}
  assert.notDeepEqual(rolled.layers[2],r.layers[2]);assert.deepEqual(rolled.layers.map(l=>l.id),r.layers.map(l=>l.id));
  assert.deepEqual(rolled,A.rollArtRecipe(r,123456));assert.deepEqual(A.normalizeArtRecipe(rolled),rolled);
  const target=fresh(),one=A.rollArtRecipe(target,42,target.layers[1].id);
  assert.equal(one.layers[0],target.layers[0]);assert.equal(one.layers[2],target.layers[2]);assert.equal(one.layers[1].id,target.layers[1].id);
  assert.throws(()=>A.rollArtRecipe(target,1,'missing'),A.ArtRecipeError);
  for(const bad of [-1,.2,Infinity,4294967296])assert.throws(()=>A.rollArtRecipe(target,bad),A.ArtRecipeError);
  for(let seed=0;seed<50;seed++)assert.doesNotThrow(()=>A.normalizeArtRecipe(A.rollArtRecipe(fresh(),seed)));

  for(const template of A.ART_TEMPLATES)for(const motion of ['none','form','scale','rotation','opacity','drift']){
    const layer=A.createArtLayer(template.id,55,'test');layer.automation={target:motion,amount:.8,cycles:3,phase:.125};
    const original=JSON.stringify(layer),at0=A.sampleArtLayer(layer,0,8),atT=A.sampleArtLayer(layer,8,8);
    assert.deepEqual(atT,at0,'loop endpoint is exact');
    for(const t of [7.75,.125,100,-8,.125,0])assert.deepEqual(A.sampleArtLayer(layer,t,8),A.sampleArtLayer(copy(layer),t,8));
    const earlier=A.sampleArtLayer(layer,.125,8);A.sampleArtLayer(layer,7,8);assert.deepEqual(A.sampleArtLayer(layer,.125,8),earlier);
    assert.equal(JSON.stringify(layer),original);assert.ok(Object.values(at0).every(Number.isFinite));
    if(motion==='none')assert.deepEqual(A.sampleArtLayer(layer,2,8),at0);
    else assert.notDeepEqual(A.sampleArtLayer(layer,1,8),at0,`${motion} makes an intentional change`);
  }
  for(const t of [NaN,Infinity,-Infinity])assert.throws(()=>A.sampleArtLayer(fresh().layers[0],t,8));
  assert.equal(A.artIsAnimated(fresh()),true);
  for(const change of [l=>l.enabled=false,l=>l.opacity=0,l=>l.automation.target='none',l=>l.automation.amount=0]){const r=fresh();r.layers.forEach(change);assert.equal(A.artIsAnimated(r),false);}
  const solo=fresh();solo.soloId=solo.layers[0].id;solo.layers[0].enabled=false;assert.equal(A.artIsAnimated(solo),false);

  // A recording Canvas contract catches non-finite geometry and measures actual
  // draw calls; pixel correctness is exercised separately in a real browser.
  function trace(recipe,time,width=640,height=400){
    const commands=[],state={globalAlpha:1},stack=[];
    const ctx=new Proxy(state,{
      set(obj,key,value){obj[key]=value;commands.push(['set',key,typeof value==='object'?'gradient':value]);return true;},
      get(obj,key){
        if(key in obj)return obj[key];
        if(key==='createLinearGradient')return(...args)=>{commands.push([key,...args]);return{addColorStop(...stops){commands.push(['stop',...stops]);}};};
        return(...args)=>{
          for(const value of args)if(typeof value==='number')assert.ok(Number.isFinite(value),`${String(key)} finite`);
          commands.push([key,...args]);
          if(key==='save')stack.push({...obj});
          if(key==='restore'){const previous=stack.pop();assert.ok(previous);for(const field of Object.keys(obj))delete obj[field];Object.assign(obj,previous);}
        };
      },
    });
    drawArt(ctx,width,height,recipe,time);assert.equal(stack.length,0);return commands;
  }
  const counts={};
  const savedRandom=Math.random;Math.random=()=>{throw new Error('Renderer used ambient randomness');};
  try{
    for(const template of A.ART_TEMPLATES){
      const recipe={...fresh(),background:'transparent',layers:[{...A.createArtLayer(template.id,17,'only'),density:1,scale:.3}]};
      const original=JSON.stringify(recipe),zero=trace(recipe,0),end=trace(recipe,8);
      assert.deepEqual(end,zero,`${template.id} exact endpoint commands`);
      const later=trace(recipe,3.25);trace(recipe,6);assert.deepEqual(trace(recipe,3.25),later);
      assert.equal(JSON.stringify(recipe),original);
      assert.ok(zero.length>40);assert.ok(zero.length<20_000,`${template.id} bounded command count`);counts[template.id]=zero.length;
    }
    const maximum={...fresh(),layers:Array.from({length:8},(_,i)=>({...A.createArtLayer('weave',i,'l'+i),density:1,scale:.3}))};
    const worst=trace(maximum,2,2160,3840).length;assert.ok(worst<60_000,`eight-layer weave command budget: ${worst}`);counts.eightLayerWeave=worst;
  }finally{Math.random=savedRandom;}
  console.log('ART RACK invariants PASS: strict recipes, protected dice, exact loops, seek independence and bounded actual draw commands',JSON.stringify(counts));
}finally{rmSync(temp,{recursive:true,force:true});}
