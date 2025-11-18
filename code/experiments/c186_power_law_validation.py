#!/usr/bin/env python3
"""
Cycle 1400: Power Law Validation Experiments

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0

PURPOSE:
--------
Validate inverse power law predictions for E_min(f_spawn):

    E_min(f) = E_∞ + A / f^α

Where (from Cycle 1399 fitting):
    E_∞ = 500.0617 ± 0.1021 units
    A   = 0.000022 ± 0.000008
    α   = 2.1890 ± 0.0568

PREDICTIONS TO TEST:
--------------------
f_spawn = 0.003 → E_min = 507.54 units
f_spawn = 0.006 → E_min = 501.70 units
f_spawn = 0.008 → E_min = 500.94 units

EXPERIMENTAL DESIGN:
--------------------
- Conditions: 3 (f_spawn ∈ {0.003, 0.006, 0.008})
- Seeds: 5 per condition
- Total experiments: 15
- Runtime: 450,000 cycles each
- spawn_cost: 5.0 (match V6b baseline)
- Architecture: Hierarchical (10 populations, V6b structure)

SUCCESS CRITERIA:
-----------------
- Measured E_min within ±1.0 unit of prediction
- Power law outperforms exponential decay
- R² > 0.999 when including new data points
- Confirms α ≈ 2.19 exponent

BASELINE PARAMETERS:
--------------------
E_consume = 0.5 units/agent/cycle
E_recharge = 1.0 units/agent/cycle
spawn_cost = 5.0 units
E_cap = 10,000,000 units
"""

import json
import sqlite3
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ============================================================================
# EXPERIMENT PARAMETERS
# ============================================================================

# Energy parameters (V6b baseline)
E_CONSUME = 0.5
E_RECHARGE = 1.0
SPAWN_COST = 5.0  # Match V6b
E_CAP = 10_000_000

# Validation f_spawn values (intermediate, untested)
F_SPAWN_VALUES = [0.003, 0.006, 0.008]
F_SPAWN_LABELS = ["0.003", "0.006", "0.008"]

# Power law predictions (from Cycle 1399)
PREDICTIONS_POWER_LAW = {
    0.003: 507.54,
    0.006: 501.70,
    0.008: 500.94
}

# Exponential predictions (for comparison)
PREDICTIONS_EXPONENTIAL = {
    0.003: 509.46,
    0.006: 501.25,
    0.008: 500.93
}

# Seeds for reproducibility (5 per condition)
SEEDS = list(range(42, 47))  # [42, 43, 44, 45, 46]

# Simulation parameters
MAX_CYCLES = 450_000
COMMIT_INTERVAL = 100  # Commit database every N cycles

# Hierarchy parameters (V6b structure)
N_POPULATIONS = 10
HIERARCHY_DEPTH = 3

# File paths
RESULTS_DIR = Path('/Volumes/dual/DUALITY-ZERO-V2/experiments/results')
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# SIMPLE AGENT CLASS
# ============================================================================

class SimpleAgent:
    """
    Minimal hierarchical agent for V6 experiments.

    Each agent:
    - Has energy (E_total)
    - Consumes E_consume per cycle
    - Recharges E_recharge per cycle
    - Can spawn child with probability f_spawn (costs spawn_cost energy)
    - Dies if energy <= 0
    - Belongs to a population (pop_id)
    - Has depth in hierarchy
    """

    def __init__(self, agent_id, energy, pop_id, depth=0):
        self.agent_id = agent_id
        self.energy = energy
        self.pop_id = pop_id
        self.depth = depth
        self.alive = True

    def cycle(self, f_spawn, spawn_cost, e_consume, e_recharge):
        """Execute one lifecycle cycle."""
        if not self.alive:
            return None

        # Consume
        self.energy -= e_consume

        # Recharge
        self.energy += e_recharge

        # Death check
        if self.energy <= 0:
            self.alive = False
            return None

        # Spawn check (probabilistic)
        import random
        if random.random() < f_spawn:
            if self.energy >= spawn_cost:
                self.energy -= spawn_cost
                # Child inherits half of parent's energy
                child_energy = self.energy / 2
                self.energy = self.energy / 2
                # Return new agent (will be added to population)
                return SimpleAgent(
                    agent_id=None,  # Will be assigned by system
                    energy=child_energy,
                    pop_id=self.pop_id,
                    depth=min(self.depth + 1, HIERARCHY_DEPTH)
                )

        return None


