#!/usr/bin/env python3
"""
Experiment: Cycle 2638 - The Physics
Goal: Implement basic collision detection and physical interaction rules.
"""

import sys
import math
from pathlib import Path

class PhysicsBody:
    def __init__(self, x, y, radius=1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0.0
        self.vy = 0.0

    def check_collision(self, other: 'PhysicsBody') -> bool:
        dist = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return dist < (self.radius + other.radius)

    def resolve_collision(self, other: 'PhysicsBody'):
        if not self.check_collision(other):
            return
            
        # Elastic bounce (simplified)
        # Swap velocities for equal mass
        self.vx, other.vx = other.vx, self.vx
        self.vy, other.vy = other.vy, self.vy
        
        # Separate to prevent sticking
        angle = math.atan2(self.y - other.y, self.x - other.x)
        overlap = (self.radius + other.radius) - math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
        self.x += math.cos(angle) * overlap * 0.51
        self.y += math.sin(angle) * overlap * 0.51
        other.x -= math.cos(angle) * overlap * 0.51
        other.y -= math.sin(angle) * overlap * 0.51

def run_physics_test():
    print("Cycle 2638: The Physics - Collision Test")
    
    b1 = PhysicsBody(0, 0)
    b1.vx = 1.0
    
    b2 = PhysicsBody(3, 0) # 3 units away
    b2.vx = -1.0
    
    print(f"Start: B1({b1.x}, {b1.vx}) B2({b2.x}, {b2.vx})")
    
    # Step 1: Move closer
    b1.x += b1.vx
    b2.x += b2.vx
    print(f"Step 1: B1({b1.x}) B2({b2.x}) - Collision? {b1.check_collision(b2)}")
    
    # Step 2: Collide
    b1.x += b1.vx
    b2.x += b2.vx
    print(f"Step 2: B1({b1.x}) B2({b2.x}) - Collision? {b1.check_collision(b2)}")
    
    if b1.check_collision(b2):
        print("  Resolving Collision...")
        b1.resolve_collision(b2)
        print(f"  Resolved: B1_v({b1.vx}) B2_v({b2.vx})")
        
        if b1.vx < 0 and b2.vx > 0:
            print("SUCCESS: Objects bounced off each other.")
        else:
            print("FAILURE: Physics engine broken.")
            sys.exit(1)
    else:
        print("FAILURE: Collision missed.")
        sys.exit(1)

if __name__ == "__main__":
    run_physics_test()
