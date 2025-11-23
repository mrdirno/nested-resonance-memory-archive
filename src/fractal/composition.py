"""
CompositionEngine - Cluster Formation via Resonance Alignment

Implements composition dynamics where fractal agents cluster through resonance alignment.
Clusters form when agents achieve sufficient phase coherence, creating emergent higher-level
agents at depth+1.

Theoretical Basis:
    - Composition: Cluster formation through resonance
    - Resonance Threshold: Minimum phase alignment for clustering
    - Energy Pooling: Cluster energy = sum of constituent energies
    - Emergent Depth: Clusters exist at depth+1 from constituents
    - Memory Inheritance: Successful patterns transfer to cluster

Reality Grounding:
    - All operations on internal Python objects (no external services)
    - Measurable cluster formation criteria
    - Verifiable energy conservation
    - Timestamp tracking for cluster lifecycle

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
"""

from typing import List, Set, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

from .agent import FractalAgent


class CompositionEngine:
    """Engine for detecting and executing composition (cluster formation).

    Composition Process:
        1. Detect resonance alignment between agents (phase coherence)
        2. Verify composition criteria (energy, resonance thresholds)
        3. Create cluster agent at depth+1
        4. Transfer energy and memory to cluster
        5. Link constituents to cluster (parent-child relationships)

    Composition Criteria:
        - Resonance threshold: All pairs must have R ≥ threshold
        - Energy threshold: All agents must have E ≥ minimum
        - Depth consistency: All constituents at same depth
        - No existing cluster: Agents not already clustered

    Usage:
        engine = CompositionEngine(resonance_threshold=0.7)
        cluster = engine.compose([agent1, agent2, agent3])
        if cluster:
            print(f\"Cluster formed: {cluster}\")

    Attributes:
        resonance_threshold: Minimum resonance for composition
        energy_threshold: Minimum energy per agent for composition
        composition_history: Record of all composition events
    """

    def __init__(
        self,
        resonance_threshold: float = 0.7,
        energy_threshold: float = 0.5,
    ):
        """Initialize composition engine.

        Args:
            resonance_threshold: Minimum resonance for composition (default: 0.7)
            energy_threshold: Minimum energy per agent (default: 0.5)
        """
        self.resonance_threshold = resonance_threshold
        self.energy_threshold = energy_threshold
        self.composition_history: List[Dict] = []

    def can_compose(self, agents: List[FractalAgent]) -> Tuple[bool, str]:
        """Check if agents can compose into cluster.

        Composition Requirements:
            1. At least 2 agents
            2. All agents at same depth
            3. All agents have sufficient energy
            4. All pairs have sufficient resonance
            5. No agent already in cluster

        Args:
            agents: List of fractal agents to check

        Returns:
            Tuple of (can_compose: bool, reason: str)
        """
        # Require at least 2 agents
        if len(agents) < 2:
            return False, "Need at least 2 agents for composition"

        # Check depth consistency
        depths = [agent.state.depth for agent in agents]
        if len(set(depths)) > 1:
            return False, f"Agents at different depths: {set(depths)}"

        # Check energy threshold
        for agent in agents:
            if agent.state.energy < self.energy_threshold:
                return False, f"Agent {agent.state.agent_id[:8]} has insufficient energy: {agent.state.energy:.3f}"

        # Check no existing cluster membership
        for agent in agents:
            if agent.state.cluster_id is not None:
                return False, f"Agent {agent.state.agent_id[:8]} already in cluster {agent.state.cluster_id[:8]}"

        # Check pairwise resonance
        for i, agent_i in enumerate(agents):
            for j, agent_j in enumerate(agents):
                if i >= j:
                    continue
                resonance = abs(agent_i.calculate_resonance(agent_j))
                if resonance < self.resonance_threshold:
                    return False, (
                        f"Insufficient resonance between agents "
                        f"{agent_i.state.agent_id[:8]} and {agent_j.state.agent_id[:8]}: "
                        f"{resonance:.3f} < {self.resonance_threshold}"
                    )

        return True, "Composition criteria met"

    def compose(self, agents: List[FractalAgent]) -> Optional[FractalAgent]:
        """Compose agents into cluster.

        Creates new cluster agent at depth+1 with:
            - Energy: Sum of constituent energies
            - Phase: Average of constituent phases
            - Position: Center of mass of constituents
            - Memory: Union of constituent pattern memories
            - Children: Links to all constituents

        Args:
            agents: List of fractal agents to compose

        Returns:
            Cluster agent if composition successful, None otherwise
        """
        # Check composition criteria
        can_compose, reason = self.can_compose(agents)
        if not can_compose:
            return None

        # Cluster properties
        depth = agents[0].state.depth + 1  # Emergent depth
        total_energy = sum(agent.state.energy for agent in agents)
        avg_phase = np.mean([agent.state.phase for agent in agents])
        center_of_mass = np.mean([agent.state.position for agent in agents], axis=0)

        # Create cluster agent
        cluster = FractalAgent(
            depth=depth,
            energy=total_energy,
            phase=avg_phase,
            position=center_of_mass,
        )

        # Establish parent-child relationships
        cluster.state.children_ids = {agent.state.agent_id for agent in agents}
        for agent in agents:
            agent.state.parent_id = cluster.state.agent_id
            agent.state.cluster_id = cluster.state.agent_id

        # Merge pattern memories (union of successful patterns)
        merged_memory: Dict[str, float] = {}
        for agent in agents:
            for pattern_id, strength in agent._pattern_memory.items():
                if pattern_id not in merged_memory:
                    merged_memory[pattern_id] = strength
                else:
                    # Take maximum strength across constituents
                    merged_memory[pattern_id] = max(merged_memory[pattern_id], strength)

        cluster._pattern_memory = merged_memory
        cluster.state.memory = merged_memory.copy()

        # Record composition event
        composition_event = {
            "timestamp": datetime.now().isoformat(),
            "cluster_id": cluster.state.agent_id,
            "constituent_ids": [agent.state.agent_id for agent in agents],
            "depth": depth,
            "energy": total_energy,
            "resonance_threshold": self.resonance_threshold,
            "num_constituents": len(agents),
        }
        self.composition_history.append(composition_event)
        cluster._composition_history.append(composition_event)

        return cluster

    def detect_clusters(
        self,
        agents: List[FractalAgent],
        min_cluster_size: int = 2,
        max_cluster_size: Optional[int] = None,
    ) -> List[List[FractalAgent]]:
        """Detect potential clusters via resonance network analysis.

        Uses greedy clustering algorithm:
            1. Compute pairwise resonance matrix
            2. Identify connected components (resonance ≥ threshold)
            3. Filter by size constraints
            4. Return cluster candidates

        Args:
            agents: List of agents to analyze
            min_cluster_size: Minimum agents per cluster (default: 2)
            max_cluster_size: Maximum agents per cluster (default: None)

        Returns:
            List of agent groups forming potential clusters
        """
        if len(agents) < min_cluster_size:
            return []

        # Filter to agents at same depth
        depth_groups: Dict[int, List[FractalAgent]] = {}
        for agent in agents:
            depth = agent.state.depth
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(agent)

        all_clusters = []

        # Cluster within each depth level
        for depth, depth_agents in depth_groups.items():
            if len(depth_agents) < min_cluster_size:
                continue

            # Compute resonance matrix
            n = len(depth_agents)
            resonance_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(i + 1, n):
                    resonance = abs(depth_agents[i].calculate_resonance(depth_agents[j]))
                    resonance_matrix[i, j] = resonance
                    resonance_matrix[j, i] = resonance

            # Find connected components (greedy)
            visited = set()
            for i in range(n):
                if i in visited:
                    continue

                cluster = [depth_agents[i]]
                visited.add(i)

                # Add connected agents
                for j in range(n):
                    if j in visited:
                        continue
                    # Check if j resonates with all current cluster members
                    if all(resonance_matrix[cluster_idx, j] >= self.resonance_threshold
                           for cluster_idx, _ in enumerate(cluster)):
                        cluster.append(depth_agents[j])
                        visited.add(j)

                # Filter by size constraints
                if len(cluster) >= min_cluster_size:
                    if max_cluster_size is None or len(cluster) <= max_cluster_size:
                        all_clusters.append(cluster)

        return all_clusters

    def compose_all(self, agents: List[FractalAgent]) -> List[FractalAgent]:
        """Detect and compose all possible clusters from agent list.

        Args:
            agents: List of agents to process

        Returns:
            List of cluster agents created
        """
        cluster_candidates = self.detect_clusters(agents)
        clusters = []

        for candidate in cluster_candidates:
            cluster = self.compose(candidate)
            if cluster:
                clusters.append(cluster)

        return clusters

    def get_composition_stats(self) -> Dict:
        """Get statistics on composition history.

        Returns:
            Dictionary with composition statistics
        """
        if not self.composition_history:
            return {
                "total_compositions": 0,
                "avg_cluster_size": 0.0,
                "avg_cluster_energy": 0.0,
                "depths": [],
            }

        cluster_sizes = [event["num_constituents"] for event in self.composition_history]
        cluster_energies = [event["energy"] for event in self.composition_history]
        depths = [event["depth"] for event in self.composition_history]

        return {
            "total_compositions": len(self.composition_history),
            "avg_cluster_size": np.mean(cluster_sizes),
            "min_cluster_size": min(cluster_sizes),
            "max_cluster_size": max(cluster_sizes),
            "avg_cluster_energy": np.mean(cluster_energies),
            "min_cluster_energy": min(cluster_energies),
            "max_cluster_energy": max(cluster_energies),
            "depths": sorted(set(depths)),
            "compositions_by_depth": {
                d: sum(1 for event in self.composition_history if event["depth"] == d)
                for d in set(depths)
            },
        }
