import { LayoutItem } from '../types';
import { ImageAsset } from '../types';
import { TitlePlan, titlePlanFor, drawTitlePlan } from './title';
import { cssFilterFor, type LookRef } from './grade';
import { sampleMove, NO_MOVE } from './motion';

export interface CropGeometry {
  sx: number; sy: number; sw: number; sh: number;
  dx: number; dy: number; dw: number; dh: number;
  /** Radians to rotate the SAMPLING by, about (tcx,tcy). 0 on the default path. */
  twist: number;
  /** The pivot — the centre of the CELL, never of the grown destination. */
  tcx: number; tcy: number;
}

/** Hard ceiling on any angle that reaches the geometry, wherever it came from. */
const MAX_TWIST = (22 * Math.PI) / 180;

/**
 * The per-slot twist angle carried on an analysis, sanitised.
 *
 * Read here rather than threaded as a parameter because `analysis` is the one
 * channel every crop path already passes through (the live Stage, the static
 * renderer, the export worker, the vector export) — see `composition.withTwist`.
 * A NaN, an Infinity or a corrupt 40-radian value from an old project file all
 * come back as a usable angle instead of poisoning the geometry.
 */
export const twistOf = (analysis: any): number => {
  const t = analysis?.twist;
  if (typeof t !== 'number' || !Number.isFinite(t) || t === 0) return 0;
  return Math.max(-MAX_TWIST, Math.min(MAX_TWIST, t));
};

/**
 * WHERE THE ROTATED SAMPLING HAS TO BE DRAWN so that it still covers the cell.
 *
 * The fragments TILE the canvas. Rotate a cell and you open wedges of background
 * between it and its neighbours, so the rotation goes on the sampling INSIDE the
 * clip path — the hole stays put, the picture leans. But a w x h rectangle
 * rotated by t about its own centre no longer contains the axis-aligned w x h
 * cell: rotate the problem by -t and the cell's extent along the drawn rect's
 * own axes is w|cos t| + h|sin t| by w|sin t| + h|cos t|, which is therefore the
 * exact size the drawn rect must reach. Anything smaller and the background
 * shows at the four corners — the same defect the tiling argument avoided, moved
 * inward where it is harder to see and easier to ship.
 *
 * ONE definition, TWO callers (`calculateSmartCrop` and the Stage's draw-item
 * builder), because a second copy of this arithmetic is a second thing to get
 * wrong — see the "never a copy" note on `stage.ts:crop`.
 *
 * At twist 0 it returns the box's own numbers by construction rather than by
 * arithmetic, so the untwisted path is bit-identical to a build without twist.
 */
export const twistedDest = (
  box: {x:number, y:number, w:number, h:number},
  twist: number,
): { dx:number; dy:number; dw:number; dh:number; tcx:number; tcy:number; twist:number } => {
  const tcx = box.x + box.w / 2;
  const tcy = box.y + box.h / 2;
  const t = twistOf({ twist });
  if (t === 0) return { dx: box.x, dy: box.y, dw: box.w, dh: box.h, tcx, tcy, twist: 0 };
  const c = Math.abs(Math.cos(t));
  const s = Math.abs(Math.sin(t));
  const dw = box.w * c + box.h * s;
  const dh = box.w * s + box.h * c;
  return { dx: tcx - dw / 2, dy: tcy - dh / 2, dw, dh, tcx, tcy, twist: t };
};

/** The historical anchor rule, and the only place it is written down. */
const CENTRE_ANCHOR = { x: 0.5, y: 0.5 };

