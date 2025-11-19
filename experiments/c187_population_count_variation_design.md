# C187: Population Count Variation - Experimental Design

**Campaign:** C187 - Hierarchical Advantage Scaling with Population Count
**Date:** 2025-11-08 (Cycle 1319)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Author:** Claude (DUALITY-ZERO-V2 Sonnet 4.5)
**Related:** Paper 8 (C186 Hierarchical Organization), Section 4.6 Future Work

---

## Research Question

**How does hierarchical advantage (α) scale with number of populations ($n_{pop}$)?**

Paper 8 established α = 607× for $n_{pop} = 10$. This experiment tests whether hierarchical advantage:
1. Increases with more populations (more redundancy/risk distribution)
2. Decreases with fewer populations (less coordination overhead)
3. Exhibits optimal population count balancing efficiency vs overhead

---

## Theoretical Framework

### Competing Hypotheses

**H1: Monotonic Increase (Risk Distribution Dominates)**
- More populations → more redundancy → higher α
- Prediction: α increases with $n_{pop}$ (no saturation)
- Mechanism: Independent failure events, rescue probability scales with population count

**H2: Diminishing Returns (Coordination Overhead Emerges)**
- Initial populations provide efficiency gains, but marginal benefit decreases
- Prediction: α increases with $n_{pop}$ but saturates (logarithmic or power-law)
- Mechanism: Coordination overhead grows faster than redundancy benefits

**H3: Optimal Population Count (Trade-off)**
- Sweet spot exists balancing efficiency vs coordination
- Prediction: α peaks at intermediate $n_{pop}$, declines at extremes
- Mechanism: Too few = no redundancy, too many = excessive overhead

**H4: Threshold Behavior (Phase Transition)**
- Hierarchical advantage emerges only above critical $n_{pop}$
- Prediction: α ≈ 1 (no advantage) for $n_{pop} < n_{crit}$, α >> 1 for $n_{pop} \geq n_{crit}$
- Mechanism: Rescue mechanism requires minimum population count for stability

### Predictions from Paper 8

**V8 Failure ($n_{pop} = 1$):**
- Single population eliminates hierarchical advantage
- Prediction: $n_{pop} = 1$ should show α ≈ 1 (no advantage over single-scale)

**V1-V5 Success ($n_{pop} = 10$):**
- 10 populations provides robust hierarchical advantage (α = 607)
- Prediction: $n_{pop} = 10$ replicates baseline α ≈ 600

**Migration Necessity (V7 Failure):**
- Migration required for rescue mechanism
- Prediction: All $n_{pop}$ variants with $f_{migrate} = 0.5\%$ should show advantage (α > 1)

---

## Experimental Design

### Independent Variable

**Population Count ($n_{pop}$):** Number of independent populations in hierarchical system

**Tested Values:**
- $n_{pop} = 1$: Single population (no hierarchy, replication of V8 edge case)
- $n_{pop} = 2$: Minimal hierarchy (pairwise rescue)
- $n_{pop} = 5$: Moderate hierarchy
- $n_{pop} = 10$: Baseline (replication of V1-V5)
- $n_{pop} = 20$: High redundancy
- $n_{pop}$ = 50$: Very high redundancy (coordination overhead test)

**Rationale:**
- Logarithmic spacing (1, 2, 5, 10, 20, 50) covers 2 orders of magnitude
- $n_{pop} = 1$ tests lower boundary (expect α ≈ 1)
- $n_{pop} = 10$ validates baseline (expect α ≈ 600)
- $n_{pop} = 50$ tests saturation/overhead effects

### Controlled Variables

**Fixed Parameters (matching C186):**
- Initial agents per population: $n_{init} = 20$
- Intra-population spawn frequency: $f_{intra} = 2.0\%$ (mid-range from V3)
- Migration frequency: $f_{migrate} = 0.5\%$ (validated in C186)
- Cycle duration: 3000 cycles
- Basin classification: A (homeostasis) vs B (collapse)

**Why $f_{intra} = 2.0\%$?**
- Mid-range frequency from C186 (between 1.0% and 5.0%)
- V3 showed stable baseline behavior (79.86 ± 4.03 agents, 100% Basin A)
- Avoids floor effects (too low) and ceiling effects (too high)

