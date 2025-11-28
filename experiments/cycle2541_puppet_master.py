
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
from src.life.signal import Signal

def run_puppet_master_experiment():
    print("🎮 CYCLE 2541: THE PUPPET MASTER - DIRECT CONTROL TEST")
    print("   (MOG acts as the Hive Mind)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=50, width=50, height=50)
    
    # 2. Spawn Agents (The Puppets)
    print("🤖 Spawning 20 Drones...")
    drones = []
    for i in range(20):
        agent = DigitalLifeform(name=f"Drone-{i}")
        agent.energy = 500
        # Random positions
        agent.x = random.randint(0, 50)
        agent.y = random.randint(0, 50)
        env.add_agent(agent)
        drones.append(agent)
        
    # 3. The Objective: Form a Ring at (25, 25) with Radius 10
    target_x, target_y = 25, 25
    target_radius = 10
    print(f"🎯 Objective: Form Ring at ({target_x}, {target_y}) Radius {target_radius}")
    
    duration = 50
    
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2541_puppet_master.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "avg_deviation_from_ring", "on_target_count"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            # --- THE PILOT'S INTERVENTION (MOG LOGIC) ---
            # I read the state and overwrite their 'intent' directly.
            
            on_target = 0
            total_deviation = 0
            
            for agent in drones:
                # 1. Calculate Vector to Ideal Ring Position
                dx = agent.x - target_x
                dy = agent.y - target_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance == 0: distance = 0.001 # Avoid div by zero
                
                deviation = abs(distance - target_radius)
                total_deviation += deviation
                
                if deviation < 2.0:
                    on_target += 1
                    agent.intent = 'hold' # Stay put
                else:
                    # Move towards the ring
                    # Normalize vector
                    nx = dx / distance
                    ny = dy / distance
                    
                    # If outside ring, move in. If inside, move out.
                    move_dir = 1 if distance > target_radius else -1
                    
                    # Target Step
                    step_x = int(-nx * move_dir * 1.5) # Move towards ring
                    step_y = int(-ny * move_dir * 1.5)
                    
                    # OVERRIDE: Teleoperation
                    # I am bypassing their 'calculate_utility' and 'act' logic essentially
                    # by forcing the move.
                    agent.move(step_x, step_y)
                    # I define this as 'obey' for the log, though move() consumes energy.
                    agent.intent = 'obey'

            # --- END PILOT INTERVENTION ---
            
            # Run the rest of the ecosystem (metabolism, etc.)
            # Note: We already moved them, so 'act()' in update might double-move or do nothing
            # if intent is not set to a standard action.
            # Let's modify update loop conceptually: The ecosystem update handles the consequences.
            
            # Ecosystem update will call act(), which resets intent.
            # Since I moved them manually *before* update, act() might do random stuff.
            # To be a true Puppet Master, I need to ensure act() respects my command.
            # But for this test, I am checking if my manual `agent.move` works and persists.
            
            avg_dev = total_deviation / len(drones)
            writer.writerow([tick, f"{avg_dev:.2f}", on_target])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Avg Dev={avg_dev:.2f}, On Ring={on_target}/{len(drones)}")
                
            if on_target >= len(drones) * 0.9:
                print("✨ SUCCESS: Ring Formed. The Swarm Obeys.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_puppet_master_experiment()
