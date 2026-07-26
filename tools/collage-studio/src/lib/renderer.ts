import { LayoutItem } from '../types';
import { ImageAsset } from '../types';

interface CropGeometry {
  sx: number; sy: number; sw: number; sh: number; 
  dx: number; dy: number; dw: number; dh: number; 
}

export const calculateSmartCrop = (
  box: {x:number, y:number, w:number, h:number},
  img: {width:number, height:number, analysis: any},
  zoom: number = 1.0
): CropGeometry => {
    const boxAsp = box.w / box.h;
    const imgAsp = img.width / img.height;
    
    let drawW, drawH;

    if (imgAsp > boxAsp) {
        drawH = img.height;
        drawW = drawH * boxAsp;
    } else {
        drawW = img.width;
        drawH = drawW / boxAsp;
    }

    const cropW = drawW / zoom;
    const cropH = drawH / zoom;

    const anchor = img.analysis.face ? img.analysis.face : img.analysis.energy;
    
    const ax = anchor.x * img.width;
    const ay = anchor.y * img.height;
    
    let sx = ax - (cropW / 2);
    let sy = ay - (cropH / 2);
    
    sx = Math.max(0, Math.min(img.width - cropW, sx));
    sy = Math.max(0, Math.min(img.height - cropH, sy));
    
    return {
      sx, sy, sw: cropW, sh: cropH,
      dx: box.x, dy: box.y, dw: box.w, dh: box.h
    };
};

export const renderCanvas = async (
  width: number,
  aspect: number,
  mode: string, 
  layoutItems: LayoutItem[],
  orderedImages: (ImageAsset | null)[], 
  seed: number,
  zoom: number = 1.0,
  bgColor: string = '#050505' // New param
): Promise<HTMLCanvasElement> => {
  const LOGICAL_W = width;
  const LOGICAL_H = width / aspect;
  
  const canvas = document.createElement('canvas');
  canvas.width = LOGICAL_W;
  canvas.height = LOGICAL_H;
  const ctx = canvas.getContext('2d');
  if (!ctx) return canvas;

  // Use Custom BG Color
  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, LOGICAL_W, LOGICAL_H);

  for (let i = 0; i < layoutItems.length; i++) {
    const item = layoutItems[i];
    const imgData = orderedImages[i]; 
    if (!imgData) continue;

    const img = await new Promise<HTMLImageElement>((resolve) => {
      const _i = new Image();
      _i.crossOrigin = 'anonymous';
      _i.onload = () => resolve(_i);
      _i.onerror = () => resolve(_i); 
      _i.src = imgData.src;
    });

    if (!img.width) continue;

    ctx.save();
    ctx.beginPath();
    item.path.forEach((p, idx) => {
        if (idx===0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    ctx.clip();

    const crop = calculateSmartCrop(item.bounds, {
      width: img.width, 
      height: img.height, 
      analysis: imgData.analysis
    }, zoom);

    ctx.drawImage(img, crop.sx, crop.sy, crop.sw, crop.sh, crop.dx, crop.dy, crop.dw, crop.dh);
    
    // Style overlays
    if (mode === 'complex') {
        ctx.strokeStyle = '#000'; 
        ctx.lineWidth = width * 0.001; 
        ctx.stroke();
    }
    ctx.restore();
  }
  return canvas;
};
