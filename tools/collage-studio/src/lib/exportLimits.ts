// src/lib/exportLimits.ts
// =============================================================================
// WHAT THIS DEVICE CAN ACTUALLY EXPORT — measured, not guessed.
//
// MASTER: platform engineer who measures the device instead of trusting a
// constant (jhildenbiddle's `canvas-size` workflow — far-corner sentinel plus
// read-back, 1-px strips for the dimension axis, immediate backing-store
// release), crossed with an A/V engineer who assumes the encoder is fussy and
// proves the artifact rather than asserting it.
//
// -----------------------------------------------------------------------------
// THE BUG THIS EXISTS TO KILL
// -----------------------------------------------------------------------------
// The MAX export walked a hardcoded ladder [30000, 24000, 16384, 12000, 8192,
// 4096] and trusted try/catch to tell it when a size was too big. Four things
// are wrong with that, and they compound:
//
//   a. The top tiers cannot succeed ANYWHERE. 30000px at aspect 1 is 900 MP
//      (3.35 GiB RGBA); the most generous cap in any shipping engine is 2^28 =
//      268,435,456 px. 30000 and 24000 fail at all four UI aspects on all four
//      engines. The ladder spent its first iterations on impossible states.
//
//   b. NO ENGINE THROWS. Blink, Gecko and WebKit all hand back a live-looking
//      CanvasRenderingContext2D for an over-limit canvas, silently drop every
//      draw, and WebKit then encodes that dead surface into a valid,
//      correctly-sized, entirely BLACK JPEG. try/catch is structurally blind to
//      all of it. An OOM-killed worker fires neither onmessage nor onerror — it
//      just goes quiet, forever, and a ladder with no timeout never advances.
//      That is exactly the owner's phone: MAX hung, 8K worked when picked by hand.
//
//   c. The worker fallback re-rendered ON THE MAIN THREAD AT THE SAME SIZE, so
//      an impossible size could "succeed" into a blank image instead of failing
//      over to a smaller tier.
//
//   d. Nothing probed what the device could allocate and nothing validated the
//      blob that came back.
//
// -----------------------------------------------------------------------------
// THE SHAPE OF THE FIX
// -----------------------------------------------------------------------------
//   MEASURE   probeMaxCanvas()   — far-corner sentinel + read-back binary search,
//                                  bounded by a free allocation-less budget,
//                                  cached in memory + sessionStorage.
//   DERIVE    deriveTiers()      — the ladder comes from the measurement, so a
//                                  30000px option is never offered to hardware
//                                  that cannot produce it.
//   ATTEMPT   runWithFallback()  — hard timeout scaled to PIXEL COUNT, mandatory
//                                  teardown, validate, step down, and report
//                                  which tier won and why the others were rejected.
//   PROVE     assertSurfaceLive()/sampleIsNonBlank()/validateExportBlob()
//
// This module has ZERO imports on purpose: it is pure logic plus DOM primitives,
// so it can be unit-tested under plain node (see `selfTest()` at the bottom) and
// so it cannot collide with concurrent edits elsewhere in the tree.
//
// -----------------------------------------------------------------------------
// WIRING SKETCH (the integrator owns the call sites; this is the intended shape)
// -----------------------------------------------------------------------------
//   const limits = await probeMaxCanvas();            // once per session, on dialog OPEN
//   const res = await runWithFallback(
//     async (attempt, ctl) => {
//       const worker = new RenderWorker();
//       ctl.onAbort(() => worker.terminate());        // MANDATORY — see the cascade note
//       return await postRender(worker, attempt);     // -> { blob, surfaceLive, failedImages }
//     },
//     { aspect, limits, fragments: layoutItems.length },
//   );
//   if (res.ok && res.blob) onBlobReady(res.blob);    // res.tier is the tier that won
//   else console.warn(res.log);                       // per-tier rejection reasons
// =============================================================================

// -----------------------------------------------------------------------------
// 1. TYPES
// -----------------------------------------------------------------------------

export interface CanvasLimits {
  /** Largest w*h (in px) this realm could allocate AND read back. */
  maxAreaPx: number;
  /** Largest single edge this realm could allocate AND read back. */
  maxDimPx: number;
  /** Where the numbers came from. 'floor' = probing was impossible; assume the safe minimum. */
  source: 'probe' | 'cache' | 'floor';
  /**
   * Which realm was measured. Blink applies its canvas-area cap in
   * html_canvas_element.cc, so OffscreenCanvas-in-worker and <canvas>-in-window
   * do NOT necessarily share a limit. A limit measured in one realm must never
   * gate a render in the other — this field exists to make that mismatch
   * impossible to ignore.
   */
  realm: 'window' | 'worker';
  /** ms spent probing (0 for cache). Telemetry only. */
  costMs: number;
  probedAt: number;
}

/** A rectangle. Structurally identical to `Rect` in src/types.ts — kept local to stay import-free. */
export interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
}

type AnyCanvas = HTMLCanvasElement | OffscreenCanvas;
type Ctx2D = CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D;

interface NavigatorWithMemory extends Navigator {
  /** Chromium-only, secure-context-only, quantised to 0.25/0.5/1/2/4/8. Absent on Safari + Firefox. */
  deviceMemory?: number;
}

/** Never probed below this: a 2048px long edge is ~4.2 MP square and has never failed anywhere. */
const SAFE_FLOOR_AREA = 2048 * 2048;
const SAFE_FLOOR_DIM = 2048;

/** Nothing in the app ever wants more than this, so never probe past it. */
const HARD_MAX_DIM = 65535;
const HARD_MAX_AREA = 30000 * 30000;

/** Bytes in flight per pixel while exporting: one RGBA backing store + one encoder copy. */
const BYTES_PER_PX_IN_FLIGHT = 8;

/**
 * Sentinel is deliberately neither black nor white, so a zeroed buffer
 * (transparent black) AND a cleared-to-white buffer both read as FAILURE.
 * Tolerance absorbs colour-management rounding.
 */
const SENTINEL_R = 127;
const SENTINEL_G = 0;
const SENTINEL_B = 255;
const CHANNEL_TOLERANCE = 8;
const SENTINEL_ALPHA_MIN = 250;

const SCHEMA = 'genart.canvasLimits.v1';

// -----------------------------------------------------------------------------
// 2. SURFACE PRIMITIVES (identical code path in window and worker)
// -----------------------------------------------------------------------------

const inWorker = (): boolean =>
  typeof document === 'undefined' && typeof OffscreenCanvas !== 'undefined';

/**
 * Allocate the SAME class of surface the renderer will use, in the SAME realm.
 * Returns null when neither surface type exists (node, or a locked-down realm) —
 * every caller treats null as "cannot allocate", which degrades to the safe floor.
 */
const createSurface = (w: number, h: number): AnyCanvas | null => {
  try {
    if (typeof document !== 'undefined' && typeof document.createElement === 'function') {
      const c = document.createElement('canvas');
      c.width = w;
      c.height = h;
      return c;
    }
    if (typeof OffscreenCanvas !== 'undefined') return new OffscreenCanvas(w, h);
  } catch {
    /* `new OffscreenCanvas` can throw RangeError on absurd dimensions; that is a clean fail. */
  }
  return null;
};

/**
 * Free the backing store NOW. Do not wait for GC — on iOS it will not come in
 * time. This is the doctrine lib/video.ts already runs (`releaseCanvas`,
 * "iOS is aggressive about canvas memory"). Without it, ten probes retain
 * several GB and the probe becomes the crash it exists to prevent.
 */
const releaseSurface = (c: AnyCanvas | null): void => {
  if (!c) return;
  try {
    c.width = 0;
    c.height = 0;
  } catch {
    /* ignore */
  }
};

const rest = (ms: number): Promise<void> => new Promise((r) => setTimeout(r, ms));

// -----------------------------------------------------------------------------
// 3. THE PRIMITIVE — can this realm produce a usable w x h surface RIGHT NOW?
// -----------------------------------------------------------------------------

/**
 * Allocate -> write a sentinel into the FAR CORNER -> read that one pixel back
 * -> release. Cost is O(1): one allocation, one 1-px fill, one 1-px read.
 *
 * WHY THE FAR CORNER: a buffer that was clamped to a smaller allocation still
 * answers correctly at (0,0). (w-1, h-1) is the only point that proves the whole
 * extent exists.
 *
 * WHY NOT try/catch ALONE — what each engine actually does on failure:
 *   Blink  — getContext('2d') returns a NON-null context, canvas.width keeps the
 *            value you set, every draw is dropped, getImageData yields 0,0,0,0.
 *            toDataURL() returns the literal string "data:," and toBlob() fires
 *            its callback with null.
 *   Gecko  — usually getContext('2d') returns null on the OOM path; when it does
 *            not, draws are dropped and the read-back is transparent black.
 *   WebKit — context is live, draws are dropped, read-back is transparent black,
 *            and toBlob STILL yields a valid, correctly-sized, entirely BLACK
 *            JPEG. No exception, no null, no catchable console error. The
 *            read-back is the ONLY signal.
 *   All, worker — `new OffscreenCanvas(w,h)` is lazy and essentially never
 *            throws for size; failure surfaces at getContext (may be null) or as
 *            silent no-op draws.
 *
 * NOTE on context options: getContext('2d') is called with NO options on
 * purpose. Probe fidelity requires the same options the renderer uses; adding
 * `willReadFrequently` would force a CPU-backed surface and measure a different
 * limit than the one that will actually be hit.
 */
