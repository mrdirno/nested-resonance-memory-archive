# A single-coordinate drive cut breaks the seed lock Ring 24 named: halving the drive turns the ten-epoch near-miss into the first non-static measurable condition in the record — but the own-relic detection does not survive the second triple

Author: Aldrin Payopay · September 18, 2026 · GPL-3.0-only

## Summary

Ring 24 generated the non-static regime `spinchladni sg0.3 gl0` fresh on one pinned
instrument, found it holds at ten eligible epochs of a required twelve across two
triples, and named the ceiling exactly: not mass and not run length but **E3, a
cross-seed seed lock** — in roughly forty percent of epochs at least one pair of
the three seeds produces near-identical relic templates, so the epoch is refused.
It left the successor one question: which **single-coordinate parameter move**, at
this pinned instrument, lowers E3 failures while A3 stays below 0.99 — a
self-gravity step, a drive (`fieldExp`) change, or a magnetism change — each its
own two-triple generation, measurement to beat 10, falsifier that no non-static
move clears 12.

This note answers it. Two moves were generated on the same pinned instrument as
Ring 24: the drive cut as two triples (six runs — the grid seeds 777, 12345, 31337
and the transcendental-digit seeds 2718, 16180, 57721), and the magnetism raise as
one triple (grid seeds, three runs), **nine runs in all**, at 4,194,304 particles
and 24 epochs. Every run recorded the same driven-page hash `test_page_sha256 =
46405b3d`; that page's behavioural identity — its `sim_digest`, which excludes
comments and prose — is `40bfdb68`, Ring 24's pin, re-checked on the working tree
here. Scored with the frozen scorer (`sha 7619ef6b`, unmodified) and the unmodified
staticness screen. The drive term is `amp * fscale * field` with `amp = 10^fieldExp`;
the magnetism term is `mag * 30 * cross(v, B)`.

The measured result:

- **A magnetism increase makes the lock worse, not better — and shows why.** `mag
  0.4 -> 0.6` collapses eligibility from 10 to **0/1/0**, drives E3 to **21-22 of 22
  epochs**, and the three seeds' final fields correlate at **0.996-0.998**: the
  Lorentz term saturates the force cap (clamp share ~52% against the base regime's
  ~7%), so every seed is pinned to the same clamp geometry and the seeds
  *synchronise*. Adding shared force tightens the lock.
- **Halving the drive breaks the lock completely, and it is robust.** `fieldExp 2 ->
  1.7` (drive amplitude 100 -> 50) sends E3 to **0 of 22 in every one of the six
  runs, both triples**. The three seeds decorrelate: the raw cross-seed correlation
  of the final field falls from the base regime's 0.43-0.79 to about zero
  (-0.013 to 0.145). Weakening the shared drive lets each seed's own structure
  dominate the relic, so the templates separate.
- **This is the first non-static condition in the programme's record that clears the
  eligibility floor and is measurable.** Triple 1 clears **19, 17, 17** eligible
  epochs (all three measurable); triple 2 clears **13, 12, 10** (two measurable).
  Five of the six runs clear the 12-epoch floor and five of six are measurable, all
  non-static (A3 0.043-0.136, well below the 0.99 static line). Ring 22's standing
  invariant — zero of 81 recorded runs both measurable and non-static — is
  inverted: here five of six are.
- **But no memory signal is established.** Own-relic *detection* (the run's own
  block-image predicts its next epoch better than a stranger's, S >= 0.02 and
  p < 0.05) fires in **2 of 3 triple-1 runs** (S = 0.042 and 0.035, just above the
  0.02 line) and in **0 of 3 triple-2 runs** (S = 0.015 and -0.011). Detection is
  borderline and does not reproduce across the two seed sets, so the measurable
  condition carries no reproducible own-relic effect. The seed lock is broken and
  the field is measurable; whether it *remembers* is the next question, not a
  finding here.

**Nothing about nested resonance memory is decided.** What is decided is narrower and
real: the E3 seed lock that has bounded this regime since Ring 17 is not fundamental
to a moving field — it is an artifact of the shared drive's strength, and a single
coordinate removes it while the field keeps moving. Measurability follows;
reproducible detection does not.

## Provenance and grounding

- **One instrument, nine runs.** Every run recorded the same driven-page hash
  `test_page_sha256 = 46405b3d…` and was produced at git rev `d67ddd16` (HEAD). That
  page's `sim_digest` is `40bfdb68…` — the Ring-18 behavioural identity that excludes
  comments and prose — Ring 24's pin, re-checked on the working tree here. (The
  sim_digest is a property of the page, verified once on it, not a field stored in
  each run record; the per-run pin is the driven-page hash `46405b3d`.) Each run records its single override in `params.overrides` and reads the
  applied value back off the page: `fieldExp = 1.7` with `selfgrav 0.3`, `mag 0.4`
  unchanged for move B; `mag = 0.6` with `fieldExp 2`, `selfgrav 0.3` unchanged for
  the magnetism arm. One coordinate moves in each; nothing else.
