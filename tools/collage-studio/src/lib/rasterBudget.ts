// src/lib/rasterBudget.ts
// =============================================================================
// HOW MUCH SOURCE RESOLUTION AN OFFLINE RENDER IS ALLOWED TO HOLD AT ONCE.
//
// MASTER: the memory-budget discipline exportLimits.ts already applies to ONE
// allocation, applied instead to a POOL that has to stay resident for the whole
// take — crossed with a scheduler's instinct that a shared budget must be
// divided fairly up front, not handed out first-come until it runs dry.
//
// -----------------------------------------------------------------------------
// THE BUG THIS EXISTS TO KILL
// -----------------------------------------------------------------------------
// `Stage.prepareOfflineStills` rasterises every source to the scale its own
// fragments consume, which is right, and its doc claims "the rasters together
// are bounded by the canvas area", which is WRONG — and the gap between those
// two sentences is the reported crash.
//
// It rasterises the WHOLE SOURCE at the scale the fragment needs, but a
// fragment shows a CROP of its source. Write it out. A fragment `dwPx` device
// pixels wide, showing a crop `isw` source pixels wide, asks for
//
//     scale = dwPx / isw          and rasterises  srcW*scale x srcH*scale
//
// so with k = srcW / isw (the crop factor — how many times the fragment's crop
// fits across the source), the raster is
//
//     (k * dwPx) x (k * dhPx)  =  k^2  x  the destination area.
//
// k is 1 only for a fragment showing its whole source. Collage fragments are
// cropped by construction: cover-fit into a box of a different aspect, plus
// zoom and pan motion. k = 2 is ordinary, k = 3 is a tight detail — and the
// cost is QUADRATIC, so those are 4x and 9x the area the comment assumed.
//
// Thirty sources at the MAX video rung (4096 long edge, ~11 MP canvas) with a
// mean k of 2 is ~45 MP of resident RGBA — 180 MB — sitting alongside the
// export canvas, the encoder's queue, and every live clip's decoder. At k = 3
// it is 400 MB. There was NO GLOBAL CEILING anywhere in the loop: it walked
// every source and allocated whatever geometry asked for. The only bound was a
// 20-second wall clock, which on a FAST machine lets it allocate more, not
// less. That is the "crashes above 2K" report, and it is worse the better the
// device and the more photos are in the collage.
//
// -----------------------------------------------------------------------------
// THE SHAPE OF THE FIX
// -----------------------------------------------------------------------------
// A total pixel budget for the pool, derived from what the device says it has,
// and divided by FAIR SHARE WITH ROLL-FORWARD: each source may claim at most an
// equal slice of what is left, and whatever it does not use rolls forward to
// the ones behind it. So a modest source costs its true size and a greedy one
// is capped — it can never eat the budget and leave the tail on thumbnails.
//
// WHY FAIR-SHARE AND NOT GREEDY-UNTIL-EMPTY. Both stay inside the budget. Only
// one of them looks right: greedy gives the first twelve photos archival
// quality and abandons photo thirteen onward at preview resolution, which reads
// as a bug in the output. Uniform-ish softening across all thirty reads as a
// render. Same bytes, and the operator's wish said it exactly — "reduce the
// higher archival quality ... so that higher resolutions don't crash but allow
// for the chance to render highest quality images in EVERY photo".
//
// THE FLOOR IS THE PREVIEW THE USER IS ALREADY LOOKING AT. Degradation stops at
// the thumbnail that is already bound and already resident, so the worst case
// of a too-tight budget is "no upgrade happened" — never a softer frame than
// the preview, never a hole, never a black frame. That is what makes it safe to
// be aggressive with the ceiling on hardware that cannot prove it has room.
//
// ZERO IMPORTS on purpose (exportLimits.ts doctrine): pure arithmetic plus two
// optional navigator reads, so the whole thing sweeps under plain node.
// =============================================================================

// -----------------------------------------------------------------------------
// 1. THE CEILING
// -----------------------------------------------------------------------------

export interface RasterBudgetInputs {
  /**
   * Pixels in the export canvas. It is resident for the whole take too, and the
   * encoder holds frames copied from it, so it is charged against the same RAM
   * before the pool gets any.
   */
  canvasPx: number;
  /** Chromium only, quantised to 0.25/0.5/1/2/4/8. Pass null to force the GPU path. */
  deviceMemoryGb?: number | null;
  /** WebGL MAX_TEXTURE_SIZE. The device-class signal on Safari and Firefox. */
  gpuMaxTextureSize?: number | null;
}

