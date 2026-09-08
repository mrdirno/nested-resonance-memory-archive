import JSZip from 'jszip';
import { AppState, ImageAsset, ProjectManifest } from '../types';
import { readProject, readImageSources } from './svgProject';
import { normalizeCaptionTrack } from './captions';
import { normalizeArtRecipe } from './artRack';
import type { SoundtrackSpec } from './soundtrack';
import {
  PROJECT_SOUNDTRACK_PATH, createProjectSoundtrackMetadata, normalizeProjectSoundtrack,
  restoreProjectSoundtrack, verifyProjectSoundtrackBytes,
} from './projectSoundtrack';

export interface LoadedProject {
  state: AppState;
  images: ImageAsset[];
  /** Absent/null means no soundtrack; never retain a previous project's music. */
  soundtrack?: SoundtrackSpec | null;
}

/** Validate the shared hydration boundary without rejecting unknown legacy fields. */
export function assertProjectState(value: unknown): asserts value is AppState {
  const record = (v: unknown): v is Record<string, unknown> =>
    !!v && typeof v === 'object' && !Array.isArray(v);
  if (!record(value) || !record(value.layout) || !record(value.style)
    || (value.mode !== undefined && value.mode !== 'simple' && value.mode !== 'advanced')) {
    throw new Error('Invalid project settings: layout, style or mode.');
  }
}

/** Discard a fully read candidate that became stale or was refused by its caller. */
export const releaseLoadedProject = (loaded: LoadedProject): void => {
  const urls = new Set(loaded.images.flatMap(image => [image.src, image.previewSrc]));
  if (loaded.soundtrack?.url) urls.add(loaded.soundtrack.url);
  for (const url of urls) {
    if (url?.startsWith('blob:')) { try { URL.revokeObjectURL(url); } catch { /* already gone */ } }
  }
};

/**
 * Build the `.collage` archive as a Blob WITHOUT downloading it. Extracted from
 * `saveProject`. Manual saves can include the original soundtrack container and
 * its authored settings. Moving video clips remain represented by their frames.
 * Crash recovery uses the separate incremental session store, not this ZIP path.
 */
