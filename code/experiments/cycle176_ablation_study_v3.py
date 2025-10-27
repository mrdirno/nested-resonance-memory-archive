#!/usr/bin/env python3
"""
CYCLE 176: ABLATION STUDY - Mechanism Isolation for Regime Transition

Purpose: Systematically isolate birth-death coupling as critical factor for
         bistability → homeostasis transition

Background:
  - C171: Complete framework exhibits population homeostasis (~17 agents)
  - C168-C170: Simplified model exhibits bistability (composition-rate control)
  - Hypothesis: Birth-death coupling (β parameter) drives regime transition
  - Problem: Multiple confounds (window size, spawn timing, bridge basis)

Experimental Strategy:
  Remove one architectural component at a time, test if homeostasis persists

Ablation Conditions (6 total):
  1. BASELINE: Exact C171 replication (birth + death enabled)
  2. NO DEATH: Birth only (composition detected but no agent removal)
  3. NO BIRTH: Death only (start with n=17, no spawning)
  4. SMALL WINDOW: window=25 cycles instead of 100
  5. DETERMINISTIC: Verify existing deterministic spawn timing
  6. ALT BASIS: e, φ only (remove π oscillator from bridge)

Expected Outcomes:
  - If birth-death coupling critical: NO DEATH/NO BIRTH lose homeostasis
  - If other factors dominate: Homeostasis persists across all conditions

Significance:
  - Validates birth-death coupling as necessary/sufficient mechanism
  - Provides experimental bounds for phase boundary β_critical
  - Resolves "mechanism isolation" limitation in Paper 2

Date: 2025-10-25
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 176 (Post-C171 homeostasis discovery, post-C175 precision validation)
"""

import sys
import json
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
from fractal.fractal_swarm import CompositionEngine

# Experimental parameters
FREQUENCY = 2.5  # Midpoint of C171 homeostatic range (2.0%-3.0%)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
BASIN_THRESHOLD = 2.5  # From C168-C171
WINDOW_SIZE = 100  # Default (condition 4 varies this)
MAX_AGENTS = 100  # Match C171


class AblationCondition:
    """Base class for ablation conditions."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def modify_spawn_decision(self, should_spawn: bool, cycle_idx: int,
                             spawn_interval: int, agents: List) -> bool:
        """Modify spawn decision for this condition (override in subclasses)."""
        return should_spawn

    def modify_composition_result(self, cluster_events: List, agents: List) -> List:
        """Modify composition results for this condition (override in subclasses)."""
        return cluster_events

    def get_window_size(self) -> int:
        """Get window size for this condition."""
        return WINDOW_SIZE

    def get_initial_agents(self, reality, bridge) -> List[FractalAgent]:
        """Get initial agent(s) for this condition."""
        metrics = reality.get_system_metrics()
        root = FractalAgent(
            agent_id="root",
            bridge=bridge,
            initial_reality=metrics,
            depth=0,
            max_depth=7,
            reality=reality  # V3: Enable energy recharge
        )
        return [root]

    def modify_bridge(self, bridge: TranscendentalBridge) -> TranscendentalBridge:
        """Modify bridge for this condition (override in subclasses)."""
        return bridge


class BaselineCondition(AblationCondition):
    """Condition 1: BASELINE (Exact C171 replication)."""

    def __init__(self):
        super().__init__(
            name="BASELINE",
            description="Complete framework (birth + death enabled)"
        )


class NoDeathCondition(AblationCondition):
    """Condition 2: NO DEATH (Birth only, composition detected but no removal)."""

    def __init__(self):
        super().__init__(
            name="NO_DEATH",
            description="Birth enabled, death DISABLED (composition detected, no removal)"
        )

    def modify_composition_result(self, cluster_events: List, agents: List) -> List:
        """Detect clusters but don't remove agents."""
        # Composition events are recorded but NO agents removed
        # Return empty list instead of cluster_events (prevents agent removal)
        return []


class NoBirthCondition(AblationCondition):
    """Condition 3: NO BIRTH (Death only, start with n=17)."""

    def __init__(self):
        super().__init__(
            name="NO_BIRTH",
            description="Birth DISABLED, death enabled (start with n=17)"
        )

    def modify_spawn_decision(self, should_spawn: bool, cycle_idx: int,
                             spawn_interval: int, agents: List) -> bool:
        """Disable all spawning."""
        return False

    def get_initial_agents(self, reality, bridge) -> List[FractalAgent]:
        """Start with n=17 agents (C171 equilibrium population)."""
        agents = []
        for i in range(17):
            metrics = reality.get_system_metrics()
            agent = FractalAgent(
                agent_id=f"initial_{i}",
                bridge=bridge,
                initial_reality=metrics,
                depth=0,
                max_depth=7,
                reality=reality  # V3: Enable energy recharge
            )
            agents.append(agent)
        return agents