/** One raster pixel is one RGBA canvas pixel: 4 bytes of backing store. */
export const BYTES_PER_RASTER_PX = 4;

/**
 * The canvas is charged at THREE times its area, not one. It is resident
 * itself, the encoder is holding at least one VideoFrame copied out of it, and
 * a third is in flight during `drawImage` composition. Undercharging here is
 * how the pool gets a budget the device cannot actually honour.
 */
export const CANVAS_WEIGHT = 3;

/**
 * Below this the pool is not worth managing: 4 MP spread over thirty sources is
 * ~370x370 each, which loses to most thumbnails, and the thumbnail floor turns
 * the whole pass into a no-op rather than a regression. Keeping a positive
 * floor (instead of 0) means a device that reports nothing still gets an
 * upgrade for a SMALL collage, where the pool is divided few ways.
 */
export const FLOOR_POOL_PX = 4_000_000;

/**
 * Never hand out more than this however much RAM is claimed. 64 MP of RGBA is
 * 256 MB of rasters; past that the bottleneck stops being our pool and starts
 * being everything else on the page, and no collage has ever needed it.
 *
 * WHY 64 AND NOT 128 — `navigator.deviceMemory` SATURATES AT 8. A 64 GB Mac
 * Studio and an 8 GB MacBook Air both report exactly 8, so the top rung is not
 * "a workstation", it is "8 GB or more" and has to be sized for the smallest
 * machine in that class rather than the largest. At 128 MP the Chromium path
 * handed the same MacBook a 512 MB pool while the GPU path below hands the
 * SAME machine 256 MB for tex >= 16384 — one laptop, two pools, decided by
 * which browser it was opened in. The two paths now agree, and they agree on
 * the more careful of the two numbers.
 */
export const CEILING_POOL_PX = 64_000_000;

/**
 * Total resident raster pixels this device may hold for one offline render.
 *
 * `deviceMemory` is a COARSE, DELIBERATELY-LIED-ABOUT signal (quantised, capped
 * at 8, absent outside Chromium secure contexts) so it is used the way
 * exportLimits uses it: as a device CLASS, spending a small fixed fraction, not
 * as an allocation plan. One sixteenth — half of what exportLimits spends on a
 * single transient still allocation, because this pool is held for minutes
 * while decoders and an encoder run beside it.
 */
export const rasterBudgetPx = (i: RasterBudgetInputs): number => {
  const canvasPx = Number.isFinite(i.canvasPx) && i.canvasPx > 0 ? i.canvasPx : 0;

  let poolBytes: number;
  const gb = typeof i.deviceMemoryGb === 'number' && i.deviceMemoryGb > 0 ? i.deviceMemoryGb : 0;
  if (gb > 0) {
    poolBytes = (gb * 1024 * 1024 * 1024) / 16;
  } else {
    // No deviceMemory => Safari/iOS/Firefox. Infer the class from the GPU, same
    // ladder exportLimits.probeBudgetAreaPx walks:
    // A7-A9 report 4096, A10-A11 8192, A12+/M-series and desktop 16384.
    const tex =
      typeof i.gpuMaxTextureSize === 'number' && i.gpuMaxTextureSize > 0 ? i.gpuMaxTextureSize : 0;
    if (tex >= 16384) poolBytes = 256 * 1024 * 1024;
    else if (tex >= 8192) poolBytes = 96 * 1024 * 1024;
    else if (tex >= 4096) poolBytes = 32 * 1024 * 1024;
    else poolBytes = FLOOR_POOL_PX * BYTES_PER_RASTER_PX;
  }

  // THE CEILING IS APPLIED BEFORE THE CANVAS IS CHARGED, and the order is the
  // difference between charging for the canvas and only appearing to. Taking
  // `min(ceiling, pool - canvas)` lets the ceiling swallow the whole canvas
  // charge whenever the device-derived pool sits above it — which is exactly
  // the top-end case, so the rung that renders the biggest canvases was the one
  // rung not paying for them. Clamp first, then subtract: the canvas comes out
  // of whatever we were actually willing to spend.
  const poolPx = Math.min(CEILING_POOL_PX, poolBytes / BYTES_PER_RASTER_PX);
  // The canvas and its encoder copies come out of the same RAM, and they are
  // not optional — the render cannot happen without them, so they are charged
  // first and the pool gets what is left.
  const afterCanvas = poolPx - canvasPx * CANVAS_WEIGHT;

  return Math.floor(Math.max(FLOOR_POOL_PX, afterCanvas));
};

