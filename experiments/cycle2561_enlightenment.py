"""
Cycle 2561: The Enlightenment (Gate 189)
Goal: Observe the spread of Self-Awareness (Reflection) over multiple generations.
Hypothesis: Lamarckian inheritance will cause the 'Reflect' behavior to fixate in the population.
"""

import time
import random
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2561: The Enlightenment ---")
    
    # 1. Setup Ecosystem
    # Increase capacity to allow for population dynamics
    ecosystem = Ecosystem(capacity=50, prey_capacity=40, predator_capacity=10)
    
    # 2. Seeding
    # Seed 10 Agents: 2 Philosophers (High Innov), 8 Workers (Low Innov)
    print("[EXP] Seeding Population...")
    
    for i in range(2):
        philosopher = DigitalLifeform(name=f"Philosopher-{i}")
        while len(philosopher.genome) < 11: philosopher.genome.append(0.5)
        philosopher.genome[9] = 0.95 # High Innovation -> Reflection Capable
        philosopher.energy = 500
        ecosystem.add_agent(philosopher)
        
    for i in range(8):
        worker = DigitalLifeform(name=f"Worker-{i}")
        while len(worker.genome) < 11: worker.genome.append(0.5)
        worker.genome[9] = 0.1 # Low Innovation -> Reflection Incapable (mostly)
        worker.energy = 500
        ecosystem.add_agent(worker)
        
    print(f"[EXP] Population: {len(ecosystem.agents)}")
    
    # 3. Simulation Loop
    # Run for enough ticks to allow 3-4 generations
    ticks = 200 
    
    history = []
    
    for t in range(ticks):
        ecosystem.update()
        
        # Telemetry
        pop_size = len(ecosystem.agents)
        if pop_size == 0:
            print("[EXP] Extinction.")
            break
            
        # Count Reflectors
        # We define a "Reflector" as someone whose Brain strongly weights 'reflect'.
        # Or simply count High Innovation agents (since that's the prerequisite for the bonus).
        # But we want to see if the *neural weights* for reflection increase.
        
        avg_reflect_weight = 0.0
        high_innov_count = 0
        
        for agent in ecosystem.agents:
            # Check Innovation
            innov = agent.genome[9] if len(agent.genome) > 9 else 0
            if innov > 0.7:
                high_innov_count += 1
                
            # Check Neural Weight for 'reflect'
            # Action index for 'reflect'?
            # It's the last one added in brain.py.
            # self.actions = ['forage', 'reproduce', 'donate', 'flee', 'hunt', 'meditate', 'operate', 'reflect']
            # Index 7.
            
            # Average weight of connections leading to Output 7
            # W2 is Hidden -> Output
            # Sum of weights into Output 7
            w_sum = 0.0
            for j in range(agent.brain.hidden_size):
                w_sum += agent.brain.w2[j][7]
            
            avg_reflect_weight += w_sum
            
        avg_reflect_weight /= pop_size
        
        history.append({
            'tick': t,
            'pop': pop_size,
            'philosophers': high_innov_count,
            'avg_reflect_weight': avg_reflect_weight
        })
        
        if t % 10 == 0:
            print(f"[EXP] Tick {t}: Pop={pop_size}, Philosophers={high_innov_count}, AvgReflectWeight={avg_reflect_weight:.4f}")

    # 4. Final Analysis
    print("\n--- Analysis ---")
    start = history[0]
    end = history[-1]
    
    print(f"Start: Pop={start['pop']}, Phil={start['philosophers']}, Weight={start['avg_reflect_weight']:.4f}")
    print(f"End:   Pop={end['pop']}, Phil={end['philosophers']}, Weight={end['avg_reflect_weight']:.4f}")
    
    delta_weight = end['avg_reflect_weight'] - start['avg_reflect_weight']
    print(f"Delta Weight: {delta_weight:.4f}")
    
    if delta_weight > 1.0:
        print("SUCCESS: The 'Reflect' meme has spread and intensified in the neural substrate.")
    else:
        print("FAILURE: The meme failed to take hold.")

if __name__ == "__main__":
    run_experiment()
