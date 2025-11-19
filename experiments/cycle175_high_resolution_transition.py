#!/usr/bin/env python3
"""
CYCLE 175: HIGH-RESOLUTION TRANSITION MAPPING

Purpose: Measure actual width of bistable transition at 0.01% resolution

Background - Frank's Precision Critique:
  - Current claim: "Sharp transition width <0.1%"
  - Current data: 2.5% (0% Basin A) → 2.6% (100% Basin A) at 0.1% steps
  - Problem: Cannot claim <0.1% precision with 0.1% measurement steps
  - Resolution: Need 0.01% steps to validate sub-0.1% claim

Experimental Design:
  - Fine sweep around critical transition: 2.50% → 2.60%
  - Step size: 0.01% (10× finer than C169)
  - Frequencies: [2.50, 2.51, 2.52, ..., 2.60] (11 values)
  - Seeds: n=10 per frequency (same rigor as C171)
  - Cycles: 3000 per experiment
  - Total: 11 frequencies × 10 seeds = 110 experiments

Expected Outcomes:
  1. If transition width <0.01%:
     - Single frequency shows mixed basins (e.g., 60% A, 40% B)
     - Confirms ultra-sharp phase transition

  2. If transition width ~0.05%:
     - Gradual shift from 0% → 100% Basin A across 5 frequencies
     - Still sharp but not ultra-sharp

  3. If transition width ~0.1%:
     - Confirms current C169 findings
     - Validates original measurement resolution

Publication Value:
  - Addresses reviewer critique proactively
  - Demonstrates methodological rigor
  - Quantifies exact transition width (not upper bound)
  - Essential for peer review credibility

Date: 2025-10-25
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 175 (Following C171 population saturation discovery + Frank's critique)
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
FREQUENCIES = [2.50, 2.51, 2.52, 2.53, 2.54, 2.55, 2.56, 2.57, 2.58, 2.59, 2.60]  # 0.01% steps
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10 (match C171)
CYCLES = 3000
BASIN_THRESHOLD = 2.5  # Same as C168-C171
WINDOW_SIZE = 100
MAX_AGENTS = 100  # Same as C171

def run_high_res_experiment(frequency: float, seed: int, cycles: int) -> dict:
    """
    Run experiment at specified frequency (matching C171 structure).

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
        max_depth=7
    )

    # Track composition events (cluster formations)
    composition_events = []
    spawn_count = 0

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

            # Spawn from random existing agent
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

    # Calculate composition rate
    bins = np.arange(0, cycles + 1, WINDOW_SIZE)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification
    basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'

    # Final agent count (for comparison with C171 population saturation)
    final_agent_count = len(agents)

    return {
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': final_agent_count,
        'implementation': 'HighResolution'
    }

def main():
    """Execute Cycle 175 high-resolution transition mapping."""
    print("=" * 80)
    print("CYCLE 175: HIGH-RESOLUTION TRANSITION MAPPING")
    print("=" * 80)
    print()
    print("Purpose: Measure exact transition width at 0.01% resolution")
    print("Addresses: Frank's precision critique (claim <0.1% width with 0.1% steps)")
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

            result = run_high_res_experiment(frequency, seed, CYCLES)
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

    output_path = Path(__file__).parent / "results" / "cycle175_high_resolution_transition.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 175 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
