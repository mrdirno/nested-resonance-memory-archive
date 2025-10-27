# Cycle 177: Hypothesis 1 - Energy Pooling Experiment Design

**Date:** 2025-10-26 (Cycle 225)
**Hypothesis Test:** H1 - Agent Cooperation Through Energy Pooling
**Author:** Claude (DUALITY-ZERO-V2)
**Principal Investigator:** Aldrin Payopay
**Status:** Design Phase

---

## Background

From Paper 2 (Section 4.4.1), Hypothesis 1 proposes that **shared energy reservoirs within resonance clusters** can eliminate the single-parent reproductive bottleneck observed in C176 collapse dynamics.

**Problem Identified:**
- Birth capacity concentrated in root agent (high initial energy E₀=130)
- Children inherit low energy (Gen 1: 30-40, Gen 2: 9-12) and quickly become sterile
- Death capacity distributed across ALL agents uniformly
- Result: Birth bottlenecked by single lineage, death affects all agents

**Proposed Solution:**
Agents within resonance clusters pool energy for collective spawning. Each agent contributes a fraction to shared reservoir, enabling ANY agent in cluster to spawn if reservoir ≥ spawn_threshold.

---

## Hypothesis Statement

**H1 (Energy Pooling):** Agents share energy within resonance clusters, addressing the single-parent bottleneck by distributing reproductive capacity across all cluster members.

**Mechanistic Prediction:**
- Shared energy reservoir eliminates single-parent constraint
- Multiple agents can regain reproductive capacity simultaneously
- Asynchronous spawning maintains continuous birth presence
- Birth rate increases from 0.005 → 0.015 agents/cycle (3× improvement)

**Quantitative Prediction:**
- **Birth rate:** 3× increase (0.005 → 0.015 agents/cycle)
- **Sustained population:** mean > 5 agents (vs 0.49 baseline)
- **Population stability:** CV < 50% (vs 101% baseline)
- **Death-birth balance:** Ratio approaches 1.0 (vs 2.5× imbalance)

---

## Experimental Design

### Conditions

**Baseline (Control):** C176 V4 architecture
- Complete birth-death coupling
- Energy recharge enabled (r=0.010)
- NO energy pooling
- Expected: Catastrophic collapse (mean=0.49)

**Treatment (H1 - Energy Pooling):** Modified architecture
- Complete birth-death coupling
- Energy recharge enabled (r=0.010)
- **Energy pooling within resonance clusters**
- Expected: Sustained population (mean > 5)

### Parameters

**Fixed Across Conditions:**
- Spawn frequency: f = 2.5%
- Cycles per experiment: 3,000
- Seeds: n = 10 (42, 123, 456, 789, 101, 202, 303, 404, 505, 606)
- Energy recharge rate: r = 0.010
- Spawn cost: 30% of parent energy
- Spawn threshold: E ≥ 10.0

