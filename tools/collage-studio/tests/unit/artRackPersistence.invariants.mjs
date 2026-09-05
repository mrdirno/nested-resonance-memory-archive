// Author: Aldrin Payopay <aldrin.gdf@gmail.com> · GPL-3.0-only
// Run: node tests/unit/artRackPersistence.invariants.mjs
// Exercise the actual writers/readers and real ZIP/Blob bytes. Browser tests
// separately prove native rendered pixels and real PNG decoding on SVG import.
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import esbuild from 'esbuild';
import JSZip from 'jszip';

const root = join(dirname(fileURLToPath(import.meta.url)), '../..');
const scratch = mkdtempSync(join(tmpdir(), 'collage-art-persistence-'));
const originalFileReader = globalThis.FileReader;
// JSZip's browser Blob path needs this browser API in Node. Do not mock ZIP I/O.
globalThis.FileReader = class {
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then(
      result => this.onload?.({ target: { result } }),
      error => this.onerror?.({ target: { error } }),
    );
  }
};
const load = async name => {
  const output = join(scratch, `${name}.mjs`);
  await esbuild.build({ entryPoints: [join(root, 'src/lib', `${name}.ts`)], outfile: output,
    bundle: true, format: 'esm', platform: 'node', logLevel: 'silent' });
  return import(pathToFileURL(output).href);
};
const clone = value => JSON.parse(JSON.stringify(value));
const urlsToRelease = [];
try {
  const { createDefaultArtRecipe, normalizeArtRecipe } = await load('artRack');
  const { buildProjectBlob, loadProject } = await load('project');
  const { projectMetadata, readProject, metaForAsset, escapeXmlText } = await load('svgProject');
  const { sessionEntries, preflightSessionAssets, hydrateSessionAssets } = await load('session');
  const art = normalizeArtRecipe(createDefaultArtRecipe());
  assert(art.layers.length > 0, 'the persistence fixture contains actual editable layers');
  const state = { version: '1.0', mode: 'simple', layout: { mode: 'minimal', primitive: 'rect',
    count: 1, seed: 0, aspect: 1, gutter: 0 }, style: { background: '#000000' } };
  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j1XkAAAAASUVORK5CYII=', 'base64');
  const source = URL.createObjectURL(new Blob([png], { type: 'image/png' }));
  urlsToRelease.push(source);
  const photo = { id: 'photo', src: source, previewSrc: source, originalName: 'photo.png',
    width: 1, height: 1, analysis: { color: { r: 20, g: 30, b: 40 } } };
  const native = { ...photo, id: 'native', originalName: 'art-rack.png', art };
  const pool = [photo, native];

  const archive = await buildProjectBlob(state, pool);
  const zip = await JSZip.loadAsync(await archive.arrayBuffer());
  const manifest = JSON.parse(await zip.file('manifest.json').async('text'));
  assert.deepEqual(manifest.images[1].art, art);
  assert.equal(Object.hasOwn(manifest.images[0], 'art'), false, 'ordinary images stay ordinary');
  assert.deepEqual(await zip.file(`images/${manifest.images[1].storageFilename}`).async('uint8array'), new Uint8Array(png));
  const reopened = await loadProject(new File([archive], 'native.collage'));
  assert(reopened, 'actual archive reopens');
  for (const image of reopened.images) urlsToRelease.push(image.src, image.previewSrc);
  assert.deepEqual(reopened.state, state);
  assert.deepEqual(reopened.images.map(image => image.id), ['photo', 'native']);
  assert.deepEqual(reopened.images[1].art, art);
  assert.deepEqual(new Uint8Array(await (await fetch(reopened.images[1].src)).arrayBuffer()), new Uint8Array(png));
  assert.equal(Object.hasOwn(reopened.images[0], 'art'), false);
  reopened.images[1].art.duration = art.duration === 2 ? 3 : 2;
  assert.deepEqual(native.art, art, 'reopening does not mutate the live recipe');
  console.log('PASS Art Rack archive: recipe, source order and real poster bytes survive actual ZIP save/open');

  const metadata = pool.map(metaForAsset);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg">${projectMetadata(state, metadata)}</svg>`;
  const svgBack = readProject(svg);
  assert(svgBack);
  assert.deepEqual(svgBack.images[1].art, art);
  assert.equal(Object.hasOwn(svgBack.images[0], 'art'), false);
  metadata[1].art.duration = art.duration === 2 ? 3 : 2;
  assert.deepEqual(native.art, art, 'SVG metadata clones recipes rather than sharing mutable draft state');

  const entries = sessionEntries(pool);
  const before = clone(entries);
  const checked = preflightSessionAssets(entries);
  assert.deepEqual(checked, entries);
  assert.notEqual(checked[1].art, entries[1].art);
  assert.notEqual(checked[1].art.layers, entries[1].art.layers);
  assert.deepEqual(entries, before, 'recovery preflight does not modify stored metadata');
  const recovered = hydrateSessionAssets(entries, {
    photo: { src: 'blob:photo', previewSrc: 'blob:photo-small' },
    native: { src: 'blob:art', previewSrc: 'blob:art-small' },
  });
  assert(recovered);
  assert.deepEqual(recovered[1].art, art);
  assert.equal(recovered[1].previewSrc, 'blob:art-small');
  assert.equal(Object.hasOwn(recovered[0], 'art'), false);
  recovered[1].art.duration = art.duration === 2 ? 3 : 2;
  assert.deepEqual(entries, before, 'recovered recipes cannot change stored metadata by reference');
  console.log('PASS Art Rack SVG/recovery: all layers survive; metadata stays independent; old photos stay compatible');

  const invalidRecipes = [null, {}, { ...clone(art), version: 999 },
    { ...clone(art), layers: Array.from({ length: 9 }, () => clone(art.layers[0])) }];
  const createURL = URL.createObjectURL;
  const previousError = console.error;
  let minted = 0;
  URL.createObjectURL = (...args) => { minted++; return createURL(...args); };
  console.error = () => {}; // Expected, visible-to-caller refusal; do not bury real test failures.
  try {
    for (const badArt of invalidRecipes) {
      const badPool = [photo, { ...native, art: badArt }];
      await assert.rejects(buildProjectBlob(state, badPool));
      assert.throws(() => projectMetadata(state, badPool));
      assert.throws(() => sessionEntries(badPool));
      const badEntries = [entries[0], { ...entries[1], art: badArt }];
      assert.equal(preflightSessionAssets(badEntries), null);
      assert.equal(hydrateSessionAssets(badEntries, {
        photo: { src: 'blob:photo', previewSrc: 'blob:photo' },
        native: { src: 'blob:art', previewSrc: 'blob:art' },
      }), null, 'a malformed late recipe refuses the whole recovery');

      const badManifest = clone(manifest);
      badManifest.images[1].art = badArt;
      const badZip = await JSZip.loadAsync(await archive.arrayBuffer());
      badZip.file('manifest.json', JSON.stringify(badManifest));
      const file = new File([await badZip.generateAsync({ type: 'uint8array' })], 'bad.collage');
      minted = 0;
      assert.equal(await loadProject(file), null);
      assert.equal(minted, 0, 'the first valid archive source must not mint before the final recipe is checked');

      const badSvg = `<svg xmlns="http://www.w3.org/2000/svg"><metadata id="collage-project">${
        escapeXmlText(JSON.stringify({ format: 1, state, images: badEntries }))
      }</metadata><image data-src-id="photo" href="${source}"/></svg>`;
      assert.equal(readProject(badSvg), null);
      assert.equal(await loadProject(new File([badSvg], 'bad.svg', { type: 'image/svg+xml' })), null);
      assert.equal(minted, 0, 'SVG recipe preflight finishes before source reads or object URLs');
    }
  } finally {
    URL.createObjectURL = createURL;
    console.error = previousError;
  }
  console.log('PASS Art Rack refusal: malformed final recipe rejects every writer/reader before any archive or SVG URL allocation');
} finally {
  for (const url of new Set(urlsToRelease)) URL.revokeObjectURL(url);
  if (originalFileReader === undefined) delete globalThis.FileReader;
  else globalThis.FileReader = originalFileReader;
  rmSync(scratch, { recursive: true, force: true });
}
