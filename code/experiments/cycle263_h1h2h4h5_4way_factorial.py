#!/usr/bin/env python3
"""
Cycle 263: 4-Way Full Factorial - H1 × H2 × H4 × H5
(Energy Pooling × Reality Sources × Spawn Throttling × Energy Recovery)

Purpose: Complete synergy landscape mapping across all four mechanisms
  - Paper 3 found: pairwise interactions (6 pairs)
  - Cycle 262 found: 3-way interactions (H1×H2×H5)
  - Hypothesis: 4-way interaction captures full emergent complexity

Experimental Design:
  - 16 conditions (2^4 factorial):
    0000: OFF-OFF-OFF-OFF (baseline)
    [Single mechanisms - 4 conditions]
    1000, 0100, 0010, 0001
    [Pairwise - 6 conditions]
    1100, 1010, 1001, 0110, 0101, 0011
    [3-way - 4 conditions]
    1110, 1101, 1011, 0111
    [4-way - 1 condition]
    1111: H1×H2×H4×H5 (full combination)

  - Cycles: 3000 per condition (deterministic n=1)
  - Paradigm: Mechanism validation
  - Synergy detection: Up to 4-way interaction terms

Analysis:
  Main effects: H1, H2, H4, H5
  2-way interactions: 6 pairs (from Paper 3)
  3-way interactions: 4 triads
  4-way interaction: Ultimate emergent synergy test

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26
Cycle: 263 (Paper 4 - full factorial)
Framework: Nested Resonance Memory (complete interaction landscape)
License: GPL-3.0
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
from itertools import product

# Import from existing modules
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

# Mechanism parameters
POOLING_SHARE_RATE = 0.10
SOURCES_BONUS_RATE = 0.005
THROTTLE_COOLDOWN = 100
RECOVERY_MULTIPLIER = 2.0

RESONANCE_THRESHOLD = 0.85

# Results path
RESULTS_FILE = Path(__file__).parent / "results" / "cycle263_h1h2h4h5_4way_factorial_results.json"


@dataclass
class Mechanism4WayCondition:
    """
    4-way factorial condition for H1, H2, H4, H5.
    """
    name: str
    h1_pooling: bool
    h2_sources: bool
    h4_throttling: bool
    h5_recovery: bool

    def __str__(self):
        h1 = "H1:ON" if self.h1_pooling else "H1:OFF"
        h2 = "H2:ON" if self.h2_sources else "H2:OFF"
        h4 = "H4:ON" if self.h4_throttling else "H4:OFF"
        h5 = "H5:ON" if self.h5_recovery else "H5:OFF"
        return f"{self.name} ({h1}, {h2}, {h4}, {h5})"

    def to_binary_code(self) -> str:
        """Return 4-bit binary code (e.g., '1011' for H1-OFF-H4-H5)."""
        bits = [
            '1' if self.h1_pooling else '0',
            '1' if self.h2_sources else '0',
            '1' if self.h4_throttling else '0',
            '1' if self.h5_recovery else '0'
        ]
        return ''.join(bits)


def run_condition(condition: Mechanism4WayCondition) -> Dict:
    """
    Run single 4-way factorial condition for 3000 cycles.

    Returns population history and final mean.
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

    # Agent list (C177 pattern)
    agents = [root]
    population_history = []
    last_spawn_cycle = {}  # For H4 throttling tracking

    # Main simulation loop
    for cycle in range(CYCLES_PER_CONDITION):
        # Record population
        population_history.append(len(agents))

        # Agent evolution
        for agent in agents:
            # Note: FractalAgent.evolve() takes delta_time only, not phase
            agent.evolve(delta_time=1.0)

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

        # Spawn new agents (with H4 throttling if enabled)
        for agent in list(agents):
            if agent.energy >= 10.0 and agent.depth < DEPTH_LIMIT and len(agents) < MAX_AGENTS:
                # H4: Spawn Throttling (if enabled)
                if condition.h4_throttling:
                    last_spawn = last_spawn_cycle.get(agent.agent_id, -THROTTLE_COOLDOWN)
                    cycles_since_spawn = cycle - last_spawn
                    if cycles_since_spawn < THROTTLE_COOLDOWN:
                        continue  # Skip spawn due to throttle

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

                # Track spawn time (for H4)
                if condition.h4_throttling:
                    last_spawn_cycle[agent.agent_id] = cycle

        # Remove dead agents
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
            'h4_throttling': condition.h4_throttling,
            'h5_recovery': condition.h5_recovery
        }
    }


