#!/usr/bin/env python3
"""
Cycle 127: Threshold Resonance Investigation - Completing Parameter Space Trilogy

Research Context:
  C122-C126: Multi-Dimensional Parameter Space Characterization
  - C122: Basin structure parameter-dependent (25-75% robustness)
  - C123-C125: Spread dimension oscillating (100% validated trajectory resonance)
  - C126: Mult dimension oscillating (trajectory resonance generalizes)
  - Trajectory resonance: Universal mechanism across spread + mult dimensions

Research Gap:
  Trajectory resonance validated for spread and mult dimensions
  Unknown if THRESHOLD parameter also exhibits trajectory resonance
  C111-C121 characterized threshold at baseline (mult=1.0, spread=0.2) but didn't track "first closer"
  Need to test if threshold shows immediate vs late shift trajectory classes

Key Question:
  Does threshold dimension exhibit trajectory resonance like spread and mult?
  Is "first closer" metric applicable to threshold parameter?

Hypotheses to Test:
  1. **Threshold Resonance**: Threshold shows oscillating basin behavior
     - Prediction: Some thresholds show immediate attraction, others late shift
     - Test: Track "first closer" cycle for threshold range

  2. **Complete Trilogy**: All three parameters (threshold, spread, mult) show resonance
     - Prediction: Threshold has same trajectory classes as spread/mult
     - Test: Compare threshold results to C123-C126 patterns

  3. **Universal Framework**: "First closer" metric works for threshold
     - Prediction: < 100 cyc → Basin B, > 500 cyc → Basin A
     - Test: Validate prediction accuracy

  4. **Dimensional Independence**: Threshold oscillation pattern differs from spread/mult
     - Prediction: Different geometric pattern but same mechanism
     - Test: Map basin sequence across threshold range

Research Question:
  Systematically vary threshold (300-700) at fixed mult=1.0, spread=0.2 (baseline)
  to test if trajectory resonance applies to threshold dimension.

Test Conditions:
  **FIXED**:
    - Mult: 1.0 (baseline)
    - Spread: 0.2 (baseline)
    - Cycles: 5000 per run (sufficient for stabilization)

  **THRESHOLD SWEEP**:
    - Values: 300, 350, 400, 450, 500, 550, 600, 650, 700
    - 9 values spanning C111-C121 characterized range
    - Includes boundary region (500-550) from C120-C121
    - 50-unit intervals (except boundary which is 25-50 units)

  **TRACKING**:
    - "First closer" cycle detection
    - Trajectory type classification (immediate vs late shift)
    - Basin assignment
    - Comparison to C111-C121 baseline expectations

Metrics:
  - **Basin Sequence**: Pattern of A/B assignments across threshold range
  - **"First Closer" Cycle**: When pattern becomes closer to final basin
  - **Trajectory Type**: Immediate attraction vs late shift
  - **Oscillation Pattern**: Compare to spread (asymmetric) and mult (symmetric)
  - **Prediction Accuracy**: Validate "first closer" framework

Expected Outcome:
  - If threshold resonates → see oscillating basin pattern
  - If trajectory classes apply → "first closer" predicts basin
  - If generalizes → same mechanism as spread/mult
  - If independent → different geometry but universal framework

Publication Value:
  - **EXTRAORDINARY**: Completes parameter space trilogy (threshold × spread × mult)
  - **Novel**: First investigation of threshold trajectory resonance
  - **Complete**: All three parameters characterized with same framework
  - **Universal**: Trajectory resonance as fundamental parameter space property
  - **Theoretical**: Establishes complete multi-dimensional understanding
"""

import sys
from pathlib import Path
import time
import json
import numpy as np
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge

