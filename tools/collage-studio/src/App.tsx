/// <reference types="vite/client" />
import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Upload, Activity, X, Lock, Unlock, RefreshCw, Shuffle, Settings, Layout, Film, Plus
} from 'lucide-react';

import { loadScriptSafe, analyzeImage } from './lib/analysis';
import { computeLayout, createRng } from './lib/layout';
import { rollDice } from './lib/diceRoll';
import { assignSources, distinctSourceCount } from './lib/fill';
import { arrangeBag, withFocus, type ArrangementId, type FocusId } from './lib/composition';
import { renderCanvas } from './lib/renderer';
import { saveProject, loadProject } from './lib/project';
import { generateVectorExport } from './engine/color/vectorExport';
import { addToHistory, HistoryItem } from './lib/history';
import { Template } from './lib/templates';
import { AppState, ImageAsset, LayoutItem, LayoutMode, LiveClip, Point, PrimitiveType } from './types';
import { isVideoFile, formatTimecode, probeVideo, extractFrames, revokeFrames, type ExtractedFrame } from './lib/video';

import { Header } from './components/Header';
import { SimpleControls } from './components/SimpleControls';
import { AdvancedControls } from './components/AdvancedControls';
import { ExportDialog } from './components/ExportDialog';
import { ResultModal } from './components/ResultModal';
import { VideoImport } from './components/VideoImport';
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

