import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class TimeCrystalSwarm:
    def __init__(self, n_agents=300, size=10.0, noise=0.1, delay=0):
        self.n = n_agents
        self.size = size
        self.noise = noise
        self.delay = delay
        self.pos = np.random.rand(n_agents, 2) * size
        self.vel = np.random.randn(n_agents, 2)
        norms = np.linalg.norm(self.vel, axis=1, keepdims=True)
        self.vel = self.vel / norms
        
        # History buffer for delayed interaction
        # Stores velocity states for past 'delay' steps
        # We need to store velocities for ALL agents at each step
        self.history = deque(maxlen=delay + 1)
        # Initialize history with current velocity
        for _ in range(delay + 1):
            self.history.append(self.vel.copy())

    def step(self):
        # 1. Retrieve Delayed State
        # If delay is 0, use current state (index -1)
        # If delay is T, use state at index 0 (oldest)
        delayed_vel = self.history[0] 
        
        # 2. Compute Neighbors (Naive O(N^2))
        dx = np.subtract.outer(self.pos[:, 0], self.pos[:, 0])
        dy = np.subtract.outer(self.pos[:, 1], self.pos[:, 1])
        
        dx = (dx + self.size/2) % self.size - self.size/2
        dy = (dy + self.size/2) % self.size - self.size/2
        
        dists = np.sqrt(dx**2 + dy**2)
        neighbors = dists < 1.0
        
        # 3. Alignment with DELAYED Velocity
        # Agents align with what their neighbors were doing T steps ago
        sum_vel_x = neighbors @ delayed_vel[:, 0]
        sum_vel_y = neighbors @ delayed_vel[:, 1]
        
        norms = np.sqrt(sum_vel_x**2 + sum_vel_y**2) + 1e-6
        target_vel_x = sum_vel_x / norms
        target_vel_y = sum_vel_y / norms
        
        # 4. Update with Noise
        noise_vec = np.random.normal(0, self.noise, (self.n, 2))
        
        new_vel_x = target_vel_x + noise_vec[:, 0]
        new_vel_y = target_vel_y + noise_vec[:, 1]
        
        new_norms = np.sqrt(new_vel_x**2 + new_vel_y**2)
        self.vel[:, 0] = new_vel_x / new_norms
        self.vel[:, 1] = new_vel_y / new_norms
        
        # 5. Move
        self.pos += self.vel * 0.1
        self.pos = self.pos % self.size
        
        # 6. Update History
        self.history.append(self.vel.copy())

    def get_order_parameter(self):
        mean_v = np.mean(self.vel, axis=0)
        return np.linalg.norm(mean_v)

def run_time_crystal_experiment():
    print("\n--- PAPER 25: THE TIME CRYSTAL (TEMPORAL SYMMETRY BREAKING) ---")
    
    # Control: No Delay
    print("Running Control (Delay=0)...")
    swarm_control = TimeCrystalSwarm(n_agents=300, delay=0)
    order_control = []
    for _ in range(200):
        swarm_control.step()
        order_control.append(swarm_control.get_order_parameter())
        
    # Experiment: Delay = 10 steps
    print("Running Experiment (Delay=10)...")
    swarm_exp = TimeCrystalSwarm(n_agents=300, delay=10)
    order_exp = []
    for _ in range(200):
        swarm_exp.step()
        order_exp.append(swarm_exp.get_order_parameter())
        
    # Analysis: FFT to find dominant frequency
    # Remove DC component
    signal_control = np.array(order_control) - np.mean(order_control)
    signal_exp = np.array(order_exp) - np.mean(order_exp)
    
    fft_control = np.fft.fft(signal_control)
    fft_exp = np.fft.fft(signal_exp)
    
    freqs = np.fft.fftfreq(len(signal_control))
    
    # Find peak power (ignoring DC)
    power_control = np.abs(fft_control)**2
    power_exp = np.abs(fft_exp)**2
    
    # Zero out negative freqs and DC
    power_control[freqs <= 0] = 0
    power_exp[freqs <= 0] = 0
    
    peak_freq_control = freqs[np.argmax(power_control)]
    peak_power_control = np.max(power_control)
    
    peak_freq_exp = freqs[np.argmax(power_exp)]
    peak_power_exp = np.max(power_exp)
    
    print(f"\nControl (Delay=0): Peak Freq={peak_freq_control:.3f}, Power={peak_power_control:.2f}")
    print(f"Experiment (Delay=10): Peak Freq={peak_freq_exp:.3f}, Power={peak_power_exp:.2f}")
    
    # Criteria:
    # Experiment should have significantly higher oscillation power than control.
    # And a distinct frequency.
    
    if peak_power_exp > peak_power_control * 2.0 and peak_power_exp > 1.0:
        print("SUCCESS: Temporal Symmetry Breaking Verified.")
        print("The swarm spontaneously generated an internal clock (Oscillation).")
    else:
        print("FAILURE: No significant oscillation detected.")

if __name__ == "__main__":
    run_time_crystal_experiment()
