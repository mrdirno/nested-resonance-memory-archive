# Paper 7 Phase 6: Debugging Stochastic Model Extinction

**Date:** 2025-10-31 (Cycle 787)
**Author:** Aldrin Payopay
**Issue:** Stochastic demographic V4 model goes to extinction (N → 0) despite starting at deterministic steady state

---

## Problem Statement

Running `paper7_phase6_stochastic_demographic_v4.py` shows:
- Test 1 (N=10 initial): Extinction (mean N = 0.00)
- Test 2 (N=215 steady state): Extinction (mean N = 0.00)

Both tests go to extinction despite theoretical birth rate > death rate.

---

## Theoretical Analysis

At steady state (E~2411, N~215, phi~0.61):
- rho = E/N = 11.22 (>> threshold of 5.0)
- energy_gate ≈ 1.0
- lambda_c = 2.5 × 1.0 × 0.61² = 0.93 per capita
- crowding = (215/100)² = 4.62
- lambda_d = 0.4 × (1 + 0.1 × 4.62) = 0.58 per capita

**Expected:** Birth rate (0.93) > death rate (0.58) → population should persist

**Observed:** Extinction in all 20 runs

---

## Hypothesis: State Update Ordering Bug

Current implementation (lines 206-217):
```python
for i in range(1, n_steps):
    # 1. Update continuous variables (E, phi, theta_rel)
    state = self.ode_step(state, R)  # Returns [E_new, N_old, phi_new, theta_rel_new]
    
    # 2. Update discrete population (N)
    N_new = self.poisson_step(state, R)  # Uses [E_new, N_old, phi_new, ...]
    state[1] = N_new
```

**Problem:** poisson_step() computes rates using:
- E_new (updated based on N_old)
- N_old (not yet updated)
- phi_new (updated based on N_old)

This creates a mismatch where:
1. ODE step advances E and phi assuming N hasn't changed
2. Poisson step then updates N based on the new E and phi
3. But the new E and phi were calculated for the OLD N

This feedback mismatch could cause E to grow unbounded (no consumption), rho → ∞, but then when N updates, it doesn't match the energy dynamics.

---

## Hypothesis: dE/dt Equation Bug

Line 136:
```python
dE_dt = gamma * R - alpha * lambda_c * E - beta * N * E
```

This uses:
- gamma * R: Energy input
- alpha * lambda_c * E: Energy consumed by births
- beta * N * E: Energy consumed by maintenance

If N drops toward 0:
- Maintenance term → 0
- Birth term depends on lambda_c which depends on energy gate and phi
- Energy could accumulate without being consumed

---

## Next Steps

1. Add debug logging to track E, N, phi, lambda_c, lambda_d over time
2. Check if rho = E/N diverges (N → 0 while E > 0)
3. Verify rate calculations at each step
4. Compare stochastic trajectories to deterministic baseline
5. Test alternative update schemes (e.g., operator splitting)

---

## Alternative Implementation Ideas

**Option 1: Synchronized Updates**
- Compute rates using current state [E, N, phi]
- Update all variables simultaneously
- Avoid feedback mismatch

**Option 2: Gillespie Algorithm**
- Use exact stochastic simulation
- Choose next event (birth or death) based on rates
- Advance time by exponential random variable
- More accurate for small populations

**Option 3: Tau-Leaping with Checks**
- Current Poisson approach is tau-leaping
- Add stability checks (e.g., don't let N change by more than 10% per step)
- Reduce dt if large fluctuations occur

---

## Status: DEBUGGING IN PROGRESS

Investigation ongoing - will document findings and implement fix.

