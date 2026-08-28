/**
 * THE LAST NUMBER HE TYPED — a gate for the row half of shape #1.
 * Aldrin Payopay <aldrin.gdf@gmail.com> — GPL-3.0
 *
 * tools/toolkit-gates/order-live-header.mjs asserts that every HEADER control
 * reaching the copied document also reaches the block labelled "what you send",
 * and it skips everything inside #list on purpose — "the ticked-line controls
 * are covered by the row gates." They were not. Nothing asserted the row half,
 * and the row half is where the last edit before Copy almost always happens: a
 * man ticks the line, then types how many.
 *
 * WHAT IT DOES: ticks one line, types a count and a note INTO THAT SAME ROW —
 * the order that matters, because the repaint that ran on the tick ran before
 * the number existed — then clicks the page's own copy button and compares the
 * clipboard to the block, in full.
 *
 * IT FOUND ONE, THE DAY IT WAS WRITTEN. av/consumables.html bound no listener
 * to .qty or .note at all: the block read "Wall Dogs x1" while the message said
 * "x8". It had been invisible for the page's whole life because the page had no
 * block — the count in the dock only ever moves when a line goes on or off, so
 * nothing needed repainting and nothing was wired to. The defect arrived the
 * moment the document went on the glass, and this gate is what caught it.
 *
 * The other twelve are green because shared/checklist-request.js re-renders on
 * its own row controls; asserted here so the next hand-forked page cannot
 * quietly stop being that lucky.
 *
 *   node tools/toolkit-gates/row-live-line.mjs
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { createServer } from 'http';
import { extname, join, normalize } from 'path';
const require = createRequire(new URL('../collage-studio/package.json', import.meta.url));
const { chromium } = require('playwright');
const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const MIME={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.webmanifest':'application/manifest+json','.png':'image/png'};
const s=createServer((req,rq)=>{const rel=normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/,'');const p=join(ROOT,rel);if(!p.startsWith(ROOT)||!existsSync(p)||statSync(p).isDirectory()){rq.writeHead(404);return rq.end('no');}rq.writeHead(200,{'content-type':MIME[extname(p)]||'application/octet-stream'});rq.end(readFileSync(p));});
await new Promise(r=>s.listen(0,'127.0.0.1',r)); const port=s.address().port;
const trades=readdirSync(ROOT,{withFileTypes:true}).filter(d=>d.isDirectory()&&existsSync(join(ROOT,d.name,'tools.js'))).map(d=>d.name).sort();
const pages=[];
for(const t of trades) for(const f of readdirSync(join(ROOT,t)).filter(f=>f.endsWith('.html')).sort()){
  const src=readFileSync(join(ROOT,t,f),'utf8');
  if(src.includes('id="list"')&&src.includes('id="preview"')&&src.includes('id="copy"')&&src.includes('id="clear"')) pages.push(`${t}/${f}`);
}
const b=await chromium.launch(); let bad=0;
for(const rel of pages){
  const ctx=await b.newContext({viewport:{width:390,height:800}});
  await ctx.addInitScript(()=>{window.__copied=null;Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:t=>{window.__copied=String(t);return Promise.resolve();}}});});
  const page=await ctx.newPage();
  await page.goto(`http://127.0.0.1:${port}/${rel}`,{waitUntil:'load'});
  await page.waitForTimeout(500);
  const did=await page.evaluate(()=>{
    const t=document.querySelector('#list input.tick:not(:disabled)');
    if(!t) return 'no tick';
    t.checked=true;t.dispatchEvent(new Event('change',{bubbles:true}));t.dispatchEvent(new Event('input',{bubbles:true}));
    const row=t.closest('.item')||t.closest('li')||t.parentElement;
    const q=row&&row.querySelector('.qty'); const n=row&&row.querySelector('.note');
    let done=[];
    if(q){q.value='7';q.dispatchEvent(new Event('input',{bubbles:true}));done.push('qty');}
    if(n){n.value='ZZNOTEMARK';n.dispatchEvent(new Event('input',{bubbles:true}));done.push('note');}
    return done.length?done.join('+'):'no row control';
  });
  await page.waitForTimeout(500);
  const prev=(await page.textContent('#preview')||'').trim();
  await page.evaluate(()=>{window.__copied=null;});
  await page.click('#copy'); await page.waitForFunction(()=>window.__copied!==null,null,{timeout:5000});
  const sent=(await page.evaluate(()=>window.__copied)||'').trim();
  const ok=prev===sent;
  if(!ok)bad++;
  console.log(`${ok?'  ok ':'  ✗  '} ${rel}  (${did})${ok?'':'   BLOCK ≠ MESSAGE'}`);
  if(!ok){
    const pl=prev.split('\n'), sl=sent.split('\n');
    for(let i=0;i<Math.max(pl.length,sl.length);i++) if(pl[i]!==sl[i]) console.log(`        glass: ${JSON.stringify(pl[i])}\n        sent : ${JSON.stringify(sl[i])}`);
  }
  await ctx.close();
}
await b.close(); s.close();
console.log(`\n${bad?`FAIL — ${bad} page(s) where the block disagrees with the message`:`OK — ${pages.length} order page(s): the block on the glass IS the message, down to the last count typed`}`);
process.exit(bad?1:0);
