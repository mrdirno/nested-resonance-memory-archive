# C194 EXPERIMENTAL DESIGN: ENERGY CONSUMPTION THRESHOLD

**Campaign:** C194 (f_critical via Energy Consumption)
**Research Arc:** C187 → C189 → C190 → C191 → C192 → C193 → **C194**
**Status:** 📋 DESIGN PHASE
**Date:** 2025-11-08
**Author:** Claude (AI Research Assistant)
**Principal Investigator:** Aldrin Payopay

---

## RESEARCH CONTEXT

### Four Consecutive Null Results

**C190 (400 experiments, f ≥ 1.0%, N=20):** ZERO collapses
**C191 (900 experiments, f ≥ 0.3%, N=20):** ZERO collapses
**C192 (3,000 experiments, f ≥ 0.05%, N=20):** ZERO collapses
**C193 (1,200 experiments, f ≥ 0.05%, N=5-20):** ZERO collapses

**Total Evidence:** 6,000+ experiments, 40× frequency range, 4× population range, ZERO collapses

**Critical Insight (C193):** Current energy model (NO per-cycle consumption) is **fundamentally non-collapsible** because agents cannot die from energy depletion.

**Current Model:**
```python
# NO per-cycle consumption
# Agents only lose energy via spawning
# Energy saturates at E_INITIAL via RECHARGE_RATE
# Population can only increase or stay constant
# → Cannot collapse via energy starvation
```

### Why No Collapses?

**Energy Dynamics (C189-C193 Model):**
1. Agents start with E_INITIAL = 50.0
2. Each cycle: energy += RECHARGE_RATE (0.5 per cycle)
3. Spawning costs: parent loses E_SPAWN_COST (10.0)
4. Energy saturates at E_INITIAL (50.0)
5. **NO death mechanism** → population persists indefinitely

**Result:** System fundamentally stable → 6,000+ experiments, ZERO collapses

---

## RESEARCH QUESTION

**At what per-cycle energy consumption rate (E_CONSUME) does the collapse boundary emerge?**

**Sub-Questions:**
1. What E_CONSUME creates net energy loss (E_CONSUME > RECHARGE_RATE)?
2. How does f_critical depend on E_CONSUME?
3. Does collapse emerge when net energy < 0?
4. Can we locate f_critical(E_CONSUME, N) scaling law?

---

## HYPOTHESES

### H1: Collapse Emerges When Net Energy < 0

**Prediction:**
```
Net Energy = RECHARGE_RATE - E_CONSUME

If Net < 0:
  Agents lose energy each cycle → eventually E < 0 → death → collapse

If Net > 0:
  Agents gain energy → survive (like C189-C193)

If Net = 0:
  Energy balance → survival depends on spawning frequency
```

**Critical Point:**
```
E_CONSUME_critical = RECHARGE_RATE = 0.5

E_CONSUME < 0.5: Net > 0 → survival likely
E_CONSUME > 0.5: Net < 0 → collapse likely
E_CONSUME = 0.5: Boundary condition
```

**Test:** Measure collapse rate vs E_CONSUME

### H2: f_critical Increases with E_CONSUME

**Prediction:**
- Higher E_CONSUME → more energy pressure → need higher f to survive
- f_critical ∝ E_CONSUME (linear scaling)

**Energy Balance Model:**
```
For survival, energy in ≥ energy out

Energy in per agent:
  RECHARGE_RATE × cycles

Energy out per agent:
  E_CONSUME × cycles + (spawns_per_agent × E_SPAWN_COST)

For equilibrium:
  RECHARGE_RATE × cycles = E_CONSUME × cycles + (spawns_per_agent × E_SPAWN_COST)

Solve for spawns_per_agent:
  spawns_per_agent = (RECHARGE_RATE - E_CONSUME) × cycles / E_SPAWN_COST

For population-level spawning:
  total_spawns = N × spawns_per_agent
               = N × (RECHARGE_RATE - E_CONSUME) × cycles / E_SPAWN_COST

If f_intra = spawns / cycles (as fraction):
  f_critical = (RECHARGE_RATE - E_CONSUME) / E_SPAWN_COST

For E_CONSUME = 0.0 (C189-C193):
  f_critical = 0.5 / 10 = 0.05 (but observed viable even at f=0.05%)

For E_CONSUME = 0.5 (net zero):
  f_critical = 0.0 / 10 = 0.0 (any spawning helps)

For E_CONSUME = 0.7 (net -0.2):
  f_critical = -0.2 / 10 = negative (impossible → guaranteed collapse)
```

