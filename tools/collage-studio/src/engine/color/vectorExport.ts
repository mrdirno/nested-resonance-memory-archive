// src/engine/color/vectorExport.ts
import { LayoutItem, createRng } from '../../lib/layout';
import { ImageAsset, AppState } from '../../types';
import { calculateSmartCrop } from '../../lib/renderer';

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
  bgColor: string = '#050505'
): Promise<string> => {
  const height = width / aspect;

  let metadataComment = '';
  if (fullState) {
      const slimState = { ...fullState };
      metadataComment = `<!-- JSON_MANIFEST: ${JSON.stringify(slimState)} -->`;
  }

  let svg = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
${metadataComment}
<svg width="${width}px" height="${height}px" viewBox="0 0 ${width} ${height}" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <desc>Smart Crop GenArt Export</desc>
  <defs>
`;

  layoutItems.forEach((item, i) => {
    const pathData = item.path.map((p, idx) => `${idx===0?'M':'L'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ') + ' Z';
    svg += `    <clipPath id="clip-${i}">
      <path d="${pathData}" />
    </clipPath>
`;
  });

  svg += `  </defs>
  
  <rect width="100%" height="100%" fill="${bgColor}" />
  
  <g id="CollageLayer">
`;

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

    const base64 = await blobToBase64(imgData.src);

    // TWIST — a NESTED group, deliberately. Putting the rotation on the same
    // element that carries `clip-path` would rotate the clip along with the
    // picture and the fragments would stop tiling; the outer group holds the
    // clip in unrotated user space, the inner one turns only the <image>. SVG's
    // rotate() is degrees, clockwise, y-down — the same sense as ctx.rotate().
    const spin = crop.twist
      ? ` transform="rotate(${((crop.twist * 180) / Math.PI).toFixed(3)} ${crop.tcx.toFixed(2)} ${crop.tcy.toFixed(2)})"`
      : '';

    svg += `    <g clip-path="url(#clip-${i})">
      <g${spin}>
        <image
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
</svg>`;

  return svg;
};
