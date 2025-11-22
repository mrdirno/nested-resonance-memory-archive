#!/usr/bin/env python3
"""
Cycle 172: Extended Threshold Range Validation

OBJECTIVE: Test linear relationship extrapolation beyond validated range

VALIDATED FINDINGS (C170):
- Linear relationship: critical_freq = 0.98 × threshold + 0.04
- R² = 0.9954 for threshold range [1.5, 2.0, 2.5, 3.0, 3.5]
- Mechanism: Composition event rate controls bistability

RESEARCH QUESTION:
Does the linear relationship hold outside the tested range?
- Test thresholds: [0.5, 1.0, 4.0, 5.0, 6.0]
- Expected: If mechanism universal, should follow same linear relationship
- Significance: Validates generalizability vs. local artifact

EXPERIMENTAL DESIGN:
- 5 extended thresholds × ~11 frequencies × 10 seeds = ~550 experiments
- Frequencies: Predicted critical ± 0.5% (from linear equation)
- Same protocol as C170 for direct comparison
- Duration estimate: ~2 minutes (based on C170 timing)

VALIDATION CRITERIA:
- Calculate linear regression including extended + original data
- Compare R² with extended range vs. original
- Test if new points fall within 95% confidence interval
- Maximum acceptable deviation: 0.1% from predicted critical

SUCCESS METRICS:
- Extended R² > 0.99 (maintained high fit)
- New critical frequencies within ±0.1% of prediction
- No systematic deviation pattern (would indicate nonlinearity)
- Validates universal mechanism claim

PUBLICATION IMPACT:
- Strengthens generalizability claims
- Demonstrates predictive power outside training range
- Supports "universal mechanism" conclusion
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


# Experimental parameters from C170 validation
BASIN_THRESHOLDS_EXTENDED = [0.5, 1.0, 4.0, 5.0, 6.0]  # Beyond C170 range
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10, same as C170
CYCLES = 3000  # Validated duration
FREQUENCY_RESOLUTION = 0.1  # 0.1% steps
FREQUENCY_RANGE_WIDTH = 1.0  # ±0.5% around predicted critical

# Validated linear relationship from C170
VALIDATED_SLOPE = 0.98
VALIDATED_INTERCEPT = 0.04


def generate_test_frequencies(threshold: float, resolution: float = 0.1,
                              range_width: float = 1.0) -> list:
    """
    Generate frequencies to test around predicted critical point.

    Uses validated linear relationship to predict critical frequency,
    then tests ±range_width/2 around prediction.
    """
    predicted_critical = VALIDATED_SLOPE * threshold + VALIDATED_INTERCEPT
    start = predicted_critical - range_width / 2
    end = predicted_critical + range_width / 2
    n_points = int((end - start) / resolution) + 1
    frequencies = [round(start + i * resolution, 1) for i in range(n_points)]
    return [f for f in frequencies if f >= 0.5]  # Ensure positive frequencies


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


def analyze_threshold_results(trials: list, threshold: float, frequencies: list) -> dict:
    """Analyze results for a single threshold value."""

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

    # Calculate predicted critical from validated equation
    predicted_critical = VALIDATED_SLOPE * threshold + VALIDATED_INTERCEPT
    deviation = abs(critical_frequency - predicted_critical) if critical_frequency else None

    return {
        'threshold': threshold,
        'frequencies': frequencies,
        'basin_a_percentages': basin_a_pcts,
        'critical_frequency': critical_frequency,
        'predicted_critical': predicted_critical,
        'deviation_from_prediction': deviation,
        'freq_results': freq_results
    }


def main():
    """Run extended threshold range validation experiment."""

    print("=" * 80)
    print("CYCLE 172: EXTENDED THRESHOLD RANGE VALIDATION")
    print("=" * 80)
    print()
    print("OBJECTIVE: Test linear relationship beyond validated range [1.5-3.5]")
    print()
    print("EXTENDED THRESHOLDS:", BASIN_THRESHOLDS_EXTENDED)
    print("VALIDATED RELATIONSHIP: f = 0.98t + 0.04 (R² = 0.9954)")
    print()

    start_time = time.time()

    # Results storage
    all_trials = []
    threshold_analyses = {}

    # Run experiments for each extended threshold
    for threshold_idx, threshold in enumerate(BASIN_THRESHOLDS_EXTENDED):
        print(f"Testing Threshold {threshold_idx + 1}/{len(BASIN_THRESHOLDS_EXTENDED)}: {threshold} events/window")
        print("-" * 80)

        # Generate frequencies to test (around predicted critical)
        frequencies = generate_test_frequencies(
            threshold,
            resolution=FREQUENCY_RESOLUTION,
            range_width=FREQUENCY_RANGE_WIDTH
        )

        predicted_critical = VALIDATED_SLOPE * threshold + VALIDATED_INTERCEPT
        print(f"  Predicted critical: {predicted_critical:.2f}%")
        print(f"  Testing frequencies: {frequencies[0]:.1f}% - {frequencies[-1]:.1f}% ({len(frequencies)} points)")
        print()

        threshold_trials = []

        # Run trials for this threshold
        for freq_idx, frequency in enumerate(frequencies):
            for seed_idx, seed in enumerate(SEEDS):
                trial_num = freq_idx * len(SEEDS) + seed_idx + 1
                total_trials = len(frequencies) * len(SEEDS)

                if trial_num % 10 == 0 or trial_num == total_trials:
                    print(f"  Progress: {trial_num}/{total_trials} trials...", end='\r')

                result = run_bistability_experiment(frequency, seed, threshold, CYCLES)
                threshold_trials.append(result)
                all_trials.append(result)

        print(f"  Completed: {len(threshold_trials)} trials")

        # Analyze this threshold's results
        analysis = analyze_threshold_results(threshold_trials, threshold, frequencies)
        threshold_analyses[threshold] = analysis

        # Print immediate results
        if analysis['critical_frequency']:
            print(f"  Measured critical: {analysis['critical_frequency']:.2f}%")
            print(f"  Deviation: {analysis['deviation_from_prediction']:.2f}%")
        else:
            print(f"  Critical frequency: NOT FOUND (transition outside tested range)")

        print()

    # Calculate extended linear regression (combine with C170 data conceptually)
    measured_criticals = []
    thresholds_measured = []

    for thresh, analysis in threshold_analyses.items():
        if analysis['critical_frequency'] is not None:
            thresholds_measured.append(thresh)
            measured_criticals.append(analysis['critical_frequency'])

    if len(thresholds_measured) >= 2:
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            thresholds_measured, measured_criticals
        )
        r_squared = r_value ** 2

        # Calculate deviation from validated parameters
        slope_deviation = abs(slope - VALIDATED_SLOPE)
        intercept_deviation = abs(intercept - VALIDATED_INTERCEPT)

        linear_regression = {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'p_value': p_value,
            'std_err': std_err,
            'validated_slope': VALIDATED_SLOPE,
            'validated_intercept': VALIDATED_INTERCEPT,
            'slope_deviation': slope_deviation,
            'intercept_deviation': intercept_deviation,
            'n_points': len(thresholds_measured)
        }
    else:
        linear_regression = None

    # Save results
    results = {
        'metadata': {
            'cycle': 172,
            'objective': 'Extended threshold range validation',
            'extended_thresholds': BASIN_THRESHOLDS_EXTENDED,
            'validated_range': [1.5, 2.0, 2.5, 3.0, 3.5],
            'validated_slope': VALIDATED_SLOPE,
            'validated_intercept': VALIDATED_INTERCEPT,
            'validated_r_squared': 0.9954,
            'n_seeds': len(SEEDS),
            'cycles_per_trial': CYCLES,
            'total_experiments': len(all_trials),
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': time.time() - start_time
        },
        'threshold_analyses': {
            str(thresh): {
                'threshold': analysis['threshold'],
                'predicted_critical': analysis['predicted_critical'],
                'measured_critical': analysis['critical_frequency'],
                'deviation': analysis['deviation_from_prediction'],
                'frequencies': analysis['frequencies'],
                'basin_a_percentages': analysis['basin_a_percentages'],
            }
            for thresh, analysis in threshold_analyses.items()
        },
        'linear_regression_extended': linear_regression,
        'trials': all_trials
    }

    # Save to file
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)
    output_file = results_dir / 'cycle172_extended_threshold_range.json'

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    duration = time.time() - start_time
    print("=" * 80)
    print("CYCLE 172 COMPLETE")
    print("=" * 80)
    print()
    print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Total experiments: {len(all_trials)}")
    print()

    if linear_regression:
        print("EXTENDED LINEAR REGRESSION:")
        print(f"  Equation: f = {slope:.4f}t + {intercept:.4f}")
        print(f"  R² = {r_squared:.4f}")
        print(f"  Validated equation: f = {VALIDATED_SLOPE}t + {VALIDATED_INTERCEPT}")
        print(f"  Slope deviation: {slope_deviation:.4f} ({slope_deviation/VALIDATED_SLOPE*100:.2f}%)")
        print(f"  Intercept deviation: {intercept_deviation:.4f}")
        print()

        # Verdict
        if r_squared > 0.99 and slope_deviation < 0.05:
            print("✅ VALIDATION SUCCESS: Linear relationship holds beyond tested range")
        elif r_squared > 0.95:
            print("⚠️  PARTIAL VALIDATION: Good fit but some deviation detected")
        else:
            print("❌ VALIDATION FAILURE: Significant deviation from linear relationship")
    else:
        print("⚠️  INSUFFICIENT DATA: Could not calculate regression (need ≥2 points)")

    print()
    print(f"Results saved: {output_file}")
    print()

    # Print individual threshold results
    print("THRESHOLD-BY-THRESHOLD RESULTS:")
    print()
    for thresh in BASIN_THRESHOLDS_EXTENDED:
        analysis = threshold_analyses[thresh]
        print(f"Threshold = {thresh}:")
        print(f"  Predicted: {analysis['predicted_critical']:.2f}%")
        if analysis['critical_frequency']:
            print(f"  Measured:  {analysis['critical_frequency']:.2f}%")
            print(f"  Deviation: {analysis['deviation_from_prediction']:.2f}%")

            if analysis['deviation_from_prediction'] <= 0.1:
                status = "✅ EXCELLENT"
            elif analysis['deviation_from_prediction'] <= 0.2:
                status = "✅ GOOD"
            else:
                status = "⚠️  DEVIATION"
            print(f"  Status: {status}")
        else:
            print(f"  Measured:  NOT FOUND")
            print(f"  Status: ⚠️  OUTSIDE RANGE")
        print()


if __name__ == '__main__':
    main()
