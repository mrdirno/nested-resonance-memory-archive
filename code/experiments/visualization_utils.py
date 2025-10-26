"""
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""


#!/usr/bin/env python3
"""
Publication-Grade Visualization Utilities
For NRM Framework Research Papers

Paper 1 (C168-C170): Validated Bistable Dynamics
- Phase diagrams (frequency × threshold)
- Bifurcation plots (Basin A % vs frequency)
- Linear regression validation plots
- Complete bistable landscape visualization

Paper 2 (C171+): Population Homeostasis Discovery
- Population trajectory time series
- Composition event constancy
- Homeostasis validation plots
- Simplified vs. complete framework comparison
- Phase space transformation diagrams

All plots use matplotlib with publication standards:
- High DPI (300+)
- Clear labels and legends
- Proper font sizes for print
- Color schemes optimized for both screen and print
- Color-blind friendly palettes
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Publication-grade plotting settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16


class BistabilityVisualizer:
    """
    Publication-grade visualization for validated bistable dynamics.

    Creates plots suitable for peer-reviewed publication based on
    C168-C170 experimental validation.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory for saving plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def plot_bifurcation_diagram(
        self,
        frequencies: List[float],
        basin_a_percentages: List[float],
        critical_freq: Optional[float] = None,
        title: str = "Bistable Bifurcation Diagram"
    ) -> Path:
        """
        Create bifurcation diagram showing Basin A % vs frequency.

        Sharp 1st order transition visualization from C169 data.

        Args:
            frequencies: Tested frequency values
            basin_a_percentages: % of trials in Basin A at each frequency
            critical_freq: Estimated critical frequency for marking
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot bifurcation curve
        ax.plot(frequencies, basin_a_percentages, 'o-', linewidth=2,
                markersize=8, color='#2E86AB', label='Observed')

        # Mark critical frequency if provided
        if critical_freq:
            ax.axvline(critical_freq, color='#A23B72', linestyle='--',
                      linewidth=2, label=f'Critical Freq = {critical_freq:.2f}%')

        # Mark basin regions
        ax.axhspan(0, 50, alpha=0.1, color='#EE6C4D', label='Dead Zone (Basin B)')
        ax.axhspan(50, 100, alpha=0.1, color='#2E86AB', label='Resonance Zone (Basin A)')

        ax.set_xlabel('Spawn Frequency (%)')
        ax.set_ylabel('Basin A Percentage (%)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(-5, 105)

        # Save
        output_path = self.output_dir / 'bifurcation_diagram.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_linear_regression(
        self,
        thresholds: List[float],
        critical_frequencies: List[float],
        slope: float,
        intercept: float,
        r_squared: float,
        title: str = "Linear Relationship: Critical Frequency vs Basin Threshold"
    ) -> Path:
        """
        Plot linear regression from C170 multi-threshold validation.

        Shows definitive validation of composition-rate control mechanism.

        Args:
            thresholds: Basin threshold values tested
            critical_frequencies: Measured critical frequencies
            slope: Linear fit slope
            intercept: Linear fit intercept
            r_squared: Goodness of fit
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data points
        ax.scatter(thresholds, critical_frequencies, s=100, color='#2E86AB',
                  edgecolors='black', linewidths=1.5, zorder=3,
                  label='Measured Critical Frequencies')

        # Linear fit
        x_fit = np.linspace(min(thresholds) - 0.2, max(thresholds) + 0.2, 100)
        y_fit = slope * x_fit + intercept
        ax.plot(x_fit, y_fit, '--', linewidth=2, color='#A23B72',
               label=f'Linear Fit: y = {slope:.3f}x + {intercept:.3f}\nR² = {r_squared:.4f}')

        # Ideal 1:1 line for comparison
        ax.plot(x_fit, x_fit, ':', linewidth=1.5, color='gray',
               alpha=0.5, label='Ideal 1:1 Line')

        ax.set_xlabel('Basin Threshold (events/window)')
        ax.set_ylabel('Critical Frequency (%)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal')

        # Add R² annotation
        ax.text(0.05, 0.95, f'R² = {r_squared:.4f}\nSlope = {slope:.4f}',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Save
        output_path = self.output_dir / 'linear_regression.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_phase_diagram(
        self,
        frequency_range: Tuple[float, float],
        threshold_range: Tuple[float, float],
        slope: float,
        intercept: float,
        title: str = "Complete Bistable Phase Diagram"
    ) -> Path:
        """
        Create 2D phase diagram showing dead zone vs resonance zone.

        Complete characterization from C168-C170 validation.

        Args:
            frequency_range: (min, max) frequency values
            threshold_range: (min, max) threshold values
            slope: Critical line slope
            intercept: Critical line intercept
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create meshgrid
        freq = np.linspace(frequency_range[0], frequency_range[1], 200)
        thresh = np.linspace(threshold_range[0], threshold_range[1], 200)
        F, T = np.meshgrid(freq, thresh)

        # Calculate critical line: freq = slope * threshold + intercept
        critical_freq = slope * T + intercept

        # Basin classification
        # Basin A (resonance zone) where freq > critical
        basin = np.where(F > critical_freq, 1, 0)

        # Plot phase regions
        im = ax.contourf(F, T, basin, levels=[0, 0.5, 1],
                        colors=['#EE6C4D', '#2E86AB'], alpha=0.3)

        # Critical line
        critical_line_freq = slope * thresh + intercept
        ax.plot(critical_line_freq, thresh, 'k-', linewidth=3,
               label=f'Critical Line: f = {slope:.2f}t + {intercept:.2f}')

        # Add text labels for regions
        ax.text(1.0, 3.0, 'Dead Zone\n(Basin B)', fontsize=14,
               ha='center', va='center', bbox=dict(boxstyle='round',
               facecolor='#EE6C4D', alpha=0.5))
        ax.text(4.0, 1.5, 'Resonance Zone\n(Basin A)', fontsize=14,
               ha='center', va='center', bbox=dict(boxstyle='round',
               facecolor='#2E86AB', alpha=0.5))

        ax.set_xlabel('Spawn Frequency (%)')
        ax.set_ylabel('Basin Threshold (events/window)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')

        # Save
        output_path = self.output_dir / 'phase_diagram.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_composition_rate_validation(
        self,
        frequencies: List[float],
        avg_composition_events: List[float],
        title: str = "Composition Event Rate vs Spawn Frequency"
    ) -> Path:
        """
        Plot validation that composition events ≈ frequency.

        Shows mechanistic relationship from C168-C170.

        Args:
            frequencies: Spawn frequency values
            avg_composition_events: Average composition events per 100 cycles
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Data points
        ax.scatter(frequencies, avg_composition_events, s=100,
                  color='#2E86AB', edgecolors='black', linewidths=1.5,
                  zorder=3, label='Measured Composition Events')

        # Ideal 1:1 line
        x_line = np.array([min(frequencies), max(frequencies)])
        ax.plot(x_line, x_line, '--', linewidth=2, color='#A23B72',
               label='Expected: Events = Frequency')

        ax.set_xlabel('Spawn Frequency (%)')
        ax.set_ylabel('Avg Composition Events (per 100 cycles)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal')

        # Add annotation
        ax.text(0.05, 0.95, 'Mechanistic Validation:\nComposition Rate ≈ Spawn Rate',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Save
        output_path = self.output_dir / 'composition_rate_validation.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path


class HomeostasisVisualizer:
    """
    Publication-grade visualization for emergent population homeostasis.

    Creates plots suitable for peer-reviewed publication based on
    C171+ experimental validation of complete NRM framework dynamics.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory for saving plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def plot_population_homeostasis(
        self,
        frequencies: List[float],
        population_means: List[float],
        population_stds: List[float],
        title: str = "Population Homeostasis Across Frequencies"
    ) -> Path:
        """
        Plot population constancy despite frequency variation.

        Shows emergent homeostatic regulation from C171 data.

        Args:
            frequencies: Tested spawn frequency values
            population_means: Mean population at each frequency
            population_stds: Standard deviation of population
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot population with error bars
        ax.errorbar(frequencies, population_means, yerr=population_stds,
                   fmt='o-', linewidth=2, markersize=10, capsize=5,
                   color='#2E86AB', ecolor='#2E86AB', alpha=0.7,
                   label='Population ± 1 SD')

        # Mark homeostatic setpoint
        setpoint = np.mean(population_means)
        ax.axhline(setpoint, color='#A23B72', linestyle='--',
                  linewidth=2, label=f'Homeostatic Setpoint ≈ {setpoint:.1f}')

        # Highlight homeostatic range
        setpoint_std = np.std(population_means)
        ax.axhspan(setpoint - setpoint_std, setpoint + setpoint_std,
                  alpha=0.1, color='#2E86AB')

        ax.set_xlabel('Spawn Frequency (%)')
        ax.set_ylabel('Mean Population (agents)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Add annotation
        cv = (setpoint_std / setpoint) * 100
        ax.text(0.05, 0.95, f'Coefficient of Variation: {cv:.1f}%\n'
               f'Regulatory Efficiency: {100*(1-cv/52):.1f}%',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Save
        output_path = self.output_dir / 'population_homeostasis.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_composition_constancy(
        self,
        frequencies: List[float],
        composition_means: List[float],
        composition_stds: List[float],
        title: str = "Composition Event Constancy (Complete Framework)"
    ) -> Path:
        """
        Plot composition event constancy showing decoupling from spawn frequency.

        Args:
            frequencies: Spawn frequency values
            composition_means: Mean composition events per window
            composition_stds: Standard deviation
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot composition events with error bars
        ax.errorbar(frequencies, composition_means, yerr=composition_stds,
                   fmt='s-', linewidth=2, markersize=10, capsize=5,
                   color='#EE6C4D', ecolor='#EE6C4D', alpha=0.7,
                   label='Composition Events ± 1 SD')

        # Mark constant level
        constant_level = np.mean(composition_means)
        ax.axhline(constant_level, color='#A23B72', linestyle='--',
                  linewidth=2, label=f'Constant Level ≈ {constant_level:.1f}/window')

        # Compare with simplified model expectation (1:1 line)
        # Convert frequency % to events per 100 cycles
        expected = np.array(frequencies)  # frequency % = events/100 cycles
        ax.plot(frequencies, expected, ':', linewidth=2, color='gray',
               alpha=0.5, label='Simplified Model Prediction (1:1)')

        ax.set_xlabel('Spawn Frequency (%)')
        ax.set_ylabel('Composition Events (per 100-cycle window)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Add annotation
        cv = (np.std(composition_means) / constant_level) * 100
        freq_range = (max(frequencies) - min(frequencies)) / min(frequencies) * 100
        ax.text(0.05, 0.95, f'Composition CV: {cv:.2f}%\n'
               f'Frequency Range: {freq_range:.1f}%\n'
               f'Decoupling Ratio: {freq_range/cv:.1f}×',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Save
        output_path = self.output_dir / 'composition_constancy.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_framework_comparison(
        self,
        frequencies: List[float],
        simplified_comp: List[float],
        complete_comp: List[float],
        complete_comp_std: List[float],
        title: str = "Simplified vs. Complete Framework Comparison"
    ) -> Path:
        """
        Side-by-side comparison of simplified and complete framework dynamics.

        Args:
            frequencies: Spawn frequency values
            simplified_comp: Composition events from simplified model
            complete_comp: Composition events from complete framework
            complete_comp_std: Standard deviation for complete framework
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Simplified model (1:1 line)
        ax.plot(frequencies, simplified_comp, 'o-', linewidth=3,
               markersize=10, color='#A23B72', alpha=0.7,
               label='Simplified Model (r=0.998)')

        # Complete framework (flat line)
        ax.errorbar(frequencies, complete_comp, yerr=complete_comp_std,
                   fmt='s-', linewidth=3, markersize=10, capsize=5,
                   color='#2E86AB', ecolor='#2E86AB', alpha=0.7,
                   label='Complete Framework (r=0.071)')

        ax.set_xlabel('Spawn Frequency (%)')
        ax.set_ylabel('Composition Events (per 100-cycle window)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=12)

        # Add annotation box
        ax.text(0.05, 0.95,
               'Simplified Model:\n'
               '  • Fixed population (n=1)\n'
               '  • Direct spawn→composition coupling\n'
               '  • Bistable attractors\n\n'
               'Complete Framework:\n'
               '  • Dynamic population (n≈17)\n'
               '  • Birth-death coupling\n'
               '  • Homeostatic attractor',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
               fontsize=10)

        # Save
        output_path = self.output_dir / 'framework_comparison.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def plot_phase_space_transformation(
        self,
        title: str = "Phase Space Transformation: Simplified → Complete"
    ) -> Path:
        """
        Visualize phase space transformation from 1D bistable to 2D homeostatic.

        Creates schematic diagram showing qualitative phase space change.

        Args:
            title: Plot title

        Returns:
            Path to saved plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Left panel: Simplified model (1D bistable)
        comp_rate = np.linspace(0, 5, 100)

        # Potential function with two minima (bistable)
        potential = 0.1 * (comp_rate - 1.5)**2 * (comp_rate - 3.5)**2

        ax1.plot(comp_rate, potential, linewidth=3, color='#A23B72')
        ax1.axvline(1.5, color='#EE6C4D', linestyle='--', linewidth=2,
                   label='Basin B (Dead Zone)')
        ax1.axvline(3.5, color='#2E86AB', linestyle='--', linewidth=2,
                   label='Basin A (Resonance)')
        ax1.scatter([1.5, 3.5], [0, 0], s=200, color=['#EE6C4D', '#2E86AB'],
                   edgecolors='black', linewidths=2, zorder=5)

        ax1.set_xlabel('Composition Rate', fontsize=12)
        ax1.set_ylabel('Potential Energy (arbitrary)', fontsize=12)
        ax1.set_title('Simplified Model:\n1D Bistable Phase Space', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(bottom=-0.5)

        # Right panel: Complete framework (2D homeostatic)
        pop = np.linspace(10, 25, 50)
        comp = np.linspace(90, 110, 50)
        POP, COMP = np.meshgrid(pop, comp)

        # Potential function with single minimum at (17, 101)
        potential_2d = ((POP - 17)**2 + (COMP - 101)**2)

        contour = ax2.contourf(POP, COMP, potential_2d, levels=20,
                              cmap='viridis', alpha=0.6)
        ax2.scatter([17], [101], s=300, color='#A23B72',
                   edgecolors='black', linewidths=2, zorder=5,
                   marker='*', label='Homeostatic Attractor')

        ax2.set_xlabel('Population (agents)', fontsize=12)
        ax2.set_ylabel('Composition Rate (events/window)', fontsize=12)
        ax2.set_title('Complete Framework:\n2D Homeostatic Attractor', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.colorbar(contour, ax=ax2, label='Potential Energy')

        # Save
        output_path = self.output_dir / 'phase_space_transformation.png'
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path


def create_c169_bifurcation_plot():
    """Create bifurcation plot from C169 precision mapping data."""

    # Load C169 results
    results_file = Path(__file__).parent / 'results' / 'cycle169_critical_transition_mapping.json'

    if not results_file.exists():
        print(f"C169 results not found: {results_file}")
        return None

    with open(results_file, 'r') as f:
        data = json.load(f)

    # Extract data
    frequencies = data['metadata']['frequencies']
    basin_summary = data['basin_summary']

    basin_a_pct = [basin_summary[str(f)]['basin_a_pct'] for f in frequencies]
    critical_freq = data['transition_analysis']['critical_frequency']

    # Create visualizer
    viz = BistabilityVisualizer(Path(__file__).parent / 'visualizations')

    # Generate plot
    plot_path = viz.plot_bifurcation_diagram(
        frequencies=frequencies,
        basin_a_percentages=basin_a_pct,
        critical_freq=critical_freq,
        title='C169: Sharp Bistable Bifurcation at 2.55%'
    )

    print(f"C169 bifurcation plot created: {plot_path}")
    return plot_path


def create_c170_linear_regression_plot():
    """Create linear regression plot from C170 threshold validation."""

    # Load C170 results
    results_file = Path(__file__).parent / 'results' / 'cycle170_basin_threshold_sensitivity.json'

    if not results_file.exists():
        print(f"C170 results not found: {results_file}")
        return None

    with open(results_file, 'r') as f:
        data = json.load(f)

    # Extract data
    threshold_analyses = data['threshold_analyses']
    thresholds = sorted([float(t) for t in threshold_analyses.keys()])
    critical_freqs = [threshold_analyses[str(t)]['critical_frequency'] for t in thresholds]

    # Remove None values if any
    valid_data = [(t, cf) for t, cf in zip(thresholds, critical_freqs) if cf is not None]
    thresholds = [t for t, cf in valid_data]
    critical_freqs = [cf for t, cf in valid_data]

    # Linear regression parameters
    lr = data['linear_regression']
    slope = lr['slope']
    intercept = lr['intercept']
    r_squared = lr['r_squared']

    # Create visualizer
    viz = BistabilityVisualizer(Path(__file__).parent / 'visualizations')

    # Generate plot
    plot_path = viz.plot_linear_regression(
        thresholds=thresholds,
        critical_frequencies=critical_freqs,
        slope=slope,
        intercept=intercept,
        r_squared=r_squared,
        title='C170: Definitive Linear Relationship (R² = 0.9954)'
    )

    print(f"C170 linear regression plot created: {plot_path}")
    return plot_path


def create_complete_phase_diagram():
    """Create complete 2D phase diagram from validated parameters."""

    # Use C170 validated parameters
    slope = 0.98
    intercept = 0.04

    # Create visualizer
    viz = BistabilityVisualizer(Path(__file__).parent / 'visualizations')

    # Generate plot
    plot_path = viz.plot_phase_diagram(
        frequency_range=(0.5, 5.0),
        threshold_range=(1.0, 4.0),
        slope=slope,
        intercept=intercept,
        title='Complete Bistable Phase Diagram (C168-C170 Validated)'
    )

    print(f"Complete phase diagram created: {plot_path}")
    return plot_path


if __name__ == '__main__':
    """Generate all publication-grade visualizations."""

    print("=" * 80)
    print("GENERATING PUBLICATION-GRADE VISUALIZATIONS")
    print("=" * 80)
    print()

    # Create output directory
    viz_dir = Path(__file__).parent / 'visualizations'
    viz_dir.mkdir(exist_ok=True)

    # Generate C169 bifurcation plot
    print("Creating C169 bifurcation diagram...")
    c169_plot = create_c169_bifurcation_plot()

    # Generate C170 linear regression plot
    print("Creating C170 linear regression plot...")
    c170_plot = create_c170_linear_regression_plot()

    # Generate complete phase diagram
    print("Creating complete phase diagram...")
    phase_diagram = create_complete_phase_diagram()

    print()
    print("=" * 80)
    print("VISUALIZATION GENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Plots saved to: {viz_dir}")
    print()
    print("Generated plots:")
    if c169_plot:
        print(f"  - C169 Bifurcation: {c169_plot}")
    if c170_plot:
        print(f"  - C170 Linear Regression: {c170_plot}")
    if phase_diagram:
        print(f"  - Complete Phase Diagram: {phase_diagram}")
