# Cycle 1785: Minimum Viable Population

**Date:** November 21, 2025
**Cycle:** 1785
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested N=2-30 to find minimum viable population for coexistence.

**FINDING: Minimum viable N=9 (98%), with small-N oscillations**

---

## Results

### Critical Boundaries

| N | Coexistence | Status |
|---|-------------|--------|
| 2-3 | 0% | IMPOSSIBLE |
| 4-8 | 12-60% | CHAOTIC |
| 9 | 98% | FIRST VIABLE |
| 14-15 | 40-42% | PRE-ZONE DIP |
| 17-18 | 100% | OPTIMAL |
| 28-30 | 52-70% | ZONE 1 APPROACH |

### Complete Data

| N | Coexist | N | Coexist | N | Coexist |
|---|---------|---|---------|---|---------|
| 2 | 0% | 12 | 86% | 22 | 80% |
| 3 | 0% | 13 | 68% | 23 | 90% |
| 4 | 32% | 14 | 40% | 24 | 100% |
| 5 | 60% | 15 | 42% | 25 | 96% |
| 6 | 30% | 16 | 76% | 26 | 92% |
| 7 | 12% | 17 | 100% | 27 | 84% |
| 8 | 56% | 18 | 100% | 28 | 70% |
| 9 | 98% | 19 | 98% | 29 | 58% |
| 10 | 84% | 20 | 96% | 30 | 52% |
| 11 | 78% | 21 | 84% | | |

---

## Analysis

### Small-N Chaos (N<9)

Insufficient agents for stable composition-decomposition dynamics.

N=9 is the minimum critical mass for the cycling loop to form.

### Pre-Zone-1 Dip (N=14-15)

A local minimum at ~40% appears before Zone 1.

This may be a "Zone 0" effect at half wavelength (~14.5 ≈ λ).

### Stable Region (N=17-27)

Optimal operating range with 80-100% coexistence.

Safe from both small-N chaos and Zone 1 effects.

---

## Design Rule Update

**Recommended operating range: N=17-27 (or N≥35)**

Avoid:
- N < 9 (insufficient agents)
- N = 14-15 (pre-zone dip)
- N = 29±3 (Zone 1)

---

## Session Status (C1664-C1785)

122 cycles completed. Research continues.

