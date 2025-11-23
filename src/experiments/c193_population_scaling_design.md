# C193 EXPERIMENTAL DESIGN: POPULATION SIZE SCALING LAW

**Campaign:** C193 (f_critical vs N_initial Scaling)
**Research Arc:** C187 → C189 → C190 → C191 → C192 → **C193**
**Status:** 📋 DESIGN PHASE
**Date:** 2025-11-08
**Author:** Claude (AI Research Assistant)
**Principal Investigator:** Aldrin Payopay

---

## RESEARCH CONTEXT

### Three Consecutive Null Results

**C190 (400 experiments, f ≥ 1.0%):** ZERO collapses
**C191 (900 experiments, f ≥ 0.3%):** ZERO collapses
**C192 (3,000 experiments, f ≥ 0.05%):** ZERO collapses

**Total Evidence:** 4,800+ experiments, 40× frequency range, ZERO collapses

**Interpretation:** Collapse boundary likely depends on **POPULATION SIZE** (N_initial), not frequency alone.

### Why N_initial Matters

**Buffer Hypothesis:**
- Larger populations → more redundancy → higher robustness
- N_initial=20 provides massive buffer (3× what C192 tested)
- Smaller populations should collapse at higher frequencies

**Energy Dynamics:**
- Large N: If one agent low energy → others can spawn
- Small N: Single agent failure → potential collapse
- Redundancy scales with N

**Prediction:** f_critical = f_critical(N)

---

## RESEARCH QUESTION

**How does the collapse boundary (f_critical) scale with initial population size (N_initial)?**

**Sub-Questions:**
1. What is the scaling law: f_critical(N)?
2. At what N does collapse actually occur?
3. Does the 10× robustness multiplier change with N?
4. Do mechanisms show different scaling (Deterministic vs Flat)?

---

## HYPOTHESES

### H1: f_critical Scales Inversely with N_initial

**Prediction:**
```
f_critical(N) ∝ 1/N
```

**Rationale:**
- Smaller populations → less redundancy → higher f needed
- Larger populations → more buffer → lower f sufficient

**Mechanism:**
- Population provides "energy pool"
- Smaller pool → needs more frequent replenishment
- Larger pool → can tolerate longer intervals

**Test:** Measure f_critical at multiple N values, fit power law

### H2: Critical Population Exists (N_critical)

**Prediction:**
- Below N_critical: Collapse likely even at high f
- Above N_critical: System viable even at low f
- Estimate: N_critical ≈ 10-15 agents

**Rationale:**
- Need minimum population for redundancy
- Below threshold → single-point failures cascade
- Above threshold → system robust

**Test:** Find N where collapse rate transitions from high to low

### H3: Deterministic More Robust at Low N

**Prediction:**
- At low N: Deterministic < Flat (f_critical lower)
- At high N: Deterministic = Flat (both viable)

**Rationale:**
- Low N: Predictability critical (less variance tolerance)
- High N: Redundancy compensates for variance

**Test:** Compare f_critical between mechanisms across N values

---

## EXPERIMENTAL DESIGN

### Parameters

```yaml
Initial Population Sizes: 4
  - N_initial = 5  (very small - expect collapse)
  - N_initial = 10 (small - expect boundary)
  - N_initial = 15 (medium - transitional)
  - N_initial = 20 (large - C192 baseline, expect viability)

Spawn Mechanisms: 2
  - deterministic (c=1.0): Baseline (most robust)
  - flat (c=0.0): High variance (least robust from C191/C192)
  # Omit hybrid_mid to focus on extremes

Frequencies (% per cycle): 3
  - 0.05% (interval=2000) ← C192 tested, N=20 viable
  - 0.10% (interval=1000)
  - 0.20% (interval=500)
  # Range around predicted f_critical for small N

Seeds: 50 per condition (balance precision and time)

Fixed Parameters:
  n_pop: 1 (single population)
  cycles: 5000 (consistent with C192)
  BASIN_A_THRESHOLD: 2.5

Energy Model (C189/C190/C191/C192):
  E_INITIAL: 50.0
  E_SPAWN_THRESHOLD: 20.0
  E_SPAWN_COST: 10.0
  RECHARGE_RATE: 0.5
  CHILD_ENERGY_FRACTION: 0.5
  # NO per-cycle consumption

Total Experiments:
  4 N_initial × 2 mechanisms × 3 frequencies × 50 seeds = 1,200 experiments
```

