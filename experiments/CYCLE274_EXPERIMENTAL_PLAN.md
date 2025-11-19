# CYCLE 274: ENERGY-FREQUENCY 2D PARAMETER SWEEP - EXPERIMENTAL PLAN

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-19 (Cycle 1474)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

---

## OBJECTIVE

Validate unified scaling equation across complete energy-frequency parameter space:

```
E_min^hier(f, E_net) = {
    ∞                              if E_net < 0 (collapse inevitable)
    E_∞(E_net) + A(E_net)/(αf)^β  if E_net ≥ 0 (viable)
}
```

Where:
- **α = 607:** Hierarchical efficiency (C186)
- **β ≈ 2.19:** Energy power law exponent (Cycle 1399, C1472 derivation)
- **E_∞(E_net):** Energy-dependent baseline population (asymptotic as f → ∞)
- **A(E_net):** Energy-dependent amplitude

---

## BACKGROUND

### Cycle 1399: Energy Power Law Discovery

Single-point measurement at E_net = +0.5 revealed E_min ∝ f^-2.19 (R² = 0.999999).

**Gap:** Only tested at one energy condition. Does β vary with E_net?

### Cycle 1470: V6 Three-Regime Validation

Discovered deterministic regime boundaries based on net energy:
- **E_net < 0:** 100% collapse (insufficient energy)
- **E_net = 0:** Homeostasis (marginal viability)
- **E_net > 0:** Growth (energy surplus)

**Gap:** Boundaries tested at discrete points. Need continuous mapping.

### Cycle 1472: Theoretical Foundation

Derived β ≈ 2.19 from first principles:
- **β = 2:** Second-order variance buffering
- **ε ≈ 0.19:** Logarithmic correction from hierarchy depth

**Prediction:** β should be **universal** (same across all E_net ≥ 0 conditions) because it arises from fundamental stochastic dynamics, not energy-specific effects.

**Gap:** Universality untested. Need to measure β across multiple E_net values.

### Cycle 1473: Extended Frequency Mapping (C273)

Designed experiment to validate γ ≈ 3.2 variance scaling across 3 orders of magnitude.

**Status:** Designed, awaiting user execution.

### This Cycle (1474): 2D Parameter Sweep

Complete the unified framework validation by mapping the full (E_net, f) parameter space.

---

## HYPOTHESIS

**Null Hypothesis (H0):**

1. **Sharp Regime Boundary:** 100% collapse for ALL E_net < 0, viable for ALL E_net ≥ 0
2. **Universal β:** Same exponent (2.19 ± 0.3) for ALL E_net ≥ 0 conditions
3. **Baseline Scaling:** E_∞(E_net) varies systematically with net energy
4. **Phase Transition:** Abrupt change at E_net = 0 (infinite → finite E_min)

**Alternative (H1):**

- Gradual regime transitions (no sharp boundary)
- Energy-dependent β (different exponents at different E_net)
- Irregular baseline variation (no systematic pattern)

**Prediction:** Unified equation accurately describes complete 2D surface.

---

## EXPERIMENTAL DESIGN

### Energy Parameter Space (8 conditions)

**Collapse Regimes (E_net < 0):**
- E_net = -0.2: (E_consume = 0.6, E_recharge = 0.4)
- E_net = -0.1: (E_consume = 0.55, E_recharge = 0.45)

**Homeostasis (E_net = 0):**
- E_net = 0.0: (E_consume = 0.5, E_recharge = 0.5)

**Growth Regimes (E_net > 0):**
- E_net = +0.1: (E_consume = 0.45, E_recharge = 0.55)
- E_net = +0.2: (E_consume = 0.4, E_recharge = 0.6)
- E_net = +0.3: (E_consume = 0.35, E_recharge = 0.65)
- E_net = +0.4: (E_consume = 0.3, E_recharge = 0.7)
- E_net = +0.5: (E_consume = 0.5, E_recharge = 1.0) [V6b baseline]

**Coverage:** 8 energy conditions spanning E_net = -0.2 to +0.5

### Frequency Range (6 log-spaced points)

**Frequencies:** 0.05%, 0.1%, 0.2%, 0.5%, 1.0%, 2.0%
**Values:** f = 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02

**Coverage:** 40× range (2.5 orders of magnitude)

