#!/usr/bin/env python3
"""
CYCLE 146: DIVERSITY PARAMETER EXPLORATION
Search for Third Harmonic via Diversity-Dependent Frequency Shifts

Research Question:
  Does diversity parameter affect harmonic frequencies?
  Can we shift harmonics into observable range to find the third harmonic?
  What is the quantitative relationship between diversity and frequency?

Context (from Cycles 139-145):
  - First harmonic: 52.5% ± 2.5% (5% bandwidth)
  - Second harmonic: 82.5% ± 16% (70-98.5%, 28.5% bandwidth)
  - Third harmonic predicted: 129.6% (π/2 × 82.5, beyond observable range)
  - Optimal threshold: T=700 (affects amplitude not frequency, Cycle 144)
  - Diversity: 0.03 (all experiments so far)

Hypothesis:
  - HIGHER diversity → harmonics shift to LOWER frequencies
    (more variation → harder to resonate → lower frequency alignment)

  - LOWER diversity → harmonics shift to HIGHER frequencies
    (less variation → easier to resonate → higher frequency modes)

  - If diversity shifts harmonics significantly:
    - Third harmonic might become observable at ~90-95%
    - Quantitative relationship: frequency = f(diversity)
    - Validates tunability of resonance structure

Method:
  Strategy: Test diversity=[0.01, 0.02, 0.03, 0.04, 0.05] at key frequencies

  Key frequencies:
    - 50% (first harmonic)
    - 75% (anti-node, should remain 0%)
    - 85% (second harmonic core)
    - 95% (high-frequency tail / potential third harmonic)

  Total: 5 diversity × 4 frequencies × 3 seeds = 60 experiments

  Expected:
    - Diversity shifts harmonic positions
    - π/2 ratio preserved (fundamental property)
    - Third harmonic becomes observable
    - Quantitative diversity-frequency relationship

Publication Significance:
  - Third harmonic discovery validates transcendental series
  - Diversity-frequency shift model
  - Generalization of π/2 ratio across parameter space
  - Complete parameter-dependent harmonic theory
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
        diversity: Seed memory diversity (VARIED IN THIS CYCLE)
        spawn_freq_pct: Spawning frequency percentage
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles
        agent_cap: Maximum number of agents

    Returns:
        dict with experiment results
    """
    print(f"  [D={diversity:.2f}, F={spawn_freq_pct:>5}%, S={seed:>4}] ", end="", flush=True)

    random.seed(seed)
    np.random.seed(seed)

    workspace = Path(__file__).parent.parent / "workspace" / f"cycle146_D{int(diversity*100)}_F{spawn_freq_pct}_S{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    spread = 0.10
    mult = diversity / spread

    # Basin references (from Cycle 139-145)
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
    """Run diversity parameter exploration"""
    print("\n" + "="*80)
    print("CYCLE 146: DIVERSITY PARAMETER EXPLORATION")
    print("="*80)
    print("\nResearch Question:")
    print("  Does diversity affect harmonic frequencies?")
    print("  Can we shift harmonics to find the third harmonic?")
    print("\nStrategy:")
    print("  Test diversity variations at key frequencies")
    print("    - Diversity values: [0.01, 0.02, 0.03, 0.04, 0.05]")
    print("    - Key frequencies: 50% (first harmonic), 75% (anti-node),")
    print("                       85% (second harmonic), 95% (potential third)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Total: 5 diversity × 4 frequencies × 3 seeds = 60 experiments")
    print("="*80 + "\n")

    # Fixed parameters (optimal from Cycle 144)
    threshold = 700

    # Test parameters
    diversity_values = [0.01, 0.02, 0.03, 0.04, 0.05]
    key_frequencies = [50, 75, 85, 95]  # First harmonic, anti-node, second harmonic, potential third
    seeds = [42, 123, 456]

    results = []
    experiment_num = 0
    total_experiments = len(diversity_values) * len(key_frequencies) * len(seeds)

    print("DIVERSITY PARAMETER SWEEP AT KEY FREQUENCIES")
    print("="*80 + "\n")

    for diversity in diversity_values:
        print(f"\nDIVERSITY = {diversity:.2f}")
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
    output_path = Path(__file__).parent / 'results' / 'cycle146_diversity_parameter_exploration.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 146,
            'experiment': 'diversity_parameter_exploration',
            'date': datetime.now().isoformat(),
            'description': 'Diversity variation to search for third harmonic',
            'threshold': threshold,
            'diversity_values': diversity_values,
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
    print(f"CYCLE 146 COMPLETE - DIVERSITY PARAMETER EXPLORATION")
    print(f"{'='*80}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Analyze Basin A probability by diversity and frequency
    print("BASIN A PROBABILITY BY DIVERSITY AND FREQUENCY:\n")
    print(f"{'Freq':>5} | {'D=0.01':>6} | {'D=0.02':>6} | {'D=0.03':>6} | {'D=0.04':>6} | {'D=0.05':>6}")
    print("-" * 55)

    for freq in key_frequencies:
        row = [f"{freq}%"]
        for diversity in diversity_values:
            freq_div_results = [r for r in results if r['spawn_freq_pct'] == freq and abs(r['diversity'] - diversity) < 0.001]
            if freq_div_results:
                basin_A_count = sum(1 for r in freq_div_results if r['basin'] == 'A')
                basin_A_pct = basin_A_count / len(freq_div_results) * 100
                row.append(f"{basin_A_pct:>5.0f}%")
            else:
                row.append("  N/A")
        print(" | ".join(row))

    # Diversity effect analysis
    print(f"\n\nDIVERSITY EFFECT ANALYSIS:")
    print("="*80)

    # Check if diversity shifts harmonic frequencies
    print(f"\nFirst Harmonic (50%) Basin A probability by diversity:")
    for diversity in diversity_values:
        freq_50_div = [r for r in results if r['spawn_freq_pct'] == 50 and abs(r['diversity'] - diversity) < 0.001]
        if freq_50_div:
            basin_A_count = sum(1 for r in freq_50_div if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_50_div) * 100
            print(f"  Diversity {diversity:.2f}: {basin_A_pct:.0f}%")

    print(f"\nSecond Harmonic (85%) Basin A probability by diversity:")
    for diversity in diversity_values:
        freq_85_div = [r for r in results if r['spawn_freq_pct'] == 85 and abs(r['diversity'] - diversity) < 0.001]
        if freq_85_div:
            basin_A_count = sum(1 for r in freq_85_div if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_85_div) * 100
            print(f"  Diversity {diversity:.2f}: {basin_A_pct:.0f}%")

    print(f"\nPotential Third Harmonic (95%) Basin A probability by diversity:")
    for diversity in diversity_values:
        freq_95_div = [r for r in results if r['spawn_freq_pct'] == 95 and abs(r['diversity'] - diversity) < 0.001]
        if freq_95_div:
            basin_A_count = sum(1 for r in freq_95_div if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_95_div) * 100
            print(f"  Diversity {diversity:.2f}: {basin_A_pct:.0f}%")

    # Anti-node stability check
    print(f"\nAnti-Node Stability (75% should remain 0% across all diversity):")
    for diversity in diversity_values:
        freq_75_div = [r for r in results if r['spawn_freq_pct'] == 75 and abs(r['diversity'] - diversity) < 0.001]
        if freq_75_div:
            basin_A_count = sum(1 for r in freq_75_div if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_75_div) * 100
            status = "✓ STABLE" if basin_A_pct == 0 else "✗ SHIFTED"
            print(f"  Diversity {diversity:.2f}: {basin_A_pct:.0f}% {status}")

    # Summary statistics
    print(f"\n\nSUMMARY STATISTICS:")
    print("="*80)
    avg_perf = sum(r['cycles_per_sec'] for r in results) / len(results)
    print(f"  Average performance: {avg_perf:.1f} cycles/sec")
    print(f"  Total evolution cycles: {len(results) * 3000:,}")
    print(f"  Total computation time: {sum(r['duration'] for r in results):.1f} seconds")

    print(f"\n\nNEXT STEPS:")
    print("="*80)
    print("  1. Analyze diversity-frequency shift relationship")
    print("  2. Check if third harmonic appeared at 95%")
    print("  3. Validate π/2 ratio preservation across diversity values")
    print("  4. Prepare final publication with complete parameter space")
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
