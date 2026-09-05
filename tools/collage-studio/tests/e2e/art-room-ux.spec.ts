// Author: Aldrin Payopay · GPL-3.0-only
// Real UI checks for large, fully fitted artwork and controls revealed by intent.
import { test, expect, type Locator, type Page } from '@playwright/test';
import fs from 'node:fs/promises';

test.use({ actionTimeout: 15_000 });
async function openRoom(page: Page) {
  await page.goto(process.env.COLLAGE_BASE_URL || '/');
  await page.getByRole('button', { name: 'Art Room', exact: true }).click();
  const room=page.getByTestId('art-rack');
  await expect(room).toBeVisible();
  return room;
}
async function reveal(settings: Locator) {
  if(await settings.getAttribute('open')===null)await settings.locator(':scope > summary').click();
}
async function recipe(page: Page,room: Locator) {
  await reveal(room.locator('details.art-project-settings'));
  const download=page.waitForEvent('download');
  await room.getByRole('button',{name:'Save recipe',exact:true}).click();
  return JSON.parse(await fs.readFile((await (await download).path())!,'utf8'));
}
async function frame(room: Locator) {
  // Canvas object-fit letterboxing is intentional: compare the actual fitted
  // artwork bounds, not just the canvas element's possibly larger CSS box.
  return room.getByLabel('Animated art preview',{exact:true}).evaluate((canvas:HTMLCanvasElement)=>{
    const box=canvas.getBoundingClientRect(),ratio=canvas.width/canvas.height;
    const width=Math.min(box.width,box.height*ratio),height=width/ratio;
    return {x:box.x+(box.width-width)/2,y:box.y+(box.height-height)/2,width,height,ratio,
      fit:getComputedStyle(canvas).objectFit};
  });
}
async function hittable(control:Locator) {
  const box=await control.evaluate(e=>{const b=e.getBoundingClientRect();const at=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return {width:b.width,height:b.height,hit:at===e||e.contains(at)};});
  expect(box.width).toBeGreaterThanOrEqual(43.5);expect(box.height).toBeGreaterThanOrEqual(43.5);expect(box.hit).toBe(true);
}

test('whole artwork and playback remain available in portrait, short landscape and desktop focus views',async({page},info)=>{
  test.setTimeout(90_000);
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  for(const viewport of [{width:390,height:844},{width:844,height:390},{width:1280,height:720}]){
    await page.setViewportSize(viewport);
    const room=await openRoom(page);
    const expanded=room.getByRole('button',{name:'Expand art preview',exact:true});
    const before=await frame(room);
    expect(before.fit).toBe('contain');
    expect(before.width).toBeGreaterThan(290);expect(before.height).toBeGreaterThan(180);
    await hittable(expanded);await expanded.click();
    await expect(room.getByRole('region',{name:'Art controls',exact:true})).toBeHidden();
    await expect(room.getByRole('button',{name:'Back to editing',exact:true})).toBeFocused();
    const fitted=await frame(room);
    expect(fitted.width*fitted.height).toBeGreaterThanOrEqual(before.width*before.height*.99);
    expect(fitted.x).toBeGreaterThanOrEqual(0);expect(fitted.y).toBeGreaterThanOrEqual(0);
    expect(fitted.x+fitted.width).toBeLessThanOrEqual(viewport.width+1);
    expect(fitted.y+fitted.height).toBeLessThanOrEqual(viewport.height+1);
    await hittable(room.getByRole('button',{name:'Add artwork',exact:true}));
    const pause=room.getByRole('button',{name:'Pause art preview',exact:true});
    if(await pause.isVisible())await pause.click();
    await room.getByLabel('Art playhead',{exact:true}).fill('2.25');
    await expect(room.locator('.art-transport output')).toHaveText('2.3 / 8s');
    await page.screenshot({path:info.outputPath(`art-focus-${viewport.width}-${viewport.height}.png`)});
    await page.keyboard.press('Escape');
    await expect(room).toBeVisible();await expect(expanded).toBeFocused();
    await expect(room.getByRole('tab',{name:'Templates',exact:true})).toHaveAttribute('aria-selected','true');
    await expect(room.getByLabel('Art playhead',{exact:true})).toHaveValue('2.25');
    await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
  }
  expect(errors).toEqual([]);
});

