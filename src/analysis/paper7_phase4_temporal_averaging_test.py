#!/usr/bin/env python3
"""
PAPER 7 PHASE 4: TEMPORAL AVERAGING HYPOTHESIS TEST

Purpose: Test if V4 CV discrepancy explained by measurement timescale difference

Hypothesis:
- Paper 2 measures population in 100-cycle windows (time-averaged)
- V4 reports instantaneous variance (single time points)
- Time-averaging V4 should reduce CV toward empirical values

Test:
1. Simulate V4 deterministic model
2. Calculate CV two ways:
   a) Instantaneous: CV of all time points (V4 current method)
   b) Time-averaged: CV of 100-cycle window means (Paper 2 method)
3. Compare to empirical CV = 9.2%

Date: 2025-10-27 (Cycle 384)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import sys

sys.path.append(str(Path(__file__).parent))

from paper7_v4_energy_threshold import NRMDynamicalSystemV4


def simulate_v4_long_term(
    model: NRMDynamicalSystemV4,
    initial_state: np.ndarray,
    t_total: float = 5000.0,
    dt: float = 0.1,
    R_value: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate V4 for long time to get steady-state statistics.

    Args:
        model: V4 model instance
        initial_state: Initial [E, N, phi, theta_rel]
        t_total: Total simulation time
        dt: Time step
        R_value: Resource level

    Returns:
        (t_span, trajectory) arrays
    """
    print(f"  Simulating V4 for {t_total} time units...")

    t_span = np.arange(0, t_total + dt, dt)
    R_func = lambda t: R_value

    trajectory = model.simulate(t_span, initial_state, R_func)

    print(f"  Final state: N = {trajectory[-1, 1]:.2f}, E = {trajectory[-1, 0]:.2f}")

    return t_span, trajectory


def calculate_instantaneous_cv(
    trajectory: np.ndarray,
    transient_fraction: float = 0.5
) -> Dict:
    """
    Calculate CV from instantaneous population values.

    This is V4's current method: treat each time point as independent sample.

    Args:
        trajectory: Full trajectory array
        transient_fraction: Fraction of trajectory to discard as transient

    Returns:
        Statistics dictionary
    """
    # Discard transient
    start_idx = int(len(trajectory) * transient_fraction)
    N_steady = trajectory[start_idx:, 1]

    mean_N = np.mean(N_steady)
    std_N = np.std(N_steady)
    cv_N = std_N / mean_N if mean_N > 0 else np.inf

    return {
        'method': 'instantaneous',
        'n_samples': len(N_steady),
        'mean_N': mean_N,
        'std_N': std_N,
        'cv_N': cv_N
    }


def calculate_windowed_cv(
    trajectory: np.ndarray,
    t_span: np.ndarray,
    window_size: float = 100.0,
    transient_fraction: float = 0.5
) -> Dict:
    """
    Calculate CV from time-averaged population in sliding windows.

    This simulates Paper 2's measurement method: average N over 100-cycle windows,
    then calculate CV of these window means.

    Args:
        trajectory: Full trajectory array
        t_span: Time points
        window_size: Window size in time units (Paper 2 uses 100 cycles)
        transient_fraction: Fraction to discard as transient

    Returns:
        Statistics dictionary
    """
    # Discard transient
    start_idx = int(len(trajectory) * transient_fraction)
    t_steady = t_span[start_idx:]
    N_steady = trajectory[start_idx:, 1]

    # Calculate dt
    dt = t_span[1] - t_span[0]

    # Window size in indices
    window_indices = int(window_size / dt)

    # Sliding window means (non-overlapping to get independent samples)
    window_means = []
    for i in range(0, len(N_steady) - window_indices, window_indices):
        window_mean = np.mean(N_steady[i:i+window_indices])
        window_means.append(window_mean)

    window_means = np.array(window_means)

    mean_N = np.mean(window_means)
    std_N = np.std(window_means)
    cv_N = std_N / mean_N if mean_N > 0 else np.inf

    return {
        'method': f'windowed ({window_size} time units)',
        'n_samples': len(window_means),
        'window_size': window_size,
        'mean_N': mean_N,
        'std_N': std_N,
        'cv_N': cv_N
    }


