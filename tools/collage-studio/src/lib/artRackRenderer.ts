// Author: Aldrin Payopay <aldrin.gdf@gmail.com>. GPL-3.0-only.
// Original geometric painters. No imported instrument engine or media is used.
import { ART_PALETTES, createArtRandom, sampleArtLayer, type ArtLayer, type ArtLayerSample, type ArtRecipe } from './artRack';
type Context=CanvasRenderingContext2D|OffscreenCanvasRenderingContext2D;
type Colors=readonly string[];
const TAU=Math.PI*2;
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
const color=(colors:Colors,index:number)=>colors[((index%colors.length)+colors.length)%colors.length];

function contour(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number,hx:number,hy:number):void {
  const random=createArtRandom(seed),p=random()*TAU,q=random()*TAU;
  const nx=48,ny=36,dx=2*(hx+.08)/nx,dy=2*(hy+.08)/ny,left=-hx-.08,top=-hy-.08;
  const values=new Float64Array((nx+1)*(ny+1));
  for(let y=0;y<=ny;y++)for(let x=0;x<=nx;x++){
    const px=left+x*dx,py=top+y*dy;
    values[y*(nx+1)+x]=Math.sin(px*5.1+p+s.form*.8)+.8*Math.cos(py*6.3+q-s.form*.9)+.42*Math.sin(px*3.5+py*4.2+p*.5+s.form);
  }
  const count=4+Math.round(s.density*6),cross=new Float64Array(8),alpha=ctx.globalAlpha;
  for(let level=0;level<count;level++){
    const threshold=mix(-1.7,1.7,(level+.5)/count);ctx.beginPath();
    for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
      const i=y*(nx+1)+x,a=values[i],b=values[i+1],c=values[i+nx+2],d=values[i+nx+1],px=left+x*dx,py=top+y*dy;
      let n=0;
      if((a<threshold)!==(b<threshold)){cross[n++]=px+dx*(threshold-a)/(b-a);cross[n++]=py;}
      if((b<threshold)!==(c<threshold)){cross[n++]=px+dx;cross[n++]=py+dy*(threshold-b)/(c-b);}
      if((c<threshold)!==(d<threshold)){cross[n++]=px+dx*(threshold-d)/(c-d);cross[n++]=py+dy;}
      if((d<threshold)!==(a<threshold)){cross[n++]=px;cross[n++]=py+dy*(threshold-a)/(d-a);}
      for(let j=0;j+3<n;j+=4){ctx.moveTo(cross[j],cross[j+1]);ctx.lineTo(cross[j+2],cross[j+3]);}
    }
    ctx.strokeStyle=color(colors,level);ctx.lineWidth=level%3===0?.0033:.0017;ctx.globalAlpha=alpha*(level%3===0?.9:.55);ctx.stroke();
  }
  ctx.globalAlpha=alpha;
}

function rosette(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number):void {
  const random=createArtRandom(seed),petals=4+Math.floor(random()*5)+Math.floor(s.density*5),turn=random()*TAU;
  const count=2+Math.round(s.density*5),samples=240,alpha=ctx.globalAlpha;
  for(let ring=count-1;ring>=0;ring--){
    const radius=.13+ring*.047,depth=.13+s.density*.15+s.form*.1;ctx.beginPath();
    for(let i=0;i<=samples;i++){
      const t=i/samples*TAU,r=radius*(1+depth*Math.cos(petals*t+s.form*1.6+ring*.19))*(1+.035*Math.sin(2*petals*t+turn));
      const a=t+turn+ring*.016*s.form,x=Math.cos(a)*r,y=Math.sin(a)*r;i?ctx.lineTo(x,y):ctx.moveTo(x,y);
    }
    ctx.closePath();ctx.strokeStyle=color(colors,ring);ctx.lineWidth=ring===count-1?.0035:.002;
    if(ring===count-1){ctx.fillStyle=color(colors,2);ctx.globalAlpha=alpha*.10;ctx.fill();}
    ctx.globalAlpha=alpha*(.65+.35*ring/Math.max(1,count-1));ctx.stroke();
  }
  ctx.globalAlpha=alpha*.7;ctx.fillStyle=color(colors,0);ctx.beginPath();ctx.arc(0,0,.008,0,TAU);ctx.fill();ctx.globalAlpha=alpha;
}

function rings(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number):void {
  const random=createArtRandom(seed),tilt=(random()-.5)*1.2,ecc=.52+random()*.34;
  const count=12+Math.round(s.density*34),alpha=ctx.globalAlpha;
  for(let family=0;family<2;family++){
    const sign=family?1:-1,cx=sign*(.085+s.form*.055),cy=sign*.055;
    for(let i=0;i<count;i++){
      const r=.05+i/count*.53;ctx.beginPath();ctx.ellipse(cx,cy,r,r*ecc,tilt+sign*(.23+s.form*.2),0,TAU);
      ctx.strokeStyle=color(colors,family?2:0);ctx.lineWidth=i%7===0?.0025:.00125;ctx.globalAlpha=alpha*(i%7===0?.75:.42);ctx.stroke();
    }
  }
  ctx.globalAlpha=alpha;
}

