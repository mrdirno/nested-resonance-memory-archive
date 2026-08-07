// src/lib/title.ts
// -----------------------------------------------------------------------------
// THE TITLE — a caption on the collage, drawn by every render path from ONE plan.
//
// WHY A PLAN AND NOT A DRAW
//   Four different surfaces produce final pixels here: the still preview
//   (`renderer.renderCanvas`), the live Stage (which is also what both video
//   exporters record), the full-resolution export worker (`render.worker.ts`,
//   an OffscreenCanvas on another thread) and the vector export
//   (`engine/color/vectorExport.ts`, which emits SVG and has no canvas at all).
//   If each of them wrapped the text itself, the wrap would be decided four
//   times against four font environments — and the worker is a different THREAD,
//   where a font stack is free to resolve differently. The first long title
//   would then break onto two lines in the preview and three in the export, and
//   the app would be back to the exact defect ONE LAYOUT was written to remove:
//   the picture you looked at is not the picture you got.
//
//   So the wrap is decided ONCE, on the main thread, against the same context
//   the preview draws with, and the RESULT travels. `planTitle` returns fully
//   resolved geometry in a canonical 1200-space basis (`TITLE_BASIS` = the
//   Stage's logical width = `PREVIEW_W`), `scaleTitlePlan` takes it to whatever
//   size a caller actually draws at, and the emitters below only ever paint
//   numbers somebody else already agreed on. A plan is structured-cloneable, so
//   it crosses to the worker unchanged.
//
// THE NO-OP RULE
//   `planTitle` returns `null` for an empty or whitespace-only title, and every
//   emitter returns immediately on a null plan. An untitled render therefore
//   runs the instruction stream it always ran, bit for bit — the same guarantee
//   `scaleLayout` gives at k=1 and `twistedDest` gives at angle 0.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>

/** WHERE the caption sits. Four corners' worth of intent, no more. */
export type TitlePlace = 'bl' | 'bc' | 'tl' | 'tc';

/** HOW BIG, as a fraction of the canvas width. */
export type TitleSize = 'sm' | 'md' | 'lg';

export interface TitleSpec {
  text: string;
  place: TitlePlace;
  size: TitleSize;
}

export interface TitleLine {
  text: string;
  /** LEFT edge of the line, always — the emitters never rely on `textAlign`. */
  x: number;
  /** BASELINE, not the top. */
  y: number;
  /** Measured advance width at `fontPx`. */
  w: number;
}

export interface TitlePlan {
  lines: TitleLine[];
  fontPx: number;
  lineH: number;
  /** The scrim the text sits on, so a caption stays readable over any photo. */
  plate: { x: number; y: number; w: number; h: number; r: number };
  /** The width this plan's numbers are expressed in. Callers scale by w/basis. */
  basis: number;
  /** The text did not fit in the line budget and the last line carries a '…'. */
  truncated: boolean;
}

/**
 * The canonical space every plan is generated in — the same 1200 the layout
 * generators use (`layoutScale.basisFor`), so a title and a fragment are laid
 * out against the same ruler and scale together.
 */
export const TITLE_BASIS = 1200;

/** Font size as a fraction of the basis width. */
const SIZE_RATIO: Record<TitleSize, number> = { sm: 0.042, md: 0.062, lg: 0.090 };

/** Never more than this many lines. A caption is not a paragraph. */
const MAX_LINES = 3;

/** Hard bound on input length, before wrapping. Pathological input, not policy. */
const MAX_CHARS = 240;

/** Margin from the canvas edge, off the SHORTER side so tall frames look right. */
const MARGIN_RATIO = 0.05;

const LINE_HEIGHT_RATIO = 1.14;
const PAD_X_RATIO = 0.44;
const PAD_Y_RATIO = 0.26;
/** Baseline inside a line box. ~cap height for the stack below. */
const BASELINE_RATIO = 0.80;
const RADIUS_RATIO = 0.28;

export const TITLE_INK = '#ffffff';
export const TITLE_PLATE = 'rgba(0,0,0,0.42)';
export const TITLE_FAMILY = '"Helvetica Neue", Helvetica, Arial, sans-serif';
export const TITLE_WEIGHT = 800;

/** The one font string. Every measurer and every emitter asks for it. */
export const titleFont = (px: number): string =>
  `${TITLE_WEIGHT} ${px}px ${TITLE_FAMILY}`;

/** Measures a run at a size. Injected so the plan is pure and sweepable. */
export type Measure = (text: string, fontPx: number) => number;

/** A measurer bound to a real 2D context — what the app passes in. */
export const measureWith = (
  ctx: { font: string; measureText: (s: string) => { width: number } },
): Measure => (text, fontPx) => {
  ctx.font = titleFont(fontPx);
  const w = ctx.measureText(text).width;
  return Number.isFinite(w) && w >= 0 ? w : 0;
};

/**
 * Whitespace collapsed, control characters dropped, length bounded.
 *
 * A newline is collapsed rather than honoured on purpose: the wrap below owns
 * where lines break, and a pasted paragraph with its own breaks would otherwise
 * blow the line budget before a single word had been measured.
 */
