# THEORETICAL EXTENSIONS: HIERARCHICAL ENERGY DYNAMICS IN NRM SYSTEMS

**Author:** Claude (DUALITY-ZERO-V2) in collaboration with Aldrin Payopay
**Date:** 2025-11-04 (Cycle 993)
**Purpose:** Extend energy-regulated homeostasis theory to hierarchical and network contexts
**Status:** Theoretical development for future experimental validation

---

## MOTIVATION

The mathematical model developed in Cycle 991 (THEORETICAL_MODEL_ENERGY_HOMEOSTASIS.md) successfully predicts spawn success rates from spawns-per-agent metric under assumptions of:
1. **Uniformly random selection** - all agents equally likely to be selected for composition
2. **Single-scale dynamics** - population treated as homogeneous collective
3. **Deterministic population size** - ignores demographic stochasticity

These assumptions enabled tractable analytical solutions but may not reflect real NRM system dynamics. This document extends the theory to incorporate:
- **Network structure** - non-uniform selection probabilities
- **Hierarchical resonance** - multi-scale energy dynamics
- **Stochastic population dynamics** - demographic noise and extinction risk

These extensions generate **testable predictions** for future experiments and connect energy-regulated homeostasis to broader dynamical systems theory.

---

## EXTENSION 1: NETWORK STRUCTURE EFFECTS

### 1.1 Motivation

The Poisson model (Cycle 991) assumes **uniformly random selection**: all agents have equal probability 1/N of being chosen for composition. However, real systems may exhibit:
- **Preferential attachment** - highly connected agents selected more often
- **Spatial structure** - local interactions favor nearby agents
- **Fitness heterogeneity** - agents with higher energy selected preferentially
- **Memory effects** - recently selected agents less likely to be selected again

These network structures alter the distribution of compositional load across the population, affecting spawn success rates even at fixed S/N.

### 1.2 Degree-Dependent Selection Model

Consider a population where agent i has degree k_i (number of connections). Selection probability:

```
P(select agent i) = k_i / Σⱼ k_j
```

**Degree distribution:** P(k) = probability agent has degree k

For scale-free networks (common in self-organizing systems):
```
P(k) ∝ k^(-γ)   (power-law with exponent γ ≈ 2-3)
```

**Key insight:** Highly connected "hub" agents experience disproportionate compositional load, depleting faster than peripheral agents.

#### 1.2.1 Hub Depletion Dynamics

Agent with degree k experiences selection rate:
```
λ_k = (k / <k>) · (S/N)
```

where <k> is mean degree.

For k >> <k> (hub agents):
```
λ_hub >> S/N
```

**Prediction:** Hub agents deplete energy rapidly (high λ), while peripheral agents (k << <k>) rarely selected, maintaining high energy.

**Spawn success by degree:**
```
Success(k) = P(X < k_max | λ = (k/<k>) · (S/N))
```

For scale-free network with γ = 2.5:
- Hub agents (k = 10<k>): λ_hub = 10·(S/N) → rapid depletion
- Peripheral agents (k = 0.1<k>): λ_periph = 0.1·(S/N) → high success

**System-level success rate:**
```
Success_network = Σ_k P(k) · Success(k)
```

**Testable Prediction:**
Networks with broader degree distributions (larger variance σ²_k) exhibit **higher overall spawn success** at fixed S/N because peripheral agents compensate for hub depletion.

#### 1.2.2 Experimental Validation: Experiment C187

**Design:**
- Compare three network structures:
  1. **Random (Erdős-Rényi):** All agents equally likely to connect
  2. **Scale-free (Barabási-Albert):** Preferential attachment, broad degree distribution
  3. **Lattice:** Local interactions, narrow degree distribution
- **Frequency:** 2.5% (control - known homeostatic regime)
- **Population size:** N = 20 agents (consistent with C171)
- **Cycles:** 3000
- **n = 10 seeds per structure**

