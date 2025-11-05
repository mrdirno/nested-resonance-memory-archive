#!/usr/bin/env python3
"""
CYCLE 177: EXTENDED FREQUENCY RANGE - Homeostasis Boundary Mapping

Purpose: Find boundaries of homeostatic regime beyond confirmed 2.0-3.0% range

Background - C171/C175 Findings:
  - C171: Homeostasis confirmed at f = 2.0%, 2.5%, 2.6%, 3.0% (100% Basin A)
  - C175: Homeostasis confirmed at f = 2.50-2.60% high-resolution (100% Basin A, n=110)
  - Combined: Homeostatic regime spans minimum 2.0-3.0% (52% variation)
  - Question: WHERE are the boundaries of homeostasis?

Experimental Design:
  - Wide frequency sweep: 0.5% → 10.0%
  - Logarithmic-like sampling for efficient coverage
  - Frequencies: [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0] (9 values)
  - Seeds: n=10 per frequency (same rigor as C171/C175)
  - Cycles: 3000 per experiment
  - Total: 9 frequencies × 10 seeds = 90 experiments

Expected Outcomes:
  1. Bounded Homeostasis:
     - Low range (0.5-1.5%): Basin B (population collapse)
     - Middle range (2.0-3.0%): Basin A (homeostasis, control replication)
     - High range (4.0-10.0%): Basin A or novel regime (saturation effects)

  2. Unbounded Homeostasis:
     - ALL frequencies: Basin A (extreme robustness)
     - Regulatory capacity exceeds tested range

  3. Complex Dynamics:
     - Mixed basins at boundary frequencies
     - Stochastic bistability indicators
     - Phase transition regions

Publication Value:
  - First quantification of homeostatic regime boundaries
  - Defines domain of applicability for population regulation
  - Tests population collapse hypothesis (low f)
  - Tests saturation hypothesis (high f)
  - Validates negative feedback loop predictions

Date: 2025-10-25 (Cycle 204 Design)
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 177 (Following C175 robustness validation)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine

# Experimental parameters
FREQUENCIES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0]  # Logarithmic-like sampling
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10 (match C171/C175)
CYCLES = 3000
BASIN_THRESHOLD = 2.5  # Same as C168-C171-C175
WINDOW_SIZE = 100
MAX_AGENTS = 100  # Same as C171/C175

def run_extended_range_experiment(frequency: float, seed: int, cycles: int) -> dict:
    """
    Run experiment at specified frequency (matching C171/C175 structure).

    Args:
        frequency: Spawn frequency (% per 100 cycles)
        seed: Random seed
        cycles: Number of cycles

    Returns:
        dict with composition events and basin classification
    """
    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Seed for reproducibility
    np.random.seed(seed)

    # Get real system metrics for initial agent
    metrics = reality.get_system_metrics()

    # Create initial fractal agent
    initial_agent = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality  # Energy recharge enabled (Cycle 215 enhancement)
    )

    # Track composition events (cluster formations)
    composition_events = []
    spawn_count = 0
    population_trajectory = []  # Track population over time (added Cycle 990 fix)

    # Calculate spawn interval from frequency
    spawn_interval = max(1, int(100.0 / frequency)) if frequency > 0 else cycles + 1

    # Active agents list (starts with root)
    agents = [initial_agent]
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Run cycles
    for cycle_idx in range(cycles):
        # Spawn new agent based on frequency
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < MAX_AGENTS:
            spawn_count += 1

            # Get current reality metrics
            current_metrics = reality.get_system_metrics()

            if len(agents) == 0:
                # Population collapsed - respawn seed agent
                seed_agent = FractalAgent(
                    agent_id=f"seed_{cycle_idx}_{spawn_count}",
                    bridge=bridge,
                    initial_reality=current_metrics,
                    depth=0,
                    max_depth=7,
                    reality=reality  # Energy recharge enabled (Cycle 215 enhancement)
                )
                agents.append(seed_agent)
            else:
                # Normal spawning from existing parent
                parent = agents[np.random.randint(len(agents))]
                child_id = f"agent_{cycle_idx}_{spawn_count}"
                child = parent.spawn_child(child_id, energy_fraction=0.3)
                if child:
                    agents.append(child)

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect clusters (composition events)
        cluster_events = composition_engine.detect_clusters(agents)

        # Record composition events
        if cluster_events:
            composition_events.append(cycle_idx)

        # Remove agents in clusters (death through composition)
        if cluster_events:
            # cluster_events is list of ClusterEvent objects
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

    # Population statistics (same as C171/C176 for comparison)
    final_population = len(agents)
    mean_population = float(np.mean(population_trajectory))
    std_population = float(np.std(population_trajectory))
    cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0.0

    return {
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': final_population,
        'mean_population': mean_population,
        'std_population': std_population,
        'cv_population': cv_population,
        'implementation': 'ExtendedRange'
    }

def main():
    """Execute Cycle 177 extended frequency range mapping."""
    print("=" * 80)
    print("CYCLE 177: EXTENDED FREQUENCY RANGE - Homeostasis Boundary Mapping")
    print("=" * 80)
    print()
    print("Purpose: Find boundaries of homeostatic regime beyond 2.0-3.0%")
    print("Background: C171/C175 showed robust homeostasis across 2.0-3.0% range")
    print()
    print(f"Frequency range: {FREQUENCIES[0]:.2f}% - {FREQUENCIES[-1]:.2f}%")
    print(f"Step size: {FREQUENCIES[1] - FREQUENCIES[0]:.2f}% (10× finer than C169)")
    print(f"Number of frequencies: {len(FREQUENCIES)}")
    print(f"Seeds per frequency: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(FREQUENCIES) * len(SEEDS)}")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    exp_num = 0
    for frequency in FREQUENCIES:
        print(f"Testing frequency = {frequency:.2f}%")
        print("-" * 80)

        for seed in SEEDS:
            exp_num += 1

            result = run_extended_range_experiment(frequency, seed, CYCLES)
            results.append(result)

            print(f"  [{exp_num:3d}/{len(FREQUENCIES)*len(SEEDS)}] "
                  f"Seed {seed:3d}: comp={result['avg_composition_events']:5.2f}, "
                  f"basin={result['basin']}, "
                  f"pop={result['final_agent_count']:2d}")

        print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Analyze transition width
    print("TRANSITION ANALYSIS:")
    print("-" * 80)
    print(f"{'Frequency':>10} | {'Basin A %':>10} | {'Basin':>6} | {'Avg Comp':>9}")
    print("-" * 80)

    for frequency in FREQUENCIES:
        freq_results = [r for r in results if r['frequency'] == frequency]
        basin_a_count = sum(1 for r in freq_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_results)) * 100
        avg_comp = np.mean([r['avg_composition_events'] for r in freq_results])

        # Determine dominant basin
        if basin_a_pct == 100:
            basin_str = "A"
        elif basin_a_pct == 0:
            basin_str = "B"
        else:
            basin_str = "MIXED"  # Critical finding!

        print(f"{frequency:>9.2f}% | {basin_a_pct:>9.0f}% | {basin_str:>6} | {avg_comp:>9.2f}")

    print()

    # Identify transition boundaries
    print("TRANSITION WIDTH ANALYSIS:")
    print("-" * 80)

    # Find last 100% Basin B frequency
    last_b = None
    for frequency in FREQUENCIES:
        freq_results = [r for r in results if r['frequency'] == frequency]
        if all(r['basin'] == 'B' for r in freq_results):
            last_b = frequency

    # Find first 100% Basin A frequency
    first_a = None
    for frequency in FREQUENCIES:
        freq_results = [r for r in results if r['frequency'] == frequency]
        if all(r['basin'] == 'A' for r in freq_results):
            first_a = frequency
            break

    if last_b is not None and first_a is not None:
        transition_width = first_a - last_b
        print(f"Last 100% Basin B: {last_b:.2f}%")
        print(f"First 100% Basin A: {first_a:.2f}%")
        print(f"Transition width: {transition_width:.2f}%")
        print()

        if transition_width <= 0.01:
            print("✅ ULTRA-SHARP TRANSITION: Width ≤0.01% (single-step)")
        elif transition_width <= 0.05:
            print("✅ VERY SHARP TRANSITION: Width ≤0.05%")
        elif transition_width <= 0.10:
            print("✅ SHARP TRANSITION: Width ≤0.10% (validates C169)")
        else:
            print("⚠️  GRADUAL TRANSITION: Width >0.10%")
    else:
        print("⚠️  Could not determine clear transition boundaries")

    print()

    # Check for mixed-basin frequencies (most interesting finding)
    mixed_freqs = []
    for frequency in FREQUENCIES:
        freq_results = [r for r in results if r['frequency'] == frequency]
        basin_a_count = sum(1 for r in freq_results if r['basin'] == 'A')
        if 0 < basin_a_count < len(freq_results):
            mixed_freqs.append(frequency)

    if mixed_freqs:
        print("MIXED-BASIN FREQUENCIES (Critical Finding):")
        print("-" * 80)
        for freq in mixed_freqs:
            freq_results = [r for r in results if r['frequency'] == freq]
            basin_a_count = sum(1 for r in freq_results if r['basin'] == 'A')
            basin_a_pct = (basin_a_count / len(freq_results)) * 100
            print(f"  {freq:.2f}%: {basin_a_pct:.0f}% Basin A ({basin_a_count}/{len(freq_results)} runs)")
        print()
        print("⭐ Mixed basins indicate stochastic bistability at this frequency")
    else:
        print("No mixed-basin frequencies detected (transition <0.01%)")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '175',
            'scenario': 'High-Resolution Transition Mapping',
            'date': start_time.isoformat(),
            'frequencies': FREQUENCIES,
            'step_size': FREQUENCIES[1] - FREQUENCIES[0],
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'purpose': 'Address Frank\'s precision critique - measure exact transition width',
        },
        'experiments': results,
        'transition_analysis': {
            'last_100pct_basin_b': float(last_b) if last_b is not None else None,
            'first_100pct_basin_a': float(first_a) if first_a is not None else None,
            'transition_width': float(first_a - last_b) if (last_b is not None and first_a is not None) else None,
            'mixed_basin_frequencies': mixed_freqs,
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle177_extended_frequency_range.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 177 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