- **Scorer frozen and unmodified.** `memory_estimator_qualify.py` hashes to
  `7619ef6b…`, the value inside every committed output. The synthetic control receipt
  reused here (`data/results/halo/memory_estimator_qualification/synthetic.json`) was
  written under that same script sha, which the scorer verifies before it will run.
  The staticness screen (`memory_pilot_staticness.py`) is unmodified. No gate,
  threshold or protocol text was touched; the staticness gate (A3 < 0.99) is stated
  here, before scoring, not patched into the frozen scorer.
- **Pipeline validated against the record.** The same scoring harness, run on Ring
  24's committed triple 1, reproduces its numbers exactly (10/10/9 eligible, E3
  8-10, A3 0.16-0.21, "insufficient support"), so the round-2 numbers stand on the
  frozen scorer, not on a re-implementation.
- **Inputs sealed; meshes regenerable.** Each triple was scored against a committed
  per-triple manifest of its three run JSON and three `*.mesh.f32` files, both
  reporting `manifest_check.verified = true`. The `*.mesh.f32` binaries are gitignored
  and regenerable by the run harness; the run JSON are committed.

## The two moves, measured

Eligible epochs are of the 22 the scorer reads (epochs 3-24). A3 is the full-field
lag-one density correlation from the unmodified staticness screen. Cross-seed is the
raw Pearson of the last epoch's full density between seed pairs (the screen's own A1
statistic, an independent code path from the scorer's E3).

| condition | seeds | eligible | E3 fails | measurable | detected | A3 | cross-seed |
|-----------|-------|---------:|---------:|-----------:|---------:|----:|-----------:|
| base (Ring 24) | 777/12345/31337 | 10/10/9 | 8-10 | 0/3 | 0/3 | 0.16-0.21 | 0.43-0.79 |
| **mag 0.6** | 777/12345/31337 | **0/1/0** | 21-22 | 0/3 | 0/3 | 0.74 | **0.996-0.998** |
| **fieldExp 1.7** t1 | 777/12345/31337 | **19/17/17** | **0/0/0** | **3/3** | 2/3 | 0.04-0.11 | ~0 |
| **fieldExp 1.7** t2 | 2718/16180/57721 | **13/12/10** | **0/0/0** | **2/3** | 0/3 | 0.07-0.14 | ~0 |

Per-run detection statistics for the drive cut (S = own-relic contrast, doubly
centred; p from block relabelling):

| triple | seed | eligible | E1 | E2 | E3 | measurable | detected | S | p |
|--------|------|---------:|---:|---:|---:|-----------:|---------:|----:|----:|
| 1 | 777   | 19 | 3 | 2 | 0 | yes | **yes** | 0.042 | 0.022 |
| 1 | 12345 | 17 | 4 | 3 | 0 | yes | no | 0.006 | 0.096 |
| 1 | 31337 | 17 | 3 | 5 | 0 | yes | **yes** | 0.035 | 0.002 |
| 2 | 2718  | 13 | 2 | 8 | 0 | yes | no | 0.015 | 0.163 |
| 2 | 16180 | 12 | 5 | 10 | 0 | yes | no | -0.011 | 0.807 |
| 2 | 57721 | 10 | 2 | 12 | 0 | no | — | — | — |

Best non-static eligible epochs at the fixed instrument: **19** (baseline 10, target
12) — the target is exceeded, and five of six runs clear the floor. Every triple
scores `insufficient support` at the grid level; this is not a falsifier firing but
the verdict cascade: `qualified` requires `F5` to pass, and `F5` passes only with at
least **three measurable conditions** (`memory_estimator_qualify.py:827`), while
`F3` recovery needs at least six measurable runs. A single condition scored as a
three-seed matrix cannot reach either, whatever the eligibility. On both triples of
the drive cut, `F1` (identity controls), `F2` (false-positive controls, including
the shared-drive heterogeneous-noise family) and `F4` (robustness) all pass.

## Why the drive cut works and the magnetism raise back-fires

The chamber's force sums several terms that every seed feels identically; the seeds
differ only in their initial particle positions. Two of those terms converge the
seeds onto a common structure. The **drive** `amp * fscale * field` is a fixed
spatial pattern imprinted on all seeds — the scorer's own synthetic model notes a
shared drive holds the coarse templates' cross-correlation near 0.8, just inside E3.
In the base regime the real drive imprints *past* that: templates correlate above
0.9 in ~40% of epochs (E3 fails). Halving the amplitude (100 -> 50) weakens the
imprint enough that each seed's own initial structure dominates the relic, and the
templates separate — measured directly as the raw cross-seed correlation collapsing
from 0.43-0.79 to ~0, and read by the scorer as E3 = 0.

