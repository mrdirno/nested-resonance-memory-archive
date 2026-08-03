/**
 * Invariant sweep for src/lib/fill.ts — the source-first, duplicate-free fill.
 *
 * Run: node tests/unit/fill.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so it
 * proves the shipped code — not a re-implementation. The matrix is source-mix ×
 * slot-count × 40 seeds, because a generative assignment can pass on one seed and
 * fail on the next (scar: count says nothing about coverage — sweep, never one).
 */
import esbuild from 'esbuild';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

const src = readFileSync(join(root, 'src/lib/fill.ts'), 'utf8');
const { code } = await esbuild.transform(src, { loader: 'ts', format: 'esm' });
const tmp = join(mkdtempSync(join(tmpdir(), 'fill-')), 'fill.mjs');
writeFileSync(tmp, code);
const { assignSources, distinctSourceCount, sourceKeyOf, groupBySource } =
  await import(pathToFileURL(tmp).href);

// mulberry32 — a small deterministic PRNG so each seed is a distinct arrangement.
const rngOf = (seed) => () => {
  seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

let photoSeq = 0, clipSeq = 0;
const photo = () => ({ id: `img-${photoSeq++}`, src: '', previewSrc: '', width: 100, height: 100, analysis: {} });
const video = (frames) => {
  const clipId = `clip-${clipSeq++}`;
  const name = `${clipId}.mp4`;
  return Array.from({ length: frames }, (_, i) => ({
    id: `${clipId}-f${i}`, src: '', previewSrc: '', width: 100, height: 100, analysis: {},
    clipId, sourceKind: 'video', sourceName: name,
  }));
};
const buildPool = (P, videoFrameCounts) => {
  const imgs = [];
  for (let i = 0; i < P; i++) imgs.push(photo());
  for (const f of videoFrameCounts) imgs.push(...video(f));
  return imgs;
};

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };
const srcOf = (images, idx) => sourceKeyOf(images[idx], idx);

const photoCounts = [0, 1, 2, 3, 6, 12, 30, 60];
const videoMixes = [[], [12], [8], [12, 12], [12, 8, 5], [1], [2, 3], [12, 12, 12, 12], [30]];
const SEEDS = 40;

for (const P of photoCounts) {
  for (const vids of videoMixes) {
    const images = buildPool(P, vids);
    if (images.length === 0) continue;
    const numSources = distinctSourceCount(images);
    const groups = groupBySource(images);
    const sizeOf = (k) => groups.get(k).length;

    // COUNT INVARIANT — the number a fresh import snaps to == photos + videos,
    // a video counting once however many frames it yielded.
    ok(); if (numSources !== P + vids.length) fail(`distinctSourceCount ${numSources} != ${P + vids.length} (P=${P}, vids=${vids})`);

    const slots = new Set([1, Math.max(1, numSources - 1), numSources, numSources + 1, numSources * 2, numSources * 3 + 1, 200]);
    for (const slotCount of slots) {
      if (slotCount <= 0) continue;
      for (let s = 0; s < SEEDS; s++) {
        const bag = assignSources({ slotCount, images, rng: rngOf(s * 7919 + P * 131 + vids.length * 17 + slotCount) });

        ok(); if (bag.length !== slotCount) fail(`len ${bag.length} != ${slotCount}`);
        ok(); if (!bag.every((i) => Number.isInteger(i) && i >= 0 && i < images.length)) fail(`invalid index (P=${P}, vids=${vids}, slot=${slotCount})`);

        const bySource = new Map();
        for (const idx of bag) { const k = srcOf(images, idx); bySource.set(k, (bySource.get(k) || 0) + 1); }
        const app = [...bySource.values()];
        const maxA = Math.max(...app), minA = Math.min(...app);
        const placed = bySource.size;
        const lo = Math.floor(slotCount / numSources), hi = Math.ceil(slotCount / numSources);

        if (slotCount >= numSources) {
          ok(); if (placed !== numSources) fail(`not all sources placed: ${placed}/${numSources} (slot=${slotCount})`);
          ok(); if (maxA > hi || minA < lo) fail(`imbalance [${minA},${maxA}] exp [${lo},${hi}] (slot=${slotCount}, src=${numSources})`);
        } else {
          ok(); if (maxA !== 1) fail(`dup source when slot<sources: maxA=${maxA} (slot=${slotCount}, src=${numSources})`);
          ok(); if (placed !== slotCount) fail(`placed ${placed} != slot ${slotCount}`);
        }

        // HEADLINE — the operator's rule: no duplicates until the pool is spent.
        if (slotCount <= numSources) {
          ok(); if (maxA !== 1) fail(`DUPLICATE SOURCE at slot<=sources: maxA=${maxA} (slot=${slotCount}, src=${numSources})`);
          ok(); if (new Set(bag).size !== bag.length) fail(`DUPLICATE ASSET at slot<=sources (slot=${slotCount})`);
        }
        if (slotCount === numSources) {
          ok(); if (!(maxA === 1 && minA === 1 && placed === numSources)) fail(`not exactly-once at slot==sources (P=${P}, vids=${vids})`);
        }

        // A repeated source hands back a fresh moment until its frames run out.
        for (const [k, cnt] of bySource) {
          const distinctFrames = new Set(bag.filter((idx) => srcOf(images, idx) === k)).size;
          const exp = Math.min(cnt, sizeOf(k));
          ok(); if (distinctFrames < exp) fail(`source ${k} reused a frame early: ${distinctFrames} < ${exp} (cnt=${cnt}, size=${sizeOf(k)})`);
        }
      }
    }
  }
}

// LOCKED CELLS — a source already on screen must not reappear while any source
// is still unshown (the round-robin seeds "shown" from `used`).
for (const seedBase of [1, 2, 3, 4, 5]) {
  const images = buildPool(5, [12]); // 6 sources: 5 photos + 1 video
  const used = new Set([0, 5]);       // lock photo #0 and the first video frame
  const lockedSources = new Set([srcOf(images, 0), srcOf(images, 5)]);
  const slotCount = 4;                // 4 unshown sources remain
  const bag = assignSources({ slotCount, images, used, rng: rngOf(seedBase) });
  const placedSources = new Set(bag.map((i) => srcOf(images, i)));
  ok(); for (const ls of lockedSources) if (placedSources.has(ls)) fail(`locked source ${ls} reappeared while unshown sources remained`);
  ok(); if (placedSources.size !== slotCount) fail(`locked-case produced a duplicate source (${placedSources.size} != ${slotCount})`);
}

// EMPTY POOL — never throws, never hangs, returns the asked-for length.
{ const bag = assignSources({ slotCount: 5, images: [], rng: rngOf(1) });
  ok(); if (bag.length !== 5) fail(`empty pool len ${bag.length} != 5`); }

console.log(`\nfill.invariants: ${checks} checks, ${fails} failure(s)`);
process.exit(fails ? 1 : 0);
