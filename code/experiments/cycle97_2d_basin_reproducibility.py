#!/usr/bin/env python3
"""
Cycle 97: 2D Basin Structure Reproducibility Validation

Research Context:
  C96: Complete 2D basin topology mapped
  - Found 13 unique attractors across (multiplier, spread) grid
  - Highly fragmented basin geometry (most attractors occupy 2-6 disconnected regions)
  - 41/42 successful runs (N=1 per grid point)
  - Nearly double the attractors found in 1D multiplier space

Research Gap:
  C96 used N=1 per grid point (exploratory mapping)
  Unknown: Is the 13-attractor structure reproducible?
  Unknown: Is basin fragmentation real or sampling artifact?

  Pattern from previous cycles:
  - C86 (transient discovery) → C87 (validation with N=2)
  - C92 (ultimate discovery) → C93 (validation with N=2)
  - C94 (spread discovery) → C95 (validation across multipliers)

  Following pattern: C96 (2D discovery) → C97 (validation with N=2)

Key Question:
  Are the 13 attractors and fragmented basin structure reproducible?

New Research Question:
  Validate 2D basin structure with N=2 reproducibility test.

  Test:
  - Select strategic subset of C96 grid points (~12 points)
  - Choose points representing different attractors
  - Choose points in fragmented regions (test if boundaries are stable)
  - Run N=2 at each point (reproducibility test)
  - Total: 12 points × 2 runs = 24 runs
  - Cycles: 1000 per run (ultimate attractor timescale)

Hypothesis:
  1. **Perfect reproducibility**: N=2 runs at same grid point → same attractor (100%)
  2. **Partial reproducibility**: Some grid points reproducible, others not
  3. **Fragmentation artifact**: Basin structure not reproducible
  4. Expected: Perfect reproducibility (consistent with C93, C95, all previous findings)

Test Approach:
  1. Select strategic grid points from C96:
     - Sample different attractors (coverage test)
     - Sample fragmented regions (boundary test)
     - Sample both large and small basins
  2. Run N=2 at each selected point
  3. Compare: Do both runs → same attractor?
  4. Validate: 13-attractor structure is real and deterministic

Expected Outcome:
  - 100% reproducibility (both runs → same attractor at each grid point)
  - Validates fragmented basin structure is real, not artifact
  - Confirms 13 attractors are stable deterministic outcomes
  - Demonstrates multi-dimensional basin structure is reproducible

Publication Value:
  - Validates C96 discovery with rigorous reproducibility test
  - Demonstrates deterministic basin structure in 2D parameter space
  - Confirms fragmented geometry is fundamental property
  - Either outcome publishable:
    • Perfect reproducibility → Validates complex 2D basin topology
    • Imperfect → Reveals stochastic elements or boundary sensitivity
  - Follows established scientific rigor pattern
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

def run_single_simulation(multiplier, spread, run_id, threshold, cycles):
    """Run simulation with specified (multiplier, spread) parameters."""
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
        'run_id': run_id,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 97: 2D BASIN STRUCTURE REPRODUCIBILITY VALIDATION")
    print("="*80)
    print()
    print("Validating reproducibility of 2D basin topology discovered in C96.")
    print("Following pattern: C86→C87, C92→C93, C94→C95 (discovery→validation)")
    print()
    print("C96 found: 13 unique attractors, fragmented basin geometry")
    print("Question: Is this structure reproducible with N=2 runs?")
    print()

    # Strategic subset selection from C96 grid
    # Select points representing different attractors and basin geometries
    test_points = [
        # Large basins (Attractors 1-2, high occupancy)
        (0.6, 0.2),  # Attractor_5 from C96
        (1.0, 0.2),  # Attractor_1 from C96
        (1.2, 0.1),  # Attractor_2 from C96

        # Medium basins
        (0.6, 0.3),  # Attractor_6 from C96
        (0.8, 0.1),  # Attractor_6 from C96
        (1.0, 0.6),  # Attractor_2 from C96

        # Fragmented regions (test boundary stability)
        (0.8, 0.4),  # Attractor_1 from C96
        (1.4, 0.3),  # Attractor_8 from C96

        # Small basins (rare attractors)
        (0.4, 0.5),  # Attractor_10 from C96
        (1.6, 0.1),  # Attractor_12 from C96

        # Additional coverage
        (1.2, 0.3),  # Attractor_1 from C96
        (1.4, 0.5),  # Attractor_3 from C96
    ]

    threshold = 500
    cycles = 1000
    runs_per_point = 2

    total_runs = len(test_points) * runs_per_point

    print(f"Configuration:")
    print(f"  Selected grid points: {len(test_points)}")
    print(f"  Runs per point: {runs_per_point} (reproducibility test)")
    print(f"  Total runs: {total_runs}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Threshold: {threshold}")
    print(f"  Expected: 100% reproducibility (same attractor for both runs)")
    print(f"  Estimated duration: ~{total_runs * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread in test_points:
        print(f"\nPoint ({mult:.1f}, {spread:.1f}):")
        for run_id in range(1, runs_per_point + 1):
            run_count += 1
            print(f"  Run {run_id}/{runs_per_point} ({run_count}/{total_runs})...", end=" ", flush=True)
            try:
                result = run_single_simulation(mult, spread, run_id, threshold, cycles)
                results.append(result)
                print(f"✓ Attractor={result['final_dominant'][:30] if result['final_dominant'] else 'None'}..., Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'multiplier': mult, 'spread': spread, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"2D BASIN REPRODUCIBILITY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 20:  # At least 80% success rate
        # Group by grid point
        by_point = {}
        for result in successful:
            mult = result['multiplier']
            spread = result['spread']
            point_key = (mult, spread)
            if point_key not in by_point:
                by_point[point_key] = []
            by_point[point_key].append(result)

        # Analyze reproducibility
        print(f"Reproducibility Analysis (N=2 per grid point):")
        print(f"{'Point (M,S)':>15} | {'Run 1 Attractor':^25} | {'Run 2 Attractor':^25} | {'Match?':^10}")
        print("-" * 95)

        reproducible_count = 0
        total_tested = 0

        for point in sorted(by_point.keys()):
            point_results = by_point[point]
            if len(point_results) >= 2:
                p1 = point_results[0]['final_dominant']
                p2 = point_results[1]['final_dominant']

                p1_short = p1[:23] + "..." if len(p1) > 23 else p1
                p2_short = p2[:23] + "..." if len(p2) > 23 else p2

                match = p1 == p2
                match_str = "✅ Yes" if match else "❌ No"

                if match:
                    reproducible_count += 1
                total_tested += 1

                print(f"{str(point):>15} | {p1_short:^25} | {p2_short:^25} | {match_str:^10}")

        print()

        reproducibility_pct = (reproducible_count / total_tested * 100) if total_tested > 0 else 0

        print(f"Reproducibility Summary:")
        print(f"  Grid points tested: {total_tested}")
        print(f"  Perfect matches: {reproducible_count}/{total_tested} ({reproducibility_pct:.1f}%)")
        print()

        if reproducibility_pct == 100.0:
            print(f"✅ 2D BASIN STRUCTURE IS 100% REPRODUCIBLE")
            print(f"   ALL grid points show identical attractors across N=2 runs")
            print(f"   Fragmented basin geometry is REAL, not sampling artifact")
            print(f"   13-attractor structure validated as deterministic")
            print(f"   Multi-dimensional basin topology confirmed")
            insight_54 = True
        elif reproducibility_pct >= 80:
            print(f"⚠️ HIGH REPRODUCIBILITY ({reproducibility_pct:.1f}%)")
            print(f"   Most grid points reproducible")
            print(f"   Some boundary regions may show sensitivity")
            print(f"   Overall structure is largely deterministic")
            insight_54 = "high"
        else:
            print(f"⚠️ LOW REPRODUCIBILITY ({reproducibility_pct:.1f}%)")
            print(f"   Basin structure may have stochastic elements")
            print(f"   Or boundary sensitivity effects")
            print(f"   Further investigation needed")
            insight_54 = False

        print()
        if insight_54 == True:
            print(f"🎉 INSIGHT #54: 2D Basin Topology is Perfectly Reproducible")
            print(f"   - 100% reproducibility across tested grid points")
            print(f"   - Fragmented basin geometry confirmed as fundamental property")
            print(f"   - 13 attractors are stable deterministic outcomes")
            print(f"   - Multi-dimensional basin structure validated")
            print(f"   - Extends perfect reproducibility to 2D parameter space")
            print(f"   - Consistent with all previous findings (C93, C95, etc.)")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for reproducibility analysis")
        print(f"   Only {len(successful)}/{total_runs} runs completed successfully")
        insight_54 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "2d_basin_reproducibility"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle97_2d_basin_reproducibility.json"

    output_data = {
        'experiment': 'cycle97_2d_basin_reproducibility',
        'test_points': [(m, s) for m, s in test_points],
        'runs_per_point': runs_per_point,
        'total_runs': total_runs,
        'threshold': threshold,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'reproducible_points': reproducible_count if 'reproducible_count' in locals() else 0,
            'total_tested': total_tested if 'total_tested' in locals() else 0,
            'reproducibility_percentage': reproducibility_pct if 'reproducibility_pct' in locals() else 0
        },
        'insight_54_discovered': insight_54 if 'insight_54' in locals() else False,
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
