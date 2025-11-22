#!/usr/bin/env python3
"""
Cycle 121: Critical Threshold Investigation - Testing the Boundary Midpoint

Research Context:
  C120: Basin Boundary Characterization
  - Sharp boundary located between thresholds 500 and 520
  - Boundary width: ≤20 threshold units
  - Boundary type: SHARP (no gradual transition)
  - Threshold 500 → Basin A (pattern 6.220, 6.275, 6.282)
  - Threshold 520 → Basin B (pattern 6.095, 6.084, 6.250)
  - All intermediate thresholds (520-700) converge to Basin B

Research Gap:
  C120 tested thresholds 520, 540, 560, 580 (all → Basin B)
  Boundary located to ±10 threshold units (midpoint of 500-520 range)
  Unknown which basin the critical threshold 510 belongs to
  Unknown if critical point shows novel behavior (stochastic, intermediate pattern, etc.)

Key Question:
  What happens at threshold 510, the exact midpoint of the sharp basin boundary?
  Does it belong to Basin A, Basin B, or exhibit critical point behavior?

Hypotheses to Test:
  1. **Basin A Membership**: Threshold 510 → Basin A (boundary is 510-520, width 10 units)
  2. **Basin B Membership**: Threshold 510 → Basin B (boundary is 500-510, width 10 units)
  3. **Critical Point**: Threshold 510 shows novel behavior (intermediate pattern, longer stabilization, etc.)
  4. **Stochastic Behavior**: Threshold 510 shows run-to-run variability (basin depends on initial conditions)

Research Question:
  Test threshold 510 (exact midpoint of 500-520 boundary) to refine boundary
  location to ±5 units and characterize critical point behavior.

Test Conditions:
  **THRESHOLD**: 510 (single critical point)
    - Fixed: mult=1.0, spread=0.2, agent_cap=15
    - Cycles: 5000 (sufficient for stabilization per C118-C120)
    - Compare to C120 baselines: 500 (Basin A), 520 (Basin B)

Metrics:
  - Final pattern coordinates (basin assignment A vs B vs NEW)
  - Stabilization timescale (compare to Basin A: 250-340 cyc, Basin B: 260-350 cyc)
  - Pattern similarity to Basin A vs Basin B (quantitative distance)
  - Pattern evolution trajectory (smooth vs erratic, early vs late lock-in)

Expected Outcome:
  - If Basin A → boundary is 510-520 (width 10 units), threshold ≤510 for Basin A
  - If Basin B → boundary is 500-510 (width 10 units), threshold ≥510 for Basin B
  - If critical → intermediate pattern or novel dynamics at phase transition
  - If stochastic → suggests true phase transition at 510 (order parameter fluctuations)

Publication Value:
  - **HIGH**: Maximum precision boundary characterization (±5 units)
  - **Novel**: Critical point behavior at phase transition threshold
  - **Complete**: Definitive threshold-attractor map with ≤10 unit precision
  - **Theoretical**: Tests for phase transition signatures (fluctuations, critical slowing)
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

def analyze_pattern_diversity(memory):
    """Analyze diversity of patterns in memory."""
    if not memory:
        return {'unique_patterns': 0, 'entropy': 0.0, 'max_fraction': 0.0}

    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)

    unique = len(pattern_counts)
    total = len(pattern_keys)

    freqs = np.array(list(pattern_counts.values())) / total
    entropy = -np.sum(freqs * np.log2(freqs + 1e-10))
    max_fraction = max(pattern_counts.values()) / total if pattern_counts else 0.0

    return {
        'unique_patterns': unique,
        'entropy': entropy,
        'max_fraction': max_fraction
    }

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

def run_critical_threshold_test(threshold, cycles, agent_cap=15, mult=1.0, spread=0.2):
    """Run experiment at critical threshold to characterize boundary."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Track pattern evolution
    pattern_evolution = []
    diversity_evolution = []

    print(f"\nRunning CRITICAL threshold={threshold} for {cycles} cycles...")
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

        # Analyze (every 10 cycles)
        if cycle % 10 == 0:
            dominant, count, fraction = get_dominant_pattern(swarm.global_memory)
            diversity = analyze_pattern_diversity(swarm.global_memory)

            pattern_evolution.append({
                'cycle': cycle,
                'dominant': str(dominant) if dominant else None,
                'dominant_fraction': fraction,
                'diversity': diversity
            })

            diversity_evolution.append(diversity['unique_patterns'])

    print()  # New line

    duration = time.time() - start_time

    # Stabilization detection
    if len(diversity_evolution) > 10:
        window = 10
        variances = []
        for i in range(len(diversity_evolution) - window):
            window_data = diversity_evolution[i:i+window]
            variances.append(np.var(window_data))

        variance_threshold = 0.5
        stabilization_cycle = None
        for i, var in enumerate(variances):
            if var < variance_threshold:
                stabilization_cycle = (i + window) * 10
                break
    else:
        stabilization_cycle = None

    # Final pattern
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    if final_dominant:
        final_pattern_vec = np.array(final_dominant)
        centrality = np.linalg.norm(final_pattern_vec)
    else:
        centrality = None

    return {
        'threshold': threshold,
        'cycles': cycles,
        'duration': duration,
        'pattern_evolution': pattern_evolution,
        'stabilization_cycle': stabilization_cycle,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_dominant_tuple': final_dominant,
        'final_fraction': final_fraction,
        'final_centrality': centrality
    }