def analyze_4way_synergy(results: Dict[str, Dict]) -> Dict:
    """
    Compute 4-way interaction synergy decomposition.

    Decomposition:
      observed = baseline + main_effects + 2way + 3way + 4way

      4way_interaction = observed(1111) - predicted_from_lower_order

    This is the ultimate test: do all four mechanisms together produce
    emergent effects beyond 1-way, 2-way, and 3-way interactions?
    """
    # Extract mean populations using binary codes
    p = {}
    for name, data in results.items():
        cond = data['condition']
        code = (
            ('1' if cond['h1_pooling'] else '0') +
            ('1' if cond['h2_sources'] else '0') +
            ('1' if cond['h4_throttling'] else '0') +
            ('1' if cond['h5_recovery'] else '0')
        )
        p[code] = data['mean_population']

    # Baseline
    baseline = p['0000']

    # Main effects
    effect_h1 = p['1000'] - baseline
    effect_h2 = p['0100'] - baseline
    effect_h4 = p['0010'] - baseline
    effect_h5 = p['0001'] - baseline

    # 2-way interactions (6 pairs)
    int_h1h2 = p['1100'] - baseline - effect_h1 - effect_h2
    int_h1h4 = p['1010'] - baseline - effect_h1 - effect_h4
    int_h1h5 = p['1001'] - baseline - effect_h1 - effect_h5
    int_h2h4 = p['0110'] - baseline - effect_h2 - effect_h4
    int_h2h5 = p['0101'] - baseline - effect_h2 - effect_h5
    int_h4h5 = p['0011'] - baseline - effect_h4 - effect_h5

    # 3-way interactions (4 triads)
    int_h1h2h4 = (p['1110'] - baseline - effect_h1 - effect_h2 - effect_h4 -
                  int_h1h2 - int_h1h4 - int_h2h4)
    int_h1h2h5 = (p['1101'] - baseline - effect_h1 - effect_h2 - effect_h5 -
                  int_h1h2 - int_h1h5 - int_h2h5)
    int_h1h4h5 = (p['1011'] - baseline - effect_h1 - effect_h4 - effect_h5 -
                  int_h1h4 - int_h1h5 - int_h4h5)
    int_h2h4h5 = (p['0111'] - baseline - effect_h2 - effect_h4 - effect_h5 -
                  int_h2h4 - int_h2h5 - int_h4h5)

    # Predicted value from lower-order terms
    predicted_1111 = (baseline +
                      effect_h1 + effect_h2 + effect_h4 + effect_h5 +
                      int_h1h2 + int_h1h4 + int_h1h5 + int_h2h4 + int_h2h5 + int_h4h5 +
                      int_h1h2h4 + int_h1h2h5 + int_h1h4h5 + int_h2h4h5)

    # 4-way interaction (ultimate emergent synergy)
    interaction_4way = p['1111'] - predicted_1111

    # Classification
    threshold = 0.1
    if interaction_4way > threshold:
        classification = "HYPER-SYNERGISTIC"
    elif interaction_4way < -threshold:
        classification = "HYPER-ANTAGONISTIC"
    else:
        classification = "PREDICTABLE (no 4-way interaction)"

    return {
        '4way_interaction': float(interaction_4way),
        'classification': classification,
        'observed_1111': float(p['1111']),
        'predicted_1111': float(predicted_1111),
        'main_effects': {
            'H1': float(effect_h1),
            'H2': float(effect_h2),
            'H4': float(effect_h4),
            'H5': float(effect_h5)
        },
        '2way_interactions': {
            'H1×H2': float(int_h1h2),
            'H1×H4': float(int_h1h4),
            'H1×H5': float(int_h1h5),
            'H2×H4': float(int_h2h4),
            'H2×H5': float(int_h2h5),
            'H4×H5': float(int_h4h5)
        },
        '3way_interactions': {
            'H1×H2×H4': float(int_h1h2h4),
            'H1×H2×H5': float(int_h1h2h5),
            'H1×H4×H5': float(int_h1h4h5),
            'H2×H4×H5': float(int_h2h4h5)
        }
    }


