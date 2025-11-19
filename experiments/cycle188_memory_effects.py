#!/usr/bin/env python3
"""
CYCLE 188: MEMORY EFFECTS VALIDATION

Purpose: Test Extension 4 (Part B) - Memory Effects predictions

Background - Theoretical Predictions:
  - Extension 4 (Part B): Memory creates refractory periods
  - Prediction: Longer memory → higher spawn success, lower burstiness
  - Mechanism: Recently-composed agents avoided in selection

Experimental Design:
  - Memory conditions: None, Short (τ=100), Medium (τ=500), Long (τ=1000)
  - Spawn frequency: f = 2.5% (validated homeostasis)
  - Cycles: 3000
  - Seeds: n = 10 per condition
  - Total experiments: 4 conditions × 10 seeds = 40

Metrics Tracked:
  1. Spawn success rate (primary outcome)
  2. Burstiness coefficient B (temporal clustering)
  3. Inter-event intervals (distribution analysis)
  4. Composition autocorrelation (temporal correlations)
  5. Basin classification
  6. Mean population size

Expected Outcomes:
  - No memory: 88% spawn success, B ≈ 0.3
  - Short memory (τ=100): 90-92% spawn success, B ≈ 0.2
  - Medium memory (τ=500): 92-94% spawn success, B ≈ 0.1
  - Long memory (τ=1000): 94-96% spawn success, B ≈ 0.0

Publication Value:
  - First test of memory effects in NRM framework
  - Validates Extension 4 (Part B) predictions
  - Demonstrates temporal regulation mechanisms

Date: 2025-11-04 (Cycle 997 Implementation)
Researcher: Claude (DUALITY-ZERO-V2)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Cycle: 188 (Following C187 network validation)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine
from fractal.memory_tracker import MemoryTracker, BurstinessCalculator

# Experimental parameters
MEMORY_CONDITIONS = [
    ('none', None),           # No memory (baseline)
    ('short', 100),           # τ = 100 cycles
    ('medium', 500),          # τ = 500 cycles
    ('long', 1000),           # τ = 1000 cycles
]
F_SPAWN = 2.5  # Validated homeostasis frequency
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100


def select_parent_with_memory(
    agents: List[FractalAgent],
    memory_tracker: Optional[MemoryTracker],
    decay_factor: float = 2.0
) -> Optional[FractalAgent]:
    """
    Select parent with memory-weighted probability.

    If memory_tracker is None, use uniform random selection (baseline).

    Args:
        agents: List of active agents
        memory_tracker: Memory tracker instance (or None for baseline)
        decay_factor: Memory decay parameter

    Returns:
        Selected parent agent
    """
    if len(agents) == 0:
        return None

    if memory_tracker is None:
        # Baseline: uniform random selection
        return np.random.choice(agents)

    # Memory-weighted selection
    agent_ids = [agent.agent_id for agent in agents]
    weights_dict = memory_tracker.get_all_weights(agent_ids, decay_factor)

    # Extract weights in agent order
    weights = np.array([weights_dict.get(agent.agent_id, 1.0) for agent in agents])

    # Normalize to probabilities
    if np.sum(weights) == 0:
        # Fallback to uniform if all weights are zero
        weights = np.ones(len(agents))

    probabilities = weights / np.sum(weights)

    # Select parent
    parent = np.random.choice(agents, p=probabilities)
    return parent


def run_memory_experiment(
    memory_condition: str,
    memory_window: Optional[int],
    seed: int,
    cycles: int
) -> dict:
    """
    Run experiment with specified memory condition.

    Args:
        memory_condition: Memory condition name ('none', 'short', 'medium', 'long')
        memory_window: Memory window size (τ_memory) or None for baseline
        seed: Random seed
        cycles: Number of cycles

    Returns:
        dict with spawn success metrics and burstiness analysis
    """
    # Seed for reproducibility
    np.random.seed(seed)

    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Initialize memory tracker (if not baseline)
    memory_tracker = MemoryTracker(memory_window) if memory_window is not None else None

    # Create initial agent
    initial_metrics = reality.get_system_metrics()
    initial_agent = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=initial_metrics,
        depth=0,
        max_depth=7,
        reality=reality
    )

    agents = [initial_agent]
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Track metrics
    composition_events = []
    spawn_count = 0
    spawn_success_count = 0
    population_trajectory = []

    # Calculate spawn interval
    spawn_interval = max(1, int(100.0 / F_SPAWN))

    # Run cycles
    for cycle_idx in range(cycles):
        # Update memory tracker cycle
        if memory_tracker is not None:
            memory_tracker.current_cycle = cycle_idx

        # Spawn new agent
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < MAX_AGENTS:
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
                agents.append(seed_agent)
                spawn_success_count += 1
            else:
                # Memory-weighted parent selection
                parent = select_parent_with_memory(agents, memory_tracker)

                if parent:
                    child_id = f"agent_{cycle_idx}_{spawn_count}"
                    child = parent.spawn_child(child_id, energy_fraction=0.3)

                    if child:
                        agents.append(child)
                        spawn_success_count += 1

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect compositions
        cluster_events = composition_engine.detect_clusters(agents)

        if cluster_events:
            composition_events.append(cycle_idx)

            # Record compositions in memory tracker
            if memory_tracker is not None:
                for cluster_event in cluster_events:
                    memory_tracker.record_composition(
                        list(cluster_event.agent_ids),
                        cycle_idx
                    )

            # Remove clustered agents
            agents_to_remove_ids = set()
            for cluster_event in cluster_events:
                for agent_id in cluster_event.agent_ids:
                    agents_to_remove_ids.add(agent_id)

            # Clear memory for removed agents
            if memory_tracker is not None:
                for agent_id in agents_to_remove_ids:
                    memory_tracker.clear_agent_history(agent_id)

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

    # Burstiness analysis
    burstiness = BurstinessCalculator.calculate_burstiness(composition_events)

    # Autocorrelation
    autocorr = BurstinessCalculator.calculate_autocorrelation(composition_events, max_lag=100)

    # Inter-event intervals
    if len(composition_events) >= 2:
        sorted_events = sorted(composition_events)
        intervals = [sorted_events[i+1] - sorted_events[i] for i in range(len(sorted_events)-1)]
        mean_iei = float(np.mean(intervals))
        std_iei = float(np.std(intervals))
    else:
        mean_iei = 0.0
        std_iei = 0.0
        intervals = []

    # Memory tracker statistics
    if memory_tracker is not None:
        memory_stats = memory_tracker.get_statistics()
    else:
        memory_stats = None

    return {
        'memory_condition': memory_condition,
        'memory_window': memory_window,
        'seed': seed,
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
        'burstiness': burstiness,
        'autocorrelation_lag1': float(autocorr[1]) if len(autocorr) > 1 else 0.0,
        'mean_inter_event_interval': mean_iei,
        'std_inter_event_interval': std_iei,
        'memory_stats': memory_stats,
        'implementation': 'MemoryEffects'
    }


def main():
    """Execute Cycle 188 memory effects validation."""
    print("=" * 80)
    print("CYCLE 188: MEMORY EFFECTS VALIDATION")
    print("=" * 80)
    print()
    print("Purpose: Test Extension 4 (Part B) - memory creates refractory periods")
    print("Background: Recently-composed agents avoided in selection")
    print()
    print(f"Memory conditions: {len(MEMORY_CONDITIONS)} (None, Short, Medium, Long)")
    print(f"Spawn frequency: {F_SPAWN:.2f}%")
    print(f"Seeds per condition: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(MEMORY_CONDITIONS) * len(SEEDS)}")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    exp_num = 0
    for condition_name, memory_window in MEMORY_CONDITIONS:
        print(f"Testing memory condition: {condition_name.upper()} (τ={memory_window if memory_window else 'N/A'})")
        print("-" * 80)

        for seed in SEEDS:
            exp_num += 1

            result = run_memory_experiment(condition_name, memory_window, seed, CYCLES)
            results.append(result)

            print(f"  [{exp_num:2d}/{len(MEMORY_CONDITIONS)*len(SEEDS)}] "
                  f"Seed {seed:3d}: "
                  f"spawn_success={result['spawn_success_rate']:.2%}, "
                  f"B={result['burstiness']:.3f}, "
                  f"basin={result['basin']}")

        print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Aggregate analysis by memory condition
    print("MEMORY CONDITION COMPARISON:")
    print("-" * 80)
    print(f"{'Condition':<12} | {'Spawn Success':>15} | {'Burstiness':>12} | {'Basin A %':>10}")
    print("-" * 80)

    for condition_name, memory_window in MEMORY_CONDITIONS:
        cond_results = [r for r in results if r['memory_condition'] == condition_name]

        spawn_success_rates = [r['spawn_success_rate'] for r in cond_results]
        mean_spawn_success = np.mean(spawn_success_rates)
        std_spawn_success = np.std(spawn_success_rates)

        burstiness_values = [r['burstiness'] for r in cond_results]
        mean_burstiness = np.mean(burstiness_values)
        std_burstiness = np.std(burstiness_values)

        basin_a_count = sum(1 for r in cond_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(cond_results)) * 100

        print(f"{condition_name:<12} | "
              f"{mean_spawn_success:>7.1%} ± {std_spawn_success:>5.1%} | "
              f"{mean_burstiness:>6.3f} ± {std_burstiness:>4.3f} | "
              f"{basin_a_pct:>9.0f}%")

    print()

    # Hypothesis validation
    print("HYPOTHESIS VALIDATION:")
    print("-" * 80)

    # Extract means by condition
    condition_spawn_success = {}
    condition_burstiness = {}

    for condition_name, memory_window in MEMORY_CONDITIONS:
        cond_results = [r for r in results if r['memory_condition'] == condition_name]
        condition_spawn_success[condition_name] = np.mean([r['spawn_success_rate'] for r in cond_results])
        condition_burstiness[condition_name] = np.mean([r['burstiness'] for r in cond_results])

    # Test spawn success ranking: Long > Medium > Short > None
    spawn_ranking = sorted(condition_spawn_success.items(), key=lambda x: x[1], reverse=True)
    expected_ranking = ['long', 'medium', 'short', 'none']
    actual_ranking = [name for name, value in spawn_ranking]

    print("Spawn Success Ranking:")
    for i, (name, value) in enumerate(spawn_ranking):
        print(f"  {i+1}. {name}: {value:.2%}")

    if actual_ranking == expected_ranking:
        print("✅ VALIDATED: Spawn success ranking matches prediction (Long > Medium > Short > None)")
    else:
        print(f"⚠️  PARTIAL: Actual ranking {actual_ranking} vs expected {expected_ranking}")

    print()

    # Test burstiness ranking: None > Short > Medium > Long
    burstiness_ranking = sorted(condition_burstiness.items(), key=lambda x: x[1], reverse=True)
    expected_b_ranking = ['none', 'short', 'medium', 'long']
    actual_b_ranking = [name for name, value in burstiness_ranking]

    print("Burstiness Ranking:")
    for i, (name, value) in enumerate(burstiness_ranking):
        print(f"  {i+1}. {name}: B = {value:.3f}")

    if actual_b_ranking == expected_b_ranking:
        print("✅ VALIDATED: Burstiness ranking matches prediction (None > Short > Medium > Long)")
    else:
        print(f"⚠️  PARTIAL: Actual ranking {actual_b_ranking} vs expected {expected_b_ranking}")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '188',
            'scenario': 'Memory Effects',
            'date': start_time.isoformat(),
            'memory_conditions': [{'name': name, 'window': window} for name, window in MEMORY_CONDITIONS],
            'f_spawn': F_SPAWN,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'purpose': 'Test Extension 4 (Part B) - memory creates refractory periods',
        },
        'experiments': results,
        'aggregate_analysis': {
            'spawn_success_by_condition': condition_spawn_success,
            'burstiness_by_condition': condition_burstiness,
            'spawn_ranking_validated': actual_ranking == expected_ranking,
            'burstiness_ranking_validated': actual_b_ranking == expected_b_ranking,
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle188_memory_effects.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 188 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
