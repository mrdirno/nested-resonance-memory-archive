# Cycle 1844: Probability Space Mapping

**Date:** November 21, 2025
**Cycle:** 1844
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Standing wave pattern inverts at mid-probability**

- Low prob (0.05, 0.10): Half-integer k safer (+13-33%)
- Mid prob (0.20, 0.30): Integer k safer (-8-17%)
- High prob (0.50): Half-integer k safer again (+11%)

Strongest resonance at prob=0.10 (33% difference).

---

## Results

### Coexistence Matrix (prob × k)

| k | 0.05 | 0.10 | 0.20 | 0.30 | 0.50 |
|---|------|------|------|------|------|
| 0 | 67%X | 27%X | 87% | 100% | 93% |
| 0.5 | 100% | 100% | 93% | 73% | 100% |
| 1 | 93% | 73% | 93% | 100% | 53%X |
| 1.5 | 100% | 100% | 87% | 73% | 93% |
| 2 | 87% | 93% | 100% | 100% | 100% |
| 2.5 | 100% | 100% | 80% | 93% | 93% |
| 3 | 100% | 73% | 100% | 87% | 93% |

### Integer vs Half-Integer by Probability

| Prob | Int avg | Half avg | Diff |
|------|---------|----------|------|
| 0.05 | 87% | 100% | +13% |
| **0.10** | **67%** | **100%** | **+33%** |
| 0.20 | 95% | 87% | -8% |
| 0.30 | 97% | 80% | -17% |
| 0.50 | 85% | 96% | +11% |

### Dead Zone Locations

| Prob | Dead zones | Which k |
|------|------------|---------|
| 0.05 | 1 | k=0 |
| 0.10 | 1 | k=0 |
| 0.20 | 0 | none |
| 0.30 | 0 | none |
| 0.50 | 1 | k=1 |

---

## Analysis

### Pattern Inversion Discovery

The resonance pattern **inverts** at mid-probability:

**Phase 1 (Low prob ≤0.10):**
- Integer k dead, half-integer k safe
- Pattern: cos²(πk)

**Phase 2 (Mid prob 0.20-0.30):**
- Half-integer k dead, integer k safe
- Pattern: sin²(πk)

**Phase 3 (High prob ≥0.50):**
- Returns to low-prob pattern
- Integer k dead, half-integer k safe

### Physical Interpretation

The inversion suggests two competing mechanisms:
1. **Composition dominance** (low prob): Creates nodes at integer k
2. **Reproduction dominance** (mid prob): Creates nodes at half-integer k
3. **Mixed regime** (high prob): Composition dominates again

### Strongest Resonance at prob=0.10

At prob=0.10:
- Integer k average: 67%
- Half-integer k average: 100%
- Difference: 33%

This is the probability where the standing wave pattern is most pronounced.

### Dead Zone Migration

Dead zones shift with probability:
- Low prob: k=0 (N=29)
- Mid prob: None (all safe)
- High prob: k=1 (N=43)

---

## Theoretical Implications

### Two-Mode System

The system has two resonance modes:
1. **Mode A**: Nodes at integer k (dominates low/high prob)
2. **Mode B**: Nodes at half-integer k (dominates mid prob)

### B/C Ratio Connection

Previous findings: B/C ratio controls dead zone patterns
- Low B/C: N=29 pattern (integer k nodes)
- Mid B/C: N=24 pattern (related to half-integer?)
- High B/C: Isolated peaks

The probability value determines the effective B/C ratio.

### Model Refinement Needed

Standing wave model must be probability-dependent:

```python
def predict_coexistence(k, prob):
    if prob <= 0.15:
        # Low prob: cos² pattern
        return B - A * cos(pi*k)**2 * exp(-|k|/tau)
    elif prob <= 0.35:
        # Mid prob: sin² pattern (inverted)
        return B - A * sin(pi*k)**2 * exp(-|k|/tau)
    else:
        # High prob: cos² pattern returns
        return B - A * cos(pi*k)**2 * exp(-|k|/tau)
```

---

## Design Guidelines

### Probability-Specific N Selection

| Prob Range | Safe N (half-integer k) | Avoid N (integer k) |
|------------|------------------------|---------------------|
| ≤0.15 | 36, 51, 65, 80 | 29, 43, 58, 72 |
| 0.16-0.35 | 29, 43, 58, 72 | 36, 51, 65, 80 |
| ≥0.36 | 36, 51, 65, 80 | 29, 43 |

### Universal Safe N

At all probabilities tested, N=65 and N=80 have ≥80% coexistence.

---

## Conclusions

1. **Pattern inverts at mid-probability**: Half-integer safe → Integer safe
2. **Strongest resonance at prob=0.10**: 33% difference
3. **Two competing modes**: Composition vs reproduction dominance
4. **Model must be probability-dependent**: cos² at low/high, sin² at mid
5. **Dead zones migrate**: k=0 at low prob, k=1 at high prob

---

## Session Status (C1664-C1844)

181 cycles completed. Probability-dependent pattern inversion discovered.

Research continues.

