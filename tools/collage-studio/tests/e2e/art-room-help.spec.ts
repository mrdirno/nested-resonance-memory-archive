// Author: Aldrin Payopay · GPL-3.0-only
// C3724 — the Art Room's top bar (Undo · Redo · Help), the instrument line on the stage,
// one-tap dice targets and the help card. Real dialogs, real focus, no mocks.
// Run: npx playwright test tests/e2e/art-room-help.spec.ts --project=chromium --project='Mobile Chrome' --project='Mobile Safari' --workers=1
import {test,expect,type Page,type Locator} from '@playwright/test';
import fs from 'node:fs/promises';

test.setTimeout(120_000);
const URL=process.env.COLLAGE_BASE_URL||'/';
const DESCRIPTION={'Knot Foundry':'A sculpted tube weaves through a lit three-dimensional knot.','Petal Engine':'Nested geometric petals opening around a quiet center.'} as const;
const WIDTHS=[320,360,390,430];

async function openRoom(page:Page){await page.goto(URL);const b=page.getByRole('button',{name:'Art Room',exact:true});if(!await b.isVisible())await page.getByRole('button',{name:'Add',exact:true}).click();await b.click();const room=page.getByTestId('art-rack');await expect(room).toBeVisible();return room;}
async function recipe(page:Page,room:Locator){const d=room.locator('details.art-project-settings');if(await d.getAttribute('open')===null)await d.locator(':scope > summary').click();const download=page.waitForEvent('download');await room.getByRole('button',{name:'Save recipe',exact:true}).click();const json=JSON.parse(await fs.readFile((await(await download).path())!,'utf8'));await d.locator(':scope > summary').click();return json;}
async function preview(room:Locator,name:string){await room.getByRole('tab',{name:'Templates',exact:true}).click();await room.getByRole('button',{name:`Preview ${name}`,exact:true}).click();await expect(room.getByTestId('art-audition')).toBeVisible();}
async function keep(room:Locator){await room.getByRole('button',{name:/^Keep layer/}).click();await expect(room.getByTestId('art-audition')).toHaveCount(0);}
const status=(room:Locator)=>room.locator('.art-footer [role=status]');
const undoButton=(room:Locator)=>room.getByRole('button',{name:'Undo art edit',exact:true});
const redoButton=(room:Locator)=>room.getByRole('button',{name:'Redo art edit',exact:true});
const helpButton=(room:Locator)=>room.getByRole('button',{name:'Help and report',exact:true});
const focusable=()=>test.info().project.name==='chromium'; // WebKit does not move focus to a tapped button; Chromium does.
async function box(l:Locator){await l.scrollIntoViewIfNeeded();const b=await l.boundingBox();expect(b,'control is rendered').not.toBeNull();return b!;}

test('the top bar holds Undo, Redo, Help and Close at 44px inside every phone width, default and bumped text',async({page},info)=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const width of WIDTHS){
  await page.setViewportSize({width,height:664});const room=await openRoom(page);
  for(const bumped of [false,true]){
   if(bumped)await page.addStyleTag({content:'.art-rack{font-size:18px}.art-header h2{font-size:26px}'});
   const names=['Undo art edit','Redo art edit','Help and report','Close Art Room'];let previousRight=0;
   for(const name of names){
    const b=await box(room.getByRole('button',{name,exact:true}));
    expect(b.width,`${name} width at ${width}${bumped?' bumped':''}`).toBeGreaterThanOrEqual(43.5);expect(b.height,`${name} height`).toBeGreaterThanOrEqual(43.5);
    expect(b.x,`${name} left edge`).toBeGreaterThanOrEqual(previousRight-0.5);expect(b.x+b.width,`${name} right edge at ${width}`).toBeLessThanOrEqual(width+0.5);previousRight=b.x+b.width;
   }
   const title=await box(room.getByRole('heading',{name:'Art Room',exact:true}));expect(title.width).toBeGreaterThan(30);
   const over=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);expect(over,`sideways scroll at ${width}`).toBeLessThanOrEqual(0);
   for(const name of ['Dice art',/^Dice layer/,/in Studio$/] as const){const b=await box(room.getByRole('button',{name}));expect(b.height).toBeGreaterThanOrEqual(43.5);expect(b.width).toBeGreaterThanOrEqual(43.5);expect(b.x).toBeGreaterThanOrEqual(-0.5);expect(b.x+b.width).toBeLessThanOrEqual(width+0.5);}
   const footer=await box(room.locator('.art-footer'));expect(footer.y+footer.height).toBeLessThanOrEqual(664.5);
  }
  await page.screenshot({path:info.outputPath(`art-top-bar-${width}.png`)});
  await room.getByRole('button',{name:'Close Art Room',exact:true}).click();
 }
 expect(errors).toEqual([]);
});

