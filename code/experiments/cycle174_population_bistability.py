"""
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""


#!/usr/bin/env python3
"""
CYCLE 174: POPULATION-BASED BISTABILITY TEST

Purpose: Test if bistability exists at population level rather than composition-rate level

Background from C171:
  - FractalSwarm does NOT exhibit composition-rate bistability
  - Population saturates at ~17 agents regardless of spawn frequency
  - Hypothesis: Population ITSELF may be the bistable variable

Experimental Design:
  - Vary max_agents: [20, 50, 100, 200] (test population capacity effect)
  - Same frequencies as C171: [2.0, 2.5, 2.6, 3.0]
  - n=5 seeds per condition (reduced for speed)
  - Cycles: 3000 per experiment
  - Total: 4 max_agents × 4 frequencies × 5 seeds = 80 experiments

Expected Outcomes:
  IF population is bistable variable:
    - Low max_agents should show different saturation points by frequency
    - Bistability may emerge as bimodal population distribution

  IF homeostasis is universal:
    - All max_agents saturate to same ~17 agent equilibrium
    - No bistability at any scale

Publication Value: Tests alternative bistability hypothesis from C171 discovery
"""

import sys
from pathlib import Path
import time
import json
import numpy as np
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
MAX_AGENTS_VALUES = [20, 50, 100, 200]  # Test population capacity effect
FREQUENCIES = [2.0, 2.5, 2.6, 3.0]  # Same as C171 (integer percentages)
SEEDS = [42, 123, 456, 789, 101]  # n=5 for speed
CYCLES = 3000
WINDOW_SIZE = 100  # For measuring composition rate
BASIN_THRESHOLD = 2.5  # Same as C168-C171

def run_population_experiment(max_agents: int, frequency: float, seed: int, cycles: int) -> dict:
    """
    Run experiment with specified population capacity (matching C171 structure).

    Measures:
    - Final population (key metric for bistability hypothesis)
    - Population trajectory (for attractor analysis)
    - Composition events (for comparison with C171)
    """
    # Initialize components (matching C171)
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

    # Track population over time
    population_trajectory = []

    # Run cycles
    for cycle_idx in range(cycles):
        # Spawn new agent based on frequency
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < max_agents:  # KEY PARAMETER: max_agents
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

        # Track population every 100 cycles
        if cycle_idx % 100 == 0:
            population_trajectory.append(len(agents))

    # Calculate metrics
    final_population = len(agents)

    # Population statistics
    if len(population_trajectory) > 0:
        pop_mean = float(np.mean(population_trajectory))
        pop_std = float(np.std(population_trajectory))
        pop_min = int(np.min(population_trajectory))
        pop_max = int(np.max(population_trajectory))
    else:
        pop_mean = pop_std = pop_min = pop_max = 0

    # Composition rate (for comparison with C171)
    bins = np.arange(0, cycles + 1, WINDOW_SIZE)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification (composition-based, for comparison)
    comp_basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'

    # Population-based basin classification (HYPOTHESIS TEST)
    # Use median population as threshold
    # If populations are bistable, we'll see bimodal distribution
    pop_basin = 'HIGH' if final_population > pop_mean else 'LOW'

    return {
        'max_agents': max_agents,
        'frequency': frequency,
        'seed': seed,
        'final_population': final_population,
        'population_mean': pop_mean,
        'population_std': pop_std,
        'population_min': pop_min,
        'population_max': pop_max,
        'population_trajectory': population_trajectory,
        'avg_composition_events': avg_composition_events,
        'composition_basin': comp_basin,
        'population_basin': pop_basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
    }

def main():
    """Execute Cycle 174 experiments."""
    print("=" * 80)
    print("CYCLE 174: POPULATION-BASED BISTABILITY TEST")
    print("=" * 80)
    print()
    print("Hypothesis: Bistability exists at population level, not composition-rate level")
    print()
    print(f"Max Agents Values: {MAX_AGENTS_VALUES}")
    print(f"Frequencies: {[f'{f:.1%}' for f in FREQUENCIES]}")
    print(f"Seeds: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(MAX_AGENTS_VALUES) * len(FREQUENCIES) * len(SEEDS)}")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    exp_num = 0
    for max_agents in MAX_AGENTS_VALUES:
        print(f"Testing max_agents = {max_agents}")
        print("-" * 80)

        for frequency in FREQUENCIES:
            print(f"  Frequency: {frequency:.1%}")

            for seed in SEEDS:
                exp_num += 1

                result = run_population_experiment(max_agents, frequency, seed, CYCLES)
                results.append(result)

                print(f"    [{exp_num:2d}/{len(MAX_AGENTS_VALUES)*len(FREQUENCIES)*len(SEEDS)}] "
                      f"Seed {seed:3d}: pop={result['final_population']:3d}, "
                      f"comp={result['avg_composition_events']:.1f}, "
                      f"basin={result['population_basin']}")

        print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Analyze population distributions by max_agents and frequency
    print("POPULATION ANALYSIS:")
    print("-" * 80)
    print(f"{'Max Agents':>11} | {'Frequency':>10} | {'Pop Mean':>8} | {'Pop Std':>8} | {'Pop Range':>12} | {'Bimodal?':>9}")
    print("-" * 80)

    for max_agents in MAX_AGENTS_VALUES:
        for frequency in FREQUENCIES:
            freq_results = [r for r in results if r['max_agents'] == max_agents and r['frequency'] == frequency]
            pops = [r['final_population'] for r in freq_results]

            pop_mean = np.mean(pops)
            pop_std = np.std(pops)
            pop_range = f"{min(pops)}-{max(pops)}"

            # Test for bimodality using coefficient of variation
            cv = pop_std / pop_mean if pop_mean > 0 else 0
            bimodal = "YES" if cv > 0.5 else "no"

            print(f"{max_agents:>11} | {frequency:>9.1%} | {pop_mean:>8.1f} | {pop_std:>8.2f} | {pop_range:>12} | {bimodal:>9}")

    print()

    # Test hypothesis: Does max_agents affect population saturation?
    print("HYPOTHESIS TEST: Population Saturation vs Max Agents")
    print("-" * 80)

    for frequency in FREQUENCIES:
        print(f"Frequency {frequency:.1%}:")

        for max_agents in MAX_AGENTS_VALUES:
            freq_results = [r for r in results if r['max_agents'] == max_agents and r['frequency'] == frequency]
            avg_pop = np.mean([r['final_population'] for r in freq_results])
            saturation_pct = (avg_pop / max_agents) * 100

            print(f"  max_agents={max_agents:3d}: avg_pop={avg_pop:5.1f} ({saturation_pct:5.1f}% of capacity)")

        print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '174',
            'scenario': 'Population-Based Bistability Test',
            'date': start_time.isoformat(),
            'max_agents_values': MAX_AGENTS_VALUES,
            'frequencies': FREQUENCIES,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'hypothesis': 'Bistability exists at population level, not composition-rate',
        },
        'experiments': results,
        'analysis': {
            'population_distributions': {
                f"max_{ma}_freq_{freq}": {
                    'mean': float(np.mean([r['final_population'] for r in results if r['max_agents'] == ma and r['frequency'] == freq])),
                    'std': float(np.std([r['final_population'] for r in results if r['max_agents'] == ma and r['frequency'] == freq])),
                    'range': [
                        int(np.min([r['final_population'] for r in results if r['max_agents'] == ma and r['frequency'] == freq])),
                        int(np.max([r['final_population'] for r in results if r['max_agents'] == ma and r['frequency'] == freq]))
                    ]
                }
                for ma in MAX_AGENTS_VALUES
                for freq in FREQUENCIES
            }
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle174_population_bistability.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 174 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
