// src/workers/render.worker.ts
/* eslint-disable no-restricted-globals */
//
// THE EXPORT RENDERER — and, since C3, an HONEST one.
//
// WHY THIS FILE CHANGED (wishing well d88093af, reported by the owner):
//   "When I hit export sometimes it will show a black screen ... partial
//    elements of the collage appeared but it failed to export full image."
//
//   Both halves were this worker lying about what happened:
//
//   1. BLACK. Over a platform's canvas ceiling, `new OffscreenCanvas(w,h)` does
//      NOT throw. getContext succeeds, fillRect succeeds, drawImage succeeds,
//      and convertToBlob hands back a valid, correctly-sized, ENTIRELY BLACK
//      JPEG. Nothing in the old code could tell that from a real render, so the
//      black file went straight to the user. We now write a sentinel into the
//      far corner and read it back BEFORE drawing anything (`assertSurfaceLive`
//      — one pixel, ~1 ms) and report `surfaceLive: false` so the caller steps
//      DOWN a tier instead of shipping the black file.
//
//   2. PARTIAL. The old code counted failed decodes and then threw
//      `Worker failed to render N images`, which the main thread caught as
//      "worker unavailable" and silently re-ran on the main thread — where the
//      still-renderer SKIPS unloadable fragments (`if (!img.width) continue`).
//      That is precisely "partial elements appeared": holes where photographs
//      should be, background showing through. We now report `failedImages` as a
//      NUMBER and let the caller decide; a decode failure is not a size failure,
//      so it must not be answered by burning the whole tier ladder.
//
// The verdicts below are the exact shape `exportLimits.runWithFallback` consumes
// (`RenderOutcome`), so this worker plugs into the tested ladder with no
// translation layer.
//
import { calculateSmartCrop } from '../lib/renderer';
import { titlePlanFor, drawTitlePlan } from '../lib/title';
import { assertSurfaceLive } from '../lib/exportLimits';

const ctx: Worker = self as any;

/** Aborted ids — the main thread sends {cancel:id} when a tier times out. */
const cancelled = new Set<number>();

/**
 * Decode the first source that actually yields pixels, in preference order.
 * Returns null only when every candidate is gone — which is the one case that
 * genuinely counts as a failed fragment.
 */
const decodeFirstAvailable = async (
  sources: (string | undefined | null)[],
): Promise<ImageBitmap | null> => {
  for (const src of sources) {
    if (!src) continue;
    try {
      const response = await fetch(src);
      if (!response.ok) continue;
      const blob = await response.blob();
      if (!blob.size) continue;
      return await createImageBitmap(blob);
    } catch {
      /* try the next one */
    }
  }
  return null;
};

