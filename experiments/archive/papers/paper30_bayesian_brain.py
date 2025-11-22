import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class Target:
    def __init__(self, width=100, height=100):
        self.pos = np.array([width/2, height/2])
        self.time = 0
        self.width = width
        self.height = height
        
    def step(self, dt=0.1):
        self.time += dt
        # Linear Path + Random Walk
        # Center
        cx, cy = self.width/2, self.height/2
        
        # Deterministic part (Linear)
        # Velocity = [10, 5]
        vx, vy = 10.0, 5.0
        
        # No Wrap around
        x = cx + vx * self.time
        y = cy + vy * self.time
        
        # Add some noise to the movement itself (Process Noise)
        self.pos = np.array([x, y]) + np.random.normal(0, 0.5, 2)
        
        return self.pos

class ReactiveAgent:
    def __init__(self, start_pos):
        self.pos = np.array(start_pos, dtype=float)
        
    def update(self, observation, dt=0.1):
        # Move towards observation directly
        # Simple P-controller
        direction = observation - self.pos
        speed = 20.0 # Faster than target
        
        dist = np.linalg.norm(direction)
        if dist > 0:
            vel = (direction / dist) * speed
            self.pos += vel * dt
            
class BayesianAgent:
    def __init__(self, start_pos):
        self.pos = np.array(start_pos, dtype=float)
        
        # Internal Model (Kalman Filter)
        # State: [x, y, vx, vy]
        self.state = np.array([start_pos[0], start_pos[1], 0, 0], dtype=float)
        
        # Covariance Matrix P
        self.P = np.eye(4) * 10.0
        
        # State Transition Matrix F
        # x' = x + vx*dt
        # v' = v
        dt = 0.1
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement Matrix H
        # We observe [x, y]
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Process Noise Q (Uncertainty in model)
        # Lower Q to trust model smoothness more
        self.Q = np.eye(4) * 0.1
        
        # Measurement Noise R (Uncertainty in sensors)
        self.R = np.eye(2) * 10.0 # Very High sensor noise!
        
    def update(self, observation, dt=0.1):
        # 1. Predict (Prior)
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        
        # 2. Update (Posterior)
        # Innovation (Prediction Error)
        y = observation - (self.H @ self.state)
        
        # Innovation Covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman Gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update State
        self.state = self.state + K @ y
        
        # Update Covariance
        I = np.eye(4)
        self.P = (I - K @ self.H) @ self.P
        
        # 3. Action
        # Move towards PREDICTED future position (or current estimated position)
        # Let's move to the estimated position
        target_pos = self.state[:2]
        
        direction = target_pos - self.pos
        speed = 20.0 # Faster than target (v~15)
        
        dist = np.linalg.norm(direction)
        if dist > 0:
            vel = (direction / dist) * speed
            self.pos += vel * dt

def run_bayesian_brain_experiment():
    print("\n--- PAPER 30: THE BAYESIAN BRAIN (PREDICTIVE CODING) ---")
    
    width, height = 10000, 10000 # Huge arena to avoid wrap-around
    target = Target(width, height)
    
    start_pos = [width/2, height/2]
    reactive_agent = ReactiveAgent(start_pos)
    bayesian_agent = BayesianAgent(start_pos)
    
    errors_reactive = []
    errors_bayesian = []
    
    print("Running Simulation...")
    for t in range(500):
        # True Target Position
        true_pos = target.step()
        
        # Noisy Observation (Sensory Input)
        # Match R (std approx sqrt(10) ~ 3.16)
        observation = true_pos + np.random.normal(0, 3.16, 2)
        
        # Update Agents
        reactive_agent.update(observation)
        bayesian_agent.update(observation)
        
        # Calculate Error (Distance to TRUE position)
        err_r = np.linalg.norm(reactive_agent.pos - true_pos)
        err_b = np.linalg.norm(bayesian_agent.pos - true_pos)
        
        errors_reactive.append(err_r)
        errors_bayesian.append(err_b)
        
    # Analysis
    mse_reactive = np.mean(np.array(errors_reactive)**2)
    mse_bayesian = np.mean(np.array(errors_bayesian)**2)
    
    print(f"Reactive Agent MSE: {mse_reactive:.4f}")
    print(f"Bayesian Agent MSE: {mse_bayesian:.4f}")
    
    improvement = (mse_reactive - mse_bayesian) / mse_reactive * 100.0
    print(f"Improvement: {improvement:.2f}%")
    
    # Criteria
    # Bayesian should be significantly better (> 40% improvement)
    if improvement > 40.0:
        print("SUCCESS: Predictive Coding Verified.")
        print("Bayesian Agent minimized Free Energy (Prediction Error) significantly better.")
    else:
        print("FAILURE: Bayesian Agent did not outperform significantly.")

if __name__ == "__main__":
    run_bayesian_brain_experiment()
