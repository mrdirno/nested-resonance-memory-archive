#!/usr/bin/env python3
"""
CYCLE 135: BASIN TRANSITION BOUNDARY MAPPING

Research Question:
  Where exactly does the Basin A/B transition occur?
  Is the transition sharp (step function) or gradual (sigmoid)?

Context:
  - Cycle 133: Discovered Basin A only at threshold=700, diversity≤0.10
  - Hypothesis: Sharp transition exists between threshold=600-700, diversity=0.10-0.15
  - Need to map exact boundary location

Hypothesis:
  1. Sharp Transition: Step function at specific (threshold, diversity) values
  2. Gradual Transition: Sigmoid-like transition region
  3. Non-Monotonic: Complex boundary shape with multiple transition zones

Method:
  - Focus on boundary region: threshold=[625, 650, 675, 700, 725], diversity=[0.08, 0.10, 0.12, 0.14]
  - Grid: 5 thresholds × 4 diversities = 20 experiments
  - Cycles per experiment: 3000 (same as Cycle 133)
  - Total cycles: 60,000
  - Fixed: spread=0.10, vary mult to achieve diversity

Expected:
  - Locate exact threshold where A→B transition occurs (at fixed diversity)
  - Locate exact diversity where A→B transition occurs (at fixed threshold)
  - Characterize transition sharpness (number of grid cells in transition region)

Publication Significance:
  - Precise boundary location enables prediction
  - Transition sharpness reveals phase transition order
  - Validates Basin A selection rule from Cycle 133
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter
import numpy as np

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


def run_boundary_experiment(threshold, diversity, cycles=3000):
    """
    Run single boundary mapping experiment

    Args:
        threshold: Burst energy threshold
        diversity: Target diversity (spread × mult = diversity, spread=0.10)
        cycles: Number of evolution cycles

    Returns:
        dict: Results including basin assignment
    """
    print(f"  threshold={threshold}, diversity={diversity:.3f}...", end=" ", flush=True)

    # Initialize swarm (matches Cycle 133 API)
    workspace = Path(__file__).parent.parent / "workspace"
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Calculate mult from diversity (spread=0.10 fixed)
    spread = 0.10
    mult = diversity / spread

    # Basin centers (from prior experiments)
    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    # Seed memory with diversity variations
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}
    for i in range(5):
        offset = (i - 2) * spread
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10
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
    """Run boundary mapping experiments"""
    print("\n" + "="*70)
    print("CYCLE 135: BASIN TRANSITION BOUNDARY MAPPING")
    print("="*70)
    print("\nResearch Question:")
    print("  Where exactly does Basin A/B transition occur?")
    print("  Is transition sharp or gradual?")
    print("\nMethod:")
    print("  - Boundary region: threshold=[625-725], diversity=[0.08-0.14]")
    print("  - Grid: 5 × 4 = 20 experiments")
    print("  - Total cycles: 60,000")
    print("\n" + "="*70 + "\n")

    # Define boundary grid
    thresholds = [625, 650, 675, 700, 725]
    diversities = [0.08, 0.10, 0.12, 0.14]

    print(f"Testing {len(thresholds)} thresholds × {len(diversities)} diversities")
    print(f"Total: {len(thresholds) * len(diversities)} experiments\n")

    results = []
    experiment_num = 0
    total_experiments = len(thresholds) * len(diversities)

    for threshold in thresholds:
        for diversity in diversities:
            experiment_num += 1
            print(f"[{experiment_num}/{total_experiments}] ", end="")

            try:
                result = run_boundary_experiment(threshold, diversity, cycles=3000)
                results.append(result)

            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle135_boundary_mapping.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 135,
            'experiment': 'boundary_mapping',
            'date': datetime.now().isoformat(),
            'thresholds': thresholds,
            'diversities': diversities,
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
    print(f"CYCLE 135 COMPLETE")
    print(f"{'='*70}")
    print(f"\nExperiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}")
    print(f"\nBasin distribution:")
    basin_counts = Counter(r['basin'] for r in results)
    for basin, count in sorted(basin_counts.items()):
        print(f"  Basin {basin}: {count}/{len(results)} ({count/len(results)*100:.1f}%)")

    print(f"\nNext steps:")
    print(f"  1. Run cycle135_analysis.py to analyze boundary location")
    print(f"  2. Generate boundary visualization (threshold vs diversity heatmap)")
    print(f"  3. Calculate transition sharpness metrics")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
