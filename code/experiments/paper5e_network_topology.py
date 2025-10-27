#!/usr/bin/env python3
"""
Paper 5E Experimental Framework: Network Topology Effects on NRM Emergence

Research Question: How does network topology affect NRM emergent patterns?

Topology Types Tested:
1. Fully connected (baseline): Every agent connects to every other agent
2. Random (Erdős-Rényi): Edges added randomly with probability p
3. Small-world (Watts-Strogatz): Ring lattice with rewiring probability β
4. Scale-free (Barabási-Albert): Preferential attachment with m edges per node
5. Regular lattice (Grid): 2D grid with periodic boundary conditions

Experimental Design:
- Fixed parameters: N=100, frequency=2.5 Hz, cycles=5000
- Topology variations: 5 types × multiple configurations
- Seeds: 5 replications per configuration
- Total conditions: 55 experiments (~55 minutes runtime)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import networkx as nx
import numpy as np


class NetworkTopologyConfig:
    """Generate experimental conditions for network topology study"""

    def __init__(self):
        self.base_population = 100
        self.base_frequency = 2.5  # Hz (known stable regime from C171/C175)
        self.cycles = 5000
        self.sampling_interval = 100  # Sample every 100 cycles (50 snapshots)
        self.seeds = [42, 123, 456, 789, 101]  # 5 replications per topology

    def generate_experiment_conditions(self) -> List[Dict]:
        """Generate all experimental conditions for topology study"""
        conditions = []

        # 1. Fully connected (baseline) - 1 topology × 5 seeds = 5 experiments
        for seed in self.seeds:
            conditions.append({
                "experiment_id": f"TOPOLOGY_FULLY_CONNECTED_SEED{seed}",
                "topology_type": "fully_connected",
                "population": self.base_population,
                "frequency": self.base_frequency,
                "cycles": self.cycles,
                "seed": seed,
                "configuration": "BASELINE",
                "topology_params": {}
            })

        # 2. Random (Erdős-Rényi) - 3 configurations × 5 seeds = 15 experiments
        connection_probabilities = [0.1, 0.3, 0.5]  # 10%, 30%, 50% connectivity
        for p in connection_probabilities:
            for seed in self.seeds:
                conditions.append({
                    "experiment_id": f"TOPOLOGY_RANDOM_P{p:.1f}_SEED{seed}",
                    "topology_type": "random",
                    "population": self.base_population,
                    "frequency": self.base_frequency,
                    "cycles": self.cycles,
                    "seed": seed,
                    "configuration": "BASELINE",
                    "topology_params": {"p": p}
                })

        # 3. Small-world (Watts-Strogatz) - 3 configurations × 5 seeds = 15 experiments
        k_neighbors = 6  # Each node connected to 6 nearest neighbors
        rewiring_probs = [0.01, 0.1, 0.5]  # Low, medium, high rewiring
        for beta in rewiring_probs:
            for seed in self.seeds:
                conditions.append({
                    "experiment_id": f"TOPOLOGY_SMALL_WORLD_K{k_neighbors}_BETA{beta:.2f}_SEED{seed}",
                    "topology_type": "small_world",
                    "population": self.base_population,
                    "frequency": self.base_frequency,
                    "cycles": self.cycles,
                    "seed": seed,
                    "configuration": "BASELINE",
                    "topology_params": {"k": k_neighbors, "beta": beta}
                })

        # 4. Scale-free (Barabási-Albert) - 3 configurations × 5 seeds = 15 experiments
        edges_per_node = [2, 4, 6]  # Number of edges to attach per new node
        for m in edges_per_node:
            for seed in self.seeds:
                conditions.append({
                    "experiment_id": f"TOPOLOGY_SCALE_FREE_M{m}_SEED{seed}",
                    "topology_type": "scale_free",
                    "population": self.base_population,
                    "frequency": self.base_frequency,
                    "cycles": self.cycles,
                    "seed": seed,
                    "configuration": "BASELINE",
                    "topology_params": {"m": m}
                })

        # 5. Regular lattice (Grid) - 1 topology × 5 seeds = 5 experiments
        grid_size = 10  # 10×10 grid = 100 nodes
        for seed in self.seeds:
            conditions.append({
                "experiment_id": f"TOPOLOGY_LATTICE_{grid_size}X{grid_size}_SEED{seed}",
                "topology_type": "lattice",
                "population": self.base_population,
                "frequency": self.base_frequency,
                "cycles": self.cycles,
                "seed": seed,
                "configuration": "BASELINE",
                "topology_params": {"grid_size": grid_size}
            })

        return conditions

    def estimate_runtime(self, conditions: List[Dict]) -> Dict:
        """Estimate total runtime for all conditions"""
        # Assume ~1 minute per experiment (baseline from C171/C175)
        # May vary slightly with topology complexity
        total_experiments = len(conditions)
        estimated_minutes = total_experiments * 1.0  # 1 minute per experiment

        # Breakdown by topology type
        topology_counts = {}
        for cond in conditions:
            topo = cond["topology_type"]
            topology_counts[topo] = topology_counts.get(topo, 0) + 1

        return {
            "total_experiments": total_experiments,
            "estimated_runtime_minutes": estimated_minutes,
            "estimated_runtime_hours": estimated_minutes / 60,
            "topology_breakdown": topology_counts
        }


class NetworkTopologyAnalyzer:
    """Analyze topology effects on NRM patterns"""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir

    def load_results(self, conditions: List[Dict]) -> Dict:
        """Load experimental results from JSON files"""
        results = []

        for cond in conditions:
            exp_id = cond["experiment_id"]
            result_file = self.results_dir / f"{exp_id}.json"

            if result_file.exists():
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    results.append({
                        "condition": cond,
                        "data": data
                    })

        return {
            "total_loaded": len(results),
            "total_expected": len(conditions),
            "results": results
        }

    def compute_network_metrics(self, graph: nx.Graph) -> Dict:
        """Compute network topology metrics"""
        try:
            # Basic metrics
            n_nodes = graph.number_of_nodes()
            n_edges = graph.number_of_edges()

            # Check if graph is connected
            is_connected = nx.is_connected(graph)

            # Degree statistics
            degrees = dict(graph.degree())
            degree_values = list(degrees.values())

            metrics = {
                "n_nodes": n_nodes,
                "n_edges": n_edges,
                "density": nx.density(graph),
                "is_connected": is_connected,
                "degree_mean": np.mean(degree_values),
                "degree_std": np.std(degree_values),
                "degree_min": np.min(degree_values),
                "degree_max": np.max(degree_values)
            }

            # Metrics requiring connected graph
            if is_connected:
                metrics["average_path_length"] = nx.average_shortest_path_length(graph)
                metrics["diameter"] = nx.diameter(graph)
            else:
                # Use largest connected component
                largest_cc = max(nx.connected_components(graph), key=len)
                subgraph = graph.subgraph(largest_cc)
                metrics["average_path_length"] = nx.average_shortest_path_length(subgraph)
                metrics["diameter"] = nx.diameter(subgraph)
                metrics["largest_component_size"] = len(largest_cc)

            # Clustering coefficient
            metrics["clustering_coefficient"] = nx.average_clustering(graph)

            # Small-world coefficient (if applicable)
            # σ = (C/C_random) / (L/L_random)
            # where C = clustering, L = average path length
            # Generate random reference graph for comparison
            random_graph = nx.erdos_renyi_graph(n_nodes, n_edges / (n_nodes * (n_nodes - 1) / 2))
            if nx.is_connected(random_graph):
                C_random = nx.average_clustering(random_graph)
                L_random = nx.average_shortest_path_length(random_graph)

                if C_random > 0 and L_random > 0:
                    C_ratio = metrics["clustering_coefficient"] / C_random
                    L_ratio = metrics["average_path_length"] / L_random
                    if L_ratio > 0:
                        metrics["small_world_coefficient"] = C_ratio / L_ratio

            return metrics

        except Exception as e:
            return {"error": str(e)}

    def generate_topology(self, topology_type: str, n_nodes: int,
                         params: Dict, seed: int) -> nx.Graph:
        """Generate network topology based on type and parameters"""

        if topology_type == "fully_connected":
            return nx.complete_graph(n_nodes)

        elif topology_type == "random":
            p = params.get("p", 0.1)
            return nx.erdos_renyi_graph(n_nodes, p, seed=seed)

        elif topology_type == "small_world":
            k = params.get("k", 6)
            beta = params.get("beta", 0.1)
            return nx.watts_strogatz_graph(n_nodes, k, beta, seed=seed)

        elif topology_type == "scale_free":
            m = params.get("m", 2)
            return nx.barabasi_albert_graph(n_nodes, m, seed=seed)

        elif topology_type == "lattice":
            grid_size = params.get("grid_size", 10)
            # Create 2D grid with periodic boundary conditions (torus)
            return nx.grid_2d_graph(grid_size, grid_size, periodic=True)

        else:
            raise ValueError(f"Unknown topology type: {topology_type}")

    def analyze_topology_pattern_relationships(self, results: Dict) -> Dict:
        """Analyze relationship between topology metrics and pattern emergence"""

        topology_summary = {}

        for result in results["results"]:
            cond = result["condition"]
            data = result["data"]
            topo_type = cond["topology_type"]

            # Generate topology and compute metrics
            graph = self.generate_topology(
                topo_type,
                cond["population"],
                cond["topology_params"],
                cond["seed"]
            )
            network_metrics = self.compute_network_metrics(graph)

            # Extract pattern metrics from experimental data
            # (Assuming data contains pattern detection results from Paper 5D tools)
            pattern_count = data.get("pattern_count", 0)
            temporal_stability = data.get("temporal_stability", 0)
            memory_consistency = data.get("memory_consistency", 0)
            composition_events = data.get("composition_events", 0)

            # Store summary
            if topo_type not in topology_summary:
                topology_summary[topo_type] = {
                    "experiments": [],
                    "network_metrics": [],
                    "pattern_metrics": []
                }

            topology_summary[topo_type]["experiments"].append(cond["experiment_id"])
            topology_summary[topo_type]["network_metrics"].append(network_metrics)
            topology_summary[topo_type]["pattern_metrics"].append({
                "pattern_count": pattern_count,
                "temporal_stability": temporal_stability,
                "memory_consistency": memory_consistency,
                "composition_events": composition_events
            })

        # Compute aggregate statistics per topology type
        for topo_type in topology_summary:
            pattern_metrics = topology_summary[topo_type]["pattern_metrics"]

            topology_summary[topo_type]["aggregate"] = {
                "mean_pattern_count": np.mean([m["pattern_count"] for m in pattern_metrics]),
                "std_pattern_count": np.std([m["pattern_count"] for m in pattern_metrics]),
                "mean_temporal_stability": np.mean([m["temporal_stability"] for m in pattern_metrics]),
                "std_temporal_stability": np.std([m["temporal_stability"] for m in pattern_metrics]),
                "mean_memory_consistency": np.mean([m["memory_consistency"] for m in pattern_metrics]),
                "std_memory_consistency": np.std([m["memory_consistency"] for m in pattern_metrics]),
                "mean_composition_events": np.mean([m["composition_events"] for m in pattern_metrics]),
                "std_composition_events": np.std([m["composition_events"] for m in pattern_metrics])
            }

        return topology_summary


def main():
    """Generate Paper 5E experimental plan"""

    # Create output directory
    output_dir = Path("data/results/paper5e")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate experimental conditions
    config = NetworkTopologyConfig()
    conditions = config.generate_experiment_conditions()

    # Estimate runtime
    runtime_estimate = config.estimate_runtime(conditions)

    # Save experimental plan
    plan = {
        "paper": "Paper 5E: Network Topology Effects",
        "research_question": "How does network topology affect NRM emergent patterns?",
        "topology_types": [
            "fully_connected (baseline)",
            "random (Erdős-Rényi)",
            "small_world (Watts-Strogatz)",
            "scale_free (Barabási-Albert)",
            "lattice (2D grid)"
        ],
        "total_conditions": len(conditions),
        "runtime_estimate": runtime_estimate,
        "conditions": conditions
    }

    plan_file = output_dir / "paper5e_experimental_plan.json"
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2)

    print(f"✓ Paper 5E Experimental Plan Generated")
    print(f"  Total conditions: {len(conditions)}")
    print(f"  Topology types: {runtime_estimate['topology_breakdown']}")
    print(f"  Estimated runtime: {runtime_estimate['estimated_runtime_minutes']:.1f} minutes")
    print(f"  Plan saved: {plan_file}")


if __name__ == "__main__":
    main()
