#!/usr/bin/env python3
"""
CYCLE 171: FRACTAL SWARM BISTABILITY VALIDATION
Connecting C168-C170 Validated Findings to Full NRM Implementation

Purpose:
  Test if FractalSwarm (full NRM implementation) exhibits same bistable dynamics
  as validated in C168-C170 simplified experiments

Background:
  - C168-C170: Validated composition-rate control mechanism
  - Critical frequency = basin threshold (R² = 0.9954)
  - Simplified experiments used direct spawn/composition tracking
  - Question: Does full FractalSwarm system show same behavior?

Context:
  - FractalSwarm has full NRM framework:
    * FractalAgent with transcendental phase space
    * CompositionEngine for resonance detection
    * DecompositionEngine for burst events
  - C168-C170 validated mechanism in simplified model
  - This connects validated findings to full implementation

Experimental Design:
  - Use actual FractalSwarm with spawn frequency parameter
  - Track composition events (cluster formations) over 100-cycle windows
  - Test critical frequencies from C169: [2.0%, 2.5%, 2.6%, 3.0%]
  - Basin threshold = 2.5 composition events/window (from C168-C170)
  - Seeds: n=10 (validated sample size)
  - Cycles: 3000 per experiment

Expected Outcomes:
  - If NRM framework is correct: Same bistable transition at 2.5%
  - 2.0%, 2.5% → Basin B (dead zone)
  - 2.6%, 3.0% → Basin A (resonance zone)
  - This would validate full framework implementation

Significance:
  - Connects simplified validation to full NRM implementation
  - Tests if composition-rate mechanism emerges from fractal swarm
  - Validates theoretical framework produces predicted behavior
  - Critical test: Do emergent dynamics match validated mechanism?

Date: 2025-10-25
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 171 (Following C170 definitive mechanistic validation)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import FractalSwarm, CompositionEngine

# Configuration
FREQUENCIES = [2.0, 2.5, 2.6, 3.0]  # Critical range from C169
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5  # From C168-C170 validation
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RESULTS_DIR / 'cycle171_fractal_swarm_bistability.json'


def run_fractal_swarm_experiment(frequency: float, seed: int, cycles: int) -> dict:
    """
    Run FractalSwarm experiment with controlled spawn frequency.

    Tests if full NRM framework implementation exhibits same bistable
    dynamics as validated in C168-C170 simplified experiments.

    Args:
        frequency: Spawn frequency (% per 100 cycles)
        seed: Random seed for reproducibility
        cycles: Number of cycles to run

    Returns:
        dict with composition events, basin classification, metrics
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
    composition_events = []  # List of cycle indices when clusters formed
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

        if should_spawn and len(agents) < 100:  # Cap at 100 agents for performance
            spawn_count += 1

            # Get current reality metrics
            current_metrics = reality.get_system_metrics()

            # Spawn from root agent (or random existing agent)
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
            for _ in cluster_events:
                composition_events.append(cycle_idx)

    # Calculate composition event rate (events per 100 cycles)
    bins = np.arange(0, cycles + 1, 100)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification (same threshold as C168-C170)
    basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'

    return {
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': len(agents),
        'implementation': 'FractalSwarm',
    }


