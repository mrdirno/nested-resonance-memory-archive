# CYCLE 273: EXTENDED FREQUENCY-VARIANCE MAPPING - EXPERIMENTAL PLAN

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-19 (Cycle 1473)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

---

## OBJECTIVE

Validate variance power law exponent γ ≈ 3.2 across extended frequency range to empirically test the unified scaling framework prediction: **σ²(f) ∝ f^-γ where γ = β + 1**.

---

## BACKGROUND

### Cycle 1471 Discovery (V6 Regime Boundary Analysis)

Analysis of V6b growth regime (E_net = +0.5) revealed frequency-dependent variance scaling:
- At f = 0.10%: σ² = 10,244 (high variance, near threshold)
- At f = 1.00%: σ² = 14 (low variance, stable)
- **Variance reduction: 740× over 10× frequency range**

Preliminary fit over 5 frequency points (0.10% - 1.00%) suggested **γ ≈ 3.2**.

### Cycle 1472 Theoretical Derivation

From first principles derivation of energy-variance coupling:

```
σ²(f) ∝ |dE_min/df| ∝ β × f^-(β+1)
```

Where:
- β ≈ 2.19 (energy power law exponent, Cycle 1399)
- Therefore: γ = β + 1 ≈ 3.19 ≈ 3.2 (exact mechanistic constraint)

**Key Insight:** Variance scales with **energy sensitivity** (derivative), not energy itself.

---

## HYPOTHESIS

**Null Hypothesis (H0):** σ²(f) ∝ f^-γ where γ = 3.19 ± 10%

**Alternative (H1):** Variance scaling follows different exponent or non-power-law behavior

**Prediction:** Power law should hold across 3 orders of magnitude (0.01% - 10%) with:
- Exponent: γ = 3.2 ± 0.3 (within 10% of theory)
- Fit quality: R² > 0.90 (strong power law)
- No systematic deviations at frequency extremes

---

## EXPERIMENTAL DESIGN

### Regime Selection

**V6b (Growth Regime):**
- E_consume = 0.5
- E_recharge = 1.0
- **Net energy = +0.5** (energy surplus)

**Rationale:** Cycle 1471 established that only growth regimes (E_net > 0) exhibit frequency-dependent variance. Homeostasis (E_net = 0) shows constant variance; collapse (E_net < 0) shows zero variance.

### Frequency Range (Log-Spaced)

**10 frequency points spanning 0.01% - 10%:**

| Frequency | Ratio to f_crit* | Expected Behavior |
|-----------|------------------|-------------------|
| 0.01% | ~1.5× f_crit | Near-threshold, high variance |
| 0.02% | ~3× f_crit | Transition region |
| 0.05% | ~7.5× f_crit | Moderate variance |
| 0.10% | ~15× f_crit | Established (V6 data) |
| 0.20% | ~30× f_crit | Low variance |
| 0.50% | ~75× f_crit | Very low variance |
| 1.00% | ~150× f_crit | Deterministic (V6 data) |
| 2.00% | ~300× f_crit | Far above threshold |
| 5.00% | ~750× f_crit | Saturation? |
| 10.00% | ~1500× f_crit | Overhead effects? |

*f_crit^hier ≈ 0.0066% (from C186 hierarchical efficiency analysis)

**Coverage:** 3 orders of magnitude (1000× frequency range)

### Replication

**Seeds:** 42-61 (n = 20 per frequency)
- Sufficient for reliable variance estimation
- Consistent with V6 methodology (n = 10 per condition)
- Doubled replication for power law fitting robustness

**Total Experiments:** 10 frequencies × 20 seeds = **200 experiments**

### Hierarchical Configuration

**Standard V6 Parameters:**
- n_pop = 10 (populations)
- f_migrate = 0.5% (inter-population migration)
- Mode = "HIERARCHICAL"

**Rationale:** Maintain consistency with V6 experiments to isolate frequency effects.

### Runtime

**Cycles per experiment:** 450,000 (~3-5 minutes each)
- Matches V6 extended runtime (not C186 short 3000-cycle runs)
- Ensures equilibration at low frequencies

**Estimated total time:** 200 × 4 min = **~13-14 hours sequential**
- Feasible for overnight run
- Can be parallelized across multiple cores if needed

---

## EXPECTED OUTCOMES

### If Hypothesis Correct (γ ≈ 3.2)

**Quantitative:**
- Power law fit: σ²(f) = A × f^-γ with γ = 3.2 ± 0.3
- R² > 0.90 (strong linear relationship in log-log space)
- Residuals show no systematic trend with frequency

