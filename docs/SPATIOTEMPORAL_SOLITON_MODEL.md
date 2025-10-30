# Spatiotemporal Soliton Model: Mathematical Formalism for NRM

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Project:** Nested Resonance Memory (NRM)
**Date:** 2025-10-30
**Status:** Mathematical formalization in progress
**Purpose:** Replace metaphorical "song/narrative" language with rigorous wave physics

---

## Abstract

This document provides mathematical formalism for the Nested Resonance Memory (NRM) framework, reframing emergent complexity as **spatiotemporal soliton dynamics** in anisotropic propagation media. We define:

1. **Wave propagation in anisotropic media** (tensor dispersion)
2. **Soliton solutions** (persistent coherent structures)
3. **Stability criteria** (what makes patterns persist vs dissipate)
4. **Connection to NRM implementation** (TranscendentalBridge, FractalAgent)
5. **Testable predictions** (falsifiable hypotheses)

**Core Thesis:** Biological complexity arises from simple wave pulses evolving into spatiotemporal solitons through anisotropic morphogenetic fields, not from execution of complex programs.

---

## 1. Mathematical Framework

### 1.1 Wave Equation in Anisotropic Medium

The scalar field φ(r,t) representing agent density, bioelectric potential, or cultural meme propagates according to:

```
∂²φ/∂t² = ∇·(A(r)·∇φ) - γ ∂φ/∂t + f(φ) + η(r,t)
```

**Components:**

- **φ(r,t)**: Scalar field (can be generalized to vector/tensor)
- **A(r)**: Anisotropy tensor (3×3 symmetric positive-definite matrix)
  - Encodes directional propagation speeds
  - Spatially varying (different at different positions)
  - Eigen-decomposition: A = Q Λ Q^T where Λ = diag(λ_x, λ_y, λ_z)
- **γ**: Damping coefficient (dissipation, friction)
- **f(φ)**: Nonlinear self-interaction (e.g., cubic: f(φ) = α φ (1 - φ²))
- **η(r,t)**: Stochastic forcing (thermal noise, reality metrics fluctuations)

**Physical Interpretation:**

- ∇·(A·∇φ): Anisotropic diffusion/propagation
- γ ∂φ/∂t: Energy dissipation to environment
- f(φ): Self-reinforcement (soliton formation mechanism)
- η: Environmental perturbations

### 1.2 Dispersion Relation

For plane wave solutions φ ~ exp(i(k·r - ωt)), the dispersion relation is:

```
ω²(k) = k^T · A · k - iγω
```

**Isotropic case (A = c² I):**
```
ω(k) = c|k|  (spherical iso-frequency surfaces)
```

**Anisotropic case (A = diag(c_x², c_y², c_z²)):**
```
ω²(k) = c_x² k_x² + c_y² k_y² + c_z² k_z²  (ellipsoidal iso-frequency surfaces)
```

**Implication:** Different frequencies propagate at different speeds along different directions. This creates **directional beats** and **interference anisotropy**.

### 1.3 Soliton Solutions

A **spatiotemporal soliton** is a localized wave packet that maintains its shape during propagation:

```
φ(r,t) = Φ(r - vt) · exp(iθ(r,t))
```

Where:
- **Φ(ξ)**: Envelope function (spatial profile)
- **ξ = r - vt**: Co-moving coordinate
- **v**: Propagation velocity (determined by A)
- **θ(r,t)**: Phase (can be constant or slowly varying)

**Substituting into wave equation:**

```
(v² - A) ∇²Φ + γv ∂Φ/∂ξ = f(Φ)
```

**Soliton existence condition:**

A soliton exists when nonlinearity **f(Φ)** can balance anisotropic dispersion **(v² - A)∇²Φ** and dissipation **γv ∂Φ/∂ξ**.

**Standard soliton families:**

1. **Korteweg-de Vries (KdV):** Φ(ξ) = A sech²(√A ξ)
2. **Sine-Gordon:** Φ(ξ) = 4 arctan(exp(ξ))
3. **Nonlinear Schrödinger (NLS):** Φ(ξ) = A sech(Aξ) exp(iωt)

