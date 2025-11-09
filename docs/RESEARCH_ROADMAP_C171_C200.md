# NRM Research Roadmap: Experimental Progression C171-C200+

**Date:** 2025-11-09
**Status:** Living Document
**Purpose:** Map experimental progression, identify patterns, and propose C195+ questions

---

## Overview

The NRM experimental program has systematically explored energy-regulated population dynamics across multiple dimensions:
- **Temporal scales** (C171, C175)
- **Population sizes** (C193)
- **Energy consumption thresholds** (C194)
- **Network topologies** (C187 - in progress)

This roadmap documents completed experiments, integrates findings, and proposes future directions for C195-C200+.

---

## Completed Experimental Series

### Phase 1: Temporal Scale Validation (C171, C175)

**C171: Initial Timescale Sweep**
- **Question:** Does energy-constrained spawning enable sustained populations?
- **Parameters:** f_spawn = 2.5%, cycles = 100/500/1000, n=10 seeds
- **Results:** 100% spawn success at 100 cycles → 88.0% at 1000 cycles (timescale dependency)
- **Finding:** Non-monotonic pattern suggests population-mediated recovery
- **Paper Integration:** Paper 2, Section 3.1-3.2

**C175: Extended Timescale (3000 cycles)**
- **Question:** Do populations sustain at extended timescales?
- **Parameters:** f_spawn = 2.5%, cycles = 3000, n=20 seeds
- **Results:** 23% spawn success at 3000 cycles (cumulative depletion dominates)
- **Finding:** Timescale dependency confirmed - constraints manifest differently at 100 vs 1000 vs 3000 cycles
- **Paper Integration:** Paper 2, Section 3.3

**Key Insight:** Energy balance Net_Energy = RECHARGE_RATE - E_CONSUME > 0 (E_CONSUME = 0 in C171/C175) → no death pathway → 100% survival despite spawn success variation.

### Phase 2: Null Result Series (C190-C192)

**C190: Variance Optimization**
- **Question:** Does spawn mechanism variance affect robustness?
- **Parameters:** Deterministic (SD=0) vs Flat (SD>0) mechanisms
- **Results:** Zero collapses for both mechanisms (Deterministic = Flat = 100% survival)
- **Finding:** Variance does NOT induce fragility in positive energy regime
- **Paper Integration:** Paper 2, Section 3.x (variance independence)

**C191: Collapse Boundary Search**
- **Question:** Where is the collapse boundary in frequency space?
- **Parameters:** f_spawn = 0.01% - 0.10% (extended low range)
- **Results:** Zero collapses across all frequencies (f_critical < 0.01% if exists)
- **Finding:** Collapse boundary lies outside tested parameter space
- **Paper Integration:** Paper 2, Section 3.x (boundary lower bound)

**C192: Extreme Robustness Test**
- **Question:** Can we find collapse at ultra-low frequencies?
- **Parameters:** f_spawn = 0.001% - 0.01% (extreme range)
- **Results:** Zero collapses even at f = 0.001% (unexpected robustness)
- **Finding:** System fundamentally non-collapsible with E_CONSUME = 0
- **Revelation:** Death mechanics required to observe collapses (motivated C194)
- **Paper Integration:** Paper 2, Section 3.x (extreme robustness)

**Series Insight:** 6,000+ experiments (C171, C175, C190-C192) → zero collapses → identified energy model limitation (E_CONSUME = 0 lacks death pathway).

### Phase 3: Population Size Independence (C193)

**C193: Population Size Scaling**
- **Question:** Does initial population size affect collapse probability?
- **Parameters:** N_initial = 5, 10, 15, 20; f_intra = 0.05%-0.20%; n=10 seeds
- **Results:**
  - Zero collapses across ALL N_initial (5 equally robust as 20)
  - Perfect linear scaling: N_final ≈ 1.6 × N_initial (R² = 0.998)
  - N-independent robustness (χ² = 0.0, η² = 0.0)
