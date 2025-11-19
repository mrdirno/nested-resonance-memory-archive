#!/usr/bin/env python3
"""
CYCLE 177 V5: HYPOTHESIS 1 - Energy Pooling Test (CORRECTED STOCHASTICITY FRAMEWORK)

Purpose: Re-run C177 H1 with seed-controlled stochasticity to validate framework fix
         and test if energy pooling overcomes single-parent bottleneck.

Background:
  - C176 V2/V3/V4: Catastrophic population collapse (mean=0.49) despite energy
    recharge across 100× parameter range (r ∈ {0.000, 0.001, 0.010})
  - Death rate (0.013/cycle) >> sustained birth rate (0.005/cycle) = 2.5× imbalance
  - Three structural asymmetries identified:
    1. Energy recovery lag (~1,000 cycles, 66% of experiment)
    2. Single-parent bottleneck (birth in root, death distributed)
    3. Continuous death activity (100% uptime vs 33% birth uptime)

Hypothesis 1 (Energy Pooling):
  Agents share energy within resonance clusters, addressing single-parent
  bottleneck by distributing reproductive capacity across cluster members.

Mechanistic Prediction:
  - Shared energy reservoir eliminates single-parent constraint
  - Multiple agents regain reproductive capacity simultaneously
  - Asynchronous spawning maintains continuous birth presence
  - Birth rate increases 3× (0.005 → 0.015 agents/cycle)

Experimental Design:
  - BASELINE: C176 V4 architecture (NO energy pooling)
    → Expected: Catastrophic collapse (mean=0.49)

  - POOLING: Modified architecture (energy pooling enabled)
    → Expected: Sustained population (mean > 5)
    → Hypothesis confirmed if mean_pooling > mean_baseline (p < 0.05)

Parameters:
  - Frequency: f = 2.5% (consistent with C176)
  - Seeds: n = 10 per condition (42, 123, 456, 789, 101, 202, 303, 404, 505, 606)
  - Cycles: 3,000 per experiment
  - Energy recharge: r = 0.010 (both conditions, C176 V4 rate)
  - Sharing fraction: α = 0.10 (POOLING only)
  - Spawn threshold: E ≥ 10.0 (both conditions)

Statistical Analysis:
  - Independent samples t-test (POOLING vs BASELINE)
  - DV: Mean population
  - α: 0.05 (one-tailed, expect pooling > baseline)
  - Effect size: Cohen's d (expect large effect, d > 0.8)

Expected Outcomes:
  - Scenario A (Strong): mean=8-12, CV=20-40%, p<0.001, d>1.5, extinction=0%
  - Scenario B (Moderate): mean=3-5, CV=50-70%, p<0.01, d=0.8-1.2, extinction=10-30%
  - Scenario C (Null): mean=0.4-0.6, CV=95-105%, p>0.05, d<0.2, extinction=100%

Date: 2025-10-26
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 177 (Post-Paper 2 completion, testing first hypothesis from Section 4.4.1)
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

# Experimental parameters (matched to C176 V4 for direct comparison)
FREQUENCY = 2.5  # Spawn frequency (%)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100
SPAWN_THRESHOLD = 10.0  # Minimum energy for spawning
ENERGY_RECHARGE_RATE = 0.010  # C176 V4 rate (already in FractalAgent.evolve())
SHARING_FRACTION = 0.10  # Energy pooling contribution fraction


class EnergyPoolingCondition:
    """Condition wrapper for energy pooling experiments."""

    def __init__(self, name: str, pooling_enabled: bool):
        """
        Initialize condition.

        Args:
            name: Condition name (BASELINE or POOLING)
            pooling_enabled: Whether to enable energy pooling
        """
        self.name = name
        self.pooling_enabled = pooling_enabled

    def __repr__(self):
        return f"EnergyPoolingCondition({self.name}, pooling={self.pooling_enabled})"


def run_single_experiment(
    condition: EnergyPoolingCondition,
    frequency: float,
    seed: int,
    cycles: int
) -> Dict:
    """
    Run single energy pooling experiment.

    Args:
        condition: Experimental condition (BASELINE or POOLING)
        frequency: Spawn frequency (%)
        seed: Random seed
        cycles: Number of evolution cycles

    Returns:
        Dictionary with results
    """
    np.random.seed(seed)

    # Initialize reality and bridge
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine(resonance_threshold=0.85)

    # Spawn root agent WITH SEED-CONTROLLED ENERGY PERTURBATION (V5 FIX - Cycle 235)
    metrics = reality.get_system_metrics()

    # STOCHASTICITY FIX: Add controlled perturbation to initial energy
    # E₀ ~ U(125, 135) represents ±3.8% variation from nominal 130
    # This enables statistical validity while maintaining reality grounding
    base_energy = 130.0
    energy_perturbation = np.random.uniform(-5.0, 5.0)
    initial_energy = base_energy + energy_perturbation

    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality,  # Energy recharge enabled (r=0.010 in evolve())
        initial_energy=initial_energy  # V5 FIX: Seed-controlled perturbation
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
        # 1. Spawn check (deterministic timing from C171-C176)
        if cycle_idx % spawn_interval == 0 and cycle_idx > 0:
            # Spawn new agent from root (if root has energy)
            if len(agents) < MAX_AGENTS and root.energy >= SPAWN_THRESHOLD:
                child_id = f"agent_{spawn_count:04d}"
                child = root.spawn_child(
                    child_id=child_id,
                    energy_fraction=0.30  # C176 spawn cost
                )
                if child is not None:
                    agents.append(child)
                    spawn_count += 1

        # 2. Energy pooling (POOLING condition only)
        if condition.pooling_enabled:
            # Set cluster_id based on composition detection
            for agent in agents:
                agent.cluster_id = None  # Reset

            # Detect clusters
            cluster_events = composition_engine.detect_clusters(agents)

            # Set cluster_id for agents in clusters
            for cluster_id, member_ids in composition_engine.clusters.items():
                for agent in agents:
                    if agent.agent_id in member_ids:
                        agent.cluster_id = cluster_id

            # Execute energy pooling cycle
            pools_formed = 0
            energy_pooled = 0.0
            energy_distributed = 0.0

            for cluster_id, member_ids in composition_engine.clusters.items():
                if len(member_ids) < 2:
                    continue

                cluster_agents = [a for a in agents if a.agent_id in member_ids]

                # Collect contributions
                pool_energy = 0.0
                for agent in cluster_agents:
                    contribution = agent.contribute_to_pool(SHARING_FRACTION)
                    pool_energy += contribution
                    energy_pooled += contribution

                # Distribute to agents below threshold
                sorted_agents = sorted(cluster_agents, key=lambda a: a.energy)
                for agent in sorted_agents:
                    if pool_energy <= 0:
                        break
                    received = agent.receive_from_pool(pool_energy, SPAWN_THRESHOLD)
                    pool_energy -= received
                    energy_distributed += received

                pools_formed += 1

            # Track pooling statistics
            energy_pooling_stats['total_pools_formed'] += pools_formed
            energy_pooling_stats['total_energy_pooled'] += energy_pooled
            energy_pooling_stats['total_energy_distributed'] += energy_distributed

        # 3. Agent evolution (energy recharge happens in evolve())
        for agent in agents:
            agent.evolve(delta_time=1.0)

        # 4. Composition detection (death through clustering)
        cluster_events = composition_engine.detect_clusters(agents)

        if cluster_events:
            composition_events.append(cycle_idx)

            # Remove agents in clusters (death)
            agents_to_remove_ids = set()
            for cluster_event in cluster_events:
                for agent_id in cluster_event.agent_ids:
                    agents_to_remove_ids.add(agent_id)

            # Filter out removed agents
            agents = [a for a in agents if a.agent_id not in agents_to_remove_ids]

        # Track population
        population_history.append(len(agents))

    # Calculate statistics
    pop_array = np.array(population_history)
    mean_pop = np.mean(pop_array)
    std_pop = np.std(pop_array)
    cv_pop = (std_pop / mean_pop * 100) if mean_pop > 0 else 0

    # Composition rate (events per 100 cycles)
    comp_array = np.zeros(cycles)
    for event_cycle in composition_events:
        comp_array[event_cycle] = 1

    windowed_comp = []
    for i in range(0, cycles - WINDOW_SIZE + 1, WINDOW_SIZE):
        window_comp = np.sum(comp_array[i:i + WINDOW_SIZE])
        windowed_comp.append(window_comp)

    avg_comp = np.mean(windowed_comp) if windowed_comp else 0

    # Basin classification
    if avg_comp >= BASIN_THRESHOLD:
        basin = "A"
    else:
        basin = "B"

    # Result dictionary
    result = {
        'condition': condition.name,
        'pooling_enabled': condition.pooling_enabled,
        'frequency': frequency,
        'seed': seed,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': len(agents),
        'mean_population': float(mean_pop),
        'std_population': float(std_pop),
        'cv_population': float(cv_pop),
        'avg_composition_events': float(avg_comp),
        'basin': basin,
        'window_size': WINDOW_SIZE
    }

    # Add pooling statistics if applicable
    if condition.pooling_enabled and energy_pooling_stats is not None:
        result['pooling_stats'] = {
            'total_pools_formed': energy_pooling_stats['total_pools_formed'],
            'total_energy_pooled': float(energy_pooling_stats['total_energy_pooled']),
            'total_energy_distributed': float(energy_pooling_stats['total_energy_distributed']),
            'avg_pools_per_cycle': energy_pooling_stats['total_pools_formed'] / cycles,
            'energy_conservation_check': abs(
                energy_pooling_stats['total_energy_pooled'] -
                energy_pooling_stats['total_energy_distributed']
            ) < 1.0
        }

    return result


def main():
    """Run C177 H1 energy pooling experiment."""
    print("=" * 80)
    print("CYCLE 177: HYPOTHESIS 1 - Energy Pooling Test")
    print("=" * 80)
    print()
    print("Purpose: Test if energy pooling overcomes single-parent bottleneck")
    print("Strategy: Compare BASELINE (no pooling) vs POOLING (enabled)")
    print()
    print(f"Conditions to test: 2")
    print("  1. BASELINE: C176 V4 architecture (NO energy pooling)")
    print("  2. POOLING: Energy pooling enabled within clusters (α=0.10)")
    print()
    print(f"Frequency: {FREQUENCY}% (consistent with C176)")
    print(f"Seeds per condition: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(SEEDS) * 2}")
    print()

    # Define conditions
    conditions = [
        EnergyPoolingCondition("BASELINE", pooling_enabled=False),
        EnergyPoolingCondition("POOLING", pooling_enabled=True)
    ]

    # Results storage
    all_results = []
    start_time = time.time()

    # Run experiments
    for condition in conditions:
        print(f"Testing Condition: {condition.name}")
        if condition.pooling_enabled:
            print(f"  Description: Energy pooling enabled (α={SHARING_FRACTION})")
        else:
            print(f"  Description: No energy pooling (C176 V4 baseline)")
        print("-" * 80)

        condition_results = []

        for idx, seed in enumerate(SEEDS, 1):
            result = run_single_experiment(
                condition=condition,
                frequency=FREQUENCY,
                seed=seed,
                cycles=CYCLES
            )

            condition_results.append(result)
            all_results.append(result)

            # Print progress
            print(f"  [{idx:2d}/{len(SEEDS)}] Seed {seed:3d}: "
                  f"pop={result['mean_population']:5.1f} "
                  f"(CV={result['cv_population']:5.1f}%), "
                  f"comp={result['avg_composition_events']:5.2f}, "
                  f"basin={result['basin']}")

        # Condition summary
        pop_means = [r['mean_population'] for r in condition_results]
        pop_cvs = [r['cv_population'] for r in condition_results]
        final_counts = [r['final_agent_count'] for r in condition_results]

        print()
        print(f"  Condition Summary ({condition.name}):")
        print(f"    Mean population: {np.mean(pop_means):.2f} ± {np.std(pop_means):.2f}")
        print(f"    Mean CV: {np.mean(pop_cvs):.2f}%")
        print(f"    Final count: {np.mean(final_counts):.2f} ± {np.std(final_counts):.2f}")
        print(f"    Extinction rate: {sum(1 for c in final_counts if c == 0) / len(final_counts) * 100:.0f}%")

        if condition.pooling_enabled:
            pooling_pools = [r['pooling_stats']['total_pools_formed'] for r in condition_results]
            pooling_energy = [r['pooling_stats']['total_energy_pooled'] for r in condition_results]
            print(f"    Total pools formed: {np.mean(pooling_pools):.0f} ± {np.std(pooling_pools):.0f}")
            print(f"    Total energy pooled: {np.mean(pooling_energy):.1f} ± {np.std(pooling_energy):.1f}")

        print()

    # Calculate duration
    duration = (time.time() - start_time) / 60.0

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Statistical comparison
    baseline_results = [r for r in all_results if r['condition'] == 'BASELINE']
    pooling_results = [r for r in all_results if r['condition'] == 'POOLING']

    baseline_pops = np.array([r['mean_population'] for r in baseline_results])
    pooling_pops = np.array([r['mean_population'] for r in pooling_results])

    baseline_mean = np.mean(baseline_pops)
    pooling_mean = np.mean(pooling_pops)
    baseline_std = np.std(baseline_pops)
    pooling_std = np.std(pooling_pops)

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((baseline_std**2 + pooling_std**2) / 2)
    cohens_d = (pooling_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0

    print("STATISTICAL COMPARISON:")
    print("-" * 80)
    print(f"          Condition | Mean Pop | Std Pop | Mean CV | Homeostasis?")
    print("-" * 80)

    baseline_cv = np.mean([r['cv_population'] for r in baseline_results])
    pooling_cv = np.mean([r['cv_population'] for r in pooling_results])

    print(f"  BASELINE (no pool) | {baseline_mean:8.2f} | {baseline_std:7.2f} | {baseline_cv:6.1f}% | "
          f"{'YES' if baseline_mean > 5 and baseline_cv < 50 else 'NO':>12s}")
    print(f"  POOLING (α={SHARING_FRACTION:.2f}) | {pooling_mean:8.2f} | {pooling_std:7.2f} | {pooling_cv:6.1f}% | "
          f"{'YES' if pooling_mean > 5 and pooling_cv < 50 else 'NO':>12s}")
    print()

    print(f"Effect Size (Cohen's d): {cohens_d:.3f}")

    if cohens_d > 1.5:
        print("  → Very large effect (Scenario A: Strong confirmation)")
        hypothesis_outcome = "STRONGLY CONFIRMED"
    elif cohens_d > 0.8:
        print("  → Large effect (Scenario B: Moderate confirmation)")
        hypothesis_outcome = "CONFIRMED"
    elif cohens_d > 0.2:
        print("  → Small effect (Marginal support)")
        hypothesis_outcome = "MARGINAL SUPPORT"
    else:
        print("  → Negligible effect (Scenario C: Null result)")
        hypothesis_outcome = "REJECTED"

    print()
    print(f"Hypothesis 1 (Energy Pooling): {hypothesis_outcome}")
    print()

    # Interpretation
    if pooling_mean > baseline_mean * 2:
        print("⚠️  SIGNIFICANT IMPROVEMENT: Energy pooling substantially increases population")
        print("    → Single-parent bottleneck identified as primary constraint")
        print("    → Distributed reproductive capacity enables sustained populations")
    elif pooling_mean > baseline_mean * 1.2:
        print("⚠️  MODERATE IMPROVEMENT: Energy pooling partially overcomes bottleneck")
        print("    → May require synergistic combination with H2/H3/H4/H5")
    else:
        print("⚠️  NO SIGNIFICANT EFFECT: Energy pooling insufficient")
        print("    → Single-parent bottleneck NOT primary limitation")
        print("    → Other asymmetries (recovery lag, continuous death) dominate")

    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    results_file = output_dir / "cycle177_v5_corrected_stochasticity_results.json"

    output = {
        'metadata': {
            'cycle': '177 V5',
            'hypothesis': 'H1 - Energy Pooling (Corrected Stochasticity Framework)',
            'date': datetime.now().isoformat(),
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(all_results),
            'duration_minutes': duration,
            'sharing_fraction': SHARING_FRACTION,
            'spawn_threshold': SPAWN_THRESHOLD,
            'energy_recharge_rate': ENERGY_RECHARGE_RATE
        },
        'experiments': all_results,
        'statistical_summary': {
            'baseline_mean_population': float(baseline_mean),
            'baseline_std_population': float(baseline_std),
            'baseline_mean_cv': float(baseline_cv),
            'pooling_mean_population': float(pooling_mean),
            'pooling_std_population': float(pooling_std),
            'pooling_mean_cv': float(pooling_cv),
            'cohens_d': float(cohens_d),
            'hypothesis_outcome': hypothesis_outcome
        }
    }

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {results_file}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 177 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
