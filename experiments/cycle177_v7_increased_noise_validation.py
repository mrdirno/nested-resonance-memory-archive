#!/usr/bin/env python3
"""
CYCLE 177 V7: MEASUREMENT NOISE VALIDATION (STOCHASTICITY FRAMEWORK V6)

Purpose: Validate that V6 measurement noise framework produces statistical
         variation while maintaining reality grounding.

Background:
  - Cycle 235: V5 added initial_energy perturbation (±5.0 units)
  - Cycle 243 Diagnostic: V5 FAILED - reality-based recharge overwhelms perturbations
    → Initial energies: std=1.89 → Final energies (100 cycles): std=0.0
    → Complete determinism despite seed control

  Root Cause: Energy recharge (~1.8/cycle) is deterministic, derived from stable
              reality metrics (CPU ~1.6%, Mem ~78.2%). After ~3 cycles, recharge
              accumulation > initial perturbation, leading to convergence.

V6 Solution: Add measurement noise to reality metric sampling
  - Represents natural variation in system monitoring (realistic)
  - Propagates through energy recharge calculations (persistent effect)
  - Maintains reality anchoring (values still come from actual system)
  - Provides statistical validity (different seeds → different trajectories)

Framework Enhancement:
  - FractalAgent.__init__(measurement_noise_std): Optional noise parameter
  - FractalAgent.evolve(): Apply proportional Gaussian noise to CPU/memory metrics
  - Noise std = measurement_noise_std × metric_value (proportional)
  - Typical values: 0.01-0.05 (1-5% noise)

Validation Criteria:
  1. Initial energies differ between seeds (σ² > 0) ✓ (V5 achieved this)
  2. Final energies differ between seeds (σ² > 0) ✗ (V5 failed, V6 should fix)
  3. Population means differ between seeds (σ² > 0) ← KEY VALIDATION
  4. Cohen's d computable (nonzero variance) ← STATISTICAL VALIDITY
  5. Reality grounding maintained (values bounded [0, 100]) ← COMPLIANCE

Expected Outcomes:
  - With noise_std=0.03 (3% noise):
    → Population mean std > 0.5 (detectable variation)
    → Cohen's d computable (variance allows effect size)
    → Different seeds produce different trajectories

Date: 2025-10-26
Cycle: 244
Principal Investigator: Aldrin Payopay
"""

import sys
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
import copy

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine, FractalSwarm

# Experimental parameters
FREQUENCY = 2.5  # Spawn frequency (%)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100
SPAWN_THRESHOLD = 10.0
ENERGY_RECHARGE_RATE = 0.010  # Already in FractalAgent.evolve()
SHARING_FRACTION = 0.10
MEASUREMENT_NOISE_STD = 0.10  # V7: 10% proportional noise on reality metrics


class EnergyPoolingCondition:
    """Condition wrapper for energy pooling experiments."""

    def __init__(self, name: str, pooling_enabled: bool):
        self.name = name
        self.pooling_enabled = pooling_enabled

    def __repr__(self):
        return f"EnergyPoolingCondition({self.name}, pooling={self.pooling_enabled})"


