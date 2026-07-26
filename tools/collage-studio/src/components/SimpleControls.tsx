import React, { useCallback, useEffect, useRef } from 'react';
import {
  Layout, Grid, Plus, Minus, RefreshCw, Shuffle, Waves, Hexagon, Square,
  Triangle, Circle, Octagon, Shapes, Layers, Activity, Lock, ImagePlus
} from 'lucide-react';
import { LayoutMode, PrimitiveType } from '../types';

interface SimpleControlsProps {
  layoutMode: LayoutMode;
  setLayoutMode: (m: LayoutMode) => void;
  primitive: PrimitiveType;
  setPrimitive: (p: PrimitiveType) => void;
  count: number;
  setCount: (fn: (prev: number) => number) => void;
  density: number;
  setDensity: (d: number) => void;
  entropy: number;
  setEntropy: (e: number) => void;
  onRemix: () => void;
  onShuffle: () => void;
  hasImages: boolean;
  isLayoutLocked: boolean;
}

const MODES: { id: LayoutMode; label: string; icon: React.ReactNode; blurb: string }[] = [
  { id: 'minimal',  label: 'Minimal',  icon: <Layout size={18} />,  blurb: 'Few large fragments, lots of open space.' },
  { id: 'balanced', label: 'Balanced', icon: <Grid size={18} />,    blurb: 'An even grid — every fragment weighs the same.' },
  { id: 'complex',  label: 'Complex',  icon: <Hexagon size={18} />, blurb: 'Irregular shards breaking across the frame.' },
];

const VARIANTS: { id: LayoutMode; label: string; icon: React.ReactNode; blurb: string }[] = [
  { id: 'complex', label: 'Shatter', icon: <Hexagon size={16} />, blurb: 'Angular voronoi shards, edge to edge.' },
  { id: 'field',   label: 'Flow',    icon: <Waves size={16} />,   blurb: 'Fragments drift along a flowing field.' },
];

const SHAPES: { id: PrimitiveType; label: string; icon: React.ReactNode; blurb: string }[] = [
  { id: 'rect',    label: 'Square', icon: <Square size={16} />,   blurb: 'Rectangular fragments.' },
  { id: 'tri',     label: 'Tri',    icon: <Triangle size={16} />, blurb: 'Triangular fragments.' },
  { id: 'circle',  label: 'Circle', icon: <Circle size={16} />,   blurb: 'Circular fragments.' },
  { id: 'octagon', label: 'Octa',   icon: <Octagon size={16} />,  blurb: 'Eight-sided fragments.' },
  { id: 'random',  label: 'Mixed',  icon: <Shapes size={16} />,   blurb: 'A different shape family each remix.' },
];

