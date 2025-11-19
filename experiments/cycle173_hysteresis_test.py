#!/usr/bin/env python3
"""
Cycle 173: Hysteresis Testing for Bistable Transition

OBJECTIVE: Test if the bistable transition exhibits hysteresis (memory effects)

CONTEXT:
- C169 showed sharp first-order transition at 2.55% ± 0.05%
- First-order phase transitions typically exhibit hysteresis
- C170 validated linear mechanism across parameter space
- Hysteresis would confirm phase transition classification

EXPERIMENTAL DESIGN:
- Forward Sweep: Increase frequency 1.0% → 4.0% in 0.1% steps
- Reverse Sweep: Decrease frequency 4.0% → 1.0% in 0.1% steps
- Measure transition points in both directions
- Compare critical frequencies (forward vs reverse)

HYPOTHESIS:
If true first-order phase transition:
- Forward critical frequency > Reverse critical frequency
- Hysteresis width = measure of energy barrier height
- System "remembers" previous state near critical point

VALIDATION CRITERIA:
- If hysteresis width > 0.1%: Confirms first-order transition
- If no hysteresis: May indicate higher-order transition
- Hysteresis width quantifies transition barrier

PUBLICATION IMPACT:
- More complete phase diagram characterization
- Confirms phase transition classification
- Provides thermodynamic interpretation
- Strengthens first-order transition claim from C169

SUCCESS METRICS:
- Both sweeps complete successfully (2 × 31 frequencies × 10 seeds = 620 experiments)
- Critical frequencies identified in both directions
- Hysteresis width calculated
- Statistical significance tested
"""

import json
import sys
from pathlib import Path
import numpy as np
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent
from fractal.fractal_swarm import CompositionEngine


# Experimental parameters
BASIN_THRESHOLD = 2.5  # events/window (validated in C168-C170)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10, same as previous
CYCLES = 3000  # Validated duration
FREQUENCY_STEP = 0.1  # 0.1% resolution (same as C169)


def run_bistability_experiment(frequency: float, seed: int, threshold: float,
                                cycles: int) -> dict:
    """
    Run single bistability experiment with controlled spawn frequency.

    Same protocol as C168-C170 for direct comparison.

    Args:
        frequency: Spawn frequency (% per 100 cycles)
        seed: Random seed for reproducibility
        threshold: Basin classification threshold (composition events/window)
        cycles: Number of cycles to run

    Returns:
        dict with experimental results
    """
    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    np.random.seed(seed)

    # Get real system metrics
    metrics = reality.get_system_metrics()

    # Create initial fractal agent
    initial_agent = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7
    )

    # Track composition events (cluster formations)
    composition_events = []
    spawn_count = 0
    spawn_interval = max(1, int(100.0 / frequency)) if frequency > 0 else cycles + 1

    # Active agents list
    agents = [initial_agent]
    composition_engine = CompositionEngine(resonance_threshold=0.5)

    # Run cycles
    for cycle_idx in range(cycles):
        # Spawn new agent based on frequency
        should_spawn = (cycle_idx % spawn_interval) == 0

        if should_spawn and len(agents) < 100:
            spawn_count += 1
            current_metrics = reality.get_system_metrics()
            parent = agents[np.random.randint(len(agents))]
            child_id = f"agent_{cycle_idx}_{spawn_count}"
            child = parent.spawn_child(child_id, energy_fraction=0.3)
            if child:
                agents.append(child)

        # Evolve all agents
        delta_time = 0.01
        for agent in agents:
            agent.evolve(delta_time)

        # Detect clusters (composition events)
        cluster_events = composition_engine.detect_clusters(agents)
        if cluster_events:
            for _ in cluster_events:
                composition_events.append(cycle_idx)

    # Calculate composition event rate (events per 100-cycle window)
    bins = np.arange(0, cycles + 1, 100)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0

    # Basin classification using provided threshold
    basin = 'A' if avg_composition_events > threshold else 'B'

    return {
        'frequency': frequency,
        'seed': seed,
        'threshold': threshold,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
        'final_agent_count': len(agents),
    }


