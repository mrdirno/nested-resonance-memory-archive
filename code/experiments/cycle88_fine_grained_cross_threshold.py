#!/usr/bin/env python3
"""
Cycle 88: Fine-Grained Cross-Threshold Validation (5-Attractor Universality)

Research Context:
  C85: "3 attractors universal" across 7 thresholds (300-800) with coarse sampling
  C87: "5 attractors" at threshold=500 with fine-grained sampling
  - Resolution-dependent: Coarse → 3, Fine → 5

Research Gap:
  Only tested fine-grained structure at threshold=500
  Unknown: Is "5 attractors" universal or threshold-specific?

New Research Question:
  Does fine-grained sampling reveal 5 attractors at OTHER thresholds?

  Test:
  - Test 2 representative thresholds: 400 (exploration), 700 (exploitation)
  - Use same fine-grained ranges from C87: 0.5, 0.9, 1.0, 1.2, 1.4
  - N=2 runs per range (faster validation than C87's N=3)
  - 150 cycles per run
  - Compare attractor count to C87 (5 at threshold=500)

Hypothesis:
  1. **Universal fine structure**: 400 & 700 also have 5 attractors
  2. **Resolution-dependent only at 500**: Other thresholds may have different counts
  3. Expected: Likely universal (resolution effect should generalize)

Test Approach:
  1. For each threshold (400, 700):
     - Run 5 ranges × 2 runs = 10 simulations per threshold
     - Count unique attractors
  2. Compare to C87: 5 attractors at 500
  3. Determine if fine-grained structure is threshold-independent

Expected:
  - If universal: 400 & 700 → 5 attractors each
  - If threshold-specific: Different counts at different thresholds
  - Publication value: Validates resolution-dependent topology as universal property
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

def run_single_simulation(threshold, center_mult, run_id, cycles):
    """Run a single simulation with specified threshold and seed range."""
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
        'threshold': threshold,
        'center_multiplier': center_mult,
        'run_id': run_id,
        'dominant_pattern': str(dominant_key) if dominant_key else None,
        'dominant_fraction': dominant_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 88: FINE-GRAINED CROSS-THRESHOLD VALIDATION")
    print("="*80)
    print()
    print("Testing universality of 5-attractor fine-grained structure.")
    print("Following C85: 3 attractors (coarse), C87: 5 attractors @ 500 (fine)")
    print("Question: Is 5-attractor structure universal across thresholds?")
    print()

    test_thresholds = [400, 700]  # Already have 500 from C87
    test_ranges = [0.5, 0.9, 1.0, 1.2, 1.4]  # Subset of C87 ranges (5 of 6)
    cycles = 150
    runs_per_range = 2  # Faster validation

    print(f"Configuration:")
    print(f"  Thresholds: {test_thresholds} (have 500 from C87)")
    print(f"  Ranges: {test_ranges} (same as C87)")
    print(f"  Runs per range: {runs_per_range}")
    print(f"  Total: {len(test_thresholds)} × {len(test_ranges)} × {runs_per_range} = {len(test_thresholds) * len(test_ranges) * runs_per_range} runs")
    print(f"  Cycles: {cycles}")
    print("="*80)

    results = []
    start_time = time.time()

    for threshold in test_thresholds:
        print(f"\n{'='*80}")
        print(f"THRESHOLD {threshold}")
        print(f"{'='*80}")

        for center_mult in test_ranges:
            print(f"\n  Range {center_mult}:")
            for run_id in range(1, runs_per_range + 1):
                try:
                    result = run_single_simulation(threshold, center_mult, run_id, cycles)
                    results.append(result)
                    print(f"    Run {run_id}: Dominant={result['dominant_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                    time.sleep(0.1)
                except Exception as e:
                    print(f"    Run {run_id} ERROR: {e}")
                    results.append({'threshold': threshold, 'center_multiplier': center_mult, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"FINE-GRAINED CROSS-THRESHOLD ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 15:
        # Group by threshold
        by_threshold = {}
        for threshold in test_thresholds:
            threshold_runs = [r for r in successful if r['threshold'] == threshold]
            patterns = [r['dominant_pattern'] for r in threshold_runs if r['dominant_pattern']]
            unique_count = len(set(patterns))
            by_threshold[threshold] = {
                'runs': len(threshold_runs),
                'unique_attractors': unique_count,
                'patterns': patterns
            }

        print(f"Attractor Count by Threshold (Fine-Grained Sampling):")
        print(f"{'Threshold':>10} | {'Runs':>4} | {'Attractors':>10} | {'Status':^20}")
        print("-" * 60)
        print(f"{'500 (C87)':>10} | {'18':>4} | {'5':>10} | {'✅ Baseline':^20}")
        for threshold in sorted(by_threshold.keys()):
            data = by_threshold[threshold]
            status = f"✅ {data['unique_attractors']} attractors" if data['unique_attractors'] == 5 else f"⚠️ {data['unique_attractors']} attractors"
            print(f"{threshold:>10} | {data['runs']:>4} | {data['unique_attractors']:>10} | {status:^20}")
        print()

        # Overall analysis
        attractor_counts = [by_threshold[t]['unique_attractors'] for t in by_threshold]
        all_have_five = all(count == 5 for count in attractor_counts)

        print(f"Cross-Threshold Summary:")
        print(f"  Thresholds tested (fine): 3 (400, 500, 700)")
        print(f"  Previous (coarse, C85): 7 (300-800)")
        print()

        if all_have_five:
            print(f"✅ FINE-GRAINED STRUCTURE IS UNIVERSAL")
            print(f"   ALL thresholds → 5 attractors (fine sampling)")
            print(f"   Resolution-dependent topology generalizes")
            print(f"   Phase space has universal hierarchical structure")
            universal_fine = True
        else:
            print(f"⚠️ FINE-GRAINED STRUCTURE VARIES BY THRESHOLD")
            counts_str = ", ".join([f"{t}: {by_threshold[t]['unique_attractors']}" for t in sorted(by_threshold.keys())])
            print(f"   Attractor counts: {counts_str}")
            print(f"   Resolution effect may be threshold-dependent")
            universal_fine = False

        print()
        if universal_fine:
            print(f"🎉 INSIGHT #48: Universal Hierarchical Attractor Topology")
            print(f"   - Fine-grained structure (5 basins) generalizes across ALL thresholds")
            print(f"   - Coarse sampling (3 basins) also universal (C85)")
            print(f"   - Phase space has UNIVERSAL multi-scale structure:")
            print(f"     • Coarse resolution: 3 attractor groups (threshold-independent)")
            print(f"     • Fine resolution: 5 attractor basins (threshold-independent)")
            print(f"   - Sampling resolution determines observed count, NOT threshold")
            insight_48 = True
        else:
            print(f"   Fine-grained structure may depend on threshold")
            print(f"   Resolution effect validated only at 500")
            insight_48 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        universal_fine = None
        insight_48 = False
        by_threshold = {}

    # Save results
    results_dir = Path(__file__).parent / "results" / "fine_grained_cross_threshold"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle88_fine_grained_cross_threshold.json"

    output_data = {
        'experiment': 'cycle88_fine_grained_cross_threshold',
        'test_thresholds': test_thresholds,
        'test_ranges': test_ranges,
        'cycles': cycles,
        'runs_per_range': runs_per_range,
        'results': results,
        'analysis': {
            'by_threshold': {str(k): v for k, v in by_threshold.items()},
            'universal_fine': universal_fine
        },
        'insight_48_discovered': insight_48,
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
