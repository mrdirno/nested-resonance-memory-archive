import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath("."))
from code.fractal.agent import FractalAgent

# --- TSF-6 CONFIGURATION ---
EXPERIMENT_ID = "TSF-6"
TITLE = "Meta-Adaptation: Adapting the Agency Strategy"
AGENTS_PER_CELL = 20
DURATION = 300 # Longer duration for adaptation scenarios

# Initial Perturbation Magnitude (dynamic)
PERTURB_MAGNITUDE_INIT = 0.02 

# Adaptation rates for perturb magnitude
EXPLORE_BOOST_FACTOR = 1.5
EXPLOIT_REDUCE_FACTOR = 0.8
STAGNATION_WINDOW = 10 # Number of steps to check for stagnation

# Initial Target Regime (same as TSF-5)
C_TARGET_INIT = 0.2
R_TARGET_INIT = 0.6

# Changing Conditions Scenarios (same as TSF-5)
CHANGE_STEP_1 = 100 # Change target at this step
CHANGE_STEP_2 = 200 # Change metabolic cost at this step

C_TARGET_SHIFT = 0.4 # New target C
R_TARGET_SHIFT = 0.3 # New target R
METABOLIC_COST_INIT = 0.02
METABOLIC_COST_INCREASE = 0.04 # New metabolic cost

