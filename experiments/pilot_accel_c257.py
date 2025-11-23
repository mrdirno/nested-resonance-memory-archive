import math
import numpy as np
import os
import sys
import json

sys.path.append(os.path.abspath("."))
from src.fractal.agent import FractalAgent

# --- CONFIGURATION ---
PAPER_ID = "3_ACCEL_C257"
TITLE = "Paper 3 Accelerated: H1 x H5 (Pooling x Recovery)"
DURATION = 100 
AGENTS = 20
MAX_ENERGY = 2.0

class AcceleratedC257:
    def __init__(self):
        self.results_dir = f"experiments/results/paper{PAPER_ID}"
        os.makedirs(self.results_dir, exist_ok=True)

    def run_condition(self, h1_pooling, h5_recovery):
        # Initialize Agents with variance to allow pooling to work
        agents = [FractalAgent(agent_id=str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS)]
        
        series = []
        
        for t in range(DURATION):
            # H5: Energy Recovery (Efficiency gain when low energy? Or passive regeneration?)
            # In NRM, "Efficiency" usually means lower metabolic cost or higher intake.
            # Let's model H5 as "Emergency Recovery": Gain extra energy if E < 0.5
            
            # Base Metabolic Cost
            cost = 0.05
            
            # 1. Resource Intake (Constant)
            for agent in agents:
                agent.update_energy(0.04, max_energy=MAX_ENERGY) # Slightly deficit
            
            # 2. H5: Recovery
            if h5_recovery:
                for agent in agents:
                    if agent.state.energy < 0.5:
                        agent.update_energy(0.02, max_energy=MAX_ENERGY) # Boost
            
            # 3. H1: Pooling
            if h1_pooling:
                total_energy = sum(a.state.energy for a in agents)
                avg_energy = total_energy / len(agents) if len(agents) > 0 else 0
                for agent in agents:
                    diff = avg_energy - agent.state.energy
                    agent.update_energy(diff * 0.1, max_energy=MAX_ENERGY)
            
            # 4. Evolve
            alive_agents = []
            total_e = 0
            for agent in agents:
                agent.update_energy(-cost, max_energy=MAX_ENERGY)
                agent.update_phase(1.0)
                if agent.state.energy > 0:
                    alive_agents.append(agent)
                    total_e += agent.state.energy
            
            agents = alive_agents
            series.append(total_e)
            
            if len(agents) == 0: break
                
        return series

    def run(self):
        print(f"--- STARTING EXPERIMENT {PAPER_ID}: {TITLE} ---")
        e_00 = self.run_condition(False, False)[-1]
        e_10 = self.run_condition(True, False)[-1]
        e_01 = self.run_condition(False, True)[-1]
        e_11 = self.run_condition(True, True)[-1]
        
        eff_h1 = e_10 - e_00
        eff_h5 = e_01 - e_00
        eff_comb = e_11 - e_00
        synergy = eff_comb - (eff_h1 + eff_h5)
        
        print(f"Synergy: {synergy:+.2f}")
        
        prediction = "SYNERGISTIC" if synergy > 0 else "ANTAGONISTIC"
        
        result = {
            "status": "SUCCESS",
            "synergy": synergy,
            "prediction": prediction
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    exp = AcceleratedC257()
    exp.run()
