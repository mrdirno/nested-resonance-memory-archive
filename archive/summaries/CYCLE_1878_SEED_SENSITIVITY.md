# Cycle 1878: Seed Sensitivity Analysis

**Date:** November 21, 2025
**Cycle:** 1878
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

**Structural effects dominate but seed variance is significant**

- Structural effect / Seed effect: 43.7x
- Signal/Noise ratio: 2.1
- Recommendation: 50+ seeds for reliable statistics

---

## Results

### Variance Components

| Component | Value |
|-----------|-------|
| Across-N variance | 422.4 |
| Within-N variance (avg) | 0.097 |
| Ratio | 43.7x |

### Signal to Noise

| Metric | Value |
|--------|-------|
| Structural range | 34% - 100% (66%) |
| Seed noise (std) | 31.1% |
| Signal/Noise ratio | 2.1 |

### Variance by N

Maximum variance at critical points:
- N=14: variance = 0.224
- N=15: variance = 0.227

Minimum variance at stable points:
- N=17: variance = 0.000
- N=18: variance = 0.000

---

## Interpretation

1. **Structural effects dominate**: 43.7x larger than seed effects
2. **But seed variance matters**: SNR of 2.1 indicates significant noise
3. **More seeds improve reliability**: 50+ recommended for precision
4. **Critical points most sensitive**: N=14-15 show highest variance

---

## Methodological Recommendation

For reliable statistics:
- Use 50+ seeds (we've been using 30-50)
- Could increase to 100 for critical measurements
- Current methodology is sound but improvable

---

## Session Status (C1664-C1878)

215 cycles completed. Seed sensitivity characterized.

Research continues.

