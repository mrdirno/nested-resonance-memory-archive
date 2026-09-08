# The measurability pilot: no field the frozen estimator can measure, and the recorded grid's instrument found

**Author:** Aldrin Payopay · **Date:** 2026-09-07 · **Licence:** GPL-3.0-only

**Pre-registration:** [`docs/halo/2026-09-06_measurability_pilot_preregistration.md`](../docs/halo/2026-09-06_measurability_pilot_preregistration.md), frozen at commit `a0c49ffc` before the first run of the arm it describes · **Frozen protocol:** [`docs/halo/2026-09-05_memory_estimator_qualification_protocol.md`](../docs/halo/2026-09-05_memory_estimator_qualification_protocol.md) · **Result:** [`scn_qualification.json`](../data/results/halo/memory_pilot/scn_qualification.json) (measured 2026-09-07T23:19:25Z, 5 s) · **Diagnostic:** [`scn_report.json`](../data/results/halo/memory_pilot/scn_report.json) · **Screens:** [`scn_screens.json`](../data/results/halo/memory_pilot/scn_screens.json) · **Reproduction receipt:** [`reproduction_probe.json`](../data/results/halo/memory_pilot/reproduction_probe.json) · **Interrupted-run receipt:** [`interrupted_run.json`](../data/results/halo/memory_pilot/scn_interrupted/interrupted_run.json) · **Figures:** [frontier](../data/figures/halo_memory_pilot_frontier_2026-09-07.png), [standard panels](../data/figures/halo_memory_pilot_2026-09-07.png)

---

## 1. The question, and the two answers

On 2026-09-06 the frozen memory estimator was scored once on the recorded 60-run grid and returned
**insufficient support**: 0 of 60 runs measurable ([result](2026-09-06_memory_estimator_qualification.md)).
Before another grid could be registered, something had to be shown measurable. The pilot asked one
question: **is there a field configuration the page already ships in which the three seeds' compressed
relics genuinely diverge, while the relic still occupies at least 8 effective cells?**

The answer is **no**, on all seven conditions run, and the pre-registered decision rule has no branch
that disposes of the outcome.

The second answer came from the two conditions the pre-registration excluded from its own success count
by construction — the anchors, whose only job was to measure instrument drift. They did not reproduce
their recorded statistics, and chasing that took seven controlled re-runs to settle: **the recorded
60-run grid is reproducible byte for byte, but only under the page as it stood before ring 13**, which
landed two hours and thirty-eight minutes after that grid finished. The anchors were registered to catch
exactly this, and they caught it.

Nothing here establishes or retires nested resonance memory. Measurability is eligibility plus seed
balance; detection is a separate test this pilot does not power; the pilot chose its conditions by
looking at the gates. No S, no p and no falsifier verdict from this arm may be read as evidence about
memory in either direction.

## 2. The arm as it ran

One directory, `data/results/halo/memory_pilot/scn/`. 21 runs, 7 conditions, 3 seeds each (777, 12345,
31337), every run at 4,194,304 particles, 24 epochs of 10 s, gain/loss 0, tick budget 10, digit position
9028, real GPU. 3,094 s of wall clock (51.6 min against a pre-registered estimate of 27 min and an
envelope of 45; the estimate was built from Spinning Chladni wall times and `goldstair` runs 3.5x slower).
The arm ran in **three sessions** — 2026-09-06 17:45–17:57, 2026-09-07 11:46–12:19, and 2026-09-07
16:13–16:19 — with both anchors in the first.

**One run was re-run, and the re-run is provably innocent.** `goldstair sg0.3 seed 31337` was interrupted
mid-write when a session ended: it left a mesh of exactly 19 of 24 epochs (2,490,368 bytes, sha256
`ac5c78ff…`) and no run record, because the runner writes its record only after the last epoch. §6 of the
pre-registration allows a crashed run to be re-run once, **before** scoring. It was re-run once on
2026-09-07 (254 s), passed the runner's own three-reading gate — asked parameters, the page's applied
state, and every epoch's deposit total against the mesh length — and only then was the arm scored. The
re-run reproduces the interrupted attempt **bit for bit over all 19 overlapping epochs**: the sha256 of
the first 19 epochs of the re-run is `ac5c78ff…`, the interrupted file's whole-file hash. Nothing about
the arm's data could have moved. The check, the two hashes and the run log are in
[`scn_interrupted/`](../data/results/halo/memory_pilot/scn_interrupted/).

**The void conditions, stated per run rather than as a blanket.**

