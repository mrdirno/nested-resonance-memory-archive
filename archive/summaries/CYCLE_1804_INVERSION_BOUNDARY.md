# Cycle 1804: Pattern Inversion Boundary

**Date:** November 21, 2025
**Cycle:** 1804
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Fine-grained mapping of pattern inversion boundary.

**FINDING: Crossover at prob ≈ 0.22, gradual transition 0.15-0.30**

---

## Results

| Prob | N=29 | N=35 | Diff | Status |
|------|------|------|------|--------|
| 0.10 | 57% | 97% | 40pp | NORMAL |
| 0.15 | 80% | 100% | 20pp | transition |
| 0.18 | 80% | 100% | 20pp | transition |
| 0.20 | 83% | 93% | 10pp | transition |
| 0.22 | 93% | 90% | -3pp | transition |
| 0.25 | 97% | 87% | -10pp | transition |
| 0.28 | 100% | 90% | -10pp | transition |
| 0.30 | 100% | 87% | -13pp | INVERTED |
| 0.35 | 100% | 67% | -33pp | INVERTED |

---

## Analysis

### Transition Structure

1. **Normal regime (prob ≤ 0.10):** Strong pattern (40pp+)
2. **Weakening (0.15-0.20):** Pattern strength decreases
3. **Crossover (prob ≈ 0.22):** N=29 ≈ N=35
4. **Inversion (0.25-0.30):** Pattern reverses
5. **Strong inversion (0.35+):** -33pp difference

### Crossover Point

At prob = 0.22:
- N=29: 93% coexistence
- N=35: 90% coexistence
- Difference: -3pp (essentially equal)

This is where the two competing mechanisms balance.

### Inversion Strength

The inverted pattern strengthens with probability:
- 0.25: -10pp
- 0.30: -13pp
- 0.35: -33pp

Suggests the inverted mechanism dominates at high reproduction rates.

---

## Mechanism Hypothesis

### Two Competing Wavelengths

**Low probability (dominates at prob < 0.22):**
- Pairing-driven dynamics
- Dead zones at N = 29, 43, 58, ...
- λ ≈ 14.48

**High probability (dominates at prob > 0.22):**
- Reproduction-driven dynamics
- Dead zones shift to different N values
- Possibly different wavelength

### Phase Competition

The system has two interference patterns:
1. **Pairing interference:** Creates original dead zones
2. **Reproduction interference:** Creates inverted pattern

At prob ≈ 0.22, these patterns destructively interfere, neutralizing the effect.

---

## Implications

### Parameter Sensitivity

Reproduction probability is a **critical parameter** that determines:
- Which interference pattern dominates
- Whether dead zones exist at N=29 or N=35
- Overall system behavior

### Design Guidelines

For original dead zone pattern:
- Use prob ≤ 0.15

For inverted pattern:
- Use prob ≥ 0.30

For no pattern (neutral):
- Use prob ≈ 0.22

---

## Conclusions

1. **Crossover at prob ≈ 0.22**
2. **Gradual transition (0.15-0.30)**
3. **Two competing mechanisms**
4. **Strong inversion at prob ≥ 0.35**
5. **Critical design parameter**

---

## Session Status (C1664-C1804)

141 cycles completed. Research continues.

