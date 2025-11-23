#!/usr/bin/env python3
"""
PAPER 7 PHASE 3: BIFURCATION VISUALIZATION TOOLS

Purpose: Generate publication-quality figures for bifurcation analysis results

Figures Generated:
- Figure 1: 1D bifurcation diagram (N* vs parameter)
- Figure 2: 2D stability map (parameter vs parameter heatmap)
- Figure 3: Eigenvalue trajectories (Re(λ) vs parameter)
- Figure 4: Comparison to empirical data (validation)

Date: 2025-10-27
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict, List, Optional


class BifurcationVisualizer:
    """Generate publication-quality bifurcation diagrams."""

    def __init__(self, results_file: Path):
        """
        Initialize visualizer with results data.

        Args:
            results_file: Path to JSON results from bifurcation analysis
        """
        with open(results_file, 'r') as f:
            self.results = json.load(f)

        self.param_name = self.results['metadata']['param_name']
        self.equilibria = self.results['equilibria']
        self.bifurcations = self.results['bifurcations']

    def plot_1d_bifurcation_diagram(
        self,
        output_file: Optional[Path] = None,
        show_stability: bool = True,
        show_bifurcations: bool = True,
        empirical_boundaries: Optional[List[float]] = None
    ) -> plt.Figure:
        """
        Generate 1D bifurcation diagram (N* vs parameter).

        Args:
            output_file: Path to save figure (PNG, 300 DPI)
            show_stability: Color-code by stability
            show_bifurcations: Annotate bifurcation points
            empirical_boundaries: Empirical regime boundaries to overlay

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        param_values = []
        N_stable = []
        N_unstable = []

        for eq in self.equilibria:
            if eq['success'] and eq['N'] is not None:
                param_values.append(eq['param_value'])

                if eq['stability'] == 'stable':
                    N_stable.append(eq['N'])
                    N_unstable.append(None)
                else:
                    N_stable.append(None)
                    N_unstable.append(eq['N'])

        # Plot stable branch (solid line)
        stable_params = [p for p, N in zip(param_values, N_stable) if N is not None]
        stable_N = [N for N in N_stable if N is not None]
        if stable_params:
            ax.plot(stable_params, stable_N, 'b-', linewidth=2, label='Stable equilibrium')

        # Plot unstable branch (dashed line)
        unstable_params = [p for p, N in zip(param_values, N_unstable) if N is not None]
        unstable_N = [N for N in N_unstable if N is not None]
        if unstable_params:
            ax.plot(unstable_params, unstable_N, 'r--', linewidth=2, label='Unstable equilibrium')

        # Mark bifurcation points
        if show_bifurcations:
            for bif in self.bifurcations:
                ax.axvline(
                    bif['param_value'],
                    color='gray',
                    linestyle=':',
                    alpha=0.5,
                    label=f"Bifurcation: {bif['type']}" if bif == self.bifurcations[0] else ""
                )

        # Overlay empirical boundaries
        if empirical_boundaries:
            for boundary in empirical_boundaries:
                ax.axvline(
                    boundary,
                    color='green',
                    linestyle='--',
                    linewidth=2,
                    alpha=0.7,
                    label=f"Empirical boundary: {boundary}"
                )

        # Labels and formatting
        ax.set_xlabel(f'Parameter: {self.param_name}', fontsize=12)
        ax.set_ylabel('Population (N*)', fontsize=12)
        ax.set_title(f'Bifurcation Diagram: Population vs {self.param_name}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc='best')

        plt.tight_layout()

        # Save figure
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Figure saved: {output_file}")

        return fig

    def plot_eigenvalue_trajectories(
        self,
        output_file: Optional[Path] = None
    ) -> plt.Figure:
        """
        Plot eigenvalue real parts vs parameter.

        Args:
            output_file: Path to save figure

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract eigenvalue data
        param_values = []
        eigenvalue_reals = [[] for _ in range(4)]  # 4 eigenvalues (4D system)

        for eq in self.equilibria:
            if eq['success'] and eq['eigenvalues'] is not None:
                param_values.append(eq['param_value'])

                for i, ev_data in enumerate(eq['eigenvalues']):
                    eigenvalue_reals[i].append(ev_data['real'])

        # Plot each eigenvalue trajectory
        colors = ['blue', 'red', 'green', 'purple']
        for i, (reals, color) in enumerate(zip(eigenvalue_reals, colors)):
            if reals:
                ax.plot(param_values, reals, color=color, linewidth=1.5, alpha=0.7, label=f'λ_{i+1}')

        # Mark stability boundary (Re(λ) = 0)
        ax.axhline(0, color='black', linestyle='--', linewidth=2, label='Re(λ) = 0')

        # Labels
        ax.set_xlabel(f'Parameter: {self.param_name}', fontsize=12)
        ax.set_ylabel('Real Part of Eigenvalues', fontsize=12)
        ax.set_title('Eigenvalue Trajectories', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc='best')

        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Figure saved: {output_file}")

        return fig

    def plot_empirical_comparison(
        self,
        empirical_data: Dict,
        output_file: Optional[Path] = None
    ) -> plt.Figure:
        """
        Compare predicted bifurcations to empirical regime boundaries.

        Args:
            empirical_data: Dict with 'boundaries' and 'labels'
            output_file: Path to save figure

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract predicted bifurcation points
        predicted_bifurcations = [bif['param_value'] for bif in self.bifurcations]

        # Plot empirical boundaries
        if 'boundaries' in empirical_data:
            for boundary, label in zip(empirical_data['boundaries'], empirical_data['labels']):
                ax.axvline(
                    boundary,
                    color='green',
                    linestyle='--',
                    linewidth=2,
                    alpha=0.7,
                    label=f"Empirical: {label}"
                )

        # Plot predicted bifurcations
        for bif_value in predicted_bifurcations:
            ax.axvline(
                bif_value,
                color='blue',
                linestyle='-',
                linewidth=2,
                alpha=0.7,
                label=f"Predicted: {bif_value:.4f}"
            )

        # Compute errors
        if 'boundaries' in empirical_data and predicted_bifurcations:
            # Match closest predicted to empirical
            errors = []
            for emp_boundary in empirical_data['boundaries']:
                closest_pred = min(predicted_bifurcations, key=lambda x: abs(x - emp_boundary))
                error = abs(closest_pred - emp_boundary)
                errors.append(error)
                ax.plot(
                    [emp_boundary, closest_pred],
                    [0.5, 0.5],
                    'ro-',
                    linewidth=1,
                    markersize=8
                )

            mean_error = np.mean(errors)
            ax.text(
                0.02, 0.98,
                f"Mean prediction error: {mean_error:.4f}",
                transform=ax.transAxes,
                fontsize=12,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            )

        ax.set_xlabel(f'Parameter: {self.param_name}', fontsize=12)
        ax.set_ylabel('', fontsize=12)
        ax.set_title('Predicted vs Empirical Bifurcations', fontsize=14, fontweight='bold')
        ax.set_ylim([0, 1])
        ax.set_yticks([])
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Figure saved: {output_file}")

        return fig


def generate_all_figures(
    results_file: Path,
    output_dir: Optional[Path] = None,
    empirical_data: Optional[Dict] = None
):
    """
    Generate all Phase 3 publication figures.

    Args:
        results_file: Path to bifurcation analysis results JSON
        output_dir: Directory to save figures
        empirical_data: Empirical regime boundaries for validation
    """
    print("\n" + "=" * 70)
    print("GENERATING PHASE 3 PUBLICATION FIGURES")
    print("=" * 70)

    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    visualizer = BifurcationVisualizer(results_file)
    param_name = visualizer.param_name

    # Figure 1: Bifurcation diagram
    print("Generating Figure 1: Bifurcation diagram...")
    visualizer.plot_1d_bifurcation_diagram(
        output_file=output_dir / f"paper7_phase3_bifurcation_{param_name}.png",
        show_stability=True,
        show_bifurcations=True,
        empirical_boundaries=empirical_data.get('boundaries') if empirical_data else None
    )

    # Figure 3: Eigenvalue trajectories
    print("Generating Figure 3: Eigenvalue trajectories...")
    visualizer.plot_eigenvalue_trajectories(
        output_file=output_dir / f"paper7_phase3_eigenvalues_{param_name}.png"
    )

    # Figure 4: Empirical comparison (if data provided)
    if empirical_data:
        print("Generating Figure 4: Empirical comparison...")
        visualizer.plot_empirical_comparison(
            empirical_data=empirical_data,
            output_file=output_dir / f"paper7_phase3_empirical_comparison_{param_name}.png"
        )

    print("\n" + "=" * 70)
    print("ALL FIGURES GENERATED")
    print(f"Output directory: {output_dir}")
    print("=" * 70)


def main():
    """Execute visualization for Phase 3 results."""

    # Example: Visualize omega parameter bifurcation analysis
    results_file = Path(__file__).parent.parent.parent / "data" / "results" / "paper7_phase3_bifurcation_omega.json"

    if not results_file.exists():
        print(f"Results file not found: {results_file}")
        print("Run paper7_phase3_bifurcation_analysis.py first.")
        return

    # Empirical data from Paper 2
    empirical_data = {
        'boundaries': [0.005, 0.025],  # 0.5%, 2.5% frequency boundaries
        'labels': ['Collapse → Bistability (0.5%)', 'Bistability → Sustained (2.5%)']
    }

    # Generate all figures
    generate_all_figures(
        results_file=results_file,
        empirical_data=empirical_data
    )


if __name__ == "__main__":
    main()
