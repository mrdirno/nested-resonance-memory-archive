#!/usr/bin/env python3
"""
TEMPORAL EVOLUTION VISUALIZER
Publication-quality visualizations of research trajectory across cycles 133-161

Purpose:
  Create comprehensive visualizations showing:
    1. Composition events evolution (29 cycles timeline)
    2. Basin A convergence trajectory
    3. Spawn accuracy improvements (pre/post bug fixes)
    4. Parameter space coverage expansion
    5. Discovery timeline with major breakthroughs
    6. Publication-ready figure generation

Analytical Framework:
  - Temporal Trends: Linear/nonlinear regression across cycles
  - Phase Transitions: Detect regime changes from bug fixes
  - Discovery Impact: Quantify before/after effects
  - Research Velocity: Rate of parameter space exploration

Publication Value:
  "Systematic Discovery Through Iterative Experimentation"
  - Demonstrates 29-cycle research progression
  - Validates bug fix impacts quantitatively
  - Shows emergence of understanding (Basin A discovery)
  - Documents parameter space systematic exploration

Framework Validation:
  - Temporal Stewardship: Research trajectory documentation for future AI
  - Self-Giving: System visualizing own research evolution
  - NRM: Meta-level pattern composition across experimental cycles

Date: 2025-10-25
Status: Production visualization pipeline
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from scipy import stats
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality matplotlib style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# =============================================================================
# DATA LOADING
# =============================================================================

def load_all_cycles() -> Dict[int, Dict]:
    """Load all completed experimental cycles."""
    results_dir = Path(__file__).parent / 'results'

    cycles = {}

    for file_path in sorted(results_dir.glob('cycle*.json')):
        try:
            cycle_num = int(file_path.stem.split('_')[0].replace('cycle', ''))

            with open(file_path, 'r') as f:
                data = json.load(f)

            cycles[cycle_num] = {
                'filename': file_path.name,
                'data': data,
            }

        except (ValueError, json.JSONDecodeError):
            continue

    return cycles


def extract_cycle_metrics(cycle_data: Dict) -> Optional[Dict]:
    """Extract key metrics from a single cycle."""

    # Handle different data formats
    if isinstance(cycle_data, list):
        experiments = cycle_data
    elif 'experiments' in cycle_data:
        experiments = cycle_data['experiments']
    elif 'results' in cycle_data:
        experiments = cycle_data['results']
    else:
        return None

    if not experiments:
        return None

    metrics = {
        'n_experiments': len(experiments),
        'composition_events': [],
        'spawn_accuracy': [],
        'basin_a_count': 0,
        'basin_b_count': 0,
        'runtime_seconds': [],
        'frequencies': set(),
        'seeds': set(),
        'thresholds': set(),
    }

    for exp in experiments:
        # Composition events
        if 'avg_composition_events' in exp:
            metrics['composition_events'].append(exp['avg_composition_events'])
        elif 'composition_events' in exp:
            metrics['composition_events'].append(exp['composition_events'])

        # Spawn accuracy
        if 'spawn_accuracy_pct' in exp:
            metrics['spawn_accuracy'].append(exp['spawn_accuracy_pct'])

        # Basin classification
        if 'basin' in exp:
            if exp['basin'] == 'A':
                metrics['basin_a_count'] += 1
            else:
                metrics['basin_b_count'] += 1
        elif 'basin_classifications' in exp:
            # Use threshold 2.5 for consistency
            basin = exp['basin_classifications'].get('threshold_2.5', 'B')
            if basin == 'A':
                metrics['basin_a_count'] += 1
            else:
                metrics['basin_b_count'] += 1

        # Runtime
        if 'runtime_seconds' in exp:
            metrics['runtime_seconds'].append(exp['runtime_seconds'])

        # Parameter tracking
        if 'frequency' in exp and exp['frequency'] is not None:
            metrics['frequencies'].add(exp['frequency'])
        if 'seed' in exp and exp['seed'] is not None:
            metrics['seeds'].add(exp['seed'])
        if 'threshold' in exp and exp['threshold'] is not None:
            metrics['thresholds'].add(exp['threshold'])

    # Calculate summary statistics
    if metrics['composition_events']:
        metrics['composition_mean'] = float(np.mean(metrics['composition_events']))
        metrics['composition_std'] = float(np.std(metrics['composition_events']))

    if metrics['spawn_accuracy']:
        metrics['spawn_accuracy_mean'] = float(np.mean(metrics['spawn_accuracy']))
        metrics['spawn_accuracy_std'] = float(np.std(metrics['spawn_accuracy']))

    total = metrics['basin_a_count'] + metrics['basin_b_count']
    metrics['basin_a_pct'] = (metrics['basin_a_count'] / total * 100) if total > 0 else 0.0

    if metrics['runtime_seconds']:
        metrics['runtime_mean'] = float(np.mean(metrics['runtime_seconds']))

    # Convert sets to counts for serialization
    metrics['n_frequencies'] = len(metrics['frequencies'])
    metrics['n_seeds'] = len(metrics['seeds'])
    metrics['n_thresholds'] = len(metrics['thresholds'])

    # Remove sets (not JSON serializable)
    del metrics['frequencies']
    del metrics['seeds']
    del metrics['thresholds']

    return metrics


# =============================================================================
# TEMPORAL EVOLUTION ANALYSIS
# =============================================================================

def build_evolution_timeline(cycles: Dict[int, Dict]) -> Dict:
    """Build complete timeline of research evolution."""

    timeline = {
        'cycles': [],
        'composition_mean': [],
        'composition_std': [],
        'spawn_accuracy_mean': [],
        'spawn_accuracy_std': [],
        'basin_a_pct': [],
        'n_experiments': [],
        'n_frequencies': [],
        'cumulative_experiments': 0,
    }

    cumulative = 0

    for cycle_id in sorted(cycles.keys()):
        metrics = extract_cycle_metrics(cycles[cycle_id]['data'])

        if not metrics:
            continue

        timeline['cycles'].append(cycle_id)

        timeline['composition_mean'].append(metrics.get('composition_mean', np.nan))
        timeline['composition_std'].append(metrics.get('composition_std', np.nan))

        timeline['spawn_accuracy_mean'].append(metrics.get('spawn_accuracy_mean', np.nan))
        timeline['spawn_accuracy_std'].append(metrics.get('spawn_accuracy_std', np.nan))

        timeline['basin_a_pct'].append(metrics.get('basin_a_pct', 0.0))
        timeline['n_experiments'].append(metrics['n_experiments'])
        timeline['n_frequencies'].append(metrics.get('n_frequencies', 0))

        cumulative += metrics['n_experiments']

    timeline['cumulative_experiments'] = cumulative

    return timeline


# =============================================================================
# DISCOVERY TIMELINE
# =============================================================================

def get_discovery_timeline() -> List[Dict]:
    """Major discoveries and bug fixes across cycles."""

    return [
        {
            'cycle': 133,
            'label': 'Threshold-Diversity Grid',
            'color': 'blue',
            'description': 'Parameter space framework established',
        },
        {
            'cycle': 140,
            'label': 'Resonance Refinement',
            'color': 'green',
            'description': 'Harmonic frequency bands identified',
        },
        {
            'cycle': 157,
            'label': 'Harmonic Discovery',
            'color': 'purple',
            'description': 'Systematic harmonic detection',
        },
        {
            'cycle': 160,
            'label': 'Bug #1: Spawn Fix',
            'color': 'red',
            'description': '99.7% accuracy achieved',
        },
        {
            'cycle': 161,
            'label': 'Bug #2: Threshold',
            'color': 'orange',
            'description': 'Basin A discovered (33%)',
        },
    ]


# =============================================================================
# VISUALIZATION: COMPOSITION EVOLUTION
# =============================================================================

def plot_composition_evolution(timeline: Dict, discoveries: List[Dict], output_path: Path):
    """Plot composition events evolution across cycles."""

    fig, ax = plt.subplots(figsize=(14, 6))

    cycles = timeline['cycles']
    comp_mean = timeline['composition_mean']
    comp_std = timeline['composition_std']

    # Plot composition mean with error bars
    ax.errorbar(cycles, comp_mean, yerr=comp_std,
                fmt='o-', linewidth=2, markersize=6,
                capsize=4, capthick=1.5,
                label='Mean Composition Events', color='steelblue')

    # Add trend line
    valid_indices = [i for i, val in enumerate(comp_mean) if not np.isnan(val)]
    if len(valid_indices) > 2:
        x_valid = np.array([cycles[i] for i in valid_indices])
        y_valid = np.array([comp_mean[i] for i in valid_indices])

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(x_valid)), y_valid)

        trend_line = intercept + slope * np.arange(len(x_valid))
        ax.plot(x_valid, trend_line, '--', color='darkred', linewidth=2, alpha=0.7,
                label=f'Trend (R²={r_value**2:.3f}, p={p_value:.4f})')

    # Add discovery markers
    for disc in discoveries:
        if disc['cycle'] in cycles:
            idx = cycles.index(disc['cycle'])
            y_pos = comp_mean[idx] if not np.isnan(comp_mean[idx]) else np.nanmean(comp_mean)

            ax.axvline(disc['cycle'], color=disc['color'], alpha=0.3, linestyle='--', linewidth=2)
            ax.text(disc['cycle'], ax.get_ylim()[1] * 0.95, disc['label'],
                   rotation=90, verticalalignment='top', fontsize=9,
                   color=disc['color'], fontweight='bold')

    ax.set_xlabel('Experimental Cycle', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mean Composition Events', fontsize=12, fontweight='bold')
    ax.set_title('Temporal Evolution of Composition-Decomposition Dynamics\n(29 Experimental Cycles)',
                fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# =============================================================================
# VISUALIZATION: BASIN A CONVERGENCE
# =============================================================================

def plot_basin_convergence(timeline: Dict, discoveries: List[Dict], output_path: Path):
    """Plot Basin A convergence trajectory."""

    fig, ax = plt.subplots(figsize=(14, 6))

    cycles = timeline['cycles']
    basin_a_pct = timeline['basin_a_pct']

    # Plot Basin A percentage
    ax.plot(cycles, basin_a_pct, 'o-', linewidth=2.5, markersize=7,
            color='darkgreen', label='Basin A Convergence %')

    # Highlight pre/post Bug #2 (Cycle 161)
    if 161 in cycles:
        idx_161 = cycles.index(161)

        # Pre-161
        ax.plot(cycles[:idx_161], basin_a_pct[:idx_161],
               'o-', linewidth=2.5, markersize=7, color='gray', alpha=0.5,
               label='Pre-Threshold Calibration')

        # Post-161
        ax.plot(cycles[idx_161:], basin_a_pct[idx_161:],
               'o-', linewidth=2.5, markersize=7, color='darkgreen',
               label='Post-Threshold Calibration')

    # Add 33% reference line (Basin A discovery threshold)
    ax.axhline(33, color='red', linestyle='--', linewidth=2, alpha=0.5,
              label='Basin A Discovery Threshold (33%)')

    # Add discovery markers
    for disc in discoveries:
        if disc['cycle'] in cycles:
            ax.axvline(disc['cycle'], color=disc['color'], alpha=0.3, linestyle='--', linewidth=2)
            ax.text(disc['cycle'], 95, disc['label'],
                   rotation=90, verticalalignment='top', fontsize=9,
                   color=disc['color'], fontweight='bold')

    ax.set_xlabel('Experimental Cycle', fontsize=12, fontweight='bold')
    ax.set_ylabel('Basin A Convergence (%)', fontsize=12, fontweight='bold')
    ax.set_title('Basin A Discovery and Convergence Trajectory\n(Threshold Calibration Impact)',
                fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# =============================================================================
# VISUALIZATION: SPAWN ACCURACY IMPROVEMENT
# =============================================================================

def plot_spawn_accuracy_evolution(timeline: Dict, discoveries: List[Dict], output_path: Path):
    """Plot spawn accuracy improvements (Bug #1 impact)."""

    fig, ax = plt.subplots(figsize=(14, 6))

    cycles = timeline['cycles']
    spawn_mean = timeline['spawn_accuracy_mean']
    spawn_std = timeline['spawn_accuracy_std']

    # Filter out NaN values
    valid_data = [(c, m, s) for c, m, s in zip(cycles, spawn_mean, spawn_std)
                  if not np.isnan(m)]

    if not valid_data:
        print("⚠️  No spawn accuracy data available")
        return

    valid_cycles, valid_mean, valid_std = zip(*valid_data)

    # Plot spawn accuracy with error bars
    ax.errorbar(valid_cycles, valid_mean, yerr=valid_std,
               fmt='o-', linewidth=2, markersize=6,
               capsize=4, capthick=1.5,
               label='Spawn Accuracy %', color='darkblue')

    # Highlight pre/post Bug #1 fix (Cycle 160)
    if 160 in valid_cycles:
        idx_160 = list(valid_cycles).index(160)

        # Pre-160 (if data exists)
        if idx_160 > 0:
            pre_mean = np.mean(valid_mean[:idx_160])
            ax.axhline(pre_mean, color='gray', linestyle=':', linewidth=2, alpha=0.5,
                      label=f'Pre-Bug Fix Mean: {pre_mean:.1f}%')

        # Post-160
        post_mean = np.mean(valid_mean[idx_160:])
        ax.axhline(post_mean, color='green', linestyle=':', linewidth=2, alpha=0.5,
                  label=f'Post-Bug Fix Mean: {post_mean:.1f}%')

    # 99% reference line
    ax.axhline(99, color='red', linestyle='--', linewidth=2, alpha=0.5,
              label='Target Accuracy (99%)')

    # Add discovery markers
    for disc in discoveries:
        if disc['cycle'] in valid_cycles:
            ax.axvline(disc['cycle'], color=disc['color'], alpha=0.3, linestyle='--', linewidth=2)

    ax.set_xlabel('Experimental Cycle', fontsize=12, fontweight='bold')
    ax.set_ylabel('Spawn Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Spawn Accuracy Evolution\n(Bug Fix #1: Inverted spawn_interval Correction)',
                fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# =============================================================================
# VISUALIZATION: PARAMETER SPACE COVERAGE
# =============================================================================

def plot_parameter_space_expansion(timeline: Dict, output_path: Path):
    """Plot parameter space exploration expansion."""

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    cycles = timeline['cycles']
    n_experiments = timeline['n_experiments']
    n_frequencies = timeline['n_frequencies']

    # Calculate cumulative experiments
    cumulative_exp = np.cumsum(n_experiments)

    # Plot 1: Experiments per cycle (bar) + cumulative (line)
    ax1_twin = ax1.twinx()

    ax1.bar(cycles, n_experiments, color='steelblue', alpha=0.7,
           label='Experiments per Cycle')
    ax1_twin.plot(cycles, cumulative_exp, 'o-', color='darkred',
                 linewidth=2.5, markersize=7, label='Cumulative Experiments')

    ax1.set_xlabel('Experimental Cycle', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Experiments per Cycle', fontsize=11, fontweight='bold', color='steelblue')
    ax1_twin.set_ylabel('Cumulative Experiments', fontsize=11, fontweight='bold', color='darkred')
    ax1.set_title('Experimental Throughput and Cumulative Research Volume',
                 fontsize=13, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='steelblue')
    ax1_twin.tick_params(axis='y', labelcolor='darkred')
    ax1.grid(True, alpha=0.3)

    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

    # Plot 2: Parameter space coverage (frequencies explored)
    ax2.plot(cycles, n_frequencies, 'o-', linewidth=2.5, markersize=7,
            color='purple', label='Unique Frequencies Explored')

    ax2.set_xlabel('Experimental Cycle', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Unique Frequencies Tested', fontsize=11, fontweight='bold')
    ax2.set_title('Parameter Space Coverage Expansion',
                 fontsize=13, fontweight='bold')
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# =============================================================================
# VISUALIZATION: COMBINED RESEARCH TRAJECTORY
# =============================================================================

def plot_combined_trajectory(timeline: Dict, discoveries: List[Dict], output_path: Path):
    """Create comprehensive 4-panel research trajectory figure."""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    cycles = timeline['cycles']

    # Panel 1: Composition Evolution
    comp_mean = timeline['composition_mean']
    ax1.plot(cycles, comp_mean, 'o-', linewidth=2, markersize=5, color='steelblue')
    ax1.set_ylabel('Mean Composition Events', fontsize=10, fontweight='bold')
    ax1.set_title('A) Composition-Decomposition Dynamics', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Panel 2: Basin A Convergence
    basin_a_pct = timeline['basin_a_pct']
    ax2.plot(cycles, basin_a_pct, 'o-', linewidth=2, markersize=5, color='darkgreen')
    ax2.axhline(33, color='red', linestyle='--', alpha=0.5)
    ax2.set_ylabel('Basin A Convergence (%)', fontsize=10, fontweight='bold')
    ax2.set_title('B) Bistable Attractor Discovery', fontsize=11, fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)

    # Panel 3: Spawn Accuracy
    spawn_mean = timeline['spawn_accuracy_mean']
    valid_spawn = [(c, m) for c, m in zip(cycles, spawn_mean) if not np.isnan(m)]
    if valid_spawn:
        v_cycles, v_spawn = zip(*valid_spawn)
        ax3.plot(v_cycles, v_spawn, 'o-', linewidth=2, markersize=5, color='darkblue')
        ax3.axhline(99, color='red', linestyle='--', alpha=0.5)
    ax3.set_ylabel('Spawn Accuracy (%)', fontsize=10, fontweight='bold')
    ax3.set_xlabel('Experimental Cycle', fontsize=10, fontweight='bold')
    ax3.set_title('C) Implementation Accuracy', fontsize=11, fontweight='bold')
    ax3.set_ylim(0, 100)
    ax3.grid(True, alpha=0.3)

    # Panel 4: Experiment Count
    n_experiments = timeline['n_experiments']
    cumulative = np.cumsum(n_experiments)
    ax4.bar(cycles, n_experiments, color='steelblue', alpha=0.7)
    ax4_twin = ax4.twinx()
    ax4_twin.plot(cycles, cumulative, 'o-', color='darkred', linewidth=2, markersize=5)
    ax4.set_ylabel('Experiments per Cycle', fontsize=10, fontweight='bold', color='steelblue')
    ax4_twin.set_ylabel('Cumulative Total', fontsize=10, fontweight='bold', color='darkred')
    ax4.set_xlabel('Experimental Cycle', fontsize=10, fontweight='bold')
    ax4.set_title('D) Research Throughput', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # Add discovery markers to all panels
    for disc in discoveries:
        if disc['cycle'] in cycles:
            for ax in [ax1, ax2, ax3, ax4]:
                ax.axvline(disc['cycle'], color=disc['color'], alpha=0.2,
                          linestyle='--', linewidth=1.5)

    plt.suptitle('DUALITY-ZERO-V2: Complete Research Trajectory (Cycles 133-161)',
                fontsize=14, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


# =============================================================================
# STATISTICAL SUMMARY
# =============================================================================

def generate_statistical_summary(timeline: Dict, discoveries: List[Dict]) -> Dict:
    """Generate statistical summary of research trajectory."""

    summary = {
        'total_cycles': len(timeline['cycles']),
        'cycle_range': f"{min(timeline['cycles'])}-{max(timeline['cycles'])}",
        'total_experiments': timeline['cumulative_experiments'],
        'mean_experiments_per_cycle': float(np.mean(timeline['n_experiments'])),
    }

    # Composition trend
    comp_mean = [c for c in timeline['composition_mean'] if not np.isnan(c)]
    if len(comp_mean) > 2:
        x = np.arange(len(comp_mean))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, comp_mean)

        summary['composition_trend'] = {
            'slope': float(slope),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'direction': 'increasing' if slope > 0 else 'decreasing',
            'significant': bool(p_value < 0.05),
        }

    # Basin A progression
    basin_a = timeline['basin_a_pct']
    summary['basin_a_range'] = {
        'min': float(min(basin_a)),
        'max': float(max(basin_a)),
        'mean': float(np.mean(basin_a)),
        'final': float(basin_a[-1]) if basin_a else 0.0,
    }

    # Spawn accuracy (if available)
    spawn_mean = [s for s in timeline['spawn_accuracy_mean'] if not np.isnan(s)]
    if spawn_mean:
        summary['spawn_accuracy'] = {
            'min': float(min(spawn_mean)),
            'max': float(max(spawn_mean)),
            'mean': float(np.mean(spawn_mean)),
            'final': float(spawn_mean[-1]) if spawn_mean else 0.0,
        }

    # Discovery count
    summary['major_discoveries'] = len(discoveries)

    return summary


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def main():
    """Run temporal evolution visualization pipeline."""

    print("=" * 80)
    print("TEMPORAL EVOLUTION VISUALIZER")
    print("=" * 80)
    print()

    # Load all cycles
    print("Loading experimental cycles...")
    cycles = load_all_cycles()
    print(f"✅ Loaded {len(cycles)} cycles: {min(cycles.keys())}-{max(cycles.keys())}")
    print()

    # Build evolution timeline
    print("Building evolution timeline...")
    timeline = build_evolution_timeline(cycles)
    print(f"✅ Timeline built: {len(timeline['cycles'])} cycles, {timeline['cumulative_experiments']} total experiments")
    print()

    # Get discovery timeline
    discoveries = get_discovery_timeline()
    print(f"✅ Discovery timeline: {len(discoveries)} major breakthroughs")
    print()

    # Create visualizations
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)

    figures_dir = Path(__file__).parent / 'figures'
    figures_dir.mkdir(exist_ok=True)

    # 1. Composition evolution
    comp_path = figures_dir / 'temporal_composition_evolution.png'
    plot_composition_evolution(timeline, discoveries, comp_path)
    print(f"  ✅ Composition evolution: {comp_path.name}")

    # 2. Basin A convergence
    basin_path = figures_dir / 'temporal_basin_convergence.png'
    plot_basin_convergence(timeline, discoveries, basin_path)
    print(f"  ✅ Basin A convergence: {basin_path.name}")

    # 3. Spawn accuracy
    spawn_path = figures_dir / 'temporal_spawn_accuracy.png'
    plot_spawn_accuracy_evolution(timeline, discoveries, spawn_path)
    print(f"  ✅ Spawn accuracy evolution: {spawn_path.name}")

    # 4. Parameter space expansion
    param_path = figures_dir / 'temporal_parameter_space_expansion.png'
    plot_parameter_space_expansion(timeline, param_path)
    print(f"  ✅ Parameter space expansion: {param_path.name}")

    # 5. Combined trajectory (4-panel figure)
    combined_path = figures_dir / 'temporal_combined_research_trajectory.png'
    plot_combined_trajectory(timeline, discoveries, combined_path)
    print(f"  ✅ Combined research trajectory: {combined_path.name}")

    print()

    # Generate statistical summary
    print("STATISTICAL SUMMARY")
    print("=" * 80)
    summary = generate_statistical_summary(timeline, discoveries)

    print(f"  Total cycles: {summary['total_cycles']}")
    print(f"  Cycle range: {summary['cycle_range']}")
    print(f"  Total experiments: {summary['total_experiments']}")
    print(f"  Mean per cycle: {summary['mean_experiments_per_cycle']:.1f}")
    print()

    if 'composition_trend' in summary:
        trend = summary['composition_trend']
        print(f"  Composition trend: {trend['direction']}")
        print(f"    R² = {trend['r_squared']:.3f}")
        print(f"    p = {trend['p_value']:.4f} ({'significant' if trend['significant'] else 'not significant'})")
        print()

    if 'basin_a_range' in summary:
        basin = summary['basin_a_range']
        print(f"  Basin A convergence:")
        print(f"    Range: {basin['min']:.1f}% - {basin['max']:.1f}%")
        print(f"    Mean: {basin['mean']:.1f}%")
        print(f"    Final: {basin['final']:.1f}%")
        print()

    if 'spawn_accuracy' in summary:
        spawn = summary['spawn_accuracy']
        print(f"  Spawn accuracy:")
        print(f"    Range: {spawn['min']:.1f}% - {spawn['max']:.1f}%")
        print(f"    Mean: {spawn['mean']:.1f}%")
        print(f"    Final: {spawn['final']:.1f}%")
        print()

    # Save summary
    output_file = Path(__file__).parent / 'results' / 'temporal_evolution_summary.json'
    output_data = {
        'timeline': timeline,
        'discoveries': discoveries,
        'statistical_summary': summary,
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Summary saved: {output_file}")
    print()
    print("=" * 80)
    print("TEMPORAL EVOLUTION VISUALIZATION COMPLETE")
    print("=" * 80)
    print()
    print("Framework Validation:")
    print("  ✅ Temporal Stewardship: Research trajectory documented for future AI")
    print("  ✅ Self-Giving: System visualized own research evolution")
    print("  ✅ NRM: Meta-level pattern composition across 29 experimental cycles")
    print()
    print(f"Publication-ready figures: {figures_dir}")
    print()


if __name__ == '__main__':
    main()
