/**
 * Invariant sweep for ADMISSION — which clips get a realtime decoder, and how a
 * stall is judged.
 *
 * Run: node tests/unit/admission.invariants.mjs
 *
 * It transpiles the REAL `src/lib/admission.ts` (esbuild, types stripped), so
 * the plan measured here is the plan `stage.refreshAdmission` performs.
 *
 * THE WISH THIS EXISTS FOR (collage well, anonymous):
 *   *"Multiple videos should play back at the same time. Concurrency not just one."*
 *
 * WHY A SWEEP. The old pixel guard was a constant that nobody had ever put two
 * phone-shot 4K clips through: it admitted the first and refused the second, on
 * every phone, and the notice on screen made it look like a hardware fact. The
 * failure mode that matters here is not a throw — it is a plan that quietly
 * seats ONE clip when the device could seat two, or seats a load that has
 * already been SEEN to stall. Both are invisible to a happy-path test.
 *
 * I1  NEVER OVER THE COUNT CAP. |live| ≤ maxClips, for every seed.
 * I2  THE BIGGEST PICTURE ALWAYS PLAYS. With admission on and ≥1 candidate, the
 *     top-ranked candidate is live — UNCONDITIONALLY, a count cap of 0 or NaN
 *     included: a budget that admits nothing is a broken page, not a budget.
 * I3  RANK IS AREA DESC, INDEX ASC, and rows come back in that order; the same
 *     input in any other order yields the same rows (order-independent).
 * I4  THE SANITY CEILING HOLDS: with no measured ceiling, livePixels ≤ maxPixels
 *     whenever more than one clip is live.
 * I5  THE MEASURED CEILING HOLDS: livePixels < measuredCeiling whenever more than
 *     one clip is live; and it is checked BEFORE the sanity ceiling, so a load
 *     both would refuse is named 'over-measured-cap'.
 * I6  MONOTONE IN LOAD, NOT IN COUNT. Lowering measuredCeiling never RAISES the
 *     admitted load; raising maxClips or maxPixels never LOWERS it. The COUNT is
 *     deliberately not monotone: rank is by on-screen area, so a roomier budget
 *     can seat one big clip where a tighter one seated two small ones — the
 *     biggest picture playing is the rule, not the most pictures.
 * I7  ONE VERDICT PER CANDIDATE, ids preserved, no duplicates; liveIds are exactly
 *     the 'live' rows; livePixels is exactly their pixel sum.
 * I7b EVERY VERDICT IS JUSTIFIED BY ITS OWN PREFIX: replaying the ranked rows, a
 *     live row fit under the count cap AND both ceilings at that point; a refused
 *     row breached exactly the guard it names, and no EARLIER guard — so a plan
 *     that refuses a clip that fits, or blames the wrong guard, fails here.
 * I8  liveEnabled=false ⇒ every row 'unused', nothing live, livePixels 0.
 * I9  THE WISH, LITERALLY. On the phone caps that iOS actually reports (3 clips,
 *     no deviceMemory), TWO 4K clips are BOTH live; on the OLD 3×1080p ceiling the
 *     second was refused — the sweep proves the constant that pinned it.
 * I10 THE THREE-1080p CASE IS BYTE-IDENTICAL: three 1080p clips are all live under
 *     the phone caps, exactly as before.
 * I11 noteStall ONLY COMES DOWN: min of the two, ignores 0/NaN, first stall sets it.
 * I12 judgeStall: nobody advanced ⇒ 'blocked'; the subject advanced ⇒ 'fine';
 *     others advanced and the subject did not ⇒ 'stalled' with exactly the
 *     non-advancing, UN-PAUSED wanted ids; a PAUSED subject ⇒ 'blocked' even
 *     when siblings move (a starved decoder is un-paused and frozen; a paused
 *     element is permission, power or end-of-media); an unknown subject or an
 *     empty panel ⇒ 'fine' (the probe has nothing to accuse). Clips that do not
 *     want to play never count as advancing OR stalled. Plus a table in the
 *     STAGE's vocabulary — ended, power-paused, buffering, mid-wrap — so the
 *     wiring's exclusions are pinned where the judge can see them.
 * I13 CONVERGENCE. Feed the plan its own stalls: record a stall at the current live
 *     load, re-plan; the admitted LOAD strictly decreases every round (a smaller
 *     clip may be swapped IN for a refused big one — more pictures moving under a
 *     lower load is the point) until one clip is left, and past MAX_STALL_ROUNDS
 *     `settleStall` collapses the plan to ONE decoder outright — a stall can
 *     never loop the Stage forever, and never past the bound.
 * I14 TOTAL. Null candidates, missing fields, NaN pixels, negative caps: a probe
 *     callback is the last place allowed to take the app down. Nonsense pixels
 *     are charged the UNKNOWN rate, never 1 — a stack of junk is not free.
 * I15 capsForSignals: mobile ≤ desktop on both axes; every ceiling holds two DCI
 *     4K clips plus a 1080p one (so two phone 4K clips of ANY 4K shape ALWAYS
 *     fit, with a 1080p beside them); any 1080p stack the count cap allows fits;
 *     an iPhone (no memory signal) is 3 clips / 2×DCI + 1×HD; monotone in cores
 *     and in REPORTED memory; an unreported desktop sits in the middle tier.
 */
