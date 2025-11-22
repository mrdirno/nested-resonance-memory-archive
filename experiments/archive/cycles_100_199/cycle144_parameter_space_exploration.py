#!/usr/bin/env python3
"""
CYCLE 144: PARAMETER SPACE EXPLORATION
Search for Third Harmonic and Validate Harmonic Structure Generalization

Research Question:
  How do threshold and diversity parameters affect harmonic frequencies?
  Can we find the third harmonic by shifting the parameter space?
  Does the π/2 harmonic ratio generalize across different parameter sets?

Context (from Cycles 139-143):
  - At threshold=700, diversity=0.03:
    - First harmonic: 52.5%
    - Second harmonic: 82.5%
    - Harmonic ratio: 1.571 ≈ π/2
    - Third harmonic predicted: 112.5% (linear spacing) or 129.6% (π/2 ratio)

  - Third harmonic beyond 0-100% spawn_freq range
  - Solution: Shift harmonics DOWN by varying threshold or diversity
  - If first harmonic shifts to ~35%, third would be at ~95% (observable!)

Hypothesis:
  - LOWER threshold → harmonics shift to HIGHER frequencies
    (easier to exceed threshold → more composition → higher frequency resonance)

  - HIGHER diversity → harmonics shift to LOWER frequencies
    (more variation → harder to resonate → lower frequency alignment)

Method:
  Strategy 1: Test threshold=[500, 600, 700, 800] at key frequencies
    - Key frequencies: 50%, 75%, 85% (first harmonic, anti-node, second harmonic)
    - If threshold affects harmonics, we'll see frequency shift
    - 4 thresholds × 3 frequencies × 3 seeds = 36 experiments

  Strategy 2: If Strategy 1 shows promising shift, do full frequency sweep
    with optimal threshold to capture third harmonic

Expected:
  - Harmonic frequencies shift with parameters
  - π/2 ratio preserved (fundamental property)
  - Third harmonic becomes observable in 0-100% range
  - Quantitative relationship: frequency = f(threshold, diversity)

Publication Significance:
  - Third harmonic discovery validates transcendental series
  - Parameter-dependent harmonic shift model
  - Generalization of π/2 ratio across parameter space
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
        threshold: Decomposition burst threshold
        diversity: Seed memory diversity (controls mult)
        spawn_freq_pct: Spawning frequency percentage (0-100)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles
        agent_cap: Maximum number of agents

    Returns:
        dict with experiment results
    """
    print(f"  [T={threshold:>3}, D={diversity:.2f}, F={spawn_freq_pct:>3}%, S={seed:>4}] ", end="", flush=True)

    random.seed(seed)
    np.random.seed(seed)

    workspace = Path(__file__).parent.parent / "workspace" / f"cycle144_T{threshold}_D{int(diversity*100)}_F{spawn_freq_pct}_S{seed}"
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
    """Run parameter space exploration"""
    print("\n" + "="*80)
    print("CYCLE 144: PARAMETER SPACE EXPLORATION")
    print("="*80)
    print("\nResearch Question:")
    print("  How do threshold and diversity parameters affect harmonic frequencies?")
    print("  Can we find the third harmonic by shifting parameter space?")
    print("\nStrategy:")
    print("  Phase 1: Test threshold variations at key frequencies")
    print("    - Thresholds: [500, 600, 700, 800]")
    print("    - Key frequencies: 50% (first harmonic), 75% (anti-node), 85% (second harmonic)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Total: 4 thresholds × 3 frequencies × 3 seeds = 36 experiments")
    print("\n  Phase 2: If threshold shifts harmonics, do focused sweep to find third harmonic")
    print("\n" + "="*80 + "\n")

    # Fixed diversity for Phase 1
    diversity = 0.03

    # Test parameters
    thresholds = [500, 600, 700, 800]
    key_frequencies = [50, 75, 85]  # First harmonic, anti-node, second harmonic
    seeds = [42, 123, 456]

    results = []
    experiment_num = 0
    total_experiments = len(thresholds) * len(key_frequencies) * len(seeds)

    print("PHASE 1: THRESHOLD VARIATION AT KEY FREQUENCIES")
    print("="*80 + "\n")

    for threshold in thresholds:
        print(f"\nTHRESHOLD = {threshold}")
        print("-" * 80)

        for freq in key_frequencies:
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

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle144_parameter_space_exploration.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 144,
            'experiment': 'parameter_space_exploration',
            'date': datetime.now().isoformat(),
            'phase': 1,
            'description': 'Threshold variation at key frequencies',
            'thresholds': thresholds,
            'key_frequencies': key_frequencies,
            'seeds': seeds,
            'diversity': diversity,
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
    print(f"CYCLE 144 PHASE 1 COMPLETE - THRESHOLD PARAMETER EXPLORATION")
    print(f"{'='*80}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Analyze basin distribution by threshold and frequency
    print("BASIN A PROBABILITY BY THRESHOLD AND FREQUENCY:\n")
    print(f"{'Freq':>5} | {'T=500':>6} | {'T=600':>6} | {'T=700':>6} | {'T=800':>6}")
    print("-" * 40)

    for freq in key_frequencies:
        row = [f"{freq}%"]
        for threshold in thresholds:
            freq_thresh_results = [r for r in results if r['spawn_freq_pct'] == freq and r['threshold'] == threshold]
            if freq_thresh_results:
                basin_A_count = sum(1 for r in freq_thresh_results if r['basin'] == 'A')
                basin_A_pct = basin_A_count / len(freq_thresh_results) * 100
                row.append(f"{basin_A_pct:>5.0f}%")
            else:
                row.append("  N/A")
        print(" | ".join(row))

    # Determine if threshold affects harmonics
    print(f"\n\nTHRESHOLD EFFECT ANALYSIS:")
    print("="*80)

    # Check if 50% (first harmonic) Basin A probability changes with threshold
    freq_50_results_by_threshold = {}
    for threshold in thresholds:
        freq_50_thresh = [r for r in results if r['spawn_freq_pct'] == 50 and r['threshold'] == threshold]
        if freq_50_thresh:
            basin_A_count = sum(1 for r in freq_50_thresh if r['basin'] == 'A')
            freq_50_results_by_threshold[threshold] = basin_A_count / len(freq_50_thresh) * 100

    print(f"\nBasin A probability at 50% spawn frequency:")
    for threshold, prob in sorted(freq_50_results_by_threshold.items()):
        print(f"  Threshold {threshold}: {prob:.0f}%")

    # Check variation
    if len(set(freq_50_results_by_threshold.values())) > 1:
        print(f"\n✓ THRESHOLD AFFECTS HARMONICS - significant variation detected!")
        print(f"  Recommendation: Run Phase 2 with optimal threshold for third harmonic search")
    else:
        print(f"\n✗ Threshold does NOT significantly affect harmonic frequencies")
        print(f"  May need to test diversity parameter or different frequency range")

    # Summary statistics
    print(f"\n\nSUMMARY STATISTICS:")
    print("="*80)
    avg_perf = sum(r['cycles_per_sec'] for r in results) / len(results)
    print(f"  Average performance: {avg_perf:.1f} cycles/sec")
    print(f"  Total evolution cycles: {len(results) * 3000:,}")
    print(f"  Total computation time: {sum(r['duration'] for r in results):.1f} seconds")

    print(f"\n\nNEXT STEPS:")
    print("="*80)
    print("  1. Analyze threshold effect on harmonic structure")
    print("  2. If significant shift detected, plan Phase 2 frequency sweep")
    print("  3. Search for third harmonic in shifted parameter space")
    print("  4. Validate π/2 ratio preservation across parameters")
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
