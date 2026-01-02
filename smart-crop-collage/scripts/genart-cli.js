#!/usr/bin/env node

/**
 * GENART CLI - Headless Collage Generator
 * Section 16.2: Headless Mode
 *
 * Usage:
 *   node scripts/genart-cli.js --source ./images --count 100 --out ./output
 *   node scripts/genart-cli.js -s ./photos -c 10 -o ./collages --mode balanced --aspect 1.5
 *
 * Requirements:
 *   npm install canvas sharp commander
 */

const fs = require('fs');
const path = require('path');
const { program } = require('commander');

// Check for required dependencies
let createCanvas, loadImage, sharp;
try {
  const canvasModule = require('canvas');
  createCanvas = canvasModule.createCanvas;
  loadImage = canvasModule.loadImage;
} catch {
  console.error('ERROR: Missing dependency. Run: npm install canvas');
  console.error('       On macOS: brew install pkg-config cairo pango libpng jpeg giflib librsvg');
  process.exit(1);
}

try {
  sharp = require('sharp');
} catch {
  console.warn('WARNING: sharp not installed. Image analysis will be limited.');
  sharp = null;
}

// ============================================================================
// LAYOUT ENGINE (Ported from TypeScript)
// ============================================================================

const createRng = (s) => {
  let t = s + 0x6D2B79F5;
  return () => {
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

const computeLayout = (W, H, count, rng, mode, gutterPercent = 0.005) => {
  const gap = Math.max(2, W * gutterPercent);

  if (mode === 'minimal') {
    let nodes = [{ x: 0, y: 0, w: W, h: H }];
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
      const splitBase = 0.382 + (rng() * 0.236);

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

    return nodes.map((n, i) => ({
      id: `cell-${i}`,
      path: [
        { x: n.x + gap, y: n.y + gap },
        { x: n.x + n.w - gap, y: n.y + gap },
        { x: n.x + n.w - gap, y: n.y + n.h - gap },
        { x: n.x + gap, y: n.y + n.h - gap }
      ],
      bounds: { x: n.x + gap, y: n.y + gap, w: n.w - gap * 2, h: n.h - gap * 2 }
    }));
  }

  if (mode === 'balanced') {
    const idealAsp = W / H;
    const cols = Math.max(2, Math.ceil(Math.sqrt(count * idealAsp)));
    const rows = Math.max(2, Math.ceil(count / cols));
    const cw = W / cols, ch = H / rows;

    const verts = [];
    for (let r = 0; r <= rows; r++) {
      const row = [];
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
        const shrink = 1.0 - (gutterPercent * 4);

        const pathPoints = [p1, p2, p3, p4].map(p => ({
          x: cx + (p.x - cx) * shrink,
          y: cy + (p.y - cy) * shrink
        }));

        const xs = pathPoints.map(p => p.x);
        const ys = pathPoints.map(p => p.y);
        const bx = Math.min(...xs), by = Math.min(...ys);

        items.push({
          id: `cell-${cellIdx++}`,
          path: pathPoints,
          bounds: { x: bx, y: by, w: Math.max(...xs) - bx, h: Math.max(...ys) - by }
        });
      }
    }
    return items.slice(0, count);
  }

  // Complex mode (Voronoi-ish)
  let polys = [[{ x: 0, y: 0 }, { x: W, y: 0 }, { x: W, y: H }, { x: 0, y: H }]];
  let s = 0;
  while (polys.length < count && s < 1000) {
    s++;
    const idx = Math.floor(rng() * polys.length);
    const poly = polys[idx];

    const xs = poly.map(p => p.x), ys = poly.map(p => p.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);

    const cx = minX + rng() * (maxX - minX);
    const cy = minY + rng() * (maxY - minY);
    const angle = rng() * Math.PI * 2;
    const dx = Math.cos(angle), dy = Math.sin(angle);

    const pA = [], pB = [];
    for (let i = 0; i < poly.length; i++) {
      const p1 = poly[i];
      const p2 = poly[(i + 1) % poly.length];
      const v1 = (p1.x - cx) * (-dy) + (p1.y - cy) * dx;
      const v2 = (p2.x - cx) * (-dy) + (p2.y - cy) * dx;

      if (v1 >= 0) pA.push(p1); else pB.push(p1);

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

  return polys.map((poly, i) => {
    let sx = 0, sy = 0;
    poly.forEach(p => { sx += p.x; sy += p.y; });
    const cx = sx / poly.length, cy = sy / poly.length;
    const shrink = 1.0 - (gutterPercent * 4);

    const pathPoints = poly.map(p => ({
      x: cx + (p.x - cx) * shrink,
      y: cy + (p.y - cy) * shrink
    }));

    const xs = pathPoints.map(p => p.x), ys = pathPoints.map(p => p.y);
    const bx = Math.min(...xs), by = Math.min(...ys);

    return {
      id: `cell-${i}`,
      path: pathPoints,
      bounds: { x: bx, y: by, w: Math.max(...xs) - bx, h: Math.max(...ys) - by }
    };
  });
};

// ============================================================================
// SMART CROP (Simplified for Node - no face detection)
// ============================================================================

const calculateSmartCrop = (box, img, analysis = { x: 0.5, y: 0.5 }) => {
  const boxAsp = box.w / box.h;
  const imgAsp = img.width / img.height;
  let drawW, drawH, drawX, drawY;

  if (imgAsp > boxAsp) {
    drawH = img.height;
    drawW = drawH * boxAsp;
    drawY = 0;
    const slack = img.width - drawW;
    drawX = Math.max(0, Math.min(slack, analysis.x * img.width - drawW / 2));
  } else {
    drawW = img.width;
    drawH = drawW / boxAsp;
    drawX = 0;
    const slack = img.height - drawH;
    drawY = Math.max(0, Math.min(slack, analysis.y * img.height - drawH / 2));
  }

  return { sx: drawX, sy: drawY, sw: drawW, sh: drawH, dx: box.x, dy: box.y, dw: box.w, dh: box.h };
};

// ============================================================================
// RENDER ENGINE
// ============================================================================

const renderCollage = async (width, height, layoutItems, images, mode, seed) => {
  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = mode === 'minimal' ? '#f5f5f5' : '#111';
  ctx.fillRect(0, 0, width, height);

  const rng = createRng(seed);
  const pool = [...images].sort(() => 0.5 - rng());

  for (let i = 0; i < layoutItems.length; i++) {
    const item = layoutItems[i];
    const imgData = pool[i % pool.length];
    if (!imgData) continue;

    const img = await loadImage(imgData.path);

    ctx.save();
    ctx.beginPath();
    item.path.forEach((p, idx) => {
      if (idx === 0) ctx.moveTo(p.x, p.y);
      else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    ctx.clip();

    const crop = calculateSmartCrop(item.bounds, { width: img.width, height: img.height }, imgData.analysis);
    ctx.drawImage(img, crop.sx, crop.sy, crop.sw, crop.sh, crop.dx, crop.dy, crop.dw, crop.dh);

    if (mode === 'complex') {
      ctx.strokeStyle = '#000';
      ctx.lineWidth = width * 0.001;
      ctx.stroke();
    }
    ctx.restore();
  }

  return canvas;
};

// ============================================================================
// ENERGY ANALYSIS (Simplified for Node)
// ============================================================================

const analyzeImage = async (imagePath) => {
  if (!sharp) return { x: 0.5, y: 0.5 };

  try {
    const { data, info } = await sharp(imagePath)
      .resize(128, 128, { fit: 'inside' })
      .raw()
      .toBuffer({ resolveWithObject: true });

    const w = info.width, h = info.height;
    let totalX = 0, totalY = 0, totalE = 0;

    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * info.channels;
        const bri = (data[i] + data[i + 1] + data[i + 2]) / 3;
        const nextI = i + info.channels;
        const nextBri = x < w - 1 ? (data[nextI] + data[nextI + 1] + data[nextI + 2]) / 3 : bri;
        const energy = Math.abs(bri - nextBri);

        totalX += x * energy;
        totalY += y * energy;
        totalE += energy;
      }
    }

    if (totalE > 0) {
      return { x: (totalX / totalE) / w, y: (totalY / totalE) / h };
    }
  } catch (e) {
    console.warn(`Analysis failed for ${imagePath}:`, e.message);
  }

  return { x: 0.5, y: 0.5 };
};

// ============================================================================
// MAIN
// ============================================================================

program
  .name('genart-cli')
  .description('Headless Smart Crop Collage Generator')
  .version('1.0.0')
  .requiredOption('-s, --source <dir>', 'Source image directory')
  .requiredOption('-o, --out <dir>', 'Output directory')
  .option('-c, --count <number>', 'Number of collages to generate', '1')
  .option('-n, --cells <number>', 'Number of cells per collage', '9')
  .option('-m, --mode <mode>', 'Layout mode: minimal|balanced|complex', 'minimal')
  .option('-w, --width <pixels>', 'Output width in pixels', '4096')
  .option('-a, --aspect <ratio>', 'Aspect ratio (width/height)', '1.5')
  .option('-g, --gutter <percent>', 'Gutter as decimal (0.005 = 0.5%)', '0.005')
  .option('-q, --quality <percent>', 'JPEG quality (1-100)', '92')
  .option('--seed <number>', 'Starting seed (increments per collage)', String(Date.now()))
  .parse(process.argv);

const opts = program.opts();

console.log(`
╔════════════════════════════════════════════════════════════════╗
║  GENART HEADLESS ENGINE v1.0                                   ║
╚════════════════════════════════════════════════════════════════╝

  Source:   ${opts.source}
  Output:   ${opts.out}
  Count:    ${opts.count} collage(s)
  Cells:    ${opts.cells} per collage
  Mode:     ${opts.mode}
  Size:     ${opts.width}px @ ${opts.aspect}:1
  Quality:  ${opts.quality}%
`);

(async () => {
  // Validate source directory
  if (!fs.existsSync(opts.source)) {
    console.error(`ERROR: Source directory not found: ${opts.source}`);
    process.exit(1);
  }

  // Create output directory
  if (!fs.existsSync(opts.out)) {
    fs.mkdirSync(opts.out, { recursive: true });
    console.log(`Created output directory: ${opts.out}`);
  }

  // Load images
  const imageExts = ['.jpg', '.jpeg', '.png', '.webp', '.gif'];
  const files = fs.readdirSync(opts.source)
    .filter(f => imageExts.includes(path.extname(f).toLowerCase()))
    .map(f => path.join(opts.source, f));

  if (files.length === 0) {
    console.error(`ERROR: No images found in ${opts.source}`);
    process.exit(1);
  }

  console.log(`Found ${files.length} images. Analyzing...`);

  // Analyze images
  const images = [];
  for (const file of files) {
    process.stdout.write(`  Analyzing: ${path.basename(file)}...`);
    const analysis = await analyzeImage(file);
    images.push({ path: file, analysis });
    process.stdout.write(` [${(analysis.x * 100).toFixed(0)}%, ${(analysis.y * 100).toFixed(0)}%]\n`);
  }

  // Generate collages
  const width = parseInt(opts.width);
  const height = Math.round(width / parseFloat(opts.aspect));
  const cells = parseInt(opts.cells);
  const count = parseInt(opts.count);
  const quality = parseInt(opts.quality);
  const gutter = parseFloat(opts.gutter);
  let seed = parseInt(opts.seed);

  console.log(`\nGenerating ${count} collage(s) at ${width}x${height}px...\n`);

  for (let i = 0; i < count; i++) {
    const currentSeed = seed + i;
    const filename = `collage-${opts.mode}-${width}x${height}-${currentSeed}.jpg`;
    const outPath = path.join(opts.out, filename);

    process.stdout.write(`  [${i + 1}/${count}] Generating ${filename}...`);

    try {
      const rng = createRng(currentSeed);
      const layoutItems = computeLayout(width, height, cells, rng, opts.mode, gutter);
      const canvas = await renderCollage(width, height, layoutItems, images, opts.mode, currentSeed);

      const buffer = canvas.toBuffer('image/jpeg', { quality: quality / 100 });
      fs.writeFileSync(outPath, buffer);

      const sizeMB = (buffer.length / 1024 / 1024).toFixed(2);
      console.log(` ✓ (${sizeMB} MB)`);
    } catch (e) {
      console.log(` ✗ ERROR: ${e.message}`);
    }
  }

  console.log(`\n✓ Complete! ${count} collage(s) saved to ${opts.out}`);
})();
