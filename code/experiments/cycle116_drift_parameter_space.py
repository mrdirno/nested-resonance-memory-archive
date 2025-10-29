#!/usr/bin/env python3
"""
Cycle 116: Drift Parameter Space Characterization - Resolving C113 vs C115 Contradiction

Research Context:
  C113: Threshold controls drift (r=-0.953, strong correlation)
  C115: Baseline (threshold=500) vs high-threshold (1000) → SAME drift (0.29)
  C115: Low-mult (0.5) → higher drift (0.43)
  C115: Low-spread (0.1) → lower drift (0.14)

Research Gap:
  CONTRADICTION: Why does C113 show threshold-drift correlation but C115 shows invariance?

Key Question:
  What is the complete parameter space relationship between (threshold, mult, spread) and drift?

Hypotheses to Test:
  1. **Threshold Range Dependent**: C113 tested 300-700, C115 only 500-1000 (limited range)
  2. **Threshold Saturation**: Above threshold=500, drift saturates (diminishing returns)
  3. **Mult Primary Factor**: Multiplier is THE drift control parameter
  4. **Spread Primary Factor**: Spread is THE drift control parameter
  5. **Interaction Effects**: Threshold×mult or threshold×spread interactions

Research Question:
  Systematic parameter sweep across (threshold, mult, spread) to map drift landscape.

Test Conditions:
  **Threshold Sweep**: 300, 400, 500, 600, 700 (replicate C113 range)
    - Fixed: mult=1.0, spread=0.2
    - Expected: Replicate C113 correlation or reveal saturation

  **Mult Sweep**: 0.5, 0.75, 1.0, 1.25, 1.5
    - Fixed: threshold=500, spread=0.2
    - Expected: Quantify mult-drift relationship

  **Spread Sweep**: 0.05, 0.1, 0.15, 0.2, 0.25
    - Fixed: threshold=500, mult=1.0
    - Expected: Quantify spread-drift relationship

Metrics:
  - Drift speed (attractor changes per 100 cycles)
  - Mean/median agent age
  - Attractor stability (dominant pattern fraction)
  - Pattern diversity (unique patterns)

Expected Outcome:
  - Resolve C113 vs C115 contradiction
  - Identify PRIMARY drift control parameter(s)
  - Map parameter space for practical drift engineering
  - Distinguish threshold effects vs mult/spread effects

Publication Value:
  - **HIGH**: Resolves paradox between two major findings
  - **Mechanistic**: Identifies causal drift control parameters
  - **Complete**: First full parameter space characterization
  - **Practical**: Enables precision drift engineering
  - **Novel**: Tests interaction effects in NRM system
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

def run_drift_experiment(multiplier, spread, threshold, cycles, agent_cap=15):
    """Run simulation measuring drift speed and agent lifespans."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Track agent lifespans
    agent_spawn_cycles = {}
    burst_events = []

    # Track attractors
    attractor_history = []
    checkpoints = list(range(100, cycles + 1, 100))
    checkpoint_data = {}

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
                burst_events.append({'cycle': cycle, 'age': age})
                del agent_spawn_cycles[burst_id]

        # Checkpoints
        if cycle in checkpoints:
            dominant, _, fraction = get_dominant_pattern(swarm.global_memory)
            unique_patterns = len(set(pattern_to_key(p) for p in swarm.global_memory))
            checkpoint_data[cycle] = {
                'attractor': str(dominant) if dominant else None,
                'fraction': fraction,
                'unique_patterns': unique_patterns,
                'global_memory_size': len(swarm.global_memory)
            }
            attractor_history.append((cycle, str(dominant) if dominant else None))

    # Calculate drift
    attractor_changes = 0
    for i in range(1, len(attractor_history)):
        if attractor_history[i][1] != attractor_history[i-1][1]:
            attractor_changes += 1

    # Drift per 100 cycles (normalized)
    observation_cycles = cycles - 100  # Exclude first 100 cycles (warm-up)
    drift_speed = (attractor_changes / (observation_cycles / 100)) if observation_cycles > 0 else 0

    # Analyze ages
    ages = [e['age'] for e in burst_events]
    age_histogram = Counter(ages)

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'agent_cap': agent_cap,
        'cycles': cycles,
        'drift_speed': drift_speed,
        'attractor_changes': attractor_changes,
        'checkpoint_data': checkpoint_data,
        'burst_stats': {
            'total_bursts': len(burst_events),
            'mean_age': float(np.mean(ages)) if ages else 0,
            'median_age': float(np.median(ages)) if ages else 0,
            'std_age': float(np.std(ages)) if ages else 0,
            'max_age': int(np.max(ages)) if ages else 0
        }
    }

