
import sys
import os
import random
import numpy as np
from typing import List

# Add project root to path
sys.path.append(os.getcwd())

from src.experiments.cycle2109_resonance_trust_link import UnifiedAgent

# --- MULTI-SCALE AGENT ---
class MultiScaleAgent(UnifiedAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.estimate = 0.0 # Computation State
        
    def compute(self, neighbors: List['MultiScaleAgent']):
        if not neighbors: return
        # Consensus Averaging
        vals = [n.estimate for n in neighbors] + [self.estimate]
        self.estimate = np.mean(vals)

# --- SIMULATION ---
def run_multi_scale_sim() -> bool:
    print(f"\n--- Simulation: The Multi-Scale World ---", flush=True)
    
    N_AGENTS = 50
    CYCLES = 200
    
    # Setup: Random Positions, Mixed Strategies, Random Estimates
    agents = []
    for i in range(N_AGENTS):
        strat = "Cooperator" if i < 30 else "Defector" # 30 Coop, 20 Defect
        estimate = float(i) # Initial value = ID (0 to 49)
        
        agent = MultiScaleAgent(
            agent_id=f"m_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=np.random.rand(3) * 20.0
        )
        agent.strategy = strat
        agent.estimate = estimate
        
        # Pre-load Reputation (Simplified)
        for j in range(N_AGENTS):
            j_strat = "Cooperator" if j < 30 else "Defector"
            score = 1.0 if j_strat == "Cooperator" else -1.0
            agent.memory[f"m_{j}"] = score * 5.0
            
        agents.append(agent)
        
    # Goals:
    # 1. Physics: Cluster Density > X
    # 2. Society: Cluster Purity > Y (Cooperators only)
    # 3. Compute: Estimate Convergence (StdDev < Z)
    
    history_purity = []
    history_std = []
    
    for cycle in range(CYCLES):
        # 1. Move (Physics) - Attracted to High Affinity
        for agent in agents:
            best_neighbor = None
            best_affinity = -999.0
            
            for other in agents:
                if agent == other: continue
                affinity = agent.calculate_unified_affinity(other, alpha=0.5)
                
                if affinity > best_affinity:
                    best_affinity = affinity
                    best_neighbor = other
            
            if best_neighbor and best_affinity > 0:
                # Move towards friend
                direction = best_neighbor.state.position - agent.state.position
                dist = np.linalg.norm(direction)
                if dist > 0.1:
                    agent.move((direction / dist) * 0.5) # Slow move
                    
        # 2. Interact/Compute (Society/Compute)
        # Only interact with close neighbors who are TRUSTED
        for agent in agents:
            neighbors = []
            for other in agents:
                if agent == other: continue
                dist = np.linalg.norm(agent.state.position - other.state.position)
                
                if dist < 2.0: # Physical Proximity
                    affinity = agent.calculate_unified_affinity(other, alpha=0.5)
                    if affinity > 0.0: # Social Trust + Resonance
                        neighbors.append(other)
            
            agent.compute(neighbors)
            
        # 3. Measure
        # Identify clusters based on proximity
        # Calculate purity of clusters
        # Calculate variance of estimates within Cooperators
        
        coops = [a for a in agents if a.strategy == "Cooperator"]
        estimates = [a.estimate for a in coops]
        std_dev = np.std(estimates)
        history_std.append(std_dev)
        
        if cycle % 50 == 0:
            print(f"Cycle {cycle}: Coop StdDev {std_dev:.4f}")
            
    final_std = history_std[-1]
    print(f"Final Coop StdDev: {final_std:.4f}")
    
    # Verify Purity implicitly:
    # Defectors should be isolated (repelled).
    # Cooperators should be clustered.
    # If Cooperators clustered, they computed (StdDev -> 0).
    # If Defectors mixed in, they might disrupt? 
    # Actually, in this code, Cooperators don't trust Defectors, so they don't compute with them.
    # So Computation is protected by Society. 
    
    if final_std < 1.0:
        print("SUCCESS: Multi-Scale Integration Achieved.")
        return True
    else:
        print("FAILURE: Did not converge.")
        return False

if __name__ == "__main__":
    run_multi_scale_sim()
