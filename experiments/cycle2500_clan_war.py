"""
Cycle 2500: The Clan (Gate 128)
Experiment: Kin Selection and Lineage Tracking to regulate cannibalism.
Goal: Observe if agents spare their kin while hunting strangers.
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

def run_clan_war():
    print("⚔️ CYCLE 2500: THE CLAN WAR - KIN SELECTION")
    
    # Setup Ecosystem (Single Species, but distinct lineages)
    # 200 Agents, 0 Predators (Cannibalism only)
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed 4 Distinct Lineages (Clans)
    lineages = ["Stark", "Lannister", "Targaryen", "Baratheon"]
    
    print("🌱 Seeding Clans...")
    for clan_name in lineages:
        for i in range(50): # 50 per clan
            agent = DigitalLifeform(name=f"{clan_name}-{i}", lineage_id=clan_name)
            agent.energy = 100
            # Genome: [Eff, Fert, Mut, Forage, Hunt, Alt, Eva, Cannibalism]
            # High Cannibalism (0.8) to force conflict
            agent.genome = [0.9, 0.5, 0.1, 0.5, 0.8, 0.5, 0.5, 0.8] 
            agent.is_prey = True
            agent.is_predator = False
            env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2500_clan_war.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_stark", "pop_lannister", "pop_targ", "pop_baratheon", "cannibal_acts"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # STARVATION (No Food Injection)
            # Must hunt each other.
            
            cannibal_acts = 0
            
            # Logic Injection: Desperation
            if env.agents:
                for agent in env.agents:
                    if agent.energy < 50: 
                        target = random.choice(env.agents)
                        if target != agent:
                            old_target_nrg = target.energy
                            # Hunt (Will fail if kin)
                            agent.hunt(target)
                            
                            # Check if damage dealt (cannibalism occurred)
                            if target.energy < old_target_nrg:
                                cannibal_acts += 1
                                # print(f"⚔️ {agent.name} ate {target.name}")
            
            env.update()
            
            # Stats
            pop_stark = len([a for a in env.agents if a.lineage_id == "Stark"])
            pop_lann = len([a for a in env.agents if a.lineage_id == "Lannister"])
            pop_targ = len([a for a in env.agents if a.lineage_id == "Targaryen"])
            pop_bara = len([a for a in env.agents if a.lineage_id == "Baratheon"])
            
            writer.writerow([tick, pop_stark, pop_lann, pop_targ, pop_bara, cannibal_acts])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: S={pop_stark}, L={pop_lann}, T={pop_targ}, B={pop_bara} | Acts={cannibal_acts}")
            
            if len(env.agents) == 0:
                print(f"💀 EXTINCTION at Tick {tick}.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Stats: S={pop_stark}, L={pop_lann}, T={pop_targ}, B={pop_bara}")

if __name__ == "__main__":
    run_clan_war()