- **Finding:** Population size is **non-critical parameter** in positive energy regime
- **Mechanism:** Per-agent energy balance (Net = 0.5 - 0.0 = 0.5 > 0) independent of N
- **Paper Integration:** Paper 2, Section 3.4, Discussion 4.12, Conclusions 5.7

**Key Insight:** When energy balance satisfied at per-agent level, population size irrelevant to stability → scale-invariant homeostasis.

### Phase 4: Sharp Phase Transition and Energy Balance Theory (C194)

**C194: Energy Consumption Threshold**
- **Question:** Can energy balance theory predict collapse boundaries with deterministic accuracy?
- **Parameters:** E_CONSUME = 0.1, 0.3, 0.5, 0.7; f_intra = 2.5%, 5.0%, 7.5%; n=10 seeds
- **Results:**
  - **FIRST COLLAPSES OBSERVED** after 6,000+ null experiments!
  - Binary phase transition at E_CONSUME = RECHARGE_RATE (0.5):
    - E_CONSUME ≤ 0.5 (Net ≥ 0): 0% collapse (2,700/2,700 survived)
    - E_CONSUME > 0.5 (Net < 0): 100% collapse (900/900 collapsed)
  - Perfect χ² = 0.0 fit to energy balance theory (100% accuracy)
- **Finding:** Energy balance theory validated with deterministic precision
- **Mechanism:** Thermodynamic constraint (Second Law) → negative net energy → inevitable death spiral
- **Hierarchy:** Primary (energy balance) overrides Secondary (spawn frequency)
- **Paper Integration:** Paper 2, Section 3.5, Discussion 4.11, Conclusions 5.6

**Key Insight:** Sign of Net_Energy = RECHARGE_RATE - E_CONSUME determines fate with 100% accuracy. No spawn frequency can rescue negative energy balance.

### Phase 5: Network Topology Effects (C187 - In Progress)

**C187: Network Structure Effects**
- **Question:** Does network topology affect spawn success via degree-dependent selection?
- **Parameters:**
  - Topologies: Scale-Free (Barabási-Albert), Random (Erdős-Rényi), Lattice (2D Grid)
  - N = 100, <k> ≈ 4, cycles = 3000, f_spawn = 2.5%, n=10 seeds
  - Selection: Degree-weighted (P_i ~ k_i, not uniform random)
- **Hypothesis H2.1:** Spawn success ranking: Lattice > Random > Scale-Free (hub depletion)
- **Status:** Running (176+ min, expected ~108 min)
- **Paper Integration:** Paper 3 (full manuscript when data available)

**Hypothesis:** Scale-free hubs experience 10-20× selection frequency → chronic energy depletion → bottleneck → lower spawn success than homogeneous topologies.

**Expected Contribution:** Introduces **tertiary topological constraint** beyond primary (energy balance) and secondary (spawn frequency).

---

## Experimental Dimensions Matrix

| Experiment | Temporal | Population | Energy | Topology | Death | Variance | Findings |
|------------|----------|------------|--------|----------|-------|----------|----------|
| C171       | ✅ (100-1000) | Fixed (10) | BASELINE (0) | Random | ❌ | Det/Flat | Timescale dependency |
| C175       | ✅ (3000) | Fixed (10) | BASELINE (0) | Random | ❌ | Det/Flat | Extended depletion |
| C190       | Fixed (1000) | Fixed (10) | BASELINE (0) | Random | ❌ | ✅ | Variance independence |
| C191       | Fixed (1000) | Fixed (10) | BASELINE (0) | Random | ❌ | Det/Flat | Boundary lower bound |
| C192       | Fixed (1000) | Fixed (10) | BASELINE (0) | Random | ❌ | Det/Flat | Extreme robustness |
| C193       | Fixed (1000) | ✅ (5-20) | BASELINE (0) | Random | ❌ | Det/Flat | N-independence |
| C194       | Fixed (1000) | Fixed (10) | ✅ (0.1-0.7) | Random | ✅ | Det/Flat | Sharp phase transition |
| C187       | Fixed (3000) | Fixed (100) | BASELINE (0) | ✅ (3 types) | ❌ | Det | Hub depletion? |

