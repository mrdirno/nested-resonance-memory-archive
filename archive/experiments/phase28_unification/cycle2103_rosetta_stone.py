
import sys
import os
import numpy as np
from typing import Callable, List

# Add project root to path
sys.path.append(os.getcwd())

class UniversalAgent:
    def __init__(self, agent_id: str, state: np.ndarray):
        self.id = agent_id
        self.state = state # Position, Opinion, Estimate
        
    def update(self, potential_gradient: np.ndarray, noise: float = 0.01):
        self.state -= potential_gradient # Gradient Descent
        self.state += np.random.randn(*self.state.shape) * noise # Thermal Noise

class UniversalSimulator:
    def __init__(self, domain: str, potential_fn: Callable[[np.ndarray], np.ndarray]):
        self.domain = domain
        self.potential_fn = potential_fn # Returns gradient
        self.agents = [UniversalAgent(f"a_{i}", np.random.rand(2) * 10.0) for i in range(10)]
        
    def step(self):
        for agent in self.agents:
            grad = self.potential_fn(agent.state)
            agent.update(grad)
            
    def status(self):
        avg_state = np.mean([a.state for a in self.agents], axis=0)
        std_state = np.std([a.state for a in self.agents], axis=0)
        return f"{self.domain}: Avg {avg_state}, Std {std_state}"

# --- POTENTIAL FUNCTIONS ---

def potential_matter(state: np.ndarray) -> np.ndarray:
    # Gorkov Potential: Attract to integer nodes (0, 5, 10)
    # Gradient of sin^2(x) is sin(2x)
    return np.sin(state * np.pi / 2.5) * 0.1 # Forces particles to 0, 5, 10

def potential_society(state: np.ndarray) -> np.ndarray:
    # Social Stress: Attract to center (Cooperation) to avoid "Harsh Winter" edges
    # Simple quadratic bowl: 0.01 * (x - 5)
    center = np.array([5.0, 5.0])
    return (state - center) * 0.05

def potential_computation(state: np.ndarray) -> np.ndarray:
    # Error Function: Minimize distance to Target (e.g., 8.0, 2.0)
    target = np.array([8.0, 2.0])
    return (state - target) * 0.1

# --- DEMONSTRATION ---

def run_rosetta_stone():
    print("MOG ONLINE: Cycle 2103 - The Rosetta Stone\n")
    
    sims = [
        UniversalSimulator("MATTER (Levitation)", potential_matter),
        UniversalSimulator("SOCIETY (Cooperation)", potential_society),
        UniversalSimulator("COMPUTE (Optimization)", potential_computation)
    ]
    
    print("--- INITIAL STATE ---")
    for sim in sims: print(sim.status())
    
    print("\n--- EVOLVING (100 Steps) ---")
    for _ in range(100):
        for sim in sims: sim.step()
        
    print("\n--- FINAL STATE ---")
    for sim in sims: print(sim.status())
    
    print("\nCONCLUSION: The same code drove three different realities.")

if __name__ == "__main__":
    run_rosetta_stone()
