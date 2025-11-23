import sys
import os
import time
import numpy as np
from typing import List, Tuple

# Add project root and code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.fractal.fractal_swarm import FractalSwarm
from src.fractal.agent import FractalAgent

def mackey_glass(length=1000, tau=17, delta_t=10, n=10, beta=0.2, gamma=0.1):
    """Generates Mackey-Glass chaotic time series."""
    history_length = int(tau / delta_t) + 1
    history = [1.2] * history_length
    sequence = []
    
    x = 1.2
    for i in range(length):
        x_tau = history[-1] # x(t - tau)
        dx = beta * x_tau / (1 + x_tau**n) - gamma * x
        x += dx * delta_t
        
        history.pop()
        history.insert(0, x)
        sequence.append(x)
        
    # Normalize to [-1, 1]
    seq = np.array(sequence)
    return (seq - np.mean(seq)) / np.std(seq)

def predictive_processing_test():
    print("--- TEMPORAL RECURSION EXPERIMENT (PAPER 13) ---")
    print("Hypothesis: Swarm acts as a Reservoir to predict chaotic futures.")
    
    # Parameters
    N_AGENTS = 100
    TRAIN_LEN = 500
    TEST_LEN = 200
    TOTAL_LEN = TRAIN_LEN + TEST_LEN
    PREDICTION_HORIZON = 1 # Steps ahead
    INPUT_SCALING = 1.0
    SPECTRAL_RADIUS = 0.9
    
    # 1. Generate Data (Mackey-Glass)
    print(f"\n1. Generating Mackey-Glass Chaos ({TOTAL_LEN} steps)...")
    data = mackey_glass(length=TOTAL_LEN + PREDICTION_HORIZON)
    inputs = data[:TOTAL_LEN]
    targets = data[PREDICTION_HORIZON:TOTAL_LEN + PREDICTION_HORIZON]
    
    # 3. Grid Search for Optimal Parameters (Energy-Based Reservoir)
    print("3. Running Grid Search (Energy-Based Reservoir / ESN)...")
    
    # Standard ESN parameters
    spectral_radii = [0.8, 0.9, 0.95, 1.0, 1.1]
    input_scalings = [0.1, 0.5, 1.0]
    leak_rates = [0.1, 0.5, 1.0]
    
    best_score = -1.0
    best_params = {}
    
    N_AGENTS_LARGE = 200
    SPARSITY = 0.1
    
    # Generate Sparse Adjacency Matrix
    W_res = np.random.normal(0, 1.0, (N_AGENTS_LARGE, N_AGENTS_LARGE))
    mask = np.random.rand(N_AGENTS_LARGE, N_AGENTS_LARGE) > SPARSITY
    W_res[mask] = 0
    rho = np.max(np.abs(np.linalg.eigvals(W_res)))
    W_res_base = W_res / rho
    
    W_in = np.random.uniform(-1, 1, N_AGENTS_LARGE)
    
    for rho_val in spectral_radii:
        W_eff = W_res_base * rho_val
        
        for scale in input_scalings:
            for alpha in leak_rates:
                print(f"  Testing Rho={rho_val}, Scale={scale}, Alpha={alpha}...", end="", flush=True)
                
                # Reset Agents (State = Energy)
                # Initialize random energy states [-1, 1]
                current_states = np.random.uniform(-1, 1, N_AGENTS_LARGE)
                
                reservoir_states = []
                
                # Run Dynamics (Standard ESN)
                # x(t+1) = (1-alpha)*x(t) + alpha * tanh(W_res @ x(t) + W_in * u(t))
                
                for t in range(TOTAL_LEN):
                    u = inputs[t]
                    
                    # Update
                    update = np.tanh(W_eff @ current_states + W_in * scale * u)
                    current_states = (1 - alpha) * current_states + alpha * update
                    
                    # Harvest State (Energy)
                    reservoir_states.append(current_states.copy())
                
                # Train & Test
                X = np.array(reservoir_states)
                X_train = X[:TRAIN_LEN]
                y_train = targets[:TRAIN_LEN]
                X_test = X[TRAIN_LEN:]
                y_test = targets[TRAIN_LEN:]
                
                # Ridge Regression
                X_train_bias = np.hstack([np.ones((TRAIN_LEN, 1)), X_train])
                reg = 1e-4 # Lower regularization for ESN
                I = np.eye(X_train_bias.shape[1])
                try:
                    W_out = np.linalg.inv(X_train_bias.T @ X_train_bias + reg * I) @ X_train_bias.T @ y_train
                    
                    X_test_bias = np.hstack([np.ones((TEST_LEN, 1)), X_test])
                    y_pred = X_test_bias @ W_out
                    
                    corr = np.corrcoef(y_test, y_pred)[0, 1]
                except:
                    corr = 0.0
                    
                print(f" Corr: {corr:.4f}")
                
                if corr > best_score:
                    best_score = corr
                    best_params = {'Rho': rho_val, 'Scale': scale, 'Alpha': alpha}
                
    print(f"\n--- BEST RESULT ---")
    print(f"Params: {best_params}")
    print(f"Correlation: {best_score:.4f}")
    
    if best_score > 0.8:
        print("SUCCESS: Swarm successfully predicted chaotic future.")
    else:
        print("FAILURE: Prediction correlation too low.")

if __name__ == "__main__":
    predictive_processing_test()