def test_temporal_averaging_hypothesis(
    base_params: Dict,
    initial_state: np.ndarray,
    empirical_cv: float = 0.092
) -> Dict:
    """
    Test if temporal averaging explains CV discrepancy.

    Args:
        base_params: V4 parameters
        initial_state: Initial state
        empirical_cv: Target CV from Paper 2

    Returns:
        Results dictionary
    """
    print("\n" + "=" * 70)
    print("TEMPORAL AVERAGING HYPOTHESIS TEST")
    print("=" * 70)
    print()
    print(f"Empirical target CV: {empirical_cv:.3f} ({empirical_cv*100:.1f}%)")
    print()

    # Create model
    model = NRMDynamicalSystemV4(base_params)

    # Simulate
    t_span, trajectory = simulate_v4_long_term(model, initial_state, t_total=5000.0)

    # Method 1: Instantaneous CV (V4 current)
    print("\n### METHOD 1: INSTANTANEOUS CV (V4 Current) ###")
    instant_stats = calculate_instantaneous_cv(trajectory)
    print(f"  N samples: {instant_stats['n_samples']}")
    print(f"  Mean N: {instant_stats['mean_N']:.2f}")
    print(f"  Std N: {instant_stats['std_N']:.2f}")
    print(f"  CV: {instant_stats['cv_N']:.3f} ({instant_stats['cv_N']*100:.1f}%)")

    # Method 2: Windowed CV (Paper 2 method)
    window_sizes = [10, 50, 100, 200, 500]
    windowed_stats = []

    print("\n### METHOD 2: WINDOWED CV (Paper 2 Method) ###")
    for window_size in window_sizes:
        stats = calculate_windowed_cv(trajectory, t_span, window_size=window_size)
        windowed_stats.append(stats)

        print(f"\n  Window size: {window_size} time units")
        print(f"    N windows: {stats['n_samples']}")
        print(f"    Mean N: {stats['mean_N']:.2f}")
        print(f"    Std N: {stats['std_N']:.2f}")
        print(f"    CV: {stats['cv_N']:.3f} ({stats['cv_N']*100:.1f}%)")

        # Check if matches empirical
        cv_error = abs(stats['cv_N'] - empirical_cv)
        if cv_error < 0.01:
            print(f"    ✅ MATCHES empirical CV! (error = {cv_error:.4f})")
        else:
            print(f"    Error from empirical: {cv_error:.4f}")

    # Summary
    results = {
        'instantaneous': instant_stats,
        'windowed': windowed_stats,
        'empirical_cv': empirical_cv,
        'trajectory': trajectory,
        't_span': t_span
    }

    return results


