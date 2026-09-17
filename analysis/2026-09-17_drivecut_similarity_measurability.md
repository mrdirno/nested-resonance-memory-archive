# The drive-cut axis, measured: a similarity rescaling makes the frozen scorer report measurable runs, on fields that do not move

Author: Aldrin Payopay · September 17, 2026 · GPL-3.0-only

## Summary

The measurability programme had produced **zero** measurable runs on every set it
scored: the registered 60-run grid (0 of 60, `analysis/2026-09-06_memory_estimator_qualification.md`)
and the 2026-09-07 pilot (0 of 21, `analysis/2026-09-07_measurability_pilot.md`).
Ring 17 asked what a condition that **cuts the imposed drive and renormalises
self-gravity to it** would look like, and whether the seed lock breaks there or
the relic collapses first. Ring 18 found that the binding refusal is not the
12-epoch floor but the seed-balance gate E5b, which rejects near-copy seeds.

This note scores, re-verifies, and writes up an exploration recorded on
2026-09-10 (the open ledger round's runs, `data/results/halo/memory_similarity/`,
committed but never written up). It applies a **similarity transform** to the
force: self-gravity, field-drive amplitude and magnetic coupling are scaled by a
common factor, so the trajectory is an exact time-rescaled image of a baseline.
The drive-cut arm (÷4) and the drive-raised arm (×4) are the same physics at two
scales.

The measured result:

- The baseline (drive on, self-gravity 0.5) clears the 12-epoch floor but yields
  **0 measurable runs** — refused after the floor by the collapse/seed-balance
  gate, with raw seeds near-copies (A1 = 1.0000; for arm A, identical up to a one-cell shift). The whole programme's failure
  mode, isolated.
- Cutting self-gravity **without** renormalising the drive leaves the three
  seeds' relic templates ≥ 0.9 correlated — 0-1 eligible epochs of 22, refused
  per-epoch by the cross-seed gate E3 — so lowering gravity alone does not make
  the seeds separable (participation stays healthy at ~16; the residual does not
  vanish).
- The **full similarity rescaling** (drive cut ÷4, or raised ×4, with self-gravity
  and magnetism scaled to match) gives **3 of 3 measurable runs in each arm** —
  the first measurable conditions this programme has produced. Pooling the two
  scales (6 runs) makes the injected-effect recovery falsifier **F3 evaluable and
  passing for the first time** (median α\*_eff = 0.0608 ≤ 0.10).
- **But every one of these arms is a static field** (epoch-to-epoch full-field
  correlation = 1.0000): the frozen scorer, which has no staticness gate, reports
  measurability on the monopole-removed **residual of a collapsed configuration.**
  Robustness F4 and support F5 still fail, one of six pooled runs shows any
  detection, and the overall verdict is unchanged: **"insufficient support."**

**Nothing about nested resonance memory is decided in either direction.** The
seed lock breaks under the rescaling, but what becomes measurable is the residual
of a static core — the same geometric confound Ring 15 named, relocated rather
than removed. The finding that matters for the next protocol is negative and
specific: the frozen protocol lacks the one gate this regime needs.

## Provenance and reproduction

The runs are round 2 of the measurability-pilot idea. They were recorded on
2026-09-10 with the single-coordinate override flags added at commit `e9816143`
and `e698bc20` (`tests/halo/memory_prereg_run.js`), scored on 2026-09-14/15, and
had never been written up, ring-logged, or closed. All 42 run files verify byte
for byte against their per-arm `manifest.json` sha256 lists (`ok=42 bad=0
missing=0`).

- **Instrument.** Both scored arms were driven by the same source page,
  `source_page_sha256 = 2c90f52c…` (the Ring-18 instrument digest is what defines
  the instrument, not the whole-file hash or the git rev). Because B and U share
  one instrument, the pooled six-run set is two realisations of the same physics
  on one instrument — the configuration Ring 17 said the programme had never had.
  Playwright 1.62.1; Apple M4 Pro (ANGLE Metal); 4,194,304 particles; 24 epochs.
- **Scorer.** The frozen qualifier `experiments/halo/memory_estimator_qualify.py`
  has `sha256 = 7619ef6b…`, which equals the `script_sha256` recorded in every
  committed `qualification.json`. Re-running it today on all six arms reproduces
  every headline field exactly (measurable runs, detections, F3/F4/F5, verdict):
  **6 of 6 arms MATCH.** The scorer was not edited; its schema string
  `halo-memory-prereg/1` is unchanged (`memory_estimator_qualify.py:57,550`).

## The similarity transform