export interface DeviceSignals {
  deviceMemoryGb: number | null;
  gpuMaxTextureSize: number | null;
}

/** Read the device signals this realm actually exposes. Safe anywhere, never throws. */
export const readDeviceSignals = (): DeviceSignals => {
  let deviceMemoryGb: number | null = null;
  let gpuMaxTextureSize: number | null = null;
  try {
    const nav = typeof navigator !== 'undefined'
      ? (navigator as Navigator & { deviceMemory?: number })
      : undefined;
    if (typeof nav?.deviceMemory === 'number' && nav.deviceMemory > 0) {
      deviceMemoryGb = nav.deviceMemory;
    }
  } catch {
    /* locked-down realm */
  }
  try {
    if (typeof document !== 'undefined' && typeof document.createElement === 'function') {
      const c = document.createElement('canvas');
      c.width = 1;
      c.height = 1;
      const gl = (c.getContext('webgl2') || c.getContext('webgl')) as WebGLRenderingContext | null;
      if (gl) {
        const v = gl.getParameter(gl.MAX_TEXTURE_SIZE) as number;
        if (Number.isFinite(v) && v > 0) gpuMaxTextureSize = v;
        const lose = gl.getExtension('WEBGL_lose_context') as { loseContext(): void } | null;
        lose?.loseContext();
      }
      c.width = 0;
      c.height = 0;
    }
  } catch {
    /* no WebGL here */
  }
  return { deviceMemoryGb, gpuMaxTextureSize };
};

/** True when a probe came back carrying at least one usable device signal. */
export const signalsUseful = (s: DeviceSignals | null | undefined): boolean =>
  !!s
  && ((typeof s.deviceMemoryGb === 'number' && s.deviceMemoryGb > 0)
    || (typeof s.gpuMaxTextureSize === 'number' && s.gpuMaxTextureSize > 0));

/**
 * How many further attempts a BLANK probe is worth before we accept that this
 * realm genuinely has nothing to tell us. Small on purpose: the retry exists to
 * survive a transient GPU-process failure, not to poll.
 */
export const BLANK_PROBE_RETRIES = 3;

/**
 * MEMOISE THE ANSWER, NOT THE FAILURE.
 *
 * `MAX_TEXTURE_SIZE` costs a WebGL context to ask for and cannot change while
 * the page lives, so it is read once. The trap is that `getContext('webgl')`
 * DOES fail transiently and for reasons that have nothing to do with the
 * device: Chromium caps live contexts per page and drops the oldest, and a GPU
 * process crash returns null from every `getContext` until it restarts. Caching
 * the FIRST result unconditionally turns one of those moments into a permanent
 * verdict — `{null, null}` reads as "a realm that tells us nothing", which
 * pins the pool at `FLOOR_POOL_PX` for the REST OF THE SESSION. On a machine
 * that could have held sixteen times that. Every export after the blip renders
 * from thumbnails, silently, and reloading the tab is the only cure.
 *
 * So a result is only cached once it CARRIES something. A blank is handed back
 * for this call and re-probed on the next one, up to `retries` further attempts
 * — after which the blank is cached too, because a realm with no
 * `deviceMemory` and no WebGL at all must not pay a context probe per export
 * forever. Both halves matter: without the retry a blip is permanent, without
 * the settle a genuinely blank realm probes without end.
 *
 * The probe is injected rather than imported so the policy sweeps under plain
 * node, where there is no DOM to fail in the first place.
 */
export const createSignalCache = (
  probe: () => DeviceSignals,
  retries: number = BLANK_PROBE_RETRIES,
): (() => DeviceSignals) => {
  const BLANK: DeviceSignals = { deviceMemoryGb: null, gpuMaxTextureSize: null };
  const max = Number.isFinite(retries) && retries > 0 ? Math.floor(retries) : 0;
  let cached: DeviceSignals | null = null;
  let blanks = 0;
  return (): DeviceSignals => {
    if (cached) return cached;
    let got: DeviceSignals;
    try {
      got = probe() || BLANK;
    } catch {
      got = BLANK;
    }
    if (signalsUseful(got)) {
      cached = got;
      return cached;
    }
    blanks += 1;
    if (blanks > max) cached = got;
    return got;
  };
};

