"""
FractalAgent - Core Agent Class with Internal State Space

Implements fractal agents as internal Python objects with composition-decomposition cycles.
Agents maintain internal state spaces undergoing transformations per NRM framework.

Theoretical Basis:
    - Nested Resonance Memory: Fractal structure across scales
    - Composition: Cluster formation through resonance alignment
    - Decomposition: Burst dissolution releasing constituent agents
    - Memory Retention: Successful patterns persist across transformations

Reality Grounding:
    - All state stored in Python dicts/objects (no external services)
    - Resource tracking via psutil metrics
    - Persistence via SQLite (if enabled)
    - Measurable depth, resonance, memory metrics

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
"""

import uuid
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class AgentState:
    """Internal state space for a fractal agent.

    Attributes:
        agent_id: Unique identifier (UUID)
        depth: Hierarchical level (0=base, 1=cluster, 2=swarm, ...)
        energy: Current energy level (normalized 0-1)
        phase: Transcendental phase (0-2π radians)
        position: Spatial coordinates in phase space
        velocity: Rate of phase change
        resonance: Resonance strength with environment (0-1)
        memory: Pattern memory from successful transformations
        birth_time: Timestamp of agent creation
        last_update: Timestamp of last state update
        parent_id: ID of parent agent (if decomposed from cluster)
        children_ids: IDs of child agents (if composed into cluster)
        cluster_id: ID of current cluster membership (if any)
    """
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    depth: int = 0
    energy: float = 1.0
    phase: float = 0.0
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: float = 0.0
    resonance: float = 0.0
    memory: Dict[str, float] = field(default_factory=dict)
    birth_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None
    children_ids: Set[str] = field(default_factory=set)
    cluster_id: Optional[str] = None


