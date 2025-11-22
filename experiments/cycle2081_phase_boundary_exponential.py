"""
Cycle 2081: Phase Boundary Exponential
=======================================
Is there a "Phase Boundary" where the scaling law breaks?

From C2080: D scales exponentially with Depth.
Hypothesis: At some extreme dimension D, the noise floor might drop
non-linearly (phase transition), allowing deeper recursion than predicted.

Design:
- Test Depth 4 at D=[16384, 32768, 65536].
- If success at D < 185,000 (predicted for Depth 7), it implies a phase transition.
- Check if the exponent alpha decreases at high D.
"""

import numpy as np
import json
from datetime import datetime

class PhaseBoundaryExponential:
    def __init__(self):
        self.target_depth = 4
        self.dimensions = [16384, 32768, 65536] 
        self.num_trials = 3 # Expensive computation, fewer trials

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def check_depth(self, d, depth, seed):
        np.random.seed(seed)
        
        # Atoms
        atoms = [self._generate(d) for _ in range(depth + 1)]
        
        # Target
        target = atoms[0]
        for i in range(1, depth + 1):
            target = self._normalize(self._circ_conv(target, atoms[i]))
            
        # Store (No Cleanup)
        memory = np.zeros(d)
        keys = []
        for atom in atoms:
            k = self._generate(d)
            memory += self._circ_conv(k, atom)
            keys.append(k)
        memory = self._normalize(memory)
        
        # Retrieve & Compose
        current = None
        for i, k in enumerate(keys):
            k_inv = np.roll(k[::-1], 1)
            retrieved = self._circ_conv(memory, k_inv)
            
            if current is None:
                current = retrieved
            else:
                current = self._normalize(self._circ_conv(current, retrieved))
                
        sim = np.dot(current, target)
        return sim, sim > 0.1

    def run_experiment(self):
        results = {"points": []}
        
        print(f"{'Dimension':<10} {'Sim':<10} {'Success':<10}")
        print("-" * 30)
        
        for d in self.dimensions:
            sims = []
            successes = 0
            
            for t in range(self.num_trials):
                sim, success = self.check_depth(d, self.target_depth, t*100 + d)
                sims.append(sim)
                if success: successes += 1
            
            avg_sim = np.mean(sims)
            success_rate = successes / self.num_trials
            
            results["points"].append({
                "dimension": d,
                "avg_similarity": float(avg_sim),
                "success_rate": float(success_rate)
            })
            
            print(f"{d:<10} {avg_sim:<10.3f} {success_rate*100:<10.0f}%")
            
        return results

    def analyze(self, results):
        points = results["points"]
        
        # Check if any D succeeded
        success = any(p["success_rate"] > 0.5 for p in points)
        
        findings = []
        if success:
            min_d = min([p["dimension"] for p in points if p["success_rate"] > 0.5])
            findings.append(f"Depth 4 achieved at D={min_d}")
            status = "TRANSITION_POSSIBLE"
        else:
            findings.append("Depth 4 failed even at D=65536")
            status = "EXPONENTIAL_CONFIRMED"
            
        # Check similarity scaling
        sims = [p["avg_similarity"] for p in points]
        if sims[-1] > sims[0]:
            findings.append("Similarity improves with D (Signal exists)")
        else:
            findings.append("Similarity stagnant (Noise dominant)")
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2081: Phase Boundary Exponential")
    print("Hypothesis: High-D suppression of noise floor.")
    print("="*60)
    
    exp = PhaseBoundaryExponential()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2081_phase_boundary.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