import esbuild from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

const load = async (rel, tag) => {
  const out = join(mkdtempSync(join(tmpdir(), `${tag}-`)), `${tag}.mjs`);
  await esbuild.build({
    entryPoints: [join(root, rel)],
    outfile: out,
    bundle: true,
    format: 'esm',
    platform: 'neutral',
    target: 'es2020',
    logLevel: 'silent',
  });
  return import(pathToFileURL(out).href);
};

const A = await load('src/lib/admission.ts', 'admission');
const { planAdmission, noteStall, settleStall, judgeStall, capsForSignals, pixelCost, HD_STREAM_PIXELS, UHD_STREAM_PIXELS, DCI_4K_STREAM_PIXELS, UNKNOWN_SOURCE_PIXELS, MAX_STALL_ROUNDS } = A;

let checks = 0;
const ok = (cond, msg) => { checks++; assert.ok(cond, msg); };
const eq = (a, b, msg) => { checks++; assert.deepEqual(a, b, msg); };

const mulberry = (seed) => () => {
  seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const SIZES = [
  [640, 360], [854, 480], [1280, 720], [1920, 1080], [1080, 1920], [1170, 2532],
  [2560, 1440], [3840, 2160], [2160, 3840], [4096, 2160], [7680, 4320],
];
const mkCands = (rnd, n) => {
  const out = [];
  for (let i = 0; i < n; i++) {
    const [w, h] = SIZES[Math.floor(rnd() * SIZES.length)];
    out.push({ id: `c${i}`, area: Math.floor(rnd() * 5) * 1000, index: i, pixels: w * h });
  }
  return out;
};
const mkCaps = (rnd) => ({
  maxClips: 1 + Math.floor(rnd() * 8),
  maxPixels: rnd() < 0.15 ? 0 : Math.floor((1 + rnd() * 5) * UHD_STREAM_PIXELS),
  measuredCeiling: rnd() < 0.5 ? 0 : Math.floor((0.5 + rnd() * 4) * UHD_STREAM_PIXELS),
});
const shuffle = (rnd, arr) => {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
};
const rankOf = (cands) => cands.slice().sort((a, b) => (b.area - a.area) || (a.index - b.index)).map((c) => c.id);

// ---------------------------------------------------------------------------
// I1–I8, I14 across seeds
// ---------------------------------------------------------------------------
for (let seed = 1; seed <= 3000; seed++) {
  const rnd = mulberry(seed);
  const n = Math.floor(rnd() * 9);
  const cands = mkCands(rnd, n);
  const caps = mkCaps(rnd);
  const plan = planAdmission(cands, caps, true);

  // I7 shape
  eq(plan.rows.map((r) => r.id), rankOf(cands), `I3/I7 seed ${seed}: rows are the ranked ids`);
  eq(plan.liveIds, plan.rows.filter((r) => r.verdict === 'live').map((r) => r.id), `I7 seed ${seed}: liveIds = live rows`);
  const byId = new Map(cands.map((c) => [c.id, c]));
  const sum = plan.liveIds.reduce((s, id) => s + byId.get(id).pixels, 0);
  eq(plan.livePixels, sum, `I7 seed ${seed}: livePixels is the sum`);
  ok(new Set(plan.rows.map((r) => r.id)).size === plan.rows.length, `I7 seed ${seed}: no duplicate rows`);
  for (const r of plan.rows) ok(['live', 'over-clip-cap', 'over-pixel-cap', 'over-measured-cap', 'unused'].includes(r.verdict), `I7 seed ${seed}: verdict vocabulary`);

  // I1
  ok(plan.liveIds.length <= caps.maxClips, `I1 seed ${seed}: ${plan.liveIds.length} live > maxClips ${caps.maxClips}`);
  // I2 — unconditional
  if (n > 0) ok(plan.rows[0].verdict === 'live', `I2 seed ${seed}: the top-ranked clip must be live (got ${plan.rows[0].verdict})`);
  if (n > 0 && seed % 50 === 0) {
    const zero = planAdmission(cands, { ...caps, maxClips: 0 }, true);
    ok(zero.rows[0].verdict === 'live' && zero.liveIds.length === 1, `I2 seed ${seed}: a count cap of 0 still seats the biggest picture, and only it`);
  }
  // I7b — every verdict justified by its own prefix
  {
    let count = 0, px = 0;
    const maxClips = Math.max(1, caps.maxClips);
    for (const r of plan.rows) {
      const c = byId.get(r.id);
      const overCount = count >= maxClips;
      const overMeasured = caps.measuredCeiling > 0 && count > 0 && px + c.pixels >= caps.measuredCeiling;
      const overPixels = caps.maxPixels > 0 && count > 0 && px + c.pixels > caps.maxPixels;
      const expected = overCount ? 'over-clip-cap' : overMeasured ? 'over-measured-cap' : overPixels ? 'over-pixel-cap' : 'live';
      eq(r.verdict, expected, `I7b seed ${seed}: row ${r.id} verdict ${r.verdict} is not justified by its prefix (count ${count}, px ${px}, +${c.pixels})`);
      if (r.verdict === 'live') { count++; px += c.pixels; }
    }
  }
  // I4
  if (plan.liveIds.length > 1 && caps.measuredCeiling === 0 && caps.maxPixels > 0) {
    ok(plan.livePixels <= caps.maxPixels, `I4 seed ${seed}: livePixels ${plan.livePixels} > maxPixels ${caps.maxPixels}`);
  }
  // I5
  if (plan.liveIds.length > 1 && caps.measuredCeiling > 0) {
    ok(plan.livePixels < caps.measuredCeiling, `I5 seed ${seed}: livePixels ${plan.livePixels} >= measured ${caps.measuredCeiling}`);
  }
  // I5 naming: a refusal that BOTH ceilings would make is named measured
  if (caps.measuredCeiling > 0 && caps.maxPixels > 0) {
    let count = 0, px = 0;
    for (const r of plan.rows) {
      const c = byId.get(r.id);
      if (r.verdict === 'live') { count++; px += c.pixels; continue; }
      if (count > 0 && count < caps.maxClips && px + c.pixels >= caps.measuredCeiling && px + c.pixels > caps.maxPixels) {
        ok(r.verdict === 'over-measured-cap', `I5 seed ${seed}: both ceilings refuse → named measured (got ${r.verdict})`);
      }
    }
  }
  // I3 order-independence
  const plan2 = planAdmission(shuffle(rnd, cands), caps, true);
  eq(plan2, plan, `I3 seed ${seed}: shuffled input, same plan`);
  // I6 monotone
  const tighter = planAdmission(cands, { ...caps, measuredCeiling: caps.measuredCeiling > 0 ? Math.floor(caps.measuredCeiling * (0.3 + rnd() * 0.7)) : Math.floor(UHD_STREAM_PIXELS * (0.5 + rnd() * 2)) }, true);
  ok(tighter.livePixels <= plan.livePixels, `I6 seed ${seed}: lower measured ceiling raised the load (${plan.livePixels} → ${tighter.livePixels})`);
  const roomier = planAdmission(cands, { ...caps, maxClips: caps.maxClips + 1 + Math.floor(rnd() * 3), maxPixels: caps.maxPixels === 0 ? 0 : caps.maxPixels * 2 }, true);
  ok(roomier.livePixels >= plan.livePixels, `I6 seed ${seed}: roomier caps lowered the load (${plan.livePixels} → ${roomier.livePixels})`);
  const moreClips = planAdmission(cands, { ...caps, maxClips: caps.maxClips + 1 + Math.floor(rnd() * 3) }, true);
  ok(moreClips.livePixels >= plan.livePixels, `I6 seed ${seed}: a higher count cap alone lowered the load`);
  const morePixels = planAdmission(cands, { ...caps, maxPixels: caps.maxPixels === 0 ? 0 : caps.maxPixels * 2 }, true);
  ok(morePixels.livePixels >= plan.livePixels, `I6 seed ${seed}: a higher pixel ceiling alone lowered the load`);
  // I8
  const off = planAdmission(cands, caps, false);
  ok(off.rows.every((r) => r.verdict === 'unused') && off.liveIds.length === 0 && off.livePixels === 0, `I8 seed ${seed}: liveEnabled=false ⇒ unused`);
}

// ---------------------------------------------------------------------------
// I9 / I10 — the wish, literally, on the caps an iPhone gets
// ---------------------------------------------------------------------------
{
  const iphone = capsForSignals({ mobile: true, cores: 4, memGb: 3 });   // iOS reports no deviceMemory → the Stage defaults 3
  const UHD = UHD_STREAM_PIXELS, HD = HD_STREAM_PIXELS;
  const two4k = [{ id: 'a', area: 100, index: 0, pixels: UHD }, { id: 'b', area: 100, index: 1, pixels: UHD }];
  const now = planAdmission(two4k, { maxClips: iphone.maxLiveClips, maxPixels: iphone.maxLivePixels, measuredCeiling: 0 }, true);
  eq(now.liveIds, ['a', 'b'], 'I9: two 4K phone clips are BOTH live on iPhone caps');
  const old = planAdmission(two4k, { maxClips: 3, maxPixels: 3 * HD, measuredCeiling: 0 }, true);
  eq(old.liveIds, ['a'], 'I9: on the OLD 3×1080p ceiling the second 4K was refused (the constant that pinned it)');
  eq(old.rows[1].verdict, 'over-pixel-cap', 'I9: …and it was named a pixel refusal');
  const three1080 = [0, 1, 2].map((i) => ({ id: `h${i}`, area: 50, index: i, pixels: HD }));
  eq(planAdmission(three1080, { maxClips: iphone.maxLiveClips, maxPixels: iphone.maxLivePixels, measuredCeiling: 0 }, true).liveIds, ['h0', 'h1', 'h2'], 'I10: three 1080p all live now');
  eq(planAdmission(three1080, { maxClips: 3, maxPixels: 3 * HD, measuredCeiling: 0 }, true).liveIds, ['h0', 'h1', 'h2'], 'I10: three 1080p all live before — byte-identical');
  // a 4K + two 1080p also fits on a phone now
  const mixed = [{ id: 'k', area: 90, index: 0, pixels: UHD }, { id: 'h1', area: 50, index: 1, pixels: HD }, { id: 'h2', area: 50, index: 2, pixels: HD }];
  eq(planAdmission(mixed, { maxClips: iphone.maxLiveClips, maxPixels: iphone.maxLivePixels, measuredCeiling: 0 }, true).liveIds, ['k', 'h1', 'h2'], 'I9: 4K + two 1080p all live on a phone');
  // two DCI 4K (4096×2160 — the sensor-crop / cinema shape) are BOTH live, and a 1080p beside two 4K too
  const DCI = DCI_4K_STREAM_PIXELS;
  const twoDci = [{ id: 'a', area: 100, index: 0, pixels: DCI }, { id: 'b', area: 100, index: 1, pixels: DCI }];
  eq(planAdmission(twoDci, { maxClips: iphone.maxLiveClips, maxPixels: iphone.maxLivePixels, measuredCeiling: 0 }, true).liveIds, ['a', 'b'], 'I9: two DCI 4K phone clips are BOTH live on iPhone caps (the 2×UHD ceiling refused the second)');
  const twoPlusHd = [{ id: 'a', area: 100, index: 0, pixels: DCI }, { id: 'b', area: 100, index: 1, pixels: UHD }, { id: 'h', area: 10, index: 2, pixels: HD }];
  eq(planAdmission(twoPlusHd, { maxClips: iphone.maxLiveClips, maxPixels: iphone.maxLivePixels, measuredCeiling: 0 }, true).liveIds, ['a', 'b', 'h'], 'I9: two 4K + a 1080p fill the phone count cap');
  const three4k = [0, 1, 2].map((i) => ({ id: `u${i}`, area: 100, index: i, pixels: UHD }));
  const p3 = planAdmission(three4k, { maxClips: iphone.maxLiveClips, maxPixels: iphone.maxLivePixels, measuredCeiling: 0 }, true);
  eq(p3.liveIds, ['u0', 'u1'], 'I9: a THIRD 4K is refused a-priori on a phone');
  eq(p3.rows[2].verdict, 'over-pixel-cap', 'I9: …named a pixel refusal');
  // an 8K stack is still refused a-priori
  const two8k = [{ id: 'x', area: 1, index: 0, pixels: 7680 * 4320 }, { id: 'y', area: 1, index: 1, pixels: 7680 * 4320 }];
  const p8 = planAdmission(two8k, { maxClips: iphone.maxLiveClips, maxPixels: iphone.maxLivePixels, measuredCeiling: 0 }, true);
  eq(p8.liveIds, ['x'], 'I9: an 8K stack is still refused a-priori on a phone');
  eq(p8.rows[1].verdict, 'over-pixel-cap', 'I9: …named a pixel refusal');
}

// ---------------------------------------------------------------------------
// I11 — noteStall only comes down
// ---------------------------------------------------------------------------
{
  eq(noteStall(0, 5), 5, 'I11: first stall sets it');
  eq(noteStall(5, 9), 5, 'I11: a higher stall says nothing new');
  eq(noteStall(9, 5), 5, 'I11: a lower stall tightens');
  eq(noteStall(9, 0), 9, 'I11: a stall at load 0 is noise');
  eq(noteStall(9, NaN), 9, 'I11: NaN is noise');
  eq(noteStall(NaN, 4), 4, 'I11: NaN ceiling treated as none');
  eq(noteStall(-3, 4), 4, 'I11: negative ceiling treated as none');
  for (let s = 1; s <= 500; s++) { const r = mulberry(s); const a = Math.floor(r() * 1e7), b = Math.floor(r() * 1e7); const out = noteStall(a, b);
    ok(out <= (a > 0 ? a : Infinity) && (b <= 0 || out <= b) && out >= 0, `I11 seed ${s}: monotone`); }
}

// ---------------------------------------------------------------------------
// I12 — judgeStall
// ---------------------------------------------------------------------------
{
  eq(judgeStall([], 'a'), { kind: 'fine', stalled: [] }, 'I12: empty panel is fine');
  eq(judgeStall(null, 'a'), { kind: 'fine', stalled: [] }, 'I12: null panel is fine');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false }], 'zz'), { kind: 'fine', stalled: [] }, 'I12: unknown subject is fine');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false }], 'a'), { kind: 'blocked', stalled: ['a'] }, 'I12: alone and frozen ⇒ blocked');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false }, { id: 'b', wantsPlay: true, advanced: false }], 'a'), { kind: 'blocked', stalled: ['a', 'b'] }, 'I12: everyone frozen ⇒ blocked');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false }, { id: 'b', wantsPlay: true, advanced: true }], 'a'), { kind: 'stalled', stalled: ['a'] }, 'I12: a sibling moves ⇒ stalled');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: true }, { id: 'b', wantsPlay: true, advanced: false }], 'a'), { kind: 'fine', stalled: [] }, 'I12: the subject moved ⇒ fine');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false }, { id: 'b', wantsPlay: false, advanced: true }], 'a'), { kind: 'blocked', stalled: ['a'] }, 'I12: a clip that does not want to play does not count as advancing');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false }, { id: 'b', wantsPlay: false, advanced: false }, { id: 'c', wantsPlay: true, advanced: true }], 'a'), { kind: 'stalled', stalled: ['a'] }, 'I12: a paused-by-choice clip is not stalled');
  // PAUSED is never a budget verdict
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false, paused: true }, { id: 'b', wantsPlay: true, advanced: true }], 'a'), { kind: 'blocked', stalled: [] }, 'I12: a PAUSED subject with a moving sibling is blocked (permission / power), not stalled');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false, paused: false }, { id: 'b', wantsPlay: true, advanced: false, paused: true }, { id: 'c', wantsPlay: true, advanced: true }], 'a'), { kind: 'stalled', stalled: ['a'] }, 'I12: the stalled set excludes paused siblings');
  eq(judgeStall([{ id: 'a', wantsPlay: true, advanced: false, paused: true }, { id: 'b', wantsPlay: true, advanced: false, paused: true }], 'a'), { kind: 'blocked', stalled: [] }, 'I12: everyone paused ⇒ blocked, nobody stalled');
  // THE STAGE'S VOCABULARY — what the wiring must do BEFORE calling the judge
  // (each row is a Stage state and the observation the Stage must produce for it)
  const STAGE_TABLE = [
    // [state, observation the Stage emits for that clip, what the judge must NOT do with it]
    ['ended non-loop clip',        { id: 'x', wantsPlay: false, advanced: false, paused: true },  'never a defendant, never a witness'],
    ['power-paused (off-screen)',  { id: 'x', wantsPlay: true,  advanced: false, paused: true },  'blocked at worst, never stalled'],
    ['still loading first frame',  { id: 'x', wantsPlay: false, advanced: false, paused: false }, 'off the panel (not seated)'],
    ['mid-wrap seek, frames came', { id: 'x', wantsPlay: true,  advanced: true,  paused: false }, 'fine'],
    ['starved decoder',            { id: 'x', wantsPlay: true,  advanced: false, paused: false }, 'stalled when a sibling moves'],
  ];
  const sib = { id: 's', wantsPlay: true, advanced: true, paused: false };
  for (const [state, o, why] of STAGE_TABLE) {
    const j = judgeStall([o, sib], 'x');
    if (!o.wantsPlay) eq(j, { kind: 'fine', stalled: [] }, `I12 table "${state}": ${why}`);
    else if (o.advanced) eq(j, { kind: 'fine', stalled: [] }, `I12 table "${state}": ${why}`);
    else if (o.paused) eq(j, { kind: 'blocked', stalled: [] }, `I12 table "${state}": ${why}`);
    else eq(j, { kind: 'stalled', stalled: ['x'] }, `I12 table "${state}": ${why}`);
    // and as a SIBLING of a frozen un-paused subject: only a seated, advancing one can make it 'stalled'
    const j2 = judgeStall([{ id: 'y', wantsPlay: true, advanced: false, paused: false }, o], 'y');
    eq(j2.kind, (o.wantsPlay && o.advanced) ? 'stalled' : 'blocked', `I12 table "${state}" as witness`);
  }
  for (let s = 1; s <= 2000; s++) {
    const r = mulberry(s);
    const n = 1 + Math.floor(r() * 6);
    const obs = Array.from({ length: n }, (_, i) => ({ id: `c${i}`, wantsPlay: r() < 0.8, advanced: r() < 0.5 }));
    const subj = `c${Math.floor(r() * n)}`;
    const j = judgeStall(obs, subj);
    const wanted = obs.filter((o) => o.wantsPlay);
    const s0 = wanted.find((o) => o.id === subj);
    if (!s0 || s0.advanced) eq(j, { kind: 'fine', stalled: [] }, `I12 seed ${s}: fine`);
    else if (s0.paused) { eq(j.kind, 'blocked', `I12 seed ${s}: paused subject ⇒ blocked`); ok(!j.stalled.includes(subj), `I12 seed ${s}: a paused subject is never in the stalled set`); }
    else {
      const stalled = wanted.filter((o) => !o.advanced).map((o) => o.id);
      eq(j, { kind: wanted.some((o) => o.advanced) ? 'stalled' : 'blocked', stalled }, `I12 seed ${s}: kind + stalled set`);
      ok(j.stalled.includes(subj), `I12 seed ${s}: the subject is in the stalled set`);
    }
  }
}

