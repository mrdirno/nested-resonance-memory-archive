import math
import numpy as np
import os
import sys
import json

# Ensure root directory is in path for imports
sys.path.append(os.path.abspath("."))

from code.fractal.agent import FractalAgent

# --- CONFIGURATION ---
PAPER_ID = "3_ACCEL"
TITLE = "Paper 3 Accelerated Pilot (Hyper-Acceleration)"
DURATION = 100 # 30x faster than 3000
AGENTS = 20

class AcceleratedExperiment:
    def __init__(self):
        self.results_dir = f"experiments/results/paper{PAPER_ID}"
        os.makedirs(self.results_dir, exist_ok=True)

    def run_condition(self, h1_pooling, h2_reality):
        # Initialize Agents
        agents = [FractalAgent(agent_id=str(i), phase=np.random.uniform(0, 2*math.pi), energy=1.0) for i in range(AGENTS)]
        MAX_ENERGY = 2.0
        
        series = []
        
        for t in range(DURATION):
            # Calculate Mean Phase for Coupling
            phases = [a.state.phase for a in agents]
            if len(phases) > 0:
                complex_sum = sum(math.e ** (1j * p) for p in phases)
                mean_phase = math.atan2(complex_sum.imag, complex_sum.real)
            else:
                mean_phase = 0

            # 1. Reality Injection (H2) - DEPENDS ON PHASE ALIGNMENT
            if h2_reality:
                # Resource has a phase (time-dependent)
                # resource_phase = (t * 0.1) % (2pi)
                resource_phase = (t * 0.1) % (2 * math.pi)
                resource_mag = 1.0 # Fixed magnitude for clarity
                
                for agent in agents:
                    if np.random.random() < 0.2: # Sparse
                        # Resonance factor
                        alignment = math.cos(agent.state.phase - resource_phase)
                        gain = resource_mag * max(0, alignment) # Only gain if aligned
                        agent.update_energy(gain, max_energy=MAX_ENERGY)
            
            # 2. Energy Pooling (H1) + PHASE COUPLING
            if h1_pooling:
                # Share energy (Mean Field Pooling)
                total_energy = sum(a.state.energy for a in agents)
                avg_energy = total_energy / len(agents) if len(agents) > 0 else 0
                
                for agent in agents:
                    # Energy Redistribution
                    diff = avg_energy - agent.state.energy
                    agent.update_energy(diff * 0.1, max_energy=MAX_ENERGY)
                    
                    # Phase Coupling (Pull towards Mean) - THE CONFLICT
                    # d(theta)/dt = K * sin(mean - theta)
                    phase_pull = math.sin(mean_phase - agent.state.phase) * 0.1
                    agent.state.phase += phase_pull
            
            # 3. Evolve (Metabolism + Death)
            alive_agents = []
            total_e = 0
            for agent in agents:
                # Metabolic Cost
                agent.update_energy(-0.01, max_energy=MAX_ENERGY)
                agent.update_phase(delta_t=1.0)
                
                if agent.state.energy > 0:
                    alive_agents.append(agent)
                    total_e += agent.state.energy
            
            agents = alive_agents
            
            # Metric: Total Energy Retention (or Population?)
            # Let's track Total Energy for now
            series.append(total_e)
            
            if len(agents) == 0:
                # Extinction
                series.extend([0] * (DURATION - t - 1))
                break
            
        return series

    def run(self):
        print(f"--- STARTING EXPERIMENT {PAPER_ID}: {TITLE} ---")
        print(f"Goal: Detect Interaction Type in {DURATION} cycles (vs 3000)")
        
        # 1. Run Baseline (OFF-OFF)
        print("Running Baseline...")
        ts_00 = self.run_condition(False, False)
        
        # 2. Run H1 (ON-OFF)
        print("Running H1 (Pooling)...")
        ts_10 = self.run_condition(True, False)
        
        # 3. Run H2 (Reality)
        print("Running H2 (Reality)...")
        ts_01 = self.run_condition(False, True)
        
        # 4. Run H1+H2 (ON-ON)
        print("Running H1+H2 (Combined)...")
        ts_11 = self.run_condition(True, True)
        
        self._analyze(ts_00, ts_10, ts_01, ts_11)

    def _analyze(self, ts_00, ts_10, ts_01, ts_11):
        print("--- ANALYSIS (SPECTRAL PREDICTION) ---")
        
        # Instead of end-point, we look at the *slope* (rate of change) and *stability* (variance)
        # But simple endpoint for now serves as the "Projected" result
        
        # Metric: Final Energy
        e_00 = ts_00[-1]
        e_10 = ts_10[-1]
        e_01 = ts_01[-1]
        e_11 = ts_11[-1]
        
        # Effects (Relative to Baseline)
        eff_h1 = e_10 - e_00
        eff_h2 = e_01 - e_00
        eff_comb = e_11 - e_00
        
        # Interaction Term (Synergy)
        # Synergy = Observed_Combined - (Effect_A + Effect_B)
        # If > 0: Synergy
        # If < 0: Antagonism
        
        expected_additive = eff_h1 + eff_h2
        synergy = eff_comb - expected_additive
        
        print(f"Baseline E: {e_00:.2f}")
        print(f"H1 Effect:  {eff_h1:+.2f}")
        print(f"H2 Effect:  {eff_h2:+.2f}")
        print(f"Combined:   {eff_comb:+.2f}")
        print(f"Expected:   {expected_additive:+.2f}")
        print(f"Synergy:    {synergy:+.2f}")
        
        # Ground Truth Check (C255 was Antagonistic)
        match_ground_truth = synergy < 0
        status = "SUCCESS" if match_ground_truth else "FAIL"
        
        print(f"Prediction: {'ANTAGONISTIC' if synergy < 0 else 'SYNERGISTIC'}")
        print(f"Ground Truth: ANTAGONISTIC")
        print(f"Status: {status}")
        
        result = {
            "status": status,
            "duration": DURATION,
            "synergy": synergy,
            "principle": "PRIN-HYPER-ACCELERATION"
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(result, f, indent=2)

        print(f"Result saved to {self.results_dir}/results.json")

if __name__ == "__main__":
    exp = AcceleratedExperiment()
    exp.run()
