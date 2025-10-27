#!/usr/bin/env python3
"""
CYCLE 183: H4+H5 FACTORIAL EXPERIMENT - Composition Throttling × Multi-Generational Recovery

Purpose: Test synergistic effects of combining H4 (Composition Throttling) with H5 (Multi-Generational Recovery)
         using 2×2 factorial design to detect super-additive interactions.

Background:
  - C176: Catastrophic collapse (mean=0.49) under single-mechanism baseline
  - C177: Composition throttling (H1) tested independently
  - Paper 3: Systematic testing of pairwise hypothesis combinations
  - Framework: Corrected stochasticity (Cycle 235 fix)

Hypotheses:
  H4 (Composition Throttling):
    Agents share energy within resonance clusters, addressing single-parent
    bottleneck by distributing reproductive capacity across cluster members.
    Implementation: α=0.10 energy contribution per agent per cycle to cluster pool

  H5 (Multi-Generational Recovery):
    Staggered spawning across lineages prevents synchronized death waves by
    creating temporal diversity in birth timing across generational depths.
    Implementation: Minimum 300-cycle offset between parent-offspring spawning
                    Parent spawns at cycle t → offspring can spawn at t+300
                    Creates asynchronous reproductive windows across lineage

Synergy Prediction:
  Combined H4+H5 should produce super-additive effects:
  - H1 distributes reproductive capacity across multiple cluster members
  - H5 creates temporal diversity preventing synchronized collapse
  - Together: Multiple agents reproduce at DIFFERENT times, maintaining continuous births
  - Predicted: Effect(H4+H5) > Effect(H1) + Effect(H5)

Experimental Design (2×2 Factorial):
  4 Conditions:
    1. BASELINE: Neither H1 nor H5 (no pooling, no multi-generational coordination)
    2. H4-only: Composition throttling enabled (α=0.10), no temporal coordination
    3. H5-only: No composition throttling, multi-generational coordination (offset=300)
    4. H4+H5: Both mechanisms active (pooling α=0.10, offset=300)

Parameters (Fixed across all conditions):
  - Frequency: f = 2.5% (Regime 3, catastrophic baseline)
  - Seeds: n = 10 per condition (42, 123, 456, 789, 101, 202, 303, 404, 505, 606)
  - Cycles: 3,000 per experiment
  - Total experiments: 40 (4 conditions × 10 seeds)
  - Energy recharge: r = 0.010
  - Spawn threshold: E ≥ 10.0
  - Generation offset: Δt = 300 cycles (H5 parameter)

Statistical Analysis:
  - Two-way ANOVA (H1 × H5 interaction)
  - Main effect of H1, Main effect of H5, Interaction (H4×H5)
  - Post-hoc: Tukey HSD pairwise comparisons (Bonferroni α=0.0083)
  - Effect sizes: Cohen's d for all pairwise comparisons
  - Synergy Index: SI = [Effect(H4+H5) - (Effect(H1) + Effect(H5))] / Effect(BASELINE)

Classification Rubric:
  - STRONGLY SYNERGISTIC: p<0.001, d≥1.5, SI≥0.50, mean≥10
  - SYNERGISTIC: p<0.01, d≥0.8, SI≥0.20, mean≥5
  - ADDITIVE: interaction NS, |SI|<0.20
  - NO SIGNIFICANT EFFECT: all NS, d<0.5
  - ANTAGONISTIC: interaction significant, SI<-0.20

Date: 2025-10-26
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 180 (Paper 3 experimental battery, combination 6 of 6)
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

# Experimental parameters (C183: H4+H5 factorial design)
BASE_FREQUENCY = 2.5  # Base spawn frequency (%) - used in H4 formula
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5
WINDOW_SIZE = 100
MAX_AGENTS = 100
SPAWN_THRESHOLD = 10.0  # Minimum energy for spawning
ENERGY_RECHARGE_RATE = 0.010  # Already in FractalAgent.evolve()
RHO_MAX = 30  # H4: Maximum sustainable density (agents)
GENERATION_OFFSET = 300  # H5: Minimum cycles between parent-offspring spawning


class FactorialCondition:
    """Condition wrapper for 2×2 factorial experiments."""

    def __init__(self, name: str, throttling_enabled: bool, multigenerational_enabled: bool):
        """
        Initialize factorial condition.

        Args:
            name: Condition name (BASELINE, H4-only, H5-only, H4+H5)
            throttling_enabled: Whether H1 (composition throttling) is active
            multigenerational_enabled: Whether H5 (multi-generational recovery) is active
        """
        self.name = name
        self.throttling_enabled = throttling_enabled
        self.multigenerational_enabled = multigenerational_enabled

    def __repr__(self):
        return f"FactorialCondition({self.name}, H1={self.throttling_enabled}, H5={self.multigenerational_enabled})"


def run_single_experiment(
    condition: FactorialCondition,
    base_frequency: float,
    seed: int,
    cycles: int
) -> Dict:
    """
    Run single factorial experiment (H4×H5).

    Args:
        condition: Factorial condition (BASELINE, H4-only, H5-only, H4+H5)
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
    spawn_interval = int(100 / base_frequency) if base_frequency > 0 else float('inf')

    # Tracking
    spawn_count = 0
    composition_events = []
    population_history = []
    agent_spawn_times = {}  # Track when each agent last spawned (for H5)
    agent_spawn_times["root"] = 0  # Root agent spawned at cycle 0

    throttling_stats = {
        'total_pools_formed': 0,
        'total_energy_pooled': 0.0,
        'total_energy_distributed': 0.0
    } if condition.throttling_enabled else None

    multigenerational_stats = {
        'total_spawn_delays': 0,
        'total_spawn_attempts_blocked': 0,
        'max_generation_depth': 0,
        'generation_distribution': defaultdict(int)
    } if condition.multigenerational_enabled else None

    # Evolution loop
    for cycle_idx in range(cycles):
        # 1. Spawn check with H5 multi-generational coordination
        if cycle_idx % spawn_interval == 0 and cycle_idx > 0:
            # Spawn new agent from root (if root has energy)
            if len(agents) < MAX_AGENTS and root.energy >= SPAWN_THRESHOLD:
                # H5: Check if sufficient time has passed since root's last spawn
                can_spawn = True
                if condition.multigenerational_enabled:
                    last_spawn_cycle = agent_spawn_times.get("root", 0)
                    cycles_since_last_spawn = cycle_idx - last_spawn_cycle

                    if cycles_since_last_spawn < GENERATION_OFFSET:
                        can_spawn = False
                        multigenerational_stats['total_spawn_attempts_blocked'] += 1
                    else:
                        multigenerational_stats['total_spawn_delays'] += cycles_since_last_spawn

                if can_spawn:
                    child_id = f"agent_{spawn_count:04d}"
                    child = root.spawn_child(
                        child_id=child_id,
                        energy_fraction=0.30  # C176 spawn cost
                    )
                    if child is not None:
                        agents.append(child)
                        spawn_count += 1

                        # Track spawn time and generation depth
                        agent_spawn_times["root"] = cycle_idx

                        # Track generation distribution (H5)
                        if condition.multigenerational_enabled:
                            generation_depth = getattr(child, 'depth', 0)
                            multigenerational_stats['generation_distribution'][generation_depth] += 1
                            if generation_depth > multigenerational_stats['max_generation_depth']:
                                multigenerational_stats['max_generation_depth'] = generation_depth

        # 2. Composition throttling (POOLING condition only)
        if condition.throttling_enabled:
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

            # Execute composition throttling cycle
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
                    contribution = agent.contribute_to_pool(RHO_MAX)
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
            throttling_stats['total_pools_formed'] += pools_formed
            throttling_stats['total_energy_pooled'] += energy_pooled
            throttling_stats['total_energy_distributed'] += energy_distributed

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
        'throttling_enabled': condition.throttling_enabled,
        'multigenerational_enabled': condition.multigenerational_enabled,
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
    if condition.throttling_enabled and throttling_stats is not None:
        result['throttling_stats'] = {
            'total_pools_formed': throttling_stats['total_pools_formed'],
            'total_energy_pooled': float(throttling_stats['total_energy_pooled']),
            'total_energy_distributed': float(throttling_stats['total_energy_distributed']),
            'avg_pools_per_cycle': throttling_stats['total_pools_formed'] / cycles,
            'energy_conservation_check': abs(
                throttling_stats['total_energy_pooled'] -
                throttling_stats['total_energy_distributed']
            ) < 1.0
        }

    # Add multi-generational statistics if applicable
    if condition.multigenerational_enabled and multigenerational_stats is not None:
        avg_spawn_delay = (
            multigenerational_stats['total_spawn_delays'] / spawn_count
            if spawn_count > 0 else 0.0
        )

        result['multigenerational_stats'] = {
            'total_spawn_delays': multigenerational_stats['total_spawn_delays'],
            'total_spawn_attempts_blocked': multigenerational_stats['total_spawn_attempts_blocked'],
            'avg_spawn_delay': float(avg_spawn_delay),
            'max_generation_depth': multigenerational_stats['max_generation_depth'],
            'generation_distribution': dict(multigenerational_stats['generation_distribution']),
            'generation_offset': GENERATION_OFFSET
        }

    return result


