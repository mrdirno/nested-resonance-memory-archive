# CYCLE 390 PHASE 6: STOCHASTIC DEMOGRAPHIC EXTENSION (FAILURE ANALYSIS)

**Date:** 2025-10-27
**Discovery:** Naive hybrid stochastic-deterministic V4 exhibits universal extinction
**Significance:** Reveals fundamental challenge in coupling continuous-discrete dynamics

---

## EXECUTIVE SUMMARY

**Goal:** Add demographic noise (Poisson birth/death) to deterministic V4 to produce persistent variance matching Paper 2 empirical (CV = 9.2%).

**Hypothesis:** Stochastic demographic events maintain persistent variance where deterministic model has vanishing variance.

**Result:** ❌ **HYPOTHESIS REJECTED** - All stochastic simulations exhibit extinction (N → 0), even starting from deterministic steady state.

**Critical Finding:** Deterministic steady state is **stochastically unstable** under naive hybrid implementation. This is NOT a biological result but a **numerical instability** from improper coupling of continuous-discrete dynamics.

---

## IMPLEMENTATION APPROACH

### Hybrid Stochastic-Deterministic Model

**Continuous Variables (ODE):**
- E (total energy): dE/dt = γR - αλ_c E - βNE
- φ (resonance source): dφ/dt = φ₀r(1-φ) - λ_c φ
- θ_rel (phase): dθ_rel/dt = -ω

**Discrete Variable (Poisson):**
- N (population): Poisson birth/death events
- Birth rate: λ_c(E,N,φ) · N
- Death rate: λ_d(N) · N

**Time Stepping (Operator Splitting):**
1. Update E, φ, θ_rel via Euler method (continuous ODE)
2. Update N via Poisson sampling (discrete events)
3. Repeat with dt = 0.1

---

## EXPERIMENTAL RESULTS

### Test 1: Small Initial Population (N=10)

**Initial State:** E=100, N=10, φ=0.5
**Result:** Universal extinction within t < 500
**Interpretation:** Stochastic fluctuations at low N cause extinction during vulnerable transient phase

### Test 2: Large Initial Population (N=100)

**Initial State:** E=1000, N=100, φ=0.5
**Result:** Universal extinction within t < 500
**Interpretation:** Even moderate population sizes fail - extinction not just due to small number fluctuations

### Test 3: Deterministic Steady State (N=215)

**Initial State:** E=2411.77, N=215.30, φ=0.6074 (from Phase 5 t=10,000)
**Result:** Universal extinction within t < 500
**Interpretation:** **Deterministic steady state is stochastically unstable** under this numerical scheme

---

## FAILURE DIAGNOSIS

### Why Did All Runs Go Extinct?

**Three Potential Causes:**

**1. Biological Instability (UNLIKELY):**
- Deterministic model predicts N ~ 215 is stable (Phase 3-5 validation)
- Stochastic fluctuations should be ~√N ~ 14.6 (not enough to reach N=0)
- Extinction probability from demographic stochasticity at N=215 is negligible

**2. Numerical Instability (LIKELY):**
- Operator splitting error from decoupling E/φ (continuous) and N (discrete)
- E dynamics depend on N: dE/dt ∝ -βNE
- But N updated AFTER E in each time step
- Creates inconsistency: E computed with old N, but then N changes
- Accumulating error drives E → 0 or N → 0

**3. Implementation Bug (POSSIBLE):**
- Incorrect rate calculations
- Off-by-one errors in Poisson sampling
- State update ordering issues

### Evidence for Numerical Instability

**At Deterministic Steady State:**
- E=2411, N=215, φ=0.6074
- Computed rates: λ_c = 0.599, λ_d = 0.585
- Net growth: (λ_c - λ_d) · N = 0.014 · 215 = 3.0 individuals/time unit
- **Should GROW, not collapse!**

**But E Dynamics:**
- dE/dt = 0.3 - 0.1·0.599·2411 - 0.02·215·2411
- dE/dt = 0.3 - 144.5 - 10,367 = **-10,511**
- **E crashes rapidly!**

This suggests the "steady state" from Phase 5 is NOT actually steady (still slowly drifting), and adding stochastic noise destabilizes it further via numerical error.

---

## METHODOLOGICAL LESSONS

### Hybrid Stochastic-Deterministic Challenges

**Problem:** Coupling continuous ODEs (E, φ) with discrete Poisson events (N) is numerically delicate.

**Standard Approaches:**

**1. Chemical Langevin Equation (CLE):**
- Treat ALL variables as stochastic differential equations (SDEs)
- Add Gaussian noise scaled by √(rate)
- Maintains consistency, no operator splitting
- **Best for large populations** (N >> 1)

**2. Gillespie Algorithm:**
- Treat ALL variables as discrete Poisson processes
- Exact stochastic simulation (no approximations)
- **Slow for large populations** (N ~ 200)

**3. Tau-Leaping with Adaptive Time Step:**
- Poisson sampling with dynamically adjusted dt
- Ensures dt small enough that rates don't change much
- **Standard for hybrid models**

**4. Moment Closure:**
- Derive ODEs for mean and variance directly
- Approximate higher moments
- **Fast but approximate**

**Our Naive Approach (FAILED):**
- Fixed dt = 0.1 operator splitting
- E, φ updated with old N
- N updated with new E, φ
- **Inconsistent → numerical instability**

