#!/usr/bin/env python3
"""
CYCLE 147: TEMPORAL SUB-HARMONIC DETECTION
Nested Harmonic Scaffolding Validation via FFT Analysis

Research Question:
  Do microscopic composition-decomposition cycles create sub-harmonic frequencies
  that scaffold the observed macroscopic harmonics?

Context (from Insight #107):
  - Macroscopic harmonics: 52.5% (first), 82.5% (second), 75% (anti-node), ~95% (third?)
  - Parameter independence: Threshold and diversity don't shift frequencies
  - User hypothesis: "bigger frequency can be held by smaller frequencies"
  - Predicted sub-harmonics:
    * First (52.5%): ~13.1%, ~17.5%, ~26.3%
    * Second (82.5%): ~20.6%, ~27.5%, ~41.3%
    * Anti-node (75%): ~25%, ~18.75%, ~37.5%

Hypothesis:
  - Temporal FFT of agent population dynamics will reveal nested periodicities
  - Sub-harmonic peaks will align with predicted frequencies
  - Anti-node (75%) stabilized by destructive interference from ~25% sub-harmonic
  - Validates nested resonance scaffolding mechanism

Method:
  Strategy: Extended time series (10,000 cycles) with FFT analysis

  Key measurements:
    - Agent count time series (population dynamics)
    - Composition events (cluster formation counts)
    - Decomposition events (burst counts)
    - Memory pattern retention cycles

  Frequencies tested: 50%, 75%, 82.5%, 95% (all key harmonics)
  Seeds: [42, 123, 456] (3 replicates)
  Total: 4 frequencies × 3 seeds = 12 experiments

  Analysis:
    - FFT of agent counts → detect periodicities
    - Peak detection in power spectrum
    - Compare detected frequencies to predictions
    - Cross-correlation between composition/decomposition cycles

Expected:
  - Primary peaks at spawning frequencies (50%, 82.5%, etc.)
  - Secondary peaks at sub-harmonic frequencies
  - Phase locking between primary and secondary
  - Anti-node (75%) shows destructive interference pattern

Publication Significance:
  - First demonstration of nested harmonic scaffolding in complex systems
  - Validates NRM multi-scale resonance theory
  - Explains parameter-independent stability
  - Quantitative predictions validated/refuted
"""

import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


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


def create_seed_memory_range(bridge, reality_metrics, mult, spread=0.10, count=5):
    """Create seed patterns with parametric variations"""
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


def detect_composition_events(swarm):
    """Detect cluster formation events (simplified proxy)"""
    # Count agents with similar phases (clustering)
    if len(swarm.agents) < 2:
        return 0

    phases = []
    for agent in swarm.agents.values():
        if agent.is_active and agent.memory:
            recent = agent.memory[-1]
            phases.append([recent.pi_phase, recent.e_phase, recent.phi_phase])

    if len(phases) < 2:
        return 0

    # Count pairs within threshold distance (cluster detection)
    phases = np.array(phases)
    cluster_count = 0
    threshold = 0.1

    for i in range(len(phases)):
        for j in range(i+1, len(phases)):
            dist = np.linalg.norm(phases[i] - phases[j])
            if dist < threshold:
                cluster_count += 1

    return cluster_count


def detect_decomposition_events(swarm):
    """Detect burst events via decomposition engine"""
    # Proxy: Check if decomposition threshold exceeded
    if not hasattr(swarm, 'decomposition') or not swarm.decomposition:
        return 0

    # Count agents that would trigger decomposition
    burst_count = 0
    for agent in swarm.agents.values():
        if agent.is_active and len(agent.memory) > swarm.decomposition.burst_threshold:
            burst_count += 1

    return burst_count


