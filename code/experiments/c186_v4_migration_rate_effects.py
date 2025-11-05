#!/usr/bin/env python3
"""
Cycle 186 V4: Migration Rate Effects on Hierarchical Viability

Purpose: Test whether higher migration rates reduce α by enabling energy sharing
Background: C186 V1 (f_intra=2.5%, f_migrate=0.5%) → 0% Basin A (complete collapse)
            C186 V2 (f_intra=5.0%, f_migrate=0.5%) → 50-60% Basin A (viability restored)

Hypothesis: Increasing f_migrate reduces effective α by allowing cross-population
            energy sharing, reducing compartmentalization overhead.

Design:
    f_intra = 2.5% (FIXED at C186 V1 failure level)
    f_migrate = 0.5%, 2.5%, 5.0% (LOW, MEDIUM, HIGH migration rates)
    n_pop = 10 populations
    N_initial = 20 agents per population

Expected Outcomes:
    f_migrate = 0.5%: Basin A ≈ 0% (replicates C186 V1 baseline)
    f_migrate = 2.5%: Basin A ≈ 30-50% (partial viability via migration)
    f_migrate = 5.0%: Basin A ≈ 70-100% (migration overcomes compartmentalization)

Mechanism:
    Higher migration → more energy sharing across populations
    → reduced isolation → lower effective α
    → improved viability even at low f_intra

Quantitative Prediction:
    α_effective(f_migrate) = α_isolated × (1 - β·f_migrate)

    where β quantifies migration's effect on reducing compartmentalization

    cycles = 3000
    seeds = 10 per frequency (30 total experiments)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-05 (Cycle 1054)
License: GPL-3.0
"""

import sys
import json
import time
import random
import sqlite3
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from bridge_isolation_utils import clear_bridge_database
from transcendental_bridge import TranscendentalBridge

# Experimental parameters
F_INTRA = 0.025  # 2.5% fixed (C186 V1 failure level)
F_MIGRATE_VALUES = [0.005, 0.025, 0.050]  # 0.5%, 2.5%, 5.0%
N_POP = 10
N_INITIAL = 20
CYCLES = 3000
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]

# Energy parameters
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5

@dataclass
class Agent:
    """Individual fractal agent"""
    id: int
    population_id: int
    energy: float
    phase: float
    depth: int = 0
    compositions: int = 0

@dataclass
class Population:
    """Population container"""
    id: int
    agents: List[Agent]

    def mean_population(self) -> float:
        return float(len(self.agents))

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

