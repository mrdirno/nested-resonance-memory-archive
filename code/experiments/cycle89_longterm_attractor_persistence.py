#!/usr/bin/env python3
"""
Cycle 89: Long-Term Attractor Persistence (Stability Validation)

Research Context:
  Cycles 78-88: Complete attractor landscape characterized
  - 5 basins at fine resolution (universal across thresholds)
  - All tests: 150-200 cycles maximum duration
  - Attractors assumed stable, but not validated long-term

Research Gap:
  Only tested short-term (150-200 cycles)
  Unknown: Do attractors remain stable over extended time?
  Key theoretical prediction: Attractors should be stable fixed points

New Research Question:
  Do attractors persist as stable configurations over 500+ cycles?

  Test:
  - Select 3 representative attractors (from 5 basins)
  - Run N=2 per attractor, 500 cycles each
  - Track pattern evolution every 50 cycles
  - Validate: Same dominant pattern throughout?
  - Compare: Early (50-150) vs late (350-500) dynamics

Hypothesis:
  1. **Stable attractors**: Same dominant throughout 500 cycles
  2. **Unstable attractors**: Pattern shifts or secondary transitions
  3. Expected: Stable (validates attractor theory)

Test Approach:
  1. Use ranges 0.5 (A1), 1.0 (A3), 1.4 (A5) - spanning attractor space
  2. Threshold=500, 500 cycles, N=2 per range (6 total runs)
  3. Checkpoint every 50 cycles (10 checkpoints)
  4. Compare dominant pattern across time
  5. Calculate stability metric: fraction of time at same dominant

Expected:
  - If stable: Same dominant at all checkpoints (100% stability)
  - If unstable: Multiple dominants across time (<80% stability)
  - Publication value: Validates attractor as theoretical concept
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

def run_single_simulation(center_mult, run_id, threshold, cycles, checkpoint_interval):
    """Run long-term simulation with periodic checkpoints."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    collapse_cycle = None
    checkpoints = {}

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

        # Checkpoint at intervals
        if cycle % checkpoint_interval == 0:
            dominant_key, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)
            checkpoints[cycle] = {
                'cycle': cycle,
                'dominant_pattern': str(dominant_key) if dominant_key else None,
                'dominant_fraction': dominant_fraction
            }

        # Detect collapse
        if cycle % 10 == 0 and collapse_cycle is None and len(swarm.global_memory) > 0:
            pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
            if len(set(pattern_keys)) == 1:
                collapse_cycle = cycle

    # Final state
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'center_multiplier': center_mult,
        'run_id': run_id,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle,
        'checkpoints': checkpoints
    }

