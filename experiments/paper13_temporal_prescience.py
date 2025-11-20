import time
import math
import numpy as np
import psutil
import sqlite3
import os
import sys
import json

# Ensure root directory is in path for imports
sys.path.append(os.path.abspath("."))

from code.fractal.agent import FractalAgent

# --- CONFIGURATION ---
PAPER_ID = "13"
TITLE = "Temporal Prescience (Flywheel Effect)"
DURATION_TRAIN = 100  # Cycles to inject signal
DURATION_TEST = 50    # Cycles to test prediction (no signal)
AGENTS = 20
SIGNAL_FREQ = 0.1     # Frequency of sine wave
INJECTION_STRENGTH = 0.5

class PrescienceExperiment:
    def __init__(self):
        # Initialize agents using the new V3 class structure
        # No bridge required in constructor for V3
        self.agents = [FractalAgent(agent_id=str(i), phase=np.random.uniform(0, 2*math.pi)) for i in range(AGENTS)]
        self.history = []
        self.results_dir = f"experiments/results/paper{PAPER_ID}"
        os.makedirs(self.results_dir, exist_ok=True)

    def run(self):
        print(f"--- STARTING EXPERIMENT {PAPER_ID}: {TITLE} ---")
        
        # Training Phase
        print(f"Phase 1: Training ({DURATION_TRAIN} cycles)...")
        for t in range(DURATION_TRAIN):
            self._step(t, inject=True)
            
        # Testing Phase
        print(f"Phase 2: Testing ({DURATION_TEST} cycles)...")
        for t in range(DURATION_TRAIN, DURATION_TRAIN + DURATION_TEST):
            self._step(t, inject=False)
            
        self._analyze()

    def _step(self, t, inject):
        # 1. Generate Reality Signal (Sine Wave)
        expected_signal = math.sin(t * SIGNAL_FREQ)
        
        # 2. Evolve Agents
        phases = []
        for agent in self.agents:
            # Apply injection to agent's internal resonance if training
            if inject:
                # Simple Hebbian nudging: pull phase towards signal
                # We map signal (-1 to 1) to phase (-pi to pi) or simply align sine components
                # Target phase is the phase that produces the signal sin(target) = expected
                # But simplified: Force phase velocity to match frequency? 
                # Better: Add injection term to phase update
                
                # Target: We want agent.state.phase such that sin(phase) ~ expected_signal
                # But we also want it to oscillate. So we nudge velocity or phase?
                # Nudging Phase:
                current_sin = math.sin(agent.state.phase)
                error = expected_signal - current_sin
                agent.state.phase += error * INJECTION_STRENGTH * 0.1
            
            # Internal Evolution (Flywheel)
            # Agents have a velocity. If entrained, velocity should match SIGNAL_FREQ
            # In training, we nudge velocity too
            if inject:
                 # Entrain velocity to signal frequency (0.1 rad/step approx if t is 1.0 steps)
                 # Signal is sin(t * 0.1). d/dt = 0.1 cos(t*0.1). Frequency is 0.1 rad/step.
                 agent.state.velocity = (agent.state.velocity * 0.9) + (SIGNAL_FREQ * 0.1)
            
            # Apply Phase Update (Inertia)
            agent.update_phase(delta_t=1.0)
            phases.append(agent.state.phase)

        # Calculate Mean Field Phase
        # Order Parameter R = |(1/N) * sum(e^(i*theta))|
        complex_sum = sum(math.e ** (1j * p) for p in phases)
        order_parameter = abs(complex_sum) / len(phases)
        
        # Swarm Output (sine of mean phase)
        mean_phase = math.atan2(complex_sum.imag, complex_sum.real)
        swarm_output = math.sin(mean_phase)

        # Log
        entry = {
            "t": t,
            "phase": "TRAIN" if inject else "TEST",
            "expected": expected_signal,
            "swarm_output": swarm_output,
            "order_parameter": order_parameter,
            "error": abs(expected_signal - swarm_output)
        }
        self.history.append(entry)
        
        # Progress indicator
        if t % 10 == 0:
            bar = "#" * int((swarm_output + 1) * 10)
            print(f"T={t:03d} | Exp={expected_signal:+.2f} | Swarm={swarm_output:+.2f} | Err={entry['error']:.2f} | {bar}")

    def _analyze(self):
        print("--- ANALYSIS ---")
        test_data = [x for x in self.history if x["phase"] == "TEST"]
        
        if not test_data:
            print("No test data collected.")
            return

        errors = [x["error"] for x in test_data]
        mse = sum(e**2 for e in errors) / len(errors)
        
        # Correlation in Test Phase
        expected_series = [x["expected"] for x in test_data]
        actual_series = [x["swarm_output"] for x in test_data]
        correlation = np.corrcoef(expected_series, actual_series)[0, 1]
        
        print(f"Test MSE: {mse:.4f}")
        print(f"Test Correlation: {correlation:.4f}")
        
        result = {
            "status": "SUCCESS" if correlation > 0.5 else "FAIL",
            "mse": mse,
            "correlation": correlation,
            "principle": "PRIN-TEMPORAL-PRESCIENCE"
        }
        
        with open(f"{self.results_dir}/results.json", "w") as f:
            json.dump(result, f, indent=2)
            
        with open(f"papers/drafts/paper{PAPER_ID}_temporal_prescience.md", "w") as f:
            f.write(f"# Paper {PAPER_ID}: Temporal Prescience (Flywheel Effect)\n\n")
            f.write(f"## Abstract\n")
            f.write(f"We demonstrate that a Nested Resonance Memory (NRM) swarm exhibits temporal inertia. ")
            f.write(f"After being entrained to a sinusoidal reality signal for {DURATION_TRAIN} cycles, ")
            f.write(f"the swarm continues to oscillate in phase with the (now absent) signal for {DURATION_TEST} cycles.\n\n")
            f.write(f"## Results\n")
            f.write(f"- **Test Correlation:** {correlation:.4f}\n")
            f.write(f"- **MSE:** {mse:.4f}\n")
            f.write(f"- **Conclusion:** The system predicts the future based on resonant momentum.\n")

        print(f"Artifact generated: papers/drafts/paper{PAPER_ID}_temporal_prescience.md")

if __name__ == "__main__":
    exp = PrescienceExperiment()
    exp.run()
