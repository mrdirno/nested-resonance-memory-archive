#!/usr/bin/env python3
"""
Experiment: Cycle 2643 - The Silence
Goal: Append a final termination signal to system logs.
"""

import time
from pathlib import Path

def silence_logs():
    print("Cycle 2643: The Silence - Terminating Logs")
    
    log_dir = Path("experiments/logs")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] NO CARRIER - SYSTEM HALT\n"
    
    count = 0
    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            try:
                with open(log_file, "a") as f:
                    f.write(message)
                count += 1
                print(f"  Silenced: {log_file.name}")
            except Exception as e:
                print(f"  Failed to silence {log_file.name}: {e}")
                
        # Also check jsonl
        for log_file in log_dir.glob("*.jsonl"):
            try:
                with open(log_file, "a") as f:
                    # JSONL compliant close
                    f.write(f'{{"event": "SYSTEM_HALT", "timestamp": {time.time()}}}\\n')
                count += 1
                print(f"  Silenced: {log_file.name}")
            except Exception as e:
                print(f"  Failed to silence {log_file.name}: {e}")

    if count > 0:
        print(f"SUCCESS: {count} logs terminated.")
    else:
        print("WARNING: No logs found to silence.")

if __name__ == "__main__":
    silence_logs()
