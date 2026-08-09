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

const src = readFileSync(join(root, 'src/lib/session.ts'), 'utf8');
const { code } = await esbuild.transform(src, { loader: 'ts', format: 'esm' });
const tmp = join(mkdtempSync(join(tmpdir(), 'session-')), 'session.mjs');
writeFileSync(tmp, code);
const {
  canAutosave, hasUnsavedWork, shouldPromptRestore, formatAgo,
  AUTOSAVE_DEBOUNCE_MS, SESSION_DB, SESSION_STORE, SESSION_KEY,
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

// --- constants are the shape the store depends on ---------------------------
eq(typeof AUTOSAVE_DEBOUNCE_MS, 'number', 'debounce is a number');
ok(AUTOSAVE_DEBOUNCE_MS > 0 || fail('debounce must be positive'));
eq(SESSION_DB, 'collage-session', 'db name stable (renaming orphans stored sessions)');
eq(SESSION_STORE, 'project', 'store name stable');
eq(SESSION_KEY, 'current', 'key stable');

console.log(`session invariants: ${checks} checks, ${fails} failures`);
process.exit(fails === 0 ? 0 : 1);
