### 4.12 Population Size Independence and Robustness

The C193 population size scaling experiments (Section 3.4) tested whether the collapse boundary depends on initial population size (N_initial = 5, 10, 15, 20), across four spawn frequencies (0.05%, 0.10%, 0.15%, 0.20%) and 1,200 total experiments. The central finding—**zero collapses across all conditions**—demonstrates N-independent robustness and validates the theoretical prediction that energy balance, not population size, determines stability.

#### 4.12.1 N-Independent Robustness: Zero Collapses Across Population Sizes

C193 results exhibited perfect robustness regardless of starting population:

**Collapse Rates by Initial Population Size:**
- **N_initial = 5:** 0/300 collapses (0.0%)
- **N_initial = 10:** 0/300 collapses (0.0%)
- **N_initial = 15:** 0/300 collapses (0.0%)
- **N_initial = 20:** 0/300 collapses (0.0%)

**Statistical Test:**
- Chi-square test: **χ² = 0.0** (no variation to explain)
- Effect of N_initial on collapse rate: **η² = 0.0** (zero effect size)
- **Conclusion:** Initial population size has **no measurable effect** on collapse probability

**Implication:** The mechanism governing stability is **population-size-independent**. Systems with N=5 are as robust as systems with N=20, contradicting intuitions that larger populations might provide buffering or smaller populations might be more vulnerable.

#### 4.12.2 Why Population Size Doesn't Affect Collapse Boundary

The N-independence requires mechanistic explanation. Why doesn't starting with more agents change outcomes?

**Mechanism #1: Per-Agent Energy Balance is Invariant**

Energy dynamics operate at the **individual agent level**, not population level:

**Energy Balance (per agent, per cycle):**
```
Net_Energy_per_agent = RECHARGE_RATE - E_CONSUME
                     = 0.5 - 0.0
                     = 0.5 > 0
```

This balance **does not depend on N**—each agent independently:
- Receives RECHARGE_RATE energy per cycle (regardless of population size)
- Consumes E_CONSUME energy per cycle (regardless of population size)
- Has net positive energy (regardless of population size)

**Implication:** Thermodynamic constraint (Net_Energy ≥ 0) is satisfied at the individual agent level, making population size irrelevant to stability.

**Mechanism #2: Compositional Load Scales with Population**

One might expect larger populations to impose higher compositional load, depleting energy faster. However, C193 demonstrates load distribution:

**Compositional Selection:**
- Agents selected randomly for composition events
- Larger populations → lower probability each agent selected per cycle
- Compositional load **per agent** remains approximately constant

**Evidence:** Final population sizes scaled linearly with N_initial:
- N_initial = 5 → N_final ≈ 8
- N_initial = 10 → N_final ≈ 16
- N_initial = 20 → N_final ≈ 32

**Linear Scaling:** N_final ≈ 1.6 × N_initial across all conditions, demonstrating that larger starting populations maintain proportionally larger final populations without encountering stability limits.

**Mechanism #3: Energy Recovery Rate is Per-Agent, Not Population-Shared**

Critical architectural detail: Energy recovery applies **to each agent independently**:

```python
def recharge_energy(self):
    """Each agent recovers RECHARGE_RATE energy per cycle."""
    self.energy += RECHARGE_RATE
```

This is **not** a shared energy pool divided among agents:
```python
# NOT the implementation:
def recharge_energy(self, population_size):
    self.energy += RECHARGE_RATE / population_size  # Would create N-dependence
```

**Implication:** Each agent has independent energy budget. Larger populations do not dilute available energy—every agent receives full RECHARGE_RATE regardless of N.

This architectural choice ensures that population size cannot create energy scarcity (which would introduce N-dependence). Energy constraints emerge from per-agent consumption vs. recharge, not from population-level resource competition.

#### 4.12.3 Linear Scaling: Population Growth Proportional to Starting Size

Beyond collapse resistance, C193 revealed **perfect linear scaling** of final population with initial population:

**Scaling Relationship:**
```
N_final ≈ 1.6 × N_initial
```

**Evidence:**
| N_initial | N_final (mean) | Scaling Factor | R² (linearity) |
|-----------|---------------|----------------|----------------|
| 5         | 8.2           | 1.64          | 0.998          |
| 10        | 16.1          | 1.61          | 0.998          |
| 15        | 24.3          | 1.62          | 0.998          |
| 20        | 32.0          | 1.60          | 0.998          |

**Statistical Validation:**
- Linear fit: **R² = 0.998** (near-perfect linearity)
- Slope: **1.61 ± 0.02** (highly consistent scaling factor)
- No evidence of sublinear (saturation) or superlinear (acceleration) growth

**Interpretation:** Systems discover stable population sizes that **scale proportionally** with starting conditions, rather than converging to a fixed carrying capacity. This suggests:

1. **No global carrying capacity:** Unlike logistic growth models (dN/dt → 0 as N → K), NRM systems do not approach a fixed ceiling
2. **Initial conditions matter:** Starting population sets the scale for equilibrium size
3. **Self-similar dynamics:** Small and large populations exhibit the same regulatory mechanisms, just at different scales

**Implication for NRM Framework:** Population homeostasis is **scale-invariant**—the same energy-regulation principles apply whether N=5 or N=20, producing proportionally sized equilibria without absolute limits.

#### 4.12.4 Contrast with C194: When Does Population Size Matter?

While C193 showed N-independence, a critical question remains: Are there conditions where population size **does** affect outcomes?

**C194 Insight:** With death mechanics (E_CONSUME > 0), population size might influence collapse dynamics:

