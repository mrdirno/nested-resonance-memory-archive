/// <reference types="vite/client" />
import React, { useState, useRef, useEffect, useLayoutEffect, useMemo, useCallback } from 'react';
import {
  Upload, Activity, X, Lock, Unlock, RefreshCw, Shuffle, Settings, Layout, Film, Plus,
  Maximize2, Minimize2, Dices, Music, Undo2, Redo2, Palette, ArrowLeftRight, Crosshair, Type, Wand2
} from 'lucide-react';

import { loadScriptSafe, analyzeImage } from './lib/analysis';
import { computeLayout, createRng } from './lib/layout';
import { rollDice, ASPECT_ROSTER } from './lib/diceRoll';
import { rollDeal } from './lib/dealRoll';
import { encodeState, decodeState, codeFromUrl, CODE_PARAM } from './lib/rollCode';
import {
  emptyHistory, commit as commitHistory, undo as undoHistory, redo as redoHistory,
  canUndo as histCanUndo, canRedo as histCanRedo,
  type CompositionHistory, type CompositionSnapshot,
} from './lib/compositionHistory';
import { assignSources, distinctSourceCount } from './lib/fill';
import { arrangeBag, withFocus, withTwist, twistAngle, type ArrangementId, type FocusId, type TwistId } from './lib/composition';
import { withMove, type MoveId } from './lib/motion';
import { isTurning, type TurnId } from './lib/turn';
import { type PaceId } from './lib/pace';
import { renderCanvas, calculateSmartCrop } from './lib/renderer';
import { withReframe, dragToFrame, poolWithFrames, framesFromPool, poolWithoutFrames, type Frame } from './lib/reframe';
import { planTitle, measureWith, type TitlePlace, type TitleSize } from './lib/title';
import { EMPTY_CAPTION_TRACK, normalizeCaptionTrack, planCaptions, captionPlanAt, type CaptionTrack } from './lib/captions';
import { normalizeProjectLocks } from './lib/projectLocks';
import { CaptionEditor } from './components/CaptionEditor';
import { ArtRoom } from './components/ArtRoom';
import { StudioStart } from './components/StudioStart';
import './styles/workspace.css';
import { ArtRackRoom } from './components/ArtRackRoom';
import { ART_SIZES, artIsAnimated, createDefaultArtRecipe, normalizeArtRecipe, type ArtRecipe } from './lib/artRack';
import { drawArt } from './lib/artRackRenderer';
import { createLyricDemo } from './lib/lyricDemo';
import { deskForLook, gradeFromDesk, sameDesk, snapDesk, type Desk, type LookId, type LookRef } from './lib/grade';
import { saveProject, loadProject } from './lib/project';
import { canAutosave, hasUnsavedWork, shouldPromptRestore, formatAgo, planAssetWrites, sessionEntries, hydrateSessionAssets, preflightSessionAssets, AUTOSAVE_DEBOUNCE_MS } from './lib/session';
import type { AssetUrls } from './lib/session';
import * as sessionStore from './lib/sessionStore';
import { generateVectorExport } from './engine/color/vectorExport';
import { addToHistory, HistoryItem } from './lib/history';
import { Template } from './lib/templates';
import { AppState, ImageAsset, LayoutItem, LayoutMode, LiveClip, Point, PrimitiveType } from './types';
import { isVideoFile, formatTimecode, openClip, revokeFrames, type ExtractedFrame } from './lib/video';
import { isAudioFile, type SoundtrackSpec } from './lib/soundtrack';
import { splitIntake, type IntakeIntent } from './lib/intake';
import { planEviction, describeEviction } from './lib/evict';
import { planSwap, describeSwap, canSwapFrom } from './lib/swap';
import { detectBeat, beatSchedule, beatLabel, BEAT_ANALYSE_SEC, isSynced, type BeatGrid, type SyncId } from './lib/beat';
import { turnHoldSec } from './lib/turn';
import { paceRate } from './lib/pace';

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
  /** A retired Art Room capture must not land after asynchronous decoding. */
  shouldCommit?: () => boolean;
  /** Procedural artwork has no faces; avoid loading inference for the starter. */
  geometryOnly?: boolean;
  /** Distinct id namespace (video frames use 'vid'). */
  idPrefix?: string;
  /** Grow `count` so the new assets are actually visible on a non-empty canvas. */
  grow?: boolean;
  /** Per-file provenance, keyed by the File object itself. */
  meta?: Map<File, AssetProvenance & { art?: ArtRecipe }>;
  /** Native artwork revisions have immutable ids and bytes in recovery. */
  replaceId?: string;
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

type StudioTool = 'add' | 'layout' | 'look' | 'motion' | 'text';

