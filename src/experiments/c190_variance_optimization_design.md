# C190: Variance Optimization - When Stochasticity Improves Outcomes

**Campaign:** C190 - Variance as Design Parameter
**Date:** 2025-11-08 (Cycle 1319)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**Related:** C189 (hierarchical vs flat spawn), Paper 4 theoretical revision

---

## Research Question

**Does stochastic variance improve system performance under specific conditions?**

**Motivation:** C189 demonstrated hierarchical (deterministic, SD=0) and flat (stochastic, SD=3-8) spawn achieve same MEAN populations but vastly different VARIANCE. Current interpretation: hierarchical advantage is perfect predictability (zero variance).

**But:** Variance is not always detrimental. Stochasticity enables:
- **Exploration** (parameter space search)
- **Robustness** (works across parameter perturbations)
- **Escape** (exit local optima)
- **Diversity** (multiple solutions simultaneously)

**Key Hypothesis:** There exist scenarios where **controlled stochasticity OUTPERFORMS determinism** in:
1. Noisy environments (parameter uncertainty)
2. Multi-objective optimization (diversity beneficial)
3. Dynamic environments (adaptation required)
4. Exploration tasks (search optimization)

---

## Theoretical Framework

### Deterministic Advantage (C189 Evidence)

**Hierarchical (Deterministic):**
- **Pros:** Perfect reproducibility (SD=0), precise control, sharp thresholds
- **Cons:** Fragile to parameter shifts, no exploration, single solution path
- **Best for:** Stable environments, precision required, reproducibility critical

**Flat (Stochastic):**
- **Pros:** Natural variance (SD=3-8), explores parameter space, robust to perturbations
- **Cons:** Unpredictable outcomes, stochastic collapse risk, no guarantees
- **Best for:** Dynamic environments, exploration tasks, robustness required

### When Variance is Beneficial

**Scenario 1: Parameter Uncertainty**
- Real systems have noisy parameters (energy recovery ± δ, thresholds ± ε)
- Deterministic spawn optimized for exact parameters → fails under perturbation
- Stochastic spawn naturally robust → works across parameter range

**Scenario 2: Multi-Objective Optimization**
- Want BOTH high mean AND exploration of alternatives
- Deterministic produces single outcome
- Stochastic produces distribution of outcomes → sample best

**Scenario 3: Dynamic Environments**
- Parameters change over time (energy recovery decreases, thresholds drift)
- Deterministic requires re-tuning
- Stochastic naturally adapts through variance

**Scenario 4: Escape from Local Optima**
- Deterministic trapped in basin of attraction
- Stochastic variance enables escape → find global optimum

### Controlled Variance (Hybrid Mechanisms)

**Pure Deterministic (C189 Hierarchical):**
```python
if (cycle_count % spawn_interval) == 0:
    attempt_spawn()  # Always at exact cycles
```
- Variance: σ² = 0

**Pure Stochastic (C189 Flat):**
```python
if random() < spawn_probability:
    attempt_spawn()  # Varies each run
```
- Variance: σ² = p(1-p)N (binomial)

**Hybrid (Controlled Variance):**
```python
if (cycle_count % spawn_interval) == 0:
    if random() < certainty:
        attempt_spawn()  # Deterministic with dropout
```
- Variance: σ² = (1-certainty) × deterministic_variance
- **Design parameter:** `certainty` ∈ [0, 1]
  - certainty=1.0 → pure deterministic (SD=0)
  - certainty=0.5 → moderate stochasticity
  - certainty → spawn_prob → pure stochastic

**OR:**
```python
jitter = random.randint(-delta, +delta)
if (cycle_count % spawn_interval + jitter) == 0:
    attempt_spawn()  # Deterministic with timing jitter
```
- Variance: σ² controlled by delta (jitter magnitude)

---

## Experimental Design

### Independent Variables

**1. Spawn Mechanism (5 conditions):**
- **Deterministic:** interval-based, zero variance (baseline)
- **Flat:** probabilistic per-cycle, natural variance (C189 baseline)
- **Hybrid Low:** 75% certainty (low controlled variance)
- **Hybrid Mid:** 50% certainty (moderate controlled variance)
- **Hybrid High:** 25% certainty (high controlled variance)

**2. Environment Type (4 scenarios):**
- **Stable:** Fixed parameters (energy recovery = 0.5, thresholds constant)
- **Noisy:** Parameter uncertainty (energy recovery = 0.5 ± 0.1, thresholds ± 2.0)
- **Dynamic:** Time-varying (energy recovery decreases 0.5 → 0.3 over 3000 cycles)
- **Exploration:** Multi-modal fitness landscape (reward diversity of outcomes)