// -----------------------------------------------------------------------------
// 2. THE ALLOCATOR
// -----------------------------------------------------------------------------

export interface RasterLedger {
  /**
   * The most the NEXT source may spend: an equal slice of what is left, across
   * the sources still to come. 0 once the ledger is spent or exhausted.
   */
  capFor(): number;
  /**
   * Record what a source actually took (0 for skipped, failed, or
   * kept-at-preview) and advance. MUST be called exactly once per source,
   * including the ones that failed — a missing commit makes every later source
   * think it has a smaller share than it really does.
   */
  commit(usedPx: number): void;
  readonly totalPx: number;
  readonly usedPx: number;
  readonly remainingPx: number;
  readonly remainingSources: number;
}

/**
 * Fair share with roll-forward.
 *
 * ORDER MATTERS, and only in the harmless direction: an early source can never
 * take more than its equal slice, so it can never starve the tail; a frugal
 * source releases its surplus to everyone behind it. The reverse — an early
 * hungry source borrowing from a later frugal one — does not happen, which
 * costs a little sharpness on the first fragments and buys the property that
 * matters: the total is bounded no matter what order the sources arrive in.
 */
export const createRasterLedger = (totalPx: number, sources: number): RasterLedger => {
  const total = Number.isFinite(totalPx) && totalPx > 0 ? Math.floor(totalPx) : 0;
  let remainingPx = total;
  let remainingSources = Number.isFinite(sources) && sources > 0 ? Math.floor(sources) : 0;
  let usedPx = 0;

  return {
    capFor: () => (remainingSources <= 0 ? 0 : Math.floor(remainingPx / remainingSources)),
    commit: (used: number) => {
      const u = Number.isFinite(used) && used > 0 ? Math.floor(used) : 0;
      usedPx += u;
      remainingPx = Math.max(0, remainingPx - u);
      remainingSources = Math.max(0, remainingSources - 1);
    },
    get totalPx() {
      return total;
    },
    get usedPx() {
      return usedPx;
    },
    get remainingPx() {
      return remainingPx;
    },
    get remainingSources() {
      return remainingSources;
    },
  };
};

// -----------------------------------------------------------------------------
// 3. TURNING A CAP INTO A RASTER
// -----------------------------------------------------------------------------

/**
 * The largest scale whose raster fits `capPx`, never above what geometry asked
 * for and never above 1 (a raster larger than its source is bytes with no
 * picture in them).
 */
export const scaleForBudget = (srcPx: number, wantScale: number, capPx: number): number => {
  const want = Number.isFinite(wantScale) && wantScale > 0 ? Math.min(1, wantScale) : 0;
  if (want <= 0) return 0;
  if (!Number.isFinite(srcPx) || srcPx <= 0) return want;
  if (!Number.isFinite(capPx) || capPx <= 0) return 0;
  const wantedPx = srcPx * want * want;
  if (wantedPx <= capPx) return want;
  return Math.min(want, Math.sqrt(capPx / srcPx));
};

export interface RasterDims {
  w: number;
  h: number;
  px: number;
  /** True when the budget, not the fragment's geometry, decided the size. */
  clamped: boolean;
}

