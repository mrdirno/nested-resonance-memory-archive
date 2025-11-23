# C192 EXPERIMENTAL DESIGN: TRUE COLLAPSE BOUNDARY LOCATION

**Campaign:** C192 (True Boundary Search)
**Research Arc:** C187 → C189 → C190 → C191 → **C192**
**Status:** 📋 DESIGN PHASE
**Date:** 2025-11-08
**Author:** Claude (AI Research Assistant)
**Principal Investigator:** Aldrin Payopay

---

## RESEARCH CONTEXT

### From C191: Boundary is Below 0.3%

**Revolutionary Null Finding (2025-11-08):**
- 900 experiments: ZERO collapses
- Tested f=0.3% to 2.0%: 100% survival
- Collapse boundary is BELOW 0.3% (or non-existent)

**Energy Balance Theory:**
```
f_critical ≈ RECHARGE_RATE / E_SPAWN_COST
           ≈ 0.5 / 10.0
           ≈ 0.05 (5%)
```

**Implication:** Actual boundary likely in range f ∈ [0.05%, 0.30%]

### Research Arc Summary

**C189:** α = Predictability (Deterministic SD=0, Flat SD=3-8)
**C190:** Variance detrimental (400 experiments, all 4 hypotheses falsified)
**C191:** Variance not fragile (900 experiments, zero collapses)
**C192:** Locate true boundary (where does collapse actually occur?)

---

## RESEARCH QUESTION

**At what frequency does the Basin A/B boundary actually exist?**

**Sub-Questions:**
1. What is f_critical for each mechanism?
2. Does variance affect f_critical? (Flat vs Deterministic)
3. Is the transition sharp (cliff) or gradual (slope)?
4. Does energy balance theory predict f_critical accurately?

---

## HYPOTHESES

### H1: Collapse Boundary Exists Near Energy Balance Critical Point

**Prediction:**
- f_critical ≈ 0.05% (5% → 0.05 expressed as percentage)
- Based on: RECHARGE_RATE / E_SPAWN_COST = 0.5 / 10.0 = 0.05

**Mechanism:**
- Below f_critical: Energy drains faster than recharge → starvation
- Above f_critical: Energy recharges faster than depletion → viability

**Test:** Measure collapse rate vs frequency, identify inflection point

### H2: Deterministic Has Lower f_critical (Most Robust)

**Prediction:**
- f_critical(Deterministic) < f_critical(Hybrid) < f_critical(Flat)
- Deterministic survives at lowest frequencies

**Mechanism:**
- Deterministic: Perfect timing → optimal energy use
- Flat: Random jitter → occasional energy waste → higher f needed

**Test:** Compare f_critical across mechanisms

### H3: Transition is Gradual (Not Cliff)

**Prediction:**
- Collapse rate increases smoothly as f → 0
- NOT: Sharp 0% → 100% transition

**Mechanism:**
- Stochastic energy dynamics create probabilistic boundary
- Some runs lucky (high energy states) → survive
- Some runs unlucky (low energy states) → collapse

**Test:** Measure collapse rate at each frequency, check for smooth gradient

---

## EXPERIMENTAL DESIGN

### Parameters

```yaml
Spawn Mechanisms: 3
  - deterministic (c=1.0): Interval-based, zero dropout
  - hybrid_mid (c=0.50): Interval-based, 50% dropout
  - flat (c=0.0): Probabilistic per-cycle

Frequencies (% per cycle): 10
  - 0.05% (interval=2000) ← predicted f_critical
  - 0.08% (interval=1250)
  - 0.10% (interval=1000)
  - 0.12% (interval=833)
  - 0.15% (interval=666)
  - 0.18% (interval=555)
  - 0.20% (interval=500)
  - 0.23% (interval=434)
  - 0.25% (interval=400)
  - 0.30% (interval=333) ← C191 baseline (100% survival)

Seeds: 100 per condition (high replication for collapse probability)

Fixed Parameters:
  n_pop: 1 (single population isolates mechanism)
  N_initial: 20 agents
  cycles: 5000 (longer to allow boundary effects)
  BASIN_A_THRESHOLD: 2.5 (pop > 2.5 → Basin A)

Energy Model (matching C189/C190/C191):
  E_INITIAL: 50.0
  E_SPAWN_THRESHOLD: 20.0
  E_SPAWN_COST: 10.0
  RECHARGE_RATE: 0.5
  CHILD_ENERGY_FRACTION: 0.5
  # NO per-cycle consumption

Total Experiments:
  3 mechanisms × 10 frequencies × 100 seeds = 3,000 experiments
```

