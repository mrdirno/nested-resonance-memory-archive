# Cycle 1643-1646: Results Invalidation Report

**Date:** November 21, 2025
**Status:** INVALIDATED
**Impact:** Critical - "Optimal Parameters" (Attack ×0.5) do NOT produce coexistence.

---

## Executive Summary

The results of Cycles 1643, 1644, 1645, and 1646, which previously reported "100% Coexistence" and "Robust Stability" under "Optimal Parameters" (Attack ×0.5), have been found to be **FALSE POSITIVES**.

A critical bug in the test scripts caused early simulation collapse (extinction) to be misreported as success due to a fallback mechanism that returned initial population values instead of the actual (zero) final values.

**Corrected Result:** 0% Coexistence (100% Failure/Collapse).

---

## Root Cause Analysis

### 1. The "Fallback" Bug
The test scripts (`cycle1643_robustness.py`, etc.) contained the following logic to calculate final populations:

```python
finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else INITIAL[i] for i in range(n_levels)}
```

*   **Intention:** Handle cases where history recording might be slightly short but valid.
*   **Reality:** When simulations collapsed early (e.g., at cycle 46 due to extinction), `histories` (recorded every 100 cycles) remained empty or very short.
*   **Consequence:** The code fell back to `INITIAL[i]` values (e.g., 300, 30, 10...).
*   **Result:** The coexistence check `all(finals[i] >= 0.5)` passed because `INITIAL` values are > 0.5, reporting "Success" despite total system collapse.

### 2. Import Path Issue
The scripts also had an incorrect import path:
`sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')`
This prevented `core.fractal_agent` from being imported correctly when run from the root directory, potentially masking the issue or causing different failure modes in different environments.

---

## Verification

1.  **Fix Applied:** The import path was corrected, and the fallback logic was removed (replaced with `else 0.0`).
2.  **Re-run (C1643):** The corrected script was run for 100 seeds.
3.  **Outcome:**
    *   **Coexistence:** 0/100 (0%)
    *   **Status:** FAILED
    *   **Observation:** Simulations collapse almost immediately (likely < 100 cycles).

---

## Impact Assessment

*   **Cycle 1643 (Robustness):** INVALID. The "Optimal Parameters" do not support coexistence.
*   **Cycle 1644 (N-Level):** INVALID. Generalization claims are unfounded.
*   **Cycle 1645 (Initial Conditions):** INVALID. Robustness to ICs is unproven.
*   **Cycle 1646 (Perturbation):** INVALID. Resistance claims are false.
*   **Synthesis:** Any theoretical synthesis based on "Attack ×0.5 = Stability" is now unsupported.

## Next Steps

1.  **Acknowledge Failure:** Update `META_OBJECTIVES.md` to reflect the invalidation.
2.  **Re-investigate Parameters:** The parameter search (C1642) that suggested "Attack ×0.5" needs review. If C1642 also had this bug, the entire parameter space exploration might be flawed.
3.  **Debug Collapse:** Determine *why* the system collapses so fast even with reduced attack rates. (Potential causes: predation too efficient even at low rates, starvation due to `e_con`, or `K` decline too aggressive).
