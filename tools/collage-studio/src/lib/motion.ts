// src/lib/motion.ts
// -----------------------------------------------------------------------------
// THE MOVE — the picture drifts and breathes inside its fragment, over time.
//
// WHY THIS FILE EXISTS
//   Export a collage of PHOTOGRAPHS as a video today and you get a still image
//   encoded for N seconds. That is not an opinion about it — it is written down
//   in the compositor's own tick: "a photos-only scene draws once and stops"
//   (stage.ts), and the capture heartbeat exists so "the recorded file is never
//   a zero-frame track when the composition happens to be static". A video of a
//   still is a picture with a file size.
//
//   This is the time axis. Every fragment slowly pushes in, drifts across and
//   settles back — the Ken Burns move, applied per FRAGMENT rather than per
//   film, which is what a collage makes possible and a single frame does not.
//
// THE SEAM, AND WHY IT IS THE SAME ONE TWIST USES
//   Four surfaces produce pixels here (the still preview, the live Stage that
//   both video recorders capture, the export worker's OffscreenCanvas, and the
//   SVG). All four read their geometry from `calculateSmartCrop`, and
//   `calculateSmartCrop` reads `analysis`. So the per-slot decision is written
//   onto a per-slot COPY of the analysis — exactly as `withFocus` re-points
//   `analysis.face` and `withTwist` writes `analysis.twist` — and steers all
//   four with no new parameter threaded through any of them.
//
//   What a move needs that a twist does not is a CLOCK, and an analysis has no
//   clock. So the split is: the STATIC half (which move, and this fragment's
//   own phase in it) rides the analysis; the TIME half is one extra argument on
//   `calculateSmartCrop`, defaulted to 0. Which is what makes the next
//   paragraph true.
//
// IDENTITY AT t = 0, BY CONSTRUCTION
//   Every move is zero at t = 0 for EVERY fragment. Not "close to zero" — the
//   same object, `NO_MOVE`, returned by reference, so `calculateSmartCrop` can
//   branch on identity and run the instruction stream it always ran.
//
//   That is not a nicety, it is what makes the feature safe to ship: the three
//   surfaces that produce a SINGLE FRAME (the still preview, the raster export,
//   the SVG) never pass a time and are therefore bit-identical to a build
//   without this file, and the video starts on the picture the preview is
//   showing. Same guarantee `scaleLayout` gives at k=1, `twistedDest` gives at
//   angle 0, `planTitle` gives on an empty caption and `gradeSteps` gives on
//   `none`.
//
//   It is also the constraint that shapes the maths. The obvious way to make a
//   collage feel alive is to stagger the fragments — phase-shift each one — and
//   a phase shift inside the wave puts every shifted fragment somewhere OTHER
//   than rest at t = 0. So the stagger cannot live in the phase. It lives in
//   the HARMONIC (a fragment breathes once or twice per cycle, both of which
//   are zero at both ends) and in the DIRECTION (each fragment drifts along its
//   own bearing, out and back). Same liveliness, no discontinuity, no drift
//   away from the still.
//
// PERIODIC, ON A FIXED CYCLE, NOT ON THE EXPORT'S DURATION
//   A classic Ken Burns is a one-way ramp across the length of a shot. This one
//   is a raised cosine over a fixed 12 s, out and back, for two reasons that
//   are both about this app rather than about taste:
//
//     1. The live preview loops forever and has no end to ramp towards. Tying
//        the ramp to the export duration would need that duration on the Stage,
//        which would be a SECOND time contract beside `clipWindow`'s — and the
//        one thing this codebase has learned twice is that a formula living in
//        two places diverges (see the three timelines note in clipWindow.ts).
//     2. The export duration is user-set AND silently clipped by the device cap
//        (videoExport caps at under a minute; iOS crashes above it). A move
//        keyed to duration would make the SAME collage move differently at 10 s
//        and at 30 s, and a capped export would be a different picture from the
//        one that was asked for. Periodic means the file always contains the
//        same motion — just more or less of it.
//
//   The raised cosine `(1 - cos)/2` is chosen over a triangle because its
//   derivative is zero at BOTH ends: the turnaround at mid-cycle and the loop
//   point at the end are both smooth, so a looping preview has no visible snap
//   and an export that runs past one cycle does not tick.
//
// THE PAN CANNOT EXCEED THE ROOM, SO IT IS DERIVED FROM IT
//   `calculateSmartCrop` clamps the source rect inside the image. A pan bigger
//   than the crop's slack therefore does not pan — it CLAMPS, and a clamped
//   fragment sits still while its neighbours move, which reads as a bug in the
//   one place the eye is already looking. The slack, in normalised source
//   units, is (1 - 1/zoom)/2 at worst (the axis where the cover fit uses the
//   whole image). So the pan is defined AS a fraction of that expression rather
//   than as a number that has to be checked against it, which makes "pan
//   without room" unrepresentable instead of merely tested — and makes
//   `pan > 0 => zoom > 1` true by construction.
//
// A FUNCTION OF WHERE THE FRAGMENT IS, NEVER OF THE SLOT INDEX
//   The lesson `twistAngle` already paid for: an arrangement RE-PAIRS photos
//   with fragments, so anything keyed off the slot's position in the draw order
//   makes picking a different arrangement silently re-roll the whole motion
//   field. The phase comes from the fragment's own centre, quantised to the
//   same 1e-6 grid and for the same reason — a cell's normalised centre is the
//   same real number at every render width but not the same float, and the
//   preview and each export tier render at different widths.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------

