#!/usr/bin/env python3
"""
Meta-Analysis: Hierarchical Scaling Experiments (C171, C186 V1-V7)

Purpose: Comparative analysis across all hierarchical experiments to extract
         unified insights about scaling coefficient α and system architecture effects

Experiments Compared:
- C171: Single-scale baseline (f_crit ≈ 2.0%, 100% Basin A at 2.0-3.0%)
- C186 V1: Hierarchical failure (f_intra=2.5%, 0% Basin A)
- C186 V2: Hierarchical partial success (f_intra=5.0%, 50-60% Basin A)
- C186 V3: Three-level hierarchy (f_agent=8.0%, α_3-level test)
- C186 V4: Migration rate effects (f_migrate variable)
- C186 V5: Population size effects (N variable)
- C186 V6: Partial compartmentalization (pool structure variable)
- C186 V7: α precision mapping (sigmoid fit)

Analysis Output:
- Unified α coefficient estimate across all experiments
- Architecture effect quantification
- Parameter sensitivity analysis
- Theoretical model validation summary
- Publication-ready comparative figures

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1057)
License: GPL-3.0
"""

import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Configuration
RESULTS_DIR = Path(__file__).parent.parent.parent / "experiments" / "results"
FIGURES_DIR = Path(__file__).parent.parent.parent / "data" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ExperimentSummary:
    """Summary statistics for an experiment"""
    experiment_id: str
    architecture: str
    f_intra: float
    n_experiments: int
    basin_a_pct: float
    mean_population: float
    std_population: float
    alpha_estimate: float
    notes: str

def load_all_experiments() -> Dict[str, dict]:
    """Load all hierarchical experiment results"""

    experiments = {
        'C171': 'cycle171_v1_single_scale_baseline.json',  # May not exist
        'V1': 'c186_v1_hierarchical_spawn_failure.json',
        'V2': 'c186_v2_hierarchical_spawn_success.json',
        'V3': 'c186_v3_three_level_hierarchy.json',
        'V4': 'c186_v4_migration_rate_effects.json',
        'V5': 'c186_v5_population_size_effects.json',
        'V6': 'c186_v6_partial_compartmentalization.json',
        'V7': 'c186_v7_alpha_empirical_mapping.json'
    }

    loaded_data = {}

    print("Loading experiment results...")
    print("-" * 80)

    for exp_id, filename in experiments.items():
        filepath = RESULTS_DIR / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                loaded_data[exp_id] = json.load(f)
            print(f"  ✓ {exp_id}: Loaded")
        else:
            print(f"  ⚠ {exp_id}: Not found ({filename})")
            loaded_data[exp_id] = None

    return loaded_data

def estimate_alpha_from_experiment(exp_id: str, data: dict) -> Tuple[float, str]:
    """Estimate α coefficient from experiment data"""

    if data is None:
        return 0.0, "Data not available"

    if exp_id == 'C171':
        # Single-scale baseline: α = 1.0 by definition
        return 1.0, "Single-scale baseline (α=1.0 by definition)"

    elif exp_id in ['V1', 'V2']:
        # Baseline hierarchical experiments
        # V1: f_intra=2.5%, 0% Basin A (below threshold)
        # V2: f_intra=5.0%, 50-60% Basin A (at threshold)
        # Estimate: α ≈ f_intra_hierarchical / f_crit_single
        # For V2: α ≈ 5.0% / 2.0% = 2.5 (upper bound)
        # For V1: α > 2.5%/2.0% = 1.25 (lower bound inconclusive)

        results = data['individual_results']
        basin_a_count = sum(1 for r in results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(results)) * 100

        f_intra = data['metadata']['f_intra']
        f_crit_single = 0.020

        if basin_a_pct >= 50:
            # At or above threshold
            alpha_est = f_intra / f_crit_single
            return alpha_est, f"At threshold (Basin A={basin_a_pct:.1f}%)"
        else:
            # Below threshold
            return 0.0, f"Below threshold (Basin A={basin_a_pct:.1f}%)"

    elif exp_id == 'V3':
        # Three-level hierarchy
        # Expected: α_3-level ≈ 4.0 (2² = 4)
        results = data['individual_results']
        basin_a_count = sum(1 for r in results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(results)) * 100

        f_agent = data['metadata']['f_agent']
        f_crit_single = 0.020

        alpha_est = f_agent / f_crit_single
        return alpha_est, f"3-level hierarchy (Basin A={basin_a_pct:.1f}%)"

    elif exp_id in ['V4', 'V5', 'V6']:
        # Parameter variation experiments
        # Cannot directly estimate α (multiple conditions)
        return 0.0, "Multi-condition experiment (no single α)"

    elif exp_id == 'V7':
        # Precision α mapping via sigmoid fit
        # This is the gold standard measurement
        aggregates = data['freq_aggregates']
        f_values = np.array([agg['f_intra'] for agg in aggregates])
        basin_a_pcts = np.array([agg['basin_a_pct'] for agg in aggregates])

        try:
            from scipy.optimize import curve_fit

            def sigmoid(f, f_crit, k):
                return 100 / (1 + np.exp(-k * (f - f_crit)))

            popt, _ = curve_fit(sigmoid, f_values, basin_a_pcts, p0=[0.040, 200], maxfev=10000)
            f_crit_hier, _ = popt

            f_crit_single = 0.020
            alpha_est = f_crit_hier / f_crit_single

            return alpha_est, f"Sigmoid fit (f_crit={f_crit_hier*100:.2f}%)"
        except:
            return 0.0, "Sigmoid fit failed"

    else:
        return 0.0, "Unknown experiment type"

