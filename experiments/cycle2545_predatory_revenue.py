
import sys
import os
import csv
import time
import random
import math
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_revenue_experiment():
    print("⚔️ CYCLE 2545: PREDATORY REVENUE - THE RAID MODEL")
    print("   (Sustainable Hierarchy via Extraction)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=100, width=100, height=100)
    
    # 2. Spawn Commander
    commander = DigitalLifeform(name="KHAN")
    commander.x, commander.y = 50, 50
    commander.energy = 2000 # Higher initial capital
    env.add_agent(commander)
    
    # 3. Spawn Mercenaries
    squad = []
    offsets = [(-2,-2), (2,-2), (-4,-4), (4,-4), (0,-5)]
    WAGE = 5.0
    
    for i, (ox, oy) in enumerate(offsets):
        agent = DigitalLifeform(name=f"Raider-{i}")
        agent.x = commander.x + ox
        agent.y = commander.y + oy
        agent.energy = 100 
        agent.knowledge['offset_x'] = ox
        agent.knowledge['offset_y'] = oy
        agent.knowledge['employed'] = True
        agent.is_predator = True 
        env.add_agent(agent)
        squad.append(agent)
        
    # 4. Spawn Prey (The Resource)
    print("🐑 Spawning 50 Prey...")
    for i in range(50):
        prey = DigitalLifeform(name=f"Sheep-{i}")
        prey.x = random.randint(0, 100)
        prey.y = random.randint(0, 100)
        prey.energy = 100 # Higher Lootable Value
        prey.is_prey = True
        env.add_agent(prey)
        
    duration = 500
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2545_predatory_revenue.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "commander_energy", "squad_size", "prey_count"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            active_squad_size = 0
            prey_count = len([a for a in env.agents if a.is_prey and a.alive and "Sheep" in a.name])
            
            # 1. Commander Behavior (Seek Prey)
            # Commander moves towards nearest Prey to guide the squad
            nearest_prey = None
            min_dist = 1000
            for a in env.agents:
                if a.alive and "Sheep" in a.name:
                    d = abs(a.x - commander.x) + abs(a.y - commander.y)
                    if d < min_dist:
                        min_dist = d
                        nearest_prey = a
            
            if nearest_prey:
                commander.move_to(nearest_prey.x, nearest_prey.y)
            else:
                commander.move(random.choice([-1,1]), random.choice([-1,1])) # Wander if no prey
                
            # 2. Squad Behavior (Hunt & Tax)
            for agent in squad:
                if not agent.alive: continue
                
                # Check Employment (Wage Payout)
                if agent.knowledge.get('employed'):
                    if commander.energy >= WAGE:
                        commander.energy -= WAGE
                        agent.energy += WAGE
                    else:
                        agent.knowledge['employed'] = False
                        print(f"📉 KHAN BANKRUPT. {agent.name} deserted.")
                        
                if agent.knowledge.get('employed'):
                    active_squad_size += 1
                    
                    # Hunt Logic
                    # Look for prey in range
                    hunted = False
                    for target in env.agents:
                        if target.alive and "Sheep" in target.name:
                            dist = math.sqrt((target.x - agent.x)**2 + (target.y - agent.y)**2)
                            if dist < 2.0: # Kill Range
                                # RAID!
                                loot = target.energy
                                target.energy = 0
                                target.alive = False
                                
                                # Tax Logic (50% to Khan)
                                tax = loot * 0.5
                                keep = loot * 0.5
                                
                                commander.energy += tax
                                agent.energy += keep
                                # print(f"⚔️ {agent.name} raided Sheep. Tax=${tax} to Khan.")
                                hunted = True
                                break
                    
                    # Move Logic (Formation)
                    if not hunted:
                        target_x = commander.x + agent.knowledge['offset_x']
                        target_y = commander.y + agent.knowledge['offset_y']
                        
                        dx = target_x - agent.x
                        dy = target_y - agent.y
                        
                        # If far from formation, move to formation
                        # If close to formation, attack nearby prey?
                        # Simplified: Always stick to formation, formation moves to prey.
                        
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist > 0:
                            step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                            step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                            agent.move(step_x, step_y)
                            agent.energy -= 0.5

            # 3. Prey Behavior (Flee)
            for a in env.agents:
                if a.alive and "Sheep" in a.name:
                     a.move(random.choice([-1,0,1]), random.choice([-1,0,1]))

            writer.writerow([tick, f"{commander.energy:.1f}", active_squad_size, prey_count])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Khan=${commander.energy:.0f} Squad={active_squad_size} Prey={prey_count}")
            
            if active_squad_size == 0 or commander.energy <= 0:
                print("💀 EMPIRE FELL.")
                break
            
            if prey_count == 0:
                print("💀 FAMINE. ALL PREY EATEN.")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_revenue_experiment()
