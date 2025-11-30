#!/usr/bin/env python3
"""
Experiment: Cycle 2648 - The Contract
Goal: Define a JSON schema for inter-swarm communication and trade.
"""

import json
from pathlib import Path

CONTRACT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Inter-Swarm Communication Protocol",
    "type": "object",
    "properties": {
        "sender_swarm_id": {"type": "string"},
        "timestamp": {"type": "number"},
        "type": {"type": "string", "enum": ["GREETING", "OFFER", "ACCEPT", "REJECT"]},
        "payload": {"type": "object"}
    },
    "required": ["sender_swarm_id", "timestamp", "type", "payload"]
}

def define_contract():
    print("Cycle 2648: The Contract - Defining Protocol")
    
    schema_path = Path("experiments/inter_swarm_contract.json")
    with open(schema_path, "w") as f:
        json.dump(CONTRACT_SCHEMA, f, indent=2)
        
    print(f"SUCCESS: Contract schema defined at {schema_path}")
    print(json.dumps(CONTRACT_SCHEMA, indent=2))

if __name__ == "__main__":
    define_contract()
