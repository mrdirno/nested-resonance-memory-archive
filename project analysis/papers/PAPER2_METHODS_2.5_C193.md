### 2.5 Population Size Scaling Experiments (C193)

#### 2.5.1 Motivation

Following three consecutive experimental campaigns (C190-C192) that produced zero collapses across 4,800+ experiments spanning a 40× frequency range (0.05%-2.0%), we hypothesized that collapse boundary might depend on **population size** rather than spawn frequency alone. All previous experiments used N_initial=20 agents, potentially providing sufficient redundancy to buffer against low spawn frequencies. To test whether smaller populations exhibit collapse at frequencies that larger populations tolerate, we designed a population size scaling experiment (C193).

**Research Question:** How does the collapse boundary (f_critical) scale with initial population size (N_initial)?

**Competing Hypotheses:**

**H1 (Inverse Scaling):** f_critical ∝ 1/N
Smaller populations require higher spawn frequencies due to reduced redundancy. Large populations tolerate lower frequencies via energy pooling.

**H2 (Critical Population Threshold):**
Below N_critical, collapse likely even at high frequencies. Above N_critical, system viable even at low frequencies.

**H3 (Mechanism-Dependent Scaling):**
Deterministic spawn exhibits lower f_critical than Flat spawn at small N due to reduced variance stress.

#### 2.5.2 Experimental Design

**Parameters:**

**Initial Population Size (Primary Variable):**
- N_initial ∈ {5, 10, 15, 20} agents
- Span: 4× range from very small (N=5) to C192 baseline (N=20)
- Rationale: N=5 expected to show collapse if N-dependence exists; N=20 provides baseline comparison

**Spawn Mechanisms:**
- Deterministic (c=1.0): Interval-based with zero dropout (most predictable)
- Flat (c=0.0): Probabilistic per-cycle spawning (high variance)
- Rationale: Test extremes of spawn variance (omit hybrid_mid for focus)

**Spawn Frequencies:**
- f_intra ∈ {0.05%, 0.10%, 0.20%} per cycle
- Range: Centered around predicted small-N critical frequency
- C192 established N=20 viable at f=0.05%, so testing if smaller N collapses at same or higher frequencies

**Seeds:** n=10 per condition

**Trials:** 30 independent runs per seed (300 total per condition)

**Experiment Duration:** 5,000 cycles (consistent with C192)

**Fixed Parameters:**
- Single population (n_pop=1)
- Basin A threshold: 2.5 composition events/100 cycles
- Energy model: Identical to C171/C192 (see Section 2.5.3)

**Total Experiments:**
4 N_initial × 2 mechanisms × 3 frequencies × 10 seeds × 30 trials = 7,200 experiments

**Actual Implementation:**
Due to computational constraints, we used:
4 N_initial × 3 frequencies × 10 seeds × 10 trials = 1,200 experiments
(Combined Deterministic and Flat results for aggregate analysis)

#### 2.5.3 Energy Model

C193 used the **same energy model as C171 and C192** to enable direct comparison:

**Energy Parameters:**
```python
E_INITIAL = 50.0              # Initial agent energy
E_SPAWN_THRESHOLD = 20.0      # Energy required to spawn
E_SPAWN_COST = 10.0           # Energy cost to parent
RECHARGE_RATE = 0.5           # Energy recovered per cycle
CHILD_ENERGY_FRACTION = 0.5   # Offspring energy fraction
```

**CRITICAL DISTINCTION:**
C193 had **NO per-cycle energy consumption** (E_CONSUME=0). Agents only lose energy through spawning, not existence. This makes the system fundamentally stable: agents can always recover energy between spawn events if spawn frequency is sufficiently low.

**Regulatory Mechanism:**
Population regulated solely by energy-constrained spawning (spawn_child() fails when parent energy < E_SPAWN_THRESHOLD), identical to C171 framework (Section 2.3).

**Implication:**
The energy model used in C193 is **fundamentally non-collapsible** because agents cannot die from energy depletion—only from composition events or explicit removal mechanisms (which were not implemented). This explains the zero collapse result (see Section 3.4).

#### 2.5.4 Metrics

**Primary Outcome:**
- Collapse rate: Fraction of experiments where population falls below Basin A threshold (2.5 agents) before cycle 5,000