export const canAllocate = (w: number, h: number): boolean => {
  if (!Number.isFinite(w) || !Number.isFinite(h) || w < 1 || h < 1) return false;
  const iw = Math.floor(w);
  const ih = Math.floor(h);
  let c: AnyCanvas | null = null;
  try {
    c = createSurface(iw, ih);
    if (!c) return false;
    // The engine refused the size and reset/clamped the element (Blink/Gecko
    // fall back to the 300x150 default).
    if (c.width !== iw || c.height !== ih) return false;

    const ctx = (c as HTMLCanvasElement).getContext('2d') as CanvasRenderingContext2D | null;
    if (!ctx) return false;

    ctx.fillStyle = `rgb(${SENTINEL_R},${SENTINEL_G},${SENTINEL_B})`;
    ctx.fillRect(iw - 1, ih - 1, 1, 1);
    const d = ctx.getImageData(iw - 1, ih - 1, 1, 1).data;

    return (
      Math.abs(d[0] - SENTINEL_R) <= CHANNEL_TOLERANCE &&
      Math.abs(d[1] - SENTINEL_G) <= CHANNEL_TOLERANCE &&
      Math.abs(d[2] - SENTINEL_B) <= CHANNEL_TOLERANCE &&
      d[3] >= SENTINEL_ALPHA_MIN
    );
  } catch {
    return false;
  } finally {
    releaseSurface(c);
  }
};

// -----------------------------------------------------------------------------
// 4. FREE PRE-FILTER — decide what is worth probing WITHOUT allocating anything
// -----------------------------------------------------------------------------

/**
 * `null` = not settled yet. A NUMBER (including 0) = this realm's final answer.
 *
 * MEMOISE THE ANSWER, NOT THE FAILURE — the same policy `createSignalCache`
 * applies to the Stage's copy of this probe in rasterBudget.ts, restated here
 * rather than imported because both files take ZERO IMPORTS on purpose (their
 * unit sweeps transpile one file and import it, so a relative import would not
 * resolve). Two copies of an eight-line policy, and the comment on each names
 * the other.
 *
 * `getContext('webgl')` returns null TRANSIENTLY for reasons that say nothing
 * about the device: Chromium evicts the oldest context past its per-page cap, a
 * GPU-process crash blanks every one until it restarts, and `createSurface`
 * itself can fail under allocation pressure. Writing that straight into the
 * cache made a blip permanent.
 */
export const BLANK_GL_PROBE_RETRIES = 3;
let glMaxTextureCache: number | null = null;
let glBlankProbes = 0;

/** GPU class signal. Costs one 1x1 WebGL context, cached, context explicitly lost. */
const gpuMaxTextureSize = (): number => {
  if (glMaxTextureCache !== null) return glMaxTextureCache;
  let out = 0;
  let c: AnyCanvas | null = null;
  try {
    c = createSurface(1, 1);
    const gl =
      c &&
      (((c as HTMLCanvasElement).getContext('webgl2') ||
        (c as HTMLCanvasElement).getContext('webgl')) as WebGLRenderingContext | null);
    if (gl) {
      out = gl.getParameter(gl.MAX_TEXTURE_SIZE) as number;
      const lose = gl.getExtension('WEBGL_lose_context') as { loseContext(): void } | null;
      lose?.loseContext();
    }
  } catch {
    out = 0;
  } finally {
    releaseSurface(c);
  }
  const got = Number.isFinite(out) && out > 0 ? out : 0;
  if (got > 0) {
    glMaxTextureCache = got;
    return got;
  }
  // A blank is re-probed on the next call, then accepted — without the retry a
  // blip is permanent, without the settle a realm that genuinely has no WebGL
  // pays a context probe every time anyone asks.
  glBlankProbes += 1;
  if (glBlankProbes > BLANK_GL_PROBE_RETRIES) glMaxTextureCache = 0;
  return 0;
};

/**
 * Was the last `probeBudgetAreaPx()` answer a GUESS made because nothing
 * answered, rather than a class we actually read? Distinguishing those two is
 * the whole point: "this device has no WebGL" is a fact about the device, and
 * "WebGL did not answer just now" is a fact about the last two milliseconds.
 */
let lastBudgetBlind = false;
export const lastProbeBudgetWasBlind = (): boolean => lastBudgetBlind;

/**
 * Ceiling on what we are willing to PROBE, derived with zero allocation.
 *
 * THIS IS THE GUARD THAT STOPS THE PROBE FROM BEING THE CRASH, and it must run
 * before the first large allocation.
 */
export const probeBudgetAreaPx = (): number => {
  const nav = typeof navigator !== 'undefined' ? (navigator as NavigatorWithMemory) : undefined;

  const gb = typeof nav?.deviceMemory === 'number' ? nav.deviceMemory : 0;
  if (gb > 0) {
    lastBudgetBlind = false;
    // Spend at most 1/8 of reported RAM on backing store + encoder copy.
    const bytes = (gb * 1024 * 1024 * 1024) / 8;
    return Math.max(SAFE_FLOOR_AREA, Math.floor(bytes / BYTES_PER_PX_IN_FLIGHT));
  }

  // No deviceMemory => Safari/iOS/Firefox. Infer device class from the GPU.
  // iOS: A7-A9 report 4096, A10-A11 report 8192, A12+/M-series report 16384.
  const tex = gpuMaxTextureSize();
  // Recorded ONCE, from the same call that produced the number — asking the
  // probe a second time would burn a retry and could answer differently, which
  // would leave the budget and the verdict about the budget disagreeing.
  lastBudgetBlind = tex <= 0 && glMaxTextureCache === null;
  if (tex >= 16384) return 268435456; // let the real probe find the truth
  if (tex >= 8192) return 134217728;
  if (tex >= 4096) return 33554432;
  return SAFE_FLOOR_AREA * 4;
};

// -----------------------------------------------------------------------------
// 5. GEOMETRY — the one place that knows how a tier becomes pixels
// -----------------------------------------------------------------------------

/** Aspect only ever arrives as one of the four UI ratios; this guards a NaN from a restored project. */
const safeAspect = (aspect: number): number =>
  Number.isFinite(aspect) && aspect > 0 ? aspect : 1;

/**
 * EXACTLY mirrors App.generateBlob():
 *   effectiveWidth  = Math.floor(aspect < 1 ? widthPx * aspect : widthPx)
 *   effectiveHeight = Math.floor(effectiveWidth / aspect)
 * so the tier the UI shows is the LONG EDGE.
 */
export const dimsForTier = (
  longEdge: number,
  aspect: number,
): { w: number; h: number; areaPx: number } => {
  const a = safeAspect(aspect);
  const w = Math.floor(a < 1 ? longEdge * a : longEdge);
  const h = Math.floor(w / a);
  return { w, h, areaPx: w * h };
};

/**
 * Largest long edge whose w*h fits `areaPx` at this aspect. Inverse of
 * dimsForTier, and CONSERVATIVE by construction: because dimsForTier floors the
 * width first, this may under-estimate by one step but never over-estimates.
 */
export const longEdgeForArea = (areaPx: number, aspect: number): number => {
  const a = safeAspect(aspect);
  return Math.floor(Math.sqrt(a < 1 ? areaPx / a : areaPx * a));
};

// -----------------------------------------------------------------------------
// 6. THE PROBE — bounded binary search, memoised, session-cached, single-flight
// -----------------------------------------------------------------------------

const MAX_DIM_STEPS = 8;
const MAX_AREA_STEPS = 6;

/** Strip search: 65535 x 1 is 256 KB, so this arm is effectively free. */
const probeMaxDim = async (): Promise<number> => {
  if (!canAllocate(SAFE_FLOOR_DIM, 1) || !canAllocate(1, SAFE_FLOOR_DIM)) return SAFE_FLOOR_DIM;
  let lo = SAFE_FLOOR_DIM;
  let hi = HARD_MAX_DIM;
  for (let i = 0; i < MAX_DIM_STEPS && hi - lo > 256; i++) {
    const mid = Math.floor((lo + hi) / 2);
    if (canAllocate(mid, 1) && canAllocate(1, mid)) lo = mid;
    else hi = mid - 1;
    await rest(0); // yield so the probe never blocks a frame
  }
  return lo;
};

