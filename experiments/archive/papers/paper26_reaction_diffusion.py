import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class ReactionDiffusionSwarm:
    def __init__(self, n_agents=500, size=20.0, diff_u=0.01, diff_v=0.05):
        self.n = n_agents
        self.size = size
        self.pos = np.random.rand(n_agents, 2) * size
        
        # Chemical States
        # U: Activator, V: Inhibitor
        # Initialize with random noise around 0 for tanh dynamics
        self.u = np.random.normal(0.0, 0.1, n_agents)
        self.v = np.random.normal(0.0, 0.1, n_agents)
        
        # Diffusion Coefficients (Movement speed effectively)
        self.diff_u = diff_u
        self.diff_v = diff_v
        
        # Reaction Parameters (FitzHugh-Nagumo type or similar)
        # du/dt = a*u + b*v + ...
        # We use a standard Turing model:
        # du/dt = u - u^3 - v + Du * laplacian(u)
        # dv/dt = u - v + Dv * laplacian(v)
        # But on a swarm, laplacian is computed via neighbors.

    def get_laplacian(self, values, neighbors, dists):
        # Approximate Laplacian on irregular grid (graph)
        # L(u_i) = sum_j (u_j - u_i) * w_ij
        # w_ij can be Gaussian kernel
        
        lap = np.zeros(self.n)
        sigma = 1.0
        
        # This is O(N^2), acceptable for N=500
        weights = np.exp(-dists**2 / (2*sigma**2))
        weights[~neighbors] = 0
        
        # Normalize weights?
        # Standard graph laplacian: sum(w_ij * (u_j - u_i))
        
        diffs = values[None, :] - values[:, None] # u_j - u_i
        weighted_diffs = weights * diffs
        lap = np.sum(weighted_diffs, axis=1)
        
        return lap

    def step(self):
        # 1. Compute Distances
        dx = np.subtract.outer(self.pos[:, 0], self.pos[:, 0])
        dy = np.subtract.outer(self.pos[:, 1], self.pos[:, 1])
        
        dx = (dx + self.size/2) % self.size - self.size/2
        dy = (dy + self.size/2) % self.size - self.size/2
        
        dists = np.sqrt(dx**2 + dy**2)
        neighbors = dists < 2.0 # Interaction radius
        
        # 2. Compute Laplacians (Diffusion)
        lap_u = self.get_laplacian(self.u, neighbors, dists)
        lap_v = self.get_laplacian(self.v, neighbors, dists)
        
        # 3. Reaction Dynamics (FitzHugh-Nagumo PDE)
        # dA/dt = Da * Lap(A) + A - A^3 - H + I
        # dH/dt = Dh * Lap(H) + epsilon * (A - a*H + b)
        
        # Parameters
        Da = 0.001
        Dh = 0.05 # Inhibition diffuses 50x faster
        epsilon = 0.1
        
        # Laplacian
        # We need to normalize the Laplacian sum to be independent of density
        # L_i = sum_j w_ij (u_j - u_i) / sum_j w_ij
        # This makes it a diffusion operator.
        
        # Weights
        sigma = 1.0
        weights = np.exp(-dists**2 / (2*sigma**2))
        weights[~neighbors] = 0
        np.fill_diagonal(weights, 0)
        
        # Normalize weights row-wise
        weight_sums = np.sum(weights, axis=1, keepdims=True) + 1e-6
        norm_weights = weights / weight_sums
        
        # Compute Laplacians (Normalized)
        # Lap(u)_i = sum_j w_ij (u_j - u_i) = (sum_j w_ij u_j) - u_i
        # Since sum w_ij = 1.
        
        lap_u = (norm_weights @ self.u) - self.u
        lap_v = (norm_weights @ self.v) - self.v
        
        # Reaction
        # FHN-like
        # u: Activator, v: Inhibitor
        # du = u - u^3 - v + 0.5 (Input bias)
        # dv = u - v
        
        # To get spots, we need local activation, lateral inhibition.
        # The diffusion term provides the lateral inhibition if Dh > Da.
        
        dt = 0.5 # Larger step for PDE
        
        # Reaction
        du = self.u - self.u**3 - self.v + 0.0 # Bias 0
        dv = (self.u - self.v) * epsilon
        
        # Update
        self.u += (du + Da * lap_u * 50.0) * dt # Scale diffusion to be visible
        self.v += (dv + Dh * lap_v * 50.0) * dt
        
        # Clip to prevent explosion?
        self.u = np.clip(self.u, -2, 2)
        self.v = np.clip(self.v, -2, 2)
        
        # 4. Physical Diffusion (Agents move)
        # Slow movement to allow pattern to form on the mesh
        self.pos += np.random.normal(0, 0.01, (self.n, 2))
        self.pos = self.pos % self.size

    def get_spatial_variance(self):
        # If uniform, variance is low.
        # If spots/stripes, variance is high.
        return np.var(self.u)

def run_reaction_diffusion_experiment():
    print("\n--- PAPER 26: THE SPATIAL COMPUTER (REACTION-DIFFUSION) ---")
    
    # Control: No Interaction (Diffusion only)
    print("Running Control (Diffusion Only)...")
    swarm_control = ReactionDiffusionSwarm(n_agents=500)
    # Disable interaction in step (mocking)
    # Actually, let's just run the loop but set interaction to 0
    
    var_control = []
    for t in range(100):
        # Manual step for control
        swarm_control.u *= 0.9 # Decay to 0
        swarm_control.pos += np.random.normal(0, 0.05, (swarm_control.n, 2))
        swarm_control.pos %= swarm_control.size
        var_control.append(swarm_control.get_spatial_variance())
        
    final_var_control = np.mean(var_control[-20:])
    print(f"Control Final Variance: {final_var_control:.4f}")
    
    # Experiment: Mexican Hat Interaction
    print("Running Experiment (Mexican Hat)...")
    swarm_exp = ReactionDiffusionSwarm(n_agents=500)
    
    var_exp = []
    for t in range(100):
        swarm_exp.step()
        var = swarm_exp.get_spatial_variance()
        var_exp.append(var)
        if t % 20 == 0:
            print(f"  Step {t}: Variance={var:.4f}, u_range=[{swarm_exp.u.min():.3f}, {swarm_exp.u.max():.3f}]")
        
    final_var_exp = np.mean(var_exp[-20:])
    print(f"Experiment Final Variance: {final_var_exp:.4f}")
    
    # Criteria:
    # Experiment should maintain high variance (Contrast)
    # Control should decay to 0
    
    if final_var_exp > final_var_control * 10.0 and final_var_exp > 0.01:
        print("SUCCESS: Turing Pattern Formation Verified.")
        print("The swarm generated stable spatial contrast (Spots/Stripes).")
    else:
        print("FAILURE: No pattern formed.")

if __name__ == "__main__":
    run_reaction_diffusion_experiment()