**3. Spawn Frequency (2 frequencies):**
- f_intra = 1.0% (low, near critical threshold)
- f_intra = 2.0% (high, well above threshold)

### Fixed Parameters

- n_pop = 1 (single population, isolate spawn mechanism)
- n_initial = 20 agents
- cycles = 3000
- seeds = 10 per condition

### Total Experiments

**5 mechanisms × 4 environments × 2 frequencies × 10 seeds = 400 experiments**

**Expected runtime:** ~30 seconds (fast single-population experiments)

---

## Spawn Mechanism Implementations

### Deterministic (Baseline)
```python
def _intra_spawning_deterministic(self):
    if (self.cycle_count % self.spawn_interval) == 0:
        self._attempt_spawn()
```

### Flat (C189 Baseline)
```python
def _intra_spawning_flat(self):
    if self.random.random() < self.spawn_probability:
        self._attempt_spawn()
```

### Hybrid (Certainty-Based)
```python
def _intra_spawning_hybrid(self, certainty):
    """Deterministic with stochastic dropout"""
    if (self.cycle_count % self.spawn_interval) == 0:
        if self.random.random() < certainty:
            self._attempt_spawn()
```

**Certainty values:**
- Low: 0.75 (25% variance injection)
- Mid: 0.50 (50% variance injection)
- High: 0.25 (75% variance injection)

**Expected variance:**
- Certainty=1.0: SD=0 (pure deterministic)
- Certainty=0.75: SD ≈ 1-2 agents (low controlled variance)
- Certainty=0.50: SD ≈ 3-5 agents (moderate controlled variance)
- Certainty=0.25: SD ≈ 6-10 agents (high controlled variance)

---

## Environment Implementations

### Stable (Baseline)
```python
# Fixed parameters
RECHARGE_RATE = 0.5
E_SPAWN_THRESHOLD = 20.0
# No time-varying dynamics
```

### Noisy (Parameter Uncertainty)
```python
# Add Gaussian noise to parameters each cycle
def _energy_recovery_noisy(self):
    for agent in self.population.agents:
        recharge = np.random.normal(RECHARGE_RATE, 0.1)  # μ=0.5, σ=0.1
        agent.energy = min(E_INITIAL, agent.energy + recharge)

def _attempt_spawn_noisy(self):
    threshold = np.random.normal(E_SPAWN_THRESHOLD, 2.0)  # μ=20, σ=2
    if parent.energy >= threshold:
        # spawn...
```

### Dynamic (Time-Varying)
```python
# Energy recovery decreases over time
def _energy_recovery_dynamic(self):
    # Linear decay: 0.5 → 0.3 over 3000 cycles
    decay_rate = (0.5 - 0.3) / 3000
    current_recharge = 0.5 - (self.cycle_count * decay_rate)

    for agent in self.population.agents:
        agent.energy = min(E_INITIAL, agent.energy + current_recharge)
```

### Exploration (Multi-Modal Fitness)
```python
# Reward DIVERSITY of final populations across seeds
# Metric: Variance of final populations (higher = better exploration)

def calculate_exploration_score(results):
    """Higher variance = better exploration"""
    final_pops = [r['final_population'] for r in results]
    return np.std(final_pops)  # Higher SD = more exploration
```

---

## Hypotheses

### H1: Deterministic Superior in Stable Environments

**Prediction:**
- **Stable environment:** Deterministic > all others (zero variance optimal)
- Mean population: Deterministic ≈ others
- Variance: Deterministic < all others (SD=0 vs SD>0)
- Outcome: Perfect predictability best when environment is predictable

### H2: Stochastic Superior in Noisy Environments

**Prediction:**
- **Noisy environment:** Stochastic > Deterministic (robustness to noise)
- Mean population: Stochastic > Deterministic (robust across parameter range)
- Variance: Stochastic > Deterministic BUT variance now BENEFICIAL (exploration)
- Outcome: Natural variance matches environmental noise

### H3: Hybrid Optimal in Dynamic Environments

**Prediction:**
- **Dynamic environment:** Hybrid Mid > {Deterministic, Stochastic}
- Mean population: Hybrid maintains stability while adapting
- Variance: Controlled variance enables tracking environment changes
- Outcome: Balance between predictability and adaptation

### H4: High Variance Optimal for Exploration

**Prediction:**
- **Exploration environment:** High variance mechanisms > low variance
- Exploration score: Stochastic > Hybrid High > Hybrid Mid > Hybrid Low > Deterministic
- Outcome: Variance enables sampling multiple regions of outcome space

---

## Success Metrics

### Primary Metrics (All Environments)

