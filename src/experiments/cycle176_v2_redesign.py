#!/usr/bin/env python3
"""
CYCLE 176 V2 REDESIGN

Purpose: Correct the spawn logic from previous C176 versions.
Strategy: Run BASELINE condition with the corrected spawn logic.
Expected: Population regulation purely through the energy-constrained mechanism.

Background:
  - C171 demonstrated population regulation via an energy constraint on spawning.
  - A bug in previous C176 implementations introduced an artificial population cap
    (`len(agents) < MAX_AGENTS`), which masked the true energy dynamics.
  - This version removes that artificial cap to restore the intended mechanism.

V2 Redesign:
  - REMOVED `len(agents) < MAX_AGENTS` check from the spawn condition.
  - Spawning is now only limited by parent energy and spawn interval.
  - This allows us to observe the true emergent population dynamics.

Date: 2025-11-18
Cycle: 176 V2 Redesign
Researcher: Gemini (DUALITY-ZERO-V2)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Gemini <noreply@google.com>
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine

# Parameters
FREQUENCY = 2.5
SEEDS = list(range(42, 62))  # n=20
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
# MAX_AGENTS = 100 # This is the bug, we are removing the check that uses it.

def run_c176_v2_redesign(frequency: float, seed: int, cycles: int) -> Dict:
    """
    Run C176 V2 with corrected spawn logic.
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
    spawn_success_count = 0
    population_trajectory = []

    # Calculate spawn interval
    spawn_interval = max(1, int(100.0 / frequency))

    # Composition engine
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Run cycles
    for cycle_idx in range(cycles):
        should_spawn = (cycle_idx % spawn_interval) == 0

        # CORRECTED LOGIC: Removed `and len(agents) < MAX_AGENTS`
        if should_spawn:
            spawn_count += 1

            parent = agents[np.random.randint(len(agents))]
            child_id = f"agent_{cycle_idx}_{spawn_count}"
            child = parent.spawn_child(child_id, energy_fraction=0.3)

            if child:
                agents.append(child)
                spawn_success_count += 1

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect clusters
        cluster_events = composition_engine.detect_clusters(agents)
        if cluster_events:
            for _ in cluster_events:
                composition_events.append(cycle_idx)

        population_trajectory.append(len(agents))

    # Calculate stats
    bins = np.arange(0, cycles + 1, WINDOW_SIZE)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0
    basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'
    final_population = len(agents)
    mean_population = float(np.mean(population_trajectory))
    std_population = float(np.std(population_trajectory))
    cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0.0
    spawn_success_rate = (spawn_success_count / spawn_count * 100) if spawn_count > 0 else 0.0

    return {
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_attempts': spawn_count,
        'spawn_successes': spawn_success_count,
        'spawn_success_rate': spawn_success_rate,
        'total_composition_events': len(composition_events),
        'final_agent_count': final_population,
        'mean_population': mean_population,
        'std_population': std_population,
        'cv_population': cv_population,
    }

def main():
    """Execute the C176 V2 Redesign experiment."""
    print("=" * 80)
    print("CYCLE 176 V2: REDESIGN EXPERIMENT")
    print("=" * 80)
    print("\nPurpose: Test population dynamics with corrected spawn logic.")
    print("Correction: Removed artificial `MAX_AGENTS` cap from spawn condition.\n")

    results = []
    start_time = datetime.now()

    for i, seed in enumerate(SEEDS, 1):
        result = run_c176_v2_redesign(FREQUENCY, seed, CYCLES)
        results.append(result)
        print(f"[{i:2d}/{len(SEEDS)}] Seed {seed:3d}: pop={result['mean_population']:5.1f}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80 + "\n")

    mean_pops = [r['mean_population'] for r in results]
    overall_mean_pop = np.mean(mean_pops)
    overall_std_pop = np.std(mean_pops)

    print("SUMMARY:")
    print(f"  Mean Population: {overall_mean_pop:.2f} ± {overall_std_pop:.2f} agents")
    print(f"  Population Range: [{min(mean_pops):.1f}, {max(mean_pops):.1f}] agents")

    output_data = {
        'metadata': {
            'cycle': '176',
            'version': 'V2_Redesign',
            'description': 'Population dynamics with corrected spawn logic (no MAX_AGENTS cap)',
            'date': start_time.isoformat(),
            'duration_minutes': duration,
        },
        'parameters': {
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'cycles': CYCLES,
        },
        'results': results,
        'summary': {
            'overall_mean_population': overall_mean_pop,
            'overall_std_population': overall_std_pop,
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle176_v2_redesign.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print(f"Duration: {duration:.2f} minutes\n")
    print("=" * 80)


if __name__ == "__main__":
    main()
