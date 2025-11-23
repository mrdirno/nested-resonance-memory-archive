#!/usr/bin/env python3
"""
Cycle 266: Phase Transitions in NRM Composition Dynamics

Purpose: Test if NRM exhibits first-order phase transitions
MOG Resonance: α = 0.68 (Moderate Priority)

Hypothesis: NRM shows bistability with discontinuous order parameter jump
Predictions:
    1. Bistability: Hysteresis loop Δf > 0.005
    2. Discontinuous jump: Δϕ > 0.05 at f_c
    3. Metastability: Nucleation time τ > 100 cycles
    4. Latent heat: Energy absorption at transition

Cross-Domain Analogy:
    Domain A (NRM): Composition rate controls population phase
    Domain B (Physics): Temperature controls matter phase (Landau 1937)
    Coupling: f_spawn ↔ Temperature, Compositional density ↔ Order parameter

Design:
    Conditions: SWEEP_UP, SWEEP_DOWN, QUENCH (3 total)
    Seeds: n = 20 per condition (60 total experiments)
    SWEEP: f_spawn 0.010 → 0.050 in steps of 0.002 (21 steps × 1000 cycles)
    QUENCH: Instantaneous jump 0.010 → 0.040
    Expected Runtime: ~6-8 hours

Falsification Criteria:
    - Reject if hysteresis width Δf < 0.002
    - Reject if discontinuity Δϕ < 0.02
    - Reject if no metastability (instant transition)

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
CONDITIONS = ['SWEEP_UP', 'SWEEP_DOWN', 'QUENCH']
SEEDS = list(range(42, 62))  # 20 seeds

# Phase sweep parameters
F_SPAWN_MIN = 0.010
F_SPAWN_MAX = 0.050
F_SPAWN_STEP = 0.002
CYCLES_PER_STEP = 1000  # Equilibration time at each f_spawn

# Quench parameters
F_SPAWN_QUENCH_INITIAL = 0.010
F_SPAWN_QUENCH_FINAL = 0.040
QUENCH_CYCLES = 5000

# Fixed control parameters
E_CONSUME = 0.5
E_RECHARGE = 1.0
SPAWN_COST = 5.0

# Energy parameters
E_MAX = 50.0
E_THRESHOLD = 20.0

# Population parameters
N_INITIAL = 100

# Composition/decomposition thresholds
THETA_COMP = 0.85
THETA_DECOMP = 0.15

@dataclass
class Agent:
    """Fractal agent"""
    agent_id: int
    energy: float
    depth: float
    birth_cycle: int

class PhaseTransitionSystem:
    """Population system with variable composition rate"""

    def __init__(self, seed: int, condition: str, db_path: Path):
        self.seed = seed
        self.condition = condition
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Current f_spawn (varies during experiment)
        self.f_spawn = F_SPAWN_MIN if condition != 'QUENCH' else F_SPAWN_QUENCH_INITIAL

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.composition_count = 0
        self.decomposition_count = 0

        # Phase order parameter history
        self.phi_history: List[float] = []  # Compositional density
        self.energy_history: List[float] = []
        self.f_spawn_history: List[float] = []

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

    def set_f_spawn(self, f_spawn: float):
        """Update composition rate"""
        self.f_spawn = f_spawn

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Spawn attempt
        if self.random.random() < self.f_spawn:
            self._attempt_spawn()

        # Energy recharge
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + E_RECHARGE)

        # Composition check (track compositions this cycle)
        comp_this_cycle = 0
        if len(self.agents) >= 2:
            agents_list = list(self.agents.values())
            for i in range(len(agents_list)):
                for j in range(i+1, len(agents_list)):
                    depth_similarity = 1.0 - abs(agents_list[i].depth - agents_list[j].depth)

                    if depth_similarity >= THETA_COMP:
                        agents_list[i].energy -= 2.0
                        agents_list[j].energy -= 2.0
                        self.composition_count += 1
                        comp_this_cycle += 1

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
            agent.energy -= E_CONSUME
            if agent.energy < E_THRESHOLD:
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            if agent_id in self.agents:
                del self.agents[agent_id]

        # Compute order parameter ϕ (compositional density)
        N = len(self.agents)
        phi = comp_this_cycle / N if N > 0 else 0.0

        # Compute total system energy
        total_energy = sum(a.energy for a in self.agents.values())

        self.phi_history.append(phi)
        self.energy_history.append(total_energy)
        self.f_spawn_history.append(self.f_spawn)

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

    def get_steady_state_phi(self, start_cycle: int, end_cycle: int) -> float:
        """Get mean ϕ over equilibration period"""
        if end_cycle > len(self.phi_history):
            end_cycle = len(self.phi_history)

        if start_cycle >= end_cycle:
            return 0.0

        return float(np.mean(self.phi_history[start_cycle:end_cycle]))

def run_sweep_experiment(seed: int, direction: str, output_path: Path, db_path: Path) -> Dict:
    """Run parameter sweep experiment"""
    exp_idx = CONDITIONS.index(f'SWEEP_{direction}') * len(SEEDS) + SEEDS.index(seed) + 1
    total_exps = len(CONDITIONS) * len(SEEDS)

    print(f"  [{exp_idx:3d}/{total_exps}] SWEEP_{direction:5s}, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = PhaseTransitionSystem(seed, f'SWEEP_{direction}', db_path)

    # Generate f_spawn sequence
    if direction == 'UP':
        f_spawn_values = np.arange(F_SPAWN_MIN, F_SPAWN_MAX + F_SPAWN_STEP/2, F_SPAWN_STEP)
    else:  # DOWN
        f_spawn_values = np.arange(F_SPAWN_MAX, F_SPAWN_MIN - F_SPAWN_STEP/2, -F_SPAWN_STEP)

    # Run sweep
    start_time = time.time()
    sweep_results = []

    for f_spawn in f_spawn_values:
        system.set_f_spawn(f_spawn)
        start_cycle = system.cycle_count

        # Equilibrate at this f_spawn
        for _ in range(CYCLES_PER_STEP):
            system.step()

        # Measure steady-state ϕ
        phi_ss = system.get_steady_state_phi(start_cycle + 500, system.cycle_count)  # Last 500 cycles

        sweep_results.append({
            'f_spawn': float(f_spawn),
            'phi': phi_ss,
            'population': len(system.agents)
        })

    elapsed = time.time() - start_time

    print(f"Steps={len(f_spawn_values)} | "
          f"Final ϕ={sweep_results[-1]['phi']:.4f} | "
          f"t={elapsed:5.1f}s")

    # Build result
    result = {
        'seed': seed,
        'condition': f'SWEEP_{direction}',
        'sweep_data': sweep_results,
        'composition_count': system.composition_count,
        'decomposition_count': system.decomposition_count,
        'runtime_seconds': elapsed,
        'timestamp': datetime.now().isoformat()
    }

    return result

def run_quench_experiment(seed: int, output_path: Path, db_path: Path) -> Dict:
    """Run quench experiment (instantaneous f_spawn jump)"""
    exp_idx = CONDITIONS.index('QUENCH') * len(SEEDS) + SEEDS.index(seed) + 1
    total_exps = len(CONDITIONS) * len(SEEDS)

    print(f"  [{exp_idx:3d}/{total_exps}] QUENCH      , Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = PhaseTransitionSystem(seed, 'QUENCH', db_path)

    # Run at initial f_spawn for equilibration
    start_time = time.time()

    for _ in range(1000):
        system.step()

    # Record pre-quench ϕ
    phi_pre = system.get_steady_state_phi(500, 1000)

    # QUENCH: Instantaneous jump
    system.set_f_spawn(F_SPAWN_QUENCH_FINAL)

    # Run post-quench
    quench_start_cycle = system.cycle_count

    for _ in range(QUENCH_CYCLES):
        system.step()

    # Detect nucleation time (when ϕ exceeds threshold)
    nucleation_time = -1
    phi_threshold = phi_pre + 0.05  # 5% jump indicates nucleation

    for t in range(quench_start_cycle, len(system.phi_history)):
        if system.phi_history[t] > phi_threshold:
            nucleation_time = t - quench_start_cycle
            break

    # Record post-quench ϕ
    phi_post = system.get_steady_state_phi(quench_start_cycle + 500, len(system.phi_history))

    elapsed = time.time() - start_time

    print(f"ϕ_pre={phi_pre:.4f} | "
          f"ϕ_post={phi_post:.4f} | "
          f"τ_nucl={nucleation_time:4d}cy | "
          f"t={elapsed:5.1f}s")

    # Build result
    result = {
        'seed': seed,
        'condition': 'QUENCH',
        'phi_pre': phi_pre,
        'phi_post': phi_post,
        'nucleation_time': nucleation_time,
        'composition_count': system.composition_count,
        'decomposition_count': system.decomposition_count,
        'runtime_seconds': elapsed,
        'timestamp': datetime.now().isoformat()
    }

    return result

def main():
    """Execute full phase transition experimental suite"""
    print("=" * 80)
    print("CYCLE 266: PHASE TRANSITIONS IN NRM COMPOSITION DYNAMICS")
    print("=" * 80)
    print()
    print("Purpose: Test if NRM exhibits first-order phase transitions")
    print("MOG Resonance: α = 0.68 (Moderate Priority)")
    print()
    print("Hypothesis: NRM shows bistability with discontinuous order parameter jump")
    print("Predictions:")
    print("  1. Bistability: Hysteresis loop Δf > 0.005")
    print("  2. Discontinuous jump: Δϕ > 0.05 at f_c")
    print("  3. Metastability: Nucleation time τ > 100 cycles")
    print("  4. Latent heat: Energy absorption at transition")
    print()
    print("Experimental Parameters:")
    print(f"  Conditions: {CONDITIONS} (3 conditions)")
    print(f"  Seeds per condition: n = {len(SEEDS)}")
    print(f"  Total experiments: {len(CONDITIONS) * len(SEEDS)}")
    print(f"  Sweep range: f_spawn = {F_SPAWN_MIN} → {F_SPAWN_MAX}")
    print(f"  Sweep step: Δf = {F_SPAWN_STEP}")
    print(f"  Equilibration per step: {CYCLES_PER_STEP} cycles")
    print(f"  Quench: {F_SPAWN_QUENCH_INITIAL} → {F_SPAWN_QUENCH_FINAL}")
    print(f"  Expected runtime: ~6-8 hours")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c266_phase_transitions.json"

    # Create database directory
    db_dir = Path(__file__).parent.parent.parent / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)

    results = []
    start_time_total = time.time()

    # Run SWEEP_UP experiments
    print()
    print("Testing SWEEP_UP condition (f_spawn: low → high)")
    print("-" * 80)

    for seed in SEEDS:
        db_workspace = db_dir / f"c266_sweep_up_seed{seed}"
        db_workspace.mkdir(parents=True, exist_ok=True)

        result = run_sweep_experiment(seed, 'UP', output_path, db_workspace)
        results.append(result)

    # Run SWEEP_DOWN experiments
    print()
    print("Testing SWEEP_DOWN condition (f_spawn: high → low)")
    print("-" * 80)

    for seed in SEEDS:
        db_workspace = db_dir / f"c266_sweep_down_seed{seed}"
        db_workspace.mkdir(parents=True, exist_ok=True)

        result = run_sweep_experiment(seed, 'DOWN', output_path, db_workspace)
        results.append(result)

    # Run QUENCH experiments
    print()
    print("Testing QUENCH condition (instantaneous jump)")
    print("-" * 80)

    for seed in SEEDS:
        db_workspace = db_dir / f"c266_quench_seed{seed}"
        db_workspace.mkdir(parents=True, exist_ok=True)

        result = run_quench_experiment(seed, output_path, db_workspace)
        results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate results
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print(f"Results saved: {output_path}")
    print()

    # Save results
    output_data = {
        'experiment': 'C266_Phase_Transitions',
        'description': 'Test if NRM exhibits first-order phase transitions',
        'mog_resonance': 0.68,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'conditions': CONDITIONS,
            'f_spawn_min': F_SPAWN_MIN,
            'f_spawn_max': F_SPAWN_MAX,
            'f_spawn_step': F_SPAWN_STEP,
            'cycles_per_step': CYCLES_PER_STEP,
            'f_spawn_quench_initial': F_SPAWN_QUENCH_INITIAL,
            'f_spawn_quench_final': F_SPAWN_QUENCH_FINAL,
            'quench_cycles': QUENCH_CYCLES,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'n_conditions': len(CONDITIONS),
            'total_experiments': len(results)
        },
        'results': results,
        'runtime_hours': elapsed_total / 3600
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Experiment complete. Next: Analyze results with falsification gauntlet.")
    print("Run: python code/analysis/analyze_c266_phase_transitions.py")
    print()

if __name__ == '__main__':
    main()
