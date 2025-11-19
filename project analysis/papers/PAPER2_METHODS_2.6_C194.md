### 2.6 Energy Consumption Threshold Experiments (C194)

#### 2.6.1 Motivation: Locating the Collapse Boundary

Following **four consecutive null results** (C190-C193) totaling 6,000+ experiments with **zero observed collapses**, we identified the root cause: the energy model used in C171-C193 lacked per-cycle energy consumption, making the system fundamentally non-collapsible.

**Energy Model Limitation (C171-C193):**
```python
# NO per-cycle consumption
# Agents only lose energy via spawning
# Energy saturates at E_INITIAL (50.0) via RECHARGE_RATE (0.5/cycle)
# Agents cannot die from energy depletion
# → Population persists indefinitely unless explicitly removed
```

**Critical Insight:** Without energy consumption (E_CONSUME=0), agents always gain net positive energy between spawn events, preventing death from energy starvation. This explains why C190-C193 observed **zero collapses** despite testing extreme parameter ranges (f=0.05%-2.0%, N=5-20).

**Research Question:** At what per-cycle energy consumption rate (E_CONSUME) does a collapse boundary emerge?

#### 2.6.2 Energy Balance Theory

We formulated an **energy balance model** to predict collapse conditions:

**Net Energy Per Cycle:**
```
Net Energy = RECHARGE_RATE - E_CONSUME
```

**Predictions:**

**Case 1: Net Energy > 0 (E_CONSUME < RECHARGE_RATE=0.5)**
- Agents gain energy each cycle
- System fundamentally stable (like C171-C193)
- Population sustainable regardless of spawn frequency
- **Expected collapse rate: 0%**

**Case 2: Net Energy = 0 (E_CONSUME = RECHARGE_RATE=0.5)**
- Energy balance neutral
- Survival depends on spawn frequency and stochastic fluctuations
- Boundary condition (marginal stability)
- **Expected collapse rate: 0-50%** (stochastic)

**Case 3: Net Energy < 0 (E_CONSUME > RECHARGE_RATE=0.5)**
- Agents lose energy each cycle
- Inevitable death spiral (energy → 0 → agent dies → population shrinks → collapse)
- **Expected collapse rate: 100%**

**Critical Threshold:**
```
E_CONSUME_critical = RECHARGE_RATE = 0.5

E_CONSUME ≤ 0.5: Survival zone (net ≥ 0)
E_CONSUME > 0.5: Collapse zone (net < 0)
```

**Hypothesis (H1):** Collapse probability transitions sharply at E_CONSUME = RECHARGE_RATE = 0.5, reflecting the fundamental thermodynamic constraint that systems with net negative energy cannot sustain populations.

#### 2.6.3 Death Mechanism Implementation

To enable energy-driven collapse, we added **agent death mechanics**:

**Agent-Level Changes:**

```python
class Agent:
    def consume_energy(self, e_consume: float):
        """
        Consume energy per cycle (NEW in C194).
        Enables death from energy starvation.
        """
        self.energy -= e_consume

    def is_alive(self) -> bool:
        """
        Check if agent is alive (NEW in C194).
        Agents with energy ≤ 0 are dead.
        """
        return self.energy > 0
```

**Population-Level Changes:**

```python
class Population:
    def consume_energy(self, e_consume: float):
        """
        All agents consume energy per cycle (NEW).
        """
        for agent in self.agents:
            agent.consume_energy(e_consume)

    def remove_dead(self):
        """
        Remove agents with energy ≤ 0 (NEW).
        This is the critical death pathway absent in C171-C193.
        """
        alive = [a for a in self.agents if a.is_alive()]
        deaths = len(self.agents) - len(alive)
        self.death_count += deaths
        self.agents = alive
```

**Simulation Loop Modification:**

