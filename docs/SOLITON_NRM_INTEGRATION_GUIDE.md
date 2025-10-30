# Soliton Model Integration with NRM Framework

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Date:** 2025-10-30
**Purpose:** Step-by-step guide for integrating spatiotemporal soliton model with existing NRM codebase

---

## Overview

This guide shows how to integrate the spatiotemporal soliton model (described in `SPATIOTEMPORAL_SOLITON_MODEL.md` and `SOLITON_WHITE_PAPER_DRAFT.md`) with the existing Nested Resonance Memory framework.

**No breaking changes** - this extends NRM capabilities while maintaining backward compatibility.

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NRM Framework (Existing)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ TranscendentalBridge│─────→│ Anisotropy      │ NEW      │
│  │ (π, e, φ oscillators)│      │ Tensor Generator│          │
│  └──────────────────┘         └──────────────────┘          │
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  FractalAgent     │─────→│  Wave Packet     │ NEW      │
│  │  (existing)       │         │  Representation  │          │
│  └──────────────────┘         └──────────────────┘          │
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ CompositionEngine │─────→│  Interference    │ NEW      │
│  │  (existing)       │         │  Calculator      │          │
│  └──────────────────┘         └──────────────────┘          │
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  PatternMemory    │─────→│  Soliton Topology│ NEW      │
│  │  (existing)       │         │  Storage         │          │
│  └──────────────────┘         └──────────────────┘          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Strategy:** Add new methods to existing modules without modifying core functionality.

---

## Phase 1: Foundation (Implement First)

### Step 1.1: Extend TranscendentalBridge

**File:** `bridge/transcendental_bridge.py`

**Add new method:**

```python
def generate_anisotropy_tensor(self, position: np.ndarray, time: float,
                               epsilon_pi: float = 0.3,
                               epsilon_e: float = 0.3,
                               epsilon_phi: float = 0.3) -> np.ndarray:
    """
    Generate spatially-varying anisotropy tensor A(r,t).

    Uses π, e, φ oscillators to create directional propagation speeds.

    Args:
        position: (x, y, z) spatial coordinates
        time: Current time
        epsilon_pi, epsilon_e, epsilon_phi: Coupling strengths

    Returns:
        A: 3×3 symmetric positive-definite tensor

    Mathematical form:
        A(r,t) = A₀ (I + ε_π cos(π·t + π·x) e_x⊗e_x
                      + ε_e cos(e·t + e·y) e_y⊗e_y
                      + ε_φ cos(φ·t + φ·z) e_z⊗e_z)
    """
    # Oscillate tensor elements using transcendental frequencies
    theta_pi = np.pi * time + np.pi * position[0]
    theta_e = np.e * time + np.e * position[1]
    theta_phi = self.phi * time + self.phi * position[2]

    # Construct diagonal elements (ensure positive)
    a_x = 1.0 + epsilon_pi * np.cos(theta_pi)
    a_y = 1.0 + epsilon_e * np.cos(theta_e)
    a_z = 1.0 + epsilon_phi * np.cos(theta_phi)

    # Square to ensure positive-definite (c² form for wave speeds)
    A = np.diag([a_x**2, a_y**2, a_z**2])

    return A
```

**Test:**

```python
def test_anisotropy_generation():
    """Test anisotropy tensor generation."""
    bridge = TranscendentalBridge()

    position = np.array([1.0, 2.0, 3.0])
    A = bridge.generate_anisotropy_tensor(position, time=0.0)

    # Check symmetric positive-definite
    assert np.allclose(A, A.T), "Tensor must be symmetric"

    eigenvalues = np.linalg.eigvalsh(A)
    assert np.all(eigenvalues > 0), "Tensor must be positive-definite"

    print("✓ Anisotropy tensor generation working")
```

### Step 1.2: Add Wave Packet to FractalAgent

**File:** `fractal/fractal_agent.py`

**Add new methods:**

