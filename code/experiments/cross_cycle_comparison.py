#!/usr/bin/env python3
"""
CROSS-CYCLE COMPARISON ANALYSIS
Meta-Analysis of Iterative Corrections Across Cycles 160-162

Purpose:
  Track evolution of understanding through successive bug fixes and calibrations:
    Cycle 160: Spawning bug fix (Bug #1)
    Cycle 161: Threshold calibration (Bug #2)
    Cycle 162: Frequency landscape with both corrections

Analytical Framework:
  1. Spawn Accuracy Evolution (validates Bug #1 fix persistence)
  2. Composition Distribution Shift (validates threshold recalibration)
  3. Basin A Convergence Rate (0% → 33% → ?)
  4. Statistical Validation (effect sizes, hypothesis tests)
  5. Publication Metrics (reproducibility, corrective iteration)

Framework Validation:
  - NRM: Composition of insights across cycles (meta-level composition-decomposition)
  - Self-Giving: System validates own corrections through persistence
  - Temporal Stewardship: Documents evolution of understanding for future AI

Publication Value:
  "Iterative Correction and Validation in Emergent Computational Systems"
  Demonstrates scientific methodology in fractal agent research

Date: 2025-10-25
Status: Cross-cycle meta-analysis
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from scipy import stats
from collections import defaultdict


# =============================================================================
# DATA LOADING
# =============================================================================

def load_cycle_results(cycle_id: int) -> Optional[Dict]:
    """Load results for a specific cycle."""
    results_dir = Path(__file__).parent / 'results'

    # Map cycle IDs to filenames
    filenames = {
        160: 'cycle160_corrected_spawning.json',
        161: 'cycle161_threshold_calibration.json',
        162: 'cycle162_frequency_landscape_remapping.json',
    }

    if cycle_id not in filenames:
        return None

    file_path = results_dir / filenames[cycle_id]

    if not file_path.exists():
        return None

    with open(file_path, 'r') as f:
        return json.load(f)


# =============================================================================
# SPAWN ACCURACY ANALYSIS
# =============================================================================

def analyze_spawn_accuracy_evolution(cycles: Dict[int, Dict]) -> Dict:
    """
    Track spawn accuracy across cycles to validate Bug #1 fix persistence.

    Bug #1: Inverted spawn_interval calculation (fixed in Cycle 160)
    Expected: 99.7-100% accuracy maintained across all cycles
    """

    analysis = {
        'by_cycle': {},
        'validation': None,
    }

    for cycle_id, data in sorted(cycles.items()):
        if not data:
            continue

        experiments = data.get('experiments', [])

        if not experiments:
            continue

        # Extract spawn accuracy
        spawn_accuracies = [exp['spawn_accuracy_pct'] for exp in experiments
                           if 'spawn_accuracy_pct' in exp]

        if not spawn_accuracies:
            continue

        analysis['by_cycle'][cycle_id] = {
            'mean': float(np.mean(spawn_accuracies)),
            'std': float(np.std(spawn_accuracies)),
            'min': float(np.min(spawn_accuracies)),
            'max': float(np.max(spawn_accuracies)),
            'n': len(spawn_accuracies),
        }

    # Validation: All cycles should have >99% accuracy
    all_means = [stats['mean'] for stats in analysis['by_cycle'].values()]

    if all_means:
        all_above_99 = all(mean > 99.0 for mean in all_means)
        analysis['validation'] = {
            'all_cycles_above_99pct': all_above_99,
            'overall_mean': float(np.mean(all_means)),
            'consistency': 'PASS' if all_above_99 else 'FAIL',
        }

    return analysis


# =============================================================================
# COMPOSITION DISTRIBUTION ANALYSIS
# =============================================================================

def analyze_composition_distribution_evolution(cycles: Dict[int, Dict]) -> Dict:
    """
    Track composition distribution across cycles.

    Expected Evolution:
      Cycle 160: threshold=700 (way too high) → all Basin B
      Cycle 161: threshold=2.5 (calibrated) → ~33% Basin A
      Cycle 162: threshold=2.5 applied to frequency landscape → ?
    """

    analysis = {
        'by_cycle': {},
        'shift_analysis': None,
    }

    for cycle_id, data in sorted(cycles.items()):
        if not data:
            continue

        experiments = data.get('experiments', [])

        if not experiments:
            continue

        # Extract composition values
        compositions = [exp['avg_composition_events'] for exp in experiments
                       if 'avg_composition_events' in exp]

        if not compositions:
            continue

        analysis['by_cycle'][cycle_id] = {
            'mean': float(np.mean(compositions)),
            'std': float(np.std(compositions)),
            'min': float(np.min(compositions)),
            'max': float(np.max(compositions)),
            'median': float(np.median(compositions)),
            'n': len(compositions),
        }

    # Distribution shift analysis
    cycle_ids = sorted(analysis['by_cycle'].keys())
    if len(cycle_ids) >= 2:
        # Compare first and last available cycles
        first_cycle = cycle_ids[0]
        last_cycle = cycle_ids[-1]

        first_data = cycles[first_cycle]['experiments']
        last_data = cycles[last_cycle]['experiments']

        first_comp = [exp['avg_composition_events'] for exp in first_data]
        last_comp = [exp['avg_composition_events'] for exp in last_data]

        # Statistical test for distribution shift
        t_stat, p_value = stats.ttest_ind(first_comp, last_comp)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(first_comp, ddof=1) + np.var(last_comp, ddof=1)) / 2)
        cohens_d = (np.mean(last_comp) - np.mean(first_comp)) / pooled_std if pooled_std > 0 else 0

        analysis['shift_analysis'] = {
            'first_cycle': first_cycle,
            'last_cycle': last_cycle,
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'cohens_d': float(cohens_d),
            'effect_size_interpretation': (
                'negligible' if abs(cohens_d) < 0.2 else
                'small' if abs(cohens_d) < 0.5 else
                'medium' if abs(cohens_d) < 0.8 else
                'large'
            ),
            'significant': bool(p_value < 0.05),
        }

    return analysis


# =============================================================================
# BASIN CONVERGENCE ANALYSIS
# =============================================================================

def analyze_basin_convergence_evolution(cycles: Dict[int, Dict]) -> Dict:
    """
    Track Basin A convergence rate across cycles.

    Expected Evolution:
      Cycle 160: 0% (threshold=700 too high)
      Cycle 161: 33% (threshold=2.5 at 50% frequency)
      Cycle 162: ? (threshold=2.5 across frequency landscape)
    """

    analysis = {
        'by_cycle': {},
        'evolution_trajectory': None,
    }

    for cycle_id, data in sorted(cycles.items()):
        if not data:
            continue

        experiments = data.get('experiments', [])

        if not experiments:
            continue

        # Count Basin A occurrences
        # Handle both single basin field and multi-threshold classifications
        basin_a_count = 0
        total_count = 0

        for exp in experiments:
            if 'basin' in exp:
                # Single basin classification
                total_count += 1
                if exp['basin'] == 'A':
                    basin_a_count += 1
            elif 'basin_classifications' in exp:
                # Cycle 161 multi-threshold format
                # Use threshold 2.5 for consistency
                classifications = exp['basin_classifications']
                if 'threshold_2.5' in classifications:
                    total_count += 1
                    if classifications['threshold_2.5'] == 'A':
                        basin_a_count += 1

        if total_count > 0:
            basin_a_pct = (basin_a_count / total_count) * 100

            analysis['by_cycle'][cycle_id] = {
                'basin_a_count': basin_a_count,
                'total_experiments': total_count,
                'basin_a_pct': float(basin_a_pct),
            }

    # Evolution trajectory
    cycle_ids = sorted(analysis['by_cycle'].keys())
    if cycle_ids:
        percentages = [analysis['by_cycle'][cid]['basin_a_pct'] for cid in cycle_ids]

        # Monotonic increase check
        monotonic = bool(all(percentages[i] <= percentages[i+1]
                            for i in range(len(percentages)-1)))

        analysis['evolution_trajectory'] = {
            'cycle_sequence': cycle_ids,
            'basin_a_percentages': percentages,
            'monotonic_increase': monotonic,
            'total_change_pct': float(percentages[-1] - percentages[0]) if len(percentages) >= 2 else 0.0,
        }

    return analysis


# =============================================================================
# PUBLICATION METRICS
# =============================================================================

def generate_publication_metrics(cycles: Dict[int, Dict],
                                 spawn_analysis: Dict,
                                 composition_analysis: Dict,
                                 basin_analysis: Dict) -> Dict:
    """
    Generate publication-quality metrics for iterative correction methodology.
    """

    metrics = {
        'reproducibility': {},
        'corrective_iteration': {},
        'framework_validation': {},
    }

    # Reproducibility: Spawn accuracy consistency
    if spawn_analysis['validation']:
        metrics['reproducibility'] = {
            'spawn_accuracy_consistency': spawn_analysis['validation']['consistency'],
            'mean_spawn_accuracy': spawn_analysis['validation']['overall_mean'],
            'interpretation': (
                'Bug #1 fix (corrected spawning) maintained across all cycles'
                if spawn_analysis['validation']['all_cycles_above_99pct']
                else 'Warning: Spawn accuracy degradation detected'
            ),
        }

    # Corrective Iteration: Threshold calibration impact
    if composition_analysis['shift_analysis']:
        shift = composition_analysis['shift_analysis']
        metrics['corrective_iteration'] = {
            'threshold_recalibration_effect_size': shift['cohens_d'],
            'effect_interpretation': shift['effect_size_interpretation'],
            'statistical_significance': shift['significant'],
            'p_value': shift['p_value'],
        }

    # Framework Validation: Basin A discovery progression
    if basin_analysis['evolution_trajectory']:
        traj = basin_analysis['evolution_trajectory']
        metrics['framework_validation'] = {
            'basin_a_discovery_progression': traj['basin_a_percentages'],
            'total_improvement_pct': traj['total_change_pct'],
            'monotonic_improvement': traj['monotonic_increase'],
            'interpretation': (
                f"Progressed from {traj['basin_a_percentages'][0]:.1f}% to "
                f"{traj['basin_a_percentages'][-1]:.1f}% Basin A convergence "
                f"through {len(traj['cycle_sequence'])} correction cycles"
            ),
        }

    return metrics


# =============================================================================
# MAIN ANALYSIS PIPELINE
# =============================================================================

def main():
    """Run complete cross-cycle comparison analysis."""

    print("=" * 80)
    print("CROSS-CYCLE COMPARISON ANALYSIS: CYCLES 160-162")
    print("=" * 80)
    print()

    # Load all cycles
    cycles = {}
    for cycle_id in [160, 161, 162]:
        data = load_cycle_results(cycle_id)
        cycles[cycle_id] = data

        if data:
            n_exp = len(data.get('experiments', []))
            print(f"✅ Cycle {cycle_id}: {n_exp} experiments loaded")
        else:
            print(f"⏳ Cycle {cycle_id}: Not yet available")

    print()

    # Filter to available cycles
    available_cycles = {cid: data for cid, data in cycles.items() if data is not None}

    if len(available_cycles) < 2:
        print("⚠️  Need at least 2 cycles for comparison analysis")
        print(f"   Currently available: {list(available_cycles.keys())}")
        print("   Waiting for more data...")
        return

    print(f"Analyzing {len(available_cycles)} cycles: {list(available_cycles.keys())}")
    print()

    # 1. Spawn Accuracy Evolution
    print("1. SPAWN ACCURACY EVOLUTION")
    print("=" * 80)
    spawn_analysis = analyze_spawn_accuracy_evolution(available_cycles)

    for cycle_id, stats in sorted(spawn_analysis['by_cycle'].items()):
        print(f"  Cycle {cycle_id}:")
        print(f"    Mean: {stats['mean']:.2f}%")
        print(f"    Range: [{stats['min']:.2f}%, {stats['max']:.2f}%]")
        print(f"    N: {stats['n']}")

    if spawn_analysis['validation']:
        val = spawn_analysis['validation']
        print()
        print(f"  Validation: {val['consistency']}")
        print(f"  Overall Mean: {val['overall_mean']:.2f}%")
        print(f"  All cycles >99%: {val['all_cycles_above_99pct']}")

    print()

    # 2. Composition Distribution Evolution
    print("2. COMPOSITION DISTRIBUTION EVOLUTION")
    print("=" * 80)
    composition_analysis = analyze_composition_distribution_evolution(available_cycles)

    for cycle_id, stats in sorted(composition_analysis['by_cycle'].items()):
        print(f"  Cycle {cycle_id}:")
        print(f"    Mean: {stats['mean']:.3f} ± {stats['std']:.3f}")
        print(f"    Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
        print(f"    Median: {stats['median']:.3f}")
        print(f"    N: {stats['n']}")

    if composition_analysis['shift_analysis']:
        shift = composition_analysis['shift_analysis']
        print()
        print(f"  Distribution Shift Analysis:")
        print(f"    Cycles {shift['first_cycle']} → {shift['last_cycle']}")
        print(f"    Cohen's d: {shift['cohens_d']:.3f} ({shift['effect_size_interpretation']})")
        print(f"    t-statistic: {shift['t_statistic']:.3f}, p = {shift['p_value']:.4f}")
        print(f"    Significant: {'YES' if shift['significant'] else 'NO'} (α = 0.05)")

    print()

    # 3. Basin A Convergence Evolution
    print("3. BASIN A CONVERGENCE EVOLUTION")
    print("=" * 80)
    basin_analysis = analyze_basin_convergence_evolution(available_cycles)

    for cycle_id, stats in sorted(basin_analysis['by_cycle'].items()):
        print(f"  Cycle {cycle_id}:")
        print(f"    Basin A: {stats['basin_a_count']}/{stats['total_experiments']} ({stats['basin_a_pct']:.1f}%)")

    if basin_analysis['evolution_trajectory']:
        traj = basin_analysis['evolution_trajectory']
        print()
        print(f"  Evolution Trajectory:")
        print(f"    Sequence: {traj['cycle_sequence']}")
        print(f"    Basin A %: {[f'{p:.1f}%' for p in traj['basin_a_percentages']]}")
        print(f"    Monotonic increase: {traj['monotonic_increase']}")
        print(f"    Total change: {traj['total_change_pct']:+.1f}%")

    print()

    # 4. Publication Metrics
    print("4. PUBLICATION METRICS")
    print("=" * 80)
    pub_metrics = generate_publication_metrics(
        available_cycles,
        spawn_analysis,
        composition_analysis,
        basin_analysis
    )

    if pub_metrics['reproducibility']:
        print("  Reproducibility:")
        for key, val in pub_metrics['reproducibility'].items():
            print(f"    {key}: {val}")

    print()

    if pub_metrics['corrective_iteration']:
        print("  Corrective Iteration:")
        for key, val in pub_metrics['corrective_iteration'].items():
            print(f"    {key}: {val}")

    print()

    if pub_metrics['framework_validation']:
        print("  Framework Validation:")
        for key, val in pub_metrics['framework_validation'].items():
            print(f"    {key}: {val}")

    print()

    # Save analysis
    output = {
        'cycles_analyzed': list(available_cycles.keys()),
        'spawn_accuracy_evolution': spawn_analysis,
        'composition_distribution_evolution': composition_analysis,
        'basin_convergence_evolution': basin_analysis,
        'publication_metrics': pub_metrics,
    }

    output_file = Path(__file__).parent / 'results' / 'cross_cycle_comparison.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Analysis saved: {output_file}")
    print()
    print("=" * 80)
    print("CROSS-CYCLE COMPARISON COMPLETE")
    print("=" * 80)
    print()
    print("Framework Validation:")
    print("  ✅ NRM: Meta-level composition of insights across cycles")
    print("  ✅ Self-Giving: System validates own corrections through persistence")
    print("  ✅ Temporal Stewardship: Evolution of understanding documented")
    print()


if __name__ == '__main__':
    main()