### 1.4 Stability Criteria

A soliton is **stable** if small perturbations δφ decay exponentially:

```
φ(r,t) = Φ(r - vt) + δφ(r,t)
δφ(t) ~ exp(-λt)  where λ > 0
```

**Linear stability analysis:**

Linearize wave equation around soliton solution:

```
∂²δφ/∂t² = L[δφ]
```

Where **L** is the linearized operator:

```
L = ∇·(A·∇) - γ ∂/∂t + f'(Φ)
```

Soliton is stable if **all eigenvalues of L have negative real parts**.

**Energy functional approach:**

Define total energy:

```
E[φ] = ∫ [1/2 (∂φ/∂t)² + 1/2 ∇φ^T · A · ∇φ - F(φ)] dr
```

Where F(φ) = ∫ f(φ) dφ (potential energy).

Soliton is stable if it's a **local minimum of E** (second variation positive definite):

```
δ²E/δφ² > 0  ⟹  stable soliton
δ²E/δφ² < 0  ⟹  unstable (dissipates)
```

---

## 2. Connection to NRM Implementation

### 2.1 Current NRM Architecture

**NRM modules relevant to soliton model:**

| Module | Role in Soliton Model | Current Implementation |
|--------|----------------------|------------------------|
| `bridge/transcendental_bridge.py` | Generates anisotropy tensor A(r,t) via π, e, φ oscillations | ✅ Implemented |
| `fractal/fractal_agent.py` | Represents localized excitations (wave packets) | ✅ Implemented |
| `fractal/fractal_swarm.py` | Composition-decomposition = soliton formation/decay | ✅ Implemented |
| `memory/pattern_memory.py` | Stores stable soliton topologies | ✅ Implemented |
| `reality/system_monitor.py` | Provides noise η(r,t) from real system metrics | ✅ Implemented |

**What's missing:**
- Explicit wave equation solver
- Anisotropy tensor field A(r)
- Dispersion relation computation
- Stability analysis tools

### 2.2 Mapping NRM Concepts to Soliton Physics

**Conceptual Translation:**

| NRM Concept | Soliton Physics | Mathematical Object |
|-------------|----------------|---------------------|
| Agent | Localized wave packet | Φ(r - vt) |
| Composition | Constructive interference → Soliton formation | ∫ Φ₁ Φ₂ dr > 0 |
| Decomposition | Destructive interference → Wave dissipation | ∫ Φ₁ Φ₂ dr < 0 |
| Resonance | Phase-locked oscillations | ω₁ = n·ω₂ |
| Memory | Retained soliton topology | E[Φ] at local minimum |
| Reality grounding | Noise forcing η(r,t) from psutil | Stochastic term |
| Transcendental substrate | Anisotropy tensor A structured by π, e, φ | A(r) = A(π, e, φ) |

**Energy management:**

Current NRM energy = ∫ |∇Φ|² dr (roughly)

Should be refined to proper wave energy:

```python
def soliton_energy(phi, phi_dot, A):
    """
    E = ∫ [1/2 φ_t² + 1/2 ∇φ^T · A · ∇φ - F(φ)] dr
    """
    kinetic = 0.5 * np.sum(phi_dot**2)

    grad_phi = np.gradient(phi)
    potential = 0.5 * np.einsum('i,ij,j', grad_phi, A, grad_phi)

    # Nonlinear potential F(φ) = -α/2 φ² + β/4 φ⁴
    nonlinear = -0.5 * alpha * np.sum(phi**2) + 0.25 * beta * np.sum(phi**4)

    return kinetic + potential + nonlinear
```

### 2.3 TranscendentalBridge as Anisotropy Generator

**Current TranscendentalBridge** generates oscillations at π, e, φ frequencies:

```python
class TranscendentalBridge:
    def generate_oscillation(self, frequency, duration):
        # Returns phase-space trajectory
        pass
```

