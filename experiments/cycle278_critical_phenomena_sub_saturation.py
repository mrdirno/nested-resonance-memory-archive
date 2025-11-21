#!/usr/bin/env python3
"""
Cycle 278: Critical Phenomena II - Sub-Saturation Regime
========================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Gemini 3 Pro (MOG Pilot)
Date: 2025-11-20 (Cycle 118)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Locate the critical frequency f_crit and measure critical exponents in the 
sub-saturation regime (0.001% - 0.01%).

"""

import sys
import time
import json
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.fractal_agent import FractalAgent, RealityInterface

# ============================================================================
# CONFIGURATION
# ============================================================================

CYCLE_ID = "C278"
CYCLE_NAME = "Critical Phenomena II (Sub-Saturation)"
AUTHOR = "Aldrin Payopay <aldrin.gdf@gmail.com>"
CO_AUTHOR = "Gemini 3 Pro (MOG Pilot)"

# Paths
BASE_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2")
EXPERIMENTS_DIR = BASE_DIR / "experiments"
RESULTS_DIR = EXPERIMENTS_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Simulation Parameters
CYCLES_PER_EXPERIMENT = 450000
N_POPULATIONS = 10
F_MIGRATE = 0.005  # 0.5%
MODE = "HIERARCHICAL"

# Energy Parameters (V6b Baseline)
ENERGY_PARAMS = {
    "E_consume": 0.5,
    "E_recharge": 1.0
}

# Frequencies to test (0.001% to 0.010%)
FREQUENCIES = [0.00001, 0.00002, 0.00003, 0.00004, 0.00005, 
               0.00006, 0.00007, 0.00008, 0.00009, 0.00010]

# Seeds (20 per frequency)
SEEDS = list(range(500, 520))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_fully_connected(n_pop: int) -> Dict[int, Set[int]]:
    """Generate fully connected topology (complete graph)."""
    return {i: set(range(n_pop)) - {i} for i in range(n_pop)}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# ============================================================================
# EXPERIMENT RUNNER
# ============================================================================

def run_experiment(freq, seed):
    """Run a single experiment."""
    print(f"Running: f={freq*100:.3f}%, seed={seed}")
    sys.stdout.flush()
    
    start_time = time.time()
    
    # Format for filename
    freq_pct = f"{freq * 100:.3f}".replace('.', '_')
    db_path = RESULTS_DIR / f"c278_CRIT_SUB_{freq_pct}pct_seed{seed}.db"
    
    # Initialize Reality
    reality = RealityInterface(
        db_path=str(db_path),
        n_populations=N_POPULATIONS,
        mode=MODE
    )
    
    reality.energy_config = ENERGY_PARAMS
    np.random.seed(seed)
    
    # Initialize Agents (10 per population)
    for pop_id in range(N_POPULATIONS):
        for _ in range(10):
            agent = FractalAgent(
                agent_id=f"agent_{pop_id}_{_}",
                population_id=pop_id,
                energy=1.0
            )
            reality.add_agent(agent, population_id=pop_id)
            
    # Topology
    adjacency = generate_fully_connected(N_POPULATIONS)
    
    # Metrics tracking
    equilibration_time = -1
    last_pop = 100
    stable_count = 0
    
    # Simulation Loop
    for cycle in range(CYCLES_PER_EXPERIMENT):
        # Spawn
        if np.random.random() < freq:
            pop_id = np.random.randint(0, N_POPULATIONS)
            agents = reality.get_population_agents(pop_id)
            if agents:
                parent = np.random.choice(agents)
                child = FractalAgent(
                    agent_id=f"spawn_{cycle}_{pop_id}",
                    population_id=pop_id,
                    energy=0.5
                )
                reality.add_agent(child, population_id=pop_id)
                
        # Migrate
        if np.random.random() < F_MIGRATE:
            source_pop = np.random.randint(0, N_POPULATIONS)
            source_agents = reality.get_population_agents(source_pop)
            if source_agents and adjacency[source_pop]:
                target_pop = np.random.choice(list(adjacency[source_pop]))
                migrant = np.random.choice(source_agents)
                reality.migrate_agent(migrant.agent_id, source_pop, target_pop)
                
        # Death / Metabolism / Reproduction
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            n_agents = len(agents)
            
            # Resource Sharing (Inflow = 5.0 per population)
            # Capacity K = Inflow / E_consume = 5.0 / 0.1 = 50 agents
            resource_inflow = 5.0
            energy_gain = resource_inflow / n_agents if n_agents > 0 else 0
            
            # Create a copy for iteration to allow modification
            for agent in list(agents):
                # 1. Metabolism
                agent.energy -= 0.1  # E_consume
                
                # 2. Resource Gain
                agent.energy += energy_gain
                
                # 3. Death
                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                    continue
                    
                # 4. Reproduction (Non-linearity)
                # If energy is high, reproduce (Cost 0.5)
                if agent.energy > 1.5:
                    agent.energy -= 0.5
                    child = FractalAgent(
                        agent_id=f"rep_{cycle}_{pop_id}_{agent.agent_id[-4:]}",
                        population_id=pop_id,
                        energy=0.5
                    )
                    reality.add_agent(child, population_id=pop_id)
                    
        # Check Equilibration (every 1000 cycles)
        if cycle % 1000 == 0:
            total_pop = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
            
            # Simple equilibration check: stable population for 50k cycles
            if abs(total_pop - last_pop) < 5:
                stable_count += 1
            else:
                stable_count = 0
                
            if stable_count >= 50 and equilibration_time == -1:
                equilibration_time = cycle
                
            last_pop = total_pop
            
            # Early exit if extinction
            if total_pop == 0:
                break
                
    runtime = time.time() - start_time
    final_pop = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
    
    print(f"  ✓ Complete: {final_pop} agents, τ={equilibration_time if equilibration_time > 0 else 'N/A'}, {runtime:.1f}s")
    sys.stdout.flush()

    # Close database connection
    reality.close()
    
    return {
        "frequency": freq,
        "seed": seed,
        "final_population": final_pop,
        "equilibration_time": equilibration_time,
        "runtime_seconds": runtime,
        "db_path": str(db_path)
    }

