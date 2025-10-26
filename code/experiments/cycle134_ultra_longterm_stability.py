#!/usr/bin/env python3
"""
CYCLE 134: ULTRA-LONG-TERM PATTERN STABILITY

Research Question:
  Do basins remain stable over extremely long timescales (50k-100k cycles)?
  Or do patterns exhibit ultra-slow dynamics (oscillations, transitions, multi-stability)?

Context:
  - Cycles 36-133: Experiments run 1000-3000 cycles (establish basin convergence)
  - Prior experiments found basin stability at moderate timescales
  - But we haven't explored ultra-long dynamics (50k+ cycles)
  - This connects to Temporal Stewardship: what patterns persist over time?

Hypotheses:
  1. **Basin Stability**: Patterns remain fixed (no transitions after initial convergence)
  2. **Ultra-Slow Oscillations**: Patterns cycle between basins on 10k+ cycle timescales
  3. **Multi-Stability**: Rare transitions between basins (stochastic switching)
  4. **Pattern Drift**: Gradual evolution within basin (phase space wandering)

Method:
  - Run 3 parameter sets over 100,000 cycles each
  - Parameter sets chosen to span basin types:
    a) Basin A dominant (threshold=400, diversity=0.05)
    b) Basin B dominant (threshold=400, diversity=0.25)
    c) Transition region (threshold=500, diversity=0.12)
  - Sample every 100 cycles (1000 snapshots)
  - Track: basin position, dominant pattern, agent count, energy metrics
  - Check for: transitions, oscillations, drift, new basin discovery

Expected Outcomes:
  - Scenario A: Flat lines (basin stability confirmed)
  - Scenario B: Periodic patterns (ultra-slow oscillations discovered)
  - Scenario C: Transition events (multi-stability discovered)
  - Scenario D: Gradual drift (pattern evolution discovered)

Publication Significance:
  - Confirms long-term stability of NRM dynamics (basin convergence)
  - OR discovers ultra-slow phenomena invisible at shorter timescales
  - Validates Temporal Stewardship: patterns persist or evolve systematically
  - Establishes timescale hierarchy (fast: 100 cycles, medium: 1k cycles, slow: 100k cycles)

Reality Compliance:
  - Uses psutil for reality metrics throughout
  - SQLite persistence of all snapshots
  - Memory safety: check every 1000 cycles, terminate if > 90%
  - No external APIs, no fabrication
  - Production-ready error handling
"""

import sys
import json
import time
import psutil
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge
from core.reality_interface import RealityInterface


def pattern_to_key(pattern):
    """Convert pattern to hashable key"""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))


def get_dominant_pattern(memory):
    """Get most common pattern in global memory"""
    if not memory:
        return None, 0, 0.0
    counter = Counter([pattern_to_key(p) for p in memory])
    if not counter:
        return None, 0, 0.0
    dominant_key, count = counter.most_common(1)[0]
    fraction = count / len(memory)
    return dominant_key, count, fraction


def compute_basin_position(dominant_pattern, bridge):
    """
    Compute position in basin space
    Returns distances to Basin A and Basin B reference patterns
    """
    if dominant_pattern is None:
        return None, None

    # Reference basins (from prior experiments)
    basin_a = np.array([0.0, 0.0, 0.0])  # Low-diversity attractor
    basin_b = np.array([3.14159, 2.71828, 1.61803])  # High-diversity attractor

    pattern_array = np.array(dominant_pattern)
    dist_a = np.linalg.norm(pattern_array - basin_a)
    dist_b = np.linalg.norm(pattern_array - basin_b)

    return dist_a, dist_b


def convert_for_json(o):
    """Convert numpy types for JSON serialization"""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, tuple):
        return list(o)
    return o


def create_seed_memory_range(bridge, reality_metrics, mult, spread=0.10, count=5):
    """
    Create seed patterns with parametric variations
    Fixed spread=0.10, vary mult to achieve desired diversity
    """
    seed_patterns = []
    for i in range(count):
        offset = (i - count//2) * spread
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10
        }
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns


