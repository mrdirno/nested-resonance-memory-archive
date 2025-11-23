#!/usr/bin/env python3
"""
Cycle 265: Critical Phenomena in NRM Energy Phase Transition

Purpose: Test if NRM energy collapse exhibits critical scaling
MOG Resonance: α = 0.75 (Strong, Tier 2 Priority)

Hypothesis: NRM shows second-order phase transition with diverging susceptibility
Predictions:
    1. Susceptibility divergence: χ ∝ |E - E_c|^(-γ) where γ ≈ 1.0
    2. Critical slowing down: τ ∝ |E - E_c|^(-ν·z)
    3. Power-law correlations: ξ ∝ |E - E_c|^(-ν)

Cross-Domain Analogy:
    Domain A (NRM): Energy collapse at E_c = 0.5 (C194 validated)
    Domain B (Physics): Ising ferromagnetic transition with critical exponents
    Coupling: Population variance ↔ Magnetic susceptibility, E_consume ↔ Temperature

Design:
    E_consume values: {0.40, 0.45, 0.47, 0.49, 0.50, 0.51, 0.53, 0.55, 0.60} (9 levels)
    Seeds: n = 50 per condition (450 total experiments)
    Cycles: 5000 (equilibration + measurement)
    Expected Runtime: ~2 hours

Falsification Criteria:
    - Reject if γ ≤ 0 (no divergence)
    - Reject if R² < 0.7 (poor power-law fit)
    - Reject if exponential fits better

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-09 (Cycle 1384 Implementation)
License: GPL-3.0
"""

import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000
E_CONSUME_VALUES = [0.40, 0.45, 0.47, 0.49, 0.50, 0.51, 0.53, 0.55, 0.60]  # 9 levels near E_c = 0.5
E_CRITICAL = 0.50  # Critical point from C194
SEEDS = list(range(42, 92))  # 50 seeds (42-91 inclusive)

# Fixed control parameters
F_SPAWN = 0.025  # 2.5%
E_RECHARGE = 0.5  # Standard from C194
SPAWN_COST = 5.0

# Energy parameters
E_MAX = 50.0
E_THRESHOLD = 20.0

# Population parameters
N_INITIAL = 10  # Standard initialization

# Composition/decomposition thresholds
THETA_COMP = 0.85
THETA_DECOMP = 0.15

# Analysis parameters
EQUILIBRIUM_START = 4000  # Measure variance over last 1000 cycles
EQUILIBRIUM_END = 5000

@dataclass
class Agent:
    """Fractal agent"""
    agent_id: int
    energy: float
    depth: float
    birth_cycle: int

