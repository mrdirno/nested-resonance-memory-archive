#!/usr/bin/env python3
"""
Minimal reproduction test for C187 hang

Purpose: Run actual NetworkedPopulationSystem to find hang
"""

import sys
import time
from pathlib import Path

print("Step 0: Script started", flush=True)

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

print("Step 1: Importing c187_network_structure...", flush=True)
from c187_network_structure import NetworkedPopulationSystem, clear_bridge_database

print("Step 2: Imports complete, starting minimal test...", flush=True)
print()

# Test parameters
SEED = 42
TOPOLOGY = 'scale_free'
CYCLES_TO_RUN = 3000  # Full experiment length

# Setup database path
db_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/databases/test_c187_minimal")
db_path.mkdir(parents=True, exist_ok=True)
bridge_db = db_path / "bridge.db"
clear_bridge_database(bridge_db)

print(f"Creating NetworkedPopulationSystem (seed={SEED}, topology={TOPOLOGY})...")
start_init = time.time()
try:
    system = NetworkedPopulationSystem(SEED, TOPOLOGY, db_path)
    elapsed_init = time.time() - start_init
    print(f"✓ System created successfully ({elapsed_init:.3f}s)")
    print(f"  Initial agents: {len(system.agents)}")
    print(f"  Network nodes: {system.network.number_of_nodes()}")
    print(f"  Network edges: {system.network.number_of_edges()}")
except Exception as e:
    print(f"✗ System creation FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print(f"Running {CYCLES_TO_RUN} simulation cycles...")
start_sim = time.time()
for cycle in range(CYCLES_TO_RUN):
    try:
        system.step()
        # Print progress every 500 cycles
        if (cycle + 1) % 500 == 0:
            elapsed = time.time() - start_sim
            rate = (cycle + 1) / elapsed
            print(f"  Cycle {cycle+1}/{CYCLES_TO_RUN}: "
                  f"{len(system.agents)} agents, "
                  f"{rate:.1f} cycles/s")
    except Exception as e:
        print(f"✗ Cycle {cycle+1} FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
elapsed_sim = time.time() - start_sim
print(f"✓ Completed {CYCLES_TO_RUN} cycles in {elapsed_sim:.1f}s ({CYCLES_TO_RUN/elapsed_sim:.1f} cycles/s)")

print()
print("✓ ALL CYCLES COMPLETED SUCCESSFULLY")
print()
print("Final statistics:")
stats = system.get_final_statistics()
print(f"  Basin: {stats['basin']}")
print(f"  Mean population: {stats['mean_population']:.1f}")
print(f"  Spawn success rate: {stats['spawn_success_rate']:.1f}%")