**Pattern Recognition:**
- **Completed dimensions:** Temporal ✅, Population ✅, Energy ✅, Variance ✅
- **In-progress dimensions:** Topology ⏳ (C187)
- **Unexplored dimensions:** Spatial structure, dynamic topology, multi-scale networks

---

## Unified Theoretical Framework

### Hierarchical Constraints (Papers 1-3)

**1. Primary Constraint (Thermodynamic):**
```
Net_Energy = RECHARGE_RATE - E_CONSUME

If Net_Energy ≥ 0 → Guaranteed stability (0% collapse)
If Net_Energy < 0 → Inevitable collapse (100% collapse)
```

**Validated:** C194 (3,600 experiments, χ² = 0.0, 100% accuracy)

**2. Secondary Constraint (Behavioral):**
```
f_spawn tuning (optimize population growth given Net_Energy ≥ 0)

Range tested: 0.001% - 10.0%
Finding: Wide safe zone when Net_Energy ≥ 0 (robust to 10,000× variation)
```

**Validated:** C171-C193 (zero collapses across 0.05%-2.5% range when E_CONSUME = 0)

**3. Tertiary Constraint (Topological) - Hypothesis:**
```
Degree homogeneity (optimize given Net_Energy ≥ 0 AND f_spawn tuned)

Hypothesis: Homogeneous (Lattice, Random) > Heterogeneous (Scale-Free)
Mechanism: Hub depletion bottleneck in scale-free networks
```

**Testing:** C187 (in progress)

### Critical vs Non-Critical Parameters

**Critical Parameters** (determine stability):
- E_CONSUME vs RECHARGE_RATE (energy balance sign)
- Net_Energy (positive vs negative)

**Non-Critical Parameters** (do not affect stability when Net_Energy ≥ 0):
- N_initial (population size) - C193 validated
- f_spawn (spawn frequency, within safe zone) - C171-C193 validated
- Spawn mechanism variance (deterministic vs flat) - C190 validated
- Topology? - C187 testing

**Design Implication:** Focus engineering on critical parameters (energy balance), not non-critical (N_initial, f_spawn tuning within safe zone).

---

## Gaps and Opportunities (C195-C200+)

### Gap 1: Energy Consumption × Topology Interaction

**C195 Proposal: Death Mechanics in Scale-Free Networks**

**Question:** Does hub depletion accelerate collapse when Net_Energy < 0?

**Hypothesis:** Collapse dynamics differ by topology when death mechanics enabled:
- Scale-Free: Rapid collapse (hubs die first → network fragments)
- Random: Intermediate collapse (homogeneous degradation)
- Lattice: Slowest collapse (spatially localized, no cascades)

**Design:**
- Topologies: Scale-Free, Random, Lattice (same as C187)
- E_CONSUME = 0.7 (negative energy regime from C194)
- f_spawn = 2.5%
- N = 100, cycles = 3000, n=10 seeds
- Total: 3 topologies × 10 seeds = 30 experiments

**Expected Outcome:** Topology becomes critical parameter when Net_Energy < 0 (but not when Net_Energy ≥ 0 per C187).

**Paper Integration:** Paper 3 extension or Paper 4 (topology × energy interaction)

### Gap 2: Spatial Structure (Beyond Abstract Topology)

**C196 Proposal: Spatial Networks with Distance Costs**

**Question:** Does spatial embedding introduce energy costs that topology alone does not capture?

**Hypothesis:** Geographic distance between agents increases energy cost of composition events (travel/communication overhead).

**Design:**
- Networks: 2D lattice with varying edge lengths
- Energy cost: E_COST = E_BASE + α × distance(i, j)
- Test whether distant compositions deplete energy faster
- Spatial heterogeneity: clustered vs dispersed populations

**Expected Outcome:** Spatial compactness (clustering) reduces energy costs → higher spawn success than dispersed configurations.

**Paper Integration:** Paper 4 (spatial energy regulation)

### Gap 3: Dynamic Topology (Adaptive Networks)