### Rationale for Parameters

**Frequency Range:**
- Lower bound: 0.05% (predicted f_critical)
- Upper bound: 0.30% (C191 showed 100% survival)
- Span: 6× range (0.05% to 0.30%)
- Resolution: 10 points (fine-grained gradient)

**High Replication (100 seeds):**
- Can detect collapse rates ≥ 1% with 95% confidence
- Smooth collapse probability curves
- Robust to sampling variation

**Extended Cycles (5000 vs 3000):**
- Allows slower dynamics to manifest
- Ensures equilibrium reached
- More conservative collapse detection

**Mechanisms:**
- Deterministic: Baseline (most efficient)
- Hybrid Mid: Intermediate variance
- Flat: Maximum variance

---

## OUTCOME MEASURES

### Primary: Collapse Rate

**Metric:** % experiments ending in Basin B (pop ≤ 2.5)

**Expected Pattern:**
```
Collapse Rate (%)
100 │
 90 │
 80 │              ╱─────  Flat (highest f_critical)
 70 │            ╱
 60 │          ╱
 50 │        ╱        ╱─────  Hybrid Mid
 40 │      ╱        ╱
 30 │    ╱        ╱
 20 │  ╱        ╱      ╱─────  Deterministic (lowest f_critical)
 10 │╱        ╱      ╱
  0 ├────────────────────────────────────────
    0.05   0.10   0.15   0.20   0.25   0.30
              Frequency (% per cycle)

KEY: Gradual transition (sigmoid curves)
     Deterministic most robust (leftmost curve)
```

### Secondary: Mean Population (Basin A Only)

**Metric:** Mean final population among survivors

**Expected Pattern:**
- Higher f → higher mean population (more spawns)
- Deterministic > Flat > Hybrid (replicating C191)
- SD: Deterministic=0, Flat=highest (replicating C189)

### Tertiary: Collapse Cycle

**Metric:** Cycle number when collapse occurred (if applicable)

**Expected Pattern:**
- Lower f → earlier collapse (faster energy depletion)
- High variance across runs (stochastic dynamics)

---

## STATISTICAL ANALYSIS PLAN

### 1. Collapse Rate Curves

**Test:** Logistic regression
```python
logit(P(collapse)) = β₀ + β₁·f + β₂·mechanism + β₃·(f × mechanism)
```

**Estimates:**
- f_critical per mechanism (50% collapse point)
- Mechanism effect on f_critical
- Interaction: Does slope differ by mechanism?

### 2. Mechanism Comparison

**Test:** Chi-square at each frequency
```python
H₀: P(collapse | Deterministic) = P(collapse | Hybrid) = P(collapse | Flat)
```

**Expected:**
- Significant at low f (near boundary)
- Non-significant at high f (all survive)

### 3. Energy Balance Validation

**Test:** Compare observed f_critical to predicted (0.05%)
```python
H₀: f_critical = 0.05% (energy balance theory)
```

**Confidence Interval:** 95% CI around observed f_critical

### 4. Transition Sharpness

**Test:** Measure slope of sigmoid curve
```python
slope = max(dP/df)  # steepest point
```

**Interpretation:**
- High slope → cliff-like transition
- Low slope → gradual transition

---

## SUCCESS CRITERIA

**Experiment succeeds if:**

1. ✅ **Boundary Located:**
   - Collapse rate transitions from 0% to 100%
   - Clear inflection point identified
   - f_critical estimated for each mechanism

2. ✅ **Hypotheses Testable:**
   - H1: f_critical near 0.05% (within 2×)
   - H2: Deterministic < Hybrid < Flat f_critical
   - H3: Transition is gradual (smooth sigmoid)

3. ✅ **Reproducibility:**
   - Individual results tracked
   - Seeds documented
   - Statistical tests reported

**Experiment fails if:**

- ❌ Zero collapses at ALL frequencies (boundary below 0.05%)
- ❌ 100% collapses at ALL frequencies (boundary above 0.30%)
- ❌ No clear transition (flat collapse rate)

