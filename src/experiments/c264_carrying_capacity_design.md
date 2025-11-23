# CYCLE 264: CARRYING CAPACITY DYNAMICS IN NRM

**Date:** 2025-11-09 (Design Phase)
**Cycle:** 264 (Proposed)
**MOG Resonance:** α = 0.92 (Very Strong, Tier 1 Priority)
**Status:** Design Complete, Awaiting Execution

---

## CROSS-DOMAIN RESONANCE

**Domain A: NRM Energy Regulation**
- Mechanism: Spawn frequency adjusts to maintain population ≈17
- Critical parameter: f_spawn = 2.5%
- Constraint: E_recharge limits sustainable spawn rate
- Observation: Population homeostasis emerges without specification

**Domain B: Ecological Carrying Capacity (K)**
- Mechanism: Birth rate adjusts to resource availability
- Critical parameter: r (intrinsic growth rate)
- Constraint: Resource availability limits sustainable population
- Observation: K emerges from resource-population feedback

**Resonance Coupling:**
- **Overlap:** Energy constraint ↔ Resource constraint (HIGH)
- **Coherence:** Self-regulation ↔ Density-dependent feedback (HIGH)
- **α = 0.92** (VERY STRONG RESONANCE)

**Novel Hypothesis:**
NRM energy homeostasis IS carrying capacity dynamics at the computational level.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1: Linear Scaling (Primary Hypothesis)

**Claim:** K = β × E_recharge (linear relationship, β > 0)

**Mechanism:**
- Higher E_recharge → More energy available per cycle
- More energy → More sustainable spawns per cycle
- More spawns → Higher equilibrium population
- Therefore: K ∝ E_recharge

**Newtonian Test (Predictive):**
- Quantitative prediction: K = β × E_recharge
- Falsifying observation: R² < 0.6 OR negative slope OR non-monotonic relationship

**Maxwellian Test (Unification):**
- Unifies: Computational energy dynamics = Ecological resource limitation
- Novel prediction at boundary: K → ∞ as E_recharge → ∞ (no constraint)

**Einsteinian Test (Limits):**
- E_recharge → 0 limit: K → 0 (extinction, no energy for births)
- E_recharge → ∞ limit: K should grow unbounded (no constraint)
- Reduces to known result: At E_recharge = 0.5 (baseline), K ≈ 17 (Papers 1-2 validated)

### Prediction 2: Allee Effect at Low Energy (Secondary Hypothesis)

**Claim:** Below critical E_recharge_min, population collapses to zero (Allee effect)

**Mechanism:**
- Very low E_recharge → Few successful spawns
- Population drops below critical density
- Stochastic extinction overwhelms reproduction
- Positive feedback: Lower N → Fewer compositions → Even lower N

**Falsification:** If no extinction threshold OR extinction is gradual (not sharp)

### Prediction 3: r-K Selection Trade-off (Exploratory)

**Claim:** f_spawn × spawn_cost parameter space exhibits r-K selection trade-off

**Mechanism:**
- High f_spawn, low spawn_cost → r-selection (many cheap offspring, unstable)
- Low f_spawn, high spawn_cost → K-selection (few expensive offspring, stable)
- Trade-off curve: f × cost = constant at equilibrium

**Falsification:** If no trade-off curve OR multiple stable strategies

---

## EXPERIMENTAL DESIGN

### Parameters

**Independent Variable:** E_recharge
- Values: {0.1, 0.25, 0.5, 1.0, 2.0, 4.0} (6 levels, 40× range)
- Rationale: Logarithmic spacing to capture potential phase transitions

**Control Variables (Fixed):**
- f_spawn = 2.5% (validated homeostasis frequency, Papers 1-2)
- E_consume = 0.3 (net positive at all E_recharge levels tested)
- spawn_cost = 5.0 (baseline from Paper 2)
- N_initial = 10 (standard initialization)
- depth_min = 0.0, depth_max = 1.0 (full range)
- Cycles = 5000 (sufficient for equilibration, verified in C171/C175/C193)

