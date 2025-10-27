#!/usr/bin/env python3
"""
DIAGNOSTIC: Stochasticity Analysis
===================================

Purpose: Investigate why C177 V5 shows complete determinism despite
         seed-controlled initial energy perturbations.

Hypothesis: Reality-grounded energy recharge is deterministic and
           overwhelms initial perturbations within first 100 cycles.

Test: Run minimal experiment with energy tracking to confirm that:
      1. Initial energies differ between seeds
      2. Energy converges to same values by cycle 100
      3. Reality metrics are stable across runs

Date: 2025-10-26
Cycle: 243
Principal Investigator: Aldrin Payopay
"""

import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge
from fractal.fractal_agent import FractalAgent


def run_diagnostic(seed: int, cycles: int = 100) -> Dict:
    """
    Run diagnostic experiment tracking energy evolution.

    Args:
        seed: Random seed
        cycles: Number of cycles to run

    Returns:
        Dictionary with energy history and reality metrics
    """
    np.random.seed(seed)

    # Initialize
    reality = RealityInterface()
    bridge = TranscendentalBridge()

    # Create agent with perturbed initial energy
    metrics = reality.get_system_metrics()
    base_energy = 130.0
    energy_perturbation = np.random.uniform(-5.0, 5.0)
    initial_energy = base_energy + energy_perturbation

    root = FractalAgent(
        agent_id="root",
        bridge=bridge,
        initial_reality=metrics,
        depth=0,
        max_depth=7,
        reality=reality,
        initial_energy=initial_energy
    )

    # Track energy and reality metrics
    energy_history = [root.energy]
    reality_history = [metrics.copy()]

    # Evolution loop
    for _ in range(cycles):
        root.evolve(delta_time=1.0)
        energy_history.append(root.energy)
        reality_history.append(reality.get_system_metrics())

    return {
        'seed': seed,
        'initial_energy': initial_energy,
        'energy_perturbation': energy_perturbation,
        'energy_history': energy_history,
        'reality_history': reality_history,
        'final_energy': root.energy,
        'energy_change': root.energy - initial_energy
    }


def main():
    """Run diagnostic across multiple seeds."""
    print("DIAGNOSTIC: Stochasticity Analysis")
    print("=" * 60)

    seeds = [42, 123, 456]
    cycles = 100

    results = []

    for seed in seeds:
        print(f"\nRunning seed {seed}...")
        result = run_diagnostic(seed, cycles)
        results.append(result)

        print(f"  Initial energy: {result['initial_energy']:.4f}")
        print(f"  Perturbation:   {result['energy_perturbation']:+.4f}")
        print(f"  Final energy:   {result['final_energy']:.4f}")
        print(f"  Change:         {result['energy_change']:+.4f}")

    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    initial_energies = [r['initial_energy'] for r in results]
    final_energies = [r['final_energy'] for r in results]

    print(f"\nInitial energies: {initial_energies}")
    print(f"  Mean:  {np.mean(initial_energies):.4f}")
    print(f"  Std:   {np.std(initial_energies):.4f}")
    print(f"  Range: [{np.min(initial_energies):.4f}, {np.max(initial_energies):.4f}]")

    print(f"\nFinal energies (after {cycles} cycles):")
    print(f"  Values: {final_energies}")
    print(f"  Mean:   {np.mean(final_energies):.4f}")
    print(f"  Std:    {np.std(final_energies):.4f}")
    print(f"  Range:  [{np.min(final_energies):.4f}, {np.max(final_energies):.4f}]")

    # Check if final energies converged (std < 0.1)
    convergence_threshold = 0.1
    converged = np.std(final_energies) < convergence_threshold

    print(f"\nConvergence test (threshold = {convergence_threshold}):")
    print(f"  Converged: {converged}")

    if converged:
        print("\n⚠️  HYPOTHESIS CONFIRMED: Energies converge to same values!")
        print("     Initial perturbations are overwhelmed by reality-based recharge.")
    else:
        print("\n✓  HYPOTHESIS REJECTED: Energies remain distinct.")
        print("     Initial perturbations persist through evolution.")

    # Check reality metrics stability
    print("\n" + "=" * 60)
    print("REALITY METRICS STABILITY")
    print("=" * 60)

    for seed_idx, result in enumerate(results):
        cpu_values = [m['cpu_percent'] for m in result['reality_history']]
        mem_values = [m['memory_percent'] for m in result['reality_history']]

        print(f"\nSeed {result['seed']}:")
        print(f"  CPU:  mean={np.mean(cpu_values):.2f}%, std={np.std(cpu_values):.4f}%")
        print(f"  Mem:  mean={np.mean(mem_values):.2f}%, std={np.std(mem_values):.4f}%")

    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)

    if converged:
        print("""
The stochasticity fix FAILED because:

1. Initial energy perturbations: ±5.0 units (small)
2. Reality-based energy recharge: ~1.8 units/cycle (large, deterministic)
3. After ~3 cycles: Recharge accumulation > Initial perturbation
4. After 100 cycles: Complete convergence to deterministic trajectory

FUNDAMENTAL TENSION:
- Statistical validity requires stochasticity
- Reality grounding enforces determinism (stable system metrics)

SOLUTIONS:
A. Add stochasticity to energy recharge (model measurement noise)
B. Remove reality-based recharge (violates Reality Imperative)
C. Accept determinism, vary reality conditions (not traditional hypothesis testing)
D. Increase perturbation magnitude (arbitrary, doesn't address root cause)

Recommendation: Option A - Add controlled noise to reality metrics
               to represent natural measurement variation while
               maintaining reality anchoring principle.
""")

    # Save results
    output_path = Path(__file__).parent / "results" / "diagnostic_stochasticity_analysis.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump({
            'analysis': 'stochasticity_diagnostic',
            'seeds': seeds,
            'cycles': cycles,
            'results': results,
            'convergence_threshold': convergence_threshold,
            'converged': converged,
            'initial_energy_stats': {
                'mean': float(np.mean(initial_energies)),
                'std': float(np.std(initial_energies)),
                'min': float(np.min(initial_energies)),
                'max': float(np.max(initial_energies))
            },
            'final_energy_stats': {
                'mean': float(np.mean(final_energies)),
                'std': float(np.std(final_energies)),
                'min': float(np.min(final_energies)),
                'max': float(np.max(final_energies))
            }
        }, f, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
