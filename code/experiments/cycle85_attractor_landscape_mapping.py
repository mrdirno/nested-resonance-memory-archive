#!/usr/bin/env python3
"""
Cycle 85: Systematic Attractor Landscape Mapping

Research Context:
  Cycle 83: 3 attractors at threshold=500 (exploration)
  Cycle 84: 3 attractors at threshold=750 (exploitation)
  - Attractor COUNT appears regime-independent
  - Attractor DYNAMICS differ by regime

Research Gap:
  Only tested 2 thresholds (500, 750)
  Unknown: Is "3 attractors" universal or threshold-dependent?
  Need complete landscape characterization

New Research Question:
  Do all thresholds exhibit exactly 3 attractors, or does count vary?

  Test:
  - Test 5 additional thresholds: 300, 400, 600, 700, 800
  - Same 3 initial condition ranges (A/B/C)
  - N=2 runs per condition (30 total runs, 6 per threshold)
  - 150 cycles per run (fast validation)
  - Map complete attractor landscape across parameter space

Hypothesis:
  1. Universal hypothesis: All thresholds → 3 attractors (strong universality)
  2. Count varies hypothesis: Different thresholds → different counts (parameter-dependent)
  3. Expected: Likely universal (validates C84 generalization)

Test Approach:
  1. For each threshold in [300, 400, 600, 700, 800]:
     - Run conditions A, B, C with N=2 each
     - Count unique attractors per threshold
  2. Compare attractor counts across thresholds
  3. Determine if structure is universal or threshold-dependent

Expected:
  - If universal: All 5 thresholds → 3 attractors (total: 15 unique patterns)
  - If varies: Different attractor counts at different thresholds
  - Publication value: Complete attractor landscape characterization
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

def create_seed_memory_standard(bridge, reality_metrics, count=5):
    """Create standard seed memory patterns (0.8-1.2x range)."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def create_seed_memory_modified(bridge, reality_metrics, count=5):
    """Create modified seed memory patterns (0.6-1.4x range)."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.6 + 0.8 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def create_seed_memory_wide(bridge, reality_metrics, count=5):
    """Create wide-range seed memory patterns (0.4-1.6x range)."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.4 + 1.2 * (i / count)) for key, value in reality_metrics.items()}
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

