#!/usr/bin/env python3
"""
Test C186 V1 Simple with SHORT cycles (100 instead of 3000)
To determine if hang is iteration-count related
"""

import sys
import json
import time
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

# Experimental parameters - REDUCED CYCLES
F_INTRA = 0.025
F_MIGRATE = 0.005
N_POP = 10
N_INITIAL = 20
CYCLES = 100  # ← REDUCED from 3000
SEEDS = [42, 123]  # Only 2 seeds for quick test

# Energy parameters
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5

@dataclass
class Agent:
    id: int
    population_id: int
    energy: float

@dataclass
class Population:
    id: int
    agents: List[Agent]

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

class HierarchicalSystem:
    def __init__(self, seed: int):
        self.seed = seed
        self.random = random.Random(seed)
        self.populations: List[Population] = []
        self.next_agent_id = 0
        self.cycle_count = 0
        self.intra_spawns = 0
        self.spawn_failures = 0
        self.migrations = 0
        self._initialize_populations()

    def _initialize_populations(self):
        for pop_id in range(N_POP):
            agents = []
            for _ in range(N_INITIAL):
                agent = Agent(
                    id=self.next_agent_id,
                    population_id=pop_id,
                    energy=E_INITIAL
                )
                agents.append(agent)
                self.next_agent_id += 1
            pop = Population(id=pop_id, agents=agents)
            self.populations.append(pop)

    def step(self):
        self.cycle_count += 1
        self._intra_spawning()
        self._inter_migration()
        self._energy_recovery()

    def _intra_spawning(self):
        for population in self.populations:
            if len(population.agents) == 0:
                continue
            n_attempts = max(1, int(len(population.agents) * F_INTRA))
            for _ in range(n_attempts):
                if len(population.agents) == 0:
                    break
                parent = self.random.choice(population.agents)
                if parent.energy >= E_SPAWN_THRESHOLD:
                    parent.energy -= E_SPAWN_COST
                    child = Agent(
                        id=self.next_agent_id,
                        population_id=population.id,
                        energy=E_INITIAL * 0.5
                    )
                    population.agents.append(child)
                    self.next_agent_id += 1
                    self.intra_spawns += 1
                else:
                    self.spawn_failures += 1

    def _inter_migration(self):
        total_agents = sum(len(pop.agents) for pop in self.populations)
        if total_agents == 0:
            return
        n_attempts = max(1, int(total_agents * F_MIGRATE))
        for _ in range(n_attempts):
            non_empty_pops = [p for p in self.populations if len(p.agents) > 0]
            if len(non_empty_pops) < 2:
                break
            source_pop = self.random.choice(non_empty_pops)
            dest_pops = [p for p in self.populations if p.id != source_pop.id]
            if not dest_pops:
                break
            if source_pop.total_energy() >= E_MIGRATE_THRESHOLD:
                migrant = self.random.choice(source_pop.agents)
                dest_pop = self.random.choice(dest_pops)
                source_pop.agents.remove(migrant)
                migrant.population_id = dest_pop.id
                dest_pop.agents.append(migrant)
                self.migrations += 1

    def _energy_recovery(self):
        for population in self.populations:
            for agent in population.agents:
                agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    def get_metrics(self) -> Dict:
        all_agents = []
        for pop in self.populations:
            all_agents.extend(pop.agents)
        if len(all_agents) == 0:
            return {
                'total_population': 0,
                'mean_energy': 0.0,
                'active_populations': 0
            }
        active_pops = sum(1 for pop in self.populations if len(pop.agents) > 0)
        return {
            'total_population': len(all_agents),
            'mean_energy': sum(a.energy for a in all_agents) / len(all_agents),
            'active_populations': active_pops
        }

def run_single_experiment(seed: int) -> Dict:
    print(f"  → Creating system (seed={seed})...", flush=True)
    system = HierarchicalSystem(seed)
    print(f"  → System created, starting {CYCLES} cycles...", flush=True)

    start_time = time.time()

    for cycle in range(CYCLES):
        system.step()
        if (cycle + 1) % 50 == 0:  # Progress every 50 cycles
            elapsed = time.time() - start_time
            metrics = system.get_metrics()
            print(f"  → Seed {seed:3d}, Cycle {cycle+1:4d}: "
                  f"pop={metrics['total_population']:3d}, "
                  f"energy={metrics['mean_energy']:.1f}, "
                  f"[{elapsed:.2f}s]", flush=True)

    final_metrics = system.get_metrics()
    elapsed = time.time() - start_time
    mean_pop = final_metrics['total_population'] / N_POP
    basin = 'A' if mean_pop > 2.5 else 'B'

    result = {
        'seed': seed,
        'basin': basin,
        'mean_population': mean_pop,
        'total_population': final_metrics['total_population'],
        'mean_energy': final_metrics['mean_energy'],
        'runtime_seconds': elapsed
    }

    return result

def main():
    print("=" * 80, flush=True)
    print("C186 V1 SHORT CYCLE TEST (100 cycles, 2 seeds)", flush=True)
    print("=" * 80, flush=True)
    print(flush=True)

    results = []
    for i, seed in enumerate(SEEDS):
        print(f"[{i+1}/{len(SEEDS)}] Running seed {seed}...", flush=True)
        result = run_single_experiment(seed)
        results.append(result)
        print(f"  → COMPLETE: Basin {result['basin']}, mean_pop={result['mean_population']:.2f}, "
              f"time={result['runtime_seconds']:.2f}s", flush=True)
        print(flush=True)

    print("=" * 80, flush=True)
    print("TEST COMPLETE - All seeds finished successfully", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    main()
