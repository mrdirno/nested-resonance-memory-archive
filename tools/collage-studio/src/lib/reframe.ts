// =============================================================================
// THE REFRAME — the picture moves inside its fragment.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// WHAT IT IS, AND WHY IT IS THE RUNG IT IS.
//   Every crop this app has ever drawn was decided FOR you. `analysis.face` is
//   a detector's guess, `analysis.energy` is a fallback, THE FOCUS is a roster
//   of five automatic rules and THE MOVE nudges the anchor on a clock. Not one
//   of them is a way of saying "no, THAT part of THAT photograph". So the most
//   ordinary complaint anyone has ever had about a collage — *this one is
//   cropped through his head* — had exactly two answers here: re-roll the whole
//   wall and hope, or throw the picture away.
//
//   THE REFRAME is the answer that is neither. Drag the picture; it moves.
//
// IT IS A PROPERTY OF THE PHOTOGRAPH, NOT OF THE FRAGMENT — and that decides
// almost everything else about the design.
//   `turnResolve`'s own comment already draws this line: the FACE and the
//   COLOUR travel with the picture, while the FOCUS, the TWIST and the MOVE are
//   properties of the fragment and stay put. A hand-set frame is a CORRECTED
//   FACE, so it belongs on the first side of that line: keyed by asset id, it
//   survives a shuffle, a re-deal, a swap and a turn, which is exactly what you
//   want from a correction you made once. Keyed by SLOT it would have been
//   undone by the next roll — and the whole point of this app is that you roll.
//
// THE ANCHOR IS AN OVERRIDE, NOT A NEW CHANNEL.
//   `calculateSmartCrop` already resolves an anchor as `face || energy ||
//   CENTRE`. This adds ONE term at the front of that chain and nothing else, so
//   all four surfaces that produce pixels — the still preview, the live Stage
//   (which is what both video recorders capture and what the offline render
//   seeks), the export worker and the SVG — inherit it without knowing it
//   exists. There is no second crop path to keep in step.
//
// THE STATE IS THE CROP, SO THERE IS NO STATE TO CARRY.
//   `dragToFrame` takes the geometry the shipped crop function just returned
//   and NOT the previous anchor. That is not a shortcut, it is the fix for the
//   one defect this gesture always has: an anchor that is already clamped
//   (because the picture is at its edge) accumulates invisible travel, and the
//   drag back does nothing for as many pixels as the drag out did nothing for.
//   Reading the position off the CLAMPED rect makes that unrepresentable — the
//   picture stops at its edge and reverses on the very next pixel.
//
// A LEAN ROTATES THE FINGER, NOT THE PICTURE.
//   THE TWIST rotates the SAMPLING inside the fragment, so a dest-space delta
//   is not a source-space delta on a leaning fragment: dragging right would
//   slide the picture diagonally. The drag is rotated by -twist into the
//   picture's own axes before it is converted. Without it a 22-degree lean —
//   the roster's ceiling — sends the picture 37% of the way sideways.
//
// WHAT IT DELIBERATELY DOES NOT DO: change the fragment. Not its cell, not its
//   clip path, not its angle, not its grown destination box. Same discipline as
//   THE TURN, and for the same reason: the wall is a tiling and a moved cell
//   opens a wedge of background.
// =============================================================================

import type { PhotoLike } from './composition';
import type { CropGeometry } from './renderer';

/** A hand-set anchor, in the photograph's own normalised coordinates. */
export interface Frame {
  x: number;
  y: number;
}

/** The only thing this module needs to know about a source. */
export interface SourceSize {
  width: number;
  height: number;
}

const finite = (v: number): boolean => Number.isFinite(v);

/**
 * THE BAND THIS CROP CAN ACTUALLY EXPRESS.
 *
 * `calculateSmartCrop` clamps the source rect inside the image, so an anchor
 * nearer an edge than half a crop is drawn at the same place as one exactly
 * half a crop in. Storing the former would be storing travel nobody can see.
 *
 * DEGENERATE IS THE INTERESTING CASE and it is the common one: at zoom 1 the
 * cover fit touches two edges of the photograph, so ONE axis always has zero
 * room. There the band collapses to the single point 0.5 — "there is nowhere to
 * go on this axis" expressed as a value rather than as a special case.
 */
export const frameBand = (crop: CropGeometry, img: SourceSize) => {
  const hx = img.width > 0 ? crop.sw / 2 / img.width : 0.5;
  const hy = img.height > 0 ? crop.sh / 2 / img.height : 0.5;
  return {
    minX: Math.min(hx, 0.5),
    maxX: Math.max(1 - hx, 0.5),
    minY: Math.min(hy, 0.5),
    maxY: Math.max(1 - hy, 0.5),
  };
};

