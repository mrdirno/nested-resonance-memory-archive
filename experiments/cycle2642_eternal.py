#!/usr/bin/env python3
"""
Experiment: Cycle 2642 - The Eternal
Goal: Verify long-duration stability of the Controller/API stack.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def run_stability_test():
    print("Cycle 2642: The Eternal - Stability Test (30s)")
    
    controller_script = Path("experiments/cycle2607_controller.py")
    
    # Start Controller
    proc = subprocess.Popen(
        [sys.executable, "-u", str(controller_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )
    
    print(f"Controller PID: {proc.pid}")
    
    # Monitor loop
    duration = 30
    start = time.time()
    
    while time.time() - start < duration:
        if proc.poll() is not None:
            print(f"FAILURE: Controller crashed early (Code {proc.returncode}).")
            print(proc.stdout.read().decode())
            sys.exit(1)
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()
        
    print("\nSUCCESS: System stable for 30 seconds.")
    
    # Cleanup
    os.killpg(os.getpgid(proc.pid), signal.SIGINT)
    proc.wait()
    print("Controller shutdown verified.")

if __name__ == "__main__":
    run_stability_test()
