import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt # Moved to top

sys.path.append(os.path.abspath("."))
from code.fractal.agent import FractalAgent
from code.pilot.cognitive_engine import CognitiveEngine

# --- TSF-3 CONFIGURATION ---
EXPERIMENT_ID = "TSF-3"
TITLE = "Agency Navigation of Complexity-Order Phase Space"
AGENTS_PER_CELL = 20
DURATION = 150 # Longer duration for navigation
LEARNING_RATE = 0.05

# Target Regime: Balanced Emergence (derived from TSF-2 analysis)
C_TARGET = 0.2 # Moderate Complexity (Energy Variance)
R_TARGET = 0.6 # Moderate Order (Phase Coherence)

class AgencyNavigationTSF3:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.history = []

        # Initial conditions for E and S
        self.energy_influx = np.random.uniform(0.01, 0.3)
        self.stability_coupling = np.random.uniform(0.0, 0.8)
        
        self.pilot = CognitiveEngine() # The Pilot will guide navigation

    def run_step(self, energy_influx, stability_coupling):
        """
        Run a single simulation step to measure C and R for given E and S.
        This is similar to a single run_cell from TSF-2.
        """
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS_PER_CELL)]
        
        energy_variance_series = []
        phase_order_series = []
        
        for t in range(DURATION // 5): # Shorter internal duration for a "reading"
            # 1. Influx
            for a in agents:
                a.update_energy(energy_influx, max_energy=10.0)
            
            # 2. Coupling (Stability - Energy Pooling & Phase Coupling)
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
            
            # 3. Evolve (Metabolism & Phase Update)
            alive_agents = []
            for a in agents:
                a.update_energy(-0.02)
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
            return 0.0, 0.0 # Extinction
        
        return np.mean(energy_variance_series[-DURATION//50:]), np.mean(phase_order_series[-DURATION//50:])


    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Target: C={C_TARGET}, R={R_TARGET}")
        
        for step in range(DURATION):
            # 1. Sense: Measure current (C, R) at current (E, S)
            current_c, current_r = self.run_step(self.energy_influx, self.stability_coupling)
            
            # 2. Evaluate Performance: How close are we to the target?
            # Inverse of distance in (C, R) space
            performance_c = -abs(current_c - C_TARGET)
            performance_r = -abs(current_r - R_TARGET)
            
            # Combine performance (could be weighted)
            total_performance = performance_c + performance_r
            
            # 3. Act: Pilot's Agency to adjust E and S
            # For simplicity, let the Pilot "tune" E and S directly
            
            # Tuning Energy Influx
            # If C is too low, increase E; if C is too high, decrease E
            delta_e = 0
            if current_c < C_TARGET:
                delta_e = LEARNING_RATE
            elif current_c > C_TARGET:
                delta_e = -LEARNING_RATE
            self.energy_influx = np.clip(self.energy_influx + delta_e, 0.01, 0.3)

            # Tuning Stability Coupling
            # If R is too low, increase S; if R is too high, decrease S
            delta_s = 0
            if current_r < R_TARGET:
                delta_s = LEARNING_RATE
            elif current_r > R_TARGET:
                delta_s = -LEARNING_RATE
            self.stability_coupling = np.clip(self.stability_coupling + delta_s, 0.0, 0.8)

            self.history.append({
                "step": step,
                "E": self.energy_influx,
                "S": self.stability_coupling,
                "C": current_c,
                "R": current_r,
                "performance": total_performance
            })
            
            print(f"Step {step:03d} | E={self.energy_influx:.2f} S={self.stability_coupling:.2f} | C={current_c:.3f} R={current_r:.3f} | Perf={total_performance:.3f}")
            
            # Check for convergence
            if abs(current_c - C_TARGET) < 0.05 and abs(current_r - R_TARGET) < 0.05:
                print(f"Converged to target (C,R) at step {step}")
                break
            
        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: AGENCY NAVIGATION ---")
        
        # Plotting the trajectory of E, S, C, R over time
        Es = [d["E"] for d in self.history]
        Ss = [d["S"] for d in self.history]
        Cs = [d["C"] for d in self.history]
        Rs = [d["R"] for d in self.history]
        steps = [d["step"] for d in self.history]

        plt.figure(figsize=(12, 6))

        plt.subplot(121)
        plt.plot(steps, Es, label='E (Energy Influx)')
        plt.plot(steps, Ss, label='S (Stability Coupling)')
        plt.axhline(y=0.01, color='r', linestyle='--', label='E_min_bound')
        plt.axhline(y=0.3, color='r', linestyle='--', label='E_max_bound')
        plt.axhline(y=0.0, color='g', linestyle='--', label='S_min_bound')
        plt.axhline(y=0.8, color='g', linestyle='--', label='S_max_bound')
        plt.title('Agent Control Parameters (E, S) over Time')
        plt.xlabel('Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)

        plt.subplot(122)
        plt.plot(steps, Cs, label='C (Complexity)')
        plt.plot(steps, Rs, label='R (Order)')
        plt.axhline(y=C_TARGET, color='c', linestyle='--', label='C_target')
        plt.axhline(y=R_TARGET, color='m', linestyle='--', label='R_target')
        plt.title('Emergent Properties (C, R) over Time')
        plt.xlabel('Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "navigation_trajectory.png"))
        plt.close()
        print(f"Navigation trajectory plot saved to {os.path.join(self.results_dir, 'navigation_trajectory.png')}")

        final_state = self.history[-1]
        converged = bool(abs(final_state["C"] - C_TARGET) < 0.05 and abs(final_state["R"] - R_TARGET) < 0.05)

        results = {
            "converged": converged,
            "final_E": final_state["E"],
            "final_S": final_state["S"],
            "final_C": final_state["C"],
            "final_R": final_state["R"],
            "target_C": C_TARGET,
            "target_R": R_TARGET,
            "steps_taken": len(self.history)
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Results saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    plt.switch_backend('Agg') # Use Agg backend for non-interactive plotting
    eng = AgencyNavigationTSF3()
    eng.run()
