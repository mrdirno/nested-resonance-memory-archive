import numpy as np
import math
import json
import os
import sys

sys.path.append(os.path.abspath("."))
from src.fractal.agent import FractalAgent
from src.pilot.cognitive_engine import CognitiveEngine

# --- TSF-2 CONFIGURATION ---
EXPERIMENT_ID = "TSF-2"
TITLE = "Complexity-Order Phase Transition Search"
DIMENSIONS = 20 # 20x20 grid for E and S
AGENTS_PER_CELL = 20
DURATION = 100 # Longer duration for stability
ENERGY_RANGE = (0.01, 0.3)
COUPLING_RANGE = (0.0, 0.8) # Stronger coupling to see freezing

class ScienceEngineTSF2:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.data_points = []

    def run_cell(self, energy_influx, stability_coupling):
        """
        Run a single cell of the parameter sweep.
        Energy Influx: Rate of resource addition.
        Stability Coupling: Strength of H1 pooling and phase coupling.
        Measure: Complexity (Variance of Energy) and Phase Order (R).
        """
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS_PER_CELL)]
        
        energy_variance_series = []
        phase_order_series = []
        
        for t in range(DURATION):
            # 1. Influx
            for a in agents:
                a.update_energy(energy_influx, max_energy=10.0)
            
            # 2. Coupling (Stability - Energy Pooling & Phase Coupling)
            current_phases = [a.state.phase for a in agents]
            current_energies = [a.state.energy for a in agents]

            if len(current_phases) > 0:
                # Phase Order Calculation
                complex_sum = sum(math.e ** (1j * p) for p in current_phases)
                mean_phase = math.atan2(complex_sum.imag, complex_sum.real)
                current_order = abs(complex_sum) / len(current_phases)
            else:
                mean_phase = 0
                current_order = 0

            if stability_coupling > 0:
                # Energy Pooling
                avg_e = sum(current_energies)/len(agents) if len(agents) > 0 else 0
                for a in agents:
                    diff_e = avg_e - a.state.energy
                    a.update_energy(diff_e * stability_coupling)
                    
                    # Phase Coupling
                    phase_pull = math.sin(mean_phase - a.state.phase) * stability_coupling
                    a.state.phase += phase_pull
            
            # 3. Evolve (Metabolism & Phase Update)
            alive_agents = []
            for a in agents:
                a.update_energy(-0.02) # Metabolism slightly higher
                a.update_phase(1.0)
                if a.state.energy > 0:
                    alive_agents.append(a)
            agents = alive_agents
            
            if not agents: # All agents died
                energy_variance_series.append(0.0)
                phase_order_series.append(0.0)
            else:
                energy_variance_series.append(np.std([a.state.energy for a in agents]))
                phase_order_series.append(current_order)
            
        # Return average of last few steps to stabilize measurement
        if not energy_variance_series or not phase_order_series:
            return 0.0, 0.0 # Extinction
        
        return np.mean(energy_variance_series[-DURATION//10:]), np.mean(phase_order_series[-DURATION//10:])

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Goal: Map C and R across E and S phase space for transitions")
        
        energies = np.linspace(ENERGY_RANGE[0], ENERGY_RANGE[1], DIMENSIONS)
        couplings = np.linspace(COUPLING_RANGE[0], COUPLING_RANGE[1], DIMENSIONS)
        
        results_grid = [] # Stores (C, R) tuples
        
        for e in energies:
            row = []
            for s in couplings:
                c, r = self.run_cell(e, s)
                self.data_points.append({"E": e, "S": s, "C": c, "R": r})
                row.append({"C": c, "R": r})
                # print(f"E={e:.2f}, S={s:.2f} -> C={c:.4f}, R={r:.4f}") # Verbose
            results_grid.append(row)
            print(f"Completed Row E={e:.2f}")
            
        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: PHASE TRANSITION DETECTION ---")
        
        Es = np.array([d["E"] for d in self.data_points])
        Ss = np.array([d["S"] for d in self.data_points])
        Cs = np.array([d["C"] for d in self.data_points])
        Rs = np.array([d["R"] for d in self.data_points])
        
        # Look for non-linearities, abrupt changes in C or R with respect to E or S
        # This requires more sophisticated analysis than simple correlations.
        # For now, we print key stats and store data for plotting.
        
        print(f"Min C: {np.min(Cs):.4f}, Max C: {np.max(Cs):.4f}")
        print(f"Min R: {np.min(Rs):.4f}, Max R: {np.max(Rs):.4f}")
        
        # Save raw data for external plotting tools (e.g., Python scripts for 3D plots)
        results = {
            "parameters": {"E_range": ENERGY_RANGE, "S_range": COUPLING_RANGE, "dimensions": DIMENSIONS},
            "data": self.data_points
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Raw data saved to {self.results_dir}/results.json for phase space mapping.")
        print(f"Next step: Visualize the results (C vs E, S and R vs E, S) to identify phase transitions.")


if __name__ == "__main__":
    eng = ScienceEngineTSF2()
    eng.run()
