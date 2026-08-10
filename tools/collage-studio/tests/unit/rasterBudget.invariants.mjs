/**
 * INVARIANT SWEEP for src/lib/rasterBudget.ts — the ceiling on how much source
 * resolution an offline render may hold at once.
 *
 *   node tests/unit/rasterBudget.invariants.mjs
 *
 * Transpiles and imports the REAL module. No re-implementation: a sweep against
 * a copy grades the copy.
 *
 * WHAT WENT WRONG, AND WHY A SWEEP RATHER THAN A CASE. `prepareOfflineStills`
 * rasterises each source at `dwPx / isw` — destination pixels over the SOURCE
 * PIXELS OF ITS CROP — and its doc claimed "the rasters together are bounded by
 * the canvas area". That is true only for a fragment showing its whole source.
 * With k = srcW / isw (how many crops fit across the source) the raster is k^2
 * times the destination area, and k = 2 is an ordinary cover-fit. Thirty
 * sources at the 4096 rung, mean k = 2, is ~180 MB of resident RGBA next to the
 * canvas, the encoder queue and every clip's decoder; at k = 3 it is 400 MB.
 * Nothing bounded the total. That is the reported crash, and it got WORSE the
 * better the device, because the only limit was a wall clock.
 *
 * A single case cannot grade the fix: the failure lives in the interaction of
 * source count, crop factor, source size and device class, so the matrix is
 * swept — and I8 replays the exact reported scenario against the old formula so
 * the number the fix removes is on the record, not asserted from memory.
 *
 * THE THREE THAT CARRY THE CYCLE
 *   I1  the pool is never exceeded, whatever order sources arrive in. This is
 *       the crash, and it is the only invariant whose failure is a dead tab.
 *   I4  no raster is ever narrower than the thumbnail already bound. The budget
 *       pushes scales DOWN, so without this the fix for a crash would be a
 *       visible softening — trading a loud bug for a quiet one.
 *   I9  the LAST source still gets a real share. Greedy-until-empty also stays
 *       inside the budget; it just gives photo 1-12 archival quality and
 *       abandons photo 13+, which reads as a bug in the output.
 */
import esbuild from 'esbuild';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

const src = readFileSync(join(root, 'src/lib/rasterBudget.ts'), 'utf8');
const { code } = await esbuild.transform(src, { loader: 'ts', format: 'esm' });
const tmp = join(mkdtempSync(join(tmpdir(), 'rasterbudget-')), 'rasterBudget.mjs');
writeFileSync(tmp, code);
const {
  rasterBudgetPx, createRasterLedger, scaleForBudget, rasterDims,
  BYTES_PER_RASTER_PX, CANVAS_WEIGHT, FLOOR_POOL_PX, CEILING_POOL_PX,
} = await import(pathToFileURL(tmp).href);

// mulberry32 — deterministic, so a failure is reproducible from its seed alone.
const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };

// --- the shapes a real collage actually presents -----------------------------
// Sizes: a 12 MP phone photo, a 24 MP mirrorless frame, a 45 MP raw export, and
// a small web image that must not be forced up to meet a budget.
const SOURCES = [
  { w: 4032, h: 3024 },  // 12 MP
  { w: 6000, h: 4000 },  // 24 MP
  { w: 8256, h: 5504 },  // 45 MP
  { w: 1600, h: 1200 },  // small
];
const CANVASES = [
  1280 * 720, 1920 * 1080, 2560 * 1440, 3840 * 2160, 4096 * 2304,
];
const DEVICES = [
  { deviceMemoryGb: 8, gpuMaxTextureSize: 16384 },   // desktop / M-series
  { deviceMemoryGb: 4, gpuMaxTextureSize: 16384 },   // mid Chromebook
  { deviceMemoryGb: 0.5, gpuMaxTextureSize: 4096 },  // the honest low end
  { deviceMemoryGb: null, gpuMaxTextureSize: 16384 },// iPhone A12+ / Safari
  { deviceMemoryGb: null, gpuMaxTextureSize: 8192 }, // iPhone A10-A11
  { deviceMemoryGb: null, gpuMaxTextureSize: 4096 }, // iPhone A7-A9
  { deviceMemoryGb: null, gpuMaxTextureSize: null }, // a realm that tells us nothing
];
const COUNTS = [1, 2, 5, 12, 30, 64];

