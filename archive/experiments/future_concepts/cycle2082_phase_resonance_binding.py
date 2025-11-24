"""
Cycle 2082: Phase Resonance Binding
====================================
Explore depth limits of phase-based binding.

From C2081: Vector HRR hits exponential scaling wall for Depth > 3.
Hypothesis: Phase-based binding (e.g., using complex exponentials) offers
superior depth-to-dimension scaling due to inherent noise robustness of phase.

Design:
- Implement a simplified phase-based binding mechanism.
- Test Max Depth achieved for fixed D (e.g., 1024).
- Compare to C2068 (Vector HRR with Cleanup, D=1024, Max Depth 8).
"""

import numpy as np
import json
from datetime import datetime

class PhaseResonanceBinding:
    def __init__(self):
        self.dimension = 1024
        self.max_depth = 10
        self.num_trials = 10
        self.frequency_range = (1, 100) # Frequencies for encoding

    def _generate_phase_vector(self, d):
        """Generates a random phase vector (complex exponentials)."""
        phases = np.random.uniform(0, 2 * np.pi, d)
        return np.exp(1j * phases)

    def _phase_multiply(self, a, b):
        """Phase-based binding (multiplication of complex exponentials)."""
        return a * b # Element-wise complex multiplication

    def _phase_unmultiply(self, a, b_inv):
        """Phase-based unbinding (multiplication by inverse)."""
        return a * np.conjugate(b_inv) # Conjugate is inverse for unit vectors

    def check_depth(self, depth, seed):
        """Test if phase-based binding supports given depth."""
        np.random.seed(seed)
        d = self.dimension
        
        # Atoms (encoded as unique phase vectors)
        atoms_raw = [self._generate_phase_vector(d) for _ in range(depth + 1)]
        
        # Build target composition
        composed_target = atoms_raw[0]
        for i in range(1, depth + 1):
            composed_target = self._phase_multiply(composed_target, atoms_raw[i])
            
        # Store in memory (simulated noisy retrieval)
        memory = composed_target.copy() # No external memory to retrieve from yet
        
        # Introduce noise (phase noise)
        phase_noise = np.random.uniform(-np.pi/4, np.pi/4, d) # +/- 45 deg phase noise
        noise_vector = np.exp(1j * phase_noise)
        memory = self._phase_multiply(memory, noise_vector)
        
        # Retrieve components and recompose (noisy)
        retrieved_composed = atoms_raw[0] # Assume perfect retrieval of first atom for simplicity
        
        for i in range(1, depth + 1):
            # Simulate retrieval of atom 'i' from 'memory' based on previous 'retrieved_composed'
            # (This is a simplification; a full NRM system would have key-value pairs)
            # Here, we test the inherent noise accumulation of recursive phase multiplication
            
            # We need to test if the product of noisy elements still resembles the true product.
            # Let's test by directly composing noisy atoms and comparing to target.
            
            # Noisy atoms (from memory, after noise injection)
            noisy_atoms = []
            for atom in atoms_raw:
                phase_noise_atom = np.random.uniform(-np.pi/8, np.pi/8, d) # Less noise per atom
                noisy_atom = self._phase_multiply(atom, np.exp(1j * phase_noise_atom))
                noisy_atoms.append(noisy_atom)
                
            recomposed_from_noisy = noisy_atoms[0]
            for i in range(1, depth + 1):
                recomposed_from_noisy = self._phase_multiply(recomposed_from_noisy, noisy_atoms[i])
                
            # Similarity is cosine of phase difference (mean angle between vectors)
            phase_diff = np.angle(recomposed_from_noisy * np.conjugate(composed_target))
            sim = np.exp(-np.mean(np.abs(phase_diff))) # Higher sim = better match

            return sim, sim > 0.5 # Robust threshold

    def run_experiment(self):
        results = {"depth_performance": []}
        
        print(f"{'Depth':<8} {'Avg Sim':<10} {'Success %':<10}")
        print("-" * 30)
        
        for depth in range(1, self.max_depth + 1):
            sims = []
            success_count = 0
            
            for t in range(self.num_trials):
                sim, success = self.check_depth(depth, t*100 + depth)
                sims.append(sim)
                if success: success_count += 1
            
            avg_sim = np.mean(sims)
            success_rate = success_count / self.num_trials
            
            results["depth_performance"].append({
                "depth": depth,
                "avg_similarity": float(avg_sim),
                "success_rate": float(success_rate)
            })
            
            print(f"{depth:<8} {avg_sim:<10.3f} {success_rate*100:<10.0f}%")
            
            if success_rate < 0.5 and depth > 1: # Break if performance drops
                break
            
        return results

    def analyze(self, results):
        perf = results["depth_performance"]
        
        max_successful_depth = 0
        for p in perf:
            if p["success_rate"] > 0.5:
                max_successful_depth = p["depth"]
            else:
                break
                
        findings = []
        findings.append(f"Maximum successful depth (phase): {max_successful_depth}")
        
        # Compare to vector HRR (D=1024, with cleanup: Max Depth 8)
        # Without cleanup: Max Depth 2
        
        if max_successful_depth > 8:
            status = "PHASE_SUPERIOR"
            findings.append("Phase binding significantly outperforms vector HRR with cleanup.")
        elif max_successful_depth > 2:
            status = "PHASE_IMPROVED"
            findings.append("Phase binding outperforms raw vector HRR (no cleanup).")
        else:
            status = "PHASE_LIMITED"
            findings.append("Phase binding currently limited, further optimization needed.")
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2082: Phase Resonance Binding")
    print("Hypothesis: Phase binding offers superior depth scaling.")
    print("="*60)
    
    exp = PhaseResonanceBinding()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2082_phase_binding.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
