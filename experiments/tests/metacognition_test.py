import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# --- EXPERIMENT: METACOGNITION (The Self-Aware Engine) ---

class Environment:
    def __init__(self):
        self.state = 0.5
        self.noise_level = 0.01
        self.regime = "STABLE"
        
    def step(self, control_signal):
        # Dynamics: x(t+1) = r * x(t) * (1 - x(t)) + control + noise
        # Logistic Map base
        r = 3.8 if self.regime == "CHAOS" else 2.5
        
        # Natural dynamics
        next_state = r * self.state * (1 - self.state)
        
        # Apply Control
        next_state += control_signal
        
        # Apply Noise
        noise = np.random.normal(0, self.noise_level)
        next_state += noise
        
        # Clip to valid range (0, 1) to prevent explosion, but allow crash
        self.state = np.clip(next_state, 0, 1)
        
        return self.state

class Predictor:
    def __init__(self):
        self.history = []
        self.errors = []
        
    def predict(self, current_state):
        # Simple internal model: Assumes STABLE regime (r=2.5)
        # This model is WRONG when the environment switches to CHAOS.
        # This mismatch creates "Uncertainty" (Prediction Error).
        pred = 2.5 * current_state * (1 - current_state)
        return pred
        
    def update(self, actual_state, predicted_state):
        error = abs(actual_state - predicted_state)
        self.errors.append(error)
        # Uncertainty is the moving average of recent errors
        if len(self.errors) > 5:
            uncertainty = np.mean(self.errors[-5:])
        else:
            uncertainty = error
        return uncertainty

class NaivePilot:
    def __init__(self):
        self.predictor = Predictor()
        
    def act(self, state):
        # Naive Goal: Force state to 0.7
        # Simple P-Controller
        target = 0.7
        pred = self.predictor.predict(state)
        
        # Naive Pilot ignores uncertainty. Just tries to close the gap.
        control = (target - pred) * 0.5 # High Gain
        
        # Update predictor (even though it ignores the error for decision making)
        # We calculate it just to show the pilot *could* have known.
        uncertainty = self.predictor.update(state, pred) # calculated but ignored
        
        return control, "OPTIMIZE"

class MetacognitivePilot:
    def __init__(self):
        self.predictor = Predictor()
        self.uncertainty_threshold = 0.1
        
    def act(self, state):
        # 1. Predict
        pred = self.predictor.predict(state)
        
        # 2. Measure Uncertainty (from previous step's prediction vs this state)
        # For simulation step t, we need to know error of pred(t-1) vs state(t).
        # Here we simplify: we look at the *recent* uncertainty history.
        if len(self.predictor.errors) > 0:
            uncertainty = np.mean(self.predictor.errors[-5:])
        else:
            uncertainty = 0.0
            
        # 3. Decide Mode
        if uncertainty > self.uncertainty_threshold:
            mode = "SAFETY"
        else:
            mode = "OPTIMIZE"
            
        # 4. Act based on Mode
        if mode == "OPTIMIZE":
            # High Gain Control (Same as Naive)
            target = 0.7
            control = (target - pred) * 0.5
        else:
            # Safety Mode: Zero Control / Dampening
            # In chaos, adding strong control often amplifies instability.
            # "Don't touch it if you don't understand it."
            control = 0.0 
            
        # Update internal model tracking
        self.predictor.update(state, pred)
        
        return control, mode

def run_simulation(pilot_type, steps=100):
    env = Environment()
    pilot = NaivePilot() if pilot_type == "NAIVE" else MetacognitivePilot()
    
    history_state = []
    history_mode = []
    crashes = 0
    
    print(f"\n--- Simulation: {pilot_type} PILOT ---")
    
    for t in range(steps):
        # Switch to CHAOS halfway
        if t == 50:
            print(f"  [t={t}] ENVIRONMENT SWITCH: STABLE -> CHAOS")
            env.regime = "CHAOS"
            env.noise_level = 0.2 # High noise
            
        # Pilot Act
        control, mode = pilot.act(env.state)
        history_mode.append(mode)
        
        # Environment Step
        state = env.step(control)
        history_state.append(state)
        
        # Check for "Crash" (Extreme values)
        if state < 0.05 or state > 0.95:
            crashes += 1
            
    avg_state = np.mean(history_state[50:]) # Avg state in Chaos
    print(f"  Result: Crashes = {crashes}")
    print(f"  Modes used: {set(history_mode)}")
    
    return crashes

def metacognition_test():
    print("\n--- PAPER 17: METACOGNITION TEST ---")
    
    # Run Naive Pilot
    crashes_naive = run_simulation("NAIVE")
    
    # Run Metacognitive Pilot
    crashes_meta = run_simulation("METACOGNITIVE")
    
    print("\n--- COMPARISON ---")
    print(f"Naive Pilot Crashes:        {crashes_naive}")
    print(f"Metacognitive Pilot Crashes: {crashes_meta}")
    
    if crashes_meta < crashes_naive:
        print("\nSUCCESS: Metacognitive Pilot survived better by engaging Safety Mode.")
    else:
        print("\nFAILURE: Metacognition did not improve survival.")

if __name__ == "__main__":
    metacognition_test()