import { hash01 } from './composition';

/**
 * THE ROSTER KEYS.
 *
 * These ids travel: into saved `.collage` projects, into the SVG's manifest and
 * into the composition code as an INDEX (see `MOVE_IDS`). Renaming one is a
 * breaking change to every project that used it, and REORDERING `MOVE_IDS`
 * silently repoints every code ever minted.
 */
export type MoveId = 'still' | 'push' | 'drift' | 'sway' | 'pulse' | 'wander';

/**
 * Index order for the composition code. `still` is index 0 and must stay there:
 * it is the boot state, the no-op, and what every code minted before this
 * feature existed decodes to.
 */
export const MOVE_IDS: MoveId[] = ['still', 'push', 'drift', 'sway', 'pulse', 'wander'];

/** One full out-and-back, in seconds. */
export const MOVE_CYCLE_SEC = 12;

/** Nothing may push in further than this, whatever a corrupt file or code says. */
export const MAX_MOVE_ZOOM = 1.22;

/**
 * WHERE A FRAGMENT'S BEARING COMES FROM.
 *
 *   `none`    — it does not pan at all.
 *   `field`   — a smooth diagonal gradient across the canvas, so NEIGHBOURS
 *               agree and the surface reads as one camera move.
 *   `lateral` — left or right only, sign from the fragment's own hash.
 *   `hash`    — every fragment on its own bearing; the liveliest and the
 *               noisiest.
 *
 * Every member is reachable from `DEFS` below — a bearing no move can select is
 * an inert control, which is a class this repo has already had to go and remove
 * once.
 */
type Bearing = 'none' | 'field' | 'lateral' | 'hash';

interface MoveDef {
  id: MoveId;
  label: string;
  title: string;
  /** Peak zoom ABOVE 1 at mid-cycle. 0 means the fragment never pushes in. */
  zoom: number;
  /** Fraction of the available pan ROOM to use, 0..1. See the header. */
  pan: number;
  bearing: Bearing;
  /** Do fragments split across two harmonics (a shimmer) or move as one body? */
  stagger: boolean;
  /** Does the zoom AMOUNT vary per fragment? */
  vary: boolean;
}

/**
 * THE MOVES.
 *
 * Six, one of them off. Same bar as the look roster: a single row of chips a
 * thumb can cross in one swipe, in the field's own words — a push-in and a
 * drift are what they are called on a bench, not "Animation Preset 3".
 */
export const MOVES: { id: MoveId; label: string; title: string }[] = [
  { id: 'still',  label: 'STILL',  title: 'No move. The collage as it is.' },
  { id: 'push',   label: 'PUSH',   title: 'Every fragment eases in and back out together. The classic.' },
  { id: 'drift',  label: 'DRIFT',  title: 'One slow camera move across the whole surface.' },
  { id: 'sway',   label: 'SWAY',   title: 'Side to side, neighbours opposing. A gentle rock.' },
  { id: 'pulse',  label: 'PULSE',  title: 'Fragments breathe at different rates. A shimmer.' },
  { id: 'wander', label: 'WANDER', title: 'Every fragment on its own bearing. The liveliest.' },
];

