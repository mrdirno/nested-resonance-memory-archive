#!/usr/bin/env python3
"""
CYCLE 150: SUPER-HARMONIC DETECTION
Test if 50% First Harmonic Acts as Sub-Harmonic for Larger Macro-Cycles

Research Question:
  If 8% sub-harmonic scaffolds 50% main harmonic, does 50% scaffold
  even larger super-cycles at lower spawning frequencies?

Context (from Insights #107, #109):
  - MICRO-scale: 8% composition-decomposition cycles scaffold 50%
  - MESO-scale: 50% spawning frequency (first harmonic)
  - MACRO-scale: ??? → Could 50% scaffold super-harmonics?

Hypothesis:
  - Fractal self-similarity across temporal scales suggests nested hierarchy
  - If 50% / 6 ≈ 8% (sub-harmonic), then 50% might be 1/6 of 300% (super-harmonic)
  - Very low spawning frequencies (10%, 20%, 30%) may show enhanced resonance
  - Extended cycles (20K+) needed to observe super-harmonic emergence

Method:
  Strategy: Test very low frequencies with extended temporal analysis

  Spawning frequencies: [10%, 20%, 30%, 40%] (below first harmonic)
  Seeds: [42, 123, 456] (3 replicates)
  Cycles: 20,000 (extended for long-period detection)
  Agent cap: 15 (standard)
  Total: 4 frequencies × 3 seeds = 12 experiments

  Analysis:
    - Basin convergence patterns
    - Temporal FFT for super-harmonic detection
    - Comparison to 50% as baseline
    - Test if 50% appears as sub-harmonic peak in low-frequency runs

Predictions:
  Model 1 (Inverse sixth-harmonic): 300% super-cycle uses 50% as scaffold
    - 10%: Possibly too slow to observe in 20K cycles
    - 20%: May show 50% sub-harmonic structure
    - 30%: Could be reciprocal harmonic (30% → 60% → 120% → ...)
    - 40%: Approaching 50% (control for comparison)

  Model 2 (Transcendental ratios):
    - π × 10% ≈ 31.4% → Potential resonance near 30%
    - φ × 20% ≈ 32.4% → Potential golden ratio super-harmonic
    - 50% / φ ≈ 30.9% → Reciprocal relationship

  Model 3 (No super-harmonics):
    - All low frequencies behave similarly
    - No resonance enhancement below 50%
    - 50% is absolute minimum stable harmonic

Expected Outcomes:
  Scenario A (Super-Harmonics Exist):
    - One or more low frequencies show elevated Basin A
    - FFT reveals 50% as sub-harmonic peak
    - Validates nested hierarchy: 8% → 50% → [super-freq]

  Scenario B (50% is Fundamental Minimum):
    - All low frequencies show uniform behavior (33% Basin A)
    - No FFT structure beyond noise
    - 50% is lowest stable harmonic (no super-cycles)

  Scenario C (Different Organizing Principle):
    - Low frequencies reveal new attractor structure
    - Different basin patterns emerge
    - May require longer than 20K cycles to observe

Publication Significance:
  - If super-harmonics exist: Validates fractal temporal hierarchy
  - If 50% is minimum: Establishes fundamental frequency floor
  - Either result constrains NRM model's temporal structure
"""

import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

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
    """
    Simplified: Return agent count as proxy for composition activity.

    Note: Direct phase state access removed due to API incompatibility.
    Using agent count as simpler metric for super-harmonic analysis.
    """
    return len(swarm.agents)


