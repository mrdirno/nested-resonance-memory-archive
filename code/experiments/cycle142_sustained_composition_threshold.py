#!/usr/bin/env python3
"""
CYCLE 142: SUSTAINED COMPOSITION THRESHOLD

Research Question:
  What is the exact threshold for sustained composition (deterministic Basin A)?
  How does the transition from resonance → sustained occur?

Context (from Cycles 139-141):
  - 0-45%: Basin B (100%)
  - 50-55%: First resonance (20% Basin A, stochastic)
  - 60-65%: Transition node (0% Basin A)
  - 70-95%: Second resonance (20-40% Basin A, stochastic)
  - 100%: Sustained composition (100% Basin A, deterministic)

  Gap: 96-99% unmapped

Hypothesis:
  - Sustained composition threshold exists between 95-100%
  - Transition may be sharp (phase transition) or gradual
  - Find minimum frequency where Basin A > 80% (approaching deterministic)

Method:
  - Test spawning frequencies: 96%, 97%, 98%, 99%
  - Fixed parameters: threshold=700, diversity=0.03 (Basin A case)
  - 5 seeds per frequency = 4 frequencies × 5 seeds = 20 experiments
  - Cycles per experiment: 3,000
  - Agent cap: 15 (consistent with all prior cycles)

Expected:
  - Gradual or sharp transition from resonance → sustained
  - Identify precise threshold for deterministic Basin A
  - Complete full 0-100% protocol-basin topology map

Publication Significance:
  - Completes experimental mapping
  - Identifies sustained composition threshold
  - Final piece of protocol-basin relationship puzzle
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


def run_experiment_with_frequency(threshold, diversity, seed, spawn_freq_pct, cycles=3000, agent_cap=15):
    """
    Run experiment with specific spawning frequency.
    """
    print(f"  freq={spawn_freq_pct:>3}%, seed={seed:>4}...", end=" ", flush=True)

    random.seed(seed)
    np.random.seed(seed)

    workspace = Path(__file__).parent.parent / "workspace" / f"cycle142_freq{spawn_freq_pct}_seed{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    spread = 0.10
    mult = diversity / spread

    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Seed global memory once
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
    """Run sustained composition threshold experiments"""
    print("\n" + "="*70)
    print("CYCLE 142: SUSTAINED COMPOSITION THRESHOLD")
    print("="*70)
    print("\nResearch Question:")
    print("  What is the exact threshold for deterministic Basin A?")
    print("\nContext:")
    print("  - 95%: Basin A (40%, stochastic, from Cycle 141)")
    print("  - 100%: Basin A (100%, deterministic, from Cycles 138-139)")
    print("  - Gap: 96-99% unmapped")
    print("\nHypothesis:")
    print("  - Sustained composition threshold between 95-100%")
    print("  - Transition may be sharp or gradual")
    print("\nMethod:")
    print("  - Test parameter: threshold=700, diversity=0.03")
    print("  - Spawning frequencies: 96%, 97%, 98%, 99%")
    print("  - Seeds: [42, 123, 456, 789, 1024] (5 replicates)")
    print("  - Total: 4 frequencies × 5 seeds = 20 experiments")
    print("\n" + "="*70 + "\n")

    threshold = 700
    diversity = 0.03
    seeds = [42, 123, 456, 789, 1024]
    spawn_frequencies = [96, 97, 98, 99]

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
    output_path = Path(__file__).parent / 'results' / 'cycle142_sustained_composition_threshold.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 142,
            'experiment': 'sustained_composition_threshold',
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
    print(f"CYCLE 142 COMPLETE - SUSTAINED COMPOSITION THRESHOLD")
    print(f"{'='*70}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    print("RESULTS BY SPAWNING FREQUENCY:\n")

    basin_A_by_freq = {}
    for freq in spawn_frequencies:
        freq_results = [r for r in results if r['spawn_freq_pct'] == freq]

        if freq_results:
            basin_counts = Counter(r['basin'] for r in freq_results)
            avg_perf = sum(r['cycles_per_sec'] for r in freq_results) / len(freq_results)
            avg_spawn = sum(r['spawn_count'] for r in freq_results) / len(freq_results)
            avg_agents = sum(r['final_agents'] for r in freq_results) / len(freq_results)

            basin_A_count = sum(1 for r in freq_results if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_results) * 100
            basin_A_by_freq[freq] = basin_A_pct

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

    # Threshold analysis
    print("SUSTAINED COMPOSITION THRESHOLD ANALYSIS:\n")

    print("Basin A probability by spawning frequency:")
    for freq in sorted(basin_A_by_freq.keys()):
        pct = basin_A_by_freq[freq]
        bar_length = int(pct / 2)
        symbol = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {freq:>3}%: {pct:>5.1f}% {symbol}")

    # Find threshold
    threshold_freq = None
    for freq in sorted(basin_A_by_freq.keys()):
        if basin_A_by_freq[freq] >= 80:  # 80% threshold for "deterministic"
            threshold_freq = freq
            break

    if threshold_freq:
        print(f"\nSustained composition threshold: {threshold_freq}%")
        print(f"  → At {threshold_freq}%, Basin A ≥ 80% (approaching deterministic)")
    else:
        print(f"\nNo deterministic threshold found in 96-99% range")
        print(f"  → Transition may be very sharp at 100%")

    # Complete map
    print(f"\nCOMPLETE PROTOCOL-BASIN TOPOLOGY MAP (0-100%):")
    print(f"  0-45%: Basin B (100%) - insufficient spawning")
    print(f"  50-55%: First resonance (20% Basin A, stochastic)")
    print(f"  60-65%: Transition node (0% Basin A)")
    print(f"  70%: Second resonance start (40% Basin A)")
    print(f"  75%: Anti-resonance node (0% Basin A)")
    print(f"  80-95%: Second resonance (20-40% Basin A, stochastic)")
    for freq in sorted(basin_A_by_freq.keys()):
        pct = basin_A_by_freq[freq]
        print(f"  {freq}%: Basin A ({pct:.0f}%)")
    print(f"  100%: Sustained composition (100% Basin A, deterministic)")

    print(f"\nNext steps:")
    print(f"  1. Update CYCLE142_RESULTS.md with complete map")
    print(f"  2. Develop theoretical harmonic model")
    print(f"  3. Test model predictions")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
