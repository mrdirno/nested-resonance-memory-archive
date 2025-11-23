import numpy as np
import math
import json
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

sys.path.append(os.path.abspath("."))
from src.fractal.agent import FractalAgent

# --- TSF-11 CONFIGURATION ---
EXPERIMENT_ID = "TSF-11"
TITLE = "Phase Space Reachability Analysis"
DIMENSIONS = 40 # Increased granularity for E and S (40x40 grid)
AGENTS_PER_CELL = 20
DURATION = 200 # Longer duration for stability measurement per cell
ENERGY_RANGE = (0.01, 0.35) # Expanded range
COUPLING_RANGE = (0.0, 0.9) # Expanded range
METABOLIC_COST = 0.02 # Constant metabolic cost for this map

class ScienceEngineTSF11:
    def __init__(self):
        self.results_dir = f"experiments/results/{EXPERIMENT_ID}"
        os.makedirs(self.results_dir, exist_ok=True)
        self.data_points = []

    def run_cell(self, energy_influx, stability_coupling):
        """
        Run a single cell of the parameter sweep.
        Returns: Complexity (Energy Variance), Phase Order (R), and Stability metrics.
        """
        agents = [FractalAgent(str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS_PER_CELL)]
        
        energy_variance_series = []
        phase_order_series = []
        
        # Burn-in period
        for t in range(DURATION // 2):
            self._evolve_agents(agents, energy_influx, stability_coupling, METABOLIC_COST)
            
        # Measurement period
        for t in range(DURATION // 2, DURATION):
            self._evolve_agents(agents, energy_influx, stability_coupling, METABOLIC_COST)
            
            # Measure C and R
            current_phases = [a.state.phase for a in agents]
            current_energies = [a.state.energy for a in agents]

            if not agents or len(current_phases) == 0:
                energy_variance_series.append(0.0)
                phase_order_series.append(0.0)
            else:
                complex_sum = sum(math.e ** (1j * p) for p in current_phases)
                current_order = abs(complex_sum) / len(current_phases)
                energy_variance_series.append(np.std(current_energies))
                phase_order_series.append(current_order)
            
        if not energy_variance_series or not phase_order_series:
            return 0.0, 0.0, 0.0, 0.0 # Extinction
        
        avg_C = np.mean(energy_variance_series)
        avg_R = np.mean(phase_order_series)
        
        # Stability Metric: Inverse of Variance over time. Low variance = high stability.
        # Avoid division by zero for completely stable states (e.g., C=0)
        stability_C = 1.0 / (np.std(energy_variance_series) + 1e-6)
        stability_R = 1.0 / (np.std(phase_order_series) + 1e-6)

        return avg_C, avg_R, stability_C, stability_R
    
    def _evolve_agents(self, agents, energy_influx, stability_coupling, metabolic_cost):
        # Influx
        for a in agents:
            a.update_energy(energy_influx, max_energy=10.0)
        
        # Coupling (Stability - Energy Pooling & Phase Coupling)
        current_phases = [a.state.phase for a in agents]
        current_energies = [a.state.energy for a in agents]

        if len(current_phases) > 0:
            complex_sum = sum(math.e ** (1j * p) for p in current_phases)
            mean_phase = math.atan2(complex_sum.imag, complex_sum.real)
        else:
            mean_phase = 0

        if stability_coupling > 0:
            avg_e = sum(current_energies)/len(agents) if len(agents) > 0 else 0
            for a in agents:
                diff_e = avg_e - a.state.energy
                a.update_energy(diff_e * stability_coupling)
                
                phase_pull = math.sin(mean_phase - a.state.phase) * stability_coupling
                a.state.phase += phase_pull
        
        # Evolve (Metabolism & Phase Update)
        alive_agents = []
        for a in agents:
            a.update_energy(-metabolic_cost)
            a.update_phase(1.0)
            if a.state.energy > 0:
                alive_agents.append(a)
        agents[:] = alive_agents # Modify in place

    def run(self):
        print(f"--- STARTING {EXPERIMENT_ID}: {TITLE} ---")
        print(f"Goal: Map stable (C,R) regions across (E,S) phase space.")
        
        energies = np.linspace(ENERGY_RANGE[0], ENERGY_RANGE[1], DIMENSIONS)
        couplings = np.linspace(COUPLING_RANGE[0], COUPLING_RANGE[1], DIMENSIONS)
        
        for e in energies:
            row_data = []
            for s in couplings:
                avg_C, avg_R, stab_C, stab_R = self.run_cell(e, s)
                self.data_points.append({"E": e, "S": s, "C": avg_C, "R": avg_R, "Stab_C": stab_C, "Stab_R": stab_R})
                row_data.append((avg_C, avg_R, stab_C, stab_R))
            print(f"Completed Row E={e:.2f}")
            
        self._analyze()

    def _analyze(self):
        print("--- ANALYSIS: REACHABILITY MAPPING ---")
        
        Es = np.array([d["E"] for d in self.data_points])
        Ss = np.array([d["S"] for d in self.data_points])
        Cs = np.array([d["C"] for d in self.data_points])
        Rs = np.array([d["R"] for d in self.data_points])
        Stab_Cs = np.array([d["Stab_C"] for d in self.data_points])
        Stab_Rs = np.array([d["Stab_R"] for d in self.data_points])
        
        # Reshape for contour plots
        num_e = len(np.unique(Es))
        num_s = len(np.unique(Ss))
        
        E_grid = Es.reshape(num_e, num_s)
        S_grid = Ss.reshape(num_e, num_s)
        C_grid = Cs.reshape(num_e, num_s)
        R_grid = Rs.reshape(num_e, num_s)
        Stab_C_grid = Stab_Cs.reshape(num_e, num_s)
        Stab_R_grid = Stab_Rs.reshape(num_e, num_s)

        # Plotting the reachable maps
        plt.figure(figsize=(18, 12)) # Wider figure
        
        # Map of C
        plt.subplot(231)
        plt.imshow(C_grid.T, origin='lower', extent=[ENERGY_RANGE[0], ENERGY_RANGE[1], COUPLING_RANGE[0], COUPLING_RANGE[1]], aspect='auto', cmap='viridis', norm=Normalize(vmin=0, vmax=max(1e-6, C_grid.max())))
        plt.colorbar(label='Avg C')
        plt.xlabel('E')
        plt.ylabel('S')
        plt.title('Reachable C Map')

        # Map of R
        plt.subplot(232)
        plt.imshow(R_grid.T, origin='lower', extent=[ENERGY_RANGE[0], ENERGY_RANGE[1], COUPLING_RANGE[0], COUPLING_RANGE[1]], aspect='auto', cmap='plasma', norm=Normalize(vmin=0, vmax=1.0))
        plt.colorbar(label='Avg R')
        plt.xlabel('E')
        plt.ylabel('S')
        plt.title('Reachable R Map')

        # Map of C_Stability
        plt.subplot(233)
        plt.imshow(Stab_C_grid.T, origin='lower', extent=[ENERGY_RANGE[0], ENERGY_RANGE[1], COUPLING_RANGE[0], COUPLING_RANGE[1]], aspect='auto', cmap='magma', norm=Normalize(vmin=0, vmax=max(1e-6, Stab_C_grid.max())))
        plt.colorbar(label='C Stability (1/std)')
        plt.xlabel('E')
        plt.ylabel('S')
        plt.title('C Stability Map')

        # Map of R_Stability
        plt.subplot(234)
        plt.imshow(Stab_R_grid.T, origin='lower', extent=[ENERGY_RANGE[0], ENERGY_RANGE[1], COUPLING_RANGE[0], COUPLING_RANGE[1]], aspect='auto', cmap='cividis', norm=Normalize(vmin=0, vmax=max(1e-6, Stab_R_grid.max())))
        plt.colorbar(label='R Stability (1/std)')
        plt.xlabel('E')
        plt.ylabel('S')
        plt.title('R Stability Map')

        plt.subplot(235) # Scatter plot of reachable C vs R
        plt.scatter(Cs, Rs, c=Es, cmap='viridis', s=20)
        plt.colorbar(label='Energy Influx (E)')
        plt.xlabel('Energy Complexity (C)')
        plt.ylabel('Phase Order (R)')
        plt.title('Reachable (C, R) States (Colored by E)')
        plt.grid(True)
        plt.xlim(0, max(1e-6, Cs.max() * 1.1))
        plt.ylim(0, 1.1)

        plt.subplot(236) # Scatter plot of reachable C vs R
        plt.scatter(Cs, Rs, c=Ss, cmap='plasma', s=20)
        plt.colorbar(label='Stability Coupling (S)')
        plt.xlabel('Energy Complexity (C)')
        plt.ylabel('Phase Order (R)')
        plt.title('Reachable (C, R) States (Colored by S)')
        plt.grid(True)
        plt.xlim(0, max(1e-6, Cs.max() * 1.1))
        plt.ylim(0, 1.1)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, "phase_space_reachability_maps.png"))
        plt.close()
        print(f"Phase space reachability maps saved to {os.path.join(self.results_dir, 'phase_space_reachability_maps.png')}")

        results = {
            "mapped_points": len(self.data_points),
            "E_range": ENERGY_RANGE,
            "S_range": COUPLING_RANGE,
            "metabolic_cost": METABOLIC_COST
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Results saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    plt.switch_backend('Agg') 
    eng = ScienceEngineTSF11()
    eng.run()
