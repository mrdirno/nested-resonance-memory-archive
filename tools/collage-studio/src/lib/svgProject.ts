// src/lib/svgProject.ts
// =============================================================================
// THE POST — the exported SVG IS the project file.
//
// A composition code is a RECIPE: it describes the collage and carries none of
// the pictures, so "send someone your collage" has meant sending a code and the
// photographs separately. The exported SVG already held both — every fragment's
// source is embedded as a base64 data URI, and the whole `AppState` rode along
// in a comment — and it could not be opened. `project.ts:loadFromSVG` parsed the
// manifest, built a DOMParser, and then `return null` under thirty lines of
// deliberation about whether the images would be recoverable. They already were:
// the very fix that TODO said it was waiting for ("vectorExport MUST convert
// images to Base64") had since shipped, and nobody came back to tell it.
//
// This module is the seam that makes the file honest, in both directions:
// what `vectorExport` writes into the SVG, and what `project.ts` reads back out.
// It is PURE — no DOM, no fetch, string in and string out — so the round trip is
// swept under plain node (`tests/unit/svgProject.invariants.mjs`) instead of
// being asserted only by an eight-minute browser run.
//
// -----------------------------------------------------------------------------
// WHY THE MANIFEST MOVED OUT OF THE XML COMMENT
// -----------------------------------------------------------------------------
// It had to. `<!-- JSON_MANIFEST: {...} -->` is not a container the manifest can
// safely live in, and the caption made that reachable from the UI:
//
//   * XML forbids `--` ANYWHERE inside a comment. Type a caption with an em-dash
//     typed as two hyphens — "well-shot -- or so I thought" — and the exported
//     SVG is not well-formed XML. Browsers parse `image/svg+xml` with a strict
//     XML parser, so the file does not render at all; it is not a degraded
//     picture, it is a parse error.
//   * A caption containing `-->` CLOSES THE COMMENT EARLY. The rest of the
//     manifest then sits in the document as raw text before the root element,
//     which is also fatal.
//
// Both were live the moment THE TITLE shipped, because the title is free text
// and `JSON.stringify` passes hyphens through untouched. So the manifest now
// lives in a real `<metadata>` element — the element SVG 1.1 defines for exactly
// this — as XML-escaped text, where `-`, `--` and `-->` are all ordinary
// characters and only `&`, `<` and `>` need care.
//
// The cost is deliberate and one-way: an SVG exported BEFORE this change carries
// the old comment and no image identity, so it cannot be reopened. It is refused
// rather than half-opened — see `readProject`.
//
// -----------------------------------------------------------------------------
// WHY THE POOL, AND WHY ALL OF IT
// -----------------------------------------------------------------------------
// The manifest carries the SOURCE POOL in POOL ORDER, not the drawn order.
// `arrangeBag` decides which photograph lands in which fragment from the pool's
// order AND its length, so a pool that comes back short or shuffled re-deals
// every slot: the same code, the same pictures, a different collage. That is the
// silent-wrong-answer failure this repo has already scarred once, so the writer
// embeds EVERY pool image (undrawn ones as hidden `<defs>` entries) and the
// reader fails closed on the first id it cannot find.
//
// Author: Aldrin Payopay <aldrin.gdf@gmail.com>
// =============================================================================

import type { AppState } from '../types';
import type { AnalysisResult } from './analysis';
import { normalizeArtRecipe, type ArtRecipe } from './artRack';

/** The element the manifest lives in, and the id that identifies it as ours. */
export const PROJECT_EL = 'metadata';
export const PROJECT_ID = 'collage-project';

/**
 * The attribute that names WHICH source an `<image>` element is.
 *
 * Positional matching was the alternative and it is fragile in the one way that
 * matters: `generateVectorExport` skips a slot whose asset is null, so the n-th
 * `<image>` is not the n-th fragment. An explicit id survives that, survives a
 * hand-edit that reorders the file, and lets a source drawn into two fragments
 * resolve to one entry.
 */
export const SRC_ID_ATTR = 'data-src-id';

/** Bumped only if the shape below stops being readable by an older reader. */
export const PROJECT_FORMAT = 1;

/** What a project needs to know about a source picture. The PIXELS are not here
 *  — they are the `<image>` element's own data URI, found by `data-src-id`. */
export interface SvgImageMeta {
  id: string;
  originalName: string;
  analysis: AnalysisResult;
  art?: ArtRecipe;
}

export interface SvgProject {
  state: AppState;
  /** The SOURCE POOL, in pool order. Not the drawn order. */
  images: SvgImageMeta[];
}

// -----------------------------------------------------------------------------
// XML ESCAPING
// -----------------------------------------------------------------------------

/**
 * Text-content escaping. Three substitutions, `&` FIRST — escape `<` first and
 * the `&` it introduces gets escaped again on the next pass, turning `<` into
 * `&amp;lt;`.
 */
export const escapeXmlText = (s: string): string =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/**
 * The exact inverse, `&amp;` LAST for the mirrored reason: unescaping it first
 * would turn a literal `&amp;lt;` (which encodes the four characters `&lt;`)
 * into `&lt;` and then into `<`, inventing a character the author never wrote.
 */
export const unescapeXmlText = (s: string): string =>
  s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

