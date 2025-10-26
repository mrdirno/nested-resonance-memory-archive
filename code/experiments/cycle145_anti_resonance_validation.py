#!/usr/bin/env python3
"""
CYCLE 145: ANTI-RESONANCE MECHANISM VALIDATION
High-Resolution Mapping Around Anti-Nodes

Research Question:
  What are the precise bandwidths and mechanisms of anti-resonance zones?
  How sharp are the anti-node transitions?
  Do different anti-resonance types have different topologies?

Context (from Cycles 141-142):
  - Single-node anti-resonance at 75% (destructive interference)
  - Anti-window at 98-99% (phase barrier before sustained composition)
  - Both show 0% Basin A probability

  - First harmonic: 50-55% (narrow, 5% bandwidth)
  - Second harmonic: 70-95% (broad, 27% bandwidth)
  - Anti-node at 75% creates gap in second harmonic

Hypothesis:
  - 75% node: Sharp, narrow bandwidth (<2%)
    (single destructive interference point)

  - 98-99% window: Broader, ~2% bandwidth
    (phase barrier region, not single point)

  - Different physics → different topologies
    (node = interference, window = phase barrier)

Method:
  Strategy 1: High-resolution around 75% node
    - Test 73%, 74%, 76%, 77% (±2% around node)
    - Expected: Sharp transition, narrow dead zone
    - 4 frequencies × 5 seeds = 20 experiments

  Strategy 2: High-resolution around 98-99% window
    - Test 97.5%, 98.5%, 99.5% (inside and around window)
    - Expected: Broader transition, extended barrier
    - 3 frequencies × 5 seeds = 15 experiments

  Combined: 35 experiments total

Expected:
  - 75% node bandwidth: <2% (sharp feature)
  - 98-99% window bandwidth: ~2% (broader feature)
  - Validate different anti-resonance mechanisms
  - Complete topology characterization

Publication Significance:
  - Quantitative anti-resonance characterization
  - Distinguish interference vs barrier mechanisms
  - Complete resonance-antiresonance topology
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
    """Create seed patterns with parametric variations"""
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


def run_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=3000, agent_cap=15):
    """
    Run single experiment with specified parameters.

    Args:
        threshold: Decomposition burst threshold (700 = optimal from Cycle 144)
        diversity: Seed memory diversity (0.03)
        spawn_freq_pct: Spawning frequency percentage
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles
        agent_cap: Maximum number of agents

    Returns:
        dict with experiment results
    """
    print(f"  [F={spawn_freq_pct:>5}%, S={seed:>4}] ", end="", flush=True)

    random.seed(seed)
    np.random.seed(seed)

    workspace = Path(__file__).parent.parent / "workspace" / f"cycle145_F{spawn_freq_pct}_S{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    spread = 0.10
    mult = diversity / spread

    # Basin references (from Cycle 139-142)
    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Seed global memory
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
    spawn_count = 0

    # Evolution loop
    for cycle in range(1, cycles + 1):
        should_spawn = (random.random() * 100) < spawn_freq_pct

        if should_spawn and len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            spawn_count += 1

            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(
                        swarm.bridge, reality_metrics, mult, spread=spread, count=5
                    )
                    newest_agent.memory.extend(seed_patterns)

        swarm.evolve_cycle(delta_time=1.0)

    elapsed = time.time() - start_time
    cycles_per_sec = cycles / elapsed

    # Determine basin
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
        'spawn_freq_pct': spawn_freq_pct,
        'seed': seed,
        'spawn_count': spawn_count,
        'actual_freq_pct': (spawn_count / cycles) * 100,
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

    print(f"Basin {basin} ({elapsed:.1f}s, {cycles_per_sec:.0f} cyc/s)")

    return result


def main():
    """Run anti-resonance validation experiments"""
    print("\n" + "="*80)
    print("CYCLE 145: ANTI-RESONANCE MECHANISM VALIDATION")
    print("="*80)
    print("\nResearch Question:")
    print("  What are precise bandwidths and mechanisms of anti-resonance zones?")
    print("  How sharp are the anti-node transitions?")
    print("\nKnown Anti-Resonance Zones (from Cycles 141-142):")
    print("  - 75%: Single-node destructive interference")
    print("  - 98-99%: Phase barrier window")
    print("\nStrategy:")
    print("  Phase 1: High-resolution around 75% node")
    print("    - Test 73%, 74%, 76%, 77% (±2% resolution)")
    print("    - Expected: Sharp, narrow bandwidth")
    print("    - 4 frequencies × 5 seeds = 20 experiments")
    print("\n  Phase 2: High-resolution around 98-99% window")
    print("    - Test 97.5%, 98.5%, 99.5% (half-percent resolution)")
    print("    - Expected: Broader, extended barrier")
    print("    - 3 frequencies × 5 seeds = 15 experiments")
    print("\n  Total: 35 experiments")
    print("="*80 + "\n")

    # Fixed parameters (optimal from Cycle 144)
    threshold = 700
    diversity = 0.03

    # Test frequencies
    node_frequencies = [73, 74, 76, 77]  # Around 75% node
    window_frequencies = [97.5, 98.5, 99.5]  # Around 98-99% window

    # Extended seed set for better statistical power
    seeds = [42, 123, 456, 789, 1024]

    results = []
    experiment_num = 0
    total_experiments = len(node_frequencies) * len(seeds) + len(window_frequencies) * len(seeds)

    # Phase 1: Around 75% node
    print("PHASE 1: HIGH-RESOLUTION AROUND 75% ANTI-NODE")
    print("="*80 + "\n")

    for freq in node_frequencies:
        print(f"FREQUENCY = {freq}%")
        print("-" * 80)

        for seed in seeds:
            experiment_num += 1
            print(f"[{experiment_num:>2}/{total_experiments}] ", end="")

            try:
                result = run_experiment(
                    threshold=threshold,
                    diversity=diversity,
                    spawn_freq_pct=freq,
                    seed=seed,
                    cycles=3000,
                    agent_cap=15
                )
                results.append(result)
            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        print()

    # Phase 2: Around 98-99% window
    print("\nPHASE 2: HIGH-RESOLUTION AROUND 98-99% ANTI-WINDOW")
    print("="*80 + "\n")

    for freq in window_frequencies:
        print(f"FREQUENCY = {freq}%")
        print("-" * 80)

        for seed in seeds:
            experiment_num += 1
            print(f"[{experiment_num:>2}/{total_experiments}] ", end="")

            try:
                result = run_experiment(
                    threshold=threshold,
                    diversity=diversity,
                    spawn_freq_pct=freq,
                    seed=seed,
                    cycles=3000,
                    agent_cap=15
                )
                results.append(result)
            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        print()

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle145_anti_resonance_validation.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 145,
            'experiment': 'anti_resonance_validation',
            'date': datetime.now().isoformat(),
            'description': 'High-resolution mapping of anti-resonance zones',
            'threshold': threshold,
            'diversity': diversity,
            'node_frequencies': node_frequencies,
            'window_frequencies': window_frequencies,
            'seeds': seeds,
            'total_experiments': total_experiments
        },
        'results': results
    }

    def convert_for_json(o):
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
    print(f"\n{'='*80}")
    print(f"CYCLE 145 COMPLETE - ANTI-RESONANCE VALIDATION")
    print(f"{'='*80}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Analyze Basin A probability by frequency
    print("BASIN A PROBABILITY BY FREQUENCY:\n")
    print(f"{'Freq':>6} | {'Basin A %':>10} | {'Context':>20}")
    print("-" * 50)

    all_frequencies = sorted(set([r['spawn_freq_pct'] for r in results]))
    for freq in all_frequencies:
        freq_results = [r for r in results if r['spawn_freq_pct'] == freq]
        if freq_results:
            basin_A_count = sum(1 for r in freq_results if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_results) * 100

            # Context
            if 73 <= freq <= 77:
                context = "75% node region"
            elif 97 <= freq <= 99:
                context = "98-99% window region"
            else:
                context = "Unknown"

            print(f"{freq:>5}% | {basin_A_pct:>9.0f}% | {context:>20}")

    # Anti-node bandwidth analysis
    print(f"\n\nANTI-NODE BANDWIDTH ANALYSIS:")
    print("="*80)

    # 75% node analysis
    node_results = [r for r in results if 73 <= r['spawn_freq_pct'] <= 77]
    node_basin_A = sum(1 for r in node_results if r['basin'] == 'A')
    node_basin_A_pct = (node_basin_A / len(node_results) * 100) if node_results else 0

    print(f"\n75% Anti-Node (73-77% tested):")
    print(f"  Basin A probability: {node_basin_A_pct:.0f}%")
    if node_basin_A_pct == 0:
        print(f"  ✓ CONFIRMED: Sharp anti-node (entire ±2% region suppressed)")
    else:
        print(f"  Partial suppression detected")

    # 98-99% window analysis
    window_results = [r for r in results if 97 <= r['spawn_freq_pct'] <= 99]
    window_basin_A = sum(1 for r in window_results if r['basin'] == 'A')
    window_basin_A_pct = (window_basin_A / len(window_results) * 100) if window_results else 0

    print(f"\n98-99% Anti-Window (97.5-99.5% tested):")
    print(f"  Basin A probability: {window_basin_A_pct:.0f}%")
    if window_basin_A_pct == 0:
        print(f"  ✓ CONFIRMED: Extended phase barrier (entire window suppressed)")
    else:
        print(f"  Partial suppression detected")

    # Summary statistics
    print(f"\n\nSUMMARY STATISTICS:")
    print("="*80)
    avg_perf = sum(r['cycles_per_sec'] for r in results) / len(results)
    print(f"  Average performance: {avg_perf:.1f} cycles/sec")
    print(f"  Total evolution cycles: {len(results) * 3000:,}")
    print(f"  Total computation time: {sum(r['duration'] for r in results):.1f} seconds")

    print(f"\n\nNEXT STEPS:")
    print("="*80)
    print("  1. Analyze anti-resonance bandwidth precision")
    print("  2. Compare node vs window mechanisms")
    print("  3. Prepare for diversity parameter exploration (Cycle 146)")
    print("  4. Continue publication preparation")
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