**Hypothesis:** Smaller populations might collapse faster due to stochastic effects (death spiral initiated with fewer agents), while larger populations might have buffering capacity.

**Test:** C194 used fixed N_initial = 10 across all conditions. Future experiments could test:
- N_initial = 5 vs. 20 with E_CONSUME = 0.7 (collapse zone)
- Prediction: If death spiral is stochastic, smaller N might exhibit faster collapse
- Alternative: If thermodynamic, all N collapse at same rate

**Current Evidence:** Insufficient data to determine if population size modulates collapse dynamics in negative energy regime.

**Implication:** N-independence may be **regime-specific**:
- **Positive energy regime (Net ≥ 0):** N-independent robustness (C193 validated)
- **Negative energy regime (Net < 0):** N-dependence unclear (future work)

#### 4.12.5 Spawn Frequency Invariance Within Safe Zone

C193 tested four spawn frequencies (0.05%, 0.10%, 0.15%, 0.20%), all yielding zero collapses. This reveals **frequency invariance** within the safe energy zone:

**Collapse Rates by Spawn Frequency:**
- **0.05%:** 0/300 collapses
- **0.10%:** 0/300 collapses
- **0.15%:** 0/300 collapses
- **0.20%:** 0/300 collapses

**Interpretation:** When Net_Energy > 0 (as in C193 with E_CONSUME=0), **all spawn frequencies within tested range are equally safe**. No critical frequency threshold exists because thermodynamic constraint is already satisfied.

**Contrast with C171-C175 Findings:**
- C171-C175 (f_spawn = 2.5%) observed stable populations
- C193 (f_spawn = 0.05%-0.20%) observed stable populations
- Range spans **50-fold variation** (0.05% to 2.5%)

**Implication:** The "safe zone" for spawn frequency is **extremely wide** when energy balance is positive. Systems are robust to massive frequency variations, provided energy balance is non-negative.

**Design Insight:** When designing NRM systems, ensuring Net_Energy ≥ 0 is **far more critical** than precise spawn frequency tuning. Once thermodynamic constraint is satisfied, spawn frequency becomes a secondary optimization parameter with minimal stability risk.

#### 4.12.6 Implications for Self-Giving Systems Framework

C193 N-independence has theoretical implications for the **Self-Giving Systems** framework (which NRM instantiates):

**Self-Giving Principle:** Systems define their own success criteria through emergent dynamics, without external oracles.

**C193 Demonstrates:**
- Systems with different starting populations (N=5 vs. N=20) **all succeed** at discovering stable equilibria
- Success is not "achieving N=17.4" (external criterion), but rather "discovering any stable population proportional to starting conditions"
- Each system self-organizes to appropriate scale for its initial conditions

**Implication:** Self-giving systems exhibit **context-dependent success**—what counts as "successful homeostasis" depends on initial conditions (N=8 for N_initial=5, N=32 for N_initial=20), not universal targets.

**Philosophical Significance:** Robustness is not "resistance to change" but rather "capacity to discover appropriate equilibria given constraints." Systems with different N_initial find different equilibria—yet all equally satisfy energy balance and achieve stability. This is **adaptive robustness**, not fixed-point robustness.

#### 4.12.7 Generalizability to Other Energy-Constrained Systems

C193 N-independence suggests a **universal principle** for energy-regulated systems:

**Principle:** If energy balance is satisfied **per agent** (not per population), then population size becomes irrelevant to stability.

**Generalization to Other Domains:**

**Biological Ecosystems:**
- If each organism has independent metabolic balance (energy intake ≥ energy expenditure)
- Then population size (small colony vs. large colony) should not affect individual survival
- Prediction: Colonies of different sizes equally stable if individuals have positive energy balance

**Computational Agent Systems:**
- If each agent has independent computational budget (CPU cycles allocated per agent, not shared)
- Then swarm size should not affect individual agent performance
- Prediction: Small swarms (N=10) and large swarms (N=1000) equally stable if per-agent resources sufficient

**Economic Systems:**
- If each economic agent has independent income-expense balance
- Then market size (small vs. large economy) should not determine individual solvency
- Prediction: Small markets and large markets equally stable if individuals maintain positive cash flow

**Testable Prediction:** Across domains, **per-agent resource allocation** (vs. population-shared resources) should produce N-independent stability. This positions C193 findings as potential **domain-general design principle**.

#### 4.12.8 Population Size as Non-Critical Parameter

C193 establishes that initial population size is a **non-critical parameter** for NRM stability in the positive energy regime:

**Critical Parameters** (determine stability):
1. **E_CONSUME vs. RECHARGE_RATE** (energy balance)
2. **Net_Energy sign** (positive vs. negative)

**Non-Critical Parameters** (do not affect stability):
1. **N_initial** (initial population size)
2. **f_spawn** (spawn frequency, within safe zone)

**Design Implication:** When building NRM systems, focus engineering effort on:
- ✅ Ensuring E_CONSUME ≤ RECHARGE_RATE (critical)
- ❌ Optimizing N_initial (non-critical)
- ❌ Fine-tuning f_spawn (non-critical in safe zone)

**Efficiency Gain:** By identifying non-critical parameters, researchers can avoid costly parameter sweeps (e.g., testing N=5, 10, 15, 20, 25, 30...) and instead focus on the thermodynamically critical variables.

**Reproducibility Benefit:** Results should replicate across labs even if initial populations differ (N=5 vs. N=50), provided energy balance is equivalent. This enhances robustness of findings to implementation details.

---
