import React, { useCallback, useEffect, useRef } from 'react';
import {
  Layout, Grid, Plus, Minus, RefreshCw, Shuffle, Square,
  Triangle, Circle, Octagon, Shapes, Layers, Activity, Lock, Unlock, ImagePlus, Dices, Copy, Type, X,
  Undo2, Redo2, Palette, SlidersHorizontal
} from 'lucide-react';
import { LayoutMode, PrimitiveType } from '../types';
import type { TitlePlace, TitleSize } from '../lib/title';
import { LOOKS, DESK_AXES, deskForLook, type Desk, type LookId } from '../lib/grade';
import { MOVES, type MoveId } from '../lib/motion';
import { TURNS, type TurnId } from '../lib/turn';
import { PACES, type PaceId } from '../lib/pace';
import { SYNCS, beatsLabel, type SyncId, type BeatGrid } from '../lib/beat';
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
  /**
   * THE COLOUR DICE — roll the colour sorting and the crop, keep the layout.
   * The other half of the same wish that put it in the full-bleed rail: the
   * dock's dice has exactly the same all-or-nothing problem, so the fix lands
   * on both. See `lib/dealRoll.ts`.
   */
  onColourDice?: () => void;
  /**
   * THE FRAME HOLD — while on, the dice keeps the shape of frame and re-deals
   * everything else. A preference about future rolls (`holdFrame` in App.tsx),
   * so it rides neither the code nor a project; the same toggle sits in the
   * full-bleed rail — the fix lands on both.
   */
  holdFrame?: boolean;
  onHoldFrame?: (h: boolean) => void;
  /** Name of the recipe the last roll came from, for the readout. */
  lastRecipe?: string;
  /** UNDO — step back to the composition before the last roll/shuffle/remix/code. */
  onUndo?: () => void;
  onRedo?: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
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
  /** THE DESK — the four axes as they should read right now (see lib/grade.ts). */
  desk?: Desk;
  onDesk?: (d: Desk) => void;
  /** True when those axes are off the preset's own — the row says CUSTOM. */
  deskCustom?: boolean;

  /** THE MOVE — how the picture drifts inside its fragment. See lib/motion.ts. */
  move?: MoveId;
  onMove?: (m: MoveId) => void;
  /** THE TURN — how often the collage re-cuts its deal. See lib/turn.ts. */
  turn?: TurnId;
  onTurn?: (t: TurnId) => void;
  /** THE PACE — how fast the move and the turn run. See lib/pace.ts. */
  pace?: PaceId;
  onPace?: (p: PaceId) => void;
  /** THE BEAT — the user's intent, which rides the code. See lib/beat.ts. */
  sync?: SyncId;
  onSync?: (s: SyncId) => void;
  /** What the TRACK turned out to be. Measured, not chosen — so it rides nothing. */
  beatGrid?: BeatGrid | null;
  /** True while the decode/analysis is still running. */
  beatBusy?: boolean;
  /** How many beats the snapped hold came to, when there is one. */
  beatBeats?: number;
  /** Is there a track at all? */
  hasMusic?: boolean;
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
  density, setDensity, entropy, setEntropy, onRemix, onShuffle, onDice, onColourDice,
  holdFrame = false, onHoldFrame, lastRecipe, onUndo, onRedo, canUndo = false, canRedo = false,
  compositionCode, onApplyCode, rejectedCode, hasImages, isLayoutLocked,
  titleText = '', titlePlace = 'bl', titleSize = 'md', onTitleText, onTitlePlace, onTitleSize,
  look = 'none', onLook, desk, onDesk, deskCustom = false, move = 'still', onMove, turn = 'hold', onTurn,
  pace = 'even', onPace,
  sync = 'off', onSync, beatGrid = null, beatBusy = false, beatBeats = 0, hasMusic = false
}) => {

  // ---- THE COMPOSITION CODE --------------------------------------------------
  // Two jobs on one strip because they are two halves of one act: the code of
  // what is on screen (tap it to copy) and a box to put somebody else's in.
  /**
   * THE DESK, disclosed rather than docked. Four sliders is a settings screen
   * if it is always on; behind one chip it is the ADJUST tab of every editor
   * anybody has used. The open/closed state is UI-local on purpose — it is not
   * part of the composition, it does not travel in a code and reopening the app
   * should not put a panel back on the screen.
   */
  const [deskOpen, setDeskOpen] = React.useState(false);
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

      {/* ---- DICE: the fastest route to something you did not expect --------
          The title and subtitle tell the truth per state: claiming "shape of
          frame" while the hold below pins it would be the button appearing to
          have done something it did not. ---------------------------------- */}
      {onDice && (
        <button
          disabled={!hasImages}
          onClick={onDice}
          className="ui-dice"
          data-testid="dock-dice"
          title={holdFrame
            ? 'Roll a whole composition — layout, fragments, chaos, gutter and colour. The frame keeps its shape while the hold is on.'
            : 'Roll a whole composition — layout, fragments, chaos, shape of frame, gutter and colour, all at once.'}
        >
          <Dices size={20} />
          <span className="ui-dice__text">
            <b>Roll the dice</b>
            <i>{lastRecipe ? `Last roll: “${lastRecipe}”` : holdFrame ? 'A new composition in the frame you kept' : 'A whole new composition, all at once'}</i>
          </span>
        </button>
      )}

      {/* ---- THE COLOUR DICE: the roll that keeps the shape you found -------
          Directly under the dice above, because it is the answer to that
          button's one weakness — the roll you cannot press once you like the
          layout. Rolls the colour sorting and the crop, touches nothing else.
          Narrower and cooler than the dice on purpose: the whole-composition
          roll stays the widest, warmest thing in the dock. ----------------- */}
      {onColourDice && (
        <button
          disabled={!hasImages}
          onClick={onColourDice}
          className="ui-dice ui-dice--deal"
          data-testid="dock-colour-dice"
          title="Roll the colour sorting and the crop — the layout, count, chaos, frame and background all stay exactly as they are."
        >
          <Palette size={18} />
          <span className="ui-dice__text">
            <b>Colour + crop</b>
            <i>New sort and framing — keeps your layout</i>
          </span>
        </button>
      )}
      {/* CREDIT ON THE PAGE, next to the thing they asked for — the ledger in
          av/credits.json is permanent, but nobody reads a JSON file. */}
      {onColourDice && hasImages && (
        <p className="ui-credit">The colour dice was wished for by an anonymous Collage user.</p>
      )}

      {/* ---- THE FRAME HOLD: pin the shape, keep rolling --------------------
          Wished for: "Tide pool is sick I like them. Maybe good idea to lock
          aspect ratio too as a toggle." Under the two dice because it is a
          claim about them: chasing a recipe means rolling again and again,
          and every press used to re-deal the shape of frame too — six of
          seven, on a roster of seven. OFF by default: until you pin it, the
          dice keeps its all-at-once promise exactly as it was. ------------ */}
      {onHoldFrame && hasImages && (
        <div className="ui-looks">
          <div className="ui-looks__chips">
            <button
              type="button"
              className="ui-chip ui-chip--mini"
              data-active={holdFrame}
              onClick={() => onHoldFrame(!holdFrame)}
              title={holdFrame
                ? 'On — the dice keeps this shape of frame. Tap to let it roll again.'
                : 'Keep the current shape of frame (aspect ratio) when the dice rolls. Everything else still rolls.'}
              aria-pressed={holdFrame}
              data-testid="dock-hold-frame"
            >{holdFrame ? <Lock size={12} /> : <Unlock size={12} />}<span>Keep frame shape</span></button>
          </div>
          <p className="ui-caption">
            {holdFrame
              ? 'Held. The dice rolls everything but the shape of frame.'
              : 'Found a frame you like? Pin it, and the dice rolls everything else.'}
          </p>
          {/* CREDIT ON THE PAGE, next to the thing they asked for — the ledger
              in av/credits.json is permanent, but nobody reads a JSON file. */}
          <p className="ui-credit">The frame hold was wished for by an anonymous Collage user.</p>
        </div>
      )}

      {/* ---- UNDO: the roll you liked, brought back -------------------------
          Directly under the dice, because that is the button that destroys the
          composition and this is the way back from it. Same pair sits in the
          full-bleed rail — the wish came from there, and the dock's dice has
          exactly the same problem, so the fix lands on both. --------------- */}
      {onUndo && onRedo && (
        <div className="ui-undo" role="group" aria-label="Undo and redo">
          <button
            type="button"
            data-testid="undo-dock"
            className="ui-btn ui-undo__btn"
            disabled={!canUndo}
            onClick={onUndo}
            title="Undo — back to the composition before this one (⌘Z)"
            aria-label="Undo the last composition change"
          >
            <Undo2 size={16} />
            <span>Undo</span>
          </button>
          <button
            type="button"
            data-testid="redo-dock"
            className="ui-btn ui-undo__btn"
            disabled={!canRedo}
            onClick={onRedo}
            title="Redo — forward again (⇧⌘Z)"
            aria-label="Redo the composition change"
          >
            <Redo2 size={16} />
            <span>Redo</span>
          </button>
        </div>
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
                data-active={!deskCustom && (look ?? 'none') === l.id}
                onClick={() => onLook(l.id)}
                title={l.title}
                aria-pressed={!deskCustom && (look ?? 'none') === l.id}
                data-testid={`look-${l.id}`}
              >{l.label}</button>
            ))}
            {/* THE DESK — the ninth chip, and the only one that is a DOOR rather
                than a choice. It lights when the axes behind it are off the
                preset, which is the one fact the eight chips can no longer
                carry: a custom grade is not any of them. */}
            {onDesk && (
              <button
                type="button"
                className="ui-chip ui-chip--mini"
                data-active={deskCustom}
                aria-pressed={deskCustom}
                aria-expanded={deskOpen}
                onClick={() => setDeskOpen(o => !o)}
                title="Set the grade by hand — exposure, contrast, colour, warmth."
                data-testid="look-desk"
              >
                <SlidersHorizontal size={11} aria-hidden="true" />
                <span>{deskCustom ? 'CUSTOM' : 'ADJUST'}</span>
              </button>
            )}
          </div>
          {/* ---- THE DESK's four axes, disclosed ---------------------------
              Every one of the eight looks above is a POINT in this space (the
              sweep holds all eight to it, bit for bit), so opening this panel
              never moves a pixel — it just shows you where the preset already
              is. --------------------------------------------------------- */}
          {deskOpen && onDesk && desk && (
            <div className="ui-desk" data-testid="desk-panel">
              {DESK_AXES.map(ax => {
                const v = desk[ax.key];
                const pct = (v - ax.min) / (ax.max - ax.min) * 100;
                const read = ax.key === 'warmth'
                  ? (v === 0 ? 'NEUTRAL' : v > 0 ? `WARM ${Math.round(v * 100)}%` : `COOL ${Math.round(-v * 100)}%`)
                  : (v === ax.mid ? 'AS SHOT' : `${v > ax.mid ? '+' : ''}${Math.round((v - ax.mid) * 100)}%`);
                return (
                  <div className="ui-field" key={ax.key}>
                    <div className="ui-field__head">
                      <span className="ui-label">{ax.label}</span>
                      <span className="ui-field__value" data-testid={`desk-read-${ax.key}`}>{read}</span>
                    </div>
                    <input
                      type="range"
                      min={ax.min} max={ax.max} step={0.01}
                      value={v}
                      onChange={e => onDesk({ ...desk, [ax.key]: parseFloat(e.target.value) })}
                      style={{ ['--fill' as string]: `${pct}%` } as React.CSSProperties}
                      aria-label={ax.label}
                      title={ax.hint}
                      data-testid={`desk-${ax.key}`}
                    />
                  </div>
                );
              })}
              <button
                type="button"
                className="ui-chip ui-chip--mini ui-desk__reset"
                disabled={!deskCustom}
                onClick={() => onDesk(deskForLook(look))}
                data-testid="desk-reset"
                title="Back to the look you started from."
              >BACK TO {String(look ?? 'none').toUpperCase()}</button>
            </div>
          )}
          <p className="ui-caption">
            {deskCustom
              ? 'Your own grade. It travels in the code, exactly as the eight do.'
              : (look ?? 'none') === 'none'
                ? 'A colour grade on the photographs. The frame colour stays what you picked.'
                : 'On the picture, the video and the SVG. It travels in the code.'}
          </p>
        </div>
      )}

      {/* ---- THE MOVE: the picture drifts inside its fragment ----------------
          The row that gives this app a time axis. A collage of PHOTOGRAPHS
          exported as a video is a still image with a file size — the
          compositor's own tick says so ("a photos-only scene draws once and
          stops") — and this is what makes the file worth having. It reaches the
          live preview and the exported video; a single frame has no time to
          sample, so the picture, the SVG and this preview's first instant are
          exactly what they were. It travels in the code. ------------------ */}
      {hasImages && onMove && (
        <div className="ui-looks">
          <div className="ui-looks__chips" role="group" aria-label="Move">
            {MOVES.map(m => (
              <button
                key={m.id}
                type="button"
                className="ui-chip ui-chip--mini"
                data-active={(move ?? 'still') === m.id}
                onClick={() => onMove(m.id)}
                title={m.title}
                aria-pressed={(move ?? 'still') === m.id}
                data-testid={`move-${m.id}`}
              >{m.label}</button>
            ))}
          </div>
          <p className="ui-caption">
            {(move ?? 'still') === 'still'
              ? 'Make the collage move. Photographs drift and breathe in their fragments.'
              : 'In the preview and in the exported video. The picture and the SVG stay still.'}
          </p>
        </div>
      )}

      {/* ---- THE TURN: the collage re-cuts -----------------------------------
          THE MOVE gave this app a time axis; every fragment still held the same
          photograph for the whole take. This is the CUT — every few seconds the
          pictures land in different fragments and cross-dissolve on the way, so
          a twenty-second export stops being one deal breathing and becomes a
          sequence. Every state is a permutation of the deal, so two fragments
          can never show the same photograph. It reaches the live preview and
          the exported video; a single frame has no schedule to be at, so the
          picture, the SVG and this preview's first instant are exactly what
          they were. It travels in the code. ------------------------------- */}
      {hasImages && onTurn && (
        <div className="ui-looks">
          <div className="ui-looks__chips" role="group" aria-label="Turn">
            {TURNS.map(t => (
              <button
                key={t.id}
                type="button"
                className="ui-chip ui-chip--mini"
                data-active={(turn ?? 'hold') === t.id}
                onClick={() => onTurn(t.id)}
                title={t.title}
                aria-pressed={(turn ?? 'hold') === t.id}
                data-testid={`turn-${t.id}`}
              >{t.label}</button>
            ))}
          </div>
          <p className="ui-caption">
            {(turn ?? 'hold') === 'hold'
              ? 'Re-cut the collage. Photographs change fragments as the take runs.'
              : 'In the preview and in the exported video. Every cut is a re-deal, never a repeat.'}
          </p>
        </div>
      )}

      {/* ---- THE PACE: how fast the clock runs -------------------------------
          The RATE half of the two rows above. Until this existed the only way
          to cut faster was to pick a different TURN — which also changes the
          permutation — and there was no way at all to drift faster: the move's
          cycle was a constant. One dial over both, because a collage has one
          clock. It scales the TIME the schedule is read against rather than
          each period, so the dissolve stays the same FRACTION of the hold at
          every rate (lib/pace.ts). It travels in the code. -------------- */}
      {hasImages && onPace && (
        <div className="ui-looks">
          <div className="ui-looks__chips" role="group" aria-label="Pace">
            {PACES.map(p => (
              <button
                key={p.id}
                type="button"
                className="ui-chip ui-chip--mini"
                data-active={(pace ?? 'even') === p.id}
                onClick={() => onPace(p.id)}
                title={p.title}
                aria-pressed={(pace ?? 'even') === p.id}
                data-testid={`pace-${p.id}`}
              >{p.label}</button>
            ))}
          </div>
          <p className="ui-caption">
            {/* SAYS WHAT IT NEEDS RATHER THAN DISABLING ITSELF. A tempo over a
                collage that neither drifts nor cuts has nothing to speed up,
                and the fix for that is a sentence, not a dead row — the chip
                still sets the rate for the move you are about to pick, and it
                still rides the dice and the code. (Scar C126: a control that
                asks which sources exist and disables itself.) */}
            {(move ?? 'still') === 'still' && (turn ?? 'hold') === 'hold'
              ? 'How fast it all runs. Pick a MOVE or a TURN above and this sets the tempo.'
              : (pace ?? 'even') === 'even'
                ? 'The tempo of the drift and the cuts, on one dial. It travels in the code.'
                : 'In the preview and in the exported video. Same shapes, different clock.'}
          </p>
        </div>
      )}

      {/* ---- THE BEAT: the cuts land on the music ---------------------------
          Not a sixth rate roster — a QUANTISER on the two rows above. The TURN
          still says what a cut is and the PACE still says how often, and this
          rounds the hold those two asked for to the nearest musical multiple of
          the detected beat (lib/beat.ts). So a synced collage keeps every
          control it had, and the dissolve becomes a FRACTION of the snapped
          hold rather than a constant, or a 150 BPM bar would be 44% soft.
          It travels in the code — the RELATIONSHIP is a recipe; the tempo is a
          fact about a file and stays out. It does NOT ride the dice.
          SAYS WHAT IT NEEDS RATHER THAN DISABLING ITSELF (scar C126): with no
          track this row is still here, still settable, and the caption is what
          tells you the piece that is missing. ---------------------------- */}
      {hasImages && onSync && (
        <div className="ui-looks">
          <div className="ui-looks__chips" role="group" aria-label="Beat sync">
            {SYNCS.map(o => (
              <button
                key={o.id}
                type="button"
                className="ui-chip ui-chip--mini"
                data-active={(sync ?? 'off') === o.id}
                onClick={() => onSync(o.id)}
                title={o.title}
                aria-pressed={(sync ?? 'off') === o.id}
                data-testid={`sync-${o.id}`}
              >{o.label}</button>
            ))}
          </div>
          <p className="ui-caption" data-testid="beat-caption">
            {!hasMusic
              ? 'Cuts on the music. Add a track and the collage lands on its beat.'
              : beatBusy
                ? 'Listening to the track\u2026'
                : !beatGrid
                  ? 'No steady beat in that track \u2014 the cuts stay on their own clock.'
                  : (turn ?? 'hold') === 'hold'
                    ? `${Math.round(beatGrid.bpm)} BPM. Pick a TURN above and the cuts land on it.`
                    : (sync ?? 'off') === 'off'
                      ? `${Math.round(beatGrid.bpm)} BPM. Snap the cuts to it.`
                      : `${Math.round(beatGrid.bpm)} BPM \u2014 cutting ${beatsLabel(beatBeats)}.`}
          </p>
          {/* CREDIT ON THE PAGE, next to the thing they asked for. It doubles as
              the only place the capability is stated: the music button's own
              tooltip does not exist on a phone. See av/credits.json. */}
          <p className="ui-credit">
            The music button also takes a video \u2014 it keeps the sound and leaves the pictures out.
            Wished for by an anonymous Collage user.
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