ctx.onmessage = async (e: MessageEvent) => {
  const d = e.data || {};

  // Cancellation channel: the ladder's teardown terminates us outright, but a
  // cooperative cancel lets an in-flight tier stop decoding immediately.
  if (d.cancel !== undefined) { cancelled.add(d.cancel); return; }

  const {
    id,
    width,
    height,
    mode,
    layoutItems,
    orderedImages,
    zoom = 1.0,
    bgColor = '#050505',
    // THE TITLE — a finished plan, wrapped on the main thread against the
    // context the PREVIEW measured with. Deliberately not re-planned here: this
    // is another thread, where the same font stack is free to resolve to
    // something else, and a title that breaks onto two lines in the preview and
    // three in the file is the exact divergence ONE LAYOUT removed.
    titlePlan = null,
  } = d;

  let failedImages = 0;
  let drawn = 0;

  try {
    let canvas: OffscreenCanvas;
    try {
        canvas = new OffscreenCanvas(width, height);
    } catch (err) {
        // The HONEST allocation failure. Distinct from the silent one below.
        ctx.postMessage({ id, success: false, surfaceLive: false, failedImages: 0, drawn: 0,
                          error: `OffscreenCanvas allocation refused (${width}x${height}).` });
        return;
    }

    const ctx2d = canvas.getContext('2d');
    if (!ctx2d) {
      ctx.postMessage({ id, success: false, surfaceLive: false, failedImages: 0, drawn: 0,
                        error: 'Could not get 2D context' });
      return;
    }

    // ---- THE ONE-PIXEL PROOF -------------------------------------------------
    // Before the background fill, before any decode. A surface that fails here
    // will drop every subsequent draw and then encode to black, so spending a
    // 30-second render on it is pure waste. ~1 ms, one pixel.
    if (!assertSurfaceLive(ctx2d, width, height)) {
      ctx.postMessage({ id, success: false, surfaceLive: false, failedImages: 0, drawn: 0,
                        error: `Surface dead at ${width}x${height} (sentinel read-back failed).` });
      return;
    }

    ctx2d.fillStyle = bgColor;
    ctx2d.fillRect(0, 0, width, height);

    for (let i = 0; i < layoutItems.length; i++) {
        if (cancelled.has(id)) { cancelled.delete(id); return; }

        const item = layoutItems[i];
        const imgMeta = orderedImages[i];
        // A null slot is not a failure: the layout can legitimately carry more
        // cells than the pool has sources. It is a HOLE, and it is the caller's
        // job to have not sent one. (See generateBlob's alignment guard.)
        if (!imgMeta || !imgMeta.src) continue;

        try {
            // TWO SOURCES, IN ORDER OF QUALITY.
            //   The preview path draws `previewSrc` (a small, always-live JPEG
            //   blob); the export path draws `src` (the ORIGINAL). So a source
            //   whose original object URL has been revoked — or is a frame the
            //   decoder refuses at full size — renders perfectly in the preview
            //   and vanishes from the export. That asymmetry IS the reported
            //   "partial elements" bug.
            //
            //   A softer fragment beats a hole, every time. We try the original
            //   and fall back to the preview, and only count a failure when
            //   BOTH are gone.
            const imgBitmap = await decodeFirstAvailable([imgMeta.src, imgMeta.fallbackSrc]);
            if (!imgBitmap) throw new Error('no decodable source');

            // EVERY save() IS POPPED IN A `finally`.
            //
            // This whole block already ran inside the outer try/catch, and the
            // catch only counted the failure — so a throw anywhere between
            // save() and restore() (a decoder that dies mid-drawImage is the
            // real one) leaked a canvas state and every LATER fragment in this
            // export inherited the dead fragment's clip. Adding a second save
            // for the twist would have leaked the ROTATION too, which is how a
            // single bad decode turns the rest of the file into a shear. The
            // nesting below is balanced on every path, thrown or not.
            ctx2d.save();
            try {
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

                // TWIST — identical to renderer.ts. Rotate the SAMPLING inside
                // the clip that is already set, then wind the transform back so
                // the 'complex' hairline still traces the unrotated cell.
                // Guarded, so an untwisted export runs exactly the instruction
                // stream it always did.
                const spun = crop.twist !== 0;
                if (spun) {
                    ctx2d.save();
                    ctx2d.translate(crop.tcx, crop.tcy);
                    ctx2d.rotate(crop.twist);
                    ctx2d.translate(-crop.tcx, -crop.tcy);
                }
                try {
                    ctx2d.drawImage(imgBitmap, crop.sx, crop.sy, crop.sw, crop.sh, crop.dx, crop.dy, crop.dw, crop.dh);
                } finally {
                    if (spun) ctx2d.restore();
                }
                imgBitmap.close();
                drawn++;

                if (mode === 'complex') {
                    ctx2d.strokeStyle = '#000';
                    ctx2d.lineWidth = width * 0.001;
                    ctx2d.stroke();
                }
            } finally {
                ctx2d.restore();
            }
        } catch (innerErr) {
            console.warn("Worker image load failed", innerErr);
            failedImages++;
        }
    }

    // THE TITLE, over the finished composition and before the surface re-check
    // — it is the last thing drawn, so a caption that vanished would mean the
    // surface died, which the proof below is what catches.
    try { drawTitlePlan(ctx2d, titlePlanFor(titlePlan, width)); }
    catch (e) { console.warn('Worker title draw failed', e); }

    // ---- THE SECOND PROOF ----------------------------------------------------
    // WebKit enforces a per-PAGE canvas budget and can discard the backing store
    // of an already-valid canvas partway through a long render. The corner that
    // was live before the decodes may be dead after them, so we check again.
    if (!assertSurfaceLive(ctx2d, width, height)) {
      ctx.postMessage({ id, success: false, surfaceLive: false, failedImages, drawn,
                        error: `Surface died during render at ${width}x${height}.` });
      return;
    }

    const blob = await canvas.convertToBlob({ type: 'image/jpeg', quality: 0.92 });

    // failedImages is REPORTED, not thrown. The ladder treats a decode failure
    // as terminal-but-explained rather than as "your device is too small".
    ctx.postMessage({ id, success: true, blob, surfaceLive: true, failedImages, drawn });

  } catch (err: any) {
    ctx.postMessage({ id, success: false, surfaceLive: true, failedImages, drawn,
                      error: err?.message || String(err) });
  }
};
