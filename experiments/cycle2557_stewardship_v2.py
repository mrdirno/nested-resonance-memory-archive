
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

def run_stewardship_v2():
    print("🌳 CYCLE 2557-V2: ADAPTIVE STEWARDSHIP")
    print("   (Proportional Harvesting)")
    
    REGEN_RATE = 0.05
    CAPACITY = 1000.0
    resource = CAPACITY
    
    agents = [DigitalLifeform(f"Steward-{i}") for i in range(10)]
    
    # Total Safe Harvest = 4% (leaves 1% growth buffer)
    PER_AGENT_RATE = 0.004 # 0.4%
    
    for tick in range(1, 101):
        harvest_total = 0
        for a in agents:
            take = resource * PER_AGENT_RATE
            resource -= take
            a.energy += take
            harvest_total += take
            
        # Regen
        growth = resource * REGEN_RATE
        resource += growth
        resource = min(resource, CAPACITY)
        
        if tick % 20 == 0:
            print(f"   Tick {tick}: Resource={resource:.1f} Harvested={harvest_total:.1f}")
            
    if resource > 900:
        print("✨ SUSTAINABILITY ACHIEVED.")
    else:
        print("💀 SYSTEM DEGRADING.")

if __name__ == "__main__":
    run_stewardship_v2()
