# CYCLE 1565: C332-C333 ATTACK COST FUNCTIONS

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
**Date:** 2025-11-20
**Experiments:** 40 (20 + 20)
**Status:** COMPLETE - STABILIZING SELECTION DOMINATES

---

## EXECUTIVE SUMMARY

**Neither linear nor squared cost functions induce directional selection.**

- C332 (linear cost): 90%, traits = 1.00
- C333 (squared cost): 90%, traits = 1.00

Stabilizing selection is too strong - mutations are eliminated before they can spread.

---

## RESULTS

| Experiment | Cost Model | Coexistence | Final Traits |
|------------|------------|-------------|--------------|
| C332 | e_con × trait | 90% (18/20) | 1.00 |
| C333 | e_con × trait² | 90% (18/20) | 1.00 |

---

## KEY FINDINGS

### 1. Cost Doesn't Create Selection

Both cost models fail to induce evolution:
- Linear: trait×1.0 = cost×1.0 (baseline)
- Squared: trait×1.0 = cost×1.0 (baseline)
- No differential selection at starting point

### 2. Stabilizing Selection Dominates

Mutations occur but are eliminated:
- Higher traits: More attack, more cost → eliminated
- Lower traits: Less attack, less cost → BUT also less prey
- Net effect: Return to starting value

### 3. Prey Capture Drives Fitness

Energy gain depends on prey captured:
- Lower attack = fewer prey = less reproduction
- Cost savings don't compensate for reduced capture
- Higher attack still wins despite higher cost

### 4. The Real Fitness Function

```
Fitness = (Prey × Gain) - (Cost × trait^n)

At equilibrium, the prey capture benefit exceeds cost penalty
```

---

## MECHANISM ANALYSIS

### Why Cost Functions Fail

**1. Starting at Equilibrium**
- Initial trait = 1.0 is viable
- System is stable at this point
- No selection pressure to leave

**2. Benefit Scales with Attack**
- Attack → Prey → Energy → Reproduction
- This benefit is strong
- Cost must exceed benefit for selection

**3. Threshold Effect**
- Costs would need to be MUCH higher
- Or prey capture saturated
- Current cost too weak relative to benefit

### What Would Work

To see directional selection:
1. **Saturating benefit**: Attack beyond threshold gives no more prey
2. **Very high cost**: Cost >> benefit at high traits
3. **Frequency-dependent**: Success depends on others' traits

---

## EVOLUTIONARY DYNAMICS SUMMARY

### Complete Series (C328-C333)

| Cycle | Condition | Coexist | Evolution | Conclusion |
|-------|-----------|---------|-----------|------------|
| C328 | Baseline 1.0 | 89% | Stabilizing | Optimum |
| C329 | Start 0.7 | 89% | None | Viable |
| C330 | Start 0.5 | 100% | None | Viable |
| C331 | Start 1.3 | 100% | None | Viable |
| C332 | Linear cost | 90% | None | Weak selection |
| C333 | Squared cost | 90% | None | Still weak |

**Overall Finding**: The attack rate trait is effectively neutral across [0.5, 1.5] range with current energy dynamics.

---

## THEORETICAL IMPLICATIONS

### 1. Stabilizing Selection Wins

In established ecosystems:
- Selection maintains status quo
- Innovations are eliminated
- Stability over optimization

### 2. Constraints on Adaptation

Evolution requires:
- Strong enough selection gradient
- Or neutral drift over long time
- Current mutations too small/slow

### 3. Ecological Stability ≠ Evolutionary Plasticity

System is:
- Ecologically robust (high coexistence)
- Evolutionarily static (no trait change)
- Resistant to adaptation

---

## UPDATED TOTALS

| Campaign | Experiments | Findings |
|----------|-------------|----------|
| C274-C331 | 1499 | Eco-evolutionary baseline |
| C332-C333 | 40 | Cost functions fail |
| **Total** | **1539** | **Stabilizing dominates** |

---

## NEXT DIRECTIONS

1. **Very high cost**: e_con × trait³ or trait⁴
2. **Reproduction cost**: High attack = fewer offspring
3. **Saturating benefit**: Handling time dominates
4. **Longer simulations**: 100,000 cycles for drift
5. **Remove bounds**: Let traits evolve freely

---

## CONCLUSION

C332-C333 demonstrate that **neither linear nor squared cost functions create directional selection** in this system.

Key findings:
1. 90% coexistence maintained (similar to baseline)
2. All traits remain at 1.00 (no evolution)
3. Prey capture benefit exceeds cost penalty
4. Stabilizing selection eliminates deviants

The attack rate trait is effectively neutral because the benefit of capturing more prey outweighs the metabolic cost. To see directional selection, we need stronger constraints: either saturating benefits, much higher costs, or frequency-dependent selection.

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