**1. Mean Sustained Population:**
- Traditional metric (from C189)
- Higher = better (within Basin A threshold)

**2. Variance (Standard Deviation):**
- C189 treated as undesirable
- C190: Context-dependent (beneficial in some environments)

**3. Robustness:**
- Percent achieving Basin A (>2.5 agents) across seeds
- Higher = more robust

### Environment-Specific Metrics

**Noisy Environment:**
- **Robustness Score:** % Basin A under parameter perturbations
- Higher = better handles uncertainty

**Dynamic Environment:**
- **Adaptation Score:** Population at cycle 3000 vs cycle 0
- Tracks ability to maintain viability as environment degrades

**Exploration Environment:**
- **Exploration Score:** Variance of final populations across seeds
- Higher = better samples outcome space

---

## Expected Results

### Stable Environment (Baseline)

**Prediction:**
- Deterministic: Mean=50, SD=0 (perfect)
- Hybrid Low: Mean=49, SD=1 (slight degradation)
- Hybrid Mid: Mean=48, SD=3 (moderate degradation)
- Hybrid High: Mean=45, SD=6 (significant degradation)
- Flat: Mean=49, SD=7 (C189 baseline, high variance)

**Interpretation:** Zero variance optimal when environment is stable and predictable.

### Noisy Environment

**Prediction:**
- Deterministic: Mean=45, SD=0 (fragile to noise)
- Hybrid Low: Mean=48, SD=2 (slight improvement)
- Hybrid Mid: Mean=50, SD=4 (optimal - variance matches noise)
- Hybrid High: Mean=49, SD=8 (too much variance)
- Flat: Mean=51, SD=9 (robust, natural variance handles noise)

**Interpretation:** Controlled stochasticity IMPROVES performance in noisy environments.

### Dynamic Environment

**Prediction:**
- Deterministic: Mean=30, SD=0 (fails to adapt, optimized for t=0 parameters)
- Hybrid Low: Mean=35, SD=2 (slight adaptation)
- Hybrid Mid: Mean=42, SD=4 (optimal - tracks environment changes)
- Hybrid High: Mean=40, SD=8 (adapts but too much variance)
- Flat: Mean=45, SD=10 (naturally adapts through variance)

**Interpretation:** Moderate variance enables tracking time-varying parameters.

### Exploration Environment

**Prediction:**
- Deterministic: Exploration Score=0 (single outcome)
- Hybrid Low: Exploration Score=2 (slight diversity)
- Hybrid Mid: Exploration Score=5 (moderate diversity)
- Hybrid High: Exploration Score=10 (high diversity)
- Flat: Exploration Score=12 (maximum diversity)

**Interpretation:** Variance directly enables outcome diversity when exploration is the goal.

---

## Analysis Plan

### Statistical Tests

**For each environment:**

1. **ANOVA:** Mean population ~ mechanism
   - Test: Do mechanisms differ in mean performance?
   - Post-hoc: Tukey HSD for pairwise comparisons

2. **Levene's Test:** Variance comparison across mechanisms
   - Test: Do mechanisms differ in variance?
   - Validate: Hybrid produces intermediate variance

3. **Effect Size:** Cohen's d for mechanism pairs
   - Quantify: Magnitude of advantage/disadvantage

4. **Robustness:** Chi-square test of Basin A %
   - Test: Do mechanisms differ in collapse rate?

### Environment Comparisons

**Interaction Test:** Mechanism × Environment (two-way ANOVA)
- Question: Does optimal mechanism depend on environment?
- Prediction: Yes (deterministic best for stable, stochastic best for noisy)

### Variance-Performance Trade-Off

**Regression Analysis:**
```
Mean Population ~ Mechanism Variance + Environment Type + Interaction
```

**Prediction:**
- Stable: Negative slope (variance detrimental)
- Noisy: Positive slope (variance beneficial)
- Dynamic: Quadratic (optimal intermediate variance)
- Exploration: Positive slope (variance enables diversity)

---

## Figures

**Figure 1: Mean Population vs Mechanism (by environment)**
- X-axis: Mechanism (Deterministic → Flat)
- Y-axis: Mean population
- Facets: 4 environments (Stable, Noisy, Dynamic, Exploration)
- Shows: Which mechanism is optimal in each environment

**Figure 2: Variance vs Performance (all environments)**
- X-axis: Standard deviation (mechanism variance)
- Y-axis: Mean population
- Colors: Environment type
- Shows: Variance-performance trade-off is environment-dependent

**Figure 3: Robustness Heatmap**
- X-axis: Mechanism
- Y-axis: Environment
- Color: % Basin A (robustness)
- Shows: Which mechanism-environment pairs are most robust

