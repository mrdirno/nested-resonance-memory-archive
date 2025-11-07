#!/usr/bin/env python3
"""
Network-Based Parent Selection for C187 Experiment

Implements degree-weighted selection for network topology effects testing.

Replaces uniform random selection with network-aware selection:
- Scale-free: Hubs selected more frequently (degree-proportional)
- Random: Approximately uniform (small degree variance)
- Lattice: Local selection only (neighbors)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 996
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import networkx as nx
import numpy as np
from typing import List, Optional
from fractal.fractal_agent import FractalAgent


class NetworkSelector:
    """
    Network-aware parent selection for fractal agent spawning.

    Theory (Extension 1):
        Network topology affects compositional load via degree-dependent selection:

        P(select agent i) ∝ degree(i)

        High-degree nodes (hubs):
            - Selected more frequently
            - Experience higher λ = (k/<k>) · (S/N)
            - Deplete energy faster
            - Lower spawn success

        Low-degree nodes (periphery):
            - Selected less frequently
            - Protected from excessive compositional load
            - Higher spawn success

    Prediction:
        Spawn success scales with network homogeneity:
        Lattice (regular) > Random (binomial) > Scale-Free (power-law)
    """

    def __init__(self, network: nx.Graph):
        """
        Initialize network-based selector.

        Args:
            network: NetworkX graph defining agent connections
        """
        self.network = network
        self.node_degrees = dict(network.degree())

    def select_parent_degree_weighted(self, agents: List[FractalAgent]) -> Optional[FractalAgent]:
        """
        Select parent with probability proportional to degree.

        Selection probability:
            P(agent_i) = degree(i) / Σ_j degree(j)

        This creates hub depletion effect in scale-free networks.

        Args:
            agents: List of active fractal agents

        Returns:
            Selected parent agent, or None if no agents available
        """
        if len(agents) == 0:
            return None

        # Map agents to network nodes (assume agent_id matches node ID)
        # Extract numeric ID from agent_id (format: "pop0_agent_cycle_count")
        agent_to_node = {}
        for agent in agents:
            # For root agents: "pop0_root" -> node 0 (use population ID)
            # For spawned agents: "pop0_agent_100_5" -> derive from hash or index
            # Simplified: Use agent index in population as node ID
            # This requires agents to have node_id attribute set during creation

            if hasattr(agent, 'node_id'):
                node_id = agent.node_id
                agent_to_node[agent] = node_id
            else:
                # Fallback: assign by index (not ideal but functional)
                agent_to_node[agent] = agents.index(agent)

        # Get degrees for available agents
        degrees = []
        valid_agents = []
        for agent in agents:
            node_id = agent_to_node.get(agent)
            if node_id is not None and node_id in self.node_degrees:
                degrees.append(self.node_degrees[node_id])
                valid_agents.append(agent)

        if len(valid_agents) == 0:
            # Fallback to uniform random if no valid mappings
            return np.random.choice(agents) if len(agents) > 0 else None

        # Normalize to probabilities
        degrees = np.array(degrees, dtype=float)
        probabilities = degrees / np.sum(degrees)

        # Select parent
        parent = np.random.choice(valid_agents, p=probabilities)
        return parent

    def select_parent_uniform(self, agents: List[FractalAgent]) -> Optional[FractalAgent]:
        """
        Select parent uniformly at random (baseline).

        Use this for comparison with network-based selection.

        Args:
            agents: List of active fractal agents

        Returns:
            Selected parent agent, or None if no agents available
        """
        if len(agents) == 0:
            return None

        return np.random.choice(agents)

    def select_parent_local(self, agents: List[FractalAgent], current_agent_id: int) -> Optional[FractalAgent]:
        """
        Select parent from local neighborhood (lattice networks).

        For lattice topologies, restrict selection to neighbors only.
        This creates spatial locality effects.

        Args:
            agents: List of active fractal agents
            current_agent_id: ID of agent initiating spawn (for neighborhood lookup)

        Returns:
            Selected parent from neighborhood, or None if no neighbors available
        """
        if len(agents) == 0:
            return None

        # Get neighbors of current agent
        if current_agent_id in self.network:
            neighbors = list(self.network.neighbors(current_agent_id))
        else:
            neighbors = []

        # Filter agents to only neighbors
        neighbor_agents = [a for a in agents
                          if hasattr(a, 'node_id') and a.node_id in neighbors]

        if len(neighbor_agents) == 0:
            # Fallback to uniform if no neighbors available
            return np.random.choice(agents) if len(agents) > 0 else None

        return np.random.choice(neighbor_agents)

    def get_degree_statistics(self, agents: List[FractalAgent]) -> dict:
        """
        Calculate degree statistics for active agents.

        Useful for tracking hub depletion over time.

        Args:
            agents: List of active fractal agents

        Returns:
            dict with degree statistics
        """
        degrees = []
        for agent in agents:
            if hasattr(agent, 'node_id') and agent.node_id in self.node_degrees:
                degrees.append(self.node_degrees[agent.node_id])

        if len(degrees) == 0:
            return {
                'mean_degree': 0.0,
                'std_degree': 0.0,
                'min_degree': 0,
                'max_degree': 0,
                'n_agents': 0,
            }

        return {
            'mean_degree': float(np.mean(degrees)),
            'std_degree': float(np.std(degrees)),
            'min_degree': int(np.min(degrees)),
            'max_degree': int(np.max(degrees)),
            'n_agents': len(degrees),
        }


class DegreeStratifiedMetrics:
    """
    Track spawn success stratified by node degree.

    Purpose:
        Validate hub depletion hypothesis by measuring spawn success
        separately for high-degree (hub) vs low-degree (peripheral) agents.

    Theory:
        If Extension 1 is correct:
            - High-degree agents: Low spawn success
            - Low-degree agents: High spawn success
    """

    def __init__(self, network: nx.Graph, n_bins: int = 3):
        """
        Initialize stratified metrics tracker.

        Args:
            network: NetworkX graph
            n_bins: Number of degree bins (default: 3 = low/medium/high)
        """
        self.network = network
        self.n_bins = n_bins

        # Calculate degree bins
        degrees = [d for n, d in network.degree()]
        self.degree_percentiles = np.percentile(degrees, np.linspace(0, 100, n_bins + 1))

        # Track spawn attempts and successes per bin
        self.spawn_attempts = {i: 0 for i in range(n_bins)}
        self.spawn_successes = {i: 0 for i in range(n_bins)}

    def get_degree_bin(self, node_id: int) -> int:
        """
        Get degree bin for node.

        Args:
            node_id: Network node ID

        Returns:
            Bin index (0 = low degree, n_bins-1 = high degree)
        """
        if node_id not in self.network:
            return 0  # Default to low bin

        degree = self.network.degree(node_id)

        # Find bin
        for i in range(self.n_bins):
            if degree <= self.degree_percentiles[i + 1]:
                return i

        return self.n_bins - 1  # Highest bin

    def record_spawn_attempt(self, node_id: int, success: bool):
        """
        Record spawn attempt outcome.

        Args:
            node_id: Network node ID of parent agent
            success: Whether spawn succeeded
        """
        bin_idx = self.get_degree_bin(node_id)
        self.spawn_attempts[bin_idx] += 1

        if success:
            self.spawn_successes[bin_idx] += 1

    def get_spawn_success_by_degree(self) -> dict:
        """
        Calculate spawn success rate for each degree bin.

        Returns:
            dict mapping bin index to spawn success rate
        """
        success_rates = {}

        for bin_idx in range(self.n_bins):
            attempts = self.spawn_attempts[bin_idx]
            successes = self.spawn_successes[bin_idx]

            if attempts > 0:
                success_rates[bin_idx] = successes / attempts
            else:
                success_rates[bin_idx] = 0.0

        return success_rates

    def get_results(self) -> dict:
        """
        Get comprehensive stratified results.

        Returns:
            dict with degree bins and spawn success rates
        """
        success_rates = self.get_spawn_success_by_degree()

        return {
            'degree_bins': {
                i: {
                    'min_degree': float(self.degree_percentiles[i]),
                    'max_degree': float(self.degree_percentiles[i + 1]),
                    'spawn_attempts': self.spawn_attempts[i],
                    'spawn_successes': self.spawn_successes[i],
                    'spawn_success_rate': success_rates[i],
                }
                for i in range(self.n_bins)
            },
            'overall': {
                'total_attempts': sum(self.spawn_attempts.values()),
                'total_successes': sum(self.spawn_successes.values()),
                'overall_success_rate': (
                    sum(self.spawn_successes.values()) / sum(self.spawn_attempts.values())
                    if sum(self.spawn_attempts.values()) > 0 else 0.0
                ),
            }
        }


if __name__ == "__main__":
    # Test degree-weighted selection
    print("Network Selection Test")
    print("=" * 80)

    # Create test network
    from fractal.network_generator import NetworkGenerator, NetworkTopology

    generator = NetworkGenerator(n_nodes=100, mean_degree=4, seed=42)
    G = generator.generate(NetworkTopology.SCALE_FREE)

    print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print()

    # Initialize selector
    selector = NetworkSelector(G)

    # Simulate selection frequency
    print("Degree-Weighted Selection Frequency")
    print("-" * 80)

    # Create mock agents (simplified for testing)
    class MockAgent:
        """Lightweight mock agent for network selection testing."""

        def __init__(self, node_id):
            """Initialize mock agent with node ID."""
            self.agent_id = f"agent_{node_id}"
            self.node_id = node_id

    agents = [MockAgent(i) for i in range(100)]

    # Run selection trials
    n_trials = 10000
    selection_counts = {i: 0 for i in range(100)}

    for _ in range(n_trials):
        parent = selector.select_parent_degree_weighted(agents)
        if parent:
            selection_counts[parent.node_id] += 1

    # Analyze correlation between degree and selection frequency
    degrees = [G.degree(i) for i in range(100)]
    frequencies = [selection_counts[i] / n_trials for i in range(100)]

    # Pearson correlation
    corr = np.corrcoef(degrees, frequencies)[0, 1]

    print(f"Trials: {n_trials}")
    print(f"Correlation (degree, selection frequency): {corr:.3f}")

    if corr > 0.9:
        print("✅ Strong positive correlation (degree-weighted selection working)")
    else:
        print("⚠️  Weak correlation (check implementation)")

    print()

    # Test stratified metrics
    print("Degree-Stratified Metrics Test")
    print("-" * 80)

    metrics = DegreeStratifiedMetrics(G, n_bins=3)

    # Simulate spawn attempts with degree-dependent success
    for node_id in range(100):
        degree = G.degree(node_id)

        # Simulate: lower success for high-degree nodes
        attempts = 10
        success_prob = max(0.5, 1.0 - (degree / 50))  # Mock relationship

        for _ in range(attempts):
            success = np.random.random() < success_prob
            metrics.record_spawn_attempt(node_id, success)

    results = metrics.get_results()

    for bin_idx in range(3):
        bin_data = results['degree_bins'][bin_idx]
        print(f"Bin {bin_idx} (degree {bin_data['min_degree']:.0f}-{bin_data['max_degree']:.0f}):")
        print(f"  Attempts: {bin_data['spawn_attempts']}")
        print(f"  Success rate: {bin_data['spawn_success_rate']:.2%}")

    print()
    print(f"Overall success rate: {results['overall']['overall_success_rate']:.2%}")
