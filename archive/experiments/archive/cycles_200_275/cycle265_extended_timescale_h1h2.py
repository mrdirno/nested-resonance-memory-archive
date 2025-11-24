#!/usr/bin/env python3
"""
Cycle 265: Extended Timescale Dynamics - H1×H2 Long-Run Analysis
(Energy Pooling × Reality Sources)

Purpose: Test synergy persistence and phase transitions over extended timescales
  - Paper 3 found: H1×H2 synergistic at 3000 cycles (saturation phase)
  - Question: Do synergies persist, adapt, or evolve over 10,000+ cycles?
  - Hypothesis: Early synergies may fade or strengthen over time

Experimental Design:
  - Selected pair: H1×H2 (known synergistic)
  - Cycles: 10,000 (extended from 3000)
  - 4 conditions: OFF-OFF, H1-only, H2-only, H1×H2
  - Temporal analysis: Sliding window synergy (1000-cycle windows)

Analysis:
  - Synergy evolution: synergy(t) over time
  - Phase transitions: Detect timepoints where classification changes
  - Adaptation patterns: Constant, increasing, decreasing, oscillating
  - Multi-generational effects: Depth distribution evolution

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26
Cycle: 265 (Paper 4 extensions - temporal dynamics)
Framework: Nested Resonance Memory (perpetual motion validation)
License: GPL-3.0
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

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
CYCLES_PER_CONDITION = 10000  # Extended from 3000
WINDOW_SIZE = 1000  # For temporal analysis

# Mechanism parameters (from Paper 3)
POOLING_SHARE_RATE = 0.10
SOURCES_BONUS_RATE = 0.005

RESONANCE_THRESHOLD = 0.85

# Results path
RESULTS_FILE = Path(__file__).parent / "results" / "cycle265_extended_timescale_h1h2_results.json"


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
    Run single condition for 10,000 cycles with detailed temporal tracking.

    Returns population history and temporal analysis.
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
    population_history = []
    depth_distribution_history = []  # Track depth evolution

    # Main simulation loop
    for cycle in range(CYCLES_PER_CONDITION):
        # Record population
        population_history.append(len(agents))

        # Record depth distribution every 100 cycles
        if cycle % 100 == 0:
            depth_counts = {}
            for agent in agents:
                depth_counts[agent.depth] = depth_counts.get(agent.depth, 0) + 1
            depth_distribution_history.append({
                'cycle': cycle,
                'depth_counts': depth_counts
            })

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

    # Compute summary statistics
    mean_population = float(np.mean(population_history))

    return {
        'mean_population': mean_population,
        'population_history': population_history,
        'depth_distribution_history': depth_distribution_history,
        'final_population': len(agents),
        'condition': {
            'h1_enabled': condition.h1_enabled,
            'h2_enabled': condition.h2_enabled
        }
    }


def compute_windowed_synergy(results: Dict[str, Dict], window_size: int) -> List[Dict]:
    """
    Compute synergy in sliding windows across time.

    Returns temporal synergy profile.
    """
    # Extract population histories
    off_off_history = results['OFF-OFF']['population_history']
    h1_only_history = results['H1-only']['population_history']
    h2_only_history = results['H2-only']['population_history']
    h1h2_history = results['H1×H2']['population_history']

    temporal_synergy = []
    num_windows = len(off_off_history) // window_size

    for w in range(num_windows):
        start = w * window_size
        end = start + window_size

        # Compute mean population in this window
        off_off_mean = float(np.mean(off_off_history[start:end]))
        h1_only_mean = float(np.mean(h1_only_history[start:end]))
        h2_only_mean = float(np.mean(h2_only_history[start:end]))
        h1h2_mean = float(np.mean(h1h2_history[start:end]))

        # Compute synergy
        h1_effect = h1_only_mean - off_off_mean
        h2_effect = h2_only_mean - off_off_mean
        additive_prediction = off_off_mean + h1_effect + h2_effect
        synergy = h1h2_mean - additive_prediction

        # Classify
        if synergy > 0.1:
            classification = "SYNERGISTIC"
        elif synergy < -0.1:
            classification = "ANTAGONISTIC"
        else:
            classification = "ADDITIVE"

        temporal_synergy.append({
            'window_index': w,
            'cycle_range': [start, end],
            'synergy': float(synergy),
            'classification': classification,
            'observed_h1h2': float(h1h2_mean),
            'predicted_h1h2': float(additive_prediction)
        })

    return temporal_synergy


def analyze_phase_transitions(temporal_synergy: List[Dict]) -> Dict:
    """
    Detect phase transitions in synergy classification over time.

    Returns transition analysis.
    """
    classifications = [w['classification'] for w in temporal_synergy]
    synergy_values = [w['synergy'] for w in temporal_synergy]

    # Detect transitions
    transitions = []
    for i in range(1, len(classifications)):
        if classifications[i] != classifications[i-1]:
            transitions.append({
                'window_index': i,
                'cycle': temporal_synergy[i]['cycle_range'][0],
                'from_classification': classifications[i-1],
                'to_classification': classifications[i],
                'synergy_before': float(synergy_values[i-1]),
                'synergy_after': float(synergy_values[i])
            })

    # Compute temporal statistics
    mean_synergy = float(np.mean(synergy_values))
    std_synergy = float(np.std(synergy_values))
    min_synergy = float(min(synergy_values))
    max_synergy = float(max(synergy_values))

    # Trend analysis (linear regression on synergy over time)
    x = np.arange(len(synergy_values))
    y = np.array(synergy_values)
    if len(x) > 1:
        slope, intercept = np.polyfit(x, y, 1)
        trend = "INCREASING" if slope > 0.01 else ("DECREASING" if slope < -0.01 else "STABLE")
    else:
        slope, intercept, trend = 0.0, 0.0, "INSUFFICIENT_DATA"

    return {
        'transitions': transitions,
        'num_transitions': len(transitions),
        'mean_synergy': mean_synergy,
        'std_synergy': std_synergy,
        'min_synergy': min_synergy,
        'max_synergy': max_synergy,
        'trend': trend,
        'trend_slope': float(slope),
        'classification_counts': {
            'SYNERGISTIC': classifications.count('SYNERGISTIC'),
            'ANTAGONISTIC': classifications.count('ANTAGONISTIC'),
            'ADDITIVE': classifications.count('ADDITIVE')
        }
    }


def main():
    """Execute extended timescale experiment."""
    print("=" * 70)
    print("CYCLE 265: EXTENDED TIMESCALE DYNAMICS - H1×H2")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES_PER_CONDITION}")
    print(f"Window size for temporal analysis: {WINDOW_SIZE}")
    print(f"Paradigm: Mechanism validation (extended timescale)")
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
        print(f"  Mean population: {result['mean_population']:.4f}")
        print()

    # Compute temporal synergy
    print("=" * 70)
    print("TEMPORAL SYNERGY ANALYSIS")
    print("=" * 70)
    temporal_synergy = compute_windowed_synergy(results, WINDOW_SIZE)

    print(f"Number of windows: {len(temporal_synergy)}")
    print()
    print("Synergy evolution:")
    for w in temporal_synergy:
        print(f"  Window {w['window_index']+1:2d} (cycles {w['cycle_range'][0]:5d}-{w['cycle_range'][1]:5d}): "
              f"synergy={w['synergy']:6.3f} ({w['classification']})")
    print()

    # Analyze phase transitions
    phase_analysis = analyze_phase_transitions(temporal_synergy)
    print("PHASE TRANSITION ANALYSIS:")
    print("-" * 70)
    print(f"Mean synergy: {phase_analysis['mean_synergy']:.4f}")
    print(f"Std synergy: {phase_analysis['std_synergy']:.4f}")
    print(f"Synergy range: [{phase_analysis['min_synergy']:.4f}, {phase_analysis['max_synergy']:.4f}]")
    print(f"Trend: {phase_analysis['trend']} (slope={phase_analysis['trend_slope']:.6f})")
    print()
    print("Classification distribution:")
    for classification, count in phase_analysis['classification_counts'].items():
        print(f"  {classification}: {count}/{len(temporal_synergy)} windows")
    print()

    if phase_analysis['num_transitions'] > 0:
        print(f"Phase transitions detected: {phase_analysis['num_transitions']}")
        for t in phase_analysis['transitions']:
            print(f"  Cycle {t['cycle']}: {t['from_classification']} → {t['to_classification']}")
    else:
        print("No phase transitions detected (synergy classification stable)")
    print()

    # Save results
    output = {
        'experiment': 'Cycle 265: Extended timescale dynamics (H1×H2)',
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'cycles_per_condition': CYCLES_PER_CONDITION,
            'window_size': WINDOW_SIZE,
            'max_agents': MAX_AGENTS,
            'initial_energy': INITIAL_ENERGY,
            'depth_limit': DEPTH_LIMIT,
            'pooling_share_rate': POOLING_SHARE_RATE,
            'sources_bonus_rate': SOURCES_BONUS_RATE,
            'resonance_threshold': RESONANCE_THRESHOLD
        },
        'conditions': results,
        'temporal_synergy': temporal_synergy,
        'phase_analysis': phase_analysis
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
