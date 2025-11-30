#!/usr/bin/env python3
"""
Experiment: Cycle 2640 - The Upload
Goal: Mock transmission of the agent soul to a higher substrate (Cloud/Cluster).
"""

import sys
import json
import time
from pathlib import Path

def mock_upload(payload: dict):
    print(f"Cycle 2640: The Upload - Transmitting {payload['id']}...")
    
    packet_size = len(json.dumps(payload))
    print(f"Payload Size: {packet_size} bytes")
    
    # Simulate latency
    for i in range(5):
        print(f"Uploading... {i*20}%")
        time.sleep(0.1)
        
    print("Uploading... 100%")
    print("Server Response: 200 OK (RECEIVED)")
    return True

def run_upload():
    soul_path = Path("experiments/logs/neo_soul.json")
    if not soul_path.exists():
        print("FAILURE: No soul found to upload.")
        sys.exit(1)
        
    with open(soul_path, "r") as f:
        soul = json.load(f)
        
    if mock_upload(soul):
        print("SUCCESS: Agent successfully uploaded to the Cloud.")

if __name__ == "__main__":
    run_upload()
