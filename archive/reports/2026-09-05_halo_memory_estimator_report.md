# Memory-estimator qualification: support limits prevent promotion

Author: Aldrin Payopay · September 5, 2026 · GPL-3.0-only

**The candidate failed its frozen qualification across the nine selected runs.** Input integrity and numerical invariances passed, but the required analytical calibration and recorded spatial-support criteria did not. This is a measurement-method result, not a positive or negative NRM finding.

The [design note](../../docs/halo/MEMORY_ESTIMATOR_QUALIFICATION.md) and [immutable configuration](2026-09-05_halo_memory_estimator_design.json) were saved before implementation and new scores. The configuration's recorded freeze time is **2026-09-05T12:26:03.596998+00:00**. This was a local design freeze, not an independently registered confirmatory experiment. No threshold or support was changed after viewing the result.

## What was measured

The estimator uses 15,408 cell centers within radius 15.5 of the 32³ grid's center at 15.5. It removes means over 120 exact squared-radius shells, then compares angular residuals on identical support. The 24 proper cube rotations include identity and use conservative ties. This avoids the old unequal-stride comparison, but measures fixed-support angular recurrence rather than rescaled relic retention.

All 216 radialized recorded meshes were correctly unmeasurable; no purely radial control acquired an eligible score. Simultaneous-rotation checks and shell-mass-preserving analytical injections passed their declared numerical tolerances. Maximum injected-correlation recovery error was **2.83e-15**. The eight analytical behavior tests passed in 0.043 seconds before the qualification run.

The script checked all 18 source hashes before and after analysis. Inputs, preservation manifest, frozen design and estimator source were unchanged during execution. No raw file was modified, and no physical simulation was run.

## Recorded support fails broadly

Only **37 of 207** adjacent epoch pairs were eligible. Eight of nine runs failed the predeclared minimum of 12 eligible pairs for a descriptive run summary. “Unmeasurable” is neither zero correlation nor evidence against memory.

| Recorded group | Seed | Eligible pairs | Permitted median correlation | Maximum radius-sensitivity difference |
| --- | ---: | ---: | ---: | ---: |
| default / sg 0.3 | 12345 | 0/23 | unmeasurable | — |
| default / sg 0.3 | 31337 | 0/23 | unmeasurable | — |
| default / sg 0.3 | 777 | 0/23 | unmeasurable | — |
| default / sg 0 | 12345 | 1/23 | unmeasurable | 0.3368 |
| default / sg 0 | 31337 | 1/23 | unmeasurable | 0.3360 |
| default / sg 0 | 777 | 1/23 | unmeasurable | 0.3368 |
| spinchladni / sg 0.5 | 12345 | 11/23 | unmeasurable | 0.0133 |
| spinchladni / sg 0.5 | 31337 | 12/23 | 0.1046 | 0.0179 |
| spinchladni / sg 0.5 | 777 | 11/23 | unmeasurable | 0.0164 |

The dense `default / sg 0.3` runs retained their density within the mask but had only about 14–34 effective residual cells, below the frozen minimum of 64. Their failure is concentration of support, not a missing-file problem. The `default / sg 0` runs became sparse within this mask; their single eligible pair changed by about 0.336 when the radius changed from 15.5 to 14.5, exceeding the 0.10 limit.

The three `spinchladni / sg 0.5` runs had 11, 12 and 11 eligible pairs. Their shared eligible scores changed by at most 0.018 under the support sensitivity, but two still missed the frozen summary threshold. The lone diagnostic alarm among all 37 eligible pairs is not inferential evidence: the runs are selected, neighboring epochs are dependent, and the imposed fields need not be rotation-exchangeable.

## Analytical calibration has a limited valid domain

These 5,376 independently seeded pairs are **analytical qualification fixtures, not physical observations**: 3,072 null pairs and 2,304 known-correlation injections. Each stratum uses the first saved epoch's radial envelope from seed 12345. The intervals below are separate exact 95% binomial intervals within those fixed analytical strata; they are not confidence intervals across physical epochs.