/**
 * ONE FULL PASS, exactly as `prepareOfflineStills` runs it: walk the sources in
 * order, ask the ledger for a cap, size the raster, commit what it took.
 */
const runPass = (budgetPx, sources) => {
  const ledger = createRasterLedger(budgetPx, sources.length);
  const out = [];
  for (const s of sources) {
    const cap = ledger.capFor();
    const scale = scaleForBudget(s.w * s.h, s.want, cap);
    const dims = rasterDims(s.w, s.h, scale, s.floorW, s.want, cap);
    ledger.commit(dims ? dims.px : 0);
    out.push({ s, cap, dims });
  }
  return { ledger, out };
};

// =============================================================================
// I1  THE POOL IS NEVER EXCEEDED — the crash, in one line.
// =============================================================================
for (let seed = 1; seed <= 60; seed++) {
  const rng = rngOf(seed);
  for (const n of COUNTS) {
    const canvasPx = CANVASES[Math.floor(rng() * CANVASES.length)];
    const dev = DEVICES[Math.floor(rng() * DEVICES.length)];
    const budgetPx = rasterBudgetPx({ canvasPx, ...dev });
    const sources = Array.from({ length: n }, () => {
      const base = SOURCES[Math.floor(rng() * SOURCES.length)];
      // k in [1, 3.5]: 1 = whole source in frame, 3.5 = a tight detail crop.
      const k = 1 + rng() * 2.5;
      const dwPx = 300 + rng() * 1400;
      return { ...base, want: Math.min(1, (k * dwPx) / base.w), floorW: 1024 };
    });
    const { ledger, out } = runPass(budgetPx, sources);
    ok(); if (ledger.usedPx > budgetPx) {
      fail(`I1 seed ${seed} n=${n}: used ${ledger.usedPx} > budget ${budgetPx}`);
    }
    // And the same claim measured from the rasters themselves, not the ledger's
    // own bookkeeping — a ledger that lies about its total would pass above.
    const summed = out.reduce((a, r) => a + (r.dims ? r.dims.px : 0), 0);
    ok(); if (summed > budgetPx) fail(`I1b seed ${seed} n=${n}: rasters ${summed} > budget ${budgetPx}`);
    ok(); if (summed !== ledger.usedPx) fail(`I1c seed ${seed} n=${n}: ledger ${ledger.usedPx} != rasters ${summed}`);
  }
}

// =============================================================================
// I2  EVERY SOURCE IS OFFERED A REAL SLICE while the pool has anything left.
// =============================================================================
for (const n of COUNTS) {
  const l = createRasterLedger(FLOOR_POOL_PX, n);
  for (let i = 0; i < n; i++) {
    const cap = l.capFor();
    ok(); if (cap <= 0) fail(`I2 n=${n}: source ${i} offered cap ${cap} with ${l.remainingPx}px left`);
    l.commit(cap); // worst case: everyone takes its whole slice
  }
  ok(); if (l.usedPx > FLOOR_POOL_PX) fail(`I2b n=${n}: everyone-takes-max overshot (${l.usedPx})`);
  ok(); if (l.capFor() !== 0) fail(`I2c n=${n}: ledger still offering after ${n} commits`);
}

// =============================================================================
// I3  A BUDGETED SCALE IS NEVER ABOVE WHAT GEOMETRY ASKED, NEVER ABOVE 1, AND
//     ITS RASTER FITS THE CAP.
// =============================================================================
for (let seed = 1; seed <= 40; seed++) {
  const rng = rngOf(seed * 7);
  for (const base of SOURCES) {
    const want = rng();
    const cap = Math.floor(1000 + rng() * 40_000_000);
    const s = scaleForBudget(base.w * base.h, want, cap);
    ok(); if (s > Math.min(1, want) + 1e-12) fail(`I3 scale ${s} > want ${want}`);
    ok(); if (s < 0) fail(`I3b negative scale ${s}`);
    const px = base.w * base.h * s * s;
    ok(); if (px > cap * (1 + 1e-9)) fail(`I3c raster ${Math.round(px)} > cap ${cap}`);
  }
}

