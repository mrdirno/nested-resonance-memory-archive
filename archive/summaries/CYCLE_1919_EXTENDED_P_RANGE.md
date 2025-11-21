# Cycle 1919: Extended P-Range Analysis

**Date:** November 21, 2025
**Cycle:** 1919
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Non-monotonic Nc(p) relationship discovered**

- Quadratic fit: Nc = 28.88p² - 8.95p + 4.83
- R² = 0.909
- Minimum at p ~0.15

---

## Results

| p | Nc |
|---|----|
| 0.01 | 4.8 |
| 0.03 | 4.5 |
| 0.05 | 4.4 |
| 0.08 | 4.3 |
| 0.10 | 4.3 |
| 0.12 | 4.3 |
| 0.15 | 4.2 |
| 0.20 | 4.1 |
| 0.25 | 4.3 |
| 0.30 | 4.8 |

---

## Model Comparison

| Model | Formula | R² |
|-------|---------|-----|
| Linear | Nc = 4.42 - 0.16p | 0.004 |
| Quadratic | Nc = 28.88p² - 8.95p + 4.83 | **0.909** |

---

## Key Discovery: Regime Change

### Low p (≤0.10)
Nc = 4.75 - 5.42p

Increasing p → Decreasing Nc

### High p (>0.10)
Nc = 3.76 + 2.81p

Increasing p → Increasing Nc

---

## Interpretation

### Optimal Reproduction Probability

The minimum Nc occurs around p ~0.15-0.20 (Nc ~4.1).

**Physical meaning:**
- Too low p: Insufficient reproduction to maintain D0 population
- Too high p: Population explosion → rapid cascade → exhaustion
- Optimal p: Balance between regeneration and cascade

### Non-linear Dynamics

The system exhibits a sweet spot where:
1. D0 replenishes adequately
2. Composition rate is manageable
3. Decomposition maintains balance

---

## Comparison with Previous Results

| Cycle | Finding |
|-------|---------|
| C1918 | Linear fit Nc = 4.8 - 3.0p (R² = 0.787) |
| C1919 | Quadratic fit (R² = 0.909), regime change |

The extended range revealed that C1918's linear fit was an artifact of limited sampling (p = 0.05-0.15).

---

## Theoretical Implications

1. **Optimal control parameter**: p ~0.15 minimizes system requirements
2. **Phase transition**: Sharp regime change at p ~0.10
3. **U-shaped response**: Extreme p values increase Nc

This suggests a resonance-like phenomenon where moderate reproduction probability optimizes system stability.

---

## Session Status (C1664-C1919)

256 cycles completed. Non-monotonic Nc(p) relationship discovered.

Research continues.
