import React, { useState, useEffect } from 'react';
import {
  Layout, Grid, Hexagon, Scissors, Palette, Moon, Contrast, Zap, Activity,
  Shuffle, RefreshCw, FileCode, History, Frame, Rows, Hash, Film, Crosshair
} from 'lucide-react';
import { getHistory, HistoryItem } from '../lib/history';
import { LayoutMode } from '../types';
import {
  ARRANGEMENTS, ARRANGEMENT_BY_ID, FOCUS_MODES, FOCUS_BY_ID,
  type ArrangementId, type FocusId,
} from '../lib/composition';

interface AdvancedControlsProps {
  layoutMode: LayoutMode;
  setLayoutMode: (m: LayoutMode) => void;
  count: number;
  setCount: (n: number) => void;
  aspect: number;
  setAspect: (a: number) => void;
  gutter: number;
  setGutter: (g: number) => void;
  entropy: number;
  setEntropy: (e: number) => void;
  arrangement: ArrangementId;
  setArrangement: (a: ArrangementId) => void;
  focus: FocusId;
  setFocus: (f: FocusId) => void;
  bgColor: string;
  setBgColor: (c: string) => void;
  avgColor: { r: number, g: number, b: number } | null;
  onRemix: () => void;
  onShuffle: () => void;
  onExportVector: () => void;
  onRestoreHistory: (item: HistoryItem) => void;
  isLayoutLocked: boolean;
  /** Whether a dropped clip stops at the frame picker. Off by default. */
  framePicker: boolean;
  setFramePicker: (b: boolean) => void;
}

const MODES: { id: LayoutMode; label: string; icon: React.ReactNode; blurb: string }[] = [
  { id: 'minimal',  label: 'Minimal',  icon: <Layout size={16} />,   blurb: 'A few large fragments.' },
  { id: 'balanced', label: 'Balanced', icon: <Grid size={16} />,     blurb: 'An even grid.' },
  { id: 'complex',  label: 'Complex',  icon: <Hexagon size={16} />,  blurb: 'Irregular voronoi shards.' },
  { id: 'stencil',  label: 'Stencil',  icon: <Scissors size={16} />, blurb: 'Fragments cut from the light and dark of each image. Slower to compute.' },
];

const RATIOS = [
  { v: 0.666,  l: '2:3',  n: 'Portrait' },
  { v: 1,      l: '1:1',  n: 'Square' },
  { v: 1.77,   l: '16:9', n: 'Wide' },
  { v: 0.5625, l: '9:16', n: 'Story' },
];

const ratioBox = (a: number): React.CSSProperties =>
  a >= 1 ? { width: 24, height: Math.max(8, Math.round(24 / a)) }
         : { width: Math.max(8, Math.round(24 * a)), height: 24 };

