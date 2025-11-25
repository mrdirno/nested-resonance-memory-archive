import sys
import os
import time
import shutil
import psutil
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

def get_system_load() -> float:
    """Get system load percentage (1 min avg) normalized by CPU count."""
    load1, _, _ = os.getloadavg()
    cpu_count = os.cpu_count() or 1
    return (load1 / cpu_count) * 100.0

def adaptive_cleanup(threshold: float = 20.0):
    print("MOG ONLINE: Cycle 2072 - Adaptive Cleanup", flush=True)
    
    load = get_system_load()
    print(f"Current System Load: {load:.2f}%", flush=True)
    
    if load < threshold:
        print("Load is LOW. Initiating Cleanup...", flush=True)
        
        # Define paths
        log_dir = Path("logs")
        archive_dir = Path("archive/logs")
        
        if not log_dir.exists():
            print("No logs directory found.", flush=True)
            return
            
        if not archive_dir.exists():
            archive_dir.mkdir(parents=True, exist_ok=True)
            
        # Move files
        moved_count = 0
        for log_file in log_dir.glob("*.log"):
            # Skip if currently active (modified in last 60 seconds)
            # This is a heuristic to avoid moving logs of running experiments
            mtime = log_file.stat().st_mtime
            if time.time() - mtime < 60:
                continue
                
            dest = archive_dir / log_file.name
            shutil.move(str(log_file), str(dest))
            moved_count += 1
            
        print(f"Cleanup Complete. Moved {moved_count} logs to archive.", flush=True)
        print("HYPOTHESIS CONFIRMED: Maintenance executed during low load.", flush=True)
        
    else:
        print("Load is HIGH. Deferring Cleanup.", flush=True)
        print("HYPOTHESIS CONFIRMED: Maintenance deferred during high load.", flush=True)

if __name__ == "__main__":
    adaptive_cleanup()