// =============================================================================
// THE GRAB — press a fragment, drag its picture, let go. From any view.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// License: GPL-3.0
//
// WHY THIS EXISTS. THE REFRAME (lib/reframe.ts) shipped the arithmetic of a
//   picture that follows the finger inside its fragment, and hid it behind three
//   steps nobody found: Expand preview, tap a fragment to ARM it, then drag. A
//   Collage user wished, in their own words, for "the ability to move the image
//   or video around if I click a tile and hold down with a finger and drag and
//   release to set new image focal point". Measured on the build before this
//   module, that exact gesture (real Chromium touch through CDP, held 600 ms,
//   dragged 160 px, released, on a Pixel 5 in the editing view) moved the
//   picture 0.0 RGB. For them the feature did not exist.
//
// WHAT THIS MODULE DECIDES, AND NOTHING ELSE: what ONE pointer's press on a
//   fragment turns out to MEAN — a TAP (the shipped verb: pin, arm or trade,
//   byte for byte), a DRAG (the reframe) or a HOLD (the grab announced) — and
//   whether the click the browser may send afterwards belongs to the drag. It
//   never touches geometry; `dragToFrame` owns that, and it never touches the
//   DOM; App wires both.
//
// A DRAG IS DISTANCE, A HOLD IS ONLY A SIGNAL. Nothing else on this page wants a
//   drag that starts on the artwork: the page is one fixed surface that never
//   scrolls (styles/base.css), overscroll is off, and the viewport refuses to
//   zoom. So the thing a drag has to be told apart from is the TAP, and a tap is
//   told apart by distance, not by time. The hold is kept as FEEDBACK — the
//   fragment lights up under a still finger, which is how the wisher's own
//   gesture ("hold down ... and drag") announces that it has been understood —
//   but a finger that presses and moves at once is not made to wait for it.
//   `needsHold` stays a rule rather than a constant so a surface that DOES
//   scroll can ask for the long-press grammar without a second module.
//
// THE SLOP IS PER POINTER KIND. The shipped armed drag used 5 px for every
//   pointer. A fingertip is not a cursor: a tap on glass wanders further than
//   that, and on the unarmed fragments the tap is the PIN — so a 6 px tremble
//   would have become a 6 px reframe and eaten the pin it was meant to be.
//   10 px for a fingertip, so a tap that wanders 8 px on glass is still the
//   pin; a mouse keeps the shipped 5, which is where every desktop OS puts its
//   own drag threshold.
//
// THE CLICK AFTER A DRAG IS EATEN BY TIME, NOT BY A FLAG. A mouse drag ends in a
//   click on the element it started on; a TOUCH drag ends in none, because the
//   browser only synthesises a click for a tap. The shipped reframe set a flag
//   at pointerup and cleared it in the click handler — so after a touch drag the
//   flag outlived the gesture and swallowed the NEXT genuine tap. Measured on
//   the build before this module: arm, drag by touch, tap once — the puck stayed
//   up; it took a second tap. `clickBelongsToDrag` is bounded by the moment the
//   drag ended, so a click that is not the drag's own is never taken.
// =============================================================================

export type PointerKind = 'mouse' | 'pen' | 'touch';

export interface GrabRules {
  /** A still press this long announces the grab (the fragment lights up). */
  holdMs: number;
  /** How far a press may wander and still be a tap, in CSS px, per kind. */
  slop: Record<PointerKind, number>;
  /** Must the hold come before a drag may start? (A scrolling surface would say yes for touch.) */
  needsHold: Record<PointerKind, boolean>;
  /** A click this soon after a drag ended is the drag's own click. */
  clickWindowMs: number;
}

export const GRAB: GrabRules = {
  holdMs: 350,
  slop: { mouse: 5, pen: 6, touch: 10 },
  needsHold: { mouse: false, pen: false, touch: false },
  // Compared on EVENT timestamps (the pointerup's and the click's), which a busy
  // main thread delays together, so the window measures the gesture and not the
  // frame rate. A drag's own click lands within a few ms of its release; no
  // finger lifts and taps again inside a quarter of a second.
  clickWindowMs: 250,
};

/**
 * pressed  — down, still inside the slop, not yet held.
 * held     — still inside the slop, and still for `holdMs`: the grab is announced.
 * dragging — past the slop: every move is a reframe.
 * refused  — moved past the slop before a REQUIRED hold: the surface's own
 *            gesture (a scroll) owns the rest of it. Never reached under the
 *            default rules, where no kind needs a hold.
 */
export type GrabPhase = 'pressed' | 'held' | 'dragging' | 'refused';

export interface Grab {
  pid: number;
  kind: PointerKind;
  phase: GrabPhase;
  /** The press point. Every drag is measured from HERE, so the spot of the picture under the finger stays under it. */
  ox: number;
  oy: number;
  /** When the press landed. */
  t0: number;
}