function ribbons(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number,hx:number):void {
  const random=createArtRandom(seed),phase=random()*TAU,count=3+Math.round(s.density*12),alpha=ctx.globalAlpha;
  const yAt=(x:number,index:number)=>mix(-.46,.46,(index+.5)/count)+(.045+.11*s.density)*Math.sin(x*5+phase+index*.45+s.form*1.8)
    +.035*Math.sin(x*10-phase+index*.25-s.form);
  for(let band=0;band<count;band++){
    const thickness=.01+.018*(.5+.5*Math.sin(band+phase)),samples=100;ctx.beginPath();
    for(let i=0;i<=samples;i++){const x=mix(-hx-.12,hx+.12,i/samples),y=yAt(x,band);i?ctx.lineTo(x,y):ctx.moveTo(x,y);}
    for(let i=samples;i>=0;i--){const x=mix(-hx-.12,hx+.12,i/samples);ctx.lineTo(x,yAt(x,band)+thickness);}
    ctx.closePath();const gradient=ctx.createLinearGradient(-hx,0,hx,0);gradient.addColorStop(0,color(colors,band));gradient.addColorStop(1,color(colors,band+2));
    ctx.fillStyle=gradient;ctx.globalAlpha=alpha*(.5+.32*(band%3)/2);ctx.fill();
  }
  ctx.globalAlpha=alpha;
}

function branches(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number):void {
  const random=createArtRandom(seed),depth=2+Math.round(s.density*4),fans=2+Math.floor(random()*2),alpha=ctx.globalAlpha;
  const grow=(x:number,y:number,length:number,angle:number,remaining:number,order:number):void=>{
    const jitter=(random()-.5)*.14,bend=s.form*.16*(1-remaining/(depth+1));
    const a=angle+jitter+bend,endX=x+Math.cos(a)*length,endY=y+Math.sin(a)*length;
    ctx.beginPath();ctx.moveTo(x,y);ctx.quadraticCurveTo(x+Math.cos(a+.1*s.form)*length*.55,y+Math.sin(a+.1*s.form)*length*.55,endX,endY);
    ctx.strokeStyle=color(colors,order%2?2:0);ctx.lineWidth=.0013+remaining*.0013;ctx.globalAlpha=alpha*(.45+.45*remaining/(depth+1));ctx.stroke();
    if(remaining>0){const spread=.29+random()*.2;grow(endX,endY,length*.7,a-spread,remaining-1,order+1);grow(endX,endY,length*.72,a+spread,remaining-1,order+1);}
    else {ctx.beginPath();ctx.ellipse(endX,endY,.004,.009,a,0,TAU);ctx.fillStyle=color(colors,3);ctx.globalAlpha=alpha*.65;ctx.fill();}
  };
  for(let i=0;i<fans;i++)grow(mix(-.28,.28,(i+.5)/fans),.43,.19+random()*.045,-Math.PI/2+(i-(fans-1)/2)*.14,depth,0);
  ctx.globalAlpha=alpha;
}

function facets(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number,hx:number,hy:number):void {
  const random=createArtRandom(seed),count=3+Math.round(s.density*10),alpha=ctx.globalAlpha;
  for(let crystal=0;crystal<count;crystal++){
    const cx=(random()-.5)*hx*1.5,cy=(random()-.5)*hy*1.5,r=.06+random()*.14,tilt=random()*TAU,n=5+Math.floor(random()*4);
    const points:number[]=[];
    for(let i=0;i<n;i++){const a=tilt+i/n*TAU,rad=r*(.72+random()*.35)*(1+s.form*.08);points.push(cx+Math.cos(a)*rad,cy+Math.sin(a)*rad*1.4);}
    const centerX=cx+s.form*r*.1,centerY=cy-r*.08;
    for(let i=0;i<n;i++){
      const j=(i+1)%n;ctx.beginPath();ctx.moveTo(centerX,centerY);ctx.lineTo(points[2*i],points[2*i+1]);ctx.lineTo(points[2*j],points[2*j+1]);ctx.closePath();
      ctx.fillStyle=color(colors,crystal+i);ctx.globalAlpha=alpha*(.38+.5*(.5+.5*Math.cos(tilt+i/n*TAU+s.form*2)));ctx.fill();
      ctx.strokeStyle=color(colors,0);ctx.lineWidth=.001;ctx.globalAlpha=alpha*.32;ctx.stroke();
    }
  }
  ctx.globalAlpha=alpha;
}