class CriticalPhenomenaSystem:
    """Population system near critical point"""

    def __init__(self, seed: int, e_consume: float, db_path: Path):
        self.seed = seed
        self.e_consume = e_consume
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.composition_count = 0
        self.decomposition_count = 0

        # Time series
        self.population_history: List[int] = []

        # Initialize population
        for _ in range(N_INITIAL):
            self._create_agent()

    def _create_agent(self) -> Agent:
        """Create new agent"""
        depth = self.random.uniform(0.0, 1.0)
        agent = Agent(
            agent_id=self.next_agent_id,
            energy=E_MAX,
            depth=depth,
            birth_cycle=self.cycle_count
        )

        self.agents[agent.agent_id] = agent
        self.next_agent_id += 1

        return agent

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Record population
        self.population_history.append(len(self.agents))

        # Spawn attempt
        if self.random.random() < F_SPAWN:
            self._attempt_spawn()

        # Energy recharge
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + E_RECHARGE)

        # Composition check
        if len(self.agents) >= 2:
            agents_list = list(self.agents.values())
            for i in range(len(agents_list)):
                for j in range(i+1, len(agents_list)):
                    depth_similarity = 1.0 - abs(agents_list[i].depth - agents_list[j].depth)

                    if depth_similarity >= THETA_COMP:
                        agents_list[i].energy -= 2.0
                        agents_list[j].energy -= 2.0
                        self.composition_count += 1

        # Decomposition check
        if len(self.agents) >= 2:
            agents_list = list(self.agents.values())
            for i in range(len(agents_list)):
                for j in range(i+1, len(agents_list)):
                    depth_distance = abs(agents_list[i].depth - agents_list[j].depth)

                    if depth_distance >= THETA_DECOMP:
                        agents_list[i].energy += 1.0
                        agents_list[j].energy += 1.0
                        self.decomposition_count += 1

        # Energy consumption and death
        agents_to_remove = []
        for agent_id, agent in self.agents.items():
            agent.energy -= self.e_consume
            if agent.energy < E_THRESHOLD:
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            if agent_id in self.agents:
                del self.agents[agent_id]

    def _attempt_spawn(self):
        """Attempt to spawn new agent"""
        self.spawn_attempts += 1

        if len(self.agents) == 0:
            return

        parent = self.random.choice(list(self.agents.values()))

        if parent.energy >= (E_THRESHOLD + SPAWN_COST):
            parent.energy -= SPAWN_COST
            self._create_agent()
            self.spawn_successes += 1

    def get_final_statistics(self) -> Dict:
        """Calculate final statistics for critical phenomena analysis"""
        # Equilibrium population metrics
        if len(self.population_history) >= EQUILIBRIUM_END:
            equilibrium_pop = self.population_history[EQUILIBRIUM_START:EQUILIBRIUM_END]
        else:
            equilibrium_pop = self.population_history

        # Susceptibility χ (population variance)
        if len(equilibrium_pop) > 0:
            mean_pop = float(np.mean(equilibrium_pop))
            variance_pop = float(np.var(equilibrium_pop, ddof=1))
            std_pop = float(np.std(equilibrium_pop, ddof=1))
        else:
            mean_pop = 0.0
            variance_pop = 0.0
            std_pop = 0.0

        # Susceptibility χ (normalized by distance from criticality)
        distance_from_critical = abs(self.e_consume - E_CRITICAL)
        susceptibility = variance_pop / distance_from_critical if distance_from_critical > 0 else variance_pop

        # Extinction detection
        extinction = (len(self.agents) == 0) or (mean_pop < 1.0)

        # Order parameter ψ (survival probability)
        order_parameter = 1.0 if not extinction else 0.0

        return {
            'mean_population': mean_pop,
            'std_population': std_pop,
            'variance_population': variance_pop,
            'susceptibility': susceptibility,
            'order_parameter': order_parameter,
            'extinction': extinction,
            'spawn_success_rate': (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0,
            'composition_count': self.composition_count,
            'decomposition_count': self.decomposition_count,
            'final_population': len(self.agents),
            'distance_from_critical': distance_from_critical
        }

def run_experiment(seed: int, e_consume: float, output_path: Path, db_path: Path) -> Dict:
    """Run single critical phenomena experiment"""
    e_consume_idx = E_CONSUME_VALUES.index(e_consume)
    seed_idx = SEEDS.index(seed)
    exp_num = e_consume_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(E_CONSUME_VALUES) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] E_c={e_consume:.2f}, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = CriticalPhenomenaSystem(seed, e_consume, db_path)

    # Run simulation
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    # Get statistics
    stats = system.get_final_statistics()
    elapsed = time.time() - start_time

    # Print results
    print(f"Pop={stats['mean_population']:5.1f} | "
          f"σ²={stats['variance_population']:6.1f} | "
          f"χ={stats['susceptibility']:7.1f} | "
          f"ψ={stats['order_parameter']:.1f} | "
          f"t={elapsed:4.1f}s")

    # Build result
    result = {
        'seed': seed,
        'e_consume': e_consume,
        **stats,
        'runtime_seconds': elapsed,
        'cycles': CYCLES,
        'timestamp': datetime.now().isoformat()
    }

    return result

