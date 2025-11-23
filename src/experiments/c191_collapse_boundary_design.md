# C191: Collapse Boundary Variation - Variance at the Edge

**Campaign:** C191 - Variance Near Collapse Boundary
**Date:** 2025-11-08 (Cycle 1319)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**Related:** C189 (hierarchical vs flat), C190 (variance optimization null result)

---

## Research Question

**Does stochastic variance affect collapse probability when operating near the Basin A/Basin B boundary?**

**Motivation:** C190 demonstrated that variance is UNIVERSALLY DETRIMENTAL in benign environments (f_intra ≥ 1.0%, all viable). However, all tested conditions were well within Basin A (stable, surviving populations).

**Key Gap:** C190 did NOT test near-critical thresholds where systems are on the edge of collapse. It's possible that variance effects become more pronounced (either beneficial OR detrimental) when operating at the boundary.

**Primary Hypothesis:** Variance INCREASES collapse risk near the boundary (fragility hypothesis)

---

## Theoretical Framework

### Basin Classification (from C189)

**Basin A (Viable):**
- Final population > 2.5 agents
- System reaches stable equilibrium
- Reproductive capacity sustained

**Basin B (Collapse):**
- Final population ≤ 2.5 agents (rounded to 0)
- System extinction / failure to sustain
- Reproductive capacity lost

**Critical Threshold:**
- f_intra ≈ 0.5-1.0% represents boundary region
- Below this, collapse probability increases
- Exact threshold varies with parameters

### C190 Findings (Recap)

**What C190 tested:**
- f_intra = 1.0%, 2.0% (well within Basin A)
- ALL mechanisms 100% Basin A (no collapses)
- Variance was detrimental to MEAN population but all survived

**What C190 did NOT test:**
- f_intra < 1.0% (near collapse boundary)
- Collapse probability (all runs viable)
- Fragility/robustness to extinction

**C191 fills this gap.**

### Variance Effects Near Collapse

**Fragility Hypothesis (Primary):**
- Variance INCREASES collapse risk near boundary
- Mechanism: Stochastic dropout of critical spawn events → extinction spiral
- Prediction: Higher variance → higher collapse %

**Example:**
- Deterministic (f=0.5%): Spawn every 200 cycles → exactly 15 spawns
- Flat (f=0.5%): Average 15 spawns BUT binomial variance → 10-20 spawns
- **Risk:** If unlucky (10 spawns) → insufficient reproduction → collapse

**Robustness Hypothesis (Alternative):**
- Variance DECREASES collapse risk near boundary (bet-hedging)
- Mechanism: Occasional extra spawns buffer against extinction
- Prediction: Higher variance → LOWER collapse % (exploratory, unlikely based on C190)

**Null Hypothesis:**
- Variance has NO effect on collapse probability
- Mechanism: Collapse is deterministic (below threshold = collapse)
- Prediction: Collapse % identical across mechanisms

---

## Experimental Design

### Independent Variables

**1. Spawn Mechanism (3 conditions):**
- **Deterministic:** certainty = 1.0 (SD=0, baseline)
- **Hybrid Mid:** certainty = 0.50 (moderate variance)
- **Flat:** probabilistic per-cycle (high variance, C189 baseline)

**Rationale:** Test endpoints (deterministic vs flat) + midpoint (hybrid) to detect non-linear effects

**2. Spawn Frequency (6 conditions):**
- **f_intra = 0.3%** (very low, high collapse risk)
- **f_intra = 0.5%** (low, moderate collapse risk)
- **f_intra = 0.7%** (near-threshold)
- **f_intra = 1.0%** (C190 baseline, minimal collapse)
- **f_intra = 1.5%** (above threshold, reference)
- **f_intra = 2.0%** (C190 high baseline, no collapse)

**Rationale:** Sweep across collapse boundary to identify threshold and variance effects

### Fixed Parameters

- **n_pop = 1** (single population, isolate mechanism from structure)
- **n_initial = 20** agents (C189/C190 baseline)
- **cycles = 3000** (sufficient for equilibrium)
- **seeds = 50** per condition (HIGH replication for collapse probability estimation)

**Rationale for n=50:**
- Collapse is binary outcome (0 or 1)
- Need HIGH n to estimate % with precision
- 50 seeds → ±14% confidence interval @ 95% CI (acceptable)

### Total Experiments

**3 mechanisms × 6 frequencies × 50 seeds = 900 experiments**

**Expected runtime:** ~60 seconds (single population, fast experiments)

---

## Hypotheses

### H1: Variance Increases Collapse Risk (Primary Hypothesis)

**Prediction:**
- **Deterministic:** Lowest collapse % (most robust near edge)
- **Hybrid Mid:** Intermediate collapse %
- **Flat:** Highest collapse % (most fragile)