export default function App() {
  const [stageDetailsOpen, setStageDetailsOpen] = useState(false);
  const handleStageDetails = useCallback((open: boolean) => { setStageDetailsOpen(open); if (open) setStudioTool(null); }, []);
  const [studioTool, setStudioTool] = useState<StudioTool | null>(null);
  const toolRefs = useRef<Partial<Record<StudioTool, HTMLButtonElement | null>>>({});
  const studioToolRef = useRef(studioTool); studioToolRef.current = studioTool;
  const inspectorCloseRef = useRef<HTMLButtonElement>(null);
  const restoreToolFocusRef = useRef<StudioTool | null>(null);
  const closeTool = () => { restoreToolFocusRef.current = studioToolRef.current; setStudioTool(null); };
  // Short viewports hide the invoking taskbar while editing. Restore focus
  // after the new layout exists; focusing a display:none button is a no-op.
  useLayoutEffect(() => {
    if (studioTool) {
      if (!toolRefs.current[studioTool]?.getClientRects().length) inspectorCloseRef.current?.focus();
    } else if (restoreToolFocusRef.current) {
      toolRefs.current[restoreToolFocusRef.current]?.focus();
      restoreToolFocusRef.current = null;
    }
  }, [studioTool]);
  const [activeTab, setActiveTab] = useState<'simple' | 'advanced'>('simple');
  const [artRoomOpen, setArtRoomOpen] = useState(false);
  const [artRoomMode, setArtRoomMode] = useState<'templates' | 'html'>('templates');
  const [artDraft, setArtDraft] = useState<ArtRecipe>(createDefaultArtRecipe);
  const [artSourceId, setArtSourceId] = useState<string | null>(null);
  const artRoomTriggerRef = useRef<HTMLButtonElement>(null);
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
  const maximizedRef = useRef(maximized); maximizedRef.current = maximized;
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
  /**
   * THE FRAME HOLD — while on, the dice keeps the shape of frame on screen.
   *
   * Wished for (wishing well, collage): *"Tide pool is sick I like them. Maybe
   * good idea to lock aspect ratio too as a toggle."* Chasing a recipe means
   * pressing the dice again and again, and every press re-dealt the canvas
   * shape too — measured 12 for 12 on a roster of seven frames.
   *
   * `diceRoll.ts` has carried the idea since the locks shipped — `RollLock`,
   * "the slot-machine hold" — with no caller ever passing it. This is that
   * hold's first surface, for the one parameter somebody asked for. A
   * preference about FUTURE rolls, the same class as `lockedCells`: it rides
   * neither the composition code, nor saved projects, nor history.
   */
  const [holdFrame, setHoldFrame] = useState(false);
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
  /**
   * HAS ANYBODY ACTUALLY CHOSEN A MOVE? `'still'` is both the app's default and a
   * legitimate answer, so the value alone cannot tell the two apart — and the
   * difference decides whether adopting music is allowed to start the collage
   * moving (see `adoptSoundtrack`).
   *
   * Only a LIVE choice counts: the move control and the dice. A restored session
   * is deliberately not one, because `sessionStore` does not carry the soundtrack
   * — so adding music after a restore is always a fresh act, never a replay of
   * one.
   */
  const moveOwnedRef = useRef(false);
  const chooseMove = (m: MoveId) => { moveOwnedRef.current = true; setMove(m); };
  /** THE TURN — how often the collage re-cuts to a new deal. See lib/turn.ts. */
  const [turn, setTurn] = useState<TurnId>('hold');
  /**
   * THE PACE — the RATE the move and the turn run at. See lib/pace.ts.
   *
   * Beside them because it is meaningless apart from them, and separate from
   * them because that separation IS the feature: the two rosters above answer
   * what SHAPE the rhythm has, and until this state existed they were also the
   * only way to ask how FAST, which meant "cut faster" was a request for a
   * different permutation.
   */
  const [pace, setPace] = useState<PaceId>('even');
  /**
   * THE BEAT — do the cuts snap to the music? See lib/beat.ts.
   *
   * TWO pieces of state, and the split is the feature: `sync` is the user's
   * INTENT and rides the composition code, because "this one cuts on the beat"
   * is a recipe somebody can rebuild with their own track. `beatGrid` is what
   * this particular FILE turned out to be, is measured rather than chosen, and
   * rides nothing at all — the same line the title and the fade sit on.
   *
   * The intent survives a track being removed and replaced, which is what makes
   * swapping the music under a synced collage a one-step act.
   */
  const [sync, setSync] = useState<SyncId>('off');
  const [beatGrid, setBeatGrid] = useState<BeatGrid | null>(null);
  /** True while the decode/analysis is running, so the chip can say so. */
  const [beatBusy, setBeatBusy] = useState(false);
  /** The url of the track a running analysis belongs to — see `analyseBeat`. */
  const beatTrackRef = useRef<string | null>(null);
  const [bgColor, setBgColor] = useState('#050505'); 
  const [avgColor, setAvgColor] = useState<{r:number, g:number, b:number} | null>(null); 

  // --- THE TITLE ------------------------------------------------------------
  // CONTENT, not a parameter — which is why it lives here and not in the roll.
  // It travels in a saved project and in the SVG manifest (both carry the whole
  // AppState) and deliberately NOT in the composition code: a code is a recipe
  // that anyone can open with their OWN photographs, and somebody else's
  // caption over your pictures is not the same collage.
  const [titleText, setTitleText] = useState('');
  const [captions, setCaptions] = useState<CaptionTrack>(EMPTY_CAPTION_TRACK);
  const [captionTake, setCaptionTake] = useState(10);
  const [captionRecording, setCaptionRecording] = useState(false);
  const [captionPanel, setCaptionPanel] = useState(false);
  const [demoBusy, setDemoBusy] = useState(false);
  // The sample awaits both image encoding and staged decoding. Ref gates are
  // synchronous, so another entrypoint cannot race React's next paint.
  const demoBusyRef = useRef(false);
  const projectReadBusyRef = useRef(0);
  const imageCountRef = useRef(images.length);
  imageCountRef.current = images.length;
  const [titlePlace, setTitlePlace] = useState<TitlePlace>('bl');
  const [titleSize, setTitleSize] = useState<TitleSize>('md');
  /** THE LOOK — the colour grade over every fragment. See lib/grade.ts. */
  const [look, setLook] = useState<LookId>('none');
  /**
   * THE DESK — the grade as four axes, once the user has moved one off the
   * preset. `null` means the look above IS the grade, which is every state this
   * app could reach before the desk existed.
   *
   * IT IS NORMALISED, not merely stored: `applyDesk` writes `null` back the
   * moment the axes match the preset's own, so "is this a custom grade" is one
   * comparison rather than a flag that can disagree with the picture. That is
   * what keeps the chip row honest (CUSTOM lights only when the pixels differ
   * from the preset) and what keeps a code minted from an untouched desk
   * byte-identical to the code this app has minted since THE BEAT.
   */
  const [adjust, setAdjust] = useState<Desk | null>(null);
  /** The four axes as the sliders should show them: the desk, or the preset's. */
  const deskShown = useMemo(() => adjust ?? deskForLook(look), [adjust, look]);
  /** The grade actually in force — what every surface that paints is handed. */
  const lookRef = useMemo<LookRef>(() => (adjust ? gradeFromDesk(adjust) : look), [adjust, look]);
  const applyDesk = useCallback((next: Desk) => {
    const snapped = snapDesk(next);
    setAdjust(sameDesk(snapped, deskForLook(look)) ? null : snapped);
  }, [look]);
  
  /** Name of the recipe the last dice roll drew from, shown in the readout. */
  const [lastRecipe, setLastRecipe] = useState<string | undefined>(undefined);

  const [lockedCells, setLockedCells] = useState<Map<number, string>>(new Map());

  /**
   * THE FRAGMENT UNDER YOUR THUMB IN FULL BLEED — index into `layoutItems`, or
   * null when nothing is armed.
   *
   * From the field: *"when full mode is active if I click a box or segment there
   * should be ability to remove that from the group of images displayed or
   * videos."* You maximize to COMPARE, which is exactly when you find the one
   * photograph wrecking every roll — and the only way to get rid of it was to
   * leave full bleed, Clear the whole pool and re-import everything minus one.
   *
   * WHY A TAP ARMS INSTEAD OF ACTING. A fragment now has TWO things that can be
   * done to it, and a bare tap cannot mean both. Outside full bleed the tap
   * still toggles the pin, byte for byte — that is the shipped gesture and an
   * e2e drives it. Inside full bleed the tap shows what is possible, which is
   * literally what was asked for ("there should be ABILITY to remove"), and it
   * also puts a LABEL on a pin control that until now no one could discover
   * except by pressing the picture and seeing what happened.
   *
   * It clears on leaving full bleed and whenever the partition changes: an index
   * into a layout that has been replaced points at a different fragment, and a
   * remove button floating over the wrong one is the worst bug this feature has.
   */
  const [armedCell, setArmedCell] = useState<number | null>(null);
  /**
   * THE REFRAME — hand-set crops, keyed by ASSET ID and never by slot.
   *
   * A frame is a property of the PHOTOGRAPH (see lib/reframe.ts), so it has to
   * survive a shuffle, a re-deal, a swap and a turn — all four of which move
   * pictures between fragments. Keyed by slot it would be undone by the next
   * roll, and rolling is what this app is for.
   *
   * Deliberately NOT in `lockedCells`' family: a pin is a preference about
   * FUTURE rolls and a frame is a correction to one picture, so a reframed
   * fragment is not pinned and a re-deal is free to move it elsewhere with its
   * correction intact.
   */
  const [frames, setFrames] = useState<Map<string, Frame>>(new Map());
  /**
   * THE SWAP'S SECOND TAP.
   *
   * A trade needs two fragments and a tap can only name one, so the Swap button
   * parks the FIRST here and the next tap on the canvas names the second. Null
   * means the canvas is doing what it has always done (arm, or pin outside full
   * bleed); a number means every fragment is a destination and the next tap
   * completes or cancels. Cleared by the same effect that clears the arming,
   * for the same reason: a cell index outlives the partition it was taken from.
   */
  const [swapFrom, setSwapFrom] = useState<number | null>(null);
  /**
   * UNDO — what is behind the composition on screen, and what is ahead of it.
   * Reported from the field: rolling the dice in full bleed to compare layouts
   * destroys the one before it, and there was no way back. See
   * `lib/compositionHistory.ts` for what counts as a step and why.
   */
  const [history, setHistory] = useState<CompositionHistory>(emptyHistory);
  const [shuffledIndices, setShuffledIndices] = useState<number[]>([]); 
  const [shuffleTrigger, setShuffleTrigger] = useState(0);
  /**
   * FORCE THE ASSIGNMENT TO RE-DERIVE ITSELF FROM THE PINS.
   *
   * Not a second shuffle: `shuffleTrigger` feeds the RNG and re-deals, this
   * does not feed anything. It exists because the assignment is DERIVED from
   * (pool, count, layout, aspect, seed, shuffle, arrangement) + the pins, and
   * the PINS are not in that dependency list — deliberately, because toggling
   * a pin is a preference about FUTURE rolls and must not disturb the deal on
   * screen.
   *
   * That is exactly right for a pin and exactly wrong for an UNDO. A step
   * restores the composition code AND the pins; a swap changes neither of the
   * code's fields, so every setter in `applyCompositionCode` writes back an
   * identical value, React bails out, the effect never runs — and Undo reverted
   * the pins while leaving the PICTURES traded. Measured before it was fixed
   * (swap.spec T6): 285 RGB away from the picture Undo claimed to restore. An
   * Undo that visibly does nothing is worse than no Undo, because it looks like
   * one.
   *
   * SAFE TO FIRE ON EVERY RESTORE, and that is why it is a nonce rather than a
   * special case for swaps: the bag is seed-deterministic, so re-deriving with
   * the same inputs reproduces the same deal exactly, and re-deriving with
   * DIFFERENT pins reproduces the deal those pins imply — which is the thing
   * being restored. The effect's own comment already prices it: "a recompute
   * that changes nothing costs one O(n log n) pass on n <= ~300".
   */
  const [assignNonce, setAssignNonce] = useState(0);

  const [layoutItems, setLayoutItems] = useState<LayoutItem[]>([]);
  const [isLayoutComputing, setIsLayoutComputing] = useState(false);

  /**
   * A CELL INDEX IS ONLY MEANINGFUL AGAINST THE PARTITION IT WAS TAKEN FROM.
   * Roll, remix, shuffle or change the count while a fragment is armed and index
   * 7 is now somewhere else entirely — so the arming does not survive a new
   * layout, or leaving full bleed. Cheap, and it forecloses the one bug that
   * would make this feature worse than not having it: a Remove button sitting
   * over a picture other than the one it would delete.
   */
  useEffect(() => { setArmedCell(null); setSwapFrom(null); }, [layoutItems, maximized, shuffledIndices]);

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
  // Restore in flight. The first cut cleared the banner on tap and then worked
  // silently — so a slow restore looked like a button that did nothing, which is
  // half of what "glitching" meant in the report. The card now stays and says
  // what it is doing, and the tap cannot be fired twice.
  const [restoring, setRestoring] = useState(false);
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
  useLayoutEffect(() => { measureBand(bandElRef.current); }, [maximized, studioTool, stageDetailsOpen, captionPanel, activeTab, measureBand]);

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

  // All chrome is outside the measured stage. Fit the entire composition to
  // the actual available box, including after inspector and preview changes.
  const artFit = useMemo(() => {
    if (!artBand || artBand.w < 1 || artBand.h < 1) return null;
    const w = Math.min(artBand.w, artBand.h * aspect);
    return { w: Math.floor(w), h: Math.floor(w / aspect) };
  }, [artBand, aspect]);

  /**
   * Never strand anyone in expanded preview. Its return control
   * lives beside the stage, and the stage only renders while there are images, so an
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
  // The keydown handler is a mount-once effect, so Escape reads the pending
  // trade the same way it reads everything else there: through a mirror.
  const swapFromRef = useRef<number | null>(null);
  swapFromRef.current = swapFrom;
  /** A trade is pending. Full-bleed only, exactly like the arming it extends. */
  const swapping = maximized && swapFrom !== null;

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
    const target = maximized ? exitBtnRef.current
      : maxBtnRef.current?.getClientRects().length ? maxBtnRef.current : inspectorCloseRef.current;
    target?.focus();
  }, [maximized]);

  const isMobile = useMemo(() => /iPhone|iPad|iPod|Android/i.test(navigator.userAgent), []);

  /**
   * F toggles expanded preview unless a field owns that letter. Escape closes
   * the innermost editing view, including from a focused field. Open dialogs
   * own their dismissal, so the shortcut never closes two views at once.
   */
  useEffect(() => {
    /**
     * WHICH FOCUSED CONTROLS OWN Cmd-Z, AND WHICH ONLY LOOK LIKE THEY DO.
     *
     * The letter shortcuts below bail on ANY focused field, which is right for
     * them — `f` is a character. Cmd-Z is different: only a control with TEXT
     * IN IT has its own undo to defend. A range slider, a colour swatch, a
     * checkbox and the file input are all `<input>` and none of them owns the
     * chord, so the broad test would have swallowed undo for the rest of the
     * session after any slider drag — silently, since a dead shortcut looks
     * exactly like a shortcut you imagined.
     *
     * Found by the WebKit run, not by reading: Mobile Safari leaves focus on
     * the file input after an upload, so U5 failed on the phone engine and
     * passed everywhere else.
     */
    const isTextEntry = (t: HTMLElement | null): boolean => {
      if (!t) return false;
      if (t.isContentEditable || t.tagName === 'TEXTAREA') return true;
      if (t.tagName !== 'INPUT') return false;
      const type = ((t as HTMLInputElement).type || 'text').toLowerCase();
      return /^(text|search|url|email|password|tel|number)$/.test(type);
    };

    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
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
      // UNDO / REDO, on the shortcut every other application on the machine
      // uses. Both spellings of redo, because Shift-Cmd-Z is the Mac one and
      // Ctrl-Y is the Windows one and a person reaches for whichever their
      // hands already know.
      if ((e.metaKey || e.ctrlKey) && !e.altKey && !isTextEntry(t)) {
        const k = e.key.toLowerCase();
        if (k === 'z' || (k === 'y' && !e.shiftKey)) {
          const go = k === 'y' || e.shiftKey ? undoRef.current.handleRedo : undoRef.current.handleUndo;
          const live = k === 'y' || e.shiftKey ? undoRef.current.canRedo : undoRef.current.canUndo;
          // Swallow the key either way once it is ours: letting a dead Cmd-Z
          // fall through to the browser's own undo would leave the page's form
          // state stepping backwards behind a collage that did not move.
          e.preventDefault();
          if (live) go();
          return;
        }
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.defaultPrevented) return;
      // Escape closes the current view even when a range or text field has
      // focus. Native select popups keep it for their own dismissal.
      if (e.key === 'Escape' && t?.tagName !== 'SELECT') {
        // A pending trade is the innermost thing Escape can back out of, and
        // backing out of it must NOT also drop full bleed — you cancel a
        // mis-tap to try again, not to leave the room you are comparing in.
        if (swapFromRef.current !== null) { setSwapFrom(null); return; }
        if (maximizedRef.current) { setMaximized(false); return; }
        const tool = studioToolRef.current;
        if (tool) { restoreToolFocusRef.current = tool; setStudioTool(null); }
        return;
      }
      if (t && (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable)) return;
      // Nothing to maximize with an empty pool — F used to hide the whole UI
      // and leave the drop target alone on a black page.
      if (e.key === 'f' || e.key === 'F') {
        if (!canMaximizeRef.current) return;
        // Keep the current composition view stable while a take is recording.
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
    // `assignNonce` re-derives the assignment from the pins WITHOUT re-dealing —
    // see its declaration. It is what makes Undo reach a swap.
  }, [images, effectiveCount, layoutItems, aspect, seed, shuffleTrigger, arrangement, assignNonce]);

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
        // THE REFRAME goes INNERMOST — it is a fact about the photograph, so
        // it is applied before the three decorations that are facts about the
        // fragment. `withReframe` hands the same object back when nobody has
        // dragged this picture, so the default path allocates nothing.
        const raw = images[idx];
        return withMove(withTwist(withFocus(withReframe(raw, raw ? frames.get(raw.id) : undefined), focus, slotSeed), twist, slotSeed, cell), move, cell);
      });
    },
    [shuffledIndices, images, focus, twist, move, seed, layoutItems, aspect, frames],
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
  /**
   * THE TURN'S ONE SEAM WITH THE COMPOSITOR.
   *
   * "Give me the photograph that BELONGS to `fromSlot`, decorated for being
   * drawn in `slot`'s fragment." The split is the whole point: the FACE and the
   * COLOUR are properties of the photograph and travel with it, while the
   * FOCUS, the TWIST and the MOVE are properties of the fragment and stay put —
   * which is why this is the same expression `orderedAssets` maps, with the
   * picture index taken from one slot and every geometric argument from the
   * other. Identity is answered from `orderedAssets` directly, so turn 0 is
   * bit-identical to the deal every still surface draws.
   *
   * A CALLBACK, not a table: the Stage asks only at a turn boundary, a few
   * dozen times a minute, and the number of turns in a preview is unbounded.
   */
  const turnResolve = useCallback((slot: number, fromSlot: number) => {
    if (slot === fromSlot) return orderedAssets[slot] ?? null;
    const idx = shuffledIndices[fromSlot];
    const raw = images[idx];
    if (!raw) return null;
    // The reframe travels with the picture, which is the whole reason it is
    // keyed by asset id: a turn hands slot `slot` the photograph that belongs
    // to `fromSlot`, and it must arrive wearing its own correction.
    const img = withReframe(raw, frames.get(raw.id));
    const H = PREVIEW_W / aspect;
    const slotSeed = (seed ^ (slot * 2654435761)) | 0;
    const b = layoutItems[slot]?.bounds;
    const cell = b && b.w > 0 && b.h > 0
      ? { cx: (b.x + b.w / 2) / PREVIEW_W, cy: (b.y + b.h / 2) / H, area: (b.w * b.h) / (PREVIEW_W * H) }
      : null;
    return withMove(withTwist(withFocus(img, focus, slotSeed), twist, slotSeed, cell), move, cell);
  }, [orderedAssets, shuffledIndices, images, focus, twist, move, seed, layoutItems, aspect, frames]);

  /** THE TURN needs at least two photographic fragments to exchange anything. */
  const turning = isTurning(turn) && images.length > 1;

  /**
   * MEMOISED, AND THAT IS NOT AN OPTIMISATION.
   *
   * This object is a DEPENDENCY of VideoStage's scene effect, and `setScene`
   * ends by resetting `moveOriginMs` to -1 — the take's clock origin. Built
   * inline in the JSX it would be a fresh object on every App render, so any
   * unrelated state change (a notice, a hover, the autosave tick) would rebuild
   * the scene and RESTART THE TAKE, which for a schedule keyed on elapsed time
   * means the turn is perpetually inside its first hold and never fires at all.
   * Every other entry in that dep array is a primitive or a `useMemo` for
   * exactly this reason — VideoStage's own comment says so about the
   * soundtrack. Found by an adversarial audit; three lenses reached it.
   */
  const turnScene = useMemo(
    () => (turning ? { id: turn, seed, resolve: turnResolve } : null),
    [turning, turn, seed, turnResolve],
  );

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
  // ...AND A TURN IS A MOVING PICTURE TOO. A collage of photographs that
  // re-cuts every few seconds is exactly the case the still path cannot show —
  // it draws one frame — so it joins the terms that claim the live surface, for
  // the same reason THE MOVE did.
  const liveMode = images.length > 0 && (clips.length > 0 || moving || turning || !!soundtrack || captions.cues.length > 0 || images.some(i => i.art && artIsAnimated(i.art))) && stageOk;

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

  // Measure once; every video frame and still export scales this same plan.
  const captionPlans = useMemo(() => {
    const ctx = measureCanvasRef.current;
    return ctx ? planCaptions(captions, aspect, measureWith(ctx)) : [];
  }, [captions, aspect, titlePlan]);
  // Still formats show the opening frame. Active lyrics replace the static title.
  const frameTitlePlan = captionPlanAt(captionPlans, 0) ?? titlePlan;

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
         const canvas = await renderCanvas(PREVIEW_W, aspect, layoutMode, layoutItems, orderedPreviews, seed, zoom, bgColor, frameTitlePlan, lookRef);
         canvas.toBlob(blob => {
             if (previewUrl) URL.revokeObjectURL(previewUrl);
             if (blob) setPreviewUrl(URL.createObjectURL(blob));
         }, 'image/jpeg', 0.85);
       } catch (e) { console.error("Render failed", e); }
    };
    const t = setTimeout(runRender, 50);
    return () => clearTimeout(t);
  }, [images, layoutItems, shuffledIndices, orderedAssets, seed, zoom, bgColor, liveMode, frameTitlePlan, lookRef]);

  const handleShuffle = () => { if (waitForLyricDemo()) return; pushHistory(); setShuffleTrigger(prev => prev + 1); };
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
   *
   * THE FRAME HOLD is the one opt-out: with `holdFrame` on, the roll keeps the
   * shape of frame on screen and re-deals everything else. See the state's
   * own note.
   */
  const handleDice = () => {
    if (waitForLyricDemo()) return;
    // Every press of this button used to destroy the picture before it. Record
    // what is on screen FIRST — `compositionCode` is still this render's, i.e.
    // the composition about to be replaced.
    pushHistory();
    // `distinctSourceCount`, never `images.length` — the ONE definition of "how
    // many things did you send" (fill.ts), the same one the import snaps the
    // count to. A second answer here would put the roll's ceiling ten times too
    // high on a project made of video, whose frames outnumber its clips.
    // `density` goes in too: what the readout calls FRAGMENTS is `count *
    // density`, and this button does not roll density (see below), so a ceiling
    // written on `count` alone would be a cap on a number nobody is reading.
    const roll = rollDice({
      hasVideo: clips.length > 0,
      sources: distinctSourceCount(images),
      density,
    });
    // The dice chooses an explicit fragment count; don't let the next upload
    // silently overwrite a composition the user rolled on purpose.
    ownCount(true);
    // This roll supersedes any count a link was still holding for a drop.
    pendingCountRef.current = null;
    setLayoutMode(roll.layout);
    setCount(roll.count);
    setEntropy(roll.entropy);
    // THE FRAME HOLD lands HERE, not in `rollDice({ locks: ['aspect'] })`: the
    // engine's lock copies `previous.aspect`, which is the last ROLL — but the
    // Canvas chips may have re-set the frame since, and the `aspect` state is
    // the one truth of what is on screen. Skipping the setter also leaves the
    // roll's rnd stream untouched, so a held roll and a free roll differ in
    // nothing but the frame — and OFF stays byte-identical to the old dice.
    if (!holdFrame) setAspect(roll.aspect);
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
    // AND IT DROPS A CUSTOM GRADE, because the dice deal a ROSTER and a roster
    // pick is the whole point of a die. A roll is a destructive composition
    // event like the shuffle and the remix, so it is already on the undo stack
    // — the axes you set come back with one press rather than being defended
    // here, which would make the dice unable to change the look at all.
    setAdjust(roll.desk ?? null);
    // And the move is part of it for the third time and the same reason — a
    // collage that drifts is not the same picture as one that sits still.
    moveOwnedRef.current = true;   // a roll is a choice, even when it rolls STILL
    setMove(roll.move ?? 'still');
    setTurn(roll.turn ?? 'hold');
    // And the pace, for the fourth time and the same reason: the same shapes on
    // a different clock is a different piece of film.
    setPace(roll.pace ?? 'even');
    // AND THE BEAT IS DELIBERATELY NOT TOUCHED — the one field of the roll this
    // button leaves alone. Every line above re-deals what the collage LOOKS
    // like; `sync` is a relationship to a FILE the dice cannot see, and a roll
    // that silently unsynced a wall somebody had just locked to their track
    // would be undoing a decision the button was never asked about. `rollDice`
    // emits no `sync` for the same reason, so there is nothing here to apply.
    setLastRecipe(roll.recipe);
    setLockedCells(new Map());
    // The deal is part of the composition and the roll re-deals it; leaving the
    // old shuffle count on would make the SAME code describe two pictures.
    setShuffleTrigger(0);
  };

  /**
   * THE COLOUR DICE — roll the colour sorting and the crop, KEEP the layout.
   *
   * Wished for (wishing well, collage/layout): *"Add another dice for color
   * sorting and cropping style. For full view for better ui/ux."*
   *
   * The dice above is all-or-nothing: it is worth pressing precisely because it
   * replaces everything, and useless the moment you like the shape on screen.
   * Until now the only route to a different colour sort was to roll the shape
   * away with it, or to leave full bleed, open Advanced and scroll thirty-two
   * chips — which on a phone is not a control that exists.
   *
   * WHAT IT DOES NOT TOUCH is the whole point, and `seed` is the one to watch:
   * the seed drives the subdivision, so rolling it would move every fragment
   * edge and this button would quietly be the first dice again. Layout, count,
   * entropy, aspect, gutter, background, look, move and the title all stay
   * exactly where they are.
   *
   * `shuffleTrigger` stays too — an arrangement is a re-ordering of the SAME
   * bag, so re-dealing underneath it would change which photo lands where for a
   * reason the button did not claim. And the locks survive: they pin cells of a
   * layout that is not being replaced, which is exactly the case `handleDice`
   * has to release them for and this one does not.
   *
   * The roll is guaranteed to differ from what is on screen — see
   * `lib/dealRoll.ts` and its sweep. A dice that hands back the picture you are
   * already looking at is a broken button.
   */
  const handleColourDice = () => {
    if (waitForLyricDemo()) return;
    pushHistory();
    const deal = rollDeal({ layout: layoutMode, previous: { arrangement, focus, twist } });
    setArrangement(deal.arrangement);
    setFocus(deal.focus);
    setTwist(deal.twist);
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
    bgColor, seed, arrangement, focus, twist, look, adjust, move, turn, pace, sync, shuffle: shuffleTrigger,
    countOwned,
  }), [layoutMode, primitive, count, density, entropy, aspect, gutter,
       bgColor, seed, arrangement, focus, twist, look, adjust, move, turn, pace, sync, shuffleTrigger, countOwned]);

  /**
   * THE BEAT'S SCHEDULE — the turn's own hold, snapped to the music.
   *
   * The TARGET is the mode's hold DIVIDED BY THE PACE, which is the whole
   * reason a beat sync did not need a rate control of its own: the pace already
   * says "cut half again as often", the mode already says what a cut IS, and
   * this only decides which musical multiple lands nearest what those two asked
   * for. `paceTime` scales the CLOCK, so the hold a rate `r` expresses is
   * `hold / r` — dividing here is reading the pace in the units this question
   * is asked in, not a second interpretation of it.
   *
   * Null whenever anything is missing — no intent, no music, no grid, or a turn
   * mode that does not cut — and null is exactly what the Stage had before this
   * feature existed, so an unsynced collage takes the byte-identical path.
   */
  const beatSched = useMemo(() => {
    if (!isSynced(sync) || !soundtrack || !beatGrid) return null;
    const hold = turnHoldSec(turn);
    if (!(hold > 0)) return null;
    return beatSchedule(beatGrid, hold / (paceRate(pace) || 1), soundtrack.inSec ?? 0);
  }, [sync, soundtrack, beatGrid, turn, pace]);

  /**
   * Apply a pasted code. Returns false when it is not one, so the caller can
   * say so instead of silently doing nothing — a half-applied composition on
   * top of the one already on screen is worse than a refusal, because you
   * cannot tell which half moved.
   */
  const applyCompositionCode = (code: string, record = true): boolean => {
    if (waitForLyricDemo()) return false;
    const s = decodeState(code);
    if (!s) return false;
    // Pasting a code replaces the whole composition, which is the same kind of
    // event as a roll and gets the same way back. Recorded only when it is a
    // REPLACEMENT: the boot code and an undo are both applications of a code
    // that must not become steps of their own — the first because there is
    // nothing behind it worth returning to, the second because it IS the return.
    if (record) pushHistory();
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
    // A code with no desk group is a code for one of the eight, so this CLEARS
    // any custom grade on screen rather than leaving it layered under somebody
    // else's recipe — an applied code is the whole composition or it is nothing.
    setAdjust(s.adjust);
    setSeed(s.seed);
    setArrangement(s.arrangement);
    setFocus(s.focus);
    setTwist(s.twist);
    setMove(s.move);
    setTurn(s.turn);
    setPace(s.pace);
    setSync(s.sync);
    setShuffleTrigger(s.shuffle);
    // Fragments pinned by hand refer to cells of the layout that is being
    // replaced, so they cannot survive the change any more than they survive a
    // roll. The recipe name belonged to a roll this session did not make.
    setLockedCells(new Map());
    setLastRecipe(undefined);
    return true;
  };

  // ===========================================================================
  // UNDO — the roll you liked, brought back.
  //
  // Reported from the field (wishing well, collage/layout): *"Need an undo
  // button for quick recall … rolling the dice in full view."* Full bleed puts
  // the dice under your thumb so you can roll repeatedly and compare — and
  // every press destroyed the picture before it.
  //
  // The composition code already IS a complete, round-trip-exact serialisation
  // of everything except the photographs, so a step costs a short string plus
  // the two things a code deliberately omits (the fragments you pinned by hand
  // and the recipe name). The stack itself is pure and swept against a
  // reference model — see `lib/compositionHistory.ts`.
  // ===========================================================================

  /**
   * The composition on screen RIGHT NOW.
   *
   * `compositionCode` is a `useMemo` over the state of this render, so inside a
   * click handler it is still the PRE-action composition — which is precisely
   * what a step needs to record. The state the button is about to produce does
   * not exist yet and cannot be captured here; nothing needs it to be.
   */
  const liveSnapshot = (): CompositionSnapshot => ({
    code: compositionCode,
    locks: Array.from(lockedCells.entries()),
    recipe: lastRecipe,
  });

  /** Record the composition that is on screen, immediately before something replaces it. */
  const pushHistory = () => setHistory(h => commitHistory(h, liveSnapshot()));

  /**
   * Put a recorded composition back on screen.
   *
   * `applyCompositionCode` clears the locks and the recipe name on purpose —
   * a code arriving from somebody else cannot carry either. An undo is not
   * somebody else, so they are put back after it, in the same batch.
   */
  const restoreSnapshot = (s: CompositionSnapshot) => {
    applyCompositionCode(s.code, false);
    setLockedCells(new Map(s.locks));
    setLastRecipe(s.recipe);
    // The pins are half of what decides the deal and they are NOT a dependency
    // of the assignment effect (a pin is a preference about future rolls). So a
    // restore has to say "re-derive" out loud, or an undo whose code fields are
    // unchanged — every swap — reverts the pins and leaves the pictures put.
    setAssignNonce((n) => n + 1);
  };

  const canUndo = histCanUndo(history);
  const canRedo = histCanRedo(history);

  const handleUndo = () => {
    const step = undoHistory(history, liveSnapshot());
    if (!step) return;
    setHistory(step.history);
    restoreSnapshot(step.restore);
  };

  const handleRedo = () => {
    const step = redoHistory(history, liveSnapshot());
    if (!step) return;
    setHistory(step.history);
    restoreSnapshot(step.restore);
  };

  /**
   * The keyboard listener below is bound once, on purpose, so it cannot close
   * over this render's handlers. Everything it needs rides through a ref.
   */
  const undoRef = useRef({ canUndo, canRedo, handleUndo, handleRedo });
  undoRef.current = { canUndo, canRedo, handleUndo, handleRedo };

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
    // `record: false` — a link opens the composition it names, and there is
    // nothing behind it to go back to. Recording it would put the app's own
    // cold-start default in the undo stack as if it were a picture you made.
    if (boot && !applyCompositionCode(boot, false)) {
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
      if (waitForLyricDemo()) return;
      // Recorded BEFORE the await: a remix re-rolls the seed and re-grafts the
      // pinned fragments onto a new layout, and both the seed and the pins are
      // in the snapshot. Doing it after would capture a composition the layout
      // computation had already started replacing.
      pushHistory();
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

  // --- THE REFRAME'S GESTURE ------------------------------------------------
  //
  // DRAG THE ARMED FRAGMENT'S PICTURE. Arming already exists and already means
  // "this is the fragment I am talking about", so the reframe needs no mode and
  // no fourth verb on the puck to enter — only a Recentre verb to leave, and
  // that one appears only on a picture somebody actually moved.
  //
  // WHY THE ARMED ONE AND NOT ANY FRAGMENT. Outside full bleed a tap PINS, and
  // a drag that begins as a tap would pin whatever it passed over. Scoping the
  // drag to the armed fragment keeps every shipped gesture byte for byte, and
  // it is what lets `touch-action: none` be scoped too — the overlay only stops
  // the page scrolling while something is armed, which only happens in full
  // bleed, where there is nothing to scroll.
  //
  // A DRAG ACCUMULATES FROM ITS ORIGIN, and that is not a style choice.
  //   The first version asked `calculateSmartCrop` for the CURRENT crop on every
  //   pointermove and applied the delta since the last one. Pointer events fire
  //   faster than React re-renders and `setFrames` is asynchronous, so several
  //   consecutive moves read the SAME stale crop, each one overwriting the last:
  //   a 600px drag arrived as whatever the final 8px event asked for. Measured,
  //   not theorised — reframe.spec T1 dragged the length of a photograph twice
  //   and landed one band from where it started.
  //   So the crop is sampled ONCE at pointerdown and every move maps the TOTAL
  //   displacement onto it. `sw`/`sh`/`dw`/`dh`/`twist` are invariant under a
  //   reframe (that is invariant I7), so the crop taken at the start stays the
  //   right basis for the whole gesture, and the clamp lands on the TOTAL —
  //   which is what makes the edge release on the very first pixel back.
  const REFRAME_SLOP = 5;
  const reframeRef = useRef<{
    pid: number; slot: number; id: string;
    ox: number; oy: number; k: number;
    crop: ReturnType<typeof calculateSmartCrop>;
    size: { width: number; height: number };
    moved: boolean;
  } | null>(null);
  /** A drag ends with a click on the same element; this eats exactly that one. */
  const reframedRef = useRef(false);
  const reframeHintRef = useRef(false);

  const beginReframe = (e: React.PointerEvent<SVGGElement>, slot: number) => {
    if (!maximized || armedCell !== slot) return;
    const rect = e.currentTarget.ownerSVGElement?.getBoundingClientRect();
    if (!rect || !(rect.width > 0) || !(rect.height > 0)) return;
    const imgIdx = shuffledIndices[slot];
    const id = imgIdx === undefined || imgIdx < 0 ? undefined : images[imgIdx]?.id;
    if (!id) return;
    // CLIENT PX -> THE 1200-UNIT BASIS the fragment boxes live in. `max` of the
    // two ratios rather than either alone: `preserveAspectRatio` defaults to
    // meet, so a viewBox that did not match its box would be letterboxed and
    // one of the two ratios would be a lie.
    const k = Math.max(PREVIEW_W / rect.width, PREVIEW_H(aspect, PREVIEW_W) / rect.height);
    const asset = orderedAssets[slot];
    const bounds = layoutItems[slot]?.bounds;
    if (!asset || !bounds || !(asset.width > 0) || !(asset.height > 0)) return;
    // AT REST, deliberately: `calculateSmartCrop`'s time argument is defaulted,
    // where `sampleMove` answers `NO_MOVE` by reference. A drift is a fact about
    // the TAKE; mapping the drag against a moving crop would make the identical
    // gesture land somewhere different depending on which instant you grabbed.
    const size = { width: asset.width, height: asset.height };
    const crop = calculateSmartCrop(bounds, { ...size, analysis: asset.analysis }, zoom);
    reframeRef.current = { pid: e.pointerId, slot, id, ox: e.clientX, oy: e.clientY, k, crop, size, moved: false };
    try { e.currentTarget.setPointerCapture(e.pointerId); } catch { /* capture is a convenience */ }
  };

  const moveReframe = (e: React.PointerEvent<SVGGElement>) => {
    const st = reframeRef.current;
    if (!st || st.pid !== e.pointerId) return;
    const dxc = e.clientX - st.ox;
    const dyc = e.clientY - st.oy;
    if (!st.moved && Math.hypot(dxc, dyc) < REFRAME_SLOP) return;
    st.moved = true;
    const next = dragToFrame(st.crop, st.size, dxc * st.k, dyc * st.k);
    setFrames(prev => { const m = new Map(prev); m.set(st.id, next); return m; });
    e.preventDefault();
  };

  const endReframe = (e: React.PointerEvent<SVGGElement>) => {
    const st = reframeRef.current;
    if (!st || st.pid !== e.pointerId) return;
    reframeRef.current = null;
    try { e.currentTarget.releasePointerCapture(e.pointerId); } catch { /* already gone */ }
    if (st.moved) reframedRef.current = true;
    // AND NOTHING IS WRITTEN INTO THE POOL HERE — measured, not assumed. See
    // lib/reframe.ts: `images` reaches the DISARM effect through `layoutItems`,
    // so a commit on pointerup takes the puck away from under the finger that
    // just let go and a second drag on the same picture becomes impossible.
    // The frame reaches the FILES through `poolForSave` instead.
  };

  // Said ONCE per session, on the first arm: a gesture with no affordance is a
  // gesture nobody finds, and a phone has no hover to teach it with.
  useEffect(() => {
    if (!maximized || armedCell === null || reframeHintRef.current) return;
    reframeHintRef.current = true;
    flashNotice('Drag the picture to move it inside its fragment.');
  }, [maximized, armedCell]);

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
        const analysis = await analyzeImage(img, opts.geometryOnly ? null : globalModel);
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
        if (opts.replaceId && batch.length === 1) {
          const oldId = opts.replaceId, nextId = batch[0].id;
          setImages(prev => prev.map(asset => asset.id === oldId ? batch[0] : asset));
          setLockedCells(prev => new Map([...prev].map(([cell, id]) => [cell, id === oldId ? nextId : id])));
          setFrames(prev => { const next = new Map(prev); const frame = next.get(oldId); next.delete(oldId); if (frame) next.set(nextId, frame); return next; });
          setAssignNonce(n => n + 1);
          // Old snapshots name immutable source ids; keep their layout history
          // and remap the replaced source's pins to its new revision.
          setHistory(h => ({ ...h, past: h.past.map(s => ({ ...s, locks: s.locks.map(([cell,id]) => [cell,id===oldId?nextId:id]) })), future: h.future.map(s => ({ ...s, locks: s.locks.map(([cell,id]) => [cell,id===oldId?nextId:id]) })) }));
        } else setImages(prev => [...prev, ...batch]);
    };

    try {
      let i = 0;
      let bite = FIRST_BITE;
      while (i < files.length) {
          const chunk = files.slice(i, i + bite);
          const results = (await Promise.all(chunk.map(decodeOne))).filter(Boolean) as ImageAsset[];
          if (opts.shouldCommit && !opts.shouldCommit()) {
            for (const asset of results) {
              URL.revokeObjectURL(asset.src);
              if (asset.previewSrc && asset.previewSrc !== asset.src) URL.revokeObjectURL(asset.previewSrc);
            }
            if (track) stepIngest(files.length - i);
            return allNewAssets;
          }
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

  /**
   * Single intake for the picker AND drop. Pictures go in. Videos go in. Music
   * goes under. The one thing that is asked is WHICH BUTTON was pressed.
   *
   * THE WISH (collage well, improve, about_tool=upload): *"Be able to add music
   * or sound without the video. Right now if you use a video for the sound or
   * import audio from video it just imports video… if you're importing audio it
   * should not display the video."*
   *
   * All three file buttons fired one `onChange` that landed here, so this
   * function forgot which one it was and routed on the FILE ALONE: press "Add
   * music", hand it a `.mov`, and `isVideoFile` said "video" — correctly, for a
   * question nobody asked. You asked for a sound and got a rectangle.
   *
   * The ladder itself now lives in `lib/intake.ts` (swept over
   * extension x MIME x intent), because it was ALSO re-spelled inside
   * `tests/unit/soundtrack.invariants.mjs`, and a rule written twice is the
   * drift this repo has already filed two scars about.
   */
  const loadLyricDemo = async () => {
    if (demoBusyRef.current || imageCountRef.current) return;
    if (ingestRef.current.total > 0 || projectReadBusyRef.current > 0) {
      flashNotice('Your media is still opening. Let it finish before starting a sample.');
      return;
    }
    demoBusyRef.current = true;
    setDemoBusy(true);
    try {
      const demo = await createLyricDemo();
      // A real import that arrived while the shapes rendered owns the canvas.
      if (imageCountRef.current) return;
      const loaded = await handleUpload(demo.files, { track: false, geometryOnly: true });
      if (!loaded.length) throw new Error('The sample artwork could not load. Try your own images.');
      // A link supplies a recipe even before any pictures exist. The starter
      // chooses its own complete recipe so a prior count, grade or turn cannot
      // silently deform it; intentionally selected music remains the user's.
      pendingCountRef.current = null;
      ownCount(true); setCount(4); setPrimitive('rect'); setEntropy(0.5);
      setAspect(9 / 16); setLayoutMode('kaleidoscope'); setSeed(500);
      setDensity(1); setGutter(0.006); setBgColor('#101528');
      setShuffleTrigger(0); setArrangement('natural'); setFocus('auto'); setTwist('none');
      setLook('none'); setAdjust(null); setTurn('hold'); setPace('even'); setSync('off');
      setLockedCells(new Map()); setFrames(new Map()); setAssignNonce(n => n + 1); setLastRecipe(undefined);
      setMove('drift'); setTitleText(''); setCaptions(demo.captions);
      setCaptionPanel(true);
      flashNotice('Original shapes, timed words, and motion. Add your music, or replace the artwork with your own.');
    } catch (error) {
      flashNotice(error instanceof Error ? error.message : 'Could not load the sample.');
    } finally { demoBusyRef.current = false; setDemoBusy(false); }
  };

  function waitForLyricDemo(): boolean {
    if (!demoBusyRef.current) return false;
    flashNotice('The sample is still loading. Try that action again when it appears.');
    return true;
  }

  const ingestFiles = (list: File[], intent: IntakeIntent = 'any') => {
      if (!list.length) return;
      if (waitForLyricDemo()) return;
      // EXACTLY ONE BUCKET EACH — now by construction rather than by three
      // filters that had to stay disjoint by hand.
      const { music, video: videos, picture: pics, rejected } = splitIntake(list, intent);

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
      // THE REFUSAL NAMES THE INTENT IT REFUSED UNDER. Under 'music' the only
      // thing that can be rejected is a picture, and telling that person
      // "images, video and music only" would list the very thing they just
      // handed over — a message that reads as a bug in the app rather than as a
      // wrong button.
      if (rejected.length > 0) flashNotice(intent === 'music'
          ? `${rejected.length} file(s) ignored — the music button takes sound or a video to take the sound from.`
          : `${rejected.length} unsupported file(s) ignored — images, video and music only.`);
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
      beatTrackRef.current = url;
      // Revoked HERE rather than inside the updater: a state updater must be a
      // pure function of `prev` (React may call it twice), and `handleClear`
      // already disposes clip urls this way.
      if (soundtrack?.url) URL.revokeObjectURL(soundtrack.url);
      setSoundtrack({ url, name: file.name, durationSec: 0, muted: false });

      /**
       * MUSIC MEANS THE PIECE MOVES — "looping image movement is the default",
       * from the same field report that asked for the range.
       *
       * Adding a soundtrack is the one import that can only mean "this is a
       * video now": a still collage exported with music under it is a photograph
       * with a song stapled to it. So the collage starts moving, and DRIFT is the
       * one that does not fight the music — a single slow camera move across the
       * whole surface, on the same 12-second loop every move here runs on.
       *
       * IT ONLY EVER OVERRIDES THE UNSPOKEN DEFAULT. `'still'` is both the
       * starting value and a real choice, which is exactly why `moveOwnedRef`
       * exists: someone who set STILL, or rolled it, asked for a still collage
       * and adding music does not un-ask it. And the notice SAYS what changed —
       * a control that moves on its own without saying so is the same defect as
       * a control that reads back the wrong state.
       */
      const started = !moveOwnedRef.current && move === 'still' && images.length > 0;
      if (started) setMove('drift');

      // THE NOTICE MUST NOT NAME A CONTROL THAT IS NOT ON SCREEN. With no
      // photographs there is no stage, so there is no dock, no chip and no
      // speaker — the music is adopted and waits, and saying so is the honest
      // version of "press the speaker".
      flashNotice(images.length === 0
          ? `Music: ${file.name} — add photos and it goes under them.`
          : started
            ? `Music: ${file.name} — the collage is drifting now. Press the speaker to hear it.`
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

      void analyseBeat(file, url);
  };

  /**
   * WHAT THIS TRACK'S TEMPO IS — decoded, measured once, kept until the music
   * changes.
   *
   * DECODED AT 8 kHz MONO, WHICH IS THE WHOLE COST DECISION. `decodeAudioData`
   * resamples into the context's own rate, so asking for an 8 kHz context turns
   * a five-minute stereo track from ~106 MB of Float32 into 9.6 MB — on a phone,
   * in a tab that is also holding a decoder per video clip. Nothing above 4 kHz
   * carries tempo: the envelope this feeds is an RMS difference, not a spectrum.
   *
   * IT NEVER BLOCKS THE IMPORT. The soundtrack is adopted and playable before
   * this starts, so a track whose analysis fails, or is still running, is a
   * working soundtrack with no BPM on its chip — the same degradation the
   * duration probe above already has.
   *
   * STALE RESULTS ARE DROPPED BY URL. Picking six songs in ten seconds is a
   * thing people do, and the sixth decode is not guaranteed to land last.
   */
  const analyseBeat = async (file: File, url: string) => {
      setBeatGrid(null);
      setBeatBusy(true);
      try {
          const w = window as unknown as {
              OfflineAudioContext?: new (ch: number, len: number, rate: number) => OfflineAudioContext;
              webkitOfflineAudioContext?: new (ch: number, len: number, rate: number) => OfflineAudioContext;
          };
          const OAC = w.OfflineAudioContext ?? w.webkitOfflineAudioContext;
          if (!OAC) return;
          const RATE = 8000;
          const ctx = new OAC(1, RATE, RATE);
          const bytes = await file.arrayBuffer();
          // The callback form is the fallback Safari still needs; `decodeAudioData`
          // DETACHES the buffer it is handed, so the promise form gets its own
          // slice rather than the one the callback form would find empty.
          const buf: AudioBuffer = await new Promise((ok, no) => {
              try {
                  const p = (ctx as unknown as { decodeAudioData(b: ArrayBuffer): Promise<AudioBuffer> })
                      .decodeAudioData(bytes.slice(0));
                  if (p && typeof p.then === 'function') { p.then(ok, no); return; }
              } catch { /* fall through to the callback form */ }
              (ctx as unknown as {
                  decodeAudioData(b: ArrayBuffer, ok: (x: AudioBuffer) => void, no: (e?: unknown) => void): void;
              }).decodeAudioData(bytes.slice(0), ok, no);
          });
          const rate = buf.sampleRate || RATE;
          const wanted = Math.min(buf.length, Math.ceil(BEAT_ANALYSE_SEC * rate));
          // Channel 0, not a downmix: a beat is not a stereo property, and summing
          // two channels would cost a second pass over every sample to learn the
          // same period.
          const mono = buf.getChannelData(0).subarray(0, wanted);
          const grid = detectBeat(mono, rate);
          // The url is the identity of the track this measurement belongs to, and
          // it is read from a REF rather than from inside a `setSoundtrack`
          // updater — an updater must be a pure function of `prev`, which is the
          // rule this file already states over `adoptSoundtrack`'s revoke.
          if (beatTrackRef.current === url) setBeatGrid(grid);
      } catch {
          /* No grid. The chip says so, and the collage cuts on its own clock. */
      } finally {
          setBeatBusy(false);
      }
  };

  const removeSoundtrack = () => {
      if (soundtrack?.url) URL.revokeObjectURL(soundtrack.url);
      beatTrackRef.current = null;
      setSoundtrack(null);
      setBeatGrid(null);
  };

  /**
   * The intent is carried by the BUTTON, not guessed from the file. It arrives
   * on the input's own `data-intake` attribute so there is exactly one handler
   * and exactly one place that says which input means what — a second handler
   * would be a second copy of this function drifting from the first.
   */
  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files ? Array.from(e.target.files) : [];
    const intent: IntakeIntent = e.target.dataset.intake === 'music' ? 'music' : 'any';
    e.target.value = '';
    ingestFiles(list, intent);
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

  /**
   * THE STATE HALF OF A HISTORY ENTRY, for the two changes that take assets OUT
   * of the pool: Clear, and evicting one source.
   *
   * It was written out inline inside `handleClear`, and the second caller is
   * exactly how a 25-field literal starts drifting: one of them gains `sync` and
   * the other does not, and a restored entry silently loses a setting. One copy,
   * two callers.
   */
  const poolSnapshotState = (): AppState => buildStateForSave();

  /**
   * THROW ONE SOURCE OUT OF THE POOL — the fragment you are pointing at.
   *
   * THE WISH (collage well, improve, about_tool=upload): *"when full mode is
   * active if I click a box or segment there should be ability to remove that
   * from the group of images displayed or videos."*
   *
   * WHAT LEAVES is decided by `lib/evict.ts` and nothing else (swept over 400
   * pools): a photograph leaves alone, a frame of a clip takes the whole clip
   * and its other frames with it, because `assignSources` already defines a
   * video as ONE source however many frames came out of it — and evicting a
   * single poster would put the clip you just deleted back on screen at the next
   * roll, wearing a different second.
   *
   * IT IS RECOVERABLE, and not through the rail's Undo: that Undo restores
   * COMPOSITIONS (`compositionHistory` holds a code and the pins, never the
   * pool), so an eviction it "restored" would come back with the asset still
   * gone — worse than no undo at all, because it would look like one. The pool
   * before the removal goes where `handleClear` already puts it: the session
   * History in Advanced, which restores images.
   */
  const evictSource = (cellIndex: number) => {
      if (recorderRef.current?.isRecording) { flashNotice('Stop the take before removing a source.'); return; }
      const imgIdx = shuffledIndices[cellIndex];
      const target = imgIdx === undefined || imgIdx < 0 ? undefined : images[imgIdx];
      const plan = planEviction(images, clips, target?.id);
      // An empty plan is a cell holding nothing, or a `shuffledIndices` entry
      // that went stale under a re-layout. Silence is the right answer to both.
      if (plan.count === 0) { setArmedCell(null); return; }

      addToHistory(poolSnapshotState(), images, previewUrl || undefined);

      const gone = new Set(plan.imageIds);
      if (plan.clipIds.length) {
          for (const id of plan.clipIds) {
              const c = clips.find(x => x.id === id);
              if (c) { try { URL.revokeObjectURL(c.url); } catch { /* already gone */ } }
          }
          setClips(prev => prev.filter(c => !plan.clipIds.includes(c.id)));
      }
      setImages(prev => prev.filter(a => !gone.has(a.id)));
      // A lock pins a CELL to an ASSET ID. Leaving a pin that names a departed
      // asset is not inert: `handleRemix` carries every pin onto the new layout
      // and the assignment pass re-reads them forever, so a pool of ten could
      // still be dragging pins for photographs deleted an hour ago.
      setLockedCells(prev => {
          let touched = false;
          const next = new Map(prev);
          prev.forEach((imgId, cell) => { if (gone.has(imgId)) { next.delete(cell); touched = true; } });
          return touched ? next : prev;
      });
      setArmedCell(null);
      flashNotice(describeEviction(plan));
  };

  /**
   * THE SWAP — two fragments trade pictures.
   *
   * The ladder has named this since the timeline rung was opened
   * ("drag-reorder … direct manipulation of the SOURCES rather than of the
   * clock"). A collage has no timeline to drag along, so the gesture a collage
   * has is a TRADE: the armed fragment's Swap button parks it, and the next tap
   * on the canvas names its partner.
   *
   * WHAT MOVES is decided by `lib/swap.ts` and nothing else (675k assertions
   * over 49k slot pairs, four mutants dead), and it is TWO things that have to
   * agree:
   *
   *   1. the ASSIGNMENT — `shuffledIndices` is the one seam every render path
   *      reads (`orderedAssets` → preview, Stage, video export, raster export,
   *      SVG), so transposing two entries reaches all five and the partition
   *      does not move: the fragment keeps its shape, focus, twist and lean,
   *      because those are properties of the FRAGMENT, not of the photograph.
   *
   *   2. the PINS — and this is the half that is not obvious.
   *      `shuffledIndices` is DERIVED: the assignment effect recomputes it from
   *      nine inputs, and `layoutItems` alone re-runs on a gutter nudge. A swap
   *      written only into the indices would be silently undone by the next
   *      touch of any of them — and worse, a pin already sitting on one of the
   *      two cells would drag its old picture back and leave HALF a trade,
   *      which is a duplicate on screen. So both cells are re-pinned to what
   *      they now hold, which is exactly what the assignment pass reads back.
   *      The mutant that skips it fails 162,521 assertions in the sweep.
   *
   * IT IS RECOVERABLE through the rail's Undo — but that took a second fix, and
   * the first version of this comment asserted it wrongly. A step records the
   * composition code AND the pins, and the pins ARE where a swap lives; what
   * that misses is that `applyCompositionCode` writes back identical values
   * when only a swap has happened, React bails out, and the assignment effect
   * never re-derives. The pins reverted and the pictures stayed traded — 285
   * RGB from the picture Undo claimed to restore, measured by writing
   * swap.spec T6 as a failing test first. `assignNonce` closes it; see its
   * declaration. Unlike an eviction, which the pool History has to carry.
   */
  const performSwap = (toCell: number) => {
      const fromCell = swapFrom;
      if (fromCell === null) return;
      // Tapping the parked fragment again is CANCEL. It is NOT the only way out
      // and must not be treated as one: the pending pill is positioned ON that
      // fragment's centroid, so on a small fragment the pill covers the very
      // area you would tap. Found by the WebKit and Mobile Chrome runs of
      // swap.spec T4, where a centre-of-fragment tap landed on the pill instead.
      // The guaranteed outs are the pill's own X (a 44 px target, right there)
      // and Escape; this one is the convenience for a fragment big enough to
      // have an edge showing.
      if (toCell === fromCell) { setSwapFrom(null); return; }
      if (recorderRef.current?.isRecording) { flashNotice('Stop the take before trading fragments.'); return; }

      const plan = planSwap(images, shuffledIndices, Array.from(lockedCells.entries()), fromCell, toCell);
      if (!plan.ok) {
          // A refusal that a hand can cause is SAID; a stale cell index is
          // silence, because the partition it named has already been replaced.
          const why = describeSwap(plan);
          if (why) flashNotice(why);
          setSwapFrom(null);
          return;
      }

      // One step for the pair, recorded before either half lands.
      pushHistory();
      setShuffledIndices(plan.indices);
      setLockedCells(new Map(plan.locks));
      setSwapFrom(null);
      flashNotice(describeSwap(plan));
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
      if (waitForLyricDemo()) return;
      addToHistory(poolSnapshotState(), images, previewUrl || undefined);
      // Clearing the pool orphans every clip: nothing is left carrying a clipId,
      // so the files would sit in memory unreachable for the rest of the session.
      for (const c of clips) { try { URL.revokeObjectURL(c.url); } catch { /* ignore */ } }
      setClips([]); setStageOk(true);
      // The music is the user's file too, and its URL is owned here.
      removeSoundtrack();
      setCaptions(EMPTY_CAPTION_TRACK);
      setImages([]); setPreviewUrl(null); setCount(0); setDensity(1); setLockedCells(new Map()); setFrames(new Map()); setAvgColor(null);
      ownCount(false); // a fresh import after Clear auto-follows the upload count again
  };

  const handleRestoreHistory = (item: HistoryItem) => {
      if (waitForLyricDemo()) return;
      let restoredCaptions: CaptionTrack;
      try { restoredCaptions = normalizeCaptionTrack(item.state.captions); }
      catch { flashNotice('That history item has an invalid caption track. Your work is unchanged.'); return; }
      setCaptions(restoredCaptions);
      setLockedCells(new Map(normalizeProjectLocks(item.state.locks, item.images)));
      setAssignNonce(n => n + 1);
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
      setTurn(l.turn ?? 'hold');
      setPace(l.pace ?? 'even');
      setSync(l.sync ?? 'off');
      if(item.state.style?.background) setBgColor(item.state.style.background);
      // ABSENT MEANS THE DEFAULT, never "keep what is on screen" — restoring a
      // snapshot that predates the title must not leave today's caption on it.
      setLook(item.state.style?.look ?? 'none');
      // Same rule, one field along: a snapshot that predates THE DESK must not
      // leave today's custom grade sitting on it.
      setAdjust(item.state.style?.adjust ?? null);
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
                  width: img.width, height: img.height, analysis: img.analysis, art: img.art,
              }) : null),
              // THE GRADE, as the id OR the five numbers — see `LookRef`. A plain
              // object crosses the structured clone the same way the title plan does,
              // and the worker resolves it through the SAME `cssFilterFor` the preview
              // called, so there is still exactly one pipeline in one file.
              zoom, bgColor, titlePlan: frameTitlePlan, look: lookRef,
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
      if (waitForLyricDemo()) return;
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
    if (waitForLyricDemo()) return;
    setShowExportDialog(false); setExportStatus('processing'); setExportMsg('VECTORIZING...');
    try {
        const rng = createRng(seed); const items = await computeLayout(1000, 1000/aspect, effectiveCount, rng, layoutMode, gutter, entropy, images, primitive, 0, aspect);
        // `orderedAssets`, not the raw pool — the SVG crops from `analysis`, and
        // that is where the crop focus lives (see renderAtSize above).
        const orderedImages = retwistFor(orderedAssets.map(a => a ?? null), items, 1000, 1000 / aspect);
        const stateForSave = buildStateForSave();
        // `images` — the raw SOURCE POOL, last. Not `orderedImages`: that is the
        // drawn permutation with focus and twist already baked into each
        // analysis, and both are re-derived from focus/twist/seed on open. The
        // SVG is the project file, so it carries the pool that made it.
        const svgContent = await generateVectorExport(1000, aspect, layoutMode, items, orderedImages, seed, stateForSave, zoom, bgColor, frameTitlePlan, lookRef, poolForSave);
        const blob = new Blob([svgContent], {type: 'image/svg+xml'});
        const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `GENART-VECTOR-${seed}.svg`; a.click(); URL.revokeObjectURL(url);
        setExportStatus('done'); setTimeout(() => setExportStatus('idle'), 2000);
    } catch (e) { setExportStatus('error'); }
  };

  /**
   * THE POOL AS IT IS WRITTEN TO A FILE — `buildStateForSave`'s counterpart for
   * the pictures, and the ONE value the three writers take instead of `images`.
   *
   * WHY IT EXISTS. A hand-set frame (THE REFRAME) lives in the `frames` Map while
   * the app is open, and every writer serialises `img.analysis` — so the archive,
   * the crash-safe snapshot and the exported SVG all carried the pool without the
   * one thing in an analysis a person put there. The SVG DREW a reframed collage
   * and REOPENED as the un-reframed one.
   *
   * WHY NOT WRITE IT INTO `images` WHEN THE DRAG ENDS, which is the obvious fix
   * and was the one this ladder named: `images` reaches the DISARM effect through
   * `layoutItems`, so the commit took the puck away from under the finger that
   * had just let go. Measured — see lib/reframe.ts.
   *
   * `Object.is`-identical to `images` whenever nobody has dragged a picture, so
   * every file this app writes for everybody else is byte-for-byte what it was.
   */
  const poolForSave = useMemo(() => poolWithFrames(images, frames), [images, frames]);

  // THE ONE `AppState` BUILDER. Save (download), autosave (crash-safe session)
  // and Clear (history) each described the project by writing this same literal
  // inline — three chances to drift, and the manifest is exactly where a silent
  // field-omission becomes a wrong answer on reopen. One source of truth now.
  const buildStateForSave = (): AppState => ({
    version: "1.0", mode: activeTab,
    layout: { mode: layoutMode, primitive, count, density, countOwned, shuffle: shuffleTrigger, seed, aspect, gutter, entropy, arrangement, focus, twist, move, turn, pace, sync },
    style: { background: bgColor, look, adjust: adjust ?? undefined },
    title: titleText ? { text: titleText, place: titlePlace, size: titleSize } : undefined,
    captions: captions.cues.length ? captions : undefined,
    locks: normalizeProjectLocks([...lockedCells], images),
  });

  const handleSaveProject = async () => {
    if (waitForLyricDemo()) return;
    setShowExportDialog(false);
    try {
      await saveProject(buildStateForSave(), poolForSave);
      dirtyRef.current = false;
      if (clips.length || soundtrack) flashNotice('Composition and lyrics saved. Video and music files stay in this session; export a video to keep the finished take.');
    } catch (error) {
      dirtyRef.current = true;
      flashNotice(error instanceof Error ? error.message : 'Could not save the project. Your work is still here.');
    }
  };

  // Write the working project to IndexedDB — the crash-safe snapshot behind the
  // first well bug ("capturing at 4k ... lost what I was doing"), and the source
  // of the SECOND one ("slow and glitching").
  //
  // WHAT CHANGED. This used to call `buildProjectBlob` — the whole `.collage`
  // archive, image bytes and all — on every debounce. Dragging the gutter slider
  // on a twenty-photo project therefore re-fetched and re-zipped ~80MB of JPEG on
  // the main thread, 1.5s after you let go, to persist a manifest change of a few
  // dozen characters. Now the bytes live one row per asset and a flush writes
  // ONLY what the store has never seen (`planAssetWrites`), so the steady state —
  // every settings change, which is nearly every flush — is one small JSON row
  // and zero image reads.
  //
  // Silent and best-effort as before: a failed write leaves the last snapshot
  // standing, and nothing about it ever reaches the user.
  const flushBusy = useRef(false);
  const flushAgain = useRef(false);
  const flushLatest = useRef<() => Promise<void>>(async () => {});
  const flushSession = async () => {
    if (images.length === 0) return;
    // Overlap guard. The pre-capture checkpoint fires `flushSession` directly at
    // the same moment a state change schedules one, and two writers racing the
    // same rows is how a store ends up naming bytes it did not write. The second
    // caller re-runs after the first lands, through `flushLatest` so it uses the
    // CURRENT pool and not the closure that was queued.
    if (flushBusy.current) { flushAgain.current = true; return; }
    flushBusy.current = true;
    try {
      const stored = await sessionStore.storedAssetIds();
      const plan = planAssetWrites(images.map(i => i.id), stored);
      const write: { id: string; asset: sessionStore.StoredAsset }[] = [];
      // Ids whose bytes this flush could NOT read. They are excluded from the
      // snapshot rather than blocking it — see below.
      const uncaptured = new Set<string>();
      for (const id of plan.write) {
        const img = images.find(i => i.id === id);
        if (!img) { uncaptured.add(id); continue; }
        // `fetch` on a blob: URL is a memory read, not a network hop — but it is
        // still a full copy of the image, which is exactly why it now happens
        // once per asset instead of once per keystroke.
        try {
          const fullBlob = await (await fetch(img.src)).blob();
          // THE THUMBNAIL TIER TRAVELS WITH THE ORIGINAL. The app draws
          // `previewSrc` — a ≤1024px JPEG — for every preview and every Stage
          // frame, so a restore that only kept the originals silently promoted
          // the whole pool to full-res previews and left the editor slower after
          // recovering than it was before the crash. Null when `createThumbnail`
          // aliased the source (already under 1024px): same bytes, stored once.
          const previewBlob = img.previewSrc && img.previewSrc !== img.src
            ? await (await fetch(img.previewSrc)).blob()
            : null;
          // ARRAYBUFFER, NOT BLOB. WebKit refuses a Blob into IndexedDB and
          // aborts the transaction — which took the manifest down with it and
          // made this whole feature a silent no-op on every iOS browser, the
          // exact device the crash it recovers from happens on. See StoredAsset.
          write.push({
            id,
            asset: {
              full: await fullBlob.arrayBuffer(),
              fullType: fullBlob.type || 'image/jpeg',
              preview: previewBlob ? await previewBlob.arrayBuffer() : null,
              previewType: previewBlob ? (previewBlob.type || 'image/jpeg') : null,
            },
          });
        } catch { uncaptured.add(id); }
      }
      // THE MANIFEST MUST NEVER NAME BYTES THE STORE DOES NOT HAVE. Restore fails
      // closed on a missing source and then clears the session, so a manifest
      // listing an asset whose bytes were never written would poison the snapshot
      // AND destroy the good one under it.
      //
      // The first cut of this guard skipped the whole write instead — and that
      // was worse, in a way that only shows up on the second flush: `plan.write`
      // holds exactly the ids the store does not have, so a single asset that
      // cannot be read is in EVERY subsequent plan, fails every time, and
      // silently freezes autosave for the rest of the session. The user believes
      // they are protected; nothing has been saved since it went bad.
      //
      // So the snapshot EXCLUDES what it could not capture rather than refusing
      // to exist. A recovery that is one photograph short is a real recovery;
      // an autosave that stopped an hour ago without saying so is not.
      const snapshot = uncaptured.size ? poolForSave.filter(i => !uncaptured.has(i.id)) : poolForSave;
      if (snapshot.length === 0) return; // nothing capturable — leave the last good one
      await sessionStore.putSession({
        // ONE manifest shape: the same `AppState` every save writes, plus the
        // per-image metadata. `sessionEntries` carries width/height so restore
        // never has to decode a picture to learn how big it is.
        manifest: { ...buildStateForSave(), images: sessionEntries(snapshot) },
        savedAt: Date.now(),
        images: snapshot.length,
        write,
        drop: plan.drop,
      });
    } catch { /* best-effort; never surface */ }
    finally {
      flushBusy.current = false;
      if (flushAgain.current) { flushAgain.current = false; void flushLatest.current(); }
    }
  };
  flushLatest.current = flushSession;

  // APPLY A LOADED PROJECT — the single hydration path shared by Open (a file
  // the user picked) and Restore (the crash-safe session). It used to live only
  // inside `handleLoadProject`; the whole class of "the path that forgot it"
  // bugs the comments below guard against is exactly what a second, hand-copied
  // apply path would reintroduce, so Restore reuses THIS one verbatim.
  const applyLoadedProject = (loaded: { state: AppState; images: ImageAsset[] }) => {
        // Validate before changing any live state, including crash-recovery records.
        const restoredCaptions = normalizeCaptionTrack(loaded.state.captions);
        setCaptions(restoredCaptions);
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
        ownCount(ldOwned); setImages(poolWithoutFrames(loaded.images)); const l = loaded.state.layout; setLayoutMode(l.mode || 'minimal'); setCount(num(l.count, 12)); setDensity(num(l.density, 1)); setShuffleTrigger(num(l.shuffle, 0)); setSeed(num(l.seed, Date.now())); setAspect(num(l.aspect, ASPECT_ROSTER[1])); setGutter(num(l.gutter, 0.005)); setEntropy(num(l.entropy, entropy)); if(l.primitive) setPrimitive(l.primitive); if(loaded.state.style?.background) setBgColor(loaded.state.style.background); setLook(loaded.state.style?.look ?? 'none'); setAdjust(loaded.state.style?.adjust ?? null); if(l.arrangement) setArrangement(l.arrangement); else setArrangement((l.resonance ?? 0) > 0.1 ? 'flow' : 'natural'); setFocus(l.focus ?? 'auto'); setTwist(l.twist ?? 'none'); setMove(l.move ?? 'still'); setTurn(l.turn ?? 'hold'); setPace(l.pace ?? 'even'); setSync(l.sync ?? 'off'); setTitleText(loaded.state.title?.text ?? ''); setTitlePlace(loaded.state.title?.place ?? 'bl'); setTitleSize(loaded.state.title?.size ?? 'md');
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
          // THE FRAMES COME OUT OF THE FILE AND INTO THE MAP. Not `new Map()` —
          // that is what the other resets here are, and it would drop every
          // correction the file carries at the moment of opening it. Lifted from
          // `loaded.images` (the pool as it arrived), while `setImages` above was
          // handed the same pool with the frames taken OFF, so the app runs with
          // one source of truth and the writers put it back.
          setClips([]); setStageOk(true); removeSoundtrack();
          setLockedCells(new Map(normalizeProjectLocks(loaded.state.locks, loaded.images)));
          setAssignNonce(n => n + 1);
          setFrames(framesFromPool(loaded.images)); setLastRecipe(undefined);
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
    if (waitForLyricDemo()) return;
    const input = document.createElement('input'); input.type = 'file'; input.accept = '.collage,.svg';
    input.onchange = async (e:any) => {
        const file = e.target.files[0]; if(!file) return;
        if (waitForLyricDemo()) return;
        projectReadBusyRef.current++;
        try {
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
        try { applyLoadedProject(loaded); }
        catch { setOpenError("COULDN'T OPEN THAT FILE"); flashNotice('The caption track is invalid. Your current work is unchanged.'); }
        } finally { projectReadBusyRef.current--; }
    };
    input.click();
  };

  // A SESSION THAT CANNOT BE RESTORED MUST BE FORGOTTEN.
  //
  // This is the other half of the "endless loop": a failed restore used to leave
  // the row in place, so the offer came back on the next launch, and the next,
  // for a session that could never load. Tap, nothing, reload, tap, nothing. If
  // it cannot come back, say so once and clear it — the user gets a real start
  // instead of a button that will fail forever.
  const abandonSession = async (why: string) => {
    setRestorePrompt(null);
    flashNotice(why);
    try { await sessionStore.clearSession(); } catch { /* best-effort, as ever */ }
  };

  // RESTORE THE CRASH-SAFE SESSION.
  //
  // The stored rows are read straight into the pool: one object URL per asset and
  // the sizes come out of the manifest, so nothing is unzipped and NOTHING is
  // decoded. The old path unzipped the whole archive and then `new Image()`-
  // decoded every photograph in sequence purely to relearn width and height —
  // seconds of it on a phone, and a single undecodable asset hung the whole thing
  // forever, because that await had no `onerror` (fixed in project.ts too, since
  // Open goes through it).
  //
  // Still one hydration path: `applyLoadedProject`, exactly as Open uses.
  // `archive` is a session written by the previous build — read once through the
  // original round-trip rather than thrown away, because it is somebody's
  // unfinished work; the next flush rewrites it in the new shape.
  const handleRestoreSession = async () => {
    if (waitForLyricDemo()) return;
    if (restoring) return;
    projectReadBusyRef.current++;
    setRestoring(true);
    const minted: string[] = [];
    try {
      const s = await sessionStore.loadSession();
      if (!s) { await abandonSession('That session could not be read — starting fresh.'); return; }
      // THE READ BROKE, THE SESSION DID NOT. Keep it: the same memory pressure
      // that caused the crash is what makes pulling a whole pool back out fail,
      // and deleting on a transient failure would turn "try again in a moment"
      // into "your work is gone" at exactly the wrong moment.
      if (s.kind === 'unreadable') {
        setRestorePrompt(null);
        flashNotice('Could not read that session just now — it is still saved. Reload to try again.');
        return;
      }

      if (s.kind === 'archive') {
        // `loadProject` reads `file.name`; a bare Blob has none, so wrap it. The
        // name must not end in `.svg`, or it takes the SVG branch and fails.
        const loaded = await loadProject(new File([s.blob], 'session.collage', { type: 'application/zip' }));
        if (!loaded) { await abandonSession('That session could not be restored.'); return; }
        applyLoadedProject(loaded);
      } else {
        const entries = preflightSessionAssets(s.manifest.images);
        if (!entries) throw new Error('Invalid art in the saved session.');
        s.manifest.images = entries;
        const urlById: Record<string, AssetUrls> = {};
        for (const [id, a] of Object.entries(s.assets)) {
          const src = URL.createObjectURL(a.full);
          minted.push(src);
          // Alias when there is no separate thumbnail, exactly as upload does.
          let previewSrc = src;
          if (a.preview) { previewSrc = URL.createObjectURL(a.preview); minted.push(previewSrc); }
          urlById[id] = { src, previewSrc };
        }
        const restored = hydrateSessionAssets(s.manifest.images, urlById);
        // Fails closed on a missing source: a pool that comes back short re-deals
        // every fragment after the gap, so it is not a slightly different collage.
        if (!restored) {
          for (const u of minted) { try { URL.revokeObjectURL(u); } catch { /* already gone */ } }
          minted.length = 0;
          await abandonSession('That session could not be restored.');
          return;
        }
        // The store carries the settings half opaquely — it persists what this
        // app hands it and never inspects it — so the shape is asserted here,
        // where `buildStateForSave` is the thing that wrote it.
        const { images: _entries, ...state } = s.manifest;
        applyLoadedProject({ state: state as unknown as AppState, images: restored as ImageAsset[] });
        minted.length = 0; // handed to the pool only after validation succeeds
      }
      // The banner clears itself the moment the pool is non-empty (the effect
      // below), so success needs no explicit dismissal — only failure does.
      flashNotice('Restored your last session.');
    } catch {
      setRestorePrompt(null);
      flashNotice('That saved session could not be restored. It is still saved; your current work is unchanged.');
    } finally {
      for (const u of minted) { try { URL.revokeObjectURL(u); } catch { /* already gone */ } }
      projectReadBusyRef.current--;
      setRestoring(false);
    }
  };

  const handleDismissRestore = async () => {
    if (waitForLyricDemo()) return;
    setRestorePrompt(null);
    dirtyRef.current = false;
    await sessionStore.clearSession();
  };

  const handleApplyTemplate = (t: Template) => {
      if (waitForLyricDemo()) return;
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
    if (!canAutosave({ imageCount: images.length, isExporting: exporting, isRestoring: !!restorePrompt || restoring })) return;
    dirtyRef.current = true; // there is now work that isn't on disk
    const t = window.setTimeout(() => { void flushSession(); }, AUTOSAVE_DEBOUNCE_MS);
    return () => window.clearTimeout(t);
  }, [images, frames, lockedCells, captions, sync, layoutMode, primitive, count, density, countOwned, shuffleTrigger, seed, aspect, gutter, entropy, bgColor, look, adjust, arrangement, focus, twist, move, turn, pace, titleText, titlePlace, titleSize, activeTab, soundtrack, captionRecording, exportStatus, restorePrompt, restoring]);

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
    <div data-editing={!!studioTool && !maximized} className="studio-shell fixed inset-0 bg-black text-white font-sans flex flex-col select-none overflow-hidden">
      {/* `display: contents` so the wrapper is invisible to the flex column,
          `none` so maximizing costs the header its space WITHOUT unmounting it
          (it owns the export shortcut, and a remount would drop it). */}
      <div style={{ display: maximized ? 'none' : 'contents' }}>
        <Header aiState={aiState} exportStatus={exportStatus} exportMsg={exportMsg} onExport={() => setShowExportDialog(true)} hasImages={images.length > 0} onSaveProject={handleSaveProject} onLoadProject={handleLoadProject} openError={openError} onPreview={() => setMaximized(true)} previewButtonRef={maxBtnRef} />
      </div>
      {/* Exports return to editing with recording progress in the persistent
          transport. Header remains mounted so its export shortcut still works. */}
      <ExportDialog artLoopSeconds={images.length && images.every(i => i.art && i.art.duration === images[0].art?.duration) ? images[0].art?.duration : undefined} canExportVideo={liveMode} onExportVideo={(secs, w) => { setMaximized(false); void flushSession(); recorderRef.current?.start(secs, w); }} videoMaxSeconds={recorderRef.current?.maxSeconds ?? 30} videoSizes={recorderRef.current?.sizes ?? []} canChooseVideoSize={!!recorderRef.current?.canChooseSize} isOpen={showExportDialog} onClose={() => setShowExportDialog(false)} onExport={handleExport} onExportSVG={handleExportSVG} onExportProject={handleSaveProject} canShare={!!navigator.share} onShare={handleShare} />
      <ResultModal isOpen={!!resultBlobUrl} onClose={() => setResultBlobUrl(null)} blobUrl={resultBlobUrl} onShare={handleShareResult} onDownload={handleDownloadResult} isMobile={isMobile} />
      {artRoomOpen && artRoomMode === 'templates' && <ArtRackRoom recipe={artDraft} onChange={setArtDraft}
        sourceId={images.some(i => i.id === artSourceId && i.art) ? artSourceId : null}
        sources={images.filter(i => i.art).map(i => ({ id: i.id, name: i.originalName || 'Art rack', recipe: i.art! }))}
        onSource={id => { setArtSourceId(id); setArtDraft(id ? normalizeArtRecipe(images.find(i => i.id === id)?.art) : createDefaultArtRecipe()); }}
        onClose={() => { setArtRoomOpen(false); (artRoomTriggerRef.current?.getClientRects().length ? artRoomTriggerRef.current : toolRefs.current.add)?.focus(); }}
        onHtml={() => setArtRoomMode('html')}
        busy={demoBusy || exportStatus === 'processing' || captionRecording || restoring}
        onApply={async (recipe, isCurrent) => {
          if (!isCurrent()) return;
          if (demoBusyRef.current || ingestRef.current.total > 0 || projectReadBusyRef.current > 0 || recorderRef.current?.isRecording || exportStatus === 'processing' || restoring) throw new Error('Let the current import or export finish, then apply the artwork.');
          const snapshot = normalizeArtRecipe(recipe), size = ART_SIZES[snapshot.size];
          const canvas = document.createElement('canvas'); canvas.width = size.width; canvas.height = size.height;
          const ctx = canvas.getContext('2d'); if (!ctx) throw new Error('Could not create artwork pixels.');
          let blob: Blob;
          try { drawArt(ctx, size.width, size.height, snapshot, 0); blob = await new Promise<Blob>((resolve, reject) => canvas.toBlob(b => b ? resolve(b) : reject(new Error('Could not encode artwork.')), 'image/png')); }
          finally { canvas.width = canvas.height = 0; }
          if (!isCurrent()) return;
          const file = new File([blob], `Art rack · ${snapshot.layers.length} layers.png`, { type: 'image/png' });
          const replaceId = images.some(i => i.id === artSourceId && i.art) ? artSourceId! : undefined;
          beginIngest(1, 'Applying artwork…');
          const loaded = await handleUpload([file], { geometryOnly: true, idPrefix: 'rack', noun: 'artwork', shouldCommit: isCurrent, replaceId, meta: new Map([[file, { art: snapshot }]]) });
          if (!isCurrent()) return;
          if (!loaded.length) throw new Error('The artwork could not be decoded. Your current artwork is unchanged.');
          setArtSourceId(loaded[0].id);
          if (!images.length) { setLayoutMode('minimal'); setPrimitive('rect'); setAspect(size.width / size.height); setGutter(0); setEntropy(0); setMove('still'); setTurn('hold'); setTwist('none'); setLook('none'); setAdjust(null); }
          flashNotice('Editable art and its animation are ready. Save a project to keep the layers.');
        }} />}
      {artRoomOpen && artRoomMode === 'html' && <ArtRoom open onTemplates={() => setArtRoomMode('templates')} onClose={() => { setArtRoomOpen(false); (artRoomTriggerRef.current?.getClientRects().length ? artRoomTriggerRef.current : toolRefs.current.add)?.focus(); }}
        busy={demoBusy || exportStatus === 'processing' || captionRecording || restoring}
        onImport={async (file, isCurrent) => {
          if (!isCurrent()) return;
          if (demoBusyRef.current || ingestRef.current.total > 0 || projectReadBusyRef.current > 0 || recorderRef.current?.isRecording || exportStatus === 'processing' || restoring) {
            throw new Error('Let the current import or export finish, then add the artwork.');
          }
          beginIngest(1, 'Adding artwork…');
          const loaded = await handleUpload([file], { geometryOnly: true, idPrefix: 'art', noun: 'artwork', shouldCommit: isCurrent });
          if (!isCurrent()) return;
          if (!loaded.length) throw new Error('The artwork could not be decoded. Try capturing again.');
          flashNotice('Artwork added as a still image. Its pixels travel in your saved project.');
        }} />}

      {notice && !artRoomOpen && <div className="studio-notice" role="status">{notice}</div>}

      <div className="studio-workspace" data-panel={!!studioTool && !maximized} data-focus={maximized}>
      <section className="studio-view" aria-label="Artwork and playback">
      <div
        data-testid="studio-stage"
        className="studio-stage relative flex items-center justify-center overflow-hidden"
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
           <StudioStart busy={demoBusy} artTriggerRef={artRoomTriggerRef}
             onArt={() => { setArtRoomMode('templates'); setArtRoomOpen(true); }}
             onImport={() => fileInputRef.current?.click()} onSample={loadLyricDemo} />
         ) : (
            <div
              className="studio-art-band relative z-10 w-full h-full flex justify-center items-center"
              ref={setBandEl}
              // Display-only space: the whole composition remains visible above
              // the controls; every exporter still draws the unchanged geometry.
              data-testid="studio-art-band"
            >
               {/* Measured pixels once the band is known; the old content-sized
                   style stays as the first-paint fallback. */}
               <div
                 className="relative shadow-2xl" data-testid="studio-artwork"
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
                       captionPlans={captionPlans}
                       onTakeChange={setCaptionTake}
                       onRecordingChange={setCaptionRecording}
                       look={lookRef}
                       turn={turnScene}
                       pace={pace}
                       move={move}
                       beat={beatSched}
                       onNotice={flashNotice}
                       onUnavailable={() => setStageOk(false)}
                       controlsHost={stageControlsHost}
                       focusMode={maximized}
                       inspectorOpen={!!studioTool && !maximized}
                       onDetailsChange={handleStageDetails}
                       onRemoveClip={removeClip}
                       recorderRef={recorderRef}
                       poolAssets={images}
                       soundtrack={soundtrack}
                       onRemoveSoundtrack={removeSoundtrack}
                       onSoundtrackMuted={(muted) => setSoundtrack((prev) => (prev ? { ...prev, muted } : prev))}
                       onSoundtrackLevel={(level) => setSoundtrack((prev) => (prev ? { ...prev, level } : prev))}
                       /* THE RANGE FADE, held here for the level's reason: App
                          owns the track, so a value that lived only in the Stage
                          would come back OFF the first time one was rebuilt. */
                       onSoundtrackFade={(fadeSec) => setSoundtrack((prev) => (prev ? { ...prev, fadeSec } : prev))}
                       /* THE RANGE. `undefined` is "the whole track" and is
                          stored as undefined rather than as [0, duration] —
                          absent means the default everywhere in this app, and
                          a stored pair would go stale the moment the probe
                          revised the length. */
                       onSoundtrackWindow={(v) => setSoundtrack((prev) => (
                         prev ? { ...prev, inSec: v?.inSec, outSec: v?.outSec } : prev
                       ))}
                     />
                   ) : (
                     previewUrl && <img src={previewUrl} className="w-full h-full object-contain pointer-events-none" />
                   )}
                   {/* Lock overlay. Stays click-through-able (each <g> is the
                       hit target); the Stage transport sits at z-40 so it wins
                       the clicks that land on it. */}
                   <svg
                     className="absolute inset-0 w-full h-full"
                     viewBox={`0 0 ${PREVIEW_W} ${PREVIEW_H(aspect, PREVIEW_W)}`}
                     /* THE REFRAME needs the browser to stop treating a drag on
                        the artwork as a scroll — but only while a fragment is
                        armed, which is a full-bleed-only state with nothing to
                        scroll. Outside that this attribute is absent and touch
                        behaves exactly as it shipped. */
                     style={armedCell !== null ? { touchAction: 'none' } : undefined}
                   >
                       {layoutItems.map((item, i) => {
                           const isLocked = lockedCells.has(i); const isArmed = maximized && armedCell === i; const d = item.path.map((p: Point, idx: number) => `${idx===0?'M':'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
                           // A PENDING TRADE RE-POINTS EVERY FRAGMENT. While one is parked,
                           // the canvas is not arming anything — every other fragment is a
                           // destination and the parked one is the way out. That is why the
                           // outline is drawn at full opacity rather than on hover: the
                           // gesture is finished with a thumb, and a phone has no hover, so
                           // "which of these can I tap" has to be VISIBLE.
                           const isSwapSource = swapping && swapFrom === i;
                           const isSwapTarget = swapping && swapFrom !== i;
                           return (
                               // OUTSIDE full bleed the tap is the shipped gesture, byte for
                               // byte: it pins. INSIDE it, a fragment has two things that can
                               // be done to it and one tap cannot mean both — so the tap ARMS
                               // and the puck below says which. Tapping the armed one again
                               // puts it away. And once Swap has parked a fragment, the tap
                               // means the third thing: trade with this one.
                               <g
                                 key={i}
                                 onClick={() => {
                                   // A REFRAME ENDS IN A CLICK on this same
                                   // element. Eating exactly that one is what
                                   // stops a drag from also disarming the
                                   // fragment you were just correcting.
                                   if (reframedRef.current) { reframedRef.current = false; return; }
                                   if (swapping) return performSwap(i);
                                   if (maximized) return setArmedCell(prev => (prev === i ? null : i));
                                   return toggleLock(i);
                                 }}
                                 onPointerDown={(e) => beginReframe(e, i)}
                                 onPointerMove={moveReframe}
                                 onPointerUp={endReframe}
                                 onPointerCancel={endReframe}
                                 className={`group ${isArmed && !swapping ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer'}`}
                               >
                                   <path d={d} fill="transparent" stroke="transparent" />
                                   <path
                                     d={d}
                                     fill="none"
                                     stroke={isSwapSource || isSwapTarget ? '#38bdf8' : isArmed ? '#34d399' : isLocked ? '#facc15' : 'white'}
                                     strokeWidth={isSwapSource ? 6 : isSwapTarget ? 3 : isArmed ? 5 : isLocked ? 4 : 2}
                                     strokeDasharray={isSwapTarget ? '14 10' : undefined}
                                     className={`transition-all ${isSwapSource ? 'opacity-100' : isSwapTarget ? 'opacity-70' : isArmed || isLocked ? 'opacity-100' : 'opacity-0 group-hover:opacity-30'}`}
                                   />
                                   {isLocked && (() => { const c = getCentroid(item.path); return ( <foreignObject x={c.x - 12} y={c.y - 12} width="24" height="24"><div className="bg-black/50 p-1 rounded-full backdrop-blur flex items-center justify-center w-full h-full"><Lock size={12} className="text-yellow-400" /></div></foreignObject> ); })()}
                               </g>
                           );
                       })}
                   </svg>
                   {/* WHAT CAN BE DONE TO THE FRAGMENT YOU TAPPED — full bleed only.
                       HTML rather than a `foreignObject`, because the SVG is a
                       1200-unit space scaled to whatever the art box measures, and a
                       tap target defined in those units is 44 px on exactly one
                       screen size. These are CSS pixels, so the 44 px law holds at
                       320 and at 2560 alike. The art box is sized to the artwork's
                       own aspect (`artFit`), so the viewBox is NOT letterboxed inside
                       it and a centroid maps straight to a percentage. */}
                   {maximized && armedCell !== null && layoutItems[armedCell] && (() => {
                       const idx = armedCell;
                       const imgIdx = shuffledIndices[idx];
                       const target = imgIdx === undefined || imgIdx < 0 ? undefined : images[imgIdx];
                       const plan = planEviction(images, clips, target?.id);
                       // A fragment holding nothing has nothing to pin and nothing to
                       // throw away. Showing two dead buttons over it would be the
                       // inert-control defect this repo has already been filed for.
                       if (plan.count === 0) return null;
                       const H = PREVIEW_H(aspect, PREVIEW_W);
                       const c = getCentroid(layoutItems[idx].path);
                       // Kept whole against the edges: a puck half off the artwork is
                       // clipped by the band, and the button you cannot reach is the
                       // one over the fragment at the corner.
                       // WHETHER THERE IS ANYBODY TO TRADE WITH is asked of the
                       // module that performs the trade (`canSwapFrom` calls
                       // `planSwap`), never re-derived here — a rule spelled a
                       // second time at the call site drifts from the rule the
                       // tests measure, which is the bug this repo has written
                       // down four times now.
                       const tradeable = canSwapFrom(images, shuffledIndices, idx);
                       // THE REFRAME'S ONLY BUTTON, and it exists only on a
                       // picture somebody moved: the way IN is the drag, so a
                       // Reframe verb would be a control for a gesture that is
                       // already available, while the way BACK has no gesture
                       // at all. Absent on every fragment nobody has touched.
                       // THE MAP IS THE ONLY PLACE A FRAME LIVES while the app is open —
                       // a correction reopened from a file is lifted into it by
                       // `applyLoadedProject`, so this one predicate covers a drag from a
                       // moment ago and one made in a previous session alike.
                       const reframed = !!(target?.id && frames.has(target.id));
                       // Kept whole against the edges: a puck half off the artwork is
                       // clipped by the band, and the button you cannot reach is the
                       // one over the fragment at the corner. The width is MEASURED,
                       // not guessed — 44 px per verb plus the gaps and the padding —
                       // and it has to grow with the third one or the clamp lets a
                       // corner puck hang off the art.
                       // MEASURED, not guessed: 44 px per verb plus the gaps
                       // and the padding. Two verbs is 108 and three is 152, so
                       // the fourth is 196 — and the clamp below needs the real
                       // number or a corner puck hangs off the art.
                       const PUCK = swapping ? 210 : 20 + 44 * (2 + (tradeable ? 1 : 0) + (reframed ? 1 : 0));
                       const clampPx = (v: number, size: number) => (size > PUCK + 12 ? Math.min(Math.max(v, PUCK / 2 + 6), size - PUCK / 2 - 6) : size / 2);
                       const left = artFit ? `${clampPx((c.x / PREVIEW_W) * artFit.w, artFit.w)}px` : `${(c.x / PREVIEW_W) * 100}%`;
                       const top = artFit ? `${clampPx((c.y / H) * artFit.h, artFit.h)}px` : `${(c.y / H) * 100}%`;
                       const isLocked = lockedCells.has(idx);
                       const what = plan.isClip ? (plan.label || 'this clip') : (plan.label || 'this picture');
                       // A PENDING TRADE TAKES THE PUCK OVER. It is the same
                       // element in the same place — the fragment you parked —
                       // so the thing you tapped stays the thing being talked
                       // about, and there is exactly one way out of the mode
                       // that does not also cost you full bleed.
                       if (swapping) return (
                           <div
                               data-testid="cell-actions"
                               /* THE SAME CLASS FIX AS THE VERBS PUCK BELOW,
                                  applied to the overlay the scar was actually
                                  filed against: the pill sits ON the fragment
                                  it parked, so on a small fragment it covered
                                  the taps meant for the artwork. The container
                                  no longer takes them; the X and the label do
                                  not need to. */
                               className="absolute z-[60] -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 rounded-2xl border border-sky-400/40 bg-black/85 backdrop-blur pl-3 pr-1.5 py-1.5 shadow-2xl pointer-events-none [&>button]:pointer-events-auto"
                               style={{ left, top }}
                           >
                               <span data-testid="swap-pending" className="text-[13px] leading-tight text-sky-300 font-medium whitespace-nowrap">Tap another fragment</span>
                               <button
                                   data-testid="swap-cancel"
                                   onClick={() => setSwapFrom(null)}
                                   title="Cancel the trade"
                                   aria-label="Cancel the trade"
                                   className="w-11 h-11 shrink-0 rounded-xl text-gray-200 hover:bg-white/10 flex items-center justify-center active:scale-95 transition"
                               ><X size={18} /></button>
                           </div>
                       );
                       return (
                           <div
                               data-testid="cell-actions"
                               /* pointer-events-none ON THE CONTAINER, auto on
                                  the buttons. The puck sits at the fragment's
                                  CENTROID — which is exactly where a thumb
                                  reaches to drag the picture — so its 6px of
                                  padding and its gaps were swallowing the
                                  gesture they sit on top of. Same class as the
                                  scar already filed against the pending pill
                                  ("the affordance covered the gesture it
                                  documented"); the verbs themselves still take
                                  every tap that lands on them. */
                               className="absolute z-[60] -translate-x-1/2 -translate-y-1/2 flex items-center gap-1 rounded-2xl border border-white/20 bg-black/80 backdrop-blur px-1.5 py-1.5 shadow-2xl pointer-events-none [&>button]:pointer-events-auto"
                               style={{ left, top }}
                           >
                               <button
                                   data-testid="cell-lock"
                                   onClick={() => toggleLock(idx)}
                                   title={isLocked ? 'Unpin this fragment' : 'Pin this fragment — it keeps this picture through a remix'}
                                   aria-label={isLocked ? 'Unpin this fragment' : 'Pin this fragment'}
                                   className={`w-11 h-11 rounded-xl flex items-center justify-center active:scale-95 transition ${isLocked ? 'text-yellow-400 bg-yellow-400/15 hover:bg-yellow-400/25' : 'text-gray-200 hover:bg-white/10'}`}
                               >{isLocked ? <Unlock size={18} /> : <Lock size={18} />}</button>
                               {tradeable && (
                                 <button
                                     data-testid="cell-swap"
                                     onClick={() => setSwapFrom(idx)}
                                     title={`Trade ${what} with another fragment`}
                                     aria-label={`Trade ${what} with another fragment`}
                                     className="w-11 h-11 rounded-xl text-sky-300 hover:bg-sky-400/20 flex items-center justify-center active:scale-95 transition"
                                 ><ArrowLeftRight size={18} /></button>
                               )}
                               {reframed && (
                                 <button
                                     data-testid="cell-recentre"
                                     onClick={() => setFrames(prev => {
                                       const m = new Map(prev);
                                       if (target?.id) m.delete(target.id);
                                       return m;
                                     })}
                                     title={`Recentre ${what} — back to the crop the app chose`}
                                     aria-label="Recentre this picture"
                                     className="w-11 h-11 rounded-xl text-emerald-300 hover:bg-emerald-400/20 flex items-center justify-center active:scale-95 transition"
                                 ><Crosshair size={18} /></button>
                               )}
                               <button
                                   data-testid="cell-remove"
                                   onClick={() => evictSource(idx)}
                                   title={plan.isClip && plan.count > 1
                                       ? `Remove ${what} — and its ${plan.count} frames`
                                       : `Remove ${what} from the pool`}
                                   aria-label={`Remove ${what} from the pool`}
                                   className="w-11 h-11 rounded-xl text-red-400 hover:bg-red-500/20 flex items-center justify-center active:scale-95 transition"
                               ><X size={18} /></button>
                           </div>
                       );
                   })()}
               </div>

            </div>
         )}
      </div>


      <div className="studio-playback" hidden={!liveMode}>
        <div ref={setStageControlsHost} className="studio-playback-host" />
      </div>
      {images.length > 0 && maximized && <div className="studio-preview-tools" role="toolbar" aria-label={maximized ? 'Full bleed tools' : 'Preview controls'}>
        <span className="studio-source-count">{images.length} source{images.length === 1 ? '' : 's'}</span>
        <button type="button" data-testid="quick-dice" onClick={handleDice} aria-label="Roll the dice"><Dices size={17}/><span>Dice</span></button>
        <button type="button" data-testid={maximized ? 'undo' : 'quick-undo'} onClick={handleUndo} disabled={!canUndo} aria-label="Undo the last composition change"><Undo2 size={17}/><span>Undo</span></button>
        <button type="button" ref={maximized ? exitBtnRef : maxBtnRef} className="studio-preview-toggle"
          onClick={() => setMaximized(m => !m)} aria-label={maximized ? 'Back to editing' : 'Expand preview'}
          title={maximized ? 'Back to editing (Esc)' : 'Expand preview (F)'}>
          {maximized ? <Minimize2 size={17}/> : <Maximize2 size={17}/>}<span>{maximized ? 'Back to editing' : 'Expand preview'}</span>
        </button>
      </div>}
      </section>

      <aside id="studio-editing-panel" className="studio-inspector" hidden={!studioTool || maximized} aria-label="Editing panel">
        <div className="studio-inspector-heading">
          <h2>{studioTool === 'add' ? 'Add to your project' : studioTool === 'layout' ? 'Shape your composition' : studioTool === 'look' ? 'Set the look' : studioTool === 'motion' ? 'Make it move' : 'Words on screen'}</h2>
          <button type="button" ref={inspectorCloseRef} onClick={closeTool} aria-label="Close editing panel" title="Back to preview"><span>Done</span><X size={16}/></button>
        </div>
        {studioTool === 'add' && <div className="studio-add-panel">
          <button type="button" ref={images.length ? artRoomTriggerRef : undefined} aria-label="Art Room" onClick={() => { setArtRoomMode('templates'); setArtRoomOpen(true); }} disabled={demoBusy || exportStatus === 'processing' || captionRecording || restoring}><Palette size={20}/><span><b>Art Room</b><small>Combine animated templates and layers</small></span></button>
          <button type="button" onClick={() => fileInputRef.current?.click()} aria-label="Add more images or video"><Plus size={20}/><span><b>Add images or video</b><small>Drop files onto the artwork, too</small></span></button>
          <button type="button" onClick={() => musicInputRef.current?.click()} aria-label={soundtrack ? 'Replace the music' : 'Add music'}><Music size={20}/><span><b>{soundtrack ? 'Replace music' : 'Add music'}</b><small>{soundtrack ? soundtrack.name : 'An audio file, or the sound from a video'}</small></span></button>
          <button type="button" data-wish-well aria-label="Feedback" onClick={() => (window as any).Feedback?.open('bug')}><span><b>Feedback</b><small>Report a bug or wish it better</small></span></button>
          <details className="studio-project-actions"><summary>Project actions</summary>
            <button type="button" onClick={() => videoInputRef.current?.click()} aria-label="Add a video">Choose video only</button>
            <button type="button" onClick={handleSaveProject}>Save editable project</button>
            <button type="button" onClick={handleClear} aria-label="Clear all" className="studio-danger">Clear all sources</button>
          </details>
        </div>}
        {studioTool === 'layout' && <div className="studio-subnav" role="group" aria-label="Layout controls">
          <button type="button" onClick={() => setActiveTab('simple')} aria-pressed={activeTab === 'simple'}>Composition</button>
          <button type="button" onClick={() => setActiveTab('advanced')} aria-label="Canvas & crop" aria-pressed={activeTab === 'advanced'}>Canvas & crop</button>
        </div>}
        {studioTool === 'text' && <div className="studio-subnav" role="group" aria-label="Text controls">
          <button type="button" onClick={() => setCaptionPanel(true)} aria-pressed={captionPanel}>Lyrics & captions</button>
          <button type="button" onClick={() => setCaptionPanel(false)} aria-pressed={!captionPanel}>Title</button>
        </div>}
        {images.length > 0 && <div className="studio-caption-panel" hidden={studioTool !== 'text' || !captionPanel}>
          <CaptionEditor defaultOpen track={captions} onChange={setCaptions} take={captionTake}
            getTime={() => recorderRef.current?.getTime() ?? 0} onSeek={time => recorderRef.current?.seek(time)}
            disabled={exportStatus === 'processing' || captionRecording}/>
        </div>}
        <div className="studio-controls-panel" hidden={!studioTool || studioTool === 'add' || (studioTool === 'text' && captionPanel) || (studioTool === 'layout' && activeTab === 'advanced')}>
          <SimpleControls section={studioTool === 'look' ? 'look' : studioTool === 'motion' ? 'motion' : studioTool === 'text' ? 'title' : 'layout'} layoutMode={layoutMode} setLayoutMode={setLayoutMode} primitive={primitive} setPrimitive={setPrimitive} count={count} setCount={updateCountSmart} density={density} setDensity={setDensity} entropy={entropy} setEntropy={setEntropy} onRemix={handleRemix} onShuffle={handleShuffle} onDice={handleDice} onColourDice={handleColourDice} holdFrame={holdFrame} onHoldFrame={setHoldFrame} lastRecipe={lastRecipe} onUndo={handleUndo} onRedo={handleRedo} canUndo={canUndo} canRedo={canRedo} compositionCode={compositionCode} onApplyCode={applyCompositionCode} rejectedCode={rejectedBootCode} hasImages={images.length > 0} isLayoutLocked={lockedCells.size > 0} titleText={titleText} titlePlace={titlePlace} titleSize={titleSize} onTitleText={setTitleText} onTitlePlace={setTitlePlace} onTitleSize={setTitleSize} look={look} onLook={(id) => { setLook(id); setAdjust(null); }} desk={deskShown} onDesk={applyDesk} deskCustom={!!adjust} move={move} onMove={chooseMove} turn={turn} onTurn={setTurn} pace={pace} onPace={setPace} sync={sync} onSync={setSync} beatGrid={beatGrid} beatBusy={beatBusy} beatBeats={beatSched?.beats ?? 0} hasMusic={!!soundtrack} />
        </div>
        <div className="studio-controls-panel" hidden={studioTool !== 'layout' || activeTab !== 'advanced'}>
          <AdvancedControls aspect={aspect} setAspect={setAspect} gutter={gutter} setGutter={setGutter} entropy={entropy} setEntropy={setEntropy} bgColor={bgColor} setBgColor={setBgColor} avgColor={avgColor} onRemix={handleRemix} onShuffle={handleShuffle} onExportVector={handleExportSVG} onRestoreHistory={handleRestoreHistory} isLayoutLocked={lockedCells.size > 0} layoutMode={layoutMode} setLayoutMode={setLayoutMode} count={count} setCount={updateCountSmart} arrangement={arrangement} setArrangement={setArrangement} focus={focus} setFocus={setFocus} twist={twist} setTwist={setTwist} />
        </div>
      </aside>
      </div>

      {images.length > 0 && <nav className="studio-taskbar" aria-label="Studio tools" hidden={maximized}>
        {([{id:'add',label:'Add',icon:<Plus size={18}/>},{id:'layout',label:'Layout',icon:<Layout size={18}/>},{id:'look',label:'Look',icon:<Palette size={18}/>},{id:'motion',label:'Motion',icon:<Wand2 size={18}/>},{id:'text',label:'Text',icon:<Type size={18}/>} ] as const).map(tool => <button
          key={tool.id} type="button" ref={el => { toolRefs.current[tool.id] = el; }}
          aria-label={tool.label} aria-expanded={studioTool === tool.id}
          aria-controls="studio-editing-panel" onClick={() => { setStudioTool(current => current === tool.id ? null : tool.id); if (tool.id === 'text') setCaptionPanel(true); }}>
          {tool.icon}<span>{tool.label}</span>
        </button>)}
      </nav>}

      {/* CRASH RECOVERY. Shown only into an empty pool (shouldPromptRestore), so
          it never shadows a project already on the stage. One-handed sizes: the
          card caps at the viewport, the label truncates, both taps clear 44px. */}
      {/* BELOW THE HEADER ON A PHONE, and that is a fix rather than a taste.
          At `top-3` this card is 94vw wide and centred, so on a 390px screen it
          spans x 12..381 and y 12..78 — and the header's OPEN button sits at
          x 294..378, y 8..52. The banner covered it completely: the offer to
          bring back the last session physically blocked the one control that
          opens a DIFFERENT one, and a centre-tap on Open hit the card. Measured
          on a Pixel 5 (reframe.spec T4 could not reach Open at all); at 320 and
          360 the header wraps to y 61..105 and the same card clipped its top
          third. `top-28` (112px) clears the wrapped header and the unwrapped
          one alike, and `md:top-3` leaves every desktop pixel where it was.
          FOURTH TIME for this shape — the pending pill, the verbs puck, the
          full-bleed rail, now this — so it is a thing this app does whenever it
          puts something over the canvas, not an accident of one component. */}
      {restorePrompt && shouldPromptRestore(true, images.length) && (
        <div className="fixed top-28 md:top-3 left-1/2 -translate-x-1/2 z-[300] w-[min(28rem,94vw)] animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="rounded-xl bg-[#0d0d0d]/95 border border-emerald-500/40 shadow-2xl backdrop-blur px-3 py-2.5">
            <div className="flex items-center gap-2.5">
              <RefreshCw size={15} className={`text-emerald-400 shrink-0${restoring ? ' animate-spin' : ''}`} />
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-black tracking-[0.14em] text-white uppercase truncate">{restoring ? 'Bringing it back' : 'Pick up where you left off'}</div>
                <div className="text-[9px] text-white/50 tracking-wide truncate">
                  {restorePrompt.images} image{restorePrompt.images === 1 ? '' : 's'} · saved {formatAgo(Date.now() - restorePrompt.savedAt)}
                </div>
              </div>
              {/* Disabled, not hidden, while the restore runs: the card holding its
                  size is what stops the layout jumping under a thumb mid-tap. */}
              <button onClick={handleRestoreSession} disabled={restoring} className="shrink-0 min-h-[44px] px-3.5 rounded-lg bg-emerald-500 text-black text-[10px] font-black tracking-[0.1em] uppercase active:scale-95 transition-transform disabled:opacity-60">{restoring ? 'Restoring' : 'Restore'}</button>
              <button onClick={handleDismissRestore} disabled={restoring} aria-label="Dismiss saved session" className="shrink-0 min-h-[44px] min-w-[44px] grid place-items-center rounded-lg bg-white/5 text-white/60 hover:text-white active:scale-95 transition-transform disabled:opacity-40"><X size={15} /></button>
            </div>
          </div>
        </div>
      )}


      <input ref={fileInputRef} type="file" multiple accept="image/*,video/*" className="hidden" onChange={onFileInputChange} />
      <input ref={videoInputRef} type="file" multiple accept="video/*,.mov,.mp4,.m4v,.webm" className="hidden" onChange={onFileInputChange} />
      {/* `audio/*` plus the spellings some pickers refuse to match on type
          alone — AND the video containers, because THAT is the wish: *"if you
          use a video for the sound … it should not display the video"*. Without
          `video/*` here the desktop picker greys the clip out and the fix is
          unreachable from a Mac; with it, `data-intake="music"` takes the sound
          and leaves the pictures. `audio/*` stays FIRST: three e2e suites find
          this input by `accept*="audio"`.
          Not `multiple`: one track is the job. */}
      <input
        ref={musicInputRef}
        type="file"
        data-intake="music"
        accept="audio/*,video/*,.mp3,.m4a,.aac,.wav,.flac,.opus,.oga,.mov,.mp4,.m4v,.webm"
        className="hidden"
        onChange={onFileInputChange}
      />
    </div>
  );
}
