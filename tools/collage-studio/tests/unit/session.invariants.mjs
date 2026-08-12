/**
 * Invariant sweep for src/lib/session.ts — the crash-safe session gates.
 *
 * Run: node tests/unit/session.invariants.mjs
 *
 * It transpiles the REAL module (esbuild, types stripped) and imports it, so it
 * proves the shipped decision core — not a re-implementation. The whole point of
 * this feature is that a snapshot is written at the right moments and NOT at the
 * dangerous ones (during a capture, into an empty pool, over a pending restore),
 * so the sweep enumerates the full boolean cube and checks each gate against an
 * independently-written spec — plus the one cross-gate property that keeps the
 * writer from ever clobbering a session the user is about to restore.
 */
import esbuild from 'esbuild';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // tools/collage-studio

// BUNDLE, DO NOT TRANSFORM: a single-file transform leaves any
// `import './sibling'` pointing at a path the temp directory does not have,
// so the sweep dies the first time this module grows a dependency (C150).
const tmp = join(mkdtempSync(join(tmpdir(), 'session-')), 'session.mjs');
await esbuild.build({
  entryPoints: [join(root, 'src/lib/session.ts')],
  outfile: tmp,
  bundle: true,
  format: 'esm',
  platform: 'neutral',
  logLevel: 'silent',
});
const {
  canAutosave, hasUnsavedWork, shouldPromptRestore, formatAgo,
  planAssetWrites, sessionEntries, hydrateSessionAssets,
  AUTOSAVE_DEBOUNCE_MS, SESSION_DB, SESSION_STORE, SESSION_KEY,
  SESSION_ASSETS, SESSION_DB_VERSION,
} = await import(pathToFileURL(tmp).href);

let checks = 0, fails = 0;
const ok = () => { checks++; };
const fail = (m) => { fails++; if (fails <= 40) console.error('  ✗', m); };
const eq = (got, want, m) => { checks++; if (got !== want) { fails++; if (fails <= 40) console.error('  ✗', `${m}: got ${JSON.stringify(got)} want ${JSON.stringify(want)}`); } };

const bools = [false, true];
const counts = [0, 1, 2, 7, 40];

// --- canAutosave: all three guards must be clear ----------------------------
// SPEC (independent): imageCount>0 AND not exporting AND not restoring.
for (const imageCount of counts) {
  for (const isExporting of bools) {
    for (const isRestoring of bools) {
      const got = canAutosave({ imageCount, isExporting, isRestoring });
      const want = imageCount > 0 && !isExporting && !isRestoring;
      eq(got, want, `canAutosave(${imageCount},exp=${isExporting},res=${isRestoring})`);
    }
  }
}
// Named danger cases spelled out, so a regression names itself.
eq(canAutosave({ imageCount: 0, isExporting: false, isRestoring: false }), false, 'empty pool never autosaves');
eq(canAutosave({ imageCount: 12, isExporting: true, isRestoring: false }), false, 'never autosave mid-export (the crash moment)');
eq(canAutosave({ imageCount: 12, isExporting: false, isRestoring: true }), false, 'never autosave while a restore is offered');
eq(canAutosave({ imageCount: 12, isExporting: false, isRestoring: false }), true, 'a normal edit does autosave');

// --- hasUnsavedWork: pool present AND changed since last download -----------
for (const imageCount of counts) {
  for (const dirty of bools) {
    eq(hasUnsavedWork(imageCount, dirty), imageCount > 0 && dirty, `hasUnsavedWork(${imageCount},${dirty})`);
  }
}

// --- shouldPromptRestore: stored session AND empty pool ---------------------
for (const hasStored of bools) {
  for (const imageCount of counts) {
    eq(shouldPromptRestore(hasStored, imageCount), hasStored && imageCount === 0, `shouldPromptRestore(${hasStored},${imageCount})`);
  }
}

// --- THE CROSS-GATE SAFETY PROPERTY -----------------------------------------
// A restore that is being OFFERED must freeze the writer, or the next autosave
// overwrites the very session the banner is about to restore. Because the offer
// requires an empty pool and the writer requires a non-empty one, the two can
// never both fire for the same pool — assert that over the whole cube.
for (const imageCount of counts) {
  for (const isExporting of bools) {
    // hasStored=true so the restore side is "armed"; the pool count decides.
    const writerLive = canAutosave({ imageCount, isExporting, isRestoring: false });
    const restoreOffered = shouldPromptRestore(true, imageCount);
    if (writerLive && restoreOffered) fail(`writer and restore-offer both live at imageCount=${imageCount}`); else ok();
  }
}

