# Qualify the memory estimator before another particle campaign

Author: Aldrin Payopay · September 5, 2026 · GPL-3.0-only

This is a proposed offline qualification step, based on the [registered protocol](../preregistrations/2026-09-02_halo_cross_epoch_memory.md) and the [recorded 60-run audit](../../analysis/2026-09-02_cross_epoch_memory_preregistered.md). No new analysis or particle run was performed for this assessment. The original statistic was confounded by sampling support and radial geometry; the existing result supplies no NRM verdict.

## Available observations

The original local collection is `/Volumes/dual/nested-resonance-memory-archive/data/results/halo/memory_prereg/`: 60 run JSON files and 60 matching `.mesh.f32` files. Each raw file contains 24 density meshes of 32³ float32 cells (3,145,728 bytes); together they contain 1,440 epoch meshes and 188,743,680 raw bytes. Recorded metadata specifies 4,194,304 particles, 24 ten-second epochs and three seeds per parameter cell. The inspected metadata recorded no page errors, missing meshes or size mismatches. This assessment did not recompute every binary hash or inspect all mesh values.

The raw meshes are ignored, untracked local data; they are **not distributed by a Git clone** and are not public evidence attachments. Nine selected raw/JSON pairs are now preserved locally in `/Volumes/dual/DUALITY-ZERO-V2/experiments/results/halo/memory_estimator_qualification/input/`. The sibling `input-provenance.json` records the source and SHA-256 values. The preservation check verified all 18 files byte for byte (28,704,849 bytes); no estimator was run. Use this DEV copy for future work.

The selection contains all three recorded seeds from each of `spinchladni_sg0.5_gl0`, `default_sg0.3_gl0` and `default_sg0_gl0`: respectively useful examples of angular structure, radial dominance/clamping and nearly empty scoring support. This selection follows the published audit and is therefore exploratory, not a held-out confirmatory sample. Eligibility must be checked per epoch; a low median clamp fraction does not certify every epoch.

Mesh snapshots are pre-rescale observations at the boundary minus one tick; JSON epoch rows describe the post-boundary state. Do not align them as if they were simultaneous. Raw records lack an embedded instrument source hash; historical build provenance belongs to the protocol and audit. The newer observation bench cannot retrospectively certify those records. Exclude `memory_prereg_voided/` from substantive inference: its discarded runs include page errors and a truncated record.

## Narrow next experiment

Qualify a support-matched, radial-controlled statistic on these saved meshes before commissioning another full particle grid. Review [the existing loader](../../experiments/halo/memory_prereg_analyze.py), [radial artefact diagnostics](../../experiments/halo/memory_prereg_artefact.py) and [old-statistic power analysis](../../experiments/halo/memory_prereg_power.py); the old power result does not calibrate a replacement statistic.

Use cell-center coordinates centered at 15.5, explicit resampling, and identical effective resolution, masks and weights for each observed/null pair. Remove each field's own radial mean. First qualify a lag-one comparison against matched nulls; do not subtract raw two-scale and four-scale correlations with unequal footprints or smoothing. Define minimum mass and residual variance before examining the new scores. Empty or purely radial support is **not measurable**, rather than a zero-memory observation.

The compact relic domains in the original scale mapping do not reach the cavity-wall shell. Moving the mask to that shell changes the question. Angular recurrence on a shell can be studied as a newly specified estimand; it does not rescue the original passive-relic claim.

Predeclare falsifiers:

- Radialized recorded density produces a claimed angular-memory signal.
- Matched surrogate controls exceed the declared false-positive allowance.
- A labeled, mass-preserving angular injection cannot be recovered at the intended sensitivity.
- The conclusion depends on arbitrary interpolation, radial binning or sparsity choices.
- Available support lacks sufficient mass or residual variance to measure the proposed effect.

Surrogates are diagnostic controls, not automatically physical counterfactuals. Independent seeds can share a degenerate radial profile, and time reversal is not guaranteed to remove memory. Calibrate uncertainty without treating spatial cells or adjacent epochs as independent observations; do not inherit the old 0.1 threshold without qualification.

Even a valid lag-one advantage over lag two can reflect ordinary persistence or decorrelation. Saved 32³ densities cannot recover particle identities, velocities, finer spatial detail or a causal intervention. A causal seeding claim would require a newly registered, targeted intervention after estimator qualification. These existing records can test whether an estimator is usable; they cannot by themselves establish that claim.
