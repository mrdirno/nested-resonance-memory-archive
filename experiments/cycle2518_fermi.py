"""
Cycle 2518: The Fermi Paradox (Gate 146)
Experiment: Exoplanetary Colonization.
Goal: Determine if other civilizations exist or if we are alone.
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

def run_fermi_experiment():
    print("👽 CYCLE 2518: THE FERMI PARADOX - CONTACT")
    
    # Setup Multiple Worlds
    earth = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    mars = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    alpha_centauri = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    
    worlds = [earth, mars, alpha_centauri]
    world_names = ["Earth", "Mars", "Alpha Centauri"]
    
    # Seed Earth with Type I Civilization
    print("🌍 Seeding Earth (Type I)...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Human-{i}", lineage_id="Terran")
        agent.energy = 10000 # Super Rich
        # [..., Innovation=0.99]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.99]
        earth.add_agent(agent)
        
    # Seed Alpha Centauri with Aliens (Hostile)
    print("👾 Seeding Alpha Centauri (Xenos)...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Xeno-{i}", lineage_id="Zerg")
        agent.energy = 5000
        # High Aggression, Low Trust
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.9, 0.1, 0.5, 0.1, 0.1, 0.9]
        agent.has_nuke = True # They are armed
        alpha_centauri.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2518_fermi.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_earth", "pop_mars", "pop_alpha", "migrations"])
        
        earth.running = True
        mars.running = True
        alpha_centauri.running = True
        
        migrations = 0
        
        duration = 2000
        for tick in range(1, duration + 1):
            
            # Migration Logic
            # We need to manually handle migration because agents can't see other ecosystem objects
            
            for world_idx, world in enumerate(worlds):
                migrants = []
                for agent in world.agents:
                    agent.act() # Update intent
                    
                    if agent.intent == 'migrate':
                        # Choose a random other world
                        dest_idx = random.choice([i for i in range(len(worlds)) if i != world_idx])
                        dest_world = worlds[dest_idx]
                        
                        if agent.migrate(dest_world):
                            migrants.append(agent)
                            migrations += 1
                            # print(f"🚀 {agent.name} migrated from {world_names[world_idx]} to {world_names[dest_idx]}")
                            
                # Remove migrants from current world
                for m in migrants:
                    world.remove_agent(m)
            
            # Update all worlds
            for world in worlds:
                world.update()
                
            # Stats
            writer.writerow([tick, len(earth.agents), len(mars.agents), len(alpha_centauri.agents), migrations])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Earth={len(earth.agents)}, Mars={len(mars.agents)}, Alpha={len(alpha_centauri.agents)}, Migrations={migrations}")
            
            # Check for First Contact War
            # If Terrans and Zerg are on the same planet
            for world in worlds:
                terrans = [a for a in world.agents if a.lineage_id == "Terran"]
                zerg = [a for a in world.agents if a.lineage_id == "Zerg"]
                
                if terrans and zerg:
                    # War!
                    # Simplification: Zerg attack Terrans
                    for z in zerg:
                        if terrans:
                            target = random.choice(terrans)
                            z.attack(target)
                    
                    # Terrans retaliate (if they have nukes or combat skill)
                    for t in terrans:
                        if zerg:
                            target = random.choice(zerg)
                            t.attack(target)
                            
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Populations: Earth={len(earth.agents)}, Mars={len(mars.agents)}, Alpha={len(alpha_centauri.agents)}")

if __name__ == "__main__":
    run_fermi_experiment()