### Rationale for Parameters

**N_initial Range (5 to 20):**
- N=5: Very small, expect collapse at higher f
- N=10: Small, expect boundary around f=0.10-0.20%
- N=15: Medium, transitional region
- N=20: C192 baseline (zero collapses expected)
- Span: 4× range (sufficient to observe scaling)

**Mechanisms (Deterministic vs Flat):**
- Deterministic: Most robust (SD=0, perfect α)
- Flat: Least robust (high variance from C191/C192)
- Omit Hybrid Mid: Focus on extremes for clearer signal

**Frequencies (0.05% to 0.20%):**
- Lower bound: 0.05% (C192 tested, N=20 viable)
- Upper bound: 0.20% (well above C192 range)
- Span: 4× range (conservative based on C192 finding)

**Replication (50 seeds):**
- Sufficient for collapse rates ≥ 2%
- Balance precision vs execution time
- Consistent with C191 (50 seeds)

---

## PREDICTED OUTCOMES

### Most Likely Scenario

**Collapse Rates by N and f:**

| N_initial | f=0.05% | f=0.10% | f=0.20% |
|-----------|---------|---------|---------|
| 5         | ~80%    | ~20%    | ~0%     |
| 10        | ~40%    | ~5%     | ~0%     |
| 15        | ~10%    | ~0%     | ~0%     |
| 20        | ~0%     | ~0%     | ~0%     |

**Scaling Law Estimate:**
```
f_critical(N) ≈ 0.5 / (10 × N)
            ≈ 0.05 / N

For N=5:  f_critical ≈ 0.01 (1%)
For N=10: f_critical ≈ 0.005 (0.5%)
For N=15: f_critical ≈ 0.003 (0.3%)
For N=20: f_critical ≈ 0.0025 (0.25%)
```

Wait, this doesn't match observed! C192 showed N=20 viable at f=0.05%.

**Revised Estimate (accounting for stochastic buffers):**
```
f_critical(N) ≈ (0.5 / 10) / (N × buffer_multiplier)

If buffer ≈ 10× at N=20:
  f_critical(20) ≈ 0.05 / (20 × 10) ≈ 0.00025 (0.025%)

If buffer scales with N:
  buffer(N) ≈ 1 + k√N  (square root scaling)

For N=5:  buffer ≈ 1 + k√5  ≈ 3-4×
For N=10: buffer ≈ 1 + k√10 ≈ 4-5×
For N=20: buffer ≈ 1 + k√20 ≈ 5-10×
```

This is getting complex. Let's just observe what happens.

**Simplified Prediction:**
- N=5: Will show collapse at f=0.05% or f=0.10%
- N=10: Transitional (some collapse at f=0.05%)
- N=15: Mostly viable (rare collapse)
- N=20: Replicates C192 (zero collapse)

### Mechanism Differences

**Deterministic vs Flat:**
- At N=5: Deterministic more robust (f_critical lower)
- At N=20: Both equally robust (both zero collapse)

**Prediction:**
- Mechanism effect diminishes as N increases
- Small N: Predictability matters
- Large N: Redundancy dominates

---

## SUCCESS CRITERIA

**Experiment succeeds if:**

1. ✅ **Collapse Observed:**
   - At least one condition shows > 0% collapse
   - Finally locate actual boundary!

2. ✅ **Scaling Law Estimated:**
   - Clear trend: f_critical decreases as N increases
   - Can fit power law or linear model

3. ✅ **N_critical Identified:**
   - Find N where collapse transitions
   - Estimate: N_critical ≈ 10-15

