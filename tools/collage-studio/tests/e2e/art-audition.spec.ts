// Author: Aldrin Payopay · GPL-3.0-only
// Ring C3722: browsing is transient; Keep commits the exact audition; Studio Apply is separate.
// Public UI/download/Canvas checks run unchanged against local and published builds.
import {test,expect,type Locator,type Page} from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import JSZip from 'jszip';

test.setTimeout(120_000);
test.use({actionTimeout:15_000});
const URL=process.env.COLLAGE_BASE_URL||'/';
async function openRoom(page:Page){
  const entry=page.getByRole('button',{name:'Art Room',exact:true});
  if(!await entry.isVisible())await page.getByRole('button',{name:'Add',exact:true}).click();
  await entry.click();const room=page.getByTestId('art-rack');await expect(room).toBeVisible();return room;
}
async function boot(page:Page){await page.goto(URL);return openRoom(page);}
async function closePreviewSettings(room:Locator){const options=room.locator('details.art-preview-options');if(await options.count()&&await options.getAttribute('open')!==null)await options.locator(':scope > summary').click();}
async function settings(room:Locator){await closePreviewSettings(room);const details=room.locator('details.art-project-settings');if(await details.getAttribute('open')===null)await details.locator(':scope > summary').click();}
async function recipe(page:Page,room:Locator){
  await settings(room);const event=page.waitForEvent('download');await room.getByRole('button',{name:'Save recipe',exact:true}).click();
  return JSON.parse(await fs.readFile((await(await event).path())!,'utf8'));
}
async function preview(room:Locator,name:string){
  await closePreviewSettings(room);await room.getByRole('tab',{name:'Templates',exact:true}).click();
  await room.getByRole('button',{name:`Preview ${name}`,exact:true}).click();
  await expect(room.getByTestId('art-audition')).toBeVisible();
}
async function previewSettings(room:Locator){const details=room.locator('details.art-preview-options');if(await details.getAttribute('open')===null)await details.locator(':scope > summary').click();}
async function keep(room:Locator){await room.getByRole('button',{name:/^(Keep layer|Replace layer \d+)$/}).click();await expect(room.getByTestId('art-audition')).toHaveCount(0);}
async function start(room:Locator,name:string){await preview(room,name);await previewSettings(room);await room.getByRole('button',{name:'Use as starting template',exact:true}).click();}
async function undo(room:Locator,redo=false){await settings(room);await room.getByRole('button',{name:redo?'Redo art edit':'Undo art edit',exact:true}).click();}
async function seek(room:Locator,time=2.25){
  const pause=room.getByRole('button',{name:'Pause art preview',exact:true});if(await pause.isVisible())await pause.click();
  await room.getByLabel('Art playhead',{exact:true}).fill(String(time));
  await expect(room.getByLabel('Art playhead',{exact:true})).toHaveValue(String(time));
  await room.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
}
async function pixels(room:Locator){
  return room.getByLabel('Animated art preview',{exact:true}).evaluate((c:HTMLCanvasElement)=>{
    const bytes=c.getContext('2d',{willReadFrequently:true})!.getImageData(0,0,c.width,c.height).data;
    let hash=2166136261;const colors=new Set<number>();
    for(let i=0;i<bytes.length;i+=4){const color=((bytes[i]<<24)|(bytes[i+1]<<16)|(bytes[i+2]<<8)|bytes[i+3])>>>0;hash=Math.imul(hash^color,16777619);if(i%128===0)colors.add(color);}
    return{hash:hash>>>0,colors:colors.size,width:c.width,height:c.height};
  });
}
async function warm(room:Locator){for(const time of [.1,.2]){await seek(room,time);await pixels(room);}await seek(room);}
async function archive(page:Page,file:string){
  await page.getByRole('button',{name:'Open',exact:true}).focus();const event=page.waitForEvent('download');await page.keyboard.press('Control+s');
  await(await event).saveAs(file);const zip=await JSZip.loadAsync(await fs.readFile(file));return{zip,manifest:JSON.parse(await zip.file('manifest.json')!.async('text'))};
}
async function originals(saved:Awaited<ReturnType<typeof archive>>){
  return Promise.all(saved.manifest.images.map(async(image:any)=>({id:image.id,name:image.originalName,sha256:createHash('sha256').update(await saved.zip.file('images/'+image.storageFilename)!.async('nodebuffer')).digest('hex')})));
}
async function applied(room:Locator,update=false){
  await room.getByRole('button',{name:update?'Update in Studio':'Use in Studio',exact:true}).click();
  await expect(room.locator('.art-footer [role=status]')).toContainText('Editable artwork applied',{timeout:30_000});
}

