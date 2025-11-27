#!/usr/bin/env python3
import time
import subprocess
import sys
import os
from datetime import datetime

import platform

def check_identity():
    if platform.system() != "Linux":
        print("⛔ ERROR: Guardian Daemon must run on GUARDIAN NODE (Ubuntu).")
        print("    Current Node: PILOT (macOS)")
        sys.exit(1)

def guardian_loop(interval=3600):
    check_identity()
    print(f"GUARDIAN DAEMON ONLINE. Monitoring every {interval} seconds.")
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts", "system_health_check.py")
    
    if not os.path.exists(script_path):
        print(f"CRITICAL: Health check script not found at {script_path}")
        sys.exit(1)

    try:
        while True:
            print(f"\n[GUARDIAN] Running Health Check at {datetime.now().isoformat()}...")
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print(f"[GUARDIAN] ERROR: {result.stderr}")
            
            if result.returncode != 0:
                print(f"[GUARDIAN] WARNING: Health check failed with code {result.returncode}")
            else:
                print("[GUARDIAN] Health check passed.")

            print(f"[GUARDIAN] Sleeping for {interval} seconds...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n[GUARDIAN] Daemon stopping...")
        sys.exit(0)

if __name__ == "__main__":
    # Default to 60 seconds for demonstration if no arg provided
    interval = 60
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            pass
    guardian_loop(interval)
