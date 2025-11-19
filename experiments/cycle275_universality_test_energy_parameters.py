#!/usr/bin/env python3
"""
Cycle 275: Universality Test 1 - Energy Parameter Variation
============================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1475)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Test β universality across different energy parameter magnitudes to verify that
the energy power law exponent β ≈ 2.19 is independent of absolute energy scale.

Background:
-----------
Cycle 1472 theoretical derivation predicts β = 2 + ε ≈ 2.19 arises from:
- β = 2: Second-order variance buffering (fundamental stochastic requirement)
- ε ≈ 0.19: Logarithmic correction from hierarchy depth

**Prediction:** β should be **invariant** across different (E_consume, E_recharge)
pairs AS LONG AS E_net > 0 (viable regime), because β arises from stochastic
dynamics, not absolute energy magnitudes.

**What should vary:** Baseline population E_∞ (higher energy → higher equilibrium)

Hypothesis:
-----------
**Null (H0):** β = 2.19 ± 0.3 for ALL energy parameter sets with E_net = +0.5
**Alternative (H1):** β varies with absolute energy magnitude

Experimental Design:
--------------------
**Energy Parameter Sets (3 conditions, all with E_net = +0.5):**

1. **Low Energy:**
   - E_consume = 0.5, E_recharge = 1.0
   - Net = +0.5 (baseline, V6b configuration)

2. **Medium Energy:**
   - E_consume = 1.0, E_recharge = 1.5
   - Net = +0.5 (2× energy scale)

3. **High Energy:**
   - E_consume = 1.5, E_recharge = 2.0
   - Net = +0.5 (3× energy scale)

**Rationale:** Keep E_net constant (+0.5) while varying absolute magnitude.
Tests if β depends on energy scale or just net energy availability.

**Frequency Range (6 log-spaced points):**
f = 0.05%, 0.1%, 0.2%, 0.5%, 1.0%, 2.0%
f = 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02

**Replication:**
- Seeds: 200-209 (n = 10 per condition)
- Total experiments: 3 energy sets × 6 frequencies × 10 seeds = **180 experiments**

**Runtime:**
- Cycles: 450,000 per experiment (~3-5 minutes each)
- Total time: ~12 hours sequential

**Hierarchical Configuration:**
- n_pop = 10 (populations)
- f_migrate = 0.5% (inter-population migration)
- Mode = "HIERARCHICAL"

Expected Outcomes:
------------------
**If β is universal (hypothesis validated):**
- Fitted β = 2.19 ± 0.3 for ALL three energy conditions
- CV(β) < 15% (low variability)
- Power law fits: R² > 0.90 for all conditions

**What SHOULD vary:**
- Baseline populations: Higher energy → higher E_∞
- Absolute population magnitudes (N scales with available energy)

**If β varies with energy scale:**
- Different exponents at different energy magnitudes
- May indicate energy-dependent corrections to β = 2 + ε

Success Criteria:
-----------------
- β universality: Mean β = 2.19 ± 0.3, CV(β) < 15%
- All fits: R² > 0.90
- Baseline scaling: E_∞ increases linearly with energy magnitude
"""

import sys
import time
import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from core.fractal_agent import FractalAgent

# ============================================================================
# CONFIGURATION
# ============================================================================

# Experiment metadata
CYCLE_ID = "C275"
CYCLE_NAME = "Universality Test 1: Energy Parameter Variation"
AUTHOR = "Aldrin Payopay <aldrin.gdf@gmail.com>"
CO_AUTHOR = "Claude Sonnet 4.5 <noreply@anthropic.com>"

# Output directories
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Energy parameter sets (all with E_net = +0.5)
ENERGY_CONDITIONS = {
    "LOW_ENERGY": {"E_consume": 0.5, "E_recharge": 1.0, "net": +0.5, "label": "Low (1×)"},
    "MED_ENERGY": {"E_consume": 1.0, "E_recharge": 1.5, "net": +0.5, "label": "Med (2×)"},
    "HIGH_ENERGY": {"E_consume": 1.5, "E_recharge": 2.0, "net": +0.5, "label": "High (3×)"}
}

# Frequency range (6 log-spaced points)
FREQUENCIES = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]  # 0.05% - 2.0%