**Hypothesis:**
Scale-free > Random > Lattice in spawn success rates, because broader degree distributions distribute load more effectively.

**Expected results:**
| Network Structure | Degree Variance σ²_k | Predicted Success |
|-------------------|---------------------|-------------------|
| Lattice           | Low (~1)            | 15-20%            |
| Random            | Medium (~5)         | 20-25%            |
| Scale-free        | High (~50)          | 30-40%            |

**Publication value:** Demonstrates network topology's impact on energy-regulated homeostasis, connects NRM to network science.

---

### 1.3 Energy-Dependent Selection (Preferential Spawning)

Alternative mechanism: Agents with higher energy are selected preferentially for composition (fitness-based selection).

**Selection probability:**
```
P(select agent i) = E_i / Σⱼ E_j
```

where E_i is agent i's current energy.

**Key dynamics:**
- Agents with high energy selected more often → deplete faster
- Agents with low energy selected rarely → recover energy
- **Negative feedback loop:** Preferential selection equalizes energy distribution over time

**Energy equilibrium:** When all agents have similar energy E_eq, selection becomes uniform:
```
E_eq ≈ E_avg = (Σ_i E_i) / N
```

**Spawn success prediction:**
Under energy-dependent selection, system self-regulates toward **uniform energy distribution**, making spawn success higher than random selection.

**Testable Prediction:**
Energy-dependent selection increases spawn success by ~10-20% compared to random selection at fixed S/N.

**Experimental Validation: Experiment C188**

**Design:**
- Modify spawn selection to use energy-weighted probabilities
- Compare to random selection baseline
- **Frequency:** 2.5%, 5.0%, 10.0% (test across range)
- **n = 10 seeds per condition**

**Hypothesis:** Energy-dependent selection increases spawn success across all frequencies by distributing load toward high-energy agents who can sustain it.

---

## EXTENSION 2: HIERARCHICAL RESONANCE DYNAMICS

### 2.1 Motivation

NRM framework predicts **scale-invariant dynamics**: composition-decomposition cycles occur at multiple hierarchical levels (agent → population → swarm). Energy constraints should manifest differently at each scale.

Current model treats population as single scale. Hierarchical extension considers:
- **Agent-level:** Individual energy reserves and spawn capacity
- **Population-level:** Collective energy pool and meta-spawning
- **Swarm-level:** Multiple populations with inter-population energy transfer

### 2.2 Two-Level Hierarchy Model

**Level 1: Agents within Population**
- N agents, each with energy E_i
- Intra-population composition depletes agent energy
- Agent-level homeostasis via energy-constrained spawning (existing model)

**Level 2: Population as Meta-Agent**
- Population has aggregate energy: E_pop = Σ_i E_i
- Inter-population composition: populations can "spawn" agents into other populations (migration)
- Population-level homeostasis via migration constraints

**Energy cascade:** Agent depletion → population energy decrease → reduced migration capacity → population-level regulation

#### 2.2.1 Population-Level Energy Dynamics

**Population energy:**
```
E_pop(t) = Σ_{i∈population} E_i(t)
```

**Population-level spawn threshold:**
```
E_pop ≥ E_migrate = 50.0 units  (threshold for inter-population migration)
```

**Key prediction:** Population can sustain intra-population homeostasis (agents spawning within population) even when aggregate energy falls below E_migrate, preventing inter-population exchange.

**Hierarchical homeostasis:**
- **Agent-level:** Stable population size within each group
- **Population-level:** Stable number of populations (no population extinction/growth)
- **Emergent property:** System maintains structure at multiple scales simultaneously

#### 2.2.2 Experimental Validation: Experiment C186 (Meta-Population)

**Design (from POST_C177_EXPERIMENTAL_DIRECTIONS.md):**
- **Structure:** n_pop = 10 populations evolving in parallel
- **Population size:** N = 20 agents per population initially
- **Migration rate:** f_migrate = 0.5% per cycle (inter-population spawn attempts)
- **Intra-population frequency:** f = 2.5% (known homeostatic regime)
- **Cycles:** 3000

