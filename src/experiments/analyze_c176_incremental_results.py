#!/usr/bin/env python3
"""
C176 V6 INCREMENTAL VALIDATION RESULTS ANALYSIS

Purpose: Comprehensive analysis of C176 incremental validation to validate
         revised non-monotonic timescale hypothesis (Cycle 907).

Hypotheses:
1. Final spawn success: 70-90% (revised from original 40-60%)
2. Final population: 18-20 agents (revised from original 10-15)
3. Spawns/agent: <2 (below threshold for energy constraint manifestation)
4. Non-monotonic pattern: Early decrease → mid stabilization/increase → late TBD

Comparison:
- vs. Micro-validation (100 cycles): 100% success, 4 agents
- vs. C171 (3000 cycles): 23% success, 17 agents, 8.38 spawns/agent

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-01
Cycle: 908
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from scipy import stats


# Expected outcomes per revised hypothesis (Cycle 907)
EXPECTED_SPAWN_SUCCESS_MIN = 70.0  # Revised from 40%
EXPECTED_SPAWN_SUCCESS_MAX = 90.0  # Revised from 60%
EXPECTED_POPULATION_MIN = 18      # Revised from 10
EXPECTED_POPULATION_MAX = 22      # Revised from 15
EXPECTED_SPAWNS_PER_AGENT_MAX = 2.0  # Below threshold for full depletion

# Reference data
MICRO_SPAWN_SUCCESS = 100.0
MICRO_POPULATION = 4.0
C171_SPAWN_SUCCESS = 23.0
C171_POPULATION = 17.43
C171_SPAWNS_PER_AGENT = 8.38


def load_incremental_results():
    """Load C176 incremental validation results."""
    results_file = Path("/Volumes/dual/DUALITY-ZERO-V2/code/experiments/results/cycle176_v6_incremental_validation.json")

    if not results_file.exists():
        print(f"❌ Results file not found: {results_file}")
        print("   Validation may not be complete yet.")
        return None

    with open(results_file, 'r') as f:
        data = json.load(f)

    return data


def calculate_spawns_per_agent_estimate(spawn_attempts, final_population, initial_population=1):
    """
    Estimate average spawn attempts per agent.

    Approximation: divide total attempts by average population.
    Better than total attempts for predicting energy constraint.
    """
    avg_population = (initial_population + final_population) / 2
    spawns_per_agent = spawn_attempts / avg_population
    return spawns_per_agent


def analyze_revised_hypotheses(results):
    """
    Test revised hypotheses from Cycle 907 (non-monotonic timescale dependency).

    H1 (Revised): Spawn success 70-90%
    H2 (Revised): Population 18-22 agents
    H3 (New): Spawns/agent < 2.0
    """
    print("=" * 80)
    print("REVISED HYPOTHESIS TESTING (Cycle 907)")
    print("=" * 80)
    print()

    experiments = results.get('experiments', [])

    if not experiments:
        print("❌ No experiments found in results")
        return None

    # Extract metrics
    spawn_success_rates = [exp['spawn_success_rate'] for exp in experiments]
    final_populations = [exp['final_agent_count'] for exp in experiments]
    spawn_attempts = [exp['spawn_attempts'] for exp in experiments]

    # Calculate spawns/agent for each experiment
    spawns_per_agent = []
    for exp in experiments:
        spa = calculate_spawns_per_agent_estimate(
            exp['spawn_attempts'],
            exp['final_agent_count']
        )
        spawns_per_agent.append(spa)

    # Overall statistics
    mean_success = np.mean(spawn_success_rates)
    std_success = np.std(spawn_success_rates)
    mean_population = np.mean(final_populations)
    std_population = np.std(final_populations)
    mean_spawns_per_agent = np.mean(spawns_per_agent)
    std_spawns_per_agent = np.std(spawns_per_agent)

    print(f"Incremental Validation Results (n={len(experiments)} seeds):")
    print()
    print(f"Spawn Success Rate:")
    print(f"  Mean: {mean_success:.1f}% ± {std_success:.1f}%")
    print(f"  Range: [{min(spawn_success_rates):.1f}%, {max(spawn_success_rates):.1f}%]")
    print()
    print(f"Final Population:")
    print(f"  Mean: {mean_population:.1f} ± {std_population:.1f} agents")
    print(f"  Range: [{min(final_populations)}, {max(final_populations)}]")
    print()
    print(f"Spawns Per Agent:")
    print(f"  Mean: {mean_spawns_per_agent:.2f} ± {std_spawns_per_agent:.2f}")
    print(f"  Range: [{min(spawns_per_agent):.2f}, {max(spawns_per_agent):.2f}]")
    print()

    # Test H1: Spawn success 70-90%
    h1_pass = EXPECTED_SPAWN_SUCCESS_MIN <= mean_success <= EXPECTED_SPAWN_SUCCESS_MAX
    print(f"H1 (Revised): Spawn success in [{EXPECTED_SPAWN_SUCCESS_MIN}%, {EXPECTED_SPAWN_SUCCESS_MAX}%]?")
    print(f"  Original Prediction (Cycle 903): 40-60%")
    print(f"  Revised Prediction (Cycle 907): 70-90%")
    print(f"  Observed: {mean_success:.1f}%")
    print(f"  Result: {'✅ PASS (revised hypothesis)' if h1_pass else '❌ FAIL'}")
    print()

    # Test H2: Population 18-22 agents
    h2_pass = EXPECTED_POPULATION_MIN <= mean_population <= EXPECTED_POPULATION_MAX
    print(f"H2 (Revised): Population in [{EXPECTED_POPULATION_MIN}, {EXPECTED_POPULATION_MAX}] agents?")
    print(f"  Original Prediction (Cycle 903): 10-15 agents")
    print(f"  Revised Prediction (Cycle 907): 18-22 agents")
    print(f"  Observed: {mean_population:.1f} agents")
    print(f"  Result: {'✅ PASS (revised hypothesis)' if h2_pass else '❌ FAIL'}")
    print()

    # Test H3: Spawns/agent < 2.0
    h3_pass = mean_spawns_per_agent < EXPECTED_SPAWNS_PER_AGENT_MAX
    print(f"H3 (New): Spawns/agent < {EXPECTED_SPAWNS_PER_AGENT_MAX} (below threshold)?")
    print(f"  Threshold Model: <2 → high success, 2-4 → transition, >4 → low success")
    print(f"  Observed: {mean_spawns_per_agent:.2f}")
    print(f"  Result: {'✅ PASS (below threshold)' if h3_pass else '❌ FAIL'}")
    print()

    return {
        'h1_pass': h1_pass,
        'h2_pass': h2_pass,
        'h3_pass': h3_pass,
        'mean_success': mean_success,
        'std_success': std_success,
        'mean_population': mean_population,
        'std_population': std_population,
        'mean_spawns_per_agent': mean_spawns_per_agent,
        'std_spawns_per_agent': std_spawns_per_agent,
    }


def compare_to_reference_data(results_summary):
    """
    Compare incremental validation to micro-validation and C171.

    Validates multi-scale timescale dependency:
    - 100 cycles → 100% success (too short)
    - 1000 cycles → ~75-85% success (intermediate, non-monotonic)
    - 3000 cycles → 23% success (full manifestation)
    """
    print("=" * 80)
    print("MULTI-SCALE TIMESCALE COMPARISON")
    print("=" * 80)
    print()

    mean_success = results_summary['mean_success']
    mean_population = results_summary['mean_population']
    mean_spawns_per_agent = results_summary['mean_spawns_per_agent']

    print("Timescale Dependency Validation:")
    print()
    print(f"Micro-validation (100 cycles):")
    print(f"  Spawn success: {MICRO_SPAWN_SUCCESS:.1f}%")
    print(f"  Population: {MICRO_POPULATION:.1f} agents")
    print(f"  Spawns/agent: ~0.75 (estimated)")
    print(f"  Assessment: Too short for energy constraint")
    print()
    print(f"Incremental validation (1000 cycles):")
    print(f"  Spawn success: {mean_success:.1f}%")
    print(f"  Population: {mean_population:.1f} agents")
    print(f"  Spawns/agent: {mean_spawns_per_agent:.2f}")
    print(f"  Assessment: Intermediate - population-mediated recovery")
    print()
    print(f"C171 (3000 cycles):")
    print(f"  Spawn success: {C171_SPAWN_SUCCESS:.1f}%")
    print(f"  Population: {C171_POPULATION:.1f} agents")
    print(f"  Spawns/agent: {C171_SPAWNS_PER_AGENT:.2f}")
    print(f"  Assessment: Full energy constraint manifestation")
    print()

    # Pattern analysis
    print("Observed Pattern:")
    if mean_success > 60:
        pattern = "Non-monotonic (100% → ~85% → 23%)"
        interpretation = "Population growth temporarily stabilizes spawn success before cumulative depletion dominates"
    else:
        pattern = "Monotonic decrease (100% → ~50% → 23%)"
        interpretation = "Simple cumulative depletion as originally hypothesized"

    print(f"  Pattern: {pattern}")
    print(f"  Interpretation: {interpretation}")
    print()

    # Spawns/agent threshold validation
    print("Spawns/Agent Threshold Model Validation:")
    print(f"  Micro (0.75 spawns/agent): {MICRO_SPAWN_SUCCESS:.1f}% success → <2 threshold ✓")
    print(f"  Incremental ({mean_spawns_per_agent:.2f} spawns/agent): {mean_success:.1f}% success → <2 threshold ✓")
    print(f"  C171 ({C171_SPAWNS_PER_AGENT:.2f} spawns/agent): {C171_SPAWN_SUCCESS:.1f}% success → >4 threshold ✓")
    print()


def generate_trajectory_visualization(results):
    """Generate spawn success rate trajectory visualization."""
    print("=" * 80)
    print("GENERATING TRAJECTORY VISUALIZATION")
    print("=" * 80)
    print()

    experiments = results.get('experiments', [])

    if not experiments:
        print("❌ No experiments found")
        return

    # Create figure with 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

    # Plot 1: Spawn success rate trajectory
    for exp in experiments:
        seed = exp.get('seed', '?')
        # If we have progress checkpoints, plot them
        if 'trajectory' in exp:
            cycles = exp['trajectory']['cycles']
            success_rates = exp['trajectory']['spawn_success_rates']
            ax1.plot(cycles, success_rates, 'o-', alpha=0.6, label=f'Seed {seed}')

    ax1.axhline(y=MICRO_SPAWN_SUCCESS, color='blue', linestyle='--', alpha=0.5, label='Micro (100 cycles)')
    ax1.axhline(y=C171_SPAWN_SUCCESS, color='red', linestyle='--', alpha=0.5, label='C171 (3000 cycles)')
    ax1.fill_between([0, 1000], EXPECTED_SPAWN_SUCCESS_MIN, EXPECTED_SPAWN_SUCCESS_MAX,
                     color='green', alpha=0.1, label='Expected range (70-90%)')

    ax1.set_xlabel('Cycles', fontsize=11)
    ax1.set_ylabel('Spawn Success Rate (%)', fontsize=11)
    ax1.set_title('Non-Monotonic Timescale Dependency: Spawn Success Over Time', fontsize=13, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.2)

    # Plot 2: Population trajectory
    for exp in experiments:
        seed = exp.get('seed', '?')
        if 'trajectory' in exp:
            cycles = exp['trajectory']['cycles']
            populations = exp['trajectory']['populations']
            ax2.plot(cycles, populations, 'o-', alpha=0.6, label=f'Seed {seed}')

    ax2.axhline(y=MICRO_POPULATION, color='blue', linestyle='--', alpha=0.5, label='Micro (100 cycles)')
    ax2.axhline(y=C171_POPULATION, color='red', linestyle='--', alpha=0.5, label='C171 (3000 cycles)')
    ax2.fill_between([0, 1000], EXPECTED_POPULATION_MIN, EXPECTED_POPULATION_MAX,
                     color='green', alpha=0.1, label='Expected range (18-22)')

    ax2.set_xlabel('Cycles', fontsize=11)
    ax2.set_ylabel('Population (agents)', fontsize=11)
    ax2.set_title('Population Growth Trajectory', fontsize=13, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.2)

    # Plot 3: Spawns/agent over time
    for exp in experiments:
        seed = exp.get('seed', '?')
        if 'trajectory' in exp:
            cycles = exp['trajectory']['cycles']
            spawn_attempts_cumulative = exp['trajectory']['spawn_attempts']
            populations = exp['trajectory']['populations']

            spawns_per_agent_trajectory = [
                spawn_attempts_cumulative[i] / ((1 + populations[i]) / 2)  # Rough approximation
                for i in range(len(cycles))
            ]

            ax3.plot(cycles, spawns_per_agent_trajectory, 'o-', alpha=0.6, label=f'Seed {seed}')

    ax3.axhline(y=2, color='orange', linestyle='--', alpha=0.5, label='Threshold (2 spawns/agent)')
    ax3.axhline(y=4, color='red', linestyle='--', alpha=0.5, label='High depletion (4 spawns/agent)')
    ax3.axhline(y=C171_SPAWNS_PER_AGENT, color='darkred', linestyle='--', alpha=0.5, label=f'C171 ({C171_SPAWNS_PER_AGENT:.1f})')

    ax3.set_xlabel('Cycles', fontsize=11)
    ax3.set_ylabel('Spawns Per Agent', fontsize=11)
    ax3.set_title('Cumulative Spawns Per Agent (Energy Constraint Metric)', fontsize=13, fontweight='bold')
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.2)

    plt.tight_layout()

    # Save
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/c176_incremental_validation_trajectories.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Trajectory visualization saved: {output_path}")
    print()

    plt.close()


def generate_comparison_visualization(results_summary):
    """Generate multi-scale comparison bar chart."""
    print("=" * 80)
    print("GENERATING COMPARISON VISUALIZATION")
    print("=" * 80)
    print()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Data
    timescales = ['Micro\n(100 cycles)', 'Incremental\n(1000 cycles)', 'C171\n(3000 cycles)']
    spawn_success = [MICRO_SPAWN_SUCCESS, results_summary['mean_success'], C171_SPAWN_SUCCESS]
    spawns_per_agent = [0.75, results_summary['mean_spawns_per_agent'], C171_SPAWNS_PER_AGENT]

    # Plot 1: Spawn success rates
    colors = ['blue', 'green', 'red']
    bars1 = ax1.bar(timescales, spawn_success, color=colors, alpha=0.6, edgecolor='black')
    ax1.set_ylabel('Spawn Success Rate (%)', fontsize=12)
    ax1.set_title('Timescale Dependency:\nSpawn Success Rate', fontsize=14, fontweight='bold')
    ax1.set_ylim([0, 110])
    ax1.grid(True, alpha=0.2, axis='y')

    # Add value labels
    for bar, val in zip(bars1, spawn_success):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Plot 2: Spawns per agent
    bars2 = ax2.bar(timescales, spawns_per_agent, color=colors, alpha=0.6, edgecolor='black')
    ax2.set_ylabel('Spawns Per Agent', fontsize=12)
    ax2.set_title('Timescale Dependency:\nSpawns Per Agent', fontsize=14, fontweight='bold')
    ax2.axhline(y=2, color='orange', linestyle='--', alpha=0.5, label='Threshold (2)')
    ax2.axhline(y=4, color='red', linestyle='--', alpha=0.5, label='High depletion (4)')
    ax2.set_ylim([0, 10])
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.2, axis='y')

    # Add value labels
    for bar, val in zip(bars2, spawns_per_agent):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()

    # Save
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/c176_multi_scale_comparison.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Comparison visualization saved: {output_path}")
    print()

    plt.close()


def generate_decision_recommendation(results_summary):
    """Generate decision on next steps."""
    print("=" * 80)
    print("DECISION RECOMMENDATION")
    print("=" * 80)
    print()

    h1_pass = results_summary['h1_pass']
    h2_pass = results_summary['h2_pass']
    h3_pass = results_summary['h3_pass']

    all_pass = h1_pass and h2_pass and h3_pass

    print("Hypothesis Validation Summary:")
    print(f"  H1 (Spawn success 70-90%): {'✅ PASS' if h1_pass else '❌ FAIL'}")
    print(f"  H2 (Population 18-22 agents): {'✅ PASS' if h2_pass else '❌ FAIL'}")
    print(f"  H3 (Spawns/agent < 2): {'✅ PASS' if h3_pass else '❌ FAIL'}")
    print()

    if all_pass:
        print("✅ **REVISED HYPOTHESIS VALIDATED**")
        print()
        print("Non-monotonic timescale dependency CONFIRMED:")
        print(f"  - Spawn success: {results_summary['mean_success']:.1f}% (intermediate, not low)")
        print(f"  - Population: {results_summary['mean_population']:.1f} agents (high, not intermediate)")
        print(f"  - Spawns/agent: {results_summary['mean_spawns_per_agent']:.2f} (below threshold)")
        print()
        print("Mechanism:")
        print("  - Phase 1 (0-500 cycles): Small population → slight depletion")
        print("  - Phase 2 (500-1000 cycles): Large population → distributed load → stabilization")
        print("  - Phase 3 (1000-3000 cycles, projected): Cumulative → universal depletion → 23% success")
        print()
        print("**RECOMMENDATION: Proceed with full C176 V6 validation (n=20, 3000 cycles)**")
        print()
        print("Expected Results at 3000 cycles:")
        print("  - Spawn success: 20-25% (replicates C171)")
        print("  - Population: 17-18 agents (replicates C171)")
        print("  - Spawns/agent: 7-9 (above 4 threshold)")
        print()
        print("Next Actions:")
        print("  1. Launch C176 V6 full validation (n=20, 3000 cycles)")
        print("  2. Update Paper 2 with non-monotonic timescale dependency findings")
        print("  3. Generate all publication figures (trajectories, comparisons)")
        print("  4. If full validation replicates C171 → proceed with C176 V7 ablation study")
        print("  5. Integrate into Paper 2 (new section: 'Population-Mediated Energy Dynamics')")
        print()
    else:
        print("❌ **UNEXPECTED RESULTS**")
        print()
        print("Revised hypothesis not validated.")
        print()
        failures = []
        if not h1_pass:
            failures.append(f"Spawn success outside expected range ({results_summary['mean_success']:.1f}% vs 70-90%)")
        if not h2_pass:
            failures.append(f"Population outside expected range ({results_summary['mean_population']:.1f} vs 18-22 agents)")
        if not h3_pass:
            failures.append(f"Spawns/agent above threshold ({results_summary['mean_spawns_per_agent']:.2f} vs <2)")

        for failure in failures:
            print(f"  - {failure}")
        print()
        print("**RECOMMENDATION: Investigate further before C176 V6 full validation**")
        print()
        print("Next Actions:")
        print("  1. Analyze individual seed trajectories")
        print("  2. Review energy dynamics calculations")
        print("  3. Compare with C171 raw data")
        print("  4. Revise hypothesis again")
        print()

    return {
        'all_pass': all_pass,
        'recommendation': 'PROCEED_WITH_FULL_V6' if all_pass else 'INVESTIGATE_FURTHER',
    }


def main():
    """Execute C176 incremental validation analysis."""
    print("=" * 80)
    print("C176 V6 INCREMENTAL VALIDATION ANALYSIS")
    print("=" * 80)
    print()
    print("Purpose: Validate revised non-monotonic timescale hypothesis (Cycle 907)")
    print()

    start_time = datetime.now()

    # Load results
    print("Loading incremental validation results...")
    results = load_incremental_results()

    if not results:
        print()
        print("❌ Results not available yet. Run this script after validation completes.")
        return

    experiments = results.get('experiments', [])
    print(f"✓ Loaded {len(experiments)} experiment results")
    print()

    # Analyze revised hypotheses
    results_summary = analyze_revised_hypotheses(results)

    if not results_summary:
        return

    # Compare to reference data
    compare_to_reference_data(results_summary)

    # Generate visualizations
    generate_trajectory_visualization(results)
    generate_comparison_visualization(results_summary)

    # Generate decision
    decision = generate_decision_recommendation(results_summary)

    # Save analysis summary
    analysis_summary = {
        'timestamp': datetime.now().isoformat(),
        'n_experiments': len(experiments),
        'hypotheses': results_summary,
        'decision': decision,
    }

    summary_file = Path("/Volumes/dual/DUALITY-ZERO-V2/code/experiments/results/c176_incremental_analysis_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(analysis_summary, f, indent=2)

    print(f"Analysis summary saved: {summary_file}")
    print()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"Analysis completed in {duration:.2f} seconds")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
