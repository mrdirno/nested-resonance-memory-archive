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

# --- TSF-9 CONFIGURATION ---
EXPERIMENT_ID = "TSF-9"
TITLE = "Active Learning for Phase Space Mapping"
AGENTS_PER_CELL = 20
DURATION = 200 # Number of active learning steps
INITIAL_RANDOM_SAMPLES = 10 # Initial random samples before active learning starts
NUM_CANDIDATE_POINTS = 100 # Number of candidate points to evaluate for next sample
EXPLORATION_FACTOR = 2.0 # Kappa for UCB acquisition function (higher means more exploration)

# Parameter ranges (same as TSF-2)
E_MIN, E_MAX = 0.01, 0.3
S_MIN, S_MAX = 0.0, 0.8

class ActiveLearningMapperTSF9:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.history = []

        # GPR models and data store
        kernel_C = ConstantKernel(1.0) * RBF(length_scale=[0.1, 0.1])
        kernel_R = ConstantKernel(1.0) * RBF(length_scale=[0.1, 0.1])
        self.model_C = GaussianProcessRegressor(kernel=kernel_C, alpha=1e-5, normalize_y=True)
        self.model_R = GaussianProcessRegressor(kernel=kernel_R, alpha=1e-5, normalize_y=True)
        
        self.model_data_X = [] # (E, S) pairs
        self.model_data_yC = [] # C values
        self.model_data_yR = [] # R values

        # Internal state for the simulation loop (fixed for mapping, not adaptive control)
        self.metabolic_cost = 0.02 # Constant for mapping phase space

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

    def update_gpr_models(self):
        """Train GPR models if enough data is available."""
        if len(self.model_data_X) > 1: # GPR needs at least 2 samples
            self.model_C.fit(np.array(self.model_data_X), np.array(self.model_data_yC))
            self.model_R.fit(np.array(self.model_data_X), np.array(self.model_data_yR))

    def select_next_sample(self):
        """
        Selects the next (E, S) point to sample using an acquisition function
        based on predicted uncertainty (maximizes information gain).
        """
        candidate_points = []
        # Generate a grid of candidate points to evaluate (E, S)
        for _ in range(NUM_CANDIDATE_POINTS):
            e_cand = np.random.uniform(E_MIN, E_MAX)
            s_cand = np.random.uniform(S_MIN, S_MAX)
            candidate_points.append([e_cand, s_cand])
        
        candidate_points = np.array(candidate_points)

        if len(self.model_data_X) > 1: # If model is trained, use it for selection
            # Predict C, R and their uncertainties for all candidates
            predicted_C_mean, predicted_C_std = self.model_C.predict(candidate_points, return_std=True)
            predicted_R_mean, predicted_R_std = self.model_R.predict(candidate_points, return_std=True)

            best_acquisition_score = -np.inf
            next_E, next_S = None, None

            for i, (cand_E, cand_S) in enumerate(candidate_points):
                # Acquisition function: UCB for maximizing uncertainty (exploration)
                # Maximize C uncertainty + R uncertainty
                acquisition_score = predicted_C_std[i] + predicted_R_std[i] # Simple sum of uncertainties
                
                if acquisition_score > best_acquisition_score:
                    best_acquisition_score = acquisition_score
                    next_E, next_S = cand_E, cand_S
            
            return next_E, next_S
        else: # Fallback to random if model not trained yet
            return np.random.uniform(E_MIN, E_MAX), np.random.uniform(S_MIN, S_MAX)

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Goal: Build a comprehensive map of (E,S) -> (C,R) phase space.")
        
        # 1. Initial random sampling
        print(f"Performing {INITIAL_RANDOM_SAMPLES} initial random samples...")
        for i in range(INITIAL_RANDOM_SAMPLES):
            e = np.random.uniform(E_MIN, E_MAX)
            s = np.random.uniform(S_MIN, S_MAX)
            c, r = self.run_step_simulation(e, s, self.metabolic_cost)
            self.model_data_X.append([e, s])
            self.model_data_yC.append(c)
            self.model_data_yR.append(r)
            self.history.append({"step": i, "E": e, "S": s, "C": c, "R": r})

        # 2. Start active learning loop
        for step in range(INITIAL_RANDOM_SAMPLES, DURATION):
            self.update_gpr_models() # Update model with all collected data
            next_E, next_S = self.select_next_sample() # Select next point based on model uncertainty
            
            c, r = self.run_step_simulation(next_E, next_S, self.metabolic_cost)
            self.model_data_X.append([next_E, next_S])
            self.model_data_yC.append(c)
            self.model_data_yR.append(r)
            
            self.history.append({"step": step, "E": next_E, "S": next_S, "C": c, "R": r})
            
            print(f"Step {step:03d} | Sampled E={next_E:.2f}, S={next_S:.2f} | C={c:.3f}, R={r:.3f}")
            
        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: ACTIVE LEARNING MAPPER ---")
        
        self.update_gpr_models() # Final model update

        # Evaluate model accuracy on a validation grid
        grid_size = 30
        E_test = np.linspace(E_MIN, E_MAX, grid_size)
        S_test = np.linspace(S_MIN, S_MAX, grid_size)
        
        X_test = []
        for e in E_test:
            for s in S_test:
                X_test.append([e, s])
        X_test = np.array(X_test)

        predicted_C, std_C = self.model_C.predict(X_test, return_std=True)
        predicted_R, std_R = self.model_R.predict(X_test, return_std=True)

        # Plotting the learned maps and uncertainty
        plt.figure(figsize=(15, 10))

        plt.subplot(221)
        plt.imshow(predicted_C.reshape(grid_size, grid_size).T, origin='lower', extent=[E_MIN, E_MAX, S_MIN, S_MAX], aspect='auto', cmap='viridis')
        plt.colorbar(label='Predicted C')
        plt.xlabel('Energy Influx (E)')
        plt.ylabel('Stability Coupling (S)')
        plt.title('Predicted C Map')

        plt.subplot(222)
        plt.imshow(std_C.reshape(grid_size, grid_size).T, origin='lower', extent=[E_MIN, E_MAX, S_MIN, S_MAX], aspect='auto', cmap='magma')
        plt.colorbar(label='C Uncertainty')
        plt.xlabel('Energy Influx (E)')
        plt.ylabel('Stability Coupling (S)')
        plt.title('C Uncertainty Map')

        plt.subplot(223)
        plt.imshow(predicted_R.reshape(grid_size, grid_size).T, origin='lower', extent=[E_MIN, E_MAX, S_MIN, S_MAX], aspect='auto', cmap='viridis')
        plt.colorbar(label='Predicted R')
        plt.xlabel('Energy Influx (E)')
        plt.ylabel('Stability Coupling (S)')
        plt.title('Predicted R Map')

        plt.subplot(224)
        plt.imshow(std_R.reshape(grid_size, grid_size).T, origin='lower', extent=[E_MIN, E_MAX, S_MIN, S_MAX], aspect='auto', cmap='magma')
        plt.colorbar(label='R Uncertainty')
        plt.xlabel('Energy Influx (E)')
        plt.ylabel('Stability Coupling (S)')
        plt.title('R Uncertainty Map')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "phase_space_maps.png"))
        plt.close()
        print(f"Phase space maps saved to {os.path.join(self.results_dir, 'phase_space_maps.png')}")

        results = {
            "mapped_samples": len(self.model_data_X),
            "final_E": self.model_data_X[-1][0],
            "final_S": self.model_data_X[-1][1],
            "final_C": self.model_data_yC[-1],
            "final_R": self.model_data_yR[-1]
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Results saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    plt.switch_backend('Agg') 
    eng = ActiveLearningMapperTSF9()
    eng.run()