**Interpretation:**
- **Validates unified scaling framework:** γ = β + 1 relationship confirmed
- **Confirms mechanistic link:** Variance ~ energy sensitivity (derivative property)
- **Establishes universality:** Power law holds across 3 orders of magnitude

### If Hypothesis Incorrect

**Scenario A: Different Exponent (γ ≠ 3.2, but power law holds)**
- May indicate frequency-dependent corrections
- β value may need revision
- Could reveal higher-order effects

**Scenario B: Non-Power-Law Behavior**
- Systematic deviations at low or high frequencies
- May indicate:
  - Critical phenomena near f_crit (divergence effects)
  - Saturation at high frequencies (overhead dominates)
  - Regime boundaries between metastable and deterministic regions

**Scenario C: Poor Fit (R² < 0.90)**
- High scatter suggests additional variance sources
- May require more replication or longer runtimes
- Could indicate regime-dependent behavior

---

## ANALYSIS PIPELINE

### Primary Analysis

**Script:** `code/analysis/c273_variance_power_law_validation.py`

**Steps:**
1. Load final population from each experiment (200 databases)
2. Calculate variance σ² at each frequency (across 20 seeds)
3. Fit power law: log(σ²) vs. log(f) linear regression
4. Extract exponent γ and test against prediction γ = 3.19

**Outputs:**
- Fitted parameters: γ, A, R²
- Hypothesis test result (within 10% tolerance?)
- Residual analysis (systematic deviations?)

### Visualization

**Figure 1: Power Law Fit (2-panel)**
- Panel A: Log-log plot with data + fitted line + theoretical prediction
- Panel B: Residuals vs. frequency (test for systematic deviations)

**Figure 2: Variance Scaling Panels (4-panel)**
- Panel A: Variance vs. frequency (log-log)
- Panel B: Standard deviation vs. frequency (σ ∝ f^-γ/2)
- Panel C: Coefficient of variation (normalized variance)
- Panel D: Mean population vs. frequency (context)

**Quality:** 300 DPI, publication-ready

### Statistical Tests

**Primary Test:** Goodness-of-fit (R² test)
- R² > 0.90: Strong power law
- R² = 0.80-0.90: Moderate power law with scatter
- R² < 0.80: Weak/no power law

**Secondary Test:** Exponent Comparison
- |γ_fit - γ_theory| / γ_theory < 10%: Hypothesis supported
- 10% < error < 20%: Partial support (qualitative agreement)
- error > 20%: Hypothesis not supported

**Tertiary Test:** Residual Analysis
- Random scatter: Power law valid across range
- Systematic trend: Frequency-dependent corrections needed
- U-shape: Critical phenomena at extremes

---

## CONNECTION TO UNIFIED FRAMEWORK

### Empirical Pillar #4

This experiment provides the **fourth empirical pillar** of the unified scaling framework:

1. **Hierarchical Efficiency:** α = 607 (C186 baseline)
2. **Energy Balance Regimes:** Three deterministic regimes (V6 validation)
3. **Energy Power Law:** E_min ∝ f^-2.19 (Cycle 1399)
4. **Variance Power Law:** σ² ∝ f^-3.2 (C273, this experiment) ✓

### Theoretical Validation

**Mechanism:** Variance scales with energy sensitivity
```
σ²(f) ∝ |dE_min/df| = β × A × f^-(β+1) ∝ f^-γ
```

**If validated:** Confirms that variance is **not** independent stochasticity, but **structured signal** revealing:
- Proximity to critical threshold f_crit (high variance = near threshold)
- Energy buffering requirements (low variance = robust energy surplus)
- System metastability (variance as diagnostic)

### Broader Implications

**Success validates:**
- γ = β + 1 is exact mechanistic constraint (not empirical correlation)
- β ≈ 2.19 is universal exponent (appears in both energy and variance)
- Unified framework accurately predicts multi-scale relationships

**Applications:**
- **Early warning signals:** Monitor variance to detect approaching thresholds
- **System design:** Quantify variance-efficiency trade-off (10× freq → 740× less variance)
- **Universality testing:** Measure γ in other hierarchical systems to test universality claim

---

## SUCCESS CRITERIA

### Primary Criteria (Must Pass)

- [ ] **Exponent match:** 2.9 < γ < 3.5 (within 10% of γ = 3.19)
- [ ] **Fit quality:** R² > 0.90 (strong power law)
- [ ] **Data completeness:** ≥ 180/200 experiments successful (≥90% success rate)

### Secondary Criteria (Desirable)

