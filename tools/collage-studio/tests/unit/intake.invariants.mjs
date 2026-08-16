/**
 * Invariant sweep for INTAKE — which bucket a picked file lands in.
 *
 * Run: node tests/unit/intake.invariants.mjs
 *
 * It transpiles the REAL `src/lib/intake.ts` (esbuild, types stripped), which
 * pulls in the REAL `soundtrack.isAudioFile` and `video.isVideoFile` behind it,
 * so what is swept here is the shipped ladder rather than a paraphrase of it.
 *
 * THE WISH THIS EXISTS FOR (collage well, improve, about_tool=upload):
 *   *"Be able to add music or sound without the video. Right now if you use a
 *   video for the sound or import audio from video it just imports video… if
 *   you're importing audio it should not display the video."*
 *
 *   All three file buttons fired one handler, so routing was a function of the
 *   FILE ALONE and the app forgot WHICH BUTTON was pressed. `isVideoFile`
 *   answered "video" for a `.mov` picked with the MUSIC button — correctly, for
 *   a question nobody asked. The clip landed in the collage as a picture.
 *
 * I1  EXACTLY ONE BUCKET, UNDER EVERY INTENT. The original invariant, restated
 *     over the new axis: extension x MIME x intent, and a file is never two
 *     things and never none.
 *
 * I2  `'any'` IS BYTE-IDENTICAL TO WHAT SHIPPED. The three inline predicates
 *     `ingestFiles` used to hold, in its order, evaluated against the module for
 *     the whole cross product. This is the assertion that says "the fix changed
 *     nothing for anyone who did not ask for it" as a MEASUREMENT — it is the
 *     drop zone, the "add images or video" button and every legacy path.
 *
 * I3  UNDER `'music'`, A VIDEO CONTAINER IS SOUND. The one line the wish is
 *     about. Same file, same predicates, different answer, because the question
 *     changed.
 *
 * I4  UNDER `'music'`, A PICTURE IS REFUSED — never quietly added. "I asked for
 *     sound and got a picture" is the bug being reported; routing a `.jpg` from
 *     the music button into the collage would be that same bug in a different
 *     extension.
 *
 * I5  AUDIO IS MUSIC UNDER EVERY INTENT. Nothing about "add images or video"
 *     makes an `.mp3` into a picture, so intent moves files BETWEEN buckets and
 *     never out of the one they were already right about.
 *
 * I6  `splitIntake` PARTITIONS: every file lands in exactly one list, none is
 *     lost, none is duplicated, and the order inside a bucket is the order the
 *     files arrived in — which is what makes "the last music file picked wins"
 *     mean what it says at the call site.
 *
 * I7  IT IS TOTAL. Empty names, missing fields, absurd MIME types, a file called
 *     `.mov` and nothing else: a picker handler is the last place allowed to
 *     throw.
 *
 * I8  INTENT IS MONOTONIC TOWARD SOUND. `'music'` never turns a music file into
 *     a picture or a video — the only transitions it may cause are
 *     video->music and picture->rejected.
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

const I = await load('src/lib/intake.ts', 'intake');
const S = await load('src/lib/soundtrack.ts', 'soundtrack');
const V = await load('src/lib/video.ts', 'video');

let checks = 0;
const ok = (cond, msg) => { checks++; assert.ok(cond, msg); };

const EXTS = [
  // audio-only spellings
  'mp3', 'm4a', 'm4b', 'aac', 'wav', 'wave', 'flac', 'opus', 'oga', 'weba', 'aif', 'aiff', 'caf', 'amr', 'wma',
  // video / ambiguous containers — the .mov the wish is about lives here
  'mp4', 'm4v', 'mov', 'qt', 'webm', 'mkv', 'avi', 'ogv', 'ogg', '3gp', '3g2', 'mpg', 'mpeg', 'ts', 'm2ts',
  // pictures and junk
  'jpg', 'jpeg', 'png', 'gif', 'webp', 'heic', 'pdf', 'txt', 'zip', '',
];
const MIMES = [
  '',                                   // iOS share sheet / Android SAF hand over nothing
  'audio/mpeg', 'audio/mp4', 'audio/x-m4a', 'audio/aac', 'audio/wav', 'audio/x-wav',
  'audio/flac', 'audio/ogg', 'audio/opus', 'audio/webm', 'audio/aiff', 'audio/amr',
  'video/mp4', 'video/quicktime', 'video/webm', 'video/x-matroska', 'video/ogg', 'video/mpeg',
  'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic',
  'application/pdf', 'application/octet-stream', 'text/plain',
];
const INTENTS = ['any', 'music'];
const BUCKETS = ['music', 'video', 'picture', 'rejected'];

/** EXACTLY the three predicates `ingestFiles` used to hold inline, in its order.
 *  This is the OLD behaviour, kept here only so I2 can measure against it. */
const legacyBucket = (f) => {
  if (S.isAudioFile(f)) return 'music';
  if (V.isVideoFile(f)) return 'video';
  if ((f.type || '').startsWith('image/')) return 'picture';
  return 'rejected';
};

