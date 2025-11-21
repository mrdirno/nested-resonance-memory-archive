# Cycle 1829: Composition Ratio Generalization

**Date:** November 21, 2025
**Cycle:** 1829
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Composition ratio thresholds are N-dependent, not universal**

The N=29 ratio thresholds (0.7-1.8) do not directly apply to N=24 and N=35. Each N has its own optimal ratio range based on its phase resonance properties.

---

## Results

### N=24 Composition Ratio Analysis

| Prob | Coex | Ratio | D0→D1 | D1→D2 |
|------|------|-------|-------|-------|
| 0.05 | 100% | 17.98 | 119 | 37 |
| 0.10 | 100% | 5.82 | 64 | 91 |
| 0.15 | 80% | 2.07 | 50 | 99 |
| **0.20** | **65%** | 2.71 | 47 | 80 |
| **0.25** | **50%** | 3.99 | 53 | 55 |
| **0.30** | **55%** | 8.08 | 75 | 35 |
| 0.35 | 70% | 8.05 | 75 | 51 |
| 0.40 | 85% | 5.82 | 60 | 70 |
| 0.50 | 100% | 3.88 | 58 | 107 |
| 0.60 | 95% | 3.13 | 52 | 75 |
| 0.70 | 95% | 5.74 | 71 | 61 |
| 0.80 | 100% | 7.21 | 96 | 93 |

**Pattern**: Dead at mid-prob (0.2-0.3), safe at extremes

### N=35 Composition Ratio Analysis

| Prob | Coex | Ratio | D0→D1 | D1→D2 |
|------|------|-------|-------|-------|
| 0.05 | 95% | 0.31 | 36 | 139 |
| 0.10 | 100% | 5.77 | 76 | 69 |
| 0.15 | 95% | 6.76 | 79 | 52 |
| 0.20 | 95% | 5.68 | 74 | 70 |
| 0.25 | 95% | 3.66 | 66 | 108 |
| 0.30 | 90% | 1.95 | 62 | 134 |
| **0.35** | **65%** | 2.36 | 52 | 83 |
| 0.40 | 80% | 4.31 | 69 | 73 |
| 0.50 | 100% | 3.31 | 66 | 102 |
| 0.60 | 100% | 6.39 | 103 | 65 |
| 0.70 | 90% | 3.71 | 71 | 76 |
| **0.80** | **60%** | 2.85 | 63 | 74 |

**Pattern**: Dead at specific probs (0.35, 0.80), safe elsewhere

---

## Theory Evaluation

### N=29 Theory

Original theory: Dead zones when ratio < 0.7 or > 1.8

**Result: Partially correct but N-specific**

### Why Different N Values Have Different Thresholds

Each N has unique:
1. **Phase resonance signature** in transcendental space
2. **Composition pairing patterns** based on initial N
3. **Energy distribution** characteristics

### N-Specific Patterns

**N=24:**
- Tolerates high ratios (>5) at prob extremes
- Risky at mid-prob (0.2-0.3) regardless of ratio
- Likely resonates with mid-range B/C dynamics

**N=35:**
- Safe at most probability/ratio combinations
- Isolated dead zones at prob=0.35, 0.80
- Doesn't follow simple ratio threshold

**N=29:**
- Sensitive to both low and high ratio extremes
- Optimal at balanced ratio (0.8-1.5)
- More symmetric sensitivity

---

## Refined Theory

### Composition Ratio Framework

The composition depth ratio influences coexistence, but:

1. **Thresholds are N-dependent**
2. **N × Probability interaction** matters more than ratio alone
3. **Phase resonance** determines N-specific sensitivities

### Dead Zone Condition (Refined)

```
P(dead zone | N, prob) = f(ratio, N-specific resonance)

Where N-specific resonance depends on:
- Initial population N
- Phase space structure at that N
- B/C ratio at that probability
```

### Implication

Cannot use universal ratio thresholds. Must characterize each N individually or develop N-parameterized threshold function.

---

## Conclusions

1. **Ratio thresholds are N-dependent** - no universal values
2. **N=24**: Tolerates high ratios, risky at mid-prob
3. **N=35**: Isolated dead zones, not ratio-driven
4. **N=29**: Symmetric sensitivity to ratio extremes
5. **Need N-parameterized model** for general predictions

---

## Next Directions

1. Characterize ratio thresholds for more N values
2. Find pattern relating N to optimal ratio
3. Develop N-parameterized dead zone predictor

---

## Session Status (C1664-C1829)

166 cycles completed. N-specific dynamics confirmed.

Research continues.