test('audition browsing, compare and dice change pixels without changing kept recipe or history',async({page},info)=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));const room=await boot(page);
  const before=await recipe(page,room);await expect(room.getByRole('button',{name:'Undo art edit',exact:true})).toBeDisabled();
  await warm(room);const original=await pixels(room);expect(original.colors).toBeGreaterThan(100);
  await preview(room,'Knot Foundry');await seek(room);const knot=await pixels(room);expect(knot.hash).not.toBe(original.hash);
  await expect(room.locator('.art-studio-pending')).toBeDisabled();
  await preview(room,'Tidal Surface');await seek(room);const tidal=await pixels(room);expect(tidal.hash).not.toBe(knot.hash);
  await previewSettings(room);await room.getByLabel('Preview opacity',{exact:true}).fill('0.43');
  await room.getByLabel('Preview blend',{exact:true}).selectOption('screen');
  await room.getByRole('button',{name:'Dice preview',exact:true}).click();await seek(room);const diced=await pixels(room);expect(diced.hash).not.toBe(tidal.hash);
  await room.getByRole('button',{name:'Preview alone',exact:true}).click();await seek(room);const alone=await pixels(room);expect(alone.hash).not.toBe(diced.hash);
  expect(await recipe(page,room)).toEqual(before);
  await expect(room.locator('.art-footer [role=status]')).toContainText(/preview.*(excluded|not included|not saved)|kept layers only/i);
  await expect(room.getByRole('button',{name:'Undo art edit',exact:true})).toBeDisabled();
  await expect(room.getByRole('button',{name:'Redo art edit',exact:true})).toBeDisabled();
  await room.getByRole('button',{name:'Dismiss preview',exact:true}).click();await seek(room);
  expect(await pixels(room)).toEqual(original);expect(await recipe(page,room)).toEqual(before);
  await expect(room.getByRole('button',{name:'Use in Studio',exact:true})).toBeEnabled();
  await fs.writeFile(info.outputPath('audition-isolation.json'),JSON.stringify({recipe:before,original,knot,tidal,diced,alone},null,2));expect(errors).toEqual([]);
});

