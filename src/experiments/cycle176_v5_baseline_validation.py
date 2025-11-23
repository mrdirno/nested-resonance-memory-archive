#!/usr/bin/env python3
"""
CYCLE 176 V5 BASELINE VALIDATION

Purpose: Validate spawn logic bug fix before full ablation study
Strategy: Run BASELINE condition only with n=20 seeds for robust statistics
Expected: Mean population ~17 agents, CV < 15% (homeostatic)

If validation passes → Proceed with full C176 V5 (6 conditions × 10 seeds)
If validation fails → Investigate further before full run

Date: 2025-11-01
Cycle: 176 V5 Baseline Validation

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
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

# Validation parameters
FREQUENCY = 2.5  # Midpoint of C171 homeostatic range (2.0%-3.0%)
SEEDS = list(range(42, 62))  # n=20 for robust statistics
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100

# Expected outcomes (from C171)
EXPECTED_MEAN_POP = 17.0
EXPECTED_CV_THRESHOLD = 15.0  # Homeostatic if CV < 15%


def run_baseline_experiment(frequency: float, seed: int, cycles: int) -> Dict:
    """
    Run BASELINE experiment with V5 spawn logic.

    Args:
        frequency: Spawn frequency (% per 100 cycles)
        seed: Random seed
        cycles: Number of cycles

    Returns:
        dict with population metrics and composition statistics
    """
    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Seed for reproducibility
    np.random.seed(seed)

    # Initial agent
    metrics = reality.get_system_metrics()
    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality
    )
    agents = [root]

    # Track metrics
    composition_events = []
    spawn_count = 0
    population_trajectory = []

    # Calculate spawn interval
    spawn_interval = max(1, int(100.0 / frequency))

    # Composition engine
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Run cycles
    for cycle_idx in range(cycles):

        # V5 spawn logic: Always spawn fresh seed agents (no population check)
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < MAX_AGENTS:
            spawn_count += 1

            # Get current reality metrics
            current_metrics = reality.get_system_metrics()

            # Always create fresh seed agent (no parent dependency)
            seed_agent = FractalAgent(
                agent_id=f"agent_{cycle_idx}_{spawn_count}",
                bridge=bridge,
                initial_reality=current_metrics,
                depth=0,
                max_depth=7,
                reality=reality
            )
            agents.append(seed_agent)

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect clusters (composition events)
        cluster_events = composition_engine.detect_clusters(agents)

        # Record composition events
        if cluster_events:
            composition_events.append(cycle_idx)

        # Remove agents in clusters
        if cluster_events:
            # Extract agent IDs from all cluster events
            agents_to_remove_ids = set()
            for cluster_event in cluster_events:
                for agent_id in cluster_event.agent_ids:
                    agents_to_remove_ids.add(agent_id)

            # Remove clustered agents from swarm
            agents = [a for a in agents if a.agent_id not in agents_to_remove_ids]

        # Track population
        population_trajectory.append(len(agents))

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

    return {
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': final_population,
        'mean_population': mean_population,
        'std_population': std_population,
        'cv_population': cv_population,
    }


def main():
    """Execute C176 V5 baseline validation."""
    print("=" * 80)
    print("CYCLE 176 V5: BASELINE VALIDATION")
    print("=" * 80)
    print()
    print("Purpose: Validate spawn logic bug fix")
    print("Condition: BASELINE only (birth + death enabled)")
    print()
    print(f"Frequency: {FREQUENCY}%")
    print(f"Seeds: n={len(SEEDS)}")
    print(f"Cycles: {CYCLES}")
    print()
    print(f"Expected Mean Population: ~{EXPECTED_MEAN_POP} agents")
    print(f"Expected CV: < {EXPECTED_CV_THRESHOLD}%")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    for i, seed in enumerate(SEEDS, 1):
        result = run_baseline_experiment(FREQUENCY, seed, CYCLES)
        results.append(result)

        print(f"[{i:2d}/{len(SEEDS)}] "
              f"Seed {seed:3d}: "
              f"pop={result['mean_population']:5.1f} ± {result['std_population']:4.1f} "
              f"(CV={result['cv_population']:4.1f}%), "
              f"comp={result['avg_composition_events']:5.2f}, "
              f"basin={result['basin']}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print()
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print()

    # Statistical summary
    mean_pops = [r['mean_population'] for r in results]
    cvs = [r['cv_population'] for r in results]

    overall_mean_pop = np.mean(mean_pops)
    overall_std_pop = np.std(mean_pops)
    overall_mean_cv = np.mean(cvs)

    print("STATISTICAL SUMMARY:")
    print("-" * 80)
    print(f"Mean Population: {overall_mean_pop:.2f} ± {overall_std_pop:.2f} agents")
    print(f"Mean CV: {overall_mean_cv:.2f}%")
    print(f"Range: [{min(mean_pops):.1f}, {max(mean_pops):.1f}] agents")
    print()

    # Validation checks
    print("VALIDATION CHECKS:")
    print("-" * 80)

    pop_check = abs(overall_mean_pop - EXPECTED_MEAN_POP) < 5.0  # Within 5 agents of expected
    cv_check = overall_mean_cv < EXPECTED_CV_THRESHOLD

    print(f"1. Population near expected ({EXPECTED_MEAN_POP} ± 5): {'✅ PASS' if pop_check else '❌ FAIL'}")
    print(f"   (Actual: {overall_mean_pop:.2f})")
    print(f"2. CV indicates homeostasis (< {EXPECTED_CV_THRESHOLD}%): {'✅ PASS' if cv_check else '❌ FAIL'}")
    print(f"   (Actual: {overall_mean_cv:.2f}%)")
    print()

    if pop_check and cv_check:
        print("✅ VALIDATION PASSED: Bug fix successful, proceed with full C176 V5")
    else:
        print("❌ VALIDATION FAILED: Further investigation needed before full run")
    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '176',
            'version': 'V5',
            'scenario': 'Baseline Validation',
            'date': start_time.isoformat(),
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'cycles_per_experiment': CYCLES,
            'duration_minutes': duration,
            'expected_mean_pop': EXPECTED_MEAN_POP,
            'expected_cv_threshold': EXPECTED_CV_THRESHOLD,
        },
        'experiments': results,
        'validation': {
            'overall_mean_pop': overall_mean_pop,
            'overall_std_pop': overall_std_pop,
            'overall_mean_cv': overall_mean_cv,
            'pop_check_passed': pop_check,
            'cv_check_passed': cv_check,
            'overall_passed': pop_check and cv_check,
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle176_v5_baseline_validation.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