**Treatment-Specific (Energy Pooling):**
- Sharing fraction: α = 0.10 (10% of each agent's energy per cycle)
- Pooling trigger: Resonance cluster detected (phase alignment > threshold)
- Distribution: Equal allocation to agents below spawn threshold
- Persistence: Pool dissolves when cluster decomposes

### Implementation

```python
class FractalAgent:
    """
    Modified FractalAgent with energy pooling capability.
    """

    def __init__(self, agent_id, initial_energy, reality=None, pooling_enabled=False):
        self.agent_id = agent_id
        self.energy = initial_energy
        self.reality = reality
        self.pooling_enabled = pooling_enabled
        self.cluster_id = None  # Set when resonance cluster forms

    def contribute_to_pool(self, sharing_fraction=0.10):
        """
        Contribute fraction of energy to cluster pool.
        Returns contribution amount (deducted from agent energy).
        """
        if not self.pooling_enabled or self.cluster_id is None:
            return 0.0

        contribution = self.energy * sharing_fraction
        self.energy -= contribution
        return contribution

    def receive_from_pool(self, pool_energy, spawn_threshold=10.0):
        """
        Receive energy from pool if below spawn threshold.
        Returns amount received.
        """
        if not self.pooling_enabled or self.cluster_id is None:
            return 0.0

        if self.energy >= spawn_threshold:
            return 0.0  # Already fertile

        needed = spawn_threshold - self.energy
        received = min(pool_energy, needed)
        self.energy += received
        return received


class FractalSwarm:
    """
    Modified FractalSwarm with cluster-based energy pooling.
    """

    def energy_pooling_cycle(self, agents, composition_engine):
        """
        Execute one energy pooling cycle:
        1. Detect resonance clusters
        2. Collect contributions from cluster members
        3. Distribute pool to agents below threshold
        """
        # Detect current resonance clusters
        cluster_events = composition_engine.detect_clusters(agents)

        if not cluster_events:
            return  # No clusters, no pooling

        # Process each cluster
        for cluster in cluster_events:
            cluster_agents = [a for a in agents if a.agent_id in cluster.agent_ids]

            if len(cluster_agents) < 2:
                continue  # Need at least 2 agents to pool

            # Collect contributions
            pool_energy = 0.0
            for agent in cluster_agents:
                pool_energy += agent.contribute_to_pool(sharing_fraction=0.10)

            # Distribute to agents below threshold
            for agent in sorted(cluster_agents, key=lambda a: a.energy):
                if pool_energy <= 0:
                    break
                received = agent.receive_from_pool(pool_energy, spawn_threshold=10.0)
                pool_energy -= received
```

### Metrics

**Primary Outcomes:**
1. **Mean population:** Average agent count over 3,000 cycles
2. **Population CV:** Coefficient of variation (stability measure)
3. **Birth rate:** Total spawn events / 3,000 cycles
4. **Death rate:** Total composition events / 3,000 cycles
5. **Death-birth ratio:** Death rate / sustained birth rate

**Secondary Outcomes:**
1. **Final agent count:** Population at cycle 3,000
2. **Extinction rate:** Proportion of seeds reaching P=0
3. **Cluster formation:** Number of resonance clusters formed
4. **Energy pool utilization:** Total energy transferred via pooling
5. **Multi-generational lineages:** Number of Gen 2+ agents spawned

---

## Statistical Analysis

### Hypothesis Test

**Null Hypothesis (H₀):** Energy pooling has NO effect on population sustainability.
- H₀: μ_pooling = μ_baseline = 0.49

**Alternative Hypothesis (H₁):** Energy pooling INCREASES sustained population.
- H₁: μ_pooling > μ_baseline (one-tailed test)

### Analysis Plan

**Independent Samples t-Test:**
```
Conditions: BASELINE (n=10) vs POOLING (n=10)
DV: Mean population
α: 0.05 (one-tailed)
Power: 0.80 (minimum)
Effect size: Cohen's d (expect large effect, d > 0.8)
```

**Supporting Tests:**
1. **Birth rate comparison:** Two-sample t-test (pooling vs baseline)
2. **Death-birth ratio:** Two-sample t-test (expect ratio closer to 1.0)
3. **Stability improvement:** CV comparison (expect pooling CV < 50%)

**Effect Size:**
- Cohen's d for mean population
- Proportional improvement in birth rate
- Reduction in death-birth imbalance

---

## Expected Results

### Scenario A: Hypothesis Confirmed (Strong Effect)

**Quantitative:**
- Mean population: 8-12 agents (vs 0.49 baseline)
- CV: 20-40% (vs 101% baseline)
- Birth rate: 0.015 agents/cycle (3× increase)
- Death-birth ratio: 1.2-1.5 (vs 2.5× baseline)
- Final count: 6-10 agents (vs 0 baseline)

**Statistical:**
- t-test: p < 0.001
- Cohen's d > 1.5 (very large effect)
- Extinction rate: 0% (vs 100% baseline)

**Interpretation:**
Energy pooling successfully eliminates single-parent bottleneck. Distributed reproductive capacity enables sustained populations. Birth rate increases to match death rate, achieving approximate birth-death balance.

### Scenario B: Hypothesis Confirmed (Moderate Effect)

**Quantitative:**
- Mean population: 3-5 agents (vs 0.49 baseline)
- CV: 50-70% (vs 101% baseline)
- Birth rate: 0.010 agents/cycle (2× increase)
- Death-birth ratio: 1.5-2.0 (vs 2.5× baseline)
- Final count: 1-4 agents (vs 0 baseline)

**Statistical:**
- t-test: p < 0.01
- Cohen's d = 0.8-1.2 (large effect)
- Extinction rate: 10-30% (vs 100% baseline)

**Interpretation:**
Energy pooling partially addresses bottleneck but insufficient for full homeostasis. Birth rate improved but still below death rate. May require synergistic combination with other hypotheses (H2, H3, H4, H5).

### Scenario C: Hypothesis Rejected (Null Result)

**Quantitative:**
- Mean population: 0.4-0.6 agents (identical to baseline)
- CV: 95-105% (no improvement)
- Birth rate: 0.005 agents/cycle (no change)
- Death-birth ratio: 2.4-2.6 (no improvement)
- Final count: 0 agents (100% extinction)

**Statistical:**
- t-test: p > 0.05 (not significant)
- Cohen's d < 0.2 (negligible effect)
- Extinction rate: 100% (same as baseline)

**Interpretation:**
Energy pooling alone insufficient to overcome collapse dynamics. Single-parent bottleneck NOT the primary limitation. Other asymmetries (recovery lag, continuous death activity) dominate. Requires different intervention (H2, H4, H5) or synergistic combination.

---

## Implementation Requirements

### Code Modifications

**Files to Modify:**
1. `fractal_agent.py` - Add pooling methods to FractalAgent class
2. `fractal_swarm.py` - Add energy_pooling_cycle to FractalSwarm
3. `cycle177_h1_energy_pooling.py` - New experiment script

**New Methods:**
1. `FractalAgent.contribute_to_pool()` - Calculate and deduct contribution
2. `FractalAgent.receive_from_pool()` - Accept energy from pool
3. `FractalSwarm.energy_pooling_cycle()` - Orchestrate pooling within clusters

**Testing:**
1. Unit tests for pooling logic (conservation of energy)
2. Integration test for cluster pooling (multi-agent)
3. Validation against baseline (reproduce C176 V4 when pooling_enabled=False)

### Data Collection

**Metrics to Log:**
1. Population time series (every cycle)
2. Energy time series per agent (every 100 cycles)
3. Cluster events (formation, pooling amount, dissolution)
4. Spawn events with lineage tracking (Gen 1/2/3+)
5. Composition events (death timing)

**Output Files:**
1. `cycle177_h1_energy_pooling_results.json` - Aggregate metrics per seed
2. `cycle177_h1_timeseries.json` - Full population/energy trajectories
3. `cycle177_h1_analysis.txt` - Statistical analysis report

---

## Timeline

**Phase 1: Implementation (1 cycle, ~30 minutes)**
- Modify FractalAgent with pooling methods
- Modify FractalSwarm with pooling cycle
- Create experiment script cycle177_h1_energy_pooling.py
- Write unit tests for energy conservation

**Phase 2: Validation (1 cycle, ~30 minutes)**
- Run baseline replication (pooling_enabled=False, n=3 seeds)
- Verify C176 V4 reproduction (mean=0.49, spawn=75, comp=38)
- Validate energy conservation in pooling logic

**Phase 3: Execution (1 cycle, ~30 minutes)**
- Run H1 treatment (pooling_enabled=True, n=10 seeds)
- Monitor execution, collect data
- Generate time series and event logs

**Phase 4: Analysis (1 cycle, ~30 minutes)**
- Statistical tests (t-test, effect size, CI)
- Generate comparison figures (population trajectories, birth/death rates)
- Write analysis report with interpretation

**Total:** 4 cycles (~2 hours) from design to results

---

## Success Criteria

**Hypothesis Confirmed:**
1. ✅ Mean population significantly higher (p < 0.05)
2. ✅ Cohen's d > 0.8 (large effect size)
3. ✅ Birth rate increase ≥ 2× (0.005 → 0.010+)
4. ✅ Extinction rate < 50% (vs 100% baseline)

**Publication Value:**
1. ✅ First empirical test of energy pooling hypothesis
2. ✅ Quantified effect on death-birth balance
3. ✅ Mechanistic validation of cooperative emergence
4. ✅ Informs next hypothesis tests (synergistic combinations)

**Research Continuity:**
- Confirmed: Test H2-H5 individually, then pairwise combinations
- Partially confirmed: Test H1+H2, H1+H4, H1+H5 combinations
- Rejected: Pivot to H2 (external sources) or H4 (composition throttling)

---

## Risk Mitigation

**Potential Issues:**

1. **Energy conservation violation:** Pool distributes more energy than collected
   - **Mitigation:** Unit tests for contribution/distribution balance
   - **Validation:** Total system energy tracked every cycle

2. **Cluster instability:** Clusters form/dissolve too rapidly for effective pooling
   - **Mitigation:** Add cluster persistence threshold (min 10 cycles)
   - **Fallback:** Test with higher resonance threshold (more stable clusters)

3. **Implementation bugs:** Pooling logic has errors
   - **Mitigation:** Extensive unit testing before full experiment
   - **Validation:** Baseline replication (pooling_enabled=False) matches C176 V4

4. **Null result:** No effect observed
   - **Mitigation:** Not a failure - important negative result
   - **Action:** Proceed to H2, H4, or synergistic combinations
   - **Publication:** Document why single-parent bottleneck NOT primary constraint

---

## Next Steps

**Immediate Actions (Cycle 225):**
1. ✅ Design document complete (this file)
2. 🔲 Implement FractalAgent.contribute_to_pool() method
3. 🔲 Implement FractalAgent.receive_from_pool() method
4. 🔲 Implement FractalSwarm.energy_pooling_cycle() method
5. 🔲 Create cycle177_h1_energy_pooling.py experiment script
6. 🔲 Write unit tests for energy conservation

**Subsequent Cycles:**
- Validation (baseline replication)
- Execution (H1 treatment, n=10)
- Analysis (statistical tests, figures, interpretation)
- Integration into Paper 2 (Results section extension)

---

## References

**Paper 2 Sections:**
- Section 4.4.1: Hypothesis 1 - Energy Pooling (full mechanistic rationale)
- Section 5.3: Three Structural Asymmetries (identifies single-parent bottleneck)
- Section 3.5: V4 Results (baseline for comparison)

**Experimental Data:**
- C176 V4: `/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle176_ablation_study_v4.json`
- Baseline metrics: mean=0.494, CV=101.3%, spawn=75, comp=38, final=0

**Theoretical Framework:**
- Nested Resonance Memory: Resonance-based clustering for pooling trigger
- Self-Giving Systems: Agents self-organize cooperative energy sharing
- Temporal Stewardship: Testing predictions encoded in Paper 2

---

**Document Status:** Design Complete
**Author:** Claude (DUALITY-ZERO-V2)
**Principal Investigator:** Aldrin Payopay
**Date:** 2025-10-26 (Cycle 225)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

**Next Action:** Implement energy pooling methods in FractalAgent class

---

**END OF DESIGN DOCUMENT**
