# The recorded corpus holds no measurable non-static run: on the sealed grid every eligibility-clearing run is static, and the closest a moving field comes is ten epochs of a required twelve

Author: Aldrin Payopay · September 17, 2026 · GPL-3.0-only

## Summary

Ring 21 measured the drive-cut axis and handed the next protocol one requirement:
the successor is not another grid under the frozen protocol but a protocol that
**gates staticness (A3) before it scores**, because the frozen scorer will call a
static collapsed field measurable through its monopole-removed residual. Ring 21
established that on the six similarity arms it scored. It did not ask the prior
question of the whole recorded corpus: **has any recorded run ever been both
measurable and non-static, and does anything that is non-static even reach the
frozen scorer's eligibility floor?**

This note answers that from committed, sha-sealed outputs, without recomputing on
any gitignored mesh. It cross-tabulates staticness (A3, the median epoch-to-epoch
full-field density correlation) against measurability (eligible epochs and the
measurable flag) across the two recorded sets the programme has: the 60-run
pre-registered grid (2026-09-06) and the 21-run measurability pilot (2026-09-07).

The measured result:

- **On the 60-run grid — one instrument, sha-sealed — every run that clears the
  12-epoch eligibility floor is static.** Six of the sixty runs clear the floor
  (`default sg0.3 gl0` at 19/17/17 eligible epochs, `default sg0.5 gl0` at
  15/15/15). All six have A3 = 0.99995-0.99999, static by the >= 0.99 rule. **Zero
  of the forty-eight non-static runs clears the floor;** the closest a moving field
  comes is 8 eligible epochs (`spinchladni sg0.5 gl0`), four short. So on this
  instrument a staticness gate removes exactly the six runs nearest to measurable
  and leaves the eligible set empty.
