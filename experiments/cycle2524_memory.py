"""
Cycle 2524: The Memory (Gate 152)
Experiment: Utility AI with Short-Term Memory.
Goal: Ensure agents can act on signals received in the same tick.
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

def run_memory_experiment():
    print("🧠 CYCLE 2524: THE MEMORY - SIGNAL PERSISTENCE")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Food Zone at (80, 80)
    food_zone = (80, 80)
    
    # Seed Agents
    print("🤔 Seeding The Thinkers...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Thinker-{i}", lineage_id="Rational")
        agent.energy = 150 # Hungry
        agent.x = 20
        agent.y = 20
        # High Mobility, High Innovation
        agent.genome = [0.5] * 9 + [0.9, 0.9]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2524_memory.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "avg_dist", "at_food", "intent_move_to_food"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Signal Injection (Simulated)
            # We want to ensure this persists through env.update()
            # The fix in genesis.py (sense() appends instead of wipes) should handle this.
            # BUT, ecosystem.py calls sense() first thing in update.
            
            # To simulate a signal from the environment *before* the agent acts,
            # we must inject it into the agent's memory.
            
            for agent in env.agents:
                # Simulate "Seeing" food
                # In a real loop, this would happen inside sense() via ecosystem spatial hash.
                # Here we cheat and inject directly.
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                agent.sensed_signals['NEAREST_FOOD'] = food_zone
            
            env.update()
            
            total_dist = 0
            at_food = 0
            intent_food_count = 0
            
            for agent in env.agents:
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                total_dist += dist
                if dist < 5:
                    at_food += 1
                    agent.energy += 20
                
                if agent.intent == 'move_to_food':
                    intent_food_count += 1
            
            avg_dist = total_dist / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, len(env.agents), f"{avg_dist:.1f}", at_food, intent_food_count])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, AvgDist={avg_dist:.1f}, AtFood={at_food}, Intent={intent_food_count}")
            
            if at_food > 80:
                print("🎉 SUCCESS! The Rational Agents found the food.")
                break
                
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_memory_experiment()
