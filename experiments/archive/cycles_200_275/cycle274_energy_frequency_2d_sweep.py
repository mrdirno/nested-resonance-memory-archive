#!/usr/bin/env python3
"""
Cycle 274: Energy-Frequency 2D Parameter Sweep
===============================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1474)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Validate unified scaling equation E_min^hier(f, E_net) across complete
energy-frequency parameter space to test:

1. Energy regime boundaries (E_net < 0 collapse, E_net ≥ 0 viable)
2. Power law scaling E_min ∝ f^-β within viable regimes
3. Energy-dependent baseline E_∞(E_net) functional form
4. Phase transition at E_net = 0

Background:
-----------
Cycle 1472 theoretical derivation predicts unified governing equation:

E_min^hier(f, E_net) = {
    ∞                              if E_net < 0 (collapse inevitable)
    E_∞(E_net) + A(E_net)/(αf)^β  if E_net ≥ 0 (viable)
}

Where:
- α = 607 (hierarchical efficiency, C186)
- β ≈ 2.19 (energy power law exponent, Cycle 1399 + C1472 derivation)
- E_∞(E_net): Energy-dependent baseline (asymptotic energy as f → ∞)
- A(E_net): Energy-dependent amplitude

Hypothesis:
-----------
1. **Regime Boundary:** 100% collapse for ALL E_net < 0, regardless of frequency
2. **Power Law:** E_min ∝ f^-2.19 for ALL E_net ≥ 0 conditions
3. **Baseline Scaling:** E_∞(E_net) increases linearly with E_net
4. **Phase Transition:** Sharp transition at E_net = 0 (infinite → finite E_min)

Experimental Design:
--------------------
**Energy Parameter Space (8 values):**
E_net = -0.2, -0.1, 0.0, +0.1, +0.2, +0.3, +0.4, +0.5

Implemented via (E_consume, E_recharge) pairs:
- E_net = -0.2: (0.6, 0.4)  [Collapse]
- E_net = -0.1: (0.55, 0.45) [Collapse]
- E_net = 0.0:  (0.5, 0.5)   [Homeostasis boundary]
- E_net = +0.1: (0.45, 0.55) [Growth]
- E_net = +0.2: (0.4, 0.6)   [Growth]
- E_net = +0.3: (0.35, 0.65) [Growth]
- E_net = +0.4: (0.3, 0.7)   [Growth]
- E_net = +0.5: (0.5, 1.0)   [Growth, V6b baseline]

**Frequency Range (6 log-spaced points):**
f = 0.05%, 0.1%, 0.2%, 0.5%, 1.0%, 2.0%
f = 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02

Coverage: 40× range (2.5 orders of magnitude)

**Replication:**
- Seeds: 100-109 (n = 10 per condition)
- Total experiments: 8 energies × 6 frequencies × 10 seeds = **480 experiments**

**Runtime:**
- Cycles: 450,000 per experiment (~3-5 minutes each)
- Total estimated time: 480 × 4 min = **~32 hours sequential**

**Hierarchical Configuration:**
- n_pop = 10 (populations)
- f_migrate = 0.5% (inter-population migration)
- Mode = "HIERARCHICAL"

Expected Outcomes:
------------------
**If hypothesis correct:**
1. Collapse regime (E_net < 0): N_final = 0 for all frequencies
2. Viable regimes (E_net ≥ 0): Power law E_min ∝ f^-2.19 with different baselines
3. Homeostasis (E_net = 0): Marginal viability, high variance
4. 2D surface plot shows clear phase boundary at E_net = 0

**If hypothesis incorrect:**
- Non-universal β (different exponents at different E_net)
- Gradual transition instead of sharp boundary
- Frequency-dependent regime boundaries

Success Criteria:
-----------------
- β = 2.19 ± 0.3 for ALL E_net ≥ 0 conditions (universal exponent)
- 100% collapse for ALL E_net < 0 conditions (sharp boundary)
- E_∞(E_net) shows systematic variation with net energy
- R² > 0.90 for power law fits in viable regimes

Connection to Unified Framework:
---------------------------------
This experiment directly tests the unified governing equation derived in
Cycle 1472. Success validates:

1. Energy regime boundaries are sharp (thermodynamic constraint)
2. Power law scaling is universal across energy conditions
3. Hierarchical efficiency operates within energy constraints
4. Unified framework accurately describes multi-dimensional parameter space
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

from core.fractal_agent import FractalAgent, RealityInterface

# ============================================================================
# CONFIGURATION
# ============================================================================

# Experiment metadata
CYCLE_ID = "C274"
CYCLE_NAME = "Energy-Frequency 2D Parameter Sweep"
AUTHOR = "Aldrin Payopay <aldrin.gdf@gmail.com>"
CO_AUTHOR = "Claude Sonnet 4.5 <noreply@anthropic.com>"

# Output directories
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Energy parameter space (8 conditions)
ENERGY_CONDITIONS = {
    "E_net_minus0.2": {"E_consume": 0.6, "E_recharge": 0.4, "net": -0.2, "regime": "COLLAPSE"},
    "E_net_minus0.1": {"E_consume": 0.55, "E_recharge": 0.45, "net": -0.1, "regime": "COLLAPSE"},
    "E_net_0.0": {"E_consume": 0.5, "E_recharge": 0.5, "net": 0.0, "regime": "HOMEOSTASIS"},
    "E_net_plus0.1": {"E_consume": 0.45, "E_recharge": 0.55, "net": +0.1, "regime": "GROWTH"},
    "E_net_plus0.2": {"E_consume": 0.4, "E_recharge": 0.6, "net": +0.2, "regime": "GROWTH"},
    "E_net_plus0.3": {"E_consume": 0.35, "E_recharge": 0.65, "net": +0.3, "regime": "GROWTH"},
    "E_net_plus0.4": {"E_consume": 0.3, "E_recharge": 0.7, "net": +0.4, "regime": "GROWTH"},
    "E_net_plus0.5": {"E_consume": 0.5, "E_recharge": 1.0, "net": +0.5, "regime": "GROWTH"}
}

# Frequency range (6 log-spaced points)
FREQUENCIES = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]  # 0.05% - 2.0%

# Replication
SEEDS = list(range(100, 110))  # Seeds 100-109 (n=10)
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
    Run single experiment at specified energy condition, frequency, and seed.

    Args:
        energy_label: Energy condition label (e.g., "E_net_plus0.5")
        energy_params: Energy parameters dict
        f_intra: Intra-population spawn frequency
        seed: Random seed for reproducibility
        cycles: Number of simulation cycles

    Returns:
        Dict with experiment results
    """
    # Format energy and frequency for filename
    freq_pct = f"{f_intra * 100:.2f}".replace('.', '_')

    # Create database path
    db_path = RESULTS_DIR / f"c274_2D_SWEEP_{energy_label}_f{freq_pct}pct_seed{seed}.db"

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
            # Select random population for spawn
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
            # Select random source population
            source_pop = np.random.randint(0, N_POPULATIONS)
            source_agents = reality.get_population_agents(source_pop)

            if source_agents:
                # Select random target population (different from source)
                target_pop = np.random.randint(0, N_POPULATIONS - 1)
                if target_pop >= source_pop:
                    target_pop += 1

                # Migrate random agent
                migrant = np.random.choice(source_agents)
                reality.migrate_agent(migrant.agent_id, source_pop, target_pop)

        # Death phase (energy-based)
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            for agent in agents:
                # Consume energy
                agent.energy -= energy_params["E_consume"]

                # Death if energy depleted
                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    # Recharge surviving agents
                    agent.energy = min(agent.energy + energy_params["E_recharge"], 2.0)

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
        "E_net": energy_params["net"],
        "E_consume": energy_params["E_consume"],
        "E_recharge": energy_params["E_recharge"],
        "regime": energy_params["regime"],
        "frequency": f_intra,
        "seed": seed,
        "final_population": final_pop,
        "cycles": cycles,
        "runtime_seconds": runtime,
        "db_path": str(db_path)
    }