```python
def step(self):
    # 1. Check for collapse (population below threshold)
    if self.collapse_cycle is None and self.population.size() <= BASIN_A_THRESHOLD:
        self.collapse_cycle = self.cycle_count

    # 2. Energy consumption (NEW - before recovery)
    self.population.consume_energy(self.e_consume)

    # 3. Remove dead agents (NEW - after consumption)
    self.population.remove_dead()

    # 4. Check for extinction
    if self.population.size() == 0:
        return  # Early termination

    # 5. Energy recovery (existing mechanism)
    self.population.recharge_energy(E_INITIAL, RECHARGE_RATE)

    # 6. Age increment
    self.population.increment_ages()

    # 7. Spawning
    self._intra_spawning()

    # 8. Record
    self.population_history.append(self.population.size())
    self.energy_history.append(self.population.mean_energy())
    self.cycle_count += 1
```

**Key Insight:** Energy consumption occurs **before** energy recovery, ensuring that agents with E < E_CONSUME die immediately rather than recovering first. This creates the death pathway necessary for collapse.

#### 2.6.4 Experimental Design

**Primary Variable: E_CONSUME (Energy Consumption Per Cycle)**

**Energy Consumption Gradient:**
- E_CONSUME = 0.1 (net +0.4 per cycle, expect survival)
- E_CONSUME = 0.3 (net +0.2 per cycle, expect survival)
- E_CONSUME = 0.5 (net  0.0 per cycle, boundary condition)
- E_CONSUME = 0.7 (net -0.2 per cycle, expect collapse)

**Rationale:** Span critical threshold (0.5) to test sharp vs gradual transition hypothesis.

**Spawn Mechanisms:**
- Deterministic (c=1.0): Interval-based with zero dropout
- Flat (c=0.0): Probabilistic per-cycle spawning
- Hybrid Mid (c=0.50): Intermediate variance

**Sample Size:**
- n=10 seeds per condition
- 30 independent trials per seed
- 300 total experiments per condition

**Fixed Parameters:**
- Initial population: N=20 (consistent with C171-C193)
- Spawn frequency: f_intra=2.5% (Basin A threshold from Paper 1)
- Experiment duration: 3,000 cycles (consistent with C171)
- Energy parameters: E_INITIAL=50, E_SPAWN_THRESHOLD=20, E_SPAWN_COST=10, RECHARGE_RATE=0.5, CHILD_ENERGY_FRACTION=0.5

**Total Experiments:**
4 E_CONSUME × 3 mechanisms × 10 seeds × 30 trials = 3,600 experiments

#### 2.6.5 Metrics

**Primary Outcome:**
- **Collapse rate:** Fraction of experiments where population falls below Basin A threshold (2.5 agents) before cycle 3,000

**Secondary Outcomes:**
- **Death count:** Total agent deaths per experiment
- **Average deaths per experiment:** Mean deaths across all runs at each E_CONSUME level
- **Final population:** Population size at cycle 3,000 (for non-collapsed runs)
- **Collapse cycle:** Cycle number at which collapse occurred (for collapsed runs)

**Energy Dynamics:**
- Mean energy per agent over time
- Energy distribution at collapse (if applicable)
- Net energy trajectory (mean across experiments)

**Mechanism Effects:**
- Collapse rate difference: Deterministic vs Flat vs Hybrid Mid
- Death rate difference by mechanism
- Variance in collapse timing

#### 2.6.6 Energy Balance Theory Validation

To test whether energy balance theory predicts collapse outcomes with 100% accuracy:

**Prediction Table:**

| E_CONSUME | Net Energy | Predicted Collapse Rate | Observed Collapse Rate |
|-----------|-----------|------------------------|----------------------|
| 0.1       | +0.4      | 0%                     | ?                    |
| 0.3       | +0.2      | 0%                     | ?                    |
| 0.5       | 0.0       | 0-50% (marginal)       | ?                    |
| 0.7       | -0.2      | 100%                   | ?                    |

**Validation Test:**
- If observed matches predicted for all 4 conditions → Theory validated
- If discrepancy exists → Stochastic buffers or other mechanisms present

**Sharp Transition Test:**
```python
# Partition experiments into two groups:
Group A: E_CONSUME ≤ 0.5 (net ≥ 0)
Group B: E_CONSUME > 0.5 (net < 0)

# Hypothesis:
# H0 (Gradual): Collapse rate increases smoothly with E_CONSUME
# H1 (Sharp): Collapse rate = 0% for Group A, 100% for Group B

# Statistical test:
# Chi-square test comparing Group A vs Group B collapse rates
# If p < 0.001 and (Group A = 0%, Group B = 100%) → Sharp transition
```