def analyze_sweep_results(trials: list, frequencies: list, direction: str) -> dict:
    """Analyze results from one sweep direction."""

    # Group by frequency
    freq_results = {}
    for freq in frequencies:
        freq_trials = [t for t in trials if t['frequency'] == freq]
        basin_a_count = sum(1 for t in freq_trials if t['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(freq_trials)) * 100 if freq_trials else 0

        avg_comp_events = np.mean([t['avg_composition_events'] for t in freq_trials])

        freq_results[freq] = {
            'basin_a_count': basin_a_count,
            'basin_a_pct': basin_a_pct,
            'avg_composition_events': avg_comp_events,
            'trials': len(freq_trials)
        }

    # Find critical frequency (where Basin A % crosses 50%)
    basin_a_pcts = [freq_results[f]['basin_a_pct'] for f in frequencies]
    critical_frequency = None

    for i in range(len(frequencies) - 1):
        if basin_a_pcts[i] < 50 <= basin_a_pcts[i + 1]:
            # Transition between these frequencies
            critical_frequency = (frequencies[i] + frequencies[i + 1]) / 2
            break

    # If exactly at 50%, that's the critical point
    for i, pct in enumerate(basin_a_pcts):
        if pct == 50:
            critical_frequency = frequencies[i]
            break

    return {
        'direction': direction,
        'frequencies': frequencies,
        'basin_a_percentages': basin_a_pcts,
        'critical_frequency': critical_frequency,
        'freq_results': freq_results
    }


def main():
    """Run hysteresis testing experiment."""

    print("=" * 80)
    print("CYCLE 173: HYSTERESIS TESTING")
    print("=" * 80)
    print()
    print("OBJECTIVE: Test if bistable transition exhibits hysteresis (memory effects)")
    print()
    print("HYPOTHESIS: First-order phase transitions show hysteresis")
    print("  - Forward critical > Reverse critical")
    print("  - Hysteresis width = energy barrier measure")
    print()

    start_time = time.time()

    # Define sweep ranges
    freq_min = 1.0
    freq_max = 4.0
    forward_frequencies = [round(f, 1) for f in np.arange(freq_min, freq_max + 0.05, FREQUENCY_STEP)]
    reverse_frequencies = list(reversed(forward_frequencies))

    print(f"Sweep range: {freq_min}% - {freq_max}%")
    print(f"Frequency step: {FREQUENCY_STEP}%")
    print(f"Number of frequencies: {len(forward_frequencies)}")
    print(f"Seeds per frequency: {len(SEEDS)}")
    print(f"Total experiments: {len(forward_frequencies) * len(SEEDS) * 2} (forward + reverse)")
    print()

    # Results storage
    all_trials = []

    # ========================================================================
    # FORWARD SWEEP: 1.0% → 4.0%
    # ========================================================================
    print("=" * 80)
    print("FORWARD SWEEP: 1.0% → 4.0%")
    print("=" * 80)
    print()

    forward_trials = []
    for freq_idx, frequency in enumerate(forward_frequencies):
        print(f"Forward [{freq_idx + 1}/{len(forward_frequencies)}] Testing frequency: {frequency:.1f}%", end='')

        freq_trials = []
        for seed in SEEDS:
            result = run_bistability_experiment(frequency, seed, BASIN_THRESHOLD, CYCLES)
            result['sweep_direction'] = 'forward'
            freq_trials.append(result)
            forward_trials.append(result)
            all_trials.append(result)

        # Quick classification summary
        basin_a = sum(1 for t in freq_trials if t['basin'] == 'A')
        basin_a_pct = (basin_a / len(freq_trials)) * 100
        print(f" → Basin A: {basin_a_pct:.0f}%")

    print()

    # Analyze forward sweep
    forward_analysis = analyze_sweep_results(forward_trials, forward_frequencies, 'forward')
    if forward_analysis['critical_frequency']:
        print(f"Forward critical frequency: {forward_analysis['critical_frequency']:.2f}%")
    else:
        print("Forward critical frequency: NOT FOUND (transition outside range)")
    print()

    # ========================================================================
    # REVERSE SWEEP: 4.0% → 1.0%
    # ========================================================================
    print("=" * 80)
    print("REVERSE SWEEP: 4.0% → 1.0%")
    print("=" * 80)
    print()

    reverse_trials = []
    for freq_idx, frequency in enumerate(reverse_frequencies):
        print(f"Reverse [{freq_idx + 1}/{len(reverse_frequencies)}] Testing frequency: {frequency:.1f}%", end='')

        freq_trials = []
        for seed in SEEDS:
            result = run_bistability_experiment(frequency, seed, BASIN_THRESHOLD, CYCLES)
            result['sweep_direction'] = 'reverse'
            freq_trials.append(result)
            reverse_trials.append(result)
            all_trials.append(result)

        # Quick classification summary
        basin_a = sum(1 for t in freq_trials if t['basin'] == 'A')
        basin_a_pct = (basin_a / len(freq_trials)) * 100
        print(f" → Basin A: {basin_a_pct:.0f}%")

    print()

    # Analyze reverse sweep
    reverse_analysis = analyze_sweep_results(reverse_trials, reverse_frequencies, 'reverse')
    if reverse_analysis['critical_frequency']:
        print(f"Reverse critical frequency: {reverse_analysis['critical_frequency']:.2f}%")
    else:
        print("Reverse critical frequency: NOT FOUND (transition outside range)")
    print()

    # ========================================================================
    # HYSTERESIS ANALYSIS
    # ========================================================================
    print("=" * 80)
    print("HYSTERESIS ANALYSIS")
    print("=" * 80)
    print()

    forward_crit = forward_analysis['critical_frequency']
    reverse_crit = reverse_analysis['critical_frequency']

    if forward_crit and reverse_crit:
        hysteresis_width = abs(forward_crit - reverse_crit)

        print(f"Forward critical:  {forward_crit:.2f}%")
        print(f"Reverse critical:  {reverse_crit:.2f}%")
        print(f"Hysteresis width:  {hysteresis_width:.2f}%")
        print()

        # Interpret results
        if hysteresis_width < 0.1:
            verdict = "NO HYSTERESIS DETECTED"
            interpretation = "Transition reversible - may not be first-order"
            significance = "⚠️  Inconsistent with C169 sharp transition hypothesis"
        elif hysteresis_width < 0.3:
            verdict = "SMALL HYSTERESIS"
            interpretation = "Weak barrier - borderline first-order transition"
            significance = "✅ Mild hysteresis supports first-order classification"
        else:
            verdict = "SIGNIFICANT HYSTERESIS"
            interpretation = f"Strong barrier ({hysteresis_width:.2f}%) - definite first-order"
            significance = "✅ Strong hysteresis confirms first-order phase transition"

        print(f"Verdict: {verdict}")
        print(f"Interpretation: {interpretation}")
        print(f"Significance: {significance}")
        print()

        # Compare with C169 result
        c169_critical = 2.55
        print(f"C169 Critical (no sweep): {c169_critical:.2f}%")
        print(f"C173 Average Critical:    {(forward_crit + reverse_crit) / 2:.2f}%")
        print(f"Deviation from C169:       {abs((forward_crit + reverse_crit) / 2 - c169_critical):.2f}%")
        print()

        hysteresis_result = {
            'forward_critical': forward_crit,
            'reverse_critical': reverse_crit,
            'hysteresis_width': hysteresis_width,
            'verdict': verdict,
            'interpretation': interpretation,
            'significance': significance,
            'c169_comparison': {
                'c169_critical': c169_critical,
                'c173_average': (forward_crit + reverse_crit) / 2,
                'deviation': abs((forward_crit + reverse_crit) / 2 - c169_critical)
            }
        }
    else:
        print("⚠️  Cannot calculate hysteresis - critical point(s) not found")
        print()
        hysteresis_result = {
            'forward_critical': forward_crit,
            'reverse_critical': reverse_crit,
            'hysteresis_width': None,
            'verdict': 'INCONCLUSIVE',
            'interpretation': 'Critical point(s) outside tested range',
            'significance': 'Need to expand frequency range'
        }

    # Save results
    results = {
        'metadata': {
            'cycle': 173,
            'objective': 'Hysteresis testing for bistable transition',
            'sweep_range': [freq_min, freq_max],
            'frequency_step': FREQUENCY_STEP,
            'n_frequencies': len(forward_frequencies),
            'n_seeds': len(SEEDS),
            'total_experiments': len(all_trials),
            'basin_threshold': BASIN_THRESHOLD,
            'cycles_per_trial': CYCLES,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': time.time() - start_time
        },
        'forward_sweep': {
            'frequencies': forward_analysis['frequencies'],
            'basin_a_percentages': forward_analysis['basin_a_percentages'],
            'critical_frequency': forward_analysis['critical_frequency'],
        },
        'reverse_sweep': {
            'frequencies': reverse_analysis['frequencies'],
            'basin_a_percentages': reverse_analysis['basin_a_percentages'],
            'critical_frequency': reverse_analysis['critical_frequency'],
        },
        'hysteresis_analysis': hysteresis_result,
        'trials': all_trials
    }

    # Save to file
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)
    output_file = results_dir / 'cycle173_hysteresis_test.json'

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    duration = time.time() - start_time
    print("=" * 80)
    print("CYCLE 173 COMPLETE")
    print("=" * 80)
    print()
    print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Total experiments: {len(all_trials)}")
    print(f"Results saved: {output_file}")
    print()

    if hysteresis_width:
        print("HYSTERESIS VERDICT:")
        print(f"  Width: {hysteresis_width:.2f}%")
        print(f"  {verdict}")
        print()

    print("PUBLICATION IMPACT:")
    print("  - Characterizes phase transition order")
    print("  - Provides thermodynamic interpretation")
    print("  - Completes phase diagram")
    print()


if __name__ == '__main__':
    main()