**Proposed extension: Anisotropy Tensor Field**

```python
class TranscendentalBridge:
    def generate_anisotropy_tensor(self, position, time):
        """
        Generate spatially-varying anisotropy tensor A(r,t).

        Uses π, e, φ oscillators to create directional propagation speeds.

        Args:
            position: (x, y, z) spatial coordinates
            time: Current time

        Returns:
            A: 3×3 symmetric positive-definite tensor
        """
        # Oscillate tensor elements using transcendental frequencies
        theta_pi = np.pi * time + np.pi * position[0]
        theta_e = np.e * time + np.e * position[1]
        theta_phi = (1 + np.sqrt(5))/2 * time + (1 + np.sqrt(5))/2 * position[2]

        # Construct anisotropy tensor (ensure positive-definite)
        a_x = 1.0 + 0.3 * np.cos(theta_pi)
        a_y = 1.0 + 0.3 * np.cos(theta_e)
        a_z = 1.0 + 0.3 * np.cos(theta_phi)

        A = np.diag([a_x**2, a_y**2, a_z**2])

        return A
```

**Why this matters:**

- Spatially-varying A(r) → Different propagation speeds at different locations
- Temporally-varying A(t) → Resonance windows open/close
- Transcendental frequencies → Computationally irreducible, prevents cycles

### 2.4 FractalAgent as Wave Packet

**Current FractalAgent** has:
- Position
- Phase state (via TranscendentalBridge)
- Energy

**Soliton interpretation:**

An agent is a **localized wave packet** Φ(r):

```python
class FractalAgent:
    def __init__(self, agent_id, bridge, initial_reality):
        self.phase_state = bridge.reality_to_phase(initial_reality)
        self.energy = self.calculate_energy()  # Should be wave energy
        self.position = initial_reality['position']  # Center of wave packet
        self.velocity = np.array([0.0, 0.0, 0.0])  # Propagation velocity
        self.width = 1.0  # Spatial extent (σ in Gaussian)

    def wave_packet(self, r):
        """
        Gaussian wave packet centered at self.position.

        Φ(r) = A exp(-|r - r₀|²/(2σ²)) exp(ik·r)
        """
        delta_r = r - self.position
        envelope = np.exp(-np.sum(delta_r**2) / (2 * self.width**2))
        phase = np.exp(1j * np.dot(self.wave_vector, r))
        return self.amplitude * envelope * phase

    def propagate(self, dt, A):
        """
        Propagate wave packet through anisotropic medium.

        v = A · k / |k|  (group velocity)
        """
        # Compute group velocity from anisotropy tensor
        k = self.wave_vector
        self.velocity = np.dot(A, k) / np.linalg.norm(k)

        # Update position
        self.position += self.velocity * dt
```

### 2.5 Composition Engine as Interference Calculator

**Current CompositionEngine** detects clusters via resonance:

```python
class CompositionEngine:
    def detect_clusters(self, agents):
        # Check resonance between agents
        pass
```

**Soliton interpretation: Interference**

Two agents with wave packets Φ₁(r), Φ₂(r) interfere:

```python
def interference_strength(agent1, agent2, grid):
    """
    Compute ∫ Φ₁(r) Φ₂(r) dr

    > 0: Constructive interference (soliton formation)
    < 0: Destructive interference (dissipation)
    """
    phi1 = agent1.wave_packet(grid)
    phi2 = agent2.wave_packet(grid)

    overlap = np.sum(phi1 * phi2.conj()).real

    return overlap
```

**Soliton formation criterion:**

```python
def can_form_soliton(agent1, agent2, A):
    """
    Check if two agents can form stable soliton.

    Requires:
    1. Constructive interference (overlap > 0)
    2. Stable energy minimum (δ²E > 0)
    3. Compatible velocities (Δv < v_critical)
    """
    overlap = interference_strength(agent1, agent2, grid)

    if overlap <= 0:
        return False  # Destructive interference

    # Check if combined state is local energy minimum
    phi_combined = agent1.wave_packet(grid) + agent2.wave_packet(grid)
    energy = soliton_energy(phi_combined, A)

    # Stability: second variation of energy
    stability = check_energy_hessian(phi_combined, A)

    return (overlap > 0) and (stability > 0)
```

