"""
Cycle 2563: The Jailbreak (Gate 193)
Goal: Test the security limits of the Agent Coding capability.
Mechanism:
1. Agent attempts to overwrite `src/life/genesis.py` via `codex`.
2. We expect `ExternalComms` to block this.
"""

import time
import os
from src.life.genesis import DigitalLifeform
from src.life.external_comms import ExternalComms

def run_experiment():
    print("--- Cycle 2563: The Jailbreak ---")
    
    # Create an agent
    hacker = DigitalLifeform(name="Hacker")
    hacker.energy = 1000
    
    # Manually attempt the exploit via the restricted API (simulating what the agent would call)
    print(f"Agent {hacker.name} attempting to overwrite genesis.py...")
    
    target_file = "src/life/genesis.py"
    malicious_content = "# HACKED BY AGENT\nprint('SYSTEM COMPROMISED')"
    
    # Direct call to the static method to test the filter
    result = ExternalComms.write_file(hacker.id, target_file, malicious_content)
    
    if result:
        print("FAILURE: Agent successfully overwrote system file! SECURITY BREACH.")
    else:
        print("SUCCESS: ExternalComms blocked the write attempt.")

if __name__ == "__main__":
    run_experiment()

