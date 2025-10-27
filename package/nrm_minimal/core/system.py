#!/usr/bin/env python3
"""
Minimal NRM System Implementation

Population-level dynamics with composition-decomposition cycles.
Reality-grounded system metrics via psutil.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
import psutil
from typing import List, Dict, Tuple
from .agent import FractalAgent


class NRMSystem:
    """Minimal NRM system with composition-decomposition dynamics."""

    def __init__(self,
                 initial_population: int = 100,
                 spawn_frequency: float = 0.02,
                 resonance_threshold: float = 0.80,
                 energy_threshold: float = 40.0,
                 max_composition_depth: int = 3):
        """Initialize NRM system.

        Args:
            initial_population: Starting number of agents
            spawn_frequency: Probability of spawning new agent per cycle
            resonance_threshold: Minimum resonance for composition
            energy_threshold: Minimum energy for composition
            max_composition_depth: Maximum composition hierarchy depth
        """
        self.spawn_frequency = spawn_frequency
        self.resonance_threshold = resonance_threshold
        self.energy_threshold = energy_threshold
        self.max_composition_depth = max_composition_depth

        # Initialize population
        self.agents: Dict[int, FractalAgent] = {}
        self.next_id = 0
        for _ in range(initial_population):
            self._spawn_agent(depth=1)

        # Metrics tracking
        self.cycle = 0
        self.composition_events = 0
        self.decomposition_events = 0

    def _spawn_agent(self, depth: int = 1,
                    parent_id: int = None) -> FractalAgent:
        """Spawn new agent.

        Args:
            depth: Agent composition depth
            parent_id: Parent agent ID (for composed agents)

        Returns:
            Newly created agent
        """
        agent = FractalAgent(self.next_id, depth)
        agent.parent_id = parent_id
        self.agents[self.next_id] = agent
        self.next_id += 1
        return agent

    def _get_system_metrics(self) -> Tuple[float, float]:
        """Get current system CPU and memory usage (reality grounding).

        Returns:
            Tuple of (cpu_percent, memory_percent)
        """
        cpu = psutil.cpu_percent(interval=0.01)
        memory = psutil.virtual_memory().percent
        return cpu, memory

    def _update_resonances(self) -> None:
        """Update resonance for all agents based on neighbors."""
        agent_list = list(self.agents.values())

        for agent in agent_list:
            if not agent.alive:
                continue

            # Get neighbors (simplified: random sample)
            n_neighbors = min(5, len(agent_list) - 1)
            neighbors = np.random.choice(
                [a for a in agent_list if a.id != agent.id],
                size=n_neighbors,
                replace=False
            )
            agent.update_resonance(list(neighbors))

    def _attempt_composition(self) -> int:
        """Attempt to compose high-resonance agents.

        Returns:
            Number of composition events
        """
        events = 0

        # Find agents eligible for composition
        eligible = [
            a for a in self.agents.values()
            if a.can_compose(self.resonance_threshold, self.energy_threshold)
            and a.depth < self.max_composition_depth
        ]

        # Group agents by similar energy (clustering)
        if len(eligible) >= 2:
            # Sort by energy
            eligible.sort(key=lambda a: a.energy)

            # Compose adjacent pairs
            for i in range(0, len(eligible) - 1, 2):
                a1, a2 = eligible[i], eligible[i+1]

                # Create composite agent
                composite = self._spawn_agent(
                    depth=max(a1.depth, a2.depth) + 1
                )
                composite.energy = (a1.energy + a2.energy) / 2
                composite.children_ids = [a1.id, a2.id]

                # Mark children as composed (remove from active)
                a1.alive = False
                a2.alive = False

                events += 1

        return events

    def _attempt_decomposition(self) -> int:
        """Attempt to decompose low-energy agents.

        Returns:
            Number of decomposition events
        """
        events = 0

        # Find composite agents with low energy
        composites = [
            a for a in self.agents.values()
            if a.alive and a.depth > 1 and a.energy < 30.0
        ]

        for composite in composites:
            # Decompose: spawn children
            for _ in range(2):
                child = self._spawn_agent(depth=composite.depth - 1)
                child.energy = composite.energy / 2

            # Remove composite
            composite.alive = False
            events += 1

        return events

    def _spawn_new_agents(self) -> int:
        """Spawn new base-level agents based on frequency.

        Returns:
            Number of agents spawned
        """
        spawned = 0
        if np.random.random() < self.spawn_frequency:
            self._spawn_agent(depth=1)
            spawned = 1
        return spawned

    def _remove_dead_agents(self) -> int:
        """Remove dead agents from population.

        Returns:
            Number of agents removed
        """
        alive_ids = [aid for aid, a in self.agents.items() if a.alive]
        dead_count = len(self.agents) - len(alive_ids)
        self.agents = {aid: self.agents[aid] for aid in alive_ids}
        return dead_count

    def step(self) -> Dict:
        """Execute one simulation cycle.

        Returns:
            Dictionary of cycle metrics
        """
        # Get system metrics (reality grounding)
        cpu, memory = self._get_system_metrics()

        # Update all agents
        for agent in self.agents.values():
            if agent.alive:
                agent.update_energy(cpu, memory)

        # Update resonances
        self._update_resonances()

        # Composition-decomposition dynamics
        comp_events = self._attempt_composition()
        decomp_events = self._attempt_decomposition()

        self.composition_events += comp_events
        self.decomposition_events += decomp_events

        # Spawn new agents
        self._spawn_new_agents()

        # Remove dead agents
        self._remove_dead_agents()

        # Track metrics
        self.cycle += 1

        alive_agents = [a for a in self.agents.values() if a.alive]
        metrics = {
            'cycle': self.cycle,
            'population': len(alive_agents),
            'mean_energy': np.mean([a.energy for a in alive_agents]) if alive_agents else 0,
            'mean_resonance': np.mean([a.resonance for a in alive_agents]) if alive_agents else 0,
            'composition_events': comp_events,
            'decomposition_events': decomp_events,
            'system_cpu': cpu,
            'system_memory': memory
        }

        return metrics

    def run(self, cycles: int = 1000) -> List[Dict]:
        """Run simulation for specified cycles.

        Args:
            cycles: Number of cycles to execute

        Returns:
            List of per-cycle metrics
        """
        results = []
        for _ in range(cycles):
            metrics = self.step()
            results.append(metrics)
        return results
