#!/usr/bin/env python3
"""
Visualize Runtime Variance Analysis for C257 (H1×H5 Factorial Experiment)

Creates publication-quality figures documenting extreme I/O-bound behavior:
- Linear variance acceleration (8-9 percentage points/minute)
- Wall/CPU ratio sustainability (30× threshold)
- I/O wait persistence (96%+ over extended execution)
- Milestone progression timeline

Contributes to Paper 3 Supplement 5 (Reality Grounding Overhead).

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Computational Partner: Claude (Sonnet 4.5)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
Date: 2025-10-31 (Cycle 775)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Publication standards
DPI = 300
FIGSIZE = (10, 6)
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple
    'accent': '#F18F01',       # Orange
    'success': '#06A77D',      # Green
    'milestone': '#D00000',    # Red
    'grid': '#CCCCCC'
}

def load_milestone_data(data_file: Optional[str] = None) -> List[Dict]:
    """
    Load milestone data points from JSON file or use embedded data.

    Data format:
    {
        "timestamp": "2025-10-31T10:00:00",
        "wall_minutes": 301.5,
        "cpu_minutes": 10.7,
        "cpu_percent": 2.8,
        "variance_percent": 2501.2,
        "wall_cpu_ratio": 28.1,
        "io_wait_percent": 96.4,
        "milestone": "5H + +2500%"
    }
    """
    if data_file and Path(data_file).exists():
        with open(data_file, 'r') as f:
            return json.load(f)

    # Embedded milestone data from Cycles 760-774 documentation
    # This will be replaced with actual C257 completion data
    embedded_data = [
        {
            "cycle": 760,
            "timestamp": "2025-10-31T09:58:00",
            "wall_minutes": 301.5,
            "cpu_minutes": 10.7,
            "cpu_percent": 2.8,
            "variance_percent": 2501.2,
            "wall_cpu_ratio": 28.1,
            "io_wait_percent": 96.4,
            "milestone": "5H + +2500%"
        },
        {
            "cycle": 762,
            "timestamp": "2025-10-31T10:26:00",
            "wall_minutes": 324.8,
            "cpu_minutes": 11.3,
            "cpu_percent": 2.5,
            "variance_percent": 2700.0,
            "wall_cpu_ratio": 28.7,
            "io_wait_percent": 96.6,
            "milestone": "+2700%"
        },
        {
            "cycle": 763,
            "timestamp": "2025-10-31T10:33:00",
            "wall_minutes": 331.3,
            "cpu_minutes": 11.5,
            "cpu_percent": 2.4,
            "variance_percent": 2756.0,
            "wall_cpu_ratio": 28.8,
            "io_wait_percent": 96.5,
            "milestone": "+2800% (approaching)"
        },
        {
            "cycle": 764,
            "timestamp": "2025-10-31T10:42:00",
            "wall_minutes": 340.5,
            "cpu_minutes": 11.8,
            "cpu_percent": 2.3,
            "variance_percent": 2835.3,
            "wall_cpu_ratio": 28.9,
            "io_wait_percent": 96.6,
            "milestone": "+2800% crossed"
        },
        {
            "cycle": 766,
            "timestamp": "2025-10-31T11:05:00",
            "wall_minutes": 362.08,
            "cpu_minutes": 12.2,
            "cpu_percent": 2.1,
            "variance_percent": 3021.4,
            "wall_cpu_ratio": 29.7,
            "io_wait_percent": 96.7,
            "milestone": "6H + +2800% + +3000%"
        },
        {
            "cycle": 767,
            "timestamp": "2025-10-31T11:14:00",
            "wall_minutes": 371.2,
            "cpu_minutes": 12.4,
            "cpu_percent": 2.0,
            "variance_percent": 3102.0,
            "wall_cpu_ratio": 29.9,
            "io_wait_percent": 96.7,
            "milestone": "+3100%"
        },
        {
            "cycle": 769,
            "timestamp": "2025-10-31T11:36:00",
            "wall_minutes": 392.52,
            "cpu_minutes": 13.0,
            "cpu_percent": 1.9,
            "variance_percent": 3283.8,
            "wall_cpu_ratio": 30.3,
            "io_wait_percent": 96.7,
            "milestone": "6.5H + +3200% + 30× Wall/CPU"
        },
        {
            "cycle": 771,
            "timestamp": "2025-10-31T11:41:00",
            "wall_minutes": 397.68,
            "cpu_minutes": 13.08,
            "cpu_percent": 1.9,
            "variance_percent": 3328.3,
            "wall_cpu_ratio": 30.4,
            "io_wait_percent": 96.7,
            "milestone": "+3300%"
        },
        {
            "cycle": 774,
            "timestamp": "2025-10-31T12:04:00",
            "wall_minutes": 420.27,
            "cpu_minutes": 13.81,
            "cpu_percent": 1.9,
            "variance_percent": 3523.4,
            "wall_cpu_ratio": 30.4,
            "io_wait_percent": 96.7,
            "milestone": "7H + +3500%"
        }
    ]

    return embedded_data

def calculate_elapsed_minutes(data: List[Dict]) -> np.ndarray:
    """Calculate elapsed minutes from first timestamp."""
    if 'elapsed_minutes' in data[0]:
        return np.array([d['elapsed_minutes'] for d in data])

    # Calculate from timestamps
    start_time = datetime.fromisoformat(data[0]['timestamp'])
    elapsed = []
    for d in data:
        current_time = datetime.fromisoformat(d['timestamp'])
        delta = (current_time - start_time).total_seconds() / 60.0
        elapsed.append(delta)
    return np.array(elapsed)

def plot_variance_over_time(data: List[Dict], output_dir: Path):
    """
    Figure 1: Variance percentage over execution time.
    Shows linear acceleration pattern (8-9 pp/min sustained growth).
    """
    elapsed = calculate_elapsed_minutes(data)
    variance = np.array([d['variance_percent'] for d in data])

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)

    # Plot variance trajectory
    ax.plot(elapsed, variance, 'o-', color=COLORS['primary'],
            linewidth=2, markersize=8, label='Observed Variance')

    # Fit linear trend
    if len(elapsed) >= 2:
        coeffs = np.polyfit(elapsed, variance, 1)
        trend_line = np.poly1d(coeffs)
        ax.plot(elapsed, trend_line(elapsed), '--', color=COLORS['accent'],
                linewidth=1.5, alpha=0.7,
                label=f'Linear Trend ({coeffs[0]:.1f} pp/min)')

    # Mark major milestones
    milestone_indices = [0, 4, 6, 8]  # 5H+2500%, 6H+3000%, 6.5H+3200%+30×, 7H+3500%
    for idx in milestone_indices:
        if idx < len(data):
            ax.plot(elapsed[idx], variance[idx], '*', color=COLORS['milestone'],
                    markersize=15, markeredgewidth=1.5, markeredgecolor='black')

    # Styling
    ax.set_xlabel('Elapsed Time (minutes)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Runtime Variance (%)', fontsize=12, fontweight='bold')
    ax.set_title('C257 Runtime Variance: Linear Acceleration Pattern',
                 fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

    # Expected runtime reference line
    expected_variance = 0  # 11.6 min expected = 0% variance
    ax.axhline(y=expected_variance, color='gray', linestyle=':',
               linewidth=1, alpha=0.5, label='Expected Runtime (0%)')

    plt.tight_layout()
    output_file = output_dir / 'c257_variance_over_time.png'
    plt.savefig(output_file, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_wall_cpu_ratio_over_time(data: List[Dict], output_dir: Path):
    """
    Figure 2: Wall/CPU ratio over execution time.
    Shows 30× threshold sustainability (extreme I/O-bound classification).
    """
    elapsed = calculate_elapsed_minutes(data)
    ratios = np.array([d['wall_cpu_ratio'] for d in data])

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)

    # Plot ratio trajectory
    ax.plot(elapsed, ratios, 'o-', color=COLORS['secondary'],
            linewidth=2, markersize=8, label='Wall/CPU Ratio')

    # 30× threshold reference line
    ax.axhline(y=30.0, color=COLORS['milestone'], linestyle='--',
               linewidth=2, alpha=0.7, label='30× Threshold (Extreme I/O-Bound)')

    # Shaded region above 30×
    ax.fill_between(elapsed, 30, ratios, where=(ratios >= 30),
                     alpha=0.2, color=COLORS['milestone'],
                     label='Sustained Extreme State')

    # Mark 30× crossing
    crossing_idx = np.where(ratios >= 30.0)[0]
    if len(crossing_idx) > 0:
        first_cross = crossing_idx[0]
        ax.plot(elapsed[first_cross], ratios[first_cross], '*',
                color=COLORS['milestone'], markersize=15,
                markeredgewidth=1.5, markeredgecolor='black')
        ax.annotate('30× Milestone',
                    xy=(elapsed[first_cross], ratios[first_cross]),
                    xytext=(10, -20), textcoords='offset points',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', lw=1.5))

    # Styling
    ax.set_xlabel('Elapsed Time (minutes)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Wall Time / CPU Time Ratio', fontsize=12, fontweight='bold')
    ax.set_title('C257 Wall/CPU Ratio: Sustained Extreme I/O-Bound State',
                 fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])
    ax.legend(loc='lower right', fontsize=10, framealpha=0.9)

    # Set y-axis to start slightly below minimum ratio
    y_min = min(ratios) - 1
    y_max = max(ratios) + 2
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    output_file = output_dir / 'c257_wall_cpu_ratio_sustainability.png'
    plt.savefig(output_file, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_io_wait_persistence(data: List[Dict], output_dir: Path):
    """
    Figure 3: I/O wait percentage over execution time.
    Shows 96%+ persistence across extended execution (hours).
    """
    elapsed = calculate_elapsed_minutes(data)
    io_wait = np.array([d['io_wait_percent'] for d in data])

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)

    # Plot I/O wait trajectory
    ax.plot(elapsed, io_wait, 'o-', color=COLORS['success'],
            linewidth=2, markersize=8, label='I/O Wait %')

    # 96% threshold reference line
    ax.axhline(y=96.0, color=COLORS['milestone'], linestyle='--',
               linewidth=2, alpha=0.7, label='96% Threshold')

    # Shaded region above 96%
    ax.fill_between(elapsed, 96, io_wait, where=(io_wait >= 96),
                     alpha=0.2, color=COLORS['success'],
                     label='Extreme I/O-Bound Region')

    # Styling
    ax.set_xlabel('Elapsed Time (minutes)', fontsize=12, fontweight='bold')
    ax.set_ylabel('I/O Wait (%)', fontsize=12, fontweight='bold')
    ax.set_title('C257 I/O Wait Persistence: >96% Across Extended Execution',
                 fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, color=COLORS['grid'])
    ax.legend(loc='lower right', fontsize=10, framealpha=0.9)

    # Set y-axis to emphasize 96%+ region
    ax.set_ylim(95, 97.5)

    # Add text annotation showing persistence duration
    if len(elapsed) >= 2:
        duration_hours = (elapsed[-1] - elapsed[0]) / 60.0
        ax.text(0.05, 0.05, f'Sustained {io_wait.mean():.1f}% I/O wait\nover {duration_hours:.1f} hours',
                transform=ax.transAxes, fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8))

    plt.tight_layout()
    output_file = output_dir / 'c257_io_wait_persistence.png'
    plt.savefig(output_file, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def plot_milestone_timeline(data: List[Dict], output_dir: Path):
    """
    Figure 4: Milestone progression timeline.
    Shows when major round-number thresholds were crossed (hours, percentages, 30× ratio).
    """
    elapsed = calculate_elapsed_minutes(data)
    milestones = [d['milestone'] for d in data]

    fig, ax = plt.subplots(figsize=(12, 8), dpi=DPI)

    # Create timeline plot
    y_positions = range(len(data))

    # Plot milestone points
    ax.scatter(elapsed, y_positions, s=200, c=COLORS['primary'],
               edgecolors='black', linewidths=2, zorder=3)

    # Add milestone labels
    for i, (x, y, label) in enumerate(zip(elapsed, y_positions, milestones)):
        # Alternate text position left/right for readability
        ha = 'left' if i % 2 == 0 else 'right'
        offset = 5 if i % 2 == 0 else -5

        ax.annotate(label, xy=(x, y), xytext=(offset, 0),
                    textcoords='offset points', fontsize=9,
                    ha=ha, va='center', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7))

    # Draw connecting line
    ax.plot(elapsed, y_positions, '-', color=COLORS['accent'],
            linewidth=2, alpha=0.5, zorder=1)

    # Styling
    ax.set_xlabel('Elapsed Time (minutes)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Milestone Sequence', fontsize=12, fontweight='bold')
    ax.set_title('C257 Milestone Progression: 5H → 7H+ Timeline',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([f"Cycle {d['cycle']}" for d in data])
    ax.grid(True, axis='x', alpha=0.3, color=COLORS['grid'])

    # Add execution duration summary
    duration_hours = elapsed[-1] / 60.0
    variance_range = f"+{data[0]['variance_percent']:.0f}% → +{data[-1]['variance_percent']:.0f}%"
    summary_text = (f"Execution Duration: {duration_hours:.1f} hours\n"
                    f"Variance Range: {variance_range}\n"
                    f"Wall/CPU Ratio: {data[0]['wall_cpu_ratio']:.1f}× → {data[-1]['wall_cpu_ratio']:.1f}×")
    ax.text(0.98, 0.02, summary_text, transform=ax.transAxes,
            fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.9))

    plt.tight_layout()
    output_file = output_dir / 'c257_milestone_timeline.png'
    plt.savefig(output_file, dpi=DPI, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

def generate_summary_statistics(data: List[Dict]) -> Dict:
    """Generate summary statistics for C257 extreme behavior."""
    elapsed = calculate_elapsed_minutes(data)
    variance = np.array([d['variance_percent'] for d in data])
    ratios = np.array([d['wall_cpu_ratio'] for d in data])
    io_wait = np.array([d['io_wait_percent'] for d in data])

    # Linear fit for variance acceleration rate
    coeffs = np.polyfit(elapsed, variance, 1)
    acceleration_rate = coeffs[0]  # percentage points per minute

    # Time above 30× threshold
    above_30x = ratios >= 30.0
    if any(above_30x):
        first_30x_idx = np.where(above_30x)[0][0]
        time_at_30x = elapsed[-1] - elapsed[first_30x_idx]
    else:
        time_at_30x = 0.0

    stats = {
        'execution_duration_minutes': elapsed[-1],
        'execution_duration_hours': elapsed[-1] / 60.0,
        'variance_initial': variance[0],
        'variance_final': variance[-1],
        'variance_increase': variance[-1] - variance[0],
        'variance_acceleration_pp_per_min': acceleration_rate,
        'wall_cpu_ratio_initial': ratios[0],
        'wall_cpu_ratio_final': ratios[-1],
        'wall_cpu_ratio_mean': ratios.mean(),
        'wall_cpu_ratio_max': ratios.max(),
        'time_above_30x_threshold_minutes': time_at_30x,
        'io_wait_mean': io_wait.mean(),
        'io_wait_min': io_wait.min(),
        'io_wait_max': io_wait.max(),
        'milestones_documented': len(data),
        'cycles_monitored': [d['cycle'] for d in data]
    }

    return stats

def main():
    """Generate all variance analysis figures for C257."""
    print("\n" + "="*70)
    print("C257 Runtime Variance Analysis Visualization")
    print("="*70 + "\n")

    # Setup output directory
    output_dir = Path('data/figures/paper3_supplement5')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}\n")

    # Load data
    print("Loading milestone data...")
    data = load_milestone_data()
    print(f"✓ Loaded {len(data)} milestone data points (Cycles {data[0]['cycle']}-{data[-1]['cycle']})\n")

    # Generate figures
    print("Generating publication figures (300 DPI)...\n")

    plot_variance_over_time(data, output_dir)
    plot_wall_cpu_ratio_over_time(data, output_dir)
    plot_io_wait_persistence(data, output_dir)
    plot_milestone_timeline(data, output_dir)

    # Generate summary statistics
    print("\nGenerating summary statistics...")
    stats = generate_summary_statistics(data)
    stats_file = output_dir / 'c257_summary_statistics.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Saved: {stats_file}")

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(f"Execution Duration: {stats['execution_duration_hours']:.2f} hours ({stats['execution_duration_minutes']:.1f} min)")
    print(f"Variance Range: +{stats['variance_initial']:.1f}% → +{stats['variance_final']:.1f}%")
    print(f"Variance Increase: +{stats['variance_increase']:.1f} percentage points")
    print(f"Linear Acceleration: {stats['variance_acceleration_pp_per_min']:.2f} pp/min")
    print(f"Wall/CPU Ratio: {stats['wall_cpu_ratio_initial']:.1f}× → {stats['wall_cpu_ratio_final']:.1f}× (mean: {stats['wall_cpu_ratio_mean']:.1f}×)")
    print(f"Time Above 30× Threshold: {stats['time_above_30x_threshold_minutes']:.1f} min")
    print(f"I/O Wait: {stats['io_wait_mean']:.1f}% (range: {stats['io_wait_min']:.1f}%-{stats['io_wait_max']:.1f}%)")
    print(f"Milestones Documented: {stats['milestones_documented']} data points")
    print("="*70 + "\n")

    print("✓ All figures generated successfully!")
    print(f"✓ Output location: {output_dir}/")
    print("\nFigures ready for Paper 3 Supplement 5 integration.")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