**Seeds per condition:** n = 20
- Rationale: Balance statistical power vs. runtime
- Previous experiments (C193: n=20) achieved p < 0.001 significance

**Total experiments:** 6 × 20 = 120
**Expected runtime:** ~2 hours (10 min/20 experiments per condition)

### Measurements

**Primary Outcome: Equilibrium Population (K)**
- Definition: Mean population over cycles 4000-5000 (last 1000 cycles)
- Rationale: Excludes transient dynamics, captures equilibrium
- Per-seed: K_i = mean(population[4000:5000])
- Per-condition: K_mean ± K_std across n=20 seeds

**Secondary Outcomes:**
1. **Population Variance:** σ²_pop (stability metric)
2. **Extinction Events:** Fraction of seeds reaching N=0
3. **Time to Equilibrium:** Cycles until |dN/dt| < 0.1 for 100 consecutive cycles
4. **Spawn Success Rate:** η = successes / attempts (resource utilization)

**Network Metrics (Exploratory):**
- Mean degree ⟨k⟩ (if using networked agents)
- Clustering coefficient C (emergent structure)
- Giant component size S (connectivity)

---

## ANALYSIS PLAN

### Primary Analysis: Linear Regression

**Model:** K ~ E_recharge

**Hypothesis Test:**
- H₀: β = 0 (no relationship)
- H₁: β > 0 (positive linear relationship)
- Threshold: R² > 0.6 AND p < 0.05

**Diagnostics:**
- Residual plot (check linearity assumption)
- Q-Q plot (check normality)
- Cook's distance (check outliers)

**Alternative Models (if linear fails):**
- Power law: K ~ E_recharge^α
- Logarithmic: K ~ log(E_recharge)
- Saturating: K ~ K_max × (1 - exp(-E_recharge/E_0))

### Secondary Analysis: Allee Effect Detection

**Method:** Identify critical threshold E_c where extinction rate > 50%

**Procedure:**
1. Plot extinction rate vs. E_recharge
2. Fit sigmoid: P(extinct) = 1 / (1 + exp((E - E_c) / σ))
3. Report E_c ± confidence interval

**Falsification:** If extinction rate monotonic (no threshold) OR E_c < 0.05 (all conditions viable)

### Exploratory Analysis: r-K Trade-off

**Method:** Compare population variance vs. mean across conditions

**Prediction:** High E_recharge → High K but also high σ² (r-selection instability)

**Visualization:**
- Scatter plot: σ²_pop vs. K_mean
- Color by E_recharge
- Look for trade-off curve (negative correlation)

---

## FALSIFICATION CRITERIA (Pre-Registered)

### Primary Hypothesis (Linear Scaling) FALSIFIED IF:

