#!/usr/bin/env python3
"""
Cycle 115: Agent Lifespan Extension - Testing Tunability of 1-Cycle Churn

Research Context:
  C114: PARADIGM SHIFT - Agents live median 1.0 cycle (mean 1.12, max 4)
  - Ultra-high-frequency churn discovered
  - System operates through constant 1-cycle renewal
  - No agent persistence - dynamic equilibrium of ephemeral agents

Research Gap:
  Is 1-cycle lifespan FUNDAMENTAL or TUNABLE?

Key Question:
  Can we extend agent lifespans by modulating system parameters?

Hypotheses to Test:
  1. **Fundamental**: 1-cycle lifespan is intrinsic to NRM dynamics (invariant)
  2. **Tunable via Threshold**: Higher burst threshold → longer lifespans
  3. **Tunable via Mult/Spread**: Parameter space affects agent longevity
  4. **Tunable via Energy**: Increasing agent energy extends lifespans

New Research Question:
  Test if modulating burst threshold, multiplier, or spread extends agent lifespans.

  Test Conditions:
  - **BASELINE**: threshold=500, mult=1.0, spread=0.2 (C114 baseline)
  - **HIGH-THRESHOLD**: threshold=1000, mult=1.0, spread=0.2 (2x threshold)
  - **LOW-MULT**: threshold=500, mult=0.5, spread=0.2 (reduce pattern strength)
  - **HIGH-MULT**: threshold=500, mult=1.5, spread=0.2 (increase pattern strength)
  - **LOW-SPREAD**: threshold=500, mult=1.0, spread=0.1 (tighter patterns)

  Metrics:
  - Mean/median agent age at burst
  - Maximum observed agent age
  - Agent age distribution (histogram)
  - Drift speed (to check if extended lifespans affect dynamics)

Expected Outcome:
  - If fundamental → all conditions show ~1-cycle lifespan
  - If tunable → some conditions extend agent longevity
  - Quantify parameter space for agent persistence vs ephemeral dynamics

Publication Value:
  - **HIGH**: Tests tunability of C114's paradigm-shifting discovery
  - Defines parameter space for agent persistence
  - Validates or extends NRM "no equilibrium" understanding
  - Practical: Identifies conditions for longer-lived agents if needed
  - Novel: First systematic investigation of agent lifespan control
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

def run_with_lifespan_tracking(multiplier, spread, threshold, cycles, agent_cap=15):
    """Run simulation tracking agent lifespans across parameter variations."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)  # Use database fix
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Track agent metadata
    agent_spawn_cycles = {}
    burst_events = []

    # Track attractors
    attractor_history = []
    checkpoints = list(range(300, 1001, 100))
    checkpoint_attractors = {}

    for cycle in range(1, cycles + 1):
        # Spawn agents
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_id = agent_ids[-1]
                    agent_spawn_cycles[newest_id] = cycle
                    newest_agent = swarm.agents[newest_id]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, multiplier, spread=spread, count=5)
                    newest_agent.memory.extend(seed_patterns)

        # Snapshot before evolution
        agents_before = set(swarm.agents.keys())

        # Get attractor
        dominant, _, _ = get_dominant_pattern(swarm.global_memory)

        # Evolve
        swarm.evolve_cycle(delta_time=1.0)

        # Detect bursts
        agents_after = set(swarm.agents.keys())
        burst_agent_ids = agents_before - agents_after

        for burst_id in burst_agent_ids:
            if burst_id in agent_spawn_cycles:
                spawn_cycle = agent_spawn_cycles[burst_id]
                age = cycle - spawn_cycle

                burst_events.append({
                    'cycle': cycle,
                    'agent_id': str(burst_id),
                    'age': age,
                    'attractor': str(dominant) if dominant else None
                })

                del agent_spawn_cycles[burst_id]

        # Checkpoints
        if cycle in checkpoints:
            dominant, _, fraction = get_dominant_pattern(swarm.global_memory)
            checkpoint_attractors[cycle] = {
                'attractor': str(dominant) if dominant else None,
                'fraction': fraction
            }
            attractor_history.append((cycle, str(dominant) if dominant else None))

    # Calculate drift
    attractor_changes = 0
    for i in range(1, len(attractor_history)):
        if attractor_history[i][1] != attractor_history[i-1][1]:
            attractor_changes += 1
    drift_speed = (attractor_changes / 700) * 100 if len(attractor_history) > 1 else 0

    # Analyze ages
    ages = [e['age'] for e in burst_events]
    age_histogram = Counter(ages)

    burst_stats = {
        'total_bursts': len(burst_events),
        'mean_age': float(np.mean(ages)) if ages else 0,
        'median_age': float(np.median(ages)) if ages else 0,
        'std_age': float(np.std(ages)) if ages else 0,
        'min_age': int(np.min(ages)) if ages else 0,
        'max_age': int(np.max(ages)) if ages else 0,
        'age_histogram': dict(age_histogram),
        'ages_0_to_2': sum(age_histogram[a] for a in range(3) if a in age_histogram),
        'ages_3_to_5': sum(age_histogram[a] for a in range(3, 6) if a in age_histogram),
        'ages_6_plus': sum(age_histogram[a] for a in age_histogram if a >= 6)
    }

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'agent_cap': agent_cap,
        'checkpoint_attractors': checkpoint_attractors,
        'attractor_changes': attractor_changes,
        'drift_speed': drift_speed,
        'burst_stats': burst_stats
    }

