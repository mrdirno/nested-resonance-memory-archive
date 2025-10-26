#!/usr/bin/env python3
"""
CYCLE 139: PROTOCOL SPACE MAPPING - SPAWNING FREQUENCY GRADIENT

Research Question:
  What is the relationship between spawning frequency and basin selection?
  Is there a critical spawning rate threshold for Basin A?

Context (from Cycle 138):
  - NO_SPAWN (0% of cycles) → Basin B (5/5, 100%)
  - CONT_SPAWN (100% of cycles) → Basin A (5/5, 100%)
  - Perfect separation - but what about intermediate rates?

Hypothesis:
  - Basin transition is not binary but may show gradient
  - There exists a critical spawning frequency threshold
  - Below threshold → Basin B, above threshold → Basin A
  - Transition may be sharp (phase transition) or gradual

Method:
  - Test spawning frequencies: 0%, 10%, 25%, 50%, 75%, 100% of cycles
  - Fixed parameters: threshold=700, diversity=0.03 (Basin A case)
  - 3 seeds per frequency = 6 frequencies × 3 seeds = 18 experiments
  - Cycles per experiment: 3,000
  - Agent cap: 15 (consistent with Cycle 133/138)

Expected:
  - Low frequency (0-25%) → Basin B (rapid bursts dominate)
  - High frequency (75-100%) → Basin A (sustained composition)
  - Middle frequencies (25-75%) → transition region (to be determined)

Publication Significance:
  - Quantifies protocol-basin relationship
  - Identifies critical threshold for Basin A
  - Maps protocol space topology
  - Extends theoretical framework (population dynamics → attractor selection)
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
    """Create seed patterns with parametric variations (Cycle 133 style)"""
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


def run_experiment_with_frequency(threshold, diversity, seed, spawn_freq_pct, cycles=3000, agent_cap=15):
    """
    Run experiment with specific spawning frequency.

    Args:
        threshold: Burst energy threshold
        diversity: Target diversity
        seed: Random seed
        spawn_freq_pct: Spawning frequency as percentage (0-100)
        cycles: Number of evolution cycles
        agent_cap: Maximum agents

    Returns:
        dict: Results including basin assignment
    """
    print(f"  freq={spawn_freq_pct:>3}%, seed={seed:>4}...", end=" ", flush=True)

    # Set random seeds
    random.seed(seed)
    np.random.seed(seed)

    # Initialize workspace
    workspace = Path(__file__).parent.parent / "workspace" / f"cycle139_freq{spawn_freq_pct}_seed{seed}"
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

    # Seed global memory once (always do this for baseline)
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

    # Run cycles with conditional spawning based on frequency
    for cycle in range(1, cycles + 1):
        # Spawn agents based on frequency
        # spawn_freq_pct = 0 means never spawn
        # spawn_freq_pct = 100 means spawn every cycle
        # spawn_freq_pct = 50 means spawn 50% of cycles (randomly selected)

        should_spawn = False
        if spawn_freq_pct == 0:
            should_spawn = False
        elif spawn_freq_pct == 100:
            should_spawn = True
        else:
            # Probabilistic spawning: random() < (spawn_freq_pct / 100)
            should_spawn = (random.random() * 100) < spawn_freq_pct

        if should_spawn and len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            spawn_count += 1

            # Seed newest agent's memory
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
        'spawn_freq_pct': spawn_freq_pct,
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

    print(f"Basin {basin} ({elapsed:.1f}s, {cycles_per_sec:.1f} cyc/s, spawned={spawn_count}, agents={result['final_agents']})")

    return result


def main():
    """Run protocol space mapping experiments"""
    print("\n" + "="*70)
    print("CYCLE 139: PROTOCOL SPACE MAPPING - SPAWNING FREQUENCY GRADIENT")
    print("="*70)
    print("\nResearch Question:")
    print("  What is the relationship between spawning frequency and basin?")
    print("\nHypothesis:")
    print("  - Critical frequency threshold exists")
    print("  - Below threshold → Basin B")
    print("  - Above threshold → Basin A")
    print("\nMethod:")
    print("  - Test parameter: threshold=700, diversity=0.03")
    print("  - Spawning frequencies: 0%, 10%, 25%, 50%, 75%, 100%")
    print("  - Seeds: [42, 123, 456] (3 replicates per frequency)")
    print("  - Total: 6 frequencies × 3 seeds = 18 experiments")
    print("\n" + "="*70 + "\n")

    # Test parameters
    threshold = 700
    diversity = 0.03

    # Seeds for reproducibility
    seeds = [42, 123, 456]

    # Spawning frequencies to test (as percentages)
    spawn_frequencies = [0, 10, 25, 50, 75, 100]

    results = []
    experiment_num = 0
    total_experiments = len(spawn_frequencies) * len(seeds)

    for freq in spawn_frequencies:
        print(f"\n{'='*70}")
        print(f"SPAWNING FREQUENCY: {freq}%")
        print(f"{'='*70}\n")

        for seed in seeds:
            experiment_num += 1
            print(f"[{experiment_num}/{total_experiments}] ", end="")

            try:
                result = run_experiment_with_frequency(
                    threshold, diversity, seed, freq, cycles=3000, agent_cap=15
                )
                results.append(result)
            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle139_protocol_space_mapping.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 139,
            'experiment': 'protocol_space_mapping',
            'date': datetime.now().isoformat(),
            'threshold': threshold,
            'diversity': diversity,
            'spawn_frequencies': spawn_frequencies,
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
    print(f"CYCLE 139 COMPLETE - PROTOCOL SPACE MAPPING")
    print(f"{'='*70}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Analyze by frequency
    print("RESULTS BY SPAWNING FREQUENCY:\n")

    for freq in spawn_frequencies:
        freq_results = [r for r in results if r['spawn_freq_pct'] == freq]

        if freq_results:
            basin_counts = Counter(r['basin'] for r in freq_results)
            avg_perf = sum(r['cycles_per_sec'] for r in freq_results) / len(freq_results)
            avg_spawn = sum(r['spawn_count'] for r in freq_results) / len(freq_results)
            avg_agents = sum(r['final_agents'] for r in freq_results) / len(freq_results)

            print(f"{freq:>3}% spawning:")
            print(f"  Experiments: {len(freq_results)}")
            print(f"  Average spawns: {avg_spawn:.1f}/{3000} ({avg_spawn/3000*100:.1f}%)")
            print(f"  Average performance: {avg_perf:.1f} cyc/s")
            print(f"  Average final agents: {avg_agents:.1f}")
            print(f"  Basin distribution:")
            for basin in sorted(basin_counts.keys()):
                count = basin_counts[basin]
                pct = count / len(freq_results) * 100
                print(f"    Basin {basin}: {count}/{len(freq_results)} ({pct:.1f}%)")
            print()

    # Find critical threshold
    print("CRITICAL THRESHOLD ANALYSIS:\n")

    basin_A_by_freq = {}
    for freq in spawn_frequencies:
        freq_results = [r for r in results if r['spawn_freq_pct'] == freq]
        if freq_results:
            basin_A_count = sum(1 for r in freq_results if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_results) * 100
            basin_A_by_freq[freq] = basin_A_pct

    print("Basin A probability by spawning frequency:")
    for freq in sorted(basin_A_by_freq.keys()):
        pct = basin_A_by_freq[freq]
        symbol = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"  {freq:>3}%: {pct:>5.1f}% {symbol}")

    # Identify transition region
    transitions = []
    freqs_sorted = sorted(basin_A_by_freq.keys())
    for i in range(len(freqs_sorted) - 1):
        f1, f2 = freqs_sorted[i], freqs_sorted[i+1]
        p1, p2 = basin_A_by_freq[f1], basin_A_by_freq[f2]
        if abs(p2 - p1) > 10:  # Significant change
            transitions.append((f1, f2, p1, p2))

    if transitions:
        print(f"\nTransition regions detected:")
        for f1, f2, p1, p2 in transitions:
            print(f"  {f1}% → {f2}%: Basin A changes from {p1:.1f}% to {p2:.1f}%")
            if p1 < 50 and p2 >= 50:
                print(f"    → CRITICAL THRESHOLD between {f1}% and {f2}%")
    else:
        print(f"\nNo sharp transitions detected - gradual change")

    print(f"\nNext steps:")
    print(f"  1. Run cycle139_analysis.py for detailed statistical analysis")
    print(f"  2. Update CYCLE139_RESULTS.md with findings")
    print(f"  3. Refine critical threshold with finer-grained frequencies if needed")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
