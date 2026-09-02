# Does one epoch's structure seed the next? A pre-registered test of cross-epoch memory in the HALO resonance chamber

**Registered:** 2026-09-02 · **Author:** Aldrin Payopay <aldrin.gdf@gmail.com> · **Status:** FROZEN BEFORE DATA · **Instrument:** HELIOS-V501 (HALO), `HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html` · **License:** GPL-3.0

This is the first pre-registration in this archive. It is written and committed before the
confirmatory data exists. Every pilot run that informed it is listed in §4 with its numbers.

---

## 1. The claim, and what retires it

Nested resonance memory, as this project has stated it, says that the relics of one scale
seed the next. The chamber makes that testable: every 10 s the frame rescales by ½, the
matter of the closing epoch becomes a compact relic, and the same field equations organise
the next, larger scale. If the claim is true in its **strong (passive-relic) reading**, the
density at the end of epoch *k* should correlate with where epoch *k−1*'s relic predicts it,
by more than a relic from two epochs back predicts it.

There is a **weak reading** that no measurement here threatens: *a self-bound object persists
across rescalings*. A collapsed core scores on every relic, one epoch back or five. Only the
strong reading is under test.

**The criterion, fixed here:** a condition passes if Retained − Two-back exceeds **0.10 for
three consecutive scored epochs**. If no condition passes on data that survives the validity
gates of §7, the strong reading retires and the archive says so in the sentences listed in §10.

---

## 2. What is already known, and why the test is still worth running

A numerical port of this chamber, validated cell by cell against the page's own mesh
(potential correlation 0.99994, force 0.99995), measured the same index at 5,000 particles over
13 epochs and 4 seeds. Its paired excess of the memory index over the two-back relic was within
noise at every setting: the largest was +0.059 ± 0.198 (t = +1.9) at self-gravity 1.0, and at
the settings this test cares about it was −0.001 ± 0.030 (t = −0.2). Its excess over an
*independent-seed* relic was likewise ≈ 0 at low self-gravity.

That is a prior, not a result at the configuration the claim is made about. The port ran 5,000
particles with `smooth` off; the page's Spinning Chladni runs 4,169,000 with `smooth` on. Two
variables differ at once. The page's own first run, at 262,144 particles, read Retained 0.003
against Two-back 0.098 — a single epoch, no seeds, no controls. Neither settles the question.

---

## 3. The instrument, and the two defects this protocol works around

The Lab panel (key 7) reads the GPU back once a simulated second onto the chamber's own 32³
particle-mesh, and correlates the density now against the relic map kept at the last zoom-out.
One function does both arms (`labCorr`, line 5250): a Pearson correlation over a cubic block,
under an integer index remap, with no rotation search and no normalisation beyond the Pearson.

**Defect A — the two arms are not a matched pair.** `labCorr(rho, relic, f)` takes
`q = floor(16/f)`, so Retained (f = 2) is computed over the inner 16³ = **4096 cells** and
Two-back (f = 4) over the inner 8³ = **512 cells**. The footprints are correct for their own
relics — a relic two epochs back really has shrunk twice — but the two numbers carry different
sampling noise on different spatial support, so their difference is not a clean contrast.
*Handled:* a region-matched arm is computed alongside (Retained restricted to the same inner
8³ block, ×2 map), and §8 requires the matched arm to agree before a pass counts.

**Defect B — the displayed value is sampled at whatever moment the 1 Hz sampler last fired.**
`lab.retained` is written at the zoom-out from `lab.memory`, which was last computed up to one
simulated second earlier, so the displayed number can lag by an epoch. *Handled:* the
confirmatory estimator is the page's own `labCorr`, applied to the page's own density meshes,
evaluated at the exact end of every epoch (one tick before the zoom-out). This is the same
estimator with the sampling phase removed, not a different one. The displayed values are
recorded alongside as a cross-check.

**Not a defect, but stated so it is not mistaken for one:** there is no de-rotation anywhere in
the estimator. This test therefore asks a lab-frame question — *does the matter reappear where
the relic was?* — and not a rotation-marginalised one. A figure that reforms in a rotated
orientation would score zero here. That is a limit on what a null licenses, and §11 says so.

---

## 4. Pilots already run, disclosed in full

These were run before registration to establish that the experiment is possible and the
plumbing correct. None is at the confirmatory configuration; none is part of the confirmatory
dataset. Their numbers:

