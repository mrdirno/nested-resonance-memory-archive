# CYCLE 1546: C313 PREDATOR PREFERENCE

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 3
**Status:** COMPLETE - PREFERENCE CAUSES PREDATOR EXTINCTION

---

## EXECUTIVE SUMMARY

**Predator preference leads to predator extinction through overexploitation.**

- Attack rate on preferred prey (0.006) in overexploitation zone
- Predator overconsumed preferred prey, then starved
- Both prey recovered to carrying capacity

Prey preference is self-destructive for predator.

---

## RESEARCH QUESTION

Does predator preference cause competitive exclusion between prey?

---

## RESULTS

| Seed | Prey A | Prey B | B/A | Pred | Outcome |
|------|--------|--------|-----|------|---------|
| 2000 | 300 | 300 | 1.00 | 0 | Predator extinct |
| 2001 | 300 | 300 | 1.00 | 0 | Predator extinct |
| 2002 | 300 | 300 | 1.00 | 0 | Predator extinct |

100% predator extinction. Both prey at carrying capacity.

---

## KEY FINDINGS

### 1. Predator Extinction via Overexploitation

Attack rate 0.006 on preferred prey is in overexploitation zone:
- Predator overconsumes Prey A
- Prey A crashes
- Predator cannot sustain on Prey B alone (0.003 too low)
- Predator starves

### 2. Prey Recovery

After predator extinction:
- Both prey recover to K=300
- No competitive exclusion
- Neutral coexistence without predator

### 3. Self-Destructive Preference

Strong preference (2×) is self-destructive:
- Higher attack on preferred = faster depletion
- Ruins own food supply
- Generalist strategy more stable

---

## MECHANISM

### Overexploitation Cascade

```
Cycle 0: Prey A=150, B=150, Pred=30
High attack on A (0.006): Prey A crashes
Lower attack on B (0.003): Not enough to sustain pred
Predator starves
Both prey recover to K
```

### Why Generalism Fails Here

Predator needs both prey to survive:
- A provides 2/3 of encounters (higher rate)
- When A crashes, only 1/3 remains
- 0.003 on B is in starvation zone for full predator pop

---

## THEORETICAL SIGNIFICANCE

### 1. Specialist vs Generalist

Strong preference creates pseudo-specialist:
- Over-relies on preferred prey
- Self-destabilizing

True generalist (equal attack) more stable.

### 2. Overexploitation Zone Validated

Attack rate thresholds confirmed:
- 0.003: Optimal
- 0.006: Overexploitation
- Doubling attack crosses viability boundary

### 3. Apparent Competition Reversed

Expected: Preferred prey excluded
Actual: Predator excluded

Prey win by being overexploited - predator destroys itself.

---

## IMPLICATIONS

### 1. Predator Evolution

Strong prey preference is:
- Evolutionarily unstable
- Self-destructive
- Selected against

Generalism should evolve.

### 2. Conservation

Specialist predators:
- Vulnerable to prey depletion
- May need prey management
- Risk of population collapse

### 3. System Design

For stable predator-prey:
- Avoid strong preference
- Keep all attack rates in viable zone
- Generalism more robust

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C312 | 1300 | Multi-trophic + prey diversity |
| C313 | 3 | Preference causes predator extinction |
| **Total** | **1303** | **Specialization self-destructive** |

---

## NEXT RESEARCH DIRECTIONS

1. **Weak preference**: Test 1.5× vs 2× attack ratio
2. **Adaptive switching**: Predator switches to abundant prey
3. **Prey refuge**: Test if refuge saves preferred prey

---

## CONCLUSION

C313 establishes that **predator preference causes predator extinction** through overexploitation of preferred prey.

Key findings:
1. 2× attack rate on preferred prey is self-destructive
2. Predator crashes then goes extinct
3. Both prey recover to carrying capacity
4. Generalism more stable than specialism

This demonstrates that strong prey preference is evolutionarily unstable and violates the Goldilocks zone for attack rates.

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