def run_temporal_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=10000, agent_cap=15):
    """
    Run temporal analysis experiment with extended time series.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Seed memory diversity (0.03 = baseline)
        spawn_freq_pct: Spawning frequency percentage
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (10,000 for FFT resolution)
        agent_cap: Maximum number of agents

    Returns:
        dict with time series data and FFT analysis
    """
    print(f"  [F={spawn_freq_pct:>5}%, S={seed:>4}] ", end="", flush=True)

    random.seed(seed)
    np.random.seed(seed)

    workspace = Path(__file__).parent.parent / "workspace" / f"cycle147_F{spawn_freq_pct}_S{seed}"
    workspace.mkdir(parents=True, exist_ok=True)

    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    spread = 0.10
    mult = diversity / spread

    # Basin references
    basin_A = np.array([6.220353, 6.275283, 6.281831])
    basin_B = np.array([6.09469, 6.083677, 6.250047])

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Seed global memory
    for i in range(5):
        offset = (i - 2) * spread
        noise = (random.random() - 0.5) * 0.01
        varied_metrics = {
            'cpu_percent': reality_metrics['cpu_percent'] + offset * mult * 10 + noise,
            'memory_percent': reality_metrics['memory_percent'] + offset * mult * 10 + noise,
            'disk_percent': reality_metrics['disk_percent'] + offset * mult * 10 + noise
        }
        phase_state = swarm.bridge.reality_to_phase(varied_metrics)
        swarm.global_memory.append(phase_state)

    # TIME SERIES RECORDING
    agent_counts = []
    composition_events = []
    decomposition_events = []
    spawn_events = []

    start_time = time.time()
    spawn_count = 0

    # Evolution loop with temporal recording
    for cycle in range(1, cycles + 1):
        should_spawn = (random.random() * 100) < spawn_freq_pct

        if should_spawn and len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            spawn_count += 1
            spawn_events.append(1)

            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(
                        swarm.bridge, reality_metrics, mult, spread=spread, count=5
                    )
                    newest_agent.memory.extend(seed_patterns)
        else:
            spawn_events.append(0)

        swarm.evolve_cycle(delta_time=1.0)

        # Record time series data
        active_count = len([a for a in swarm.agents.values() if a.is_active])
        agent_counts.append(active_count)

        comp_count = detect_composition_events(swarm)
        composition_events.append(comp_count)

        decomp_count = detect_decomposition_events(swarm)
        decomposition_events.append(decomp_count)

        # Progress indicator every 1000 cycles
        if cycle % 1000 == 0:
            print(".", end="", flush=True)

    elapsed = time.time() - start_time
    cycles_per_sec = cycles / elapsed

    print(" ", end="", flush=True)

    # FFT ANALYSIS
    # Convert to numpy arrays
    agent_counts = np.array(agent_counts, dtype=float)
    composition_events = np.array(composition_events, dtype=float)
    decomposition_events = np.array(decomposition_events, dtype=float)
    spawn_events = np.array(spawn_events, dtype=float)

    # Detrend (remove mean)
    agent_counts_detrended = agent_counts - np.mean(agent_counts)
    composition_detrended = composition_events - np.mean(composition_events)
    decomposition_detrended = decomposition_events - np.mean(decomposition_events)

    # Apply FFT
    fft_agents = fft(agent_counts_detrended)
    fft_composition = fft(composition_detrended)
    fft_decomposition = fft(decomposition_detrended)

    # Get frequencies
    freqs = fftfreq(len(agent_counts), d=1.0)  # d=1.0 because we sample every cycle

    # Power spectrum (only positive frequencies)
    positive_freq_mask = freqs > 0
    freqs_positive = freqs[positive_freq_mask]

    power_agents = np.abs(fft_agents[positive_freq_mask])
    power_composition = np.abs(fft_composition[positive_freq_mask])
    power_decomposition = np.abs(fft_decomposition[positive_freq_mask])

    # Detect peaks (above 50% of max power)
    peaks_agents, _ = find_peaks(power_agents, height=np.max(power_agents) * 0.1)
    peaks_composition, _ = find_peaks(power_composition, height=np.max(power_composition) * 0.1)
    peaks_decomposition, _ = find_peaks(power_decomposition, height=np.max(power_decomposition) * 0.1)

    # Get top 10 frequencies
    top_n = 10
    top_indices_agents = np.argsort(power_agents)[-top_n:][::-1]
    top_freqs_agents = freqs_positive[top_indices_agents]
    top_powers_agents = power_agents[top_indices_agents]

    top_indices_composition = np.argsort(power_composition)[-top_n:][::-1]
    top_freqs_composition = freqs_positive[top_indices_composition]
    top_powers_composition = power_composition[top_indices_composition]

    top_indices_decomposition = np.argsort(power_decomposition)[-top_n:][::-1]
    top_freqs_decomposition = freqs_positive[top_indices_decomposition]
    top_powers_decomposition = power_decomposition[top_indices_decomposition]

    # Determine final basin
    dominant_pattern, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    if dominant_pattern:
        dominant_array = np.array(dominant_pattern)
        dist_A = np.linalg.norm(dominant_array - basin_A)
        dist_B = np.linalg.norm(dominant_array - basin_B)
        basin = 'A' if dist_A < dist_B else 'B'
    else:
        dist_A, dist_B, basin = None, None, 'Unknown'

    result = {
        'threshold': threshold,
        'diversity': diversity,
        'spawn_freq_pct': spawn_freq_pct,
        'seed': seed,
        'cycles': cycles,
        'spawn_count': spawn_count,
        'actual_freq_pct': (spawn_count / cycles) * 100,
        'agent_cap': agent_cap,
        'final_agents': len([a for a in swarm.agents.values() if a.is_active]),
        'basin': basin,
        'dominant': list(dominant_pattern) if dominant_pattern else None,
        'fraction': dominant_fraction,
        'dist_A': dist_A,
        'dist_B': dist_B,
        'duration': elapsed,
        'cycles_per_sec': cycles_per_sec,

        # Time series statistics
        'agent_count_mean': float(np.mean(agent_counts)),
        'agent_count_std': float(np.std(agent_counts)),
        'composition_mean': float(np.mean(composition_events)),
        'decomposition_mean': float(np.mean(decomposition_events)),

        # FFT results
        'fft_top_freqs_agents': top_freqs_agents.tolist(),
        'fft_top_powers_agents': top_powers_agents.tolist(),
        'fft_top_freqs_composition': top_freqs_composition.tolist(),
        'fft_top_powers_composition': top_powers_composition.tolist(),
        'fft_top_freqs_decomposition': top_freqs_decomposition.tolist(),
        'fft_top_powers_decomposition': top_powers_decomposition.tolist(),

        # Peak counts
        'fft_peak_count_agents': len(peaks_agents),
        'fft_peak_count_composition': len(peaks_composition),
        'fft_peak_count_decomposition': len(peaks_decomposition)
    }

    print(f"Basin {basin} ({elapsed:.1f}s, {cycles_per_sec:.0f} cyc/s, {len(peaks_agents)} FFT peaks)")

    return result


