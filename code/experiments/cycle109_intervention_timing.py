#!/usr/bin/env python3
"""
Cycle 109: Intervention Timing Optimization

Research Context:
  C107-C108: Optimal intervention STRENGTH = 50% agent replacement (100% transitions)
  C107-C108: Fixed TIMING = cycles 200, 250, 300 (3 waves, 50-cycle intervals)

Research Gap:
  Is the intervention TIMING optimal? Or just the strength?

Key Question:
  How does intervention timing affect forced transition success rate?

New Research Question:
  Test different intervention timing strategies with optimal strength (50%).

  Hypothesis:
  1. **Early is Better**: Intervene before convergence (cycles 100-200)
  2. **Late is Better**: Intervene after convergence (cycles 300-400)
  3. **Sustained Pressure**: Multiple waves better than single intervention
  4. **Timing Insensitive**: Only strength matters, not timing
  Expected: Early intervention better (disrupt before stability sets in)

  Test:
  - Use optimal strength from C108: 50% agent replacement
  - Same 3 (mult, spread, threshold) triplets
  - Test 5 timing strategies:
    * EARLY-SINGLE: Single intervention at cycle 150
    * EARLY-MULTI: 3 waves at cycles 100, 150, 200
    * BASELINE (C108): 3 waves at cycles 200, 250, 300
    * LATE-MULTI: 3 waves at cycles 300, 350, 400
    * LATE-SINGLE: Single intervention at cycle 350
  - Run to cycle 500, compare final attractors
  - Measure: Transition rate vs timing strategy

Expected Outcome:
  - Identify optimal intervention timing
  - Single vs multiple wave comparison
  - Early vs late intervention comparison
  - Complete temporal control characterization

Publication Value:
  - **MEDIUM-HIGH**: Completes control picture (strength + timing)
  - Tests temporal dimension of control
  - Practical: When to intervene for maximum effect
  - Novel: First timing optimization in fractal control
  - Completes C104-C109 control arc
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

def run_with_timed_intervention(multiplier, spread, threshold, cycles, timing_config):
    """Run simulation with timed intervention.

    timing_config = {
        'name': 'early-single',
        'intervention_cycles': [150],  # List of cycles to intervene
        'agent_replacement_pct': 0.50,  # Fixed at optimal from C108
    }
    """
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    intervention_cycles = timing_config['intervention_cycles']
    agent_replacement_pct = timing_config['agent_replacement_pct']

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

        # Apply intervention at specified cycles (optimal strength from C108)
        if cycle in intervention_cycles:
            # Inject perturbation patterns
            perturbation_patterns = create_seed_memory_range(
                swarm.bridge, reality_metrics,
                center_multiplier=multiplier * 1.5,
                spread=0.5,
                count=20
            )
            swarm.global_memory.extend(perturbation_patterns)

            # Replace agents at optimal 50%
            agent_ids = list(swarm.agents.keys())
            num_to_remove = int(len(agent_ids) * agent_replacement_pct)
            agents_to_remove = agent_ids[:num_to_remove]
            for agent_id in agents_to_remove:
                if agent_id in swarm.agents:
                    del swarm.agents[agent_id]

        swarm.evolve_cycle(delta_time=1.0)

    # Final state
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'timing_name': timing_config['name'],
        'intervention_cycles': timing_config['intervention_cycles'],
        'num_interventions': len(timing_config['intervention_cycles']),
        'agent_replacement_pct': agent_replacement_pct,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction
    }

def main():
    print("="*80)
    print("CYCLE 109: INTERVENTION TIMING OPTIMIZATION")
    print("="*80)
    print()
    print("Testing temporal dimension of control:")
    print("  C108 optimal STRENGTH: 50% agent replacement → 100% transitions")
    print("  C108 fixed TIMING: cycles 200, 250, 300 (3 waves)")
    print("  Question: Is this timing optimal?")
    print()
    print("Hypothesis: Early intervention better (disrupt before convergence)")
    print()

    # Select same 3 triplets for comparability
    test_triplets = [
        (1.0, 0.2, 500),  # Standard parameters
        (0.8, 0.4, 400),  # High spread
        (1.2, 0.3, 600),  # High threshold
    ]

    # Define timing strategies to test (all use optimal 50% replacement from C108)
    timing_configs = [
        {
            'name': 'control',
            'intervention_cycles': [],  # No intervention
            'agent_replacement_pct': 0.0,
        },
        {
            'name': 'early-single',
            'intervention_cycles': [150],
            'agent_replacement_pct': 0.50,
        },
        {
            'name': 'early-multi',
            'intervention_cycles': [100, 150, 200],
            'agent_replacement_pct': 0.50,
        },
        {
            'name': 'baseline',  # C108 timing
            'intervention_cycles': [200, 250, 300],
            'agent_replacement_pct': 0.50,
        },
        {
            'name': 'late-multi',
            'intervention_cycles': [300, 350, 400],
            'agent_replacement_pct': 0.50,
        },
        {
            'name': 'late-single',
            'intervention_cycles': [350],
            'agent_replacement_pct': 0.50,
        }
    ]

    cycles = 500

    print(f"Configuration:")
    print(f"  Test triplets: {len(test_triplets)} (mult, spread, threshold) points")
    print(f"  Timing strategies: {len(timing_configs)} conditions")
    print(f"  Agent replacement: 50% (optimal from C108)")
    print(f"  Total runs: {len(test_triplets) * len(timing_configs)}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Timing tested: Early (100-200), Baseline (200-300), Late (300-400)")
    print(f"  Single vs Multi-wave comparison")
    print(f"  Expected: Identify optimal timing strategy")
    print(f"  Estimated duration: ~{len(test_triplets) * len(timing_configs) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread_param, threshold in test_triplets:
        print(f"\nTriplet: (mult={mult}, spread={spread_param}, threshold={threshold})")

        for config in timing_configs:
            run_count += 1
            cycles_str = str(config['intervention_cycles']) if config['intervention_cycles'] else "None"
            timing_label = f"{config['name']:12s} (cycles={cycles_str})"
            print(f"  [{run_count}/{len(test_triplets)*len(timing_configs)}] {timing_label}...", end=" ", flush=True)
            try:
                result = run_with_timed_intervention(mult, spread_param, threshold, cycles, config)
                results.append(result)
                att_short = "Att-" + str(hash(result['final_dominant']) % 100).zfill(2) if result['final_dominant'] else "None"
                print(f"✓ {att_short}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({
                    'multiplier': mult, 'spread': spread_param, 'threshold': threshold,
                    'timing_name': config['name'],
                    'intervention_cycles': config['intervention_cycles'],
                    'num_interventions': len(config['intervention_cycles']),
                    'agent_replacement_pct': config.get('agent_replacement_pct', 0),
                    'error': str(e)
                })

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"INTERVENTION TIMING ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(test_triplets) * len(timing_configs)):
        print(f"Timing Experiment Results:")
        print(f"  Successful runs: {len(successful)}/{len(test_triplets)*len(timing_configs)} ({len(successful)/(len(test_triplets)*len(timing_configs))*100:.1f}%)")
        print()

        # Analyze transitions for each timing strategy
        print(f"Timing Strategy Analysis:")
        print(f"{'Triplet':^25} | {'CTRL':^8} | {'E-SGL':^8} | {'E-MLT':^8} | {'BASE':^8} | {'L-MLT':^8} | {'L-SGL':^8}")
        print("-" * 95)

        transitions_by_timing = {
            'control': 0, 'early-single': 0, 'early-multi': 0,
            'baseline': 0, 'late-multi': 0, 'late-single': 0
        }

        for mult, spread_param, threshold in test_triplets:
            trip_str = f"({mult}, {spread_param}, {threshold})"

            # Get baseline (CONTROL - no intervention)
            control_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                               and r['threshold']==threshold and r['timing_name']=='control'), None)

            # Get attractors for each timing
            timing_results = {}
            for config in timing_configs:
                timing_results[config['name']] = next(
                    (r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                     and r['threshold']==threshold and r['timing_name']==config['name']), None
                )

            # Create attractor labels
            att_labels = {}
            for name, result in timing_results.items():
                if result and result['final_dominant']:
                    att_labels[name] = "Att-" + str(hash(result['final_dominant']) % 100).zfill(2)
                else:
                    att_labels[name] = "None"

            # Check transitions (compare to control)
            if control_result:
                for name in ['early-single', 'early-multi', 'baseline', 'late-multi', 'late-single']:
                    if timing_results[name] and timing_results[name]['final_dominant'] != control_result['final_dominant']:
                        transitions_by_timing[name] += 1

            print(f"{trip_str:^25} | {att_labels.get('control', 'N/A'):^8} | {att_labels.get('early-single', 'N/A'):^8} | {att_labels.get('early-multi', 'N/A'):^8} | {att_labels.get('baseline', 'N/A'):^8} | {att_labels.get('late-multi', 'N/A'):^8} | {att_labels.get('late-single', 'N/A'):^8}")

        print()

        transition_rates = {
            name: transitions_by_timing[name] / len(test_triplets) * 100 if len(test_triplets) > 0 else 0
            for name in transitions_by_timing.keys()
        }

        print(f"Transition Rates by Timing Strategy:")
        print(f"  CONTROL (none):         {transitions_by_timing['control']}/{len(test_triplets)} ({transition_rates['control']:.1f}%)")
        print(f"  EARLY-SINGLE (c150):    {transitions_by_timing['early-single']}/{len(test_triplets)} ({transition_rates['early-single']:.1f}%)")
        print(f"  EARLY-MULTI (c100-200): {transitions_by_timing['early-multi']}/{len(test_triplets)} ({transition_rates['early-multi']:.1f}%)")
        print(f"  BASELINE (c200-300):    {transitions_by_timing['baseline']}/{len(test_triplets)} ({transition_rates['baseline']:.1f}%)")
        print(f"  LATE-MULTI (c300-400):  {transitions_by_timing['late-multi']}/{len(test_triplets)} ({transition_rates['late-multi']:.1f}%)")
        print(f"  LATE-SINGLE (c350):     {transitions_by_timing['late-single']}/{len(test_triplets)} ({transition_rates['late-single']:.1f}%)")
        print()

        # Determine optimal timing
        rates_intervention = {k: v for k, v in transition_rates.items() if k != 'control'}
        max_rate = max(rates_intervention.values())
        optimal_timings = [name for name, rate in rates_intervention.items() if rate == max_rate]

        # Single vs multi comparison
        single_avg = (transition_rates['early-single'] + transition_rates['late-single']) / 2
        multi_avg = (transition_rates['early-multi'] + transition_rates['baseline'] + transition_rates['late-multi']) / 3

        # Early vs late comparison
        early_avg = (transition_rates['early-single'] + transition_rates['early-multi']) / 2
        late_avg = (transition_rates['late-single'] + transition_rates['late-multi']) / 2

        print(f"Timing Pattern Analysis:")
        print(f"  Single-wave average: {single_avg:.1f}%")
        print(f"  Multi-wave average: {multi_avg:.1f}%")
        print(f"  Early (100-200) average: {early_avg:.1f}%")
        print(f"  Late (300-400) average: {late_avg:.1f}%")
        print()

        if multi_avg > single_avg + 10:
            timing_pattern = "multi_wave_superior"
            conclusion = f"Multi-wave interventions superior ({multi_avg:.1f}% vs {single_avg:.1f}%)"
        elif single_avg > multi_avg + 10:
            timing_pattern = "single_wave_superior"
            conclusion = f"Single-wave interventions superior ({single_avg:.1f}% vs {multi_avg:.1f}%)"
        elif early_avg > late_avg + 10:
            timing_pattern = "early_superior"
            conclusion = f"Early interventions superior ({early_avg:.1f}% vs {late_avg:.1f}%)"
        elif late_avg > early_avg + 10:
            timing_pattern = "late_superior"
            conclusion = f"Late interventions superior ({late_avg:.1f}% vs {early_avg:.1f}%)"
        else:
            timing_pattern = "timing_insensitive"
            conclusion = f"Timing largely insensitive (all ~{multi_avg:.0f}%)"

        print(f"📊 INSIGHT #66: Timing Pattern - {conclusion}")
        print(f"   - {len(test_triplets)} basins tested with 6 timing strategies")
        print(f"   - Optimal timing: {', '.join(optimal_timings)} ({max_rate:.1f}%)")
        print(f"   - Pattern: {timing_pattern}")
        print(f"   - Single vs Multi: {single_avg:.1f}% vs {multi_avg:.1f}%")
        print(f"   - Early vs Late: {early_avg:.1f}% vs {late_avg:.1f}%")
        print(f"   - First temporal optimization of fractal control")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for timing analysis")
        print(f"   Only {len(successful)}/{len(test_triplets)*len(timing_configs)} runs completed successfully")
        timing_pattern = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "intervention_timing"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle109_intervention_timing.json"

    output_data = {
        'experiment': 'cycle109_intervention_timing',
        'test_triplets': [(t[0], t[1], t[2]) for t in test_triplets],
        'timing_configs': timing_configs,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'transitions_by_timing': transitions_by_timing if 'transitions_by_timing' in locals() else {},
            'transition_rates': transition_rates if 'transition_rates' in locals() else {},
            'timing_pattern': timing_pattern if 'timing_pattern' in locals() else False,
            'optimal_timings': optimal_timings if 'optimal_timings' in locals() else [],
            'single_vs_multi': {
                'single_avg': single_avg if 'single_avg' in locals() else 0,
                'multi_avg': multi_avg if 'multi_avg' in locals() else 0
            },
            'early_vs_late': {
                'early_avg': early_avg if 'early_avg' in locals() else 0,
                'late_avg': late_avg if 'late_avg' in locals() else 0
            }
        },
        'insight_66_discovered': True if 'timing_pattern' in locals() and timing_pattern else False,
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
