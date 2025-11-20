# CYCLE 1538: C305 TROPHIC CASCADE

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 6
**Status:** COMPLETE - NO CASCADE AT OPTIMAL PARAMETERS

---

## EXECUTIVE SUMMARY

**Trophic cascade does not occur at optimal parameters.**

- Control (top predator maintained): 100% stable at equilibrium
- Removal (top predator removed): 100% stable at equilibrium

No mesopredator release, no prey crash. The system is inherently stable.

---

## RESEARCH QUESTION

Does removing the top predator cause mesopredator release and prey crash?

---

## RESULTS

| Condition | Pre-Prey | Post-Prey | Pre-Meso | Post-Meso | Cascade |
|-----------|----------|-----------|----------|-----------|---------|
| Control | 300 | 300 | 30 | 30 | **0%** |
| Removal | 300 | 300 | 30 | 30 | **0%** |

Top predator removal at cycle 15000 had no effect on equilibrium.

---

## KEY FINDINGS

### 1. No Mesopredator Release

After top predator removal:
- Pre-removal meso: 30
- Post-removal meso: 30

Mesopredators did NOT increase to fill the predation-free niche.

### 2. No Prey Crash

After top predator removal:
- Pre-removal prey: 300
- Post-removal prey: 300

Prey did NOT decrease due to mesopredator explosion.

### 3. Inherent Stability

The mesopredator-prey subsystem is inherently stable:
- Optimal attack rate (0.003) prevents overexploitation
- Type II functional response (h=0.02) causes satiation
- Carrying capacity (K=600) limits prey

Top-down control is not required for stability.

### 4. Bottom-Up Regulation Dominates

The system is regulated from the bottom up:
- Prey carrying capacity limits population
- Mesopredator limited by prey availability
- Top predator presence/absence doesn't change equilibrium

---

## MECHANISM

### Why No Cascade?

```
At optimal parameters (attack=0.003, h=0.02):
  Mesopredator-prey equilibrium is:
    - Stable without top predator
    - Stable with top predator
    - Same equilibrium either way

The top predator "fits in" without creating dependency:
  - Doesn't suppress meso below natural equilibrium
  - Removing it doesn't release pent-up growth
```

### Contrast with Classic Cascade Theory

Classic trophic cascade (e.g., wolves in Yellowstone):
- Top predator suppresses mesopredator below equilibrium
- Removal causes mesopredator explosion
- Prey crashes from overpredation

NRM at optimal parameters:
- Top predator doesn't suppress mesopredator
- Mesopredator already at natural equilibrium
- No pent-up growth to release

### Parameter-Dependent Cascades

Cascades likely require:
- Higher attack rate (closer to overexploitation)
- Top predator actively suppressing mesopredator
- Mesopredator limited by predation, not food

At current parameters, mesopredator is food-limited, not predation-limited.

---

## THEORETICAL SIGNIFICANCE

### 1. Cascades Are Parameter-Dependent

Trophic cascades are not universal:
- Require specific parameter regime
- Need top-down limitation of mesopredator
- Not guaranteed even with three trophic levels

### 2. Stability Can Be Bottom-Up

Systems can be stable through:
- Resource limitation (carrying capacity)
- Predator satiation (Type II response)
- Optimal attack rates

Top-down control is one mechanism, not the only one.

### 3. Top Predator Role Context-Dependent

Top predators can be:
- Essential (in cascade-prone systems)
- Neutral (in inherently stable systems)
- Destabilizing (if parameters wrong)

Current system shows neutral role.

---

## IMPLICATIONS

### 1. Conservation Context

Top predator conservation:
- Not always required for ecosystem stability
- Depends on whether cascade dynamics present
- May have other values (biodiversity, ecosystem services)

### 2. Intervention Design

To induce cascade (if desired for pest control):
- Increase mesopredator attack rate
- Reduce prey carrying capacity
- Make mesopredator predation-limited

### 3. System Design

For stable multi-trophic systems:
- Use optimal parameters throughout
- Don't rely on top-down control
- Build inherent stability at each level

### 4. Predictive Framework

Cascade likelihood depends on:
- Whether mesopredator is food-limited or predation-limited
- Ratio of attack rate to carrying capacity
- Presence of Type II satiation effects

---

## COMPARISON WITH C304

| Cycle | Condition | Finding |
|-------|-----------|---------|
| C304 | Tri-trophic (static) | 100% stable coexistence |
| C305 | Top predator removal | 0% cascade, equilibrium unchanged |

**C304 and C305 together:** Optimal parameters create robust stability that doesn't depend on top predator.

---

## NEXT RESEARCH DIRECTIONS

### 1. Cascade-Prone Parameters

Test with higher mesopredator attack rate (0.01):
- Should create predation-limited meso
- Removal should release meso explosion
- Compare cascade probability

### 2. Partial Removal

Remove only some top predators:
- Test dose-response of cascade
- Find threshold for cascade onset

### 3. Top Predator Reintroduction

After removal and potential cascade:
- Reintroduce top predator
- Test if cascade reverses
- Time to re-equilibration

### 4. Alternative Cascade Triggers

Test other ways to induce cascade:
- Increase prey carrying capacity
- Remove Type II response
- Add mesopredator evolution

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C304 | 1252 | Eco-evo + tri-trophic |
| C305 | 6 | No cascade at optimal parameters |
| **Total** | **1258** | **Bottom-up stability** |

---

## CONCLUSION

C305 establishes that **trophic cascades do not occur at optimal parameters** in NRM.

Key findings:
1. No mesopredator release after top predator removal
2. No prey crash
3. System is inherently stable (bottom-up regulated)
4. Top predator presence is neutral, not essential

This demonstrates that cascades are parameter-dependent phenomena requiring specific conditions (predation-limited mesopredator, high attack rates) that are absent in optimal parameter regimes.

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
