#!/usr/bin/env python3
"""
Cycle 126: Mult Parameter Investigation - Generalizing Trajectory Resonance

Research Context:
  C122-C125: Spread Parameter Complete Characterization
  - C122: Parameter-dependent basin structure (25-75% robustness)
  - C123: OSCILLATING basin assignment in spread dimension (B→B→B→A→B→A)
  - C124: TRAJECTORY RESONANCE mechanism (late shift vs immediate attraction)
  - C125: 100% prediction accuracy validation, isolated Basin B at spread 0.25

Research Gap:
  C122-C125 fully characterized SPREAD dimension at threshold 400, mult 1.0
  Unknown if MULT parameter shows similar oscillating/resonance behavior
  Unknown if "first closer" metric applies to mult dimension
  Unknown if trajectory resonance is GENERAL phenomenon or spread-specific

Key Question:
  Does mult parameter exhibit trajectory resonance similar to spread parameter?
  Is the "first closer" predictive framework generalizable across parameters?

Hypotheses to Test:
  1. **Mult Oscillation**: Mult dimension shows oscillating basin assignment like spread
     - Prediction: Mult sweep reveals non-monotonic A/B pattern
     - Test: Systematically vary mult (0.5-1.5) at fixed threshold, spread

  2. **Trajectory Resonance Applies**: "First closer" metric works for mult
     - Prediction: Immediate attraction (< 100 cyc) vs late shift (> 500 cyc)
     - Test: Track "first closer" cycle for each mult value

  3. **Cross-Parameter Generalization**: Mechanism applies beyond spread
     - Prediction: Same late-shift vs immediate-attraction classes
     - Test: Compare mult results to spread results (C123-C125)

  4. **Parameter Independence**: Mult and spread are independent controls
     - Prediction: Mult shows different basin sequence than spread
     - Test: Check if mult oscillation pattern differs from spread pattern

Research Question:
  Systematically vary mult parameter (0.5-1.5) at fixed threshold=400, spread=0.2
  (baseline parameters) to test if trajectory resonance generalizes to mult dimension.

Test Conditions:
  **FIXED**:
    - Threshold: 400 (same as C122-C125)
    - Spread: 0.2 (baseline, middle of spread range)
    - Cycles: 5000 per run (sufficient for stabilization)

  **MULT SWEEP**:
    - Values: 0.5, 0.7, 0.9, 1.0 (baseline), 1.1, 1.3, 1.5
    - 7 values spanning C122 tested range (0.5, 1.5) plus intermediate
    - 0.2 intervals (similar granularity to spread's 0.05 intervals relative to range)

  **TRACKING**: Same as C124/C125
    - Pattern evolution every 10 cycles
    - "First closer" cycle detection
    - Basin distances over time

Metrics:
  - **Basin Sequence**: Pattern of A/B assignments across mult range
  - **"First Closer" Cycle**: When pattern becomes closer to final basin
  - **Trajectory Type**: Immediate attraction vs late shift
  - **Oscillation Pattern**: Compare to spread oscillation (C123)
  - **Lock-in Timing**: When pattern stabilizes

Expected Outcome:
  - If mult oscillates → see non-monotonic A/B pattern like spread
  - If trajectory resonance applies → "first closer" predicts basin
  - If generalizes → same mechanism classes (immediate vs late)
  - If independent → different oscillation pattern than spread

Publication Value:
  - **HIGH**: Tests generalizability of C123-C125 trajectory resonance mechanism
  - **Novel**: First investigation of mult dimension resonance
  - **Complete**: Parallel characterization to spread dimension
  - **Theoretical**: Validates trajectory resonance as general phenomenon vs parameter-specific
  - **Engineering**: Extends "first closer" framework to mult parameter
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
from workspace_utils import get_workspace_path, get_results_path

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

def run_mult_sweep(threshold, mult, spread, cycles, agent_cap=15):
    """Run experiment varying mult to test trajectory resonance."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Basin centers from C119-C121
    basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
    basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

    # Track evolution
    distance_evolution = []

    print(f"\nRunning mult={mult} (threshold={threshold}, spread={spread}) for {cycles} cycles...")
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

    return {
        'threshold': threshold,
        'mult': mult,
        'spread': spread,
        'cycles': cycles,
        'duration': duration,
        'distance_evolution': distance_evolution,
        'first_closer_cycle': first_closer_cycle,
        'final_basin': final_basin,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_dominant_tuple': final_dominant,
        'final_fraction': final_fraction,
        'final_dist_A': final_dist_A,
        'final_dist_B': final_dist_B
    }

