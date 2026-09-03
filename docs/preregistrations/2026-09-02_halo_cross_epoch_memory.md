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
# The recovered builder resolves the repo from its own directory, so write it
# INTO tests/halo; run from /tmp it dies with CalledProcessError. Verified 2026-09-03
# by rebuilding the instrument bit-exactly to the checksum below.
git show 5cb08e51:tests/halo/make_test_page.py > _mtp_5cb08e51.py
python3 _mtp_5cb08e51.py --from-git 5cb08e51   # THE instrument; see below
md5 rc-test.html   # must read e91d5a1d44a1dde519195e4e925fa515  (343,524 bytes)
node memory_budget_identity.js --n=4194304 --lab   # must print PASS
bash memory_prereg_grid.sh                # 60 runs, about 90 minutes
python3 ../../experiments/halo/memory_prereg_analyze.py
```

**This block was wrong when it was written, and the correction is recorded in §13.** It said
`python3 make_test_page.py --from-git HEAD`. `HEAD` moves, and it has: the confirmatory runs
were measured on the page as of commit `5cb08e51`, and today's `make_test_page.py` cannot
rebuild that page at all — it would produce one that throws on load. The instrument is pinned
above by both revision and checksum, so a reader can tell whether they have it before spending
ninety minutes finding out they do not.

Without a GPU the same grid runs under SwiftShader at 262,144 particles
(`N=262144 bash memory_prereg_grid.sh`). Measured on this machine: 4 epochs in 25 s, so a
24-epoch run is about 150 s and the 60-run grid about 2.5 hours on CPU alone. SwiftShader also
reports `EXT_float_blend`, so the deposit target is full float there too and the saturation gate
of §7 passes on the software path — but 262,144 particles is a different point in the space and
is reported as such, never as the confirmatory result.

The analysis reads only the exported meshes, so it can be re-run, and re-argued, without a GPU
and without re-running the chamber.

---

## 13. Deviations

Any departure from §5–§9 is recorded in this section, with the date, what changed, and why,
before the affected analysis is run.

**2026-09-02, after registration, before any confirmatory analysis was run — an addition, not
a departure.** A positive control was added to §6 as a diagnostic: **Recurrence_k**, the same
correlation between ρ_k and ρ_{k−1} with *no rescale map at all* (map factor 1, the full mesh),
together with its own independent-seed null. It answers the one question a null cannot answer
on its own: *can this estimator see a spatial correlation when one is certainly present?* If
Recurrence is near zero, a null on Retained means only that the instrument is blind, and the
verdict would be uninterpretable. Recurrence does **not** enter the decision rule of §8 and
cannot cause a pass or a failure; the rule is unchanged. The reason for adding it after
registration is that it was requested by an adversarial reading of §3's rotation caveat, and it
costs no new data — it is computed from meshes the protocol already exports.

**2026-09-02, during data collection — the grid was restarted from zero, and why.** The first
26 runs were discarded and the grid re-run. Cause: `make_test_page.py` built the headless test
page from the *working tree*, which at the time carried another lane's uncommitted
`<script src="/nested-resonance-memory-archive/shared/feedback.js">`. Under `file://` that path
does not resolve, so Chromium logged one console error — `net::ERR_FILE_NOT_FOUND` — in every
run. Gate 4 of §7 voids a run that logs a console error, so **every run was void**, on a
resource that touches nothing in the physics or the instruments.

The gate was **not** weakened. The defect was one layer down and was fixed there:
`make_test_page.py` gained `--from-git <rev>`, so the confirmatory grid is built from a named
commit rather than from whatever happens to be in the tree — which an experiment needs anyway
to be reproducible by anyone else. `memory_prereg_grid.sh` now aborts on the first run that
logs an error, instead of discovering after sixty runs that all of them are void. A clean boot
was verified to log zero errors before the restart.

The 26 discarded runs are kept, not deleted, under `data/results/halo/memory_prereg_voided/`.
**Nothing in §5–§9 changed:** same grid, same seeds, same estimators, same gates, same decision
rule. The cost was about 35 minutes of machine time and the benefit is that no reader has to
take on trust that a logged error was harmless.

**Also recorded, for the reader's benefit:** in the 262k dry-run pilot of §4 this control read
+0.50 to +0.85 while its own independent-seed null read the same value to three decimals. That
is a pilot at a different particle count and is not the confirmatory result.