/**
 * Area search over SQUARE-ish surfaces.
 *
 * WHY SQUARE IS VALID FOR EVERY ASPECT: every engine models the limit as
 * (area cap) AND (dimension cap) independently — Blink kMaximumCanvasArea +
 * kMaximumCanvasSize, WebKit maxCanvasArea, Gecko gfx.max-alloc-size — and under
 * pure memory pressure bytes are bytes. So ONE probe serves every aspect and the
 * cache is aspect-independent.
 *
 * WHY THE GEOMETRIC MEAN: area scales as L^2, so the geometric midpoint is the
 * true midpoint in cost-space. Over [2048^2, 2^28] the first probe lands at
 * ~27 MP (108 MB) instead of the arithmetic ~96 MP (384 MB) — same convergence,
 * a quarter of the peak allocation. Do NOT "simplify" this back to (lo+hi)/2.
 *
 * MONOTONICITY IS ASSUMED ("if A allocates then any A' < A allocates"). True for
 * the engines' constants, violable under heap fragmentation — in which case the
 * search converges LOW, i.e. it fails toward safer. Never present the result to
 * the user as a hard device spec.
 */
const probeMaxArea = async (maxDim: number): Promise<number> => {
  const budget = Math.min(probeBudgetAreaPx(), HARD_MAX_AREA, maxDim * maxDim);
  if (budget <= SAFE_FLOOR_AREA) return SAFE_FLOOR_AREA;
  if (!canAllocate(SAFE_FLOOR_DIM, SAFE_FLOOR_DIM)) return SAFE_FLOOR_AREA;

  let lo = SAFE_FLOOR_AREA;
  let hi = budget;
  for (let i = 0; i < MAX_AREA_STEPS && hi / lo > 1.12; i++) {
    const midArea = Math.floor(Math.sqrt(lo * hi)); // geometric bisection
    const side = Math.min(maxDim, Math.max(1, Math.floor(Math.sqrt(midArea))));
    if (canAllocate(side, side)) {
      lo = side * side;
      await rest(0);
    } else {
      hi = Math.max(lo, side * side - 1);
      // A failed probe just asked the engine for hundreds of MB. Give it a beat
      // to reclaim, or the next probe fails against our own corpse and the
      // search converges far too low.
      await rest(80);
    }
  }
  return lo;
};

let memo: CanvasLimits | null = null;
let inflight: Promise<CanvasLimits> | null = null;

const cacheKey = (): string => {
  const ua = typeof navigator !== 'undefined' ? navigator.userAgent : 'nav?';
  const dpr = typeof devicePixelRatio === 'number' ? devicePixelRatio : 1;
  return `${SCHEMA}|${inWorker() ? 'worker' : 'window'}|${dpr}|${ua}`;
};

const readCache = (): CanvasLimits | null => {
  try {
    if (typeof sessionStorage === 'undefined') return null;
    const raw = sessionStorage.getItem(cacheKey());
    if (!raw) return null;
    const v = JSON.parse(raw) as CanvasLimits;
    if (!v || typeof v.maxAreaPx !== 'number' || typeof v.maxDimPx !== 'number') return null;
    if (!(v.maxAreaPx >= SAFE_FLOOR_AREA) || !(v.maxDimPx >= SAFE_FLOOR_DIM)) return null;
    return { ...v, source: 'cache', costMs: 0 };
  } catch {
    return null; // private mode / quota / disabled storage
  }
};

const writeCache = (v: CanvasLimits): void => {
  try {
    if (typeof sessionStorage === 'undefined') return;
    sessionStorage.setItem(cacheKey(), JSON.stringify(v));
  } catch {
    /* ignore */
  }
};

/**
 * Measure (or recall) this realm's real ceiling. Safe to call from anywhere and
 * as often as you like: single-flight and memoised for the session.
 *
 * WHEN: call it when the export sheet OPENS, not at app boot — at boot it
 * competes with the blazeface download and the first layout+render.
 *
 * WHERE: prefer running it INSIDE the render worker. A fatal allocation kills a
 * worker (recoverable); the same allocation on the main thread kills the tab and
 * the user's whole session. `createSurface()` branches on `typeof document` so
 * the identical code runs in both realms — and `realm` records which one you got.
 *
 * RE-PROBE (`force = true`) after anything that changes the memory picture —
 * notably once live video fragments are playing, since decoders and their
 * surfaces hold significant memory concurrently with the export and a limit
 * probed on an idle page will over-promise.
 *
 * sessionStorage, not localStorage: capability changes with OS updates and
 * memory pressure, so a session is the right TTL.
 */
export const probeMaxCanvas = async (force = false): Promise<CanvasLimits> => {
  if (!force && memo) return memo;
  if (!force) {
    const cached = readCache();
    if (cached) {
      memo = cached;
      return cached;
    }
  }
  if (inflight) return inflight;

  inflight = (async (): Promise<CanvasLimits> => {
    const t0 = Date.now();
    const realm: CanvasLimits['realm'] = inWorker() ? 'worker' : 'window';
    try {
      const maxDimPx = await probeMaxDim();
      const maxAreaPx = await probeMaxArea(maxDimPx);
      // Read AFTER the probe, because `probeMaxArea` is what calls
      // `probeBudgetAreaPx` — this is that run's own verdict, not a stale one.
      const blind = lastProbeBudgetWasBlind();
      const out: CanvasLimits = {
        maxAreaPx,
        maxDimPx,
        source: 'probe',
        realm,
        costMs: Date.now() - t0,
        probedAt: Date.now(),
      };
      // A MEASUREMENT TAKEN UNDER A CEILING WE GUESSED IS PROVISIONAL.
      //
      // `probeMaxArea` searches up to `probeBudgetAreaPx()`, so when the GPU
      // probe came back blank the search stopped at SAFE_FLOOR_AREA*4 — 16.7 MP
      // against the 268 MP a real 16384 answer allows, a 16x cut — and the
      // number it found is a fact about the guess, not about the device. It was
      // then written to sessionStorage as `source: 'probe'`, indistinguishable
      // from a genuine measurement, and `readCache` only checks it clears the
      // floor. So one blank WebGL probe in the moment the export sheet first
      // opened deleted the top rungs of the size ladder for the rest of the
      // browser session AND SURVIVED THE RELOAD that would have cured it.
      //
      // Neither persisted nor memoised while the GPU class is merely UNKNOWN,
      // so the next open re-probes and finds the truth. Bounded: after
      // BLANK_GL_PROBE_RETRIES the class settles to known-absent, `blind` goes
      // false, and a realm that really has no WebGL caches exactly as before.
      if (!blind) {
        writeCache(out);
        memo = out;
      }
      return out;
    } catch {
      const out: CanvasLimits = {
        maxAreaPx: SAFE_FLOOR_AREA,
        maxDimPx: SAFE_FLOOR_DIM,
        source: 'floor',
        realm,
        costMs: Date.now() - t0,
        probedAt: Date.now(),
      };
      memo = out;
      return out;
    } finally {
      inflight = null;
    }
  })();

  return inflight;
};

/** Alias kept for the published integration contract. Same single-flight instance. */
export const getCanvasLimits = probeMaxCanvas;

/** Cheap predicate for code that already holds the limits. */
export const isFeasible = (w: number, h: number, l: CanvasLimits): boolean =>
  w > 0 && h > 0 && w <= l.maxDimPx && h <= l.maxDimPx && w * h <= l.maxAreaPx;

/**
 * Default ladder rungs. 30000 and 24000 are DELIBERATELY ABSENT: computed
 * against the most generous cap in any shipping engine (2^28) they are
 * impossible at all four UI aspects (0.5625, 0.666, 1, 1.77) on all four
 * engines. Offering them was the bug.
 */
export const DEFAULT_TIER_PRESETS: readonly number[] = [16384, 12000, 8192, 4096, 2048];

/**
 * The achievable export ladder, DERIVED from the measurement.
 *
 * Returns descending long edges, always non-empty (2048 is the guaranteed
 * floor), measured ceiling first so MAX starts at the truth rather than a wish.
 *
 * Reference ladders at aspect 0.666:
 *   iOS legacy cap (16.7 MP)   -> [4992, 4096, 2048]
 *   owner's phone  (44.7 MP)   -> [8128, 4096, 2048]
 *   Firefox        (125.0 MP)  -> [13696, 12000, 8192, 4096, 2048]
 *   Chrome desktop (268.4 MP)  -> [20032, 16384, 12000, 8192, 4096, 2048]
 * and the same Chrome desktop at aspect 1.0 -> [16384, 12000, 8192, 4096, 2048].
 *
 * NOTE FOR THE UI: the top rung is non-round AND aspect-reactive. Any copy that
 * says "30 000 px" or "16K — desktop only" is now false; render this number and
 * re-render it when `aspect` changes.
 */
export const deriveTiers = (
  limits: CanvasLimits,
  aspect: number,
  presets: readonly number[] = DEFAULT_TIER_PRESETS,
): number[] => {
  // The long edge IS the larger side by construction, so the per-dimension cap
  // applies to it directly and the short side is covered for free.
  const ceiling = Math.min(longEdgeForArea(limits.maxAreaPx, aspect), limits.maxDimPx, 30000);

  const out: number[] = [];
  const push = (v: number) => {
    const n = Math.floor(v);
    if (n >= SAFE_FLOOR_DIM && !out.includes(n)) out.push(n);
  };

  // The measured ceiling, floored to a multiple of 64 so the JPEG encoder gets
  // whole MCUs and the number reads as deliberate in the UI.
  push(Math.floor(ceiling / 64) * 64);
  for (const p of presets) if (p <= ceiling) push(p);
  push(SAFE_FLOOR_DIM);

  return out.sort((a, b) => b - a);
};