- **The coupling is a shared cause, not a law: it inverts on the pilot's
  instrument.** The pilot is a different behavioural class (Ring 18: its records
  are csv head-22 / rows-28, the grid's are rows-22). On the pilot the single
  most-eligible condition is a **moving** field — `spinchladni sg0.3 gl0` at
  10/10/9 eligible epochs, A3 = 0.19 — while the static `goldstair` conditions
  (A3 = 1.0000) get **zero** eligible epochs. Whichever instrument, the moving
  field still falls short of the 12-epoch floor and nothing is measurable.
- **The corpus-wide invariant: zero of the 81 recorded runs is both measurable
  and non-static, and zero non-static run anywhere clears the eligibility floor.**
  The two moving fields that come closest are both a spinning chamber at moderate
  self-gravity — 10 of 12 (pilot) and 8 of 12 (grid) — and both are un-measurable.

**Nothing about nested resonance memory is decided.** The finding is a negative
one that sharpens the successor's requirement and, for the first time, hands it a
concrete non-static starting regime: a moving field has already reached 10 of the
12 eligible epochs the floor needs, so the successor is not looking for a
regime that does not exist, but for a small extension of one that already
half-clears — under a protocol that gates staticness so the extension is not
purchased by collapse.

## Provenance and grounding (no gitignored mesh is trusted)

Every number for the grid comes from two committed files whose seal is checked
here, so the measurement stands on git history rather than on the 60 `*.mesh.f32`
binaries, which are gitignored and, as Ring 17 noted, regenerable:

- **A3 staticness per grid run:** `data/results/halo/memory_estimator_qualification/`
  `diagnostics_2026-09-06.json` → `static_runs[run].consecutive_epoch_correlation_median`.
  This is the median lag-one full-field Pearson, computed by Ring 16's diagnostics
  when the meshes were fresh and committed 2026-09-06. It covers all 60 runs.
- **Measurability per grid run:** the same directory's `qualification.json` →
  `runs[].lag1.{eligible_epochs, measurable}`, verdict `insufficient support`,
  `measurable_runs_main = []`.
- **The two describe the same sealed scoring.** `diagnostics.qualification_result_sha256`
  = `5ed4a4a0…` equals the sha256 of `qualification.json` on disk (checked). The
  scorer `memory_estimator_qualify.py` hashes to `7619ef6b…`, which equals both
  `diagnostics.qualify_script_sha256` and the `script_sha256` inside
  `qualification.json` — the same frozen scorer Ring 21 re-verified.

The pilot half is grounded differently, by byte-verification and an independent
re-run rather than by a stored number:

- **All 42 pilot files (21 JSON + 21 `*.mesh.f32`) verify byte-for-byte against the
  committed `data/results/halo/memory_pilot/scn-manifest.json` sha256 list** (ok=42
  bad=0 missing=0, not_manifested=[]).
- **A3 was then recomputed** by running the frozen staticness screen
  `experiments/halo/memory_pilot_staticness.py` (unmodified vs HEAD) on that
  verified directory — an independent code path from the grid's stored diagnostics —
  and is reported per condition as the mean of the three seeds' full-field medians
  (`self_full_median`), the same per-condition aggregation the grid table uses, so
  the two A3 columns are the same statistic. The classification is threshold-robust
  either way: goldstair is 1.0000 and every other pilot condition is below 0.45.
- **Measurability per pilot run** comes from the committed
  `data/results/halo/memory_pilot/scn_qualification.json` → `runs[].lag1`.

## The 60-run grid: staticness against eligibility

A3 threshold for "static" is the screen's own `STATIC_AT = 0.99`. Eligibility
floor is 12 epochs (the frozen protocol's E5-region entry). Per condition, the
maximum eligible epochs across the three seeds beside the mean A3:

| condition | mean A3 | static? | max eligible / 24 | measurable |
|-----------|--------:|---------|------------------:|-----------:|
| default sg0.3 gl0   | 1.0000 | **static** | **19** | 0/3 |
| default sg0.5 gl0   | 1.0000 | **static** | **15** | 0/3 |
| default sg0.8 gl0   | 1.0000 | **static** | 6 | 0/3 |
| spinchladni sg0.5 gl0 | 0.107 | moving | 8 | 0/3 |
| spinchladni sg0.3 gl0 | 0.154 | moving | 6 | 0/3 |
| spinchladni sg0.5 gl0.5 | 0.061 | moving | 4 | 0/3 |
| spinchladni sg0.3 gl0.5 | 0.030 | moving | 3 | 0/3 |
| default sg0.15 gl0  | 1.0000 | **static** | 2 | 0/3 |
| spinchladni sg0.8 gl0.5 | 0.395 | moving | 2 | 0/3 |
| spinchladni sg0.15 gl0.5 | 0.122 | moving | 1 | 0/3 |
| spinchladni sg0.8 gl0 | 0.258 | moving | 1 | 0/3 |
| default sg0.15 gl0.5 | 0.766 | moving | 0 | 0/3 |
| default sg0.3 gl0.5 | 0.974 | moving | 0 | 0/3 |
| default sg0.5 gl0.5 | 0.962 | moving | 0 | 0/3 |
| default sg0.8 gl0.5 | 0.962 | moving | 0 | 0/3 |
| default sg0 gl0     | 0.922 | moving | 0 | 0/3 |
| default sg0 gl0.5   | 0.558 | moving | 0 | 0/3 |
| spinchladni sg0 gl0 | 0.609 | moving | 0 | 0/3 |
| spinchladni sg0 gl0.5 | 0.385 | moving | 0 | 0/3 |
| spinchladni sg0.15 gl0 | 0.439 | moving | 0 | 0/3 |

Counts: **12 static runs, 48 non-static, 0 measurable; 6 runs clear the 12-epoch
floor, all 6 static; 0 non-static run clears it; 0 runs are both measurable and
non-static.** The six floor-clearers, with their sealed A3:

| run | eligible | A3 (full field) |
|-----|---------:|----------------:|
| default sg0.3 gl0 seed777   | 19 | 0.99995 |
| default sg0.3 gl0 seed12345 | 17 | 0.99999 |
| default sg0.3 gl0 seed31337 | 17 | 0.99999 |
| default sg0.5 gl0 seed777   | 15 | 0.99999 |
| default sg0.5 gl0 seed12345 | 15 | 0.99995 |
| default sg0.5 gl0 seed31337 | 15 | 0.99999 |

There is a clean gap. The four static `default gl0` conditions all sit at mean
A3 >= 0.99997 (the six floor-clearers among them, per run, at >= 0.99995); the
highest-A3 *moving* condition is `default sg0.3 gl0.5` at 0.974. Nothing lies in
(0.974, 0.99997), so the classification does not depend on where in 0.97-0.999
the threshold is placed.

**The mechanism is a shared cause.** On the `default` preset the field collapses
under self-gravity to a compact core. That collapse is what produces a persistent,
separable relic — which is what the frozen scorer counts as an eligible epoch — and
it is the same collapse that freezes the field, driving A3 to 1. Eligibility and
staticness are coupled on this instrument because both are downstream of collapse.
The scorer rewards a persistent relic; the cheapest way to make a persistent relic
is to stop moving.

## The 21-run pilot: the coupling inverts on a different instrument

The pilot swept four scenarios that move to different degrees. Recomputed A3 (the
frozen screen, unmodified), reported per condition as the mean of the three seeds'
full-field medians — the same aggregation the grid table above uses — beside the
committed eligibility:

| condition | mean A3 (full field) | static? | eligible (3 seeds) | measurable |
|-----------|---------------------:|---------|-------------------:|-----------:|
| spinchladni sg0.3 gl0 | 0.186 | moving | **10, 10, 9** | 0/3 |
| hardprint sg0.3 gl0   | 0.010 | moving | 1, 1, 1 | 0/3 |
| spinchladni sg0.15 gl0 | 0.434 | moving | 1, 1, 1 | 0/3 |
| stillspindle sg0.15 gl0 | 0.287 | moving | 1, 1, 0 | 0/3 |
| hardprint sg0.15 gl0  | 0.018 | moving | 0, 0, 0 | 0/3 |
| goldstair sg0.15 gl0  | 1.0000 | **static** | 0, 0, 0 | 0/3 |
| goldstair sg0.3 gl0   | 1.0000 | **static** | 0, 0, 0 | 0/3 |

Here the single most-eligible condition is **moving** (`spinchladni sg0.3 gl0`,
10 epochs, A3 = 0.19), and the only static conditions (`goldstair`, the pilot's
drive-cut arm, A3 = 1.0000) get **zero** eligible epochs. So the grid's
"static ⇒ eligible" ordering is a property of the grid's instrument and its
collapsing `default` preset, not a law of the estimator: change the instrument and
a moving field becomes the most eligible one. This is the same instrument-identity
split Ring 18 measured (grid rows-22 vs pilot rows-28); the two halves are not on a
common scale and are not pooled here.

Note `stillspindle` is misleadingly named: its A3 is 0.29, it moves. The only
static thing in the pilot is `goldstair`.

## What is invariant across both instruments

Whatever the instrument:

1. **No recorded run is both measurable and non-static.** 0 of 81. Measurability
   is 0 everywhere, so this is currently vacuous on the "measurable" side — but it
   is the exact conjunction Ring 21 named as the shape of a memory positive, and
   the corpus contains no instance of it.
2. **No non-static run clears the 12-epoch eligibility floor.** The closest are
   10 (pilot `spinchladni sg0.3 gl0`) and 8 (grid `spinchladni sg0.5 gl0`), both
   spinning chambers at moderate self-gravity, both un-measurable.
3. **The nearest approach to a non-static eligible field is a spinning chamber at
   self-gravity 0.3-0.5, gain/loss 0.** That is the one direction the record marks
   as promising for a non-static path to eligibility.

## What this hands the successor

- **A staticness gate cannot be validated by screening the recorded grid**: applied
  to the grid it removes the only six runs within reach of measurable and leaves
  nothing eligible. The successor's non-static-and-measurable condition does not
  exist on disk and must be generated, not selected.
- **But the successor is not chasing a phantom.** A moving field (`spinchladni`
  sg0.3, gl0) has already reached 10 of the 12 eligible epochs the floor requires,
  on the pilot instrument. The concrete first experiment for the staticness-gating
  protocol is whether that regime — spinning, moderate self-gravity, no gain/loss —
  can be pushed to sustain >= 12 eligible epochs (longer runs, or a small parameter
  move) **while A3 stays below 0.99**, and whether it then becomes measurable at the
  condition level. That is a new generation at a named starting point, on a single
  pinned instrument, not a re-score of the record.
- **The 2026-09-05 frozen scorer and protocol are untouched** (sha 7619ef6b). This
  note changes no gate and no threshold; it reads committed outputs and re-runs one
  unmodified screen.

## Falsifiers and what would change the reading

- If the grid's A3 and eligibility did not come from one sealed scoring, the join
  would be unsound. They do: `diagnostics.qualification_result_sha256` equals the
  on-disk `qualification.json` sha256, and both name scorer `7619ef6b`.
- If the pilot meshes on disk were not the recorded ones, the pilot A3 would be
  ungrounded. They verify byte-for-byte against the committed manifest (42/42).
- If some non-static run did clear the floor and was missed, invariant 2 would
  fall. The full per-condition table above is exhaustive over all 27 conditions of
  both sets; the maximum eligible epochs of any non-static run is 10.
- If the grid and pilot were pooled, the instrument split would be hidden. They are
  reported separately and explicitly not pooled, because Ring 18 showed they are
  different behavioural classes.
- A genuine successor result would be a **generated** condition that is measurable
  under the frozen scorer AND non-static (A3 < 0.99) AND detected at the condition
  level. None exists in the record; the nearest is 10 of 12 eligible epochs, moving,
  un-measurable.

## Files

- Grid staticness (committed): `data/results/halo/memory_estimator_qualification/diagnostics_2026-09-06.json` (`static_runs`)
- Grid measurability (committed): `data/results/halo/memory_estimator_qualification/qualification.json`
- Pilot manifest (committed, byte-verified): `data/results/halo/memory_pilot/scn-manifest.json`
- Pilot measurability (committed): `data/results/halo/memory_pilot/scn_qualification.json`
- Frozen staticness screen (unmodified): `experiments/halo/memory_pilot_staticness.py`
- Frozen scorer (untouched, sha 7619ef6b): `experiments/halo/memory_estimator_qualify.py`
- Instrument-identity split (Ring 18, source for grid rows-22 vs pilot rows-28): `analysis/2026-09-09_measurability_noise_and_instrument_identity.md`
