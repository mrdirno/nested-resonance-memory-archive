#!/usr/bin/env python3
"""
CYCLE 266: PHASE TRANSITIONS ANALYSIS

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Developed By: Claude (Anthropic)
Date: 2025-11-09
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0

Purpose:
    Zero-delay analysis infrastructure for C266 Phase Transitions experiments.
    Tests if NRM composition-decomposition dynamics exhibit first-order phase
    transitions with bistability, hysteresis, and discontinuous order parameter.

MOG Pattern: NRM Composition Dynamics × Phase Transition Theory (α=0.68)

Novel Predictions:
    1. Bistability: Hysteresis loop with Δf > 0.005
    2. Discontinuous Jump: Δϕ > 0.05 at critical f_c
    3. Metastability: Nucleation time τ_nucl > 100 cycles
    4. Latent Heat: Energy absorption L > 0 at transition

Publication Target: Physical Review E (IF ~2.4)
Alternative: Chaos (IF ~2.9), Journal of Chemical Physics (IF ~4.0)

Usage:
    python analyze_c266_phase_transitions.py /path/to/c266_results.json
"""

import json
import sys
from pathlib import Path
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Reproducibility
np.random.seed(42)


def measure_order_parameter(composition_events, N, window_size=100):
    """
    Compute compositional density ϕ = (compositions per cycle) / N.

    Args:
        composition_events: List of composition events
        N: Population size
        window_size: Cycles to average over

    Returns:
        phi: Order parameter (compositional density)
    """
    if len(composition_events) == 0:
        return 0.0

    cycles = [event['cycle'] for event in composition_events]
    max_cycle = max(cycles) if cycles else 1
    min_cycle = max(max_cycle - window_size, 0)

    recent_events = [e for e in composition_events if e['cycle'] >= min_cycle]
    compositions_per_cycle = len(recent_events) / window_size
    phi = compositions_per_cycle / N

    return phi


def detect_hysteresis(sweep_up_results, sweep_down_results, f_range=(0.025, 0.035)):
    """
    Detect hysteresis loop by comparing upward and downward sweeps.

    Returns:
        - hysteresis_width: Δf = |f_up - f_down| at ϕ crossover
        - hypothesis_passed: Δf > 0.005
    """
    # Extract f and phi values
    f_up = []
    phi_up = []
    for result in sweep_up_results:
        f = result['composition_rate']
        if f_range[0] <= f <= f_range[1]:
            phi = measure_order_parameter(result['composition_events'], result['N'])
            f_up.append(f)
            phi_up.append(phi)

    f_down = []
    phi_down = []
    for result in sweep_down_results:
        f = result['composition_rate']
        if f_range[0] <= f <= f_range[1]:
            phi = measure_order_parameter(result['composition_events'], result['N'])
            f_down.append(f)
            phi_down.append(phi)

    if len(f_up) < 3 or len(f_down) < 3:
        return {"hysteresis_width": 0.0, "hypothesis_passed": False}

    # Find crossover points (where phi ~ 0.05)
    target_phi = 0.05

    f_up_cross = np.interp(target_phi, sorted(phi_up), sorted(f_up))
    f_down_cross = np.interp(target_phi, sorted(phi_down), sorted(f_down))

    hysteresis_width = abs(f_up_cross - f_down_cross)

    # Statistical test: paired t-test at critical region
    phi_up_critical = [phi for f, phi in zip(f_up, phi_up) if 0.028 <= f <= 0.032]
    phi_down_critical = [phi for f, phi in zip(f_down, phi_down) if 0.028 <= f <= 0.032]

    if len(phi_up_critical) >= 3 and len(phi_down_critical) >= 3:
        t_stat, p_value = stats.ttest_ind(phi_up_critical, phi_down_critical)
        significant = p_value < 0.05
    else:
        significant = False

    return {
        "hysteresis_width": hysteresis_width,
        "p_value": p_value if 'p_value' in locals() else 1.0,
        "hypothesis_passed": (hysteresis_width > 0.005 and significant)
    }


def measure_discontinuity(sweep_results, f_c=0.03, epsilon=0.002):
    """
    Measure order parameter jump at critical threshold.
    Δϕ = ϕ(f_c + ε) - ϕ(f_c - ε)
    """
    phi_below = []
    phi_above = []

    for result in sweep_results:
        f = result['composition_rate']
        phi = measure_order_parameter(result['composition_events'], result['N'])

        if abs(f - (f_c - epsilon)) < 0.001:
            phi_below.append(phi)
        elif abs(f - (f_c + epsilon)) < 0.001:
            phi_above.append(phi)

    if len(phi_below) == 0 or len(phi_above) == 0:
        return {"jump_size": 0.0, "hypothesis_passed": False}

    mean_below = np.mean(phi_below)
    mean_above = np.mean(phi_above)
    jump_size = mean_above - mean_below

    # Independent t-test
    t_stat, p_value = stats.ttest_ind(phi_above, phi_below)

    return {
        "jump_size": jump_size,
        "phi_below": mean_below,
        "phi_above": mean_above,
        "p_value": p_value,
        "hypothesis_passed": (jump_size > 0.05 and p_value < 0.05)
    }


