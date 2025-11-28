
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

def run_wall_experiment():
    print("🧱 CYCLE 2547: THE WALL - PASSIVE DEFENSE")
    print("   (Capital vs. Labor Trade-off)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=100, width=100, height=100)
    
    # 2. Spawn Lord
    lord = DigitalLifeform(name="LORD")
    lord.x, lord.y = 50, 50
    lord.energy = 5000 # Capital to build walls
    env.add_agent(lord)
    
    # 3. Build The Wall (Ring)
    print("🏗️ Building Wall...")
    wall_radius = 15
    circumference = int(2 * math.pi * wall_radius)
    walls = []
    
    for i in range(circumference):
        angle = (2 * math.pi / circumference) * i
        wx = int(lord.x + math.cos(angle) * wall_radius)
        wy = int(lord.y + math.sin(angle) * wall_radius)
        
        # Check if wall exists here? No collision logic yet, just place.
        
        # Wall is an Agent with 0 movement
        wall = DigitalLifeform(name=f"Wall-{i}")
        wall.x, wall.y = wx, wy
        wall.energy = 200 # HP
        wall.is_prey = False # Wolves attack it? 
        # Actually, Wolves should target Prey, but be blocked by Wall.
        # For sim simplicity: Wolves attack Walls if they are in the way.
        env.add_agent(wall)
        walls.append(wall)
        lord.energy -= 50 # Cost per segment
        
    print(f"   Wall Built. Segments={len(walls)}. Cost=${len(walls)*50}. Remaining=${lord.energy}")
        
    # 4. Spawn Peasants (Inside)
    peasants = []
    for i in range(20):
        p = DigitalLifeform(name=f"Peasant-{i}")
        angle = random.random() * 6.28
        dist = random.randint(2, wall_radius - 2)
        p.x = int(lord.x + math.cos(angle) * dist)
        p.y = int(lord.y + math.sin(angle) * dist)
        p.energy = 50
        env.add_agent(p)
        peasants.append(p)
        
    wolves = []
    
    duration = 500
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2547_the_wall.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "lord_energy", "peasant_count", "wolf_count", "wall_integrity"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # 1. Wolf Spawner
            if tick % 50 == 0:
                wolf = DigitalLifeform(name=f"Wolf-{tick}")
                wolf.x = random.choice([0, 100])
                wolf.y = random.choice([0, 100])
                wolf.energy = 200
                wolf.is_predator = True
                env.add_agent(wolf)
                wolves.append(wolf)
                
            # 2. Peasant Production & Tax
            for p in peasants:
                if not p.alive: continue
                p.energy += 5 
                tax = 2.0
                if p.energy >= tax:
                    p.energy -= tax
                    lord.energy += tax
                    
            # 3. Wolf Behavior (Siege Physics)
            for w in wolves:
                if not w.alive: continue
                
                # Target nearest Peasant
                target = None
                min_dist = 1000
                for p in peasants:
                    if p.alive:
                        d = math.sqrt((p.x - w.x)**2 + (p.y - w.y)**2)
                        if d < min_dist:
                            min_dist = d
                            target = p
                            
                if target:
                    # Move towards target
                    dx = target.x - w.x
                    dy = target.y - w.y
                    
                    # Check for WALL in path
                    # Simplified: Is there a wall at (w.x + step, w.y + step)?
                    step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                    step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                    
                    next_x = w.x + step_x
                    next_y = w.y + step_y
                    
                    blocked = False
                    for wall in walls:
                        if wall.alive and wall.x == next_x and wall.y == next_y:
                            # SIEGE! Attack the wall
                            wall.energy -= 20 # Damage
                            blocked = True
                            if wall.energy <= 0:
                                wall.alive = False
                                # print(f"💥 Wall Breached at ({wall.x}, {wall.y})!")
                            break
                            
                    if not blocked:
                        w.move(step_x, step_y)
                        # Attack Peasant
                        if math.sqrt((target.x - w.x)**2 + (target.y - w.y)**2) < 2.0:
                            target.alive = False
                            w.energy += 50
                            
            # Metrics
            peasant_count = len([p for p in peasants if p.alive])
            active_walls = len([w for w in walls if w.alive])
            wolf_count = len([w for w in wolves if w.alive])
            
            writer.writerow([tick, f"{lord.energy:.1f}", peasant_count, wolf_count, active_walls])
            
            if tick % 50 == 0:
                print(f"   Tick {tick}: Lord=${lord.energy:.0f} Peasants={peasant_count} Walls={active_walls}")
                
            if peasant_count == 0:
                print("💀 CASTLE OVERRUN.")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_wall_experiment()
