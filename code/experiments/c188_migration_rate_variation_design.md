# C188: Migration Rate Variation - Experimental Design

**Campaign:** C188 - Migration Rescue Efficiency vs Coupling Strength
**Date:** 2025-11-08 (Cycle 1319)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**Related:** Paper 8 (C186 Hierarchical Organization), C187 (Population Count Variation)

---

## Research Question

**How does migration rate ($f_{migrate}$) affect hierarchical advantage and rescue efficiency?**

Paper 8 used $f_{migrate} = 0.5\%$ (same as minimum tested spawn frequency). V7 demonstrated zero migration ($f_{migrate} = 0.0\%$) eliminates hierarchical advantage entirely. This experiment systematically varies migration rate to:

1. Quantify relationship between $f_{migrate}$ and hierarchical advantage (α)
2. Identify optimal migration rate balancing rescue efficiency vs overhead
3. Test whether rescue mechanism requires minimum coupling strength

---

## Theoretical Framework

### Migration as Coupling Strength

**Conceptual Model:**
- **Compartmentalization** = Independent energy pools (enables risk distribution)
- **Migration** = Inter-compartment coupling (enables rescue)
- **Hierarchical advantage** emerges from balance: isolation + integration

**Coupling Strength Spectrum:**
- $f_{migrate} = 0.0\%$: Full isolation (no rescue) → α ≈ 1
- $f_{migrate} > 0\%$: Partial coupling (rescue enabled) → α > 1
- $f_{migrate}$ very high: Strong coupling (rescue efficient but overhead risk)

### Competing Hypotheses

**H1: Monotonic Increase (More Rescue Always Better)**
- Higher migration → more rescue → higher α
- Prediction: α increases monotonically with $f_{migrate}$
- Mechanism: More agent transfers = more opportunities to rebalance populations

**H2: Optimal Migration Rate (Trade-off)**
- Sweet spot balances rescue benefit vs coupling overhead
- Prediction: α peaks at intermediate $f_{migrate}$ (e.g., 1.0%-2.0%)
- Mechanism: Too low = insufficient rescue, too high = homogenization reduces compartmentalization benefit

**H3: Threshold Behavior (Minimum Coupling Required)**
- Phase transition at critical $f_{migrate}$
- Prediction: α ≈ 1 for $f_{migrate} < f_{crit}$, α >> 1 for $f_{migrate} \geq f_{crit}$
- Mechanism: Rescue requires minimum agent transfer rate to prevent collapse

**H4: Plateau (Saturation Above Minimum)**
- Any non-zero migration sufficient for rescue
- Prediction: α jumps at $f_{migrate} > 0$, then plateaus
- Mechanism: Rare rescue events prevent catastrophic failures; additional migration doesn't improve efficiency

### Predictions from Paper 8

**V7 Result ($f_{migrate} = 0.0\%$):**
- Zero migration causes system failure (stuck state, 18-30% CPU)
- Prediction: $f_{migrate} = 0.0\%$ shows α ≈ 1 (no advantage)

**V1-V5 Result ($f_{migrate} = 0.5\%$):**
- 0.5% migration enables robust hierarchical advantage (α = 607)
- Prediction: $f_{migrate} = 0.5\%$ replicates baseline α ≈ 600

**Migration Necessity:**
- V7 failure validates migration as necessary mechanism
- Prediction: Even very low $f_{migrate}$ (e.g., 0.1%) should enable some advantage (α > 1)

---

## Experimental Design

### Independent Variable

**Migration Frequency ($f_{migrate}$):** Probability per cycle of inter-population agent transfer

**Tested Values:**
- $f_{migrate} = 0.0\%$: No migration (replication of V7 edge case, expect failure)
- $f_{migrate} = 0.1\%$: Very low coupling (test minimum rescue threshold)
- $f_{migrate} = 0.2\%$: Low coupling
- $f_{migrate} = 0.5\%$: Baseline (replication of V1-V5)
- $f_{migrate} = 1.0\%$: Moderate coupling
- $f_{migrate} = 2.0\%$: High coupling
- $f_{migrate} = 5.0\%$: Very high coupling (test overhead/homogenization effects)

**Rationale:**
- $f_{migrate} = 0.0\%$ lower boundary (expect α ≈ 1, system failure)
- $f_{migrate} = 0.5\%$ validates baseline (expect α ≈ 600)
- Fine resolution (0.1%, 0.2%, 0.5%) near lower boundary tests threshold
- Higher values (1.0%, 2.0%, 5.0%) test saturation and overhead

