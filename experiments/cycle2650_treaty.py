#!/usr/bin/env python3
"""
Experiment: Cycle 2650 - The Treaty
Goal: Simulate a negotiation handshake (Offer/Accept).
"""

import sys
import time
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2649_embassy import EmbassyAgent, DiplomaticMessage
except ImportError:
    sys.exit(1)

def run_treaty_negotiation():
    print("Cycle 2650: The Treaty - Negotiation Simulation")
    
    helios = EmbassyAgent("HELIOS-ONE")
    terra = EmbassyAgent("TERRA-TWO")
    
    # 1. Helios sends Offer
    offer = {
        "sender_swarm_id": "HELIOS-ONE",
        "timestamp": time.time(),
        "type": "OFFER",
        "payload": {"resource": "compute", "amount": 100}
    }
    print("HELIOS -> TERRA: OFFER (100 Compute)")
    # Mock network transit
    import json
    terra.receive(json.dumps(offer))
    
    # 2. Terra evaluates and Accepts
    last_msg = terra.inbox[-1]
    if last_msg.type == "OFFER":
        accept = {
            "sender_swarm_id": "TERRA-TWO",
            "timestamp": time.time(),
            "type": "ACCEPT",
            "payload": {"ref_id": last_msg.timestamp}
        }
        print("TERRA -> HELIOS: ACCEPT")
        helios.receive(json.dumps(accept))
        
    # Verify Treaty
    if helios.inbox[-1].type == "ACCEPT":
        print("SUCCESS: Treaty signed.")
    else:
        print("FAILURE: Negotiation failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_treaty_negotiation()