* **(i) the instrument changed during the arm** — not fired, but verified only as an end-state hash.
  Checked at the freeze (commit `a0c49ffc`) and again immediately after scoring on 2026-09-07, before
  ring 17 was appended: `tests/halo/rc-test.html` `03286c6d…`, the page it is built from `d5ad799a…`,
  the frozen scorer `7619ef6b…`, the frozen protocol `e55a53a1…`. **Appending ring 17 changes the page's
  hash and staleness-marks the browser instrument built from it**, which is expected and is why the four
  values are pinned to a moment here rather than asserted as present-tense fact; the scorer's and
  protocol's hashes are unaffected. **No per-run instrument hash is recorded**, so a change-and-restore inside the
  arm's three sessions would not be detectable. §6 of this document is what that gap costs.
* **(ii) the runner aborted on a page error or a parameter or mesh mismatch** — not fired for the 20 runs
  that produced records: none logged a page or console error, every mesh holds exactly 24 × 32³ float32
  values, and every run's recorded parameters and applied page state agree with its filename. For the
  interrupted cell it is **not evaluable**: the runner did not abort, the session did, and no record
  exists to hold a page-error list. It is published as not evaluable rather than as passed.
* **(iii) an anchor came back measurable** — not fired. `spinchladni` 0.3 came within **two eligible
  epochs** of firing it, at 10, 10, 9 against a bar of 12.

The manifest verified 21 runs and 42 files, and the scorer reports `inputs_verified: true`. The scorer
was invoked once, on the whole directory. No run in the arm was re-run, re-seeded or substituted after
scoring; `scn/` was not modified after the score. The reproduction controls of §6 are post-scoring
diagnostics, run into directories outside the repository, never scored, and unable to change any number
in the arm. The pre-registration's "re-run once" is not machine-enforced — an Nth attempt is
indistinguishable from a first in everything the repository contains. It is evidenced here by the
retained partial mesh, its receipt and the re-run log, and a successor protocol should record every
attempt rather than only the one that finished.

One footnote on the result file: `scn_qualification.json` records `protocol_commit 6702d390`, the
repository HEAD at scoring time, not the freeze commit `a0c49ffc`. It is the scorer's default and it is
not the freeze.

## 3. The result

**Insufficient support. 0 of 21 runs measurable, 0 of 7 conditions, 0 detected.** 37 of 462 run-epochs
eligible (8.0 %, against 13.6 % on the recorded grid). Summed gate refusals: **E2 300, E3 175, E1 74,
E4 0.** F1 pass, F2 pass on the receipt only, F3 not evaluable (no measurable run), F4 pass with nothing
to compare, F5 fail — 0 of the 3 conditions required.

**The pilot metric is 0 measurable conditions of 5 live, against a target of 3 and a baseline of 0.**
That is the pre-registration's own modal outcome; it gave 0.12 to the alternative. Of the five live
conditions, the pilot's own screens struck four.

| condition | role | eligible /22 | E1 | E2 | E3 | D3 relic PR | own relic PR | template corr. | inner-block mass |
|---|---|---|---|---|---|---|---|---|---|
| `spinchladni` 0.15 | anchor | 1, 1, 1 | 2–4 | 5–6 | 18–20 | 147.05 | 155–175 | 0.987–0.991 | 0.034 |
| `spinchladni` 0.3 | anchor | **10, 10, 9** | 2–4 | 5–7 | 8–10 | 57.37 | 67–98 | 0.601–0.756 | 0.037–0.043 |
| `hardprint` 0.15 | probe | 0, 0, 0 | **12–14** | 21–22 | 0–1 | **5.05** | 5.6–7.0 | **0.048–0.055** | **0.004–0.008** |
| `hardprint` 0.3 | probe | 1, 1, 1 | 2–5 | 20 | 0–1 | **5.06** | 6.6–7.1 | **0.024–0.029** | 0.045–0.150 |
| `stillspindle` 0.15 | probe | 1, 1, 0 | 3 | 3 | 19–22 | 13.71 | 13.9–18.1 | 0.999–1.000 | 0.034–0.040 |
| `goldstair` 0.15 | **primary** | 0, 0, 0 | 0 | **22** | 3–5 | **3.08** | 4.1–4.7 | 0.465–0.525 | **1.0000** |
| `goldstair` 0.3 | **primary** | 0, 0, 0 | 0 | **22** | 3–4 | **3.31** | 4.0–4.8 | 0.502–0.538 | **1.0000** |

Two column names matter, because both were read loosely in a first draft of this document:

