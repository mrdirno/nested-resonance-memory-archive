"""
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""


#!/usr/bin/env python3
"""
Cycle 117: Ultra-Long Timescale Validation - Testing Framework Robustness at 10,000 Cycles

Research Context:
  C111-C116: Complete mechanistic arc validated
  - Threshold controls agent lifespans (C115)
  - Lifespans control turnover rate (C111)
  - Turnover rate controls drift (C111, C113, C116)
  - Single causal chain: threshold → lifespans → turnover → drift
  - Perfect replication: C116 r=-0.945 vs C113 r=-0.953

Research Gap:
  All experiments limited to 1000 cycles (short-term validation)
  Unknown if threshold-drift relationship holds at extreme timescales
  NRM "no equilibrium" principle untested at 10,000+ cycles
  Potential for saturation, depletion, or emergent long-term phenomena

Key Question:
  Does the C111-C116 mechanistic framework remain valid at 10x longer timescales?

Hypotheses to Test:
  1. **Robust Relationship**: Threshold-drift correlation persists at 10,000 cycles
  2. **Saturation Effect**: Drift saturates/plateaus after extended duration
  3. **Depletion Effect**: System exhausts phase space, drift decreases
  4. **Emergent Phenomena**: New long-term patterns appear (e.g., meta-attractors)
  5. **NRM "No Equilibrium"**: System maintains perpetual motion indefinitely

Research Question:
  Test threshold-drift relationship at 10,000 cycles to validate mechanistic framework
  and probe for long-term phenomena invisible at 1000-cycle scale.

Test Conditions:
  **THRESHOLD RANGE**: 300, 500, 700 (captures full drift spectrum from C116)
    - Fixed: mult=1.0, spread=0.2, agent_cap=15
    - Expected: Maintain threshold-drift correlation or reveal saturation

Metrics:
  - Drift speed across full 10,000 cycles
  - Drift speed in epochs (0-1000, 1000-2000, ..., 9000-10000)
  - Agent lifespan statistics
  - Attractor stability metrics
  - Pattern diversity evolution
  - System health (memory, agents, patterns)