export const buildProjectBlob = async (
  state: AppState, images: ImageAsset[], soundtrack?: SoundtrackSpec | null,
): Promise<Blob> => {
  assertProjectState(state);
  const zip = new JSZip();

  // 1. Manifest
  // Ensure unique filenames for ZIP storage
  const imageMeta = images.map((img, idx) => {
    // Get extension
    const ext = img.originalName ? img.originalName.split('.').pop() : 'png';
    const safeFilename = `asset-${idx}-${img.id}.${ext}`;

    return {
      id: img.id,
      storageFilename: safeFilename, // Internal name in ZIP
      originalName: img.originalName || 'image.png',
      // The asset has always known its own size and the manifest threw it away,
      // so `loadProject` decoded every photograph back — sequentially — purely to
      // relearn two numbers. Written from now on; absent on older archives, which
      // is why the load path still has a decode fallback.
      width: img.width,
      height: img.height,
      analysis: img.analysis,
      ...(img.art === undefined ? {} : { art: normalizeArtRecipe(img.art) }),
    };
  });

  const manifest: ProjectManifest = {
    ...state,
    images: imageMeta
  };

  if (soundtrack) {
    // The app owns a File-backed URL. Never substitute a remote reference or a
    // rendered mix: a saved project must carry the original container bytes.
    if (!soundtrack.url?.startsWith('blob:')) throw new Error('Could not save the soundtrack — its local original is unavailable. Your work is still open.');
    let original: Blob;
    try {
      const response = await fetch(soundtrack.url);
      if (!response.ok) throw new Error('unreadable source');
      original = await response.blob();
    } catch {
      throw new Error(`Could not save ${soundtrack.name || 'the soundtrack'} — its original could not be read. Your work is still open; try saving again.`);
    }
    manifest.soundtrack = await createProjectSoundtrackMetadata(soundtrack, original);
    zip.file(PROJECT_SOUNDTRACK_PATH, original, { compression: 'STORE' });
  }

  zip.file("manifest.json", JSON.stringify(manifest, null, 2));

  // 2. Images — the originals, and the thumbnail tier beside them.
  //
  // WHY `previews/` EXISTS. The app draws `previewSrc` — a <=1024px JPEG built at
  // upload — for every preview render and every Stage frame (`stage.ts`: "The
  // Stage draws `previewSrc` ... everywhere"). An archive that stored only the
  // originals made `loadProject` alias `previewSrc` to the full-resolution
  // image, so every reopened project quietly promoted its whole pool to full-res
  // previews: a 4032x3024 photo is 15.5x the pixels of its thumbnail, re-decoded
  // on every slider drag. Additive and backward compatible — an archive without
  // this folder loads exactly as it always did.
  const imgFolder = zip.folder("images");
  const previewFolder = zip.folder("previews");
  if (imgFolder) {
    for (let i = 0; i < images.length; i++) {
      const img = images[i];
      const meta = imageMeta[i];
      try {
        const response = await fetch(img.src);
        if (!response.ok) throw new Error(`source returned HTTP ${response.status}`);
        const blob = await response.blob();
        if (blob.size === 0) throw new Error('source is empty');
        imgFolder.file(meta.storageFilename, blob);
      } catch {
        // The reader refuses a missing required source. Do not download an
        // archive that only LOOKS saved and cannot reopen: the caller reports
        // this rejection and retains its unsaved-work state.
        throw new Error(`Could not save ${img.originalName || 'a source image'} — its original could not be read. Your composition is still open; try saving again.`);
      }
      // Only when it is genuinely a different image: `createThumbnail` returns
      // the source unchanged under 1024px, and storing those bytes twice would
      // grow every archive for nothing.
      if (previewFolder && img.previewSrc && img.previewSrc !== img.src) {
        try {
          const response = await fetch(img.previewSrc);
          if (!response.ok) throw new Error(`preview returned HTTP ${response.status}`);
          const p = await response.blob();
          if (p.size === 0) throw new Error('preview is empty');
          previewFolder.file(meta.storageFilename, p);
        } catch (e) {
          console.warn(`Failed to save preview for ${img.id}`, e);
        }
      }
    }
  }

  // 3. Generate
  return await zip.generateAsync({ type: "blob" });
};

export const saveProject = async (state: AppState, images: ImageAsset[], soundtrack?: SoundtrackSpec | null) => {
  const content = await buildProjectBlob(state, images, soundtrack);

  // Download
  const url = URL.createObjectURL(content);
  const a = document.createElement('a');
  a.href = url;
  a.download = `project-${Date.now()}.collage`;
  a.click();
  URL.revokeObjectURL(url);
};

/**
 * How long a single image gets to decode before the load gives up on it.
 *
 * THE HANG THIS EXISTS FOR (collage well, bug: "endless loop of restore, also
 * does not restore quickly"): the archive branch below used to await
 * `imgElem.onload` with NO `onerror` and no timeout. An asset the browser
 * refuses to decode — a truncated blob from a write that hit quota, or a 4K
 * frame on a phone already at its memory line — fires `error`, never `load`, and
 * that promise never settles. Open, or Restore, then hangs FOREVER: no picture,
 * no message, no failure. Reload, and the offer is right there again. That is
 * the loop the report describes. `loadFromSVG` twenty lines down always handled
 * `onerror`; this branch is the one that forgot it.
 */
const DECODE_TIMEOUT_MS = 15_000;

/**
 * Intrinsic size for one source, without ever hanging. Manifest first (archives
 * written from 2026-08-09 carry it, so the common path decodes NOTHING); then a
 * real decode that resolves on load, on error, AND on a timer.
 */