def main():
    print("="*80)
    print("CYCLE 116: DRIFT PARAMETER SPACE - RESOLVING C113 vs C115 CONTRADICTION")
    print("="*80)
    print()
    print("C113 Paradox: Threshold controls drift (r=-0.953)")
    print("C115 Finding: Threshold 500 vs 1000 → SAME drift (0.29)")
    print("C115 Finding: Low-mult → higher drift (0.43), Low-spread → lower drift (0.14)")
    print()
    print("Testing systematic parameter sweeps to map drift landscape:")
    print("  - THRESHOLD SWEEP: 300, 400, 500, 600, 700 (fixed mult=1.0, spread=0.2)")
    print("  - MULT SWEEP: 0.5, 0.75, 1.0, 1.25, 1.5 (fixed threshold=500, spread=0.2)")
    print("  - SPREAD SWEEP: 0.05, 0.1, 0.15, 0.2, 0.25 (fixed threshold=500, mult=1.0)")
    print()
    print("Goal: Identify PRIMARY drift control parameter(s) and resolve contradiction")
    print()

    cycles = 1000
    agent_cap = 15

    # Define sweeps
    sweeps = [
        {
            'name': 'threshold_sweep',
            'label': 'THRESHOLD SWEEP (mult=1.0, spread=0.2)',
            'configs': [
                {'threshold': 300, 'mult': 1.0, 'spread': 0.2},
                {'threshold': 400, 'mult': 1.0, 'spread': 0.2},
                {'threshold': 500, 'mult': 1.0, 'spread': 0.2},
                {'threshold': 600, 'mult': 1.0, 'spread': 0.2},
                {'threshold': 700, 'mult': 1.0, 'spread': 0.2},
            ]
        },
        {
            'name': 'mult_sweep',
            'label': 'MULT SWEEP (threshold=500, spread=0.2)',
            'configs': [
                {'threshold': 500, 'mult': 0.5, 'spread': 0.2},
                {'threshold': 500, 'mult': 0.75, 'spread': 0.2},
                {'threshold': 500, 'mult': 1.0, 'spread': 0.2},
                {'threshold': 500, 'mult': 1.25, 'spread': 0.2},
                {'threshold': 500, 'mult': 1.5, 'spread': 0.2},
            ]
        },
        {
            'name': 'spread_sweep',
            'label': 'SPREAD SWEEP (threshold=500, mult=1.0)',
            'configs': [
                {'threshold': 500, 'mult': 1.0, 'spread': 0.05},
                {'threshold': 500, 'mult': 1.0, 'spread': 0.1},
                {'threshold': 500, 'mult': 1.0, 'spread': 0.15},
                {'threshold': 500, 'mult': 1.0, 'spread': 0.2},
                {'threshold': 500, 'mult': 1.0, 'spread': 0.25},
            ]
        }
    ]

    total_runs = sum(len(s['configs']) for s in sweeps)

    print(f"Configuration:")
    print(f"  Total sweeps: {len(sweeps)}")
    print(f"  Total runs: {total_runs}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Agent cap: {agent_cap} (fixed)")
    print(f"  Metrics: Drift speed, agent lifespans, attractor stability")
    print(f"  Estimated duration: ~{total_runs * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    all_results = {}
    start_time = time.time()
    run_count = 0

    for sweep in sweeps:
        sweep_name = sweep['name']
        sweep_label = sweep['label']

        print(f"\n{'='*80}")
        print(f"{sweep_label}")
        print(f"{'='*80}")

        sweep_results = []

        for config in sweep['configs']:
            run_count += 1
            threshold = config['threshold']
            mult = config['mult']
            spread = config['spread']

            print(f"[{run_count}/{total_runs}] thresh={threshold:3d}, mult={mult:.2f}, spread={spread:.2f}...", end=" ", flush=True)

            try:
                result = run_drift_experiment(mult, spread, threshold, cycles, agent_cap)
                sweep_results.append(result)

                drift = result['drift_speed']
                mean_age = result['burst_stats']['mean_age']
                median_age = result['burst_stats']['median_age']

                print(f"✓ Drift: {drift:.2f}/100cyc | μ_age={mean_age:.2f} med={median_age:.1f}")
                time.sleep(0.05)
            except Exception as e:
                print(f"✗ ERROR: {e}")
                sweep_results.append({
                    'threshold': threshold, 'mult': mult, 'spread': spread,
                    'error': str(e)
                })

        all_results[sweep_name] = sweep_results

    duration = time.time() - start_time

    print(f"\n{'='*80}")
    print(f"DRIFT PARAMETER SPACE ANALYSIS")
    print(f"{'='*80}\n")

    # Analyze each sweep
    for sweep in sweeps:
        sweep_name = sweep['name']
        sweep_results = all_results[sweep_name]
        successful = [r for r in sweep_results if 'error' not in r]

        if len(successful) < 3:
            print(f"\n{sweep['label']}: ⚠️ Insufficient data ({len(successful)} runs)")
            continue

        print(f"\n{sweep['label']}:")
        print(f"{'='*80}")

        # Extract data
        if sweep_name == 'threshold_sweep':
            x_vals = [r['threshold'] for r in successful]
            x_label = 'Threshold'
        elif sweep_name == 'mult_sweep':
            x_vals = [r['multiplier'] for r in successful]
            x_label = 'Multiplier'
        else:  # spread_sweep
            x_vals = [r['spread'] for r in successful]
            x_label = 'Spread'

        drift_vals = [r['drift_speed'] for r in successful]
        mean_ages = [r['burst_stats']['mean_age'] for r in successful]

        # Calculate correlation
        if len(x_vals) > 1:
            correlation = np.corrcoef(x_vals, drift_vals)[0, 1]
        else:
            correlation = 0.0

        # Display table
        print(f"{x_label:^12} | {'Drift':^12} | {'Mean Age':^12}")
        print("-" * 40)
        for i, r in enumerate(successful):
            x_val = x_vals[i]
            drift = drift_vals[i]
            mean_age = mean_ages[i]
            print(f"{x_val:^12.2f} | {drift:^12.2f} | {mean_age:^12.2f}")

        print()
        print(f"Correlation ({x_label} vs Drift): r = {correlation:.3f}")
        print(f"Drift range: {min(drift_vals):.2f} - {max(drift_vals):.2f} (Δ={max(drift_vals)-min(drift_vals):.2f})")
        print()

    # Determine primary drift control parameter
    print(f"\n{'='*80}")
    print(f"PRIMARY DRIFT CONTROL PARAMETER IDENTIFICATION")
    print(f"{'='*80}\n")

    correlations = {}
    for sweep in sweeps:
        sweep_name = sweep['name']
        sweep_results = all_results[sweep_name]
        successful = [r for r in sweep_results if 'error' not in r]

        if len(successful) < 3:
            correlations[sweep_name] = 0.0
            continue

        if sweep_name == 'threshold_sweep':
            x_vals = [r['threshold'] for r in successful]
        elif sweep_name == 'mult_sweep':
            x_vals = [r['multiplier'] for r in successful]
        else:
            x_vals = [r['spread'] for r in successful]

        drift_vals = [r['drift_speed'] for r in successful]
        correlations[sweep_name] = np.corrcoef(x_vals, drift_vals)[0, 1] if len(x_vals) > 1 else 0.0

    print("Correlation Summary:")
    print(f"  Threshold vs Drift: r = {correlations.get('threshold_sweep', 0.0):.3f}")
    print(f"  Mult vs Drift: r = {correlations.get('mult_sweep', 0.0):.3f}")
    print(f"  Spread vs Drift: r = {correlations.get('spread_sweep', 0.0):.3f}")
    print()

    # Identify strongest correlation
    strongest = max(correlations.items(), key=lambda x: abs(x[1]))
    strongest_param = strongest[0].replace('_sweep', '')
    strongest_r = strongest[1]

    if abs(strongest_r) > 0.7:
        conclusion = f"{strongest_param.upper()} is PRIMARY drift control (r={strongest_r:.3f})"
        insight_type = f"{strongest_param}_primary"
    elif abs(strongest_r) > 0.4:
        conclusion = f"{strongest_param.upper()} moderately controls drift (r={strongest_r:.3f})"
        insight_type = f"{strongest_param}_moderate"
    else:
        conclusion = f"NO strong drift control parameter identified (max |r|={abs(strongest_r):.3f})"
        insight_type = "weak_control"

    print(f"📊 INSIGHT #73: Parameter Space Drift Control - {conclusion}")
    print()

    # Resolve C113 vs C115 contradiction
    threshold_r = correlations.get('threshold_sweep', 0.0)
    print(f"C113 vs C115 Contradiction Resolution:")
    print(f"  C113 finding: Threshold controls drift (r=-0.953)")
    print(f"  C116 finding: Threshold vs drift (r={threshold_r:.3f})")

    if abs(threshold_r) > 0.7:
        resolution = "C113 REPLICATED - Threshold does control drift"
    elif abs(threshold_r) < 0.3:
        resolution = "C115 VALIDATED - Threshold has minimal drift effect"
    else:
        resolution = "PARTIAL EFFECT - Threshold moderately affects drift"

    print(f"  Resolution: {resolution}")
    print()

    print("="*80)

    # Save results
    results_dir = Path(__file__).parent / "results" / "drift_parameter_space"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle116_drift_parameter_space.json"

    output_data = {
        'experiment': 'cycle116_drift_parameter_space',
        'sweeps': sweeps,
        'cycles': cycles,
        'agent_cap': agent_cap,
        'all_results': all_results,
        'correlations': correlations,
        'strongest_parameter': strongest_param,
        'strongest_correlation': strongest_r,
        'insight_type': insight_type,
        'c113_resolution': resolution,
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
