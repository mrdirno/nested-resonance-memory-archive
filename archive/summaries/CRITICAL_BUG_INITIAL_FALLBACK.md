# CRITICAL BUG: INITIAL Fallback Invalidates Results

**Date:** November 20, 2025
**Severity:** CRITICAL
**Affected Cycles:** C1643-C1646 (possibly earlier)

---

## Summary

The coexistence check in experiment code has a fallback that uses INITIAL values when history length ≤ 10. This fallback triggers for ALL experiments because simulations collapse before cycle 100 (first history recording).

---

## The Bug

```python
finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else INITIAL[i] for i in range(n_levels)}
return {"seed": seed, "coexist": all(finals[i] >= 0.5 for i in range(n_levels))}
```

When `len(histories[i]) <= 10`, finals uses INITIAL values:
- INITIAL = [300, 30, 10, 5, 3, 2, 2]
- All values > 0.5
- Therefore coexist = True for ANY collapsed simulation

---

## Evidence

Testing seeds 140001-140010 with the exact experiment code:

```
Seed 140001: hist_len=1, actual_coexist=True, used_fallback=True
Seed 140002: hist_len=1, actual_coexist=True, used_fallback=True
...
Seed 140010: hist_len=1, actual_coexist=True, used_fallback=True
```

ALL experiments have hist_len=1 (collapsed before cycle 100) and use INITIAL fallback.

---

## Impact

### Invalid Results

The following findings may be completely invalid:

| Cycle | Reported Result | Actual |
|-------|-----------------|--------|
| C1643 | 100/100 = 100% | All fallback |
| C1642 | Attack ×0.5 = 100% | Unknown |
| C1644 | Universal generalization | Unknown |
| C1645 | Pyramid required | Unknown |
| C1646 | 97% resilience | Unknown |

### Synthesis Document

The synthesis document `SYNTHESIS_C1635_C1646_STABLE_DYNAMICS.md` claims "1,860 experiments" validating the attack ×0.5 principle. These experiments may all be false positives.

---

## Root Cause Analysis

### Why Simulations Collapse

Simulations collapse at cycle 46-56, before the first history recording at cycle 100. This means:
1. History has only 0-1 data points
2. Fallback triggers
3. False positive reported

### Why Collapse Happens

The break condition checks ns after predation updates:
```python
if all(n == 0 for n in ns[:3]): break
```

During the predation loop, ns[prey_lvl] is updated. So by cycle 46, all of L0-L2 are consumed, and the break triggers.

### Mystery

When running the actual cycle1643_robustness.py file directly, it reports 100/100 success. But inline code with identical logic shows immediate collapse. This discrepancy needs further investigation.

---

## Recommended Actions

### Immediate

1. **Re-run C1643 with debug output** to verify actual behavior
2. **Check SimulationInterface** for any state persistence issues
3. **Fix the fallback bug** - use 0 instead of INITIAL when history is short

### If Bug Confirmed

1. **Invalidate C1643-C1646** results
2. **Update synthesis document** with retraction
3. **Re-run all experiments** with fixed code
4. **Investigate earlier experiments** for same bug

---

## Proposed Fix

```python
# Instead of:
finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else INITIAL[i] for i in range(n_levels)}

# Use:
finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else 0 for i in range(n_levels)}
```

This ensures collapsed simulations report coexist=False.

---

## Additional Finding: Root Cause Identified

### Cascade Collapse Mechanism

Traced simulation dynamics for seed 140001 with attack ×0.5:

```
C0-C13:  L2-L6 go extinct (insufficient attack rate → starvation)
C13-C25: L1 explodes (no predators) → consumes all L0
C25-C46: L1 dies (no prey)
```

The attack ×0.5 rate is TOO LOW for L2-L6 to survive. They starve, which removes predation pressure from L1, causing L1 to explode and consume all L0.

### Baseline (×1.0) Also Fails

Tested baseline attack rate:
- Runs to cycle 29999 (proper history)
- Final: [200, 0, 0, 0, 0, 0, 0] - only L0 survives
- Coexist: False

**Neither ×0.5 nor ×1.0 achieves coexistence.** The 7-level trophic system is fundamentally unstable with these parameters.

### Conclusion

The C1640-C1646 "100% coexistence" results are ALL false positives due to the INITIAL fallback bug. The experiments didn't actually succeed - they all collapsed before cycle 100, triggering the fallback.

---

## Status

**CONFIRMED - MAJOR RETRACTION REQUIRED**

The entire research arc C1635-C1646 must be retracted. The "attack ×0.5 optimal" finding is incorrect. Both attack rates lead to extinction.

