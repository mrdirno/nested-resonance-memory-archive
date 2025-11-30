#!/usr/bin/env python3
"""
Experiment: Cycle 2607 - The Controller
Goal: Implement a master process manager to launch and monitor API and Hive components.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
API_SCRIPT = BASE_DIR / "cycle2606_api.py"
# Note: The API script currently runs its own simulation loop in a thread.
# In a production version, we might separate them, but for now, we just need to ensure
# the API (which hosts the hive logic) is up and running.

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.running = True

    def start_process(self, name, command, log_file=None):
        """Start a subprocess."""
        print(f"[CONTROLLER] Starting {name}...")
        
        stdout_dest = subprocess.PIPE
        if log_file:
            stdout_dest = open(log_file, "w")
            
        try:
            proc = subprocess.Popen(
                command,
                stdout=stdout_dest,
                stderr=subprocess.STDOUT,
                cwd=str(BASE_DIR.parent), # Run from root for imports
                preexec_fn=os.setsid # New process group
            )
            self.processes[name] = proc
            print(f"[CONTROLLER] {name} started (PID: {proc.pid})")
            return True
        except Exception as e:
            print(f"[CONTROLLER] Failed to start {name}: {e}")
            return False

    def monitor(self):
        """Monitor running processes."""
        try:
            while self.running:
                for name, proc in list(self.processes.items()):
                    ret = proc.poll()
                    if ret is not None:
                        print(f"[CONTROLLER] WARNING: {name} exited with code {ret}")
                        del self.processes[name]
                        
                if not self.processes:
                    print("[CONTROLLER] All processes exited. Shutting down.")
                    self.running = False
                    break
                    
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[CONTROLLER] Interrupt received. Stopping...")
            self.stop_all()

    def stop_all(self):
        """Terminate all managed processes."""
        self.running = False
        print("[CONTROLLER] Terminating processes...")
        for name, proc in self.processes.items():
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                print(f"[CONTROLLER] Stopped {name}")
            except Exception as e:
                print(f"[CONTROLLER] Error stopping {name}: {e}")

def main():
    print("Cycle 2607: The Controller - System Startup")
    
    manager = ProcessManager()
    
    # 1. Start API (which includes the Hive simulation backend)
    # Use unbuffered output (-u)
    if not manager.start_process("API_Server", [sys.executable, "-u", str(API_SCRIPT)], log_file="experiments/logs/api.log"):
        sys.exit(1)

    # Wait for API to initialize
    time.sleep(2)
    
    # 2. (Optional) Start Dashboard if requested
    # For now, we just run the API as the core service.
    # In a real deployment, we might launch the visualization server or other agents here.
    
    print("[CONTROLLER] System Running. Check experiments/logs/api.log for output.")
    print("[CONTROLLER] Press Ctrl+C to shutdown.")
    
    manager.monitor()

if __name__ == "__main__":
    # Ensure log dir exists
    Path("experiments/logs").mkdir(exist_ok=True)
    main()
