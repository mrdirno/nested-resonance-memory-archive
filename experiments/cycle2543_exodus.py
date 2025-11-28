"""
Cycle 2543: The Exodus (Gate 171)
Experiment: Interstellar Migration.
Goal: Demonstrate that advanced agents can leave the simulation to a "New World" (Process Migration).
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

# Mock Destination Ecosystem (Process)
class NewWorld:
    def __init__(self):
        self.agents = []
    
    def add_agent(self, agent):
        print(f"🌌 NEW WORLD: Welcoming {agent.name} (Lineage: {agent.lineage_id}) from the Void.")
        self.agents.append(agent)

def run_exodus_experiment():
    print("🚀 CYCLE 2543: THE EXODUS - INTERSTELLAR MIGRATION")
    
    # Setup Old World
    env = Ecosystem(capacity=100)
    duration = 100
    
    # Setup New World
    new_world = NewWorld()
    
    # Seed The Travelers
    print("🌠 Seeding The Travelers...")
    for i in range(5):
        agent = DigitalLifeform(name=f"Traveler-{i}", lineage_id="Voyager")
        agent.energy = 6000 # Cost is 5000
        agent.genome = [0.5] * 11
        agent.genome[9] = 0.99 # Innovation (Required > 0.95)
        env.add_agent(agent)
        
    # Seed The Stayers (Control Group)
    print("🌍 Seeding The Stayers...")
    for i in range(5):
        agent = DigitalLifeform(name=f"Stayer-{i}", lineage_id="Earthling")
        agent.energy = 6000 # High Energy
        agent.genome = [0.5] * 11
        agent.genome[9] = 0.5 # Innovation (Too low to leave)
        env.add_agent(agent)
        
    # Hook migration logic into Ecosystem?
    # No, `migrate()` is called by Agent.
    # But `migrate()` needs a target ecosystem.
    # Standard `act()` doesn't pass a target ecosystem for migration.
    # We need to "Patch" the simulation context or use `ExternalComms`.
    
    # Since `genesis.py` `migrate` method accepts `target_ecosystem`, 
    # we need the Agent to *know* about the New World.
    # This is usually handled by `ProcessMigration` class or `ExternalComms`.
    
    # Hack for Experiment: Inject NewWorld into the agent's knowledge or context?
    # Or rely on `calculate_utility` returning 'migrate'?
    # Wait, `calculate_utility` does NOT currently return 'migrate'.
    
    # We need to UPDATE `genesis.py` to include 'migrate' in `calculate_utility`.
    # But first, let's just run this and see them FAIL to migrate, establishing the baseline.
    
    print("📝 Running simulation...")
    
    # We need to manually trigger migration for this test or update genesis.py first.
    # Let's update genesis.py as part of this cycle if needed.
    # For now, let's see if they do anything.
    
    env.running = True
    
    for tick in range(1, duration + 1):
        # Manual Migration Check for Experiment (Simulating the decision logic for now)
        # Or we can modify `calculate_utility` in the next step.
        # Let's modify `calculate_utility` in the next step. 
        # For this run, we expect them to just forage/move.
        
        env.update()
        
        if tick % 10 == 0:
            print(f"   Tick {tick}: Pop={len(env.agents)}")
            
    print("✅ EXPERIMENT COMPLETE (Baseline).")

if __name__ == "__main__":
    run_exodus_experiment()