/** The single number the MAX row should display for the current aspect. */
export const maxTierForAspect = (limits: CanvasLimits, aspect: number): number =>
  deriveTiers(limits, aspect)[0];

/**
 * The ladder for an export the user ASKED for at a specific size.
 *
 * `deriveTiers` answers "what can this device do". This answers "what should we
 * try, given they picked 8K". Those differ, and conflating them is how you get
 * either of the two failures we actually shipped:
 *
 *   - starting at the measured ceiling ignores the pick and silently hands back
 *     a different size than the one on the button;
 *   - offering ONLY the pick means one rejected tier is a dead end, which is
 *     precisely the "click export, get nothing" report.
 *
 * So: the pick is the top rung — honoured even when it is above the measured
 * ceiling, because a measurement is a snapshot and being wrong in the generous
 * direction costs one fast rejection — and everything strictly below it in the
 * derived ladder is the fallback. `preferred === null` means MAX: no pick to
 * honour, use the measurement.
 *
 * Pure, total, and swept in selfTest: it never throws, never returns an empty
 * ladder when one was available, and is always strictly descending.
 */
export const composeTiers = (
  preferred: number | null,
  ladder: readonly number[],
): number[] => {
  const clean = ladder
    .filter((t) => Number.isFinite(t) && t >= 1)
    .slice()
    .sort((a, b) => b - a);
  if (preferred === null || !Number.isFinite(preferred) || preferred < 1) return clean;
  const p = Math.floor(preferred);
  return [p, ...clean.filter((t) => t < p)];
};

/** Reset for tests, or for a retry after the user closed other memory-hungry tabs. */
export const _resetCanvasLimits = (): void => {
  memo = null;
  inflight = null;
  glMaxTextureCache = null;
  try {
    if (typeof sessionStorage !== 'undefined') sessionStorage.removeItem(cacheKey());
  } catch {
    /* ignore */
  }
};

// -----------------------------------------------------------------------------
// 7. SOURCE-SIDE PROOF — free, definitive, runs on the live surface
// -----------------------------------------------------------------------------

/**
 * Write a sentinel into the far corner and read it back. Call IMMEDIATELY after
 * getContext — before the background fill and before any image decode.
 *
 * This is the whole silent-failure defence and it costs one pixel. It converts
 * the render itself into a probe at zero extra allocation and fails in ~1 ms
 * instead of ~30 s. A surface that fails here will drop every subsequent draw
 * and then encode to black.
 *
 * THE PROBE DOES NOT REPLACE THIS. WebKit enforces a per-PAGE canvas memory
 * budget and can discard the backing store of an already-valid canvas later, so
 * probeMaxCanvas() is a snapshot, never a promise. Drop this check and the
 * black-JPEG bug returns unfixed on exactly the owner's platform.
 */
export const assertSurfaceLive = (ctx: Ctx2D, w: number, h: number): boolean => {
  try {
    const prev = ctx.fillStyle;
    ctx.fillStyle = `rgb(${SENTINEL_R},${SENTINEL_G},${SENTINEL_B})`;
    ctx.fillRect(w - 1, h - 1, 1, 1);
    const d = ctx.getImageData(w - 1, h - 1, 1, 1).data;
    ctx.fillStyle = prev;
    return (
      Math.abs(d[0] - SENTINEL_R) <= CHANNEL_TOLERANCE &&
      Math.abs(d[1] - SENTINEL_G) <= CHANNEL_TOLERANCE &&
      Math.abs(d[2] - SENTINEL_B) <= CHANNEL_TOLERANCE &&
      d[3] >= SENTINEL_ALPHA_MIN
    );
  } catch {
    return false;
  }
};

export interface BlankSample {
  blank: boolean;
  min: number;
  max: number;
  mean: number;
}

/**
 * Sample small rects INSIDE known content and report whether anything landed.
 *
 * Sampling arbitrary points would be wrong: a legitimate collage on a black
 * background is mostly background, so "the page is dark" is not evidence. Pass
 * `layoutItems[i].bounds` — a working render MUST have a photograph there.
 *
 * Thresholds are lifted verbatim from lib/video.ts analyzeFrame() so the
 * codebase keeps ONE definition of "blank".
 */
export const sampleIsNonBlank = (
  ctx: Ctx2D,
  boxes: readonly Box[],
  maxBoxes = 6,
): BlankSample => {
  let min = 1;
  let max = 0;
  let sum = 0;
  let n = 0;
  const step = Math.max(1, Math.floor(boxes.length / maxBoxes));

  for (let b = 0; b < boxes.length && n < maxBoxes * 64; b += step) {
    const box = boxes[b];
    const sx = Math.max(0, Math.floor(box.x + box.w / 2) - 4);
    const sy = Math.max(0, Math.floor(box.y + box.h / 2) - 4);
    let data: Uint8ClampedArray;
    try {
      data = ctx.getImageData(sx, sy, 8, 8).data;
    } catch {
      continue;
    }
    for (let i = 0; i < data.length; i += 4) {
      const lum = (data[i] * 299 + data[i + 1] * 587 + data[i + 2] * 114) / 255000;
      if (lum < min) min = lum;
      if (lum > max) max = lum;
      sum += lum;
      n++;
    }
  }

  if (n === 0) return { blank: true, min: 0, max: 0, mean: 0 };
  const mean = sum / n;
  // Same test analyzeFrame uses: flat contrast, or crushed to black, or blown out.
  const blank = max - min < 6 / 255 || mean < 4 / 255 || mean > 251 / 255;
  return { blank, min, max, mean };
};

// -----------------------------------------------------------------------------
// 8. BLOB VALIDATION — header truth, and why a byte-length floor is not enough
// -----------------------------------------------------------------------------

export interface BlobCheck {
  ok: boolean;
  /** Machine-readable; the UI maps it to copy, the ladder maps it to a decision. */
  reason: 'ok' | 'empty' | 'not-jpeg' | 'truncated' | 'dimension-mismatch' | 'suspiciously-small';
  encodedW?: number;
  encodedH?: number;
  bytesPerPx?: number;
}

/** Read only what we need; never pull a 20 MB blob into memory to read a header. */
const HEADER_BYTES = 64 * 1024;

/** JPEG dimension fields are 16-bit: anything past 65535 cannot be expressed. */
export const JPEG_MAX_DIM = 65535;

/**
 * Minimal JPEG SOF parser. Segment layout after a two-byte FFCn marker:
 *   [0..1] length  [2] precision  [3..4] height  [5..6] width  [7] components
 * FFC4 (DHT), FFC8 (JPG) and FFCC (DAC) share the C-range but are NOT SOF.
 *
 * Returns null rather than throwing for every malformed input — it is fed
 * whatever the encoder produced, including nothing.
 */
export const readJpegSize = (bytes: Uint8Array): { w: number; h: number } | null => {
  if (bytes.length < 4 || bytes[0] !== 0xff || bytes[1] !== 0xd8) return null; // no SOI
  let i = 2;
  while (i + 9 < bytes.length) {
    if (bytes[i] !== 0xff) {
      i++; // resync over fill bytes / padding
      continue;
    }
    const marker = bytes[i + 1];
    if (marker === 0xff) {
      i++;
      continue;
    }
    if (marker === 0xd8 || marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) {
      i += 2;
      continue;
    }
    if (marker === 0xda || marker === 0xd9) return null; // hit the scan with no SOF
    const len = (bytes[i + 2] << 8) | bytes[i + 3];
    if (len < 2) return null;
    const isSOF =
      marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc;
    if (isSOF) {
      const h = (bytes[i + 5] << 8) | bytes[i + 6];
      const w = (bytes[i + 7] << 8) | bytes[i + 8];
      return w > 0 && h > 0 ? { w, h } : null;
    }
    i += 2 + len;
  }
  return null;
};

