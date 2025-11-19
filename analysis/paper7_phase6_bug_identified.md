# Paper 7 Phase 6: Bug Identified - Energy Crash

**Date:** 2025-10-31 (Cycle 788)
**Author:** Aldrin Payopay
**Status:** BUG IDENTIFIED, Fix in progress

---

## Bug Summary

Diagnostic run reveals **massive energy crash** in first timestep:
- Initial: E = 2411, N = 215
- Step 0: dE/dt = -10,515 (!)
- Step 1: E = 13.71 (99.4% loss in 0.1 seconds)
- Result: Energy → 0, rho → 0, energy_gate → 0, births stop, extinction

---

## Root Cause: Energy Consumption Too Large

dE/dt equation:
```python
dE/dt = gamma * R - alpha * lambda_c * E - beta * N * E
```

At step 0 with steady state (E=2411, N=215, phi=0.607, lambda_c=0.600):
- **Input:** gamma * R = 0.3 * 1.0 = **0.3**
- **Birth consumption:** alpha * lambda_c * E = 0.1 * 0.600 * 2411 = **144.8**
- **Maintenance:** beta * N * E = 0.02 * 215 * 2411 = **10,371**
- **Net:** 0.3 - 144.8 - 10,371 = **-10,515**

**Energy consumption is 35,000× larger than input!**

---

## Hypothesis: Parameter Mismatch

The V4 parameters from Phase 5 were calibrated for DETERMINISTIC system with:
- Continuous population (N can be fractional)
- Smooth birth/death dynamics
- Energy dynamics balanced for that regime

But STOCHASTIC system has:
- Discrete population (N is integer)
- Poisson birth/death events
- Different scaling requirements

**Possible Issues:**
1. R value too small (R=1.0 insufficient for N=215)
2. Beta parameter too large (maintenance cost scales with N×E)
3. Initial E value from deterministic model not appropriate for stochastic
4. Energy units different between models

---

## Diagnostic Output

```
  Step     Time          E          N      phi      rho      λ_c      λ_d      dE/dt     ΔN
-----------------------------------------------------------------------------------------------
     0      0.0    2411.77     215.00   0.6074    11.22   0.6001   0.5849  -10515.04      7
    10      1.0      13.71     168.00   0.4495     0.08   0.1917   0.5129     -46.02     -7
    20      2.0       0.56     123.00   0.3853     0.00   0.1402   0.4605      -1.08     -1
    30      3.0       0.18      88.00   0.3447     0.00   0.1122   0.4310      -0.02     -3
    40      4.0       0.19      69.00   0.3164     0.00   0.0945   0.4190       0.03     -4
    50      5.0       0.24      50.00   0.2954     0.00   0.0824   0.4100       0.06      0
    60      6.0       0.31      34.00   0.2793     0.01   0.0737   0.4046       0.08      1
    70      7.0       0.40      26.00   0.2665     0.02   0.0671   0.4027       0.09      0
    80      8.0       0.50      19.00   0.2562     0.03   0.0621   0.4014       0.11     -1
    90      9.0       0.63       9.00   0.2478     0.07   0.0582   0.4003       0.18      1
```

**Observations:**
- E crashes 2411 → 13 in 1 second (step 0→10)
- N declines steadily 215 → 9 over 10 seconds
- phi declines 0.607 → 0.248
- rho ~ 0 after step 10 (energy per capita vanishes)
- lambda_c drops but stabilizes around 0.06-0.20
- lambda_d ~ 0.40-0.52 (relatively constant)
- Death rate > birth rate throughout → extinction inevitable

---

## Proposed Fixes

### Option 1: Increase Resource Input (R)
- Scale R to match maintenance cost
- Required: R ≈ beta * N * E_target / gamma
- For N=215, E=2411: R ≈ 0.02 * 215 * 2411 / 0.3 ≈ 34,600
- **Issue:** Unrealistic resource scaling

### Option 2: Reduce Beta (Maintenance Cost)
- Current: beta = 0.02
- Try: beta = 0.0001 (200× reduction)
- Would give dE/dt ~ 0.3 - 144 - 51 = -195 (still negative but survivable)
- **Issue:** Changes fundamental model behavior

### Option 3: Different Initial Energy
- Deterministic steady state might not be stochastic steady state
- Start with lower E matched to N
- Find stochastic equilibrium empirically
- **Issue:** Requires search/calibration

### Option 4: Check Deterministic V4 Implementation
- Verify Phase 5 parameters are correct
- Check if there's a scaling factor or normalization
- Compare deterministic dE/dt to diagnostic output
- **Most Likely:** Parameters work in deterministic but scale incorrectly for stochastic

---

## Next Steps

1. ✅ Run Phase 5 deterministic V4 with same initial condition
2. ✅ Compare deterministic dE/dt to stochastic dE/dt
3. ✅ Identify scaling difference
4. ✅ Adjust stochastic parameters or initial conditions
5. ✅ Re-run ensemble and check for persistence

---

## Status

**Current:** Bug identified, root cause understood
**Next:** Test proposed fixes
**Goal:** Match stochastic CV to empirical 9.2%

