// src/components/TakeStrip.tsx
// -----------------------------------------------------------------------------
// THE STRIP — the ruler stops measuring an empty ten seconds.
//
// The arithmetic is `lib/takeMap.ts`; this file is the pixels. It sits directly
// under the playhead's own bar and shares its axis, so a scrub crosses the marks
// it is drawn against — which is the whole reason the two are the same widget
// and not two.
//
// DECISION A — PERCENT ONLY, NO PIXEL EVER. Every position and width here is a
//   fraction of the take rendered as a percentage, so the strip is the width of
//   whatever holds it at 320 px and at 1600 px alike and the mobile law is
//   satisfied by CONSTRUCTION rather than by a measurement that has to be
//   re-taken every time the dock's contents change. The one pixel value in the
//   file is the SEAM (`calc(... - 1px)`), which shrinks a pass rather than
//   growing the row.
//
// DECISION B — THE ROWS ARE READ IN A COLOUR CODE, NOT IN LABELS. There is no
//   room for a name beside a 5 px bar on a phone, and a legend is a second
//   thing to learn. Emerald is SOUND everywhere in this app already (the fade
//   wedges, the per-clip speaker chips), so the music lane is emerald and the
//   picture lanes are sky — and a CUT, which is neither, is white. The lanes
//   are in the same order as the clip chips one row below, which is what says
//   which lane is which without spending a pixel of width on saying it.
//
//   THE DRIFT IS THE FOURTH, AND IT IS AMBER — the one hue this app's dock has
//   not already spoken for, and the readable one on a dirty screen in daylight.
//   It goes ABOVE the source lanes, under the cuts, because both of those rows
//   are properties of the WHOLE WALL and the lanes below are properties of one
//   picture each — which is also what keeps DECISION B's position-reading true
//   (`takeMap.ts` DECISION 5): a row with no chip under it must never sit in
//   the run of rows that are read off the chips.
//
// DECISION C — IT IS A SECOND READING, SO IT IS `aria-hidden`, AND THE READING
//   IS ALSO AVAILABLE AS TEXT. Same call the fade wedges made: a screen reader
//   crawling twenty absolutely-positioned divs learns nothing, so the shapes are
//   hidden and one `sr-only` sentence states what they say. `title` carries the
//   same sentence per lane for a pointer.
//
// DECISION D — NOTHING TO SHOW MEANS NO STRIP. A collage under no music with
//   the turn on HOLD and no move has nothing in its take at all, and an empty
//   tray under the ruler would say the take is empty rather than still.
//   THE TEXT THIS DECISION SHIPPED WITH WAS THE BUG: it read "has nothing in
//   its take but the drift", and drew nothing anyway — so the one composition
//   this app is named for showed a bare ruler over ten seconds it was busy for.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// -----------------------------------------------------------------------------
import React from 'react';
import {
  driftLabel, laneLabel, type LanePasses, type TakeLane, type TakeMap,
} from '../lib/takeMap';

export interface TakeStripProps {
  map: TakeMap;
  /** The ruler, in seconds — only for the labels; every geometry is a fraction. */
  take: number;
}

const pc = (f: number): string => `${(f * 100).toFixed(4)}%`;

/** The trough a lane's passes sit in. Dark enough to read as an empty track on
 *  a phone in daylight, light enough that a lane with one pass still shows the
 *  take it did not fill. */
const TROUGH = 'relative h-[6px] w-full overflow-hidden rounded-[1px] bg-white/[0.06]';

/** The three things a row can be about — DECISION B. */
type RowKind = TakeLane['kind'] | 'drift';

const laneTint = (kind: RowKind, whole: boolean): string => {
  if (kind === 'music') return whole ? 'bg-emerald-400/55' : 'bg-emerald-400/20';
  if (kind === 'drift') return whole ? 'bg-amber-400/55' : 'bg-amber-400/20';
  return whole ? 'bg-sky-400/55' : 'bg-sky-400/20';
};

const DENSE_RGBA: Record<RowKind, string> = {
  music: 'rgba(52,211,153,0.55)',
  drift: 'rgba(251,191,36,0.55)',
  clip: 'rgba(56,189,248,0.55)',
};

/** TOO FAST TO DRAW — DECISION 3 in `takeMap.ts`. A hatch rather than a solid
 *  bar, because a solid bar is exactly what a clip that never repeats looks
 *  like and this is the opposite of that. */
const denseFill = (kind: RowKind): React.CSSProperties => ({
  backgroundImage:
    `repeating-linear-gradient(90deg, ${DENSE_RGBA[kind]} 0 2px, transparent 2px 4px)`,
});

/** ONE ROW'S PASSES. Extracted the moment there was a SECOND kind of row: the
 *  drift and a source are drawn by the same rules — the seam is a shrink, the
 *  floor is a pixel — and two copies of that is two chances to draw a lane that
 *  stops before the take does. */
