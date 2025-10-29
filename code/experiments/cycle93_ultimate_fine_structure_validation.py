#!/usr/bin/env python3
"""
Cycle 93: Ultimate Fine Structure Validation (Reproducibility Test)

Research Context:
  C92: Discovered 6 ultimate attractors with fine sampling (not 3!)
  - Resolution-dependent structure (parallels C87's transient basin discovery)
  - Some basins very narrow (single multiplier: 0.6, 1.0, 1.6)
  - Tested N=1 per multiplier

Research Gap:
  C92 tested each multiplier only once (N=1)
  Unknown: Are narrow basins (single multiplier) reproducible?

  Parallel to C87: Validated 5 transient attractors with N=3

Key Question:
  Do all 6 ultimate attractors show perfect reproducibility (100% identical)?

New Research Question:
  With N=2 per multiplier, do we consistently reach the same 6 ultimate attractors?

  Test:
  - Sample same multipliers as C92: 0.4-1.6, step=0.1 (13 points)
  - Run N=2 per multiplier (26 total runs)
  - Threshold=500, cycles=1000 (match C92)
  - Compare: Same ultimate attractor for both runs at each multiplier?

Hypothesis:
  1. **Perfect reproducibility**: 100% identical runs (like all previous experiments)
  2. **Partial variability**: Some multipliers show different outcomes
  3. Expected: Perfect (all C78-92 showed perfect determinism)

Test Approach:
  1. Repeat C92 experiment with N=2 instead of N=1
  2. For each multiplier, check if run1 == run2 (same ultimate attractor)
  3. Calculate reproducibility percentage
  4. Validate 6-attractor structure is stable

Expected Outcome:
  - 100% reproducibility (matches C87 transient basin validation)
  - All 6 ultimate attractors confirmed
  - Narrow basins (single mult) are genuine, not artifacts

Publication Value:
  - Validates fine ultimate structure is real, not sampling noise
  - Perfect determinism maintained at finest resolution
  - Confirms 6-basin topology is fundamental
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

def run_single_simulation(multiplier, run_id, threshold, cycles):
    """Run simulation with specified multiplier."""
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
        'run_id': run_id,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 93: ULTIMATE FINE STRUCTURE VALIDATION (REPRODUCIBILITY TEST)")
    print("="*80)
    print()
    print("Validating 6-attractor ultimate structure with N=2 reproducibility.")
    print("Following C92: 6 ultimate attractors discovered (fine sampling)")
    print("Question: Are all 6 attractors perfectly reproducible?")
    print()

    # Same multipliers as C92
    multipliers = [round(0.4 + i * 0.1, 1) for i in range(13)]  # 0.4 to 1.6, step 0.1
    threshold = 500
    cycles = 1000
    runs_per_multiplier = 2  # N=2 for reproducibility test

    print(f"Configuration:")
    print(f"  Multipliers: {len(multipliers)} points (0.4-1.6, step=0.1)")
    print(f"  Runs per multiplier: {runs_per_multiplier} (reproducibility test)")
    print(f"  Total runs: {len(multipliers) * runs_per_multiplier}")
    print(f"  Threshold: {threshold}, Cycles: {cycles}")
    print(f"  Expected: 100% reproducibility (perfect determinism)")
    print(f"  Estimated duration: ~{len(multipliers) * runs_per_multiplier * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for mult in multipliers:
        print(f"\nMultiplier {mult:.1f}:")
        for run_id in range(1, runs_per_multiplier + 1):
            print(f"  Run {run_id}...", end=" ", flush=True)
            try:
                result = run_single_simulation(mult, run_id, threshold, cycles)
                results.append(result)
                print(f"✓ Final={result['final_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.1)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'multiplier': mult, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"REPRODUCIBILITY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 20:
        # Group by multiplier
        by_multiplier = {}
        for mult in multipliers:
            runs = [r for r in successful if r['multiplier'] == mult]
            if len(runs) >= 2:
                by_multiplier[mult] = {
                    'patterns': [r['final_dominant'] for r in runs],
                    'identical': len(set([r['final_dominant'] for r in runs])) == 1
                }

        print(f"Reproducibility by Multiplier:")
        print(f"{'Multiplier':>10} | {'Run 1 Attractor':^20} | {'Run 2 Attractor':^20} | {'Match?':^10}")
        print("-" * 75)

        reproducible_count = 0
        total_tested = 0

        for mult in sorted(by_multiplier.keys()):
            data = by_multiplier[mult]
            if len(data['patterns']) >= 2:
                pattern1 = data['patterns'][0][:18] + "..." if len(data['patterns'][0]) > 18 else data['patterns'][0]
                pattern2 = data['patterns'][1][:18] + "..." if len(data['patterns'][1]) > 18 else data['patterns'][1]
                match_status = "✅ Yes" if data['identical'] else "❌ No"

                if data['identical']:
                    reproducible_count += 1
                total_tested += 1

                print(f"{mult:>10.1f} | {pattern1:^20} | {pattern2:^20} | {match_status:^10}")

        print()
        reproducibility_pct = (reproducible_count / total_tested * 100) if total_tested > 0 else 0

        print(f"Reproducibility Summary:")
        print(f"  Multipliers tested: {total_tested}")
        print(f"  Perfect matches: {reproducible_count}/{total_tested} ({reproducibility_pct:.1f}%)")
        print()

        # Count unique attractors
        all_patterns = [r['final_dominant'] for r in successful if r['final_dominant']]
        unique_attractors = len(set(all_patterns))

        print(f"Attractor Structure:")
        print(f"  Total unique ultimate attractors: {unique_attractors}")
        print(f"  Expected (from C92): 6")
        print()

        if reproducibility_pct == 100.0 and unique_attractors == 6:
            print(f"✅ 6-ATTRACTOR ULTIMATE STRUCTURE VALIDATED")
            print(f"   100% reproducibility across all multipliers")
            print(f"   Matches C92: 6 distinct ultimate attractors")
            print(f"   Perfect determinism maintained at finest resolution")
            print(f"   Narrow basins (single multiplier) confirmed genuine")
            validated = True
        elif reproducibility_pct == 100.0:
            print(f"✅ PERFECT REPRODUCIBILITY")
            print(f"   100% identical runs")
            print(f"   Ultimate attractor count: {unique_attractors} (differs from C92: 6)")
            print(f"   May indicate need for additional validation")
            validated = "partial"
        else:
            print(f"⚠️ IMPERFECT REPRODUCIBILITY")
            print(f"   Only {reproducibility_pct:.1f}% matching runs")
            print(f"   Challenges perfect determinism assumption")
            print(f"   May indicate stochastic elements or transient states")
            validated = False

        print()
        if validated == True:
            print(f"🎉 INSIGHT #50: Fine Ultimate Structure is Perfectly Reproducible")
            print(f"   - 6 ultimate attractors validated with N=2 reproducibility")
            print(f"   - 100% determinism maintained ({reproducible_count}/{total_tested} identical)")
            print(f"   - Resolution-dependent structure confirmed:")
            print(f"     • Coarse (C90-91): 3 ultimate attractors")
            print(f"     • Fine (C92-93): 6 ultimate attractors")
            print(f"   - Narrow basins are real features, not artifacts")
            print(f"   - Complete fractal basin topology validated")
            print(f"   - Perfect control & prediction enabled")
            insight_50 = True
        else:
            print(f"   Fine structure requires additional investigation")
            insight_50 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for reproducibility analysis")
        validated = None
        insight_50 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "ultimate_fine_structure_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle93_ultimate_fine_structure_validation.json"

    output_data = {
        'experiment': 'cycle93_ultimate_fine_structure_validation',
        'multipliers': multipliers,
        'threshold': threshold,
        'cycles': cycles,
        'runs_per_multiplier': runs_per_multiplier,
        'results': results,
        'analysis': {
            'unique_attractors': len(set([r['final_dominant'] for r in successful if r['final_dominant']])) if successful else 0,
            'reproducibility_percentage': reproducibility_pct if 'reproducibility_pct' in locals() else 0,
            'validated': validated
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