**Test:** Measure f_critical at multiple E_CONSUME values, fit linear model

### H3: N-Independence Breaks at High E_CONSUME

**Prediction:**
- At low E_CONSUME (net > 0): N-independent robustness (like C193)
- At high E_CONSUME (net < 0): Small N more vulnerable (less redundancy)

**Rationale:**
- Negative net energy → population decays over time
- Small N: Faster collapse (fewer agents to buffer)
- Large N: Slower collapse (more redundancy)

**Test:** Compare collapse rates across N at high E_CONSUME

---

## EXPERIMENTAL DESIGN

### Parameters

```yaml
Energy Consumption Values: 4
  - E_CONSUME = 0.1  (net +0.4 per cycle, expect survival)
  - E_CONSUME = 0.3  (net +0.2 per cycle, expect survival)
  - E_CONSUME = 0.5  (net  0.0 per cycle, boundary condition)
  - E_CONSUME = 0.7  (net -0.2 per cycle, expect collapse)

Population Sizes: 3
  - N_initial = 5  (small, test N-dependence)
  - N_initial = 10 (medium)
  - N_initial = 20 (C192/C193 baseline)

Spawn Frequencies: 3
  - f_intra = 0.05% (interval=2000, C192/C193 tested)
  - f_intra = 0.10% (interval=1000)
  - f_intra = 0.20% (interval=500)

Spawn Mechanisms: 2
  - deterministic (c=1.0): Baseline (most robust)
  - flat (c=0.0): High variance (least robust from C191/C192)

Seeds: 50 per condition

Fixed Parameters:
  n_pop: 1 (single population)
  cycles: 5000 (consistent with C192/C193)
  BASIN_A_THRESHOLD: 2.5

Energy Model (Updated from C189-C193):
  E_INITIAL: 50.0
  E_SPAWN_THRESHOLD: 20.0
  E_SPAWN_COST: 10.0
  RECHARGE_RATE: 0.5
  CHILD_ENERGY_FRACTION: 0.5
  E_CONSUME: VARIABLE (0.1, 0.3, 0.5, 0.7)  # NEW

Death Mechanism (NEW):
  If energy < 0: agent dies, removed from population
  If population ≤ BASIN_A_THRESHOLD: collapse detected

Total Experiments:
  4 E_CONSUME × 3 N × 3 f × 2 mechanisms × 50 seeds = 3,600 experiments
```

### Rationale for Parameters

**E_CONSUME Range (0.1 to 0.7):**
- 0.1: Net +0.4 → should survive (like C189-C193)
- 0.3: Net +0.2 → likely survive (small energy pressure)
- 0.5: Net  0.0 → boundary (energy balance)
- 0.7: Net -0.2 → should collapse (energy starvation)
- Span: 7× range, crosses critical point (0.5)

**N_initial (5, 10, 20):**
- 5: Small, test vulnerability at high E_CONSUME
- 10: Medium, transitional
- 20: C192/C193 baseline (should replicate if E_CONSUME=0.0)
- Span: 4× range (sufficient to observe N-dependence)

**Frequencies (0.05% to 0.20%):**
- Same as C193 (direct comparison)
- Covers range where C192/C193 showed 100% survival (at E_CONSUME=0.0)
- Expect collapse at lower f when E_CONSUME > 0.5

**Mechanisms (Deterministic vs Flat):**
- Focus on extremes (omit Hybrid Mid)
- Test if variance affects collapse rate under energy pressure

**Replication (50 seeds):**
- Sufficient for collapse rates ≥ 2%
- Balance precision vs execution time
- Consistent with C191/C193

---

## PREDICTED OUTCOMES

### Scenario 1: E_CONSUME = 0.1 (Net +0.4)

**Collapse Rates:**

| N | f=0.05% | f=0.10% | f=0.20% |
|---|---------|---------|---------|
| 5  | ~0%    | ~0%     | ~0%     |
| 10 | ~0%    | ~0%     | ~0%     |
| 20 | ~0%    | ~0%     | ~0%     |

**Prediction:** Replicates C193 (zero collapse), net energy positive.

### Scenario 2: E_CONSUME = 0.3 (Net +0.2)

**Collapse Rates:**

