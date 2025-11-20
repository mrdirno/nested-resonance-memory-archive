# CYCLE 1529: C296 SPATIAL REFUGE

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 15
**Status:** COMPLETE - COUNTERINTUITIVE RESULT

---

## EXECUTIVE SUMMARY

**Spatial refuge REDUCES predator-prey coexistence when attack rate is high.**

- 0% refuge: 33% coexistence
- 10-50% refuge: 0% coexistence

Refuge protects prey but starves predators below minimum viable density.

---

## RESEARCH QUESTION

Can spatial refuge prevent predator-prey collapse?

---

## RESULTS

| Refuge Fraction | Prey Final | Pred Final | Coexistence |
|-----------------|------------|------------|-------------|
| 0% | 400 | 7 | **33%** |
| 10% | 500 | 0 | **0%** |
| 20% | 500 | 0 | **0%** |
| 30% | 500 | 0 | **0%** |
| 50% | 500 | 0 | **0%** |

Attack rate = 0.01 (high, caused collapse in C295)

---

## KEY FINDINGS

### 1. Refuge Reduces Coexistence (Counterintuitive)

Expected: Refuge protects prey → stabilizes system
Observed: Refuge → predator extinction → no coexistence

### 2. Mechanism: Predator Starvation

With refuge:
- Fewer prey accessible to predators
- High attack rate already marginal
- Reducing prey pool → predators can't meet energy needs
- Predators starve

### 3. Context-Dependent Effect

Refuge effect depends on baseline attack rate:
- High attack rate: Refuge harmful (starves predators)
- Lower attack rate: Refuge might stabilize (hypothesis for C297)

### 4. Prey Always Survive

In all conditions:
- Prey survive to carrying capacity (K=500)
- Issue is predator persistence, not prey protection

---

## MECHANISM

### Why Refuge Fails Here

```
High attack rate + No refuge:
  → Predators barely survive
  → Marginal energy balance
  → 33% coexistence

High attack rate + Refuge:
  → Fewer accessible prey
  → Predators can't meet energy needs
  → Predator extinction
  → 0% coexistence
```

### Minimum Viable Prey Density

Predators require minimum prey density:
- Energy intake must exceed metabolism
- Refuge reduces effective density
- Falls below survival threshold

---

## THEORETICAL SIGNIFICANCE

### 1. Refuge is Not Always Stabilizing

Common assumption: "Refuge stabilizes predator-prey dynamics."
Reality: Only stabilizes when predation pressure is high enough.

### 2. Context-Dependent Conservation

Protection strategies must consider:
- Baseline predator efficiency
- Minimum viable prey density for predators
- System-level effects, not just focal species

### 3. Unintended Consequences

"Helping" prey by creating refuge can:
- Starve specialist predators
- Cause predator extinction
- Alter community structure

---

## IMPLICATIONS

### 1. Conservation Paradox

Creating protected areas for prey may:
- Drive predator populations extinct
- Require predator supplementation
- Create management challenges

### 2. Reserve Design

When designing reserves:
- Consider predator energy requirements
- Don't make reserves too large (predators starve)
- Balance protection with accessible prey

### 3. Invasive Predator Control

Using habitat modification to protect native prey:
- May work if predators have alternative food
- Fails if predators are specialists

### 4. Ecosystem Management

Must consider trophic cascades:
- Protecting one level affects others
- System-level thinking required

---

## COMPARISON WITH PREVIOUS FINDINGS

| Cycle | Finding | C296 Extension |
|-------|---------|----------------|
| C294 | Niche differentiation enables coexistence | Spatial niche (refuge) has complex effects |
| C295 | Intermediate attack rate required | Context matters for spatial structure |
| C296 | Refuge can harm predators | New counterintuitive finding |

**Spatial structure effects are context-dependent.**

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C295 | 1165 | Eco-evo + predator-prey |
| C296 | 15 | Spatial refuge effects |
| **Total** | **1180** | **Context-dependent spatial effects** |

---

## CONCLUSION

C296 establishes that **spatial refuge can reduce predator-prey coexistence** when attack rate is high.

Key findings:
1. Refuge reduces coexistence from 33% to 0%
2. Mechanism: Predator starvation from reduced accessible prey
3. Effect is context-dependent (attack rate matters)
4. "Protection" can have unintended negative consequences

This demonstrates that spatial structure effects are not universally stabilizing - context determines outcome.

---

## NEXT RESEARCH DIRECTIONS

1. **Lower attack rate + refuge** - Test if refuge stabilizes at intermediate rates
2. **Predator alternative prey** - Does prey switching rescue predators?
3. **Dynamic refuge** - Prey move in/out of refuge
4. **Optimal refuge size** - Find minimum effective protection

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