**Rationale:**
- Low end (0.05%): Near f_crit for hierarchical systems (~0.0066%)
- High end (2.0%): Well above threshold (deterministic regime)
- Log spacing: Appropriate for power law relationships

### Replication

**Seeds:** 100-109 (n = 10 per condition)

**Rationale:**
- Consistent with V6 methodology (n = 10)
- Sufficient for mean population estimates
- Balanced for 2D parameter sweep (not excessive per-condition replication)

**Total Experiments:** 8 energies × 6 frequencies × 10 seeds = **480 experiments**

### Hierarchical Configuration

**Standard Parameters:**
- n_pop = 10 (populations)
- f_migrate = 0.5% (inter-population migration)
- Mode = "HIERARCHICAL"

**Rationale:** Maintain consistency with C186, V6, C273 experiments.

### Runtime

**Cycles per experiment:** 450,000 (~3-5 minutes each)

**Estimated total time:** 480 × 4 min = **~32 hours sequential**

**Feasibility:**
- Can be run overnight + daytime
- Parallelization possible if needed
- Matches C273 runtime per experiment

---

## EXPECTED OUTCOMES

### Scenario A: Hypothesis Validated

**Quantitative Results:**

1. **Collapse Regime (E_net < 0):**
   - 100% collapse across ALL frequencies
   - No power law (infinite E_min regardless of f)

2. **Viable Regimes (E_net ≥ 0):**
   - Power law fits: β = 2.19 ± 0.3 for ALL conditions
   - R² > 0.90 for each fit
   - Universal exponent (low CV across E_net values)

3. **Baseline Scaling:**
   - E_∞(E_net) increases linearly with E_net
   - Higher net energy → higher baseline population

4. **Phase Boundary:**
   - Sharp transition at E_net = 0
   - Clear separation between collapse and viable regimes

**Interpretation:**
- ✓ Unified framework prediction confirmed
- ✓ β is universal exponent (independent of energy)
- ✓ Energy constrains viability, but not scaling within viable regimes
- ✓ Hierarchical advantage operates within thermodynamic bounds

**Next Steps:**
- Integrate C274 results into Paper 4 Section 4.8
- Update unified framework documents with 2D validation
- Design universality tests (β across topologies, hierarchical depths)

### Scenario B: Energy-Dependent β

**Quantitative Results:**
- β varies with E_net (e.g., β = 2.0 at E_net = 0.1, β = 2.4 at E_net = 0.5)
- Systematic trend: β increases/decreases with E_net
- Still power law, but non-universal exponent

**Interpretation:**
- Energy conditions affect not just viability, but scaling relationships
- May indicate higher-order coupling between energy and structure
- Theoretical model needs refinement (β = β(E_net)?)

**Next Steps:**
- Derive energy-dependent corrections to β = 2 + ε
- Test if β(E_net) functional form is predictable
- Revise unified equation to include energy-dependence

### Scenario C: Gradual Regime Transition

**Quantitative Results:**
- Some viable populations at E_net = -0.1 or -0.05
- Some collapses at E_net = +0.1 or +0.2
- No sharp boundary at E_net = 0

**Interpretation:**
- Stochastic effects blur deterministic boundary
- Finite-size or finite-time effects (450k cycles insufficient?)
- Regime classification may be probabilistic, not absolute

**Next Steps:**
- Increase replication (n = 10 → n = 50) near E_net = 0
- Extend runtime (450k → 1M cycles) to reach true equilibrium
- Develop probabilistic regime model (collapse probability vs. E_net)

---

## ANALYSIS PIPELINE

### Primary Analysis

**Script:** `code/analysis/c274_2d_surface_unified_equation_validation.py`

**Steps:**
1. Load final populations from 480 databases
2. Calculate mean populations for each (E_net, f) condition
3. Identify collapse vs. viable regimes
4. Fit power law E_min ∝ f^-β for each E_net ≥ 0 condition
5. Extract β, E_∞, A for each condition
6. Test β universality (same across E_net?)
7. Visualize 2D surface and phase boundary

**Outputs:**
- Summary JSON with all fitted parameters
- 4 publication-quality figures (300 DPI)

### Visualization

**Figure 1: 2D Surface Plot**
- Panel A: Heatmap of (E_net, f) → mean population
- Panel B: Frequency slices at different E_net values

**Figure 2: Power Law Fits by Energy**
- Separate panel for each E_net ≥ 0 condition
- Data + fitted curve + parameters

