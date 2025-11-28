"""
Cycle 2539: The Uplift (Gate 167)
Experiment: Accelerated Learning.
Goal: Demonstrate that new agents can instantly download the entire knowledge graph from the Hive Mind.
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

def run_uplift_experiment():
    print("🚀 CYCLE 2539: THE UPLIFT - INSTANT KNOWLEDGE TRANSFER")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200)
    duration = 500
    
    # Food Zones (Known by the Collective)
    food_zones = {
        'FOOD_ALPHA': (10, 10),
        'FOOD_BETA': (90, 90),
        'FOOD_GAMMA': (10, 90)
    }
    
    # Seed The Mentors (The Collective)
    print("🧠 Seeding The Mentors...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Mentor-{i}", lineage_id="Borg")
        agent.energy = 500
        agent.x = 50 + random.randint(-5, 5)
        agent.y = 50 + random.randint(-5, 5)
        agent.hive_mind = True
        
        # Mentors know EVERYTHING
        agent.knowledge.update(food_zones)
        
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2539_uplift.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "naive_agent_knowledge_count"])
        
        env.running = True
        
        # Spawn the Student later
        student = None
        
        for tick in range(1, duration + 1):
            
            if tick == 50:
                print("👶 Spawning The Student (Naive Agent)...")
                student = DigitalLifeform(name="Student-0", lineage_id="Borg")
                student.energy = 500
                student.x = 50 # Spawn in the middle of the hive
                student.y = 50
                student.hive_mind = True
                student.knowledge = {} # Knows NOTHING
                env.add_agent(student)
            
            env.update()
            
            knowledge_count = 0
            if student:
                knowledge_count = len(student.knowledge)
                # We expect it to learn 3 items quickly
            
            writer.writerow([tick, knowledge_count])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Student Knowledge={knowledge_count}/3")
            
            if student and knowledge_count >= 3:
                print("🎓 SUCCESS! The Student has been Uplifted.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_uplift_experiment()