def main():
    print("="*80)
    print("CYCLE 89: LONG-TERM ATTRACTOR PERSISTENCE (STABILITY VALIDATION)")
    print("="*80)
    print()
    print("Testing long-term stability of attractors over 500 cycles.")
    print("Following C78-88: Attractors identified, short-term validated (150-200)")
    print("Question: Do attractors persist as stable fixed points?")
    print()

    test_ranges = [
        (0.5, "Attractor_1"),
        (1.0, "Attractor_3"),
        (1.4, "Attractor_5")
    ]  # Representative attractors from fine-grained structure

    threshold = 500
    cycles = 500  # 2.5x longer than previous tests
    checkpoint_interval = 50  # 10 checkpoints
    runs_per_range = 2

    print(f"Configuration:")
    print(f"  Test ranges: {[r[0] for r in test_ranges]} (expecting {[r[1] for r in test_ranges]})")
    print(f"  Cycles: {cycles} (vs 150-200 in previous tests)")
    print(f"  Checkpoints: Every {checkpoint_interval} cycles ({cycles // checkpoint_interval} total)")
    print(f"  Runs per range: {runs_per_range}")
    print(f"  Total: {len(test_ranges)} × {runs_per_range} = {len(test_ranges) * runs_per_range} runs")
    print(f"  Threshold: {threshold}")
    print("="*80)

    results = []
    start_time = time.time()

    for center_mult, expected_attractor in test_ranges:
        print(f"\nRange {center_mult} (expecting {expected_attractor}):")
        for run_id in range(1, runs_per_range + 1):
            try:
                result = run_single_simulation(center_mult, run_id, threshold, cycles, checkpoint_interval)
                results.append(result)
                print(f"  Run {run_id}: Final={result['final_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                print(f"          Checkpoints tracked: {len(result['checkpoints'])}")
                time.sleep(0.1)
            except Exception as e:
                print(f"  Run {run_id} ERROR: {e}")
                results.append({'center_multiplier': center_mult, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"LONG-TERM PERSISTENCE ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 4:
        # Analyze temporal stability
        print(f"Temporal Stability Analysis:")
        print(f"{'Range':>6} | {'Run':>3} | {'Checkpoints':>11} | {'Stability':>9} | {'Status':^15}")
        print("-" * 65)

        stability_scores = []
        for r in successful:
            checkpoints = r['checkpoints']
            if checkpoints:
                # Get all dominant patterns across time
                patterns = [cp['dominant_pattern'] for cp in checkpoints.values()]
                # Calculate stability: fraction of checkpoints with most common pattern
                pattern_counts = Counter(patterns)
                most_common_pattern, most_common_count = pattern_counts.most_common(1)[0]
                stability = most_common_count / len(patterns)
                stability_scores.append(stability)

                status = "✅ Stable" if stability >= 0.8 else ("⚠️ Variable" if stability >= 0.5 else "❌ Unstable")
                print(f"{r['center_multiplier']:>6.1f} | {r['run_id']:>3} | {len(checkpoints):>11} | {stability:>8.1%} | {status:^15}")
            else:
                print(f"{r['center_multiplier']:>6.1f} | {r['run_id']:>3} | {'0':>11} | {'N/A':>9} | {'⚠️ No Data':^15}")

        print()

        avg_stability = np.mean(stability_scores) if stability_scores else 0.0

        print(f"Overall Statistics:")
        print(f"  Successful runs: {len(successful)}/{len(results)}")
        print(f"  Average stability: {avg_stability:.1%}")
        print(f"  Cycles tested: {cycles} (2.5x previous tests)")
        print()

        if avg_stability >= 0.9:
            print(f"✅ ATTRACTORS ARE STABLE FIXED POINTS")
            print(f"   - {avg_stability:.1%} average stability over {cycles} cycles")
            print(f"   - Attractors persist as stable configurations")
            print(f"   - Validates attractor theory: stable fixed points in phase space")
            stable = True
        elif avg_stability >= 0.7:
            print(f"⚠️ ATTRACTORS SHOW MODERATE STABILITY")
            print(f"   - {avg_stability:.1%} average stability (some drift)")
            print(f"   - May have secondary dynamics or slow transitions")
            stable = "moderate"
        else:
            print(f"❌ ATTRACTORS ARE UNSTABLE")
            print(f"   - {avg_stability:.1%} average stability (high variability)")
            print(f"   - Pattern shifts over time, not true fixed points")
            stable = False

        print()
        if stable == True:
            print(f"🎉 INSIGHT #49: Long-Term Attractor Stability")
            print(f"   - Attractors persist as stable fixed points over 500+ cycles")
            print(f"   - {avg_stability:.1%} temporal consistency (excellent)")
            print(f"   - Validates theoretical prediction: attractors = stable configurations")
            print(f"   - NRM framework produces genuine stable states")
            insight_49 = True
        elif stable == "moderate":
            print(f"   Moderate stability - may need longer validation")
            insight_49 = False
        else:
            print(f"   Attractors may be quasi-stable or have slow dynamics")
            insight_49 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        stable = None
        insight_49 = False
        avg_stability = 0.0

    # Save results
    results_dir = Path(__file__).parent / "results" / "longterm_persistence"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle89_longterm_attractor_persistence.json"

    output_data = {
        'experiment': 'cycle89_longterm_attractor_persistence',
        'threshold': threshold,
        'cycles': cycles,
        'checkpoint_interval': checkpoint_interval,
        'test_ranges': [[r[0], r[1]] for r in test_ranges],
        'runs_per_range': runs_per_range,
        'results': results,
        'analysis': {
            'stable': stable,
            'avg_stability': avg_stability
        },
        'insight_49_discovered': insight_49,
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
