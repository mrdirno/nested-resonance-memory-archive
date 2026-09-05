// Ring C3713: selecting a template is replacement; addition needs explicit intent.
// Author: Aldrin Payopay · GPL-3.0-only
import {test,expect,type Page,type Locator} from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import JSZip from 'jszip';
import {createHash} from 'node:crypto';

test.setTimeout(120_000);
const URL=process.env.COLLAGE_BASE_URL||'/';
async function settings(room:Locator){const d=room.locator('details.art-project-settings');if(await d.getAttribute('open')===null)await d.locator(':scope > summary').click();}
async function recipe(page:Page,room:Locator){await settings(room);const download=page.waitForEvent('download');await room.getByRole('button',{name:'Save recipe',exact:true}).click();return JSON.parse(await fs.readFile((await(await download).path())!,'utf8'));}
async function openRoom(page:Page){const b=page.getByRole('button',{name:'Art Room',exact:true});if(!await b.isVisible())await page.getByRole('button',{name:'Add',exact:true}).click();await b.click();return page.getByTestId('art-rack');}
async function boot(page:Page){await page.goto(URL);return openRoom(page);}
async function templates(room:Locator){await room.getByRole('tab',{name:'Templates',exact:true}).click();}
async function layers(room:Locator){await room.getByRole('tab',{name:/^Layers/}).click();}
async function use(room:Locator,name:string){await templates(room);await room.getByRole('button',{name:`Use ${name}`,exact:true}).click();}
async function undo(room:Locator,redo=false){await settings(room);await room.getByRole('button',{name:redo?'Redo art edit':'Undo art edit',exact:true}).click();}
async function archive(page:Page){await page.getByRole('button',{name:'Open',exact:true}).focus();const download=page.waitForEvent('download');await page.keyboard.press('Control+s');const p=(await(await download).path())!;const bytes=await fs.readFile(p);const zip=await JSZip.loadAsync(bytes);const manifest=JSON.parse(await zip.file('manifest.json')!.async('text'));return{zip,manifest,bytes};}
const hash=(v:Buffer)=>createHash('sha256').update(v).digest('hex');
async function originals(a:Awaited<ReturnType<typeof archive>>){return Promise.all(a.manifest.images.map(async(i:any)=>({id:i.id,name:i.originalName,hash:hash(await a.zip.file('images/'+i.storageFilename)!.async('nodebuffer'))})));}

test('Ring C3713 primary A then B replaces the stack in one undoable transaction',async({page},info)=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));const room=await boot(page);
 const original=await recipe(page,room);await room.getByLabel('Art canvas size',{exact:true}).selectOption('square');await room.getByLabel('Art loop duration',{exact:true}).selectOption('12');
 const canvas=await room.getByLabel('Animated art preview',{exact:true}).elementHandle();
 await use(room,'Contour Atlas');const a=await recipe(page,room);expect(a.layers.map((l:any)=>l.kind)).toEqual(['contour']);expect(a.size).toBe('square');expect(a.duration).toBe(12);expect(a.background).toBe(original.background);
 await use(room,'Prism Garden');const b=await recipe(page,room);expect(b.layers.map((l:any)=>l.kind)).toEqual(['facets']);expect(b.soloId).toBeNull();expect(b.layers[0].id).not.toBe(a.layers[0].id);
 expect(await canvas!.evaluate(el=>el===document.querySelector('canvas[aria-label="Animated art preview"]'))).toBe(true);
 await undo(room);expect(await recipe(page,room)).toEqual(a);await expect(room.getByLabel('Dice scope',{exact:true})).toHaveValue('composition');await layers(room);await expect(room.getByRole('button',{name:'Select Contour Atlas layer',exact:true})).toHaveAttribute('aria-pressed','true');
 await undo(room,true);expect(await recipe(page,room)).toEqual(b);await layers(room);await expect(room.getByRole('button',{name:'Select Prism Garden layer',exact:true})).toHaveAttribute('aria-pressed','true');
 await fs.writeFile(info.outputPath('template-replacement.json'),JSON.stringify({before:original,a,b},null,2));expect(errors).toEqual([]);
});

