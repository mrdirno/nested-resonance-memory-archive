# Wish coverage: source inventory and five live samples

Author: Aldrin Payopay · GPL-3.0-only · September 8, 2026

All 189 maintained HTML source pages have a recognizable Wish runtime inclusion. That is source coverage, not evidence that every visitor can find or use the control. The three maintained pages exercised live opened the correct modal; all three lost unsent feedback after reload. Commons exposes its feedback form through “Add gear to the list,” below the initial phone viewport, rather than a named Wish or Feedback control.

Nothing in this folder changes or publishes a production page. No feedback was submitted. No login, account preferences, or server acceptance was tested.

## Files and scope

- `source_inventory.py` reads the actual Pages workflow and source HTML. It writes only the report path explicitly supplied through `--output`.
- `source-inventory.json` preserves source paths, deployed paths, inclusion evidence, source hashes, the workflow hash, and untested behavior facets.
- `live_sample.cjs` exercises five explicitly listed URLs in isolated Playwright Chromium contexts. It blocks all non-GET/HEAD/OPTIONS requests and never clicks a submit button.
- `live-observations.json` preserves the latest five-page browser measurements, including exact timestamps, page errors and screenshot paths.
- `verify_live_identity.py` and `live-identity.json` preserve separate byte comparisons for the two sampled legacy HTML pages.
- `screenshots/` contains eight screenshots: a page screenshot for each sample and the opened modal for the three maintained samples.

The source inventory was recorded at `2026-09-08T13:00:41.796294+00:00` against Git HEAD `042ce6b9938d2539e4eff9b29dff33b430a0ce22`. Each source file has its own hash, so the report does not assume HEAD captures every filesystem change. The latest browser sample ran from `2026-09-08T13:02:13.470Z` to `2026-09-08T13:02:18.613Z`. Maintained browser pages were not byte-matched to source. A later read-only comparison matched both sampled legacy HTML bodies to their source bytes; assets were not compared.

## What the source inventory measures

| Source group | Maintained source HTML | Recognized runtime inclusion |
| --- | ---: | ---: |
| 17 trade toolkits | 184 | 184 |
| Commons | 3 | 3 |
| Active HALO | 1 | 1 |
| Current Collage Studio | 1 | 1 |
| Total | 189 | 189 |

Those 189 source files map to 190 deployed HTML paths because the active HALO source is copied both to `/index.html` and its archive path. Directory-index URL aliases such as `/collage/` do not increase the count.

The deployment also stages legacy material. The inventory records 502 archived HTML sources other than active HALO, one Collage Beta source, and the classic Bridge source: **504 legacy source pages, zero recognized shared Wish inclusions**. These are separately labeled legacy debt. They do not fail the maintained-source audit. The full archive directory has 503 HTML files including HALO; counting that directory alone as 503 current failures would misstate lifecycle and double-count active HALO.

The workflow header says the repo-root `collage-beta/` directory is not served, but its executable staging block contains `cp -R collage-beta/. HELIOS-BRIDGE/dist/collage-beta/`. The fresh `/collage-beta/` response is byte-identical to `collage-beta/index.html`: 1,030 bytes and SHA-256 `a0013f03fafe1b37e0a25b3b7fbd38844487f36ebb5f8f98378556ff9e684a37`. The report follows that staging instruction and measured response, not the contradictory header. Archive V045 also matched exactly, at 27,983 bytes and SHA-256 `3b772c47067965e4e61627c58496a5a1c952527cd88c5b3acc5ed6e2400b96b6`. These are separate HTML identity receipts, not an inference from HTTP 200 or a shared page title.

`TRADES` and the active root source are parsed from `.github/workflows/deploy_bridge.yml`. The known Commons, Collage, archive, Beta and classic staging statements are asserted. Missing expected files, unknown requested pages, changed mappings or unmatched trade directories produce an error. This is a narrow adapter for the current deployment structure, not a shell interpreter or a freshly assembled Pages artifact. Generated SPA routes and additional Vite public/build output are not inferred.

Inclusion evidence comes from actual script tags and a recognizable dynamic `script.src` assignment, including Collage's runtime loader. HTML comments do not count. Inclusion does not establish successful network loading, reachable UI, correct surface attribution, draft durability, or a successful database insert. The JSON explicitly leaves those facets `not_tested`.

## Live evidence: five URLs, one viewport

Playwright Chromium used a 390 × 844 mobile/touch viewport with a dark browser color preference. These are browser-emulation results, not physical-device results.

