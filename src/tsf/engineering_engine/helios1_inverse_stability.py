import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath("."))
from src.fractal.agent import FractalAgent

# --- HELIOS-1 CONFIGURATION ---
EXPERIMENT_ID = "HELIOS-1"
TITLE = "Inverse Design of Stability: The Robustness Kernel"
AGENTS_PER_CELL = 20
DURATION = 200 
VALIDATION_RUNS = 5

# Target Emergent State: "Robust Stability"
# High Phase Order (Cohesion) + Moderate Complexity (Adaptability)
# This corresponds to the "Balanced Emergence" regime boundaries identified in TSF-11
TARGET_C_RANGE = (0.1, 0.2)
TARGET_R_RANGE = (0.5, 0.7)

# Derived Optimal Parameters from TSF-11 Reachability Map
# Looking at TSF-11 maps, for C~0.15 and R~0.6, we need:
# Energy Influx (E) ~ 0.15
# Stability Coupling (S) ~ 0.4
OPTIMAL_E = 0.15
OPTIMAL_S = 0.4

# Stress Test Scenarios
STRESS_LEVELS = [0.0, 0.02, 0.04, 0.06, 0.08] # Increasing Metabolic Cost

class HeliosInverseDesign:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.results = {}

    def run_validation(self, energy_influx, stability_coupling, metabolic_cost):
        """
        Runs a simulation with fixed parameters to validate emergent properties.
        """
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS_PER_CELL)]
        
        energy_variance_series = []
        phase_order_series = []
        
        for t in range(DURATION):
            # 1. Influx
            for a in agents:
                a.update_energy(energy_influx, max_energy=10.0)
            
            # 2. Coupling
            current_phases = [a.state.phase for a in agents]
            current_energies = [a.state.energy for a in agents]

            if len(current_phases) > 0:
                complex_sum = sum(math.e ** (1j * p) for p in current_phases)
                mean_phase = math.atan2(complex_sum.imag, complex_sum.real)
                current_order = abs(complex_sum) / len(current_phases)
            else:
                mean_phase = 0
                current_order = 0

            if stability_coupling > 0:
                avg_e = sum(current_energies)/len(agents) if len(agents) > 0 else 0
                for a in agents:
                    diff_e = avg_e - a.state.energy
                    a.update_energy(diff_e * stability_coupling)
                    phase_pull = math.sin(mean_phase - a.state.phase) * stability_coupling
                    a.state.phase += phase_pull
            
            # 3. Evolve
            alive_agents = []
            for a in agents:
                a.update_energy(-metabolic_cost)
                a.update_phase(1.0)
                if a.state.energy > 0:
                    alive_agents.append(a)
            agents = alive_agents
            
            if not agents:
                energy_variance_series.append(0.0)
                phase_order_series.append(0.0)
            else:
                energy_variance_series.append(np.std([a.state.energy for a in agents]))
                phase_order_series.append(current_order)
            
        if not energy_variance_series or not phase_order_series:
            return 0.0, 0.0, False # Extinction
        
        final_C = np.mean(energy_variance_series[-DURATION//10:])
        final_R = np.mean(phase_order_series[-DURATION//10:])
        
        success = (TARGET_C_RANGE[0] <= final_C <= TARGET_C_RANGE[1]) and \
                  (TARGET_R_RANGE[0] <= final_R <= TARGET_R_RANGE[1])
                  
        return final_C, final_R, success

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Hypothesis: Parameters E={OPTIMAL_E}, S={OPTIMAL_S} yield Robust Stability (C~{TARGET_C_RANGE}, R~{TARGET_R_RANGE})")
        
        for stress in STRESS_LEVELS:
            print(f"\n--- Testing Stress Level: Metabolic Cost = {stress} ---")
            success_count = 0
            c_values = []
            r_values = []
            
            for i in range(VALIDATION_RUNS):
                c, r, success = self.run_validation(OPTIMAL_E, OPTIMAL_S, stress)
                c_values.append(c)
                r_values.append(r)
                if success: success_count += 1
                # print(f"Run {i+1}: C={c:.3f}, R={r:.3f} -> {{'SUCCESS' if success else 'FAIL'}}")
            
            avg_c = np.mean(c_values)
            avg_r = np.mean(r_values)
            success_rate = success_count / VALIDATION_RUNS
            
            print(f"Stress {stress}: Avg C={avg_c:.3f}, Avg R={avg_r:.3f}, Success Rate={success_rate*100:.0f}%")
            
            self.results[str(stress)] = {
                "avg_C": avg_c,
                "avg_R": avg_r,
                "success_rate": success_rate,
                "raw_C": c_values,
                "raw_R": r_values
            }

        self._analyze()

    def _analyze(self):
        print("\n--- ANALYSIS: INVERSE DESIGN VALIDATION ---")
        
        stress_vals = [float(k) for k in self.results.keys()]
        avg_cs = [v["avg_C"] for v in self.results.values()]
        avg_rs = [v["avg_R"] for v in self.results.values()]
        success_rates = [v["success_rate"] for v in self.results.values()]

        plt.figure(figsize=(10, 6))
        plt.plot(stress_vals, avg_cs, label='Avg Complexity (C)', marker='o')
        plt.plot(stress_vals, avg_rs, label='Avg Order (R)', marker='s')
        plt.fill_between(stress_vals, TARGET_C_RANGE[0], TARGET_C_RANGE[1], alpha=0.2, color='blue', label='Target C Range')
        plt.fill_between(stress_vals, TARGET_R_RANGE[0], TARGET_R_RANGE[1], alpha=0.2, color='orange', label='Target R Range')
        
        plt.xlabel('Metabolic Stress (Cost)')
        plt.ylabel('Emergent Property Value')
        plt.title('Robustness of Inverse-Designed System under Stress')
        plt.legend()
        plt.grid(True)
        
        plt.savefig(os.path.join(self.results_dir, "robustness_kernel_validation.png"))
        print(f"Robustness validation plot saved to {os.path.join(self.results_dir, 'robustness_kernel_validation.png')}")
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(self.results, f, indent=2)
            
        print(f"Results saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    plt.switch_backend('Agg')
    eng = HeliosInverseDesign()
    eng.run()
