#!/usr/bin/env python3
"""
Cycle 276: Universality Test 2 - Topology Variation
====================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1475)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Test β universality across different population topologies to verify that the
energy power law exponent β ≈ 2.19 is independent of inter-population connectivity.

Background:
-----------
Cycle 1472 derivation: β = 2 + ε arises from:
- β = 2: Second-order variance buffering (fundamental)
- ε ≈ 0.19: Logarithmic correction from hierarchy depth L(f)

**Prediction:** β should be invariant across topologies because it arises from
local stochastic dynamics within populations, NOT global connectivity patterns.

**What SHOULD vary:** α (hierarchical efficiency) may change with topology,
as connectivity affects rescue dynamics and risk distribution.

Hypothesis:
-----------
**Null (H0):** β = 2.19 ± 0.3 for ALL topologies
**Alternative (H1):** β varies with topology (connectivity affects scaling)

Experimental Design:
--------------------
**Topologies (4 conditions, all with same n_pop = 10):**

1. **FULLY_CONNECTED (Baseline):**
   - Each population can migrate to any other (9 neighbors each)
   - Current V6 configuration (random target selection)

2. **RING:**
   - Each population connects to 2 neighbors (circular)
   - Migration restricted to adjacent populations only
   - Tests minimal connectivity (k = 2)

3. **STAR:**
   - Central hub connects to all periphery populations
   - Periphery populations only connect to hub
   - Tests hub-and-spoke asymmetry

4. **RANDOM_GRAPH:**
   - Each population connects to 4 random neighbors
   - Tests intermediate connectivity (k = 4)
   - Graph generated once, used for all experiments

**Energy Parameters (Fixed):**
- E_consume = 0.5, E_recharge = 1.0 (V6b baseline, E_net = +0.5)

**Frequency Range (6 log-spaced points):**
f = 0.05%, 0.1%, 0.2%, 0.5%, 1.0%, 2.0%

**Replication:**
- Seeds: 300-309 (n = 10 per condition)
- Total experiments: 4 topologies × 6 frequencies × 10 seeds = **240 experiments**

**Runtime:**
- Cycles: 450,000 per experiment (~3-5 minutes each)
- Total time: ~16 hours sequential

**Hierarchical Configuration:**
- n_pop = 10 (populations)
- f_migrate = 0.5% (same across all topologies)
- Mode = "HIERARCHICAL" (topology-aware migration)

Expected Outcomes:
------------------
**If β is universal (hypothesis validated):**
- Fitted β = 2.19 ± 0.3 for ALL four topologies
- CV(β) < 15% (low variability)
- Power law fits: R² > 0.90 for all topologies

**What SHOULD vary:**
- α (hierarchical efficiency): Connectivity affects rescue mechanism
- Baseline populations: Topology affects equilibrium
- Edge case vulnerability: Some topologies may be more fragile

**If β varies with topology:**
- Different exponents for different connectivity patterns
- May indicate global structure affects local scaling

Success Criteria:
-----------------
- β universality: Mean β = 2.19 ± 0.3, CV(β) < 15%
- All fits: R² > 0.90
- α variation documented (expected, not failure)
"""

import sys
import time
import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from core.fractal_agent import FractalAgent

# ============================================================================
# CONFIGURATION
# ============================================================================

# Experiment metadata
CYCLE_ID = "C276"
CYCLE_NAME = "Universality Test 2: Topology Variation"
AUTHOR = "Aldrin Payopay <aldrin.gdf@gmail.com>"
CO_AUTHOR = "Claude Sonnet 4.5 <noreply@anthropic.com>"

# Output directories
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Energy parameters (fixed at V6b baseline)
ENERGY_PARAMS = {"E_consume": 0.5, "E_recharge": 1.0, "net": +0.5}

# Frequency range
FREQUENCIES = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]

# Replication
SEEDS = list(range(300, 310))  # Seeds 300-309 (n=10)
CYCLES_PER_EXPERIMENT = 450_000
N_POPULATIONS = 10
F_MIGRATE = 0.005
MODE = "HIERARCHICAL"

# ============================================================================
# TOPOLOGY DEFINITIONS
# ============================================================================

