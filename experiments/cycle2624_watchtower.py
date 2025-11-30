#!/usr/bin/env python3
"""
Experiment: Cycle 2624 - The Watchtower
Goal: Persistent logging daemon for long-term system observation.
"""

import time
import json
import sys
import urllib.request
from pathlib import Path

def watch_loop():
    print("Cycle 2624: The Watchtower - Monitoring Service Started")
    log_file = Path("experiments/logs/system_history.jsonl")
    url = "http://localhost:8081/status"
    
    count = 0
    limit = 5 # Run for 5 ticks for this test
    
    while count < limit:
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                
                record = {
                    "timestamp": time.time(),
                    "agents_active": len(data.get("agents", [])),
                    "target_pos": data.get("target", {})
                }
                
                with open(log_file, "a") as f:
                    f.write(json.dumps(record) + "\n")
                    
                print(f"  [WATCH] Logged state at {record['timestamp']}")
                
        except Exception as e:
            print(f"  [WATCH] Error contacting API: {e}")
            # Don't crash, just retry
            
        time.sleep(1) # 1 sec interval
        count += 1

    print("Watchtower cycle complete.")

if __name__ == "__main__":
    watch_loop()