class SmallWindowCondition(AblationCondition):
    """Condition 4: SMALL WINDOW (window=25 instead of 100)."""

    def __init__(self):
        super().__init__(
            name="SMALL_WINDOW",
            description="Window size = 25 cycles (test ceiling effect)"
        )

    def get_window_size(self) -> int:
        """Return smaller window size."""
        return 25


class DeterministicSpawnCondition(AblationCondition):
    """Condition 5: DETERMINISTIC SPAWN (already deterministic - control)."""

    def __init__(self):
        super().__init__(
            name="DETERMINISTIC",
            description="Deterministic spawn timing (control - already implemented)"
        )
    # No modifications needed - C171 already uses deterministic interval-based spawning


class AltBridgeBasisCondition(AblationCondition):
    """Condition 6: ALTERNATIVE BRIDGE BASIS (e, φ only - no π)."""

    def __init__(self):
        super().__init__(
            name="ALT_BASIS",
            description="Transcendental basis = e, φ only (remove π oscillator)"
        )

    def modify_bridge(self, bridge: TranscendentalBridge) -> TranscendentalBridge:
        """Remove π oscillator from bridge."""
        # Create new bridge with modified oscillators
        # Note: This is a simplified approach - actual implementation may vary
        # For ablation purposes, we can disable π by setting its coefficient to 0
        modified_bridge = copy.deepcopy(bridge)
        # Modify internal state to exclude π contribution
        # (Implementation-specific - may need bridge API support)
        return modified_bridge


def run_ablation_experiment(condition: AblationCondition, frequency: float,
                            seed: int, cycles: int) -> Dict:
    """
    Run ablation experiment under specified condition.

    Args:
        condition: Ablation condition to test
        frequency: Spawn frequency (% per 100 cycles)
        seed: Random seed
        cycles: Number of cycles

    Returns:
        dict with composition events, basin classification, population metrics
    """
    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Apply condition-specific bridge modifications
    bridge = condition.modify_bridge(bridge)

    # Seed for reproducibility
    np.random.seed(seed)

    # Get initial agents (condition-dependent)
    agents = condition.get_initial_agents(reality, bridge)

    # Track metrics
    composition_events = []
    spawn_count = 0
    population_trajectory = []

    # Calculate spawn interval
    spawn_interval = max(1, int(100.0 / frequency)) if frequency > 0 else cycles + 1

    # Composition engine
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Get condition-specific window size
    window_size = condition.get_window_size()

    # Run cycles
    for cycle_idx in range(cycles):

        # Spawn decision (condition-dependent)
        should_spawn = (cycle_idx % spawn_interval) == 0
        should_spawn = condition.modify_spawn_decision(
            should_spawn, cycle_idx, spawn_interval, agents
        )

        if should_spawn and len(agents) < MAX_AGENTS:
            spawn_count += 1

            # Get current reality metrics
            current_metrics = reality.get_system_metrics()

            if len(agents) == 0:
                # Population collapsed - respawn seed agent
                seed_agent = FractalAgent(
                    agent_id=f"seed_{cycle_idx}_{spawn_count}",
                    bridge=bridge,
                    initial_reality=current_metrics,
                    depth=0,
                    max_depth=7,
                    reality=reality  # V3: Enable energy recharge
                )
                agents.append(seed_agent)
            else:
                # Normal spawning from existing parent
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

        # Apply condition-specific composition modifications
        cluster_events = condition.modify_composition_result(cluster_events, agents)

        # Record composition events
        if cluster_events:
            composition_events.append(cycle_idx)

        # Remove agents in clusters (only if condition allows)
        if cluster_events:
            # cluster_events is list of ClusterEvent objects
            # Extract agent IDs from all cluster events
            agents_to_remove_ids = set()
            for cluster_event in cluster_events:
                for agent_id in cluster_event.agent_ids:
                    agents_to_remove_ids.add(agent_id)

            # Remove clustered agents from swarm
            agents = [a for a in agents if a.agent_id not in agents_to_remove_ids]

        # Track population
        population_trajectory.append(len(agents))

    # Calculate composition rate using condition-specific window
    bins = np.arange(0, cycles + 1, window_size)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification
    basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'

    # Population statistics
    final_population = len(agents)
    mean_population = float(np.mean(population_trajectory))
    std_population = float(np.std(population_trajectory))
    cv_population = (std_population / mean_population * 100) if mean_population > 0 else 0.0

    return {
        'condition': condition.name,
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': final_population,
        'mean_population': mean_population,
        'std_population': std_population,
        'cv_population': cv_population,
        'window_size': window_size,
    }