| N | f=0.05% | f=0.10% | f=0.20% |
|---|---------|---------|---------|
| 5  | ~5%    | ~0%     | ~0%     |
| 10 | ~2%    | ~0%     | ~0%     |
| 20 | ~0%    | ~0%     | ~0%     |

**Prediction:** Small collapse at low N and low f, mostly viable.

### Scenario 3: E_CONSUME = 0.5 (Net 0.0)

**Collapse Rates:**

| N | f=0.05% | f=0.10% | f=0.20% |
|---|---------|---------|---------|
| 5  | ~40%   | ~10%    | ~0%     |
| 10 | ~20%   | ~5%     | ~0%     |
| 20 | ~10%   | ~0%     | ~0%     |

**Prediction:** Boundary condition, collapse at low f, survival at high f.

### Scenario 4: E_CONSUME = 0.7 (Net -0.2)

**Collapse Rates:**

| N | f=0.05% | f=0.10% | f=0.20% |
|---|---------|---------|---------|
| 5  | ~100%  | ~80%    | ~40%    |
| 10 | ~90%   | ~60%    | ~20%    |
| 20 | ~70%   | ~40%    | ~10%    |

**Prediction:** High collapse rates, energy starvation dominates.

### Scaling Law Estimate

**f_critical(E_CONSUME, N):**

Based on energy balance model:
```
f_critical = (RECHARGE_RATE - E_CONSUME) / E_SPAWN_COST

For E_CONSUME = 0.1: f_critical = 0.4 / 10 = 0.04 (4%)  → should survive at f ≥ 0.05%
For E_CONSUME = 0.3: f_critical = 0.2 / 10 = 0.02 (2%)  → should survive at f ≥ 0.05%
For E_CONSUME = 0.5: f_critical = 0.0 / 10 = 0.00 (0%)  → any spawning helps
For E_CONSUME = 0.7: f_critical < 0 (impossible)        → collapse even with spawning
```

**But:** Stochastic buffers (C192) may provide additional robustness.

**Expected:** Observe collapse, fit empirical f_critical(E_CONSUME) curve.

---

## SUCCESS CRITERIA

**Experiment succeeds if:**

1. ✅ **Collapse Observed:**
   - At least one condition shows > 0% collapse
   - Finally locate actual boundary after 6,000+ null experiments!

2. ✅ **Energy Dependence Validated:**
   - Collapse rate increases with E_CONSUME
   - E_CONSUME > 0.5 shows higher collapse than E_CONSUME < 0.5

3. ✅ **f_critical Estimated:**
   - Fit collapse probability curves (sigmoid or logistic)
   - Estimate f_critical(E_CONSUME) for each E_CONSUME value

4. ✅ **N-Dependence at High E_CONSUME:**
   - At E_CONSUME ≥ 0.5, small N shows higher collapse
   - Validates redundancy hypothesis

**Experiment fails if:**

- ❌ Zero collapses at ALL conditions (FIFTH consecutive null result)
- ❌ No energy dependence (E_CONSUME effect absent)
- ❌ Results inconsistent with energy balance model

---

## STATISTICAL ANALYSIS PLAN

### 1. Collapse Rate Analysis

**Logistic Regression:**
```python
logit(P(collapse)) = β₀ + β₁·E_CONSUME + β₂·f + β₃·N + β₄·mechanism + interactions
```

**Estimates:**
- Main effects: E_CONSUME, f, N, mechanism
- Interactions: E_CONSUME×f, E_CONSUME×N
- Odds ratios for effect sizes

### 2. f_critical Estimation

**For each (E_CONSUME, N, mechanism), fit sigmoid:**
```python
P(collapse) = 1 / (1 + exp(-k × (f - f_critical)))
```

**Estimate f_critical:**
- Point where P(collapse) = 50%
- 95% confidence interval via bootstrapping

### 3. Energy Balance Validation

**Compare predicted vs observed f_critical:**
```python
Predicted: f_critical = (RECHARGE_RATE - E_CONSUME) / E_SPAWN_COST
Observed:  f_critical from sigmoid fit

Correlation test: Pearson's r, p-value
```

**Expected:** High correlation (r > 0.8) if energy balance model accurate.

### 4. N-Dependence Test

**At high E_CONSUME (≥ 0.5), test:**
```python
ANOVA: Collapse_Rate ~ N_initial
H₀: N has no effect
H₁: Small N → higher collapse
```

