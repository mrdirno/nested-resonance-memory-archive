import React, { useCallback, useEffect, useRef } from 'react';
import {
  Layout, Grid, Plus, Minus, RefreshCw, Shuffle, Square,
  Triangle, Circle, Octagon, Shapes, Layers, Activity, Lock, ImagePlus, Dices, Copy, Type, X
} from 'lucide-react';
import { LayoutMode, PrimitiveType } from '../types';
import type { TitlePlace, TitleSize } from '../lib/title';
import { LOOKS, type LookId } from '../lib/grade';
import { GENERATORS, GENERATOR_BY_ID, FAMILIES, FAMILY_LABEL } from '../engine/geom/generators';

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
  /** Roll a whole composition — layout, count, chaos, aspect, gutter, colour. */
  onDice?: () => void;
  /** Name of the recipe the last roll came from, for the readout. */
  lastRecipe?: string;
  /** The composition on screen, as a code — see lib/rollCode.ts. */
  compositionCode?: string;
  /** Apply a pasted code. False when it is not one. */
  onApplyCode?: (code: string) => boolean;
  /** A code that arrived in the URL damaged — shown so it can be repaired. */
  rejectedCode?: string;
  hasImages: boolean;
  isLayoutLocked: boolean;

  /** THE TITLE — the caption drawn over the finished collage. */
  titleText?: string;
  titlePlace?: TitlePlace;
  titleSize?: TitleSize;
  onTitleText?: (t: string) => void;
  onTitlePlace?: (p: TitlePlace) => void;
  onTitleSize?: (s: TitleSize) => void;

  /** THE LOOK — the colour grade over every fragment. See lib/grade.ts. */
  look?: LookId;
  onLook?: (l: LookId) => void;
}

/**
 * WHERE the caption sits. Four, not nine: a nine-box placement grid is a
 * settings screen, and the four that get used are the two bottom corners and
 * their two mirrors. Labels are the field's own shorthand, not prose.
 */
const TITLE_PLACES: { id: TitlePlace; label: string; title: string }[] = [
  { id: 'bl', label: 'BOT L', title: 'Bottom left — the default, and where a caption reads first.' },
  { id: 'bc', label: 'BOT C', title: 'Bottom centre.' },
  { id: 'tl', label: 'TOP L', title: 'Top left.' },
  { id: 'tc', label: 'TOP C', title: 'Top centre.' },
];

const TITLE_SIZES: { id: TitleSize; label: string; title: string }[] = [
  { id: 'sm', label: 'S', title: 'Small — a credit line.' },
  { id: 'md', label: 'M', title: 'Medium.' },
  { id: 'lg', label: 'L', title: 'Large — a poster title.' },
];

/**
 * The two original grid modes. They are the only ones that read `primitive`,
 * and they are kept because "an even grid of squares" is a legitimate thing to
 * want — it is just no longer the whole tool.
 */