Expected Outcome:
  - If robust → threshold-drift correlation holds (r similar to C116's -0.945)
  - If saturation → drift decreases over time (early high, late low)
  - If depletion → system behavior degrades or stabilizes
  - If emergent → new phenomena appear at >1000 cycle timescale

Publication Value:
  - **HIGH**: Validates C111-C116 framework at extreme timescales
  - **Robust**: Demonstrates stability of mechanistic findings
  - **Novel**: First 10,000-cycle systematic study
  - **Framework-Testing**: Tests NRM "no equilibrium" at unprecedented duration
  - **Practical**: Establishes operational limits or confirms scalability
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

def run_ultralong_experiment(threshold, cycles, agent_cap=15, mult=1.0, spread=0.2):
    """Run 10,000-cycle experiment to test framework robustness."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Track agent lifespans
    agent_spawn_cycles = {}
    burst_events = []

    # Track attractors at checkpoints
    checkpoint_interval = 1000
    checkpoints = list(range(checkpoint_interval, cycles + 1, checkpoint_interval))
    checkpoint_data = {}
    attractor_history = []

    # Epoch analysis (10 epochs of 1000 cycles each)
    epoch_size = 1000
    epoch_drift = []

    print(f"\nRunning threshold={threshold} for {cycles} cycles...")
    print(f"Checkpoints every {checkpoint_interval} cycles")
    print(f"Epoch analysis: {cycles//epoch_size} epochs")

    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Progress indicator
        if cycle % 100 == 0:
            elapsed = time.time() - start_time
            rate = cycle / elapsed
            remaining = (cycles - cycle) / rate
            print(f"  Cycle {cycle:5d}/{cycles} ({cycle/cycles*100:5.1f}%) | {rate:6.1f} cyc/s | ETA: {remaining/60:5.1f} min", end='\r', flush=True)

        # Spawn agents
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_id = agent_ids[-1]
                    agent_spawn_cycles[newest_id] = cycle
                    newest_agent = swarm.agents[newest_id]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, mult, spread=spread, count=5)
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

            # Calculate drift for this epoch
            epoch_start = cycle - checkpoint_interval
            epoch_attractors = [a[1] for a in attractor_history if a[0] > epoch_start]
            epoch_changes = sum(1 for i in range(1, len(epoch_attractors)) if epoch_attractors[i] != epoch_attractors[i-1])
            epoch_drift_rate = epoch_changes / (checkpoint_interval / 100)  # Per 100 cycles
            epoch_drift.append(epoch_drift_rate)

            checkpoint_data[cycle] = {
                'attractor': str(dominant) if dominant else None,
                'fraction': fraction,
                'unique_patterns': unique_patterns,
                'global_memory_size': len(swarm.global_memory),
                'agent_count': len(swarm.agents),
                'epoch_drift': epoch_drift_rate
            }

            print(f"\n  Checkpoint {cycle:5d}: Agents={len(swarm.agents):2d} | Patterns={unique_patterns:4d} | Drift={epoch_drift_rate:.2f}/100cyc | Fraction={fraction:.2%}")

        # Record attractor (every 100 cycles for drift calculation)
        if cycle % 100 == 0:
            attractor_history.append((cycle, str(dominant) if dominant else None))

    print()  # New line after progress

    duration = time.time() - start_time

    # Calculate overall drift
    attractor_changes = sum(1 for i in range(1, len(attractor_history)) if attractor_history[i][1] != attractor_history[i-1][1])
    observation_cycles = cycles - 100  # Exclude first 100 cycles
    overall_drift = (attractor_changes / (observation_cycles / 100)) if observation_cycles > 0 else 0

    # Analyze ages
    ages = [e['age'] for e in burst_events]
    age_histogram = Counter(ages)

    return {
        'threshold': threshold,
        'multiplier': mult,
        'spread': spread,
        'agent_cap': agent_cap,
        'cycles': cycles,
        'duration': duration,
        'overall_drift': overall_drift,
        'attractor_changes': attractor_changes,
        'epoch_drift': epoch_drift,
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
    print("CYCLE 117: ULTRA-LONG TIMESCALE VALIDATION (10,000 CYCLES)")
    print("="*80)
    print()
    print("Testing C111-C116 mechanistic framework at 10x longer timescale")
    print()
    print("C111-C116 Findings:")
    print("  - Threshold controls drift (r=-0.945)")
    print("  - Threshold controls agent lifespans")
    print("  - Lifespans control turnover rate")
    print("  - Turnover controls drift speed")
    print()
    print("Research Question: Does this framework hold at 10,000 cycles?")
    print()
    print("Test Conditions:")
    print("  - Thresholds: 300, 500, 700 (full spectrum)")
    print("  - Cycles: 10,000 per condition (10x baseline)")
    print("  - Checkpoints: Every 1000 cycles (10 total)")
    print("  - Epoch analysis: Drift per 1000-cycle epoch")
    print()

    cycles = 10000
    agent_cap = 15
    mult = 1.0
    spread = 0.2

    thresholds = [300, 500, 700]

    print(f"Configuration:")
    print(f"  Conditions: {len(thresholds)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(thresholds) * cycles:,}")
    print(f"  Agent cap: {agent_cap} (fixed)")
    print(f"  Estimated duration: ~{len(thresholds) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, threshold in enumerate(thresholds):
        print(f"\n[{i+1}/{len(thresholds)}] THRESHOLD = {threshold}")
        print("-" * 80)

        try:
            result = run_ultralong_experiment(threshold, cycles, agent_cap, mult, spread)
            results.append(result)

            drift = result['overall_drift']
            mean_age = result['burst_stats']['mean_age']
            median_age = result['burst_stats']['median_age']
            epoch_drift_mean = np.mean(result['epoch_drift'])
            epoch_drift_std = np.std(result['epoch_drift'])

            print(f"\n  ✓ COMPLETE: Drift={drift:.2f}/100cyc | Age: μ={mean_age:.2f}, med={median_age:.1f}")
            print(f"    Epoch drift: μ={epoch_drift_mean:.2f}±{epoch_drift_std:.2f}")
            time.sleep(0.05)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            results.append({
                'threshold': threshold, 'mult': mult, 'spread': spread,
                'error': str(e)
            })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"ULTRA-LONG TIMESCALE ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 2:
        print("Threshold-Drift Relationship at 10,000 Cycles:")
        print(f"{'Threshold':^12} | {'Overall Drift':^14} | {'Mean Age':^12} | {'Epoch Drift':^20}")
        print("-" * 65)

        thresholds_tested = []
        drifts = []
        ages = []

        for r in successful:
            thresh = r['threshold']
            drift = r['overall_drift']
            mean_age = r['burst_stats']['mean_age']
            epoch_drift_mean = np.mean(r['epoch_drift'])
            epoch_drift_std = np.std(r['epoch_drift'])

            thresholds_tested.append(thresh)
            drifts.append(drift)
            ages.append(mean_age)

            print(f"{thresh:^12d} | {drift:^14.2f} | {mean_age:^12.2f} | {epoch_drift_mean:.2f} ± {epoch_drift_std:.2f}")

        print()

        # Calculate correlation
        if len(thresholds_tested) > 1:
            correlation = np.corrcoef(thresholds_tested, drifts)[0, 1]
        else:
            correlation = 0.0

        print(f"Correlation (Threshold vs Drift): r = {correlation:.3f}")
        print(f"C116 correlation (1000 cycles): r = -0.945")
        print(f"Drift range: {min(drifts):.2f} - {max(drifts):.2f} (Δ={max(drifts)-min(drifts):.2f})")
        print()

        # Determine validity
        if abs(correlation) > 0.8:
            if abs(correlation - (-0.945)) < 0.1:
                validity = "PERFECT REPLICATION"
                insight_type = "robust_framework"
            else:
                validity = "STRONG CORRELATION MAINTAINED"
                insight_type = "modified_strength"
        elif abs(correlation) > 0.4:
            validity = "MODERATE CORRELATION (WEAKENED)"
            insight_type = "partial_saturation"
        else:
            validity = "CORRELATION LOST (SATURATION/DEPLETION)"
            insight_type = "breakdown"

        print(f"📊 INSIGHT #74: Ultra-Long Timescale Validation - {validity}")
        print(f"   - Tested 10,000 cycles (10x baseline)")
        print(f"   - Threshold-drift correlation: r={correlation:.3f}")
        print(f"   - Framework validity: {validity}")
        print()

        # Epoch analysis
        print("Epoch-by-Epoch Drift Evolution:")
        for i, r in enumerate(successful):
            thresh = r['threshold']
            epoch_drifts = r['epoch_drift']
            print(f"\n  Threshold {thresh}:")
            for j, ed in enumerate(epoch_drifts):
                epoch_num = j + 1
                epoch_range = f"{epoch_num*1000-999:5d}-{epoch_num*1000:5d}"
                print(f"    Epoch {epoch_num} ({epoch_range}): {ed:.2f}/100cyc")

        # Test for saturation/trends
        print("\nSaturation Analysis:")
        for r in successful:
            thresh = r['threshold']
            epoch_drifts = r['epoch_drift']

            if len(epoch_drifts) > 1:
                # Linear regression on epoch drift over time
                epochs = np.arange(len(epoch_drifts))
                slope, intercept = np.polyfit(epochs, epoch_drifts, 1)

                if abs(slope) < 0.01:
                    trend = "STABLE (no saturation)"
                elif slope < -0.01:
                    trend = "DECREASING (saturation)"
                else:
                    trend = "INCREASING (escalation)"

                print(f"  Threshold {thresh}: {trend} (slope={slope:.3f})")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        print(f"   Only {len(successful)}/{len(thresholds)} runs completed successfully")
        insight_type = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "ultralong_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle117_ultralong_validation.json"

    output_data = {
        'experiment': 'cycle117_ultralong_validation',
        'cycles': cycles,
        'thresholds': thresholds,
        'results': results,
        'correlation': correlation if 'correlation' in locals() else None,
        'validity': validity if 'validity' in locals() else None,
        'insight_type': insight_type if 'insight_type' in locals() else False,
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