// ---------------------------------------------------------------------------
// I13 — convergence: feeding the plan its own stalls strictly lowers the load
// ---------------------------------------------------------------------------
let maxRounds = 0;
for (let seed = 1; seed <= 1500; seed++) {
  const rnd = mulberry(seed);
  const cands = mkCands(rnd, 1 + Math.floor(rnd() * 8));
  const caps = { maxClips: 1 + Math.floor(rnd() * 8), maxPixels: rnd() < 0.3 ? 0 : Math.floor((2 + rnd() * 6) * UHD_STREAM_PIXELS), measuredCeiling: 0 };
  let plan = planAdmission(cands, caps, true);
  const byId = new Map(cands.map((c) => [c.id, c]));
  let rounds = 0;
  while (plan.liveIds.length > 1) {
    rounds++;
    const top = byId.get(plan.liveIds[0]).pixels;
    const ceiling = settleStall(caps.measuredCeiling, plan.livePixels, rounds, top);
    ok(ceiling > 0 && ceiling <= plan.livePixels, `I13 seed ${seed}: ceiling recorded at or under the stalled load`);
    ok(ceiling >= top + 1, `I13 seed ${seed}: the ceiling never sinks below the top clip + 1 (the floor)`);
    if (rounds <= MAX_STALL_ROUNDS) eq(ceiling, noteStall(caps.measuredCeiling, plan.livePixels), `I13 seed ${seed}: within the bound, settle == note`);
    caps.measuredCeiling = ceiling;
    const next = planAdmission(cands, caps, true);
    ok(next.livePixels < plan.livePixels, `I13 seed ${seed}: round ${rounds} did not lower the load (${plan.livePixels} → ${next.livePixels})`);
    ok(next.liveIds.length <= caps.maxClips, `I13 seed ${seed}: the count cap still holds mid-convergence`);
    ok(next.rows[0].verdict === 'live', `I13 seed ${seed}: the biggest picture never leaves`);
    if (rounds > MAX_STALL_ROUNDS) eq(next.liveIds.length, 1, `I13 seed ${seed}: past the bound the plan collapses to ONE decoder`);
    plan = next;
    ok(rounds <= MAX_STALL_ROUNDS + 1, `I13 seed ${seed}: runaway (${rounds} rounds for ${cands.length} clips)`);
  }
  if (rounds > maxRounds) maxRounds = rounds;
  ok(plan.liveIds.length === (cands.length > 0 ? 1 : 0), `I13 seed ${seed}: converges to one clip`);
}