test('layer editing reveals look, motion and recipe tools without losing recipe history',async({page})=>{
  test.setTimeout(60_000);
  const room=await openRoom(page);
  await expect(room.getByLabel('Editing artwork',{exact:true})).toBeHidden();
  await expect(room.getByRole('button',{name:'Undo art edit',exact:true})).toBeHidden();
  await room.getByRole('button',{name:'Add Woven Circuit',exact:true}).click();
  await expect(room.getByRole('tab',{name:'Look',exact:true})).toHaveAttribute('aria-selected','true');
  await expect(room.getByRole('button',{name:'Disable Woven Circuit layer',exact:true})).toBeVisible();
  await expect(room.getByRole('button',{name:'Solo Woven Circuit layer',exact:true})).toBeHidden();
  await expect(room.getByLabel('Automation target',{exact:true})).toHaveCount(0);
  await room.getByLabel('Layer palette',{exact:true}).selectOption('ember');
  await room.getByLabel('Opacity',{exact:true}).fill('0.65');
  await reveal(room.locator('details.art-layer-options'));
  await room.getByRole('button',{name:'Lock Woven Circuit dice',exact:true}).click();
  await expect(room.getByRole('button',{name:'Dice layer',exact:true})).toBeDisabled();
  await room.getByRole('tab',{name:'Motion',exact:true}).click();
  await expect(room.getByLabel('Layer palette',{exact:true})).toHaveCount(0);
  await room.getByLabel('Automation target',{exact:true}).selectOption('rotation');
  await room.getByLabel('Automation amount',{exact:true}).fill('0.4');
  await expect(room.getByLabel('Automation cycles',{exact:true})).toBeHidden();
  await room.getByText('Motion timing',{exact:true}).click();
  await room.getByLabel('Automation cycles',{exact:true}).selectOption('3');
  await room.getByLabel('Automation phase',{exact:true}).fill('0.25');
  const changed=await recipe(page,room),woven=changed.layers.find((l:any)=>l.kind==='weave');
  expect(woven).toMatchObject({palette:'ember',opacity:.65,locked:true,automation:{target:'rotation',amount:.4,cycles:3,phase:.25}});
  await room.getByRole('button',{name:'Undo art edit',exact:true}).click();
  const undone=await recipe(page,room);
  expect(undone.layers.find((l:any)=>l.id===woven.id).automation.phase).not.toBe(.25);
  await room.getByRole('button',{name:'Redo art edit',exact:true}).click();
  expect(await recipe(page,room)).toEqual(changed);
  await room.getByRole('button',{name:'Add another template',exact:true}).click();
  await expect(room.getByRole('tab',{name:'Templates',exact:true})).toHaveAttribute('aria-selected','true');
  expect(await room.locator('.art-gallery .art-template').count()).toBe(8);
});

test('portrait and wide recipes fit fully in the focus view without cropping',async({page})=>{
  await page.setViewportSize({width:844,height:390});
  const room=await openRoom(page);
  for(const size of ['portrait','wide']){
    await reveal(room.locator('details.art-project-settings'));
    await room.getByLabel('Art canvas size',{exact:true}).selectOption(size);
    await room.getByRole('button',{name:'Expand art preview',exact:true}).click();
    const fitted=await frame(room);
    expect(fitted.ratio).toBeCloseTo(size==='portrait'?1080/1920:1920/1080,2);
    expect(fitted.height).toBeGreaterThan(200);
    expect(fitted.y).toBeGreaterThanOrEqual(44);
    expect(fitted.y+fitted.height).toBeLessThan(390-90);
    await expect(room.getByLabel('Art playhead',{exact:true})).toBeVisible();
    await room.getByRole('button',{name:'Back to editing',exact:true}).click();
  }
});
