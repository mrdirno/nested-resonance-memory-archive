#!/usr/bin/env python3
"""
CYCLE 176 V6 BASELINE VALIDATION

Purpose: Validate energy-regulated population mechanism discovered in Cycle 891
Strategy: Run BASELINE condition only (exact C171 replication) with n=20 seeds
Expected: Mean population ~18-20 agents, CV < 15% (homeostatic)

Background:
  - C171: Population ~18-20 agents via ENERGY regulation, NOT agent removal
  - Mechanism: parent.spawn_child() fails when energy too low
  - CRITICAL: C171 NEVER removes agents on composition
  - Population control via failed spawning, not death

V6 Validation:
  - Match C171 exact spawn logic: parent.spawn_child(energy_fraction=0.3)
  - NO agent removal on composition (only count events)
  - Verify: 60 spawn attempts → 18-20 final agents via energy constraint

If validation passes → Proceed with full C176 V6 ablation study (6 conditions × 10 seeds)
If validation fails → Investigate mechanism further

Date: 2025-11-01
Cycle: 176 V6 Baseline Validation
Researcher: Claude (DUALITY-ZERO-V2)

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

# Validation parameters (match C171)
FREQUENCY = 2.5  # Midpoint of C171 homeostatic range (2.0%-3.0%)
SEEDS = list(range(42, 62))  # n=20 for robust statistics
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100

# Expected outcomes (from C171)
EXPECTED_MEAN_POP = 18.0  # C171 typical: 18-20 agents
EXPECTED_CV_THRESHOLD = 15.0  # Homeostatic if CV < 15%


def run_baseline_validation(frequency: float, seed: int, cycles: int) -> Dict:
    """
    Run BASELINE validation with V6 energy-regulated spawn logic.

    This exactly matches C171:
    - Spawn from random parent using parent.spawn_child(energy_fraction=0.3)
    - NO agent removal on composition (only count events)
    - Energy constraint naturally limits population

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

    # Initial agent (C171 line 84-90)
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
        # V6 spawn logic: Match C171 exact mechanism (C171 lines 133-141)
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < MAX_AGENTS:
            spawn_count += 1

            # Spawn from random parent (C171 exact implementation)
            parent = agents[np.random.randint(len(agents))]
            child_id = f"agent_{cycle_idx}_{spawn_count}"
            child = parent.spawn_child(child_id, energy_fraction=0.3)

            # Only add if spawn succeeded (energy-regulated)
            if child:
                agents.append(child)
                spawn_success_count += 1

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect clusters (composition events)
        cluster_events = composition_engine.detect_clusters(agents)

        # V6 FIX: C171 only COUNTS composition events, NEVER removes agents
        # (C171 lines 148-154)
        if cluster_events:
            for _ in cluster_events:
                composition_events.append(cycle_idx)

        # NO AGENT REMOVAL - population regulates via energy-constrained spawning

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

    # Spawn success rate (key metric for energy-regulated mechanism)
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
    """Execute C176 V6 baseline validation."""
    print("=" * 80)
    print("CYCLE 176 V6: BASELINE VALIDATION")
    print("=" * 80)
    print()
    print("Purpose: Validate energy-regulated population mechanism (Cycle 891 discovery)")
    print("Condition: BASELINE only (exact C171 replication)")
    print()
    print("Mechanism Tested:")
    print("  - parent.spawn_child() with energy_fraction=0.3")
    print("  - Spawn fails when parent energy too low")
    print("  - NO agent removal on composition")
    print("  - Population regulates via energy constraint")
    print()
    print(f"Frequency: {FREQUENCY}%")
    print(f"Seeds: n={len(SEEDS)}")
    print(f"Cycles: {CYCLES}")
    print()
    print(f"Expected Mean Population: ~{EXPECTED_MEAN_POP} agents")
    print(f"Expected CV: < {EXPECTED_CV_THRESHOLD}%")
    print(f"Expected Spawn Success Rate: ~30-35% (energy-constrained)")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    for i, seed in enumerate(SEEDS, 1):
        result = run_baseline_validation(FREQUENCY, seed, CYCLES)
        results.append(result)

        print(f"[{i:2d}/{len(SEEDS)}] "
              f"Seed {seed:3d}: "
              f"pop={result['mean_population']:5.1f} ± {result['std_population']:4.1f} "
              f"(CV={result['cv_population']:4.1f}%), "
              f"spawns={result['spawn_successes']}/{result['spawn_attempts']} "
              f"({result['spawn_success_rate']:4.1f}%), "
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
    spawn_rates = [r['spawn_success_rate'] for r in results]

    overall_mean_pop = np.mean(mean_pops)
    overall_std_pop = np.std(mean_pops)
    overall_mean_cv = np.mean(cvs)
    overall_mean_spawn_rate = np.mean(spawn_rates)

    print("STATISTICAL SUMMARY:")
    print("-" * 80)
    print(f"Mean Population: {overall_mean_pop:.2f} ± {overall_std_pop:.2f} agents")
    print(f"Mean CV: {overall_mean_cv:.2f}%")
    print(f"Mean Spawn Success Rate: {overall_mean_spawn_rate:.2f}%")
    print(f"Population Range: [{min(mean_pops):.1f}, {max(mean_pops):.1f}] agents")
    print()

    # Validation checks
    print("VALIDATION CHECKS:")
    print("-" * 80)

    # Check 1: Population near expected (18-20 agents)
    pop_check = 16.0 <= overall_mean_pop <= 22.0  # Allow ±2 from C171 range
    print(f"1. Population in expected range (16-22): {'✅ PASS' if pop_check else '❌ FAIL'}")
    print(f"   (Actual: {overall_mean_pop:.2f}, C171 typical: 18-20)")

    # Check 2: CV indicates homeostasis
    cv_check = overall_mean_cv < EXPECTED_CV_THRESHOLD
    print(f"2. CV indicates homeostasis (< {EXPECTED_CV_THRESHOLD}%): {'✅ PASS' if cv_check else '❌ FAIL'}")
    print(f"   (Actual: {overall_mean_cv:.2f}%)")

    # Check 3: Spawn success rate indicates energy constraint
    spawn_rate_check = 25.0 <= overall_mean_spawn_rate <= 45.0  # Expected ~30-35%
    print(f"3. Spawn success rate shows energy constraint (25-45%): {'✅ PASS' if spawn_rate_check else '❌ FAIL'}")
    print(f"   (Actual: {overall_mean_spawn_rate:.2f}%, indicates failed spawns due to low energy)")

    print()

    # Overall validation
    all_checks_pass = pop_check and cv_check and spawn_rate_check

    if all_checks_pass:
        print("✅ VALIDATION PASSED: Energy-regulated population mechanism confirmed!")
        print()
        print("Key Evidence:")
        print(f"  - Population homeostasis: {overall_mean_pop:.1f} agents (CV={overall_mean_cv:.1f}%)")
        print(f"  - Energy constraint: {overall_mean_spawn_rate:.1f}% spawn success")
        print(f"  - Mechanism: ~{100-overall_mean_spawn_rate:.0f}% spawns fail due to low parent energy")
        print()
        print("Next Steps:")
        print("  ✅ C176 V6 fundamental redesign validated")
        print("  → Proceed with full C176 V6 ablation study (6 conditions × 10 seeds)")
        print("  → Design conditions to test energy-regulated mechanism components")
    else:
        print("❌ VALIDATION FAILED: Mechanism doesn't match C171")
        print()
        print("Investigation Needed:")
        if not pop_check:
            print(f"  - Population {overall_mean_pop:.1f} outside expected range (16-22)")
        if not cv_check:
            print(f"  - CV {overall_mean_cv:.1f}% too high (homeostasis not achieved)")
        if not spawn_rate_check:
            print(f"  - Spawn success rate {overall_mean_spawn_rate:.1f}% unexpected")
        print()
        print("Next Steps:")
        print("  → Investigate spawn_child() energy mechanics")
        print("  → Compare with C171 source code in detail")
        print("  → Check if energy depletion from composition is working")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '176',
            'version': 'V6',
            'scenario': 'Baseline Validation - Energy-Regulated Population Mechanism',
            'date': start_time.isoformat(),
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'cycles_per_experiment': CYCLES,
            'duration_minutes': duration,
            'expected_mean_pop': EXPECTED_MEAN_POP,
            'expected_cv_threshold': EXPECTED_CV_THRESHOLD,
            'discovery_cycle': 891,
            'mechanism': 'energy-constrained spawning (parent.spawn_child with energy_fraction=0.3)',
        },
        'experiments': results,
        'validation': {
            'overall_mean_pop': overall_mean_pop,
            'overall_std_pop': overall_std_pop,
            'overall_mean_cv': overall_mean_cv,
            'overall_mean_spawn_rate': overall_mean_spawn_rate,
            'pop_check_passed': pop_check,
            'cv_check_passed': cv_check,
            'spawn_rate_check_passed': spawn_rate_check,
            'overall_passed': all_checks_pass,
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle176_v6_baseline_validation.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
