#!/usr/bin/env python3
"""
FIGURE GENERATION: C176 V6 Baseline Validation Results

Purpose: Generate publication-quality figures (300 DPI) for C176 V6 energy-regulated homeostasis validation

Figures:
- Figure 1: Population time series (all 20 seeds + mean)
- Figure 2: Spawn success rate distribution
- Figure 3: Population homeostasis metrics (mean, CV, basin distribution)
- Figure 4: Energy mechanism validation summary

Output: PNG @ 300 DPI for Paper 2 integration

Date: 2025-11-01
Cycle: 903
Researcher: Claude (DUALITY-ZERO-V2)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from datetime import datetime

# Figure parameters (publication quality)
DPI = 300
FIGSIZE_SINGLE = (8, 6)
FIGSIZE_DOUBLE = (12, 8)
FIGSIZE_QUAD = (16, 12)

# Colors (publication-friendly)
COLOR_INDIVIDUAL = '#CCCCCC'  # Light gray for individual seeds
COLOR_MEAN = '#2E86AB'  # Blue for mean
COLOR_EXPECTED = '#A23B72'  # Purple for expected range
COLOR_SUCCESS = '#28A745'  # Green for pass
COLOR_FAILURE = '#DC3545'  # Red for fail

# Expected values (from C171)
EXPECTED_MEAN_POP = 18.0
EXPECTED_CV_THRESHOLD = 15.0
EXPECTED_SPAWN_RATE_MIN = 25.0
EXPECTED_SPAWN_RATE_MAX = 40.0


def load_validation_results():
    """Load C176 V6 baseline validation results."""
    results_file = Path("experiments/results/cycle176_v6_baseline_validation.json")

    if not results_file.exists():
        raise FileNotFoundError(
            f"Results file not found: {results_file}\n"
            f"Has C176 V6 validation completed?"
        )

    with open(results_file, 'r') as f:
        data = json.load(f)

    return data


def figure1_population_timeseries(data, output_dir):
    """
    Figure 1: Population Time Series

    Shows population N(t) over 3000 cycles for all 20 seeds.
    Demonstrates homeostatic stability if C171 mechanism replicates.
    """
    print("Generating Figure 1: Population Time Series...")

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE, dpi=DPI)

    experiments = data['experiments']

    # Note: Current validation script doesn't save population trajectories
    # This is a template - would need to modify validation script to save
    # population_trajectory data for each seed

    # For now, create placeholder showing final populations
    seeds = [exp['seed'] for exp in experiments]
    final_pops = [exp['final_agent_count'] for exp in experiments]
    mean_pops = [exp['mean_population'] for exp in experiments]

    ax.scatter(seeds, final_pops, alpha=0.6, s=100,
               label='Final Population', color=COLOR_MEAN)
    ax.axhline(y=EXPECTED_MEAN_POP, color=COLOR_EXPECTED,
               linestyle='--', linewidth=2, label='Expected (~18 agents)')

    ax.set_xlabel('Random Seed', fontsize=12, fontweight='bold')
    ax.set_ylabel('Final Agent Count', fontsize=12, fontweight='bold')
    ax.set_title('C176 V6: Final Population Across Seeds',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = output_dir / "figure1_population_timeseries.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_path}")
    return output_path


def figure2_spawn_success_distribution(data, output_dir):
    """
    Figure 2: Spawn Success Rate Distribution

    Histogram of spawn success rates across 20 seeds.
    Tests H3: Energy constraint manifests as ~30-35% success rate.
    """
    print("Generating Figure 2: Spawn Success Rate Distribution...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGSIZE_DOUBLE, dpi=DPI)

    experiments = data['experiments']
    spawn_rates = [exp['spawn_success_rate'] for exp in experiments]

    # Panel A: Histogram
    ax1.hist(spawn_rates, bins=15, color=COLOR_MEAN, alpha=0.7, edgecolor='black')
    ax1.axvline(x=EXPECTED_SPAWN_RATE_MIN, color=COLOR_EXPECTED,
                linestyle='--', linewidth=2, label='Expected Range')
    ax1.axvline(x=EXPECTED_SPAWN_RATE_MAX, color=COLOR_EXPECTED,
                linestyle='--', linewidth=2)
    ax1.axvline(x=np.mean(spawn_rates), color=COLOR_SUCCESS,
                linestyle='-', linewidth=3, label=f'Mean: {np.mean(spawn_rates):.1f}%')

    ax1.set_xlabel('Spawn Success Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Frequency (Seeds)', fontsize=12, fontweight='bold')
    ax1.set_title('A) Spawn Success Rate Distribution',
                  fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Panel B: Box plot
    box = ax2.boxplot([spawn_rates], vert=True, patch_artist=True,
                       labels=['C176 V6'])
    box['boxes'][0].set_facecolor(COLOR_MEAN)
    box['boxes'][0].set_alpha(0.7)

    ax2.axhspan(EXPECTED_SPAWN_RATE_MIN, EXPECTED_SPAWN_RATE_MAX,
                color=COLOR_EXPECTED, alpha=0.2, label='Expected Range (25-40%)')

    ax2.set_ylabel('Spawn Success Rate (%)', fontsize=12, fontweight='bold')
    ax2.set_title('B) Success Rate Summary',
                  fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_path = output_dir / "figure2_spawn_success_distribution.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_path}")
    return output_path


def figure3_homeostasis_metrics(data, output_dir):
    """
    Figure 3: Population Homeostasis Metrics

    Multi-panel showing:
    - Mean population distribution
    - CV distribution
    - Basin A vs B distribution
    """
    print("Generating Figure 3: Homeostasis Metrics...")

    fig = plt.figure(figsize=FIGSIZE_QUAD, dpi=DPI)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    experiments = data['experiments']
    mean_pops = [exp['mean_population'] for exp in experiments]
    cvs = [exp['cv_population'] for exp in experiments]
    basins = [exp['basin'] for exp in experiments]

    # Panel A: Mean Population
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(mean_pops, bins=12, color=COLOR_MEAN, alpha=0.7, edgecolor='black')
    ax1.axvline(x=EXPECTED_MEAN_POP, color=COLOR_EXPECTED,
                linestyle='--', linewidth=2, label=f'Expected: {EXPECTED_MEAN_POP}')
    ax1.axvline(x=np.mean(mean_pops), color=COLOR_SUCCESS,
                linestyle='-', linewidth=3, label=f'Observed: {np.mean(mean_pops):.1f}')

    ax1.set_xlabel('Mean Population (agents)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Frequency (Seeds)', fontsize=11, fontweight='bold')
    ax1.set_title('A) Population Homeostasis', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Panel B: CV Distribution
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(cvs, bins=12, color=COLOR_MEAN, alpha=0.7, edgecolor='black')
    ax2.axvline(x=EXPECTED_CV_THRESHOLD, color=COLOR_EXPECTED,
                linestyle='--', linewidth=2, label=f'Threshold: {EXPECTED_CV_THRESHOLD}%')
    ax2.axvline(x=np.mean(cvs), color=COLOR_SUCCESS,
                linestyle='-', linewidth=3, label=f'Mean CV: {np.mean(cvs):.1f}%')

    ax2.set_xlabel('Coefficient of Variation (%)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency (Seeds)', fontsize=11, fontweight='bold')
    ax2.set_title('B) Population Stability (CV)', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Panel C: Basin Distribution
    ax3 = fig.add_subplot(gs[1, 0])
    basin_counts = {
        'A': basins.count('A'),
        'B': basins.count('B')
    }
    bars = ax3.bar(basin_counts.keys(), basin_counts.values(),
                   color=[COLOR_MEAN, COLOR_INDIVIDUAL], alpha=0.7, edgecolor='black')

    ax3.set_xlabel('Basin', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Count (Seeds)', fontsize=11, fontweight='bold')
    ax3.set_title('C) Basin Classification', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    # Add percentages on bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)} ({height/20*100:.0f}%)',
                ha='center', va='bottom', fontweight='bold')

    # Panel D: Summary Statistics Table
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')

    validation_results = data.get('validation', {})

    summary_data = [
        ['Metric', 'Expected', 'Observed', 'Status'],
        ['Mean Population', f'{EXPECTED_MEAN_POP:.1f}',
         f"{validation_results.get('overall_mean_pop', 0):.1f}",
         '✓' if validation_results.get('pop_check_passed', False) else '✗'],
        ['CV Threshold', f'< {EXPECTED_CV_THRESHOLD}%',
         f"{validation_results.get('overall_mean_cv', 0):.1f}%",
         '✓' if validation_results.get('cv_check_passed', False) else '✗'],
        ['Spawn Success', '25-40%',
         f"{validation_results.get('overall_mean_spawn_rate', 0):.1f}%",
         '✓' if validation_results.get('spawn_rate_check_passed', False) else '✗'],
    ]

    table = ax4.table(cellText=summary_data, cellLoc='center', loc='center',
                      colWidths=[0.3, 0.2, 0.2, 0.1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Style header row
    for i in range(4):
        table[(0, i)].set_facecolor('#E8E8E8')
        table[(0, i)].set_text_props(weight='bold')

    # Color status column
    for i in range(1, 4):
        status = summary_data[i][3]
        if status == '✓':
            table[(i, 3)].set_facecolor('#D4EDDA')
            table[(i, 3)].set_text_props(color='#155724', weight='bold')
        else:
            table[(i, 3)].set_facecolor('#F8D7DA')
            table[(i, 3)].set_text_props(color='#721C24', weight='bold')

    ax4.set_title('D) Validation Summary', fontsize=12, fontweight='bold', pad=20)

    plt.suptitle('C176 V6: Energy-Regulated Homeostasis Validation',
                 fontsize=16, fontweight='bold', y=0.98)

    output_path = output_dir / "figure3_homeostasis_metrics.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_path}")
    return output_path


def figure4_mechanism_summary(data, output_dir):
    """
    Figure 4: Energy Mechanism Validation Summary

    Visual summary of hypothesis testing results and mechanism diagram.
    """
    print("Generating Figure 4: Mechanism Summary...")

    fig = plt.figure(figsize=FIGSIZE_DOUBLE, dpi=DPI)
    gs = gridspec.GridSpec(2, 1, figure=fig, height_ratios=[1, 1], hspace=0.3)

    # Panel A: Hypothesis Test Results
    ax1 = fig.add_subplot(gs[0])
    ax1.axis('off')

    validation = data.get('validation', {})

    hypothesis_results = [
        ['Hypothesis', 'Expected', 'Observed', 'Pass', 'Interpretation'],
        ['H1: Population\nHomeostasis',
         '16-22 agents',
         f"{validation.get('overall_mean_pop', 0):.1f} agents",
         '✓' if validation.get('pop_check_passed', False) else '✗',
         'Energy-mediated\nself-regulation' if validation.get('pop_check_passed', False) else 'Mechanism\nfailure'],
        ['H2: Homeostatic\nStability',
         'CV < 15%',
         f"{validation.get('overall_mean_cv', 0):.1f}%",
         '✓' if validation.get('cv_check_passed', False) else '✗',
         'Low variance\nacross time' if validation.get('cv_check_passed', False) else 'High\nvariability'],
        ['H3: Energy\nConstraint',
         '25-40%',
         f"{validation.get('overall_mean_spawn_rate', 0):.1f}%",
         '✓' if validation.get('spawn_rate_check_passed', False) else '✗',
         'Failed spawns\nfrom low energy' if validation.get('spawn_rate_check_passed', False) else 'No energy\nlimitation'],
    ]

    table = ax1.table(cellText=hypothesis_results, cellLoc='center', loc='center',
                      colWidths=[0.2, 0.15, 0.15, 0.08, 0.22])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)

    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', weight='bold')

    # Color results
    for i in range(1, 4):
        status = hypothesis_results[i][3]
        if status == '✓':
            table[(i, 3)].set_facecolor('#D4EDDA')
            table[(i, 3)].set_text_props(color='#155724', weight='bold', size=14)
        else:
            table[(i, 3)].set_facecolor('#F8D7DA')
            table[(i, 3)].set_text_props(color='#721C24', weight='bold', size=14)

    ax1.set_title('A) Hypothesis Testing Results',
                  fontsize=12, fontweight='bold', pad=20)

    # Panel B: Mechanism Diagram (text-based for now)
    ax2 = fig.add_subplot(gs[1])
    ax2.axis('off')

    mechanism_text = """
    Energy-Regulated Population Homeostasis Mechanism:

    1. Parent Agent spawns child via parent.spawn_child(energy_fraction=0.3)
       → Requires sufficient parent energy
       → Spawn FAILS if parent energy too low

    2. Agent Composition Events deplete parent energy
       → Composition detected but agents NOT removed
       → Energy depletion accumulates over time

    3. Population Self-Regulates
       → High spawn success early (energy abundant)
       → Success rate declines as energy depletes
       → Equilibrium at ~30-35% success → ~18-20 agents

    Key Discovery (Cycle 891):
       - C176 V4/V5 had BUG: removed agents on composition (artifact collapse)
       - C171 NEVER removed agents but still homeostased
       - Mechanism: Energy constraint creates natural reproductive limits
       - NO explicit death needed - failed spawns = population regulation
    """

    ax2.text(0.05, 0.95, mechanism_text, transform=ax2.transAxes,
             fontsize=10, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='#F0F0F0', alpha=0.8))

    ax2.set_title('B) Energy-Mediated Homeostasis Mechanism',
                  fontsize=12, fontweight='bold', pad=20)

    plt.suptitle('C176 V6: Energy Mechanism Validation Summary',
                 fontsize=14, fontweight='bold', y=0.98)

    output_path = output_dir / "figure4_mechanism_summary.png"
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_path}")
    return output_path


def main():
    """Generate all C176 V6 validation figures."""
    print("=" * 80)
    print("C176 V6 FIGURE GENERATION")
    print("=" * 80)
    print()

    start_time = datetime.now()

    # Output directory
    output_dir = Path("data/figures/cycle176_v6")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load results
        print("Loading C176 V6 validation results...")
        data = load_validation_results()
        print(f"  Loaded {len(data['experiments'])} experiments")
        print()

        # Generate figures
        figures_created = []

        fig1 = figure1_population_timeseries(data, output_dir)
        figures_created.append(fig1)

        fig2 = figure2_spawn_success_distribution(data, output_dir)
        figures_created.append(fig2)

        fig3 = figure3_homeostasis_metrics(data, output_dir)
        figures_created.append(fig3)

        fig4 = figure4_mechanism_summary(data, output_dir)
        figures_created.append(fig4)

        # Summary
        print()
        print("=" * 80)
        print("FIGURE GENERATION COMPLETE")
        print("=" * 80)
        print()
        print(f"Generated {len(figures_created)} figures @ {DPI} DPI:")
        for fig_path in figures_created:
            print(f"  - {fig_path.name}")
        print()
        print(f"Output directory: {output_dir}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Duration: {duration:.1f} seconds")
        print()
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print()
        print("C176 V6 validation has not completed yet.")
        print("Run this script after validation finishes and generates results JSON.")
        print()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
