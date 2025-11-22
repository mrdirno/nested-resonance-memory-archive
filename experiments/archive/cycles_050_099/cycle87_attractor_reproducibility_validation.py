#!/usr/bin/env python3
"""
Cycle 87: Attractor Reproducibility Validation (5 vs 3 Resolution)

Research Context:
  C83-C85: "3 attractors universal" with coarse sampling (N=2-3 per condition)
  C86: Found 5 attractors with fine-grained sampling (N=1 per range)
  - Coordinates ARE distinct (not duplicates)
  - 2 match C83's A & B, 3 are new

Critical Question:
  Is "5 attractors" real (fine structure) or artifact (N=1 variability)?

Research Question:
  With N=3 runs per range, do we still see 5 attractors or collapse to 3?

  Test:
  - Select 6 representative ranges from C86 (spanning all 5 attractors)
  - Run N=3 per range (18 total runs)
  - Threshold=500, 150 cycles
  - Check reproducibility: Same range → same attractor?
  - Compare diversity: 3 vs 5 attractors with higher N?

Hypothesis:
  1. **5 attractors real**: N=3 reproduces C86's 5-attractor structure
  2. **3 attractors correct**: N=3 collapses to 3 attractors (C86 was N=1 noise)
  3. Expected: If C86 real, should see 5 attractors with high within-range reproducibility

Test Approach:
  1. Select 6 ranges: 0.5 (A1), 0.7 (A1), 0.9 (A2), 1.0 (A3), 1.2 (A4), 1.4 (A5)
     - Covers all 5 C86 attractors
     - Tests within-attractor consistency (0.5 & 0.7 both → A1?)
  2. Run N=3 per range
  3. Analyze within-range diversity (should be low if deterministic)
  4. Count unique attractors across all runs
  5. Compare to C83 (3 attractors) and C86 (5 attractors)

Expected:
  - If 5 real: 15-18 runs → 5 unique attractors, high within-range consistency
  - If 3 correct: 15-18 runs → 3 unique attractors, C86 ranges map to same 3
  - If fuzzy: Many unique patterns, low within-range consistency
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

def run_single_simulation(center_mult, run_id, threshold, cycles):
    """Run a single simulation with specified seed range center."""
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
        'run_id': run_id,
        'dominant_pattern': str(dominant_key) if dominant_key else None,
        'dominant_fraction': dominant_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 87: ATTRACTOR REPRODUCIBILITY VALIDATION (5 vs 3)")
    print("="*80)
    print()
    print("Testing reproducibility of C86's 5-attractor finding with higher N.")
    print("Following C83: 3 attractors (N=2-3), C86: 5 attractors (N=1)")
    print("Question: Is 5 attractors real or N=1 sampling artifact?")
    print()

    # Select 6 representative ranges spanning all 5 C86 attractors
    test_ranges = [
        (0.5, "A1"),  # C86 Attractor_1
        (0.7, "A1"),  # C86 Attractor_1 (test within-attractor consistency)
        (0.9, "A2"),  # C86 Attractor_2
        (1.0, "A3"),  # C86 Attractor_3
        (1.2, "A4"),  # C86 Attractor_4
        (1.4, "A5")   # C86 Attractor_5
    ]

    threshold = 500
    cycles = 150
    runs_per_range = 3

    print(f"Configuration:")
    print(f"  Test ranges: {[r[0] for r in test_ranges]}")
    print(f"  Expected attractors (C86): {[r[1] for r in test_ranges]}")
    print(f"  Runs per range: {runs_per_range}")
    print(f"  Total runs: {len(test_ranges)} × {runs_per_range} = {len(test_ranges) * runs_per_range}")
    print(f"  Threshold: {threshold}, Cycles: {cycles}")
    print("="*80)

    results = []
    start_time = time.time()

    for center_mult, expected_attractor in test_ranges:
        print(f"\nRange {center_mult} (C86 → {expected_attractor}):")
        for run_id in range(1, runs_per_range + 1):
            try:
                result = run_single_simulation(center_mult, run_id, threshold, cycles)
                results.append(result)
                print(f"  Run {run_id}: Dominant={result['dominant_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.1)
            except Exception as e:
                print(f"  Run {run_id} ERROR: {e}")
                results.append({'center_multiplier': center_mult, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"REPRODUCIBILITY VALIDATION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 15:
        # Group by range
        by_range = {}
        for center_mult, _ in test_ranges:
            range_runs = [r for r in successful if r['center_multiplier'] == center_mult]
            patterns = [r['dominant_pattern'] for r in range_runs]
            unique = len(set(patterns))
            by_range[center_mult] = {
                'runs': len(range_runs),
                'unique_patterns': unique,
                'diversity': unique / len(range_runs) if range_runs else 0.0,
                'patterns': patterns
            }

        # Within-range reproducibility
        print(f"Within-Range Reproducibility:")
        print(f"{'Range':>6} | {'Runs':>4} | {'Unique':>6} | {'Diversity':>9} | {'Status':^15}")
        print("-" * 60)
        for center_mult in sorted(by_range.keys()):
            data = by_range[center_mult]
            diversity = data['diversity']
            status = "✅ Consistent" if diversity <= 0.34 else ("⚠️ Variable" if diversity <= 0.67 else "❌ Chaotic")
            print(f"{center_mult:>6.1f} | {data['runs']:>4} | {data['unique_patterns']:>6} | {diversity:>8.1%} | {status:^15}")
        print()

        # Overall diversity
        all_patterns = [r['dominant_pattern'] for r in successful]
        unique_count = len(set(all_patterns))
        overall_diversity = unique_count / len(all_patterns) if all_patterns else 0.0

        print(f"Overall Attractor Count:")
        print(f"  Successful runs: {len(successful)}/{len(results)}")
        print(f"  Unique attractors: {unique_count}")
        print(f"  Overall diversity: {overall_diversity:.1%}")
        print()

        # Compare to C83/C86
        avg_within_diversity = np.mean([data['diversity'] for data in by_range.values()])

        print(f"Comparison to Previous Cycles:")
        print(f"  C83 (N=2-3, coarse): 3 attractors")
        print(f"  C86 (N=1, fine):     5 attractors")
        print(f"  C87 (N=3, fine):     {unique_count} attractors")
        print()

        if unique_count >= 5 and avg_within_diversity < 0.5:
            print(f"✅ C86 VALIDATED: 5 Attractors Confirmed")
            print(f"   - {unique_count} unique attractors found")
            print(f"   - High within-range consistency (avg {avg_within_diversity:.1%})")
            print(f"   - Fine-grained sampling reveals true structure")
            print(f"   - Coarse sampling (C83-C85) missed attractor complexity")
            validated = "5_attractors"
        elif unique_count == 3 and avg_within_diversity < 0.5:
            print(f"❌ C86 REFUTED: 3 Attractors Confirmed")
            print(f"   - {unique_count} unique attractors (matches C83)")
            print(f"   - C86's 5 attractors were N=1 sampling artifact")
            print(f"   - Coarse sampling (C83-C85) was correct")
            validated = "3_attractors"
        else:
            print(f"⚠️ INCONCLUSIVE RESULTS")
            print(f"   - {unique_count} attractors, high variability ({avg_within_diversity:.1%})")
            print(f"   - May need higher N or longer cycles")
            validated = "inconclusive"

        print()
        if validated == "5_attractors":
            print(f"🎉 INSIGHT #47: Fine-Grained Attractor Structure (5 Basins)")
            print(f"   - Phase space has 5 distinct attractor basins (not 3)")
            print(f"   - Coarse sampling collapses nearby attractors")
            print(f"   - Sampling resolution affects observed structure")
            print(f"   - C85/C46 needs revision: 'At least 3' not 'exactly 3'")
            insight_47 = True
        elif validated == "3_attractors":
            print(f"   C83-C85 findings validated, C86 was sampling artifact")
            insight_47 = False
        else:
            print(f"   Need further investigation")
            insight_47 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        validated = None
        insight_47 = False
        by_range = {}

    # Save results
    results_dir = Path(__file__).parent / "results" / "reproducibility_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle87_attractor_reproducibility_validation.json"

    output_data = {
        'experiment': 'cycle87_attractor_reproducibility_validation',
        'threshold': threshold,
        'cycles': cycles,
        'runs_per_range': runs_per_range,
        'test_ranges': [[r[0], r[1]] for r in test_ranges],
        'results': results,
        'analysis': {
            'by_range': {str(k): v for k, v in by_range.items()},
            'validated': validated
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