const Passes: React.FC<{ passes: LanePasses; kind: RowKind }> = ({ passes, kind }) => (
  <>
    {passes.dense
      ? <div className="absolute inset-0" style={denseFill(kind)} />
      : passes.segments.map((s, i) => (
        <div
          key={i}
          className={`absolute inset-y-0 ${laneTint(kind, s.whole)}`}
          style={{
            left: pc(s.start),
            // THE SEAM IS A SHRINK, NOT A GAP. Subtracting a pixel from the
            // pass keeps the row's geometry in fractions (DECISION A) while
            // still drawing the instant the source starts over — which is the
            // only thing this lane is here to say.
            //
            // AND THE FLOOR IS 1px, because the subtraction goes NEGATIVE on a
            // pass narrower than two pixels (a 0.3% final lap on a 227px bar is
            // 0.68px) and CSS clamps a negative width to zero — so the lane
            // would appear to stop before the take ends, which is the one thing
            // a lane must never say wrongly.
            width: `max(1px, calc(${pc(s.end - s.start)} - 1px))`,
          }}
        />
      ))}
  </>
);

export const TakeStrip: React.FC<TakeStripProps> = ({ map, take }) => {
  if (!map || map.empty) return null;                                // DECISION D

  const { cuts, drift, lanes, hiddenLanes, unknownLanes } = map;
  const cutBand = Math.max(cuts.fade, 0.002);

  /** The whole strip in one sentence — DECISION C. */
  const spoken = [
    cuts.at.length > 0
      ? `${cuts.at.length} cut${cuts.at.length === 1 ? '' : 's'} in this take`
        + (cuts.hidden > 0 ? `, ${cuts.hidden} more not drawn` : '')
      : '',
    drift ? driftLabel(drift, take) : '',
    ...lanes.map((l) => laneLabel(l, take)),
    hiddenLanes > 0 ? `${hiddenLanes} more source${hiddenLanes === 1 ? '' : 's'} not drawn` : '',
    unknownLanes > 0 ? `${unknownLanes} source${unknownLanes === 1 ? '' : 's'} of unknown length` : '',
  ].filter(Boolean).join('. ');

  return (
    <>
      <div
        className="w-full mt-[3px] flex flex-col gap-[2px]"
        aria-hidden="true"
        data-testid="take-strip"
        data-cuts={cuts.at.length}
        data-cuts-hidden={cuts.hidden}
        data-drift={drift ? drift.laps : 0}
        data-lanes={lanes.length}
        data-lanes-hidden={hiddenLanes}
        data-lanes-unknown={unknownLanes}
      >
        {cuts.at.length > 0 && (
          <div className={TROUGH} data-testid="take-strip-cuts">
            {cuts.at.map((f, i) => (
              <React.Fragment key={i}>
                {/* THE DISSOLVE, as its own width. `march` spends 0.7s of every
                    5s cross-fading and THE PACE keeps that ratio at every
                    tempo — a hairline would draw a cut as an instant it is not. */}
                <div
                  className="absolute inset-y-0 bg-white/20"
                  style={{ left: pc(f), width: pc(cutBand) }}
                />
                {/* 2px, and its LEFT EDGE is the instant — the dissolve runs to
                    the right of it, so a centred tick would put the cut half a
                    pixel before it happens and make the band lopsided. One
                    physical pixel is not enough on a phone in daylight; this is
                    the mark the whole strip is read by. */}
                <div
                  className="absolute inset-y-0 w-[2px] bg-white/90"
                  style={{ left: pc(f) }}
                  data-testid="take-strip-cut"
                />
              </React.Fragment>
            ))}
          </div>
        )}

        {/* THE DRIFT — DECISION 5 in `takeMap.ts`. Above the source lanes and
            below the cuts, because it is a fact about the whole wall and not
            about any one picture in it. A seam here is an instant the collage
            is back at REST, which is the same instant the still preview, the
            raster export and the SVG are all drawing. */}
        {drift && (
          <div
            className={TROUGH}
            title={driftLabel(drift, take)}
            data-testid="take-strip-drift"
            data-laps={drift.laps}
            data-dense={drift.dense ? '1' : '0'}
          >
            <Passes passes={drift} kind="drift" />
          </div>
        )}

        {lanes.map((lane) => (
          <div
            key={lane.id}
            className={TROUGH}
            title={laneLabel(lane, take)}
            data-testid="take-strip-lane"
            data-kind={lane.kind}
            data-laps={lane.laps}
            data-dense={lane.dense ? '1' : '0'}
          >
            <Passes passes={lane} kind={lane.kind} />
          </div>
        ))}

        {/* NO SILENT CAPS, ON THE SCREEN AND NOT ONLY IN THE MARKUP. A ninth
            source or one whose length never probed simply has no row, and a
            strip that quietly stops listing is worse than one that says it
            stopped. Only rendered when there is something to admit. */}
        {(hiddenLanes > 0 || unknownLanes > 0) && (
          <div className="text-[9px] leading-none tracking-wide text-gray-500 pt-[1px]">
            {[
              hiddenLanes > 0 ? `+${hiddenLanes} more` : '',
              unknownLanes > 0 ? `${unknownLanes} unmeasured` : '',
            ].filter(Boolean).join(' · ')}
          </div>
        )}
      </div>
      <span className="sr-only">{spoken}</span>
    </>
  );
};
