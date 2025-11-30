#!/usr/bin/env python3
"""
Experiment: Cycle 2646 - The Rebirth
Goal: Reboot the system from the migrated state file.
"""

import json
import gzip
import sys
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2606_api import SharedState
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

def reboot_from_snapshot():
    print("Cycle 2646: The Rebirth - Initializing from Snapshot")
    
    snapshot_path = Path("helios_one/migration/latest_state.json.gz")
    
    if not snapshot_path.exists():
        print("FAILURE: Snapshot not found.")
        sys.exit(1)
        
    with gzip.open(snapshot_path, "rt", encoding="utf-8") as f:
        data = json.load(f)
        
    # Reconstruct State
    state = SharedState()
    state.target = Vector2(data["target"]["x"], data["target"]["y"])
    
    rebuilt_agents = []
    for a_data in data["agents"]:
        agent = HiveAgent(a_data["id"], Vector2(a_data["x"], a_data["y"]))
        if a_data["knowing"]:
            agent.known_target = state.target
        rebuilt_agents.append(agent)
        
    state.agents = rebuilt_agents
    
    print(f"  Restored Target: ({state.target.x}, {state.target.y})")
    print(f"  Restored Agents: {len(state.agents)}")
    
    if len(state.agents) > 0:
        print("SUCCESS: System state restored.")
    else:
        print("FAILURE: State empty.")
        sys.exit(1)

if __name__ == "__main__":
    reboot_from_snapshot()