def plot_temporal_averaging_results(results: Dict, output_dir: Path):
    """
    Visualize temporal averaging test results.

    Args:
        results: Test results
        output_dir: Output directory
    """
    print("\nGenerating temporal averaging figure...")

    instant = results['instantaneous']
    windowed = results['windowed']
    empirical_cv = results['empirical_cv']

    # Extract window sizes and CVs
    window_sizes = [w['window_size'] for w in windowed]
    cvs = [w['cv_N'] for w in windowed]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel 1: CV vs Window Size
    ax = axes[0]
    ax.plot([0] + window_sizes, [instant['cv_N']] + cvs, 'o-',
            markersize=8, linewidth=2, label='V4 CV (windowed)')
    ax.axhline(empirical_cv, color='red', linestyle='--', linewidth=2,
               label=f'Paper 2 Empirical = {empirical_cv:.3f}')
    ax.axhline(instant['cv_N'], color='gray', linestyle=':', alpha=0.5,
               label=f'V4 Instantaneous = {instant["cv_N"]:.3f}')

    ax.set_xlabel('Window Size (time units)', fontsize=11)
    ax.set_ylabel('Coefficient of Variation', fontsize=11)
    ax.set_title('CV vs. Temporal Averaging Window', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_xscale('log')

    # Panel 2: Population trajectory example
    ax = axes[1]
    t_span = results['t_span']
    trajectory = results['trajectory']

    # Show segment of trajectory
    start_idx = len(t_span) // 2
    end_idx = start_idx + 2000  # 200 time units at dt=0.1
    t_segment = t_span[start_idx:end_idx]
    N_segment = trajectory[start_idx:end_idx, 1]

    ax.plot(t_segment, N_segment, 'k-', alpha=0.7, linewidth=0.5, label='Instantaneous N')

    # Overlay 100-unit window means
    window_size = 100.0
    dt = t_span[1] - t_span[0]
    window_indices = int(window_size / dt)

    window_starts = range(0, len(N_segment) - window_indices, window_indices)
    for i in window_starts:
        window_mean = np.mean(N_segment[i:i+window_indices])
        ax.plot([t_segment[i], t_segment[i+window_indices]], [window_mean, window_mean],
                'r-', linewidth=2, alpha=0.7)

    ax.plot([], [], 'r-', linewidth=2, label='100-unit window mean')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Population (N)', fontsize=11)
    ax.set_title('Instantaneous vs. Time-Averaged Population', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    fig.suptitle('Temporal Averaging Hypothesis Test: V4 vs. Paper 2 Measurement Methods',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / f"paper7_phase4_temporal_averaging_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def main():
    """Main execution: Test temporal averaging hypothesis."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 4: TEMPORAL AVERAGING HYPOTHESIS TEST")
    print("=" * 70)
    print()

    print("Hypothesis:")
    print("  Paper 2 empirical CV calculated from time-averaged measurements")
    print("  V4 CV calculated from instantaneous values")
    print("  → Time-averaging V4 should reduce CV toward empirical")
    print()

    # V4 base parameters
    base_params = {
        'r': 0.15,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 2.5,
        'mu_0': 0.4,
        'sigma': 0.1,
        'omega': 0.02,
        'kappa': 0.1,
        'phi_0': 0.06,
        'rho_threshold': 5.0
    }

    initial_state = np.array([100.0, 10.0, 0.5, 0.0])
    empirical_cv = 0.092  # Paper 2 within-experiment CV

    # Run test
    results = test_temporal_averaging_hypothesis(base_params, initial_state, empirical_cv)

    # Visualize
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_temporal_averaging_results(results, output_dir)

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()

    instant_cv = results['instantaneous']['cv_N']
    windowed_100 = [w for w in results['windowed'] if w['window_size'] == 100][0]
    windowed_cv = windowed_100['cv_N']

    print(f"V4 Instantaneous CV: {instant_cv:.3f} ({instant_cv*100:.1f}%)")
    print(f"V4 Windowed CV (100 units): {windowed_cv:.3f} ({windowed_cv*100:.1f}%)")
    print(f"Paper 2 Empirical CV: {empirical_cv:.3f} ({empirical_cv*100:.1f}%)")
    print()

    cv_reduction = (instant_cv - windowed_cv) / instant_cv * 100
    print(f"CV reduction from windowing: {cv_reduction:.1f}%")
    print()

    # Test hypothesis
    if abs(windowed_cv - empirical_cv) < 0.01:
        print("✅ HYPOTHESIS VALIDATED")
        print("   Temporal averaging explains CV discrepancy!")
        print("   V4 and Paper 2 consistent when using same measurement method.")
    elif windowed_cv < instant_cv and abs(windowed_cv - empirical_cv) < 0.03:
        print("⚠️ HYPOTHESIS PARTIALLY SUPPORTED")
        print("   Temporal averaging reduces CV toward empirical")
        print("   But gap remains - other factors also contribute")
    else:
        print("❌ HYPOTHESIS REJECTED")
        print("   Temporal averaging does not explain discrepancy")
        print("   Gap likely due to structural model differences")

    print()


if __name__ == "__main__":
    main()