def run_campaign():
    """
    Execute full experimental campaign (480 experiments).
    """
    print("=" * 80)
    print(f"CYCLE 274: ENERGY-FREQUENCY 2D PARAMETER SWEEP")
    print(f"Author: {AUTHOR}")
    print(f"Co-Authored-By: {CO_AUTHOR}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nExperimental Design:")
    print(f"  Energy conditions: {len(ENERGY_CONDITIONS)} (E_net: -0.2 to +0.5)")
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
            print(f"Energy: {energy_label} (E_net = {energy_params['net']:+.1f}, "
                  f"Regime: {energy_params['regime']})")
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
                        "E_net": energy_params["net"],
                        "frequency": freq,
                        "seed": seed,
                        "final_population": 0,
                        "error": str(e)
                    })

            # Calculate summary statistics for this condition
            populations = [r['final_population'] for r in freq_results if 'error' not in r]

            if populations:
                mean_pop = np.mean(populations)
                std_pop = np.std(populations, ddof=1)

                print(f"\nCondition Summary ({energy_label}, f={freq*100:.2f}%):")
                print(f"  Mean: {mean_pop:.1f}")
                print(f"  Std Dev: {std_pop:.1f}")
                print(f"  Collapse: {sum(p == 0 for p in populations)}/{len(populations)}")

            results.extend(freq_results)

    # Save complete results
    results_file = RESULTS_DIR / "c274_energy_frequency_2d_sweep_results.json"
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
    print(f"\nNext: Run analysis script to fit 2D surface and validate unified equation")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    run_campaign()
