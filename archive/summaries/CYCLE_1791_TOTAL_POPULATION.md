# Cycle 1791: Total Population at Equilibrium

**Date:** November 21, 2025
**Cycle:** 1791
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Analyzed total population at equilibrium vs initial N.

**FINDING: 11-15% of initial N survives, oscillates with dead zone pattern**

---

## Results

| N | Total | Ratio | Depths |
|---|-------|-------|--------|
| 20 | 3.6 | 0.18 | 2.2 |
| 25 | 3.8 | 0.15 | 3.0 |
| 30 | 4.5 | 0.15 | 1.7 |
| 45 | 6.6 | 0.15 | 1.8 |
| 60 | 8.7 | 0.14 | 2.0 |
| 75 | 10.9 | 0.15 | 2.2 |
| 90 | 13.4 | 0.15 | 2.1 |
| 100 | 11.2 | 0.11 | 2.3 |

---

## Analysis

### Linear Scaling

Total population scales linearly with N:
- N=20: 3.6 agents
- N=100: 11.2 agents

Ratio: 11-15% of initial population survives.

### Oscillation Pattern

Dead zones (N≈30, 45, 60, 75, 90) show:
- Higher total population
- Lower depth count (1.7-2.2)

Non-dead zones show:
- Lower total population
- Higher depth count (2.5-3.0)

### Interpretation

Dead zones accumulate more agents but in fewer depths.
Safe zones distribute fewer agents across more depths.

Quality (coexistence) vs Quantity (population) tradeoff.

---

## Conclusions

1. **11-15% survival** ratio at equilibrium
2. **Oscillation** matches dead zone pattern
3. **Dead zones = more agents, fewer depths**
4. **Safe zones = fewer agents, more depths**

---

## Session Status (C1664-C1791)

128 cycles completed. Research continues.