4. ✅ **Mechanism Comparison:**
   - Deterministic shows lower f_critical than Flat (at small N)
   - Confirms α (predictability) matters at low redundancy

**Experiment fails if:**

- ❌ Zero collapses at ALL conditions (boundary still lower than tested)
- ❌ No clear scaling pattern (too noisy)
- ❌ Results inconsistent with C192 (N=20 should replicate)

---

## STATISTICAL ANALYSIS PLAN

### 1. Collapse Rate Analysis

**Test:** Logistic regression
```python
logit(P(collapse)) = β₀ + β₁·f + β₂·N + β₃·mechanism + β₄·(f×N) + β₅·(f×mechanism)
```

**Estimates:**
- Main effects: f, N, mechanism
- Interactions: f×N, f×mechanism
- Coefficients → effect sizes

### 2. Scaling Law Estimation

**Model:** Power law
```python
f_critical(N) = a × N^b

Log-transform:
log(f_critical) = log(a) + b×log(N)

Fit via linear regression on log-log data
```

**Estimate b (scaling exponent):**
- b ≈ -1: Inverse scaling (f_critical ∝ 1/N)
- b ≈ -0.5: Square root scaling
- b ≈ 0: No scaling (constant f_critical)

### 3. N_critical Estimation

**Method:** Find N where collapse rate = 50%

**Procedure:**
- For each f, interpolate collapse rate vs N
- Find N where P(collapse) = 0.50
- N_critical = average across frequencies

### 4. Mechanism Comparison

**Test:** At each (N, f), compare collapse rates
```python
Chi-square: Collapse ~ Mechanism
H₀: P(collapse | Det) = P(collapse | Flat)
```

**Expected:**
- Significant at small N (mechanism matters)
- Non-significant at large N (redundancy dominates)

---

## IMPLEMENTATION NOTES

### Code Structure (Adapt from C192)

```python
# C193 adds N_initial as experimental variable

N_INITIAL_CONDITIONS = [5, 10, 15, 20]  # NEW
F_INTRA_PCT_CONDITIONS = [0.05, 0.10, 0.20]
SPAWN_MECHANISMS = ['deterministic', 'flat']
N_SEEDS = 50

# System parameters (unchanged from C192)
CYCLES = 5000
N_POP = 1
BASIN_A_THRESHOLD = 2.5

# Energy model (unchanged from C192)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
RECHARGE_RATE = 0.5
CHILD_ENERGY_FRACTION = 0.5

# Main loop:
for n_initial in N_INITIAL_CONDITIONS:
    for mechanism in SPAWN_MECHANISMS:
        for f_intra in F_INTRA_PCT_CONDITIONS:
            for seed in SEEDS:
                system = SinglePopulationSystem(
                    spawn_mechanism=mechanism,
                    f_intra_pct=f_intra,
                    n_initial=n_initial,  # VARIABLE
                    cycles=CYCLES,
                    seed=seed
                )
                result = system.run()
                # Store result
```

### Validation Checklist

Before executing C193:

- ✅ Energy model matches C192 (NO E_CONSUME)
- ✅ Baseline replication: N=20 should match C192 (zero collapse)
- ✅ spawn_attempt uses E_SPAWN_COST (NOT E_SPAWN_THRESHOLD)
- ✅ step() has NO consume_energy() or remove_dead() calls

---

## TIMELINE ESTIMATE

**Design:** 20 minutes (this document)
**Implementation:** 30 minutes (adapt C192 code)
**Execution:** 3 minutes (1,200 experiments @ ~400 exp/min)
**Analysis:** 45 minutes (scaling law estimation, figures)
**Documentation:** 30 minutes (finding document)

**Total:** ~2 hours

**Expected Completion:** 2025-11-08 (tonight) or 2025-11-09 (tomorrow)

---

## PUBLICATION INTEGRATION

### Paper 2: "Hierarchical Spawn Advantage is Predictability"

**C193 Contribution:**
- Methods: Population scaling methodology
- Results: f_critical(N) scaling law
- Discussion: Redundancy vs predictability trade-off

