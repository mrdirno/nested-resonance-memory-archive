#!/usr/bin/env python3
"""
Experiment: Cycle 2625 - The Archive
Goal: Create a full snapshot of the agent state for cold storage.
"""

import urllib.request
import json
import time
import gzip
from pathlib import Path

def create_snapshot():
    print("Cycle 2625: The Archive - Snapshotting...")
    url = "http://localhost:8081/status"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"experiments/logs/snapshot_{timestamp}.json.gz"
            
            with gzip.open(filename, "wt", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            print(f"SUCCESS: Snapshot saved to {filename}")
            
    except Exception as e:
        print(f"FAILURE: Could not snapshot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_snapshot()
