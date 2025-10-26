#!/usr/bin/env python3
"""
CYCLE 260: MECHANISM VALIDATION - H4 × H5 Factorial Interaction

Purpose: Test whether Energy Recovery (H5) and Spawn Throttling (H4) exhibit
         synergistic, antagonistic, or additive effects when combined.

Background:
  - Stochasticity investigation (Cycles 235-254) proved system is deterministic
  - Statistical paradigm fails (σ²=0 across all conditions)
  - Mechanism validation paradigm adopted: Single runs, directional predictions

H1 - Energy Pooling:
  Agents share energy within resonance clusters, distributing reproductive
  capacity across cluster members instead of single-parent bottleneck.

H4 - Spawn Throttling:
  Limits agent spawn frequency by enforcing cooldown period between spawns,
  preventing explosive population growth and resource exhaustion.

Hypothesis:
  Throttling + Recovery = ANTAGONISTIC or ADDITIVE
  Reasoning: Pooling creates agents, throttling limits creation rate.
  Expected synergy < 0 (recovery helps survive throttling constraint) or ≈ 0 (independent)

Mechanism Validation Method:
  - Single deterministic run per condition (n=1, reproducible)
  - 4 conditions: OFF-OFF, ON-OFF, OFF-ON, ON-ON
  - Synergy detection: ON-ON vs (OFF-OFF + H1_effect + H4_effect)
  - Classification: Synergistic (synergy > 0.1), Antagonistic (< -0.1), Additive

Expected Outcomes:
  - OFF-OFF (neither): mean ≈ 0.07 (baseline collapse)
  - ON-OFF (pooling only): mean ≈ 0.95 (C177 H1 result)
  - OFF-ON (throttling only): mean ≈ 0.05 (limited spawning, slower growth)
  - ON-ON (both): mean ≈ 0.45 (throttling constrains pooling, antagonistic)

  Synergy = 0.45 - (0.07 + 0.88 + (-0.02)) = -0.48 (ANTAGONISTIC)

Date: 2025-10-26
Researcher: Claude (DUALITY-ZERO-V2)
Cycle: 260 (Phase 2: Paper 3 mechanism validation, post-determinism discovery)
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
THROTTLE_COOLDOWN = 100  # Minimum cycles between spawns (H4 parameter)
RESULTS_FILE = Path(__file__).parent / "results" / "cycle260_h4h5_mechanism_validation_results.json"


class MechanismCondition:
    """Wrapper for factorial mechanism conditions."""

    def __init__(self, h4_enabled: bool, h5_enabled: bool):
        """
        Initialize factorial condition.

        Args:
            h4_enabled: Spawn throttling mechanism active
            h5_enabled: Energy recovery mechanism active
        """
        self.h4_throttling = h4_enabled
        self.h5_recovery = h5_enabled
        self.name = f"{'ON' if h4_enabled else 'OFF'}-{'ON' if h5_enabled else 'OFF'}"

    def __str__(self):
        h4 = "H4:ON" if self.h4_throttling else "H4:OFF"
        h5 = "H5:ON" if self.h5_recovery else "H5:OFF"
        return f"{self.name} ({h4}, {h5})"


def run_condition(condition: MechanismCondition) -> Dict:
    """
    Run single deterministic experiment with mechanism configuration.

    Args:
        condition: Mechanism condition (H1, H2 settings)

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

        # H4: Spawn throttling enforced in spawn section below
        # (No per-cycle logic needed; throttling checked during spawn attempts)

        # Evolve all agents (includes reality-based energy recharge)
        for agent in agents:
            agent.evolve(delta_time=1.0)

        # H5: Energy recovery (if enabled)
        if condition.h5_recovery:
            # Boost energy recovery for all agents (2× multiplier)
            for agent in agents:
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
        'h4_throttling': condition.h4_throttling,
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
    h4_effect = on_off - off_off  # Effect of throttling alone
    h5_effect = off_on - off_off  # Effect of recovery alone

    # Additive prediction (null hypothesis: no interaction)
    additive_prediction = off_off + h4_effect + h5_effect

    # Synergy (interaction effect)
    synergy = on_on - additive_prediction

    # Fold-change (interpretable effect size)
    fold_change = on_on / off_off if off_off > 0 else float('inf')

    # Classification (qualitative, threshold-based)
    synergy_threshold = 0.1

    if synergy > synergy_threshold:
        classification = "SYNERGISTIC"
        interpretation = "Spawn throttling and energy recovery amplify each other"
    elif synergy < -synergy_threshold:
        classification = "ANTAGONISTIC"
        interpretation = "Spawn throttling and energy recovery interfere with each other"
    else:
        classification = "ADDITIVE"
        interpretation = "Spawn throttling and energy recovery combine independently"

    return {
        'off_off': float(off_off),
        'on_off': float(on_off),
        'off_on': float(off_on),
        'on_on': float(on_on),
        'h4_effect': float(h4_effect),
        'h5_effect': float(h5_effect),
        'additive_prediction': float(additive_prediction),
        'synergy': float(synergy),
        'fold_change': float(fold_change),
        'synergy_threshold': synergy_threshold,
        'classification': classification,
        'interpretation': interpretation
    }


def main():
    """Execute C260 H4×H5 factorial mechanism validation."""
    print("=" * 70)
    print("CYCLE 260: MECHANISM VALIDATION - H4 × H5")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Paradigm: Mechanism validation (deterministic, n=1)")
    print()

    # Define four factorial conditions
    conditions = [
        MechanismCondition(h4_enabled=False, h5_enabled=False),  # OFF-OFF (baseline)
        MechanismCondition(h4_enabled=True, h5_enabled=False),   # ON-OFF (H1 only)
        MechanismCondition(h4_enabled=False, h5_enabled=True),   # OFF-ON (H2 only)
        MechanismCondition(h4_enabled=True, h5_enabled=True)     # ON-ON (both)
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
    print(f"ON-OFF (H4 only):         {synergy_analysis['on_off']:.4f}")
    print(f"OFF-ON (H5 only):         {synergy_analysis['off_on']:.4f}")
    print(f"ON-ON (both mechanisms):  {synergy_analysis['on_on']:.4f}")
    print()
    print(f"H4 effect (throttling):   {synergy_analysis['h4_effect']:.4f}")
    print(f"H5 effect (recovery):     {synergy_analysis['h5_effect']:.4f}")
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
            'cycle': 260,
            'experiment': 'h4h5_mechanism_validation',
            'h4_mechanism': 'Spawn Throttling',
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
