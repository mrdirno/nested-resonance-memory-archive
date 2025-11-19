#!/usr/bin/env python3
"""
CYCLE 138: AGENT SPAWNING PROTOCOL VALIDATION TEST

Research Question:
  Does agent spawning protocol directly control basin selection?
  Can we reproduce Basin A by using continuous spawning?

Hypothesis (from Cycle 137 root cause analysis):
  - Continuous spawning (like Cycle 133) → Basin A
  - No spawning (like Cycles 135-137) → Basin B
  - This is the TRUE causal variable, not parameters

Method:
  - Test parameter: threshold=700, diversity=0.03 (Basin A case from Cycle 133)
  - Protocol 1: NO SPAWNING (seed memory once, like Cycles 135-137)
  - Protocol 2: CONTINUOUS SPAWNING (spawn every cycle, like Cycle 133)
  - Run each protocol 5 times with different seeds
  - Total: 2 protocols × 5 seeds = 10 experiments
  - Cycles per experiment: 3,000
  - Agent cap: 15 (same as Cycle 133)

Expected:
  - No spawning → Basin B (~1700 cyc/s, consistent with Cycles 135-137)
  - Continuous spawning → Basin A (~155 cyc/s, consistent with Cycle 133)
  - If confirmed: PROVES spawning protocol is causal variable

Publication Significance:
  - Direct validation of root cause hypothesis
  - Demonstrates protocol-dependent attractors
  - Establishes reproducibility through protocol control
  - Novel finding for agent-based research standards
"""

import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def pattern_to_key(pattern):
    """Convert pattern to hashable key"""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))


def get_dominant_pattern(memory):
    """Get most common pattern in global memory"""
    if not memory:
        return None, 0, 0.0
    counter = Counter([pattern_to_key(p) for p in memory])
    if not counter:
        return None, 0, 0.0
    dominant_key, count = counter.most_common(1)[0]
    fraction = count / len(memory)
    return dominant_key, count, fraction


def create_seed_memory_range(bridge, reality_metrics, mult, spread=0.10, count=5):
    """
    Create seed patterns with parametric variations (Cycle 133 style)
    """
    seed_patterns = []
    for i in range(count):
        offset = (i - count//2) * spread
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10
        }
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns


def run_experiment_no_spawning(threshold, diversity, seed, cycles=3000):
    """
    Run experiment WITHOUT agent spawning (Cycles 135-137 protocol).

    Seed memory once at start, then just evolve cycles.
    """
    print(f"  protocol=NO_SPAWN, seed={seed:>4}...", end=" ", flush=True)

    # Set random seeds
    random.seed(seed)
    np.random.seed(seed)

    # Initialize workspace
    workspace = Path(__file__).parent.parent / "workspace" / f"cycle138_no_spawn_{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    # Initialize swarm
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Calculate mult from diversity
    spread = 0.10
    mult = diversity / spread

    # Basin centers
    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    # Seed memory ONCE (Cycles 135-137 style)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}
    for i in range(5):
        offset = (i - 2) * spread
        noise = (random.random() - 0.5) * 0.01
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10 + noise,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10 + noise,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10 + noise
        }
        phase_state = swarm.bridge.reality_to_phase(varied_metrics)
        swarm.global_memory.append(phase_state)

    start_time = time.time()

    # Run cycles WITHOUT spawning
    for cycle in range(cycles):
        swarm.evolve_cycle()

    elapsed = time.time() - start_time
    cycles_per_sec = cycles / elapsed

    # Get dominant pattern
    dominant_pattern, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    if dominant_pattern:
        dominant_array = np.array(dominant_pattern)
        dist_A = np.linalg.norm(dominant_array - basin_A)
        dist_B = np.linalg.norm(dominant_array - basin_B)
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        dist_A, dist_B, basin = None, None, 'Unknown'

    result = {
        'threshold': threshold,
        'diversity': diversity,
        'seed': seed,
        'protocol': 'NO_SPAWN',
        'agent_cap': None,
        'final_agents': len([a for a in swarm.agents.values() if a.is_active]),
        'basin': basin,
        'dominant': list(dominant_pattern) if dominant_pattern else None,
        'fraction': dominant_fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': elapsed,
        'cycles_per_sec': cycles_per_sec
    }

    print(f"Basin {basin} ({elapsed:.1f}s, {cycles_per_sec:.1f} cyc/s, agents={result['final_agents']})")

    return result