export const calculateSmartCrop = (
  box: {x:number, y:number, w:number, h:number},
  img: {width:number, height:number, analysis: any},
  zoom: number = 1.0,
  /**
   * THE MOVE'S CLOCK, in output seconds. See lib/motion.ts.
   *
   * A fourth parameter rather than a fifth channel on `analysis` because a move
   * is the only per-slot decision here that is not a constant: which move, and
   * this fragment's own phase in it, DO ride the analysis (that is the seam
   * `withFocus` and `withTwist` share) — but the time cannot, because one
   * analysis is drawn at many instants.
   *
   * DEFAULTED TO 0, and 0 is the identity by construction. The three surfaces
   * that produce a single frame — the still preview, the export worker and the
   * SVG — pass nothing and are therefore bit-identical to a build without
   * motion; only the Stage, which is what both video recorders capture and what
   * the offline render seeks, ever passes a real time.
   */
  timeSec: number = 0,
): CropGeometry => {
    // The DESTINATION first: a twist grows it, and the cover fit below has to be
    // computed against the grown aspect or the picture is drawn stretched.
    const dest = twistedDest(box, twistOf(img.analysis));

    const boxAsp = dest.dw / dest.dh;
    const imgAsp = img.width / img.height;

    let drawW, drawH;

    if (imgAsp > boxAsp) {
        drawH = img.height;
        drawW = drawH * boxAsp;
    } else {
        drawW = img.width;
        drawH = drawW / boxAsp;
    }

    // THE MOVE. `sampleMove` returns the shared `NO_MOVE` BY REFERENCE whenever
    // nothing should happen, so the untouched path is guarded by an identity
    // check rather than by arithmetic that happens to be a no-op — no multiply
    // by 1.0, no add of 0, no float that could round differently than it did
    // before this feature existed.
    const move = sampleMove(img.analysis?.move, timeSec);
    const moving = move !== NO_MOVE;

    const cropW = moving ? drawW / (zoom * move.zoom) : drawW / zoom;
    const cropH = moving ? drawH / (zoom * move.zoom) : drawH / zoom;

    // GUARDED. The old unconditional `img.analysis.face` threw on any asset that
    // arrived without an analysis, which every caller then had to work around
    // (stage.ts kept a FALLBACK_ANALYSIS constant purely for this). A centred
    // anchor is what all of them substituted; it belongs here, once.
    const an = img.analysis || {};
    // THE REFRAME goes at the FRONT of this chain and is the whole of that
    // feature's contact with the geometry (lib/reframe.ts). A hand-set frame is
    // a corrected FACE, so it overrides the detector, the focus roster's
    // re-pointed face and the energy fallback alike — the one thing that beats
    // an automatic guess is somebody saying where to look. Absent on every
    // asset nobody has dragged, so the default path is the chain it always was.
    const anchor = an.frame || an.face || an.energy || CENTRE_ANCHOR;

    // The move nudges the ANCHOR, not the finished rect: the clamp below is what
    // keeps the crop inside the image, and a pan applied after it would leave
    // that guarantee behind. `motion.sampleMove` sizes its own reach from the
    // slack this zoom leaves, so in the ordinary centred case the clamp has
    // nothing to do — but it stays the backstop for an off-centre anchor, which
    // could already reach an edge before any of this existed.
    const ax = (moving ? anchor.x + move.ax : anchor.x) * img.width;
    const ay = (moving ? anchor.y + move.ay : anchor.y) * img.height;

    let sx = ax - (cropW / 2);
    let sy = ay - (cropH / 2);

    sx = Math.max(0, Math.min(img.width - cropW, sx));
    sy = Math.max(0, Math.min(img.height - cropH, sy));

    return {
      sx, sy, sw: cropW, sh: cropH,
      dx: dest.dx, dy: dest.dy, dw: dest.dw, dh: dest.dh,
      twist: dest.twist, tcx: dest.tcx, tcy: dest.tcy,
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
  bgColor: string = '#050505', // New param
  /** THE TITLE, planned once at `TITLE_BASIS` by the caller. Null draws nothing. */
  titlePlan: TitlePlan | null = null,
  /** THE LOOK — the colour grade. `'none'` (the default) touches nothing. */
  look: LookRef | null = null,
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

  // THE LOOK — set ONCE, after the background and before the fragments.
  //
  // AFTER the fill because the grade belongs to the PHOTOGRAPHS: the background
  // is a colour the user picked off a swatch and it must come out the colour
  // they picked. Set once rather than per item because every fragment carries
  // the same grade and `save()`/`restore()` inside the loop preserve it — the
  // state each item restores to is this one. Guarded on `'none'` so an ungraded
  // render never touches `ctx.filter` at all and is bit-identical to a build
  // without this feature.
  const gradeCss = cssFilterFor(look);
  if (gradeCss !== 'none') ctx.filter = gradeCss;

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

    // TWIST — rotate the SAMPLING, inside the clip that is already set. The clip
    // was taken in unrotated space and stays there, so the fragment keeps its
    // exact tiled outline; only what shows through it leans. The transform is
    // wound back before the hairline, which traces the CELL and would otherwise
    // be stroked at the picture's angle.
    if (crop.twist) {
      ctx.save();
      ctx.translate(crop.tcx, crop.tcy);
      ctx.rotate(crop.twist);
      ctx.translate(-crop.tcx, -crop.tcy);
    }
    ctx.drawImage(img, crop.sx, crop.sy, crop.sw, crop.sh, crop.dx, crop.dy, crop.dw, crop.dh);
    if (crop.twist) ctx.restore();

    // Style overlays
    if (mode === 'complex') {
        ctx.strokeStyle = '#000'; 
        ctx.lineWidth = width * 0.001; 
        ctx.stroke();
    }
    ctx.restore();
  }

  // The grade comes OFF before the caption. A title is something written on the
  // finished picture, not a thing in it — grading it would tint the scrim and
  // desaturate white text on `mono`, which is a caption that changed colour
  // because of a filter applied to the photographs underneath it.
  if (gradeCss !== 'none') ctx.filter = 'none';

  // THE TITLE goes on LAST, over every fragment — it is a caption on the
  // finished picture, not a fragment of it. Scaled from the plan's basis to
  // this canvas, so the preview and every export carry the identical wrap.
  drawTitlePlan(ctx, titlePlanFor(titlePlan, LOGICAL_W));

  return canvas;
};