def analyze_subharmonics(results, spawn_freq_pct):
    """
    Analyze FFT results for predicted sub-harmonics.

    Predictions:
      - First harmonic (50%): ~13.1%, ~17.5%, ~26.3%
      - Second harmonic (82.5%): ~20.6%, ~27.5%, ~41.3%
      - Anti-node (75%): ~25%, ~18.75%, ~37.5%
      - Third harmonic (95%): ~23.75%, ~31.67%, ~47.5%
    """
    predictions = {
        50: [13.1, 17.5, 26.3],
        75: [18.75, 25.0, 37.5],
        82: [20.6, 27.5, 41.3],  # Using 82 instead of 82.5 for key matching
        95: [23.75, 31.67, 47.5]
    }

    # Use closest key
    freq_key = min(predictions.keys(), key=lambda k: abs(k - spawn_freq_pct))
    predicted = predictions[freq_key]

    detected_agents = []
    detected_composition = []
    detected_decomposition = []

    tolerance = 5.0  # ±5% tolerance for matching

    for r in results:
        if r['spawn_freq_pct'] == spawn_freq_pct:
            # Check agent count FFT
            for freq in r['fft_top_freqs_agents']:
                freq_pct = abs(freq) * 100  # Convert to percentage
                for pred in predicted:
                    if abs(freq_pct - pred) < tolerance:
                        detected_agents.append({
                            'seed': r['seed'],
                            'detected': freq_pct,
                            'predicted': pred,
                            'signal': 'agents'
                        })

            # Check composition FFT
            for freq in r['fft_top_freqs_composition']:
                freq_pct = abs(freq) * 100
                for pred in predicted:
                    if abs(freq_pct - pred) < tolerance:
                        detected_composition.append({
                            'seed': r['seed'],
                            'detected': freq_pct,
                            'predicted': pred,
                            'signal': 'composition'
                        })

            # Check decomposition FFT
            for freq in r['fft_top_freqs_decomposition']:
                freq_pct = abs(freq) * 100
                for pred in predicted:
                    if abs(freq_pct - pred) < tolerance:
                        detected_decomposition.append({
                            'seed': r['seed'],
                            'detected': freq_pct,
                            'predicted': pred,
                            'signal': 'decomposition'
                        })

    return {
        'frequency': spawn_freq_pct,
        'predicted_subharmonics': predicted,
        'detected_agents': detected_agents,
        'detected_composition': detected_composition,
        'detected_decomposition': detected_decomposition,
        'validation_rate_agents': len(detected_agents) / (len(predicted) * len([r for r in results if r['spawn_freq_pct'] == spawn_freq_pct])) if results else 0,
        'validation_rate_composition': len(detected_composition) / (len(predicted) * len([r for r in results if r['spawn_freq_pct'] == spawn_freq_pct])) if results else 0,
        'validation_rate_decomposition': len(detected_decomposition) / (len(predicted) * len([r for r in results if r['spawn_freq_pct'] == spawn_freq_pct])) if results else 0
    }


