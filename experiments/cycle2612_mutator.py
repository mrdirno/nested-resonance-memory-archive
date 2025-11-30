#!/usr/bin/env python3
"""
Experiment: Cycle 2612 - The Mutator
Goal: Demonstrate genetic drift/mutation in agent parameters over time.
"""

import sys
import random
import statistics
from pathlib import Path
from typing import List

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

class MutatingAgent(HiveAgent):
    def __init__(self, agent_id: str, start_pos: Vector2):
        super().__init__(agent_id, start_pos)
        # Base params from parent: speed=4.0, sensor_range=20.0
        # We allow them to drift

    def mutate(self, rate: float = 0.1):
        """Randomly adjust parameters."""
        # Mutate Speed
        if random.random() < 0.5:
            change = random.uniform(-rate, rate)
            self.speed = max(0.5, self.speed + change)
            
        # Mutate Sensor Range
        if random.random() < 0.5:
            change = random.uniform(-rate, rate)
            self.sensor_range = max(5.0, self.sensor_range + change)

def run_evolution():
    print("Cycle 2612: The Mutator - Evolution Start")
    
    population = [MutatingAgent(f"gen0_{i}", Vector2(0,0)) for i in range(10)]
    
    print(f"Initial Speed: {population[0].speed}")
    print(f"Initial Range: {population[0].sensor_range}")
    
    generations = 50
    
    history_speed = []
    history_range = []
    
    for gen in range(generations):
        speeds = []
        ranges = []
        
        for agent in population:
            agent.mutate(rate=0.5) # High mutation for demo
            speeds.append(agent.speed)
            ranges.append(agent.sensor_range)
            
        avg_speed = statistics.mean(speeds)
        avg_range = statistics.mean(ranges)
        
        history_speed.append(avg_speed)
        history_range.append(avg_range)
        
        if gen % 10 == 0:
            print(f"Gen {gen}: AvgSpeed={avg_speed:.2f}, AvgRange={avg_range:.2f}")

    print(f"\nFinal Generation ({generations}):")
    print(f"Avg Speed: {history_speed[-1]:.2f} (Start: 4.0)")
    print(f"Avg Range: {history_range[-1]:.2f} (Start: 20.0)")
    
    # Check for divergence
    speed_variance = statistics.variance([a.speed for a in population])
    print(f"Speed Variance: {speed_variance:.4f}")
    
    if speed_variance > 0.1:
        print("SUCCESS: Population parameters have drifted/diversified.")
    else:
        print("FAILURE: Little to no mutation observed.")
        sys.exit(1)

if __name__ == "__main__":
    run_evolution()
