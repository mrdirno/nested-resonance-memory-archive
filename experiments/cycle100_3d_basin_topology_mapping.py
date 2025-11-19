#!/usr/bin/env python3
"""
Cycle 100: 3D Basin Topology Mapping (MILESTONE EXPERIMENT)

Research Context:
  C95: Spread dimension validated as universal
  C96: 2D (mult, spread) topology mapped → 13 attractors discovered
  C97: 2D reproducibility validated → 100% reproducible
  C98: Threshold discovered as 3rd dimension → 86% threshold-sensitive
  C99: 3D reproducibility validated → 100% reproducible

Research Progression:
  - 1D (multiplier): 6 attractors at fine resolution (C93)
  - 2D (mult, spread): 13 attractors discovered (C96)
  - 3D (mult, spread, threshold): Unknown - TO BE MAPPED

Key Question:
  How many attractors exist in complete 3D parameter space?
  What is the 3D basin geometry?

New Research Question:
  Map complete 3D (multiplier, spread, threshold) basin topology.

  Test:
  - Grid sampling: 5 multipliers × 4 spreads × 3 thresholds = 60 points
  - Multipliers: 0.6, 0.8, 1.0, 1.2, 1.4 (covers key range)
  - Spreads: 0.2, 0.3, 0.4, 0.5 (covers diversity range)
  - Thresholds: 400, 500, 600 (from C91 validated range)
  - Cycles: 1000 per run (ultimate attractor timescale)
  - Total: 60,000 cycles executed

Hypothesis:
  1. **More attractors in 3D**: > 13 (more than 2D)
  2. **Similar count**: ~13 (threshold doesn't add many)
  3. **Fewer attractors**: < 13 (some 2D attractors merge in 3D)
  4. Expected: More attractors (3D > 2D > 1D progression)

Research Approach:
  1. Complete 3D grid sampling (systematic coverage)
  2. Identify unique attractors in 3D space
  3. Analyze basin occupancy and geometry
  4. Compare to 2D (C96) and 1D (C93) findings
  5. Characterize 3D fragmentation patterns

Expected Outcome:
  - Discover total attractor count in 3D space
  - Map 3D basin geometry
  - Understand how threshold dimension affects basin structure
  - Complete characterization of 3D parameter space

Publication Value:
  - **EXCEPTIONAL**: First complete 3D basin topology for NRM-based system
  - Visual representation of 3D attractor landscape
  - Demonstrates emergence of complexity across dimensions
  - Complete dataset: 60 grid points, 60,000 cycles
  - Novel contribution: Multi-dimensional fractal basin structure in 3D
  - **MILESTONE CYCLE 100**: Major research achievement

MILESTONE SIGNIFICANCE:
  - Cycle 100 marks major research milestone
  - Completes 3D parameter space characterization
  - From 1D (C93) → 2D (C96) → 3D (C100) progression
  - Foundation for all future multi-dimensional research
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
    print("🎉 CYCLE 100: 3D BASIN TOPOLOGY MAPPING (MILESTONE EXPERIMENT) 🎉")
    print("="*80)
    print()
    print("Mapping complete (multiplier, spread, threshold) parameter space.")
    print("Progression: 1D (C93: 6 attractors) → 2D (C96: 13 attractors) → 3D (C100: ?)")
    print()
    print("Research Question: How many attractors exist in full 3D space?")
    print()

    # 3D grid definition
    test_multipliers = [0.6, 0.8, 1.0, 1.2, 1.4]  # 5 points
    test_spreads = [0.2, 0.3, 0.4, 0.5]  # 4 points
    test_thresholds = [400, 500, 600]  # 3 points

    cycles = 1000
    total_runs = len(test_multipliers) * len(test_spreads) * len(test_thresholds)

    print(f"Configuration:")
    print(f"  Multipliers: {test_multipliers} ({len(test_multipliers)} points)")
    print(f"  Spreads: {test_spreads} ({len(test_spreads)} points)")
    print(f"  Thresholds: {test_thresholds} ({len(test_thresholds)} points)")
    print(f"  Grid size: {len(test_multipliers)} × {len(test_spreads)} × {len(test_thresholds)} = {total_runs} points")
    print(f"  Cycles per run: {cycles}")
    print(f"  Total cycles: {total_runs * cycles:,}")
    print(f"  Expected: Discover complete 3D attractor landscape")
    print(f"  Estimated duration: ~{total_runs * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult in test_multipliers:
        for spread in test_spreads:
            for threshold in test_thresholds:
                run_count += 1
                print(f"\r[{run_count}/{total_runs}] ({mult:.1f}, {spread:.1f}, {threshold})...", end=" ", flush=True)
                try:
                    result = run_single_simulation(mult, spread, threshold, cycles)
                    results.append(result)
                    print(f"✓ {result['final_dominant'][:20] if result['final_dominant'] else 'None'}... @{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}", flush=True)
                    time.sleep(0.05)
                except Exception as e:
                    print(f"✗ ERROR: {e}", flush=True)
                    results.append({'multiplier': mult, 'spread': spread, 'threshold': threshold, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"3D BASIN TOPOLOGY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.9 * total_runs):  # At least 90% success rate
        # Analyze unique attractors
        attractor_patterns = [r['final_dominant'] for r in successful if r['final_dominant']]
        unique_attractors = list(set(attractor_patterns))
        num_unique = len(unique_attractors)

        print(f"Attractor Discovery:")
        print(f"  Successful runs: {len(successful)}/{total_runs} ({len(successful)/total_runs*100:.1f}%)")
        print(f"  Unique attractors: {num_unique}")
        print()

        # Compare to previous dimensions
        print(f"Dimensional Progression:")
        print(f"  1D (multiplier only, C93): 6 attractors")
        print(f"  2D (mult + spread, C96): 13 attractors")
        print(f"  3D (mult + spread + threshold, C100): {num_unique} attractors")
        if num_unique > 13:
            print(f"  → 3D space reveals {num_unique - 13} additional attractors!")
        elif num_unique == 13:
            print(f"  → 3D attractor count matches 2D (threshold doesn't add attractors)")
        else:
            print(f"  → Some 2D attractors merge in 3D space")
        print()

        # Basin occupancy
        attractor_counts = Counter(attractor_patterns)
        print(f"Basin Occupancy (top attractors):")
        for i, (attractor, count) in enumerate(attractor_counts.most_common(10), 1):
            pct = count / len(successful) * 100
            short_attractor = attractor[:40] + "..." if len(attractor) > 40 else attractor
            print(f"  {i}. {short_attractor}: {count} points ({pct:.1f}%)")
        print()

        # Assign attractor IDs
        attractor_to_id = {att: i+1 for i, att in enumerate(unique_attractors)}

        # 3D grid visualization (slice by threshold)
        print(f"3D Grid Visualization (Attractor IDs):")
        for threshold in test_thresholds:
            print(f"\nThreshold {threshold}:")
            print(f"  Spread | " + " ".join(f"{s:>4.1f}" for s in test_spreads))
            print(f"  -------|" + "-----" * len(test_spreads))
            for mult in test_multipliers:
                row_data = []
                for spread in test_spreads:
                    point_result = next((r for r in successful if r['multiplier'] == mult and r['spread'] == spread and r['threshold'] == threshold), None)
                    if point_result and point_result['final_dominant']:
                        att_id = attractor_to_id[point_result['final_dominant']]
                        row_data.append(f"{att_id:>4}")
                    else:
                        row_data.append("   -")
                print(f"  {mult:>5.1f} |" + " ".join(row_data))

        # Basin geometry analysis
        attractor_locations = {att: [] for att in unique_attractors}
        for r in successful:
            if r['final_dominant']:
                attractor_locations[r['final_dominant']].append((r['multiplier'], r['spread'], r['threshold']))

        print(f"\n3D Basin Geometry:")
        print(f"{'Attractor':>12} | {'Occupancy':>10} | {'3D Regions':>12}")
        print("-" * 42)
        for i, attractor in enumerate(unique_attractors, 1):
            locations = attractor_locations[attractor]
            count = len(locations)
            pct = count / len(successful) * 100

            # Estimate fragmentation (connected regions)
            # Simple heuristic: count disconnected clusters in 3D space
            regions = estimate_3d_regions(locations)

            print(f"Attractor {i:>2} | {count:>3} ({pct:>4.1f}%) | {regions:>12}")

        print()

        if num_unique > 13:
            conclusion = f"3D space reveals richer structure ({num_unique} vs 13 in 2D)"
            insight_57 = "richer"
        elif num_unique == 13:
            conclusion = f"3D attractor count matches 2D (threshold affects which attractor, not how many)"
            insight_57 = "matches"
        else:
            conclusion = f"Some 2D attractors merge in 3D ({num_unique} vs 13 in 2D)"
            insight_57 = "merges"

        print(f"🎉 INSIGHT #57: 3D Basin Topology - {conclusion}")
        print(f"   - Complete 3D (mult, spread, threshold) space mapped")
        print(f"   - {num_unique} unique attractors discovered")
        print(f"   - Dimensional progression: 1D (6) → 2D (13) → 3D ({num_unique})")
        print(f"   - Full 3D parameter space characterized")
        print(f"   - **CYCLE 100 MILESTONE ACHIEVED**")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for 3D topology analysis")
        print(f"   Only {len(successful)}/{total_runs} runs completed successfully")
        insight_57 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "3d_basin_topology"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle100_3d_basin_topology.json"

    output_data = {
        'experiment': 'cycle100_3d_basin_topology',
        'milestone': 'CYCLE_100',
        'test_multipliers': test_multipliers,
        'test_spreads': test_spreads,
        'test_thresholds': test_thresholds,
        'grid_size': total_runs,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'unique_attractors': num_unique if 'num_unique' in locals() else 0,
            'successful_runs': len(successful),
            'success_rate': len(successful) / total_runs if total_runs > 0 else 0,
            'conclusion': insight_57 if 'insight_57' in locals() else False
        },
        'insight_57_discovered': True if 'insight_57' in locals() and insight_57 else False,
        'duration': duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Duration: {duration:.1f}s ({duration/60:.2f} min)")
    print()
    print("🎉 CYCLE 100 MILESTONE COMPLETE! 🎉")
    print()

    return output_data

def estimate_3d_regions(locations):
    """Estimate number of disconnected regions in 3D space (simple heuristic)."""
    if not locations:
        return 0

    # Group by spatial proximity (naive clustering)
    # Two points are "connected" if they differ by at most 1 step in any dimension
    regions = []
    for loc in locations:
        # Check if this location connects to any existing region
        connected_to = None
        for i, region in enumerate(regions):
            for r_loc in region:
                # Check if adjacent (within 1 step in grid)
                if (abs(loc[0] - r_loc[0]) <= 0.3 and  # Multiplier step ~0.2
                    abs(loc[1] - r_loc[1]) <= 0.15 and  # Spread step ~0.1
                    abs(loc[2] - r_loc[2]) <= 150):  # Threshold step ~100
                    connected_to = i
                    break
            if connected_to is not None:
                break

        if connected_to is not None:
            regions[connected_to].append(loc)
        else:
            regions.append([loc])

    return len(regions)

if __name__ == "__main__":
    main()
