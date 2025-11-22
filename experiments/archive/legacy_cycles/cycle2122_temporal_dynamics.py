"""
Cycle 2122: Temporal Dynamics
==============================
Can Phase Resonance track changing inputs?

From C2121: Phase is a good static compressor.
Hypothesis: Phase can track a moving target (temporal sequence) better than vectors
because phase rotation maps naturally to time.

Design:
- Input: A sequence of vectors A -> B -> C -> D
- Encoding:
  - Vector: M_t = alpha * M_{t-1} + input_t
  - Phase: theta_t = theta_{t-1} + delta_theta (rotation)
- Task: Predict next item.
"""

import numpy as np
import json
from datetime import datetime

class TemporalDynamics:
    def __init__(self):
        self.dimension = 1024
        self.sequence_length = 10
        self.num_trials = 10

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def run_vector_tracking(self, sequence, seed):
        """Standard exponential moving average."""
        d = self.dimension
        memory = np.zeros(d)
        decay = 0.5
        
        predictions = []
        
        for item in sequence:
            # Predict next? No mechanism in simple EMA.
            # EMA just tracks state.
            # To predict, we need a transition matrix or similar.
            # Let's measure *lag*. How close is memory to current item?
            
            memory = self._normalize(memory * (1-decay) + item * decay)
            sim = np.dot(memory, item)
            predictions.append(sim)
            
        return np.mean(predictions)

    def run_phase_tracking(self, sequence, seed):
        """Phase rotation tracking."""
        # Convert sequence to phase vectors
        # Assume items are complex unit vectors
        d = self.dimension
        
        # Map real vectors to phases
        # item -> exp(i * item * pi)
        seq_phase = [np.exp(1j * item * np.pi) for item in sequence]
        
        memory = np.zeros(d, dtype=np.complex128)
        decay = 0.5
        
        predictions = []
        
        for item in seq_phase:
            # Update
            memory = memory * (1-decay) + item * decay
            # Normalize to unit circle (Phase Reset)
            memory = memory / (np.abs(memory) + 1e-10)
            
            # Sim
            sim = np.abs(np.vdot(memory, item)) / d
            predictions.append(sim)
            
        return np.mean(predictions)

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{ 'Method':<10} {'Tracking Sim':<15}")
        print("-" * 30)
        
        methods = ["vector", "phase"]
        
        for method in methods:
            sims = []
            for t in range(self.num_trials):
                # Generate sequence
                seq = [self._generate(self.dimension) for _ in range(self.sequence_length)]
                
                if method == "vector":
                    res = self.run_vector_tracking(seq, t*100)
                else:
                    res = self.run_phase_tracking(seq, t*100)
                    
                sims.append(res)
                
            avg_sim = np.mean(sims)
            results["conditions"].append({
                "method": method,
                "avg_tracking_sim": float(avg_sim)
            })
            
            print(f"{method:<10} {avg_sim:<15.3f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        vector = [c for c in conds if c["method"] == "vector"][0]
        phase = [c for c in conds if c["method"] == "phase"][0]
        
        diff = phase["avg_tracking_sim"] - vector["avg_tracking_sim"]
        
        findings = []
        findings.append(f"Phase vs Vector Tracking Diff: {diff:+.3f}")
        
        if diff > 0.05:
            status = "PHASE_SUPERIOR"
            findings.append("Phase tracking maintains higher fidelity to current state.")
        else:
            status = "EQUIVALENT"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2122: Temporal Dynamics")
    print("Hypothesis: Phase tracks dynamic inputs better.")
    print("="*60)
    
    exp = TemporalDynamics()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2122_temporal_dynamics.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()