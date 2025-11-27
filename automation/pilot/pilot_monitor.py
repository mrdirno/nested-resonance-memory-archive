"""
Cycle 2443: Pilot Monitor (Gate 71)
Role: The Pilot Monitor
Responsibility: Monitor Pilot Health on macOS.
Logic:
1. Verify Identity (macOS).
2. Run Heartbeat.
3. Check for new directives.
"""

import sys
import platform
import time
import os

def check_identity():
    if platform.system() != "Darwin":
        print("⛔ ERROR: Pilot Monitor must run on PILOT NODE (macOS).")
        print(f"    Current Node: {platform.system()}")
        sys.exit(1)

def pilot_loop(interval=3600):
    check_identity()
    print(f"PILOT MONITOR ONLINE. Monitoring every {interval} seconds.")
    
    try:
        while True:
            print(f"\n[PILOT] Heartbeat...")
            # In a real scenario, we would check for incoming messages from Guardian
            # For now, we just pulse.
            print("[PILOT] System Nominal.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[PILOT] Monitor stopping...")
        sys.exit(0)

if __name__ == "__main__":
    interval = 60
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            pass
    pilot_loop(interval)