def generate_fully_connected(n_pop: int) -> Dict[int, Set[int]]:
    """Generate fully connected topology (complete graph)."""
    return {i: set(range(n_pop)) - {i} for i in range(n_pop)}


def generate_ring(n_pop: int) -> Dict[int, Set[int]]:
    """Generate ring topology (each node connects to 2 neighbors)."""
    return {i: {(i - 1) % n_pop, (i + 1) % n_pop} for i in range(n_pop)}


def generate_star(n_pop: int) -> Dict[int, Set[int]]:
    """Generate star topology (hub at 0, periphery at 1-9)."""
    adjacency = {0: set(range(1, n_pop))}  # Hub connects to all
    for i in range(1, n_pop):
        adjacency[i] = {0}  # Periphery only connects to hub
    return adjacency


def generate_random_graph(n_pop: int, k: int = 4, seed: int = 42) -> Dict[int, Set[int]]:
    """Generate random graph (each node connects to k random neighbors)."""
    np.random.seed(seed)
    adjacency = {i: set() for i in range(n_pop)}

    for i in range(n_pop):
        possible_neighbors = list(set(range(n_pop)) - {i} - adjacency[i])
        n_to_add = max(0, k - len(adjacency[i]))

        if n_to_add > 0 and possible_neighbors:
            neighbors_to_add = np.random.choice(
                possible_neighbors,
                size=min(n_to_add, len(possible_neighbors)),
                replace=False
            )
            for neighbor in neighbors_to_add:
                adjacency[i].add(neighbor)
                adjacency[neighbor].add(i)  # Undirected

    return adjacency