export type GrabEvent =
  | { type: 'move'; pid: number; x: number; y: number; t: number }
  | { type: 'hold'; pid: number; t: number }
  | { type: 'up'; pid: number; t: number }
  | { type: 'cancel'; pid: number; t: number };

export interface GrabStep {
  /** The gesture after this event; null once it is over. */
  grab: Grab | null;
  /** When the picture must move: the TOTAL displacement since the press, in client px. */
  drag: { dx: number; dy: number } | null;
  /** True on exactly the event that announced the hold. */
  heldNow: boolean;
  /** On the event that ENDS the gesture: did it end a drag whose click may follow? */
  endedDrag: boolean;
}

const finite = (v: number) => Number.isFinite(v);

/** Anything the Pointer Events spec might report collapses onto the three kinds this module knows. */
export const pointerKind = (t: string | null | undefined): PointerKind =>
  t === 'touch' ? 'touch' : t === 'pen' ? 'pen' : 'mouse';

export const pressGrab = (pid: number, kind: PointerKind, x: number, y: number, t: number): Grab => ({
  pid, kind, phase: 'pressed',
  ox: finite(x) ? x : 0, oy: finite(y) ? y : 0,
  t0: finite(t) ? t : 0,
});

const idle = (grab: Grab | null): GrabStep => ({ grab, drag: null, heldNow: false, endedDrag: false });

/**
 * ONE EVENT IN, THE GESTURE'S NEXT STATE OUT. Pure: same inputs, same answer,
 * nothing retained between calls but the `Grab` the caller hands back.
 *
 * A LATE TIMER IS STILL A HOLD. The hold is a `setTimeout`, and a main thread
 * busy drawing the Stage can deliver it late or not before the next move. The
 * clock, not the timer, is the authority: a move that arrives after `holdMs` of
 * stillness is treated as having been held, so a slow frame can never turn the
 * wisher's hold-and-drag into a refused one.
 */
export function stepGrab(g: Grab | null, e: GrabEvent, rules: GrabRules = GRAB): GrabStep {
  if (!g) return idle(null);
  // ONE FINGER OWNS THE GESTURE. A second pointer is not this gesture's business.
  if (e.pid !== g.pid) return idle(g);

  if (e.type === 'up' || e.type === 'cancel') {
    // A cancel is the browser or the OS taking the pointer away; no click
    // follows it, so there is nothing of the drag's to eat.
    return { grab: null, drag: null, heldNow: false, endedDrag: e.type === 'up' && g.phase === 'dragging' };
  }

  const elapsed = finite(e.t) ? e.t - g.t0 : 0;

  if (e.type === 'hold') {
    if (g.phase !== 'pressed' || !(elapsed >= rules.holdMs)) return idle(g);
    return { grab: { ...g, phase: 'held' }, drag: null, heldNow: true, endedDrag: false };
  }

  // --- move ---
  if (g.phase === 'refused') return idle(g);
  if (!finite(e.x) || !finite(e.y)) return idle(g);
  const dx = e.x - g.ox;
  const dy = e.y - g.oy;

  if (g.phase === 'dragging') return { grab: g, drag: { dx, dy }, heldNow: false, endedDrag: false };

  if (Math.hypot(dx, dy) < rules.slop[g.kind]) {
    // Still a tap's tremble. A hold that the timer has not delivered yet is
    // still a hold (see above) — announce it here rather than lose it.
    if (g.phase === 'pressed' && elapsed >= rules.holdMs) {
      return { grab: { ...g, phase: 'held' }, drag: null, heldNow: true, endedDrag: false };
    }
    return idle(g);
  }

  // PAST THE SLOP. Held, or a kind that never needs holding, or a hold the
  // clock already vouches for: the picture moves.
  const heldByClock = g.phase === 'pressed' && elapsed >= rules.holdMs;
  if (g.phase === 'held' || heldByClock || !rules.needsHold[g.kind]) {
    return { grab: { ...g, phase: 'dragging' }, drag: { dx, dy }, heldNow: heldByClock, endedDrag: false };
  }
  return { grab: { ...g, phase: 'refused' }, drag: null, heldNow: false, endedDrag: false };
}

/**
 * IS THIS CLICK THE DRAG'S OWN? Only when a drag ended, and only within the
 * window after it ended — so a touch drag, which ends in no click at all,
 * cannot bank a swallow that lands on the next genuine tap.
 */
export const clickBelongsToDrag = (dragEndedAt: number | null, now: number, rules: GrabRules = GRAB): boolean =>
  dragEndedAt !== null && finite(dragEndedAt) && finite(now) && now >= dragEndedAt && now - dragEndedAt <= rules.clickWindowMs;
