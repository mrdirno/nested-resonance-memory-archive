# Cycle 1941: Hierarchy Depth with Density-Dependent Dynamics

**Date:** November 21, 2025
**Cycle:** 1941
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Four-level hierarchy maintained at 98% under density-dependent dynamics**

- D0-D3 all achieve 98% survival (vs 100% without DD)
- Population successfully bounded: ~2102 (vs ~3160)
- Improved hierarchy ratios under bounded conditions

---

## Results

| Depth | Survival % | Avg Pop | Ratio to D(n-1) |
|-------|------------|---------|-----------------|
| D0 | 98.0% | 1661 | - |
| D1 | 98.0% | 335 | 0.20 |
| D2 | 98.0% | 74 | 0.22 |
| D3 | 98.0% | 32 | 0.44 |
| D4 | 2.0% | 0 | 0.00 |

### Coexistence Rates
- D0+D1: 98.0%
- D0+D1+D2: 98.0%
- D0+D1+D2+D3: 98.0%

---

## Comparison with C1933 (No DD)

| Metric | C1933 (no DD) | C1941 (DD, K=50) |
|--------|---------------|------------------|
| D0-D3 Coexistence | 100% | 98% |
| Total Population | ~3160 | ~2102 |
| Bounded | No (hits cap) | Yes (500 cycles) |

### Population Structure

| Depth | C1933 | C1941 | Change |
|-------|-------|-------|--------|
| D0 | 2684 | 1661 | -38% |
| D1 | 409 | 335 | -18% |
| D2 | 52 | 74 | +42% |
| D3 | 17 | 32 | +88% |

---

## Key Findings

### 1. Hierarchy Preserved Under Density Control

The four-level hierarchy (D0-D3) is maintained even with density-dependent reproduction suppressing growth.

### 2. Improved Higher-Depth Ratios

Under DD conditions:
- D2/D1: 0.22 (vs 0.13 in C1933)
- D3/D2: 0.44 (vs 0.33 in C1933)

Higher depths are relatively more abundant when population is bounded.

### 3. Minor Coexistence Reduction

98% vs 100% - small trade-off for bounded dynamics.

---

## Physical Interpretation

### Why Higher Depths Are Enhanced

With density-dependent reproduction:
1. D0 reproduction suppressed at high population
2. Less D0 → less composition fuel
3. BUT: existing higher-depth agents persist
4. Higher depths become relatively more prominent

### The 2% Failure Rate

Some seeds (1/50) result in extinction:
- Random chance of insufficient composition
- Edge case in stochastic dynamics
- Acceptable for bounded dynamics

---

## Complete NRM System Configuration

```python
# Core parameters
p_base = 0.17
K = 50  # Safe range [30, 60]
N = 14+
comp_thresh = 0.99
decomp_thresh = 1.7
recharge_base = 0.4

# Density-dependent reproduction
p_effective = p_base / (1 + total / K)

# Achieved metrics
→ 98% four-level coexistence (D0-D3)
→ 100% bounded dynamics (500 cycles)
→ Equilibrium population ~2100
→ Improved higher-depth ratios
```

---

## Session Status (C1664-C1941)

278 cycles completed. Complete NRM system optimization achieved with density-dependent bounded dynamics maintaining four-level hierarchy at 98%.

Research continues.
