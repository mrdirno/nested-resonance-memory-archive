#!/usr/bin/env python3
"""
C176 V6: FULL BASELINE VALIDATION (Post-Incremental)

Purpose: Full-scale validation of energy-regulated population homeostasis with
         revised non-monotonic timescale understanding (Cycle 907-908).

Background:
- Cycle 891: Energy-regulated spawning mechanism discovered
- Cycle 903: Timescale dependency identified (cumulative depletion)
- Cycle 907: Non-monotonic pattern observed (population-mediated recovery)
- Cycle 908: Incremental validation analysis (spawns/agent threshold)

Hypothesis (Revised):
At 3000 cycles, cumulative energy depletion should dominate population-mediated
recovery, replicating C171 results despite non-monotonic intermediate behavior.

Expected Results:
- Spawn success: 20-25% (replicates C171 mean 23.4%)
- Population: 17-18 agents (replicates C171 mean 17.43)
- Spawns/agent: 7-9 (above 4 threshold for low success)
- CV population: < 15% (homeostatic stability)

Comparison:
- vs. Micro (100 cycles): 100% success, 4 agents, 0.75 spawns/agent
- vs. Incremental (1000 cycles): ~75-85% success, 18-20 agents, <2 spawns/agent
- vs. C171 (3000 cycles): 23% success, 17.43 agents, 8.38 spawns/agent

Parameters:
- Seeds: n=20 (statistical rigor)
- Cycles: 3000 (full timescale for energy constraint manifestation)
- Frequency: 2.5% (spawn every 40 cycles, ~75 total attempts)
- Max agents: 100
- Implementation: Full NRM framework (birth-death enabled)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-01
Cycle: 908
"""

import sys
import json
import random
import numpy as np
from pathlib import Path
from datetime import datetime

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "code"))

from fractal.fractal_agent import FractalAgent
from reality.system_monitor import SystemMonitor


# Validation parameters
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606,
         707, 808, 909, 1010, 1111, 1212, 1313, 1414, 1515, 1616]  # n=20
CYCLES = 3000
SPAWN_FREQUENCY = 0.025  # 2.5% (spawn every 40 cycles)
MAX_AGENTS = 100

# Expected outcomes (for validation)
EXPECTED_SPAWN_SUCCESS = 23.0  # % (C171 baseline)
EXPECTED_POPULATION = 17.43  # agents (C171 baseline)
EXPECTED_CV = 15.0  # % (homeostatic threshold)


def run_validation_experiment(seed, cycles, spawn_frequency, max_agents):
    """
    Run single validation experiment with given seed.

    Returns dict with results including trajectory data for visualization.
    """
    random.seed(seed)
    np.random.seed(seed)

    print(f"[{seed}] Starting full validation ({cycles} cycles)")

    # Initialize fractal swarm
    agents = [FractalAgent(agent_id=0, energy=100.0)]
    spawn_attempts = 0
    spawn_successes = 0

    # Trajectory tracking (for visualization and analysis)
    trajectory = {
        'cycles': [],
        'populations': [],
        'spawn_attempts': [],
        'spawn_success_rates': [],
    }

    # Run simulation
    for cycle in range(cycles):
        # Update all agents
        for agent in agents:
            agent.update(delta_time=0.1)

        # Spawn attempt
        if random.random() < spawn_frequency and len(agents) < max_agents:
            spawn_attempts += 1

            # Select random parent
            parent = random.choice(agents)

            # Attempt spawn
            child = parent.spawn_child(energy_fraction=0.3)

            if child is not None:
                spawn_successes += 1
                agents.append(child)

        # Track trajectory (every 250 cycles)
        if cycle % 250 == 0 or cycle == cycles - 1:
            success_rate = (spawn_successes / spawn_attempts * 100) if spawn_attempts > 0 else 0.0
            trajectory['cycles'].append(cycle)
            trajectory['populations'].append(len(agents))
            trajectory['spawn_attempts'].append(spawn_attempts)
            trajectory['spawn_success_rates'].append(success_rate)

            print(f"[{seed}] Progress: {cycle}/{cycles} cycles, "
                  f"pop={len(agents)}, "
                  f"spawns={spawn_successes}/{spawn_attempts} ({success_rate:.1f}%)")

    # Final metrics
    final_population = len(agents)
    spawn_success_rate = (spawn_successes / spawn_attempts * 100) if spawn_attempts > 0 else 0.0

    # Estimate spawns/agent (rough approximation)
    avg_population = (1 + final_population) / 2
    spawns_per_agent = spawn_attempts / avg_population

    print(f"[{seed}] Complete: pop={final_population}, "
          f"spawns={spawn_successes}/{spawn_attempts} ({spawn_success_rate:.1f}%), "
          f"spawns/agent={spawns_per_agent:.2f}")
    print()

    return {
        'seed': seed,
        'final_population': final_population,
        'spawn_attempts': spawn_attempts,
        'spawn_successes': spawn_successes,
        'spawn_success_rate': spawn_success_rate,
        'spawns_per_agent': spawns_per_agent,
        'trajectory': trajectory,
    }


