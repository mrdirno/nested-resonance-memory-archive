import numpy as np
import sys
import os

class HolographicMemory:
    def __init__(self, dimension=2048):
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
        """Circular Correlation (Unbinding)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))
    
    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return v 
    
    def store_pair(self, key, value):
        """Store K -> V as K * V"""
        term = self._circ_conv(key, value)
        self.memory_trace += term
        
    def retrieve(self, key, possible_values=None):
        """Retrieve V given K"""
        noisy_val = self._circ_corr(self.memory_trace, key)
        
        if possible_values is None:
            return noisy_val, 0.0
            
        # Cleanup
        best_match = None
        max_sim = -1.0
        
        noisy_val_norm = self._normalize(noisy_val)
        
        for val_vec in possible_values:
            sim = np.dot(noisy_val_norm, self._normalize(val_vec))
            if sim > max_sim:
                max_sim = sim
                best_match = val_vec
                
        return best_match, max_sim

class HolographicSelfCorrectingMemory:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.auto_mem = HolographicMemory(dimension)   # Stores K -> K
        self.hetero_mem = HolographicMemory(dimension) # Stores K -> V
        
    def store(self, key, value):
        # 1. Learn the valid key pattern (Auto-Association)
        self.auto_mem.store_pair(key, key)
        
        # 2. Learn the association (Hetero-Association)
        self.hetero_mem.store_pair(key, value)
        
    def retrieve(self, query_key, possible_values=None, possible_keys=None, threshold=0.5):
        """
        Retrieve with recursive correction.
        """
        # Pass 1: Direct Retrieval
        result_1, conf_1 = self.hetero_mem.retrieve(query_key, possible_values)
        
        print(f"  [Pass 1] Confidence: {conf_1:.4f}")
        
        if conf_1 > threshold:
            return result_1, conf_1, "Direct"
            
        # Pass 2: Correction (Auto-Associative Cleanup)
        print("  [Low Confidence] Triggering Self-Correction...")
        
        # Use Auto-Mem to clean the key
        # We query Auto-Mem with the noisy key. Ideally, it returns the clean key.
        # Note: For Auto-Mem to work well as a cleaner, we might need a cleanup step 
        # if we have a list of valid keys.
        refined_key_raw, _ = self.auto_mem.retrieve(query_key)
        
        # If we have possible_keys (the "vocabulary" of keys), we can snap to the best one.
        # This is the "conscious" step of recognizing the key.
        refined_key = refined_key_raw
        if possible_keys:
            best_k = None
            max_k_sim = -1.0
            refined_norm = self.hetero_mem._normalize(refined_key_raw)
            for k in possible_keys:
                sim = np.dot(refined_norm, self.hetero_mem._normalize(k))
                if sim > max_k_sim:
                    max_k_sim = sim
                    best_k = k
            refined_key = best_k
            print(f"  [Correction] Key Recognition Confidence: {max_k_sim:.4f}")
        
        # Pass 3: Retry with Refined Key
        result_2, conf_2 = self.hetero_mem.retrieve(refined_key, possible_values)
        print(f"  [Pass 2] Confidence: {conf_2:.4f}")
        
        return result_2, conf_2, "Corrected"

class CorrectionExperiment:
    def __init__(self):
        self.mem = HolographicSelfCorrectingMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "direct_accuracy": 0.0,
            "corrected_accuracy": 0.0,
            "correction_rate": 0.0 # How often correction was triggered
        }

    def run(self):
        print("Cycle 302: Recursive Self-Correction Experiment")
        print("---------------------------------------------")
        
        hits_direct = 0
        hits_corrected = 0
        corrections_triggered = 0
        
        for i in range(self.num_trials):
            # 1. Setup
            K = self.mem.hetero_mem.generate_vector()
            V = self.mem.hetero_mem.generate_vector()
            
            # Distractors
            K_dist = self.mem.hetero_mem.generate_vector()
            V_dist = self.mem.hetero_mem.generate_vector()
            
            possible_keys = [K, K_dist]
            possible_values = [V, V_dist]
            
            # Reset memories
            self.mem.auto_mem.memory_trace = np.zeros(self.mem.d)
            self.mem.hetero_mem.memory_trace = np.zeros(self.mem.d)
            
            # Store
            self.mem.store(K, V)
            self.mem.store(K_dist, V_dist)
            
            # 2. Generate Noisy Query
            # Add significant noise to K
            noise_level = 1.5 # High noise
            Noise = self.mem.hetero_mem.generate_vector()
            K_noisy = self.mem.hetero_mem._normalize(K + Noise * noise_level)
            
            print(f"\nTrial {i+1}:")
            
            # 3. Test Direct Retrieval (Control)
            # We simulate what would happen without the wrapper logic
            res_direct, conf_direct = self.mem.hetero_mem.retrieve(K_noisy, possible_values)
            if res_direct is V:
                hits_direct += 1
            
            # 4. Test Corrected Retrieval
            # We use a high threshold to force correction if noise is high
            res_final, conf_final, method = self.mem.retrieve(K_noisy, possible_values, possible_keys, threshold=0.6)
            
            if res_final is V:
                hits_corrected += 1
                
            if method == "Corrected":
                corrections_triggered += 1
                
        self.results["direct_accuracy"] = hits_direct / self.num_trials
        self.results["corrected_accuracy"] = hits_corrected / self.num_trials
        self.results["correction_rate"] = corrections_triggered / self.num_trials
        
        print("\nResults Summary:")
        print(f"Direct Retrieval Accuracy (Noisy): {self.results['direct_accuracy']*100:.1f}%")
        print(f"Corrected Retrieval Accuracy: {self.results['corrected_accuracy']*100:.1f}%")
        print(f"Correction Trigger Rate: {self.results['correction_rate']*100:.1f}%")
        
        return self.results

if __name__ == "__main__":
    exp = CorrectionExperiment()
    results = exp.run()
