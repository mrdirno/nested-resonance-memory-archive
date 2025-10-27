#!/usr/bin/env python3
"""
CYCLE 178: H1+H2 FACTORIAL EXPERIMENT - Energy Pooling × External Sources

Purpose: Test synergistic effects of combining H1 (Energy Pooling) with H2 (External Sources)
         using 2×2 factorial design to detect super-additive interactions.

Background:
  - C176: Catastrophic collapse (mean=0.49) under single-mechanism baseline
  - C177: Energy pooling (H1) tested independently
  - Paper 3: Systematic testing of pairwise hypothesis combinations
  - Framework: Corrected stochasticity (Cycle 235 fix)

Hypotheses:
  H1 (Energy Pooling):
    Agents share energy within resonance clusters, addressing single-parent
    bottleneck by distributing reproductive capacity across cluster members.
    Implementation: α=0.10 energy contribution per agent per cycle to cluster pool

  H2 (External Sources):
    Agents receive energy rewards from environment when forming resonance clusters,
    accelerating recovery and enabling faster return to reproductive capacity.
    Implementation: E_reward=5.0 energy units per successful cluster formation event

Synergy Prediction:
  Combined H1+H2 should produce super-additive effects:
  - H1 distributes reproductive capacity across multiple agents
  - H2 accelerates energy recovery for all agents
  - Together: Multiple agents recover quickly AND can reproduce
  - Predicted: Effect(H1+H2) > Effect(H1) + Effect(H2)

Experimental Design (2×2 Factorial):
  4 Conditions:
    1. BASELINE: Neither H1 nor H2 (no pooling, no external sources)
    2. H1-only: Energy pooling enabled (α=0.10), no external sources
    3. H2-only: No energy pooling, external sources enabled (E_reward=5.0)
    4. H1+H2: Both mechanisms active (pooling α=0.10, external E_reward=5.0)

Parameters (Fixed across all conditions):
  - Frequency: f = 2.5% (Regime 3, catastrophic baseline)
  - Seeds: n = 10 per condition (42, 123, 456, 789, 101, 202, 303, 404, 505, 606)
  - Cycles: 3,000 per experiment
  - Total experiments: 40 (4 conditions × 10 seeds)
  - Energy recharge: r = 0.010
  - Spawn threshold: E ≥ 10.0

Statistical Analysis:
  - Two-way ANOVA (H1 × H2 interaction)
  - Main effect of H1, Main effect of H2, Interaction (H1×H2)
  - Post-hoc: Tukey HSD pairwise comparisons (Bonferroni α=0.0083)
  - Effect sizes: Cohen's d for all pairwise comparisons
  - Synergy Index: SI = [Effect(H1+H2) - (Effect(H1) + Effect(H2))] / Effect(BASELINE)

Classification Rubric:
  - STRONGLY SYNERGISTIC: p<0.001, d≥1.5, SI≥0.50, mean≥10
  - SYNERGISTIC: p<0.01, d≥0.8, SI≥0.20, mean≥5
  - ADDITIVE: interaction NS, |SI|<0.20
  - NO SIGNIFICANT EFFECT: all NS, d<0.5
  - ANTAGONISTIC: interaction significant, SI<-0.20

Date: 2025-10-26
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 178 (Paper 3 experimental battery, combination 1 of 6)
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

# Experimental parameters (C178: H1+H2 factorial design)
FREQUENCY = 2.5  # Spawn frequency (%)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100
SPAWN_THRESHOLD = 10.0  # Minimum energy for spawning
ENERGY_RECHARGE_RATE = 0.010  # Already in FractalAgent.evolve()
SHARING_FRACTION = 0.10  # H1: Energy pooling contribution fraction (α)
EXTERNAL_REWARD = 5.0  # H2: Energy reward per cluster formation event (E_reward)


class FactorialCondition:
    """Condition wrapper for 2×2 factorial experiments."""

    def __init__(self, name: str, pooling_enabled: bool, external_sources_enabled: bool):
        """
        Initialize factorial condition.

        Args:
            name: Condition name (BASELINE, H1-only, H2-only, H1+H2)
            pooling_enabled: Whether H1 (energy pooling) is active
            external_sources_enabled: Whether H2 (external energy sources) is active
        """
        self.name = name
        self.pooling_enabled = pooling_enabled
        self.external_sources_enabled = external_sources_enabled

    def __repr__(self):
        return f"FactorialCondition({self.name}, H1={self.pooling_enabled}, H2={self.external_sources_enabled})"


def run_single_experiment(
    condition: FactorialCondition,
    frequency: float,
    seed: int,
    cycles: int
) -> Dict:
    """
    Run single factorial experiment (H1×H2).

    Args:
        condition: Factorial condition (BASELINE, H1-only, H2-only, H1+H2)
        frequency: Spawn frequency (%)
        seed: Random seed
        cycles: Number of evolution cycles

    Returns:
        Dictionary with results including synergy metrics
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

    external_sources_stats = {
        'total_rewards_given': 0,
        'total_energy_rewarded': 0.0
    } if condition.external_sources_enabled else None

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

            # H2: External sources - reward agents BEFORE they are removed
            if condition.external_sources_enabled:
                for cluster_event in cluster_events:
                    for agent_id in cluster_event.agent_ids:
                        # Find agent and give energy reward
                        for agent in agents:
                            if agent.agent_id == agent_id:
                                agent.energy += EXTERNAL_REWARD
                                external_sources_stats['total_rewards_given'] += 1
                                external_sources_stats['total_energy_rewarded'] += EXTERNAL_REWARD
                                break

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
        'external_sources_enabled': condition.external_sources_enabled,
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

    # Add external sources statistics if applicable
    if condition.external_sources_enabled and external_sources_stats is not None:
        result['external_sources_stats'] = {
            'total_rewards_given': external_sources_stats['total_rewards_given'],
            'total_energy_rewarded': float(external_sources_stats['total_energy_rewarded']),
            'avg_rewards_per_cycle': external_sources_stats['total_rewards_given'] / cycles,
            'avg_energy_per_reward': (
                external_sources_stats['total_energy_rewarded'] / external_sources_stats['total_rewards_given']
                if external_sources_stats['total_rewards_given'] > 0 else 0.0
            )
        }

    return result


