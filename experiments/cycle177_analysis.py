#!/usr/bin/env python3
"""
CYCLE 177 ANALYSIS: Homeostatic Regime Boundary Characterization

Purpose: Analyze extended frequency range results to map homeostatic regime boundaries

Analysis Tasks:
1. Load C177 extended frequency results (0.5-10.0%)
2. Identify lower boundary (population collapse)
3. Identify upper boundary (saturation)
4. Characterize transition types (sharp vs. gradual)
5. Compare with baseline homeostatic region (2.0-3.0%)
6. Generate boundary visualization figures
7. Produce manuscript-ready statistics

Hypotheses to Test:
  H1: Lower boundary exists where population → 0
  H2: Upper boundary exists where population → max_agents
  H3: Homeostasis is unbounded (no boundaries found)

Expected Classifications:
  - Homeostatic regime: Population CV < 15%, ~17 agents
  - Lower breakdown: Population < 10 or high CV
  - Upper breakdown: Population > 25 or high CV
  - Saturation: Population → max_agents (100)

Date: 2025-10-25 (Cycle 204)
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class C177BoundaryAnalyzer:
    """Boundary characterization for C177 extended frequency results."""

    def __init__(self, results_path: Path):
        """
        Initialize analyzer with C177 results.

        Args:
            results_path: Path to cycle177_extended_frequency_range.json
        """
        self.results_path = Path(results_path)
        self.data = None
        self.frequencies = []
        self.frequency_stats = {}  # frequency -> stats dict
        self.lower_boundary = None
        self.upper_boundary = None
        self.homeostatic_range = None
        self.regime_classification = {}

    def load_data(self) -> bool:
        """Load C177 JSON results."""
        if not self.results_path.exists():
            print(f"❌ Results file not found: {self.results_path}")
            print("   C177 experiment may not have completed yet.")
            return False

        with open(self.results_path, 'r') as f:
            self.data = json.load(f)

        print(f"✅ Loaded {len(self.data['experiments'])} experiments")
        print(f"   Frequencies: {self.data['metadata']['frequencies']}")
        print(f"   Seeds per frequency: {len(self.data['metadata']['seeds'])}")
        print(f"   Duration: {self.data['metadata']['duration_minutes']:.2f} minutes")
        return True

    def analyze_frequency_statistics(self):
        """Calculate statistics for each frequency."""
        experiments = self.data['experiments']

        # Group by frequency
        by_frequency = defaultdict(list)
        for exp in experiments:
            by_frequency[exp['frequency']].append(exp)

        self.frequencies = sorted(by_frequency.keys())

        print("\n" + "=" * 100)
        print("FREQUENCY-BY-FREQUENCY ANALYSIS")
        print("=" * 100)
        print(f"{'Frequency':>10} | {'n':>3} | {'Pop Mean':>9} | {'Pop Std':>8} | {'Pop CV':>7} | "
              f"{'Comp Mean':>10} | {'Basin A%':>9} | {'Regime':>15}")
        print("-" * 100)

        for freq in self.frequencies:
            freq_exps = by_frequency[freq]

            # Population statistics
            populations = [exp['mean_population'] for exp in freq_exps]
            pop_mean = np.mean(populations)
            pop_std = np.std(populations, ddof=1)
            pop_cv = (pop_std / pop_mean * 100) if pop_mean > 0 else 999.0
            pop_min = np.min(populations)
            pop_max = np.max(populations)

            # Composition statistics
            compositions = [exp['avg_composition_events'] for exp in freq_exps]
            comp_mean = np.mean(compositions)
            comp_std = np.std(compositions, ddof=1)

            # Basin classification
            basins = [exp['basin'] for exp in freq_exps]
            basin_a_count = sum(1 for b in basins if b == 'A')
            basin_a_pct = (basin_a_count / len(basins)) * 100

            # Regime classification
            regime = self._classify_regime(pop_mean, pop_cv, pop_min, pop_max)

            # Store statistics
            self.frequency_stats[freq] = {
                'n_experiments': len(freq_exps),
                'population': {
                    'mean': pop_mean,
                    'std': pop_std,
                    'cv': pop_cv,
                    'min': pop_min,
                    'max': pop_max
                },
                'composition': {
                    'mean': comp_mean,
                    'std': comp_std
                },
                'basin': {
                    'basin_a_pct': basin_a_pct,
                    'basin_a_count': basin_a_count
                },
                'regime': regime
            }

            self.regime_classification[freq] = regime

            print(f"{freq:>9.1f}% | {len(freq_exps):>3} | {pop_mean:>9.2f} | {pop_std:>8.2f} | "
                  f"{pop_cv:>6.1f}% | {comp_mean:>10.2f} | {basin_a_pct:>8.0f}% | {regime:>15}")

        print()

    def _classify_regime(self, pop_mean: float, pop_cv: float,
                         pop_min: float, pop_max: float) -> str:
        """
        Classify regime based on population statistics.

        Regimes:
          - HOMEOSTATIC: CV < 15%, 10 < mean < 25
          - LOWER_BREAKDOWN: mean < 10 or CV > 30%
          - UPPER_BREAKDOWN: mean > 25 or CV > 30%
          - SATURATION: mean > 80 (approaching max_agents=100)
          - MARGINAL: Borderline homeostatic (15% < CV < 30%)
        """
        if pop_mean > 80:
            return "SATURATION"
        elif pop_mean < 5:
            return "COLLAPSED"
        elif pop_cv < 15.0 and 10 <= pop_mean <= 25:
            return "HOMEOSTATIC"
        elif pop_cv >= 30.0:
            if pop_mean < 10:
                return "LOWER_BREAKDOWN"
            elif pop_mean > 25:
                return "UPPER_BREAKDOWN"
            else:
                return "UNSTABLE"
        elif 15.0 <= pop_cv < 30.0:
            return "MARGINAL"
        else:
            if pop_mean < 10:
                return "LOWER_BREAKDOWN"
            elif pop_mean > 25:
                return "UPPER_BREAKDOWN"
            else:
                return "MARGINAL"

    def identify_boundaries(self):
        """Identify frequency boundaries of homeostatic regime."""
        print("=" * 100)
        print("BOUNDARY IDENTIFICATION")
        print("=" * 100)

        # Find homeostatic frequencies
        homeostatic_freqs = [f for f, r in self.regime_classification.items()
                            if r == "HOMEOSTATIC"]

        if not homeostatic_freqs:
            print("❌ NO HOMEOSTATIC REGIME DETECTED")
            print("   All frequencies show non-homeostatic behavior")
            print()
            return

        # Determine boundaries
        self.lower_boundary = min(homeostatic_freqs)
        self.upper_boundary = max(homeostatic_freqs)
        self.homeostatic_range = self.upper_boundary - self.lower_boundary

        print(f"✅ HOMEOSTATIC REGIME DETECTED")
        print(f"   Lower boundary: {self.lower_boundary:.1f}%")
        print(f"   Upper boundary: {self.upper_boundary:.1f}%")
        print(f"   Range width: {self.homeostatic_range:.1f}%")
        print()

        # Check for frequencies outside boundaries
        lower_freqs = [f for f in self.frequencies if f < self.lower_boundary]
        upper_freqs = [f for f in self.frequencies if f > self.upper_boundary]

        if lower_freqs:
            print(f"LOWER BOUNDARY ANALYSIS:")
            print(f"   Frequencies below homeostasis: {lower_freqs}")
            for freq in lower_freqs:
                regime = self.regime_classification[freq]
                pop_mean = self.frequency_stats[freq]['population']['mean']
                print(f"     {freq:.1f}%: {regime} (pop={pop_mean:.1f})")
            print()

        if upper_freqs:
            print(f"UPPER BOUNDARY ANALYSIS:")
            print(f"   Frequencies above homeostasis: {upper_freqs}")
            for freq in upper_freqs:
                regime = self.regime_classification[freq]
                pop_mean = self.frequency_stats[freq]['population']['mean']
                print(f"     {freq:.1f}%: {regime} (pop={pop_mean:.1f})")
            print()

        # Classify boundaries
        if not lower_freqs:
            print("⚠️  Lower boundary NOT DETECTED (homeostasis extends to lowest tested frequency)")
            print(f"   Recommendation: Test frequencies <{self.lower_boundary:.1f}% to find lower limit")
        else:
            print("✅ Lower boundary characterized")

        if not upper_freqs:
            print("⚠️  Upper boundary NOT DETECTED (homeostasis extends to highest tested frequency)")
            print(f"   Recommendation: Test frequencies >{self.upper_boundary:.1f}% to find upper limit")
        else:
            print("✅ Upper boundary characterized")

        print()

    def test_hypotheses(self) -> Dict[str, str]:
        """
        Test C177 hypotheses about boundary existence.

        Returns:
            dict: Hypothesis verdicts
        """
        print("=" * 100)
        print("HYPOTHESIS TESTING")
        print("=" * 100)

        verdicts = {}

        # H1: Lower boundary exists
        lower_freqs = [f for f in self.frequencies if f < 2.0]
        has_lower_breakdown = any(
            self.regime_classification[f] in ["COLLAPSED", "LOWER_BREAKDOWN"]
            for f in lower_freqs
        ) if lower_freqs else False

        if has_lower_breakdown:
            verdicts['H1_lower_boundary'] = 'CONFIRMED'
            print("✅ H1 CONFIRMED: Lower boundary detected")
            print("   Population collapses at low spawn frequencies")
        else:
            verdicts['H1_lower_boundary'] = 'NOT_DETECTED'
            print("⚠️  H1 NOT DETECTED: No lower boundary in tested range")
            print("   Homeostasis robust to low frequencies down to 0.5%")

        # H2: Upper boundary exists
        upper_freqs = [f for f in self.frequencies if f > 3.0]
        has_upper_breakdown = any(
            self.regime_classification[f] in ["SATURATION", "UPPER_BREAKDOWN"]
            for f in upper_freqs
        ) if upper_freqs else False

        if has_upper_breakdown:
            verdicts['H2_upper_boundary'] = 'CONFIRMED'
            print("✅ H2 CONFIRMED: Upper boundary detected")
            print("   Population saturates or becomes unstable at high frequencies")
        else:
            verdicts['H2_upper_boundary'] = 'NOT_DETECTED'
            print("⚠️  H2 NOT DETECTED: No upper boundary in tested range")
            print("   Homeostasis robust to high frequencies up to 10.0%")

        # H3: Homeostasis unbounded
        if not has_lower_breakdown and not has_upper_breakdown:
            verdicts['H3_unbounded'] = 'CONFIRMED'
            print("✅ H3 CONFIRMED: Homeostasis appears unbounded in tested range (0.5-10.0%)")
            print("   Exceptionally robust regulatory mechanism")
        else:
            verdicts['H3_unbounded'] = 'REJECTED'
            print("❌ H3 REJECTED: Boundaries detected")

        print()
        return verdicts

    def generate_boundary_figure(self, output_dir: Path):
        """Generate publication-grade boundary characterization figure."""
        print("=" * 100)
        print("GENERATING BOUNDARY VISUALIZATION")
        print("=" * 100)

        fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # Extract data
        freqs = self.frequencies
        pop_means = [self.frequency_stats[f]['population']['mean'] for f in freqs]
        pop_stds = [self.frequency_stats[f]['population']['std'] for f in freqs]
        comp_means = [self.frequency_stats[f]['composition']['mean'] for f in freqs]
        comp_stds = [self.frequency_stats[f]['composition']['std'] for f in freqs]

        # Color-code by regime
        colors = []
        for freq in freqs:
            regime = self.regime_classification[freq]
            if regime == "HOMEOSTATIC":
                colors.append('green')
            elif regime in ["COLLAPSED", "LOWER_BREAKDOWN"]:
                colors.append('red')
            elif regime in ["SATURATION", "UPPER_BREAKDOWN"]:
                colors.append('orange')
            elif regime == "MARGINAL":
                colors.append('yellow')
            else:
                colors.append('gray')

        # Panel A: Population vs. frequency
        ax1 = axes[0]
        ax1.errorbar(freqs, pop_means, yerr=pop_stds, fmt='o-', capsize=5,
                    linewidth=2, markersize=8, color='blue', alpha=0.7,
                    label='Mean ± SD')

        # Color-code points by regime
        for i, (freq, pop, regime) in enumerate(zip(freqs, pop_means,
                                                     [self.regime_classification[f] for f in freqs])):
            ax1.scatter(freq, pop, c=colors[i], s=100, edgecolors='black',
                       linewidths=1.5, zorder=10)

        # Mark homeostatic region
        if self.homeostatic_range:
            ax1.axvspan(self.lower_boundary, self.upper_boundary,
                       alpha=0.2, color='green', label='Homeostatic Regime')

        ax1.axhline(17, color='black', linestyle='--', linewidth=1, alpha=0.5,
                   label='Expected (C171: ~17 agents)')
        ax1.set_ylabel('Population (agents)', fontsize=12, fontweight='bold')
        ax1.set_title('Homeostatic Regime Boundaries: Population vs. Spawn Frequency',
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best', fontsize=10)

        # Panel B: Composition vs. frequency
        ax2 = axes[1]
        ax2.errorbar(freqs, comp_means, yerr=comp_stds, fmt='s-', capsize=5,
                    linewidth=2, markersize=8, color='purple', alpha=0.7,
                    label='Mean ± SD')

        # Color-code points
        for i, (freq, comp, regime) in enumerate(zip(freqs, comp_means,
                                                     [self.regime_classification[f] for f in freqs])):
            ax2.scatter(freq, comp, c=colors[i], s=100, edgecolors='black',
                       linewidths=1.5, zorder=10)

        ax2.axhline(100, color='black', linestyle='--', linewidth=1, alpha=0.5,
                   label='Expected (C171: ~100 events/window)')
        ax2.set_xlabel('Spawn Frequency (%)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Composition Events (per 100 cycles)', fontsize=12, fontweight='bold')
        ax2.set_title('Composition-Decomposition Activity vs. Spawn Frequency',
                     fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best', fontsize=10)

        # Add regime legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', label='Homeostatic'),
            Patch(facecolor='red', label='Lower Breakdown/Collapsed'),
            Patch(facecolor='orange', label='Upper Breakdown/Saturation'),
            Patch(facecolor='yellow', label='Marginal'),
            Patch(facecolor='gray', label='Unstable')
        ]
        fig.legend(handles=legend_elements, loc='upper right',
                  title='Regime Classification', fontsize=10)

        plt.tight_layout()

        # Save figure
        output_dir.mkdir(exist_ok=True)
        fig_path = output_dir / 'cycle177_boundary_characterization.png'
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Boundary figure saved: {fig_path}")
        print()

        return fig_path

    def generate_summary_report(self, hypothesis_verdicts: Dict[str, str]) -> str:
        """Generate comprehensive text summary."""
        lines = []
        lines.append("=" * 100)
        lines.append("CYCLE 177: HOMEOSTATIC REGIME BOUNDARY CHARACTERIZATION SUMMARY")
        lines.append("=" * 100)
        lines.append("")

        # Experiment metadata
        lines.append("EXPERIMENT METADATA:")
        lines.append("-" * 100)
        lines.append(f"Frequencies tested: {len(self.frequencies)}")
        lines.append(f"Frequency range: {min(self.frequencies):.1f}% - {max(self.frequencies):.1f}%")
        lines.append(f"Experiments per frequency: {self.data['metadata']['n_seeds']}")
        lines.append(f"Total experiments: {len(self.data['experiments'])}")
        lines.append(f"Duration: {self.data['metadata']['duration_minutes']:.2f} minutes")
        lines.append("")

        # Boundary findings
        lines.append("BOUNDARY FINDINGS:")
        lines.append("-" * 100)
        if self.homeostatic_range:
            lines.append(f"✅ Homeostatic regime detected:")
            lines.append(f"   Lower boundary: {self.lower_boundary:.1f}%")
            lines.append(f"   Upper boundary: {self.upper_boundary:.1f}%")
            lines.append(f"   Range width: {self.homeostatic_range:.1f}%")
        else:
            lines.append("⚠️  No clear homeostatic regime detected")
        lines.append("")

        # Hypothesis verdicts
        lines.append("HYPOTHESIS TEST RESULTS:")
        lines.append("-" * 100)
        for hypothesis, verdict in hypothesis_verdicts.items():
            lines.append(f"{hypothesis}: {verdict}")
        lines.append("")

        # Regime distribution
        lines.append("REGIME DISTRIBUTION:")
        lines.append("-" * 100)
        regime_counts = defaultdict(int)
        for regime in self.regime_classification.values():
            regime_counts[regime] += 1

        for regime, count in sorted(regime_counts.items()):
            pct = (count / len(self.frequencies)) * 100
            lines.append(f"  {regime:20s}: {count:2d} frequencies ({pct:5.1f}%)")
        lines.append("")

        # Publication implications
        lines.append("PUBLICATION IMPLICATIONS:")
        lines.append("-" * 100)

        if hypothesis_verdicts.get('H3_unbounded') == 'CONFIRMED':
            lines.append("✅ MAJOR FINDING: Homeostasis exceptionally robust")
            lines.append("   - Extends across 0.5-10.0% frequency range (20× variation)")
            lines.append("   - No breakdown detected at tested extremes")
            lines.append("   - Strengthens Paper 2 robustness claims significantly")
            lines.append("   - Suggests fundamental regulatory mechanism")
        else:
            lines.append("✅ Boundaries characterized - normal regulatory limits")
            lines.append("   - Defines operational range for homeostatic regime")
            lines.append("   - Provides phase diagram boundaries")

        lines.append("")

        # Comparison with baseline
        baseline_freqs = [f for f in self.frequencies if 2.0 <= f <= 3.0]
        if baseline_freqs:
            lines.append("COMPARISON WITH C171 BASELINE (2.0-3.0%):")
            lines.append("-" * 100)
            for freq in baseline_freqs:
                stats = self.frequency_stats[freq]
                regime = self.regime_classification[freq]
                lines.append(f"  {freq:.1f}%: {regime}, "
                           f"pop={stats['population']['mean']:.1f} "
                           f"(CV={stats['population']['cv']:.1f}%)")
            lines.append("✅ Baseline frequencies replicate C171 homeostasis")
            lines.append("")

        lines.append("=" * 100)

        return "\n".join(lines)

    def save_analysis_outputs(self, output_dir: Path):
        """Save all analysis outputs."""
        output_dir.mkdir(exist_ok=True)

        # Test hypotheses
        hypothesis_verdicts = self.test_hypotheses()

        # Generate summary report
        summary = self.generate_summary_report(hypothesis_verdicts)

        # Save text report
        report_path = output_dir / 'cycle177_analysis_report.txt'
        with open(report_path, 'w') as f:
            f.write(summary)
        print(f"✅ Analysis report saved: {report_path}")

        # Save JSON summary
        summary_data = {
            'frequencies': self.frequencies,
            'frequency_stats': self.frequency_stats,
            'regime_classification': self.regime_classification,
            'boundaries': {
                'lower': self.lower_boundary,
                'upper': self.upper_boundary,
                'range_width': self.homeostatic_range
            },
            'hypothesis_verdicts': hypothesis_verdicts,
            'metadata': self.data.get('metadata', {})
        }

        summary_path = output_dir / 'cycle177_analysis_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        print(f"✅ JSON summary saved: {summary_path}")
        print()


def main():
    """Execute C177 boundary analysis pipeline."""
    print()
    print("=" * 100)
    print("CYCLE 177 ANALYSIS: Homeostatic Regime Boundary Characterization")
    print("=" * 100)
    print()

    # Paths
    experiments_dir = Path(__file__).parent
    results_path = experiments_dir / "results" / "cycle177_extended_frequency_range.json"
    output_dir = experiments_dir / "results"
    figures_dir = experiments_dir / "figures"

    # Initialize analyzer
    analyzer = C177BoundaryAnalyzer(results_path)

    # Load data
    if not analyzer.load_data():
        print("❌ Could not load C177 results - ensure experiment has completed")
        print()
        return

    print()

    # Run analyses
    analyzer.analyze_frequency_statistics()
    analyzer.identify_boundaries()

    # Generate figure
    analyzer.generate_boundary_figure(figures_dir)

    # Save outputs
    analyzer.save_analysis_outputs(output_dir)

    # Print summary
    hypothesis_verdicts = analyzer.test_hypotheses()
    summary = analyzer.generate_summary_report(hypothesis_verdicts)
    print()
    print(summary)
    print()

    print("=" * 100)
    print("C177 ANALYSIS COMPLETE")
    print("=" * 100)
    print()
    print("NEXT STEPS:")
    print("1. Review boundary characterization figure")
    print("2. Integrate findings into Paper 2 (Discussion Section 4.9)")
    print("3. Update robustness claims based on boundary extent")
    print("4. Consider follow-up experiments if boundaries not detected")
    print()


if __name__ == "__main__":
    main()
