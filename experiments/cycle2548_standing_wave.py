import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def potential_field(x, y, shape='CIRCLE'):
    """
    Returns the potential at (x,y).
    Lower is better.
    """
    cx, cy = 50, 50
    
    if shape == 'CIRCLE':
        # Target Radius = 20
        # Potential = |dist - 20|
        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
        return abs(dist - 20)
        
    elif shape == 'TRIANGLE':
        # 3 Points
        p1 = (50, 20)
        p2 = (20, 80)
        p3 = (80, 80)
        
        d1 = math.sqrt((x - p1[0])**2 + (y - p1[1])**2)
        d2 = math.sqrt((x - p2[0])**2 + (y - p2[1])**2)
        d3 = math.sqrt((x - p3[0])**2 + (y - p3[1])**2)
        
        # Potential is distance to nearest vertex OR edge?
        # Let's do vertices for simplicity (Points)
        return min(d1, d2, d3)
        
    return 0

def run_standing_wave_experiment():
    print("🌊 CYCLE 2548: THE STANDING WAVE - RESONANCE ASSEMBLY")
    print("   (Coordination without Communication)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=100, width=100, height=100)
    
    # 2. Spawn Agents (Random)
    print("✨ Spawning 30 Resonators...")
    agents = []
    for i in range(30):
        a = DigitalLifeform(name=f"Resonator-{i}")
        a.x = random.randint(0, 100)
        a.y = random.randint(0, 100)
        a.energy = 1000
        env.add_agent(a)
        agents.append(a)
        
    target_shape = 'CIRCLE'
    
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2548_standing_wave.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "avg_potential", "convergence_score"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            total_potential = 0
            converged_count = 0
            
            for agent in agents:
                # 1. Sense Gradient
                current_pot = potential_field(agent.x, agent.y, target_shape)
                
                # Look at neighbors (Up, Down, Left, Right)
                best_move = (0,0)
                min_pot = current_pot
                
                moves = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]
                random.shuffle(moves)
                
                for dx, dy in moves:
                    nx, ny = agent.x + dx, agent.y + dy
                    # Bounds check
                    if 0 <= nx <= 100 and 0 <= ny <= 100:
                        p = potential_field(nx, ny, target_shape)
                        if p < min_pot:
                            min_pot = p
                            best_move = (dx, dy)
                            
                # 2. Move Downhill
                if best_move != (0,0):
                    agent.move(best_move[0], best_move[1])
                    
                total_potential += min_pot
                if min_pot < 1.0: converged_count += 1
                
            avg_pot = total_potential / len(agents)
            writer.writerow([tick, f"{avg_pot:.2f}", converged_count])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: AvgPot={avg_pot:.2f} Converged={converged_count}/{len(agents)}")
                
            if converged_count == len(agents):
                print("✨ RESONANCE ACHIEVED.")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_standing_wave_experiment()