### Controlled Variables

**Fixed Parameters (matching C186):**
- Population count: $n_{pop} = 10$
- Initial agents per population: $n_{init} = 20$ (200 total)
- Intra-population spawn frequency: $f_{intra} = 2.0\%$
- Cycle duration: 3000 cycles
- Basin classification: A (homeostasis) vs B (collapse)

**Why $f_{intra} = 2.0\%$?**
- Mid-range frequency (V3 baseline)
- Stable behavior in C186 (79.86 ± 4.03 agents, 100% Basin A)
- Avoids confounding with spawn frequency effects

### Dependent Variables

**Primary Outcome:**
- **Hierarchical advantage:** $\alpha = f_{crit}^{single} / f_{crit}^{hier}$

**Secondary Outcomes:**
1. **Sustained population size** (mean, SD across seeds)
2. **Basin classification** (% Basin A vs B)
3. **Inter-population variance** (coefficient of variation across populations)
4. **Migration events** (total agent transfers per experiment)
5. **System health** (CPU usage, stuck state detection)

### Experimental Conditions

**7 conditions × 10 seeds = 70 experiments**

| Condition | $f_{migrate}$ (%) | Expected Runtime | Expected Behavior |
|-----------|-------------------|------------------|-------------------|
| C188-0 | 0.0 | 85 min* | FAILURE (stuck state, V7 replication) |
| C188-1 | 0.1 | 20 min | Minimal rescue (test threshold) |
| C188-2 | 0.2 | 22 min | Low rescue |
| C188-5 | 0.5 | 25 min | BASELINE (V1-V5 replication, α≈600) |
| C188-10 | 1.0 | 28 min | Moderate rescue |
| C188-20 | 2.0 | 30 min | High rescue |
| C188-50 | 5.0 | 35 min | Very high rescue (test overhead) |

*Note: C188-0 expected to fail (stuck state like V7), may require manual termination

**Total Runtime:** ~175 minutes (~3 hours) if C188-0 monitored and terminated early

**Seeds:** 10 independent random seeds per condition

---

## Implementation Notes

### Edge Case Handling ($f_{migrate} = 0.0\%$)

**V7 Behavior:** Zero migration caused stuck state (18-30% CPU, 85 min runtime, 0 experiments completed)

**Defensive Implementation for C188-0:**
1. **Timeout mechanism:** Terminate experiment after 30 min if stuck detected
2. **CPU monitoring:** Track CPU usage every 1 min, flag if drops below 50% (stuck threshold)
3. **Graceful termination:** Save partial results, mark as "FAILED - stuck state"
4. **Automatic skip option:** If desired, skip $f_{migrate} = 0.0\%$ entirely (already validated in V7)

**Recommendation:** Include C188-0 for completeness (validates α ≈ 1 at zero migration), but monitor closely and terminate if stuck.

### Migration Logic Verification

**Per-Cycle Migration:**
```python
if random() < f_migrate:
    source = random_choice(populations)
    target = random_choice([p for p in populations if p != source])
    if source.agents:
        agent = random_choice(source.agents)
        source.remove(agent)
        target.add(agent)
        migration_count += 1
```

**Expected Migration Events:**
- $f_{migrate} = 0.1\%$: ~3 migrations per 3000-cycle experiment
- $f_{migrate} = 0.5\%$: ~15 migrations per experiment (C186 baseline)
- $f_{migrate} = 5.0\%$: ~150 migrations per experiment

**Validation:** Count actual migrations, compare to expected (3000 × $f_{migrate}$)

---

## Analysis Plan

### Hierarchical Advantage Calculation

**For each condition ($f_{migrate}$):**
1. Calculate mean sustained population across 10 seeds
2. Compare to single-scale baseline ($f_{crit}^{single} \approx 4.0\%$)
3. Calculate $\alpha = f_{crit}^{single} / f_{crit}^{hier}$

**Expected Pattern:**
- $f_{migrate} = 0.0\%$: α ≈ 1 (no advantage)
- $f_{migrate} = 0.5\%$: α ≈ 600 (baseline)
- Higher $f_{migrate}$: Test hypotheses (monotonic, optimal, threshold, plateau)

### Statistical Tests

**Primary Tests:**
1. **ANOVA:** α ~ $f_{migrate}$ (7 levels, or 6 if C188-0 excluded)
2. **Post-hoc:** Tukey HSD for pairwise comparisons (if ANOVA significant)

