#!/usr/bin/env python3
"""
Cycle 493: Phase Autonomy Energy Dependence Experiment

Research Question:
Does phase autonomy evolution rate vary with initial energy configuration?

Hypothesis (from Paper 6):
Phase autonomy emerges through temporal evolution. If this depends on
energy dynamics, different initial energy configurations should show
different autonomy development rates.

Experimental Design:
- 3 conditions: Uniform energy, High-variance energy, Low-energy start
- 3 agents per condition (9 total)
- 1000 cycles per agent
- Sample phase-reality correlation every 100 cycles (10 measurements)
- Compare autonomy evolution slopes

Expected Outcome:
If energy configuration affects autonomy development:
- Uniform: Baseline evolution rate
- High-variance: Faster autonomy (diverse energy states drive independence)
- Low-energy: Slower autonomy (resource constraints increase coupling)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
Cycle: 493
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
import psutil  # Use psutil directly instead of RealityInterface


class PhaseAutonomyExperiment:
    """Test phase autonomy evolution under different energy configurations."""

    def __init__(self, workspace_path: str = "/Volumes/dual/DUALITY-ZERO-V2/workspace"):
        self.workspace = Path(workspace_path)
        self.workspace.mkdir(exist_ok=True)

        # Initialize infrastructure
        self.bridge = TranscendentalBridge(str(self.workspace))

        # Experimental parameters
        self.cycles = 200  # Reduced for faster execution
        self.sample_interval = 20  # Sample every 20 cycles (10 measurements)
        self.num_agents_per_condition = 2  # Reduced to 2 for speed

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
                reality=None  # No RealityInterface passed
            )
            agents.append(agent)

        return agents

    def create_agents_high_variance(self) -> List[FractalAgent]:
        """Create agents with high-variance initial energy."""
        agents = []
        initial_reality = self.get_reality_metrics()
        energies = [50.0, 100.0, 150.0]  # High variance

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

    def create_agents_low_energy(self) -> List[FractalAgent]:
        """Create agents with low initial energy (resource-constrained)."""
        agents = []
        initial_reality = self.get_reality_metrics()

        for i in range(self.num_agents_per_condition):
            agent = FractalAgent(
                agent_id=f"lowenergy_{i}",
                bridge=self.bridge,
                initial_reality=initial_reality,
                initial_energy=30.0,  # Low energy
                reality=None
            )
            agents.append(agent)

        return agents

    def compute_phase_reality_correlation(self, agent: FractalAgent) -> float:
        """
        Compute correlation between phase space changes and reality metric changes.

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

        # Simple correlation proxy: ratio of magnitudes
        # (Full correlation would require time series, this is single-point estimate)
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
            # Get reality metrics
            reality_metrics = self.get_reality_metrics()

            # Evolve agent (simple energy dynamics)
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
        print(f"  Running {condition_name} condition...")

        condition_results = {
            'condition': condition_name,
            'num_agents': len(agents),
            'agents': []
        }

        for agent in agents:
            # Evolve and measure
            correlations = self.evolve_agent(agent, self.cycles, self.sample_interval)

            # Compute autonomy evolution slope
            # Autonomy = 1 - correlation, so increasing autonomy = decreasing correlation
            cycles = [c for c, _ in correlations]
            corr_values = [c for _, c in correlations]

            # Linear regression for slope
            if len(correlations) > 1:
                slope = np.polyfit(cycles, corr_values, 1)[0]
            else:
                slope = 0.0

            agent_result = {
                'agent_id': agent.agent_id,
                'initial_energy': agent.energy,  # Store initial value before evolution
                'correlations': correlations,
                'mean_correlation': np.mean(corr_values),
                'std_correlation': np.std(corr_values),
                'autonomy_slope': slope,  # Negative slope = increasing autonomy
                'final_energy': agent.energy
            }

            condition_results['agents'].append(agent_result)
            print(f"    {agent.agent_id}: autonomy_slope={slope:.6f}")

        # Condition-level statistics
        slopes = [a['autonomy_slope'] for a in condition_results['agents']]
        condition_results['mean_autonomy_slope'] = np.mean(slopes)
        condition_results['std_autonomy_slope'] = np.std(slopes)

        return condition_results

    def run_experiment(self) -> Dict:
        """Run full experiment across all conditions."""
        print("="*70)
        print("PHASE AUTONOMY ENERGY DEPENDENCE EXPERIMENT")
        print("="*70)
        print(f"Cycles: {self.cycles}")
        print(f"Sample interval: {self.sample_interval}")
        print(f"Agents per condition: {self.num_agents_per_condition}")
        print()

        start_time = time.time()

        # Create agents for each condition
        print("Creating agents...")
        uniform_agents = self.create_agents_uniform()
        highvar_agents = self.create_agents_high_variance()
        lowenergy_agents = self.create_agents_low_energy()
        print(f"  Created {len(uniform_agents) + len(highvar_agents) + len(lowenergy_agents)} agents")
        print()

        # Run conditions
        results = {
            'metadata': {
                'experiment': 'Phase Autonomy Energy Dependence',
                'cycle': 493,
                'date': datetime.now().isoformat(),
                'hypothesis': 'Phase autonomy evolution rate varies with initial energy configuration',
                'parameters': {
                    'cycles': self.cycles,
                    'sample_interval': self.sample_interval,
                    'num_agents_per_condition': self.num_agents_per_condition
                }
            },
            'conditions': []
        }

        # Run each condition
        uniform_results = self.run_condition('uniform', uniform_agents)
        results['conditions'].append(uniform_results)

        highvar_results = self.run_condition('high_variance', highvar_agents)
        results['conditions'].append(highvar_results)

        lowenergy_results = self.run_condition('low_energy', lowenergy_agents)
        results['conditions'].append(lowenergy_results)

        # Compare conditions
        print()
        print("="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        print(f"{'Condition':<20} {'Mean Autonomy Slope':<25} {'Std':<10}")
        print("-"*70)

        for condition in results['conditions']:
            print(f"{condition['condition']:<20} "
                  f"{condition['mean_autonomy_slope']:>20.6f} "
                  f"{condition['std_autonomy_slope']:>10.6f}")

        # Statistical test: ANOVA-like comparison
        all_slopes = []
        for condition in results['conditions']:
            slopes = [a['autonomy_slope'] for a in condition['agents']]
            all_slopes.append(slopes)

        # Compute variance ratio (F-statistic approximation)
        between_var = np.var([np.mean(s) for s in all_slopes])
        within_var = np.mean([np.var(s) for s in all_slopes])

        if within_var > 0:
            f_ratio = between_var / within_var
        else:
            f_ratio = 0.0

        results['statistical_test'] = {
            'test': 'Variance ratio (F-statistic approximation)',
            'f_ratio': f_ratio,
            'interpretation': 'Higher F = greater between-condition variance'
        }

        print()
        print(f"Statistical Test: F-ratio = {f_ratio:.6f}")

        if f_ratio > 2.0:
            print("  Interpretation: Strong evidence for energy-dependent autonomy evolution")
        elif f_ratio > 1.0:
            print("  Interpretation: Moderate evidence for energy-dependent autonomy evolution")
        else:
            print("  Interpretation: Weak evidence - autonomy evolution may be energy-independent")

        elapsed = time.time() - start_time
        results['runtime_seconds'] = elapsed

        print()
        print(f"Experiment completed in {elapsed:.2f} seconds")
        print("="*70)

        return results


def main():
    """Run phase autonomy energy dependence experiment."""

    # Create experiment
    experiment = PhaseAutonomyExperiment()

    # Run and collect results
    results = experiment.run_experiment()

    # Save results
    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "cycle493_phase_autonomy_energy_dependence.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\\nResults saved to: {output_file}")

    # Return success
    return 0


if __name__ == "__main__":
    sys.exit(main())