def run_single_simulation(threshold, condition, run_id, cycles, seed_fn):
    """Run a single simulation for given threshold and condition."""
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
                    seed_patterns = seed_fn(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        swarm.evolve_cycle(delta_time=1.0)

        if cycle % 10 == 0 and collapse_cycle is None and len(swarm.global_memory) > 0:
            pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
            if len(set(pattern_keys)) == 1:
                collapse_cycle = cycle

    dominant_key, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'threshold': threshold,
        'condition': condition,
        'run_id': run_id,
        'dominant_pattern': str(dominant_key) if dominant_key else None,
        'dominant_fraction': dominant_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 85: SYSTEMATIC ATTRACTOR LANDSCAPE MAPPING")
    print("="*80)
    print()
    print("Testing attractor count universality across threshold parameter space.")
    print("Following C83-C84: 3 attractors at both threshold=500 and 750")
    print("Question: Is '3 attractors' universal or threshold-dependent?")
    print()

    thresholds = [300, 400, 600, 700, 800]  # Already have 500, 750 from C83-C84
    cycles = 150
    runs_per_condition = 2

    print(f"Configuration:")
    print(f"  Thresholds: {thresholds} (testing 5 new, have 500 & 750)")
    print(f"  Cycles per run: {cycles}")
    print(f"  Runs per condition: {runs_per_condition}")
    print(f"  Total: {len(thresholds)} thresholds × 3 conditions × {runs_per_condition} = {len(thresholds) * 3 * runs_per_condition} runs")
    print("="*80)

    results = []
    seed_fns = {'A': create_seed_memory_standard, 'B': create_seed_memory_modified, 'C': create_seed_memory_wide}

    start_time = time.time()

    for threshold in thresholds:
        print(f"\n{'='*80}")
        print(f"THRESHOLD {threshold}")
        print(f"{'='*80}")

        for condition in ['A', 'B', 'C']:
            print(f"\n  CONDITION {condition}:")
            for run_id in range(1, runs_per_condition + 1):
                try:
                    result = run_single_simulation(threshold, condition, run_id, cycles, seed_fns[condition])
                    results.append(result)
                    print(f"    {condition}-{run_id}: Done - Dominant={result['dominant_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                    time.sleep(0.1)  # Brief pause
                except Exception as e:
                    print(f"    {condition}-{run_id} Error: {e}")
                    results.append({'threshold': threshold, 'condition': condition, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"ATTRACTOR LANDSCAPE ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 20:  # Need majority of 30 runs
        # Group by threshold
        by_threshold = {}
        for threshold in thresholds:
            threshold_runs = [r for r in successful if r['threshold'] == threshold]
            patterns = [r['dominant_pattern'] for r in threshold_runs if r['dominant_pattern']]
            unique_count = len(set(patterns))
            by_threshold[threshold] = {
                'runs': len(threshold_runs),
                'unique_attractors': unique_count,
                'patterns': patterns
            }

        print(f"Attractor Count by Threshold:")
        print(f"{'Threshold':>10} | {'Runs':>4} | {'Attractors':>10} | {'Status':^15}")
        print("-" * 50)
        for threshold in sorted(by_threshold.keys()):
            data = by_threshold[threshold]
            status = "✅ 3 attractors" if data['unique_attractors'] == 3 else f"⚠️ {data['unique_attractors']} attractors"
            print(f"{threshold:>10} | {data['runs']:>4} | {data['unique_attractors']:>10} | {status:^15}")
        print()

        # Overall analysis
        attractor_counts = [by_threshold[t]['unique_attractors'] for t in by_threshold]
        all_have_three = all(count == 3 for count in attractor_counts)

        print(f"Cross-Threshold Summary:")
        print(f"  Thresholds tested: {len(by_threshold)} (300, 400, 600, 700, 800)")
        print(f"  Plus previous: 2 (500 from C83, 750 from C84)")
        print(f"  Total coverage: 7 thresholds (300-800 range)")
        print()

        if all_have_three:
            print(f"✅ UNIVERSAL ATTRACTOR STRUCTURE CONFIRMED")
            print(f"   ALL thresholds → 3 attractors")
            print(f"   Attractor count is THRESHOLD-INDEPENDENT")
            print(f"   Strong universality: Framework property across full parameter range")
            universal = True
        else:
            print(f"⚠️ VARIABLE ATTRACTOR STRUCTURE")
            print(f"   Attractor count varies by threshold:")
            for threshold in sorted(by_threshold.keys()):
                print(f"     Threshold {threshold}: {by_threshold[threshold]['unique_attractors']} attractors")
            print(f"   Attractor count is THRESHOLD-DEPENDENT")
            universal = False

        print()
        if universal:
            print(f"🎉 INSIGHT #46: Universal Attractor Structure (Strong Universality)")
            print(f"   - Attractor count (3) is invariant across ALL energy regimes")
            print(f"   - Tested 300-800 threshold range (7 data points)")
            print(f"   - Framework property: Energy controls dynamics, NOT structure")
            print(f"   - Strongest evidence yet for NRM universality")
            insight_46 = True
        else:
            print(f"   Attractor count varies - partial universality only")
            insight_46 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        universal = None
        insight_46 = False
        by_threshold = {}

    # Save results
    results_dir = Path(__file__).parent / "results" / "attractor_landscape"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle85_attractor_landscape_mapping.json"

    output_data = {
        'experiment': 'cycle85_attractor_landscape_mapping',
        'thresholds_tested': thresholds,
        'cycles': cycles,
        'runs_per_condition': runs_per_condition,
        'total_runs': len(results),
        'successful_runs': len(successful),
        'results': results,
        'analysis': {
            'by_threshold': {str(k): v for k, v in by_threshold.items()},
            'universal': universal
        },
        'insight_46_discovered': insight_46,
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