def run_campaign():
    """Execute full experimental campaign."""
    print("=" * 80)
    print(f"{CYCLE_ID}: {CYCLE_NAME}")
    print(f"Author: {AUTHOR}")
    print(f"Co-Authored-By: {CO_AUTHOR}")
    print("=" * 80)
    
    results = []
    total_exps = len(FREQUENCIES) * len(SEEDS)
    current_exp = 0
    
    for freq in FREQUENCIES:
        freq_results = []
        print(f"\nFrequency: {freq*100:.3f}% ({len(SEEDS)} experiments)")
        print("-" * 40)
        
        for seed in SEEDS:
            current_exp += 1
            print(f"[{current_exp}/{total_exps}] ", end="")
            
            try:
                res = run_experiment(freq, seed)
                freq_results.append(res)
            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                freq_results.append({
                    "frequency": freq,
                    "seed": seed,
                    "error": str(e)
                })
        
        # Summary for this frequency
        pops = [r['final_population'] for r in freq_results if 'error' not in r]
        if pops:
            mean_pop = np.mean(pops)
            var_pop = np.var(pops, ddof=1)
            print(f"Summary (f={freq*100:.3f}%): Mean Pop={mean_pop:.1f}, Var={var_pop:.1f}")
            
        results.extend(freq_results)

    # Save Results
    results_file = RESULTS_DIR / "c278_critical_phenomena_sub_saturation_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "cycle_name": CYCLE_NAME,
            "date": datetime.now().isoformat(),
            "author": AUTHOR,
            "co_author": CO_AUTHOR,
            "config": {
                "frequencies": FREQUENCIES,
                "seeds": SEEDS,
                "cycles_per_experiment": CYCLES_PER_EXPERIMENT,
                "n_populations": N_POPULATIONS,
                "f_migrate": F_MIGRATE,
                "energy_params": ENERGY_PARAMS
            },
            "results": results
        }, f, indent=2, cls=NumpyEncoder)
        
    print(f"\n{'='*80}")
    print(f"CAMPAIGN COMPLETE")
    print(f"Results saved: {results_file}")

if __name__ == "__main__":
    run_campaign()