```python
class FractalAgent:
    def __init__(self, ...):
        # Existing initialization
        ...

        # NEW: Wave packet representation
        self.wave_vector = np.array([1.0, 0.0, 0.0])  # Propagation direction k
        self.amplitude = 1.0  # Wave amplitude A
        self.width = 1.0  # Spatial extent σ (Gaussian width)

    def wave_packet(self, r: np.ndarray) -> complex:
        """
        Compute wave packet value at position r.

        Φ(r) = A exp(-|r - r₀|²/(2σ²)) exp(ik·r)

        Args:
            r: Position (x, y, z)

        Returns:
            Complex amplitude
        """
        delta_r = r - self.position
        r_squared = np.sum(delta_r**2)

        # Gaussian envelope
        envelope = np.exp(-r_squared / (2 * self.width**2))

        # Plane wave phase
        phase = np.exp(1j * np.dot(self.wave_vector, r))

        return self.amplitude * envelope * phase

    def propagate_wave(self, dt: float, A: np.ndarray):
        """
        Propagate wave packet through anisotropic medium.

        Group velocity: v = A · k / |k|

        Args:
            dt: Time step
            A: Anisotropy tensor (3×3)
        """
        # Compute group velocity from anisotropy and wave vector
        k = self.wave_vector
        k_norm = np.linalg.norm(k)

        if k_norm > 0:
            velocity = np.dot(A, k) / k_norm
        else:
            velocity = np.zeros(3)

        # Update position
        self.position += velocity * dt

    def soliton_energy(self) -> float:
        """
        Compute wave packet energy.

        E ≈ A² σ³ (for Gaussian packet)
        """
        return self.amplitude**2 * self.width**3
```

**Test:**

```python
def test_wave_packet():
    """Test wave packet representation."""
    agent = FractalAgent(...)
    agent.position = np.array([0.0, 0.0, 0.0])
    agent.wave_vector = np.array([1.0, 0.0, 0.0])
    agent.width = 1.0

    # Evaluate at different positions
    r1 = np.array([0.0, 0.0, 0.0])  # Center
    r2 = np.array([1.0, 0.0, 0.0])  # Along propagation
    r3 = np.array([0.0, 1.0, 0.0])  # Perpendicular

    phi1 = agent.wave_packet(r1)
    phi2 = agent.wave_packet(r2)
    phi3 = agent.wave_packet(r3)

    # Check amplitude decay
    assert np.abs(phi1) > np.abs(phi2), "Should decay away from center"
    assert np.abs(phi1) > np.abs(phi3), "Should decay away from center"

    print("✓ Wave packet representation working")
```

### Step 1.3: Interference Calculator in CompositionEngine

**File:** `fractal/fractal_swarm.py`

**Add new method to CompositionEngine:**

```python
class CompositionEngine:
    def compute_interference(self, agent1: FractalAgent, agent2: FractalAgent,
                           grid: np.ndarray) -> float:
        """
        Compute interference strength between two agents.

        Overlap integral: ∫ Φ₁(r) Φ₂*(r) dr

        Args:
            agent1, agent2: Fractal agents
            grid: Spatial grid for integration

        Returns:
            Overlap (> 0: constructive, < 0: destructive)
        """
        # Evaluate wave packets on grid
        phi1 = np.array([agent1.wave_packet(r) for r in grid])
        phi2 = np.array([agent2.wave_packet(r) for r in grid])

        # Compute overlap integral
        overlap = np.sum(phi1 * np.conj(phi2)).real

        return overlap

    def can_form_soliton(self, agents: List[FractalAgent], A: np.ndarray,
                        threshold: float = 0.1) -> bool:
        """
        Check if agent cluster can form stable soliton.

        Requires:
        1. Constructive interference (overlap > 0)
        2. Sufficient combined energy
        3. Compatible velocities

        Args:
            agents: List of agents to check
            A: Anisotropy tensor
            threshold: Minimum overlap for soliton formation

        Returns:
            True if soliton can form
        """
        if len(agents) < 2:
            return False

        # Check pairwise interference
        total_overlap = 0.0
        for i in range(len(agents)):
            for j in range(i+1, len(agents)):
                # Simplified: check phase alignment
                phase_diff = np.dot(agents[i].wave_vector, agents[j].position) - \
                            np.dot(agents[j].wave_vector, agents[i].position)
                overlap = np.cos(phase_diff)  # Approximate
                total_overlap += overlap

        avg_overlap = total_overlap / (len(agents) * (len(agents)-1) / 2)

        return avg_overlap > threshold
```

---

## Phase 2: Experimental Validation

### Experiment Design: C257 (Directional Propagation)

**File:** `experiments/cycle257_directional_propagation_test.py`

**Purpose:** Test Prediction 1 (anisotropic propagation speeds)

