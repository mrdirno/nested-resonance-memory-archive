#!/usr/bin/env python3
"""
CYCLE 148: TEMPORAL REGIME BOUNDARY MAPPING
Identify Transition Point Between Frequency-Driven and Seed-Driven Dynamics

Research Question:
  Where exactly does the temporal regime transition occur between 3K and 10K cycles?
  At what point do frequency-dependent resonances give way to seed-dependent attractors?

Context (from Insight #108 - Cycle 147):
  - SHORT-TERM (3K cycles): Frequency determines basin (50%→33%, 82%→100%, 95%→33%)
  - LONG-TERM (10K cycles): Seed determines basin (uniform 33% pattern across frequencies)
  - Transition hypothesis: Crossover occurs somewhere between 5K-7.5K cycles

Hypothesis:
  - Basin A probability shifts gradually from frequency-dependent to seed-dependent
  - 82% frequency shows most dramatic transition (100% → 33%)
  - 95% may show elevation at all scales (potential true long-term harmonic)
  - Quantitative boundary identification possible via systematic sampling

Method:
  Strategy: Test multiple cycle counts at key frequencies to map transition

  Cycle counts tested: 3000, 5000, 7500, 10000, 15000, 20000 (6 temporal scales)
  Frequencies: 50% (stable), 82% (collapsing), 95% (elevating)
  Seeds: [42, 123, 456] (3 replicates for statistical validation)
  Total: 6 cycles × 3 frequencies × 3 seeds = 54 experiments

  Predictions:
    - 3K cycles: Frequency-driven (baseline from Cycles 139-146)
    - 5K-7.5K: Transition zone (82% drops, frequencies diverge)
    - 10K+: Seed-driven (uniform 33% except 95%)
    - 15K-20K: Validate stability of seed regime

Expected:
  - Identify exact temporal scale where organizing principle shifts
  - 82% Basin A: 100% @ 3K → ~67% @ 5K → ~33% @ 10K+ (monotonic decline)
  - 50% Basin A: 33% stable across all scales
  - 95% Basin A: 33% @ 3K → elevated @ 10K+ (potential harmonic emergence)

Publication Significance:
  - Quantitative temporal regime boundary identification
  - Validates temporal scale as fundamental variable
  - Maps transition dynamics (not just endpoint states)
  - Establishes methodology for temporal regime detection
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


def run_experiment(threshold, diversity, spawn_freq_pct, seed, cycles, agent_cap=15):
    """
    Run single experiment with specified cycle count.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Seed memory diversity (0.03 = baseline)
        spawn_freq_pct: Spawning frequency percentage
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (VARIABLE IN THIS CYCLE)
        agent_cap: Maximum number of agents

    Returns:
        dict with experiment results
    """
    print(f"  [C={cycles:>5}, F={spawn_freq_pct:>3}%, S={seed:>3}] ", end="", flush=True)

    random.seed(seed)
    np.random.seed(seed)

    workspace = Path(__file__).parent.parent / "workspace" / f"cycle148_C{cycles}_F{spawn_freq_pct}_S{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    spread = 0.10
    mult = diversity / spread

    # Basin references
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
        'cycles': cycles,
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
    """Run temporal regime boundary mapping"""
    print("\n" + "="*80)
    print("CYCLE 148: TEMPORAL REGIME BOUNDARY MAPPING")
    print("="*80)
    print("\nResearch Question:")
    print("  Where does the transition occur between frequency-driven (3K)")
    print("  and seed-driven (10K+) dynamics?")
    print("\nStrategy:")
    print("  Test multiple cycle counts to map transition")
    print("    - Cycle counts: [3K, 5K, 7.5K, 10K, 15K, 20K] (6 temporal scales)")
    print("    - Frequencies: 50% (stable), 82% (collapsing), 95% (elevating)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Total: 6 cycles × 3 frequencies × 3 seeds = 54 experiments")
    print("="*80 + "\n")

    # Fixed parameters (optimal from previous cycles)
    threshold = 700
    diversity = 0.03

    # Test parameters
    cycle_counts = [3000, 5000, 7500, 10000, 15000, 20000]
    key_frequencies = [50, 82, 95]  # Stable, collapsing, elevating
    seeds = [42, 123, 456]

    results = []
    experiment_num = 0
    total_experiments = len(cycle_counts) * len(key_frequencies) * len(seeds)

    print("TEMPORAL REGIME BOUNDARY MAPPING")
    print("="*80 + "\n")

    for cycles in cycle_counts:
        print(f"\nCYCLE COUNT = {cycles:,}")
        print("-" * 80)

        for freq in key_frequencies:
            print(f"  Frequency = {freq}%")

            for seed in seeds:
                experiment_num += 1
                print(f"  [{experiment_num:>2}/{total_experiments}] ", end="")

                try:
                    result = run_experiment(
                        threshold=threshold,
                        diversity=diversity,
                        spawn_freq_pct=freq,
                        seed=seed,
                        cycles=cycles,
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
    output_path = Path(__file__).parent / 'results' / 'cycle148_temporal_regime_boundary_mapping.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 148,
            'experiment': 'temporal_regime_boundary_mapping',
            'date': datetime.now().isoformat(),
            'description': 'Map transition between frequency-driven and seed-driven dynamics',
            'threshold': threshold,
            'diversity': diversity,
            'cycle_counts': cycle_counts,
            'key_frequencies': key_frequencies,
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
    print(f"CYCLE 148 COMPLETE - TEMPORAL REGIME BOUNDARY MAPPING")
    print(f"{'='*80}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Basin A probability by cycle count and frequency
    print("BASIN A PROBABILITY BY CYCLE COUNT AND FREQUENCY:")
    print("="*80 + "\n")

    print(f"{'Cycles':>7} | {'50%':>6} | {'82%':>6} | {'95%':>6} | Notes")
    print("-" * 75)

    for cycles in cycle_counts:
        row = [f"{cycles:>6,}"]
        notes = []

        for freq in key_frequencies:
            freq_cycle_results = [r for r in results if r['cycles'] == cycles and r['spawn_freq_pct'] == freq]
            if freq_cycle_results:
                basin_A_count = sum(1 for r in freq_cycle_results if r['basin'] == 'A')
                basin_A_pct = basin_A_count / len(freq_cycle_results) * 100
                row.append(f"{basin_A_pct:>5.0f}%")

                # Note significant transitions
                if freq == 82 and basin_A_pct < 80:
                    notes.append(f"82% drop")
                if freq == 95 and basin_A_pct > 50:
                    notes.append(f"95% rise")
            else:
                row.append("  N/A")

        notes_str = ", ".join(notes) if notes else ""
        print(" | ".join(row) + f" | {notes_str}")

    # Transition analysis
    print(f"\n\nTRANSITION ANALYSIS:")
    print("="*80)

    print(f"\n82% Frequency (Collapsing Harmonic):")
    for cycles in cycle_counts:
        freq_82_cycle = [r for r in results if r['cycles'] == cycles and r['spawn_freq_pct'] == 82]
        if freq_82_cycle:
            basin_A_count = sum(1 for r in freq_82_cycle if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_82_cycle) * 100

            if basin_A_pct >= 80:
                status = "FREQUENCY-DRIVEN"
            elif basin_A_pct <= 40:
                status = "SEED-DRIVEN"
            else:
                status = "TRANSITION ZONE"

            print(f"  {cycles:>6,} cycles: {basin_A_pct:>5.0f}% Basin A - {status}")

    print(f"\n95% Frequency (Potential Long-Term Harmonic):")
    for cycles in cycle_counts:
        freq_95_cycle = [r for r in results if r['cycles'] == cycles and r['spawn_freq_pct'] == 95]
        if freq_95_cycle:
            basin_A_count = sum(1 for r in freq_95_cycle if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_95_cycle) * 100

            if basin_A_pct > 50:
                status = "ELEVATED (HARMONIC)"
            elif basin_A_pct <= 40:
                status = "BASELINE (SEED)"
            else:
                status = "INTERMEDIATE"

            print(f"  {cycles:>6,} cycles: {basin_A_pct:>5.0f}% Basin A - {status}")

    # Summary statistics
    print(f"\n\nSUMMARY STATISTICS:")
    print("="*80)
    avg_perf = sum(r['cycles_per_sec'] for r in results) / len(results) if results else 0
    total_cycles = sum(r['cycles'] for r in results)
    print(f"  Average performance: {avg_perf:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {sum(r['duration'] for r in results):.1f} seconds")

    print(f"\n\nNEXT STEPS:")
    print("="*80)
    print("  1. Identify exact temporal regime transition point")
    print("  2. Quantify transition rate (how fast does 82% collapse?)")
    print("  3. Validate 95% as true long-term harmonic (if elevated at 15K-20K)")
    print("  4. Update NRM framework with temporal boundary model")
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