### Dependent Variables

**Primary Outcome:**
- **Hierarchical advantage:** $\alpha = f_{crit}^{single} / f_{crit}^{hier}$
- Calculated by comparing sustained population at $f_{intra} = 2.0\%$ to single-scale critical threshold

**Secondary Outcomes:**
1. **Sustained population size** (mean, SD across seeds)
2. **Basin classification** (% Basin A vs B)
3. **Population variance** (across populations, measure of load balancing)
4. **Migration flow** (inter-population agent transfers per cycle)

### Experimental Conditions

**6 conditions × 10 seeds = 60 experiments**

| Condition | $n_{pop}$ | Total Initial Agents | Expected Runtime |
|-----------|-----------|----------------------|------------------|
| C187-1 | 1 | 20 | 18 min |
| C187-2 | 2 | 40 | 20 min |
| C187-5 | 5 | 100 | 22 min |
| C187-10 | 10 | 200 | 25 min |
| C187-20 | 20 | 400 | 30 min |
| C187-50 | 50 | 1000 | 45 min |

**Total Runtime:** ~160 minutes (~2.7 hours)

**Seeds:** 10 independent random seeds per condition (ensure statistical reliability)

---

## Implementation Notes

### Total Agent Count Normalization

**Challenge:** Different $n_{pop}$ yields different total agent counts ($N_{total} = n_{pop} \times n_{init}$)

**Options:**
1. **Fixed total agents** ($N_{total} = 200$ for all conditions, vary $n_{init}$)
   - Advantage: Controls for total system size
   - Disadvantage: Confounds $n_{pop}$ with $n_{init}$ (fewer agents per population)

2. **Fixed agents per population** ($n_{init} = 20$ for all conditions, vary $N_{total}$)
   - Advantage: Isolates $n_{pop}$ as independent variable
   - Disadvantage: Total agent count varies (1×20 to 50×1000)

**Chosen Approach:** Fixed $n_{init} = 20$ (Option 2)

**Rationale:**
- Isolates effect of population count cleanly
- Matches C186 baseline ($n_{init} = 20$)
- Total agent count increase is feature, not bug (tests scaling)
- Migration frequency $f_{migrate} = 0.5\%$ applies per cycle, not per population (normalized)

### Migration Logic

**Per-Cycle Migration:**
- Each cycle, with probability $f_{migrate} = 0.5\%$:
  1. Select random source population (from all populations)
  2. Select random target population (exclude source)
  3. Transfer random agent from source to target (if source non-empty)

**Normalization:**
- Migration rate is **per system**, not per population
- Expected migrations per cycle: 0.5% probability
- Independent of $n_{pop}$ (no bias toward systems with more populations)

### Edge Case Handling

**$n_{pop} = 1$ (C187-1):**
- Single population, no migration possible (no valid target)
- **Defensive implementation:** Skip migration logic when $n_{pop} = 1$
- Expect: No hierarchical advantage (α ≈ 1), replicates V8 behavior

**$n_{pop} = 50$ (C187-50):**
- 50 populations, very high redundancy
- Test whether coordination overhead degrades efficiency
- Expect: Either continued advantage (H1) or saturation/decline (H2/H3)

---

## Analysis Plan

### Hierarchical Advantage Calculation

**For each condition ($n_{pop}$):**
1. Calculate mean sustained population across 10 seeds
2. Normalize by total initial agents: $\bar{N}_{sustained} / N_{total}$
3. Compare to single-scale baseline (assume $f_{crit}^{single} \approx 4.0\%$ from literature)
4. Calculate $\alpha = f_{crit}^{single} / f_{crit}^{hier}$ via extrapolation or direct comparison

**Example:**
- If $n_{pop} = 10$ sustains 80 agents with $f_{intra} = 2.0\%$
- And single-scale sustains 80 agents with $f_{intra} = 4.0\%$
- Then $\alpha = 4.0\% / 2.0\% = 2.0$ (hierarchical is 2× more efficient)

### Statistical Tests

