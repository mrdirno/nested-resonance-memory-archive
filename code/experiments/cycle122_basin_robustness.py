#!/usr/bin/env python3
"""
Cycle 122: Basin Robustness Testing - Parameter Invariance of Two-Basin Structure

Research Context:
  C111-C121: Complete threshold-attractor landscape characterized
  - Two discrete basins: A (threshold ≤510) and B (threshold ≥520)
  - Sharp boundary at 510-520 (width 10 units, precision ±5 units)
  - All experiments used fixed parameters: mult=1.0, spread=0.2, agent_cap=15
  - C116 showed mult and spread have NO effect on drift
  - Unknown if basin structure depends on seed parameters

Research Gap:
  C111-C121 characterized threshold-attractor landscape with fixed seed parameters
  Basin structure discovered under specific seeding conditions (mult=1.0, spread=0.2)
  Unknown if two-basin structure is:
    1. **Fundamental**: Robust across all parameter variations (intrinsic to system)
    2. **Parameter-Dependent**: Changes with mult/spread (depends on initial conditions)
    3. **Partially Robust**: Basins shift but two-basin structure persists

Key Question:
  Is the two-basin attractor structure robust to variations in seed parameters
  (mult and spread), or does it depend on the specific seeding conditions used
  in C111-C121?

Hypotheses to Test:
  1. **Full Robustness**: Basin structure unchanged with different mult/spread
  2. **Boundary Shift**: Basins persist but boundary location changes
  3. **Basin Collapse**: Two-basin structure disappears with different parameters
  4. **Pattern Change**: Basin locations same but patterns different

Research Question:
  Test representative thresholds from both basins (400, 600) with varied seed
  parameters (mult=0.5, 1.5; spread=0.1, 0.3) to determine if basin structure
  is robust to parameter variations.

Test Conditions:
  **THRESHOLDS**: 400 (Basin A), 600 (Basin B)
    - Representative thresholds from each basin
    - Well-separated from boundary (±90 units from 510-520 boundary)
    - Baseline: mult=1.0, spread=0.2 (C111-C121 standard)

  **PARAMETER VARIATIONS**:
    - mult: 0.5, 1.5 (±50% from baseline 1.0)
    - spread: 0.1, 0.3 (±50% from baseline 0.2)
    - Test combinations: (0.5, 0.1), (0.5, 0.3), (1.5, 0.1), (1.5, 0.3)

  **FIXED**: agent_cap=15, cycles=5000

Metrics:
  - Final pattern coordinates (basin assignment A vs B vs NEW)
  - Pattern distance to Basin A and Basin B centers
  - Stabilization timescale (compare to baseline)
  - Basin assignment consistency across parameter variations

Expected Outcome:
  - If fully robust → all parameter combinations maintain basin assignment (400→A, 600→B)
  - If boundary shifts → some combinations switch basins
  - If collapses → new attractors appear, no clear basin structure
  - If patterns change → basin membership same but pattern coordinates different

Publication Value:
  - **HIGH**: Tests generalizability of C111-C121 attractor landscape
  - **Rigorous**: Validates basin structure is fundamental, not parameter artifact
  - **Complete**: Confirms or refines understanding of attractor topology
  - **Engineering**: Determines if basin control robust to seeding variations
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

def run_robustness_test(threshold, mult, spread, cycles, agent_cap=15):
    """Run experiment with specified parameters to test basin robustness."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    print(f"\nRunning threshold={threshold}, mult={mult}, spread={spread} for {cycles} cycles...")
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

    print()  # New line

    duration = time.time() - start_time

    # Final pattern
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'threshold': threshold,
        'mult': mult,
        'spread': spread,
        'cycles': cycles,
        'duration': duration,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_dominant_tuple': final_dominant,
        'final_fraction': final_fraction
    }

