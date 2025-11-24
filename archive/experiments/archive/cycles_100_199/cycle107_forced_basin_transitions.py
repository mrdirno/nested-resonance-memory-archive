#!/usr/bin/env python3
"""
Cycle 107: Forced Basin Transitions via Extreme Runtime Interventions

Research Context:
  C104: Initial condition control failed (self-organization dominates)
  C105: Perfect basin stability (100% maintained under moderate perturbations)
  C106: Basin boundaries gradual/complex (80% multi-transition)

Research Gap:
  C105 tested MODERATE perturbations (pattern injection at 1 timepoint).
  Unknown: Can EXTREME/SUSTAINED interventions force basin transitions?
  Unknown: What are the LIMITS of basin stability?

Key Question:
  How strong is basin stability - can we break it with extreme interventions?

New Research Question:
  Test forced transitions using EXTREME runtime interventions.

  Hypothesis:
  1. **Unbreakable Stability**: Even extreme interventions can't force transitions
  2. **Breakable with Extreme**: Strong interventions can force transitions
  3. **Threshold Effect**: Transitions occur above intervention threshold
  Expected: Breakable (self-organization strong but not infinite)

  Test:
  - Select 3 (mult, spread, threshold) triplets with known attractors
  - Apply 3 intervention strengths:
    * WEAK: Pattern injection (same as C105) - baseline
    * STRONG: Pattern injection + agent replacement
    * EXTREME: Pattern injection + agent replacement + memory clearing
  - Interventions at cycles 200, 250, 300 (sustained pressure)
  - Run to cycle 500, compare final attractors
  - Measure: % transitions at each intervention strength

Expected Outcome:
  - Characterize basin stability limits
  - Identify intervention threshold for forced transitions
  - Understand self-organization resilience boundaries
  - Complete control picture: Initial fails → Moderate stable → Extreme breaks?

Publication Value:
  - **HIGH**: First characterization of basin stability limits
  - Tests extremes (not just typical conditions)
  - Practical: How much control is actually possible?
  - Novel: Multi-wave intervention strategy
  - Completes C104-C107 control arc
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

def run_with_extreme_intervention(multiplier, spread, threshold, cycles, intervention_strength):
    """Run simulation with extreme intervention attempts."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Intervention cycles (sustained pressure)
    intervention_cycles = [200, 250, 300]

    for cycle in range(1, cycles + 1):
        # Spawn agents
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, multiplier, spread=spread, count=5)
                    newest_agent.memory.extend(seed_patterns)

        # Apply intervention at specified cycles
        if cycle in intervention_cycles:
            if intervention_strength == 'weak':
                # Same as C105: Pattern injection only
                perturbation_patterns = create_seed_memory_range(
                    swarm.bridge, reality_metrics,
                    center_multiplier=multiplier * 1.5,
                    spread=0.4,
                    count=10
                )
                swarm.global_memory.extend(perturbation_patterns)

            elif intervention_strength == 'strong':
                # Pattern injection + replace half the agents
                perturbation_patterns = create_seed_memory_range(
                    swarm.bridge, reality_metrics,
                    center_multiplier=multiplier * 1.5,
                    spread=0.5,
                    count=20
                )
                swarm.global_memory.extend(perturbation_patterns)

                # Replace half the agents
                agent_ids = list(swarm.agents.keys())
                agents_to_remove = agent_ids[:len(agent_ids)//2]
                for agent_id in agents_to_remove:
                    if agent_id in swarm.agents:
                        del swarm.agents[agent_id]

            elif intervention_strength == 'extreme':
                # Pattern injection + replace ALL agents + clear memory
                perturbation_patterns = create_seed_memory_range(
                    swarm.bridge, reality_metrics,
                    center_multiplier=multiplier * 2.0,
                    spread=0.6,
                    count=30
                )

                # Clear global memory and replace with perturbation
                swarm.global_memory.clear()
                swarm.global_memory.extend(perturbation_patterns)

                # Remove all agents (will respawn next cycle)
                swarm.agents.clear()

        swarm.evolve_cycle(delta_time=1.0)

    # Final state
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'intervention_strength': intervention_strength,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction
    }