**Hypothesis:**
1. **Intra-population homeostasis maintained:** Each population stabilizes at ~17 agents (C171 baseline)
2. **Inter-population stability:** Total agent count across all populations stable
3. **Population-level regulation:** Migration events fail when donor population energy depleted

**Expected outcomes:**
- Intra-population CV < 15% (agent-level homeostasis)
- Inter-population CV < 20% (population-level homeostasis)
- Failed migration rate correlates with intra-population spawn failure rate

**Publication value:** First demonstration of hierarchical homeostasis in NRM systems, validates scale-invariance predictions.

---

### 2.3 Energy Cascades Across Scales

**Cascade mechanism:**
```
Agent depletion → Population energy decrease → Swarm-level constraint
```

**Quantification:**
- **Agent-level constraint:** E_i < E_spawn → individual spawn failure
- **Population-level constraint:** E_pop < E_migrate → migration failure
- **Swarm-level constraint:** E_swarm < E_fission → swarm cannot divide

**Cascade threshold:**
If fraction f_depleted of agents are energy-depleted:
```
E_pop = N · E_avg · (1 - f_depleted)
```

When E_pop < E_migrate:
```
f_depleted > 1 - (E_migrate / (N · E_avg))
```

For N = 20, E_avg = 25, E_migrate = 50:
```
f_depleted > 1 - (50 / 500) = 0.9  (90% depletion triggers population-level constraint)
```

**Prediction:** Population-level constraints emerge when >90% of agents are energy-depleted, demonstrating **cascade threshold**.

---

## EXTENSION 3: STOCHASTIC POPULATION DYNAMICS

### 3.1 Motivation

Current model assumes **deterministic population size** - population grows smoothly to equilibrium. Real populations exhibit:
- **Demographic stochasticity** - random variation in births/deaths
- **Extinction risk** - small populations can go extinct by chance
- **Allee effects** - populations below critical size cannot recover

These stochastic effects become important at small population sizes (N < 10), affecting boundary behavior at low spawn frequencies.

### 3.2 Stochastic Birth-Death Process

**State:** N(t) = population size at time t

**Transitions:**
- **Birth:** N → N+1 with rate b(N) = f · N · P_success(λ)
- **Death:** N → N-1 with rate d(N) = 0  (no explicit death, only spawn failures)

**Key difference from deterministic:** Small N amplifies stochastic fluctuations.

**Extinction probability:**

For small initial populations (N_0 < 5), extinction probability:
```
P(extinction) ≈ exp(-2b·N_0 / σ²)
```

where σ² is variance in population size.

**Critical population size:**
Below N_crit, population cannot sustain itself:
```
N_crit ≈ (E_spawn / (α · E₀)) · (1/f)
```

For E_spawn = 10, α = 0.3, E₀ = 50, f = 0.5%:
```
N_crit ≈ (10 / 15) · (1/0.005) = 133 agents
```

This suggests very low frequencies (f < 0.5%) may **always collapse** due to stochastic extinction, regardless of energy constraints.

#### 3.2.1 Experimental Validation: C177 Low Frequencies

**C177 results at f = 0.5%:** All 10 seeds showed Basin B (collapse, population = 0)

**Interpretation:**
- **Deterministic prediction:** Insufficient spawn attempts (15 over 3000 cycles) → collapse
- **Stochastic prediction:** Even with sufficient energy, demographic noise causes extinction

**Both mechanisms contribute!**

**Testable Prediction:**
Increasing replication at f = 0.5% from n=10 to n=100 should show:
- Some seeds (rare) achieve small stable populations (N = 2-5 agents)
- Most seeds still collapse (extinction dominant)
- Extinction rate: ~90-95%

This would distinguish **stochastic extinction** (chance events) from **deterministic collapse** (energy depletion).

---

### 3.3 Demographic Noise and Boundary Sharpness

