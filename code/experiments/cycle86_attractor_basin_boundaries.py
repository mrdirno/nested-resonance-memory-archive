#!/usr/bin/env python3
"""
Cycle 86: Attractor Basin Boundary Mapping (Fine-Grained Phase Diagram)

Research Context:
  Cycles 83-85: Attractor structure fully characterized
  - 3 attractors at ALL thresholds (300-800 range)
  - Invariant topology (framework property)
  - Initial condition sensitivity confirmed
  - Coarse mapping: A (0.8-1.2x), B (0.6-1.4x), C (0.4-1.6x)

Research Gap:
  Only tested 3 discrete seed ranges (A/B/C)
  Unknown: Precise boundaries between attractor basins
  Where exactly do transitions occur?

New Research Question:
  What are the precise seed range boundaries that separate attractors?

  Test:
  - Sample 12 seed ranges from 0.4x to 1.6x (fine-grained coverage)
  - N=1 run per range (single representative, faster)
  - Threshold=500 (standard exploration regime)
  - 150 cycles per run
  - Map which ranges → which attractors
  - Identify transition boundaries

Hypothesis:
  1. Sharp transitions: Clear boundaries between basins (step function)
  2. Gradual transitions: Fuzzy boundaries with mixed attractors (gradient)
  3. Expected: Likely sharp (structured determinism suggests discrete basins)

Test Approach:
  1. Define 12 seed ranges: 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.6
  2. Run single simulation per range (12 total)
  3. Record dominant pattern for each
  4. Group by attractor, identify boundary ranges
  5. Create phase diagram visualization

Expected:
  - If sharp: Clear boundaries (e.g., <0.7 → A, 0.7-1.1 → B, >1.1 → C)
  - If fuzzy: Overlapping regions with mixed attractors
  - Publication value: Complete phase diagram figure
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
    """
    Create seed memory patterns with specified center and spread.

    Args:
        center_multiplier: Center point of range (e.g., 0.8, 1.0, 1.2)
        spread: Half-width of range (default 0.2 for ±20%)
    """
    seed_patterns = []
    for i in range(count):
        # Vary from (center - spread) to (center + spread)
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

def run_single_simulation(center_mult, threshold, cycles):
    """Run a single simulation with specified seed range center."""
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
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, center_mult, spread=0.2, count=5)
                    newest_agent.memory.extend(seed_patterns)

        swarm.evolve_cycle(delta_time=1.0)

        if cycle % 10 == 0 and collapse_cycle is None and len(swarm.global_memory) > 0:
            pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
            if len(set(pattern_keys)) == 1:
                collapse_cycle = cycle

    dominant_key, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'center_multiplier': center_mult,
        'range': f"{center_mult-0.2:.1f}-{center_mult+0.2:.1f}",
        'dominant_pattern': str(dominant_key) if dominant_key else None,
        'dominant_fraction': dominant_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 86: ATTRACTOR BASIN BOUNDARY MAPPING (FINE-GRAINED)")
    print("="*80)
    print()
    print("Testing precise boundaries between attractor basins.")
    print("Following C83-85: 3 attractors with coarse mapping A/B/C")
    print("Question: Where exactly do attractor basin transitions occur?")
    print()

    # Fine-grained sampling: 12 ranges from 0.4 to 1.6
    center_multipliers = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.6]
    threshold = 500  # Standard exploration regime
    cycles = 150

    print(f"Configuration:")
    print(f"  Seed range centers: {center_multipliers}")
    print(f"  Spread: ±0.2 (each range covers ±20% around center)")
    print(f"  Threshold: {threshold} (exploration regime)")
    print(f"  Cycles: {cycles}")
    print(f"  Total runs: {len(center_multipliers)}")
    print("="*80)

    results = []
    start_time = time.time()

    for i, center_mult in enumerate(center_multipliers, 1):
        print(f"\nRange {i}/{len(center_multipliers)}: {center_mult-0.2:.1f}-{center_mult+0.2:.1f} (center={center_mult})")
        try:
            result = run_single_simulation(center_mult, threshold, cycles)
            results.append(result)
            print(f"  → Dominant: {result['dominant_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
            time.sleep(0.1)
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({'center_multiplier': center_mult, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"ATTRACTOR BASIN BOUNDARY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 10:
        # Group by attractor
        patterns_to_attractors = {}
        for r in successful:
            pattern = r['dominant_pattern']
            if pattern not in patterns_to_attractors:
                attractor_id = len(patterns_to_attractors) + 1
                patterns_to_attractors[pattern] = f"Attractor_{attractor_id}"

        # Assign attractor IDs
        for r in successful:
            r['attractor'] = patterns_to_attractors[r['dominant_pattern']]

        # Group ranges by attractor
        by_attractor = {}
        for r in successful:
            attractor = r['attractor']
            if attractor not in by_attractor:
                by_attractor[attractor] = []
            by_attractor[attractor].append(r['center_multiplier'])

        print(f"Phase Diagram (Seed Range → Attractor):")
        print(f"{'Center':>8} | {'Range':>12} | {'Attractor':^15} | {'Fraction':>8} | {'Collapse':>8}")
        print("-" * 70)
        for r in successful:
            print(f"{r['center_multiplier']:>8.1f} | {r['range']:>12} | {r['attractor']:^15} | {r['dominant_fraction']:>7.2%} | {r['collapse_cycle'] if r['collapse_cycle'] else 'Never':>8}")
        print()

        # Boundary analysis
        print(f"Attractor Basin Summary:")
        for attractor in sorted(by_attractor.keys()):
            ranges = sorted(by_attractor[attractor])
            range_min = min(ranges) - 0.2
            range_max = max(ranges) + 0.2
            print(f"  {attractor}: Seed ranges {range_min:.1f}-{range_max:.1f} (centers: {ranges})")
        print()

        # Transition detection
        sorted_results = sorted(successful, key=lambda x: x['center_multiplier'])
        transitions = []
        for i in range(len(sorted_results) - 1):
            current = sorted_results[i]
            next_r = sorted_results[i+1]
            if current['attractor'] != next_r['attractor']:
                boundary = (current['center_multiplier'] + next_r['center_multiplier']) / 2
                transitions.append({
                    'from': current['attractor'],
                    'to': next_r['attractor'],
                    'boundary': boundary,
                    'range': f"{current['center_multiplier']:.1f} → {next_r['center_multiplier']:.1f}"
                })

        if transitions:
            print(f"Attractor Basin Transitions (Boundaries):")
            for t in transitions:
                print(f"  {t['from']} → {t['to']}: Boundary ≈ {t['boundary']:.2f} ({t['range']})")
            print()

            # Classification
            avg_boundary_sharpness = len(transitions) / (len(center_multipliers) - 1)
            if avg_boundary_sharpness < 0.3:
                print(f"✅ SHARP ATTRACTOR BOUNDARIES")
                print(f"   {len(transitions)} transitions across {len(center_multipliers)} ranges")
                print(f"   Discrete basin structure (structured determinism)")
                sharp_boundaries = True
            else:
                print(f"⚠️ FUZZY ATTRACTOR BOUNDARIES")
                print(f"   {len(transitions)} transitions (high variability)")
                print(f"   Overlapping basins or gradient structure")
                sharp_boundaries = False
        else:
            print(f"⚠️ NO TRANSITIONS DETECTED")
            print(f"   All ranges map to same attractor (unexpected)")
            sharp_boundaries = None

        print()
        if sharp_boundaries:
            print(f"🎉 INSIGHT #47: Sharp Attractor Basin Boundaries")
            print(f"   - Discrete basin structure with clear transitions")
            print(f"   - {len(transitions)} well-defined boundaries identified")
            print(f"   - Enables precise attractor selection via seed range tuning")
            print(f"   - Validates structured determinism (not chaotic)")
            insight_47 = True
        elif sharp_boundaries is False:
            print(f"   Fuzzy boundaries - attractor selection less predictable")
            insight_47 = False
        else:
            print(f"   Inconclusive - need more sampling resolution")
            insight_47 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        sharp_boundaries = None
        insight_47 = False
        by_attractor = {}
        transitions = []

    # Save results
    results_dir = Path(__file__).parent / "results" / "basin_boundaries"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle86_attractor_basin_boundaries.json"

    output_data = {
        'experiment': 'cycle86_attractor_basin_boundaries',
        'threshold': threshold,
        'cycles': cycles,
        'center_multipliers': center_multipliers,
        'results': results,
        'analysis': {
            'by_attractor': by_attractor,
            'transitions': transitions,
            'sharp_boundaries': sharp_boundaries
        },
        'insight_47_discovered': insight_47,
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