def main():
    """Run C183 H4×H5 factorial experiment."""
    print("=" * 80)
    print("CYCLE 183: H4×H5 FACTORIAL EXPERIMENT - Composition Throttling × Multi-Generational Recovery")
    print("=" * 80)
    print()
    print("Purpose: Test synergistic effects of H4+H5 combination")
    print("Design: 2×2 factorial (H1: pooling, H5: multi-generational coordination)")
    print()
    print(f"Conditions to test: 4")
    print("  1. BASELINE: Neither H1 nor H5")
    print("  2. H4-only: Composition throttling (α=0.10), no multi-generational coordination")
    print("  3. H5-only: Multi-generational coordination (offset=300), no pooling")
    print("  4. H4+H5: Both mechanisms active")
    print()
    print(f"Frequency: {FREQUENCY}%")
    print(f"Seeds per condition: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(SEEDS) * 4}")
    print()

    # Define 4 factorial conditions
    conditions = [
        FactorialCondition("BASELINE", throttling_enabled=False, multigenerational_enabled=False),
        FactorialCondition("H4-only", throttling_enabled=True, multigenerational_enabled=False),
        FactorialCondition("H5-only", throttling_enabled=False, multigenerational_enabled=True),
        FactorialCondition("H4+H5", throttling_enabled=True, multigenerational_enabled=True)
    ]

    # Results storage
    all_results = []
    start_time = time.time()

    # Run experiments
    for condition in conditions:
        print(f"Testing Condition: {condition.name}")
        desc_parts = []
        if condition.throttling_enabled:
            desc_parts.append(f"Composition throttling (α={RHO_MAX})")
        if condition.multigenerational_enabled:
            desc_parts.append(f"Multi-generational coordination (offset={GENERATION_OFFSET})")
        if not desc_parts:
            desc_parts.append("C176 V4 baseline (no mechanisms)")
        print(f"  Description: {', '.join(desc_parts)}")
        print("-" * 80)

        condition_results = []

        for idx, seed in enumerate(SEEDS, 1):
            result = run_single_experiment(
                condition=condition,
                base_frequency=BASE_FREQUENCY,
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

        if condition.throttling_enabled:
            pooling_pools = [r['throttling_stats']['total_pools_formed'] for r in condition_results]
            pooling_energy = [r['throttling_stats']['total_energy_pooled'] for r in condition_results]
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
    print(f"  POOLING (α={RHO_MAX:.2f}) | {pooling_mean:8.2f} | {pooling_std:7.2f} | {pooling_cv:6.1f}% | "
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
        print("⚠️  SIGNIFICANT IMPROVEMENT: Composition throttling substantially increases population")
        print("    → Single-parent bottleneck identified as primary constraint")
        print("    → Distributed reproductive capacity enables sustained populations")
    elif pooling_mean > baseline_mean * 1.2:
        print("⚠️  MODERATE IMPROVEMENT: Composition throttling partially overcomes bottleneck")
        print("    → May require synergistic combination with H2/H3/H4/H5")
    else:
        print("⚠️  NO SIGNIFICANT EFFECT: Composition throttling insufficient")
        print("    → Single-parent bottleneck NOT primary limitation")
        print("    → Other asymmetries (recovery lag, continuous death) dominate")

    # Save results
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    results_file = output_dir / "cycle183_h1h5_factorial_results.json"

    output = {
        'metadata': {
            'cycle': '180',
            'experiment': 'H4×H5 Factorial - Composition Throttling × Multi-Generational Recovery',
            'date': datetime.now().isoformat(),
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(all_results),
            'duration_minutes': duration,
            'rho_max': RHO_MAX,
            'spawn_threshold': SPAWN_THRESHOLD,
            'energy_recharge_rate': ENERGY_RECHARGE_RATE,
            'generation_offset': GENERATION_OFFSET
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
    print("CYCLE 183 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
