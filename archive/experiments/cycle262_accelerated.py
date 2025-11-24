#!/usr/bin/env python3
"""
Cycle 262: 3-Way Factorial Interaction - H1 × H2 × H5 (ACCELERATED)
(Energy Pooling × Reality Sources × Energy Recovery)

ACCELERATED VERSION FOR FAST EXECUTION
"""

import sys
import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Import from existing modules
sys.path.append(os.path.abspath("."))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

# Experimental parameters
MAX_AGENTS = 100
INITIAL_ENERGY = 130.0
DEPTH_LIMIT = 7
CYCLES_PER_CONDITION = 200 # ACCELERATED from 3000

# Mechanism parameters (from Paper 3)
POOLING_SHARE_RATE = 0.10  # H1: 10% energy sharing in clusters
SOURCES_BONUS_RATE = 0.005  # H2: 0.5% boost per reality sample
RECOVERY_MULTIPLIER = 2.0   # H5: 2× energy recovery rate

RESONANCE_THRESHOLD = 0.85

# Results path
RESULTS_FILE = Path("experiments/results/cycle262_h1h2h5_3way_factorial_results.json")


@dataclass
class Mechanism3WayCondition:
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
        phase=bridge.reality_to_phase(reality.get_system_metrics()).pi_phase
    )

    # Agent list
    agents = [root]
    population_history = []

    # Main simulation loop
    for cycle in range(CYCLES_PER_CONDITION):
        population_history.append(len(agents))

        # Agent evolution
        for agent in agents:
            agent.evolve(delta_time=1.0)

        # H1: Energy Pooling
        if condition.h1_pooling:
            clusters = composition_engine.detect_clusters(agents)
            for cluster_agents in clusters:
                if len(cluster_agents) > 1:
                    total_energy = sum(a.energy for a in cluster_agents)
                    shared_energy = total_energy * POOLING_SHARE_RATE
                    per_agent_share = shared_energy / len(cluster_agents)
                    for agent in cluster_agents:
                        agent.energy = min(agent.energy + per_agent_share, 200.0)

        # H2: Reality Sources
        if condition.h2_sources:
            for agent in agents:
                extra_metrics = reality.get_system_metrics()
                # Simple metric extraction (mocked if failing)
                try:
                    cpu = extra_metrics.get('cpu_percent', 50)
                    mem = extra_metrics.get('memory_percent', 50)
                except:
                    cpu, mem = 50, 50
                    
                available_capacity = (100 - cpu) + (100 - mem)
                bonus_energy = SOURCES_BONUS_RATE * available_capacity
                agent.energy = min(agent.energy + bonus_energy, 200.0)

        # H5: Energy Recovery
        if condition.h5_recovery:
            for agent in agents:
                try:
                    extra_metrics = reality.get_system_metrics()
                    cpu = extra_metrics.get('cpu_percent', 50)
                    mem = extra_metrics.get('memory_percent', 50)
                except:
                    cpu, mem = 50, 50
                    
                available_capacity = (100 - cpu) + (100 - mem)
                recovery_boost = 0.01 * available_capacity * RECOVERY_MULTIPLIER
                agent.energy = min(agent.energy + recovery_boost, 200.0)

        # Spawn new agents
        for agent in list(agents):
            if agent.energy >= 10.0 and agent.depth < DEPTH_LIMIT and len(agents) < MAX_AGENTS:
                child_id = f"{agent.agent_id}_child_{cycle}"
                child_phase = bridge.reality_to_phase(reality.get_system_metrics()).pi_phase
                child = FractalAgent(
                    agent_id=child_id,
                    depth=agent.depth + 1,
                    energy=10.0,
                    phase=child_phase
                )
                # Link parent/child manually as FractalAgent might not do it in init
                child.state.parent_id = agent.agent_id
                agent.state.children_ids.add(child.agent_id)
                
                agents.append(child)
                agent.children.append(child)
                agent.energy -= 10.0

        # Remove dead agents
        agents = [a for a in agents if a.energy > 0]
        
        # Rescue if empty
        if not agents:
             root = FractalAgent(
                agent_id=f"root_rescue_{cycle}",
                depth=0,
                energy=INITIAL_ENERGY,
                phase=bridge.reality_to_phase(reality.get_system_metrics()).pi_phase
            )
             agents.append(root)

    mean_population = float(np.mean(population_history))
    max_population = int(np.max(population_history)) if population_history else 0

    return {
        'mean_population': mean_population,
        'max_population': max_population,
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
    """
    # Extract mean populations
    p000 = results['000']['mean_population']
    p100 = results['100']['mean_population']
    p010 = results['010']['mean_population']
    p001 = results['001']['mean_population']
    p110 = results['110']['mean_population']
    p101 = results['101']['mean_population']
    p011 = results['011']['mean_population']
    p111 = results['111']['mean_population']

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
    print("CYCLE 262: 3-WAY FACTORIAL - H1 × H2 × H5 (ACCELERATED)")
    print("=" * 70)
    
    # Define 8 conditions (2^3 factorial) - Using binary codes for aggregator compatibility
    conditions = [
        Mechanism3WayCondition("000", h1_pooling=False, h2_sources=False, h5_recovery=False),
        Mechanism3WayCondition("100", h1_pooling=True, h2_sources=False, h5_recovery=False),
        Mechanism3WayCondition("010", h1_pooling=False, h2_sources=True, h5_recovery=False),
        Mechanism3WayCondition("001", h1_pooling=False, h2_sources=False, h5_recovery=True),
        Mechanism3WayCondition("110", h1_pooling=True, h2_sources=True, h5_recovery=False),
        Mechanism3WayCondition("101", h1_pooling=True, h2_sources=False, h5_recovery=True),
        Mechanism3WayCondition("011", h1_pooling=False, h2_sources=True, h5_recovery=True),
        Mechanism3WayCondition("111", h1_pooling=True, h2_sources=True, h5_recovery=True)
    ]

    # Run all conditions

    results = {}
    for i, condition in enumerate(conditions, 1):
        print(f"[{i}/8] Running {condition.name}...")
        result = run_condition(condition)
        results[condition.name] = result
        print(f"  Mean population: {result['mean_population']:.4f}")

    print("=" * 70)
    print("3-WAY SYNERGY ANALYSIS")
    print("=" * 70)
    synergy_analysis = analyze_3way_synergy(results)

    print(f"3-way interaction: {synergy_analysis['3way_interaction']:.4f}")
    print(f"Classification: {synergy_analysis['classification']}")
    
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    output = {
        'experiment': 'Cycle 262: H1×H2×H5 3-way factorial',
        'timestamp': datetime.now().isoformat(),
        'conditions': results,
        'synergy_analysis': synergy_analysis
    }
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {RESULTS_FILE}")
    return 0

if __name__ == "__main__":
    sys.exit(main())