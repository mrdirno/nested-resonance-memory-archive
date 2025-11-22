#!/usr/bin/env python3
"""
CYCLE 141: DEAD ZONE BOUNDARY MAPPING

Research Question:
  Where does the dead zone end and sustained composition begin?
  What is the minimum spawning frequency for deterministic Basin A?

Context (from Cycles 139-140):
  - 0-45%: Basin B (100%)
  - 50-55%: Resonance band (20% Basin A, stochastic)
  - 60%: Basin B (100%, from Cycle 140)
  - 65%: Basin B (100%, from Cycle 140)
  - 75%: Basin B (100%, from Cycle 139) - DEAD ZONE
  - 100%: Basin A (100%, from Cycles 138-139) - SUSTAINED

  Hypothesis from Cycle 139: "Dead zone" exists around 60-75% where neither
  resonance nor sustained composition mechanisms are active.

Hypothesis:
  - Dead zone spans approximately 60-75%
  - Sustained composition threshold exists between 75-100%
  - Transition from dead zone → sustained may be sharp or gradual
  - Find minimum frequency for >50% Basin A (transition point)

Method:
  - Test spawning frequencies: 70%, 75%, 80%, 85%, 90%, 95%
  - Fixed parameters: threshold=700, diversity=0.03 (Basin A case)
  - 5 seeds per frequency = 6 frequencies × 5 seeds = 30 experiments
  - Cycles per experiment: 3,000
  - Agent cap: 15 (consistent with all prior cycles)

Expected:
  - 70-75%: Dead zone continues (Basin B 100%)
  - 80-95%: Transition to sustained composition
  - Find critical frequency where Basin A probability > 50%

Publication Significance:
  - Complete protocol-basin relationship map
  - Identify sustained composition threshold
  - Quantify three distinct regions: resonance, dead zone, sustained
  - Validate NRM predictions about critical transitions
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
    workspace = Path(__file__).parent.parent / "workspace" / f"cycle141_freq{spawn_freq_pct}_seed{seed}"
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
        # Probabilistic spawning based on frequency
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
    """Run dead zone boundary mapping experiments"""
    print("\n" + "="*70)
    print("CYCLE 141: DEAD ZONE BOUNDARY MAPPING")
    print("="*70)
    print("\nResearch Question:")
    print("  Where does dead zone end and sustained composition begin?")
    print("\nContext (from Cycles 139-140):")
    print("  - 60-65%: Basin B (100%) - dead zone start")
    print("  - 75%: Basin B (100%) - dead zone confirmed (Cycle 139)")
    print("  - 100%: Basin A (100%) - sustained composition")
    print("\nHypothesis:")
    print("  - Dead zone spans ~60-75%")
    print("  - Sustained composition threshold exists between 75-100%")
    print("\nMethod:")
    print("  - Test parameter: threshold=700, diversity=0.03")
    print("  - Spawning frequencies: 70%, 75%, 80%, 85%, 90%, 95%")
    print("  - Seeds: [42, 123, 456, 789, 1024] (5 replicates per frequency)")
    print("  - Total: 6 frequencies × 5 seeds = 30 experiments")
    print("\n" + "="*70 + "\n")

    # Test parameters
    threshold = 700
    diversity = 0.03

    # Seeds for reproducibility
    seeds = [42, 123, 456, 789, 1024]

    # Frequencies to test (as percentages)
    spawn_frequencies = [70, 75, 80, 85, 90, 95]

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
    output_path = Path(__file__).parent / 'results' / 'cycle141_dead_zone_boundary_mapping.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 141,
            'experiment': 'dead_zone_boundary_mapping',
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
    print(f"CYCLE 141 COMPLETE - DEAD ZONE BOUNDARY MAPPING")
    print(f"{'='*70}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Analyze by frequency
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

    # Transition analysis
    print("DEAD ZONE → SUSTAINED COMPOSITION TRANSITION:\n")

    print("Basin A probability by spawning frequency:")
    for freq in sorted(basin_A_by_freq.keys()):
        pct = basin_A_by_freq[freq]
        bar_length = int(pct / 2)  # Scale to 50 chars max
        symbol = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {freq:>3}%: {pct:>5.1f}% {symbol}")

    # Find transition point
    transition_freq = None
    for freq in sorted(basin_A_by_freq.keys()):
        if basin_A_by_freq[freq] >= 50:
            transition_freq = freq
            break

    if transition_freq:
        print(f"\nSustained composition threshold: {transition_freq}% spawning")
        print(f"  → At {transition_freq}%, Basin A ≥ 50% (majority)")
    else:
        print(f"\nNo sustained composition found in 70-95% range")
        print(f"  → Threshold must be between 95-100%")

    # Dead zone boundaries
    print(f"\nDead Zone Boundaries:")
    dead_zone_freqs = [f for f in sorted(basin_A_by_freq.keys()) if basin_A_by_freq[f] == 0]
    if dead_zone_freqs:
        print(f"  Dead zone frequencies: {dead_zone_freqs}")
        print(f"  Dead zone range: {min(dead_zone_freqs)}% - {max(dead_zone_freqs)}%")
    else:
        print(f"  No complete dead zone found in tested range")

    # Complete protocol-basin map
    print(f"\nComplete Protocol-Basin Relationship Map:")
    print(f"  0-45%: Basin B (100%) - insufficient spawning")
    print(f"  50-55%: Resonance band (20% Basin A, stochastic)")
    print(f"  60-??%: Dead zone (Basin B 100%, to be confirmed)")
    print(f"  ??-100%: Sustained composition (Basin A majority/100%)")

    print(f"\nNext steps:")
    print(f"  1. Update CYCLE141_RESULTS.md with findings")
    print(f"  2. Test 96-99% if needed to find precise sustained threshold")
    print(f"  3. Compile complete protocol-basin map for publication")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
