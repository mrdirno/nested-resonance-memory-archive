"""
Cycle 2547: The Harmonic Convergence (Gate 175)
Experiment: Collective Resonance.
Goal: Observe if agents with similar phases cluster together spatially.
Hypothesis: If resonance drives behavior, agents with similar phases might end up in similar locations due to shared responses to environmental signals.
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

def run_convergence_experiment():
    print("🌌 CYCLE 2547: THE HARMONIC CONVERGENCE - PHASE CLUSTERING")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=50, width=100, height=100)
    
    # Seed Agents with random phases
    print("🎵 Seeding The Swarm...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Resonator-{i}")
        # Random phase via Genome[0]
        agent.genome[0] = i / 50.0 # Evenly distributed phases 0.0 to 1.0
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2547_convergence.csv"
    
    env.running = True
    duration = 200
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "avg_dist_similar_phase", "avg_dist_dissimilar_phase"])
        
        print("📝 Running simulation...")
        for tick in range(1, duration + 1):
            env.update()
            
            if tick % 10 == 0:
                # Calculate spatial clustering
                # Metric: Average distance between agents with phase diff < 0.1
                # vs Average distance between agents with phase diff > 0.5
                
                dist_similar = []
                dist_dissimilar = []
                
                agents = [a for a in env.agents if a.alive]
                if len(agents) < 2: break
                
                for i in range(len(agents)):
                    for j in range(i+1, len(agents)):
                        a1 = agents[i]
                        a2 = agents[j]
                        
                        # Spatial Distance
                        dist = math.sqrt((a1.x - a2.x)**2 + (a1.y - a2.y)**2)
                        
                        # Phase Distance (Circular)
                        p1 = a1.genome[0]
                        p2 = a2.genome[0]
                        phase_diff = abs(p1 - p2)
                        if phase_diff > 0.5: phase_diff = 1.0 - phase_diff
                        
                        if phase_diff < 0.1:
                            dist_similar.append(dist)
                        elif phase_diff > 0.4:
                            dist_dissimilar.append(dist)
                            
                avg_sim = sum(dist_similar) / len(dist_similar) if dist_similar else 0
                avg_dissim = sum(dist_dissimilar) / len(dist_dissimilar) if dist_dissimilar else 0
                
                writer.writerow([tick, avg_sim, avg_dissim])
                print(f"   Tick {tick}: Dist(Similar)={avg_sim:.1f}, Dist(Dissim)={avg_dissim:.1f}")
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_convergence_experiment()
