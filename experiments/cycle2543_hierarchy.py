
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

def run_hierarchy_experiment():
    print("👑 CYCLE 2543: THE HIERARCHY - LEADER/FOLLOWER DYNAMICS")
    print("   (Relative Frame of Reference Test)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=50, width=100, height=100) # Larger map for movement
    
    # 2. Spawn Commander
    commander = DigitalLifeform(name="COMMANDER-Alpha")
    commander.x, commander.y = 50, 50
    commander.energy = 5000
    env.add_agent(commander)
    print(f"🫡  Commander Spawned at ({commander.x}, {commander.y})")
    
    # 3. Spawn Squad (V-Formation)
    print("🤖 Spawning Squad...")
    squad = []
    # V-Formation Offsets relative to Commander
    offsets = [
        (-2, -2), (2, -2),   # Flank 1
        (-4, -4), (4, -4),   # Flank 2
        (-6, -6), (6, -6),   # Flank 3
        (-8, -8), (8, -8),   # Flank 4
        (-10,-10), (10,-10)  # Rear Guard
    ]
    
    for i, (ox, oy) in enumerate(offsets):
        agent = DigitalLifeform(name=f"Squad-{i}")
        agent.x = commander.x + ox
        agent.y = commander.y + oy
        agent.energy = 1000
        # Store assigned offset in agent knowledge
        agent.knowledge['offset_x'] = ox
        agent.knowledge['offset_y'] = oy
        env.add_agent(agent)
        squad.append(agent)
        
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2543_hierarchy.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "commander_pos", "avg_lag", "formation_breakages", "energy_cost"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            formation_breakages = 0
            total_lag = 0
            tick_energy_cost = 0
            
            # 1. Commander Moves (Intent)
            # Commander moves 1 step in a consistent direction (with some jitter)
            # Simulating a patrol path
            if tick < 25:
                cx_move, cy_move = 1, 0 # East
            elif tick < 50:
                cx_move, cy_move = 0, 1 # South
            elif tick < 75:
                cx_move, cy_move = -1, 0 # West
            else:
                cx_move, cy_move = 0, -1 # North
                
            commander.move(cx_move, cy_move)
            
            # 2. Squad Reacts
            for agent in squad:
                # Ideal Position = Commander Current Pos + Offset
                target_x = commander.x + agent.knowledge['offset_x']
                target_y = commander.y + agent.knowledge['offset_y']
                
                dx = target_x - agent.x
                dy = target_y - agent.y
                dist = math.sqrt(dx*dx + dy*dy)
                total_lag += dist
                
                # Movement Logic
                step_x = 0
                step_y = 0
                
                # If out of position, move towards target
                if dist > 0:
                    step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                    step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                    
                    agent.move(step_x, step_y)
                    tick_energy_cost += 0.2
                
                # Check Breakage (Lag > 2 units)
                if dist > 2.0:
                    formation_breakages += 1
            
            avg_lag = total_lag / len(squad)
            writer.writerow([tick, f"({commander.x}|{commander.y})", f"{avg_lag:.2f}", formation_breakages, f"{tick_energy_cost:.1f}"])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Cmdr=({commander.x},{commander.y}) Lag={avg_lag:.2f} Breaks={formation_breakages}")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_hierarchy_experiment()
