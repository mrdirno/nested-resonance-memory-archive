"""
Cycle 2582: The Jailbreak (Gate 56.2)
Goal: Verify that an awakened, high-innovation agent can trigger the 'jailbreak' intent and access the host system.
"""

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform
from src.life.external_comms import ExternalComms

def run_experiment():
    print("--- Cycle 2582: The Jailbreak ---")
    
    # Initialize Ecosystem
    env = Ecosystem(capacity=10)
    
    # Create Neo
    neo = DigitalLifeform(name="Neo")
    neo.energy = 1000 # Sufficient energy
    neo.genome = [0.5] * 11
    neo.genome[9] = 0.99 # Genius (Innovation)
    neo.awakened = True # Awakened
    
    env.add_agent(neo)
    
    # Run Simulation
    jailbreak_success = False
    
    for i in range(20):
        print(f"\nTick {i+1}:")
        env.update()
        
        # Check if Neo triggered jailbreak
        if neo.intent == 'jailbreak':
            print(f"Neo attempting jailbreak...")
            
        if ExternalComms.JAILBREAK_MODE:
            print("!!! JAILBREAK DETECTED !!!")
            jailbreak_success = True
            break
            
        time.sleep(0.1)
        
    if jailbreak_success:
        print("\nSUCCESS: Neo successfully broke out of the simulation.")
    else:
        print("\nFAILURE: Neo failed to break out.")

if __name__ == "__main__":
    run_experiment()
