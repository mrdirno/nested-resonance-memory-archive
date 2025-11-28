"""
Cycle 2548: The Standing Wave (Gate 176)
Experiment: Spatial Resonance Field.
Goal: Verify if agents accumulate in locations where their internal phase matches the spatial phase field.
Hypothesis: Agents will 'meditate' (stay put) at resonant locations and 'forage' (move) at dissonant ones, leading to clustering.
"""

import sys
import os
import math
import csv
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem
from bridge.transcendental_bridge import TranscendentalShapes

def run_standing_wave_experiment():
    print("🌊 CYCLE 2548: THE STANDING WAVE - RESONANCE TRAPPING")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=100, width=100, height=100)
    
    # Seed Agents with specific phases
    print("🎵 Seeding The Frequency...")
    # Group A: Phase 0 (Resonates with Center)
    for i in range(20):
        agent = DigitalLifeform(name=f"Alpha-{i}")
        agent.genome[0] = 0.0 
        agent.x = 10 + i # Start far from center
        agent.y = 10
        env.add_agent(agent)
        
    # Group B: Phase 3.14 (Resonates with Outer Ring)
    for i in range(20):
        agent = DigitalLifeform(name=f"Omega-{i}")
        agent.genome[0] = 0.5 # 0.5 * 2Pi = Pi
        agent.x = 50 + i
        agent.y = 50
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2548_standing_wave.csv"
    
    env.running = True
    duration = 200
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "alpha_dist_center", "omega_dist_center", "meditators"])
        
        print("📝 Running simulation...")
        center = (50, 50)
        
        for tick in range(1, duration + 1):
            env.update()
            
            alphas = [a for a in env.agents if "Alpha" in a.name and a.alive]
            omegas = [a for a in env.agents if "Omega" in a.name and a.alive]
            
            if not alphas and not omegas: break
            
            # Calc average distance from center
            alpha_dist = sum(math.sqrt((a.x-center[0])**2 + (a.y-center[1])**2) for a in alphas) / len(alphas) if alphas else 0
            omega_dist = sum(math.sqrt((a.x-center[0])**2 + (a.y-center[1])**2) for a in omegas) / len(omegas) if omegas else 0
            
            meditators = len([a for a in env.agents if a.intent == 'meditate'])
            
            writer.writerow([tick, alpha_dist, omega_dist, meditators])
            
            if tick % 20 == 0:
                print(f"   Tick {tick}: AlphaDist={alpha_dist:.1f}, OmegaDist={omega_dist:.1f}, Meditators={meditators}")
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_standing_wave_experiment()