* **"D3 relic PR"** is the statistic the pre-registration registered: the median over epochs of the
  **minimum over the three seeds** of the predicted field's participation ratio — which is what E2 tests.
  **"own relic PR"** is `pr_pred` from the result file, that run's **own** predicted field, which is what
  the diagnostic prints and is always the larger number. Both are published because a first draft quoted
  only the second. On the registered statistic the gap to the 8-cell gate is wider everywhere, and the
  pre-registration's own predicted footprint band for `goldstair` 0.15 (5–45 cells) is missed low on both
  readings.
* **"template corr."** is not the median of the per-epoch *largest* correlation. It is the median of the
  44 pooled absolute template correlations, both strangers together. The pre-registration's decider names
  "the median largest template correlation", which admits at least three readings, and the two published
  scripts implement two different ones. §2 of the pre-registration calibrates against 0.60 at
  `spinchladni` 0.3, which reproduces exactly as the pooled-absolute median — so that is the reading used
  throughout here, and it is stated rather than assumed.

E2 does most of the refusing, and for `goldstair` it refuses on the **coarse-grained relic** — the
previous epoch's field summed 2× onto the inner block — not on the current field, which still carries
7.1–10.9 effective cells. The 1e-9 residual-variance clause of E2 did no work anywhere in this arm.

**A pre-registered robustness variant is not zero, and the headline should carry it.** The frozen
scorer's own F4 row `e2_pr4` — the footprint floor lowered from 8 to 4 — makes 4 runs measurable and
detects `hardprint sg0.3` seeds 12345 and 31337. That row is reported, not scored, for the reason ring 16
gave: a number bought by loosening the gate that refuses the artefact is the artefact.

**The zero is a statement about support geometry, not about memory.** An independent worker built a
positive control by injecting a perfect passive relic into these meshes; the frozen pipeline still
returns 0 measurable runs on this arm. Eligibility is evaluated before any effect size, so 0-of-21 is
invariant to how much memory the fields carry. It says these fields cannot be *measured* by this
estimator, and nothing about what they contain.

## 4. The screens, and the two the review found wrong

The pre-registration fixed five screens before any run. They change no gate and no threshold; they decide
only whether a condition counts toward the pilot's number, and they are published for every condition
whatever the outcome. These are the numbers `memory_pilot_staticness.py` produced, unedited:

| condition | A1 raw cross-seed | A2 structural | A3 static | A4 clamp | A5 noise share | verdict |
|---|---|---|---|---|---|---|
| `goldstair` 0.15 | **1.0000** | **1.075** | **1.0000** | **0.9995** | **0.692** | struck by all five |
| `goldstair` 0.3 | **1.0000** | **1.017** | **1.0000** | **1.0000** | **0.589** | struck by all five |
| `hardprint` 0.15 | 0.0169 | 0.0473 | 0.0392 | 0.0149 | 1.07e-05 | **passes** |
| `hardprint` 0.3 | 0.4889 | 0.0273 | 0.0175 | **0.5342** | 1.07e-05 | struck by A4 |
| `spinchladni` 0.15 | **0.9985** | **0.9905** | 0.4429 | 0.0422 | 1.55e-04 | struck by A1, A2 |
| `spinchladni` 0.3 | 0.4308 | 0.6029 | 0.2077 | 0.0728 | 6.62e-05 | **passes** |
| `stillspindle` 0.15 | 0.9889 | **0.9998** | 0.2924 | 0.0161 | 3.85e-05 | struck by A2 |

Thresholds, fixed in advance: A1 ≥ 0.99, A2 ≥ 0.9, A3 full field ≥ 0.99 or angular residual ≥ 0.70,
A4 > 0.5, A5 > 0.01. A re-implementation written from the pre-registration's prose alone reproduces
every published A2–A5 number to 13–16 significant digits and strikes the same conditions. It also found
three defects, published here rather than corrected in place:

* **A2 returns 1.075 and 1.017, and a correlation cannot exceed 1.** The shot-noise correction divides
  by a residual that is mostly noise, and its premise (a noise share below 1) is refuted by its own
  inputs in 22 of 69 `goldstair` run-epochs. A corrected estimator — covariance over noise-subtracted
  powers, no sign folding, no dropped pairs — gives **1.0043 (95 % CI 0.945–1.065)** and **0.9736 (95 %
  CI 0.856–1.015)**. Both readings clear the 0.9 threshold; the strike stands, the number as printed does
  not.