# ============================================================================
# HIERARCHICAL SYSTEM
# ============================================================================

def run_hierarchical_experiment(f_spawn, spawn_cost, seed, max_cycles=450_000):
    """
    Run hierarchical agent experiment (V6b architecture).

    Parameters:
    -----------
    f_spawn : float
        Spawn probability per agent per cycle
    spawn_cost : float
        Energy cost to spawn new agent
    seed : int
        Random seed for reproducibility
    max_cycles : int
        Maximum simulation cycles

    Returns:
    --------
    results : dict
        Experiment results and metrics
    """

    import random
    random.seed(seed)

    # Create unique experiment ID
    exp_id = f"c186_power_law_validation_F_{f_spawn:.4f}_SEED_{seed}"

    # Create database
    db_path = RESULTS_DIR / f"{exp_id}.db"
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create results table
    cursor.execute('''
        CREATE TABLE results (
            cycle INTEGER PRIMARY KEY,
            population INTEGER,
            energy_total REAL,
            energy_mean REAL,
            spawns_total INTEGER,
            deaths_total INTEGER
        )
    ''')
    conn.commit()

    # Initialize populations (10 populations, V6b structure)
    populations = {}
    for pop_id in range(N_POPULATIONS):
        # Each population starts with 10 agents
        populations[pop_id] = []
        for i in range(10):
            agent_id = pop_id * 10 + i
            # Initial energy: E_recharge × 10 (same as V6b)
            init_energy = E_RECHARGE * 10
            agent = SimpleAgent(agent_id, init_energy, pop_id, depth=0)
            populations[pop_id].append(agent)

    # Tracking
    total_spawns = 0
    total_deaths = 0
    next_agent_id = N_POPULATIONS * 10

    # Main simulation loop
    start_time = time.time()

    for cycle in range(max_cycles):

        # Process each population
        for pop_id in range(N_POPULATIONS):
            agents = populations[pop_id]

            # Process each agent
            new_agents = []
            for agent in agents:
                if agent.alive:
                    child = agent.cycle(f_spawn, spawn_cost, E_CONSUME, E_RECHARGE)
                    if child is not None:
                        child.agent_id = next_agent_id
                        next_agent_id += 1
                        new_agents.append(child)
                        total_spawns += 1

            # Add new agents to population
            populations[pop_id].extend(new_agents)

            # Remove dead agents
            alive_agents = [a for a in populations[pop_id] if a.alive]
            dead_count = len(populations[pop_id]) - len(alive_agents)
            total_deaths += dead_count
            populations[pop_id] = alive_agents

        # Compute metrics
        all_agents = []
        for pop_id in range(N_POPULATIONS):
            all_agents.extend(populations[pop_id])

        population = len(all_agents)

        if population == 0:
            # Extinction
            print(f"\n⚠ EXTINCTION at cycle {cycle} (f_spawn={f_spawn:.4f}, seed={seed})")

            # Record final state
            cursor.execute('''
                INSERT INTO results VALUES (?, ?, ?, ?, ?, ?)
            ''', (cycle, 0, 0.0, 0.0, total_spawns, total_deaths))
            conn.commit()

            # Compute E_min (undefined for extinction)
            e_min = None
            termination_reason = f"EXTINCTION at cycle {cycle}"

            break

        energy_total = sum(a.energy for a in all_agents)
        energy_mean = energy_total / population

        # Energy cap check
        if energy_total > E_CAP:
            print(f"\n⚠ ENERGY CAP EXCEEDED at cycle {cycle} (f_spawn={f_spawn:.4f}, seed={seed})")

            # Record final state
            cursor.execute('''
                INSERT INTO results VALUES (?, ?, ?, ?, ?, ?)
            ''', (cycle, population, energy_total, energy_mean, total_spawns, total_deaths))
            conn.commit()

            # Compute E_min
            e_min = energy_total / population
            termination_reason = f"ENERGY_CAP at cycle {cycle}"

            break

        # Record to database (every cycle)
        cursor.execute('''
            INSERT INTO results VALUES (?, ?, ?, ?, ?, ?)
        ''', (cycle, population, energy_total, energy_mean, total_spawns, total_deaths))

        # Commit periodically
        if cycle % COMMIT_INTERVAL == 0:
            conn.commit()

        # Progress update (every 50k cycles)
        if cycle % 50_000 == 0 and cycle > 0:
            elapsed = time.time() - start_time
            print(f"  Cycle {cycle:,}/{max_cycles:,} | Pop: {population:,} | E_total: {energy_total:,.0f} | E_mean: {energy_mean:.2f} | Elapsed: {elapsed:.1f}s")

    else:
        # Reached max_cycles without termination
        # Record final state
        all_agents = []
        for pop_id in range(N_POPULATIONS):
            all_agents.extend(populations[pop_id])

        population = len(all_agents)
        energy_total = sum(a.energy for a in all_agents)
        energy_mean = energy_total / population if population > 0 else 0.0

        cursor.execute('''
            INSERT INTO results VALUES (?, ?, ?, ?, ?, ?)
        ''', (max_cycles, population, energy_total, energy_mean, total_spawns, total_deaths))
        conn.commit()

        e_min = energy_total / population if population > 0 else None
        termination_reason = f"MAX_CYCLES at {max_cycles}"

    # Close database
    conn.close()

    elapsed_total = time.time() - start_time

    # Assemble results
    results = {
        'experiment_id': exp_id,
        'parameters': {
            'f_spawn': f_spawn,
            'spawn_cost': spawn_cost,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'e_cap': E_CAP,
            'seed': seed,
            'max_cycles': max_cycles,
            'n_populations': N_POPULATIONS
        },
        'final_state': {
            'cycle': cycle if 'cycle' in locals() else max_cycles,
            'population': population,
            'energy_total': energy_total,
            'energy_mean': energy_mean,
            'e_min': e_min,
            'total_spawns': total_spawns,
            'total_deaths': total_deaths
        },
        'predictions': {
            'power_law': PREDICTIONS_POWER_LAW[f_spawn],
            'exponential': PREDICTIONS_EXPONENTIAL[f_spawn]
        },
        'termination': termination_reason,
        'runtime_seconds': elapsed_total,
        'database': str(db_path)
    }

    # Save JSON
    json_path = RESULTS_DIR / f"{exp_id}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)

    return results


