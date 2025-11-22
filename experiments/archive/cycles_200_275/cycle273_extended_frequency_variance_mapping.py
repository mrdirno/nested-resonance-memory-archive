#!/usr/bin/env python3
"""
Cycle 273: Extended Frequency-Variance Mapping
==============================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1473)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Validate variance power law exponent γ ≈ 3.2 across extended frequency range
to test unified scaling framework prediction: σ²(f) ∝ f^-γ where γ = β + 1.

Background:
-----------
Cycle 1471 discovery: V6b growth regime (E_net = +0.5) shows variance scaling
σ² decreases 740× from f=0.10% (σ²=10,244) to f=1.00% (σ²=14).

Preliminary power law fit: γ_obs ≈ 3.2 (measured over 5 frequency points)

Theoretical prediction (Cycle 1472): γ = β + 1 = 2.19 + 1 = 3.19 ≈ 3.2

Hypothesis:
-----------
Variance scaling σ²(f) ∝ f^-3.2 should hold across 3 orders of magnitude
(0.01% - 10%) in growth regime (E_net > 0).

Experimental Design:
--------------------
**Regime:** V6b (Growth)
- E_consume = 0.5
- E_recharge = 1.0
- Net energy = +0.5 (energy surplus, growth)

**Frequencies (log-spaced, 10 points):**
- 0.01%, 0.02%, 0.05%, 0.10%, 0.20%, 0.50%, 1.00%, 2.00%, 5.00%, 10.00%
- Spans 3 orders of magnitude (0.01% - 10%)
- Includes both near-threshold (0.01% ≈ 1.5× f_crit) and far-above-threshold (10%)

**Replication:**
- Seeds: 42-61 (n = 20 per frequency point)
- Total experiments: 10 frequencies × 20 seeds = 200 experiments

**Runtime:**
- Cycles: 450,000 per experiment (~3-5 minutes each)
- Total estimated time: 200 × 4 min = ~13-14 hours sequential

**Hierarchical Configuration:**
- n_pop = 10 (populations)
- f_migrate = 0.5% (inter-population migration)
- Mode = "HIERARCHICAL"

Expected Outcomes:
------------------
**If hypothesis correct:**
- Log-log plot of σ² vs f shows linear relationship
- Slope: -3.2 ± 0.2 (confirming γ = β + 1)
- R² > 0.95 (strong power law fit)

**If hypothesis incorrect:**
- Non-linear relationship on log-log plot
- Exponent significantly different from 3.2
- May indicate frequency-dependent corrections or regime boundaries

Analysis:
---------
1. Load final population from each experiment (last cycle)
2. Calculate variance across 20 seeds for each frequency
3. Fit power law: σ²(f) = A × f^-γ using log-log linear regression
4. Compare fitted γ to predicted γ = 3.19
5. Test for deviations at extreme frequencies (near f_crit or high f)

Success Criteria:
-----------------
- γ_fitted = 3.2 ± 0.3 (within 10% of prediction)
- R² > 0.90 (strong power law fit)
- No systematic deviations at frequency extremes

Connection to Unified Framework:
---------------------------------
This experiment directly validates the mechanistic relationship:

σ²(f) ∝ |dE_min/df| ∝ f^-(β+1)

Where β ≈ 2.19 (energy power law exponent, validated Cycle 1399)
Therefore γ = β + 1 ≈ 3.19

Success confirms:
1. Variance scaling is derivative of energy scaling (mechanistic link)
2. β and γ are universal exponents (hold across frequency ranges)
3. Unified framework accurately predicts multi-scale relationships
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
CYCLE_ID = "C273"
CYCLE_NAME = "Extended Frequency-Variance Mapping"
AUTHOR = "Aldrin Payopay <aldrin.gdf@gmail.com>"
CO_AUTHOR = "Claude Sonnet 4.5 <noreply@anthropic.com>"

# Output directories
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Experimental parameters
FREQUENCIES = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10]  # 0.01% - 10%
SEEDS = list(range(42, 62))  # Seeds 42-61 (n=20)
CYCLES_PER_EXPERIMENT = 450_000
N_POPULATIONS = 10
F_MIGRATE = 0.005  # 0.5%
MODE = "HIERARCHICAL"

# V6b Growth Regime parameters
ENERGY_PARAMS_V6B = {
    "E_consume": 0.5,
    "E_recharge": 1.0,
    "net_energy": +0.5,
    "regime": "GROWTH"
}

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def run_single_experiment(
    f_intra: float,
    seed: int,
    cycles: int = CYCLES_PER_EXPERIMENT
) -> Dict:
    """
    Run single experiment at specified frequency and seed.

    Args:
        f_intra: Intra-population spawn frequency
        seed: Random seed for reproducibility
        cycles: Number of simulation cycles

    Returns:
        Dict with experiment results
    """
    # Initialize random seed for reproducibility
    np.random.seed(seed)

    # Format frequency for filename (0.01% -> 0_01pct)
    freq_pct = f"{f_intra * 100:.2f}".replace('.', '_')

    # Create database path
    db_path = RESULTS_DIR / f"c273_v6b_EXTENDED_VARIANCE_{freq_pct}pct_seed{seed}.db"

    # Initialize reality interface
    reality = RealityInterface(
        db_path=str(db_path),
        n_populations=N_POPULATIONS,
        mode=MODE
    )

    # Set energy parameters (V6b growth regime)
    reality.energy_config = {
        "E_consume": ENERGY_PARAMS_V6B["E_consume"],
        "E_recharge": ENERGY_PARAMS_V6B["E_recharge"]
    }

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
                agent.energy -= ENERGY_PARAMS_V6B["E_consume"]

                # Death if energy depleted
                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    # Recharge surviving agents
                    agent.energy = min(agent.energy + ENERGY_PARAMS_V6B["E_recharge"], 2.0)

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
        "frequency": f_intra,
        "seed": seed,
        "final_population": final_pop,
        "cycles": cycles,
        "runtime_seconds": runtime,
        "db_path": str(db_path)
    }


def run_campaign():
    """
    Execute full experimental campaign (200 experiments).
    """
    print("=" * 80)
    print(f"CYCLE 273: EXTENDED FREQUENCY-VARIANCE MAPPING")
    print(f"Author: {AUTHOR}")
    print(f"Co-Authored-By: {CO_AUTHOR}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nExperimental Design:")
    print(f"  Regime: V6b (Growth, E_net = +{ENERGY_PARAMS_V6B['net_energy']})")
    print(f"  Frequencies: {len(FREQUENCIES)} points (0.01% - 10%)")
    print(f"  Seeds per frequency: {len(SEEDS)}")
    print(f"  Total experiments: {len(FREQUENCIES) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES_PER_EXPERIMENT:,}")

    results = []
    total_experiments = len(FREQUENCIES) * len(SEEDS)
    completed = 0

    for freq in FREQUENCIES:
        freq_results = []

        print(f"\n{'='*80}")
        print(f"Frequency: {freq*100:.2f}% ({len(SEEDS)} experiments)")
        print(f"{'='*80}")

        for seed in SEEDS:
            completed += 1
            print(f"\n[{completed}/{total_experiments}] Running: f={freq*100:.2f}%, seed={seed}")

            try:
                result = run_single_experiment(freq, seed, CYCLES_PER_EXPERIMENT)
                freq_results.append(result)

                print(f"  ✓ Complete: {result['final_population']} agents, "
                      f"{result['runtime_seconds']:.1f}s")

            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                freq_results.append({
                    "frequency": freq,
                    "seed": seed,
                    "final_population": 0,
                    "error": str(e)
                })

        # Calculate variance for this frequency
        populations = [r['final_population'] for r in freq_results if 'error' not in r]

        if populations:
            mean_pop = np.mean(populations)
            std_pop = np.std(populations, ddof=1)
            var_pop = std_pop ** 2

            print(f"\nFrequency {freq*100:.2f}% Summary:")
            print(f"  Mean: {mean_pop:.1f}")
            print(f"  Std Dev: {std_pop:.1f}")
            print(f"  Variance: {var_pop:.1f}")
            print(f"  CV: {std_pop/mean_pop if mean_pop > 0 else 0:.4f}")

        results.extend(freq_results)

    # Save complete results
    results_file = RESULTS_DIR / "c273_extended_variance_mapping_results.json"
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
                "energy_params": ENERGY_PARAMS_V6B
            },
            "results": results
        }, f, indent=2)

    print(f"\n{'='*80}")
    print(f"CAMPAIGN COMPLETE")
    print(f"{'='*80}")
    print(f"Total experiments: {len(results)}")
    print(f"Results saved: {results_file}")
    print(f"\nNext: Run analysis script to fit power law and validate γ ≈ 3.2")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    run_campaign()