TOPOLOGIES = {
    "FULLY_CONNECTED": {
        "adjacency": generate_fully_connected(N_POPULATIONS),
        "label": "Fully Connected (k=9)"
    },
    "RING": {
        "adjacency": generate_ring(N_POPULATIONS),
        "label": "Ring (k=2)"
    },
    "STAR": {
        "adjacency": generate_star(N_POPULATIONS),
        "label": "Star (hub+9)"
    },
    "RANDOM_GRAPH": {
        "adjacency": generate_random_graph(N_POPULATIONS, k=4),
        "label": "Random (k≈4)"
    }
}

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_single_experiment(
    topology_label: str,
    adjacency: Dict[int, Set[int]],
    f_intra: float,
    seed: int,
    cycles: int = CYCLES_PER_EXPERIMENT
) -> Dict:
    """
    Run single experiment with specified topology, frequency, and seed.
    """
    # Format for filename
    freq_pct = f"{f_intra * 100:.2f}".replace('.', '_')

    # Create database path
    db_path = RESULTS_DIR / f"c276_UNIV_TOPO_{topology_label}_f{freq_pct}pct_seed{seed}.db"

    # Initialize reality interface
    reality = RealityInterface(
        db_path=str(db_path),
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    # Set energy parameters
    reality.energy_config = {
        "E_consume": ENERGY_PARAMS["E_consume"],
        "E_recharge": ENERGY_PARAMS["E_recharge"]
    }

    # Set random seed
    np.random.seed(seed)

    # Initialize agents
    for pop_id in range(N_POPULATIONS):
        for _ in range(10):
            agent = FractalAgent(
                agent_id=f"agent_{pop_id}_{_}",
                population_id=pop_id,
                energy=1.0
            )
            reality.add_agent(agent, population_id=pop_id)

    # Run simulation
    start_time = time.time()

    for cycle in range(cycles):
        # Spawn phase
        if np.random.random() < f_intra:
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

        # Migration phase (topology-aware)
        if np.random.random() < F_MIGRATE:
            source_pop = np.random.randint(0, N_POPULATIONS)
            source_agents = reality.get_population_agents(source_pop)

            if source_agents and adjacency[source_pop]:
                # Select random neighbor according to topology
                target_pop = np.random.choice(list(adjacency[source_pop]))

                migrant = np.random.choice(source_agents)
                reality.migrate_agent(migrant.agent_id, source_pop, target_pop)

        # Death phase
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            for agent in agents:
                agent.energy -= ENERGY_PARAMS["E_consume"]

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    agent.energy = min(agent.energy + ENERGY_PARAMS["E_recharge"], 2.0)

        # Record metrics every 1000 cycles
        if cycle % 1000 == 0:
            total_pop = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
            total_energy = sum(
                sum(a.energy for a in reality.get_population_agents(p))
                for p in range(N_POPULATIONS)
            )

            reality.log_cycle_metrics(
                cycle=cycle,
                population=total_pop,
                energy_total=total_energy,
                n_compositions=0,
                n_decompositions=0
            )

    # Get final population
    final_pop = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
    runtime = time.time() - start_time

    # Close database
    reality.close()

    return {
        "topology": topology_label,
        "frequency": f_intra,
        "seed": seed,
        "final_population": final_pop,
        "cycles": cycles,
        "runtime_seconds": runtime,
        "db_path": str(db_path)
    }


def run_campaign():
    """
    Execute full experimental campaign (240 experiments).
    """
    print("=" * 80)
    print(f"CYCLE 276: UNIVERSALITY TEST 2 - TOPOLOGY VARIATION")
    print(f"Author: {AUTHOR}")
    print(f"Co-Authored-By: {CO_AUTHOR}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nExperimental Design:")
    print(f"  Topologies: {len(TOPOLOGIES)}")
    for label, data in TOPOLOGIES.items():
        print(f"    - {label}: {data['label']}")
    print(f"  Frequencies: {len(FREQUENCIES)} points (0.05% - 2.0%)")
    print(f"  Seeds per condition: {len(SEEDS)}")
    print(f"  Total experiments: {len(TOPOLOGIES) * len(FREQUENCIES) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES_PER_EXPERIMENT:,}")

    results = []
    total_experiments = len(TOPOLOGIES) * len(FREQUENCIES) * len(SEEDS)
    completed = 0

    for topology_label, topology_data in TOPOLOGIES.items():
        adjacency = topology_data["adjacency"]

        for freq in FREQUENCIES:
            print(f"\n{'='*80}")
            print(f"Topology: {topology_label} ({topology_data['label']})")
            print(f"Frequency: {freq*100:.2f}% ({len(SEEDS)} experiments)")
            print(f"{'='*80}")

            freq_results = []

            for seed in SEEDS:
                completed += 1
                print(f"\n[{completed}/{total_experiments}] "
                      f"Running: {topology_label}, f={freq*100:.2f}%, seed={seed}")

                try:
                    result = run_single_experiment(
                        topology_label, adjacency, freq, seed, CYCLES_PER_EXPERIMENT
                    )
                    freq_results.append(result)

                    print(f"  ✓ Complete: {result['final_population']} agents, "
                          f"{result['runtime_seconds']:.1f}s")

                except Exception as e:
                    print(f"  ✗ FAILED: {e}")
                    freq_results.append({
                        "topology": topology_label,
                        "frequency": freq,
                        "seed": seed,
                        "final_population": 0,
                        "error": str(e)
                    })

            # Calculate summary statistics
            populations = [r['final_population'] for r in freq_results if 'error' not in r]

            if populations:
                mean_pop = np.mean(populations)
                std_pop = np.std(populations, ddof=1)

                print(f"\nCondition Summary ({topology_label}, f={freq*100:.2f}%):")
                print(f"  Mean: {mean_pop:.1f}")
                print(f"  Std Dev: {std_pop:.1f}")

            results.extend(freq_results)

    # Save complete results
    results_file = RESULTS_DIR / "c276_universality_topology_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "cycle_name": CYCLE_NAME,
            "date": datetime.now().isoformat(),
            "author": AUTHOR,
            "co_author": CO_AUTHOR,
            "config": {
                "topologies": {k: {"label": v["label"], "adjacency": {kk: list(vv) for kk, vv in v["adjacency"].items()}}
                              for k, v in TOPOLOGIES.items()},
                "energy_params": ENERGY_PARAMS,
                "frequencies": FREQUENCIES,
                "seeds": SEEDS,
                "cycles_per_experiment": CYCLES_PER_EXPERIMENT,
                "n_populations": N_POPULATIONS,
                "f_migrate": F_MIGRATE
            },
            "results": results
        }, f, indent=2)

    print(f"\n{'='*80}")
    print(f"CAMPAIGN COMPLETE")
    print(f"{'='*80}")
    print(f"Total experiments: {len(results)}")
    print(f"Results saved: {results_file}")
    print(f"\nNext: Run analysis to test β universality across topologies")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    run_campaign()
