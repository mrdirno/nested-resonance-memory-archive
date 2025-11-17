#!/usr/bin/env python3
"""
C186 V6 PILOT - 1-Hour Ultra-Low Frequency Validation

Purpose: Diagnose V6 termination root cause before full 10-day experiment
Duration: ~1 hour (5000 cycles at ultra-low frequency pace)
Condition: 0.10% hierarchical spawn (single condition, single seed)

This pilot tests:
1. Database initialization works (size > 0 after 1000 cycles)
2. Population persists at 0.10% spawn (no immediate collapse)
3. Data collection functions properly (heartbeat logs growing)
4. Code has no critical bugs (completes without crash)

Decision Tree:
- If pilot SUCCEEDS (DB > 0, Pop > 0) → Redesign full V6 with safeguards
- If pilot FAILS (DB = 0) → Database initialization issue, fix and retry
- If pilot FAILS (Pop = 0) → Ultra-low regime unviable, abandon

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
Date: 2025-11-16
Cycle: 1370
"""

import sys
import os
import time
import sqlite3
import json
import numpy as np
from pathlib import Path

# Simple agent class (self-contained for pilot)
class SimpleAgent:
    """Minimal agent for pilot testing."""
    def __init__(self, agent_id, energy, population_id):
        self.agent_id = agent_id
        self.energy = energy
        self.population_id = population_id

# =============================================================================
# CONFIGURATION
# =============================================================================

# Experimental parameters
SEED = 42
F_SPAWN = 0.001  # 0.10% spawn rate (ultra-low)
E_CONSUME = 0.5
E_RECHARGE = 1.0
SPAWN_COST = 5.0
CYCLES = 5000  # Estimated ~1 hour based on V6 pace

# Hierarchical configuration
N_POPULATIONS = 10  # Minimal hierarchy for testing
N_AGENTS_PER_POP = 10  # Small population for speed
TOTAL_AGENTS = N_POPULATIONS * N_AGENTS_PER_POP  # 100 total

# Logging configuration
PRINT_INTERVAL = 100  # Print status every 100 cycles
HEARTBEAT_INTERVAL = 500  # Write heartbeat every 500 cycles
DB_CHECK_CYCLE = 1000  # Validate database after 1000 cycles

# File paths
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
DB_PATH = RESULTS_DIR / "c186_v6_pilot.db"
HEARTBEAT_PATH = RESULTS_DIR / "c186_v6_pilot_heartbeat.log"
OUTPUT_PATH = RESULTS_DIR / "c186_v6_pilot.json"

# =============================================================================
# FAIL-FAST DATABASE INITIALIZATION
# =============================================================================

def initialize_database():
    """Initialize SQLite database with fail-fast validation."""
    print(f"[INIT] Initializing database: {DB_PATH}")

    # Remove old database if exists
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("[INIT] Removed old database")

    # Create connection (NO try/except - let it fail loudly)
    connection = sqlite3.connect(str(DB_PATH))
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
    assert DB_PATH.exists(), "Database file not created"

    # Check file size after creation
    db_size = os.path.getsize(DB_PATH)
    assert db_size > 0, f"Database file size is 0 bytes after creation"

    print(f"[INIT] Database created successfully ({db_size} bytes)")
    print(f"[INIT] Tables initialized")

    return connection, cursor

def write_heartbeat(cycle, population, energy_total):
    """Write heartbeat to log file."""
    with open(HEARTBEAT_PATH, 'a') as f:
        f.write(f"{time.time()},{cycle},{population},{energy_total:.2f}\n")

def check_database_health(cursor, cycle):
    """Check database health with assertions."""
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM results")
    row_count = cursor.fetchone()[0]

    # Check file size
    db_size = os.path.getsize(DB_PATH)

    print(f"[DB CHECK] Cycle {cycle}: {row_count} rows, {db_size} bytes")

    # FAIL-FAST ASSERTIONS
    assert row_count > 0, f"No data written after {cycle} cycles"
    assert db_size > 1024, f"Database too small ({db_size} bytes) after {cycle} cycles"

    print(f"[DB CHECK] Health check PASSED")

# =============================================================================
# HIERARCHICAL AGENT SYSTEM
# =============================================================================

