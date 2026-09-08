# Persistent, personal pages: working study

Author: Aldrin Payopay · September 8, 2026 · GPL-3.0-only

This local preview turns explicit presentation choices into a saved, versioned recipe. It demonstrates time-following themes, deterministic original artwork, two navigable views, persistent writing and Wish drafts, import/export, undo and reset. It also records current Wish coverage gaps and an executable counterexample to a legacy game-evaluation metric.

**Production status:** no live site pages were changed. No login sync, DeepSeek calls, Gavel integration, live Wish submission or Bifurcata engine integration is implemented by this study. Its source can be shared in the research repository without adding another public tool to the site's catalog.

- [Implementation proposal and rollout](DESIGN.md)
- [Wish inventory and five live samples](audit/README.md)
- [Game evaluator falsifier](game-eval-audit/README.md)
- [Browser acceptance receipt](evidence/receipt.json)
- [320px preview](evidence/visual-top-light-320.png)
- [390px night preview](evidence/visual-top-dark-390.png)
- [Desktop preview](evidence/visual-top-light-1280.png)

## Try it

From this directory, serve the files and open `http://127.0.0.1:8768/`:

```sh
python3 -m http.server 8768 --bind 127.0.0.1
```

Change a palette, choose Light & dark, visit Writing desk, type and reload. Open Wish, write a draft, close it and return. Choose **Your page recipe** to save/open a JSON recipe or set a pattern number. Wishes are saved locally and can be exported; they are never sent to a team by this preview.

The runtime has no package dependencies or remote assets. A consistent localhost port matters because browser storage is origin-scoped. On this Mac the server was launched through `automation/run_background.py` from the development workspace, as required for persistent processes.

## Validation

`node --test engine.test.mjs` passed **15/15** tests: strict schema, frozen recipe/geometry vectors, all 36 answer combinations, held-out seed reproduction, malformed input and exact local-time boundaries.

The final [browser run](evidence/receipt.json), `2026-09-08T13-09-10-804Z`, passed **12/12 groups**, with **54 layout observations** and **54 computed contrast pairs**. It used isolated Chromium 145 contexts through Playwright 1.58.2 at 320, 390 and 1280 pixels. Source hashes matched at start and end. No external network requests or uncaught browser errors occurred. The lowest measured ordinary text/control-boundary contrast was **5.347:1**. This is a bounded contrast check, not a full accessibility certification or physical-device test.

Tests cover actual navigation/reload, recipe and writing persistence, mode changes, clock boundaries without reload, modal keyboard behavior, draft context, rejected imports, export bytes, storage failure and cross-tab preference updates. They do not test production login, provider output, another browser engine or every existing website route.

Earlier receipts remain dated, including test-harness timing mistakes, the actual Quiet SVG visibility bug, and insufficient control-border contrast. The Quiet fix uses an SVG `hidden` attribute; functional controls now have stronger edges than decorative dividers. Selected option labels were shortened after an actual 320px visual check showed clipping. Final screenshots include those fixes.

For browser checks, reuse an installed Playwright package:

```sh
PAGE_STUDY_PLAYWRIGHT_ROOT=/absolute/path/to/package-root node browser.test.mjs
```

Without the variable, the test resolves `tools/collage-studio` relative to the repository. On this Mac it was run with `/Volumes/dual/persona500` and launched through `automation/run_background.py`. The test refuses a non-local base URL. `PAGE_STUDY_URL` can select another localhost port.

The source-inclusion audit recognizes **189 maintained source files**, mapping to **190 HTML paths**. This proves inclusion patterns only. The five live samples separately show lost drafts on reload in AV, Commons and current Collage, and missing named Wish controls on sampled legacy pages. The game falsifier reproduced a comment-only fingerprint change with unchanged fixture behavior; its three error controls reject missing/unknown/changed evaluator evidence. None of these results establishes site-wide coverage or game improvement.