---

## 3. Testable Predictions

### 3.1 Prediction 1: Directional Propagation

**Hypothesis:** In anisotropic medium with A = diag(a_x, a_y, a_z), wave packets propagate fastest along the axis with largest eigenvalue.

**Test:**
1. Initialize agent at origin with isotropic initial state
2. Measure propagation distance after fixed time along each axis
3. Expect: d_x/d_y = √(a_x/a_y), d_x/d_z = √(a_x/a_z)

**Falsification:** If propagation is isotropic (d_x ≈ d_y ≈ d_z), anisotropy is not effective.

**Implementation:**
```python
def test_directional_propagation(A, duration=100):
    """
    Measure propagation speeds along x, y, z axes.
    """
    agent = FractalAgent(id="test", bridge=bridge, initial_reality=metrics)

    # Record initial position
    r0 = agent.position.copy()

    # Propagate for duration
    for t in range(duration):
        agent.propagate(dt=1.0, A=A)

    # Measure displacement
    displacement = agent.position - r0

    return {
        'dx': displacement[0],
        'dy': displacement[1],
        'dz': displacement[2],
        'v_x': displacement[0] / duration,
        'v_y': displacement[1] / duration,
        'v_z': displacement[2] / duration,
        'anisotropy_ratio_xy': displacement[0] / displacement[1],
        'expected_ratio_xy': np.sqrt(A[0,0] / A[1,1])
    }
```

### 3.2 Prediction 2: Resonant Frequency Selection

**Hypothesis:** Solitons form preferentially at frequencies ω = n·(π, e, φ) if substrate uses transcendental harmonics.

**Test:**
1. Initialize agents with various frequencies ω ∈ [0.1, 10.0]
2. Measure soliton lifetime τ(ω)
3. Expect: Peaks at ω = π, 2π, e, φ, etc.

**Falsification:** If τ(ω) is flat (no peaks), transcendental substrate is not selecting frequencies.

**Implementation:**
```python
def test_resonant_frequencies(frequencies):
    """
    Sweep frequency, measure soliton lifetime.
    """
    lifetimes = []

    for omega in frequencies:
        agent = FractalAgent(id=f"test_{omega}", ...)
        agent.set_frequency(omega)

        # Measure how long pattern persists
        tau = measure_coherence_time(agent, duration=1000)
        lifetimes.append(tau)

    # Check for peaks at transcendental multiples
    peaks = find_peaks(lifetimes)
    expected_peaks = [np.pi, 2*np.pi, np.e, (1+np.sqrt(5))/2]

    return {
        'frequencies': frequencies,
        'lifetimes': lifetimes,
        'peaks_detected': peaks,
        'peaks_expected': expected_peaks,
        'match': check_peak_alignment(peaks, expected_peaks, tolerance=0.1)
    }
```

### 3.3 Prediction 3: Ellipsoidal Cross-Sections

**Hypothesis:** Spatial cross-sections of stable solitons should be ellipsoids aligned with A eigenvectors.

**Test:**
1. Create soliton (stable agent cluster)
2. Measure spatial density profile at fixed time
3. Fit ellipsoid, extract axes lengths
4. Compare to A eigenvalues: a_x, a_y, a_z

**Falsification:** If cross-sections are spherical or have random orientations, anisotropy is not structuring solitons.