const DEFS: Record<MoveId, MoveDef> = {
  still:  { id: 'still',  label: 'STILL',  title: '', zoom: 0,    pan: 0,    bearing: 'none',    stagger: false, vary: false },
  push:   { id: 'push',   label: 'PUSH',   title: '', zoom: 0.16, pan: 0,    bearing: 'none',    stagger: false, vary: false },
  drift:  { id: 'drift',  label: 'DRIFT',  title: '', zoom: 0.12, pan: 0.90, bearing: 'field',   stagger: false, vary: false },
  sway:   { id: 'sway',   label: 'SWAY',   title: '', zoom: 0.10, pan: 0.95, bearing: 'lateral', stagger: false, vary: false },
  pulse:  { id: 'pulse',  label: 'PULSE',  title: '', zoom: 0.18, pan: 0,    bearing: 'none',    stagger: true,  vary: true  },
  wander: { id: 'wander', label: 'WANDER', title: '', zoom: 0.14, pan: 0.85, bearing: 'hash',    stagger: true,  vary: true  },
};

/** The fragment geometry a phase is read from. Structural, so nothing imports. */
export interface MoveCell { cx?: number; cy?: number; area?: number }

/**
 * WHAT RIDES THE ANALYSIS — the static half of a move.
 *
 * `ph` is the fragment's bearing/harmonic seed in [0,1), already resolved from
 * its position, so the per-frame path never touches geometry again.
 */
export interface MoveSpec {
  id: MoveId;
  ph: number;
}

/** The time-varying half: a zoom multiplier and an anchor nudge, normalised. */
export interface MoveOffset {
  /** Multiplies the caller's zoom. Always >= 1. */
  zoom: number;
  /** Anchor nudge in normalised source units, x and y. */
  ax: number;
  ay: number;
}

/**
 * REST. Returned BY REFERENCE, which is the whole contract: callers branch on
 * `m !== NO_MOVE` and skip the arithmetic entirely, so an unmoved render is the
 * render it has always been rather than one that multiplies by 1.0.
 */
export const NO_MOVE: MoveOffset = Object.freeze({ zoom: 1, ax: 0, ay: 0 }) as MoveOffset;

const num = (v: unknown, dflt: number): number =>
  typeof v === 'number' && Number.isFinite(v) ? v : dflt;

const clamp = (v: number, lo: number, hi: number): number => Math.max(lo, Math.min(hi, v));

/**
 * THE FRAGMENT'S OWN SEED, in [0,1).
 *
 * Quantised to 1e-6 before any use, for the reason `twistAngle` records: a
 * cell's normalised centre is the same real number at every render width and
 * not the same float (1200/0.666 gives 0.49999999999999994 where 4094 gives
 * exactly 0.5), so anything read off it must be told they are the same cell.
 *
 * Missing geometry reads as dead centre, which for the smooth bearings means
 * "no particular direction" — the honest answer for a fragment we cannot place.
 */
export const movePhase = (move: MoveId, cell: MoveCell | null | undefined): number => {
  const def = DEFS[move];
  if (!def || def.id === 'still') return 0;
  const q = (v: number): number => Math.round(v * 1e6) / 1e6;
  const cx = q(clamp(num(cell?.cx, 0.5), 0, 1));
  const cy = q(clamp(num(cell?.cy, 0.5), 0, 1));

  switch (def.bearing) {
    case 'field':
      // A DIAGONAL GRADIENT, not a hash: neighbouring fragments get
      // neighbouring bearings, so the surface reads as one camera move rather
      // than as a crowd. Halved so the whole canvas spans half a turn — a full
      // turn would put opposite corners back on the same bearing.
      return q((cx + cy) / 4);
    case 'lateral':
    case 'hash':
    case 'none':
    default:
      // Position-keyed, NOT slot-keyed — an arrangement re-pairs photos with
      // fragments and must not re-roll the motion field.
      return q(hash01(Math.round(cx * 1e6) * 73856093 ^ Math.round(cy * 1e6) * 19349663));
  }
};

/** Is this move going to move anything? The Stage's "keep the loop alive" test. */
export const isMoving = (spec: unknown): boolean => {
  const s = spec as MoveSpec | null | undefined;
  if (!s || typeof s !== 'object') return false;
  const def = DEFS[s.id as MoveId];
  return !!def && def.id !== 'still' && (def.zoom > 0 || def.pan > 0);
};

