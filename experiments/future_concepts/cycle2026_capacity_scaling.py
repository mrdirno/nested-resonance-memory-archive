import numpy as np
import json
import os
import datetime
from scipy import stats

class HolographicCapacityExperiment:
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

    def test_capacity(self, dimension, max_items=2000, step=10, trials=10):
        """
        Tests max capacity for a given dimension.
        Capacity is defined as the max number of items where retrieval accuracy is > 0.99.
        """
        # Binary search or linear scan? Linear scan is safer to see the curve.
        # But we can be smart.
        # Let's do chunks.
        
        # Actually, let's just add items one by one (or in batches) until failure.
        
        # Optimization: We don't need to re-generate everything.
        # We can keep adding to the superposition.
        
        # But we need to average over trials.
        
        k_crit_sum = 0
        
        for t in range(trials):
            items = []
            memory = np.zeros(dimension)
            
            # We'll add in batches
            current_k = 0
            alive = True
            
            while alive and current_k < max_items:
                # Add batch
                batch_size = step
                new_items = [self.generate_vector(dimension) for _ in range(batch_size)]
                
                # Update memory
                # Note: In standard HRR, M = sum(Xi).
                # We don't re-normalize M usually, but for dot product similarity we might need to scale.
                # If we don't normalize M, dot(M, Xi) = 1 + noise.
                # If we normalize M, dot(M, Xi) = 1/sqrt(K) + noise.
                # Let's stick to unnormalized M for simplicity of math (Signal = 1.0).
                
                for item in new_items:
                    memory += item
                    items.append(item)
                
                current_k += batch_size
                
                # Test Retrieval of ALL items
                # This is expensive O(K^2).
                # We can just test a sample? No, "Capacity" implies *all* are retrievable.
                # Or at least, the probability of error is low.
                
                # Let's test a random sample of 50 items if K is large, to save time.
                test_subset = items
                if len(items) > 50:
                    # Random sample
                    indices = np.random.choice(len(items), 50, replace=False)
                    test_subset = [items[i] for i in indices]
                
                success_count = 0
                for item in test_subset:
                    # Sim = dot(M, item)
                    # Expected Signal = 1.0
                    # Noise Variance = (K-1)/D.
                    # We need Signal > Noise.
                    # But what is the threshold?
                    # In a clean system, we just need to distinguish from non-stored items.
                    # Non-stored item sim ~ N(0, K/D).
                    # Stored item sim ~ N(1, (K-1)/D).
                    # We need 1 > 3*sigma (for 99% confidence)?
                    # sigma = sqrt(K/D).
                    # 1 > 3 * sqrt(K/D) => 1 > 9 * K/D => D > 9K => K < D/9.
                    
                    # Let's use a fixed threshold of 0.7?
                    # Or just check if it's distinguishable.
                    # Let's use a threshold of 0.5.
                    # If noise is high, 0.5 might be crossed by non-stored items.
                    
                    sim = np.dot(memory, item)
                    if sim > 0.5:
                        success_count += 1
                
                accuracy = success_count / len(test_subset)
                
                if accuracy < 0.99:
                    alive = False
                    # The previous step was the last good one.
                    # Let's say failure happened halfway through this batch?
                    # Conservative: return current_k - batch_size.
                    k_crit_sum += (current_k - batch_size)
            
            if alive:
                # Reached max_items
                k_crit_sum += max_items
                
        return k_crit_sum / trials

    def run(self):
        print("Cycle 2026: Capacity Scaling Experiment")
        print("---------------------------------------")
        
        dimensions = [512, 1024, 2048, 4096, 8192]
        
        scaling_data = {}
        
        print(f"{'Dimension':<10} | {'K_crit':<10} | {'Alpha (K/D)':<15}")
        print("-" * 40)
        
        for d in dimensions:
            # Adjust max_items based on expected alpha ~ 0.15
            # 8192 * 0.2 = 1600. Max 2000 is fine.
            # For small D, step can be smaller.
            step = max(5, int(d / 100))
            
            k_crit = self.test_capacity(d, max_items=int(d*0.5), step=step, trials=5)
            alpha = k_crit / d
            
            print(f"{d:<10} | {k_crit:<10.1f} | {alpha:<15.4f}")
            
            scaling_data[d] = k_crit
            
            self.results.append({
                "dimension": d,
                "k_crit": k_crit,
                "alpha": alpha
            })

        # Analysis
        x = np.array([r['dimension'] for r in self.results])
        y = np.array([r['k_crit'] for r in self.results])
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        print("\nRegression Analysis:")
        print(f"Slope (Alpha): {slope:.4f}")
        print(f"R-squared:     {r_value**2:.4f}")
        
        if r_value**2 > 0.98:
            print("SUCCESS: Linear scaling confirmed.")
        else:
            print("FAILURE: Scaling is not linear.")

        # Save Results
        output_path = "data/results/cognitive/c2026_capacity_scaling.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump({
                "cycle": 2026,
                "timestamp": self.timestamp,
                "scaling_data": scaling_data,
                "regression": {
                    "slope": slope,
                    "r_squared": r_value**2
                },
                "results": self.results
            }, f, indent=2)

if __name__ == "__main__":
    exp = HolographicCapacityExperiment()
    exp.run()