def main():
    print("="*80)
    print("CYCLE 126: MULT PARAMETER INVESTIGATION")
    print("="*80)
    print()
    print("Testing if trajectory resonance generalizes to mult dimension")
    print()
    print("C122-C125 Findings:")
    print("  - Spread dimension fully characterized (9 values, 100% validated)")
    print("  - TRAJECTORY RESONANCE mechanism (late shift vs immediate attraction)")
    print("  - 'First closer' metric 100% accurate for spread")
    print("  - Isolated Basin B at spread 0.25")
    print()
    print("Research Question: Does mult show similar oscillating/resonance behavior?")
    print()
    print("Test Approach:")
    print("  - Fixed threshold=400, spread=0.2 (baseline)")
    print("  - Mult sweep: 0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5")
    print("  - Track 'first closer' metric")
    print("  - Compare to spread oscillation pattern")
    print()

    cycles = 5000
    agent_cap = 15
    threshold = 400  # Fixed (baseline)
    spread = 0.2  # Fixed (baseline, middle of spread range)

    # Mult sweep (spanning C122 range plus intermediate values)
    mult_values = [0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5]

    print(f"Configuration:")
    print(f"  Fixed threshold: {threshold}")
    print(f"  Fixed spread: {spread}")
    print(f"  Mult values: {mult_values}")
    print(f"  Total experiments: {len(mult_values)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(mult_values) * cycles:,}")
    print(f"  Estimated duration: ~{len(mult_values) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, mult in enumerate(mult_values):
        print(f"\n[{i+1}/{len(mult_values)}] MULT = {mult}")
        print("-" * 80)

        try:
            result = run_mult_sweep(threshold, mult, spread, cycles, agent_cap)
            results.append(result)

            first_closer = result['first_closer_cycle']
            final_basin = result['final_basin']

            print(f"\n  ✓ COMPLETE:")
            print(f"    Final basin: {final_basin}")
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
    print(f"MULT PARAMETER ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 1:
        print("Basin Assignment by Mult:")
        print(f"{'Mult':^8} | {'First Closer':^13} | {'Basin':^6} | {'Trajectory Type':^20}")
        print("-" * 65)

        mult_basin_map = []

        for r in successful:
            mult = r['mult']
            basin = r['final_basin']
            first_closer = r['first_closer_cycle'] if r['first_closer_cycle'] else 'N/A'

            # Classify trajectory type based on C124/C125 criteria
            if first_closer != 'N/A':
                if first_closer < 100:
                    traj_type = 'Immediate'
                elif first_closer > 500:
                    traj_type = 'Late Shift'
                else:
                    traj_type = 'Intermediate'
            else:
                traj_type = 'Unknown'

            mult_basin_map.append({
                'mult': mult,
                'basin': basin,
                'first_closer': first_closer,
                'trajectory_type': traj_type
            })

            first_closer_str = str(first_closer) if first_closer != 'N/A' else 'N/A'
            print(f"{mult:^8.1f} | {first_closer_str:^13} | {basin:^6} | {traj_type:^20}")

        print()

        # Analyze oscillation
        print("="*80)
        print("OSCILLATION ANALYSIS")
        print("="*80)

        mult_sequence = [item['mult'] for item in sorted(mult_basin_map, key=lambda x: x['mult'])]
        basin_sequence = [item['basin'] for item in sorted(mult_basin_map, key=lambda x: x['mult'])]

        print(f"Mult sequence:  {mult_sequence}")
        print(f"Basin sequence: {basin_sequence}")
        print()

        # Check for transitions
        basin_changes = []
        for i in range(len(basin_sequence) - 1):
            if basin_sequence[i] != basin_sequence[i+1]:
                basin_changes.append({
                    'from_mult': mult_sequence[i],
                    'to_mult': mult_sequence[i+1],
                    'from_basin': basin_sequence[i],
                    'to_basin': basin_sequence[i+1]
                })

        if len(basin_changes) == 0:
            relationship_type = "CONSTANT"
            print(f"✓ Basin assignment is CONSTANT across all mult values")
            print(f"✓ All mult values → Basin {basin_sequence[0]}")
            insight_type = "mult_invariant"
        elif len(basin_changes) == 1:
            relationship_type = "CRITICAL TRANSITION"
            change = basin_changes[0]
            print(f"✓ CRITICAL TRANSITION detected:")
            print(f"  Mult ≤ {change['from_mult']}: Basin {change['from_basin']}")
            print(f"  Mult ≥ {change['to_mult']}: Basin {change['to_basin']}")
            insight_type = "critical_transition"
        else:
            relationship_type = "MULTIPLE TRANSITIONS"
            print(f"⚠️ MULTIPLE TRANSITIONS detected (OSCILLATING):")
            for change in basin_changes:
                print(f"  {change['from_mult']:.1f} → {change['to_mult']:.1f}: Basin {change['from_basin']} → {change['to_basin']}")
            insight_type = "oscillating"

        print()

        # Compare to spread results
        print("="*80)
        print("COMPARISON TO SPREAD DIMENSION")
        print("="*80)
        print("Spread dimension (C123-C125):")
        print("  - Oscillating pattern: B→B→B→B→A→A→B→A→A (9 values)")
        print("  - Multiple transitions: 3 (0.175→0.200, 0.225→0.250, 0.250→0.275)")
        print("  - Isolated Basin B at spread 0.25")
        print()
        print(f"Mult dimension (C126):")
        print(f"  - Pattern: {' → '.join(basin_sequence)} ({len(mult_sequence)} values)")
        print(f"  - Transitions: {len(basin_changes)}")
        if relationship_type == "MULTIPLE TRANSITIONS":
            print(f"  - ✓ OSCILLATING (similar to spread)")
        elif relationship_type == "CRITICAL TRANSITION":
            print(f"  - ⚠️ SINGLE TRANSITION (different from spread)")
        else:
            print(f"  - ⚠️ CONSTANT (different from spread)")

        print()
        print(f"📊 INSIGHT #83: Mult Parameter Investigation - {relationship_type}")
        print(f"   - Tested 7 mult values (0.5-1.5)")
        print(f"   - Relationship type: {relationship_type}")
        print(f"   - Insight type: {insight_type}")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        relationship_type = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "mult_parameter"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle126_mult_parameter.json"

    output_data = {
        'experiment': 'cycle126_mult_parameter',
        'threshold': threshold,
        'spread': spread,
        'mult_values': mult_values,
        'cycles': cycles,
        'results': results,
        'relationship_type': relationship_type if 'relationship_type' in locals() else None,
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
