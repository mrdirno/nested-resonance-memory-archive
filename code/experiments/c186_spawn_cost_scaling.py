#!/usr/bin/env python3
"""
C186 Spawn Cost Scaling Validation Experiment

Purpose: Test buffer factor k ≈ 95 universality hypothesis across spawn_cost values.

Hypothesis: E_min = k × spawn_cost where k ≈ 94.69 (universal constant)

Predictions:
- spawn_cost = 2.5 → E_min ≈ 237 units, K ≈ 42,194 agents
- spawn_cost = 5.0 → E_min ≈ 473 units, K ≈ 21,097 agents (baseline, validated)
- spawn_cost = 7.5 → E_min ≈ 710 units, K ≈ 14,065 agents
- spawn_cost = 10.0 → E_min ≈ 947 units, K ≈ 10,549 agents

Expected Results:
- k ≈ 95 ± 5 across all spawn_cost values (CV < 0.1)
- E_min linear scaling: R² > 0.99 for E_min vs spawn_cost
- K_equilibrium inverse scaling: K = E_cap / E_min

Experimental Design:
- Conditions: 4 spawn_cost values (2.5, 5.0, 7.5, 10.0)
- Seeds: 42-51 (10 replicates per condition)
- Total: 40 experiments
- Duration: 450,000 cycles per experiment (~20 seconds each)
- Total runtime: ~13 minutes

Validation Criteria:
- CV(k) < 0.1 across spawn_cost values → Hypothesis SUPPORTED
- R²(E_min vs spawn_cost) > 0.99 → Linear scaling VALIDATED
- All k within 95 ± 10 → Universal buffer factor CONFIRMED

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (Anthropic)
License: GPL-3.0
"""

import sys
import time
import sqlite3
import json
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from core.agent import Agent
from core.world import World

# Configuration
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
SPAWN_COSTS = [2.5, 5.0, 7.5, 10.0]
SEEDS = list(range(42, 52))  # Seeds 42-51 (10 replicates)
CYCLES = 450_000
SAVE_INTERVAL = 100_000

# Fixed parameters (V6b growth regime)
E_PRODUCE = 1.0
E_CONSUME = 0.5
E_NET = E_PRODUCE - E_CONSUME  # +0.5 (growth regime)
E_CAP = 10_000_000
F_SPAWN = 0.005  # Mid-range spawn rate (0.5%)
DEATH_THRESHOLD = 0.0  # No mortality (same as V6b)

def run_experiment(spawn_cost, seed):
    """Run single experiment with specified spawn_cost and seed."""

    # Create label
    spawn_cost_label = f"{int(spawn_cost*10):02d}_{int((spawn_cost*10 % 1)*10):01d}"
    label = f"SPAWN_COST_{spawn_cost_label}_seed{seed}"

    print(f"\n{'='*80}")
    print(f"EXPERIMENT: spawn_cost={spawn_cost}, seed={seed}")
    print(f"{'='*80}")

    # Initialize world
    world = World(
        energy_cap=E_CAP,
        initial_population=200,
        e_produce=E_PRODUCE,
        e_consume=E_CONSUME,
        spawn_cost=spawn_cost,  # VARIABLE
        f_spawn=F_SPAWN,
        death_threshold=DEATH_THRESHOLD,
        seed=seed
    )

    # Setup database
    db_path = RESULTS_DIR / f"c186_{label}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            cycle INTEGER PRIMARY KEY,
            population INTEGER,
            energy_total REAL,
            n_compositions INTEGER,
            n_decompositions INTEGER
        )
    """)
    conn.commit()

    # Run simulation
    start_time = time.time()
    last_report = 0

    for cycle in range(CYCLES):
        world.step()

        # Save to database every 100 cycles
        if cycle % 100 == 0:
            cursor.execute("""
                INSERT INTO results VALUES (?, ?, ?, ?, ?)
            """, (cycle, world.population, world.energy_total,
                  world.n_compositions_total, world.n_decompositions_total))

        # Progress report
        if cycle - last_report >= 10_000:
            elapsed = time.time() - start_time
            rate = cycle / elapsed if elapsed > 0 else 0
            eta = (CYCLES - cycle) / rate if rate > 0 else 0

            print(f"Cycle {cycle:7,} | Pop: {world.population:5,} | "
                  f"E_total: {world.energy_total:12,.1f} | "
                  f"Spawn: {world.n_compositions_total:3,} | "
                  f"Rate: {rate:,.1f} cyc/s | ETA: {eta/3600:.1f}h")

            last_report = cycle

            # Backup JSON
            if cycle % SAVE_INTERVAL == 0:
                conn.commit()

    # Final database commit
    conn.commit()
    conn.close()

    # Calculate final statistics
    runtime = time.time() - start_time
    rate = CYCLES / runtime

    # Calculate E_avg at asymptote (last 10%)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(energy_total * 1.0 / population)
        FROM results
        WHERE cycle >= ?
    """, (int(CYCLES * 0.9),))

    e_avg_asymptote = cursor.fetchone()[0]
    conn.close()

    buffer_factor = e_avg_asymptote / spawn_cost if spawn_cost > 0 else 0

    print(f"\n{'='*80}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*80}")
    print(f"spawn_cost: {spawn_cost}")
    print(f"seed: {seed}")
    print(f"Runtime: {runtime:.1f} seconds")
    print(f"Rate: {rate:,.1f} cycles/second")
    print(f"Final population: {world.population:,}")
    print(f"Final energy: {world.energy_total:,.2f}")
    print(f"E_avg (asymptote): {e_avg_asymptote:.2f} units")
    print(f"Buffer factor k: {buffer_factor:.2f}")
    print(f"{'='*80}\n")

    # Return summary
    return {
        'spawn_cost': spawn_cost,
        'seed': seed,
        'runtime': runtime,
        'cycles': CYCLES,
        'rate': rate,
        'final_population': world.population,
        'final_energy': world.energy_total,
        'e_avg_asymptote': e_avg_asymptote,
        'buffer_factor': buffer_factor,
        'database': str(db_path)
    }

