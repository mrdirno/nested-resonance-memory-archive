#!/usr/bin/env python3
"""
Investigate Agent-Level Energy Dynamics in V6b Growth Regime

Purpose: Understand why E_avg shows exponential decay with f_spawn
         when mechanistic model predicts hyperbolic (1/f_spawn).

Approach:
1. Extract E_avg time series for all spawn rates
2. Analyze equilibrium E_avg values
3. Infer age distribution from birth/death dynamics
4. Test theoretical predictions

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (Anthropic)
License: GPL-3.0
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuration
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
SPAWN_RATES = [0.001, 0.0025, 0.005, 0.0075, 0.01]
SPAWN_LABELS = ["0.10%", "0.25%", "0.50%", "0.75%", "1.00%"]
SEED = 42  # Use seed 42 for consistency

def load_timeseries(spawn_rate, seed=42):
    """Load time series data from database."""
    # Construct filename
    spawn_pct = int(spawn_rate * 10000) / 100  # Convert to percentage
    if spawn_pct < 1.0:
        label = f"0_{int(spawn_pct*100):02d}pct"
    else:
        label = f"{int(spawn_pct)}_{int((spawn_pct % 1)*100):02d}pct"

    db_path = RESULTS_DIR / f"c186_v6b_HIERARCHICAL_GROWTH_{label}_seed{seed}.db"

    if not db_path.exists():
        print(f"WARNING: Database not found: {db_path}")
        return None

    # Load data
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cycle, population, energy_total, n_compositions, n_decompositions
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
    deaths = np.array([row[4] for row in data])

    # Calculate E_avg
    e_avg = energy_total / np.maximum(population, 1)  # Avoid division by zero

    return {
        'cycle': cycles,
        'population': population,
        'energy_total': energy_total,
        'e_avg': e_avg,
        'births': births,
        'deaths': deaths,
        'spawn_rate': spawn_rate
    }

def analyze_equilibrium(data):
    """Analyze equilibrium properties."""
    # Use last 10% of data as equilibrium
    n_total = len(data['cycle'])
    n_equil = n_total // 10

    equil_start = n_total - n_equil

    e_avg_equil = data['e_avg'][equil_start:]
    pop_equil = data['population'][equil_start:]
    births_equil = data['births'][equil_start:]
    deaths_equil = data['deaths'][equil_start:]

    results = {
        'e_avg_mean': np.mean(e_avg_equil),
        'e_avg_std': np.std(e_avg_equil),
        'population_mean': np.mean(pop_equil),
        'population_std': np.std(pop_equil),
        'birth_rate_mean': np.mean(births_equil),
        'death_rate_mean': np.mean(deaths_equil),
        'net_rate': np.mean(births_equil) - np.mean(deaths_equil)
    }

    return results

def infer_age_distribution(data):
    """Infer age distribution properties from birth/death dynamics."""
    # In equilibrium (growth cap), birth rate ≈ death rate
    # Average age can be estimated from turnover rate

    equil = analyze_equilibrium(data)

    # Birth rate per agent per cycle
    birth_rate_per_agent = equil['birth_rate_mean'] / equil['population_mean']

    # Death rate per agent per cycle
    death_rate_per_agent = equil['death_rate_mean'] / equil['population_mean']

    # In stationary population, average age ≈ 1 / death_rate
    # (This is for exponential age distribution)
    if death_rate_per_agent > 0:
        avg_age_exponential = 1.0 / death_rate_per_agent
    else:
        avg_age_exponential = np.inf

    return {
        'birth_rate_per_agent': birth_rate_per_agent,
        'death_rate_per_agent': death_rate_per_agent,
        'avg_age_exponential_model': avg_age_exponential
    }

def plot_timeseries(all_data):
    """Plot time series for all spawn rates."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('V6b Growth Regime: Time Series Analysis', fontsize=14, fontweight='bold')

    # Plot 1: Population over time
    ax = axes[0, 0]
    for i, data in enumerate(all_data):
        if data is not None:
            ax.plot(data['cycle'], data['population'],
                   label=f"f_spawn={SPAWN_LABELS[i]}", alpha=0.8)
    ax.set_xlabel('Cycle')
    ax.set_ylabel('Population')
    ax.set_title('Population Growth')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: E_avg over time
    ax = axes[0, 1]
    for i, data in enumerate(all_data):
        if data is not None:
            ax.plot(data['cycle'], data['e_avg'],
                   label=f"f_spawn={SPAWN_LABELS[i]}", alpha=0.8)
    ax.set_xlabel('Cycle')
    ax.set_ylabel('E_avg (energy per agent)')
    ax.set_title('Average Energy per Agent')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(500, color='red', linestyle='--', alpha=0.5, label='E_min=500')

    # Plot 3: Birth rate over time
    ax = axes[1, 0]
    for i, data in enumerate(all_data):
        if data is not None:
            # Calculate cumulative births
            cum_births = np.cumsum(data['births'])
            ax.plot(data['cycle'], cum_births,
                   label=f"f_spawn={SPAWN_LABELS[i]}", alpha=0.8)
    ax.set_xlabel('Cycle')
    ax.set_ylabel('Cumulative Births')
    ax.set_title('Composition Dynamics')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 4: Birth rate per agent (instantaneous)
    ax = axes[1, 1]
    for i, data in enumerate(all_data):
        if data is not None:
            # Birth rate per agent
            birth_rate_per_agent = data['births'] / np.maximum(data['population'], 1)
            # Smooth with moving average
            window = 100
            if len(birth_rate_per_agent) > window:
                smoothed = np.convolve(birth_rate_per_agent,
                                      np.ones(window)/window, mode='valid')
                ax.plot(data['cycle'][window-1:], smoothed,
                       label=f"f_spawn={SPAWN_LABELS[i]}", alpha=0.8)
    ax.set_xlabel('Cycle')
    ax.set_ylabel('Birth Rate per Agent per Cycle')
    ax.set_title('Per-Agent Birth Rate (smoothed)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/v6b_energy_dynamics_investigation.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved: {output_path}")

    plt.close()

def main():
    """Main analysis."""
    print("=" * 70)
    print("INVESTIGATING ENERGY DYNAMICS IN V6B GROWTH REGIME")
    print("=" * 70)
    print()
    print("Research Question:")
    print("  Why does E_avg show exponential decay with f_spawn")
    print("  when mechanistic theory predicts hyperbolic (1/f_spawn)?")
    print()
    print("=" * 70)
    print()

    # Load all data
    all_data = []
    for spawn_rate in SPAWN_RATES:
        print(f"Loading data for f_spawn = {spawn_rate:.4f}...")
        data = load_timeseries(spawn_rate, seed=SEED)
        all_data.append(data)

    print("\n" + "=" * 70)
    print("EQUILIBRIUM ANALYSIS")
    print("=" * 70)
    print()

    # Analyze equilibrium for each spawn rate
    results_table = []
    for i, data in enumerate(all_data):
        if data is None:
            continue

        equil = analyze_equilibrium(data)
        age_dist = infer_age_distribution(data)

        print(f"f_spawn = {SPAWN_LABELS[i]} ({SPAWN_RATES[i]:.4f})")
        print(f"  Population: {equil['population_mean']:.1f} ± {equil['population_std']:.1f}")
        print(f"  E_avg: {equil['e_avg_mean']:.2f} ± {equil['e_avg_std']:.2f}")
        print(f"  Birth rate: {equil['birth_rate_mean']:.2f}/cycle")
        print(f"  Death rate: {equil['death_rate_mean']:.2f}/cycle")
        print(f"  Net rate: {equil['net_rate']:.2f}/cycle")
        print(f"  Birth rate per agent: {age_dist['birth_rate_per_agent']:.6f}")
        print(f"  Death rate per agent: {age_dist['death_rate_per_agent']:.6f}")
        print(f"  Avg age (exponential model): {age_dist['avg_age_exponential_model']:.1f} cycles")
        print()

        results_table.append({
            'f_spawn': SPAWN_RATES[i],
            'label': SPAWN_LABELS[i],
            'e_avg': equil['e_avg_mean'],
            'population': equil['population_mean'],
            'birth_rate_per_agent': age_dist['birth_rate_per_agent'],
            'avg_age': age_dist['avg_age_exponential_model']
        })

    # Test theoretical predictions
    print("=" * 70)
    print("THEORETICAL PREDICTION TESTS")
    print("=" * 70)
    print()

    print("Hypothesis 1: Age distribution is exponential with λ = f_spawn")
    print("  If true, then avg_age ≈ 1 / f_spawn")
    print()
    print("f_spawn | Observed avg_age | Predicted (1/f_spawn) | Ratio")
    print("--------|------------------|------------------------|-------")
    for r in results_table:
        predicted_age = 1.0 / r['f_spawn']
        ratio = r['avg_age'] / predicted_age
        print(f"{r['f_spawn']:.4f}  | {r['avg_age']:16.1f} | {predicted_age:22.1f} | {ratio:.3f}")
    print()

    print("Hypothesis 2: Birth rate per agent = f_spawn")
    print("  (Spawn rate should match configured probability)")
    print()
    print("f_spawn | Observed birth rate | Ratio (obs/expected)")
    print("--------|---------------------|----------------------")
    for r in results_table:
        ratio = r['birth_rate_per_agent'] / r['f_spawn']
        print(f"{r['f_spawn']:.4f}  | {r['birth_rate_per_agent']:19.6f} | {ratio:.3f}")
    print()

    print("Hypothesis 3: E_avg = E_min + r / f_spawn (hyperbolic)")
    print("  Fitting r from first two data points:")
    if len(results_table) >= 2:
        e0 = results_table[0]['e_avg']
        e1 = results_table[1]['e_avg']
        f0 = results_table[0]['f_spawn']
        f1 = results_table[1]['f_spawn']
        E_min = 500  # Assumed

        # Solve for r:
        # e0 = E_min + r / f0
        # e1 = E_min + r / f1
        # e0 - e1 = r * (1/f0 - 1/f1)
        r = (e0 - e1) / (1/f0 - 1/f1)

        print(f"  Fitted r = {r:.2f}")
        print(f"  E_min = {E_min}")
        print()
        print("f_spawn | E_avg observed | E_avg predicted (hyperbolic) | Error")
        print("--------|----------------|------------------------------|-------")
        for res in results_table:
            predicted = E_min + r / res['f_spawn']
            error = abs(predicted - res['e_avg']) / res['e_avg'] * 100
            print(f"{res['f_spawn']:.4f}  | {res['e_avg']:14.2f} | {predicted:28.2f} | {error:5.1f}%")
        print()

    print("Hypothesis 4: E_avg = E_min + A * exp(-B * f_spawn) (exponential)")
    print("  Using fitted parameters: A=141.1, B=564.3, E_min=500")
    print()
    A = 141.1
    B = 564.3
    E_min = 500
    print("f_spawn | E_avg observed | E_avg predicted (exponential) | Error")
    print("--------|----------------|-------------------------------|-------")
    for res in results_table:
        predicted = E_min + A * np.exp(-B * res['f_spawn'])
        error = abs(predicted - res['e_avg']) / res['e_avg'] * 100
        print(f"{res['f_spawn']:.4f}  | {res['e_avg']:14.2f} | {predicted:29.2f} | {error:5.1f}%")
    print()

    # Plot time series
    print("=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    plot_timeseries(all_data)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
