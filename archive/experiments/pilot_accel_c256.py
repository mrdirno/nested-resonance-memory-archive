import math
import numpy as np
import os
import sys
import json

# Ensure root directory is in path for imports
sys.path.append(os.path.abspath("."))

from code.fractal.agent import FractalAgent

# --- CONFIGURATION ---
PAPER_ID = "3_ACCEL_C256"
TITLE = "Paper 3 Accelerated: H1 x H4 (Pooling x Throttling)"
DURATION = 100 
AGENTS = 20
MAX_ENERGY = 2.0

class AcceleratedC256:
    def __init__(self):
        self.results_dir = f"experiments/results/paper{PAPER_ID}"
        os.makedirs(self.results_dir, exist_ok=True)

    def run_condition(self, h1_pooling, h4_throttling):
        # Initialize Agents with VARIANCE
        agents = [FractalAgent(agent_id=str(i), phase=np.random.uniform(0, 2*math.pi), energy=np.random.uniform(0.5, 1.5)) for i in range(AGENTS)]
        
        series = []
        
        for t in range(DURATION):
            # H4: Spawn Throttling (Simulated by limiting max population/energy influx)
            # Since we have fixed N agents, we simulate throttling by capping Recharge Rate
            # In full simulation, H4 prevents birth. Here, H4 prevents energy gain above threshold.
            
            # Base Resource Influx
            resource_influx = 0.05
            
            if h4_throttling:
                # Stricter Throttling
                limit = 1.2
            else:
                limit = MAX_ENERGY # 2.0
            
            # 1. Resource Intake
            for agent in agents:
                if agent.state.energy < limit:
                    agent.update_energy(resource_influx, max_energy=MAX_ENERGY)
            
            # 2. Energy Pooling (H1)
            if h1_pooling:
                total_energy = sum(a.state.energy for a in agents)
                avg_energy = total_energy / len(agents) if len(agents) > 0 else 0
                for agent in agents:
                    diff = avg_energy - agent.state.energy
                    agent.update_energy(diff * 0.1, max_energy=MAX_ENERGY)
            
            # 3. Evolve (Metabolism)
            total_e = 0
            alive_agents = []
            for agent in agents:
                # Higher Stress
                agent.update_energy(-0.045, max_energy=MAX_ENERGY)
                agent.update_phase(delta_t=1.0)
                if agent.state.energy > 0:
                    alive_agents.append(agent)
                    total_e += agent.state.energy
            
            agents = alive_agents
            series.append(total_e)
            
            if len(agents) == 0:
                break
                
        return series

    def run(self):
        print(f"--- STARTING EXPERIMENT {PAPER_ID}: {TITLE} ---")
        
        # 1. Baseline (OFF-OFF)
        e_00 = self.run_condition(False, False)[-1]
        
        # 2. H1 (ON-OFF)
        e_10 = self.run_condition(True, False)[-1]
        
        # 3. H4 (OFF-ON)
        e_01 = self.run_condition(False, True)[-1]
        
        # 4. H1+H4 (ON-ON)
        e_11 = self.run_condition(True, True)[-1]
        
        # Analysis
        eff_h1 = e_10 - e_00
        eff_h4 = e_01 - e_00
        eff_comb = e_11 - e_00
        expected = eff_h1 + eff_h4
        synergy = eff_comb - expected
        
        print(f"Synergy: {synergy:+.2f}")
        
        # Interpretation
        # H1 distributes energy. H4 caps energy.
        # If H1 distributes energy to agents near the cap, H4 prevents them from gaining more?
        # Actually, H1 is redistribution. H4 is intake limit.
        # Hypothesis: Antagonistic because H1 keeps agents 'average', potentially preventing
        # some from reaching the safety buffer that H4 respects? Or H1 helps survive H4?
        
        prediction = "ANTAGONISTIC" if synergy < 0 else "SYNERGISTIC"
        
        result = {
            "status": "SUCCESS",
            "synergy": synergy,
            "prediction": prediction,
            "principle": "PRIN-HYPER-ACCELERATION"
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    exp = AcceleratedC256()
    exp.run()