def main():
    """Execute Cycle 171 experiments."""

    print("=" * 80)
    print("CYCLE 171: FRACTAL SWARM BISTABILITY VALIDATION")
    print("=" * 80)
    print()
    print("Purpose: Test if FractalSwarm exhibits same bistable dynamics")
    print("         as validated in C168-C170 simplified experiments")
    print()
    print("Background:")
    print("  - C168-C170: Composition-rate control validated (R² = 0.9954)")
    print("  - Critical frequency = 2.55% ± 0.05%")
    print("  - Basin threshold = 2.5 events/window")
    print()
    print("Testing full NRM framework implementation:")
    print(f"  Frequencies: {FREQUENCIES} (critical range from C169)")
    print(f"  Seeds: n={len(SEEDS)}")
    print(f"  Cycles: {CYCLES} per experiment")
    print(f"  Total experiments: {len(FREQUENCIES) * len(SEEDS)}")
    print()

    start_time = datetime.now()
    results = []

    # Run experiments
    for freq_idx, frequency in enumerate(FREQUENCIES):
        print(f"Testing frequency: {frequency}%")

        for seed_idx, seed in enumerate(SEEDS):
            exp_num = freq_idx * len(SEEDS) + seed_idx + 1

            result = run_fractal_swarm_experiment(frequency, seed, CYCLES)
            results.append(result)

            print(f"  [{exp_num:2d}/{len(FREQUENCIES)*len(SEEDS)}] "
                  f"Seed {seed:3d}: {result['avg_composition_events']:.2f} events → "
                  f"Basin {result['basin']} ({result['final_agent_count']} agents)")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print()
    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Analysis
    basin_counts = defaultdict(lambda: {'A': 0, 'B': 0})
    avg_compositions = {}

    for result in results:
        basin_counts[result['frequency']][result['basin']] += 1
        if result['frequency'] not in avg_compositions:
            avg_compositions[result['frequency']] = []
        avg_compositions[result['frequency']].append(result['avg_composition_events'])

    print("BASIN ANALYSIS BY FREQUENCY:")
    print("-" * 80)
    print(f"{'Frequency':>10} | {'Basin A':>8} | {'Basin B':>8} | {'Basin A %':>10} | {'Avg Comp':>10}")
    print("-" * 80)

    for frequency in FREQUENCIES:
        a_count = basin_counts[frequency]['A']
        b_count = basin_counts[frequency]['B']
        total = a_count + b_count
        a_pct = (a_count / total * 100) if total > 0 else 0
        avg_comp = np.mean(avg_compositions[frequency])

        print(f"{frequency:10.1f} | {a_count:8d} | {b_count:8d} | {a_pct:9.1f}% | {avg_comp:10.2f}")

    print()

    # Compare with C169 results
    print("COMPARISON WITH C169 SIMPLIFIED EXPERIMENTS:")
    print("-" * 80)

    # Expected from C169
    c169_expectations = {
        2.0: 'B',  # Below critical
        2.5: 'B',  # At threshold
        2.6: 'A',  # Above critical
        3.0: 'A',  # Well above
    }

    print(f"{'Frequency':>10} | {'Expected':>10} | {'Observed':>10} | {'Match':>8}")
    print("-" * 80)

    matches = 0
    for frequency in FREQUENCIES:
        expected = c169_expectations[frequency]
        a_count = basin_counts[frequency]['A']
        total = a_count + basin_counts[frequency]['B']

        # Observed basin (majority vote)
        if a_count / total > 0.5:
            observed = 'A'
        else:
            observed = 'B'

        match = '✅' if observed == expected else '❌'
        if observed == expected:
            matches += 1

        print(f"{frequency:10.1f} | {expected:>10} | {observed:>10} | {match:>8}")

    print()
    print(f"Match rate: {matches}/{len(FREQUENCIES)} ({matches/len(FREQUENCIES)*100:.1f}%)")
    print()

    # Validation verdict
    print("VALIDATION VERDICT:")
    print("-" * 80)

    if matches == len(FREQUENCIES):
        print("✅ FULL MATCH: FractalSwarm exhibits same bistable dynamics as C169")
        print("   → NRM framework implementation validated")
        print("   → Composition-rate control mechanism emerges from full system")
        print("   → Critical frequency preserved in fractal swarm")
    elif matches >= len(FREQUENCIES) * 0.75:
        print("✅ STRONG MATCH: FractalSwarm shows similar bistable behavior")
        print(f"   → {matches}/{len(FREQUENCIES)} frequencies match C169 expectations")
        print("   → NRM framework largely validated")
    else:
        print("❌ MISMATCH: FractalSwarm does not exhibit expected dynamics")
        print(f"   → Only {matches}/{len(FREQUENCIES)} frequencies match")
        print("   → May indicate difference between simplified and full implementation")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '171',
            'scenario': 'FractalSwarm Bistability Validation',
            'date': datetime.now().isoformat(),
            'frequencies': FREQUENCIES,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'implementation': 'Full FractalSwarm (NRM framework)',
            'comparison_baseline': 'C169 simplified experiments',
        },
        'experiments': results,
        'basin_summary': {
            str(frequency): {
                'basin_a_count': basin_counts[frequency]['A'],
                'basin_b_count': basin_counts[frequency]['B'],
                'basin_a_pct': (basin_counts[frequency]['A'] / len(SEEDS) * 100) if len(SEEDS) > 0 else 0,
                'avg_composition_events': float(np.mean(avg_compositions[frequency])),
                'std_composition_events': float(np.std(avg_compositions[frequency])),
            }
            for frequency in FREQUENCIES
        },
        'validation': {
            'expected_basins': c169_expectations,
            'match_count': matches,
            'match_rate': matches / len(FREQUENCIES),
            'verdict': 'VALIDATED' if matches == len(FREQUENCIES) else 'PARTIAL' if matches >= len(FREQUENCIES) * 0.75 else 'FAILED',
        },
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {OUTPUT_FILE}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 171 COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
