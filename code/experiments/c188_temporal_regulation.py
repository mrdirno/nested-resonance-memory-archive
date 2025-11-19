#!/usr/bin/env python3
"""
Cycle 188: Temporal Regulation and Memory Effects

Purpose: Test whether agent memory of recent compositions affects spawn success and temporal dynamics
Background: Paper 2 treated selection as memoryless (uniform random each cycle).
            Real systems exhibit temporal dependencies (refractory periods, memory effects).

Hypothesis: Memory creates effective refractory periods:
            - Recently composed agents → lower selection probability → energy recovery time
            - Result: temporal spreading of compositional load → improved spawn success
            - Prediction: η increases with memory timescale τ

Design:
    Four Memory Conditions:
    1. Baseline (τ=∞): No memory, uniform random (Paper 2 replication)
    2. Short (τ=100): Recent history affects selection
    3. Medium (τ=500): Intermediate memory window
    4. Long (τ=1000): Long-term memory (~1/3 experiment duration)

    Selection Method: Memory-weighted probability
        weight(agent) = exp(-n_recent_compositions / 2.0)

Expected Outcomes:
    H4.1 (Memory Improves Spawn Success):
        η increases with τ: η(τ=1000) > η(τ=∞)

    H4.2 (Memory Reduces Burstiness):
        Burstiness coefficient B decreases with τ: B(τ=1000) < B(τ=∞)
        B = (σ_IEI - μ_IEI) / (σ_IEI + μ_IEI)

    H4.3 (Negative Autocorrelation):
        Agent selection autocorrelation C(τ) < 0 for τ < τ_memory

Mechanism:
    Memory → temporal spreading → fewer simultaneous energy depletions → more spawning capacity

Parameters:
    cycles = 3000
    N_max = 15 (population cap)
    f_spawn = 2.5% (validated homeostasis frequency)
    seeds = 10 per condition (40 total experiments)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-08 (Cycle 1295)
License: GPL-3.0
"""

import sys
import json
import time
import random
import sqlite3
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional, Set
from datetime import datetime
from collections import defaultdict, deque

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 3000
N_INITIAL_MIN = 10
N_INITIAL_MAX = 20
N_MAX = 15  # Population cap (from Paper 2)
F_SPAWN = 0.025  # 2.5% (validated homeostasis frequency)
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Memory conditions (τ_memory in cycles)
MEMORY_CONDITIONS = {
    'baseline': float('inf'),  # No memory (uniform random)
    'short': 100,              # Short-term memory
    'medium': 500,             # Medium-term memory
    'long': 1000,              # Long-term memory
}

# Energy parameters
E_INITIAL = 50.0
E_MAX = 50.0
E_THRESHOLD = 20.0
E_COST = 10.0
RECHARGE_RATE = 0.5

# Composition parameters
THETA_COMP = 0.85
THETA_DECOMP = 10.0

# Population parameters
BASIN_A_THRESHOLD = 2.5

@dataclass
class Agent:
    """Individual fractal agent with composition tracking"""
    id: int
    energy: float
    phase: float
    depth: int = 0
    compositions: int = 0
    last_composition_cycle: int = -1000  # Last time this agent composed

@dataclass
class CompositionEvent:
    """Record of a composition event for burstiness analysis"""
    cycle: int
    parent_id: int
    child_id: int

class MemoryTracker:
    """Track composition history for memory-weighted selection"""

    def __init__(self, tau_memory: float):
        self.tau_memory = tau_memory
        # Map agent_id → deque of composition cycles
        self.history: Dict[int, deque] = defaultdict(lambda: deque())

    def record_composition(self, agent_id: int, cycle: int):
        """Record that agent participated in composition at cycle"""
        self.history[agent_id].append(cycle)

    def count_recent(self, agent_id: int, current_cycle: int) -> int:
        """Count recent compositions within memory window"""
        if agent_id not in self.history:
            return 0

        # Remove old events outside memory window
        agent_history = self.history[agent_id]
        while agent_history and (current_cycle - agent_history[0]) > self.tau_memory:
            agent_history.popleft()

        return len(agent_history)

    def cleanup(self, alive_agent_ids: Set[int]):
        """Remove history for agents that no longer exist"""
        dead_agents = set(self.history.keys()) - alive_agent_ids
        for agent_id in dead_agents:
            del self.history[agent_id]

