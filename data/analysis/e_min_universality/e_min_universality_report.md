# E_min Universality Analysis (Across f_spawn and spawn_cost)

**Date:** November 18, 2025
**Total Experiments:** 140 (50 V6b + 50 V6c + 40 spawn_cost)
**Hypothesis:** E_min ≈ 502.5 units is universal across f_spawn and spawn_cost

---

## EXECUTIVE SUMMARY

**Verdict:** FALSIFIED

**Key Findings:**
- E_min overall = 512.05 ± 25.40 units
- Coefficient of variation: CV = 0.0496 (4.96%)
- ANOVA (E_min vs f_spawn): p = 0.000000
- E_min VARIES with f_spawn
- Correlation with f_spawn: r = -0.6611, R² = 0.4371

---

## CAMPAIGN SUMMARIES

### V6b Campaign (spawn_cost=5.0, varying f_spawn)
- Experiments: 50
- f_spawn values tested: 5 (0.10%, 0.25%, 0.50%, 0.75%, 1.00%)
- Seeds: 10 per condition

### V6c Campaign (spawn_cost=7.5, varying f_spawn)
- Experiments: 50
- f_spawn values tested: 5 (0.10%, 0.25%, 0.50%, 0.75%, 1.00%)
- Seeds: 10 per condition

### Spawn Cost Campaign (f_spawn=0.005, varying spawn_cost)
- Experiments: 40
- spawn_cost values tested: 4 (2.5, 5.0, 7.5, 10.0)
- Seeds: 10 per condition

---

## STATISTICAL RESULTS

### Overall E_min Statistics (All 90 experiments)

| Metric | Value |
|--------|-------|
| Mean | 512.0523 |
| Std Dev | 25.3975 |
| CV | 0.0496 |
| Min | 500.5166 |
| Max | 587.0886 |

### E_min by f_spawn

| f_spawn | Mean E_min | Std Dev | Min | Max | N |
|---------|------------|---------|-----|-----|---|
| 0.00100 | 582.9380 | 3.4031 | 578.2293 | 587.0886 | 10 |
| 0.00250 | 511.1617 | 0.7701 | 510.1511 | 512.6358 | 10 |
| 0.00500 | 502.5407 | 0.1329 | 502.2697 | 502.8258 | 50 |
| 0.00750 | 501.0530 | 0.0537 | 500.9616 | 501.1446 | 10 |
| 0.01000 | 500.6144 | 0.0675 | 500.5166 | 500.7425 | 10 |

### Statistical Tests

**ANOVA (E_min across f_spawn groups):**
- F-statistic: 11018.6438
- p-value: 0.000000
- Interpretation: E_min VARIES with f_spawn

**Correlation (E_min vs f_spawn):**
- Pearson r: -0.6611
- R²: 0.4371
- p-value: 1.33e-12

---

## HYPOTHESIS TESTS

### CV_TEST

**Criterion:** CV(E_min) < 0.10
**Value:** 0.049599
**Status:** ✅ PASS
**Description:** Low variation in E_min overall

### ANOVA_TEST

**Criterion:** ANOVA p > 0.05
**Value:** 0.000000
**Status:** ❌ FAIL
**Description:** E_min does not vary significantly with f_spawn

### RANGE_TEST

**Criterion:** 495 < E_min < 510
**Value:** 512.052285
**Status:** ❌ FAIL
**Description:** E_min near predicted value ~502.5

---

**Analysis complete.**