| pilot | configuration | result |
|---|---|---|
| throughput | 262k / 1M / 4.19M particles, tick budget 1 and 10, GPU and SwiftShader | GPU (ANGLE Metal, M4 Pro) at 4,194,304 particles and budget 10 runs at **3.4× real time**; SwiftShader at the same point runs at 0.131×. Timing only; no memory value was read. |
| tick-budget identity | 262,144 and 4,194,304 particles, Lab on, 200 ticks, seeded ICs | **max abs difference 0** across 786,432 position components between budget 1 and budget 10. |
| plumbing, 262k | Spinning Chladni, sg 0.3, gl 0, seed 999, 5 epochs | Retained −0.016 / −0.048 / (stale) / 0.194; Two-back −0.058 / 0.164; ceiling 0.003–0.164. Epochs 1–3 reproduced to full float precision in a second run of different length. |
| plumbing, 4.19M | Spinning Chladni, sg 0.3, gl 0, seed 999, 4 epochs | Retained −0.063, Two-back −0.098, ceiling 0.204. Deposit target **full float**; mass 4095.998 of 4096 expected; max cell 31,117 particles. |
| plumbing, default preset | shipped defaults, sg 0.3, gl 0, seed 999, 3 epochs, 262k | Retained 0.591, Two-back 0.325 — a difference of 0.27, above the criterion — with **ceiling share 1.000**. This is why §7 has a ceiling gate. |
| dry grid | Spinning Chladni, sg {0, 0.3}, gl 0, seeds {12345, 777}, 6 epochs, 262k | The independent-seed null tracked Retained closely (e.g. +0.108 against +0.108 at sg 0, and +0.201 against +0.162 at sg 0.3). |

---

## 5. The confirmatory design

Fixed here, and not to be changed without a recorded deviation (§13).

