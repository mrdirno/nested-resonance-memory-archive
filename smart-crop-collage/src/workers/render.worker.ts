/**
 * RENDER WORKER
 * Section 18.2: Compute Sharing
 *
 * Offloads heavy rendering to a dedicated Web Worker.
 * Uses OffscreenCanvas when available.
 */

// Check for OffscreenCanvas support
const hasOffscreenCanvas = typeof OffscreenCanvas !== 'undefined';

// ============================================================================
// MESSAGE HANDLER
// ============================================================================

self.onmessage = async (event: MessageEvent) => {
  const { type, id, payload } = event.data;

  try {
    switch (type) {
      case 'RENDER_TILE':
        await handleRenderTile(id, payload);
        break;

      case 'COMPUTE_LAYOUT':
        handleComputeLayout(id, payload);
        break;

      case 'ANALYZE_IMAGE':
        await handleAnalyzeImage(id, payload);
        break;

      case 'ENCODE_IMAGE':
        await handleEncodeImage(id, payload);
        break;

      default:
        postMessage({ type: 'ERROR', id, error: `Unknown message type: ${type}` });
    }
  } catch (error) {
    postMessage({
      type: 'ERROR',
      id,
      error: error instanceof Error ? error.message : String(error),
    });
  }
};

// ============================================================================
// TILE RENDERING
// ============================================================================

interface RenderTilePayload {
  tileWidth: number;
  tileHeight: number;
  offsetX: number;
  offsetY: number;
  layoutItems: any[];
  images: ImageBitmap[];
  backgroundColor: string;
}

