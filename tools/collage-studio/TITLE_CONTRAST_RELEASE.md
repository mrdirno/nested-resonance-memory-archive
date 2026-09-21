# Title contrast — September 21, 2026

Author: Aldrin Payopay · GPL-3.0-only

Status: published and verified live. Source [`7ba19031`](https://github.com/mrdirno/nested-resonance-memory-archive/commit/7ba19031fdf71a554d3c7b6a32ce0d44b181a39c); [Pages 35631462820](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/35631462820) succeeded. [Open Studio](https://mrdirno.github.io/nested-resonance-memory-archive/collage/).

Bright artwork could wash out yellow, red, blue and pink titles. The earlier colour gate compared text with opaque black or white while the actual plate was translucent. This release raises the plate opacity just enough for the existing 3:1 large-title contrast contract under ordinary opaque sRGB compositing. It preserves the chosen ink, title geometry, fonts and every existing white/black palette.

| Title | Previous black plate | Corrected black plate |
|---|---:|---:|
| Yellow | 42% | 53% |
| Red | 42% | 75% |
| Blue | 42% | 77% |
| Pink | 42% | 76% |

The visible tradeoff is a darker patch behind these four colours, covering the same area. No additional control, media format, dependency or network service is introduced. One plan still supplies the still preview, live Stage, raster worker and SVG, but their outputs are tested separately.

## Reused work and regression

Resumes the prepared C3733 correction from the existing fleet handoff, integrating it with C3742 font selection. The new composited-colour unit suite fails on the actual unchanged source (yellow over #d2d2d2 gives 2.99843:1), while the old opaque-anchor assertion passes that defective palette. Corrected colour checks: 1,687; existing geometry checks: 82,871; font checks: 26,958. Typecheck and production build pass.

The real-page regression uses an owned white image, measured glyph interiors and a substantial bright plate region. It separately drives still preview, downloaded worker JPEG, SVG, manual project Save/Open, live Stage and a decoded recorded MP4. Antialiased edges and JPEG/video ringing are excluded from solid-region measurements rather than claimed to meet the palette bound.

Reusable commands: `node tests/unit/title-colour.invariants.mjs`, `node tests/unit/title.invariants.mjs`, `node tests/unit/title-font.invariants.mjs`; `npx playwright test tests/e2e/title-contrast.spec.ts --workers=1 --project=chromium --project="Mobile Chrome"`. Use the real Collage preview on strict port 5199. `COLLAGE_BASE_URL` targets the public page. Media checks use muted Chromium; pure-image cases additionally run on WebKit.

## Boundaries and next work

This verifies the composited palette and measured exported samples. It does not certify every compressed or antialiased pixel, small displayed text, HDR/wide-gamut rendering, external SVG editors, or physical phones. Small text can require stronger contrast.

No changes to layer audition/Keep/Apply, viewport geometry, original media or project schemas. The next substantial portability gap remains manual video-original packaging with clip/poster bindings AND authored trim, requested speed, length-sync mode, mute, level and source fade. Merely bundling video blobs would silently lose edits. Current title colour/font, audio portability and native art must survive that future change.

## Delivered evidence

34 built and 34 public browser checks pass: eight existing colour/font cases, ten new contrast/Save/Open/media cases, and sixteen mobile layout cases. Pure-image tests span Chromium, Mobile Chrome, Mobile Safari and desktop WebKit; the two media cases run only in muted Chromium profiles. Their two built and two public MP4 files decode completely with no errors. All five public runtime files match the tested build. The previous public build fails the same new regression for all four inks: bright-image preview/JPEG ratios 1.12–2.12:1, versus at least 3:1 in the corrected sampled interiors. The negative run and exported originals are retained in the release checkpoint.

The test initially assumed an exact 2048px export and fixed-size sampling windows. Actual aspect quantization produces 2047px, and a small Stage needs sampling windows scaled to its native font and plate padding. These harness corrections retain the strict contrast threshold and original failures. Existing build warnings about bundle size, browser-data age and Actions runtime migration remain; none caused a failed release gate.