- [ ] **Tight fit:** 3.0 < γ < 3.4 (within 5% of γ = 3.19)
- [ ] **Excellent fit:** R² > 0.95 (very strong power law)
- [ ] **No systematic deviations:** Random residuals across frequency range

### Failure Criteria (Indicates Problem)

- [ ] **Poor exponent:** γ < 2.5 or γ > 4.0 (>25% error)
- [ ] **Weak fit:** R² < 0.80 (high scatter)
- [ ] **Data loss:** <150/200 experiments successful (<75% success rate)

---

## TIMELINE

### Execution Phase

**Script:** `experiments/cycle273_extended_frequency_variance_mapping.py`

- **Start:** User-initiated (when system resources available)
- **Duration:** ~13-14 hours (200 experiments × 4 min each)
- **Monitoring:** Check progress periodically, no intervention needed

**Output:** 200 databases in `experiments/results/`

### Analysis Phase

**Script:** `code/analysis/c273_variance_power_law_validation.py`

- **Start:** After all experiments complete
- **Duration:** ~5 minutes (load data, fit, visualize)
- **Output:**
  - Summary JSON: `c273_variance_power_law_analysis_summary.json`
  - Figure 1: `c273_variance_power_law_validation.png`
  - Figure 2: `c273_variance_scaling_panels.png`

### Integration Phase

**Documents to update:**
1. **Archive summary:** Create `CYCLE_1473_C273_VARIANCE_VALIDATION.md`
2. **Paper 4:** Add C273 results to Section 4.8 (if validated)
3. **META_OBJECTIVES:** Update with C273 completion status
4. **Unified framework doc:** Update with empirical validation of γ

---

## CONTINGENCY PLANS

### If Experiments Fail (Technical Issues)

**Scenario:** Databases corrupt, processes crash, results missing

**Action:**
1. Identify failure pattern (specific frequencies? seeds? system resource exhaustion?)
2. Reduce scope: Test 5 frequencies × 20 seeds = 100 experiments (still validates power law)
3. Or increase runtime: 450k → 200k cycles (faster, less robust equilibration)

### If Power Law Doesn't Fit (γ significantly different)

**Scenario:** γ = 2.5 or 4.0 (>20% error from prediction)

**Action:**
1. Check for systematic errors (data loading, variance calculation)
2. Test frequency sub-ranges (low vs. high f separately)
3. Look for regime transitions (where does power law break?)
4. Revise theoretical model (may need higher-order corrections)

### If Fit is Weak (R² < 0.80)

**Scenario:** High scatter, no clear power law

**Action:**
1. Increase replication: n = 20 → n = 40 per frequency (more seeds)
2. Extend runtime: 450k → 1M cycles (better equilibration)
3. Check for confounds (CPU load, system state, database corruption)
4. Consider non-power-law models (stretched exponential, critical scaling)

---

## DOCUMENTATION

**Experiment code:** `experiments/cycle273_extended_frequency_variance_mapping.py`
**Analysis code:** `code/analysis/c273_variance_power_law_validation.py`
**This plan:** `experiments/CYCLE273_EXPERIMENTAL_PLAN.md`

**After completion, create:**
- `archive/summaries/CYCLE_1473_C273_VARIANCE_VALIDATION.md` (synthesis)
- Update Paper 4 Section 4.8 with empirical validation
- Update unified framework documents with γ confirmation

---

## REFERENCES

**Theoretical Foundation:**
- Cycle 1471: Variance scaling discovery (`CYCLE_1471_VARIANCE_SCALING_DISCOVERY.md`)
- Cycle 1472: Energy power law derivation (`ENERGY_POWER_LAW_DERIVATION.md`)
- Cycle 1472: Variance scaling derivation (`VARIANCE_SCALING_DERIVATION.md`)
- Cycle 1471: Unified scaling framework (`UNIFIED_SCALING_FRAMEWORK.md`)

**Empirical Precedent:**
- C186 V6b data: 50 experiments, 5 frequencies, preliminary γ ≈ 3.2
- This extends: 200 experiments, 10 frequencies, validates power law across 3 orders of magnitude

---

**Status:** Ready for execution (user initiation required)

**Next Actions:**
1. User decides when to launch C273 (system resources, timing)
2. Execute: `python experiments/cycle273_extended_frequency_variance_mapping.py`
3. Monitor: Check progress periodically (~14 hours runtime)
4. Analyze: `python code/analysis/c273_variance_power_law_validation.py`
5. Document: Create Cycle 1473 synthesis with results

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