def main():
    """Execute full critical phenomena experimental suite"""
    print("=" * 80)
    print("CYCLE 265: CRITICAL PHENOMENA IN NRM ENERGY PHASE TRANSITION")
    print("=" * 80)
    print()
    print("Purpose: Test if NRM energy collapse exhibits critical scaling")
    print("MOG Resonance: α = 0.75 (Strong, Tier 2 Priority)")
    print()
    print("Hypothesis: NRM shows second-order phase transition with diverging susceptibility")
    print("Predictions:")
    print("  1. Susceptibility divergence: χ ∝ |E - E_c|^(-γ) where γ ≈ 1.0")
    print("  2. Critical slowing down: τ ∝ |E - E_c|^(-ν·z)")
    print("  3. Power-law correlations: ξ ∝ |E - E_c|^(-ν)")
    print()
    print("Experimental Parameters:")
    print(f"  E_consume values: {E_CONSUME_VALUES} (9 levels near E_c = {E_CRITICAL})")
    print(f"  E_recharge = {E_RECHARGE} (fixed)")
    print(f"  f_spawn = {F_SPAWN * 100}%")
    print(f"  Cycles = {CYCLES}")
    print(f"  Seeds per condition: n = {len(SEEDS)}")
    print(f"  Total experiments: {len(E_CONSUME_VALUES) * len(SEEDS)}")
    print(f"  Expected runtime: ~2 hours")
    print()
    print("Falsification Criteria:")
    print("  - Reject if γ ≤ 0 (no divergence)")
    print("  - Reject if R² < 0.7 (poor power-law fit)")
    print("  - Reject if exponential fits better")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c265_critical_phenomena.json"

    # Create database directory
    db_dir = Path(__file__).parent.parent.parent / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)

    results = []
    start_time_total = time.time()

    # Run experiments
    for e_consume in E_CONSUME_VALUES:
        print()
        print(f"Testing E_consume = {e_consume} (distance from E_c = {abs(e_consume - E_CRITICAL):.2f})")
        print("-" * 80)

        for seed in SEEDS:
            # Create unique database workspace
            db_workspace = db_dir / f"c265_econsume{e_consume}_seed{seed}"
            db_workspace.mkdir(parents=True, exist_ok=True)

            result = run_experiment(seed, e_consume, output_path, db_workspace)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate results
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'E_consume':>10s} | {'|E-E_c|':>10s} | {'Mean χ':>10s} | {'Mean ψ':>10s} | {'Extinct %':>10s}")
    print("-" * 80)

    for e_consume in E_CONSUME_VALUES:
        condition_results = [r for r in results if r['e_consume'] == e_consume]

        mean_susceptibility = np.mean([r['susceptibility'] for r in condition_results])
        mean_order = np.mean([r['order_parameter'] for r in condition_results])

        extinction_count = sum(1 for r in condition_results if r['extinction'])
        extinction_pct = (extinction_count / len(condition_results)) * 100

        distance = abs(e_consume - E_CRITICAL)

        print(f"{e_consume:10.2f} | {distance:10.2f} | {mean_susceptibility:10.1f} | {mean_order:10.2f} | {extinction_pct:10.1f}")

    print()
    print("=" * 80)
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print(f"Results saved: {output_path}")
    print()

    # Save results
    output_data = {
        'experiment': 'C265_Critical_Phenomena',
        'description': 'Test if NRM energy collapse exhibits critical scaling',
        'mog_resonance': 0.75,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'e_consume_values': E_CONSUME_VALUES,
            'e_critical': E_CRITICAL,
            'f_spawn': F_SPAWN,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'equilibrium_start': EQUILIBRIUM_START,
            'equilibrium_end': EQUILIBRIUM_END,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'total_experiments': len(results)
        },
        'results': results,
        'runtime_hours': elapsed_total / 3600
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Experiment complete. Next: Analyze results with falsification gauntlet.")
    print("Run: python code/analysis/analyze_c265_critical_phenomena.py")
    print()

if __name__ == '__main__':
    main()