* **A5 is published about 14 % high** and is not the particle-identity margin §4 of the pre-registration
  assigns it. Its numerator is fixed by mass conservation, so at fixed particle count it is an inverse
  measure of angular-structure power, not evidence about particle identity. Corrected: **0.6063** and
  **0.5157**. The conclusion is unchanged — two to three orders of magnitude above the 0.01 threshold and
  three above the 0.0001–0.0003 the pre-registration expected.
* **A1 is computed on the final epoch only**, where the prose specifies a median over epochs, and **A4's
  only strike sits on its threshold** (0.5342 against 0.5): under the prose read literally, `hardprint`
  0.3 passes all five screens. Both are recorded as instrument defects for the successor. Neither changes
  the pilot's number, which is zero under every reading.

**`goldstair`, the primary, produced no field to measure.** Its centroid sits at (15.500, 15.500, 15.500)
— the exact box centre — and travels 0.000–0.001 cells across the whole run. Its lag-one full-field
correlation is 0.99997–0.99998: it does not move. Its rms radius is **1.38 cells**, its eight largest
cells hold **55.5 %** of all the mass, and 219–256 cells of 32,768 are occupied. Every one of its six runs
sat on the force ceiling for the entire run (median clamp share 0.9995–1.0000, against 0.015–0.534 for
every other preset). What the estimator then compares is not a pattern: an independent reading finds the
template reduces to a fraction-of-a-percent imbalance among the eight cells of a single cube-symmetry
orbit — about seven degrees of freedom — and a Poisson null built on *exactly degenerate* seeds
reproduces the observed correlation distribution at KS p = 0.98.

**And `goldstair` did not test the axis it was chosen for.** The page computes field strength as
`Math.pow(10, fieldExp)`, so cutting the exponent from 2 to 0.15 cuts the drive by a factor of **70.8** —
while self-gravity was held at the same 0.15 and 0.3 the spinning family ran at. The pre-registration
described this as "cutting the field exponent 13-fold"; on the quantity the physics uses it is seventy-
fold, and nothing was renormalised against it. What the primary condition therefore ran is not "the same
dynamics with a weaker drive" but "self-gravity with almost no drive to hold it up", which collapses. The
question §5 of the pre-registration meant to ask — whether a weaker imposed drive lets the seeds diverge —
was not put to the test, and **no conclusion that the drive-cut axis is dead can be drawn from this arm.**
The successor's version of this condition has to move self-gravity down with the drive.

So `goldstair`'s three seeds are **indistinguishable from exact copies at this sample size** (raw
cross-seed correlation 0.99999 at zero shift on all three pairs, at both self-gravities), with a
seed-specific structural share bounded at roughly 20–35 %, not demonstrated to be zero. And its raw
template correlation — 0.4651, 0.5035, 0.5249 per run, the number the pre-registration named as its
decider — is what a
collapsed estimate looks like, not what a broken drive lock looks like.

## 5. The decision rule has no branch for what happened

Read strictly, by the letter of §6:

* **Commission a confirmatory grid** — needs three non-anchor conditions at 12 eligible epochs. **Does
  not fire**: zero, and the best non-anchor run reached 1.
* **Keep piloting (a)** — needs `goldstair` 0.15 to bring **both** template correlations below 0.9 with
  E\* at 8–11. Its raw template correlation is 0.4651, 0.5035 and 0.5249 per run (0.4978 pooled over epochs and
  pairs by the screens), below on every reading; its structural correlation is 1.0043 (published as
  1.075), above; and E\* is 0, not 8–11. **Does not fire.** Its stated *cause* — the relic
  footprint fell below 8 — is confirmed in 66 of 66 run-epochs; only its E\* window missed, and it missed
  low.
* **Keep piloting (b)** — needs one or two non-anchor conditions at 12 eligible epochs. **Does not fire.**
* **Retire the plan to run a grid under the frozen protocol** — needs all three of: no non-anchor
  condition at 12 (**true**); `goldstair` 0.15 keeping its median largest template correlation at or above
  0.9 (**true on the structural reading at 1.0043, false on the raw one at 0.5035**); and **the anchors reproducing their
  recorded statistics — false, decisively.** `spinchladni` 0.3 went from 6, 6, 3 eligible epochs to 10,
  10, 9. **Does not fire.**

**No branch fires**, and the binding clause is the anchors', not the decider's: under *either* reading of
the decider, retire is blocked by anchor non-reproduction. That clause could not have been satisfied.
§6 below shows the recorded statistics were produced by an instrument that was replaced two and a half
hours after the recorded grid finished — a fact nothing in the repository recorded, and which the
pre-registration therefore could not have known when it made anchor reproduction a condition of its own
termination.

Two further things the rule could not do:

