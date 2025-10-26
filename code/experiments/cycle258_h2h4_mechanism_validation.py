#!/usr/bin/env python3
"""
CYCLE 258: MECHANISM VALIDATION - H2 × H4 Factorial Interaction

Purpose: Test whether Reality Sources (H2) and Spawn Throttling (H4) exhibit
         synergistic, antagonistic, or additive effects when combined.

Background:
  - Stochasticity investigation (Cycles 235-254) proved system is deterministic
  - Statistical paradigm fails (σ²=0 across all conditions)
  - Mechanism validation paradigm adopted: Single runs, directional predictions

H2 - Reality Sources:
  Multiple reality sampling sources provide diverse energy inputs, stabilizing
  population dynamics through resource diversification.

H4 - Spawn Throttling:
  Limits agent spawn frequency by enforcing cooldown period between spawns,
  preventing explosive population growth and resource exhaustion.

Hypothesis:
  Sources + Throttling = ADDITIVE or WEAKLY SYNERGISTIC
  Reasoning: Sources provide energy, throttling limits usage. Minimal interaction expected.
  Expected synergy ≈ 0 (independent mechanisms)

Mechanism Validation Method:
  - Single deterministic run per condition (n=1, reproducible)
  - 4 conditions: OFF-OFF, ON-OFF, OFF-ON, ON-ON
  - Synergy detection: ON-ON vs (OFF-OFF + H2_effect + H4_effect)
  - Classification: Synergistic (synergy > 0.1), Antagonistic (< -0.1), Additive

Expected Outcomes:
  - OFF-OFF (neither): mean ≈ 0.07 (baseline collapse)
  - ON-OFF (sources only): mean ≈ 0.12 (modest improvement)
  - OFF-ON (throttling only): mean ≈ 0.05 (limited spawning)
  - ON-ON (both): mean ≈ 0.10 (additive, minimal interaction)

  Synergy = 0.10 - (0.07 + 0.05 + (-0.02)) = 0.00 (ADDITIVE)

Date: 2025-10-26
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 258 (Phase 2: Paper 3 mechanism validation, post-determinism discovery)
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
THROTTLE_COOLDOWN = 100  # H4 parameter: Minimum cycles between spawns
RESULTS_FILE = Path(__file__).parent / "results" / "cycle258_h2h4_mechanism_validation_results.json"


class MechanismCondition:
    """Wrapper for factorial mechanism conditions."""

    def __init__(self, h2_enabled: bool, h4_enabled: bool):
        """
        Initialize factorial condition.

        Args:
            h2_enabled: Reality sources mechanism active
            h4_enabled: Spawn throttling mechanism active
        """
        self.h2_sources = h2_enabled
        self.h4_throttling = h4_enabled
        self.name = f"{'ON' if h2_enabled else 'OFF'}-{'ON' if h4_enabled else 'OFF'}"

    def __str__(self):
        h2 = "H2:ON" if self.h2_sources else "H2:OFF"
        h4 = "H4:ON" if self.h4_throttling else "H4:OFF"
        return f"{self.name} ({h2}, {h4})"


def run_condition(condition: MechanismCondition) -> Dict:
    """
    Run single deterministic experiment with mechanism configuration.

    Args:
        condition: Mechanism condition (H2, H4 settings)

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

    # H4: Throttling tracker (cycle number when agent last spawned)
    last_spawn_cycle = {}  # agent_id -> cycle number

    # Run simulation
    for cycle in range(CYCLES):
        # H2: Reality sources (if enabled)
        if condition.h2_sources:
            # Additional reality sampling for all agents
            for agent in agents:
                extra_metrics = reality.get_system_metrics()
                available_capacity = (100 - extra_metrics['cpu_percent']) + \
                                   (100 - extra_metrics['memory_percent'])
                bonus_energy = 0.005 * available_capacity  # 0.5% boost
                agent.energy = min(agent.energy + bonus_energy, 200.0)

        # Evolve all agents (includes reality-based energy recharge)
        for agent in agents:
            agent.evolve(delta_time=1.0)

        # Spawn new agents if energy threshold met
        for agent in list(agents):  # Copy list to avoid modification during iteration
            if agent.energy >= 10.0 and agent.depth < 7 and len(agents) < MAX_AGENTS:
                # H4: Check throttling cooldown if enabled
                if condition.h4_throttling:
                    last_spawn = last_spawn_cycle.get(agent.agent_id, -THROTTLE_COOLDOWN)
                    cycles_since_spawn = cycle - last_spawn
                    if cycles_since_spawn < THROTTLE_COOLDOWN:
                        continue  # Skip spawn - throttle enforced

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

                # H4: Update last spawn cycle
                last_spawn_cycle[agent.agent_id] = cycle

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
        'h4_throttling': condition.h4_throttling,
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
    h4_effect = off_on - off_off  # Effect of throttling alone

    # Additive prediction (null hypothesis: no interaction)
    additive_prediction = off_off + h2_effect + h4_effect

    # Synergy (interaction effect)
    synergy = on_on - additive_prediction

    # Fold-change (interpretable effect size)
    fold_change = on_on / off_off if off_off > 0 else float('inf')

    # Classification (qualitative, threshold-based)
    synergy_threshold = 0.1

    if synergy > synergy_threshold:
        classification = "SYNERGISTIC"
        interpretation = "Reality sources and spawn throttling amplify each other"
    elif synergy < -synergy_threshold:
        classification = "ANTAGONISTIC"
        interpretation = "Reality sources and spawn throttling interfere with each other"
    else:
        classification = "ADDITIVE"
        interpretation = "Reality sources and spawn throttling combine independently"

    return {
        'off_off': float(off_off),
        'on_off': float(on_off),
        'off_on': float(off_on),
        'on_on': float(on_on),
        'h2_effect': float(h2_effect),
        'h4_effect': float(h4_effect),
        'additive_prediction': float(additive_prediction),
        'synergy': float(synergy),
        'fold_change': float(fold_change),
        'synergy_threshold': synergy_threshold,
        'classification': classification,
        'interpretation': interpretation
    }


def main():
    """Execute C258 H2×H4 factorial mechanism validation."""
    print("=" * 70)
    print("CYCLE 258: MECHANISM VALIDATION - H2 × H4")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Paradigm: Mechanism validation (deterministic, n=1)")
    print()

    # Define four factorial conditions
    conditions = [
        MechanismCondition(h2_enabled=False, h4_enabled=False),  # OFF-OFF (baseline)
        MechanismCondition(h2_enabled=True, h4_enabled=False),   # ON-OFF (H2 only)
        MechanismCondition(h2_enabled=False, h4_enabled=True),   # OFF-ON (H4 only)
        MechanismCondition(h2_enabled=True, h4_enabled=True)     # ON-ON (both)
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
    print(f"OFF-ON (H4 only):         {synergy_analysis['off_on']:.4f}")
    print(f"ON-ON (both mechanisms):  {synergy_analysis['on_on']:.4f}")
    print()
    print(f"H2 effect (sources):      {synergy_analysis['h2_effect']:.4f}")
    print(f"H4 effect (throttling):   {synergy_analysis['h4_effect']:.4f}")
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
            'cycle': 258,
            'experiment': 'h2h4_mechanism_validation',
            'h2_mechanism': 'Reality Sources',
            'h4_mechanism': 'Spawn Throttling',
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
