// src/dev/roster.ts
// -----------------------------------------------------------------------------
// DEV-ONLY visual proof of the generator roster. Not an app route, not in the
// production build (vite only emits index.html) — this exists so a layout can be
// LOOKED AT rather than reasoned about.
//
// Why it earns its keep: the defect that started this rebuild ("the circle one
// sucks") is invisible in source and obvious in a picture. Every generator gets
// the same seed, count and gutter here, so they can be compared honestly, and
// the actual emitted cell count is printed next to the requested one — a
// generator that silently returns 4 cells when asked for 48 is the single most
// common failure mode in this kind of code and it is otherwise very easy to miss.
// -----------------------------------------------------------------------------

import { GENERATORS } from '../engine/geom/generators';
import { createRng } from '../lib/layout';
import { gutterPx } from '../engine/geom/poly';
import type { LayoutItem } from '../types';

const grid = document.getElementById('grid') as HTMLDivElement;
const stat = document.getElementById('stat') as HTMLSpanElement;
const countEl = document.getElementById('count') as HTMLInputElement;
const entEl = document.getElementById('entropy') as HTMLInputElement;
const gutEl = document.getElementById('gutter') as HTMLInputElement;
const aspEl = document.getElementById('aspect') as HTMLSelectElement;

let seed = 1234;

/** A stand-in for a photograph: enough hue and luminance variation that cell
 *  shape, gutter consistency and overlap are all visible at a glance. */
const makeSwatch = (): HTMLCanvasElement => {
  const c = document.createElement('canvas');
  c.width = 512; c.height = 512;
  const x = c.getContext('2d')!;
  const g = x.createLinearGradient(0, 0, 512, 512);
  g.addColorStop(0, '#ff8a3d'); g.addColorStop(0.35, '#e0446e');
  g.addColorStop(0.7, '#5a4bd8'); g.addColorStop(1, '#22d3c5');
  x.fillStyle = g; x.fillRect(0, 0, 512, 512);
  // Concentric rings make any mis-clipped or doubled cell obvious.
  x.globalAlpha = 0.22; x.strokeStyle = '#000'; x.lineWidth = 8;
  for (let r = 24; r < 400; r += 34) { x.beginPath(); x.arc(256, 256, r, 0, Math.PI * 2); x.stroke(); }
  x.globalAlpha = 1;
  return c;
};
const SWATCH = makeSwatch();

/**
 * Fraction of the frame actually covered by cells.
 *
 * This is the metric that catches the failure mode staring out of every early build:
 * a construction that runs, reports a healthy cell count, and still leaves a
 * black annulus or a dead corner. Count says nothing about coverage — a
 * generator can return 48 cells that occupy 40% of the frame. Reading the
 * painted pixels is the only honest measure, and it is cheap.
 */
const coverage = (cv: HTMLCanvasElement, W: number, H: number): number => {
  const x = cv.getContext('2d', { willReadFrequently: true })!;
  const d = x.getImageData(0, 0, W, H).data;
  let hit = 0;
  const total = W * H;
  // The harness background is #0d0e11; anything brighter is a painted cell.
  for (let i = 0; i < d.length; i += 4) {
    if (d[i] > 26 || d[i + 1] > 26 || d[i + 2] > 30) hit++;
  }
  return hit / total;
};

const draw = (cv: HTMLCanvasElement, items: LayoutItem[], W: number, H: number) => {
  const x = cv.getContext('2d')!;
  x.clearRect(0, 0, W, H);
  x.fillStyle = '#0d0e11';
  x.fillRect(0, 0, W, H);
  items.forEach((it, i) => {
    x.save();
    x.beginPath();
    it.path.forEach((p, k) => (k === 0 ? x.moveTo(p.x, p.y) : x.lineTo(p.x, p.y)));
    x.closePath();
    x.clip();
    // Vary the source window per cell so neighbours never share pixels — that
    // is what a real collage does and it makes cell boundaries legible.
    const s = 512 * (0.34 + ((i * 37) % 61) / 140);
    const sx = ((i * 97) % 100) / 100 * (512 - s);
    const sy = ((i * 53) % 100) / 100 * (512 - s);
    x.drawImage(SWATCH, sx, sy, s, s, it.bounds.x, it.bounds.y, it.bounds.w, it.bounds.h);
    x.restore();
  });
};

