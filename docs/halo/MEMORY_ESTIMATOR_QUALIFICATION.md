# Angular-recurrence estimator qualification

Author: Aldrin Payopay · September 5, 2026 · GPL-3.0-only

This design was written before implementing or inspecting new estimator scores. Input selection followed the historical audit and is exploratory. The immutable [design configuration](../../archive/reports/2026-09-05_halo_memory_estimator_design.json) records the freeze time and all decision thresholds. Results will be reported separately without retuning those thresholds.

## Question and measurement

Can a centered, radial-residual statistic measure **fixed-support angular recurrence** on the nine preserved density sequences while resisting radial-profile confounds? This changes the estimand from the failed compact rescaled-relic statistic. It does not test causal seeding or rescue the original NRM criterion.

The existing `pmCellOf` coordinate map and `labReadDensity` unpacking place cell centers at `i + 0.5 - 16`, with array axes `(z, y, x)`. Use a fixed sphere of radius 15.5 cells about `(15.5, 15.5, 15.5)` inside the 32³ grid. No interpolation, alignment search or unequal lag-dependent rescaling is performed. Group cells by the exact integer squared radius `(2*i-31)² + (2*j-31)² + (2*k-31)²`; subtract each field's own mean on each such shell. Exact groups avoid residual radial variation within arbitrary-width bins. Every score and its controls use the identical mask and uniform cell-volume weights.

The score is the normalized inner product of the two radial residual vectors. For an eligible pair, compare the current residual to all 24 proper cube rotations of the previous residual, including identity. The orientation rank is the fraction of these scores at least as large as the identity score, counting ties conservatively with tolerance `1e-12`. The qualification alarm requires rank ≤ 0.05 and correlation ≥ 0.10. With 24 rotations the smallest rank is 1/24.

Under a transformation-invariant null, the full-group construction supplies an exact rank test. HALO's forced, axis-dependent fields do **not** automatically satisfy that assumption, so recorded orientation ranks are descriptive diagnostics. They will not be presented as evidence of physical memory. This distinction follows the group-invariance requirement in [Hemerik and Goeman (2018)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6405018/).

## Eligibility and falsifiers fixed before scoring

Each field must have finite nonnegative density, at least 1% of its total density inside the mask, radial-residual RMS at least `0.001 ×` its masked mean density, and residual effective support `(sum r²)² / sum r⁴ ≥ 64` cells. An ineligible pair is **unmeasurable**, never a zero or negative finding. These are numerical-support criteria, not certification of physical validity. Post-boundary clamp records cannot certify the pre-boundary density snapshots.

All 216 recorded epochs are checked after radialization. Their residual energy must vanish to relative tolerance `1e-12`, and no radialized pair may be eligible. Simultaneous proper rotations must preserve scores to `1e-10`. Analytical injections must retain nonnegative density, preserve shell mass to relative tolerance `1e-12`, and recover their assigned residual correlation to `1e-10`.

Recorded lag-one comparisons use all 23 adjacent pairs per run; no pooled cell/epoch significance test is permitted. A run needs at least 12 eligible pairs for a descriptive summary. A predefined support sensitivity uses radius 14.5 with otherwise identical rules: at least 90% of primary eligible pairs must remain eligible and every shared pair's score difference must be ≤ 0.10. Failure limits spatial robustness; it must not trigger threshold or mask tuning.

## Analytical controls and power qualification

These fixtures are **analytical measurement tests, not physical evidence or new particle simulations**. Take the radial envelope of the first saved epoch from seed 12345 in each of the three parameter groups. This anchor rule is fixed before examining scores. Use independently seeded angular fields from two families: independent Gaussian cell values, and Gaussian values smoothed with an isotropic two-cell Gaussian kernel and reflecting cube boundaries. Both constructions commute with cube rotations; radial projection and a radial envelope preserve that symmetry.

For each of these six fixed envelope/family strata, generate 512 independent null pairs using independent angular fields. Also generate 128 independent pairs at each assigned residual correlation 0.15, 0.30 and 0.50. For power fixtures, Gram–Schmidt projection supplies two orthogonal radial residuals; their prescribed mixture sets the correlation. Rescale residual amplitudes separately so no density deviates from its radial envelope by more than 20%. Null pairs are **not** Gram–Schmidt orthogonalized, which would artificially force their correlation to zero. All fixture random streams derive from seed `2026090501`.

At least 95% of fixtures in each stratum must meet the unchanged eligibility criteria. The two-sided exact 95% Clopper–Pearson upper bound on null alarm frequency, and separately on rank-only exceedance frequency, must be ≤ 0.10. At correlation 0.30 the exact 95% lower bound on detection must be ≥ 0.80 in every stratum. The 0.15 and 0.50 results describe sensitivity and are not substitutes for a failed target. These tolerances are qualification limits; passing does not establish a 5% physical false-positive rate. Intervals apply only to independent analytical trials within each fixed stratum, using [SciPy's exact binomial interval](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html).

A static anisotropic density copied to both sides is also scored. A high recurrence score on this control is expected and demonstrates why recurrence alone cannot establish causal memory. Radial-only failure, excess null alarms, poor target power, insufficient support, failure of numerical invariances or sensitivity to the specified support change must all be retained in the result.

## Provenance and scope

The input path and manifest are specified in the frozen configuration. All 18 file hashes must match before analysis and again afterward. Inputs remain local-only; a public clone cannot reproduce the physical-data portion without them. The existing [integrity audit](../../archive/reports/2026-09-05_halo_memory_input_integrity.md), [next-step assessment](NEXT_MEMORY_ESTIMATOR.md) and [historical memory audit](../../analysis/2026-09-02_cross_epoch_memory_preregistered.md) retain their separate claims and limitations. No raw file, original protocol or historical result is changed by this qualification.

## Recorded result after the design freeze

The [qualification report](../../archive/reports/2026-09-05_halo_memory_estimator_report.md) records **failure to qualify across the nine selected runs**. Numerical invariances passed, but only 37 of 207 recorded pairs were eligible, eight runs lacked the required summary support, and the dense-profile analytical strata were unmeasurable. Four other analytical strata met the frozen null and target-power bounds. Static anisotropic controls demonstrate that a recurrence alarm is not causal memory. No threshold was changed after scoring, and no NRM verdict follows. The [machine-readable result](../../archive/reports/2026-09-05_halo_memory_estimator_results.json) preserves each gate and run.
