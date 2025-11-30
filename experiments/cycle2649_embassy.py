#!/usr/bin/env python3
"""
Experiment: Cycle 2649 - The Embassy
Goal: Establish a diplomatic channel agent that listens for foreign messages.
"""

import sys
import json
import time
from dataclasses import dataclass, asdict

@dataclass
class DiplomaticMessage:
    sender_swarm_id: str
    timestamp: float
    type: str
    payload: dict

class EmbassyAgent:
    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.inbox = []

    def receive(self, msg_json: str):
        try:
            data = json.loads(msg_json)
            # Simple validation against "contract" logic
            if "sender_swarm_id" in data and "type" in data:
                msg = DiplomaticMessage(**data)
                self.inbox.append(msg)
                print(f"[{self.swarm_id} EMBASSY] Received {msg.type} from {msg.sender_swarm_id}")
                return True
            else:
                print(f"[{self.swarm_id} EMBASSY] Invalid message format.")
                return False
        except Exception as e:
            print(f"[{self.swarm_id} EMBASSY] Decoding error: {e}")
            return False

def run_embassy_test():
    print("Cycle 2649: The Embassy - Channel Test")
    
    embassy = EmbassyAgent("HELIOS-PRIME")
    
    # Simulate foreign message
    foreign_msg = {
        "sender_swarm_id": "LUNA-CORE",
        "timestamp": time.time(),
        "type": "GREETING",
        "payload": {"intent": "peace"}
    }
    
    if embassy.receive(json.dumps(foreign_msg)):
        print("SUCCESS: Diplomatic channel active.")
    else:
        print("FAILURE: Message rejected.")
        sys.exit(1)

if __name__ == "__main__":
    run_embassy_test()