**Primary Test: ANOVA**
- One-way ANOVA: $\alpha$ ~ $n_{pop}$ (6 levels)
- Null hypothesis: No difference in α across $n_{pop}$ conditions
- Alternative: At least one pair differs

**Post-Hoc Tests:**
- Tukey HSD for pairwise comparisons (if ANOVA significant)
- Bonferroni correction for multiple comparisons

**Trend Analysis:**
- Linear regression: $\alpha$ ~ log($n_{pop}$) (test logarithmic scaling)
- Polynomial regression: $\alpha$ ~ $n_{pop} + n_{pop}^2$ (test quadratic for optimal)

### Figures

**Figure 1: Hierarchical Advantage vs Population Count**
- X-axis: $n_{pop}$ (logarithmic scale: 1, 2, 5, 10, 20, 50)
- Y-axis: Hierarchical advantage α
- Error bars: ±1 SD across 10 seeds
- Fit: Test linear, logarithmic, and quadratic models

**Figure 2: Sustained Population Size vs $n_{pop}$**
- X-axis: $n_{pop}$
- Y-axis: Mean sustained population (normalized by $N_{total}$)
- Compare to single-scale baseline (horizontal line at expected value)

**Figure 3: Migration Flow vs $n_{pop}$**
- X-axis: $n_{pop}$
- Y-axis: Mean inter-population migrations per cycle
- Hypothesis: Migration flow increases with more populations (more rescue opportunities)

---

## Expected Results

### Hypothesis-Specific Predictions

**If H1 (Monotonic Increase):**
- α increases monotonically: $\alpha_1 < \alpha_2 < \alpha_5 < \alpha_{10} < \alpha_{20} < \alpha_{50}$
- Linear or logarithmic fit best
- Implication: More redundancy always beneficial (no overhead penalty)

**If H2 (Diminishing Returns):**
- α increases but saturates: $\alpha_{20} \approx \alpha_{50}$ (plateau)
- Logarithmic fit best: $\alpha \sim \log(n_{pop})$
- Implication: Marginal benefit decreases, but overhead doesn't dominate

**If H3 (Optimal Population Count):**
- α peaks at intermediate $n_{pop}$: e.g., $\alpha_{10}$ or $\alpha_{20}$ highest
- Quadratic fit best: $\alpha \sim n_{pop} - c \cdot n_{pop}^2$ (inverted U)
- Implication: Trade-off exists, optimal redundancy balances efficiency vs overhead

**If H4 (Threshold Behavior):**
- α jumps at critical $n_{pop}$: $\alpha_1 \approx 1$, $\alpha_2 >> 1$
- Step function or sigmoid fit best
- Implication: Phase transition, hierarchical advantage emerges at $n_{pop} \geq 2$

### Baseline Expectations

**$n_{pop} = 1$ (C187-1):**
- No hierarchical structure, no rescue
- Expect α ≈ 1 (no advantage)
- Replicates V8 edge case behavior

**$n_{pop} = 10$ (C187-10):**
- Replicates V1-V5 baseline
- Expect α ≈ 600 (607× from Paper 8)
- Validates consistency with C186

**$n_{pop} = 50$ (C187-50):**
- Tests upper limit of redundancy benefit
- If H1: α >> 600
- If H2: α ≈ 600 (saturated)
- If H3: α < 600 (overhead penalty)

---

## Implementation Plan

### Script Structure

**Filename:** `c187_population_count_variation.py`

**Main Loop:**
```python
for n_pop in [1, 2, 5, 10, 20, 50]:
    for seed in range(10):
        # Initialize hierarchical system
        populations = [Population(n_init=20) for _ in range(n_pop)]

        # Run 3000-cycle experiment
        for cycle in range(3000):
            # Spawn logic (per population, f_intra=2.0%)
            for pop in populations:
                if random() < 0.02:  # 2.0%
                    pop.spawn_agent()

            # Migration logic (per system, f_migrate=0.5%)
            if n_pop > 1 and random() < 0.005:  # 0.5%
                source = random_choice(populations)
                target = random_choice([p for p in populations if p != source])
                if source.agents:
                    agent = random_choice(source.agents)
                    source.remove(agent)
                    target.add(agent)

            # Agent death (stochastic)
            for pop in populations:
                for agent in pop.agents:
                    if random() < death_rate:
                        pop.remove(agent)

        # Record final population
        total_population = sum(len(pop.agents) for pop in populations)
        basin = "A" if total_population >= n_pop * 20 else "B"

        # Save result
        save_result({
            "n_pop": n_pop,
            "seed": seed,
            "final_population": total_population,
            "basin": basin
        })
```