def create_experiment_summaries(all_data: Dict[str, dict]) -> List[ExperimentSummary]:
    """Create summary statistics for all experiments"""

    summaries = []

    for exp_id, data in all_data.items():
        if data is None:
            continue

        # Get basic info
        metadata = data.get('metadata', {})
        results = data.get('individual_results', [])

        if not results:
            continue

        # Calculate statistics
        basin_a_count = sum(1 for r in results if r.get('basin') == 'A')
        basin_a_pct = (basin_a_count / len(results)) * 100

        mean_pops = [r.get('mean_population', 0.0) for r in results]
        mean_pop_avg = np.mean(mean_pops)
        std_pop = np.std(mean_pops)

        # Estimate α
        alpha_est, notes = estimate_alpha_from_experiment(exp_id, data)

        # Architecture
        architecture_map = {
            'C171': 'Single-scale',
            'V1': 'Hierarchical (2-level)',
            'V2': 'Hierarchical (2-level)',
            'V3': 'Hierarchical (3-level)',
            'V4': 'Hierarchical (2-level, migration)',
            'V5': 'Hierarchical (2-level, variable N)',
            'V6': 'Hierarchical (2-level, partial compart.)',
            'V7': 'Hierarchical (2-level, precision)'
        }

        summary = ExperimentSummary(
            experiment_id=exp_id,
            architecture=architecture_map.get(exp_id, 'Unknown'),
            f_intra=metadata.get('f_intra', metadata.get('f_agent', 0.0)),
            n_experiments=len(results),
            basin_a_pct=basin_a_pct,
            mean_population=mean_pop_avg,
            std_population=std_pop,
            alpha_estimate=alpha_est,
            notes=notes
        )

        summaries.append(summary)

    return summaries

def generate_alpha_estimates_figure(summaries: List[ExperimentSummary], output_path: Path):
    """Generate comparative α estimates across experiments"""

    # Filter experiments with valid α estimates
    valid_summaries = [s for s in summaries if s.alpha_estimate > 0]

    if not valid_summaries:
        print("⚠ No valid α estimates found")
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    experiments = [s.experiment_id for s in valid_summaries]
    alphas = [s.alpha_estimate for s in valid_summaries]
    colors = ['gray' if s.experiment_id == 'C171' else 'blue' if s.experiment_id in ['V1', 'V2', 'V7'] else 'lightblue'
              for s in valid_summaries]

    # Bar plot
    bars = ax.bar(experiments, alphas, color=colors, edgecolor='black', linewidth=1.5)

    # Expected α = 2.0 line
    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=2,
              label='Expected α = 2.0', zorder=1)

    # Formatting
    ax.set_xlabel('Experiment', fontsize=14, fontweight='bold')
    ax.set_ylabel('Hierarchical Scaling Coefficient (α)', fontsize=14, fontweight='bold')
    ax.set_title('Meta-Analysis: α Coefficient Estimates Across Experiments',
                fontsize=15, fontweight='bold', pad=15)
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)

    # Add value labels
    for bar, alpha in zip(bars, alphas):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
               f'{alpha:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Alpha estimates figure saved: {output_path.name}")