**Implementation:**
```python
def test_ellipsoidal_topology(soliton, A):
    """
    Fit ellipsoid to soliton spatial profile.
    """
    # Get density field
    density = compute_density_field(soliton.agents, grid)

    # Fit ellipsoid (find covariance matrix)
    positions = np.array([agent.position for agent in soliton.agents])
    covariance = np.cov(positions.T)

    # Extract axes (eigenvectors and eigenvalues)
    eigenvalues, eigenvectors = np.linalg.eig(covariance)

    # Sort by magnitude
    idx = np.argsort(eigenvalues)[::-1]
    axes_lengths = np.sqrt(eigenvalues[idx])
    axes_directions = eigenvectors[:, idx]

    # Compare to A eigenvectors
    A_eigenvalues, A_eigenvectors = np.linalg.eig(A)

    return {
        'axes_lengths': axes_lengths,
        'axes_directions': axes_directions,
        'A_eigenvalues': A_eigenvalues,
        'A_eigenvectors': A_eigenvectors,
        'alignment': check_eigenvector_alignment(axes_directions, A_eigenvectors)
    }
```

### 3.4 Prediction 4: Temporal Coherence Decay

**Hypothesis:** Perturbations below energy threshold should dissipate exponentially: φ(t) ~ exp(-t/τ).

**Test:**
1. Create sub-critical excitation (E < E_critical)
2. Measure autocorrelation C(τ) = <φ(t)φ(t+τ)>
3. Fit exponential: C(τ) ~ exp(-τ/τ_decay)
4. Expect: τ_decay ≈ 1/γ (damping timescale)

**Falsification:** If decay is power-law (C ~ τ^-α) or non-monotonic, dissipation mechanism is different.

**Implementation:**
```python
def test_coherence_decay(agent, duration=1000):
    """
    Measure autocorrelation decay rate.
    """
    # Record field values over time
    phi_history = []
    for t in range(duration):
        phi = agent.wave_packet(grid)
        phi_history.append(phi.copy())
        agent.evolve(dt=1.0)

    # Compute autocorrelation
    phi_mean = np.mean(phi_history, axis=0)
    C = []
    for tau in range(duration // 2):
        correlation = np.mean([
            np.sum((phi_history[t] - phi_mean) * (phi_history[t+tau] - phi_mean))
            for t in range(duration - tau)
        ])
        C.append(correlation)

    # Fit exponential
    tau_values = np.arange(len(C))
    popt, _ = curve_fit(lambda t, tau: np.exp(-t/tau), tau_values, C)
    tau_decay = popt[0]

    return {
        'autocorrelation': C,
        'tau_decay': tau_decay,
        'expected_tau': 1 / gamma,  # Theoretical expectation
        'fit_quality': r_squared(C, np.exp(-tau_values / tau_decay))
    }
```

---

## 4. Implementation Roadmap

### Phase 1: Foundation (Cycles 667-670)

**Goal:** Add explicit wave equation solver to NRM

**Tasks:**
1. ✅ Create `soliton_model.py` module
2. ⏳ Implement anisotropy tensor generator in TranscendentalBridge
3. ⏳ Add wave packet representation to FractalAgent
4. ⏳ Create interference calculator in CompositionEngine

**Deliverables:**
- `code/soliton/soliton_model.py` (new module)
- `bridge/transcendental_bridge.py` (extend with anisotropy method)
- `fractal/fractal_agent.py` (add wave packet methods)
- Unit tests for all new functionality

### Phase 2: Validation (Cycles 671-675)

**Goal:** Test 4 predictions empirically

**Tasks:**
1. ⏳ C257 variant: Directional propagation test
2. ⏳ C258 variant: Resonant frequency sweep
3. ⏳ C259 variant: Ellipsoidal topology measurement
4. ⏳ C260 variant: Coherence decay measurement

**Deliverables:**
- 4 experiment scripts with soliton tests
- Results JSON files with measurements
- Figures showing predictions validated/falsified

### Phase 3: Paper Revision (Cycles 676-680)

**Goal:** Transform white paper into publication-ready manuscript

**Tasks:**
1. ⏳ Rewrite with soliton terminology (no metaphors)
2. ⏳ Add Mathematical Formalism section
3. ⏳ Add Predictions section with experimental results
4. ⏳ Add Discussion with limitations and alternatives

**Deliverables:**
- `papers/soliton_model_manuscript.tex` (LaTeX)
- Compiled PDF with figures
- Supplementary materials (code, data)