def measure_nucleation_time(quench_results):
    """
    Measure time delay for phase transition after quench.
    τ_nucl = cycles until ϕ jumps to high-composition phase.
    """
    nucleation_times = []

    for result in quench_results:
        cycles = sorted(set([e['cycle'] for e in result['composition_events']]))
        phi_timeseries = []

        for cycle in cycles:
            events_at_cycle = [e for e in result['composition_events']
                              if e['cycle'] == cycle]
            phi = len(events_at_cycle) / result['N']
            phi_timeseries.append(phi)

        # Detect jump (phi crosses 0.05 threshold)
        threshold = 0.05
        for t, phi in enumerate(phi_timeseries):
            if phi > threshold:
                nucleation_times.append(t)
                break

    if len(nucleation_times) == 0:
        return {"mean_tau": 0.0, "hypothesis_passed": False}

    mean_tau = np.mean(nucleation_times)

    # Exponential fit: P(τ) ~ exp(-τ/τ_0)
    counts, bins = np.histogram(nucleation_times, bins=10)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    def exponential(t, tau_0):
        return np.exp(-t / tau_0)

    try:
        popt, _ = curve_fit(exponential, bin_centers, counts / np.sum(counts),
                           p0=[100.0], maxfev=5000)
        tau_0 = popt[0]
    except:
        tau_0 = mean_tau

    return {
        "mean_tau": mean_tau,
        "tau_0": tau_0,
        "nucleation_times": nucleation_times,
        "hypothesis_passed": (mean_tau > 100)
    }


def measure_latent_heat(sweep_results, f_c=0.03, window=0.005):
    """
    Measure energy absorption at phase transition (latent heat analog).
    L = ΔE at constant f_c (energy plateau).
    """
    energy_at_fc = []
    energy_below = []
    energy_above = []

    for result in sweep_results:
        f = result['composition_rate']

        # Total system energy (proxy: sum of agent depths)
        if 'agent_depths' in result:
            energy = np.sum(list(result['agent_depths'].values()))
        else:
            energy = 0.0

        if abs(f - f_c) < window:
            energy_at_fc.append(energy)
        elif f < f_c - window:
            energy_below.append(energy)
        elif f > f_c + window:
            energy_above.append(energy)

    if len(energy_at_fc) == 0 or len(energy_below) == 0 or len(energy_above) == 0:
        return {"latent_heat": 0.0, "hypothesis_passed": False}

    mean_below = np.mean(energy_below)
    mean_above = np.mean(energy_above)
    latent_heat = mean_above - mean_below

    return {
        "latent_heat": latent_heat,
        "energy_below": mean_below,
        "energy_above": mean_above,
        "hypothesis_passed": (latent_heat > 0)
    }