// I13b — THE FLOOR: a stale or nonsense load can cost at most the collapse state
{
  const top = 8_294_400;
  eq(settleStall(0, 1_000, 1, top), top + 1, 'I13b: a stall "at 1,000 px" (a stale load) floors at top + 1, not 1,000');
  eq(settleStall(0, 20_000_000, 1, top), 20_000_000, 'I13b: a real load above the floor is recorded as is');
  eq(settleStall(30_000_000, 25_000_000, MAX_STALL_ROUNDS + 1, top), top + 1, 'I13b: past the bound, collapse to one decoder');
  eq(settleStall(0, 0, 1, top), 0, 'I13b: no load, no ceiling (disabled stays disabled)');
  // and one decoder is what the floor means: the top clip alone is seated, a second never is
  const cands = [{ id: 'a', area: 9, index: 0, pixels: top }, { id: 'b', area: 1, index: 1, pixels: 1 }];
  eq(planAdmission(cands, { maxClips: 8, maxPixels: 0, measuredCeiling: top + 1 }, true).liveIds, ['a'], 'I13b: at the floor, exactly one decoder');
}

// ---------------------------------------------------------------------------
// I14 — total
// ---------------------------------------------------------------------------
{
  const junk = [null, undefined, {}, { id: 'a' }, { id: 'b', pixels: NaN, area: 'x', index: null }, { id: 'c', pixels: -5, area: Infinity, index: 2 }, 7, 'str'];
  let p;
  assert.doesNotThrow(() => { p = planAdmission(junk, { maxClips: NaN, maxPixels: -1, measuredCeiling: undefined }, true); }, 'I14: junk candidates do not throw');
  ok(p.liveIds.length === 1 && p.rows[0].verdict === 'live', 'I14: NaN maxClips ⇒ clamped to 1 ⇒ exactly the top is live (and nothing thrown)');
  assert.doesNotThrow(() => planAdmission(null, null, true), 'I14: null everything');
  assert.doesNotThrow(() => planAdmission(undefined, undefined, false), 'I14: undefined everything');
  const p2 = planAdmission(junk, { maxClips: 3, maxPixels: 0, measuredCeiling: 0 }, true);
  eq(p2.rows.map((r) => r.id).sort(), ['a', 'b', 'c'], 'I14: only rows with a string id survive');
  ok(p2.rows.every((r) => r.verdict === 'live') && p2.livePixels === 3 * UNKNOWN_SOURCE_PIXELS, 'I14: junk pixels are charged the UNKNOWN rate each, never 1, never free');
  eq(pixelCost(0, 0, 0, 0), UNKNOWN_SOURCE_PIXELS, 'I14: unknown source charge');
  eq(pixelCost(1920, 1080, 0, 0), 1920 * 1080, 'I14: real frame wins');
  eq(pixelCost(0, 0, 640, 360), 640 * 360, 'I14: hint when no frame');
  eq(pixelCost(-1, 5, 0, 0), UNKNOWN_SOURCE_PIXELS, 'I14: a nonsense frame is unknown, not negative');
}