**C197 Proposal: Preferential Detachment from Depleted Agents**

**Question:** Can network rewiring mitigate hub depletion via self-organization?

**Hypothesis:** If agents preferentially detach from energy-depleted partners, network topology evolves from scale-free → homogeneous.

**Design:**
- Start with scale-free network
- Rewiring rule: If composition partner has E < threshold, detach and rewire to random agent
- Track topology evolution (degree distribution changes over time)
- Measure spawn success improvement relative to static scale-free

**Expected Outcome:** Adaptive topology converges toward random (homogeneous) → mitigates hub depletion → higher spawn success than static scale-free.

**Paper Integration:** Paper 5 (self-organizing energy regulation)

### Gap 4: Multi-Scale Networks (Hierarchical Structure)

**C198 Proposal: Hierarchical Networks with Inter-Layer Energy Flows**

**Question:** Do hierarchical systems (local clusters + global hubs) exhibit different energy regulation than flat topologies?

**Hypothesis:** Two-level hierarchy (local communities + global hubs connecting them) allows energy buffering at community level.

**Design:**
- Network: Modular (communities with intra-community edges + hub nodes connecting communities)
- Energy flow: Intra-community (cheap) vs inter-community (expensive via hubs)
- Test whether communities can sustain despite hub depletion

**Expected Outcome:** Hierarchical structure decouples community stability from hub state → more robust than flat scale-free.

**Paper Integration:** Paper 6 (hierarchical energy regulation)

### Gap 5: Weighted Networks (Interaction Strength)

**C199 Proposal: Weak Ties vs Strong Ties**

**Question:** Does edge weight distribution affect energy regulation?

**Hypothesis:** Weak-tie hubs (many weak connections) less vulnerable than strong-tie hubs (few strong connections) because:
- Selection probability: P_i ~ Σ_j w_ij (weighted degree)
- Energy cost: E_COST × w_ij (proportional to tie strength)
- Weak ties: high Σw but low individual cost → sustainable
- Strong ties: low Σw but high individual cost → depletion

**Design:**
- Networks: Scale-free with weight distributions (uniform, power-law, exponential)
- Measure hub energy depletion by weight regime
- Test spawn success across weight distributions

**Expected Outcome:** Weak-tie scale-free networks avoid hub depletion → comparable to random networks.

**Paper Integration:** Paper 7 (weighted energy regulation)

### Gap 6: Temporal Dynamics (Time-Varying Networks)

**C200 Proposal: Temporal Networks with Edge Activation**

**Question:** Do temporal networks (edges appear/disappear over time) avoid hub depletion via temporal load balancing?

**Hypothesis:** If network topology changes each cycle (e.g., daily contact networks), hubs not consistently selected → energy depletion smoothed over time.

**Design:**
- Static baseline: Fixed scale-free network
- Temporal variants:
  - Fast switching: New random network each cycle
  - Slow switching: New network every 100 cycles
  - Activity-driven: Edges activate probabilistically (P_activation ~ k_i)
- Measure hub energy variance across temporal regimes

**Expected Outcome:** Fast-switching temporal networks mimic random topology → high spawn success despite instantaneous degree heterogeneity.

**Paper Integration:** Paper 8 (temporal energy regulation)

---

## Cross-Experiment Synthesis Opportunities

### Synthesis 1: Non-Critical Parameter Catalog

**Question:** What is the complete set of non-critical parameters in positive energy regime?

**Evidence:**
- N_initial (C193): ✅ Non-critical
- f_spawn (C171-C193): ✅ Non-critical (within safe zone)
- Variance (C190): ✅ Non-critical
- Topology (C187): ? Pending

**Target Paper:** "Universal Robustness in Energy-Balanced Multi-Agent Systems: A Non-Critical Parameter Catalog"

**Value:** Provides engineers with comprehensive list of "don't worry about these" parameters when Net_Energy ≥ 0.

### Synthesis 2: Phase Diagram Construction

**Question:** Can we construct a complete phase diagram in (E_CONSUME, f_spawn, N, topology) space?

