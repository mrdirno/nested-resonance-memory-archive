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

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude (Anthropic)
License: GPL-3.0
Date: 2025-11-18
Cycle: 1394
"""

import sys
import os
import time
import sqlite3
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Simple agent class (self-contained)
class SimpleAgent:
    """Minimal agent for V6b experiments."""
    def __init__(self, agent_id, energy, population_id):
        self.agent_id = agent_id
        self.energy = energy
        self.population_id = population_id

# =============================================================================
# CONFIGURATION
# =============================================================================

# V6b Parameters (NET-POSITIVE GROWTH - matched exactly)
E_CONSUME = 0.5  # Energy consumed per cycle
E_RECHARGE = 1.0  # Energy recharged per cycle (NET ENERGY = +0.5)
F_SPAWN = 0.005  # Spawn rate (0.5%, mid-range, CONSTANT)

# Spawn costs (VARIABLE - parameter sweep)
SPAWN_COSTS = [2.5, 5.0, 7.5, 10.0]
SPAWN_LABELS = ["2.5", "5.0", "7.5", "10.0"]

# Seeds (10 replications per condition)
SEEDS = list(range(42, 52))

# Hierarchical configuration
N_POPULATIONS = 10  # Hierarchical structure
N_AGENTS_PER_POP = 10  # Initial agents per population
INITIAL_AGENTS = N_POPULATIONS * N_AGENTS_PER_POP  # 100 total

# Experimental timeline
CYCLES = 450_000  # ~10× pilot duration
PRINT_INTERVAL = 10_000  # Print status every 10,000 cycles
HEARTBEAT_INTERVAL = 10_000  # Write heartbeat every 10,000 cycles
DB_CHECK_CYCLE = 50_000  # Validate database after 50,000 cycles (~1h pilot equivalent)
JSON_BACKUP_INTERVAL = 100_000  # Backup to JSON every 100,000 cycles

# Safeguards
POPULATION_CAP = 100_000  # Prevent memory overflow
ENERGY_CAP = 10_000_000  # Prevent numerical overflow

# File paths
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# FAIL-FAST DATABASE INITIALIZATION
# =============================================================================

def initialize_database(db_path):
    """Initialize SQLite database with fail-fast validation."""
    print(f"[INIT] Initializing database: {db_path}")

    # Remove old database if exists
    if db_path.exists():
        db_path.unlink()
        print("[INIT] Removed old database")

    # Create connection (NO try/except - let it fail loudly)
    connection = sqlite3.connect(str(db_path))
    cursor = connection.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            cycle INTEGER,
            population INTEGER,
            energy_total REAL,
            n_compositions INTEGER,
            n_decompositions INTEGER,
            timestamp REAL
        )
    """)

    connection.commit()

    # FAIL-FAST VALIDATION
    assert connection is not None, "Database connection failed"
    assert db_path.exists(), "Database file not created"

    # Check file size after creation
    db_size = os.path.getsize(db_path)
    assert db_size > 0, f"Database file size is 0 bytes after creation"

    print(f"[INIT] Database created successfully ({db_size} bytes)")
    print(f"[INIT] Tables initialized")

    return connection, cursor

def write_heartbeat(heartbeat_path, cycle, population, energy_total):
    """Write heartbeat to log file."""
    with open(heartbeat_path, 'a') as f:
        f.write(f"{time.time()},{cycle},{population},{energy_total:.2f}\n")

def check_database_health(cursor, db_path, cycle):
    """Check database health with assertions."""
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM results")
    row_count = cursor.fetchone()[0]

    # Check file size
    db_size = os.path.getsize(db_path)

    print(f"[DB CHECK] Cycle {cycle}: {row_count} rows, {db_size} bytes")

    # FAIL-FAST ASSERTIONS
    assert row_count > 0, f"No data written after {cycle} cycles"
    assert db_size > 1024, f"Database too small ({db_size} bytes) after {cycle} cycles"

    print(f"[DB CHECK] Health check PASSED")

def save_json_backup(output_path, summary):
    """Save JSON backup of experimental state."""
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"[BACKUP] JSON saved: {output_path.name}")

# =============================================================================
# HIERARCHICAL AGENT SYSTEM
# =============================================================================

def create_hierarchical_agents():
    """Create hierarchical population structure."""
    agents = []

    for pop_id in range(N_POPULATIONS):
        for agent_id in range(N_AGENTS_PER_POP):
            agent = SimpleAgent(
                agent_id=pop_id * N_AGENTS_PER_POP + agent_id,
                energy=E_RECHARGE * 10,  # Start with 10× recharge (buffer)
                population_id=pop_id
            )
            agents.append(agent)

    return agents

