#!/usr/bin/env python3
"""
Minimal NRM Experiment Runner

Runs a single NRM experiment and generates results + visualization.

Usage:
    python run_minimal_experiment.py

Output:
    - data/results_TIMESTAMP.json (experimental data)
    - data/population_dynamics.png (visualization)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import NRMSystem

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available, skipping visualization")


def run_experiment(cycles: int = 1000,
                   population: int = 100,
                   spawn_frequency: float = 0.02,
                   resonance_threshold: float = 0.80,
                   energy_threshold: float = 40.0) -> dict:
    """Run minimal NRM experiment.

    Args:
        cycles: Number of simulation cycles
        population: Initial population size
        spawn_frequency: Spawn probability per cycle
        resonance_threshold: Minimum resonance for composition
        energy_threshold: Minimum energy for composition

    Returns:
        Dictionary containing experiment results
    """
    print("=" * 70)
    print("MINIMAL NRM EXPERIMENT")
    print("=" * 70)
    print(f"\nParameters:")
    print(f"  Population: {population}")
    print(f"  Cycles: {cycles}")
    print(f"  Spawn frequency: {spawn_frequency}")
    print(f"  Resonance threshold: {resonance_threshold}")
    print(f"  Energy threshold: {energy_threshold}")
    print()

    # Initialize system
    print("Initializing NRM system...")
    system = NRMSystem(
        initial_population=population,
        spawn_frequency=spawn_frequency,
        resonance_threshold=resonance_threshold,
        energy_threshold=energy_threshold,
        max_composition_depth=3
    )

    # Run simulation
    print(f"Running simulation ({cycles} cycles)...")
    results = system.run(cycles=cycles)

    # Extract time series
    populations = [r['population'] for r in results]
    energies = [r['mean_energy'] for r in results]
    resonances = [r['mean_resonance'] for r in results]
    comp_events = sum(r['composition_events'] for r in results)
    decomp_events = sum(r['decomposition_events'] for r in results)

    # Compute statistics
    pop_mean = np.mean(populations)
    pop_std = np.std(populations)
    pop_cv = (pop_std / pop_mean * 100) if pop_mean > 0 else 0

    energy_mean = np.mean(energies)
    energy_std = np.std(energies)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nPopulation Dynamics:")
    print(f"  Mean: {pop_mean:.1f} agents")
    print(f"  Std: {pop_std:.1f} agents")
    print(f"  CV: {pop_cv:.1f}%")
    print(f"  Range: [{min(populations)}, {max(populations)}]")
    print(f"\nEnergy Dynamics:")
    print(f"  Mean: {energy_mean:.1f}")
    print(f"  Std: {energy_std:.1f}")
    print(f"\nEmergent Events:")
    print(f"  Composition events: {comp_events}")
    print(f"  Decomposition events: {decomp_events}")
    print(f"  Total transitions: {comp_events + decomp_events}")
    print()

    # Package results
    experiment_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'cycles': cycles,
            'initial_population': population
        },
        'parameters': {
            'spawn_frequency': spawn_frequency,
            'resonance_threshold': resonance_threshold,
            'energy_threshold': energy_threshold
        },
        'statistics': {
            'population_mean': float(pop_mean),
            'population_std': float(pop_std),
            'population_cv': float(pop_cv),
            'energy_mean': float(energy_mean),
            'energy_std': float(energy_std),
            'composition_events': comp_events,
            'decomposition_events': decomp_events
        },
        'time_series': {
            'population': populations,
            'mean_energy': energies,
            'mean_resonance': resonances
        }
    }

    return experiment_data


def save_results(data: dict, output_dir: Path = None) -> Path:
    """Save experiment results to JSON.

    Args:
        data: Experiment data dictionary
        output_dir: Output directory (default: data/)

    Returns:
        Path to saved results file
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data"

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"results_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Results saved: {output_file}")
    return output_file


def visualize_results(data: dict, output_dir: Path = None) -> Path:
    """Create visualization of experiment results.

    Args:
        data: Experiment data dictionary
        output_dir: Output directory (default: data/)

    Returns:
        Path to saved figure
    """
    if not HAS_MATPLOTLIB:
        print("Skipping visualization (matplotlib not available)")
        return None

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract time series
    populations = data['time_series']['population']
    energies = data['time_series']['mean_energy']
    resonances = data['time_series']['mean_resonance']
    cycles = list(range(len(populations)))

    # Create figure
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))

    # Population dynamics
    axes[0].plot(cycles, populations, 'b-', linewidth=1.5)
    axes[0].set_ylabel('Population', fontsize=12)
    axes[0].set_title('NRM System Dynamics', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # Energy dynamics
    axes[1].plot(cycles, energies, 'r-', linewidth=1.5)
    axes[1].set_ylabel('Mean Energy', fontsize=12)
    axes[1].grid(True, alpha=0.3)

    # Resonance dynamics
    axes[2].plot(cycles, resonances, 'g-', linewidth=1.5)
    axes[2].set_ylabel('Mean Resonance', fontsize=12)
    axes[2].set_xlabel('Cycle', fontsize=12)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_file = output_dir / "population_dynamics.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Visualization saved: {output_file}")

    return output_file


def main():
    """Main execution function."""
    # Run experiment
    results = run_experiment(
        cycles=1000,
        population=100,
        spawn_frequency=0.02,
        resonance_threshold=0.80,
        energy_threshold=40.0
    )

    # Save results
    save_results(results)

    # Create visualization
    visualize_results(results)

    print("\n" + "=" * 70)
    print("EXPERIMENT COMPLETE")
    print("=" * 70)
    print("\nOutputs:")
    print("  - data/results_TIMESTAMP.json")
    print("  - data/population_dynamics.png")
    print("\nNext steps:")
    print("  - Examine JSON for detailed metrics")
    print("  - View PNG for visual dynamics")
    print("  - Modify parameters in script for exploration")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