async function handleRenderTile(id: string, payload: RenderTilePayload) {
  const { tileWidth, tileHeight, offsetX, offsetY, layoutItems, images, backgroundColor } = payload;

  if (!hasOffscreenCanvas) {
    postMessage({ type: 'ERROR', id, error: 'OffscreenCanvas not supported' });
    return;
  }

  const canvas = new OffscreenCanvas(tileWidth, tileHeight);
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    postMessage({ type: 'ERROR', id, error: 'Failed to get 2D context' });
    return;
  }

  // Fill background
  ctx.fillStyle = backgroundColor;
  ctx.fillRect(0, 0, tileWidth, tileHeight);

  // Render each cell that intersects this tile
  for (let i = 0; i < layoutItems.length; i++) {
    const item = layoutItems[i];
    const img = images[i % images.length];

    if (!img) continue;

    // Check if cell intersects tile
    const cellBounds = item.bounds;
    const intersects =
      cellBounds.x < offsetX + tileWidth &&
      cellBounds.x + cellBounds.w > offsetX &&
      cellBounds.y < offsetY + tileHeight &&
      cellBounds.y + cellBounds.h > offsetY;

    if (!intersects) continue;

    // Translate coordinates to tile space
    ctx.save();
    ctx.translate(-offsetX, -offsetY);

    // Clip to cell path
    ctx.beginPath();
    item.path.forEach((p: { x: number; y: number }, idx: number) => {
      if (idx === 0) ctx.moveTo(p.x, p.y);
      else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    ctx.clip();

    // Calculate smart crop (simplified)
    const boxAsp = cellBounds.w / cellBounds.h;
    const imgAsp = img.width / img.height;

    let sx, sy, sw, sh;
    if (imgAsp > boxAsp) {
      sh = img.height;
      sw = sh * boxAsp;
      sy = 0;
      sx = (img.width - sw) / 2;
    } else {
      sw = img.width;
      sh = sw / boxAsp;
      sx = 0;
      sy = (img.height - sh) / 2;
    }

    ctx.drawImage(img, sx, sy, sw, sh, cellBounds.x, cellBounds.y, cellBounds.w, cellBounds.h);
    ctx.restore();
  }

  // Convert to blob
  const blob = await canvas.convertToBlob({ type: 'image/png' });
  const bitmap = await createImageBitmap(blob);

  postMessage(
    { type: 'TILE_COMPLETE', id, bitmap },
    { transfer: [bitmap] }
  );
}

// ============================================================================
// LAYOUT COMPUTATION
// ============================================================================

interface ComputeLayoutPayload {
  width: number;
  height: number;
  count: number;
  seed: number;
  mode: 'minimal' | 'balanced' | 'complex';
  gutter: number;
}

function handleComputeLayout(id: string, payload: ComputeLayoutPayload) {
  const { width, height, count, seed, mode, gutter } = payload;

  const createRng = (s: number) => {
    let t = s + 0x6D2B79F5;
    return () => {
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  const rng = createRng(seed);
  const gap = Math.max(2, width * gutter);

  let result;

  if (mode === 'minimal') {
    let nodes = [{ x: 0, y: 0, w: width, h: height }];
    let safety = 0;

    while (nodes.length < count && safety < 1000) {
      safety++;
      let idx = -1, maxScore = -1;

      for (let i = 0; i < nodes.length; i++) {
        const score = nodes[i].w * nodes[i].h * (0.8 + rng() * 0.4);
        if (score > maxScore) { maxScore = score; idx = i; }
      }

      if (idx === -1) break;

      const p = nodes[idx];
      nodes.splice(idx, 1);

      const isVert = p.w > p.h;
      const splitBase = 0.382 + rng() * 0.236;

      if (isVert) {
        const w1 = p.w * splitBase;
        nodes.push(
          { x: p.x, y: p.y, w: w1, h: p.h },
          { x: p.x + w1, y: p.y, w: p.w - w1, h: p.h }
        );
      } else {
        const h1 = p.h * splitBase;
        nodes.push(
          { x: p.x, y: p.y, w: p.w, h: h1 },
          { x: p.x, y: p.y + h1, w: p.w, h: p.h - h1 }
        );
      }
    }

    result = nodes.map((n, i) => ({
      id: `cell-${i}`,
      path: [
        { x: n.x + gap, y: n.y + gap },
        { x: n.x + n.w - gap, y: n.y + gap },
        { x: n.x + n.w - gap, y: n.y + n.h - gap },
        { x: n.x + gap, y: n.y + n.h - gap },
      ],
      bounds: { x: n.x + gap, y: n.y + gap, w: n.w - gap * 2, h: n.h - gap * 2 },
    }));
  } else if (mode === 'balanced') {
    // Balanced grid with jitter
    const idealAsp = width / height;
    const cols = Math.max(2, Math.ceil(Math.sqrt(count * idealAsp)));
    const rows = Math.max(2, Math.ceil(count / cols));
    const cw = width / cols, ch = height / rows;

    const verts: { x: number; y: number }[][] = [];
    for (let r = 0; r <= rows; r++) {
      const row: { x: number; y: number }[] = [];
      for (let col = 0; col <= cols; col++) {
        let x = col * cw, y = r * ch;
        if (r > 0 && r < rows && col > 0 && col < cols) {
          x += (rng() - 0.5) * cw * 0.5;
          y += (rng() - 0.5) * ch * 0.5;
        }
        row.push({ x, y });
      }
      verts.push(row);
    }

    const items = [];
    let cellIdx = 0;
    for (let r = 0; r < rows; r++) {
      for (let col = 0; col < cols; col++) {
        const p1 = verts[r][col], p2 = verts[r][col + 1];
        const p3 = verts[r + 1][col + 1], p4 = verts[r + 1][col];

        const cx = (p1.x + p2.x + p3.x + p4.x) / 4;
        const cy = (p1.y + p2.y + p3.y + p4.y) / 4;
        const shrink = 1.0 - gutter * 4;

        const pathPoints = [p1, p2, p3, p4].map((p) => ({
          x: cx + (p.x - cx) * shrink,
          y: cy + (p.y - cy) * shrink,
        }));

        const xs = pathPoints.map((p) => p.x);
        const ys = pathPoints.map((p) => p.y);
        const bx = Math.min(...xs), by = Math.min(...ys);

        items.push({
          id: `cell-${cellIdx++}`,
          path: pathPoints,
          bounds: { x: bx, y: by, w: Math.max(...xs) - bx, h: Math.max(...ys) - by },
        });
      }
    }
    result = items.slice(0, count);
  } else {
    // Complex (Voronoi-ish)
    let polys = [[{ x: 0, y: 0 }, { x: width, y: 0 }, { x: width, y: height }, { x: 0, y: height }]];
    let s = 0;

    while (polys.length < count && s < 1000) {
      s++;
      const idx = Math.floor(rng() * polys.length);
      const poly = polys[idx];

      const xs = poly.map((p) => p.x), ys = poly.map((p) => p.y);
      const minX = Math.min(...xs), maxX = Math.max(...xs);
      const minY = Math.min(...ys), maxY = Math.max(...ys);

      const cx = minX + rng() * (maxX - minX);
      const cy = minY + rng() * (maxY - minY);
      const angle = rng() * Math.PI * 2;
      const dx = Math.cos(angle), dy = Math.sin(angle);

      const pA: { x: number; y: number }[] = [], pB: { x: number; y: number }[] = [];

      for (let i = 0; i < poly.length; i++) {
        const p1 = poly[i];
        const p2 = poly[(i + 1) % poly.length];
        const v1 = (p1.x - cx) * -dy + (p1.y - cy) * dx;
        const v2 = (p2.x - cx) * -dy + (p2.y - cy) * dx;

        if (v1 >= 0) pA.push(p1);
        else pB.push(p1);

        if ((v1 >= 0 && v2 < 0) || (v1 < 0 && v2 >= 0)) {
          const t = v1 / (v1 - v2);
          const mid = { x: p1.x + t * (p2.x - p1.x), y: p1.y + t * (p2.y - p1.y) };
          pA.push(mid);
          pB.push(mid);
        }
      }

      if (pA.length > 2 && pB.length > 2) {
        polys.splice(idx, 1, pA, pB);
      }
    }

    result = polys.map((poly, i) => {
      let sx = 0, sy = 0;
      poly.forEach((p) => { sx += p.x; sy += p.y; });
      const cx = sx / poly.length, cy = sy / poly.length;
      const shrink = 1.0 - gutter * 4;

      const pathPoints = poly.map((p) => ({
        x: cx + (p.x - cx) * shrink,
        y: cy + (p.y - cy) * shrink,
      }));

      const xs = pathPoints.map((p) => p.x), ys = pathPoints.map((p) => p.y);
      const bx = Math.min(...xs), by = Math.min(...ys);

      return {
        id: `cell-${i}`,
        path: pathPoints,
        bounds: { x: bx, y: by, w: Math.max(...xs) - bx, h: Math.max(...ys) - by },
      };
    });
  }

  postMessage({ type: 'LAYOUT_COMPLETE', id, result });
}

// ============================================================================
// IMAGE ANALYSIS
// ============================================================================

interface AnalyzeImagePayload {
  bitmap: ImageBitmap;
}

async function handleAnalyzeImage(id: string, payload: AnalyzeImagePayload) {
  const { bitmap } = payload;

  if (!hasOffscreenCanvas) {
    postMessage({ type: 'ANALYSIS_COMPLETE', id, result: { x: 0.5, y: 0.5 } });
    return;
  }

  const canvas = new OffscreenCanvas(128, 128);
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    postMessage({ type: 'ANALYSIS_COMPLETE', id, result: { x: 0.5, y: 0.5 } });
    return;
  }

  // Resize for analysis
  const scale = Math.min(128 / bitmap.width, 128 / bitmap.height);
  const w = Math.floor(bitmap.width * scale);
  const h = Math.floor(bitmap.height * scale);

  ctx.drawImage(bitmap, 0, 0, w, h);

  const imageData = ctx.getImageData(0, 0, w, h);
  const data = imageData.data;

  let totalX = 0, totalY = 0, totalE = 0;

  for (let y = 0; y < h; y += 4) {
    for (let x = 0; x < w; x += 4) {
      const i = (y * w + x) * 4;
      const r = data[i], g = data[i + 1], b = data[i + 2];
      const bri = (r + g + b) / 3;

      const nextI = i + 16;
      const nextBri = x < w - 4 ? (data[nextI] + data[nextI + 1] + data[nextI + 2]) / 3 : bri;
      let energy = Math.abs(bri - nextBri);

      const maxC = Math.max(r, g, b);
      const minC = Math.min(r, g, b);
      if (maxC - minC > 40) energy *= 1.5;

      const dx = x - w / 2, dy = y - h / 2;
      const dist = Math.sqrt(dx * dx + dy * dy) / (w / 1.5);
      energy *= 1.2 - Math.min(1, dist);

      totalX += x * energy;
      totalY += y * energy;
      totalE += energy;
    }
  }

  const result = totalE > 0 ? { x: totalX / totalE / w, y: totalY / totalE / h } : { x: 0.5, y: 0.5 };

  postMessage({ type: 'ANALYSIS_COMPLETE', id, result });
}

// ============================================================================
// IMAGE ENCODING
// ============================================================================

interface EncodeImagePayload {
  bitmap: ImageBitmap;
  format: 'jpeg' | 'png' | 'webp';
  quality: number;
}

async function handleEncodeImage(id: string, payload: EncodeImagePayload) {
  const { bitmap, format, quality } = payload;

  if (!hasOffscreenCanvas) {
    postMessage({ type: 'ERROR', id, error: 'OffscreenCanvas not supported' });
    return;
  }

  const canvas = new OffscreenCanvas(bitmap.width, bitmap.height);
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    postMessage({ type: 'ERROR', id, error: 'Failed to get 2D context' });
    return;
  }

  ctx.drawImage(bitmap, 0, 0);

  const mimeType = `image/${format}`;
  const blob = await canvas.convertToBlob({ type: mimeType, quality });

  postMessage(
    { type: 'ENCODE_COMPLETE', id, blob },
    { transfer: [] }
  );
}

// Log startup
console.log('[RenderWorker] Initialized', { hasOffscreenCanvas });