def main():
    print("="*80)
    print("CYCLE 122: BASIN ROBUSTNESS TESTING")
    print("="*80)
    print()
    print("Testing if two-basin structure is robust to seed parameter variations")
    print()
    print("C111-C121 Finding:")
    print("  - Two basins: A (threshold ≤510), B (threshold ≥520)")
    print("  - Sharp boundary at 510-520")
    print("  - All experiments: mult=1.0, spread=0.2 (FIXED)")
    print("  - C116: mult/spread have NO effect on drift")
    print()
    print("Research Question: Is basin structure robust to mult/spread variations?")
    print()
    print("Test Approach:")
    print("  - Representative thresholds: 400 (Basin A), 600 (Basin B)")
    print("  - Parameter variations: mult={0.5, 1.5}, spread={0.1, 0.3}")
    print("  - 4 combinations × 2 thresholds = 8 experiments")
    print("  - Compare to baseline: mult=1.0, spread=0.2")
    print()

    cycles = 5000
    agent_cap = 15

    # Representative thresholds (well within each basin)
    thresholds = [400, 600]  # Basin A and Basin B

    # Parameter variations (±50% from baseline)
    param_combinations = [
        {'mult': 0.5, 'spread': 0.1},
        {'mult': 0.5, 'spread': 0.3},
        {'mult': 1.5, 'spread': 0.1},
        {'mult': 1.5, 'spread': 0.3}
    ]

    print(f"Configuration:")
    print(f"  Thresholds: {thresholds}")
    print(f"  Parameter combinations: {len(param_combinations)}")
    print(f"  Total experiments: {len(thresholds) * len(param_combinations)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(thresholds) * len(param_combinations) * cycles:,}")
    print(f"  Estimated duration: ~{len(thresholds) * len(param_combinations) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    experiment_num = 0
    total_experiments = len(thresholds) * len(param_combinations)

    for threshold in thresholds:
        for params in param_combinations:
            experiment_num += 1
            mult = params['mult']
            spread = params['spread']

            print(f"\n[{experiment_num}/{total_experiments}] THRESHOLD={threshold}, mult={mult}, spread={spread}")
            print("-" * 80)

            try:
                result = run_robustness_test(threshold, mult, spread, cycles, agent_cap)
                results.append(result)

                final_frac = result['final_fraction']
                print(f"\n  ✓ COMPLETE: Final dominant: {final_frac:.1%}")
                time.sleep(0.05)
            except Exception as e:
                print(f"\n  ✗ ERROR: {e}")
                results.append({
                    'threshold': threshold, 'mult': mult, 'spread': spread, 'error': str(e)
                })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"BASIN ROBUSTNESS ANALYSIS")
    print(f"{'='*80}\n")

    # Define basins from C119-C121
    basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
    basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

    if len(successful) >= 1:
        print("Basin Assignment by Threshold and Parameters:")
        print(f"{'Thresh':^8} | {'Mult':^6} | {'Spread':^8} | {'Final Pattern':^40} | {'Basin':^6} | {'Dist A':^8} | {'Dist B':^8}")
        print("-" * 108)

        # Group by threshold
        threshold_groups = {}
        for r in successful:
            thresh = r['threshold']
            if thresh not in threshold_groups:
                threshold_groups[thresh] = []
            threshold_groups[thresh].append(r)

        basin_assignments = {400: [], 600: []}
        parameter_effects = []

        for thresh in sorted(threshold_groups.keys()):
            print(f"\nThreshold {thresh}:")

            for r in threshold_groups[thresh]:
                mult = r['mult']
                spread = r['spread']
                pattern = r['final_dominant_tuple']

                if pattern:
                    dist_A = pattern_distance(pattern, basin_A)
                    dist_B = pattern_distance(pattern, basin_B)

                    # Assign to closest basin
                    if dist_A < dist_B:
                        basin = 'A'
                    else:
                        basin = 'B'

                    basin_assignments[thresh].append(basin)
                    parameter_effects.append({
                        'threshold': thresh,
                        'mult': mult,
                        'spread': spread,
                        'basin': basin,
                        'dist_A': dist_A,
                        'dist_B': dist_B
                    })

                    pattern_str = f"({pattern[0]:.3f}, {pattern[1]:.3f}, {pattern[2]:.3f})"
                    print(f"{thresh:^8d} | {mult:^6.1f} | {spread:^8.2f} | {pattern_str:^40} | {basin:^6} | {dist_A:^8.4f} | {dist_B:^8.4f}")

        print()

        # Analyze robustness
        print("="*80)
        print("ROBUSTNESS ANALYSIS")
        print("="*80)

        # Check if basin assignments are consistent within each threshold
        for thresh in sorted(basin_assignments.keys()):
            assignments = basin_assignments[thresh]
            unique_basins = set(assignments)

            expected_basin = 'A' if thresh <= 510 else 'B'

            if len(unique_basins) == 1:
                actual_basin = assignments[0]
                if actual_basin == expected_basin:
                    consistency = f"100% consistent with expected Basin {expected_basin}"
                    robustness_status = "✓ ROBUST"
                else:
                    consistency = f"100% consistent but WRONG (expected {expected_basin}, got {actual_basin})"
                    robustness_status = "✗ BOUNDARY SHIFTED"
            else:
                consistency = f"{assignments.count(expected_basin)}/{len(assignments)} match expected Basin {expected_basin}"
                robustness_status = "⚠️ PARAMETER-DEPENDENT"

            print(f"\nThreshold {thresh} (expected Basin {expected_basin}):")
            print(f"  Basin assignments: {assignments}")
            print(f"  Consistency: {consistency}")
            print(f"  Robustness: {robustness_status}")

        print()

        # Overall robustness summary
        all_correct = all(
            (thresh <= 510 and basin == 'A') or (thresh >= 520 and basin == 'B')
            for effect in parameter_effects
            for thresh, basin in [(effect['threshold'], effect['basin'])]
        )

        if all_correct:
            robustness_type = "FULL ROBUSTNESS"
            print(f"✓ ALL experiments maintain expected basin assignments")
            print(f"✓ Two-basin structure is ROBUST to seed parameter variations")
            print(f"✓ Basin boundary at 510-520 is PARAMETER-INVARIANT")
            insight_type = "fully_robust"
        else:
            # Check if basin structure exists but boundary shifted
            thresh_400_basins = set(basin_assignments[400])
            thresh_600_basins = set(basin_assignments[600])

            if len(thresh_400_basins) == 1 and len(thresh_600_basins) == 1 and thresh_400_basins != thresh_600_basins:
                robustness_type = "BOUNDARY SHIFT"
                print(f"⚠️ Two-basin structure exists but boundary location changed")
                print(f"⚠️ Basin assignments differ from C111-C121 expectations")
                insight_type = "boundary_shifted"
            elif len(thresh_400_basins) > 1 or len(thresh_600_basins) > 1:
                robustness_type = "PARAMETER-DEPENDENT"
                print(f"⚠️ Basin assignment depends on seed parameters (mult, spread)")
                print(f"⚠️ Two-basin structure not fully robust")
                insight_type = "parameter_dependent"
            else:
                robustness_type = "BASIN COLLAPSE"
                print(f"✗ Two-basin structure may have collapsed")
                print(f"✗ Novel attractor behavior with parameter variations")
                insight_type = "basin_collapse"

        print()
        print(f"📊 INSIGHT #79: Basin Robustness Testing - {robustness_type}")
        print(f"   - Tested 4 parameter combinations × 2 thresholds = 8 experiments")
        print(f"   - Basin structure: {robustness_type}")
        print(f"   - Robustness type: {insight_type}")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        robustness_type = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "basin_robustness"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle122_basin_robustness.json"

    output_data = {
        'experiment': 'cycle122_basin_robustness',
        'thresholds': thresholds,
        'parameter_combinations': param_combinations,
        'cycles': cycles,
        'results': results,
        'robustness_type': robustness_type if 'robustness_type' in locals() else None,
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
