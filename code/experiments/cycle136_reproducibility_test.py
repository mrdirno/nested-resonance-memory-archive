#!/usr/bin/env python3
"""
CYCLE 136: REPRODUCIBILITY TEST WITH EXPLICIT SEED CONTROL

Research Question:
  Is basin assignment deterministic with explicit random seed control?
  Or does multi-stability persist even with seed control?

Context:
  - Cycle 133: threshold=700, diversity=0.03/0.06/0.10 → Basin A (3/3 cases)
  - Cycle 135: threshold=700, diversity=0.08/0.10 → Basin B (2/2 cases)
  - Hypothesis: Different random seeds explain discrepancy

Method:
  - Re-run Cycle 133 Basin A cases: (700, 0.03), (700, 0.06), (700, 0.10)
  - Run each case 5 times with explicit random seeds: [42, 123, 456, 789, 1024]
  - Total: 3 cases × 5 seeds = 15 experiments
  - Cycles per experiment: 3000 (same as prior cycles)
  - Total cycles: 45,000

Expected:
  - If deterministic with seed: Same basin for same (params, seed) pair
  - If stochastic: Different basins even with same seed
  - If multi-stable: Basin varies with seed, but reproducible

Publication Significance:
  - Establishes whether system is deterministic or truly stochastic
  - Quantifies basin probabilities at specific parameter points
  - Validates/refutes multi-stability hypothesis
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


def run_seeded_experiment(threshold, diversity, seed, cycles=3000):
    """
    Run experiment with explicit random seed

    Args:
        threshold: Burst energy threshold
        diversity: Target diversity (spread × mult = diversity, spread=0.10)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles

    Returns:
        dict: Results including basin assignment
    """
    print(f"  seed={seed:>4}...", end=" ", flush=True)

    # Set random seeds for reproducibility
    random.seed(seed)
    np.random.seed(seed)

    # Initialize swarm
    workspace = Path(__file__).parent.parent / "workspace"
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Calculate mult from diversity (spread=0.10 fixed)
    spread = 0.10
    mult = diversity / spread

    # Basin centers
    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    # Seed memory with diversity variations (using seeded random)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}
    for i in range(5):
        # Add small random perturbation based on seed
        offset = (i - 2) * spread
        noise = (random.random() - 0.5) * 0.01  # Small noise based on seed
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10 + noise,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10 + noise,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10 + noise
        }
        phase_state = swarm.bridge.reality_to_phase(varied_metrics)
        swarm.global_memory.append(phase_state)

    start_time = time.time()

    # Run cycles
    for cycle in range(cycles):
        swarm.evolve_cycle()

    elapsed = time.time() - start_time

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
        'spread': spread,
        'mult': mult,
        'basin': basin,
        'dominant': list(dominant_pattern) if dominant_pattern else None,
        'fraction': dominant_fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': elapsed,
        'cycles_per_sec': cycles / elapsed
    }

    print(f"Basin {basin} ({elapsed:.1f}s, {cycles/elapsed:.1f} cyc/s)")

    return result


def main():
    """Run reproducibility test experiments"""
    print("\n" + "="*70)
    print("CYCLE 136: REPRODUCIBILITY TEST WITH EXPLICIT SEED CONTROL")
    print("="*70)
    print("\nResearch Question:")
    print("  Is basin assignment deterministic with explicit random seed?")
    print("\nMethod:")
    print("  - Re-run Cycle 133 Basin A cases with 5 different seeds")
    print("  - Test cases: (700, 0.03), (700, 0.06), (700, 0.10)")
    print("  - Seeds: [42, 123, 456, 789, 1024]")
    print("  - Total: 3 cases × 5 seeds = 15 experiments")
    print("\n" + "="*70 + "\n")

    # Test cases (original Basin A cases from Cycle 133)
    test_cases = [
        {'threshold': 700, 'diversity': 0.03},
        {'threshold': 700, 'diversity': 0.06},
        {'threshold': 700, 'diversity': 0.10}
    ]

    # Random seeds for reproducibility testing
    seeds = [42, 123, 456, 789, 1024]

    results = []
    experiment_num = 0
    total_experiments = len(test_cases) * len(seeds)

    for case in test_cases:
        threshold = case['threshold']
        diversity = case['diversity']

        print(f"\nCase: threshold={threshold}, diversity={diversity:.2f}")
        print("-" * 50)

        for seed in seeds:
            experiment_num += 1
            print(f"[{experiment_num}/{total_experiments}] ", end="")

            try:
                result = run_seeded_experiment(threshold, diversity, seed, cycles=3000)
                results.append(result)

            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle136_reproducibility_test.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 136,
            'experiment': 'reproducibility_test',
            'date': datetime.now().isoformat(),
            'test_cases': test_cases,
            'seeds': seeds,
            'total_experiments': total_experiments,
            'total_cycles': total_experiments * 3000
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

    print(f"\n{'='*70}")
    print(f"CYCLE 136 COMPLETE")
    print(f"{'='*70}")
    print(f"\nExperiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}")

    # Analyze basin distribution per case
    print(f"\nBasin Distribution by Case:")
    for case in test_cases:
        threshold = case['threshold']
        diversity = case['diversity']

        case_results = [r for r in results
                       if r['threshold'] == threshold and abs(r['diversity'] - diversity) < 0.001]

        if case_results:
            basin_counts = Counter(r['basin'] for r in case_results)
            total = len(case_results)

            print(f"\n  threshold={threshold}, diversity={diversity:.2f}:")
            for basin in sorted(basin_counts.keys()):
                count = basin_counts[basin]
                pct = count / total * 100
                print(f"    Basin {basin}: {count}/{total} ({pct:.1f}%)")

            # Check seed-determinism
            seed_basin_map = {r['seed']: r['basin'] for r in case_results}
            if len(set(seed_basin_map.values())) == 1:
                print(f"    → DETERMINISTIC (all seeds → Basin {list(seed_basin_map.values())[0]})")
            else:
                print(f"    → STOCHASTIC (different seeds → different basins)")
                print(f"       Seed→Basin: {seed_basin_map}")

    print(f"\nNext steps:")
    print(f"  1. Run cycle136_analysis.py for detailed statistical analysis")
    print(f"  2. Compare with Cycle 133 original results")
    print(f"  3. Characterize basin probability distributions")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