class MetaPopulationSystem:
    """Meta-population system testing migration rate effects"""

    def __init__(self, seed: int, f_migrate: float, db_path: Path):
        self.seed = seed
        self.f_migrate = f_migrate
        self.random = random.Random(seed)
        self.bridge = TranscendentalBridge(db_path)

        self.populations: List[Population] = []
        self.next_agent_id = 0
        self.cycle_count = 0

        self.intra_spawns = 0
        self.spawn_failures = 0
        self.migrations = 0
        self.composition_events = 0

        self._initialize_populations()

    def _initialize_populations(self):
        """Create initial population structure"""
        for pop_id in range(N_POP):
            agents = []
            for _ in range(N_INITIAL):
                phase = self.random.uniform(0, 2 * 3.14159)
                agent = Agent(
                    id=self.next_agent_id,
                    population_id=pop_id,
                    energy=E_INITIAL,
                    phase=phase,
                    depth=0,
                    compositions=0
                )
                agents.append(agent)
                self.next_agent_id += 1

            pop = Population(id=pop_id, agents=agents)
            self.populations.append(pop)

    def step(self):
        """Execute one cycle"""
        self.cycle_count += 1
        self._intra_spawning()
        if self.f_migrate > 0:
            self._inter_migration()
        self._energy_recovery()
        self._composition_detection()

    def _intra_spawning(self):
        """Agents spawn within populations at F_INTRA rate"""
        for population in self.populations:
            if len(population.agents) == 0:
                continue

            n_attempts = int(len(population.agents) * F_INTRA)
            if self.random.random() < (len(population.agents) * F_INTRA - n_attempts):
                n_attempts += 1

            for _ in range(n_attempts):
                parent = self.random.choice(population.agents)

                if parent.energy >= E_SPAWN_THRESHOLD:
                    parent.energy -= E_SPAWN_COST
                    child_phase = parent.phase + self.random.gauss(0, 0.1)
                    child = Agent(
                        id=self.next_agent_id,
                        population_id=population.id,
                        energy=E_INITIAL * 0.5,
                        phase=child_phase,
                        depth=parent.depth + 1,
                        compositions=0
                    )
                    population.agents.append(child)
                    self.next_agent_id += 1
                    self.intra_spawns += 1
                else:
                    self.spawn_failures += 1

    def _inter_migration(self):
        """Migration between populations at f_migrate rate"""
        if len(self.populations) < 2:
            return

        total_agents = sum(len(pop.agents) for pop in self.populations)
        n_attempts = int(total_agents * self.f_migrate)
        if self.random.random() < (total_agents * self.f_migrate - n_attempts):
            n_attempts += 1

        for _ in range(n_attempts):
            source_pops = [p for p in self.populations if len(p.agents) > 0]
            if not source_pops:
                continue

            source_pop = self.random.choice(source_pops)

            if source_pop.total_energy() >= E_MIGRATE_THRESHOLD:
                migrant = self.random.choice(source_pop.agents)
                dest_pops = [p for p in self.populations if p.id != source_pop.id]
                if not dest_pops:
                    continue

                dest_pop = self.random.choice(dest_pops)
                source_pop.agents.remove(migrant)
                migrant.population_id = dest_pop.id
                dest_pop.agents.append(migrant)
                self.migrations += 1

    def _energy_recovery(self):
        """All agents recover energy"""
        for population in self.populations:
            for agent in population.agents:
                agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def _composition_detection(self):
        """Detect composition events"""
        for population in self.populations:
            if len(population.agents) < 2:
                continue

            for i, agent_i in enumerate(population.agents):
                for agent_j in population.agents[i+1:]:
                    phase_diff = abs(agent_i.phase - agent_j.phase)
                    if phase_diff < 0.1 or phase_diff > (2 * 3.14159 - 0.1):
                        agent_i.compositions += 1
                        agent_j.compositions += 1
                        self.composition_events += 1
                        agent_i.phase = (agent_i.phase + 0.05) % (2 * 3.14159)
                        agent_j.phase = (agent_j.phase + 0.05) % (2 * 3.14159)
                        break

    def get_statistics(self) -> Dict:
        """Compute statistics"""
        all_agents = []
        populations_data = []

        for pop in self.populations:
            all_agents.extend(pop.agents)
            populations_data.append({
                'pop_id': pop.id,
                'n_agents': len(pop.agents),
                'total_energy': pop.total_energy(),
                'mean_energy': pop.total_energy() / len(pop.agents) if pop.agents else 0.0
            })

        mean_population = len(all_agents) / N_POP if N_POP > 0 else 0.0
        basin = 'A' if mean_population > 2.5 else 'B'

        pop_sizes = [len(pop.agents) for pop in self.populations]
        if len(pop_sizes) > 1 and mean_population > 0:
            import statistics
            cv = (statistics.stdev(pop_sizes) / mean_population) * 100
        else:
            cv = 0.0

        total_spawn_attempts = self.intra_spawns + self.spawn_failures
        spawn_success_rate = (self.intra_spawns / total_spawn_attempts * 100) if total_spawn_attempts > 0 else 0.0

        return {
            'cycle': self.cycle_count,
            'total_agents': len(all_agents),
            'mean_population': mean_population,
            'basin': basin,
            'cv_percent': cv,
            'intra_spawns': self.intra_spawns,
            'spawn_failures': self.spawn_failures,
            'spawn_success_rate': spawn_success_rate,
            'migrations': self.migrations,
            'compositions': self.composition_events,
            'populations': populations_data
        }

def run_experiment(seed: int, f_migrate: float, output_path: Path, db_path: Path) -> Dict:
    """Run single experiment"""
    freq_idx = F_MIGRATE_VALUES.index(f_migrate)
    seed_idx = SEEDS.index(seed)
    exp_num = freq_idx * len(SEEDS) + seed_idx + 1
    total_exps = len(F_MIGRATE_VALUES) * len(SEEDS)

    print(f"  [{exp_num:2d}/{total_exps}] f_migrate={f_migrate*100:4.1f}%, Seed {seed:3d}: ", end='', flush=True)

    clear_bridge_database(db_path)
    system = MetaPopulationSystem(seed, f_migrate, db_path)

    start_time = time.time()
    for cycle in range(CYCLES):
        system.step()

    final_stats = system.get_statistics()
    elapsed_total = time.time() - start_time

    print(f"Basin {final_stats['basin']} | "
          f"Pop: {final_stats['mean_population']:4.1f} | "
          f"CV: {final_stats['cv_percent']:5.1f}% | "
          f"Migrations: {final_stats['migrations']:4d} | "
          f"{elapsed_total:4.0f}s")

    final_stats['seed'] = seed
    final_stats['f_intra'] = F_INTRA
    final_stats['f_migrate'] = f_migrate
    final_stats['elapsed_seconds'] = elapsed_total

    return final_stats

