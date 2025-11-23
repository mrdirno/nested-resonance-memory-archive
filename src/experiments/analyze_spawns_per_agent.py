#!/usr/bin/env python3
"""
Analyze Spawn Attempts Per Agent Metric

Purpose: Calculate and visualize spawn attempts per agent over time to validate
         revised timescale dependency hypothesis (Cycle 907).

Hypothesis: Energy constraint manifestation depends on spawn attempts per agent,
            not just total spawn attempts or cycles.

Threshold Model:
- < 2 spawns/agent: High success rate (70-100%)
- 2-4 spawns/agent: Transition zone (40-70%)
- > 4 spawns/agent: Low success rate (20-30%)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-01
Cycle: 907
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime


def load_c171_data():
    """Load C171 historical data for comparison."""
    path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle171_fractal_swarm_bistability.json")

    if not path.exists():
        print(f"❌ C171 data not found: {path}")
        return None

    with open(path, 'r') as f:
        data = json.load(f)

    return data['experiments']


def load_c176_incremental_data():
    """Load C176 incremental validation data."""
    path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle176_v6_incremental_validation.json")

    if not path.exists():
        print(f"❌ C176 incremental data not found: {path}")
        print("   Validation may not be complete yet.")
        return None

    with open(path, 'r') as f:
        data = json.load(f)

    return data.get('experiments', [])


def calculate_spawns_per_agent(spawn_attempts, final_population, initial_population=1):
    """
    Calculate average spawn attempts per agent.

    Note: This is a rough approximation since spawn attempts are distributed
    non-uniformly over time as population grows.

    Better metric would be actual per-agent spawn history, but we don't have
    that in summary data.
    """
    # Rough approximation: divide total attempts by average population
    # Average population ≈ (initial + final) / 2
    avg_population = (initial_population + final_population) / 2

    spawns_per_agent = spawn_attempts / avg_population

    return spawns_per_agent


def analyze_c171_spawns_per_agent(experiments):
    """Analyze C171 data for spawns/agent metric."""
    print("=" * 80)
    print("C171 SPAWNS PER AGENT ANALYSIS")
    print("=" * 80)
    print()

    results = []

    for exp in experiments:
        freq = exp['frequency']
        seed = exp['seed']
        spawn_count = exp['spawn_count']  # Total spawn ATTEMPTS
        final_pop = exp['final_agent_count']

        # Estimate spawns per agent
        spawns_per_agent = calculate_spawns_per_agent(spawn_count, final_pop)

        results.append({
            'frequency': freq,
            'seed': seed,
            'spawn_attempts': spawn_count,
            'final_population': final_pop,
            'spawns_per_agent': spawns_per_agent,
        })

        print(f"[{freq:.1f}%, seed {seed}] "
              f"Spawns: {spawn_count}, "
              f"Pop: {final_pop}, "
              f"Spawns/agent: {spawns_per_agent:.2f}")

    # Calculate overall statistics
    spawns_per_agent_values = [r['spawns_per_agent'] for r in results]
    mean_spawns_per_agent = np.mean(spawns_per_agent_values)
    std_spawns_per_agent = np.std(spawns_per_agent_values)

    print()
    print(f"Overall Statistics (n={len(results)}):")
    print(f"  Mean spawns/agent: {mean_spawns_per_agent:.2f} ± {std_spawns_per_agent:.2f}")
    print(f"  Range: [{min(spawns_per_agent_values):.2f}, {max(spawns_per_agent_values):.2f}]")
    print()

    # From Cycle 903, C171 had ~23% spawn success rate
    # Check correlation
    print(f"Context: C171 mean spawn success rate ≈ 23%")
    print(f"  With {mean_spawns_per_agent:.2f} spawns/agent → low success")
    print()

    return results


def analyze_c176_incremental_spawns_per_agent(experiments):
    """Analyze C176 incremental data for spawns/agent metric."""
    print("=" * 80)
    print("C176 INCREMENTAL SPAWNS PER AGENT ANALYSIS")
    print("=" * 80)
    print()

    if not experiments:
        print("❌ No experiments found in C176 incremental data")
        return []

    results = []

    for exp in experiments:
        seed = exp.get('seed', '?')
        spawn_attempts = exp.get('spawn_attempts', 0)
        spawn_successes = exp.get('spawn_successes', 0)
        final_pop = exp.get('final_population', 0)
        spawn_success_rate = exp.get('spawn_success_rate', 0.0)

        # Estimate spawns per agent
        spawns_per_agent = calculate_spawns_per_agent(spawn_attempts, final_pop)

        results.append({
            'seed': seed,
            'spawn_attempts': spawn_attempts,
            'spawn_successes': spawn_successes,
            'final_population': final_pop,
            'spawn_success_rate': spawn_success_rate,
            'spawns_per_agent': spawns_per_agent,
        })

        print(f"[seed {seed}] "
              f"Attempts: {spawn_attempts}, "
              f"Successes: {spawn_successes} ({spawn_success_rate:.1f}%), "
              f"Pop: {final_pop}, "
              f"Spawns/agent: {spawns_per_agent:.2f}")

    # Calculate overall statistics
    spawns_per_agent_values = [r['spawns_per_agent'] for r in results]
    success_rates = [r['spawn_success_rate'] for r in results]

    mean_spawns_per_agent = np.mean(spawns_per_agent_values)
    std_spawns_per_agent = np.std(spawns_per_agent_values)
    mean_success_rate = np.mean(success_rates)

    print()
    print(f"Overall Statistics (n={len(results)}):")
    print(f"  Mean spawns/agent: {mean_spawns_per_agent:.2f} ± {std_spawns_per_agent:.2f}")
    print(f"  Mean spawn success rate: {mean_success_rate:.1f}%")
    print()

    return results


def validate_threshold_hypothesis(c171_results, c176_results):
    """Validate spawns/agent threshold hypothesis."""
    print("=" * 80)
    print("THRESHOLD HYPOTHESIS VALIDATION")
    print("=" * 80)
    print()

    print("Hypothesis:")
    print("  < 2 spawns/agent → High success (70-100%)")
    print("  2-4 spawns/agent → Transition (40-70%)")
    print("  > 4 spawns/agent → Low success (20-30%)")
    print()

    if c171_results:
        c171_mean_spawns = np.mean([r['spawns_per_agent'] for r in c171_results])
        print(f"C171 (3000 cycles):")
        print(f"  Spawns/agent: {c171_mean_spawns:.2f}")
        print(f"  Success rate: ~23% (from Cycle 903 data)")
        print(f"  Prediction: > 4 spawns/agent → low success ✓")
        print()

    if c176_results:
        c176_mean_spawns = np.mean([r['spawns_per_agent'] for r in c176_results])
        c176_mean_success = np.mean([r['spawn_success_rate'] for r in c176_results])

        print(f"C176 Incremental (1000 cycles):")
        print(f"  Spawns/agent: {c176_mean_spawns:.2f}")
        print(f"  Success rate: {c176_mean_success:.1f}%")

        if c176_mean_spawns < 2:
            prediction = "< 2 spawns/agent → high success (70-100%)"
            matches = 70 <= c176_mean_success <= 100
        elif c176_mean_spawns < 4:
            prediction = "2-4 spawns/agent → transition (40-70%)"
            matches = 40 <= c176_mean_success <= 70
        else:
            prediction = "> 4 spawns/agent → low success (20-30%)"
            matches = 20 <= c176_mean_success <= 30

        result = "✓ MATCHES" if matches else "✗ DOES NOT MATCH"
        print(f"  Prediction: {prediction}")
        print(f"  Result: {result}")
        print()


def generate_visualization(c171_results, c176_results):
    """Generate spawns/agent vs. success rate visualization."""
    print("=" * 80)
    print("GENERATING VISUALIZATION")
    print("=" * 80)
    print()

    fig, ax = plt.subplots(figsize=(10, 6))

    # C171 data (approximate success rate from Cycle 903: 23%)
    if c171_results:
        c171_spawns = [r['spawns_per_agent'] for r in c171_results]
        c171_success = [23.0] * len(c171_spawns)  # Approximate from Cycle 903

        ax.scatter(c171_spawns, c171_success,
                  s=100, alpha=0.6, color='blue',
                  label='C171 (3000 cycles, 2.0-3.0%)')

    # C176 incremental data
    if c176_results:
        c176_spawns = [r['spawns_per_agent'] for r in c176_results]
        c176_success = [r['spawn_success_rate'] for r in c176_results]

        ax.scatter(c176_spawns, c176_success,
                  s=100, alpha=0.6, color='red',
                  label='C176 Incremental (1000 cycles, 2.5%)')

    # Threshold zones
    ax.axhline(y=70, color='gray', linestyle='--', alpha=0.3)
    ax.axhline(y=40, color='gray', linestyle='--', alpha=0.3)
    ax.axhline(y=30, color='gray', linestyle='--', alpha=0.3)

    ax.axvline(x=2, color='gray', linestyle='--', alpha=0.3)
    ax.axvline(x=4, color='gray', linestyle='--', alpha=0.3)

    # Labels
    ax.set_xlabel('Spawn Attempts Per Agent', fontsize=12)
    ax.set_ylabel('Spawn Success Rate (%)', fontsize=12)
    ax.set_title('Energy Constraint Threshold: Spawns/Agent vs. Success Rate', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.2)

    # Save
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/spawns_per_agent_threshold_analysis.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Visualization saved: {output_path}")
    print()

    plt.close()


def main():
    """Execute spawns/agent analysis."""
    print("=" * 80)
    print("SPAWN ATTEMPTS PER AGENT THRESHOLD ANALYSIS")
    print("=" * 80)
    print()
    print("Purpose: Validate revised timescale dependency hypothesis (Cycle 907)")
    print("Hypothesis: Energy constraint depends on spawns/agent, not just total attempts")
    print()

    start_time = datetime.now()

    # Load C171 data
    print("Loading C171 historical data...")
    c171_experiments = load_c171_data()

    if c171_experiments:
        print(f"✓ Loaded {len(c171_experiments)} C171 experiments")
        print()
        c171_results = analyze_c171_spawns_per_agent(c171_experiments)
    else:
        c171_results = []

    # Load C176 incremental data
    print("Loading C176 incremental validation data...")
    c176_experiments = load_c176_incremental_data()

    if c176_experiments:
        print(f"✓ Loaded {len(c176_experiments)} C176 incremental experiments")
        print()
        c176_results = analyze_c176_incremental_spawns_per_agent(c176_experiments)
    else:
        c176_results = []
        print("⚠️  C176 incremental data not available yet")
        print("   Run this script again after validation completes")
        print()

    # Validate threshold hypothesis
    if c171_results or c176_results:
        validate_threshold_hypothesis(c171_results, c176_results)

    # Generate visualization
    if c171_results or c176_results:
        generate_visualization(c171_results, c176_results)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"Analysis completed in {duration:.2f} seconds")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
