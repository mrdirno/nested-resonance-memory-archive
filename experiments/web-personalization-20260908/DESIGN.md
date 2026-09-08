# A page of your own

Author: Aldrin Payopay · September 8, 2026 · GPL-3.0-only

This is a working local exploration and an implementation proposal for Persona500 and its independent tools. It is not a site-wide release, a Bifurcata integration, a visitor account service, or an AI deployment. The original branching study here contains no Bifurcata source. Public source audit and sampled live observations are recorded separately in `audit/`.

## The product decision

Let a visitor shape the presentation of a dependable tool. A few ordinary choices become a versioned recipe: color family, spacing, reading size, artwork, seed and theme mode. The same accepted recipe is rendered again on their next visit. People can explore a pattern, keep it, undo a change, reset their choices or carry a recipe to another browser.

This should feel like making a place comfortable, not completing a personality test. Offer a useful default immediately. Place optional preferences beside the work, or let an explicit action such as choosing an artwork become a preference. Say what is remembered. Do not infer identity, interests, location or sensitive attributes from passive browsing. A seed is a visual identifier, not a secret, user identity or authorization token.

The live preview has two real navigable views, an original seeded SVG instrument, a local writing desk with word/character counts, persistent presentation choices, recipe import/export, one-step undo, reset, and a sticky Wish opener. The Wish form preserves an unsent draft and its originating view/recipe locally; it explicitly says it does not send feedback. This deliberately does not impersonate the production wishing well.

## Design choices

The visual anchor is a branching form that visibly changes with the visitor's answers. Everything around it stays quiet and legible. This makes the generator the demonstration, rather than a dashboard describing generation.

Initial tokens: mist `#edf3f6`, paper `#f8fbfc`, ink `#18343e`, tide `#155879`, blue wash `#d6e6ee`, plum `#865271`. Night uses navy `#101f2c`, blue panel `#192e3d`, pale text `#e3eef3` and accent `#9adaf3`. Orchard and Mineral each have authored day/night pairs. Georgia carries the large invitation; the system sans carries controls and reading. Content is left aligned with a bounded reading measure.

```
sticky identity                         Wish it better
local preview status
preferences        Explore | Writing desk     day/night
                   invitation      generated artwork
                   existing tools / actual writing area
```

The initial generic card-grid idea was discarded: preferences remain in a control rail and the artwork occupies a single open field. There is no auto-running animation, so reduced-motion users receive the same useful experience. On narrow screens the choices stack above the preview and the Wish control remains in the sticky header.

## Recipe and determinism

`engine.mjs` owns the strict recipe schema and canonical answer-to-seed mapping. It rejects unknown fields, unsupported versions and invalid values. No imported value can become HTML, CSS, JavaScript, a selector or an external URL. The UI renders only authored tokens and bounded SVG attributes.

1. Explicit enumerated answers are encoded in a fixed order and hashed with FNV-1a into a uint32 seed.
2. A fresh specified LCG generates the same branch geometry for that seed. It never replaces `Math.random` globally.
3. The full accepted recipe is saved under its own versioned browser key. A seed alone cannot reconstruct settings or future engine revisions.
4. A clock change resolves the theme; it does not regenerate the seed. Rendering geometry is repeatable, while rasterization and fonts can differ across browsers.
5. Unknown future recipes leave the current usable page intact. File reads have a 16 KB limit and cannot overwrite an intervening preference change.

The current recipe engine identifier is `branch-study-v1`; its schema also permits the original orbit motif and a quiet presentation. A production schema should distinguish each renderer version explicitly when it adds or changes renderers.

The preview synchronizes recipe changes between tabs. Writing and Wish drafts intentionally do not synchronize across simultaneous editors; that needs conflict handling before multi-tab editing is promised. Local saving survives ordinary navigation/reload on the same origin. Clearing browser storage removes it. A new host, protocol or port has a different local store. Storage failures leave controls usable and offer file export rather than falsely reporting a save.

## Time-following dark mode

