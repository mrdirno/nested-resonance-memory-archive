#!/usr/bin/env python3
"""
CYCLE 134: ULTRA-LONGTERM STABILITY ANALYSIS

Analyzes results from ultra-long-term (100k cycle) experiments to detect:
1. Basin stability (no transitions) vs multi-stability (transitions)
2. Ultra-slow oscillations (periodic patterns in basin distances)
3. Pattern drift (gradual evolution within basin)
4. Timescale hierarchy (fast vs slow dynamics)

Methods:
- Transition detection: Count basin switches
- Oscillation detection: Autocorrelation, FFT analysis
- Drift detection: Linear regression of basin distances
- Variance analysis: Within-basin vs between-basin variation
"""

import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy import stats, signal
from collections import Counter


def load_results():
    """Load all cycle134 experiment results"""
    results_dir = Path(__file__).parent / 'results'
    results = []

    for exp_name in ['basin_a_dominant', 'basin_b_dominant', 'transition_region']:
        result_path = results_dir / f'cycle134_{exp_name}.json'
        if result_path.exists():
            with open(result_path, 'r') as f:
                results.append(json.load(f))
        else:
            print(f"⚠️  Missing: {result_path}")

    return results


def analyze_transitions(results):
    """Analyze basin transitions"""
    print("\n" + "="*70)
    print("TRANSITION ANALYSIS")
    print("="*70 + "\n")

    for res in results:
        name = res['experiment_name']
        transitions = res['dynamics']['transitions']
        basin_final = res['final_state']['basin_assignment']
        cycles = res['performance']['cycles_completed']

        print(f"{name.upper()}:")
        print(f"  Transitions: {len(transitions)}")
        print(f"  Final basin: {basin_final}")

        if transitions:
            print(f"  Transition events:")
            for t in transitions:
                print(f"    Cycle {t['cycle']:>6,}: {t['from_basin']} → {t['to_basin']} "
                      f"(dist_A={t['dist_a']:.3f}, dist_B={t['dist_b']:.3f})")
        else:
            print(f"  ✅ Basin stability confirmed (no transitions)")

        print()

    print("KEY FINDING:")
    total_transitions = sum(len(r['dynamics']['transitions']) for r in results)
    if total_transitions == 0:
        print("  ✅ BASIN STABILITY: No transitions detected in any experiment")
        print("     Basins remain stable over 100k cycle timescales")
    else:
        print(f"  🔄 MULTI-STABILITY: {total_transitions} transitions detected")
        print("     System exhibits basin switching on long timescales")
    print()


