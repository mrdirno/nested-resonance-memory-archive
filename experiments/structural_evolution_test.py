import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# --- EXPERIMENT: STRUCTURAL EVOLUTION (The Architect Engine) ---

class KuramotoNetwork:
    def __init__(self, n_agents=50, coupling=1.0, dt=0.05):
        self.n = n_agents
        self.K = coupling
        self.dt = dt
        self.phases = np.random.uniform(0, 2*np.pi, n_agents)
        self.omegas = np.random.normal(0, 0.5, n_agents) # Natural frequencies
        
        # Initialize Random Graph (Erdos-Renyi)
        self.adj = np.random.choice([0, 1], size=(n_agents, n_agents), p=[0.9, 0.1])
        np.fill_diagonal(self.adj, 0)
        # Make symmetric
        self.adj = np.maximum(self.adj, self.adj.T)
        
    def get_order_parameter(self):
        z = np.mean(np.exp(1j * self.phases))
        return np.abs(z)
        
    def step(self, dynamic_topology=False):
        # 1. Calculate Interactions
        # sin(theta_j - theta_i)
        diffs = self.phases[None, :] - self.phases[:, None]
        interactions = np.sin(diffs)
        
        # Apply Adjacency
        coupled_interactions = np.sum(self.adj * interactions, axis=1)
        
        # 2. Update Phases
        d_theta = self.omegas + (self.K / self.n) * coupled_interactions
        self.phases += d_theta * self.dt
        self.phases = np.mod(self.phases, 2*np.pi)
        
        # 3. Structural Evolution (Hebbian Rewiring)
        if dynamic_topology:
            # "Fire together, wire together" -> "Sync together, link together"
            # Measure pairwise synchronization: cos(theta_i - theta_j)
            # Close to 1 = Synced. Close to -1 = Anti-synced.
            sync_matrix = np.cos(diffs)
            
            # Rewiring Rule:
            # If highly synced (> 0.9) AND not connected -> Add Link (0.01 prob)
            # If desynced (< 0.0) AND connected -> Remove Link (0.01 prob)
            
            # Add Links
            candidates_add = (sync_matrix > 0.9) & (self.adj == 0)
            # Randomly select some to add
            add_mask = (np.random.random(self.adj.shape) < 0.01) & candidates_add
            self.adj[add_mask] = 1
            
            # Remove Links
            candidates_remove = (sync_matrix < 0.0) & (self.adj == 1)
            remove_mask = (np.random.random(self.adj.shape) < 0.01) & candidates_remove
            self.adj[remove_mask] = 0
            
            # Enforce Symmetry & No Self-Loops
            self.adj = np.maximum(self.adj, self.adj.T)
            np.fill_diagonal(self.adj, 0)

def run_simulation(mode, steps=200):
    net = KuramotoNetwork(n_agents=50, coupling=2.0) # High coupling to allow sync
    history_r = []
    
    dynamic = (mode == "DYNAMIC")
    
    for t in range(steps):
        net.step(dynamic_topology=dynamic)
        r = net.get_order_parameter()
        history_r.append(r)
        
    return history_r

def structural_evolution_test():
    print("\n--- PAPER 19: STRUCTURAL EVOLUTION TEST ---")
    
    # Run Static Topology
    print("Running Static Topology (Fixed Network)...")
    hist_static = run_simulation("STATIC")
    final_r_static = np.mean(hist_static[-20:])
    print(f"  Static Final R: {final_r_static:.4f}")
    
    # Run Dynamic Topology
    print("Running Dynamic Topology (Evolving Network)...")
    hist_dynamic = run_simulation("DYNAMIC")
    final_r_dynamic = np.mean(hist_dynamic[-20:])
    print(f"  Dynamic Final R: {final_r_dynamic:.4f}")
    
    # Comparison
    print(f"\nImprovement: {final_r_dynamic - final_r_static:.4f}")
    
    if final_r_dynamic > final_r_static + 0.05: # Significant improvement
        print("\nSUCCESS: Evolving Network synchronized better.")
    else:
        print("\nFAILURE: Structural Evolution did not improve synchronization.")

if __name__ == "__main__":
    structural_evolution_test()
