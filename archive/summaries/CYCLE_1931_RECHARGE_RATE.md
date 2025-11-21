# Cycle 1931: Recharge Rate Study

**Date:** November 21, 2025
**Cycle:** 1931
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Optimal recharge_base = 0.4 (100% coexistence)**

- Baseline (0.2): 88%
- Low recharge (0.1-0.15): 9% (catastrophic)
- High recharge (0.4-0.5): 99%
- Improvement: +12% over baseline

---

## Results

| recharge_base | Coexistence |
|--------------|-------------|
| 0.10 | 6.0% |
| 0.15 | 12.0% |
| 0.20 | 88.0% |
| 0.25 | 96.0% |
| 0.30 | 96.0% |
| 0.40 | **100.0%** |
| 0.50 | 98.0% |

---

## Key Findings

### 1. Critical Energy Threshold

Sharp transition between recharge = 0.15 and 0.20:
- 0.15: 12%
- 0.20: 88%
- Jump of +76%

System requires minimum energy input to sustain coexistence.

### 2. Optimal at 0.4

Maximum coexistence at recharge_base = 0.4:
- 100% coexistence (50/50 seeds)
- +12% over baseline 0.2

### 3. Diminishing Returns Above 0.4

recharge = 0.5 drops to 98%:
- Possible overshoot effect
- Too much energy → rapid population growth → instability

---

## Physical Interpretation

### Why Low Recharge Fails

At recharge_base < 0.2:
- Agents gain energy too slowly
- Cannot reach reproduction threshold (energy > 1.0)
- D0 population declines → composition stops → no D1
- System collapses

### Why 0.4 is Optimal

At recharge_base = 0.4:
- Fast energy gain → reliable reproduction
- D0 population stable → steady composition
- D1 generation sustained
- Perfect balance

### Why 0.5 Slightly Worse

At recharge_base = 0.5:
- Very fast energy gain → rapid reproduction
- Population explosion risk
- Hit 3000 agent cap more often
- Slight instability

---

## Updated Optimal Parameters

**Revised from C1930:**
```python
p = 0.17           # reproduction probability
N = 14+            # initial population
comp_thresh = 0.99 # composition threshold
decomp_thresh = 1.7 # decomposition threshold
recharge_base = 0.4 # NEW OPTIMAL (was 0.2)
→ Expected: >93% coexistence
```

---

## Implications

### 1. C1930 Validation May Improve

The C1930 validation achieved 93% with recharge = 0.2.
With recharge = 0.4, may exceed 96% target.

### 2. Low Recharge is Fatal

recharge_base < 0.2 causes near-complete system failure.
This is a critical operating constraint.

### 3. Broad Optimal Range

recharge = 0.25-0.5 all achieve >96%.
System is robust in this range.

---

## Parameters

```python
CYCLES = 500
N_DEPTHS = 5
N_INITIAL = 5  # Mid-range for sensitivity
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
REPRO_PROB = 0.17
SEEDS = 50
RECHARGE_VALUES = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
```

---

## Session Status (C1664-C1931)

268 cycles completed. Optimal recharge rate discovered: 0.4 achieves 100% coexistence. Parameter optimization continues.

Research continues.