// --- formatAgo: coarse buckets, monotonic, never throws ---------------------
eq(formatAgo(0), 'moments ago', 'formatAgo(0)');
eq(formatAgo(10_000), 'moments ago', 'formatAgo(10s)');
eq(formatAgo(44_000), 'moments ago', 'formatAgo(44s)');
eq(formatAgo(90_000), '1m ago', 'formatAgo(90s)');
eq(formatAgo(59 * 60_000), '59m ago', 'formatAgo(59m)');
eq(formatAgo(60 * 60_000), '1h ago', 'formatAgo(1h)');
eq(formatAgo(23 * 3600_000), '23h ago', 'formatAgo(23h)');
eq(formatAgo(24 * 3600_000), '1d ago', 'formatAgo(24h)');
eq(formatAgo(3 * 86_400_000), '3d ago', 'formatAgo(3d)');
eq(formatAgo(-5000), 'moments ago', 'formatAgo negative clamps');
// Never throws across a wide range, and never returns empty.
for (let ms = 0; ms <= 10 * 86_400_000; ms += 137_000) {
  const s = formatAgo(ms);
  if (typeof s !== 'string' || s.length === 0) fail(`formatAgo(${ms}) empty`); else ok();
}

// --- planAssetWrites: THE CLAIM THAT MAKES AUTOSAVE CHEAP -------------------
// The bug this fixes ("restoring is slow and glitching") was the autosave
// re-zipping the entire image pool on every debounce. The cure is a diff, and
// the load-bearing property is the steady state: a pool that did not change
// writes NOTHING. Assert it directly, then the rest of the algebra.
const ids = (n, p = 'a') => Array.from({ length: n }, (_, i) => `${p}${i}`);

for (const n of [1, 2, 5, 40]) {
  const pool = ids(n);
  const p = planAssetWrites(pool, pool);
  eq(p.write.length, 0, `unchanged pool of ${n} writes no bytes`);
  eq(p.drop.length, 0, `unchanged pool of ${n} drops nothing`);
}
// A cold store writes everything, exactly once, in pool order.
{
  const pool = ids(6);
  const p = planAssetWrites(pool, []);
  eq(p.write.join(','), pool.join(','), 'cold store writes the whole pool in order');
  eq(p.drop.length, 0, 'cold store drops nothing');
}
// One photo added -> exactly one write.
{
  const before = ids(5);
  const p = planAssetWrites([...before, 'new'], before);
  eq(p.write.join(','), 'new', 'adding one image writes exactly one row');
  eq(p.drop.length, 0, 'adding one image drops nothing');
}
// One photo removed -> exactly one delete, no writes.
{
  const before = ids(5);
  const p = planAssetWrites(before.slice(1), before);
  eq(p.write.length, 0, 'removing an image writes nothing');
  eq(p.drop.join(','), 'a0', 'removing an image drops exactly that id');
}
// Reordering is not a change: the same set in a different order is free.
{
  const pool = ids(8);
  const p = planAssetWrites([...pool].reverse(), pool);
  eq(p.write.length, 0, 'reordering writes nothing');
  eq(p.drop.length, 0, 'reordering drops nothing');
}
// Duplicates collapse — the same bytes must never be written twice.
{
  const p = planAssetWrites(['x', 'x', 'y', 'x'], []);
  eq(p.write.join(','), 'x,y', 'duplicate ids collapse to one write each');
}
// Empties are legal at both ends.
eq(planAssetWrites([], []).write.length, 0, 'empty/empty writes nothing');
eq(planAssetWrites([], ['g1', 'g2']).drop.join(','), 'g1,g2', 'emptied pool drops every stored id');
eq(planAssetWrites(['n'], []).write.join(','), 'n', 'empty store writes the one id');
// GENERAL PROPERTY over random pools: write = pool \ stored (deduped, pool
// order), drop = stored \ pool, and the two are always disjoint.
let seed = 12345;
const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
for (let trial = 0; trial < 400; trial++) {
  const universe = ids(12, 'u');
  const pool = universe.filter(() => rnd() < 0.5);
  const stored = universe.filter(() => rnd() < 0.5);
  const p = planAssetWrites(pool, stored);
  const wantWrite = [...new Set(pool)].filter((i) => !stored.includes(i));
  const wantDrop = stored.filter((i) => !pool.includes(i));
  eq(p.write.join(','), wantWrite.join(','), `trial ${trial} write set`);
  eq(p.drop.join(','), wantDrop.join(','), `trial ${trial} drop set`);
  if (p.write.some((i) => p.drop.includes(i))) fail(`trial ${trial}: an id was both written and dropped`); else ok();
  // Nothing already stored is ever re-written — the whole point.
  if (p.write.some((i) => stored.includes(i))) fail(`trial ${trial}: re-wrote a stored asset`); else ok();
}

