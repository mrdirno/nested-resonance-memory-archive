"""
Cycle 2077: Curriculum Learning Pilot
======================================
Can the Meta-Controller learn if we start easy?

From C2075: Meta-Controller stagnated at Depth 3.
Hypothesis: Starting at Depth 1, then 2, then 3 (Curriculum) will allow
the gradient to flow, avoiding local minima.

Design:
- Stage 1: Depth 1 (Simple Binding)
- Stage 2: Depth 2 (Composition)
- Stage 3: Depth 3 (Hierarchy)
- Transfer parameters between stages.
"""

import numpy as np
import json
from datetime import datetime

class CurriculumLearningPilot:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 200
        self.iterations_per_stage = 15
        
        # Initial Params [rate, pool, clean]
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

    def evaluate(self, params, depth, seed):
        refresh_rate, pool_thresh, cleanup_prob = params
        np.random.seed(seed)
        d = self.dimension
        
        # Setup Task based on Depth
        atoms = [self._generate(d) for _ in range(depth + 1)]
        codebook = atoms.copy()
        
        # Target Construction
        target = atoms[0]
        for i in range(1, depth + 1):
            target = self._normalize(self._circ_conv(target, atoms[i]))
            
        # Store atoms
        memory = np.zeros(d)
        keys = []
        for atom in atoms:
            k = self._generate(d)
            memory += self._circ_conv(k, atom)
            keys.append(k)
        memory = self._normalize(memory)
        
        current_memory = memory.copy()
        energy = 100.0
        
        for cycle in range(self.num_cycles):
            current_memory = self._normalize(current_memory + np.random.normal(0, 0.01, d))
            
            if np.random.random() < refresh_rate:
                idx = cycle % len(keys)
                current_memory = self._normalize(current_memory + 0.5 * self._circ_conv(keys[idx], atoms[idx]))
                energy -= 0.5
                
            if energy < pool_thresh * 100:
                energy += 5.0
                energy -= 1.0
                
            if energy <= 0:
                return -1.0, 0.0 # Dead
                
        # Retrieval
        current = None
        for i, k in enumerate(keys):
            k_inv = np.roll(k[::-1], 1)
            retrieved = self._circ_conv(current_memory, k_inv)
            
            if np.random.random() < cleanup_prob:
                retrieved = self._cleanup(retrieved, codebook)
                energy -= 0.2
                
            if current is None:
                current = retrieved
            else:
                current = self._normalize(self._circ_conv(current, retrieved))
                
        sim = np.dot(current, target)
        accuracy = 1.0 if sim > 0.1 else 0.0
        
        total_cost = (refresh_rate * 0.5) + (cleanup_prob * 0.2)
        score = accuracy - total_cost
        
        return score, accuracy

    def run_stage(self, depth, initial_params):
        current_params = initial_params.copy()
        best_score, best_acc = self.evaluate(current_params, depth, 0)
        
        history = []
        
        for i in range(self.iterations_per_stage):
            perturb = np.random.normal(0, 0.1, 3)
            new_params = current_params + perturb
            for j in range(3):
                new_params[j] = np.clip(new_params[j], self.bounds[j][0], self.bounds[j][1])
                
            new_score, new_acc = self.evaluate(new_params, depth, i + depth*100)
            
            if new_score > best_score:
                current_params = new_params
                best_score = new_score
                best_acc = new_acc
                
            history.append({
                "depth": depth,
                "iter": i,
                "params": current_params.tolist(),
                "score": float(best_score),
                "accuracy": float(best_acc)
            })
            
        return current_params, best_score, best_acc, history

    def run_experiment(self):
        results = {"stages": []}
        
        params = self.params.copy()
        
        print(f"{'Stage':<8} {'Depth':<8} {'Rate':<8} {'Pool':<8} {'Clean':<8} {'Score':<8}")
        print("------------------------------------------------------------")
        
        for stage, depth in enumerate([1, 2, 3]):
            params, score, acc, history = self.run_stage(depth, params)
            
            results["stages"].append({
                "stage": stage,
                "depth": depth,
                "final_params": params.tolist(),
                "final_score": score,
                "final_accuracy": acc,
                "history": history
            })
            
            print(f"{stage:<8} {depth:<8} {params[0]:<8.2f} {params[1]:<8.2f} {params[2]:<8.2f} {score:<8.2f}")
            
        return results

    def analyze(self, results):
        stages = results["stages"]
        final_stage = stages[-1]
        
        findings = []
        findings.append(f"Final Depth 3 Score: {final_stage['final_score']:.2f}")
        findings.append(f"Final Depth 3 Accuracy: {final_stage['final_accuracy']:.2f}")
        
        # Check if parameters evolved
        initial_rate = 0.1
        final_rate = final_stage['final_params'][0]
        
        findings.append(f"Rate Evolution: {initial_rate:.2f} -> {final_rate:.2f}")
        
        if final_stage['final_score'] > 0:
            status = "SUCCESS"
        else:
            status = "FAILURE"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2077: Curriculum Learning Pilot")
    print("Hypothesis: Curriculum enables convergence on difficult tasks.")
    print("="*60)
    
    exp = CurriculumLearningPilot()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2077_curriculum.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
