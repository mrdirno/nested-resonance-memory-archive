# PAPER 7 PHASE 3: BIFURCATION ANALYSIS PLANNING

**Date:** 2025-10-27 (Cycle 376)
**Status:** Planning phase
**Prerequisites:** Phase 1 complete ✅, Phase 2 implementation complete ✅
**Estimated Duration:** 1-2 weeks
**Target:** Map parameter space, identify bifurcations, validate against Paper 5A empirical data

---

## OBJECTIVES

### Primary Goals
1. **Parameter Space Mapping:** Systematically vary NRM parameters to map stable/unstable regions
2. **Bifurcation Detection:** Identify critical parameter values where qualitative behavior changes
3. **Regime Boundaries:** Validate theoretical bifurcations against empirical regime transitions (Paper 2)
4. **Predictive Framework:** Use bifurcation diagram to predict system behavior for new parameter sets

### Specific Questions
1. At what parameter values does steady-state population transition from sustained → collapse?
2. Do bifurcations correspond to empirical regime boundaries (Paper 2: 0.5%, 2.5% frequency)?
3. Can we predict bistability regions before running experiments?
4. What parameters most strongly influence stability?

---

## BACKGROUND

### Bifurcation Theory Primer

**Bifurcation:** Qualitative change in system dynamics as parameter varies
- **Saddle-node bifurcation:** Creation/annihilation of equilibria
- **Hopf bifurcation:** Transition from stable fixed point to limit cycle (oscillations)
- **Transcritical bifurcation:** Exchange of stability between two equilibria
- **Pitchfork bifurcation:** Symmetric equilibria splitting

**Bifurcation Diagram:** Plot of equilibria (or attractors) vs parameter
- X-axis: Bifurcation parameter (e.g., frequency, energy threshold)
- Y-axis: Equilibrium values (e.g., steady-state population N*)
- Solid lines: Stable equilibria
- Dashed lines: Unstable equilibria
- Bifurcation points: Where stability changes

### Relevant to NRM

From Paper 2 empirical findings:
- **Sustained regime:** f > 2.5% → N* ≈ 0.95 (stable)
- **Bistability regime:** 0.5% < f < 2.5% → N* depends on initial conditions
- **Collapse regime:** f < 0.5% → N* ≈ 0.07 (unstable, decaying)

**Hypothesis:** These transitions correspond to bifurcations in the NRM ODE system:
- **Bifurcation 1 (f ≈ 0.5%):** Saddle-node or transcritical (collapse → bistability)
- **Bifurcation 2 (f ≈ 2.5%):** Transcritical or pitchfork (bistability → sustained)

---

## METHODS

### 1. Continuation Methods

**Approach:** Follow equilibrium branches as parameter varies

**Algorithm (Pseudo-continuation):**
```python
def trace_equilibrium_branch(ode_system, param_name, param_range, N_initial):
    """
    Trace equilibrium branch using pseudo-arclength continuation.

    Args:
        ode_system: NRM ODE system (Phase 1 V2 constrained)
        param_name: Parameter to vary (e.g., 'omega' for frequency)
        param_range: Array of parameter values
        N_initial: Initial guess for equilibrium population

    Returns:
        equilibria: List of (param_value, N_equilibrium, stability)
    """
    equilibria = []
    N_guess = N_initial

    for param_value in param_range:
        # Update parameter
        ode_system.params[param_name] = param_value

        # Find equilibrium near N_guess
        def equilibrium_condition(state):
            # dN/dt = 0 at equilibrium
            dstate_dt = ode_system.ode_system_constrained(state, t=0, R_func=lambda t: 1.0)
            return dstate_dt[1]  # dN/dt component

        # Solve for equilibrium
        result = scipy.optimize.root(equilibrium_condition, x0=[...])

        if result.success:
            N_eq = result.x[1]  # Extract population component

            # Determine stability via eigenvalues
            stability = check_stability(ode_system, result.x)

            equilibria.append((param_value, N_eq, stability))
            N_guess = N_eq  # Use as next initial guess
        else:
            # Equilibrium disappeared (possible bifurcation)
            equilibria.append((param_value, None, None))

    return equilibria
```

