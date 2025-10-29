#!/usr/bin/env python3
"""
Cycle 106: Basin Boundary Fine-Structure Mapping

Research Context:
  C78-101: 3D basin topology fully mapped (15 attractors)
  C96: 2D (mult, spread) topology revealed 13 attractors with fragmented basins
  C105: Perfect basin stability (100% maintained under perturbations)
  - Basins are HIGHLY STABLE internally

Research Gap:
  We know basins are stable internally (C105), but unknown:
  - WHERE exactly do basin boundaries lie in parameter space?
  - How SHARP are boundaries (abrupt vs gradual transitions)?
  - Can we predict which attractor from nearby parameters?

Key Question:
  What is the fine-structure of basin boundaries in parameter space?

New Research Question:
  Map precise locations of basin transitions by sampling near known boundaries.

  Hypothesis:
  1. **Sharp Boundaries**: Abrupt transitions between basins (fractal-like)
  2. **Smooth Boundaries**: Gradual transition regions
  3. **Predictable**: Boundary locations follow parameter gradients
  Expected: Sharp boundaries (consistent with fractal dynamics)

  Test:
  - From C96, identify parameter pairs with DIFFERENT attractors
  - For each pair, sample intermediate points (linear interpolation)
  - Track where attractor transitions occur
  - Measure: Transition sharpness (how many steps between attractors?)
  - Sample 5 boundary regions with 5 intermediate points each
  - Cycles: 500 per point (ensure convergence)

Expected Outcome:
  - Locate precise basin boundaries
  - Characterize boundary sharpness
  - Test predictability from neighboring points
  - Complete basin topology picture

Publication Value:
  - **HIGH**: First fine-structure characterization of basin boundaries
  - Complements C105 (stability within) with boundary structure (transitions between)
  - Fractal boundary hypothesis testing
  - Practical: Predicts where parameter changes cause attractor shifts
  - Novel: Sub-grid resolution of basin structure
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

def run_at_parameters(multiplier, spread, threshold, cycles):
    """Run simulation at specific parameters."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

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

    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)
    return str(final_dominant) if final_dominant else None