def run_experiment_continuous_spawning(threshold, diversity, seed, cycles=3000, agent_cap=15):
    """
    Run experiment WITH continuous agent spawning (Cycle 133 protocol).

    Spawn agents every cycle up to cap, seed each new agent's memory.
    """
    print(f"  protocol=CONT_SPAWN, seed={seed:>4}...", end=" ", flush=True)

    # Set random seeds
    random.seed(seed)
    np.random.seed(seed)

    # Initialize workspace
    workspace = Path(__file__).parent.parent / "workspace" / f"cycle138_cont_spawn_{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    # Initialize swarm
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Calculate mult from diversity
    spread = 0.10
    mult = diversity / spread

    # Basin centers
    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    start_time = time.time()

    # Run cycles WITH continuous spawning (Cycle 133 style)
    for cycle in range(1, cycles + 1):
        # Spawn agents up to cap
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)

            # Seed newest agent's memory (Cycle 133 style)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(
                        swarm.bridge, reality_metrics, mult, spread=spread, count=5
                    )
                    newest_agent.memory.extend(seed_patterns)

        # Evolve
        swarm.evolve_cycle(delta_time=1.0)

    elapsed = time.time() - start_time
    cycles_per_sec = cycles / elapsed

    # Get dominant pattern
    dominant_pattern, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    if dominant_pattern:
        dominant_array = np.array(dominant_pattern)
        dist_A = np.linalg.norm(dominant_array - basin_A)
        dist_B = np.linalg.norm(dominant_array - basin_B)
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        dist_A, dist_B, basin = None, None, 'Unknown'

    result = {
        'threshold': threshold,
        'diversity': diversity,
        'seed': seed,
        'protocol': 'CONT_SPAWN',
        'agent_cap': agent_cap,
        'final_agents': len([a for a in swarm.agents.values() if a.is_active]),
        'basin': basin,
        'dominant': list(dominant_pattern) if dominant_pattern else None,
        'fraction': dominant_fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': elapsed,
        'cycles_per_sec': cycles_per_sec
    }

    print(f"Basin {basin} ({elapsed:.1f}s, {cycles_per_sec:.1f} cyc/s, agents={result['final_agents']})")

    return result