The chamber's per-particle force is a sum of terms entering at known powers
(`HELIOS-V501…:3206`, and the header of `tests/halo/memory_prereg_run.js`):

```
F = amp·fscale·field  +  uHubble·p·uAniso  +  uHelix·6·(−p.z,0,p.x)
    − uSelfGrav·SG_GAIN·g/(2·PM_CELL)  +  uMag·30·cross(v,B),     amp = 10^fieldExp
```

Cutting the imposed drive is a change of the coordinate `fieldExp`, not a preset
swap. The 2026-09-07 pilot could only cut the drive by naming a different
scenario (goldstair against spinchladni), which moved damping, steps/s, hubble,
magnetism, anisotropy and helix at the same time, so its drive-cut arm "was not
put to the test." The override flags move one coordinate each.

The baseline **A** is the default scenario at self-gravity 0.5, `fieldExp 0`
(amp = 1), magnetism 0.6. The similarity arms scale the three amplitude-carrying
terms by a common factor s:

| arm | s | self-gravity | fieldExp (amp) | magnetism | seeds |
|-----|------|--------------|-----------------|-----------|-------|
| A_base_sg0.5 | 1 | 0.5 | 0 (×1) | 0.6 | 777, 12345, 31337 |
| B_quarter_full | ¼ | 0.125 | −0.60206 (×¼) | 0.15 | 777, 12345, 31337 |
| U_quadruple_full | 4 | 2.0 | +0.60206 (×4) | 2.4 | 777, 12345, 31337 |
| C_selfgrav_only | — | 0.125 | 0 (×1, **not** scaled) | 0.6 (**not** scaled) | 777, 12345, 31337 |
| D_base_triple2 | 1 | 0.5 | 0 (×1) | 0.6 | 2718, 16180, 57721 |

`fieldExp ±0.60206 = ±log₁₀4`, so B has amp ÷4 and U has amp ×4. **B and U are the
baseline dynamics viewed at scales ¼ and 4**; the drive-cut axis realised as a
similarity image rather than a scenario swap. **C** is the diagnostic
counterexample — self-gravity alone lowered, the drive left at baseline — and
**D** re-runs the baseline under three transcendental-digit seeds to test seed
robustness.

## Results (frozen scorer, re-verified today)

| arm | eligible epochs / run (of 22) | measurable runs | detected | F3 | F4 | F5 | measurable conditions |
|-----|------------------------------|-----------------|----------|----|----|----|-----------------------|
| A_base_sg0.5 | 15, 15, 15 | **0 / 3** | 0 | n/e | pass | fail | 0 |
| D_base_triple2 | 13, 13, 13 | **0 / 3** | 0 | n/e | pass | fail | 0 |
| C_selfgrav_only | 0, 1, 0 | **0 / 3** | 0 | n/e | pass | fail | 0 |
| B_quarter_full | 15, 14, 15 | **3 / 3** | 0 | n/e (3 runs) | pass | fail | 1 |
| U_quadruple_full | 14, 13, 13 | **3 / 3** | 1 | n/e (3 runs) | pass | fail | 1 |
| pooled_B_U | (the six above) | **6 / 6** | 1 | **pass** | **fail** | fail | 2 |

- **Metric (conditions with all three seeds measurable, of conditions run): 2 of 5**
  (B and U), against a baseline of 0 and a target of 3. First non-zero value the
  programme has recorded.
- **A and D clear the floor and are still not measurable.** 15 and 13 eligible
  epochs per run, no run below the floor (`below_floor_runs_main = []`), yet zero
  measurable — so the refusal is the collapse/seed-balance gate (E5/E5b), not the
  epoch count. Their raw seeds are near-copies (staticness screen A1 = 1.0000;
  for arm A, identical up to a one-cell shift), the near-copy condition E5b is
  built to reject. This is Ring 18's result reproduced
  on an isolated axis.
- **C fails on eligibility, at the cross-seed gate E3.** Lowering self-gravity
  without renormalising the drive leaves 0, 1, 0 eligible epochs of 22 — but not
  because support is thin: participation stays ~16.3 and residual variance ~6e-3
  (E1, E2 pass in every epoch). Its three seeds' relic templates are 0.95-0.96
  correlated (tmpl_xcorr, above the E3 ceiling of 0.9), so the epochs are refused
  as indistinguishable. Cutting gravity alone does not make the seeds separable;
  it is a different, un-measurable condition — the same near-copy failure as A/D,
  surfacing at per-epoch eligibility (E3) rather than the run-level balance gate.
- **B and U break the seed lock.** With the whole force rescaled together, 13-15
  epochs are eligible and all six runs pass E5/E5b: the seeds are no longer
  near-copies at the level the gate reads. This is the direct answer to Ring 17:
  **the seed lock breaks; the relic does not (here) collapse below measurability.**
