/// <reference types="vite/client" />
import React, { useState, useRef, useEffect, useLayoutEffect, useMemo, useCallback } from 'react';
import {
  Upload, Activity, X, Lock, Unlock, RefreshCw, Shuffle, Settings, Layout, Film, Plus,
  Maximize2, Minimize2, Dices, Music
} from 'lucide-react';

import { loadScriptSafe, analyzeImage } from './lib/analysis';
import { computeLayout, createRng } from './lib/layout';
import { rollDice, ASPECT_ROSTER } from './lib/diceRoll';
import { encodeState, decodeState, codeFromUrl, CODE_PARAM } from './lib/rollCode';
import { assignSources, distinctSourceCount } from './lib/fill';
import { arrangeBag, withFocus, withTwist, twistAngle, type ArrangementId, type FocusId, type TwistId } from './lib/composition';
import { withMove, type MoveId } from './lib/motion';
import { renderCanvas } from './lib/renderer';
import { planTitle, measureWith, type TitlePlace, type TitleSize } from './lib/title';
import type { LookId } from './lib/grade';
import { saveProject, loadProject, buildProjectBlob } from './lib/project';
import { canAutosave, hasUnsavedWork, shouldPromptRestore, formatAgo, AUTOSAVE_DEBOUNCE_MS } from './lib/session';
import * as sessionStore from './lib/sessionStore';
import { generateVectorExport } from './engine/color/vectorExport';
import { addToHistory, HistoryItem } from './lib/history';
import { Template } from './lib/templates';
import { AppState, ImageAsset, LayoutItem, LayoutMode, LiveClip, Point, PrimitiveType } from './types';
import { isVideoFile, formatTimecode, openClip, revokeFrames, type ExtractedFrame } from './lib/video';
import { isAudioFile, type SoundtrackSpec } from './lib/soundtrack';

import { Header } from './components/Header';
import { SimpleControls } from './components/SimpleControls';
import { AdvancedControls } from './components/AdvancedControls';
import { ExportDialog } from './components/ExportDialog';
import { ResultModal } from './components/ResultModal';
import { VideoStage, type StageRecorder } from './components/VideoStage';
import RenderWorker from './workers/render.worker?worker';
// THE LADDER. Built and unit-tested (57 cases) in an earlier cycle and then
// never imported by anything — which is exactly why the black-export bug that
// this module was written to prevent was still reachable when it was reported.
import {
  runWithFallback, probeMaxCanvas, deriveTiers, composeTiers,
  type TierAttempt, type AttemptControl, type RenderOutcome, type FallbackResult,
} from './lib/exportLimits';

let globalModel: any = null;

/** Monotonic across every upload call — `Date.now()` alone collides when two
 *  imports start in the same millisecond, and a duplicate id silently pins the
 *  wrong image to a locked cell. */
let assetSeq = 0;

/** Same reasoning as `assetSeq`, for clips. A collision here would make two
 *  different videos share one decoder. */
let clipSeq = 0;

/** Provenance carried from a video import into the shared asset pool. */
type AssetProvenance = Pick<ImageAsset, 'sourceKind' | 'sourceName' | 'sourceTime' | 'clipId'>;

interface UploadOptions {
  /** Distinct id namespace (video frames use 'vid'). */
  idPrefix?: string;
  /** Grow `count` so the new assets are actually visible on a non-empty canvas. */
  grow?: boolean;
  /** Per-file provenance, keyed by the File object itself. */
  meta?: Map<File, AssetProvenance>;
  /** Noun for the progress strip ("images" / "frames"). */
  noun?: string;
  /**
   * Advance the batch counter as these land. FALSE for a video's frames: the
   * unit the user picked was the CLIP, and the clip reports its own sub-
   * progress — counting its 8 frames as 8 more items makes the bar lurch.
   */
  track?: boolean;
}

/**
 * Images decoded before the FIRST commit to the canvas.
 *
 * Deliberately tiny. Everything before this bite lands is time the user spends
 * looking at an empty screen, and it is the only stretch of the import with no
 * visual answer to "is this working". Two pictures is enough to fill the frame
 * and prove the app came back.
 */
const FIRST_BITE = 2;

/** Steady-state bite, once pictures are visibly arriving and latency is hidden. */
const BITE = 5;

/** One paint. Committed assets are useless if React never gets to draw them. */
const nextFrame = (): Promise<void> =>
  new Promise((resolve) => {
    if (typeof requestAnimationFrame === 'function') requestAnimationFrame(() => resolve());
    else setTimeout(resolve, 16);
  });

const getCentroid = (path: {x:number, y:number}[]) => {
    let x = 0, y = 0;
    path.forEach(p => { x += p.x; y += p.y; });
    return { x: x / path.length, y: y / path.length };
};

const getDist = (p1: {x:number, y:number}, p2: {x:number, y:number}) => {
    return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
};

const createThumbnail = async (img: HTMLImageElement, maxDim = 1024): Promise<string> => {
    const scale = Math.min(maxDim / img.width, maxDim / img.height, 1);
    if (scale === 1) return img.src; 
    const canvas = document.createElement('canvas');
    canvas.width = Math.floor(img.width * scale);
    canvas.height = Math.floor(img.height * scale);
    const ctx = canvas.getContext('2d');
    if(!ctx) return img.src;
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    return new Promise(resolve => {
        canvas.toBlob(b => resolve(b ? URL.createObjectURL(b) : img.src), 'image/jpeg', 0.85);
    });
};

/** A laid-across stage rail: 44px of button, 16px inset, 8px of air. */
const RAIL_ROW_H = 68;

/**
 * HOW TALL THE STAGE RAIL IS AS A COLUMN — DERIVED, NOT GUESSED.
 *
 * Maximize · add · add video · add music · clear, at 44px with 8px between,
 * inset 16px from the top and given the same 16px back at the bottom. The
 * threshold that decides column-vs-row USED TO BE THE LITERAL 200, which was
 * already 16px short of the FOUR-button column it was written for — so a band
 * between 200 and 216px clipped the Clear button off the bottom, quietly,
 * because the rail sits inside an `overflow-hidden` parent and a clipped
 * absolute child costs the document no scrollWidth at all. Adding the music
 * button made that gap 68px wide and turned a latent edge into the ordinary
 * case: any phone with the video dock open lost Clear entirely.
 *
 * Deriving it means the next button added to the rail cannot reintroduce this.
 */
const RAIL_BUTTONS = 5;
const RAIL_COL_H = 16 + RAIL_BUTTONS * 44 + (RAIL_BUTTONS - 1) * 8 + 16;

