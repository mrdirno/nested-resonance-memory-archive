#!/usr/bin/env python3
"""
Regime Classification Visualization

Creates publication-quality figures for Gate 1.2 regime detection analysis
showing condition-regime relationships and mechanistic insights.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
Cycle: 871
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from typing import Dict, List


# Publication-quality style settings
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13


# Color scheme for regimes (colorblind-friendly)
REGIME_COLORS = {
    'collapse': '#D55E00',      # Orange-red
    'accumulation': '#0072B2',  # Blue
    'bistability': '#009E73',   # Green
    'unknown': '#999999'         # Gray
}


def load_analysis_results(results_path: Path) -> Dict:
    """Load regime classification analysis results."""
    with open(results_path) as f:
        return json.load(f)


def plot_regime_distribution(results: Dict, output_path: Path):
    """
    Create bar chart of overall regime distribution.

    Args:
        results: Analysis results dictionary
        output_path: Path to save figure
    """
    regime_counts = results['regime_counts']
    total = results['total_experiments']

    # Sort by count (descending)
    sorted_regimes = sorted(regime_counts.items(), key=lambda x: x[1], reverse=True)
    regimes = [r[0] for r in sorted_regimes if r[1] > 0]
    counts = [r[1] for r in sorted_regimes if r[1] > 0]
    percentages = [(c / total) * 100 for c in counts]
    colors = [REGIME_COLORS.get(r, '#999999') for r in regimes]

    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(range(len(regimes)), counts, color=colors, edgecolor='black', linewidth=1.2)

    # Add count and percentage labels on bars
    for i, (bar, count, pct) in enumerate(zip(bars, counts, percentages)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{count}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xticks(range(len(regimes)))
    ax.set_xticklabels([r.capitalize() for r in regimes], rotation=0)
    ax.set_ylabel('Number of Experiments')
    ax.set_title(f'Regime Distribution (Cycle 176 Ablation Study)\nN={total}')
    ax.set_ylim(0, max(counts) * 1.2)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_path}")


def plot_condition_regime_heatmap(results: Dict, output_path: Path):
    """
    Create heatmap showing condition → regime mapping.

    Args:
        results: Analysis results dictionary
        output_path: Path to save figure
    """
    condition_regime_map = results['condition_regime_map']

    # Extract conditions and regimes
    conditions = list(condition_regime_map.keys())
    all_regimes = ['collapse', 'accumulation', 'bistability', 'unknown']
    regime_labels = [r.capitalize() for r in all_regimes]

    # Build count matrix
    matrix = np.zeros((len(conditions), len(all_regimes)))
    for i, cond in enumerate(conditions):
        for j, regime in enumerate(all_regimes):
            matrix[i, j] = condition_regime_map[cond].get(regime, 0)

    fig, ax = plt.subplots(figsize=(7, 5))

    # Create heatmap
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=10)

    # Set ticks and labels
    ax.set_xticks(range(len(all_regimes)))
    ax.set_yticks(range(len(conditions)))
    ax.set_xticklabels(regime_labels)
    ax.set_yticklabels(conditions)

    # Rotate condition labels for readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add text annotations
    for i in range(len(conditions)):
        for j in range(len(all_regimes)):
            count = int(matrix[i, j])
            if count > 0:
                text = ax.text(j, i, str(count),
                              ha="center", va="center", color="black",
                              fontsize=11, fontweight='bold')

    ax.set_title('Condition → Regime Mapping\n(Cycle 176: 6 Conditions × 10 Seeds)')
    ax.set_xlabel('Regime Classification')
    ax.set_ylabel('Ablation Condition')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Number of Experiments', rotation=270, labelpad=20)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_path}")


def plot_cv_by_condition(results: Dict, output_path: Path):
    """
    Create violin plot of CV distribution by condition.

    Args:
        results: Analysis results dictionary
        output_path: Path to save figure
    """
    classifications = results['classifications']

    # Group CV values by condition
    condition_cv_map = {}
    for cls in classifications:
        cond = cls['condition']
        cv = cls['cv_percent']
        if cond not in condition_cv_map:
            condition_cv_map[cond] = []
        condition_cv_map[cond].append(cv)

    conditions = list(condition_cv_map.keys())
    cv_data = [condition_cv_map[c] for c in conditions]

    fig, ax = plt.subplots(figsize=(8, 5))

    # Create violin plot
    parts = ax.violinplot(cv_data, positions=range(len(conditions)),
                          showmeans=True, showmedians=True)

    # Color by dominant regime
    condition_regime_map = results['condition_regime_map']
    for i, (cond, part) in enumerate(zip(conditions, parts['bodies'])):
        # Find dominant regime for this condition
        regimes = condition_regime_map[cond]
        dominant_regime = max(regimes.items(), key=lambda x: x[1])[0]
        color = REGIME_COLORS.get(dominant_regime, '#999999')
        part.set_facecolor(color)
        part.set_alpha(0.7)

    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions, rotation=45, ha='right')
    ax.set_ylabel('Coefficient of Variation (%)')
    ax.set_title('CV Distribution by Ablation Condition\n(Cycle 176)')

    # Add threshold lines
    ax.axhline(y=20, color='green', linestyle='--', linewidth=1.5, alpha=0.7,
              label='Bistability threshold (CV=20%)')
    ax.axhline(y=80, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
              label='Collapse threshold (CV=80%)')

    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_path}")


def plot_confidence_distribution(results: Dict, output_path: Path):
    """
    Create histogram of classification confidence scores.

    Args:
        results: Analysis results dictionary
        output_path: Path to save figure
    """
    classifications = results['classifications']

    # Group by regime
    regime_confidence_map = {'collapse': [], 'accumulation': [], 'bistability': [], 'unknown': []}
    for cls in classifications:
        regime = cls['regime']
        conf = cls['confidence']
        if regime in regime_confidence_map:
            regime_confidence_map[regime].append(conf)

    fig, ax = plt.subplots(figsize=(7, 4))

    # Plot histograms for each regime
    for regime, confidences in regime_confidence_map.items():
        if len(confidences) > 0:
            color = REGIME_COLORS.get(regime, '#999999')
            ax.hist(confidences, bins=20, alpha=0.6, label=f'{regime.capitalize()} (n={len(confidences)})',
                   color=color, edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Classification Confidence')
    ax.set_ylabel('Number of Experiments')
    ax.set_title('Regime Classification Confidence Distribution\n(Cycle 176)')
    ax.legend(loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_xlim(0, 1.05)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_path}")


def main():
    """Generate all visualization figures."""
    # Paths
    results_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/regime_classification_analysis_c176.json")
    figures_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/regime_classification")
    figures_dir.mkdir(parents=True, exist_ok=True)

    if not results_path.exists():
        print(f"❌ Results file not found: {results_path}")
        return 1

    print("=" * 80)
    print("REGIME CLASSIFICATION VISUALIZATION")
    print("=" * 80)
    print(f"\nLoading results from: {results_path.name}\n")

    # Load data
    results = load_analysis_results(results_path)

    # Generate figures
    print("Generating publication-quality figures...\n")

    plot_regime_distribution(results, figures_dir / "regime_distribution.png")
    plot_condition_regime_heatmap(results, figures_dir / "condition_regime_heatmap.png")
    plot_cv_by_condition(results, figures_dir / "cv_by_condition.png")
    plot_confidence_distribution(results, figures_dir / "confidence_distribution.png")

    print("\n" + "=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)
    print(f"\n✓ All figures saved to: {figures_dir}/")
    print(f"  - regime_distribution.png")
    print(f"  - condition_regime_heatmap.png")
    print(f"  - cv_by_condition.png")
    print(f"  - confidence_distribution.png")
    print(f"\nFigure specifications: 300 DPI, publication-ready")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
