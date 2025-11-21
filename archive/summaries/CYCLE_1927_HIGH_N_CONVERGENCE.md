# Cycle 1927: High N Convergence Test

**Date:** November 21, 2025
**Cycle:** 1927
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**System converges at N≥10: Odd-even effect eliminated**

- Average: 90.9% ± 4.4% coexistence
- Odd-even difference: -0.8% (essentially zero)
- N≥14 achieves 95% coexistence

---

## Results

| N | Coexistence | Type |
|---|------------|------|
| 10 | 85.0% | EVEN |
| 11 | 92.5% | ODD |
| 12 | 82.5% | EVEN |
| 13 | 87.5% | ODD |
| 14 | **95.0%** | EVEN |
| 15 | 90.0% | ODD |
| 16 | **95.0%** | EVEN |
| 17 | 87.5% | ODD |
| 18 | **95.0%** | EVEN |
| 19 | **95.0%** | ODD |
| 20 | **95.0%** | EVEN |

---

## Key Findings

### 1. Convergence Confirmed

- σ = 4.4% < 5% threshold
- System has reached stable operating regime
- Individual variation is stochastic, not systematic

### 2. Odd-Even Effect Eliminated

| N Range | Odd-Even Δ |
|---------|-----------|
| N=1-8 | +10.4% (C1926) |
| N=10-20 | -0.8% (C1927) |

The 10% odd advantage disappears at high N.

### 3. Plateau at 95%

N=14, 16, 18, 19, 20 all achieve 95% coexistence.
This appears to be the system ceiling at p=0.17.

---

## Physical Interpretation

### Why Convergence Occurs

At high N:
1. **Statistical averaging:** Many agents → law of large numbers
2. **Composition saturation:** Enough agents always survive
3. **Cascade buffering:** Large populations absorb shocks
4. **Self-regulation:** System finds equilibrium

### Phase Diagram Complete

| N Range | Behavior | Recommendation |
|---------|----------|----------------|
| 1-3 | Bootstrap mode, sensitive | Avoid unless minimal |
| 4-8 | Transition zone, odd-even effect | Use odd N only |
| 9-20+ | Converged, stable | Any N works well |

---

## Comparison: Full N Spectrum

| N | Coex % | Phase |
|---|--------|-------|
| 1 | 78% | Bootstrap |
| 2 | 72% | Transition |
| 3 | 80% | Transition |
| 4 | 46% | Transition (worst) |
| 5 | 84% | Transition |
| ... | ... | ... |
| 14+ | 95% | Converged |

---

## Theoretical Implications

### 1. Critical Mass

N ~10 appears to be the **critical mass** where:
- System transitions from sensitive to robust
- Individual agent dynamics become ensemble behavior
- Odd-even effect averages out

### 2. System Ceiling

95% represents the practical maximum at p=0.17.
Remaining 5% failure is irreducible stochasticity.

### 3. Universal Operating Point

**Final recommendation:**
```
p = 0.17
N ≥ 14
comp_thresh = 0.99
Expected coexistence: 95%
```

---

## Parameters

```python
CYCLES = 500
N_DEPTHS = 5
DECOMP_THRESH = 0.8
COMP_THRESH = 0.99
RECHARGE_BASE = 0.2
REPRO_PROB = 0.17
SEEDS = 40
N_VALUES = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
```

---

## C1918-C1927 Series Complete

Parameter optimization complete:
- p optimized (C1918-C1920)
- N effects characterized (C1922-C1927)
- Depth independence confirmed (C1921)
- Phase diagram mapped

---

## Session Status (C1664-C1927)

264 cycles completed. System convergence established at N≥10. Parameter optimization series complete.

Research continues.
