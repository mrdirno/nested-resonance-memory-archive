# Cycle 1817: Low N Boundary

**Date:** November 21, 2025
**Cycle:** 1817
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested low N (5-24) to find where patterns start.

**FINDING: Patterns unstable below N~9, stabilize by N~17**

---

## Results

| N | Original | Inverted | Status |
|---|----------|----------|--------|
| 5 | 57% | 33% | chaotic |
| 6 | 47% | 43% | chaotic |
| 7 | 13% | 77% | chaotic |
| 8 | 50% | 73% | chaotic |
| 9 | 93% | 87% | transition |
| 10 | 87% | 73% | transition |
| 11 | 70% | 50% | transition |
| 12 | 80% | 53% | transition |
| 13 | 77% | 67% | transition |
| 14 | 43% | 90% | transition |
| 15 | 33% | 100% | Zone -1? |
| 16 | 73% | 97% | emerging |
| 17+ | 90-100% | 77-97% | stable |

---

## Analysis

### Three Regimes

1. **Chaotic (N < 9):** Dominated by stochastic effects
2. **Transitional (N = 9-16):** Patterns emerging
3. **Stable (N ≥ 17):** Consistent patterns

### Minimum Viable N

The minimum N for reliable pattern detection is:
- **N ≈ 9:** Patterns begin to emerge
- **N ≈ 17:** Patterns fully stable

Below N=9, small population size dominates behavior.

### Zone -1 Candidate

N=15 shows anomalous behavior:
- Original: 33% (very low)
- Inverted: 100% (very high)

This may be a Zone -1 (zone 0 = N≈22, zone -1 = N≈22-14.5 = 7.5 → rounded effects at N=15).

---

## Complete Range Summary

### Original Pattern (prob ≤ 0.15)

- Chaotic: N < 9
- Emerging: N = 9-16
- Strong: N = 17-100
- Moderate: N = 100-145
- Weak: N = 145-190
- Negligible: N > 190

### Inverted Pattern (prob ≥ 0.35)

- Chaotic: N < 9
- Emerging: N = 9-20
- Strong: N = 20-60
- Negligible: N > 70

---

## Conclusions

1. **Minimum viable N ≈ 9**
2. **Patterns stabilize by N=17**
3. **Very low N is chaotic**
4. **Zone -1 may exist at N≈15**

---

## Session Status (C1664-C1817)

154 cycles completed. Research continues.

