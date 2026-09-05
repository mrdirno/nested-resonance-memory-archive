// Original procedural sample artwork. Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// Canvas shapes, not model-generated images. All pixels are made on this device.
import type { CaptionTrack } from './captions';

const SIDE = 960;
const PALETTES = [
  ['#ece7d9', '#183bc5', '#ef705b', '#c7db54'],
  ['#183bc5', '#ece7d9', '#c7db54', '#ef705b'],
  ['#ef705b', '#183bc5', '#ece7d9', '#c7db54'],
  ['#c7db54', '#183bc5', '#ef705b', '#ece7d9'],
];

const makeArtwork = async (index: number): Promise<File> => {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = SIDE;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('This browser could not create the sample artwork canvas.');
  let seed = (0x91ac751 + index * 0x51f31) >>> 0;
  const random = () => { seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5; return (seed >>> 0) / 4294967296; };
  const [paper, ink, accent, light] = PALETTES[index];
  try {
    ctx.fillStyle = paper;
    ctx.fillRect(0, 0, SIDE, SIDE);
    // Oversized cut-paper disc; the crop makes a whole image from a few shapes.
    ctx.fillStyle = ink;
    ctx.beginPath();
    ctx.arc(210 + index * 108, 280 + (index % 2) * 310, 338, 0, Math.PI * 2);
    ctx.fill();
    // A broad ribbon travels through the composition, with a finer inner seam.
    for (const [width, color] of [[182, accent], [14, paper]] as const) {
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(-120, 780 - index * 80);
      ctx.bezierCurveTo(350, 850, 450 - index * 40, -180, 1100, 320 + index * 100);
      ctx.stroke();
    }
    // A suspended disc and offset ring add a second scale of movement.
    ctx.fillStyle = light;
    ctx.beginPath();
    ctx.arc(690 - index * 80, 260 + index * 110, 114, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = ink;
    ctx.lineWidth = 7;
    ctx.beginPath();
    ctx.arc(728 - index * 80, 222 + index * 110, 140, 0, Math.PI * 2);
    ctx.stroke();
    // Small repeated arcs create rhythm without introducing labels or glyphs.
    ctx.save();
    ctx.translate(680, 735);
    ctx.rotate(index * 0.45 - 0.6);
    ctx.strokeStyle = paper;
    ctx.lineWidth = 9;
    for (let i = 0; i < 7; i++) {
      ctx.beginPath();
      ctx.arc(0, 0, 28 + i * 21, Math.PI * 0.1, Math.PI * 1.25);
      ctx.stroke();
    }
    ctx.restore();
    // Deterministic pigment grain; no downloaded textures or source media.
    for (let i = 0; i < 22000; i++) {
      ctx.fillStyle = random() > 0.5 ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.07)';
      const size = 0.5 + random() * 1.5;
      ctx.fillRect(random() * SIDE, random() * SIDE, size, size);
    }
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((value) => value ? resolve(value) : reject(new Error('The browser could not encode sample artwork as PNG.')), 'image/png');
    });
    return new File([blob], `original-shapes-${index + 1}.png`, { type: 'image/png' });
  } finally { canvas.width = canvas.height = 0; }
};

export const createLyricDemo = async (): Promise<{ files: File[]; captions: CaptionTrack }> => {
  const files: File[] = [];
  for (let i = 0; i < PALETTES.length; i++) files.push(await makeArtwork(i));
  return {
    files,
    captions: { place: 'bc', size: 'md', cues: [
      { id: 'sample-1', start: 0, end: 3.3, text: 'MAKE SOMETHING' },
      { id: 'sample-2', start: 3.3, end: 6.6, text: 'ONLY YOU' },
      { id: 'sample-3', start: 6.6, end: 10, text: 'COULD MAKE' },
    ] },
  };
};