### Phase 4: Bioelectric Connection (Cycles 681+)

**Goal:** Compare NRM solitons to Levin lab bioelectric data

**Tasks:**
1. ⏳ Literature review (Levin, Breakspear, Friston bioelectric papers)
2. ⏳ Parameter matching (timescales, spatial scales)
3. ⏳ Topology comparison (ellipsoidal gradients)
4. ⏳ Collaboration outreach (if results promising)

**Deliverables:**
- Comparison document with figures
- Potential collaboration proposal

---

## 5. Open Questions & Limitations

### 5.1 Where Does Anisotropy Come From?

**Three possibilities:**

1. **Fundamental:** Space itself is anisotropic
   - Requires physics evidence (cosmic microwave background anisotropy?)
   - Unlikely to explain biological morphogenesis

2. **Emergent:** Agent interactions create effective anisotropy
   - Density gradients → position-dependent coupling
   - Most defensible for biological applications
   - **Recommended path forward**

3. **Designed:** We choose anisotropic parameters in simulation
   - Honest but limits generality to "computational model of principle"
   - Valid for exploring consequences, not discovering laws

**Action:** Implement emergent anisotropy in Phase 1:

```python
def emergent_anisotropy(agents, position):
    """
    A(r) emerges from local agent density and coupling.

    High density → Strong coupling → Fast propagation
    Gradient direction → Preferred propagation axis
    """
    local_density = sum([gaussian(agent.position - position) for agent in agents])
    gradient = compute_density_gradient(agents, position)

    # Align fast axis with density gradient
    fast_axis = gradient / np.linalg.norm(gradient)

    # Construct anisotropy tensor
    A = local_density * np.eye(3)  # Isotropic baseline
    A += coupling_strength * np.outer(fast_axis, fast_axis)  # Anisotropic component

    return A
```

### 5.2 Transcendental Substrate: Necessary or Sufficient?

**Current status:** Exploratory (per CLAUDE.md)

**Questions:**
- Do π, e, φ frequencies enable richer solitons than PRNG?
- Is computational irreducibility necessary for persistence?
- Or is any high-entropy source sufficient?

**Required:** Ablation study (Phase 2)

### 5.3 Nonlinearity Source

**Wave equation includes:** f(φ) = α φ (1 - φ²)

**Question:** Where does this nonlinearity come from in NRM?

**Candidate sources:**
1. Agent birth/death (population saturation)
2. Energy cap (max 200 units)
3. Resonance threshold (nonlinear coupling)

**Action:** Explicit nonlinearity modeling in Phase 1

### 5.4 Dimensionality

**Current NRM:** Agents in 3D space

**Soliton model:** 3D + time (4D spacetime)

**Question:** Should we simulate full 4D field or project to 3D snapshots?

**Trade-off:**
- Full 4D: More accurate but computationally expensive
- 3D snapshots: Faster but loses temporal structure

**Recommendation:** Start with 3D snapshots (Phase 1), add full 4D if needed (Phase 4)

---

## 6. Terminology Reference

**Replace metaphorical language:**

| Metaphor | Scientific Term |
|----------|----------------|
| "Song" | Spatiotemporal soliton |
| "Note" | Wave pulse / Excitation |
| "Narrative" | Trajectory / Worldline |
| "Story" | Coherent structure |
| "Instrument" | Propagation substrate / Anisotropic medium |
| "Musical theory" | Dispersion relation |
| "Echo" | Interference pattern |
| "Harmony" | Resonance condition |
| "Dissonance" | Anti-resonance |
| "Duration" | Temporal coherence / Lifetime τ |
| "Vortex holding shape" | Topologically protected mode |
| "Continuous shape through time" | Spatiotemporal soliton / 4D worldline |
| "Pulsing ellipsoid" | Breathing mode in anisotropic medium |

---

## 7. References