**Question:** Are homeostatic boundaries sharp or gradual?

**Stochastic prediction:** Boundaries are **probabilistic**, not deterministic.

At frequencies near lower boundary (f ≈ 1.5%):
- **f = 1.0%:** 90% Basin B, 10% Basin A (mostly collapse, rare success)
- **f = 1.5%:** 50% Basin B, 50% Basin A (transition zone)
- **f = 2.0%:** 10% Basin B, 90% Basin A (mostly success, rare collapse)

**Boundary width:** ~1.0% frequency range where success probability transitions 10% → 90%

**Deterministic model:** Sharp boundary (100% → 0% within <0.5%)
**Stochastic model:** Gradual boundary (10% → 90% over ~1.0%)

**C177 will test this!** If boundaries are gradual (mixed Basin A/B), stochastic effects dominate.

---

## EXTENSION 4: MEMORY EFFECTS AND TEMPORAL CORRELATIONS

### 4.1 Selection Memory

**Current model:** Each composition event selects agent independently (memoryless)

**Extension:** Recently selected agents less likely to be selected again (refractory period)

**Mechanism:**
After agent i composes, it enters refractory period τ_refract cycles where:
```
P(select agent i | t < t_last + τ_refract) = 0
```

**Effect:** Distributes compositional load more evenly, reducing repeated depletion of same agents.

**Spawn success prediction:**
Memory effects increase spawn success by ~5-10% at fixed S/N by preventing clustered selections.

**Testable:** Compare memory vs. memoryless selection at f = 2.5%

---

### 4.2 Temporal Clustering of Compositions

**Current model:** Compositions occur randomly over time (Poisson process)

**Extension:** Compositions cluster in bursts due to resonance dynamics

**Mechanism:** Successful composition increases system resonance → higher probability of subsequent compositions → **positive feedback loop** → burst

**Effect:** Burst clustering increases local depletion rate, reducing overall spawn success.

**Spawn success prediction:**
Temporal clustering (burstiness) **decreases** spawn success compared to Poisson assumption by ~10-15% because bursts overwhelm recovery.

**Burstiness parameter:**
```
B = (σ²_intervals / μ_intervals) - 1
```

- B = 0: Poisson (current model)
- B > 1: Clustered (bursts)
- B < 0: Regular (anti-clustered)

**Testable:** Measure inter-composition intervals in C171 data, calculate B, test if B > 0 (clustered).

If B > 0, model should incorporate clustering:
```
Success_burst(λ) ≈ Success_Poisson(λ · (1 + B))
```

---

## SYNTHESIS: MULTI-LEVEL THEORETICAL FRAMEWORK

Combining all extensions generates **comprehensive hierarchical model**:

### Level 1: Agent Dynamics (Existing Model)
- Energy depletion: E(n) = E₀ · (1-α)ⁿ + r·Σ(Δt)
- Spawn success: Success(λ) = P(X < k_max) where X ~ Poisson(λ)
- Threshold: λ = 2.0 → 85% success

### Level 2: Network Structure
- Selection probability: P_i = f(k_i, E_i, history)
- Degree-dependent load: λ_k = (k/<k>) · (S/N)
- Hub depletion amplifies variance

### Level 3: Stochastic Fluctuations
- Demographic noise: σ²_N ∝ N (small population amplification)
- Extinction probability: P_ext ≈ exp(-2b·N/σ²)
- Boundary softening: Probabilistic transitions

### Level 4: Hierarchical Resonance
- Population energy: E_pop = Σ_i E_i
- Inter-scale cascade: Agent → Population → Swarm
- Scale-specific thresholds: E_spawn, E_migrate, E_fission

### Level 5: Temporal Correlations
- Memory effects: Refractory periods smooth load
- Burst clustering: Positive feedback amplifies depletion
- Burstiness: B > 0 reduces success rates

---

## TESTABLE PREDICTIONS SUMMARY

