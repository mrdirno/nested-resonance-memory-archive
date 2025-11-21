import sys
import os
import numpy as np
import json
import time

# Ensure the project root is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class HolographicMemory:
    def __init__(self, dimension=1024):
        self.d = dimension
        self.memory_trace = np.zeros(self.d)
        
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: return v
        return v / norm

    def _circ_conv(self, a, b):
        """Circular Convolution (Binding)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))

    def _circ_corr(self, a, b):
        """Circular Correlation (Unbinding) - Approximate Inverse"""
        # Correlation of a and b is convolution of a and involution of b
        # For real vectors, involution is just reversing the vector (except index 0)
        # Or more simply in Fourier domain: ifft(fft(a) * conj(fft(b)))
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def encode_pair(self, key, value):
        """Bind key and value and add to superposition"""
        # Generate random vectors if inputs are strings/ids
        # For this exp, we assume key and value are already vectors or we gen them here
        # Let's assume we generate them here for simplicity of the test
        pass 

    def store(self, key_vec, value_vec):
        """Bind and Add"""
        trace = self._circ_conv(key_vec, value_vec)
        self.memory_trace += trace
        # We don't normalize the trace itself usually, but for stability we might
        # self.memory_trace = self._normalize(self.memory_trace) 

    def retrieve(self, key_vec, possible_values=None):
        """Unbind and Cleanup"""
        # Noisy recall vector
        noisy_val = self._circ_corr(self.memory_trace, key_vec)
        
        if possible_values is None:
            return noisy_val
            
        # Cleanup Memory: Find closest match in possible_values
        best_match = None
        max_sim = -1.0
        
        for val_vec in possible_values:
            sim = np.dot(self._normalize(noisy_val), self._normalize(val_vec))
            if sim > max_sim:
                max_sim = sim
                best_match = val_vec
                
        return best_match

class DiscreteMemory:
    def __init__(self):
        self.storage = {}
        
    def store(self, key, value):
        self.storage[key] = value
        
    def retrieve(self, key):
        return self.storage.get(key, None)

class HolographicExperiment:
    def __init__(self):
        self.dimension = 1024
        self.num_pairs = 10
        self.noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        self.results = {
            "hrr": {"noise": [], "accuracy": []},
            "discrete": {"noise": [], "accuracy": []}
        }

    def generate_vector(self):
        """Generate a random distributed vector (Gaussian)"""
        v = np.random.normal(0, 1.0/np.sqrt(self.dimension), self.dimension)
        return v # / np.linalg.norm(v) # Normalization usually happens at usage

    def run(self):
        print("Cycle 294: Holographic Memory Experiment")
        print("----------------------------------------")
        
        # 1. Generate Data
        keys = [self.generate_vector() for _ in range(self.num_pairs)]
        values = [self.generate_vector() for _ in range(self.num_pairs)]
        
        # Discrete keys need to be hashable (e.g. bytes of the vector)
        discrete_keys = [k.tobytes() for k in keys]
        
        for noise_std in self.noise_levels:
            print(f"\nTesting Noise Level: {noise_std}")
            
            # --- HRR Test ---
            hrr = HolographicMemory(self.dimension)
            
            # Store
            for k, v in zip(keys, values):
                hrr.store(k, v)
            
            # Inject Noise into Memory Trace (Simulating synaptic degradation)
            noise_vec = np.random.normal(0, noise_std, self.dimension)
            hrr.memory_trace += noise_vec
            
            # Retrieve
            hrr_hits = 0
            for i, k in enumerate(keys):
                retrieved = hrr.retrieve(k, possible_values=values)
                # Check if retrieved is the correct value object (by reference or equality)
                # Since we return the exact object from possible_values list:
                if retrieved is values[i]:
                    hrr_hits += 1
            
            hrr_acc = hrr_hits / self.num_pairs
            self.results["hrr"]["noise"].append(noise_std)
            self.results["hrr"]["accuracy"].append(hrr_acc)
            print(f"HRR Accuracy: {hrr_acc*100:.1f}%")
            
            # --- Discrete Test ---
            disc = DiscreteMemory()
            
            # Store
            for k, v in zip(discrete_keys, values):
                disc.store(k, v)
            
            # Inject Noise into Keys (Simulating input corruption)
            # Discrete memory fails if the key is even slightly different.
            # To be fair, we corrupt the query key.
            
            disc_hits = 0
            for i, k_vec in enumerate(keys):
                # Corrupt the key vector
                noisy_key_vec = k_vec + np.random.normal(0, noise_std, self.dimension)
                noisy_key_bytes = noisy_key_vec.tobytes()
                
                # Retrieve
                retrieved = disc.retrieve(noisy_key_bytes)
                
                # In discrete memory, exact match required. 
                # With float vectors, even 0.0 noise usually fails due to precision, 
                # but here we explicitly add noise.
                if retrieved is values[i]:
                    disc_hits += 1
            
            disc_acc = disc_hits / self.num_pairs
            self.results["discrete"]["noise"].append(noise_std)
            self.results["discrete"]["accuracy"].append(disc_acc)
            print(f"Discrete Accuracy: {disc_acc*100:.1f}%")

        return self.results

if __name__ == "__main__":
    exp = HolographicExperiment()
    results = exp.run()
    
    with open("experiments/cycle294_results.json", "w") as f:
        json.dump(results, f, indent=4)
