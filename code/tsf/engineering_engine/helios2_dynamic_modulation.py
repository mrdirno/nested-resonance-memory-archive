import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath("."))
from code.fractal.agent import FractalAgent

# --- HELIOS-2 CONFIGURATION ---
EXPERIMENT_ID = "HELIOS-2"
TITLE = "Dynamic Parameter Modulation for Stability"
AGENTS_PER_CELL = 20
DURATION = 300
METABOLIC_COST = 0.02

# Target Emergent State: "Balanced Emergence"
# High Phase Order (Cohesion) + Moderate Complexity (Adaptability)
TARGET_C_RANGE = (0.1, 0.2)
TARGET_R_RANGE = (0.5, 0.7)

# Modulation Parameters
# We oscillate E and S around their "optimal" static values to keep the system "awake"
E_BASE = 0.15
E_AMP = 0.05
E_FREQ = 0.1 # Frequency of modulation

S_BASE = 0.4
S_AMP = 0.2
S_FREQ = 0.05 # Different frequency to create interference patterns

class HeliosDynamicModulation:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.history = []

    def run_simulation(self):
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS_PER_CELL)]
        
        c_series = []
        r_series = []
        e_input_series = []
        s_input_series = []
        
        for t in range(DURATION):
            # 1. Dynamic Modulation
            energy_influx = E_BASE + E_AMP * math.sin(t * E_FREQ)
            stability_coupling = S_BASE + S_AMP * math.sin(t * S_FREQ)
            
            # 2. Influx
            for a in agents:
                a.update_energy(energy_influx, max_energy=10.0)
            
            # 3. Coupling
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
            
            # 4. Evolve
            alive_agents = []
            for a in agents:
                a.update_energy(-METABOLIC_COST)
                a.update_phase(1.0)
                if a.state.energy > 0:
                    alive_agents.append(a)
            agents = alive_agents
            
            # 5. Measure
            if not agents:
                current_c = 0.0
                current_r = 0.0
            else:
                current_c = np.std([a.state.energy for a in agents])
                current_r = current_order
            
            c_series.append(current_c)
            r_series.append(current_r)
            e_input_series.append(energy_influx)
            s_input_series.append(stability_coupling)
            
            if t % 50 == 0:
                print(f"Step {t}: E={energy_influx:.2f}, S={stability_coupling:.2f} -> C={current_c:.3f}, R={current_r:.3f}")

        self._analyze(c_series, r_series, e_input_series, s_input_series)

    def _analyze(self, c_series, r_series, e_series, s_series):
        print("\n--- ANALYSIS: DYNAMIC MODULATION ---")
        
        steps = range(DURATION)
        
        plt.figure(figsize=(12, 10))
        
        plt.subplot(311)
        plt.plot(steps, e_series, label='E (Energy Influx)', color='orange')
        plt.plot(steps, s_series, label='S (Stability Coupling)', color='green')
        plt.title('Dynamic Control Parameters')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(312)
        plt.plot(steps, c_series, label='Complexity (C)')
        plt.axhline(y=TARGET_C_RANGE[0], color='blue', linestyle='--', alpha=0.5)
        plt.axhline(y=TARGET_C_RANGE[1], color='blue', linestyle='--', alpha=0.5, label='Target C')
        plt.title('Emergent Complexity Response')
        plt.legend()
        plt.grid(True)

        plt.subplot(313)
        plt.plot(steps, r_series, label='Order (R)', color='red')
        plt.axhline(y=TARGET_R_RANGE[0], color='purple', linestyle='--', alpha=0.5)
        plt.axhline(y=TARGET_R_RANGE[1], color='purple', linestyle='--', alpha=0.5, label='Target R')
        plt.title('Emergent Order Response')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "dynamic_modulation_response.png"))
        print(f"Dynamic response plot saved to {os.path.join(self.results_dir, 'dynamic_modulation_response.png')}")
        
        # Calculate time spent in target zone
        in_zone_count = 0
        for c, r in zip(c_series, r_series):
            if (TARGET_C_RANGE[0] <= c <= TARGET_C_RANGE[1]) and (TARGET_R_RANGE[0] <= r <= TARGET_R_RANGE[1]):
                in_zone_count += 1
        
        success_rate = in_zone_count / DURATION
        print(f"Time in Target Zone: {success_rate*100:.1f}%")
        
        results = {
            "success_rate": success_rate,
            "avg_C": np.mean(c_series),
            "avg_R": np.mean(r_series),
            "var_C": np.var(c_series),
            "var_R": np.var(r_series)
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    plt.switch_backend('Agg')
    eng = HeliosDynamicModulation()
    eng.run_simulation()
