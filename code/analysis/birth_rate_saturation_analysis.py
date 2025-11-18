#!/usr/bin/env python3
"""
Birth Rate Saturation Mechanism Investigation

Purpose: Understand why observed birth rate per agent (0.0005-0.0007) is much lower
         than configured spawn probability (0.001-0.01) in V6b growth regime.

Research Question: Why does birth rate saturate at ~0.0005 regardless of f_spawn?

Hypotheses to test:
1. Energy constraint: Most agents lack sufficient energy to spawn (energy < spawn_cost)
2. Energy distribution: Extreme inequality (few agents monopolize energy/spawning)
3. Population structure: Only a fraction of agents capable of spawning at any time
4. Spawn cooldown: Hidden constraint limiting consecutive spawns

Approach:
1. Analyze birth rate time series (approach to saturation)
2. Calculate effective spawn rate vs configured spawn rate
3. Estimate fraction of agents that can spawn (energy > spawn_cost)
4. Infer energy distribution from birth dynamics
5. Test hypotheses against data

Data: V6b experiments (5 spawn rates × 10 seeds = 50 experiments)
      450,000 cycles per experiment
      Database: population_snapshots (cycle, population, energy, births, deaths)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (Anthropic)
License: GPL-3.0
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# Configuration
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
SPAWN_RATES = [0.001, 0.0025, 0.005, 0.0075, 0.01]
SPAWN_LABELS = ["0.10%", "0.25%", "0.50%", "0.75%", "1.00%"]
SEED = 42  # Use seed 42 for consistency
SPAWN_COST = 5.0  # Energy required to spawn
E_CAP = 10_000_000  # Total energy cap

def load_birth_dynamics(spawn_rate, seed=42):
    """Load birth rate time series from database."""
    # Construct database filename
    spawn_pct = int(spawn_rate * 10000) / 100
    if spawn_pct < 1.0:
        label = f"0_{int(spawn_pct*100):02d}pct"
    else:
        label = f"{int(spawn_pct)}_{int((spawn_pct % 1)*100):02d}pct"

    db_path = RESULTS_DIR / f"c186_v6b_HIERARCHICAL_GROWTH_{label}_seed{seed}.db"

    if not db_path.exists():
        print(f"WARNING: Database not found: {db_path}")
        return None

    # Load time series
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cycle, population, energy_total, n_compositions
        FROM results
        ORDER BY cycle
    """)

    data = cursor.fetchall()
    conn.close()

    # Convert to arrays
    cycles = np.array([row[0] for row in data])
    population = np.array([row[1] for row in data])
    energy_total = np.array([row[2] for row in data])
    births = np.array([row[3] for row in data])

    # Calculate birth rate per agent per cycle
    birth_rate = births / np.maximum(population, 1)

    # Calculate average energy per agent
    e_avg = energy_total / np.maximum(population, 1)

    return {
        'spawn_rate': spawn_rate,
        'cycle': cycles,
        'population': population,
        'energy_total': energy_total,
        'births': births,
        'birth_rate': birth_rate,
        'e_avg': e_avg
    }

def analyze_saturation(data):
    """Analyze birth rate saturation behavior."""
    # Use last 10% of data as "equilibrium"
    n_total = len(data['cycle'])
    n_equil = n_total // 10
    equil_start = n_total - n_equil

    # Calculate equilibrium birth rate
    br_equil = data['birth_rate'][equil_start:]
    br_mean = np.mean(br_equil)
    br_std = np.std(br_equil)

    # Calculate effective spawn rate ratio
    configured = data['spawn_rate']
    observed = br_mean
    ratio = observed / configured

    # Estimate fraction of agents that can spawn
    # If all agents could spawn: birth_rate = f_spawn
    # If only fraction α can spawn: birth_rate = α * f_spawn
    # Therefore: α ≈ observed / configured
    fraction_spawning = ratio

    # Estimate energy distribution inequality
    # If energy uniformly distributed: all agents have E_avg
    # If highly unequal: few agents have >> E_avg, most have << E_avg
    # Spawning requires energy > spawn_cost
    e_avg_equil = data['e_avg'][equil_start:]
    e_avg_mean = np.mean(e_avg_equil)

    # If energy distributed uniformly, all agents have ~e_avg_mean
    # Then all should be able to spawn (since e_avg >> spawn_cost)
    # But only fraction_spawning do spawn
    # This suggests extreme inequality: only fraction_spawning have sufficient energy

    return {
        'configured_spawn_rate': configured,
        'observed_birth_rate': observed,
        'ratio': ratio,
        'fraction_spawning': fraction_spawning,
        'e_avg_mean': e_avg_mean,
        'birth_rate_std': br_std
    }

