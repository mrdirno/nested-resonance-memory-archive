#!/usr/bin/env python3
"""
Cycle 264: Carrying Capacity Dynamics in NRM

Purpose: Test if K = β × E_recharge (ecological carrying capacity analogy)
MOG Resonance: α = 0.92 (Very Strong, Tier 1 Priority)

Hypothesis: NRM energy homeostasis IS carrying capacity dynamics
Prediction: Linear scaling K = β × E_recharge (β > 0, R² > 0.6)

Cross-Domain Analogy:
    Domain A (NRM): Energy constraint limits sustainable population
    Domain B (Ecology): Resource availability determines carrying capacity K
    Coupling: Energy ↔ Resource (HIGH), Self-regulation ↔ Density-dependence (HIGH)

Design:
    Independent Variable: E_recharge = {0.1, 0.25, 0.5, 1.0, 2.0, 4.0}
    Dependent Variable: K (equilibrium population, mean over cycles 4000-5000)
    Control: f_spawn = 2.5%, E_consume = 0.3, spawn_cost = 5.0, cycles = 5000
    Seeds: n = 20 per condition (120 total experiments)
    Expected Runtime: ~2 hours

Falsification Criteria:
    - Reject if R² < 0.6 (weak correlation)
    - Reject if β ≤ 0 (non-positive slope)
    - Reject if non-monotonic relationship

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Date: 2025-11-09 (Cycle 1370 Design, Implementation)
License: GPL-3.0
"""

import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000
E_RECHARGE_VALUES = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]  # 6 levels, 40× range
SEEDS = list(range(42, 62))  # Seeds 42-61 inclusive (n=20)

# Fixed control parameters
F_SPAWN = 0.025  # 2.5% (validated homeostasis frequency)
E_CONSUME = 0.3  # Fixed at net-positive level (all conditions viable)
SPAWN_COST = 5.0  # Baseline from Paper 2
N_INITIAL = 10  # Standard initialization

# Energy parameters (varied by E_recharge)
E_MAX = 50.0
E_THRESHOLD = 20.0

# Composition parameters
THETA_COMP = 0.85  # Composition threshold (85% depth similarity)
THETA_DECOMP = 10.0  # Decomposition threshold (10 units depth distance)

# Analysis parameters
EQUILIBRIUM_START = 4000  # Exclude transient dynamics
EQUILIBRIUM_END = 5000  # Last 1000 cycles for K measurement

@dataclass
class Agent:
    """Single fractal agent with energy and depth"""
    agent_id: int
    energy: float
    depth: float
    birth_cycle: int

@dataclass
class ExperimentResult:
    """Results from single experiment run"""
    seed: int
    e_recharge: float
    mean_population: float  # K (equilibrium population)
    std_population: float  # Population variance
    extinction: bool  # Did population reach zero?
    time_to_equilibrium: int  # Cycles until equilibration
    spawn_success_rate: float  # η = successes / attempts
    spawn_attempts: int
    spawn_successes: int
    composition_events: int
    decomposition_events: int
    final_population: int  # Population at end
    basin: str  # Classification (A, B, C based on population)

