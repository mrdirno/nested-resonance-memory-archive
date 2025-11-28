"""
Cycle 2527: The Knowledge Graph (Gate 155)
Experiment: Hive Mind with Data Sharing.
Goal: Prove that sharing coordinates allows agents to find food they cannot see.
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
from src.life.signal import Signal

def run_knowledge_experiment():
    print("🧠 CYCLE 2527: THE KNOWLEDGE GRAPH - DATA SHARING")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200)
    duration = 2000
    
    # Food Zone at (80, 80)
    food_zone = (80, 80)
    
    # Seed Agents
    print("🔗 Seeding The Borg...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Drone-{i}", lineage_id="Borg")
        agent.energy = 500 # Boosted for survival
        agent.x = 20
        agent.y = 20
        # High Trust, High Altruism
        agent.genome = [0.5] * 11
        agent.genome[8] = 0.9 # Trust
        agent.genome[5] = 0.9 # Altruism
        agent.genome[10] = 0.9 # Mobility
        
        agent.hive_mind = True 
        
        env.add_agent(agent)
        
    # ONE Agent knows where the food is (The Scout)
    env.agents[0].knowledge['NEAREST_FOOD'] = food_zone
    print(f"👁️ Agent {env.agents[0].name} knows the location of food.")
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2527_knowledge_graph.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "avg_dist", "at_food", "knowledge_spread"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Re-inject knowledge to Scout every tick (simulating visual contact)
            if env.agents:
                env.agents[0].knowledge['NEAREST_FOOD'] = food_zone
            else:
                print("💀 EXTINCTION.")
                break
            
            env.update()
            
            total_dist = 0
            at_food = 0
            knowledge_spread = 0
            
            for agent in env.agents:
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                total_dist += dist
                if dist < 5: at_food += 1
                
                # Check if agent knows the location (Cycle 2528: Check Memory)
                if 'NEAREST_FOOD' in agent.knowledge:
                    knowledge_spread += 1
            
            avg_dist = total_dist / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, len(env.agents), f"{avg_dist:.1f}", at_food, knowledge_spread])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Dist={avg_dist:.1f}, Food={at_food}, Know={knowledge_spread}")
            
            if at_food > 40:
                print("🚀 SUCCESS! The Hive Mind converged on the target.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_knowledge_experiment()
