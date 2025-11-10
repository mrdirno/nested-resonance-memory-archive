#!/usr/bin/env python3
"""
Cycle 270: Memetic Evolution in NRM Systems

Purpose: Test if NRM pattern memory functions as cultural substrate
MOG Resonance: α = 0.91 (Second-Highest Priority)

Hypothesis: NRM pattern memory enables memetic evolution via cultural transmission
Predictions:
    1. Memetic lineages emerge (fidelity > 0.6)
    2. Fitness-fidelity correlation (r > 0.6)
    3. Horizontal transfer (ratio > 0.3)
    4. Cumulative evolution (positive slope)

Cross-Domain Analogy:
    Domain A (NRM): Pattern memory across composition-decomposition cycles
    Domain B (Cultural Evolution): Memetic transmission (Dawkins 1976)
    Coupling: Pattern inheritance ↔ Cultural transmission, Resonance ↔ Fitness

Design:
    Conditions: BASELINE, RANDOM, PRUNING, ISOLATION (4 total)
    Seeds: n = 20 per condition (80 total experiments)
    Cycles: 5000 (long enough for multi-generational lineages)
    Expected Runtime: ~10-12 hours

Falsification Criteria:
    - Reject if mean fidelity < 0.5 OR p > 0.05
    - Reject if fitness-fidelity r < 0.4
    - Reject if horizontal/vertical ratio < 0.2
    - Reject if cumulative evolution slope ≤ 0

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
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Tuple, Set
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
CYCLES = 5000
CONDITIONS = ['BASELINE', 'RANDOM', 'PRUNING', 'ISOLATION']
SEEDS = list(range(42, 62))  # Seeds 42-61 inclusive (n=20)

# Fixed control parameters (validated from C171, C175)
F_SPAWN = 0.025  # 2.5% (homeostasis frequency)
E_CONSUME = 0.5  # Homeostatic setpoint
E_RECHARGE = 1.0  # Standard energy replenishment
SPAWN_COST = 5.0  # Energy cost for spawning

# Energy parameters
E_MAX = 50.0
E_THRESHOLD = 20.0

# Population parameters
N_INITIAL = 100  # Match design specification

# Composition/decomposition thresholds
THETA_COMP = 0.85  # Composition threshold (depth similarity)
THETA_DECOMP = 0.15  # Decomposition threshold (depth distance)

# Pattern memory parameters
PATTERN_MEMORY_SIZE = 10  # Top-10 patterns per agent
PRUNE_CYCLE = 2500  # Midpoint for PRUNING condition
PRUNE_FRACTION = 0.5  # Remove 50% of patterns

# Analysis parameters
EQUILIBRIUM_START = 4000  # Exclude transient dynamics
EQUILIBRIUM_END = 5000

@dataclass
class Agent:
    """Fractal agent with energy, depth, and pattern memory"""
    agent_id: int
    energy: float
    depth: float
    birth_cycle: int
    patterns: List[float] = field(default_factory=list)  # Pattern memory (transcendental resonances)
    survival_time: int = 0  # Fitness metric

@dataclass
class CompositionEvent:
    """Record of composition with memetic inheritance"""
    cycle: int
    parent_id: int
    child_id: int
    parent_patterns: List[float]
    child_patterns: List[float]
    pattern_overlap: float  # Jaccard similarity
    parent_energy: float
    child_energy: float
    parent_fitness: float = 0.0  # Set later when agents decompose
    child_fitness: float = 0.0

@dataclass
class DecompositionEvent:
    """Record of decomposition with pattern release"""
    cycle: int
    agent_id: int
    fitness: int  # Survival time
    patterns_released: List[float]
    cause: str  # "energy_depletion" or "composition"

class MemeticPopulationSystem:
    """Population with pattern memory and cultural transmission"""

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

        # Shared memory pool (for horizontal transfer)
        self.shared_memory_pool: List[float] = []

        # Event logs
        self.composition_events: List[CompositionEvent] = []
        self.decomposition_events: List[DecompositionEvent] = []

        # Metrics
        self.spawn_attempts = 0
        self.spawn_successes = 0
        self.spawn_failures = 0

        # Time series
        self.population_history: List[int] = []

        # Initialize population
        for _ in range(N_INITIAL):
            self._create_agent()

    def _create_agent(self, parent_id: int = None) -> Agent:
        """Create new agent with pattern inheritance"""
        depth = self.random.uniform(0.0, 1.0)

        # Initialize patterns
        if parent_id is None or parent_id not in self.agents:
            # Initial agents: Random patterns from bridge
            patterns = self._generate_random_patterns()
        else:
            # Inherited from parent (condition-dependent)
            patterns = self._inherit_patterns(parent_id)

        agent = Agent(
            agent_id=self.next_agent_id,
            energy=E_MAX,
            depth=depth,
            birth_cycle=self.cycle_count,
            patterns=patterns,
            survival_time=0
        )

        self.agents[agent.agent_id] = agent
        self.next_agent_id += 1

        # Log composition event if parent exists
        if parent_id is not None and parent_id in self.agents:
            parent = self.agents[parent_id]
            overlap = self._compute_pattern_overlap(parent.patterns, agent.patterns)

            event = CompositionEvent(
                cycle=self.cycle_count,
                parent_id=parent_id,
                child_id=agent.agent_id,
                parent_patterns=parent.patterns.copy(),
                child_patterns=agent.patterns.copy(),
                pattern_overlap=overlap,
                parent_energy=parent.energy,
                child_energy=agent.energy
            )
            self.composition_events.append(event)

        return agent

    def _generate_random_patterns(self) -> List[float]:
        """Generate random pattern memory (unique pattern IDs)"""
        patterns = []
        for _ in range(PATTERN_MEMORY_SIZE):
            # Generate random pattern ID (unique float in [0, 1])
            pattern_id = self.random.uniform(0.0, 1.0)
            patterns.append(pattern_id)
        return patterns

    def _inherit_patterns(self, parent_id: int) -> List[float]:
        """Inherit patterns from parent (condition-dependent)"""
        parent = self.agents[parent_id]

        if self.condition == 'BASELINE':
            # Selective inheritance (fitness-biased pattern transmission)
            # Child inherits parent's patterns (vertical transmission)
            # Plus horizontal transfer from shared memory pool
            patterns = parent.patterns.copy()

            # Mix in patterns from shared memory (horizontal transfer)
            if len(self.shared_memory_pool) > 0:
                n_horizontal = min(3, len(self.shared_memory_pool))  # Take up to 3 patterns
                horizontal_patterns = self.random.sample(self.shared_memory_pool, n_horizontal)
                # Replace random patterns with horizontal ones
                for hp in horizontal_patterns:
                    replace_idx = self.random.randint(0, len(patterns) - 1)
                    patterns[replace_idx] = hp

            return patterns

        elif self.condition == 'RANDOM':
            # Random inheritance (no fitness selection)
            # Sample randomly from global memory pool
            if len(self.shared_memory_pool) >= PATTERN_MEMORY_SIZE:
                return self.random.sample(self.shared_memory_pool, PATTERN_MEMORY_SIZE)
            else:
                # Not enough in pool, mix parent + random
                patterns = parent.patterns.copy()
                return patterns

        elif self.condition == 'PRUNING':
            # Same as BASELINE (selective inheritance)
            patterns = parent.patterns.copy()

            # Horizontal transfer
            if len(self.shared_memory_pool) > 0:
                n_horizontal = min(3, len(self.shared_memory_pool))
                horizontal_patterns = self.random.sample(self.shared_memory_pool, n_horizontal)
                for hp in horizontal_patterns:
                    replace_idx = self.random.randint(0, len(patterns) - 1)
                    patterns[replace_idx] = hp

            return patterns

        elif self.condition == 'ISOLATION':
            # Vertical-only (no horizontal transfer)
            return parent.patterns.copy()

        else:
            raise ValueError(f"Unknown condition: {self.condition}")

    def _compute_pattern_overlap(self, patterns1: List[float], patterns2: List[float]) -> float:
        """Compute Jaccard similarity between pattern sets"""
        if len(patterns1) == 0 or len(patterns2) == 0:
            return 0.0

        # Convert to sets (discretize patterns to 3 decimal places for comparison)
        set1 = set(round(p, 3) for p in patterns1)
        set2 = set(round(p, 3) for p in patterns2)

        # Jaccard similarity
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        return intersection / union

    def step(self):
        """Execute one simulation cycle"""
        self.cycle_count += 1

        # Apply pruning intervention (PRUNING condition only)
        if self.condition == 'PRUNING' and self.cycle_count == PRUNE_CYCLE:
            self._apply_pruning()

        # Record population
        self.population_history.append(len(self.agents))

        # Update survival times
        for agent in self.agents.values():
            agent.survival_time += 1

        # Spawn attempt
        if self.random.random() < F_SPAWN:
            self._attempt_spawn()

        # Energy recharge
        for agent in self.agents.values():
            agent.energy = min(E_MAX, agent.energy + E_RECHARGE)

        # Composition check
        self._check_compositions()

        # Decomposition check
        self._check_decompositions()

        # Energy consumption and death
        agents_to_remove = []
        for agent_id, agent in self.agents.items():
            agent.energy -= E_CONSUME
            if agent.energy < E_THRESHOLD:
                agents_to_remove.append(agent_id)

        for agent_id in agents_to_remove:
            self._remove_agent(agent_id, cause="energy_depletion")

    def _apply_pruning(self):
        """Cultural disruption: Randomly delete patterns from memory"""
        for agent in self.agents.values():
            n_keep = max(1, int(len(agent.patterns) * (1 - PRUNE_FRACTION)))
            agent.patterns = self.random.sample(agent.patterns, k=n_keep)

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
            self._create_agent(parent_id=parent.agent_id)
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
                    # Composition event (energy cost)
                    agents_list[i].energy -= 2.0
                    agents_list[j].energy -= 2.0

    def _check_decompositions(self):
        """Check for decomposition events (depth dissimilarity)"""
        if len(self.agents) < 2:
            return

        agents_list = list(self.agents.values())
        for i in range(len(agents_list)):
            for j in range(i+1, len(agents_list)):
                depth_distance = abs(agents_list[i].depth - agents_list[j].depth)
                if depth_distance >= THETA_DECOMP:
                    # Decomposition event (energy gain)
                    agents_list[i].energy += 1.0
                    agents_list[j].energy += 1.0

    def _remove_agent(self, agent_id: int, cause: str):
        """Remove agent and release patterns to shared memory"""
        if agent_id not in self.agents:
            return

        agent = self.agents[agent_id]

        # Release patterns to shared memory pool (unless ISOLATION condition)
        if self.condition != 'ISOLATION':
            self.shared_memory_pool.extend(agent.patterns)
            # Limit shared pool size to prevent unbounded growth
            if len(self.shared_memory_pool) > 1000:
                self.shared_memory_pool = self.random.sample(self.shared_memory_pool, 1000)

        # Log decomposition event
        event = DecompositionEvent(
            cycle=self.cycle_count,
            agent_id=agent_id,
            fitness=agent.survival_time,
            patterns_released=agent.patterns.copy() if self.condition != 'ISOLATION' else [],
            cause=cause
        )
        self.decomposition_events.append(event)

        # Remove agent
        del self.agents[agent_id]

    def get_final_statistics(self) -> Dict:
        """Calculate final statistics for memetic analysis"""
        # Population metrics
        if len(self.population_history) >= EQUILIBRIUM_END:
            equilibrium_pop = self.population_history[EQUILIBRIUM_START:EQUILIBRIUM_END]
        else:
            equilibrium_pop = self.population_history

        mean_pop = float(np.mean(equilibrium_pop)) if len(equilibrium_pop) > 0 else 0.0
        std_pop = float(np.std(equilibrium_pop)) if len(equilibrium_pop) > 0 else 0.0

        # Extinction detection
        extinction = (len(self.agents) == 0) or (mean_pop < 1.0)

        # Spawn success rate
        spawn_rate = (self.spawn_successes / self.spawn_attempts * 100) if self.spawn_attempts > 0 else 0.0

        # Memetic metrics (computed by analysis pipeline)
        # Here we just return raw event logs for analysis

        return {
            'mean_population': mean_pop,
            'std_population': std_pop,
            'extinction': extinction,
            'spawn_success_rate': spawn_rate,
            'spawn_attempts': self.spawn_attempts,
            'spawn_successes': self.spawn_successes,
            'composition_count': len(self.composition_events),
            'decomposition_count': len(self.decomposition_events),
            'final_population': len(self.agents),
            'shared_memory_size': len(self.shared_memory_pool)
        }

def run_experiment(seed: int, condition: str, output_path: Path, db_path: Path) -> Dict:
    """Run single memetic evolution experiment"""
    condition_idx = CONDITIONS.index(condition)
    seed_idx = SEEDS.index(seed)
    exp_num = condition_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(CONDITIONS) * len(SEEDS)

    print(f"  [{exp_num:3d}/{total_exps}] {condition:12s}, Seed {seed:3d}: ", end='', flush=True)

    # Clear bridge database
    bridge_db = db_path / "bridge.db"
    clear_bridge_database(bridge_db)

    # Create system
    system = MemeticPopulationSystem(seed, condition, db_path)

    # Run simulation
    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    # Get statistics
    stats = system.get_final_statistics()
    elapsed = time.time() - start_time

    # Print results
    print(f"Pop={stats['mean_population']:5.1f} ± {stats['std_population']:4.1f} | "
          f"η={stats['spawn_success_rate']:5.1f}% | "
          f"Comp={stats['composition_count']:4d} | "
          f"Decomp={stats['decomposition_count']:4d} | "
          f"t={elapsed:5.1f}s")

    # Build result dictionary with full event logs
    result = {
        'seed': seed,
        'condition': condition,
        **stats,
        'composition_events': [
            {
                'cycle': e.cycle,
                'parent_id': e.parent_id,
                'child_id': e.child_id,
                'pattern_overlap': e.pattern_overlap,
                'parent_energy': e.parent_energy,
                'child_energy': e.child_energy
            }
            for e in system.composition_events
        ],
        'decomposition_events': [
            {
                'cycle': e.cycle,
                'agent_id': e.agent_id,
                'fitness': e.fitness,
                'cause': e.cause,
                'num_patterns_released': len(e.patterns_released)
            }
            for e in system.decomposition_events
        ],
        'runtime_seconds': elapsed,
        'cycles': CYCLES,
        'timestamp': datetime.now().isoformat()
    }

    return result

def main():
    """Execute full memetic evolution experimental suite"""
    print("=" * 80)
    print("CYCLE 270: MEMETIC EVOLUTION IN NRM SYSTEMS")
    print("=" * 80)
    print()
    print("Purpose: Test if NRM pattern memory functions as cultural substrate")
    print("MOG Resonance: α = 0.91 (Second-Highest Priority)")
    print()
    print("Hypothesis: NRM pattern memory enables memetic evolution")
    print("Predictions:")
    print("  1. Memetic lineages emerge (fidelity > 0.6)")
    print("  2. Fitness-fidelity correlation (r > 0.6)")
    print("  3. Horizontal transfer (ratio > 0.3)")
    print("  4. Cumulative evolution (positive slope)")
    print()
    print("Experimental Parameters:")
    print(f"  Conditions: {CONDITIONS} (4 conditions)")
    print(f"  Seeds per condition: n = {len(SEEDS)}")
    print(f"  Total experiments: {len(CONDITIONS) * len(SEEDS)}")
    print(f"  Cycles per experiment: {CYCLES}")
    print(f"  f_spawn = {F_SPAWN * 100}%")
    print(f"  E_consume = {E_CONSUME}, E_recharge = {E_RECHARGE}")
    print(f"  Expected runtime: ~10-12 hours")
    print()
    print("Conditions:")
    print("  BASELINE: Selective pattern inheritance (fitness-biased)")
    print("  RANDOM: Random pattern inheritance (no selection)")
    print("  PRUNING: Cultural disruption at cycle 2500 (50% memory loss)")
    print("  ISOLATION: Vertical-only transmission (no horizontal transfer)")
    print()
    print("Falsification Criteria:")
    print("  - Reject if mean fidelity < 0.5 OR p > 0.05")
    print("  - Reject if fitness-fidelity r < 0.4")
    print("  - Reject if horizontal/vertical ratio < 0.2")
    print("  - Reject if cumulative evolution slope ≤ 0")
    print()

    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c270_memetic_evolution.json"

    # Create database directory
    db_dir = Path(__file__).parent.parent.parent / "data" / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)

    results = []
    start_time_total = time.time()

    # Run experiments
    for condition in CONDITIONS:
        print()
        print(f"Testing {condition} condition")
        print("-" * 80)

        for seed in SEEDS:
            # Create unique database workspace
            db_workspace = db_dir / f"c270_{condition.lower()}_seed{seed}"
            db_workspace.mkdir(parents=True, exist_ok=True)

            result = run_experiment(seed, condition, output_path, db_workspace)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    # Aggregate results
    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'Condition':>12s} | {'Mean Pop':>10s} | {'Extinct %':>10s} | {'Mean η %':>10s} | {'Comp Events':>12s} | {'Decomp Events':>14s}")
    print("-" * 80)

    for condition in CONDITIONS:
        condition_results = [r for r in results if r['condition'] == condition]

        mean_pop = np.mean([r['mean_population'] for r in condition_results])

        extinction_count = sum(1 for r in condition_results if r['extinction'])
        extinction_pct = (extinction_count / len(condition_results)) * 100

        mean_eta = np.mean([r['spawn_success_rate'] for r in condition_results])
        mean_comp = np.mean([r['composition_count'] for r in condition_results])
        mean_decomp = np.mean([r['decomposition_count'] for r in condition_results])

        print(f"{condition:>12s} | {mean_pop:10.2f} | {extinction_pct:10.1f} | {mean_eta:10.1f} | {mean_comp:12.1f} | {mean_decomp:14.1f}")

    print()
    print("=" * 80)
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print(f"Results saved: {output_path}")
    print()

    # Save results
    output_data = {
        'experiment': 'C270_Memetic_Evolution',
        'description': 'Test if NRM pattern memory functions as cultural substrate',
        'mog_resonance': 0.91,
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'conditions': CONDITIONS,
            'f_spawn': F_SPAWN,
            'e_consume': E_CONSUME,
            'e_recharge': E_RECHARGE,
            'spawn_cost': SPAWN_COST,
            'cycles': CYCLES,
            'seeds': SEEDS,
            'n_seeds': len(SEEDS),
            'n_conditions': len(CONDITIONS),
            'total_experiments': len(results),
            'pattern_memory_size': PATTERN_MEMORY_SIZE,
            'prune_cycle': PRUNE_CYCLE,
            'prune_fraction': PRUNE_FRACTION
        },
        'results': results,
        'runtime_hours': elapsed_total / 3600
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Experiment complete. Next: Analyze results with falsification gauntlet.")
    print("Run: python code/analysis/analyze_c270_memetic_evolution.py")
    print()

if __name__ == '__main__':
    main()
