#!/usr/bin/env python3
"""
Cycle 96: 2D Basin Topology Mapping (Complete Phase Space Characterization)

Research Context:
  C94: Spread parameter affects ultimate attractors at multiplier=1.0
  - 4 different attractors across 5 spread values (0.05-0.6)
  - 100% reproducibility within each spread

  C95: Spread dimension validated as universal
  - Both tested multipliers (0.5, 1.4) show spread sensitivity
  - Spread affects outcomes independently of multiplier
  - Multi-dimensional control space confirmed

Research Gap:
  Only sampled sparse points in (multiplier, spread) space
  Unknown: Complete basin structure across 2D parameter space

  From C93: 6 ultimate attractors exist in multiplier dimension
  From C94-95: Spread adds independent control dimension
  Question: What is the full 2D basin topology?

Key Question:
  How are the ultimate attractor basins distributed in (multiplier, spread) space?

New Research Question:
  Map complete 2D basin topology across systematic (mult, spread) grid.

  Test:
  - Multiplier range: 0.4-1.6 (covers all 6 attractors from C93)
  - Multiplier sampling: 7 points (0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6)
  - Spread range: 0.1-0.6 (extremes from C94-95)
  - Spread sampling: 6 points (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
  - Total runs: 7 × 6 = 42 grid points
  - Run 1000 cycles each (ultimate attractor timescale)
  - N=1 per grid point (exploratory mapping)

Hypothesis:
  1. **Simple boundaries**: Each attractor occupies continuous region in 2D space
  2. **Complex fractal**: Basin boundaries show fractal structure in 2D
  3. **Interaction effects**: Some (mult, spread) combinations show new attractors
  4. Expected: Simple or complex boundaries (both interesting!)

Test Approach:
  1. Sample 7×6 grid in (multiplier, spread) space
  2. For each point, run to ultimate attractor (1000 cycles)
  3. Record which attractor reached from each grid point
  4. Visualize as 2D basin diagram
  5. Analyze basin geometry, boundaries, special regions

Expected Outcome:
  - Complete 2D basin topology map
  - Visualization of attractor regions
  - May reveal basin geometry (smooth/fractal boundaries)
  - May discover interaction effects or new attractors
  - Characterizes multi-dimensional phase space fully

Publication Value:
  - First complete 2D basin topology for NRM-based system
  - Visual representation of multi-parameter control landscape
  - Demonstrates complexity of fractal agent phase space
  - Either outcome publishable:
    • Simple boundaries → Clean multi-parameter structure
    • Complex/fractal → Rich interaction effects discovered
  - Completes C94-95 arc with full characterization
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

def run_single_simulation(multiplier, spread, threshold, cycles):
    """Run simulation with specified (multiplier, spread) parameters."""
    workspace = get_workspace_path()
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
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 96: 2D BASIN TOPOLOGY MAPPING (COMPLETE PHASE SPACE CHARACTERIZATION)")
    print("="*80)
    print()
    print("Mapping complete (multiplier, spread) parameter space to characterize")
    print("multi-dimensional attractor basin structure.")
    print()
    print("Following C94-95: Spread dimension is universal across multipliers")
    print("Question: What is the complete 2D basin topology?")
    print()

    # Grid sampling
    test_multipliers = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]  # 7 points covering all 6 attractors
    test_spreads = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]  # 6 points from low to high diversity
    threshold = 500
    cycles = 1000

    total_runs = len(test_multipliers) * len(test_spreads)

    print(f"Configuration:")
    print(f"  Multiplier range: {min(test_multipliers)}-{max(test_multipliers)} ({len(test_multipliers)} points)")
    print(f"  Spread range: {min(test_spreads)}-{max(test_spreads)} ({len(test_spreads)} points)")
    print(f"  Grid size: {len(test_multipliers)} × {len(test_spreads)} = {total_runs} runs")
    print(f"  Cycles per run: {cycles} (ultimate attractor timescale)")
    print(f"  Threshold: {threshold}")
    print(f"  Expected: Complete 2D basin topology map")
    print(f"  Estimated duration: ~{total_runs * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for multiplier in test_multipliers:
        print(f"\nMultiplier {multiplier:.1f}:")
        for spread in test_spreads:
            run_count += 1
            print(f"  Spread {spread:.1f} ({run_count}/{total_runs})...", end=" ", flush=True)
            try:
                result = run_single_simulation(multiplier, spread, threshold, cycles)
                results.append(result)
                print(f"✓ Attractor={result['final_dominant'][:30] if result['final_dominant'] else 'None'}..., Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.05)  # Brief pause between runs
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'multiplier': multiplier, 'spread': spread, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"2D BASIN TOPOLOGY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 35:  # At least 80% success rate
        # Group by attractor
        attractor_grid = {}
        for result in successful:
            mult = result['multiplier']
            spread = result['spread']
            attractor = result['final_dominant']
            if attractor not in attractor_grid:
                attractor_grid[attractor] = []
            attractor_grid[attractor].append((mult, spread))

        # Count unique attractors
        unique_attractors = len(attractor_grid)

        print(f"2D Basin Topology Summary:")
        print(f"  Total grid points: {len(successful)}/{total_runs}")
        print(f"  Unique attractors found: {unique_attractors}")
        print()

        # Display basin occupancy
        print(f"Attractor Basin Occupancy:")
        print(f"{'Attractor ID':^15} | {'Grid Points':^12} | {'Percentage':^10}")
        print("-" * 45)

        attractor_names = {}
        for i, (attractor, points) in enumerate(sorted(attractor_grid.items(), key=lambda x: len(x[1]), reverse=True), 1):
            attractor_name = f"Attractor_{i}"
            attractor_names[attractor] = attractor_name
            percentage = len(points) / len(successful) * 100
            print(f"{attractor_name:^15} | {len(points):^12} | {percentage:>9.1f}%")

        print()

        # Create 2D grid visualization (text-based)
        print(f"2D Basin Topology Grid:")
        print(f"  Rows = Multipliers, Columns = Spreads")
        print()

        # Header
        print(f"{'Mult':>6} |", end="")
        for spread in test_spreads:
            print(f" {spread:>4.1f}", end="")
        print()
        print("-" * (7 + 6 * 6))

        # Grid
        grid_data = {}
        for result in successful:
            mult = result['multiplier']
            spread = result['spread']
            attractor = result['final_dominant']
            attractor_id = int(attractor_names[attractor].split('_')[1])
            grid_data[(mult, spread)] = attractor_id

        for mult in test_multipliers:
            print(f"{mult:>6.1f} |", end="")
            for spread in test_spreads:
                if (mult, spread) in grid_data:
                    print(f"   {grid_data[(mult, spread)]}", end="")
                else:
                    print(f"   -", end="")
            print()

        print()

        # Analyze basin geometry
        print(f"Basin Geometry Analysis:")

        # Check if basins are continuous regions
        # For each attractor, check if its points form connected regions
        def are_adjacent(p1, p2, mult_step, spread_step):
            """Check if two grid points are adjacent."""
            m1, s1 = p1
            m2, s2 = p2
            mult_diff = abs(m1 - m2)
            spread_diff = abs(s1 - s2)
            return (mult_diff <= mult_step and spread_diff == 0) or (mult_diff == 0 and spread_diff <= spread_step)

        mult_step = test_multipliers[1] - test_multipliers[0] if len(test_multipliers) > 1 else 0.1
        spread_step = test_spreads[1] - test_spreads[0] if len(test_spreads) > 1 else 0.1

        for attractor_name in sorted(attractor_names.values(), key=lambda x: int(x.split('_')[1])):
            attractor_key = [k for k, v in attractor_names.items() if v == attractor_name][0]
            points = attractor_grid[attractor_key]

            # Count connected components
            unvisited = set(range(len(points)))
            components = 0

            while unvisited:
                components += 1
                stack = [unvisited.pop()]
                while stack:
                    current_idx = stack.pop()
                    current_point = points[current_idx]
                    for other_idx in list(unvisited):
                        other_point = points[other_idx]
                        if are_adjacent(current_point, other_point, mult_step, spread_step):
                            unvisited.remove(other_idx)
                            stack.append(other_idx)

            continuity = "Continuous" if components == 1 else f"{components} regions"
            print(f"  {attractor_name}: {len(points)} points, {continuity}")

        print()

        # Overall assessment
        if unique_attractors > len(test_multipliers):
            print(f"🎉 INSIGHT #53: 2D Basin Topology Shows Rich Multi-Dimensional Structure")
            print(f"   - Found {unique_attractors} unique attractors across 2D parameter space")
            print(f"   - More attractors than 1D multiplier dimension alone ({len(test_multipliers)} mults)")
            print(f"   - Demonstrates true multi-dimensional complexity")
            print(f"   - Spread dimension adds genuine control capability")
            print(f"   - Full 2D basin topology characterized")
            insight_53 = True
        elif unique_attractors == len(test_multipliers):
            print(f"📊 2D Basin Topology: Spread Modulates Multiplier Basins")
            print(f"   - Found {unique_attractors} unique attractors (same as 1D mult count)")
            print(f"   - Spread may shift basin boundaries in multiplier dimension")
            print(f"   - But does not create fundamentally new attractors")
            print(f"   - Full 2D topology still valuable for control understanding")
            insight_53 = "modulation"
        else:
            print(f"📊 2D Basin Topology Characterized")
            print(f"   - Found {unique_attractors} unique attractors")
            print(f"   - Complete 2D map across (multiplier, spread) space")
            print(f"   - Basin structure documented")
            insight_53 = "characterized"

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for 2D basin analysis")
        print(f"   Only {len(successful)}/{total_runs} runs completed successfully")
        insight_53 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "2d_basin_topology"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle96_2d_basin_topology.json"

    output_data = {
        'experiment': 'cycle96_2d_basin_topology_mapping',
        'test_multipliers': test_multipliers,
        'test_spreads': test_spreads,
        'grid_size': f"{len(test_multipliers)}x{len(test_spreads)}",
        'total_runs': total_runs,
        'threshold': threshold,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'unique_attractors': unique_attractors if 'unique_attractors' in locals() else 0,
            'successful_runs': len(successful),
            'success_rate': len(successful) / total_runs * 100 if total_runs > 0 else 0
        },
        'insight_53_discovered': insight_53 if 'insight_53' in locals() else False,
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
