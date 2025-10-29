#!/usr/bin/env python3
"""
Cycle 495: Mapping Decay Dynamics of Energy-Dependent Phase Autonomy

Research Question:
At what timescale does energy-dependent phase autonomy transition from
significant (Cycle 493: F=2.39 at 200 cycles) to negligible (Cycle 494: F=0.12 at 1000 cycles)?

Hypothesis:
Energy configuration effects decay exponentially with characteristic timescale τ.
F-ratio should cross 1.0 (significance threshold) at critical transition point
between 200-1000 cycles. Expected: τ ≈ 300-400 cycles.

Experimental Design:
- 2 conditions: Uniform (100.0) vs. High-variance (50/75/100/125/150)
- 3 agents per condition (6 total, for speed)
- 4 timescales: 400, 600, 800, 1000 cycles (interpolate C493-C494 gap)
- Sample every N/10 cycles (10 measurements per agent)
- Compare F-ratios across timescales

Expected Outcome:
- F-ratio decay: F(t) = F₀ × exp(-t/τ) + F_∞
- Critical transition: F(t_c) = 1.0 → estimate τ
- Map full decay curve from 200 to 1000 cycles

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
Cycle: 495
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


class DecayDynamicsExperiment:
    """Map temporal decay dynamics of energy-dependent phase autonomy."""

    def __init__(self, workspace_path: str = "/Volumes/dual/DUALITY-ZERO-V2/workspace"):
        self.workspace = Path(workspace_path)
        self.workspace.mkdir(exist_ok=True)

        # Initialize infrastructure
        self.bridge = TranscendentalBridge(str(self.workspace))

        # Experimental parameters
        self.num_agents_per_condition = 3  # Reduced for speed across 4 timescales
        self.timescales = [400, 600, 800, 1000]  # Interpolate C493-C494 gap

    def get_reality_metrics(self) -> Dict[str, float]:
        """Get current system reality metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }

    def create_agents_uniform(self) -> List[FractalAgent]:
        """Create agents with uniform initial energy."""
        agents = []
        initial_reality = self.get_reality_metrics()

        for i in range(self.num_agents_per_condition):
            agent = FractalAgent(
                agent_id=f"uniform_{i}",
                bridge=self.bridge,
                initial_reality=initial_reality,
                initial_energy=100.0,
                reality=None
            )
            agents.append(agent)

        return agents

    def create_agents_high_variance(self) -> List[FractalAgent]:
        """Create agents with high-variance initial energy."""
        agents = []
        initial_reality = self.get_reality_metrics()
        energies = [50.0, 100.0, 150.0]  # 3 agents spanning variance range

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
        """Compute correlation between phase space and reality metrics."""
        current_reality = self.get_reality_metrics()
        phase_state = agent.phase_state

        phase_magnitude = np.sqrt(
            phase_state.pi_phase**2 +
            phase_state.e_phase**2 +
            phase_state.phi_phase**2
        )

        reality_magnitude = np.sqrt(
            current_reality['cpu_percent']**2 +
            current_reality['memory_percent']**2 +
            current_reality['disk_percent']**2
        )

        if reality_magnitude > 0:
            correlation_proxy = abs(phase_magnitude - reality_magnitude) / reality_magnitude
        else:
            correlation_proxy = 0.0

        return min(1.0, correlation_proxy)

    def evolve_agent(self, agent: FractalAgent, cycles: int,
                     sample_interval: int) -> List[Tuple[int, float]]:
        """Evolve agent and sample phase-reality correlation."""
        correlations = []

        for cycle in range(cycles):
            delta_time = 1.0
            agent.evolve(delta_time)

            if cycle % sample_interval == 0:
                corr = self.compute_phase_reality_correlation(agent)
                correlations.append((cycle, corr))

        return correlations

    def run_condition(self, condition_name: str, agents: List[FractalAgent],
                     cycles: int, sample_interval: int) -> Dict:
        """Run experiment for one condition at one timescale."""
        condition_results = {
            'condition': condition_name,
            'num_agents': len(agents),
            'cycles': cycles,
            'agents': []
        }

        for agent in agents:
            correlations = self.evolve_agent(agent, cycles, sample_interval)

            cycles_list = [c for c, _ in correlations]
            corr_values = [c for _, c in correlations]

            if len(correlations) > 1:
                slope = np.polyfit(cycles_list, corr_values, 1)[0]
            else:
                slope = 0.0

            agent_result = {
                'agent_id': agent.agent_id,
                'initial_energy': agent.energy,
                'autonomy_slope': slope,
                'mean_correlation': np.mean(corr_values),
                'std_correlation': np.std(corr_values)
            }

            condition_results['agents'].append(agent_result)

        slopes = [a['autonomy_slope'] for a in condition_results['agents']]
        condition_results['mean_autonomy_slope'] = np.mean(slopes)
        condition_results['std_autonomy_slope'] = np.std(slopes)

        return condition_results

    def run_timescale(self, cycles: int) -> Dict:
        """Run experiment at one timescale."""
        print(f"\n  Timescale: {cycles} cycles")
        sample_interval = cycles // 10  # 10 measurements per agent

        # Create fresh agents for this timescale
        uniform_agents = self.create_agents_uniform()
        highvar_agents = self.create_agents_high_variance()

        print(f"    Evolving uniform agents...", end='', flush=True)
        uniform_results = self.run_condition('uniform', uniform_agents,
                                           cycles, sample_interval)
        print(f" mean_slope={uniform_results['mean_autonomy_slope']:.6f}")

        print(f"    Evolving high-variance agents...", end='', flush=True)
        highvar_results = self.run_condition('high_variance', highvar_agents,
                                            cycles, sample_interval)
        print(f" mean_slope={highvar_results['mean_autonomy_slope']:.6f}")

        # Compute statistics
        uniform_slopes = [a['autonomy_slope'] for a in uniform_results['agents']]
        highvar_slopes = [a['autonomy_slope'] for a in highvar_results['agents']]

        all_slopes = [uniform_slopes, highvar_slopes]
        between_var = np.var([np.mean(s) for s in all_slopes])
        within_var = np.mean([np.var(s) for s in all_slopes])

        if within_var > 0:
            f_ratio = between_var / within_var
        else:
            f_ratio = 0.0

        mean_diff = np.mean(uniform_slopes) - np.mean(highvar_slopes)

        print(f"    F-ratio: {f_ratio:.6f}, Mean diff: {mean_diff:.6f}")

        return {
            'cycles': cycles,
            'conditions': [uniform_results, highvar_results],
            'f_ratio': f_ratio,
            'mean_difference': mean_diff,
            'interpretation': 'Significant' if f_ratio > 2.0 else 'Moderate' if f_ratio > 1.0 else 'Weak'
        }

    def run_experiment(self) -> Dict:
        """Run full decay dynamics mapping experiment."""
        print("="*70)
        print("DECAY DYNAMICS MAPPING: ENERGY-DEPENDENT PHASE AUTONOMY")
        print("="*70)
        print(f"Timescales: {self.timescales}")
        print(f"Agents per condition: {self.num_agents_per_condition}")
        print(f"Total experiments: {len(self.timescales)} timescales × 2 conditions")
        print()

        start_time = time.time()

        results = {
            'metadata': {
                'experiment': 'Decay Dynamics Mapping of Energy-Dependent Phase Autonomy',
                'cycle': 495,
                'date': datetime.now().isoformat(),
                'hypothesis': 'Energy effects decay exponentially with characteristic timescale τ ≈ 300-400 cycles',
                'parameters': {
                    'timescales': self.timescales,
                    'num_agents_per_condition': self.num_agents_per_condition,
                    'reference_points': {
                        'cycle_493': {'cycles': 200, 'f_ratio': 2.39},
                        'cycle_494': {'cycles': 1000, 'f_ratio': 0.12}
                    }
                }
            },
            'timescales': []
        }

        # Run each timescale
        for cycles in self.timescales:
            timescale_result = self.run_timescale(cycles)
            results['timescales'].append(timescale_result)

        # Analyze decay dynamics
        print()
        print("="*70)
        print("DECAY DYNAMICS ANALYSIS")
        print("="*70)

        cycles_values = [200] + self.timescales  # Include C493 reference
        f_ratios = [2.39] + [t['f_ratio'] for t in results['timescales']]

        print(f"{'Cycles':<10} {'F-ratio':<12} {'Interpretation':<15}")
        print("-"*70)
        for c, f in zip(cycles_values, f_ratios):
            interp = 'Strong' if f > 2.0 else 'Moderate' if f > 1.0 else 'Weak'
            print(f"{c:<10} {f:>10.6f}   {interp:<15}")

        # Fit exponential decay model: F(t) = F_inf + (F_0 - F_inf) * exp(-t/tau)
        # Approximate with simple exponential fit to measured points
        if len(cycles_values) >= 3:
            # Transform to linear: log(F - F_inf) = log(F_0 - F_inf) - t/tau
            # Assume F_inf ≈ 0 for simplicity
            log_f = [np.log(max(f, 0.01)) for f in f_ratios]  # Avoid log(0)

            # Linear fit to log(F) vs t
            fit = np.polyfit(cycles_values, log_f, 1)
            tau_inv = -fit[0]  # -1/tau from slope
            if tau_inv > 0:
                tau = 1.0 / tau_inv
            else:
                tau = float('inf')

            # Estimate critical transition (F=1.0)
            if tau < float('inf'):
                # F(t_c) = F_0 * exp(-t_c/tau) = 1.0
                # t_c = -tau * ln(1.0/F_0)
                F_0 = f_ratios[0]
                if F_0 > 1.0:
                    t_critical = -tau * np.log(1.0 / F_0)
                else:
                    t_critical = 0.0
            else:
                t_critical = float('inf')

            print()
            print("Decay Model: F(t) ≈ F₀ × exp(-t/τ)")
            print(f"  Estimated τ (decay timescale): {tau:.1f} cycles")
            print(f"  Estimated t_c (F=1.0 transition): {t_critical:.1f} cycles")

            results['decay_model'] = {
                'model': 'F(t) = F_0 * exp(-t/tau)',
                'tau_cycles': tau,
                't_critical_cycles': t_critical,
                'F_0': f_ratios[0],
                'fit_quality': 'exponential approximation'
            }
        else:
            print("\nInsufficient data points for decay model fitting")
            results['decay_model'] = None

        elapsed = time.time() - start_time
        results['runtime_seconds'] = elapsed

        print()
        print(f"Experiment completed in {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)")
        print("="*70)

        return results


def main():
    """Run decay dynamics mapping experiment."""

    experiment = DecayDynamicsExperiment()
    results = experiment.run_experiment()

    output_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "cycle495_decay_dynamics_mapping.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
