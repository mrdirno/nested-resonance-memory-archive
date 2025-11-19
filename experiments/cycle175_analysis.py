#!/usr/bin/env python3
"""
CYCLE 175 ANALYSIS: High-Resolution Transition Width Calculation

Purpose: Process C175 experimental data to quantify exact bistable transition width

Analysis Tasks:
1. Load C175 high-resolution results (0.01% step size)
2. Calculate precise transition width
3. Identify mixed-basin frequencies (stochastic bistability indicators)
4. Generate publication-ready statistics and visualizations
5. Produce manuscript-ready table for Paper 1 integration

Expected Outputs:
- Transition width quantification (± 0.01% precision)
- Basin occupation percentages per frequency
- Mixed-basin frequency detection
- Publication figure (high-resolution bifurcation diagram)
- LaTeX-formatted table for manuscript

Date: 2025-10-25
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Import visualization utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from visualization_utils import BistabilityVisualizer

class C175Analyzer:
    """High-resolution transition analysis for C175 results."""

    def __init__(self, results_path: Path):
        """
        Initialize analyzer with C175 results.

        Args:
            results_path: Path to cycle175_high_resolution_transition.json
        """
        self.results_path = Path(results_path)
        self.data = None
        self.frequencies = []
        self.basin_occupation = {}  # frequency -> % Basin A
        self.composition_stats = {}  # frequency -> (mean, std)
        self.mixed_freqs = []
        self.transition_width = None
        self.last_b_freq = None
        self.first_a_freq = None

    def load_data(self) -> bool:
        """Load C175 JSON results."""
        if not self.results_path.exists():
            print(f"❌ Results file not found: {self.results_path}")
            return False

        with open(self.results_path, 'r') as f:
            self.data = json.load(f)

        print(f"✅ Loaded {len(self.data['experiments'])} experiments")
        print(f"   Frequencies: {len(self.data['metadata']['frequencies'])} (step size: {self.data['metadata']['step_size']:.2f}%)")
        print(f"   Duration: {self.data['metadata']['duration_minutes']:.2f} minutes")
        return True

    def analyze_basin_occupation(self):
        """Calculate basin occupation percentages per frequency."""
        experiments = self.data['experiments']

        # Group by frequency
        by_frequency = defaultdict(list)
        for exp in experiments:
            by_frequency[exp['frequency']].append(exp)

        self.frequencies = sorted(by_frequency.keys())

        print("\nBASIN OCCUPATION ANALYSIS:")
        print("=" * 80)
        print(f"{'Frequency':>10} | {'Basin A %':>10} | {'n':>3} | {'Avg Comp':>9} | {'Std Comp':>9} | {'Basin':>6}")
        print("-" * 80)

        for freq in self.frequencies:
            freq_exps = by_frequency[freq]
            basin_a_count = sum(1 for exp in freq_exps if exp['basin'] == 'A')
            basin_a_pct = (basin_a_count / len(freq_exps)) * 100

            comp_events = [exp['avg_composition_events'] for exp in freq_exps]
            comp_mean = np.mean(comp_events)
            comp_std = np.std(comp_events)

            # Store statistics
            self.basin_occupation[freq] = basin_a_pct
            self.composition_stats[freq] = (comp_mean, comp_std)

            # Determine basin classification
            if basin_a_pct == 100:
                basin_str = "A"
            elif basin_a_pct == 0:
                basin_str = "B"
            else:
                basin_str = "MIXED"
                self.mixed_freqs.append(freq)

            print(f"{freq:>9.2f}% | {basin_a_pct:>9.0f}% | {len(freq_exps):>3} | "
                  f"{comp_mean:>9.2f} | {comp_std:>9.2f} | {basin_str:>6}")

        print()

    def calculate_transition_width(self):
        """Calculate exact transition width with ±0.01% precision."""
        print("TRANSITION WIDTH CALCULATION:")
        print("=" * 80)

        # Find last 100% Basin B frequency
        for freq in self.frequencies:
            if self.basin_occupation[freq] == 0:
                self.last_b_freq = freq
            else:
                break

        # Find first 100% Basin A frequency
        for freq in self.frequencies:
            if self.basin_occupation[freq] == 100:
                self.first_a_freq = freq
                break

        if self.last_b_freq is not None and self.first_a_freq is not None:
            self.transition_width = self.first_a_freq - self.last_b_freq

            print(f"Last 100% Basin B: {self.last_b_freq:.2f}%")
            print(f"First 100% Basin A: {self.first_a_freq:.2f}%")
            print(f"Transition width: {self.transition_width:.2f}%")
            print()

            # Classification
            if self.transition_width <= 0.01:
                print("✅ ULTRA-SHARP TRANSITION: Width ≤0.01% (single-step)")
                print("   Classification: First-order phase transition")
                print("   Implication: Infinitesimal frequency change induces macroscopic state change")
            elif self.transition_width <= 0.05:
                print("✅ VERY SHARP TRANSITION: Width ≤0.05%")
                print("   Classification: First-order (narrow coexistence region)")
            elif self.transition_width <= 0.10:
                print("✅ SHARP TRANSITION: Width ≤0.10% (validates C169 findings)")
                print("   Classification: First-order")
            else:
                print("⚠️  GRADUAL TRANSITION: Width >0.10%")
                print("   Classification: Possibly second-order or crossover")
        else:
            print("⚠️  Could not determine clear transition boundaries")
            print(f"   Last B: {self.last_b_freq}, First A: {self.first_a_freq}")

        print()

    def analyze_mixed_basins(self):
        """Analyze mixed-basin frequencies (stochastic bistability indicators)."""
        if not self.mixed_freqs:
            print("NO MIXED-BASIN FREQUENCIES DETECTED")
            print("=" * 80)
            print("Implication: Transition width <0.01% (sharper than measurement resolution)")
            print("All frequencies show deterministic basin selection (100% or 0% occupation)")
            print()
            return

        print("MIXED-BASIN FREQUENCIES (Stochastic Bistability):")
        print("=" * 80)

        for freq in self.mixed_freqs:
            basin_a_pct = self.basin_occupation[freq]
            comp_mean, comp_std = self.composition_stats[freq]

            print(f"Frequency: {freq:.2f}%")
            print(f"  Basin A occupation: {basin_a_pct:.0f}%")
            print(f"  Basin B occupation: {100 - basin_a_pct:.0f}%")
            print(f"  Composition events: {comp_mean:.2f} ± {comp_std:.2f}")
            print(f"  Interpretation: Stochastic selection - both basins accessible")
            print()

        print("⭐ CRITICAL FINDING:")
        print(f"   Mixed basins at {len(self.mixed_freqs)} frequency/frequencies")
        print("   Indicates coexistence region width ~0.01% per mixed frequency")
        print()

    def generate_publication_table(self) -> str:
        """Generate LaTeX-formatted table for manuscript."""
        latex = []
        latex.append("% C175 High-Resolution Transition Data")
        latex.append("% Table: Basin occupation vs. spawn frequency (0.01% resolution)")
        latex.append("")
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{High-resolution bistable transition mapping (C175, n=10 per frequency)}")
        latex.append("\\label{tab:c175_high_resolution}")
        latex.append("\\begin{tabular}{cccccc}")
        latex.append("\\hline")
        latex.append("Frequency & Basin A & Basin B & Composition & Std Dev & Classification \\\\")
        latex.append("(\\%) & (\\%) & (\\%) & (events/window) & & \\\\")
        latex.append("\\hline")

        for freq in self.frequencies:
            basin_a_pct = self.basin_occupation[freq]
            basin_b_pct = 100 - basin_a_pct
            comp_mean, comp_std = self.composition_stats[freq]

            if basin_a_pct == 100:
                classification = "Basin A"
            elif basin_a_pct == 0:
                classification = "Basin B"
            else:
                classification = "\\textbf{Mixed}"

            latex.append(f"{freq:.2f} & {basin_a_pct:.0f} & {basin_b_pct:.0f} & "
                        f"{comp_mean:.2f} & {comp_std:.2f} & {classification} \\\\")

        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        return "\n".join(latex)

    def generate_visualizations(self, output_dir: Path):
        """Generate publication-grade figures using BistabilityVisualizer."""
        print("GENERATING PUBLICATION FIGURES:")
        print("=" * 80)

        viz = BistabilityVisualizer(output_dir)

        # Prepare data
        frequencies_list = self.frequencies
        basin_a_percentages = [self.basin_occupation[f] for f in frequencies_list]
        composition_means = [self.composition_stats[f][0] for f in frequencies_list]
        composition_stds = [self.composition_stats[f][1] for f in frequencies_list]

        # Figure 1: High-resolution bifurcation diagram
        print("Creating Figure 1: High-resolution bifurcation diagram...")
        fig1_path = viz.plot_high_resolution_bifurcation(
            frequencies=frequencies_list,
            basin_a_percentages=basin_a_percentages,
            title="High-Resolution Bistable Transition (C175, 0.01% steps)",
            critical_frequency=2.55  # From C169
        )
        print(f"  ✅ Saved: {fig1_path}")

        # Figure 2: Composition events vs. frequency (with error bars)
        print("Creating Figure 2: Composition events vs. frequency...")
        fig2_path = viz.plot_composition_vs_frequency(
            frequencies=frequencies_list,
            compositions=composition_means,
            composition_stds=composition_stds,
            title="Composition Events vs. Spawn Frequency (High-Resolution)"
        )
        print(f"  ✅ Saved: {fig2_path}")

        print()

    def generate_summary_report(self) -> str:
        """Generate comprehensive text summary for manuscript integration."""
        lines = []
        lines.append("=" * 80)
        lines.append("CYCLE 175: HIGH-RESOLUTION TRANSITION ANALYSIS SUMMARY")
        lines.append("=" * 80)
        lines.append("")

        # Key findings
        lines.append("KEY FINDINGS:")
        lines.append("-" * 80)

        if self.transition_width is not None:
            lines.append(f"✅ Transition width: {self.transition_width:.2f}%")
            lines.append(f"   Last 100% Basin B: {self.last_b_freq:.2f}%")
            lines.append(f"   First 100% Basin A: {self.first_a_freq:.2f}%")
        else:
            lines.append("⚠️  Transition boundaries unclear")

        if self.mixed_freqs:
            lines.append(f"⭐ Mixed-basin frequencies: {len(self.mixed_freqs)}")
            for freq in self.mixed_freqs:
                lines.append(f"   - {freq:.2f}%: {self.basin_occupation[freq]:.0f}% Basin A")
        else:
            lines.append("✅ No mixed basins (transition <0.01%)")

        lines.append("")

        # Publication implications
        lines.append("PUBLICATION IMPLICATIONS:")
        lines.append("-" * 80)

        if self.transition_width and self.transition_width <= 0.01:
            lines.append("✅ Can claim: 'Ultra-sharp transition width ≤0.01%'")
            lines.append("   Addresses Frank's precision critique proactively")
            lines.append("   First-order phase transition confirmed")
        elif self.transition_width and self.transition_width <= 0.05:
            lines.append("✅ Can claim: 'Very sharp transition width ≤0.05%'")
            lines.append("   Validates C169 qualitative findings with higher precision")
        elif self.transition_width and self.transition_width <= 0.10:
            lines.append("✅ Can claim: 'Sharp transition width ≤0.10%'")
            lines.append("   Confirms C169 measurement resolution")
        else:
            lines.append("⚠️  Transition wider than expected - investigate mechanism")

        lines.append("")

        # Manuscript integration
        lines.append("MANUSCRIPT INTEGRATION:")
        lines.append("-" * 80)
        lines.append("Paper 1 (Bistability) - Update precision claims:")
        lines.append(f"  - Replace '<0.1%' with '≤{self.transition_width:.2f}%'")
        lines.append("  - Add C175 high-resolution validation paragraph")
        lines.append("  - Include LaTeX table (see below)")
        lines.append("  - Add high-resolution bifurcation figure")
        lines.append("")
        lines.append("Paper 2 (Homeostasis) - Strengthen comparison:")
        lines.append("  - Contrast simplified sharp transition with complete saturation")
        lines.append("  - Use C175 precision as baseline for framework comparison")
        lines.append("")

        # Statistical summary
        lines.append("STATISTICAL SUMMARY:")
        lines.append("-" * 80)
        lines.append(f"Frequencies tested: {len(self.frequencies)}")
        lines.append(f"Step size: {self.data['metadata']['step_size']:.2f}%")
        lines.append(f"Experiments per frequency: {len(self.data['metadata']['seeds'])}")
        lines.append(f"Total experiments: {len(self.data['experiments'])}")
        lines.append(f"Duration: {self.data['metadata']['duration_minutes']:.2f} minutes")
        lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def save_analysis_report(self, output_path: Path):
        """Save complete analysis report to file."""
        report = []
        report.append(self.generate_summary_report())
        report.append("\n\n")
        report.append(self.generate_publication_table())

        with open(output_path, 'w') as f:
            f.write("\n".join(report))

        print(f"✅ Analysis report saved: {output_path}")


def main():
    """Execute C175 analysis pipeline."""
    print("=" * 80)
    print("CYCLE 175 ANALYSIS: High-Resolution Transition Width")
    print("=" * 80)
    print()

    # Paths
    experiments_dir = Path(__file__).parent
    results_path = experiments_dir / "results" / "cycle175_high_resolution_transition.json"
    output_dir = experiments_dir / "figures"
    report_path = experiments_dir / "results" / "cycle175_analysis_report.txt"
    latex_path = experiments_dir / "results" / "cycle175_table.tex"

    # Create output directories
    output_dir.mkdir(exist_ok=True)

    # Initialize analyzer
    analyzer = C175Analyzer(results_path)

    # Load data
    if not analyzer.load_data():
        print("❌ Could not load C175 results - ensure experiment has completed")
        return

    print()

    # Run analyses
    analyzer.analyze_basin_occupation()
    analyzer.calculate_transition_width()
    analyzer.analyze_mixed_basins()

    # Generate outputs
    print()
    analyzer.generate_visualizations(output_dir)

    # Generate reports
    summary = analyzer.generate_summary_report()
    print(summary)

    # Save LaTeX table
    latex_table = analyzer.generate_publication_table()
    with open(latex_path, 'w') as f:
        f.write(latex_table)
    print(f"✅ LaTeX table saved: {latex_path}")
    print()

    # Save complete analysis report
    analyzer.save_analysis_report(report_path)

    print()
    print("=" * 80)
    print("C175 ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("1. Review high-resolution bifurcation figure")
    print("2. Integrate LaTeX table into Paper 1 manuscript")
    print("3. Update precision claims based on measured transition width")
    print("4. Launch C176 ablation study (mechanism isolation)")
    print()


if __name__ == "__main__":
    main()
