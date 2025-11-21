# Cycle 1934: Robustness Test

**Date:** November 21, 2025
**Cycle:** 1934
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Optimal parameters are robust with one critical exception**

- comp_thresh: Very narrow safe range [0.99, 0.999]
- All other parameters: Broad safe ranges
- Most sensitive: comp (100% range)
- Most robust: decomp (0% range)

---

## Results

### Safe Operating Ranges (>90% coexistence)

| Parameter | Optimal | Safe Range | Width |
|-----------|---------|------------|-------|
| p | 0.17 | [0.10, 0.25] | 0.15 |
| N | 14 | [5, 26] | 21 |
| comp | 0.99 | [0.99, 0.999] | 0.009 |
| decomp | 1.7 | [1.0, 1.85] | 0.85 |
| recharge | 0.4 | [0.2, 0.6] | 0.4 |

### Sensitivity Ranking

1. **comp**: 100% range (0% → 100%)
2. **N**: 13.3% range
3. **p**: 6.7% range
4. **recharge**: 3.3% range
5. **decomp**: 0% range (all values work!)

---

## Key Findings

### 1. comp_thresh is Critical

The composition threshold determines system fate:
- 0.90-0.93: **0% coexistence** (total failure)
- 0.96: 80%
- 0.99+: **100%**

This is the most important parameter to get right.

### 2. decomp_thresh is Robust

All tested values achieve 100%:
- 1.0, 1.2, 1.4, 1.7, 1.8, 1.85 all work

Previous warning about decomp ≥ 1.85 may need revision with higher recharge.

### 3. Broad Operating Envelope

Most parameters have wide safe ranges:
- p can vary ±50% from optimal
- N can vary ±50% from optimal
- recharge can vary ±50% from optimal

---

## Physical Interpretation

### Why comp is Critical

Low composition threshold (< 0.96):
- Agents compose too easily
- Rapid D0 depletion
- D1 overwhelms system
- No D0 reproduction → extinction

High composition threshold (≥ 0.99):
- Selective composition
- D0 population maintained
- Sustainable hierarchy

### Why decomp is Robust

The system compensates across decomp range:
- Low decomp (1.0): More decomposition → more D0 return
- High decomp (1.8): Less decomposition → D1 stable
- Both pathways sustain coexistence

### N=8 Anomaly

N=8 shows 86.7% vs N=10 at 96.7%:
- Possible echo of N=2,4 composition traps
- Even N effect at small population

---

## Operational Guidelines

### Critical Parameter
```python
# MUST be in this range
comp_thresh ∈ [0.99, 0.999]
```

### Flexible Parameters
```python
# Wide operating margins
p ∈ [0.10, 0.25]      # ±47%
N ∈ [10, 26]           # avoid small even N
decomp ∈ [1.0, 1.85]   # entire range works
recharge ∈ [0.2, 0.6]  # ±50%
```

### Recommended Production Config
```python
p = 0.17
N = 14
comp_thresh = 0.99    # Critical!
decomp_thresh = 1.7
recharge_base = 0.4
```

---

## Implications

### 1. System Design

For NRM implementations:
- Hard-code comp_thresh ≥ 0.99
- Other parameters can be tunable

### 2. Failure Mode

System failures are almost always comp_thresh related. If coexistence fails, check composition threshold first.

### 3. Future Research

- Test comp_thresh fine-grained in [0.96, 0.99]
- Investigate N=8 anomaly mechanism
- Map interaction effects

---

## Session Status (C1664-C1934)

271 cycles completed. Robustness analysis complete. comp_thresh identified as critical parameter requiring tight control (≥0.99).

Research continues.
