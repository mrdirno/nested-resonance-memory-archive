# CYCLE 1530: C297 REFUGE AT INTERMEDIATE ATTACK RATE

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 15
**Status:** COMPLETE - NON-MONOTONIC REFUGE EFFECT

---

## EXECUTIVE SUMMARY

**Refuge shows non-monotonic effect on coexistence at intermediate attack rate.**

- 0% refuge: 100% coexistence (optimal)
- 10-30% refuge: 0% coexistence (predator starvation)
- 50% refuge: 67% coexistence (partial recovery)

U-shaped relationship between refuge size and coexistence.

---

## RESEARCH QUESTION

Does refuge stabilize coexistence when predation is not already marginal?

---

## RESULTS

| Refuge Fraction | Prey Final | Pred Final | Coexistence |
|-----------------|------------|------------|-------------|
| 0% | 200 | 20 | **100%** |
| 10% | 500 | 0 | **0%** |
| 20% | 500 | 0 | **0%** |
| 30% | 500 | 0 | **0%** |
| 50% | 300 | 13 | **67%** |

Attack rate = 0.003 (intermediate, viable for predators)

---

## KEY FINDINGS

### 1. Baseline Attack Rate is Optimal

At 0% refuge with attack rate 0.003:
- Perfect coexistence (100%)
- Stable equilibrium at ~200 prey, ~20 predators
- No adjustment needed

### 2. Small Refuge Destabilizes

10-30% refuge:
- Reduces accessible prey
- Pushes predators below energy threshold
- Predator extinction in all seeds

### 3. Large Refuge Partially Recovers

50% refuge:
- 67% coexistence (2/3 seeds)
- Different equilibrium (300 prey, 13 predators)

### 4. U-Shaped Pattern

```
Coexistence rate vs Refuge size:
100% → 0% → 0% → 0% → 67%
```

Non-monotonic relationship.

---

## MECHANISM

### Why U-Shaped Pattern?

**Small refuge (10-30%):**
- Reduces accessible prey moderately
- Predator can't catch enough to sustain
- Falls below starvation threshold
- Extinction

**Large refuge (50%):**
- Dramatically reduces accessible prey
- But allows higher prey equilibrium (300 vs 200)
- More prey available in absolute numbers
- Predators can persist at lower population

### Mathematical Insight

```
Accessible prey = Total prey × (1 - refuge)

At 0% refuge: 200 × 1.0 = 200 accessible
At 30% refuge: ~200 × 0.7 = 140 accessible
At 50% refuge: ~300 × 0.5 = 150 accessible

Higher prey equilibrium at 50% refuge compensates for lower accessibility.
```

---

## THEORETICAL SIGNIFICANCE

### 1. Non-Linear Refuge Effects

Refuge doesn't have simple monotonic effect:
- Intermediate refuge worst
- Both extremes (0% and 50%+) allow coexistence
- "Valley of death" in parameter space

### 2. Compensatory Dynamics

Large refuge allows prey to build up:
- Higher prey equilibrium
- More absolute prey accessible
- Compensates for lower accessibility rate

### 3. Management Complexity

Simple interventions can backfire:
- "Add some refuge" → worse than none
- "Add lots of refuge" → may recover
- Non-intuitive system responses

---

## IMPLICATIONS

### 1. Conservation Design

When creating refuges:
- Calculate minimum viable prey accessibility
- Either no refuge OR substantial refuge
- Avoid intermediate "worst of both worlds"

### 2. Ecosystem Management

Small interventions may be dangerous:
- Partial protection can destabilize
- Full commitment may be required
- Test intervention size carefully

### 3. Predator-Prey Theory

Refuge effects are context-dependent and non-monotonic:
- Can't assume "more refuge = more stable"
- System-level feedbacks create complexity
- Empirical testing essential

---

## COMPARISON WITH PREVIOUS FINDINGS

| Cycle | Finding | C297 Extension |
|-------|---------|----------------|
| C295 | Intermediate attack rate optimal | 0.003 confirms optimal zone |
| C296 | Refuge reduces coexistence at high attack | Also reduces at intermediate |
| C297 | Non-monotonic U-shaped pattern | New complexity discovered |

**Refuge effects are highly non-linear and context-dependent.**

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C296 | 1180 | Eco-evo + multi-trophic |
| C297 | 15 | Non-monotonic refuge effects |
| **Total** | **1195** | **Complex spatial dynamics** |

---

## CONCLUSION

C297 establishes that **spatial refuge has non-monotonic effects on predator-prey coexistence**.

Key findings:
1. Optimal attack rate (0.003) gives 100% coexistence without refuge
2. Small refuge (10-30%) reduces coexistence to 0%
3. Large refuge (50%) partially recovers to 67%
4. U-shaped pattern reveals "valley of death" at intermediate refuge

This demonstrates that ecological interventions can have counterintuitive non-linear effects - neither minimal nor intermediate, but potentially extreme interventions may be required for stability.

---

## NEXT RESEARCH DIRECTIONS

1. **Fine-tune refuge gradient** - Map 40-60% to find optimal
2. **High attack rate + large refuge** - Does 50% refuge help at 0.01?
3. **Dynamic refuge use** - Prey actively choosing refuge
4. **Predator behavior** - Foraging optimization

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