**2026-09-03, before the confirmatory analysis was run — the grid was resumed, and the
instrument it was resumed on was pinned.** Collection stopped on 2026-09-02 with 28 of the 60
cells written and one mesh half-written. §9 provides for exactly this: *"If the machine fails
mid-grid, the run resumes at the cell that failed; cells already written are not re-run."* The
grid was resumed on 2026-09-03 and ran the remaining cells. No seed, condition, epoch count or
estimator changed, and no completed cell was re-run.

Resuming a grid a day later only means anything if the second half was measured on the same
instrument as the first, so that was established before the resume rather than asserted after
it. The instrument is `tests/halo/rc-test.html`, **md5 `e91d5a1d44a1dde519195e4e925fa515`,
343,524 bytes**. It was checksummed before the resume, polled every 20 s throughout it, and
checksummed again at the end; it never changed. It is git-ignored, so the checksum is the only
thing that identifies it, and §12's instructions did not reproduce it:

- Exactly one pair of revisions rebuilds it byte for byte, out of 45 pairs tried:
  `make_test_page.py` at `5cb08e51` (the blob at `a30ada56` gives identical output) applied to
  the page blob `809c4cd1`, which is the HALO page at both of those commits.
- §12's literal command, `--from-git HEAD`, builds a different page — 508,750 bytes today.
- Worse, **today's `make_test_page.py` cannot rebuild the run-time instrument at any revision.**
  At `122d0a57` it gained a probe bridge that eagerly names 16 identifiers (`pmDeposit`,
  `syncPm`, `DIMER`, `consRT`, `fieldAmp`, …) which do not exist in the run-time page. The
  object literal evaluates them on load, so the page would throw a `ReferenceError` and every
  run would be void under §7 gate 4. A reader following §12 would not have got a wrong number;
  they would have got sixty void runs.
- The page itself moved after the runs. Every measured-path change lands at ring 13
  (`122d0a57`): `labReadDensity`, `simTick`, `pmSolve`, `DEFAULTS`, `sanitizeState`, `labTick`
  and the velocity shader all changed there, each guarded so the shipped defaults take the old
  path. The estimator §6 rests on, `labCorr`, is byte-identical across every revision from the
  run-time blob to HEAD, as are `simStep`, `applyPreset`, `cavityForce`, `TICK = 1/20`, the
  500-unit force clamp and the Spinning Chladni scenario at step 9028. Guarded-equivalent is
  not measured-equivalent — the GLSL text differs, so the compiled program differs — which is
  why the runs stayed on the pinned build instead of a rebuild.

Two further facts a reader is entitled to. **The run schema records no instrument identity.**
`halo-memory-prereg/1` stores the GPU, the caps and the applied state, but no revision and no
checksum, so nothing inside the data binds these runs to the page that produced them; the
checksum above is recorded here because the schema cannot carry it, and changing the schema
mid-grid would have been a deviation from §5. And the file's timestamp, the only other link,
was overwritten at 09:21:57 on 2026-09-03 — by the provenance check itself, which copied the
identical bytes back over the file while testing candidate rebuilds. The content was
checksummed before and after and is unchanged; the mtime is no longer evidence of anything.

§12 has been corrected to pin the instrument by revision and checksum. Nothing in §5–§9 changed.

**2026-09-03, before the confirmatory analysis was run — the deciding script was
differential-tested against the frozen prose, and six defects were repaired.** §8 is the rule;
`experiments/halo/memory_prereg_verdict.py` is only its implementation, and the two had drifted.
Three implementations of §7 and §8 were written from this document alone, by readers who were
forbidden to open the existing script, and all four were run over a battery of 22 synthetic
grids built to sit on the rule's boundaries. They agreed on 4 of 22 cases. Where the prose is
determinate the existing script was wrong, and it was corrected:

1. **Scored epochs were not restricted to k = 3…24.** `contrast()` iterated the whole series and
   `fires()` streaked over list position, so epochs 1 and 2 could complete a triple. *Latent, not
   live:* `retained` is undefined at epoch 1 and `twoback` at epoch 2, so both entries are always
   `None` in real data and no run could reach it. Now filtered explicitly.