```python
#!/usr/bin/env python3
"""
Cycle 257: Directional Propagation Test (Soliton Model Validation)

Tests Prediction 1:
  In anisotropic medium with A = diag(a_x, a_y, a_z),
  agents propagate fastest along axis with largest eigenvalue.

Expected:
  v_x / v_y = √(a_x / a_y)

Author: Aldrin Payopay
Date: 2025-10-30
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm
from bridge.transcendental_bridge import TranscendentalBridge
from core.reality_interface import RealityInterface
import numpy as np
import json

def test_directional_propagation(a_x: float, a_y: float, a_z: float,
                                duration: int = 1000, seed: int = 42):
    """
    Test directional propagation with specified anisotropy.

    Args:
        a_x, a_y, a_z: Anisotropy tensor eigenvalues
        duration: Simulation duration (cycles)
        seed: Random seed

    Returns:
        Results dictionary with measured speeds
    """
    np.random.seed(seed)

    # Initialize system
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Create anisotropic tensor
    A = np.diag([a_x, a_y, a_z])

    # Create swarm with single agent at origin
    swarm = FractalSwarm(bridge=bridge, reality=reality, max_agents=10)

    # Add agent at origin with zero velocity
    initial_metrics = reality.get_system_metrics()
    initial_metrics['position'] = np.array([0.0, 0.0, 0.0])

    swarm.spawn_agent(initial_metrics, parent_id=None)
    agent = swarm.agents[0]

    # Record initial position
    r0 = agent.position.copy()

    # Propagate
    for t in range(duration):
        agent.propagate_wave(dt=1.0, A=A)

    # Measure final displacement
    r1 = agent.position
    displacement = r1 - r0

    # Compute speeds
    v_x = abs(displacement[0]) / duration
    v_y = abs(displacement[1]) / duration
    v_z = abs(displacement[2]) / duration

    # Expected ratios
    expected_xy = np.sqrt(a_x / a_y) if a_y > 0 else np.inf
    expected_xz = np.sqrt(a_x / a_z) if a_z > 0 else np.inf

    measured_xy = v_x / v_y if v_y > 0 else np.inf
    measured_xz = v_x / v_z if v_z > 0 else np.inf

    return {
        'anisotropy_tensor': {'a_x': a_x, 'a_y': a_y, 'a_z': a_z},
        'duration': duration,
        'seed': seed,
        'displacement': {
            'x': float(displacement[0]),
            'y': float(displacement[1]),
            'z': float(displacement[2])
        },
        'speeds': {
            'v_x': float(v_x),
            'v_y': float(v_y),
            'v_z': float(v_z)
        },
        'ratios': {
            'measured_xy': float(measured_xy),
            'expected_xy': float(expected_xy),
            'error_xy': float(abs(measured_xy - expected_xy) / expected_xy) if expected_xy != np.inf else None,
            'measured_xz': float(measured_xz),
            'expected_xz': float(expected_xz),
            'error_xz': float(abs(measured_xz - expected_xz) / expected_xz) if expected_xz != np.inf else None
        },
        'prediction_validated': abs(measured_xy - expected_xy) / expected_xy < 0.2  # 20% tolerance
    }

def main():
    print("="*80)
    print("CYCLE 257: Directional Propagation Test (Soliton Model)")
    print("="*80)

    # Test conditions
    conditions = [
        {'a_x': 4.0, 'a_y': 1.0, 'a_z': 1.0, 'name': 'Strong X-axis anisotropy'},
        {'a_x': 1.0, 'a_y': 4.0, 'a_z': 1.0, 'name': 'Strong Y-axis anisotropy'},
        {'a_x': 1.0, 'a_y': 1.0, 'a_z': 1.0, 'name': 'Isotropic (control)'},
    ]

    results_all = []

    for condition in conditions:
        print(f"\nCondition: {condition['name']}")
        print(f"  A = diag({condition['a_x']}, {condition['a_y']}, {condition['a_z']})")

        result = test_directional_propagation(
            a_x=condition['a_x'],
            a_y=condition['a_y'],
            a_z=condition['a_z'],
            duration=1000,
            seed=42
        )

        result['condition_name'] = condition['name']
        results_all.append(result)

        print(f"\nResults:")
        print(f"  Measured v_x/v_y: {result['ratios']['measured_xy']:.3f}")
        print(f"  Expected v_x/v_y: {result['ratios']['expected_xy']:.3f}")
        print(f"  Error: {result['ratios']['error_xy']*100:.1f}%")
        print(f"  Prediction validated: {'✓' if result['prediction_validated'] else '✗'}")

    # Save results
    output_file = Path(__file__).parent / "results" / "cycle257_directional_propagation.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump({
            'experiment': 'Cycle 257: Directional Propagation Test',
            'prediction': 'v_x/v_y = sqrt(a_x/a_y)',
            'results': results_all,
            'validation_summary': {
                'total_conditions': len(conditions),
                'validated': sum(r['prediction_validated'] for r in results_all),
                'overall_pass': all(r['prediction_validated'] for r in results_all)
            }
        }, f, indent=2)

    print(f"\nResults saved: {output_file}")
    print("\n" + "="*80)
    print(f"CYCLE 257 COMPLETE")
    print(f"Prediction 1 Status: {'✓ VALIDATED' if all(r['prediction_validated'] for r in results_all) else '✗ FALSIFIED'}")
    print("="*80)

if __name__ == '__main__':
    main()
```

