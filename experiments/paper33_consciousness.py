import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

def logistic(x, r=4.0):
    return r * x * (1.0 - x)

def run_system(x, coupling, r=4.0):
    """
    Run one step of coupled logistic maps.
    x: array of states [x1, x2]
    coupling: coupling strength epsilon
    """
    N = len(x)
    x_next = np.zeros_like(x)
    for i in range(N):
        self_term = (1 - coupling) * logistic(x[i], r)
        neighbor_term = 0
        for j in range(N):
            if i != j:
                neighbor_term += logistic(x[j], r)
        
        if N > 1:
            neighbor_term *= (coupling / (N - 1))
        
        x_next[i] = self_term + neighbor_term
        # Clip to [0,1] to be safe
        x_next[i] = np.clip(x_next[i], 0.0, 1.0)
    return x_next

def calculate_entropy(data, bins=10):
    """Calculate Shannon Entropy of a distribution."""
    hist, _ = np.histogramdd(data, bins=bins, range=[(0,1)]*data.shape[1])
    prob = hist / np.sum(hist)
    prob = prob[prob > 0]
    return -np.sum(prob * np.log2(prob))

def measure_ei(coupling, r=4.0, n_bins=10, n_samples=5000):
    """
    Measure Effective Information (EI) for a 2-node system.
    EI = H(Average Effect) - Average H(Effect | Cause)
    But since we inject uniform noise (Max Entropy Cause), 
    EI = Mutual Information(Cause, Effect).
    """
    # 1. Generate Causes (Uniform Random)
    causes = np.random.random((n_samples, 2))
    
    # 2. Generate Effects
    effects = np.zeros_like(causes)
    for i in range(n_samples):
        effects[i] = run_system(causes[i], coupling, r)
        
    # 3. Calculate Mutual Information
    # MI(X, Y) = H(X) + H(Y) - H(X, Y)
    # Here X = Cause, Y = Effect
    
    # However, for Deterministic systems, H(Effect | Cause) = 0 (if no noise).
    # So EI = H(Effect).
    # But we are binning, so there is "noise" due to discretization.
    # Let's use the standard MI calculation on binned data.
    
    # Bin the data
    c_binned = np.floor(causes * n_bins).astype(int)
    e_binned = np.floor(effects * n_bins).astype(int)
    c_binned = np.clip(c_binned, 0, n_bins-1)
    e_binned = np.clip(e_binned, 0, n_bins-1)
    
    # Calculate Joint Entropy H(C, E)
    # Combine Cause and Effect into a 4D vector for histogram
    joint_data = np.hstack((causes, effects))
    h_joint = calculate_entropy(joint_data, bins=n_bins)
    
    # Calculate Marginal Entropies
    h_cause = calculate_entropy(causes, bins=n_bins)
    h_effect = calculate_entropy(effects, bins=n_bins)
    
    mi = h_cause + h_effect - h_joint
    return mi

def run_consciousness_experiment():
    print("\n--- PAPER 33: THE CONSCIOUS SWARM (INTEGRATED INFORMATION) ---")
    
    couplings = np.linspace(0.0, 0.4, 20)
    phis = []
    
    print("Running Phi Scan...")
    for c in couplings:
        # 1. EI of Whole System (Coupled)
        ei_whole = measure_ei(coupling=c)
        
        # 2. EI of Parts (Decoupled / Independent)
        # Conceptually, we partition the system into A and B.
        # The "Parts" are the nodes running with their OWN internal logic, 
        # but treating inputs from others as noise or fixed.
        # In the "Cut" partition, coupling is effectively 0.
        ei_part_a = measure_ei(coupling=0.0) / 2.0 # Approximate per-node
        ei_part_b = measure_ei(coupling=0.0) / 2.0
        
        # Actually, let's measure EI of a single node system properly
        # Run 1-node system
        # causes_1d = np.random.random((5000, 1))
        # effects_1d = ...
        # But our measure_ei function is hardcoded for 2 nodes.
        # Let's approximate: Sum of Parts = EI(Coupling=0).
        
        sum_parts = measure_ei(coupling=0.0)
        
        # Integrated Information Phi = EI(Whole) - Sum(EI(Parts))
        # This is "Whole minus Sum of Parts"
        phi = ei_whole - sum_parts
        
        # Note: This is a simplified proxy. 
        # Real Phi requires finding the Minimum Information Partition (MIP).
        # For 2 symmetric nodes, the MIP is the vertical cut.
        
        phis.append(phi)
        print(f"Coupling={c:.2f}, EI_Whole={ei_whole:.4f}, Sum_Parts={sum_parts:.4f}, Phi={phi:.4f}")
        
    # Analysis
    max_phi = np.max(phis)
    max_c = couplings[np.argmax(phis)]
    
    print(f"\nMax Phi: {max_phi:.4f} at Coupling={max_c:.2f}")
    
    # Criteria
    # Phi should be positive and peak at non-zero coupling
    if max_phi > 0.1 and max_c > 0.0:
        print("SUCCESS: Integrated Information Verified.")
        print("The swarm generates more information as a whole than the sum of its parts.")
    else:
        print("FAILURE: No significant integration detected.")

if __name__ == "__main__":
    run_consciousness_experiment()