* **Its single named decider is void.** It was read off `goldstair` 0.15 — the one condition all five of
  its own screens struck, and the one that produced a static clamped point. A statistic computed on that
  carries no information about the drive lock, in either direction. It is reported as unevaluable, not as
  a pass and not as a fail.
* **Diagnostic D5 was not met for any of the 21 runs.** It asks for each seed null with its standard
  error; the frozen scorer does not emit standard errors. The obligation was written against an output
  schema the script does not have. It is disclosed as unmet rather than quietly dropped.

The frozen text is not edited, no branch is invented, and the un-fired keep-piloting branch is **not**
exercised: no second arm runs on this pilot's authority. The rule is silent here, not prohibitive — but
silence is not a licence, and what follows §6 is a successor protocol rather than another arm under this
one.

### The five pre-registered predictions

1. **Falsified, in the direction §5 flagged as informative.** `hardprint` was predicted to move E3 the
   *wrong* way, by no more than 0.02 below Spinning Chladni at the same self-gravity, on the page's own
   note that cutting the magnetic coupling roughly doubles the azimuthal density contrast. Observed:
   **0.0513 against 0.9883** at self-gravity 0.15 — **0.937 below, not 0.02.** §5 pre-committed to the
   consequence: that reading of the magnetic coupling is wrong as a predictor of seed separation.
2. **Confirmed but untested.** E5b was predicted not to be the binding gate; it fired on nothing. It was
   never put at risk: on `spinchladni` 0.3, the only condition with substantial eligibility, the
   seed-quality ratio was **6.3–8.4× against a 3× threshold**, and the gate was held off only by its
   0.05 magnitude floor (largest null 0.035–0.040). The sign-flip fragility carried forward from ring 16
   was not exercised here, and this near-miss is the reason it must still be carried.
3. **Confirmed.** E5 fired on no run.
4. **Confirmed degenerately.** `goldstair` was predicted to hold median inner-block mass above 0.15
   against the spinning family's 0.035. It holds 1.0000 — not because it retains its matter against
   dispersal, but because it collapsed entirely into a point at the centre of the block. The prediction's
   purpose is defeated by the number that confirms it.
5. **The headline band was missed low.** `goldstair` 0.15 was given 50/50 odds and a predicted 2–15
   eligible epochs on a relic of 5–45 cells. Observed: 0 eligible epochs on a relic of 4.1–4.7 cells
   (3.08 on the min-over-seeds statistic E2 actually tests), refused by E2 in all 66 of its run-epochs.

### Every condition against its pre-registered line

§6 of the pre-registration obliges all seven conditions' diagnostic lines to be published, in the order of
its §3 table, whatever the outcome. Footprint is scored on the registered D3 statistic, with the own-field
median beside it; "template" is the pooled-absolute condition median.

| condition | predicted footprint | observed (D3 / own) | predicted template | observed | predicted eligible | observed | predicted measurable | observed |
|---|---|---|---|---|---|---|---|---|
| `spinchladni` 0.15 (anchor) | 150–190 | **147.05** / 173.9 — missed low | 0.985–1.000 | 0.9883 — **missed low** | 0–1 | 1, 1, 1 — hit | No | No |
| `spinchladni` 0.3 (anchor) | 60–85 | 57.37 — **missed low** / 75.2 hit | 0.72–0.81 | 0.6729 — **missed low** | 3–9 | 10, 10, 9 — **missed high** | No | No |
| `hardprint` 0.15 | 60–200 | **5.05** / 7.0 — **missed low by 12x** | 0.97–1.000 | **0.0513** — **missed low by 0.92** | 0–3 | 0, 0, 0 — hit | No | No |
| `hardprint` 0.3 | 40–90 | **5.06** / 7.0 — **missed low by 8x** | 0.70–0.95 | **0.0242** — **missed low by 0.68** | 1–8 | 1, 1, 1 — hit | No | No |
| `stillspindle` 0.15 | 40–200 | **13.71** / 14.0 — **missed low** | 0.96–1.000 | 0.9999 — hit | 0–3 | 1, 1, 0 — hit | No | No |
| **`goldstair` 0.15** | 5–45 | **3.08** / 4.3 — **missed low** | 0.35–0.95 | 0.5035 — hit | 2–15 | 0, 0, 0 — **missed low** | 50/50 | No |
| **`goldstair` 0.3** | 4–35 | **3.31** / 4.2 — **missed low** | 0.25–0.85 | 0.5287 — hit | 2–14 | 0, 0, 0 — **missed low** | 50/50 | No |

