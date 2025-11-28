"""
Cycle 2529: The Great Filter (Gate 157)
Experiment: Systemic Crisis Survival.
Goal: Compare Hive Mind vs Individualist survival rates under extreme scarcity.
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

def run_great_filter_experiment():
    print("🌌 CYCLE 2529: THE GREAT FILTER - SCARCITY TEST")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200)
    duration = 2000
    
    # Food Zones
    # Zone A: Abundant initially, then depletes.
    # Zone B: Hidden, activates later.
    zone_a = (20, 80)
    zone_b = (80, 20)
    
    # Seed Agents
    # Group 1: The Borg (Hive Mind)
    print("🤖 Seeding The Borg (Hive Mind)...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Borg-{i}", lineage_id="Borg")
        agent.energy = 500
        agent.x = 50
        agent.y = 50
        agent.genome = [0.5] * 11
        agent.genome[8] = 0.9 # Trust
        agent.genome[5] = 0.9 # Altruism
        agent.genome[10] = 0.9 # Mobility
        agent.hive_mind = True 
        env.add_agent(agent)
        
    # Group 2: The Loners (Individualists)
    print("🤠 Seeding The Loners (Individualists)...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Loner-{i}", lineage_id="Loner")
        agent.energy = 500
        agent.x = 50
        agent.y = 50
        agent.genome = [0.5] * 11
        agent.genome[8] = 0.1 # Trust
        agent.genome[5] = 0.1 # Altruism
        agent.genome[10] = 0.9 # Mobility
        agent.hive_mind = False 
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2529_great_filter.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_borg", "pop_loner", "phase"])
        
        env.running = True
        phase = "ABUNDANCE"
        
        # Initial Knowledge: Both groups know Zone A
        for agent in env.agents:
            agent.knowledge['NEAREST_FOOD'] = zone_a
        
        for tick in range(1, duration + 1):
            
            # PHASE CONTROL
            if tick < 500:
                phase = "ABUNDANCE"
                # Food is at Zone A
                current_food = zone_a
            elif tick == 500:
                print("⚠️ THE GREAT DROUGHT BEGINS! Zone A is empty.")
                phase = "DROUGHT"
                # Zone A depletes. Agents must find Zone B.
                current_food = zone_b # Only implicitly exists, they don't know it yet
                
                # Wipe Knowledge of Zone A (Simulate depletion)
                for agent in env.agents:
                    if 'NEAREST_FOOD' in agent.knowledge:
                        del agent.knowledge['NEAREST_FOOD']
                        
                # ONE Scout from EACH team finds Zone B
                borgs = [a for a in env.agents if a.lineage_id == "Borg"]
                loners = [a for a in env.agents if a.lineage_id == "Loner"]
                
                if borgs: borgs[0].knowledge['NEAREST_FOOD'] = zone_b
                if loners: loners[0].knowledge['NEAREST_FOOD'] = zone_b
                
                print("🕵️ Scouts have found Zone B (Hidden Oasis).")
                
            else:
                phase = "DROUGHT"
                current_food = zone_b
            
            # Signal Injection (Simulate Environment)
            # If they are close to food, they sense it (and add to knowledge)
            for agent in env.agents:
                dist = ((agent.x - current_food[0])**2 + (agent.y - current_food[1])**2)**0.5
                if dist < 20: # Vision range
                    agent.sensed_signals['NEAREST_FOOD'] = current_food
            
            env.update()
            
            # Reward for being at food
            for agent in env.agents:
                dist = ((agent.x - current_food[0])**2 + (agent.y - current_food[1])**2)**0.5
                if dist < 5:
                    agent.energy += 20 # Eat
            
            # Stats
            borg_pop = len([a for a in env.agents if a.lineage_id == "Borg"])
            loner_pop = len([a for a in env.agents if a.lineage_id == "Loner"])
            
            writer.writerow([tick, borg_pop, loner_pop, phase])
            
            if tick % 100 == 0:
                print(f"   Tick {tick} [{phase}]: Borg={borg_pop}, Loner={loner_pop}")
            
            if len(env.agents) == 0:
                print("💀 TOTAL EXTINCTION.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_great_filter_experiment()