1. **R² < 0.6:** Weak correlation (less than 60% variance explained)
2. **β ≤ 0:** Negative or zero slope (K doesn't increase with E_recharge)
3. **Non-monotonic:** K decreases then increases (non-linear relationship)
4. **p > 0.05:** Statistically insignificant relationship

### Alternative Outcomes:

**If Power Law Fits Better (R² > 0.7):**
- Accept K ~ E_recharge^α (non-linear carrying capacity)
- Report α as scaling exponent
- Compare to ecological scaling laws (often α ≈ 0.75, Kleiber's law)

**If Saturating Function Fits Better:**
- Accept K ~ K_max × (1 - exp(-E_recharge/E_0))
- Interpretation: Hard ceiling on population (space/time constraint)
- Report K_max and E_0

**If No Relationship (R² < 0.3):**
- **Reject resonance hypothesis (α = 0.92 was WRONG)**
- Publish negative result: "NRM energy regulation does NOT exhibit carrying capacity dynamics"
- Investigate alternative mechanisms (e.g., frequency-dependent selection)

---

## EXPECTED OUTCOMES & IMPLICATIONS

### Scenario A: Linear Scaling Confirmed (R² > 0.6, β > 0)

**Interpretation:** NRM energy homeostasis = ecological carrying capacity

**Implications:**
1. **Theoretical:** Energy-as-resource analogy validated at computational level
2. **Practical:** K can be predicted from E_recharge (engineering tool)
3. **Publication:** Nature Ecology & Evolution or Theoretical Ecology

**Follow-up Experiments:**
- C265: Test r-K selection trade-off explicitly (f_spawn × spawn_cost space)
- C266: Test Allee effect at very low E_recharge (<0.1)
- C267: Vary N_initial to test density-dependence predictions

### Scenario B: Power Law or Saturation (R² > 0.7, non-linear)

**Interpretation:** Carrying capacity exists but with non-linear scaling

**Implications:**
1. **Theoretical:** More complex than simple resource limitation
2. **Practical:** Requires non-linear model for K prediction
3. **Publication:** PLOS Computational Biology or Theoretical Population Biology

**Follow-up:**
- Investigate mechanism for non-linearity
- Compare α to ecological allometry exponents
- Test universality: Does α change with other parameters?

### Scenario C: No Relationship (R² < 0.3)

**Interpretation:** Resonance hypothesis FALSIFIED

**Implications:**
1. **MOG Methodology:** α calculation can produce false positives (refinement needed)
2. **NRM Mechanism:** Population regulation is NOT resource-limited (alternative mechanism)
3. **Publication:** PLOS ONE (negative results) or arXiv (methodological critique)

**MOG Feedback:**
- Update resonance detection algorithm (increase α threshold to 0.95?)
- Identify where analogy broke down (overlap vs. coherence vs. scale mismatch)
- Document as failed resonance for future reference (Negative-Space Commons)

---

## INTEGRATION WITH EXISTING RESEARCH

### Connection to Paper 2 (Energy-Regulated Homeostasis)

**Paper 2 Finding:** Population ≈17 emerges at E_recharge = 0.5, f_spawn = 2.5%

**C264 Extends This By:**
- Testing if K = 17 is specific to E_recharge = 0.5
- Quantifying relationship: K = β × E_recharge → K(0.5) = β × 0.5 = 17 → β ≈ 34
- Validating that Paper 2's homeostasis IS carrying capacity dynamics

**Prediction:** At E_recharge = 1.0, should observe K ≈ 34 (double the population)

### Connection to C193 (N-Independent Robustness)

**C193 Finding:** Population size scaling (N=5-20) does NOT affect dynamics IF net energy ≥ 0

**C264 Distinguishes:**
- N_initial (starting condition) vs. K (equilibrium outcome)
- C193 varied N_initial with fixed E_recharge
- C264 varies E_recharge to find K(E)

**Complementary Findings:**
- C193: K is robust to initialization (N_initial doesn't matter)
- C264: K is determined by energy availability (E_recharge matters)

### Connection to C194 (Sharp Phase Transition)

**C194 Finding:** Binary collapse at E_consume = 0.5 (energy balance threshold)

**C264 Tests Opposite Direction:**
- C194: Fixed E_recharge, varied E_consume → found collapse threshold
- C264: Fixed E_consume, varied E_recharge → find carrying capacity scaling

**Unified Framework:**
- **Survival threshold (C194):** E_consume ≤ E_recharge (binary)
- **Carrying capacity (C264):** K ∝ (E_recharge - E_consume) (quantitative)

**Combined Prediction:** K = β × (E_recharge - E_consume) for E_recharge > E_consume, else K = 0

---

## REPRODUCIBILITY SPECIFICATIONS

### Code Implementation

**File:** `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/c264_carrying_capacity.py`

**Key Functions:**
```python
def run_experiment(seed: int, e_recharge: float) -> Dict:
    """Run single carrying capacity experiment"""
    # Initialize system with e_recharge parameter
    # Run 5000 cycles
    # Measure equilibrium population K (mean over 4000-5000)
    # Return {seed, e_recharge, K, sigma_pop, extinction, ...}

def main():
    """Execute full experimental suite (120 experiments)"""
    e_recharge_values = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
    seeds = range(42, 62)  # n=20

    results = []
    for e_recharge in e_recharge_values:
        for seed in seeds:
            result = run_experiment(seed, e_recharge)
            results.append(result)

    # Save to JSON
    save_results(results, "c264_carrying_capacity.json")

    # Perform statistical analysis
    analyze_results(results)
```

**Output:** `/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c264_carrying_capacity.json`

**Analysis Script:** `/Volumes/dual/DUALITY-ZERO-V2/code/analysis/analyze_c264_carrying_capacity.py`

### Reproducibility Checklist

- [ ] Exact parameter values documented (e_recharge, f_spawn, etc.)
- [ ] Random seeds specified (42-61 inclusive)
- [ ] Cycle count fixed (5000)
- [ ] Equilibrium window defined (cycles 4000-5000)
- [ ] Statistical tests pre-registered (linear regression, R² > 0.6 threshold)
- [ ] Alternative hypotheses specified (power law, saturation)
- [ ] Falsification criteria explicit (R² < 0.6 OR β ≤ 0)
- [ ] Runtime estimate provided (~2 hours)
- [ ] Expected file size: ~150 KB JSON

---

## SUCCESS CRITERIA

### Experiment Succeeds If:

1. ✅ All 120 experiments complete without crashes
2. ✅ Results file written to disk (JSON format, ~150 KB)
3. ✅ Statistical analysis produces clear outcome (linear/power-law/saturation/none)
4. ✅ Falsification criteria definitively tested (accept or reject hypothesis)
5. ✅ Results synced to GitHub within 1 hour of completion

### Experiment Fails If:

- ❌ Crashes or hangs during execution
- ❌ Results ambiguous (R² ≈ 0.5, inconclusive)
- ❌ Statistical tests not applied
- ❌ Results not synced to GitHub

### Publication Readiness:

**Regardless of outcome (positive or negative), this experiment is publication-ready IF:**
- Pre-registered hypotheses tested
- Statistical rigor maintained (p-values, effect sizes, confidence intervals)
- Alternative explanations considered
- Reproducibility documentation complete
- Results contribute to understanding of NRM energy dynamics

---

## TEMPORAL STEWARDSHIP ENCODING

**Patterns for Future AI:**

1. **Cross-domain resonance methodology:** How to identify analogies (α calculation)
2. **Falsifiable hypothesis design:** Pre-register predictions + falsification criteria
3. **Logarithmic parameter spacing:** Test wide ranges efficiently (0.1 - 4.0, 40×)
4. **Equilibrium detection:** Use last 20% of cycles to avoid transient effects
5. **Multi-model comparison:** Test linear/power-law/saturation systematically

**Novel Contribution:**

If K = β × E_recharge is validated, this establishes **the first quantitative law relating computational energy to emergent population dynamics**—a bridge between resource ecology and computational complexity.

---

## NEXT ACTIONS

### After C187 Completes:

1. **Implement C264 experiment code** (~1 hour coding)
2. **Test single seed** (validate implementation, ~10 min)
3. **Execute full suite** (120 experiments, ~2 hours)
4. **Analyze results** (statistical tests, ~30 min)
5. **Sync to GitHub** (commit + push, ~5 min)
6. **Update META_OBJECTIVES** (document findings)

**Total Time:** ~4 hours from start to GitHub sync

**Priority:** Execute immediately after C187 completes (highest MOG resonance α=0.92)

---

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Authored-By:** Claude Sonnet 4.5 (MOG-Active + NRM-Passive Integration)
**MOG Resonance:** α = 0.92 (Very Strong)
**Tier:** 1 (Immediate Execution)
**License:** GPL-3.0

---

**Quote:**
> "Energy shapes population. Population reveals energy. The strongest resonance predicts the deepest law. If K = 34 × E, we have found the first equation of computational ecology."