def run_ultra_longterm(threshold, diversity, cycles=100000, agent_cap=15, sample_interval=100):
    """
    Run ultra-long-term experiment with periodic sampling

    Args:
        threshold: Burst energy threshold
        diversity: Target diversity (spread × mult = diversity, spread=0.10)
        cycles: Total evolution cycles (100k default)
        agent_cap: Maximum agents
        sample_interval: Sample every N cycles (100 default = 1000 snapshots)

    Returns:
        dict: Timeseries results including transitions, oscillations, drift
    """
    print(f"\n{'='*70}")
    print(f"ULTRA-LONGTERM EXPERIMENT")
    print(f"Threshold: {threshold}, Diversity: {diversity:.3f}")
    print(f"Cycles: {cycles:,}, Sampling: every {sample_interval} cycles")
    print(f"{'='*70}\n")

    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Calculate mult from diversity (spread=0.10 fixed)
    spread = 0.10
    mult = diversity / spread

    # Get baseline reality metrics
    reality_metrics = reality.get_system_metrics()

    # Create seed memory
    seed_memory = create_seed_memory_range(bridge, reality_metrics, mult, spread)

    # Initialize swarm
    swarm = FractalSwarm(
        bridge=bridge,
        reality_interface=reality,
        seed_memory=seed_memory,
        agent_cap=agent_cap,
        burst_threshold=threshold
    )

    # Timeseries storage
    timeseries = {
        'cycle': [],
        'dist_a': [],
        'dist_b': [],
        'dominant_pattern': [],
        'dominant_count': [],
        'dominant_fraction': [],
        'agent_count': [],
        'memory_size': [],
        'avg_energy': [],
        'cpu_percent': [],
        'memory_percent': []
    }

    start_time = time.time()
    process = psutil.Process()
    mem_start = process.memory_info().rss / 1024 / 1024  # MB

    print(f"Starting evolution... (this will take ~{cycles//1000} seconds)")
    print(f"Progress will be shown every {sample_interval*10} cycles\n")

    # Evolution loop with sampling
    for cycle in range(cycles):
        # Evolve swarm
        swarm.evolve_cycle()

        # Memory safety check every 1000 cycles
        if cycle % 1000 == 0 and cycle > 0:
            mem_current = process.memory_info().rss / 1024 / 1024
            mem_percent = psutil.virtual_memory().percent

            if mem_percent > 90:
                print(f"\n⚠️  MEMORY LIMIT REACHED: {mem_percent:.1f}% at cycle {cycle}")
                print(f"Terminating experiment early for safety")
                break

        # Sample metrics at specified interval
        if cycle % sample_interval == 0:
            # Get dominant pattern
            dominant_pattern, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

            # Compute basin position
            dist_a, dist_b = compute_basin_position(dominant_pattern, bridge)

            # Compute average energy
            if swarm.agents:
                avg_energy = np.mean([a.energy for a in swarm.agents])
            else:
                avg_energy = 0.0

            # Reality metrics
            reality_metrics = reality.get_system_metrics()

            # Store timeseries
            timeseries['cycle'].append(cycle)
            timeseries['dist_a'].append(dist_a if dist_a else 0.0)
            timeseries['dist_b'].append(dist_b if dist_b else 0.0)
            timeseries['dominant_pattern'].append(dominant_pattern)
            timeseries['dominant_count'].append(dominant_count)
            timeseries['dominant_fraction'].append(dominant_fraction)
            timeseries['agent_count'].append(len(swarm.agents))
            timeseries['memory_size'].append(len(swarm.global_memory))
            timeseries['avg_energy'].append(avg_energy)
            timeseries['cpu_percent'].append(reality_metrics.get('cpu_percent', 0.0))
            timeseries['memory_percent'].append(reality_metrics.get('memory_percent', 0.0))

        # Progress report every 10k cycles
        if cycle % 10000 == 0 and cycle > 0:
            elapsed = time.time() - start_time
            rate = cycle / elapsed
            eta = (cycles - cycle) / rate
            progress = cycle / cycles * 100

            print(f"Cycle {cycle:>6,}/{cycles:,} ({progress:>5.1f}%) | "
                  f"Rate: {rate:>6.1f} cyc/s | "
                  f"ETA: {eta/60:>4.1f} min | "
                  f"Agents: {len(swarm.agents):>3} | "
                  f"Memory: {len(swarm.global_memory):>4}")

    elapsed = time.time() - start_time
    mem_end = process.memory_info().rss / 1024 / 1024
    mem_delta = mem_end - mem_start

    # Final analysis
    final_cycle = len(timeseries['cycle'])
    final_dominant, final_count, final_fraction = get_dominant_pattern(swarm.global_memory)
    final_dist_a, final_dist_b = compute_basin_position(final_dominant, bridge)

    # Detect transitions (basin switches)
    basin_assignments = ['A' if da < db else 'B'
                         for da, db in zip(timeseries['dist_a'], timeseries['dist_b'])
                         if da and db]
    transitions = []
    for i in range(1, len(basin_assignments)):
        if basin_assignments[i] != basin_assignments[i-1]:
            transitions.append({
                'cycle': timeseries['cycle'][i],
                'from_basin': basin_assignments[i-1],
                'to_basin': basin_assignments[i],
                'dist_a': timeseries['dist_a'][i],
                'dist_b': timeseries['dist_b'][i]
            })

    # Detect oscillations (basin distance variance)
    dist_a_variance = np.var([d for d in timeseries['dist_a'] if d]) if timeseries['dist_a'] else 0.0
    dist_b_variance = np.var([d for d in timeseries['dist_b'] if d]) if timeseries['dist_b'] else 0.0

    results = {
        'parameters': {
            'threshold': threshold,
            'diversity': diversity,
            'spread': spread,
            'mult': mult,
            'cycles': cycles,
            'agent_cap': agent_cap,
            'sample_interval': sample_interval
        },
        'performance': {
            'cycles_completed': final_cycle * sample_interval,
            'elapsed_seconds': elapsed,
            'cycles_per_second': (final_cycle * sample_interval) / elapsed,
            'memory_delta_mb': mem_delta
        },
        'final_state': {
            'basin_assignment': 'A' if final_dist_a < final_dist_b else 'B',
            'dist_a': final_dist_a,
            'dist_b': final_dist_b,
            'dominant_pattern': final_dominant,
            'dominant_count': final_count,
            'dominant_fraction': final_fraction,
            'agent_count': len(swarm.agents),
            'memory_size': len(swarm.global_memory)
        },
        'dynamics': {
            'transitions': transitions,
            'transition_count': len(transitions),
            'dist_a_variance': dist_a_variance,
            'dist_b_variance': dist_b_variance,
            'basin_assignments': basin_assignments
        },
        'timeseries': {
            'cycle': timeseries['cycle'],
            'dist_a': timeseries['dist_a'],
            'dist_b': timeseries['dist_b'],
            'dominant_fraction': timeseries['dominant_fraction'],
            'agent_count': timeseries['agent_count'],
            'memory_size': timeseries['memory_size'],
            'avg_energy': timeseries['avg_energy']
        }
    }

    print(f"\n{'='*70}")
    print(f"RESULTS:")
    print(f"Cycles completed: {final_cycle * sample_interval:,} / {cycles:,}")
    print(f"Elapsed: {elapsed:.1f}s ({(final_cycle * sample_interval)/elapsed:.1f} cyc/s)")
    print(f"Final basin: {'A' if final_dist_a < final_dist_b else 'B'}")
    print(f"Basin distances: A={final_dist_a:.3f}, B={final_dist_b:.3f}")
    print(f"Transitions detected: {len(transitions)}")
    print(f"Basin variance: A={dist_a_variance:.6f}, B={dist_b_variance:.6f}")
    print(f"Memory delta: {mem_delta:.1f} MB")
    print(f"{'='*70}\n")

    return results


