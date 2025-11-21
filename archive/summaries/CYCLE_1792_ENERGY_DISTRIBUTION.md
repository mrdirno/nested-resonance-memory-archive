# Cycle 1792: Energy Distribution at Equilibrium

**Date:** November 21, 2025
**Cycle:** 1792
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Analyzed energy levels of surviving agents by depth.

**FINDING: D3 is stable accumulator due to low energy (0.6 << 1.3 threshold)**

---

## Results

### Trough (N=35)

| Depth | Count | Mean E | Std E |
|-------|-------|--------|-------|
| D0 | 0 | N/A | N/A |
| D1 | 23 | 0.887 | 0.281 |
| D2 | 6 | 1.247 | 0.030 |
| D3 | 75 | 0.630 | 0.079 |
| D4 | 33 | 1.182 | 0.072 |

### Peak (N=29)

| Depth | Count | Mean E | Std E |
|-------|-------|--------|-------|
| D0 | 8 | 0.603 | 0.008 |
| D1 | 14 | 1.009 | 0.287 |
| D2 | 4 | 1.203 | 0.021 |
| D3 | 98 | 0.591 | 0.034 |
| D4 | 10 | 1.144 | 0.065 |

---

## Analysis

### D3 Stability Mechanism

D3 energy (0.59-0.63) is far below decomposition threshold (1.3).

Agents can't decompose → accumulate indefinitely.

Low energy variance (σ=0.03-0.08) indicates stable equilibrium.

### D4 Cycling

D4 energy (1.14-1.18) is near decomposition threshold.

Agents constantly decomposing back to D3.

This creates the D3-D4 cycling loop.

### Peak vs Trough

**Peak (N=29):**
- More D3 (98) but fewer D4 (10)
- D3/D4 ratio = 9.8

**Trough (N=35):**
- Balanced D3 (75) and D4 (33)
- D3/D4 ratio = 2.3

Troughs maintain better D3/D4 balance for coexistence.

### Energy Stratification

- D2, D4: High energy (~1.2) - cycling/transit
- D1: Medium energy (~0.9-1.0) - transit
- D3: Low energy (~0.6) - stable accumulator

---

## Conclusions

1. **D3 accumulates** due to low energy
2. **D4 cycles** due to high energy
3. **Peak = D3 dominant** (high ratio)
4. **Trough = balanced** D3/D4

---

## Session Status (C1664-C1792)

129 cycles completed. Research continues.

