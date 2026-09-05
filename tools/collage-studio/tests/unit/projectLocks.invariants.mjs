// Author: Aldrin Payopay <aldrin.gdf@gmail.com> · GPL-3.0-only
// Run: node tests/unit/projectLocks.invariants.mjs
// The actual TypeScript modules are bundled, never reimplemented here.
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import esbuild from 'esbuild';
import JSZip from 'jszip';

const root = join(dirname(fileURLToPath(import.meta.url)), '../..');
const scratch = mkdtempSync(join(tmpdir(), 'collage-project-integrity-'));
// JSZip's browser Blob path uses FileReader, which Node does not expose. Only
// adapt that browser API; real Blob bytes still flow through the actual ZIP.
const originalFileReader = globalThis.FileReader;
globalThis.FileReader = class {
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then(
      (result) => this.onload?.({ target: { result } }),
      (error) => this.onerror?.({ target: { error } }),
    );
  }
};
const load = async (name) => {
  const output = join(scratch, `${name}.mjs`);
  await esbuild.build({ entryPoints: [join(root, 'src/lib', `${name}.ts`)], outfile: output,
    bundle: true, format: 'esm', platform: 'node', logLevel: 'silent' });
  return import(pathToFileURL(output).href);
};

try {
  const { normalizeProjectLocks: normalize, MAX_PROJECT_LOCK_SLOTS: slots } = await load('projectLocks');
  const pool = Object.freeze([{ id: 'a' }, { id: 'b' }, { id: '__proto__' }].map(Object.freeze));
  for (const bad of [undefined, null, false, 1, 'pins', {}, new Map([[0, 'a']])]) {
    assert.deepEqual(normalize(bad, pool), []);
  }
  const raw = Object.freeze([
    [12, 'a'], [2, 'b'], [12, 'b'], [0, 'a'], [1, 'a'], [slots - 1, '__proto__'],
    [-1, 'a'], [NaN, 'a'], [Infinity, 'a'], [0.5, 'a'], [slots, 'a'],
    [Number.MAX_SAFE_INTEGER, 'a'], ['3', 'a'], [3, 'missing'], [4, null],
    null, {}, [5], [6, 'a', 'extra'],
  ].map((entry) => Array.isArray(entry) ? Object.freeze(entry) : entry));
  const expected = [[0, 'a'], [1, 'a'], [2, 'b'], [12, 'b'], [slots - 1, '__proto__']];
  assert.deepEqual(normalize(raw, pool), expected);
  assert.deepEqual(normalize(expected, pool), expected);
  assert.deepEqual(normalize([...expected].reverse(), pool), expected);
  assert.deepEqual(normalize(raw, []), []);
  assert.equal(Object.is(normalize([[-0, 'a']], pool)[0][0], -0), false);

  let assertions = 0;
  for (let count = 1; count <= 64; count++) {
    const sourcePool = Array.from({ length: count }, (_, n) => ({ id: `source-${n}` }));
    const entries = Array.from({ length: count * 3 }, (_, n) => [n * 3, sourcePool[n % count].id]);
    const normalized = normalize(entries, sourcePool);
    assert.deepEqual(normalized, entries); assertions++;
    assert.deepEqual(normalize(normalized, sourcePool), normalized); assertions++;
    assert.deepEqual(normalize([...entries].reverse(), sourcePool), entries); assertions++;
    // Source repetition remains legal; a one-source collage can pin 3 cells.
    assert.equal(normalized.length, entries.length); assertions++;
    const shorterPool = sourcePool.slice(1);
    assert(normalize(entries, shorterPool).every(([, id]) => id !== sourcePool[0].id)); assertions++;
  }
  console.log(`PASS project placement: ${assertions} generated assertions plus malformed, duplicate, boundary and frozen-input cases`);

  const { buildProjectBlob, loadProject } = await load('project');
  const state = { version: '1.0', mode: 'simple', layout: { mode: 'minimal', primitive: 'rect',
    count: 1, seed: 0, aspect: 1, gutter: 0 }, style: { background: '#000000' } };
  // Real Fetch/Blob/ZIP paths, including real object-URL expiry. The archive
  // contents must preserve the required bytes and safely omit a dead preview.
  const original = URL.createObjectURL(new Blob(['required original bytes'], { type: 'image/png' }));
  const expired = URL.createObjectURL(new Blob(['expired bytes']));
  URL.revokeObjectURL(expired);
  const image = { id: 'source', src: original, previewSrc: original, originalName: 'photo.png',
    width: 1, height: 1, analysis: {} };
  try {
    const archive = await buildProjectBlob(state, [image]);
    const zip = await JSZip.loadAsync(await archive.arrayBuffer());
    const meta = JSON.parse(await zip.file('manifest.json').async('text'));
    assert.equal(await zip.file(`images/${meta.images[0].storageFilename}`).async('text'), 'required original bytes');
    await assert.rejects(buildProjectBlob(state, [{ ...image, src: expired }]), /Could not save photo\.png/);
    await assert.rejects(buildProjectBlob(state, [{ ...image, src: 'data:image/png;base64,' }]), /Could not save photo\.png/);

    const realFetch = globalThis.fetch;
    try {
      globalThis.fetch = async (url, ...args) => url === 'test:unavailable'
        ? new Response('error body is not a photograph', { status: 503 }) : realFetch(url, ...args);
      await assert.rejects(buildProjectBlob(state, [{ ...image, src: 'test:unavailable' }]), /Could not save photo\.png/);
    } finally { globalThis.fetch = realFetch; }

    const previousWarn = console.warn;
    let warning = '';
    console.warn = (message) => { warning += String(message); };
    try {
      const fallback = await buildProjectBlob(state, [{ ...image, previewSrc: expired }]);
      const fallbackZip = await JSZip.loadAsync(await fallback.arrayBuffer());
      assert(fallbackZip.file(`images/${meta.images[0].storageFilename}`));
      assert.equal(fallbackZip.file(`previews/${meta.images[0].storageFilename}`), null);
      assert.match(warning, /Failed to save preview/);
    } finally { console.warn = previousWarn; }
    console.log('PASS project archive: original bytes survive; expired, empty and non-OK sources reject; preview failure retains a usable archive');
    const badTrack = { cues: [{ id: 'bad', start: 3, end: 1, text: 'Must refuse' }], place: 'bc', size: 'md' };
    const badZip = new JSZip();
    badZip.file('manifest.json', JSON.stringify({ ...state, images: [], captions: badTrack }));
    const badArchive = new File([await badZip.generateAsync({ type: 'uint8array' })], 'bad.collage');
    const badSvg = new File([
      `<svg xmlns="http://www.w3.org/2000/svg"><metadata id="collage-project">${JSON.stringify({
        format: 1, state: { ...state, captions: badTrack }, images: [],
      })}</metadata></svg>`,
    ], 'bad.svg', { type: 'image/svg+xml' });
    const previousError = console.error;
    const rejections = [];
    console.error = (...args) => rejections.push(args);
    try {
      assert.equal(await loadProject(badArchive), null);
      assert.equal(await loadProject(badSvg), null);
      assert.equal(rejections.length, 2);
    } finally { console.error = previousError; }
    console.log('PASS caption import: malformed archive and SVG tracks refuse before hydration');
  } finally { URL.revokeObjectURL(original); }
} finally {
  if (originalFileReader === undefined) delete globalThis.FileReader;
  else globalThis.FileReader = originalFileReader;
  rmSync(scratch, { recursive: true, force: true });
}