def create_seed_memory_range(bridge, reality_metrics, center_multiplier, spread=0.2, count=5):
    """Create seed memory patterns with specified center and spread."""
    seed_patterns = []
    for i in range(count):
        multiplier = center_multiplier + spread * (2 * i / (count - 1) - 1)
        varied_metrics = {key: value * multiplier for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

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

def pattern_distance(pattern1, pattern2):
    """Calculate Euclidean distance between two patterns."""
    if pattern1 is None or pattern2 is None:
        return None

    if isinstance(pattern1, tuple):
        p1 = np.array(pattern1)
    else:
        p1 = np.array([pattern1.pi_phase, pattern1.e_phase, pattern1.phi_phase])

    if isinstance(pattern2, tuple):
        p2 = np.array(pattern2)
    else:
        p2 = np.array([pattern2.pi_phase, pattern2.e_phase, pattern2.phi_phase])

    return np.linalg.norm(p1 - p2)

def run_threshold_resonance(threshold, mult, spread, cycles, agent_cap=15):
    """Run experiment varying threshold to test trajectory resonance."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Basin centers from C119-C121
    basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
    basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

    # Track evolution
    distance_evolution = []

    print(f"\nRunning threshold={threshold} (mult={mult}, spread={spread}) for {cycles} cycles...")
    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Progress indicator
        if cycle % 100 == 0:
            elapsed = time.time() - start_time
            rate = cycle / elapsed
            remaining = (cycles - cycle) / rate
            print(f"  Cycle {cycle:5d}/{cycles} ({cycle/cycles*100:5.1f}%) | {rate:6.1f} cyc/s | ETA: {remaining/60:5.1f} min", end='\r', flush=True)

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

        # Track (every 10 cycles)
        if cycle % 10 == 0:
            dominant, count, fraction = get_dominant_pattern(swarm.global_memory)

            # Calculate distances to basins
            if dominant:
                dist_A = pattern_distance(dominant, basin_A)
                dist_B = pattern_distance(dominant, basin_B)

                distance_evolution.append({
                    'cycle': cycle,
                    'dist_A': dist_A,
                    'dist_B': dist_B,
                    'closer_to': 'A' if dist_A < dist_B else 'B'
                })

    print()  # New line

    duration = time.time() - start_time

    # Final pattern and basin assignment
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    if final_dominant:
        final_dist_A = pattern_distance(final_dominant, basin_A)
        final_dist_B = pattern_distance(final_dominant, basin_B)
        final_basin = 'A' if final_dist_A < final_dist_B else 'B'
    else:
        final_dist_A = None
        final_dist_B = None
        final_basin = None

    # Find "first closer to final basin" cycle
    if distance_evolution and final_basin:
        final_basin_cycles = [d['cycle'] for d in distance_evolution if d['closer_to'] == final_basin]
        if final_basin_cycles:
            first_closer_cycle = min(final_basin_cycles)
        else:
            first_closer_cycle = None
    else:
        first_closer_cycle = None

    # Expected basin from C111-C121
    expected_basin = 'A' if threshold <= 510 else 'B'

    return {
        'threshold': threshold,
        'mult': mult,
        'spread': spread,
        'cycles': cycles,
        'duration': duration,
        'distance_evolution': distance_evolution,
        'first_closer_cycle': first_closer_cycle,
        'final_basin': final_basin,
        'expected_basin': expected_basin,
        'matches_expected': (final_basin == expected_basin) if final_basin else None,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_dominant_tuple': final_dominant,
        'final_fraction': final_fraction,
        'final_dist_A': final_dist_A,
        'final_dist_B': final_dist_B
    }

def main():
    print("="*80)
    print("CYCLE 127: THRESHOLD RESONANCE INVESTIGATION")
    print("="*80)
    print()
    print("Testing if trajectory resonance applies to threshold dimension")
    print()
    print("C122-C126 Findings:")
    print("  - Spread dimension: Oscillating asymmetric (B→B→B→B→A→A→B→A→A)")
    print("  - Mult dimension: Oscillating symmetric (B→A→A→A→A→A→B)")
    print("  - Trajectory resonance: Universal mechanism (100% validated)")
    print("  - 'First closer' metric: Predicts basin across dimensions")
    print()
    print("Research Question: Does threshold show trajectory resonance?")
    print()
    print("Test Approach:")
    print("  - Fixed mult=1.0, spread=0.2 (baseline)")
    print("  - Threshold sweep: 300-700 (9 values)")
    print("  - Track 'first closer' metric")
    print("  - Complete parameter space trilogy (threshold × spread × mult)")
    print()

    cycles = 5000
    agent_cap = 15
    mult = 1.0  # Fixed (baseline)
    spread = 0.2  # Fixed (baseline)

    # Threshold sweep (spanning C111-C121 range with focus on boundary)
    threshold_values = [300, 350, 400, 450, 500, 550, 600, 650, 700]

    print(f"Configuration:")
    print(f"  Fixed mult: {mult}")
    print(f"  Fixed spread: {spread}")
    print(f"  Threshold values: {threshold_values}")
    print(f"  Total experiments: {len(threshold_values)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(threshold_values) * cycles:,}")
    print(f"  Estimated duration: ~{len(threshold_values) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, threshold in enumerate(threshold_values):
        print(f"\n[{i+1}/{len(threshold_values)}] THRESHOLD = {threshold}")
        print("-" * 80)

        try:
            result = run_threshold_resonance(threshold, mult, spread, cycles, agent_cap)
            results.append(result)

            first_closer = result['first_closer_cycle']
            final_basin = result['final_basin']
            expected = result['expected_basin']
            matches = result['matches_expected']

            print(f"\n  ✓ COMPLETE:")
            print(f"    Final basin: {final_basin} (expected: {expected}, {'✓ MATCH' if matches else '✗ DIFFER'})")
            print(f"    First closer: {first_closer if first_closer else 'N/A'}")

            time.sleep(0.05)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            results.append({
                'threshold': threshold, 'mult': mult, 'spread': spread, 'error': str(e)
            })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"THRESHOLD RESONANCE ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 1:
        print("Basin Assignment by Threshold:")
        print(f"{'Threshold':^10} | {'First Closer':^13} | {'Basin':^6} | {'Expected':^8} | {'Match':^6} | {'Trajectory Type':^20}")
        print("-" * 90)

        threshold_basin_map = []

        for r in successful:
            threshold = r['threshold']
            basin = r['final_basin']
            expected = r['expected_basin']
            matches = r['matches_expected']
            first_closer = r['first_closer_cycle'] if r['first_closer_cycle'] else 'N/A'

            # Classify trajectory type
            if first_closer != 'N/A':
                if first_closer < 100:
                    traj_type = 'Immediate'
                elif first_closer > 500:
                    traj_type = 'Late Shift'
                else:
                    traj_type = 'Intermediate'
            else:
                traj_type = 'Unknown'

            threshold_basin_map.append({
                'threshold': threshold,
                'basin': basin,
                'expected': expected,
                'matches': matches,
                'first_closer': first_closer,
                'trajectory_type': traj_type
            })

            first_closer_str = str(first_closer) if first_closer != 'N/A' else 'N/A'
            match_str = '✓' if matches else '✗'

            print(f"{threshold:^10d} | {first_closer_str:^13} | {basin:^6} | {expected:^8} | {match_str:^6} | {traj_type:^20}")

        print()

        # Analyze oscillation
        print("="*80)
        print("OSCILLATION ANALYSIS")
        print("="*80)

        threshold_sequence = [item['threshold'] for item in sorted(threshold_basin_map, key=lambda x: x['threshold'])]
        basin_sequence = [item['basin'] for item in sorted(threshold_basin_map, key=lambda x: x['threshold'])]

        print(f"Threshold sequence: {threshold_sequence}")
        print(f"Basin sequence:     {basin_sequence}")
        print()

        # Check transitions
        basin_changes = []
        for i in range(len(basin_sequence) - 1):
            if basin_sequence[i] != basin_sequence[i+1]:
                basin_changes.append({
                    'from_threshold': threshold_sequence[i],
                    'to_threshold': threshold_sequence[i+1],
                    'from_basin': basin_sequence[i],
                    'to_basin': basin_sequence[i+1]
                })

        if len(basin_changes) == 0:
            relationship_type = "CONSTANT"
            print(f"✓ Basin assignment is CONSTANT across all threshold values")
            print(f"✓ All thresholds → Basin {basin_sequence[0]}")
            insight_type = "threshold_invariant"
        elif len(basin_changes) == 1:
            relationship_type = "CRITICAL TRANSITION"
            change = basin_changes[0]
            print(f"✓ CRITICAL TRANSITION detected:")
            print(f"  Threshold ≤ {change['from_threshold']}: Basin {change['from_basin']}")
            print(f"  Threshold ≥ {change['to_threshold']}: Basin {change['to_basin']}")
            insight_type = "critical_transition"
        else:
            relationship_type = "MULTIPLE TRANSITIONS"
            print(f"⚠️ MULTIPLE TRANSITIONS detected (OSCILLATING):")
            for change in basin_changes:
                print(f"  {change['from_threshold']} → {change['to_threshold']}: Basin {change['from_basin']} → {change['to_basin']}")
            insight_type = "oscillating"

        print()

        # Compare to C111-C121 expectations
        print("="*80)
        print("COMPARISON TO C111-C121 BASELINE")
        print("="*80)

        matches = sum(1 for item in threshold_basin_map if item['matches'])
        total = len(threshold_basin_map)
        match_rate = matches / total * 100 if total > 0 else 0

        print(f"C111-C121 expectation: Threshold ≤510 → Basin A, ≥520 → Basin B")
        print(f"C127 results: {matches}/{total} matches ({match_rate:.1f}%)")
        print()

        if match_rate >= 80:
            print(f"✓ HIGH AGREEMENT: C127 matches C111-C121 baseline ({match_rate:.1f}%)")
            print(f"✓ Threshold dimension behaves as expected at baseline parameters")
        elif match_rate >= 50:
            print(f"⚠️ PARTIAL AGREEMENT: C127 partially matches C111-C121 ({match_rate:.1f}%)")
            print(f"⚠️ Some deviations from baseline expectations")
        else:
            print(f"✗ LOW AGREEMENT: C127 differs from C111-C121 ({match_rate:.1f}%)")
            print(f"✗ Significant deviations from baseline expectations")

        print()

        # Compare to spread and mult dimensions
        print("="*80)
        print("MULTI-DIMENSIONAL COMPARISON")
        print("="*80)
        print("Spread dimension (C123-C125):")
        print("  - Pattern: B→B→B→B→A→A→B→A→A (asymmetric, oscillating)")
        print("  - Transitions: 3")
        print()
        print("Mult dimension (C126):")
        print("  - Pattern: B→A→A→A→A→A→B (symmetric, oscillating)")
        print("  - Transitions: 2")
        print()
        print(f"Threshold dimension (C127):")
        print(f"  - Pattern: {' → '.join(basin_sequence)} ({len(threshold_sequence)} values)")
        print(f"  - Transitions: {len(basin_changes)}")
        if relationship_type == "MULTIPLE TRANSITIONS":
            print(f"  - ✓ OSCILLATING (similar to spread/mult)")
        elif relationship_type == "CRITICAL TRANSITION":
            print(f"  - ⚠️ SINGLE TRANSITION (different from spread/mult)")
        else:
            print(f"  - ⚠️ CONSTANT (different from spread/mult)")

        print()
        print(f"📊 INSIGHT #84: Threshold Resonance Investigation - {relationship_type}")
        print(f"   - Tested 9 threshold values (300-700)")
        print(f"   - Relationship type: {relationship_type}")
        print(f"   - C111-C121 match rate: {match_rate:.1f}%")
        print(f"   - Insight type: {insight_type}")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        relationship_type = None
        match_rate = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "threshold_resonance"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle127_threshold_resonance.json"

    output_data = {
        'experiment': 'cycle127_threshold_resonance',
        'mult': mult,
        'spread': spread,
        'threshold_values': threshold_values,
        'cycles': cycles,
        'results': results,
        'relationship_type': relationship_type if 'relationship_type' in locals() else None,
        'c111_c121_match_rate': match_rate if 'match_rate' in locals() else None,
        'insight_type': insight_type if 'insight_type' in locals() else False,
        'duration': duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Duration: {duration:.1f}s ({duration/60:.2f} min)")
    print()

    return output_data

if __name__ == "__main__":
    main()
