
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform

def run_stewardship_experiment():
    print("🌳 CYCLE 2557: THE STEWARDSHIP - SUSTAINABLE COMMONS")
    print("   (Greedy vs. Optimal Harvesting)")
    
    REGEN_RATE = 0.05
    CAPACITY = 1000.0
    
    # Phase 1: Greedy
    print("\n--- PHASE 1: GREEDY ---")
    resource = CAPACITY
    agents = [DigitalLifeform(f"Greedy-{i}") for i in range(10)]
    
    for tick in range(1, 51):
        # Harvest
        for a in agents:
            take = 20.0 # High demand
            if resource >= take:
                resource -= take
                a.energy += take
            else:
                resource = 0
                
        # Regen
        resource += resource * REGEN_RATE
        resource = min(resource, CAPACITY)
        
        if tick % 10 == 0:
            print(f"   Tick {tick}: Resource={resource:.1f}")
            
        if resource <= 1.0:
            print("💀 COLLAPSE.")
            break
            
    # Phase 2: Stewards
    print("\n--- PHASE 2: STEWARDS ---")
    resource = CAPACITY
    agents = [DigitalLifeform(f"Steward-{i}") for i in range(10)]
    
    # Optimal: Total Harvest <= Total Regen
    # Regen at Cap = 1000 * 0.05 = 50 per tick.
    # 10 agents -> 5 per agent max.
    OPTIMAL_RATE = 5.0
    
    for tick in range(1, 101):
        for a in agents:
            # Steward checks limits
            take = OPTIMAL_RATE
            if resource >= take:
                resource -= take
                a.energy += take
                
        resource += resource * REGEN_RATE
        resource = min(resource, CAPACITY)
        
        if tick % 20 == 0:
            print(f"   Tick {tick}: Resource={resource:.1f}")
            
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_stewardship_experiment()