class MemoryRegulatedPopulation:
    """Single population with memory-weighted selection"""

    def __init__(self, seed: int, memory_condition: str, db_path: Path):
        self.seed = seed
        self.memory_condition = memory_condition
        self.tau_memory = MEMORY_CONDITIONS[memory_condition]
        self.random = random.Random(seed)
        self.np_random = np.random.RandomState(seed)
        self.bridge = TranscendentalBridge(db_path)

        # Agent population
        self.agents: Dict[int, Agent] = {}
        self.next_agent_id = 0
        self.cycle_count = 0

        # Memory tracker
        self.memory_tracker = MemoryTracker(self.tau_memory)

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.spawn_failures = 0
        self.composition_events: List[CompositionEvent] = []

        # Selection tracking (for autocorrelation analysis)
        self.selection_history: Dict[int, List[int]] = defaultdict(list)  # agent_id → [cycles when selected]

        self._initialize_agents()

    def _initialize_agents(self):
        """Create initial population"""
        n_initial = self.random.randint(N_INITIAL_MIN, N_INITIAL_MAX)

        for _ in range(n_initial):
            phase = self.bridge.get_phase(np.pi)
            agent = Agent(
                id=self.next_agent_id,
                energy=E_INITIAL,
                phase=phase,
                depth=0,
                compositions=0
            )
            self.agents[self.next_agent_id] = agent
            self.next_agent_id += 1

    def _select_parent_memory_weighted(self) -> Optional[Agent]:
        """Select parent with memory-weighted probability"""
        if not self.agents:
            return None

        # Baseline condition: uniform random (no memory)
        if self.memory_condition == 'baseline':
            return self.random.choice(list(self.agents.values()))

        # Memory-weighted selection
        agent_list = list(self.agents.values())
        weights = []

        for agent in agent_list:
            # Count recent compositions
            n_recent = self.memory_tracker.count_recent(agent.id, self.cycle_count)

            # Exponential decay: more recent compositions → lower weight
            weight = np.exp(-n_recent / 2.0)
            weights.append(weight)

        # Normalize and sample
        total_weight = sum(weights)
        if total_weight == 0:
            # Fallback to uniform random if all weights are 0 (shouldn't happen)
            return self.random.choice(agent_list)

        probabilities = np.array(weights) / total_weight
        selected_idx = self.np_random.choice(len(agent_list), p=probabilities)

        return agent_list[selected_idx]

    def _try_spawn(self):
        """Attempt to spawn new agent (memory-weighted parent selection)"""
        self.spawn_attempts += 1

        parent = self._select_parent_memory_weighted()
        if parent is None:
            self.spawn_failures += 1
            return

        # Record selection
        self.selection_history[parent.id].append(self.cycle_count)

        # Check energy threshold
        if parent.energy < E_THRESHOLD:
            self.spawn_failures += 1
            return

        # Check population cap
        if len(self.agents) >= N_MAX:
            self.spawn_failures += 1
            return

        # Spawn succeeds
        parent.energy -= E_COST
        parent.compositions += 1
        parent.last_composition_cycle = self.cycle_count
        self.spawn_successes += 1

        # Record composition event
        self.memory_tracker.record_composition(parent.id, self.cycle_count)

        # Create child agent
        phase = self.bridge.get_phase(np.e)
        child = Agent(
            id=self.next_agent_id,
            energy=E_INITIAL,
            phase=phase,
            depth=parent.depth + 1,
            compositions=0
        )
        self.agents[self.next_agent_id] = child

        # Record composition event for burstiness analysis
        event = CompositionEvent(
            cycle=self.cycle_count,
            parent_id=parent.id,
            child_id=self.next_agent_id
        )
        self.composition_events.append(event)

        self.next_agent_id += 1

    def _recharge_energy(self):
        """Recharge all agents' energy"""
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + RECHARGE_RATE)

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Spawn attempts (Poisson with mean = f_spawn * N)
        n_agents = len(self.agents)
        n_spawn_attempts = self.np_random.poisson(F_SPAWN * n_agents)

        for _ in range(n_spawn_attempts):
            self._try_spawn()

        # Energy recharge
        self._recharge_energy()

        # Periodic cleanup of memory tracker (remove dead agents)
        if self.cycle_count % 100 == 0:
            alive_ids = set(self.agents.keys())
            self.memory_tracker.cleanup(alive_ids)

    def _calculate_burstiness(self) -> float:
        """Calculate burstiness coefficient B = (σ - μ) / (σ + μ)"""
        if len(self.composition_events) < 2:
            return 0.0

        # Inter-event intervals (IEI)
        event_times = [e.cycle for e in self.composition_events]
        ieis = np.diff(sorted(event_times))

        if len(ieis) == 0:
            return 0.0

        mu = np.mean(ieis)
        sigma = np.std(ieis)

        if mu + sigma == 0:
            return 0.0

        B = (sigma - mu) / (sigma + mu)
        return B

    def _calculate_autocorrelation(self, max_lag: int = 100) -> List[float]:
        """Calculate average autocorrelation across all agents"""
        if not self.selection_history:
            return [0.0] * (max_lag + 1)

        # Create binary time series for each agent
        autocorrs = []

        for agent_id, selection_cycles in self.selection_history.items():
            if len(selection_cycles) < 3:  # Need minimum selections for meaningful ACF
                continue

            # Create binary series: 1 if selected, 0 otherwise
            series = np.zeros(self.cycle_count + 1)
            for cycle in selection_cycles:
                series[cycle] = 1

            # Compute autocorrelation
            try:
                acf = np.correlate(series, series, mode='full')
                acf = acf[len(acf)//2:]  # Take positive lags only

                # Normalize by zero-lag value
                if acf[0] > 0:
                    acf = acf / acf[0]
                    acf = acf[:max_lag + 1]  # Truncate to max_lag

                    # Pad if needed
                    if len(acf) < max_lag + 1:
                        acf = np.pad(acf, (0, max_lag + 1 - len(acf)))

                    autocorrs.append(acf)
            except:
                pass

        if not autocorrs:
            return [0.0] * (max_lag + 1)

        # Average across agents
        mean_acf = np.mean(autocorrs, axis=0)
        return mean_acf.tolist()

    def get_final_statistics(self) -> Dict:
        """Calculate final experiment statistics"""
        mean_population = len(self.agents)
        basin = 'A' if mean_population > BASIN_A_THRESHOLD else 'B'

        spawn_success_rate = (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0

        # Burstiness
        burstiness = self._calculate_burstiness()

        # Autocorrelation
        autocorrelation = self._calculate_autocorrelation(max_lag=100)

        # Inter-event intervals for analysis
        event_times = [e.cycle for e in self.composition_events]
        ieis = np.diff(sorted(event_times)).tolist() if len(event_times) > 1 else []

        # Agent selection frequency
        agent_data = []
        for aid, agent in self.agents.items():
            n_selections = len(self.selection_history.get(aid, []))
            agent_data.append({
                'agent_id': aid,
                'final_energy': agent.energy,
                'depth': agent.depth,
                'compositions': agent.compositions,
                'n_selections': n_selections,
                'last_composition_cycle': agent.last_composition_cycle,
            })

        return {
            'cycle': self.cycle_count,
            'memory_condition': self.memory_condition,
            'tau_memory': self.tau_memory,
            'final_agents': len(self.agents),
            'mean_population': mean_population,
            'basin': basin,
            'spawn_attempts': self.spawn_attempts,
            'spawn_successes': self.spawn_successes,
            'spawn_failures': self.spawn_failures,
            'spawn_success_rate': spawn_success_rate,
            'n_composition_events': len(self.composition_events),
            'temporal_metrics': {
                'burstiness': burstiness,
                'autocorrelation': autocorrelation,
                'mean_iei': np.mean(ieis) if ieis else 0.0,
                'std_iei': np.std(ieis) if ieis else 0.0,
            },
            'inter_event_intervals': ieis,  # For detailed analysis
            'agent_data': agent_data,
        }

def run_experiment(seed: int, memory_condition: str, output_path: Path, db_path: Path) -> Dict:
    """Run single memory regulation experiment"""
    conditions = list(MEMORY_CONDITIONS.keys())
    cond_idx = conditions.index(memory_condition)
    seed_idx = SEEDS.index(seed)
    exp_num = cond_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(conditions) * len(SEEDS)

    tau = MEMORY_CONDITIONS[memory_condition]
    tau_str = "∞" if tau == float('inf') else f"{tau:4.0f}"

    print(f"  [{exp_num:2d}/{total_exps}] {memory_condition:8s} (τ={tau_str}), Seed {seed:3d}: ", end='', flush=True)

    clear_bridge_database(db_path / "bridge.db")
    system = MemoryRegulatedPopulation(seed, memory_condition, db_path)

    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    final_stats = system.get_final_statistics()
    elapsed_total = time.time() - start_time

    print(f"Basin {final_stats['basin']} | "
          f"Pop: {final_stats['mean_population']:5.1f} | "
          f"η: {final_stats['spawn_success_rate']:5.1f}% | "
          f"B: {final_stats['temporal_metrics']['burstiness']:6.3f} | "
          f"{elapsed_total:4.0f}s")

    final_stats['seed'] = seed
    final_stats['elapsed_seconds'] = elapsed_total

    return final_stats

def main():
    """Execute C188 temporal regulation experiments"""

    print("=" * 80)
    print("CYCLE 188: TEMPORAL REGULATION AND MEMORY EFFECTS")
    print("=" * 80)
    print()
    print("Purpose: Test if memory of recent compositions affects spawn success and temporal dynamics")
    print("Background: Paper 2 treated selection as memoryless (uniform random each cycle).")
    print("            C188 tests memory-weighted selection (recently composed → lower probability)")
    print()
    print(f"Memory Conditions (τ_memory):")
    print(f"  Baseline (τ=∞): No memory, uniform random (Paper 2 replication)")
    print(f"  Short (τ=100): Recent history affects selection")
    print(f"  Medium (τ=500): Intermediate memory window")
    print(f"  Long (τ=1000): Long-term memory (~1/3 experiment duration)")
    print()
    print(f"Selection Method:")
    print(f"  weight(agent) = exp(-n_recent_compositions / 2.0)")
    print(f"  Recently composed agents → lower selection probability → energy recovery time")
    print()
    print(f"Experimental Parameters:")
    print(f"  f_spawn = {F_SPAWN*100:.1f}% (validated homeostasis frequency)")
    print(f"  N_max = {N_MAX} (population cap)")
    print(f"  Cycles = {CYCLES}")
    print(f"  Seeds per condition: n={len(SEEDS)}")
    print(f"  Total experiments: {len(MEMORY_CONDITIONS) * len(SEEDS)}")
    print(f"  Expected runtime: ~{len(MEMORY_CONDITIONS) * len(SEEDS) * 0.06:.1f} hours")
    print()
    print(f"Hypotheses:")
    print(f"  H4.1 (Memory Improves Spawn Success): η increases with τ")
    print(f"  H4.2 (Memory Reduces Burstiness): B decreases with τ")
    print(f"  H4.3 (Negative Autocorrelation): C(τ) < 0 for τ < τ_memory")
    print()

    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c188_temporal_regulation.json"

    db_path = Path(__file__).parent.parent / "bridge"

    results = []
    start_time_total = time.time()

    for memory_condition in MEMORY_CONDITIONS.keys():
        print()
        print(f"Testing {memory_condition.upper()} memory (τ={MEMORY_CONDITIONS[memory_condition]})")
        print("-" * 80)

        for seed in SEEDS:
            result = run_experiment(seed, memory_condition, output_path, db_path)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'Condition':>10s} | {'τ':>6s} | {'Basin A %':>10s} | {'Mean η %':>10s} | {'Mean B':>8s}")
    print("-" * 80)

    condition_aggregates = []
    for memory_condition in MEMORY_CONDITIONS.keys():
        cond_results = [r for r in results if r['memory_condition'] == memory_condition]

        basin_a_count = sum(1 for r in cond_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(cond_results)) * 100

        spawn_rates = [r['spawn_success_rate'] for r in cond_results]
        mean_spawn_rate = np.mean(spawn_rates)

        burstiness_values = [r['temporal_metrics']['burstiness'] for r in cond_results]
        mean_burstiness = np.mean(burstiness_values)

        tau = MEMORY_CONDITIONS[memory_condition]
        tau_str = "∞" if tau == float('inf') else f"{tau:.0f}"

        condition_aggregates.append({
            'memory_condition': memory_condition,
            'tau_memory': tau,
            'basin_a_pct': basin_a_pct,
            'mean_spawn_rate': mean_spawn_rate,
            'spawn_rate_values': spawn_rates,  # For statistical tests
            'mean_burstiness': mean_burstiness,
            'burstiness_values': burstiness_values,
        })

        print(f"{memory_condition:>10s} | {tau_str:>6s} | {basin_a_pct:9.1f}% | {mean_spawn_rate:9.1f}% | {mean_burstiness:8.3f}")

    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print()

    print("=" * 80)
    print("HYPOTHESIS TESTING")
    print("=" * 80)
    print()

    # H4.1: Memory improves spawn success
    baseline_rate = condition_aggregates[0]['mean_spawn_rate']  # baseline
    short_rate = condition_aggregates[1]['mean_spawn_rate']     # short
    medium_rate = condition_aggregates[2]['mean_spawn_rate']    # medium
    long_rate = condition_aggregates[3]['mean_spawn_rate']      # long

    print("H4.1 (Memory Improves Spawn Success):")
    print(f"  Baseline (τ=∞):  η = {baseline_rate:.1f}%")
    print(f"  Short (τ=100):   η = {short_rate:.1f}%")
    print(f"  Medium (τ=500):  η = {medium_rate:.1f}%")
    print(f"  Long (τ=1000):   η = {long_rate:.1f}%")

    if long_rate > baseline_rate:
        improvement = long_rate - baseline_rate
        print(f"  ✓ Memory IMPROVES spawn success: Δη = +{improvement:.1f}%")
        h41_result = "SUPPORTED"
    else:
        print(f"  ⚠ Memory does NOT improve spawn success")
        h41_result = "NOT_SUPPORTED"
    print()

    # H4.2: Memory reduces burstiness
    baseline_B = condition_aggregates[0]['mean_burstiness']
    short_B = condition_aggregates[1]['mean_burstiness']
    medium_B = condition_aggregates[2]['mean_burstiness']
    long_B = condition_aggregates[3]['mean_burstiness']

    print("H4.2 (Memory Reduces Burstiness):")
    print(f"  Baseline (τ=∞):  B = {baseline_B:.3f}")
    print(f"  Short (τ=100):   B = {short_B:.3f}")
    print(f"  Medium (τ=500):  B = {medium_B:.3f}")
    print(f"  Long (τ=1000):   B = {long_B:.3f}")

    if long_B < baseline_B:
        reduction = baseline_B - long_B
        print(f"  ✓ Memory REDUCES burstiness: ΔB = -{reduction:.3f}")
        h42_result = "SUPPORTED"
    else:
        print(f"  ⚠ Memory does NOT reduce burstiness")
        h42_result = "NOT_SUPPORTED"
    print()

    print(f"Note: Detailed statistical tests (ANOVA, t-tests, autocorrelation) will be performed by")
    print(f"      analysis pipeline (analyze_c188_temporal_regulation.py)")
    print()

    output_data = {
        'metadata': {
            'experiment': 'C188_TEMPORAL_REGULATION',
            'date': datetime.now().isoformat(),
            'purpose': 'Test memory effects on spawn success and temporal dynamics',
            'memory_conditions': {k: v for k, v in MEMORY_CONDITIONS.items()},
            'f_spawn': F_SPAWN,
            'n_max': N_MAX,
            'cycles': CYCLES,
            'seeds': SEEDS,
            'hypotheses': {
                'H4.1': 'Memory improves spawn success: η increases with τ',
                'H4.2': 'Memory reduces burstiness: B decreases with τ',
                'H4.3': 'Negative autocorrelation: C(τ) < 0 for τ < τ_memory',
            }
        },
        'condition_aggregates': condition_aggregates,
        'hypothesis_results': {
            'H4.1': h41_result,
            'H4.2': h42_result,
        },
        'individual_results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("C188 COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Run analysis pipeline: python code/analysis/analyze_c188_temporal_regulation.py")
    print("  2. Generate publication figures (η vs. τ, burstiness, autocorrelation)")
    print("  3. Perform statistical tests (ANOVA, correlations)")
    print("  4. Update Paper 4 Section 3.4 with empirical results")

if __name__ == "__main__":
    main()
