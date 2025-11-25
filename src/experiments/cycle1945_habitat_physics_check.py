#!/usr/bin/env python3
"""
CYCLE 1945: HABITAT PHYSICS CHECK

Verifying that the 'Transcendental Habitat' potential actually moves agents.
We will initialize agents at radius R=40 and track their distance to center
over time. They should fall into the ring at R~=6 (first Bessel peak/trough).
"""
import sys, numpy as np, math
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/src')

from core.fractal_agent import FractalAgent, RealityInterface

# Copy potential logic from C1944
def get_ring_potential(x, y, z, scale=0.5, center=(50,50,50)):
    r = math.sqrt((x - center[0])**2 + (y - center[1])**2)
    return -math.cos(r * scale)

def main():
    print("Initializing Physics Check...")
    
    # Initialize 10 agents at Radius 40
    agents = []
    for i in range(10):
        angle = (i / 10) * 2 * math.pi
        x = 50 + 40 * math.cos(angle)
        y = 50 + 40 * math.sin(angle)
        agents.append(FractalAgent(f"Test_{i}", 0, 1.0, 0, x, y))
        
    print(f"Initial Avg Radius: {np.mean([math.sqrt((a.x-50)**2 + (a.y-50)**2) for a in agents]):.2f}")
    
    potential_fn = lambda x, y, z: get_ring_potential(x, y, z)
    
    print("\nSimulating 50 steps (Step Size = 2.0)...")
    for t in range(50):
        dists = []
        for a in agents:
            a.update_position(potential_fn, step_size=2.0)
            d = math.sqrt((a.x-50)**2 + (a.y-50)**2)
            dists.append(d)
        
        if t % 10 == 0:
            print(f"T={t}: Avg Radius = {np.mean(dists):.2f}")
            
    print(f"Final Avg Radius: {np.mean(dists):.2f}")
    
    # Check if they moved IN
    if np.mean(dists) < 35.0:
        print("SUCCESS: Agents are falling into the well.")
    else:
        print("FAILURE: Agents are not responding to gravity.")

if __name__ == "__main__":
    main()
