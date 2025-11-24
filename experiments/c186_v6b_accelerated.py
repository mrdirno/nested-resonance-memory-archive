#!/usr/bin/env python3
"""
C186 V6b - Net-Positive Growth Regime (ACCELERATED)

Purpose: ACCELERATED execution of V6b to validate runaway growth hypothesis within cycle limits.
         Testing 5 spawn rates with single seed for 5000 cycles (vs 450,000).

Duration: ~1-2 minutes
Conditions: 5 spawn rates (0.10%-1.00%) × 1 seed = 5 experiments
Energy: E_consume = 0.5, E_recharge = 1.0 (net +0.5, growth regime)
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
# CONFIGURATION (ACCELERATED)
# =============================================================================

# V6b Parameters (NET-POSITIVE GROWTH)
E_CONSUME = 0.5
E_RECHARGE = 1.0
SPAWN_COST = 5.0

# Spawn rates
F_SPAWN_VALUES = [0.001, 0.0025, 0.005, 0.0075, 0.01]
SPAWN_LABELS = ["0.10%", "0.25%", "0.50%", "0.75%", "1.00%"]

# Seeds (Single seed for acceleration)
SEEDS = [42]

# Hierarchical configuration
N_POPULATIONS = 10
N_AGENTS_PER_POP = 10
INITIAL_AGENTS = N_POPULATIONS * N_AGENTS_PER_POP

# Experimental timeline (ACCELERATED)
CYCLES = 10_000  # Enough to see runaway growth (pilot used 5000)
PRINT_INTERVAL = 1_000
HEARTBEAT_INTERVAL = 1_000
DB_CHECK_CYCLE = 5_000
JSON_BACKUP_INTERVAL = 5_000

# Safeguards
POPULATION_CAP = 100_000
ENERGY_CAP = 10_000_000

# File paths
RESULTS_DIR = Path("experiments/results/v6b_accel")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# UTILS
# =============================================================================

def initialize_database(db_path):
    if db_path.exists():
        db_path.unlink()
    
    connection = sqlite3.connect(str(db_path))
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            cycle INTEGER,
            population INTEGER,
            energy_total REAL,
            n_compositions INTEGER,
            n_decompositions INTEGER,
            timestamp REAL
        )
    """ )
    connection.commit()
    return connection, cursor

def create_hierarchical_agents():
    agents = []
    for pop_id in range(N_POPULATIONS):
        for agent_id in range(N_AGENTS_PER_POP):
            agent = SimpleAgent(
                agent_id=pop_id * N_AGENTS_PER_POP + agent_id,
                energy=E_RECHARGE * 10,
                population_id=pop_id
            )
            agents.append(agent)
    return agents

def hierarchical_spawn(agents, f_spawn, rng):
    spawned = []
    for pop_id in range(N_POPULATIONS):
        pop_agents = [a for a in agents if a.population_id == pop_id]
        if not pop_agents: continue
        
        interval = int(1.0 / f_spawn) if f_spawn > 0 else float('inf')
        
        if rng.random() < (len(pop_agents) / interval):
            parent = rng.choice(pop_agents)
            if parent.energy >= SPAWN_COST:
                child = SimpleAgent(
                    agent_id=len(agents) + len(spawned),
                    energy=SPAWN_COST,
                    population_id=pop_id
                )
                parent.energy -= SPAWN_COST
                spawned.append(child)
    return spawned

def run_experiment(f_spawn, spawn_label, seed):
    condition_name = f"ACCEL_GROWTH_{spawn_label.replace('.', '_').replace('%', 'pct')}"
    db_path = RESULTS_DIR / f"c186_v6b_{condition_name}_seed{seed}.db"
    json_path = RESULTS_DIR / f"c186_v6b_{condition_name}_seed{seed}.json"

    print(f"Running {condition_name} (Seed {seed})...")
    
    rng = np.random.default_rng(seed)
    connection, cursor = initialize_database(db_path)
    agents = create_hierarchical_agents()
    
    start_time = time.time()
    n_decompositions_total = 0
    
    for cycle in range(CYCLES):
        # Energy
        for agent in agents[:]:
            agent.energy = agent.energy - E_CONSUME + E_RECHARGE
            if agent.energy <= 0:
                agents.remove(agent)
                n_decompositions_total += 1
                
        # Spawn
        new_agents = hierarchical_spawn(agents, f_spawn, rng)
        agents.extend(new_agents)
        
        population = len(agents)
        energy_total = sum(a.energy for a in agents)
        
        # Database
        cursor.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?, ?)", 
                      (cycle, population, energy_total, len(new_agents), n_decompositions_total, time.time()))
        
        if cycle % 1000 == 0: connection.commit()
        
        if population > POPULATION_CAP:
            print(f"  [STOP] Cap reached: {population} agents")
            break
            
    connection.commit()
    connection.close()
    
    elapsed = time.time() - start_time
    final_pop = len(agents)
    
    print(f"  Done. Pop: {final_pop}, Time: {elapsed:.2f}s")
    
    # Save summary
    summary = {
        'experiment': 'C186_V6b_ACCEL',
        'condition': condition_name,
        'f_spawn': f_spawn,
        'final_population': final_pop,
        'cycles_run': cycle,
        'success': final_pop > INITIAL_AGENTS # Growth check
    }
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
        
    return summary

def main():
    print("="*60)
    print("V6b ACCELERATED CAMPAIGN")
    print("="*60)
    
    results = []
    for f_spawn, label in zip(F_SPAWN_VALUES, SPAWN_LABELS):
        for seed in SEEDS:
            res = run_experiment(f_spawn, label, seed)
            results.append(res)
            
    print("\nSummary:")
    for r in results:
        status = "GROWTH" if r['success'] else "STABLE/LOSS"
        print(f"{r['condition']}: Pop {r['final_population']} ({status})")
        
    # Save overall summary
    with open(RESULTS_DIR / "campaign_summary.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