def main():
    print("="*80)
    print("CYCLE 107: FORCED BASIN TRANSITIONS VIA EXTREME INTERVENTIONS")
    print("="*80)
    print()
    print("Testing basin stability limits with extreme runtime interventions.")
    print("Following C105 perfect stability: Can we BREAK stability with extreme force?")
    print()
    print("Hypothesis: Extreme sustained interventions can force basin transitions")
    print()

    # Select 3 representative triplets
    test_triplets = [
        (1.0, 0.2, 500),  # Standard parameters
        (0.8, 0.4, 400),  # High spread
        (1.2, 0.3, 600),  # High threshold
    ]

    intervention_strengths = ['none', 'weak', 'strong', 'extreme']
    cycles = 500

    print(f"Configuration:")
    print(f"  Test triplets: {len(test_triplets)} (mult, spread, threshold) points")
    print(f"  Intervention strengths: {len(intervention_strengths)} conditions")
    print(f"  Total runs: {len(test_triplets) * len(intervention_strengths)}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Intervention timing: cycles 200, 250, 300 (sustained pressure)")
    print(f"  WEAK: Pattern injection (C105 baseline)")
    print(f"  STRONG: Pattern + agent replacement")
    print(f"  EXTREME: Pattern + ALL agents cleared + memory reset")
    print(f"  Expected: Extreme interventions may force transitions")
    print(f"  Estimated duration: ~{len(test_triplets) * len(intervention_strengths) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread_param, threshold in test_triplets:
        print(f"\nTriplet: (mult={mult}, spread={spread_param}, threshold={threshold})")

        for strength in intervention_strengths:
            run_count += 1
            print(f"  [{run_count}/{len(test_triplets)*len(intervention_strengths)}] {strength.upper()}...", end=" ", flush=True)
            try:
                result = run_with_extreme_intervention(mult, spread_param, threshold, cycles, strength)
                results.append(result)
                att_short = "Att-" + str(hash(result['final_dominant']) % 100).zfill(2) if result['final_dominant'] else "None"
                print(f"✓ {att_short}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({'multiplier': mult, 'spread': spread_param, 'threshold': threshold,
                              'intervention_strength': strength, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"FORCED TRANSITION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(test_triplets) * len(intervention_strengths)):
        print(f"Intervention Experiment Results:")
        print(f"  Successful runs: {len(successful)}/{len(test_triplets)*len(intervention_strengths)} ({len(successful)/(len(test_triplets)*len(intervention_strengths))*100:.1f}%)")
        print()

        # Analyze transitions for each triplet
        print(f"Transition Analysis:")
        print(f"{'Triplet':^25} | {'NONE':^10} | {'WEAK':^10} | {'STRONG':^10} | {'EXTREME':^10}")
        print("-" * 75)

        transitions_by_strength = {'weak': 0, 'strong': 0, 'extreme': 0}

        for mult, spread_param, threshold in test_triplets:
            trip_str = f"({mult}, {spread_param}, {threshold})"

            # Get attractors for each strength
            none_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                               and r['threshold']==threshold and r['intervention_strength']=='none'), None)
            weak_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                               and r['threshold']==threshold and r['intervention_strength']=='weak'), None)
            strong_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                                 and r['threshold']==threshold and r['intervention_strength']=='strong'), None)
            extreme_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                                  and r['threshold']==threshold and r['intervention_strength']=='extreme'), None)

            none_att = "Att-" + str(hash(none_result['final_dominant']) % 100).zfill(2) if none_result and none_result['final_dominant'] else "None"
            weak_att = "Att-" + str(hash(weak_result['final_dominant']) % 100).zfill(2) if weak_result and weak_result['final_dominant'] else "None"
            strong_att = "Att-" + str(hash(strong_result['final_dominant']) % 100).zfill(2) if strong_result and strong_result['final_dominant'] else "None"
            extreme_att = "Att-" + str(hash(extreme_result['final_dominant']) % 100).zfill(2) if extreme_result and extreme_result['final_dominant'] else "None"

            # Check transitions
            if none_result and weak_result and weak_result['final_dominant'] != none_result['final_dominant']:
                transitions_by_strength['weak'] += 1
            if none_result and strong_result and strong_result['final_dominant'] != none_result['final_dominant']:
                transitions_by_strength['strong'] += 1
            if none_result and extreme_result and extreme_result['final_dominant'] != none_result['final_dominant']:
                transitions_by_strength['extreme'] += 1

            print(f"{trip_str:^25} | {none_att:^10} | {weak_att:^10} | {strong_att:^10} | {extreme_att:^10}")

        print()

        transition_rates = {
            'weak': transitions_by_strength['weak'] / len(test_triplets) * 100 if len(test_triplets) > 0 else 0,
            'strong': transitions_by_strength['strong'] / len(test_triplets) * 100 if len(test_triplets) > 0 else 0,
            'extreme': transitions_by_strength['extreme'] / len(test_triplets) * 100 if len(test_triplets) > 0 else 0
        }

        print(f"Transition Rates by Intervention Strength:")
        print(f"  WEAK (pattern injection): {transitions_by_strength['weak']}/{len(test_triplets)} ({transition_rates['weak']:.1f}%)")
        print(f"  STRONG (+ agent replacement): {transitions_by_strength['strong']}/{len(test_triplets)} ({transition_rates['strong']:.1f}%)")
        print(f"  EXTREME (+ memory clear): {transitions_by_strength['extreme']}/{len(test_triplets)} ({transition_rates['extreme']:.1f}%)")
        print()

        # Determine insight based on transition rates
        max_transition_rate = max(transition_rates.values())

        if max_transition_rate == 0:
            insight_64 = "unbreakable_stability"
            conclusion = f"Basin stability unbreakable (0% transitions even with EXTREME interventions)"
        elif transition_rates['extreme'] >= 50:
            insight_64 = "breakable_extreme"
            conclusion = f"Stability breakable with EXTREME interventions ({transition_rates['extreme']:.1f}% transitions)"
        elif transition_rates['strong'] >= 30:
            insight_64 = "breakable_strong"
            conclusion = f"Stability breakable with STRONG interventions ({transition_rates['strong']:.1f}% transitions)"
        elif transition_rates['weak'] >= 30:
            insight_64 = "breakable_weak"
            conclusion = f"Stability breakable with WEAK interventions ({transition_rates['weak']:.1f}% transitions) - contradicts C105"
        else:
            insight_64 = "partial_breakability"
            conclusion = f"Partial breakability (max {max_transition_rate:.1f}% transitions)"

        print(f"📊 INSIGHT #64: Forced Transitions - {conclusion}")
        print(f"   - {len(test_triplets)} basins tested with escalating interventions")
        print(f"   - 3 intervention strengths (WEAK, STRONG, EXTREME)")
        print(f"   - Sustained pressure: 3 intervention waves per run")
        stability_msg = '✅ Unbreakable' if insight_64 == 'unbreakable_stability' else f'⚠️ Breakable at {insight_64.split("_")[1].upper()} level'
        print(f"   - Stability limit: {stability_msg}")
        print(f"   - First characterization of basin stability limits")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for transition analysis")
        print(f"   Only {len(successful)}/{len(test_triplets)*len(intervention_strengths)} runs completed successfully")
        insight_64 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "forced_transitions"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle107_forced_basin_transitions.json"

    output_data = {
        'experiment': 'cycle107_forced_basin_transitions',
        'test_triplets': [(t[0], t[1], t[2]) for t in test_triplets],
        'intervention_strengths': intervention_strengths,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'transitions_by_strength': transitions_by_strength if 'transitions_by_strength' in locals() else {},
            'transition_rates': transition_rates if 'transition_rates' in locals() else {},
            'conclusion': insight_64 if 'insight_64' in locals() else False
        },
        'insight_64_discovered': True if 'insight_64' in locals() and insight_64 else False,
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