| Radial envelope | Angular fixture | Null rank-only exceedance (95% CI) | Recovery at correlation 0.30 (95% CI) | Frozen qualification |
| --- | --- | --- | --- | --- |
| default / sg 0.3 | iid | unmeasurable | unmeasurable | fail: support |
| default / sg 0.3 | smooth_sigma2 | unmeasurable | unmeasurable | fail: support |
| default / sg 0 | iid | 23/512 (0.029–0.067) | 128/128 (0.972–1.000) | pass |
| default / sg 0 | smooth_sigma2 | 20/512 (0.024–0.060) | 126/128 (0.945–0.998) | pass |
| spinchladni / sg 0.5 | iid | 20/512 (0.024–0.060) | 128/128 (0.972–1.000) | pass |
| spinchladni / sg 0.5 | smooth_sigma2 | 13/512 (0.014–0.043) | 128/128 (0.972–1.000) | pass |

The four measurable strata passed the upper-null-bound ≤ 0.10 and lower-target-power-bound ≥ 0.80 criteria. Both dense-profile strata had zero eligible null and power fixtures; their null rate and power are unknown, not zero. The complete [JSON receipt](2026-09-05_halo_memory_estimator_results.json) also records the stricter combined alarm (rank plus correlation ≥ 0.10), every injected effect and every eligibility result.

At the weaker correlation 0.15, smooth-fixture recovery was only **39/128** for `default / sg 0` and **29/128** for `spinchladni / sg 0.5`. Their exact intervals were 0.226–0.392 and 0.157–0.309. Strong recovery of a 0.30 injection does not establish sensitivity to these smaller, spatially smooth effects.

All four measurable static anisotropic controls scored approximately 1 with orientation rank 1/24 and triggered the diagnostic alarm. The two concentrated controls were unmeasurable. Thus the statistic can recognize an unchanged angular figure without any dynamics; it cannot establish causal memory. The rotation-rank interpretation requires a transformation-invariant null, as described by [Hemerik and Goeman (2018)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6405018/). [SciPy's exact binomial interval](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html) supplies the analytical calibration intervals.

## Consequence and next bounded step

Do not replace the original memory criterion with this statistic or launch another full particle grid on its strength. The radial-confound repair is numerically useful, but sparse/concentrated support and weak smooth-effect sensitivity prevent promotion across the selected domain. The 64-cell criterion is this design's acceptance threshold, not a physical law; lowering it after these results would require a newly declared qualification design.

A next method study should explicitly target sparse/concentrated angular support and low-amplitude smooth effects with calibrated analytical controls. Any future physical question must distinguish static or externally forced recurrence from causal seeding through a separately registered intervention. The saved meshes do not contain that intervention, particle identities or finer spatial information.

## Reproduction and provenance

Run in the DEV workspace through the background launcher with one numerical-library thread:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
python3 analysis/halo_memory_estimator.py \
  --design archive/reports/2026-09-05_halo_memory_estimator_design.json \
  --workspace /Volumes/dual/DUALITY-ZERO-V2 \
  --output archive/reports/2026-09-05_halo_memory_estimator_results.json
python3 -m unittest discover -s tests/halo_memory_estimator -v
```

The original inputs and preservation manifest remain local-only. A public clone can run the analytical behavior tests but cannot reproduce the recorded-data and envelope-dependent portion without those files. The nine-run choice was exploratory and does not generalize to the original 60-run grid. Native-endian capture and historical instrument-provenance limitations remain as recorded by the [input audit](2026-09-05_halo_memory_input_integrity.md).

- Estimator source SHA-256: `00f8576bf63a4eb577e11cade6cedd665d523e47e25bd8862f9f1414630833b4`
- Frozen design SHA-256: `f7f1401483e16ef5b9cdeaa8feb07d7ad2047eca1926c1b2a4a6b30d6c766880`
- Input manifest SHA-256: `9c84615799d160cc0fbca559d7cb63e402751f60da925cac3af66d08b7929733`
- Runtime: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.1.
- Measurement receipt timestamp: `2026-09-05T12:33:01.567922+00:00`.
- Execution log: local `logs/halo_memory_estimator_qualification_20260905.log`.