| URL suffix | Lifecycle | Runtime loaded | Named Wish/Feedback trigger | Opens matching modal | Draft close/reopen | Draft reload |
| --- | --- | --- | --- | --- | --- | --- |
| `av/consumables.html` | Maintained | Toolkit | Yes; initially visible and hit-tested | Yes; AV | Retained | Lost |
| `commons/index.html` | Maintained | Feedback | No; “Add gear to the list” | Yes; Commons, after scrolling | Retained | Lost |
| `collage/` | Maintained | Feedback | Yes; accessible name “Wish it better,” visible text “Wish” | Yes; Collage | Retained | Lost |
| `archive/HELIOS-V045-amethyst-interference.html` | Archived | No shared runtime | No known shared trigger | Not tested | Not tested | Not tested |
| `collage-beta/` | Legacy | No shared runtime | No known shared trigger | Not tested | Not tested | Not tested |

All five URLs returned HTTP 200. The Commons opener is reachable after scrolling and was clicked successfully; being outside the initial viewport is not being inaccessible. The initial viewport screenshot demonstrates why it is not a persistent, immediately visible Wish control. All three maintained openers passed center hit-testing after any necessary scrolling, and their runtime surface matched the expected modal.

All three maintained samples had zero page errors. Collage Beta reported a root-scoped service-worker request for `https://mrdirno.github.io/sw.js` returning 404. The initial earlier probe ended before that asynchronous error; the reusable sample waits for network idle and captures it. This is recorded as legacy debt, not a new failure in the current Collage app.

All five samples measured zero document horizontal overflow at this viewport. No wider device or modal-layout conclusion follows from that single measurement. The screenshots were saved before synthetic draft text was entered. The report records no attempted network writes and no submissions.

AV and Commons kept their light body background under the dark browser preference. Collage's app remained dark while its feedback modal was light, visible in `screenshots/collage-modal.png`. The initial source scan found no `prefers-color-scheme`, `data-theme`, `theme-mode` or `themeMode` signals in the 184 trade HTML pages or the three Commons pages. A source-pattern scan is not a test of time-based theme behavior; no clock-boundary theme test was performed.

## Reproduce

From this `audit/` directory:

```sh
python3 source_inventory.py --output source-inventory.json
python3 source_inventory.py --page /collage/index.html
python3 source_inventory.py --page av/consumables.html
node live_sample.cjs
python3 verify_live_identity.py
```

To select a different checkout or a served artifact:

```sh
python3 source_inventory.py --root /absolute/path/to/checkout
node live_sample.cjs /absolute/path/to/checkout https://example.test/site-base/
```

The optional browser sample uses the selected checkout's installed `tools/collage-studio/node_modules/playwright`. It does not install dependencies. It replaces its own JSON and screenshot outputs on each run. Its five URL cases are explicit and do not constitute a full-site sweep.

Meaningful error probes were run:

```sh
python3 source_inventory.py --page /not-a-real-tool.html
python3 source_inventory.py --root /Volumes/dual/DUALITY-ZERO-V2/experiments/web-personalization-20260908/audit/missing-root
```

Both returned exit 2 with a specific unknown-page or missing-workflow error. The full inventory returned exit 0 with 189/189 recognized maintained inclusions. Missing maintained inclusions return exit 1. Legacy omissions remain measured debt. The live sample returned exit 0 with no audit errors; this means its probes executed, not that every usability facet passed. Lost drafts and the unnamed Commons trigger remain explicit findings.

## Existing evaluations and the next concrete gate

The checkout has 40 `.mjs` scripts under `tools/toolkit-gates`. Searching the current `.github/workflows/*.yml` files found only `build-docsindex.mjs` referenced. Existing behavior tests are available; most of these browser gates are not enforced by those workflows.

Useful existing commands, **not run as part of this bounded audit**:

```sh
node tools/toolkit-gates/mobile-watertight.mjs https://mrdirno.github.io/nested-resonance-memory-archive/ --only=av/consumables.html
node tools/toolkit-gates/overlay-reachability.mjs https://mrdirno.github.io/nested-resonance-memory-archive/
```

Relevant source locations in the current checkout:

- `.github/workflows/deploy_bridge.yml:571` asserts toolkit runtime inclusion on trade hubs, rather than all tool pages.
- `.github/workflows/deploy_bridge.yml:795` describes feedback on every surface but its non-trade check names only current Collage.
- `shared/feedback.js:595` contains the modal open/close lifecycle; neither it nor the toolkit well stores unsent feedback drafts.
- `shared/toolkit.js:576` mounts the contextual tool-specific Wish button.
- `commons/index.html:99` requests a custom feedback trigger, implemented as the Add Gear control.

The next maintained-surface gate should use this inventory to select pages, then separately verify runtime loading, a named visible and reachable opener, the matching modal, and draft behavior. Source integration coverage can pass while any of those user-facing facets fail. Legacy coverage needs an explicit restoration policy rather than silently treating every archived study as an actively maintained product.
