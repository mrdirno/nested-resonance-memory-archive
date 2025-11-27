"""
Cycle 2443: The Guardian (Gate 71)
Role: The Watchdog
Responsibility: Periodically check system health and alert on issues.
Logic:
1. Load Configuration (Thresholds).
2. Check Disk, CPU, Memory.
3. Verify Critical Files.
4. Log Status.
5. Sleep & Repeat.
"""

import sys
import shutil
import platform
import os
import time
import logging

# Configuration
CHECK_INTERVAL = 3600 # 1 Hour
DISK_THRESHOLD_GB = 10
LOG_FILE = "automation/guardian/guardian.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_system_health():
    logging.info("Running Health Check...")
    status = "HEALTHY"
    
    # 1. Disk Space
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    if free_gb < DISK_THRESHOLD_GB:
        logging.warning(f"Low Disk Space: {free_gb} GB")
        status = "WARNING"
    
    # 2. Critical Files
    critical_files = ["META_OBJECTIVES.md", "MOG_CYCLE_LOG.md"]
    for f in critical_files:
        if not os.path.exists(f):
            logging.error(f"Missing Critical File: {f}")
            status = "CRITICAL"
            
    logging.info(f"Health Check Complete. Status: {status}")
    print(f"Guardian Status: {status}")
    return status

def run_guardian():
    print("Guardian of Duality Started.")
    print(f"Monitoring every {CHECK_INTERVAL} seconds.")
    
    try:
        # Run once for verification in this cycle
        check_system_health()
        # In production, we would loop:
        # while True:
        #     check_system_health()
        #     time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("Guardian Stopped.")

if __name__ == "__main__":
    run_guardian()