test('Ring C3713 explicit Add preserves siblings and replacement undo restores selected locks and solo',async({page})=>{
 const room=await boot(page);await use(room,'Contour Atlas');await layers(room);
 await room.locator('details.art-layer-options > summary').click();await room.getByRole('button',{name:'Lock Contour Atlas dice',exact:true}).click();await room.getByRole('button',{name:'Solo Contour Atlas layer',exact:true}).click();await room.getByRole('button',{name:'Disable Contour Atlas layer',exact:true}).click();
 const a=await recipe(page,room);await templates(room);await room.getByRole('button',{name:'Add Prism Garden',exact:true}).click();const added=await recipe(page,room);
 expect(added.layers.map((l:any)=>l.kind)).toEqual(['contour','facets']);expect(added.layers[0]).toEqual(a.layers[0]);expect(added.soloId).toBe(a.soloId);expect(new Set(added.layers.map((l:any)=>l.id)).size).toBe(2);
 await room.getByRole('button',{name:'Select Contour Atlas layer',exact:true}).click();await use(room,'Orbit Press');expect((await recipe(page,room)).layers.map((l:any)=>l.kind)).toEqual(['rings']);
 await undo(room);expect(await recipe(page,room)).toEqual(added);await layers(room);await expect(room.getByRole('button',{name:'Select Contour Atlas layer',exact:true})).toHaveAttribute('aria-pressed','true');await expect(room.getByRole('button',{name:'Dice selected layer',exact:true})).toBeDisabled();
 await undo(room,true);expect((await recipe(page,room)).layers.map((l:any)=>l.kind)).toEqual(['rings']);
 await undo(room);await layers(room);await expect(room.getByLabel('Opacity',{exact:true})).toBeEnabled();await room.getByLabel('Opacity',{exact:true}).fill('0.42');const edited=await recipe(page,room);expect(edited.layers[0]).toEqual({...added.layers[0],opacity:.42});expect(edited.layers[1]).toEqual(added.layers[1]);await expect(room.locator('.art-control-help')).toContainText('contour lines');
});

test('Ring C3713 dice scope mutates only its unlocked enabled target',async({page})=>{
 const room=await boot(page);await layers(room);await room.getByRole('button',{name:'Select Petal Engine layer',exact:true}).click();
 const before=await recipe(page,room);await room.getByRole('button',{name:'Dice selected layer',exact:true}).click();const after=await recipe(page,room);const id=before.layers.find((l:any)=>l.kind==='rosette').id;
 for(const l of before.layers)if(l.id!==id)expect(after.layers.find((n:any)=>n.id===l.id)).toEqual(l);
 expect(after.layers.find((l:any)=>l.id===id)).not.toEqual(before.layers.find((l:any)=>l.id===id));
 await room.locator('details.art-layer-options > summary').click();await room.getByRole('button',{name:'Lock Petal Engine dice',exact:true}).click();await room.getByRole('button',{name:'Disable Contour Atlas layer',exact:true}).click();const held=await recipe(page,room);
 await room.getByLabel('Dice scope',{exact:true}).selectOption('composition');await room.getByRole('button',{name:'Dice composition',exact:true}).click();const all=await recipe(page,room);
 for(const l of held.layers)if(l.locked||!l.enabled)expect(all.layers.find((n:any)=>n.id===l.id)).toEqual(l);
 expect(all.layers.find((l:any)=>l.kind==='particles')).not.toEqual(held.layers.find((l:any)=>l.kind==='particles'));
 await undo(room);expect(await recipe(page,room)).toEqual(held);
});

