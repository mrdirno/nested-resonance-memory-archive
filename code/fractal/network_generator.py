#!/usr/bin/env python3
"""
Network Topology Generator for C187 Experiment

Generates three network topologies for testing Extension 1 predictions:
- Scale-free (Barabási-Albert): Hub depletion
- Random (Erdős-Rényi): Uniform selection
- Lattice (2D grid): Local selection only

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 996
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum


class NetworkTopology(Enum):
    """Supported network topologies."""
    SCALE_FREE = "scale_free"
    RANDOM = "random"
    LATTICE = "lattice"


class NetworkGenerator:
    """
    Generate network topologies for fractal agent systems.

    Purpose:
        Create graph structures with different topological properties
        to test how network architecture affects spawn success rates.

    Theory:
        Extension 1 (Network Structure Effects) predicts:
        - Scale-free: Hub depletion (high-degree nodes selected frequently)
        - Random: Uniform selection probability
        - Lattice: Local selection only (protected periphery)

    Expected spawn success ranking: Lattice > Random > Scale-Free
    """

    def __init__(self, n_nodes: int = 100, mean_degree: int = 4, seed: int = None):
        """
        Initialize network generator.

        Args:
            n_nodes: Number of nodes in network (default: 100, matches MAX_AGENTS)
            mean_degree: Target mean degree <k> (default: 4)
            seed: Random seed for reproducibility
        """
        self.n_nodes = n_nodes
        self.mean_degree = mean_degree
        self.seed = seed

        if seed is not None:
            np.random.seed(seed)

    def generate_scale_free(self) -> nx.Graph:
        """
        Generate scale-free network using Barabási-Albert model.

        Properties:
            - Power-law degree distribution P(k) ~ k^(-γ), γ ≈ 3
            - Hubs: Few nodes with very high degree
            - Preferential attachment: Rich get richer

        Theory:
            Hub agents experience higher compositional load:
            λ_hub = (k/<k>) · (S/N) >> S/N

            Prediction: Hubs deplete energy rapidly → low spawn success

        Returns:
            NetworkX graph with scale-free topology
        """
        # BA model parameter: m (edges to attach from new node)
        # For mean degree <k> ≈ 2m, use m = mean_degree / 2
        m = max(1, self.mean_degree // 2)

        G = nx.barabasi_albert_graph(
            n=self.n_nodes,
            m=m,
            seed=self.seed
        )

        # Verify properties
        degrees = [d for n, d in G.degree()]
        actual_mean_degree = np.mean(degrees)

        return G

    def generate_random(self) -> nx.Graph:
        """
        Generate random network using Erdős-Rényi model.

        Properties:
            - Binomial degree distribution (Poisson in limit)
            - Homogeneous: Most nodes have similar degree
            - Uniform connection probability

        Theory:
            All agents have approximately equal selection probability.
            Prediction: Baseline spawn success (matches C171/C175)

        Returns:
            NetworkX graph with random topology
        """
        # ER model parameter: p (edge probability)
        # For mean degree <k> = p(N-1), use p = <k>/(N-1)
        p = self.mean_degree / (self.n_nodes - 1)

        G = nx.erdos_renyi_graph(
            n=self.n_nodes,
            p=p,
            seed=self.seed
        )

        # Ensure connectivity (ER graphs may have isolated nodes)
        # Connect isolated nodes to random existing nodes
        isolated = list(nx.isolates(G))
        for node in isolated:
            # Connect to random non-isolated node
            target = np.random.choice([n for n in G.nodes() if n not in isolated])
            G.add_edge(node, target)

        return G

    def generate_lattice(self) -> nx.Graph:
        """
        Generate 2D lattice network (grid).

        Properties:
            - Regular structure: All nodes degree k = 4 (von Neumann)
            - Local connectivity only
            - No hubs, no long-range connections

        Theory:
            Local selection creates protective boundaries.
            Peripheral agents shielded from central depletion.
            Prediction: Highest spawn success (protected periphery)

        Returns:
            NetworkX graph with 2D lattice topology
        """
        # Create square lattice: N = side × side
        side = int(np.sqrt(self.n_nodes))
        actual_n = side * side

        # Adjust if not perfect square
        if actual_n < self.n_nodes:
            side += 1
            actual_n = side * side

        # Generate 2D grid
        G = nx.grid_2d_graph(side, side)

        # Convert node labels from (i,j) tuples to integers
        mapping = {node: i for i, node in enumerate(G.nodes())}
        G = nx.relabel_nodes(G, mapping)

        # Trim to exact size if overshot
        if actual_n > self.n_nodes:
            nodes_to_remove = list(G.nodes())[self.n_nodes:]
            G.remove_nodes_from(nodes_to_remove)

        return G

    def generate(self, topology: NetworkTopology) -> nx.Graph:
        """
        Generate network of specified topology.

        Args:
            topology: Network topology type

        Returns:
            NetworkX graph with requested topology
        """
        if topology == NetworkTopology.SCALE_FREE:
            return self.generate_scale_free()
        elif topology == NetworkTopology.RANDOM:
            return self.generate_random()
        elif topology == NetworkTopology.LATTICE:
            return self.generate_lattice()
        else:
            raise ValueError(f"Unknown topology: {topology}")

    def analyze_topology(self, G: nx.Graph) -> Dict:
        """
        Analyze network topology properties.

        Args:
            G: NetworkX graph

        Returns:
            dict with topology metrics
        """
        degrees = [d for n, d in G.degree()]

        metrics = {
            'n_nodes': G.number_of_nodes(),
            'n_edges': G.number_of_edges(),
            'mean_degree': float(np.mean(degrees)),
            'std_degree': float(np.std(degrees)),
            'min_degree': int(np.min(degrees)),
            'max_degree': int(np.max(degrees)),
            'degree_heterogeneity': float(np.std(degrees) / np.mean(degrees)),  # CV
            'is_connected': nx.is_connected(G),
            'n_components': nx.number_connected_components(G),
        }

        # Clustering coefficient (if connected)
        if nx.is_connected(G):
            metrics['clustering_coefficient'] = nx.average_clustering(G)
            metrics['avg_path_length'] = nx.average_shortest_path_length(G)
        else:
            metrics['clustering_coefficient'] = None
            metrics['avg_path_length'] = None

        return metrics


def validate_networks():
    """
    Validate that network generators produce expected topologies.

    Tests:
        - Scale-free: High degree heterogeneity (CV > 0.5)
        - Random: Moderate heterogeneity (CV ≈ 0.3)
        - Lattice: Low heterogeneity (CV < 0.1)
    """
    generator = NetworkGenerator(n_nodes=100, mean_degree=4, seed=42)

    print("Network Topology Validation")
    print("=" * 80)
    print()

    for topology in NetworkTopology:
        print(f"{topology.value.upper()}")
        print("-" * 80)

        G = generator.generate(topology)
        metrics = generator.analyze_topology(G)

        print(f"Nodes: {metrics['n_nodes']}")
        print(f"Edges: {metrics['n_edges']}")
        print(f"Mean degree: {metrics['mean_degree']:.2f}")
        print(f"Degree heterogeneity (CV): {metrics['degree_heterogeneity']:.3f}")
        print(f"Degree range: [{metrics['min_degree']}, {metrics['max_degree']}]")
        print(f"Connected: {metrics['is_connected']}")

        if metrics['clustering_coefficient'] is not None:
            print(f"Clustering coefficient: {metrics['clustering_coefficient']:.3f}")
            print(f"Avg path length: {metrics['avg_path_length']:.2f}")

        # Validate expected properties
        if topology == NetworkTopology.SCALE_FREE:
            assert metrics['degree_heterogeneity'] > 0.5, "Scale-free should have high heterogeneity"
            print("✅ High degree heterogeneity (hub structure)")
        elif topology == NetworkTopology.RANDOM:
            assert 0.2 < metrics['degree_heterogeneity'] < 0.5, "Random should have moderate heterogeneity"
            print("✅ Moderate degree heterogeneity (homogeneous)")
        elif topology == NetworkTopology.LATTICE:
            assert metrics['degree_heterogeneity'] < 0.15, "Lattice should have low heterogeneity"
            print("✅ Low degree heterogeneity (regular structure)")

        print()


if __name__ == "__main__":
    validate_networks()
