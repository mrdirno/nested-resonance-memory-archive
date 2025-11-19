#!/usr/bin/env python3
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode='w', buffering=1)

import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from c187_network_structure import NetworkedPopulationSystem, clear_bridge_database

SEED = 42
TOPOLOGY = 'scale_free'
CYCLES = 100

db_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/databases/test_step_debug")
db_path.mkdir(parents=True, exist_ok=True)
bridge_db = db_path / "bridge.db"
clear_bridge_database(bridge_db)

print("Creating system...", flush=True)
system = NetworkedPopulationSystem(SEED, TOPOLOGY, db_path)
print(f"System created. Agents: {len(system.agents)}", flush=True)

for cycle in range(CYCLES):
    if cycle % 10 == 0:
        print(f"BEFORE cycle {cycle}", flush=True)
    start = time.time()
    system.step()
    elapsed = time.time() - start
    if cycle % 10 == 0:
        print(f"AFTER cycle {cycle}: {elapsed*1000:.1f}ms, {len(system.agents)} agents", flush=True)

print("ALL CYCLES COMPLETE", flush=True)
