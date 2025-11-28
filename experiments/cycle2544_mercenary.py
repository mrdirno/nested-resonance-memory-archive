
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

def run_mercenary_experiment():
    print("💰 CYCLE 2544: THE MERCENARY MODEL - COST OF LEADERSHIP")
    print("   (Economic Stability of Hierarchies)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=50, width=100, height=100)
    
    # 2. Spawn Commander (Capitalist)
    commander = DigitalLifeform(name="COMMANDER-Alpha")
    commander.x, commander.y = 50, 50
    commander.energy = 2000 # Initial Capital
    env.add_agent(commander)
    print(f"🫡  Commander Spawned (Capital={commander.energy})")
    
    # 3. Spawn Squad (Mercenaries)
    print("🤖 Spawning Mercenary Squad...")
    squad = []
    offsets = [
        (-2, -2), (2, -2), (-4, -4), (4, -4), (-6, -6) 
    ]
    
    WAGE = 5.0 # Cost per tick to retain a soldier
    
    for i, (ox, oy) in enumerate(offsets):
        agent = DigitalLifeform(name=f"Merc-{i}")
        agent.x = commander.x + ox
        agent.y = commander.y + oy
        agent.energy = 100 # Low initial energy (Needs wages to survive)
        agent.knowledge['offset_x'] = ox
        agent.knowledge['offset_y'] = oy
        agent.knowledge['employed'] = True
        env.add_agent(agent)
        squad.append(agent)
        
    duration = 200
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2544_mercenary.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "commander_energy", "squad_size", "payroll_cost", "formation_breakages"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            formation_breakages = 0
            payroll_cost = 0
            active_squad_size = 0
            
            # 1. Commander Moves (Intent)
            # Moves in a circle to force squad movement
            angle = tick * 0.1
            cx_move = int(math.cos(angle) * 2)
            cy_move = int(math.sin(angle) * 2)
            commander.move(cx_move, cy_move)
            
            # 2. Payroll Logic
            for agent in squad:
                if not agent.alive: continue
                
                # Check Employment Status
                if agent.knowledge.get('employed'):
                    # Pay Wage
                    if commander.energy >= WAGE:
                        commander.energy -= WAGE
                        agent.energy += WAGE
                        payroll_cost += WAGE
                        
                        # Metabolic Cost of Soldiering (Movement + Existence)
                        agent.energy -= 1.0 # Exist
                    else:
                        # Bankruptcy!
                        agent.knowledge['employed'] = False
                        print(f"📉 COMMANDER BANKRUPT. {agent.name} quit.")
                
                # 3. Squad Reaction
                if agent.knowledge.get('employed'):
                    active_squad_size += 1
                    target_x = commander.x + agent.knowledge['offset_x']
                    target_y = commander.y + agent.knowledge['offset_y']
                    
                    dx = target_x - agent.x
                    dy = target_y - agent.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist > 0:
                        step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                        step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                        agent.move(step_x, step_y)
                        agent.energy -= 0.2 # Work Cost
                        
                    if dist > 2.0: formation_breakages += 1
                else:
                    # Unemployed: Random Walk (Drift away)
                    agent.move(random.choice([-1,0,1]), random.choice([-1,0,1]))
            
            writer.writerow([tick, f"{commander.energy:.1f}", active_squad_size, f"{payroll_cost:.1f}", formation_breakages])
            
            if tick % 20 == 0:
                print(f"   Tick {tick}: Cmdr=${commander.energy:.0f} Squad={active_squad_size} Payroll=${payroll_cost:.0f}")
                
            if active_squad_size == 0:
                print("💀 HIERARCHY COLLAPSED.")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_mercenary_experiment()