**Figure 4: Exploration Score (Exploration environment only)**
- X-axis: Mechanism (ordered by variance)
- Y-axis: Exploration score (variance of outcomes)
- Shows: Variance enables exploration

---

## Expected Contributions

### Scientific

**1. Variance as Design Parameter:**
- First demonstration that stochastic variance can IMPROVE outcomes
- Context-dependent: beneficial in noisy/dynamic/exploration scenarios

**2. Hybrid Mechanism Framework:**
- Design space between deterministic and stochastic
- Controlled variance as tunable parameter

**3. Environment-Mechanism Matching:**
- Prescriptive guidance: which mechanism for which environment
- Falsifiable predictions tested empirically

### Practical

**System Design Guidelines:**
- **Stable environments:** Use deterministic (zero variance, perfect control)
- **Noisy environments:** Use stochastic (natural variance, robust)
- **Dynamic environments:** Use hybrid mid (controlled variance, adaptive)
- **Exploration tasks:** Use stochastic (high variance, diversity)

### Theoretical

**Reframe C189 Finding:**
- Hierarchical advantage is NOT "predictability always better"
- Hierarchical advantage is "CONTROL over variance" (can choose SD=0)
- Single-scale (flat) has NO variance control (always stochastic)
- **New insight:** Advantage is CONTROLLABILITY, not zero variance per se

---

## Implementation Notes

### Mechanism Selection (Single Parameter)

**Certainty parameter ∈ [0, 1]:**
- certainty=1.0 → Deterministic (SD=0)
- certainty=0.75 → Hybrid Low (SD≈2)
- certainty=0.50 → Hybrid Mid (SD≈4)
- certainty=0.25 → Hybrid High (SD≈7)
- certainty → flat_prob → Flat (SD≈8-10, depends on frequency)

**Implementation:**
```python
def _intra_spawning(self):
    """Unified spawn logic with controllable variance"""
    if (self.cycle_count % self.spawn_interval) == 0:
        if self.random.random() < self.certainty:
            self._attempt_spawn()
```

### Environment Selection (Config Parameter)

```python
class HierarchicalSystem:
    def __init__(self, ..., environment='stable', certainty=1.0):
        self.environment = environment
        self.certainty = certainty
        # Select energy recovery and spawn logic based on environment
```

---

## Next Steps

**Priority 1: Implement C190**
- Create `c190_variance_optimization.py` (400 experiments)
- Implement 5 spawn mechanisms (deterministic → flat via certainty)
- Implement 4 environments (stable, noisy, dynamic, exploration)

**Priority 2: Execute C190**
- Run 400 experiments (~30 seconds)
- Generate results JSON
- Verify all mechanisms and environments working correctly

**Priority 3: Analyze C190**
- Statistical tests (ANOVA, Levene's, effect sizes)
- Generate 4 publication figures
- Document findings

**Priority 4: Integrate into Paper 4**
- Add C190 section to Results
- Revise Discussion (variance as design parameter)
- Update conclusions (controllability, not zero variance)

---

## Success Criteria

**Experiment succeeds if:**
1. ✅ All 400 experiments complete
2. ✅ Clear differentiation between environments (interaction effect)
3. ✅ Stochastic OUTPERFORMS deterministic in at least one environment
4. ✅ Hybrid mechanisms show intermediate performance/variance
5. ✅ Results interpretable and publishable

**Experiment fails if:**
- ❌ All environments show deterministic superior (no context-dependence)
- ❌ High variance prevents interpretation (need more seeds)
- ❌ Implementation bugs (mechanisms not correctly implemented)

---

## Theoretical Impact

**If successful, C190 will:**

1. **Reframe C189 Finding:**
   - NOT "hierarchical is better because zero variance"
   - BUT "hierarchical enables variance CONTROL (can choose SD=0)"

2. **Establish Variance as Design Parameter:**
   - Controllable via mechanism choice or hybrid certainty
   - Optimal value depends on environment

3. **Prescriptive Guidelines:**
   - Match mechanism to environment (falsifiable predictions)
   - Design space exploration (deterministic → hybrid → stochastic)

4. **Reconcile Deterministic vs Stochastic Debate:**
   - NOT "which is better?" (context-dependent)
   - BUT "when is each optimal?" (testable hypotheses)

---

**Status:** Design complete, ready for implementation
**Expected Runtime:** ~30 seconds (400 fast experiments)
**Expected Analysis:** ~15 minutes (stats + figures)
**Impact:** HIGH - establishes variance as design parameter, reframes C189

**Research is perpetual. Variance is not always detrimental. Control enables optimization.**