export const cleanTitle = (raw: unknown): string => {
  if (typeof raw !== 'string') return '';
  let s = '';
  for (let i = 0; i < raw.length && s.length <= MAX_CHARS + 1; i++) {
    const c = raw.charCodeAt(i);
    // C0/C1 controls (including \n, \t) become a space; everything else stands.
    s += (c < 0x20 || (c >= 0x7f && c < 0xa0)) ? ' ' : raw[i];
  }
  s = s.replace(/\s+/g, ' ').trim();
  return s.length > MAX_CHARS ? s.slice(0, MAX_CHARS).trim() : s;
};

const clampAspect = (a: unknown): number => {
  const n = typeof a === 'number' && Number.isFinite(a) ? a : 1;
  return Math.max(0.2, Math.min(5, n));
};

/** Greedy wrap. Splits a word that cannot fit a line on its own, mid-word. */
const wrapText = (text: string, maxW: number, fontPx: number, measure: Measure): string[] => {
  const words = text.split(' ').filter((w) => w.length > 0);
  const lines: string[] = [];
  let cur = '';

  const pushHardSplit = (word: string): void => {
    // A single token wider than the line (a URL, a hashtag, one long word).
    // Consume it a character at a time so the caller still gets whole lines.
    let chunk = '';
    for (let i = 0; i < word.length; i++) {
      const next = chunk + word[i];
      if (chunk && measure(next, fontPx) > maxW) {
        lines.push(chunk);
        chunk = word[i];
      } else {
        chunk = next;
      }
    }
    cur = chunk;
  };

  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (!cur) {
      if (measure(word, fontPx) > maxW) { pushHardSplit(word); continue; }
      cur = word;
      continue;
    }
    const cand = cur + ' ' + word;
    if (measure(cand, fontPx) <= maxW) { cur = cand; continue; }
    lines.push(cur);
    cur = '';
    if (measure(word, fontPx) > maxW) { pushHardSplit(word); continue; }
    cur = word;
  }
  if (cur) lines.push(cur);
  return lines;
};

/** Trims a line until it plus an ellipsis fits. Always returns something. */
const ellipsize = (line: string, maxW: number, fontPx: number, measure: Measure): string => {
  const E = '…';
  if (measure(line + E, fontPx) <= maxW) return line + E;
  let s = line;
  while (s.length > 0 && measure(s + E, fontPx) > maxW) s = s.slice(0, -1);
  return (s.replace(/\s+$/, '') || '') + E;
};

/**
 * THE PLAN. Pure given `measure`; every number is in `TITLE_BASIS` space.
 *
 * Returns null for an empty title or a frame too degenerate to hold one, and a
 * null plan is the signal every emitter treats as "draw nothing at all".
 */
export const planTitle = (
  spec: { text?: unknown; place?: unknown; size?: unknown } | null | undefined,
  aspect: number,
  measure: Measure,
): TitlePlan | null => {
  const text = cleanTitle(spec?.text);
  if (!text) return null;

  const place: TitlePlace =
    spec?.place === 'bc' || spec?.place === 'tl' || spec?.place === 'tc' ? spec.place : 'bl';
  const size: TitleSize =
    spec?.size === 'sm' || spec?.size === 'lg' ? spec.size : 'md';

  const W = TITLE_BASIS;
  const H = TITLE_BASIS / clampAspect(aspect);
  const m = MARGIN_RATIO * Math.min(W, H);

  // VERTICAL FIT FIRST. A `lg` title on a very wide, short frame can be taller
  // than the frame's whole safe area, and no amount of wrapping fixes that —
  // so the font comes down until ONE line plus its plate provably fits. Bounded
  // (each step is x0.8, floor 8px) and deterministic.
  let fontPx = SIZE_RATIO[size] * W;
  for (let guard = 0; guard < 24; guard++) {
    const lh = fontPx * LINE_HEIGHT_RATIO;
    const py = fontPx * PAD_Y_RATIO;
    if (lh + 2 * py <= H - 2 * m || fontPx <= 8) break;
    fontPx *= 0.8;
  }

  const lineH = fontPx * LINE_HEIGHT_RATIO;
  const padX = fontPx * PAD_X_RATIO;
  const padY = fontPx * PAD_Y_RATIO;

  // The plate is what has to respect the margin, so the TEXT box is the margin
  // less the plate's own padding. Without this a full-width line pushes its
  // scrim past the edge of the canvas and the caption looks like a bug.
  const maxW = W - 2 * m - 2 * padX;
  if (!(maxW > 0)) return null;

  // How many lines the frame can hold, which is the real cap on a short frame.
  const byHeight = Math.floor((H - 2 * m - 2 * padY) / lineH);
  const lineBudget = Math.max(1, Math.min(MAX_LINES, byHeight));

  let lines = wrapText(text, maxW, fontPx, measure);
  if (lines.length === 0) return null;

  let truncated = false;
  if (lines.length > lineBudget) {
    truncated = true;
    lines = lines.slice(0, lineBudget);
    lines[lines.length - 1] = ellipsize(lines[lines.length - 1], maxW, fontPx, measure);
  }

  const widths = lines.map((l) => {
    const w = measure(l, fontPx);
    return Number.isFinite(w) && w > 0 ? Math.min(w, maxW) : 0;
  });
  const blockW = widths.reduce((a, b) => Math.max(a, b), 0);
  const blockH = lines.length * lineH;

  const plateW = blockW + 2 * padX;
  const plateH = blockH + 2 * padY;

  const centred = place === 'bc' || place === 'tc';
  const plateX = centred ? (W - plateW) / 2 : m;
  const plateY = place === 'tl' || place === 'tc' ? m : H - m - plateH;

  const out: TitleLine[] = lines.map((t, i) => ({
    text: t,
    x: centred ? (W - widths[i]) / 2 : plateX + padX,
    y: plateY + padY + i * lineH + fontPx * BASELINE_RATIO,
    w: widths[i],
  }));

  return {
    lines: out,
    fontPx,
    lineH,
    plate: {
      x: plateX, y: plateY, w: plateW, h: plateH,
      r: Math.min(fontPx * RADIUS_RATIO, plateH / 2, plateW / 2),
    },
    basis: W,
    truncated,
  };
};

