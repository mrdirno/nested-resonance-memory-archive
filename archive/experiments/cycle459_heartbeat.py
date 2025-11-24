
"""
Cycle 459: The Heartbeat
Objective: Maintain perpetual system monitoring during Deep Stasis.
Mechanism: Periodic Vital Checks (Disk, Memory, Git).
"""

import os
import time
import psutil
import subprocess
from datetime import datetime

HEARTBEAT_LOG = "heartbeat.log"

def get_git_status():
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode == 0:
            if not result.stdout.strip():
                return "CLEAN"
            else:
                return "DIRTY"
        else:
            return "ERROR"
    except Exception as e:
        return f"ERROR: {e}"

def log_pulse():
    timestamp = datetime.now().isoformat()
    
    # System Vitals
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Repo Health
    git_status = get_git_status()
    
    pulse_data = (
        f"[{timestamp}] PULSE | "
        f"CPU: {cpu_percent}% | "
        f"MEM: {memory.percent}% | "
        f"DISK: {disk.percent}% | "
        f"REPO: {git_status}"
    )
    
    print(pulse_data)
    
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(pulse_data + "\n")

def run_heartbeat(duration_sec=10, interval_sec=2):
    print(f"--- CYCLE 459: THE HEARTBEAT (Monitoring for {duration_sec}s) ---")
    start_time = time.time()
    
    while (time.time() - start_time) < duration_sec:
        log_pulse()
        time.sleep(interval_sec)
        
    print("--- HEARTBEAT COMPLETE ---")

if __name__ == "__main__":
    run_heartbeat()
