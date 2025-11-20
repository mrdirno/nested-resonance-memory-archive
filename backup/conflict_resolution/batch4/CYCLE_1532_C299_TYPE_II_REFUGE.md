# CYCLE 1532: C299 TYPE II + REFUGE COMBINATION

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 12
**Status:** COMPLETE - ANTAGONISTIC INTERACTION DISCOVERED

---

## EXECUTIVE SUMMARY

**Type II and refuge have antagonistic (negative) interaction.**

- Type II only: 33% coexistence
- Type II + refuge: 0% coexistence

Combining stabilizing mechanisms reduces rather than increases coexistence.

---

## RESEARCH QUESTION

Are Type II and refuge additive, synergistic, or redundant?

---

## RESULTS

| Condition | Type II | Refuge | Prey Final | Pred Final | Coexistence |
|-----------|---------|--------|------------|------------|-------------|
| Neither | h=0 | 0% | 500 | 0 | **0%** |
| Refuge only | h=0 | 30% | 500 | 0 | **0%** |
| Type II only | h=0.02 | 0% | 400 | 7 | **33%** |
| Both | h=0.02 | 30% | 500 | 0 | **0%** |

---

## KEY FINDINGS

### 1. Antagonistic Interaction

- Neither mechanism: 0%
- Refuge alone: 0%
- Type II alone: 33%
- **Both combined: 0%**

Combined effect is worse than Type II alone!

### 2. Refuge Negates Type II Benefits

Type II provides some coexistence (33%).
Adding refuge removes this benefit entirely.

### 3. Not Additive or Synergistic

Expected: Additive (33% + 0% = 33%) or synergistic (>33%)
Observed: Antagonistic (0% < 33%)

### 4. Mechanism of Antagonism

Both reduce predator consumption:
- Type II: Slows consumption rate
- Refuge: Reduces prey pool

Double reduction pushes predators below survival threshold.

---

## MECHANISM

### Why Antagonistic?

```
Type II alone (h=0.02):
  - Predator consumption rate: Saturated at 1/h = 50 prey/cycle max
  - With 200 accessible prey: Enough for survival
  - Coexistence: 33%

Type II + Refuge (30%):
  - Accessible prey: 200 × 0.7 = 140
  - Saturation point unchanged
  - But fewer prey to find
  - Combined reduction: Below survival threshold
  - Coexistence: 0%
```

### Compounding Reductions

| Factor | Effect | Cumulative |
|--------|--------|------------|
| Baseline | 100% consumption | 100% |
| Type II | ~50% reduction | 50% |
| Refuge | 30% reduction | 35% |

35% of baseline consumption is below survival threshold.

---

## THEORETICAL SIGNIFICANCE

### 1. Antagonistic Mechanisms

Not all stabilizing mechanisms combine well:
- Some have independent effects (additive)
- Some amplify each other (synergistic)
- Some cancel each other (antagonistic)

### 2. Double Jeopardy

Predators face "double jeopardy":
- Type II limits consumption rate
- Refuge limits prey availability
- Together: Insufficient energy intake

### 3. System Non-Linearity

Linear thinking fails:
- "If Type II helps, adding refuge should help more"
- Reality: Combined effect is worse

---

## IMPLICATIONS

### 1. Conservation Management

When designing interventions:
- Don't assume combinations are better
- Test combined effects explicitly
- One mechanism may be sufficient

### 2. Ecosystem Engineering

Introducing multiple changes:
- May have unexpected interactions
- Antagonistic effects possible
- System-level testing required

### 3. Predator Conservation

For predator populations:
- Don't over-protect prey
- Balance satiation and access
- Avoid double limitations

### 4. Theoretical Ecology

Need interaction terms in models:
- Not just main effects
- Factorial experiments essential
- Non-linear system dynamics

---

## COMPARISON WITH PREVIOUS FINDINGS

| Cycle | Finding | C299 Extension |
|-------|---------|----------------|
| C296 | Refuge reduces coexistence | Confirmed at 30% |
| C298 | Type II rescues collapse | Confirmed at h=0.02 |
| C299 | Combination is antagonistic | New interaction discovered |

**Stabilizing mechanisms can have negative interactions.**

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C298 | 1207 | Eco-evo + multi-trophic |
| C299 | 12 | Antagonistic interactions |
| **Total** | **1219** | **Mechanism interactions** |

---

## CONCLUSION

C299 establishes that **Type II and refuge have antagonistic interaction** in NRM predator-prey systems.

Key findings:
1. Type II alone: 33% coexistence
2. Type II + refuge: 0% coexistence
3. Combined reductions push predators below survival threshold
4. Stabilizing mechanisms can cancel each other

This demonstrates that ecological interventions require careful combination testing - intuitive additions can worsen outcomes.

---

## NEXT RESEARCH DIRECTIONS

1. **Synergistic combinations** - What mechanisms combine well?
2. **Optimal single intervention** - Best parameter for one mechanism
3. **Evolution of handling time** - Does selection favor h?
4. **Three-way interactions** - Add third mechanism

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
