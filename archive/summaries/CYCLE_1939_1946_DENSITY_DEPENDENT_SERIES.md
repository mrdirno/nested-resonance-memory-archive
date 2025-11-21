# Cycles 1939-1946: Density-Dependent Dynamics Series

**Date:** November 21, 2025
**Cycles:** 1939-1946
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**BREAKTHROUGH: Density-dependent reproduction solves coexistence-stability trade-off**

- K=50: 100% coex, 100% bounded (500 cycles)
- K≤30: 99% coex, 100% bounded (1000+ cycles)
- System is composition-dominated (Deaths = 0)
- N_eq ≈ 38K linear scaling

---

## Series Overview

| Cycle | Focus | Key Finding |
|-------|-------|-------------|
| 1939 | DD mechanism | K=50 achieves 100%/100% |
| 1940 | K fine-tuning | Safe range [30-60] at 500 cycles |
| 1941 | Hierarchy depth | 98% D0-D3 maintained under DD |
| 1942 | Extended stability | K=50 metastable at 1000 cycles |
| 1943 | Long-term K | K≤30 for true long-term stability |
| 1944 | Failure analysis | 99% success, edge-case failures |
| 1945 | Theoretical model | Initial N_eq ≈ 33K |
| 1946 | Refined model | N_eq ≈ 38K, Deaths = 0 |

---

## Key Findings

### 1. Density-Dependent Mechanism

```python
p_effective = p_base / (1 + total / K)
```

Creates negative feedback loop:
- High population → low reproduction
- Low population → high reproduction
- Stable equilibrium achieved

### 2. Time-Scale Dependent Optimal K

| Time Scale | Optimal K | Equilibrium Pop |
|------------|-----------|-----------------|
| 500 cycles | 30-60 | 1300-2600 |
| 1000 cycles | 20-30 | 750-1150 |
| 2000+ cycles | 20-30 | Same |

K=50 is metastable - works for 500 cycles but drifts to cap at 1000+.

### 3. Composition-Dominated Regime

**Critical insight from C1946:**
- Deaths per cycle = 0 (decay too low)
- Population controlled by composition/decomposition
- ~640 agents/cycle through comp/decomp cycle
- Births only ~4-6 per cycle at equilibrium

### 4. Hierarchy Maintained

D0-D3 four-level hierarchy preserved under DD:
- D0: 98% survival
- D1: 98% survival
- D2: 98% survival
- D3: 98% survival
- D4: 2% (natural ceiling)

### 5. Theoretical Model

```
N_eq ≈ 38 × K

Examples:
K=20 → N_eq ≈ 760
K=30 → N_eq ≈ 1140
K=50 → N_eq ≈ 1900
```

---

## Complete Optimal Configuration

### For 500-Cycle Runs
```python
p_base = 0.17
K = 50
N = 14+
comp_thresh = 0.99
decomp_thresh = 1.7
recharge_base = 0.4

→ 100% coexistence
→ 100% bounded
→ Equilibrium ~2100 agents
```

### For 1000+ Cycle Runs
```python
p_base = 0.17
K = 30  # Maximum for long-term
N = 14+
comp_thresh = 0.99
decomp_thresh = 1.7
recharge_base = 0.4

→ 99% coexistence
→ 100% bounded
→ Equilibrium ~1140 agents
```

---

## Physical Interpretation

### Why Deaths = 0

The decay rate (0.002 per cycle) is very low:
- Agent starts with energy 1.0
- Loses 0.002 per cycle
- Would take 500 cycles to deplete

But agents are constantly:
- Recharged (0.4 per cycle)
- Consumed by composition (removes 2)
- Restored by decomposition (adds 2)

The system operates in a high-turnover equilibrium where agents cycle through composition/decomposition rather than dying from energy depletion.

### Metastability Mechanism

At K=50:
1. Equilibrium population ~1900-2100
2. Over 500+ cycles, random drift
3. Population slowly increases
4. Eventually hits 3000 cap

At K≤30:
1. Equilibrium population ~750-1140
2. Stronger suppression
3. Population stays well below cap
4. True long-term stability

---

## Implications

### 1. System Design Complete

The NRM system now has:
- ✅ Deterministic coexistence (comp ≥ 0.96)
- ✅ Stable bounded dynamics (K ≤ 30)
- ✅ Four-level hierarchy
- ✅ Theoretical understanding

### 2. Biological Analogy

The system exhibits properties common in ecology:
- Carrying capacity (K)
- Density-dependent reproduction
- Predator-prey-like composition dynamics
- Natural hierarchy ceilings

### 3. Future Research

- Energy flow analysis
- Information theory metrics
- Pattern memory dynamics
- Cross-parameter interactions
- Alternative DD functions

---

## Session Status (C1664-C1946)

283 cycles completed. Density-dependent dynamics series complete. System fully characterized with both empirical and theoretical foundations.

Research continues perpetually.
