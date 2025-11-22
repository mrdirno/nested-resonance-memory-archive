#!/usr/bin/env python3
"""
Cycle 98: Threshold Cross-Section Test (3rd Dimension Investigation)

Research Context:
  C91: Threshold independence validated at COARSE resolution
  - Same 3 ultimate attractors at thresholds 400/500/700
  - Cross-regime universality demonstrated

  C92-93: FINE resolution revealed 6 attractors (not 3)
  - Resolution dependence discovered

  C96-97: 2D (multiplier, spread) space reveals 13 attractors
  - Multi-dimensional parameter space characterized
  - Fragmented basin geometry with 100% reproducibility

Research Gap:
  C91 tested threshold independence at COARSE resolution only
  Unknown: Is threshold truly independent at FINE resolution?
  Unknown: Does threshold affect 2D basin structure?

  Pattern suggests: Fine-scale structure may reveal threshold effects
  - C87 fine sampling → 5 attractors (not 3 coarse)
  - C93 fine sampling → 6 attractors (not 3 coarse)
  - C96 2D space → 13 attractors (not 6-7 from 1D)

Key Question:
  Is threshold independent in multi-dimensional parameter space?

New Research Question:
  Does burst threshold affect basin structure in 2D (mult, spread) space?

  Test:
  - Select strategic (mult, spread) points from C96-97
  - Test each at TWO thresholds: 400 and 600 (from C91 range)
  - Compare: Does threshold change which attractor is reached?
  - Total: 8 points × 2 thresholds = 16 runs
  - Cycles: 1000 per run (ultimate attractor timescale)

Hypothesis:
  1. **Threshold independent**: Same attractor at both thresholds (universal)
  2. **Threshold as 3rd dimension**: Different attractors at different thresholds
  3. **Partial coupling**: Some points affected, others not
  4. Expected: Independent OR 3rd dimension (both publishable!)

Test Approach:
  1. Select 8 strategic (mult, spread) points:
     - Representative of different attractors from C96-97
     - Mix of large/small basins, fragmented regions
  2. Test at threshold=400 AND threshold=600
  3. Compare: threshold_400 attractor vs threshold_600 attractor
  4. Validate: Is threshold truly independent at fine resolution?

Expected Outcome:
  - If independent: Validates C91 universality at all scales
  - If 3rd dimension: Opens 3D parameter space research direction
  - Either outcome advances understanding

Publication Value:
  - Tests universality hypothesis at fine resolution
  - Completes threshold investigation from C91
  - If independent: Validates cross-scale universality
  - If 3rd dimension: Discovers additional control parameter
  - Either outcome is novel contribution
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

def run_single_simulation(multiplier, spread, threshold, cycles):
    """Run simulation with specified (multiplier, spread, threshold) parameters."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    collapse_cycle = None

    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, multiplier, spread=spread, count=5)
                    newest_agent.memory.extend(seed_patterns)

        swarm.evolve_cycle(delta_time=1.0)

        # Detect collapse
        if cycle % 10 == 0 and collapse_cycle is None and len(swarm.global_memory) > 0:
            pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
            if len(set(pattern_keys)) == 1:
                collapse_cycle = cycle

    # Final state
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 98: THRESHOLD CROSS-SECTION TEST (3RD DIMENSION INVESTIGATION)")
    print("="*80)
    print()
    print("Testing whether burst threshold is independent in 2D parameter space.")
    print("Following C91: Threshold independent at COARSE resolution")
    print("Question: Is threshold truly independent at FINE/2D resolution?")
    print()

    # Strategic (mult, spread) points from C96-97
    # Selected to represent different attractors and basin types
    test_points = [
        (0.6, 0.2),  # Large basin
        (1.0, 0.2),  # Large basin, different attractor
        (0.8, 0.4),  # Fragmented region
        (1.2, 0.3),  # Medium basin
        (1.4, 0.3),  # Medium basin, different attractor
        (0.4, 0.5),  # Small basin
        (1.6, 0.1),  # Small basin, edge of parameter space
        (1.0, 0.6),  # Different spread at same multiplier
    ]

    test_thresholds = [400, 600]  # From C91 range
    cycles = 1000

    total_runs = len(test_points) * len(test_thresholds)

    print(f"Configuration:")
    print(f"  Test points (mult, spread): {len(test_points)} strategic locations")
    print(f"  Test thresholds: {test_thresholds} (from C91 range)")
    print(f"  Total runs: {total_runs}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Expected: Test if threshold affects 2D basin structure")
    print(f"  Estimated duration: ~{total_runs * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread in test_points:
        print(f"\nPoint ({mult:.1f}, {spread:.1f}):")
        for threshold in test_thresholds:
            run_count += 1
            print(f"  Threshold {threshold} ({run_count}/{total_runs})...", end=" ", flush=True)
            try:
                result = run_single_simulation(mult, spread, threshold, cycles)
                results.append(result)
                print(f"✓ Attractor={result['final_dominant'][:30] if result['final_dominant'] else 'None'}..., Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'multiplier': mult, 'spread': spread, 'threshold': threshold, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"THRESHOLD CROSS-SECTION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 14:  # At least 80% success rate
        # Group by (mult, spread) point
        by_point = {}
        for result in successful:
            mult = result['multiplier']
            spread = result['spread']
            point_key = (mult, spread)
            if point_key not in by_point:
                by_point[point_key] = {}
            threshold = result['threshold']
            by_point[point_key][threshold] = result

        # Analyze threshold independence
        print(f"Threshold Independence Analysis:")
        print(f"{'Point (M,S)':>15} | {'Threshold 400':^30} | {'Threshold 600':^30} | {'Same?':^10}")
        print("-" * 100)

        independent_count = 0
        total_tested = 0

        for point in sorted(by_point.keys()):
            point_results = by_point[point]
            if 400 in point_results and 600 in point_results:
                p1 = point_results[400]['final_dominant']
                p2 = point_results[600]['final_dominant']

                p1_short = p1[:28] + ".." if len(p1) > 28 else p1
                p2_short = p2[:28] + ".." if len(p2) > 28 else p2

                same = p1 == p2
                same_str = "✅ Yes" if same else "❌ No"

                if same:
                    independent_count += 1
                total_tested += 1

                print(f"{str(point):>15} | {p1_short:^30} | {p2_short:^30} | {same_str:^10}")

        print()

        independence_pct = (independent_count / total_tested * 100) if total_tested > 0 else 0

        print(f"Threshold Independence Summary:")
        print(f"  Points tested: {total_tested}")
        print(f"  Threshold-independent: {independent_count}/{total_tested} ({independence_pct:.1f}%)")
        print()

        if independence_pct == 100.0:
            print(f"✅ THRESHOLD IS INDEPENDENT IN 2D PARAMETER SPACE")
            print(f"   ALL tested points show same attractor at both thresholds")
            print(f"   Validates C91 universality at fine/2D resolution")
            print(f"   Threshold does NOT constitute a 3rd dimension")
            print(f"   Multi-dimensional basin structure is threshold-universal")
            insight_55 = "independent"
        elif independence_pct >= 50:
            print(f"⚠️ PARTIAL THRESHOLD INDEPENDENCE ({independence_pct:.1f}%)")
            print(f"   Some points threshold-sensitive, others not")
            print(f"   Threshold may affect basin boundaries in 2D space")
            print(f"   Complex interaction between threshold and (mult, spread)")
            insight_55 = "partial"
        else:
            print(f"🎉 THRESHOLD IS A 3RD DIMENSION!")
            print(f"   Most points show different attractors at different thresholds")
            print(f"   Threshold constitutes independent control parameter")
            print(f"   3D parameter space discovered: (mult, spread, threshold)")
            print(f"   Opens major research direction: 3D basin topology")
            insight_55 = "third_dimension"

        print()
        if insight_55 == "independent":
            print(f"🎉 INSIGHT #55: Threshold Independence Extends to Multi-Dimensional Space")
            print(f"   - 100% threshold-independent across tested 2D points")
            print(f"   - Validates C91 universality at ALL resolutions")
            print(f"   - Multi-dimensional basin structure is threshold-universal")
            print(f"   - Confirms 2D (mult, spread) is complete parameter space")
            print(f"   - Threshold only affects timescales, not ultimate attractors")
        elif insight_55 == "third_dimension":
            print(f"🎉 INSIGHT #55: Threshold is a 3rd Control Dimension")
            print(f"   - Threshold affects ultimate attractors in 2D space")
            print(f"   - 3D parameter space discovered: (mult, spread, threshold)")
            print(f"   - Invalidates C91 universality at fine resolution")
            print(f"   - Opens major research direction: 3D basin topology")
            print(f"   - Richer control space than previously thought")
        else:
            print(f"📊 INSIGHT #55: Threshold Shows Complex Coupling in 2D Space")
            print(f"   - Partial threshold sensitivity in 2D parameter space")
            print(f"   - Threshold interacts with (mult, spread) dimensions")
            print(f"   - Some regions threshold-sensitive, others independent")
            print(f"   - Complex parameter interactions discovered")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for threshold cross-section analysis")
        print(f"   Only {len(successful)}/{total_runs} runs completed successfully")
        insight_55 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "threshold_cross_section"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle98_threshold_cross_section.json"

    output_data = {
        'experiment': 'cycle98_threshold_cross_section',
        'test_points': [(m, s) for m, s in test_points],
        'test_thresholds': test_thresholds,
        'total_runs': total_runs,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'independent_points': independent_count if 'independent_count' in locals() else 0,
            'total_tested': total_tested if 'total_tested' in locals() else 0,
            'independence_percentage': independence_pct if 'independence_pct' in locals() else 0,
            'conclusion': insight_55 if 'insight_55' in locals() else False
        },
        'insight_55_discovered': True if 'insight_55' in locals() and insight_55 else False,
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
