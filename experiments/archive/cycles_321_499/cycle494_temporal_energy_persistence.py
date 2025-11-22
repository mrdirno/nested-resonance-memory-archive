#!/usr/bin/env python3
"""
Cycle 494: Temporal Persistence of Energy-Dependent Phase Autonomy

Research Question:
Does the energy-dependent phase autonomy evolution observed in Cycle 493
persist or diminish over extended temporal scales?

Hypothesis (from Cycle 493):
Uniform energy configurations show stronger autonomy development than
heterogeneous configurations over 200 cycles. If this effect is fundamental
to NRM dynamics, the autonomy gap should persist or widen over 5× longer
duration.

Experimental Design:
- 2 conditions: Uniform (100.0) vs. High-variance (50/100/150)
- 5 agents per condition (10 total, improved statistical power)
- 1000 cycles per agent (5× longer than Cycle 493)
- Sample phase-reality correlation every 100 cycles (10 measurements)
- Compare autonomy evolution slopes and trajectories

Expected Outcome:
If energy configuration effect is fundamental:
- Uniform: Autonomy slope remains negative (increasing autonomy)
- High-variance: Autonomy slope remains positive or near-zero (stable coupling)
- Gap between conditions persists or widens over time

If energy configuration effect is transient:
- Both conditions converge to similar slopes over extended time
- Gap narrows as initial conditions wash out

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
Cycle: 494
License: GPL-3.0
"""

import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import time

# Add parent to path for module imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fractal.fractal_agent import FractalAgent
from bridge.transcendental_bridge import TranscendentalBridge
import psutil