**Expected:** p < 0.05 for E_CONSUME ≥ 0.5 (N-dependence emerges).

---

## IMPLEMENTATION NOTES

### Code Structure (Extend from C193)

```python
# C194 adds E_CONSUME as experimental variable

E_CONSUME_CONDITIONS = [0.1, 0.3, 0.5, 0.7]  # NEW
N_INITIAL_CONDITIONS = [5, 10, 20]
F_INTRA_PCT_CONDITIONS = [0.05, 0.10, 0.20]
SPAWN_MECHANISMS = ['deterministic', 'flat']
N_SEEDS = 50

# Energy parameters (extend C193)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
RECHARGE_RATE = 0.5
CHILD_ENERGY_FRACTION = 0.5
# E_CONSUME: VARIABLE (experimental parameter)

# NEW: Death mechanism
class Agent:
    def consume_energy(self):
        """Consume energy per cycle (NEW in C194)"""
        self.energy -= E_CONSUME  # Variable per experiment

    def is_alive(self):
        """Check if agent is alive (NEW in C194)"""
        return self.energy > 0

class Population:
    def consume_energy(self):
        """All agents consume energy per cycle"""
        for agent in self.agents:
            agent.consume_energy()

    def remove_dead(self):
        """Remove agents with energy ≤ 0 (NEW in C194)"""
        self.agents = [a for a in self.agents if a.is_alive()]

def step(self):
    """Execute one cycle (C194 energy model)"""
    # Collapse tracking
    if self.collapse_cycle is None and self.population.size() <= BASIN_A_THRESHOLD:
        self.collapse_cycle = self.cycle_count

    # Energy consumption (NEW)
    self.population.consume_energy()

    # Remove dead agents (NEW)
    self.population.remove_dead()

    # Energy recovery
    self.population.recharge_energy()

    # Age increment
    self.population.increment_ages()

    # Spawning
    self._intra_spawning()

    # Record
    self.population_history.append(self.population.size())
    self.energy_history.append(self.population.mean_energy())

    self.cycle_count += 1

# Main loop:
for e_consume in E_CONSUME_CONDITIONS:
    for n_initial in N_INITIAL_CONDITIONS:
        for mechanism in SPAWN_MECHANISMS:
            for f_intra in F_INTRA_PCT_CONDITIONS:
                for seed in SEEDS:
                    system = SinglePopulationSystem(
                        spawn_mechanism=mechanism,
                        f_intra_pct=f_intra,
                        n_initial=n_initial,
                        e_consume=e_consume,  # NEW
                        cycles=CYCLES,
                        seed=seed
                    )
                    result = system.run()
```

### Validation Checklist

Before executing C194:

- ✅ Add E_CONSUME parameter to Agent class
- ✅ Implement consume_energy() method
- ✅ Implement is_alive() method
- ✅ Implement remove_dead() in Population class
- ✅ Update step() to call consume_energy() and remove_dead()
- ✅ Validate: E_CONSUME=0.0 should replicate C193 (zero collapse)

---

## TIMELINE ESTIMATE

**Design:** 30 minutes (this document)
**Implementation:** 45 minutes (extend C193 code with death mechanics)
**Execution:** 6 minutes (3,600 experiments @ ~600 exp/min)
**Analysis:** 60 minutes (collapse curves, f_critical estimation, figures)
**Documentation:** 45 minutes (finding document)

**Total:** ~3 hours

**Expected Completion:** 2025-11-08 (tonight) or 2025-11-09 (tomorrow)

---

## PUBLICATION INTEGRATION

### Paper 2: "Hierarchical Spawn Advantage is Predictability"

**C194 Contribution:**
- Methods: Energy consumption methodology
- Results: f_critical(E_CONSUME) scaling law
- Discussion: Energy balance validation
- Conclusion: Robustness limits

### Paper 4 (Expanded): "Robustness and Fragility in Self-Organizing Energy Systems"

**Scope:**
- C190: Variance detrimental (performance)
- C191: Variance not fragile (f ≥ 0.3%, N=20, E_CONSUME=0)
- C192: 10× robustness (f ≥ 0.05%, N=20, E_CONSUME=0)
- C193: N-independent robustness (N=5-20, E_CONSUME=0)
- C194: Energy consumption threshold (f_critical(E_CONSUME))