const measureSource = (url: string, meta: any): Promise<{ w: number; h: number }> => {
  const mw = meta?.width, mh = meta?.height;
  if (typeof mw === 'number' && typeof mh === 'number' && Number.isFinite(mw) && Number.isFinite(mh) && mw > 0 && mh > 0) {
    return Promise.resolve({ w: mw, h: mh });
  }
  return new Promise((resolve) => {
    const el = new Image();
    let settled = false;
    const finish = (w: number, h: number) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve({ w, h });
    };
    const timer = setTimeout(() => finish(0, 0), DECODE_TIMEOUT_MS);
    el.onload = () => finish(el.naturalWidth || el.width, el.naturalHeight || el.height);
    el.onerror = () => finish(0, 0);
    el.src = url;
  });
};

/** Stop decompression at the declared, validated bound instead of allocating an
 * untrusted member in full and discovering afterwards that it was too large. */
const readSoundtrackBytes = (file: JSZip.JSZipObject, expected: number): Promise<ArrayBuffer> =>
  new Promise((resolve, reject) => {
    const chunks: Uint8Array[] = [];
    let total = 0;
    let stopped = false;
    // JSZip 3.10 exposes this browser API but omits it from JSZipObject's types.
    const stream = (file as JSZip.JSZipObject & {
      internalStream(type: 'uint8array'): JSZip.JSZipStreamHelper<Uint8Array>;
    }).internalStream('uint8array');
    const fail = (error: Error) => {
      if (stopped) return;
      stopped = true; stream.pause(); chunks.length = 0; reject(error);
    };
    stream.on('data', (chunk: Uint8Array) => {
      if (stopped) return;
      total += chunk.byteLength;
      if (total > expected) { fail(new Error('Invalid project soundtrack: original byte count exceeds its metadata.')); return; }
      chunks.push(chunk);
    });
    stream.on('error', fail);
    stream.on('end', () => {
      if (stopped) return;
      if (total !== expected) { fail(new Error('Invalid project soundtrack: original byte count does not match.')); return; }
      const bytes = new Uint8Array(total);
      let offset = 0;
      for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
      chunks.length = 0; stopped = true; resolve(bytes.buffer);
    });
    stream.resume();
  });

