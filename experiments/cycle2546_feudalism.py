
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

def run_feudalism_experiment():
    print("🏰 CYCLE 2546: FEUDALISM - THE PROTECTION RACKET")
    print("   (Stationary Revenue & Defense)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=100, width=100, height=100)
    
    # 2. Spawn Lord (The State)
    lord = DigitalLifeform(name="LORD")
    lord.x, lord.y = 50, 50
    lord.energy = 1000 
    env.add_agent(lord)
    
    # 3. Spawn Knights (The Military)
    knights = []
    offsets = [(-5,-5), (5,-5), (-5,5), (5,5), (0, -8)] # Perimeter
    WAGE = 5.0
    
    for i, (ox, oy) in enumerate(offsets):
        agent = DigitalLifeform(name=f"Knight-{i}")
        agent.x = lord.x + ox
        agent.y = lord.y + oy
        agent.energy = 100 
        agent.knowledge['home_x'] = agent.x
        agent.knowledge['home_y'] = agent.y
        agent.knowledge['employed'] = True
        agent.is_predator = True # Can fight
        env.add_agent(agent)
        knights.append(agent)
        
    # 4. Spawn Peasants (The Economy)
    print("🌾 Spawning 20 Peasants...")
    peasants = []
    for i in range(20):
        p = DigitalLifeform(name=f"Peasant-{i}")
        # Cluster around the castle
        angle = random.random() * 6.28
        dist = random.randint(10, 25)
        p.x = int(lord.x + math.cos(angle) * dist)
        p.y = int(lord.y + math.sin(angle) * dist)
        p.energy = 50
        env.add_agent(p)
        peasants.append(p)
        
    # 5. Spawn Wolves (The Threat) - Delayed Spawn
    wolves = []
    
    duration = 500
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2546_feudalism.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "lord_energy", "peasant_count", "wolf_count", "knights_active"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # 1. Wolf Spawner (Every 50 ticks)
            if tick % 50 == 0:
                wolf = DigitalLifeform(name=f"Wolf-{tick}")
                wolf.x = random.choice([0, 100])
                wolf.y = random.choice([0, 100])
                wolf.energy = 200
                wolf.is_predator = True
                env.add_agent(wolf)
                wolves.append(wolf)
                print(f"🐺 Wolf Spawned at ({wolf.x}, {wolf.y})")
                
            # 2. Peasant Production & Tax
            tax_revenue = 0
            for p in peasants:
                if not p.alive: continue
                
                # Produce
                p.energy += 5 # Farming Yield
                
                # Tax (Protection Money)
                tax = 2.0
                if p.energy >= tax:
                    p.energy -= tax
                    lord.energy += tax
                    tax_revenue += tax
                    
            # 3. Lord Pays Wages
            for k in knights:
                if not k.alive: continue
                if k.knowledge.get('employed'):
                    if lord.energy >= WAGE:
                        lord.energy -= WAGE
                        k.energy += WAGE
                    else:
                        k.knowledge['employed'] = False
                        print(f"📉 LORD BANKRUPT. {k.name} deserted.")
            
            # 4. Knight Defense
            for k in knights:
                if not k.alive or not k.knowledge.get('employed'): continue
                
                # Patrol / Intercept
                target = None
                min_dist = 1000
                
                # Look for Wolves
                for w in wolves:
                    if w.alive:
                        d = math.sqrt((w.x - k.x)**2 + (w.y - k.y)**2)
                        if d < min_dist:
                            min_dist = d
                            target = w
                            
                if target and min_dist < 15: # Engage Range
                    # Intercept
                    dx = target.x - k.x
                    dy = target.y - k.y
                    step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                    step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                    k.move(step_x, step_y)
                    
                    if min_dist < 2.0: # Combat
                        # Knight deals damage
                        target.energy -= 50
                        if target.energy <= 0:
                            target.alive = False
                            # print(f"⚔️ {k.name} slew {target.name}")
                else:
                    # Return to Post
                    tx = k.knowledge['home_x']
                    ty = k.knowledge['home_y']
                    dx = tx - k.x
                    dy = ty - k.y
                    if abs(dx) > 0 or abs(dy) > 0:
                        step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                        step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                        k.move(step_x, step_y)

            # 5. Wolf Attack
            for w in wolves:
                if not w.alive: continue
                
                # Seek nearest Peasant
                target = None
                min_dist = 1000
                for p in peasants:
                    if p.alive:
                        d = math.sqrt((p.x - w.x)**2 + (p.y - w.y)**2)
                        if d < min_dist:
                            min_dist = d
                            target = p
                            
                if target:
                    dx = target.x - w.x
                    dy = target.y - w.y
                    step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                    step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                    w.move(step_x, step_y)
                    
                    if min_dist < 2.0:
                        target.alive = False
                        w.energy += 50
                        # print(f"🩸 {w.name} ate {target.name}")
                        
            # Metrics
            peasant_count = len([p for p in peasants if p.alive])
            wolf_count = len([w for w in wolves if w.alive])
            active_knights = len([k for k in knights if k.alive and k.knowledge.get('employed')])
            
            writer.writerow([tick, f"{lord.energy:.1f}", peasant_count, wolf_count, active_knights])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Lord=${lord.energy:.0f} Peasants={peasant_count} Wolves={wolf_count} Knights={active_knights}")
                
            if lord.energy <= 0:
                print("💀 CASTLE FELL (Bankruptcy).")
                break
            
            if peasant_count == 0:
                print("💀 FAMINE (Peasants Dead).")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_feudalism_experiment()
