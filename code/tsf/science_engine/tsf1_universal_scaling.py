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
        Measure: Complexity (Variance of Agent States) and Phase Order.
        """
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi)) for i in range(AGENTS_PER_CELL)]
        
        # Pilot is not directly used in this baseline measurement, but could be for adaptive sampling.
        # pilot = CognitiveEngine()
        
        energy_variance_series = []
        phase_order_series = []
        
        for t in range(DURATION):
            # 1. Influx
            for a in agents:
                a.update_energy(energy_influx, max_energy=10.0)
            
            # 2. Coupling (Stability)
            current_phases = [a.state.phase for a in agents]
            if len(current_phases) > 0:
                complex_sum = sum(math.e ** (1j * p) for p in current_phases)
                mean_phase = math.atan2(complex_sum.imag, complex_sum.real)
                current_order = abs(complex_sum) / len(current_phases)
            else:
                mean_phase = 0
                current_order = 0

            if stability_coupling > 0:
                energies = [a.state.energy for a in agents]
                avg_e = sum(energies)/len(agents)
                for a in agents:
                    # Energy Pooling (H1)
                    diff_e = avg_e - a.state.energy
                    a.update_energy(diff_e * stability_coupling)
                    
                    # Phase Coupling (H1 - the 'stability' component for order)
                    phase_pull = math.sin(mean_phase - a.state.phase) * stability_coupling
                    a.state.phase += phase_pull
            
            # 3. Evolve
            for a in agents:
                a.update_energy(-0.01) # Metabolism
                a.update_phase(1.0)
            
            # 4. Measure Complexity (Standard Deviation of Energy) and Phase Order
            current_energies = [a.state.energy for a in agents]
            energy_variance = np.std(current_energies)
            energy_variance_series.append(energy_variance)
            phase_order_series.append(current_order)
            
        return np.mean(energy_variance_series[-10:]), np.mean(phase_order_series[-10:])

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Goal: Find C, R = f(E, S)")
        
        energies = np.linspace(0.01, 0.2, DIMENSIONS)
        couplings = np.linspace(0.0, 0.5, DIMENSIONS)
        
        results_grid = []
        
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
        print("--- ANALYSIS: EQUATION DISCOVERY ---")
        
        Es = np.array([d["E"] for d in self.data_points])
        Ss = np.array([d["S"] for d in self.data_points])
        Cs = np.array([d["C"] for d in self.data_points])
        Rs = np.array([d["R"] for d in self.data_points])
        
        # Correlations
        corr_EC = np.corrcoef(Es, Cs)[0,1]
        corr_SC = np.corrcoef(Ss, Cs)[0,1]
        corr_SR = np.corrcoef(Ss, Rs)[0,1]
        corr_ER = np.corrcoef(Es, Rs)[0,1] # Expect neutral or slightly positive
        
        print(f"Corr(E, C): {corr_EC:.4f} (Energy vs Energy_Variance - Expect Positive)")
        print(f"Corr(S, C): {corr_SC:.4f} (Coupling vs Energy_Variance - Expect Negative)")
        print(f"Corr(S, R): {corr_SR:.4f} (Coupling vs Phase_Order - Expect Positive)")
        print(f"Corr(E, R): {corr_ER:.4f} (Energy vs Phase_Order - Expect neutral/positive)")
        
        equation = "C ~ E^a * S^b; R ~ S^c * E^d"
        
        results = {
            "correlations": {"EC": corr_EC, "SC": corr_SC, "SR": corr_SR, "ER": corr_ER},
            "data": self.data_points
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Data saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    eng = ScienceEngineTSF1()
    eng.run()