const render = async () => {
  const count = +countEl.value;
  const entropy = +entEl.value / 100;
  const gut = +gutEl.value;
  const aspect = +aspEl.value;
  (document.getElementById('countv') as HTMLSpanElement).textContent = String(count);
  (document.getElementById('entv') as HTMLSpanElement).textContent = entropy.toFixed(2);
  (document.getElementById('gutv') as HTMLSpanElement).textContent = String(gut);

  // MEASURE AT THE RESOLUTION THAT SHIPS. The app composes at 1200 logical
  // pixels; measuring at the 520px display size makes a constant-pixel gutter
  // more than twice as costly relative to cell size, so thin-celled generators
  // (slit scan, hilbert) score as broken here while being fine in the product.
  // The canvas is displayed scaled down by CSS — the numbers stay honest.
  const W = 1200;
  const H = Math.round(W / aspect);
  grid.innerHTML = '';
  let slowest = 0;
  let slowestName = '';
  let broken = 0;

  for (const spec of GENERATORS) {
    const fig = document.createElement('figure');
    const cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    const cap = document.createElement('figcaption');
    const blurb = document.createElement('div');
    blurb.className = 'blurb';
    blurb.textContent = spec.blurb;
    fig.append(cv, cap, blurb);
    grid.append(fig);

    let items: LayoutItem[] = [];
    let err = '';
    const t0 = performance.now();
    try {
      items = await spec.run({
        W, H, count, rng: createRng(seed), gutter: gutterPx(W, H, gut / 1000),
        entropy, t: 0,
      });
    } catch (e) {
      err = e instanceof Error ? e.message : String(e);
    }
    const ms = performance.now() - t0;
    if (ms > slowest) { slowest = ms; slowestName = spec.name; }

    if (!err) draw(cv, items, W, H);
    const cov = err ? 0 : coverage(cv, W, H);

    // The honest report: requested vs delivered vs COVERED. A generator that
    // returns far fewer cells than asked has collapsed; one that returns the
    // right number but covers 55% of the frame has a hole in it. Both are
    // failures and only the pair of numbers distinguishes them.
    const ratio = count > 0 ? items.length / count : 1;
    const bad = err || items.length === 0 || ratio < 0.4 || cov < 0.80;
    const off = err ? 'bad' : (bad || ratio > 2.6) ? 'warn' : '';
    if (bad) broken++;
    cap.innerHTML =
      `<span class="nm">${spec.name}</span>` +
      `<span class="meta ${off}">${err ? 'ERR ' + err
        : `${items.length}/${count} · ${(cov * 100).toFixed(0)}% · ${ms.toFixed(0)}ms`}</span>`;
  }
  stat.textContent =
    `seed ${seed} · ${GENERATORS.length} generators · slowest ${slowestName} ${slowest.toFixed(0)}ms` +
    (broken ? ` · ${broken} NEED WORK` : ' · all delivering, all covered');
};

(document.getElementById('reseed') as HTMLButtonElement).onclick = () => {
  seed = Math.floor(Math.random() * 1e6);
  void render();
};
for (const el of [countEl, entEl, gutEl, aspEl]) {
  el.addEventListener('change', () => void render());
}
countEl.addEventListener('input', () => {
  (document.getElementById('countv') as HTMLSpanElement).textContent = countEl.value;
});

void render();

// Expose for browser-driven assertions from the agent loop.
(window as unknown as Record<string, unknown>).__roster = {
  render, GENERATORS, setSeed: (s: number) => { seed = s; return render(); },
};
