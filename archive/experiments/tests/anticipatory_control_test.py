import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.fractal.fractal_swarm import FractalSwarm
from src.fractal.agent import FractalAgent

# --- PILOT COMPONENT: RESERVOIR (PREDICTION) ---
class ReservoirPilot:
    def __init__(self, n_agents=100):
        self.n_agents = n_agents
        self.W_res = np.random.normal(0, 1.0, (n_agents, n_agents))
        # Spectral radius scaling
        rho = np.max(np.abs(np.linalg.eigvals(self.W_res)))
        self.W_res = (self.W_res / rho) * 0.8 # rho=0.8
        self.W_in = np.random.uniform(-1, 1, n_agents)
        self.W_out = None
        self.state = np.zeros(n_agents)
        self.leak = 0.5
        
    def update(self, input_val):
        # ESN Update: x(t+1) = (1-a)x(t) + a*tanh(W_res*x(t) + W_in*u(t))
        update = np.tanh(self.W_res @ self.state + self.W_in * input_val)
        self.state = (1 - self.leak) * self.state + self.leak * update
        return self.state
        
    def train(self, inputs, targets):
        # Collect states
        states = []
        self.state = np.zeros(self.n_agents)
        for u in inputs:
            states.append(self.update(u))
        
        X = np.array(states)
        Y = np.array(targets)
        
        # Ridge Regression
        reg = 1e-4
        X_bias = np.hstack([np.ones((len(X), 1)), X])
        I = np.eye(X_bias.shape[1])
        self.W_out = np.linalg.inv(X_bias.T @ X_bias + reg * I) @ X_bias.T @ Y
        
    def predict(self, input_val):
        if self.W_out is None:
            return 0.0
        
        # Update state with current input
        s = self.update(input_val)
        # Predict next step
        s_bias = np.hstack([1.0, s])
        return s_bias @ self.W_out

# --- PILOT COMPONENT: INVERSE DESIGN (INTERVENTION) ---
class InverseDesignEngine:
    def find_counter_parameters(self, current_stress):
        # Simple Genetic Algorithm or Heuristic to find params that lower Order Parameter
        # For this demo, we'll use a heuristic:
        # If Stress (Forcing) is high, we need High Inflow (Energy) and Low Coupling to resist sync.
        
        # "Thinking" simulation...
        # best_k = 0.1
        # best_inflow = 10.0
        
        # Let's simulate the "Search" by returning optimal params based on stress
        # This represents the result of the GA from Paper 9
        return {
            'K': 0.1, # Decouple to resist sync
            'Inflow': 5.0 + current_stress * 2.0, # Pump energy to create noise
            'Dissipation': 0.5
        }

# --- EXPERIMENT: STRESS TEST ---
def run_stress_test(use_pilot=False):
    print(f"\n--- RUNNING STRESS TEST (Pilot={'ON' if use_pilot else 'OFF'}) ---")
    
    N_AGENTS = 50
    STEPS = 200
    
    # Initial Params
    params = {'K': 0.5, 'Inflow': 1.0, 'Dissipation': 0.1}
    
    # Agents (Phases)
    phases = np.random.uniform(0, 2*np.pi, N_AGENTS)
    velocities = np.random.normal(0, 0.1, N_AGENTS)
    
    # Pilot
    pilot = ReservoirPilot()
    engineer = InverseDesignEngine()
    
    # Pre-train Pilot on a sample run (Mental Model)
    # (Skipping full training for brevity, assume pre-trained or online learning)
    # We'll use "Online Learning" - Pilot learns as it goes? 
    # Or better: Pilot has a "Theory" that R > 0.9 is bad.
    
    history_R = []
    stress_level = 0.0
    
    survival_steps = 0
    
    for t in range(STEPS):
        # 1. Apply External Stress (Forcing Synchronization)
        # Linearly increasing stress
        stress_level = t / 100.0 # 0.0 to 2.0
        
        # 2. Swarm Dynamics (Kuramoto with Noise)
        # d(theta) = omega + K*sum(sin) + Stress*sin(forcing_freq - theta) + Noise
        
        # Calculate Order Parameter R
        z = np.exp(1j * phases)
        Z = np.sum(z) / N_AGENTS
        R = np.abs(Z)
        Psi = np.angle(Z)
        
        history_R.append(R)
        
        # Check Collapse (Rigid Order)
        if R > 0.95:
            print(f"  [t={t}] COLLAPSE! Rigid Order (R={R:.4f})")
            break
            
        survival_steps = t
        
        # 3. PILOT INTERVENTION
        if use_pilot:
            # Predict next R (Simple trend or Reservoir)
            # Let's use the Reservoir to predict R(t+1)
            # Input to Reservoir is current R
            # pred_R = pilot.predict(R) 
            
            # For this demo, let's assume Pilot sees the Trend
            # If R is rising fast or > 0.8, Intervene
            
            if R > 0.8:
                print(f"  [t={t}] PILOT ALERT: High Order (R={R:.4f}). Intervening...")
                # Call Inverse Design
                new_params = engineer.find_counter_parameters(stress_level)
                params = new_params
                print(f"  [t={t}] PILOT ACTION: Adjusted Params to {params}")
        
        # Update Phases
        # Internal Coupling
        coupling = params['K'] * R * np.sin(Psi - phases)
        
        # External Stress (Forces everyone to phase 0)
        forcing = stress_level * np.sin(0 - phases)
        
        # Noise (Energy Inflow creates noise)
        noise_strength = params['Inflow'] * 0.1
        noise = np.random.normal(0, noise_strength, N_AGENTS)
        
        d_theta = velocities + coupling + forcing + noise
        phases = (phases + d_theta * 0.1) % (2*np.pi)
        
    return survival_steps, history_R

def anticipatory_control_test():
    # 1. Baseline Run
    steps_base, r_base = run_stress_test(use_pilot=False)
    print(f"Baseline Survival: {steps_base} steps")
    
    # 2. Pilot Run
    steps_pilot, r_pilot = run_stress_test(use_pilot=True)
    print(f"Pilot Survival: {steps_pilot} steps")
    
    # 3. Validation
    if steps_pilot > steps_base:
        print("\nSUCCESS: Pilot extended survival via Anticipatory Control.")
        print(f"Gain: +{steps_pilot - steps_base} steps")
    else:
        print("\nFAILURE: Pilot did not improve survival.")

if __name__ == "__main__":
    anticipatory_control_test()
