import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath("."))
from code.fractal.agent import FractalAgent

# --- HELIOS-3 CONFIGURATION ---
EXPERIMENT_ID = "HELIOS-3"
TITLE = "Structural Heterogeneity: Mixed Swarm Dynamics"
AGENTS_PER_CELL = 20
DURATION = 300
METABOLIC_COST = 0.02

# Target Emergent State: "Balanced Emergence"
TARGET_C_RANGE = (0.1, 0.2)
TARGET_R_RANGE = (0.5, 0.7)

# Agent Types
# Type A: Stabilizers (Low E, High S) -> Tend to Order
# Type B: Energizers (High E, Low S) -> Tend to Chaos
# Goal: Mix them to achieve Balance

TYPE_A_E = 0.05
TYPE_A_S = 0.8

TYPE_B_E = 0.25
TYPE_B_S = 0.1

MIX_RATIOS = [0.0, 0.25, 0.5, 0.75, 1.0] # Percent of Type A (Stabilizers)

class HeliosHeterogeneity:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.results = {}

    def run_mixed_simulation(self, ratio_A):
        num_A = int(AGENTS_PER_CELL * ratio_A)
        num_B = AGENTS_PER_CELL - num_A
        
        agents = []
        # Initialize Stabilizers
        for i in range(num_A):
            a = FractalAgent(f"A_{i}", phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5))
            a.type = "A"
            agents.append(a)
            
        # Initialize Energizers
        for i in range(num_B):
            a = FractalAgent(f"B_{i}", phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5))
            a.type = "B"
            agents.append(a)
            
        c_series = []
        r_series = []
        
        for t in range(DURATION):
            # 1. Influx (Heterogeneous)
            for a in agents:
                e_influx = TYPE_A_E if a.type == "A" else TYPE_B_E
                a.update_energy(e_influx, max_energy=10.0)
            
            # 2. Coupling (Heterogeneous)
            current_phases = [a.state.phase for a in agents]
            current_energies = [a.state.energy for a in agents]

            if len(current_phases) > 0:
                complex_sum = sum(math.e ** (1j * p) for p in current_phases)
                mean_phase = math.atan2(complex_sum.imag, complex_sum.real)
                current_order = abs(complex_sum) / len(current_phases)
            else:
                mean_phase = 0
                current_order = 0

            # Compute average energy for pooling
            avg_e = sum(current_energies)/len(agents) if len(agents) > 0 else 0

            for a in agents:
                s_coupling = TYPE_A_S if a.type == "A" else TYPE_B_S
                
                if s_coupling > 0:
                    diff_e = avg_e - a.state.energy
                    a.update_energy(diff_e * s_coupling)
                    
                    phase_pull = math.sin(mean_phase - a.state.phase) * s_coupling
                    a.state.phase += phase_pull
            
            # 3. Evolve
            alive_agents = []
            for a in agents:
                a.update_energy(-METABOLIC_COST)
                a.update_phase(1.0)
                if a.state.energy > 0:
                    alive_agents.append(a)
            agents = alive_agents
            
            # 4. Measure
            if not agents:
                c_series.append(0.0)
                r_series.append(0.0)
            else:
                c_series.append(np.std([a.state.energy for a in agents]))
                r_series.append(current_order)
                
        return c_series, r_series

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        
        plt.figure(figsize=(15, 10))
        
        for i, ratio in enumerate(MIX_RATIOS):
            print(f"Running Mix Ratio A={ratio*100}% ...")
            c_series, r_series = self.run_mixed_simulation(ratio)
            
            avg_c = np.mean(c_series[-DURATION//5:])
            avg_r = np.mean(r_series[-DURATION//5:])
            
            success = (TARGET_C_RANGE[0] <= avg_c <= TARGET_C_RANGE[1]) and \
                      (TARGET_R_RANGE[0] <= avg_r <= TARGET_R_RANGE[1])
            
            print(f"  -> Result: C={avg_c:.3f}, R={avg_r:.3f} | {'SUCCESS' if success else 'FAIL'}")
            
            self.results[str(ratio)] = {
                "avg_C": avg_c,
                "avg_R": avg_r,
                "success": bool(success)
            }
            
            # Plotting
            plt.subplot(2, 3, i+1)
            plt.plot(c_series, label='Complexity (C)', color='blue')
            plt.plot(r_series, label='Order (R)', color='red')
            plt.axhline(y=TARGET_C_RANGE[0], color='blue', linestyle='--', alpha=0.3)
            plt.axhline(y=TARGET_C_RANGE[1], color='blue', linestyle='--', alpha=0.3)
            plt.axhline(y=TARGET_R_RANGE[0], color='red', linestyle='--', alpha=0.3)
            plt.axhline(y=TARGET_R_RANGE[1], color='red', linestyle='--', alpha=0.3)
            plt.title(f"Mix A={ratio*100}%")
            plt.legend()
            plt.grid(True)
            plt.ylim(0, 1.1)

        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "heterogeneity_sweep.png"))
        print(f"Sweep plot saved to {os.path.join(self.results_dir, 'heterogeneity_sweep.png')}")
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    plt.switch_backend('Agg')
    eng = HeliosHeterogeneity()
    eng.run()