test('Undo is one tap in the top bar and names the step it took back; Redo puts it back; sliders count',async({page})=>{
 const room=await openRoom(page);
 await expect(undoButton(room)).toBeVisible();await expect(undoButton(room)).toBeDisabled();await expect(redoButton(room)).toBeDisabled();
 await preview(room,'Knot Foundry');await keep(room);
 await expect(room.getByRole('button',{name:'Layer 4: Knot Foundry',exact:true})).toBeVisible();
 const kept=await recipe(page,room);expect(kept.layers.map((l:any)=>l.kind)).toContain('torus-knot');
 await undoButton(room).click();
 await expect(status(room)).toHaveText('Undid: Keep Knot Foundry as layer 4.');
 await expect(room.getByRole('button',{name:'Layer 4: Knot Foundry',exact:true})).toHaveCount(0);
 await expect(undoButton(room)).toBeDisabled();await expect(redoButton(room)).toBeEnabled();
 if(focusable())await expect(redoButton(room)).toBeFocused(); // the finger's button went dark; focus went to its partner, not <body>
 await redoButton(room).click();
 await expect(status(room)).toHaveText('Redid: Keep Knot Foundry as layer 4.');
 expect(await recipe(page,room)).toEqual(kept);
 await room.getByRole('tab',{name:/^Layers/}).click();await room.getByRole('button',{name:'Select Knot Foundry layer',exact:true}).click();
 await room.getByLabel('Opacity',{exact:true}).fill('0.42');
 await undoButton(room).click();await expect(status(room)).toHaveText('Undid: Opacity on Knot Foundry.');
 expect(await recipe(page,room)).toEqual(kept);
 // The old doors are gone: no scope select, no Undo inside Canvas & recipe.
 await expect(room.getByLabel('Dice scope',{exact:true})).toHaveCount(0);
 await expect(room.locator('details.art-project-settings').getByRole('button',{name:/undo/i})).toHaveCount(0);
});

test('Dice layer and Dice art each roll their own target in one tap, and the stage says which',async({page})=>{
 const room=await openRoom(page);
 await expect(room.getByRole('button',{name:'Dice art',exact:true})).toBeEnabled();
 await room.getByRole('tab',{name:/^Layers/}).click();await room.getByRole('button',{name:'Select Petal Engine layer',exact:true}).click();
 const layerDice=room.getByRole('button',{name:'Dice layer: Petal Engine',exact:true});await expect(layerDice).toBeEnabled();
 const before=await recipe(page,room);const rosette=before.layers.find((l:any)=>l.kind==='rosette').id;
 await layerDice.click();
 await expect(status(room)).toHaveText('Petal Engine variation rolled.');await expect(room.getByTestId('art-scope-context')).toContainText('Layer: Petal Engine');
 const afterLayer=await recipe(page,room);
 for(const l of before.layers)if(l.id!==rosette)expect(afterLayer.layers.find((n:any)=>n.id===l.id)).toEqual(l);
 expect(afterLayer.layers.find((l:any)=>l.id===rosette)).not.toEqual(before.layers.find((l:any)=>l.id===rosette));
 await room.getByRole('button',{name:'Dice art',exact:true}).click();
 await expect(status(room)).toContainText('rolled');await expect(room.getByTestId('art-scope-context')).toContainText('Art composition');
 const afterArt=await recipe(page,room);
 for(const l of afterLayer.layers)if(l.enabled&&!l.locked)expect(afterArt.layers.find((n:any)=>n.id===l.id)).not.toEqual(l);
 await undoButton(room).click();await expect(status(room)).toHaveText('Undid: Dice art.');expect(await recipe(page,room)).toEqual(afterLayer);
 await undoButton(room).click();await expect(status(room)).toHaveText('Undid: Dice layer Petal Engine.');expect(await recipe(page,room)).toEqual(before);
});

