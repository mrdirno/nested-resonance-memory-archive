// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// Exercise the actual shipped parser/planner, not a second implementation.
import assert from 'node:assert/strict';
import esbuild from 'esbuild';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const temp = mkdtempSync(join(tmpdir(), 'captions-invariants-'));
try {
  const root = join(dirname(fileURLToPath(import.meta.url)), '../..');
  const out = join(temp, 'captions.mjs');
  await esbuild.build({ entryPoints: [join(root, 'src/lib/captions.ts')], outfile: out, bundle: true, platform: 'neutral', format: 'esm', logLevel: 'silent' });
  const C = await import(pathToFileURL(out).href);
  const cue = (id, start, end, text = 'A line') => ({ id, start, end, text });
  const track = (cues) => ({ cues, place: 'bc', size: 'md' });
  const reject = (value) => assert.throws(() => C.normalizeCaptionTrack(value), C.CaptionError);
  assert.deepEqual(C.normalizeCaptionTrack(undefined), track([]));
  for (const value of [false, [], 1, 'x', {}, { cues: 'x' }, { cues: [], place: 'bl' }, { cues: [], size: 'xl' }]) reject(value);
  const originals = [cue('b', 1, 2), cue('a', 0, 1)];
  assert.deepEqual(C.normalizeCaptionTrack(track(originals)).cues.map((x) => x.id), ['a', 'b']);
  assert.equal(originals[0].id, 'b', 'normalization must not mutate input');
  for (const bad of [cue('a', -1, 1), cue('a', 0, .049), cue('a', 3600, 3601), cue('a', NaN, 1), cue('a', 0, Infinity), cue('', 0, 1), cue('a', 0, 1, ''), cue('a', 0, 1, 'A'.repeat(241)), cue('a', 0, 1, 'a\u0000b'), cue('a', 0, 1, 'a\n\nb'), cue('a', 0, 1, '\ud800')]) reject(track([bad]));
  reject(track([cue('a', 0, 2), cue('b', 1, 3)]));
  reject(track([cue('a', 0, 1), cue('a', 1, 2)]));
  reject(track(Array.from({ length: 201 }, (_, i) => cue(String(i), i, i + 1))));
  assert.equal(C.normalizeCaptionTrack(track([cue('a', .1, .15)])).cues[0].end, .15);
  assert.equal(C.normalizeCaptionTrack(track([cue('a', 3599.95, 3600)])).cues[0].end, 3600);

  const rich = track([cue('one', 0, 1.005, '世界 🌊\nA <tag> & literal &amp; "quote"'), cue('two', 1.005, 3600, 'Another line')]);
  const withoutIds = (cues) => cues.map(({ id, ...rest }) => rest);
  for (const [format, exportFn] of [['srt', C.serializeSrt], ['vtt', C.serializeVtt]]) {
    const text = exportFn(rich);
    assert.ok(!text.includes('<tag>'), 'markup must be escaped');
    assert.deepEqual(withoutIds(C.parseCaptions(text, format)), withoutIds(rich.cues), `${format} preserves text, Unicode, multiline and millisecond times`);
    assert.deepEqual(withoutIds(C.parseCaptions('\ufeff' + text.replace(/\n/g, '\r\n'), format)), withoutIds(rich.cues));
  }
  const vtt = 'WEBVTT\n\nNOTE a comment\nIgnored\n\nid\n00:00.000 --> 00:01.000\nA &amp; B';
  assert.equal(C.parseCaptions(vtt)[0].text, 'A & B');
  for (const value of ['', '1\n00:00:00,000 --> 00:00:01,000\n<b>bold</b>', '1\n00:60:00,000 --> 00:00:01,000\nHi', 'WEBVTT\n\nSTYLE\n::cue { color:red }', 'WEBVTT\n\nREGION\nid:r', 'WEBVTT\n\n00:00.000 --> 00:01.000 align:start\nHi', 'WEBVTT\nX-TIMESTAMP-MAP=LOCAL:00:00.000\n\n00:00.000 --> 00:01.000\nHi', '1\n00:00:01,000 --> 00:00:00,000\nHi']) assert.throws(() => C.parseCaptions(value), C.CaptionError, value);
  assert.throws(() => C.parseCaptions('A'.repeat(256001)), C.CaptionError);
  assert.throws(() => C.parseCaptions(vtt, 'srt'), C.CaptionError);
  assert.throws(() => C.parseCaptions(C.serializeSrt(rich), 'vtt'), C.CaptionError);

  const draft = C.draftCaptions('one\ntwo\n\nthree', 10);
  assert.equal(draft.length, 3);
  assert.equal(draft[0].start, 0);
  assert.equal(draft.at(-1).end, 10);
  for (let i = 1; i < draft.length; i++) assert.equal(draft[i].start, draft[i - 1].end);
  assert.throws(() => C.draftCaptions('one\ntwo', .05), C.CaptionError);
  assert.throws(() => C.draftCaptions('a\n'.repeat(201), 100), C.CaptionError);
  assert.throws(() => C.draftCaptions('a'.repeat(241), 10), C.CaptionError);
  const timeline = track([cue('a', 0, 1), cue('b', 1, 2), cue('c', 3, 4)]);
  for (const [at, id] of [[-1, null], [0, 'a'], [.999, 'a'], [1, 'b'], [2, null], [3, 'c'], [4, null], [NaN, null], [Infinity, null]]) assert.equal(C.captionAt(timeline, at)?.id ?? null, id);
  assert.equal(C.captionAt(undefined, 0), null);
  const measure = (text, px) => [...text].length * px * .62;
  for (const aspect of [9 / 16, 1, 16 / 9, 5]) for (const size of ['sm', 'md', 'lg']) {
    const planned = C.planCaptions({ ...timeline, size }, aspect, measure);
    assert.equal(planned.length, 3);
    assert.equal(C.captionPlanAt(planned, 1), planned[1].plan);
    assert.equal(C.captionPlanAt(planned, 2), null);
    const long = C.planCaptions({ ...track([cue('long', 0, 1, 'word '.repeat(48).trim())]), size }, aspect, measure)[0].plan;
    assert.equal(long.truncated, false, 'caption words must not be ellipsized');
    assert.equal(long.lines.map((line) => line.text).join(' '), 'word '.repeat(48).trim());
    assert.ok(long.plate.x >= 0 && long.plate.y >= 0);
    assert.ok(long.plate.x + long.plate.w <= 1200.0001);
    assert.ok(long.plate.y + long.plate.h <= 1200 / aspect + .0001);
    const emoji = C.planCaptions({ ...track([cue('emoji', 0, 1, '🌊'.repeat(120))]), size }, aspect, measure)[0].plan;
    assert.equal(emoji.lines.map((line) => line.text).join(''), '🌊'.repeat(120));
    for (const line of emoji.lines) assert.ok(!/[\ud800-\udbff]$|^[\udc00-\udfff]/.test(line.text), 'wrapping must not split a Unicode surrogate pair');
  }
  assert.deepEqual(C.planCaptions(null, 1, measure), []);
  assert.equal(C.captionPlanAt(null, 0), null);
  console.log('CAPTIONS invariants: validation, import/export, timing and full-text geometry PASS');
} finally { rmSync(temp, { recursive: true, force: true }); }
