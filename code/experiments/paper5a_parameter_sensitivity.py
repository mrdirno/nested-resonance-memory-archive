#!/usr/bin/env python3
"""
Paper 5A: Parameter Sensitivity Analysis - Experimental Framework

Systematic parameter sweeps across NRM configuration space to identify
robustness patterns, critical transitions, and design guidelines.

Research Question:
How sensitive are NRM composition-decomposition dynamics to parameter variations?

Experimental Design:
- Resonance thresholds: 0.70, 0.75, 0.80, 0.85, 0.90 (5 levels)
- Energy thresholds: 30, 35, 40, 45, 50 (5 levels)
- Frequencies: 2.0, 2.5, 3.0, 3.5, 4.0 (5 levels)
- Population sizes: 50, 100, 200, 400 (4 levels)
- Seeds: 10 replications per condition

Novel Contributions:
1. Robustness maps showing stable vs. unstable parameter regions
2. Critical transitions where dynamics change qualitatively
3. Design guidelines for reliable NRM implementations

Target Timeline: 2-3 weeks
Publication Target: IEEE Transactions on Systems, Man, and Cybernetics
Confidence: ⭐⭐⭐⭐⭐ (5/5)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from itertools import product
import sys
from workspace_utils import get_workspace_path, get_results_path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class ParameterSweepConfig:
    """Configuration for Paper 5A parameter sensitivity experiments."""

    def __init__(self):
        """Initialize parameter sweep configuration."""
        # Parameter ranges (start with subset for pilot experiments)
        self.resonance_thresholds = [0.70, 0.75, 0.80, 0.85, 0.90]
        self.energy_thresholds = [30, 35, 40, 45, 50]
        self.frequencies = [2.0, 2.5, 3.0, 3.5, 4.0]
        self.population_sizes = [50, 100, 200, 400]

        # Fixed parameters (from successful C171/C175 baselines)
        self.cycles_per_experiment = 5000
        self.seeds = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

        # Experimental design
        self.sweep_type = "factorial_subset"  # Full factorial would be 5×5×5×4 = 500 conditions
        self.focus_parameters = ["resonance_threshold", "frequency"]  # Start with 2D sweep

    def generate_pilot_conditions(self) -> List[Dict[str, Any]]:
        """Generate pilot experimental conditions (2D sweep).

        Start with resonance_threshold × frequency (5×5 = 25 conditions).
        This validates methodology before full parameter space exploration.

        Returns:
            List of condition dictionaries
        """
        conditions = []

        # 2D sweep: resonance_threshold × frequency
        for res_thresh, freq in product(self.resonance_thresholds, self.frequencies):
            condition = {
                'resonance_threshold': res_thresh,
                'energy_threshold': 40,  # Fixed at baseline value
                'frequency': freq,
                'population_size': 100,  # Fixed at baseline value
                'cycles': self.cycles_per_experiment,
                'condition_name': f"RT{res_thresh:.2f}_F{freq:.1f}"
            }
            conditions.append(condition)

        return conditions

    def generate_full_factorial(self) -> List[Dict[str, Any]]:
        """Generate full factorial experimental conditions.

        Full 4D sweep: 5×5×5×4 = 500 conditions.
        Use this after pilot validates methodology.

        Returns:
            List of condition dictionaries
        """
        conditions = []

        for res_thresh, energy_thresh, freq, pop_size in product(
            self.resonance_thresholds,
            self.energy_thresholds,
            self.frequencies,
            self.population_sizes
        ):
            condition = {
                'resonance_threshold': res_thresh,
                'energy_threshold': energy_thresh,
                'frequency': freq,
                'population_size': pop_size,
                'cycles': self.cycles_per_experiment,
                'condition_name': f"RT{res_thresh:.2f}_ET{energy_thresh}_F{freq:.1f}_P{pop_size}"
            }
            conditions.append(condition)

        return conditions

    def estimate_runtime(self, conditions: List[Dict], seeds: List[int]) -> Dict[str, float]:
        """Estimate total experiment runtime.

        Based on C171/C175 baselines:
        - 5000 cycles, single run: ~3-4 minutes (optimized)
        - Per-condition (10 seeds): ~30-40 minutes

        Args:
            conditions: List of experimental conditions
            seeds: List of random seeds

        Returns:
            Dictionary with runtime estimates
        """
        minutes_per_run = 3.5  # Conservative estimate (post-optimization)
        total_runs = len(conditions) * len(seeds)
        total_minutes = total_runs * minutes_per_run

        return {
            'total_conditions': len(conditions),
            'seeds_per_condition': len(seeds),
            'total_runs': total_runs,
            'minutes_per_run': minutes_per_run,
            'total_minutes': total_minutes,
            'total_hours': total_minutes / 60,
            'total_days': total_minutes / (60 * 24)
        }


class ParameterSensitivityAnalyzer:
    """Analyze parameter sensitivity results."""

    def __init__(self, results_dir: Path):
        """Initialize analyzer.

        Args:
            results_dir: Directory containing experimental results
        """
        self.results_dir = Path(results_dir)

    def load_results(self, experiment_file: str) -> Dict:
        """Load experimental results from JSON.

        Args:
            experiment_file: Name of results JSON file

        Returns:
            Dictionary containing experimental data
        """
        filepath = self.results_dir / experiment_file
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return {}

        with open(filepath, 'r') as f:
            return json.load(f)

    def compute_robustness_metrics(self, data: Dict) -> Dict[str, float]:
        """Compute robustness metrics for a condition.

        Metrics:
        - Population stability (mean, std, CV)
        - Composition event consistency
        - Basin persistence
        - System viability (survival rate)

        Args:
            data: Experimental results dictionary

        Returns:
            Dictionary of robustness metrics
        """
        if not data or 'experiments' not in data:
            return {}

        experiments = data['experiments']

        # Population metrics
        final_populations = [exp.get('final_agent_count', 0) for exp in experiments]
        mean_populations = [exp.get('mean_population', 0) for exp in experiments]
        composition_events = [exp.get('avg_composition_events', 0) for exp in experiments]

        # Viability: fraction of runs that maintain population > 0
        viable_runs = sum(1 for pop in final_populations if pop > 0)
        viability_rate = viable_runs / len(experiments) if experiments else 0

        # Stability: coefficient of variation in mean population
        mean_pop_avg = np.mean(mean_populations) if mean_populations else 0
        mean_pop_std = np.std(mean_populations) if mean_populations else 0
        cv = (mean_pop_std / mean_pop_avg * 100) if mean_pop_avg > 0 else float('inf')

        # Activity: consistency in composition events
        comp_event_mean = np.mean(composition_events) if composition_events else 0
        comp_event_std = np.std(composition_events) if composition_events else 0

        return {
            'viability_rate': viability_rate,
            'mean_population': mean_pop_avg,
            'population_std': mean_pop_std,
            'population_cv': cv,
            'composition_events_mean': comp_event_mean,
            'composition_events_std': comp_event_std,
            'n_experiments': len(experiments)
        }

    def generate_robustness_map(self, results: Dict[str, Dict]) -> np.ndarray:
        """Generate 2D robustness heatmap.

        For pilot 2D sweep (resonance_threshold × frequency),
        create heatmap showing viability rates across parameter space.

        Args:
            results: Dictionary mapping condition names to results

        Returns:
            2D numpy array for heatmap visualization
        """
        # Extract parameter dimensions from condition names
        conditions = list(results.keys())

        # Parse resonance thresholds and frequencies
        res_thresholds = sorted(set(
            float(cond.split('_')[0].replace('RT', ''))
            for cond in conditions if 'RT' in cond
        ))
        frequencies = sorted(set(
            float(cond.split('_')[1].replace('F', ''))
            for cond in conditions if '_F' in cond
        ))

        # Create 2D grid
        heatmap = np.zeros((len(res_thresholds), len(frequencies)))

        for cond_name, cond_results in results.items():
            metrics = self.compute_robustness_metrics(cond_results)

            # Find indices
            try:
                rt = float(cond_name.split('_')[0].replace('RT', ''))
                freq = float(cond_name.split('_')[1].replace('F', ''))

                i = res_thresholds.index(rt)
                j = frequencies.index(freq)

                heatmap[i, j] = metrics.get('viability_rate', 0)
            except (ValueError, IndexError):
                continue

        return heatmap

    def identify_critical_transitions(self, heatmap: np.ndarray,
                                     threshold: float = 0.5) -> List[Tuple[int, int]]:
        """Identify parameter combinations at critical transition boundaries.

        Critical transitions occur where viability rate crosses threshold,
        indicating qualitative change in system dynamics.

        Args:
            heatmap: 2D robustness map
            threshold: Viability threshold for critical transition (default: 0.5)

        Returns:
            List of (i, j) indices at transition boundaries
        """
        transitions = []

        rows, cols = heatmap.shape

        # Find horizontal transitions (resonance threshold changes)
        for i in range(rows - 1):
            for j in range(cols):
                if (heatmap[i, j] < threshold <= heatmap[i+1, j]) or \
                   (heatmap[i, j] >= threshold > heatmap[i+1, j]):
                    transitions.append((i, j))

        # Find vertical transitions (frequency changes)
        for i in range(rows):
            for j in range(cols - 1):
                if (heatmap[i, j] < threshold <= heatmap[i, j+1]) or \
                   (heatmap[i, j] >= threshold > heatmap[i, j+1]):
                    transitions.append((i, j))

        return list(set(transitions))  # Remove duplicates


def generate_paper5a_experimental_plan():
    """Generate experimental plan for Paper 5A."""
    print("="*70)
    print("PAPER 5A: PARAMETER SENSITIVITY ANALYSIS - EXPERIMENTAL PLAN")
    print("="*70)

    config = ParameterSweepConfig()

    # Generate pilot conditions (2D sweep)
    print("\n1. PILOT EXPERIMENTAL CONDITIONS (2D Sweep)")
    print("-" * 70)
    pilot_conditions = config.generate_pilot_conditions()
    print(f"Total conditions: {len(pilot_conditions)}")
    print(f"Parameter ranges:")
    print(f"  - Resonance thresholds: {config.resonance_thresholds}")
    print(f"  - Frequencies: {config.frequencies}")
    print(f"  - Fixed: energy_threshold=40, population_size=100")
    print(f"  - Seeds per condition: {len(config.seeds)}")

    # Estimate pilot runtime
    pilot_runtime = config.estimate_runtime(pilot_conditions, config.seeds)
    print(f"\nPilot runtime estimate:")
    print(f"  - Total runs: {pilot_runtime['total_runs']}")
    print(f"  - Total time: {pilot_runtime['total_hours']:.1f} hours ({pilot_runtime['total_days']:.2f} days)")

    # Generate full factorial (for reference)
    print("\n2. FULL FACTORIAL CONDITIONS (4D Sweep)")
    print("-" * 70)
    full_conditions = config.generate_full_factorial()
    print(f"Total conditions: {len(full_conditions)}")
    print(f"Parameter ranges:")
    print(f"  - Resonance thresholds: {config.resonance_thresholds}")
    print(f"  - Energy thresholds: {config.energy_thresholds}")
    print(f"  - Frequencies: {config.frequencies}")
    print(f"  - Population sizes: {config.population_sizes}")

    # Estimate full runtime
    full_runtime = config.estimate_runtime(full_conditions, config.seeds)
    print(f"\nFull factorial runtime estimate:")
    print(f"  - Total runs: {full_runtime['total_runs']}")
    print(f"  - Total time: {full_runtime['total_hours']:.1f} hours ({full_runtime['total_days']:.2f} days)")

    # Execution recommendation
    print("\n3. EXECUTION RECOMMENDATION")
    print("-" * 70)
    print("Phase 1: Pilot (2D sweep)")
    print(f"  - {len(pilot_conditions)} conditions × {len(config.seeds)} seeds = {len(pilot_conditions) * len(config.seeds)} runs")
    print(f"  - Runtime: ~{pilot_runtime['total_hours']:.1f} hours")
    print("  - Validates methodology, identifies promising parameter regions")
    print("")
    print("Phase 2: Focused expansion (3D sweep)")
    print("  - Add energy_threshold dimension to promising regions from pilot")
    print("  - Estimated: 50-100 additional conditions")
    print("  - Runtime: ~20-40 hours")
    print("")
    print("Phase 3: Full factorial (if needed)")
    print(f"  - All {len(full_conditions)} conditions for complete robustness map")
    print(f"  - Runtime: ~{full_runtime['total_days']:.1f} days")
    print("  - Only execute if critical transitions require complete characterization")

    print("\n4. OUTPUT ARTIFACTS")
    print("-" * 70)
    print("- Robustness heatmaps (2D, 3D visualizations)")
    print("- Critical transition boundaries (parameter thresholds)")
    print("- Design guidelines (recommended parameter ranges)")
    print("- Statistical analysis (ANOVA, effect sizes)")
    print("- Manuscript with 5-8 publication figures")

    print("\n" + "="*70)
    print("Plan generated. Ready for execution after Papers 3-4 complete.")
    print("="*70)

    return config, pilot_conditions, full_conditions


def main():
    """Main execution function."""
    config, pilot_conditions, full_conditions = generate_paper5a_experimental_plan()

    # Save experimental plan to JSON
    output_dir = get_results_path()
    output_file = output_dir / "paper5a_experimental_plan.json"

    plan = {
        'metadata': {
            'paper': 'Paper 5A - Parameter Sensitivity Analysis',
            'date_created': datetime.now().isoformat(),
            'confidence': '⭐⭐⭐⭐⭐',
            'timeline': '2-3 weeks',
            'publication_target': 'IEEE Transactions on Systems, Man, and Cybernetics'
        },
        'pilot_conditions': pilot_conditions,
        'full_factorial_conditions': full_conditions,
        'parameter_ranges': {
            'resonance_thresholds': config.resonance_thresholds,
            'energy_thresholds': config.energy_thresholds,
            'frequencies': config.frequencies,
            'population_sizes': config.population_sizes
        },
        'fixed_parameters': {
            'cycles_per_experiment': config.cycles_per_experiment,
            'seeds': config.seeds
        },
        'runtime_estimates': {
            'pilot': config.estimate_runtime(pilot_conditions, config.seeds),
            'full_factorial': config.estimate_runtime(full_conditions, config.seeds)
        }
    }

    with open(output_file, 'w') as f:
        json.dump(plan, f, indent=2)

    print(f"\nExperimental plan saved to: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
