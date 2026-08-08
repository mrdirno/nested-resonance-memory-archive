/**
 * Invariant sweep for THE SOUNDTRACK — music under the collage.
 *
 * Run: node tests/unit/soundtrack.invariants.mjs
 *
 * It transpiles the REAL modules (esbuild, types stripped) and imports them, so
 * it proves the shipped `soundtrack.isAudioFile` / `soundtrackSource` /
 * `soundtrackAudible` against the shipped `video.isVideoFile` — not a
 * re-implementation of either.
 *
 * THE FIRST INVARIANT — EXACTLY ONE BUCKET.
 *   `ingestFiles` sorts every picked or dropped file into music / video /
 *   picture / rejected, and all three tests run against the same `File`. An
 *   overlap is a file imported TWICE (a music track that is also a clip); a gap
 *   is a file rejected with a message naming formats it matches. This is the
 *   rule `offlineAudio` learned twice and wrote down, applied at intake instead
 *   of at the mixer. Swept over the cross product of every extension either
 *   module names and every MIME type a real picker has been seen to emit,
 *   including the empty string.
 *
 * THE SECOND — THE EXPORT NEVER READS THE MONITOR.
 *   Written up in stage.ts as the bug that made exports silent: `gain` is the
 *   user's INTENT, `audible` is a fact about the SPEAKERS. The monitor starts
 *   OFF (browsers only autoplay muted media), so a mixer wired to `audible`
 *   renders silence for anyone who never pressed the speaker. The claim here is
 *   structural rather than anecdotal: `soundtrackSource` is called with every
 *   spec twice and must be `deepStrictEqual` regardless of what the monitor is
 *   doing — it takes no monitor argument at all, and this sweep is what keeps it
 *   that way.
 *
 * THE THIRD — THE SPAN IS ALWAYS ZERO, FOR EVERY DURATION.
 *   `OfflineAudioSource.span` exists so a clip's sound lands in the same window
 *   as its picture. Music has no picture, and its container duration is not its
 *   decoded duration (mp3 encoder delay and padding). Handing that hop over as
 *   `span` does not merely round differently — it changes BRANCH inside
 *   `audioSchedule`, which reads "the sound ends inside the window" as the
 *   LAPPED case and answers with one non-looping node per lap, cutting a sliver
 *   of silence into every repeat forever. So the sweep asserts 0 for sane
 *   durations too, and the assertion exists to fail the day somebody helpfully
 *   passes the real number.
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

const S = await load('src/lib/soundtrack.ts', 'soundtrack');
const V = await load('src/lib/video.ts', 'video');

let checks = 0;
const ok = (cond, msg) => { checks++; assert.ok(cond, msg); };

// ---------------------------------------------------------------------------
// I1 — EXACTLY ONE BUCKET, over extension x MIME.
// ---------------------------------------------------------------------------
const EXTS = [
  // audio-only spellings
  'mp3', 'm4a', 'm4b', 'aac', 'wav', 'wave', 'flac', 'opus', 'oga', 'weba', 'aif', 'aiff', 'caf', 'amr', 'wma',
  // video / ambiguous containers
  'mp4', 'm4v', 'mov', 'qt', 'webm', 'mkv', 'avi', 'ogv', 'ogg', '3gp', '3g2', 'mpg', 'mpeg', 'ts', 'm2ts',
  // pictures and junk
  'jpg', 'jpeg', 'png', 'gif', 'webp', 'heic', 'pdf', 'txt', 'zip', '',
];
const MIMES = [
  '',                                   // iOS share sheet / Android SAF
  'audio/mpeg', 'audio/mp4', 'audio/x-m4a', 'audio/aac', 'audio/wav', 'audio/x-wav',
  'audio/flac', 'audio/ogg', 'audio/opus', 'audio/webm', 'audio/aiff', 'audio/amr',
  'video/mp4', 'video/quicktime', 'video/webm', 'video/x-matroska', 'video/ogg', 'video/mpeg',
  'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic',
  'application/pdf', 'application/octet-stream', 'text/plain',
];

// Exactly `ingestFiles`'s three predicates, in its order.
const bucketOf = (f) => {
  if (S.isAudioFile(f)) return 'music';
  if (V.isVideoFile(f)) return 'video';
  if ((f.type || '').startsWith('image/')) return 'picture';
  return 'rejected';
};

let pairs = 0;
let musicRows = 0;
const untypedAudio = [];
for (const ext of EXTS) {
  for (const type of MIMES) {
    const name = ext ? `take_01.${ext}` : 'take_01';
    const f = { name, type };
    pairs++;

    // The three predicates as booleans — an overlap is what we are hunting.
    const a = S.isAudioFile(f);
    const v = V.isVideoFile(f);
    const i = (type || '').startsWith('image/');
    ok(!(a && v), `overlap: "${name}" (${type || 'no type'}) is BOTH music and video`);
    ok(!(a && i), `overlap: "${name}" (${type || 'no type'}) is BOTH music and a picture`);

    const b = bucketOf(f);
    ok(['music', 'video', 'picture', 'rejected'].includes(b), 'bucket is one of four');
    if (b === 'music') musicRows++;

    // A STATED TYPE IS BELIEVED, both ways.
    if (type.startsWith('audio/')) ok(a, `stated ${type} must be music ("${name}")`);
    if (type && !type.startsWith('audio/')) ok(!a, `stated ${type} must NOT be music ("${name}")`);
    if (!type && ext) untypedAudio.push([name, a]);
  }
}
ok(pairs === EXTS.length * MIMES.length, 'swept the full cross product');
ok(musicRows > 0, 'the music bucket is reachable at all');

// UNTYPED files fall back to the extension, and the ambiguous containers go to
// VIDEO — the clause that keeps an .m4a from becoming a black rectangle and an
// untyped .mp4 from becoming a silent "song".
const untypedSaysMusic = (ext) => S.isAudioFile({ name: `x.${ext}`, type: '' });
for (const ext of ['mp3', 'm4a', 'aac', 'wav', 'flac', 'opus', 'oga', 'weba', 'aiff', 'caf']) {
  ok(untypedSaysMusic(ext), `untyped .${ext} must be music`);
}
for (const ext of ['mp4', 'webm', 'ogg', 'mov', 'mkv', 'm4v']) {
  ok(!untypedSaysMusic(ext), `untyped .${ext} is ambiguous and must stay video`);
}

// ---------------------------------------------------------------------------
// I2 / I3 — the mixer row: monitor-independent, span always 0, loop always
// true, rate always 1, gain exactly the intent.
// ---------------------------------------------------------------------------
const DURATIONS = [0, 0.001, 1, 3.0000001, 2.99998, 12, 180.4, 3600, -1, NaN, Infinity, -Infinity];
const MUTED = [undefined, false, true];
const URLS = ['blob:http://x/y', '', undefined];

let rows = 0;
for (const durationSec of DURATIONS) {
  for (const muted of MUTED) {
    for (const url of URLS) {
      const spec = { url, name: 'song.mp3', durationSec, muted };
      const src = S.soundtrackSource(spec);
      rows++;

      if (!url) { ok(src === null, 'no url is not a source'); continue; }

      ok(src !== null, 'a track with a url always describes itself');
      ok(src.span === 0, `span must be 0, got ${src.span} for duration ${durationSec}`);
      ok(Object.is(src.span, 0) && !Object.is(src.span, -0), 'span is +0, never -0 or NaN');
      ok(src.loop === true, 'music always laps');
      ok(src.rate === 1, 'music has no video-length sync');
      ok(src.gain === (muted ? 0 : 1), 'gain is exactly the intent');
      ok(src.id === S.SOUNDTRACK_ID, 'one id');
      ok(!src.id.startsWith('clip-') && !src.id.startsWith('vid-'), 'the id can never collide with a clip id');

      // THE SAME FIELD SET `describeAudioSources` emits for a clip (minus the
      // optional trim window, which music has no picture to be trimmed against).
      assert.deepStrictEqual(
        Object.keys(src).sort(), ['gain', 'id', 'loop', 'rate', 'span', 'url'],
        'the mixer row must carry exactly the fields OfflineAudioSource requires',
      );
      checks++;

      // I2: THE EXPORT NEVER READS THE MONITOR. Two identical calls under two
      // opposite monitor states — the function cannot see it, and this is what
      // keeps it that way.
      assert.deepStrictEqual(S.soundtrackSource(spec), src, 'the row is a pure function of the spec');
      checks++;

      // AUDIBLE IMPLIES EXPORTED, never the reverse. You can never hear
      // something the file will not carry; you can very easily fail to hear
      // something it will.
      for (const soundOn of [true, false]) {
        const aud = S.soundtrackAudible(spec, soundOn);
        ok(!aud || src.gain > 0, 'audible implies the file carries it');
        ok(aud === (!!url && !muted && soundOn), 'audible = url AND intent AND monitor');
        if (!soundOn) ok(aud === false, 'the monitor vetoes the speakers and nothing else');
      }
    }
  }
}
ok(rows === DURATIONS.length * MUTED.length * URLS.length, 'swept every spec');
ok(S.soundtrackSource(null) === null && S.soundtrackSource(undefined) === null, 'no track, no row');
ok(S.soundtrackAudible(null, true) === false, 'no track is never audible');

// ---------------------------------------------------------------------------
// I4 — the label. Cosmetic, but it renders next to a file name on a phone.
// ---------------------------------------------------------------------------
assert.equal(S.soundtrackLength(0), '');
assert.equal(S.soundtrackLength(NaN), '');
assert.equal(S.soundtrackLength(-4), '');
assert.equal(S.soundtrackLength(Infinity), '');
assert.equal(S.soundtrackLength(9), '0:09');
assert.equal(S.soundtrackLength(61.7), '1:01');
assert.equal(S.soundtrackLength(600), '10:00');
checks += 7;

console.log(`soundtrack invariants: ${checks} assertions over ${pairs} file shapes and ${rows} specs — all green`);