const clockOf = (ts: number) => {
  try { return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
  catch { return ''; }
};

export const AdvancedControls: React.FC<AdvancedControlsProps> = ({
  layoutMode, setLayoutMode, count, setCount, aspect, setAspect, gutter, setGutter,
  entropy, setEntropy, arrangement, setArrangement, focus, setFocus, bgColor, setBgColor, avgColor,
  onRemix, onShuffle, onExportVector, onRestoreHistory, isLayoutLocked,
  framePicker, setFramePicker
}) => {

  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Poll for session snapshots, but only re-render when the set actually
  // changed — the old 1 Hz setState re-rendered this whole panel forever.
  useEffect(() => {
    const sig = (a: HistoryItem[]) => a.map(i => i.id).join('|');
    const sync = () => setHistory(prev => {
      const next = getHistory();
      return sig(prev) === sig(next) ? prev : next;
    });
    sync();
    const t = setInterval(sync, 2000);
    return () => clearInterval(t);
  }, []);

  // No `hasImages` prop is available here; count only leaves 0 once a source
  // has been ingested, so it is the honest proxy.
  const ready = count > 0;

  const setBgAdaptive = (type: 'avg' | 'grey' | 'contrast') => {
    if (!avgColor) return;
    if (type === 'avg') setBgColor(`rgb(${avgColor.r},${avgColor.g},${avgColor.b})`);
    if (type === 'grey') {
      const l = Math.round((avgColor.r + avgColor.g + avgColor.b) / 3);
      setBgColor(`rgb(${l},${l},${l})`);
    }
    if (type === 'contrast') {
      setBgColor(`rgb(${255 - avgColor.r},${255 - avgColor.g},${255 - avgColor.b})`);
    }
  };

  const avgCss = avgColor ? `rgb(${avgColor.r},${avgColor.g},${avgColor.b})` : '#2b3134';
  const greyCss = avgColor
    ? (() => { const l = Math.round((avgColor.r + avgColor.g + avgColor.b) / 3); return `rgb(${l},${l},${l})`; })()
    : '#2b3134';
  const invCss = avgColor ? `rgb(${255 - avgColor.r},${255 - avgColor.g},${255 - avgColor.b})` : '#2b3134';

  const countMax = Math.max(60, count + 12);

  return (
    <div className="ui-dock">

      {/* ================= GEOMETRY ========================================= */}
      <div className="ui-stack--tight">
        <div className="ui-title"><Frame size={12} /> Geometry</div>

        <div className="ui-grid-4">
          {MODES.map(m => (
            <button
              key={m.id}
              disabled={!ready}
              onClick={() => setLayoutMode(m.id)}
              data-active={m.id === 'complex'
                ? (layoutMode === 'complex' || layoutMode === 'field')
                : layoutMode === m.id}
              className="ui-tile ui-tile--sm"
              title={m.blurb}
            >
              {m.icon}
              <span className="ui-tile__label">{m.label}</span>
            </button>
          ))}
        </div>
        <p className="ui-caption">
          {MODES.find(m => m.id === layoutMode)?.blurb
            ?? 'Fragments drift along a flowing vector field.'}
        </p>
      </div>

      {/* ---- continuous parameters ---------------------------------------- */}
      <div className="ui-panel p-3 ui-stack--tight">

        <div className="ui-field">
          <div className="ui-field__head">
            <span className="ui-label flex items-center gap-1.5"><Hash size={12} /> Fragments</span>
            <span className="ui-field__value">{count}</span>
          </div>
          <input
            type="range" min="1" max={countMax} step="1"
            value={Math.max(1, count)}
            disabled={!ready}
            onChange={e => setCount(parseInt(e.target.value, 10))}
            style={{ ['--fill' as string]: `${((Math.max(1, count) - 1) / (countMax - 1)) * 100}%` } as React.CSSProperties}
            aria-label="Fragment count"
          />
          <p className="ui-caption -mt-1">How many pieces the canvas is cut into.</p>
        </div>

        <div className="ui-field pt-2 border-t border-[color:var(--line-1)]">
          <div className="ui-field__head">
            <span className="ui-label flex items-center gap-1.5"><Rows size={12} /> Padding</span>
            <span className="ui-field__value">{(gutter * 100).toFixed(1)}%</span>
          </div>
          <input
            type="range" min="0" max="0.05" step="0.001"
            value={gutter}
            disabled={!ready}
            onChange={e => setGutter(parseFloat(e.target.value))}
            style={{ ['--fill' as string]: `${(gutter / 0.05) * 100}%` } as React.CSSProperties}
            aria-label="Padding between fragments"
          />
          <p className="ui-caption -mt-1">Gap between fragments — background shows through here.</p>
        </div>

        <div className="ui-field pt-2 border-t border-[color:var(--line-1)]">
          <div className="ui-field__head">
            <span className="ui-label flex items-center gap-1.5"><Activity size={12} /> Chaos</span>
            <span className="ui-field__value">{(entropy * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range" min="0" max="1" step="0.01"
            value={entropy}
            disabled={!ready}
            onChange={e => setEntropy(parseFloat(e.target.value))}
            style={{ ['--fill' as string]: `${entropy * 100}%` } as React.CSSProperties}
            aria-label="Chaos"
          />
          <p className="ui-caption -mt-1">
            How far fragments drift off the grid. No effect in Minimal.
          </p>
        </div>

        {/* ---- ARRANGEMENT ------------------------------------------------
            WHICH PHOTO GOES IN WHICH FRAGMENT. This replaced a "Colour
            resonance" slider that was a binary wearing a percentage — only the
            10% threshold did anything, and above it there was exactly one
            ordering. Eleven NAMED pairings say what they do, and the one you
            picked is a thing you can tell someone. --------------------------- */}
        <div className="ui-stack--tight pt-2 border-t border-[color:var(--line-1)]">
          <div className="ui-field__head">
            <span className="ui-label flex items-center gap-1.5">
              <Zap size={12} className={arrangement !== 'natural' ? 'text-[color:var(--warn)]' : ''} /> Arrangement
            </span>
            <span className="ui-field__value">{ARRANGEMENT_BY_ID[arrangement]?.label ?? arrangement}</span>
          </div>
          <div className="ui-famrow" role="group" aria-label="Arrangement">
            {ARRANGEMENTS.map(a => (
              <button
                key={a.id}
                disabled={!ready}
                onClick={() => setArrangement(a.id)}
                data-active={arrangement === a.id}
                className="ui-gchip"
                title={a.blurb}
              >
                {a.label}
              </button>
            ))}
          </div>
          <p className="ui-caption -mt-1">{ARRANGEMENT_BY_ID[arrangement]?.blurb}</p>
        </div>

        {/* ---- FOCUS ------------------------------------------------------
            WHAT EACH FRAGMENT CENTRES ON. A fragment is a `cover` crop, so most
            of every photo is thrown away — which part survives is a composition
            decision, and it is per-FRAGMENT, so the same photo in three places
            can show three different parts of itself. --------------------- */}
        <div className="ui-stack--tight pt-2">
          <div className="ui-field__head">
            <span className="ui-label flex items-center gap-1.5">
              <Crosshair size={12} className={focus !== 'auto' ? 'text-[color:var(--warn)]' : ''} /> Crop focus
            </span>
            <span className="ui-field__value">{FOCUS_BY_ID[focus]?.label ?? focus}</span>
          </div>
          <div className="ui-famrow" role="group" aria-label="Crop focus">
            {FOCUS_MODES.map(f => (
              <button
                key={f.id}
                disabled={!ready}
                onClick={() => setFocus(f.id)}
                data-active={focus === f.id}
                className="ui-gchip"
                title={f.blurb}
              >
                {f.label}
              </button>
            ))}
          </div>
          <p className="ui-caption -mt-1">{FOCUS_BY_ID[focus]?.blurb}</p>
          {/* CREDIT. Both pickers above exist because somebody asked for them,
              and the person who asked gets their name on the thing they caused
              — see credits.json. This wisher chose to stay anonymous. */}
          <p className="ui-caption ui-label--dim mt-2 pt-2 border-t border-[color:var(--line-1)]">
            Arrangement and Crop focus were wished for by an anonymous Collage user.
          </p>
        </div>
      </div>

      {/* ================= CANVAS =========================================== */}
      <div className="ui-stack--tight">
        <div className="ui-title"><Frame size={12} /> Canvas</div>

        <div className="ui-grid-4">
          {RATIOS.map(r => (
            <button
              key={r.l}
              onClick={() => setAspect(r.v)}
              data-active={Math.abs(aspect - r.v) < 0.01}
              className="ui-ratio"
              title={`${r.n} — ${r.l}`}
            >
              <span className="ui-ratio__box" style={ratioBox(r.v)} />
              <span className="ui-ratio__label">{r.l}</span>
            </button>
          ))}
        </div>

        <span className="ui-label mt-1">Background</span>
        <div className="ui-grid-5">
          <button
            onClick={() => setBgColor('#050505')}
            data-active={bgColor === '#050505'}
            className="ui-swatch"
            title="Near-black background"
          >
            <span className="ui-swatch__dot" style={{ background: '#050505' }} />
            <span className="ui-swatch__label">Black</span>
          </button>
          <button
            onClick={() => setBgColor('#f5f5f5')}
            data-active={bgColor === '#f5f5f5'}
            className="ui-swatch"
            title="Paper-white background"
          >
            <span className="ui-swatch__dot" style={{ background: '#f5f5f5' }} />
            <span className="ui-swatch__label">White</span>
          </button>
          <button
            disabled={!avgColor}
            onClick={() => setBgAdaptive('avg')}
            data-active={!!avgColor && bgColor === avgCss}
            className="ui-swatch"
            title="Average colour of everything you loaded"
          >
            <span className="ui-swatch__dot" style={{ background: avgCss }}>
              <Palette size={11} className="opacity-70" />
            </span>
            <span className="ui-swatch__label">Average</span>
          </button>
          <button
            disabled={!avgColor}
            onClick={() => setBgAdaptive('grey')}
            data-active={!!avgColor && bgColor === greyCss}
            className="ui-swatch"
            title="Average brightness, no hue"
          >
            <span className="ui-swatch__dot" style={{ background: greyCss }}>
              <Moon size={11} className="opacity-70" />
            </span>
            <span className="ui-swatch__label">Grey</span>
          </button>
          <button
            disabled={!avgColor}
            onClick={() => setBgAdaptive('contrast')}
            data-active={!!avgColor && bgColor === invCss}
            className="ui-swatch"
            title="Inverse of the average colour — maximum separation"
          >
            <span className="ui-swatch__dot" style={{ background: invCss }}>
              <Contrast size={11} className="opacity-70" />
            </span>
            <span className="ui-swatch__label">Invert</span>
          </button>
        </div>
        {!avgColor && (
          <p className="ui-caption">Adaptive backgrounds unlock once images are analysed.</p>
        )}
      </div>

      {/* ================= SESSION ========================================== */}
      <div className="ui-stack--tight">
        <div className="ui-title"><History size={12} /> Session snapshots</div>
        {history.length === 0 ? (
          <div className="ui-empty">
            <div className="ui-empty__icon"><History size={16} /></div>
            <div className="min-w-0">
              <div className="ui-label ui-label--on">Nothing stored yet</div>
              <div className="ui-caption mt-1">
                Clearing the canvas files the current set here, so you can step back into it.
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-1.5">
            {history.map(item => (
              <button
                key={item.id}
                onClick={() => onRestoreHistory(item)}
                className="ui-row"
                title={`Restore ${item.images.length} images and their layout`}
              >
                <span className="ui-row__thumb">
                  {item.thumbnail
                    ? <img src={item.thumbnail} alt="" />
                    : <Frame size={14} className="text-[color:var(--ink-4)]" />}
                </span>
                <span className="flex-1 min-w-0">
                  <span className="block ui-label ui-label--on truncate">
                    {item.images.length} images · {item.state.layout.mode}
                  </span>
                  <span className="block ui-caption mt-0.5 ui-num">
                    {clockOf(item.timestamp)} · seed {String(item.state.layout.seed).slice(-5)}
                  </span>
                </span>
                <span className="ui-label" style={{ color: 'var(--signal)' }}>Load</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* ---- VIDEO ---------------------------------------------------------- */}
      <div className="ui-stack--tight">
        <div className="ui-title"><Film size={12} /> Video</div>
        <div className="ui-panel p-3">
          <button
            onClick={() => setFramePicker(!framePicker)}
            role="switch"
            aria-checked={framePicker}
            /* min-h-11: the row is a switch, so the whole row is the hit box —
               its natural height was 29px, which is a thumb-miss on a phone. */
            className="w-full min-h-11 flex items-center gap-3 text-left"
            title="Off: a dropped clip goes straight into the collage and plays. On: you choose which extracted frames to keep first."
          >
            <span
              className="shrink-0 w-9 h-5 rounded-full transition-colors relative"
              style={{ background: framePicker ? 'var(--signal)' : 'var(--line-1)' }}
            >
              <span
                className="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all"
                style={{ left: framePicker ? '1.125rem' : '0.125rem' }}
              />
            </span>
            <span className="flex-1 min-w-0">
              <span className="block ui-label ui-label--on">Choose frames on import</span>
              <span className="block ui-caption mt-0.5">
                {framePicker
                  ? 'A dropped clip stops at the frame picker first.'
                  : 'A dropped clip goes straight in and plays.'}
              </span>
            </span>
          </button>
        </div>
      </div>

      {/* ---- ACTIONS -------------------------------------------------------- */}
      <div className="ui-actionbar">
        <button
          disabled={!ready}
          onClick={onShuffle}
          className="ui-btn ui-btn--stack ui-btn--tall flex-1"
          title="Deal the images into different fragments. The shapes stay put."
        >
          <Shuffle size={17} />
          <span>Shuffle<br />images</span>
        </button>
        <button
          disabled={!ready}
          onClick={onRemix}
          className={`ui-btn ui-btn--stack ui-btn--tall flex-1 ${isLayoutLocked ? 'ui-btn--warn' : ''}`}
          title={isLayoutLocked
            ? 'New shapes. Locked fragments keep their image and move to the nearest new cell.'
            : 'Generate a brand new set of shapes from a fresh seed.'}
        >
          <RefreshCw size={17} />
          <span>Remix<br />shapes</span>
        </button>
        <button
          disabled={!ready}
          onClick={onExportVector}
          className="ui-btn ui-btn--stack ui-btn--tall flex-1"
          title="Export the layout as SVG — vector outlines with the images embedded."
        >
          <FileCode size={17} />
          <span>Vector<br />SVG</span>
        </button>
      </div>
    </div>
  );
};
