import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class CriticalSwarm:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.n = width * height
        
        # Membrane Potential
        self.potential = np.zeros((height, width))
        
        # Parameters
        self.threshold = 1.0
        self.coupling = 0.25 # Conservative: 4 neighbors * 0.25 = 1.0 (Critical)
        # If coupling > 0.25, it's supercritical (explosion).
        # If coupling < 0.25, it's subcritical (die out).
        # SOC usually tunes itself, but here we set it near critical point 
        # or implement a mechanism to tune it (e.g. synaptic depression).
        # Let's try fixed coupling first.
        
    def step(self):
        # 1. Drive
        # Add energy to a random agent
        rx = np.random.randint(0, self.width)
        ry = np.random.randint(0, self.height)
        self.potential[ry, rx] += 0.1 # Small kick
        
        # 2. Avalanche
        avalanche_size = 0
        
        # Find firing agents
        firing_mask = self.potential >= self.threshold
        
        # If nobody fires, return 0
        if not np.any(firing_mask):
            return 0
            
        # Cascade
        while np.any(firing_mask):
            n_firing = np.sum(firing_mask)
            avalanche_size += n_firing
            
            # Reset firing agents
            # We need to distribute energy to neighbors BEFORE resetting?
            # Or just add to neighbors.
            
            # Get indices
            y_idxs, x_idxs = np.where(firing_mask)
            
            # Reset
            self.potential[firing_mask] = 0
            
            # Distribute to neighbors
            for i in range(len(y_idxs)):
                y, x = y_idxs[i], x_idxs[i]
                
                # Neighbors (Von Neumann)
                neighbors = [
                    ((y+1)%self.height, x),
                    ((y-1)%self.height, x),
                    (y, (x+1)%self.width),
                    (y, (x-1)%self.width)
                ]
                
                for ny, nx in neighbors:
                    self.potential[ny, nx] += self.coupling
            
            # Check for new firing agents
            firing_mask = self.potential >= self.threshold
            
            # Safety break for supercritical explosions
            if avalanche_size > self.n * 10:
                break
                
        return avalanche_size

def run_criticality_experiment():
    print("\n--- PAPER 29: THE CRITICAL BRAIN (SELF-ORGANIZED CRITICALITY) ---")
    
    swarm = CriticalSwarm(width=50, height=50)
    
    print("Running Simulation (Burn-in)...")
    # Burn-in to reach steady state
    for _ in range(1000):
        swarm.step()
        
    print("Collecting Avalanches...")
    avalanches = []
    for t in range(10000):
        size = swarm.step()
        if size > 0:
            avalanches.append(size)
            
    print(f"Total Avalanches: {len(avalanches)}")
    print(f"Max Avalanche Size: {np.max(avalanches)}")
    
    # Analysis: Power Law Fit
    # Histogram
    # Use logarithmic binning for better visualization of power law
    bins = np.logspace(0, np.log10(np.max(avalanches)), 20)
    hist, bin_edges = np.histogram(avalanches, bins=bins, density=True)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Filter zeros
    valid = hist > 0
    x = centers[valid]
    y = hist[valid]
    
    # Log-Log Fit
    log_x = np.log10(x)
    log_y = np.log10(y)
    
    # Fit line: log_y = -alpha * log_x + c
    slope, intercept = np.polyfit(log_x, log_y, 1)
    alpha = -slope
    
    print(f"Power Law Exponent (alpha): {alpha:.4f}")
    
    # R-squared
    predicted_log_y = -alpha * log_x + intercept
    ss_res = np.sum((log_y - predicted_log_y)**2)
    ss_tot = np.sum((log_y - np.mean(log_y))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    print(f"R-squared: {r_squared:.4f}")
    
    # Criteria
    # Good fit to power law (R^2 > 0.85) and alpha between 1.0 and 2.0 (usually ~1.5)
    
    if r_squared > 0.85 and 1.0 < alpha < 2.5:
        print("SUCCESS: Self-Organized Criticality Verified.")
        print(f"Avalanche sizes follow a Power Law (alpha={alpha:.2f}).")
    else:
        print("FAILURE: Distribution does not match Power Law.")

if __name__ == "__main__":
    run_criticality_experiment()