**Tools:**
- `scipy.optimize.root`: Find equilibrium (dN/dt = 0)
- `scipy.linalg.eig`: Compute Jacobian eigenvalues for stability
- `matplotlib`: Plot bifurcation diagram

**Alternative (if manual fails):**
- `PyDSTool`: Professional continuation software (Python)
- `AUTO-07p`: Industry-standard bifurcation software (Fortran, Python interface)
- `MATCONT`: MATLAB continuation toolbox

### 2. Stability Analysis

**Jacobian Matrix:**
At equilibrium state x*, compute:
```
J = ∂f/∂x |_{x=x*}
```

For NRM system (4D: E, N, φ, θ):
```
J = [∂(dE/dt)/∂E   ∂(dE/dt)/∂N   ∂(dE/dt)/∂φ   ∂(dE/dt)/∂θ  ]
    [∂(dN/dt)/∂E   ∂(dN/dt)/∂N   ∂(dN/dt)/∂φ   ∂(dN/dt)/∂θ  ]
    [∂(dφ/dt)/∂E   ∂(dφ/dt)/∂N   ∂(dφ/dt)/∂φ   ∂(dφ/dt)/∂θ  ]
    [∂(dθ/dt)/∂E   ∂(dθ/dt)/∂N   ∂(dθ/dt)/∂φ   ∂(dθ/dt)/∂θ  ]
```

**Stability Criterion:**
- **Stable:** All eigenvalues have negative real parts (Re(λ) < 0)
- **Unstable:** At least one eigenvalue has positive real part (Re(λ) > 0)
- **Marginally stable:** Eigenvalues on imaginary axis (Re(λ) = 0)

**Implementation:**
```python
def check_stability(ode_system, equilibrium_state):
    """
    Determine stability of equilibrium via Jacobian eigenvalues.

    Args:
        ode_system: NRM ODE system
        equilibrium_state: [E*, N*, φ*, θ*]

    Returns:
        'stable', 'unstable', or 'marginal'
    """
    # Compute Jacobian numerically
    epsilon = 1e-6
    J = np.zeros((4, 4))

    for i in range(4):
        state_plus = equilibrium_state.copy()
        state_minus = equilibrium_state.copy()
        state_plus[i] += epsilon
        state_minus[i] -= epsilon

        f_plus = ode_system.ode_system_constrained(state_plus, t=0, R_func=lambda t: 1.0)
        f_minus = ode_system.ode_system_constrained(state_minus, t=0, R_func=lambda t: 1.0)

        J[:, i] = (f_plus - f_minus) / (2 * epsilon)

    # Eigenvalue analysis
    eigenvalues = np.linalg.eigvals(J)
    max_real_part = np.max(np.real(eigenvalues))

    if max_real_part < -1e-6:
        return 'stable'
    elif max_real_part > 1e-6:
        return 'unstable'
    else:
        return 'marginal'  # Bifurcation point
```

### 3. Parameter Sweeps

**Primary Parameters to Vary:**
1. **ω (omega):** External frequency (links to Paper 2 frequency parameter)
2. **K (carrying capacity):** Energy limit per agent
3. **λ₀ (lambda_0):** Base composition rate
4. **μ₀ (mu_0):** Base decomposition rate
5. **α (alpha):** Reality coupling strength

**Secondary Parameters (if time permits):**
6. r (recharge rate)
7. β (beta): Maintenance cost
8. γ (gamma): Composition cost
9. σ (sigma): Crowding sensitivity
10. κ (kappa): Resonance decay

**Sweep Strategy:**
- **Coarse sweep:** 20-50 values per parameter (initial mapping)
- **Fine sweep:** 100-500 values near suspected bifurcations (refinement)
- **2D sweep:** Vary two parameters simultaneously (e.g., ω vs K)

### 4. Bifurcation Detection