---

## PREDICTED OUTCOMES

### Most Likely Scenario

**Collapse Boundary Exists in Range [0.08%, 0.20%]**

**Evidence:**
- C191: 100% survival at 0.30%
- Energy theory: f_critical ~ 0.05%
- Margin: 1.5-4× theory (stochastic buffer)

**Expected f_critical:**
- Deterministic: ~0.08-0.10% (closest to theory)
- Hybrid Mid: ~0.12-0.15% (dropout increases f_critical)
- Flat: ~0.15-0.20% (jitter requires higher f)

**Transition Shape:**
- Gradual sigmoid (not cliff)
- Width: ~0.05% (span from 10% to 90% collapse)

### Alternative Scenarios

**Scenario A: Boundary Below 0.05%**
- Observation: Zero collapses at all tested frequencies
- Implication: Energy balance theory underestimates robustness
- Next: Test f ∈ [0.01%, 0.05%] (extend lower bound)

**Scenario B: Boundary Above 0.30%**
- Observation: 100% collapses at all tested frequencies
- Implication: Extended cycles (5000) insufficient
- Next: Test with cycles=10,000 or N_initial=40

**Scenario C: No Boundary (System Always Viable)**
- Observation: Low collapse rates (<10%) at all frequencies
- Implication: N_initial=20 provides sufficient buffer
- Next: Test with N_initial=10 to induce boundary

---

## IMPLEMENTATION NOTES

### Code Structure

```python
# Energy model (CRITICAL: match C189/C190/C191)
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
RECHARGE_RATE = 0.5
CHILD_ENERGY_FRACTION = 0.5
# NO E_CONSUME (per-cycle consumption)

# Agent class
class Agent:
    def __init__(self, energy=E_INITIAL):
        self.energy = energy
        self.age = 0

    def increment_age(self):
        self.age += 1

# Population class
class Population:
    def recharge_energy(self):
        for agent in self.agents:
            agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def increment_ages(self):
        for agent in self.agents:
            agent.increment_age()

    def spawn_attempt(self) -> bool:
        if self.size() == 0:
            self.spawn_failures += 1
            return False

        parent = self.random.choice(self.agents)

        if parent.energy >= E_SPAWN_THRESHOLD:
            offspring_energy = E_INITIAL * CHILD_ENERGY_FRACTION
            offspring = Agent(energy=offspring_energy)
            self.agents.append(offspring)
            parent.energy -= E_SPAWN_COST  # NOT E_SPAWN_THRESHOLD
            self.spawn_count += 1
            return True
        else:
            self.spawn_failures += 1
            return False

# System step (CRITICAL: no consume_energy or remove_dead)
def step(self):
    # Track collapse
    if self.collapse_cycle is None and self.population.size() <= BASIN_A_THRESHOLD:
        self.collapse_cycle = self.cycle_count

    # Energy recovery
    self.population.recharge_energy()

    # Age increment
    self.population.increment_ages()

    # Intra-population spawning
    self._intra_spawning()

    # Record state
    self.population_history.append(self.population.size())
    self.energy_history.append(self.population.mean_energy())

    self.cycle_count += 1
```

### Validation Checklist

Before executing C192, verify:

- ✅ Energy model matches C189/C190/C191 (NO E_CONSUME)
- ✅ spawn_attempt uses E_SPAWN_COST (NOT E_SPAWN_THRESHOLD)
- ✅ step() has NO consume_energy() or remove_dead() calls
- ✅ Baseline replication: f=0.30% should show ~100% survival (matching C191)

---

## TIMELINE ESTIMATE

**Design:** 30 minutes (this document)
**Implementation:** 45 minutes (adapt C191 code)
**Execution:** 5 minutes (3,000 experiments @ ~100 exp/sec)
**Analysis:** 60 minutes (statistical tests, figures)
**Documentation:** 45 minutes (finding document)

**Total:** ~3 hours

**Expected Completion:** 2025-11-09 (tomorrow)

---

## PUBLICATION INTEGRATION

### Paper 2: "Hierarchical Spawn Advantage is Predictability"

**C192 Contribution:**
- Methods: Collapse boundary search methodology
- Results: f_critical measurements for each mechanism
- Discussion: Energy balance theory validation

**Integration Point:** After C191 robustness findings