class TemporalPersistenceExperiment:
    """Test temporal persistence of energy-dependent phase autonomy."""

    def __init__(self, workspace_path: str = "/Volumes/dual/DUALITY-ZERO-V2/workspace"):
        self.workspace = Path(workspace_path)
        self.workspace.mkdir(exist_ok=True)

        # Initialize infrastructure
        self.bridge = TranscendentalBridge(str(self.workspace))

        # Experimental parameters (5× longer than Cycle 493)
        self.cycles = 1000
        self.sample_interval = 100  # Sample every 100 cycles (10 measurements)
        self.num_agents_per_condition = 5  # Increased for better statistics

    def get_reality_metrics(self) -> Dict[str, float]:
        """Get current system reality metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }

    def create_agents_uniform(self) -> List[FractalAgent]:
        """Create agents with uniform initial energy (baseline)."""
        agents = []
        initial_reality = self.get_reality_metrics()

        for i in range(self.num_agents_per_condition):
            agent = FractalAgent(
                agent_id=f"uniform_{i}",
                bridge=self.bridge,
                initial_reality=initial_reality,
                initial_energy=100.0,  # Uniform
                reality=None
            )
            agents.append(agent)

        return agents

    def create_agents_high_variance(self) -> List[FractalAgent]:
        """Create agents with high-variance initial energy."""
        agents = []
        initial_reality = self.get_reality_metrics()

        # 5 agents with distributed energies across variance range
        energies = [50.0, 75.0, 100.0, 125.0, 150.0]

        for i, energy in enumerate(energies):
            agent = FractalAgent(
                agent_id=f"highvar_{i}",
                bridge=self.bridge,
                initial_reality=initial_reality,
                initial_energy=energy,
                reality=None
            )
            agents.append(agent)

        return agents

    def compute_phase_reality_correlation(self, agent: FractalAgent) -> float:
        """
        Compute correlation between phase space and reality metrics.

        This measures phase autonomy: low correlation = high autonomy.
        """
        # Get current reality metrics
        current_reality = self.get_reality_metrics()

        # Get agent's phase state
        phase_state = agent.phase_state

        # Compute phase vector magnitude
        phase_magnitude = np.sqrt(
            phase_state.pi_phase**2 +
            phase_state.e_phase**2 +
            phase_state.phi_phase**2
        )

        # Compute reality vector magnitude
        reality_magnitude = np.sqrt(
            current_reality['cpu_percent']**2 +
            current_reality['memory_percent']**2 +
            current_reality['disk_percent']**2
        )

        # Correlation proxy: normalized distance
        if reality_magnitude > 0:
            correlation_proxy = abs(phase_magnitude - reality_magnitude) / reality_magnitude
        else:
            correlation_proxy = 0.0

        # Normalize to [0, 1] range
        correlation_proxy = min(1.0, correlation_proxy)

        return correlation_proxy

    def evolve_agent(self, agent: FractalAgent, cycles: int,
                     sample_interval: int) -> List[Tuple[int, float]]:
        """
        Evolve agent and sample phase-reality correlation.

        Returns:
            List of (cycle, correlation) tuples
        """
        correlations = []

        for cycle in range(cycles):
            # Evolve agent with reality grounding
            delta_time = 1.0
            agent.evolve(delta_time)

            # Sample correlation at intervals
            if cycle % sample_interval == 0:
                corr = self.compute_phase_reality_correlation(agent)
                correlations.append((cycle, corr))

        return correlations

    def run_condition(self, condition_name: str,
                     agents: List[FractalAgent]) -> Dict:
        """Run experiment for one condition."""
        print(f"  Running {condition_name} condition ({len(agents)} agents)...")

        condition_results = {
            'condition': condition_name,
            'num_agents': len(agents),
            'agents': []
        }

        for i, agent in enumerate(agents):
            print(f"    Evolving {agent.agent_id}...", end='', flush=True)

            # Evolve and measure
            correlations = self.evolve_agent(agent, self.cycles, self.sample_interval)

            # Compute autonomy evolution slope
            cycles = [c for c, _ in correlations]
            corr_values = [c for _, c in correlations]

            # Linear regression for slope
            if len(correlations) > 1:
                slope = np.polyfit(cycles, corr_values, 1)[0]
            else:
                slope = 0.0

            agent_result = {
                'agent_id': agent.agent_id,
                'initial_energy': agent.energy,
                'correlations': correlations,
                'mean_correlation': np.mean(corr_values),
                'std_correlation': np.std(corr_values),
                'autonomy_slope': slope,
                'final_energy': agent.energy
            }

            condition_results['agents'].append(agent_result)
            print(f" slope={slope:.6f}")

        # Condition-level statistics
        slopes = [a['autonomy_slope'] for a in condition_results['agents']]
        condition_results['mean_autonomy_slope'] = np.mean(slopes)
        condition_results['std_autonomy_slope'] = np.std(slopes)
        condition_results['median_autonomy_slope'] = np.median(slopes)

        return condition_results

    def run_experiment(self) -> Dict:
        """Run full experiment across conditions."""
        print("="*70)
        print("TEMPORAL PERSISTENCE OF ENERGY-DEPENDENT PHASE AUTONOMY")
        print("="*70)
        print(f"Cycles: {self.cycles} (5× longer than Cycle 493)")
        print(f"Sample interval: {self.sample_interval}")
        print(f"Agents per condition: {self.num_agents_per_condition}")
        print(f"Total evolution steps: {self.cycles * self.num_agents_per_condition * 2}")
        print()

        start_time = time.time()

        # Create agents for each condition
        print("Creating agents...")
        uniform_agents = self.create_agents_uniform()
        highvar_agents = self.create_agents_high_variance()
        print(f"  Created {len(uniform_agents) + len(highvar_agents)} agents")
        print()

        # Run conditions
        results = {
            'metadata': {
                'experiment': 'Temporal Persistence of Energy-Dependent Phase Autonomy',
                'cycle': 494,
                'date': datetime.now().isoformat(),
                'hypothesis': 'Energy-dependent autonomy evolution persists over extended temporal scales',
                'parameters': {
                    'cycles': self.cycles,
                    'sample_interval': self.sample_interval,
                    'num_agents_per_condition': self.num_agents_per_condition,
                    'comparison_to_cycle_493': '5× longer duration, 2.5× more agents'
                }
            },
            'conditions': []
        }

        # Run each condition
        uniform_results = self.run_condition('uniform', uniform_agents)
        results['conditions'].append(uniform_results)

        highvar_results = self.run_condition('high_variance', highvar_agents)
        results['conditions'].append(highvar_results)

        # Compare conditions
        print()
        print("="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        print(f"{'Condition':<20} {'Mean Slope':<15} {'Median Slope':<15} {'Std':<10}")
        print("-"*70)

        for condition in results['conditions']:
            print(f"{condition['condition']:<20} "
                  f"{condition['mean_autonomy_slope']:>12.6f}   "
                  f"{condition['median_autonomy_slope']:>12.6f}   "
                  f"{condition['std_autonomy_slope']:>10.6f}")

        # Statistical tests
        uniform_slopes = [a['autonomy_slope'] for a in uniform_results['agents']]
        highvar_slopes = [a['autonomy_slope'] for a in highvar_results['agents']]

        # Variance ratio (F-statistic approximation)
        all_slopes = [uniform_slopes, highvar_slopes]
        between_var = np.var([np.mean(s) for s in all_slopes])
        within_var = np.mean([np.var(s) for s in all_slopes])

        if within_var > 0:
            f_ratio = between_var / within_var
        else:
            f_ratio = 0.0

        # Effect size (Cohen's d)
        mean_diff = np.mean(uniform_slopes) - np.mean(highvar_slopes)
        pooled_std = np.sqrt((np.var(uniform_slopes) + np.var(highvar_slopes)) / 2)

        if pooled_std > 0:
            cohens_d = mean_diff / pooled_std
        else:
            cohens_d = 0.0

        results['statistical_test'] = {
            'f_ratio': f_ratio,
            'cohens_d': cohens_d,
            'mean_difference': mean_diff,
            'interpretation': self._interpret_statistics(f_ratio, cohens_d)
        }

        print()
        print("Statistical Tests:")
        print(f"  F-ratio: {f_ratio:.6f}")
        print(f"  Cohen's d: {cohens_d:.6f} ({'large' if abs(cohens_d) > 0.8 else 'medium' if abs(cohens_d) > 0.5 else 'small'} effect)")
        print(f"  Mean difference: {mean_diff:.6f}")
        print()
        print(f"Interpretation: {results['statistical_test']['interpretation']}")

        elapsed = time.time() - start_time
        results['runtime_seconds'] = elapsed

        print()
        print(f"Experiment completed in {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)")
        print("="*70)

        return results

    def _interpret_statistics(self, f_ratio: float, cohens_d: float) -> str:
        """Interpret statistical results."""
        if f_ratio > 2.0 and abs(cohens_d) > 0.8:
            return "Strong evidence: Energy-dependent autonomy effect persists over extended temporal scales (large effect size)"
        elif f_ratio > 2.0 and abs(cohens_d) > 0.5:
            return "Moderate evidence: Energy-dependent effect persists with medium effect size"
        elif f_ratio > 1.5:
            return "Weak evidence: Energy-dependent effect may persist but with small magnitude"
        else:
            return "Insufficient evidence: Energy configuration effects may wash out over time"


def main():
    """Run temporal persistence experiment."""

    # Create experiment
    experiment = TemporalPersistenceExperiment()

    # Run and collect results
    results = experiment.run_experiment()

    # Save results
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "cycle494_temporal_energy_persistence.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Return success
    return 0


if __name__ == "__main__":
    sys.exit(main())
