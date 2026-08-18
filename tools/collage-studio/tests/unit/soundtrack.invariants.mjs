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
const I = await load('src/lib/intake.ts', 'intake');

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

// THE SHIPPED LADDER, not a copy of it. This was three inline predicates
// re-spelled here, which measured a paraphrase of `ingestFiles` rather than
// `ingestFiles` — the exact drift this repo has filed twice (`lib/level.ts` I5:
// the gain read `t.muted ? 0 : 1` in one emitter and `wanted ? 1 : 0` in the
// other, and only the copy was under test). `lib/intake.ts` now owns the order
// of these tests, so the sweep asks IT. `'any'` is the intent every path here
// has always used; the music button's intent is swept in intake.invariants.mjs.
const bucketOf = (f) => I.routeIntake(f, 'any');

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

      // THE SAME FIELD SET `describeAudioSources` emits for a clip. The window
      // is in it now — music has no picture to be trimmed against, but it does
      // have a part you wanted, which is what a range on a song means. And the
      // range fade rides with it: `fadeSec` joined the row when lib/windowFade
      // landed, and OfflineAudioSource consumes it (offlineAudio.ts) — this
      // list went stale in that commit and sat red on HEAD until noticed.
      assert.deepStrictEqual(
        Object.keys(src).sort(), ['fadeSec', 'gain', 'id', 'inSec', 'loop', 'outSec', 'rate', 'span', 'url'],
        'the mixer row must carry exactly the fields OfflineAudioSource requires',
      );
      checks++;
      ok(src.inSec === undefined && src.outSec === undefined, 'no range set means no range emitted');

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

// ---------------------------------------------------------------------------
// I5 — THE RANGE. "Need a way to click it and select the range", from the field.
//
// The whole claim of DECISION 1b is that keeping `span: 0` is not a leftover but
// the thing that makes a range on MUSIC correct, so it is asserted the only way
// a claim like that can be: by MODELLING THE MIXER (the real `normaliseWindow` +
// `audioSchedule`, not a paraphrase of them) and running both the shipped
// resolution and the tempting one side by side.
//
// The two lengths a song has are genuinely different numbers. `durationSec` is
// what `<audio>.duration` reported and what the OUT slider's max was; the mixer
// decodes and gets `buf.duration`, which for an mp3 differs by the encoder's
// delay and padding — in either direction, depending on the encoder and the
// browser's demuxer. The sweep walks that hop across its real range.
// ---------------------------------------------------------------------------
const W = await load('src/lib/clipWindow.ts', 'clipwindow');

/**
 * THE MIXER, as `offlineAudio.mixSources` actually performs it — the two lines
 * copied here are the two lines under test, and they are the reason this reads
 * `src.span > 0 ? src.span : bufDur` rather than just using a duration.
 */
const mix = (src, bufDur, startAt, seconds) => {
  const span = src.span > 0 ? src.span : bufDur;
  const window = W.normaliseWindow(span, src.inSec, src.outSec);
  return {
    window,
    sched: W.audioSchedule({ window, loop: src.loop, rate: src.rate ?? 1 }, startAt, seconds, bufDur),
  };
};

const CONTAINER = [12, 30.5, 127, 203.77, 600];
// The decoded length minus the container length. Zero, an mp3 frame (26 ms), a
// generous padding, and both signs — a demuxer that reports short is as ordinary
// as one that reports long.
const HOP = [0, 0.026, 0.104, -0.026, -0.104];
const TAKES = [4, 30, 120];

