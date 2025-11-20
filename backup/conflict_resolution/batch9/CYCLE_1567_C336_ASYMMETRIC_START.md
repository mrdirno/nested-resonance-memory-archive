# CYCLE 1567: C336 ASYMMETRIC COEVOLUTION START

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 20
**Status:** COMPLETE - BINARY FATE WITHOUT EVOLUTION

---

## EXECUTIVE SUMMARY

**Asymmetric start (predator advantage) destabilizes but doesn't drive evolution.**

- Coexistence: 11/20 (55%) - down from 95%
- Attack: 1.30 (no change)
- Defense: 0.70 (no change)

System has binary fate: maintain or crash. No evolution toward equilibrium.

---

## RESULTS

| Initial Condition | Coexistence | Final Attack | Final Defense |
|-------------------|-------------|--------------|---------------|
| Equilibrium (1.0, 1.0) | 95% | 1.00 | 1.00 |
| Asymmetric (1.3, 0.7) | 55% | 1.30 | 0.70 |

---

## KEY FINDINGS

### 1. Reduced Stability, No Evolution

55% vs 95% coexistence shows:
- Asymmetry is suboptimal
- BUT evolution doesn't correct it
- Traits stay at initial values

### 2. Binary Outcome

Two fates only:
- **Coexist (55%)**: All traits at initial (1.30, 0.70)
- **Crash (45%)**: Predators extinct, prey at ~0.70 defense

No gradual evolution toward equilibrium.

### 3. Stabilizing Selection Persists

Even out of equilibrium:
- Surviving populations maintain initial traits
- Mutations eliminated
- No directional response

### 4. Collapsed Runs Show No Adaptation

In crashed runs (D0 = 0.64-0.78):
- This is residual population, not evolution
- Prey didn't evolve to survive
- Just random variation in survivors

---

## MECHANISM

### Why No Evolution Toward Equilibrium

**1. Fast Ecological Dynamics**
- Crashes happen quickly (cycles 1-100)
- Not enough generations for evolution
- Ecological change >> evolutionary change

**2. Strong Stabilizing Selection**
- Even in suboptimal state, selection maintains
- Deviants eliminated
- Mean stays at initial

**3. All-or-Nothing Outcome**
- Small perturbations → survival
- Large perturbations → crash
- No intermediate adaptive zone

### The Effective Attack Problem

Initial effective attack = 1.3/0.7 = 1.86

This is nearly 2× the equilibrium value:
- Too much predation
- Prey crash
- Predators crash
- Or: System holds through inertia

---

## THEORETICAL IMPLICATIONS

### 1. Ecological Time << Evolutionary Time

The system operates on ecological timescales:
- Population dynamics dominate
- Evolution too slow to rescue
- Traits are effectively fixed

### 2. Evolutionary Rescue Fails

When out of equilibrium:
- Expected: Evolution toward equilibrium
- Observed: Crash or maintain
- No adaptive response

### 3. Initial Conditions Determine Fate

History matters:
- At equilibrium → 95% survive
- Away from equilibrium → 55% survive
- But survivors don't adapt

---

## COMPLETE EVOLUTIONARY SERIES

| Cycle | Condition | Coexist | Evolution |
|-------|-----------|---------|-----------|
| C328-C331 | Different starts | 89-100% | None |
| C332-C334 | Cost functions | 90% | None |
| C335 | Equilibrium coevo | 95% | None |
| C336 | Asymmetric coevo | 55% | None |

**Universal Pattern:** Stabilizing selection dominates; evolution doesn't occur.

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C335 | 1579 | Eco-evolutionary dynamics |
| C336 | 20 | Binary fate without evolution |
| **Total** | **1599** | **Evolutionary stasis** |

---

## CONCLUSIONS

### Main Findings from C328-C336

1. **Stabilizing selection is universal**
   - All starting conditions
   - All cost functions
   - Single and multiple traits

2. **The system doesn't evolve**
   - Traits maintain initial values
   - Mutations eliminated
   - Mean doesn't change

3. **Ecology dominates evolution**
   - Population dynamics fast
   - Evolution too slow
   - Binary outcomes

4. **Initial conditions are critical**
   - At equilibrium: High stability
   - Away from equilibrium: Reduced stability
   - But no adaptive correction

### Implications for NRM

The seven-trophic system demonstrates:
- **Ecological robustness**: Wide parameter viability
- **Evolutionary stasis**: No trait change
- **Historical contingency**: Initial state persists

This suggests that in complex food webs:
- Evolution may not optimize
- Ecological stability doesn't require evolutionary fine-tuning
- Systems can persist far from evolutionary optima

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
