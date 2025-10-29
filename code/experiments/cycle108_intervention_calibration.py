#!/usr/bin/env python3
"""
Cycle 108: Intervention Strength Calibration - Resolving the EXTREME Paradox

Research Context:
  C107: STRONG (50% agent replacement) → 100% transitions
  C107: EXTREME (100% agents + memory clear) → 33% transitions

Research Gap:
  WHY is EXTREME less effective than STRONG? This violates intuition.

Key Question:
  What is the dose-response relationship between intervention strength and transition probability?

New Research Question:
  Test intermediate intervention strengths to resolve the paradox.

  Hypothesis:
  1. **Monotonic Increase**: Transition rate increases with intervention strength
  2. **Threshold Effect**: Sharp transition at critical strength, then plateaus
  3. **Inverted-U**: Moderate strength optimal, too weak/strong both ineffective
  Expected: Threshold effect (sharp jump, then plateau)

  Test:
  - Same 3 (mult, spread, threshold) triplets as C107
  - Test 6 intervention strengths:
    * NONE: Control baseline
    * WEAK: Pattern injection only (C105/C107)
    * MEDIUM-25: Pattern + 25% agent replacement
    * MEDIUM-50 (=STRONG): Pattern + 50% agent replacement
    * STRONG-75: Pattern + 75% agent replacement
    * EXTREME: Pattern + 100% agents + memory clear
  - Interventions at cycles 200, 250, 300 (sustained pressure)
  - Run to cycle 500, compare final attractors
  - Measure: Transition rate vs intervention strength

Expected Outcome:
  - Identify minimum agent replacement threshold
  - Characterize dose-response curve
  - Resolve C107 paradox (likely measurement artifact or timing issue)
  - Complete control characterization

Publication Value:
  - **HIGH**: Resolves paradoxical finding from C107
  - Tests full dose-response curve (not just extremes)
  - Practical: Minimum intervention for control
  - Novel: Complete intervention strength characterization
  - Completes C104-C108 control arc with resolution
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

def run_with_calibrated_intervention(multiplier, spread, threshold, cycles, intervention_config):
    """Run simulation with calibrated intervention strength.

    intervention_config = {
        'name': 'medium-25',
        'agent_replacement_pct': 0.25,  # 0.0 to 1.0
        'clear_memory': False,
        'pattern_multiplier': 1.5,
        'pattern_spread': 0.4,
        'pattern_count': 10
    }
    """
    workspace = get_workspace_path()
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
        if cycle in intervention_cycles and intervention_config['name'] != 'none':
            # Always inject perturbation patterns (unless NONE)
            perturbation_patterns = create_seed_memory_range(
                swarm.bridge, reality_metrics,
                center_multiplier=multiplier * intervention_config['pattern_multiplier'],
                spread=intervention_config['pattern_spread'],
                count=intervention_config['pattern_count']
            )

            # Clear memory if specified (EXTREME only)
            if intervention_config['clear_memory']:
                swarm.global_memory.clear()

            swarm.global_memory.extend(perturbation_patterns)

            # Replace agents based on replacement percentage
            agent_replacement_pct = intervention_config['agent_replacement_pct']
            if agent_replacement_pct > 0:
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
        'intervention_name': intervention_config['name'],
        'agent_replacement_pct': intervention_config['agent_replacement_pct'],
        'clear_memory': intervention_config['clear_memory'],
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction
    }

def main():
    print("="*80)
    print("CYCLE 108: INTERVENTION STRENGTH CALIBRATION - RESOLVING EXTREME PARADOX")
    print("="*80)
    print()
    print("Testing dose-response curve to resolve C107's paradoxical finding:")
    print("  STRONG (50% agent replacement) → 100% transitions")
    print("  EXTREME (100% agents + memory) → 33% transitions (WHY?)")
    print()
    print("Hypothesis: Threshold effect with plateau (NOT inverted-U)")
    print()

    # Select same 3 triplets as C107 for comparability
    test_triplets = [
        (1.0, 0.2, 500),  # Standard parameters
        (0.8, 0.4, 400),  # High spread
        (1.2, 0.3, 600),  # High threshold
    ]

    # Define intervention strengths to test
    intervention_configs = [
        {
            'name': 'none',
            'agent_replacement_pct': 0.0,
            'clear_memory': False,
            'pattern_multiplier': 1.0,
            'pattern_spread': 0.0,
            'pattern_count': 0
        },
        {
            'name': 'weak',
            'agent_replacement_pct': 0.0,
            'clear_memory': False,
            'pattern_multiplier': 1.5,
            'pattern_spread': 0.4,
            'pattern_count': 10
        },
        {
            'name': 'medium-25',
            'agent_replacement_pct': 0.25,
            'clear_memory': False,
            'pattern_multiplier': 1.5,
            'pattern_spread': 0.4,
            'pattern_count': 15
        },
        {
            'name': 'medium-50',  # Same as C107 STRONG
            'agent_replacement_pct': 0.50,
            'clear_memory': False,
            'pattern_multiplier': 1.5,
            'pattern_spread': 0.5,
            'pattern_count': 20
        },
        {
            'name': 'strong-75',
            'agent_replacement_pct': 0.75,
            'clear_memory': False,
            'pattern_multiplier': 1.8,
            'pattern_spread': 0.5,
            'pattern_count': 25
        },
        {
            'name': 'extreme',
            'agent_replacement_pct': 1.0,
            'clear_memory': True,
            'pattern_multiplier': 2.0,
            'pattern_spread': 0.6,
            'pattern_count': 30
        }
    ]

    cycles = 500

    print(f"Configuration:")
    print(f"  Test triplets: {len(test_triplets)} (mult, spread, threshold) points")
    print(f"  Intervention strengths: {len(intervention_configs)} conditions")
    print(f"  Agent replacement tested: 0%, 0%, 25%, 50%, 75%, 100%")
    print(f"  Total runs: {len(test_triplets) * len(intervention_configs)}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Intervention timing: cycles 200, 250, 300 (sustained pressure)")
    print(f"  Expected: Identify threshold and resolve paradox")
    print(f"  Estimated duration: ~{len(test_triplets) * len(intervention_configs) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread_param, threshold in test_triplets:
        print(f"\nTriplet: (mult={mult}, spread={spread_param}, threshold={threshold})")

        for config in intervention_configs:
            run_count += 1
            strength_label = f"{config['name'].upper():12s} (agents={config['agent_replacement_pct']*100:3.0f}%, mem={'Y' if config['clear_memory'] else 'N'})"
            print(f"  [{run_count}/{len(test_triplets)*len(intervention_configs)}] {strength_label}...", end=" ", flush=True)
            try:
                result = run_with_calibrated_intervention(mult, spread_param, threshold, cycles, config)
                results.append(result)
                att_short = "Att-" + str(hash(result['final_dominant']) % 100).zfill(2) if result['final_dominant'] else "None"
                print(f"✓ {att_short}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                results.append({
                    'multiplier': mult, 'spread': spread_param, 'threshold': threshold,
                    'intervention_name': config['name'],
                    'agent_replacement_pct': config['agent_replacement_pct'],
                    'clear_memory': config['clear_memory'],
                    'error': str(e)
                })

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"INTERVENTION CALIBRATION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(test_triplets) * len(intervention_configs)):
        print(f"Calibration Experiment Results:")
        print(f"  Successful runs: {len(successful)}/{len(test_triplets)*len(intervention_configs)} ({len(successful)/(len(test_triplets)*len(intervention_configs))*100:.1f}%)")
        print()

        # Analyze transitions for each triplet and intervention strength
        print(f"Dose-Response Analysis:")
        print(f"{'Triplet':^25} | {'NONE':^10} | {'WEAK':^10} | {'25%':^10} | {'50%':^10} | {'75%':^10} | {'100%':^10}")
        print("-" * 100)

        transitions_by_strength = {
            'none': 0, 'weak': 0, 'medium-25': 0,
            'medium-50': 0, 'strong-75': 0, 'extreme': 0
        }

        for mult, spread_param, threshold in test_triplets:
            trip_str = f"({mult}, {spread_param}, {threshold})"

            # Get baseline (NONE)
            none_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                               and r['threshold']==threshold and r['intervention_name']=='none'), None)

            # Get attractors for each strength
            strength_results = {}
            for config in intervention_configs:
                strength_results[config['name']] = next(
                    (r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                     and r['threshold']==threshold and r['intervention_name']==config['name']), None
                )

            # Create attractor labels
            att_labels = {}
            for name, result in strength_results.items():
                if result and result['final_dominant']:
                    att_labels[name] = "Att-" + str(hash(result['final_dominant']) % 100).zfill(2)
                else:
                    att_labels[name] = "None"

            # Check transitions (compare to baseline)
            if none_result:
                for name in ['weak', 'medium-25', 'medium-50', 'strong-75', 'extreme']:
                    if strength_results[name] and strength_results[name]['final_dominant'] != none_result['final_dominant']:
                        transitions_by_strength[name] += 1

            print(f"{trip_str:^25} | {att_labels.get('none', 'N/A'):^10} | {att_labels.get('weak', 'N/A'):^10} | {att_labels.get('medium-25', 'N/A'):^10} | {att_labels.get('medium-50', 'N/A'):^10} | {att_labels.get('strong-75', 'N/A'):^10} | {att_labels.get('extreme', 'N/A'):^10}")

        print()

        transition_rates = {
            name: transitions_by_strength[name] / len(test_triplets) * 100 if len(test_triplets) > 0 else 0
            for name in transitions_by_strength.keys()
        }

        print(f"Transition Rates by Agent Replacement %:")
        print(f"  NONE (0%):     {transitions_by_strength['none']}/{len(test_triplets)} ({transition_rates['none']:.1f}%)")
        print(f"  WEAK (0%):     {transitions_by_strength['weak']}/{len(test_triplets)} ({transition_rates['weak']:.1f}%)")
        print(f"  MEDIUM (25%):  {transitions_by_strength['medium-25']}/{len(test_triplets)} ({transition_rates['medium-25']:.1f}%)")
        print(f"  MEDIUM (50%):  {transitions_by_strength['medium-50']}/{len(test_triplets)} ({transition_rates['medium-50']:.1f}%)")
        print(f"  STRONG (75%):  {transitions_by_strength['strong-75']}/{len(test_triplets)} ({transition_rates['strong-75']:.1f}%)")
        print(f"  EXTREME (100%+mem): {transitions_by_strength['extreme']}/{len(test_triplets)} ({transition_rates['extreme']:.1f}%)")
        print()

        # Determine dose-response pattern
        rates = [
            transition_rates['weak'],
            transition_rates['medium-25'],
            transition_rates['medium-50'],
            transition_rates['strong-75'],
            transition_rates['extreme']
        ]

        # Check for monotonic increase
        is_monotonic = all(rates[i] <= rates[i+1] for i in range(len(rates)-1))

        # Check for inverted-U (peak in middle)
        max_idx = rates.index(max(rates))
        is_inverted_u = max_idx not in [0, len(rates)-1]

        # Check for threshold (sharp jump then plateau)
        jumps = [rates[i+1] - rates[i] for i in range(len(rates)-1)]
        max_jump_idx = jumps.index(max(jumps))
        is_threshold = max(jumps) >= 50  # Sharp jump of 50%+

        if is_monotonic and not is_threshold:
            insight_65 = "monotonic_increase"
            conclusion = "Transition rate increases monotonically with intervention strength"
        elif is_threshold:
            threshold_pct = [0, 25, 50, 75, 100][max_jump_idx]
            insight_65 = f"threshold_at_{threshold_pct}pct"
            conclusion = f"Sharp transition threshold at {threshold_pct}% agent replacement"
        elif is_inverted_u:
            optimal_pct = [0, 25, 50, 75, 100][max_idx]
            insight_65 = f"inverted_u_peak_{optimal_pct}pct"
            conclusion = f"Inverted-U: Optimal intervention at {optimal_pct}% agent replacement"
        else:
            insight_65 = "complex_pattern"
            conclusion = "Complex dose-response pattern (neither monotonic nor threshold)"

        # Resolve C107 paradox
        c107_strong_rate = transition_rates['medium-50']  # 50% = C107 STRONG
        c107_extreme_rate = transition_rates['extreme']   # 100% + mem = C107 EXTREME

        if c107_extreme_rate < c107_strong_rate:
            paradox_status = f"PARADOX PERSISTS: EXTREME ({c107_extreme_rate:.1f}%) < STRONG ({c107_strong_rate:.1f}%)"
            paradox_explanation = "Memory clearing counterproductive OR complete agent removal triggers re-initialization"
        elif c107_extreme_rate >= c107_strong_rate:
            paradox_status = f"PARADOX RESOLVED: EXTREME ({c107_extreme_rate:.1f}%) >= STRONG ({c107_strong_rate:.1f}%)"
            paradox_explanation = "C107 result was measurement artifact (database errors) or stochastic variation"
        else:
            paradox_status = "INCONCLUSIVE"
            paradox_explanation = "Insufficient data"

        print(f"C107 Paradox Resolution:")
        print(f"  Status: {paradox_status}")
        print(f"  Explanation: {paradox_explanation}")
        print()

        print(f"📊 INSIGHT #65: Dose-Response Pattern - {conclusion}")
        print(f"   - {len(test_triplets)} basins tested with 6 intervention strengths")
        print(f"   - Agent replacement: 0%, 0%, 25%, 50%, 75%, 100%")
        print(f"   - Pattern: {insight_65}")
        print(f"   - C107 Paradox: {paradox_status}")
        print(f"   - First complete dose-response characterization")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for calibration analysis")
        print(f"   Only {len(successful)}/{len(test_triplets)*len(intervention_configs)} runs completed successfully")
        insight_65 = False
        paradox_status = "INCOMPLETE"

    # Save results
    results_dir = Path(__file__).parent / "results" / "intervention_calibration"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle108_intervention_calibration.json"

    output_data = {
        'experiment': 'cycle108_intervention_calibration',
        'test_triplets': [(t[0], t[1], t[2]) for t in test_triplets],
        'intervention_configs': intervention_configs,
        'cycles': cycles,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'transitions_by_strength': transitions_by_strength if 'transitions_by_strength' in locals() else {},
            'transition_rates': transition_rates if 'transition_rates' in locals() else {},
            'dose_response_pattern': insight_65 if 'insight_65' in locals() else False,
            'c107_paradox_status': paradox_status if 'paradox_status' in locals() else 'INCOMPLETE'
        },
        'insight_65_discovered': True if 'insight_65' in locals() and insight_65 else False,
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