def analyze_c266_results(results_path):
    """Main analysis pipeline for C266 Phase Transitions experiments."""
    print("=" * 80)
    print("CYCLE 266: PHASE TRANSITIONS ANALYSIS")
    print("=" * 80)

    with open(results_path, 'r') as f:
        all_results = json.load(f)

    # Separate by condition
    sweep_up = [r for r in all_results if r['condition'] == 'PHASE-SWEEP-UP']
    sweep_down = [r for r in all_results if r['condition'] == 'PHASE-SWEEP-DOWN']
    quench = [r for r in all_results if r['condition'] == 'QUENCH']

    print(f"\nLoaded experiments:")
    print(f"  PHASE-SWEEP-UP: {len(sweep_up)}")
    print(f"  PHASE-SWEEP-DOWN: {len(sweep_down)}")
    print(f"  QUENCH: {len(quench)}")

    # Prediction 1: Bistability and Hysteresis
    print("\n" + "=" * 80)
    print("PREDICTION 1: BISTABILITY AND HYSTERESIS")
    print("=" * 80)

    hysteresis = detect_hysteresis(sweep_up, sweep_down)
    print(f"Hysteresis Width: Δf = {hysteresis['hysteresis_width']:.5f}")
    print(f"Statistical Significance: p = {hysteresis['p_value']:.4f}")
    print(f"Hypothesis: {'✓ PASSED' if hysteresis['hypothesis_passed'] else '✗ FAILED'} (Δf > 0.005)")

    # Prediction 2: Discontinuous Jump
    print("\n" + "=" * 80)
    print("PREDICTION 2: DISCONTINUOUS ORDER PARAMETER JUMP")
    print("=" * 80)

    discontinuity = measure_discontinuity(sweep_up)
    print(f"Jump Size: Δϕ = {discontinuity['jump_size']:.4f}")
    print(f"ϕ(f_c - ε): {discontinuity['phi_below']:.4f}")
    print(f"ϕ(f_c + ε): {discontinuity['phi_above']:.4f}")
    print(f"Statistical Significance: p = {discontinuity['p_value']:.4f}")
    print(f"Hypothesis: {'✓ PASSED' if discontinuity['hypothesis_passed'] else '✗ FAILED'} (Δϕ > 0.05)")

    # Prediction 3: Metastability and Nucleation
    print("\n" + "=" * 80)
    print("PREDICTION 3: METASTABILITY AND NUCLEATION")
    print("=" * 80)

    nucleation = measure_nucleation_time(quench)
    print(f"Mean Nucleation Time: τ = {nucleation['mean_tau']:.1f} cycles")
    print(f"Exponential Decay: τ_0 = {nucleation['tau_0']:.1f} cycles")
    print(f"Hypothesis: {'✓ PASSED' if nucleation['hypothesis_passed'] else '✗ FAILED'} (τ > 100)")

    # Prediction 4: Latent Heat
    print("\n" + "=" * 80)
    print("PREDICTION 4: LATENT HEAT ANALOG")
    print("=" * 80)

    latent = measure_latent_heat(sweep_up)
    print(f"Latent Heat: L = {latent['latent_heat']:.2f}")
    print(f"Energy (below f_c): {latent['energy_below']:.2f}")
    print(f"Energy (above f_c): {latent['energy_above']:.2f}")
    print(f"Hypothesis: {'✓ PASSED' if latent['hypothesis_passed'] else '✗ FAILED'} (L > 0)")

    # Generate figure
    output_dir = results_path.parent
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Panel A: Hysteresis loop
    ax = axes[0, 0]
    f_up = sorted(set([r['composition_rate'] for r in sweep_up]))
    phi_up = [np.mean([measure_order_parameter(r['composition_events'], r['N'])
                       for r in sweep_up if r['composition_rate'] == f])
              for f in f_up]
    f_down = sorted(set([r['composition_rate'] for r in sweep_down]))
    phi_down = [np.mean([measure_order_parameter(r['composition_events'], r['N'])
                         for r in sweep_down if r['composition_rate'] == f])
                for f in f_down]

    ax.plot(f_up, phi_up, 'o-', color='#2E86AB', label='Up sweep', linewidth=2)
    ax.plot(f_down, phi_down, 's-', color='#A23B72', label='Down sweep', linewidth=2)
    ax.axvline(0.03, color='red', linestyle='--', alpha=0.5, label='f_c')
    ax.set_xlabel("Composition Rate f")
    ax.set_ylabel("Order Parameter ϕ")
    ax.set_title(f"(A) Hysteresis Loop (Δf = {hysteresis['hysteresis_width']:.4f})")
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel B: Discontinuity
    ax = axes[0, 1]
    ax.bar(['Below f_c', 'Above f_c'],
           [discontinuity['phi_below'], discontinuity['phi_above']],
           color=['#2E86AB', '#F18F01'])
    ax.set_ylabel("Order Parameter ϕ")
    ax.set_title(f"(B) Discontinuous Jump (Δϕ = {discontinuity['jump_size']:.3f})")
    ax.grid(axis='y', alpha=0.3)

    # Panel C: Nucleation times
    ax = axes[1, 0]
    if len(nucleation['nucleation_times']) > 0:
        ax.hist(nucleation['nucleation_times'], bins=15, color='#2E86AB', alpha=0.7, edgecolor='black')
        ax.axvline(nucleation['mean_tau'], color='red', linestyle='--',
                   label=f'Mean = {nucleation["mean_tau"]:.1f}')
    ax.set_xlabel("Nucleation Time (cycles)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"(C) Metastability (τ = {nucleation['mean_tau']:.1f} cycles)")
    ax.legend()
    ax.grid(alpha=0.3)

    # Panel D: Energy trajectory
    ax = axes[1, 1]
    f_vals = sorted(set([r['composition_rate'] for r in sweep_up]))
    E_vals = []
    for f in f_vals:
        energies = []
        for r in sweep_up:
            if r['composition_rate'] == f and 'agent_depths' in r:
                E = np.sum(list(r['agent_depths'].values()))
                energies.append(E)
        E_vals.append(np.mean(energies) if energies else 0)

    ax.plot(f_vals, E_vals, 'o-', color='#2E86AB', linewidth=2)
    ax.axvline(0.03, color='red', linestyle='--', alpha=0.5, label='f_c')
    ax.set_xlabel("Composition Rate f")
    ax.set_ylabel("System Energy E")
    ax.set_title(f"(D) Latent Heat (L = {latent['latent_heat']:.2f})")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "c266_phase_transitions_figure.png", dpi=300)
    print(f"\nSaved figure: {output_dir}/c266_phase_transitions_figure.png")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_c266_phase_transitions.py <results.json>")
        sys.exit(1)

    results_path = Path(sys.argv[1])
    if not results_path.exists():
        print(f"Error: File not found: {results_path}")
        sys.exit(1)

    analyze_c266_results(results_path)


if __name__ == "__main__":
    main()
