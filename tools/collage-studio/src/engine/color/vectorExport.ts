// src/engine/color/vectorExport.ts
import { LayoutItem, createRng } from '../../lib/layout';
import { ImageAsset, AppState } from '../../types';
import { calculateSmartCrop, renderArtSource } from '../../lib/renderer';
import { TitlePlan, titlePlanFor, titlePlanToSvg } from '../../lib/title';
import { svgFilterFor, svgFilterAttrFor, type LookRef } from '../../lib/grade';
import { projectMetadata, metaForAsset, srcIdAttr } from '../../lib/svgProject';

const blobToBase64 = async (url: string): Promise<string> => {
  try {
    const response = await fetch(url);
    const blob = await response.blob();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.readAsDataURL(blob);
    });
  } catch (e) {
    console.error("Failed to convert blob", e);
    return "";
  }
};

export const generateVectorExport = async (
  width: number,
  aspect: number,
  mode: string,
  layoutItems: LayoutItem[],
  orderedImages: (ImageAsset | null)[],
  seed: number,
  fullState?: AppState,
  zoom: number = 1.0,
  bgColor: string = '#050505',
  /** THE TITLE, planned once at `TITLE_BASIS` by the caller. Null emits nothing. */
  titlePlan: TitlePlan | null = null,
  /** THE LOOK — the colour grade, as real `<filter>` primitives. */
  look: LookRef | null = null,
  /**
   * THE SOURCE POOL, in POOL ORDER — what makes this file a project rather than
   * a picture. `orderedImages` above is the DRAWN permutation with the crop
   * focus and the twist already baked into each `analysis`; those are derived
   * per-slot from `focus`/`twist`/`seed` and must be re-derived on open, not
   * restored. So the manifest carries the pool's own untouched analyses, and
   * `arrangeBag` gets back the exact list — same members, same order, same
   * length — that produced this collage.
   */
  sourcePool: ImageAsset[] = [],
): Promise<string> => {
  const height = width / aspect;

  let svg = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="${width}px" height="${height}px" viewBox="0 0 ${width} ${height}" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <desc>Smart Crop GenArt Export</desc>
${projectMetadata(fullState ?? null, sourcePool.map(metaForAsset))}  <defs>
`;

  layoutItems.forEach((item, i) => {
    const pathData = item.path.map((p, idx) => `${idx===0?'M':'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ') + ' Z';
    svg += `    <clipPath id="clip-${i}">
      <path d="${pathData}" />
    </clipPath>
`;
  });

  // THE LOOK — real filter primitives, in the pipeline order `lib/grade.ts`
  // fixes, carrying `color-interpolation-filters="sRGB"` because SVG defaults
  // to linear light and the canvas paths evaluate the identical functions in
  // sRGB.
  //
  // Appended only when there IS one, rather than interpolated as a
  // possibly-empty line: an ungraded export has to be BYTE-identical to what
  // this function produced before the feature existed, and an empty
  // interpolation still emits its own indentation and newline. That is a
  // difference no eye would catch and every diff would.
  const lookFilter = svgFilterFor(look);
  if (lookFilter) svg += `    ${lookFilter}\n`;

  svg += `  </defs>
  
  <rect width="100%" height="100%" fill="${bgColor}" />
  
  <g id="CollageLayer"${svgFilterAttrFor(look)}>
`;

  /** Which pool ids already have their bytes in the file. Drawn twice = written
   *  once as far as the READER is concerned; the undrawn sweep below reads it. */
  const embedded = new Set<string>();
  const artData = new Map<string, string>();
  const sourceData = async (asset: ImageAsset): Promise<string> => {
    if (!asset.art) return blobToBase64(asset.src ?? '');
    const key = asset.src || asset.id;
    const found = artData.get(key);
    if (found) return found;
    const source = renderArtSource(asset.art, Math.max(width, width / aspect));
    try {
      const png = source.toDataURL('image/png');
      if (!png.startsWith('data:image/png;')) throw new Error('Could not encode native artwork.');
      artData.set(key, png); return png;
    } finally { source.width = 0; source.height = 0; }
  };

  for (let i = 0; i < layoutItems.length; i++) {
    const item = layoutItems[i];
    const imgData = orderedImages[i];
    if (!imgData) continue;

    const crop = calculateSmartCrop(item.bounds, {
        width: imgData.width, 
        height: imgData.height, 
        analysis: imgData.analysis
    }, zoom);

    const scale = crop.dw / crop.sw;
    const tx = crop.dx - (crop.sx * scale);
    const ty = crop.dy - (crop.sy * scale);
    const finalW = imgData.width * scale;
    const finalH = imgData.height * scale;

    const base64 = await sourceData(imgData);

    // TWIST — a NESTED group, deliberately. Putting the rotation on the same
    // element that carries `clip-path` would rotate the clip along with the
    // picture and the fragments would stop tiling; the outer group holds the
    // clip in unrotated user space, the inner one turns only the <image>. SVG's
    // rotate() is degrees, clockwise, y-down — the same sense as ctx.rotate().
    const spin = crop.twist
      ? ` transform="rotate(${((crop.twist * 180) / Math.PI).toFixed(3)} ${crop.tcx.toFixed(2)} ${crop.tcy.toFixed(2)})"`
      : '';

    // `data-src-id` names WHICH source this is, so reopening the file can put
    // the pool back in its own order instead of guessing from position. It is an
    // annotation only: no renderer reads it and the drawn geometry is untouched.
    if (imgData.id) embedded.add(imgData.id);

    svg += `    <g clip-path="url(#clip-${i})">
      <g${spin}>
        <image${srcIdAttr(imgData.id)}
          xlink:href="${base64}"
          x="${tx.toFixed(2)}"
          y="${ty.toFixed(2)}"
          width="${finalW.toFixed(2)}"
          height="${finalH.toFixed(2)}"
          preserveAspectRatio="none"
        />
      </g>
    </g>
`;
  }

  if (mode === 'complex') {
     svg += `  <g id="CutLines" stroke="magenta" stroke-width="0.5" fill="none">
`;
     layoutItems.forEach((item) => {
        const pathData = item.path.map((p, idx) => `${idx===0?'M':'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ') + ' Z';
        svg += `    <path d="${pathData}" />
`;
     });
     svg += `  </g>
`;
  }

  svg += `  </g>
`;

  // THE POOL'S UNDRAWN MEMBERS.
  //
  // A collage can hold fewer fragments than the project holds photographs, and
  // `arrangeBag` deals from the pool's LENGTH as well as its order — so a file
  // that carried only the pictures it happens to show would reopen as a
  // different pairing of the same photographs. That is the plausible-looking
  // wrong answer this repo has scarred before, so the rest of the pool goes in
  // too, inside <defs>: referenced by nothing, rendered by nothing, byte for
  // byte invisible in the picture. Costs nothing in the ordinary case, because
  // the app derives the fragment count from the number of sources until
  // somebody takes it over.
  const undrawn = sourcePool.filter((a) => a && a.id && !embedded.has(a.id));
  if (undrawn.length > 0) {
    svg += `  <defs id="collage-sources">
`;
    for (const a of undrawn) {
      const b64 = await sourceData(a);
      if (!b64) continue;
      svg += `    <image${srcIdAttr(a.id)} xlink:href="${b64}" width="1" height="1" />
`;
    }
    svg += `  </defs>
`;
  }

  // THE TITLE — real <text>, not an outline, so it stays selectable, editable
  // and re-typeable in whatever the SVG is opened in. Same plan, same wrap, same
  // basis as every raster path; only the scale differs.
  svg += titlePlanToSvg(titlePlanFor(titlePlan, width));

  svg += `</svg>`;

  return svg;
};
