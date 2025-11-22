import sys
import os
import numpy as np
import json
import time

# Ensure the project root is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent
from core.reality_interface import RealityInterface

class PredictiveControlExperiment:
    def __init__(self):
        self.reality = RealityInterface()
        self.results = {
            "reactive": {"mse": [], "variance_trace": [], "e_trace": []},
            "predictive": {"mse": [], "variance_trace": [], "e_trace": []}
        }
        # Target variance representing "Criticality"
        # Based on the synthetic model below, Max Variance is ~10.0.
        self.target_variance = 8.0 
        self.steps = 1000
        self.prediction_horizon = 5
        self.history_window = 10
        
        # Plant Parameters (The "Physics" of NRM)
        self.E_crit = 0.1045
        self.sigma = 0.002 # Width of the critical region
        self.V_max = 10.0
        self.noise_level = 1.0
        self.drift_amplitude = 0.001 # E_crit drifts over time

    def simulate_step(self, agent, t):
        """
        Simulates the NRM system response (Variance) to the agent's E_consume.
        Includes a drifting critical point to test adaptation.
        """
        # 1. Drift the critical point (Simulate environmental change)
        current_E_crit = self.E_crit + self.drift_amplitude * np.sin(t / 100.0)
        
        # 2. Calculate Variance (The "Hill" of Criticality)
        # V(E) = V_max * exp(- (E - E_crit)^2 / (2*sigma^2))
        delta_E = agent.E_consume - current_E_crit
        variance = self.V_max * np.exp(-(delta_E**2) / (2 * self.sigma**2))
        
        # 3. Add Noise (Stochasticity)
        noise = np.random.normal(0, self.noise_level)
        variance = max(0, variance + noise)
        
        return variance

    def run_controller(self, mode="reactive"):
        print(f"Starting {mode} control run...")
        agent = FractalAgent(agent_id="0")
        
        # Initialize parameters
        agent.E_consume = 0.100 
        current_e = 0.100
        
        variance_history = []
        smoothed_variance_history = [] 
        alpha = 0.1 # Stronger smoothing
        current_smoothed_var = 0
        
        error_sum = 0
        squared_error_sum = 0
        
        # Gains
        Kp_reactive = 0.0005
        Kp_predictive = 0.0001 # Trust prediction less
        
        trace_var = []
        trace_e = []

        for t in range(self.steps):
            # 1. Run Simulation Step
            current_variance = self.simulate_step(agent, t)
            
            # Update smoothed variance
            if t == 0:
                current_smoothed_var = current_variance
            else:
                current_smoothed_var = alpha * current_variance + (1 - alpha) * current_smoothed_var
            
            # 2. Control Logic
            control_signal = 0
            
            if mode == "reactive":
                error = self.target_variance - current_variance
                control_signal = Kp_reactive * error
                
            elif mode == "predictive":
                # Predict based on SMOOTHED history
                if len(smoothed_variance_history) >= self.history_window:
                    # Linear Extrapolation on Smoothed Data
                    y = np.array(smoothed_variance_history[-self.history_window:])
                    x = np.arange(len(y))
                    A = np.vstack([x, np.ones(len(x))]).T
                    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
                    
                    # Predict at t + horizon (Reduced horizon)
                    horizon = 2
                    future_x = len(y) + horizon
                    predicted_variance = m * future_x + c
                    
                    # Control based on predicted error
                    error = self.target_variance - predicted_variance
                    control_signal = Kp_predictive * error
                else:
                    # Fallback
                    error = self.target_variance - current_smoothed_var
                    control_signal = Kp_predictive * error

            # 3. Apply Control
            current_e += control_signal
            
            # Clamp E 
            current_e = max(0.090, min(0.120, current_e))
            agent.E_consume = current_e
            
            # Record
            variance_history.append(current_variance)
            smoothed_variance_history.append(current_smoothed_var)
            trace_var.append(current_variance)
            trace_e.append(current_e)
            squared_error_sum += (self.target_variance - current_variance) ** 2
            
        mse = squared_error_sum / self.steps
        self.results[mode]["mse"] = mse
        self.results[mode]["variance_trace"] = trace_var
        self.results[mode]["e_trace"] = trace_e
        print(f"Finished {mode}. MSE: {mse}")

    def run(self):
        print("Cycle 293: Predictive Control Experiment")
        print("----------------------------------------")
        
        # Run Reactive
        self.run_controller("reactive")
        
        # Run Predictive
        self.run_controller("predictive")
        
        # Compare
        mse_reactive = self.results["reactive"]["mse"]
        mse_predictive = self.results["predictive"]["mse"]
        
        print("\nResults:")
        print(f"Reactive MSE:   {mse_reactive:.5f}")
        print(f"Predictive MSE: {mse_predictive:.5f}")
        
        improvement = (mse_reactive - mse_predictive) / mse_reactive * 100
        print(f"Improvement:    {improvement:.2f}%")
        
        return {
            "mse_reactive": mse_reactive,
            "mse_predictive": mse_predictive,
            "improvement": improvement
        }

if __name__ == "__main__":
    exp = PredictiveControlExperiment()
    results = exp.run()
    
    # Save results
    with open("experiments/cycle293_results.json", "w") as f:
        json.dump(results, f, indent=4)