def main():
    """Run C178 H1×H2 factorial experiment."""
    print("=" * 80)
    print("CYCLE 178: H1×H2 FACTORIAL EXPERIMENT - Energy Pooling × External Sources")
    print("=" * 80)
    print()
    print("Purpose: Test synergistic effects of H1+H2 combination")
    print("Design: 2×2 factorial (H1: pooling, H2: external sources)")
    print()
    print(f"Conditions to test: 4")
    print("  1. BASELINE: Neither H1 nor H2")
    print("  2. H1-only: Energy pooling (α=0.10), no external sources")
    print("  3. H2-only: External sources (E_reward=5.0), no pooling")
    print("  4. H1+H2: Both mechanisms active")
    print()
    print(f"Frequency: {FREQUENCY}%")
    print(f"Seeds per condition: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(SEEDS) * 4}")
    print()

    # Define 4 factorial conditions
    conditions = [
        FactorialCondition("BASELINE", pooling_enabled=False, external_sources_enabled=False),
        FactorialCondition("H1-only", pooling_enabled=True, external_sources_enabled=False),
        FactorialCondition("H2-only", pooling_enabled=False, external_sources_enabled=True),
        FactorialCondition("H1+H2", pooling_enabled=True, external_sources_enabled=True)
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

    results_file = output_dir / "cycle178_h1h2_factorial_results.json"

    output = {
        'metadata': {
            'cycle': '178',
            'experiment': 'H1×H2 Factorial - Energy Pooling × External Sources',
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
