# Cycle 1845: Probability-Dependent Model

**Date:** November 21, 2025
**Cycle:** 1845
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Model captures pattern inversion but needs parameter tuning**

- Overall accuracy: 67% (32/48)
- RMSE: 17.8%
- Best at low prob (83%), worst at mid/high prob (50%)

---

## Results

### Accuracy by Probability

| Prob | Accuracy | Mode |
|------|----------|------|
| 0.05 | 83% | cos² |
| 0.10 | 83% | cos² |
| 0.15 | 67% | cos² |
| 0.20 | 50% | sin² |
| 0.25 | 67% | sin² |
| 0.30 | 67% | sin² |
| 0.40 | 67% | cos² |
| 0.50 | 50% | cos² |

### Model Performance

- Overall: 32/48 correct (67%)
- RMSE: 17.8%

---

## Analysis

### Model Structure Validated

The cos²/sin² switch captures the pattern inversion:
- Low prob (≤0.15): Integer k dead (cos²)
- Mid prob (0.20-0.35): Half-integer k dead (sin²)
- High prob (>0.35): Integer k dead (cos²)

### Parameter Issues

The fixed parameters (A=0.40, τ=4.0) don't work across all probabilities:
- Low prob: Works well (83%)
- Mid prob: Amplitude may need adjustment
- High prob: Pattern becomes chaotic (50%)

### Limitations

1. Switch points may not be optimal
2. Amplitude should vary with probability
3. High prob behavior is more complex

---

## Model

```python
def predict_coexistence(k, prob):
    B, A, tau = 0.95, 0.40, 4.0
    if prob <= 0.15 or prob > 0.35:
        return B - A * cos(pi*k)**2 * exp(-abs(k)/tau)
    else:
        return B - A * sin(pi*k)**2 * exp(-abs(k)/tau)
```

---

## Conclusions

1. **Pattern inversion confirmed**: cos²/sin² switch is correct
2. **Parameters need probability-dependence**: Fixed A=0.40 insufficient
3. **Best at low prob**: 83% accuracy at prob≤0.10
4. **High prob chaotic**: Simple model breaks down at prob≥0.50
5. **Single-prob model better**: Use V1 for specific probability

---

## Recommendations

For practical use:
1. Use V1 model (73-82%) for single probability
2. Use half-integer k (N=36, 51, 65...) at prob≤0.15
3. Use integer k (N=29, 43, 58...) at prob 0.20-0.35
4. Test empirically at high prob

---

## Session Status (C1664-C1845)

182 cycles completed. Probability-dependent model validated conceptually.

Research continues.

