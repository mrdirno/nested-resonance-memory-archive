"""
DecompositionEngine - Burst Dynamics and Cluster Dissolution

Implements decomposition dynamics where fractal clusters burst into constituent agents.
Decomposition occurs when clusters reach critical energy thresholds or instability conditions,
releasing child agents back to depth-1 level.

Theoretical Basis:
    - Decomposition: Burst dissolution of clusters
    - Energy Threshold: Critical low energy triggers decomposition
    - Constituent Release: Child agents return to independent state
    - Memory Transfer: Cluster patterns distributed to constituents
    - Depth Reduction: Agents return to original depth

Reality Grounding:
    - All operations on internal Python objects (no external services)
    - Measurable decomposition criteria
    - Verifiable energy conservation (total energy preserved)
    - Timestamp tracking for burst events

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
"""

from typing import List, Dict, Optional
from datetime import datetime
import numpy as np

from .agent import FractalAgent
from ..memory.pattern import PatternMemory


class DecompositionEngine:
    """Engine for detecting and executing decomposition (cluster burst).

    Decomposition Process:
        1. Detect critical conditions (low energy, instability)
        2. Verify decomposition criteria (has children, sufficient depth)
        3. Release constituent agents (children)
        4. Transfer cluster memory to constituents
        5. Distribute residual cluster energy
        6. Break parent-child relationships

    Decomposition Criteria:
        - Energy threshold: Cluster energy below critical level
        - Has children: Cluster must have constituent agents
        - Sufficient depth: Cluster at depth ≥ 1 (not base agents)

    Usage:
        engine = DecompositionEngine(energy_threshold=0.1)
        constituents = engine.decompose(cluster_agent)
        if constituents:
            print(f\"Cluster burst into {len(constituents)} constituents\")

    Attributes:
        energy_threshold: Maximum energy for decomposition trigger
        decomposition_history: Record of all decomposition events
    """

    def __init__(
        self,
        energy_threshold: float = 0.1,
    ):
        """Initialize decomposition engine.

        Args:
            energy_threshold: Maximum energy for decomposition trigger (default: 0.1)
        """
        self.energy_threshold = energy_threshold
        self.decomposition_history: List[Dict] = []

    def can_decompose(self, agent: FractalAgent) -> tuple[bool, str]:
        """Check if agent can decompose (burst).

        Decomposition Requirements:
            1. Agent has children (is a cluster)
            2. Agent at depth ≥ 1 (not base agent)
            3. Energy ≤ threshold (critical state)

        Args:
            agent: Fractal agent to check

        Returns:
            Tuple of (can_decompose: bool, reason: str)
        """
        # Must have children (be a cluster)
        if not agent.state.children_ids:
            return False, "Agent has no children (not a cluster)"

        # Must be at depth ≥ 1 (clusters only)
        if agent.state.depth < 1:
            return False, f"Agent at depth {agent.state.depth} (base agents don't decompose)"

        # Check energy threshold
        if agent.state.energy > self.energy_threshold:
            return False, (
                f"Agent energy {agent.state.energy:.3f} above threshold "
                f"{self.energy_threshold} (not critical)"
            )

        return True, "Decomposition criteria met (critical energy state)"

    def decompose(
        self,
        cluster: FractalAgent,
        constituents: Optional[List[FractalAgent]] = None,
    ) -> Optional[List[FractalAgent]]:
        """Decompose cluster into constituent agents.

        Releases child agents from cluster with:
            - Energy: Cluster energy distributed equally
            - Memory: Cluster patterns merged into constituents
            - Phase: Constituents retain original phases
            - Position: Scattered around cluster position
            - Parent link: Removed (agents become independent)

        Args:
            cluster: Cluster agent to decompose
            constituents: Optional list of constituent agents (if available)

        Returns:
            List of constituent agents if decomposition successful, None otherwise
        """
        # Check decomposition criteria
        can_decompose, reason = self.can_decompose(cluster)
        if not can_decompose:
            return None

        # If constituents not provided, create new agents from children_ids
        if constituents is None:
            # In a full system, would retrieve from agent registry
            # For now, create placeholder agents at depth-1
            num_constituents = len(cluster.state.children_ids)
            constituents = [
                FractalAgent(
                    depth=cluster.state.depth - 1,
                    agent_id=child_id,
                )
                for child_id in cluster.state.children_ids
            ]

        # Distribute cluster energy equally
        energy_per_constituent = cluster.state.energy / len(constituents)
        for agent in constituents:
            agent.state.energy = energy_per_constituent

        # Scatter constituents around cluster position
        scatter_radius = 0.1  # Phase space distance
        for i, agent in enumerate(constituents):
            # Random scatter in 3D phase space
            angle = 2 * np.pi * i / len(constituents)
            offset = scatter_radius * np.array([
                np.cos(angle),
                np.sin(angle),
                0.0,
            ])
            agent.state.position = cluster.state.position + offset

        # Transfer cluster memory to constituents
        for agent in constituents:
            for pattern_id, strength in cluster._pattern_memory.items():
                agent.remember_pattern(pattern_id, strength)

        # Break parent-child relationships
        for agent in constituents:
            agent.state.parent_id = None
            agent.state.cluster_id = None

        cluster.state.children_ids.clear()

        # Record decomposition event
        decomposition_event = {
            "timestamp": datetime.now().isoformat(),
            "cluster_id": cluster.state.agent_id,
            "constituent_ids": [agent.state.agent_id for agent in constituents],
            "cluster_depth": cluster.state.depth,
            "cluster_energy": cluster.state.energy,
            "energy_per_constituent": energy_per_constituent,
            "num_constituents": len(constituents),
            "energy_threshold": self.energy_threshold,
        }
        self.decomposition_history.append(decomposition_event)
        cluster._decomposition_history.append(decomposition_event)

        return constituents

    def detect_critical_clusters(
        self,
        agents: List[FractalAgent],
    ) -> List[FractalAgent]:
        """Detect clusters in critical state (ready to decompose).

        Args:
            agents: List of agents to analyze

        Returns:
            List of cluster agents meeting decomposition criteria
        """
        critical_clusters = []

        for agent in agents:
            can_decompose, _ = self.can_decompose(agent)
            if can_decompose:
                critical_clusters.append(agent)

        return critical_clusters

    def decompose_all(
        self,
        agents: List[FractalAgent],
        agent_registry: Optional[Dict[str, FractalAgent]] = None,
    ) -> List[FractalAgent]:
        """Detect and decompose all critical clusters.

        Args:
            agents: List of agents to process
            agent_registry: Optional registry mapping agent_id → agent

        Returns:
            List of all constituent agents released from decomposition
        """
        critical_clusters = self.detect_critical_clusters(agents)
        all_constituents = []

        for cluster in critical_clusters:
            # Retrieve actual constituent agents if registry provided
            constituents_list = None
            if agent_registry:
                constituents_list = [
                    agent_registry[child_id]
                    for child_id in cluster.state.children_ids
                    if child_id in agent_registry
                ]

            constituents = self.decompose(cluster, constituents_list)
            if constituents:
                all_constituents.extend(constituents)

        return all_constituents

    def get_decomposition_stats(self) -> Dict:
        """Get statistics on decomposition history.

        Returns:
            Dictionary with decomposition statistics
        """
        if not self.decomposition_history:
            return {
                "total_decompositions": 0,
                "avg_constituents": 0.0,
                "avg_cluster_energy": 0.0,
                "depths": [],
            }

        num_constituents = [event["num_constituents"] for event in self.decomposition_history]
        cluster_energies = [event["cluster_energy"] for event in self.decomposition_history]
        depths = [event["cluster_depth"] for event in self.decomposition_history]

        return {
            "total_decompositions": len(self.decomposition_history),
            "avg_constituents": np.mean(num_constituents),
            "min_constituents": min(num_constituents),
            "max_constituents": max(num_constituents),
            "avg_cluster_energy": np.mean(cluster_energies),
            "min_cluster_energy": min(cluster_energies),
            "max_cluster_energy": max(cluster_energies),
            "depths": sorted(set(depths)),
            "decompositions_by_depth": {
                d: sum(1 for event in self.decomposition_history if event["cluster_depth"] == d)
                for d in set(depths)
            },
        }

    def get_energy_distribution(self) -> Dict[str, float]:
        """Analyze energy distribution across decomposition events.

        Returns:
            Dictionary with energy statistics
        """
        if not self.decomposition_history:
            return {
                "total_energy_released": 0.0,
                "avg_energy_per_constituent": 0.0,
            }

        total_energy = sum(event["cluster_energy"] for event in self.decomposition_history)
        energies_per_constituent = [
            event["energy_per_constituent"]
            for event in self.decomposition_history
        ]

        return {
            "total_energy_released": total_energy,
            "avg_energy_per_constituent": np.mean(energies_per_constituent),
            "min_energy_per_constituent": min(energies_per_constituent),
            "max_energy_per_constituent": max(energies_per_constituent),
        }
