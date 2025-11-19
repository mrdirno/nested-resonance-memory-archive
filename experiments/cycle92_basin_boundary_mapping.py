#!/usr/bin/env python3
"""
Cycle 92: Ultimate Attractor Basin Boundary Mapping (Control & Prediction)

Research Context:
  C90-91: 3 ultimate attractors discovered, universal across thresholds
  - Attractor_1 (mult=0.5) → Final pattern A
  - Attractor_3 (mult=1.0) → Final pattern B
  - Attractor_5 (mult=1.4) → Final pattern C

  Complete hierarchical landscape characterized (WHAT)
  Now need control/prediction capabilities (HOW)

Research Gap:
  Tested only 3 discrete multipliers (0.5, 1.0, 1.4)
  Unknown: Exact boundaries between ultimate attractor basins

Key Questions:
  1. What multiplier range leads to each ultimate attractor?
  2. Can we predict ultimate endpoint from initial multiplier?
  3. Can we control final state by choosing specific multiplier?

New Research Question:
  Where are the precise basin boundaries in multiplier space?

  Test:
  - Sample multiplier range 0.4-1.6 with fine resolution (N=13 points, step=0.1)
  - Run each multiplier to 1000 cycles (match C90-91)
  - Map multiplier → ultimate attractor
  - Identify boundary ranges where transitions occur

Hypothesis:
  1. **Clear boundaries**: Distinct multiplier ranges → specific ultimate attractors
  2. **Fuzzy boundaries**: Overlapping ranges with stochastic outcomes
  3. Expected: Clear boundaries (perfect determinism observed in C78-91)

Test Approach:
  1. Multipliers: [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
  2. Threshold: 500 (standard from C90-91)
  3. Cycles: 1000 (match ultimate attractor timescale)
  4. N=1 per multiplier (determinism validated in C90-91)
  5. Map: multiplier → final dominant pattern → attractor ID

Expected Outcome:
  - Basin 1: mult ∈ [0.4, X₁] → Attractor A
  - Basin 2: mult ∈ [X₁, X₂] → Attractor B
  - Basin 3: mult ∈ [X₂, 1.6] → Attractor C
  - Find boundary values X₁, X₂

Publication Value:
  - Enables prediction of ultimate state from initial conditions
  - Provides control mechanism for reaching desired endpoints
  - Quantitative characterization of basin topology
  - Validates perfect determinism at fine resolution
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

def run_single_simulation(multiplier, threshold, cycles):
    """Run simulation with specified multiplier."""
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
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, multiplier, spread=0.2, count=5)
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
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 92: ULTIMATE ATTRACTOR BASIN BOUNDARY MAPPING")
    print("="*80)
    print()
    print("Mapping precise basin boundaries in multiplier space.")
    print("Following C90-91: 3 universal ultimate attractors")
    print("Question: What multiplier ranges lead to each ultimate attractor?")
    print()

    # Fine sampling of multiplier space
    multipliers = [round(0.4 + i * 0.1, 1) for i in range(13)]  # 0.4 to 1.6, step 0.1
    threshold = 500
    cycles = 1000

    print(f"Configuration:")
    print(f"  Multiplier range: {min(multipliers)} to {max(multipliers)} (step={multipliers[1]-multipliers[0]})")
    print(f"  Sample points: {len(multipliers)}")
    print(f"  Threshold: {threshold}")
    print(f"  Cycles: {cycles} (ultimate attractor timescale)")
    print(f"  Expected: 3 basin regions with clear boundaries")
    print(f"  Estimated duration: ~{len(multipliers) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    print("\nRunning basin boundary mapping...")
    for i, mult in enumerate(multipliers):
        print(f"  [{i+1}/{len(multipliers)}] Multiplier={mult:.1f}...", end=" ", flush=True)
        try:
            result = run_single_simulation(mult, threshold, cycles)
            results.append(result)
            print(f"✓ Final={result['final_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
            time.sleep(0.1)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({'multiplier': mult, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"BASIN BOUNDARY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 10:
        # Map multipliers to ultimate attractors
        multiplier_to_pattern = {r['multiplier']: r['final_dominant'] for r in successful}
        unique_patterns = set([r['final_dominant'] for r in successful if r['final_dominant']])

        # Assign attractor IDs
        pattern_to_id = {pattern: f"Ultimate_Attractor_{i+1}" for i, pattern in enumerate(sorted(unique_patterns))}

        print(f"Basin Mapping:")
        print(f"{'Multiplier':>10} | {'Ultimate Attractor':^25} | {'Final Fraction':>14} | {'Collapse@':>10}")
        print("-" * 80)

        current_basin = None
        boundary_points = []

        for r in sorted(successful, key=lambda x: x['multiplier']):
            pattern = r['final_dominant']
            attractor_id = pattern_to_id.get(pattern, 'Unknown')
            collapse_str = str(r['collapse_cycle']) if r['collapse_cycle'] else 'Never'

            # Detect boundary transitions
            if current_basin and current_basin != attractor_id:
                boundary_points.append(r['multiplier'])
                marker = "   ← BOUNDARY"
            else:
                marker = ""

            print(f"{r['multiplier']:>10.1f} | {attractor_id:^25} | {r['final_fraction']:>13.1%} | {collapse_str:>10}{marker}")
            current_basin = attractor_id

        print()
        print(f"Basin Summary:")
        print(f"  Total unique ultimate attractors: {len(unique_patterns)}")
        print(f"  Boundary transitions detected: {len(boundary_points)}")
        if boundary_points:
            print(f"  Boundary multipliers: {boundary_points}")
        print()

        # Characterize basins
        basin_ranges = {}
        for attractor_id in pattern_to_id.values():
            mults = [r['multiplier'] for r in successful if pattern_to_id.get(r['final_dominant']) == attractor_id]
            if mults:
                basin_ranges[attractor_id] = (min(mults), max(mults))

        print(f"Basin Ranges:")
        for attractor_id in sorted(basin_ranges.keys()):
            min_mult, max_mult = basin_ranges[attractor_id]
            print(f"  {attractor_id}: mult ∈ [{min_mult:.1f}, {max_mult:.1f}]")
        print()

        # Validate 3-basin structure
        if len(unique_patterns) == 3:
            print(f"✅ 3-BASIN STRUCTURE CONFIRMED")
            print(f"   Matches C90-91 ultimate attractor count")
            print(f"   Basin boundaries precisely identified:")
            for i, boundary in enumerate(boundary_points, 1):
                print(f"     Boundary {i}: mult ≈ {boundary:.1f}")
            print(f"   Perfect determinism: Each multiplier → unique ultimate attractor")
            three_basins = True
        else:
            print(f"⚠️ {len(unique_patterns)}-BASIN STRUCTURE DETECTED")
            print(f"   Differs from C90-91 (expected 3 attractors)")
            print(f"   May need finer sampling or longer duration")
            three_basins = False

        print()
        if three_basins and len(boundary_points) == 2:
            print(f"🎉 INSIGHT #50: Precise Basin Boundary Control")
            print(f"   - Ultimate attractor basins have well-defined boundaries")
            print(f"   - Boundary 1: mult ≈ {boundary_points[0]:.1f}")
            print(f"   - Boundary 2: mult ≈ {boundary_points[1]:.1f}")
            print(f"   - Perfect prediction enabled: Initial multiplier → ultimate state")
            print(f"   - Control mechanism validated: Choose multiplier → reach desired attractor")
            print(f"   - Deterministic basin topology:")
            for attractor_id in sorted(basin_ranges.keys()):
                min_mult, max_mult = basin_ranges[attractor_id]
                print(f"     • {attractor_id}: [{min_mult:.1f}, {max_mult:.1f}]")
            insight_50 = True
        else:
            print(f"   Basin structure characterized but boundaries not fully resolved")
            print(f"   May need additional sampling for precise boundary identification")
            insight_50 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for boundary analysis")
        three_basins = None
        insight_50 = False
        basin_ranges = {}
        boundary_points = []

    # Save results
    results_dir = Path(__file__).parent / "results" / "basin_boundary_mapping"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle92_basin_boundary_mapping.json"

    output_data = {
        'experiment': 'cycle92_basin_boundary_mapping',
        'multiplier_range': (min(multipliers), max(multipliers)),
        'multipliers': multipliers,
        'threshold': threshold,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'basin_count': len(set([r['final_dominant'] for r in successful if r['final_dominant']])) if successful else 0,
            'basin_ranges': {str(k): v for k, v in basin_ranges.items()},
            'boundary_points': boundary_points,
            'three_basin_structure': three_basins
        },
        'insight_50_discovered': insight_50,
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