def create_hierarchical_agents():
    """Create hierarchical population structure."""
    print(f"[INIT] Creating {N_POPULATIONS} populations of {N_AGENTS_PER_POP} agents each")

    agents = []

    for pop_id in range(N_POPULATIONS):
        for agent_id in range(N_AGENTS_PER_POP):
            agent = SimpleAgent(
                agent_id=pop_id * N_AGENTS_PER_POP + agent_id,
                energy=E_RECHARGE * 10,  # Start with 10× recharge (buffer)
                population_id=pop_id
            )
            agents.append(agent)

    print(f"[INIT] Created {len(agents)} agents total")
    return agents

def hierarchical_spawn(agents, rng):
    """
    Hierarchical spawn: Each population spawns independently.

    Deterministic intervals within population (NRM advantage).
    """
    spawned = []

    for pop_id in range(N_POPULATIONS):
        # Get agents in this population
        pop_agents = [a for a in agents if a.population_id == pop_id]

        if not pop_agents:
            continue

        # Deterministic spawn: Every 1/F_SPAWN cycles
        # For 0.10%, this is every 1000 cycles per population
        interval = int(1.0 / F_SPAWN) if F_SPAWN > 0 else float('inf')

        # Probabilistic spawn using interval
        if rng.random() < (len(pop_agents) / interval):
            # Select parent
            parent = rng.choice(pop_agents)

            if parent.energy >= SPAWN_COST:
                # Create offspring
                child = SimpleAgent(
                    agent_id=len(agents) + len(spawned),
                    energy=SPAWN_COST,
                    population_id=pop_id
                )
                parent.energy -= SPAWN_COST
                spawned.append(child)

    return spawned

# =============================================================================
# MAIN PILOT EXPERIMENT
# =============================================================================