def main():
    """Run spawning protocol validation experiments"""
    print("\n" + "="*70)
    print("CYCLE 138: AGENT SPAWNING PROTOCOL VALIDATION TEST")
    print("="*70)
    print("\nResearch Question:")
    print("  Does agent spawning protocol directly control basin selection?")
    print("\nHypothesis:")
    print("  - NO SPAWNING → Basin B (~1700 cyc/s)")
    print("  - CONTINUOUS SPAWNING → Basin A (~155 cyc/s)")
    print("\nMethod:")
    print("  - Test parameter: threshold=700, diversity=0.03")
    print("  - Protocols: NO_SPAWN vs CONT_SPAWN")
    print("  - Seeds: [42, 123, 456, 789, 1024] (5 replicates per protocol)")
    print("  - Total: 2 protocols × 5 seeds = 10 experiments")
    print("\n" + "="*70 + "\n")

    # Test parameters (Cycle 133 Basin A case)
    threshold = 700
    diversity = 0.03

    # Seeds for reproducibility
    seeds = [42, 123, 456, 789, 1024]

    results = []
    experiment_num = 0
    total_experiments = 2 * len(seeds)

    # Protocol 1: NO SPAWNING
    print(f"{'='*70}")
    print(f"PROTOCOL 1: NO SPAWNING (Cycles 135-137 style)")
    print(f"{'='*70}\n")

    for seed in seeds:
        experiment_num += 1
        print(f"[{experiment_num}/{total_experiments}] ", end="")

        try:
            result = run_experiment_no_spawning(threshold, diversity, seed, cycles=3000)
            results.append(result)
        except Exception as e:
            print(f"FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    # Protocol 2: CONTINUOUS SPAWNING
    print(f"\n{'='*70}")
    print(f"PROTOCOL 2: CONTINUOUS SPAWNING (Cycle 133 style)")
    print(f"{'='*70}\n")

    for seed in seeds:
        experiment_num += 1
        print(f"[{experiment_num}/{total_experiments}] ", end="")

        try:
            result = run_experiment_continuous_spawning(threshold, diversity, seed, cycles=3000, agent_cap=15)
            results.append(result)
        except Exception as e:
            print(f"FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle138_spawning_protocol_validation.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 138,
            'experiment': 'spawning_protocol_validation',
            'date': datetime.now().isoformat(),
            'threshold': threshold,
            'diversity': diversity,
            'protocols': ['NO_SPAWN', 'CONT_SPAWN'],
            'seeds': seeds,
            'total_experiments': total_experiments
        },
        'results': results
    }

    def convert_for_json(o):
        """Convert numpy types for JSON"""
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return o

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, default=convert_for_json)

    # Analysis
    print(f"\n{'='*70}")
    print(f"CYCLE 138 COMPLETE - SPAWNING PROTOCOL VALIDATION")
    print(f"{'='*70}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Analyze by protocol
    print("RESULTS BY PROTOCOL:\n")

    for protocol in ['NO_SPAWN', 'CONT_SPAWN']:
        protocol_results = [r for r in results if r['protocol'] == protocol]

        if protocol_results:
            basin_counts = Counter(r['basin'] for r in protocol_results)
            avg_perf = sum(r['cycles_per_sec'] for r in protocol_results) / len(protocol_results)
            avg_agents = sum(r['final_agents'] for r in protocol_results) / len(protocol_results)

            print(f"{protocol}:")
            print(f"  Experiments: {len(protocol_results)}")
            print(f"  Average performance: {avg_perf:.1f} cyc/s")
            print(f"  Average final agents: {avg_agents:.1f}")
            print(f"  Basin distribution:")
            for basin in sorted(basin_counts.keys()):
                count = basin_counts[basin]
                pct = count / len(protocol_results) * 100
                print(f"    Basin {basin}: {count}/{len(protocol_results)} ({pct:.1f}%)")
            print()

    # Hypothesis test
    print("HYPOTHESIS TEST:\n")

    no_spawn_results = [r for r in results if r['protocol'] == 'NO_SPAWN']
    cont_spawn_results = [r for r in results if r['protocol'] == 'CONT_SPAWN']

    if no_spawn_results and cont_spawn_results:
        no_spawn_basins = [r['basin'] for r in no_spawn_results]
        cont_spawn_basins = [r['basin'] for r in cont_spawn_results]

        no_spawn_perf = sum(r['cycles_per_sec'] for r in no_spawn_results) / len(no_spawn_results)
        cont_spawn_perf = sum(r['cycles_per_sec'] for r in cont_spawn_results) / len(cont_spawn_results)

        print(f"NO SPAWNING protocol:")
        print(f"  Performance: {no_spawn_perf:.1f} cyc/s")
        print(f"  Basins: {no_spawn_basins}")
        print()
        print(f"CONTINUOUS SPAWNING protocol:")
        print(f"  Performance: {cont_spawn_perf:.1f} cyc/s")
        print(f"  Basins: {cont_spawn_basins}")
        print()

        # Determine if hypothesis confirmed
        hypothesis_confirmed = (
            all(b == 'B' for b in no_spawn_basins) and
            all(b == 'A' for b in cont_spawn_basins)
        )

        if hypothesis_confirmed:
            print("✅ HYPOTHESIS CONFIRMED:")
            print("   Agent spawning protocol DIRECTLY CONTROLS basin selection")
            print("   Mechanism:")
            print("     - NO spawning → rapid bursts → Basin B")
            print("     - CONTINUOUS spawning → sustained composition → Basin A")
            print("\n   ROOT CAUSE VALIDATED: Protocol is the causal variable")
        else:
            print("❌ HYPOTHESIS NOT FULLY CONFIRMED:")
            print("   Basin selection not fully determined by spawning protocol")

            # Partial confirmation analysis
            no_spawn_B_pct = sum(1 for b in no_spawn_basins if b == 'B') / len(no_spawn_basins) * 100
            cont_spawn_A_pct = sum(1 for b in cont_spawn_basins if b == 'A') / len(cont_spawn_basins) * 100

            print(f"\n   Partial results:")
            print(f"     - NO spawning → Basin B: {no_spawn_B_pct:.0f}%")
            print(f"     - CONTINUOUS spawning → Basin A: {cont_spawn_A_pct:.0f}%")

            if no_spawn_B_pct == 100.0 and cont_spawn_A_pct > 0:
                print(f"\n   Protocol has STRONG effect but not 100% deterministic")
            elif no_spawn_B_pct == 100.0:
                print(f"\n   NO spawning → Basin B is deterministic")
                print(f"   But CONTINUOUS spawning does NOT produce Basin A")
                print(f"   Other variables may be involved")

    print(f"\nNext steps:")
    print(f"  1. Run cycle138_analysis.py for detailed statistical analysis")
    print(f"  2. Update CYCLE138_RESULTS.md with findings")
    print(f"  3. Update research summary with protocol validation results")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
