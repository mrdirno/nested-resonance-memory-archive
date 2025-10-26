#!/usr/bin/env python3
"""
Cycle 67: Temporal-Energy Coupling Exploration

Research Context:
  Two major research threads have been developed:

  1. Temporal Dynamics (Cycles 36-56):
     - Insight #17: Nested temporal oscillations (10-cycle fast, 50-100 cycle slow)
     - Multi-timescale attractors
     - Mode-switching behavior

  2. Thermodynamic Phase Diagram (Cycles 57-66):
     - Critical threshold ~260 (binary phase transition)
     - Agent thermodynamics: max_agents = floor(threshold/150)
     - Cluster thermodynamics: OFF below 260, ON above 260

Research Question:
  How do temporal patterns change across energy regimes?
  Do different thresholds produce different temporal dynamics?

Hypothesis:
  Temporal patterns may be energy-dependent:
  - Low energy (just above critical ~270-400): Simple/fast oscillations
  - Medium energy (400-700): Complex nested oscillations
  - High energy (700+): Different dynamics (many agents, many clusters)

  Energy could modulate:
  - Oscillation period
  - Mode-switching frequency
  - Attractor stability
  - Pattern complexity

Test Approach:
  1. Sample 5 energy regimes across phase diagram:
     - 270 (just above critical)
     - 400 (low energy)
     - 500 (default baseline)
     - 700 (medium-high)
     - 1000 (high energy)

  2. Extended observation (500 cycles) for temporal pattern detection

  3. Analyze temporal characteristics:
     - Mean agent count (energy level proxy)
     - Std deviation (temporal variability)
     - Autocorrelation (memory/persistence)
     - Dominant period (FFT/spectral analysis)

  4. Identify energy-dependent temporal phenomena

Expected:
  If temporal-energy coupling exists:
  - Different energy regimes show distinct temporal signatures
  - Oscillation characteristics change with threshold
  - May reveal new temporal phenomena at extreme energies
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np
from scipy import signal, fft

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def analyze_temporal_spectrum(agent_counts: list) -> dict:
    """
    Perform spectral analysis to identify dominant periods.

    Args:
        agent_counts: Time series of agent counts

    Returns:
        dict with spectral analysis results
    """
    if len(agent_counts) < 10:
        return {
            'dominant_period': None,
            'spectral_power': None,
            'frequencies': [],
            'power_spectrum': []
        }

    # Detrend and normalize
    signal_data = np.array(agent_counts)
    detrended = signal.detrend(signal_data)

    # FFT
    n = len(detrended)
    fft_vals = np.fft.fft(detrended)
    power = np.abs(fft_vals[:n//2])**2
    freqs = np.fft.fftfreq(n, d=1.0)[:n//2]

    # Find dominant frequency (excluding DC component)
    if len(power) > 1:
        dominant_idx = np.argmax(power[1:]) + 1
        dominant_freq = freqs[dominant_idx]
        dominant_period = 1.0 / dominant_freq if dominant_freq > 0 else None
        dominant_power = power[dominant_idx]
    else:
        dominant_period = None
        dominant_power = None

    return {
        'dominant_period': dominant_period,
        'spectral_power': dominant_power,
        'frequencies': freqs.tolist()[:10],  # First 10 frequencies
        'power_spectrum': power.tolist()[:10]
    }


def run_temporal_energy_test(threshold: float, cycles: int = 500) -> dict:
    """
    Extended temporal observation at given threshold.

    Args:
        threshold: Burst threshold (energy level)
        cycles: Number of cycles for temporal analysis

    Returns:
        dict with temporal-energy metrics
    """
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (Temporal Analysis)")
    print(f"{'='*80}")

    # Create swarm
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Tracking
    agent_counts = []
    cluster_counts = []
    checkpoint_interval = 5  # High temporal resolution

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Spawn
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            agent_count = len(swarm.agents)
            cluster_count = len(swarm.composition.clusters)

            agent_counts.append(agent_count)
            cluster_counts.append(cluster_count)

    duration = time.time() - start_time

    # Temporal statistics
    mean_agents = np.mean(agent_counts) if agent_counts else 0
    std_agents = np.std(agent_counts) if agent_counts else 0
    cv_agents = std_agents / mean_agents if mean_agents > 0 else 0

    # Autocorrelation (lag=1)
    if len(agent_counts) > 1:
        agents_array = np.array(agent_counts)
        autocorr_lag1 = np.corrcoef(agents_array[:-1], agents_array[1:])[0,1]
    else:
        autocorr_lag1 = 0

    # Spectral analysis
    spectral = analyze_temporal_spectrum(agent_counts)

    # Cluster statistics
    mean_clusters = np.mean(cluster_counts) if cluster_counts else 0

    print(f"  Temporal Metrics:")
    print(f"    Mean agents: {mean_agents:.2f}")
    print(f"    Std agents: {std_agents:.2f}")
    print(f"    CV: {cv_agents:.3f}")
    print(f"    Autocorr (lag=1): {autocorr_lag1:.3f}")
    if spectral['dominant_period']:
        print(f"    Dominant period: {spectral['dominant_period']:.1f} checkpoints ({spectral['dominant_period']*checkpoint_interval:.1f} cycles)")
    else:
        print(f"    Dominant period: None detected")
    print(f"  Energy Metrics:")
    print(f"    Threshold: {threshold}")
    print(f"    Mean clusters: {mean_clusters:.1f}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'checkpoints': len(agent_counts),
        'mean_agents': mean_agents,
        'std_agents': std_agents,
        'cv_agents': cv_agents,
        'autocorr_lag1': autocorr_lag1,
        'dominant_period': spectral['dominant_period'],
        'spectral_power': spectral['spectral_power'],
        'mean_clusters': mean_clusters,
        'agent_counts': agent_counts,
        'cluster_counts': cluster_counts,
        'duration': duration
    }


def analyze_temporal_energy_coupling(results: list) -> dict:
    """
    Analyze relationship between energy and temporal patterns.

    Args:
        results: List of threshold test results

    Returns:
        dict with coupling analysis
    """
    print(f"\n{'='*80}")
    print(f"TEMPORAL-ENERGY COUPLING ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    mean_agents = [r['mean_agents'] for r in results]
    cv_agents = [r['cv_agents'] for r in results]
    autocorr = [r['autocorr_lag1'] for r in results]
    periods = [r['dominant_period'] if r['dominant_period'] else 0 for r in results]

    print("Temporal Patterns Across Energy Regimes:")
    print(f"{'Threshold':>10} | {'Mean A':>8} | {'CV':>8} | {'Autocorr':>10} | {'Period':>10}")
    print("-" * 60)
    for i, threshold in enumerate(thresholds):
        period_str = f"{periods[i]:.1f}" if periods[i] > 0 else "None"
        print(f"{threshold:>10.0f} | {mean_agents[i]:>8.2f} | {cv_agents[i]:>8.3f} | "
              f"{autocorr[i]:>10.3f} | {period_str:>10}")
    print()

    # Check for correlations
    # 1. Period vs Energy
    valid_periods = [(thresholds[i], periods[i]) for i in range(len(periods)) if periods[i] > 0]
    if len(valid_periods) >= 3:
        period_thresholds, period_values = zip(*valid_periods)
        period_correlation = np.corrcoef(period_thresholds, period_values)[0,1]
        print(f"Period-Energy Correlation: {period_correlation:.3f}")

        if abs(period_correlation) > 0.7:
            direction = "increases" if period_correlation > 0 else "decreases"
            print(f"  → Dominant period {direction} with energy (strong coupling)")
        elif abs(period_correlation) > 0.3:
            direction = "tends to increase" if period_correlation > 0 else "tends to decrease"
            print(f"  → Dominant period {direction} with energy (moderate coupling)")
        else:
            print(f"  → No clear period-energy relationship")
    else:
        period_correlation = None
        print("Period-Energy Correlation: Insufficient data")
    print()

    # 2. Variability vs Energy
    cv_correlation = np.corrcoef(thresholds, cv_agents)[0,1]
    print(f"Variability-Energy Correlation: {cv_correlation:.3f}")
    if abs(cv_correlation) > 0.7:
        direction = "increases" if cv_correlation > 0 else "decreases"
        print(f"  → Temporal variability {direction} with energy (strong coupling)")
    elif abs(cv_correlation) > 0.3:
        direction = "tends to increase" if cv_correlation > 0 else "tends to decrease"
        print(f"  → Temporal variability {direction} with energy (moderate coupling)")
    else:
        print(f"  → Variability remains constant across energy regimes")
    print()

    # 3. Memory vs Energy (autocorrelation)
    memory_correlation = np.corrcoef(thresholds, autocorr)[0,1]
    print(f"Memory-Energy Correlation: {memory_correlation:.3f}")
    if abs(memory_correlation) > 0.7:
        direction = "increases" if memory_correlation > 0 else "decreases"
        print(f"  → Temporal memory {direction} with energy (strong coupling)")
    elif abs(memory_correlation) > 0.3:
        direction = "tends to increase" if memory_correlation > 0 else "tends to decrease"
        print(f"  → Temporal memory {direction} with energy (moderate coupling)")
    else:
        print(f"  → Memory persistence constant across energy regimes")
    print()

    # Identify regime-specific phenomena
    coupling_detected = (
        (period_correlation is not None and abs(period_correlation) > 0.3) or
        abs(cv_correlation) > 0.3 or
        abs(memory_correlation) > 0.3
    )

    return {
        'period_energy_correlation': float(period_correlation) if period_correlation is not None else None,
        'variability_energy_correlation': float(cv_correlation),
        'memory_energy_correlation': float(memory_correlation),
        'coupling_detected': bool(coupling_detected)
    }


def main():
    """Run temporal-energy coupling exploration."""
    print("="*80)
    print("CYCLE 67: TEMPORAL-ENERGY COUPLING EXPLORATION")
    print("="*80)
    print()
    print("Exploring how temporal patterns (oscillations, variability, memory)")
    print("change across energy regimes in the thermodynamic phase diagram.")
    print()

    # Sample energy regimes across phase diagram
    test_thresholds = [270, 400, 500, 700, 1000]

    print(f"Testing {len(test_thresholds)} energy regimes: {test_thresholds}")
    print("Extended observation (500 cycles) with high temporal resolution")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_temporal_energy_test(threshold, cycles=500)
            results.append(result)
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"\n⚠️ Error testing threshold {threshold}: {e}")
            results.append({
                'threshold': threshold,
                'error': str(e)
            })

    overall_duration = time.time() - overall_start

    # Filter successful results
    successful_results = [r for r in results if 'error' not in r]

    if len(successful_results) >= 4:
        # Analyze temporal-energy coupling
        coupling_analysis = analyze_temporal_energy_coupling(successful_results)

        print("="*80)
        if coupling_analysis['coupling_detected']:
            print("🎉 INSIGHT #31: TEMPORAL-ENERGY COUPLING DETECTED")
            print("="*80)
            print()
            print("Temporal dynamics are energy-dependent:")
            if coupling_analysis['period_energy_correlation'] and abs(coupling_analysis['period_energy_correlation']) > 0.3:
                direction = "increases" if coupling_analysis['period_energy_correlation'] > 0 else "decreases"
                print(f"  - Oscillation period {direction} with energy")
            if abs(coupling_analysis['variability_energy_correlation']) > 0.3:
                direction = "increases" if coupling_analysis['variability_energy_correlation'] > 0 else "decreases"
                print(f"  - Temporal variability {direction} with energy")
            if abs(coupling_analysis['memory_energy_correlation']) > 0.3:
                direction = "increases" if coupling_analysis['memory_energy_correlation'] > 0 else "decreases"
                print(f"  - Temporal memory {direction} with energy")
            print()
            print("Theoretical Significance:")
            print("  - Unites temporal dynamics and thermodynamic frameworks")
            print("  - Energy modulates temporal behavior (time-energy coupling)")
            print("  - Validates NRM prediction of multi-scale dynamics")
            print()
            insight_31 = True
        else:
            print("TEMPORAL-ENERGY INDEPENDENCE")
            print("="*80)
            print()
            print("Temporal patterns remain constant across energy regimes:")
            print("  - Oscillation characteristics independent of threshold")
            print("  - Universal temporal dynamics regardless of energy")
            print("  - Temporal and thermodynamic layers decoupled")
            print()
            insight_31 = False
        print("="*80)
    else:
        print("⚠️ Insufficient successful tests for coupling analysis")
        coupling_analysis = {}
        insight_31 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "temporal_energy"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle67_temporal_energy_coupling.json"

    output_data = {
        'experiment': 'cycle67_temporal_energy_coupling',
        'test_thresholds': test_thresholds,
        'results': results,
        'coupling_analysis': coupling_analysis,
        'insight_31_discovered': insight_31,
        'overall_duration': overall_duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Total experiment duration: {overall_duration:.1f}s ({overall_duration/60:.2f} min)")
    print()

    return output_data


if __name__ == "__main__":
    main()