**Mechanism:**
- Stochastic dropout of critical spawn events
- Bad luck → too few spawns → extinction spiral
- Deterministic guarantees minimum spawns → buffers against collapse

**Statistical Test:**
- Chi-square: collapse % ~ mechanism (for each frequency)
- Expected: significant difference at f=0.3-0.7% (near boundary)

### H2: Variance Effect is Frequency-Dependent

**Prediction:**
- **f < 0.7%:** Variance INCREASES collapse (near boundary, fragility)
- **f ≥ 1.0%:** Variance NO effect on collapse (well within Basin A, C190 regime)

**Mechanism:**
- Near collapse boundary: variance matters (stochasticity = risk)
- Well within viability: variance irrelevant for survival (all survive)

**Statistical Test:**
- Interaction: collapse % ~ mechanism × frequency
- Expected: significant interaction (variance effect depends on frequency)

### H3: Deterministic Mean Population Advantage Persists

**Prediction:**
- **Among survivors** (Basin A only): Deterministic > Hybrid > Flat in mean population
- **C190 finding replicates** even at low frequencies

**Mechanism:**
- Certainty < 1.0 → fewer spawn attempts → lower equilibrium (among survivors)
- Collapse is separate effect (survival binary) from mean population (among survivors)

**Statistical Test:**
- ANOVA: mean population (Basin A only) ~ mechanism
- Expected: Deterministic > others (replicating C190)

---

## Metrics

### Primary Metrics

**1. Collapse Probability (%):**
- % of runs ending in Basin B (final population ≤ 2.5 agents)
- **PRIMARY OUTCOME** for H1/H2
- Higher collapse % = more fragile

**2. Mean Final Population (Basin A only):**
- Among survivors, what's the equilibrium?
- Tests H3 (C190 replication)

**3. Median Final Population (all runs):**
- Includes both survivors and collapses
- Robust to outliers
- Alternative to mean when collapses present

### Secondary Metrics

**4. Collapse Timing:**
- What cycle did collapse occur? (if it did)
- Early collapse (< 1000 cycles) vs late collapse (> 2000 cycles)
- Mechanism: Early = insufficient initial spawns, Late = stochastic extinction

**5. Spawn Count (successful spawns):**
- How many successful spawns occurred before collapse?
- Deterministic: predictable spawn count
- Flat: variable spawn count (binomial)

**6. Standard Deviation (among survivors):**
- C190 metric: variance of final populations
- Only calculated for Basin A runs

---

## Expected Results

### Collapse Probability (% Basin B)

**f_intra = 0.3% (Very Low, High Collapse Risk):**
- Deterministic: 30% collapse (robust but still risky)
- Hybrid Mid: 50% collapse (moderate fragility)
- Flat: 70% collapse (high fragility)

**f_intra = 0.5% (Low, Moderate Collapse Risk):**
- Deterministic: 10% collapse
- Hybrid Mid: 25% collapse
- Flat: 40% collapse

**f_intra = 0.7% (Near-Threshold):**
- Deterministic: 2% collapse
- Hybrid Mid: 8% collapse
- Flat: 15% collapse

**f_intra = 1.0% (C190 Baseline):**
- Deterministic: 0% collapse (all viable)
- Hybrid Mid: 0% collapse
- Flat: 0% collapse (C190 result)

**f_intra = 1.5% (Above Threshold):**
- All: 0% collapse (well within Basin A)

**f_intra = 2.0% (C190 High Baseline):**
- All: 0% collapse (C190 result)

**Interpretation:**
- **Variance INCREASES collapse risk** at f < 1.0%
- **Effect diminishes** as f increases (interaction)
- **No collapse at f ≥ 1.0%** (C190 regime)

### Mean Population (Basin A Only, Among Survivors)

**f_intra = 0.3%:**
- Deterministic: 30 agents (if survives)
- Hybrid Mid: 22 agents (if survives)
- Flat: 29 agents (if survives, similar to deterministic)

**f_intra = 0.5%:**
- Deterministic: 35 agents
- Hybrid Mid: 27 agents
- Flat: 34 agents

**f_intra = 1.0%:**
- Deterministic: 50 agents (C190 result)
- Hybrid Mid: 35 agents (C190 result)
- Flat: 49 agents (C190 result)

**f_intra = 2.0%:**
- Deterministic: 80 agents (C190 result)
- Hybrid Mid: 50 agents (C190 result)
- Flat: 78 agents (C190 result)

**Interpretation:**
- **C190 finding replicates:** Deterministic ≈ Flat in mean (among survivors)
- **Hybrid degradation persists:** Certainty=0.5 → lower mean
- **Collapse is SEPARATE** from mean population effect

