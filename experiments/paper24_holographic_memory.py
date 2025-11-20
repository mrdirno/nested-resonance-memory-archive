import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class HolographicSwarm:
    def __init__(self, n_agents=400, size=20.0):
        self.n = n_agents
        self.size = size
        self.pos = np.random.rand(n_agents, 2) * size
        self.vel = np.random.randn(n_agents, 2)
        # Normalize velocity
        norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = self.vel / norms
        
        # Virtual Pheromone Field (The "Memory")
        # In a real biological system, this would be environmental modification (stigmergy).
        # Here we simulate it as a grid.
        self.grid_res = 40
        self.pheromone = np.zeros((self.grid_res, self.grid_res))
        
    def update_pheromone(self):
        # Agents deposit pheromone at their location
        decay = 0.95
        self.pheromone *= decay
        
        for i in range(self.n):
            x, y = self.pos[i]
            gx = int((x / self.size) * self.grid_res) % self.grid_res
            gy = int((y / self.size) * self.grid_res) % self.grid_res
            self.pheromone[gx, gy] += 1.0

    def get_field_gradient(self, pos):
        # Calculate gradient of pheromone field at pos to guide agents
        x, y = pos
        gx = int((x / self.size) * self.grid_res) % self.grid_res
        gy = int((y / self.size) * self.grid_res) % self.grid_res
        
        # Simple finite difference
        gx_p = (gx + 1) % self.grid_res
        gx_m = (gx - 1) % self.grid_res
        gy_p = (gy + 1) % self.grid_res
        gy_m = (gy - 1) % self.grid_res
        
        dx = self.pheromone[gx_p, gy] - self.pheromone[gx_m, gy]
        dy = self.pheromone[gx, gy_p] - self.pheromone[gx, gy_m]
        
        return np.array([dx, dy])

    def step(self, mode="TRAINING"):
        # 1. Physics
        
        # Target Velocity
        target_vel = np.zeros((self.n, 2))
        
        if mode == "TRAINING":
            # Train to form a Ring
            # Potential: V(r) = (r - R)^2
            center = np.array([self.size/2, self.size/2])
            R = self.size / 4.0
            
            to_center = center - self.pos
            dists = np.linalg.norm(to_center, axis=1, keepdims=True)
            
            # Force towards radius R
            # If dist > R, move in. If dist < R, move out.
            radial_force = (dists - R) * (to_center / (dists + 1e-6))
            
            # Tangential flow (Rotation)
            tangent = np.stack([-to_center[:,1], to_center[:,0]], axis=1)
            tangent = tangent / (dists + 1e-6)
            
            target_vel = radial_force + 2.0 * tangent
            
        elif mode == "MEMORY":
            # Agents follow the Pheromone Field (Self-Sustaining Structure)
            # They are attracted to high pheromone concentration
            
            for i in range(self.n):
                grad = self.get_field_gradient(self.pos[i])
                # Normalize gradient
                gnorm = np.linalg.norm(grad)
                if gnorm > 1e-6:
                    target_vel[i] = grad / gnorm
                else:
                    # Random walk if no signal
                    target_vel[i] = np.random.randn(2)
                    
        # Update Velocity
        self.vel += 0.1 * target_vel + np.random.normal(0, 0.05, (self.n, 2))
        norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = self.vel / norms
        
        # Move
        self.pos += self.vel * 0.1
        self.pos = self.pos % self.size
        
        # Update Memory (Pheromone)
        self.update_pheromone()

    def lesion(self, fraction=0.5):
        # Remove random agents
        n_remove = int(self.n * fraction)
        keep_indices = np.random.choice(self.n, self.n - n_remove, replace=False)
        
        self.pos = self.pos[keep_indices]
        self.vel = self.vel[keep_indices]
        self.n = len(self.pos)
        print(f"Lesioned Swarm: Removed {n_remove} agents. Remaining: {self.n}")

    def get_shape_error(self):
        # Measure deviation from ideal Ring
        center = np.array([self.size/2, self.size/2])
        R = self.size / 4.0
        
        dists = np.linalg.norm(self.pos - center, axis=1)
        errors = np.abs(dists - R)
        mean_error = np.mean(errors)
        
        # Normalize by R
        return mean_error / R

def run_holographic_memory_experiment():
    print("\n--- PAPER 24: THE HOLOGRAPHIC MEMORY (DISTRIBUTED STORAGE) ---")
    
    swarm = HolographicSwarm(n_agents=400)
    
    print("Phase 1: Training (Encoding Pattern)...")
    for t in range(200):
        swarm.step(mode="TRAINING")
        
    error_trained = swarm.get_shape_error()
    print(f"Trained Shape Error: {error_trained:.4f}")
    
    print("\nPhase 2: Lesioning (Removing 50% of Agents)...")
    swarm.lesion(fraction=0.5)
    
    print("\nPhase 3: Recall (Testing Persistence)...")
    # Run in MEMORY mode (Self-Sustaining via Pheromone)
    # Without the external training force
    
    errors = []
    for t in range(100):
        swarm.step(mode="MEMORY")
        errors.append(swarm.get_shape_error())
        
    final_error = np.mean(errors[-20:])
    print(f"Final Shape Error (Holographic Recall): {final_error:.4f}")
    
    # Control Baseline (Random Distribution)
    # If agents were random, mean dist from center is approx size/3?
    # Actually, for uniform distribution in square, mean dist to center is complicated but > 0.
    # Let's just say if error is low, it retained the ring.
    
    # Random points error
    rand_pos = np.random.rand(200, 2) * 20.0
    center = np.array([10.0, 10.0])
    R = 5.0
    rand_dists = np.linalg.norm(rand_pos - center, axis=1)
    rand_error = np.mean(np.abs(rand_dists - R)) / R
    print(f"Random Baseline Error: {rand_error:.4f}")
    
    if final_error < 0.3 and final_error < rand_error * 0.6:
        print("SUCCESS: Holographic Memory Verified.")
        print("The swarm maintained the pattern despite 50% agent loss.")
    else:
        print("FAILURE: Pattern collapsed.")

if __name__ == "__main__":
    run_holographic_memory_experiment()
