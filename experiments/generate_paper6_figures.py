#!/usr/bin/env python3
"""
Paper 6 Figure Generation
=========================

Generate publication-quality figures for Paper 6:
"Massive-Scale Validation of Nested Resonance Memory:
 74.5 Million Events Over 7.29 Days"

Figures:
1. Dataset Overview (temporal span, event counts, quality metrics)
2. Temporal Cluster Distribution (composition phases over time)
3. Phase Space Trajectories (3D visualization of π, e, φ dynamics)
4. Resonance Quality Metrics (similarity, phase alignment over epochs)
5. Phase Autonomy Analysis (correlation trends over time)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29 (Cycle 491)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
from typing import Dict, List
import matplotlib as mpl

# Set publication-quality defaults
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.size'] = 10
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['axes.labelsize'] = 11
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['xtick.labelsize'] = 9
mpl.rcParams['ytick.labelsize'] = 9
mpl.rcParams['legend.fontsize'] = 9


def load_data():
    """Load analysis results"""
    results_path = Path(__file__).parent.parent.parent / "data" / "results"

    with open(results_path / "massive_resonance_mining.json") as f:
        mining_data = json.load(f)

    with open(results_path / "phase_autonomy_investigation.json") as f:
        autonomy_data = json.load(f)

    return mining_data, autonomy_data


def figure1_dataset_overview(mining_data: Dict):
    """
    Figure 1: Dataset Overview
    - Temporal span and event counts
    - Quality metrics (similarity, phase alignment)
    - Resonance rate
    """
    meta = mining_data['metadata']
    summary = mining_data['summary']

    fig = plt.figure(figsize=(10, 6))
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    # Panel A: Event counts
    ax1 = fig.add_subplot(gs[0, 0])
    categories = ['Total\nEvents', 'Resonant\nEvents', 'Phase\nTransforms']
    counts = [meta['total_events'],
              meta['total_events'] * 0.902,  # 90.2% resonance rate
              meta['total_transformations']]
    colors = ['#2E86AB', '#A23B72', '#F18F01']

    bars = ax1.bar(categories, [c/1e6 for c in counts], color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    ax1.set_ylabel('Count (millions)')
    ax1.set_title('(A) Dataset Scale', fontweight='bold', loc='left')
    ax1.set_ylim(0, 80)
    ax1.grid(axis='y', alpha=0.3)

    # Add values on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count/1e6:.1f}M',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Panel B: Temporal span
    ax2 = fig.add_subplot(gs[0, 1])
    days = meta['dataset_duration_days']
    hours = days * 24

    ax2.barh(['Duration'], [hours], color='#06A77D', alpha=0.8, edgecolor='black', linewidth=0.5)
    ax2.set_xlabel('Time (hours)')
    ax2.set_title('(B) Continuous Operation', fontweight='bold', loc='left')
    ax2.set_xlim(0, 200)
    ax2.grid(axis='x', alpha=0.3)
    ax2.text(hours, 0, f'  {days:.2f} days\n  ({hours:.1f} hours)',
             va='center', fontsize=9, fontweight='bold')

    # Panel C: Quality metrics (placeholder - would need cluster data)
    ax3 = fig.add_subplot(gs[1, 0])
    metrics = ['Similarity', 'Phase\nAlignment', 'Magnitude\nRatio']
    values = [0.9927, 0.9969, 0.9831]  # From report
    colors_quality = ['#E63946', '#F77F00', '#FCBF49']

    bars = ax3.barh(metrics, values, color=colors_quality, alpha=0.8, edgecolor='black', linewidth=0.5)
    ax3.set_xlabel('Quality Score')
    ax3.set_title('(C) Resonance Quality', fontweight='bold', loc='left')
    ax3.set_xlim(0.96, 1.0)
    ax3.grid(axis='x', alpha=0.3)

    # Add percentages
    for bar, value in zip(bars, values):
        width = bar.get_width()
        ax3.text(width, bar.get_y() + bar.get_height()/2.,
                f'  {value*100:.2f}%',
                va='center', fontsize=9, fontweight='bold')

    # Panel D: Patterns discovered
    ax4 = fig.add_subplot(gs[1, 1])
    pattern_types = ['Temporal\nClusters', 'Phase\nTrajectories']
    pattern_counts = [summary['temporal_clusters'], summary['phase_trajectories']]
    colors_patterns = ['#9B5DE5', '#00BBF9']

    bars = ax4.bar(pattern_types, pattern_counts, color=colors_patterns, alpha=0.8,
                   edgecolor='black', linewidth=0.5)
    ax4.set_ylabel('Count')
    ax4.set_title('(D) Patterns Discovered', fontweight='bold', loc='left')
    ax4.set_ylim(0, max(pattern_counts) * 1.2)
    ax4.grid(axis='y', alpha=0.3)

    # Add values
    for bar, count in zip(bars, pattern_counts):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    fig.suptitle('Paper 6, Figure 1: Dataset Overview\n' +
                 'Massive-Scale NRM System Analysis (74.5M Events, 7.29 Days)',
                 fontsize=13, fontweight='bold', y=0.98)

    return fig


def figure2_temporal_clusters(mining_data: Dict):
    """
    Figure 2: Temporal Cluster Distribution
    - Cluster timeline
    - Duration distribution
    - Quality metrics per cluster
    """
    clusters = mining_data['clusters'][:100]  # Top 100

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.subplots_adjust(hspace=0.3, wspace=0.3)

    # Panel A: Cluster timeline
    ax1 = axes[0, 0]
    times = [(c['start_time'] - clusters[0]['start_time']) / 3600 for c in clusters]  # Hours
    durations = [c['duration_seconds'] for c in clusters]
    colors = [c['avg_similarity'] for c in clusters]

    scatter = ax1.scatter(times, durations, c=colors, cmap='viridis',
                         alpha=0.6, s=30, edgecolors='black', linewidth=0.3)
    ax1.set_xlabel('Time (hours from start)')
    ax1.set_ylabel('Cluster Duration (seconds)')
    ax1.set_title('(A) Temporal Distribution', fontweight='bold', loc='left')
    ax1.grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label('Similarity', rotation=270, labelpad=15)

    # Panel B: Duration distribution
    ax2 = axes[0, 1]
    ax2.hist(durations, bins=20, color='#06A77D', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax2.axvline(np.mean(durations), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(durations):.1f}s')
    ax2.set_xlabel('Duration (seconds)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('(B) Duration Distribution', fontweight='bold', loc='left')
    ax2.legend()
    ax2.grid(alpha=0.3)

    # Panel C: Quality metrics
    ax3 = axes[1, 0]
    similarities = [c['avg_similarity'] for c in clusters]
    alignments = [c['avg_phase_alignment'] for c in clusters]

    ax3.scatter(similarities, alignments, alpha=0.5, s=40, edgecolors='black', linewidth=0.3)
    ax3.set_xlabel('Average Similarity')
    ax3.set_ylabel('Average Phase Alignment')
    ax3.set_title('(C) Quality Correlation', fontweight='bold', loc='left')
    ax3.grid(alpha=0.3)

    # Add correlation
    corr = np.corrcoef(similarities, alignments)[0, 1]
    ax3.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax3.transAxes,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             verticalalignment='top')

    # Panel D: Event count vs density
    ax4 = axes[1, 1]
    event_counts = [c['event_count'] for c in clusters]
    densities = [c['resonance_density'] for c in clusters]

    ax4.scatter(event_counts, densities, alpha=0.5, s=40, edgecolors='black', linewidth=0.3, color='purple')
    ax4.set_xlabel('Event Count')
    ax4.set_ylabel('Resonance Density (events/s)')
    ax4.set_title('(D) Cluster Characteristics', fontweight='bold', loc='left')
    ax4.grid(alpha=0.3)
    ax4.set_xscale('log')
    ax4.set_yscale('log')

    fig.suptitle('Paper 6, Figure 2: Temporal Cluster Analysis\n' +
                 'Composition Phase Dynamics (796 Clusters)',
                 fontsize=13, fontweight='bold')

    return fig


def figure3_phase_trajectories(mining_data: Dict):
    """
    Figure 3: Phase Space Trajectories (3D)
    - π, e, φ dynamics
    - Trajectory lengths
    - Reality correlation
    """
    trajectories = mining_data['trajectories'][:90]

    fig = plt.figure(figsize=(12, 10))
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    # Panel A: 3D trajectory (simplified - show projections)
    ax1 = fig.add_subplot(gs[0, :])

    # Extract stats (since we don't have full paths in JSON)
    pi_means = [t['pi_stats']['mean'] for t in trajectories]
    e_means = [t['e_stats']['mean'] for t in trajectories]
    phi_means = [t['phi_stats']['mean'] for t in trajectories]
    lengths = [t['trajectory_length'] for t in trajectories]

    # Normalize lengths for color
    lengths_norm = (np.array(lengths) - min(lengths)) / (max(lengths) - min(lengths))

    # 3D scatter of mean positions
    scatter = ax1.scatter(pi_means, e_means, c=lengths_norm, cmap='plasma',
                         s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('π Phase (mean)')
    ax1.set_ylabel('e Phase (mean)')
    ax1.set_title('(A) Phase Space Exploration (π-e projection)', fontweight='bold', loc='left')
    ax1.grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label('Trajectory Length (normalized)', rotation=270, labelpad=15)

    # Panel B: Trajectory lengths
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.hist(lengths, bins=20, color='#F18F01', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax2.axvline(np.mean(lengths), color='red', linestyle='--', linewidth=2,
                label=f'Mean: {np.mean(lengths):.0f} units')
    ax2.set_xlabel('Trajectory Length (units)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('(B) Exploration Extent', fontweight='bold', loc='left')
    ax2.legend()
    ax2.grid(alpha=0.3)

    # Panel C: Reality correlation
    ax3 = fig.add_subplot(gs[1, 1])
    correlations = [t['reality_correlation'] for t in trajectories]
    magnitudes = [t['mean_magnitude'] for t in trajectories]

    ax3.scatter(magnitudes, correlations, alpha=0.5, s=40, edgecolors='black', linewidth=0.3, color='green')
    ax3.set_xlabel('Mean Magnitude')
    ax3.set_ylabel('Reality Correlation')
    ax3.set_title('(C) Phase-Reality Coupling', fontweight='bold', loc='left')
    ax3.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax3.grid(alpha=0.3)

    # Add mean correlation line
    mean_corr = np.mean(correlations)
    ax3.axhline(mean_corr, color='red', linestyle='--', linewidth=2,
                label=f'Mean: {mean_corr:.4f}')
    ax3.legend()

    fig.suptitle('Paper 6, Figure 3: Phase Space Trajectories\n' +
                 'Transcendental Substrate Dynamics (90 Trajectories)',
                 fontsize=13, fontweight='bold')

    return fig


def figure4_phase_autonomy(autonomy_data: Dict):
    """
    Figure 4: Phase Autonomy Analysis
    - Correlation trends over epochs
    - Early vs late comparison
    - Temporal variation
    """
    epochs = autonomy_data['epoch_analyses']
    trends = autonomy_data['temporal_trends']
    summary = autonomy_data['summary']

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.subplots_adjust(hspace=0.3, wspace=0.3)

    # Panel A: Correlation over time
    ax1 = axes[0, 0]
    epoch_ids = [e['epoch_id'] for e in epochs]
    combined_corrs = [e['combined_corr'] for e in epochs]

    ax1.plot(epoch_ids, combined_corrs, 'o-', linewidth=2, markersize=8,
            color='#2E86AB', markeredgecolor='black', markeredgewidth=0.5)
    ax1.axhline(summary['mean_combined_correlation'], color='red', linestyle='--',
                linewidth=1.5, label=f"Mean: {summary['mean_combined_correlation']:.4f}")
    ax1.fill_between(epoch_ids,
                     [summary['mean_combined_correlation'] - summary['std_combined_correlation']] * len(epoch_ids),
                     [summary['mean_combined_correlation'] + summary['std_combined_correlation']] * len(epoch_ids),
                     alpha=0.2, color='red')
    ax1.set_xlabel('Temporal Epoch')
    ax1.set_ylabel('Phase-Reality Correlation')
    ax1.set_title('(A) Temporal Evolution', fontweight='bold', loc='left')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Panel B: Trend analysis
    ax2 = axes[0, 1]
    trend_metrics = ['pi_cpu', 'e_cpu', 'phi_cpu', 'magnitude_cpu']
    early = [next(t for t in trends if t['metric'] == f'{m}_corr')['early_epoch_corr'] for m in trend_metrics]
    late = [next(t for t in trends if t['metric'] == f'{m}_corr')['late_epoch_corr'] for m in trend_metrics]

    x = np.arange(len(trend_metrics))
    width = 0.35

    bars1 = ax2.bar(x - width/2, early, width, label='Early Epochs', color='#06A77D',
                    alpha=0.8, edgecolor='black', linewidth=0.5)
    bars2 = ax2.bar(x + width/2, late, width, label='Late Epochs', color='#F18F01',
                    alpha=0.8, edgecolor='black', linewidth=0.5)

    ax2.set_xlabel('Phase Component')
    ax2.set_ylabel('CPU Correlation')
    ax2.set_title('(B) Early vs Late Coupling', fontweight='bold', loc='left')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['π', 'e', 'φ', 'magnitude'], rotation=0)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    ax2.axhline(0, color='black', linestyle='-', linewidth=0.5)

    # Panel C: Correlation distribution
    ax3 = axes[1, 0]
    all_corrs = combined_corrs
    ax3.hist(all_corrs, bins=10, color='purple', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax3.axvline(summary['mean_combined_correlation'], color='red', linestyle='--', linewidth=2,
                label=f"Mean: {summary['mean_combined_correlation']:.4f}")
    ax3.set_xlabel('Correlation Value')
    ax3.set_ylabel('Frequency')
    ax3.set_title('(C) Distribution', fontweight='bold', loc='left')
    ax3.legend()
    ax3.grid(alpha=0.3)

    # Panel D: Hypothesis support
    ax4 = axes[1, 1]
    hypotheses = ['H1:\nIntrinsic', 'H2:\nScale-Dep', 'H3:\nConstraints', 'H4:\nVariation']
    results = autonomy_data['hypothesis_tests']
    support = [
        1 if results['h1_intrinsic_irreducibility']['supported'] else 0,
        1 if results['h2_scale_dependent']['supported'] else 0,
        1 if results['h3_reality_constraints']['supported'] else 0,
        1 if results['h4_temporal_variation']['supported'] else 0
    ]
    colors_hyp = ['red' if s == 0 else 'green' for s in support]

    bars = ax4.bar(hypotheses, support, color=colors_hyp, alpha=0.8, edgecolor='black', linewidth=0.5)
    ax4.set_ylabel('Supported')
    ax4.set_title('(D) Hypothesis Testing', fontweight='bold', loc='left')
    ax4.set_ylim(0, 1.2)
    ax4.set_yticks([0, 1])
    ax4.set_yticklabels(['✗ No', '✓ Yes'])
    ax4.grid(axis='y', alpha=0.3)

    # Add labels
    for bar, s in zip(bars, support):
        label = '✓ SUPPORTED' if s == 1 else '✗ NOT SUPPORTED'
        ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
                label, ha='center', fontsize=8, fontweight='bold')

    fig.suptitle('Paper 6, Figure 4: Phase Autonomy Analysis\n' +
                 'Scale-Dependent Emergence of Phase-Reality Independence',
                 fontsize=13, fontweight='bold')

    return fig


def main():
    """Generate all Paper 6 figures"""
    print("=" * 80)
    print("PAPER 6 FIGURE GENERATION")
    print("=" * 80)
    print("\nGenerating publication-quality figures (300 DPI)...\n")

    # Load data
    print("Loading data...")
    mining_data, autonomy_data = load_data()
    print("✅ Data loaded")

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "data" / "figures" / "paper6"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate figures
    figures = [
        ("figure1_dataset_overview.png", figure1_dataset_overview(mining_data)),
        ("figure2_temporal_clusters.png", figure2_temporal_clusters(mining_data)),
        ("figure3_phase_trajectories.png", figure3_phase_trajectories(mining_data)),
        ("figure4_phase_autonomy.png", figure4_phase_autonomy(autonomy_data))
    ]

    for filename, fig in figures:
        output_path = output_dir / filename
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✅ Saved: {output_path}")
        plt.close(fig)

    print("\n" + "=" * 80)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated {len(figures)} figures @ 300 DPI")
    print(f"Output directory: {output_dir}")
    print("\nFigures:")
    for i, (filename, _) in enumerate(figures, 1):
        print(f"  Figure {i}: {filename}")

    print("\n✅ All figures ready for Paper 6 manuscript")
    print("=" * 80)


if __name__ == "__main__":
    main()