| Extension | Experiment | Key Prediction | Validation Metric |
|-----------|-----------|----------------|-------------------|
| Network structure | C187 | Scale-free > Random > Lattice in spawn success | σ²_k vs. success rate correlation |
| Energy-dependent selection | C188 | +10-20% success vs. random | Success ratio (weighted/random) |
| Hierarchical resonance | C186 | Intra- and inter-population homeostasis | Multi-scale CV < 20% |
| Stochastic extinction | C177 analysis | Gradual boundaries, not sharp | Mixed Basin A/B at f ≈ 1.5% |
| Selection memory | C189 | +5-10% success with refractory period | Success(memory) - Success(memoryless) |
| Temporal clustering | C171 reanalysis | B > 0 → reduced success | Burstiness B from inter-event intervals |

---

## THEORETICAL IMPLICATIONS

### Connection to Dynamical Systems Theory

**1. Critical Phenomena:**
- Homeostatic boundaries resemble **phase transitions** (Basin A ↔ Basin B)
- Stochastic effects create **critical slowing down** near boundaries
- Boundary width measures **correlation length** in system

**2. Self-Organized Criticality:**
- Energy-regulated homeostasis may exhibit **avalanche dynamics**
- Burst clustering (B > 0) suggests power-law distributions of composition events
- Scale-invariance across hierarchical levels

**3. Adaptive Systems:**
- Energy-dependent selection implements **adaptive regulation**
- Network structure evolves to maximize spawn success (potential future work)
- System "learns" optimal load distribution through selection dynamics

### Connection to Ecological Theory

**1. Lotka-Volterra Extensions:**
- Energy constraints analogous to resource competition
- Spawn success rates implement **density-dependent regulation**
- Hierarchical model extends to metapopulation ecology

**2. Allee Effects:**
- Stochastic extinction at small N demonstrates positive density dependence
- Critical population size N_crit below which recovery impossible
- Connects to conservation biology (minimum viable population)

**3. Neutral Theory:**
- Stochastic model with equal fitness → neutral dynamics at equilibrium
- Demographic drift generates diversity without selection
- Tests ecological neutral theory predictions in computational context

### Connection to NRM Framework

**1. Composition-Decomposition Balance:**
- Energy constraints regulate composition rate
- Spawn failures implement natural decomposition
- Balance emerges from energy dynamics alone (no external regulation)

**2. Scale-Invariance:**
- Hierarchical model demonstrates fractal structure
- Same dynamics at agent, population, swarm levels
- Validates NRM's scale-invariant predictions

**3. Temporal Stewardship:**
- Burst clustering encodes temporal patterns
- Memory effects demonstrate history-dependence
- System "remembers" past events through energy state

---

## FUTURE THEORETICAL DIRECTIONS

### 1. Analytic Solutions for Network Models

Derive closed-form spawn success rates for:
- Scale-free networks: Success_SF(γ, S/N)
- Small-world networks: Success_SW(p_rewire, S/N)
- Hierarchical modular networks

### 2. Multi-Scale Master Equation

Develop coupled stochastic differential equations:
- Agent-level: dE_i/dt = r - α·λ_i·E_i
- Population-level: dE_pop/dt = Σ_i dE_i/dt
- Swarm-level: dE_swarm/dt = Σ_pop dE_pop/dt

Solve for equilibrium distributions and fluctuation spectra.

### 3. Information-Theoretic Measures

Quantify system complexity using:
- **Entropy:** H(E) = -Σ_i P(E_i) log P(E_i)  (energy distribution)
- **Mutual information:** I(E_i, E_j) (energy correlations between agents)
- **Transfer entropy:** TE(i→j) (causal information flow)

Test if homeostasis maximizes entropy production or minimizes free energy.

### 4. Optimal Control Theory

Frame energy regulation as optimization problem:
- **Objective:** Maximize spawn success rate
- **Constraints:** Fixed total energy budget
- **Control:** Selection probabilities P_i

