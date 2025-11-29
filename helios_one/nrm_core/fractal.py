"""
NRM Core: Fractal Dynamics
"""
import math
import random
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
from .vector import Vector

@dataclass
class PhaseState:
    """Phase state for Kuramoto dynamics."""
    phases: Vector

    @classmethod
    def random(cls, dimensions: int = 3):
        return cls(Vector([random.uniform(0, 2*math.pi) for _ in range(dimensions)]))

class FractalAgent:
    """
    A fractal agent with energy dynamics and phase coupling.
    """
    def __init__(self, agent_id: str, energy: float = 1.0):
        self.agent_id = agent_id
        self.energy = energy
        # [pi_phase, phi_phase, e_phase]
        self.phase_state = PhaseState.random() 
        self.memory: Dict[str, Any] = {}

    def consume_energy(self, amount: float) -> bool:
        self.energy -= amount
        return self.energy > 0

    def recharge(self, amount: float, cap: float = 2.0):
        self.energy = min(self.energy + amount, cap)

    def coupled_evolve(self, delta_time: float, neighbors: List['FractalAgent'], coupling_strength: float = 1.0):
        """
        Evolve phase state based on neighbors (Kuramoto model).
        """
        if not neighbors:
            return

        # Simple Kuramoto: dtheta/dt = omega + K * sum(sin(theta_j - theta_i))
        # We assume intrinsic frequency omega = 0 for simplicity or add it later
        
        # Convert phases to vector for calculation if needed, 
        # but here we just iterate over dimensions
        
        new_phases = []
        for dim in range(len(self.phase_state.phases)):
            my_phase = self.phase_state.phases[dim]
            interaction = 0.0
            for neighbor in neighbors:
                their_phase = neighbor.phase_state.phases[dim]
                interaction += math.sin(their_phase - my_phase)
            
            interaction /= len(neighbors)
            d_theta = coupling_strength * interaction
            new_phase = (my_phase + d_theta * delta_time) % (2 * math.pi)
            new_phases.append(new_phase)
            
        self.phase_state.phases = Vector(new_phases)

    def compute_coherence(self, other: 'FractalAgent') -> float:
        """
        Compute phase coherence (0.0 to 1.0).
        """
        # Average coherence across dimensions
        total_coherence = 0.0
        dims = len(self.phase_state.phases)
        
        for dim in range(dims):
            diff = abs(self.phase_state.phases[dim] - other.phase_state.phases[dim])
            diff = min(diff, 2*math.pi - diff)
            total_coherence += max(0.0, 1.0 - (diff / math.pi))
            
        return total_coherence / dims

    def __repr__(self):
        return f"FractalAgent({self.agent_id}, E={self.energy:.2f})"

class Population:
    """
    A container for FractalAgents.
    """
    def __init__(self):
        self.agents: Dict[str, FractalAgent] = {}

    def add(self, agent: FractalAgent):
        self.agents[agent.agent_id] = agent

    def remove(self, agent_id: str):
        if agent_id in self.agents:
            del self.agents[agent_id]

    def step(self, delta_time: float = 0.1):
        """
        Run one simulation step.
        """
        agents_list = list(self.agents.values())
        # Naive O(N^2) interaction for now
        for agent in agents_list:
            neighbors = [a for a in agents_list if a != agent]
            agent.coupled_evolve(delta_time, neighbors)
            agent.consume_energy(0.01) # Metabolic cost

        # Remove dead agents
        dead = [aid for aid, a in self.agents.items() if a.energy <= 0]
        for aid in dead:
            self.remove(aid)