def run_single_experiment(
    condition: EnergyPoolingCondition,
    frequency: float,
    seed: int,
    cycles: int,
    measurement_noise_std: float
) -> Dict:
    """
    Run single V6 experiment with measurement noise.

    Args:
        condition: Experimental condition
        frequency: Spawn frequency (%)
        seed: Random seed
        cycles: Number of evolution cycles
        measurement_noise_std: Std dev for measurement noise (proportional)

    Returns:
        Dictionary with results
    """
    np.random.seed(seed)

    # Initialize
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine(resonance_threshold=0.85)

    # Spawn root agent with V6 framework
    metrics = reality.get_system_metrics()

    # V5: Initial energy perturbation (still included for comparison)
    base_energy = 130.0
    energy_perturbation = np.random.uniform(-5.0, 5.0)
    initial_energy = base_energy + energy_perturbation

    # V7: Add measurement noise parameter
    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality,
        initial_energy=initial_energy,  # V5 feature
        measurement_noise_std=measurement_noise_std  # V6 ENHANCEMENT
    )

    agents = [root]
    spawn_interval = int(100 / frequency) if frequency > 0 else float('inf')

    # Tracking
    spawn_count = 0
    composition_events = []
    population_history = []
    energy_pooling_stats = {
        'total_pools_formed': 0,
        'total_energy_pooled': 0.0,
        'total_energy_distributed': 0.0
    } if condition.pooling_enabled else None

    # Evolution loop
    for cycle_idx in range(cycles):
        # 1. Spawn check
        if cycle_idx % spawn_interval == 0 and cycle_idx > 0:
            if len(agents) < MAX_AGENTS and root.energy >= SPAWN_THRESHOLD:
                child_id = f"agent_{spawn_count:04d}"
                child = root.spawn_child(child_id=child_id, energy_fraction=0.30)
                if child is not None:
                    agents.append(child)
                    spawn_count += 1

        # 2. Energy pooling (POOLING condition only)
        if condition.pooling_enabled:
            for agent in agents:
                agent.cluster_id = None

            cluster_events = composition_engine.detect_clusters(agents)

            for cluster_id, member_ids in composition_engine.clusters.items():
                for agent in agents:
                    if agent.agent_id in member_ids:
                        agent.cluster_id = cluster_id

            pools_formed = 0
            energy_pooled = 0.0
            energy_distributed = 0.0

            for cluster_id, member_ids in composition_engine.clusters.items():
                if len(member_ids) < 2:
                    continue

                cluster_agents = [a for a in agents if a.agent_id in member_ids]

                pool_energy = 0.0
                for agent in cluster_agents:
                    contribution = agent.contribute_to_pool(SHARING_FRACTION)
                    pool_energy += contribution
                    energy_pooled += contribution

                sorted_agents = sorted(cluster_agents, key=lambda a: a.energy)
                for agent in sorted_agents:
                    if pool_energy <= 0:
                        break
                    received = agent.receive_from_pool(pool_energy, SPAWN_THRESHOLD)
                    pool_energy -= received
                    energy_distributed += received

                pools_formed += 1

            energy_pooling_stats['total_pools_formed'] += pools_formed
            energy_pooling_stats['total_energy_pooled'] += energy_pooled
            energy_pooling_stats['total_energy_distributed'] += energy_distributed

        # 3. Agent evolution (V6 measurement noise applied in evolve())
        for agent in agents:
            agent.evolve(delta_time=1.0)

        # 4. Composition detection (death)
        cluster_events = composition_engine.detect_clusters(agents)

        if cluster_events:
            composition_events.append(cycle_idx)

            agents_to_remove_ids = set()
            for cluster_event in cluster_events:
                for agent_id in cluster_event.agent_ids:
                    agents_to_remove_ids.add(agent_id)

            agents = [a for a in agents if a.agent_id not in agents_to_remove_ids]

        # 5. Track population
        population_history.append(len(agents))

    # Compute statistics
    population_array = np.array(population_history)
    mean_population = np.mean(population_array)
    std_population = np.std(population_array)
    cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0

    # Basin classification
    basin = "B" if mean_population < BASIN_THRESHOLD else "A"

    result = {
        'condition': condition.name,
        'pooling_enabled': condition.pooling_enabled,
        'frequency': frequency,
        'seed': seed,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': len(agents),
        'mean_population': mean_population,
        'std_population': std_population,
        'cv_population': cv_population,
        'avg_composition_events': len(composition_events) / cycles,
        'basin': basin,
        'window_size': WINDOW_SIZE,
        'measurement_noise_std': measurement_noise_std,  # V6 metadata
        'initial_energy_perturbation': energy_perturbation  # V5 metadata
    }

    if condition.pooling_enabled:
        result['pooling_stats'] = energy_pooling_stats
        result['pooling_stats']['avg_pools_per_cycle'] = \
            energy_pooling_stats['total_pools_formed'] / cycles
        result['pooling_stats']['energy_conservation_check'] = \
            abs(energy_pooling_stats['total_energy_pooled'] -
                energy_pooling_stats['total_energy_distributed']) < 1.0

    return result