// =============================================================================
// I4  NEVER SOFTER THAN THE PREVIEW. A budgeted raster narrower than or equal
//     to the thumbnail already bound is refused outright — the fragment keeps
//     what it has. Without this, fixing a crash would ship a softening.
// =============================================================================
for (let seed = 1; seed <= 60; seed++) {
  const rng = rngOf(seed * 13);
  for (const base of SOURCES) {
    const floorW = [256, 512, 1024, 2048][Math.floor(rng() * 4)];
    const want = rng();
    const cap = Math.floor(1 + rng() * 20_000_000);
    const scale = scaleForBudget(base.w * base.h, want, cap);
    const d = rasterDims(base.w, base.h, scale, floorW, want, cap);
    if (d) {
      ok(); if (d.w <= floorW) fail(`I4 raster ${d.w} <= floor ${floorW}`);
      ok(); if (d.w > base.w || d.h > base.h) fail(`I4b upscaled ${d.w}x${d.h} from ${base.w}x${base.h}`);
      ok(); if (d.px !== d.w * d.h) fail(`I4c px ${d.px} != ${d.w}x${d.h}`);
    } else {
      // Refusing is only ever allowed to mean "the thumbnail already carries
      // this much picture" — never "we could have upgraded and didn't".
      //
      // Derived from the CONTINUOUS contract — source, scale, cap — and not
      // from the module's own rounding, so this stays a grader rather than a
      // restatement of the code it grades. One pixel of slack, because the
      // integer path floors every ceiling on purpose.
      const wouldBe = Math.min(base.w, base.w * Math.min(1, scale), Math.sqrt((cap * base.w) / base.h));
      ok(); if (wouldBe > floorW + 1 && scale > 0) fail(`I4d refused ${wouldBe.toFixed(1)} which beats floor ${floorW}`);
    }
  }
}

// =============================================================================
// I5  MONOTONIC IN THE BUDGET — more room never yields a smaller raster. A
//     non-monotonic allocator makes "upgrade your phone" a downgrade.
// =============================================================================
for (const base of SOURCES) {
  for (const want of [0.15, 0.4, 0.85, 1]) {
    let prev = -1;
    for (const cap of [50_000, 250_000, 1_000_000, 4_000_000, 16_000_000, 64_000_000]) {
      const s = scaleForBudget(base.w * base.h, want, cap);
      const d = rasterDims(base.w, base.h, s, 0, want, cap);
      const px = d ? d.px : 0;
      ok(); if (px < prev) fail(`I5 ${base.w}x${base.h} want=${want}: cap ${cap} gave ${px} < ${prev}`);
      prev = px;
    }
  }
}

// =============================================================================
// I6  THE CEILING IS BOUNDED AND SPENDS THE CANVAS FIRST. The canvas, the frame
//     the encoder is holding and the one in flight are not optional; a pool
//     that ignores them hands out room the device cannot honour.
// =============================================================================
for (const dev of DEVICES) {
  let prev = Infinity;
  for (const canvasPx of CANVASES) {
    const b = rasterBudgetPx({ canvasPx, ...dev });
    ok(); if (b < FLOOR_POOL_PX) fail(`I6 budget ${b} under floor ${FLOOR_POOL_PX}`);
    ok(); if (b > CEILING_POOL_PX) fail(`I6b budget ${b} over ceiling ${CEILING_POOL_PX}`);
    ok(); if (b > prev) fail(`I6c a BIGGER canvas (${canvasPx}) got a BIGGER pool (${b} > ${prev})`);
    prev = b;
  }
}
// A realm that reports nothing still renders — it just does not get a big pool.
{
  const b = rasterBudgetPx({ canvasPx: 3840 * 2160, deviceMemoryGb: null, gpuMaxTextureSize: null });
  ok(); if (b !== FLOOR_POOL_PX) fail(`I6d silent realm got ${b}, expected the floor ${FLOOR_POOL_PX}`);
}
// Garbage in is not a crash out: NaN/negative canvas is treated as zero.
for (const canvasPx of [NaN, -1, undefined]) {
  const b = rasterBudgetPx({ canvasPx, deviceMemoryGb: 8, gpuMaxTextureSize: 16384 });
  ok(); if (!Number.isFinite(b) || b < FLOOR_POOL_PX) fail(`I6e canvasPx=${canvasPx} produced ${b}`);
}

