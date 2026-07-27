/// <reference types="vite/client" />
import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Upload, Activity, X, Lock, Unlock, RefreshCw, Shuffle, Settings, Layout, Film, Plus
} from 'lucide-react';

import { loadScriptSafe, analyzeImage } from './lib/analysis';
import { computeLayout, createRng } from './lib/layout';
import { renderCanvas } from './lib/renderer';
import { saveProject, loadProject } from './lib/project';
import { generateVectorExport } from './engine/color/vectorExport';
import { addToHistory, HistoryItem } from './lib/history';
import { Template } from './lib/templates';
import { AppState, ImageAsset, LayoutItem, LayoutMode, LiveClip, Point, PrimitiveType } from './types';
import { isVideoFile, formatTimecode, type ExtractedFrame } from './lib/video';

import { Header } from './components/Header';
import { SimpleControls } from './components/SimpleControls';
import { AdvancedControls } from './components/AdvancedControls';
import { ExportDialog } from './components/ExportDialog';
import { ResultModal } from './components/ResultModal';
import { VideoImport } from './components/VideoImport';
import { VideoStage } from './components/VideoStage';
import RenderWorker from './workers/render.worker?worker';

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
  /** Noun for the busy overlay ("images" / "frames"). */
  noun?: string;
}

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
  const [density, setDensity] = useState(1);
  const [seed, setSeed] = useState(Date.now());
  const [aspect, setAspect] = useState(0.666); 
  const [gutter, setGutter] = useState(0.005);
  const [entropy, setEntropy] = useState(0.5); 
  const [resonance, setResonance] = useState(0); 
  const [bgColor, setBgColor] = useState('#050505'); 
  const [avgColor, setAvgColor] = useState<{r:number, g:number, b:number} | null>(null); 
  
  const [lockedCells, setLockedCells] = useState<Map<number, string>>(new Map());
  const [shuffledIndices, setShuffledIndices] = useState<number[]>([]); 
  const [shuffleTrigger, setShuffleTrigger] = useState(0);

  const [layoutItems, setLayoutItems] = useState<LayoutItem[]>([]);
  const [isLayoutComputing, setIsLayoutComputing] = useState(false);

  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isComputing, setIsComputing] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
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
        const newIndices = new Array(effectiveCount).fill(-1);
        const rng = createRng(seed + shuffleTrigger);
        const imageIdToIndex = new Map(images.map((img, i) => [img.id, i]));
        const usedImageIndices = new Set<number>();
        lockedCells.forEach((imgId, cellIdx) => {
            const currentImgIdx = imageIdToIndex.get(imgId);
            if (cellIdx < effectiveCount && currentImgIdx !== undefined) {
                newIndices[cellIdx] = currentImgIdx;
                usedImageIndices.add(currentImgIdx);
            }
        });
        const emptySlots = [];
        for(let i=0; i<effectiveCount; i++) { if(newIndices[i] === -1) emptySlots.push(i); }
        if (emptySlots.length > 0) {
            const unusedImages = images.map((_, i) => i).filter(i => !usedImageIndices.has(i));
            const allImages = images.map((_, i) => i);
            const bag: number[] = [];
            const shuffle = (arr: number[]) => {
                for (let i = arr.length - 1; i > 0; i--) {
                    const j = Math.floor(rng() * (i + 1));
                    [arr[i], arr[j]] = [arr[j], arr[i]];
                }
                return arr;
            };
            if(unusedImages.length > 0) bag.push(...shuffle(unusedImages));
            while(bag.length < emptySlots.length) { bag.push(...shuffle([...allImages])); }
            
            // Resonance Sorting
            if (resonance > 0.1) {
                bag.sort((a, b) => {
                    const cA = images[a].analysis?.color || { h: 0, s: 0, l: 0 };
                    const cB = images[b].analysis?.color || { h: 0, s: 0, l: 0 };
                    if (Math.abs(cA.h - cB.h) > 0.1) return cA.h - cB.h;
                    return cA.l - cB.l;
                });
            }

            emptySlots.forEach((slotIdx, i) => { newIndices[slotIdx] = bag[i]; });
        }
        return newIndices;
    });
  }, [images, effectiveCount, seed, shuffleTrigger, resonance]); 

  /** The pool in draw order. Memoised because the live Stage rebuilds its whole
   *  draw list whenever this identity changes — a fresh array every render would
   *  re-do the crop maths and the clip admission pass on every keystroke. */
  const orderedAssets = useMemo(
    () => shuffledIndices.map(idx => images[idx]),
    [shuffledIndices, images],
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

  /** Resolves with the assets that actually landed — the caller needs to know
   *  whether anything decoded before it commits to keeping the source alive. */
  const handleUpload = async (files: File[], opts: UploadOptions = {}): Promise<ImageAsset[]> => {
    if (!files.length) return [];
    const noun = opts.noun || 'images';
    const prefix = opts.idPrefix || 'img';
    setIsComputing(true);
    setStatusMsg(`Preparing ${files.length} ${noun}...`);
    const CHUNK_SIZE = 5;
    const allNewAssets: ImageAsset[] = [];
    await new Promise(r => setTimeout(r, 50));
    let totalR=0, totalG=0, totalB=0, colorCount=0;

    try {
      for (let i = 0; i < files.length; i += CHUNK_SIZE) {
          const chunk = files.slice(i, i + CHUNK_SIZE);
          setStatusMsg(`Processing ${i + 1} - ${Math.min(i+CHUNK_SIZE, files.length)} of ${files.length}...`);
          const promises = chunk.map(async (file) => {
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
              const asset: ImageAsset = {
                  id: `${prefix}-${Date.now()}-${assetSeq++}`,
                  src: url,
                  previewSrc: thumbUrl,
                  originalName: file.name,
                  width: img.width,
                  height: img.height,
                  analysis,
                  ...(opts.meta?.get(file) ?? {}),
              };
              return asset;
          });
          const results = (await Promise.all(promises)).filter(Boolean) as ImageAsset[];
          allNewAssets.push(...results);
          await new Promise(r => setTimeout(r, 10));
      }
      if(colorCount > 0) {
          const avg = { r: Math.round(totalR/colorCount), g: Math.round(totalG/colorCount), b: Math.round(totalB/colorCount) };
          setAvgColor(avg);
      }
      if (allNewAssets.length < files.length) {
          flashNotice(`${files.length - allNewAssets.length} file(s) could not be decoded and were skipped.`);
      }
      setImages(prev => {
          const combined = [...prev, ...allNewAssets];
          // Both branches are IDEMPOTENT: this updater runs twice under React 18
          // StrictMode and must not compound.
          if(prev.length === 0 && combined.length > 0) { updateCountSmart(Math.min(combined.length, 12)); }
          else if (opts.grow && allNewAssets.length > 0) {
              const target = Math.min(combined.length, Math.max(12, allNewAssets.length), 36);
              updateCountSmart(c => Math.max(c, target));
          }
          return combined;
      });
    } catch (e) { console.error("Upload failed", e); flashNotice('Import failed — see console for details.'); }
    finally { setIsComputing(false); setStatusMsg(''); }
    return allNewAssets;
  };

  /** Single intake for picker AND drop: images go straight in, videos queue for extraction. */
  const ingestFiles = (list: File[]) => {
      if (!list.length) return;
      const videos = list.filter(isVideoFile);
      const pics = list.filter(f => !isVideoFile(f) && f.type.startsWith('image/'));
      const rejected = list.length - videos.length - pics.length;
      if (pics.length) handleUpload(pics);
      if (videos.length) setVideoQueue(prev => [...prev, ...videos]);
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
      const landed = await handleUpload(files, { idPrefix: 'vid', grow: true, meta, noun: 'frames' });

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
      if (isComputing) return;
      ingestFiles(Array.from(e.dataTransfer.files || []));
  };

  const handleClear = () => {
      const state: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, seed, aspect, gutter }, style: { background: bgColor } };
      addToHistory(state, images, previewUrl || undefined);
      // Clearing the pool orphans every clip: nothing is left carrying a clipId,
      // so the files would sit in memory unreachable for the rest of the session.
      for (const c of clips) { try { URL.revokeObjectURL(c.url); } catch { /* ignore */ } }
      setClips([]); setStageOk(true);
      setImages([]); setPreviewUrl(null); setCount(0); setDensity(1); setLockedCells(new Map()); setAvgColor(null);
  };

  const handleRestoreHistory = (item: HistoryItem) => {
      setImages(item.images);
      const l = item.state.layout;
      setLayoutMode(l.mode); if(l.primitive) setPrimitive(l.primitive);
      setCount(l.count); setSeed(l.seed); setAspect(l.aspect); setGutter(l.gutter); setActiveTab(item.state.mode);
      if(l.entropy) setEntropy(l.entropy);
      if(l.resonance) setResonance(l.resonance);
      if(item.state.style?.background) setBgColor(item.state.style.background);
  };

  const generateBlob = async (widthPx: number, quality = 0.92): Promise<Blob> => {
      const orderedImages = shuffledIndices.map(idx => images[idx]);
      const effectiveWidth = Math.floor(aspect < 1 ? widthPx * aspect : widthPx);
      const effectiveHeight = Math.floor(effectiveWidth / aspect);
      const rng = createRng(seed);
      const items = await computeLayout(effectiveWidth, effectiveHeight, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive);
      try {
          const worker = new RenderWorker();
          return await new Promise<Blob>((resolve, reject) => {
              worker.onmessage = (e: MessageEvent<{ success: boolean; blob: Blob; error?: string }>) => {
                  if (e.data.success) resolve(e.data.blob); else reject(new Error(e.data.error)); worker.terminate();
              };
              worker.onerror = (e: ErrorEvent) => { reject(e); worker.terminate(); };
              worker.postMessage({ id: 1, width: effectiveWidth, height: effectiveHeight, mode: layoutMode, layoutItems: items, 
                  orderedImages: orderedImages.map(img => ({ src: img.src, width: img.width, height: img.height, analysis: img.analysis })),
                  zoom, bgColor 
              });
          });
      } catch (e) {
          console.warn("Worker failed, fallback", e);
          const canvas = await renderCanvas(effectiveWidth, aspect, layoutMode, items, orderedImages, seed, zoom, bgColor);
          return new Promise((resolve, reject) => { canvas.toBlob(b => b ? resolve(b) : reject(new Error("Blob failed")), 'image/jpeg', quality); });
      }
  };

  const onBlobReady = (blob: Blob) => {
      const url = URL.createObjectURL(blob);
      setResultBlobUrl(url); 
      setExportStatus('done'); setTimeout(() => setExportStatus('idle'), 3000);
  };

  const handleExport = async (size: number) => {
      if (size === 30000) {
          handleMaxRezzy();
      } else {
          setShowExportDialog(false); setExportStatus('processing'); setExportMsg(`${size}px Rendering...`);
          try {
              await new Promise(r => setTimeout(r, 100));
              const blob = await generateBlob(size);
              onBlobReady(blob);
          } catch (e) { console.warn("Export failed", e); setExportStatus('error'); }
      }
  };

  const handleMaxRezzy = async () => {
      setShowExportDialog(false); setExportStatus('processing');
      const TIERS = [30000, 24000, 16384, 12000, 8192, 4096]; 
      for (const tier of TIERS) {
          try {
              setExportMsg(`${tier}px Attempt...`);
              await new Promise(r => setTimeout(r, 200));
              const blob = await generateBlob(tier);
              setExportMsg(`ENCODING...`);
              await new Promise(r => setTimeout(r, 100));
              onBlobReady(blob);
              return; 
          } catch (e) { console.warn(`Tier ${tier} failed`, e); await new Promise(r => setTimeout(r, 1000)); }
      }
      setExportStatus('error');
  };

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
        const stateForSave: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, seed, aspect, gutter }, style: { background: bgColor } };
        const svgContent = await generateVectorExport(1000, aspect, layoutMode, items, orderedImages, seed, stateForSave, zoom, bgColor);
        const blob = new Blob([svgContent], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `GENART-VECTOR-${seed}.svg`; a.click(); URL.revokeObjectURL(url);
        setExportStatus('done'); setTimeout(() => setExportStatus('idle'), 2000);
    } catch (e) { setExportStatus('error'); }
  };

  const handleSaveProject = async () => { setShowExportDialog(false); const state: AppState = { version: "1.0", mode: activeTab, layout: { mode: layoutMode, primitive, count, seed, aspect, gutter }, style: { background: bgColor } }; await saveProject(state, images); };
  const handleLoadProject = () => { 
    const input = document.createElement('input'); input.type = 'file'; input.accept = '.collage,.svg';
    input.onchange = async (e:any) => {
        const file = e.target.files[0]; if(!file) return;
        const loaded = await loadProject(file);
        if(loaded) { setImages(loaded.images); const l = loaded.state.layout; setLayoutMode(l.mode || 'minimal'); setCount(l.count || 12); setSeed(l.seed || Date.now()); setAspect(l.aspect || 0.666); setGutter(l.gutter || 0.005); if(l.entropy) setEntropy(l.entropy); if(l.primitive) setPrimitive(l.primitive); if(loaded.state.style?.background) setBgColor(loaded.state.style.background); if(l.resonance) setResonance(l.resonance); }
    };
    input.click();
  };

  const handleApplyTemplate = (t: Template) => {
      setLayoutMode(t.layout.mode); setCount(t.layout.count); setSeed(t.layout.seed); setAspect(t.layout.aspect); setGutter(t.layout.gutter);
  };

  return (
    <div className="fixed inset-0 bg-black text-white font-sans flex flex-col select-none overflow-hidden">
      <Header aiState={aiState} exportStatus={exportStatus} exportMsg={exportMsg} onExport={() => setShowExportDialog(true)} hasImages={images.length > 0} onSaveProject={handleSaveProject} onLoadProject={handleLoadProject} />
      <ExportDialog isOpen={showExportDialog} onClose={() => setShowExportDialog(false)} onExport={handleExport} onExportJPG={() => handleExport(4096)} onExportMax={handleMaxRezzy} onExportSVG={handleExportSVG} onExportProject={handleSaveProject} canShare={!!navigator.share} onShare={handleShare} />
      <ResultModal isOpen={!!resultBlobUrl} onClose={() => setResultBlobUrl(null)} blobUrl={resultBlobUrl} onShare={handleShareResult} onDownload={handleDownloadResult} isMobile={isMobile} />

      <div
        className="flex-1 relative bg-[#050505] flex items-center justify-center overflow-hidden"
        onDragEnter={onDragEnter} onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}
      >
         <div className="absolute inset-0 opacity-[0.05] pointer-events-none z-0" style={{ backgroundImage: 'linear-gradient(#444 1px, transparent 1px), linear-gradient(90deg, #444 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
         {(isComputing || isLayoutComputing) && (<div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm"><div className="flex flex-col items-center animate-in fade-in zoom-in duration-300"><Activity className="animate-spin text-emerald-500 mb-2" size={48} /><span className="text-xs font-black text-white tracking-[0.2em] uppercase drop-shadow-lg">{isLayoutComputing ? 'COMPUTING LAYOUT...' : statusMsg}</span></div></div>)}
         {isDragging && (
            <div className="absolute inset-3 z-[150] pointer-events-none rounded-2xl border-2 border-dashed border-emerald-500/70 bg-emerald-500/5 flex flex-col items-center justify-center gap-2">
               <Film size={26} className="text-emerald-400" />
               <span className="text-[10px] font-black tracking-[0.2em] text-white uppercase">Drop images or video</span>
            </div>
         )}
         {images.length === 0 ? (
            <div onClick={() => !isComputing && fileInputRef.current?.click()} className="relative z-10 group flex flex-col items-center justify-center p-10 border border-dashed rounded-full border-gray-800 cursor-pointer hover:border-emerald-500/50 hover:bg-white/5 active:scale-95 transition-all">
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
                     onClick={() => !isComputing && fileInputRef.current?.click()}
                     title="Add more images or video"
                     aria-label="Add more images or video"
                     className="w-10 h-10 rounded bg-[#111] text-gray-300 border border-gray-800 flex items-center justify-center hover:bg-white/10 hover:text-white transition-colors shadow-lg"
                   ><Plus size={18} /></button>
                   <button
                     onClick={() => !isComputing && videoInputRef.current?.click()}
                     title="Extract frames from a video"
                     aria-label="Extract frames from a video"
                     className="w-10 h-10 rounded bg-[#111] text-emerald-400 border border-gray-800 flex items-center justify-center hover:bg-emerald-500/15 transition-colors shadow-lg"
                   ><Film size={18} /></button>
                   <button onClick={handleClear} title="Clear all" aria-label="Clear all" className="w-10 h-10 rounded bg-[#111] text-red-500 border border-gray-800 flex items-center justify-center hover:bg-red-900/30 transition-colors shadow-lg"><X size={18} /></button>
               </div>

               {/* LIVE CLIPS. Dropping one frees its decoder AND its file while
                   keeping every still already extracted from it — so this is a
                   real lever on a device that has run out of decoders, not just
                   a delete button. */}
               {clips.length > 0 && (
                 <div className="absolute top-4 left-4 z-20 flex flex-col gap-1.5 max-w-[45%]">
                   {clips.map(c => (
                     <div key={c.id} className="flex items-center gap-1.5 pl-2 pr-1 py-1 rounded-lg bg-black/70 backdrop-blur border border-white/10 shadow-lg">
                       <Film size={11} className="text-emerald-400 shrink-0" />
                       <span className="text-[9px] tracking-wide text-gray-300 truncate" title={c.name}>{c.name}</span>
                       <span className="text-[8px] tracking-widest text-gray-600 tabular-nums shrink-0">{c.frameCount}f</span>
                       <button
                         onClick={() => removeClip(c.id)}
                         title={`Stop playing ${c.name} (keeps its ${c.frameCount} frames)`}
                         aria-label={`Stop playing ${c.name}`}
                         className="w-5 h-5 rounded flex items-center justify-center text-gray-500 hover:text-red-400 hover:bg-white/10 transition-colors shrink-0"
                       ><X size={11} /></button>
                     </div>
                   ))}
                 </div>
               )}
            </div>
         )}
      </div>

      <div className="bg-[#0a0a0a] border-t border-white/10 pb-safe z-50 relative shrink-0">
         <div className="flex border-b border-white/5 bg-[#0e0e0e]">
             <button onClick={()=>setActiveTab('simple')} className={`flex-1 py-3 flex items-center justify-center ${activeTab==='simple'?'text-white bg-[#1a1a1a] border-t-2 border-emerald-500':'text-gray-500 hover:text-white'}`}><Layout size={16} /></button>
             <button onClick={()=>setActiveTab('advanced')} className={`flex-1 py-3 flex items-center justify-center ${activeTab==='advanced'?'text-white bg-[#1a1a1a] border-t-2 border-emerald-500':'text-gray-500 hover:text-white'}`}><Settings size={16} /></button>
         </div>
         {activeTab === 'simple' ? (
           <SimpleControls layoutMode={layoutMode} setLayoutMode={setLayoutMode} primitive={primitive} setPrimitive={setPrimitive} count={count} setCount={updateCountSmart} density={density} setDensity={setDensity} entropy={entropy} setEntropy={setEntropy} onRemix={handleRemix} onShuffle={handleShuffle} hasImages={images.length > 0} isLayoutLocked={lockedCells.size > 0} />
         ) : (
           <AdvancedControls aspect={aspect} setAspect={setAspect} gutter={gutter} setGutter={setGutter} entropy={entropy} setEntropy={setEntropy} bgColor={bgColor} setBgColor={setBgColor} avgColor={avgColor} onRemix={handleRemix} onShuffle={handleShuffle} onExportVector={handleExportSVG} onRestoreHistory={handleRestoreHistory} isLayoutLocked={lockedCells.size > 0} layoutMode={layoutMode} setLayoutMode={setLayoutMode} count={count} setCount={updateCountSmart} resonance={resonance} setResonance={setResonance} />
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
          onCommit={handleVideoFrames}
          onClose={() => setVideoQueue(q => q.slice(1))}
        />
      )}

      <input ref={fileInputRef} type="file" multiple accept="image/*,video/*" className="hidden" onChange={onFileInputChange} />
      <input ref={videoInputRef} type="file" multiple accept="video/*,.mov,.mp4,.m4v,.webm" className="hidden" onChange={onFileInputChange} />
    </div>
  );
}