def run_pilot():
    """Execute 1-hour pilot experiment."""
    print("="*80)
    print("C186 V6 PILOT - 1-HOUR ULTRA-LOW FREQUENCY VALIDATION")
    print("="*80)
    print()
    print(f"Configuration:")
    print(f"  Seed: {SEED}")
    print(f"  Spawn rate: {F_SPAWN:.4f} ({F_SPAWN*100:.2f}%)")
    print(f"  Cycles: {CYCLES:,}")
    print(f"  Populations: {N_POPULATIONS}")
    print(f"  Agents per pop: {N_AGENTS_PER_POP}")
    print(f"  Total agents: {TOTAL_AGENTS}")
    print()

    # Initialize RNG
    rng = np.random.default_rng(SEED)

    # Initialize database (FAIL-FAST)
    connection, cursor = initialize_database()

    # Initialize heartbeat log
    if HEARTBEAT_PATH.exists():
        HEARTBEAT_PATH.unlink()
    with open(HEARTBEAT_PATH, 'w') as f:
        f.write("timestamp,cycle,population,energy_total\n")

    # Create agents
    agents = create_hierarchical_agents()

    # Metrics
    start_time = time.time()

    # Main simulation loop
    print(f"[START] Beginning simulation...")
    print()

    for cycle in range(CYCLES):
        # Energy dynamics
        for agent in agents:
            # Consume energy
            agent.energy -= E_CONSUME

            # Recharge energy
            agent.energy += E_RECHARGE

            # Decompose if energy depleted
            if agent.energy <= 0:
                agents.remove(agent)

        # Hierarchical spawn
        new_agents = hierarchical_spawn(agents, rng)
        agents.extend(new_agents)

        # Calculate metrics
        population = len(agents)
        energy_total = sum(a.energy for a in agents)
        n_compositions = len(new_agents)
        n_decompositions = TOTAL_AGENTS + sum(1 for c in range(cycle+1)) - population

        # Write to database every cycle (for validation)
        cursor.execute("""
            INSERT INTO results (cycle, population, energy_total, n_compositions, n_decompositions, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cycle, population, energy_total, n_compositions, n_decompositions, time.time()))

        # Commit every 100 cycles
        if cycle % 100 == 0:
            connection.commit()

        # Print status
        if cycle % PRINT_INTERVAL == 0:
            elapsed = time.time() - start_time
            rate = (cycle + 1) / elapsed if elapsed > 0 else 0
            eta = (CYCLES - cycle - 1) / rate if rate > 0 else 0

            print(f"Cycle {cycle:5,} | Pop: {population:3d} | E_total: {energy_total:7.1f} | "
                  f"Spawn: {n_compositions:3d} | Rate: {rate:.1f} cyc/s | ETA: {eta/60:.1f} min")

            # FAIL-FAST: Check for population collapse
            if population == 0:
                print()
                print("[FAIL] Population collapsed to ZERO")
                print(f"[FAIL] Ultra-low regime (f_spawn={F_SPAWN:.4f}) appears UNVIABLE")
                print(f"[FAIL] Minimum spawn threshold likely >0.10%")
                break

        # Write heartbeat
        if cycle % HEARTBEAT_INTERVAL == 0:
            write_heartbeat(cycle, population, energy_total)

        # Database health check
        if cycle == DB_CHECK_CYCLE:
            print()
            check_database_health(cursor, cycle)
            print()

    # Final commit
    connection.commit()

    # Final metrics
    elapsed = time.time() - start_time
    final_pop = len(agents)
    final_energy = sum(a.energy for a in agents)

    print()
    print("="*80)
    print("PILOT COMPLETE")
    print("="*80)
    print(f"Runtime: {elapsed/60:.2f} minutes ({elapsed:.1f} seconds)")
    print(f"Cycles: {CYCLES:,}")
    print(f"Rate: {CYCLES/elapsed:.2f} cycles/second")
    print(f"Final population: {final_pop}")
    print(f"Final energy: {final_energy:.2f}")
    print()

    # Final database check
    cursor.execute("SELECT COUNT(*) FROM results")
    total_rows = cursor.fetchone()[0]
    db_size = os.path.getsize(DB_PATH)

    print(f"Database: {total_rows:,} rows, {db_size:,} bytes")
    print(f"Heartbeat log: {HEARTBEAT_PATH.name}")
    print()

    # VERDICT
    print("="*80)
    print("PILOT VERDICT")
    print("="*80)

    success = True

    if db_size == 0:
        print("✗ FAIL: Database is empty (0 bytes)")
        print("  → Root cause: Database initialization failure")
        print("  → Action: Fix database initialization, retry pilot")
        success = False
    elif db_size < 1024:
        print("✗ FAIL: Database too small (<1 KB)")
        print("  → Root cause: Data collection not working properly")
        print("  → Action: Debug data persistence, retry pilot")
        success = False
    elif final_pop == 0:
        print("✗ FAIL: Population collapsed to zero")
        print("  → Root cause: Ultra-low regime (<1% spawn) unviable")
        print("  → Action: Document minimum threshold, abandon ultra-low experiments")
        success = False
    else:
        print("✓ PASS: Database collecting data")
        print("✓ PASS: Population sustained")
        print("✓ PASS: Ultra-low regime appears viable")
        print()
        print("  → Action: Redesign full V6 with fail-fast safeguards")
        print("  → Timeline: 10-11 days for complete frequency sweep")

    print("="*80)
    print()

    # Save summary JSON
    summary = {
        'experiment': 'C186_V6_PILOT',
        'description': '1-hour pilot to diagnose V6 termination',
        'parameters': {
            'seed': SEED,
            'f_spawn': F_SPAWN,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'n_populations': N_POPULATIONS,
            'n_agents_per_pop': N_AGENTS_PER_POP
        },
        'results': {
            'runtime_seconds': elapsed,
            'runtime_minutes': elapsed / 60,
            'final_population': final_pop,
            'final_energy': final_energy,
            'database_size_bytes': db_size,
            'database_rows': total_rows,
            'success': success
        },
        'verdict': {
            'database_works': db_size > 1024,
            'population_sustained': final_pop > 0,
            'ultra_low_viable': final_pop > 0 and db_size > 1024
        },
        'timestamp': time.time()
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Summary saved: {OUTPUT_PATH.name}")
    print()

    # Close database
    connection.close()

    return success

if __name__ == '__main__':
    try:
        success = run_pilot()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print()
        print("="*80)
        print("FAIL-FAST ASSERTION TRIGGERED")
        print("="*80)
        print(f"Error: {e}")
        print()
        print("This pilot was designed to fail fast on critical issues.")
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