def main():
    """Main experimental campaign."""

    print("="*80)
    print("C186 SPAWN COST SCALING VALIDATION")
    print("="*80)
    print()
    print("Hypothesis: Buffer factor k ≈ 95 is universal constant")
    print("Test: E_min = k × spawn_cost across spawn_cost values")
    print()
    print("Experimental Design:")
    print(f"  Spawn costs: {SPAWN_COSTS}")
    print(f"  Seeds: {SEEDS[0]}-{SEEDS[-1]} (n={len(SEEDS)} per condition)")
    print(f"  Total experiments: {len(SPAWN_COSTS) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES:,}")
    print(f"  Expected runtime: ~13 minutes")
    print()
    print("="*80)
    print()

    # Run all experiments
    all_results = []
    campaign_start = time.time()

    for i, spawn_cost in enumerate(SPAWN_COSTS):
        print(f"\n{'='*80}")
        print(f"CONDITION {i+1}/{len(SPAWN_COSTS)}: spawn_cost = {spawn_cost}")
        print(f"{'='*80}")

        for j, seed in enumerate(SEEDS):
            print(f"\nReplicate {j+1}/{len(SEEDS)}")

            result = run_experiment(spawn_cost, seed)
            all_results.append(result)

    campaign_runtime = time.time() - campaign_start

    # Summary statistics
    print("\n" + "="*80)
    print("CAMPAIGN SUMMARY")
    print("="*80)
    print()
    print(f"Total experiments: {len(all_results)}")
    print(f"Total runtime: {campaign_runtime/60:.1f} minutes")
    print(f"Average runtime per experiment: {campaign_runtime/len(all_results):.1f} seconds")
    print()

    # Buffer factor analysis
    print("BUFFER FACTOR ANALYSIS")
    print("-"*80)
    print(f"{'Spawn Cost':<12} | {'k (mean)':<10} | {'k (std)':<10} | {'E_min (mean)':<12} | {'K (predicted)':<12}")
    print("-"*80)

    for spawn_cost in SPAWN_COSTS:
        # Filter results for this spawn_cost
        results_subset = [r for r in all_results if r['spawn_cost'] == spawn_cost]

        k_values = [r['buffer_factor'] for r in results_subset]
        e_avg_values = [r['e_avg_asymptote'] for r in results_subset]

        k_mean = np.mean(k_values)
        k_std = np.std(k_values)
        e_avg_mean = np.mean(e_avg_values)
        k_predicted = E_CAP / e_avg_mean

        print(f"{spawn_cost:<12.1f} | {k_mean:<10.2f} | {k_std:<10.2f} | {e_avg_mean:<12.2f} | {k_predicted:<12,.0f}")

    print()

    # Universality test
    all_k = [r['buffer_factor'] for r in all_results]
    k_overall_mean = np.mean(all_k)
    k_overall_std = np.std(all_k)
    k_cv = k_overall_std / k_overall_mean

    print("UNIVERSALITY TEST")
    print("-"*80)
    print(f"Overall k: {k_overall_mean:.2f} ± {k_overall_std:.2f}")
    print(f"Coefficient of variation: {k_cv:.3f}")
    print(f"Hypothesis: k ≈ 95 (universal)")
    print(f"Result: {'SUPPORTED (CV < 0.1)' if k_cv < 0.1 else 'NOT SUPPORTED (CV >= 0.1)'}")
    print()

    # Linear scaling test
    spawn_cost_values = [r['spawn_cost'] for r in all_results]
    e_min_values = [r['e_avg_asymptote'] for r in all_results]

    # Linear regression: E_min = a + b * spawn_cost
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(spawn_cost_values, e_min_values)
    r_squared = r_value ** 2

    print("LINEAR SCALING TEST")
    print("-"*80)
    print(f"Model: E_min = {intercept:.2f} + {slope:.2f} × spawn_cost")
    print(f"R² = {r_squared:.4f}")
    print(f"Expected: E_min = 0 + 94.69 × spawn_cost")
    print(f"Result: {'LINEAR SCALING VALIDATED (R² > 0.99)' if r_squared > 0.99 else 'LINEAR SCALING WEAK (R² < 0.99)'}")
    print()

    # Save results
    results_path = RESULTS_DIR / "spawn_cost_scaling_summary.json"
    with open(results_path, 'w') as f:
        json.dump({
            'campaign_runtime': campaign_runtime,
            'experiments': all_results,
            'statistics': {
                'k_overall_mean': k_overall_mean,
                'k_overall_std': k_overall_std,
                'k_cv': k_cv,
                'linear_fit': {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_squared,
                    'p_value': p_value
                }
            }
        }, f, indent=2)

    print(f"Results saved: {results_path}")
    print()
    print("="*80)
    print("VALIDATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