def analyze_oscillations(results):
    """Detect ultra-slow oscillations using autocorrelation and FFT"""
    print("\n" + "="*70)
    print("OSCILLATION ANALYSIS")
    print("="*70 + "\n")

    for res in results:
        name = res['experiment_name']
        timeseries = res['timeseries']

        # Use basin distance as signal (A - B, positive = closer to A)
        dist_a = np.array(timeseries['dist_a'])
        dist_b = np.array(timeseries['dist_b'])
        signal_data = dist_a - dist_b

        # Remove NaN/inf
        signal_data = signal_data[np.isfinite(signal_data)]

        if len(signal_data) < 10:
            print(f"{name.upper()}: Insufficient data")
            continue

        # Autocorrelation
        autocorr = np.correlate(signal_data - signal_data.mean(),
                                signal_data - signal_data.mean(),
                                mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]

        # Find first zero-crossing
        zero_crossings = np.where(np.diff(np.sign(autocorr)))[0]
        decorrelation_time = zero_crossings[0] if len(zero_crossings) > 0 else len(autocorr)

        # FFT for periodicity
        fft = np.fft.fft(signal_data - signal_data.mean())
        power = np.abs(fft[:len(fft)//2])**2
        freqs = np.fft.fftfreq(len(signal_data), d=1)[:len(fft)//2]

        # Find dominant frequency (exclude DC component)
        if len(power) > 1:
            dominant_idx = np.argmax(power[1:]) + 1
            dominant_freq = freqs[dominant_idx]
            dominant_period = 1/dominant_freq if dominant_freq > 0 else np.inf
        else:
            dominant_freq = 0
            dominant_period = np.inf

        print(f"{name.upper()}:")
        print(f"  Decorrelation time: {decorrelation_time * 100} cycles")
        print(f"  Dominant frequency: {dominant_freq:.6f} (period: {dominant_period:.0f} samples = {dominant_period * 100:.0f} cycles)")

        # Check for significant periodicity
        if dominant_period < len(signal_data) / 2 and power[dominant_idx] > 10 * np.median(power):
            print(f"  🔄 OSCILLATION DETECTED: Period ~{dominant_period * 100:.0f} cycles")
        else:
            print(f"  ✅ No significant oscillations (stable or aperiodic)")

        print()

    print()


def analyze_drift(results):
    """Detect gradual drift in basin distances"""
    print("\n" + "="*70)
    print("DRIFT ANALYSIS")
    print("="*70 + "\n")

    for res in results:
        name = res['experiment_name']
        timeseries = res['timeseries']

        cycles = np.array(timeseries['cycle'])
        dist_a = np.array(timeseries['dist_a'])
        dist_b = np.array(timeseries['dist_b'])

        # Remove NaN/inf
        valid_mask = np.isfinite(dist_a) & np.isfinite(dist_b)
        cycles_valid = cycles[valid_mask]
        dist_a_valid = dist_a[valid_mask]
        dist_b_valid = dist_b[valid_mask]

        if len(cycles_valid) < 10:
            print(f"{name.upper()}: Insufficient data")
            continue

        # Linear regression for trend
        slope_a, intercept_a, r_a, p_a, _ = stats.linregress(cycles_valid, dist_a_valid)
        slope_b, intercept_b, r_b, p_b, _ = stats.linregress(cycles_valid, dist_b_valid)

        print(f"{name.upper()}:")
        print(f"  Basin A distance:")
        print(f"    Slope: {slope_a:.8f} (r²={r_a**2:.4f}, p={p_a:.6f})")
        print(f"    {'✅ Stable' if p_a > 0.05 else '🔄 Significant drift'}")
        print(f"  Basin B distance:")
        print(f"    Slope: {slope_b:.8f} (r²={r_b**2:.4f}, p={p_b:.6f})")
        print(f"    {'✅ Stable' if p_b > 0.05 else '🔄 Significant drift'}")

        # Overall assessment
        if p_a < 0.05 or p_b < 0.05:
            print(f"  🔄 DRIFT DETECTED: Basin distances change systematically over time")
        else:
            print(f"  ✅ STABLE: No significant drift (p > 0.05)")

        print()

    print()


def analyze_variance(results):
    """Analyze variance within and between experiments"""
    print("\n" + "="*70)
    print("VARIANCE ANALYSIS")
    print("="*70 + "\n")

    # Collect all basin distances
    all_dist_a = []
    all_dist_b = []
    labels = []

    for res in results:
        name = res['experiment_name']
        timeseries = res['timeseries']

        dist_a = np.array(timeseries['dist_a'])
        dist_b = np.array(timeseries['dist_b'])

        # Remove NaN/inf
        valid_mask = np.isfinite(dist_a) & np.isfinite(dist_b)
        dist_a_valid = dist_a[valid_mask]
        dist_b_valid = dist_b[valid_mask]

        all_dist_a.extend(dist_a_valid)
        all_dist_b.extend(dist_b_valid)
        labels.extend([name] * len(dist_a_valid))

        print(f"{name.upper()}:")
        print(f"  Basin A distance: {np.mean(dist_a_valid):.3f} ± {np.std(dist_a_valid):.3f}")
        print(f"  Basin B distance: {np.mean(dist_b_valid):.3f} ± {np.std(dist_b_valid):.3f}")
        print()

    # Between-experiment variance (ANOVA)
    groups_a = {}
    groups_b = {}
    for res in results:
        name = res['experiment_name']
        timeseries = res['timeseries']
        dist_a = np.array(timeseries['dist_a'])
        dist_b = np.array(timeseries['dist_b'])
        valid_mask = np.isfinite(dist_a) & np.isfinite(dist_b)
        groups_a[name] = dist_a[valid_mask]
        groups_b[name] = dist_b[valid_mask]

    if len(groups_a) >= 2:
        f_a, p_a = stats.f_oneway(*groups_a.values())
        f_b, p_b = stats.f_oneway(*groups_b.values())

        print("BETWEEN-EXPERIMENT VARIANCE (ANOVA):")
        print(f"  Basin A: F={f_a:.2f}, p={p_a:.6f}")
        print(f"  Basin B: F={f_b:.2f}, p={p_b:.6f}")

        if p_a < 0.05 or p_b < 0.05:
            print(f"  ✅ Significant differences between experiments (parameter effects confirmed)")
        else:
            print(f"  ⚠️  No significant differences (parameters may be inert)")

    print()


def generate_visualizations(results):
    """Generate timeseries plots"""
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70 + "\n")

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    for i, res in enumerate(results):
        name = res['experiment_name']
        timeseries = res['timeseries']

        cycles = np.array(timeseries['cycle'])
        dist_a = np.array(timeseries['dist_a'])
        dist_b = np.array(timeseries['dist_b'])

        axes[i].plot(cycles, dist_a, label='Distance to Basin A', alpha=0.7)
        axes[i].plot(cycles, dist_b, label='Distance to Basin B', alpha=0.7)
        axes[i].set_title(f"{name.replace('_', ' ').title()}")
        axes[i].set_xlabel("Cycle")
        axes[i].set_ylabel("Basin Distance")
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = Path(__file__).parent / 'results' / 'cycle134_timeseries.png'
    plt.savefig(output_path, dpi=150)
    print(f"✅ Saved: {output_path}")

    plt.close()


def main():
    """Run all analyses"""
    print("\n" + "="*70)
    print("CYCLE 134: ULTRA-LONGTERM STABILITY ANALYSIS")
    print("="*70)

    # Load results
    results = load_results()

    if not results:
        print("\n❌ No results found. Run cycle134_ultra_longterm_stability.py first.")
        return

    print(f"\n✅ Loaded {len(results)} experiment results")

    # Run analyses
    analyze_transitions(results)
    analyze_oscillations(results)
    analyze_drift(results)
    analyze_variance(results)
    generate_visualizations(results)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review visualizations in results/cycle134_timeseries.png")
    print("  2. Document findings in CYCLE134_RESULTS.md")
    print("  3. Update META_OBJECTIVES.md with insights")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