# ============================================================================
# CAMPAIGN EXECUTION
# ============================================================================

def run_validation_campaign():
    """Execute full validation campaign (15 experiments)."""

    print("="*80)
    print("CYCLE 1400: POWER LAW VALIDATION CAMPAIGN")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"\nExperimental Design:")
    print(f"  f_spawn values: {F_SPAWN_VALUES}")
    print(f"  Seeds per condition: {len(SEEDS)}")
    print(f"  Total experiments: {len(F_SPAWN_VALUES) * len(SEEDS)}")
    print(f"  Runtime per experiment: {MAX_CYCLES:,} cycles")
    print(f"\nPower Law Predictions:")
    for f in F_SPAWN_VALUES:
        print(f"  f_spawn={f:.4f} → E_min={PREDICTIONS_POWER_LAW[f]:.2f} units")

    print("\n" + "-"*80)
    print("LAUNCHING EXPERIMENTS")
    print("-"*80)

    campaign_start = time.time()
    all_results = []

    total_experiments = len(F_SPAWN_VALUES) * len(SEEDS)
    completed = 0

    for f_spawn in F_SPAWN_VALUES:
        for seed in SEEDS:
            completed += 1
            print(f"\n[{completed}/{total_experiments}] f_spawn={f_spawn:.4f}, seed={seed}")
            print("-" * 40)

            exp_start = time.time()
            results = run_hierarchical_experiment(
                f_spawn=f_spawn,
                spawn_cost=SPAWN_COST,
                seed=seed,
                max_cycles=MAX_CYCLES
            )
            exp_elapsed = time.time() - exp_start

            all_results.append(results)

            # Print results
            e_min = results['final_state']['e_min']
            pred_power = results['predictions']['power_law']
            pred_exp = results['predictions']['exponential']

            if e_min is not None:
                error_power = abs(e_min - pred_power)
                error_exp = abs(e_min - pred_exp)

                print(f"\n  ✓ COMPLETE")
                print(f"  E_min measured: {e_min:.2f} units")
                print(f"  Power law prediction: {pred_power:.2f} units (error: {error_power:.2f})")
                print(f"  Exponential prediction: {pred_exp:.2f} units (error: {error_exp:.2f})")
                print(f"  Runtime: {exp_elapsed:.1f}s")

                # Validation check
                if error_power < 1.0:
                    print(f"  ✅ Power law VALIDATED (error < 1.0 unit)")
                else:
                    print(f"  ⚠ Power law error > 1.0 unit")
            else:
                print(f"\n  ⚠ EXTINCTION (E_min undefined)")

            # Filesystem sync delay
            print("  Syncing filesystem...")
            os.sync()
            time.sleep(10)

    campaign_elapsed = time.time() - campaign_start

    # Campaign summary
    print("\n" + "="*80)
    print("CAMPAIGN COMPLETE")
    print("="*80)
    print(f"\nTotal experiments: {len(all_results)}")
    print(f"Campaign runtime: {campaign_elapsed/60:.1f} minutes")
    print(f"Average per experiment: {campaign_elapsed/len(all_results):.1f} seconds")

    # Compute validation statistics
    valid_results = [r for r in all_results if r['final_state']['e_min'] is not None]

    if valid_results:
        print(f"\nSuccessful experiments: {len(valid_results)}/{len(all_results)}")

        # Group by f_spawn
        for f_spawn in F_SPAWN_VALUES:
            f_results = [r for r in valid_results if r['parameters']['f_spawn'] == f_spawn]

            if f_results:
                e_mins = [r['final_state']['e_min'] for r in f_results]
                e_min_mean = sum(e_mins) / len(e_mins)
                e_min_std = (sum((e - e_min_mean)**2 for e in e_mins) / len(e_mins)) ** 0.5

                pred_power = PREDICTIONS_POWER_LAW[f_spawn]
                pred_exp = PREDICTIONS_EXPONENTIAL[f_spawn]

                error_power = abs(e_min_mean - pred_power)
                error_exp = abs(e_min_mean - pred_exp)

                print(f"\nf_spawn={f_spawn:.4f}:")
                print(f"  E_min measured: {e_min_mean:.2f} ± {e_min_std:.2f} units (N={len(e_mins)})")
                print(f"  Power law prediction: {pred_power:.2f} (error: {error_power:.2f})")
                print(f"  Exponential prediction: {pred_exp:.2f} (error: {error_exp:.2f})")

                if error_power < error_exp:
                    print(f"  → Power law WINS (lower error)")
                else:
                    print(f"  → Exponential WINS (lower error)")

    # Save campaign summary
    summary = {
        'campaign': 'power_law_validation',
        'cycle': 1400,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'f_spawn_values': F_SPAWN_VALUES,
            'spawn_cost': SPAWN_COST,
            'seeds': SEEDS,
            'max_cycles': MAX_CYCLES
        },
        'predictions': {
            'power_law': PREDICTIONS_POWER_LAW,
            'exponential': PREDICTIONS_EXPONENTIAL
        },
        'results': all_results,
        'runtime_seconds': campaign_elapsed
    }

    summary_path = RESULTS_DIR / 'c186_power_law_validation_campaign_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Campaign summary saved: {summary_path}")

    return summary


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    summary = run_validation_campaign()

    print("\n" + "="*80)
    print("CYCLE 1400 COMPLETE")
    print("="*80)
    print("\nNext: Analyze validation results and update functional form")
