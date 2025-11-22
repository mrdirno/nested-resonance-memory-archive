"""
Cycle 2121: Compression Comparison
===================================
Can we store "Heavy" items using Phase Resonance?

From C2120: Capacity is ~100 slots.
Hypothesis: Phase vectors can compress high-dimensional data better than
amplitude vectors.

Design:
- Source: 4096-dim real vector.
- Target: 1024-dim compressed vector.
- Method A: Linear Projection (Random Matrix).
- Method B: Phase Projection (Angle Encoding).
- Task: Reconstruct original vector (cosine similarity).
"""

import numpy as np
import json
from datetime import datetime

class CompressionComparison:
    def __init__(self):
        self.input_dim = 4096
        self.compressed_dim = 1024
        self.num_trials = 10

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _generate_source(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.input_dim), self.input_dim)
        return self._normalize(v)

    def run_linear_projection(self, source, seed):
        """Standard random projection (Johnson-Lindenstrauss)."""
        np.random.seed(seed)
        
        # Projector
        matrix = np.random.normal(0, 1.0/np.sqrt(self.compressed_dim), (self.compressed_dim, self.input_dim))
        
        # Compress
        compressed = np.dot(matrix, source)
        
        # Reconstruct (pseudo-inverse is just transpose for JL)
        reconstructed = np.dot(matrix.T, compressed)
        
        return self._normalize(reconstructed)

    def run_phase_projection(self, source, seed):
        """Phase encoding: Map vector values to angles."""
        np.random.seed(seed)
        
        # Projector (to 1024 complex numbers)
        # We map 4096 reals -> 1024 complex phases?
        # No, let's keep bit-count fair. 
        # 1024 complex = 2048 floats. 
        # Let's stick to dimension count for fairness.
        
        # Simple Phase Encoder:
        # 1. Linear Project to 1024 dim
        matrix = np.random.normal(0, 1.0/np.sqrt(self.compressed_dim), (self.compressed_dim, self.input_dim))
        projected = np.dot(matrix, source)
        
        # 2. Phase Quantization (The "Phase" part)
        # Take only the phase (sign) of the projection? Or true phase?
        # Let's treat projected as amplitudes and convert to phase.
        # V_phase = exp(i * V_proj * scale)
        
        scale = np.pi # Map -1..1 to -pi..pi
        phases = np.exp(1j * projected * scale)
        
        # 3. Reconstruct
        # Unwind phase: V_rec = angle(V_phase) / scale
        reconstructed_proj = np.angle(phases) / scale
        
        # Back-project
        reconstructed = np.dot(matrix.T, reconstructed_proj)
        
        return self._normalize(reconstructed)

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Method':<10} {'Similarity':<10}")
        print("-" * 25)
        
        methods = ["linear", "phase"]
        
        for method in methods:
            sims = []
            for t in range(self.num_trials):
                source = self._generate_source()
                
                if method == "linear":
                    recon = self.run_linear_projection(source, t*100)
                else:
                    recon = self.run_phase_projection(source, t*100)
                    
                sim = np.dot(source, recon)
                sims.append(sim)
                
            avg_sim = np.mean(sims)
            
            results["conditions"].append({
                "method": method,
                "similarity": float(avg_sim)
            })
            
            print(f"{method:<10} {avg_sim:<10.3f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        linear = [c for c in conds if c["method"] == "linear"][0]
        phase = [c for c in conds if c["method"] == "phase"][0]
        
        diff = phase["similarity"] - linear["similarity"]
        
        findings = []
        findings.append(f"Phase vs Linear Diff: {diff:+.3f}")
        
        if diff > 0.05:
            status = "PHASE_BETTER"
            findings.append("Phase encoding preserves more structure.")
        elif diff < -0.05:
            status = "LINEAR_BETTER"
            findings.append("Linear projection preserves more structure (amplitude matters).")
        else:
            status = "EQUIVALENT"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2121: Compression Comparison")
    print("Hypothesis: Phase allows non-linear compression.")
    print("="*60)
    
    exp = CompressionComparison()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2121_compression_comparison.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
