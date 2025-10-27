#!/usr/bin/env python3
"""
Minimal NRM Agent Implementation

Simplified fractal agent with depth, resonance, and energy states.
Reality-grounded through system metrics (CPU, memory).

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
from typing import Optional


class FractalAgent:
    """Minimal fractal agent with composition-decomposition capability."""

    def __init__(self, agent_id: int, depth: int = 1):
        """Initialize agent.

        Args:
            agent_id: Unique agent identifier
            depth: Composition depth (1=individual, 2+=composite)
        """
        self.id = agent_id
        self.depth = depth
        self.energy = 50.0  # Initial energy
        self.resonance = 0.0  # Phase alignment
        self.alive = True
        self.parent_id: Optional[int] = None
        self.children_ids: list[int] = []

    def update_resonance(self, neighbors: list['FractalAgent']) -> None:
        """Update resonance based on neighbor alignment.

        Args:
            neighbors: List of neighboring agents
        """
        if not neighbors:
            self.resonance = 0.0
            return

        # Phase alignment measure (simplified)
        energy_diffs = [abs(self.energy - n.energy) for n in neighbors]
        mean_diff = np.mean(energy_diffs)

        # Resonance inversely proportional to energy difference
        self.resonance = 1.0 / (1.0 + mean_diff / 10.0)

    def update_energy(self, system_cpu: float, system_memory: float,
                     recharge_rate: float = 1.0) -> None:
        """Update energy based on system metrics (reality grounding).

        Args:
            system_cpu: Current CPU usage (0-100%)
            system_memory: Current memory usage (0-100%)
            recharge_rate: Energy recharge multiplier
        """
        # Energy recharge coupled to system availability
        cpu_factor = (100.0 - system_cpu) / 100.0
        memory_factor = (100.0 - system_memory) / 100.0

        # Recharge energy (reality-grounded)
        recharge = recharge_rate * cpu_factor * memory_factor
        self.energy = min(100.0, self.energy + recharge)

        # Energy decay
        self.energy -= 0.5

        # Death if energy depleted
        if self.energy <= 0:
            self.alive = False

    def can_compose(self, resonance_threshold: float,
                    energy_threshold: float) -> bool:
        """Check if agent can participate in composition.

        Args:
            resonance_threshold: Minimum resonance required
            energy_threshold: Minimum energy required

        Returns:
            True if agent meets composition criteria
        """
        return (self.alive and
                self.resonance >= resonance_threshold and
                self.energy >= energy_threshold)

    def __repr__(self) -> str:
        return (f"Agent({self.id}, depth={self.depth}, "
                f"E={self.energy:.1f}, R={self.resonance:.2f})")