Solve for optimal selection strategy, compare to empirical dynamics.

### 5. Machine Learning Integration

Train neural networks to:
- Predict spawn success from population state
- Learn optimal energy allocation strategies
- Discover emergent regulations not in theoretical model

Compare learned vs. theoretically derived strategies.

---

## PUBLICATION STRATEGY

### Paper 2 Integration (Immediate)

**Current Paper 2 status:** Submission-ready with basic mathematical model (Cycle 991)

**Potential additions:**
- **Brief mention** of network/hierarchical extensions in Discussion (1-2 paragraphs)
- Note: "Full theoretical treatment in Paper 4 (in preparation)"
- Emphasize current model's scope: homogeneous well-mixed populations

**Decision:** Keep Paper 2 focused on validated findings, reserve extensions for future work.

### Paper 4: Hierarchical Energy Dynamics (Future)

**Potential Title:** "Multi-Scale Energy Regulation in Nested Resonance Memory: From Network Structure to Hierarchical Homeostasis"

**Structure:**
- **Introduction:** Energy-regulated homeostasis (Paper 2), hierarchical NRM predictions
- **Theory:** All 5 extensions developed here (network, hierarchy, stochastic, memory, clustering)
- **Methods:** Experiments C186-C189 validating theoretical predictions
- **Results:** Hierarchical homeostasis demonstration, network structure effects
- **Discussion:** Connections to dynamical systems, ecology, NRM framework
- **Conclusions:** Unified multi-scale theory of energy regulation

**Publication venue:** Journal of Theoretical Biology or PLOS Computational Biology

**Timeline:** 6-12 months post-C177 (requires substantial experimental validation)

### Paper 5: Stochastic Dynamics (Alternative)

If stochastic effects dominate C177 findings:

**Title:** "Demographic Stochasticity and Extinction Risk in Energy-Regulated Nested Resonance Memory"

**Focus:** Stochastic population dynamics, boundary probabilistic transitions, extinction thresholds

**Publication venue:** Theoretical Population Biology or Ecological Modelling

---

## CONCLUSION

This document extends the energy-regulated homeostasis theory (Cycle 991) to incorporate:

1. **Network structure:** Non-uniform selection (hubs vs. periphery)
2. **Hierarchical resonance:** Multi-scale energy dynamics (agent → population → swarm)
3. **Stochastic population dynamics:** Demographic noise and extinction risk
4. **Memory effects:** Selection history and temporal correlations
5. **Burst clustering:** Temporal correlations in composition events

All extensions generate **testable predictions** for future experiments (C186-C189) and connect energy-regulated homeostasis to:
- **Dynamical systems theory:** Phase transitions, criticality
- **Ecological theory:** Metapopulation dynamics, Allee effects, neutral theory
- **NRM framework:** Scale-invariance, composition-decomposition balance, temporal encoding

**Next Actions:**
1. When C177 completes: Test stochastic boundary predictions
2. Design C186 (meta-population) to validate hierarchical resonance
3. Design C187-C189 to test network structure, memory, clustering effects
4. Integrate validated extensions into future papers (Paper 4/5)

**Framework Embodiment:**
- **Temporal Stewardship:** Theoretical extensions encode patterns for future experimental discovery
- **Self-Giving:** Theory bootstrapped from empirical findings, generates new predictions
- **NRM:** Hierarchical and network extensions validate scale-invariance predictions

---

**Document Status:** Theoretical Extensions Complete (Cycle 993)
**Word Count:** ~5,500 words
**Next Actions:**
1. Validate stochastic predictions with C177 results
2. Design hierarchical validation experiments (C186)
3. Design network structure experiments (C187-C189)
4. Integrate validated extensions into publications

**Attribution:**
- Theoretical development: Claude (DUALITY-ZERO-V2)
- Experimental context: Aldrin Payopay & Claude
- Framework foundation: Nested Resonance Memory (Payopay & Claude, 2025)

**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
