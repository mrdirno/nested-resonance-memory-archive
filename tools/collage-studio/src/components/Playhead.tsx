// src/components/Playhead.tsx
// -----------------------------------------------------------------------------
// THE PLAYHEAD — the take's clock, on the bar, draggable.
//
// The arithmetic is `lib/playhead.ts`; this file is the pixels and the two
// pieces of plumbing that cannot be pure:
//
// DECISION A — THE POSITION IS WRITTEN TO THE DOM, NEVER TO REACT STATE. A
//   playhead changes sixty times a second and a `setState` at that rate
//   re-renders the whole transport — every clip chip, every duration button —
//   sixty times a second, on the one surface whose entire architecture is a
//   frame budget. The Stage publishes its clock through a plain getter for
//   exactly this reason (`onStatus` is deduped and event-driven BY CONTRACT and
//   would have to be broken to carry a time), so the loop below reads that
//   getter and writes `input.value`, one CSS variable and one text node
//   directly. Nothing above this component re-renders while the preview plays.
//
// DECISION B — THE LOOP BACKS OFF WHEN THE CLOCK IS STILL. A rAF that never
//   stops is exactly the cost the Stage's own demand-driven tick refuses to pay
//   ("nothing playing and nothing dirty -> NO rAF is rescheduled"), and a
//   playhead sitting at 0 under a still collage would reintroduce it from the
//   outside. After `IDLE_FRAMES` frames with no movement the loop drops to a
//   250 ms timer and goes back to rAF the moment the clock moves again — so a
//   parked or idle preview costs four wake-ups a second instead of sixty, and a
//   playing one is still perfectly smooth.
//
// DECISION C — THE FINGER OWNS THE CONTROL WHILE IT IS DOWN. `scrubTo` parks
//   the Stage synchronously, so in practice the clock stops before the first
//   seek resolves — but "in practice" is not a guarantee, and one frame of the
//   loop writing `input.value` mid-drag would yank the thumb out from under the
//   thumb. The pointer flag is the guarantee.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------
import React, { useCallback, useEffect, useRef } from 'react';
import type { Stage } from '../lib/stage';
import {
  PLAYHEAD_STEP_SEC, PUMP_IDLE, fadeMarks, formatPosition, formatSpan,
  fractionOf, lapAdjust, pumpRequest, pumpSettle, seekFromInput,
  type PumpState,
} from '../lib/playhead';

/** Frames of a motionless clock before the loop drops to a timer — DECISION B. */
const IDLE_FRAMES = 40;
/** The idle poll. Four wake-ups a second is imperceptible on a parked preview. */
const IDLE_POLL_MS = 250;
/** Below this the position has not moved enough to be worth a DOM write. */
const PAINT_EPSILON = 0.008;

export interface PlayheadProps {
  stageRef: React.MutableRefObject<Stage | null>;
  /** The ruler, in seconds — already clamped to what the device can record. */
  take: number;
  /** The fade AS REQUESTED; the wedges read `fadeSpan` themselves. */
  fadeSec: number;
  /** A take is running: the clock is the recorder's now, not the viewer's. */
  disabled: boolean;
}

