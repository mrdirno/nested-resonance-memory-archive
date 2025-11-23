#!/usr/bin/env python3
"""
CYCLE 176 MICRO-VALIDATION: Energy-Regulated Spawn Mechanism

Purpose: Minimal test of parent.spawn_child() energy regulation with n=3 seeds, 100 cycles
Strategy: Validate core mechanism works before full n=20, 3000-cycle validation
Expected: ~5-10 agents after 100 cycles if energy regulation works

This is a diagnostic script to debug C176 V6 validation hang issue.

Date: 2025-11-01
Cycle: 897
Researcher: Claude (DUALITY-ZERO-V2)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sys
import numpy as np
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine

# Minimal parameters
FREQUENCY = 2.5
SEEDS = [42, 123, 456]  # n=3 for quick test
CYCLES = 100  # Short run
MAX_AGENTS = 100


def run_micro_validation(seed: int) -> dict:
    """Run minimal validation with diagnostic output."""

    print(f"\n{'='*60}")
    print(f"SEED {seed}: Starting micro-validation")
    print(f"{'='*60}")

    # Initialize
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    np.random.seed(seed)

    print(f"[{seed}] Components initialized")

    # Create root agent
    metrics = reality.get_system_metrics()
    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality
    )
    agents = [root]

    print(f"[{seed}] Root agent created, ID={root.agent_id}")

    # Track metrics
    spawn_attempts = 0
    spawn_successes = 0
    composition_count = 0

    # Calculate spawn interval
    spawn_interval = max(1, int(100.0 / FREQUENCY))
    print(f"[{seed}] Spawn interval: every {spawn_interval} cycles")

    # Composition engine
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    print(f"[{seed}] Starting main loop ({CYCLES} cycles)...")

    # Main loop
    for cycle_idx in range(CYCLES):

        # Spawn decision
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < MAX_AGENTS:
            spawn_attempts += 1

            # Get current metrics
            current_metrics = reality.get_system_metrics()

            # Spawn from random parent
            parent = agents[np.random.randint(len(agents))]
            child_id = f"agent_{cycle_idx}_{spawn_attempts}"
            child = parent.spawn_child(child_id, energy_fraction=0.3)

            if child:
                agents.append(child)
                spawn_successes += 1
                if spawn_successes % 5 == 0:
                    print(f"[{seed}] Cycle {cycle_idx}: {spawn_successes} successful spawns, population={len(agents)}")

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect composition (but don't remove agents)
        cluster_events = composition_engine.detect_clusters(agents)
        if cluster_events:
            composition_count += len(cluster_events)
            if composition_count % 10 == 0:
                print(f"[{seed}] Cycle {cycle_idx}: {composition_count} total compositions detected")

        # Progress indicator every 25 cycles
        if (cycle_idx + 1) % 25 == 0:
            print(f"[{seed}] Progress: {cycle_idx+1}/{CYCLES} cycles, pop={len(agents)}, spawns={spawn_successes}/{spawn_attempts}")

    # Results
    final_population = len(agents)
    spawn_success_rate = (spawn_successes / spawn_attempts * 100) if spawn_attempts > 0 else 0.0

    print(f"\n[{seed}] RESULTS:")
    print(f"  Final population: {final_population} agents")
    print(f"  Spawn attempts: {spawn_attempts}")
    print(f"  Spawn successes: {spawn_successes}")
    print(f"  Success rate: {spawn_success_rate:.1f}%")
    print(f"  Compositions detected: {composition_count}")

    return {
        'seed': seed,
        'final_population': final_population,
        'spawn_attempts': spawn_attempts,
        'spawn_successes': spawn_successes,
        'spawn_success_rate': spawn_success_rate,
        'composition_count': composition_count,
    }


def main():
    """Execute micro-validation."""
    print("=" * 80)
    print("CYCLE 176 MICRO-VALIDATION: Energy-Regulated Spawn Mechanism")
    print("=" * 80)
    print()
    print(f"Purpose: Debug C176 V6 validation hang issue")
    print(f"Parameters: n={len(SEEDS)} seeds, {CYCLES} cycles each")
    print(f"Expected: ~5-10 agents if energy regulation works")
    print()

    start_time = datetime.now()
    results = []

    for seed in SEEDS:
        result = run_micro_validation(seed)
        results.append(result)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Summary
    print("\n" + "=" * 80)
    print("MICRO-VALIDATION COMPLETE")
    print("=" * 80)
    print()

    avg_pop = np.mean([r['final_population'] for r in results])
    avg_success_rate = np.mean([r['spawn_success_rate'] for r in results])

    print("SUMMARY:")
    print(f"  Average final population: {avg_pop:.1f} agents")
    print(f"  Average spawn success rate: {avg_success_rate:.1f}%")
    print(f"  Duration: {duration:.1f} seconds")
    print()

    # Validation check
    if 5 <= avg_pop <= 15 and 20 <= avg_success_rate <= 50:
        print("✅ MICRO-VALIDATION PASSED: Energy regulation mechanism working")
        print()
        print("Next steps:")
        print("  → Investigate C176 V6 full validation hang (likely performance issue)")
        print("  → Consider incremental validation (n=5 seeds, 1000 cycles)")
        print("  → Or proceed directly with C176 V7 ablation study")
    else:
        print("❌ MICRO-VALIDATION UNEXPECTED: Energy mechanism behaving differently")
        print()
        print(f"Expected: 5-15 agents, 20-50% success rate")
        print(f"Actual: {avg_pop:.1f} agents, {avg_success_rate:.1f}% success rate")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
