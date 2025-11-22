"""
Cycle 2080: Exponential Growth Dynamics
========================================
Projecting the resource cost of Human-Level Cognition.

From C2079: Depth is capped by Noise at D=1024.
Hypothesis: Required Dimension D scales exponentially with Depth.
D_req = D_0 * exp(alpha * Depth)

Design:
- Find min D required for Depth [1, 2, 3, 4].
- Fit exponential curve.
- Extrapolate D required for Depth 7 (Human Working Memory).
"""

import numpy as np
import json
from datetime import datetime

class ExponentialGrowthDynamics:
    def __init__(self):
        self.depths = [1, 2, 3, 4]
        self.num_trials = 5
        # Search range for D
        self.d_range = [512, 1024, 2048, 4096, 8192, 16384]

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v

    def _circ_conv(self, a, b):
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _generate(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def check_depth(self, d, depth, seed):
        """Check if dimension D supports given depth."""
        np.random.seed(seed)
        
        # Create atoms
        atoms = [self._generate(d) for _ in range(depth + 1)]
        
        # Build target
        target = atoms[0]
        for i in range(1, depth + 1):
            target = self._normalize(self._circ_conv(target, atoms[i]))
            
        # Store atoms (No Cleanup, Pure Capacity Test)
        memory = np.zeros(d)
        keys = []
        for atom in atoms:
            k = self._generate(d)
            memory += self._circ_conv(k, atom)
            keys.append(k)
        memory = self._normalize(memory)
        
        # Retrieve & Compose
        current = None
        for i, k in enumerate(keys):
            k_inv = np.roll(k[::-1], 1)
            retrieved = self._circ_conv(memory, k_inv)
            
            if current is None:
                current = retrieved
            else:
                current = self._normalize(self._circ_conv(current, retrieved))
                
        sim = np.dot(current, target)
        return sim > 0.1 # Consistent threshold

    def find_min_dimension(self, depth):
        """Binary search or scan for min D."""
        for d in self.d_range:
            success_count = 0
            for t in range(self.num_trials):
                if self.check_depth(d, depth, t*100 + depth):
                    success_count += 1
            
            if success_count / self.num_trials >= 0.8:
                return d
        return -1 # Failed even at max D

    def run_experiment(self):
        results = {"points": []}
        
        print(f"{'Depth':<8} {'Min D':<10}")
        print("-" * 20)
        
        for depth in self.depths:
            min_d = self.find_min_dimension(depth)
            
            results["points"].append({
                "depth": depth,
                "min_dimension": min_d
            })
            
            print(f"{depth:<8} {min_d:<10}")
            
        return results

    def analyze(self, results):
        points = [p for p in results["points"] if p["min_dimension"] > 0]
        
        depths = np.array([p["depth"] for p in points])
        dims = np.array([p["min_dimension"] for p in points])
        
        if len(points) < 2:
            return {"status": "INSUFFICIENT_DATA", "findings": []}
            
        # Fit Exponential: D = a * exp(b * depth)
        # ln(D) = ln(a) + b * depth
        log_dims = np.log(dims)
        coeffs = np.polyfit(depths, log_dims, 1)
        
        b = coeffs[0]
        a = np.exp(coeffs[1])
        
        predicted = a * np.exp(b * depths)
        r_squared = 1 - np.sum((dims - predicted)**2) / np.sum((dims - np.mean(dims))**2)
        
        # Extrapolate
        d_req_7 = a * np.exp(b * 7)
        d_req_9 = a * np.exp(b * 9)
        
        findings = []
        findings.append(f"Scaling Law: D ≈ {a:.0f} * exp({b:.2f} * Depth)")
        findings.append(f"Fit Quality (R²): {r_squared:.3f}")
        findings.append(f"Projected D for Depth 7: {d_req_7:.0f}")
        findings.append(f"Projected D for Depth 9: {d_req_9:.0f}")
        
        return {"status": "SUCCESS", "findings": findings}

def main():
    print("="*60)
    print("Cycle 2080: Exponential Growth Dynamics")
    print("Hypothesis: Cognitive Depth requires Exponential Dimension.")
    print("="*60)
    
    exp = ExponentialGrowthDynamics()
    results = exp.run_experiment()
    analysis = exp.analyze(results)
    
    print("\nANALYSIS:")
    print(f"Status: {analysis['status']}")
    for f in analysis['findings']:
        print(f"- {f}")
    
    with open('/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c2080_exponential_growth.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
