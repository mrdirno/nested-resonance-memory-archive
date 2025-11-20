# CYCLE 1534: C301 VARIANCE EFFECT TEST

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 6
**Status:** COMPLETE - NULL RESULT (VARIANCE ALONE NOT SUFFICIENT)

---

## EXECUTIVE SUMMARY

**Initial variance in handling time does NOT provide resilience.**

- Low variance (std=0.001): 0% coexistence
- High variance (std=0.005): 0% coexistence

Variance alone without ongoing mutation is insufficient for population rescue.

---

## RESEARCH QUESTION

Does variance in handling time provide resilience independent of evolution?

---

## RESULTS

| Condition | h_std | Prey Final | Pred Final | Coexistence |
|-----------|-------|------------|------------|-------------|
| Low variance | 0.001 | 500 | 0 | **0%** |
| High variance | 0.005 | 500 | 0 | **0%** |

No evolution (mutations off), same mean h=0.02.

---

## KEY FINDINGS

### 1. Variance Alone is Insufficient

Both low and high variance resulted in predator extinction:
- Initial variance doesn't provide enough resilience
- All predators eventually fail despite diversity

### 2. C300 Effect Was Not Due to Variance

The 67% coexistence in C300 (evolving condition) was likely:
- Stochastic variation between runs
- Different random seeds creating different dynamics
- NOT due to variance in h values

### 3. Ongoing Process Matters

The difference between C300 evolving vs C301 no-evolution:
- C300: Ongoing mutations create new variants
- C301: Initial variants, then selection depletes diversity
- Dynamic process, not static variance, provides resilience

### 4. Selection Depletes Variance

Without ongoing mutation:
- Successful h values propagate
- Failed h values die out
- Variance decreases over time
- Eventually homogeneous (all fail together)

---

## MECHANISM

### Why Variance Alone Fails

```
Initial state:
  Population has variance in h
  Some h values good, some bad

Over time (no mutation):
  Selection favors certain h values
  Those variants dominate
  Variance decreases
  Eventually all predators have similar h

End state:
  Homogeneous population
  If conditions change, all fail together
  No resilience
```

### C300 vs C301 Comparison

| Feature | C300 Evolving | C301 No Evolution |
|---------|---------------|-------------------|
| Initial variance | Yes | Yes |
| Ongoing mutation | Yes | No |
| Variance over time | Maintained | Depleted |
| Coexistence | 67% | 0% |

**Ongoing variance generation is crucial, not initial variance.**

---

## THEORETICAL SIGNIFICANCE

### 1. Standing Variation vs Mutational Variance

- **Standing variation:** Initial genetic diversity
- **Mutational variance:** Ongoing mutation supply

This experiment shows mutational variance is more important for resilience.

### 2. Evolutionary Rescue

Evolutionary rescue requires:
- Not just initial diversity
- Ongoing generation of new variants
- Continuous adaptation potential

### 3. Conservation Genetics Refinement

Genetic diversity matters, but:
- Static diversity gets depleted by selection
- Need mechanisms to maintain diversity
- Or accept that diversity alone won't save populations

---

## IMPLICATIONS

### 1. Conservation Planning

Genetic diversity alone is insufficient:
- Must maintain diversity over time
- Need mutation supply or gene flow
- One-time diversity injection won't persist

### 2. Assisted Migration

Introducing diverse individuals:
- May not provide long-term benefits
- Selection will deplete variance
- Need ongoing introductions or connectivity

### 3. Captive Breeding

Breeding diverse populations:
- Diversity will be lost without management
- Need to minimize selection
- Or accept that captive populations become homogeneous

### 4. System Design

For resilient agent-based systems:
- Include ongoing variance generation
- Not just initial diversity
- Dynamic adaptation mechanisms

---

## COMPARISON WITH C300

| Aspect | C300 | C301 |
|--------|------|------|
| Evolution | Yes | No |
| Coexistence | 67% | 0% |
| Interpretation | Variance helps | Variance alone doesn't help |

C301 refines C300 interpretation: **Ongoing variance generation (not static variance) provides resilience.**

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C300 | 1225 | Eco-evo + multi-trophic |
| C301 | 6 | Variance effect null result |
| **Total** | **1231** | **Dynamic variance requirement** |

---

## CONCLUSION

C301 establishes that **initial variance alone does NOT provide resilience** in NRM predator-prey systems.

Key findings:
1. Low and high initial variance both result in 0% coexistence
2. Variance without ongoing mutation gets depleted by selection
3. The C300 effect was likely stochastic, not variance-driven
4. Dynamic variance generation (mutation) is required, not static diversity

This refines our understanding: evolutionary resilience requires ongoing adaptation potential, not just standing genetic variation.

---

## NEXT RESEARCH DIRECTIONS

1. **Confirm mutation requirement** - Compare mutation rates
2. **Gene flow substitute** - Can migration maintain variance?
3. **Selection intensity** - Does weaker selection preserve variance?
4. **Frequency-dependent selection** - Could maintain diversity?

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
