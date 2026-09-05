// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
// Recipes, including their random choices, are data. Rendering never advances RNG state.
export type ArtKind = 'contour' | 'rosette' | 'rings' | 'ribbons' | 'branches' | 'facets' | 'weave' | 'particles';
export const ART_TEMPLATES: ReadonlyArray<{id: ArtKind; name: string; description: string; category: string}> = [
  {id:'contour',name:'Contour Atlas',description:'Fine contours moving through an imagined landscape.',category:'Fields'},
  {id:'rosette',name:'Petal Engine',description:'Nested geometric petals opening around a quiet center.',category:'Geometry'},
  {id:'rings',name:'Orbit Press',description:'Offset ellipses weave a field of luminous interference.',category:'Geometry'},
  {id:'ribbons',name:'Ribbon Choir',description:'Long bands bend together like a slow standing wave.',category:'Fields'},
  {id:'branches',name:'Branch Fans',description:'Seeded branches sway into delicate botanical fans.',category:'Organic'},
  {id:'facets',name:'Prism Garden',description:'Angular crystal forms catch a moving imaginary light.',category:'Geometry'},
  {id:'weave',name:'Woven Circuit',description:'Crossing bands turn a precise grid into a living textile.',category:'Pattern'},
  {id:'particles',name:'Satellite Dust',description:'Small marks and analytic trails float around closed paths.',category:'Atmosphere'},
];

export const ART_PALETTES = {
  cobalt:{id:'cobalt',name:'Cobalt / coral',colors:['#F1E9D5','#557BEE','#82D0CB','#EF866F','#D4B574']},
  verdigris:{id:'verdigris',name:'Verdigris / paper',colors:['#EFE4CC','#82B4A2','#4C8990','#CF886C','#C9CB93']},
  citrus:{id:'citrus',name:'Citrus / dusk',colors:['#E6EC99','#9CC772','#6CABAC','#DD8974','#F3E8CF']},
  ember:{id:'ember',name:'Ember / violet',colors:['#F0C697','#DC7961','#A999CD','#E6A7AF','#F4E6CE']},
  ink:{id:'ink',name:'Ink / silver',colors:['#F3EEE1','#BBC5D0','#8DA9BD','#6A8F9B','#DDC49C']},
  orchid:{id:'orchid',name:'Orchid / lagoon',colors:['#D1A9DD','#8EA5DC','#78C6BF','#EDD5BB','#E899B3']},
} as const;
export type ArtPaletteId = keyof typeof ART_PALETTES;
export const ART_SIZES = {
  card:{width:2066,height:1319,label:'Vibe card'},
  square:{width:1200,height:1200,label:'Square'},
  portrait:{width:1080,height:1920,label:'Portrait'},
  wide:{width:1920,height:1080,label:'Wide'},
} as const;
export type ArtSizeId = keyof typeof ART_SIZES;
export type ArtAutomationTarget = 'none' | 'form' | 'scale' | 'rotation' | 'opacity' | 'drift';
export interface ArtLayer {
  id:string; kind:ArtKind; seed:number; palette:ArtPaletteId; enabled:boolean; locked:boolean;
  opacity:number; blend:'source-over'|'screen'|'multiply'|'lighter'; scale:number; density:number;
  rotation:number; x:number; y:number;
  automation:{target:ArtAutomationTarget;amount:number;cycles:number;phase:number};
}
export interface ArtRecipe {
  version:1; size:ArtSizeId; duration:number; background:string; soloId:string|null; layers:ArtLayer[];
}
export interface ArtLayerSample {
  scale:number; density:number; rotation:number; x:number; y:number; opacity:number; form:number;
}
export class ArtRecipeError extends Error { constructor(message:string) {super(message);this.name='ArtRecipeError';} }
const kinds=ART_TEMPLATES.map(item=>item.id), palettes=Object.keys(ART_PALETTES) as ArtPaletteId[];
const targets:ArtAutomationTarget[]=['none','form','scale','rotation','opacity','drift'];
const blends:ArtLayer['blend'][]=['source-over','screen','multiply','lighter'];
const clamp=(x:number,low:number,high:number)=>Math.min(high,Math.max(low,x));