**Automated Detection:**
```python
def detect_bifurcations(equilibria):
    """
    Identify bifurcation points from equilibrium trace.

    Args:
        equilibria: List of (param, N_eq, stability)

    Returns:
        bifurcation_points: List of (param, bifurcation_type)
    """
    bifurcations = []

    for i in range(1, len(equilibria)):
        prev_param, prev_N, prev_stab = equilibria[i-1]
        curr_param, curr_N, curr_stab = equilibria[i]

        # Stability change → bifurcation
        if prev_stab != curr_stab:
            bifurcations.append((curr_param, 'stability_change'))

        # Equilibrium disappears → saddle-node
        if prev_N is not None and curr_N is None:
            bifurcations.append((prev_param, 'saddle_node'))

        # Equilibrium appears → saddle-node
        if prev_N is None and curr_N is not None:
            bifurcations.append((curr_param, 'saddle_node'))

        # Large jump in N → transcritical or pitchfork
        if prev_N is not None and curr_N is not None:
            if abs(curr_N - prev_N) > 0.5:  # Threshold
                bifurcations.append((curr_param, 'large_jump'))

    return bifurcations
```

---

## VALIDATION AGAINST EMPIRICAL DATA

### Paper 2 Empirical Regime Boundaries

From C171 + C175 + C177 data:
- **Collapse → Bistability:** f ≈ 0.5% (150 cycles period)
- **Bistability → Sustained:** f ≈ 2.5% (30 cycles period)

**Validation Test:**
1. Run bifurcation analysis varying ω (external frequency)
2. Map ω values to experiment frequency: f = ω / (2π) or similar
3. Compare predicted bifurcation points to empirical boundaries
4. **Success criterion:** Bifurcations within ±0.25% of empirical boundaries

### Paper 5A Parameter Sensitivity

Once Paper 5A executes (parameter sensitivity experiments):
- Compare empirical robustness to theoretical stability margins
- Validate that parameters with wide stability regions show low sensitivity
- Parameters near bifurcations should show high sensitivity

---

## DELIVERABLES

### Code Artifacts
1. `paper7_phase3_bifurcation_analysis.py`: Main analysis script
   - Continuation algorithm
   - Stability analysis
   - Bifurcation detection
   - 2D parameter sweeps

2. `paper7_phase3_jacobian_tools.py`: Stability utilities
   - Numerical Jacobian computation
   - Eigenvalue analysis
   - Stability classification

3. `paper7_phase3_visualization.py`: Plotting tools
   - 1D bifurcation diagrams
   - 2D stability maps
   - 3D parameter surfaces

### Figures (Publication Quality, 300 DPI)
1. **Figure 1:** 1D bifurcation diagram (N* vs ω)
   - Stable/unstable branches
   - Bifurcation points annotated
   - Empirical regime boundaries overlaid

2. **Figure 2:** 2D stability map (ω vs K)
   - Heatmap of stability (stable=blue, unstable=red)
   - Bifurcation curves marked
   - Paper 2 parameter values indicated

3. **Figure 3:** Eigenvalue trajectories
   - Real parts of λ vs parameter
   - Crossing of Re(λ) = 0 indicates bifurcation

4. **Figure 4:** Comparison to empirical data
   - Predicted vs observed regime boundaries
   - Error bars on empirical estimates

### Documentation
1. **PAPER7_PHASE3_BIFURCATION_RESULTS.md**: Analysis report
   - Bifurcation points identified
   - Stability regions mapped
   - Validation against empirical data
   - Interpretation of findings

2. **PAPER7_MANUSCRIPT_DRAFT.md updates**:
   - Integrate Phase 3 results into Results section
   - Add bifurcation figures
   - Update Discussion with stability implications

---

## EXPECTED OUTCOMES

### Scientific Findings
1. **Bifurcation Identification:** 2-3 critical bifurcations in ω parameter
2. **Regime Mapping:** Stability boundaries align with empirical regimes (Paper 2)
3. **Predictive Power:** Bifurcation diagram predicts new parameter behaviors
4. **Sensitivity Ranking:** Identify which parameters most affect stability

### Theoretical Insights
1. **Mechanism:** What drives regime transitions? (Energy? Resonance? Phase coupling?)
2. **Control:** Which parameters can be tuned to stay in sustained regime?
3. **Robustness:** How wide are stability margins? (Links to Paper 5A)
4. **Emergence:** Are regime transitions emergent or reducible to bifurcations?

### Publication Value
- **Novel contribution:** First bifurcation analysis of NRM dynamics
- **Validation:** Theoretical predictions match empirical observations
- **Practical utility:** Bifurcation diagram enables parameter design
- **Generalization:** Methodology applies to other emergent systems

