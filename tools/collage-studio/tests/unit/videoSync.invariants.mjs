/**
 * Invariant sweep for src/lib/videoSync.ts — per-clip playbackRate/loop.
 * Run: node tests/unit/videoSync.invariants.mjs
 * Transpiles and imports the REAL module (no re-implementation).
 */
import esbuild from 'esbuild';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');
// BUNDLE, DO NOT TRANSFORM — `videoSync.ts` imports `speed.ts` (the per-clip
// SPEED enters through `computeClipPlayback`), and a single-file transform
// leaves that import pointing at a path the temp directory does not have.
const tmp = join(mkdtempSync(join(tmpdir(), 'vsync-')), 'videoSync.mjs');
await esbuild.build({
  entryPoints: [join(root, 'src/lib/videoSync.ts')],
  outfile: tmp,
  bundle: true,
  format: 'esm',
  platform: 'neutral',
  logLevel: 'silent',
});
const { computeClipPlayback, referenceLength, RATE_MIN, RATE_MAX, CLIP_LENGTH_MODES } =
  await import(pathToFileURL(tmp).href);

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };
const approx = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps * Math.max(1, Math.abs(a), Math.abs(b));

const durationSets = [
  [], [5], [3, 3, 3], [2, 8], [1, 4, 9, 16], [0.5, 30], [10, 20, 40],
  [0, 5, 10], [NaN, 4, 8], [-1, 6], [1000, 0.1], [7.3, 2.1, 19.8, 0.9, 12.4],
];

for (const durs of durationSets) {
  const clips = durs.map((d, i) => ({ id: `c${i}`, durationSec: d }));
  const known = durs.filter((d) => Number.isFinite(d) && d > 0);
  const Lmax = known.length ? Math.max(...known) : 0;
  const Lmin = known.length ? Math.min(...known) : 0;

  for (const mode of CLIP_LENGTH_MODES) {
    const out = computeClipPlayback(clips, mode);

    // Totality: one output per input, ids aligned & preserved, loop always true.
    ok(); if (out.length !== clips.length) fail(`len ${out.length} != ${clips.length} (${mode})`);
    ok(); if (!out.every((o, i) => o.id === clips[i].id)) fail(`id misaligned (${mode})`);
    ok(); if (!out.every((o) => o.loop === true)) fail(`loop not true (${mode})`);
    // Rates always within the media-element bounds.
    ok(); if (!out.every((o) => o.playbackRate >= RATE_MIN && o.playbackRate <= RATE_MAX)) fail(`rate out of [${RATE_MIN},${RATE_MAX}] (${mode})`);
    // Unknown/zero/negative durations never get rescaled.
    out.forEach((o, i) => { if (!(Number.isFinite(durs[i]) && durs[i] > 0)) { ok(); if (o.playbackRate !== 1) fail(`bad-duration clip rescaled to ${o.playbackRate} (${mode})`); } });

    if (mode === 'loop') {
      ok(); if (!out.every((o) => o.playbackRate === 1)) fail(`loop mode changed a rate`);
    }

    if (mode === 'stretch-longest' && known.length) {
      const ref = Lmax;
      out.forEach((o, i) => {
        const d = durs[i];
        if (!(Number.isFinite(d) && d > 0)) return;
        const ideal = d / ref; // <= 1
        // Effective length == ref, unless the ideal rate was clamped.
        if (ideal >= RATE_MIN && ideal <= RATE_MAX) {
          ok(); if (!approx(d / o.playbackRate, ref)) fail(`stretch-longest effective ${d / o.playbackRate} != ${ref} (d=${d})`);
          ok(); if (o.playbackRate > 1 + 1e-9) fail(`stretch-longest sped a clip up: rate ${o.playbackRate} (d=${d})`);
        } else {
          ok(); if (o.playbackRate !== Math.min(RATE_MAX, Math.max(RATE_MIN, ideal))) fail(`stretch clamp wrong`);
        }
      });
      // The longest clip is the reference → rate exactly 1.
      const li = durs.findIndex((d) => d === Lmax);
      ok(); if (Math.abs(out[li].playbackRate - 1) > 1e-9) fail(`longest clip not rate 1 (got ${out[li].playbackRate})`);
    }

    if (mode === 'speed-shortest' && known.length) {
      const ref = Lmin;
      out.forEach((o, i) => {
        const d = durs[i];
        if (!(Number.isFinite(d) && d > 0)) return;
        const ideal = d / ref; // >= 1
        if (ideal >= RATE_MIN && ideal <= RATE_MAX) {
          ok(); if (!approx(d / o.playbackRate, ref)) fail(`speed-shortest effective ${d / o.playbackRate} != ${ref} (d=${d})`);
          ok(); if (o.playbackRate < 1 - 1e-9) fail(`speed-shortest slowed a clip down: rate ${o.playbackRate} (d=${d})`);
        }
      });
      const si = durs.findIndex((d) => d === Lmin);
      ok(); if (Math.abs(out[si].playbackRate - 1) > 1e-9) fail(`shortest clip not rate 1 (got ${out[si].playbackRate})`);
    }
  }

  // referenceLength contract
  ok(); if (referenceLength(clips, 'loop') !== null) fail(`loop referenceLength not null`);
  if (known.length) {
    ok(); if (referenceLength(clips, 'stretch-longest') !== Lmax) fail(`ref stretch != Lmax`);
    ok(); if (referenceLength(clips, 'speed-shortest') !== Lmin) fail(`ref speed != Lmin`);
  } else {
    ok(); if (referenceLength(clips, 'stretch-longest') !== null) fail(`ref should be null (no durations)`);
  }
}

// Single clip is never rescaled in any mode.
for (const mode of CLIP_LENGTH_MODES) {
  const out = computeClipPlayback([{ id: 'solo', durationSec: 12.5 }], mode);
  ok(); if (out[0].playbackRate !== 1) fail(`single clip rescaled in ${mode} (got ${out[0].playbackRate})`);
}

console.log(`\nvideoSync.invariants: ${checks} checks, ${fails} failure(s)`);
process.exit(fails ? 1 : 0);
