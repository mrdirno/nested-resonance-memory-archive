import numpy as np
import math
import json
import os
import sys

sys.path.append(os.path.abspath("."))
from code.fractal.agent import FractalAgent
from code.pilot.cognitive_engine import CognitiveEngine

# --- TSF-1 CONFIGURATION ---
EXPERIMENT_ID = "TSF-1"
TITLE = "Universal Scaling Search"
DIMENSIONS = 20 # 20x20 grid
AGENTS_PER_CELL = 10
DURATION = 50

class ScienceEngineTSF1:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.data_points = []

    def run_cell(self, energy_influx, stability_coupling):
        """
        Run a single cell of the parameter sweep.
        Energy Influx: Rate of resource addition.
        Stability Coupling: Strength of H1 pooling (homogenization).
        Measure: Complexity (Variance of Agent States).
        """
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi)) for i in range(AGENTS_PER_CELL)]
        
        # Pre-load Pilot
        pilot = CognitiveEngine()
        
        complexity_series = []
        
        for t in range(DURATION):
            # 1. Influx
            for a in agents:
                a.update_energy(energy_influx, max_energy=10.0)
            
            # 2. Coupling (Stability)
            if stability_coupling > 0:
                energies = [a.state.energy for a in agents]
                avg_e = sum(energies)/len(agents)
                for a in agents:
                    # Pull to mean
                    diff = avg_e - a.state.energy
                    a.update_energy(diff * stability_coupling)
            
            # 3. Evolve
            for a in agents:
                a.update_energy(-0.01) # Metabolism
                a.update_phase(1.0)
            
            # 4. Measure Complexity (Standard Deviation of Energy)
            current_energies = [a.state.energy for a in agents]
            complexity = np.std(current_energies)
            complexity_series.append(complexity)
            
        return np.mean(complexity_series[-10:]) # Average of last 10 steps

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Goal: Find C = f(E, S)")
        
        energies = np.linspace(0.01, 0.2, DIMENSIONS)
        couplings = np.linspace(0.0, 0.5, DIMENSIONS)
        
        results_grid = []
        
        for e in energies:
            row = []
            for s in couplings:
                c = self.run_cell(e, s)
                self.data_points.append({"E": e, "S": s, "C": c})
                row.append(c)
                # print(f"E={e:.2f}, S={s:.2f} -> C={c:.4f}") # Verbose
            results_grid.append(row)
            print(f"Completed Row E={e:.2f}")
            
        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: EQUATION DISCOVERY ---")
        # Attempt to fit C = k * E^alpha * S^beta
        # log(C) = log(k) + alpha*log(E) + beta*log(S)
        # But S can be 0, so use S+epsilon or model S differently.
        # Actually, Coupling (S) reduces Complexity. So C ~ E / S?
        
        # Let's try to find correlation
        Es = np.array([d["E"] for d in self.data_points])
        Ss = np.array([d["S"] for d in self.data_points])
        Cs = np.array([d["C"] for d in self.data_points])
        
        # Simple correlation
        corr_EC = np.corrcoef(Es, Cs)[0,1]
        corr_SC = np.corrcoef(Ss, Cs)[0,1]
        
        print(f"Corr(E, C): {corr_EC:.4f} (Expect Positive)")
        print(f"Corr(S, C): {corr_SC:.4f} (Expect Negative)")
        
        equation = "C ~ E^a * S^b"
        
        results = {
            "correlations": {"EC": corr_EC, "SC": corr_SC},
            "data": self.data_points
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Data saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    eng = ScienceEngineTSF1()
    eng.run()
