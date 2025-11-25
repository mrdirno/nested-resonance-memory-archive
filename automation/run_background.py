#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import datetime

def run_background(command, log_name=None):
    """
    Runs a command in the background, redirecting output to a log file.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if log_name is None:
        cmd_slug = command.split()[0].split('/')[-1].replace('.py', '')
        log_name = f"{cmd_slug}_{timestamp}.log"
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_path = os.path.join(log_dir, log_name)
    
    print(f"Launching: {command}")
    print(f"Logging to: {log_path}")
    
    with open(log_path, "w") as log_file:
        # specific to unix-like systems
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setpgrp # Detach from parent group
        )
    
    print(f"Process ID: {process.pid}")
    return process.pid, log_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_background.py '<command>' [log_name]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    log = sys.argv[2] if len(sys.argv) > 2 else None
    
    run_background(cmd, log)
