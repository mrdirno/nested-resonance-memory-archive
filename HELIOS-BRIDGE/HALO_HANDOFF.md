# HALO — Helios Bridge iteration V501 · handoff for Claude Code on macOS

**Code name:** HALO (Helios Adaptive Lab Object). **Artifact:** `chamber/HELIOS-V501-halo-resonance-chamber.html`,
a single self-contained page (three.js from cdnjs, no build step, ~290 KB) — the Resonance Chamber at Ring 9.
**Live reference copy:** https://claude.ai/code/artifact/f81a4b50-694b-4580-9755-7639a4f001d0
**Repository target:** `mrdirno/nested-resonance-memory-archive`, the Helios Bridge live pages
(https://mrdirno.github.io/nested-resonance-memory-archive/).
**Author of record:** Aldrin Payopay <aldrin.gdf@gmail.com>. Commits carry exactly one author and no AI
co-author trailers (repo `CLAUDE.md`, Zero-Leak and attribution sections). AI assistance is disclosed in
`ACKNOWLEDGMENTS.md`, nowhere else.

Nothing in this package was pushed. Integrate it from your machine so the commits are yours.

---

## 1. What HALO is, in one paragraph

A GPU particle laboratory (up to 4.19 M particles) in which the eigenmodes of a spherical cavity are
sequenced by the digits of π, e, √2 and φ, with self-gravity (particle-mesh Poisson), structured gain/loss,
an expanding background with epochs, a magnetic term, and a SoundHack sonification bridge. Ring 9 turned it
from a visualizer into an instrument: the physics runs on a fixed 1/20 s tick on every machine with interpolated
rendering (a preset now means the same thing at 30 Hz and 120 Hz); the magnetic term can be stepped as Euler
(how every preset was found) or as the exact Boris rotation; a Lab panel measures the chamber against its own
claims — a Benettin Lyapunov meter that ignores wall kicks and reports the share of particles on the force
ceiling, a cross-epoch memory index with its two-back control beside it, a realized spherical-harmonic spectrum,
a CSV log — and three one-click experiments load a measured claim with the instruments on. Every claim in the
page's hints was measured on the page or in a numpy port validated cell-by-cell against the page's own GPU mesh,
and the ones that failed are labelled as such (see §3).

## 2. Package contents

```
HANDOFF.md                         this file
chamber/HELIOS-V501-halo-resonance-chamber.html   the artifact (rings 1–9 sealed in a comment at the end)
chamber/tests/                     headless Playwright suite (mk_test.py builds rc-test.html with a probe bridge — NEVER ship rc-test.html)
chamber/patches/                   the write-at-end patch scripts that produced rings 8–9 (provenance only)
chamber/shots/                     screenshots of the Lab panel and experiments
choreography/choreo4.py            four-charge Z4 choreography: Boris step, exact tangent map, Newton shooting, Floquet, 1e6-cycle run
choreography/final_spec.log        the run under the task's specification (no non-planar orbit exists: proved and witnessed)
choreography/final_extension.log   the run with an axial spring: a 3-D choreography, 24/24 multipliers on the unit circle, 7e-5 over 1e6 cycles
rings/ring8.txt, ring9_final.txt   the sealed ring texts; ring9_notes.txt = raw worker findings with numbers
workers/numpy-ports/               port2.py (GPU-validated to 2e-3), jeans_*.py, disc_*.py, memory_*.py — the falsifiers, rerunnable
workers/results/                   their JSON outputs (thresholds, ladders, Floquet controls, memory nulls)
```

## 3. What Ring 9 found (the honest list; details and numbers in rings/ring9_final.txt)

1. **Rotational support, not Jeans.** The self-gravity threshold does not move with the expansion rate
   (log-log slope 0.07 ± 0.06 over a factor 8); it is centrifugal balance of the 6·helix/damping spin
   (predicted 0.495, page 0.45 holds / 0.6 folds at hubble 0.3 and 1.2 alike; helix 1.2: 0.55 holds / 0.75 folds).
2. **Memory across epochs: a null at low self-gravity.** Retained memory at self-gravity 0/0.15/0.3 is within
   noise of the shuffle, two-back and independent-seed nulls; it rises only where the swarm is self-bound, and
   there the two-back relic scores equal or better — persistence of a collapsed object, not imprinting.
   The instrument now shows Two-back beside Retained (page first run: 0.003 vs 0.098).
3. **The Razor Disc is the integrator's.** Its speed is 500·√(dt/2γ) (predicted 88, measured 86), it exists
   where coupling²·dt > damping/55, and under exact rotation the same settings pile matter at the poles.
4. **The user's own Spinning Chladni is real physics with a borrowed speed.** With the magnetic coupling at zero
   the figure stands and streams at 38; at 0.4 under Euler it streams at 57 because the explicit Lorentz kick
   injects 30–37% of the damping loss; under exact rotation at 0.4 it goes to the poles; at 0.3 under exact
   rotation the figure returns (7.1 / 13.0 / 35.5 measured vs 7.6 / 13.0 / 33 predicted). Shipped as the family
   preset **Spinning Chladni, exact**. The mechanism is a cyclotron resonance (gyration 4.2 rad/s against a
   4.8 rad/s drive) where a small residual decides poles vs streaming.
5. **Numerical floors made visible:** the 500 force ceiling sizes every collapsed core (more substeps shrink it
   toward the mesh cell); a half-float additive deposit stops counting at 2048 particles per cell (now float
   where the GPU can blend float); the sim step used to depend on the viewer's refresh rate (now fixed).

## 4. Integration into the Helios Bridge live pages

See §4a for the deploy facts as read from the repository on 2026-09-02, then follow the steps.

### 4a. Deploy facts (from `.github/workflows/deploy_bridge.yml`)
- One Pages artifact is built from `HELIOS-BRIDGE/dist` (Vite app) and everything else is copied INTO that dist:
  `HELIOS-BRIDGE-ARCHIVE/.` → `/archive/`, `collage-beta/.` → `/collage-beta/`, `shared/.` → `/shared/`,
  each trade dir → `/<trade>/`, `commons/.` → `/commons/`.
- Deploys run on push to **main** when a listed path changes (`HELIOS-BRIDGE/**`, `HELIOS-BRIDGE-ARCHIVE/**`, …).
  A file outside those paths never reaches Pages.
- The archive holds **500** generated variations, `HELIOS-V001` … `HELIOS-V500` (50 palettes × 10 sequences ×
  10 force fields × 10 behaviors × 10 UI themes, curated), plus `MANIFEST.json`, `index.html` (the gallery, which
  inlines the manifest as a JS constant and filters by force field), `endless.html`, and `README.md`. All three
  generated files are written by `generate_500_variations.mjs` at the repo root — hand edits to `index.html` are
  lost if it is ever regenerated, so HALO is registered outside the 5-axis manifest, as a "beyond the 500" entry.
- HALO is **V501**; the file name in this package follows the archive's `HELIOS-V{NNN}-{name}.html` pattern and
  is already on the branch at `HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html`.

### 4b. Steps (each one a commit you make locally; verify before the next)
1. `git checkout main && git pull`, then confirm `git config user.name` / `user.email` are Aldrin's.
2. Copy `chamber/HELIOS-V501-halo-resonance-chamber.html` to `HELIOS-BRIDGE-ARCHIVE/`.
   Open it locally in a browser first (any static server; the page only needs cdnjs). Press 7 for the Lab.
3. Register it in the archive gallery without touching the generated manifest: add one card above the grid in
   `HELIOS-BRIDGE-ARCHIVE/index.html` (right after the `<div class="toolbar">…</div>` block) AND the same
   markup in the index template inside `generate_500_variations.mjs`, so a regeneration keeps it:
   ```html
   <a class="card halo" href="HELIOS-V501-halo-resonance-chamber.html">
     <div class="card-title">V501 · HALO — Resonance Chamber, Ring 9</div>
     <div class="card-meta">Beyond the 500: a laboratory that measures its own claims — fixed tick, exact or Euler magnetic step, Lyapunov, memory with its control, spectrum. Press 7.</div>
   </a>
   ```
   (Reuse the gallery's existing `.card` styles; `.halo` only needs a border color.) The archive `README.md`
   already carries a "Beyond the 500" section on this branch. The bridge app itself (`HELIOS-BRIDGE/App.tsx`) has
   no version list to extend; the archive is reached from the app's archive link. Direct URL after deploy:
   `https://mrdirno.github.io/nested-resonance-memory-archive/archive/HELIOS-V501-halo-resonance-chamber.html`.
4. README, under "THE BRIDGE (Live Interface)": one line, offer not shove, under the existing entry, e.g.
   *"Newest iteration: HALO (V501) — a particle laboratory that measures its own claims: [open](…/archive/HELIOS-V501-halo-resonance-chamber.html)."*
   No claim inflation: the page presents hypotheses as tests, and two of its own claims are labelled failed.
5. `CYCLE_LOGS.md` (and `META_OBJECTIVES.md` if the cycle convention asks): one entry in the existing format
   naming V501/HALO, the fixed tick, the Lab, and the four findings of §3 with their numbers.
6. `python3 automation/scripts/cleanup_repo.py` (root hygiene), `git status` review — no `fabrication/`, no
   `*.stl/*.obj/*.gcode/*.3mf`, no `rc-test.html`, no secrets — then commit and push to main.
   The deploy workflow triggers on the archive path; check the Actions run and the live URL.
7. Optional, same discipline: `choreography/choreo4.py` and its two logs belong under `src/experiments/`
   or `analysis/` as a reproducible experiment (numpy; numba optional), with a `CYCLE_LOGS.md` line.

### 4c. What NOT to do
- Do not add `Co-Authored-By:` trailers naming AI tools (repo `CLAUDE.md`; it hurt attribution before).
- Do not ship `chamber/tests/rc-test.html` or anything with `window.__probe` — test-only bridge.
- Do not "fix" the Euler magnetic step by making exact rotation the default: nine shared presets were found
  under Euler and are labelled; the exact step is a choice, and the exact sibling preset exists for the user's state.
- Do not rewrite or delete any ring text; rings are append-only.

## 5. Running the tests on macOS

```
cd chamber/tests
npm init -y >/dev/null && npm i playwright@1 && npx playwright install chromium
python3 mk_test.py                  # builds rc-test.html from ../HELIOS-V501-halo-resonance-chamber.html (three.min.js is included here)
node tick_test.js                   # fixed tick, interpolation, Boris toggle, float deposit — 13 checks, ~2 min
node lab_test.js                    # instruments in three regimes — 26 checks, ~8 min
node smoke.js                       # the whole UI — 95 checks, ~6 min
```
The suite was written for headless SwiftShader; on a real GPU it runs faster and the same numbers should
reproduce because the physics tick is fixed. `mk_test.py` swaps the cdnjs three.js tag for the local
`three.min.js` shipped beside it and appends a `window.__probe` bridge; `rc-test.html` is a test build only.

```
cd choreography
pip install numpy numba
python3 choreo4.py --quick --N 128          # 35 s: every layer except the 1e6-cycle run
python3 choreo4.py --N 256                  # 95 s: the specification as written
python3 choreo4.py --N 256 --kz 1.0         # 95 s: the extension (axial spring) — the 3-D choreography
```

## 6. Continuing the loop cycles (BUILD · BRANCH · BAN · BREAK · SHIP v2.1)

Each cycle: ban the obvious answer first, branch the searches to workers who report *what I found / how
sure / what would prove it wrong*, break the result on the page before shipping, ship a working artifact,
report in one paragraph, and append a new ring (never edit an old one). Ring 10 candidates, in order of
information per hour:

1. **The 0.2 floor.** Vary the mesh box and drop the mean subtraction in `workers/numpy-ports/jeans_pm.py`;
   if the helix-0 threshold moves, the Jeans swindle is a wall of its own here (a box-shaped bias a
   periodic cosmological code hides). Falsifier ready-made in the port.
2. **Memory at 4 M particles.** Run the Lab's memory experiment on a real GPU for 20+ epochs at
   self-gravity 0.15 / 0.3 / 0.5 and export the CSV: Retained must clear Two-back by > 0.1 for several
   epochs running to give the claim a leg. Nothing so far does.
3. **The nine coupling ≥ 0.6 presets under exact rotation.** Which survive, what the exact physics puts in
   their place; ship the survivors as "…, exact" siblings the way Spinning Chladni got one.
4. **Ω² scaling of the threshold** on the page (helix and damping both move Ω); the port predicts it, the
   page has only the endpoints.
5. **A 64³ mesh** (halves the floor under a collapsed core, doubles the Poisson cost) and a strobe test of
   the interpolated renderer against the raw ticks.
6. **Choreography:** a zero-mean-drive Z4 family near the Bessel zeros of the free motion
   (qB0/(mω) = 2.4048, 5.52); the induced electric field the specification omits; a transverse field
   component in place of the spring.

## 7. State of the art: where this stands, honestly

What is at or past the current practice: an in-browser GPU particle-mesh N-body with a fixed reproducible
tick, twin-particle Lyapunov measurement inside the shader, a memory index shipped with its own null, an
exact Boris option beside the Euler step with the difference measured and explained (a cyclotron-resonance
residual), and every headline claim carried with the number that could kill it. The choreography script
proves two impossibility theorems the task assumed away and then delivers the object in the nearest model
that can hold it, with all five verification layers met.

What is not yet there: the memory claim has no positive result anywhere; the collapse physics is bounded by a
force ceiling and a 32³ mesh; the chamber's magnetic model omits the induced electric field a time-varying B
requires; and no result has been checked by anyone outside this loop. The next level is not more features —
it is a positive, pre-registered result on the memory claim at full particle count, or its retirement.