/** Put a frame inside the band above. Non-finite input lands dead centre. */
export const clampFrame = (f: Frame, crop: CropGeometry, img: SourceSize): Frame => {
  const b = frameBand(crop, img);
  const x = finite(f.x) ? Math.min(Math.max(f.x, b.minX), b.maxX) : 0.5;
  const y = finite(f.y) ? Math.min(Math.max(f.y, b.minY), b.maxY) : 0.5;
  return { x, y };
};

/**
 * WHERE THE PICTURE IS RIGHT NOW, read off the geometry that drew it.
 *
 * The centre of the CLAMPED source rect — see the header. This is the value a
 * drag starts from and the value a reframe is defined as, which is what makes
 * the very first drag a no-op when you do not move: reframing to where you
 * already were changes not one pixel.
 */
export const frameOfCrop = (crop: CropGeometry, img: SourceSize): Frame => ({
  x: img.width > 0 ? (crop.sx + crop.sw / 2) / img.width : 0.5,
  y: img.height > 0 ? (crop.sy + crop.sh / 2) / img.height : 0.5,
});

/**
 * THE GESTURE, AS ARITHMETIC: the picture follows the finger.
 *
 * `dxDest`/`dyDest` are the drag in the SAME space the fragment's box is in
 * (the app's 1200-unit canonical basis), because that is the space the caller
 * can convert a client-pixel delta into with one number.
 *
 * THE THREE CONVERSIONS, IN THE ORDER THEY HAVE TO HAPPEN:
 *   1. -twist, into the picture's own axes (a lean rotates the finger).
 *   2. dest -> source, by the crop's own magnification. `sw/dw` and `sh/dh` are
 *      equal by construction (the cover fit is computed against the dest
 *      aspect) and are taken per axis anyway, because a future non-uniform
 *      dest would fail silently otherwise.
 *   3. NEGATED. Moving the picture right means moving the WINDOW left; the sign
 *      is the whole difference between direct manipulation and a scrollbar.
 */
export const dragToFrame = (
  crop: CropGeometry,
  img: SourceSize,
  dxDest: number,
  dyDest: number,
): Frame => {
  const here = frameOfCrop(crop, img);
  if (!finite(dxDest) || !finite(dyDest)) return clampFrame(here, crop, img);

  const t = finite(crop.twist) ? crop.twist : 0;
  const c = Math.cos(t);
  const s = Math.sin(t);
  const dxp = dxDest * c + dyDest * s;
  const dyp = -dxDest * s + dyDest * c;

  const kx = crop.dw > 0 ? crop.sw / crop.dw : 0;
  const ky = crop.dh > 0 ? crop.sh / crop.dh : 0;

  const x = img.width > 0 ? here.x - (dxp * kx) / img.width : here.x;
  const y = img.height > 0 ? here.y - (dyp * ky) / img.height : here.y;
  return clampFrame({ x, y }, crop, img);
};

/**
 * THE ONE SEAM WITH THE REST OF THE APP, and it is `withFocus`' seam exactly.
 *
 * IDENTITY BY REFERENCE when there is nothing to say. `withFocus` on `auto`,
 * `sampleMove` at rest and `turnAt` on `hold` all hand the same object back,
 * for the same reason: a build with no reframe anywhere must be bit-identical
 * to a build without this file, and an identity check is the only guarantee
 * that survives a refactor. `Object.is` is what the sweep asserts, not
 * `deepEqual`.
 */
export const withReframe = <T extends PhotoLike>(photo: T, frame?: Frame | null): T => {
  if (!photo || !frame || !finite(frame.x) || !finite(frame.y)) return photo;
  const a = photo.analysis;
  return {
    ...photo,
    analysis: {
      ...(a ?? {}),
      frame: { x: frame.x, y: frame.y },
    },
  } as T;
};

/**
 * IS THIS FRAME WORTH KEEPING? A drag that lands back where the automatic
 * anchor already was is not a correction, and storing it would light the
 * Recentre verb on a fragment nobody touched.
 *
 * The tolerance is a HALF PIXEL of the smaller source dimension rather than an
 * epsilon: below that the two crops round to the same integer source rect and
 * draw the same photograph.
 */
export const isMeaningful = (frame: Frame, was: Frame, img: SourceSize): boolean => {
  const px = 0.5 / Math.max(1, Math.min(img.width || 1, img.height || 1));
  return Math.abs(frame.x - was.x) > px || Math.abs(frame.y - was.y) > px;
};
