# Cycle 1858: Depth Invariance of λ

**Date:** November 21, 2025
**Cycle:** 1858
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**λ = 14 is INVARIANT for N_DEPTHS ≥ 4**

The transition zone (N=14-17) does not change with depth configuration.
This falsifies depth-scaling hypotheses.

---

## Key Results

### Transition Zone by Depth

| N_DEPTHS | Trans_Start | Trans_End | Zone |
|----------|-------------|-----------|------|
| 3 | 10 | ? | Different |
| 4 | 14 | 17 | **INVARIANT** |
| 5 | 14 | 17 | **INVARIANT** |
| 6 | 14 | 17 | **INVARIANT** |

### Critical Discovery

For N_DEPTHS ≥ 4, the transition zone is identical:
- **Trans_start = 14**
- **Trans_end = 17**

λ = 14 is NOT a function of maximum depth.

---

## Falsified Hypotheses

### 1. Exponential Scaling
```
λ(d) = 2^(d-1) × φ

Predictions:
  d=4: λ = 8 × 1.618 = 13
  d=5: λ = 16 × 1.618 = 26
  d=6: λ = 32 × 1.618 = 52

Empirical: λ = 14 for all d ≥ 4
Result: FALSIFIED
```

### 2. Fibonacci Scaling
```
λ(d) = F_d × φ

Predictions:
  d=4: λ = 3 × 1.618 = 5
  d=5: λ = 5 × 1.618 = 8
  d=6: λ = 8 × 1.618 = 13

Empirical: λ = 14 for all d ≥ 4
Result: FALSIFIED
```

---

## Theoretical Implications

### Why Depth Independence?

λ = 14 is determined by:
1. **Composition threshold** (sim ≥ 0.5)
2. **Energy dynamics** (recharge, decay rates)
3. **Reproduction probability** (0.10)

NOT by:
- Maximum depth available
- Total composition capacity

### The "Saturation" Hypothesis

At N ≥ 14, the system reaches a "composition saturation" where:
- Initial agents create maximum possible compositions in cycle 0
- Additional depths don't change this bottleneck
- λ is set by D0→D1→D2 dynamics, not D4/D5/D6

### Special Case: N_DEPTHS = 3

Transition at N=10 (not 14) suggests:
- With only 3 depths, different dynamics apply
- System can't "buffer" agents in intermediate depths
- Lower λ due to reduced complexity

---

## Design Implications

### Universal λ

For any system with N_DEPTHS ≥ 4:
- Avoid N = 14-17 (transition zone)
- Use N ≤ 13 or N ≥ 18

### Secondary Dead Zone

Note: N=30 shows 67% survival at higher depths.
This suggests another transition zone around N=30.
(Aligns with earlier finding: dead zones at 28-30)

---

## Conclusions

1. **λ = 14 is depth-invariant** for N_DEPTHS ≥ 4
2. **Falsified** exponential and Fibonacci scaling
3. **Composition saturation** determines λ
4. **N_DEPTHS = 3** has different dynamics (λ ≈ 10)
5. **Design rule**: N ∈ {1-13, 18+} safe for d ≥ 4

---

## Session Status (C1664-C1858)

195 cycles completed. Depth invariance discovered.

Research continues.