**Trend Analysis:**
- **Linear:** α ~ $f_{migrate}$ (test monotonic increase H1)
- **Quadratic:** α ~ $f_{migrate} + f_{migrate}^2$ (test optimal H2)
- **Step function:** α ~ I($f_{migrate} > 0$) (test threshold H3)
- **Logarithmic:** α ~ log($f_{migrate}$) (test saturation H4)

**Model Selection:** Compare AIC/BIC across models, select best fit

### Rescue Efficiency Metric

**Definition:** Rescue efficiency = $\alpha$ per migration event

$$\text{Rescue Efficiency} = \frac{\alpha}{\text{mean migrations per experiment}}$$

**Interpretation:**
- High efficiency: Small number of migrations produces large α (rare rescues sufficient)
- Low efficiency: Many migrations required to achieve α (frequent rescues needed)

**Prediction:**
- If H4 (plateau): Rescue efficiency highest at low $f_{migrate}$ (diminishing returns)
- If H1 (monotonic): Rescue efficiency constant (linear benefit)

---

## Figures

**Figure 1: Hierarchical Advantage vs Migration Rate**
- X-axis: $f_{migrate}$ (%) - logarithmic scale (0.0, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0)
- Y-axis: Hierarchical advantage α
- Error bars: ±1 SD across 10 seeds
- Fits: Linear, quadratic, step function overlaid

**Figure 2: Sustained Population vs Migration Rate**
- X-axis: $f_{migrate}$ (%)
- Y-axis: Mean sustained population (absolute and normalized by initial)
- Compare to single-scale baseline (horizontal line)

**Figure 3: Rescue Efficiency**
- X-axis: $f_{migrate}$ (%)
- Y-axis: Rescue efficiency (α per migration event)
- Interpretation: Optimal rescue strategy (maximize α with minimal migration overhead)

**Figure 4: Inter-Population Variance vs Migration**
- X-axis: $f_{migrate}$ (%)
- Y-axis: Coefficient of variation (CV) across populations
- Hypothesis: Higher migration → lower CV (homogenization effect)

---

## Expected Results

### Hypothesis-Specific Predictions

**If H1 (Monotonic Increase):**
- α increases with $f_{migrate}$: $\alpha_{0.0} < \alpha_{0.1} < ... < \alpha_{5.0}$
- Linear fit best
- Rescue efficiency constant
- Implication: More coupling always better (no overhead penalty)

**If H2 (Optimal Migration Rate):**
- α peaks at intermediate $f_{migrate}$ (e.g., 1.0%-2.0%)
- Quadratic fit best (inverted U-shape)
- Rescue efficiency highest at peak
- Implication: Trade-off exists, optimal coupling balances rescue vs compartmentalization

**If H3 (Threshold Behavior):**
- α ≈ 1 for $f_{migrate} = 0.0\%$, α >> 1 for $f_{migrate} \geq 0.1\%$
- Step function fit best
- Rescue efficiency highest just above threshold
- Implication: Minimum coupling required, but exact value not critical

**If H4 (Plateau Above Minimum):**
- α jumps at $f_{migrate} > 0.0\%$, then plateaus: $\alpha_{0.1} \approx \alpha_{0.5} \approx \alpha_{5.0}$
- Logarithmic fit best
- Rescue efficiency decreases with higher $f_{migrate}$
- Implication: Rare rescue events sufficient; additional migration yields diminishing returns

### Baseline Expectations

**$f_{migrate} = 0.0\%$ (C188-0):**
- No migration, no rescue
- Expect α ≈ 1 (no advantage)
- Expect system failure (stuck state like V7)

**$f_{migrate} = 0.5\%$ (C188-5):**
- Replicates V1-V5 baseline
- Expect α ≈ 600
- Validates consistency with C186

**$f_{migrate} = 5.0\%$ (C188-50):**
- Very high coupling
- If H1: α >> 600
- If H2: α < peak (overhead penalty)
- If H4: α ≈ 600 (saturated)

---

## Integration with Paper 8

### Option 1: Integrate into Paper 8

**New Section:** 3.8 Migration Rate Optimization (after Population Count Scaling if C187 integrated)

**Key Additions:**
- Figure: Hierarchical advantage α vs $f_{migrate}$
- Discussion 4.9: Optimal coupling strength for rescue efficiency
- Abstract mention: "...tested migration rates $f_{migrate} = 0.0\%-5.0\%$..."

### Option 2: Combined Paper 8B

**Title:** "Optimizing Hierarchical Multi-Agent Systems: Population Count and Migration Rate Trade-offs"

