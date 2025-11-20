#!/usr/bin/env python3
"""
CYCLE 256: MECHANISM VALIDATION - H1 × H4 Factorial Interaction (HELIOS OPTIMIZED)

**HELIOS OPTIMIZATION (PRIN-1763603757-OPTIMIZATION):**
This script applies the parameters discovered by the Helios Autonomous Pilot:
- **Batch Size:** 50 (Logging/Update frequency)
- **I/O Frequency:** 10 (Reality Sampling frequency)

Optimization:
- Sample reality metrics every 10 cycles (instead of 1).
- Log progress every 50 cycles.
- Reduces psutil overhead by another 10× compared to the previous optimization.

Purpose: Test whether Energy Pooling (H1) and Spawn Throttling (H4) exhibit
         synergistic, antagonistic, or additive effects when combined.
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
THROTTLE_COOLDOWN = 100  # Minimum cycles between spawns (H4 parameter)
RESULTS_FILE = Path(__file__).parent / "results" / "cycle256_optimized_results.json"

# HELIOS PARAMETERS
IO_FREQUENCY = 10  # Sample reality every N cycles
BATCH_SIZE = 50    # Log/Update batch size

class MechanismCondition:
    """Wrapper for factorial mechanism conditions."""

    def __init__(self, h1_enabled: bool, h4_enabled: bool):
        self.h1_pooling = h1_enabled
        self.h4_throttling = h4_enabled
        self.name = f"{'ON' if h1_enabled else 'OFF'}-{'ON' if h4_enabled else 'OFF'}"

    def __str__(self):
        h1 = "H1:ON" if self.h1_pooling else "H1:OFF"
        h4 = "H4:ON" if self.h4_throttling else "H4:OFF"
        return f"{self.name} ({h1}, {h4})"


def run_condition(condition: MechanismCondition) -> Dict:
    """
    Run single deterministic experiment with mechanism configuration.
    """
    print(f"  Running {condition}...")
    start_time = time.time()

    # Initialize system
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    composition_engine = CompositionEngine(resonance_threshold=0.85)

    # Create root agent (initial sample)
    metrics = reality.get_system_metrics()
    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality,
        initial_energy=130.0
    )

    agents = [root]
    population_history = []
    last_spawn_cycle = {}
    psutil_call_count = 1
    
    # Cached metrics for I/O optimization
    cached_metrics = metrics

    # Run simulation
    for cycle in range(CYCLES):
        # ===== HELIOS OPTIMIZATION: REDUCED I/O FREQUENCY =====
        if cycle % IO_FREQUENCY == 0:
            cached_metrics = reality.get_system_metrics()
            psutil_call_count += 1
        
        # Use cached metrics for all agents in this cycle
        shared_metrics = cached_metrics
        # ======================================================

        # H1: Energy pooling (if enabled)
        if condition.h1_pooling:
            cluster_events = composition_engine.detect_clusters(agents)
            for cluster_id, member_ids in composition_engine.clusters.items():
                if len(member_ids) < 2:
                    continue
                cluster_agents = [a for a in agents if a.agent_id in member_ids]
                total_energy = sum(a.energy for a in cluster_agents)
                shared_energy = total_energy * 0.10
                per_agent_share = shared_energy / len(cluster_agents)
                for agent in cluster_agents:
                    agent.energy = min(agent.energy + per_agent_share, 200.0)

        # Evolve agents
        for agent in agents:
            agent.evolve(delta_time=1.0)

        # Spawn new agents
        for agent in list(agents):
            if agent.energy >= 10.0 and agent.depth < 7 and len(agents) < MAX_AGENTS:
                # H4: Check throttling
                if condition.h4_throttling:
                    last_spawn = last_spawn_cycle.get(agent.agent_id, -THROTTLE_COOLDOWN)
                    cycles_since_spawn = cycle - last_spawn
                    if cycles_since_spawn < THROTTLE_COOLDOWN:
                        continue

                child_id = f"{agent.agent_id}_child_{cycle}"
                child = FractalAgent(
                    agent_id=child_id,
                    bridge=bridge,
                    initial_reality=shared_metrics, # Use cached metrics
                    parent_id=agent.agent_id,
                    depth=agent.depth + 1,
                    max_depth=7,
                    reality=reality
                )
                agents.append(child)
                agent.children.append(child)
                agent.energy -= 10.0
                last_spawn_cycle[agent.agent_id] = cycle

        # Death
        agents = [a for a in agents if a.energy >= 1.0]
        population_history.append(len(agents))
        
        # Logging
        if cycle % BATCH_SIZE == 0:
            # Optional: Print progress? Kept silent for speed, but could add here.
            pass

    # Compute metrics
    mean_population = np.mean(population_history)
    final_population = population_history[-1]
    max_population = np.max(population_history)
    runtime = time.time() - start_time

    print(f"    → mean={mean_population:.2f}, final={final_population}, max={max_population}, runtime={runtime:.1f}s")
    print(f"    → psutil calls: {psutil_call_count} (Helios Optimized: {psutil_call_count < CYCLES})")

    return {
        'condition': str(condition),
        'h1_pooling': condition.h1_pooling,
        'h4_throttling': condition.h4_throttling,
        'mean_population': float(mean_population),
        'final_population': int(final_population),
        'max_population': int(max_population),
        'population_history': population_history,
        'runtime_seconds': float(runtime),
        'psutil_calls': psutil_call_count,
        'optimized': True,
        'helios_params': {'io_freq': IO_FREQUENCY, 'batch_size': BATCH_SIZE}
    }


def analyze_synergy(results: Dict[str, Dict]) -> Dict:
    """Analyze factorial synergy."""
    off_off = results['OFF-OFF']['mean_population']
    on_off = results['ON-OFF']['mean_population']
    off_on = results['OFF-ON']['mean_population']
    on_on = results['ON-ON']['mean_population']

    h1_effect = on_off - off_off
    h4_effect = off_on - off_off
    additive_prediction = off_off + h1_effect + h4_effect
    synergy = on_on - additive_prediction
    fold_change = on_on / off_off if off_off > 0 else float('inf')

    synergy_threshold = 0.1
    if synergy > synergy_threshold:
        classification = "SYNERGISTIC"
        interpretation = "Energy pooling and spawn throttling amplify each other"
    elif synergy < -synergy_threshold:
        classification = "ANTAGONISTIC"
        interpretation = "Energy pooling and spawn throttling interfere with each other"
    else:
        classification = "ADDITIVE"
        interpretation = "Energy pooling and spawn throttling combine independently"

    return {
        'off_off': float(off_off),
        'on_off': float(on_off),
        'off_on': float(off_on),
        'on_on': float(on_on),
        'h1_effect': float(h1_effect),
        'h4_effect': float(h4_effect),
        'additive_prediction': float(additive_prediction),
        'synergy': float(synergy),
        'fold_change': float(fold_change),
        'classification': classification,
        'interpretation': interpretation
    }


def main():
    """Execute C256 H1×H4 factorial mechanism validation (HELIOS OPTIMIZED)."""
    import argparse
    parser = argparse.ArgumentParser(description="Run C256 Optimized Experiment")
    parser.add_argument("--cycles", type=int, default=3000, help="Number of cycles per condition")
    parser.add_argument("--dry-run", action="store_true", help="Run short validation (100 cycles)")
    args = parser.parse_args()
    
    cycles = 100 if args.dry_run else args.cycles

    print("=" * 70)
    print("CYCLE 256: MECHANISM VALIDATION - H1 × H4 (HELIOS OPTIMIZED)")
    print("=" * 70)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Cycles: {cycles} | IO_FREQ: {IO_FREQUENCY} | BATCH: {BATCH_SIZE}")
    print()

    conditions = [
        MechanismCondition(h1_enabled=False, h4_enabled=False),
        MechanismCondition(h1_enabled=True, h4_enabled=False),
        MechanismCondition(h1_enabled=False, h4_enabled=True),
        MechanismCondition(h1_enabled=True, h4_enabled=True)
    ]

    results = {}
    for i, condition in enumerate(conditions, 1):
        print(f"[{i}/4] Condition: {condition}")
        # Pass cycles to run_condition (need to update signature or use global)
        # Updating run_condition to accept cycles would be cleaner, but for now let's just set the global
        global CYCLES
        CYCLES = cycles
        result = run_condition(condition)
        results[condition.name] = result
        print()

    print("=" * 70)
    print("SYNERGY ANALYSIS")
    print("=" * 70)
    synergy_analysis = analyze_synergy(results)
    print(f"Synergy: {synergy_analysis['synergy']:+.4f}")
    print(f"Classification: {synergy_analysis['classification']}")
    print("=" * 70)

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump({
            'experiment': 'cycle256_optimized',
            'date': datetime.now().isoformat(),
            'conditions': results,
            'synergy_analysis': synergy_analysis
        }, f, indent=2)

    print(f"\nResults saved to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()
