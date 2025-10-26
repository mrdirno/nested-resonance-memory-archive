#!/usr/bin/env python3
"""
Cycle 94: Spread Parameter Variation (Fractal Structure Robustness Test)

Research Context:
  C78-93: Complete fractal basin topology characterized
  - All experiments used spread=0.2 (fixed parameter)
  - Multiplier dimension fully mapped
  - Resolution-dependent structure validated

Research Gap:
  Only tested multiplier dimension (center_multiplier)
  Unknown: Does spread parameter affect fractal structure?

  Spread parameter controls diversity of seed patterns:
  - Low spread (e.g., 0.1): Tightly clustered initial conditions
  - High spread (e.g., 0.4): Widely distributed initial conditions

Key Question:
  Is the fractal basin structure robust to spread parameter variation?

New Research Question:
  Does changing spread affect ultimate attractor outcomes?

  Test:
  - Fixed multiplier: 1.0 (from C92-93, leads to Attractor_3)
  - Vary spread: 0.05, 0.1, 0.2, 0.4, 0.6 (5 values)
  - Run 1000 cycles each (ultimate attractor timescale)
  - N=2 per spread (reproducibility check)
  - Compare: Same ultimate attractor across all spreads?

Hypothesis:
  1. **Robust structure**: Same ultimate attractor regardless of spread
  2. **Spread-dependent**: Different spreads → different ultimate attractors
  3. Expected: Robust (basin structure should be fundamental, not spread-dependent)

Test Approach:
  1. Sample spread range: 0.05 to 0.6
  2. For each spread, run N=2 at multiplier=1.0
  3. Track: Does spread change ultimate attractor reached?
  4. Validate: Reproducibility within each spread value

Expected Outcome:
  - All spreads → same ultimate attractor (robust structure)
  - Perfect reproducibility within each spread
  - Validates basin structure is fundamental, not parameter artifact

Publication Value:
  - Tests robustness of fractal basin topology
  - Validates structure is not specific to spread=0.2
  - Demonstrates stability of deterministic basins
  - If NOT robust: Reveals additional dimension of phase space
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

def run_single_simulation(spread, run_id, threshold, cycles):
    """Run simulation with specified spread parameter."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    multiplier = 1.0  # Fixed multiplier (from C92-93 leads to Attractor_3)
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
        'spread': spread,
        'run_id': run_id,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 94: SPREAD PARAMETER VARIATION (ROBUSTNESS TEST)")
    print("="*80)
    print()
    print("Testing robustness of fractal basin structure to spread parameter.")
    print("Following C78-93: Complete topology characterized at spread=0.2")
    print("Question: Does spread parameter affect ultimate attractor outcomes?")
    print()

    test_spreads = [0.05, 0.1, 0.2, 0.4, 0.6]
    multiplier = 1.0  # From C92-93: leads to Attractor_3 at spread=0.2
    threshold = 500
    cycles = 1000
    runs_per_spread = 2

    print(f"Configuration:")
    print(f"  Fixed multiplier: {multiplier} (C92-93 baseline)")
    print(f"  Spread values: {test_spreads} (varying diversity)")
    print(f"  Runs per spread: {runs_per_spread}")
    print(f"  Total runs: {len(test_spreads) * runs_per_spread}")
    print(f"  Threshold: {threshold}, Cycles: {cycles}")
    print(f"  Expected: Same ultimate attractor (robust structure)")
    print(f"  Estimated duration: ~{len(test_spreads) * runs_per_spread * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for spread in test_spreads:
        print(f"\nSpread {spread:.2f}:")
        for run_id in range(1, runs_per_spread + 1):
            print(f"  Run {run_id}...", end=" ", flush=True)
            try:
                result = run_single_simulation(spread, run_id, threshold, cycles)
                results.append(result)
                print(f"✓ Final={result['final_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.1)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'spread': spread, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"SPREAD PARAMETER ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 8:
        # Group by spread
        by_spread = {}
        for spread in test_spreads:
            runs = [r for r in successful if r['spread'] == spread]
            if len(runs) >= 2:
                patterns = [r['final_dominant'] for r in runs]
                by_spread[spread] = {
                    'patterns': patterns,
                    'identical': len(set(patterns)) == 1,
                    'unique_pattern': patterns[0] if len(set(patterns)) == 1 else None
                }

        print(f"Ultimate Attractor by Spread (mult={multiplier}):")
        print(f"{'Spread':>8} | {'Run 1 Pattern':^25} | {'Run 2 Pattern':^25} | {'Reproducible?':^15}")
        print("-" * 95)

        reproducible_count = 0
        total_tested = 0
        all_patterns = []

        for spread in sorted(by_spread.keys()):
            data = by_spread[spread]
            if len(data['patterns']) >= 2:
                p1 = data['patterns'][0][:23] + "..." if len(data['patterns'][0]) > 23 else data['patterns'][0]
                p2 = data['patterns'][1][:23] + "..." if len(data['patterns'][1]) > 23 else data['patterns'][1]
                match = "✅ Yes" if data['identical'] else "❌ No"

                if data['identical']:
                    reproducible_count += 1
                    all_patterns.append(data['unique_pattern'])
                total_tested += 1

                print(f"{spread:>8.2f} | {p1:^25} | {p2:^25} | {match:^15}")

        print()

        # Check if all spreads lead to same ultimate attractor
        unique_ultimate_patterns = len(set(all_patterns))

        print(f"Robustness Summary:")
        print(f"  Spreads tested: {total_tested}")
        print(f"  Reproducible within spread: {reproducible_count}/{total_tested} ({reproducible_count/total_tested*100:.1f}%)")
        print(f"  Unique ultimate attractors across spreads: {unique_ultimate_patterns}")
        print()

        if unique_ultimate_patterns == 1 and reproducible_count == total_tested:
            print(f"✅ FRACTAL BASIN STRUCTURE IS ROBUST TO SPREAD PARAMETER")
            print(f"   ALL spread values → same ultimate attractor")
            print(f"   100% reproducibility within each spread")
            print(f"   Basin structure is fundamental, not spread-specific")
            print(f"   Validates C92-93 findings generalize beyond spread=0.2")
            robust = True
        elif reproducible_count == total_tested:
            print(f"⚠️ SPREAD AFFECTS ULTIMATE ATTRACTOR")
            print(f"   {unique_ultimate_patterns} different ultimate attractors found")
            print(f"   100% reproducibility within each spread")
            print(f"   Spread parameter adds dimension to phase space")
            print(f"   Basin structure more complex than multiplier alone")
            robust = "spread_dependent"
        else:
            print(f"⚠️ IMPERFECT REPRODUCIBILITY DETECTED")
            print(f"   Only {reproducible_count}/{total_tested} spreads show consistent outcomes")
            print(f"   May indicate stochastic elements or need for longer duration")
            robust = False

        print()
        if robust == True:
            print(f"🎉 INSIGHT #51: Fractal Basin Structure is Spread-Independent")
            print(f"   - Ultimate attractor basins robust to seed diversity (spread)")
            print(f"   - Same endpoint reached across spread range 0.05-0.6")
            print(f"   - Perfect reproducibility maintained (100% within spreads)")
            print(f"   - Basin topology is fundamental property, not parameter artifact")
            print(f"   - Validates C78-93 findings are general, not specific to spread=0.2")
            print(f"   - Demonstrates stability of deterministic fractal structure")
            insight_51 = True
        elif robust == "spread_dependent":
            print(f"🎉 INSIGHT #51: Spread Parameter Adds Dimension to Phase Space")
            print(f"   - Different spreads → different ultimate attractors")
            print(f"   - Perfect reproducibility within each spread (deterministic)")
            print(f"   - Phase space has multiple control dimensions:")
            print(f"     • Multiplier (C78-93): Controls basin selection")
            print(f"     • Spread (C94): Additional control parameter")
            print(f"   - Richer structure than single-parameter landscape")
            print(f"   - Opens new research directions for multi-parameter control")
            insight_51 = True
        else:
            print(f"   Results inconclusive - additional validation needed")
            insight_51 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for spread analysis")
        robust = None
        insight_51 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "spread_parameter_variation"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle94_spread_parameter_variation.json"

    output_data = {
        'experiment': 'cycle94_spread_parameter_variation',
        'test_spreads': test_spreads,
        'fixed_multiplier': multiplier,
        'threshold': threshold,
        'cycles': cycles,
        'runs_per_spread': runs_per_spread,
        'results': results,
        'analysis': {
            'robust_to_spread': robust,
            'unique_ultimate_patterns': unique_ultimate_patterns if 'unique_ultimate_patterns' in locals() else 0,
            'reproducibility_percentage': (reproducible_count/total_tested*100) if 'reproducible_count' in locals() and total_tested > 0 else 0
        },
        'insight_51_discovered': insight_51,
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