def main():
    """Run V6 validation experiment."""
    start_time = time.time()

    print("=" * 70)
    print("CYCLE 177 V7: MEASUREMENT NOISE VALIDATION")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Seeds: {len(SEEDS)} (n=10)")
    print(f"Cycles: {CYCLES:,}")
    print(f"Measurement noise std: {MEASUREMENT_NOISE_STD} (10% proportional)")
    print()

    conditions = [
        EnergyPoolingCondition("BASELINE", pooling_enabled=False),
        EnergyPoolingCondition("POOLING", pooling_enabled=True)
    ]

    results = []

    for condition in conditions:
        print(f"\nCondition: {condition.name}")
        print("-" * 70)

        for seed_idx, seed in enumerate(SEEDS, 1):
            print(f"  [{seed_idx}/{len(SEEDS)}] Seed {seed}... ", end="", flush=True)

            result = run_single_experiment(
                condition=condition,
                frequency=FREQUENCY,
                seed=seed,
                cycles=CYCLES,
                measurement_noise_std=MEASUREMENT_NOISE_STD
            )

            results.append(result)
            print(f"mean={result['mean_population']:.2f}, basin={result['basin']}")

    # Statistical summary
    print("\n" + "=" * 70)
    print("STATISTICAL SUMMARY")
    print("=" * 70)

    baseline_means = [r['mean_population'] for r in results if r['condition'] == 'BASELINE']
    pooling_means = [r['mean_population'] for r in results if r['condition'] == 'POOLING']

    baseline_mean = np.mean(baseline_means)
    baseline_std = np.std(baseline_means)
    pooling_mean = np.mean(pooling_means)
    pooling_std = np.std(pooling_means)

    print(f"\nBASELINE (n={len(baseline_means)}):")
    print(f"  Mean population: {baseline_mean:.4f} ± {baseline_std:.4f}")
    print(f"  Range: [{np.min(baseline_means):.4f}, {np.max(baseline_means):.4f}]")

    print(f"\nPOOLING (n={len(pooling_means)}):")
    print(f"  Mean population: {pooling_mean:.4f} ± {pooling_std:.4f}")
    print(f"  Range: [{np.min(pooling_means):.4f}, {np.max(pooling_means):.4f}]")

    # V6 VALIDATION: Check if variance exists
    print("\n" + "=" * 70)
    print("V6 VALIDATION RESULTS")
    print("=" * 70)

    baseline_has_variance = baseline_std > 0.01
    pooling_has_variance = pooling_std > 0.01

    print(f"\nBaseline std: {baseline_std:.4f} → Variance exists: {baseline_has_variance}")
    print(f"Pooling std:  {pooling_std:.4f} → Variance exists: {pooling_has_variance}")

    if baseline_has_variance and pooling_has_variance:
        # Compute Cohen's d
        pooled_std = np.sqrt((baseline_std**2 + pooling_std**2) / 2)
        cohens_d = (pooling_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0.0

        print(f"\n✓ V6 SUCCESS: Variance detected in both conditions!")
        print(f"  Cohen's d = {cohens_d:.4f} (computable)")
        print(f"  Statistical validity: ACHIEVED")

        hypothesis_outcome = "CONFIRMED" if cohens_d > 0.8 else "PARTIAL" if cohens_d > 0.2 else "REJECTED"
    else:
        cohens_d = 0.0
        print(f"\n✗ V6 FAILURE: Insufficient variance")
        print(f"  Cohen's d = 0.0 (not computable)")
        print(f"  Statistical validity: FAILED")
        hypothesis_outcome = "REJECTED"

    print(f"\nHypothesis outcome: {hypothesis_outcome}")

    # Save results
    duration_minutes = (time.time() - start_time) / 60

    output = {
        'metadata': {
            'cycle': '177 V6',
            'hypothesis': 'H1 - Energy Pooling (V6 Measurement Noise Framework)',
            'date': datetime.now().isoformat(),
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration_minutes,
            'sharing_fraction': SHARING_FRACTION,
            'spawn_threshold': SPAWN_THRESHOLD,
            'energy_recharge_rate': ENERGY_RECHARGE_RATE,
            'measurement_noise_std': MEASUREMENT_NOISE_STD
        },
        'experiments': results,
        'statistical_summary': {
            'baseline_mean_population': baseline_mean,
            'baseline_std_population': baseline_std,
            'baseline_mean_cv': np.mean([r['cv_population'] for r in results if r['condition'] == 'BASELINE']),
            'pooling_mean_population': pooling_mean,
            'pooling_std_population': pooling_std,
            'pooling_mean_cv': np.mean([r['cv_population'] for r in results if r['condition'] == 'POOLING']),
            'cohens_d': cohens_d,
            'hypothesis_outcome': hypothesis_outcome,
            'v6_validation_passed': baseline_has_variance and pooling_has_variance
        }
    }

    output_path = Path(__file__).parent / "results" / "cycle177_v7_measurement_noise_validation_results.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n" + "=" * 70)
    print(f"Duration: {duration_minutes:.2f} minutes")
    print(f"Results saved to: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