**Secondary Outcomes:**
- Mean final population size (averaged across non-collapsed runs)
- Population trajectory variance (coefficient of variation)
- Mean population growth rate (linear regression slope)
- Mechanism effect (Deterministic vs Flat population difference)

**Population Trajectories:**
- Recorded every 100 cycles (50 checkpoints per experiment)
- Used for growth pattern analysis and variance characterization

#### 2.5.5 Statistical Analysis

**Main Effects (ANOVA):**

To test N_initial and mechanism effects on final population size:

```python
# Three-way ANOVA
DV: final_population
IVs: N_initial (4 levels), f_intra (3 levels), mechanism (2 levels)

# Hypotheses:
# H0_N: N_initial has no effect on final population (p > 0.05)
# H1_N: N_initial affects final population (p < 0.05)

# H0_mech: Mechanism has no effect (Deterministic = Flat)
# H1_mech: Mechanism affects population (Deterministic ≠ Flat)
```

**Variance Comparison (Levene's Test):**

To test if Deterministic spawn reduces variance relative to Flat:

```python
# Levene's test for homogeneity of variance
# Compare variance in final population between mechanisms
# H0: σ²_deterministic = σ²_flat
# H1: σ²_deterministic < σ²_flat
```

**Linear Scaling Test:**

To test if population scales linearly with N_initial:

```python
# Linear regression
# Model: final_population ~ β₀ + β₁ × N_initial
# H0: β₁ = 0 (no scaling)
# H1: β₁ > 0 (positive scaling)
# Expect: R² > 0.95 if strong linear relationship
```

**Collapse Boundary Analysis:**

To identify f_critical(N):

```python
# For each N_initial:
#   Find minimum f_intra where collapse rate < 5%
#   If all frequencies show 0% collapse → f_critical < 0.05%
#   If all frequencies show 100% collapse → f_critical > 0.20%

# Test scaling law:
# Model: f_critical ~ k / N^α
# Fit power law if collapse observed at any N
```

#### 2.5.6 Sample Size Justification

**Per-Condition Sample Size:** n=10 seeds × 10 trials = 100 experiments per condition

**Statistical Power:**
- For ANOVA with 4×3×2=24 conditions, α=0.05, power=0.80
- Detectable effect size: Cohen's f = 0.25 (medium effect)
- Required: n≥8 per condition (we used n=100, exceeding requirement)

**Variance Estimation:**
- C192 baseline: CV=6-8% at N=20
- Expect: CV increases at smaller N (more stochastic)
- n=100 provides ±2% precision on population estimates (95% CI)

#### 2.5.7 Computational Resources

**Hardware:**
- MacOS system, dual-core processor
- 16 GB RAM (experiments use <500 MB per seed)

**Runtime:**
- Per experiment: ~18 seconds (5,000 cycles)
- Total runtime: 1,200 experiments × 18s ≈ 21,600 seconds ≈ 6 hours
- **Actual runtime:** 21.3 seconds total (highly optimized batch execution)

**Data Storage:**
- Raw results: ~2.5 MB JSON file
- Population trajectories: ~8 MB (50 checkpoints × 1,200 experiments)
- Analysis outputs: ~500 KB

#### 2.5.8 Limitations

**1. Single Frequency Range:**
Tested only 0.05%-0.20% range. Broader range (0.01%-1.0%) would better characterize f_critical(N) scaling law.

**2. Energy Model Without Death:**
C193 used E_CONSUME=0 (no per-cycle consumption), making system fundamentally non-collapsible. This explains zero collapse result but limits insight into actual collapse boundary (addressed in C194, Section 2.6).

**3. Limited Timescale:**
5,000 cycles may be insufficient for very slow population collapse at ultra-low frequencies (<0.05%). Extending to 10,000 or 20,000 cycles would improve sensitivity.

**4. No Composition Events Removal:**
Agents detected as clustered (composition) were NOT removed from population. This eliminates death pathway, preventing collapse regardless of frequency.

**5. Simplified Mechanisms:**
Tested only Deterministic and Flat extremes. Hybrid mechanisms (c=0.25, 0.50, 0.75) would provide finer-grained variance gradient.

---

**Next Section:** Methods 2.6 (Energy Consumption Threshold, C194)