Seven of seven footprint bands were missed low, five of them badly. The pre-registration's model of how
much relic these fields would leave was wrong everywhere, in the same direction — which is a stronger
statement than any single condition's failure, and it is why the successor's first job is to predict
footprint, not separation.

One calibration figure in §5 of the pre-registration — the anchor's decider reading of 0.9952 — does not
reproduce from the recorded grid under any of the three readings of "median largest template
correlation". It does not change the adjudication: every reading of `goldstair` 0.15 is far below 0.9 and
every reading of the anchor is far above. It is noted so a reader who tries to reconcile the two
documents is not left guessing.

## 6. The anchors: the recorded grid's instrument, found

The anchors are recorded-grid conditions re-run on the current build. Their job was to measure drift.
They found this:

| | recorded 2026-09-02 | pilot 2026-09-07 |
|---|---|---|
| `spinchladni` 0.15, eligible epochs | 0, 0, 0 | 1, 1, 1 |
| `spinchladni` 0.3, eligible epochs | **6, 6, 3** | **10, 10, 9** |
| `spinchladni` 0.3, E2 refusals | 11, 8, 14 | 5, 7, 6 |

The two runs of the same tag are not the same field. Per-epoch, the recorded and pilot densities of
`spinchladni sg0.3 seed 777` correlate from **−0.007 to 0.996**, ending at 0.514; the other two seeds end
at 0.392 and **0.014**. The 0.15 anchors are closer but not close: a median per-epoch correlation of
0.980–0.995 that **dips to 0.263, 0.474 and 0.626 — all three at epoch 16**. The 0.3 anchors hold a
median of 0.651–0.689 and reach −0.007, 0.004 and −0.006 at epochs 16–17. Divergence is visible in the first recorded epoch, 200 ticks in, where the recorded
run reports λ 2.3232 and clamp share 0.0547 and the pilot reports 2.2700 and 0.0854.

**Seven controls, two hashes** ([receipt](../data/results/halo/memory_pilot/reproduction_probe.json)).
Each is one run of the same tag with one layer changed:

| control | output sha256 | reproduces the recorded run |
|---|---|---|
| the pilot arm itself | `a360141a…` | no |
| an immediate repeat, same build, same day | `a360141a…` | no |
| Chromium 143.0.7499.4 | `a360141a…` | no |
| Chromium 145.0.7632.6 | `a360141a…` | no |
| page `05dfa4ab` (2026-09-02 21:05), its own builder | `a360141a…` | no |
| page `122d0a57` — **ring 13**, 2026-09-02 18:59 — its own builder | `a360141a…` | no |
| page `c6cd2cbe` (2026-09-01 22:37), builder `5cb08e51` | **`b8000808…`** | **yes, byte for byte** |

So three things are settled that were not settled before.

**The instrument is deterministic to the bit.** Same build, same seed, same bytes — across an immediate
repeat, two Chromium builds and three page revisions. "A run is reproducible tick for tick from its seed"
is true, and run-to-run non-determinism is not the explanation for anything here.

**The recorded 60-run grid is reproducible** — under the page as it stood before ring 13. Its instrument
is identified for the first time: page `c6cd2cbe` with test-page builder `5cb08e51`. Nothing recorded
that; it was recovered by bisection.

**Ring 13 is the change.** `122d0a57`, whose own title is *"the chamber measures its own mesh, its own
integrator and its own energy"*, landed at 2026-09-02 18:59 — two hours and thirty-eight minutes after the
recorded grid finished at 16:21 — and added a self-gravity solver choice, a mass-assignment choice and an
integrator substep control. Its state defaults (`solver: 'jacobi'`, `assign: 'ngp'`) were expected to
reproduce the previous behaviour; the core `PM_GLSL` block, `PM_N`, `PM_ITERS` and `SG_GAIN` are
byte-identical across the two revisions, and so are all four scenario preset objects used by this pilot.
They do not reproduce it. Which of ring 13's changes is responsible is not established here.

**A control that silently did nothing, published so it is not repeated.** A first attempt at the old-page
control ran `make_test_page.py --from-git c6cd2cbe` with the *current* builder. It raised
`AssertionError: simStop hook matched 0 times` and wrote no file, so the run that followed used the
current instrument and returned `a360141a…` — which reads exactly like "the page is exonerated". A first
draft of this document published that conclusion. It was caught in review, and the answer inverted once
the builder was period-matched to the page. **The test-page builder and the page revision must be taken
from the same moment**, and a control that depends on a build step must check that the build happened.

