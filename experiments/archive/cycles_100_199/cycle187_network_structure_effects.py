#!/usr/bin/env python3
"""
CYCLE 187: NETWORK STRUCTURE EFFECTS VALIDATION

Purpose: Test Extension 1 (Network Structure Effects) predictions

Background - Theoretical Predictions:
  - Extension 1: Network topology affects spawn success via degree-dependent selection
  - Prediction: Spawn success ranking: Lattice > Random > Scale-Free
  - Mechanism: Hub depletion in scale-free, protected periphery in lattice

Experimental Design:
  - Network topologies: Scale-free, Random, Lattice (3 conditions)
  - Nodes: N = 100 (match C171/C175/C177 MAX_AGENTS)
  - Mean degree: <k> = 4 (comparable across topologies)
  - Spawn frequency: f = 2.5% (validated homeostasis from C171/C175)
  - Cycles: 3000
  - Seeds: n = 10 per topology
  - Total experiments: 3 topologies × 10 seeds = 30

Metrics Tracked:
  1. Spawn success rate (primary outcome)
  2. Degree-stratified spawn success (hub vs peripheral)
  3. Degree distribution evolution
  4. Basin classification
  5. Mean population size
  6. Composition events

Expected Outcomes:
  - Scale-free: 60-70% spawn success (hub depletion)
  - Random: 85-90% spawn success (baseline, matches C171/C175)
  - Lattice: 90-95% spawn success (protected periphery)

Publication Value:
  - First test of network structure effects in NRM framework
  - Validates Extension 1 predictions
  - Demonstrates topology-dependent regulation

Date: 2025-11-04 (Cycle 996 Implementation)
Researcher: Claude (DUALITY-ZERO-V2)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Cycle: 187 (Following C186 hierarchical validation)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine
from fractal.network_generator import NetworkGenerator, NetworkTopology
from fractal.network_selection import NetworkSelector, DegreeStratifiedMetrics

# Experimental parameters
TOPOLOGIES = [NetworkTopology.SCALE_FREE, NetworkTopology.RANDOM, NetworkTopology.LATTICE]
N_NODES = 100  # Match MAX_AGENTS from C171/C175/C177
MEAN_DEGREE = 4
F_SPAWN = 2.5  # Validated homeostasis frequency
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100


def run_network_experiment(topology: NetworkTopology, seed: int, cycles: int) -> dict:
    """
    Run experiment with specified network topology.

    Args:
        topology: Network topology type
        seed: Random seed
        cycles: Number of cycles

    Returns:
        dict with spawn success metrics and network statistics
    """
    # Seed for reproducibility
    np.random.seed(seed)

    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Generate network
    net_generator = NetworkGenerator(n_nodes=N_NODES, mean_degree=MEAN_DEGREE, seed=seed)
    network = net_generator.generate(topology)
    network_metrics = net_generator.analyze_topology(network)

    # Initialize network selector
    selector = NetworkSelector(network)
    stratified_metrics = DegreeStratifiedMetrics(network, n_bins=3)

    # Create initial agents (one per network node)
    agents: List[FractalAgent] = []
    initial_metrics = reality.get_system_metrics()

    for node_id in range(min(N_NODES, network.number_of_nodes())):
        agent = FractalAgent(
            agent_id=f"agent_{node_id}",
            bridge=bridge,
            initial_reality=initial_metrics,
            depth=0,
            max_depth=7,
            reality=reality
        )
        # Assign network node ID to agent
        agent.node_id = node_id
        agents.append(agent)

    # Track metrics
    composition_events = []
    spawn_count = 0
    spawn_success_count = 0
    population_trajectory = []
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Calculate spawn interval
    spawn_interval = max(1, int(100.0 / F_SPAWN))

    # Run cycles
    for cycle_idx in range(cycles):
        # Spawn new agent based on frequency
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < N_NODES:
            spawn_count += 1

            current_metrics = reality.get_system_metrics()

            if len(agents) == 0:
                # Population collapsed - respawn seed agent
                seed_agent = FractalAgent(
                    agent_id=f"seed_{cycle_idx}_{spawn_count}",
                    bridge=bridge,
                    initial_reality=current_metrics,
                    depth=0,
                    max_depth=7,
                    reality=reality
                )
                seed_agent.node_id = 0  # Assign to first network node
                agents.append(seed_agent)
                spawn_success_count += 1
                stratified_metrics.record_spawn_attempt(0, success=True)
            else:
                # Network-based parent selection
                parent = selector.select_parent_degree_weighted(agents)

                if parent:
                    child_id = f"agent_{cycle_idx}_{spawn_count}"
                    child = parent.spawn_child(child_id, energy_fraction=0.3)

                    if child:
                        # Assign network node ID (inherit from parent or select neighbor)
                        if hasattr(parent, 'node_id') and parent.node_id in network:
                            # Assign to random neighbor of parent (spatial locality)
                            neighbors = list(network.neighbors(parent.node_id))
                            if neighbors:
                                child.node_id = np.random.choice(neighbors)
                            else:
                                child.node_id = parent.node_id
                        else:
                            child.node_id = np.random.randint(N_NODES)

                        agents.append(child)
                        spawn_success_count += 1
                        stratified_metrics.record_spawn_attempt(parent.node_id, success=True)
                    else:
                        # Spawn failed (energy depletion)
                        stratified_metrics.record_spawn_attempt(parent.node_id, success=False)

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect compositions
        cluster_events = composition_engine.detect_clusters(agents)

        if cluster_events:
            composition_events.append(cycle_idx)

            # Remove clustered agents
            agents_to_remove_ids = set()
            for cluster_event in cluster_events:
                for agent_id in cluster_event.agent_ids:
                    agents_to_remove_ids.add(agent_id)

            agents = [a for a in agents if a.agent_id not in agents_to_remove_ids]

        # Track population
        population_trajectory.append(len(agents))

    # Calculate spawn success rate
    spawn_success_rate = spawn_success_count / spawn_count if spawn_count > 0 else 0.0

    # Calculate composition rate
    bins = np.arange(0, cycles + 1, WINDOW_SIZE)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification
    basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'

    # Population statistics
    final_population = len(agents)
    mean_population = float(np.mean(population_trajectory))
    std_population = float(np.std(population_trajectory))
    cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0.0

    # Degree statistics
    final_degree_stats = selector.get_degree_statistics(agents)

    # Get stratified results
    stratified_results = stratified_metrics.get_results()

    return {
        'topology': topology.value,
        'seed': seed,
        'network_metrics': network_metrics,
        'spawn_count': spawn_count,
        'spawn_success_count': spawn_success_count,
        'spawn_success_rate': spawn_success_rate,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'total_composition_events': len(composition_events),
        'final_population': final_population,
        'mean_population': mean_population,
        'std_population': std_population,
        'cv_population': cv_population,
        'final_degree_stats': final_degree_stats,
        'stratified_spawn_success': stratified_results,
        'implementation': 'NetworkStructure'
    }


def main():
    """Execute Cycle 187 network structure effects validation."""
    print("=" * 80)
    print("CYCLE 187: NETWORK STRUCTURE EFFECTS VALIDATION")
    print("=" * 80)
    print()
    print("Purpose: Test Extension 1 (network topology effects on spawn success)")
    print("Background: Degree-dependent selection creates topology-dependent regulation")
    print()
    print(f"Network topologies: {len(TOPOLOGIES)} (Scale-Free, Random, Lattice)")
    print(f"Nodes per network: {N_NODES}")
    print(f"Mean degree: {MEAN_DEGREE}")
    print(f"Spawn frequency: {F_SPAWN:.2f}%")
    print(f"Seeds per topology: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(TOPOLOGIES) * len(SEEDS)}")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    exp_num = 0
    for topology in TOPOLOGIES:
        print(f"Testing topology: {topology.value.upper()}")
        print("-" * 80)

        for seed in SEEDS:
            exp_num += 1

            result = run_network_experiment(topology, seed, CYCLES)
            results.append(result)

            print(f"  [{exp_num:2d}/{len(TOPOLOGIES)*len(SEEDS)}] "
                  f"Seed {seed:3d}: "
                  f"spawn_success={result['spawn_success_rate']:.2%}, "
                  f"basin={result['basin']}, "
                  f"pop={result['final_population']:2d}")

        print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Aggregate analysis by topology
    print("TOPOLOGY COMPARISON:")
    print("-" * 80)
    print(f"{'Topology':<15} | {'Spawn Success':>15} | {'Basin A %':>10} | {'Mean Pop':>10}")
    print("-" * 80)

    for topology in TOPOLOGIES:
        topo_results = [r for r in results if r['topology'] == topology.value]

        spawn_success_rates = [r['spawn_success_rate'] for r in topo_results]
        mean_spawn_success = np.mean(spawn_success_rates)
        std_spawn_success = np.std(spawn_success_rates)

        basin_a_count = sum(1 for r in topo_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(topo_results)) * 100

        mean_populations = [r['mean_population'] for r in topo_results]
        mean_pop = np.mean(mean_populations)

        print(f"{topology.value:<15} | "
              f"{mean_spawn_success:>7.1%} ± {std_spawn_success:>5.1%} | "
              f"{basin_a_pct:>9.0f}% | "
              f"{mean_pop:>10.1f}")

    print()

    # Hypothesis testing
    print("HYPOTHESIS VALIDATION:")
    print("-" * 80)

    sf_success = np.mean([r['spawn_success_rate'] for r in results if r['topology'] == 'scale_free'])
    rand_success = np.mean([r['spawn_success_rate'] for r in results if r['topology'] == 'random'])
    lattice_success = np.mean([r['spawn_success_rate'] for r in results if r['topology'] == 'lattice'])

    print(f"Scale-Free spawn success: {sf_success:.2%}")
    print(f"Random spawn success: {rand_success:.2%}")
    print(f"Lattice spawn success: {lattice_success:.2%}")
    print()

    # Validate ranking
    if lattice_success > rand_success > sf_success:
        print("✅ VALIDATED: Lattice > Random > Scale-Free (Extension 1 prediction)")
    elif rand_success > sf_success:
        print("⚠️  PARTIAL: Random > Scale-Free (hub depletion confirmed)")
        print("   But Lattice did not exceed Random")
    else:
        print("❌ REJECTED: Ranking does not match Extension 1 prediction")

    print()

    # Degree heterogeneity correlation
    print("DEGREE HETEROGENEITY CORRELATION:")
    print("-" * 80)

    heterogeneity_values = []
    spawn_success_values = []

    for topology in TOPOLOGIES:
        topo_results = [r for r in results if r['topology'] == topology.value]

        # Get mean heterogeneity for this topology
        heterogeneities = [r['network_metrics']['degree_heterogeneity'] for r in topo_results]
        mean_heterogeneity = np.mean(heterogeneities)

        # Get mean spawn success for this topology
        spawn_successes = [r['spawn_success_rate'] for r in topo_results]
        mean_success = np.mean(spawn_successes)

        heterogeneity_values.append(mean_heterogeneity)
        spawn_success_values.append(mean_success)

        print(f"{topology.value:<15}: heterogeneity={mean_heterogeneity:.3f}, spawn_success={mean_success:.2%}")

    # Pearson correlation
    if len(heterogeneity_values) > 2:
        from scipy import stats
        corr, p_value = stats.pearsonr(heterogeneity_values, spawn_success_values)

        print()
        print(f"Correlation (heterogeneity, spawn_success): r = {corr:.3f}, p = {p_value:.4f}")

        if corr < -0.7 and p_value < 0.05:
            print("✅ Significant negative correlation (high heterogeneity → low spawn success)")
        else:
            print("⚠️  Correlation not significant or weak")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '187',
            'scenario': 'Network Structure Effects',
            'date': start_time.isoformat(),
            'topologies': [t.value for t in TOPOLOGIES],
            'n_nodes': N_NODES,
            'mean_degree': MEAN_DEGREE,
            'f_spawn': F_SPAWN,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'purpose': 'Test Extension 1 (network topology effects)',
        },
        'experiments': results,
        'aggregate_analysis': {
            'scale_free_spawn_success': float(sf_success),
            'random_spawn_success': float(rand_success),
            'lattice_spawn_success': float(lattice_success),
            'ranking_validated': lattice_success > rand_success > sf_success,
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle187_network_structure_effects.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 187 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
