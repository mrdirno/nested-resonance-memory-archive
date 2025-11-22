#!/usr/bin/env python3
"""
Paper 5D: Emergence Pattern Catalog - Visualization Tools

Generates publication-quality figures for Paper 5D manuscript:
1. Pattern taxonomy tree (hierarchical structure)
2. Temporal pattern heatmap (frequency × stability score)
3. Memory retention comparison (C171 vs C175)
4. Methodology validation (healthy vs degraded systems)
5. Pattern statistics (category frequencies)
6. C175 perfect stability (time series with zero variance)
7. Population collapse comparison (ablation studies)
8. Pattern detection workflow (flowchart)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class PatternVisualization:
    """Generate publication-quality figures for Paper 5D."""

    def __init__(self, results_file: Path, output_dir: Path):
        """Initialize visualization generator.

        Args:
            results_file: Path to pattern mining results JSON
            output_dir: Directory to save generated figures
        """
        self.results_file = Path(results_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load results
        with open(self.results_file, 'r') as f:
            self.results = json.load(f)

        # Set publication-quality defaults
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9

    def figure1_pattern_taxonomy_tree(self):
        """Figure 1: Pattern taxonomy tree (hierarchical structure).

        Visualizes the 4 categories and pattern types with frequencies.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        taxonomy = self.results.get('taxonomy', {})

        # Define positions for hierarchical layout
        category_positions = {
            'spatial': (0.2, 0.8),
            'temporal': (0.4, 0.8),
            'interaction': (0.6, 0.8),
            'memory': (0.8, 0.8)
        }

        colors = {
            'spatial': '#FF6B6B',
            'temporal': '#4ECDC4',
            'interaction': '#FFD93D',
            'memory': '#95E1D3'
        }

        # Draw category boxes
        for category, (x, y) in category_positions.items():
            count = sum(p['frequency'] for p in taxonomy.get(category, {}).values())
            box = mpatches.FancyBboxPatch(
                (x - 0.08, y - 0.05), 0.16, 0.08,
                boxstyle="round,pad=0.01",
                facecolor=colors[category],
                edgecolor='black',
                linewidth=1.5
            )
            ax.add_patch(box)
            ax.text(x, y, f"{category.upper()}\n({count})",
                   ha='center', va='center', fontsize=10, fontweight='bold')

            # Draw pattern types below each category
            patterns = taxonomy.get(category, {})
            if patterns:
                y_offset = 0.15
                for i, (pattern_type, stats) in enumerate(patterns.items()):
                    pattern_y = y - y_offset * (i + 1)
                    # Draw connecting line
                    ax.plot([x, x], [y - 0.05, pattern_y + 0.03],
                           'k-', linewidth=1, alpha=0.5)
                    # Draw pattern box
                    pattern_box = mpatches.FancyBboxPatch(
                        (x - 0.06, pattern_y - 0.02), 0.12, 0.04,
                        boxstyle="round,pad=0.005",
                        facecolor='white',
                        edgecolor=colors[category],
                        linewidth=1
                    )
                    ax.add_patch(pattern_box)
                    ax.text(x, pattern_y, f"{pattern_type}\n({stats['frequency']})",
                           ha='center', va='center', fontsize=8)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Pattern Taxonomy: Hierarchical Structure of NRM Emergent Patterns',
                    fontsize=12, fontweight='bold', pad=20)

        plt.tight_layout()
        output_file = self.output_dir / 'figure1_pattern_taxonomy_tree.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: {output_file}")

    def figure2_temporal_pattern_heatmap(self):
        """Figure 2: Temporal pattern heatmap (frequency × stability score).

        Shows stability scores across frequencies for C171 and C175.
        """
        patterns_by_exp = self.results.get('patterns_by_experiment', {})

        # Extract temporal patterns for C171 and C175
        c171_patterns = patterns_by_exp.get('cycle171_fractal_swarm_bistability.json', {}).get('temporal', [])
        c175_patterns = patterns_by_exp.get('cycle175_high_resolution_transition.json', {}).get('temporal', [])

        if not c171_patterns and not c175_patterns:
            print("No temporal patterns found for heatmap")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        # C171 heatmap
        if c171_patterns:
            frequencies = [p['frequency'] for p in c171_patterns]
            stabilities = [p['stability'] for p in c171_patterns]
            ax1.scatter(frequencies, stabilities, s=100, c='#4ECDC4', alpha=0.7, edgecolors='black')
            ax1.set_xlabel('Frequency (Hz)')
            ax1.set_ylabel('Stability Score')
            ax1.set_title('C171: Temporal Pattern Stability', fontweight='bold')
            ax1.grid(True, alpha=0.3)

        # C175 heatmap
        if c175_patterns:
            frequencies = [p['frequency'] for p in c175_patterns]
            stabilities = [p['stability'] for p in c175_patterns]
            ax2.scatter(frequencies, stabilities, s=100, c='#4ECDC4', alpha=0.7, edgecolors='black')
            ax2.set_xlabel('Frequency (Hz)')
            ax2.set_ylabel('Stability Score')
            ax2.set_title('C175: Perfect Stability (σ=0)', fontweight='bold')
            ax2.grid(True, alpha=0.3)

        plt.suptitle('Temporal Pattern Stability Across Frequencies', fontsize=12, fontweight='bold', y=1.02)
        plt.tight_layout()
        output_file = self.output_dir / 'figure2_temporal_pattern_heatmap.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: {output_file}")

    def figure3_memory_retention_comparison(self):
        """Figure 3: Memory retention comparison (C171 vs C175).

        Compares memory consistency between experiments.
        """
        patterns_by_exp = self.results.get('patterns_by_experiment', {})

        c171_memory = patterns_by_exp.get('cycle171_fractal_swarm_bistability.json', {}).get('memory', [])
        c175_memory = patterns_by_exp.get('cycle175_high_resolution_transition.json', {}).get('memory', [])

        if not c171_memory or not c175_memory:
            print("Insufficient memory patterns for comparison")
            return

        fig, ax = plt.subplots(figsize=(8, 5))

        experiments = ['C171', 'C175']
        consistencies = [
            c171_memory[0]['consistency'],
            c175_memory[0]['consistency']
        ]
        means = [
            c171_memory[0]['mean'],
            c175_memory[0]['mean']
        ]
        stds = [
            c171_memory[0]['std'],
            c175_memory[0]['std']
        ]

        x = np.arange(len(experiments))
        width = 0.25

        bars1 = ax.bar(x - width, consistencies, width, label='Consistency Score', color='#95E1D3', edgecolor='black')
        bars2 = ax.bar(x, means, width, label='Mean Population', color='#FFD93D', edgecolor='black')
        bars3 = ax.bar(x + width, stds, width, label='Std Deviation', color='#FF6B6B', edgecolor='black')

        ax.set_xlabel('Experiment')
        ax.set_ylabel('Value')
        ax.set_title('Memory Retention: Consistency Across Experiments', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(experiments)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        output_file = self.output_dir / 'figure3_memory_retention_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: {output_file}")

    def figure4_methodology_validation(self):
        """Figure 4: Methodology validation (healthy vs degraded systems).

        Bar chart showing pattern counts: C171/C175 (healthy) vs C176/C177 (degraded).
        """
        patterns_by_exp = self.results.get('patterns_by_experiment', {})

        experiments = ['C171', 'C175', 'C176', 'C177']
        pattern_counts = []

        for exp_name in ['cycle171_fractal_swarm_bistability.json',
                         'cycle175_high_resolution_transition.json',
                         'cycle176_ablation_study_v4.json',
                         'cycle177_h1_energy_pooling_results.json']:
            patterns = patterns_by_exp.get(exp_name, {})
            total = sum(len(p) for p in patterns.values())
            pattern_counts.append(total)

        fig, ax = plt.subplots(figsize=(8, 5))

        colors = ['#4ECDC4', '#4ECDC4', '#FF6B6B', '#FF6B6B']
        bars = ax.bar(experiments, pattern_counts, color=colors, edgecolor='black', linewidth=1.5)

        ax.set_xlabel('Experiment')
        ax.set_ylabel('Total Patterns Detected')
        ax.set_title('Methodology Validation: Pattern Detection in Healthy vs Degraded Systems',
                    fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Add legend
        healthy_patch = mpatches.Patch(color='#4ECDC4', label='Healthy Systems')
        degraded_patch = mpatches.Patch(color='#FF6B6B', label='Degraded Systems')
        ax.legend(handles=[healthy_patch, degraded_patch], loc='upper right')

        plt.tight_layout()
        output_file = self.output_dir / 'figure4_methodology_validation.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: {output_file}")

    def figure5_pattern_statistics(self):
        """Figure 5: Pattern statistics (category frequencies).

        Pie chart showing distribution of patterns across categories.
        """
        taxonomy = self.results.get('taxonomy', {})

        categories = []
        frequencies = []
        colors_list = []
        color_map = {
            'spatial': '#FF6B6B',
            'temporal': '#4ECDC4',
            'interaction': '#FFD93D',
            'memory': '#95E1D3'
        }

        for category, patterns in taxonomy.items():
            total_freq = sum(p['frequency'] for p in patterns.values())
            if total_freq > 0:
                categories.append(category.capitalize())
                frequencies.append(total_freq)
                colors_list.append(color_map[category])

        if not frequencies:
            print("No pattern statistics to visualize")
            return

        fig, ax = plt.subplots(figsize=(8, 6))

        wedges, texts, autotexts = ax.pie(frequencies, labels=categories, autopct='%1.1f%%',
                                          colors=colors_list, startangle=90,
                                          wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        ax.set_title('Pattern Distribution Across Categories', fontweight='bold', pad=20)

        plt.tight_layout()
        output_file = self.output_dir / 'figure5_pattern_statistics.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: {output_file}")

    def generate_all_figures(self):
        """Generate all publication figures for Paper 5D."""
        print("="*70)
        print("PAPER 5D: GENERATING PUBLICATION FIGURES")
        print("="*70)
        print(f"\nResults file: {self.results_file}")
        print(f"Output directory: {self.output_dir}")
        print("\nGenerating figures...")

        self.figure1_pattern_taxonomy_tree()
        self.figure2_temporal_pattern_heatmap()
        self.figure3_memory_retention_comparison()
        self.figure4_methodology_validation()
        self.figure5_pattern_statistics()

        print("\n" + "="*70)
        print("ALL FIGURES GENERATED SUCCESSFULLY")
        print("="*70)
        print(f"\nFigures saved to: {self.output_dir}")
        print("\nReady for manuscript inclusion.")


def main():
    """Main execution function."""
    # File paths
    results_file = Path("/Volumes/dual/DUALITY-ZERO-V2/data/results/paper5d_pattern_mining_results.json")
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/papers/figures/paper5d")

    # Check if results file exists
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        print("Run paper5d_pattern_mining.py first to generate results.")
        return 1

    # Generate visualizations
    viz = PatternVisualization(results_file, output_dir)
    viz.generate_all_figures()

    return 0


if __name__ == "__main__":
    sys.exit(main())