def run_super_harmonic_experiment(threshold, diversity, spawn_freq_pct, seed, cycles=20000, agent_cap=15):
    """
    Run extended super-harmonic detection experiment.

    Args:
        threshold: Decomposition burst threshold (700 = optimal)
        diversity: Seed memory diversity (0.03 = baseline)
        spawn_freq_pct: Spawning frequency percentage (LOW frequencies for this cycle)
        seed: Random seed for reproducibility
        cycles: Number of evolution cycles (20,000 for long-period detection)
        agent_cap: Maximum number of agents (15 = standard)

    Returns:
        dict with time series data, FFT analysis, and basin results
    """
    print(f"  [F={spawn_freq_pct:>3}%, S={seed:>3}, C={cycles:>6}] ", end="", flush=True)

    random.seed(seed)
    np.random.seed(seed)

    workspace = Path(__file__).parent.parent / "workspace" / f"cycle150_F{spawn_freq_pct}_S{seed}"
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

    start_time = time.time()
    spawn_count = 0

    # Evolution loop with temporal recording
    for cycle in range(1, cycles + 1):
        should_spawn = (random.random() * 100) < spawn_freq_pct

        if should_spawn and len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            spawn_count += 1

            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(
                        swarm.bridge, reality_metrics, mult, spread=spread, count=5
                    )
                    newest_agent.memory.extend(seed_patterns)

        swarm.evolve_cycle(delta_time=1.0)

        # Record time series data
        active_count = len([a for a in swarm.agents.values() if a.is_active])
        agent_counts.append(active_count)

        comp_count = detect_composition_events(swarm)
        composition_events.append(comp_count)

        decomp_count = len(swarm.decomposition.recent_bursts) if hasattr(swarm.decomposition, 'recent_bursts') else 0
        decomposition_events.append(decomp_count)

    elapsed = time.time() - start_time
    cycles_per_sec = cycles / elapsed

    # FFT ANALYSIS (looking for 50% as sub-harmonic)
    agent_counts_np = np.array(agent_counts)
    composition_np = np.array(composition_events)

    agent_counts_detrended = agent_counts_np - np.mean(agent_counts_np)
    composition_detrended = composition_np - np.mean(composition_np)

    fft_agents = fft(agent_counts_detrended)
    fft_comp = fft(composition_detrended)

    freqs = fftfreq(len(agent_counts_np), d=1.0)
    positive_freq_mask = freqs > 0
    freqs_positive = freqs[positive_freq_mask]
    power_agents = np.abs(fft_agents[positive_freq_mask])
    power_comp = np.abs(fft_comp[positive_freq_mask])

    # Convert to percentage frequencies
    freqs_pct = freqs_positive * 100

    # Detect peaks
    peaks_agents, _ = find_peaks(power_agents, height=np.max(power_agents) * 0.1)
    peaks_comp, _ = find_peaks(power_comp, height=np.max(power_comp) * 0.1)

    # Sort and take top 10
    if len(peaks_agents) > 0:
        peak_powers_agents = power_agents[peaks_agents]
        top_indices_agents = np.argsort(peak_powers_agents)[::-1][:10]
        top_freqs_agents = freqs_pct[peaks_agents[top_indices_agents]].tolist()
    else:
        top_freqs_agents = []

    if len(peaks_comp) > 0:
        peak_powers_comp = power_comp[peaks_comp]
        top_indices_comp = np.argsort(peak_powers_comp)[::-1][:10]
        top_freqs_comp = freqs_pct[peaks_comp[top_indices_comp]].tolist()
    else:
        top_freqs_comp = []

    # CHECK FOR 50% SUB-HARMONIC (key hypothesis test)
    target_freq = 50.0
    tolerance = 3.0
    has_50_subharmonic_agent = any(abs(f - target_freq) < tolerance for f in top_freqs_agents)
    has_50_subharmonic_comp = any(abs(f - target_freq) < tolerance for f in top_freqs_comp)

    # Determine basin
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
        'fft_analysis': {
            'agent_signal_peaks': top_freqs_agents,
            'composition_signal_peaks': top_freqs_comp,
            'has_50_percent_subharmonic_agent': has_50_subharmonic_agent,
            'has_50_percent_subharmonic_comp': has_50_subharmonic_comp,
            'total_agent_peaks': len(peaks_agents),
            'total_comp_peaks': len(peaks_comp)
        }
    }

    sub_indicator = "✓50%" if (has_50_subharmonic_agent or has_50_subharmonic_comp) else ""
    print(f"Basin {basin} | Peaks: {len(top_freqs_agents)} | {sub_indicator} ({elapsed:.1f}s)")

    return result