export default function App() {
  const [activeTab, setActiveTab] = useState<'simple' | 'advanced'>('simple');
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('minimal');
  const [primitive, setPrimitive] = useState<PrimitiveType>('rect');
  const [count, setCount] = useState(0);
  // false → the fragment count auto-follows the number of uploaded sources
  // (one per photo/video). Flips true the moment the user owns the count
  // themselves — the slider, the dice, or a loaded project/template.
  const countTouchedRef = useRef(false);
  const [density, setDensity] = useState(1);
  const [seed, setSeed] = useState(Date.now());
  const [aspect, setAspect] = useState(0.666); 
  const [gutter, setGutter] = useState(0.005);
  const [entropy, setEntropy] = useState(0.5);
  // COMPOSITION — which photo lands in which fragment, and what each fragment
  // centres on inside it. See lib/composition.ts. Both default to the behaviour
  // the app has always had, so nothing moves until you ask it to.
  const [arrangement, setArrangement] = useState<ArrangementId>('natural');
  const [focus, setFocus] = useState<FocusId>('auto');
  const [bgColor, setBgColor] = useState('#050505'); 
  const [avgColor, setAvgColor] = useState<{r:number, g:number, b:number} | null>(null); 
  
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
  const [videoQueue, setVideoQueue] = useState<File[]>([]);
  /**
   * Clips still playable, as opposed to the stills already taken from them.
   * The app owns their object URLs for the whole session — see `LiveClip`.
   */
  const [clips, setClips] = useState<LiveClip[]>([]);
  /** Cleared if the live compositor cannot be created; falls back to the still preview. */
  const [stageOk, setStageOk] = useState(true);
  /**
   * Settings > Video. OFF means a dropped clip goes straight in and plays;
   * ON restores the frame picker. Persisted because it is a standing preference
   * about how the tool behaves, not a per-collage parameter.
   */
  const [framePicker, setFramePicker] = useState(() => {
    try { return localStorage.getItem('genart.framePicker') === '1'; } catch { return false; }
  });
  useEffect(() => {
    try { localStorage.setItem('genart.framePicker', framePicker ? '1' : '0'); } catch { /* private mode */ }
  }, [framePicker]);
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

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const isMobile = useMemo(() => /iPhone|iPad|iPod|Android/i.test(navigator.userAgent), []);

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
  useEffect(() => {
    if (images.length === 0) return;
    const n = distinctSourceCount(images);
    setCount(prev => (countTouchedRef.current ? Math.max(prev, n) : n));
  }, [images]);

  // --- ASYNC LAYOUT ENGINE ---
  useEffect(() => {
      let active = true;
      const runLayout = async () => {
          if (images.length === 0) return;
          setIsLayoutComputing(true);
          try {
              const rng = createRng(seed);
              // Pass images for Stencil Mode
              const items = await computeLayout(PREVIEW_W, PREVIEW_W / aspect, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive);
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
            const placed = arrangeBag({ bag, cells: bagCells, images, arrangement });

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
   *  reference, so the default path allocates nothing and recomputes nothing. */
  const orderedAssets = useMemo(
    () => shuffledIndices.map((idx, slot) => withFocus(images[idx], focus, (seed ^ (slot * 2654435761)) | 0)),
    [shuffledIndices, images, focus, seed],
  );

  /**
   * LIVE when there is a clip to play. This is the whole switch between the two
   * preview paths: photographs get the cheap static JPEG they have always had,
   * and a composition containing video gets a canvas that keeps moving.
   * `stageOk` drops it back to the still path if the compositor cannot start.
   */
  const liveMode = clips.length > 0 && stageOk;

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
         const canvas = await renderCanvas(PREVIEW_W, aspect, layoutMode, layoutItems, orderedPreviews, seed, zoom, bgColor);
         canvas.toBlob(blob => {
             if (previewUrl) URL.revokeObjectURL(previewUrl);
             if (blob) setPreviewUrl(URL.createObjectURL(blob));
         }, 'image/jpeg', 0.85);
       } catch (e) { console.error("Render failed", e); }
    };
    const t = setTimeout(runRender, 50);
    return () => clearTimeout(t);
  }, [images, layoutItems, shuffledIndices, orderedAssets, seed, zoom, bgColor, liveMode]);

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
    countTouchedRef.current = true;
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
    setLastRecipe(roll.recipe);
    setLockedCells(new Map());
  };

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
      const newLayout = await computeLayout(PREVIEW_W, PREVIEW_W/aspect, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive);
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
    countTouchedRef.current = true;
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
    }
    return allNewAssets;
  };

  /**
   * SEAMLESS VIDEO INTAKE — no sheet, no questions, no extra taps.
   *
   * Dropping a video means "put this in the collage". Everything the app needs
   * beyond that (a frame count, a sampling strategy, which frames to keep) has a
   * defensible default, and asking for it turned a one-gesture action into a
   * three-tap errand that also hid the fact that the clip plays at all.
   *
   * The frames are still extracted — they are the surface the clip is drawn
   * into and the fallback when a device runs out of decoders — it just happens
   * without making the user watch. Only a real failure interrupts, and only the
   * opt-in setting brings the picker back.
   */
  const autoIngestVideo = async (file: File) => {
      const shortName = file.name.length > 26 ? `${file.name.slice(0, 23)}…` : file.name;
      subIngest(0, `Reading ${shortName}…`);
      try {
          const probe = await probeVideo(file);
          if (probe.error || probe.duration <= 0) {
              flashNotice(probe.error || `${file.name} could not be read.`);
              return;
          }
          if (probe.width <= 0 || probe.height <= 0) {
              flashNotice(`${file.name} has no visual track — it looks like audio only.`);
              return;
          }
          // Same trim the sheet applies: the first and last instants of a clip
          // are usually a fade or a black frame.
          const trim = Math.min(probe.duration * 0.02, 0.25);
          const res = await extractFrames(file, {
              frameCount: isMobile ? 8 : 12,
              strategy: 'smart',
              maxDim: isMobile ? 1280 : 1600,
              maxSamples: isMobile ? 48 : 96,
              startTime: trim,
              endTime: Math.max(trim + 0.1, probe.duration - trim),
              knownDuration: probe.duration,
              onProgress: (p) => subIngest(p.ratio ?? 0, `Reading ${shortName}…`),
          });
          try {
              await handleVideoFrames(res.frames, {
                  file,
                  name: file.name,
                  duration: probe.duration,
                  width: probe.width,
                  height: probe.height,
              });
          } finally {
              // handleUpload minted its own URLs from these blobs.
              revokeFrames(res.frames);
          }
      } catch (e) {
          console.error('[video] auto import failed', e);
          flashNotice(isMobile
              ? `${file.name} could not be read. On iPhone, Photos exports are often HEVC — share it as “Most Compatible” (H.264) and retry.`
              : `${file.name} could not be read.`);
      } finally {
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

  /** Single intake for picker AND drop. Images go straight in; so do videos,
   *  unless the frame picker has been switched on in Settings. */
  const ingestFiles = (list: File[]) => {
      if (!list.length) return;
      const videos = list.filter(isVideoFile);
      const pics = list.filter(f => !isVideoFile(f) && f.type.startsWith('image/'));
      const rejected = list.length - videos.length - pics.length;

      // Videos routed to the opt-in sheet are NOT counted: the sheet drives its
      // own progress and nothing here would ever mark them done.
      const counted = pics.length + (framePicker ? 0 : videos.length);
      if (counted > 0) beginIngest(counted, `Adding ${counted} item${counted === 1 ? '' : 's'}…`);

      if (pics.length) void handleUpload(pics);
      if (videos.length) {
          if (framePicker) setVideoQueue(prev => [...prev, ...videos]);
          else {
              videoJobRef.current = videoJobRef.current
                  .then(async () => { for (const v of videos) await autoIngestVideo(v); })
                  .catch(() => { /* each clip already flashed its own notice */ });
          }
      }
      if (rejected > 0) flashNotice(`${rejected} unsupported file(s) ignored — images and video only.`);
  };

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files ? Array.from(e.target.files) : [];
    e.target.value = '';
    ingestFiles(list);
  };

  /**
   * Frames accepted in the video sheet -> the SAME pool, the SAME analysis path.
   *
   * AND, new: the clip itself is kept alive. Every frame is stamped with the
   * `clipId` of the video it came from, which is the binding the live compositor
   * uses to put the moving clip back where its still is sitting. Extraction is
   * unchanged — the stills are still real assets, still shuffle and lock and
   * export exactly as before, and a device that cannot spare a decoder simply
   * shows them. The clip is an ADDITION to the still, never a replacement.
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
  useEffect(() => () => {
      for (const c of clipsRef.current) { try { URL.revokeObjectURL(c.url); } catch { /* ignore */ } }
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
      const state: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, seed, aspect, gutter, entropy, arrangement, focus }, style: { background: bgColor } };
      addToHistory(state, images, previewUrl || undefined);
      // Clearing the pool orphans every clip: nothing is left carrying a clipId,
      // so the files would sit in memory unreachable for the rest of the session.
      for (const c of clips) { try { URL.revokeObjectURL(c.url); } catch { /* ignore */ } }
      setClips([]); setStageOk(true);
      setImages([]); setPreviewUrl(null); setCount(0); setDensity(1); setLockedCells(new Map()); setAvgColor(null);
      countTouchedRef.current = false; // a fresh import after Clear auto-follows the upload count again
  };

  const handleRestoreHistory = (item: HistoryItem) => {
      countTouchedRef.current = true; // restoring a saved composition's own count
      setImages(item.images);
      const l = item.state.layout;
      setLayoutMode(l.mode); if(l.primitive) setPrimitive(l.primitive);
      setCount(l.count); setSeed(l.seed); setAspect(l.aspect); setGutter(l.gutter); setActiveTab(item.state.mode);
      if(l.entropy) setEntropy(l.entropy);
      if(l.arrangement) setArrangement(l.arrangement);
      // A project saved before this cycle stored the old binary hue sort as a
      // 0..1 "resonance". Anything above the threshold it used WAS colour flow.
      else if((l.resonance ?? 0) > 0.1) setArrangement('flow');
      if(l.focus) setFocus(l.focus);
      if(item.state.style?.background) setBgColor(item.state.style.background);
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
      const ordered = shuffledIndices.map(idx => images[idx] ?? null);

      const rng = createRng(seed);
      const items = await computeLayout(w, h, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive);

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
              zoom, bgColor,
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

  const handleDownloadResult = () => {
      if (!resultBlobUrl) return;
      const a = document.createElement('a'); a.href = resultBlobUrl; a.download = `GENART-${Date.now()}.jpg`; a.click();
  };

  const handleExportSVG = async () => {
    setShowExportDialog(false); setExportStatus('processing'); setExportMsg('VECTORIZING...');
    try {
        const rng = createRng(seed); const items = await computeLayout(1000, 1000/aspect, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive);
        const orderedImages = shuffledIndices.map(idx => images[idx]);
        const stateForSave: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, seed, aspect, gutter, entropy, arrangement, focus }, style: { background: bgColor } };
        const svgContent = await generateVectorExport(1000, aspect, layoutMode, items, orderedImages, seed, stateForSave, zoom, bgColor);
        const blob = new Blob([svgContent], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `GENART-VECTOR-${seed}.svg`; a.click(); URL.revokeObjectURL(url);
        setExportStatus('done'); setTimeout(() => setExportStatus('idle'), 2000);
    } catch (e) { setExportStatus('error'); }
  };

  const handleSaveProject = async () => { setShowExportDialog(false); const state: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, seed, aspect, gutter, entropy, arrangement, focus }, style: { background: bgColor } }; await saveProject(state, images); };
  const handleLoadProject = () => { 
    const input = document.createElement('input'); input.type = 'file'; input.accept = '.collage,.svg';
    input.onchange = async (e:any) => {
        const file = e.target.files[0]; if(!file) return;
        const loaded = await loadProject(file);
        if(loaded) { countTouchedRef.current = true; setImages(loaded.images); const l = loaded.state.layout; setLayoutMode(l.mode || 'minimal'); setCount(l.count || 12); setSeed(l.seed || Date.now()); setAspect(l.aspect || 0.666); setGutter(l.gutter || 0.005); if(l.entropy) setEntropy(l.entropy); if(l.primitive) setPrimitive(l.primitive); if(loaded.state.style?.background) setBgColor(loaded.state.style.background); if(l.arrangement) setArrangement(l.arrangement); else if((l.resonance ?? 0) > 0.1) setArrangement('flow'); if(l.focus) setFocus(l.focus); }
    };
    input.click();
  };

  const handleApplyTemplate = (t: Template) => {
      countTouchedRef.current = true; // a template carries its own explicit fragment count
      setLayoutMode(t.layout.mode); setCount(t.layout.count); setSeed(t.layout.seed); setAspect(t.layout.aspect); setGutter(t.layout.gutter);
  };

  return (
    <div className="fixed inset-0 bg-black text-white font-sans flex flex-col select-none overflow-hidden">
      <Header aiState={aiState} exportStatus={exportStatus} exportMsg={exportMsg} onExport={() => setShowExportDialog(true)} hasImages={images.length > 0} onSaveProject={handleSaveProject} onLoadProject={handleLoadProject} />
      <ExportDialog canExportVideo={liveMode} onExportVideo={(secs) => recorderRef.current?.start(secs)} videoMaxSeconds={recorderRef.current?.maxSeconds ?? 30} isOpen={showExportDialog} onClose={() => setShowExportDialog(false)} onExport={handleExport} onExportSVG={handleExportSVG} onExportProject={handleSaveProject} canShare={!!navigator.share} onShare={handleShare} />
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
               <span className="text-[10px] font-black tracking-[0.2em] text-white uppercase">Drop images or video</span>
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
            <div className="relative z-10 w-full h-full p-6 flex items-center justify-center" ref={containerRef}>
               <div className="relative shadow-2xl transition-all duration-300" style={{ aspectRatio: aspect, maxHeight: '100%', maxWidth: '100%' }}>
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
                       onNotice={flashNotice}
                       onUnavailable={() => setStageOk(false)}
                       controlsHost={stageControlsHost}
                       onRemoveClip={removeClip}
                       recorderRef={recorderRef}
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
               <div className="absolute top-4 right-4 flex flex-col gap-2">
                   <button
                     onClick={() => fileInputRef.current?.click()}
                     title="Add more images or video"
                     aria-label="Add more images or video"
                     className="w-11 h-11 rounded bg-[#111] text-gray-300 border border-gray-800 flex items-center justify-center hover:bg-white/10 hover:text-white transition-colors shadow-lg"
                   ><Plus size={18} /></button>
                   <button
                     onClick={() => videoInputRef.current?.click()}
                     title="Extract frames from a video"
                     aria-label="Extract frames from a video"
                     className="w-11 h-11 rounded bg-[#111] text-emerald-400 border border-gray-800 flex items-center justify-center hover:bg-emerald-500/15 transition-colors shadow-lg"
                   ><Film size={18} /></button>
                   <button onClick={handleClear} title="Clear all" aria-label="Clear all" className="w-11 h-11 rounded bg-[#111] text-red-500 border border-gray-800 flex items-center justify-center hover:bg-red-900/30 transition-colors shadow-lg"><X size={18} /></button>
               </div>

            </div>
         )}
      </div>

      <div className="bg-[#0a0a0a] border-t border-white/10 pb-safe z-50 relative shrink-0">
         {/* VIDEO DOCK — everything the live stage needs to say or be driven by,
             OUTSIDE the canvas. This used to float over the collage; chrome on
             top of the artwork covers the thing the user is here to look at. */}
         {clips.length > 0 && (
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
           <SimpleControls layoutMode={layoutMode} setLayoutMode={setLayoutMode} primitive={primitive} setPrimitive={setPrimitive} count={count} setCount={updateCountSmart} density={density} setDensity={setDensity} entropy={entropy} setEntropy={setEntropy} onRemix={handleRemix} onShuffle={handleShuffle} onDice={handleDice} lastRecipe={lastRecipe} hasImages={images.length > 0} isLayoutLocked={lockedCells.size > 0} />
         ) : (
           <AdvancedControls aspect={aspect} setAspect={setAspect} gutter={gutter} setGutter={setGutter} entropy={entropy} setEntropy={setEntropy} bgColor={bgColor} setBgColor={setBgColor} avgColor={avgColor} onRemix={handleRemix} onShuffle={handleShuffle} onExportVector={handleExportSVG} onRestoreHistory={handleRestoreHistory} isLayoutLocked={lockedCells.size > 0} layoutMode={layoutMode} setLayoutMode={setLayoutMode} count={count} setCount={updateCountSmart} arrangement={arrangement} setArrangement={setArrangement} focus={focus} setFocus={setFocus} framePicker={framePicker} setFramePicker={setFramePicker} />
         )}
      </div>
      {notice && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[250] max-w-[92vw] px-4 py-2.5 rounded-xl bg-[#161616] border border-yellow-500/30 text-[10px] tracking-wide text-yellow-300 shadow-2xl">
          {notice}
        </div>
      )}

      {videoQueue.length > 0 && (
        <VideoImport
          key={`${videoQueue[0].name}:${videoQueue[0].size}:${videoQueue.length}`}
          file={videoQueue[0]}
          isMobile={isMobile}
          queued={videoQueue.length - 1}
          allowFramePicker={framePicker}
          onCommit={handleVideoFrames}
          onClose={() => setVideoQueue(q => q.slice(1))}
        />
      )}

      <input ref={fileInputRef} type="file" multiple accept="image/*,video/*" className="hidden" onChange={onFileInputChange} />
      <input ref={videoInputRef} type="file" multiple accept="video/*,.mov,.mp4,.m4v,.webm" className="hidden" onChange={onFileInputChange} />
    </div>
  );
}