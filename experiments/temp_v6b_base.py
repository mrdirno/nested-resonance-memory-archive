#!/usr/bin/env python3
"""
C186 V6b - Net-Positive Growth Regime (Dual-Regime Campaign Part 2)

Purpose: Test hierarchical spawning advantage at ultra-low frequencies under
         net-positive energy conditions enabling population growth (net energy = +0.5).

Duration: TBD (450,000 cycles, likely faster due to population cap)
Conditions: 5 spawn rates (0.10%-1.00%) × 10 seeds = 50 experiments
Energy: E_consume = 0.5, E_recharge = 1.0 (net +0.5, growth regime)

This is Phase 2 of the dual-regime V6 campaign, following V6a (net-zero homeostasis).
Direct comparison of homeostasis vs growth dynamics at ultra-low spawn frequencies.

Background:
- Original V6 failed after 10-11 days (database initialization failure)
- Pilot (C186 V6 Pilot) validated ultra-low regime viability (2.8s, 128x growth)
- Pilot revealed unexpected: Runaway growth at net-positive energy (E_recharge > E_consume)
- Solution: Test BOTH regimes (homeostasis + growth) for comprehensive understanding

Hypothesis:
- Net-positive energy (+0.5) enables population growth similar to pilot (128× in 5000 cycles)
- Population will reach cap (100K agents) quickly despite ultra-low spawn rates
- Hierarchical spawning may show different dynamics in growth vs homeostasis regimes
- Comparison to V6a reveals energy regime's effect on population stability

Decision Tree:
- If similar growth to pilot → Energy regime is primary driver (validates V6a comparison)
- If population stabilizes below cap → Spawn rate limits growth (interesting boundary)
- If population collapses → Unexpected dynamics (revise hypothesis)

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
Date: 2025-11-16
Cycle: 1374
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

# V6b Parameters (NET-POSITIVE GROWTH)
E_CONSUME = 0.5  # Energy consumed per cycle (REDUCED from V6a's 1.0)
E_RECHARGE = 1.0  # Energy recharged per cycle (NET ENERGY = +0.5)
SPAWN_COST = 5.0  # Energy cost to spawn offspring

# Spawn rates (0.10%-1.00%, ultra-low frequency range)
F_SPAWN_VALUES = [0.001, 0.0025, 0.005, 0.0075, 0.01]
SPAWN_LABELS = ["0.10%", "0.25%", "0.50%", "0.75%", "1.00%"]

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

def hierarchical_spawn(agents, f_spawn, rng):
    """
    Hierarchical spawn: Each population spawns independently.

    Deterministic intervals within population (NRM advantage hypothesis).
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
# MAIN EXPERIMENT RUNNER
# =============================================================================

def run_experiment(f_spawn, spawn_label, seed):
    """Execute single V6b experiment."""
    print("="*80)
    print(f"C186 V6b - NET-POSITIVE GROWTH REGIME")
    print("="*80)
    print()
    print(f"Configuration:")
    print(f"  Condition: HIERARCHICAL_GROWTH_{spawn_label}")
    print(f"  Seed: {seed}")
    print(f"  Spawn rate: {f_spawn:.4f} ({spawn_label})")
    print(f"  Energy: E_consume={E_CONSUME}, E_recharge={E_RECHARGE} (net=+0.5)")
    print(f"  Cycles: {CYCLES:,}")
    print(f"  Populations: {N_POPULATIONS}")
    print(f"  Agents per pop: {N_AGENTS_PER_POP}")
    print(f"  Total agents: {INITIAL_AGENTS}")
    print()

    # File paths for this experiment
    condition_name = f"HIERARCHICAL_GROWTH_{spawn_label.replace('.', '_').replace('%', 'pct')}"
    db_path = RESULTS_DIR / f"c186_v6b_{condition_name}_seed{seed}.db"
    heartbeat_path = RESULTS_DIR / f"c186_v6b_{condition_name}_seed{seed}_heartbeat.log"
    json_path = RESULTS_DIR / f"c186_v6b_{condition_name}_seed{seed}.json"

    # Initialize RNG
    rng = np.random.default_rng(seed)

    # Initialize database (FAIL-FAST)
    connection, cursor = initialize_database(db_path)