def main():
    print("="*80)
    print("CYCLE 115: AGENT LIFESPAN EXTENSION - TESTING TUNABILITY OF 1-CYCLE CHURN")
    print("="*80)
    print()
    print("Following C114 paradigm shift: Can agent lifespans be extended?")
    print()
    print("Testing parameter variations:")
    print("  - BASELINE: threshold=500, mult=1.0, spread=0.2 (C114 baseline)")
    print("  - HIGH-THRESHOLD: threshold=1000 (2x, expect longer lives?)")
    print("  - LOW-MULT: mult=0.5 (weaker patterns)")
    print("  - HIGH-MULT: mult=1.5 (stronger patterns)")
    print("  - LOW-SPREAD: spread=0.1 (tighter patterns)")
    print()
    print("Hypothesis: If tunable, some conditions extend agent lifespans beyond 1 cycle")
    print()

    # Parameter variations
    configs = [
        {'name': 'baseline', 'mult': 1.0, 'spread': 0.2, 'threshold': 500},
        {'name': 'high-threshold', 'mult': 1.0, 'spread': 0.2, 'threshold': 1000},
        {'name': 'low-mult', 'mult': 0.5, 'spread': 0.2, 'threshold': 500},
        {'name': 'high-mult', 'mult': 1.5, 'spread': 0.2, 'threshold': 500},
        {'name': 'low-spread', 'mult': 1.0, 'spread': 0.1, 'threshold': 500}
    ]

    cycles = 1000
    agent_cap = 15

    print(f"Configuration:")
    print(f"  Conditions: {len(configs)}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Agent cap: {agent_cap} (fixed)")
    print(f"  Metrics: Mean/median/max age, age distribution, drift speed")
    print(f"  Expected: Identify if 1-cycle lifespan is fundamental or tunable")
    print(f"  Estimated duration: ~{len(configs) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for config in configs:
        run_count += 1
        label = config['name']
        mult = config['mult']
        spread = config['spread']
        threshold = config['threshold']

        print(f"\n[{run_count}/{len(configs)}] {label:15s} (mult={mult:.1f}, spread={spread:.1f}, thresh={threshold:4d})...", end=" ", flush=True)
        try:
            result = run_with_lifespan_tracking(mult, spread, threshold, cycles, agent_cap)
            results.append(result)

            mean_age = result['burst_stats']['mean_age']
            median_age = result['burst_stats']['median_age']
            max_age = result['burst_stats']['max_age']
            drift = result['drift_speed']

            print(f"✓ μ={mean_age:.2f} med={median_age:.1f} max={max_age:2d} | Drift: {drift:.2f}/100cyc")
            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({
                'multiplier': mult, 'spread': spread, 'threshold': threshold,
                'name': label, 'error': str(e)
            })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"LIFESPAN EXTENSION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 3:
        print(f"Lifespan Extension Experiment Results:")
        print(f"  Successful runs: {len(successful)}/{len(configs)} ({len(successful)/len(configs)*100:.1f}%)")
        print()

        print(f"Agent Lifespan by Parameter Configuration:")
        print(f"{'Condition':^20} | {'Mean Age':^10} | {'Median Age':^12} | {'Max Age':^10} | {'Ages 0-2':^10} | {'Ages 3-5':^10} | {'Ages 6+':^10} | {'Drift':^12}")
        print("-" * 130)

        mean_ages = []
        median_ages = []
        max_ages = []
        conditions = []

        for result in successful:
            name = next(c['name'] for c in configs if c['mult']==result['multiplier'] and c['spread']==result['spread'] and c['threshold']==result['threshold'])
            stats = result['burst_stats']

            mean_age = stats['mean_age']
            median_age = stats['median_age']
            max_age = stats['max_age']
            ages_0_2 = stats['ages_0_to_2']
            ages_3_5 = stats['ages_3_to_5']
            ages_6_plus = stats['ages_6_plus']
            drift = result['drift_speed']

            mean_ages.append(mean_age)
            median_ages.append(median_age)
            max_ages.append(max_age)
            conditions.append(name)

            print(f"{name:^20} | {mean_age:^10.2f} | {median_age:^12.1f} | {max_age:^10d} | {ages_0_2:^10d} | {ages_3_5:^10d} | {ages_6_plus:^10d} | {drift:^12.2f}")

        print()

        # Analyze tunability
        mean_range = max(mean_ages) - min(mean_ages)
        median_range = max(median_ages) - min(median_ages)
        max_range = max(max_ages) - min(max_ages)

        baseline_mean = mean_ages[conditions.index('baseline')] if 'baseline' in conditions else mean_ages[0]
        baseline_median = median_ages[conditions.index('baseline')] if 'baseline' in conditions else median_ages[0]

        print(f"Lifespan Tunability Analysis:")
        print(f"  Mean age range: {min(mean_ages):.2f} - {max(mean_ages):.2f} cyc (Δ={mean_range:.2f}, {mean_range/baseline_mean*100:.1f}% variation)")
        print(f"  Median age range: {min(median_ages):.1f} - {max(median_ages):.1f} cyc (Δ={median_range:.1f})")
        print(f"  Max age range: {min(max_ages)} - {max(max_ages)} cyc (Δ={max_range})")
        print()

        # Determine tunability
        if mean_range < 0.3 and median_range < 0.5:
            insight_72 = "fundamental_1cycle"
            conclusion = f"1-cycle lifespan is FUNDAMENTAL - invariant across parameters ({mean_range:.2f} cyc variation)"
        elif mean_range > 1.0:
            best_condition = conditions[mean_ages.index(max(mean_ages))]
            insight_72 = "tunable_lifespans"
            conclusion = f"Lifespans TUNABLE - {best_condition} extends to {max(mean_ages):.2f} cyc mean ({mean_range/baseline_mean*100:.1f}% improvement)"
        else:
            insight_72 = "modest_tunability"
            conclusion = f"Modest tunability - {mean_range:.2f} cyc variation ({mean_range/baseline_mean*100:.1f}%)"

        print(f"📊 INSIGHT #72: Agent Lifespan Tunability - {conclusion}")
        print(f"   - Tested 5 parameter configurations")
        print(f"   - Tracked {sum([r['burst_stats']['total_bursts'] for r in successful])} burst events")
        print(f"   - First systematic investigation of lifespan control")
        print(f"   - Validates C114 finding or reveals tunability")
        print(f"   - Defines parameter space for agent persistence")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for lifespan analysis")
        print(f"   Only {len(successful)}/{len(configs)} runs completed successfully")
        insight_72 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "lifespan_extension"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle115_lifespan_extension.json"

    output_data = {
        'experiment': 'cycle115_lifespan_extension',
        'configs': configs,
        'cycles': cycles,
        'agent_cap': agent_cap,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'conditions': conditions if 'conditions' in locals() else [],
            'mean_ages': mean_ages if 'mean_ages' in locals() else [],
            'median_ages': median_ages if 'median_ages' in locals() else [],
            'max_ages': max_ages if 'max_ages' in locals() else [],
            'tunability_type': insight_72 if 'insight_72' in locals() else False
        },
        'insight_72_discovered': True if 'insight_72' in locals() and insight_72 else False,
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