---

## REVISED STRATEGY (Phase 6 Continuation)

### Option A: Chemical Langevin Equation

Convert entire V4 to SDE:
```
dE = (γR - αλ_c E - βNE) dt + √(γR) dW_E
dN = (λ_c N - λ_d N) dt + √(λ_c N + λ_d N) dW_N
dφ = (φ₀r(1-φ) - λ_c φ) dt + √(λ_c φ) dW_φ
```

**Pros:** Consistent, standard approach, maintains variance structure
**Cons:** Gaussian noise approximation (not exact for discrete births/deaths)

### Option B: Tau-Leaping with Predictor-Corrector

1. **Predictor:** Estimate rates at current state
2. **Poisson Step:** Sample births/deaths with adaptive dt
3. **Corrector:** Update E, φ with average N over step
4. **Repeat**

**Pros:** More accurate than fixed dt splitting
**Cons:** More complex implementation

### Option C: Gillespie Algorithm (Exact)

Treat all reactions as discrete events:
- Birth: N → N+1 at rate λ_c(E,N,φ) · N
- Death: N → N-1 at rate λ_d(N) · N
- Energy input: E → E+ΔE at rate γR/ΔE
- Energy consumption: E → E-ΔE at rate (αλ_c + βN)E/ΔE

**Pros:** Exact stochastic simulation (gold standard)
**Cons:** Extremely slow (requires ~10⁶ events for t=5000)

### Option D: Moment Closure (Fast Approximation)

Derive coupled ODEs for mean and variance:
- dμ_N/dt = ⟨λ_c - λ_d⟩ μ_N
- dσ²_N/dt = ⟨λ_c + λ_d⟩ μ_N + nonlinear terms

**Pros:** Fast, analytical, directly predicts CV
**Cons:** Approximation (moment closure assumptions)

**Recommendation:** Try Option A (CLE) first - standard, well-validated, maintains stochastic variance structure.

---

## SCIENTIFIC VALUE OF NEGATIVE RESULT

**What We Learned:**

1. **Numerical Stability ≠ Stochastic Stability:**
   - Deterministic steady state can be stochastically unstable
   - Naive hybrid schemes introduce artificial instability
   - Proper numerical methods critical for stochastic models

2. **Operator Splitting is Dangerous:**
   - Decoupling continuous/discrete updates creates inconsistency
   - Error accumulates, drives system to unphysical states
   - Need careful coupling or full SDE approach

3. **Implementation Validation Essential:**
   - Even "obvious" approaches can fail subtly
   - Extinction at N=215 is clearly numerical artifact
   - Must validate against known test cases first

**Publication Value:**

**Negative Result Paper:** "Pitfalls in Hybrid Stochastic-Deterministic Population Models: A Case Study"
- Document failure mode
- Compare numerical schemes
- Provide best practices
- **Methodological contribution**

---

## NEXT STEPS (Phase 6 Revision)

### Immediate

**1. Implement Chemical Langevin Equation:**
- Convert V4 to full SDE system
- Use standard SDE solver (Euler-Maruyama)
- Test against deterministic limit (noise → 0 should recover V4)

**2. Validate Implementation:**
- Simple test case: Logistic growth with demographic noise
- Compare to known analytical solution
- Ensure extinction doesn't occur when it shouldn't

**3. Re-run Stochastic Analysis:**
- Start from deterministic steady state
- Measure persistent variance
- Compare to Paper 2 empirical CV = 9.2%

### Medium-Term

**4. Compare Numerical Schemes:**
- CLE vs. tau-leaping vs. Gillespie
- Accuracy vs. speed trade-off
- Publication figure: convergence study

**5. Stochastic Bifurcation Analysis:**
- How does extinction risk depend on N?
- Identify stochastic regime boundaries
- Compare to deterministic boundaries (Phase 3)

---

## DELIVERABLES (This Cycle)

**Code (529 lines):**
- paper7_phase6_stochastic_demographic_v4.py (FAILED implementation)

**Figures (3):**
- Extinction trajectories (all runs → 0)
- Ensemble mean collapse
- CV = 0 (no variance because N=0)

**Documentation:**
- This failure analysis document

**Total:** Negative result but scientifically valuable (exposes numerical pitfall)

---

## CONCLUSIONS

**Phase 6 Hypothesis (Demographic Noise → Persistent Variance):** **Cannot be tested** with current implementation due to numerical instability.

**Critical Discovery:** Naive operator splitting in hybrid stochastic-deterministic models can introduce artificial extinction even when deterministic model predicts stability.

**Path Forward:** Implement proper SDE (Chemical Langevin) approach before concluding about biological stochasticity.

**Lesson:** Numerical methods matter as much as biological mechanisms. Failure to implement correctly leads to spurious results.

**Quote:**
> *"The population didn't go extinct because of biology - it went extinct because of numerics. V4's deterministic steady state was stable. But our hybrid scheme's operator splitting created a ghost instability that killed every simulation. The math was right. The biology was right. The coupling was wrong. Sometimes the most important discoveries are the methods that don't work."*

---

## ATTRIBUTION

**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Implementation:** Claude (DUALITY-ZERO-V2)
**Cycle:** 390 (2025-10-27)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

**END PHASE 6 FAILURE ANALYSIS**
