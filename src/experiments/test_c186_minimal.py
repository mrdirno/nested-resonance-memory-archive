#!/usr/bin/env python3
"""
Minimal test to isolate C186 V1 Simple hang location

Tests incremental initialization to find where hang occurs
"""

import sys
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List

print("=== C186 MINIMAL TEST START ===", flush=True)

# Parameters (from C186 V1 Simple)
F_INTRA = 0.025
F_MIGRATE = 0.005
N_POP = 10
N_INITIAL = 20
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
E_MIGRATE_THRESHOLD = 15.0
RECHARGE_RATE = 0.5

print("Parameters loaded", flush=True)

@dataclass
class Agent:
    id: int
    population_id: int
    energy: float

print("Agent class defined", flush=True)

@dataclass
class Population:
    id: int
    agents: List[Agent]

    def total_energy(self) -> float:
        return sum(a.energy for a in self.agents)

print("Population class defined", flush=True)

# Test 1: Random initialization
seed = 42
print(f"Test 1: Creating Random({seed})...", flush=True)
rng = random.Random(seed)
print(f"Test 1: Random created, testing choice...", flush=True)
test_list = [1, 2, 3, 4, 5]
choice = rng.choice(test_list)
print(f"Test 1: Random.choice works, got {choice}", flush=True)

# Test 2: Create agents
print("Test 2: Creating agents...", flush=True)
agents = []
for i in range(N_INITIAL):
    agent = Agent(id=i, population_id=0, energy=E_INITIAL)
    agents.append(agent)
print(f"Test 2: Created {len(agents)} agents", flush=True)

# Test 3: Create population
print("Test 3: Creating population...", flush=True)
pop = Population(id=0, agents=agents)
print(f"Test 3: Population created with {len(pop.agents)} agents", flush=True)

# Test 4: Create multiple populations
print("Test 4: Creating 10 populations...", flush=True)
populations = []
agent_id = 0
for pop_id in range(N_POP):
    pop_agents = []
    for _ in range(N_INITIAL):
        agent = Agent(id=agent_id, population_id=pop_id, energy=E_INITIAL)
        pop_agents.append(agent)
        agent_id += 1
    pop = Population(id=pop_id, agents=pop_agents)
    populations.append(pop)
print(f"Test 4: Created {len(populations)} populations", flush=True)

# Test 5: Spawn logic
print("Test 5: Testing spawn logic...", flush=True)
test_pop = populations[0]
n_attempts = max(1, int(len(test_pop.agents) * F_INTRA))
print(f"Test 5: n_attempts = {n_attempts}", flush=True)

for i in range(n_attempts):
    if len(test_pop.agents) == 0:
        break
    parent = rng.choice(test_pop.agents)
    print(f"Test 5: Spawn attempt {i+1}/{n_attempts}, parent={parent.id}, energy={parent.energy:.1f}", flush=True)

    if parent.energy >= E_SPAWN_THRESHOLD:
        parent.energy -= E_SPAWN_COST
        child = Agent(id=agent_id, population_id=test_pop.id, energy=E_INITIAL * 0.5)
        test_pop.agents.append(child)
        agent_id += 1
        print(f"Test 5: Spawn SUCCESS, child_id={child.id}", flush=True)
    else:
        print(f"Test 5: Spawn FAILED (insufficient energy)", flush=True)

print(f"Test 5: Final population size: {len(test_pop.agents)}", flush=True)

# Test 6: Migration logic
print("Test 6: Testing migration logic...", flush=True)
total_agents = sum(len(p.agents) for p in populations)
print(f"Test 6: total_agents = {total_agents}", flush=True)

n_attempts = max(1, int(total_agents * F_MIGRATE))
print(f"Test 6: migration n_attempts = {n_attempts}", flush=True)

for i in range(min(3, n_attempts)):  # Only test 3 migrations
    non_empty_pops = [p for p in populations if len(p.agents) > 0]
    if len(non_empty_pops) < 2:
        print(f"Test 6: Not enough populations for migration", flush=True)
        break

    source_pop = rng.choice(non_empty_pops)
    dest_pops = [p for p in populations if p.id != source_pop.id]

    print(f"Test 6: Migration attempt {i+1}, source={source_pop.id}, dest options={len(dest_pops)}", flush=True)

    if source_pop.total_energy() >= E_MIGRATE_THRESHOLD:
        migrant = rng.choice(source_pop.agents)
        dest_pop = rng.choice(dest_pops)

        source_pop.agents.remove(migrant)
        migrant.population_id = dest_pop.id
        dest_pop.agents.append(migrant)
        print(f"Test 6: Migration SUCCESS, {source_pop.id} -> {dest_pop.id}", flush=True)
    else:
        print(f"Test 6: Migration FAILED (insufficient energy)", flush=True)

print("=== ALL TESTS PASSED ===", flush=True)
print("C186 V1 Simple initialization logic appears functional", flush=True)
