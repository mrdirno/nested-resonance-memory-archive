# Spawn Cost Scaling Validation Analysis

**Date:** November 18, 2025
**Experiments:** 40 (4 spawn_cost values × 10 seeds)
**Hypothesis:** Buffer factor k ≈ 95 is universal across spawn_cost values

---

## EXECUTIVE SUMMARY

**Verdict:** FALSIFIED

**Key Findings:**
- Buffer factor k = 104.69 ± 59.22
- Coefficient of variation: CV = 0.5656 (56.56%)
- Linear scaling: R² = 0.051845
- ANOVA p-value: 0.000000

---

## STATISTICAL RESULTS

### Overall k Statistics

| Metric | Value |
|--------|-------|
| Mean | 104.6937 |
| Std Dev | 59.2186 |
| CV | 0.5656 |
| SEM | 9.3633 |
| Min | 50.2444 |
| Max | 201.0881 |
| Median | 83.7538 |
| N | 40 |

### k by spawn_cost Group

| spawn_cost | Mean k | Std Dev | N |
|------------|--------|---------|---|
| 2.5 | 201.0041 | 0.0531 | 10 |
| 5.0 | 100.5056 | 0.0270 | 10 |
| 7.5 | 67.0055 | 0.0202 | 10 |
| 10.0 | 50.2596 | 0.0120 | 10 |

### Linear Regression (E_min vs spawn_cost)

- **Slope:** 0.0108
- **Intercept:** 502.4765
- **R²:** 0.051845
- **p-value:** 1.58e-01
- **Std Error:** 0.0075

### ANOVA (k across spawn_cost groups)

- **F-statistic:** 44475955.6280
- **p-value:** 0.000000

---

## HYPOTHESIS TESTS

### CV_TEST

**Criterion:** CV(k) < 0.10
**Value:** 0.565637
**Status:** ❌ FAIL
**Description:** Low variation across conditions

### R_SQUARED_TEST

**Criterion:** R² > 0.99
**Value:** 0.051845
**Status:** ❌ FAIL
**Description:** Strong linear E_min vs spawn_cost

### RANGE_TEST

**Criterion:** 85 < k < 105
**Value:** 104.693693
**Status:** ✅ PASS
**Description:** k near expected value ~95

### ANOVA_TEST

**Criterion:** p > 0.05
**Value:** 0.000000
**Status:** ❌ FAIL
**Description:** No significant k difference across spawn_costs

---

## RAW DATA SUMMARY

- spawn_cost=10.0, seed=42: E_min=502.57, k=50.26, pop=19906, success=True
- spawn_cost=2.5, seed=42: E_min=502.39, k=200.96, pop=19915, success=True
- spawn_cost=5.0, seed=42: E_min=502.39, k=100.48, pop=19915, success=True
- spawn_cost=7.5, seed=42: E_min=502.32, k=66.98, pop=19911, success=True

---

**Analysis complete.**