def main():
    """Execute C186 V4 migration rate effects experiments"""

    print("=" * 80)
    print("CYCLE 186 V4: MIGRATION RATE EFFECTS ON HIERARCHICAL VIABILITY")
    print("=" * 80)
    print()
    print("Purpose: Test if higher migration reduces α via energy sharing")
    print("Background: C186 V1 (f_intra=2.5%, f_migrate=0.5%) → 0% Basin A")
    print("            C186 V2 (f_intra=5.0%, f_migrate=0.5%) → 50-60% Basin A")
    print()
    print(f"Experimental Design:")
    print(f"  f_intra = {F_INTRA*100:.1f}% (FIXED at C186 V1 failure level)")
    print(f"  f_migrate = 0.5%, 2.5%, 5.0% (LOW, MEDIUM, HIGH)")
    print(f"  n_pop = {N_POP} populations")
    print(f"  N_initial = {N_INITIAL} agents per population")
    print()
    print(f"Experimental Parameters:")
    print(f"  Seeds per migration rate: n={len(SEEDS)}")
    print(f"  Cycles per seed: {CYCLES}")
    print(f"  Total experiments: {len(F_MIGRATE_VALUES) * len(SEEDS)}")
    print(f"  Expected runtime: ~{len(F_MIGRATE_VALUES) * len(SEEDS) * 0.04:.1f} hours")
    print()
    print(f"Hypothesis:")
    print(f"  f_migrate = 0.5%: Basin A ≈ 0% (replicates C186 V1)")
    print(f"  f_migrate = 2.5%: Basin A ≈ 30-50% (partial viability)")
    print(f"  f_migrate = 5.0%: Basin A ≈ 70-100% (migration overcomes compartmentalization)")
    print()

    output_dir = Path(__file__).parent.parent.parent / "experiments" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "c186_v4_migration_rate_effects.json"

    db_path = Path(__file__).parent.parent / "bridge" / "bridge.db"

    results = []
    start_time_total = time.time()

    for f_migrate in F_MIGRATE_VALUES:
        print()
        print(f"Testing f_migrate = {f_migrate*100:.2f}%")
        print("-" * 80)

        for seed in SEEDS:
            result = run_experiment(seed, f_migrate, output_path, db_path)
            results.append(result)

    elapsed_total = time.time() - start_time_total

    print()
    print("=" * 80)
    print("AGGREGATE RESULTS")
    print("=" * 80)
    print()
    print(f"{'f_migrate':>10s} | {'Basin A %':>10s} | {'Mean Pop':>10s} | {'CV %':>8s} | {'Migrations':>12s}")
    print("-" * 80)

    rate_aggregates = []
    for f_migrate in F_MIGRATE_VALUES:
        rate_results = [r for r in results if abs(r['f_migrate'] - f_migrate) < 0.0001]

        basin_a_count = sum(1 for r in rate_results if r['basin'] == 'A')
        basin_a_pct = (basin_a_count / len(rate_results)) * 100

        mean_pops = [r['mean_population'] for r in rate_results]
        mean_pop_avg = sum(mean_pops) / len(mean_pops)

        cvs = [r['cv_percent'] for r in rate_results]
        cv_avg = sum(cvs) / len(cvs)

        migrations = [r['migrations'] for r in rate_results]
        migrations_avg = sum(migrations) / len(migrations)

        rate_aggregates.append({
            'f_migrate': f_migrate,
            'basin_a_pct': basin_a_pct,
            'mean_pop_avg': mean_pop_avg,
            'cv_avg': cv_avg,
            'migrations_avg': migrations_avg
        })

        print(f"{f_migrate*100:9.1f}% | {basin_a_pct:9.1f}% | {mean_pop_avg:10.2f} | {cv_avg:7.1f}% | {migrations_avg:12.1f}")

    print()
    print(f"Total runtime: {elapsed_total/3600:.2f} hours")
    print()

    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()

    baseline = rate_aggregates[0]['basin_a_pct']  # f_migrate = 0.5%
    medium = rate_aggregates[1]['basin_a_pct']    # f_migrate = 2.5%
    high = rate_aggregates[2]['basin_a_pct']      # f_migrate = 5.0%

    if abs(baseline) < 10:
        print(f"✓ Control validated: f_migrate=0.5% → {baseline:.1f}% Basin A (matches C186 V1)")
    else:
        print(f"⚠ Control mismatch: f_migrate=0.5% → {baseline:.1f}% Basin A (expected ~0%)")

    if high > medium > baseline:
        print(f"✓ Hypothesis SUPPORTED: Basin A increases with f_migrate")
        print(f"  Migration reduces compartmentalization overhead")
        print(f"  {baseline:.1f}% → {medium:.1f}% → {high:.1f}% Basin A")
    else:
        print(f"⚠ Hypothesis NOT SUPPORTED: Basin A does not increase monotonically")

    print()

    output_data = {
        'metadata': {
            'experiment': 'C186_V4_MIGRATION_RATE_EFFECTS',
            'date': datetime.now().isoformat(),
            'purpose': 'Test if higher migration reduces α via energy sharing',
            'f_intra': F_INTRA,
            'f_migrate_values': F_MIGRATE_VALUES,
            'n_pop': N_POP,
            'n_initial': N_INITIAL,
            'cycles': CYCLES,
            'seeds': SEEDS,
        },
        'rate_aggregates': rate_aggregates,
        'individual_results': results
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("C186 V4 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