---

## TIMELINE

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | Implement continuation + stability analysis | Code complete, tested |
| 1 | Run 1D bifurcation analysis (ω parameter) | Figure 1, initial results |
| 1 | Validate against Paper 2 empirical boundaries | Comparison analysis |
| 2 | Run 2D bifurcation analysis (ω vs K) | Figure 2, stability map |
| 2 | Additional parameter sweeps (λ₀, μ₀, α) | Extended analysis |
| 2 | Write results document + integrate into manuscript | Phase 3 complete |

**Total:** 1-2 weeks (10-15 hours coding + analysis)

---

## DEPENDENCIES

**Prerequisites:**
- ✅ Phase 1 V2 constrained model (complete, Cycle 371)
- ✅ Phase 2 SINDy implementation (complete, Cycle 373)
- ✅ Paper 2 empirical regime data (complete, C171 + C175 + C177)

**External Tools (optional):**
- `pysindy`: Already planned for Phase 2 (can skip if manual works)
- `PyDSTool`: Professional continuation (if manual fails)
- `AUTO-07p`: Industry standard (if PyDSTool insufficient)

**Data Dependencies:**
- Paper 5A results (for validation, not blocking)
- Can proceed without Paper 5A, validate retroactively

---

## RISKS & MITIGATION

### Risk 1: Numerical Instability
**Issue:** Jacobian computation may be unstable near bifurcations
**Mitigation:** Use adaptive step sizes, reduce epsilon, switch to symbolic differentiation

### Risk 2: High-Dimensional Complexity
**Issue:** 4D system has complex bifurcation structure
**Mitigation:** Focus on 1-2 primary parameters, use projection methods

### Risk 3: No Clear Bifurcations
**Issue:** System may have gradual transitions, not sharp bifurcations
**Mitigation:** Document gradual transitions, compare to empirical smoothness

### Risk 4: Tool Learning Curve
**Issue:** PyDSTool/AUTO-07p may require significant learning
**Mitigation:** Start with manual scipy methods, only use tools if necessary

---

## SUCCESS CRITERIA

Phase 3 is successful when:
1. ✅ Bifurcation diagram generated for at least 1 parameter (ω)
2. ✅ Stability analysis identifies stable/unstable regions
3. ✅ Predicted bifurcations align with empirical regimes (±0.5% error acceptable)
4. ✅ Figures publication-ready (300 DPI, clear labels)
5. ✅ Results integrated into Paper 7 manuscript
6. ✅ Code documented and committed to repository

---

## NEXT STEPS (AFTER PHASE 3)

**Phase 4:** Stochastic Analysis (1-2 weeks)
- Characterize R(t) noise properties
- Predict variance from stochastic forcing
- Compare to empirical variance (Paper 5B data)

**Phase 5:** Symbolic Regression Testing (Phase 2 execution)
- Run Phase 2 SINDy script (requires pysindy installation)
- Validate discovered equations
- Integrate into manuscript

**Phase 6:** Manuscript Finalization (1-2 weeks)
- Polish all sections
- Generate all figures
- Format for Physical Review E / Chaos
- Submit

---

## REFERENCES

**Bifurcation Theory:**
- Strogatz, S. H. (2015). *Nonlinear Dynamics and Chaos*. Westview Press.
- Kuznetsov, Y. A. (2004). *Elements of Applied Bifurcation Theory*. Springer.

**Continuation Methods:**
- Doedel, E. J. (2007). "AUTO-07p: Continuation and bifurcation software." *http://www.dam.brown.edu/people/sandsted/auto/auto.html*
- Clewley, R. (2012). "Hybrid models and biological model reduction with PyDSTool." *PLoS Computational Biology*, 8(8).

**NRM Background:**
- Paper 2: "From Bistability to Collapse" (empirical regime boundaries)
- Paper 7 Phase 1: V2 constrained model (ODE system)
- Paper 7 Theoretical Scaffold: Governing equations

---

**Document Version:** 1.0
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Date:** 2025-10-27 (Cycle 376)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

**Quote:** *"Bifurcations are not failures of stability - they are discoveries of possibility."*
