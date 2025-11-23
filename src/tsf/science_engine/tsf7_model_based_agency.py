import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression # For model building

sys.path.append(os.path.abspath("."))
from src.fractal.agent import FractalAgent

# --- TSF-7 CONFIGURATION ---
EXPERIMENT_ID = "TSF-7"
TITLE = "Model-Based Agency / Predictive Control"
AGENTS_PER_CELL = 20
DURATION = 300 # Longer duration for adaptation scenarios
MODEL_UPDATE_INTERVAL = 10 # Steps between model updates
EXPLORATION_STEPS = 5 # Initial random exploration steps to build model
NUM_CANDIDATE_PERTS = 10 # Number of candidate perturbations to evaluate with model

# Target Regime (same as TSF-5/6)
C_TARGET_INIT = 0.2
R_TARGET_INIT = 0.6

# Changing Conditions Scenarios (same as TSF-5/6)
CHANGE_STEP_1 = 100 # Change target at this step
CHANGE_STEP_2 = 200 # Change metabolic cost at this step

C_TARGET_SHIFT = 0.4 # New target C
R_TARGET_SHIFT = 0.3 # New target R
METABOLIC_COST_INIT = 0.02
METABOLIC_COST_INCREASE = 0.04 # New metabolic cost

class ModelBasedAgencyTSF7:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.history = []

        # Initial control parameters (E, S)
        self.energy_influx = np.random.uniform(0.01, 0.3)
        self.stability_coupling = np.random.uniform(0.0, 0.8)
        
        # Internal model and data store
        self.model_C = LinearRegression()
        self.model_R = LinearRegression()
        self.model_data_X = [] # (E, S) pairs
        self.model_data_yC = [] # C values
        self.model_data_yR = [] # R values

        # Internal state for the simulation loop
        self.metabolic_cost = METABOLIC_COST_INIT
        self.c_target = C_TARGET_INIT
        self.r_target = R_TARGET_INIT
        self.last_performance = -np.inf

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
        Lower is better (like an error function).
        """
        dist_c = abs(c_val - self.c_target)
        dist_r = abs(r_val - self.r_target)
        return -(dist_c + dist_r) 

    def update_model(self):
        """Build or update the internal linear regression models."""
        if len(self.model_data_X) > 1: # Need at least 2 data points for linear regression
            self.model_C.fit(self.model_data_X, self.model_data_yC)
            self.model_R.fit(self.model_data_X, self.model_data_yR)
        else:
            # print("Not enough data to train model yet.")
            pass # Not an error, just need more data

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Initial Target: C={self.c_target}, R={self.r_target}")
        
        # Initial exploration to build first model
        print("Initial exploration to build phase space model...")
        for _ in range(EXPLORATION_STEPS):
            e_pert = np.random.uniform(0.01, 0.3)
            s_pert = np.random.uniform(0.0, 0.8)
            c, r = self.run_step_simulation(e_pert, s_pert, self.metabolic_cost)
            self.model_data_X.append([e_pert, s_pert])
            self.model_data_yC.append(c)
            self.model_data_yR.append(r)
        self.update_model()
        
        # Start main control loop
        for step in range(DURATION):
            # --- Scenario Changes ---
            if step == CHANGE_STEP_1:
                self.c_target = C_TARGET_SHIFT
                self.r_target = R_TARGET_SHIFT
                print(f"\n--- Step {step}: TARGET SHIFTED to C={self.c_target}, R={self.r_target} ---")
                # Clear and re-explore for new model if phase space changed
                self.model_data_X = []
                self.model_data_yC = []
                self.model_data_yR = []
                for _ in range(EXPLORATION_STEPS):
                    e_pert = np.clip(self.energy_influx + np.random.normal(0, 0.05), 0.01, 0.3)
                    s_pert = np.clip(self.stability_coupling + np.random.normal(0, 0.05), 0.0, 0.8)
                    c, r = self.run_step_simulation(e_pert, s_pert, self.metabolic_cost)
                    self.model_data_X.append([e_pert, s_pert])
                    self.model_data_yC.append(c)
                    self.model_data_yR.append(r)
                self.update_model()
            
            if step == CHANGE_STEP_2:
                self.metabolic_cost = METABOLIC_COST_INCREASE
                print(f"\n--- Step {step}: METABOLIC COST INCREASED to {self.metabolic_cost} ---")
                # Clear and re-explore for new model if phase space changed
                self.model_data_X = []
                self.model_data_yC = []
                self.model_data_yR = []
                for _ in range(EXPLORATION_STEPS):
                    e_pert = np.clip(self.energy_influx + np.random.normal(0, 0.05), 0.01, 0.3)
                    s_pert = np.clip(self.stability_coupling + np.random.normal(0, 0.05), 0.0, 0.8)
                    c, r = self.run_step_simulation(e_pert, s_pert, self.metabolic_cost)
                    self.model_data_X.append([e_pert, s_pert])
                    self.model_data_yC.append(c)
                    self.model_data_yR.append(r)
                self.update_model()


            # 1. Sense current (C, R) at current (E, S)
            current_c, current_r = self.run_step_simulation(self.energy_influx, self.stability_coupling, self.metabolic_cost)
            
            # Store current observation for model training
            self.model_data_X.append([self.energy_influx, self.stability_coupling])
            self.model_data_yC.append(current_c)
            self.model_data_yR.append(current_r)
            
            # 2. Update Model Periodically
            if step > EXPLORATION_STEPS and (step % MODEL_UPDATE_INTERVAL == 0 or step == CHANGE_STEP_1 + 1 or step == CHANGE_STEP_2 + 1):
                self.update_model()
                # print(f"Model updated at step {step}.")

            # 3. Predict & Select Best Action
            if len(self.model_data_X) > 1: # Only use model if trained
                best_predicted_performance = -np.inf
                best_E_action = self.energy_influx
                best_S_action = self.stability_coupling

                for _ in range(NUM_CANDIDATE_PERTS):
                    # Explore nearby (E,S) points
                    candidate_E = np.clip(self.energy_influx + np.random.normal(0, 0.02), 0.01, 0.3)
                    candidate_S = np.clip(self.stability_coupling + np.random.normal(0, 0.02), 0.0, 0.8)
                    
                    # Predict C, R using the internal model
                    predicted_C = self.model_C.predict([[candidate_E, candidate_S]])[0]
                    predicted_R = self.model_R.predict([[candidate_E, candidate_S]])[0]
                    
                    # Evaluate predicted performance
                    predicted_performance = self.calculate_performance(predicted_C, predicted_R)
                    
                    if predicted_performance > best_predicted_performance:
                        best_predicted_performance = predicted_performance
                        best_E_action = candidate_E
                        best_S_action = candidate_S
                
                # Apply the best predicted action
                self.energy_influx = best_E_action
                self.stability_coupling = best_S_action
            else:
                # Fallback to random walk if model not ready (e.g., in initial exploration)
                self.energy_influx = np.clip(self.energy_influx + np.random.normal(0, 0.02), 0.01, 0.3)
                self.stability_coupling = np.clip(self.stability_coupling + np.random.normal(0, 0.02), 0.0, 0.8)
            
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
                # return # Stop if converged

        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: MODEL-BASED AGENCY ---")
        
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
        plt.savefig(os.path.join(self.results_dir, "model_based_control_trajectory.png"))
        plt.close()
        print(f"Model-based control trajectory plot saved to {os.path.join(self.results_dir, 'model_based_control_trajectory.png')}")

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
    eng = ModelBasedAgencyTSF7()
    eng.run()