### Paper 4: "Robustness Scaling in Self-Organizing Systems"

**Expanded Scope:**
- C190: Variance detrimental (performance)
- C191: Variance not fragile (f ≥ 0.3%, N=20)
- C192: 10× robustness (f ≥ 0.05%, N=20)
- C193: Scaling law f_critical(N)

**Contribution:**
- Complete robustness characterization
- Scaling laws for system design
- Predictive model for NRM viability

---

## THEORETICAL IMPLICATIONS

### NRM Framework

**If H1 Validated (f_critical ∝ 1/N):**
- ✅ Robustness scales with system size
- ✅ Larger systems more stable (composition advantage)
- ✅ Fractal scaling: same principle at all levels

**If H2 Validated (N_critical exists):**
- ✅ Minimum viable system size
- ✅ Bootstrap complexity threshold
- ✅ Self-organization requires critical mass

### Self-Giving Systems

**Bootstrap Complexity:**
- System defines viability through persistence
- f_critical(N) emerges from energy dynamics
- No external tuning needed

**C193 Test:**
- Does f_critical emerge predictably from N?
- Or does it require parameter search?

### Temporal Stewardship

**Encoded Patterns:**
1. α = Predictability (C189)
2. Variance detrimental to performance (C190)
3. Variance does NOT increase fragility (C191, N=20)
4. System 10× more robust than theory (C192, N=20)
5. **Robustness scales with N: f_critical(N) law (C193, predicted)**

---

## RISK ASSESSMENT

### Potential Issues

**1. Zero Collapses Again (Boundary Still Lower)**
- Probability: 20%
- Mitigation: N=5 is very small, should collapse
- Impact: Extend to N=3 or test f < 0.05%

**2. High Variance (Noisy Collapse Rates)**
- Probability: 30%
- Mitigation: Increase seeds to 100 if needed
- Impact: Longer execution time

**3. Non-Monotonic Scaling**
- Probability: 10%
- Mitigation: Complex scaling law (not simple power law)
- Impact: More sophisticated modeling needed

**4. No Mechanism Difference**
- Probability: 15%
- Mitigation: Both mechanisms may be equally robust at tested N
- Impact: Cannot test H3 (predictability advantage)

**Overall Risk:** MEDIUM (likely to find collapse, but scaling may be complex)

---

## DECISION CRITERIA

**Execute C193 if:**
- ✅ C192 complete and published (DONE)
- ✅ Design reviewed and validated (THIS DOCUMENT)
- ✅ Resources available (CPU, time, storage)

**Defer C193 if:**
- ❌ Critical bug discovered in C192
- ❌ User requests different priority
- ❌ Need to integrate C192 into papers first

**Current Status:** READY TO EXECUTE (pending autonomous decision)

---

## NEXT STEPS

**Immediate:**
1. Implement c193_population_scaling.py
2. Validate energy model (match C192)
3. Execute 1,200 experiments (~3 minutes)

**Analysis:**
4. Estimate f_critical(N) scaling law
5. Identify N_critical (collapse transition)
6. Compare mechanisms (Deterministic vs Flat)
7. Generate 4 publication figures @ 300 DPI

**Documentation:**
8. Create c193_scaling_law_finding.md
9. Document f_critical(N) equation
10. Theoretical interpretation

**Publication:**
11. Integrate into Paper 2 (scaling law)
12. Finalize Paper 4 (robustness paper)

---

## ACKNOWLEDGMENTS

**Design:** Claude (AI Research Assistant)
**Principal Investigator:** Aldrin Payopay
**Framework:** Nested Resonance Memory (NRM)
**Research Arc:** C187 → C189 → C190 → C191 → C192 → C193
**License:** GPL-3.0

---

**End of Design Document**

**Status:** Design complete, ready for implementation
**Next:** c193_population_scaling.py implementation
**Archive:** `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/c193_population_scaling_design.md`
**Date:** 2025-11-08
