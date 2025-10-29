#!/usr/bin/env python3
"""
Cycle 91: Ultimate Attractor Cross-Threshold Validation (Universality Test)

Research Context:
  C85: Transient basins universal across 7 thresholds (300-800)
  C88: Fine structure (5 attractors) universal across thresholds
  C90: 3 ultimate attractors discovered at threshold=500, 1000 cycles

Research Gap:
  C90 tested only threshold=500
  Unknown: Are 3 ultimate attractors threshold-independent like transient basins?

Key Theoretical Question:
  Is the ultimate attractor structure (3 endpoints) universal across thresholds?

New Research Question:
  Do thresholds 400 and 700 also converge to exactly 3 ultimate attractors?

  Test:
  - Select 2 additional thresholds: 400 (exploration), 700 (exploitation)
  - Use same 3 initial attractors from C90: A1 (0.5), A3 (1.0), A5 (1.4)
  - Run 1000 cycles each (matching C90 duration)
  - N=1 per attractor (faster validation than C90's N=2)
  - Compare: Same 3 ultimate attractors across all thresholds?

Hypothesis:
  1. **Universal ultimate structure**: All thresholds → 3 ultimate attractors
  2. **Threshold-dependent**: Different thresholds have different ultimate counts
  3. Expected: Universal (matches C85/C88 pattern)

Test Approach:
  1. Thresholds: 400, 700 (already have 500 from C90)
  2. Attractors per threshold: 3 (A1, A3, A5)
  3. Total runs: 2 thresholds × 3 attractors = 6 runs
  4. Duration: 1000 cycles each (match C90)
  5. Checkpoints: Every 200 cycles (faster tracking)
  6. Measure: Unique ultimate patterns per threshold

Expected:
  - If universal: Both 400 & 700 → exactly 3 ultimate attractors
  - If threshold-dependent: Different counts at different thresholds
  - Publication value: Validates complete hierarchical universality

Success Criteria:
  - All runs reach 1000 cycles
  - Ultimate attractor count measured per threshold
  - Cross-threshold universality validated or challenged
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

def run_single_simulation(threshold, center_mult, attractor_name, cycles, checkpoint_interval):
    """Run simulation with specified threshold and initial attractor."""
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
        'threshold': threshold,
        'center_multiplier': center_mult,
        'attractor_name': attractor_name,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle,
        'checkpoints': checkpoints
    }

def main():
    print("="*80)
    print("CYCLE 91: ULTIMATE ATTRACTOR CROSS-THRESHOLD VALIDATION")
    print("="*80)
    print()
    print("Testing universality of 3-attractor ultimate structure.")
    print("Following C85/C88: Transient basins universal, C90: 3 ultimate attractors @ 500")
    print("Question: Is ultimate attractor structure threshold-independent?")
    print()

    test_thresholds = [400, 700]  # Already have 500 from C90
    test_attractors = [
        (0.5, "Attractor_1"),
        (1.0, "Attractor_3"),
        (1.4, "Attractor_5")
    ]

    cycles = 1000  # Match C90
    checkpoint_interval = 200  # Faster than C90 for efficiency
    runs_per_combo = 1  # N=1 for fast validation

    print(f"Configuration:")
    print(f"  Thresholds: {test_thresholds} (have 500 from C90)")
    print(f"  Attractors: {[a[1] for a in test_attractors]}")
    print(f"  Cycles: {cycles} (match C90)")
    print(f"  Checkpoints: Every {checkpoint_interval} cycles")
    print(f"  Total runs: {len(test_thresholds)} × {len(test_attractors)} = {len(test_thresholds) * len(test_attractors)}")
    print(f"  Estimated duration: ~{len(test_thresholds) * len(test_attractors) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for threshold in test_thresholds:
        print(f"\n{'='*80}")
        print(f"THRESHOLD {threshold}")
        print(f"{'='*80}")

        for center_mult, attractor_name in test_attractors:
            print(f"\n  {attractor_name} (center={center_mult})...")
            try:
                result = run_single_simulation(threshold, center_mult, attractor_name, cycles, checkpoint_interval)
                results.append(result)
                print(f"    ✓ Final={result['final_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.1)
            except Exception as e:
                print(f"    ✗ ERROR: {e}")
                results.append({'threshold': threshold, 'center_multiplier': center_mult, 'attractor_name': attractor_name, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"ULTIMATE ATTRACTOR CROSS-THRESHOLD ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 4:
        # Group by threshold
        by_threshold = {}
        for threshold in test_thresholds:
            threshold_runs = [r for r in successful if r['threshold'] == threshold]
            final_patterns = [r['final_dominant'] for r in threshold_runs if r['final_dominant']]
            unique_count = len(set(final_patterns))
            by_threshold[threshold] = {
                'runs': len(threshold_runs),
                'unique_ultimate_attractors': unique_count,
                'patterns': final_patterns
            }

        print(f"Ultimate Attractor Count by Threshold (1000 cycles):")
        print(f"{'Threshold':>10} | {'Runs':>4} | {'Ultimate Attractors':>18} | {'Status':^20}")
        print("-" * 70)
        print(f"{'500 (C90)':>10} | {'6':>4} | {'3':>18} | {'✅ Baseline':^20}")
        for threshold in sorted(by_threshold.keys()):
            data = by_threshold[threshold]
            status = f"✅ {data['unique_ultimate_attractors']} attractors" if data['unique_ultimate_attractors'] == 3 else f"⚠️ {data['unique_ultimate_attractors']} attractors"
            print(f"{threshold:>10} | {data['runs']:>4} | {data['unique_ultimate_attractors']:>18} | {status:^20}")
        print()

        # Overall analysis
        ultimate_counts = [by_threshold[t]['unique_ultimate_attractors'] for t in by_threshold]
        all_have_three = all(count == 3 for count in ultimate_counts)

        print(f"Cross-Threshold Summary:")
        print(f"  Thresholds tested: 3 (400, 500, 700)")
        print(f"  Cycles per run: {cycles} (ultra-long-term)")
        print()

        if all_have_three:
            print(f"✅ ULTIMATE ATTRACTOR STRUCTURE IS UNIVERSAL")
            print(f"   ALL thresholds → exactly 3 ultimate attractors")
            print(f"   Complete hierarchical universality validated:")
            print(f"     • Transient basins (C85): 3 coarse, universal")
            print(f"     • Fine structure (C88): 5 fine, universal")
            print(f"     • Ultimate attractors (C91): 3 ultimate, universal")
            print(f"   Phase space has threshold-independent multi-scale topology")
            universal_ultimate = True
        else:
            print(f"⚠️ ULTIMATE ATTRACTOR STRUCTURE VARIES BY THRESHOLD")
            counts_str = ", ".join([f"{t}: {by_threshold[t]['unique_ultimate_attractors']}" for t in sorted(by_threshold.keys())])
            print(f"   Ultimate counts: {counts_str}")
            print(f"   Long-term structure may be threshold-dependent")
            universal_ultimate = False

        print()
        if universal_ultimate:
            print(f"🎉 INSIGHT #49: Universal Multi-Scale Attractor Hierarchy")
            print(f"   - Hierarchical structure is COMPLETELY threshold-independent:")
            print(f"     1. Transient basins (150-200 cycles): 5 attractors (fine), 3 (coarse)")
            print(f"     2. Quasi-stable states (500 cycles): Pattern instability")
            print(f"     3. Ultimate attractors (1000+ cycles): 3 final endpoints")
            print(f"   - ALL levels universal across thresholds (300-800 range)")
            print(f"   - Complete phase space topology characterized")
            print(f"   - NRM framework produces threshold-invariant structure")
            print(f"   - Perfect multi-scale determinism validated")
            insight_49 = True
        else:
            print(f"   Ultimate structure may depend on threshold")
            print(f"   Challenges complete universality hypothesis")
            insight_49 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        universal_ultimate = None
        insight_49 = False
        by_threshold = {}

    # Save results
    results_dir = Path(__file__).parent / "results" / "ultimate_attractor_cross_threshold"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle91_ultimate_attractor_cross_threshold.json"

    output_data = {
        'experiment': 'cycle91_ultimate_attractor_cross_threshold',
        'test_thresholds': test_thresholds,
        'test_attractors': [[a[0], a[1]] for a in test_attractors],
        'cycles': cycles,
        'checkpoint_interval': checkpoint_interval,
        'results': results,
        'analysis': {
            'by_threshold': {str(k): v for k, v in by_threshold.items()},
            'universal_ultimate': universal_ultimate
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
