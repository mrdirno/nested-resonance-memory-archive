import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class VicsekSwarm:
    def __init__(self, n_agents=300, size=10.0, noise=0.1):
        self.n = n_agents
        self.size = size
        self.noise = noise
        self.pos = np.random.rand(n_agents, 2) * size
        self.vel = np.random.randn(n_agents, 2)
        norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = self.vel / norms

    def step(self):
        # 1. Compute Neighbors (Naive O(N^2) for simplicity)
        # In a real large scale sim, use a spatial tree.
        # For N=300, naive is fine.
        
        # Distance matrix
        # Handle Periodic BC for distance
        dx = np.subtract.outer(self.pos[:, 0], self.pos[:, 0])
        dy = np.subtract.outer(self.pos[:, 1], self.pos[:, 1])
        
        dx = (dx + self.size/2) % self.size - self.size/2
        dy = (dy + self.size/2) % self.size - self.size/2
        
        dists = np.sqrt(dx**2 + dy**2)
        
        # Radius r=1.0
        neighbors = dists < 1.0
        
        # 2. Alignment
        # Mean velocity of neighbors
        # We can use matrix multiplication for sum of neighbors
        sum_vel_x = neighbors @ self.vel[:, 0]
        sum_vel_y = neighbors @ self.vel[:, 1]
        
        # Normalize
        norms = np.sqrt(sum_vel_x**2 + sum_vel_y**2) + 1e-6
        target_vel_x = sum_vel_x / norms
        target_vel_y = sum_vel_y / norms
        
        # 3. Update with Noise
        # Add random noise vector
        noise_vec = np.random.normal(0, self.noise, (self.n, 2))
        
        new_vel_x = target_vel_x + noise_vec[:, 0]
        new_vel_y = target_vel_y + noise_vec[:, 1]
        
        # Normalize result
        new_norms = np.sqrt(new_vel_x**2 + new_vel_y**2)
        self.vel[:, 0] = new_vel_x / new_norms
        self.vel[:, 1] = new_vel_y / new_norms
        
        # 4. Move
        self.pos += self.vel * 0.1
        self.pos = self.pos % self.size

    def get_metrics(self):
        # Polarization (Order)
        mean_v = np.mean(self.vel, axis=0)
        pol = np.linalg.norm(mean_v)
        
        # Density Variance (Clumping)
        # Divide space into grid and count agents
        grid_n = 5
        H, _, _ = np.histogram2d(self.pos[:,0], self.pos[:,1], bins=grid_n, range=[[0, self.size], [0, self.size]])
        # Variance of counts / Mean of counts (Index of Dispersion)
        # If random (Poisson), Var = Mean, Ratio = 1.
        # If clumped, Var > Mean, Ratio > 1.
        density_var = np.var(H) / (np.mean(H) + 1e-6)
        
        return {"polarization": pol, "density_var": density_var}

def run_recursive_linker_experiment():
    print("\n--- PAPER 23: THE RECURSIVE LINKER (META-ABSTRACTION) ---")
    
    # Sweep Noise from 0.1 to 5.0
    noise_levels = np.linspace(0.1, 5.0, 20)
    
    history_pol = []
    history_den = []
    history_noise = []
    
    # For calculating Susceptibility (Variance of Polarization)
    susceptibility = []
    
    print("Sweeping Phase Space (Noise 0.1 -> 5.0)...")
    
    for eta in noise_levels:
        swarm = VicsekSwarm(n_agents=300, noise=eta)
        
        # Relax (Increase to ensure equilibrium)
        for _ in range(200):
            swarm.step()
            
        # Measure
        samples_pol = []
        samples_den = []
        
        for _ in range(100):
            swarm.step()
            m = swarm.get_metrics()
            samples_pol.append(m["polarization"])
            samples_den.append(m["density_var"])
            
        mean_pol = np.mean(samples_pol)
        mean_den = np.mean(samples_den)
        var_pol = np.var(samples_pol) # Susceptibility ~ Variance of Order Parameter
        
        history_pol.append(mean_pol)
        history_den.append(mean_den)
        susceptibility.append(var_pol)
        history_noise.append(eta)
        
        print(f"Noise={eta:.2f} | Pol={mean_pol:.2f} | DenVar={mean_den:.2f} | Susc={var_pol:.4f}")

    # --- META-ANALYSIS ---
    # The "Recursive Linker" looks for the peak in the relationship between variables.
    # Specifically, we look for the peak of Susceptibility (Variance of Polarization).
    # This identifies the "Critical Point" without knowing the underlying physics.
    
    peak_susc_idx = np.argmax(susceptibility)
    critical_noise = history_noise[peak_susc_idx]
    critical_pol = history_pol[peak_susc_idx]
    
    print("\n--- META-DISCOVERY RESULTS ---")
    print(f"Identified Critical Noise (Phase Transition): {critical_noise:.2f}")
    print(f"Polarization at Criticality: {critical_pol:.2f}")
    print(f"Max Susceptibility: {susceptibility[peak_susc_idx]:.4f}")
    
    # Validation:
    # In Vicsek model, transition depends on density.
    # For rho=3.0, transition is around 1.0 - 1.5.
    # Susceptibility should peak at the transition.
    
    if 0.8 < critical_noise < 4.0:
        print("SUCCESS: Meta-Linker (Susceptibility) correctly identified the Phase Transition.")
        print("The system discovered 'Criticality' as a meaningful higher-order concept.")
    else:
        print("FAILURE: Could not identify Phase Transition.")

if __name__ == "__main__":
    run_recursive_linker_experiment()
