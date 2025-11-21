# Cycle 1939: Density-Dependent Reproduction

**Date:** November 21, 2025
**Cycle:** 1939
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**BREAKTHROUGH: K=50 achieves 100% coexistence AND 100% bounded**

- Density-dependent reproduction solves coexistence-stability trade-off
- K=50: 100% coex, 100% bounded, avg pop 2154
- Major improvement over C1938 (77% coex, 23% bounded)

---

## Results

| K | Coexistence | Bounded | Avg Pop |
|---|-------------|---------|---------|
| 50 | **100.0%** | **100.0%** | 2154 |
| 100 | 100.0% | 0.0% | 3020 |
| 200 | 100.0% | 0.0% | 3027 |
| 500 | 100.0% | 0.0% | 3036 |
| 1000 | 100.0% | 0.0% | 3045 |
| 2000 | 100.0% | 0.0% | 3048 |

---

## Key Findings

### 1. Perfect Balance Achieved

K=50 is the optimal carrying capacity:
- 100% coexistence maintained
- 100% runs complete 500 cycles
- Stable population ~2154

### 2. Sharp K Threshold

K > 50 causes population explosion:
- K=100: hits 3000 cap
- K=50: stable at ~2154
- Critical transition between 50-100

### 3. Equilibrium Population

Average population scales with K:
- K=50 → ~2154 (below cap)
- K≥100 → ~3000+ (hits cap)

---

## Physical Mechanism

### Density-Dependent Reproduction

```python
p_effective = p_base / (1 + total / K)
```

At K=50:
- total=14: p ≈ 0.17/(1+0.28) = 0.13
- total=500: p ≈ 0.17/(1+10) = 0.015
- total=2000: p ≈ 0.17/(1+40) = 0.004

### Negative Feedback Loop

1. Population grows → p decreases
2. Less reproduction → growth slows
3. Reaches equilibrium where births ≈ deaths
4. Stable bounded population

### Why K=50 Works

At K=50, equilibrium occurs at ~2154:
- Population below 3000 cap
- Reproduction still high enough for D1 generation
- Balance between growth and suppression

---

## Comparison

### C1938 (Fixed p) vs C1939 (Density-Dependent)

| Metric | C1938 Best | C1939 K=50 |
|--------|------------|------------|
| Coexistence | 77% | **100%** |
| Bounded | 23% | **100%** |
| Method | p=0.05 | p_eff=0.17/(1+N/50) |

Improvement: +23% coex, +77% bounded

### Trade-off Resolution

The fundamental trade-off identified in C1938 is resolved:
- High reproduction for coexistence: ✓ (at low pop)
- Low reproduction for stability: ✓ (at high pop)
- Dynamic balance achieved

---

## Updated Optimal Parameters

### For Bounded + Coexistence
```python
p_base = 0.17
K = 50  # Carrying capacity
N = 14+
comp_thresh = 0.99
decomp_thresh = 1.7
recharge_base = 0.4

# Effective reproduction
p_effective = p_base / (1 + total / K)

→ 100% coexistence, 100% bounded
→ Equilibrium population ~2154
```

---

## Implications

### 1. System Design Complete

The NRM system now has:
- Deterministic coexistence (comp ≥ 0.96)
- Stable bounded dynamics (K=50)
- Robust multi-level hierarchy

### 2. Biological Analogy

Density-dependent reproduction is common in nature:
- Carrying capacity limits
- Resource competition
- Territorial constraints

The NRM system now exhibits this fundamental property.

### 3. Further Research

- Fine-tune K for specific population targets
- Test other density-dependent mechanisms
- Explore K effect on hierarchy depth

---

## Session Status (C1664-C1939)

276 cycles completed. Density-dependent reproduction with K=50 achieves 100% coexistence AND 100% bounded dynamics. Major breakthrough in NRM system design.

Research continues.