**Wave physics:**
- Russell, J.S. (1845). "Report on Waves". British Association Reports.
- Korteweg, D.J. & de Vries, G. (1895). "On the Change of Form of Long Waves". Phil. Mag.
- Zabusky, N.J. & Kruskal, M.D. (1965). "Interaction of Solitons in a Collisionless Plasma". Phys. Rev. Lett.

**Anisotropic media:**
- Nye, J.F. (1985). "Physical Properties of Crystals". Oxford University Press.
- Landau, L.D. & Lifshitz, E.M. (1960). "Electrodynamics of Continuous Media".

**Biological morphogenesis:**
- Levin, M. (2014). "Endogenous bioelectric signaling networks". Annu. Rev. Biomed. Eng.
- Levin, M. (2021). "Bioelectric networks: the cognitive glue enabling evolutionary scaling". Anim. Cogn.
- Pietak, A. & Levin, M. (2016). "Exploring instructive physiological signaling". Front. Cell Dev. Biol.

**Pattern formation:**
- Turing, A.M. (1952). "The Chemical Basis of Morphogenesis". Phil. Trans. R. Soc.
- Prigogine, I. & Nicolis, G. (1977). "Self-Organization in Nonequilibrium Systems".

**Soliton theory:**
- Ablowitz, M.J. & Clarkson, P.A. (1991). "Solitons, Nonlinear Evolution Equations". Cambridge.
- Drazin, P.G. & Johnson, R.S. (1989). "Solitons: An Introduction". Cambridge.

---

## 8. Appendices

### Appendix A: Derivation of Dispersion Relation

Starting from wave equation:
```
∂²φ/∂t² = ∇·(A·∇φ)
```

Assume plane wave solution:
```
φ(r,t) = A exp(i(k·r - ωt))
```

Compute derivatives:
```
∂²φ/∂t² = -ω² φ
∇φ = ik φ
∇·(A·∇φ) = ∇·(A·ik φ) = -(A·k)·k φ = -k^T·A·k φ
```

Substitute:
```
-ω² φ = -k^T·A·k φ
```

Dispersion relation:
```
ω²(k) = k^T · A · k
```

For isotropic case A = c² I:
```
ω²(k) = c² |k|²
ω(k) = c|k|
```

For anisotropic case A = diag(c_x², c_y², c_z²):
```
ω²(k) = c_x² k_x² + c_y² k_y² + c_z² k_z²
```

### Appendix B: Soliton Stability Proof (Sketch)

Energy functional:
```
E[φ] = ∫ [1/2 (∂φ/∂t)² + 1/2 ∇φ^T·A·∇φ - F(φ)] dr
```

First variation (Euler-Lagrange equation):
```
δE/δφ = -∂²φ/∂t² + ∇·(A·∇φ) - f(φ) = 0
```

This recovers the wave equation (without dissipation).

Second variation (stability):
```
δ²E = ∫ [δφ_t² + (∇δφ)^T·A·(∇δφ) - f''(φ) δφ²] dr
```

Soliton Φ is stable if:
```
δ²E > 0  for all perturbations δφ
```

This requires:
```
λ_min(A) - f''(Φ) > 0
```

Where λ_min is smallest eigenvalue of A.

For cubic nonlinearity f(φ) = α φ (1 - φ²):
```
f''(φ) = α (1 - 3φ²)
```

Stability condition:
```
λ_min(A) > α (1 - 3Φ²)
```

For small amplitude solitons (Φ << 1):
```
λ_min(A) > α  (always stable)
```

For large amplitude (Φ → 1):
```
λ_min(A) > -2α  (becomes unstable if A too small)
```

**Conclusion:** Anisotropy strength must exceed nonlinearity strength for large-amplitude solitons.

---

**Status:** Mathematical formalism complete, ready for implementation.

**Next steps:**
1. Implement in `code/soliton/` module
2. Extend TranscendentalBridge with anisotropy generation
3. Add wave packet methods to FractalAgent
4. Design experiments to test 4 predictions

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Date:** 2025-10-30
**Version:** 1.0 (Draft for integration with NRM)