// ---------------------------------------------------------------------------
// I15 — capsForSignals
// ---------------------------------------------------------------------------
{
  const DCI = DCI_4K_STREAM_PIXELS, HD = HD_STREAM_PIXELS, UHD = UHD_STREAM_PIXELS;
  const seatsOf = (clips, s) => s * DCI + (clips - s) * HD;
  const iphone = capsForSignals({ mobile: true, cores: 4, memGb: 0 });
  eq(iphone, { maxLiveClips: 3, maxLivePixels: seatsOf(3, 2) }, 'I15: iPhone (no memory signal) = 3 clips / two 4K seats + one 1080p');
  eq(capsForSignals({ mobile: true, cores: 6, memGb: 3 }), iphone, 'I15: a phone reporting 3 GB is the same tier');
  const flagship = capsForSignals({ mobile: true, cores: 8, memGb: 8 });
  eq(flagship, { maxLiveClips: 4, maxLivePixels: seatsOf(4, 2) }, 'I15: flagship (Android, reported) = 4 clips / two 4K seats + two 1080p');
  eq(capsForSignals({ mobile: true, cores: 8, memGb: 0 }).maxLiveClips, 3, 'I15: 8 cores with NO memory signal is not a flagship (iPhone by construction)');
  const desk8 = capsForSignals({ mobile: false, cores: 14, memGb: 8 });
  eq(desk8, { maxLiveClips: 8, maxLivePixels: seatsOf(8, 4) }, 'I15: 8+ core desktop with 8 GB = 8 clips / four 4K seats');
  const deskUnknown = capsForSignals({ mobile: false, cores: 14, memGb: 0 });
  eq(deskUnknown, { maxLiveClips: 8, maxLivePixels: seatsOf(8, 3) }, 'I15: desktop with NO memory signal (Safari, Firefox) = middle tier, three 4K seats');
  const desk4lo = capsForSignals({ mobile: false, cores: 4, memGb: 4 });
  eq(desk4lo, { maxLiveClips: 6, maxLivePixels: seatsOf(6, 2) }, 'I15: 4-core low-RAM desktop = 6 clips / two 4K seats');
  const desk2 = capsForSignals({ mobile: false, cores: 2, memGb: 8 });
  eq(desk2, { maxLiveClips: 4, maxLivePixels: seatsOf(4, 4) }, 'I15: 2-core desktop = 4 clips / four 4K seats');
  for (let s = 1; s <= 1000; s++) {
    const r = mulberry(s);
    const cores = 1 + Math.floor(r() * 24), mem = Math.floor(r() * 17);   // 0 = not reported
    const m = capsForSignals({ mobile: true, cores, memGb: mem });
    const d = capsForSignals({ mobile: false, cores, memGb: mem });
    ok(m.maxLiveClips <= d.maxLiveClips && m.maxLivePixels <= d.maxLivePixels, `I15 seed ${s}: mobile ≤ desktop`);
    ok(m.maxLivePixels >= 2 * DCI + HD && d.maxLivePixels >= 2 * DCI + HD, `I15 seed ${s}: two DCI 4K clips plus a 1080p always fit`);
    ok(m.maxLivePixels >= 2 * UHD && d.maxLivePixels >= 2 * UHD, `I15 seed ${s}: two phone 4K clips always fit`);
    ok(m.maxLivePixels >= m.maxLiveClips * HD, `I15 seed ${s}: any 1080p stack the mobile count cap allows fits`);
    ok(d.maxLivePixels >= d.maxLiveClips * HD, `I15 seed ${s}: any 1080p stack the desktop count cap allows fits`);
    ok(m.maxLivePixels < 3 * UHD, `I15 seed ${s}: a third phone 4K is refused a-priori on every phone`);
    const m2 = capsForSignals({ mobile: true, cores: cores + 1, memGb: mem === 0 ? 0 : mem + 1 });
    const d2 = capsForSignals({ mobile: false, cores: cores + 1, memGb: mem === 0 ? 0 : mem + 1 });
    ok(m2.maxLiveClips >= m.maxLiveClips && m2.maxLivePixels >= m.maxLivePixels, `I15 seed ${s}: mobile monotone`);
    ok(d2.maxLiveClips >= d.maxLiveClips && d2.maxLivePixels >= d.maxLivePixels, `I15 seed ${s}: desktop monotone (cores, reported memory)`);
  }
  // desktop 1080p stacks: 8 × 1080p fits at every desktop tier, by construction
  const d = capsForSignals({ mobile: false, cores: 16, memGb: 4 });
  ok(d.maxLivePixels >= 8 * HD, 'I15: eight 1080p clips fit even on the low-RAM desktop tier');
  assert.doesNotThrow(() => capsForSignals(null), 'I15: null signals');
  assert.doesNotThrow(() => capsForSignals({}), 'I15: empty signals');
}

console.log(`admission.invariants: ${checks} checks passed (I13 worst-case convergence: ${maxRounds} rounds)`);