| | |
|---|---|
| particles | **4,194,304** (the page's maximum; `sanitizeState` clamps there) |
| presets | **Spinning Chladni** (the page's `spinchladni`, digit step 9028) and the page's **shipped defaults** (digit step 0) |
| self-gravity | **0, 0.15, 0.3, 0.5, 0.8** |
| gain/loss | **0, 0.5** |
| seeds | **12345, 777, 31337** (the port's own seeds) |
| epoch | **10 s**, cascade out, 24 epochs per run |
| integrator | as shipped: Euler magnetic step, 1 substep, fixed 1/20 s tick |
| runs | 2 × 5 × 2 × 3 = **60** |

Twenty-four epochs give 23 scored Retained values and **22 scored contrasts** per run (Retained
needs one prior relic, Two-back needs two), which satisfies the "at least 20 epochs" the
programme called for. Three seeds is the minimum that gives every run an independent-seed
partner while keeping the grid inside one session; it is fixed here so it cannot be extended
after seeing a near-miss.

Each run gets a **fresh page**: reusing one page for a second run does not reproduce it,
because `applyPreset` consumes random draws that depend on the state it starts from. Initial
conditions are drawn from a seeded linear congruential generator installed over `Math.random`
before the preset is applied, which makes a run reproducible tick for tick.

---

## 6. Estimators

All are the page's own `labCorr`, evaluated offline on the exported 32³ meshes. For epoch *k*
with density ρ_k (end of epoch, pre-rescale):

- **Retained_k** = corr(ρ_k, ρ_{k−1}) under the ×2 map, inner 16³ (n = 4096) — *primary arm*
- **Two-back_k** = corr(ρ_k, ρ_{k−2}) under the ×4 map, inner 8³ (n = 512) — *control arm*
- **Retained_k^M** = Retained restricted to the inner 8³ (n = 512) — *region-matched arm*
- **SeedNull_k** = corr(ρ_k, ρ'_{k−1}) where ρ' is an independent seed at the same epoch and
  the same settings — *the null: what the estimator reads when there is nothing to remember*
- **ShuffleNull_k** = corr(ρ_k, shuffled ρ_{k−1}) — *the floor of the estimator itself*

The contrasts: **Δ_k = Retained_k − Two-back_k** (the criterion as stated) and
**Δ_k^M = Retained_k^M − Two-back_k** (the same contrast with the footprint confound removed).

---

## 7. Validity gates, applied before any contrast is read

A run or condition that fails a gate cannot support a positive.

1. **Saturation.** The additive deposit stops counting at 2048 particles per cell in a
   half-float target, and cells at this particle count reach 31,117. Every run records the
   deposit target type and the total mesh mass; a run whose mass departs from
   *particles*/1024 by more than 1 part in 1,000 is **void**.
2. **Force ceiling.** A condition whose median ceiling share over scored epochs is **≥ 0.5** is
   **ceiling-bound**: its numbers measure the 500-unit force clamp, not the physics. It is
   reported, and it cannot support a positive.
3. **Undefined epochs.** An epoch whose inner 8³ block has zero variance yields no contrast. It
   is excluded and counted; a run with more than 4 such epochs is void.
4. **Page errors.** A run that logs a page error or console error is void.

---

## 8. The decision rule

Scored epochs are k = 3 … 24. For each of the 20 conditions and each of its 3 seeds:

- the cell **fires** if there exist three consecutive scored epochs with Δ > 0.10;
- the cell **fires-matched** if the same holds for Δ^M.

**POSITIVE** — the strong reading survives — requires all of:
(a) at least one condition fires in **≥ 2 of its 3 seeds**;
(b) that condition also **fires-matched** in ≥ 2 of 3 seeds;
(c) that condition is **not** ceiling-bound and has **no void** runs;
(d) the number of firing cells across the grid **exceeds** the number produced by the identical
rule applied to the SeedNull series, by a one-sided binomial test at p < 0.05 over the 60 cells.

**NULL** — the strong reading retires — if no condition satisfies (a)–(c).

**INCONCLUSIVE** if every condition satisfying (a) and (b) is ceiling-bound or void. An
inconclusive result is reported as inconclusive; it is not reported as a positive, and it does
not retire the claim either.

**False-positive calibration.** The rule in (d) is calibrated on this dataset, not assumed: the
identical three-in-a-row test is applied to SeedNull_k − Two-back_k, where there is by
construction nothing to remember. The fraction of cells that fire under that series is the
rule's empirical false-positive rate, and it is reported whatever the verdict.

No other analysis decides. Any further analysis is exploratory and labelled so.

---

## 9. Stopping rule

The grid is run once, to completion, at the sizes in §5. There is no interim look, no adding
seeds, no adding conditions, and no extending epochs. A run that fails a §7 gate is reported as
void and is **not** re-rolled with a different seed. If the machine fails mid-grid, the run
resumes at the cell that failed; cells already written are not re-run.

---

## 10. What the archive does with each outcome

**On a null.** The strong reading retires and these sentences change to the weak survivor, in
this commit's own follow-up: the Cosmos panel hint (`HELIOS-V501…html:781`, "earlier structure
persists as relics"), the About modal's Cosmos paragraph (:1760–1763), the About modal's phrase
"the memory the scale retained" (:1853–1860), and any README sentence that asserts one epoch
seeds the next. The Lab panel help (:1548–1563) already states the null and needs no change.
The honest survivor — *a self-bound object persists across rescalings* — is stated plainly in
its place, with the measured numbers beside it.

**On a positive.** It is the first evidence for the project's namesake claim in the project's
own vocabulary. It is reported with the condition, the seeds, the epochs, the ceiling share and
the null rate, and the next cycle attempts to break it: exact-rotation integrator, a second
machine, and a rotation-marginalised estimator.

**On inconclusive.** The reason is named (ceiling-bound, or void) and the next cycle changes
the integrator, not the analysis.

---

## 11. What this does not control

- **Rotation.** A figure that reforms rotated scores zero here (§3). A null licenses "no
  lab-frame cross-epoch memory", not "no memory in any frame".
- **One machine, one GPU.** All 60 runs are on one Apple M4 Pro under ANGLE Metal. The deposit
  target type is recorded per run so another machine's result is comparable, but no second
  machine is used.
- **The integrator.** The magnetic term is stepped as Euler, which is how every preset in this
  archive was found and which is known to inject energy. The exact-rotation step is not tested
  here.
- **The mesh.** 32³ cells. Structure finer than the cell is invisible to the index.
- **Sound, camera, overlays, and the Sacred-geometry fold** are off or irrelevant; the fold
  changes pixels only and is not on the instrument's path.

---

## 12. Reproduction

From a fresh clone, on a machine with a GPU that reports `EXT_color_buffer_float` and
`EXT_float_blend`:

```bash
cd tests/halo
npm init -y && npm i playwright@1 && npx playwright install chromium
python3 make_test_page.py                 # builds rc-test.html (git-ignored)
node memory_budget_identity.js --n=4194304 --lab   # must print PASS
bash memory_prereg_grid.sh                # 60 runs, about 90 minutes
python3 ../../experiments/halo/memory_prereg_analyze.py
```

Without a GPU the same grid runs under SwiftShader at 262,144 particles
(`N=262144 bash memory_prereg_grid.sh`), which is a different point in the space and is
reported as such, never as the confirmatory result.

The analysis reads only the exported meshes, so it can be re-run, and re-argued, without a GPU
and without re-running the chamber.

---

## 13. Deviations

Any departure from §5–§9 is recorded in this section, with the date, what changed, and why,
before the affected analysis is run. This section is empty at registration.
