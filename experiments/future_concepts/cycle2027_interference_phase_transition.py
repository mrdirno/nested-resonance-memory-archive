import numpy as np
import json
import os
import datetime
from scipy.optimize import curve_fit

class HolographicTransitionExperiment:
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

    def measure_accuracy(self, dimension, k, trials=50):
        """
        Measures retrieval accuracy for a specific load K.
        """
        success_count = 0
        
        for _ in range(trials):
            # Generate K items
            items = [self.generate_vector(dimension) for _ in range(k)]
            
            # Superpose
            memory = np.sum(items, axis=0)
            
            # Test one random item (representative)
            # Or test all? Testing all reduces variance.
            # Let's test a sample of 10 items per trial.
            sample_size = min(k, 10)
            indices = np.random.choice(k, sample_size, replace=False)
            
            trial_success = 0
            for idx in indices:
                item = items[idx]
                # Check if retrievable
                # Threshold: We need to distinguish from noise.
                # Signal = 1.0. Noise Var = (K-1)/D.
                # We count "Success" if dot > 0.5 (Arbitrary but consistent).
                # Or better: Is it the closest match? (Too expensive to check against universe).
                # Let's stick to the dot > 0.5 threshold used in C2026.
                
                sim = np.dot(memory, item)
                if sim > 0.5:
                    trial_success += 1
            
            success_count += (trial_success / sample_size)
            
        return success_count / trials

    def sigmoid(self, x, k_crit, beta):
        # We want Acc to go from 1 to 0.
        # Standard sigmoid goes 0 to 1.
        # So: 1 - sigmoid? Or 1 / (1 + exp(beta * (x - k_crit)))
        # If x < k_crit, exp is small, 1/(1+0) = 1.
        # If x > k_crit, exp is large, 1/(1+inf) = 0.
        # This works.
        return 1.0 / (1.0 + np.exp(beta * (x - k_crit)))

    def run(self):
        print("Cycle 2027: Interference Phase Transition")
        print("-----------------------------------------")
        
        dimension = 2048
        k_values = np.arange(10, 205, 5)
        accuracies = []
        
        print(f"Testing Dimension: {dimension}")
        print(f"{'Load (K)':<10} | {'Accuracy':<10}")
        print("-" * 25)
        
        for k in k_values:
            acc = self.measure_accuracy(dimension, k)
            accuracies.append(acc)
            print(f"{k:<10} | {acc:<10.4f}")
            
        # Curve Fitting
        try:
            # Initial guess: K_crit around 96 (from C2026), beta around 0.1
            popt, pcov = curve_fit(self.sigmoid, k_values, accuracies, p0=[96, 0.1], bounds=([10, 0], [200, 1.0]))
            k_crit_fit, beta_fit = popt
            
            print("\nPhase Transition Analysis:")
            print(f"K_crit (Inflection): {k_crit_fit:.2f}")
            print(f"Beta (Steepness):    {beta_fit:.4f}")
            
            if beta_fit > 0.05:
                print("Result: Sharp Phase Transition (The Cliff).")
            else:
                print("Result: Gradual Decay.")
                
        except Exception as e:
            print(f"\nFitting Failed: {e}")
            k_crit_fit = 0
            beta_fit = 0

        # Save Results
        output_path = "data/results/cognitive/c2027_interference_phase_transition.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "cycle": 2027,
                "timestamp": self.timestamp,
                "dimension": dimension,
                "data": {
                    "k": k_values.tolist(),
                    "accuracy": accuracies
                },
                "fit": {
                    "k_crit": k_crit_fit,
                    "beta": beta_fit
                }
            }, f, indent=2)

if __name__ == "__main__":
    exp = HolographicTransitionExperiment()
    exp.run()