test('Keep promotes the exact preview pixels and settings without leaving the library',async({page},info)=>{
  const room=await boot(page);await start(room,'Knot Foundry');const first=await recipe(page,room);await warm(room);
  await preview(room,'Crystal Vault');await previewSettings(room);await room.getByLabel('Preview placement',{exact:true}).selectOption('add');
  await room.getByRole('button',{name:'Dice preview',exact:true}).click();
  await previewSettings(room);await room.getByLabel('Preview opacity',{exact:true}).fill('0.61');await room.getByLabel('Preview blend',{exact:true}).selectOption('screen');
  await seek(room);const audition=await pixels(room);expect(audition.colors).toBeGreaterThan(100);
  expect(await recipe(page,room)).toEqual(first);await keep(room);await expect(room.getByRole('button',{name:'Preview Crystal Vault',exact:true})).toBeFocused();await seek(room);expect(await pixels(room)).toEqual(audition);
  await expect(room.getByRole('tab',{name:'Templates',exact:true})).toHaveAttribute('aria-selected','true');
  const kept=await recipe(page,room);expect(kept.layers).toHaveLength(2);expect(kept.layers[0]).toEqual(first.layers[0]);
  expect(kept.layers[1]).toMatchObject({kind:'crystal-vault',opacity:.61,blend:'screen',enabled:true,locked:false});expect(kept.layers[1].id).not.toBe(first.layers[0].id);
  await room.getByRole('button',{name:'Layer 2: Crystal Vault',exact:true}).click();
  await expect(room.getByRole('tabpanel',{name:'Layers',exact:true})).toBeVisible();
  await expect(room.getByRole('button',{name:'Select Crystal Vault layer',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(room.getByLabel('Opacity',{exact:true})).toHaveValue('0.61');
  await undo(room);expect(await recipe(page,room)).toEqual(first);await undo(room,true);expect(await recipe(page,room)).toEqual(kept);
  await seek(room);expect(await pixels(room)).toEqual(audition);
  await fs.writeFile(info.outputPath('exact-kept-preview.json'),JSON.stringify({first,kept,pixels:audition},null,2));
});

test('audition suspends solo only for comparison and replacement Undo restores the selected held layer',async({page})=>{
  const room=await boot(page);await room.getByRole('button',{name:'Layer 2: Petal Engine',exact:true}).click();
  await room.locator('details.art-layer-options > summary').click();
  await room.getByRole('button',{name:'Lock Petal Engine dice',exact:true}).click();await room.getByRole('button',{name:'Solo Petal Engine layer',exact:true}).click();
  await room.getByRole('button',{name:'Disable Contour Atlas layer',exact:true}).click();
  const held=await recipe(page,room);expect(held.soloId).toBe(held.layers[1].id);await warm(room);const solo=await pixels(room);
  await preview(room,'Tidal Surface');await seek(room);expect((await pixels(room)).hash).not.toBe(solo.hash);expect(await recipe(page,room)).toEqual(held);
  await room.getByRole('button',{name:'Dismiss preview',exact:true}).click();await seek(room);expect(await pixels(room)).toEqual(solo);
  await preview(room,'Tidal Surface');await previewSettings(room);await room.getByLabel('Preview placement',{exact:true}).selectOption('replace');await seek(room);const replacePreview=await pixels(room);
  await keep(room);await seek(room);expect(await pixels(room)).toEqual(replacePreview);
  const replaced=await recipe(page,room);expect(replaced.layers).toHaveLength(3);expect(replaced.soloId).toBeNull();
  expect(replaced.layers[0]).toEqual(held.layers[0]);expect(replaced.layers[2]).toEqual(held.layers[2]);expect(replaced.layers[1].kind).toBe('wave-surface');expect(replaced.layers[1].id).not.toBe(held.layers[1].id);
  await undo(room);expect(await recipe(page,room)).toEqual(held);await seek(room);expect(await pixels(room)).toEqual(solo);
  await room.getByRole('tab',{name:/^Layers/}).click();await expect(room.getByRole('button',{name:'Select Petal Engine layer',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(room.getByRole('button',{name:'Dice selected layer',exact:true})).toBeDisabled();
  await undo(room,true);expect(await recipe(page,room)).toEqual(replaced);
});

test('audition, kept draft and Studio Apply have separate portable project boundaries and preserve originals',async({page},info)=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(URL);
  await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles([path.resolve('tests/fixtures/img_a.jpg'),path.resolve('tests/fixtures/img_b.jpg')]);
  await expect(page.getByTestId('studio-artwork')).toBeVisible();const original=await archive(page,info.outputPath('imported-originals.collage'));const owned=await originals(original);
  let room=await openRoom(page);await start(room,'Knot Foundry');await preview(room,'Crystal Vault');await keep(room);
  const first=await recipe(page,room);expect(first.layers.map((l:any)=>l.kind)).toEqual(['torus-knot','crystal-vault']);await applied(room);await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
  const firstArchive=await archive(page,info.outputPath('kept-two-layers.collage'));expect(firstArchive.manifest.images).toHaveLength(3);const firstArt=firstArchive.manifest.images.find((i:any)=>i.art);expect(firstArt.art).toEqual(first);
  room=await openRoom(page);await preview(room,'Stellar Passage');await expect(room.locator('.art-studio-pending')).toBeDisabled();expect(await recipe(page,room)).toEqual(first);
  await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
  const browsed=await archive(page,info.outputPath('unkept-preview-excluded.collage'));expect(browsed.manifest.images).toEqual(firstArchive.manifest.images);expect(await originals(browsed)).toEqual(await originals(firstArchive));
  room=await openRoom(page);await expect(room.getByTestId('art-audition')).toHaveCount(0);await preview(room,'Stellar Passage');await keep(room);const draft=await recipe(page,room);expect(draft.layers).toHaveLength(3);
  await room.getByRole('button',{name:'Close Art Room',exact:true}).click();const unapplied=await archive(page,info.outputPath('kept-draft-not-applied.collage'));expect(unapplied.manifest.images).toEqual(firstArchive.manifest.images);expect(await originals(unapplied)).toEqual(await originals(firstArchive));
  room=await openRoom(page);await applied(room,true);await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
  const finalPath=info.outputPath('kept-three-layers-applied.collage'),finalArchive=await archive(page,finalPath);const finalArt=finalArchive.manifest.images.find((i:any)=>i.art);
  expect(finalArchive.manifest.images).toHaveLength(3);expect(finalArt.id).not.toBe(firstArt.id);expect(finalArt.art).toEqual(draft);
  expect((await originals(finalArchive)).filter(i=>owned.some(o=>o.id===i.id))).toEqual(owned);
  await page.reload();const chooser=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Open',exact:true}).click();await(await chooser).setFiles(finalPath);await expect(page.getByTestId('studio-artwork')).toBeVisible();
  room=await openRoom(page);await settings(room);await room.getByLabel('Editing artwork',{exact:true}).selectOption(finalArt.id);expect(await recipe(page,room)).toEqual(draft);
  await expect(room.getByRole('button',{name:'Undo art edit',exact:true})).toBeDisabled();expect(errors).toEqual([]);
  await info.attach('portable-kept-project',{path:finalPath,contentType:'application/octet-stream'});
});

test('keyboard Keep restores a visible focus target in full preview and after filtering away its template',async({page})=>{
  const room=await boot(page);const untouched=await recipe(page,room);
  await preview(room,'Crystal Vault');await previewSettings(room);await room.getByLabel('Preview opacity',{exact:true}).fill('0.41');
  await room.getByLabel('Preview opacity',{exact:true}).focus();await page.keyboard.press('Control+z');
  await expect(room.getByTestId('art-audition')).toHaveCount(0);await expect(room.getByRole('button',{name:'Preview Crystal Vault',exact:true})).toBeFocused();
  expect(await recipe(page,room)).toEqual(untouched);await expect(room.getByRole('button',{name:'Undo art edit',exact:true})).toBeDisabled();
  await preview(room,'Crystal Vault');await room.getByRole('button',{name:'Expand art preview',exact:true}).click();
  await room.getByRole('button',{name:'Keep layer',exact:true}).focus();await page.keyboard.press('Enter');
  await expect(room.getByTestId('art-audition')).toHaveCount(0);await expect(room.getByRole('button',{name:'Back to editing',exact:true})).toBeFocused();
  await room.getByRole('button',{name:'Back to editing',exact:true}).click();expect((await recipe(page,room)).layers).toHaveLength(4);
  await preview(room,'Knot Foundry');await room.getByLabel('Template family',{exact:true}).selectOption('Fields');
  await expect(room.getByRole('button',{name:'Preview Knot Foundry',exact:true})).toHaveCount(0);
  await room.getByRole('button',{name:'Keep layer',exact:true}).focus();await page.keyboard.press('Enter');
  await expect(room.getByTestId('art-audition')).toHaveCount(0);await expect(room.getByLabel('Template family',{exact:true})).toBeFocused();
  const kept=await recipe(page,room);expect(kept.layers).toHaveLength(5);expect(kept.layers.at(-1).kind).toBe('torus-knot');
});

// Hold one real PNG encoder completion, rather than fabricating an app result.
// The fallback releases in 15s and each case also releases in finally.
async function holdApply(page:Page){
  await page.evaluate(()=>{
    const native=HTMLCanvasElement.prototype.toBlob;
    let deliver:(()=>void)|undefined,released=false;
    const gate={entered:false,timedOut:false,release:()=>{released=true;clearTimeout(timer);HTMLCanvasElement.prototype.toBlob=native;deliver?.();deliver=undefined;}};
    const timer=setTimeout(()=>{gate.timedOut=true;gate.release();},15_000);
    (window as any).__artApplyGate=gate;
    HTMLCanvasElement.prototype.toBlob=function(callback,type,quality){
      HTMLCanvasElement.prototype.toBlob=native;gate.entered=true;
      native.call(this,blob=>{if(released)callback(blob);else deliver=()=>callback(blob);},type,quality);
    };
  });
}
async function releaseApply(page:Page){await page.evaluate(()=>{(window as any).__artApplyGate?.release();});}

test('pending Apply protects workspace navigation and a completion after Close cannot replace saved art',async({page},info)=>{
  let room=await boot(page);const first=await recipe(page,room);
  await holdApply(page);
  try{
    await room.getByRole('button',{name:'Use in Studio',exact:true}).click();
    await expect.poll(()=>page.evaluate(()=>(window as any).__artApplyGate.entered)).toBe(true);
    await expect(room.getByRole('button',{name:'Applying…',exact:true})).toBeDisabled();
    for(const name of ['Templates',/^Layers/])await expect(room.getByRole('tab',{name})).toBeDisabled();
    await expect(room.getByRole('button',{name:'Layer 1: Contour Atlas',exact:true})).toBeDisabled();
    await expect(room.getByRole('button',{name:'Browse for layer 4',exact:true})).toBeDisabled();
    await expect(room.getByRole('button',{name:'Preview Knot Foundry',exact:true})).toBeDisabled();
    await releaseApply(page);
    await expect(room.locator('.art-footer [role=status]')).toContainText('Editable artwork applied',{timeout:30_000});
    expect(await page.evaluate(()=>(window as any).__artApplyGate.timedOut)).toBe(false);
  }finally{await releaseApply(page);}
  await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
  const saved=await archive(page,info.outputPath('pending-apply-completed.collage'));expect(saved.manifest.images).toHaveLength(1);expect(saved.manifest.images[0].art).toEqual(first);
  room=await openRoom(page);await preview(room,'Stellar Passage');await keep(room);const edited=await recipe(page,room);expect(edited.layers).toHaveLength(4);
  await holdApply(page);
  try{
    await room.getByRole('button',{name:'Update in Studio',exact:true}).click();await expect.poll(()=>page.evaluate(()=>(window as any).__artApplyGate.entered)).toBe(true);
    await room.getByRole('button',{name:'Close Art Room',exact:true}).click();await releaseApply(page);
    // A completed old callback must not commit, even after the next room opens.
    room=await openRoom(page);await expect(room.getByRole('button',{name:'Update in Studio',exact:true})).toBeEnabled();expect(await recipe(page,room)).toEqual(edited);
    await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
    const stale=await archive(page,info.outputPath('closed-apply-refused.collage'));expect(stale.manifest.images).toEqual(saved.manifest.images);expect(await originals(stale)).toEqual(await originals(saved));
    expect(await page.evaluate(()=>(window as any).__artApplyGate.timedOut)).toBe(false);
  }finally{await releaseApply(page);}
});

async function reachable(control:Locator,viewport:{width:number;height:number}){
  await control.scrollIntoViewIfNeeded();const geometry=await control.evaluate(e=>{const r=e.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return{label:e.getAttribute('aria-label')||e.textContent,x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,hit:hit===e||e.contains(hit),interceptor:hit?.outerHTML.slice(0,250)};});
  const reason=JSON.stringify({viewport,...geometry});
  try{
    expect(geometry.w,reason).toBeGreaterThanOrEqual(43.5);expect(geometry.h,reason).toBeGreaterThanOrEqual(43.5);expect(geometry.x,reason).toBeGreaterThanOrEqual(0);expect(geometry.y,reason).toBeGreaterThanOrEqual(0);expect(geometry.right,reason).toBeLessThanOrEqual(viewport.width+1);expect(geometry.bottom,reason).toBeLessThanOrEqual(viewport.height+1);expect(geometry.hit,reason).toBe(true);
  }catch(error){await control.page().screenshot({path:test.info().outputPath(`blocked-${viewport.width}-${viewport.height}.png`)});throw error;}
}

test('horizontal library and audition actions remain reachable from 320px phones through short landscape',async({page},info)=>{
  for(const viewport of [{width:320,height:664},{width:360,height:780},{width:390,height:844},{width:844,height:390},{width:320,height:448}]){
    await page.setViewportSize(viewport);const room=await boot(page);const gallery=room.locator('.art-gallery');
    const horizontal=await gallery.evaluate(e=>({client:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX}));expect(horizontal.scroll).toBeGreaterThan(horizontal.client);expect(['auto','scroll']).toContain(horizontal.overflow);
    await reachable(room.getByRole('button',{name:'Preview Tidal Surface',exact:true}),viewport);await room.getByRole('button',{name:'Preview Tidal Surface',exact:true}).click();
    await expect(room.getByTestId('art-audition')).toBeVisible();
    await page.screenshot({path:info.outputPath(`audition-${viewport.width}-${viewport.height}.png`)});
    for(const name of ['Dismiss preview','Keep layer','Dice preview'])await reachable(room.getByRole('button',{name,exact:true}),viewport);
    await previewSettings(room);await reachable(room.getByLabel('Preview placement',{exact:true}),viewport);await reachable(room.getByLabel('Preview blend',{exact:true}),viewport);
    await previewSettings(room);await room.getByLabel('Preview opacity',{exact:true}).fill('0.57');await room.getByLabel('Preview blend',{exact:true}).selectOption('screen');
    await reachable(room.getByRole('button',{name:'Keep layer',exact:true}),viewport);await keep(room);
    await expect(room.getByRole('tab',{name:'Templates',exact:true})).toHaveAttribute('aria-selected','true');
    const selected=room.getByRole('button',{name:'Layer 4: Tidal Surface',exact:true});await reachable(selected,viewport);await selected.click();await expect(room.getByLabel('Opacity',{exact:true})).toHaveValue('0.57');
    await expect(room.getByRole('button',{name:'Select Tidal Surface layer',exact:true})).toHaveAttribute('aria-pressed','true');
    expect(await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
    const frame=await room.getByLabel('Animated art preview',{exact:true}).boundingBox();expect(frame!.height).toBeGreaterThanOrEqual(viewport.height<530?60:140);
    await page.screenshot({path:info.outputPath(`kept-layer-${viewport.width}-${viewport.height}.png`)});
    await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
  }
});
