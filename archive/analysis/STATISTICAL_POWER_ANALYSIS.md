# Statistical Power Analysis

**Purpose:** Determine sample size sufficiency for detecting predicted effects
**Target:** Power ≥80% (80% probability of detecting real effects)
**Significance Level:** α=0.05

## Power Summary

| Test | Effect Size | n | Power | Adequate? | Recommended n |
|------|-------------|---|-------|-----------|---------------|
| one_sample_t | 50.000 | 10 | 100.0% | ✅ Yes | N/A |
| one_sample_t | 2.000 | 10 | 100.0% | ✅ Yes | N/A |
| anova | 1.100 | 10 | 93.6% | ✅ Yes | N/A |
| correlation | 0.700 | 10 | 63.1% | ⚠️ No | 14 |

## Detailed Analysis

### Test 1: One Sample T

- **Effect Size**: 50.000
- **Sample Size**: n=10
- **Alpha**: 0.05
- **Power**: 100.0%
- **Adequacy**: ✅ Sufficient (power ≥80%)
- **Notes**: Testing H0: μ=5.0% vs H1: μ<5.0%. Observed: μ=0.00%, SD=0.10%

### Test 2: One Sample T

- **Effect Size**: 2.000
- **Sample Size**: n=10
- **Alpha**: 0.05
- **Power**: 100.0%
- **Adequacy**: ✅ Sufficient (power ≥80%)
- **Notes**: Testing H1: μ∈[10.0,20.0]. Observed: μ=14.00, SD=2.00

### Test 3: Anova

- **Effect Size**: 1.100
- **Sample Size**: n=10
- **Alpha**: 0.05
- **Power**: 93.6%
- **Adequacy**: ✅ Sufficient (power ≥80%)
- **Notes**: ANOVA with 3 groups. Means: [10.0, 5.0, 2.0], Pooled SD: 3.00

### Test 4: Correlation

- **Effect Size**: 0.700
- **Sample Size**: n=10
- **Alpha**: 0.05
- **Power**: 63.1%
- **Adequacy**: ⚠️ Underpowered (power <80%)
- **Recommended n**: 14 (to achieve 80% power)
- **Notes**: Testing H0: ρ=0 vs H1: ρ≠0. Expected r=0.70

## Interpretation

⚠️ **Some tests underpowered** (3/4 adequate)

Recommendations:
- **correlation**: Increase n from 10 to 14

---

**Generated:** 2025-11-05 (Cycle 1023)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude <noreply@anthropic.com>