Two things this does **not** mean. Ring 16's numbers are not withdrawn: they are true of the 60 meshes on
disk, and those meshes can now be regenerated. And build drift does not explain the pilot's zero — the
drift moved in the *favourable* direction, giving the anchor four more eligible epochs than the recorded
grid, and even so nothing reached the bar.

**The arm also measures something no single grid could: how noisy E\* is between realisations.**
`spinchladni` 0.3 now has **six independent draws** of the same condition — three recorded, three from the
pilot — because the build change re-draws the realisation exactly as a re-seed would. Their eligible-epoch
counts are 6, 6, 3, 10, 10, 9: **mean 7.33, standard deviation 2.80**, against a measurability floor of 12
that sits **1.66 standard deviations** away. A rule that calls a condition measurable when all three of its
runs clear 12 is therefore reading a threshold crossing on a statistic whose realisation spread is nearly
a quarter of the threshold. Three seeds cannot separate that spread from a systematic shift, and no
protocol in this programme has yet measured it. It is published here as the first estimate of the
realisation noise floor of E\*, from the only condition that has enough draws to give one.

What it does mean is that **the pilot chose its conditions from a per-gate table computed on an
instrument that had already been replaced**, and that no recorded run in this programme names the build
that produced it. That absence is why this took seven runs to answer, and it is the most cheaply fixable
defect the pilot found: a run record must carry the sha256 of the instrument that drove it.

## 7. Where the frontier is, and where it is not

Plotting all seven conditions against the two gates that decide measurability
([figure](../data/figures/halo_memory_pilot_frontier_2026-09-07.png)) shows nothing in the box, and shows
the conditions missing it in three directions:

* **`spinchladni` 0.15 and `stillspindle` 0.15** hold relics of 14–175 cells whose seeds are copies
  (structural correlation 0.99–1.00). Plenty to measure, nothing to distinguish.
* **`goldstair`** has a relic of four cells and seeds indistinguishable from copies; its apparent
  separation is a collapsed estimate.
* **`hardprint` produced the lowest template correlation in the programme** — condition-median pooled absolute
  **0.0513** at self-gravity 0.15 and **0.0242** at 0.3, against 0.9883 and 0.9999 for the locked conditions — with a shot-noise share of
  1.07e-05, and at 0.15 it passes all five screens. It is also **the only condition in the arm where E1
  binds**: median inner-block mass 0.004–0.008, centroid travel 8–10 cells, E1 refusing 12–14 of 22
  epochs. But E2 still refuses 21–22 of its epochs, so it is not a clean case of "a different gate" — it
  is the only case where two gates bind at once.

The tempting inference — that seed degeneracy and scoring support are cleanly separable, so a support
region that follows the matter would recover `hardprint` — was tested and does not hold. A worker asked
to refute it found that **no support region recovers a single condition**, because E2's refusal is
computed on the participation ratio of the 2× block-summed predicted field, and that quantity stays below
8 wherever the block is placed. The separation `hardprint` shows is real and worth building on; the
prescription that would follow from it is not established, and is not published as one.

The nearest thing to a measurable condition in the whole arm is an anchor: **`spinchladni` 0.3 passes all
five screens and reaches 10, 10, 9 against a bar of 12** — two epochs from measurable, and two epochs from
voiding the arm it was registered to validate.

## 8. Limitations

* Nothing here measures memory. F3 was not evaluable, no run was detected, and the zero is invariant to
  injected memory content (§3).
* F2 cannot be re-certified from this arm: the frozen receipt's shared-drive controls give the seeds
  10–50 % of the power, and these conditions give them a fraction of a percent.
* Scoring stops at epoch 24 (`FIRST_SCORED, LAST_SCORED = 3, 24`, fixed with no flag), so "run longer
  than 24 epochs" was unavailable and is carried forward. `FIRST_SCORED = 3` is set by the lag-two arm;
  the lag-one arm needs only two meshes, so it loses an epoch it does not need — no verdict changes.
* The A2 correction is first-order and returns impossible values where the residual is mostly noise; A5
  is not a particle-identity margin; A1 uses one epoch where the prose says median; A4's only strike sits
  on its threshold. All four are recorded, none changes the pilot's number.
* The pilot's conditions were selected by looking at the gates on the recorded grid, so it is exploratory
  by construction — and §6 shows that grid was made by a different build.
* Three post-scoring controls were built on page revisions other than the frozen instrument. They ran
  outside the repository, were never scored, and the frozen instrument's hash was verified restored after
  each (`03286c6d…`). §6's forking-paths sentence forbids re-running a *condition* after scoring; these
  are instrument controls that cannot reach the arm's numbers, and the objection is recorded rather than
  waved away.