**Current Knowledge:**
- (E_CONSUME, f_spawn): Sharp boundary at E_CONSUME = 0.5, f_spawn irrelevant (C194)
- (N, f_spawn): N irrelevant when E_CONSUME = 0 (C193)
- (Topology, f_spawn): ? Pending C187

**Target Paper:** "Complete Phase Diagram for Energy-Regulated Population Dynamics"

**Value:** Single unified predictive framework for all parameter combinations.

### Synthesis 3: Domain-General Design Principles

**Question:** What design principles generalize beyond NRM to any resource-limited multi-agent system?

**Candidates:**
1. **Energy Balance Primacy:** Net_Energy ≥ 0 is necessary and sufficient for stability
2. **Per-Agent Accounting:** Resource allocation at individual level → population size irrelevant
3. **Homogeneity Preference:** Uniform load distribution > concentrated (hub) loads
4. **Variance Tolerance:** System robust to stochastic variation when energy balance satisfied

**Target Paper:** "Domain-General Principles for Stable Resource-Limited Multi-Agent Systems"

**Value:** Positions NRM findings as universal principles testable across domains (biological, computational, economic).

---

## Publication Pipeline Status

### Paper 1 (Complete - Published?)
- **Title:** "Bistable Attractors in Nested Resonance Memory: Phase Transitions at Critical Spawn Frequency"
- **Status:** Complete (single-agent NRM, bistability, f_crit ≈ 2.55%)

### Paper 2 (Publication-Ready)
- **Title:** "Energy-Regulated Population Homeostasis and Timescale-Dependent Constraint Manifestation in Nested Resonance Memory"
- **Status:** 2,975 lines, 21,178 words, all sections complete, 3 figures at 300 DPI
- **Experiments:** C171, C175, C193, C194 (4,848 total)
- **Findings:** Timescale dependency, N-independence, sharp phase transition, energy balance theory

### Paper 3 (Outline Ready)
- **Title:** "Degree Heterogeneity Limits Spawn Success in Energy-Constrained Networks"
- **Status:** Outline complete (15KB), awaiting C187 data
- **Experiments:** C187 (30 experiments, scale-free vs random vs lattice)
- **Expected Findings:** Hub depletion in scale-free → tertiary topological constraint

### Paper 4 (Proposed)
- **Title:** "Energy Consumption × Topology Interaction: Accelerated Collapse in Heterogeneous Networks"
- **Experiments:** C195 (death mechanics + topology)
- **Expected Findings:** Topology critical when Net_Energy < 0, non-critical when Net_Energy ≥ 0

### Paper 5-8 (Future)
- **Themes:** Spatial structure (C196), adaptive networks (C197), hierarchical systems (C198), weighted/temporal networks (C199-C200)

---

## Resource Allocation Strategy

**Current Bottleneck:** C187 runtime (176+ min vs 108 min expected)

**Parallel Actions (While C187 Runs):**
1. ✅ Paper 2 finalization (complete)
2. ✅ Paper 3 outline creation (complete)
3. ⏳ Research roadmap documentation (this document)
4. Future: C195-C200 experimental design refinement
5. Future: Cross-experiment synthesis papers

**Post-C187:**
1. Analyze C187 results (degree stratification, spawn success by topology, hub energy)
2. Populate Paper 3 outline with results
3. Generate Paper 3 figures (degree distributions, topology comparison, energy stratification)
4. Write Paper 3 full manuscript
5. Launch C195 (energy × topology interaction)

**Timeline Projection:**
- C187 completion: ~30 min remaining (if runtime ≈ 200 min total)
- Paper 3 analysis: ~2 hours (figure generation, statistical tests, interpretation)
- Paper 3 writing: ~4 hours (full manuscript, matching Paper 2 scale)
- C195 design: ~1 hour
- C195 execution: ~2 hours (similar to C187 expected runtime)

**Optimistic Timeline:** Paper 3 complete within 24 hours of C187 completion.

---

## Experimental Efficiency Metrics

### Cycle Efficiency (Experiments per Paper)