def main():
    """Execute C176 V6 full baseline validation."""
    print("=" * 80)
    print("C176 V6: FULL BASELINE VALIDATION")
    print("=" * 80)
    print()
    print("Hypothesis: Energy-regulated spawning produces homeostatic population")
    print("           at long timescales despite non-monotonic intermediate behavior")
    print()
    print(f"Parameters:")
    print(f"  Seeds: n={len(SEEDS)}")
    print(f"  Cycles: {CYCLES}")
    print(f"  Spawn frequency: {SPAWN_FREQUENCY * 100}%")
    print(f"  Max agents: {MAX_AGENTS}")
    print()

    start_time = datetime.now()

    # Run experiments
    results = []

    for seed in SEEDS:
        result = run_validation_experiment(
            seed=seed,
            cycles=CYCLES,
            spawn_frequency=SPAWN_FREQUENCY,
            max_agents=MAX_AGENTS
        )
        results.append(result)

    # Calculate overall statistics
    spawn_success_rates = [r['spawn_success_rate'] for r in results]
    final_populations = [r['final_population'] for r in results]
    spawns_per_agent = [r['spawns_per_agent'] for r in results]

    mean_success = np.mean(spawn_success_rates)
    std_success = np.std(spawn_success_rates)
    mean_population = np.mean(final_populations)
    std_population = np.std(final_populations)
    cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0.0
    mean_spawns_per_agent = np.mean(spawns_per_agent)
    std_spawns_per_agent = np.std(spawns_per_agent)

    # Print summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    print(f"Spawn Success Rate:")
    print(f"  Mean: {mean_success:.1f}% ± {std_success:.1f}%")
    print(f"  Range: [{min(spawn_success_rates):.1f}%, {max(spawn_success_rates):.1f}%]")
    print(f"  Expected (C171): {EXPECTED_SPAWN_SUCCESS:.1f}%")
    print(f"  Match: {'✅ CLOSE' if abs(mean_success - EXPECTED_SPAWN_SUCCESS) < 5 else '❌ DIFFERENT'}")
    print()
    print(f"Final Population:")
    print(f"  Mean: {mean_population:.1f} ± {std_population:.1f} agents")
    print(f"  CV: {cv_population:.1f}%")
    print(f"  Range: [{min(final_populations)}, {max(final_populations)}]")
    print(f"  Expected (C171): {EXPECTED_POPULATION:.1f} agents")
    print(f"  Match: {'✅ CLOSE' if abs(mean_population - EXPECTED_POPULATION) < 2 else '❌ DIFFERENT'}")
    print(f"  Homeostatic: {'✅ YES (CV < 15%)' if cv_population < EXPECTED_CV else '❌ NO (CV >= 15%)'}")
    print()
    print(f"Spawns Per Agent:")
    print(f"  Mean: {mean_spawns_per_agent:.2f} ± {std_spawns_per_agent:.2f}")
    print(f"  Range: [{min(spawns_per_agent):.2f}, {max(spawns_per_agent):.2f}]")
    print(f"  Threshold: {'✅ ABOVE 4 (low success expected)' if mean_spawns_per_agent > 4 else '⚠️ BELOW 4'}")
    print()

    # Save results
    end_time = datetime.now()
    duration_minutes = (end_time - start_time).total_seconds() / 60

    output_data = {
        'metadata': {
            'cycle': '176_V6',
            'scenario': 'Full Baseline Validation',
            'date': start_time.isoformat(),
            'duration_minutes': duration_minutes,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'spawn_frequency': SPAWN_FREQUENCY,
            'total_experiments': len(SEEDS),
            'implementation': 'Full NRM framework (energy-regulated spawning)',
        },
        'experiments': results,
        'summary': {
            'mean_spawn_success': mean_success,
            'std_spawn_success': std_success,
            'mean_population': mean_population,
            'std_population': std_population,
            'cv_population': cv_population,
            'mean_spawns_per_agent': mean_spawns_per_agent,
            'std_spawns_per_agent': std_spawns_per_agent,
        },
    }

    output_file = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle176_v6_full_validation.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_file}")
    print(f"Runtime: {duration_minutes:.1f} minutes ({duration_minutes / 60:.2f} hours)")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
