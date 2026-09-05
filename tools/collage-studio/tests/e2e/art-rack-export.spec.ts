// Author: Aldrin Payopay · GPL-3.0-only
// A real native art-only scene, public controls, and decoded exported video.
import { test, expect } from '@playwright/test';
import fs from 'node:fs/promises';

test('native art alone advances, seeks deterministically and exports one complete moving loop', async ({ page }, info) => {
  test.setTimeout(180_000);
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.getByRole('button',{name:'Art Room',exact:true}).click();
  await page.getByRole('button',{name:'Add artwork',exact:true}).click();
  await expect(page.locator('.art-footer p[role=status]')).toContainText('Editable artwork applied', {timeout:60_000});
  await page.getByRole('button',{name:'Close Art Room',exact:true}).click();
  await expect(page.getByRole('button',{name:'Record video',exact:true})).toBeEnabled();
  const hash=()=>page.locator('canvas[aria-hidden=true]').first().evaluate((c:HTMLCanvasElement)=>{
    const x=document.createElement('canvas');x.width=240;x.height=150;const ctx=x.getContext('2d',{willReadFrequently:true})!;ctx.drawImage(c,0,0,240,150);
    const pixels=ctx.getImageData(0,0,240,150).data;let hash=2166136261,lit=0;
    for(let i=0;i<pixels.length;i+=4){hash=Math.imul(hash^pixels[i],16777619)>>>0;if(pixels[i]+pixels[i+1]+pixels[i+2]>160)lit++;}return{hash,lit,pixels:Array.from(pixels)};
  });
  await expect.poll(async()=>(await hash()).lit).toBeGreaterThan(100);
  const initial=await hash();await expect.poll(async()=>(await hash()).hash).not.toBe(initial.hash);
  // The public Stage playhead must seek an art-only scene too.
  const playhead=page.getByLabel(/^Playhead/);
  // Warm browser readback/compositing before comparing repeated parked frames.
  for (const t of ['0.3','0.5']) { await playhead.fill(t); await page.waitForTimeout(160); await hash(); }
  await playhead.fill('2');await page.waitForTimeout(160);const at2=await hash();
  await playhead.fill('5');await page.waitForTimeout(160);const at5=await hash();expect(at5.hash).not.toBe(at2.hash);
  await playhead.fill('2');await page.waitForTimeout(160);const back=await hash();
  const diffs=back.pixels.map((v,i)=>Math.abs(v-at2.pixels[i]));
  const comparison={max:diffs.reduce((a,b)=>Math.max(a,b),0),mean:diffs.reduce((a,b)=>a+b,0)/diffs.length,changed:diffs.filter(d=>d>0).length,large:diffs.filter(d=>d>3).length};
  await fs.writeFile(info.outputPath('stage-seek-comparison.json'),JSON.stringify(comparison));
  // Readback of a GPU-composited preview can differ by 1–2 color levels at
  // a handful of antialiased edges. The direct renderer/Stage seams remain exact.
  expect(comparison.max,JSON.stringify(comparison)).toBeLessThanOrEqual(2);
  expect(comparison.mean,JSON.stringify(comparison)).toBeLessThan(.002);
  expect(comparison.changed,JSON.stringify(comparison)).toBeLessThan(150);
  await page.getByRole('button',{name:'Export',exact:true}).click();
  const sheet=page.getByRole('dialog',{name:'Export',exact:true});
  await expect(sheet.getByRole('button',{name:'Loop 8s',exact:true})).toHaveAttribute('aria-pressed','true');
  const size=sheet.getByRole('radiogroup',{name:'Video size',exact:true});
  if(await size.count())await size.getByRole('radio').first().click();
  await sheet.getByRole('button',{name:'Record 8s video',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'Recorded take',exact:true})).toBeVisible({timeout:140_000});
  const result=await page.evaluate(async()=>{
    const v=document.querySelector('video[controls]') as HTMLVideoElement;v.pause();v.loop=false;
    const c=document.createElement('canvas');c.width=240;c.height=150;const ctx=c.getContext('2d')!;
    const frames=[] as {hash:number;lit:number}[];
    for(const t of [.1,2,5,7.9]){
      await new Promise<void>((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Export did not seek')),12000);v.addEventListener('seeked',()=>{clearTimeout(timer);resolve();},{once:true});v.currentTime=t;});
      // WebKit can emit seeked before the decoded frame reaches the surface.
      await new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve())));
      ctx.drawImage(v,0,0,240,150);const pixels=ctx.getImageData(0,0,240,150).data;let hash=2166136261,lit=0;
      for(let i=0;i<pixels.length;i+=4){hash=Math.imul(hash^pixels[i],16777619)>>>0;if(pixels[i]+pixels[i+1]+pixels[i+2]>160)lit++;}frames.push({hash,lit});
    }
    const blob=await(await fetch(v.currentSrc||v.src)).blob(),bytes=new Uint8Array(await blob.arrayBuffer());let raw='';for(let i=0;i<bytes.length;i+=8192)raw+=String.fromCharCode(...bytes.subarray(i,i+8192));
    return{frames,duration:v.duration,width:v.videoWidth,height:v.videoHeight,type:blob.type,data:btoa(raw)};
  });
  await fs.writeFile(info.outputPath(result.type.includes('mp4')?'Art-Rack-Loop.mp4':'Art-Rack-Loop.webm'),Buffer.from(result.data,'base64'));
  await fs.writeFile(info.outputPath('art-export-receipt.json'),JSON.stringify({...result,data:undefined},null,2));
  expect(result.duration).toBeGreaterThan(7.8);expect(result.duration).toBeLessThan(8.2);
  expect(new Set(result.frames.map(f=>f.hash)).size).toBe(4);for(const frame of result.frames)expect(frame.lit).toBeGreaterThan(100);
  expect(result.width).toBeGreaterThanOrEqual(600);expect(result.height).toBeGreaterThan(400);
  await page.screenshot({path:info.outputPath('art-rack-recorded.png')});
  expect(errors).toEqual([]);
});