/** Attribute-value escaping. Ids are app-minted and safe; this does not assume it. */
export const escapeXmlAttr = (s: string): string =>
  escapeXmlText(s).replace(/"/g, '&quot;').replace(/'/g, '&apos;');

const unescapeXmlAttr = (s: string): string =>
  s.replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

// -----------------------------------------------------------------------------
// WRITE
// -----------------------------------------------------------------------------

/** ` data-src-id="…"`, or `''` for an asset with no id — never a bare `undefined`. */
export const srcIdAttr = (id: string | null | undefined): string =>
  typeof id === 'string' && id.length > 0 ? ` ${SRC_ID_ATTR}="${escapeXmlAttr(id)}"` : '';

/**
 * The `<metadata>` element carrying the whole project, ready to splice into the
 * document. Returns `''` when there is no state to carry, so an export without
 * one is byte-identical to a build without this feature.
 */
export const projectMetadata = (
  state: AppState | null | undefined,
  images: SvgImageMeta[] | null | undefined,
): string => {
  if (!state) return '';
  const payload = { format: PROJECT_FORMAT, state, images: (images ?? []).map(metaForAsset) };
  return `  <${PROJECT_EL} id="${PROJECT_ID}">${escapeXmlText(JSON.stringify(payload))}</${PROJECT_EL}>\n`;
};

/** The pool entry for an asset — the fields that must survive, and no others. */
export const metaForAsset = (a: {
  id: string;
  originalName?: string;
  analysis: AnalysisResult;
  art?: ArtRecipe;
}): SvgImageMeta => ({
  id: a.id,
  originalName: a.originalName || 'image.png',
  analysis: a.analysis,
  ...(a.art === undefined ? {} : { art: normalizeArtRecipe(a.art) }),
});

// -----------------------------------------------------------------------------
// READ
// -----------------------------------------------------------------------------

/**
 * Pull the manifest back out. `null` on anything that is not one of ours —
 * including an SVG exported before this existed, which carries the old comment
 * and no image identity at all and therefore cannot be reopened exactly.
 *
 * Scanned with `indexOf` rather than a regular expression on purpose: the text
 * this runs over holds every photograph as base64 and can be tens of megabytes,
 * and a pattern with two lazy quantifiers over that is a way to hang a tab.
 */
export const readProject = (svgText: string): SvgProject | null => {
  if (typeof svgText !== 'string' || svgText.length === 0) return null;

  const open = svgText.indexOf(`<${PROJECT_EL} id="${PROJECT_ID}"`);
  if (open < 0) return null;
  const gt = svgText.indexOf('>', open);
  if (gt < 0) return null;
  const close = svgText.indexOf(`</${PROJECT_EL}>`, gt);
  if (close < 0) return null;

  let parsed: unknown;
  try {
    parsed = JSON.parse(unescapeXmlText(svgText.slice(gt + 1, close)));
  } catch {
    return null;
  }

  const o = parsed as { state?: unknown; images?: unknown } | null;
  if (!o || typeof o !== 'object') return null;

  const state = o.state as AppState | undefined;
  if (!state || typeof state !== 'object') return null;
  if (!state.layout || typeof state.layout !== 'object') return null;
  if (!Array.isArray(o.images)) return null;

  const images: SvgImageMeta[] = [];
  for (const raw of o.images as unknown[]) {
    const m = raw as Partial<SvgImageMeta> | null;
    // An entry with no id cannot be matched to its pixels, and a pool with a
    // hole in it re-deals every slot after the hole. Refuse the whole file.
    if (!m || typeof m.id !== 'string' || m.id.length === 0) return null;
    try {
      images.push({
        id: m.id,
        originalName: typeof m.originalName === 'string' ? m.originalName : 'image.png',
        analysis: m.analysis as AnalysisResult,
        ...(m.art === undefined ? {} : { art: normalizeArtRecipe(m.art) }),
      });
    } catch { return null; }
  }

  return { state, images };
};

/**
 * Every embedded source, keyed by `data-src-id`.
 *
 * One linear pass. `>` cannot occur inside a base64 data URI (the alphabet is
 * `A-Za-z0-9+/=` and the `data:…;base64,` prefix has none either), so the first
 * `>` after `<image` really is the end of the tag — which is what makes the
 * cheap scan safe on a document whose tags are megabytes wide.
 */
export const readImageSources = (svgText: string): Map<string, string> => {
  const out = new Map<string, string>();
  if (typeof svgText !== 'string') return out;

  let i = svgText.indexOf('<image');
  while (i >= 0) {
    const after = svgText.charAt(i + 6);
    // `<image` must be the whole element name — not the prefix of a longer one.
    if (after === ' ' || after === '\n' || after === '\t' || after === '\r' || after === '/' || after === '>') {
      const end = svgText.indexOf('>', i);
      if (end < 0) break;
      const tag = svgText.slice(i, end);
      const id = attrIn(tag, SRC_ID_ATTR);
      const href = attrIn(tag, 'xlink:href') ?? attrIn(tag, 'href');
      if (id && href && !out.has(id)) out.set(id, href);
      i = svgText.indexOf('<image', end);
    } else {
      i = svgText.indexOf('<image', i + 6);
    }
  }
  return out;
};

/** One double-quoted attribute out of a single tag's text. */
const attrIn = (tag: string, name: string): string | null => {
  const key = `${name}="`;
  const at = tag.indexOf(key);
  if (at < 0) return null;
  const from = at + key.length;
  const to = tag.indexOf('"', from);
  if (to < 0) return null;
  return unescapeXmlAttr(tag.slice(from, to));
};