/**
 * Bytes-per-pixel floor for "this is probably not a solid colour".
 *
 * MEASURED, NOT ASSUMED — and the measurement falsified the first draft. I
 * reasoned a priori that a blank JPEG costs "a couple of bits per MCU" and
 * picked 0.015. A fixture killed it. Real numbers at q=92:
 *
 *   solid black, 2727x4094 (11.2 MP) ->   177,405 B = 0.0159 B/px  <- THE ARTIFACT
 *   real photo,  2727x4094 (11.2 MP) -> 1,605,454 B = 0.1438 B/px
 *   real photo,  512x512   (0.26 MP) ->   308,089 B = 1.1753 B/px
 *
 * 4:2:0 still spends ~6 blocks x ~6 bits per 16x16 MCU on nothing, so the blank
 * floor is ~0.016 and the separation is ~9x, NOT the ~100x assumed: 0.015 would
 * have PASSED the exact artifact it exists to catch. 0.04 is the geometric
 * midpoint of the measured gap — 2.5x above the blank floor, 3.6x below the real
 * one — and it is scale-invariant because the cost is per-MCU.
 *
 * CRITICAL: this is a SCREEN, never a verdict. A legitimate collage with one
 * small fragment on a large dark background genuinely lands near the floor, so
 * `suspiciously-small` returns ok:true and must NOT drive a step-down — a blank
 * surface at 8K is equally blank at 4K, so stepping down cannot fix it. The
 * verdict belongs to assertSurfaceLive()/sampleIsNonBlank() at the source, which
 * are definitive and free.
 */
export const MIN_BYTES_PER_PX = 0.04;

/**
 * WHY NOT JUST A BYTE-LENGTH FLOOR: WebKit's black JPEG at 8K is ~700 KB — it
 * clears any plausible absolute floor. Byte length alone cannot distinguish "a
 * big picture" from "a big picture of nothing", and it cannot see the other
 * failure at all (toBlob falling back to the 300x150 default surface, which
 * yields a *small* but perfectly valid file). So this checks three orthogonal
 * things, cheaply: the container is a JPEG at all, the encoded dimensions are
 * the ones we asked for (parsed from the header, ~64 KB read), and the byte
 * budget per pixel is plausible (advisory only).
 *
 * WHAT IT DELIBERATELY DOES NOT DO: re-decode the exported JPEG. A 179 MP JPEG
 * costs ~716 MB to decode, so the validator would become a second, larger copy
 * of the bug it exists to catch.
 */
export const validateExportBlob = async (
  blob: Blob | null,
  expectW: number,
  expectH: number,
): Promise<BlobCheck> => {
  if (!blob || blob.size === 0) return { ok: false, reason: 'empty' };
  if (blob.type && blob.type !== 'image/jpeg') return { ok: false, reason: 'not-jpeg' };

  const head = new Uint8Array(await blob.slice(0, HEADER_BYTES).arrayBuffer());
  const size = readJpegSize(head);
  if (!size) return { ok: false, reason: 'truncated' };

  // Tolerance is +/-1 px per axis ON PURPOSE: the worker floors its height while
  // the main-thread fallback passes an unfloored width/aspect that only agrees
  // via implicit unsigned-long truncation. Do not tighten.
  if (Math.abs(size.w - expectW) > 1 || Math.abs(size.h - expectH) > 1) {
    return { ok: false, reason: 'dimension-mismatch', encodedW: size.w, encodedH: size.h };
  }

  const bytesPerPx = blob.size / Math.max(1, size.w * size.h);
  if (bytesPerPx < MIN_BYTES_PER_PX) {
    return {
      ok: true, // WARNING, not a rejection — see MIN_BYTES_PER_PX
      reason: 'suspiciously-small',
      encodedW: size.w,
      encodedH: size.h,
      bytesPerPx,
    };
  }

  return { ok: true, reason: 'ok', encodedW: size.w, encodedH: size.h, bytesPerPx };
};

// -----------------------------------------------------------------------------
// 9. TIMEOUT — the thing that makes the ladder able to advance at all
// -----------------------------------------------------------------------------

/**
 * Per-attempt budget in ms, scaled to PIXEL COUNT — derived, not picked.
 * The render is DECODE-bound, not fill-bound:
 *   - allocate + memset the backing store  ~0.03 ms/MP (~150 ms at 44.7 MP)
 *   - per fragment: blob fetch 1-5 ms + full-size createImageBitmap of a 12 MP
 *     phone photo (~80-200 ms A12-class, ~30-60 ms A17) + clipped drawImage with
 *     downscale 10-40 ms  => ~250 ms typical, ~500 ms worst
 *   - JPEG encode: phones sustain ~30-80 MP/s single-threaded => 15-30 ms/MP
 *
 * Exact values at aspect 0.666 with 24 fragments (asserted in selfTest — the
 * first draft of these was transcribed from ROUNDED prose, "44.7 MP", and the
 * self-test caught it; the MP figures below are exact px counts, not display
 * roundings):
 *    4096 -> 2727x4094   =  11,164,338 px ->  20,391 ms
 *    8192 -> 5455x8190   =  44,676,450 px ->  28,769 ms   <- the owner's working tier
 *   12000 -> 7992x12000  =  95,904,000 px ->  41,576 ms
 *   16384 -> 10911x16382 = 178,744,002 px ->  62,286 ms
 * The 20 s floor only binds on genuinely small renders (2048px square with no
 * fragments = 9,049 ms raw -> clamped to 20,000).
 *
 * A slow-but-WORKING phone must not be killed: this is not a performance judge.
 * It exists because the hang has no other exit — an OOM-killed worker fires
 * neither onmessage nor onerror, it simply goes quiet forever.
 */
export const attemptTimeoutMs = (areaPx: number, fragments: number): number => {
  const mp = Math.max(0, areaPx) / 1e6;
  const frags = Math.max(0, fragments);
  return Math.min(120000, Math.max(20000, Math.round(8000 + mp * 250 + frags * 400)));
};

export class RenderTimeout extends Error {
  constructor(public readonly ms: number) {
    super(`Render exceeded ${ms} ms`);
    this.name = 'RenderTimeout';
  }
}

/**
 * Race work against the clock, and hand the loser's teardown to `onAbort`.
 *
 * Terminating a timed-out worker is CORRECTNESS, not hygiene: a worker that
 * timed out at 16384px is still holding ~700 MB. If the ladder steps down to
 * 12000px without killing it, the smaller tier allocates against our own corpse
 * and fails too — the step-down cascades into a total failure that looks like
 * "nothing works on this device".
 */
export const withTimeout = <T>(
  work: (signal: { cancelled: boolean }) => Promise<T>,
  ms: number,
  onAbort: () => void,
): Promise<T> => {
  const state = { cancelled: false };
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => {
      state.cancelled = true;
      try {
        onAbort();
      } catch {
        /* ignore */
      }
      reject(new RenderTimeout(ms));
    }, ms);
    work(state).then(
      (v) => {
        clearTimeout(timer);
        if (!state.cancelled) resolve(v);
      },
      (e) => {
        clearTimeout(timer);
        if (!state.cancelled) reject(e);
      },
    );
  });
};

// -----------------------------------------------------------------------------
// 10. THE LADDER — attempt, validate, step down, and SAY WHAT HAPPENED
// -----------------------------------------------------------------------------

export interface TierAttempt {
  /** Long edge, i.e. the number the UI shows. */
  tier: number;
  w: number;
  h: number;
  areaPx: number;
  timeoutMs: number;
  /** 0-based position in the ladder, and how long the ladder is. For progress copy. */
  index: number;
  total: number;
}

/**
 * What a render attempt reports back. Returning a bare Blob is accepted as
 * shorthand for `{ blob }` so a trivial renderer stays a one-liner, but a real
 * worker SHOULD report the taxonomy: `surfaceLive` is the free source-side proof
 * (assertSurfaceLive right after getContext) and `failedImages` separates a
 * decode problem from a size problem.
 */
export interface RenderOutcome {
  blob: Blob | null;
  /** false => the surface is dead => this is a SIZE problem => step DOWN. */
  surfaceLive?: boolean;
  /** >0 => image(s) failed to decode. NOT a size problem; stepping down cannot fix it. */
  failedImages?: number;
  /** Fragments actually drawn. Telemetry. */
  drawn?: number;
}

export interface AttemptControl {
  /** Flips true the moment this attempt's deadline expires. Poll it in long loops. */
  readonly cancelled: boolean;
  /**
   * Register teardown for this attempt — `() => worker.terminate()`. Runs on
   * timeout, on throw, and after success. Guaranteed to run at most once.
   */
  onAbort(fn: () => void): void;
}

export type RenderAtSize = (
  attempt: TierAttempt,
  ctl: AttemptControl,
) => Promise<RenderOutcome | Blob>;

export type RejectReason =
  | 'infeasible'
  | 'timeout'
  | 'threw'
  | 'surface-dead'
  | 'blob-empty'
  | 'blob-not-jpeg'
  | 'blob-truncated'
  | 'blob-dimension-mismatch'
  | 'decode-failure';

export interface AttemptRecord {
  tier: number;
  w: number;
  h: number;
  areaPx: number;
  timeoutMs: number;
  elapsedMs: number;
  ok: boolean;
  reason: 'ok' | RejectReason;
  detail?: string;
  bytesPerPx?: number;
}

export interface FallbackResult {
  ok: boolean;
  /** INVARIANT: ok === false implies blob === null. Never hand back a half-render. */
  blob: Blob | null;
  /** The tier that won, or null. */
  tier: number | null;
  w: number;
  h: number;
  reason: 'ok' | 'no-tiers' | 'exhausted' | 'decode-failure';
  /** Non-fatal notes on the winning render (e.g. a suspiciously low B/px). */
  warnings: string[];
  /** Every tier tried, in order, with why it was rejected. */
  attempts: AttemptRecord[];
  /** One-line human summary for the console / an error toast. */
  log: string;
}

