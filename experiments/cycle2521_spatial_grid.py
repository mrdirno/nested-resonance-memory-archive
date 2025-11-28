"""
Cycle 2521: The Grid (Gate 149)
Experiment: Spatial Dimension (2D Physics).
Goal: Verify that agents have (x,y) coordinates and move over time.
"""

import sys
import os
import time
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_spatial_grid_experiment():
    print("🕸️ CYCLE 2521: THE GRID - SPATIAL PHYSICS")
    
    # 1. Setup Ecosystem with Grid
    width = 50
    height = 50
    env = Ecosystem(capacity=100, width=width, height=height)
    
    # 2. Add Agents
    print("📍 Seeding Agents...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Walker-{i}")
        agent.energy = 1000 # High energy to support movement cost
        env.add_agent(agent)
        print(f"   {agent.name} spawned at ({agent.x}, {agent.y})")
        
    print(f"   Grid Size: {width}x{height}")
    
    # 3. Run Simulation
    print("🚀 Starting Simulation...")
    env.running = True
    
    for tick in range(1, 51):
        env.update()
        
        # Print positions every 10 ticks
        if tick % 10 == 0:
            print(f"--- Tick {tick} ---")
            for agent in env.agents:
                print(f"   {agent.name}: ({agent.x}, {agent.y}) Energy={agent.energy:.1f}")
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_spatial_grid_experiment()
