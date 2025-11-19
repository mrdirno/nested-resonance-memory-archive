#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Stochasticity Validation Test
===============================================

Quick test to confirm seed-controlled perturbations produce variance in results.

Post-Fix Validation (Cycle 235):
- Tests FractalAgent initial_energy parameter
- Runs 3 seeds (42, 123, 456) for 100 cycles each
- Uses controlled perturbations: E0 ~ U(125, 135)
- Success criterion: Seeds produce DIFFERENT results (variance > 0)

Author: Claude (DUALITY-ZERO-V2)
Principal Investigator: Aldrin Payopay
Date: 2025-10-26 (Cycle 235)
"""

import sys
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent


def run_validation_experiment(
    seed: int,
    cycles: int = 100,
    spawn_interval: int = 10
) -> Dict[str, Any]:
    """
    Run single validation experiment with seed-controlled perturbation.

    Args:
        seed: Random seed for reproducibility
        cycles: Number of simulation cycles (default: 100 for quick test)
        spawn_interval: Cycles between spawn attempts

    Returns:
        Dictionary with results (mean population, spawn count, etc.)
    """
    np.random.seed(seed)

    # Initialize reality interface
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Get initial reality metrics
    initial_metrics = reality.get_system_metrics()

    # CRITICAL: Seed-controlled energy perturbation
    # E0 ~ U(125, 135) represents ±3.8% variation from nominal 130
    base_energy = 130.0
    energy_perturbation = np.random.uniform(-5.0, 5.0)
    initial_energy = base_energy + energy_perturbation

    print(f"[Seed {seed}] Initial energy: {initial_energy:.2f} (perturbation: {energy_perturbation:+.2f})")

    # Create root agent with seed-controlled initial energy
    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=initial_metrics,
        depth=0,
        max_depth=7,
        reality=reality,
        initial_energy=initial_energy  # NEW: Overrides reality-based calculation
    )

    # Population tracking
    agents = [root]
    population_history = []
    spawn_count = 0

    # Run simulation
    for cycle_idx in range(cycles):
        # Track population
        population_history.append(len(agents))

        # Spawn interval
        if cycle_idx % spawn_interval == 0 and cycle_idx > 0:
            # Try to spawn from all fertile agents
            new_agents = []
            for agent in agents:
                if agent.energy >= 10.0 and agent.is_active:
                    child_id = f"agent_{spawn_count}"
                    child = agent.spawn_child(child_id)
                    if child is not None:
                        new_agents.append(child)
                        spawn_count += 1

            agents.extend(new_agents)

        # Evolve all agents
        for agent in agents:
            if agent.is_active:
                agent.evolve(delta_time=1.0)

        # Remove extinct agents
        agents = [a for a in agents if a.is_active and a.energy > 0]

    # Calculate statistics
    mean_population = np.mean(population_history)
    std_population = np.std(population_history)
    final_population = len(agents)

    return {
        "seed": seed,
        "initial_energy": initial_energy,
        "energy_perturbation": energy_perturbation,
        "mean_population": mean_population,
        "std_population": std_population,
        "final_population": final_population,
        "spawn_count": spawn_count,
        "cycles": cycles
    }


def main():
    """Run validation test with 3 seeds."""
    print("=" * 70)
    print("DUALITY-ZERO-V2: Stochasticity Validation Test")
    print("=" * 70)
    print("\nObjective: Confirm seed-controlled perturbations produce variance")
    print("Baseline Issue: All seeds produced identical results (complete determinism)")
    print("Fix: FractalAgent now accepts initial_energy parameter")
    print("Test: Run 3 seeds with E0 ~ U(125, 135), check if variance > 0")
    print("=" * 70)

    # Test parameters
    seeds = [42, 123, 456]
    cycles = 100
    spawn_interval = 10

    print(f"\nParameters:")
    print(f"  Seeds: {seeds}")
    print(f"  Cycles: {cycles}")
    print(f"  Spawn interval: {spawn_interval}")
    print(f"  Energy distribution: E0 ~ U(125, 135)")
    print("\n" + "=" * 70)

    # Run experiments
    results = []
    for seed in seeds:
        print(f"\nRunning seed {seed}...")
        start_time = time.time()

        result = run_validation_experiment(seed, cycles, spawn_interval)
        results.append(result)

        elapsed = time.time() - start_time
        print(f"[Seed {seed}] Completed in {elapsed:.2f}s")
        print(f"  Mean population: {result['mean_population']:.4f}")
        print(f"  Final population: {result['final_population']}")
        print(f"  Spawn count: {result['spawn_count']}")

    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    # Extract mean populations
    mean_pops = [r['mean_population'] for r in results]
    initial_energies = [r['initial_energy'] for r in results]
    spawn_counts = [r['spawn_count'] for r in results]

    print(f"\nInitial Energies (E0 ~ U(125, 135)):")
    for seed, E0 in zip(seeds, initial_energies):
        print(f"  Seed {seed:>3}: {E0:.4f}")

    print(f"\nMean Populations:")
    for seed, pop in zip(seeds, mean_pops):
        print(f"  Seed {seed:>3}: {pop:.4f}")

    print(f"\nSpawn Counts:")
    for seed, spawns in zip(seeds, spawn_counts):
        print(f"  Seed {seed:>3}: {spawns}")

    # Statistical analysis
    variance_pop = np.var(mean_pops)
    std_pop = np.std(mean_pops)
    mean_pop = np.mean(mean_pops)
    cv_pop = (std_pop / mean_pop * 100) if mean_pop > 0 else 0

    variance_energy = np.var(initial_energies)
    std_energy = np.std(initial_energies)

    print("\n" + "=" * 70)
    print("STATISTICAL SUMMARY")
    print("=" * 70)

    print(f"\nInitial Energy:")
    print(f"  Variance: {variance_energy:.6f}")
    print(f"  Std Dev: {std_energy:.4f}")

    print(f"\nMean Population:")
    print(f"  Variance: {variance_pop:.6f}")
    print(f"  Std Dev: {std_pop:.4f}")
    print(f"  Mean: {mean_pop:.4f}")
    print(f"  CV: {cv_pop:.2f}%")

    print("\n" + "=" * 70)
    print("OUTCOME")
    print("=" * 70)

    # Success criterion: Variance > 0
    if variance_pop > 0:
        print("\n✅ VALIDATION SUCCESSFUL")
        print(f"   - Initial energies vary (σ² = {variance_energy:.4f})")
        print(f"   - Mean populations vary (σ² = {variance_pop:.4f})")
        print("   - Seeds produce DIFFERENT results")
        print("   - Stochasticity fix WORKING")
        success = True
    else:
        print("\n❌ VALIDATION FAILED")
        print("   - Initial energies vary but populations identical")
        print("   - Determinism still present in evolution dynamics")
        print("   - Further investigation required")
        success = False

    print("\n" + "=" * 70)

    # Save results
    results_path = Path(__file__).parent / "results" / "stochasticity_validation.txt"
    results_path.parent.mkdir(exist_ok=True)

    with open(results_path, 'w') as f:
        f.write("DUALITY-ZERO-V2: Stochasticity Validation Results\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Cycles: {cycles}\n")
        f.write(f"Seeds: {seeds}\n\n")

        f.write("Initial Energies:\n")
        for seed, E0 in zip(seeds, initial_energies):
            f.write(f"  Seed {seed}: {E0:.6f}\n")

        f.write("\nMean Populations:\n")
        for seed, pop in zip(seeds, mean_pops):
            f.write(f"  Seed {seed}: {pop:.6f}\n")

        f.write(f"\nVariance (Initial Energy): {variance_energy:.6f}\n")
        f.write(f"Variance (Mean Population): {variance_pop:.6f}\n")
        f.write(f"Std Dev (Mean Population): {std_pop:.6f}\n")
        f.write(f"Coefficient of Variation: {cv_pop:.2f}%\n")

        f.write(f"\nOutcome: {'SUCCESS' if success else 'FAILED'}\n")

    print(f"\nResults saved to: {results_path}")
    print("=" * 70)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