export const Playhead: React.FC<PlayheadProps> = ({ stageRef, take, fadeSec, disabled }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const readRef = useRef<HTMLSpanElement>(null);
  const pumpRef = useRef<PumpState>(PUMP_IDLE);
  const draggingRef = useRef(false);

  // --- DECISION A + B: paint from the clock, back off when it is still -------
  useEffect(() => {
    let raf = 0;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;
    let last = -1;
    let idle = 0;

    const paint = () => {
      const stage = stageRef.current;
      if (stage) {
        // `lapAdjust` again, even though the Stage laps its own clock: this is
        // the one frame after a take change where the two can disagree, and a
        // bar that briefly draws past its own maximum is the exact lie the
        // module exists to forbid.
        const pos = lapAdjust(stage.takePosition, take).position;
        if (Math.abs(pos - last) < PAINT_EPSILON) {
          idle++;
        } else {
          idle = 0;
          last = pos;
          const el = inputRef.current;
          if (el && !draggingRef.current) {          // DECISION C
            el.value = String(pos);
            el.style.setProperty('--fill', `${fractionOf(pos, take) * 100}%`);
          }
          if (readRef.current) readRef.current.textContent = formatPosition(pos);
        }
      }
      if (stopped) return;
      if (idle >= IDLE_FRAMES) timer = setTimeout(paint, IDLE_POLL_MS);
      else raf = requestAnimationFrame(paint);
    };

    raf = requestAnimationFrame(paint);
    return () => {
      stopped = true;
      cancelAnimationFrame(raf);
      if (timer !== undefined) clearTimeout(timer);
    };
  }, [stageRef, take]);

  // --- the seek pump: at most one render in flight, latest always wins ------
  const seek = useCallback((t: number) => {
    const stage = stageRef.current;
    if (!stage) return;
    const asked = pumpRequest(pumpRef.current, t);
    pumpRef.current = asked.state;
    if (!asked.start) return;
    const run = (at: number) => {
      // SETTLE ON BOTH OUTCOMES. `renderAtTime` is written never to reject, but
      // a pump left holding `inFlight` after one unexpected throw stops
      // accepting seeks for the life of the mount — the control would simply go
      // dead, silently, and only for the user it happened to.
      const after = () => {
        const done = pumpSettle(pumpRef.current);
        pumpRef.current = done.state;
        if (done.next !== null) run(done.next);
      };
      void stage.scrubTo(at).then(after, after);
    };
    run(t);
  }, [stageRef]);

  if (!(take > 0)) return null;

  const marks = fadeMarks(take, fadeSec);

  return (
    <div className="flex items-center gap-2 basis-full min-w-0">
      <div className="flex-1 min-w-0">
        <input
          ref={inputRef}
          type="range"
          min={0}
          max={take}
          step={PLAYHEAD_STEP_SEC}
          defaultValue={0}
          disabled={disabled}
          onPointerDown={() => { draggingRef.current = true; }}
          onPointerUp={() => { draggingRef.current = false; }}
          onPointerCancel={() => { draggingRef.current = false; }}
          onLostPointerCapture={() => { draggingRef.current = false; }}
          onInput={(e) => {
            const el = e.currentTarget;
            const t = seekFromInput(el.value, take);
            el.style.setProperty('--fill', `${fractionOf(t, take) * 100}%`);
            if (readRef.current) readRef.current.textContent = formatPosition(t);
            seek(t);
          }}
          aria-label={`Playhead — scrub the ${formatSpan(take)} take`}
          title={disabled
            ? 'Finish the take before scrubbing.'
            : `Drag to see any moment of the ${formatSpan(take)} take. `
              + 'Arrow keys step a tenth of a second.'}
          /* `--fill` IS NOT OPTIONAL: the app's global range track is a gradient
             stopped at `var(--fill, 50%)`, so a bar that never sets it opens
             half-filled with the thumb at zero — the fill contradicting the
             handle it belongs to, on the one control whose whole job is to say
             where you are. Set here for the first paint and by the loop after. */
          style={{ ['--fill' as string]: '0%' } as React.CSSProperties}
          className="w-full"
        />
        {/* THE FADE, AS ITS OWN SHAPE. Two triangles under the ruler, drawn from
            `fadeSpan` rather than from the number on the chip — so when a 2s
            fade is clamped to 1.5s by a 3s take, the picture of it moves too.
            Three pixels tall and aria-hidden: it is a second reading of a fact
            the fade chip already states, not a control. */}
        {marks && (
          <div className="relative h-[3px] w-full -mt-0.5" aria-hidden="true">
            <div
              className="absolute inset-y-0 left-0 bg-emerald-400/40"
              style={{ width: `${marks.inEnd * 100}%`, clipPath: 'polygon(0 100%, 100% 0, 100% 100%)' }}
            />
            <div
              className="absolute inset-y-0 right-0 bg-emerald-400/40"
              style={{ left: `${marks.outStart * 100}%`, clipPath: 'polygon(0 0, 100% 0, 0 100%)' }}
            />
          </div>
        )}
      </div>
      <span
        className="shrink-0 text-[10px] tabular-nums text-gray-300 tracking-tight"
        data-testid="playhead-readout"
      >
        <span ref={readRef}>0:00.0</span>
        <span className="text-gray-600">{` / ${formatSpan(take)}`}</span>
      </span>
    </div>
  );
};