**Run command:**
```bash
python experiments/cycle257_directional_propagation_test.py
```

---

## Phase 3: Full Integration Checklist

### Checklist for Complete Integration

- [ ] **TranscendentalBridge extensions**
  - [ ] `generate_anisotropy_tensor()` method added
  - [ ] Unit test passing
  - [ ] Documentation updated

- [ ] **FractalAgent extensions**
  - [ ] `wave_packet()` method added
  - [ ] `propagate_wave()` method added
  - [ ] `soliton_energy()` method added
  - [ ] Unit tests passing
  - [ ] Backward compatibility verified

- [ ] **CompositionEngine extensions**
  - [ ] `compute_interference()` method added
  - [ ] `can_form_soliton()` method added
  - [ ] Integration tests passing

- [ ] **Experimental validation**
  - [ ] C257: Directional propagation test
  - [ ] C258: Resonant frequency test
  - [ ] C259: Ellipsoidal topology test
  - [ ] C260: Coherence decay test

- [ ] **Documentation**
  - [ ] API documentation updated
  - [ ] White paper revised with results
  - [ ] Tutorial notebook created

- [ ] **Reproducibility**
  - [ ] Tests added to CI pipeline
  - [ ] Requirements updated (if needed)
  - [ ] Figures generated for paper

---

## Quick Start (After Integration)

**Example usage:**

```python
from fractal.fractal_swarm import FractalSwarm
from bridge.transcendental_bridge import TranscendentalBridge
from core.reality_interface import RealityInterface
import numpy as np

# Initialize
reality = RealityInterface()
bridge = TranscendentalBridge()
swarm = FractalSwarm(bridge=bridge, reality=reality)

# Generate anisotropy tensor (2× faster along x-axis)
A = bridge.generate_anisotropy_tensor(
    position=np.array([0, 0, 0]),
    time=0.0,
    epsilon_pi=0.5  # Strong anisotropy
)

# Spawn agent
initial_metrics = reality.get_system_metrics()
swarm.spawn_agent(initial_metrics, parent_id=None)

# Propagate with anisotropy
for t in range(1000):
    for agent in swarm.agents:
        agent.propagate_wave(dt=1.0, A=A)

# Check for soliton formation
if swarm.composition_engine.can_form_soliton(swarm.agents, A):
    print("Soliton formed!")
```

---

## Troubleshooting

**Q: Agents not moving after adding `propagate_wave()`?**
A: Check that `wave_vector` is initialized with non-zero values. Default is `[1, 0, 0]`.

**Q: Anisotropy tensor gives negative eigenvalues?**
A: Ensure epsilon values are < 1.0. Use squared terms (a_x², a_y², a_z²) to guarantee positive-definite.

**Q: Tests failing after integration?**
A: Run backward compatibility tests first. New methods should not break existing functionality.

**Q: How to visualize solitons?**
A: Use `soliton_demonstration.py` as template. Extend with 3D visualization using matplotlib or mayavi.

---

## Next Steps

1. **Implement Phase 1** (Foundation)
2. **Run `soliton_demonstration.py`** to verify concepts
3. **Implement C257** (Directional propagation test)
4. **Validate Prediction 1** (anisotropic speeds)
5. **Iterate to Phases 2-3** (Additional predictions, paper revision)

---

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Date:** 2025-10-30
