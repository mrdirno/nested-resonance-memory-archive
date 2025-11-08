#!/usr/bin/env python3
"""
C187 Network Structure Effects Analysis Pipeline

Analyzes experimental results from C187 testing network topology effects on
energy-regulated composition dynamics. Tests pre-registered hypotheses H2.1-H2.3
regarding hub depletion, spawn success ranking, and degree-weighted selection.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-08 (Cycle 1287+)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Experimental Design:
- 3 topologies: scale-free, random, lattice (2D grid)
- 10 seeds per topology
- f_spawn = 2.0% (baseline)
- Duration = 2000 cycles
- N_max = 50 agents

Pre-Registered Hypotheses:
- H2.1: Hub depletion observable (negative correlation: degree vs. final energy)
- H2.2: Spawn success ranking: Lattice > Random > Scale-Free
- H2.3: Degree-weighted selection causes hub vulnerability

Zero-Delay Infrastructure: Analysis pipeline created BEFORE experiments run,
enabling instant analysis upon completion (Paper 4 methodological contribution).

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib as mpl

# Publication-quality figure settings
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.size'] = 10
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['axes.labelsize'] = 11
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['xtick.labelsize'] = 9
mpl.rcParams['ytick.labelsize'] = 9
mpl.rcParams['legend.fontsize'] = 9


class C187NetworkAnalyzer:
    """
    Analyzes C187 network structure experimental results.
    Tests hypotheses about hub depletion and topology effects.
    """

    def __init__(self, results_dir: str, output_dir: str):
        """
        Initialize analyzer.

        Args:
            results_dir: Directory containing C187 result JSON files
            output_dir: Directory for analysis outputs and figures
        """
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.topologies = ['scale-free', 'random', 'lattice']
        self.n_seeds = 10

        # Results storage
        self.data = {topo: [] for topo in self.topologies}
        self.summary = {}
        self.hypotheses = {}

    def load_data(self) -> None:
        """Load all C187 experimental result files."""
        print("Loading C187 experimental data...")

        for topo in self.topologies:
            for seed in range(self.n_seeds):
                pattern = f"c187_{topo}_seed{seed:02d}.json"
                filepath = self.results_dir / pattern

                if not filepath.exists():
                    print(f"  WARNING: Missing {pattern}")
                    continue

                with open(filepath, 'r') as f:
                    result = json.load(f)
                    self.data[topo].append(result)

        # Verify data completeness
        for topo in self.topologies:
            n_loaded = len(self.data[topo])
            print(f"  {topo}: {n_loaded}/{self.n_seeds} runs loaded")

            if n_loaded < self.n_seeds:
                print(f"    WARNING: Incomplete data for {topo}")

    def test_h21_hub_depletion(self) -> Dict:
        """
        Test H2.1: Hub depletion observable (negative correlation: degree vs. final energy).

        Returns:
            Dict with correlation statistics per topology
        """
        print("\n=== Testing H2.1: Hub Depletion ===")

        results = {}

        for topo in self.topologies:
            if not self.data[topo]:
                continue

            correlations = []

            for run in self.data[topo]:
                # Extract degree and final energy for each agent
                degrees = []
                energies = []

                if 'final_network_state' in run and 'agent_states' in run:
                    network = run['final_network_state']
                    agents = run['agent_states']

                    for agent_id in agents:
                        if agent_id in network:
                            degree = len(network[agent_id])  # Number of connections
                            energy = agents[agent_id].get('energy', 0)
                            degrees.append(degree)
                            energies.append(energy)

                if len(degrees) > 2:  # Need at least 3 points for correlation
                    r, p = stats.pearsonr(degrees, energies)
                    correlations.append({'r': r, 'p': p, 'n': len(degrees)})

            if correlations:
                r_values = [c['r'] for c in correlations]
                p_values = [c['p'] for c in correlations]

                results[topo] = {
                    'mean_r': np.mean(r_values),
                    'std_r': np.std(r_values),
                    'median_r': np.median(r_values),
                    'mean_p': np.mean(p_values),
                    'n_significant': sum(1 for p in p_values if p < 0.05),
                    'n_negative': sum(1 for r in r_values if r < 0),
                    'n_runs': len(correlations)
                }

                print(f"\n{topo}:")
                print(f"  Mean correlation: r = {results[topo]['mean_r']:.3f} ± {results[topo]['std_r']:.3f}")
                print(f"  Negative correlations: {results[topo]['n_negative']}/{results[topo]['n_runs']}")
                print(f"  Significant (p<0.05): {results[topo]['n_significant']}/{results[topo]['n_runs']}")

        # H2.1 passes if scale-free shows consistent negative correlation
        h21_pass = False
        if 'scale-free' in results:
            sf = results['scale-free']
            # Criterion: Mean r < -0.3 AND majority negative
            h21_pass = (sf['mean_r'] < -0.3 and sf['n_negative'] >= 0.7 * sf['n_runs'])

        print(f"\nH2.1 Hub Depletion: {'PASS ✓' if h21_pass else 'FAIL ✗'}")
        print(f"  Criterion: Mean r < -0.3 AND ≥70% runs negative")

        self.hypotheses['H2.1'] = {
            'passed': h21_pass,
            'points': 2 if h21_pass else 0,
            'data': results
        }

        return results

    def test_h22_spawn_success_ranking(self) -> Dict:
        """
        Test H2.2: Spawn success ranking (Lattice > Random > Scale-Free).

        Returns:
            Dict with spawn success statistics per topology
        """
        print("\n=== Testing H2.2: Spawn Success Ranking ===")

        results = {}

        for topo in self.topologies:
            if not self.data[topo]:
                continue

            spawn_counts = []

            for run in self.data[topo]:
                if 'metrics' in run and 'total_compositions' in run['metrics']:
                    spawn_counts.append(run['metrics']['total_compositions'])

            if spawn_counts:
                results[topo] = {
                    'mean': np.mean(spawn_counts),
                    'std': np.std(spawn_counts),
                    'median': np.median(spawn_counts),
                    'n': len(spawn_counts),
                    'values': spawn_counts
                }

                print(f"\n{topo}:")
                print(f"  Mean spawns: {results[topo]['mean']:.1f} ± {results[topo]['std']:.1f}")
                print(f"  Median spawns: {results[topo]['median']:.1f}")

        # Statistical ranking test
        h22_pass = False

        if all(topo in results for topo in self.topologies):
            lattice_mean = results['lattice']['mean']
            random_mean = results['random']['mean']
            sf_mean = results['scale-free']['mean']

            # Test ordering: Lattice > Random > Scale-Free
            ordering_correct = (lattice_mean > random_mean > sf_mean)

            # Statistical significance (t-tests)
            t_lat_rand, p_lat_rand = stats.ttest_ind(
                results['lattice']['values'],
                results['random']['values']
            )
            t_rand_sf, p_rand_sf = stats.ttest_ind(
                results['random']['values'],
                results['scale-free']['values']
            )

            both_significant = (p_lat_rand < 0.05 and p_rand_sf < 0.05)

            h22_pass = (ordering_correct and both_significant)

            print(f"\nRanking: Lattice ({lattice_mean:.1f}) > Random ({random_mean:.1f}) > SF ({sf_mean:.1f})")
            print(f"  Lattice vs Random: t={t_lat_rand:.2f}, p={p_lat_rand:.4f}")
            print(f"  Random vs Scale-Free: t={t_rand_sf:.2f}, p={p_rand_sf:.4f}")

        print(f"\nH2.2 Spawn Success Ranking: {'PASS ✓' if h22_pass else 'FAIL ✗'}")
        print(f"  Criterion: Lattice > Random > SF (both comparisons p<0.05)")

        self.hypotheses['H2.2'] = {
            'passed': h22_pass,
            'points': 2 if h22_pass else 0,
            'data': results
        }

        return results

    def test_h23_degree_weighted_selection(self) -> Dict:
        """
        Test H2.3: Degree-weighted selection causes hub vulnerability.

        Analyzes whether high-degree nodes are selected more frequently
        and experience greater energy depletion.

        Returns:
            Dict with selection frequency statistics
        """
        print("\n=== Testing H2.3: Degree-Weighted Selection ===")

        results = {}

        for topo in self.topologies:
            if not self.data[topo]:
                continue

            selection_ratios = []  # High-degree selection frequency / low-degree

            for run in self.data[topo]:
                if 'selection_history' in run and 'final_network_state' in run:
                    history = run['selection_history']
                    network = run['final_network_state']

                    # Calculate degree for each agent
                    degrees = {aid: len(neighbors) for aid, neighbors in network.items()}

                    if not degrees:
                        continue

                    # Split into high/low degree (median split)
                    median_degree = np.median(list(degrees.values()))

                    # Count selections
                    high_degree_selections = sum(
                        1 for aid in history if degrees.get(aid, 0) >= median_degree
                    )
                    low_degree_selections = sum(
                        1 for aid in history if degrees.get(aid, 0) < median_degree
                    )

                    if low_degree_selections > 0:
                        ratio = high_degree_selections / low_degree_selections
                        selection_ratios.append(ratio)

            if selection_ratios:
                results[topo] = {
                    'mean_ratio': np.mean(selection_ratios),
                    'std_ratio': np.std(selection_ratios),
                    'n': len(selection_ratios)
                }

                print(f"\n{topo}:")
                print(f"  Mean selection ratio (high/low degree): {results[topo]['mean_ratio']:.2f} ± {results[topo]['std_ratio']:.2f}")

        # H2.3 passes if scale-free shows significantly higher selection ratio (>1.5)
        h23_pass = False
        if 'scale-free' in results:
            sf_ratio = results['scale-free']['mean_ratio']
            # Criterion: High-degree selected 50%+ more often than low-degree
            h23_pass = (sf_ratio > 1.5)

        print(f"\nH2.3 Degree-Weighted Selection: {'PASS ✓' if h23_pass else 'FAIL ✗'}")
        print(f"  Criterion: High-degree selection ratio > 1.5 in scale-free")

        self.hypotheses['H2.3'] = {
            'passed': h23_pass,
            'points': 2 if h23_pass else 0,
            'data': results
        }

        return results

    def generate_figures(self) -> None:
        """Generate publication-quality figures for C187 analysis."""
        print("\n=== Generating Figures ===")

        # Figure 1: Hub depletion scatter plots
        self._plot_hub_depletion()

        # Figure 2: Spawn success by topology
        self._plot_spawn_success()

        # Figure 3: Selection frequency by degree
        self._plot_selection_frequency()

        print(f"\nFigures saved to: {self.output_dir}/")

    def _plot_hub_depletion(self) -> None:
        """Plot degree vs. final energy for each topology."""
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        for idx, topo in enumerate(self.topologies):
            ax = axes[idx]

            if not self.data[topo]:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center')
                ax.set_title(topo.capitalize())
                continue

            # Aggregate all runs
            all_degrees = []
            all_energies = []

            for run in self.data[topo]:
                if 'final_network_state' in run and 'agent_states' in run:
                    network = run['final_network_state']
                    agents = run['agent_states']

                    for agent_id in agents:
                        if agent_id in network:
                            degree = len(network[agent_id])
                            energy = agents[agent_id].get('energy', 0)
                            all_degrees.append(degree)
                            all_energies.append(energy)

            if all_degrees:
                ax.scatter(all_degrees, all_energies, alpha=0.3, s=20)

                # Fit line
                if len(all_degrees) > 2:
                    r, p = stats.pearsonr(all_degrees, all_energies)
                    z = np.polyfit(all_degrees, all_energies, 1)
                    p_fit = np.poly1d(z)
                    x_fit = np.linspace(min(all_degrees), max(all_degrees), 100)
                    ax.plot(x_fit, p_fit(x_fit), 'r-', alpha=0.7, linewidth=2,
                           label=f'r = {r:.3f}, p = {p:.3f}')

                ax.set_xlabel('Degree (number of connections)')
                ax.set_ylabel('Final Energy')
                ax.set_title(topo.capitalize())
                ax.legend()
                ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c187_hub_depletion.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c187_hub_depletion.png")

    def _plot_spawn_success(self) -> None:
        """Plot spawn success comparison across topologies."""
        fig, ax = plt.subplots(figsize=(8, 6))

        positions = []
        spawn_data = []
        labels = []

        for idx, topo in enumerate(self.topologies):
            if topo in self.hypotheses.get('H2.2', {}).get('data', {}):
                values = self.hypotheses['H2.2']['data'][topo]['values']
                positions.append(idx)
                spawn_data.append(values)
                labels.append(topo.capitalize())

        if spawn_data:
            bp = ax.boxplot(spawn_data, positions=positions, labels=labels,
                           patch_artist=True, widths=0.6)

            # Color by expected ranking
            colors = ['#2ecc71', '#f39c12', '#e74c3c']  # Green, Orange, Red
            for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)

            ax.set_xlabel('Network Topology')
            ax.set_ylabel('Total Compositions')
            ax.set_title('Spawn Success by Topology (H2.2)')
            ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c187_spawn_success.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c187_spawn_success.png")

    def _plot_selection_frequency(self) -> None:
        """Plot selection frequency ratio (high-degree / low-degree)."""
        fig, ax = plt.subplots(figsize=(8, 6))

        if 'H2.3' in self.hypotheses and 'data' in self.hypotheses['H2.3']:
            data = self.hypotheses['H2.3']['data']

            topos = []
            ratios = []
            errors = []

            for topo in self.topologies:
                if topo in data:
                    topos.append(topo.capitalize())
                    ratios.append(data[topo]['mean_ratio'])
                    errors.append(data[topo]['std_ratio'])

            if topos:
                x = np.arange(len(topos))
                bars = ax.bar(x, ratios, yerr=errors, capsize=5, alpha=0.7,
                             color=['#e74c3c', '#f39c12', '#2ecc71'])

                # Threshold line at 1.5
                ax.axhline(y=1.5, color='red', linestyle='--', linewidth=2,
                          label='H2.3 threshold (1.5)')

                # Neutral line at 1.0
                ax.axhline(y=1.0, color='gray', linestyle=':', linewidth=1,
                          label='Equal selection (1.0)')

                ax.set_xlabel('Network Topology')
                ax.set_ylabel('Selection Ratio (High-Degree / Low-Degree)')
                ax.set_title('Degree-Weighted Selection Effect (H2.3)')
                ax.set_xticks(x)
                ax.set_xticklabels(topos)
                ax.legend()
                ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'figure_c187_selection_frequency.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("  Created: figure_c187_selection_frequency.png")

    def calculate_composite_scorecard(self) -> Dict:
        """
        Calculate composite scorecard contribution from C187 analysis.

        Returns:
            Dict with scorecard summary
        """
        print("\n=== Composite Scorecard (C187 Contribution) ===")

        total_points = 0
        max_points = 6  # H2.1 (2) + H2.2 (2) + H2.3 (2)

        for hyp_id in ['H2.1', 'H2.2', 'H2.3']:
            if hyp_id in self.hypotheses:
                points = self.hypotheses[hyp_id]['points']
                passed = self.hypotheses[hyp_id]['passed']
                total_points += points

                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {hyp_id}: {points}/2 points {status}")

        print(f"\nC187 Total: {total_points}/{max_points} points ({100*total_points/max_points:.0f}%)")

        scorecard = {
            'total_points': total_points,
            'max_points': max_points,
            'percentage': 100 * total_points / max_points,
            'hypotheses': self.hypotheses
        }

        return scorecard

    def save_results(self) -> None:
        """Save analysis results to JSON."""
        output_file = self.output_dir / 'c187_analysis_results.json'

        results = {
            'experiment': 'C187_Network_Structure_Effects',
            'date_analyzed': '2025-11-08',
            'hypotheses': self.hypotheses,
            'composite_scorecard': self.calculate_composite_scorecard()
        }

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def run_full_analysis(self) -> None:
        """Execute complete C187 analysis pipeline."""
        print("="*60)
        print("C187 NETWORK STRUCTURE EFFECTS ANALYSIS")
        print("="*60)

        self.load_data()
        self.test_h21_hub_depletion()
        self.test_h22_spawn_success_ranking()
        self.test_h23_degree_weighted_selection()
        self.generate_figures()
        self.calculate_composite_scorecard()
        self.save_results()

        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)


def main():
    """Main entry point for C187 analysis."""
    # Default paths
    results_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4/c187"

    # Allow command-line overrides
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    # Run analysis
    analyzer = C187NetworkAnalyzer(results_dir, output_dir)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
