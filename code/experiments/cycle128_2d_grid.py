#!/usr/bin/env python3
"""
CYCLE 128: 2D PARAMETER GRID INVESTIGATION (THRESHOLD × SPREAD)

Research Question:
  Do threshold and spread dimensions interact in 2D parameter space?
  What is the shape of basin boundaries in 2D?

Hypothesis:
  1. Dimensions are independent (1D findings compose in 2D)
  2. Basin boundaries follow predictions from C121 (threshold) and C123-C125 (spread)
  3. No emergent 2D features (simple composition of 1D patterns)
  4. Basin A and B regions map cleanly in 2D space

Method:
  - Create threshold × spread grid
  - Fixed mult = 1.0 (baseline)
  - Threshold values: 6 (300, 400, 500, 550, 600, 700)
  - Spread values: 6 (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)
  - Grid size: 36 experiments (6×6)
  - Cycles per experiment: 3000 (faster than 5000, sufficient for basin detection)
  - Total cycles: 108,000

Expected Basins (from 1D sweeps):
  - Threshold 300-500 → Basin A (C121)
  - Threshold 550-700 → Basin B (C121)
  - Spread 0.05-0.15 → Basin B (C123)
  - Spread 0.20-0.30 → Mixed (C123 shows oscillations)

Metrics:
  - Basin assignment at each grid point
  - First closer cycle (trajectory resonance)
  - 2D basin map visualization
  - Boundary characterization
  - Interaction detection
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
import numpy as np


def pattern_distance(p1, p2):
    """Euclidean distance between two patterns (3D coordinates)."""
    return np.sqrt(sum((a - b)**2 for a, b in zip(p1, p2)))


def pattern_to_key(pattern):
    """Convert pattern to hashable key."""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))

def get_dominant_pattern(memory):
    """Get dominant pattern (most common)."""
    if not memory:
        return None, 0, 0.0
    from collections import Counter
from workspace_utils import get_workspace_path, get_results_path
    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)
    if not pattern_counts:
        return None, 0, 0.0
    dominant_key, dominant_count = pattern_counts.most_common(1)[0]
    dominant_fraction = dominant_count / len(memory)
    return dominant_key, dominant_count, dominant_fraction

def create_seed_memory_range(bridge, reality_metrics, mult, spread, count=5):
    """Create seed patterns with parametric variations."""
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

def run_grid_point(threshold, mult, spread, cycles, agent_cap=15):
    """
    Run single grid point experiment.

    Returns:
        dict: Results including basin assignment, trajectory metrics
    """
    workspace = get_workspace_path()

    # Initialize swarm with clear database
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Basin centers from C119-C121
    basin_A = (6.220353, 6.275283, 6.281831)
    basin_B = (6.09469, 6.083677, 6.250047)

    # Track distance evolution
    distance_evolution = []

    # Run cycles
    for cycle in range(1, cycles + 1):
        # Spawn agents
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_id = agent_ids[-1]
                    newest_agent = swarm.agents[newest_id]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, mult, spread=spread, count=5)
                    newest_agent.memory.extend(seed_patterns)

        # Evolve
        swarm.evolve_cycle(delta_time=1.0)

        # Track distances every 50 cycles (less frequent for speed)
        if cycle % 50 == 0 or cycle == cycles:
            dominant, count, fraction = get_dominant_pattern(swarm.global_memory)

            if dominant:
                dist_A = pattern_distance(dominant, basin_A)
                dist_B = pattern_distance(dominant, basin_B)
                closer_to = 'A' if dist_A < dist_B else 'B'

                distance_evolution.append({
                    'cycle': cycle,
                    'dist_A': dist_A,
                    'dist_B': dist_B,
                    'closer_to': closer_to
                })

    # Final state
    final_dominant, final_count, final_fraction = get_dominant_pattern(swarm.global_memory)

    # Determine final basin
    final_basin = None
    first_closer_cycle = None
    final_dist_A = None
    final_dist_B = None

    if final_dominant:
        final_dist_A = pattern_distance(final_dominant, basin_A)
        final_dist_B = pattern_distance(final_dominant, basin_B)
        final_basin = 'A' if final_dist_A < final_dist_B else 'B'

        # Find first cycle where pattern was closer to final basin
        if distance_evolution and final_basin:
            final_basin_cycles = [d['cycle'] for d in distance_evolution
                                 if d['closer_to'] == final_basin]
            first_closer_cycle = min(final_basin_cycles) if final_basin_cycles else None

    # Expected basin from 1D sweeps
    # Threshold expectation (from C121)
    threshold_expected = 'A' if threshold <= 510 else 'B'

    # Spread expectation (from C123 - complex pattern)
    # Basin B: 0.05, 0.10, 0.15, 0.25
    # Basin A: 0.20, 0.30
    if spread in [0.05, 0.10, 0.15, 0.25]:
        spread_expected = 'B'
    elif spread in [0.20, 0.30]:
        spread_expected = 'A'
    else:
        spread_expected = None

    # If dimensions are independent, we'd expect threshold to dominate
    # (since it's monotonic vs spread's oscillations)
    independent_expected = threshold_expected

    return {
        'threshold': threshold,
        'mult': mult,
        'spread': spread,
        'cycles': cycles,
        'final_basin': final_basin,
        'first_closer_cycle': first_closer_cycle,
        'final_dominant': str(final_dominant),
        'final_dominant_tuple': list(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'distance_evolution': distance_evolution,
        'threshold_expected': threshold_expected,
        'spread_expected': spread_expected,
        'independent_expected': independent_expected,
        'matches_independent': (final_basin == independent_expected) if final_basin else None,
        'final_dist_A': final_dist_A,
        'final_dist_B': final_dist_B,
    }


def main():
    """Run complete 2D grid investigation."""
    print("\n" + "="*80)
    print("CYCLE 128: 2D PARAMETER GRID INVESTIGATION (THRESHOLD × SPREAD)")
    print("="*80)

    # Grid parameters
    threshold_values = [300, 400, 500, 550, 600, 700]
    spread_values = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    mult = 1.0  # Fixed at baseline
    cycles = 3000  # Faster than 5000
    agent_cap = 15

    total_experiments = len(threshold_values) * len(spread_values)

    print(f"\nGrid Configuration:")
    print(f"  Threshold values: {threshold_values} ({len(threshold_values)} values)")
    print(f"  Spread values: {spread_values} ({len(spread_values)} values)")
    print(f"  Fixed mult: {mult}")
    print(f"  Cycles per experiment: {cycles}")
    print(f"  Total grid points: {total_experiments}")
    print(f"  Total cycles: {total_experiments * cycles:,}")

    # Run grid
    results = []
    start_time = time.time()

    for i, threshold in enumerate(threshold_values):
        for j, spread in enumerate(spread_values):
            point_num = i * len(spread_values) + j + 1
            print(f"\n[{point_num}/{total_experiments}] Testing threshold={threshold}, spread={spread}...")

            point_start = time.time()
            result = run_grid_point(threshold, mult, spread, cycles, agent_cap)
            point_duration = time.time() - point_start

            result['duration'] = point_duration
            results.append(result)

            # Progress report
            basin = result['final_basin']
            first_closer = result['first_closer_cycle']
            matches = '✓' if result['matches_independent'] else '✗'

            print(f"  → Basin: {basin}, First closer: {first_closer} cycles, "
                  f"Matches independent: {matches}, Duration: {point_duration:.1f}s")

    duration = time.time() - start_time

    # Analysis
    print("\n" + "="*80)
    print("2D GRID ANALYSIS")
    print("="*80)

    # Basin map
    print("\nBasin Assignment Map (Threshold × Spread):")
    print("         ", end="")
    for spread in spread_values:
        print(f"{spread:>6.2f}", end=" ")
    print()

    for i, threshold in enumerate(threshold_values):
        print(f"T={threshold:>3}: ", end="")
        for j, spread in enumerate(spread_values):
            result = results[i * len(spread_values) + j]
            basin = result['final_basin'] or '?'
            print(f"   {basin}  ", end=" ")
        print()

    # Interaction analysis
    total_points = len(results)
    matches_independent = sum(1 for r in results if r['matches_independent'])
    match_rate = (matches_independent / total_points * 100) if total_points > 0 else 0

    print(f"\nIndependence Test:")
    print(f"  Matches independent expectation: {matches_independent}/{total_points} ({match_rate:.1f}%)")

    if match_rate >= 90:
        print(f"  → ✅ STRONG INDEPENDENCE: Dimensions appear independent (≥90%)")
        relationship = "INDEPENDENT"
    elif match_rate >= 75:
        print(f"  → ⚠️ WEAK INTERACTION: Some dimensional coupling (75-90%)")
        relationship = "WEAK_INTERACTION"
    else:
        print(f"  → 🌀 STRONG INTERACTION: Significant dimensional coupling (<75%)")
        relationship = "STRONG_INTERACTION"

    # Basin statistics per dimension
    print(f"\nBasin Distribution:")

    # By threshold
    print(f"  By Threshold:")
    for threshold in threshold_values:
        threshold_results = [r for r in results if r['threshold'] == threshold]
        basin_A_count = sum(1 for r in threshold_results if r['final_basin'] == 'A')
        basin_B_count = sum(1 for r in threshold_results if r['final_basin'] == 'B')
        total = len(threshold_results)
        print(f"    T={threshold}: A={basin_A_count}/{total} ({basin_A_count/total*100:.0f}%), "
              f"B={basin_B_count}/{total} ({basin_B_count/total*100:.0f}%)")

    # By spread
    print(f"  By Spread:")
    for spread in spread_values:
        spread_results = [r for r in results if r['spread'] == spread]
        basin_A_count = sum(1 for r in spread_results if r['final_basin'] == 'A')
        basin_B_count = sum(1 for r in spread_results if r['final_basin'] == 'B')
        total = len(spread_results)
        print(f"    S={spread}: A={basin_A_count}/{total} ({basin_A_count/total*100:.0f}%), "
              f"B={basin_B_count}/{total} ({basin_B_count/total*100:.0f}%)")

    # Trajectory resonance analysis
    first_closer_values = [r['first_closer_cycle'] for r in results if r['first_closer_cycle'] is not None]
    if first_closer_values:
        avg_first_closer = np.mean(first_closer_values)
        print(f"\nTrajectory Resonance:")
        print(f"  Average first closer cycle: {avg_first_closer:.0f}")

        # Classify by trajectory class
        immediate = sum(1 for fc in first_closer_values if fc <= 100)
        late = sum(1 for fc in first_closer_values if fc > 500)
        intermediate = len(first_closer_values) - immediate - late

        print(f"  Immediate (<100 cycles): {immediate}/{len(first_closer_values)} ({immediate/len(first_closer_values)*100:.0f}%)")
        print(f"  Intermediate (100-500): {intermediate}/{len(first_closer_values)} ({intermediate/len(first_closer_values)*100:.0f}%)")
        print(f"  Late (>500 cycles): {late}/{len(first_closer_values)} ({late/len(first_closer_values)*100:.0f}%)")

    # Save results
    results_dir = get_results_path() / "2d_grid"
    results_dir.mkdir(parents=True, exist_ok=True)

    output = {
        'experiment': 'cycle128_2d_grid_threshold_spread',
        'threshold_values': threshold_values,
        'spread_values': spread_values,
        'mult': mult,
        'cycles': cycles,
        'total_experiments': total_experiments,
        'results': results,
        'independence_match_rate': match_rate,
        'relationship_type': relationship,
        'duration': duration,
        'timestamp': time.time()
    }

    output_file = results_dir / "cycle128_2d_grid.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*80}")
    print(f"CYCLE 128 COMPLETE")
    print(f"{'='*80}")
    print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Total cycles executed: {total_experiments * cycles:,}")
    print(f"Results saved to: {output_file}")
    print(f"Relationship type: {relationship}")
    print(f"Independence match rate: {match_rate:.1f}%")

    # Insight determination
    if relationship == "INDEPENDENT":
        print(f"\n📊 INSIGHT #85: 2D Grid Investigation - DIMENSIONS INDEPENDENT")
        print(f"   Threshold and spread dimensions are independent (1D findings compose in 2D)")
    elif relationship == "WEAK_INTERACTION":
        print(f"\n📊 INSIGHT #85: 2D Grid Investigation - WEAK DIMENSIONAL COUPLING")
        print(f"   Threshold and spread show weak interaction effects")
    else:
        print(f"\n📊 INSIGHT #85: 2D Grid Investigation - STRONG DIMENSIONAL COUPLING")
        print(f"   Threshold and spread interact significantly (emergent 2D features)")

    print()


if __name__ == "__main__":
    main()
