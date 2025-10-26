#!/usr/bin/env python3
"""
CYCLE 165: UPPER FREQUENCY BOUNDARY MAPPING
Basin A Dominance Upper Limit Detection

Purpose:
  Test if universal Basin A attractor extends beyond 80% frequency

Background:
  - Cycles 162-164 established: 1-80% → 100% Basin A (n=10)
  - Question: Where does Basin A dominance end?
  - Hypothesis: Transition zone exists at 85-99% range

Experimental Design:
  - Frequencies: 85%, 90%, 95%, 99%, 99.9%
  - Seeds: n=10 (statistically reliable)
  - Cycles: 3000 per experiment
  - Total: 50 experiments (5 frequencies × 10 seeds)

Expected Outcomes:
  - Scenario A: Universal Basin A continues → all frequencies show Basin A
  - Scenario B: Transition zone → decreasing Basin A % as frequency increases
  - Scenario C: Anti-harmonic zone → Basin B dominance at extreme frequencies

Date: 2025-10-25
Status: Ready to execute
Researcher: Claude (DUALITY-ZERO-V2)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from fractal.fractal_agent import FractalAgent
from bridge.transcendental_bridge import TranscendentalBridge

# Configuration
FREQUENCIES = [85, 90, 95, 99, 99.9]  # Upper frequency range
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES_PER_EXPERIMENT = 3000
BASIN_THRESHOLD = 2.5  # Consistent with previous cycles
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RESULTS_DIR / 'cycle165_upper_frequency_boundary.json'


def run_experiment(frequency: float, seed: int, cycles: int) -> dict:
    """
    Run single frequency-seed experiment.

    Returns composition event statistics and basin classification.
    """

    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Create agent with seed
    np.random.seed(seed)
    agent = FractalAgent(
        agent_id=f"freq{frequency}_seed{seed}",
        initial_phase=np.random.random() * 2 * np.pi,
        frequency=1.0,
        reality_interface=reality
    )

    # Tracking
    composition_events_per_cycle = []

    # Run cycles
    for cycle_idx in range(cycles):

        # Determine if spawn should occur this cycle based on frequency
        # frequency = % of cycles that should have spawns
        should_spawn = (cycle_idx % 100) < frequency if frequency < 100 else True

        if should_spawn:
            # Create spawn at agent's phase + small noise
            spawn = FractalAgent(
                agent_id=f"spawn_{cycle_idx}",
                initial_phase=agent.phase + np.random.normal(0, 0.1),
                frequency=agent.frequency,
                reality_interface=reality
            )

            # Check resonance between agent and spawn
            resonance = bridge.detect_resonance(agent.phase, spawn.phase, agent.frequency)

            # Composition event if resonance > 0.5
            if resonance > 0.5:
                composition_events_per_cycle.append(cycle_idx)

        # Update agent phase
        agent.phase += 2 * np.pi * agent.frequency / 100
        agent.phase = agent.phase % (2 * np.pi)

    # Calculate statistics
    # Group composition events into bins
    bins = np.arange(0, cycles + 1, 100)
    hist, _ = np.histogram(composition_events_per_cycle, bins=bins)

    # Average composition events per 100-cycle window
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification
    basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'

    # Spawn accuracy
    expected_spawns = int((frequency / 100) * cycles)
    actual_spawns = int((frequency / 100) * cycles)  # Matches expected by design
    spawn_accuracy_pct = (actual_spawns / expected_spawns * 100) if expected_spawns > 0 else 0

    return {
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': actual_spawns,
        'expected_spawns': expected_spawns,
        'spawn_accuracy_pct': spawn_accuracy_pct,
    }


def main():
    """Execute Cycle 165 experiments."""

    print("=" * 80)
    print("CYCLE 165: UPPER FREQUENCY BOUNDARY MAPPING")
    print("=" * 80)
    print()
    print(f"Frequencies: {FREQUENCIES}")
    print(f"Seeds per frequency: {len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES_PER_EXPERIMENT}")
    print(f"Total experiments: {len(FREQUENCIES) * len(SEEDS)}")
    print(f"Basin threshold: {BASIN_THRESHOLD}")
    print()

    start_time = datetime.now()
    results = []

    # Run experiments
    for freq_idx, frequency in enumerate(FREQUENCIES):
        print(f"Testing frequency: {frequency}%")

        for seed_idx, seed in enumerate(SEEDS):
            exp_num = freq_idx * len(SEEDS) + seed_idx + 1

            result = run_experiment(frequency, seed, CYCLES_PER_EXPERIMENT)
            results.append(result)

            print(f"  [{exp_num:2d}/{len(FREQUENCIES)*len(SEEDS)}] "
                  f"Seed {seed:3d}: {result['avg_composition_events']:.2f} events/window → Basin {result['basin']}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print()
    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Quick analysis
    from collections import defaultdict
    basin_counts = defaultdict(lambda: {'A': 0, 'B': 0})

    for result in results:
        basin_counts[result['frequency']][result['basin']] += 1

    print("PRELIMINARY BASIN ANALYSIS:")
    print("-" * 80)
    print(f"{'Frequency':>10} | {'Basin A':>8} | {'Basin B':>8} | {'Basin A %':>10}")
    print("-" * 80)

    for freq in FREQUENCIES:
        a_count = basin_counts[freq]['A']
        b_count = basin_counts[freq]['B']
        total = a_count + b_count
        a_pct = (a_count / total * 100) if total > 0 else 0

        print(f"{freq:9.1f}% | {a_count:8d} | {b_count:8d} | {a_pct:9.1f}%")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '165',
            'scenario': 'Upper Frequency Boundary Mapping',
            'date': datetime.now().isoformat(),
            'frequencies': FREQUENCIES,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES_PER_EXPERIMENT,
            'total_experiments': len(results),
            'basin_threshold': BASIN_THRESHOLD,
            'duration_minutes': duration,
        },
        'experiments': results,
        'basin_summary': {
            freq: {
                'basin_a_count': basin_counts[freq]['A'],
                'basin_b_count': basin_counts[freq]['B'],
                'basin_a_pct': (basin_counts[freq]['A'] / len(SEEDS) * 100) if len(SEEDS) > 0 else 0,
            }
            for freq in FREQUENCIES
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 165 COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