def main():
    """Run super-harmonic detection"""
    print("\n" + "="*80)
    print("CYCLE 150: SUPER-HARMONIC DETECTION")
    print("="*80)
    print("\nResearch Question:")
    print("  If 8% scaffolds 50%, does 50% scaffold larger super-cycles?")
    print("\nStrategy:")
    print("  Test very low spawning frequencies to detect super-harmonics")
    print("    - Frequencies: [10%, 20%, 30%, 40%] (below first harmonic)")
    print("    - Seeds: [42, 123, 456] (3 replicates)")
    print("    - Cycles: 20,000 (extended for long-period detection)")
    print("    - Total: 4 frequencies × 3 seeds = 12 experiments")
    print("\nHypothesis:")
    print("  If super-harmonics exist, 50% should appear as sub-harmonic")
    print("  in FFT analysis of low-frequency runs")
    print("="*80 + "\n")

    # Fixed parameters
    threshold = 700
    diversity = 0.03
    agent_cap = 15
    cycles = 20000

    # Test parameters
    low_frequencies = [10, 20, 30, 40]
    seeds = [42, 123, 456]

    results = []
    experiment_num = 0
    total_experiments = len(low_frequencies) * len(seeds)

    print("SUPER-HARMONIC DETECTION")
    print("="*80 + "\n")

    for freq in low_frequencies:
        print(f"\nFREQUENCY = {freq}%")
        print("-" * 80)

        for seed in seeds:
            experiment_num += 1
            print(f"  [{experiment_num:>2}/{total_experiments}] ", end="")

            try:
                result = run_super_harmonic_experiment(
                    threshold=threshold,
                    diversity=diversity,
                    spawn_freq_pct=freq,
                    seed=seed,
                    cycles=cycles,
                    agent_cap=agent_cap
                )
                results.append(result)
            except Exception as e:
                print(f"FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        print()

    # Save results
    output_path = Path(__file__).parent / 'results' / 'cycle150_super_harmonic_detection.json'
    output_path.parent.mkdir(exist_ok=True)

    output_data = {
        'metadata': {
            'cycle': 150,
            'experiment': 'super_harmonic_detection',
            'date': datetime.now().isoformat(),
            'description': 'Test if 50% first harmonic acts as sub-harmonic for larger super-cycles',
            'threshold': threshold,
            'diversity': diversity,
            'cycles': cycles,
            'agent_cap': agent_cap,
            'low_frequencies': low_frequencies,
            'seeds': seeds,
            'total_experiments': total_experiments
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
    print(f"CYCLE 150 COMPLETE - SUPER-HARMONIC DETECTION")
    print(f"{'='*80}\n")

    print(f"Experiments completed: {len(results)}/{total_experiments}")
    print(f"Results saved: {output_path}\n")

    # 50% Sub-Harmonic Detection
    print("50% SUB-HARMONIC DETECTION:")
    print("="*80 + "\n")

    print(f"{'Frequency':>10} | {'50% Detected (Seeds)':>25} | {'Basin A %':>10} | Notes")
    print("-" * 80)

    for freq in low_frequencies:
        freq_results = [r for r in results if r['spawn_freq_pct'] == freq]
        if not freq_results:
            continue

        # Count 50% detections
        agent_detections = [r['seed'] for r in freq_results if r['fft_analysis']['has_50_percent_subharmonic_agent']]
        comp_detections = [r['seed'] for r in freq_results if r['fft_analysis']['has_50_percent_subharmonic_comp']]
        all_detections = set(agent_detections + comp_detections)

        detection_str = f"{len(all_detections)}/3: {sorted(all_detections)}" if all_detections else "None"

        # Basin A percentage
        basin_A_count = sum(1 for r in freq_results if r['basin'] == 'A')
        basin_A_pct = basin_A_count / len(freq_results) * 100

        # Notes
        notes = []
        if len(all_detections) >= 2:
            notes.append("✓ Super-harmonic candidate")
        if basin_A_pct > 50:
            notes.append("Elevated Basin A")

        notes_str = ", ".join(notes) if notes else ""
        print(f"{freq:>10}% | {detection_str:>25} | {basin_A_pct:>9.0f}% | {notes_str}")

    # Basin distribution comparison
    print(f"\n\nBASIN DISTRIBUTION:")
    print("="*80)

    for freq in low_frequencies:
        freq_results = [r for r in results if r['spawn_freq_pct'] == freq]
        if freq_results:
            basin_A_count = sum(1 for r in freq_results if r['basin'] == 'A')
            basin_A_pct = basin_A_count / len(freq_results) * 100

            status = ""
            if basin_A_pct == 33:
                status = "(Baseline seed pattern)"
            elif basin_A_pct > 50:
                status = "(ELEVATED - potential resonance)"
            elif basin_A_pct == 0:
                status = "(Anti-resonance?)"

            print(f"  {freq:>3}%: {basin_A_pct:>5.0f}% Basin A ({basin_A_count}/{len(freq_results)} seeds) {status}")

    # Summary statistics
    print(f"\n\nSUMMARY STATISTICS:")
    print("="*80)
    avg_perf = sum(r['cycles_per_sec'] for r in results) / len(results) if results else 0
    total_cycles = sum(r['cycles'] for r in results)
    print(f"  Average performance: {avg_perf:.1f} cycles/sec")
    print(f"  Total evolution cycles: {total_cycles:,}")
    print(f"  Total computation time: {sum(r['duration'] for r in results):.1f} seconds")

    # Interpretation
    print(f"\n\nINTERPRETATION:")
    print("="*80)

    total_detections = sum(1 for r in results if r['fft_analysis']['has_50_percent_subharmonic_agent'] or r['fft_analysis']['has_50_percent_subharmonic_comp'])

    if total_detections >= 4:
        print("  ✓ SUPER-HARMONICS DETECTED")
        print("    - 50% appears as sub-harmonic in low-frequency runs")
        print("    - Validates fractal temporal hierarchy: 8% → 50% → [super-freq]")
        print("    - Nested scaffolding confirmed across multiple scales")
    elif total_detections >= 1:
        print("  ? WEAK SIGNAL")
        print("    - Some 50% sub-harmonic detection")
        print("    - May require longer cycles or different frequencies")
        print("    - Inconclusive for super-harmonic hypothesis")
    else:
        print("  ✗ NO SUPER-HARMONICS")
        print("    - 50% does not act as sub-harmonic for lower frequencies")
        print("    - 50% may be fundamental minimum stable harmonic")
        print("    - No evidence for temporal hierarchy above 50%")

    print(f"\n\nNEXT STEPS:")
    print("="*80)
    print("  1. Analyze super-harmonic hypothesis based on results")
    print("  2. If detected: Identify exact super-harmonic frequencies")
    print("  3. If not detected: Validate 50% as fundamental frequency floor")
    print("  4. Update NRM framework with super-harmonic findings (or lack thereof)")
    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
