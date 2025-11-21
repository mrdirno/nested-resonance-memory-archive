# Cycle 1710: D1→D2 Ratio as Predictor

**Date:** November 21, 2025
**Cycle:** 1710
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Tested if D1→D2 ratio can predict optimal N across recharge rates.

**Finding: Identifies failures (n=30) but not always optimal N**

---

## Results

### All Recharge Rates

| Rate | Highest D1→D2 | Best Coexist | Correct? |
|------|---------------|--------------|----------|
| 0.05 | n=20 (3.59) | n=35 (100%) | No |
| 0.10 | n=20 (7.10) | n=20 (95%) | Yes |
| 0.15 | n=20 (10.74) | n=20 (100%) | Yes |

### n=30 Consistently Fails

| Rate | D1→D2 Ratio | Coexist |
|------|-------------|---------|
| 0.05 | 0.95 | 55% |
| 0.10 | 1.08 | 50% |
| 0.15 | 2.39 | 50% |

---

## Analysis

### Strength: Failure Detection

D1→D2 ratio consistently identifies n=30 as worst:
- Ratio < 3 at all rates
- Coexistence 50-55%

### Limitation: Optimal Prediction

n=20 has highest ratio at all rates, but:
- At rate 0.05, n=35 has better coexistence
- Ratio alone doesn't capture all success factors

### Parameter Sensitivity

Optimal N appears to shift with recharge rate:
- Rate 0.05: n=35 best (100%)
- Rate 0.10: n=20 best (95%)
- Rate 0.15: n=20/35 tied (100%)

---

## Implications

### For System Design

1. D1→D2 ratio useful for failure detection
2. Target ratio >3 for reliable coexistence
3. Optimal N varies with parameters

### For Mechanism

The n=25 optimum at standard params (rate 0.1) may shift to n=20 or n=35 at different rates. The "universal optimum" is parameter-specific.

---

## Session Status (C1664-C1710)

47 cycles investigating NRM dynamics:
- Complete mechanism (C1697-C1709)
- **Metric prediction: Partial (C1710)**

---

## Conclusions

1. **D1→D2 ratio identifies failures** (n=30 consistently worst)
2. **Not perfect optimal predictor** (2/3 correct)
3. **Optimal N shifts with parameters**
4. **Target ratio >3** for reliable coexistence

