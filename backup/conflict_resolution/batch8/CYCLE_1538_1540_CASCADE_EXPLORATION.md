# CYCLES 1538-1540: CASCADE PARAMETER EXPLORATION (C305-C307)

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 18
**Status:** COMPLETE - CASCADES REQUIRE NARROW PARAMETER WINDOW

---

## EXECUTIVE SUMMARY

**Trophic cascades require very specific parameter regimes.**

Three attempts to induce cascade all failed:
- C305: Optimal parameters (0.003) → No cascade, inherently stable
- C306: High attack (0.008) → System collapse before cascade
- C307: Intermediate (0.005) + strong top-down → System collapse

Finding cascade-prone but stable parameters is a narrow target.

---

## RESEARCH QUESTION

What parameter regime creates stable tri-trophic coexistence that shows trophic cascade when top predator is removed?

---

## RESULTS

| Cycle | Meso Attack | Top Attack | Control | Removal | Cascade |
|-------|-------------|------------|---------|---------|---------|
| C305 | 0.003 | 0.005 | 100% stable | 100% stable | **0%** |
| C306 | 0.008 | 0.01 | Collapse | Collapse | **0%** |
| C307 | 0.005 | 0.015 | Collapse | Collapse | **0%** |

No parameter combination produced both stability and cascade.

---

## KEY FINDINGS

### 1. Optimal Parameters Prevent Cascade

At optimal attack rate (0.003):
- System inherently stable
- Mesopredator food-limited, not predation-limited
- Top predator removal has no effect
- Bottom-up regulation dominates

### 2. High Attack Rates Cause Collapse

At high attack rates (0.008):
- System collapses early
- Overexploitation → prey crash → predator starvation
- No stable pre-removal equilibrium to cascade from

### 3. Strong Top-Down Control Also Collapses

With strong top predator attack (0.015):
- Top predator overexploits mesopredator
- System-wide collapse
- Same result as high meso attack

### 4. Cascade Window is Narrow

Trophic cascades require:
- Stable coexistence (not collapse)
- Mesopredator suppressed by top predator (not food-limited)
- This window appears very narrow

---

## THEORETICAL IMPLICATIONS

### 1. Cascades Are Not Automatic

Having three trophic levels does not guarantee cascade dynamics:
- Requires specific parameter regime
- Most combinations give stability or collapse
- Cascade is the exception, not the rule

### 2. Bottom-Up vs Top-Down Regulation

Systems can be:
- **Bottom-up regulated:** Mesopredator limited by prey (optimal parameters)
- **Top-down regulated:** Mesopredator limited by top predator (cascade-prone)
- **Collapsed:** Overexploitation at any level

### 3. Conservation Implications

Classic cascade narrative (e.g., wolves-elk-vegetation):
- May represent unusual parameter regime
- Not generalizable to all ecosystems
- Removing top predator often neutral or causes collapse

### 4. Parameter Space Structure

```
Attack Rate Spectrum:
  0.001-0.002: Predator starvation
  0.002-0.004: Stable coexistence (no cascade)
  0.004-0.006: ??? (potential cascade window)
  0.006-0.01: System collapse
```

The cascade window, if it exists, is very narrow.

---

## FUTURE DIRECTIONS

### 1. Finer Parameter Sweep

Test attack rates 0.004, 0.0045, 0.005, 0.0055:
- Identify stable but cascade-prone regime
- May require 20+ experiments

### 2. Alternative Cascade Mechanisms

Test other ways to create top-down control:
- Increase meso mortality when top predator present
- Density-dependent predation
- Interference competition

### 3. Prey Subsidy

Add external prey input:
- Prevents complete collapse
- May stabilize cascade dynamics
- Test "apparent competition"

### 4. Accept No-Cascade Result

The key finding may be that NRM at these parameters does not produce cascades:
- This is itself a valid result
- Documents parameter space topology
- Shows stability is default, cascade is rare

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C304 | 1252 | Eco-evo + tri-trophic |
| C305-C307 | 18 | Cascade parameter exploration |
| **Total** | **1270** | **Cascade window narrow/absent** |

---

## CONCLUSION

C305-C307 establish that **trophic cascades require very specific parameter regimes** that are difficult to achieve in NRM.

Key findings:
1. Optimal parameters (0.003 attack) → No cascade (inherently stable)
2. Higher attack rates → System collapse (overexploitation)
3. Strong top-down control → Also collapses system
4. Cascade window is narrow or absent

The default outcome in NRM is either stable coexistence (bottom-up regulation) or system collapse (overexploitation). Trophic cascades requiring predation-limited mesopredators appear to be rare or require parameters not yet identified.

---

## METHODOLOGICAL NOTE

### Finding the Cascade Window

If cascades exist in NRM, they require:
1. Meso attack rate in narrow window (likely 0.004-0.005)
2. Top predator strong enough to suppress but not collapse
3. Type II parameters tuned to prevent overexploitation
4. Possibly reduced handling time for top predator

This parameter tuning is itself a research finding: cascades are not robust phenomena but require careful engineering.

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