**Defensive Edge Case Handling:**
- Skip migration when $n_{pop} = 1$ (no valid targets)
- Log warning if unexpected behavior (e.g., negative populations)

### Output Format

**JSON Result File:** `c187_results.json`

```json
{
  "campaign": "C187",
  "title": "Population Count Variation",
  "date": "2025-11-08",
  "conditions": [
    {
      "n_pop": 1,
      "seeds": 10,
      "results": [
        {"seed": 0, "final_population": 18, "basin": "B"},
        {"seed": 1, "final_population": 22, "basin": "A"},
        ...
      ],
      "mean_population": 19.5,
      "sd_population": 3.2,
      "basin_a_percent": 50
    },
    ...
  ],
  "hierarchical_advantage": {
    "n_pop=1": 1.02,
    "n_pop=2": 45.3,
    "n_pop=5": 320.1,
    "n_pop=10": 607.2,
    "n_pop=20": 890.5,
    "n_pop=50": 1120.3
  },
  "best_fit_model": "logarithmic"
}
```

---

## Integration with Paper 8

### If Integrated into Paper 8:

**New Section:** 3.7 Population Count Scaling (after current Results sections)

**Key Additions:**
- Figure 4: Hierarchical advantage α vs $n_{pop}$ (C187 results)
- Discussion 4.8: Population count scaling mechanisms
- Extended abstract mention: "...tested across population counts $n_{pop} = 1$ to 50..."

### If Separate Publication (Paper 8B):

**Title:** "Scaling Hierarchical Advantage with Population Count in Nested Resonance Memory Systems"

**Focus:**
- Quantify relationship between $n_{pop}$ and α
- Test competing hypotheses (monotonic, diminishing, optimal, threshold)
- Identify optimal population count for hierarchical efficiency

**Target:** Same as Paper 8 (PLOS Computational Biology primary)

---

## Timeline

**Execution:** ~3 hours (60 experiments @ ~160 min total runtime)
**Analysis:** ~2 hours (statistical tests, figure generation)
**Integration:** ~1-2 hours (if adding to Paper 8) or ~4-6 hours (if separate Paper 8B)

**Total:** 6-11 hours from execution to publication-ready results

---

## Success Criteria

**Experiment succeeds if:**
1. ✅ All 60 experiments complete (6 conditions × 10 seeds)
2. ✅ $n_{pop} = 1$ replicates V8 behavior (α ≈ 1)
3. ✅ $n_{pop} = 10$ replicates V1-V5 baseline (α ≈ 600)
4. ✅ Clear trend emerges (monotonic, logarithmic, optimal, or threshold)
5. ✅ Results publishable (extend Paper 8 or standalone Paper 8B)

**Experiment fails if:**
- ❌ Edge cases (n_pop=1, n_pop=50) cause system crashes
- ❌ No consistent pattern in α vs $n_{pop}$ relationship
- ❌ Results contradict Paper 8 baseline (n_pop=10 doesn't replicate)

---

## Notes

**Design Rationale:**
- Directly extends Paper 8 findings to unexplored parameter space
- Tests theoretical predictions from Discussion section 4.6
- Provides quantitative scaling law for hierarchical advantage

**Novel Contribution:**
- First systematic study of population count scaling in hierarchical NRM
- Could establish design principles for optimal hierarchical organization

**Generalizability:**
- Results apply to any hierarchical multi-agent system with rescue dynamics
- Informs distributed computing, organizational design, ecological metapopulations

---

**Status:** Experimental design complete, ready for implementation
**Next Actions:** Implement `c187_population_count_variation.py`, execute experiment, analyze results
**Expected Completion:** 6-11 hours total (execution + analysis + integration)

**Research is perpetual. Next experiment designed. Implementation awaits.**
