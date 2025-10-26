#!/usr/bin/env python3
"""
Cycle 262: 3-Way Factorial Interaction - H1 × H2 × H5
(Energy Pooling × Reality Sources × Energy Recovery)

Purpose: Test for emergent 3-way synergy beyond pairwise interactions
  - Paper 3 found: H1×H2 synergistic, H1×H5 synergistic
  - Hypothesis: H1×H2×H5 exhibits super-synergy (non-linear interaction)
  - Prediction: 3-way > sum of 2-way synergies

Experimental Design:
  - 8 conditions (2^3 factorial):
    000: OFF-OFF-OFF (baseline)
    100: H1-only
    010: H2-only
    001: H5-only
    110: H1×H2
    101: H1×H5
    011: H2×H5
    111: H1×H2×H5 (full combination)

  - Cycles: 3000 per condition (deterministic n=1)
  - Paradigm: Mechanism validation
  - Synergy detection: 3-way interaction term

Analysis:
  Main effects: H1, H2, H5 (from single-mechanism conditions)
  2-way interactions: H1×H2, H1×H5, H2×H5
  3-way interaction: H1×H2×H5 (super-synergy test)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26
Cycle: 262 (Paper 4 initiation)
Framework: Nested Resonance Memory (composition-decomposition dynamics)
License: GPL-3.0
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Import from existing modules (using C255 proven pattern)
sys.path.append(str(Path(__file__).parent.parent))

from code.core.reality_interface import RealityInterface
from code.bridge.transcendental_bridge import TranscendentalBridge
from code.fractal.fractal_agent import FractalAgent
from code.fractal.composition_engine import CompositionEngine

# Experimental parameters
MAX_AGENTS = 100
INITIAL_ENERGY = 130.0
DEPTH_LIMIT = 7
CYCLES_PER_CONDITION = 3000

# Mechanism parameters (from Paper 3)
POOLING_SHARE_RATE = 0.10  # H1: 10% energy sharing in clusters
SOURCES_BONUS_RATE = 0.005  # H2: 0.5% boost per reality sample
RECOVERY_MULTIPLIER = 2.0   # H5: 2× energy recovery rate

RESONANCE_THRESHOLD = 0.85

# Results path
RESULTS_FILE = Path(__file__).parent / "results" / "cycle262_h1h2h5_3way_factorial_results.json"


@dataclass
class Mechanism3WayCondition:
    """
    3-way factorial condition for H1 (pooling), H2 (sources), H5 (recovery).
    """
    name: str
    h1_pooling: bool
    h2_sources: bool
    h5_recovery: bool

    def __str__(self):
        h1 = "H1:ON" if self.h1_pooling else "H1:OFF"
        h2 = "H2:ON" if self.h2_sources else "H2:OFF"
        h5 = "H5:ON" if self.h5_recovery else "H5:OFF"
        return f"{self.name} ({h1}, {h2}, {h5})"


def run_condition(condition: Mechanism3WayCondition) -> Dict:
    """
    Run single 3-way factorial condition for 3000 cycles.

    Returns population history and final mean.
    """
    # Initialize reality interface and bridge
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Initialize composition engine (resonance detection)
    composition_engine = CompositionEngine(resonance_threshold=RESONANCE_THRESHOLD)

    # Create root agent
    root = FractalAgent(
        agent_id="root",
        depth=0,
        energy=INITIAL_ENERGY,
        phase=bridge.reality_to_phase(reality.get_system_metrics())
    )

    # Agent list (direct management, C177 pattern)
    agents = [root]
    population_history = []

    # Main simulation loop
    for cycle in range(CYCLES_PER_CONDITION):
        # Record population
        population_history.append(len(agents))

        # Agent evolution (transcendental dynamics)
        for agent in agents:
            metrics = reality.get_system_metrics()
            phase = bridge.reality_to_phase(metrics)
            agent.evolve(phase, delta_t=1.0)

        # H1: Energy Pooling (if enabled)
        if condition.h1_pooling:
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
        if condition.h2_sources:
            for agent in agents:
                extra_metrics = reality.get_system_metrics()
                available_capacity = (100 - extra_metrics['cpu_percent']) + \
                                   (100 - extra_metrics['memory_percent'])
                bonus_energy = SOURCES_BONUS_RATE * available_capacity
                agent.energy = min(agent.energy + bonus_energy, 200.0)

        # H5: Energy Recovery (if enabled)
        if condition.h5_recovery:
            for agent in agents:
                recovery_metrics = reality.get_system_metrics()
                available_capacity = (100 - recovery_metrics['cpu_percent']) + \
                                   (100 - recovery_metrics['memory_percent'])
                recovery_boost = 0.01 * available_capacity * RECOVERY_MULTIPLIER
                agent.energy = min(agent.energy + recovery_boost, 200.0)

        # Spawn new agents if energy threshold met
        for agent in list(agents):  # Copy list to avoid modification during iteration
            if agent.energy >= 10.0 and agent.depth < DEPTH_LIMIT and len(agents) < MAX_AGENTS:
                # Create child agent
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

        # Remove dead agents (energy exhaustion)
        agents = [a for a in agents if a.energy > 0]

    # Compute summary statistics
    mean_population = float(np.mean(population_history))

    return {
        'mean_population': mean_population,
        'population_history': population_history,
        'final_population': len(agents),
        'condition': {
            'h1_pooling': condition.h1_pooling,
            'h2_sources': condition.h2_sources,
            'h5_recovery': condition.h5_recovery
        }
    }


def analyze_3way_synergy(results: Dict[str, Dict]) -> Dict:
    """
    Compute 3-way interaction synergy beyond pairwise effects.

    Synergy formula:
      3-way interaction = observed(111) - predicted_from_lower_order

      where predicted = baseline + main_effects + 2way_interactions

      main_effects = (100-000) + (010-000) + (001-000)
      2way_interactions = [(110-000)-(100-000)-(010-000)] +
                         [(101-000)-(100-000)-(001-000)] +
                         [(011-000)-(010-000)-(001-000)]
    """
    # Extract mean populations
    p000 = results['OFF-OFF-OFF']['mean_population']
    p100 = results['H1-only']['mean_population']
    p010 = results['H2-only']['mean_population']
    p001 = results['H5-only']['mean_population']
    p110 = results['H1×H2']['mean_population']
    p101 = results['H1×H5']['mean_population']
    p011 = results['H2×H5']['mean_population']
    p111 = results['H1×H2×H5']['mean_population']

    # Main effects
    effect_h1 = p100 - p000
    effect_h2 = p010 - p000
    effect_h5 = p001 - p000

    # 2-way interactions
    interaction_h1h2 = p110 - p000 - effect_h1 - effect_h2
    interaction_h1h5 = p101 - p000 - effect_h1 - effect_h5
    interaction_h2h5 = p011 - p000 - effect_h2 - effect_h5

    # Predicted value from lower-order terms
    predicted_p111 = p000 + effect_h1 + effect_h2 + effect_h5 + \
                    interaction_h1h2 + interaction_h1h5 + interaction_h2h5

    # 3-way interaction (super-synergy)
    interaction_3way = p111 - predicted_p111

    # Classification
    threshold = 0.1
    if interaction_3way > threshold:
        classification = "SUPER-SYNERGISTIC"
    elif interaction_3way < -threshold:
        classification = "SUPER-ANTAGONISTIC"
    else:
        classification = "ADDITIVE (no 3-way interaction)"

    return {
        '3way_interaction': float(interaction_3way),
        'classification': classification,
        'observed_111': float(p111),
        'predicted_111': float(predicted_p111),
        'main_effects': {
            'H1': float(effect_h1),
            'H2': float(effect_h2),
            'H5': float(effect_h5)
        },
        '2way_interactions': {
            'H1×H2': float(interaction_h1h2),
            'H1×H5': float(interaction_h1h5),
            'H2×H5': float(interaction_h2h5)
        }
    }


def main():
    """Execute 3-way factorial experiment."""
    print("=" * 70)
    print("CYCLE 262: 3-WAY FACTORIAL - H1 × H2 × H5")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES_PER_CONDITION}")
    print(f"Paradigm: Mechanism validation (deterministic, n=1)")
    print()

    # Define 8 conditions (2^3 factorial)
    conditions = [
        Mechanism3WayCondition("OFF-OFF-OFF", h1_pooling=False, h2_sources=False, h5_recovery=False),
        Mechanism3WayCondition("H1-only", h1_pooling=True, h2_sources=False, h5_recovery=False),
        Mechanism3WayCondition("H2-only", h1_pooling=False, h2_sources=True, h5_recovery=False),
        Mechanism3WayCondition("H5-only", h1_pooling=False, h2_sources=False, h5_recovery=True),
        Mechanism3WayCondition("H1×H2", h1_pooling=True, h2_sources=True, h5_recovery=False),
        Mechanism3WayCondition("H1×H5", h1_pooling=True, h2_sources=False, h5_recovery=True),
        Mechanism3WayCondition("H2×H5", h1_pooling=False, h2_sources=True, h5_recovery=True),
        Mechanism3WayCondition("H1×H2×H5", h1_pooling=True, h2_sources=True, h5_recovery=True)
    ]

    print("EXPERIMENTAL CONDITIONS:")
    print("-" * 70)
    for i, cond in enumerate(conditions, 1):
        print(f"[{i}/8] Condition: {cond}")
    print()

    # Run all conditions
    results = {}
    for i, condition in enumerate(conditions, 1):
        print(f"[{i}/8] Running {condition.name}...")
        result = run_condition(condition)
        results[condition.name] = result
        print(f"  Mean population: {result['mean_population']:.4f}")
        print()

    # Analyze 3-way synergy
    print("=" * 70)
    print("3-WAY SYNERGY ANALYSIS")
    print("=" * 70)
    synergy_analysis = analyze_3way_synergy(results)

    print(f"3-way interaction: {synergy_analysis['3way_interaction']:.4f}")
    print(f"Classification: {synergy_analysis['classification']}")
    print(f"Observed H1×H2×H5: {synergy_analysis['observed_111']:.4f}")
    print(f"Predicted (from lower-order): {synergy_analysis['predicted_111']:.4f}")
    print()
    print("Main effects:")
    for mech, effect in synergy_analysis['main_effects'].items():
        print(f"  {mech}: {effect:.4f}")
    print()
    print("2-way interactions:")
    for pair, interaction in synergy_analysis['2way_interactions'].items():
        print(f"  {pair}: {interaction:.4f}")
    print()

    # Save results
    output = {
        'experiment': 'Cycle 262: H1×H2×H5 3-way factorial',
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'cycles_per_condition': CYCLES_PER_CONDITION,
            'max_agents': MAX_AGENTS,
            'initial_energy': INITIAL_ENERGY,
            'depth_limit': DEPTH_LIMIT,
            'pooling_share_rate': POOLING_SHARE_RATE,
            'sources_bonus_rate': SOURCES_BONUS_RATE,
            'recovery_multiplier': RECOVERY_MULTIPLIER,
            'resonance_threshold': RESONANCE_THRESHOLD
        },
        'conditions': results,
        'synergy_analysis': synergy_analysis
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