def hierarchical_spawn(agents, f_spawn, spawn_cost, rng):
    """
    Hierarchical spawn: Each population spawns independently.

    Deterministic intervals within population (NRM advantage hypothesis).
    spawn_cost is now a parameter (VARIABLE for validation).
    """
    spawned = []

    for pop_id in range(N_POPULATIONS):
        # Get agents in this population
        pop_agents = [a for a in agents if a.population_id == pop_id]

        if not pop_agents:
            continue

        # Deterministic spawn: Every 1/F_SPAWN cycles
        interval = int(1.0 / f_spawn) if f_spawn > 0 else float('inf')

        # Probabilistic spawn using interval
        if rng.random() < (len(pop_agents) / interval):
            # Select parent
            parent = rng.choice(pop_agents)

            if parent.energy >= spawn_cost:  # VARIABLE spawn cost
                # Create offspring
                child = SimpleAgent(
                    agent_id=len(agents) + len(spawned),
                    energy=spawn_cost,  # VARIABLE spawn cost
                    population_id=pop_id
                )
                parent.energy -= spawn_cost  # VARIABLE spawn cost
                spawned.append(child)

    return spawned

# =============================================================================
# MAIN EXPERIMENT RUNNER
# =============================================================================

def run_experiment(spawn_cost, spawn_label, seed):
    """Execute single spawn_cost validation experiment."""
    print("="*80)
    print(f"C186 SPAWN COST SCALING VALIDATION")
    print("="*80)
    print()
    print(f"Configuration:")
    print(f"  Condition: SPAWN_COST_{spawn_label}")
    print(f"  Seed: {seed}")
    print(f"  Spawn cost: {spawn_cost:.1f} units (VARIABLE)")
    print(f"  Spawn rate: {F_SPAWN:.4f} (0.5%, constant)")
    print(f"  Energy: E_consume={E_CONSUME}, E_recharge={E_RECHARGE} (net=+0.5)")
    print(f"  Cycles: {CYCLES:,}")
    print(f"  Populations: {N_POPULATIONS}")
    print(f"  Agents per pop: {N_AGENTS_PER_POP}")
    print(f"  Total agents: {INITIAL_AGENTS}")
    print()

    # File paths for this experiment
    condition_name = f"SPAWN_COST_{spawn_label.replace('.', '_')}"
    db_path = RESULTS_DIR / f"c186_spawn_cost_{condition_name}_seed{seed}.db"
    heartbeat_path = RESULTS_DIR / f"c186_spawn_cost_{condition_name}_seed{seed}_heartbeat.log"
    json_path = RESULTS_DIR / f"c186_spawn_cost_{condition_name}_seed{seed}.json"

    # Initialize RNG
    rng = np.random.default_rng(seed)

    # Initialize database (FAIL-FAST)
    connection, cursor = initialize_database(db_path)

    # Initialize heartbeat log
    if heartbeat_path.exists():
        heartbeat_path.unlink()
    with open(heartbeat_path, 'w') as f:
        f.write("timestamp,cycle,population,energy_total\n")

    # Create agents
    agents = create_hierarchical_agents()

    # Metrics
    start_time = time.time()
    n_decompositions_total = 0

    # Main simulation loop
    print(f"[START] Beginning simulation...")
    print()

    for cycle in range(CYCLES):
        # Energy dynamics
        for agent in agents[:]:  # Iterate over copy to allow removal
            # Consume energy
            agent.energy -= E_CONSUME

            # Recharge energy
            agent.energy += E_RECHARGE

            # Decompose if energy depleted
            if agent.energy <= 0:
                agents.remove(agent)
                n_decompositions_total += 1

        # Hierarchical spawn (F_SPAWN constant, spawn_cost variable)
        new_agents = hierarchical_spawn(agents, F_SPAWN, spawn_cost, rng)
        agents.extend(new_agents)

        # Calculate metrics
        population = len(agents)
        energy_total = sum(a.energy for a in agents)
        n_compositions = len(new_agents)

        # SAFEGUARD: Check caps
        if population > POPULATION_CAP:
            print()
            print(f"[ABORT] Population cap exceeded: {population} > {POPULATION_CAP}")
            print(f"[ABORT] Terminating experiment at cycle {cycle}")
            break

        if energy_total > ENERGY_CAP:
            print()
            print(f"[ABORT] Energy cap exceeded: {energy_total:.2f} > {ENERGY_CAP}")
            print(f"[ABORT] Terminating experiment at cycle {cycle}")
            break

        # Write to database every cycle
        cursor.execute("""
            INSERT INTO results (cycle, population, energy_total, n_compositions, n_decompositions, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cycle, population, energy_total, n_compositions, n_decompositions_total, time.time()))

        # Commit every 100 cycles
        if cycle % 100 == 0:
            connection.commit()

        # Print status
        if cycle % PRINT_INTERVAL == 0:
            elapsed = time.time() - start_time
            rate = (cycle + 1) / elapsed if elapsed > 0 else 0
            eta = (CYCLES - cycle - 1) / rate if rate > 0 else 0

            print(f"Cycle {cycle:6,} | Pop: {population:5d} | E_total: {energy_total:10.1f} | "
                  f"Spawn: {n_compositions:3d} | Rate: {rate:.1f} cyc/s | ETA: {eta/3600:.1f}h")

        # Write heartbeat
        if cycle % HEARTBEAT_INTERVAL == 0:
            write_heartbeat(heartbeat_path, cycle, population, energy_total)

        # Database health check
        if cycle == DB_CHECK_CYCLE:
            print()
            check_database_health(cursor, db_path, cycle)
            print()

        # JSON backup
        if cycle > 0 and cycle % JSON_BACKUP_INTERVAL == 0:
            summary = {
                'experiment': 'C186_V6b_NET_POSITIVE_GROWTH',
                'condition': condition_name,
                'seed': seed,
                'parameters': {
                    'f_spawn': f_spawn,
                    'e_consume': E_CONSUME,
                    'e_recharge': E_RECHARGE,
                    'spawn_cost': SPAWN_COST,
                    'cycles': cycle,
                    'n_populations': N_POPULATIONS,
                    'n_agents_per_pop': N_AGENTS_PER_POP
                },
                'results': {
                    'current_cycle': cycle,
                    'current_population': population,
                    'current_energy': energy_total,
                    'total_decompositions': n_decompositions_total,
                    'runtime_seconds': time.time() - start_time
                },
                'timestamp': time.time()
            }
            save_json_backup(json_path, summary)

    # Final commit
    connection.commit()

    # Final metrics
    elapsed = time.time() - start_time
    final_pop = len(agents)
    final_energy = sum(a.energy for a in agents)

    print()
    print("="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)
    print(f"Condition: {condition_name}")
    print(f"Seed: {seed}")
    print(f"Runtime: {elapsed/3600:.2f} hours ({elapsed:.1f} seconds)")
    print(f"Cycles: {CYCLES:,}")
    print(f"Rate: {CYCLES/elapsed:.2f} cycles/second")
    print(f"Final population: {final_pop}")
    print(f"Final energy: {final_energy:.2f}")
    print()

    # Final database check
    cursor.execute("SELECT COUNT(*) FROM results")
    total_rows = cursor.fetchone()[0]
    db_size = os.path.getsize(db_path)

    print(f"Database: {total_rows:,} rows, {db_size:,} bytes")
    print(f"Heartbeat log: {heartbeat_path.name}")
    print()

    # VERDICT
    print("="*80)
    print("VERDICT")
    print("="*80)

    success = True

    if db_size == 0:
        print("✗ FAIL: Database is empty (0 bytes)")
        print("  → Root cause: Database initialization failure")
        success = False
    elif db_size < 1024:
        print("✗ FAIL: Database too small (<1 KB)")
        print("  → Root cause: Data collection not working properly")
        success = False
    elif final_pop == 0:
        print("✗ FAIL: Population collapsed to zero")
        print("  → Root cause: Energy balance incorrect OR ultra-low regime unviable")
        success = False
    else:
        print("✓ PASS: Database collecting data")
        print("✓ PASS: Population sustained")
        print("✓ PASS: Net-positive growth regime viable")
        print()
        if final_pop > INITIAL_AGENTS * 10:
            print("  → Note: Significant growth despite net=0 (unexpected)")
        elif final_pop < INITIAL_AGENTS / 2:
            print("  → Note: Population declined (check energy balance)")
        else:
            print("  → Note: Population growth enabled (net-positive energy)")

    print("="*80)
    print()

    # Save final summary JSON
    summary = {
        'experiment': 'C186_V6b_NET_POSITIVE_GROWTH',
        'condition': condition_name,
        'seed': seed,
        'parameters': {
            'f_spawn': f_spawn,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'n_populations': N_POPULATIONS,
            'n_agents_per_pop': N_AGENTS_PER_POP
        },
        'results': {
            'runtime_seconds': elapsed,
            'runtime_hours': elapsed / 3600,
            'final_population': final_pop,
            'final_energy': final_energy,
            'total_decompositions': n_decompositions_total,
            'database_size_bytes': db_size,
            'database_rows': total_rows,
            'success': success
        },
        'verdict': {
            'database_works': db_size > 1024,
            'population_sustained': final_pop > 0,
            'growth_enabled': final_pop > 0 and db_size > 1024
        },
        'timestamp': time.time()
    }

    save_json_backup(json_path, summary)

    print(f"Final summary saved: {json_path.name}")
    print()

    # Close database with explicit sync
    connection.close()

    # Ensure database file fully written to disk (macOS APFS fix)
    os.sync()

    print(f"[SYNC] Database closed and synced to disk")
    print()

    return success

# =============================================================================
# BATCH EXECUTION
# =============================================================================

def run_spawn_cost_campaign():
    """Execute all 40 spawn_cost validation experiments (4 conditions × 10 seeds)."""
    print()
    print("="*80)
    print("C186 SPAWN COST SCALING VALIDATION CAMPAIGN")
    print("="*80)
    print()
    print(f"Total experiments: {len(SPAWN_COSTS)} conditions × {len(SEEDS)} seeds = {len(SPAWN_COSTS) * len(SEEDS)}")
    print(f"Estimated duration: ~13 minutes (450,000 cycles × 40 experiments)")
    print(f"Energy regime: E_consume={E_CONSUME}, E_recharge={E_RECHARGE} (net=+0.5, growth)")
    print(f"Spawn rate: F_SPAWN={F_SPAWN} (0.5%, constant)")
    print()

    campaign_start = time.time()
    results = []

    for i, (spawn_cost, spawn_label) in enumerate(zip(SPAWN_COSTS, SPAWN_LABELS)):
        print()
        print("="*80)
        print(f"CONDITION {i+1}/{len(SPAWN_COSTS)}: spawn_cost = {spawn_cost}")
        print("="*80)
        print()

        for j, seed in enumerate(SEEDS):
            print()
            print(f"--- Experiment {i*len(SEEDS) + j + 1}/{len(SPAWN_COSTS)*len(SEEDS)} ---")
            print()

            try:
                success = run_experiment(spawn_cost, spawn_label, seed)
                results.append({
                    'spawn_cost': spawn_cost,
                    'spawn_label': spawn_label,
                    'seed': seed,
                    'success': success
                })

                # FILESYSTEM SYNC DELAY (Fix for rapid sequential I/O stress)
                # Allow filesystem to flush buffers and release locks
                print()
                print(f"[SYNC] Filesystem sync delay (10 seconds)...")
                os.sync()  # Explicit filesystem sync
                time.sleep(10)  # 10-second delay for macOS APFS
                print(f"[SYNC] Ready for next experiment")
                print()

            except Exception as e:
                print()
                print(f"[ERROR] Experiment failed: {e}")
                print()
                import traceback
                traceback.print_exc()
                results.append({
                    'f_spawn': f_spawn,
                    'spawn_label': spawn_label,
                    'seed': seed,
                    'success': False,
                    'error': str(e)
                })

                # FILESYSTEM SYNC DELAY (even after errors)
                print()
                print(f"[SYNC] Filesystem sync delay (10 seconds)...")
                os.sync()  # Explicit filesystem sync
                time.sleep(10)  # 10-second delay
                print(f"[SYNC] Ready for next experiment")
                print()

    campaign_elapsed = time.time() - campaign_start

    # Campaign summary
    print()
    print("="*80)
    print("V6b CAMPAIGN COMPLETE")
    print("="*80)
    print(f"Total runtime: {campaign_elapsed/3600:.2f} hours ({campaign_elapsed/86400:.2f} days)")
    print(f"Experiments run: {len(results)}")
    print(f"Successes: {sum(1 for r in results if r['success'])}")
    print(f"Failures: {sum(1 for r in results if not r['success'])}")
    print()

    # Save campaign summary
    campaign_summary = {
        'campaign': 'C186_V6b_NET_POSITIVE_GROWTH',
        'start_time': campaign_start,
        'end_time': time.time(),
        'duration_hours': campaign_elapsed / 3600,
        'duration_days': campaign_elapsed / 86400,
        'parameters': {
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'f_spawn_values': F_SPAWN_VALUES,
            'seeds': SEEDS
        },
        'results': results,
        'summary': {
            'total_experiments': len(results),
            'successes': sum(1 for r in results if r['success']),
            'failures': sum(1 for r in results if not r['success'])
        }
    }

    campaign_json_path = RESULTS_DIR / "c186_v6a_campaign_summary.json"
    with open(campaign_json_path, 'w') as f:
        json.dump(campaign_summary, f, indent=2)

    print(f"Campaign summary saved: {campaign_json_path}")
    print()

    return campaign_summary

if __name__ == '__main__':
    try:
        # Run full spawn_cost validation campaign
        campaign_summary = run_spawn_cost_campaign()

        # Exit with success if all experiments succeeded
        if campaign_summary['summary']['failures'] == 0:
            sys.exit(0)
        else:
            sys.exit(1)

    except AssertionError as e:
        print()
        print("="*80)
        print("FAIL-FAST ASSERTION TRIGGERED")
        print("="*80)
        print(f"Error: {e}")
        print()
        print("This experiment was designed to fail fast on critical issues.")
        print("The assertion indicates a fundamental problem that must be fixed.")
        print()
        sys.exit(2)

    except Exception as e:
        print()
        print("="*80)
        print("UNEXPECTED ERROR")
        print("="*80)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        sys.exit(3)