class FractalAgent:
    """Fractal agent with internal state space and composition-decomposition dynamics.

    Core NRM Implementation:
        - Internal state space (no external services)
        - Composition: Cluster with other agents via resonance
        - Decomposition: Burst into constituent agents
        - Memory: Retain patterns across transformations
        - Reality-grounded: All operations measurable

    Usage:
        agent = FractalAgent(depth=0)
        agent.update_phase(delta_t=0.01)
        agent.calculate_resonance(other_agent)
        cluster = agent.compose_with([other_agent1, other_agent2])
        constituents = cluster.decompose()

    Attributes:
        state: Internal state space (AgentState)
        _composition_history: Record of composition events
        _decomposition_history: Record of decomposition events
        _pattern_memory: Successful patterns retained across transformations
    """

    def __init__(
        self,
        depth: int = 0,
        energy: float = 1.0,
        phase: float = 0.0,
        position: Optional[np.ndarray] = None,
        agent_id: Optional[str] = None,
    ):
        """Initialize fractal agent with internal state space.

        Args:
            depth: Hierarchical level (0=base agent, 1=cluster, 2=swarm, ...)
            energy: Initial energy level (normalized 0-1)
            phase: Initial transcendental phase (0-2π radians)
            position: Initial position in phase space (default: origin)
            agent_id: Optional UUID (auto-generated if None)
        """
        if position is None:
            position = np.zeros(3)

        self.state = AgentState(
            agent_id=agent_id if agent_id else str(uuid.uuid4()),
            depth=depth,
            energy=energy,
            phase=phase,
            position=position.copy(),
        )

        # Composition-decomposition history
        self._composition_history: List[Dict] = []
        self._decomposition_history: List[Dict] = []

        # Pattern memory (successful strategies persist)
        self._pattern_memory: Dict[str, float] = {}

    def update_phase(self, delta_t: float, frequency: float = 1.0) -> None:
        """Update agent's transcendental phase based on time evolution.

        Phase evolution follows: φ(t+Δt) = φ(t) + 2π * f * Δt (mod 2π)

        Args:
            delta_t: Time step (seconds)
            frequency: Oscillation frequency (Hz)
        """
        # Phase evolution (transcendental dynamics)
        self.state.phase = (self.state.phase + 2 * np.pi * frequency * delta_t) % (2 * np.pi)

        # Velocity update (rate of phase change)
        self.state.velocity = 2 * np.pi * frequency

        # Update timestamp
        self.state.last_update = datetime.now()

    def calculate_resonance(self, other: 'FractalAgent') -> float:
        """Calculate resonance strength with another agent via phase alignment.

        Resonance formula: R = cos(Δφ) where Δφ = φ₁ - φ₂

        Perfect alignment (Δφ=0): R = 1.0 (constructive resonance)
        Opposite phase (Δφ=π): R = -1.0 (destructive resonance)
        Quadrature (Δφ=π/2): R = 0.0 (no resonance)

        Args:
            other: Another fractal agent

        Returns:
            Resonance strength in range [-1, 1]
        """
        # Phase difference
        delta_phase = self.state.phase - other.state.phase

        # Resonance via cosine (phase alignment)
        resonance = np.cos(delta_phase)

        # Update internal resonance state (absolute value)
        self.state.resonance = abs(resonance)

        return resonance

    def update_energy(self, delta_energy: float, min_energy: float = 0.0, max_energy: float = 1.0) -> None:
        """Update agent's energy level with bounds.

        Args:
            delta_energy: Energy change (positive = gain, negative = loss)
            min_energy: Minimum energy threshold (default: 0.0)
            max_energy: Maximum energy capacity (default: 1.0)
        """
        self.state.energy = np.clip(self.state.energy + delta_energy, min_energy, max_energy)
        self.state.last_update = datetime.now()

    def move(self, delta_position: np.ndarray) -> None:
        """Move agent in phase space.

        Args:
            delta_position: Position change vector (3D)
        """
        self.state.position += delta_position
        self.state.last_update = datetime.now()

    def is_alive(self, energy_threshold: float = 0.0) -> bool:
        """Check if agent has sufficient energy to persist.

        Args:
            energy_threshold: Minimum energy for survival (default: 0.0)

        Returns:
            True if energy > threshold, False otherwise
        """
        return self.state.energy > energy_threshold

    def can_compose(self, resonance_threshold: float = 0.5) -> bool:
        """Check if agent can participate in composition.

        Composition requires sufficient resonance alignment with environment.

        Args:
            resonance_threshold: Minimum resonance for composition (default: 0.5)

        Returns:
            True if resonance ≥ threshold, False otherwise
        """
        return self.state.resonance >= resonance_threshold

    def can_decompose(self, energy_threshold: float = 0.1) -> bool:
        """Check if agent should decompose (burst).

        Decomposition triggered by insufficient energy or critical instability.

        Args:
            energy_threshold: Maximum energy for decomposition trigger (default: 0.1)

        Returns:
            True if energy ≤ threshold (critical state), False otherwise
        """
        return self.state.energy <= energy_threshold

    def remember_pattern(self, pattern_id: str, strength: float) -> None:
        """Store successful pattern in memory.

        Pattern memory persists across composition-decomposition cycles.

        Args:
            pattern_id: Unique pattern identifier
            strength: Pattern strength/success metric (0-1)
        """
        self._pattern_memory[pattern_id] = strength
        self.state.memory = self._pattern_memory.copy()
        self.state.last_update = datetime.now()

    def recall_pattern(self, pattern_id: str) -> Optional[float]:
        """Retrieve pattern from memory.

        Args:
            pattern_id: Pattern identifier to recall

        Returns:
            Pattern strength if found, None otherwise
        """
        return self._pattern_memory.get(pattern_id)

    def get_age(self) -> float:
        """Calculate agent's age in seconds since birth.

        Returns:
            Age in seconds
        """
        return (datetime.now() - self.state.birth_time).total_seconds()

    def to_dict(self) -> Dict:
        """Export agent state as dictionary for serialization.

        Returns:
            Dictionary representation of agent state
        """
        return {
            "agent_id": self.state.agent_id,
            "depth": self.state.depth,
            "energy": float(self.state.energy),
            "phase": float(self.state.phase),
            "position": self.state.position.tolist(),
            "velocity": float(self.state.velocity),
            "resonance": float(self.state.resonance),
            "memory": self.state.memory.copy(),
            "birth_time": self.state.birth_time.isoformat(),
            "last_update": self.state.last_update.isoformat(),
            "parent_id": self.state.parent_id,
            "children_ids": list(self.state.children_ids),
            "cluster_id": self.state.cluster_id,
            "age_seconds": self.get_age(),
            "composition_history": self._composition_history.copy(),
            "decomposition_history": self._decomposition_history.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'FractalAgent':
        """Reconstruct agent from dictionary representation.

        Args:
            data: Dictionary with agent state

        Returns:
            Reconstructed FractalAgent instance
        """
        agent = cls(
            depth=data["depth"],
            energy=data["energy"],
            phase=data["phase"],
            position=np.array(data["position"]),
            agent_id=data["agent_id"],
        )

        agent.state.velocity = data["velocity"]
        agent.state.resonance = data["resonance"]
        agent._pattern_memory = data["memory"].copy()
        agent.state.memory = data["memory"].copy()
        agent.state.birth_time = datetime.fromisoformat(data["birth_time"])
        agent.state.last_update = datetime.fromisoformat(data["last_update"])
        agent.state.parent_id = data.get("parent_id")
        agent.state.children_ids = set(data.get("children_ids", []))
        agent.state.cluster_id = data.get("cluster_id")
        agent._composition_history = data.get("composition_history", []).copy()
        agent._decomposition_history = data.get("decomposition_history", []).copy()

        return agent

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"FractalAgent(id={self.state.agent_id[:8]}..., "
            f"depth={self.state.depth}, "
            f"energy={self.state.energy:.3f}, "
            f"phase={self.state.phase:.3f}, "
            f"resonance={self.state.resonance:.3f})"
        )