class MetaAdaptationTSF6:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.history = []

        # Initial control parameters (E, S)
        self.energy_influx = np.random.uniform(0.01, 0.3)
        self.stability_coupling = np.random.uniform(0.0, 0.8)
        
        # Meta-adaptive parameter
        self.perturb_magnitude = PERTURB_MAGNITUDE_INIT
        self.last_performance_history = [-np.inf] * STAGNATION_WINDOW # For stagnation check

        # Internal state for the simulation loop
        self.metabolic_cost = METABOLIC_COST_INIT
        self.c_target = C_TARGET_INIT
        self.r_target = R_TARGET_INIT
        self.best_performance_overall = -np.inf # Keep track of global best

    def run_step_simulation(self, energy_influx, stability_coupling, metabolic_cost):
        """
        Run a single simulation chunk to measure C and R for given E and S.
        """
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS_PER_CELL)]
        
        energy_variance_series = []
        phase_order_series = []
        
        internal_duration = 50 
        
        for t in range(internal_duration):
            for a in agents:
                a.update_energy(energy_influx, max_energy=10.0)
            
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
            return 0.0, 0.0 # Extinction
        
        return np.mean(energy_variance_series[-internal_duration//10:]), np.mean(phase_order_series[-internal_duration//10:])

    def calculate_performance(self, c_val, r_val):
        """
        Calculates a performance score based on proximity to current target C and R.
        """
        dist_c = abs(c_val - self.c_target)
        dist_r = abs(r_val - self.r_target)
        return -(dist_c + dist_r) 

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Initial Target: C={self.c_target}, R={self.r_target}")
        
        for step in range(DURATION):
            # --- Scenario Changes ---
            if step == CHANGE_STEP_1:
                self.c_target = C_TARGET_SHIFT
                self.r_target = R_TARGET_SHIFT
                print(f"\n--- Step {step}: TARGET SHIFTED to C={self.c_target}, R={self.r_target} ---")
                # Reset perturb magnitude to encourage re-exploration
                self.perturb_magnitude = PERTURB_MAGNITUDE_INIT * EXPLORE_BOOST_FACTOR
                self.best_performance_overall = -np.inf # Reset best performance
            
            if step == CHANGE_STEP_2:
                self.metabolic_cost = METABOLIC_COST_INCREASE
                print(f"\n--- Step {step}: METABOLIC COST INCREASED to {self.metabolic_cost} ---")
                # Reset perturb magnitude to encourage re-exploration
                self.perturb_magnitude = PERTURB_MAGNITUDE_INIT * EXPLORE_BOOST_FACTOR
                self.best_performance_overall = -np.inf # Reset best performance

            # 1. Sense: Measure current (C, R) at current (E, S) under current metabolic cost
            current_c, current_r = self.run_step_simulation(self.energy_influx, self.stability_coupling, self.metabolic_cost)
            current_performance = self.calculate_performance(current_c, current_r)
            
            # --- Meta-Adaptation Logic ---
            # Update history for stagnation check
            self.last_performance_history.pop(0)
            self.last_performance_history.append(current_performance)

            # Check for stagnation
            stagnation_threshold = 0.01 # Performance hasn't improved much
            if (current_performance - np.mean(self.last_performance_history)) < stagnation_threshold and step > STAGNATION_WINDOW:
                self.perturb_magnitude *= EXPLORE_BOOST_FACTOR # Explore more
                self.perturb_magnitude = np.clip(self.perturb_magnitude, 0.001, 0.1) # Bounds
                # print(f"Stagnation detected, perturb_magnitude increased to {self.perturb_magnitude:.4f}")
            elif current_performance > self.best_performance_overall + stagnation_threshold:
                self.perturb_magnitude *= EXPLOIT_REDUCE_FACTOR # Exploit more
                self.perturb_magnitude = np.clip(self.perturb_magnitude, 0.001, 0.1) # Bounds
                self.best_performance_overall = current_performance
                # print(f"Performance improved, perturb_magnitude reduced to {self.perturb_magnitude:.4f}")

            # 2. Agency: Probabilistic Hill Climbing with adaptive perturb_magnitude
            # Propose a new (E,S) state
            trial_E = np.clip(self.energy_influx + np.random.normal(0, self.perturb_magnitude), 0.01, 0.3)
            trial_S = np.clip(self.stability_coupling + np.random.normal(0, self.perturb_magnitude), 0.0, 0.8)
            
            # Simulate the trial state with current metabolic cost
            trial_c, trial_r = self.run_step_simulation(trial_E, trial_S, self.metabolic_cost)
            trial_performance = self.calculate_performance(trial_c, trial_r)

            # Decide to accept or reject trial state
            if trial_performance > current_performance: # If new state is better
                self.energy_influx = trial_E
                self.stability_coupling = trial_S
                # Update current C,R and performance for logging (it's the new 'best')
                current_c, current_r = trial_c, trial_r 
                current_performance = trial_performance
            
            self.history.append({
                "step": step,
                "E": self.energy_influx,
                "S": self.stability_coupling,
                "C": current_c,
                "R": current_r,
                "target_C": self.c_target,
                "target_R": self.r_target,
                "metabolic_cost": self.metabolic_cost,
                "performance": current_performance,
                "perturb_magnitude": self.perturb_magnitude
            })
            
            print(f"Step {step:03d} | E={self.energy_influx:.2f} S={self.stability_coupling:.2f} | C={current_c:.3f} R={current_r:.3f} | Target C={self.c_target:.1f} R={self.r_target:.1f} | Cost={self.metabolic_cost:.2f} | Perturb={self.perturb_magnitude:.4f} | Perf={current_performance:.3f}")
            
        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: META-ADAPTIVE CONTROL ---")
        
        Es = [d["E"] for d in self.history]
        Ss = [d["S"] for d in self.history]
        Cs = [d["C"] for d in self.history]
        Rs = [d["R"] for d in self.history]
        target_Cs = [d["target_C"] for d in self.history]
        target_Rs = [d["target_R"] for d in self.history]
        metabolic_costs = [d["metabolic_cost"] for d in self.history]
        perturb_magnitudes = [d["perturb_magnitude"] for d in self.history]
        performances = [d["performance"] for d in self.history]
        steps = [d["step"] for d in self.history]

        plt.figure(figsize=(12, 12))

        plt.subplot(411)
        plt.plot(steps, Es, label='E (Energy Influx)')
        plt.plot(steps, Ss, label='S (Stability Coupling)')
        plt.title('Agent Control Parameters (E, S) over Time')
        plt.xlabel('Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)

        plt.subplot(412)
        plt.plot(steps, Cs, label='C (Complexity)')
        plt.plot(steps, Rs, label='R (Order)')
        plt.plot(steps, target_Cs, 'c--', label='Target C')
        plt.plot(steps, target_Rs, 'm--', label='Target R')
        plt.title('Emergent Properties (C, R) vs Targets over Time')
        plt.xlabel('Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(413)
        plt.plot(steps, metabolic_costs, label='Metabolic Cost', color='red')
        plt.title('Metabolic Cost over Time')
        plt.xlabel('Step')
        plt.ylabel('Cost')
        plt.legend()
        plt.grid(True)

        plt.subplot(414)
        plt.plot(steps, perturb_magnitudes, label='Perturb Magnitude', color='green')
        plt.plot(steps, performances, label='Performance', color='purple', linestyle=':')
        plt.title('Meta-Adaptation (Perturb Magnitude) and Performance')
        plt.xlabel('Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "meta_adaptive_control_trajectory.png"))
        plt.close()
        print(f"Meta-adaptive control trajectory plot saved to {os.path.join(self.results_dir, 'meta_adaptive_control_trajectory.png')}")

        final_state = self.history[-1]
        converged_final = bool(abs(final_state["C"] - final_state["target_C"]) < 0.05 and abs(final_state["R"] - final_state["target_R"]) < 0.05)

        results = {
            "converged_final": converged_final,
            "final_E": final_state["E"],
            "final_S": final_state["S"],
            "final_C": final_state["C"],
            "final_R": final_state["R"],
            "target_C_final": final_state["target_C"],
            "target_R_final": final_state["target_R"],
            "metabolic_cost_final": final_state["metabolic_cost"],
            "steps_taken": len(self.history)
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Results saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    plt.switch_backend('Agg') 
    eng = MetaAdaptationTSF6()
    eng.run()