**Integrate C187 + C188:**
- Section 3.1: Population count variation (C187)
- Section 3.2: Migration rate variation (C188)
- Section 4: Combined analysis (interaction effects, design principles)

**Target:** PLOS Computational Biology or Complexity

### Option 3: Separate Paper 8C

**Title:** "Migration Rescue Efficiency in Hierarchical Nested Resonance Memory Systems"

**Focus:**
- Quantify rescue efficiency across migration rates
- Identify optimal coupling strength
- Establish design principles for hierarchical rescue mechanisms

---

## Timeline

**Execution:** ~3 hours (70 experiments, with C188-0 monitored/terminated early)
**Analysis:** ~2 hours (statistical tests, figure generation)
**Integration:** ~1-2 hours (Paper 8 extension) or ~6-8 hours (standalone Paper 8C)

**Total:** 6-13 hours from execution to publication-ready results

---

## Success Criteria

**Experiment succeeds if:**
1. ✅ All 70 experiments complete (or 60 if C188-0 excluded after validation)
2. ✅ $f_{migrate} = 0.0\%$ replicates V7 behavior (α ≈ 1, stuck state)
3. ✅ $f_{migrate} = 0.5\%$ replicates V1-V5 baseline (α ≈ 600)
4. ✅ Clear relationship emerges (monotonic, optimal, threshold, or plateau)
5. ✅ Results publishable (extend Paper 8, combined 8B, or standalone 8C)

**Experiment fails if:**
- ❌ No consistent pattern in α vs $f_{migrate}$ relationship
- ❌ Results contradict Paper 8 baseline ($f_{migrate} = 0.5\%$ doesn't replicate)
- ❌ All conditions show stuck states (implementation error)

---

## Design Rationale

**Why This Experiment Matters:**

1. **Mechanism Validation:** Paper 8 established migration is *necessary* (V7 failure). C188 quantifies *how much* migration is required.

2. **Design Principles:** Identifies optimal coupling strength for hierarchical systems (generalizable beyond NRM).

3. **Rescue Efficiency:** Quantifies cost-benefit of inter-compartment communication (important for resource-constrained systems).

4. **Theoretical Insight:** Tests trade-off between isolation (compartmentalization benefit) and integration (rescue mechanism).

**Novel Contribution:**
- First systematic study of migration rate optimization in hierarchical NRM
- Establishes rescue efficiency metric (α per migration event)
- Could inform distributed system design (bandwidth allocation for fault tolerance)

**Generalizability:**
- Results apply to any system with compartmentalized resources and inter-compartment rescue
- Distributed computing: Node failure recovery
- Ecological metapopulations: Dispersal rate optimization
- Organizational design: Communication frequency in hierarchical teams

---

## Relationship to C187

**Complementary Experiments:**

**C187 (Population Count):**
- Tests *breadth* of hierarchy (how many compartments?)
- Fixed migration rate ($f_{migrate} = 0.5\%$)

**C188 (Migration Rate):**
- Tests *coupling strength* of hierarchy (how connected are compartments?)
- Fixed population count ($n_{pop} = 10$)

**Combined Analysis (If Both Executed):**
- 2×2 design space: ($n_{pop}$, $f_{migrate}$)
- Test interaction: Does optimal migration rate depend on population count?
- Example: More populations → require lower migration per population (rescue probability scales with $n_{pop}$)

**Potential Paper 8B:** "Design Principles for Hierarchical Multi-Agent Systems: Population Count and Coupling Strength Trade-offs"

---

## Notes

**Implementation Priority:**
- C187 (population count) should execute first (validates $n_{pop} = 10$ baseline)
- C188 (migration rate) can run independently or after C187

**Defensive Coding:**
- C188-0 ($f_{migrate} = 0.0\%$) needs timeout and stuck state detection
- Log CPU usage every cycle for health monitoring
- Save partial results if experiment terminated early

**Expected Discovery:**
- If H4 (plateau): Reveals minimum migration rate for rescue (design guideline)
- If H2 (optimal): Identifies sweet spot balancing rescue vs overhead
- If H1 (monotonic): Suggests no upper limit to coupling benefit (surprising result)

---

**Status:** Experimental design complete, ready for implementation
**Next Actions:** Implement `c188_migration_rate_variation.py`, execute after C187 (or independently), analyze results
**Expected Completion:** 6-13 hours total (execution + analysis + integration)

**Research is perpetual. C188 designed to complement C187. Implementation awaits.**
