import JSZip from 'jszip';
import { AppState, ImageAsset, ProjectManifest } from '../types';
import { readProject, readImageSources } from './svgProject';

export const saveProject = async (state: AppState, images: ImageAsset[]) => {
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
      analysis: img.analysis
    };
  });

  const manifest: ProjectManifest = {
    ...state,
    images: imageMeta
  };
  
  zip.file("manifest.json", JSON.stringify(manifest, null, 2));
  
  // 2. Images
  const imgFolder = zip.folder("images");
  if (imgFolder) {
    for (let i = 0; i < images.length; i++) {
      const img = images[i];
      const meta = imageMeta[i];
      try {
        const response = await fetch(img.src);
        const blob = await response.blob();
        imgFolder.file(meta.storageFilename, blob);
      } catch (e) {
        console.warn(`Failed to save image ${img.id}`, e);
      }
    }
  }
  
  // 3. Generate
  const content = await zip.generateAsync({type:"blob"});
  
  // 4. Download
  const url = URL.createObjectURL(content);
  const a = document.createElement('a');
  a.href = url;
  a.download = `project-${Date.now()}.collage`;
  a.click();
  URL.revokeObjectURL(url);
};

export const loadProject = async (file: File): Promise<{state: AppState, images: ImageAsset[]} | null> => {
  try {
    // Check if it's an SVG (Smart SVG)
    if (file.type === 'image/svg+xml' || file.name.endsWith('.svg')) {
       return await loadFromSVG(file);
    }

    const zip = await JSZip.loadAsync(file);
    const manifestFile = zip.file("manifest.json");
    if (!manifestFile) throw new Error("Invalid project file: missing manifest");
    
    const manifestStr = await manifestFile.async("text");
    const manifest: any = JSON.parse(manifestStr); // relaxed type for compat
    
    const images: ImageAsset[] = [];
    const imgFolder = zip.folder("images");
    
    if (imgFolder) {
      for (const meta of manifest.images) {
        // Fallback for legacy files that used 'filename' instead of 'storageFilename'
        const fname = meta.storageFilename || meta.filename;
        const file = imgFolder.file(fname);
        if (file) {
          const blob = await file.async("blob");
          const url = URL.createObjectURL(blob);
          
          const imgElem = new Image();
          imgElem.src = url;
          await new Promise(r => imgElem.onload = r);
          
          images.push({
            id: meta.id,
            src: url,
            // REQUIRED. Without it every loaded asset carries previewSrc
            // undefined, and stencil.ts does `img.src = imgAsset.previewSrc`,
            // which stringifies to "undefined", resolves to <base>/undefined
            // and 404s. The archive stores one image per asset, so the full
            // image IS the preview here.
            previewSrc: url,
            originalName: meta.originalName || meta.filename,
            width: imgElem.width,
            height: imgElem.height,
            analysis: meta.analysis
          });
        }
      }
    }
    
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { images: _ignore, ...state } = manifest;
    return { state, images };
    
  } catch (e) {
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
const loadFromSVG = async (file: File): Promise<{state: AppState, images: ImageAsset[]} | null> => {
  const minted: string[] = [];
  try {
    const text = await file.text();

    const project = readProject(text);
    // No manifest of ours: either not a Collage Studio export, or one made
    // before the SVG could carry image identity. Neither can be reopened.
    if (!project) return null;

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