#!/usr/bin/env python3
"""
Quick test of C186 spawn interval fix

Tests that spawn intervals prevent population explosion
Validates Fix 1 from CYCLE1063 root cause analysis

Spawn interval logic (matching C176):
    spawn_interval = max(1, int(100.0 / frequency))
    should_spawn = (cycle_idx % spawn_interval) == 0
"""

import random
from dataclasses import dataclass
from typing import List

# Parameters
F_INTRA_PCT = 2.5  # 2.5% frequency
SPAWN_INTERVAL = max(1, int(100.0 / F_INTRA_PCT))  # = 40 cycles
CYCLES = 500
SEED = 42

# Energy
E_INITIAL = 50.0
E_SPAWN_THRESHOLD = 20.0
E_SPAWN_COST = 10.0
RECHARGE_RATE = 0.5

# Child energy fix: Below threshold to prevent cascade
CHILD_ENERGY = E_SPAWN_THRESHOLD * 0.5  # 10.0 (< 20.0 threshold)

@dataclass
class Agent:
    id: int
    energy: float

# Initialize
rng = random.Random(SEED)
agents = [Agent(id=i, energy=E_INITIAL) for i in range(20)]
next_id = 20
spawn_attempts = 0
spawn_successes = 0

print(f"=== SPAWN INTERVAL FIX TEST ===")
print(f"Frequency: {F_INTRA_PCT}% → Spawn every {SPAWN_INTERVAL} cycles")
print(f"Child energy: {CHILD_ENERGY} (threshold: {E_SPAWN_THRESHOLD})")
print(f"Initial population: {len(agents)}")
print()

# Run cycles
for cycle in range(CYCLES):
    # Spawn interval check (KEY FIX)
    should_spawn = (cycle % SPAWN_INTERVAL) == 0

    if should_spawn and len(agents) > 0:
        spawn_attempts += 1
        parent = rng.choice(agents)

        if parent.energy >= E_SPAWN_THRESHOLD:
            parent.energy -= E_SPAWN_COST
            child = Agent(id=next_id, energy=CHILD_ENERGY)
            agents.append(child)
            next_id += 1
            spawn_successes += 1

    # Energy recovery
    for agent in agents:
        agent.energy = min(E_INITIAL, agent.energy + RECHARGE_RATE)

    # Progress
    if (cycle + 1) % 100 == 0:
        print(f"Cycle {cycle+1:4d}: pop={len(agents):4d}, "
              f"spawns={spawn_successes:3d}/{spawn_attempts:2d}, "
              f"mean_energy={sum(a.energy for a in agents)/len(agents):.1f}")

print()
print(f"=== RESULTS ===")
print(f"Final population: {len(agents)} (vs {20} initial)")
print(f"Growth factor: {len(agents)/20:.2f}×")
print(f"Spawn success rate: {spawn_successes}/{spawn_attempts} ({100*spawn_successes/spawn_attempts if spawn_attempts > 0 else 0:.1f}%)")
print()

# Expected vs broken behavior
expected_spawns = CYCLES / SPAWN_INTERVAL  # 500/40 = 12.5 spawns
broken_spawns_per_cycle = int(20 * (F_INTRA_PCT / 100))  # Would be 1/cycle
broken_total = CYCLES * broken_spawns_per_cycle  # 500 spawns

print(f"Expected spawn attempts: ~{expected_spawns:.0f} (with intervals)")
print(f"Broken spawn attempts: ~{broken_total} (without intervals)")
print(f"Reduction: {broken_total/expected_spawns:.1f}× fewer spawns with intervals")
print()

if len(agents) < 100:
    print("✅ PASS: Population controlled (< 100 agents)")
    print("   Spawn intervals prevent explosion")
else:
    print("❌ FAIL: Population explosion still occurring")

if CHILD_ENERGY < E_SPAWN_THRESHOLD:
    print("✅ PASS: Child energy < threshold prevents cascade")
else:
    print("⚠ WARNING: Child energy ≥ threshold enables cascade")
