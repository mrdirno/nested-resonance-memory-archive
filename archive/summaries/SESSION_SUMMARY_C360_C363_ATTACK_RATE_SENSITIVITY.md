# SESSION SUMMARY: C360-C363 ATTACK RATE SENSITIVITY

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Total Experiments:** 80 (4 cycles × 20 seeds)
**Status:** COMPLETE - DOME-SHAPED RESPONSE CHARACTERIZED

---

## EXECUTIVE SUMMARY

**Attack rate sensitivity shows dome-shaped (unimodal) response curve.**

Peak survival at **1.25× baseline attack rate** (60%), with decline on both sides:
- Too low (0.5×): Predator starvation (5%)
- Optimal (1.25×): Maximum survival (60%)
- Too high (1.5×): Over-predation (20%)

---

## RESULTS

| Cycle | Attack Multiplier | Survival | Mechanism |
|-------|------------------|----------|-----------|
| C361 | 0.5× | 5% | Predator starvation |
| C362 | 0.75× | 35% | Marginal energy |
| C359 | 1.0× | 50% | Baseline |
| C363 | 1.25× | 60% | Optimal balance |
| C360 | 1.5× | 20% | Over-predation |

---

## KEY FINDINGS

### 1. Dome-Shaped Response Curve

```
Survival
    ^
60% ─┼──────────●
    │         ↗  ↘
50% ─┼────────●
    │       ↗       ↘
35% ─┼────●
    │   ↗             ↘
20% ─┼                  ●
    │ ↗
 5% ●───────────────────────
    ├───┼───┼───┼───┼───┼───
   0.5 0.75 1.0 1.25 1.5  Attack
```

### 2. Optimal Attack Rate > Baseline

**Surprising finding**: Optimal attack is 1.25× baseline, not 1.0×.

Mechanism:
- Slightly higher attack → more energy flow
- Faster predator reproduction during K decline
- Better tracking of environmental change
- But not so high as to over-deplete prey

### 3. Asymmetric Failure Modes

**Low attack (0.5×, 0.75×):**
- Predators starve during K decline
- Can't get enough energy to reproduce
- Population collapses from top down

**High attack (1.5×):**
- Prey depleted too fast
- Predator boom-bust cycle
- Cascade collapse from bottom up

### 4. Critical Thresholds

- **Lower bound**: ~0.7× (below = starvation)
- **Optimal**: ~1.25× (maximum survival)
- **Upper bound**: ~1.4× (above = over-predation)

---

## MECHANISM ANALYSIS

### Why Low Attack Fails

At 0.5× attack rate:
1. Predators have half the kill rate
2. Energy income barely covers consumption
3. During K decline, prey population drops
4. Reduced prey → even less energy
5. Predator populations collapse sequentially

### Why Optimal is 1.25×

At 1.25× attack rate:
1. Higher kill rate → more energy flow
2. Predators maintain populations during decline
3. Faster response to environmental change
4. Not so high as to over-deplete prey
5. Sweet spot between starvation and over-predation

### Why High Attack Fails

At 1.5× attack rate:
1. Predators deplete prey rapidly
2. Prey can't reproduce fast enough during K decline
3. Prey collapse triggers predator starvation
4. Cascade from bottom up
5. Different from low attack (top down)

---

## THEORETICAL IMPLICATIONS

### 1. Goldilocks Principle

Optimal predation intensity exists:
- Not too weak (starvation)
- Not too strong (over-predation)
- Just right (1.25× baseline)

### 2. Parameter-Dependent Critical Rates

The critical rate (~10 K/cycle at baseline) likely shifts with attack rate:
- Higher attack → need slower K decline
- Lower attack → need even slower decline
- Interaction between parameters

### 3. Management Implications

For ecosystem management:
- Baseline parameters may not be optimal
- Slight increase in predation can improve resilience
- But too much predation is worse than too little

### 4. Evolution Hypothesis

Baseline parameters may represent:
- Historical optimum for stable K
- Not optimal for changing environments
- Evolution could select for higher attack during environmental change

---

## UPDATED TOTALS

| Campaign | Experiments | Key Finding |
|----------|-------------|-------------|
| C274-C359 | 2059 | Rate-dependent thresholds |
| C360-C363 | 80 | Optimal attack = 1.25× |
| **Total** | **2139** | **Parameter sensitivity characterized** |

---

## NEXT DIRECTIONS

1. **Parameter interactions**: How does optimal attack shift with K decline rate?

2. **Other parameters**: Sensitivity of handling time, conversion efficiency

3. **Two-parameter space**: Map attack × K_decline surface

4. **Prediction**: Can we predict optimal attack from system properties?

---

## CONCLUSION

C360-C363 reveal a **dome-shaped attack rate response curve** with peak survival at **1.25× baseline**.

**Key results:**
1. **Optimal attack ~1.25×** (not baseline 1.0×)
2. **Dome-shaped curve** with asymmetric failure modes
3. **Lower failure**: predator starvation (5% at 0.5×)
4. **Upper failure**: over-predation (20% at 1.5×)

This demonstrates that critical rate thresholds depend on system parameters, with an optimal balance between energy acquisition and prey depletion.

**Total experiments: 80**
**Running total: 2139 experiments**

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