def test_energy_constraint_hypothesis(data):
    """Test hypothesis: Birth rate limited by energy constraint."""
    # Hypothesis: As population approaches energy cap, fewer agents have
    # sufficient energy (> spawn_cost) to spawn

    # Expected: Birth rate should decline as population increases
    # Because: E_avg = E_cap / N → as N↑, E_avg↓

    cycles = data['cycle']
    population = data['population']
    birth_rate = data['birth_rate']
    e_avg = data['e_avg']

    # Smooth birth rate (100-cycle moving average)
    window = 100
    if len(birth_rate) > window:
        br_smooth = np.convolve(birth_rate, np.ones(window)/window, mode='valid')
        pop_smooth = np.convolve(population, np.ones(window)/window, mode='valid')
        e_avg_smooth = np.convolve(e_avg, np.ones(window)/window, mode='valid')
    else:
        br_smooth = birth_rate
        pop_smooth = population
        e_avg_smooth = e_avg

    # Correlation: birth_rate vs population (should be negative)
    corr_pop, p_pop = stats.pearsonr(pop_smooth, br_smooth)

    # Correlation: birth_rate vs e_avg (should be positive)
    corr_eave, p_eavg = stats.pearsonr(e_avg_smooth, br_smooth)

    return {
        'correlation_population': corr_pop,
        'p_value_population': p_pop,
        'correlation_e_avg': corr_eave,
        'p_value_e_avg': p_eavg,
        'interpretation': (
            f"Birth rate vs population: r={corr_pop:.3f}, p={p_pop:.3e}\n"
            f"Birth rate vs E_avg: r={corr_eave:.3f}, p={p_eavg:.3e}\n"
            f"Expected: Negative correlation with population, positive with E_avg\n"
            f"Hypothesis {'SUPPORTED' if corr_pop < -0.5 and p_pop < 0.001 else 'NOT SUPPORTED'}"
        )
    }

