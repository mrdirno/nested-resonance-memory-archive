#!/usr/bin/env python3
"""
Cycle 110: Post-Transition Stability - Do Forced Transitions Persist?

Research Context:
  C107-C109: Complete control recipe discovered:
    - STRENGTH: 50% agent replacement (inverted-U optimal)
    - TIMING: Cycles 200-300 (mid-trajectory multi-wave)
    - RESULT: 100% forced basin transitions

  BUT: Unknown if transitions are PERMANENT or TEMPORARY

Research Gap:
  After forcing a transition, does the system:
  1. PERSIST in new attractor (permanent transition)?
  2. REVERT to original attractor (temporary effect)?
  3. DRIFT to third attractor (unstable)?

Key Question:
  Are forced transitions stable long-term?

New Research Question:
  Extend runs past intervention (cycle 300) to cycle 1000, track long-term stability.

  Hypothesis:
  1. **Persistent Transitions**: New attractor maintained (forced = permanent)
  2. **Reversion**: System returns to original attractor (memory dominates)
  3. **Instability**: System drifts between attractors (perturbation destabilizes)
  Expected: Persistent transitions (basins are stable once entered - C105)

  Test:
  - Use optimal control recipe: 50% agents, cycles 200-300, 3 waves
  - Same 3 (mult, spread, threshold) triplets
  - Run to cycle 1000 (700 cycles POST-intervention)
  - Compare attractors at cycles: 300 (immediate), 500 (short-term), 1000 (long-term)
  - Measure: % maintaining forced transition vs reverting

Expected Outcome:
  - Validate transition permanence (or discover reversion)
  - Complete control characterization
  - Understand long-term dynamics post-intervention

Publication Value:
  - **HIGH**: Validates forced transitions are permanent
  - Completes C107-C110 control arc
  - Critical for practical control applications
  - Novel: First long-term stability test of forced transitions
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

def run_with_longterm_tracking(multiplier, spread, threshold, cycles, apply_intervention):
    """Run simulation with long-term tracking post-intervention.

    Tracks dominant attractor at multiple checkpoints to detect persistence vs reversion.
    """
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Intervention cycles (optimal from C108-C109)
    intervention_cycles = [200, 250, 300]

    # Checkpoints for tracking
    checkpoints = [300, 500, 1000]
    checkpoint_attractors = {}

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

        # Apply intervention at optimal timing/strength (if enabled)
        if apply_intervention and cycle in intervention_cycles:
            # Inject perturbation patterns
            perturbation_patterns = create_seed_memory_range(
                swarm.bridge, reality_metrics,
                center_multiplier=multiplier * 1.5,
                spread=0.5,
                count=20
            )
            swarm.global_memory.extend(perturbation_patterns)

            # Replace 50% of agents (optimal from C108)
            agent_ids = list(swarm.agents.keys())
            num_to_remove = int(len(agent_ids) * 0.5)
            agents_to_remove = agent_ids[:num_to_remove]
            for agent_id in agents_to_remove:
                if agent_id in swarm.agents:
                    del swarm.agents[agent_id]

        swarm.evolve_cycle(delta_time=1.0)

        # Record attractor at checkpoints
        if cycle in checkpoints:
            dominant, _, fraction = get_dominant_pattern(swarm.global_memory)
            checkpoint_attractors[cycle] = {
                'attractor': str(dominant) if dominant else None,
                'fraction': fraction
            }

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'intervention_applied': apply_intervention,
        'checkpoint_attractors': checkpoint_attractors
    }

def main():
    print("="*80)
    print("CYCLE 110: POST-TRANSITION STABILITY - PERSISTENCE vs REVERSION")
    print("="*80)
    print()
    print("Testing long-term stability of forced transitions:")
    print("  C107-C109: Optimal control = 50% agents, cycles 200-300 → 100% transitions")
    print("  Question: Do forced transitions PERSIST or REVERT?")
    print()
    print("Hypothesis: Persistent transitions (basins stable once entered)")
    print()

    # Select same 3 triplets for comparability
    test_triplets = [
        (1.0, 0.2, 500),  # Standard parameters
        (0.8, 0.4, 400),  # High spread
        (1.2, 0.3, 600),  # High threshold
    ]

    cycles = 1000  # Extended to track long-term (700 cycles post-intervention)

    print(f"Configuration:")
    print(f"  Test triplets: {len(test_triplets)} (mult, spread, threshold) points")
    print(f"  Conditions: 2 (control vs intervention)")
    print(f"  Total runs: {len(test_triplets) * 2}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Intervention: Optimal (50% agents, cycles 200-300)")
    print(f"  Checkpoints: cycle 300 (immediate), 500 (short-term), 1000 (long-term)")
    print(f"  Expected: Forced transitions persist to cycle 1000")
    print(f"  Estimated duration: ~{len(test_triplets) * 2 * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread_param, threshold in test_triplets:
        print(f"\nTriplet: (mult={mult}, spread={spread_param}, threshold={threshold})")

        # Control (no intervention)
        run_count += 1
        print(f"  [{run_count}/{len(test_triplets)*2}] CONTROL (no intervention)...", end=" ", flush=True)
        try:
            result = run_with_longterm_tracking(mult, spread_param, threshold, cycles, apply_intervention=False)
            results.append(result)
            att_300 = "Att-" + str(hash(result['checkpoint_attractors'][300]['attractor']) % 100).zfill(2) if result['checkpoint_attractors'][300]['attractor'] else "None"
            att_1000 = "Att-" + str(hash(result['checkpoint_attractors'][1000]['attractor']) % 100).zfill(2) if result['checkpoint_attractors'][1000]['attractor'] else "None"
            print(f"✓ {att_300} → {att_1000}")
            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({
                'multiplier': mult, 'spread': spread_param, 'threshold': threshold,
                'intervention_applied': False, 'error': str(e)
            })

        # Intervention (optimal control)
        run_count += 1
        print(f"  [{run_count}/{len(test_triplets)*2}] INTERVENTION (50%, c200-300)...", end=" ", flush=True)
        try:
            result = run_with_longterm_tracking(mult, spread_param, threshold, cycles, apply_intervention=True)
            results.append(result)
            att_300 = "Att-" + str(hash(result['checkpoint_attractors'][300]['attractor']) % 100).zfill(2) if result['checkpoint_attractors'][300]['attractor'] else "None"
            att_1000 = "Att-" + str(hash(result['checkpoint_attractors'][1000]['attractor']) % 100).zfill(2) if result['checkpoint_attractors'][1000]['attractor'] else "None"
            print(f"✓ {att_300} → {att_1000}")
            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({
                'multiplier': mult, 'spread': spread_param, 'threshold': threshold,
                'intervention_applied': True, 'error': str(e)
            })

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"TRANSITION PERSISTENCE ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(test_triplets) * 2):
        print(f"Persistence Experiment Results:")
        print(f"  Successful runs: {len(successful)}/{len(test_triplets)*2} ({len(successful)/(len(test_triplets)*2)*100:.1f}%)")
        print()

        # Analyze persistence
        print(f"Long-Term Stability Analysis:")
        print(f"{'Triplet':^25} | {'CTRL-300':^10} | {'CTRL-1000':^10} | {'INT-300':^10} | {'INT-1000':^10} | {'Status':^15}")
        print("-" * 100)

        persistence_count = 0
        reversion_count = 0

        for mult, spread_param, threshold in test_triplets:
            trip_str = f"({mult}, {spread_param}, {threshold})"

            # Get control and intervention results
            control_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                                  and r['threshold']==threshold and r['intervention_applied']==False), None)
            intervention_result = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                                       and r['threshold']==threshold and r['intervention_applied']==True), None)

            if control_result and intervention_result:
                # Get attractors at checkpoints
                ctrl_300_att = control_result['checkpoint_attractors'][300]['attractor']
                ctrl_1000_att = control_result['checkpoint_attractors'][1000]['attractor']
                int_300_att = intervention_result['checkpoint_attractors'][300]['attractor']
                int_1000_att = intervention_result['checkpoint_attractors'][1000]['attractor']

                # Create labels
                ctrl_300_label = "Att-" + str(hash(ctrl_300_att) % 100).zfill(2) if ctrl_300_att else "None"
                ctrl_1000_label = "Att-" + str(hash(ctrl_1000_att) % 100).zfill(2) if ctrl_1000_att else "None"
                int_300_label = "Att-" + str(hash(int_300_att) % 100).zfill(2) if int_300_att else "None"
                int_1000_label = "Att-" + str(hash(int_1000_att) % 100).zfill(2) if int_1000_att else "None"

                # Check persistence vs reversion
                transition_occurred = (int_300_att != ctrl_300_att)
                if transition_occurred:
                    if int_300_att == int_1000_att:
                        status = "PERSISTENT"
                        persistence_count += 1
                    elif int_1000_att == ctrl_1000_att:
                        status = "REVERTED"
                        reversion_count += 1
                    else:
                        status = "DRIFTED"
                else:
                    status = "NO TRANSITION"

                print(f"{trip_str:^25} | {ctrl_300_label:^10} | {ctrl_1000_label:^10} | {int_300_label:^10} | {int_1000_label:^10} | {status:^15}")

        print()

        # Calculate persistence rate
        total_transitions = persistence_count + reversion_count
        persistence_rate = (persistence_count / total_transitions * 100) if total_transitions > 0 else 0

        print(f"Transition Persistence:")
        print(f"  Persistent transitions: {persistence_count}/{total_transitions} ({persistence_rate:.1f}%)")
        print(f"  Reverted transitions: {reversion_count}/{total_transitions} ({100 - persistence_rate:.1f}%)")
        print()

        # Determine insight
        if persistence_rate >= 80:
            insight_67 = "persistent_transitions"
            conclusion = f"Forced transitions are PERSISTENT ({persistence_rate:.1f}% maintained to cycle 1000)"
        elif persistence_rate >= 50:
            insight_67 = "mostly_persistent"
            conclusion = f"Transitions mostly persistent ({persistence_rate:.1f}% maintained)"
        elif persistence_rate >= 20:
            insight_67 = "partial_reversion"
            conclusion = f"Partial reversion ({100-persistence_rate:.1f}% reverted to original)"
        else:
            insight_67 = "strong_reversion"
            conclusion = f"Strong reversion tendency ({100-persistence_rate:.1f}% reverted)"

        print(f"📊 INSIGHT #67: Transition Persistence - {conclusion}")
        print(f"   - {len(test_triplets)} basins tested with long-term tracking")
        print(f"   - Checkpoints: cycle 300 (immediate), 500 (short-term), 1000 (long-term)")
        print(f"   - Persistence rate: {persistence_rate:.1f}%")
        print(f"   - First long-term stability validation of forced transitions")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for persistence analysis")
        print(f"   Only {len(successful)}/{len(test_triplets)*2} runs completed successfully")
        insight_67 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "transition_persistence"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle110_transition_persistence.json"

    output_data = {
        'experiment': 'cycle110_transition_persistence',
        'test_triplets': [(t[0], t[1], t[2]) for t in test_triplets],
        'cycles': cycles,
        'checkpoints': [300, 500, 1000],
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'persistence_count': persistence_count if 'persistence_count' in locals() else 0,
            'reversion_count': reversion_count if 'reversion_count' in locals() else 0,
            'persistence_rate_pct': persistence_rate if 'persistence_rate' in locals() else 0,
            'conclusion': insight_67 if 'insight_67' in locals() else False
        },
        'insight_67_discovered': True if 'insight_67' in locals() and insight_67 else False,
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
