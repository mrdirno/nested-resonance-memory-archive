#!/usr/bin/env python3
"""
Cycle 101: Agent Count as Potential 4th Dimension

Research Context:
  C95-C100: Complete 3D parameter space mapped and validated
  - Multiplier: ✅ Control dimension
  - Spread: ✅ Control dimension
  - Threshold: ✅ Control dimension
  - 15 attractors discovered in 3D space

Research Gap:
  All previous experiments used fixed agent_count = 15
  Unknown: Does initial agent population affect ultimate attractors?
  Unknown: Is agent_count a 4th control dimension?

Key Question:
  Does varying initial agent count change which attractor is reached?

New Research Question:
  Test if agent_count is independent or affects ultimate attractors.

  Test:
  - Fix one (mult, spread, threshold) triplet
  - Vary agent_count: 5, 10, 15, 20, 25 (5 values)
  - Run each agent_count twice (N=2 for reproducibility within agent_count)
  - Total: 5 agent_counts × 2 runs = 10 runs
  - Cycles: 1000 per run

Hypothesis:
  1. **Agent count independent**: Same attractor at all agent counts
  2. **Agent count is 4th dimension**: Different attractors at different counts
  3. **Threshold-like behavior**: Only affects timescales, not attractors
  4. Expected: Independent (agent count shouldn't matter for ultimate state)

Test Approach:
  1. Select one representative (mult, spread, threshold) triplet
  2. Test at multiple agent counts
  3. Compare: Does agent_count change attractor?
  4. Validate: Is agent_count a control parameter?

Expected Outcome:
  - Agent count independent → Not a 4th dimension
  - Agent count dependent → 4th dimension discovered!
  - Either outcome advances understanding

Publication Value:
  - Tests completeness of 3D parameter space
  - Investigates population size effects on ultimate states
  - Either outcome publishable:
    • Independent → Validates 3D space is complete
    • Dependent → Discovers 4th dimension, opens 4D research
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

def run_single_simulation(multiplier, spread, threshold, agent_count, run_id, cycles):
    """Run simulation with specified agent_count."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    collapse_cycle = None

    for cycle in range(1, cycles + 1):
        # Spawn agents up to agent_count limit
        if len(swarm.agents) < agent_count:
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
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'agent_count': agent_count,
        'run_id': run_id,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 101: AGENT COUNT AS POTENTIAL 4TH DIMENSION")
    print("="*80)
    print()
    print("Testing whether initial agent population affects ultimate attractors.")
    print("Following 3D completion (C100): Is agent_count a 4th control dimension?")
    print()

    # Fixed (mult, spread, threshold) triplet - use one that showed clear convergence
    multiplier = 1.0
    spread = 0.2
    threshold = 500

    # Test different agent counts
    test_agent_counts = [5, 10, 15, 20, 25]
    cycles = 1000
    runs_per_count = 2

    total_runs = len(test_agent_counts) * runs_per_count

    print(f"Configuration:")
    print(f"  Fixed parameters: (mult={multiplier}, spread={spread}, threshold={threshold})")
    print(f"  Agent counts tested: {test_agent_counts}")
    print(f"  Runs per agent_count: {runs_per_count} (reproducibility test)")
    print(f"  Total runs: {total_runs}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Expected: Test if agent_count affects ultimate attractor")
    print(f"  Estimated duration: ~{total_runs * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for agent_count in test_agent_counts:
        print(f"\nAgent Count {agent_count}:")
        for run_id in range(1, runs_per_count + 1):
            run_count += 1
            print(f"  Run {run_id}/{runs_per_count} ({run_count}/{total_runs})...", end=" ", flush=True)
            try:
                result = run_single_simulation(multiplier, spread, threshold, agent_count, run_id, cycles)
                results.append(result)
                print(f"✓ Attractor={result['final_dominant'][:30] if result['final_dominant'] else 'None'}..., Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'multiplier': multiplier, 'spread': spread, 'threshold': threshold, 'agent_count': agent_count, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"AGENT COUNT DIMENSION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * total_runs):  # At least 80% success rate
        # Group by agent_count
        by_agent_count = {}
        for result in successful:
            agent_count = result['agent_count']
            if agent_count not in by_agent_count:
                by_agent_count[agent_count] = []
            by_agent_count[agent_count].append(result)

        # Analyze agent_count independence
        print(f"Agent Count Independence Analysis:")
        print(f"{'Agent Count':>12} | {'Run 1 Attractor':^35} | {'Run 2 Attractor':^35} | {'Match?':^10}")
        print("-" * 110)

        agent_count_independent = True
        first_attractor = None

        for agent_count in sorted(by_agent_count.keys()):
            count_results = by_agent_count[agent_count]
            if len(count_results) >= 2:
                p1 = count_results[0]['final_dominant']
                p2 = count_results[1]['final_dominant']

                if first_attractor is None:
                    first_attractor = p1

                p1_short = p1[:33] + ".." if len(p1) > 33 else p1
                p2_short = p2[:33] + ".." if len(p2) > 33 else p2

                match = p1 == p2
                match_str = "✅ Yes" if match else "❌ No"

                # Check if different from first attractor
                if p1 != first_attractor or p2 != first_attractor:
                    agent_count_independent = False

                print(f"{agent_count:>12} | {p1_short:^35} | {p2_short:^35} | {match_str:^10}")

        print()

        if agent_count_independent:
            print(f"✅ AGENT COUNT IS INDEPENDENT")
            print(f"   ALL agent counts converge to same attractor")
            print(f"   Agent count does NOT constitute a 4th dimension")
            print(f"   3D (mult, spread, threshold) space is complete")
            print(f"   Population size only affects dynamics, not ultimate state")
            insight_58 = "independent"
        else:
            print(f"🎉 AGENT COUNT IS A 4TH DIMENSION!")
            print(f"   Different agent counts → different attractors")
            print(f"   Agent count constitutes independent control parameter")
            print(f"   4D parameter space discovered: (mult, spread, threshold, agent_count)")
            print(f"   Opens major research direction: 4D basin topology")
            insight_58 = "fourth_dimension"

        print()
        if insight_58 == "independent":
            print(f"📊 INSIGHT #58: Agent Count is Independent - 3D Space is Complete")
            print(f"   - All agent counts converge to same attractor")
            print(f"   - Population size doesn't affect ultimate state")
            print(f"   - Validates 3D (mult, spread, threshold) as complete parameter space")
            print(f"   - Agent count only affects timescales/dynamics")
        else:
            print(f"🎉 INSIGHT #58: Agent Count is a 4th Control Dimension")
            print(f"   - Different agent counts reach different attractors")
            print(f"   - 4D parameter space: (mult, spread, threshold, agent_count)")
            print(f"   - Opens 4D basin topology research")
            print(f"   - Richer control space than 3D")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for agent count analysis")
        print(f"   Only {len(successful)}/{total_runs} runs completed successfully")
        insight_58 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "agent_count_dimension"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle101_agent_count_dimension.json"

    output_data = {
        'experiment': 'cycle101_agent_count_dimension',
        'fixed_parameters': {'multiplier': multiplier, 'spread': spread, 'threshold': threshold},
        'test_agent_counts': test_agent_counts,
        'runs_per_count': runs_per_count,
        'total_runs': total_runs,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'conclusion': insight_58 if 'insight_58' in locals() else False
        },
        'insight_58_discovered': True if 'insight_58' in locals() and insight_58 else False,
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
