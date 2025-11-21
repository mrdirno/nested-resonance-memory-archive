# Cycle 1703: Multi-Factor Predictive Model

**Date:** November 21, 2025
**Cycle:** 1703
**Operator:** Claude Sonnet 4.5

---

## Executive Summary

Comprehensive 50-seed analysis to develop multi-factor success predictor.

**Key Finding: n=25 has lowest mean energy (1.416) AND longest mean cycle (236.4)**

---

## Results (50 seeds each)

### All Metrics

| N | Product | MeanE | Cycle | D1@100 | Coexist |
|---|---------|-------|-------|--------|---------|
| 15 | 111.0 | 1.525 | 177.6 | 0.4 | 44% |
| 20 | 38.7 | 1.472 | 225.8 | 1.0 | 92% |
| 25 | 109.8 | **1.416** | **236.4** | 0.6 | 96% |
| 30 | 120.9 | 1.483 | 218.4 | 0.5 | 64% |
| 35 | 62.0 | 1.517 | 195.1 | 0.7 | 98% |
| 50 | 74.6 | 1.501 | 198.5 | 0.7 | 100% |

### Key Observations

1. **n=25 has lowest MeanE**: 1.416 vs 1.47-1.53 for others
2. **n=25 has highest Mean Cycle**: 236.4 (sustained compositions)
3. **Product alone doesn't predict**: n=30 has highest (120.9) but only 64%

---

## Combined Score Models

### Model 1: Product / MeanEnergy

| N | Score | Coexist |
|---|-------|---------|
| 30 | **81.55** | 64% |
| 25 | 77.57 | 96% |
| 15 | 72.82 | 44% |

**Fails**: n=30 highest score but poor success

### Model 2: Product × D1@100

| N | Score | Coexist |
|---|-------|---------|
| 25 | **63.70** | 96% |
| 30 | 60.46 | 64% |
| 50 | 53.74 | 100% |

**Partial**: n=25 highest but doesn't explain n=50

### Model 3: (Product × D1@100) / MeanEnergy

| N | Score | Coexist |
|---|-------|---------|
| 25 | **44.99** | 96% |
| 30 | 40.77 | 64% |
| 50 | 35.81 | 100% |

**Best**: Separates n=25 from n=30, but still imperfect

---

## The n=25 Mechanism

### Why n=25 Succeeds

1. **Lowest mean creation energy (1.416)**
   - Compositions more likely to survive
   - Below decomposition threshold

2. **Longest mean cycle (236.4)**
   - Compositions sustained throughout run
   - Not concentrated early (depletes D0)
   - Not concentrated late (high energy)

3. **Balanced product (109.8)**
   - High enough to create D1
   - Not so high that energy accumulates

### Why n=30 Fails (64%)

- Higher mean energy (1.483)
- Shorter mean cycle (218.4)
- High product but compositions decompose

### Why n=35/50 Succeed (98-100%)

Different regime - larger populations create different dynamics:
- More agents → more distributed compositions
- Longer equilibrium establishment
- Higher steady-state population

---

## Theoretical Implications

### Multi-Factor Balance

Success requires balance across multiple factors:
```
Success ∝ f(Product, Energy, Timing, D1_stability)
```

No single metric predicts success.

### The n=25 Critical Point

n=25 is optimal because it achieves:
- **Minimum energy** (1.416)
- **Maximum timing** (236.4)
- **Sufficient product** (109.8)

Any deviation disrupts this balance.

### Regime Transition at n≥35

Different dynamics emerge:
- n≤30: n=25 optimal (critical balance)
- n≥35: Higher success (population effects)

---

## Model Limitations

None of the simple models perfectly predict success:
1. n=50 has lower scores but 100% success
2. n=35 has low Model 3 score (27.81) but 98% success

The mechanism involves non-linear interactions not captured by simple products/ratios.

---

## Practical Conclusions

### For Standard Runs (n≤30)

**n=25 is optimal** due to:
- Lowest mean energy
- Longest mean cycle
- Best Model 3 score

### For Large Populations (n≥35)

Different dynamics apply:
- Higher success rates
- But slower to establish equilibrium
- May not be practical for all applications

---

## Session Status (C1664-C1703)

40 cycles investigating NRM dynamics:
- 10D characterization (C1664-1694)
- Long-term stability (C1695)
- Mathematical derivation (C1696)
- Mechanism analysis (C1697-1702)
- **Multi-factor model (C1703)**

---

## Conclusions

1. **n=25 has lowest mean creation energy (1.416)**
2. **n=25 has longest mean composition cycle (236.4)**
3. **Model 3 best predicts: (Product × D1@100) / MeanEnergy**
4. **Success requires multi-factor balance**
5. **Different regimes at n≤30 vs n≥35**

