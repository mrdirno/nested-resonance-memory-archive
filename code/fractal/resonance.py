"""
ResonanceDetector - Phase Alignment Analysis for Composition

Provides utilities for detecting resonance between fractal agents via phase alignment.
Resonance detection identifies compatible agents for composition (cluster formation).

Theoretical Basis:
    - Phase Coherence: Agents with aligned phases resonate constructively
    - Resonance Strength: R = cos(Δφ) where Δφ = phase difference
    - Resonance Networks: Graph analysis of pairwise resonance
    - Composition Readiness: Identify clusters from resonance structure

Reality Grounding:
    - All operations on internal agent objects (no external services)
    - Measurable phase differences and resonance values
    - Verifiable cluster detection via graph algorithms

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
"""

from typing import List, Dict, Set, Tuple, Optional
import numpy as np
import networkx as nx

from .agent import FractalAgent


class ResonanceDetector:
    """Detector for resonance alignment between fractal agents.

    Analyzes phase coherence to identify composition-ready agent groups.

    Resonance Analysis:
        - Pairwise resonance: R(i,j) = cos(φ_i - φ_j)
        - Resonance network: Graph with agents as nodes, R as edges
        - Cluster detection: Connected components with R ≥ threshold
        - Composition readiness: Clusters meeting size/energy criteria

    Usage:
        detector = ResonanceDetector(threshold=0.7)
        resonance = detector.calculate_resonance(agent1, agent2)
        clusters = detector.detect_resonance_clusters(agent_list)
        network = detector.build_resonance_network(agent_list)

    Attributes:
        threshold: Minimum resonance for composition (default: 0.7)
        use_absolute: Use |R| for resonance (ignore phase sign)
    """

    def __init__(
        self,
        threshold: float = 0.7,
        use_absolute: bool = True,
    ):
        """Initialize resonance detector.

        Args:
            threshold: Minimum resonance for composition (default: 0.7)
            use_absolute: Use absolute value of resonance (default: True)
        """
        self.threshold = threshold
        self.use_absolute = use_absolute

    def calculate_resonance(
        self,
        agent1: FractalAgent,
        agent2: FractalAgent,
    ) -> float:
        """Calculate resonance between two agents.

        Resonance formula: R = cos(Δφ) where Δφ = φ₁ - φ₂

        Args:
            agent1: First fractal agent
            agent2: Second fractal agent

        Returns:
            Resonance strength in range [-1, 1] or [0, 1] if use_absolute
        """
        # Phase difference
        delta_phase = agent1.state.phase - agent2.state.phase

        # Resonance via cosine
        resonance = np.cos(delta_phase)

        # Optionally use absolute value
        if self.use_absolute:
            resonance = abs(resonance)

        return resonance

    def calculate_resonance_matrix(
        self,
        agents: List[FractalAgent],
    ) -> np.ndarray:
        """Calculate pairwise resonance matrix for agent list.

        Matrix element R[i,j] = resonance between agents[i] and agents[j]

        Args:
            agents: List of fractal agents

        Returns:
            N×N resonance matrix
        """
        n = len(agents)
        matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    matrix[i, j] = 1.0  # Self-resonance
                else:
                    resonance = self.calculate_resonance(agents[i], agents[j])
                    matrix[i, j] = resonance
                    matrix[j, i] = resonance  # Symmetric

        return matrix

    def build_resonance_network(
        self,
        agents: List[FractalAgent],
    ) -> nx.Graph:
        """Build resonance network as graph.

        Nodes: Agents
        Edges: Pairs with resonance ≥ threshold
        Edge weights: Resonance values

        Args:
            agents: List of fractal agents

        Returns:
            NetworkX graph with resonance edges
        """
        # Create graph
        G = nx.Graph()

        # Add nodes (agents)
        for agent in agents:
            G.add_node(
                agent.state.agent_id,
                agent=agent,
                depth=agent.state.depth,
                energy=agent.state.energy,
                phase=agent.state.phase,
            )

        # Add edges (resonance connections)
        for i, agent_i in enumerate(agents):
            for j, agent_j in enumerate(agents):
                if i >= j:
                    continue

                resonance = self.calculate_resonance(agent_i, agent_j)

                if resonance >= self.threshold:
                    G.add_edge(
                        agent_i.state.agent_id,
                        agent_j.state.agent_id,
                        resonance=resonance,
                    )

        return G

    def detect_resonance_clusters(
        self,
        agents: List[FractalAgent],
        min_size: int = 2,
        max_size: Optional[int] = None,
    ) -> List[List[FractalAgent]]:
        """Detect clusters via resonance network analysis.

        Uses connected components in resonance graph.

        Args:
            agents: List of agents to analyze
            min_size: Minimum cluster size (default: 2)
            max_size: Maximum cluster size (default: None)

        Returns:
            List of agent groups forming resonance clusters
        """
        # Build resonance network
        G = self.build_resonance_network(agents)

        # Find connected components
        components = list(nx.connected_components(G))

        # Filter by size constraints
        clusters = []
        for component in components:
            if len(component) >= min_size:
                if max_size is None or len(component) <= max_size:
                    # Convert node IDs back to agents
                    cluster_agents = [
                        G.nodes[node_id]["agent"]
                        for node_id in component
                    ]
                    clusters.append(cluster_agents)

        return clusters

    def get_resonance_stats(
        self,
        agents: List[FractalAgent],
    ) -> Dict:
        """Get resonance network statistics.

        Args:
            agents: List of agents to analyze

        Returns:
            Dictionary with network statistics
        """
        if len(agents) < 2:
            return {
                "num_agents": len(agents),
                "num_edges": 0,
                "avg_resonance": 0.0,
                "density": 0.0,
                "num_components": len(agents),
            }

        # Build network
        G = self.build_resonance_network(agents)

        # Calculate statistics
        num_edges = G.number_of_edges()
        resonance_values = [G[u][v]["resonance"] for u, v in G.edges()]
        avg_resonance = np.mean(resonance_values) if resonance_values else 0.0
        density = nx.density(G)
        num_components = nx.number_connected_components(G)

        return {
            "num_agents": len(agents),
            "num_edges": num_edges,
            "avg_resonance": avg_resonance,
            "min_resonance": min(resonance_values) if resonance_values else 0.0,
            "max_resonance": max(resonance_values) if resonance_values else 0.0,
            "density": density,
            "num_components": num_components,
            "avg_component_size": len(agents) / num_components if num_components > 0 else 0.0,
        }

    def find_maximum_clique(
        self,
        agents: List[FractalAgent],
    ) -> List[FractalAgent]:
        """Find maximum clique in resonance network.

        A clique is a fully connected subgraph (all pairs resonate).

        Args:
            agents: List of agents to analyze

        Returns:
            Largest clique of mutually resonating agents
        """
        if len(agents) < 2:
            return agents

        # Build network
        G = self.build_resonance_network(agents)

        # Find maximum clique
        try:
            clique_nodes = nx.approximation.max_clique(G)
            clique_agents = [
                G.nodes[node_id]["agent"]
                for node_id in clique_nodes
            ]
            return clique_agents
        except:
            # If algorithm fails, return empty list
            return []

    def calculate_average_phase(
        self,
        agents: List[FractalAgent],
    ) -> float:
        """Calculate average phase of agent group.

        Handles circular phase values correctly (0-2π wrapping).

        Args:
            agents: List of agents

        Returns:
            Average phase in radians (0-2π)
        """
        if not agents:
            return 0.0

        # Convert phases to unit vectors
        phases = np.array([agent.state.phase for agent in agents])
        x = np.mean(np.cos(phases))
        y = np.mean(np.sin(phases))

        # Convert back to angle
        avg_phase = np.arctan2(y, x)

        # Ensure positive angle (0-2π)
        if avg_phase < 0:
            avg_phase += 2 * np.pi

        return avg_phase

    def calculate_phase_coherence(
        self,
        agents: List[FractalAgent],
    ) -> float:
        """Calculate phase coherence of agent group.

        Coherence measures how aligned phases are (0=random, 1=perfect alignment).

        Args:
            agents: List of agents

        Returns:
            Phase coherence in range [0, 1]
        """
        if len(agents) < 2:
            return 1.0

        # Calculate order parameter
        phases = np.array([agent.state.phase for agent in agents])
        x = np.mean(np.cos(phases))
        y = np.mean(np.sin(phases))

        # Coherence = magnitude of order parameter
        coherence = np.sqrt(x**2 + y**2)

        return coherence