// =============================================================================
// I7  A MISSING COMMIT IS THE ONE MISUSE THAT SILENTLY STARVES THE TAIL, so the
//     ledger must stay bounded even when a source takes nothing at all.
// =============================================================================
{
  const l = createRasterLedger(12_000_000, 30);
  let taken = 0;
  for (let i = 0; i < 30; i++) {
    const cap = l.capFor();
    const used = i % 3 === 0 ? 0 : Math.floor(cap * 0.6); // every third source refuses
    l.commit(used); taken += used;
  }
  ok(); if (l.usedPx !== taken) fail(`I7 ledger ${l.usedPx} != taken ${taken}`);
  ok(); if (taken > 12_000_000) fail(`I7b overshoot ${taken}`);
  ok(); if (l.remainingSources !== 0) fail(`I7c ${l.remainingSources} sources left after 30 commits`);
  // The surplus the refusers left must have reached the sources behind them.
  ok(); if (taken < 12_000_000 * 0.5) fail(`I7d roll-forward failed: only ${taken} of 12,000,000 spent`);
}

// =============================================================================
// I8  THE REPORTED CRASH, REPLAYED. Thirty phone photos, k = 2, 4096 rung —
//     what the old geometry-only path would have allocated vs what the pool
//     allows. Both numbers printed, because the fix is the difference.
// =============================================================================
{
  const canvasPx = 4096 * 2304;
  const n = 30;
  const base = { w: 4032, h: 3024 };
  const dwPx = 1100;                    // a fragment about a quarter of a 4096 frame
  const k = 2;                          // an ordinary cover-fit crop
  const want = Math.min(1, (k * dwPx) / base.w);
  const oldPx = n * (base.w * want) * (base.h * want);
  const sources = Array.from({ length: n }, () => ({ ...base, want, floorW: 1024 }));

  for (const dev of DEVICES) {
    const budgetPx = rasterBudgetPx({ canvasPx, ...dev });
    const { ledger } = runPass(budgetPx, sources);
    const mb = (px) => (px * BYTES_PER_RASTER_PX) / 1048576;
    ok(); if (ledger.usedPx > budgetPx) fail(`I8 ${JSON.stringify(dev)}: ${ledger.usedPx} > ${budgetPx}`);
    ok(); if (mb(ledger.usedPx) > 512) fail(`I8b ${JSON.stringify(dev)}: ${mb(ledger.usedPx).toFixed(0)} MB is not a fix`);
    console.log(
      `  30x12MP @4096, ${dev.deviceMemoryGb ?? '—'}GB/tex${dev.gpuMaxTextureSize ?? '—'}: ` +
      `was ${mb(oldPx).toFixed(0)} MB unbounded -> now ${mb(ledger.usedPx).toFixed(0)} MB ` +
      `(pool ${mb(budgetPx).toFixed(0)} MB, canvas charged ${mb(canvasPx * CANVAS_WEIGHT).toFixed(0)} MB)`,
    );
  }
  ok(); if (mbOver(oldPx) < 150) fail(`I8c the scenario stopped being a crash (${mbOver(oldPx).toFixed(0)} MB) — retune the sweep`);
  function mbOver(px) { return (px * BYTES_PER_RASTER_PX) / 1048576; }
}

// =============================================================================
// I8d THE NUMBER THAT ACTUALLY PROVES THE FIX: what the render holds must not
//     MOVE with the photo count or the crop factor.
//
//     One scenario at one size cannot show this. The old path was linear in n
//     and QUADRATIC in k with no ceiling anywhere, so "add twenty more photos"
//     and "crop in tighter" were both allocation decisions the user made
//     without knowing it — which is why the report reads "crashes above 2K"
//     rather than "crashes at n=37". A bound that holds at n=30 and drifts at
//     n=120 has not fixed that; it has moved it.
// =============================================================================
{
  const canvasPx = 4096 * 2304;
  const base = { w: 4032, h: 3024 };
  const dev = { deviceMemoryGb: 8, gpuMaxTextureSize: 16384 };
  const budgetPx = rasterBudgetPx({ canvasPx, ...dev });
  const mb = (px) => (px * BYTES_PER_RASTER_PX) / 1048576;
  const rows = [];
  let worstNew = 0, worstOld = 0;

  for (const [n, k] of [[30, 2], [30, 3], [60, 3], [120, 3.5]]) {
    const want = Math.min(1, (k * 1100) / base.w);
    const sources = Array.from({ length: n }, () => ({ ...base, want, floorW: 1024 }));
    const { ledger } = runPass(budgetPx, sources);
    const oldPx = n * base.w * want * base.h * want;
    worstNew = Math.max(worstNew, ledger.usedPx);
    worstOld = Math.max(worstOld, oldPx);
    rows.push(`  n=${String(n).padStart(3)} k=${k}: was ${mb(oldPx).toFixed(0).padStart(5)} MB -> now ${mb(ledger.usedPx).toFixed(0).padStart(3)} MB`);
    ok(); if (ledger.usedPx > budgetPx) fail(`I8d n=${n} k=${k}: ${ledger.usedPx} > pool ${budgetPx}`);
  }
  rows.forEach((r) => console.log(r));

  // The whole claim in one number: the heaviest collage costs no more resident
  // raster than the lightest one, because the pool — not the content — decides.
  ok(); if (worstNew > budgetPx) fail(`I8e worst case ${worstNew} escaped the pool ${budgetPx}`);
  // And the scenario must still be a real crash on the old path, or this
  // sweep is congratulating itself for bounding something harmless.
  ok(); if (mb(worstOld) < 1000) fail(`I8f the heavy scenario is only ${mb(worstOld).toFixed(0)} MB — retune it`);
  console.log(`  ceiling holds: heaviest ${mb(worstNew).toFixed(0)} MB vs unbounded ${mb(worstOld).toFixed(0)} MB`);
}