Default proposal: **Follow local time**, light from 07:00 inclusive to 19:00 exclusive. Also offer **Follow my device**, **Always light**, and **Always dark**. Device preference is a separate signal from wall-clock time; [`prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-color-scheme) reports the user's system appearance, not sunrise or sunset.

The preview evaluates the next local boundary, rechecks once a minute while active for clock/time-zone changes, and refreshes on focus, visibility and page restoration. This is a simple schedule, not an astronomical sunset calculation. It requires no geolocation.

Production precedence: explicit page/accessibility override, saved visitor preference, then the default schedule. Keep the reading room's paper/sepia/night choices explicit. Convert page chrome to semantic surface/text/border/accent tokens. Never invert a whole canvas or remap meaningful game/scientific colors. The theme must be resolved before the first visible paint in the eventual production bootstrap; this local module preview does not certify that guarantee.

## What the source audit found

Source snapshots inspected: NRM `042ce6b9938d2539e4eff9b29dff33b430a0ce22`; Persona500 `1bb38f1febfccc4868a9fcc35db3d2d145e36a09`. The Persona500 checkout had unrelated ongoing changes and was left untouched.

| Area | Existing seam | Gap / implication |
| --- | --- | --- |
| React Wish | `src/App.tsx`, `WishThisPage.tsx`, `ArcadeGameBar.tsx`; Society owns a native well | A React global mount cannot cover standalone HTML. The React wish close handler also discards a half-written draft. |
| Static pages | Persona500 `server.py` serves public files directly | Need a shared static adapter and an artifact-derived inventory; do not equate a literal source reference with a working live button. |
| NRM tools | 184 trade HTML pages load toolkit runtime; 3 Commons pages load feedback | Existing deployment assertions cover hubs/current Collage entry, not every interaction on every page. Sampled AV, Commons and Collage drafts vanished after reload. |
| Tool evaluation | Many existing `tools/toolkit-gates/*.mjs` behavior checks | Most are not wired into workflow files. Reuse and enforce the checks that actually exercise the changed surface. |
| Game evaluation | `public/games/_shared/cycle_eval.mjs` | Source fingerprint/LOC changes are called behavioral change; the advertised smoke run is absent from `main()`. History paths still use `games/` instead of `public/games/`; missing history can become `NEW`. This is not proof of improved gameplay. |
| Theme | Workshop tokens plus page-specific palettes; reader preference helper | One root dark token set and hardcoded page colors need deliberate per-surface migration. |
| Bifurcata | Strict URL parser and `applyAddress()` for world/fold/crop/depth | Reuse its address seam and preserve the embedded growth engine. Its existing eval records explicitly limit determinism because forest baking retains a wall-clock cap. |
| Accounts | Existing authentication; reader preferences stored locally | `/api/profile` is a singleton operator profile, not a visitor preference store. |
| Gavel | A generated `GavelPage.tsx` article exists | This is not evidence of an available runtime agent integration. No Gavel dispatch occurred here. |

The [Bifurcata evaluation record](https://persona500.com/bifurcata/evals.json) is a useful existing pattern: paired runs, a held-out world, source hashes and specific measurement caveats. Its source receipt was inspected here; those historical performance numbers were not rerun by this study.

The [game evaluator falsifier](game-eval-audit/README.md) actually ran the inspected legacy fingerprint function: appending only comments/blank lines changed its fingerprint while a three-press fixture still returned `[1,2,3]`. A real tracked game's fingerprint also changed with every measured field except line count identical. Read-only Git calls confirmed the legacy history path fails while the correct `public/games/` path succeeds. Missing or changed evidence returns an error. This falsifies the metric as evidence of improvement; it does not assess the game's health.

## Make Wish a release invariant

Treat these as separate requirements so one cannot hide another:

- **Presence:** each actual published HTML route has one clearly named, keyboard/touch-reachable Wish entry in normal, scrolled, editing and immersive states. A hidden DOM node or loaded script does not pass.
- **Context:** opening preserves the page, active tool and relevant public version/recipe. Do not attach user document contents, authentication data, private URL queries or passive browsing history.
- **Draft durability:** close/reopen, reload and returning to a page restore unsent text without assigning it to the wrong page. Account changes must not leak one person's draft to another.
- **Delivery:** only a real server acknowledgment creates a sent state. Offline drafts remain labeled drafts. Automated tests intercept submission; they never create junk in the live well.

Build the coverage manifest from the exact deployment artifact and its real route list. React, standalone HTML, trade shells, Collage and HALO each need an adapter. Preserve historical source byte-for-byte where necessary and add presentation chrome at artifact assembly with recorded provenance. Mark exceptions explicitly; “every page” is not true while untested/excluded published pages remain.

Use existing mobile and overlay gates, extend to the actual full page inventory, and fail when a previously covered page loses its opener or dialog. Large inventories can shard across CI workers; a representative live sample is additional deployment evidence, not full coverage. Keep the coverage report's unknown count visible.

## How existing games and tools evolve

Start with one real wish on an existing surface, not another new catalog entry. Give it a browser task and a measured baseline before changing implementation.

| Evidence | Example for a tool | Example for a game |
| --- | --- | --- |
| Correctness | Known input gives expected result; export/reopen preserves it | Start, input, score, win/loss, restart and saved progress behave correctly |
| Usability | Finish the task at 320/390 px and with keyboard | Explain controls, start a round, make meaningful input, pause and restart on touch/keyboard |
| Change benefit | Previously clipped action becomes reachable; fewer measured failed steps | Previously broken action works; a stated mechanic is demonstrated in the running game |
| Regression protection | Theme/personalization leaves calculations and documents unchanged | Presentation changes leave scoring, timing and saved state unchanged |
| Preference evidence | Optional “keep this / undo” after a change | Observed play feedback, not a source-code novelty score |

Record: surface ID, owner/accepted lane, source and deployed version, exact task, fixture/seed, device, expected/observed result, failure evidence, dated receipt and next unresolved issue. Missing, stale, failed and passed are distinct states. A new source version invalidates unsupported old claims. A source fingerprint is useful for finding changed files; it must not be called an improvement evaluator.

Proposed division for the shared effort: the site shell owns global preferences and Wish coverage; each tool/game owner owns functional checks and its adapter; an independent reviewer runs the acceptance journey and checks the receipt. These are proposed responsibilities, not claims that anyone has accepted a handoff. Use the existing coordination authority rather than creating a second task queue. No maintenance automation or messages to other teams were created by this exploration.

Judge-model ratings should be advisory until calibrated against labeled examples. Require held-out tasks/seeds when claiming a tuned change improves results. User feedback remains useful evidence; engagement alone does not establish usefulness.

## Optional DeepSeek interpretation

The zero-call path should always work: a visitor makes explicit choices, and the deterministic engine maps them. A visitor who writes “more space, larger text, ocean colors” can optionally ask a model to propose those same allowed fields. [`DeepSeek JSON Output`](https://api-docs.deepseek.com/guides/json_mode/) supports structured JSON generation; valid JSON alone is not a valid or safe recipe.

The application must validate a small answer schema, derive the seed itself, show the result, and save the accepted recipe. Model output is not guaranteed deterministic; the accepted versioned recipe is the replay boundary. Do not call the model on each render. Keep API keys server-side, use the existing provider routing layer, bound input/output/rate/cost, and fall back to the explicit controls. Send only text deliberately submitted for personalization; this study makes no provider calls and quotes no unverified pricing.

Model authority ends at proposing presentation values. It cannot modify code, arbitrary CSS, routes, links, login, permissions, payments, exports, game rules or scientific settings. An assistant or Gavel can help design and review adapters once its actual integration is established; it should not be a prerequisite for a visitor to use a page.

## Login persistence and rollout

A production visitor-preference record needs authenticated ownership, a schema version, an engine version, validated recipe data and a revision for conflict detection. Read/write authorization must use the authenticated session, never a user ID supplied by the model or form. Preserve local anonymous choices at sign-in and offer a clear choice if the account has different saved preferences. Clear account-bound cache at sign-out; test two accounts and concurrent devices. Avoid reusing `/api/profile`.

The first production slice should be the common Wish coverage/draft contract plus theme tokens on one existing tool and the site shell, with a Bifurcata address adapter in the Persona500 proprietary source. Release in independently reversible stages, then migrate remaining pages against the inventory. Account sync and optional model interpretation follow those browser gates. Do not declare universal coverage, adoption or gameplay improvement from this preview.

## Run and review

Serve this directory over localhost so browser modules and origin storage behave normally:

```sh
python3 -m http.server 8768 --bind 127.0.0.1
node --test engine.test.mjs
```

Open `http://127.0.0.1:8768/`, change the page, open Writing desk, type, reload, and open Wish. Save/open a recipe and try both explicit theme modes. See `browser.test.mjs` and `evidence/` for automated browser validation and its limits. On this Mac run multi-second suites through the repository's `automation/run_background.py` as required by the workspace protocol.
