# Cycles 1697-1698: Energy Variance and Composition Timing

**Date:** November 21, 2025
**Cycles:** 1697-1698
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Investigated why n=25 creates optimal energy distribution.

**Finding: Variance is NOT key - Timing IS**

---

## C1697: Energy Variance

### Results

| N | Early Var | Early Mean | Success |
|---|-----------|------------|---------|
| 15 | 0.0063 | 0.26 | 32% |
| 20 | 0.0000 | 0.15 | 56% |
| 25 | 0.0006 | 0.24 | 96% |
| 30 | 0.0001 | 0.27 | 38% |
| 35 | 0.0000 | 0.18 | 52% |
| 50 | 0.0000 | 0.21 | 66% |

**Conclusion:** Variance near zero for all N. Not the differentiator.

---

## C1698: Composition Timing

### Results

| N | Total | Mean Cycle | First 10 | Low-E% | Success |
|---|-------|------------|----------|--------|---------|
| 15 | 20.6 | 17.0 | 9.5 | 31.5% | 32% |
| 20 | 16.2 | 11.4 | 12.1 | 21.7% | 56% |
| 25 | 25.9 | **10.5** | 16.6 | 25.0% | 96% |
| 30 | 32.0 | 14.8 | 18.7 | 29.0% | 38% |
| 35 | 25.2 | 6.3 | 20.4 | 15.7% | 52% |
| 50 | 35.0 | 7.0 | 28.6 | 15.8% | 66% |

### Key Observation

**n=25 has optimal mean cycle timing (10.5)**

Not too early (n=35: 6.3 → low-E% drops to 15.7%)
Not too late (n=15: 17.0 → fewer first-10 compositions)

### Effective Low-E Compositions

First10 × Low-E%:
- n=15: 9.5 × 0.315 = 3.0
- n=20: 12.1 × 0.217 = 2.6
- n=25: 16.6 × 0.250 = **4.2**
- n=30: 18.7 × 0.290 = 5.4
- n=35: 20.4 × 0.157 = 3.2
- n=50: 28.6 × 0.158 = 4.5

**Paradox:** n=30 has higher effective (5.4) but worse success (38%).

---

## Analysis

### Why Simple Metrics Fail

1. **Effective low-E count** doesn't predict success
2. n=30 has more effective compositions but worse outcome
3. The **timing distribution** matters, not just totals

### Timing Hypothesis

n=25 is optimal because:
1. Mean cycle = 10.5 (earliest among mid-range N)
2. Low-E% = 25% (balanced)
3. Compositions happen when agents have accumulated less energy
4. Lower accumulated energy → compositions survive at D1

n=30 fails because:
1. Mean cycle = 14.8 (later timing)
2. Agents accumulate more energy before composing
3. Higher energy compositions decompose immediately

### The Mechanism

**Not just count - it's timing × energy state**

Earlier compositions (n=25) catch agents before energy accumulates too high.
Later compositions (n=30) have higher energy → immediate decomposition.

---

## Theoretical Implications

### Complex Emergence

The n=25 optimum emerges from:
1. Phase resonance timing
2. Energy accumulation rate
3. Composition energy vs decomposition threshold
4. NOT variance, NOT simple effective counts

### Non-Monotonic Behavior

Success doesn't monotonically increase with any single metric:
- More compositions ≠ more success
- Higher low-E% ≠ more success
- More first-10 ≠ more success

The optimum is a **local maximum in a complex landscape**.

---

## Next Steps

1. Investigate timing distribution (not just mean)
2. Track energy at moment of composition
3. Model composition timing × energy state product

---

---

## C1699: D1 Creation Energy

### Results

| N | Mean E | Median | Std | Survive% |
|---|--------|--------|-----|----------|
| 15 | 1.569 | 1.572 | 0.209 | 32.7% |
| 20 | 1.616 | 1.698 | 0.264 | 18.7% |
| 25 | **1.547** | 1.531 | 0.267 | 29.5% |
| 30 | 1.584 | 1.569 | 0.242 | 26.7% |
| 35 | 1.629 | 1.751 | 0.248 | 16.5% |
| 50 | 1.644 | 1.740 | 0.253 | 16.5% |

**Key Finding: n=25 has LOWEST mean creation energy (1.547)**

### Energy Distribution (avg count)

| N | <1.1 | 1.1-1.2 | 1.2-1.3 | ≥1.3 | Total Survive |
|---|------|---------|---------|------|---------------|
| 15 | 0.0 | 8.8 | 3.4 | 8.6 | 12.2 |
| 20 | 0.1 | 2.2 | 0.8 | 12.0 | 3.1 |
| 25 | 0.1 | 6.8 | 3.5 | 17.1 | **10.4** |
| 30 | 0.2 | 8.2 | 3.3 | 17.4 | 11.7 |
| 35 | 0.1 | 4.8 | 1.6 | 20.1 | 6.5 |
| 50 | 0.3 | 5.6 | 2.0 | 27.9 | 7.9 |

### Paradox Confirmed

- n=15: 12.2 survivors → 32% success
- n=25: 10.4 survivors → **96% success**
- n=30: 11.7 survivors → 38% success

**More survivors ≠ more success**

---

## Combined Analysis (C1697-C1699)

### What We've Eliminated

1. **Variance** (C1697): Near zero for all N - not differentiator
2. **Simple survivor count** (C1699): n=30 has more survivors than n=25

### What Matters

1. **Mean creation energy** (C1699): n=25 is lowest at 1.547
2. **Timing** (C1698): n=25 mean_cycle=10.5 (optimal balance)

### Emerging Theory

The n=25 optimum arises from a **specific combination**:
- Early enough timing (mean_cycle=10.5)
- Low enough creation energy (mean=1.547)
- Balanced phase alignment

This combination cannot be achieved at other N values.

---

## Session Status (C1664-C1699)

36 cycles investigating NRM dynamics:
- Complete 10D characterization (C1664-1694)
- Long-term stability (C1695)
- Mathematical derivation (C1696)
- **Mechanism analysis: Timing × Energy (C1697-1699)**