// =============================================================================
// I9  FAIR SHARE, NOT GREEDY. The last source in a thirty-photo collage must
//     still be offered a usable slice; greedy-until-empty passes I1 and still
//     ships a render whose back half is thumbnails.
// =============================================================================
//     TWO REGIMES, AND THE PROMISE IS NOT THE SAME IN BOTH. This used to assert
//     "everyone gets a raster" flat, which passed only because the pool was
//     four times bigger than the ceiling now allows. Tightening it exposed the
//     real boundary: an equal share either clears the source's thumbnail or it
//     does not, and the regime is DERIVED here rather than assumed, so the next
//     ceiling change reports the truth instead of failing a stale promise.
for (const n of [12, 30, 64]) {
  const canvasPx = 3840 * 2160;
  const budgetPx = rasterBudgetPx({ canvasPx, deviceMemoryGb: 8, gpuMaxTextureSize: 16384 });
  const FLOOR_W = 1024;
  // Every source is HUNGRY — each would take the whole pool if allowed.
  const sources = Array.from({ length: n }, () => ({ w: 8256, h: 5504, want: 1, floorW: FLOOR_W }));
  const { out } = runPass(budgetPx, sources);
  const caps = out.map((r) => r.cap);
  const got = out.filter((r) => r.dims);

  ok(); if (caps[caps.length - 1] <= 0) fail(`I9 n=${n}: the last source was offered nothing`);

  // ANTI-GREEDY, and it holds in BOTH regimes: an offer never shrinks as the
  // pass walks down. Greedy-until-empty is precisely the allocator whose caps
  // collapse toward zero, so this single line is what separates the two.
  for (let i = 1; i < caps.length; i++) {
    ok(); if (caps[i] < caps[i - 1]) fail(`I9b n=${n}: cap fell ${caps[i - 1]} -> ${caps[i]} at ${i}`);
  }
  // The FIRST source may never exceed an equal slice of the whole pool — that
  // is the greedy failure mode exactly, and the only place the bound is a real
  // claim. A LATER source going over 1/n is roll-forward working as designed:
  // it is spending surplus the sources ahead of it did not need, which is the
  // difference between "fair" and "identical" and is the behaviour we want.
  ok(); if (out[0].dims && out[0].dims.px > budgetPx / n + 1) {
    fail(`I9c n=${n}: the first source took ${out[0].dims.px}, over its 1/${n} share`);
  }
  // Whatever WAS lifted beats the thumbnail — a "fair share" of nothing is not fair.
  ok(); if (got.some((r) => r.dims.w <= FLOOR_W)) fail(`I9d n=${n}: a share landed at or under the thumbnail`);

  // Can an equal share clear the floor at all? w = sqrt(cap * srcW / srcH).
  const equalShare = Math.floor(budgetPx / n);
  const liftable = Math.sqrt((equalShare * 8256) / 5504) > FLOOR_W;
  if (liftable) {
    // Room for everyone means EVERYONE — this is the regime the wish asks for,
    // "the chance to render highest quality images in every photo".
    ok(); if (got.length !== n) fail(`I9e n=${n}: pool affords all ${n} but lifted only ${got.length}`);
  } else {
    // Not enough to lift all of them. The floor makes that safe — every
    // unlifted source keeps the preview, so the worst case is "no upgrade",
    // never a softer frame and never a hole.
    ok(); if (got.length >= n) fail(`I9f n=${n}: claims to lift all ${n} on a share of ${equalShare}px`);
    console.log(`  n=${n}: pool lifts ${got.length}/${n}; the rest keep their ${FLOOR_W}px preview`);
  }
}

