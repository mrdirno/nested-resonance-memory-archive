// Original art instrument. Author: Aldrin Payopay <aldrin.gdf@gmail.com>.
// GPL-3.0-only, as the host project. No borrowed engine, media or network assets.
export const ART_ROOM_STARTER_NAME = 'Tidal Paper';
export const ART_ROOM_STARTER_HTML = String.raw`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tidal Paper — an Art Room instrument</title>
<style>
*{box-sizing:border-box}html,body{margin:0;background:#101619;color:#f2eee2;font:14px system-ui,sans-serif}body{padding:16px}
.head{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;margin-bottom:12px}h1{font-size:18px;letter-spacing:.14em;margin:0}.sub{font-size:11px;color:#a6b5b8}
canvas{display:block;width:100%;height:auto;max-height:54vh;object-fit:contain;background:#102d3a;border-radius:4px}
.controls{display:flex;align-items:end;gap:8px;flex-wrap:wrap;margin-top:12px}label{display:flex;flex-direction:column;gap:4px;font-size:11px;color:#b6c4c5;flex:1;min-width:88px}button,input,select{font:inherit;min-height:44px;border:1px solid #526165;border-radius:7px;background:#1b282c;color:#f2eee2;padding:8px;max-width:100%;width:100%}button{cursor:pointer;min-width:84px;width:auto;font-size:12px}button:hover{background:#30474b}input[type=range]{padding:6px;accent-color:#efad73}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid #f4c28a;outline-offset:2px}.note{font-size:11px;color:#a6b5b8;line-height:1.5;margin:10px 0 0}@media(max-width:400px){body{padding:10px}.controls{gap:6px}h1{font-size:15px}canvas{max-height:44vh}}
</style></head><body>
<div class="head"><h1>TIDAL PAPER</h1><span class="sub">AN ORIGINAL SEED INSTRUMENT</span></div>
<canvas id="art" width="1200" height="900" aria-label="Tidal Paper artwork" data-art-ready="true"></canvas>
<div class="controls">
<label>Seed<input id="seed" type="number" min="1" max="999999" value="500" aria-label="Art seed"></label>
<button id="new" type="button">New seed</button>
<label>Palette<select id="palette" aria-label="Art palette"><option value="tide">Tide &amp; copper</option><option value="orchid">Orchid &amp; cream</option><option value="moss">Moss &amp; ochre</option></select></label>
<label>Motion<input id="motion" aria-label="Art motion" type="range" min="0" max="1" step=".05" value=".35"></label>
<button id="pause" type="button" aria-pressed="false">Pause</button>
</div>
<p class="note">A seed repeats the composition. Motion changes the tides. Pause to choose a moment, then use the artwork in GenArt.</p>
<script>
(() => {
'use strict';
const canvas=document.getElementById('art'),ctx=canvas.getContext('2d');
const seedInput=document.getElementById('seed'),paletteInput=document.getElementById('palette'),motionInput=document.getElementById('motion'),pause=document.getElementById('pause');
const palettes={tide:['#102d3a','#174858','#27706e','#71a5a0','#d9d5b8','#d69c64','#a75e45'],orchid:['#30243c','#594b73','#826990','#bc98a5','#f1dfbf','#eaaa81','#80574c'],moss:['#182e29','#294c3e','#5a7450','#8f9b68','#e2d5a0','#c79845','#936432']};
let seed=500,phase=0,last=0,running=!matchMedia('(prefers-reduced-motion: reduce)').matches,frame=0,points=[];
const grain=document.createElement('canvas');grain.width=1200;grain.height=900;const gc=grain.getContext('2d');
function rng(n){return()=>{n|=0;n=n+0x6d2b79f5|0;let t=Math.imul(n^n>>>15,1|n);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function rebuild(){const r=rng(seed);points=Array.from({length:12},()=>({a:r()*6.28,b:r()*6.28,h:20+r()*70,tilt:(r()-.5)*120}));gc.clearRect(0,0,1200,900);for(let i=0;i<18000;i++){gc.fillStyle=r()>.5?'rgba(250,246,228,.075)':'rgba(12,20,28,.055)';gc.fillRect(r()*1200,r()*900,.7+r()*1.7,.7+r()*1.7);}phase=0;paint();}
function paint(){if(!ctx)return;const p=palettes[paletteInput.value],amount=Number(motionInput.value);ctx.fillStyle=p[0];ctx.fillRect(0,0,1200,900);
// Broad paper strata make the image at three scales: a quiet sky, a woven
// coastline, and a fine luminous seam. Every contour comes from this seed.
const r=rng(seed+371),sunX=220+r()*760,sunY=165+r()*175,sunR=72+r()*70;
ctx.fillStyle=p[4];ctx.beginPath();ctx.arc(sunX,sunY,sunR,0,Math.PI*2);ctx.fill();
ctx.save();ctx.strokeStyle=p[5];ctx.lineWidth=2;ctx.beginPath();ctx.arc(sunX,sunY,sunR+22,0,Math.PI*2);ctx.stroke();ctx.restore();
for(let k=0;k<12;k++){const q=points[k],base=310+k*55;ctx.beginPath();ctx.moveTo(-20,950);for(let x=-20;x<=1220;x+=10){const u=x/1200;const y=base+Math.sin(u*5.8+q.a+phase*.18*amount)*q.h+Math.sin(u*12+q.b-phase*.1*amount)*20+q.tilt*(u-.5);ctx.lineTo(x,y);}ctx.lineTo(1220,950);ctx.closePath();ctx.fillStyle=p[1+k%6];ctx.fill();ctx.strokeStyle=k%3===0?p[4]:'rgba(8,18,24,.22)';ctx.lineWidth=k%3===0?2.2:1;ctx.stroke();}
ctx.globalCompositeOperation='soft-light';ctx.drawImage(grain,0,0);ctx.globalCompositeOperation='source-over';
canvas.dataset.artName='Tidal Paper · seed '+seed+' · '+paletteInput.value;canvas.dataset.artExportName='tidal-paper-'+seed+'-'+paletteInput.value+'.png';}
function loop(now){frame=0;if(!running||document.hidden)return;if(last)phase+=Math.min(.06,(now-last)/1000);last=now;paint();frame=requestAnimationFrame(loop);}
function wake(){last=0;if(running&&!document.hidden&&!frame)frame=requestAnimationFrame(loop);}
function pauseLabel(){pause.textContent=running?'Pause':'Play';pause.setAttribute('aria-pressed',String(!running));}
seedInput.addEventListener('change',()=>{seed=Math.max(1,Math.min(999999,Math.floor(Number(seedInput.value)||500)));seedInput.value=String(seed);rebuild();});
document.getElementById('new').addEventListener('click',()=>{seed=1+crypto.getRandomValues(new Uint32Array(1))[0]%999999;seedInput.value=String(seed);rebuild();});
paletteInput.addEventListener('change',paint);motionInput.addEventListener('input',paint);
pause.addEventListener('click',()=>{running=!running;pauseLabel();if(!running&&frame){cancelAnimationFrame(frame);frame=0;}wake();});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&frame){cancelAnimationFrame(frame);frame=0;}wake();});
rebuild();pauseLabel();wake();
})();
</script></body></html>`;
