import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel

sys.path.append(os.path.abspath("."))
from src.fractal.agent import FractalAgent

# --- TSF-12 CONFIGURATION ---
EXPERIMENT_ID = "TSF-12"
TITLE = "Optimal Control within Reachable Phase Space"
AGENTS_PER_CELL = 20
DURATION = 300 # Longer duration for adaptation scenarios
MODEL_UPDATE_INTERVAL = 10 # Steps between model updates
INITIAL_RANDOM_SAMPLES = 20 # Initial random samples for GPR model training
CANDIDATE_GRID_DENSITY = 20 # Density of (E,S) grid for global search

# GPR specific parameters (from TSF-8/9/10)
GPR_ALPHA = 1e-5 

# Parameter ranges (same as TSF-2)
E_MIN, E_MAX = 0.01, 0.3
S_MIN, S_MAX = 0.0, 0.8

# Initial Realistic Target Regime (Derived from TSF-11 reachability analysis)
# Example: a point within the "Balanced Emergence" or "Chaotic Complexity"
# For this run, let's pick C=0.15, R=0.4 - assuming it's reachable.
C_TARGET_INIT = 0.15
R_TARGET_INIT = 0.4

# Changing Conditions Scenarios (same as TSF-5/6/7)
CHANGE_STEP_1 = 100 # Change target at this step
CHANGE_STEP_2 = 200 # Change metabolic cost at this step

C_TARGET_SHIFT = 0.25 # New target C
R_TARGET_SHIFT = 0.65 # New target R (shifted into a different known regime)
METABOLIC_COST_INIT = 0.02
METABOLIC_COST_INCREASE = 0.04 # New metabolic cost

