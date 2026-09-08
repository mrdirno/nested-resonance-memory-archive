// Author: Aldrin Payopay <aldrin.gdf@gmail.com> · GPL-3.0-only
// Run: node tests/unit/projectSoundtrack.invariants.mjs
// Real module, Fetch/Blob URLs and ZIP bytes; no reimplementation of the writer.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import esbuild from 'esbuild';
import JSZip from 'jszip';

const root = join(dirname(fileURLToPath(import.meta.url)), '../..');
const scratch = mkdtempSync(join(tmpdir(), 'collage-project-soundtrack-'));
const originalFileReader = globalThis.FileReader;
const originalImage = globalThis.Image;
const realCreate = URL.createObjectURL.bind(URL);
const realRevoke = URL.revokeObjectURL.bind(URL);
const realFetch = globalThis.fetch;
const realError = console.error;
const live = new Set();
const created = [];
let failures = [];
let checks = 0;
globalThis.FileReader = class {
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then(result => this.onload?.({ target: { result } }),
      error => this.onerror?.({ target: { error } }));
  }
};
URL.createObjectURL = blob => { const url = realCreate(blob); live.add(url); created.push(url); return url; };
URL.revokeObjectURL = url => { live.delete(url); realRevoke(url); };
console.error = (...args) => { failures.push(args.map(String).join(' ')); };
const test = async (name, fn) => { await fn(); checks++; console.log(`PASS ${name}`); };
const loadModule = async name => {
  const output = join(scratch, `${name}.mjs`);
  await esbuild.build({ entryPoints: [join(root, 'src/lib', `${name}.ts`)], outfile: output,
    bundle: true, format: 'esm', platform: 'node', logLevel: 'silent' });
  return import(pathToFileURL(output).href);
};
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const asFile = async blob => new File([await blob.arrayBuffer()], 'test.collage');
const readZip = async blob => JSZip.loadAsync(await blob.arrayBuffer());