// --- sessionEntries + hydrateSessionAssets: a lossless round trip -----------
// Restore reads these two numbers instead of decoding the picture to relearn
// them, so if the mapping loses them the fix silently reverts to the slow path.
{
  const pool = [
    { id: 'i1', originalName: 'a.jpg', width: 4032, height: 3024, analysis: { k: 1 } },
    { id: 'i2', originalName: 'b.png', width: 800, height: 1200, analysis: { k: 2 } },
    { id: 'i3', width: 1, height: 1, analysis: null },
  ];
  const entries = sessionEntries(pool);
  eq(entries.length, 3, 'one entry per image');
  eq(entries.map((e) => e.id).join(','), 'i1,i2,i3', 'entry order follows the pool');
  eq(entries[0].width, 4032, 'width survives the mapping');
  eq(entries[0].height, 3024, 'height survives the mapping');
  eq(entries[2].originalName, 'image.png', 'a nameless asset gets the documented default');

  // Two of the three have a real thumbnail; the third aliases, exactly as
  // `createThumbnail` leaves an image that was already under 1024px.
  const urls = {
    i1: { src: 'blob:full-1', previewSrc: 'blob:thumb-1' },
    i2: { src: 'blob:full-2', previewSrc: 'blob:thumb-2' },
    i3: { src: 'blob:full-3', previewSrc: 'blob:full-3' },
  };
  const back = hydrateSessionAssets(entries, urls);
  eq(back.length, 3, 'hydrate returns the whole pool');
  eq(back.map((a) => a.id).join(','), 'i1,i2,i3', 'hydrate preserves order (arrangeBag deals from it)');
  for (let i = 0; i < 3; i++) {
    eq(back[i].width, pool[i].width, `width round-trips for ${pool[i].id}`);
    eq(back[i].height, pool[i].height, `height round-trips for ${pool[i].id}`);
    eq(back[i].src, urls[pool[i].id].src, `src is the minted url for ${pool[i].id}`);
    eq(JSON.stringify(back[i].analysis), JSON.stringify(pool[i].analysis), `analysis round-trips for ${pool[i].id}`);
  }

  // THE THUMBNAIL TIER MUST SURVIVE THE RESTORE. This is the regression that
  // made the editor SLOWER after recovering than before the crash: previewSrc
  // was set to the full-resolution original, and the app draws previewSrc
  // everywhere. If these two ever collapse to src again, restore is quietly
  // handing a 4032px photograph to a code path built for a 1024px one.
  eq(back[0].previewSrc, 'blob:thumb-1', 'the stored thumbnail comes back as previewSrc');
  eq(back[1].previewSrc, 'blob:thumb-2', 'the stored thumbnail comes back as previewSrc');
  if (back[0].previewSrc === back[0].src) fail('previewSrc collapsed onto the full-res src'); else ok();
  // ...and it still ALIASES when there genuinely is no separate thumbnail.
  eq(back[2].previewSrc, back[2].src, 'no thumbnail means previewSrc aliases src');
  // A blank/absent previewSrc falls back to src rather than to "undefined",
  // which is the stencil.ts 404 this field's comment has always warned about.
  eq(hydrateSessionAssets([entries[0]], { i1: { src: 'blob:full-1', previewSrc: '' } })[0].previewSrc, 'blob:full-1', 'an empty preview url falls back to src');

  // FAILS CLOSED. One missing source must refuse the whole restore — a short
  // pool re-deals every fragment after the gap, so it is somebody else's collage.
  eq(hydrateSessionAssets(entries, { i1: urls.i1, i3: urls.i3 }), null, 'a missing source refuses the restore');
  eq(hydrateSessionAssets(entries, { i1: urls.i1, i2: { src: '', previewSrc: 'x' }, i3: urls.i3 }), null, 'an empty source url refuses the restore');
  eq(hydrateSessionAssets(entries, {}), null, 'no sources at all refuses the restore');
  eq(hydrateSessionAssets([], { i1: 'blob:1' }), null, 'an empty manifest is not a session');
  eq(hydrateSessionAssets(null, {}), null, 'a missing manifest is not a session');
  eq(hydrateSessionAssets(undefined, {}), null, 'an undefined manifest is not a session');
}

// --- constants are the shape the store depends on ---------------------------
eq(typeof AUTOSAVE_DEBOUNCE_MS, 'number', 'debounce is a number');
ok(AUTOSAVE_DEBOUNCE_MS > 0 || fail('debounce must be positive'));
eq(SESSION_DB, 'collage-session', 'db name stable (renaming orphans stored sessions)');
eq(SESSION_STORE, 'project', 'store name stable');
eq(SESSION_KEY, 'current', 'key stable');
eq(SESSION_ASSETS, 'assets', 'assets store name stable');
// v1 rows live in `project`; the upgrade must be a bump, never a rename, or
// every session written by the previous build is orphaned on deploy.
eq(SESSION_DB_VERSION, 2, 'db version is 2 (v1 rows still readable)');

console.log(`session invariants: ${checks} checks, ${fails} failures`);
process.exit(fails === 0 ? 0 : 1);
