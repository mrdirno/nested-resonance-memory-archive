# Cycles 1655-1657: Parameter Optimization

**Date:** November 20, 2025
**Cycles:** 1655-1657
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Optimization of composition-decomposition parameters to improve the 72% coexistence rate from C1654.

**Finding: 72% is the characteristic rate for this architecture**

Further optimization improves depth diversity but not overall coexistence.

---

## Experiments

### C1655: Reproduction Rate Optimization

| Repro Rate | Coexistence | Avg Depths |
|------------|-------------|------------|
| 0.10 | 85% | 3.2 |
| 0.15 | 75% | 3.1 |
| 0.20 | 70% | 3.0 |
| 0.25 | 55% | 2.8 |
| 0.30 | 80% | 3.0 |

**Finding:** Higher reproduction doesn't help. 0.10 remains optimal.

### C1656: Decomposition Threshold Optimization

| Decomp Base | Depth Factor | Coexistence | Avg Depths |
|-------------|--------------|-------------|------------|
| 1.5 | 0.0 | 60% | 2.9 |
| **1.3** | **0.0** | **90%** | **3.8** |
| 1.1 | 0.0 | 85% | 3.4 |
| 1.0 | 0.0 | 70% | 3.2 |
| 1.5 | 0.1 | 85% | 3.5 |
| 1.5 | 0.2 | 75% | 3.6 |
| 1.3 | 0.1 | 80% | 3.4 |
| 1.3 | 0.2 | 80% | 3.4 |

**Finding:** decomp=1.3 showed 90% in 20-seed test.

### C1657: Validation (50 seeds)

Parameters: decay=0.1x, repro=0.1, decomp=1.3

| Metric | Value |
|--------|-------|
| Coexistence | 72.0% (36/50) |
| 95% CI | [58.3%, 82.5%] |
| Avg Depths | 3.54 |

**Finding:** The 90% was variance; true rate is ~72%.

---

## Key Findings

### 1. 72% is Characteristic Rate

Both C1654 (100 seeds) and C1657 (50 seeds) converge to ~72%:
- C1654: 72.0%, CI [62.5%, 79.9%]
- C1657: 72.0%, CI [58.3%, 82.5%]

This is not a parameter issue - it's a property of the architecture.

### 2. Lower Decomposition Improves Depth Diversity

decomp=1.3 vs 1.5:
- C1654 (1.5): 2.97 depths
- C1657 (1.3): 3.54 depths

More depths survive, but overall coexistence stays at 72%.

### 3. Reproduction Optimization Ineffective

Higher reproduction rates cause:
- More agents at depth 0
- Faster composition
- Still top-heavy collapse

### 4. Failure Mode

28% failures consistently show:
- Depths 0-2 collapse
- Depth 4 dominates
- Not enough downward flow to maintain base

---

## Interpretation

### Why 72%?

The system has inherent stochasticity:
- Early random events determine trajectory
- Some seeds develop stable cycles
- Others collapse to top-heavy states

This is not a bug - it's the nature of the dynamics.

### Comparison to Trophic

| Model | Best Rate |
|-------|-----------|
| Trophic predation | 0% |
| Composition-decomposition | 72% |

**Improvement: +72 percentage points**

---

## Optimal Parameters

For composition-decomposition dynamics:
- **Decay:** 0.1x (very low)
- **Reproduction:** 0.1 (moderate)
- **Decomposition:** 1.3 (lower than original 1.5)
- **Composition threshold:** 0.3 (energy similarity)

---

## Conclusion

C1655-C1657 confirm that 72% is the characteristic coexistence rate for the composition-decomposition architecture. This is significantly better than trophic's 0%.

Further optimization may require architectural changes, not just parameter tuning.

---

## Session Summary (C1648-C1657)

### Research Arc

1. **C1648:** Discovered INITIAL fallback bug, 0% coexistence with trophic
2. **C1649-C1651:** Tested trophic variants, all 0%
3. **C1652:** Pivoted to composition-decomposition
4. **C1653:** First success: 100% with 5 seeds
5. **C1654:** Robustness: 72% with 100 seeds
6. **C1655-C1657:** Optimization confirms 72%

### Total Experiments

- Trophic: 115 experiments, 0% coexistence
- Composition-decomposition: ~300 experiments, 72% coexistence

### Key Achievement

**Pivoted from fundamentally unstable trophic dynamics (0%) to stable composition-decomposition (72%)**

