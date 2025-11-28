"""
Cycle 2533: The Debugger (Gate 161)
Experiment: Trace signal path for construction.
Goal: Determine why build signals are not processed.
"""

import sys
import os
import csv
import time
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_debug_experiment():
    print("🐞 CYCLE 2533: THE DEBUGGER - SIGNAL TRACE")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200)
    duration = 10
    
    # Seed a single Planter
    print("👨‍🌾 Seeding One Planter...")
    agent = DigitalLifeform(name="Planter-Debug", lineage_id="Builders")
    agent.energy = 1000 # Very Rich
    agent.x = 50
    agent.y = 50
    agent.genome = [0.5] * 11
    agent.genome[9] = 0.9 # Innovation
    env.add_agent(agent)
        
    print("📝 Running trace...")
    
    for tick in range(1, duration + 1):
        print(f"--- Tick {tick} ---")
        env.update()
        
        farms = len([s for s in env.structures if s['type'] == 'FARM'])
        print(f"   Farms: {farms}")
        
        if farms > 0:
            print("🎉 SUCCESS! Debugging complete. Farms built.")
            break
            
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_debug_experiment()
