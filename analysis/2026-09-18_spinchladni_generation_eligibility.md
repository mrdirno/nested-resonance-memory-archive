# The generated non-static condition reproduces the pilot's near-miss on a fresh pinned instrument: two independent triples peak at 10 and 9 eligible epochs, both short of twelve, and the ceiling is a seed lock (E3), not run length

Author: Aldrin Payopay · September 18, 2026 · GPL-3.0-only

## Summary

Ring 22 established, from the sealed 81-run record, that no recorded run is both
measurable and non-static, and that the one non-static regime within reach of the
12-epoch eligibility floor — a spinning chamber at moderate self-gravity,
`spinchladni sg0.3 gl0` — had reached 10 of 12 eligible epochs on the pilot
instrument but was un-measurable. Because a staticness gate cannot be validated by
re-screening the record (applied to the grid it empties the eligible set), Ring 22
handed the successor one concrete first experiment: **generate** that regime — not
select it from disk — on a single pinned instrument, and ask whether it can be
pushed to sustain **≥ 12 eligible epochs while A3 stays below 0.99**, needing at
least two independent triples to separate a systematic shift from realisation noise.

This note is that generation, scored with the frozen scorer (`sha 7619ef6b`,
unmodified) and the staticness screen (`memory_pilot_staticness.py`, unmodified,
which sits beside the scorer and changes nothing it does). Six new runs of
`spinchladni sg0.3 gl0` at 4,194,304 particles and 24 epochs were produced on one
pinned instrument (behavioural identity `sim_digest 40bfdb68`), in two independent
seed triples: the grid's standard seeds (777, 12345, 31337) and three
transcendental-digit seeds (2718, 16180, 57721).

The measured result:

- **The pilot's near-miss reproduces, and it is systematic across two triples.**
  Triple 1 clears **10, 10, 9** eligible epochs of the 22 the scorer reads; triple
  2 clears **8, 7, 9**. The best non-static run reaches **10 eligible epochs** — the
  same value the pilot's best run reached on a different instrument — and neither
  triple, and no single run of the six, clears the 12-epoch floor. The near-miss at
  ten is a property of the regime on this instrument, not a lucky seed.
- **Every one of the six runs is non-static.** Full-field lag-one density
  correlation A3 = 0.111–0.208 (static is ≥ 0.99); the mass centroid travels
  7.3–13.4 cells across the run. The condition passes every pilot screen (A1–A5):
  the worst raw cross-seed correlation is 0.785 (below the 0.99 near-copy line), so
  these are not degenerate re-runs of one field.
- **0 of 6 runs is measurable; both triples score "insufficient support."** The
  refusal is the eligibility floor (10 and 9 < 12), reached before the run-level
  seed-balance gates E5/E5b even bind (neither fires on any run).
- **The binding constraint is E3, a seed lock.** Across the six runs the most-failed
  per-epoch gate is E3 (cross-seed relic-template correlation ≥ 0.9): it rejects
  **8–10 of the 22 scored epochs** in every run, and is the strictly-highest gate in
  five of six runs (tied with E2 at seed 16180, 9 and 9). In roughly forty percent of
  epochs at least one pair of the three seeds produces near-identical relic templates,
  so the epoch cannot distinguish an own-relic effect from a stranger's and is
  refused. E1 (mask mass) fails in 2–5 epochs and E2 (participation / residual
  variance) in 5–9 — E2 reaches E3's count only at that one seed, so the seed lock,
  not mass or participation, is the ceiling.
- **The "run longer than 24 epochs" lever is dead under the frozen scorer.** The
  scorer scores epochs `[FIRST_SCORED, LAST_SCORED] = [3, 24]` (`memory_estimator_qualify.py:56`),
  so a run of any length yields at most 22 scored epochs. Extending past 24 epochs
  adds zero eligible epochs; the only lever that can move the metric without
  patching the frozen scorer is a parameter move.

**Nothing about nested resonance memory is decided.** The finding is negative and
sharpening: the named non-static regime, generated fresh on a pinned instrument and
confirmed across two triples, holds at a ceiling of ten eligible epochs, and that
ceiling is a seed lock the frozen scorer names E3, in tension with staticness.

## Provenance and grounding

- **Instrument (one pin, verified).** All six runs are on the same behavioural
  instrument: `instrument_identity.py` gives `sim_digest = 40bfdb685f82902a` for the
  test page, for the source page at the runs' git rev `aad6330c`, and for the current
  working tree — identical across all three. Five runs recorded
  `source_page_sha256 = c0f78b88…` (the aad6330c page); the sixth (seed 57721,
  regenerated here after the originating cycle left it truncated) recorded
  `1fc99fce…`. Those whole-file hashes differ only by appended ring HTML comments;
  the sim_digest — the Ring-18 identity that excludes comments and prose — is the
  same, which is exactly the case `instrument_identity.py` was built to read. The
  two are one instrument.
- **Scorer, unmodified and frozen.** `experiments/halo/memory_estimator_qualify.py`
  hashes to `7619ef6b…`, which equals the `script_sha256` in every committed output
  and the sha the synthetic control receipt was written under. The staticness screen
  is unmodified vs HEAD. No gate, threshold or protocol text was touched; the
  staticness gate (A3 < 0.99) is stated here, before scoring, and is not patched
  into the frozen scorer.
- **Inputs sealed; meshes regenerable.** Each triple was scored against a committed
  manifest of its three JSON and three `*.mesh.f32` files (`triple1_manifest.json`,
  `triple2_manifest.json`); both scorings report `manifest_check.verified = true`.
  The `*.mesh.f32` binaries are gitignored and, as prior rings noted, regenerable by
  the run harness; the run JSON are committed, so every number here rests on
  committed files plus the frozen scorer.
