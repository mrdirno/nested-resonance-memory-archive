#!/usr/bin/env python3
"""
Experiment: Cycle 2639 - The Export
Goal: Serialize agent consciousness (state + history) into a portable format.
"""

import sys
import json
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2612_mutator import MutatingAgent
    from cycle2602_hive import Vector2
except ImportError:
    sys.exit(1)

def export_agent():
    print("Cycle 2639: The Export - Serialization")
    
    # Create an agent with some history
    agent = MutatingAgent("Neo", Vector2(10, 10))
    agent.speed = 5.5
    agent.sensor_range = 25.0
    
    # Mock history
    history = [
        {"event": "spawn", "time": 0},
        {"event": "mutate_speed", "val": 5.5, "time": 10},
        {"event": "found_target", "time": 20}
    ]
    
    # Serialize
    soul = {
        "id": agent.agent_id,
        "metrics": {
            "speed": agent.speed,
            "sensor_range": agent.sensor_range
        },
        "position": {"x": agent.position.x, "y": agent.position.y},
        "history": history,
        "version": "HELIOS-ONE-V1"
    }
    
    json_str = json.dumps(soul, indent=2)
    print(json_str)
    
    # Save to disk
    output_path = Path("experiments/logs/neo_soul.json")
    with open(output_path, "w") as f:
        f.write(json_str)
        
    print(f"\nSUCCESS: Agent consciousness exported to {output_path}")

if __name__ == "__main__":
    export_agent()