let ranges = 0;
let lappedWhenHelpful = 0;
for (const dur of CONTAINER) {
  // Exactly the ranges the sheet can author: the two handles are `<input
  // type="range" min={0} max={span}>`, so OUT === dur is not a corner case, it
  // is what "from the drop to the end" produces on the first drag.
  const RANGES = [
    undefined,                      // untrimmed
    [0, dur],                       // both handles at the ends
    [dur * 0.25, dur],              // the common one: start late, run to the end
    [dur * 0.3, dur * 0.6],         // a middle section
    [0, dur * 0.5],                 // the first half
    [dur - 0.2, dur],               // a sliver at the very end
  ];
  for (const r of RANGES) {
    const spec = {
      url: 'blob:song', name: 'song.mp3', durationSec: dur, muted: false,
      inSec: r ? r[0] : undefined, outSec: r ? r[1] : undefined,
    };
    const src = S.soundtrackSource(spec);
    ranges++;

    // I5a — THE SPAN IS STILL ZERO. The one invariant a range could plausibly
    // have been thought to relax, and the one it must not.
    ok(src.span === 0, `span must stay 0 with a range set (${dur}, ${r})`);

    // I5b — PASS-THROUGH, NOT RESOLUTION. Two copies of a window is the shape
    // this project keeps getting burned by; the row carries the user's numbers
    // verbatim and the mixer is the only thing that resolves them.
    ok(Object.is(src.inSec, spec.inSec) && Object.is(src.outSec, spec.outSec),
      'the row carries the range verbatim');

    for (const hop of HOP) {
      const bufDur = dur + hop;
      for (const seconds of TAKES) {
        const { window, sched } = mix(src, bufDur, 0, seconds);

        // I5c — MUSIC IS NEVER SILENCED BY ITS OWN RANGE, and never LAPPED.
        // `silent` and `lapped` both mean "the window ran past the end of the
        // sound", which cannot happen when the window was resolved against that
        // same sound. This is the assertion DECISION 1b exists to make true.
        ok(!sched.silent, `a range on music is never silent (dur ${dur} hop ${hop})`);
        ok(!sched.lapped, `a range on music never laps (dur ${dur} hop ${hop} range ${r})`);
        ok(!sched.truncated, 'and never truncates');
        ok(sched.starts.length === 1, 'one node: music is periodic at its own window');

        // I5d — THE LOOP REGION IS INSIDE THE DECODED BUFFER. A `loopEnd` past
        // the buffer is undefined behaviour in Web Audio, which is the reason
        // `spanLimit` exists at all.
        const st = sched.starts[0];
        ok(st.offset >= -1e-9 && st.offset <= bufDur + 1e-9, 'offset inside the buffer');
        if (st.loop) {
          ok(st.loopStart >= -1e-9, 'loopStart inside the buffer');
          ok(st.loopEnd <= bufDur + 1e-9, 'loopEnd inside the buffer');
          ok(st.loopEnd > st.loopStart, 'a loop region with room in it');
        }

        // I5e — AND THE SOUND STAYS IN THE PART THE USER PICKED, for the whole
        // take. Asserted against `schedulePositionAt` — the model of the node —
        // rather than against a second copy of the algebra.
        for (let k = 0; k <= 40; k++) {
          const u = (seconds * k) / 40;
          const pos = W.schedulePositionAt(sched.starts, u);
          ok(pos !== null, 'the music is playing somewhere at every instant');
          ok(pos >= window.inSec - 1e-6 && pos <= window.outSec + 1e-6,
            `position ${pos} outside [${window.inSec}, ${window.outSec}] at u=${u}`);
        }
      }

      // I5f — THE CONTRAST, so the decision above is load-bearing and not a
      // story. Hand `durationSec` over as the span — the "helpful" edit — and
      // the same user range takes the LAPPED branch the moment the decoded
      // buffer is shorter than the container: one non-looping node per picture
      // lap, a sliver of silence cut into every repeat, forever. The failure
      // this sweep is protecting is reproduced here rather than described.
      if (r && bufDur < dur && r[1] > bufDur) {
        const helpful = { ...src, span: dur };
        const bad = mix(helpful, bufDur, 0, 30);
        if (bad.sched.lapped) lappedWhenHelpful++;
      }
    }
  }
}
ok(lappedWhenHelpful > 0,
  'the contrast case must actually reproduce the lapped defect, or I5 proves nothing');

// ---------------------------------------------------------------------------
// I6 — THE LABEL SIDE. `soundtrackWindow` is the ONLY place `durationSec` is
// treated as a span, it is for the chip and the sliders, and it must be total:
// the length arrives asynchronously, so every call before it lands is made
// against 0 / NaN / Infinity and none of them may throw or draw a handle
// somewhere impossible.
// ---------------------------------------------------------------------------
let labels = 0;
for (const dur of [0, NaN, Infinity, -5, 0.1, 12, 127, 600]) {
  for (const r of [undefined, [0, dur], [3, 9], [9, 3], [-4, 1e9], [NaN, NaN], [5, 5]]) {
    const spec = { url: 'blob:s', name: 's.mp3', durationSec: dur, muted: false,
      inSec: r ? r[0] : undefined, outSec: r ? r[1] : undefined };
    const w = S.soundtrackWindow(spec);
    labels++;
    ok(Number.isFinite(w.inSec) && Number.isFinite(w.outSec) && Number.isFinite(w.length),
      `a drawable window for duration ${dur}`);
    ok(w.inSec >= 0 && w.outSec >= w.inSec, 'never inverted');
    if (Number.isFinite(dur) && dur > 0) ok(w.outSec <= dur + 1e-9, 'never past the track');
    const label = S.soundtrackRangeLabel(spec);
    ok(w.full ? label === '' : /^\d+:\d\d→\d+:\d\d$/.test(label),
      `a full window says nothing, a trimmed one says what (${dur}, ${r}) -> "${label}"`);
  }
}
ok(S.soundtrackRangeLabel(null) === '', 'no track, no badge');
ok(S.soundtrackClock(0) === '0:00', 'a position of zero is a real answer');
ok(S.soundtrackLength(0) === '', 'a length of zero is not');
checks += 3;

console.log(`soundtrack invariants: ${checks} assertions over ${pairs} file shapes, ${rows} specs, ${ranges} ranges and ${labels} label cases — all green`);
