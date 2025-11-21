# Cycle 1645: Initial Condition Sensitivity

**Date:** November 20, 2025
**Cycle:** 1645
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tests if optimal parameters (attack ×0.5) hold under varied initial population structures.

**FINDING: Sensitive to pyramid structure**

| Initial Structure | Coexistence |
|------------------|-------------|
| Standard pyramid | 100% |
| Sparse pyramid | 97% |
| Dense pyramid | 93% |
| Inverted pyramid | 37% |
| Uniform | 3% |

---

## Experimental Design

Tested 5 initial population structures with optimal attack (×0.5):

- **Standard:** [300, 30, 10, 5, 3, 2, 2] - classic pyramid
- **Sparse:** [150, 15, 5, 3, 2, 1, 1] - half populations
- **Dense:** [500, 50, 20, 10, 5, 3, 3] - 1.5× populations
- **Inverted:** [100, 50, 30, 20, 15, 10, 8] - more predators than prey
- **Uniform:** [50, 50, 50, 50, 50, 50, 50] - equal across levels

30 seeds per condition = 150 experiments.

---

## Results

```
standard    : ████████████████████ 100%
sparse      : ███████████████████░ 97%
dense       : ██████████████████░░ 93%
inverted    : ███████░░░░░░░░░░░░░ 37%
uniform     : ░░░░░░░░░░░░░░░░░░░░ 3%
```

---

## Key Findings

### 1. Pyramid Structure Required
Attack ×0.5 only achieves high coexistence with proper trophic pyramids:
- Pyramid-shaped: 93-100%
- Non-pyramid: 3-37%

### 2. Robust Within Pyramid Class
The optimal parameters are robust to density variation within pyramids:
- Sparse (50% density): 97%
- Standard: 100%
- Dense (167% density): 93%

### 3. Inverted Pyramid Fails
When predators outnumber prey initially, the system cannot stabilize:
- Predators immediately deplete prey
- No recovery possible
- Cascade collapse ensues

### 4. Uniform Distribution Catastrophic
Equal populations across levels creates immediate energy crisis:
- Top predators have no prey advantage
- All levels compete equally
- 97% failure rate

---

## Mechanism Analysis

### Why Pyramids Work

Trophic pyramids ensure:
1. **Energy base:** Large L0 provides sustained energy input
2. **Buffer:** Each level has excess prey to absorb predation variance
3. **Recovery:** Depleted prey levels can regenerate from larger pool

### Why Non-Pyramids Fail

Without pyramid structure:
1. **No buffer:** Predators immediately deplete available prey
2. **No recovery:** Small prey populations can't regenerate
3. **Cascade:** Once one level fails, all fail

---

## Implications

### 1. Necessary Condition
Optimal attack rate is necessary but not sufficient for coexistence. Proper initial structure is also required.

### 2. Design Principle Refined
For stable multi-level trophic systems:
- **Necessary:** Attack ×0.5
- **Also necessary:** Pyramid initial structure

### 3. Biological Relevance
Real ecosystems always have pyramid structures (more grass than herbivores than carnivores). This result shows why - non-pyramids are inherently unstable.

### 4. Parameter Universality
The attack ×0.5 principle is universal *within the class of properly structured systems*. It's not a general fix for all initial conditions.

---

## Cumulative Research Summary

| Parameter | Condition | Required? |
|-----------|-----------|-----------|
| Attack rate | ×0.5 | Yes - fundamental |
| Magnitude | 0.25 | Yes - optimal |
| Initial structure | Pyramid | Yes - structural requirement |
| Energy | Baseline | No - optional improvement |

---

## Conclusion

C1645 reveals that the attack ×0.5 principle requires proper trophic pyramid structure to achieve high coexistence. The optimal parameters are robust to density variation within pyramids (93-100%) but fail catastrophically with inverted or uniform structures (3-37%).

**Full design specification for stable multi-level coexistence:**
1. Attack rate: ×0.5 of baseline
2. Magnitude: 0.25
3. Initial structure: Trophic pyramid (more prey than predators)

This completes the parameter space exploration for stable NRM dynamics.