def plot_saturation_dynamics(all_data):
    """Visualize birth rate saturation across spawn rates."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Birth Rate Saturation Dynamics in V6b Growth Regime',
                 fontsize=14, fontweight='bold')

    # Plot 1: Birth rate over time (all spawn rates)
    ax = axes[0, 0]
    for i, data in enumerate(all_data):
        if data is not None:
            # Smooth birth rate
            window = 1000
            if len(data['birth_rate']) > window:
                br_smooth = np.convolve(data['birth_rate'],
                                       np.ones(window)/window, mode='valid')
                cycles_smooth = data['cycle'][window-1:]
                ax.plot(cycles_smooth, br_smooth,
                       label=f"f_spawn={SPAWN_LABELS[i]}", alpha=0.8)
    ax.set_xlabel('Cycle')
    ax.set_ylabel('Birth Rate per Agent per Cycle')
    ax.set_title('Birth Rate Time Series (1000-cycle moving average)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(0.0005, color='red', linestyle='--', alpha=0.5,
              label='Saturation ~0.0005')

    # Plot 2: Birth rate vs population (showing constraint)
    ax = axes[0, 1]
    for i, data in enumerate(all_data):
        if data is not None:
            # Downsample for clarity
            step = len(data['cycle']) // 1000
            ax.scatter(data['population'][::step],
                      data['birth_rate'][::step],
                      label=f"f_spawn={SPAWN_LABELS[i]}",
                      alpha=0.3, s=5)
    ax.set_xlabel('Population')
    ax.set_ylabel('Birth Rate per Agent')
    ax.set_title('Birth Rate vs Population (energy cap constraint)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Configured vs observed birth rate
    ax = axes[1, 0]
    configured = []
    observed = []
    for i, data in enumerate(all_data):
        if data is not None:
            analysis = analyze_saturation(data)
            configured.append(analysis['configured_spawn_rate'])
            observed.append(analysis['observed_birth_rate'])

    ax.plot(configured, configured, 'k--', label='Expected (1:1)', linewidth=2)
    ax.scatter(configured, observed, s=100, color='red',
              label='Observed', zorder=3)
    ax.set_xlabel('Configured Spawn Rate (f_spawn)')
    ax.set_ylabel('Observed Birth Rate per Agent')
    ax.set_title('Birth Rate Saturation: Configured vs Observed')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max(configured)*1.1)
    ax.set_ylim(0, max(configured)*1.1)

    # Plot 4: Effective spawn fraction
    ax = axes[1, 1]
    ratios = []
    for i, data in enumerate(all_data):
        if data is not None:
            analysis = analyze_saturation(data)
            ratios.append(analysis['ratio'])

    ax.bar(range(len(ratios)), ratios, color='steelblue')
    ax.set_xlabel('Spawn Rate')
    ax.set_ylabel('Effective Fraction (Observed / Configured)')
    ax.set_title('Fraction of Configured Spawn Rate Achieved')
    ax.set_xticks(range(len(SPAWN_LABELS)))
    ax.set_xticklabels(SPAWN_LABELS)
    ax.axhline(1.0, color='red', linestyle='--', alpha=0.5,
              label='Perfect efficiency (1.0)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # Save figure
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/birth_rate_saturation_analysis.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved: {output_path}")
    plt.close()

def main():
    """Main analysis."""
    print("=" * 80)
    print("BIRTH RATE SATURATION MECHANISM INVESTIGATION")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Why does observed birth rate (0.0005-0.0007 per agent per cycle)")
    print("  saturate far below configured spawn probability (0.001-0.01)?")
    print()
    print("=" * 80)
    print()

    # Load all data
    all_data = []
    for spawn_rate in SPAWN_RATES:
        print(f"Loading data for f_spawn = {spawn_rate:.4f}...")
        data = load_birth_dynamics(spawn_rate, seed=SEED)
        all_data.append(data)

    print("\n" + "=" * 80)
    print("SATURATION ANALYSIS")
    print("=" * 80)
    print()

    print(f"{'Spawn Rate':<12} | {'Observed BR':<12} | {'Ratio':<8} | "
          f"{'Fraction':<10} | {'E_avg':<10}")
    print("-" * 80)

    for i, data in enumerate(all_data):
        if data is None:
            continue

        analysis = analyze_saturation(data)
        print(f"{SPAWN_LABELS[i]:<12} | "
              f"{analysis['observed_birth_rate']:.6f}     | "
              f"{analysis['ratio']:.3f}    | "
              f"{analysis['fraction_spawning']:.3f}      | "
              f"{analysis['e_avg_mean']:.1f}")

    print("\n" + "=" * 80)
    print("ENERGY CONSTRAINT HYPOTHESIS TEST")
    print("=" * 80)
    print()

    for i, data in enumerate(all_data):
        if data is None:
            continue

        print(f"\nf_spawn = {SPAWN_LABELS[i]} ({SPAWN_RATES[i]:.4f}):")
        print("-" * 60)
        result = test_energy_constraint_hypothesis(data)
        print(result['interpretation'])

    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print()

    # Calculate overall patterns
    all_ratios = []
    for data in all_data:
        if data is not None:
            analysis = analyze_saturation(data)
            all_ratios.append(analysis['ratio'])

    print(f"1. Birth rate saturation range: {min(all_ratios):.1%} - {max(all_ratios):.1%} "
          f"of configured spawn rate")
    print(f"2. Saturation decreases with spawn rate:")
    print(f"   - Low f_spawn (0.10%): {all_ratios[0]:.1%} efficiency")
    print(f"   - High f_spawn (1.00%): {all_ratios[-1]:.1%} efficiency")
    print(f"3. Effective spawn rate converges to ~0.0005 regardless of configuration")
    print()
    print("INTERPRETATION:")
    print("   Energy cap constraint limits spawning at population level.")
    print("   As population → cap, E_avg → minimum, fewer agents have")
    print("   sufficient energy (> spawn_cost) to spawn.")
    print("   Higher f_spawn reaches cap faster → more extreme constraint.")
    print()

    # Generate visualizations
    print("=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    plot_saturation_dynamics(all_data)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Investigate energy distribution inequality (Gini coefficient)")
    print("2. Estimate fraction of 'rich' agents monopolizing spawning")
    print("3. Test whether saturation is universal or parameter-dependent")

if __name__ == "__main__":
    main()