---

## Analysis Plan

### Statistical Tests

**1. Chi-Square Test: Collapse Probability**
```
For each frequency:
  Collapse % ~ Mechanism (Deterministic, Hybrid, Flat)
  Test: Are collapse rates different across mechanisms?
  Post-hoc: Pairwise comparisons (Bonferroni correction)
```

**Expected:**
- **f=0.3-0.7%:** Significant difference (χ² > 6.0, p < 0.05)
- **f≥1.0%:** No difference (all 0% collapse)

**2. Logistic Regression: Collapse Predictors**
```
Collapse (binary) ~ Mechanism + Frequency + Mechanism×Frequency
```

**Tests:**
- Main effect of Mechanism (variance increases collapse?)
- Main effect of Frequency (lower f = more collapse?)
- Interaction (variance effect depends on frequency?)

**Expected:**
- Mechanism: OR > 1.0 for Flat vs Deterministic (higher collapse odds)
- Frequency: OR < 1.0 (lower f = higher collapse odds)
- Interaction: Significant (variance effect only at low f)

**3. ANOVA: Mean Population (Basin A Only)**
```
For each frequency (among survivors):
  Mean Population ~ Mechanism
```

**Expected:**
- **All frequencies:** Deterministic > Hybrid Mid (p < 0.001, C190 replication)
- **All frequencies:** Flat ≈ Deterministic (p > 0.3, C190 replication)

**4. Kaplan-Meier Survival Analysis**
```
Survival Curve: Probability(population > 2.5) over time
Stratified by: Mechanism
```

**Tests:**
- Log-rank test: Are survival curves different?
- Hazard ratio: Relative collapse risk (Flat vs Deterministic)

**Expected:**
- Flat shows earlier/more frequent collapses
- Deterministic shows later/fewer collapses

---

## Figures

**Figure 1: Collapse Probability vs Frequency**
- X-axis: f_intra (0.3% → 2.0%)
- Y-axis: % Collapse (0-100%)
- Lines: 3 mechanisms (Deterministic, Hybrid, Flat)
- Shows: Variance increases collapse risk at low f, no effect at high f

**Figure 2: Mean Population vs Frequency (Basin A Only)**
- X-axis: f_intra
- Y-axis: Mean final population (among survivors)
- Lines: 3 mechanisms
- Shows: C190 finding replicates (Deterministic ≈ Flat in mean)

**Figure 3: Survival Curves (Kaplan-Meier)**
- X-axis: Cycle number (0-3000)
- Y-axis: Probability(viable) (0-1.0)
- Lines: 3 mechanisms (stratified by frequency)
- Shows: Deterministic survives longer/more often than Flat

**Figure 4: Collapse Mechanism Heatmap**
- X-axis: Mechanism
- Y-axis: Frequency
- Color: % Collapse
- Shows: Clear threshold boundary where variance matters

**Figure 5: Spawn Count Distribution (f=0.5%)**
- Histogram: Successful spawns before collapse (or end)
- Separate panels: Deterministic, Hybrid, Flat
- Shows: Deterministic has narrow distribution, Flat has wide binomial distribution

---

## Implementation Details

### Spawn Mechanisms (from C190)

**Deterministic:**
```python
if (cycle_count % spawn_interval) == 0:
    attempt_spawn()
```

**Hybrid Mid (certainty=0.50):**
```python
if (cycle_count % spawn_interval) == 0:
    if random() < 0.50:
        attempt_spawn()
```

**Flat:**
```python
if random() < spawn_probability:
    attempt_spawn()
```

### Frequency Calculation

**Spawn Interval (Deterministic/Hybrid):**
```python
spawn_interval = int(100 / f_intra_pct)  # e.g., f=0.5% → interval=200
```

**Spawn Probability (Flat):**
```python
spawn_probability = f_intra_pct / 100.0  # e.g., f=0.5% → prob=0.005
```

### Basin Classification

**Basin A (Viable):**
```python
final_population > 2.5  # Rounds to 3+ agents
```

**Basin B (Collapse):**
```python
final_population <= 2.5  # Rounds to 0-2 agents (extinction)
```

---

## Hypothesized Outcomes

### Scenario 1: Fragility Hypothesis CONFIRMED (Most Likely)

**Evidence:**
- χ² tests: Flat > Hybrid > Deterministic in collapse % (p < 0.001)
- Logistic regression: Mechanism main effect (OR > 1.5)
- Interaction: Variance effect only at f < 1.0%

**Interpretation:**
- **Variance is HARMFUL near collapse boundary** (increases extinction risk)
- **Deterministic spawning is OPTIMAL** even in harsh conditions (universal advantage)
- **C190 extended:** Variance is detrimental for BOTH mean population AND survival