export interface FallbackOptions {
  aspect: number;
  /** Defaults to deriveTiers(limits, aspect) when `limits` is supplied. */
  tiers?: readonly number[];
  /** When supplied, provably-infeasible tiers are skipped without spending a render. */
  limits?: CanvasLimits;
  /** Fragment count (layoutItems.length) — feeds the timeout model. */
  fragments?: number;
  /** Injectable for tests. */
  timeoutMs?: (areaPx: number, fragments: number) => number;
  validate?: (blob: Blob, w: number, h: number) => Promise<BlobCheck>;
  cooldownMs?: (reason: RejectReason) => number;
  sleep?: (ms: number) => Promise<void>;
  onProgress?: (attempt: TierAttempt) => void;
  /**
   * A decode failure is not a size failure: the same image fails at every size,
   * so continuing burns the whole ladder and reports a size problem that never
   * existed. Default true = stop and say so.
   */
  stopOnDecodeFailure?: boolean;
}

/** Cross-realm-safe: `instanceof Blob` is unreliable across worker/window boundaries. */
const isBlobLike = (v: unknown): v is Blob =>
  !!v &&
  typeof (v as Blob).size === 'number' &&
  typeof (v as Blob).slice === 'function' &&
  typeof (v as Blob).arrayBuffer === 'function';

const defaultCooldown = (reason: RejectReason): number => {
  switch (reason) {
    case 'timeout':
      return 800; // the corpse is large; give the engine time to reclaim
    case 'surface-dead':
      return 500;
    case 'infeasible':
    case 'decode-failure':
      return 0;
    default:
      return 300;
  }
};

const BLOB_REASON: Record<string, RejectReason> = {
  empty: 'blob-empty',
  'not-jpeg': 'blob-not-jpeg',
  truncated: 'blob-truncated',
  'dimension-mismatch': 'blob-dimension-mismatch',
};

/**
 * Walk the ladder from the best achievable tier down, and return the first
 * result that is PROVEN good.
 *
 * Every clause here is a specific bug from the old loop:
 *   - the ladder comes from a measurement, so impossible tiers are never tried;
 *   - every attempt has a hard, pixel-count-scaled deadline, so a silent hang
 *     cannot pin the loop forever;
 *   - teardown is mandatory and runs in `finally`, so a timed-out worker cannot
 *     hold ~700 MB while the next tier tries to allocate;
 *   - a returned blob is validated before it is accepted, so a black or
 *     wrong-sized file steps down instead of being handed to the user;
 *   - a decode failure is reported as a decode failure instead of masquerading
 *     as "your device is too small".
 *
 * `render` is a parameter so this whole ladder is unit-testable without React,
 * without a DOM, and without a worker (see selfTest).
 */
export const runWithFallback = async (
  render: RenderAtSize,
  opts: FallbackOptions,
): Promise<FallbackResult> => {
  const aspect = safeAspect(opts.aspect);
  const fragments = opts.fragments ?? 0;
  const budget = opts.timeoutMs ?? attemptTimeoutMs;
  const validate = opts.validate ?? validateExportBlob;
  const cooldown = opts.cooldownMs ?? defaultCooldown;
  const sleep = opts.sleep ?? rest;
  const stopOnDecode = opts.stopOnDecodeFailure ?? true;

  const tiers = (opts.tiers ?? (opts.limits ? deriveTiers(opts.limits, aspect) : []))
    .filter((t) => Number.isFinite(t) && t >= 1)
    .slice()
    .sort((a, b) => b - a);

  const attempts: AttemptRecord[] = [];
  const warnings: string[] = [];

  const finish = (r: Omit<FallbackResult, 'attempts' | 'log' | 'warnings'>): FallbackResult => {
    const tried = attempts
      .map((a) => `${a.tier}px:${a.reason}${a.detail ? `(${a.detail})` : ''}`)
      .join(' -> ');
    const log = r.ok
      ? `export: ${r.tier}px (${r.w}x${r.h}) won${
          attempts.length > 1 ? `; rejected ${tried}` : ''
        }${warnings.length ? `; warnings: ${warnings.join(', ')}` : ''}`
      : `export FAILED (${r.reason}); ${tried || 'no tiers attempted'}`;
    return { ...r, attempts, warnings, log };
  };

  if (tiers.length === 0) {
    return finish({ ok: false, blob: null, tier: null, w: 0, h: 0, reason: 'no-tiers' });
  }

  for (let i = 0; i < tiers.length; i++) {
    const tier = tiers[i];
    const { w, h, areaPx } = dimsForTier(tier, aspect);
    const timeoutMs = budget(areaPx, fragments);
    const attempt: TierAttempt = { tier, w, h, areaPx, timeoutMs, index: i, total: tiers.length };

    // Free pre-filter: never spend a render on a size we already measured as impossible.
    if (opts.limits && !isFeasible(w, h, opts.limits)) {
      attempts.push({
        tier,
        w,
        h,
        areaPx,
        timeoutMs,
        elapsedMs: 0,
        ok: false,
        reason: 'infeasible',
        detail: `> measured ${opts.limits.maxAreaPx}px area / ${opts.limits.maxDimPx}px edge`,
      });
      continue;
    }

    opts.onProgress?.(attempt);

    const t0 = Date.now();
    const teardown: Array<() => void> = [];
    let tornDown = false;
    const runTeardown = () => {
      if (tornDown) return;
      tornDown = true;
      for (const fn of teardown) {
        try {
          fn();
        } catch {
          /* ignore */
        }
      }
    };

    let record: AttemptRecord;
    try {
      const raw = await withTimeout(
        (signal) => {
          const ctl: AttemptControl = {
            get cancelled() {
              return signal.cancelled;
            },
            onAbort: (fn: () => void) => {
              teardown.push(fn);
            },
          };
          return Promise.resolve(render(attempt, ctl));
        },
        timeoutMs,
        runTeardown,
      );

      const out: RenderOutcome = isBlobLike(raw) ? { blob: raw } : raw;
      const elapsedMs = Date.now() - t0;

      if (out.surfaceLive === false) {
        // Definitive size verdict from the source. Step DOWN.
        record = {
          tier,
          w,
          h,
          areaPx,
          timeoutMs,
          elapsedMs,
          ok: false,
          reason: 'surface-dead',
          detail: 'far-corner read-back failed',
        };
      } else if ((out.failedImages ?? 0) > 0) {
        // NOT a size problem — do not step down into a ladder-wide burn.
        record = {
          tier,
          w,
          h,
          areaPx,
          timeoutMs,
          elapsedMs,
          ok: false,
          reason: 'decode-failure',
          detail: `${out.failedImages} fragment(s) failed to decode`,
        };
        attempts.push(record);
        runTeardown();
        if (stopOnDecode) {
          return finish({
            ok: false,
            blob: null,
            tier: null,
            w: 0,
            h: 0,
            reason: 'decode-failure',
          });
        }
        await sleep(cooldown('decode-failure'));
        continue;
      } else if (!out.blob) {
        // Blink's over-limit toBlob fires its callback with null.
        record = { tier, w, h, areaPx, timeoutMs, elapsedMs, ok: false, reason: 'blob-empty' };
      } else {
        const check = await validate(out.blob, w, h);
        if (!check.ok) {
          record = {
            tier,
            w,
            h,
            areaPx,
            timeoutMs,
            elapsedMs,
            ok: false,
            reason: BLOB_REASON[check.reason] ?? 'blob-empty',
            detail:
              check.encodedW !== undefined ? `encoded ${check.encodedW}x${check.encodedH}` : undefined,
            bytesPerPx: check.bytesPerPx,
          };
        } else {
          if (check.reason === 'suspiciously-small') {
            // WARN only. Stepping down cannot fix a blank surface.
            warnings.push(
              `low bytes/px ${check.bytesPerPx?.toFixed(4)} at ${tier}px (may be a dark collage)`,
            );
          }
          attempts.push({
            tier,
            w,
            h,
            areaPx,
            timeoutMs,
            elapsedMs,
            ok: true,
            reason: 'ok',
            bytesPerPx: check.bytesPerPx,
          });
          runTeardown();
          return finish({ ok: true, blob: out.blob, tier, w, h, reason: 'ok' });
        }
      }
    } catch (e) {
      const elapsedMs = Date.now() - t0;
      const timedOut = e instanceof RenderTimeout;
      record = {
        tier,
        w,
        h,
        areaPx,
        timeoutMs,
        elapsedMs,
        ok: false,
        reason: timedOut ? 'timeout' : 'threw',
        detail: timedOut ? `no answer in ${timeoutMs}ms` : String((e as Error)?.message ?? e),
      };
    } finally {
      runTeardown(); // never leave a worker holding the backing store
    }

    attempts.push(record);
    await sleep(cooldown(record.reason as RejectReason));
  }

  return finish({ ok: false, blob: null, tier: null, w: 0, h: 0, reason: 'exhausted' });
};