export const SimpleControls: React.FC<SimpleControlsProps> = ({
  layoutMode, setLayoutMode, primitive, setPrimitive, count, setCount,
  density, setDensity, entropy, setEntropy, onRemix, onShuffle,
  hasImages, isLayoutLocked
}) => {

  const isComplexGroup = layoutMode === 'complex' || layoutMode === 'field';
  const usesChaos = layoutMode === 'balanced' || isComplexGroup;
  const effective = Math.max(0, count * density);

  const adjustCount = useCallback((delta: number) => {
    setCount(prev => {
      const step = prev > 25 ? delta * 2 : delta;
      return Math.max(1, prev + step);
    });
  }, [setCount]);

  /* ---- press-and-hold on the stepper --------------------------------------
     Going 12 -> 60 fragments should not cost 48 taps. Hold accelerates; a
     normal tap still runs through onClick so the keyboard path is intact. */
  const holdRef = useRef<number | null>(null);
  const repeatedRef = useRef(false);

  const endHold = useCallback(() => {
    if (holdRef.current !== null) { window.clearTimeout(holdRef.current); holdRef.current = null; }
  }, []);

  const startHold = useCallback((delta: number) => {
    repeatedRef.current = false;
    let delay = 420;
    const tick = () => {
      repeatedRef.current = true;
      adjustCount(delta);
      delay = Math.max(55, delay * 0.7);
      holdRef.current = window.setTimeout(tick, delay);
    };
    holdRef.current = window.setTimeout(tick, delay);
  }, [adjustCount]);

  useEffect(() => endHold, [endHold]);

  const stepProps = (delta: number) => ({
    onPointerDown: () => hasImages && startHold(delta),
    onPointerUp: endHold,
    onPointerLeave: endHold,
    onPointerCancel: endHold,
    onClick: () => { if (repeatedRef.current) { repeatedRef.current = false; return; } adjustCount(delta); },
  });

  const activeMode = MODES.find(m => m.id === layoutMode) ?? MODES[2];
  const activeVariant = VARIANTS.find(v => v.id === layoutMode);
  const activeShape = SHAPES.find(s => s.id === primitive) ?? SHAPES[0];

  const detail = isComplexGroup
    ? (activeVariant?.blurb ?? activeMode.blurb)
    : activeMode.blurb;

  return (
    <div className="ui-dock">

      {/* ---- persistent caption: the whole panel state in one mono line ---- */}
      {hasImages ? (
        <div className="ui-readout" aria-live="polite">
          <span><b>{(isComplexGroup ? activeVariant?.label ?? activeMode.label : activeMode.label).toUpperCase()}</b></span>
          <i>/</i>
          <span>{isComplexGroup ? 'VORONOI' : activeShape.label.toUpperCase()}</span>
          <i>/</i>
          <span><b>{effective}</b> FRAGMENTS</span>
          {density > 1 && <><i>/</i><span>{count}&nbsp;×&nbsp;{density} DENSITY</span></>}
          {usesChaos && <><i>/</i><span>CHAOS {(entropy * 100).toFixed(0)}%</span></>}
        </div>
      ) : (
        <div className="ui-empty">
          <div className="ui-empty__icon"><ImagePlus size={16} /></div>
          <div className="min-w-0">
            <div className="ui-label ui-label--on">No source loaded</div>
            <div className="ui-caption mt-1">Tap the ring on the canvas — or drop files onto it — to load images or video. These controls unlock once the first one lands.</div>
          </div>
        </div>
      )}

      {/* ---- LAYOUT --------------------------------------------------------- */}
      <div className="ui-stack--tight">
        <span className="ui-label">Layout</span>
        <div className="ui-grid-3">
          {MODES.map(m => (
            <button
              key={m.id}
              disabled={!hasImages}
              onClick={() => setLayoutMode(m.id)}
              data-active={m.id === 'complex' ? isComplexGroup : layoutMode === m.id}
              className="ui-tile"
              title={m.blurb}
            >
              {m.icon}
              <span className="ui-tile__label">{m.label}</span>
            </button>
          ))}
        </div>
        <p className="ui-caption">{detail}</p>
      </div>

      {/* ---- VARIANT (complex) or SHAPE (minimal / balanced) ---------------- */}
      {isComplexGroup ? (
        <div className="ui-stack--tight">
          <span className="ui-label">Break pattern</span>
          <div className="ui-grid-2">
            {VARIANTS.map(v => (
              <button
                key={v.id}
                disabled={!hasImages}
                onClick={() => setLayoutMode(v.id)}
                data-active={layoutMode === v.id}
                className="ui-tile ui-tile--sm"
                title={v.blurb}
              >
                {v.icon}
                <span className="ui-tile__label">{v.label}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="ui-stack--tight">
          <span className="ui-label">Fragment shape</span>
          <div className="ui-grid-5">
            {SHAPES.map(s => (
              <button
                key={s.id}
                disabled={!hasImages}
                onClick={() => setPrimitive(s.id)}
                data-active={primitive === s.id}
                className="ui-tile ui-tile--sm"
                title={s.blurb}
              >
                {s.icon}
                <span className="ui-tile__label">{s.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ---- DENSITY + CHAOS ------------------------------------------------ */}
      <div className="ui-panel p-3 ui-stack--tight">
        <div className="flex items-center gap-2">
          <Layers size={14} className="text-[color:var(--ink-3)] shrink-0" />
          <span className="ui-label mr-auto">Density</span>
          <div className="flex gap-1.5">
            {[1, 2, 3, 4].map(d => (
              <button
                key={d}
                disabled={!hasImages}
                onClick={() => setDensity(d)}
                data-active={density === d}
                className="ui-chip px-0"
                title={`${d}× — ${d === 1 ? 'one fragment per slot' : `${d} times the fragments, cropped tighter`}`}
              >
                {d}×
              </button>
            ))}
          </div>
        </div>
        <p className="ui-caption">
          {density === 1
            ? 'One fragment per slot.'
            : `${density}× the fragments, cropped ${Math.round((density - 1) * 50)}% tighter.`}
        </p>

        {usesChaos && (
          <div className="ui-field pt-2 border-t border-[color:var(--line-1)]">
            <div className="ui-field__head">
              <span className="ui-label flex items-center gap-1.5">
                <Activity size={12} /> Chaos
              </span>
              <span className="ui-field__value">{(entropy * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.01"
              value={entropy}
              disabled={!hasImages}
              onChange={e => setEntropy(parseFloat(e.target.value))}
              style={{ ['--fill' as string]: `${entropy * 100}%` } as React.CSSProperties}
              aria-label="Chaos"
            />
            <p className="ui-caption -mt-1">How far fragments drift off the grid.</p>
          </div>
        )}
      </div>

      {/* ---- ACTIONS: pinned to the thumb ---------------------------------- */}
      <div className="ui-actionbar">
        <div className="ui-stepper flex-1 min-w-0">
          <button
            className="ui-stepper__btn"
            disabled={!hasImages || count <= 1}
            aria-label="Fewer fragments"
            title="Fewer fragments (hold to run down)"
            {...stepProps(-1)}
          >
            <Minus size={18} />
          </button>
          <div className="ui-stepper__body">
            <span className="ui-stepper__value">{count}</span>
            <span className="ui-label" style={{ fontSize: 10 }}>Fragments</span>
          </div>
          <button
            className="ui-stepper__btn"
            disabled={!hasImages}
            aria-label="More fragments"
            title="More fragments (hold to run up)"
            {...stepProps(1)}
          >
            <Plus size={18} />
          </button>
        </div>

        <button
          disabled={!hasImages}
          onClick={onShuffle}
          className="ui-btn ui-btn--stack ui-btn--tall"
          style={{ width: 76 }}
          title="Deal the images into different fragments. The shapes stay put."
        >
          <Shuffle size={17} />
          <span>Shuffle<br />images</span>
        </button>

        <button
          disabled={!hasImages}
          onClick={onRemix}
          className={`ui-btn ui-btn--stack ui-btn--tall ${isLayoutLocked ? 'ui-btn--warn' : ''}`}
          style={{ width: 76 }}
          title={isLayoutLocked
            ? 'New shapes. Locked fragments keep their image and move to the nearest new cell.'
            : 'Generate a brand new set of shapes from a fresh seed.'}
        >
          {isLayoutLocked ? <Lock size={17} /> : <RefreshCw size={17} />}
          <span>Remix<br />shapes</span>
        </button>
      </div>
    </div>
  );
};