export const loadProject = async (file: File): Promise<LoadedProject | null> => {
  // Every object URL minted on the way in, so a refusal releases them all. The
  // archive branch used to `return null` from its catch with every URL it had
  // minted still live — a whole pool of full-resolution bytes pinned for the
  // page's life, stranded at the worst possible moment (a failed restore during
  // OOM recovery). `loadFromSVG` below always did this; this branch did not.
  const minted: string[] = [];
  const releaseMinted = () => { for (const u of minted) { try { URL.revokeObjectURL(u); } catch { /* already gone */ } } };
  try {
    // Check if it's an SVG (Smart SVG)
    if (file.type === 'image/svg+xml' || file.name.endsWith('.svg')) {
       return await loadFromSVG(file);
    }

    const zip = await JSZip.loadAsync(file);
    const manifestFile = zip.file("manifest.json");
    if (!manifestFile) throw new Error("Invalid project file: missing manifest");
    
    const manifestStr = await manifestFile.async("text");
    const candidate: unknown = JSON.parse(manifestStr);
    assertProjectState(candidate);
    const manifest: any = candidate; // relaxed image metadata for legacy compat
    // Validate timed text before any source is decoded or any editor state is
    // replaced. A malformed track must refuse the file as a whole, not throw
    // later from the render after its photographs have already been adopted.
    if (manifest.captions !== undefined) manifest.captions = normalizeCaptionTrack(manifest.captions);
    // Preflight the ENTIRE pool before any source URL is minted. A bad final
    // recipe must not leave earlier images adopted, decoded or stranded.
    if (!Array.isArray(manifest.images)) throw new Error('Invalid project image list');
    for (const meta of manifest.images) {
      if (!meta || typeof meta !== 'object') throw new Error('Invalid project image entry');
      if (meta.art !== undefined) meta.art = normalizeArtRecipe(meta.art);
    }
    
    const soundtrackMeta = normalizeProjectSoundtrack(manifest.soundtrack);
    let soundtrackBlob: Blob | null = null;
    if (soundtrackMeta) {
      const member = zip.file(PROJECT_SOUNDTRACK_PATH);
      if (!member) throw new Error('The project is missing its soundtrack original.');
      const bytes = await readSoundtrackBytes(member, soundtrackMeta.sizeBytes);
      await verifyProjectSoundtrackBytes(soundtrackMeta, bytes);
      soundtrackBlob = new Blob([bytes], { type: soundtrackMeta.mimeType });
    }

    const images: ImageAsset[] = [];
    const imgFolder = zip.folder("images");
    const previewFolder = zip.folder("previews");
    const prepared: { meta: any; original: Blob; preview: Blob | null }[] = [];

    // Read every required member before minting any URL. A missing late image
    // or a corrupt soundtrack cannot leave a partly adopted candidate behind.
    if (imgFolder) {
      for (const meta of manifest.images) {
        // Fallback for legacy files that used 'filename' instead of 'storageFilename'
        const fname = meta.storageFilename || meta.filename;
        const file = imgFolder.file(fname);
        // FAIL CLOSED ON A MANIFEST ENTRY WITH NO MEMBER. This used to be a bare
        // `if (file)` that silently dropped the entry and returned a SHORT pool —
        // the exact thing `loadFromSVG` and the session path both refuse, and for
        // the reason they both state: `arrangeBag` deals from the pool's order and
        // length, so one missing source re-deals every fragment after it. Worse,
        // if EVERY member were missing the pool came back empty, the caller
        // treated that as success, the restore banner was never dismissed, and
        // the offer came straight back — the reported endless loop, on this exact
        // branch. A visible refusal beats a plausible picture that is not theirs.
        if (!file) throw new Error(`archive is missing ${fname}`);
        const original = await file.async('blob');
        if (!original.size) throw new Error(`archive source is empty: ${fname}`);
        let preview: Blob | null = null;
        const pf = previewFolder?.file(fname);
        if (pf) { try { const blob = await pf.async('blob'); if (blob.size) preview = blob; } catch { /* original remains usable */ } }
        prepared.push({ meta, original, preview });
      }
    }

    for (const { meta, original, preview } of prepared) {
          const url = URL.createObjectURL(original);
          minted.push(url);

          const { w, h } = await measureSource(url, meta);
          // A source that will not decode has no size, and an asset with no size
          // is not a picture: `handleUpload` rejects exactly this on the way in
          // (`if(!img.width) return null`), and letting one through here meant a
          // permanent hole in the collage AND — once the session store copied the
          // manifest forward — a zero-sized entry that restored blank on every
          // future launch. Same rule on both doors.
          if (!w || !h) throw new Error(`undecodable source for ${meta.id}`);

          // THE THUMBNAIL TIER, when the archive carries one. Archives written
          // before 2026-08-09 have no `previews/`, so `previewSrc` aliases the
          // original exactly as it always did — but every archive written from
          // now on reopens with the small tier the preview path expects, instead
          // of quietly re-decoding full-resolution photographs on every drag.
          let previewUrl = url;
          if (preview) {
            try { previewUrl = URL.createObjectURL(preview); minted.push(previewUrl); } catch { previewUrl = url; }
          }

          images.push({
            id: meta.id,
            src: url,
            // REQUIRED. Without it every loaded asset carries previewSrc
            // undefined, and stencil.ts does `img.src = imgAsset.previewSrc`,
            // which stringifies to "undefined", resolves to <base>/undefined
            // and 404s. Aliases `src` when the archive has no preview for it.
            previewSrc: previewUrl,
            originalName: meta.originalName || meta.filename,
            width: w,
            height: h,
            analysis: meta.analysis,
            ...(meta.art === undefined ? {} : { art: meta.art }),
          });
    }

    // Audio is last: all image metadata, required bytes and necessary legacy
    // decodes must have passed. No settings or editor state are adopted here.
    let soundtrack: SoundtrackSpec | null = null;
    if (soundtrackMeta && soundtrackBlob) {
      const url = URL.createObjectURL(soundtrackBlob);
      minted.push(url);
      soundtrack = restoreProjectSoundtrack(soundtrackMeta, url);
    }
    
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { images: _ignore, soundtrack: _soundtrack, ...state } = manifest;
    // Handed to the caller — the app owns these URLs for the rest of the session.
    minted.length = 0;
    return { state, images, soundtrack };

  } catch (e) {
    // Nothing partial escapes, and nothing leaks.
    releaseMinted();
    console.error("Failed to load project", e);
    return null;
  }
};

