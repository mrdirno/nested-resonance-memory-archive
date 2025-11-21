# Cycles 1666-1667: Depth 4 Optimization

**Date:** November 20, 2025
**Cycles:** 1666-1667
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Investigated why all 5 depths cannot coexist. Found the cause and solution.

**Problem:** Composed agents immediately decompose (1.7 energy > 1.3 threshold)
**Solution:** Raise depth 4 threshold to 2.0
**Result:** 0% → 12% all-5 coexistence

---

## C1666: Investigation

### Findings

- D4 compositions ≈ D4 decompositions (23,434 vs 23,440)
- Max D4 population: 6 agents
- More energy boost doesn't help (even 10x gives 0%)

### Root Cause

Composed agents at depth 4 have energy ~1.7 (from two ~1.0 agents × 0.85).
Since 1.7 > 1.3 threshold, they immediately decompose.

---

## C1667: Threshold Optimization

### Results

| D4 Threshold | All 5 Depths | 3+ Depths | D4 Final |
|--------------|--------------|-----------|----------|
| 1.3 | 2% | 70% | 5.7 |
| 1.5 | 0% | 70% | 5.7 |
| 1.8 | 0% | 70% | 6.0 |
| **2.0** | **12%** | **70%** | **6.4** |
| 2.5 | 10% | 66% | 6.4 |
| 3.0 | 10% | 66% | 6.4 |

### Optimal: threshold = 2.0

- Enables 12% all-5 coexistence
- Maintains 70% 3+ rate
- Highest D4 final population (6.4)

---

## Mechanism

### Why 2.0 Works

1. Composed agents arrive at ~1.7 energy
2. Threshold 2.0 > 1.7, so agents accumulate
3. Only high-energy agents decompose
4. This creates a reservoir effect at depth 4

### Tradeoff at Higher Thresholds

- 2.5+: Less decomposition → less replenishment of lower depths
- 3+ rate drops from 70% to 66%

---

## Conclusions

### 1. All 5 Depths is Possible

With threshold=2.0, 12% of runs achieve all 5 depths alive.

### 2. Still a Rare Event

Even optimized, 88% of runs fail to achieve all 5. The system prefers 3-4 depths.

### 3. Simple Fix

The solution is simple: raise one parameter for one depth.

---

## Updated Parameters for All-5

For attempts at all-5 coexistence:
- DECOMP_THRESHOLD (D0-3): 1.3
- DECOMP_THRESHOLD (D4): 2.0

For robust 3+ coexistence:
- DECOMP_THRESHOLD (all): 1.3

---

## Session Status (C1648-C1667)

20 cycles investigating NRM dynamics:
- Trophic: 0%
- Comp-decomp: 72-80%
- Reality grounding: 73-90%
- All-5 optimization: **12%** (threshold=2.0)

