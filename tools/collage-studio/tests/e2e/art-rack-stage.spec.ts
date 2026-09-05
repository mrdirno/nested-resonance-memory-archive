// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
/**
 * LOCAL-ONLY native compositor seam, using real Vite modules and canvas pixels.
 * Production UI, project and encoded-movie proof lives in art-rack-export.spec.ts.
 * No product hooks; internal cache observations prove source reuse and release.
 *
 * npx playwright test tests/e2e/art-rack-stage.spec.ts --project=chromium --project=webkit-desktop --workers=1 --reporter=line
 */
import { test } from '@playwright/test';
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
const APP_URL = process.env.COLLAGE_BASE_URL || 'http://localhost:5199/';
test.skip(!['localhost', '127.0.0.1', '[::1]'].includes(new URL(APP_URL).hostname),
  'This compositor seam imports Vite source modules and cannot certify a deployed bundle.');

test('native sources share raw output time across live, parked, turn, budgeted offline and still exports', async ({ page }, testInfo) => {
  test.setTimeout(60_000);
  await page.setViewportSize({ width: 1280, height: 900 });
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto(APP_URL);
  const result = await page.evaluate(async () => {
      const { createStage } = await import('/src/lib/stage.ts');
      const { createDefaultArtRecipe } = await import('/src/lib/artRack.ts');
      const { drawArt } = await import('/src/lib/artRackRenderer.ts');
      const { renderCanvas, artSourceSize } = await import('/src/lib/renderer.ts');
      const { generateVectorExport } = await import('/src/engine/color/vectorExport.ts');
      const { turnAt } = await import('/src/lib/turn.ts');
      const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
      const canvas = document.createElement('canvas');
      canvas.style.cssText='position:fixed;inset:0;width:512px;height:512px;z-index:99999';
      document.body.append(canvas);
      const stage = createStage(canvas, { logicalWidth:512,maxBackingWidth:512,audio:false,pauseWhenHidden:false,pauseWhenOffscreen:false });
      const hash = cv => { const d = cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data; let h=2166136261; for(let i=0;i<d.length;i++) h=Math.imul(h^d[i],16777619); return h>>>0; };
      const rect = (x,w) => ({bounds:{x,y:0,w,h:512},path:[{x,y:0},{x:x+w,y:0},{x:x+w,y:512},{x,y:512}]});
      const recipe={...createDefaultArtRecipe(),size:'square'};
      const poster=document.createElement('canvas');poster.width=poster.height=4;poster.getContext('2d').fillStyle='#ff0000';poster.getContext('2d').fillRect(0,0,4,4);
      const asset={id:'native-proof',src:poster.toDataURL(),previewSrc:'native-preview-no-network',width:1200,height:1200,analysis:{},art:recipe};
      const scene={layoutItems:[rect(0,256),rect(256,256)],orderedAssets:[asset,asset],clips:[],mode:'minimal',aspect:1,bgColor:'#050505',pace:'rush'};
      try {
        stage.setScene(scene);stage.setTake(8);await sleep(100);
        await stage.scrubTo(0);const zero=hash(canvas);
        const sources=stage.nativeSources;
        let clears=0;const ctx=sources[0].ctx,clear=ctx.clearRect.bind(ctx);ctx.clearRect=(...args)=>{clears++;clear(...args);};
        await stage.renderAtTime(2);const two=hash(canvas);const usedPerFrame=clears;
        const sourceTime=sources[0].paintedTime;
        const screenshot = canvas.toDataURL('image/png');
        const reference=document.createElement('canvas');reference.width=sources[0].canvas.width;reference.height=sources[0].canvas.height;
        drawArt(reference.getContext('2d'),reference.width,reference.height,recipe,2);
        const rawTimeExact=hash(reference)===hash(sources[0].canvas);
        await stage.renderAtTime(0);const back=hash(canvas);
        await stage.renderAtTime(8);const loop=hash(canvas);
        const previews=sources.map(x=>({w:x.canvas.width,h:x.canvas.height}));
        stage.start();await stage.scrubTo(.2);stage.resumeFromGesture({sound:false});await sleep(240);const live={time:stage.takePosition,hash:hash(canvas),painted:sources[0].paintedTime};
        await stage.scrubTo(2);const parked=hash(canvas);await sleep(100);const staysParked=hash(canvas)===parked&&stage.takePosition===2;
        stage.beginOfflineRender({maxWidth:2048,fullRes:true});
        const report=await stage.prepareOfflineStills({budgetPx:4_000_000});
        await stage.renderAtTime(2);const offline={w:canvas.width,h:canvas.height,sourceW:sources[0].canvas.width,sourceH:sources[0].canvas.height,painted:sources[0].paintedTime,report};
        const fullHash=hash(canvas);await stage.renderAtTime(0);await stage.renderAtTime(2);const offlineRepeat=fullHash===hash(canvas);
        stage.endOfflineRender();await stage.scrubTo(0);const shrink=sources[0].canvas.width===previews[0].w&&sources[0].canvas.height===previews[0].h;
        const photo={...asset,id:'photo',src:poster.toDataURL('image/jpeg'),previewSrc:poster.toDataURL('image/jpeg'),art:undefined};
        const mixed=[asset,photo];stage.setScene({...scene,orderedAssets:mixed,pace:'even',turn:{id:'march',seed:7,resolve:(_slot,from)=>mixed[from]}});await sleep(100);
        let fadeTime=0;for(let t=0;t<12;t+=.01){const v=turnAt('march',t);if(v.mix>0&&v.mix<1){fadeTime=t;break;}}
        // Frame transition internals give an independent assertion that the incoming
        // native source is actually being painted, not merely the outgoing source.
        await stage.renderAtTime(fadeTime||3.5);
        const dissolve={time:fadeTime,mix:stage.items.map(x=>x.mix),nativeIncoming:stage.items.some(x=>x.mix>0&&x.still2===sources[0].canvas),painted:sources[0].paintedTime};
        const sourceCount=stage.nativeSources.length;
        const stillRecipe={...recipe,layers:recipe.layers.map(x=>({...x,automation:{...x.automation,target:'none'}}))};
        stage.setScene({...scene,orderedAssets:[{...asset,art:stillRecipe},{...asset,art:stillRecipe}],pace:'even'});stage.start();stage.resumeFromGesture({sound:false});await sleep(120);const staticFrames=stage.frames;await sleep(120);const staticIdle=staticFrames===stage.frames;
        const opening=await renderCanvas(512,1,'minimal',[rect(0,512)],[asset],0);
        const nativeStatic=hash(opening)!==hash(poster);
        const referenceLarge=document.createElement('canvas');referenceLarge.width=referenceLarge.height=1200;drawArt(referenceLarge.getContext('2d'),1200,1200,recipe,0);
        const referenceScaled=document.createElement('canvas');referenceScaled.width=referenceScaled.height=512;referenceScaled.getContext('2d').fillStyle='#050505';referenceScaled.getContext('2d').fillRect(0,0,512,512);referenceScaled.getContext('2d').drawImage(referenceLarge,0,0,512,512);
        const staticMatches=hash(opening)===hash(referenceScaled);
        const svg=await generateVectorExport(512,1,'minimal',[rect(0,512)],[asset],0,undefined,1,'#050505',null,null,[asset]);
        const embedded=new DOMParser().parseFromString(svg,'image/svg+xml').querySelector('image');const href=embedded?.getAttribute('href')||embedded?.getAttribute('xlink:href');
        const bmp=await createImageBitmap(await (await fetch(href)).blob());const check=document.createElement('canvas');check.width=bmp.width;check.height=bmp.height;check.getContext('2d').drawImage(bmp,0,0);bmp.close();
        const svgMatches=hash(check)===hash(referenceLarge);
        const sizes=[8000,16000,30000].map(n=>artSourceSize(recipe,n));
        let workerResult;
        const worker=new Worker(new URL('/src/workers/render.worker.ts',location.href),{type:'module'});
        try{ workerResult=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('worker timeout')),20000);worker.onerror=e=>{clearTimeout(timer);reject(Error(e.message));};worker.onmessage=e=>{clearTimeout(timer);resolve({success:e.data.success,drawn:e.data.drawn,failed:e.data.failedImages,bytes:e.data.blob?.size,error:e.data.error});};worker.postMessage({id:91,width:512,height:512,mode:'minimal',layoutItems:[rect(0,512)],orderedImages:[asset],zoom:1,bgColor:'#050505'});});}finally{worker.terminate();}
        const nativeCanvas=stage.nativeSources[0].canvas;stage.destroy();const freed=nativeCanvas.width===0&&nativeCanvas.height===0;
        return {screenshot,zero,two,back,loop,usedPerFrame,rawTimeExact,sourceTime,previews,live,staysParked,offline,offlineRepeat,shrink,dissolve,sourceCount,staticIdle,nativeStatic,staticMatches,svgMatches,sizes,workerResult,freed};
      } finally { stage.destroy();canvas.remove(); }
    });

  const { screenshot, ...evidence } = result;
  const evidencePath = testInfo.outputPath('native-stage-evidence.json');
  const screenshotPath = testInfo.outputPath('native-stage-at-two-seconds.png');
  await writeFile(evidencePath, JSON.stringify({ ...evidence, errors }, null, 2));
  await writeFile(screenshotPath, Buffer.from(screenshot.split(',')[1], 'base64'));
  await testInfo.attach('native-stage-and-output-evidence', { path: evidencePath, contentType: 'application/json' });
  await testInfo.attach('native-stage-at-two-seconds', { path: screenshotPath, contentType: 'image/png' });
  assert.notEqual(result.zero,result.two);assert.equal(result.zero,result.back);assert.equal(result.zero,result.loop);
  assert.equal(result.usedPerFrame,1);assert.equal(result.rawTimeExact,true);assert.equal(result.sourceTime,2);
  assert.ok(result.live.time>.3&&result.live.painted>.3);assert.equal(result.staysParked,true);
  assert.ok(result.offline.sourceW>result.previews[0].w);assert.ok(result.offline.report.usedPx<=result.offline.report.budgetPx);assert.equal(result.offline.painted,2);
  assert.equal(result.offlineRepeat,true);assert.equal(result.shrink,true);assert.equal(result.sourceCount,1);
  assert.equal(result.dissolve.nativeIncoming,true);assert.equal(result.dissolve.painted,result.dissolve.time);
  assert.equal(result.staticIdle,true);assert.equal(result.staticMatches,true);assert.equal(result.svgMatches,true);
  assert.ok(result.sizes.every(x=>x.width<=4096&&x.height<=4096&&x.width*x.height<=16_000_000));
  assert.equal(result.workerResult.success,true);assert.equal(result.workerResult.failed,0);assert.equal(result.workerResult.drawn,1);assert.ok(result.workerResult.bytes>2000);
  assert.equal(result.freed,true);assert.deepEqual(errors,[]);
 });
