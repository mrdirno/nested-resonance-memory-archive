# Cycle 1940: Fine-Tune Carrying Capacity K

**Date:** November 21, 2025
**Cycle:** 1940
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Safe K range: [30, 60] for 100% coexistence AND 100% bounded**

- K ≤ 60: Both metrics at 100%
- K = 70: Bounded drops to 28%
- K ≥ 80: Bounded fails completely
- Population equilibrium scales linearly with K

---

## Results

| K | Coexistence | Bounded | Avg Population |
|---|-------------|---------|----------------|
| 30 | 100.0% | 100.0% | 1285 |
| 40 | 100.0% | 100.0% | 1721 |
| 50 | 100.0% | 100.0% | 2151 |
| 60 | 100.0% | 100.0% | 2564 |
| 70 | 100.0% | 28.0% | 2999 |
| 80 | 100.0% | 0.0% | 3023 |

---

## Key Findings

### 1. Safe Operating Range

K ∈ [30, 60] achieves perfect metrics:
- 100% coexistence
- 100% bounded (completes 500 cycles)

### 2. Critical Threshold at K ~65

Sharp transition between K=60 and K=70:
- K=60: 100% bounded
- K=70: 28% bounded

The equilibrium population crosses ~3000 cap between these values.

### 3. Linear Population Scaling

Population scales approximately linearly with K:
- slope ≈ 43 agents per K unit
- K=30: 1285, K=60: 2564 (+1279 for +30K)

---

## Physical Interpretation

### Equilibrium Population

With density-dependent reproduction:
```
p_effective = p_base / (1 + total / K)
```

At equilibrium:
- births ≈ deaths + composition losses
- total ≈ constant

Higher K → less suppression → higher equilibrium population.

### The K=60-70 Transition

At K=60: equilibrium ≈ 2564 (below cap)
At K=70: equilibrium ≈ 3000 (at cap)

The cap acts as a hard ceiling that breaks bounded dynamics.

---

## Updated Final Parameters

### Complete Optimal Configuration
```python
# Core parameters
p_base = 0.17
N = 14+
comp_thresh = 0.99
decomp_thresh = 1.7
recharge_base = 0.4

# Density-dependent reproduction
K = 50  # Safe range [30, 60]
p_effective = p_base / (1 + total / K)

→ 100% coexistence
→ 100% bounded
→ Equilibrium ~2000-2500 agents
```

### Population Targets

| Target Population | K Value |
|-------------------|---------|
| ~1300 | 30 |
| ~1700 | 40 |
| ~2200 | 50 |
| ~2600 | 60 |

---

## Session Status (C1664-C1940)

277 cycles completed. Complete parameter optimization achieved. Safe K range [30-60] identified for density-dependent bounded dynamics with 100% coexistence.

Research continues.
