#!/usr/bin/env python3
"""
Cycle 123: Spread Parameter Investigation - Understanding Basin Control

Research Context:
  C122: Basin Robustness Testing
  - Basin structure is PARAMETER-DEPENDENT (not fully robust)
  - Threshold 400: 25% maintained Basin A with parameter variations
  - Threshold 600: 75% maintained Basin B (more robust)
  - **KEY FINDING**: Low spread (0.1) → Basin B for BOTH thresholds (400 & 600)
  - Spread appears to control basin accessibility independently of threshold

Research Gap:
  C122 tested spread at two extreme values (0.1, 0.3) with ±50% from baseline
  Unknown at what spread value basin assignment transitions
  Unknown if spread-basin relationship is:
    1. **Binary**: Low spread → Basin B, high spread → Basin A
    2. **Gradual**: Smooth transition with critical spread value
    3. **Non-Monotonic**: Complex relationship (e.g., U-shaped, inverted-U)
    4. **Threshold-Dependent**: Spread effect varies by threshold

Key Question:
  How does spread parameter control basin assignment? Is there a critical
  spread value where basin selection transitions from Basin B to Basin A
  (or becomes threshold-dependent)?

Hypotheses to Test:
  1. **Critical Spread**: Single critical value where basin switches (e.g., 0.15-0.2)
  2. **Gradual Transition**: Progressive shift in basin probability across spread range
  3. **Spread Dominates**: At low spread, Basin B dominates regardless of threshold
  4. **Threshold Restoration**: At high spread, threshold controls basin (C111-C121 behavior restored)

Research Question:
  Systematically vary spread (0.05-0.3) at fixed threshold to characterize
  spread-basin relationship and identify critical transition point.

Test Conditions:
  **THRESHOLD**: 400 (representative of Basin A at baseline)
    - Expected Basin A at baseline (mult=1.0, spread=0.2)
    - C122: Switched to Basin B at spread=0.1
    - Question: At what spread does it switch back to Basin A?

  **MULT**: 1.0 (baseline, fixed)
    - Isolate spread effect by holding mult constant

  **SPREAD SWEEP**: 0.05, 0.1, 0.15, 0.2 (baseline), 0.25, 0.3
    - 6 values spanning C122 tested range
    - Includes baseline (0.2) for comparison
    - Fine-grained to detect critical transition

  **FIXED**: agent_cap=15, cycles=5000

Metrics:
  - Final pattern coordinates (basin assignment A vs B vs NEW)
  - Pattern distance to Basin A and Basin B centers
  - Basin assignment as function of spread
  - Critical spread value (where assignment changes)

Expected Outcome:
  - If critical spread → identify exact transition point (e.g., 0.15 < critical < 0.2)
  - If gradual → characterize transition function (linear, sigmoid, etc.)
  - If spread dominates → low spread always → Basin B
  - If threshold restored → high spread → Basin A (C111-C121 behavior)

Publication Value:
  - **HIGH**: Identifies spread as independent control parameter for basin selection
  - **Novel**: First systematic characterization of spread-basin relationship
  - **Complete**: Fills gap from C122 discovery (why does low spread favor Basin B?)
  - **Engineering**: Enables basin control via spread parameter (alternative to threshold)
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

def run_spread_sweep(threshold, mult, spread, cycles, agent_cap=15):
    """Run experiment with specified spread to characterize spread-basin relationship."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
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
    print("CYCLE 123: SPREAD PARAMETER INVESTIGATION")
    print("="*80)
    print()
    print("Understanding how spread parameter controls basin assignment")
    print()
    print("C122 Discovery:")
    print("  - Low spread (0.1) → Basin B for BOTH thresholds (400 & 600)")
    print("  - High spread (0.3) → Varied basin assignments (threshold-dependent)")
    print("  - Spread appears to control basin accessibility independently")
    print()
    print("Research Question: At what spread value does basin assignment transition?")
    print()
    print("Test Approach:")
    print("  - Fixed threshold: 400 (Basin A at baseline)")
    print("  - Fixed mult: 1.0 (baseline)")
    print("  - Spread sweep: 0.05, 0.1, 0.15, 0.2 (baseline), 0.25, 0.3")
    print("  - Identify critical spread where basin switches")
    print()

    cycles = 5000
    agent_cap = 15
    threshold = 400  # Representative of Basin A at baseline
    mult = 1.0  # Baseline

    # Spread sweep (fine-grained around baseline 0.2)
    spread_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]

    print(f"Configuration:")
    print(f"  Fixed threshold: {threshold}")
    print(f"  Fixed mult: {mult}")
    print(f"  Spread values: {spread_values}")
    print(f"  Total experiments: {len(spread_values)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(spread_values) * cycles:,}")
    print(f"  Estimated duration: ~{len(spread_values) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, spread in enumerate(spread_values):
        print(f"\n[{i+1}/{len(spread_values)}] SPREAD = {spread}")
        print("-" * 80)

        try:
            result = run_spread_sweep(threshold, mult, spread, cycles, agent_cap)
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
    print(f"SPREAD PARAMETER ANALYSIS")
    print(f"{'='*80}\n")

    # Define basins from C119-C121
    basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
    basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

    if len(successful) >= 1:
        print("Basin Assignment by Spread:")
        print(f"{'Spread':^8} | {'Final Pattern':^40} | {'Basin':^6} | {'Dist A':^8} | {'Dist B':^8}")
        print("-" * 95)

        spread_basin_map = []

        for r in successful:
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

                spread_basin_map.append({'spread': spread, 'basin': basin, 'dist_A': dist_A, 'dist_B': dist_B})

                pattern_str = f"({pattern[0]:.3f}, {pattern[1]:.3f}, {pattern[2]:.3f})"
                print(f"{spread:^8.2f} | {pattern_str:^40} | {basin:^6} | {dist_A:^8.4f} | {dist_B:^8.4f}")

        print()

        # Analyze spread-basin relationship
        print("="*80)
        print("SPREAD-BASIN RELATIONSHIP")
        print("="*80)

        basin_sequence = [item['basin'] for item in sorted(spread_basin_map, key=lambda x: x['spread'])]
        spread_sequence = [item['spread'] for item in sorted(spread_basin_map, key=lambda x: x['spread'])]

        print(f"Spread sequence: {spread_sequence}")
        print(f"Basin sequence:  {basin_sequence}")
        print()

        # Check for critical transition
        basin_changes = []
        for i in range(len(basin_sequence) - 1):
            if basin_sequence[i] != basin_sequence[i+1]:
                basin_changes.append({
                    'from_spread': spread_sequence[i],
                    'to_spread': spread_sequence[i+1],
                    'from_basin': basin_sequence[i],
                    'to_basin': basin_sequence[i+1]
                })

        if len(basin_changes) == 0:
            relationship_type = "CONSTANT"
            print(f"✓ Basin assignment is CONSTANT across all spread values")
            print(f"✓ All spread values → Basin {basin_sequence[0]}")
            insight_type = "spread_invariant"
        elif len(basin_changes) == 1:
            relationship_type = "CRITICAL TRANSITION"
            change = basin_changes[0]
            critical_lower = change['from_spread']
            critical_upper = change['to_spread']
            print(f"✓ CRITICAL TRANSITION detected:")
            print(f"  Spread ≤ {critical_lower}: Basin {change['from_basin']}")
            print(f"  Spread ≥ {critical_upper}: Basin {change['to_basin']}")
            print(f"  Critical range: {critical_lower} < spread < {critical_upper}")
            insight_type = "critical_transition"
        else:
            relationship_type = "MULTIPLE TRANSITIONS"
            print(f"⚠️ MULTIPLE TRANSITIONS detected:")
            for change in basin_changes:
                print(f"  {change['from_spread']:.2f} → {change['to_spread']:.2f}: Basin {change['from_basin']} → {change['to_basin']}")
            insight_type = "complex_relationship"

        print()

        # Check baseline (spread=0.2) behavior
        baseline_result = next((item for item in spread_basin_map if item['spread'] == 0.2), None)
        if baseline_result:
            baseline_basin = baseline_result['basin']
            expected_basin = 'A'  # Threshold 400 expected Basin A at baseline
            if baseline_basin == expected_basin:
                print(f"✓ Baseline (spread=0.2) matches C111-C121 expectation: Basin {baseline_basin}")
            else:
                print(f"⚠️ Baseline (spread=0.2) DIFFERS from C111-C121: Expected Basin {expected_basin}, got Basin {baseline_basin}")

        print()
        print(f"📊 INSIGHT #80: Spread Parameter Investigation - {relationship_type}")
        print(f"   - Tested 6 spread values (0.05-0.3) at threshold 400")
        print(f"   - Relationship type: {relationship_type}")
        print(f"   - Insight type: {insight_type}")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        relationship_type = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "spread_parameter"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle123_spread_parameter.json"

    output_data = {
        'experiment': 'cycle123_spread_parameter_investigation',
        'threshold': threshold,
        'mult': mult,
        'spread_values': spread_values,
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