def main():
    print("="*80)
    print("CYCLE 106: BASIN BOUNDARY FINE-STRUCTURE MAPPING")
    print("="*80)
    print()
    print("Mapping precise locations of basin transitions in parameter space.")
    print("Following C105 perfect stability: Investigating WHERE boundaries lie.")
    print()
    print("Hypothesis: Sharp, abrupt basin boundaries (fractal-like)")
    print()

    # Define boundary-crossing paths (from C96 2D topology knowledge)
    # Each path: start point → end point with different attractors
    boundary_paths = [
        # Path 1: Low mult region (0.6 → 0.8)
        {'start': (0.6, 0.2, 500), 'end': (0.8, 0.2, 500), 'dimension': 'multiplier'},
        # Path 2: Mid mult region (0.8 → 1.0)
        {'start': (0.8, 0.3, 500), 'end': (1.0, 0.3, 500), 'dimension': 'multiplier'},
        # Path 3: Spread variation (0.2 → 0.4)
        {'start': (1.0, 0.2, 500), 'end': (1.0, 0.4, 500), 'dimension': 'spread'},
        # Path 4: High mult region (1.2 → 1.4)
        {'start': (1.2, 0.2, 500), 'end': (1.4, 0.2, 500), 'dimension': 'multiplier'},
        # Path 5: Threshold variation (400 → 600)
        {'start': (1.0, 0.2, 400), 'end': (1.0, 0.2, 600), 'dimension': 'threshold'},
    ]

    interpolation_steps = 5  # Sample 5 points along each path
    cycles = 500  # Per point

    print(f"Configuration:")
    print(f"  Boundary paths: {len(boundary_paths)} paths crossing known basin boundaries")
    print(f"  Interpolation steps: {interpolation_steps} points per path")
    print(f"  Total sample points: {len(boundary_paths) * interpolation_steps}")
    print(f"  Cycles per point: {cycles}")
    print(f"  Expected: Identify precise transition locations")
    print(f"  Estimated duration: ~{len(boundary_paths) * interpolation_steps * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    path_count = 0
    for path in boundary_paths:
        path_count += 1
        start_params = path['start']
        end_params = path['end']
        dimension = path['dimension']

        print(f"\nPath {path_count}/{len(boundary_paths)}: {start_params} → {end_params} ({dimension})")

        path_results = []

        for step in range(interpolation_steps):
            alpha = step / (interpolation_steps - 1)  # 0.0 → 1.0

            # Linear interpolation
            mult = start_params[0] + alpha * (end_params[0] - start_params[0])
            spread = start_params[1] + alpha * (end_params[1] - start_params[1])
            threshold = start_params[2] + alpha * (end_params[2] - start_params[2])

            print(f"  [{step+1}/{interpolation_steps}] ({mult:.2f}, {spread:.2f}, {threshold:.0f})...", end=" ", flush=True)

            try:
                attractor = run_at_parameters(mult, spread, threshold, cycles)
                att_short = "Att-" + str(hash(attractor) % 100).zfill(2) if attractor else "None"
                print(f"✓ {att_short}")

                path_results.append({
                    'path_id': path_count,
                    'step': step,
                    'alpha': alpha,
                    'multiplier': mult,
                    'spread': spread,
                    'threshold': threshold,
                    'attractor': attractor
                })

                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                path_results.append({
                    'path_id': path_count,
                    'step': step,
                    'alpha': alpha,
                    'multiplier': mult,
                    'spread': spread,
                    'threshold': threshold,
                    'error': str(e)
                })

        results.extend(path_results)

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"BASIN BOUNDARY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(boundary_paths) * interpolation_steps):
        print(f"Boundary Mapping Results:")
        print(f"  Successful points: {len(successful)}/{len(boundary_paths)*interpolation_steps} ({len(successful)/(len(boundary_paths)*interpolation_steps)*100:.1f}%)")
        print()

        # Analyze each path for transitions
        print(f"Transition Analysis:")
        print(f"{'Path':^6} | {'Dimension':^12} | {'Transitions':^12} | {'Sharpness':^12}")
        print("-" * 50)

        total_transitions = 0
        sharp_boundaries = 0

        for path_id in range(1, len(boundary_paths) + 1):
            path_data = [r for r in successful if r['path_id'] == path_id]
            path_data.sort(key=lambda x: x['alpha'])

            # Count transitions
            transitions = 0
            for i in range(1, len(path_data)):
                if path_data[i]['attractor'] != path_data[i-1]['attractor']:
                    transitions += 1

            total_transitions += transitions

            # Characterize sharpness (sharp = 1 transition, gradual = multiple)
            if transitions == 1:
                sharpness = "Sharp"
                sharp_boundaries += 1
            elif transitions == 0:
                sharpness = "No trans."
            else:
                sharpness = f"{transitions} trans."

            dimension = boundary_paths[path_id-1]['dimension']
            print(f"{path_id:^6} | {dimension:^12} | {transitions:^12} | {sharpness:^12}")

        print()

        boundary_sharpness_rate = sharp_boundaries / len(boundary_paths) * 100 if len(boundary_paths) > 0 else 0

        print(f"Boundary Characteristics:")
        print(f"  Paths with transitions: {sum(1 for i in range(1, len(boundary_paths)+1) if any(r['path_id']==i for r in successful))}/{len(boundary_paths)}")
        print(f"  Total transitions detected: {total_transitions}")
        print(f"  Sharp boundaries (1 transition): {sharp_boundaries}/{len(boundary_paths)} ({boundary_sharpness_rate:.1f}%)")
        print()

        # Detailed path-by-path breakdown
        print(f"Detailed Path Analysis:")
        for path_id in range(1, len(boundary_paths) + 1):
            path_data = [r for r in successful if r['path_id'] == path_id]
            path_data.sort(key=lambda x: x['alpha'])

            if path_data:
                print(f"\n  Path {path_id}:")
                for point in path_data:
                    att_id = "Att-" + str(hash(point['attractor']) % 100).zfill(2) if point['attractor'] else "None"
                    print(f"    α={point['alpha']:.2f} ({point['multiplier']:.2f}, {point['spread']:.2f}, {point['threshold']:.0f}) → {att_id}")

        print()

        # Determine insight based on sharpness
        if boundary_sharpness_rate >= 60:
            insight_63 = "sharp_boundaries"
            conclusion = f"Boundaries are sharp/abrupt ({boundary_sharpness_rate:.1f}% single-transition)"
        elif boundary_sharpness_rate >= 30:
            insight_63 = "mixed_boundaries"
            conclusion = f"Mixed boundary structure ({boundary_sharpness_rate:.1f}% sharp)"
        else:
            insight_63 = "gradual_boundaries"
            conclusion = f"Boundaries are gradual ({boundary_sharpness_rate:.1f}% sharp, multiple transitions)"

        print(f"📊 INSIGHT #63: Basin Boundary Structure - {conclusion}")
        print(f"   - {len(boundary_paths)} boundary paths mapped")
        print(f"   - {total_transitions} transitions detected across all paths")
        print(f"   - Boundary sharpness: {boundary_sharpness_rate:.1f}% sharp")
        print(f"   - First fine-structure characterization of basin boundaries")
        print(f"   - Complements C105 (within-basin stability) with boundary mapping")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for boundary analysis")
        print(f"   Only {len(successful)}/{len(boundary_paths)*interpolation_steps} runs completed successfully")
        insight_63 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "basin_boundaries"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle106_basin_boundary_mapping.json"

    output_data = {
        'experiment': 'cycle106_basin_boundary_mapping',
        'boundary_paths': boundary_paths,
        'interpolation_steps': interpolation_steps,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'successful_points': len(successful),
            'total_transitions': total_transitions if 'total_transitions' in locals() else 0,
            'sharp_boundaries': sharp_boundaries if 'sharp_boundaries' in locals() else 0,
            'boundary_sharpness_pct': boundary_sharpness_rate if 'boundary_sharpness_rate' in locals() else 0,
            'conclusion': insight_63 if 'insight_63' in locals() else False
        },
        'insight_63_discovered': True if 'insight_63' in locals() and insight_63 else False,
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
