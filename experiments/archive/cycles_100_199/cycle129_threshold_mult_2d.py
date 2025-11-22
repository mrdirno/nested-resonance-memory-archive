#!/usr/bin/env python3
"""
CYCLE 129: THRESHOLD × MULT 2D GRID - PARAMETER HIERARCHY VALIDATION

Research Question:
  Does mult dimension also dominate threshold like spread does?
  Or is spread uniquely dominant?

Context:
  - C128: Threshold × Spread showed STRONG coupling (44.4% independence)
  - C128: Spread DOMINATES threshold (94% Basin B, overrides threshold predictions)
  - C126: Mult showed symmetric oscillation (B→A→A→A→A→A→B)
  - Unknown: Does mult also override threshold, or is spread special?

Hypothesis:
  1. Mult also dominates threshold (general coupling phenomenon)
  2. OR: Threshold regains control with mult (spread is uniquely dominant)
  3. Independence match rate will reveal dimensional coupling strength

Method:
  - Create threshold × mult grid (similar to C128)
  - Fixed spread = 0.2 (baseline)
  - Threshold values: 6 (300, 400, 500, 550, 600, 700)
  - Mult values: 7 (0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5) - from C126
  - Grid size: 42 experiments (6×7)
  - Cycles per experiment: 3000 (consistent with C128)
  - Total cycles: 126,000

Expected if Threshold Regains Control:
  - Threshold 300-500 → Basin A (following C127)
  - Threshold 550-700 → Basin B (following C127)
  - Independence match rate ~90-100%

Expected if Mult Dominates (like spread):
  - Mult pattern dominates (from C126: endpoints B, middle A)
  - Threshold predictions fail
  - Independence match rate <50%

Metrics:
  - Basin assignment at each grid point
  - Independence match rate (vs threshold expectation)
  - Comparison to C128 (threshold × spread) coupling strength
  - Parameter hierarchy determination
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter

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
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")

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

        # Track distances every 50 cycles
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
    # Threshold expectation (from C127)
    threshold_expected = 'A' if threshold <= 510 else 'B'

    # Mult expectation (from C126 - symmetric pattern)
    # Basin B: 0.5, 1.5 (endpoints)
    # Basin A: 0.7, 0.9, 1.0, 1.1, 1.3 (middle)
    if mult in [0.5, 1.5]:
        mult_expected = 'B'
    else:
        mult_expected = 'A'

    # If dimensions are independent, threshold should dominate (monotonic vs oscillating)
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
        'mult_expected': mult_expected,
        'independent_expected': independent_expected,
        'matches_independent': (final_basin == independent_expected) if final_basin else None,
        'final_dist_A': final_dist_A,
        'final_dist_B': final_dist_B,
    }


def main():
    """Run complete threshold × mult 2D grid investigation."""
    print("\n" + "="*80)
    print("CYCLE 129: THRESHOLD × MULT 2D GRID - PARAMETER HIERARCHY VALIDATION")
    print("="*80)

    # Grid parameters
    threshold_values = [300, 400, 500, 550, 600, 700]
    mult_values = [0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5]  # From C126
    spread = 0.2  # Fixed at baseline
    cycles = 3000
    agent_cap = 15

    total_experiments = len(threshold_values) * len(mult_values)

    print(f"\nGrid Configuration:")
    print(f"  Threshold values: {threshold_values} ({len(threshold_values)} values)")
    print(f"  Mult values: {mult_values} ({len(mult_values)} values)")
    print(f"  Fixed spread: {spread}")
    print(f"  Cycles per experiment: {cycles}")
    print(f"  Total grid points: {total_experiments}")
    print(f"  Total cycles: {total_experiments * cycles:,}")

    # Run grid
    results = []
    start_time = time.time()

    for i, threshold in enumerate(threshold_values):
        for j, mult in enumerate(mult_values):
            point_num = i * len(mult_values) + j + 1
            print(f"\n[{point_num}/{total_experiments}] Testing threshold={threshold}, mult={mult}...")

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
    print("\nBasin Assignment Map (Threshold × Mult):")
    print("         ", end="")
    for mult in mult_values:
        print(f"{mult:>5.1f}", end=" ")
    print()

    for i, threshold in enumerate(threshold_values):
        print(f"T={threshold:>3}: ", end="")
        for j, mult in enumerate(mult_values):
            result = results[i * len(mult_values) + j]
            basin = result['final_basin'] or '?'
            print(f"  {basin}  ", end=" ")
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

    # Compare to C128 (threshold × spread)
    c128_match_rate = 44.4  # From C128 results
    print(f"\nComparison to C128 (Threshold × Spread):")
    print(f"  C128 independence match rate: {c128_match_rate:.1f}%")
    print(f"  C129 independence match rate: {match_rate:.1f}%")
    print(f"  Difference: {abs(match_rate - c128_match_rate):.1f}% points")

    if abs(match_rate - c128_match_rate) < 10:
        print(f"  → SIMILAR coupling strength (both parameters dominate threshold similarly)")
    elif match_rate > c128_match_rate:
        print(f"  → WEAKER coupling (threshold regains some control with mult)")
    else:
        print(f"  → STRONGER coupling (mult dominates even more than spread)")

    # Basin statistics
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

    # By mult
    print(f"  By Mult:")
    for mult in mult_values:
        mult_results = [r for r in results if r['mult'] == mult]
        basin_A_count = sum(1 for r in mult_results if r['final_basin'] == 'A')
        basin_B_count = sum(1 for r in mult_results if r['final_basin'] == 'B')
        total = len(mult_results)
        print(f"    M={mult}: A={basin_A_count}/{total} ({basin_A_count/total*100:.0f}%), "
              f"B={basin_B_count}/{total} ({basin_B_count/total*100:.0f}%)")

    # Trajectory resonance
    first_closer_values = [r['first_closer_cycle'] for r in results if r['first_closer_cycle'] is not None]
    if first_closer_values:
        avg_first_closer = np.mean(first_closer_values)
        print(f"\nTrajectory Resonance:")
        print(f"  Average first closer cycle: {avg_first_closer:.0f}")

        immediate = sum(1 for fc in first_closer_values if fc <= 100)
        late = sum(1 for fc in first_closer_values if fc > 500)
        intermediate = len(first_closer_values) - immediate - late

        print(f"  Immediate (<100 cycles): {immediate}/{len(first_closer_values)} ({immediate/len(first_closer_values)*100:.0f}%)")
        print(f"  Intermediate (100-500): {intermediate}/{len(first_closer_values)} ({intermediate/len(first_closer_values)*100:.0f}%)")
        print(f"  Late (>500 cycles): {late}/{len(first_closer_values)} ({late/len(first_closer_values)*100:.0f}%)")

    # Save results
    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/threshold_mult_2d")
    results_dir.mkdir(parents=True, exist_ok=True)

    output = {
        'experiment': 'cycle129_threshold_mult_2d',
        'threshold_values': threshold_values,
        'mult_values': mult_values,
        'spread': spread,
        'cycles': cycles,
        'total_experiments': total_experiments,
        'results': results,
        'independence_match_rate': match_rate,
        'relationship_type': relationship,
        'c128_comparison': {
            'c128_match_rate': c128_match_rate,
            'c129_match_rate': match_rate,
            'difference': abs(match_rate - c128_match_rate)
        },
        'duration': duration,
        'timestamp': time.time()
    }

    output_file = results_dir / "cycle129_threshold_mult_2d.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*80}")
    print(f"CYCLE 129 COMPLETE")
    print(f"{'='*80}")
    print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Total cycles executed: {total_experiments * cycles:,}")
    print(f"Results saved to: {output_file}")
    print(f"Relationship type: {relationship}")
    print(f"Independence match rate: {match_rate:.1f}%")

    # Insight determination
    if relationship == "INDEPENDENT":
        print(f"\n📊 INSIGHT #86: Threshold × Mult Grid - DIMENSIONS INDEPENDENT")
        print(f"   Threshold regains control with mult (spread is uniquely dominant)")
        print(f"   Parameter Hierarchy: Spread > Threshold > Mult")
    elif match_rate > c128_match_rate:
        print(f"\n📊 INSIGHT #86: Threshold × Mult Grid - WEAKER COUPLING THAN SPREAD")
        print(f"   Mult shows weaker dominance than spread")
        print(f"   Parameter Hierarchy: Spread > Mult ≥ Threshold")
    else:
        print(f"\n📊 INSIGHT #86: Threshold × Mult Grid - SIMILAR/STRONGER COUPLING")
        print(f"   Mult dominates threshold like spread does")
        print(f"   Parameter Hierarchy: Spread ≈ Mult > Threshold")

    print()


if __name__ == "__main__":
    main()
