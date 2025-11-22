"""
Cycle 2075: Meta-Controller Integration
========================================
Full autonomous control of Swarm parameters.

From C2074: Single-parameter tuning works.
Hypothesis: Multi-parameter tuning (Refresh Rate, Pooling Threshold, Cleanup Frequency)
can find the "Sweet Spot" for complex tasks.

Task: Hierarchical Retrieval (Depth 3)
Controller: Random Perturbation Hill Climbing (Simple Evolutionary Strategy)
"""

import numpy as np
import json
from datetime import datetime

class MetaControllerIntegration:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 200
        self.iterations = 20
        
        # Parameters to tune [rate, pooling_threshold, cleanup_prob]
        self.params = np.array([0.1, 0.5, 0.1]) 
        self.bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]

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

    def evaluate(self, params, seed):
        refresh_rate, pool_thresh, cleanup_prob = params
        np.random.seed(seed)
        d = self.dimension
        
        # Setup Task: Depth 3 Hierarchy
        # ((A+B)+C)
        atoms = [self._generate(d) for _ in range(3)]
        codebook = atoms.copy()
        
        # Target
        target = self._normalize(self._circ_conv(
            self._circ_conv(atoms[0], atoms[1]), atoms[2]
        ))
        
        # Store atoms
        memory = np.zeros(d)
        keys = []
        for atom in atoms:
            k = self._generate(d)
            memory += self._circ_conv(k, atom)
            keys.append(k)
        memory = self._normalize(memory)
        
        current_memory = memory.copy()
        
        # Simulation Loop
        energy = 100.0
        survival = True
        
        for cycle in range(self.num_cycles):
            # Noise
            current_memory = self._normalize(current_memory + np.random.normal(0, 0.01, d))
            
            # Refresh (Cost)
            if np.random.random() < refresh_rate:
                k = keys[cycle % 3]
                current_memory = self._normalize(current_memory + 0.5 * self._circ_conv(k, atoms[cycle % 3]))
                energy -= 0.5
                
            # Pooling (Cost if triggered)
            # Simulated: if energy drops below threshold, pay cost to "pool" (boost)
            if energy < pool_thresh * 100:
                energy += 5.0 # Boost
                energy -= 1.0 # Tax
                
            # Cleanup (Cost)
            # Simulated as implicit cost during retrieval operations later
            
            if energy <= 0:
                survival = False
                break
                
        if not survival:
            return -1.0, 0.0
            
        # Retrieval
        current = None
        cleanup_count = 0
        for i, k in enumerate(keys):
            k_inv = np.roll(k[::-1], 1)
            retrieved = self._circ_conv(current_memory, k_inv)
            
            if np.random.random() < cleanup_prob:
                retrieved = self._cleanup(retrieved, codebook)
                cleanup_count += 1
                energy -= 0.2 # Cleanup cost
                
            if current is None:
                current = retrieved
            else:
                current = self._normalize(self._circ_conv(current, retrieved))
                
        sim = np.dot(current, target)
        accuracy = 1.0 if sim > 0.1 else 0.0
        
        # Score = Accuracy - Total Cost
        # We want high accuracy with low params
        total_cost = (refresh_rate * 0.5) + (cleanup_prob * 0.2)
        score = accuracy - total_cost
        
        return score, accuracy

    def run_experiment(self):
        results = {"trajectory": []}
        
        # Initial
        score, acc = self.evaluate(self.params, 0)
        
        print(f"{ 'Iter':<6} { 'Rate':<6} { 'Pool':<6} { 'Clean':<6} { 'Acc':<6} { 'Score':<6}")
        print("-" * 50)
        print(f"{0:<6} {self.params[0]:<6.2f} {self.params[1]:<6.2f} {self.params[2]:<6.2f} {acc:<6.2f} {score:<6.2f}")
        
        results["trajectory"].append({
            "iteration": 0,
            "params": self.params.tolist(),
            "accuracy": acc,
            "score": score
        })
        
        for i in range(1, self.iterations):
            # Perturb
            perturbation = np.random.normal(0, 0.1, 3)
            new_params = self.params + perturbation
            
            # Clip to bounds
            for j in range(3):
                new_params[j] = np.clip(new_params[j], self.bounds[j][0], self.bounds[j][1])
                
            new_score, new_acc = self.evaluate(new_params, i)
            
            if new_score > score:
                self.params = new_params
                score = new_score
                acc = new_acc
                
            results["trajectory"].append({
                "iteration": i,
                "params": self.params.tolist(),
                "accuracy": float(acc),
                "score": float(score)
            })
            
            print(f"{i:<6} {self.params[0]:<6.2f} {self.params[1]:<6.2f} {self.params[2]:<6.2f} {acc:<6.2f} {score:<6.2f}")
            
        return results

    def analyze(self, results):
        traj = results["trajectory"]
        initial = traj[0]
        final = traj[-1]
        
        improvement = final["score"] - initial["score"]
        
        findings = []
        findings.append(f"Final Params: Rate={final['params'][0]:.2f}, Pool={final['params'][1]:.2f}, Clean={final['params'][2]:.2f}")
        findings.append(f"Score Improvement: {improvement:+.2f}")
        
        if improvement > 0:
            status = "ADAPTED"
        else:
            status = "STAGNANT"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2075: Meta-Controller Integration")
    print("Hypothesis: Multi-parameter auto-tuning finds optimal swarm state.")
    print("="*60)
    
    exp = MetaControllerIntegration()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2075_meta_controller.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()