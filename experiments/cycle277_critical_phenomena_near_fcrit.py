#!/usr/bin/env python3
"""
Cycle 277: Critical Phenomena Near f_crit
==========================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-19 (Cycle 1477)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Objective:
----------
Test predicted critical phenomena as spawn frequency approaches critical threshold
f_crit ≈ 0.0066% (hierarchical critical frequency from C186).

Background:
-----------
Cycle 1472 theoretical derivation predicts divergent behavior near f_crit:

1. Energy divergence: E_min ~ (f - f_crit)^-ν_E
2. Variance divergence: σ² ~ (f - f_crit)^-ν_σ
3. Relaxation time divergence: τ ~ (f - f_crit)^-ν_τ

These are signatures of critical phenomena connecting to statistical physics
universality classes.

Hypothesis:
-----------
Near-critical behavior exhibits power law divergences with measurable critical
exponents ν_E, ν_σ, ν_τ as f approaches f_crit from above.

Experimental Design:
--------------------
**Critical Frequency:** f_crit^hier ≈ 0.0066% (from C186 α = 607 analysis)

**Test Frequencies (5 points near threshold):**
- 0.01% (~1.5× f_crit): Near-critical, high instability expected
- 0.015% (~2.3× f_crit): Transition region
- 0.02% (~3.0× f_crit): Moderate distance from threshold
- 0.03% (~4.5× f_crit): Further from threshold
- 0.05% (~7.6× f_crit): Well above threshold (reference)

**Rationale:** Logarithmic spacing around f_crit to capture divergence behavior
across ~5× range (1.5× to 7.6× f_crit).

**Energy Configuration:**
- E_consume = 0.5, E_recharge = 1.0 (V6b growth regime, E_net = +0.5)
- Ensures viability (E_net > 0) while testing frequency effects

**Replication:**
- Seeds: 400-429 (n = 30 per frequency)
- Higher replication for near-threshold stochasticity
- Total experiments: 5 frequencies × 30 seeds = **150 experiments**

**Runtime:**
- Cycles: 450,000 per experiment (~3-5 minutes)
- Total time: ~10 hours sequential

**Measurements:**
- Final population N_final (for E_min estimation)
- Population variance σ² across seeds
- Relaxation time τ (time to equilibrium)

**Hierarchical Configuration:**
- n_pop = 10 (populations)
- f_migrate = 0.5% (inter-population migration)
- Mode = "HIERARCHICAL"

Expected Outcomes:
------------------
**If critical phenomena present:**
- E_min increases as f → f_crit (divergence)
- σ² increases as f → f_crit (critical fluctuations)
- τ increases as f → f_crit (critical slowing down)
- Log-log plots show power law relationships

**Critical exponents (predicted):**
- ν_E ≈ β ≈ 2.19 (energy divergence)
- ν_σ ≈ γ ≈ 3.2 (variance divergence)
- ν_τ ≈ 1-2 (relaxation time divergence, theoretical estimate)

Success Criteria:
-----------------
- Clear increase in E_min, σ², τ as f approaches f_crit
- Power law fits: R² > 0.80 (challenging near threshold)
- Critical exponents measurable (order of magnitude agreement)
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
CYCLE_ID = "C277"
CYCLE_NAME = "Critical Phenomena Near f_crit"
AUTHOR = "Aldrin Payopay <aldrin.gdf@gmail.com>"
CO_AUTHOR = "Claude Sonnet 4.5 <noreply@anthropic.com>"

# Output directories
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Critical frequency (from C186)
F_CRIT_HIER = 0.000066  # 0.0066% hierarchical critical frequency

# Test frequencies (near f_crit)
FREQUENCIES = [0.0001, 0.00015, 0.0002, 0.0003, 0.0005]  # 0.01% - 0.05%

# Replication
SEEDS = list(range(400, 430))  # Seeds 400-429 (n=30)
CYCLES_PER_EXPERIMENT = 450_000
N_POPULATIONS = 10
F_MIGRATE = 0.005  # 0.5%
MODE = "HIERARCHICAL"

# V6b Growth Regime parameters
ENERGY_PARAMS = {
    "E_consume": 0.5,
    "E_recharge": 1.0,
    "net_energy": +0.5
}

# Equilibration detection parameters
EQUILIBRATION_WINDOW = 10000  # Check equilibration every 10k cycles
EQUILIBRATION_THRESHOLD = 0.05  # 5% stability criterion

# ============================================================================
# EXPERIMENT EXECUTION
# ============================================================================

def detect_equilibration(population_history: List[int], window: int = 10) -> int:
    """
    Detect equilibration time (when population stabilizes).

    Args:
        population_history: List of population values over time
        window: Number of recent measurements for stability check

    Returns:
        Equilibration time (cycle number), or -1 if not equilibrated
    """
    if len(population_history) < window:
        return -1

    recent = population_history[-window:]
    mean_pop = np.mean(recent)

    if mean_pop == 0:  # Collapsed
        return -1

    cv = np.std(recent) / mean_pop if mean_pop > 0 else 1.0

    if cv < EQUILIBRATION_THRESHOLD:
        # Find first time stability was reached
        for i in range(len(population_history) - window):
            segment = population_history[i:i+window]
            seg_mean = np.mean(segment)
            seg_cv = np.std(segment) / seg_mean if seg_mean > 0 else 1.0
            if seg_cv < EQUILIBRATION_THRESHOLD:
                return i * EQUILIBRATION_WINDOW

    return -1


def run_single_experiment(
    f_intra: float,
    seed: int,
    cycles: int = CYCLES_PER_EXPERIMENT
) -> Dict:
    """
    Run single experiment at specified frequency and seed.

    Measures relaxation time in addition to final population.
    """
    # Format frequency for filename
    freq_pct = f"{f_intra * 100:.3f}".replace('.', '_')

    # Create database path
    db_path = RESULTS_DIR / f"c277_CRITICAL_{freq_pct}pct_seed{seed}.db"

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

    # Run simulation with equilibration tracking
    start_time = time.time()
    population_history = []
    equilibration_time = -1

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

        # Death phase
        for pop_id in range(N_POPULATIONS):
            agents = reality.get_population_agents(pop_id)
            for agent in agents:
                agent.energy -= ENERGY_PARAMS["E_consume"]

                if agent.energy <= 0:
                    reality.remove_agent(agent.agent_id, pop_id)
                else:
                    agent.energy = min(agent.energy + ENERGY_PARAMS["E_recharge"], 2.0)

        # Record metrics and check equilibration
        if cycle % EQUILIBRATION_WINDOW == 0:
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

            population_history.append(total_pop)

            # Check equilibration
            if equilibration_time == -1:
                equilibration_time = detect_equilibration(population_history)

    # Get final population
    final_pop = sum(len(reality.get_population_agents(p)) for p in range(N_POPULATIONS))
    runtime = time.time() - start_time

    # Close database
    reality.close()

    return {
        "frequency": f_intra,
        "f_over_fcrit": f_intra / F_CRIT_HIER,
        "seed": seed,
        "final_population": final_pop,
        "equilibration_time": equilibration_time,
        "cycles": cycles,
        "runtime_seconds": runtime,
        "db_path": str(db_path)
    }


def run_campaign():
    """
    Execute full experimental campaign (150 experiments).
    """
    print("=" * 80)
    print(f"CYCLE 277: CRITICAL PHENOMENA NEAR f_crit")
    print(f"Author: {AUTHOR}")
    print(f"Co-Authored-By: {CO_AUTHOR}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nExperimental Design:")
    print(f"  f_crit (hierarchical): {F_CRIT_HIER*100:.4f}%")
    print(f"  Test frequencies: {len(FREQUENCIES)} points near f_crit")
    print(f"  Seeds per frequency: {len(SEEDS)}")
    print(f"  Total experiments: {len(FREQUENCIES) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES_PER_EXPERIMENT:,}")

    results = []
    total_experiments = len(FREQUENCIES) * len(SEEDS)
    completed = 0

    for freq in FREQUENCIES:
        freq_results = []

        print(f"\n{'='*80}")
        print(f"Frequency: {freq*100:.3f}% ({freq/F_CRIT_HIER:.1f}× f_crit, {len(SEEDS)} experiments)")
        print(f"{'='*80}")

        for seed in SEEDS:
            completed += 1
            print(f"\n[{completed}/{total_experiments}] Running: f={freq*100:.3f}%, seed={seed}")

            try:
                result = run_single_experiment(freq, seed, CYCLES_PER_EXPERIMENT)
                freq_results.append(result)

                tau_str = f"{result['equilibration_time']:,}" if result['equilibration_time'] > 0 else "not equilibrated"
                print(f"  ✓ Complete: {result['final_population']} agents, "
                      f"τ={tau_str}, {result['runtime_seconds']:.1f}s")

            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                freq_results.append({
                    "frequency": freq,
                    "seed": seed,
                    "final_population": 0,
                    "equilibration_time": -1,
                    "error": str(e)
                })

        # Calculate summary statistics
        populations = [r['final_population'] for r in freq_results if 'error' not in r]
        tau_values = [r['equilibration_time'] for r in freq_results
                     if 'error' not in r and r['equilibration_time'] > 0]

        if populations:
            mean_pop = np.mean(populations)
            std_pop = np.std(populations, ddof=1)
            var_pop = std_pop ** 2

            print(f"\nFrequency {freq*100:.3f}% Summary:")
            print(f"  Mean population: {mean_pop:.1f}")
            print(f"  Variance: {var_pop:.1f}")
            print(f"  Mean τ: {np.mean(tau_values) if tau_values else 'N/A'}")
            print(f"  Distance from f_crit: {freq/F_CRIT_HIER:.1f}×")

        results.extend(freq_results)

    # Save complete results
    results_file = RESULTS_DIR / "c277_critical_phenomena_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "cycle_name": CYCLE_NAME,
            "date": datetime.now().isoformat(),
            "author": AUTHOR,
            "co_author": CO_AUTHOR,
            "config": {
                "f_crit_hier": F_CRIT_HIER,
                "frequencies": FREQUENCIES,
                "seeds": SEEDS,
                "cycles_per_experiment": CYCLES_PER_EXPERIMENT,
                "n_populations": N_POPULATIONS,
                "f_migrate": F_MIGRATE,
                "energy_params": ENERGY_PARAMS
            },
            "results": results
        }, f, indent=2)

    print(f"\n{'='*80}")
    print(f"CAMPAIGN COMPLETE")
    print(f"{'='*80}")
    print(f"Total experiments: {len(results)}")
    print(f"Results saved: {results_file}")
    print(f"\nNext: Run analysis to measure critical exponents")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    run_campaign()
