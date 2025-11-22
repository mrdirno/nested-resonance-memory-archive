"""
Cycle 2071: Fractal Stereopsis Integration
===========================================
Can a swarm of low-D agents outperform a single high-D agent?

Synthesis of C2058-C2070 findings:
- Stereopsis (Multi-View) > Monolithic (C2070)
- Cleanup enables composition (C2066)
- Round-Robin stabilizes load (C2060)

Design:
- Task: Complex Hierarchical Retrieval (Depth 3) under noise.
- System A (Monolith): Single 1024-dim vector with Cleanup + Round-Robin.
- System B (Swarm): Four 256-dim vectors with Cleanup + Round-Robin + Voting.
- Constraint: Equal total bits (1024).

Hypothesis:
System B will maintain higher accuracy at Depth 3 because diversity of 
perspective cancels out view-specific structural noise.
"""

import numpy as np
import json
from datetime import datetime

class FractalStereopsis:
    def __init__(self):
        self.total_bits = 1024
        self.num_views = 4
        self.dim_per_view = self.total_bits // self.num_views
        self.num_trials = 20
        self.depth = 3
        self.noise_levels = [0.01, 0.05, 0.1, 0.2]

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def _cleanup(self, noisy, codebook):
        best_match = None
        best_sim = -1
        for clean in codebook:
            sim = np.dot(noisy, clean)
            if sim > best_sim:
                best_sim = sim
                best_match = clean
        return best_match if best_match is not None else noisy

    def run_monolith(self, noise_level, seed):
        """Run single high-D agent."""
        np.random.seed(seed)
        d = self.total_bits
        
        # Create atoms
        atoms = [self._generate(d) for _ in range(self.depth + 1)]
        codebook = atoms.copy()
        
        # Build target: ((A+B)+C)+D ...
        target = atoms[0]
        for i in range(1, self.depth + 1):
            target = self._normalize(self._circ_conv(target, atoms[i]))
            
        # Store atoms
        memory = np.zeros(d)
        keys = []
        for atom in atoms:
            k = self._generate(d)
            memory += self._circ_conv(k, atom)
            keys.append(k)
        memory = self._normalize(memory)
        
        # Inject Noise
        memory = self._normalize(memory + np.random.normal(0, noise_level, d))
        
        # Retrieve & Compose
        current = None
        for i, k in enumerate(keys):
            k_inv = np.roll(k[::-1], 1)
            retrieved = self._circ_conv(memory, k_inv)
            # Cleanup
            retrieved = self._cleanup(retrieved, codebook)
            
            if current is None:
                current = retrieved
            else:
                current = self._normalize(self._circ_conv(current, retrieved))
                
        sim = np.dot(current, target)
        return sim > 0.1

    def run_swarm(self, noise_level, seed):
        """Run swarm of low-D agents with voting."""
        np.random.seed(seed)
        
        votes = 0
        
        for view in range(self.num_views):
            d = self.dim_per_view
            
            # Each view generates its own representation of atoms
            # "Shared Reality" means there is a correspondence, but vectors are unique.
            # We simulate this by running the Monolith logic at smaller d.
            
            atoms = [self._generate(d) for _ in range(self.depth + 1)]
            codebook = atoms.copy()
            
            target = atoms[0]
            for i in range(1, self.depth + 1):
                target = self._normalize(self._circ_conv(target, atoms[i]))
                
            memory = np.zeros(d)
            keys = []
            for atom in atoms:
                k = self._generate(d)
                memory += self._circ_conv(k, atom)
                keys.append(k)
            memory = self._normalize(memory)
            
            # Inject Noise (Independent per view)
            memory = self._normalize(memory + np.random.normal(0, noise_level, d))
            
            # Retrieve & Compose
            current = None
            for i, k in enumerate(keys):
                k_inv = np.roll(k[::-1], 1)
                retrieved = self._circ_conv(memory, k_inv)
                retrieved = self._cleanup(retrieved, codebook)
                
                if current is None:
                    current = retrieved
                else:
                    current = self._normalize(self._circ_conv(current, retrieved))
            
            sim = np.dot(current, target)
            if sim > 0.1:
                votes += 1
                
        # Consensus: Majority Vote
        return votes > (self.num_views / 2)

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Noise':<8} {'Monolith':<10} {'Swarm':<10} {'Diff':<10}")
        print("""-----------------------------------""")
        
        for noise in self.noise_levels:
            mono_score = 0
            swarm_score = 0
            
            for t in range(self.num_trials):
                seed = t * 100 + int(noise * 1000)
                if self.run_monolith(noise, seed): mono_score += 1
                if self.run_swarm(noise, seed): swarm_score += 1
                
            avg_mono = mono_score / self.num_trials
            avg_swarm = swarm_score / self.num_trials
            diff = avg_swarm - avg_mono
            
            results["conditions"].append({
                "noise": noise,
                "monolith": avg_mono,
                "swarm": avg_swarm,
                "diff": diff
            })
            
            print(f"{noise:<8.2f} {avg_mono:<10.2f} {avg_swarm:<10.2f} {diff:+.2f}")
            
        return results

    def analyze(self, results):
        findings = []
        diffs = [c["diff"] for c in results["conditions"]]
        avg_diff = np.mean(diffs)
        
        if avg_diff > 0.05:
            status = "CONFIRMED"
            findings.append(f"Swarm outperforms Monolith by {avg_diff*100:.1f}% on average.")
        elif avg_diff < -0.05:
            status = "FALSIFIED"
            findings.append(f"Monolith outperforms Swarm by {abs(avg_diff)*100:.1f}%")
        else:
            status = "NEUTRAL"
            findings.append("No significant difference.")
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2071: Fractal Stereopsis Integration")
    print("Hypothesis: 4x256 Swarm > 1x1024 Monolith at Depth 3")
    print("="*60)
    
    exp = FractalStereopsis()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2071_fractal_stereopsis.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