- **Grid and pilot are not pooled.** This is one condition on one instrument; the
  pilot's 10/10/9 is cited only as the value the successor was handed, on a
  different behavioural class (Ring 18), and no statistic mixes the two.

## The two triples

Eligible epochs are of the 22 the scorer reads (epochs 3–24). A3 is the full-field
lag-one density correlation from the unmodified staticness screen.

| triple | seed | eligible / 22 | A3 (full) | centroid travel | measurable | most-failed gate |
|--------|------|--------------:|----------:|----------------:|-----------:|------------------|
| 1 | 777   | **10** | 0.208 | 7.29  | no | E3 (10) |
| 1 | 12345 | **10** | 0.159 | 10.28 | no | E3 (10) |
| 1 | 31337 | 9  | 0.192 | 8.38  | no | E3 (8) |
| 2 | 2718  | 8  | 0.113 | 13.38 | no | E3 (8) |
| 2 | 16180 | 7  | 0.111 | 11.09 | no | E2 (9), E3 (9) |
| 2 | 57721 | 9  | 0.199 | 9.30  | no | E3 (8) |

Best non-static eligible epochs at the fixed instrument: **10** (baseline 10, target
12). Per-triple best: 10 (triple 1), 9 (triple 2). Both triples score
`insufficient support`; `measurable_runs_main = []`, `detected_runs_main = []`,
`below_floor_runs_main = []` (no run reaches the floor to be tested for a below-floor
signal). E5 collapse and E5b imbalance fire on none of the six.

## Why it stops at ten: the seed lock, in tension with staticness

The ceiling is E3 — the requirement that the three seeds' relic templates be
distinguishable (|cross-correlation| < 0.9) — not mask mass (E1), and save a single
tie at seed 16180 not participation (E2). In 8–10 of the 22 scored epochs of every
run, at least one seed pair's predicted relic residuals are ≥ 0.9 correlated — the
seeds are near-copies at the level the gate reads, in those epochs — so the epoch is
refused. This is the same seed lock
Rings 17, 18 and 21 kept meeting. Ring 21 showed one way to break it: a similarity
rescaling of the whole force made the seeds separable and produced measurable runs —
but it did so by collapsing the field to a static core (A3 = 1.0000), which is the
confound the whole programme exists to avoid. So the two properties the successor
needs are in direct tension on this regime: **break the seed lock (fewer E3
failures) without freezing the field (keep A3 < 0.99).** A moving field keeps the
seeds diverse enough to move but too similar in template to separate; a collapsing
field separates the templates but stops moving. Ten eligible epochs is where that
tension currently sits.

## What this hands the successor (round 2)

- The only lever that can raise eligible epochs without patching the frozen scorer
  is a **small parameter move** — the "run longer" half of the hypothesis is retired
  (the scorer caps at epoch 24). The move must reduce E3 failures (or, secondarily,
  E2 failures) in more of epochs 3–24 **while A3 stays below 0.99**.
- Candidate single-coordinate moves at the same pinned instrument, each testable as
  its own two-triple generation and each screened for staticness before it is
  scored: a small self-gravity step off 0.3 (0.25 / 0.35), a small drive change
  (`fieldExp`), or a magnetism change — the coordinates the Ring-19 override flags
  isolate. The measurement to beat is 10; the falsifier is that no non-static move
  clears 12 (the tension is fundamental to the regime), which would send the search
  to a different non-static preset.
- Two independent triples are the minimum, as here, so a systematic shift separates
  from realisation noise; report condition-level measurability beside A3 and eligible
  epochs per run, and make no memory claim from any static field.

## Falsifiers and what would change the reading

- If the six runs were not on one instrument, "systematic across two triples" would
  confound instrument with seed set. They share `sim_digest 40bfdb68` (verified);
  the differing whole-file hashes are appended ring comments only.
- If the runs were static, the eligibility would be the residual-of-a-collapsed-core
  confound Ring 15 retired. They are not: A3 = 0.111–0.208, centroids travel 7–13
  cells, and the staticness screen strikes nothing.
- If the seeds were near-copies, the E3 refusals would be an artifact of degenerate
  inputs rather than a real seed lock. They are not degenerate: worst raw cross-seed
  correlation 0.785, below the 0.99 line, and A1 does not strike.
- If a re-run of the frozen scorer did not reproduce these counts, the result would
  be void. It is deterministic (fixed permutation and shuffle seeds) and the manifest
  verifies; the committed `triple1_qualification.json` / `triple2_qualification.json`
  carry every per-epoch number.
- A genuine successor result would be a **generated** condition, non-static under A3,
  that clears the 12-epoch floor **and** is measurable at the condition level. This
  regime, at this parameter point, is not it — it holds at ten, un-measurable.

## Files

- Runs (committed JSON; `*.mesh.f32` gitignored, regenerable):
  `data/results/halo/memory_sgsweep/scn/spinchladni_sg0.3_gl0_seed{777,12345,31337,2718,16180,57721}_n4194304_e24.json`
- Sealed manifests + scored outputs (committed):
  `data/results/halo/memory_sgsweep/{triple1,triple2}_manifest.json`,
  `{triple1,triple2}_qualification.json`, `staticness_screens.json`
- Frozen scorer (untouched, sha 7619ef6b): `experiments/halo/memory_estimator_qualify.py`
- Staticness screen (unmodified): `experiments/halo/memory_pilot_staticness.py`
- Instrument identity: `experiments/halo/instrument_identity.py` (sim_digest 40bfdb68)
- Run harness: `tests/halo/memory_prereg_run.js`
- Ring 22 (the question this answers): `analysis/2026-09-17_corpus_staticness_vs_eligibility.md`
