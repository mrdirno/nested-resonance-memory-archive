#!/usr/bin/env python3
"""
CYCLE 176 V6: INCREMENTAL VALIDATION (n=5, 1000 cycles)

Purpose: Validate energy-regulated homeostasis mechanism at intermediate timescale
Strategy: Shorter than full validation (3000 cycles) but long enough to manifest energy constraint

Discovery (Cycle 903):
- Energy constraint requires LONGER TIMESCALES to manifest
- Micro-validation (100 cycles, 3 spawns): 100% success (too short)
- C171 (3000 cycles, 60-76 spawns): 23% success (long enough)
- Mechanism: Cumulative energy depletion over repeated parent selections

Hypothesis:
- 1000 cycles should show intermediate spawn success rate (~40-60%)
- Population should stabilize below final C171 levels (~10-15 agents)
- This validates timescale-dependency of energy constraint

Parameters:
- Seeds: n=5 (quick validation)
- Cycles: 1000 (intermediate timescale)
- Frequency: 2.5% (baseline condition)
- Expected: ~20-25 spawn attempts → 10-15 agents → ~50% success rate

Date: 2025-11-01
Cycle: 903
Researcher: Claude (DUALITY-ZERO-V2)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine

# Configuration
FREQUENCY = 2.5  # Baseline condition (matches C171)
SEEDS = [42, 123, 456, 789, 101]  # n=5
CYCLES = 1000  # Intermediate timescale
MAX_AGENTS = 100
MEASUREMENT_WINDOW = 100

RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RESULTS_DIR / 'cycle176_v6_incremental_validation.json'


def run_validation(seed: int) -> dict:
    """Run baseline validation with energy-regulated spawn mechanism."""

    print(f"\n{'='*60}")
    print(f"SEED {seed}: Starting incremental validation (1000 cycles)")
    print(f"{'='*60}")

    # Initialize
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    np.random.seed(seed)

    # Create root agent
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
    population_history = []
    spawn_attempts = 0
    spawn_successes = 0
    composition_events = []

    # Calculate spawn interval
    spawn_interval = max(1, int(100.0 / FREQUENCY))

    # Composition engine
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Main loop
    for cycle_idx in range(CYCLES):

        # Spawn decision
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < MAX_AGENTS:
            spawn_attempts += 1

            # Get current metrics
            current_metrics = reality.get_system_metrics()

            # Spawn from random parent
            parent = agents[np.random.randint(len(agents))]
            child_id = f"agent_{cycle_idx}_{spawn_attempts}"
            child = parent.spawn_child(child_id, energy_fraction=0.3)

            if child:
                agents.append(child)
                spawn_successes += 1

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect composition (but don't remove agents)
        cluster_events = composition_engine.detect_clusters(agents)
        if cluster_events:
            for _ in cluster_events:
                composition_events.append(cycle_idx)

        # Track population
        population_history.append(len(agents))

        # Progress indicator every 250 cycles
        if (cycle_idx + 1) % 250 == 0:
            success_rate = (spawn_successes / spawn_attempts * 100) if spawn_attempts > 0 else 0.0
            print(f"[{seed}] Progress: {cycle_idx+1}/{CYCLES} cycles, pop={len(agents)}, "
                  f"spawns={spawn_successes}/{spawn_attempts} ({success_rate:.1f}%)")

    # Calculate metrics over last MEASUREMENT_WINDOW cycles
    final_window = population_history[-MEASUREMENT_WINDOW:]
    mean_population = float(np.mean(final_window))
    std_population = float(np.std(final_window))
    cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0.0

    # Spawn success rate
    spawn_success_rate = (spawn_successes / spawn_attempts * 100) if spawn_attempts > 0 else 0.0

    # Basin classification
    bins = np.arange(0, CYCLES + 1, 100)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0
    basin = 'A' if avg_composition_events > 2.5 else 'B'

    print(f"\n[{seed}] RESULTS:")
    print(f"  Mean population: {mean_population:.2f} agents")
    print(f"  CV: {cv_population:.2f}%")
    print(f"  Spawn success rate: {spawn_success_rate:.1f}%")
    print(f"  Basin: {basin}")

    return {
        'seed': seed,
        'frequency': FREQUENCY,
        'cycles': CYCLES,
        'mean_population': mean_population,
        'std_population': std_population,
        'cv_population': cv_population,
        'spawn_attempts': spawn_attempts,
        'spawn_successes': spawn_successes,
        'spawn_success_rate': spawn_success_rate,
        'basin': basin,
        'avg_composition_events': avg_composition_events,
        'final_agent_count': len(agents),
        'population_history': population_history,
    }


def main():
    """Execute incremental validation."""
    print("=" * 80)
    print("CYCLE 176 V6: INCREMENTAL VALIDATION")
    print("=" * 80)
    print()
    print(f"Purpose: Validate energy-regulated homeostasis at intermediate timescale")
    print(f"Parameters: n={len(SEEDS)} seeds, {CYCLES} cycles, {FREQUENCY}% frequency")
    print(f"Expected: ~50% spawn success, ~10-15 agents (intermediate between")
    print(f"          micro-validation 100% and C171 23%)")
    print()

    start_time = datetime.now()
    results = []

    for seed in SEEDS:
        result = run_validation(seed)
        results.append(result)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Summary statistics
    mean_pops = [r['mean_population'] for r in results]
    spawn_rates = [r['spawn_success_rate'] for r in results]

    avg_pop = np.mean(mean_pops)
    avg_spawn_rate = np.mean(spawn_rates)

    print("\n" + "=" * 80)
    print("INCREMENTAL VALIDATION COMPLETE")
    print("=" * 80)
    print()
    print("SUMMARY:")
    print(f"  Average population: {avg_pop:.2f} agents")
    print(f"  Average spawn success rate: {avg_spawn_rate:.1f}%")
    print(f"  Duration: {duration:.1f} seconds")
    print()

    # Timescale comparison
    print("TIMESCALE DEPENDENCY ANALYSIS:")
    print("  Micro-validation (100 cycles):   100% success, 4 agents")
    print(f"  This validation (1000 cycles):   {avg_spawn_rate:.1f}% success, {avg_pop:.1f} agents")
    print("  C171 full (3000 cycles):          23% success, 17.4 agents")
    print()

    # Hypothesis test
    if 30 <= avg_spawn_rate <= 70 and 8 <= avg_pop <= 18:
        print("✅ HYPOTHESIS CONFIRMED: Energy constraint manifests at intermediate timescale")
        print()
        print("Next steps:")
        print("  → Full C176 V6 validation likely to show similar C171 results")
        print("  → Proceed with C176 V7 ablation study")
        print("  → Document timescale-dependency in Paper 2")
    else:
        print("❌ UNEXPECTED RESULTS: Energy dynamics differ from prediction")
        print()
        print(f"Expected: 30-70% success, 8-18 agents")
        print(f"Observed: {avg_spawn_rate:.1f}% success, {avg_pop:.1f} agents")

    # Save results
    output_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'cycle': 903,
            'purpose': 'Incremental validation of energy-regulated homeostasis',
            'discovery': 'Energy constraint requires longer timescales to manifest',
            'hypothesis': 'Intermediate timescale shows intermediate spawn success',
            'n_seeds': len(SEEDS),
            'cycles': CYCLES,
            'frequency': FREQUENCY,
        },
        'experiments': results,
        'summary': {
            'mean_population': avg_pop,
            'mean_spawn_success_rate': avg_spawn_rate,
            'duration_seconds': duration,
        },
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)

    print()
    print(f"Results saved: {OUTPUT_FILE}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