class PopulationSystem:
    """Single population with energy regulation (no network structure)"""

    def __init__(self, seed: int, e_recharge: float, db_path: Path):
        self.seed = seed
        self.e_recharge = e_recharge
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
        self.spawn_failures = 0
        self.composition_events = 0
        self.decomposition_events = 0

        # Time series
        self.population_history: List[int] = []
        self.spawn_rate_history: List[float] = []

        # Initialize population
        for _ in range(N_INITIAL):
            self._create_agent()

    def _create_agent(self) -> Agent:
        """Create new agent with random depth"""
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
        pop = len(self.agents)
        self.population_history.append(pop)

        # Spawn attempt
        if self.random.random() < F_SPAWN:
            self._attempt_spawn()

        # Energy recharge for all agents
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + self.e_recharge)

        # Composition check
        self._check_compositions()

        # Decomposition check
        self._check_decompositions()

        # Energy consumption (death if below threshold after consumption)
        agents_to_remove = []
        for agent_id, agent in self.agents.items():
            agent.energy -= E_CONSUME
            if agent.energy < E_THRESHOLD:
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            del self.agents[agent_id]

    def _attempt_spawn(self):
        """Attempt to spawn new agent"""
        self.spawn_attempts += 1

        if len(self.agents) == 0:
            self.spawn_failures += 1
            return

        # Select random parent
        parent = self.random.choice(list(self.agents.values()))

        # Check energy cost
        if parent.energy >= (E_THRESHOLD + SPAWN_COST):
            parent.energy -= SPAWN_COST
            self._create_agent()
            self.spawn_successes += 1
        else:
            self.spawn_failures += 1

    def _check_compositions(self):
        """Check for composition events (depth similarity)"""
        if len(self.agents) < 2:
            return

        agents_list = list(self.agents.values())
        for i in range(len(agents_list)):
            for j in range(i+1, len(agents_list)):
                depth_similarity = 1.0 - abs(agents_list[i].depth - agents_list[j].depth)
                if depth_similarity >= THETA_COMP:
                    # Composition event (both agents lose energy)
                    agents_list[i].energy -= 2.0
                    agents_list[j].energy -= 2.0
                    self.composition_events += 1

    def _check_decompositions(self):
        """Check for decomposition events (depth dissimilarity)"""
        if len(self.agents) < 2:
            return

        agents_list = list(self.agents.values())
        for i in range(len(agents_list)):
            for j in range(i+1, len(agents_list)):
                depth_distance = abs(agents_list[i].depth - agents_list[j].depth)
                if depth_distance >= THETA_DECOMP:
                    # Decomposition event (both agents gain energy)
                    agents_list[i].energy += 1.0
                    agents_list[j].energy += 1.0
                    self.decomposition_events += 1

    def get_final_statistics(self) -> Dict:
        """Calculate final statistics for analysis"""
        # Equilibrium population (mean over last 1000 cycles)
        equilibrium_pop = self.population_history[EQUILIBRIUM_START:EQUILIBRIUM_END]
        mean_pop = float(np.mean(equilibrium_pop))
        std_pop = float(np.std(equilibrium_pop))

        # Extinction detection
        extinction = (len(self.agents) == 0) or (mean_pop < 1.0)

        # Time to equilibrium (when |dN/dt| < 0.1 for 100 consecutive cycles)
        time_to_eq = self._find_equilibrium_time()

        # Spawn success rate
        spawn_rate = (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0

        # Basin classification (based on mean population)
        if mean_pop < 5.0:
            basin = 'C'  # Low population
        elif mean_pop < 25.0:
            basin = 'A'  # Normal homeostasis
        else:
            basin = 'B'  # High population

        return {
            'mean_population': mean_pop,
            'std_population': std_pop,
            'extinction': extinction,
            'time_to_equilibrium': time_to_eq,
            'spawn_success_rate': spawn_rate,
            'spawn_attempts': self.spawn_attempts,
            'spawn_successes': self.spawn_successes,
            'composition_events': self.composition_events,
            'decomposition_events': self.decomposition_events,
            'final_population': len(self.agents),
            'basin': basin
        }

    def _find_equilibrium_time(self) -> int:
        """Find cycle when system reaches equilibrium"""
        if len(self.population_history) < 200:
            return -1

        for t in range(100, len(self.population_history) - 100):
            window = self.population_history[t:t+100]
            # Check if derivative is small
            diffs = np.diff(window)
            if np.max(np.abs(diffs)) < 0.1:
                return t

        return -1  # No equilibrium found

def run_experiment(seed: int, e_recharge: float, output_path: Path, db_path: Path) -> Dict:
    """Run single carrying capacity experiment"""
    exp_num = SEEDS.index(seed) + 1 + (E_RECHARGE_VALUES.index(e_recharge) * len(SEEDS))
    total_exps = len(E_RECHARGE_VALUES) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] E_recharge={e_recharge:4.2f}, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database for clean experiment
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = PopulationSystem(seed, e_recharge, db_path)

    # Run simulation
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    # Get statistics
    stats = system.get_final_statistics()
    elapsed = time.time() - start_time

    # Print results
    print(f"K={stats['mean_population']:5.1f} ± {stats['std_population']:4.1f} | "
          f"Basin {stats['basin']} | "
          f"η={stats['spawn_success_rate']:5.1f}% | "
          f"t={elapsed:5.1f}s")

    # Build result dictionary
    result = {
        'seed': seed,
        'e_recharge': e_recharge,
        **stats,
        'runtime_seconds': elapsed,
        'cycles': CYCLES,
        'timestamp': datetime.now().isoformat()
    }

    return result

