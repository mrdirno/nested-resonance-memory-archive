#!/usr/bin/env python3
"""
Cycle 266: Hierarchical Synergy Analysis - H1×H2 Depth-Stratified
(Energy Pooling × Reality Sources)

Purpose: Test scale invariance of synergy patterns across fractal depth levels
  - NRM predicts: Same dynamics at all fractal levels (scale invariance)
  - Question: Do H1×H2 synergies appear equivalently at depth=1, 3, 7?
  - Hypothesis: Synergy magnitude constant across depths (fractal property)

Experimental Design:
  - Selected pair: H1×H2 (known synergistic)
  - Cycles: 3000 per condition
  - 4 conditions: OFF-OFF, H1-only, H2-only, H1×H2
  - Depth stratification: Track population separately by agent depth (0-7)

Analysis:
  - Depth-specific synergy: synergy(depth) for each depth level
  - Scale invariance test: Variance of synergy across depths
  - Cross-level interactions: Do depth=1 synergies affect depth=7 dynamics?
  - Critical depth identification: Which depths show strongest synergies?

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26
Cycle: 266 (Paper 4 extensions - hierarchical analysis)
Framework: Nested Resonance Memory (scale invariance validation)
License: GPL-3.0
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Import from existing modules
sys.path.append(str(Path(__file__).parent.parent))

from src.core.reality_interface import RealityInterface
from src.bridge.transcendental_bridge import TranscendentalBridge
from src.fractal.fractal_agent import FractalAgent
from src.fractal.composition_engine import CompositionEngine

# Experimental parameters
MAX_AGENTS = 100
INITIAL_ENERGY = 130.0
DEPTH_LIMIT = 7
CYCLES_PER_CONDITION = 3000

# Mechanism parameters
POOLING_SHARE_RATE = 0.10
SOURCES_BONUS_RATE = 0.005

RESONANCE_THRESHOLD = 0.85

# Results path
RESULTS_FILE = Path(__file__).parent / "results" / "cycle266_hierarchical_synergy_h1h2_results.json"


@dataclass
class MechanismCondition:
    """
    H1×H2 factorial condition.
    """
    h1_enabled: bool
    h2_enabled: bool

    def __str__(self):
        if not self.h1_enabled and not self.h2_enabled:
            return "OFF-OFF"
        elif self.h1_enabled and not self.h2_enabled:
            return "H1-only"
        elif not self.h1_enabled and self.h2_enabled:
            return "H2-only"
        else:
            return "H1×H2"


def run_condition(condition: MechanismCondition) -> Dict:
    """
    Run single condition for 3000 cycles with depth-stratified tracking.

    Returns population history per depth level.
    """
    # Initialize reality interface and bridge
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Initialize composition engine
    composition_engine = CompositionEngine(resonance_threshold=RESONANCE_THRESHOLD)

    # Create root agent
    root = FractalAgent(
        agent_id="root",
        depth=0,
        energy=INITIAL_ENERGY,
        phase=bridge.reality_to_phase(reality.get_system_metrics())
    )

    # Agent list
    agents = [root]

    # Depth-stratified tracking (depth → [population_per_cycle])
    depth_population_history = defaultdict(list)

    # Main simulation loop
    for cycle in range(CYCLES_PER_CONDITION):
        # Count agents by depth for this cycle
        depth_counts = defaultdict(int)
        for agent in agents:
            depth_counts[agent.depth] += 1

        # Record population for each depth level (including zero counts)
        for depth in range(DEPTH_LIMIT + 1):
            depth_population_history[depth].append(depth_counts.get(depth, 0))

        # Agent evolution
        for agent in agents:
            # Note: FractalAgent.evolve() takes delta_time only, not phase
            agent.evolve(delta_time=1.0)

        # H1: Energy Pooling (if enabled)
        if condition.h1_enabled:
            cluster_events = composition_engine.detect_clusters(agents)
            for cluster_id, member_ids in composition_engine.clusters.items():
                cluster_agents = [a for a in agents if a.agent_id in member_ids]
                if len(cluster_agents) > 1:
                    total_energy = sum(a.energy for a in cluster_agents)
                    shared_energy = total_energy * POOLING_SHARE_RATE
                    per_agent_share = shared_energy / len(cluster_agents)
                    for agent in cluster_agents:
                        agent.energy = min(agent.energy + per_agent_share, 200.0)

        # H2: Reality Sources (if enabled)
        if condition.h2_enabled:
            for agent in agents:
                extra_metrics = reality.get_system_metrics()
                available_capacity = (100 - extra_metrics['cpu_percent']) + \
                                   (100 - extra_metrics['memory_percent'])
                bonus_energy = SOURCES_BONUS_RATE * available_capacity
                agent.energy = min(agent.energy + bonus_energy, 200.0)

        # Spawn new agents
        for agent in list(agents):
            if agent.energy >= 10.0 and agent.depth < DEPTH_LIMIT and len(agents) < MAX_AGENTS:
                child_id = f"{agent.agent_id}_child_{cycle}"
                child_phase = bridge.reality_to_phase(reality.get_system_metrics())
                child = FractalAgent(
                    agent_id=child_id,
                    depth=agent.depth + 1,
                    energy=10.0,
                    phase=child_phase,
                    parent=agent
                )
                agents.append(child)
                agent.children.append(child)
                agent.energy -= 10.0

        # Remove dead agents
        agents = [a for a in agents if a.energy > 0]

    # Compute mean population per depth
    depth_mean_population = {}
    for depth in range(DEPTH_LIMIT + 1):
        depth_mean_population[depth] = float(np.mean(depth_population_history[depth]))

    # Overall mean population
    total_population_history = [sum(depth_counts.values())
                                for depth_counts in
                                [defaultdict(int, {d: depth_population_history[d][i]
                                                  for d in range(DEPTH_LIMIT + 1)})
                                 for i in range(CYCLES_PER_CONDITION)]]
    overall_mean_population = float(np.mean(total_population_history))

    return {
        'overall_mean_population': overall_mean_population,
        'depth_mean_population': depth_mean_population,
        'depth_population_history': {d: list(h) for d, h in depth_population_history.items()},
        'final_population': len(agents),
        'condition': {
            'h1_enabled': condition.h1_enabled,
            'h2_enabled': condition.h2_enabled
        }
    }


def compute_depth_stratified_synergy(results: Dict[str, Dict]) -> Dict:
    """
    Compute synergy separately for each depth level.

    Returns depth-synergy relationship and scale invariance metrics.
    """
    depth_synergies = {}

    for depth in range(DEPTH_LIMIT + 1):
        # Extract depth-specific mean populations
        off_off = results['OFF-OFF']['depth_mean_population'][str(depth)]
        h1_only = results['H1-only']['depth_mean_population'][str(depth)]
        h2_only = results['H2-only']['depth_mean_population'][str(depth)]
        h1h2 = results['H1×H2']['depth_mean_population'][str(depth)]

        # Compute synergy
        h1_effect = h1_only - off_off
        h2_effect = h2_only - off_off
        additive_prediction = off_off + h1_effect + h2_effect
        synergy = h1h2 - additive_prediction

        # Classify
        if synergy > 0.1:
            classification = "SYNERGISTIC"
        elif synergy < -0.1:
            classification = "ANTAGONISTIC"
        else:
            classification = "ADDITIVE"

        depth_synergies[depth] = {
            'synergy': float(synergy),
            'classification': classification,
            'observed_h1h2': float(h1h2),
            'predicted_h1h2': float(additive_prediction),
            'baseline': float(off_off),
            'h1_effect': float(h1_effect),
            'h2_effect': float(h2_effect)
        }

    # Compute scale invariance metrics
    synergy_values = [ds['synergy'] for ds in depth_synergies.values()]
    mean_synergy = float(np.mean(synergy_values))
    std_synergy = float(np.std(synergy_values))
    min_synergy = float(min(synergy_values))
    max_synergy = float(max(synergy_values))
    synergy_range = float(max_synergy - min_synergy)

    # Coefficient of variation (normalized dispersion)
    cv_synergy = float(std_synergy / mean_synergy) if mean_synergy != 0 else float('inf')

    # Scale invariance classification
    if cv_synergy < 0.2:
        scale_invariance = "STRONG (CV < 0.2)"
    elif cv_synergy < 0.5:
        scale_invariance = "MODERATE (0.2 ≤ CV < 0.5)"
    else:
        scale_invariance = "WEAK (CV ≥ 0.5)"

    # Identify critical depths (highest synergy)
    critical_depth = max(depth_synergies.keys(), key=lambda d: depth_synergies[d]['synergy'])

    return {
        'depth_synergies': depth_synergies,
        'mean_synergy': mean_synergy,
        'std_synergy': std_synergy,
        'min_synergy': min_synergy,
        'max_synergy': max_synergy,
        'synergy_range': synergy_range,
        'coefficient_of_variation': cv_synergy,
        'scale_invariance': scale_invariance,
        'critical_depth': int(critical_depth)
    }


def main():
    """Execute hierarchical synergy analysis."""
    print("=" * 70)
    print("CYCLE 266: HIERARCHICAL SYNERGY ANALYSIS - H1×H2")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES_PER_CONDITION}")
    print(f"Depth stratification: 0-{DEPTH_LIMIT}")
    print(f"Paradigm: Mechanism validation (depth-stratified)")
    print()

    # Define 4 conditions
    conditions = [
        MechanismCondition(h1_enabled=False, h2_enabled=False),
        MechanismCondition(h1_enabled=True, h2_enabled=False),
        MechanismCondition(h1_enabled=False, h2_enabled=True),
        MechanismCondition(h1_enabled=True, h2_enabled=True)
    ]

    print("EXPERIMENTAL CONDITIONS:")
    print("-" * 70)
    for i, cond in enumerate(conditions, 1):
        print(f"[{i}/4] {cond}")
    print()

    # Run all conditions
    results = {}
    for i, condition in enumerate(conditions, 1):
        print(f"[{i}/4] Running {condition}...")
        result = run_condition(condition)
        results[str(condition)] = result
        print(f"  Overall mean population: {result['overall_mean_population']:.4f}")
        print(f"  Depth distribution: {[result['depth_mean_population'][str(d)] for d in range(DEPTH_LIMIT + 1)]}")
        print()

    # Compute depth-stratified synergy
    print("=" * 70)
    print("HIERARCHICAL SYNERGY ANALYSIS")
    print("=" * 70)
    hierarchical_analysis = compute_depth_stratified_synergy(results)

    print(f"Mean synergy across depths: {hierarchical_analysis['mean_synergy']:.4f}")
    print(f"Std synergy: {hierarchical_analysis['std_synergy']:.4f}")
    print(f"Synergy range: [{hierarchical_analysis['min_synergy']:.4f}, {hierarchical_analysis['max_synergy']:.4f}]")
    print(f"Coefficient of variation: {hierarchical_analysis['coefficient_of_variation']:.4f}")
    print(f"Scale invariance: {hierarchical_analysis['scale_invariance']}")
    print(f"Critical depth (max synergy): {hierarchical_analysis['critical_depth']}")
    print()
    print("Depth-specific synergies:")
    print("-" * 70)
    for depth in range(DEPTH_LIMIT + 1):
        ds = hierarchical_analysis['depth_synergies'][depth]
        print(f"  Depth {depth}: synergy={ds['synergy']:6.3f} ({ds['classification']:13s}) | "
              f"obs={ds['observed_h1h2']:6.2f}, pred={ds['predicted_h1h2']:6.2f}")
    print()

    # NRM validation
    if hierarchical_analysis['coefficient_of_variation'] < 0.2:
        print("✅ NRM PREDICTION VALIDATED: Strong scale invariance detected")
        print("   Synergy patterns consistent across fractal depth levels")
    elif hierarchical_analysis['coefficient_of_variation'] < 0.5:
        print("⚠️  NRM PREDICTION PARTIALLY VALIDATED: Moderate scale invariance")
        print("   Some depth-specific variation, but overall pattern consistent")
    else:
        print("❌ NRM PREDICTION CHALLENGED: Weak scale invariance")
        print("   Significant depth-specific interaction patterns detected")
    print()

    # Save results
    output = {
        'experiment': 'Cycle 266: Hierarchical synergy analysis (H1×H2)',
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'cycles_per_condition': CYCLES_PER_CONDITION,
            'max_agents': MAX_AGENTS,
            'initial_energy': INITIAL_ENERGY,
            'depth_limit': DEPTH_LIMIT,
            'pooling_share_rate': POOLING_SHARE_RATE,
            'sources_bonus_rate': SOURCES_BONUS_RATE,
            'resonance_threshold': RESONANCE_THRESHOLD
        },
        'conditions': results,
        'hierarchical_analysis': hierarchical_analysis
    }

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print(f"Results saved: {RESULTS_FILE}")
    print("=" * 70)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