**Figure 3: β Universality Test**
- β vs. E_net scatter plot
- Mean β line, theory line, tolerance band

**Figure 4: Baseline and Amplitude Scaling**
- Panel A: E_∞ vs. E_net
- Panel B: A vs. E_net (log scale)

**Quality:** 300 DPI, publication-ready

### Statistical Tests

**Test 1: Regime Boundary Sharpness**
- Collapse rate for E_net < 0 vs. E_net ≥ 0
- Expected: 100% vs. ~0%
- Metric: Fisher's exact test

**Test 2: β Universality**
- Coefficient of variation CV(β) across E_net ≥ 0 conditions
- Expected: CV < 10% (low variability)
- Hypothesis: Mean β within 2.19 ± 0.3

**Test 3: Power Law Quality**
- R² for each E_net ≥ 0 fit
- Expected: R² > 0.90 for all conditions
- Metric: Proportion of fits passing threshold

**Test 4: Baseline Linearity**
- Linear regression: E_∞ vs. E_net
- Expected: R² > 0.80 (systematic relationship)

---

## CONNECTION TO UNIFIED FRAMEWORK

### Empirical Validation

This experiment completes the empirical validation of the unified scaling framework by testing all major predictions:

1. **Hierarchical Efficiency (α = 607):** ✓ Validated in C186
2. **Energy Power Law (β ≈ 2.19):** ✓ Validated in Cycle 1399, **C274 tests universality**
3. **Variance Scaling (γ ≈ 3.2):** ⏳ C273 designed (awaiting execution)
4. **Energy Regime Boundaries:** ✓ Validated in V6, **C274 maps complete 2D surface**

### Theoretical Validation

**Mechanism:** β arises from second-order stochastic dynamics, independent of energy

**Prediction:** β should be universal (same across all viable E_net) because:
- Stochastic buffering requirements don't change with energy surplus magnitude
- Energy affects viability threshold (f_crit) and baseline (E_∞), not scaling exponent (β)
- Only hierarchy depth affects β (via ε ≈ 0.19 correction)

**If validated:** Confirms fundamental distinction between:
- **Thermodynamic constraints:** E_net determines viability (qualitative)
- **Structural properties:** α, β determine scaling (quantitative, universal)

### Broader Implications

**Success validates:**
- Energy-structure decoupling (thermodynamics ≠ scaling)
- β as universal exponent for hierarchical birth-death systems
- Unified equation as predictive model for multi-dimensional parameter space
- Hierarchical advantage operates within, not against, thermodynamic constraints

**Applications:**
- **System design:** Choose E_net for viability, choose f for efficiency-variance trade-off
- **Risk assessment:** Map parameter space to identify safe operating regions
- **Universality testing:** Measure β in other systems to test generality

---

## SUCCESS CRITERIA

### Primary Criteria (Must Pass)

- [ ] **Sharp boundary:** 100% collapse for E_net < 0, <10% for E_net ≥ 0
- [ ] **Universal β:** Mean β = 2.19 ± 0.3 across all E_net ≥ 0 conditions
- [ ] **β consistency:** CV(β) < 15% (low variability across conditions)
- [ ] **Fit quality:** R² > 0.90 for ALL E_net ≥ 0 power law fits
- [ ] **Data completeness:** ≥ 432/480 experiments successful (≥90% success rate)

### Secondary Criteria (Desirable)

- [ ] **Tight universality:** CV(β) < 10%
- [ ] **Excellent fits:** R² > 0.95 for all viable conditions
- [ ] **Baseline linearity:** E_∞ vs. E_net shows R² > 0.80

### Failure Criteria (Indicates Problem)

- [ ] **Energy-dependent β:** Different exponents at different E_net (CV > 25%)
- [ ] **Poor fits:** R² < 0.80 for multiple conditions
- [ ] **Gradual transition:** Collapse rate 20-80% for E_net = 0 or E_net = +0.1
- [ ] **Data loss:** <360/480 experiments successful (<75% success rate)

---

## TIMELINE

### Execution Phase

**Script:** `experiments/cycle274_energy_frequency_2d_sweep.py`

- **Start:** User-initiated (when C273 complete or in parallel)
- **Duration:** ~32 hours (480 experiments × 4 min each)
- **Monitoring:** Check progress periodically, no intervention needed