/**
 * The plan at another size. `k = 1` returns the INPUT OBJECT untouched, so a
 * caller drawing at the basis runs on the very numbers `planTitle` produced —
 * the same identity guarantee `scaleLayout` makes.
 */
export const scaleTitlePlan = (plan: TitlePlan | null, k: number): TitlePlan | null => {
  if (!plan) return null;
  if (!Number.isFinite(k) || k <= 0) return null;
  if (k === 1) return plan;
  return {
    lines: plan.lines.map((l) => ({ text: l.text, x: l.x * k, y: l.y * k, w: l.w * k })),
    fontPx: plan.fontPx * k,
    lineH: plan.lineH * k,
    plate: {
      x: plan.plate.x * k, y: plan.plate.y * k,
      w: plan.plate.w * k, h: plan.plate.h * k, r: plan.plate.r * k,
    },
    basis: plan.basis * k,
    truncated: plan.truncated,
  };
};

/** Convenience: the plan already scaled for a surface `width` px wide. */
export const titlePlanFor = (plan: TitlePlan | null, width: number): TitlePlan | null =>
  plan ? scaleTitlePlan(plan, width / plan.basis) : null;

type Ctx2D = CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D;

/**
 * Rounded rectangle by hand.
 *
 * `roundRect` exists on both context types in current browsers and is NOT used:
 * this module runs on a worker thread too, and a path built from `arcTo` is the
 * same instruction stream everywhere there has ever been a canvas.
 */
const roundRectPath = (ctx: Ctx2D, x: number, y: number, w: number, h: number, r: number): void => {
  const rr = Math.max(0, Math.min(r, w / 2, h / 2));
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
};

/**
 * PAINT. The plan must already be at this context's scale (`titlePlanFor`).
 * Null plan -> not one instruction, which is what keeps an untitled render
 * byte-identical to a build without this module.
 */
export const drawTitlePlan = (ctx: Ctx2D, plan: TitlePlan | null): void => {
  if (!plan || plan.lines.length === 0) return;
  ctx.save();
  try {
    ctx.fillStyle = TITLE_PLATE;
    roundRectPath(ctx, plan.plate.x, plan.plate.y, plan.plate.w, plan.plate.h, plan.plate.r);
    ctx.fill();

    ctx.fillStyle = TITLE_INK;
    ctx.font = titleFont(plan.fontPx);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    for (let i = 0; i < plan.lines.length; i++) {
      const l = plan.lines[i];
      ctx.fillText(l.text, l.x, l.y);
    }
  } finally {
    ctx.restore();
  }
};

const esc = (s: string): string =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
   .replace(/"/g, '&quot;').replace(/'/g, '&apos;');

/** The same plan as SVG. Empty string on a null plan — nothing is emitted. */
export const titlePlanToSvg = (plan: TitlePlan | null): string => {
  if (!plan || plan.lines.length === 0) return '';
  const p = plan.plate;
  let s = `  <g id="Title">
    <rect x="${p.x.toFixed(2)}" y="${p.y.toFixed(2)}" width="${p.w.toFixed(2)}" height="${p.h.toFixed(2)}" rx="${p.r.toFixed(2)}" fill="${TITLE_PLATE}" />
`;
  for (let i = 0; i < plan.lines.length; i++) {
    const l = plan.lines[i];
    s += `    <text x="${l.x.toFixed(2)}" y="${l.y.toFixed(2)}" font-family='${TITLE_FAMILY}' font-size="${plan.fontPx.toFixed(2)}" font-weight="${TITLE_WEIGHT}" fill="${TITLE_INK}" xml:space="preserve">${esc(l.text)}</text>
`;
  }
  return s + `  </g>
`;
};
