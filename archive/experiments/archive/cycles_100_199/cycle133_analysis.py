#!/usr/bin/env python3
"""
CYCLE 133 ANALYSIS: Threshold × Diversity Independence Test

Analyzes results from cycle133_threshold_diversity_2d.py to determine:
1. Are threshold and diversity independent?
2. Is there interaction between them?
3. Can we reduce dimensionality further (2D → 1D)?
"""

import json
import numpy as np
from pathlib import Path
from scipy.stats import chi2_contingency, pointbiserialr
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend


def load_results(results_file):
    """Load experimental results"""
    with open(results_file) as f:
        data = json.load(f)
    return data['metadata'], data['results']


def analyze_independence(results):
    """
    Test if threshold and diversity are independent

    Uses chi-square test of independence
    """
    # Extract data
    thresholds = sorted(set(r['threshold'] for r in results))
    diversities = sorted(set(r['diversity'] for r in results))

    # Create contingency table (threshold × diversity → basin)
    # We'll use 2×5×7 (Basin × Threshold × Diversity)
    basin_A_grid = np.zeros((len(thresholds), len(diversities)))
    basin_B_grid = np.zeros((len(thresholds), len(diversities)))

    for r in results:
        i = thresholds.index(r['threshold'])
        j = diversities.index(r['diversity'])
        if r['basin'] == 'A':
            basin_A_grid[i, j] = 1
        elif r['basin'] == 'B':
            basin_B_grid[i, j] = 1

    # Chi-square test for each threshold
    print("Independence Tests (per threshold):")
    print("=" * 60)

    for i, threshold in enumerate(thresholds):
        # For this threshold, is basin independent of diversity?
        row_A = basin_A_grid[i, :]
        row_B = basin_B_grid[i, :]
        contingency = np.array([row_A, row_B])

        if contingency.sum() > 0:
            chi2, p, dof, expected = chi2_contingency(contingency)
            print(f"Threshold {threshold}: χ²={chi2:.2f}, p={p:.4f}, dof={dof}")

    # Overall test: Is basin distribution independent across all conditions?
    print()
    print("Overall Independence Test:")
    print("=" * 60)

    # Reshape for overall test
    observed = []
    for i in range(len(thresholds)):
        for j in range(len(diversities)):
            basin_A_count = int(basin_A_grid[i, j])
            basin_B_count = int(basin_B_grid[i, j])
            observed.append([basin_A_count, basin_B_count])

    observed = np.array(observed).T  # 2 × 35 (Basin × Experiments)

    # This tests if basin frequency is uniform across all conditions
    chi2, p, dof, expected = chi2_contingency(observed)
    print(f"Overall: χ²={chi2:.2f}, p={p:.4f}, dof={dof}")

    if p < 0.05:
        print("→ REJECT independence (parameters affect basin)")
    else:
        print("→ ACCEPT independence (basin distribution uniform)")

    return basin_A_grid, basin_B_grid


def analyze_interactions(results):
    """
    Test for threshold × diversity interactions

    Uses point-biserial correlation with interaction term
    """
    print()
    print("Interaction Analysis:")
    print("=" * 60)

    # Binary encode basin
    basin_binary = [0 if r['basin'] == 'A' else 1 for r in results]

    # Extract predictors
    thresholds = [r['threshold'] for r in results]
    diversities = [r['diversity'] for r in results]
    interactions = [t * d for t, d in zip(thresholds, diversities)]

    # Correlations
    r_threshold, p_threshold = pointbiserialr(basin_binary, thresholds)
    r_diversity, p_diversity = pointbiserialr(basin_binary, diversities)
    r_interaction, p_interaction = pointbiserialr(basin_binary, interactions)

    print(f"Threshold correlation:   r={r_threshold:6.3f}, p={p_threshold:.4f}")
    print(f"Diversity correlation:   r={r_diversity:6.3f}, p={p_diversity:.4f}")
    print(f"Interaction correlation: r={r_interaction:6.3f}, p={p_interaction:.4f}")

    # Variance explained
    print()
    print("Variance Explained (r²):")
    print(f"Threshold:   {r_threshold**2*100:.1f}%")
    print(f"Diversity:   {r_diversity**2*100:.1f}%")
    print(f"Interaction: {r_interaction**2*100:.1f}%")

    # Best predictor
    r_values = {
        'threshold': abs(r_threshold),
        'diversity': abs(r_diversity),
        'interaction': abs(r_interaction)
    }
    best = max(r_values, key=r_values.get)
    print()
    print(f"Best predictor: {best} (|r|={r_values[best]:.3f})")

    return r_threshold, r_diversity, r_interaction


def plot_2d_basin_map(results, basin_A_grid, basin_B_grid, output_path):
    """Create 2D heatmap of basin assignments"""
    thresholds = sorted(set(r['threshold'] for r in results))
    diversities = sorted(set(r['diversity'] for r in results))

    # Create grid (0=A, 1=B)
    grid = np.zeros((len(thresholds), len(diversities)))
    for r in results:
        i = thresholds.index(r['threshold'])
        j = diversities.index(r['diversity'])
        grid[i, j] = 0 if r['basin'] == 'A' else 1

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    im = ax.imshow(grid, cmap='RdBu_r', aspect='auto', origin='lower')

    # Labels
    ax.set_xticks(range(len(diversities)))
    ax.set_xticklabels([f'{d:.2f}' for d in diversities])
    ax.set_yticks(range(len(thresholds)))
    ax.set_yticklabels(thresholds)

    ax.set_xlabel('Diversity (spread × mult)')
    ax.set_ylabel('Threshold')
    ax.set_title('Basin Assignment: Threshold × Diversity Grid')

    # Colorbar
    cbar = plt.colorbar(im, label='Basin (0=A, 1=B)')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print()
    print(f"2D basin map saved: {output_path}")


def main():
    # Load results
    results_file = Path(__file__).parent / "results" / "cycle133_threshold_diversity_grid.json"

    if not results_file.exists():
        print(f"ERROR: Results file not found: {results_file}")
        print("Run cycle133_threshold_diversity_2d.py first")
        return

    metadata, results = load_results(results_file)

    print("=" * 70)
    print("CYCLE 133 ANALYSIS: Threshold × Diversity Independence")
    print("=" * 70)
    print(f"Experiments: {metadata['total_experiments']}")
    print(f"Total cycles: {metadata['total_cycles']:,}")
    print()

    # Independence test
    basin_A_grid, basin_B_grid = analyze_independence(results)

    # Interaction analysis
    r_threshold, r_diversity, r_interaction = analyze_interactions(results)

    # Plot
    output_dir = Path(__file__).parent.parent / "DUALITY_ZERO_V2_CORE_RESEARCH" / "figures"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_path = output_dir / "cycle133_threshold_diversity_map.png"
    plot_2d_basin_map(results, basin_A_grid, basin_B_grid, output_path)

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Determine relationship
    if abs(r_interaction) > max(abs(r_threshold), abs(r_diversity)):
        print("→ INTERACTION DETECTED: threshold × diversity predicts best")
        print("  Further dimensional reduction may be possible (2D → 1D)")
    elif abs(r_threshold) < 0.3 and abs(r_diversity) < 0.3:
        print("→ INDEPENDENT: threshold and diversity are orthogonal")
        print("  2D parameter space confirmed")
    else:
        print("→ PARTIALLY COUPLED: Some relationship exists")
        print("  2D parameter space with non-orthogonal axes")

    print("=" * 70)


if __name__ == "__main__":
    main()