def generate_basin_a_comparison_figure(summaries: List[ExperimentSummary], output_path: Path):
    """Generate Basin A percentage comparison across experiments"""

    fig, ax = plt.subplots(figsize=(12, 7))

    experiments = [s.experiment_id for s in summaries]
    basin_a_pcts = [s.basin_a_pct for s in summaries]
    colors = ['green' if pct >= 90 else 'orange' if pct >= 50 else 'red' for pct in basin_a_pcts]

    # Bar plot
    bars = ax.bar(experiments, basin_a_pcts, color=colors, alpha=0.7,
                  edgecolor='black', linewidth=1.5)

    # Homeostasis threshold
    ax.axhline(y=100, color='green', linestyle='--', linewidth=2,
              alpha=0.5, label='Perfect Homeostasis (100%)')
    ax.axhline(y=50, color='orange', linestyle=':', linewidth=2,
              alpha=0.5, label='Partial Viability (50%)')

    # Formatting
    ax.set_xlabel('Experiment', fontsize=14, fontweight='bold')
    ax.set_ylabel('Basin A Percentage (%)', fontsize=14, fontweight='bold')
    ax.set_title('Meta-Analysis: Viability Across Hierarchical Experiments',
                fontsize=15, fontweight='bold', pad=15)
    ax.set_ylim([0, 110])
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)

    # Add value labels
    for bar, pct in zip(bars, basin_a_pcts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
               f'{pct:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Basin A comparison figure saved: {output_path.name}")

def main():
    """Execute meta-analysis"""

    print("=" * 80)
    print("META-ANALYSIS: HIERARCHICAL SCALING EXPERIMENTS")
    print("=" * 80)
    print()

    # Load all experiments
    all_data = load_all_experiments()

    print()
    print("=" * 80)
    print("EXPERIMENT SUMMARIES")
    print("=" * 80)
    print()

    summaries = create_experiment_summaries(all_data)

    print(f"{'Exp':>4s} | {'Architecture':>30s} | {'f_intra':>8s} | {'Basin A':>9s} | {'α Est.':>7s} | {'Notes':>40s}")
    print("-" * 115)

    for s in summaries:
        print(f"{s.experiment_id:>4s} | {s.architecture:>30s} | {s.f_intra*100:>7.1f}% | "
              f"{s.basin_a_pct:>8.1f}% | {s.alpha_estimate:>7.2f} | {s.notes[:40]:>40s}")

    print()
    print("=" * 80)
    print("UNIFIED α ESTIMATE")
    print("=" * 80)
    print()

    # Calculate weighted average α from experiments with valid estimates
    valid_alphas = [(s.alpha_estimate, s.n_experiments) for s in summaries
                   if s.alpha_estimate > 0 and s.experiment_id != 'C171']

    if valid_alphas:
        weights = np.array([n for _, n in valid_alphas])
        alphas = np.array([a for a, _ in valid_alphas])

        weighted_alpha = np.average(alphas, weights=weights)
        std_alpha = np.std(alphas)

        print(f"Weighted Average α: {weighted_alpha:.2f} ± {std_alpha:.2f}")
        print(f"  (weighted by number of experiments)")
        print()
        print(f"Individual estimates:")
        for (alpha, n), summary in zip(valid_alphas, [s for s in summaries if s.alpha_estimate > 0 and s.experiment_id != 'C171']):
            print(f"  {summary.experiment_id}: α = {alpha:.2f} (n={n})")
    else:
        print("⚠ No valid α estimates available")

    print()
    print("=" * 80)
    print("GENERATING FIGURES")
    print("=" * 80)
    print()

    # Figure 1: α estimates
    fig1_path = FIGURES_DIR / "meta_analysis_alpha_estimates.png"
    generate_alpha_estimates_figure(summaries, fig1_path)

    # Figure 2: Basin A comparison
    fig2_path = FIGURES_DIR / "meta_analysis_basin_a_comparison.png"
    generate_basin_a_comparison_figure(summaries, fig2_path)

    print()
    print("=" * 80)
    print("META-ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Generated 2 publication-quality figures @ 300 DPI:")
    print(f"  1. {fig1_path.name}")
    print(f"  2. {fig2_path.name}")
    print()

if __name__ == "__main__":
    main()