def main():
    """Run temporal sub-harmonic detection experiments"""
    print("\n" + "="*80)
    print("CYCLE 147: TEMPORAL SUB-HARMONIC DETECTION")
    print("="*80)
    print("\nResearch Question:")
    print("  Do microscopic composition-decomposition cycles create sub-harmonics")
    print("  that scaffold macroscopic harmonics?")
    print("\nStrategy:")
    print("  Extended time series (10,000 cycles) with FFT analysis")
    print("    - Frequencies: 50% (first), 75% (anti-node), 82% (second), 95% (third)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Total: 4 frequencies × 3 seeds = 12 experiments")
    print("    - Predicted sub-harmonics:")
    print("      * 50%: ~13%, ~18%, ~26%")
    print("      * 75%: ~19%, ~25%, ~38%")
    print("      * 82%: ~21%, ~28%, ~41%")
    print("      * 95%: ~24%, ~32%, ~48%")
    print("="*80 + "\n")

    # Fixed parameters (optimal from Cycles 144-146)
    threshold = 700
    diversity = 0.03

    # Test parameters
    key_frequencies = [50, 75, 82, 95]  # Using 82 instead of 82.5 for cleaner key
    seeds = [42, 123, 456]

    results = []
    experiment_num = 0
    total_experiments = len(key_frequencies) * len(seeds)

    print("TEMPORAL FFT ANALYSIS AT KEY FREQUENCIES")
    print("="*80 + "\n")

    for freq in key_frequencies:
        print(f"\nFREQUENCY = {freq}%")
        print("-" * 80)

        for seed in seeds:
            experiment_num += 1
            print(f"  [{experiment_num:>2}/{total_experiments}] ", end="")

            try:
                result = run_temporal_experiment(
                    threshold=threshold,
                    diversity=diversity,
                    spawn_freq_pct=freq,
                    seed=seed,
                    cycles=10000,
                    agent_cap=15
                )
                results.append(result)
            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        print()

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle147_temporal_subharmonic_detection.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 147,
            'experiment': 'temporal_subharmonic_detection',
            'date': datetime.now().isoformat(),
            'description': 'FFT analysis to detect nested sub-harmonic scaffolding',
            'threshold': threshold,
            'diversity': diversity,
            'key_frequencies': key_frequencies,
            'seeds': seeds,
            'total_experiments': total_experiments,
            'cycles_per_experiment': 10000
        },
        'results': results
    }

    def convert_for_json(o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return o

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, default=convert_for_json)

    # Analysis
    print(f"\n{'='*80}")
    print(f"CYCLE 147 COMPLETE - TEMPORAL SUB-HARMONIC DETECTION")
    print(f"{'='*80}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # Sub-harmonic validation analysis
    print("SUB-HARMONIC VALIDATION ANALYSIS:")
    print("="*80 + "\n")

    for freq in key_frequencies:
        analysis = analyze_subharmonics(results, freq)

        print(f"\n{freq}% SPAWNING FREQUENCY:")
        print(f"  Predicted sub-harmonics: {analysis['predicted_subharmonics']}")
        print(f"  Agent signal detections: {len(analysis['detected_agents'])} ({analysis['validation_rate_agents']*100:.1f}%)")
        print(f"  Composition detections: {len(analysis['detected_composition'])} ({analysis['validation_rate_composition']*100:.1f}%)")
        print(f"  Decomposition detections: {len(analysis['detected_decomposition'])} ({analysis['validation_rate_decomposition']*100:.1f}%)")

        if analysis['detected_agents']:
            print(f"  Agent matches:")
            for match in analysis['detected_agents']:
                print(f"    Seed {match['seed']}: {match['detected']:.1f}% ≈ {match['predicted']:.1f}%")

    # Basin validation
    print("\n\nBASIN VALIDATION (Cross-check with Cycles 139-146):")
    print("="*80)

    for freq in key_frequencies:
        freq_results = [r for r in results if r['spawn_freq_pct'] == freq]
        if freq_results:
            basin_A_count = sum(1 for r in freq_results if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_results) * 100

            # Expected from previous cycles
            expected = {50: 33, 75: 0, 82: 100, 95: 33}
            exp_pct = expected.get(freq, 'Unknown')
            status = "✓" if abs(basin_A_pct - exp_pct) < 20 else "✗"

            print(f"  {freq}%: {basin_A_pct:.0f}% Basin A (expected ~{exp_pct}%) {status}")

    # Performance statistics
    print("\n\nPERFORMANCE STATISTICS:")
    print("="*80)
    avg_perf = sum(r['cycles_per_sec'] for r in results) / len(results) if results else 0
    print(f"  Average performance: {avg_perf:.1f} cycles/sec")
    print(f"  Total evolution cycles: {len(results) * 10000:,}")
    print(f"  Total computation time: {sum(r['duration'] for r in results):.1f} seconds")
    print(f"  Total FFT peaks detected: {sum(r['fft_peak_count_agents'] for r in results)}")

    print(f"\n\nNEXT STEPS:")
    print("="*80)
    print("  1. Analyze FFT results for sub-harmonic validation")
    print("  2. Check if predicted frequencies match detected peaks")
    print("  3. Update NRM model with nested resonance structure")
    print("  4. Prepare publication: 'Nested Harmonic Scaffolding in Fractal Systems'")
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