function record(value:unknown,label:string):Record<string,unknown> {
  if(!value||typeof value!=='object'||Array.isArray(value))throw new ArtRecipeError(`${label} must be an object.`);
  return value as Record<string,unknown>;
}
function keys(value:Record<string,unknown>,allowed:string[],label:string):void {
  if(Object.keys(value).some(key=>!allowed.includes(key)))throw new ArtRecipeError(`${label} contains an unsupported setting.`);
}
function number(value:unknown,low:number,high:number,label:string,integer=false):number {
  if(typeof value!=='number'||!Number.isFinite(value)||value<low||value>high||(integer&&!Number.isSafeInteger(value)))
    throw new ArtRecipeError(`${label} must be ${integer?'a whole number ':'a number '}from ${low} to ${high}.`);
  return value;
}
function choice<T extends string>(value:unknown,allowed:readonly T[],label:string):T {
  if(typeof value!=='string'||!allowed.includes(value as T))throw new ArtRecipeError(`${label} is not supported.`);
  return value as T;
}
function identifier(value:unknown):string {
  if(typeof value!=='string'||!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$/.test(value))throw new ArtRecipeError('Each art layer needs a valid, unique ID.');
  return value;
}
function boolean(value:unknown,label:string):boolean {
  if(typeof value!=='boolean')throw new ArtRecipeError(`${label} must be on or off.`);return value;
}