2. **The ceiling median included the two unscored epochs.** §7.2 says "over scored epochs". Now
   filtered. *Latent:* the measured ceiling shares are bimodal — conditions sit at 0.99–1.00 or at
   0.02–0.19, with nothing between 0.22 and 0.92 — so no run is near the 0.5 gate either way.
3. **"Median" was the upper-middle element**, not the median, on the even-length lists every run
   produces. Now the mean of the two middle values. *Latent, same reason as 2.*
4. **A condition holding fewer than three seeds could satisfy the 2-of-3 quorum on one run.**
   `need = 2 if len(group) >= 3 else len(group)` reduced the quorum to whatever was present. This
   is reachable only on an unfinished grid. Now the quorum is literally 2.
5. **A run with no mass evidence crashed the script** instead of failing gate 1. A half-written
   run now voids its own cell, which is what §9 anticipates when a machine stops mid-grid.
6. **The script would score an unfinished grid.** It now refuses unless `--partial` is passed, and
   `--partial` stamps the output "THIS DECIDES NOTHING" and writes to `verdict_partial.json`.

Every one of these makes the code match this document. None changes what §8 says, and the four
that are reachable at all are unreachable on the completed grid. The uncorrected original is kept
so the two can be run side by side, and they are, below the verdict.

**Criterion (d) was NOT changed, and it has a defect this document must own.** (d) estimates the
null firing rate from the same 60 cells and then tests against it as if it were known. When the
independent-seed arm fires in **zero** cells — which is what a good null looks like — the estimated
rate is exactly 0, and the chance of seeing even one firing cell under a process that fires with
probability 0 is 0. So a *single* firing cell clears p < 0.05 automatically, at any threshold. At
n = 60 with a silent null arm the registered rule needs one firing cell; all three independent
readings need seven. That is the difference between a result and an artefact, and it was found
before the confirmatory numbers were known.

The rule is frozen, so the registered p-value still decides. It is now reported beside two others
that do not throw the uncertainty away — the same binomial with the null rate at its one-sided 95%
upper bound (the rule of three, 0.0487 at n = 60), and the exact paired McNemar test the design
actually earns, since both arms are measured on the same cell. `memory_prereg_nullrate.py` computes
all three and says plainly when the registered one is degenerate. **If they disagree, the honest
report is that this criterion under-determines the outcome, and the disagreement is published.**

**Also recorded: §9 was broken, in the small.** §9 allows no interim look. During the audit above,
the verdict script was run on the stale 14-run `analysis.json` left over from 2026-09-02, and its
output — `NULL, cells 14, fired 1, fired under the seed null 0` — was read before the grid finished.
It is disclosed rather than buried. It changed no design decision: every repair listed above was
derived from this document's prose by readers who never saw the data, and the corrections are all
behaviour-neutral on the completed grid. The completeness guard added as repair 6 exists so this
cannot happen again by accident.

---

**2026-09-03, after the confirmatory read — what an independent audit of the grid's provenance
found, including a second interim look this document had not recorded.** Three auditors and eight
refutation attempts were run against the completed grid and the verdict. None changed the verdict.
Seven things they found belong here rather than in the analysis, because they are facts about how
this protocol was executed.

1. **A second interim look, one day earlier than the one disclosed above.**
   `data/results/halo/memory_prereg_voided/verdict.json`, written 2026-09-02 15:47:44, is a full
   §8 verdict over **13** cells — `NULL, cells 13, fired 1, fired under the seed null 0,
   null rate 0.0, p 0.0` — computed while the void grid was still collecting. The look disclosed
   above is a different one (14 cells, read 2026-09-03). Two more partial artefacts sit beside it:
   `voided/analysis.json` (15:34:35, 13 runs) and `voided/rotation.json` (15:31:26, 10 runs). Both
   looks were at the *void* grid, whose 23 runs each record `console: Failed to load resource:
   net::ERR_FILE_NOT_FOUND` and none of which contributed a number to the confirmatory result. It
   is still an interim look, §9 still forbids it, and it is recorded here.

2. **The `admissible_subset` block was added to the deciding script after the freeze.** Commit
   `39834d08`, 26 minutes after `a30ada56`. It is the source of the secondary reading "9
   conditions, 27 cells → NULL". It never assigns to `verdict`, its own comment says "REPORTED
   ALONGSIDE, NOT A CHANGE TO THE RULE", and §8 permits labelled exploratory analysis — but the
   addition was not recorded, and now is.