test('the instrument\'s own sentence sits where the decision is made — the preview sheet, then the layer heading — and a held layer says why Dice layer is dark',async({page})=>{
 const room=await openRoom(page);const note=room.getByTestId('art-instrument-note');
 await expect(note).toHaveCount(0);
 const fresh=await box(room.getByLabel('Animated art preview',{exact:true})); // no notice, no sheet, no sentence
 await preview(room,'Knot Foundry');
 await expect(note).toHaveText(DESCRIPTION['Knot Foundry']);await expect(note).toHaveAttribute('data-state','preview');
 const sheet=await box(room.getByTestId('art-audition')),n=await box(note);expect(n.y).toBeGreaterThanOrEqual(sheet.y-0.5);expect(n.y+n.height).toBeLessThanOrEqual(sheet.y+sheet.height+0.5);
 // The sentence never taxes the artwork: previewing clears the footer notice, so fresh vs previewing isolates the sheet + sentence.
 const previewing=await box(room.getByLabel('Animated art preview',{exact:true}));expect(Math.abs(previewing.height-fresh.height)).toBeLessThanOrEqual(1);
 await room.getByRole('button',{name:'Dismiss preview',exact:true}).click();await expect(note).toHaveCount(0);
 await preview(room,'Knot Foundry');await keep(room);
 await expect(room.getByRole('button',{name:'Dice layer: Knot Foundry',exact:true})).toBeEnabled();
 await room.getByRole('tab',{name:/^Layers/}).click();
 await expect(note).toHaveText(DESCRIPTION['Knot Foundry']);await expect(note).toHaveAttribute('data-state','layer');
 await room.locator('details.art-layer-options > summary').click();
 await room.getByRole('button',{name:'Lock Knot Foundry dice',exact:true}).click();
 await expect(note).toHaveAttribute('data-state','held');await expect(note).toContainText('Knot Foundry is held');
 await expect(room.getByTestId('art-scope-context')).toContainText('Layer: Knot Foundry · held');
 await expect(room.getByRole('button',{name:'Dice layer: Knot Foundry',exact:true})).toBeDisabled();
 await room.getByRole('button',{name:'Unlock Knot Foundry dice',exact:true}).click();await expect(note).toHaveAttribute('data-state','layer');await expect(room.getByTestId('art-scope-context')).toHaveText(/Layer: Knot Foundry(?! ·)/);
 await room.getByRole('button',{name:'Disable Knot Foundry layer',exact:true}).click();
 await expect(note).toHaveAttribute('data-state','off');await expect(room.getByTestId('art-scope-context')).toContainText('Layer: Knot Foundry · off');await expect(room.getByRole('button',{name:'Dice layer: Knot Foundry',exact:true})).toBeDisabled();
 await room.getByRole('button',{name:'Select Petal Engine layer',exact:true}).click();await expect(note).toHaveText(DESCRIPTION['Petal Engine']);
});

test('the help card opens from the top bar, Escape and the backdrop close only the card, and the room keeps its work',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const room=await openRoom(page);await preview(room,'Knot Foundry');await keep(room);
 const card=room.getByRole('dialog',{name:'How the Art Room works',exact:true});
 await expect(card).toBeHidden();
 await helpButton(room).click();await expect(card).toBeVisible();
 await expect(card.getByRole('listitem')).toHaveCount(4);
 await expect(card).toContainText('Dice art rolls every unlocked layer');await expect(card).toContainText('Undo takes any step back');
 await expect(card).toContainText('wished for by an anonymous Collage user');
 await expect(card.getByRole('button',{name:/Something wrong\? Report it/})).toBeVisible();
 if(focusable())await expect(card.getByRole('heading',{name:'How the Art Room works',exact:true})).toBeFocused();
 const keys=card.locator('details.art-help-keys');
 if(test.info().project.name.startsWith('Mobile'))await expect(keys).toBeHidden();else await expect(keys).toBeVisible();
 const b=await box(card.getByRole('button',{name:'Close help',exact:true}));expect(b.width).toBeGreaterThanOrEqual(43.5);expect(b.height).toBeGreaterThanOrEqual(43.5);
 await page.keyboard.press('Escape');
 await expect(card).toBeHidden();await expect(room).toBeVisible();
 await expect(room.getByRole('button',{name:'Layer 4: Knot Foundry',exact:true})).toBeVisible();
 if(focusable())await expect(helpButton(room)).toBeFocused();
 await helpButton(room).click();await expect(card).toBeVisible();
 await page.mouse.click(4,4);await expect(card).toBeHidden();await expect(room).toBeVisible();
 await helpButton(room).click();await expect(card).toBeVisible();
 await card.getByRole('button',{name:'Close help',exact:true}).click();await expect(card).toBeHidden();await expect(room).toBeVisible();
 await page.keyboard.press('Escape');await expect(room).toBeHidden(); // Escape with no card up still closes the room, as before
 expect(errors).toEqual([]);
});
