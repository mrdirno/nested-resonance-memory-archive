import sys
import os
import numpy as np
import json
import time

# Ensure the project root is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class HolographicMemory:
    def __init__(self, dimension=2048): # Increased dimension for better capacity at depth
        self.d = dimension
        
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: return v
        return v / norm

    def _circ_conv(self, a, b):
        """Circular Convolution (Binding)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        """Circular Correlation (Unbinding)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return v 

class RecursiveExperiment:
    def __init__(self):
        self.hrr = HolographicMemory(dimension=2048)
        self.max_depth = 5
        self.num_trials = 100
        self.results = {"depth": [], "accuracy": []}

    def run(self):
        print("Cycle 295: Recursive Composition Experiment")
        print("-------------------------------------------")
        
        for depth in range(1, self.max_depth + 1):
            print(f"\nTesting Recursion Depth: {depth}")
            hits = 0
            
            for _ in range(self.num_trials):
                # 1. Generate Items
                items = [self.hrr.generate_vector() for _ in range(depth + 1)]
                
                # 2. Recursive Binding: ((A + B) + C) ...
                # Start with A + B (Binding is usually A * B, but here we use + for superposition? 
                # Wait, recursive structure is usually binding. 
                # Let's define structure: S_0 = Item_0
                # S_n = S_{n-1} * Item_n (Binding)
                # If we just sum, it's a bag of words. If we bind, it's structure.
                # Let's test strictly hierarchical binding: S = (...((I0 * I1) * I2) * ... * In)
                
                structure = items[0]
                for i in range(1, depth + 1):
                    structure = self.hrr._circ_conv(structure, items[i])
                
                # 3. Recursive Unbinding (Peeling the onion)
                # To recover Item_0, we need to unbind Item_n, then Item_{n-1}...
                # But usually we want to query: "What is bound to S_{n-1}?" -> Item_n
                # Let's try to recover the DEEPEST item (Item_0) by unbinding all others.
                
                current_trace = structure
                
                # Unbind items from n down to 1 to reveal Item_0
                for i in range(depth, 0, -1):
                    current_trace = self.hrr._circ_corr(current_trace, items[i])
                
                # 4. Check if result matches Item_0
                # We compare against ALL items to see if we picked the right one
                # (Simulating a cleanup memory of all possible atomic concepts)
                
                recovered = current_trace
                best_match = None
                max_sim = -1.0
                
                # Cleanup against the specific items used in this trial (simulating active context)
                for item in items:
                    sim = np.dot(self.hrr._normalize(recovered), self.hrr._normalize(item))
                    if sim > max_sim:
                        max_sim = sim
                        best_match = item
                
                # Check identity
                if best_match is items[0]:
                    hits += 1
            
            accuracy = hits / self.num_trials
            self.results["depth"].append(depth)
            self.results["accuracy"].append(accuracy)
            print(f"Depth {depth} Accuracy: {accuracy*100:.1f}%")

        return self.results

if __name__ == "__main__":
    exp = RecursiveExperiment()
    results = exp.run()
    
    with open("experiments/cycle295_results.json", "w") as f:
        json.dump(results, f, indent=4)
