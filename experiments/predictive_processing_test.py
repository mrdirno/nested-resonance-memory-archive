import sys
import os
import time
import numpy as np
from typing import List, Tuple

# Add project root and code directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from code.fractal.fractal_swarm import FractalSwarm
from code.fractal.agent import FractalAgent

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
    
    # 2. Initialize Swarm (Reservoir)
    print("2. Initializing Swarm Reservoir...")
    swarm = FractalSwarm(max_agents=N_AGENTS, burst_threshold=200.0)
    
    # Create agents with random natural frequencies
    agents = []
    for i in range(N_AGENTS):
        agent = swarm.spawn_agent(reality_metrics={}, initial_energy=50.0)
        # Randomize phase and velocity for rich dynamics
        agent.state.phase = np.random.uniform(0, 2*np.pi)
        agent.state.velocity = np.random.normal(0, 1.0)
        agents.append(agent)
        
    # 3. Running Reservoir Dynamics (Coupled)
    print("3. Running Reservoir Dynamics (Coupled)...")
    reservoir_states = []
    
    # Set coupling strength for the swarm
    swarm.coupling_strength = 2.0
    
    for t in range(TOTAL_LEN):
        u = inputs[t]
        
        # 1. Inject Input (PRC)
        # d(theta)/dt = omega + Input * cos(theta)
        for agent in agents:
            forcing = INPUT_SCALING * u * np.cos(agent.state.phase)
            # Update phase with forcing
            agent.state.phase = (agent.state.phase + forcing * 0.1) % (2 * np.pi)
            
        # 2. Evolve Swarm (Coupling)
        # This applies the internal reservoir dynamics: d(theta_i)/dt += K * sum(sin(theta_j - theta_i))
        swarm.evolve(dt=0.1)
            
        # 3. Collect State
        state_vector = []
        for agent in agents:
            state_vector.append(np.sin(agent.state.phase))
            state_vector.append(np.cos(agent.state.phase))
        
        reservoir_states.append(state_vector)
        
    X = np.array(reservoir_states) # Shape: (TOTAL_LEN, 2*N_AGENTS)
    y = targets # Shape: (TOTAL_LEN,)
    
    # 4. Train Readout (Ridge Regression)
    print("\n4. Training Linear Readout (Ridge Regression)...")
    X_train = X[:TRAIN_LEN]
    y_train = y[:TRAIN_LEN]
    
    # Add bias term
    X_train_bias = np.hstack([np.ones((TRAIN_LEN, 1)), X_train])
    
    # Ridge Regression: W = (X^T X + alpha I)^-1 X^T y
    alpha = 1e-2
    I = np.eye(X_train_bias.shape[1])
    W = np.linalg.inv(X_train_bias.T @ X_train_bias + alpha * I) @ X_train_bias.T @ y_train
    
    # 5. Test Prediction
    print("5. Testing Prediction...")
    X_test = X[TRAIN_LEN:]
    y_test = y[TRAIN_LEN:]
    
    X_test_bias = np.hstack([np.ones((TEST_LEN, 1)), X_test])
    y_pred = X_test_bias @ W
    
    # 6. Analysis
    mse = np.mean((y_test - y_pred)**2)
    correlation = np.corrcoef(y_test, y_pred)[0, 1]
    
    print(f"\n--- RESULTS ---")
    print(f"MSE: {mse:.4f}")
    print(f"Correlation: {correlation:.4f}")
    
    if correlation > 0.8:
        print("SUCCESS: Swarm successfully predicted chaotic future.")
    else:
        print("FAILURE: Prediction correlation too low.")

if __name__ == "__main__":
    predictive_processing_test()