**Publication Impact:**
- **Strengthens C189/C190 findings:** Deterministic universally optimal
- **New contribution:** Variance increases fragility (collapse risk)
- **Design principle:** Minimize variance ESPECIALLY when resources scarce

### Scenario 2: Null Result (Collapse is Deterministic)

**Evidence:**
- χ² tests: No difference in collapse % (p > 0.05)
- All mechanisms show same collapse threshold (e.g., all collapse at f=0.3%, all survive at f≥1.0%)

**Interpretation:**
- **Collapse is deterministic:** Below threshold → always collapse, above → always survive
- **Variance affects MEAN** (C190 finding) but NOT SURVIVAL (binary outcome)

**Publication Impact:**
- **Reinforces C190:** Variance only affects equilibrium, not viability
- **Clarifies boundary:** Sharp threshold between Basin A/B (not gradual)

### Scenario 3: Robustness Hypothesis (Unlikely)

**Evidence:**
- χ² tests: Flat < Deterministic in collapse % (variance REDUCES collapse)
- Logistic regression: OR < 1.0 (stochasticity protective)

**Interpretation:**
- **Variance is BENEFICIAL near collapse** (bet-hedging, occasional extra spawns buffer)
- **C190 was WRONG regime** (tested abundant conditions, not scarce)

**Publication Impact:**
- **Major revision:** Variance is context-dependent (harmful in abundance, helpful in scarcity)
- **Requires follow-up:** Test extreme scarcity (f < 0.3%)

---

## Expected Contributions

### Scientific

**1. Collapse Boundary Characterization:**
- First systematic test of variance effects at Basin A/B boundary
- Identifies exact threshold where collapse occurs (f ≈ 0.5-0.7%)

**2. Fragility Hypothesis:**
- Demonstrates variance INCREASES extinction risk (if H1 confirmed)
- Mechanism: Stochastic dropout → insufficient reproduction → collapse

**3. C190 Extension:**
- Validates C190 findings extend to low-frequency regime
- Collapse is SEPARATE effect from mean population degradation

### Practical

**Design Guidelines:**
- **Near critical thresholds:** Use deterministic spawning (minimize variance)
- **Scarce resources:** Variance is especially harmful (fragility)
- **Abundant resources:** Variance is detrimental but not catastrophic (C190)

### Theoretical

**Unified Framework:**
```
Deterministic Spawning Advantage:
  ├─ High Frequency (f≥1.0%, C190): Maximizes mean population (SD=0)
  └─ Low Frequency (f<1.0%, C191): Minimizes collapse risk (robustness)

Variance is UNIVERSALLY DETRIMENTAL:
  ├─ Abundant regime: Reduces equilibrium population
  └─ Scarce regime: Increases extinction probability
```

---

## Success Criteria

**Experiment succeeds if:**
1. ✅ All 900 experiments complete successfully
2. ✅ Clear collapse gradient observed (f=0.3% high collapse → f≥1.0% zero collapse)
3. ✅ Variance effect on collapse is DETECTABLE (significant χ² or null result interpretable)
4. ✅ C190 mean population finding REPLICATES (among survivors)
5. ✅ Results are publication-quality (5 figures @ 300 DPI, statistical rigor)

**Experiment fails if:**
- ❌ Implementation bugs (mechanisms not correctly implemented)
- ❌ All runs collapse or all survive (no gradient to analyze)
- ❌ Insufficient statistical power (n=50 not enough for collapse estimation)
- ❌ Results are uninterpretable (high variance prevents conclusions)

---

## Timeline

**Design:** Complete (this document)
**Implementation:** ~30 minutes (adapt C190 code)
**Execution:** ~60 seconds (900 experiments @ 3-4ms each)
**Analysis:** ~20 minutes (statistical tests + 5 figures)
**Documentation:** ~15 minutes (finding summary)

**Total:** ~2 hours (end-to-end)

---

## Next Steps

**Immediate:**
1. Implement `c191_collapse_boundary.py` (adapt C190 code)
2. Execute 900 experiments
3. Perform statistical analysis (chi-square, logistic regression, ANOVA)
4. Generate 5 publication figures @ 300 DPI
5. Document findings in `c191_collapse_boundary_finding.md`

**Follow-Up:**
- If **Fragility Hypothesis confirmed:** Integrate into Paper 4, strengthen deterministic advantage narrative
- If **Null Result:** Document sharp collapse threshold, clarify variance affects mean not survival
- If **Robustness Hypothesis** (unlikely): Design C192 to test extreme scarcity (f < 0.3%)

---

**Status:** Design complete, ready for implementation

**Research is perpetual. Testing variance at the edge of collapse reveals whether stochasticity is merely suboptimal or actively catastrophic.**