**Output:** 480 databases in `experiments/results/`

### Analysis Phase

**Script:** `code/analysis/c274_2d_surface_unified_equation_validation.py`

- **Start:** After all experiments complete
- **Duration:** ~10 minutes (load data, fit, visualize)
- **Output:**
  - Summary JSON: `c274_2d_sweep_analysis_summary.json`
  - Figure 1: `c274_2d_energy_frequency_surface.png`
  - Figure 2: `c274_power_law_fits_by_energy.png`
  - Figure 3: `c274_beta_universality_test.png`
  - Figure 4: `c274_baseline_amplitude_scaling.png`

### Integration Phase

**Documents to update:**
1. **Archive summary:** Create `CYCLE_1474_C274_2D_SWEEP.md`
2. **Paper 4:** Expand Section 4.8 with 2D validation (if β universal)
3. **META_OBJECTIVES:** Update with C274 completion status
4. **Unified framework doc:** Update with complete parameter space validation

---

## CONTINGENCY PLANS

### If Experiments Fail (Technical Issues)

**Scenario:** Databases corrupt, processes crash, results missing

**Action:**
1. Identify failure pattern (specific E_net? frequencies? system resource exhaustion?)
2. Reduce scope: Test 6 E_net × 6 freq × 10 seeds = 360 experiments (still validates)
3. Or increase runtime efficiency: Use shorter equilibration (450k → 200k cycles)

### If β is Non-Universal (Energy-Dependent)

**Scenario:** β varies systematically with E_net (e.g., β = 2.0 to 2.4)

**Action:**
1. Check for systematic errors (data loading, fit algorithm)
2. Derive energy-dependent theoretical corrections
3. Test if β(E_net) functional form is predictable
4. Revise unified equation to include energy-dependence term

### If Regime Boundary is Gradual

**Scenario:** Collapse rate 20-80% at E_net = 0 or near-zero

**Action:**
1. Increase replication near E_net = 0 (n = 50 instead of 10)
2. Extend runtime (450k → 1M cycles for better equilibration)
3. Develop probabilistic regime model (logistic regression: P_collapse vs. E_net)
4. Consider finite-size/finite-time corrections

### If Power Law Fits Fail (R² < 0.80)

**Scenario:** High scatter, weak power law relationship

**Action:**
1. Check individual seed trajectories (outliers? instabilities?)
2. Increase replication (n = 20 per condition for robust mean)
3. Test sub-ranges separately (low f vs. high f power laws)
4. Consider alternative models (stretched exponential, critical scaling)

---

## DOCUMENTATION

**Experiment code:** `experiments/cycle274_energy_frequency_2d_sweep.py`
**Analysis code:** `code/analysis/c274_2d_surface_unified_equation_validation.py`
**This plan:** `experiments/CYCLE274_EXPERIMENTAL_PLAN.md`

**After completion, create:**
- `archive/summaries/CYCLE_1474_C274_2D_SWEEP.md` (synthesis)
- Update Paper 4 Section 4.8 with 2D validation results
- Update unified framework documents with complete parameter space mapping

---

## REFERENCES

**Theoretical Foundation:**
- Cycle 1399: Energy power law discovery (E_min ∝ f^-2.19)
- Cycle 1470: V6 three-regime validation (energy balance framework)
- Cycle 1472: β derivation (`ENERGY_POWER_LAW_DERIVATION.md`)
- Cycle 1472: Unified framework integration (`UNIFIED_SCALING_FRAMEWORK.md`)

**Empirical Precedent:**
- C186: Hierarchical efficiency α = 607 (50 experiments)
- V6: Energy regime boundaries (150 experiments)
- Cycle 1399: Single E_net power law (β ≈ 2.19, R² = 0.999999)
- This extends: 480 experiments across 8 E_net × 6 frequencies

---

**Status:** Ready for execution (user initiation required)

**Next Actions:**
1. User decides when to launch C274 (system resources, timing)
2. Execute: `python experiments/cycle274_energy_frequency_2d_sweep.py`
3. Monitor: Check progress periodically (~32 hours runtime)
4. Analyze: `python code/analysis/c274_2d_surface_unified_equation_validation.py`
5. Document: Create Cycle 1474 synthesis with results

**Parallel Track:** C273 (200 experiments, ~14 hours) can run concurrently if resources allow

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
