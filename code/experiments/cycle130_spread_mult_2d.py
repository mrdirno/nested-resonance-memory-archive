#!/usr/bin/env python3
"""
CYCLE 130: SPREAD × MULT 2D GRID - SEED PARAMETER INTERACTION

Research Question:
  How do two seed parameters (spread × mult) interact in 2D space?
  Do seed parameters couple like seed-burst pairs, or remain independent?

Context:
  - C128: Threshold × Spread (burst × seed) → 44.4% independence (STRONG coupling)
  - C129: Threshold × Mult (burst × seed) → 45.2% independence (STRONG coupling)
  - Parameter Hierarchy: Seed (Spread ≈ Mult) >> Burst (Threshold)
  - Unknown: Do seed parameters interact with each other?

Hypothesis:
  1. High independence (90%+): Seeds don't interfere (orthogonal parameters)
  2. Moderate coupling (~70%): Some seed-seed interaction
  3. Strong coupling (<50%): Seeds couple like seed-burst pairs

Method:
  - Create spread × mult grid (seed × seed interaction)
  - Fixed threshold = 400 (low, solidly in Basin A range from 1D C127)
  - Spread values: 6 (0.05, 0.10, 0.15, 0.20, 0.25, 0.30) - from C123
  - Mult values: 7 (0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5) - from C126
  - Grid size: 42 experiments (6×7)
  - Cycles per experiment: 3000 (consistent with C128-C129)
  - Total cycles: 126,000

Expected from 1D Sweeps:
  - Spread (C123): Oscillating B→B→B→B→A→A→B→A→A
  - Mult (C126): Oscillating symmetric B→A→A→A→A→A→B
  - If independent: Patterns compose (complex 2D pattern)
  - If coupled: One dominates or emergent 2D behavior

Metrics:
  - Basin assignment at each grid point
  - 2D basin map visualization
  - Independence test (do 1D patterns compose?)
  - Comparison to C128-C129 coupling strength
  - Seed-seed vs seed-burst interaction characterization
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
from workspace_utils import get_workspace_path, get_results_path


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
    # Spread expectation (from C123 - oscillating pattern)
    spread_basin_map = {
        0.05: 'B', 0.10: 'B', 0.15: 'B',
        0.20: 'A', 0.25: 'B', 0.30: 'A'
    }
    spread_expected = spread_basin_map.get(spread, None)

    # Mult expectation (from C126 - symmetric oscillating)
    if mult in [0.5, 1.5]:
        mult_expected = 'B'  # Endpoints
    else:
        mult_expected = 'A'  # Middle values

    # If dimensions are independent, need to determine which dominates
    # or if they compose somehow
    # For simplicity, test if EITHER prediction holds (loose independence)
    # or if BOTH must agree (strict independence)
    independent_expected_loose = spread_expected or mult_expected
    independent_expected_strict = spread_expected if spread_expected == mult_expected else None

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
        'spread_expected': spread_expected,
        'mult_expected': mult_expected,
        'agrees_with_spread': (final_basin == spread_expected) if spread_expected and final_basin else None,
        'agrees_with_mult': (final_basin == mult_expected) if mult_expected and final_basin else None,
        'agrees_with_both': (final_basin == spread_expected == mult_expected) if spread_expected and mult_expected and final_basin else None,
        'final_dist_A': final_dist_A,
        'final_dist_B': final_dist_B,
    }


def main():
    """Run complete spread × mult 2D grid investigation."""
    print("\n" + "="*80)
    print("CYCLE 130: SPREAD × MULT 2D GRID - SEED PARAMETER INTERACTION")
    print("="*80)

    # Grid parameters
    spread_values = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]  # From C123
    mult_values = [0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5]  # From C126
    threshold = 400  # Fixed (Basin A in 1D C127)
    cycles = 3000
    agent_cap = 15

    total_experiments = len(spread_values) * len(mult_values)

    print(f"\nGrid Configuration:")
    print(f"  Spread values: {spread_values} ({len(spread_values)} values)")
    print(f"  Mult values: {mult_values} ({len(mult_values)} values)")
    print(f"  Fixed threshold: {threshold}")
    print(f"  Cycles per experiment: {cycles}")
    print(f"  Total grid points: {total_experiments}")
    print(f"  Total cycles: {total_experiments * cycles:,}")

    # Run grid
    results = []
    start_time = time.time()

    for i, spread in enumerate(spread_values):
        for j, mult in enumerate(mult_values):
            point_num = i * len(mult_values) + j + 1
            print(f"\n[{point_num}/{total_experiments}] Testing spread={spread}, mult={mult}...")

            point_start = time.time()
            result = run_grid_point(threshold, mult, spread, cycles, agent_cap)
            point_duration = time.time() - point_start

            result['duration'] = point_duration
            results.append(result)

            # Progress report
            basin = result['final_basin']
            first_closer = result['first_closer_cycle']
            agrees_spread = '✓' if result['agrees_with_spread'] else ('✗' if result['agrees_with_spread'] is not None else '?')
            agrees_mult = '✓' if result['agrees_with_mult'] else ('✗' if result['agrees_with_mult'] is not None else '?')

            print(f"  → Basin: {basin}, First closer: {first_closer} cycles, "
                  f"Agrees spread: {agrees_spread}, Agrees mult: {agrees_mult}, Duration: {point_duration:.1f}s")

    duration = time.time() - start_time

    # Analysis
    print("\n" + "="*80)
    print("2D GRID ANALYSIS")
    print("="*80)

    # Basin map
    print("\nBasin Assignment Map (Spread × Mult):")
    print("         ", end="")
    for mult in mult_values:
        print(f"{mult:>5.1f}", end=" ")
    print()

    for i, spread in enumerate(spread_values):
        print(f"S={spread:>4.2f}: ", end="")
        for j, mult in enumerate(mult_values):
            result = results[i * len(mult_values) + j]
            basin = result['final_basin'] or '?'
            print(f"  {basin}  ", end=" ")
        print()

    # Agreement analysis
    total_points = len(results)

    # Spread agreement
    spread_agrees = sum(1 for r in results if r['agrees_with_spread'])
    spread_total = sum(1 for r in results if r['spread_expected'] is not None)
    spread_rate = (spread_agrees / spread_total * 100) if spread_total > 0 else 0

    # Mult agreement
    mult_agrees = sum(1 for r in results if r['agrees_with_mult'])
    mult_total = sum(1 for r in results if r['mult_expected'] is not None)
    mult_rate = (mult_agrees / mult_total * 100) if mult_total > 0 else 0

    # Both agree
    both_agree = sum(1 for r in results if r['agrees_with_both'])
    both_possible = sum(1 for r in results if r['spread_expected'] is not None and r['mult_expected'] is not None)
    both_rate = (both_agree / both_possible * 100) if both_possible > 0 else 0

    print(f"\nParameter Agreement Test:")
    print(f"  Agrees with spread expectation: {spread_agrees}/{spread_total} ({spread_rate:.1f}%)")
    print(f"  Agrees with mult expectation: {mult_agrees}/{mult_total} ({mult_rate:.1f}%)")
    print(f"  Agrees with BOTH: {both_agree}/{both_possible} ({both_rate:.1f}%)")

    # Determine relationship type
    avg_agreement = (spread_rate + mult_rate) / 2

    if avg_agreement >= 90:
        print(f"  → ✅ HIGH INDEPENDENCE: Parameters appear independent (≥90%)")
        relationship = "HIGH_INDEPENDENCE"
    elif avg_agreement >= 70:
        print(f"  → ⚠️ MODERATE COUPLING: Some seed-seed interaction (70-90%)")
        relationship = "MODERATE_COUPLING"
    else:
        print(f"  → 🌀 STRONG COUPLING: Significant seed-seed interaction (<70%)")
        relationship = "STRONG_COUPLING"

    # Compare to C128-C129 (seed-burst coupling)
    c128_match = 44.4
    c129_match = 45.2
    seed_burst_avg = (c128_match + c129_match) / 2

    print(f"\nComparison to Seed-Burst Coupling:")
    print(f"  C128 (T×S seed-burst): {c128_match:.1f}% independence")
    print(f"  C129 (T×M seed-burst): {c129_match:.1f}% independence")
    print(f"  C130 (S×M seed-seed): {avg_agreement:.1f}% average agreement")
    print(f"  Difference from seed-burst: {avg_agreement - seed_burst_avg:.1f}% points")

    if avg_agreement > seed_burst_avg + 20:
        print(f"  → Seed-seed interaction WEAKER than seed-burst (more independent)")
    elif avg_agreement < seed_burst_avg - 20:
        print(f"  → Seed-seed interaction STRONGER than seed-burst (more coupled)")
    else:
        print(f"  → Seed-seed interaction SIMILAR to seed-burst coupling")

    # Basin statistics
    print(f"\nBasin Distribution:")

    # By spread
    print(f"  By Spread:")
    for spread in spread_values:
        spread_results = [r for r in results if r['spread'] == spread]
        basin_A_count = sum(1 for r in spread_results if r['final_basin'] == 'A')
        basin_B_count = sum(1 for r in spread_results if r['final_basin'] == 'B')
        total = len(spread_results)
        print(f"    S={spread}: A={basin_A_count}/{total} ({basin_A_count/total*100:.0f}%), "
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
    results_dir = get_results_path() / "spread_mult_2d"
    results_dir.mkdir(parents=True, exist_ok=True)

    output = {
        'experiment': 'cycle130_spread_mult_2d',
        'spread_values': spread_values,
        'mult_values': mult_values,
        'threshold': threshold,
        'cycles': cycles,
        'total_experiments': total_experiments,
        'results': results,
        'spread_agreement_rate': spread_rate,
        'mult_agreement_rate': mult_rate,
        'both_agreement_rate': both_rate,
        'average_agreement': avg_agreement,
        'relationship_type': relationship,
        'comparison_to_seed_burst': {
            'c128_independence': c128_match,
            'c129_independence': c129_match,
            'seed_burst_avg': seed_burst_avg,
            'seed_seed_avg': avg_agreement,
            'difference': avg_agreement - seed_burst_avg
        },
        'duration': duration,
        'timestamp': time.time()
    }

    output_file = results_dir / "cycle130_spread_mult_2d.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*80}")
    print(f"CYCLE 130 COMPLETE")
    print(f"{'='*80}")
    print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Total cycles executed: {total_experiments * cycles:,}")
    print(f"Results saved to: {output_file}")
    print(f"Relationship type: {relationship}")
    print(f"Average parameter agreement: {avg_agreement:.1f}%")

    # Insight determination
    if relationship == "HIGH_INDEPENDENCE":
        print(f"\n📊 INSIGHT #87: Spread × Mult Grid - SEED PARAMETERS INDEPENDENT")
        print(f"   Seed parameters (spread, mult) don't interfere with each other")
        print(f"   Seed-seed coupling WEAKER than seed-burst coupling")
    elif relationship == "MODERATE_COUPLING":
        print(f"\n📊 INSIGHT #87: Spread × Mult Grid - MODERATE SEED-SEED COUPLING")
        print(f"   Seed parameters show moderate interaction")
        print(f"   Weaker than seed-burst but not fully independent")
    else:
        print(f"\n📊 INSIGHT #87: Spread × Mult Grid - STRONG SEED-SEED COUPLING")
        print(f"   Seed parameters interact as strongly as seed-burst pairs")
        print(f"   All parameter pairs show strong coupling")

    print()


if __name__ == "__main__":
    main()