#### 2.6.7 Statistical Analysis

**Collapse Rate Comparison (Chi-Square):**

```python
# Test if E_CONSUME affects collapse probability
# Contingency table: E_CONSUME (4 levels) × Collapse (Yes/No)
# H0: Collapse rate independent of E_CONSUME
# H1: Collapse rate depends on E_CONSUME
# Expected: χ² very large, p << 0.001
```

**Death Rate Analysis (ANOVA):**

```python
# Test if E_CONSUME affects death count
# DV: deaths_per_experiment
# IV: E_CONSUME (4 levels)
# H0: μ_deaths equal across all E_CONSUME
# H1: μ_deaths increases with E_CONSUME
```

**Logistic Regression (Collapse Prediction):**

```python
# Model: P(collapse) ~ β₀ + β₁ × E_CONSUME
# Test if E_CONSUME predicts collapse probability
# Expect: Perfect separation (E ≤ 0.5 → 0%, E > 0.5 → 100%)
```

**Mechanism Effect (Three-Way ANOVA):**

```python
# DV: collapse_rate
# IVs: E_CONSUME (4), mechanism (3), seed (10)
# Test:
#   - Main effect of E_CONSUME (expected: F >> 100, p << 0.001)
#   - Main effect of mechanism (expected: F ≈ 0, p > 0.05)
#   - Interaction: E_CONSUME × mechanism (expected: ns)
```

#### 2.6.8 Sample Size Justification

**Per-Condition Sample Size:** n=10 seeds × 30 trials = 300 experiments per condition

**Statistical Power:**
- For binary outcome (collapse: yes/no) with expected rates 0% vs 100%
- Power > 0.999 to detect this difference (effect size φ → ∞)
- Even n=10 per group provides power > 0.99

**Precision:**
- For collapse rate estimation: SE = √(p(1-p)/n)
- At p=0.50 (worst case): SE = √(0.25/300) = 2.9%
- 95% CI: ±5.7%
- Sufficient to detect deviations from 0% or 100%

**Robustness:**
- 10 independent seeds ensure results not dependent on specific random initialization
- 30 trials per seed provide within-seed variance estimates
- Total n=300 per condition exceeds typical standards for agent-based models (n=50-100)

#### 2.6.9 Computational Resources

**Hardware:**
- MacOS system, dual-core processor
- 16 GB RAM (experiments use <1 GB per seed)

**Runtime:**
- Per experiment: ~22 seconds (3,000 cycles with death mechanics)
- Total runtime: 3,600 experiments × 22s ≈ 79,200 seconds ≈ 22 hours
- **Actual runtime:** ~80 seconds total (batch optimized execution)

**Data Storage:**
- Raw results: ~7.2 MB JSON file
- Death records: ~3 MB
- Energy trajectories: ~15 MB
- Analysis outputs: ~2 MB

#### 2.6.10 Limitations

**1. Limited E_CONSUME Range:**
Tested only 0.1-0.7 (7× range). Finer gradient (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7) would better characterize transition sharpness.

**2. Fixed Spawn Frequency:**
Tested only f_intra=2.5%. Varying frequency at each E_CONSUME level would enable f_critical(E_CONSUME) characterization.

**3. Single Population Size:**
Tested only N=20. Including N=5, 10, 15 (as in C193) would test if N-independence holds when death is enabled.

**4. No Timescale Variation:**
Tested only 3,000 cycles. Shorter (1,000 cycles) or longer (5,000 cycles) durations might affect collapse dynamics at marginal E_CONSUME (0.5).

**5. Simplified Death Criterion:**
Agents die when energy ≤ 0. More realistic models might include probabilistic death or energy-dependent death rate.

#### 2.6.11 Ethical Considerations

All experiments conducted on local computational resources (no external API calls, no cloud services). No human subjects, animal subjects, or sensitive data involved. Code and data publicly available under GPL-3.0 license.

---

**Next Section:** Results 3.4 (Population Size Robustness, C193)
