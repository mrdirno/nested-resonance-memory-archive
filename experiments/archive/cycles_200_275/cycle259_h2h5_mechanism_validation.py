#!/usr/bin/env python3
"""
CYCLE 259: MECHANISM VALIDATION - H2 × H5 Factorial Interaction

Purpose: Test whether Reality Sources (H2) and Energy Recovery (H5) exhibit
         synergistic, antagonistic, or additive effects when combined.

Background:
  - Stochasticity investigation (Cycles 235-254) proved system is deterministic
  - Statistical paradigm fails (σ²=0 across all conditions)
  - Mechanism validation paradigm adopted: Single runs, directional predictions

H2 - Reality Sources:
  Multiple reality sampling sources provide diverse energy inputs, stabilizing
  population dynamics through resource diversification.

H5 - Energy Recovery:
  Boosts energy recovery rate through enhanced reality coupling, stabilizing
  populations by accelerating energy regeneration during low-energy states.

Hypothesis:
  Sources + Recovery = SYNERGISTIC
  Reasoning: sources creates agents, recovery sustains them through faster recharge.
  Expected synergy > 0.1 (recovery extends lifespan of pooled agents)

Mechanism Validation Method:
  - Single deterministic run per condition (n=1, reproducible)
  - 4 conditions: OFF-OFF, ON-OFF, OFF-ON, ON-ON
  - Synergy detection: ON-ON vs (OFF-OFF + H1_effect + H5_effect)
  - Classification: Synergistic (synergy > 0.1), Antagonistic (< -0.1), Additive

Expected Outcomes:
  - OFF-OFF (neither): mean ≈ 0.07 (baseline collapse)
  - ON-OFF (sources only): mean ≈ 0.12 (modest improvement)
  - OFF-ON (recovery only): mean ≈ 0.15 (modest survival boost)
  - ON-ON (both): mean ≈ 2.20 (synergistic amplification, sustained growth)

  Synergy = 2.20 - (0.07 + 0.88 + 0.08) = 1.17 (SYNERGISTIC)

Date: 2025-10-26
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 259 (Phase 2: Paper 3 mechanism validation, post-determinism discovery)
Principal Investigator: Aldrin Payopay (aldrin.gdf@gmail.com)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import sys
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine, FractalSwarm

# Experimental parameters
CYCLES = 3000
MAX_AGENTS = 100
RECOVERY_MULTIPLIER = 2.0  # H5 parameter: 2× energy recovery rate
RESULTS_FILE = Path(__file__).parent / "results" / "cycle259_h2h5_mechanism_validation_results.json"


class MechanismCondition:
    """Wrapper for factorial mechanism conditions."""

    def __init__(self, h2_enabled: bool, h5_enabled: bool):
        """
        Initialize factorial condition.

        Args:
            h2_enabled: Reality sources mechanism active
            h5_enabled: Energy recovery mechanism active
        """
        self.h2_sources = h2_enabled
        self.h5_recovery = h5_enabled
        self.name = f"{'ON' if h2_enabled else 'OFF'}-{'ON' if h5_enabled else 'OFF'}"

    def __str__(self):
        h2 = "H2:ON" if self.h2_sources else "H2:OFF"
        h5 = "H5:ON" if self.h5_recovery else "H5:OFF"
        return f"{self.name} ({h2}, {h5})"


def run_condition(condition: MechanismCondition) -> Dict:
    """
    Run single deterministic experiment with mechanism configuration.

    Args:
        condition: Mechanism condition (H1, H5 settings)

    Returns:
        Dictionary with population metrics
    """
    print(f"  Running {condition}...")
    start_time = time.time()

    # Initialize system
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine(resonance_threshold=0.85)

    # Create root agent
    metrics = reality.get_system_metrics()
    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality,
        initial_energy=130.0  # Fixed initial energy (deterministic)
    )

    # Direct agent list management (C177 pattern)
    agents = [root]

    # Population tracking
    population_history = []

    # Run simulation
    for cycle in range(CYCLES):
        # H2: Reality sources (if enabled)
        if condition.h2_sources:
            # Detect resonance clusters
            cluster_events = composition_engine.detect_clusters(agents)

            # Share energy within each cluster
            for cluster_id, member_ids in composition_engine.clusters.items():
                if len(member_ids) < 2:
                    continue

                cluster_agents = [a for a in agents if a.agent_id in member_ids]

                # Pool 10% of total cluster energy
                total_energy = sum(a.energy for a in cluster_agents)
                shared_energy = total_energy * 0.10
                per_agent_share = shared_energy / len(cluster_agents)

                # Distribute equally to all cluster members
                for agent in cluster_agents:
                    agent.energy = min(agent.energy + per_agent_share, 200.0)

        # Evolve all agents (includes reality-based energy recharge)
        for agent in agents:
            agent.evolve(delta_time=1.0)

        # H5: Energy recovery (if enabled)
        if condition.h5_recovery:
            # Boost energy recovery for all agents (2× multiplier)
            for agent in agents:
                current_energy = agent.energy
                # Sample reality for recovery boost
                recovery_metrics = reality.get_system_metrics()
                available_capacity = (100 - recovery_metrics['cpu_percent']) + \
                                   (100 - recovery_metrics['memory_percent'])
                # Recovery bonus: 1% of available capacity (2× H2 rate)
                recovery_boost = 0.01 * available_capacity * RECOVERY_MULTIPLIER
                agent.energy = min(agent.energy + recovery_boost, 200.0)

        # Spawn new agents if energy threshold met
        for agent in list(agents):  # Copy list to avoid modification during iteration
            if agent.energy >= 10.0 and agent.depth < 7 and len(agents) < MAX_AGENTS:
                # Create child agent
                child_id = f"{agent.agent_id}_child_{cycle}"
                child_metrics = reality.get_system_metrics()
                child = FractalAgent(
                    agent_id=child_id,
                    bridge=bridge,
                    initial_reality=child_metrics,
                    parent_id=agent.agent_id,
                    depth=agent.depth + 1,
                    max_depth=7,
                    reality=reality
                )
                agents.append(child)
                agent.children.append(child)
                agent.energy -= 10.0  # Spawning cost

        # Death (energy depletion)
        agents = [a for a in agents if a.energy >= 1.0]

        # Record population
        population_history.append(len(agents))

    # Compute metrics
    mean_population = np.mean(population_history)
    final_population = population_history[-1]
    max_population = np.max(population_history)
    runtime = time.time() - start_time

    print(f"    → mean={mean_population:.2f}, final={final_population}, max={max_population}, runtime={runtime:.1f}s")

    return {
        'condition': str(condition),
        'h2_sources': condition.h2_sources,
        'h5_recovery': condition.h5_recovery,
        'mean_population': float(mean_population),
        'final_population': int(final_population),
        'max_population': int(max_population),
        'population_history': population_history,
        'runtime_seconds': float(runtime)
    }


def analyze_synergy(results: Dict[str, Dict]) -> Dict:
    """
    Analyze factorial synergy using mechanism validation paradigm.

    Args:
        results: Dictionary of condition results

    Returns:
        Synergy analysis dictionary
    """
    # Extract outcomes
    off_off = results['OFF-OFF']['mean_population']
    on_off = results['ON-OFF']['mean_population']
    off_on = results['OFF-ON']['mean_population']
    on_on = results['ON-ON']['mean_population']

    # Compute individual mechanism effects
    h2_effect = on_off - off_off  # Effect of sources alone
    h5_effect = off_on - off_off  # Effect of recovery alone

    # Additive prediction (null hypothesis: no interaction)
    additive_prediction = off_off + h2_effect + h5_effect

    # Synergy (interaction effect)
    synergy = on_on - additive_prediction

    # Fold-change (interpretable effect size)
    fold_change = on_on / off_off if off_off > 0 else float('inf')

    # Classification (qualitative, threshold-based)
    synergy_threshold = 0.1

    if synergy > synergy_threshold:
        classification = "SYNERGISTIC"
        interpretation = "Reality sources and energy recovery amplify each other"
    elif synergy < -synergy_threshold:
        classification = "ANTAGONISTIC"
        interpretation = "Reality sources and energy recovery interfere with each other"
    else:
        classification = "ADDITIVE"
        interpretation = "Reality sources and energy recovery combine independently"

    return {
        'off_off': float(off_off),
        'on_off': float(on_off),
        'off_on': float(off_on),
        'on_on': float(on_on),
        'h2_effect': float(h2_effect),
        'h5_effect': float(h5_effect),
        'additive_prediction': float(additive_prediction),
        'synergy': float(synergy),
        'fold_change': float(fold_change),
        'synergy_threshold': synergy_threshold,
        'classification': classification,
        'interpretation': interpretation
    }


def main():
    """Execute C257 H2×H5 factorial mechanism validation."""
    print("=" * 70)
    print("CYCLE 259: MECHANISM VALIDATION - H2 × H5")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Paradigm: Mechanism validation (deterministic, n=1)")
    print()

    # Define four factorial conditions
    conditions = [
        MechanismCondition(h2_enabled=False, h5_enabled=False),  # OFF-OFF (baseline)
        MechanismCondition(h2_enabled=True, h5_enabled=False),   # ON-OFF (H2 only)
        MechanismCondition(h2_enabled=False, h5_enabled=True),   # OFF-ON (H5 only)
        MechanismCondition(h2_enabled=True, h5_enabled=True)     # ON-ON (both)
    ]

    # Run all four conditions
    print("EXPERIMENTAL CONDITIONS:")
    print("-" * 70)
    results = {}
    for i, condition in enumerate(conditions, 1):
        print(f"[{i}/4] Condition: {condition}")
        result = run_condition(condition)
        results[condition.name] = result
        print()

    # Analyze synergy
    print("SYNERGY ANALYSIS:")
    print("-" * 70)
    synergy_analysis = analyze_synergy(results)

    print(f"OFF-OFF (baseline):       {synergy_analysis['off_off']:.4f}")
    print(f"ON-OFF (H2 only):         {synergy_analysis['on_off']:.4f}")
    print(f"OFF-ON (H5 only):         {synergy_analysis['off_on']:.4f}")
    print(f"ON-ON (both mechanisms):  {synergy_analysis['on_on']:.4f}")
    print()
    print(f"H2 effect (sources):      {synergy_analysis['h2_effect']:.4f}")
    print(f"H5 effect (recovery):      {synergy_analysis['h5_effect']:.4f}")
    print(f"Additive prediction:      {synergy_analysis['additive_prediction']:.4f}")
    print()
    print(f"SYNERGY:                  {synergy_analysis['synergy']:.4f}")
    print(f"Fold-change (ON-ON/OFF-OFF): {synergy_analysis['fold_change']:.2f}×")
    print()
    print(f"CLASSIFICATION:           {synergy_analysis['classification']}")
    print(f"INTERPRETATION:           {synergy_analysis['interpretation']}")
    print()

    # Save results
    output = {
        'metadata': {
            'cycle': 259,
            'experiment': 'h2h5_mechanism_validation',
            'h2_mechanism': 'Reality Sources',
            'h5_mechanism': 'Energy Recovery',
            'paradigm': 'mechanism_validation',
            'n_per_condition': 1,  # Deterministic single run
            'cycles_per_experiment': CYCLES,
            'timestamp': datetime.now().isoformat(),
            'author': 'Aldrin Payopay <aldrin.gdf@gmail.com>',
            'repository': 'https://github.com/mrdirno/nested-resonance-memory-archive'
        },
        'conditions': results,
        'synergy_analysis': synergy_analysis
    }

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {RESULTS_FILE}")
    print("=" * 70)
    print(f"End time: {datetime.now().isoformat()}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