// -----------------------------------------------------------------------------
// 11. SELF-TEST — runs under plain node, no DOM, no React, no worker
// -----------------------------------------------------------------------------
// Transpile and run:
//   npx esbuild src/lib/exportLimits.ts --bundle --format=esm --outfile=/tmp/el.mjs \
//     && node -e "import('/tmp/el.mjs').then(m=>m.selfTest()).then(r=>{
//          console.log(r.report); process.exit(r.failed ? 1 : 0); })"
//
// Tree-shakeable: nothing at module scope has side effects and App.tsx never
// imports selfTest, so Rollup drops this whole section from the production bundle.

export interface SelfTestReport {
  passed: number;
  failed: number;
  lines: string[];
  report: string;
}

/**
 * Minimal valid JPEG header (SOI + JFIF APP0 + SOF0), padded to `totalBytes`.
 * Return type is deliberately INFERRED as Uint8Array<ArrayBuffer>: annotating it
 * `Uint8Array` widens the buffer to ArrayBufferLike, which TS 5.7+ refuses as a
 * BlobPart.
 */
const synthJpeg = (w: number, h: number, totalBytes: number) => {
  const head = [
    0xff, 0xd8, // SOI
    0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00,
    0x00, 0x01, 0x00, 0x01, 0x00, 0x00, // APP0/JFIF, len 16 — exercises the skip path
    0xff, 0xc0, 0x00, 0x11, 0x08, // SOF0, len 17, precision 8
    (h >> 8) & 0xff, h & 0xff,
    (w >> 8) & 0xff, w & 0xff,
    0x03, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1,
  ];
  const out = new Uint8Array(Math.max(head.length, Math.floor(totalBytes)));
  out.set(head.slice(0, out.length));
  return out;
};