/**
 * THE POST — open an exported SVG as the project it is.
 *
 * This used to `return null` under thirty lines of deliberation about whether
 * the pictures would be recoverable, ending on "vectorExport MUST convert images
 * to Base64… I need to fix vectorExport". That fix shipped; the TODO waiting on
 * it never heard. So the file input has advertised `.svg` — and the Open button
 * has said "or an exported SVG layout" — for as long as neither could work.
 *
 * The pictures are the `<image>` elements' own data URIs, matched to the pool by
 * `data-src-id`; the settings are the `<metadata>` manifest. See `svgProject.ts`
 * for both, and for why the manifest is no longer an XML comment.
 *
 * FAILS CLOSED, on purpose. A pool that comes back short or reordered does not
 * produce a slightly-wrong collage — `arrangeBag` deals from the pool's order
 * and length, so one missing source re-deals every fragment after it. A refusal
 * the user can act on beats a plausible picture that is not theirs.
 */
const loadFromSVG = async (file: File): Promise<LoadedProject | null> => {
  const minted: string[] = [];
  try {
    const text = await file.text();

    const project = readProject(text);
    // No manifest of ours: either not a Collage Studio export, or one made
    // before the SVG could carry image identity. Neither can be reopened.
    if (!project) return null;
    assertProjectState(project.state);
    if (project.state.captions !== undefined) {
      project.state.captions = normalizeCaptionTrack(project.state.captions);
    }

    const sources = readImageSources(text);
    const images: ImageAsset[] = [];

    for (const meta of project.images) {
      const href = sources.get(meta.id);
      if (!href) throw new Error(`no embedded source for ${meta.id}`);

      // data: -> Blob -> object URL. The rest of the app (the export worker's
      // postMessage, stencil.ts, the Stage's decode cache) already handles an
      // object URL everywhere, and a multi-megabyte data URI re-decoded on every
      // read is the same picture at a worse price.
      const blob = await (await fetch(href)).blob();
      const url = URL.createObjectURL(blob);
      minted.push(url);

      const el = new Image();
      el.src = url;
      await new Promise<void>((r) => { el.onload = () => r(); el.onerror = () => r(); });
      if (!el.naturalWidth) throw new Error(`undecodable source for ${meta.id}`);

      images.push({
        id: meta.id,
        src: url,
        // Same reason as the archive branch above: one image per asset, so the
        // full image IS the preview.
        previewSrc: url,
        originalName: meta.originalName,
        width: el.naturalWidth,
        height: el.naturalHeight,
        analysis: meta.analysis,
        ...(meta.art === undefined ? {} : { art: meta.art }),
      });
    }

    return { state: project.state, images };
  } catch (e) {
    // Nothing partial escapes, and nothing leaks: every URL minted on the way to
    // a failure is released here.
    for (const u of minted) { try { URL.revokeObjectURL(u); } catch { /* already gone */ } }
    console.error('Failed to open SVG project', e);
    return null;
  }
};