The magnetism raise fails for the opposite reason and proves the mechanism by
contradiction. `mag * 30 * cross(v, B)` is a velocity-dependent force; at 0.6 it
saturates the force cap (clamp share ~52% against ~7% at base). A clamped force is
not the physical force law but the cap's fixed geometry, which is the *same* for
every seed, so the seeds synchronise — their final fields correlate at 0.996-0.998,
and E3 fails in nearly every epoch. The lesson is not "force separates seeds" but
"**less shared forcing** separates seeds": adding force (magnetism) tightens the
lock by saturating the cap; removing force (drive) loosens it. This also resolves
the tension Ring 24 posed — break the lock without freezing the field — the right
direction keeps A3 *lower* than base (0.04-0.14 vs 0.16-0.21), because a weaker drive
is a field that moves more freely, not less.

## The honest limit: measurable is not remembered

Measurability here means a run clears every eligibility gate and passes the
per-run detection test's floor; it does not mean a reproducible own-relic effect.
Detection fires in two of three triple-1 runs, with S only just above the 0.02 line,
and in none of triple 2, where S sits at zero. Across the whole false-positive
family the scorer calibrates a ~5-7% chance detection rate, so two of six is above
chance but not reproduced, and the sign of S even flips between seed sets. The
correct reading is that the drive cut delivers the *precondition* the programme
never had — a non-static field that is measurable — but the memory signal itself is
at or near the noise floor and seed-dependent. No memory positive is claimed.

The two triples also differ in *why* they clear the floor. E3 is zero in both, so
the seed lock is broken in both; the difference is E2 (participation), which fails
2-5 epochs for the standard seeds and 8-12 for the transcendental-digit seeds. The
eligibility gap (19/17/17 vs 13/12/10) is a participation effect of the seed set, not
a difference in the lock. That seed-dependence of participation is itself a carried
question.

## What this hands round 3

- **Reproducibility of detection.** Is S at the noise floor or is there a small real
  effect the two triples under-sample? More triples of `fieldExp 1.7`, and the
  distribution of S against the shuffled-relic floor per run, would settle it.
- **A path to the `qualified` verdict.** The grid verdict needs at least three
  measurable *conditions*. A small drive sweep — `fieldExp 1.6 / 1.7 / 1.8`, each a
  three-seed condition — could put three measurable conditions in one scoring, make
  `F3` recovery evaluable over six-plus runs, and for the first time let the frozen
  protocol return something other than `insufficient support`.
- **The threshold of the cut.** Does a gentler drive cut (`fieldExp 1.85`, amplitude
  70) also zero E3, or is 1.7 near a threshold? And does the lock return smoothly as
  the drive is restored — a dose-response that would confirm the drive as the lock's
  cause.
- **The participation seed-dependence** that separates the two triples' eligibility.

## Falsifiers and what would change the reading

- If the runs were not one instrument, "robust across two triples" would confound
  instrument with seed set. All nine share `test_page_sha256 46405b3d`, and the
  driven page's `sim_digest` is `40bfdb68`.
- If E3 = 0 were a degeneracy (undefined templates read as passing) rather than real
  separation, the claim would be hollow. It is not: the independent raw cross-seed
  correlation is ~0 for the drive cut and 0.996 for the magnetism arm, and the
  eligible epochs pass E1 (mass) and E2 (participation), so they carry real structure.
- If the drive cut had frozen the field like Ring 21's rescaling, eligibility would
  be the collapsed-core confound. It is not: A3 is 0.04-0.14 and lower than base.
- If detection had reproduced, a memory positive would be in reach. It did not
  (2/3 then 0/3), so none is claimed.
- If the magnetism arm had merely under-performed, the mechanism would be unproven.
  Instead it synchronised the seeds to 0.996-0.998 correlation, the exact opposite of
  separation, which is the mechanism's prediction under force-cap saturation.

## Files

- Runs (committed JSON; `*.mesh.f32` gitignored, regenerable):
  `data/results/halo/memory_sgsweep_r2/{fieldexp1.7_t1,fieldexp1.7_t2,mag0.6_t1}/spinchladni_sg0.3_gl0_seed*_n4194304_e24_*.json`
- Sealed manifests + scored outputs + staticness (committed):
  `data/results/halo/memory_sgsweep_r2/*/{manifest,qualification,staticness}.json`
- Frozen scorer (untouched, sha 7619ef6b): `experiments/halo/memory_estimator_qualify.py`
- Staticness screen (unmodified): `experiments/halo/memory_pilot_staticness.py`
- Instrument identity: `experiments/halo/instrument_identity.py` (sim_digest 40bfdb68)
- Run harness (override flags, force decomposition at lines 51-53): `tests/halo/memory_prereg_run.js`
- Ring 24 (the question this answers): `analysis/2026-09-18_spinchladni_generation_eligibility.md`