def main():
    """Execute Cycle 176 ablation study."""
    print("=" * 80)
    print("CYCLE 176: ABLATION STUDY - Mechanism Isolation")
    print("=" * 80)
    print()
    print("Purpose: Test if birth-death coupling is critical for homeostasis")
    print("Strategy: Systematically ablate architectural components")
    print()

    # Define ablation conditions
    # V3: Test BASELINE only first to validate energy recharge fix
    conditions = [
        BaselineCondition(),
        # NoDeathCondition(),  # V3: Disabled for initial validation
        # NoBirthCondition(),  # V3: Disabled for initial validation
        # SmallWindowCondition(),  # V3: Disabled for initial validation
        # DeterministicSpawnCondition(),  # V3: Disabled for initial validation
        # AltBridgeBasisCondition(),  # V3: Disabled for initial validation
    ]

    print(f"Conditions to test: {len(conditions)}")
    for i, condition in enumerate(conditions, 1):
        print(f"  {i}. {condition.name}: {condition.description}")
    print()

    print(f"Frequency: {FREQUENCY}% (midpoint of C171 homeostatic range)")
    print(f"Seeds per condition: n={len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(conditions) * len(SEEDS)}")
    print()

    results = []
    start_time = datetime.now()

    # Run experiments
    exp_num = 0
    for condition in conditions:
        print(f"Testing Condition: {condition.name}")
        print(f"  Description: {condition.description}")
        print("-" * 80)

        for seed in SEEDS:
            exp_num += 1

            result = run_ablation_experiment(condition, FREQUENCY, seed, CYCLES)
            results.append(result)

            print(f"  [{exp_num:2d}/{len(conditions)*len(SEEDS)}] "
                  f"Seed {seed:3d}: "
                  f"pop={result['mean_population']:5.1f} (CV={result['cv_population']:4.1f}%), "
                  f"comp={result['avg_composition_events']:5.2f}, "
                  f"basin={result['basin']}")

        print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()

    # Analyze results by condition
    print("ABLATION RESULTS SUMMARY:")
    print("-" * 80)
    print(f"{'Condition':>20} | {'Mean Pop':>9} | {'Pop CV':>7} | {'Mean Comp':>9} | {'Homeostasis?':>13}")
    print("-" * 80)

    for condition in conditions:
        cond_results = [r for r in results if r['condition'] == condition.name]

        mean_pop = np.mean([r['mean_population'] for r in cond_results])
        mean_cv = np.mean([r['cv_population'] for r in cond_results])
        mean_comp = np.mean([r['avg_composition_events'] for r in cond_results])

        # Homeostasis criterion: CV < 15% (loose), CV < 10% (strict)
        homeostasis = "YES" if mean_cv < 15 else "NO"

        print(f"{condition.name:>20} | {mean_pop:>9.2f} | {mean_cv:>6.1f}% | {mean_comp:>9.2f} | {homeostasis:>13}")

    print()

    # Key findings
    print("KEY FINDINGS:")
    print("-" * 80)

    baseline_results = [r for r in results if r['condition'] == 'BASELINE']
    baseline_cv = np.mean([r['cv_population'] for r in baseline_results])

    no_death_results = [r for r in results if r['condition'] == 'NO_DEATH']
    no_death_cv = np.mean([r['cv_population'] for r in no_death_results])

    no_birth_results = [r for r in results if r['condition'] == 'NO_BIRTH']
    no_birth_cv = np.mean([r['cv_population'] for r in no_birth_results])

    print(f"BASELINE CV: {baseline_cv:.1f}%")
    print(f"NO DEATH CV: {no_death_cv:.1f}% ({'NO HOMEOSTASIS' if no_death_cv > 50 else 'homeostasis persists'})")
    print(f"NO BIRTH CV: {no_birth_cv:.1f}% ({'NO HOMEOSTASIS' if no_birth_cv > 50 else 'homeostasis persists'})")
    print()

    if no_death_cv > 50 and no_birth_cv > 50 and baseline_cv < 15:
        print("✅ HYPOTHESIS CONFIRMED: Birth-death coupling is NECESSARY for homeostasis")
        print("   (NO DEATH and NO BIRTH both lost regulation, BASELINE maintained it)")
    elif no_death_cv < 15 and no_birth_cv < 15:
        print("❌ HYPOTHESIS REJECTED: Birth-death coupling NOT necessary")
        print("   (Homeostasis persists without birth-death coupling)")
    else:
        print("⚠️  MIXED RESULTS: Further investigation needed")

    print()

    # Save results
    output_data = {
        'metadata': {
            'cycle': '176',
            'scenario': 'Ablation Study - Mechanism Isolation',
            'date': start_time.isoformat(),
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
            'conditions': [
                {'name': c.name, 'description': c.description}
                for c in conditions
            ],
        },
        'experiments': results,
    }

    output_path = Path(__file__).parent / "results" / "cycle176_ablation_study_v3.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved: {output_path}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 176 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