export function normalizeArtRecipe(value:unknown):ArtRecipe {
  const r=record(value,'Art recipe');keys(r,['version','size','duration','background','soloId','layers'],'Art recipe');
  if(r.version!==1)throw new ArtRecipeError('This art recipe version is not supported.');
  if(!Array.isArray(r.layers)||r.layers.length>8)throw new ArtRecipeError('An art recipe can contain up to eight layers.');
  if(typeof r.background!=='string'||(r.background!=='transparent'&&!/^#[0-9a-fA-F]{6}$/.test(r.background)))
    throw new ArtRecipeError('Choose a six-digit background color or transparent.');
  const seen=new Set<string>();
  const layers=r.layers.map((raw,index):ArtLayer=>{
    const l=record(raw,`Layer ${index+1}`);
    keys(l,['id','kind','seed','palette','enabled','locked','opacity','blend','scale','density','rotation','x','y','automation'],'Art layer');
    const id=identifier(l.id);if(seen.has(id))throw new ArtRecipeError('Art layer IDs must be unique.');seen.add(id);
    const a=record(l.automation,'Automation');keys(a,['target','amount','cycles','phase'],'Automation');
    return {
      id,kind:choice(l.kind,kinds,'Art family'),seed:number(l.seed,0,0xffffffff,'Seed',true),
      palette:choice(l.palette,palettes,'Palette'),enabled:boolean(l.enabled,'Layer enabled'),locked:boolean(l.locked,'Layer locked'),
      opacity:number(l.opacity,0,1,'Opacity'),blend:choice(l.blend,blends,'Blend'),scale:number(l.scale,.3,2,'Scale'),
      density:number(l.density,0,1,'Density'),rotation:number(l.rotation,-180,180,'Rotation'),
      x:number(l.x,-.75,.75,'Horizontal position'),y:number(l.y,-.75,.75,'Vertical position'),
      automation:{target:choice(a.target,targets,'Automation target'),amount:number(a.amount,0,1,'Automation amount'),
        cycles:number(a.cycles,1,4,'Automation cycles',true),phase:number(a.phase,0,1,'Automation phase')},
    };
  });
  if(r.soloId!==null&&(typeof r.soloId!=='string'||!seen.has(r.soloId)))throw new ArtRecipeError('The solo layer is missing from this recipe.');
  return {version:1,size:choice(r.size,Object.keys(ART_SIZES) as ArtSizeId[],'Art size'),
    duration:number(r.duration,2,24,'Loop duration'),background:r.background,soloId:r.soloId as string|null,layers};
}

/** A small integer PRNG; every caller owns its stream. Never use a frame clock as seed. */
export function createArtRandom(seed:number):()=>number {
  let state=seed>>>0;
  return ()=>{state=(state+0x6d2b79f5)>>>0;let z=state;z=Math.imul(z^(z>>>15),z|1);z^=z+Math.imul(z^(z>>>7),z|61);return ((z^(z>>>14))>>>0)/4294967296;};
}

export function createArtLayer(kind:ArtKind,seed:number,id:string):ArtLayer {
  choice(kind,kinds,'Art family');number(seed,0,0xffffffff,'Seed',true);identifier(id);
  const random=createArtRandom(seed);
  return {id,kind,seed,palette:'cobalt',enabled:true,locked:false,opacity:.8,blend:'source-over',scale:1,density:.5,
    rotation:0,x:0,y:0,automation:{target:'form',amount:.4,cycles:1,phase:Math.round(random()*1000)/1000}};
}

export function createDefaultArtRecipe():ArtRecipe {
  return {version:1,size:'card',duration:8,background:'#0B1722',soloId:null,layers:[
    {...createArtLayer('contour',314159,'layer-contour'),opacity:.42,scale:1.1,density:.42,automation:{target:'form',amount:.35,cycles:1,phase:0}},
    {...createArtLayer('rosette',271828,'layer-rosette'),opacity:.93,scale:.93,density:.6,x:-.06,y:.01,automation:{target:'form',amount:.48,cycles:1,phase:.15}},
    {...createArtLayer('particles',161803,'layer-particles'),opacity:.8,blend:'screen',density:.24,automation:{target:'drift',amount:.35,cycles:1,phase:0}},
  ]};
}

/** Locked, disabled, and untargeted layer objects remain untouched, including IDs. */
export function rollArtRecipe(recipe:ArtRecipe,seed:number,onlyLayerId?:string):ArtRecipe {
  const normalized=normalizeArtRecipe(recipe);number(seed,0,0xffffffff,'Dice seed',true);
  if(onlyLayerId!==undefined&&!normalized.layers.some(layer=>layer.id===onlyLayerId))throw new ArtRecipeError('Choose an existing layer to roll.');
  const random=createArtRandom(seed),palette=palettes[Math.floor(random()*palettes.length)];
  const rounded=(value:number)=>Math.round(value*1000)/1000;
  return {...normalized,layers:recipe.layers.map(layer=>{
    if(layer.locked||!layer.enabled||(onlyLayerId!==undefined&&layer.id!==onlyLayerId))return layer;
    return {...layer,seed:Math.floor(random()*4294967296),palette,
      density:rounded(.2+random()*.7),scale:rounded(.7+random()*.65),rotation:rounded((random()-.5)*90),
      x:rounded((random()-.5)*.24),y:rounded((random()-.5)*.2),
      automation:{...layer.automation,amount:rounded(.2+random()*.55),phase:rounded(random())}};
  })};
}

export function sampleArtLayer(layer:ArtLayer,time:number,duration:number):ArtLayerSample {
  if(!Number.isFinite(time))throw new ArtRecipeError('Art time must be finite.');
  number(duration,2,24,'Loop duration');
  const s:ArtLayerSample={scale:layer.scale,density:layer.density,rotation:layer.rotation,x:layer.x,y:layer.y,opacity:layer.opacity,form:0};
  const a=layer.automation;if(a.target==='none'||a.amount===0)return s;
  const u=((time%duration)+duration)%duration/duration;
  const angle=2*Math.PI*((u*a.cycles+a.phase)%1),wave=Math.sin(angle),quad=Math.cos(angle),amount=a.amount;
  switch(a.target){
    case 'form':s.form=wave*amount;break;
    case 'scale':s.scale=clamp(s.scale*(1+.35*wave*amount),.3,2);break;
    case 'rotation':s.rotation=((s.rotation+90*wave*amount+540)%360)-180;break;
    case 'opacity':s.opacity*=1-.45*amount+.45*amount*quad;break;
    case 'drift':s.x=clamp(s.x+.18*amount*wave,-.75,.75);s.y=clamp(s.y+.12*amount*(quad-1),-.75,.75);break;
  }
  return s;
}

export function artIsAnimated(recipe:ArtRecipe):boolean {
  return recipe.layers.some(layer=>layer.enabled&&(!recipe.soloId||recipe.soloId===layer.id)&&layer.opacity>0
    &&layer.automation.target!=='none'&&layer.automation.amount>0);
}
