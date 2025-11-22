"""
Cycle 2076: Universality Test (Energy Scale)
=============================================
Does the optimal refresh rate scale with available energy?

From C2074: Optimal rate was 0.124 for Energy=100.
Hypothesis: If we double Energy (200), optimal rate should double?
Or is it a structural property of the memory?

Design:
- Test Optimal Refresh Rate at Energy [50, 100, 200, 400].
- Check if Rate_opt * Energy = Constant (Energy Budget)
- Or if Rate_opt = Constant (Structural Requirement)
"""

import numpy as np
import json
from datetime import datetime

class UniversalityTestEnergy:
    def __init__(self):
        self.dimension = 1024
        self.num_cycles = 200
        self.num_trials = 5
        self.iterations = 10

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def optimize_rate(self, initial_energy, seed):
        """Find optimal rate for a given energy budget."""
        np.random.seed(seed)
        d = self.dimension
        
        n_items = 20
        memory = np.zeros(d)
        keys = []
        values = []
        for _ in range(n_items):
            k = self._generate(d)
            v = self._generate(d)
            memory += self._circ_conv(k, v)
            keys.append(k)
            values.append(v)
        memory = self._normalize(memory)
        
        phi = (1 + np.sqrt(5)) / 2
        comp_prob = 0.1 * phi
        
        def run_sim(rate):
            current_memory = memory.copy()
            refresh_idx = 0
            energy = initial_energy
            
            for cycle in range(self.num_cycles):
                # Noise
                current_memory = self._normalize(current_memory + np.random.normal(0, 0.01, d))
                
                # Comp
                if np.random.random() < comp_prob:
                    k = self._generate(d)
                    v = self._generate(d)
                    current_memory = self._normalize(current_memory + 0.1 * self._circ_conv(k, v))
                    
                # Refresh
                if energy > 0.5 and np.random.random() < rate:
                    k = keys[refresh_idx]
                    v = values[refresh_idx]
                    current_memory = self._normalize(current_memory + 0.5 * self._circ_conv(k, v))
                    refresh_idx = (refresh_idx + 1) % n_items
                    energy -= 0.5
                    
            # Recall
            correct = 0
            for i in range(n_items):
                k_inv = np.roll(keys[i][::-1], 1)
                retrieved = self._circ_conv(current_memory, k_inv)
                if np.dot(retrieved, values[i]) > 0.1:
                    correct += 1
            return correct / n_items

        # Simple optimization (Hill Climbing)
        best_rate = 0.1
        best_acc = run_sim(best_rate)
        
        for i in range(self.iterations):
            perturb = np.random.normal(0, 0.05)
            new_rate = np.clip(best_rate + perturb, 0.01, 1.0)
            acc = run_sim(new_rate)
            
            if acc > best_acc:
                best_rate = new_rate
                best_acc = acc
                
        return best_rate, best_acc

    def run_experiment(self):
        energies = [50.0, 100.0, 200.0, 400.0]
        results = {"conditions": []}
        
        print(f"{ 'Energy':<8} {'Opt Rate':<10} {'Accuracy':<10}")
        print("-" * 35)
        
        for e in energies:
            rates = []
            accs = []
            for t in range(self.num_trials):
                r, a = self.optimize_rate(e, int(e) + t*100)
                rates.append(r)
                accs.append(a)
                
            avg_rate = np.mean(rates)
            avg_acc = np.mean(accs)
            
            results["conditions"].append({
                "energy": e,
                "optimal_rate": float(avg_rate),
                "accuracy": float(avg_acc)
            })
            
            print(f"{e:<8.1f} {avg_rate:<10.3f} {avg_acc:<10.3f}")
            
        return results

    def analyze(self, results):
        conds = results["conditions"]
        
        energies = [c["energy"] for c in conds]
        rates = [c["optimal_rate"] for c in conds]
        
        # Check correlations
        correlation = np.corrcoef(energies, rates)[0, 1]
        
        findings = []
        findings.append(f"Correlation (Energy vs Rate): {correlation:.3f}")
        
        # Determine scaling law
        # Is Rate constant? Or proportional?
        rate_variance = np.var(rates)
        
        if rate_variance < 0.005:
            status = "STRUCTURAL_CONSTANT"
            findings.append("Optimal rate is independent of energy (Structural Requirement).")
        elif correlation > 0.9:
            status = "ENERGY_DEPENDENT"
            findings.append("Optimal rate scales with energy budget.")
        else:
            status = "COMPLEX_NONLINEAR"
            
        return {"status": status, "findings": findings}

def main():
    print("="*60)
    print("Cycle 2076: Universality Test (Energy Scale)")
    print("Hypothesis: Rate is structural, not budgetary.")
    print("="*60)
    
    exp = UniversalityTestEnergy()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2076_universality.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()