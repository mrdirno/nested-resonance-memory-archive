#!/usr/bin/env python3
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)  # Line buffering
sys.stderr = open(sys.stderr.fileno(), mode='w', buffering=1)

print("STEP A: Starting")
import time
print("STEP B: Imported time")
from pathlib import Path
print("STEP C: Imported Path")

sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
print("STEP D: Set paths")

from c187_network_structure import NetworkedPopulationSystem, clear_bridge_database
print("STEP E: Imported NetworkedPopulationSystem")

SEED = 42
TOPOLOGY = 'scale_free'
db_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/databases/test_simple")
db_path.mkdir(parents=True, exist_ok=True)
print("STEP F: Created db path")

bridge_db = db_path / "bridge.db"
clear_bridge_database(bridge_db)
print("STEP G: Cleared bridge database")

print("STEP H: Creating NetworkedPopulationSystem...")
system = NetworkedPopulationSystem(SEED, TOPOLOGY, db_path)
print("STEP I: System created!")

print("SUCCESS")
