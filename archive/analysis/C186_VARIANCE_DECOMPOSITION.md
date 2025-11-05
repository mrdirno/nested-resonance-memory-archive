# Variance Decomposition Analysis

**Purpose:** Quantify sources of variance in hierarchical NRM experiments
**Framework:** Extension 2 (Hierarchical Energy Dynamics)

**Sample size:** n=3 experiments

## Runtime Variance

- **Mean:** 1483.6 seconds (24.7 minutes)
- **Stdev:** 87.1 seconds (1.5 minutes)
- **Range:** 1383.1 - 1535.4 seconds
- **Coefficient of Variation:** 5.9%

## Variance Components

### Seed Variance

- **Variance:** 7579.06
- **Stdev:** 87.06 (1.5 minutes)
- **Percent of Total:** 100.0%
- **Description:** Stochastic variance across 3 random seeds

## Dynamical Metric Correlations

### Runtime vs. CV

- **Correlation (r):** 1.000
- **Interpretation:** Strong
- **p-value (est):** 0.050

### Runtime vs. Migrations

- **Correlation (r):** 0.000
- **Interpretation:** Weak
- **p-value (est):** 1.000

## Interpretation

✅ **Moderate runtime variance** (CV < 50%)

Runtime is relatively consistent across seeds, suggesting:
- Robust computational scaling
- Limited hierarchical amplification

## Dynamical Metrics Summary

### CV (Coefficient of Variation)

- Mean: 47.5%
- Stdev: 10.3%
- Range: 35.6% - 53.6%

### Migrations

- Mean: 14.0
- Stdev: 0.0
- Range: 14-14

---

**Generated:** 2025-11-05 (Cycle 1021)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude <noreply@anthropic.com>