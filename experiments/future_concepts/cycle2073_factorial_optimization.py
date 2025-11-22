"""
Cycle 2073: Factorial Optimization
===================================
Find the optimal combination of Swarm mechanisms.

Factors:
1. Stereopsis (1 vs 4 views)
2. Cleanup (On vs Off)
3. Pooling (On vs Off)

Task:
- Hierarchical retrieval at Depth 3 under moderate noise (0.1).
- Metric: Performance Score = (Accuracy * 100) + (Survival * 0.5)

Hypothesis:
Synergy! The combination of all three (Full Swarm) will outperform
any single mechanism or pairwise combination.
"""

import numpy as np
import json
from datetime import datetime

class FactorialOptimization:
    def __init__(self):
        self.total_bits = 1024
        self.noise_level = 0.1
        self.depth = 3
        self.num_trials = 10
        self.max_cycles = 100

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

    def run_trial(self, stereo, cleanup, pooling, seed):
        """Run a single trial with the given configuration."""
        np.random.seed(seed)
        
        # Configuration
        num_views = 4 if stereo else 1
        dim_per_view = self.total_bits // num_views
        
        # Setup Agents
        agents = []
        for _ in range(num_views):
            agents.append({
                "energy": 100.0,
                "alive": True,
                "memory": np.zeros(dim_per_view),
                "keys": [],
                "atoms": [], # Codebook for cleanup
                "target": None
            })
            
        # Task: Construct Depth 3 hierarchy
        # ((A+B)+C)+D
        
        for agent in agents:
            d = dim_per_view
            atoms = [self._generate(d) for _ in range(self.depth + 1)]
            agent["atoms"] = atoms.copy()
            
            # Build target
            target = atoms[0]
            for i in range(1, self.depth + 1):
                target = self._normalize(self._circ_conv(target, atoms[i]))
            agent["target"] = target
            
            # Store
            for atom in atoms:
                k = self._generate(d)
                agent["memory"] += self._circ_conv(k, atom)
                agent["keys"].append(k)
            agent["memory"] = self._normalize(agent["memory"])
            
            # Add Noise
            agent["memory"] = self._normalize(agent["memory"] + np.random.normal(0, self.noise_level, d))

        # Simulation Loop (Survival)
        drain_rates = np.ones(num_views)
        if num_views > 1:
            drain_rates[0] = 4.0 # Stress one agent
            
        survival_cycles = 0
        
        for cycle in range(self.max_cycles):
            # Energy Dynamics
            alive_indices = [i for i, a in enumerate(agents) if a["alive"]]
            if not alive_indices: break
            
            for i in alive_indices:
                agents[i]["energy"] -= drain_rates[i]
                
            if pooling:
                total = sum(agents[i]["energy"] for i in alive_indices)
                avg = total / len(alive_indices)
                for i in alive_indices:
                    agents[i]["energy"] = avg
                    
            # Check Death
            for i in alive_indices:
                if agents[i]["energy"] <= 0:
                    agents[i]["alive"] = False
            
            if any(a["alive"] for a in agents):
                survival_cycles += 1
            else:
                break
                
        # Retrieval Task (Accuracy)
        # Only alive agents vote
        votes = 0
        alive_count = 0
        
        for agent in agents:
            if not agent["alive"]: continue
            alive_count += 1
            
            keys = agent["keys"]
            mem = agent["memory"]
            codebook = agent["atoms"]
            
            current = None
            for i, k in enumerate(keys):
                k_inv = np.roll(k[::-1], 1)
                retrieved = self._circ_conv(mem, k_inv)
                
                if cleanup:
                    retrieved = self._cleanup(retrieved, codebook)
                    
                if current is None:
                    current = retrieved
                else:
                    current = self._normalize(self._circ_conv(current, retrieved))
            
            sim = np.dot(current, agent["target"])
            if sim > 0.1:
                votes += 1
                
        accuracy = 0.0
        if alive_count > 0:
            # Majority vote
            if votes > (alive_count / 2):
                accuracy = 1.0
        
        return {
            "accuracy": accuracy,
            "survival": survival_cycles
        }

    def run_experiment(self):
        factors = [
            (False, False, False), # Baseline
            (True, False, False),  # Stereo only
            (False, True, False),  # Cleanup only
            (False, False, True),  # Pooling only
            (True, True, False),   # Stereo + Cleanup
            (True, False, True),   # Stereo + Pooling
            (False, True, True),   # Cleanup + Pooling
            (True, True, True)     # Full Swarm
        ]
        
        results = {"conditions": []}
        
        print(f"{ 'Stereo':<8} { 'Clean':<8} { 'Pool':<8} { 'Acc':<8} { 'Surv':<8} { 'Score':<8}")
        print("""--------------------""")
        
        for stereo, clean, pool in factors:
            accuracies = []
            survivals = []
            
            for t in range(self.num_trials):
                res = self.run_trial(stereo, clean, pool, t*100)
                accuracies.append(res["accuracy"])
                survivals.append(res["survival"])
                
            avg_acc = np.mean(accuracies)
            avg_surv = np.mean(survivals)
            score = (avg_acc * 100) + (avg_surv * 0.5)
            
            results["conditions"].append({
                "stereo": stereo,
                "cleanup": clean,
                "pooling": pool,
                "accuracy": avg_acc,
                "survival": avg_surv,
                "score": score
            })
            
            print(f"{str(stereo):<8} {str(clean):<8} {str(pool):<8} {avg_acc:<8.2f} {avg_surv:<8.1f} {score:<8.1f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        
        # Find best
        best = max(conds, key=lambda x: x["score"])
        baseline = conds[0]
        
        improvement = best["score"] - baseline["score"]
        
        findings = []
        findings.append(f"Best Configuration: Stereo={best['stereo']}, Clean={best['cleanup']}, Pool={best['pooling']}")
        findings.append(f"Score: {best['score']:.1f} (Baseline: {baseline['score']:.1f})")
        findings.append(f"Improvement: +{improvement:.1f} points")
        
        if best["stereo"] and best["cleanup"] and best["pooling"]:
            status = "SYNERGY_CONFIRMED"
        else:
            status = "PARTIAL_OPTIMAL"
            
        return {"status": status, "findings": findings}

def main():
    print("""====================""")
    print("Cycle 2073: Factorial Optimization")
    print("Hypothesis: Full Swarm (Stereo+Clean+Pool) is optimal.")
    print("""====================""")
    
    exp = FactorialOptimization()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2073_factorial.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
