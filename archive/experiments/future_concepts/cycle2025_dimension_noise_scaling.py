import numpy as np
import json
import os
import datetime

class HolographicNoiseExperiment:
    def __init__(self):
        self.results = []
        self.timestamp = datetime.datetime.now().isoformat()

    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: return v
        return v / norm

    def generate_vector(self, d):
        v = np.random.normal(0, 1.0/np.sqrt(d), d)
        return self._normalize(v)

    def test_capacity(self, dimension, noise_std, num_items=10, trials=20):
        """
        Tests retrieval accuracy for a given dimension and noise level.
        """
        correct_count = 0
        
        for _ in range(trials):
            # 1. Generate Items
            items = [self.generate_vector(dimension) for _ in range(num_items)]
            
            # 2. Superpose
            memory = np.sum(items, axis=0)
            
            # 3. Add Noise
            noise = np.random.normal(0, noise_std, dimension)
            noisy_memory = memory + noise
            
            # 4. Retrieve
            # Check if each item is retrieved correctly (dot product > threshold)
            # Threshold is tricky with noise. 
            # Instead, let's check if the item is closer to the memory than a random vector?
            # Or standard retrieval check: dot(M, I) > 0.5?
            # With superposition of 10 items, expected dot is 1/10? No.
            # M = I1 + ... + I10.
            # M . I1 = 1 + sum(noise).
            # So expected dot is 1.0.
            # With added noise N: (M+N).I1 = 1 + sum(inter-item) + N.I1.
            
            # Let's use a strict check: Is the dot product > 0.5?
            # Or better: Can we distinguish it from a random vector?
            # Let's count "successful retrievals".
            
            trial_success = 0
            for item in items:
                sim = np.dot(noisy_memory, item)
                # Expected sim for target = 1.0
                # Expected sim for random = 0.0
                # With 10 items, noise from other items is sqrt(9/D).
                # External noise is sigma * sqrt(1/D)? No.
                # Noise vector N has std sigma. Length is sigma * sqrt(D).
                # Dot product N . I (unit vector) is Normal(0, sigma).
                
                # So we have Signal (1.0) + Interference (N(0, sqrt(K-1)/sqrt(D))) + External Noise (N(0, sigma)).
                # We want Signal > Noise.
                # Let's set threshold at 0.5.
                if sim > 0.5:
                    trial_success += 1
            
            if trial_success == num_items:
                correct_count += 1
                
        return correct_count / trials

    def run(self):
        print("Cycle 2025: Dimension Noise Scaling")
        print("-----------------------------------")
        
        dimensions = [512, 1024, 2048, 4096, 8192]
        noise_levels = np.arange(0.0, 2.1, 0.1)
        
        scaling_data = {}
        
        for d in dimensions:
            print(f"\nTesting Dimension: {d}")
            sigma_crit = 0.0
            
            for sigma in noise_levels:
                accuracy = self.test_capacity(d, sigma, num_items=10)
                print(f"  Noise {sigma:.1f}: Accuracy {accuracy:.2f}")
                
                if accuracy < 0.9:
                    # Found the breaking point
                    sigma_crit = sigma
                    print(f"  -> Critical Noise Limit: {sigma_crit:.2f}")
                    break
            
            # If we didn't break, limit is > 2.0
            if sigma_crit == 0.0 and accuracy >= 0.9:
                sigma_crit = 2.0
                
            scaling_data[d] = sigma_crit
            
            self.results.append({
                "dimension": d,
                "sigma_crit": sigma_crit
            })

        # Save Results
        output_path = "data/results/cognitive/c2025_dimension_noise_scaling.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "cycle": 2025,
                "timestamp": self.timestamp,
                "scaling_data": scaling_data,
                "results": self.results
            }, f, indent=2)
            
        print("\nScaling Analysis:")
        print("Dimension | Sigma_crit | Ratio (Sigma/sqrt(D))")
        for res in self.results:
            d = res['dimension']
            s = res['sigma_crit']
            ratio = s / np.sqrt(d)
            print(f"{d:9d} | {s:10.2f} | {ratio:.5f}")

if __name__ == "__main__":
    exp = HolographicNoiseExperiment()
    exp.run()