def main():
    """Execute full carrying capacity experimental suite"""
    print("=" * 80)
    print("CYCLE 264: CARRYING CAPACITY DYNAMICS IN NRM")
    print("=" * 80)
    print()
    print("Purpose: Test if K = β × E_recharge (ecological carrying capacity analogy)")
    print("MOG Resonance: α = 0.92 (Very Strong Cross-Domain Coupling)")
    print()
    print("Hypothesis: NRM energy homeostasis IS carrying capacity dynamics")
    print("Prediction: K = β × E_recharge (linear relationship, β > 0)")
    print()
    print("Experimental Parameters:")
    print(f"  E_recharge values: {E_RECHARGE_VALUES} (6 levels, 40× range)")
    print(f"  f_spawn = {F_SPAWN * 100}% (validated homeostasis frequency)")
    print(f"  E_consume = {E_CONSUME} (net positive at all levels)")
    print(f"  Cycles = {CYCLES} (sufficient for equilibration)")
    print(f"  Seeds per condition: n = {len(SEEDS)}")
    print(f"  Total experiments: {len(E_RECHARGE_VALUES) * len(SEEDS)}")
    print(f"  Expected runtime: ~2 hours")
    print()
    print("Falsification Criteria:")
    print("  - Reject if R² < 0.6 (weak correlation)")
    print("  - Reject if β ≤ 0 (non-positive slope)")
    print("  - Reject if non-monotonic relationship")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c264_carrying_capacity.json"

    # Create database directory
    db_dir = Path(__file__).parent.parent.parent / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)

    results = []
    start_time_total = time.time()

    # Run experiments
    for e_recharge in E_RECHARGE_VALUES:
        print()
        print(f"Testing E_recharge = {e_recharge}")
        print("-" * 80)

        for seed in SEEDS:
            # Create unique database workspace
            db_workspace = db_dir / f"c264_erecharge{e_recharge}_seed{seed}"
            db_workspace.mkdir(parents=True, exist_ok=True)

            result = run_experiment(seed, e_recharge, output_path, db_workspace)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate results
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'E_recharge':>11s} | {'Mean K':>10s} | {'Std K':>10s} | {'Extinction %':>13s} | {'Mean η %':>10s}")
    print("-" * 80)

    for e_recharge in E_RECHARGE_VALUES:
        condition_results = [r for r in results if r['e_recharge'] == e_recharge]

        mean_K = np.mean([r['mean_population'] for r in condition_results])
        std_K = np.std([r['mean_population'] for r in condition_results])

        extinction_count = sum(1 for r in condition_results if r['extinction'])
        extinction_pct = (extinction_count / len(condition_results)) * 100

        mean_eta = np.mean([r['spawn_success_rate'] for r in condition_results])

        print(f"{e_recharge:11.2f} | {mean_K:10.2f} | {std_K:10.2f} | {extinction_pct:13.1f} | {mean_eta:10.1f}")

    print()
    print("=" * 80)
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print(f"Results saved: {output_path}")
    print()

    # Save results
    output_data = {
        'experiment': 'C264_Carrying_Capacity',
        'description': 'Test if K = β × E_recharge (ecological carrying capacity analogy)',
        'mog_resonance': 0.92,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'e_recharge_values': E_RECHARGE_VALUES,
            'f_spawn': F_SPAWN,
            'e_consume': E_CONSUME,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
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
    print()

if __name__ == '__main__':
    main()