test('Ring C3713 browsing replacement does not rewrite existing art or imported originals before Apply',async({page})=>{
 await page.goto(URL);await page.locator('input[type=file][accept="image/*,video/*"]').setInputFiles([path.resolve('tests/fixtures/img_a.jpg'),path.resolve('tests/fixtures/img_b.jpg')]);await expect(page.getByTestId('studio-artwork')).toBeVisible();
 const before=await archive(page),owned=await originals(before);let room=await openRoom(page);const legacy=await recipe(page,room);expect(legacy.layers).toHaveLength(3);
 await room.getByRole('button',{name:'Add artwork',exact:true}).click();await expect(room.locator('.art-footer [role=status]')).toContainText('Editable artwork applied');await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
 const saved=await archive(page);const art=saved.manifest.images.find((i:any)=>i.art);expect(saved.manifest.images).toHaveLength(3);expect(art.art).toEqual(legacy);
 await page.reload();const chooser=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Open',exact:true}).click();await(await chooser).setFiles({name:'legacy-stacked.collage',mimeType:'application/octet-stream',buffer:saved.bytes});await expect(page.getByTestId('studio-artwork')).toBeVisible();
 room=await openRoom(page);await settings(room);await room.getByLabel('Editing artwork',{exact:true}).selectOption(art.id);expect(await recipe(page,room)).toEqual(legacy);
 await use(room,'Contour Atlas');await use(room,'Prism Garden');const replacement=await recipe(page,room);expect(replacement.layers.map((l:any)=>l.kind)).toEqual(['facets']);await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
 const untouched=await archive(page);expect(untouched.manifest.images.find((i:any)=>i.id===art.id).art).toEqual(legacy);expect(await originals(untouched)).toEqual(await originals(saved));
 room=await openRoom(page);await room.getByRole('button',{name:'Update artwork',exact:true}).click();await expect(room.locator('.art-footer [role=status]')).toContainText('Editable artwork applied');await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
 const applied=await archive(page);expect(applied.manifest.images).toHaveLength(3);const revised=applied.manifest.images.find((i:any)=>i.art);expect(revised.art).toEqual(replacement);expect(revised.id).not.toBe(art.id);expect((await originals(applied)).filter(i=>owned.some((o:any)=>o.id===i.id))).toEqual(owned);
});

test('Ring C3713 primary and Add remain separate reachable targets at narrow widths',async({page},info)=>{
 const room=await boot(page);
 for(const size of [{width:320,height:664},{width:390,height:844},{width:844,height:390}]){
  await page.setViewportSize(size);await templates(room);
  for(const label of ['Use Contour Atlas','Add Contour Atlas']){const control=room.getByRole('button',{name:label,exact:true});await control.scrollIntoViewIfNeeded();const b=await control.evaluate(e=>{const r=e.getBoundingClientRect();const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return{w:r.width,h:r.height,right:r.right,bottom:r.bottom,hit:hit===e||e.contains(hit)};});expect(b.w).toBeGreaterThanOrEqual(43.5);expect(b.h).toBeGreaterThanOrEqual(43.5);expect(b.right).toBeLessThanOrEqual(size.width);expect(b.bottom).toBeLessThanOrEqual(size.height);expect(b.hit).toBe(true);}
  const scope=room.getByLabel('Dice scope',{exact:true});const b=await scope.boundingBox();expect(b!.height).toBeGreaterThanOrEqual(43.5);expect(b!.x+b!.width).toBeLessThanOrEqual(size.width);
  await page.screenshot({path:info.outputPath(`template-intent-${size.width}.png`)});
 }
});


test('Ring C3713 a full eight-layer stack permits replacement while Add refuses a ninth',async({page})=>{
 const room=await boot(page);
 for(const name of ['Orbit Press','Ribbon Choir','Branch Fans','Prism Garden','Woven Circuit']){await templates(room);await room.getByRole('button',{name:`Add ${name}`,exact:true}).click();}
 const full=await recipe(page,room);expect(full.layers).toHaveLength(8);
 await templates(room);await room.getByRole('button',{name:'Add Contour Atlas',exact:true}).click();await expect(room.locator('.art-footer [role=status]')).toContainText('Eight layers');expect(await recipe(page,room)).toEqual(full);
 await use(room,'Prism Garden');expect((await recipe(page,room)).layers.map((l:any)=>l.kind)).toEqual(['facets']);await undo(room);expect(await recipe(page,room)).toEqual(full);
});