/**
 * The raster to actually allocate — or null, meaning "do not allocate anything,
 * keep the preview".
 *
 * THE CAP IS ENFORCED HERE, NOT UPSTREAM, AND THAT IS THE WHOLE POINT.
 * `scaleForBudget` proves `srcPx * s^2 <= capPx` in CONTINUOUS arithmetic, and
 * that proof does not survive `Math.round`: a width and a height each rounded
 * UP push the area past a cap that was chosen to be met exactly. It is a few
 * hundred pixels per source — invisible on its own, and precisely the kind of
 * off-by-a-rounding that turns a bound into a suggestion once thirty of them
 * accumulate under a ledger that trusted the number it was handed. So the
 * function that produces the INTEGERS is the function that owns the ceiling.
 *
 * Three ceilings, each FLOORED, tightest wins:
 *   - the source itself   — never upscale, bytes with no picture in them;
 *   - the wanted scale    — never sharper than a fragment can show;
 *   - the cap             — w <= sqrt(capPx * srcW / srcH), the widest raster
 *                           whose height still fits, which makes
 *                           w*h <= w^2*srcH/srcW <= capPx an identity rather
 *                           than a rounding accident.
 *
 * `floorW` is the width of the thumbnail already bound for this source. Two
 * rules hang off it, and they are the reason a tight budget is a no-op instead
 * of a regression:
 *
 *   - a budgeted raster NARROWER than the thumbnail would make the fragment
 *     SOFTER than the preview the user is looking at, so it is refused;
 *   - a raster no wider than the thumbnail buys no picture and still costs a
 *     full allocation plus a fetch and a decode, so it is refused too.
 *
 * The existing code carried a comment promising the first of these and never
 * implemented it. Under a budget that pushes scales DOWN it stops being
 * theoretical, so it is enforced here where the numbers live.
 *
 * -----------------------------------------------------------------------------
 * `floorW = null` MEANS "THE PREVIEW HAS NOT DECODED YET", WHICH IS NOT ZERO.
 * -----------------------------------------------------------------------------
 * Both rules above need a number, and the caller can only supply one once the
 * thumbnail has landed. Passing 0 for "not yet" reads as "this fragment is
 * drawing nothing, anything is an upgrade" — and the render then sizes a raster
 * against a starved pool, adopts a 258px postage stamp, and reports it as a
 * source that came back FULL. The user gets a soft take and a report that says
 * every source was satisfied. It is the loudest possible version of the quiet
 * failure this whole file exists to avoid, and it fires exactly when someone
 * hits Export the moment the photos are in, which is the normal way to use it.
 *
 * So an unknown floor is its own value, and it admits ONE size: the raster the
 * budget did NOT decide. An UNCLAMPED raster is bounded by the source itself or
 * by `wantScale` — the sampling the destination can actually show — so it is
 * exactly sufficient by construction and cannot be softer than any preview
 * derived from the same source, whatever that preview turns out to be. A
 * clamped one has no such guarantee, so it is refused, and refusing is the safe
 * outcome twice over: the report tells the truth, and the fragment falls back
 * to a preview that is still on its way rather than being pinned forever to a
 * raster sized against a floor of zero.
 */
export const rasterDims = (
  srcW: number,
  srcH: number,
  scale: number,
  floorW: number | null,
  wantScale: number,
  capPx: number,
): RasterDims | null => {
  if (!Number.isFinite(srcW) || !Number.isFinite(srcH) || srcW < 1 || srcH < 1) return null;
  const s = Number.isFinite(scale) && scale > 0 ? Math.min(1, scale) : 0;
  if (s <= 0) return null;
  // NaN must not reach the Math.min below: NaN loses every comparison, so an
  // unsanitised cap would sail through the `w < 2` guard as a NaN width and
  // allocate a garbage canvas. Absent or nonsensical means zero, means refuse.
  const cap = Number.isFinite(capPx) && capPx > 0 ? capPx : 0;

  const byScale = Math.floor(srcW * s);
  const byCap = Math.floor(Math.sqrt((cap * srcW) / srcH));
  const bySource = Math.floor(srcW);
  const w = Math.min(bySource, byScale, byCap);
  // Under two pixels there is no picture to carry, only an allocation.
  if (w < 2) return null;

  const want = Number.isFinite(wantScale) && wantScale > 0 ? Math.min(1, wantScale) : 0;
  // Reported clamped when EITHER ceiling was the budget's: the continuous scale
  // having been pushed down, or the integer cap having bound on its own.
  const clamped = s < want - 1e-9 || byCap < Math.min(bySource, byScale);

  if (floorW === null) {
    // No floor to measure against, so only the size the budget did NOT choose
    // may be adopted. See the header: unclamped is exactly sufficient by
    // construction; clamped is a guess against a floor of zero.
    if (clamped) return null;
  } else {
    const floor = Number.isFinite(floorW) && floorW > 0 ? floorW : 0;
    // Not worth the allocation: the thumbnail already carries this much picture.
    if (w <= floor) return null;
  }

  const h = Math.floor((srcH * w) / srcW);
  if (h < 2) return null;

  return { w, h, px: w * h, clamped };
};
