#!/usr/bin/env python3
"""
Experiment: Cycle 2622 - The Optimizer
Goal: Test an improved flocking algorithm (Boids-like separation) for HiveAgents.
"""

import sys
import math
import random
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

class BoidAgent(HiveAgent):
    """
    Optimized Agent with Separation Logic to avoid crowding.
    """
    def update(self, target_pos: Vector2, neighbors: list = None) -> None:
        # 1. Standard Seek
        dist_to_target = math.sqrt((self.position.x - target_pos.x)**2 + 
                                   (self.position.y - target_pos.y)**2)
        
        msg_out = None
        if dist_to_target < self.sensor_range:
            if not self.known_target:
                self.known_target = target_pos
                # (Message generation handled by caller in this sim)

        # 2. Boid Logic (Separation)
        separation = Vector2(0, 0)
        if neighbors:
            for n in neighbors:
                dist = math.sqrt((self.position.x - n.position.x)**2 + 
                                 (self.position.y - n.position.y)**2)
                if dist < 5.0 and dist > 0: # Too close
                    push = (self.position - n.position).normalize()
                    separation = separation + push
        
        # 3. Combine Forces
        if self.known_target:
            goal_dir = (self.known_target - self.position).normalize()
            # 80% Goal, 20% Separation
            self.velocity = goal_dir.scale(0.8) + separation.scale(0.2)
            self.velocity = self.velocity.normalize()
        else:
            # Random walk
            self.velocity = (self.velocity + Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))).normalize()

        self.position = self.position + self.velocity.scale(self.speed)
        return msg_out

def run_optimization_test():
    print("Cycle 2622: The Optimizer - Boids Logic Test")
    
    target = Vector2(50, 50)
    # Crowd them
    agents = [BoidAgent(f"boid_{i}", Vector2(10 + random.uniform(-1,1), 10 + random.uniform(-1,1))) for i in range(5)]
    
    # Give knowledge
    for a in agents: a.known_target = target
    
    print("Simulating crowding...")
    for step in range(10):
        for i, agent in enumerate(agents):
            neighbors = [a for j, a in enumerate(agents) if i != j]
            agent.update(target, neighbors)
            
    # Check spread
    # If they separated, variance in position should increase or at least not be 0
    # Simple check: are they all on top of each other?
    
    positions = [a.position for a in agents]
    avg_x = sum(p.x for p in positions) / len(positions)
    avg_y = sum(p.y for p in positions) / len(positions)
    
    # Calculate spread (average distance from center)
    spread = sum(math.sqrt((p.x - avg_x)**2 + (p.y - avg_y)**2) for p in positions) / len(positions)
    
    print(f"Final Crowd Spread: {spread:.2f}")
    
    if spread > 1.0:
        print("SUCCESS: Agents maintained separation while moving.")
    else:
        print("FAILURE: Agents collapsed into a singularity.")
        sys.exit(1)

if __name__ == "__main__":
    run_optimization_test()