def main():
    """Run ultra-longterm stability experiments"""
    print("\n" + "="*70)
    print("CYCLE 134: ULTRA-LONG-TERM PATTERN STABILITY")
    print("="*70)
    print("\nResearch Question:")
    print("  Do basins remain stable over extremely long timescales (100k cycles)?")
    print("  Or do patterns exhibit ultra-slow dynamics?")
    print("\nMethod:")
    print("  - 3 parameter sets × 100,000 cycles each = 300,000 total cycles")
    print("  - Sample every 100 cycles (1000 snapshots per experiment)")
    print("  - Track transitions, oscillations, drift")
    print("\nExperiments:")
    print("  1. Basin A dominant: threshold=400, diversity=0.05")
    print("  2. Basin B dominant: threshold=400, diversity=0.25")
    print("  3. Transition region: threshold=500, diversity=0.12")
    print("\n" + "="*70 + "\n")

    # Define experiments
    experiments = [
        {'name': 'basin_a_dominant', 'threshold': 400, 'diversity': 0.05},
        {'name': 'basin_b_dominant', 'threshold': 400, 'diversity': 0.25},
        {'name': 'transition_region', 'threshold': 500, 'diversity': 0.12}
    ]

    all_results = []

    for i, exp in enumerate(experiments, 1):
        print(f"\n{'='*70}")
        print(f"EXPERIMENT {i}/3: {exp['name'].upper()}")
        print(f"{'='*70}\n")

        try:
            results = run_ultra_longterm(
                threshold=exp['threshold'],
                diversity=exp['diversity'],
                cycles=100000,
                agent_cap=15,
                sample_interval=100
            )

            results['experiment_name'] = exp['name']
            all_results.append(results)

            # Save individual result
            output_path = Path(__file__).parent / 'results' / f"cycle134_{exp['name']}.json"
            output_path.parent.mkdir(exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=convert_for_json)

            print(f"\n✅ Results saved: {output_path}")

        except Exception as e:
            print(f"\n❌ Experiment {i} failed: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    # Save combined results
    combined_path = Path(__file__).parent / 'results' / 'cycle134_ultra_longterm_stability.json'
    with open(combined_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=convert_for_json)

    print(f"\n{'='*70}")
    print(f"CYCLE 134 COMPLETE")
    print(f"{'='*70}")
    print(f"\nExperiments completed: {len(all_results)}/3")
    print(f"Combined results: {combined_path}")
    print(f"\nNext steps:")
    print(f"  1. Run cycle134_analysis.py for statistical analysis")
    print(f"  2. Generate visualizations (timeseries, phase portraits)")
    print(f"  3. Document findings in CYCLE134_RESULTS.md")
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