export const selfTest = async (): Promise<SelfTestReport> => {
  const lines: string[] = [];
  let passed = 0;
  let failed = 0;
  const ok = (name: string, cond: boolean, got?: unknown) => {
    if (cond) {
      passed++;
      lines.push(`  ok   ${name}`);
    } else {
      failed++;
      lines.push(`  FAIL ${name}${got !== undefined ? ` -> got ${JSON.stringify(got)}` : ''}`);
    }
  };
  const eq = (name: string, a: unknown, b: unknown) =>
    ok(name, JSON.stringify(a) === JSON.stringify(b), a);

  // --- geometry: must mirror App.generateBlob exactly -------------------------
  lines.push('geometry (mirrors App.tsx generateBlob)');
  eq('4096 @0.666 -> 2727x4094', dimsForTier(4096, 0.666), { w: 2727, h: 4094, areaPx: 2727 * 4094 });
  eq('8192 @0.666 -> 5455x8190', dimsForTier(8192, 0.666), { w: 5455, h: 8190, areaPx: 5455 * 8190 });
  eq('16384 @1 -> 16384x16384', dimsForTier(16384, 1), { w: 16384, h: 16384, areaPx: 268435456 });
  eq('8192 @1.77 -> 8192x4628', dimsForTier(8192, 1.77), { w: 8192, h: 4628, areaPx: 8192 * 4628 });
  ok('30000 @1 is 900 MP (impossible everywhere)', dimsForTier(30000, 1).areaPx === 900000000);
  ok('NaN aspect degrades to square, not NaN', Number.isFinite(dimsForTier(4096, NaN).areaPx));

  // longEdgeForArea must be a CONSERVATIVE inverse at every UI aspect / real cap
  let invOk = true;
  for (const a of [0.5625, 0.666, 1, 1.77]) {
    for (const cap of [16777216, 44690000, 124992400, 268435456]) {
      if (dimsForTier(longEdgeForArea(cap, a), a).areaPx > cap) invOk = false;
    }
  }
  ok('longEdgeForArea never over-estimates (4 aspects x 4 caps)', invOk);

  // --- tier derivation --------------------------------------------------------
  lines.push('deriveTiers (measured ladder, never offers the impossible)');
  const mk = (area: number, dim: number): CanvasLimits => ({
    maxAreaPx: area,
    maxDimPx: dim,
    source: 'probe',
    realm: 'window',
    costMs: 0,
    probedAt: 0,
  });
  eq('iOS legacy 16.7MP @0.666', deriveTiers(mk(16777216, 4194303), 0.666), [4992, 4096, 2048]);
  eq("owner's phone 44.7MP @0.666", deriveTiers(mk(44690000, 4194303), 0.666), [8128, 4096, 2048]);
  eq('Firefox 125MP @0.666', deriveTiers(mk(124992400, 32767), 0.666), [13696, 12000, 8192, 4096, 2048]);
  eq('Chrome 268MP @0.666', deriveTiers(mk(268435456, 65535), 0.666), [20032, 16384, 12000, 8192, 4096, 2048]);
  eq('Chrome 268MP @1.0', deriveTiers(mk(268435456, 65535), 1), [16384, 12000, 8192, 4096, 2048]);
  const worst = deriveTiers(mk(SAFE_FLOOR_AREA, SAFE_FLOOR_DIM), 0.5625);
  ok('never empty even at the floor', worst.length > 0, worst);

  // --- composeTiers: the user's pick vs the measured ceiling ------------------
  lines.push("composeTiers (honour the pick, then fall back)");
  const phone = deriveTiers(mk(44690000, 4194303), 0.666); // [8128, 4096, 2048]
  eq('the pick leads, lower rungs follow', composeTiers(4096, phone), [4096, 2048]);
  eq('a pick ABOVE the ceiling is still tried first', composeTiers(16384, phone), [16384, 8128, 4096, 2048]);
  eq('null means MAX -> the measurement decides', composeTiers(null, phone), [8128, 4096, 2048]);
  eq('a pick equal to a rung is not duplicated', composeTiers(8128, phone), [8128, 4096, 2048]);
  eq('a pick below every rung still gives one attempt', composeTiers(512, phone), [512]);
  eq('empty ladder + a pick is not a dead end', composeTiers(4096, []), [4096]);
  eq('empty ladder + no pick is honestly empty', composeTiers(null, []), []);
  eq('an unsorted ladder is repaired', composeTiers(9000, [2048, 8128, 4096]), [9000, 8128, 4096, 2048]);
  eq('junk rungs are dropped', composeTiers(null, [NaN, 4096, 0, Infinity, 2048]), [4096, 2048]);
  eq('a junk pick degrades to the ladder', composeTiers(NaN, phone), [8128, 4096, 2048]);
  // The two invariants the export path actually depends on.
  let composeOk = true;
  for (const pick of [null, 512, 2048, 4096, 8128, 16384, 30000]) {
    for (const cap of [16777216, 44690000, 268435456]) {
      for (const a of [0.5625, 0.666, 1, 1.77]) {
        const t = composeTiers(pick, deriveTiers(mk(cap, 65535), a));
        for (let i = 1; i < t.length; i++) if (t[i] >= t[i - 1]) composeOk = false; // strictly descending
        if (pick !== null && t[0] !== pick) composeOk = false;                      // the pick always leads
        if (t.length === 0) composeOk = false;                                      // always something to try
      }
    }
  }
  ok('strictly descending, pick-led, never empty (84 combos)', composeOk);
  let ladderOk = true;
  for (const a of [0.5625, 0.666, 1, 1.77]) {
    for (const cap of [16777216, 44690000, 124992400, 268435456]) {
      const l = mk(cap, 65535);
      const t = deriveTiers(l, a);
      for (let i = 1; i < t.length; i++) if (t[i] >= t[i - 1]) ladderOk = false; // strictly descending
      for (const v of t) {
        const d = dimsForTier(v, a);
        if (!isFeasible(d.w, d.h, l)) ladderOk = false;
        if (v >= 24000) ladderOk = false; // 24000/30000 must NEVER appear
      }
    }
  }
  ok('every derived tier is descending, feasible, and < 24000', ladderOk);

  // --- timeout model ----------------------------------------------------------
  lines.push('attemptTimeoutMs (scaled to pixels, not a flat constant)');
  eq('8192 @0.666 x24 frags = 28769ms', attemptTimeoutMs(5455 * 8190, 24), 28769);
  eq('4096 @0.666 x24 frags = 20391ms', attemptTimeoutMs(2727 * 4094, 24), 20391);
  eq('16384 @0.666 x24 frags = 62286ms', attemptTimeoutMs(10911 * 16382, 24), 62286);
  eq('small render clamps UP to the 20s floor', attemptTimeoutMs(2048 * 2048, 0), 20000);
  ok('clamped to 120s', attemptTimeoutMs(900000000, 999) === 120000);
  ok('monotone in area', attemptTimeoutMs(2e8, 12) > attemptTimeoutMs(1e8, 12));

  // --- JPEG header parser -----------------------------------------------------
  lines.push('readJpegSize (proven against synthesized + garbage input)');
  eq('parses SOF past APP0', readJpegSize(synthJpeg(2727, 4094, 4096)), { w: 2727, h: 4094 });
  eq('parses 16-bit max dims', readJpegSize(synthJpeg(65535, 65535, 512)), { w: 65535, h: 65535 });
  const garbage: Array<[string, Uint8Array]> = [
    ['empty', new Uint8Array(0)],
    ['2-byte SOI only', new Uint8Array([0xff, 0xd8])],
    ['PNG magic', new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 0])],
    ['64KB of zeros', new Uint8Array(65536)],
    ['SOI + junk', new Uint8Array([0xff, 0xd8, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])],
    ['SOI + SOS with no SOF', new Uint8Array([0xff, 0xd8, 0xff, 0xda, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0])],
  ];
  let garbageOk = true;
  for (const [, bytes] of garbage) {
    try {
      if (readJpegSize(bytes) !== null) garbageOk = false;
    } catch {
      garbageOk = false;
    }
  }
  ok('6 garbage inputs -> null, never throws', garbageOk);

  // --- blob validation --------------------------------------------------------
  lines.push('validateExportBlob (the black-JPEG artifact is the fixture)');
  const jpg = (w: number, h: number, bytes: number) =>
    new Blob([synthJpeg(w, h, bytes)], { type: 'image/jpeg' });
  const real = await validateExportBlob(jpg(2727, 4094, 1605454), 2727, 4094);
  eq('real photo 0.1438 B/px -> ok', real.reason, 'ok');
  const black = await validateExportBlob(jpg(2727, 4094, 177405), 2727, 4094);
  ok('measured black JPEG 0.0159 B/px -> suspiciously-small', black.reason === 'suspiciously-small', black);
  ok('...and it WARNS (ok:true), never steps down', black.ok === true);
  ok('...0.015 would have passed it', (black.bytesPerPx ?? 1) > 0.015 === true);
  const wrong = await validateExportBlob(jpg(300, 150, 500000), 2727, 4094);
  eq('toBlob fell back to 300x150 -> dimension-mismatch', wrong.reason, 'dimension-mismatch');
  const drift = await validateExportBlob(jpg(2727, 4093, 1605454), 2727, 4094);
  eq('+/-1px floor drift tolerated', drift.reason, 'ok');
  eq('empty blob', (await validateExportBlob(new Blob([]), 10, 10)).reason, 'empty');
  eq(
    'wrong mime',
    (await validateExportBlob(new Blob([new Uint8Array(9999)], { type: 'image/png' }), 10, 10)).reason,
    'not-jpeg',
  );
  eq(
    'truncated',
    (await validateExportBlob(new Blob([new Uint8Array([0xff, 0xd8, 1, 2])], { type: 'image/jpeg' }), 10, 10))
      .reason,
    'truncated',
  );

  // --- source-side proof against a fake context -------------------------------
  lines.push('assertSurfaceLive / sampleIsNonBlank');
  const fakeCtx = (r: number, g: number, b: number, a: number): Ctx2D =>
    ({
      fillStyle: '',
      fillRect: () => undefined,
      getImageData: (_x: number, _y: number, w: number, h: number) => ({
        data: Uint8ClampedArray.from(
          Array.from({ length: w * h * 4 }, (_, i) => [r, g, b, a][i % 4]),
        ),
      }),
    }) as unknown as Ctx2D;
  ok('live surface returns the sentinel -> true', assertSurfaceLive(fakeCtx(127, 0, 255, 255), 8, 8));
  ok('dead surface reads transparent black -> false', !assertSurfaceLive(fakeCtx(0, 0, 0, 0), 8, 8));
  ok('WebKit black-but-opaque -> false', !assertSurfaceLive(fakeCtx(0, 0, 0, 255), 8, 8));
  const boxes: Box[] = [{ x: 0, y: 0, w: 64, h: 64 }];
  ok('flat black inside a layout item -> blank', sampleIsNonBlank(fakeCtx(0, 0, 0, 255), boxes).blank);
  ok('no boxes -> blank (cannot prove content)', sampleIsNonBlank(fakeCtx(1, 2, 3, 255), []).blank);

  // --- the ladder -------------------------------------------------------------
  lines.push('runWithFallback (injected renderer; no DOM, no worker)');
  const fast = {
    aspect: 0.666,
    fragments: 8,
    timeoutMs: () => 25,
    sleep: async () => undefined,
    cooldownMs: () => 0,
  } as const;
  const goodBlob = (w: number, h: number) => jpg(w, h, Math.round(w * h * 0.2));

  // 1. The owner's exact failure shape: hang -> dead surface -> wrong-size blob -> win.
  let aborts = 0;
  const r1 = await runWithFallback(async (a, ctl) => {
    ctl.onAbort(() => {
      aborts++;
    });
    if (a.tier === 16384) return new Promise<Blob>(() => undefined); // silent hang, never settles
    if (a.tier === 12000) return { blob: null, surfaceLive: false };
    if (a.tier === 8192) return { blob: jpg(300, 150, 90000), surfaceLive: true };
    return { blob: goodBlob(a.w, a.h), surfaceLive: true, failedImages: 0 };
  }, { ...fast, tiers: [16384, 12000, 8192, 4096] });
  ok('steps down past a HANG to a real win', r1.ok && r1.tier === 4096, r1.log);
  eq(
    'reports why each tier was rejected',
    r1.attempts.map((a) => a.reason),
    ['timeout', 'surface-dead', 'blob-dimension-mismatch', 'ok'],
  );
  ok('timed-out worker was torn down (no 700MB corpse)', aborts >= 1, aborts);
  ok('winner geometry is reported', r1.w === 2727 && r1.h === 4094, [r1.w, r1.h]);

  // 2. A decode failure must NOT burn the ladder.
  let calls = 0;
  const r2 = await runWithFallback(async () => {
    calls++;
    return { blob: goodBlob(2727, 4094), surfaceLive: true, failedImages: 2 };
  }, { ...fast, tiers: [8192, 4096, 2048] });
  ok('decode failure stops the ladder', !r2.ok && r2.reason === 'decode-failure', r2.log);
  ok('...after exactly ONE attempt', calls === 1, calls);
  ok('...and never returns a partial blob', r2.blob === null);

  // 3. Infeasible tiers are skipped for free (no render spent).
  let rendered = 0;
  const r3 = await runWithFallback(async (a) => {
    rendered++;
    return { blob: goodBlob(a.w, a.h), surfaceLive: true };
  }, { ...fast, tiers: [16384, 8192, 4096], limits: mk(16777216, 4194303) });
  ok('skips measured-impossible tiers without rendering', rendered === 1 && r3.tier === 4096, [rendered, r3.tier]);
  eq('...and says so', r3.attempts.map((a) => a.reason), ['infeasible', 'infeasible', 'ok']);

  // 4. Exhaustion is honest.
  const r4 = await runWithFallback(async () => {
    throw new Error('boom');
  }, { ...fast, tiers: [8192, 4096] });
  ok('all tiers failing -> exhausted, blob null', !r4.ok && r4.reason === 'exhausted' && r4.blob === null);
  eq('every failure recorded', r4.attempts.map((a) => a.reason), ['threw', 'threw']);
  const r5 = await runWithFallback(async () => null as unknown as Blob, { ...fast, tiers: [] });
  ok('no tiers -> no-tiers, never throws', !r5.ok && r5.reason === 'no-tiers');

  // 5. A bare Blob return is accepted, and a dark-but-valid render still wins with a warning.
  const r6 = await runWithFallback(async (a) => jpg(a.w, a.h, 177405), { ...fast, tiers: [4096] });
  ok('bare Blob shorthand works', r6.ok && r6.tier === 4096, r6.log);
  ok('dark render wins but WARNS', r6.warnings.length === 1, r6.warnings);

  // --- probe degrades safely with no canvas ----------------------------------
  lines.push('probeMaxCanvas (headless realm)');
  _resetCanvasLimits();
  ok('canAllocate is false without a canvas, never throws', canAllocate(4096, 4096) === false);
  ok('rejects nonsense dimensions', !canAllocate(0, 10) && !canAllocate(NaN, 10) && !canAllocate(-1, -1));
  const lim = await probeMaxCanvas();
  ok('degrades to the safe floor, never over-promises', lim.maxAreaPx === SAFE_FLOOR_AREA && lim.maxDimPx === SAFE_FLOOR_DIM, lim);
  ok('probe is memoised (second call is free)', (await probeMaxCanvas()).probedAt === lim.probedAt);
  ok('single-flight: 4 concurrent calls -> one result', (await Promise.all([probeMaxCanvas(), probeMaxCanvas(), probeMaxCanvas(), probeMaxCanvas()])).every((x) => x.probedAt === lim.probedAt));
  ok('floor ladder still offers something', deriveTiers(lim, 0.666).length > 0);
  _resetCanvasLimits();

  const report = [`exportLimits selfTest: ${passed} passed, ${failed} failed`, ...lines].join('\n');
  return { passed, failed, lines, report };
};