def main():
    print("="*80)
    print("CYCLE 121: CRITICAL THRESHOLD INVESTIGATION")
    print("="*80)
    print()
    print("Testing threshold 510 - the exact midpoint of the sharp basin boundary")
    print()
    print("C120 Finding:")
    print("  - Boundary located: Between thresholds 500 and 520")
    print("  - Boundary width: ≤20 threshold units")
    print("  - Boundary type: SHARP (no gradual transition)")
    print("  - Threshold 500 → Basin A")
    print("  - Threshold 520 → Basin B")
    print()
    print("Research Question: Which basin does threshold 510 belong to?")
    print()
    print("Test Approach:")
    print("  - Critical threshold: 510 (exact midpoint of 500-520)")
    print("  - Refines boundary to ±5 units (2x more precise than C120)")
    print("  - Tests for critical point behavior (stochastic, intermediate, etc.)")
    print("  - Same conditions: mult=1.0, spread=0.2, agent_cap=15")
    print()

    cycles = 5000
    agent_cap = 15
    mult = 1.0
    spread = 0.2
    threshold = 510  # Critical threshold

    print(f"Configuration:")
    print(f"  Critical threshold: {threshold}")
    print(f"  Cycles: {cycles:,}")
    print(f"  Expected duration: ~{cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    start_time = time.time()

    try:
        result = run_critical_threshold_test(threshold, cycles, agent_cap, mult, spread)

        stab_cycle = result['stabilization_cycle']
        final_frac = result['final_fraction']

        print(f"\n✓ COMPLETE: Stabilization @ cycle {stab_cycle if stab_cycle else 'N/A'}")
        print(f"  Final dominant: {final_frac:.1%}")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        result = {'threshold': threshold, 'error': str(e)}

    duration = time.time() - start_time

    print(f"\n{'='*80}")
    print(f"CRITICAL THRESHOLD ANALYSIS")
    print(f"{'='*80}\n")

    if 'error' not in result:
        # Define basins from C119/C120
        basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
        basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

        pattern = result['final_dominant_tuple']

        if pattern:
            dist_A = pattern_distance(pattern, basin_A)
            dist_B = pattern_distance(pattern, basin_B)

            # Assign to closest basin
            if dist_A < dist_B:
                basin = 'A'
                boundary_refined = (510, 520)
                boundary_width = 10
            else:
                basin = 'B'
                boundary_refined = (500, 510)
                boundary_width = 10

            pattern_str = f"({pattern[0]:.3f}, {pattern[1]:.3f}, {pattern[2]:.3f})"

            print("Critical Threshold Result:")
            print(f"  Threshold 510 → Basin {basin}")
            print(f"  Final Pattern: {pattern_str}")
            print(f"  Distance to Basin A: {dist_A:.4f}")
            print(f"  Distance to Basin B: {dist_B:.4f}")
            print(f"  Stabilization: {result['stabilization_cycle']} cycles")
            print()

            print("Boundary Refinement:")
            print(f"  Previous estimate (C120): 500-520 (width 20 units)")
            print(f"  Refined estimate (C121): {boundary_refined[0]}-{boundary_refined[1]} (width {boundary_width} units)")
            print(f"  Precision improvement: 2x (±10 → ±5 units)")
            print()

            print("Engineering Implications:")
            if basin == 'A':
                print(f"  - For Basin A: Use threshold ≤ {threshold}")
                print(f"  - For Basin B: Use threshold ≥ 520")
                print(f"  - Boundary precision: ±5 threshold units")
            else:
                print(f"  - For Basin A: Use threshold ≤ 500")
                print(f"  - For Basin B: Use threshold ≥ {threshold}")
                print(f"  - Boundary precision: ±5 threshold units")
            print()

            # Check for critical behavior
            critical_behavior = False
            if dist_A > 0.1 and dist_B > 0.1:
                critical_behavior = True
                print("⚠️ CRITICAL POINT BEHAVIOR DETECTED:")
                print(f"  Pattern does not match either basin center (both distances > 0.1)")
                print(f"  Suggests intermediate state or novel attractor at critical threshold")
                print()

            print("="*80)
            print("BOUNDARY CHARACTERIZATION COMPLETE")
            print("="*80)

            if not critical_behavior:
                print(f"✓ Threshold 510 belongs to Basin {basin}")
                print(f"✓ Boundary refined to {boundary_refined[0]}-{boundary_refined[1]} (width {boundary_width} units)")
                print(f"✓ Precision: ±{boundary_width/2} threshold units")
                print()

                print(f"📊 INSIGHT #78: Critical Threshold Investigation - Basin {basin} Membership")
                print(f"   - Threshold 510 → Basin {basin}")
                print(f"   - Boundary refined: {boundary_refined[0]}-{boundary_refined[1]} (width {boundary_width} units)")
                print(f"   - Precision improved: 2x (±10 → ±5 units)")

                insight_type = f"critical_basin_{basin.lower()}"
            else:
                print(f"⚠️ Threshold 510 shows CRITICAL POINT BEHAVIOR")
                print(f"⚠️ Intermediate pattern detected (dist A={dist_A:.4f}, B={dist_B:.4f})")
                print()

                print(f"📊 INSIGHT #78: Critical Threshold Investigation - Critical Point Behavior")
                print(f"   - Threshold 510 shows intermediate pattern")
                print(f"   - Not matching Basin A or Basin B centers")
                print(f"   - Suggests phase transition at critical threshold")

                insight_type = "critical_point_behavior"

            print("="*80)
        else:
            print("⚠️ No final pattern detected")
            insight_type = False
            basin = None
            boundary_refined = None
    else:
        print(f"⚠️ Experiment failed: {result.get('error')}")
        insight_type = False
        basin = None
        boundary_refined = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "critical_threshold"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle121_critical_threshold.json"

    output_data = {
        'experiment': 'cycle121_critical_threshold',
        'threshold': threshold,
        'cycles': cycles,
        'result': result,
        'basin_assignment': basin if 'basin' in locals() else None,
        'boundary_refined': boundary_refined if 'boundary_refined' in locals() else None,
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