class OptimalReachableControlTSF12:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.history = []

        # Internal GPR models and data store
        kernel_C = ConstantKernel(1.0) * RBF(length_scale=[0.1, 0.1])
        kernel_R = ConstantKernel(1.0) * RBF(length_scale=[0.1, 0.1])
        self.model_C = GaussianProcessRegressor(kernel=kernel_C, alpha=GPR_ALPHA, normalize_y=True)
        self.model_R = GaussianProcessRegressor(kernel=kernel_R, alpha=GPR_ALPHA, normalize_y=True)
        
        self.global_map_data_X = [] 
        self.global_map_yC = []
        self.global_map_yR = []

        # Initial control parameters (E, S)
        self.energy_influx = np.random.uniform(E_MIN, E_MAX)
        self.stability_coupling = np.random.uniform(S_MIN, S_MAX)
        
        # Internal state for the simulation loop
        self.metabolic_cost = METABOLIC_COST_INIT
        self.c_target = C_TARGET_INIT
        self.r_target = R_TARGET_INIT

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
        Maximizing this is minimizing distance.
        """
        dist_c = abs(c_val - self.c_target)
        dist_r = abs(r_val - self.r_target)
        return -(dist_c + dist_r) 

    def _train_gpr_models(self):
        """Trains the GPR models using the collected data."""
        if len(self.global_map_data_X) > 1: # GPR needs at least 2 samples
            self.model_C.fit(np.array(self.global_map_data_X), np.array(self.global_map_yC))
            self.model_R.fit(np.array(self.global_map_data_X), np.array(self.global_map_yR))
            # print("Global GPR models trained.")
            return True
        else:
            # print("Not enough global map data to train GPR models yet.")
            return False

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Initial Target: C={self.c_target}, R={self.r_target}")
        
        # Initial random exploration to build first global model
        print(f"Performing {INITIAL_RANDOM_SAMPLES} initial random samples for global model...")
        for _ in range(INITIAL_RANDOM_SAMPLES):
            e_sample = np.random.uniform(E_MIN, E_MAX)
            s_sample = np.random.uniform(S_MIN, S_MAX)
            c, r = self.run_step_simulation(e_sample, s_sample, self.metabolic_cost)
            self.global_map_data_X.append([e_sample, s_sample])
            self.global_map_yC.append(c)
            self.global_map_yR.append(r)
        self._train_gpr_models() # Train initial model
        print(f"Initial global model trained with {len(self.global_map_data_X)} samples.")

        # Start main control loop
        for step in range(DURATION):
            # --- Scenario Changes ---
            if step == CHANGE_STEP_1:
                self.c_target = C_TARGET_SHIFT
                self.r_target = R_TARGET_SHIFT
                print(f"\n--- Step {step}: TARGET SHIFTED to C={self.c_target}, R={self.r_target} ---")
                # When conditions change, the global map is invalidated. Re-explore.
                self.global_map_data_X = []
                self.global_map_yC = []
                self.global_map_yR = []
                for _ in range(INITIAL_RANDOM_SAMPLES): # Re-explore to build new model
                    e_pert = np.clip(self.energy_influx + np.random.normal(0, 0.05), E_MIN, E_MAX)
                    s_pert = np.clip(self.stability_coupling + np.random.normal(0, 0.05), S_MIN, S_MAX)
                    c, r = self.run_step_simulation(e_pert, s_pert, self.metabolic_cost)
                    self.global_map_data_X.append([e_pert, s_pert])
                    self.global_map_yC.append(c)
                    self.global_map_yR.append(r)
                self._train_gpr_models()
            
            if step == CHANGE_STEP_2:
                self.metabolic_cost = METABOLIC_COST_INCREASE
                print(f"\n--- Step {step}: METABOLIC COST INCREASED to {self.metabolic_cost} ---")
                # Re-explore locally to build new model for changed physics.
                self.global_map_data_X = []
                self.global_map_yC = []
                self.global_map_yR = []
                for _ in range(INITIAL_RANDOM_SAMPLES): # Re-explore to build new model
                    e_pert = np.clip(self.energy_influx + np.random.normal(0, 0.05), E_MIN, E_MAX)
                    s_pert = np.clip(self.stability_coupling + np.random.normal(0, 0.05), S_MIN, S_MAX)
                    c, r = self.run_step_simulation(e_pert, s_pert, self.metabolic_cost)
                    self.global_map_data_X.append([e_pert, s_pert])
                    self.global_map_yC.append(c)
                    self.global_map_yR.append(r)
                self._train_gpr_models()

            # 1. Query current (C, R) at current (E, S) from simulation
            current_c, current_r = self.run_step_simulation(self.energy_influx, self.stability_coupling, self.metabolic_cost)
            
            # Add current observation for model training
            self.global_map_data_X.append([self.energy_influx, self.stability_coupling])
            self.global_map_yC.append(current_c)
            self.global_map_yR.append(current_r)
            
            # 2. Update Model Periodically
            if step > INITIAL_RANDOM_SAMPLES and (step % MODEL_UPDATE_INTERVAL == 0 or step == CHANGE_STEP_1 + 1 or step == CHANGE_STEP_2 + 1):
                self._train_gpr_models()
                # print(f"Model updated at step {step}.")

            # 3. Global Planning: Predict & Select Best Action from a global grid
            best_performance_score = -np.inf
            best_E_action = self.energy_influx
            best_S_action = self.stability_coupling

            # Generate candidate (E,S) points across the entire defined phase space
            e_candidates = np.linspace(E_MIN, E_MAX, CANDIDATE_GRID_DENSITY)
            s_candidates = np.linspace(S_MIN, S_MAX, CANDIDATE_GRID_DENSITY)
            
            candidate_points_grid = []
            for ec in e_candidates:
                for sc in s_candidates:
                    candidate_points_grid.append([ec, sc])
            candidate_points_grid = np.array(candidate_points_grid)

            if len(self.global_map_data_X) > 1: # Only use model if trained
                predicted_C_mean = self.model_C.predict(candidate_points_grid) 
                predicted_R_mean = self.model_R.predict(candidate_points_grid)

                for i, (cand_E, cand_S) in enumerate(candidate_points_grid):
                    predicted_C = predicted_C_mean[i]
                    predicted_R = predicted_R_mean[i]
                    
                    # Evaluate predicted performance
                    predicted_performance = self.calculate_performance(predicted_C, predicted_R)
                    
                    if predicted_performance > best_performance_score:
                        best_performance_score = predicted_performance
                        best_E_action = cand_E
                        best_S_action = cand_S
            
            # Apply the best predicted action
            self.energy_influx = best_E_action
            self.stability_coupling = best_S_action
            
            self.history.append({
                "step": step,
                "E": self.energy_influx,
                "S": self.stability_coupling,
                "C": current_c,
                "R": current_r,
                "target_C": self.c_target,
                "target_R": self.r_target,
                "metabolic_cost": self.metabolic_cost,
                "performance": self.calculate_performance(current_c, current_r)
            })
            
            print(f"Step {step:03d} | E={self.energy_influx:.2f} S={self.stability_coupling:.2f} | C={current_c:.3f} R={current_r:.3f} | Target C={self.c_target:.1f} R={self.r_target:.1f} | Cost={self.metabolic_cost:.2f} | Perf={self.history[-1]['performance']:.3f}")
            
            # Check for convergence
            if abs(current_c - self.c_target) < 0.05 and abs(current_r - self.r_target) < 0.05:
                print(f"Converged to target (C,R) at step {step}")
                # We do not return so it can adapt to changes.

        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: OPTIMAL REACHABLE CONTROL ---")
        
        Es = [d["E"] for d in self.history]
        Ss = [d["S"] for d in self.history]
        Cs = [d["C"] for d in self.history]
        Rs = [d["R"] for d in self.history]
        target_Cs = [d["target_C"] for d in self.history]
        target_Rs = [d["target_R"] for d in self.history]
        metabolic_costs = [d["metabolic_cost"] for d in self.history]
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
        plt.plot(steps, performances, label='Performance', color='purple')
        plt.title('Performance (Negative Distance to Target)')
        plt.xlabel('Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "optimal_reachable_control_trajectory.png"))
        plt.close()
        print(f"Optimal reachable control trajectory plot saved to {os.path.join(self.results_dir, 'optimal_reachable_control_trajectory.png')}")

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
    eng = OptimalReachableControlTSF12()
    eng.run()