- **F3 becomes evaluable by pooling.** Six measurable runs across two scales let
  the injected-effect recovery falsifier run for the first time. Five of six runs
  recover an injected relic at α\*_eff 0.053-0.070; one U seed does not recover
  (`unrecovered_at_0.2 = 1`), but its template ρ is 0.64 (> the 0.5 allowance), so
  the "unrecovered at low template ρ" list is empty and F3 passes (median α\*_eff
  0.0608). The estimator can recover an injected effect when given runs it deems
  measurable.

## The caveat that governs the result: these fields do not move

The pilot's own staticness screen (`experiments/halo/memory_pilot_staticness.py`,
which sits **beside** the frozen scorer and changes nothing it does) reports, for
every arm including B and U, a median epoch-to-epoch **full-field** density
correlation of **A3 = 1.0000** — static by the ≥ 0.99 criterion — and raw seed
correlation **A1 = 1.0000**. Every arm is flagged static, and every arm is
"STRUCK" by the exploratory screens.

The frozen scorer works on the monopole-removed **residual**, whose epoch-to-epoch
correlation (A3-res) is 0.93 (B) and 0.91 (U), and whose seed templates are
distinguishable (A2 template 0.78/0.73 < the E3 threshold 0.9). So the
measurability the scorer reports is real **within its own definition** and lives
entirely in the residual of a collapsed, static configuration. This is exactly
the confound Ring 15 retired the original statistic for — a static centrally
peaked field passing a lag-one criterion — surviving in the residual after the
rescaling made the seeds separable.

F4 (robustness) fails: ten of eleven gate-sweep variants are stable, but the
"classes" variant (swapping the lag matrix the arm is read from) flips
measurability, so the robustness gate registers a violation. F5 (support) fails
because it requires three measurable conditions and there are two. The overall
verdict on every arm, main and pooled, remains **"insufficient support."**

## What this answers, and what it hands the next protocol

- **Ring 17** ("what does cutting the drive and renormalising self-gravity look
  like; does the seed lock break or the relic collapse?"): realised as a
  similarity image, the seed lock **breaks** (E5b passes, 3/3 measurable in each
  arm) and the relic does not collapse below the floor — but the field is static,
  so what is measured is the residual of a collapsed core, not motion. Cutting
  self-gravity **alone** (arm C) leaves the seeds near-copies (E3 fails, template
  correlation 0.95-0.96) and never reaches the floor instead.
- **Ring 18 / Ring 20** ("does the successor need a seed-balance gate at all, or
  seeds that cannot be near-copies?"): the rescaling produces seeds that **pass
  E5b** yet remain raw-degenerate (A1 = 1.0) and static (A3 = 1.0). So E5b is
  neither necessary nor sufficient for a meaningful measurement: it is the wrong
  gate to lean on. **The binding property is staticness, which the frozen protocol
  does not gate at all.**
- **META_OBJECTIVES item 2** ("the drive-cut axis remains the successor's remaining
  job"): the axis is now measured. The successor is not another grid under the
  frozen protocol; it is a protocol that **gates staticness (A3) before it scores**,
  because the frozen scorer will otherwise call a static collapsed field
  "measurable" through its residual. A positive memory result requires a
  configuration that is measurable **and** non-static — which none of these arms
  is.

## Falsifiers and what would change the reading

- If a re-run of the frozen scorer on these arms did not reproduce the verdicts,
  the result would be void. It reproduces (6 of 6 arms MATCH, scorer sha
  unchanged).
- If B and U were not on one instrument, the pooled F3 would confound scale with
  instrument. They share `source_page_sha256 2c90f52c…`.
- If the arms were **not** static, the residual measurability would be a candidate
  memory signal rather than a confound. They are static (A3 = 1.0000).
- A genuine successor result would be a condition that is measurable under the
  frozen scorer **and** non-static under A3 **and** shows a condition-level
  detection (not one seed of six). None of these arms clears all three.

## Files

- Runs and per-arm manifests: `data/results/halo/memory_similarity/{A_base_sg0.5,
  B_quarter_full, C_selfgrav_only, D_base_triple2, U_quadruple_full, pooled_B_U}/`
- Committed scorer outputs re-verified here: each arm's `qualification.json`
- Frozen scorer: `experiments/halo/memory_estimator_qualify.py` (sha256 7619ef6b…)
- Staticness screen: `experiments/halo/memory_pilot_staticness.py`
- Override harness: `tests/halo/memory_prereg_run.js` (commits `e9816143`, `e698bc20`)