const CLASSIC: { id: LayoutMode; label: string; icon: React.ReactNode; blurb: string }[] = [
  { id: 'minimal',  label: 'Minimal',  icon: <Layout size={16} />, blurb: 'Few large fragments, lots of open space.' },
  { id: 'balanced', label: 'Balanced', icon: <Grid size={16} />,   blurb: 'An even grid — every fragment weighs the same.' },
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
  density, setDensity, entropy, setEntropy, onRemix, onShuffle, onDice,
  lastRecipe, compositionCode, onApplyCode, rejectedCode, hasImages, isLayoutLocked,
  titleText = '', titlePlace = 'bl', titleSize = 'md', onTitleText, onTitlePlace, onTitleSize,
  look = 'none', onLook
}) => {

  // ---- THE COMPOSITION CODE --------------------------------------------------
  // Two jobs on one strip because they are two halves of one act: the code of
  // what is on screen (tap it to copy) and a box to put somebody else's in.
  const [copied, setCopied] = React.useState(false);
  const [pasted, setPasted] = React.useState('');
  const [rejected, setRejected] = React.useState(false);
  const copiedTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => { if (copiedTimer.current) clearTimeout(copiedTimer.current); }, []);

  // A code that came in damaged lands here rather than vanishing, so a dropped
  // character is visible and one keystroke from fixed.
  useEffect(() => { if (rejectedCode) { setPasted(rejectedCode); setRejected(true); } }, [rejectedCode]);

  const copyCode = async () => {
    if (!compositionCode) return;
    try {
      await navigator.clipboard.writeText(compositionCode);
    } catch {
      // Clipboard permission is not granted everywhere, and an iOS Safari tab
      // that has lost focus refuses outright. Selecting the text is a worse
      // affordance than a copy, and a far better one than nothing happening.
      const sel = window.getSelection?.();
      const node = document.getElementById('composition-code-value');
      if (sel && node) { const r = document.createRange(); r.selectNodeContents(node); sel.removeAllRanges(); sel.addRange(r); }
    }
    setCopied(true);
    if (copiedTimer.current) clearTimeout(copiedTimer.current);
    copiedTimer.current = setTimeout(() => setCopied(false), 1600);
  };

  const openCode = () => {
    if (!onApplyCode) return;
    const ok = onApplyCode(pasted);
    setRejected(!ok);
    if (ok) setPasted('');
  };

  const generator = GENERATOR_BY_ID[layoutMode];
  const isClassic = !generator;
  // Every generator responds to chaos; of the classics only `balanced` does
  // (minimal has nothing to jitter) and the legacy complex/field pair.
  const usesChaos = !!generator || layoutMode === 'balanced'
    || layoutMode === 'complex' || layoutMode === 'field';
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

  const classic = CLASSIC.find(m => m.id === layoutMode);
  const activeShape = SHAPES.find(s => s.id === primitive) ?? SHAPES[0];
  const activeLabel = generator?.name
    ?? classic?.label
    // The two retired ids still load from saved projects, so they must still name themselves.
    ?? (layoutMode === 'complex' ? 'Shatter (classic)' : layoutMode === 'field' ? 'Flow (classic)' : 'Layout');
  const detail = generator?.blurb ?? classic?.blurb ?? 'A layout saved from an earlier version.';

  return (
    <div className="ui-dock">

      {/* ---- persistent caption: the whole panel state in one mono line ---- */}
      {hasImages ? (
        <div className="ui-readout" aria-live="polite">
          <span><b>{activeLabel.toUpperCase()}</b></span>
          {isClassic && <><i>/</i><span>{activeShape.label.toUpperCase()}</span></>}
          {lastRecipe && <><i>/</i><span>“{lastRecipe.toUpperCase()}”</span></>}
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

      {/* ---- DICE: the fastest route to something you did not expect -------- */}
      {onDice && (
        <button
          disabled={!hasImages}
          onClick={onDice}
          className="ui-dice"
          title="Roll a whole composition — layout, fragments, chaos, shape of frame, gutter and colour, all at once."
        >
          <Dices size={20} />
          <span className="ui-dice__text">
            <b>Roll the dice</b>
            <i>{lastRecipe ? `Last roll: “${lastRecipe}”` : 'A whole new composition, all at once'}</i>
          </span>
        </button>
      )}

      {/* ---- THE TITLE: say what it is ---------------------------------------
          The one thing in this panel that is CONTENT rather than a parameter,
          so it is the one thing you type instead of tick. It is drawn over the
          finished collage by every path that produces pixels — the preview you
          are looking at, the exported picture, the recorded video and the SVG —
          and it is NOT in the composition code, because a code is a recipe for
          somebody else's photographs and your caption is not. ------------- */}
      {/* ---- THE LOOK: the colour grade, on every fragment ------------------
          One row, one job. It reaches the preview, the live video, the exported
          picture and the SVG — and unlike the caption it IS in the composition
          code, because a grade is part of the recipe. ------------------- */}
      {hasImages && onLook && (
        <div className="ui-looks">
          <div className="ui-looks__chips" role="group" aria-label="Look">
            {LOOKS.map(l => (
              <button
                key={l.id}
                type="button"
                className="ui-chip ui-chip--mini"
                data-active={(look ?? 'none') === l.id}
                onClick={() => onLook(l.id)}
                title={l.title}
                aria-pressed={(look ?? 'none') === l.id}
                data-testid={`look-${l.id}`}
              >{l.label}</button>
            ))}
          </div>
          <p className="ui-caption">
            {(look ?? 'none') === 'none'
              ? 'A colour grade on the photographs. The frame colour stays what you picked.'
              : 'On the picture, the video and the SVG. It travels in the code.'}
          </p>
        </div>
      )}

      {hasImages && onTitleText && (
        <div className="ui-titler">
          <div className="ui-titler__row">
            <span className="ui-titler__tag" aria-hidden="true"><Type size={13} /></span>
            <input
              type="text"
              value={titleText}
              onChange={e => onTitleText(e.target.value)}
              placeholder="Say what it is"
              maxLength={240}
              spellCheck={false}
              aria-label="Title drawn on the collage"
              data-testid="title-input"
            />
            {titleText.length > 0 && (
              <button
                type="button"
                className="ui-titler__clear"
                onClick={() => onTitleText('')}
                aria-label="Clear the title"
                data-testid="title-clear"
              >
                <X size={14} />
              </button>
            )}
          </div>

          {titleText.trim().length > 0 && (
            <>
              <div className="ui-titler__chips" role="group" aria-label="Title placement">
                {TITLE_PLACES.map(p => (
                  <button
                    key={p.id}
                    type="button"
                    className="ui-chip ui-chip--mini"
                    data-active={titlePlace === p.id}
                    onClick={() => onTitlePlace?.(p.id)}
                    title={p.title}
                    aria-pressed={titlePlace === p.id}
                    data-testid={`title-place-${p.id}`}
                  >{p.label}</button>
                ))}
              </div>
              <div className="ui-titler__chips" role="group" aria-label="Title size">
                {TITLE_SIZES.map(z => (
                  <button
                    key={z.id}
                    type="button"
                    className="ui-chip ui-chip--mini"
                    data-active={titleSize === z.id}
                    onClick={() => onTitleSize?.(z.id)}
                    title={z.title}
                    aria-pressed={titleSize === z.id}
                    data-testid={`title-size-${z.id}`}
                  >{z.label}</button>
                ))}
              </div>
            </>
          )}

          <p className="ui-caption">
            {titleText.trim().length > 0
              ? 'On the picture, the video and the SVG — same wrap in all of them. Not in the code.'
              : 'A caption on the collage. It goes into every export, not just the preview.'}
          </p>
        </div>
      )}

      {/* ---- THE CODE: keep the good roll, or open somebody else's ----------
          Every composition has one, and it is in the address bar too, so the
          link you already have IS the collage. The photographs are not in it —
          that is what makes it worth sending. ---------------------------- */}
      {compositionCode && (
        <div className="ui-code">
          <button
            type="button"
            onClick={copyCode}
            className="ui-code__copy"
            title="Copy this composition's code — paste it back here, or into a chat"
            aria-label={`Copy composition code ${compositionCode}`}
            data-copied={copied || undefined}
          >
            <span className="ui-code__tag">{copied ? 'Copied' : 'Code'}</span>
            <span className="ui-code__value" id="composition-code-value" data-testid="composition-code">
              {compositionCode}
            </span>
            <Copy size={14} className="shrink-0 opacity-70" />
          </button>

          {onApplyCode && (
            <div className="ui-code__open">
              <input
                type="text"
                value={pasted}
                onChange={e => { setPasted(e.target.value); setRejected(false); }}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); openCode(); } }}
                placeholder="Paste a code"
                spellCheck={false}
                autoCapitalize="characters"
                autoCorrect="off"
                aria-label="Paste a composition code"
                aria-invalid={rejected || undefined}
                data-testid="composition-code-input"
              />
              <button
                type="button"
                onClick={openCode}
                disabled={!pasted.trim()}
                className="ui-code__go"
                /* The Header already has a button that says "Open" — it opens a
                   saved project. Two controls with the same accessible name and
                   different meanings is a real ambiguity for anyone navigating
                   by name, and it silently broke a passing test the moment this
                   strip landed. The label stays visible and short; the
                   accessible name CONTAINS it, so label-in-name still holds. */
                aria-label="Open the pasted composition code"
                data-testid="composition-code-open"
              >
                Open
              </button>
            </div>
          )}

          <p className="ui-caption">
            {rejected
              ? 'That is not a composition code — check it came across whole.'
              : isLayoutLocked
              // Pinning a fragment does not just hold one picture in place: it
              // claims that image, which re-deals every slot after it. So a code
              // minted with pins does not describe what is on screen, and saying
              // nothing would be the same silent lie the pool count used to be.
              ? 'Pinned fragments are not in the code — this opens unpinned, which deals the pictures differently.'
              : 'Your photographs, their composition. Sources are never in the code.'}
          </p>
        </div>
      )}

      {/* ---- LAYOUT --------------------------------------------------------
          A ROSTER, NOT THREE BUTTONS. Grouped by family and scrolled
          horizontally: each row is short enough to scan, and the grouping is
          what makes ~25 options legible instead of a wall. The blurb under the
          rows always describes the SELECTED construction, honestly — several of
          these are famous figures and calling one by the wrong name is worse
          than not naming it. --------------------------------------------- */}
      <div className="ui-stack--tight">
        <span className="ui-label">Layout</span>

        <div className="ui-famrow">
          {CLASSIC.map(m => (
            <button
              key={m.id}
              disabled={!hasImages}
              onClick={() => setLayoutMode(m.id)}
              data-active={layoutMode === m.id}
              className="ui-gchip"
              title={m.blurb}
            >
              {m.icon}<span>{m.label}</span>
            </button>
          ))}
        </div>

        {FAMILIES.map(fam => {
          const items = GENERATORS.filter(g => g.family === fam);
          if (!items.length) return null;
          return (
            <div key={fam} className="ui-stack--tight">
              <span className="ui-label ui-label--dim">{FAMILY_LABEL[fam]}</span>
              <div className="ui-famrow">
                {items.map(g => (
                  <button
                    key={g.id}
                    disabled={!hasImages}
                    onClick={() => setLayoutMode(g.id as LayoutMode)}
                    data-active={layoutMode === g.id}
                    className="ui-gchip"
                    title={g.blurb}
                  >
                    <span>{g.name}</span>
                  </button>
                ))}
              </div>
            </div>
          );
        })}

        <p className="ui-caption">{detail}</p>
      </div>

      {/* ---- SHAPE — only the classic grid modes read it -------------------- */}
      {isClassic && (
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
