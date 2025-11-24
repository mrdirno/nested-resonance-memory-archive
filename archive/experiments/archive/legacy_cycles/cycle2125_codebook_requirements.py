"""
Cycle 2125: Codebook Requirements
==================================
How many atomic symbols do we need to represent a complex concept?

Hypothesis: There is a minimum "Codebook Density" required for semantic robustness.
If we use too few atoms, concepts alias (overlap). If we use too many, cleanup becomes expensive.

Design:
- Define a "Concept" as a random composition of K atoms.
- Generate N unique concepts.
- Test retrieval of Concepts from Memory.
- Vary Codebook Size (number of atoms available).
"""

import numpy as np
import json
from datetime import datetime

class CodebookRequirements:
    def __init__(self):
        self.dimension = 1024
        self.num_concepts = 50
        self.num_trials = 5
        self.codebook_sizes = [10, 50, 100, 500, 1000]
        self.concept_complexity = 3 # Depth 3 (A+B+C)

    def _normalize(self, v):
        return v / (np.abs(v) + 1e-10)

    def _generate(self, d):
        phases = np.random.uniform(0, 2 * np.pi, d)
        return np.exp(1j * phases)

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def run_trial(self, codebook_size, seed):
        np.random.seed(seed)
        d = self.dimension
        
        # Generate Atoms (Codebook)
        codebook = [self._generate(d) for _ in range(codebook_size)]
        
        # Generate Concepts
        # Concept = Binding of K random atoms from codebook
        concepts = []
        concept_keys = []
        
        for _ in range(self.num_concepts):
            # Pick K atoms
            indices = np.random.choice(codebook_size, self.concept_complexity, replace=False)
            atoms = [codebook[i] for i in indices]
            
            # Bind them
            vec = atoms[0]
            for i in range(1, self.concept_complexity):
                # Phase binding: element-wise multiply
                vec = vec * atoms[i] 
            
            concepts.append(vec)
            concept_keys.append(self._generate(d))
            
        # Store
        memory = np.zeros(d, dtype=np.complex128)
        for k, c in zip(concept_keys, concepts):
            memory += k * c
            
        # Retrieve
        correct = 0
        for k, target in zip(concept_keys, concepts):
            retrieved = memory * np.conjugate(k)
            
            # Check against distractors (other concepts)
            # We need to ensure concepts are distinct
            
            sim = np.abs(np.vdot(retrieved, target))
            
            # Distractor check
            distractor_idx = np.random.randint(self.num_concepts)
            while concepts[distractor_idx] is target:
                distractor_idx = np.random.randint(self.num_concepts)
            
            sim_dist = np.abs(np.vdot(retrieved, concepts[distractor_idx]))
            
            if sim > sim_dist:
                correct += 1
                
        return correct / self.num_concepts

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Codebook':<10} {'Accuracy':<10}")
        print("-" * 25)
        
        for size in self.codebook_sizes:
            accs = []
            for t in range(self.num_trials):
                acc = self.run_trial(size, t*100 + size)
                accs.append(acc)
                
            avg_acc = np.mean(accs)
            
            results["conditions"].append({
                "codebook_size": size,
                "accuracy": float(avg_acc)
            })
            
            print(f"{size:<10} {avg_acc:<10.3f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        
        # Find saturation point
        best_acc = max([c["accuracy"] for c in conds])
        optimal_size = 0
        
        for c in conds:
            if c["accuracy"] >= best_acc - 0.01:
                optimal_size = c["codebook_size"]
                break
                
        findings = []
        findings.append(f"Optimal Codebook Size: {optimal_size}")
        
        # Check if small codebooks fail (Aliasing)
        small_acc = conds[0]["accuracy"]
        if small_acc < 0.9:
            findings.append(f"Aliasing detected at Size {conds[0]['codebook_size']} (Acc {small_acc:.2f})")
        else:
            findings.append("No aliasing observed.")
            
        return {"status": "COMPLETE", "findings": findings}

def main():
    print("=" * 60)
    print("Cycle 2125: Codebook Requirements")
    print("Hypothesis: Small codebooks cause concept aliasing.")
    print("=" * 60)
    
    exp = CodebookRequirements()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2125_codebook_requirements.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