3. **The discarded-run count above is wrong by three.** §13 says "the first 26 runs were
   discarded". `memory_prereg_voided/` holds **23** complete runs plus one truncated mesh
   (`spinchladni_sg0.5_gl0.5_seed31337`, 2,752,512 bytes = 21 of 24 epochs, no sibling JSON): the
   void grid attempted 24 cells and was killed inside the 24th.

4. **"One mesh half-written" understates the 2026-09-02 stop.** Three cells lacked records, not
   one: two mid-sequence failures (`spinchladni_sg0.3_gl0_seed12345`, `default_sg0_gl0_seed31337`)
   as well as the tail. The grid loop continued past them and all three were produced on 09-03 in
   loop order. This is not a §9 violation — §9 permits resuming at a failed cell and
   `memory_prereg_grid.sh` never re-runs a written one — but the description was wrong. The count
   of 28 written cells is right.

5. **Two runs were executed concurrently on the one GPU** during the 09-02 sitting.
   `spinchladni_sg0.15_gl0.5_seed31337` ran 16:09:18–16:16:29 (431 s wall, against 99 s and 102 s
   for its uncontended siblings) overlapping two `default_sg0_gl0` runs by 305 s and 93 s. §11's
   "one machine, one GPU" stays literally true, and the effect is measurable rather than argued:
   that contended run and its uncontended counterpart in the void grid share mesh md5
   `4f1bfff0f9dd18d3ee6b7b5a536ecefb`. Contention cost wall-clock and changed no number.

6. **Instrument identity is established by the data, not only by the checksum — and this
   supersedes the concession above.** §13 previously conceded that "nothing inside the data binds
   these runs to the page that produced them". That is now too weak. `spinchladni_sg0.3_gl0_seed12345`
   was measured 2026-09-02 15:34:34 and again 2026-09-03 09:23:36 and **both meshes are md5
   `d71c53a9ee2200e66db87d5ec47ccdd0`**, with identical `epochs[]` and `csv_rows`. All **23 of 23**
   completed void runs replicate bit for bit against their confirmatory counterparts. They were
   genuinely re-run and not copied: `wall_seconds` differs in 9 of the 23 (173 s → 118 s,
   99 s → 431 s, 182 s → 170 s) while every measured value is identical. A bit-exact replication
   across two days, two sittings and a browser restart is stronger evidence of instrument identity
   than any file checksum.

7. **The ceiling-share modes quoted above are slightly off.** §13 says the conditions "sit at
   0.99–1.00 or at 0.02–0.19, with nothing between 0.22 and 0.92". The empty band holds and the
   conclusion is unaffected, but the low mode reaches exactly 0.0000 and the high mode starts at
   0.9619: the actual gap is **0.1702 to 0.9619**.

**Also confirmed, and worth as much as the corrections.** §§1–11 are byte-identical across every
revision of this file — section md5s match at `a30ada56`, `250dc096`, `97d70e15`, `5cb08e51` and
today. The freeze precedes the data by 34 seconds: `a30ada56` is 2026-09-02 15:21:28 −0700 and the
earliest data byte anywhere is 15:22:02.637. The grid is exactly the 60 cells §5 specifies, with 0
missing, 0 extra, 0 duplicate, 0 filename-content mismatches, 0 out-of-protocol runs, and 60 of 60
meshes exactly 24 × 32768 float32 with no NaN, no inf, no negative and no all-zero epoch. An
independent re-implementation written from this document's prose, sharing no code with the
analysis, reproduced all 6,768 estimator values to within 1.9 × 10⁻¹⁵ and agreed with the verdict
table on all 60 cells.

**One gate is enforced by no code.** §7.4 ("a run that logs a page error or console error is
void") is checked nowhere: the runner captures errors into `pageerrors`, but the analyser never
carries that field into `analysis.json` and the void test has only three terms. It is vacuous on
this grid — 0 errors across 60 of 60 runs — and it would not have been vacuous on the void grid,
where all 23 runs logged one. The hole is recorded rather than patched, because patching the
deciding code after the confirmatory read is exactly what §9 exists to prevent.
