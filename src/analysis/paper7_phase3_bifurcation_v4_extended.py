#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: EXTENDED BIFURCATION ANALYSIS ON V4 MODEL

Purpose: Multi-parameter bifurcation analysis to identify regime boundaries

Methods:
- Multiple parameter sweeps: omega, K, lambda_0, mu_0, r
- 2D parameter space exploration
- Compare to Paper 2 empirical boundaries
- Generate publication-quality figures

Date: 2025-10-27 (Cycle 381)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json
import sys

sys.path.append(str(Path(__file__).parent))

from paper7_phase3_bifurcation_v4 import (
    BifurcationAnalyzerV4,
    NRMDynamicalSystemV4
)


def analyze_bifurcation_results(results_path: Path) -> Dict:
    """
    Analyze bifurcation results from JSON file.

    Args:
        results_path: Path to results JSON

    Returns:
        Summary statistics
    """
    with open(results_path, 'r') as f:
        results = json.load(f)

    # Count equilibria found
    n_found = sum(results['found'])
    n_total = len(results['found'])
    success_rate = n_found / n_total * 100

    # Extract equilibrium values
    equilibria = [eq for eq in results['equilibria'] if eq is not None]

    if equilibria:
        equilibria = np.array(equilibria)
        E_values = equilibria[:, 0]
        N_values = equilibria[:, 1]
        phi_values = equilibria[:, 2]
        theta_values = equilibria[:, 3]

        summary = {
            'success_rate': success_rate,
            'n_found': n_found,
            'n_total': n_total,
            'E_mean': np.mean(E_values),
            'E_std': np.std(E_values),
            'N_mean': np.mean(N_values),
            'N_std': np.std(N_values),
            'phi_mean': np.mean(phi_values),
            'phi_std': np.std(phi_values),
            'theta_mean': np.mean(theta_values),
            'theta_std': np.std(theta_values),
        }
    else:
        summary = {
            'success_rate': 0.0,
            'n_found': 0,
            'n_total': n_total
        }

    return summary


def multi_parameter_sweep(
    base_params: Dict[str, float],
    initial_guess: np.ndarray,
    output_dir: Path
) -> List[Dict]:
    """
    Perform sweeps across multiple parameters.

    Args:
        base_params: Base parameter set
        initial_guess: Initial equilibrium guess
        output_dir: Directory for outputs

    Returns:
        List of results dictionaries
    """
    analyzer = BifurcationAnalyzerV4(base_params)

    sweep_configs = [
        {'name': 'omega', 'range': np.linspace(0.01, 0.05, 40)},
        {'name': 'K', 'range': np.linspace(50, 150, 40)},
        {'name': 'lambda_0', 'range': np.linspace(1.0, 4.0, 40)},
        {'name': 'mu_0', 'range': np.linspace(0.2, 0.6, 40)},
        {'name': 'r', 'range': np.linspace(0.05, 0.25, 40)},
    ]

    all_results = []

    for config in sweep_configs:
        print(f"Parameter sweep: {config['name']}")
        print(f"  Range: {config['range'][0]:.4f} to {config['range'][-1]:.4f}")

        results = analyzer.parameter_sweep_1d(
            param_name=config['name'],
            param_range=config['range'],
            initial_guess=initial_guess,
            R_value=1.0
        )

        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_path = output_dir / "results" / f"paper7_bifurcation_v4_{config['name']}_{timestamp}.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)

        results_json = {
            'param_name': results['param_name'],
            'param_values': results['param_values'],
            'equilibria': [eq.tolist() if eq is not None else None for eq in results['equilibria']],
            'stability': results['stability'],
            'found': results['found'],
            'bifurcations_detected': results['bifurcations_detected']
        }

        with open(results_path, 'w') as f:
            json.dump(results_json, f, indent=2)

        # Generate figure
        fig_path = output_dir / "figures" / f"paper7_bifurcation_v4_{config['name']}_{timestamp}.png"
        analyzer.generate_bifurcation_diagram(results, fig_path)

        # Summary
        n_found = sum(results['found'])
        n_bifurcations = len(results['bifurcations_detected'])
        print(f"  Found: {n_found}/{len(results['found'])} equilibria")
        print(f"  Bifurcations: {n_bifurcations}")
        print()

        all_results.append(results)

    return all_results


def create_composite_figure(
    all_results: List[Dict],
    output_dir: Path
) -> None:
    """
    Create composite figure showing all parameter sweeps.

    Args:
        all_results: List of results from all sweeps
        output_dir: Directory for output
    """
    n_sweeps = len(all_results)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, results in enumerate(all_results):
        ax = axes[i]

        param_values = np.array(results['param_values'])
        equilibria = results['equilibria']
        stability = results['stability']

        # Extract N values
        N_stable = []
        N_unstable = []
        param_stable = []
        param_unstable = []

        for j, eq in enumerate(equilibria):
            if eq is not None:
                param_val = param_values[j]
                N_val = eq[1]

                if stability[j] == 'stable':
                    N_stable.append(N_val)
                    param_stable.append(param_val)
                elif stability[j] == 'unstable':
                    N_unstable.append(N_val)
                    param_unstable.append(param_val)

        # Plot
        if N_stable:
            ax.plot(param_stable, N_stable, 'b-', linewidth=2, label='Stable')
        if N_unstable:
            ax.plot(param_unstable, N_unstable, 'r--', linewidth=2, label='Unstable')

        # Mark bifurcations
        for bif in results['bifurcations_detected']:
            ax.axvline(bif['param_value'], color='k', linestyle=':', alpha=0.5)

        ax.set_xlabel(f"{results['param_name']}", fontsize=10)
        ax.set_ylabel("Population (N)", fontsize=10)
        ax.set_title(f"{results['param_name']} sweep", fontsize=11)
        ax.grid(alpha=0.3)

        if i == 0:
            ax.legend(fontsize=9)

    # Remove extra subplot
    if n_sweeps < len(axes):
        fig.delaxes(axes[-1])

    fig.suptitle("V4 Model: Multi-Parameter Bifurcation Analysis", fontsize=14, fontweight='bold')
    plt.tight_layout()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / "figures" / f"paper7_bifurcation_v4_composite_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Composite figure saved: {save_path}")
    plt.close()


def main():
    """Execute extended bifurcation analysis."""
    print("\n" + "=" * 70)
    print("V4 MODEL: EXTENDED BIFURCATION ANALYSIS")
    print("=" * 70)
    print()

    # Base parameters
    params = {
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

    initial_guess = np.array([521.70, 50.00, 0.5092, 0.4715])

    output_dir = Path(__file__).parent.parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Performing multi-parameter sweeps...")
    print()

    all_results = multi_parameter_sweep(params, initial_guess, output_dir)

    print("Creating composite figure...")
    create_composite_figure(all_results, output_dir)

    print()
    print("=" * 70)
    print("EXTENDED BIFURCATION ANALYSIS COMPLETE")
    print("=" * 70)
    print()

    # Summary
    print("Summary:")
    for results in all_results:
        param_name = results['param_name']
        n_found = sum(results['found'])
        n_total = len(results['found'])
        n_bif = len(results['bifurcations_detected'])
        print(f"  {param_name}: {n_found}/{n_total} equilibria, {n_bif} bifurcations")

    print()


if __name__ == "__main__":
    main()
