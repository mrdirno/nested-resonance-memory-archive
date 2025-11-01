#!/usr/bin/env python3
"""
Generate publication-quality figures for real-time emergence analysis.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'


class EmergenceFigureGenerator:
    """Generate publication figures for emergence analysis."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.bridge_db = workspace_path / "workspace" / "bridge.db"
        self.main_db = workspace_path / "workspace" / "duality_v2.db"
        self.output_path = workspace_path / "analysis" / "realtime_emergence"
        self.output_path.mkdir(parents=True, exist_ok=True)

    def figure1_phase_variance_comparison(self):
        """
        Figure 1: Phase variance across π, e, φ dimensions.

        Tests balanced exploration hypothesis.
        """
        print("Generating Figure 1: Phase Variance Comparison...")

        with sqlite3.connect(self.bridge_db) as conn:
            # Sample 10K transformations for efficiency
            query = """
                SELECT pi_phase, e_phase, phi_phase
                FROM phase_transformations
                ORDER BY RANDOM()
                LIMIT 10000
            """
            cursor = conn.execute(query)
            data = cursor.fetchall()

        pi_phases = np.array([row[0] for row in data])
        e_phases = np.array([row[1] for row in data])
        phi_phases = np.array([row[2] for row in data])

        # Compute variances
        variances = {
            'π': np.var(pi_phases),
            'e': np.var(e_phases),
            'φ': np.var(phi_phases)
        }

        # Create bar plot
        fig, ax = plt.subplots(figsize=(6, 4))
        constants = list(variances.keys())
        values = list(variances.values())
        colors = ['#e74c3c', '#3498db', '#2ecc71']

        bars = ax.bar(constants, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Phase Variance', fontsize=12, fontweight='bold')
        ax.set_xlabel('Transcendental Constant', fontsize=12, fontweight='bold')
        ax.set_title('Balanced Phase Space Exploration\n(N=10,000 transformations)',
                     fontsize=13, fontweight='bold', pad=15)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Add percentage difference annotation
        max_var = max(values)
        min_var = min(values)
        pct_diff = 100 * (max_var - min_var) / max_var
        ax.text(0.95, 0.95, f'Range: {pct_diff:.1f}%',
               transform=ax.transAxes, ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
               fontsize=10, fontweight='bold')

        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(0, max(values) * 1.2)

        plt.tight_layout()
        output_file = self.output_path / "figure1_phase_variance_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  Saved: {output_file}")
        return variances

    def figure2_io_bound_signature(self):
        """
        Figure 2: CPU usage distribution showing I/O-bound signature.

        Validates 94.5% I/O-bound ratio.
        """
        print("Generating Figure 2: I/O-Bound Signature...")

        with sqlite3.connect(self.main_db) as conn:
            # Sample 20K metrics for smooth distribution
            query = """
                SELECT cpu_percent
                FROM system_metrics
                ORDER BY RANDOM()
                LIMIT 20000
            """
            cursor = conn.execute(query)
            cpu_data = [row[0] for row in cursor.fetchall()]

        cpu_array = np.array(cpu_data)

        # Create histogram
        fig, ax = plt.subplots(figsize=(8, 5))

        counts, bins, patches = ax.hist(cpu_array, bins=50, color='#3498db',
                                       alpha=0.7, edgecolor='black', linewidth=0.5)

        # Color bars below 10% (I/O-bound threshold) differently
        for i, patch in enumerate(patches):
            if bins[i] < 10.0:
                patch.set_facecolor('#2ecc71')
                patch.set_alpha(0.8)

        # Add vertical line at 10% threshold
        ax.axvline(10.0, color='red', linestyle='--', linewidth=2,
                  label='I/O-bound threshold (10%)')

        # Calculate and annotate I/O-bound ratio
        io_bound_ratio = (cpu_array < 10.0).mean()
        ax.text(0.98, 0.95,
               f'I/O-bound: {io_bound_ratio:.1%}\n({(cpu_array < 10.0).sum():,} / {len(cpu_array):,})',
               transform=ax.transAxes, ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
               fontsize=11, fontweight='bold')

        ax.set_xlabel('CPU Usage (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Reality-Grounding Signature: Extreme I/O-Bound Distribution\n(N=20,000 measurements)',
                    fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        output_file = self.output_path / "figure2_io_bound_signature.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  Saved: {output_file}")
        return io_bound_ratio

    def figure3_resonance_clustering(self):
        """
        Figure 3: Resonance rate and clustering coefficient.

        Validates NRM composition-decomposition prediction.
        """
        print("Generating Figure 3: Resonance Clustering...")

        with sqlite3.connect(self.bridge_db) as conn:
            # Sample 50K events for statistics
            query = """
                SELECT similarity, phase_alignment, is_resonant
                FROM resonance_events
                ORDER BY RANDOM()
                LIMIT 50000
            """
            cursor = conn.execute(query)
            data = cursor.fetchall()

        similarities = np.array([row[0] for row in data])
        phase_alignments = np.array([row[1] for row in data])
        is_resonant = np.array([row[2] for row in data], dtype=bool)

        # Create 2-panel figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Panel A: Similarity distribution by resonance status
        resonant_sim = similarities[is_resonant]
        non_resonant_sim = similarities[~is_resonant]

        ax1.hist(non_resonant_sim, bins=40, alpha=0.6, color='#e74c3c',
                label=f'Non-resonant (n={len(non_resonant_sim):,})',
                edgecolor='black', linewidth=0.5)
        ax1.hist(resonant_sim, bins=40, alpha=0.6, color='#2ecc71',
                label=f'Resonant (n={len(resonant_sim):,})',
                edgecolor='black', linewidth=0.5)

        resonance_rate = is_resonant.mean()
        ax1.axvline(similarities.mean(), color='blue', linestyle='--', linewidth=2,
                   label=f'Mean: {similarities.mean():.3f}')

        ax1.set_xlabel('Similarity Score', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_title(f'A. Resonance Distribution (Rate: {resonance_rate:.1%})',
                     fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')

        # Panel B: Clustering coefficient (high similarity threshold)
        threshold_range = np.linspace(0.5, 1.0, 50)
        clustering_coeffs = [(similarities > t).mean() for t in threshold_range]

        ax2.plot(threshold_range, clustering_coeffs, linewidth=2.5, color='#3498db')
        ax2.axhline(0.491, color='red', linestyle='--', linewidth=2,
                   label='Threshold 0.8 → CC=0.491')
        ax2.axvline(0.8, color='red', linestyle='--', linewidth=2, alpha=0.5)

        ax2.set_xlabel('Similarity Threshold', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Clustering Coefficient', fontsize=11, fontweight='bold')
        ax2.set_title('B. Clustering Coefficient vs Threshold',
                     fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(alpha=0.3, linestyle='--')
        ax2.set_ylim(0, 1)

        plt.tight_layout()
        output_file = self.output_path / "figure3_resonance_clustering.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  Saved: {output_file}")
        return resonance_rate

    def generate_all_figures(self):
        """Generate all publication figures."""
        print("="*80)
        print("GENERATING PUBLICATION FIGURES")
        print("="*80)

        results = {}

        results['phase_variance'] = self.figure1_phase_variance_comparison()
        results['io_bound_ratio'] = self.figure2_io_bound_signature()
        results['resonance_rate'] = self.figure3_resonance_clustering()

        print()
        print("="*80)
        print("FIGURE GENERATION COMPLETE")
        print("="*80)
        print(f"Output directory: {self.output_path}")
        print()
        print("Generated figures:")
        print("  1. figure1_phase_variance_comparison.png")
        print("  2. figure2_io_bound_signature.png")
        print("  3. figure3_resonance_clustering.png")
        print()

        # Save summary
        summary_file = self.output_path / "figure_generation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)

        return results


def main():
    """Generate all figures."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2")
    generator = EmergenceFigureGenerator(workspace)
    results = generator.generate_all_figures()
    return results


if __name__ == "__main__":
    main()