# Replication
SEEDS = list(range(200, 210))  # Seeds 200-209 (n=10)
CYCLES_PER_EXPERIMENT = 450_000
N_POPULATIONS = 10
F_MIGRATE = 0.005  # 0.5%
MODE = "HIERARCHICAL"

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_single_experiment(
    energy_label: str,
    energy_params: Dict,
    f_intra: float,
    seed: int,
    cycles: int = CYCLES_PER_EXPERIMENT
) -> Dict:
    """
    Run single experiment at specified energy parameters, frequency, and seed.
    """
    # Format for filename
    freq_pct = f"{f_intra * 100:.2f}".replace('.', '_')

    # Create database path
    db_path = RESULTS_DIR / f"c275_UNIV_ENERGY_{energy_label}_f{freq_pct}pct_seed{seed}.db"

    # Initialize reality interface
    reality = RealityInterface(
        db_path=str(db_path),
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    # Set energy parameters
    reality.energy_config = {
        "E_consume": energy_params["E_consume"],
        "E_recharge": energy_params["E_recharge"]
    }

    # Set random seed
    np.random.seed(seed)

    # Initialize agents (10 initial agents per population)
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

        # Migration phase
        if np.random.random() < F_MIGRATE:
            source_pop = np.random.randint(0, N_POPULATIONS)
            source_agents = reality.get_population_agents(source_pop)

            if source_agents:
                target_pop = np.random.randint(0, N_POPULATIONS - 1)
                if target_pop >= source_pop:
                    target_pop += 1

                migrant = np.random.choice(source_agents)
                reality.migrate_agent(migrant.agent_id, source_pop, target_pop)

        # Death phase (energy-based)
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            for agent in agents:
                agent.energy -= energy_params["E_consume"]

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    agent.energy = min(agent.energy + energy_params["E_recharge"], 5.0)

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
        "energy_label": energy_label,
        "E_consume": energy_params["E_consume"],
        "E_recharge": energy_params["E_recharge"],
        "E_net": energy_params["net"],
        "frequency": f_intra,
        "seed": seed,
        "final_population": final_pop,
        "cycles": cycles,
        "runtime_seconds": runtime,
        "db_path": str(db_path)
    }


def run_campaign():
    """
    Execute full experimental campaign (180 experiments).
    """
    print("=" * 80)
    print(f"CYCLE 275: UNIVERSALITY TEST 1 - ENERGY PARAMETER VARIATION")
    print(f"Author: {AUTHOR}")
    print(f"Co-Authored-By: {CO_AUTHOR}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nExperimental Design:")
    print(f"  Energy conditions: {len(ENERGY_CONDITIONS)} (all E_net = +0.5)")
    print(f"  Frequencies: {len(FREQUENCIES)} points (0.05% - 2.0%)")
    print(f"  Seeds per condition: {len(SEEDS)}")
    print(f"  Total experiments: {len(ENERGY_CONDITIONS) * len(FREQUENCIES) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES_PER_EXPERIMENT:,}")

    results = []
    total_experiments = len(ENERGY_CONDITIONS) * len(FREQUENCIES) * len(SEEDS)
    completed = 0

    for energy_label, energy_params in ENERGY_CONDITIONS.items():
        for freq in FREQUENCIES:
            print(f"\n{'='*80}")
            print(f"Energy: {energy_label} ({energy_params['label']}, "
                  f"E_consume={energy_params['E_consume']}, E_recharge={energy_params['E_recharge']})")
            print(f"Frequency: {freq*100:.2f}% ({len(SEEDS)} experiments)")
            print(f"{'='*80}")

            freq_results = []

            for seed in SEEDS:
                completed += 1
                print(f"\n[{completed}/{total_experiments}] "
                      f"Running: {energy_label}, f={freq*100:.2f}%, seed={seed}")

                try:
                    result = run_single_experiment(
                        energy_label, energy_params, freq, seed, CYCLES_PER_EXPERIMENT
                    )
                    freq_results.append(result)

                    print(f"  ✓ Complete: {result['final_population']} agents, "
                          f"{result['runtime_seconds']:.1f}s")

                except Exception as e:
                    print(f"  ✗ FAILED: {e}")
                    freq_results.append({
                        "energy_label": energy_label,
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

                print(f"\nCondition Summary ({energy_label}, f={freq*100:.2f}%):")
                print(f"  Mean: {mean_pop:.1f}")
                print(f"  Std Dev: {std_pop:.1f}")

            results.extend(freq_results)

    # Save complete results
    results_file = RESULTS_DIR / "c275_universality_energy_parameters_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "cycle_name": CYCLE_NAME,
            "date": datetime.now().isoformat(),
            "author": AUTHOR,
            "co_author": CO_AUTHOR,
            "config": {
                "energy_conditions": ENERGY_CONDITIONS,
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
    print(f"\nNext: Run analysis to test β universality across energy conditions")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    run_campaign()
