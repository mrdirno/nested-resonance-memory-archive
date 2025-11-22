#!/usr/bin/env python3
"""
CYCLE 189: BURST CLUSTERING VALIDATION

Purpose: Test Extension 4 (Part C) - Temporal Clustering predictions

Background - Theoretical Predictions:
  - Extension 4 (Part C): Compositions exhibit burst dynamics
  - Prediction: Inter-event intervals follow power-law (NOT exponential/Poisson)
  - Mechanism: Cascades (avalanches) from energy depletion correlations

Experimental Design:
  - Frequency conditions: f = 1.5%, 2.0%, 2.5%, 3.0%, 5.0%
  - Cycles: 5000 (extended run for burst statistics)
  - Seeds: n = 20 per frequency
  - Total experiments: 5 frequencies × 20 seeds = 100

Metrics Tracked:
  1. Inter-event interval (IEI) distribution (primary outcome)
  2. Power-law exponent α (fitted to IEI tail)
  3. Burstiness coefficient B (temporal clustering)
  4. Autocorrelation function (lag analysis)
  5. Avalanche size distribution (cascade events)
  6. Mean population size
  7. Basin classification

Expected Outcomes:
  - Power-law IEI: α = 2.0-2.5 (avalanche dynamics)
  - Burstiness: B > 0.3 (significantly clustered)
  - α decreases with frequency (more bursty at high f)

Publication Value:
  - First quantification of temporal clustering in NRM framework
  - Validates Extension 4 (Part C) predictions
  - Connects NRM to self-organized criticality (SOC) literature
  - Demonstrates avalanche dynamics in fractal agent systems

Date: 2025-11-04 (Cycle 997 Implementation)
Researcher: Claude (DUALITY-ZERO-V2)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Cycle: 189 (Following C187 network and C188 memory validation)
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
sys.path.insert(0, str(Path(__file__).parent.parent / "analysis"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine
from analysis.burst_analysis import comprehensive_burst_analysis

# Experimental parameters
FREQUENCY_CONDITIONS = [1.5, 2.0, 2.5, 3.0, 5.0]  # Spawn frequencies (%)
SEEDS = list(range(42, 62))  # n=20 per frequency (42-61)
CYCLES = 5000  # Extended run for burst statistics
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100


def run_burst_experiment(
    frequency: float,
    seed: int,
    cycles: int
) -> dict:
    """
    Run experiment with specified spawn frequency.

    Args:
        frequency: Spawn frequency (% per 100 cycles)
        seed: Random seed
        cycles: Number of cycles

    Returns:
        dict with burst clustering metrics and IEI analysis
    """
    # Seed for reproducibility
    np.random.seed(seed)

    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

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
    spawn_interval = max(1, int(100.0 / frequency))

    # Run cycles
    for cycle_idx in range(cycles):
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
                # Random parent selection
                parent = np.random.choice(agents)
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

    # Burst clustering analysis
    burst_results = comprehensive_burst_analysis(composition_events)

    # Extract key metrics
    return {
        'frequency': frequency,
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
        'burst_analysis': burst_results,
        'composition_events': composition_events,  # Raw event times for analysis
        'implementation': 'BurstClustering'
    }


def main():
    """Execute Cycle 189 burst clustering validation."""
    print("=" * 80)
    print("CYCLE 189: BURST CLUSTERING VALIDATION")
    print("=" * 80)
    print()
    print("Purpose: Test Extension 4 (Part C) - temporal clustering predictions")
    print("Background: Compositions exhibit burst dynamics (avalanches)")
    print()
    print(f"Frequency conditions: {len(FREQUENCY_CONDITIONS)} ({min(FREQUENCY_CONDITIONS):.1f}%-{max(FREQUENCY_CONDITIONS):.1f}%)")
    print(f"Seeds per frequency: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(FREQUENCY_CONDITIONS) * len(SEEDS)}")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    exp_num = 0
    for frequency in FREQUENCY_CONDITIONS:
        print(f"Testing frequency = {frequency:.2f}%")
        print("-" * 80)

        for seed in SEEDS:
            exp_num += 1

            result = run_burst_experiment(frequency, seed, CYCLES)
            results.append(result)

            # Extract burst metrics
            burst = result['burst_analysis']

            # Handle cases with insufficient data
            if 'error' in burst:
                print(f"  [{exp_num:3d}/{len(FREQUENCY_CONDITIONS)*len(SEEDS)}] "
                      f"Seed {seed:3d}: "
                      f"comp={result['total_composition_events']}, "
                      f"error={burst['error']}")
            else:
                dist_fit = burst['distribution_fits']
                alpha = dist_fit['power_law']['alpha'] if 'power_law' in dist_fit else np.nan
                B = burst['burstiness']

                print(f"  [{exp_num:3d}/{len(FREQUENCY_CONDITIONS)*len(SEEDS)}] "
                      f"Seed {seed:3d}: "
                      f"comp={result['total_composition_events']}, "
                      f"B={B:.3f}, "
                      f"α={alpha:.2f}, "
                      f"basin={result['basin']}")

        print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Aggregate analysis by frequency
    print("FREQUENCY COMPARISON:")
    print("-" * 80)
    print(f"{'Freq (%)':>8} | {'N Events':>10} | {'Burstiness':>12} | {'Power-law α':>14} | {'Basin A %':>10}")
    print("-" * 80)

    for frequency in FREQUENCY_CONDITIONS:
        freq_results = [r for r in results if r['frequency'] == frequency]

        # Composition events
        comp_events = [r['total_composition_events'] for r in freq_results]
        mean_comp = np.mean(comp_events)

        # Burstiness
        burstiness_values = []
        for r in freq_results:
            burst = r['burst_analysis']
            if 'burstiness' in burst:
                burstiness_values.append(burst['burstiness'])

        mean_burstiness = np.mean(burstiness_values) if burstiness_values else np.nan
        std_burstiness = np.std(burstiness_values) if burstiness_values else np.nan

        # Power-law exponent
        alpha_values = []
        for r in freq_results:
            burst = r['burst_analysis']
            if 'distribution_fits' in burst and 'power_law' in burst['distribution_fits']:
                alpha = burst['distribution_fits']['power_law']['alpha']
                if not np.isnan(alpha):
                    alpha_values.append(alpha)

        mean_alpha = np.mean(alpha_values) if alpha_values else np.nan
        std_alpha = np.std(alpha_values) if alpha_values else np.nan

        # Basin A percentage
        basin_a_count = sum(1 for r in freq_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_results)) * 100

        print(f"{frequency:>8.2f} | "
              f"{mean_comp:>10.1f} | "
              f"{mean_burstiness:>6.3f} ± {std_burstiness:>4.3f} | "
              f"{mean_alpha:>7.2f} ± {std_alpha:>5.2f} | "
              f"{basin_a_pct:>9.0f}%")

    print()

    # Hypothesis validation
    print("HYPOTHESIS VALIDATION:")
    print("-" * 80)

    # Extract frequency-level metrics
    freq_burstiness = {}
    freq_alpha = {}

    for frequency in FREQUENCY_CONDITIONS:
        freq_results = [r for r in results if r['frequency'] == frequency]

        # Aggregate burstiness
        B_values = [
            r['burst_analysis']['burstiness']
            for r in freq_results
            if 'burstiness' in r['burst_analysis']
        ]
        freq_burstiness[frequency] = np.mean(B_values) if B_values else np.nan

        # Aggregate alpha
        alpha_values = [
            r['burst_analysis']['distribution_fits']['power_law']['alpha']
            for r in freq_results
            if ('distribution_fits' in r['burst_analysis'] and
                'power_law' in r['burst_analysis']['distribution_fits'] and
                not np.isnan(r['burst_analysis']['distribution_fits']['power_law']['alpha']))
        ]
        freq_alpha[frequency] = np.mean(alpha_values) if alpha_values else np.nan

    # Test 1: Burstiness > 0.3 (significantly clustered)
    print("Test 1: Burstiness Coefficient")
    for frequency, B in freq_burstiness.items():
        if not np.isnan(B):
            status = "✅" if B > 0.3 else "⚠️"
            print(f"  f={frequency:.1f}%: B={B:.3f} {status}")

    print()

    # Test 2: Power-law exponent α = 2.0-2.5
    print("Test 2: Power-Law Exponent")
    for frequency, alpha in freq_alpha.items():
        if not np.isnan(alpha):
            status = "✅" if 2.0 <= alpha <= 2.5 else "⚠️"
            print(f"  f={frequency:.1f}%: α={alpha:.2f} {status}")

    print()

    # Test 3: α decreases with frequency
    print("Test 3: Frequency Dependence")
    valid_alphas = [(f, a) for f, a in freq_alpha.items() if not np.isnan(a)]

    if len(valid_alphas) >= 3:
        frequencies_sorted = [f for f, _ in sorted(valid_alphas, key=lambda x: x[0])]
        alphas_sorted = [a for _, a in sorted(valid_alphas, key=lambda x: x[0])]

        # Check if alpha decreases with frequency
        decreasing = all(alphas_sorted[i] >= alphas_sorted[i+1] for i in range(len(alphas_sorted)-1))

        if decreasing:
            print("✅ α decreases with frequency (more bursty at high f)")
        else:
            print("⚠️  α trend does not match prediction")

        print(f"  Lowest f ({frequencies_sorted[0]:.1f}%): α={alphas_sorted[0]:.2f}")
        print(f"  Highest f ({frequencies_sorted[-1]:.1f}%): α={alphas_sorted[-1]:.2f}")
    else:
        print("⚠️  Insufficient valid power-law fits for trend analysis")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '189',
            'scenario': 'Burst Clustering',
            'date': start_time.isoformat(),
            'frequency_conditions': FREQUENCY_CONDITIONS,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'purpose': 'Test Extension 4 (Part C) - temporal clustering predictions',
        },
        'experiments': results,
        'aggregate_analysis': {
            'burstiness_by_frequency': freq_burstiness,
            'alpha_by_frequency': freq_alpha,
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle189_burst_clustering.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 189 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
