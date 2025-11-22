"""
Cycle 2079: Metabolic Stress
=============================
From C2078: Stereopsis failed at Depth 2 due to energy cost.
Hypothesis: Reducing the metabolic cost of additional views (economies of scale)
will allow the Stereopsis advantage to manifest.

Design:
- Test Stereopsis Swarm at varying "Cost Multipliers" [1.0, 0.75, 0.5, 0.25].
- 1.0 = Full cost (4x energy for 4 views).
- 0.25 = Efficient Swarm (4 views cost same as 1 view).
- Metric: Depth reached.
"""

import numpy as np
import json
from datetime import datetime

class MetabolicStress:
    def __init__(self):
        self.total_bits = 1024
        self.num_views = 4
        self.dim_per_view = self.total_bits // self.num_views
        self.num_cycles = 200
        self.num_trials = 10
        
        # Cost multipliers to test
        self.cost_multipliers = [1.0, 0.75, 0.5, 0.25]

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

    def evaluate(self, cost_multiplier, depth, seed):
        refresh_rate = 0.1 # Fixed reasonable rate
        pool_thresh = 0.5
        cleanup_prob = 0.1
        
        np.random.seed(seed)
        
        # Run 4 Views
        votes = 0
        total_energy_cost = 0
        
        for view in range(self.num_views):
            d = self.dim_per_view
            
            atoms = [self._generate(d) for _ in range(depth + 1)]
            codebook = atoms.copy()
            
            target = atoms[0]
            for i in range(1, depth + 1):
                target = self._normalize(self._circ_conv(target, atoms[i]))
                
            memory = np.zeros(d)
            keys = []
            for atom in atoms:
                k = self._generate(d)
                memory += self._circ_conv(k, atom)
                keys.append(k)
            memory = self._normalize(memory)
            
            current_memory = memory.copy()
            energy = 100.0
            survival = True
            
            # Apply cost multiplier to all active energy costs
            base_refresh_cost = 0.5 * cost_multiplier
            base_cleanup_cost = 0.2 * cost_multiplier
            
            for cycle in range(self.num_cycles):
                current_memory = self._normalize(current_memory + np.random.normal(0, 0.01, d))
                
                if np.random.random() < refresh_rate:
                    idx = cycle % len(keys)
                    current_memory = self._normalize(current_memory + 0.5 * self._circ_conv(keys[idx], atoms[idx]))
                    energy -= base_refresh_cost
                    
                if energy < pool_thresh * 100:
                    energy += 5.0
                    energy -= 1.0 # Pooling overhead (fixed)
                    
                if energy <= 0:
                    survival = False
                    break
            
            if not survival:
                continue
                
            # Retrieval
            current = None
            for i, k in enumerate(keys):
                k_inv = np.roll(k[::-1], 1)
                retrieved = self._circ_conv(current_memory, k_inv)
                
                if np.random.random() < cleanup_prob:
                    retrieved = self._cleanup(retrieved, codebook)
                    energy -= base_cleanup_cost
                    
                if current is None:
                    current = retrieved
                else:
                    current = self._normalize(self._circ_conv(current, retrieved))
            
            sim = np.dot(current, target)
            if sim > 0.1:
                votes += 1
                
        accuracy = 1.0 if votes > (self.num_views / 2) else 0.0
        return accuracy

    def run_experiment(self):
        results = {"conditions": []}
        
        print(f"{'Cost Mult':<12} {'Depth':<8} {'Accuracy':<8}")
        print("-" * 40)
        
        for cost_mult in self.cost_multipliers:
            # Test increasing depth until failure
            for depth in [1, 2, 3, 4]:
                accuracies = []
                for t in range(self.num_trials):
                    acc = self.evaluate(cost_mult, depth, t*100 + int(cost_mult*1000))
                    accuracies.append(acc)
                
                avg_acc = np.mean(accuracies)
                
                results["conditions"].append({
                    "cost_multiplier": cost_mult,
                    "depth": depth,
                    "accuracy": float(avg_acc)
                })
                
                print(f"{cost_mult:<12.2f} {depth:<8} {avg_acc:<8.2f}")
                
                # If failed, stop increasing depth for this cost
                if avg_acc < 0.5:
                    break
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        
        # Find max depth for each cost
        max_depths = {}
        for c in conds:
            cm = c["cost_multiplier"]
            if c["accuracy"] >= 0.5:
                if cm not in max_depths or c["depth"] > max_depths[cm]:
                    max_depths[cm] = c["depth"]
            elif cm not in max_depths:
                max_depths[cm] = 0
                
        findings = []
        for cm in self.cost_multipliers:
            depth = max_depths.get(cm, 0)
            findings.append(f"Cost {cm:.2f}: Max Depth = {depth}")
            
        # Check if efficiency unlocks depth
        full_cost_depth = max_depths.get(1.0, 0)
        efficient_depth = max_depths.get(0.25, 0)
        
        if efficient_depth > full_cost_depth:
            status = "CONFIRMED"
            findings.append(f"Efficiency gain unlocked +{efficient_depth - full_cost_depth} depth.")
        else:
            status = "NEUTRAL"
            findings.append("Efficiency did not increase functional depth.")
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2079: Metabolic Stress")
    print("Hypothesis: Lower cost multipliers unlock deeper cognition.")
    print("="*60)
    
    exp = MetabolicStress()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2079_metabolic_stress.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()