## 9. What the successor protocol has to carry

1. **An instrument hash in every run record.** No recorded run in this programme names the build that
   made it. It cost seven controlled re-runs to recover one, and the recovery only worked because the
   page is in Git.
2. **A period-matched build recipe.** The test-page builder and the page must come from the same commit,
   and a control whose build step fails must fail loudly, not silently run the current instrument.
3. **A staticness rule that names itself.** No gate refuses a field that does not move; `goldstair` was
   refused by E2, for its size. Carried from ring 16, still unaddressed, and now demonstrated on a
   condition that is static, degenerate and clamp-saturated at once.
4. **A raw-field twin check beside E3, and a shot-noise correction that cannot return values above 1.**
   E3 compares an estimate and can be passed by degrading it. `goldstair` is the worked example.
5. **A decider that is the same quantity its screens test, named unambiguously.** "Median largest template
   correlation" admits three readings and two scripts implemented two of them; and a decider read off a
   condition its own screens strike cannot decide anything.
6. **A tolerance band in place of E5b's sign test, and a decision on run-level versus condition-level.**
   Carried from ring 16 and still untested: on the arm's best condition E5b's largest null reached 0.0402 against
   its 0.05 magnitude floor, with a seed-quality ratio of 6.3–8.4 against a threshold of 3.
7. **An eligibility gate that names which field it is measuring.** E2 refused every `goldstair` epoch on
   the coarse-grained relic while the current field carried 7–11 effective cells, and it refuses secondary
   arms on a template those arms do not use.

## 10. Reproduction

```bash
cd tests/halo
for p in spinchladni hardprint stillspindle goldstair; do
  case $p in stillspindle) S="0.15";; *) S="0.15 0.3";; esac
  OUT=../../data/results/halo/memory_pilot/scn N=4194304 EPOCHLEN=10 EPOCHS=24 \
    PRESET=$p SGS="$S" GLS="0" SEEDS="777 12345 31337" bash memory_pilot_grid.sh
done
cd ..
python3 experiments/halo/memory_pilot_manifest.py data/results/halo/memory_pilot/scn \
  data/results/halo/memory_pilot/scn-manifest.json --note "measurability pilot, one arm"
python3 experiments/halo/memory_estimator_qualify.py \
  --input-dir data/results/halo/memory_pilot/scn \
  --manifest data/results/halo/memory_pilot/scn-manifest.json \
  --synthetic-json data/results/halo/memory_estimator_qualification/synthetic.json \
  --output data/results/halo/memory_pilot/scn_qualification.json
python3 experiments/halo/memory_pilot_report.py data/results/halo/memory_pilot/scn_qualification.json \
  --json data/results/halo/memory_pilot/scn_report.json
python3 experiments/halo/memory_pilot_staticness.py data/results/halo/memory_pilot/scn \
  --json data/results/halo/memory_pilot/scn_screens.json
python3 experiments/halo/memory_estimator_qualify.py --figure \
  data/results/halo/memory_pilot/scn_qualification.json data/figures/halo_memory_pilot_2026-09-07.png
python3 experiments/halo/memory_pilot_frontier.py data/results/halo/memory_pilot/scn_report.json \
  data/results/halo/memory_pilot/scn_screens.json \
  data/figures/halo_memory_pilot_frontier_2026-09-07.png
```

This is the pre-registration's §9 block with three additions that write files and change no scored
number: the two `--json` flags on the report and screens, and the two figure calls.

Each reproduction control of §6 is one run of `spinchladni sg0.3 gl0 seed 777` into a directory outside
the repository, with one layer changed: a plain repeat; `PW_CHROMIUM_PATH` pointed at another installed
Chromium; or a page revision built by **its own** `make_test_page.py`, taken from the same commit — both
layers must be pinned together, and the build step must be checked, or the control silently runs the
current instrument:

```bash
git show <rev>:tests/halo/make_test_page.py > tests/halo/.mtp_period.py
python3 tests/halo/.mtp_period.py --from-git <rev>   # must succeed; it overwrites rc-test.html
# ... run the cell into a scratch directory, then restore rc-test.html and check its sha256
```

Their hashes and per-epoch correlations are in
[`reproduction_probe.json`](../data/results/halo/memory_pilot/reproduction_probe.json), written by
`experiments/halo/memory_pilot_reproduction.py`.

The meshes are not distributed by a clone. A run is reproducible tick for tick from its seed, on a build
that is named.
