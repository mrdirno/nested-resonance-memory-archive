// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
// Local real-module pixel seam; production UI/project/video proof is separate.
import {test,expect} from '@playwright/test';
const APP_URL=process.env.COLLAGE_BASE_URL||'http://localhost:5199/';
test.skip(!['localhost','127.0.0.1','[::1]'].includes(new URL(APP_URL).hostname),'This seam imports Vite source; it cannot certify a deployed bundle.');

test('eight families have real distinct pixels, exact loops, editable alpha and deterministic seeks',async({page},testInfo)=>{
  test.setTimeout(60_000);await page.goto(APP_URL);
  const evidence=await page.evaluate(async()=>{
    const A=await import('/src/lib/artRack.ts'),{drawArt}=await import('/src/lib/artRackRenderer.ts');
    document.body.innerHTML='';document.body.style.cssText='margin:0;padding:24px;background:#0b1722;color:#f1e9d5;font:14px system-ui;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px';
    const results=[];
    const hash=(pixels:Uint8ClampedArray)=>{let n=2166136261;for(const byte of pixels)n=Math.imul(n^byte,16777619);return n>>>0;};
    const different=(a:Uint8ClampedArray,b:Uint8ClampedArray)=>{let n=0;for(let i=0;i<a.length;i+=4)if(a[i]!==b[i]||a[i+1]!==b[i+1]||a[i+2]!==b[i+2]||a[i+3]!==b[i+3])n++;return n;};
    for(const template of A.ART_TEMPLATES){
      const holder=document.createElement('figure');holder.style.cssText='margin:0';
      const canvas=document.createElement('canvas');canvas.width=320;canvas.height=240;canvas.style.cssText='width:100%;height:auto;border:1px solid #46606a;border-radius:8px;background:#112430';
      const caption=document.createElement('figcaption');caption.textContent=template.name;caption.style.cssText='margin-top:8px';holder.append(canvas,caption);document.body.append(holder);
      const ctx=canvas.getContext('2d',{willReadFrequently:true})!;
      const recipe={...A.createDefaultArtRecipe(),background:'transparent',layers:[A.createArtLayer(template.id,55,'one')]};
      recipe.layers[0].automation={target:'form',amount:.75,cycles:1,phase:0};
      const render=(t:number)=>{drawArt(ctx,320,240,recipe,t);return ctx.getImageData(0,0,320,240).data;};
      const zero=render(0),end=render(recipe.duration),middle=render(2);render(7);const seek=render(2);
      recipe.layers[0].automation.target='none';const still=render(0),stillLater=render(3);
      recipe.layers[0].enabled=false;const empty=render(0);
      recipe.layers[0].enabled=true;recipe.layers[0].automation.target='form';render(0);
      let painted=0,transparent=0;for(let i=3;i<zero.length;i+=4){if(zero[i]>0)painted++;else transparent++;}
      results.push({kind:template.id,hash:hash(zero),painted,transparent,endpoint:different(zero,end),motion:different(zero,middle),seek:different(middle,seek),static:different(still,stillLater),disabled:empty.some((_,i)=>i%4===3&&empty[i]>0)});
    }
    const canvas=document.createElement('canvas');canvas.width=640;canvas.height=400;const ctx=canvas.getContext('2d')!;
    const recipe=A.createDefaultArtRecipe(),snapshot=JSON.stringify(recipe);
    drawArt(ctx,640,400,recipe,0);const normal=ctx.getImageData(0,0,640,400).data;
    ctx.globalAlpha=.23;ctx.filter='blur(2px)';ctx.shadowBlur=7;ctx.setLineDash([3,5]);ctx.translate(4,5);
    const callerBefore={alpha:ctx.globalAlpha,filter:ctx.filter,shadow:ctx.shadowBlur,dash:ctx.getLineDash().join(','),translate:ctx.getTransform().e};
    drawArt(ctx,640,400,recipe,0);const restored=ctx.getImageData(0,0,640,400).data;
    const callerAfter={alpha:ctx.globalAlpha,filter:ctx.filter,shadow:ctx.shadowBlur,dash:ctx.getLineDash().join(','),translate:ctx.getTransform().e};
    const callerRestored=JSON.stringify(callerBefore)===JSON.stringify(callerAfter);
    const times=[];const worst={...recipe,layers:A.ART_TEMPLATES.map((t:any,i:number)=>({...A.createArtLayer(t.id,i+1,'l'+i),density:1,scale:.3}))};
    for(let i=0;i<6;i++){const start=performance.now();drawArt(ctx,640,400,worst,i/4);times.push(performance.now()-start);}
    const png=canvas.toDataURL('image/png');
    return{results,contextDifference:different(normal,restored),callerRestored,callerBefore,callerAfter,immutable:snapshot===JSON.stringify(recipe),times,pngBytes:png.length};
  });
  await testInfo.attach('engine-pixel-and-time-evidence',{body:JSON.stringify(evidence,null,2),contentType:'application/json'});
  expect(new Set(evidence.results.map(x=>x.hash)).size).toBe(8);
  for(const result of evidence.results){
    expect(result.painted,result.kind).toBeGreaterThan(100);expect(result.transparent,result.kind).toBeGreaterThan(100);
    expect(result.endpoint,result.kind).toBe(0);expect(result.seek,result.kind).toBe(0);expect(result.static,result.kind).toBe(0);
    expect(result.motion,result.kind).toBeGreaterThan(20);expect(result.disabled,result.kind).toBe(false);
  }
  expect(evidence.contextDifference).toBe(0);expect(evidence.callerAfter).toEqual(evidence.callerBefore);expect(evidence.immutable).toBe(true);expect(evidence.pngBytes).toBeGreaterThan(1000);
  expect(Math.max(...evidence.times),'catastrophic eight-layer regression guard, not a real-time promise').toBeLessThan(2000);
  await page.screenshot({path:testInfo.outputPath('art-rack-families.png'),fullPage:true});
});
