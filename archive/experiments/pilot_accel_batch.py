import math
import numpy as np
import os
import sys
import json

sys.path.append(os.path.abspath("."))
from code.fractal.agent import FractalAgent

# --- CONFIGURATION ---
DURATION = 100 
AGENTS = 20
MAX_ENERGY = 2.0

class BatchAccelerator:
    def __init__(self):
        self.results_dir = "experiments/results/paper3_ACCEL_BATCH"
        os.makedirs(self.results_dir, exist_ok=True)

    def run_simulation(self, h2_reality, h4_throttling, h5_recovery):
        agents = [FractalAgent(agent_id=str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS)]
        
        series = []
        
        for t in range(DURATION):
            # Base Resource
            for agent in agents:
                agent.update_energy(0.04, max_energy=MAX_ENERGY)
            
            # H2: Reality Injection (Periodic)
            if h2_reality:
                resource = max(0, math.sin(t * 0.1))
                for agent in agents:
                    if np.random.random() < 0.2:
                        agent.update_energy(resource * 0.5, max_energy=MAX_ENERGY)

            # H4: Throttling (Capacity Constraint)
            if h4_throttling:
                limit = 1.2
                for agent in agents:
                    if agent.state.energy > limit:
                        # Drain excess (Hard Cap simulation)
                        agent.state.energy = limit
            
            # H5: Recovery (Safety Net)
            if h5_recovery:
                for agent in agents:
                    if agent.state.energy < 0.5:
                        agent.update_energy(0.02, max_energy=MAX_ENERGY)

            # Evolve
            alive_agents = []
            total_e = 0
            for agent in agents:
                agent.update_energy(-0.05, max_energy=MAX_ENERGY) # High stress
                agent.update_phase(1.0)
                if agent.state.energy > 0:
                    alive_agents.append(agent)
                    total_e += agent.state.energy
            
            agents = alive_agents
            series.append(total_e)
            if len(agents) == 0: break
            
        return series[-1] if series else 0

    def run_pair(self, name, h2, h4, h5):
        print(f"--- Analyzing {name} ---")
        # Baseline (None)
        e_00 = self.run_simulation(False, False, False)
        
        # Factor A
        e_10 = self.run_simulation(h2, h4, h5) # This logic is flawed. Need individual toggles.
        # Let's redefine.
        
        pass

    def analyze_c258(self):
        print("\n--- C258: H2 (Reality) x H4 (Throttling) ---")
        e_00 = self.run_simulation(False, False, False)
        e_10 = self.run_simulation(True, False, False) # H2 only
        e_01 = self.run_simulation(False, True, False) # H4 only
        e_11 = self.run_simulation(True, True, False)  # H2 + H4
        
        eff_h2 = e_10 - e_00
        eff_h4 = e_01 - e_00
        eff_comb = e_11 - e_00
        synergy = eff_comb - (eff_h2 + eff_h4)
        print(f"Synergy: {synergy:+.2f}")
        return synergy

    def analyze_c259(self):
        print("\n--- C259: H2 (Reality) x H5 (Recovery) ---")
        e_00 = self.run_simulation(False, False, False)
        e_10 = self.run_simulation(True, False, False) # H2 only
        e_01 = self.run_simulation(False, False, True) # H5 only
        e_11 = self.run_simulation(True, False, True)  # H2 + H5
        
        eff_h2 = e_10 - e_00
        eff_h5 = e_01 - e_00
        eff_comb = e_11 - e_00
        synergy = eff_comb - (eff_h2 + eff_h5)
        print(f"Synergy: {synergy:+.2f}")
        return synergy

    def analyze_c260(self):
        print("\n--- C260: H4 (Throttling) x H5 (Recovery) ---")
        e_00 = self.run_simulation(False, False, False)
        e_10 = self.run_simulation(False, True, False) # H4 only
        e_01 = self.run_simulation(False, False, True) # H5 only
        e_11 = self.run_simulation(False, True, True)  # H4 + H5
        
        eff_h4 = e_10 - e_00
        eff_h5 = e_01 - e_00
        eff_comb = e_11 - e_00
        synergy = eff_comb - (eff_h4 + eff_h5)
        print(f"Synergy: {synergy:+.2f}")
        return synergy

    def run(self):
        syn_258 = self.analyze_c258()
        syn_259 = self.analyze_c259()
        syn_260 = self.analyze_c260()
        
        results = {
            "C258": syn_258,
            "C259": syn_259,
            "C260": syn_260
        }
        
        with open(f"{self.results_dir}/batch_results.json", "w") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    exp = BatchAccelerator()
    exp.run()