export default function App() {
  const [activeTab, setActiveTab] = useState<'simple' | 'advanced'>('simple');
  /**
   * FULL BLEED. The controls dock is `shrink-0` with no height cap, so every
   * control panel added over the life of this app took its space out of the ONE
   * thing the app exists to show. Measured on production before this: the
   * artwork was 6.2% of a 1280x900 window, 10% of a 390px phone, and at 320px
   * the stage band collapsed to 52px — inside which `p-6` left the collage
   * rendering at THREE BY FOUR PIXELS. Every mobile gate passed, because they
   * assert the canvas is *visible*, never that it is big enough to look at.
   * (Operator: "it's hard to see the layouts when it's minimized and there's
   * so many features stacking — you need a way to maximize the shot".)
   * Maximized hides the header and the dock with `display:none`, which keeps
   * both MOUNTED: the Stage never leaves its position in the tree, so the clip
   * keeps its decoder, its AudioContext and its playhead across the toggle.
   */
  const [maximized, setMaximized] = useState(false);
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('minimal');
  const [primitive, setPrimitive] = useState<PrimitiveType>('rect');
  const [count, setCount] = useState(0);
  // false → the fragment count auto-follows the number of uploaded sources
  // (one per photo/video). Flips true the moment the user owns the count
  // themselves — the slider, the dice, or a loaded project/template.
  const countTouchedRef = useRef(false);
  /**
   * A MIRROR of the ref above, for the one consumer that needs to re-render when
   * it changes: the composition code. The ref has to stay, because the
   * auto-follow effect reads it from inside a closure whose deps are `[images]`
   * and a state read there would be one render stale. Both are written through
   * `ownCount` so they cannot drift apart.
   */
  const [countOwned, setCountOwned] = useState(false);
  const ownCount = (owned: boolean) => { countTouchedRef.current = owned; setCountOwned(owned); };
  const [density, setDensity] = useState(1);
  /** Why the last Open did nothing. Null when there is nothing to say. */
  const [openError, setOpenError] = useState<string | null>(null);
  const [seed, setSeed] = useState(Date.now());
  // The roster value, not a retyped 0.666. The frame shape travels in the share
  // code as a roster INDEX, so a default that is a rounding error off the roster
  // cannot round-trip through its own code.
  const [aspect, setAspect] = useState(ASPECT_ROSTER[1]);
  const [gutter, setGutter] = useState(0.005);
  const [entropy, setEntropy] = useState(0.5);
  // COMPOSITION — which photo lands in which fragment, what each fragment
  // centres on inside it, and how far the picture leans in there. See
  // lib/composition.ts. All three default to the behaviour the app has always
  // had, so nothing moves until you ask it to.
  const [arrangement, setArrangement] = useState<ArrangementId>('natural');
  const [focus, setFocus] = useState<FocusId>('auto');
  const [twist, setTwist] = useState<TwistId>('none');
  /** THE MOVE — how the picture drifts inside its fragment. See lib/motion.ts. */
  const [move, setMove] = useState<MoveId>('still');
  const [bgColor, setBgColor] = useState('#050505'); 
  const [avgColor, setAvgColor] = useState<{r:number, g:number, b:number} | null>(null); 

  // --- THE TITLE ------------------------------------------------------------
  // CONTENT, not a parameter — which is why it lives here and not in the roll.
  // It travels in a saved project and in the SVG manifest (both carry the whole
  // AppState) and deliberately NOT in the composition code: a code is a recipe
  // that anyone can open with their OWN photographs, and somebody else's
  // caption over your pictures is not the same collage.
  const [titleText, setTitleText] = useState('');
  const [titlePlace, setTitlePlace] = useState<TitlePlace>('bl');
  const [titleSize, setTitleSize] = useState<TitleSize>('md');
  /** THE LOOK — the colour grade over every fragment. See lib/grade.ts. */
  const [look, setLook] = useState<LookId>('none');
  
  /** Name of the recipe the last dice roll drew from, shown in the readout. */
  const [lastRecipe, setLastRecipe] = useState<string | undefined>(undefined);

  const [lockedCells, setLockedCells] = useState<Map<number, string>>(new Map());
  const [shuffledIndices, setShuffledIndices] = useState<number[]>([]); 
  const [shuffleTrigger, setShuffleTrigger] = useState(0);

  const [layoutItems, setLayoutItems] = useState<LayoutItem[]>([]);
  const [isLayoutComputing, setIsLayoutComputing] = useState(false);

  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  /**
   * WHAT IS STILL ARRIVING — and never a reason to cover the screen.
   *
   * This replaced a `fixed inset-0` black overlay that stayed up until the LAST
   * file had decoded. Picking 30 things in Photos therefore meant: iOS spends a
   * while handing the files over, then the app blanks itself for the whole
   * decode, then everything appears at once. From the outside that is
   * indistinguishable from a hang, and it hid the one fact worth showing —
   * how much is left.
   *
   * Now the assets commit in bites as they decode, so the collage FILLS while
   * the import runs, and this drives a slim strip that never takes the canvas.
   * `sub` is progress within the current item (a clip's frame extraction),
   * which is the only unit that takes long enough to need its own bar.
   */
  const [ingest, setIngest] = useState<{ done: number; total: number; label: string; sub: number } | null>(null);
  const [exportStatus, setExportStatus] = useState('idle');
  const [exportMsg, setExportMsg] = useState('');
  const [aiState, setAiState] = useState('inactive');
  
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [resultBlobUrl, setResultBlobUrl] = useState<string | null>(null);

  // --- VIDEO INTAKE ---
  /**
   * Clips still playable, as opposed to the stills already taken from them.
   * The app owns their object URLs for the whole session — see `LiveClip`.
   */
  const [clips, setClips] = useState<LiveClip[]>([]);
  /** Cleared if the live compositor cannot be created; falls back to the still preview. */
  const [stageOk, setStageOk] = useState(true);
  /**
   * THERE IS NO FRAME PICKER. There is no setting for one either.
   *
   * This app used to answer "here is a video" with "how many frames shall I pull
   * out of it?" — a slider, a strategy, a contact sheet, a commit button. It was
   * made opt-in, then default-off, and the owner filed the same complaint a third
   * time anyway: "you're still asking for how many frames to pull instead of just
   * loading the video. Stop asking for frames period." Default-off was the wrong
   * fix, because an opt-in ask is still an ask — the toggle sat in Settings under
   * the words "Choose frames on import", and the button that took a video was
   * labelled "Extract frames from a video". A video is a video.
   *
   * So the route is gone: no `videoQueue`, no sheet, no `genart.framePicker`
   * preference (a persisted `'1'` from an older visit would otherwise pin a
   * returning user to the behaviour they asked us to delete). Frames survive
   * ONLY as an internal detail — one poster raster per clip, which is what the
   * static exports draw and what a device with no decoder to spare falls back
   * to. Nothing about it reaches the user, and nothing about it asks.
   */
  /**
   * Where the live-stage transport renders. It is a DOM node in the control
   * dock rather than an overlay on the canvas: chrome that sits on the artwork
   * covers the thing the user is here to look at.
   */
  const [stageControlsHost, setStageControlsHost] = useState<HTMLDivElement | null>(null);
  /** Set by the live stage while it is mounted; null otherwise. See StageRecorder. */
  const recorderRef = useRef<StageRecorder | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const dragDepth = useRef(0);
  const noticeTimer = useRef<number | null>(null);
  // CRASH-SAFE SESSION RECOVERY (well bug: "capturing at 4k ... lost what I was
  // doing"). `restorePrompt` holds the stored session's metadata while the
  // launch banner offers to bring it back; `dirtyRef` tracks whether the pool
  // has changed since the last explicit download, which is what the unload
  // guard warns about. The autosave itself is best-effort insurance in
  // IndexedDB — see lib/session.ts (gates) and lib/sessionStore.ts (I/O).
  const [restorePrompt, setRestorePrompt] = useState<{ savedAt: number; images: number } | null>(null);
  const dirtyRef = useRef(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const musicInputRef = useRef<HTMLInputElement>(null);
  /**
   * THE SOUNDTRACK. One track, because "music under this collage" is one job —
   * a second one is a mix, and a mix is a different tool. The `blob:` URL is
   * minted and OWNED here (revoked when replaced or cleared), exactly like a
   * `LiveClip`'s: the Stage is handed the string and never revokes it.
   */
  const [soundtrack, setSoundtrack] = useState<SoundtrackSpec | null>(null);
  /**
   * HOW BIG THE ARTWORK IS ALLOWED TO BE — and why it has to be measured.
   *
   * The frame was `{ aspectRatio, maxHeight: '100%', maxWidth: '100%' }` with no
   * width or height, so it was CONTENT-SIZED: it sized to the canvas, and the
   * canvas sizes itself from `cv.clientWidth` (Stage.resize, floored at 240),
   * which comes from the frame. A circular definition resolves at the floor and
   * stays there, so the collage rendered at 240x360 CSS px on a 1280px window
   * and 300x450 on a 1900x1300 one — a 1900x776 band showing a 300px picture.
   * `maxHeight` could only ever shrink that further; nothing could grow it. The
   * two symptoms the operator reported are the same bug seen from both ends.
   *
   * So the BAND is measured and the frame is given explicit pixels. The canvas
   * still picks its own backing store off that CSS width (a render budget, not
   * a display size), but it can no longer decide how big the artwork looks.
   */
  const [artBand, setArtBand] = useState<{ w: number; h: number } | null>(null);
  const bandObserverRef = useRef<ResizeObserver | null>(null);
  const bandElRef = useRef<HTMLDivElement | null>(null);

  /** Read the band's content box right now, from layout. */
  const measureBand = useCallback((el: HTMLDivElement | null) => {
    if (!el) return;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    setArtBand({
      w: Math.floor(r.width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)),
      h: Math.floor(r.height - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom)),
    });
  }, []);

  /**
   * THE ONE TRANSITION THAT CANNOT WAIT A FRAME. A ResizeObserver reports after
   * layout, so on a discontinuous band change the frame keeps its old explicit
   * pixels for one paint — and the band is `overflow-hidden`, so that paint is
   * CLIPPED, not letterboxed. An adversarial verifier caught it in real
   * composited pixels (CDP screencast, frame-stamped): leaving full bleed at
   * 1280x900 painted the collage at 589x884 inside a 1248x459 band, header and
   * dock already back, top and bottom sliced off — 8 of 8 exits, 5 captured on
   * screen. Entering and leaving full bleed is OUR state change, so it is
   * measured in a layout effect: React flushes this before the browser paints,
   * and the frame is never wrong on screen. `maxWidth/maxHeight` below stay as
   * the backstop for the changes we do not drive (rotation, URL-bar collapse).
   */
  useLayoutEffect(() => { measureBand(bandElRef.current); }, [maximized, measureBand]);

  const setBandEl = useCallback((el: HTMLDivElement | null) => {
    bandObserverRef.current?.disconnect();
    bandObserverRef.current = null;
    bandElRef.current = el;
    if (!el) return;
    // MEASURE FIRST, OBSERVE SECOND. This needs no observer, and doing it after
    // the ResizeObserver guard meant an engine without one fell through to the
    // content-sized style FOREVER — silently restoring the exact bug this is
    // here to delete, on the oldest devices, where it is worst.
    measureBand(el);
    if (typeof ResizeObserver === 'undefined') return;
    // `contentRect` is the content box, so the band's own padding is already
    // out of it and the fit below never has to know what the padding is.
    const ro = new ResizeObserver((entries) => {
      const box = entries[entries.length - 1].contentRect;
      setArtBand({ w: Math.floor(box.width), h: Math.floor(box.height) });
    });
    ro.observe(el);
    bandObserverRef.current = ro;
  }, []);
  useEffect(() => () => bandObserverRef.current?.disconnect(), []);

  /**
   * The stage rail is four 44px buttons and three gaps — 200px of column, plus
   * its 16px inset. A phone held LANDSCAPE leaves the band about 118px, and the
   * band clips, so `Clear all` was simply gone off the bottom with nothing to
   * scroll. Short band, lay the rail across instead of down.
   */
  const railRow = !!artBand && artBand.h < RAIL_COL_H;

  /**
   * The largest box of ratio `aspect` that fits the measured band.
   *
   * A rail laid ACROSS reaches back over the middle of a narrow viewport, where
   * the column never did, so it would sit on top of the artwork instead of
   * beside it — on a 320px phone it covered the picture outright. A row is
   * therefore charged against the band (44px of buttons, 16px inset, 8px of
   * air) and the artwork fits under it. Small, but never hidden — and full
   * bleed, which is the honest answer at these heights, is one tap away.
   */
  const artFit = useMemo(() => {
    if (!artBand || artBand.w < 1 || artBand.h < 1) return null;
    const bandH = railRow ? artBand.h - RAIL_ROW_H : artBand.h;
    if (bandH < 1) return null;
    const w = Math.min(artBand.w, bandH * aspect);
    return { w: Math.floor(w), h: Math.floor(w / aspect) };
  }, [artBand, aspect, railRow]);

  /**
   * Never strand anyone in full bleed. Both exits — the pill and the rail —
   * live on the stage, and the stage only renders while there are images, so an
   * empty pool while maximized is a screen with no way out but a keyboard. The
   * REACHABLE way in was pressing F with nothing loaded (the shortcut had no
   * pool condition, this effect only re-runs when the COUNT changes, and F does
   * not change it), so the entry is now refused at the door and this stays as
   * the backstop for a pool that empties later.
   */
  const canMaximize = images.length > 0;
  useEffect(() => { if (!canMaximize) setMaximized(false); }, [canMaximize]);
  // Read through a ref: the key listener is bound once, on purpose.
  const canMaximizeRef = useRef(canMaximize);
  canMaximizeRef.current = canMaximize;

  /**
   * Put the caret on the control that REPLACED the one that just vanished.
   * `display:none` on the dock blurs whatever had focus inside it, and the
   * maximize button and the exit pill unmount each other, so without this a
   * keyboard user is dumped back to the top of the tab order on every toggle.
   * Skips the first run so nothing is focus-grabbed on load.
   */
  const maxBtnRef = useRef<HTMLButtonElement>(null);
  const exitBtnRef = useRef<HTMLButtonElement>(null);
  const maxSettled = useRef(false);
  useEffect(() => {
    if (!maxSettled.current) { maxSettled.current = true; return; }
    (maximized ? exitBtnRef.current : maxBtnRef.current)?.focus();
  }, [maximized]);

  const isMobile = useMemo(() => /iPhone|iPad|iPod|Android/i.test(navigator.userAgent), []);

  /**
   * F toggles full bleed, Escape leaves it. Deliberately deaf while a field has
   * focus (the title box takes an `f` like any other letter) and while a dialog
   * is open, because Export, Result and the trim sheet each own Escape already
   * and stealing it would close two things with one press.
   */
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const t = e.target as HTMLElement | null;
      if (t && (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable)) return;
      // RENDERED, not merely PRESENT. The shared wishing well closes with
      // `modal.classList.remove("on")` against a `.fb-wrap{display:none}` rule —
      // it builds its sheet once and leaves it in the document forever. Testing
      // for the existence of [role="dialog"] therefore killed F and Escape for
      // the rest of the session the moment anyone opened Feedback once. A
      // display:none subtree has no client rects, which is true for every
      // dialog here and costs no layout to ask.
      const dialogs = document.querySelectorAll('[role="dialog"]');
      for (let i = 0; i < dialogs.length; i++) {
        if (dialogs[i].getClientRects().length > 0) return;
      }
      if (e.key === 'Escape') { setMaximized(false); return; }
      // Nothing to maximize with an empty pool — F used to hide the whole UI
      // and leave the drop target alone on a black page.
      if (e.key === 'f' || e.key === 'F') {
        if (!canMaximizeRef.current) return;
        // Stop lives in the transport row, and full bleed hides the dock. A take
        // you cannot see and cannot stop is worse than no shortcut.
        if (recorderRef.current?.isRecording) return;
        e.preventDefault();
        setMaximized(m => !m);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    const bootAI = async () => {
      setAiState('loading');
      // @ts-ignore
      const tfLoaded = await loadScriptSafe('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.11.0/dist/tf.min.js');
      // @ts-ignore
      const bfLoaded = await loadScriptSafe('https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js');
      if (!tfLoaded || !bfLoaded) { setAiState('failed'); return; }
      try {
        // @ts-ignore
        if (window.blazeface) { globalModel = await window.blazeface.load(); setAiState('ready'); } 
        else { setAiState('failed'); }
      } catch (e) { setAiState('failed'); }
    };
    bootAI();
  }, []);

  const PREVIEW_W = 1200;
  const effectiveCount = count * density;
  const zoom = 1 + (density - 1) * 0.5;

  // --- FRAGMENT COUNT FOLLOWS THE UPLOAD --------------------------------------
  // One fragment per photo or video imported — a video counts ONCE however many
  // frames were extracted from it. Until the user sets a count themselves the
  // count simply IS the upload total, so a fresh import shows exactly the things
  // that were imported, each once, instead of a randomised field with one clip
  // multiplied across a dozen look-alikes.
  //
  // Once the count is user-owned we keep their number — but never let it fall
  // BELOW the number of sources: a photo or (crucially) a video just imported
  // must always have a slot to appear and PLAY in. That grow-to-cover is the
  // "nothing uploaded is stranded" guarantee, and it restores the behaviour the
  // old ceiling logic used to give a late video add, which the touched-gate had
  // otherwise removed.
  //
  // A CODE CHOOSES ITS COUNT BEFORE IT CAN SEE THE POOL, and grow-to-cover has
  // to be told so. The sender picks a count against photographs that are already
  // loaded, so the effect above never re-runs and their number stands. The
  // recipient's order is reversed — `?c=` applies at mount, the photographs land
  // afterwards — and grow-to-cover then read that as a late add and raised the
  // count to the pool size. Same code, same photographs, different collage, and
  // the address bar was rewritten to the NEW code 400ms later, so the thing they
  // were sent could not even be recovered. Measured: a 3-fragment code opened
  // with 6 sources produced 6.
  //
  // `pendingCountRef` holds the count a code asked for until the drop it is
  // waiting for has landed, which makes the two orders agree. It is cleared at
  // the END of an ingest rather than on the first batch, because one drop
  // commits in several batches and each one re-runs this effect. Anything
  // imported after that is a genuine late add and grows the count as before, so
  // the "nothing uploaded is stranded" guarantee is untouched for every source
  // that arrives once the composition is in place.
  // The latch is keyed to a DROP, and the drop marker is React state rather than
  // a flag cleared when the upload loop finishes. That first attempt raced and
  // lost: the loop yields with `requestAnimationFrame`, which resolves BEFORE
  // React flushes passive effects, so the flag was already cleared by the time
  // this effect ran and the count grew anyway. Threading the marker through
  // state puts it in the same ordered queue as `setImages`, so there is no
  // window at all — the correctness comes from React's ordering rather than
  // from a guess about when a frame lands.
  const [dropId, setDropId] = useState(0);
  const pendingCountRef = useRef<{ count: number; drop: number } | null>(null);
  useEffect(() => {
    if (images.length === 0) return;
    if (pendingCountRef.current) {
      // While the drop a code is waiting for is still landing, the count the
      // code asked for stands — `applyCompositionCode` has already set it, so
      // the honest thing here is to do nothing. Once that drop is over the latch
      // retires, and every later import grows the count exactly as before.
      if (pendingCountRef.current.drop !== dropId) pendingCountRef.current = null;
      return;
    }
    const n = distinctSourceCount(images);
    setCount(prev => (countTouchedRef.current ? Math.max(prev, n) : n));
  }, [images, dropId]);

  // --- ASYNC LAYOUT ENGINE ---
  useEffect(() => {
      let active = true;
      const runLayout = async () => {
          if (images.length === 0) return;
          setIsLayoutComputing(true);
          try {
              const rng = createRng(seed);
              // Pass images for Stencil Mode
              const items = await computeLayout(PREVIEW_W, PREVIEW_W / aspect, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive, 0, aspect);
              if (active) setLayoutItems(items);
          } catch(e) { console.error("Layout failed", e); } 
          finally { if (active) setIsLayoutComputing(false); }
      };
      const t = setTimeout(runLayout, 50);
      return () => { active = false; clearTimeout(t); };
  }, [layoutMode, primitive, effectiveCount, seed, aspect, gutter, entropy, images]); 

  function PREVIEW_H(a: number, w: number) { return w / a; }

  // --- ASSIGNMENT LOGIC ---
  useEffect(() => {
    if (images.length === 0) return;
    setShuffledIndices(prev => {
        /**
         * ONE SLOT PER ACTUAL CELL — not per REQUESTED cell.
         *
         * `effectiveCount` is what the user asked for; `layoutItems.length` is
         * what the construction produced, and for most of the generative roster
         * those differ on purpose. A kaleidoscope must contain a whole number of
         * mirrored wedges, a Flower of Life emits seven cells per lattice
         * centre, Penrose deflates in phi^2 steps — the count is documented as a
         * target, not a guarantee.
         *
         * Sizing the assignment to the request left every cell past it holding
         * `undefined`, and `renderCanvas` skips those — so asking for 70
         * fragments of a 105-cell kaleidoscope painted 35 of them BLACK, in
         * wedges, which reads as a broken layout rather than a missing image.
         * The legacy grid modes returned exactly `count`, so nothing downstream
         * had ever been told the two could differ.
         */
        const slotCount = Math.max(effectiveCount, layoutItems.length);
        const newIndices = new Array(slotCount).fill(-1);
        const rng = createRng(seed + shuffleTrigger);
        const imageIdToIndex = new Map(images.map((img, i) => [img.id, i]));
        const usedImageIndices = new Set<number>();
        lockedCells.forEach((imgId, cellIdx) => {
            const currentImgIdx = imageIdToIndex.get(imgId);
            if (cellIdx < slotCount && currentImgIdx !== undefined) {
                newIndices[cellIdx] = currentImgIdx;
                usedImageIndices.add(currentImgIdx);
            }
        });
        const emptySlots = [];
        for(let i=0; i<slotCount; i++) { if(newIndices[i] === -1) emptySlots.push(i); }
        if (emptySlots.length > 0) {
            // SOURCE-FIRST, DUPLICATE-FREE FILL. `assignSources` (src/lib/fill.ts)
            // round-robins the pool by SOURCE — a video is one source however many
            // frames were extracted from it — so every distinct photo/video is
            // placed before any repeats, and a repeat is always a fresh moment. At
            // the default count (one slot per upload) each source appears exactly
            // once, and the fragment holding a video carries its clipId and plays
            // the live clip instead of being buried under its own look-alike stills.
            const bag = assignSources({
                slotCount: emptySlots.length,
                images,
                used: usedImageIndices,
                rng,
            });

            // ARRANGEMENT — which of those photos goes in which fragment.
            //
            // NOT a sort of the bag: `arrangeBag` (lib/composition.ts) ranks the
            // photos by a metric AND the fragments by a spatial key, then zips the
            // two, which is what lets "by hue" mean "the colour wheel wrapped
            // around the canvas" instead of "left to right". It is a PERMUTATION
            // of the bag, so the duplicate-free guarantee above survives it
            // untouched. It necessarily re-clumps a clip's frames (they share a
            // palette) — that IS what choosing one means, and `natural` is the
            // default, so the source-first order is what you normally get.
            const bagCells = emptySlots.map(slotIdx => {
                const b = layoutItems[slotIdx]?.bounds;
                if (!b || !(b.w > 0) || !(b.h > 0)) return null;
                const H = PREVIEW_W / aspect;
                return {
                    cx: (b.x + b.w / 2) / PREVIEW_W,
                    cy: (b.y + b.h / 2) / H,
                    area: (b.w * b.h) / (PREVIEW_W * H),
                };
            });
            // `shuffleTrigger` re-deals INSIDE the ranking. Without it, an
            // arrangement's output depends only on the SET of photos and the
            // geometry, so Shuffle — which only re-orders the bag — produced the
            // identical picture every press, silently, on the default count.
            const placed = arrangeBag({ bag, cells: bagCells, images, arrangement, shuffle: shuffleTrigger });

            emptySlots.forEach((slotIdx, i) => { newIndices[slotIdx] = placed[i]; });
        }
        return newIndices;
    });
    // `layoutItems.length` is a dependency because the cell count is an OUTPUT
    // of the layout, not an input to it — without it the assignment keeps the
    // size from the previous layout and the new one is short by the difference.
    // `layoutItems` (not just its length) because an arrangement reads the
    // fragments' POSITIONS and AREAS, so the same bag lands differently the
    // moment the construction moves. The bag itself is seed-deterministic, so a
    // recompute that changes nothing costs one O(n log n) pass on n <= ~300.
  }, [images, effectiveCount, layoutItems, aspect, seed, shuffleTrigger, arrangement]);

  /** The pool in draw order. Memoised because the live Stage rebuilds its whole
   *  draw list whenever this identity changes — a fresh array every render would
   *  re-do the crop maths and the clip admission pass on every keystroke.
   *
   *  FOCUS is applied HERE, per SLOT rather than per photo, so one photo landing
   *  in three fragments can show three different parts of itself. `withFocus`
   *  re-points `analysis.face`, which every crop path already reads — the live
   *  Stage, the static renderer, the export worker and the vector export — so
   *  one seam steers all four. On `auto` it hands back the same object by
   *  reference, so the default path allocates nothing and recomputes nothing.
   *
   *  TWIST rides the SAME seam for the same reason, and takes the fragment's
   *  geometry as well as the slot: an angle is a field over the canvas, so
   *  `pinwheel` and `cascade` need to know WHERE this fragment sits, not merely
   *  which slot it is. That is why `layoutItems` is a dependency here — move the
   *  construction and the lean has to be recomputed with it. */
  const orderedAssets = useMemo(
    () => {
      const H = PREVIEW_W / aspect;
      return shuffledIndices.map((idx, slot) => {
        const slotSeed = (seed ^ (slot * 2654435761)) | 0;
        const b = layoutItems[slot]?.bounds;
        const cell = b && b.w > 0 && b.h > 0
          ? { cx: (b.x + b.w / 2) / PREVIEW_W, cy: (b.y + b.h / 2) / H, area: (b.w * b.h) / (PREVIEW_W * H) }
          : null;
        return withMove(withTwist(withFocus(images[idx], focus, slotSeed), twist, slotSeed, cell), move, cell);
      });
    },
    [shuffledIndices, images, focus, twist, move, seed, layoutItems, aspect],
  );

  /**
   * LIVE when there is a clip to play. This is the whole switch between the two
   * preview paths: photographs get the cheap static JPEG they have always had,
   * and a composition containing video gets a canvas that keeps moving.
   * `stageOk` drops it back to the still path if the compositor cannot start.
   */
  /**
   * LIVE when there is something to keep drawing — a clip to play, OR a move.
   *
   * THE MOVE HAD TO WIDEN THIS OR IT WOULD HAVE BEEN UNREACHABLE. The gate used
   * to be `clips.length > 0` alone, and it feeds three things: which preview is
   * mounted, whether the static JPEG is rendered at all, and — through
   * `canExportVideo` — whether the export sheet offers video. So on the old
   * gate a collage of PHOTOGRAPHS could not be recorded at all, which is fine
   * for a still (there is nothing to record) and wrong the moment the fragments
   * drift: the one thing a photo collage could never be was a video, and a move
   * is precisely what makes it one.
   *
   * Widening it costs nothing when nothing moves. `Stage` composites stills on
   * exactly the path it already uses for a video collage's photographic
   * fragments, `syncClips([])` is a no-op, the transport dock renders per clip
   * and so renders none, and the demand-driven tick idles at zero rAF unless
   * `moving` — which is the same flag this depends on.
   */
  const moving = move !== 'still' && images.length > 0;
  // A LIVE COMPOSITION IS ONE THAT CHANGES OR SOUNDS. Clips move; THE MOVE makes
  // photographs move; MUSIC makes a still collage a thing worth recording — and
  // the Stage is the only surface that can play it (its `masterGain` is what
  // `captureStream` taps), so without this the track would be inaudible and
  // absent from a realtime take.
  // ...AND THERE HAS TO BE A COLLAGE. `images.length > 0` is what decides
  // whether the art branch — and therefore the Stage — is rendered at all, so
  // without it here `liveMode` claims a live surface that does not exist: the
  // dock draws 13px of empty chrome (measured) and the Export sheet offers a
  // video whose recorder handle is null. It is a no-op for the two older terms
  // (`moving` already requires images, and a clip cannot exist without the
  // frames it landed in the pool) and load-bearing for the third, because music
  // is the one source that can arrive before any photograph.
  const liveMode = images.length > 0 && (clips.length > 0 || moving || !!soundtrack) && stageOk;

  /**
   * THE WRAP IS DECIDED HERE, ONCE, and the RESULT is what travels.
   *
   * Four surfaces draw this caption — the still preview, the live Stage (which
   * both video recorders capture), an OffscreenCanvas on a worker THREAD and an
   * SVG string. Letting each of them wrap the text itself would decide the
   * break four times against four font environments, and the worker is the one
   * that would disagree: a title on two lines in the preview and three in the
   * exported file is precisely the divergence ONE LAYOUT was written to remove.
   * So it is measured against a real 2D context here, at `TITLE_BASIS`, and
   * every path scales the finished plan.
   */
  const measureCanvasRef = useRef<CanvasRenderingContext2D | null>(null);
  const titlePlan = useMemo(() => {
    if (!measureCanvasRef.current) {
      try {
        const c = document.createElement('canvas');
        c.width = 8; c.height = 8;
        measureCanvasRef.current = c.getContext('2d');
      } catch { measureCanvasRef.current = null; }
    }
    const mctx = measureCanvasRef.current;
    if (!mctx) return null;
    return planTitle({ text: titleText, place: titlePlace, size: titleSize }, aspect, measureWith(mctx));
  }, [titleText, titlePlace, titleSize, aspect]);

  // --- RENDER (still path) ---
  // Skipped entirely in live mode: the Stage is painting the same composition
  // onto a real canvas, so producing a JPEG of it every state change would be
  // pure waste — and a second, disagreeing source of truth for the same pixels.
  useEffect(() => {
    if (liveMode) return;
    if (images.length === 0 || shuffledIndices.length === 0 || layoutItems.length === 0) return;
    const runRender = async () => {
       try {
         const orderedImages = orderedAssets;
         const orderedPreviews = orderedImages.map(img => img ? ({ ...img, src: img.previewSrc || img.src }) : img);
         const canvas = await renderCanvas(PREVIEW_W, aspect, layoutMode, layoutItems, orderedPreviews, seed, zoom, bgColor, titlePlan, look);
         canvas.toBlob(blob => {
             if (previewUrl) URL.revokeObjectURL(previewUrl);
             if (blob) setPreviewUrl(URL.createObjectURL(blob));
         }, 'image/jpeg', 0.85);
       } catch (e) { console.error("Render failed", e); }
    };
    const t = setTimeout(runRender, 50);
    return () => clearTimeout(t);
  }, [images, layoutItems, shuffledIndices, orderedAssets, seed, zoom, bgColor, liveMode, titlePlan, look]);

  const handleShuffle = () => setShuffleTrigger(prev => prev + 1);
  /**
   * ROLL EVERYTHING AT ONCE — layout, fragment count, chaos, frame shape,
   * gutter, background and seed.
   *
   * Deliberately NOT a "randomise" that nudges one slider: the interesting
   * space is the combination, and the whole point of the roll is to reach
   * pairings nobody would assemble by hand. `rollDice` does the constraining
   * (see diceRoll.ts) so what lands here is always a coherent composition.
   *
   * Locked fragments are released: a roll that kept them would have to graft
   * them onto a layout with a different topology, and `handleRemix` already
   * exists for exactly that "keep what I chose" intent.
   */
  const handleDice = () => {
    const roll = rollDice({ hasVideo: clips.length > 0 });
    // The dice chooses an explicit fragment count; don't let the next upload
    // silently overwrite a composition the user rolled on purpose.
    ownCount(true);
    // This roll supersedes any count a link was still holding for a drop.
    pendingCountRef.current = null;
    setLayoutMode(roll.layout);
    setCount(roll.count);
    setEntropy(roll.entropy);
    setAspect(roll.aspect);
    setGutter(roll.gutter);
    setBgColor(roll.bg);
    // `zoom` is DERIVED from density here, not stored — so the roll does not
    // touch it. Rolling density instead would silently multiply the fragment
    // count it just chose (effectiveCount = count * density), which is exactly
    // the kind of hidden coupling that makes a random button feel broken.
    setSeed(roll.seed);
    // The composition is part of the roll, not a setting the roll leaves alone:
    // the same fragments in the same shapes, paired a different way, is a
    // genuinely different picture — which is the whole point of pressing it.
    setArrangement(roll.arrangement);
    setFocus(roll.focus);
    setTwist(roll.twist);
    // The grade is part of the roll for the same reason the composition is: the
    // same fragments graded differently is a different picture, and the point
    // of the button is a different picture.
    setLook(roll.look ?? 'none');
    // And the move is part of it for the third time and the same reason — a
    // collage that drifts is not the same picture as one that sits still.
    setMove(roll.move ?? 'still');
    setLastRecipe(roll.recipe);
    setLockedCells(new Map());
    // The deal is part of the composition and the roll re-deals it; leaving the
    // old shuffle count on would make the SAME code describe two pictures.
    setShuffleTrigger(0);
  };

  // ===========================================================================
  // THE COMPOSITION CODE — the good roll you can keep, come back to, and send.
  //
  // `diceRoll.ts` has promised "same code, same collage, on any device" since
  // the roster landed and nothing ever called `encodeRoll`. The missing piece
  // was never the codec: it was that the roll only flowed ONE way, into fifteen
  // setState calls with no route back. `lib/rollCode.ts` is that route, in both
  // directions, pure, so the round trip is swept to a hard equality.
  //
  // Everything the picture depends on rides in it EXCEPT the photographs, which
  // is the point — a code is a recipe. Your photographs, their composition.
  // ===========================================================================
  const compositionCode = useMemo(() => encodeState({
    layoutMode, primitive, count, density, entropy, aspect, gutter,
    bgColor, seed, arrangement, focus, twist, look, move, shuffle: shuffleTrigger,
    countOwned,
  }), [layoutMode, primitive, count, density, entropy, aspect, gutter,
       bgColor, seed, arrangement, focus, twist, look, move, shuffleTrigger, countOwned]);

  /**
   * Apply a pasted code. Returns false when it is not one, so the caller can
   * say so instead of silently doing nothing — a half-applied composition on
   * top of the one already on screen is worse than a refusal, because you
   * cannot tell which half moved.
   */
  const applyCompositionCode = (code: string): boolean => {
    const s = decodeState(code);
    if (!s) return false;
    // The code says whether its count was a DECISION or a DEFAULT, and that is
    // the whole difference between "3 fragments, I meant it" and "6 fragments,
    // because I had 6 photographs". Copying the sender's answer is what lets a
    // derived count still get out of the way of the recipient's pool — including
    // on a plain refresh, which now replays this page's own address bar.
    ownCount(s.countOwned);
    // And when an OWNED count arrives BEFORE the photographs — a `?c=` link on a
    // cold page — latch it, or grow-to-cover reads the first drop as a late add
    // and silently replaces the number the sender chose. Cleared when that
    // drop ends. A derived count is never latched: it is a default, and the
    // recipient's own pool is a better one.
    if (s.countOwned && images.length === 0) {
      pendingCountRef.current = { count: s.count, drop: dropId };
    }
    setLayoutMode(s.layoutMode);
    setPrimitive(s.primitive);
    setCount(s.count);
    setDensity(s.density);
    setEntropy(s.entropy);
    setAspect(s.aspect);
    setGutter(s.gutter);
    setBgColor(s.bgColor);
    setLook(s.look);
    setSeed(s.seed);
    setArrangement(s.arrangement);
    setFocus(s.focus);
    setTwist(s.twist);
    setMove(s.move);
    setShuffleTrigger(s.shuffle);
    // Fragments pinned by hand refer to cells of the layout that is being
    // replaced, so they cannot survive the change any more than they survive a
    // roll. The recipe name belonged to a roll this session did not make.
    setLockedCells(new Map());
    setLastRecipe(undefined);
    return true;
  };

  /**
   * A CODE IN THE ADDRESS BAR, so a link is a composition.
   *
   * Read once on mount, then kept current with `replaceState` — replace, never
   * push, or every slider tick would become a Back-button step. The address bar
   * carrying the live code is what makes the browser's own share sheet work
   * without this app shipping a share button of its own.
   */
  const bootCodeRef = useRef<string | null>(null);
  if (bootCodeRef.current === null && typeof window !== 'undefined') {
    bootCodeRef.current = codeFromUrl(window.location.href) ?? '';
  }
  /**
   * A code that arrived damaged, kept where it can be read and repaired.
   *
   * A truncated or mangled `?c=` used to do NOTHING — no picture, no message —
   * and 400ms later the address-bar rewrite replaced it with this session's own
   * code, so the thing you were sent could not even be looked at. Refusing half
   * a composition is right; refusing it silently and then destroying the
   * evidence is not. It is handed to the paste box instead, where a missing
   * character is visible and one keystroke from fixed.
   */
  const [rejectedBootCode, setRejectedBootCode] = useState('');
  useEffect(() => {
    const boot = bootCodeRef.current;
    if (boot && !applyCompositionCode(boot)) {
      setRejectedBootCode(boot);
      flashNotice('That link’s composition code did not survive the trip — it is in the paste box below.');
    }
    // Mount only: a link opens the composition it names, and from then on the
    // person driving the app owns the state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.history?.replaceState) return;
    const t = setTimeout(() => {
      try {
        const url = new URL(window.location.href);
        if (url.searchParams.get(CODE_PARAM) === compositionCode) return;
        url.searchParams.set(CODE_PARAM, compositionCode);
        // A link that arrived as `#CODE` has now been answered in the query, and
        // leaving the hash behind would park a STALE code one character away
        // from the live one in the same address bar. Cleared only when the hash
        // is itself a code — a real anchor is somebody else's business.
        if (url.hash && codeFromUrl(`${url.origin}${url.pathname}${url.hash}`)) url.hash = '';
        window.history.replaceState(null, '', url.toString());
      } catch { /* a URL the browser will not rewrite is not worth a crash */ }
    }, 400);
    return () => clearTimeout(t);
  }, [compositionCode]);

  const handleRemix = async () => {
      const lockedGoals: {imgId: string, x: number, y: number}[] = [];
      lockedCells.forEach((imgId, idx) => {
          if (layoutItems[idx]) {
              const c = getCentroid(layoutItems[idx].path);
              lockedGoals.push({ imgId, x: c.x, y: c.y });
          }
      });
      const newSeed = Date.now();
      const rng = createRng(newSeed);
      const newLayout = await computeLayout(PREVIEW_W, PREVIEW_W/aspect, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive, 0, aspect);
      const newLocked = new Map<number, string>();
      const occupiedNewIndices = new Set<number>();
      lockedGoals.forEach(goal => {
          let closestIdx = -1; let minD = Number.MAX_VALUE;
          newLayout.forEach((item, i) => {
              if (occupiedNewIndices.has(i)) return;
              const c = getCentroid(item.path); const d = getDist(c, goal);
              if (d < minD) { minD = d; closestIdx = i; }
          });
          if (closestIdx !== -1) { newLocked.set(closestIdx, goal.imgId); occupiedNewIndices.add(closestIdx); }
          else {
              const anyIdx = newLayout.findIndex((_, i) => !occupiedNewIndices.has(i));
              if (anyIdx !== -1) { newLocked.set(anyIdx, goal.imgId); occupiedNewIndices.add(anyIdx); }
          }
      });
      setLockedCells(newLocked);
      setSeed(newSeed);
  };

  const toggleLock = (index: number) => {
      const imgIdx = shuffledIndices[index]; if (imgIdx === undefined) return;
      const imgId = images[imgIdx]?.id; if (!imgId) return;
      setLockedCells(prev => {
          const next = new Map(prev);
          if (next.has(index)) next.delete(index);
          else next.set(index, imgId);
          return next;
      });
  };

  const updateCountSmart = (newValOrFn: number | ((prev: number) => number)) => {
    // The user is driving the count now — stop auto-following the upload total.
    ownCount(true);
    setCount(prev => {
      let candidate = typeof newValOrFn === 'function' ? newValOrFn(prev) : newValOrFn;
      if (candidate < 1) candidate = 1;
      if (layoutMode === 'balanced') {
        const W = 1000; const H = 1000 / aspect;
        const cols = Math.max(2, Math.ceil(Math.sqrt(candidate * (W/H))));
        const rows = Math.max(2, Math.ceil(candidate / cols));
        const snapped = cols * rows;
        if (snapped > candidate && candidate > prev) return snapped; 
        if (snapped < candidate && candidate < prev) return snapped;
        return snapped;
      }
      return candidate;
    });
  };

  const flashNotice = (msg: string) => {
      setNotice(msg);
      if (noticeTimer.current !== null) window.clearTimeout(noticeTimer.current);
      noticeTimer.current = window.setTimeout(() => setNotice(null), 4000);
  };
  useEffect(() => () => { if (noticeTimer.current !== null) window.clearTimeout(noticeTimer.current); }, []);

  // --- INGEST PROGRESS ------------------------------------------------------
  // Held in a ref as well as state because two selections can overlap: the
  // second must EXTEND the run in flight, not restart the bar at zero, and a
  // setState closure cannot see a total another call just raised.
  const ingestRef = useRef({ done: 0, total: 0, label: '', sub: 0 });
  const pushIngest = () => setIngest({ ...ingestRef.current });

  const beginIngest = (n: number, label: string) => {
    const r = ingestRef.current;
    if (r.total === 0) r.done = 0;
    r.total += n; r.label = label; r.sub = 0;
    pushIngest();
  };
  /** Mark `n` picked items finished. Clears the strip once the run drains. */
  const stepIngest = (n: number, label?: string) => {
    const r = ingestRef.current;
    if (r.total === 0) return;   // nothing in flight; never resurrect the strip
    r.done = Math.min(r.total, r.done + n);
    if (label !== undefined) r.label = label;
    r.sub = 0;
    if (r.total > 0 && r.done >= r.total) {
      r.done = 0; r.total = 0; r.label = ''; r.sub = 0;
      setIngest(null);
      return;
    }
    pushIngest();
  };
  /** Progress WITHIN the current item — only clips are slow enough to need it. */
  const subIngest = (ratio: number, label: string) => {
    const r = ingestRef.current;
    if (r.total === 0) return;
    r.sub = Math.max(0, Math.min(1, ratio)); r.label = label;
    pushIngest();
  };

  /** Resolves with the assets that actually landed — the caller needs to know
   *  whether anything decoded before it commits to keeping the source alive. */
  const handleUpload = async (files: File[], opts: UploadOptions = {}): Promise<ImageAsset[]> => {
    if (!files.length) return [];
    const noun = opts.noun || 'images';
    const prefix = opts.idPrefix || 'img';
    const track = opts.track !== false;
    const allNewAssets: ImageAsset[] = [];
    let totalR=0, totalG=0, totalB=0, colorCount=0;

    const decodeOne = async (file: File): Promise<ImageAsset | null> => {
        if (!file.type.startsWith('image/')) return null;
        const url = URL.createObjectURL(file);
        const img = await new Promise<HTMLImageElement>(r => {
            const el = new Image(); el.crossOrigin="anonymous";
            el.onload=()=>r(el); el.onerror=()=>r(el); el.src=url;
        });
        if(!img.width) { URL.revokeObjectURL(url); return null; }
        const analysis = await analyzeImage(img, globalModel);
        if(analysis.color) { totalR += analysis.color.r; totalG += analysis.color.g; totalB += analysis.color.b; colorCount++; }
        // NOTE: createThumbnail returns img.src unchanged when the image is
        // already <=1024px, so previewSrc may ALIAS src. Never revoke one
        // without checking the other.
        const thumbUrl = await createThumbnail(img);
        return {
            id: `${prefix}-${Date.now()}-${assetSeq++}`,
            src: url,
            previewSrc: thumbUrl,
            originalName: file.name,
            width: img.width,
            height: img.height,
            analysis,
            ...(opts.meta?.get(file) ?? {}),
        };
    };

    /**
     * PUT THIS BITE ON THE CANVAS NOW.
     *
     * The old code accumulated every asset and called setImages ONCE at the
     * end, which is why nothing appeared until everything had decoded. Staged
     * commits let the first pictures land while the rest are still decoding.
     *
     * The fragment count is NOT set here any more: the auto-follow effect above
     * derives it from the pool (one per uploaded photo/video), so this is a
     * plain concat and the React 18 StrictMode double-invoke is harmless.
     */
    const commit = (batch: ImageAsset[]) => {
        if (!batch.length) return;
        setImages(prev => [...prev, ...batch]);
    };

    try {
      let i = 0;
      let bite = FIRST_BITE;
      while (i < files.length) {
          const chunk = files.slice(i, i + bite);
          const results = (await Promise.all(chunk.map(decodeOne))).filter(Boolean) as ImageAsset[];
          allNewAssets.push(...results);
          commit(results);
          i += chunk.length;
          if (track) stepIngest(chunk.length, `Adding ${noun}…`);
          bite = BITE;
          // Yield the thread so React actually PAINTS what was just committed.
          // Without this the loop hogs the frame and the staged commits render
          // in one lump at the end — the exact behaviour being fixed.
          await nextFrame();
      }
      if(colorCount > 0) {
          const avg = { r: Math.round(totalR/colorCount), g: Math.round(totalG/colorCount), b: Math.round(totalB/colorCount) };
          setAvgColor(avg);
      }
      if (allNewAssets.length < files.length) {
          flashNotice(`${files.length - allNewAssets.length} file(s) could not be decoded and were skipped.`);
      }
    } catch (e) {
      console.error("Upload failed", e);
      flashNotice('Import failed — see console for details.');
      // The counter must not strand the strip on screen at 12/30 forever.
      if (track) stepIngest(Math.max(0, files.length - allNewAssets.length));
    } finally {
      // This drop is over, however it went. Bumping the marker retires any code
      // latch waiting on it, so the next import is a genuine late add again.
      setDropId(d => d + 1);
    }
    return allNewAssets;
  };

  /**
   * VIDEO INTAKE — a video becomes ONE looping cell. Nothing is asked.
   *
   * Loading a video means "put this clip in the collage and loop it" — the same
   * way a photo is one cell. It is NOT decomposed into a field of stills, and
   * there is no sheet, no slider and no setting standing between the file and
   * the collage. (Operator, three times: "just load the video"; "no more frame
   * picking"; "stop asking for frames period.")
   *
   * ONE poster raster comes back with the clip. It is not a still the user asked
   * for and it is never presented as one — it is what the STATIC exports
   * (JPEG/PNG/SVG) draw under the cell, and the fallback for a device that
   * cannot spare a decoder. `openClip` takes it in the same decoder pass that
   * reads the clip's shape, so the wait before the collage moves is a single
   * seek instead of a probe, a re-open, a prime and three seeks.
   */
  const autoIngestVideo = async (file: File) => {
      const shortName = file.name.length > 26 ? `${file.name.slice(0, 23)}…` : file.name;
      subIngest(0, `Loading ${shortName}…`);
      let poster: ExtractedFrame | null = null;
      try {
          const clip = await openClip(file, {
              maxDim: isMobile ? 1280 : 1600,
              onProgress: (r) => subIngest(r, `Loading ${shortName}…`),
          });
          poster = clip.poster;
          if (clip.error || clip.duration <= 0) {
              flashNotice(clip.error || `${file.name} could not be read.`);
              return;
          }
          if (clip.width <= 0 || clip.height <= 0) {
              flashNotice(`${file.name} has no visual track — it looks like audio only.`);
              return;
          }
          if (!clip.poster) {
              flashNotice(`${file.name} could not be read.`);
              return;
          }
          await handleVideoFrames([clip.poster], {
              file,
              name: file.name,
              duration: clip.duration,
              width: clip.width,
              height: clip.height,
          });
      } catch (e) {
          console.error('[video] import failed', e);
          flashNotice(isMobile
              ? `${file.name} could not be read. On iPhone, Photos exports are often HEVC — share it as “Most Compatible” (H.264) and retry.`
              : `${file.name} could not be read.`);
      } finally {
          // handleUpload minted its OWN URLs from the blob, so the intake's copy
          // is ours to give back however this went.
          revokeFrames(poster ? [poster] : null);
          // The clip is DONE as far as the batch is concerned, however it went.
          stepIngest(1);
      }
  };

  /**
   * Clips are worked through ONE AT A TIME — frame extraction drives a real
   * decoder and two at once thrash it — but the queue never blocks the thread
   * the pictures are landing on, and never blocks the UI.
   */
  const videoJobRef = useRef<Promise<void>>(Promise.resolve());

  /** Single intake for the picker AND drop. Pictures go in. Videos go in. There
   *  is no third case and nothing is asked. */
  const ingestFiles = (list: File[]) => {
      if (!list.length) return;
      // EXACTLY ONE BUCKET EACH. `isAudioFile` and `isVideoFile` are written to
      // be disjoint (the ambiguous containers — .mp4, .webm, .ogg — belong to
      // video), and the music filter runs first so the reject count below stays
      // the honest "none of the three".
      const music = list.filter(isAudioFile);
      const videos = list.filter(f => !isAudioFile(f) && isVideoFile(f));
      const pics = list.filter(f => !isAudioFile(f) && !isVideoFile(f) && f.type.startsWith('image/'));
      const rejected = list.length - videos.length - pics.length - music.length;

      const counted = pics.length + videos.length;
      if (counted > 0) beginIngest(counted, `Adding ${counted} item${counted === 1 ? '' : 's'}…`);

      // ONE TRACK. The last one picked wins, which is what "replace the music"
      // means, and the rest are named rather than silently dropped.
      if (music.length) {
          adoptSoundtrack(music[music.length - 1]);
          if (music.length > 1) flashNotice(`One music track at a time — using ${music[music.length - 1].name}.`);
      }
      if (pics.length) void handleUpload(pics);
      if (videos.length) {
          videoJobRef.current = videoJobRef.current
              .then(async () => { for (const v of videos) await autoIngestVideo(v); })
              .catch(() => { /* each clip already flashed its own notice */ });
      }
      if (rejected > 0) flashNotice(`${rejected} unsupported file(s) ignored — images, video and music only.`);
  };

  /**
   * ADOPT A MUSIC FILE — SYNCHRONOUSLY, then learn its length.
   *
   * The first cut awaited a metadata probe before calling `setSoundtrack`, and
   * that is a race with an obvious loser: pick a long track, then a short one
   * before the first probe returns, and the SHORT one lands first, the LONG
   * one's probe then overwrites it and REVOKES the url of the track actually on
   * screen. "The last file picked wins" quietly became "the fastest file to
   * report its own duration wins", and the other one's music went dead.
   *
   * Nothing about the render needs the duration (`lib/soundtrack.ts`,
   * DECISION 1 — the mixer takes its window from the DECODED buffer), so there
   * is nothing to wait for: adopt now, and let the probe fill in the label if
   * and when it arrives, and only if this is still the track it was probing.
   * A probe that never fires leaves a fully working soundtrack with no length
   * on its chip, which is the correct degradation.
   */
  const adoptSoundtrack = (file: File) => {
      const url = URL.createObjectURL(file);
      // Revoked HERE rather than inside the updater: a state updater must be a
      // pure function of `prev` (React may call it twice), and `handleClear`
      // already disposes clip urls this way.
      if (soundtrack?.url) URL.revokeObjectURL(soundtrack.url);
      setSoundtrack({ url, name: file.name, durationSec: 0, muted: false });
      // THE NOTICE MUST NOT NAME A CONTROL THAT IS NOT ON SCREEN. With no
      // photographs there is no stage, so there is no dock, no chip and no
      // speaker — the music is adopted and waits, and saying so is the honest
      // version of "press the speaker".
      flashNotice(images.length === 0
          ? `Music: ${file.name} — add photos and it goes under them.`
          : `Music: ${file.name} — press the speaker to hear it.`);

      try {
          const probe = document.createElement('audio');
          probe.preload = 'metadata';
          const land = (v: number) => {
              probe.onloadedmetadata = null; probe.onerror = null;
              // RELEASE THE DECODER. A probe left holding a src is a decoder per
              // adopted track, and picking a different song is a thing people do
              // ten times in a row. `removeAttribute` + `load()` is the release;
              // `src = ''` re-resolves against the document URL and fires a
              // spurious error instead.
              try { probe.removeAttribute('src'); probe.load(); } catch { /* ignore */ }
              if (!(v > 0)) return;
              setSoundtrack((prev) => (prev && prev.url === url ? { ...prev, durationSec: v } : prev));
          };
          probe.onloadedmetadata = () => land(Number.isFinite(probe.duration) ? probe.duration : 0);
          probe.onerror = () => land(0);
          probe.src = url;
      } catch { /* the chip simply shows no length */ }
  };

  const removeSoundtrack = () => {
      if (soundtrack?.url) URL.revokeObjectURL(soundtrack.url);
      setSoundtrack(null);
  };

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files ? Array.from(e.target.files) : [];
    e.target.value = '';
    ingestFiles(list);
  };

  /**
   * Poster(s) for a clip -> the SAME pool, the SAME analysis path. The default
   * intake hands exactly ONE poster; only the opt-in sheet hands several.
   *
   * The clip itself is kept alive: every poster is stamped with the `clipId` of
   * the video it came from, the binding the live compositor uses to loop the
   * moving clip where its still is sitting. A poster is a real asset — it shuffles
   * and locks and exports, and a device that cannot spare a decoder simply shows
   * it. The live clip is an ADDITION to the poster, never a replacement.
   */
  const handleVideoFrames = async (
      frames: ExtractedFrame[],
      source: { file: File; name: string; duration: number; width: number; height: number },
  ) => {
      if (!frames.length) return;
      const base = (source.name.replace(/\.[^.]+$/, '') || 'clip').slice(0, 40);

      // Minted HERE, not in the sheet: the sheet revokes everything it creates
      // when it unmounts, and it unmounts the instant this resolves.
      const clipId = `clip-${Date.now()}-${clipSeq++}`;
      const clipUrl = URL.createObjectURL(source.file);

      const meta = new Map<File, AssetProvenance>();
      const files = frames.map(f => {
          const stamp = formatTimecode(f.time).replace(/:/g, 'm');
          const file = new File([f.blob], `${base}_${String(f.index + 1).padStart(2, '0')}_${stamp}s.jpg`, { type: 'image/jpeg' });
          meta.set(file, { sourceKind: 'video', sourceName: source.name, sourceTime: f.time, clipId });
          return file;
      });
      // handleUpload mints its OWN object URLs from these blobs, so the sheet is
      // free to revoke the extraction URLs the moment this resolves.
      // track:false — the CLIP is the unit the user picked. Counting its frames
      // as separate items makes the batch counter lurch past its own total.
      const landed = await handleUpload(files, { idPrefix: 'vid', grow: true, meta, noun: 'frames', track: false });

      if (landed.length === 0) {
          // Nothing decoded, so nothing carries this clipId and no fragment could
          // ever show the clip. Keeping the URL would leak the whole file.
          URL.revokeObjectURL(clipUrl);
          return;
      }
      setClips(prev => [...prev, {
          id: clipId,
          url: clipUrl,
          name: source.name,
          width: source.width,
          height: source.height,
          durationSec: source.duration,
          frameCount: landed.length,
      }]);
  };

  /** Drop a clip back to stills: frees its decoder and its file, keeps its frames. */
  const removeClip = (id: string) => {
      setClips(prev => {
          const gone = prev.find(c => c.id === id);
          if (gone) { try { URL.revokeObjectURL(gone.url); } catch { /* already gone */ } }
          return prev.filter(c => c.id !== id);
      });
      // The stills stay in the pool and keep their provenance; only the live
      // binding is cut, so the fragments fall back to the extracted frame.
      setImages(prev => prev.map(img => img.clipId === id ? { ...img, clipId: undefined } : img));
  };

  // Last line of defence for the clip files, on UNMOUNT ONLY.
  //
  // It has to read through a ref: with `clips` in the dep list the cleanup would
  // run on every ADD as well, revoking the URL of every clip already playing the
  // moment a second one is imported. An empty dep list plus a mirror ref is the
  // only shape that frees everything exactly once, at the end.
  const clipsRef = useRef<LiveClip[]>([]);
  useEffect(() => { clipsRef.current = clips; }, [clips]);
  // The music file is the user's too, and it is held by exactly one url.
  const trackUrlRef = useRef<string>('');
  useEffect(() => { trackUrlRef.current = soundtrack?.url ?? ''; }, [soundtrack]);
  useEffect(() => () => {
      for (const c of clipsRef.current) { try { URL.revokeObjectURL(c.url); } catch { /* ignore */ } }
      if (trackUrlRef.current) { try { URL.revokeObjectURL(trackUrlRef.current); } catch { /* ignore */ } }
  }, []);

  // --- DRAG AND DROP (images AND video, same target) ---
  const onDragEnter = (e: React.DragEvent) => {
      if (!e.dataTransfer?.types?.includes('Files')) return;
      e.preventDefault();
      dragDepth.current += 1;
      setIsDragging(true);
  };
  const onDragOver = (e: React.DragEvent) => {
      if (!e.dataTransfer?.types?.includes('Files')) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = 'copy';
  };
  const onDragLeave = (e: React.DragEvent) => {
      if (!e.dataTransfer?.types?.includes('Files')) return;
      e.preventDefault();
      dragDepth.current = Math.max(0, dragDepth.current - 1);
      if (dragDepth.current === 0) setIsDragging(false);
  };
  const onDrop = (e: React.DragEvent) => {
      if (!e.dataTransfer?.types?.includes('Files')) return;
      e.preventDefault();
      dragDepth.current = 0;
      setIsDragging(false);
      // No busy-guard: a drop mid-import EXTENDS the run (beginIngest adds to
      // the total in flight) instead of being silently thrown away.
      ingestFiles(Array.from(e.dataTransfer.files || []));
  };

  const handleClear = () => {
      const state: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, density, countOwned, shuffle: shuffleTrigger, seed, aspect, gutter, entropy, arrangement, focus, twist, move }, style: { background: bgColor, look }, title: titleText ? { text: titleText, place: titlePlace, size: titleSize } : undefined };
      addToHistory(state, images, previewUrl || undefined);
      // Clearing the pool orphans every clip: nothing is left carrying a clipId,
      // so the files would sit in memory unreachable for the rest of the session.
      for (const c of clips) { try { URL.revokeObjectURL(c.url); } catch { /* ignore */ } }
      setClips([]); setStageOk(true);
      // The music is the user's file too, and its URL is owned here.
      removeSoundtrack();
      setImages([]); setPreviewUrl(null); setCount(0); setDensity(1); setLockedCells(new Map()); setAvgColor(null);
      ownCount(false); // a fresh import after Clear auto-follows the upload count again
  };

  const handleRestoreHistory = (item: HistoryItem) => {
      ownCount(true); // restoring a saved composition's own count
      setImages(item.images);
      const l = item.state.layout;
      setLayoutMode(l.mode); if(l.primitive) setPrimitive(l.primitive);
      setCount(l.count); setSeed(l.seed); setAspect(l.aspect); setGutter(l.gutter); setActiveTab(item.state.mode);
      if(l.entropy) setEntropy(l.entropy);
      // ALL THREE COMPOSITION CONTROLS RESTORE THE SAME WAY, and the way is
      // "absent means the default", never "absent means keep what is on screen".
      // Truthiness-guarding these (`if (l.focus) setFocus(l.focus)`) silently
      // half-restores a snapshot: reopen a project saved before crop focus
      // existed while Wander is selected and you get that project's fragments
      // with today's crop, which is a composition nobody ever saved.
      if(l.arrangement) setArrangement(l.arrangement);
      // A project saved before this cycle stored the old binary hue sort as a
      // 0..1 "resonance". `flow` is the CLOSEST arrangement in the roster, not an
      // exact restoration: the old sort zipped hue against plain reading order,
      // and `flow` runs it serpentine (every other row reversed). A resonance
      // project therefore reopens recognisable but not identical.
      else setArrangement((l.resonance ?? 0) > 0.1 ? 'flow' : 'natural');
      setFocus(l.focus ?? 'auto');
      setTwist(l.twist ?? 'none');
      setMove(l.move ?? 'still');
      if(item.state.style?.background) setBgColor(item.state.style.background);
      // ABSENT MEANS THE DEFAULT, never "keep what is on screen" — restoring a
      // snapshot that predates the title must not leave today's caption on it.
      setLook(item.state.style?.look ?? 'none');
      setTitleText(item.state.title?.text ?? '');
      setTitlePlace(item.state.title?.place ?? 'bl');
      setTitleSize(item.state.title?.size ?? 'md');
  };

  /**
   * ONE tier attempt, in the shape `runWithFallback` consumes.
   *
   * Everything that used to be able to hand the user a broken file now returns
   * a VERDICT instead: a dead surface says so (`surfaceLive: false`) and the
   * ladder steps down; a fragment that would not decode is COUNTED rather than
   * silently dropped. Nothing here decides policy — that is the ladder's job.
   */
  const renderAtSize = async (attempt: TierAttempt, ctl: AttemptControl): Promise<RenderOutcome> => {
      const { w, h } = attempt;

      // THE ALIGNMENT GUARD.
      //   `shuffledIndices` can carry an undefined slot whenever the fill bag
      //   comes up shorter than the layout (more cells than distinct sources).
      //   The old code did `orderedImages.map(img => ({ src: img.src, ... }))`
      //   with no guard, so that slot threw a TypeError *while building the
      //   worker message* — before either renderer's own null check could run.
      //   The throw was caught as "worker unavailable" and quietly re-rendered
      //   on the main thread at full export size. That is the out-of-bounds the
      //   report guessed at. Slots stay POSITIONAL (null, never dropped) because
      //   index i must keep addressing layoutItems[i].
      //
      //   AND IT READS `orderedAssets`, NOT THE RAW POOL. `orderedAssets` is the
      //   draw order WITH the crop focus applied (withFocus re-points
      //   `analysis.face`, which is the field the worker crops from). Re-deriving
      //   from `images` here — which is what this line used to do — silently
      //   exported every fragment at the historical face-else-energy anchor, so
      //   a user who picked Wander watched the preview re-frame and then
      //   downloaded a file cropped the old way. Exactly the shape of the
      //   already-scarred preview/export split, one field over.
      const rng = createRng(seed);
      const items = await computeLayout(w, h, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive, 0, aspect);
      //   AND THE TWIST IS RE-BAKED against THESE items, not the preview's.
      const ordered = retwistFor(orderedAssets.map(a => a ?? null), items, w, h);

      const worker = new RenderWorker();
      let settled = false;
      // Mandatory teardown: a timed-out worker must not keep its surface alive
      // while the next tier down tries to allocate one of its own.
      ctl.onAbort(() => {
          try { worker.postMessage({ cancel: 1 }); } catch { /* ignore */ }
          worker.terminate();
      });

      return await new Promise<RenderOutcome>((resolve, reject) => {
          worker.onmessage = (e: MessageEvent<any>) => {
              if (settled) return;
              settled = true;
              const d = e.data || {};
              worker.terminate();
              if (d.success) {
                  resolve({ blob: d.blob, surfaceLive: true, failedImages: d.failedImages ?? 0, drawn: d.drawn ?? 0 });
              } else if (d.surfaceLive === false) {
                  // A SIZE verdict. Report it; do not throw. The ladder steps down.
                  resolve({ blob: null, surfaceLive: false, failedImages: d.failedImages ?? 0, drawn: d.drawn ?? 0 });
              } else {
                  reject(new Error(d.error || 'render failed'));
              }
          };
          worker.onerror = (ev: ErrorEvent) => {
              if (settled) return;
              settled = true;
              worker.terminate();
              reject(new Error(ev.message || 'worker error'));
          };
          worker.postMessage({
              id: 1, width: w, height: h, mode: layoutMode, layoutItems: items,
              orderedImages: ordered.map(img => img ? ({
                  src: img.src,
                  // The preview's source, carried so a revoked or undecodable
                  // original degrades to a softer fragment instead of a hole.
                  fallbackSrc: img.previewSrc || img.src,
                  width: img.width, height: img.height, analysis: img.analysis,
              }) : null),
              zoom, bgColor, titlePlan, look,
          });
      });
  };

  /**
   * Export at the best size that is PROVABLY good, starting from what was asked.
   *
   * The old loop tried a hardcoded tier list, accepted whatever came back, and
   * had no way to notice a black file. This walks a ladder derived from a real
   * measurement of THIS device, validates every blob before accepting it, and
   * returns a reason when it cannot.
   */
  const exportWithLadder = async (preferred: number | null): Promise<FallbackResult> => {
      const limits = await probeMaxCanvas();
      // Honour the user's pick as the top rung, then fall back down the derived
      // ladder. A pick above what the device can do is not an error — it is just
      // the first rung that gets rejected. (Pure + swept in exportLimits.selfTest.)
      const tiers = composeTiers(preferred, deriveTiers(limits, aspect));

      return runWithFallback(renderAtSize, {
          aspect,
          tiers,
          limits,
          fragments: effectiveCount,
          onProgress: (a) => setExportMsg(
              a.total > 1 && a.index > 0 ? `${a.tier}px (retry ${a.index + 1}/${a.total})…` : `${a.tier}px Rendering…`
          ),
      });
  };

  /** Kept for callers that just want pixels or nothing (Share). Throws with the
   *  ladder's own explanation rather than a bare "Blob failed". */
  const generateBlob = async (widthPx: number): Promise<Blob> => {
      const r = await exportWithLadder(widthPx);
      if (!r.ok || !r.blob) throw new Error(r.log);
      console.info(r.log);
      return r.blob;
  };

  const onBlobReady = (blob: Blob) => {
      const url = URL.createObjectURL(blob);
      setResultBlobUrl(url); 
      setExportStatus('done'); setTimeout(() => setExportStatus('idle'), 3000);
  };

  /**
   * Why a failed export now SAYS something.
   *
   * The old path set status 'error' and left the user staring at a word. Worse,
   * the common case never reached it at all: the file came back black and got
   * handed over as a success. Every branch below is a distinct, actionable
   * thing that actually went wrong.
   */
  const explainExportFailure = (r: FallbackResult): string => {
      if (r.reason === 'decode-failure') {
          const n = r.attempts[r.attempts.length - 1]?.detail || 'some fragments';
          return `Couldn't read ${n}. Re-add those images and try again.`;
      }
      if (r.reason === 'no-tiers') return "This device won't give us a canvas. Try a smaller size.";
      const smallest = r.attempts[r.attempts.length - 1]?.tier;
      return smallest
          ? `Too big for this device — ${smallest}px failed too. Close other tabs and retry.`
          : 'Export failed.';
  };

  const runExport = async (preferred: number | null) => {
      setShowExportDialog(false);
      // CHECKPOINT BEFORE THE CLIFF. A still export at MAX allocates a canvas 4×
      // larger; flush the pre-export state NOW so an OOM reload mid-render still
      // has "what I was doing" durable. Fire-and-forget — it only zips images.
      void flushSession();
      setExportStatus('processing');
      setExportMsg(preferred ? `${preferred}px Rendering…` : 'Finding your device’s limit…');
      await new Promise(r => setTimeout(r, 60)); // let the spinner paint before we block
      try {
          const r = await exportWithLadder(preferred);
          // The whole point: a run that is not PROVEN good never reaches the user.
          if (!r.ok || !r.blob) {
              console.warn(r.log);
              setExportMsg(explainExportFailure(r));
              setExportStatus('error');
              return;
          }
          console.info(r.log);
          if (r.warnings.length) console.warn('export warnings:', r.warnings.join('; '));
          onBlobReady(r.blob);
      } catch (e) {
          console.warn('Export failed', e);
          setExportMsg('Export failed. Try a smaller size.');
          setExportStatus('error');
      }
  };

  const handleExport = async (size: number) => {
      // MAX asks the ladder to start from the measured ceiling instead of a
      // number someone typed in 2026 — `deriveTiers` already knows what fits.
      await runExport(size === 30000 ? null : size);
  };

  const handleMaxRezzy = async () => { await runExport(null); };

  const handleShare = async () => {
      setShowExportDialog(false); setExportStatus('processing');
      try {
          const blob = await generateBlob(4096);
          const file = new File([blob], 'collage.jpg', { type: 'image/jpeg' });
          if (navigator.canShare && navigator.canShare({ files: [file] })) {
              await navigator.share({ files: [file], title: 'GenArt', text: 'Collage' });
              setExportStatus('done');
          } else { onBlobReady(blob); }
          setTimeout(() => setExportStatus('idle'), 3000);
      } catch (e) { setExportStatus('error'); }
  };

  const handleShareResult = async () => {
      if (!resultBlobUrl || !navigator.canShare) return;
      try {
          const res = await fetch(resultBlobUrl);
          const blob = await res.blob();
          const file = new File([blob], 'collage.jpg', { type: 'image/jpeg' });
          await navigator.share({ files: [file], title: 'GenArt', text: 'Collage' });
      } catch (e) { console.error(e); }
  };

  /**
   * RE-BAKE THE TWIST AGAINST THE LAYOUT THAT IS ACTUALLY BEING DRAWN.
   *
   * A twist angle is a FIELD over the canvas — `pinwheel` and `cascade` are
   * functions of WHERE the fragment sits. The preview memo bakes them against
   * the preview layout (PREVIEW_W), but every export recomputes its OWN layout
   * at its own width (renderAtSize at the tier size, handleExportSVG at a
   * hardcoded 1000px), and `computeLayout` is NOT scale-invariant: generateRects
   * floors each split, so a near-tie in its argmax can flip at a different
   * width. Measured on the shipped generator: 11.3% of seeds at count=24 and
   * 27.7% at count=40 produce a genuinely DIFFERENT partition, in which slot i
   * addresses a different rectangle entirely.
   *
   * That divergence is older and bigger than twist — it re-pairs the
   * photographs too, because `arrangeBag` ranks against the same preview cells —
   * and fixing it belongs in the layout, not here (see the book's scars). What
   * this does is stop twist ADDING to it: the angle is recomputed from the
   * geometry being rendered, so each output is at least internally honest —
   * every fragment leans according to where it actually ended up.
   *
   * Writes the angle unconditionally rather than going through `withTwist`,
   * which short-circuits on a zero angle and would leave the preview's stale
   * value in place on exactly the fragments whose field evaluates to zero.
   */
  const retwistFor = (
    assets: (ImageAsset | null)[],
    items: LayoutItem[],
    W: number,
    H: number,
  ): (ImageAsset | null)[] => {
    if (twist === 'none') return assets;
    return assets.map((a, slot) => {
      if (!a) return a;
      const b = items[slot]?.bounds;
      const cell = b && b.w > 0 && b.h > 0
        ? { cx: (b.x + b.w / 2) / W, cy: (b.y + b.h / 2) / H, area: (b.w * b.h) / (W * H) }
        : null;
      const angle = twistAngle(twist, (seed ^ (slot * 2654435761)) | 0, cell);
      return { ...a, analysis: { ...(a.analysis ?? {}), twist: angle } } as ImageAsset;
    });
  };

  const handleDownloadResult = () => {
      if (!resultBlobUrl) return;
      const a = document.createElement('a'); a.href = resultBlobUrl; a.download = `GENART-${Date.now()}.jpg`; a.click();
  };

  const handleExportSVG = async () => {
    setShowExportDialog(false); setExportStatus('processing'); setExportMsg('VECTORIZING...');
    try {
        const rng = createRng(seed); const items = await computeLayout(1000, 1000/aspect, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive, 0, aspect);
        // `orderedAssets`, not the raw pool — the SVG crops from `analysis`, and
        // that is where the crop focus lives (see renderAtSize above).
        const orderedImages = retwistFor(orderedAssets.map(a => a ?? null), items, 1000, 1000 / aspect);
        const stateForSave: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, density, countOwned, shuffle: shuffleTrigger, seed, aspect, gutter, entropy, arrangement, focus, twist, move }, style: { background: bgColor, look }, title: titleText ? { text: titleText, place: titlePlace, size: titleSize } : undefined };
        // `images` — the raw SOURCE POOL, last. Not `orderedImages`: that is the
        // drawn permutation with focus and twist already baked into each
        // analysis, and both are re-derived from focus/twist/seed on open. The
        // SVG is the project file, so it carries the pool that made it.
        const svgContent = await generateVectorExport(1000, aspect, layoutMode, items, orderedImages, seed, stateForSave, zoom, bgColor, titlePlan, look, images);
        const blob = new Blob([svgContent], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `GENART-VECTOR-${seed}.svg`; a.click(); URL.revokeObjectURL(url);
        setExportStatus('done'); setTimeout(() => setExportStatus('idle'), 2000);
    } catch (e) { setExportStatus('error'); }
  };

  // THE ONE `AppState` BUILDER. Save (download), autosave (crash-safe session)
  // and Clear (history) each described the project by writing this same literal
  // inline — three chances to drift, and the manifest is exactly where a silent
  // field-omission becomes a wrong answer on reopen. One source of truth now.
  const buildStateForSave = (): AppState => ({ version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, density, countOwned, shuffle: shuffleTrigger, seed, aspect, gutter, entropy, arrangement, focus, twist, move }, style: { background: bgColor, look }, title: titleText ? { text: titleText, place: titlePlace, size: titleSize } : undefined });

  const handleSaveProject = async () => { setShowExportDialog(false); await saveProject(buildStateForSave(), images); dirtyRef.current = false; };

  // Write the working project to IndexedDB — the crash-safe snapshot behind the
  // well bug ("capturing at 4k ... lost what I was doing"). Cheap (the archive
  // never carries video bytes) and silent (insurance, not a feature): a failed
  // write just leaves the previous snapshot standing.
  const flushSession = async () => {
    if (images.length === 0) return;
    try {
      const blob = await buildProjectBlob(buildStateForSave(), images);
      await sessionStore.putSession(blob, images.length);
    } catch { /* best-effort; never surface */ }
  };

  // APPLY A LOADED PROJECT — the single hydration path shared by Open (a file
  // the user picked) and Restore (the crash-safe session). It used to live only
  // inside `handleLoadProject`; the whole class of "the path that forgot it"
  // bugs the comments below guard against is exactly what a second, hand-copied
  // apply path would reintroduce, so Restore reuses THIS one verbatim.
  const applyLoadedProject = (loaded: { state: AppState; images: ImageAsset[] }) => {
        setOpenError(null);
        // `??`, NOT `||`, on every number here. `||` treats a legal ZERO as
        // absent, and three of these have a meaningful zero: seed 0 became
        // `Date.now()` (a different collage every time you opened the same
        // file), gutter 0 became 0.005 (fragments that touched grew a hairline),
        // entropy 0 was skipped entirely and kept whatever was on screen. Same
        // family as the `Math.max(0, indexOf(x))` scar: a plausible neighbour
        // substituted for information that was actually there.
        const num = (v: unknown, d: number) => (typeof v === 'number' && Number.isFinite(v) ? v : d);
        // LATCH THE COUNT. `setImages` below replaces the pool wholesale, and the
        // grow-to-cover effect reads any pool bigger than the count as a late ADD
        // — so a project saved with FOUR fragments and FIVE photographs reopened
        // with five, silently, and re-exported as a different collage. This is
        // the same latch the composition code uses (see applyCompositionCode) and
        // the same rule: only an OWNED count is protected, because a derived one
        // is a default and the pool it lands next to is a better one.
        const ld = loaded.state.layout;
        const ldOwned = ld.countOwned ?? true;
        if(ldOwned) pendingCountRef.current = { count: num(ld.count, 12), drop: dropId };
        ownCount(ldOwned); setImages(loaded.images); const l = loaded.state.layout; setLayoutMode(l.mode || 'minimal'); setCount(num(l.count, 12)); setDensity(num(l.density, 1)); setShuffleTrigger(num(l.shuffle, 0)); setSeed(num(l.seed, Date.now())); setAspect(num(l.aspect, ASPECT_ROSTER[1])); setGutter(num(l.gutter, 0.005)); setEntropy(num(l.entropy, entropy)); if(l.primitive) setPrimitive(l.primitive); if(loaded.state.style?.background) setBgColor(loaded.state.style.background); setLook(loaded.state.style?.look ?? 'none'); if(l.arrangement) setArrangement(l.arrangement); else setArrangement((l.resonance ?? 0) > 0.1 ? 'flow' : 'natural'); setFocus(l.focus ?? 'auto'); setTwist(l.twist ?? 'none'); setMove(l.move ?? 'still'); setTitleText(loaded.state.title?.text ?? ''); setTitlePlace(loaded.state.title?.place ?? 'bl'); setTitleSize(loaded.state.title?.size ?? 'md');
          // THE TAB IS PART OF THE STATE, and it was WRITTEN and never read.
          // `stateForSave` has always put `mode: activeTab` in the manifest, so an
          // export taken with Settings open said "advanced" and reopening left the
          // app on Layout — which then re-exported "simple" and broke the
          // byte-identical guarantee outright. `handleRestoreHistory` already got
          // this right; this is the same restore, in the path that forgot it.
          if(loaded.state.mode) setActiveTab(loaded.state.mode);
          // WHAT THE OLD POOL LEAVES BEHIND. `setImages` above replaces the pool
          // wholesale, exactly as `handleClear` does — and `handleClear` is the
          // one that documents why that orphans things. Nothing in the new pool
          // can carry a `clipId` (`metaForAsset` keeps id/name/analysis and the
          // video bytes are not in an SVG at all), so a surviving clip is
          // unreachable for the rest of the session while the dock and live mode
          // both keep rendering off `clips.length > 0`. Pinned cells refer to a
          // layout being replaced and the recipe name to a roll this project did
          // not make — the same reasoning `applyCompositionCode` uses.
          for (const c of clips) { try { URL.revokeObjectURL(c.url); } catch { /* ignore */ } }
          setClips([]); setStageOk(true); setLockedCells(new Map()); setLastRecipe(undefined);
          // RETIRE THE LATCH WITH THE LOAD THAT ARMED IT. Nothing else bumps
          // `dropId` here, so the latch stayed live past the Open and the NEXT
          // import paid for it: its final effect pass took the `drop !== dropId`
          // branch, cleared the latch and returned WITHOUT ever reaching
          // grow-to-cover — so the first photos added after opening a project got
          // no fragment, once, silently. `handleUpload`'s `finally` bumps this for
          // exactly the same reason ("the next import is a genuine late add
          // again"); opening a file is a drop too. Both effect passes return
          // before `setCount`, so the loaded count is protected either way,
          // batched or not.
          setDropId(d => d + 1);
  };

  const handleLoadProject = () => {
    const input = document.createElement('input'); input.type = 'file'; input.accept = '.collage,.svg';
    input.onchange = async (e:any) => {
        const file = e.target.files[0]; if(!file) return;
        const loaded = await loadProject(file);
        // A refused file used to do NOTHING — no picture, no message, no way to
        // tell a rejected file from a slow one. `loadProject` fails closed by
        // design (see loadFromSVG), so the refusal has to be visible, and it
        // belongs on the button that was pressed.
        if(!loaded) {
          setOpenError("COULDN'T OPEN THAT FILE");
          flashNotice("COULDN'T OPEN THAT FILE — it must be a .collage archive, or an SVG exported by this app. SVGs exported before 2026-08-08 carry no image identity and cannot be reopened.");
          setTimeout(() => setOpenError(null), 6000);
          return;
        }
        applyLoadedProject(loaded);
    };
    input.click();
  };

  // RESTORE THE CRASH-SAFE SESSION. The stored `.collage` blob is fed through the
  // exact `loadProject` round-trip a picked file uses, then the shared apply
  // path — one format, one hydration, no drift.
  const handleRestoreSession = async () => {
    setRestorePrompt(null);
    const blob = await sessionStore.getSessionBlob();
    if (!blob) { flashNotice('That session could not be read — starting fresh.'); return; }
    // `loadProject` reads `file.name`; a bare Blob has none, so wrap it. The name
    // must not end in `.svg`, or it takes the SVG branch and fails.
    const file = new File([blob], 'session.collage', { type: 'application/zip' });
    const loaded = await loadProject(file);
    if (!loaded) { flashNotice('That session could not be restored.'); return; }
    applyLoadedProject(loaded);
    flashNotice('Restored your last session.');
  };

  const handleDismissRestore = async () => {
    setRestorePrompt(null);
    dirtyRef.current = false;
    await sessionStore.clearSession();
  };

  const handleApplyTemplate = (t: Template) => {
      ownCount(true); // a template carries its own explicit fragment count
      setLayoutMode(t.layout.mode); setCount(t.layout.count); setSeed(t.layout.seed); setAspect(t.layout.aspect); setGutter(t.layout.gutter);
  };

  // CRASH-SAFE AUTOSAVE. A debounced snapshot of the working project to
  // IndexedDB, so the next OOM reload / accidental refresh during a heavy 4K
  // capture no longer takes the whole collage with it. `canAutosave` (unit-swept)
  // is the chokepoint: never into an empty pool, never DURING an export or
  // capture (the memory cliff we are fixing), never over a session a restore
  // banner is about to bring back. Every field `buildStateForSave` serialises is
  // a dep, so each run re-schedules with the latest state; the timer replaces the
  // previous one, which is the debounce.
  useEffect(() => {
    const exporting = exportStatus === 'processing' || !!recorderRef.current?.isRecording;
    if (!canAutosave({ imageCount: images.length, isExporting: exporting, isRestoring: !!restorePrompt })) return;
    dirtyRef.current = true; // there is now work that isn't on disk
    const t = window.setTimeout(() => { void flushSession(); }, AUTOSAVE_DEBOUNCE_MS);
    return () => window.clearTimeout(t);
  }, [images, layoutMode, primitive, count, density, countOwned, shuffleTrigger, seed, aspect, gutter, entropy, bgColor, look, arrangement, focus, twist, move, titleText, titlePlace, titleSize, activeTab, soundtrack, exportStatus, restorePrompt]);

  // OFFER TO RESTORE, once, at launch. Only the metadata is read here — the
  // (large) blob is pulled only if the user actually taps Restore. The banner's
  // render is additionally gated on an empty pool (shouldPromptRestore), so a
  // deep-link or Open that populates the pool first silently wins.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const meta = await sessionStore.getSessionMeta();
      if (!cancelled && meta) setRestorePrompt(meta);
    })();
    return () => { cancelled = true; };
  }, []);

  // If the user ignores the banner and just starts working, that IS a decision:
  // dismiss the offer so autosave unfreezes and protects the NEW work. The old
  // snapshot is then overwritten by the first save of the new project — the user
  // saw "restore?" and chose to build instead.
  useEffect(() => {
    if (restorePrompt && images.length > 0) setRestorePrompt(null);
  }, [images.length, restorePrompt]);

  // Belt-and-suspenders for the SOFT reload — an accidental refresh, a back
  // gesture, a tab close — where the browser lets us warn first. A hard OOM kill
  // never fires this; that path is what the IndexedDB autosave covers.
  useEffect(() => {
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedWork(images.length, dirtyRef.current)) { e.preventDefault(); e.returnValue = ''; }
    };
    window.addEventListener('beforeunload', onBeforeUnload);
    return () => window.removeEventListener('beforeunload', onBeforeUnload);
  }, [images.length]);

  return (
    <div className="fixed inset-0 bg-black text-white font-sans flex flex-col select-none overflow-hidden">
      {/* `display: contents` so the wrapper is invisible to the flex column,
          `none` so maximizing costs the header its space WITHOUT unmounting it
          (it owns the export shortcut, and a remount would drop it). */}
      <div style={{ display: maximized ? 'none' : 'contents' }}>
        <Header aiState={aiState} exportStatus={exportStatus} exportMsg={exportMsg} onExport={() => setShowExportDialog(true)} hasImages={images.length > 0} onSaveProject={handleSaveProject} onLoadProject={handleLoadProject} openError={openError} />
      </div>
      {/* Leaving full bleed BEFORE the take starts: the Stop button and the
          recording indicator both live in the dock that full bleed hides, and
          Cmd-E still reaches this dialog while maximized because the Header
          stays mounted under `display:none`. */}
      <ExportDialog canExportVideo={liveMode} onExportVideo={(secs, w) => { setMaximized(false); void flushSession(); recorderRef.current?.start(secs, w); }} videoMaxSeconds={recorderRef.current?.maxSeconds ?? 30} videoSizes={recorderRef.current?.sizes ?? []} canChooseVideoSize={!!recorderRef.current?.canChooseSize} isOpen={showExportDialog} onClose={() => setShowExportDialog(false)} onExport={handleExport} onExportSVG={handleExportSVG} onExportProject={handleSaveProject} canShare={!!navigator.share} onShare={handleShare} />
      <ResultModal isOpen={!!resultBlobUrl} onClose={() => setResultBlobUrl(null)} blobUrl={resultBlobUrl} onShare={handleShareResult} onDownload={handleDownloadResult} isMobile={isMobile} />

      <div
        className="flex-1 relative bg-[#050505] flex items-center justify-center overflow-hidden"
        onDragEnter={onDragEnter} onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}
      >
         <div className="absolute inset-0 opacity-[0.05] pointer-events-none z-0" style={{ backgroundImage: 'linear-gradient(#444 1px, transparent 1px), linear-gradient(90deg, #444 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
         {/* WHAT IS STILL LANDING. A strip, not a curtain: the collage behind it
             is filling in as this counts up, and covering that with a black
             overlay is what made a working import look like a frozen app. */}
         {ingest && ingest.total > 0 && (
           <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[120] w-[min(21rem,90vw)] pointer-events-none animate-in fade-in slide-in-from-top-2 duration-200">
             <div className="rounded-xl bg-[#0d0d0d]/95 border border-white/10 shadow-2xl backdrop-blur px-3 py-2">
               <div className="flex items-center gap-2">
                 <Activity size={12} className="animate-spin text-emerald-400 shrink-0" />
                 <span className="flex-1 min-w-0 truncate text-[9px] font-bold tracking-[0.16em] text-white uppercase">{ingest.label}</span>
                 <span className="shrink-0 text-[10px] font-black tabular-nums text-emerald-400">{ingest.done}/{ingest.total}</span>
               </div>
               <div className="mt-1.5 h-1 rounded-full bg-white/10 overflow-hidden">
                 <div
                   className="h-full bg-emerald-500 transition-[width] duration-200"
                   style={{ width: `${Math.max(3, Math.round(((ingest.done + ingest.sub) / ingest.total) * 100))}%` }}
                 />
               </div>
             </div>
           </div>
         )}
         {/* Layout recompute now fires once per COMMITTED BITE, so it can no
             longer be a full-screen flash — that would strobe the canvas black
             for the whole import. */}
         {isLayoutComputing && !ingest && (
           <div className="absolute bottom-3 right-3 z-[110] pointer-events-none flex items-center gap-1.5 px-2 py-1 rounded-lg bg-black/70 border border-white/10">
             <Activity size={10} className="animate-spin text-emerald-400" />
             <span className="text-[8px] font-bold tracking-[0.18em] text-gray-400 uppercase">Layout</span>
           </div>
         )}
         {isDragging && (
            <div className="absolute inset-3 z-[150] pointer-events-none rounded-2xl border-2 border-dashed border-emerald-500/70 bg-emerald-500/5 flex flex-col items-center justify-center gap-2">
               <Film size={26} className="text-emerald-400" />
               <span className="text-[10px] font-black tracking-[0.2em] text-white uppercase">Drop images, video or music</span>
            </div>
         )}
         {images.length === 0 ? (
            <div onClick={() => fileInputRef.current?.click()} className="relative z-10 group flex flex-col items-center justify-center p-10 border border-dashed rounded-full border-gray-800 cursor-pointer hover:border-emerald-500/50 hover:bg-white/5 active:scale-95 transition-all">
               <div className="flex items-center gap-2 mb-3 text-gray-600 group-hover:text-emerald-500 transition-colors">
                  <Upload size={26} />
                  <Film size={26} />
               </div>
               <span className="text-[9px] font-bold tracking-widest text-gray-500 group-hover:text-white">LOAD SOURCE</span>
               <span className="text-[8px] tracking-widest text-gray-700 mt-1 uppercase">Images or video</span>
            </div>
         ) : (
            <div className={`relative z-10 w-full h-full flex justify-center ${railRow && !maximized ? 'items-end' : 'items-center'} ${maximized ? 'p-1 sm:p-2' : 'p-2 sm:p-4'}`} ref={setBandEl}>
               {/* `items-end` under a laid-across rail: the fit already gave the
                   rail its 68px, and centring the remainder would put half of
                   that slack back ABOVE the artwork, under the buttons. */}
               {/* Measured pixels once the band is known; the old content-sized
                   style stays as the first-paint fallback. */}
               <div
                 className="relative shadow-2xl"
                 // maxWidth/maxHeight stay ON TOP of the measured pixels: a
                 // ResizeObserver is a frame behind layout, and without the CSS
                 // clamp the frame keeps its old size for that frame and
                 // overshoots a shrinking band into an overflow-hidden parent.
                 style={artFit
                   ? { width: artFit.w, height: artFit.h, maxWidth: '100%', maxHeight: '100%' }
                   : { aspectRatio: aspect, maxHeight: '100%', maxWidth: '100%' }}
               >
                   {liveMode ? (
                     // Same composition, same 1200-space, same smart crops — but
                     // the video fragments keep moving and the whole surface can
                     // be recorded. The lock overlay below is unchanged because
                     // the Stage paints into the identical coordinate system.
                     <VideoStage
                       layoutItems={layoutItems}
                       orderedAssets={orderedAssets}
                       clips={clips}
                       mode={layoutMode}
                       aspect={aspect}
                       zoom={zoom}
                       bgColor={bgColor}
                       titlePlan={titlePlan}
                       look={look}
                       onNotice={flashNotice}
                       onUnavailable={() => setStageOk(false)}
                       controlsHost={stageControlsHost}
                       onRemoveClip={removeClip}
                       recorderRef={recorderRef}
                       poolAssets={images}
                       soundtrack={soundtrack}
                       onRemoveSoundtrack={removeSoundtrack}
                       onSoundtrackMuted={(muted) => setSoundtrack((prev) => (prev ? { ...prev, muted } : prev))}
                     />
                   ) : (
                     previewUrl && <img src={previewUrl} className="w-full h-full object-contain pointer-events-none" />
                   )}
                   {/* Lock overlay. Stays click-through-able (each <g> is the
                       hit target); the Stage transport sits at z-40 so it wins
                       the clicks that land on it. */}
                   <svg className="absolute inset-0 w-full h-full" viewBox={`0 0 ${PREVIEW_W} ${PREVIEW_H(aspect, PREVIEW_W)}`}>
                       {layoutItems.map((item, i) => {
                           const isLocked = lockedCells.has(i); const d = item.path.map((p: Point, idx: number) => `${idx===0?'M':'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
                           return (
                               <g key={i} onClick={() => toggleLock(i)} className="group cursor-pointer">
                                   <path d={d} fill="transparent" stroke="transparent" />
                                   <path d={d} fill="none" stroke={isLocked ? '#facc15' : 'white'} strokeWidth={isLocked ? 4 : 2} className={`transition-all ${isLocked ? 'opacity-100' : 'opacity-0 group-hover:opacity-30'}`} />
                                   {isLocked && (() => { const c = getCentroid(item.path); return ( <foreignObject x={c.x - 12} y={c.y - 12} width="24" height="24"><div className="bg-black/50 p-1 rounded-full backdrop-blur flex items-center justify-center w-full h-full"><Lock size={12} className="text-yellow-400" /></div></foreignObject> ); })()}
                               </g>
                           );
                       })}
                   </svg>
               </div>
               {/* FULL BLEED: art, and one thumb-reachable bar. The three
                   buttons here are the ones you are maximized IN ORDER to use —
                   the operator maximizes to compare LAYOUTS, so rolling,
                   reshuffling and remixing have to work without dropping back
                   out to the dock every time. */}
               {maximized && (
                 // pb-safe: maximized hides the Header (pt-safe) and the dock
                 // (pb-safe), so nothing else in the app honours the inset in
                 // this state — and Exit is the only way out on a touch device,
                 // which put it under the iOS home indicator.
                 // `max(...)`, not the pb-safe utility: --safe-b is 0px on every
                 // desktop, and the utility would win the cascade and take the
                 // pill's own 12px of air with it.
                 <div
                   className="absolute inset-x-0 bottom-0 z-[130] flex justify-center px-3 pointer-events-none"
                   style={{ paddingBottom: 'max(0.75rem, var(--safe-b))' }}
                 >
                   <div className="pointer-events-auto flex items-center gap-1 rounded-2xl border border-white/15 bg-black/70 backdrop-blur px-1.5 py-1.5 shadow-2xl">
                     <button onClick={handleDice} title="Roll the dice" aria-label="Roll the dice" className="w-11 h-11 rounded-xl text-emerald-400 flex items-center justify-center hover:bg-white/10 active:scale-95 transition"><Dices size={19} /></button>
                     <button onClick={handleShuffle} title="Shuffle images" aria-label="Shuffle images" className="w-11 h-11 rounded-xl text-gray-200 flex items-center justify-center hover:bg-white/10 active:scale-95 transition"><Shuffle size={18} /></button>
                     <button onClick={handleRemix} title="Remix shapes" aria-label="Remix shapes" className="w-11 h-11 rounded-xl text-gray-200 flex items-center justify-center hover:bg-white/10 active:scale-95 transition"><RefreshCw size={18} /></button>
                     <span className="mx-0.5 h-6 w-px bg-white/15" aria-hidden="true" />
                     <button ref={exitBtnRef} onClick={() => setMaximized(false)} title="Exit full bleed (Esc)" aria-label="Exit full bleed" className="w-11 h-11 rounded-xl text-white bg-white/10 flex items-center justify-center hover:bg-white/20 active:scale-95 transition"><Minimize2 size={18} /></button>
                   </div>
                 </div>
               )}

               {!maximized && (
               <div className={`absolute top-4 right-4 flex gap-2 ${railRow ? 'flex-row' : 'flex-col'}`}>
                   <button
                     ref={maxBtnRef}
                     onClick={() => { if (!recorderRef.current?.isRecording) setMaximized(true); }}
                     title="Maximize the shot (F)"
                     aria-label="Maximize the shot"
                     className="w-11 h-11 rounded bg-[#111] text-white border border-gray-800 flex items-center justify-center hover:bg-white/10 transition-colors shadow-lg"
                   ><Maximize2 size={18} /></button>
                   <button
                     onClick={() => fileInputRef.current?.click()}
                     title="Add more images or video"
                     aria-label="Add more images or video"
                     className="w-11 h-11 rounded bg-[#111] text-gray-300 border border-gray-800 flex items-center justify-center hover:bg-white/10 hover:text-white transition-colors shadow-lg"
                   ><Plus size={18} /></button>
                   <button
                     onClick={() => videoInputRef.current?.click()}
                     title="Add a video — it loads and loops"
                     aria-label="Add a video"
                     className="w-11 h-11 rounded bg-[#111] text-emerald-400 border border-gray-800 flex items-center justify-center hover:bg-emerald-500/15 transition-colors shadow-lg"
                   ><Film size={18} /></button>
                   <button
                     onClick={() => musicInputRef.current?.click()}
                     title={soundtrack ? `Music: ${soundtrack.name} — pick another to replace it` : 'Add music — it plays under the collage and lands in the export'}
                     aria-label={soundtrack ? 'Replace the music' : 'Add music'}
                     className={`w-11 h-11 rounded bg-[#111] border flex items-center justify-center transition-colors shadow-lg ${
                       soundtrack
                         ? 'text-emerald-400 border-emerald-500/40 hover:bg-emerald-500/15'
                         : 'text-gray-300 border-gray-800 hover:bg-white/10 hover:text-white'
                     }`}
                   ><Music size={18} /></button>
                   <button onClick={handleClear} title="Clear all" aria-label="Clear all" className="w-11 h-11 rounded bg-[#111] text-red-500 border border-gray-800 flex items-center justify-center hover:bg-red-900/30 transition-colors shadow-lg"><X size={18} /></button>
               </div>
               )}

            </div>
         )}
      </div>

      {/* THE DOCK GIVES BACK ITS HEIGHT THROUGH THE SCROLLER IT ALREADY HAS.
          It grew with every panel added and the stage got the leftovers — down
          to 52px on a 320px phone. The first attempt wrapped the whole dock in a
          SECOND capped scroller, and an adversarial audit caught what that costs:
          `.ui-dock` is already a capped scroller (`--dock-max`) whose primary
          action bar — the fragment count, Shuffle, Remix — is `position: sticky`
          against ITS bottom. Nesting a second scroller pinned that bar to the
          bottom of an inner box pushed below the outer scrollport, and the most
          used controls in the app went off-screen (measured: 778..832 in a
          844px viewport, to 869..923). So the cap moved to `--dock-max` itself,
          where there is exactly one scroller and the sticky bar stays in it.
          `display:none` (not an unmount) hides the dock when maximized, so the
          Stage's portal host survives. */}
      <div
        style={{ display: maximized ? 'none' : undefined }}
        className="bg-[#0a0a0a] border-t border-white/10 pb-safe z-50 relative shrink-0"
      >
         {/* VIDEO DOCK — everything the live stage needs to say or be driven by,
             OUTSIDE the canvas. This used to float over the collage; chrome on
             top of the artwork covers the thing the user is here to look at. */}
         {/* THE BAR EXISTS TO HOST THE STAGE'S PORTAL, so its condition is
             "is the Stage mounted" — which is `liveMode`, not a guess at what
             the Stage would contain. Gated on `clips.length > 0` it rendered
             13px of empty chrome whenever a source existed but the Stage did
             not: music dropped before any photograph (measured), and clips on a
             device where the compositor could not start. */}
         {liveMode && (
           <div className="flex items-center px-2 py-1.5 border-b border-white/5 bg-[#0c0c0c]">
             {/* The live stage portals its clip chips + transport in here. */}
             <div ref={setStageControlsHost} className="flex-1 flex items-center min-w-0" />
           </div>
         )}
         <div className="flex border-b border-white/5 bg-[#0e0e0e]">
             <button onClick={()=>setActiveTab('simple')} title="Layout" aria-label="Layout" className={`flex-1 py-3.5 flex items-center justify-center ${activeTab==='simple'?'text-white bg-[#1a1a1a] border-t-2 border-emerald-500':'text-gray-500 hover:text-white'}`}><Layout size={16} /></button>
             <button onClick={()=>setActiveTab('advanced')} title="Settings" aria-label="Settings" className={`flex-1 py-3.5 flex items-center justify-center ${activeTab==='advanced'?'text-white bg-[#1a1a1a] border-t-2 border-emerald-500':'text-gray-500 hover:text-white'}`}><Settings size={16} /></button>
         </div>
         {activeTab === 'simple' ? (
           <SimpleControls layoutMode={layoutMode} setLayoutMode={setLayoutMode} primitive={primitive} setPrimitive={setPrimitive} count={count} setCount={updateCountSmart} density={density} setDensity={setDensity} entropy={entropy} setEntropy={setEntropy} onRemix={handleRemix} onShuffle={handleShuffle} onDice={handleDice} lastRecipe={lastRecipe} compositionCode={compositionCode} onApplyCode={applyCompositionCode} rejectedCode={rejectedBootCode} hasImages={images.length > 0} isLayoutLocked={lockedCells.size > 0} titleText={titleText} titlePlace={titlePlace} titleSize={titleSize} onTitleText={setTitleText} onTitlePlace={setTitlePlace} onTitleSize={setTitleSize} look={look} onLook={setLook} move={move} onMove={setMove} />
         ) : (
           <AdvancedControls aspect={aspect} setAspect={setAspect} gutter={gutter} setGutter={setGutter} entropy={entropy} setEntropy={setEntropy} bgColor={bgColor} setBgColor={setBgColor} avgColor={avgColor} onRemix={handleRemix} onShuffle={handleShuffle} onExportVector={handleExportSVG} onRestoreHistory={handleRestoreHistory} isLayoutLocked={lockedCells.size > 0} layoutMode={layoutMode} setLayoutMode={setLayoutMode} count={count} setCount={updateCountSmart} arrangement={arrangement} setArrangement={setArrangement} focus={focus} setFocus={setFocus} twist={twist} setTwist={setTwist} />
         )}
      </div>
      {/* CRASH RECOVERY. Shown only into an empty pool (shouldPromptRestore), so
          it never shadows a project already on the stage. One-handed sizes: the
          card caps at the viewport, the label truncates, both taps clear 44px. */}
      {restorePrompt && shouldPromptRestore(true, images.length) && (
        <div className="fixed top-3 left-1/2 -translate-x-1/2 z-[300] w-[min(28rem,94vw)] animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="rounded-xl bg-[#0d0d0d]/95 border border-emerald-500/40 shadow-2xl backdrop-blur px-3 py-2.5">
            <div className="flex items-center gap-2.5">
              <RefreshCw size={15} className="text-emerald-400 shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-black tracking-[0.14em] text-white uppercase truncate">Pick up where you left off</div>
                <div className="text-[9px] text-white/50 tracking-wide truncate">
                  {restorePrompt.images} image{restorePrompt.images === 1 ? '' : 's'} · saved {formatAgo(Date.now() - restorePrompt.savedAt)}
                </div>
              </div>
              <button onClick={handleRestoreSession} className="shrink-0 min-h-[44px] px-3.5 rounded-lg bg-emerald-500 text-black text-[10px] font-black tracking-[0.1em] uppercase active:scale-95 transition-transform">Restore</button>
              <button onClick={handleDismissRestore} aria-label="Dismiss saved session" className="shrink-0 min-h-[44px] min-w-[44px] grid place-items-center rounded-lg bg-white/5 text-white/60 hover:text-white active:scale-95 transition-transform"><X size={15} /></button>
            </div>
          </div>
        </div>
      )}
      {notice && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[250] max-w-[92vw] px-4 py-2.5 rounded-xl bg-[#161616] border border-yellow-500/30 text-[10px] tracking-wide text-yellow-300 shadow-2xl">
          {notice}
        </div>
      )}

      <input ref={fileInputRef} type="file" multiple accept="image/*,video/*" className="hidden" onChange={onFileInputChange} />
      <input ref={videoInputRef} type="file" multiple accept="video/*,.mov,.mp4,.m4v,.webm" className="hidden" onChange={onFileInputChange} />
      {/* `audio/*` plus the spellings some pickers refuse to match on type
          alone. Not `multiple`: one track is the job. */}
      <input ref={musicInputRef} type="file" accept="audio/*,.mp3,.m4a,.aac,.wav,.flac,.opus,.oga" className="hidden" onChange={onFileInputChange} />
    </div>
  );
}