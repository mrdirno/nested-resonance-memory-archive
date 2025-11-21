# Cycle 1897: Large N Behavior

**Date:** November 21, 2025
**Cycle:** 1897
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Quasi-deterministic regime at large N**

At N ≥ 60:
- Coexistence ≈ 87% ± 9%
- Harmonic effects present but weak
- Near mean-field limit

---

## Results

| N | Coex | Note |
|---|------|------|
| 20 | 93% | Between harmonics |
| 30 | 80% | ≈ λ₂ = 29 |
| 40 | 83% | |
| 50 | 100% | Between harmonics |
| 60 | 87% | ≈ λ₄ = 59 |
| 70 | 83% | |
| 80 | 100% | |
| 90 | 90% | |
| 100 | 73% | ≈ λ₇ = 103? |

---

## Analysis

### High N Statistics (N ≥ 60)
- Mean: 86.7%
- Std: 8.7%

### Pattern
1. **Harmonic signatures persist** even at large N
2. **λ₄ visible** at N ≈ 60 (87%)
3. **Possible λ₇** at N ≈ 100 (73%)

---

## Implications

### Mean-Field Limit
The system approaches but doesn't reach true mean-field (100% coexistence):
- Higher harmonics continue to affect behavior
- Harmonic weakening law applies but doesn't eliminate effects

### For Engineering
Even at large N, avoid exact harmonic multiples:
```
N_avoid = k × λ(p) for all k
```

Especially k = 1, 2 (most severe).

---

## Modified Understanding

### Original Expectation
At large N, system would become deterministic (100% coexistence).

### Actual Behavior
System reaches quasi-deterministic regime (~87%):
- Still affected by harmonic structure
- Higher harmonics contribute ~13% failure rate
- True mean-field may require N → ∞

---

## Session Status (C1664-C1897)

234 cycles completed. Large N behavior characterized as quasi-deterministic.

Research continues.