// ---------------------------------------------------------------------------
// I1–I5, I8 — the cross product.
// ---------------------------------------------------------------------------
let rows = 0;
let movedToMusic = 0;
let refusedPictures = 0;
for (const ext of EXTS) {
  for (const type of MIMES) {
    const name = ext ? `take_01.${ext}` : 'take_01';
    const f = { name, type };
    const legacy = legacyBucket(f);

    for (const intent of INTENTS) {
      rows++;
      const b = I.routeIntake(f, intent);

      // I1 — one of exactly four, always.
      ok(BUCKETS.includes(b), `bucket is one of four ("${name}", ${type || 'no type'}, ${intent})`);

      if (intent === 'any') {
        // I2 — byte-identical to what shipped.
        ok(b === legacy,
          `'any' changed a routing: "${name}" (${type || 'no type'}) was ${legacy}, now ${b}`);
      } else {
        // I3 — a video container asked for as sound IS sound.
        if (legacy === 'video') { ok(b === 'music', `"${name}" under 'music' must be sound, got ${b}`); movedToMusic++; }
        // I4 — a picture asked for as sound is refused, never added.
        if (legacy === 'picture') { ok(b === 'rejected', `"${name}" under 'music' must be refused, got ${b}`); refusedPictures++; }
        // I5 — audio is music whatever was pressed.
        if (legacy === 'music') ok(b === 'music', `"${name}" is audio; 'music' must not move it (${b})`);
        // I8 — monotonic toward sound: the only moves are video->music and
        // picture->rejected. Nothing may become a PICTURE or a VIDEO that was
        // not one already.
        ok(b === legacy || (legacy === 'video' && b === 'music') || (legacy === 'picture' && b === 'rejected'),
          `'music' made an illegal move for "${name}": ${legacy} -> ${b}`);
        ok(b !== 'video' && b !== 'picture',
          `'music' must never produce a ${b} ("${name}")`);
      }
    }
  }
}
ok(rows === EXTS.length * MIMES.length * INTENTS.length, 'swept the full cross product');
ok(movedToMusic > 0, 'the wish is reachable at all — some file DID move video->music');
ok(refusedPictures > 0, 'the refusal is reachable at all');

// The default argument is the shipped default, and it is `'any'`. A call site
// that forgets to pass an intent must behave exactly as it did before.
for (const ext of ['mov', 'mp4', 'jpg', 'mp3']) {
  const f = { name: `x.${ext}`, type: '' };
  ok(I.routeIntake(f) === I.routeIntake(f, 'any'), `the default intent is 'any' (.${ext})`);
}

// The concrete cases the wish names, spelled out so a future refactor reads them
// as sentences rather than as coordinates in a cross product.
ok(I.routeIntake({ name: 'clip.mov', type: 'video/quicktime' }, 'music') === 'music',
  'THE WISH: a .mov picked with the music button is SOUND');
ok(I.routeIntake({ name: 'clip.mov', type: '' }, 'music') === 'music',
  'THE WISH, from an iPhone share sheet (no MIME type at all)');
ok(I.routeIntake({ name: 'clip.mov', type: 'video/quicktime' }, 'any') === 'video',
  'the same file dropped on the canvas is still a CLIP');
ok(I.routeIntake({ name: 'song.mp3', type: 'audio/mpeg' }, 'any') === 'music',
  'an mp3 is music however it arrived');

// ---------------------------------------------------------------------------
// I6 — splitIntake partitions, in arrival order.
// ---------------------------------------------------------------------------
const mulberry = (seed) => () => {
  seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
let splits = 0;
for (let seed = 1; seed <= 200; seed++) {
  const rnd = mulberry(seed * 7919);
  const n = Math.floor(rnd() * 12);
  const list = [];
  for (let i = 0; i < n; i++) {
    const ext = EXTS[Math.floor(rnd() * EXTS.length)];
    const type = MIMES[Math.floor(rnd() * MIMES.length)];
    list.push({ name: `${i}_file${ext ? '.' + ext : ''}`, type });
  }
  for (const intent of INTENTS) {
    splits++;
    const s = I.splitIntake(list, intent);
    const total = s.music.length + s.video.length + s.picture.length + s.rejected.length;
    ok(total === list.length, `partition loses or duplicates nothing (seed ${seed}, ${intent})`);
    // Every file is in the bucket its own routing names, and in no other.
    for (const f of list) {
      const b = I.routeIntake(f, intent);
      ok(s[b].includes(f), `"${f.name}" is in its own bucket (${b})`);
      for (const other of BUCKETS) if (other !== b) ok(!s[other].includes(f), `"${f.name}" is in NO other bucket`);
    }
    // Order inside a bucket is arrival order — "the last music file wins"
    // is a claim about this.
    for (const b of BUCKETS) {
      const idx = s[b].map((f) => list.indexOf(f));
      ok(idx.every((v, i) => i === 0 || v > idx[i - 1]), `${b} keeps arrival order (seed ${seed})`);
    }
  }
}
ok(I.splitIntake([], 'music').music.length === 0, 'an empty pick is an empty split');

// ---------------------------------------------------------------------------
// I7 — total.
// ---------------------------------------------------------------------------
const NASTY = [
  { name: '', type: '' },
  { name: '.mov', type: '' },
  { name: 'no-extension', type: 'application/x-thing' },
  { name: 'UPPER.MOV', type: '' },
  { name: 'two.dots.mp4', type: '' },
  { name: 'trailing.', type: '' },
  { name: 'x'.repeat(600) + '.mov', type: '' },
  { name: 'emoji 🎬.mov', type: 'video/quicktime' },
  { name: 'song.mp3', type: 'AUDIO/MPEG' },
];
for (const f of NASTY) {
  for (const intent of [...INTENTS, undefined, 'nonsense']) {
    const b = I.routeIntake(f, intent);
    ok(BUCKETS.includes(b), `total for "${f.name}" (${intent}) -> ${b}`);
  }
}
// An UPPERCASE extension is still that container — the picker on a camera roll
// hands `IMG_0042.MOV` and the wish is about exactly that file.
ok(I.routeIntake({ name: 'IMG_0042.MOV', type: '' }, 'music') === 'music',
  'an uppercase .MOV from a camera roll is sound under the music button');

console.log(`intake invariants: ${checks} assertions over ${rows} file x intent rows, ${splits} splits — all green`);
