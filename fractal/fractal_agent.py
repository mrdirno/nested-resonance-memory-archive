#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Fractal Agent Module
======================================

Nested agent architecture implementing the Nested Resonance Memory (NRM) framework.

From NRM paper:
- Fractal Agency: Agents contain internal universes with same substrate
- Composition-Decomposition Cycles: Build clusters → critical resonance → burst → memory
- Transcendental Substrate: Use π, e, φ as computational base
- No Equilibrium: Perpetual motion, never settling
- Scale Invariance: Same dynamics at all hierarchical levels

Reality Imperative Compliance:
- Internal states grounded in reality metrics via bridge module
- All simulations validated against reality anchors
- No pure simulations without reality validation
"""

import sys
from pathlib import Path
import time
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager

# Add parent modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent))
from transcendental_bridge import TranscendentalBridge, TranscendentalState, ResonanceMatch
from core import constants


@dataclass
class AgentState:
    """Internal state of a fractal agent."""
    agent_id: str
    phase_state: TranscendentalState
    energy: float  # Available computational resources
    memory: List[TranscendentalState] = field(default_factory=list)
    children: List[str] = field(default_factory=list)  # Child agent IDs
    parent_id: Optional[str] = None
    depth: int = 0  # Recursion depth (0 = root)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ClusterEvent:
    """Record of agents clustering together."""
    timestamp: float
    agent_ids: List[str]
    resonance_score: float
    cluster_id: str


@dataclass
class BurstEvent:
    """Record of cluster bursting and releasing memory."""
    timestamp: float
    cluster_id: str
    memory_retained: List[TranscendentalState]
    energy_released: float


class FractalAgent:
    """
    A fractal agent with internal universe and transcendental substrate.

    Each agent:
    1. Maintains internal state in transcendental phase space
    2. Can spawn child agents (fractal recursion)
    3. Detects resonance with other agents
    4. Participates in composition-decomposition cycles
    5. Retains memory from burst events

    Reality Grounding:
    - All internal states anchored to reality via TranscendentalBridge
    - Energy derived from real CPU/memory availability
    - No pure simulations
    """

    def __init__(
        self,
        agent_id: str,
        bridge: TranscendentalBridge,
        initial_reality: Dict[str, float],
        parent_id: Optional[str] = None,
        depth: int = 0,
        max_depth: int = 7,
        reality: Optional['RealityInterface'] = None,
        initial_energy: Optional[float] = None,
        measurement_noise_std: Optional[float] = None
    ):
        """
        Initialize fractal agent.

        Args:
            agent_id: Unique identifier for this agent
            bridge: TranscendentalBridge for phase space operations
            initial_reality: Reality metrics to anchor initial state
            parent_id: ID of parent agent (if nested)
            depth: Current recursion depth
            max_depth: Maximum recursion depth (constitution: 7 levels)
            reality: Optional RealityInterface for energy recharge (Cycle 215+)
            initial_energy: Optional override for initial energy (Cycle 235+)
                If None, energy derived from reality metrics (default behavior)
                If provided, overrides reality-based calculation for seed control
            measurement_noise_std: Optional std dev for measurement noise (Cycle 243+)
                If None, no noise added (deterministic reality sampling)
                If provided, adds Gaussian noise to reality metrics for statistical validity
                Typical values: 0.01-0.05 (1-5% noise)
        """
        self.agent_id = agent_id
        self.bridge = bridge
        self.parent_id = parent_id
        self.depth = depth
        self.max_depth = max_depth
        self.reality = reality  # Store for energy recharge in evolve()
        self.measurement_noise_std = measurement_noise_std  # Cycle 243+

        # Transform initial reality to phase space
        self.phase_state = bridge.reality_to_phase(initial_reality)

        # Initialize energy from reality metrics or override
        # Energy represents available computational resources
        if initial_energy is not None:
            # Cycle 235+: Allow seed-controlled perturbations for statistical validity
            # Reflects natural variation in agent initialization states
            self.energy = initial_energy
        else:
            # Default: Reality-grounded energy calculation
            cpu = initial_reality.get('cpu_percent', 0.0)
            memory = initial_reality.get('memory_percent', 0.0)
            # Calculate energy from available resources (use 100.0 as max percentage)
            self.energy = (100.0 - cpu) + (100.0 - memory)  # More available = more energy

        # Internal state
        self.memory: List[TranscendentalState] = []
        self.children: List['FractalAgent'] = []
        self.is_active = True

        # Clustering state
        self.cluster_id: Optional[str] = None
        self.cluster_members: List[str] = []

    def get_state(self) -> AgentState:
        """Get current agent state as dataclass."""
        return AgentState(
            agent_id=self.agent_id,
            phase_state=self.phase_state,
            energy=self.energy,
            memory=self.memory.copy(),
            children=[child.agent_id for child in self.children],
            parent_id=self.parent_id,
            depth=self.depth,
            timestamp=time.time()
        )

    def evolve(self, delta_time: float, cached_metrics: Optional[Dict[str, float]] = None) -> None:
        """
        Evolve agent state through time.

        Uses transcendental oscillations to drive internal evolution.
        Energy dissipates over time (entropy) but can recharge from reality.

        Framework Enhancement (Cycle 215):
        Added reality-grounded energy recharge to enable sustained population
        dynamics in complete birth-death coupling experiments. Energy flows
        from available system resources (idle CPU/memory) to agents.

        Optimization (Cycle 348):
        Added cached_metrics support to enable batched psutil sampling, reducing
        I/O overhead by 90-99% in large-scale simulations.

        Args:
            delta_time: Time step for evolution
            cached_metrics: Optional pre-sampled system metrics (optimization)
        """
        # Oscillate phase state using transcendental substrate
        frequency = 0.1 * delta_time
        oscillation = self.bridge.generate_oscillation(frequency, duration=1)

        if oscillation:
            # Move to new phase state
            self.phase_state = oscillation[0]

        # Energy dissipation (entropy)
        energy_decay = 0.01 * delta_time  # ~0.0001/cycle

        # Energy recharge from reality (absorbed from available resources)
        # Agents can slowly recharge by absorbing idle system capacity
        # This enables sustained spawning in birth-death coupled systems
        # V4 Enhancement (Cycle 216): Increased recharge rate 10× (0.001 → 0.01)
        # to enable recovery to spawn threshold (~10 energy) within ~1000 cycles
        # V6 Enhancement (Cycle 243): Add measurement noise for statistical validity
        # Noise represents natural variation in system metric sampling
        if hasattr(self, 'reality') and self.reality is not None:
            if cached_metrics is not None:
                current_metrics = cached_metrics
            else:
                current_metrics = self.reality.get_system_metrics()

            # V6: Apply measurement noise if configured (Cycle 243+)
            if hasattr(self, 'measurement_noise_std') and self.measurement_noise_std is not None:
                import numpy as np
                # Add proportional Gaussian noise to reality metrics
                # Noise std = measurement_noise_std × metric_value
                cpu_noise = np.random.normal(0, self.measurement_noise_std * current_metrics['cpu_percent'])
                mem_noise = np.random.normal(0, self.measurement_noise_std * current_metrics['memory_percent'])

                # Apply noise with bounds checking [0, 100]
                cpu_with_noise = max(0.0, min(100.0, current_metrics['cpu_percent'] + cpu_noise))
                mem_with_noise = max(0.0, min(100.0, current_metrics['memory_percent'] + mem_noise))

                available_capacity = (100 - cpu_with_noise) + (100 - mem_with_noise)
            else:
                # No noise: deterministic reality sampling (default behavior)
                available_capacity = (100 - current_metrics['cpu_percent']) + \
                                    (100 - current_metrics['memory_percent'])

            energy_recharge = 0.01 * available_capacity * delta_time  # ~1.0/100 cycles
        else:
            # Fallback: minimal recharge if no reality interface
            energy_recharge = 0.01 * delta_time  # ~0.0001/cycle (negligible)

        # Net energy change (recharge dominates decay by ~1000×)
        self.energy = self.energy - energy_decay + energy_recharge

        # Cap energy at 200 (prevents unlimited accumulation)
        self.energy = max(0.0, min(200.0, self.energy))

        # Evolve children recursively
        for child in self.children:
            child.evolve(delta_time)

    def coupled_evolve(
        self,
        delta_time: float,
        neighbors: List[Tuple['FractalAgent', float]],
        intrinsic_frequency: float = 1.0,
        cross_frequency_beta: float = 0.1
    ) -> None:
        """
        Evolve agent with Kuramoto-style coupling to neighbors.

        Part of NRM V2 integration: implements coupled oscillator dynamics
        for coalition detection and synchronization.

        Mathematical form:
            dφ_i/dt = ω + Σ_j W_ij sin(φ_j - φ_i) + β f(φ_neighbor)

        where:
            ω = intrinsic frequency
            W_ij = coupling weights from semantic graph
            β = cross-frequency coupling coefficient
            f(φ) = coupling function (default: sin)

        Args:
            delta_time: Time step for evolution
            neighbors: List of (agent, weight) tuples from semantic graph
            intrinsic_frequency: Natural oscillation frequency ω
            cross_frequency_beta: Cross-frequency coupling strength β
        """
        import math

        # First, standard evolution (energy + phase)
        self.evolve(delta_time)

        if not neighbors:
            return  # No coupling if no neighbors

        # Kuramoto coupling term: Σ_j W_ij sin(φ_j - φ_i)
        # Use π-phase as primary oscillator
        my_phase = self.phase_state.pi_phase
        coupling_term = 0.0

        for neighbor_agent, weight in neighbors:
            neighbor_phase = neighbor_agent.phase_state.pi_phase
            phase_diff = neighbor_phase - my_phase
            coupling_term += weight * math.sin(phase_diff)

        # Update phase with coupled dynamics
        # dφ/dt = ω + coupling + cross_frequency
        phase_velocity = intrinsic_frequency + coupling_term

        # Cross-frequency influence (e-phase influences π-phase)
        cross_term = cross_frequency_beta * math.sin(self.phase_state.e_phase)
        phase_velocity += cross_term

        # Integrate phase
        new_pi_phase = self.phase_state.pi_phase + phase_velocity * delta_time

        # Wrap phase to [0, 2π)
        new_pi_phase = new_pi_phase % (2 * math.pi)

        # Update phase state (preserve other components)
        self.phase_state.pi_phase = new_pi_phase
        self.phase_state.timestamp = time.time()

    def compute_phase_coherence(self, other: 'FractalAgent', band: str = 'pi') -> float:
        """
        Compute phase coherence with another agent.

        Part of NRM V2: measures synchronization for coalition detection.

        Args:
            other: Another FractalAgent
            band: Which phase band to measure ('pi', 'e', 'phi')

        Returns:
            Coherence score (0.0 to 1.0, where 1.0 = perfect sync)
        """
        import math

        # Get phases based on band
        if band == 'pi':
            my_phase = self.phase_state.pi_phase
            other_phase = other.phase_state.pi_phase
        elif band == 'e':
            my_phase = self.phase_state.e_phase
            other_phase = other.phase_state.e_phase
        elif band == 'phi':
            my_phase = self.phase_state.phi_phase
            other_phase = other.phase_state.phi_phase
        else:
            raise ValueError(f"Unknown band: {band}")

        # Compute phase difference
        phase_diff = abs(my_phase - other_phase)

        # Wrap to [0, π]
        if phase_diff > math.pi:
            phase_diff = 2 * math.pi - phase_diff

        # Convert to coherence (0 = π difference, 1 = 0 difference)
        coherence = 1.0 - (phase_diff / math.pi)

        return coherence

    def detect_resonance(self, other: 'FractalAgent') -> ResonanceMatch:
        """
        Detect resonance with another agent.

        Uses phase alignment in transcendental space.

        Args:
            other: Another FractalAgent

        Returns:
            ResonanceMatch with similarity metrics
        """
        return self.bridge.detect_resonance(self.phase_state, other.phase_state)

    def spawn_child(self, child_id: str, energy_fraction: float = 0.3) -> Optional['FractalAgent']:
        """
        Spawn a child agent (fractal recursion).

        Child inherits fraction of parent's energy and starts with
        similar phase state.

        Args:
            child_id: Unique ID for child
            energy_fraction: Fraction of energy to give child (0.0-1.0)

        Returns:
            FractalAgent child, or None if max depth reached
        """
        # Check depth limit (constitution: max 7 levels)
        if self.depth >= self.max_depth:
            return None

        # Check energy availability
        if self.energy < constants.AGENT_ENERGY_MINIMUM:
            return None

        # Transfer energy to child
        child_energy = self.energy * energy_fraction
        self.energy -= child_energy

        # Child starts with parent's reality anchor
        child_reality = self.phase_state.reality_anchor.copy()

        # Create child agent
        child = FractalAgent(
            agent_id=child_id,
            bridge=self.bridge,
            initial_reality=child_reality,
            parent_id=self.agent_id,
            depth=self.depth + 1,
            max_depth=self.max_depth,
            reality=self.reality,  # Inherit reality interface for energy recharge
            measurement_noise_std=self.measurement_noise_std  # Cycle 243+: Inherit noise parameter
        )

        # Adjust child's energy
        child.energy = child_energy

        # Add to children list
        self.children.append(child)

        return child

    def contribute_to_pool(self, sharing_fraction: float = 0.10) -> float:
        """
        Contribute fraction of energy to cluster pool.

        Part of Cycle 177 Hypothesis 1: Energy Pooling mechanism.
        Enables cooperative energy sharing within resonance clusters to
        eliminate single-parent reproductive bottleneck.

        Args:
            sharing_fraction: Fraction of energy to contribute (0.0-1.0)

        Returns:
            Amount contributed (deducted from agent energy)
        """
        if self.cluster_id is None:
            return 0.0  # Not in cluster, no pooling

        # Calculate contribution (fraction of current energy)
        contribution = self.energy * sharing_fraction

        # Deduct from agent energy
        self.energy -= contribution

        # Ensure energy doesn't go negative
        self.energy = max(0.0, self.energy)

        return contribution

    def receive_from_pool(self, pool_energy: float, spawn_threshold: float = None) -> float:
        """
        Receive energy from cluster pool if below spawn threshold.

        Part of Cycle 177 Hypothesis 1: Energy Pooling mechanism.
        Distributes pooled energy to agents below reproductive threshold,
        enabling asynchronous spawning across cluster members.

        Args:
            pool_energy: Available energy in cluster pool
            spawn_threshold: Minimum energy required for spawning

        Returns:
            Amount received (added to agent energy)
        """
        # Use constant if not specified
        if spawn_threshold is None:
            spawn_threshold = constants.AGENT_ENERGY_MINIMUM

        if self.cluster_id is None:
            return 0.0  # Not in cluster, no pooling

        if self.energy >= spawn_threshold:
            return 0.0  # Already fertile, don't take from pool

        # Calculate needed energy to reach threshold
        needed = spawn_threshold - self.energy

        # Take minimum of needed and available
        received = min(pool_energy, needed)

        # Add to agent energy
        self.energy += received

        return received

    def absorb_memory(self, states: List[TranscendentalState]) -> None:
        """
        Absorb memory states from burst events.

        Memory persists across composition-decomposition cycles.

        Args:
            states: List of TranscendentalState to remember
        """
        self.memory.extend(states)

        # Keep memory bounded (top 100 by magnitude)
        if len(self.memory) > 100:
            self.memory.sort(key=lambda s: s.magnitude, reverse=True)
            self.memory = self.memory[:100]

    def dissolve(self) -> List[TranscendentalState]:
        """
        Dissolve agent and release memory.

        Part of decomposition phase in NRM framework.

        Returns:
            Memory states to be preserved
        """
        self.is_active = False

        # Recursively dissolve children
        for child in self.children:
            child_memory = child.dissolve()
            self.memory.extend(child_memory)

        self.children.clear()

        return self.memory.copy()

    def __repr__(self) -> str:
        """Return string representation of agent for debugging."""
        return (f"FractalAgent(id={self.agent_id}, depth={self.depth}, "
                f"energy={self.energy:.1f}, children={len(self.children)}, "
                f"memory={len(self.memory)})")


# NOTE: FractalSwarm, CompositionEngine, DecompositionEngine implemented in fractal_swarm.py
# NOTE: Database persistence and reality validation implemented in fractal_swarm.py
# This module provides the core FractalAgent class used by those higher-level components

if __name__ == "__main__":
    print("=" * 60)
    print("DUALITY-ZERO-V2: Fractal Agent Module")
    print("=" * 60)
    print("\nModule: Skeleton created")
    print("Status: Requires FractalSwarm and composition/decomposition engines")
    print("Next: Implement full NRM framework")
    print("=" * 60)