def main():
    """Execute 4-way full factorial experiment."""
    print("=" * 70)
    print("CYCLE 263: 4-WAY FULL FACTORIAL - H1 × H2 × H4 × H5")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES_PER_CONDITION}")
    print(f"Total conditions: 16 (2^4 factorial)")
    print(f"Paradigm: Mechanism validation (deterministic, n=1)")
    print()

    # Generate all 16 conditions programmatically
    conditions = []
    for h1, h2, h4, h5 in product([False, True], repeat=4):
        # Generate name
        bits = [h1, h2, h4, h5]
        if not any(bits):
            name = "OFF-OFF-OFF-OFF"
        elif all(bits):
            name = "H1×H2×H4×H5"
        else:
            active = []
            if h1: active.append("H1")
            if h2: active.append("H2")
            if h4: active.append("H4")
            if h5: active.append("H5")
            name = "×".join(active) if len(active) > 1 else active[0] + "-only"

        conditions.append(Mechanism4WayCondition(
            name=name,
            h1_pooling=h1,
            h2_sources=h2,
            h4_throttling=h4,
            h5_recovery=h5
        ))

    print("EXPERIMENTAL CONDITIONS:")
    print("-" * 70)
    for i, cond in enumerate(conditions, 1):
        print(f"[{i:2d}/16] {cond.to_binary_code()}: {cond}")
    print()

    # Run all conditions
    results = {}
    for i, condition in enumerate(conditions, 1):
        print(f"[{i:2d}/16] Running {condition.name}...")
        result = run_condition(condition)
        results[condition.name] = result
        print(f"  Mean population: {result['mean_population']:.4f}")
        print()

    # Analyze 4-way synergy
    print("=" * 70)
    print("4-WAY SYNERGY ANALYSIS")
    print("=" * 70)
    synergy_analysis = analyze_4way_synergy(results)

    print(f"4-way interaction: {synergy_analysis['4way_interaction']:.4f}")
    print(f"Classification: {synergy_analysis['classification']}")
    print(f"Observed H1×H2×H4×H5: {synergy_analysis['observed_1111']:.4f}")
    print(f"Predicted (from 1-way + 2-way + 3-way): {synergy_analysis['predicted_1111']:.4f}")
    print()
    print("Main effects:")
    for mech, effect in synergy_analysis['main_effects'].items():
        print(f"  {mech}: {effect:.4f}")
    print()
    print("2-way interactions:")
    for pair, interaction in synergy_analysis['2way_interactions'].items():
        print(f"  {pair}: {interaction:.4f}")
    print()
    print("3-way interactions:")
    for triad, interaction in synergy_analysis['3way_interactions'].items():
        print(f"  {triad}: {interaction:.4f}")
    print()

    # Save results
    output = {
        'experiment': 'Cycle 263: H1×H2×H4×H5 4-way full factorial',
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'cycles_per_condition': CYCLES_PER_CONDITION,
            'max_agents': MAX_AGENTS,
            'initial_energy': INITIAL_ENERGY,
            'depth_limit': DEPTH_LIMIT,
            'pooling_share_rate': POOLING_SHARE_RATE,
            'sources_bonus_rate': SOURCES_BONUS_RATE,
            'throttle_cooldown': THROTTLE_COOLDOWN,
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
