"""
Cycle 2120: Shannon Bound Check
================================
Is the 0.1 item/dimension limit fundamental?

From C2119: Capacity is 100 items for D=1024.
Hypothesis: We can exceed this if we use "Sparse Phase Encoding".
Instead of full-circle random phases, what if we quantize them?

Design:
- Test Binary Phase (0, pi) - Equivalent to Real Vectors
- Test Quaternary Phase (0, pi/2, pi, 3pi/2)
- Test Continuous Phase (current baseline)
- Metric: Max items at 99% accuracy.
"""

import numpy as np
import json
from datetime import datetime

class ShannonBoundCheck:
    def __init__(self):
        self.dimension = 1024
        self.num_trials = 5
        self.capacities = [50, 100, 150, 200, 250, 300]

    def _generate_binary(self, d):
        # 0 or pi -> 1 or -1
        phases = np.random.choice([0, np.pi], d)
        return np.exp(1j * phases)

    def _generate_quaternary(self, d):
        # 0, pi/2, pi, 3pi/2
        phases = np.random.choice([0, np.pi/2, np.pi, 3*np.pi/2], d)
        return np.exp(1j * phases)

    def _generate_continuous(self, d):
        phases = np.random.uniform(0, 2 * np.pi, d)
        return np.exp(1j * phases)

    def run_trial(self, mode, n_items, seed):
        np.random.seed(seed)
        d = self.dimension
        
        generator = {
            "binary": self._generate_binary,
            "quaternary": self._generate_quaternary,
            "continuous": self._generate_continuous
        }[mode]
        
        items = [generator(d) for _ in range(n_items)]
        keys = [generator(d) for _ in range(n_items)]
        
        memory = np.zeros(d, dtype=np.complex128)
        for k, i in zip(keys, items):
            memory += k * i
            
        correct = 0
        for k, target in zip(keys, items):
            retrieved_raw = memory * np.conjugate(k)
            
            # Similarity
            sim = np.abs(np.vdot(retrieved_raw, target)) / np.linalg.norm(retrieved_raw) / np.linalg.norm(target)
            
            distractor = generator(d)
            sim_dist = np.abs(np.vdot(retrieved_raw, distractor)) / np.linalg.norm(retrieved_raw) / np.linalg.norm(distractor)
            
            if sim > sim_dist:
                correct += 1
                
        return correct / n_items

    def run_experiment(self):
        results = {"modes": []}
        
        for mode in ["binary", "quaternary", "continuous"]:
            print(f"\nTesting Mode: {mode}")
            print(f"{'Items':<10} {'Accuracy':<10}")
            print("-" * 25)
            
            mode_results = []
            for n in self.capacities:
                accs = []
                for t in range(self.num_trials):
                    acc = self.run_trial(mode, n, t*100 + n)
                    accs.append(acc)
                
                avg_acc = np.mean(accs)
                mode_results.append({"n": n, "acc": avg_acc})
                print(f"{n:<10} {avg_acc:<10.3f}")
                
            results["modes"].append({"name": mode, "data": mode_results})
            
        return results

    def analyze(self, results):
        findings = []
        
        limits = {}
        for mode_data in results["modes"]:
            limit = 0
            for dp in mode_data["data"]:
                if dp["acc"] >= 0.99:
                    limit = dp["n"]
                else:
                    break
            limits[mode_data["name"]] = limit
            
        findings.append(f"Binary Limit: {limits['binary']}")
        findings.append(f"Quaternary Limit: {limits['quaternary']}")
        findings.append(f"Continuous Limit: {limits['continuous']}")
        
        if limits['continuous'] > limits['binary']:
            status = "CONTINUOUS_SUPERIOR"
        else:
            status = "QUANTIZED_SUPERIOR"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2120: Shannon Bound Check")
    print("Hypothesis: Continuous phase holds more info than quantized.")
    print("="*60)
    
    exp = ShannonBoundCheck()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2120_shannon_bound.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
