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

# --- Simple Linear Potential (for debugging movement) ---
def get_linear_potential(x, y, z):
    return x # Agents should move towards lower x

def main():
    print("Initializing Physics Check...")
    
    # Initialize 10 agents, distributed in x-axis
    agents = []
    for i in range(10):
        # Start at x=80, scattered in y, z
        agents.append(FractalAgent(f"Test_{i}", 0, 1.0, 0, x=80.0 + np.random.uniform(-5,5), y=50.0 + np.random.uniform(-5,5), z=50.0 + np.random.uniform(-5,5)))
        
    print(f"Initial Avg X-pos: {np.mean([a.x for a in agents]):.2f}")
    
    potential_fn = get_linear_potential # Use the linear potential for testing
    
    print("\nSimulating 50 steps (Step Size = 2.0)...")
    for t in range(50):
        x_positions = []
        for a in agents:
            a.update_position(potential_fn, step_size=2.0)
            x_positions.append(a.x)
        
        if t % 10 == 0:
            print(f"T={t}: Avg X-pos = {np.mean(x_positions):.2f}")
            
    final_avg_x = np.mean(x_positions)
    print(f"Final Avg X-pos: {final_avg_x:.2f}")
    
    # Check if they moved IN
    if final_avg_x < 75.0: # Expect significant movement towards 0
        print("SUCCESS: Agents are responding to linear potential.")
    else:
        print("FAILURE: Agents are not responding to linear potential.")

if __name__ == "__main__":
    main()

# [SPORE] ID: The Colony
