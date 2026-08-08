import React, { useState, useEffect } from 'react';
import {
  Layout, Grid, Hexagon, Scissors, Palette, Moon, Contrast, Zap, Activity,
  Shuffle, RefreshCw, FileCode, History, Frame, Rows, Hash, Crosshair, RotateCw
} from 'lucide-react';
import { getHistory, HistoryItem } from '../lib/history';
import { LayoutMode } from '../types';
import {
  ARRANGEMENTS, ARRANGEMENT_BY_ID, FOCUS_MODES, FOCUS_BY_ID, TWIST_MODES, TWIST_BY_ID,
  type ArrangementId, type FocusId, type TwistId,
} from '../lib/composition';
import { ASPECT_ROSTER } from '../lib/diceRoll';

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
  twist: TwistId;
  setTwist: (t: TwistId) => void;
  bgColor: string;
  setBgColor: (c: string) => void;
  avgColor: { r: number, g: number, b: number } | null;
  onRemix: () => void;
  onShuffle: () => void;
  onExportVector: () => void;
  onRestoreHistory: (item: HistoryItem) => void;
  isLayoutLocked: boolean;
}

const MODES: { id: LayoutMode; label: string; icon: React.ReactNode; blurb: string }[] = [
  { id: 'minimal',  label: 'Minimal',  icon: <Layout size={16} />,   blurb: 'A few large fragments.' },
  { id: 'balanced', label: 'Balanced', icon: <Grid size={16} />,     blurb: 'An even grid.' },
  { id: 'complex',  label: 'Complex',  icon: <Hexagon size={16} />,  blurb: 'Irregular voronoi shards.' },
  { id: 'stencil',  label: 'Stencil',  icon: <Scissors size={16} />, blurb: 'Fragments cut from the light and dark of each image. Slower to compute.' },
];

/**
 * The frame shapes, taken from the ROSTER rather than retyped.
 *
 * These four used to be written out by hand as 0.666 / 1 / 1.77 / 0.5625 while
 * the dice rolled from `ASPECTS` = … 0.6667 … 1.7778 …, so two of the four
 * chips sat a rounding error off the roster. Invisible on screen (2px of canvas
 * height at 1200 wide) and invisible to the chip's own `< 0.01` active test —
 * but the share code carries the frame as a roster INDEX, so a code copied from
 * a hand-set 2:3 came back as the roster's 2:3 and the collage moved. One list,
 * read by both, is the only version of this that stays true.
 */
const RATIOS = [
  { v: ASPECT_ROSTER[1], l: '2:3',  n: 'Portrait' },
  { v: ASPECT_ROSTER[0], l: '1:1',  n: 'Square' },
  { v: ASPECT_ROSTER[5], l: '16:9', n: 'Wide' },
  { v: ASPECT_ROSTER[6], l: '9:16', n: 'Story' },
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
  entropy, setEntropy, arrangement, setArrangement, focus, setFocus, twist, setTwist, bgColor, setBgColor, avgColor,
  onRemix, onShuffle, onExportVector, onRestoreHistory, isLayoutLocked,
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

  /**
   * ONE SPELLING FOR A COLOUR — `#rrggbb`, everywhere.
   *
   * These three derived backgrounds used to be written `rgb(r,g,b)` while the
   * two fixed swatches were hex. Nothing rendered differently (canvas reads both
   * identically), but the background is now serialised into the share code and
   * read back out of it, and a round trip that returns the same COLOUR in a
   * different SPELLING breaks every `bgColor === …` comparison on this panel —
   * the swatch you are looking at stops highlighting itself. Canonicalising here
   * is cheaper and more honest than teaching four comparisons to parse CSS.
   */
  const hexOf = (r: number, g: number, b: number) =>
    `#${[r, g, b].map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0')).join('')}`;

  const avgCss = avgColor ? hexOf(avgColor.r, avgColor.g, avgColor.b) : '#2b3134';
  const greyCss = avgColor
    ? (() => { const l = (avgColor.r + avgColor.g + avgColor.b) / 3; return hexOf(l, l, l); })()
    : '#2b3134';
  const invCss = avgColor ? hexOf(255 - avgColor.r, 255 - avgColor.g, 255 - avgColor.b) : '#2b3134';

  const setBgAdaptive = (type: 'avg' | 'grey' | 'contrast') => {
    if (!avgColor) return;
    if (type === 'avg') setBgColor(avgCss);
    if (type === 'grey') setBgColor(greyCss);
    if (type === 'contrast') setBgColor(invCss);
  };

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
        </div>

        {/* ---- TWIST ------------------------------------------------------
            HOW FAR THE PICTURE LEANS in its fragment. The fragments TILE the
            canvas, so nothing here rotates a cell — the hole stays exactly
            where it was and the picture sits in it at an angle, which is what
            a scrapbook actually does. The cost is real and worth knowing: a
            lean has to be covered, so the crop pulls in by |cos|+|sin|. ---- */}
        <div className="ui-stack--tight pt-2">
          <div className="ui-field__head">
            <span className="ui-label flex items-center gap-1.5">
              <RotateCw size={12} className={twist !== 'none' ? 'text-[color:var(--warn)]' : ''} /> Twist
            </span>
            <span className="ui-field__value">{TWIST_BY_ID[twist]?.label ?? twist}</span>
          </div>
          <div className="ui-famrow" role="group" aria-label="Twist">
            {TWIST_MODES.map(t => (
              <button
                key={t.id}
                disabled={!ready}
                onClick={() => setTwist(t.id)}
                data-active={twist === t.id}
                className="ui-gchip"
                title={t.blurb}
              >
                {t.label}
              </button>
            ))}
          </div>
          <p className="ui-caption -mt-1">{TWIST_BY_ID[twist]?.blurb}</p>
          {/* CREDIT. All three pickers above exist because somebody asked for
              them, in one wish, and the person who asked gets their name on the
              thing they caused — see credits.json. This wisher stayed anonymous. */}
          <p className="ui-caption ui-label--dim mt-2 pt-2 border-t border-[color:var(--line-1)]">
            Arrangement, Crop focus and Twist were wished for by an anonymous Collage user.
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

        {/* CREDIT. The frame now fills the space it is given, the controls stop
            at half the screen, and there is a full-bleed view — all because
            somebody said the artwork was too small to judge a layout by. This
            wisher stayed anonymous too. See credits.json. */}
        <p className="ui-caption ui-label--dim mt-1">
          Full bleed (the <span className="font-bold">⤢</span> on the stage, or <span className="font-bold">F</span>) and
          giving the artwork the room were wished for by an anonymous Collage user.
        </p>

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

      {/* NO VIDEO SETTINGS BLOCK. It held one switch, "Choose frames on
          import", which routed a dropped clip into a sheet that asked how many
          frames to pull. Default-off was not enough — an opt-in ask is still an
          ask, and the owner filed it a third time. A video loads and loops;
          there is nothing left to configure about that. */}

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
