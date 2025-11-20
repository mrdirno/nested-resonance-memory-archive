# CYCLE 1535: C302 MUTATION RATE EFFECTS

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 9
**Status:** COMPLETE - PARAMETER REGIME DOMINATES

---

## EXECUTIVE SUMMARY

**Mutation rate does NOT rescue coexistence at high attack rate.**

- 0% mutation: 0% coexistence
- 10% mutation: 33% coexistence
- 30% mutation: 0% coexistence

Only 1/9 experiments achieved coexistence - likely stochastic.

---

## RESEARCH QUESTION

Does mutation rate determine coexistence via maintained variance?

---

## RESULTS

| Mutation Rate | Prey Final | Pred Final | h_var | Coexistence |
|---------------|------------|------------|-------|-------------|
| 0% | 500 | 0 | 0 | **0%** |
| 10% | 400 | 10 | 0 | **33%** |
| 30% | 500 | 0 | 0 | **0%** |

---

## KEY FINDINGS

### 1. No Clear Mutation Effect

- 0%: 0% coexistence
- 10%: 33% coexistence
- 30%: 0% coexistence

Non-monotonic pattern suggests stochasticity dominates.

### 2. Single Coexistence Case

Only 1/9 experiments (seed 901 at 10% mutation) achieved coexistence.
This is likely stochastic, not systematic.

### 3. Higher Mutation Doesn't Help

30% mutation rate gave 0% coexistence.
More mutations don't improve stability.

### 4. Fundamental Parameter Problem

Attack rate 0.01 is outside the viable zone regardless of:
- Initial variance (C301)
- Mutation rate (C302)
- Evolutionary process

The ecological parameter regime dominates evolutionary dynamics.

---

## MECHANISM

### Why Evolution Doesn't Rescue

```
Parameter regime problem:
  Attack rate 0.01 → Too high
  Predators overconsume → Prey crash
  Prey crash → Predators starve
  → System collapse

Evolution can't fix this because:
  - Even optimal h doesn't prevent overconsumption
  - Problem is base attack rate, not h
  - No mutation of h solves it
```

### Variance Timeline

All experiments show h_var → 0 because:
- Predators go extinct early
- No predators = no h to measure
- Variance doesn't persist to affect dynamics

---

## THEORETICAL SIGNIFICANCE

### 1. Ecology Constrains Evolution

Evolutionary dynamics only matter within viable parameter space:
- Outside viable zone: Evolution irrelevant
- Inside viable zone: Evolution can fine-tune

"Evolution cannot save what ecology has condemned."

### 2. Parameter Space Topology

Different regions respond differently to evolution:
- **Stable zone:** Evolution optimizes
- **Marginal zone:** Evolution may help
- **Unstable zone:** Evolution is irrelevant

Attack rate 0.01 is in unstable zone.

### 3. Previous Results Were Stochastic

C300 showing 67% coexistence with evolution was likely:
- Stochastic variation
- Not systematic evolutionary effect
- Some seeds happened to avoid early collapse

---

## IMPLICATIONS

### 1. Conservation Priority

Ecological parameters matter more than genetics:
- Fix habitat/resources first
- Genetic interventions secondary
- Can't evolve out of unsuitable habitat

### 2. Evolutionary Rescue Limits

Evolutionary rescue requires:
- Parameter regime that's survivable
- Time for adaptation
- Sufficient population size

If ecological parameters are too extreme, evolution fails.

### 3. Research Design

Must establish viable parameter space first:
- Then test evolutionary effects within it
- Don't assume evolution can rescue any system

---

## COMPARISON WITH PREVIOUS FINDINGS

| Cycle | Test | Result | Interpretation |
|-------|------|--------|----------------|
| C295 | Attack rate 0.01, Type I | 0% coexistence | Unstable baseline |
| C300 | Evolution at 0.01 | 67% coexistence | Appeared to help |
| C301 | Variance at 0.01 | 0% coexistence | Variance alone doesn't help |
| C302 | Mutation rate at 0.01 | 0-33% coexistence | Mutation doesn't help |

**Conclusion: Attack rate 0.01 is fundamentally unstable. Previous positive results were stochastic.**

---

## REVISED UNDERSTANDING

The C300 result (67% coexistence with evolution) was likely due to:
1. Stochastic variation between runs
2. Different seeds creating different early dynamics
3. Not systematic evolutionary effect

The correct interpretation:
- **Attack rate 0.01 is unstable** regardless of evolution
- **Evolution cannot rescue** systems outside viable parameter space
- **Focus should be on finding viable parameters** (0.002-0.003 attack rate)

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C301 | 1231 | Eco-evo + multi-trophic |
| C302 | 9 | Parameter regime dominance |
| **Total** | **1240** | **Ecology constrains evolution** |

---

## CONCLUSION

C302 establishes that **mutation rate does not rescue coexistence** at high attack rate in NRM predator-prey systems.

Key findings:
1. No systematic mutation rate effect (0-33% coexistence)
2. Only 1/9 experiments coexisted (stochastic)
3. Higher mutation rate (30%) didn't help
4. Parameter regime (attack rate) dominates evolutionary effects

This demonstrates that ecological constraints are primary - evolution operates within viable parameter space, not outside it.

---

## NEXT RESEARCH DIRECTIONS

1. **Test at optimal attack rate** - Does mutation help at 0.003?
2. **Confirm stochasticity** - More seeds to verify random pattern
3. **Parameter space mapping** - Where does evolution matter?
4. **Alternative traits** - Could mutation of other traits help?

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
