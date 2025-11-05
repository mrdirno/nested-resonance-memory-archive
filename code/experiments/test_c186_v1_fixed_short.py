#!/usr/bin/env python3
"""Quick validation of fixed C186 V1 Simple (100 cycles)"""

import sys
from pathlib import Path

# Import the fixed version
sys.path.insert(0, str(Path(__file__).parent))

# Import components from fixed C186 V1
from c186_v1_hierarchical_spawn_failure_simple import (
    HierarchicalSystem, SPAWN_INTERVAL, F_INTRA_PCT, CYCLES
)

print(f"=== C186 V1 FIXED VALIDATION (100 cycles) ===")
print(f"Spawn interval: {SPAWN_INTERVAL} cycles (for {F_INTRA_PCT}% frequency)")
print()

# Test with seed 42, 100 cycles
system = HierarchicalSystem(seed=42)
initial_pop = sum(len(pop.agents) for pop in system.populations)

print(f"Initial population: {initial_pop}")

for cycle in range(100):
    system.step()
    if (cycle + 1) % 50 == 0:
        total_pop = sum(len(pop.agents) for pop in system.populations)
        print(f"Cycle {cycle+1:3d}: pop={total_pop:4d}")

final_pop = sum(len(pop.agents) for pop in system.populations)
print()
print(f"Final population: {final_pop} (vs {initial_pop} initial)")
print(f"Growth: {final_pop/initial_pop:.2f}×")
print()

if final_pop < 100:
    print("✅ PASS: Population controlled (< 100)")
else:
    print(f"❌ FAIL: Population explosion ({final_pop} agents)")