function weave(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number,hx:number,hy:number):void {
  const random=createArtRandom(seed),spacing=1/(5+Math.round(s.density*12)),width=spacing*(.32+random()*.16),phase=random()*TAU;
  // Zooming out must not turn a layer into an unbounded number of stitches.
  const cols=Math.min(40,Math.ceil(2*hx/spacing)+2),rows=Math.min(40,Math.ceil(2*hy/spacing)+2),alpha=ctx.globalAlpha;
  ctx.lineCap='butt';
  // Bottom and top crossings are batched by ink: eight strokes, not thousands.
  for(let pass=0;pass<2;pass++)for(let shade=0;shade<4;shade++){
    ctx.beginPath();
    for(let row=0;row<rows;row++)for(let col=0;col<cols;col++){
      const horizontal=((row+col)%2===0)===(pass===1);
      const ink=horizontal?(row%2?0:1):(col%2?2:3);if(ink!==shade)continue;
      const x=(col-(cols-1)/2)*spacing+s.form*.022*Math.sin(row*.7+phase),y=(row-(rows-1)/2)*spacing+s.form*.022*Math.cos(col*.6+phase);
      if(horizontal){ctx.moveTo(x-spacing*.47,y);ctx.lineTo(x+spacing*.47,y);}
      else{ctx.moveTo(x,y-spacing*.47);ctx.lineTo(x,y+spacing*.47);}
    }
    ctx.strokeStyle=color(colors,shade);ctx.lineWidth=width;ctx.globalAlpha=alpha*.7;ctx.stroke();
  }
  ctx.globalAlpha=alpha;
}

function particles(ctx:Context,s:ArtLayerSample,colors:Colors,seed:number,hx:number,hy:number):void {
  const random=createArtRandom(seed),count=24+Math.round(s.density*168),alpha=ctx.globalAlpha;
  for(let i=0;i<count;i++){
    const orbit=Math.sqrt(random()),angle=random()*TAU,stretch=.5+random()*.5,speed=.3+random()*.8,r=.0015+Math.pow(random(),3)*.009;
    const mark=random(),trail=i%5===0?5:1;
    for(let j=trail-1;j>=0;j--){
      const a=angle+s.form*speed-j*.025,x=Math.cos(a)*orbit*hx*.98,y=Math.sin(a)*orbit*hy*stretch*.98;
      ctx.globalAlpha=alpha*(j?(.18*(1-j/trail)):(.4+.5*orbit));ctx.fillStyle=color(colors,i%5);ctx.beginPath();
      if(mark>.88){ctx.moveTo(x,y-r*1.6);ctx.lineTo(x+r,y);ctx.lineTo(x,y+r*1.6);ctx.lineTo(x-r,y);ctx.closePath();}
      else ctx.arc(x,y,r*(j?.7:1),0,TAU);
      ctx.fill();
    }
  }
  ctx.globalAlpha=alpha;
}

/** Render directly from the frozen recipe and requested time; seek order is irrelevant. */
export function drawArt(ctx:Context,width:number,height:number,recipe:ArtRecipe,timeSeconds:number):void {
  if(!Number.isSafeInteger(width)||!Number.isSafeInteger(height)||width<1||height<1||width>4096||height>4096||width*height>16_000_000)
    throw new Error('Art output must fit within 4096 pixels per side and 16 megapixels.');
  if(!Number.isFinite(timeSeconds))throw new Error('Art time must be finite.');
  const unit=Math.min(width,height),hx=width/unit/2,hy=height/unit/2;
  // WebKit can expose an assigned filter as an ordinary JS property, outside
  // Canvas save/restore. Preserve it explicitly and do not create it if absent.
  const hadFilter='filter' in ctx,callerFilter=ctx.filter;
  ctx.save();
  try{
    ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';
    if(hadFilter)ctx.filter='none';ctx.shadowBlur=0;ctx.shadowOffsetX=0;ctx.shadowOffsetY=0;ctx.shadowColor='rgba(0,0,0,0)';ctx.setLineDash([]);ctx.lineDashOffset=0;
    ctx.clearRect(0,0,width,height);
    if(recipe.background!=='transparent'){ctx.fillStyle=recipe.background;ctx.fillRect(0,0,width,height);}
    for(const layer of recipe.layers){
      if(!layer.enabled||(recipe.soloId&&recipe.soloId!==layer.id)||layer.opacity===0)continue;
      const s=sampleArtLayer(layer,timeSeconds,recipe.duration);if(s.opacity<=0)continue;
      ctx.save();
      try{
        ctx.globalAlpha=s.opacity;ctx.globalCompositeOperation=layer.blend;ctx.lineCap='round';ctx.lineJoin='round';
        ctx.translate(width/2+s.x*width,height/2+s.y*height);ctx.rotate(s.rotation*Math.PI/180);ctx.scale(unit*s.scale,unit*s.scale);
        const colors=ART_PALETTES[layer.palette].colors;
        switch(layer.kind){
          case 'contour':contour(ctx,s,colors,layer.seed,hx/s.scale,hy/s.scale);break;
          case 'rosette':rosette(ctx,s,colors,layer.seed);break;
          case 'rings':rings(ctx,s,colors,layer.seed);break;
          case 'ribbons':ribbons(ctx,s,colors,layer.seed,hx/s.scale);break;
          case 'branches':branches(ctx,s,colors,layer.seed);break;
          case 'facets':facets(ctx,s,colors,layer.seed,hx,hy);break;
          case 'weave':weave(ctx,s,colors,layer.seed,hx/s.scale,hy/s.scale);break;
          case 'particles':particles(ctx,s,colors,layer.seed,hx,hy);break;
        }
      }finally{ctx.restore();}
    }
  }finally{ctx.restore();if(hadFilter)ctx.filter=callerFilter;}
}