try {
  const { buildProjectBlob, loadProject, releaseLoadedProject, assertProjectState } = await loadModule('project');
  const { MAX_PROJECT_SOUNDTRACK_BYTES: limit, PROJECT_SOUNDTRACK_PATH: member,
    normalizeProjectSoundtrack: normalize, createProjectSoundtrackMetadata, verifyProjectSoundtrackBytes,
  } = await loadModule('projectSoundtrack');
  const state = { version: '1.0', mode: 'simple', layout: { mode: 'minimal', primitive: 'rect',
    count: 1, seed: 0, aspect: 1, gutter: 0 }, style: { background: '#000000' },
    locks: [[0, 'photo']], captions: { version: 1, cues: [], place: 'bc', size: 'md' } };
  // A valid little-endian PCM WAV: the save path must retain its header and all
  // samples, not just something another decoder would consider equivalent.
  const wav = Buffer.alloc(44 + 80);
  wav.write('RIFF', 0); wav.writeUInt32LE(wav.length - 8, 4); wav.write('WAVEfmt ', 8);
  wav.writeUInt32LE(16, 16); wav.writeUInt16LE(1, 20); wav.writeUInt16LE(1, 22);
  wav.writeUInt32LE(8000, 24); wav.writeUInt32LE(8000, 28); wav.writeUInt16LE(1, 32);
  wav.writeUInt16LE(8, 34); wav.write('data', 36); wav.writeUInt32LE(80, 40);
  for (let i = 44; i < wav.length; i++) wav[i] = (i * 13) % 256;
  const audioFile = new File([wav], 'my original song.wav', { type: 'audio/wav' });
  const audioURL = URL.createObjectURL(audioFile);
  const imageURL = URL.createObjectURL(new Blob(['original picture'], { type: 'image/png' }));
  const previewURL = URL.createObjectURL(new Blob(['smaller preview'], { type: 'image/jpeg' }));
  const image = { id: 'photo', src: imageURL, previewSrc: previewURL, originalName: 'photo.png',
    width: 1, height: 1, analysis: {} };
  const track = { url: audioURL, name: audioFile.name, durationSec: 90, muted: true,
    level: 0.125, inSec: 2.75, outSec: 32.25, fadeSec: 0.5 };
  const archive = await buildProjectBlob(state, [image], track);
  const zip = await readZip(archive);
  const meta = JSON.parse(await zip.file('manifest.json').async('text'));
  const descriptor = meta.soundtrack;
  const rewrite = async edit => {
    const changed = await readZip(archive);
    const manifest = JSON.parse(await changed.file('manifest.json').async('text'));
    await edit(manifest, changed);
    changed.file('manifest.json', JSON.stringify(manifest));
    return new File([await changed.generateAsync({ type: 'uint8array' })], 'changed.collage');
  };
  const refused = async (file, { preflight = true, message } = {}) => {
    const before = new Set(live), count = created.length;
    failures = [];
    assert.equal(await loadProject(file), null);
    assert.deepEqual(live, before, 'every candidate URL must be released');
    if (preflight) assert.equal(created.length, count, 'metadata/bytes must refuse before URL mint');
    if (message) assert.match(failures.join('\n'), message);
  };

  await test('the actual ZIP preserves original PCM bytes, MIME, filename, SHA-256 and authored settings', async () => {
    const stored = await zip.file(member).async('uint8array');
    assert.deepEqual(Buffer.from(stored), wav);
    assert.equal(descriptor.sha256, sha256(wav));
    assert.equal(descriptor.sizeBytes, audioFile.size);
    assert.equal(descriptor.mimeType, 'audio/wav');
    assert.equal(descriptor.originalName, audioFile.name);
    assert.deepEqual(descriptor, { version: 1, storageFilename: 'original', originalName: audioFile.name,
      mimeType: 'audio/wav', sizeBytes: wav.length, sha256: sha256(wav), durationSec: 90,
      muted: true, level: 0.125, inSec: 2.75, outSec: 32.25, fadeSec: 0.5 });
    assert.equal(JSON.stringify(meta).includes('blob:'), false);
    assert.equal('soundtrack' in state, false);
  });
  await test('load returns a fresh original URL with authored settings; re-save preserves bytes and descriptor', async () => {
    const loaded = await loadProject(await asFile(archive));
    assert(loaded?.soundtrack);
    try {
      assert.notEqual(loaded.soundtrack.url, audioURL);
      assert.deepEqual({ ...loaded.soundtrack, url: audioURL }, track);
      assert.equal('soundtrack' in loaded.state, false);
      const restored = await (await fetch(loaded.soundtrack.url)).blob();
      assert.equal(restored.type, audioFile.type);
      assert.deepEqual(Buffer.from(await restored.arrayBuffer()), wav);
      const again = await readZip(await buildProjectBlob(loaded.state, loaded.images, loaded.soundtrack));
      const againMeta = JSON.parse(await again.file('manifest.json').async('text'));
      assert.deepEqual(againMeta.soundtrack, descriptor);
      assert.equal(sha256(await again.file(member).async('uint8array')), sha256(wav));
    } finally { releaseLoadedProject(loaded); }
  });
  await test('loaded originals and separate previews are released on stale-candidate disposal', async () => {
    const before = new Set(live);
    const loaded = await loadProject(await asFile(archive));
    assert(loaded?.soundtrack);
    const urls = [loaded.soundtrack.url, loaded.images[0].src, loaded.images[0].previewSrc];
    assert.equal(new Set(urls).size, 3);
    releaseLoadedProject(loaded); releaseLoadedProject(loaded);
    assert.deepEqual(live, before);
    for (const url of urls) await assert.rejects(fetch(url));
    assert.equal((await fetch(audioURL)).ok, true, 'original open work remains readable');
  });
  await test('a video container used as music retains its MIME and every opaque source byte', async () => {
    // Container bytes remain opaque here; codec support is the real-browser gate.
    const container = new Blob([Uint8Array.from([0, 0, 0, 20, 102, 116, 121, 112, 105, 115, 111, 109])], { type: 'video/mp4' });
    const url = URL.createObjectURL(container);
    try {
      const saved = await buildProjectBlob(state, [image], { url, name: 'camera sound.mp4', durationSec: 0 });
      const loaded = await loadProject(await asFile(saved));
      assert(loaded?.soundtrack);
      try {
        const original = await (await fetch(loaded.soundtrack.url)).blob();
        assert.equal(original.type, 'video/mp4');
        assert.deepEqual(await original.arrayBuffer(), await container.arrayBuffer());
        assert.deepEqual(Object.keys(loaded.soundtrack).sort(), ['durationSec', 'name', 'url']);
      } finally { releaseLoadedProject(loaded); }
    } finally { URL.revokeObjectURL(url); }
  });
  await test('an empty original MIME stays empty through ZIP load and re-save', async () => {
    const file = new File([wav], 'phone.wav');
    const url = URL.createObjectURL(file);
    try {
      const saved = await buildProjectBlob(state, [image], { url, name: file.name, durationSec: 0, muted: false, level: 0, fadeSec: 0 });
      const loaded = await loadProject(await asFile(saved));
      assert(loaded?.soundtrack);
      try {
        assert.equal((await (await fetch(loaded.soundtrack.url)).blob()).type, '');
        assert.equal(loaded.soundtrack.level, 0);
        assert.equal(loaded.soundtrack.muted, false);
        const again = await readZip(await buildProjectBlob(loaded.state, loaded.images, loaded.soundtrack));
        assert.equal(JSON.parse(await again.file('manifest.json').async('text')).soundtrack.mimeType, '');
      } finally { releaseLoadedProject(loaded); }
    } finally { URL.revokeObjectURL(url); }
  });
  await test('two-argument legacy saves and explicit null do not add a soundtrack field or member', async () => {
    for (const soundtrack of [undefined, null]) {
      const saved = await buildProjectBlob(state, [image], soundtrack);
      const old = await readZip(saved);
      assert.equal('soundtrack' in JSON.parse(await old.file('manifest.json').async('text')), false);
      assert.equal(old.file(member), null);
      const loaded = await loadProject(await asFile(saved));
      assert(loaded); assert.equal(loaded.soundtrack, null); releaseLoadedProject(loaded);
    }
  });
  await test('legacy image filename aliases and unknown state fields still open', async () => {
    const file = await rewrite(manifest => {
      delete manifest.soundtrack; delete manifest.mode;
      manifest.oldExtension = { retained: true };
      manifest.images[0].filename = manifest.images[0].storageFilename;
      delete manifest.images[0].storageFilename;
    });
    const loaded = await loadProject(file);
    assert(loaded); assert.equal(loaded.soundtrack, null);
    assert.deepEqual(loaded.state.oldExtension, { retained: true }); releaseLoadedProject(loaded);
  });
  await test('expired, empty, remote and non-OK soundtrack originals visibly refuse saving', async () => {
    const expired = URL.createObjectURL(new Blob([wav])); URL.revokeObjectURL(expired);
    const empty = URL.createObjectURL(new Blob([], { type: 'audio/wav' }));
    try {
      await assert.rejects(buildProjectBlob(state, [image], { ...track, url: expired }), /original could not be read/);
      await assert.rejects(buildProjectBlob(state, [image], { ...track, url: empty }), /must contain bytes/);
      let fetched = false;
      globalThis.fetch = async (...args) => { fetched = true; return realFetch(...args); };
      await assert.rejects(buildProjectBlob(state, [image], { ...track, url: 'https://example.invalid/song.wav' }), /local original/);
      assert.equal(fetched, false, 'remote URLs must not be fetched');
      globalThis.fetch = async url => url === audioURL ? new Response('not audio', { status: 503 }) : realFetch(url);
      await assert.rejects(buildProjectBlob(state, [image], track), /original could not be read/);
    } finally { globalThis.fetch = realFetch; URL.revokeObjectURL(empty); }
  });
  await test('256 MiB limit rejects before hashing or allocating an oversized source', async () => {
    let read = false;
    await assert.rejects(createProjectSoundtrackMetadata(track, { size: limit + 1, type: 'audio/wav',
      arrayBuffer: async () => { read = true; throw new Error('must not read'); } }), /256 MiB/);
    assert.equal(read, false);
    assert.equal(normalize({ ...descriptor, sizeBytes: limit }).sizeBytes, limit);
    await refused(await rewrite(manifest => { manifest.soundtrack.sizeBytes = limit + 1; }), { message: /256 MiB/ });
  });
  await test('metadata rejects unknown versions, extra URL/monitor state, bad paths and non-object values', async () => {
    for (const bad of [null, [], false, 'track', 1, { ...descriptor, version: 2 },
      { ...descriptor, url: 'https://example.invalid/song.wav' }, { ...descriptor, soundOn: true },
      { ...descriptor, soloId: 'track' }, { ...descriptor, storageFilename: '../original' },
      { ...descriptor, storageFilename: 'https://example.invalid/source' }]) {
      assert.throws(() => normalize(bad));
      await refused(await rewrite(manifest => { manifest.soundtrack = bad; }));
    }
    assert.equal(normalize(undefined), null);
  });
  await test('metadata rejects malformed checksums, size, MIME, name and authored values without coercion', async () => {
    for (const patch of [{ sha256: 'bad' }, { sha256: descriptor.sha256.toUpperCase() },
      { sizeBytes: 0 }, { sizeBytes: -1 }, { sizeBytes: 1.5 }, { sizeBytes: '124' },
      { originalName: '' }, { originalName: '\0track' }, { originalName: 'a'.repeat(1025) },
      { mimeType: 'https://example.test/sound' }, { mimeType: 'audio/wav\n' },
      { muted: 'false' }, { level: -0.1 }, { level: 1.1 }, { level: null },
      { durationSec: -1 }, { inSec: -1 }, { outSec: -1 }, { inSec: 5, outSec: 5 },
      { inSec: 5, outSec: 4 }, { fadeSec: -1 }, { fadeSec: '0.5' }]) {
      assert.throws(() => normalize({ ...descriptor, ...patch }));
      await refused(await rewrite(manifest => { Object.assign(manifest.soundtrack, patch); }));
    }
    for (const field of ['durationSec', 'level', 'inSec', 'outSec', 'fadeSec']) {
      for (const number of [NaN, Infinity, -Infinity]) assert.throws(() => normalize({ ...descriptor, [field]: number }));
    }
    const frozen = Object.freeze({ ...descriptor });
    assert.deepEqual(normalize(frozen), descriptor);
    assert.notEqual(normalize(frozen), frozen);
  });
  await test('trim requires paired endpoints inside known duration, tolerates rounding and retains unknown-duration or tiny windows', async () => {
    for (const patch of [{ inSec: undefined }, { outSec: undefined },
      { inSec: 90, outSec: 90.0000005 }, { inSec: 91, outSec: 92 },
      { inSec: 2, outSec: 90.000002 }]) {
      assert.throws(() => normalize({ ...descriptor, ...patch }));
      await refused(await rewrite(manifest => { Object.assign(manifest.soundtrack, patch); }));
    }
    for (const patch of [{ inSec: 2, outSec: 90.0000005 },
      { inSec: 2, outSec: 2.01 }, { durationSec: 0, inSec: 120, outSec: 150 }]) {
      const expected = { ...descriptor, ...patch };
      assert.deepEqual(normalize(expected), expected, 'valid values survive without clamping');
      const loaded = await loadProject(await rewrite(manifest => { Object.assign(manifest.soundtrack, patch); }));
      assert(loaded?.soundtrack);
      try {
        assert.equal(loaded.soundtrack.inSec, expected.inSec);
        assert.equal(loaded.soundtrack.outSec, expected.outSec);
        assert.equal(loaded.soundtrack.durationSec, expected.durationSec);
      } finally { releaseLoadedProject(loaded); }
    }
  });
  await test('missing original member refuses before any image or audio URL is minted', async () => {
    await refused(await rewrite((manifest, archive) => { archive.remove(member); }), { message: /missing its soundtrack/ });
  });
  await test('same-length corrupt original refuses its SHA-256 before any URL mint', async () => {
    const corrupted = Buffer.from(wav); corrupted[corrupted.length - 1] ^= 1;
    await refused(await rewrite((manifest, archive) => { archive.file(member, corrupted); }), { message: /checksum does not match/ });
    await assert.rejects(verifyProjectSoundtrackBytes(descriptor, new Uint8Array(corrupted)), /checksum/);
  });
  await test('short or expanded compressed members refuse the declared byte count before URL mint', async () => {
    await refused(await rewrite((manifest, archive) => { archive.file(member, wav.subarray(0, -1)); }), { message: /byte count/ });
    await refused(await rewrite((manifest, archive) => {
      manifest.soundtrack.sizeBytes = 1;
      archive.file(member, new Uint8Array(1024 * 1024), { compression: 'DEFLATE' });
    }), { message: /byte count/ });
  });
  await test('missing later image and malformed settings preflight before minting a valid soundtrack URL', async () => {
    await refused(await rewrite(manifest => { manifest.images.push({ ...manifest.images[0], id: 'missing', storageFilename: 'missing.png' }); }));
    for (const patch of [{ layout: null }, { layout: [] }, { style: null }, { style: [] }, { mode: {} }, { mode: 'other' }]) {
      assert.throws(() => assertProjectState({ ...state, ...patch }));
      await refused(await rewrite(manifest => { Object.assign(manifest, patch); }));
    }
  });
  await test('legacy decode failure releases every earlier image/preview and never mints audio', async () => {
    globalThis.Image = class { set src(value) { queueMicrotask(() => this.onerror?.()); } };
    await refused(await rewrite((manifest, archive) => {
      manifest.images.push({ ...manifest.images[0], id: 'broken', storageFilename: 'broken.png', width: 0, height: 0 });
      archive.file('images/broken.png', 'undecodable');
    }), { preflight: false, message: /undecodable source/ });
    globalThis.Image = originalImage;
  });
  await test('failure minting final soundtrack URL releases all prepared image URLs', async () => {
    const trackedCreate = URL.createObjectURL;
    let calls = 0;
    URL.createObjectURL = blob => { calls++; if (calls === 3) throw new Error('Injected audio URL allocation failure'); return trackedCreate(blob); };
    try { await refused(await asFile(archive), { preflight: false, message: /allocation failure/ }); }
    finally { URL.createObjectURL = trackedCreate; }
    assert.equal(calls, 3);
  });
  console.log(`PASS project soundtrack: ${checks} groups; exact originals and authored values survive, incompatible/corrupt candidates fail closed`);
} finally {
  for (const url of live) realRevoke(url);
  URL.createObjectURL = realCreate; URL.revokeObjectURL = realRevoke;
  globalThis.fetch = realFetch; console.error = realError;
  if (originalFileReader === undefined) delete globalThis.FileReader; else globalThis.FileReader = originalFileReader;
  if (originalImage === undefined) delete globalThis.Image; else globalThis.Image = originalImage;
  rmSync(scratch, { recursive: true, force: true });
}