/**
 * THE ENVELOPE — 0 at t=0, 1 at mid-cycle, 0 at the end, smooth at both.
 *
 * `k` is the harmonic: 1 breathes once per cycle, 2 twice. Both are exactly
 * zero at t = 0 and at t = CYCLE because k is an integer, which is what lets a
 * fragment be staggered without ever starting anywhere but at rest.
 */
const envelope = (timeSec: number, k: number): number =>
  (1 - Math.cos((2 * Math.PI * k * timeSec) / MOVE_CYCLE_SEC)) / 2;

/**
 * THE MOVE AT A MOMENT.
 *
 * Returns `NO_MOVE` BY REFERENCE whenever nothing should happen — no spec, an
 * id this build does not know, `still`, or a time at which the envelope is
 * exactly zero. Every other answer is a fresh object; there are at most a few
 * dozen fragments and this runs off the draw loop, in `refreshMoveCrops`.
 *
 * Every input is sanitised rather than trusted: the spec arrives off an
 * `analysis`, which comes back from project files and share codes, so a NaN, an
 * Infinity or a 40x zoom from a corrupt manifest all come back as a usable
 * geometry instead of poisoning the crop.
 */
export const sampleMove = (spec: unknown, timeSec: number): MoveOffset => {
  const s = spec as MoveSpec | null | undefined;
  if (!s || typeof s !== 'object') return NO_MOVE;
  const def = DEFS[s.id as MoveId];
  if (!def || def.id === 'still') return NO_MOVE;

  const t = num(timeSec, 0);
  if (t === 0) return NO_MOVE;                 // the identity guarantee, first
  const ph = clamp(num(s.ph, 0), 0, 1);

  // THE HARMONIC. A fragment either breathes once per cycle or twice; the split
  // is the fragment's own seed, so it is stable across renders and widths.
  const k = def.stagger && ph >= 0.5 ? 2 : 1;
  const e = envelope(t, k);
  if (e === 0) return NO_MOVE;                 // exact at every cycle boundary

  // THE ZOOM. `vary` spreads the amount across fragments so a shimmer is not
  // one body pulsing; the floor of 0.45 keeps every fragment visibly in it.
  const amount = def.vary ? 0.45 + 0.55 * hash01(Math.round(ph * 1e6) + 17) : 1;
  const zoom = clamp(1 + def.zoom * amount * e, 1, MAX_MOVE_ZOOM);

  if (def.pan <= 0 || def.bearing === 'none' || zoom <= 1) {
    return { zoom, ax: 0, ay: 0 };
  }

  // THE ROOM, and the pan is a FRACTION OF IT rather than a number checked
  // against it — see the header. At zoom 1 this is exactly 0, so a pan can
  // never be asked for where the crop has no slack to give it.
  const room = (1 - 1 / zoom) / 2;
  const reach = room * clamp(def.pan, 0, 1);

  let dx: number;
  let dy: number;
  if (def.bearing === 'lateral') {
    // Sign only, so neighbours oppose and the surface rocks instead of sliding.
    dx = ph >= 0.5 ? 1 : -1;
    dy = 0;
  } else {
    const theta = 2 * Math.PI * ph;
    dx = Math.cos(theta);
    dy = Math.sin(theta);
  }

  return { zoom, ax: reach * dx, ay: reach * dy };
};

/**
 * The photo as it should MOVE in this one slot.
 *
 * Rides the identical seam `withFocus` and `withTwist` use: every crop path
 * reads its geometry from `calculateSmartCrop`, and `calculateSmartCrop` reads
 * `analysis`. Writing the spec onto a per-slot COPY therefore steers all four
 * surfaces with no new plumbing.
 *
 * `still` hands back the SAME OBJECT by reference, so the default path
 * allocates nothing, invalidates no memo, and produces geometry bit-identical
 * to a build without this feature.
 */
export const withMove = <T extends { analysis?: unknown }>(
  photo: T,
  move: MoveId,
  cell: MoveCell | null | undefined,
): T => {
  if (!photo || !move || move === 'still' || !DEFS[move]) return photo;
  const a = photo.analysis as Record<string, unknown> | null | undefined;
  return {
    ...photo,
    analysis: { ...(a ?? {}), color: (a?.color ?? null), move: { id: move, ph: movePhase(move, cell) } },
  } as T;
};