// =============================================================================
// I10 THE INTEGER RASTER FITS THE CAP — the bound that a continuous proof does
//     NOT give you, and the failure this sweep actually caught.
//
//     `scaleForBudget` returns the scale where srcPx * s^2 == capPx exactly.
//     Rounding a width and a height UP from an exact fit lands ABOVE it, every
//     time, by a few hundred pixels. Thirty of those under a ledger that
//     believed the number it was handed is a pool that quietly runs over — so
//     the claim is made against `dims.px`, the number that becomes a real
//     canvas, and never against the scale that suggested it.
//
//     Swept past the well-formed cases into the hostile ones on purpose: a cap
//     of NaN loses every comparison it is in, which is exactly how a guard
//     written as `if (w < 2) return null` lets a NaN width through.
// =============================================================================
{
  const HOSTILE = [NaN, undefined, null, -1, 0, 1, 3, 4, 9, 100];
  for (let seed = 1; seed <= 60; seed++) {
    const rng = rngOf(seed * 29);
    for (const base of [...SOURCES, { w: 12000, h: 400 }, { w: 400, h: 12000 }, { w: 3, h: 2 }]) {
      const cap = seed <= HOSTILE.length && rng() < 0.5
        ? HOSTILE[seed - 1]
        : Math.floor(1 + rng() * 30_000_000);
      const want = rng();
      const s = scaleForBudget(base.w * base.h, want, cap);
      const d = rasterDims(base.w, base.h, s, 0, want, cap);
      if (!d) { ok(); continue; }
      ok(); if (!Number.isFinite(d.w) || !Number.isFinite(d.h) || !Number.isFinite(d.px)) {
        fail(`I10 non-finite dims ${d.w}x${d.h} at cap ${cap}`);
      }
      ok(); if (d.px > cap) fail(`I10b ${base.w}x${base.h} cap ${cap}: raster ${d.w}x${d.h}=${d.px} exceeds it`);
      ok(); if (d.w < 2 || d.h < 2) fail(`I10c degenerate raster ${d.w}x${d.h}`);
      ok(); if (d.w > base.w || d.h > base.h) fail(`I10d upscaled ${d.w}x${d.h} from ${base.w}x${base.h}`);
      // Aspect must survive the flooring — a raster that fits the cap by going
      // the wrong shape is a stretched photo, which is worse than a soft one.
      //
      // Stated in PIXELS, not as a ratio. Flooring the height can cost at most
      // one pixel, and one pixel is the whole error however large the raster
      // is; a percentage tolerance calls that same one pixel a 12% stretch at
      // 3x2 and a rounding error at 3000x2000, which grades the raster's SIZE
      // rather than its shape. The height cannot be rounded up to close the
      // gap either — the w*h <= cap proof runs through h <= srcH*w/srcW — so
      // one floored pixel is the correct, and the only available, answer.
      const exactH = (base.h * d.w) / base.w;
      ok(); if (Math.abs(d.h - exactH) > 1) {
        fail(`I10e ${base.w}x${base.h}: h ${d.h} is ${Math.abs(d.h - exactH).toFixed(2)}px off exact ${exactH.toFixed(2)}`);
      }
      // And where a stretch would actually be VISIBLE, hold the ratio too —
      // below ~64px tall nothing is being looked at closely enough for the
      // ratio to be the thing that is wrong.
      if (d.h >= 64) {
        const ar = base.w / base.h, got = d.w / d.h;
        ok(); if (Math.abs(got - ar) > ar * 0.02) {
          fail(`I10f visible aspect drift ${got.toFixed(3)} vs ${ar.toFixed(3)} at ${d.w}x${d.h}`);
        }
      }
    }
  }
}

console.log(`\nrasterBudget.invariants: ${checks} checks, ${fails} failure(s)`);
process.exit(fails ? 1 : 0);