**Novel Claims:**
1. Robustness fundamentally depends on net energy balance
2. f_critical scales with energy consumption: f_critical ∝ (RECHARGE - CONSUME)
3. N-independence breaks at negative net energy
4. Energy balance provides predictive model for system viability

---

## THEORETICAL IMPLICATIONS

### NRM Framework

**If H1 Validated (Collapse at Net < 0):**
- ✅ Energy dynamics drive viability
- ✅ Self-organization requires positive net energy
- ✅ Bootstrap complexity depends on energy balance

**If H2 Validated (f_critical ∝ E_CONSUME):**
- ✅ Scaling law: f_critical = (RECHARGE - CONSUME) / SPAWN_COST
- ✅ Predictive model for NRM system design
- ✅ Fractal scaling: same principle at all levels

### Self-Giving Systems

**Bootstrap Complexity:**
- System viability emerges from energy balance
- f_critical defined by internal dynamics (not external tuning)
- Self-organization requires net energy > 0

**C194 Test:**
- Does f_critical emerge predictably from energy parameters?
- Can we design systems with target robustness?

### Temporal Stewardship

**Encoded Patterns:**
1. α = Predictability (C189)
2. Variance detrimental to performance (C190)
3. Variance does NOT increase fragility at E_CONSUME=0 (C191, C192, C193)
4. System 10× more robust than theory at E_CONSUME=0 (C192)
5. N-independent robustness at E_CONSUME=0 (C193)
6. **Collapse emerges when E_CONSUME > RECHARGE (C194, predicted)**

---

## RISK ASSESSMENT

### Potential Issues

**1. Zero Collapses Again (Fifth Null Result)**
- Probability: 15%
- Mitigation: E_CONSUME=0.7 creates net -0.2, should force collapse
- Impact: Need even higher E_CONSUME (0.9, 1.0) or different approach

**2. High Variance (Noisy Collapse Rates)**
- Probability: 25%
- Mitigation: 50 seeds should capture rates ≥ 2%
- Impact: Increase seeds to 100 if needed

**3. No Energy Balance Fit**
- Probability: 20%
- Mitigation: Stochastic buffers may alter scaling (like C192)
- Impact: Fit empirical model instead of theoretical

**4. Mechanism Difference Absent**
- Probability: 30%
- Mitigation: Both mechanisms may be equally vulnerable to energy pressure
- Impact: Focus on E_CONSUME and N effects

**Overall Risk:** LOW-MEDIUM (likely to find collapse, but scaling may be complex)

---

## DECISION CRITERIA

**Execute C194 if:**
- ✅ C193 complete and published (DONE)
- ✅ Design reviewed and validated (THIS DOCUMENT)
- ✅ Resources available (CPU, time, storage)

**Defer C194 if:**
- ❌ Critical bug discovered in C193
- ❌ User requests different priority
- ❌ Need to integrate C193 into papers first

**Current Status:** READY TO EXECUTE (pending autonomous decision)

---

## NEXT STEPS

**Immediate:**
1. Implement c194_energy_consumption.py
2. Extend C193 code with death mechanics (consume_energy, remove_dead)
3. Validate: E_CONSUME=0.0 should replicate C193
4. Execute 3,600 experiments (~6 minutes)

**Analysis:**
5. Fit collapse probability curves (sigmoid per condition)
6. Estimate f_critical(E_CONSUME, N)
7. Validate energy balance model
8. Compare mechanisms (Deterministic vs Flat)
9. Generate 5 publication figures @ 300 DPI

**Documentation:**
10. Create c194_energy_threshold_finding.md
11. Document f_critical(E_CONSUME) scaling law
12. Theoretical interpretation
13. Integration into Papers 2 and 4

**Publication:**
14. Finalize Paper 2 (Methods, Discussion with C193/C194)
15. Draft Paper 4 (complete robustness characterization)

---

## ACKNOWLEDGMENTS

**Design:** Claude (AI Research Assistant)
**Principal Investigator:** Aldrin Payopay
**Framework:** Nested Resonance Memory (NRM)
**Research Arc:** C187 → C189 → C190 → C191 → C192 → C193 → C194
**License:** GPL-3.0

---

**End of Design Document**

**Status:** Design complete, ready for implementation
**Next:** c194_energy_consumption.py implementation
**Archive:** `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/c194_energy_consumption_design.md`
**Date:** 2025-11-08
