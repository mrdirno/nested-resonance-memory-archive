# C3712 — Preview-first Studio

Author: Aldrin Payopay · September 5, 2026 · GPL-3.0-only

[Open Studio](https://mrdirno.github.io/nested-resonance-memory-archive/collage/) · [Code 496a17ba](https://github.com/mrdirno/nested-resonance-memory-archive/commit/496a17ba75aa622576ddc4de77ccc72119f8716c) · [Successful deployment](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/33995354619)

The artwork gets the available screen space. Editing controls open for one task at a time, and playback stays reachable. This responds to the user's report that the controls were overwhelming and the whole frame was hard to see.

## The flow

1. Start with **Art Room**, **Add images or video**, or **Try a lyric film**.
2. In Art Room, choose templates, then select a layer to edit its look or motion. Layer options hold reorder, solo, duplicate and delete. **Canvas & recipe** holds project settings, saved recipes and secondary HTML import.
3. **Add artwork** applies the editable source. Close Art Room to compose the project.
4. Choose **Add**, **Layout**, **Look**, **Motion** or **Text**. Done returns to the full preview. Canvas size/crop is under Layout → Canvas & crop; lyrics and the static title are under Text.
5. Play, pause or scrub in the compact transport. **Details** contains sources, trims, levels, duration and recording; **Export** offers the output formats and native loop length.
6. Use the expand icon or **F** for more preview space. **Back to editing** or **Escape** returns to the prior editing context. Nested dialogs and Details handle Escape first. Recording Stop remains visible.

## What changed on the public page

The same silent lyric sample was measured in fresh browser contexts, 500ms after readiness. The temporary notice occupies its own row and retires after four seconds. The comparison is a viewport test, not physical-device certification.

| Viewport | Before artwork | C3712 artwork |
|---|---:|---:|
| Desktop 1280×720 | 111×199 | 273×487 |
| Phone 390×844 | 164×292 | 338×602 |
| Landscape 844×390 | 19×34 | 88×157 |

Visible default buttons fell from **19 to 11**. The entire frame fits; controls sit outside the art. Opening one inspector gives it a bounded share of the view. Closing it returns that space to playback.

## Evidence and limits

**173/173 public browser cases** passed: native art/room 24, HTML and lyric help 30, compact transport 15, mobile geometry 21, project integrity 6, flow/captions/real exports 45, legacy viewport/decoder 32. These repeat 173 local cases. The first six groups cover Chromium, Mobile Chrome and Mobile Safari; legacy viewport cases cover Chromium and Mobile Safari. **40/40 unit suites**, typecheck and production build passed. Deployed JS, CSS, render worker and service worker match the tested build byte for byte.

Actual eight-second native MP4s decode to 240 desktop frames and 192 frames per mobile profile, with no blank frames. Caption MP4s retain the imported soundtrack, measured from decoded samples, plus text at the expected times. Project/SVG/recovery checks retain editable art and captions; local owned Bifurcata capture was exercised in all three profiles. Existing bundle-size, stale Browserslist and Actions runtime warnings are non-failing and remain visible in build evidence.

The Stage, recipe semantics and existing export engine remain in place. This release does not add audio/video-original packaging, global overlay/shot sequencing, built-in lyric extraction or a moving-HTML adapter. Those remain in the [art and intelligence roadmap](ART_AND_INTELLIGENCE_ROADMAP.md).

The final evolution book and this receipt are read before future work. The existing fleet publication thread is `persona500-collage-C3712-release`; a stored broadcast and peer acknowledgement are separate observations.
