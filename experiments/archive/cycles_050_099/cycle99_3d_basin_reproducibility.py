#!/usr/bin/env python3
"""
Cycle 99: 3D Basin Reproducibility Validation

Research Context:
  C98: Threshold discovered as 3rd dimension
  - Only 14% threshold-independent (1/7 points)
  - 86% show different attractors at different thresholds
  - 3D parameter space: (multiplier, spread, threshold)

Research Gap:
  C98 used N=1 per (mult, spread, threshold) point
  Unknown: Is the 3D basin structure reproducible?
  Unknown: Does threshold dimension show same determinism as mult/spread?

  Pattern from previous cycles:
  - C96 (2D discovery) → C97 (2D validation with N=2, 100% reproducible)
  - C98 (3D discovery) → C99 (3D validation with N=2)

Key Question:
  Is the 3D (multiplier, spread, threshold) basin structure reproducible?

New Research Question:
  Validate 3D basin structure with N=2 reproducibility test.

  Test:
  - Select strategic subset of C98 points (~6 triplets)
  - Choose points that showed threshold sensitivity in C98
  - Run N=2 at each (mult, spread, threshold) triplet
  - Total: 6 triplets × 2 runs = 12 runs
  - Cycles: 1000 per run (ultimate attractor timescale)

Hypothesis:
  1. **Perfect reproducibility**: N=2 runs at same triplet → same attractor (100%)
  2. **Partial reproducibility**: Some triplets reproducible, others not
  3. **3D structure artifact**: Basin structure not reproducible
  4. Expected: Perfect reproducibility (consistent with C93, C95, C97)

Test Approach:
  1. Select 6 strategic (mult, spread, threshold) triplets from C98:
     - Points that showed threshold sensitivity
     - Mix of different (mult, spread) combinations
     - Both thresholds (400 and 600) represented
  2. Run N=2 at each triplet
  3. Compare: Do both runs → same attractor?
  4. Validate: 3D basin structure is deterministic

Expected Outcome:
  - 100% reproducibility (both runs → same attractor at each triplet)
  - Validates threshold dimension is as deterministic as mult/spread
  - Confirms 3D basin structure is real, not artifact
  - Extends perfect reproducibility to 3D parameter space

Publication Value:
  - Validates C98 discovery with rigorous reproducibility test
  - Demonstrates deterministic 3D basin structure
  - Extends reproducibility to full 3D parameter space
  - Either outcome publishable:
    • Perfect reproducibility → Validates 3D basin topology
    • Imperfect → Reveals stochastic elements or special threshold properties
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

def run_single_simulation(multiplier, spread, threshold, run_id, cycles):
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
        'run_id': run_id,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 99: 3D BASIN REPRODUCIBILITY VALIDATION")
    print("="*80)
    print()
    print("Validating reproducibility of 3D (mult, spread, threshold) basin structure.")
    print("Following pattern: C96→C97 (2D), C98→C99 (3D) (discovery→validation)")
    print()
    print("C98 found: Threshold is 3rd dimension (86% threshold-sensitive)")
    print("Question: Is 3D basin structure reproducible with N=2 runs?")
    print()

    # Strategic subset from C98 - points that showed threshold sensitivity
    test_triplets = [
        # Threshold-sensitive points from C98
        (0.6, 0.2, 400),  # Showed different attractor at threshold 600
        (0.6, 0.2, 600),
        (1.0, 0.2, 400),  # Showed different attractor at threshold 600
        (1.0, 0.2, 600),
        (1.2, 0.3, 400),  # Showed different attractor at threshold 600
        (1.2, 0.3, 600),
    ]

    cycles = 1000
    runs_per_triplet = 2

    total_runs = len(test_triplets) * runs_per_triplet

    print(f"Configuration:")
    print(f"  Selected 3D triplets (mult, spread, threshold): {len(test_triplets)}")
    print(f"  Runs per triplet: {runs_per_triplet} (reproducibility test)")
    print(f"  Total runs: {total_runs}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Expected: 100% reproducibility (same attractor for both runs)")
    print(f"  Estimated duration: ~{total_runs * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread, threshold in test_triplets:
        print(f"\nTriplet ({mult:.1f}, {spread:.1f}, {threshold}):")
        for run_id in range(1, runs_per_triplet + 1):
            run_count += 1
            print(f"  Run {run_id}/{runs_per_triplet} ({run_count}/{total_runs})...", end=" ", flush=True)
            try:
                result = run_single_simulation(mult, spread, threshold, run_id, cycles)
                results.append(result)
                print(f"✓ Attractor={result['final_dominant'][:30] if result['final_dominant'] else 'None'}..., Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'multiplier': mult, 'spread': spread, 'threshold': threshold, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"3D BASIN REPRODUCIBILITY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * total_runs):  # At least 80% success rate
        # Group by (mult, spread, threshold) triplet
        by_triplet = {}
        for result in successful:
            mult = result['multiplier']
            spread = result['spread']
            threshold = result['threshold']
            triplet_key = (mult, spread, threshold)
            if triplet_key not in by_triplet:
                by_triplet[triplet_key] = []
            by_triplet[triplet_key].append(result)

        # Analyze reproducibility
        print(f"Reproducibility Analysis (N=2 per 3D triplet):")
        print(f"{'Triplet (M,S,T)':>20} | {'Run 1 Attractor':^30} | {'Run 2 Attractor':^30} | {'Match?':^10}")
        print("-" * 110)

        reproducible_count = 0
        total_tested = 0

        for triplet in sorted(by_triplet.keys()):
            triplet_results = by_triplet[triplet]
            if len(triplet_results) >= 2:
                p1 = triplet_results[0]['final_dominant']
                p2 = triplet_results[1]['final_dominant']

                p1_short = p1[:28] + ".." if len(p1) > 28 else p1
                p2_short = p2[:28] + ".." if len(p2) > 28 else p2

                match = p1 == p2
                match_str = "✅ Yes" if match else "❌ No"

                if match:
                    reproducible_count += 1
                total_tested += 1

                print(f"{str(triplet):>20} | {p1_short:^30} | {p2_short:^30} | {match_str:^10}")

        print()

        reproducibility_pct = (reproducible_count / total_tested * 100) if total_tested > 0 else 0

        print(f"Reproducibility Summary:")
        print(f"  3D triplets tested: {total_tested}")
        print(f"  Perfect matches: {reproducible_count}/{total_tested} ({reproducibility_pct:.1f}%)")
        print()

        if reproducibility_pct == 100.0:
            print(f"✅ 3D BASIN STRUCTURE IS 100% REPRODUCIBLE")
            print(f"   ALL triplets show identical attractors across N=2 runs")
            print(f"   Threshold dimension is as deterministic as mult/spread")
            print(f"   3D (mult, spread, threshold) basin structure validated")
            print(f"   Perfect determinism extends to full 3D parameter space")
            insight_56 = True
        elif reproducibility_pct >= 80:
            print(f"⚠️ HIGH REPRODUCIBILITY ({reproducibility_pct:.1f}%)")
            print(f"   Most triplets reproducible")
            print(f"   Some points may show sensitivity")
            print(f"   Overall 3D structure is largely deterministic")
            insight_56 = "high"
        else:
            print(f"⚠️ LOW REPRODUCIBILITY ({reproducibility_pct:.1f}%)")
            print(f"   3D basin structure may have stochastic elements")
            print(f"   Or special threshold properties")
            print(f"   Further investigation needed")
            insight_56 = False

        print()
        if insight_56 == True:
            print(f"🎉 INSIGHT #56: 3D Basin Topology is Perfectly Reproducible")
            print(f"   - 100% reproducibility across tested 3D triplets")
            print(f"   - Threshold dimension is deterministic")
            print(f"   - 3D (mult, spread, threshold) structure validated")
            print(f"   - Extends perfect reproducibility to full 3D parameter space")
            print(f"   - Consistent with all previous findings (C93, C95, C97)")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for reproducibility analysis")
        print(f"   Only {len(successful)}/{total_runs} runs completed successfully")
        insight_56 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "3d_basin_reproducibility"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle99_3d_basin_reproducibility.json"

    output_data = {
        'experiment': 'cycle99_3d_basin_reproducibility',
        'test_triplets': [(m, s, t) for m, s, t in test_triplets],
        'runs_per_triplet': runs_per_triplet,
        'total_runs': total_runs,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'reproducible_triplets': reproducible_count if 'reproducible_count' in locals() else 0,
            'total_tested': total_tested if 'total_tested' in locals() else 0,
            'reproducibility_percentage': reproducibility_pct if 'reproducibility_pct' in locals() else 0
        },
        'insight_56_discovered': insight_56 if 'insight_56' in locals() else False,
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