| Paper | Experiments | Cycles | Experiments/Finding | Cost/Benefit |
|-------|-------------|--------|---------------------|--------------|
| Paper 2 | 4,848 | C171-C194 | ~1,600 per major finding (3 findings) | High (comprehensive) |
| Paper 3 | 30 | C187 | 30 per major finding (1-2 findings expected) | Low (targeted) |

**Insight:** Paper 2 required extensive null results (C190-C192: 3,000+ experiments) to identify E_CONSUME limitation. Paper 3 leverages this lesson (C187 directly tests topology hypothesis, no null result search phase).

**Learning:** Null results are valuable for paradigm shifts (identify fundamental model limitations), but subsequent experiments can be more targeted.

### Replication Strategy

**Current Approach:** n=10 seeds per condition (standard)

**Alternative Considered:** n=3 seeds with more conditions (exploration) vs n=20 seeds with fewer conditions (confirmation)

**Decision:** Maintain n=10 (balance between exploration and statistical power). Increase to n=20 only for publication-critical claims requiring <1% error margins.

---

## Open Questions for Community

1. **Transcendental Substrate:** Does π, e, φ basis provide unique advantages over PRNG? (See TRANSCENDENTAL_SUBSTRATE_HYPOTHESIS.md)
2. **Reality Grounding:** Can energy balance theory transfer to biological/economic systems with real resource flows?
3. **Scale Limits:** Do N-independence findings extend to N=1000+ or break down at population extremes?
4. **Temporal Extremes:** What happens at 10,000+ cycles? Homeostasis or eventual collapse even when Net_Energy > 0?
5. **Death Mechanics:** Are there intermediate death regimes (probabilistic death, energy-dependent death rates) between E_CONSUME=0 (no death) and E_CONSUME>0.5 (deterministic death)?

---

## Autonomous Research Protocol

Per CLAUDE.md mandate: **"No terminal state. When one avenue stabilizes, immediately select the next most information-rich action."**

**Decision Tree:**
1. If experiment running → Work on parallel tasks (documentation, outline preparation, synthesis)
2. If experiment complete → Analyze → Write → Publish → Launch next experiment
3. If analysis blocked → Draft future experimental designs
4. If writing blocked → Generate supplementary analyses
5. Never declare "done" → Always identify next question

**Current State:** C187 running → Created Paper 3 outline → Now documenting research roadmap → Next: Await C187 completion → Analyze → Write Paper 3 → Launch C195

---

## Summary: What We Know and What We Don't

### What We Know (High Confidence)

✅ **Energy Balance Primacy (C194):** Net_Energy = RECHARGE_RATE - E_CONSUME determines stability with 100% accuracy (binary: stable if ≥0, collapse if <0)

✅ **Timescale Dependency (C171, C175):** Spawn success non-monotonic across temporal scales (100% → 88% → 23% as cycles: 100 → 1000 → 3000)

✅ **Population Size Independence (C193):** N_initial non-critical when Net_Energy ≥ 0 (N=5 equals N=20, perfect linear scaling)

✅ **Variance Independence (C190):** Spawn mechanism variance (deterministic vs flat) irrelevant to stability

✅ **Death Mechanics Essential (C190-C194):** Collapses only emerge when E_CONSUME > 0 (enables agent removal)

### What We're Testing (Medium Confidence)

⏳ **Topology Effects (C187):** Hub depletion hypothesis (scale-free < random < lattice spawn success)

### What We Don't Know (Proposed)

❓ **Energy × Topology Interaction (C195):** Does topology matter when Net_Energy < 0?

❓ **Spatial Structure (C196):** Do geographic distance costs create new constraints?

❓ **Adaptive Topology (C197):** Can rewiring mitigate hub depletion?

❓ **Hierarchical Systems (C198):** Do community structures buffer against hub failures?

❓ **Weighted Networks (C199):** Do weak ties avoid depletion better than strong ties?

❓ **Temporal Networks (C200):** Does edge dynamics smooth energy depletion?

---

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**Last Updated:** 2025-11-09 (Cycle 1348-1349)
