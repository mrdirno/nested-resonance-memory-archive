import { test, expect, type Page } from '@playwright/test';
import { writeFile } from 'node:fs/promises';

const url = process.env.COLLAGE_BASE_URL || '/';
async function film(page: Page) {
  await page.goto(url);
  await page.getByRole('button', {name:'Try a lyric film',exact:true}).click();
  await expect(page.getByTestId('studio-artwork')).toBeVisible({timeout:60_000});
  await expect(page.getByTestId('video-transport')).toBeVisible();
}
async function dimensions(page: Page) {
  return page.getByTestId('studio-artwork').evaluate(el => {
    const art=el.getBoundingClientRect(), band=el.closest('[data-testid="studio-art-band"]')!.getBoundingClientRect();
    return {x:art.x,y:art.y,width:art.width,height:art.height,band:{x:band.x,y:band.y,right:band.right,bottom:band.bottom},right:art.right,bottom:art.bottom};
  });
}
async function fits(page: Page, minimum=100) {
  await expect.poll(async () => (await dimensions(page)).height).toBeGreaterThan(minimum);
  const d=await dimensions(page);
  expect(d.x).toBeGreaterThanOrEqual(d.band.x-1);expect(d.y).toBeGreaterThanOrEqual(d.band.y-1);
  expect(d.right).toBeLessThanOrEqual(d.band.right+1);expect(d.bottom).toBeLessThanOrEqual(d.band.bottom+1);
  return d;
}

test('start offers three clear creative paths without a disabled editing wall', async ({page}) => {
  await page.goto(url);
  await expect(page.getByRole('heading',{name:'Start a new piece'})).toBeVisible();
  for(const name of ['Art Room','Load source images or video','Try a lyric film']) {
    await expect(page.getByRole('button',{name,exact:true})).toBeVisible();
  }
  await expect(page.getByRole('navigation',{name:'Studio tools'})).toHaveCount(0);
  const count=await page.locator('button:visible').count();expect(count).toBeLessThanOrEqual(5);
  await page.getByRole('button',{name:'Art Room',exact:true}).click();
  await page.getByRole('button',{name:'Close Art Room',exact:true}).click();
  await expect(page.getByRole('button',{name:'Art Room',exact:true})).toBeFocused();
});

test('sample playback is fitted and large in desktop, portrait and short landscape', async ({page},info) => {
  test.setTimeout(90_000);
  await film(page);const measurements=[];
  for(const size of [{width:1280,height:720,min:400},{width:390,height:844,min:500},{width:844,height:390,min:140},{width:320,height:448,min:170}]) {
    await page.setViewportSize(size);
    const d=await fits(page,size.min);
    const buttons=await page.locator('button:visible').count();expect(buttons).toBeLessThanOrEqual(12);
    measurements.push({viewport:size,artwork:d,buttons});
    await page.screenshot({path:info.outputPath(`studio-preview-${size.width}-${size.height}.png`)});
  }
  await writeFile(info.outputPath('preview-dimensions.json'), JSON.stringify(measurements,null,2));
  await info.attach('preview-dimensions',{body:JSON.stringify(measurements,null,2),contentType:'application/json'});
});

test('editing tasks and playback details are exclusive and preserve the parked canvas', async ({page}) => {
  await film(page);
  const canvas=await page.getByTestId('studio-artwork').locator('canvas').elementHandle();
  await page.getByLabel(/^Playhead/).fill('2.5');
  const tools=page.getByRole('navigation',{name:'Studio tools'});
  await tools.getByRole('button',{name:'Layout',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Shape your composition'})).toBeVisible();
  await expect(page.getByTestId('move-drift')).not.toBeVisible();
  await page.getByRole('button',{name:'Details',exact:true}).click();
  await expect(page.getByRole('complementary',{name:'Editing panel'})).not.toBeVisible();
  await expect(page.getByRole('button',{name:'Record video',exact:true})).toBeVisible();
  await tools.getByRole('button',{name:'Motion',exact:true}).click();
  await expect(page.getByRole('button',{name:'Details',exact:true})).toHaveAttribute('aria-expanded','false');
  await expect(page.getByTestId('move-drift')).toBeVisible();
  await expect(page.getByTestId('dock-dice')).not.toBeVisible();
  await expect(page.getByLabel(/^Playhead/)).toHaveValue('2.5');
  expect(await canvas!.evaluate(el=>el===document.querySelector('[data-testid="studio-artwork"] canvas'))).toBe(true);
  await page.getByRole('button',{name:'Close editing panel',exact:true}).click();
  await expect(tools.getByRole('button',{name:'Motion',exact:true})).toBeFocused();
});

test('expanded preview retains playback and returns to the editing context', async ({page}) => {
  await film(page);
  await page.getByRole('navigation',{name:'Studio tools'}).getByRole('button',{name:'Look',exact:true}).click();
  await page.getByLabel(/^Playhead/).fill('2');
  await page.getByRole('button',{name:'Expand preview',exact:true}).click();
  await expect(page.getByRole('button',{name:'Back to editing',exact:true})).toBeFocused();
  await expect(page.getByRole('navigation',{name:'Studio tools'})).not.toBeVisible();
  await expect(page.getByLabel(/^Playhead/)).toBeVisible();
  await page.getByLabel(/^Playhead/).fill('3');
  await fits(page,300);
  await page.keyboard.press('Escape');
  await expect(page.getByRole('heading',{name:'Set the look'})).toBeVisible();
  await expect(page.getByRole('button',{name:'Expand preview',exact:true})).toBeFocused();
  await expect(page.getByLabel(/^Playhead/)).toHaveValue('3');
});

test('short portrait editing keeps artwork and reachable controls; Escape works from an input', async ({page}) => {
  await page.setViewportSize({width:360,height:448});await film(page);
  await page.getByRole('navigation',{name:'Studio tools'}).getByRole('button',{name:'Layout',exact:true}).click();
  await expect(page.getByRole('button',{name:'Close editing panel',exact:true})).toBeFocused();
  await page.keyboard.press('f');
  await expect(page.getByRole('button',{name:'Back to editing',exact:true})).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button',{name:'Close editing panel',exact:true})).toBeFocused();
  await page.getByRole('button',{name:'Balanced',exact:true}).click();
  await fits(page,100);
  const close=page.getByRole('button',{name:'Close editing panel',exact:true});
  const box=await close.boundingBox();expect(box!.y).toBeGreaterThanOrEqual(0);expect(box!.y+box!.height).toBeLessThanOrEqual(448);
  await close.click();
  const layout=page.getByRole('navigation',{name:'Studio tools'}).getByRole('button',{name:'Layout',exact:true});
  await expect(layout).toBeFocused();await layout.click();
  const chaos=page.getByRole('slider',{name:'Chaos',exact:true});await chaos.focus();await page.keyboard.press('Escape');
  await expect(page.getByRole('complementary',{name:'Editing panel'})).not.toBeVisible();
  await expect(page.getByRole('button',{name:'Expand preview',exact:true})).toBeVisible();
  await expect(page.getByRole('navigation',{name:'Studio tools'}).getByRole('button',{name:'Layout',exact:true})).toBeFocused();
});

test('status messages occupy their own row and never cover playback', async ({page}) => {
  await film(page);
  const notice=page.locator('.studio-notice');await expect(notice).toBeVisible();
  const n=await notice.boundingBox(), p=await page.getByRole('group',{name:'Preview playback',exact:true}).boundingBox();
  expect(n!.y+n!.height).toBeLessThanOrEqual(p!.y);
});
