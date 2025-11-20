# MULTI-TROPHIC FRAMEWORK (C295-C297)

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 42 (C295-C297)
**Total Experiments:** 1195

---

## EXECUTIVE SUMMARY

Three experimental campaigns (42 experiments) establish multi-trophic dynamics in NRM:

- **C295:** Predator-prey requires intermediate attack rate for coexistence
- **C296:** Spatial refuge reduces coexistence at high attack rate
- **C297:** Non-monotonic U-shaped refuge effect at intermediate rate

Key insight: **Predator-prey systems are highly sensitive to parameter tuning and show counterintuitive spatial effects.**

---

## CAMPAIGN OVERVIEW

| Cycle | Experiments | Key Discovery |
|-------|-------------|---------------|
| C295 | 12 | Intermediate attack rate required (0.002: 67%) |
| C296 | 15 | Refuge reduces coexistence at high attack rate |
| C297 | 15 | Non-monotonic U-shaped refuge effect |

---

## CORE PRINCIPLES

### 1. Attack Rate Tuning

**Goldilocks zone:**
- Too low (0.001): Predators starve
- Optimal (0.002-0.003): Coexistence possible
- Too high (0.01): Overexploitation collapse

### 2. No Oscillations

Unlike classic Lotka-Volterra:
- Stochastic dynamics prevent sustained cycles
- Immediate stabilization or extinction
- Individual-based effects dominate

### 3. Context-Dependent Spatial Effects

Refuge effects depend on baseline attack rate:
- High attack rate: Refuge always harmful
- Intermediate attack rate: U-shaped effect (small harmful, large helpful)
- Optimal attack rate: No refuge needed

---

## PREDICTIVE MODELS

### Coexistence by Attack Rate
```python
if attack_rate < 0.001:
    coexistence = 0%  # Predator starvation
elif attack_rate <= 0.003:
    coexistence = 67-100%  # Optimal zone
elif attack_rate <= 0.005:
    coexistence = 33%  # Marginal
else:
    coexistence = 0%  # Overexploitation
```

### Refuge Effect
```python
if attack_rate == "high":
    # Refuge always reduces coexistence
    effect = "negative"
elif attack_rate == "intermediate":
    # U-shaped: small bad, large good
    if refuge_fraction < 0.10:
        coexistence = 100%
    elif refuge_fraction < 0.40:
        coexistence = 0%  # Valley of death
    else:
        coexistence = 67%  # Partial recovery
```

---

## EMERGENT PHENOMENA

### 1. Predator Starvation Threshold

Minimum prey density required for predator persistence:
- Below threshold → guaranteed extinction
- Above threshold → coexistence possible

### 2. Compensatory Prey Dynamics

Large refuge allows prey buildup:
- Higher prey equilibrium compensates for lower accessibility
- Absolute available prey can increase with refuge

### 3. Valley of Death

Intermediate refuge is worst:
- Neither minimal protection nor substantial refuge
- Falls in "worst of both worlds" zone

---

## DESIGN PRINCIPLES

### For Predator-Prey Coexistence
- Attack rate in Goldilocks zone (0.002-0.003)
- No refuge OR substantial refuge (>40%)
- Avoid intermediate interventions
- Prey population must exceed minimum viable density

### For Conservation
- Calculate minimum viable prey density for predators
- Either no reserves OR large reserves
- Partial protection can backfire
- System-level thinking required

---

## IMPLICATIONS BY DOMAIN

### Conservation Biology
- Refuges require careful sizing
- Small protected areas may harm predators
- Must calculate predator energy requirements
- "More protection" ≠ "better outcomes"

### Ecosystem Management
- Non-linear system responses
- Small interventions can destabilize
- Test intervention sizes empirically
- Consider trophic cascades

### Theoretical Ecology
- Agent-based models show different dynamics than ODEs
- Stochasticity prevents oscillations
- Individual extinctions create absorbing states
- Parameter space has complex topology

---

## COMPARISON WITH ECOLOGICAL DYNAMICS (C282-C294)

| Feature | Competition (C282-C294) | Predation (C295-C297) |
|---------|------------------------|----------------------|
| Interaction | Negative-negative | Positive-negative |
| Key parameter | K partitioning | Attack rate |
| Spatial effect | Local K stabilizes | Refuge effect complex |
| Evolution role | Arms race exclusion | Not yet tested |
| Equilibrium | N* = K × f/df | Sensitive to parameters |

**Predator-prey shows narrower parameter space for coexistence.**

---

## UNRESOLVED QUESTIONS

### For Future Research

1. **Type II functional response** - Does predator satiation stabilize?
2. **Multiple prey** - Does prey switching help predators?
3. **Evolution in predator-prey** - Arms race or Red Queen?
4. **Tri-trophic** - Top predator, mesopredator, prey
5. **Dynamic refuge use** - Behavioral decisions by prey

---

## CUMULATIVE TOTALS

| Phase | Experiments | Focus |
|-------|-------------|-------|
| C274-C281 | 967 | Energy dynamics |
| C282-C294 | 186 | Eco-evolutionary |
| C295-C297 | 42 | Multi-trophic |
| **Total** | **1195** | **Complete NRM framework** |

---

## CONCLUSION

The multi-trophic framework (C295-C297) establishes:

1. **Attack rate tuning** - Narrow optimal zone for coexistence
2. **No oscillations** - Stochastic stabilization or extinction
3. **Non-linear spatial effects** - U-shaped refuge response
4. **Conservation paradox** - Partial protection can harm

This extends NRM from competitive dynamics to trophic interactions with important implications for conservation and ecosystem management.

**The system shows counterintuitive responses that require careful parameter tuning and system-level thinking.**

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