### Paper 4: "Robustness of Self-Organizing NRM Systems"

**Dedicated Paper:**
- C190: Variance detrimental (performance)
- C191: Variance not fragile (survival, f ≥ 0.3%)
- C192: True boundary location (f_critical measurements)

**Contribution:**
- Complete robustness characterization
- Energy balance theory → empirical validation
- Practical bounds for NRM system design

---

## THEORETICAL IMPLICATIONS

### NRM Framework

**If H1 Validated (f_critical ~ 0.05%):**
- ✅ Energy balance theory predicts viability
- ✅ Simple physical model explains complex system
- ✅ Self-regulation emerges from energy constraints

**If H2 Validated (Deterministic most robust):**
- ✅ α (predictability) → survival advantage
- ✅ Hierarchical organization → robustness
- ✅ Stochastic variance → fragility (at boundary)

### Self-Giving Systems

**Bootstrap Complexity:**
- System self-defines viability (energy balance)
- No external tuning needed (f_critical emerges)
- Success = persistence (no oracle)

**C192 Test:**
- Does f_critical emerge from energy dynamics?
- Or does it require parameter tuning?

### Temporal Stewardship

**Encoded Patterns:**
1. α = Predictability (C189)
2. Variance detrimental to performance (C190)
3. Variance not fragile at f ≥ 0.3% (C191)
4. f_critical ~ 0.05% for N_initial=20 (C192, predicted)

**Future AI Training:**
- Learn energy balance → viability prediction
- Design systems with adequate f (safety margin)
- Optimize for predictability (deterministic spawn)

---

## RISK ASSESSMENT

### Potential Issues

**1. Boundary Below 0.05%**
- Probability: 20%
- Mitigation: Extend range to f ∈ [0.01%, 0.05%]
- Impact: Delays C192 completion

**2. Boundary Above 0.30%**
- Probability: 5%
- Mitigation: Increase cycles to 10,000 or N_initial to 40
- Impact: Requires redesign

**3. No Clear Boundary**
- Probability: 10%
- Mitigation: Reduce N_initial to 10 (induce boundary)
- Impact: Extends research arc

**4. High Variance (Flat collapse rates)**
- Probability: 15%
- Mitigation: Increase seeds to 200 per condition
- Impact: Execution time × 2

**Overall Risk:** LOW (boundary likely in tested range)

---

## DECISION CRITERIA

**Execute C192 if:**
- ✅ C191 complete and published (DONE)
- ✅ Design reviewed and validated (THIS DOCUMENT)
- ✅ Resources available (CPU, time, storage) (CHECK BEFORE RUN)

**Defer C192 if:**
- ❌ Paper 2 requires urgent attention
- ❌ Critical bug discovered in previous experiments
- ❌ User requests different priority

**Current Status:** READY TO EXECUTE (pending user confirmation or autonomous decision)

---

## NEXT STEPS

**Immediate:**
1. Implement c192_true_boundary.py (adapt from c191_collapse_boundary.py)
2. Validate energy model (match C189/C190/C191)
3. Execute 3,000 experiments (~5 minutes)

**Analysis:**
4. Statistical tests (logistic regression, chi-square)
5. Generate figures (collapse rate curves, f_critical comparison)
6. Document findings (c192_boundary_finding.md)

**Publication:**
7. Integrate into Paper 2 (Methods + Results)
8. Prepare Paper 4 outline (robustness paper)

---

## ACKNOWLEDGMENTS

**Design:** Claude (AI Research Assistant)
**Principal Investigator:** Aldrin Payopay
**Framework:** Nested Resonance Memory (NRM)
**Research Arc:** C187 → C189 → C190 → C191 → C192
**License:** GPL-3.0

---

## REFERENCES

**C189:** α = Predictability (Hierarchical advantage)
**C190:** Variance detrimental (4 hypotheses falsified)
**C191:** Variance not fragile (900 experiments, zero collapses)
**Energy Balance Theory:** f_critical = RECHARGE_RATE / E_SPAWN_COST

---

**End of Design Document**

**Status:** Design complete, ready for implementation
**Next:** c192_true_boundary.py implementation
**Archive:** `/Volumes/dual/DUALITY-ZERO-V2/code/experiments/c192_true_boundary_design.md`
**Date:** 2025-11-08
