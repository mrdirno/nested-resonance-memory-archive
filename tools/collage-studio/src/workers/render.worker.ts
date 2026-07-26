// src/workers/render.worker.ts
/* eslint-disable no-restricted-globals */
import { calculateSmartCrop } from '../lib/renderer';

const ctx: Worker = self as any;

ctx.onmessage = async (e: MessageEvent) => {
  const { 
    id, 
    width, 
    height, 
    mode, 
    layoutItems, 
    orderedImages,
    zoom = 1.0,
    bgColor = '#050505'
  } = e.data;

  let errorCount = 0;

  try {
    let canvas: OffscreenCanvas;
    try {
        canvas = new OffscreenCanvas(width, height);
    } catch (err) {
        throw new Error(`OffscreenCanvas creation failed (Size: ${width}x${height}).`);
    }
    
    const ctx2d = canvas.getContext('2d');
    if (!ctx2d) throw new Error("Could not get 2D context");

    ctx2d.fillStyle = bgColor;
    ctx2d.fillRect(0, 0, width, height);

    for (let i = 0; i < layoutItems.length; i++) {
        const item = layoutItems[i];
        const imgMeta = orderedImages[i];
        if (!imgMeta) continue;

        try {
            const response = await fetch(imgMeta.src);
            if (!response.ok) throw new Error(`Fetch failed: ${response.status}`);
            const blob = await response.blob();
            const imgBitmap = await createImageBitmap(blob);

            ctx2d.save();
            ctx2d.beginPath();
            item.path.forEach((p: any, idx: number) => {
                if (idx===0) ctx2d.moveTo(p.x, p.y); else ctx2d.lineTo(p.x, p.y);
            });
            ctx2d.closePath();
            ctx2d.clip();

            const crop = calculateSmartCrop(item.bounds, {
                width: imgMeta.width,
                height: imgMeta.height,
                analysis: imgMeta.analysis
            }, zoom);

            ctx2d.drawImage(imgBitmap, crop.sx, crop.sy, crop.sw, crop.sh, crop.dx, crop.dy, crop.dw, crop.dh);
            imgBitmap.close(); 
            
            if (mode === 'complex') {
                ctx2d.strokeStyle = '#000'; 
                ctx2d.lineWidth = width * 0.001; 
                ctx2d.stroke();
            }
            ctx2d.restore();
        } catch (innerErr) {
            console.warn("Worker image load failed", innerErr);
            errorCount++;
        }
    }

    // If we had errors (missing images), we should consider this a failure so the main thread fallback runs
    if (errorCount > 0) {
        throw new Error(`Worker failed to render ${errorCount} images.`);
    }

    const blob = await canvas.convertToBlob({ type: 'image/jpeg', quality: 0.92 });
    ctx.postMessage({ id, success: true, blob });

  } catch (err: any) {
    ctx.postMessage({ id, success: false, error: err.message });
  }
};
