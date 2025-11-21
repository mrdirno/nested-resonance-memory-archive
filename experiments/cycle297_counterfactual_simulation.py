import numpy as np
import sys
import os

class HolographicCounterfactualMemory:
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
            return noisy_val
            
        # Cleanup
        best_match = None
        max_sim = -1.0
        
        for val_vec in possible_values:
            sim = np.dot(self._normalize(noisy_val), self._normalize(val_vec))
            if sim > max_sim:
                max_sim = sim
                best_match = val_vec
                
        return best_match

    def substitute(self, old_key, new_key):
        """
        Perform Counterfactual Substitution: Change 'old_key -> V' to 'new_key -> V'
        without explicitly retrieving V.
        
        Operation: M_new = M * inv(old_key) * new_key
        Since we use unitary vectors (approx), inv(old_key) is approx old_key (for correlation)
        or we can use circular correlation to unbind old_key and convolution to bind new_key.
        
        M_new = (M # old_key) * new_key
        """
        # 1. Unbind old_key (Correlation)
        # This gives us V + noise
        extracted_content = self._circ_corr(self.memory_trace, old_key)
        
        # 2. Bind new_key (Convolution)
        # This gives us new_key * V + new_key * noise
        new_term = self._circ_conv(new_key, extracted_content)
        
        # In a real scenario, we might want to subtract the old term and add the new term
        # to the existing trace, or create a purely new trace.
        # For this experiment, we will return a NEW memory trace representing the counterfactual world.
        return new_term

class CounterfactualExperiment:
    def __init__(self):
        self.mem = HolographicCounterfactualMemory(dimension=2048)
        self.num_trials = 100
        self.results = {
            "original_accuracy": 0.0,
            "counterfactual_accuracy": 0.0,
            "control_accuracy": 0.0 # Accuracy of old key on new trace (should be low)
        }

    def run(self):
        print("Cycle 297: Counterfactual Simulation Experiment")
        print("-----------------------------------------------")
        
        orig_hits = 0
        cf_hits = 0
        control_hits = 0
        
        for _ in range(self.num_trials):
            # 1. Generate Vectors
            A = self.mem.generate_vector() # Original Cause
            A_prime = self.mem.generate_vector() # Counterfactual Cause
            B = self.mem.generate_vector() # Effect
            C = self.mem.generate_vector() # Distractor
            
            # Reset memory
            self.mem.memory_trace = np.zeros(self.mem.d)
            
            # 2. Store Original: A -> B
            self.mem.store_pair(A, B)
            
            # 3. Verify Original Retrieval
            retrieved_B = self.mem.retrieve(A, possible_values=[A, A_prime, B, C])
            if retrieved_B is B:
                orig_hits += 1
                
            # 4. Perform Substitution: Create Counterfactual Trace M'
            # "What if A' happened instead of A?"
            # M' should contain A' -> B
            cf_trace_vec = self.mem.substitute(A, A_prime)
            
            # Create a temporary memory object for the counterfactual world
            cf_mem = HolographicCounterfactualMemory(dimension=2048)
            cf_mem.memory_trace = cf_trace_vec
            
            # 5. Test Counterfactual Retrieval: Query M' with A'
            # Should retrieve B
            cf_retrieved = cf_mem.retrieve(A_prime, possible_values=[A, A_prime, B, C])
            if cf_retrieved is B:
                cf_hits += 1
                
            # 6. Control Test: Query M' with A
            # Should NOT retrieve B (link A->B should be broken or noisy in M')
            # M' = (A*B # A) * A' = B * A' (approx)
            # Query M' with A: (B * A') # A. Should be noise.
            control_retrieved = cf_mem.retrieve(A, possible_values=[A, A_prime, B, C])
            if control_retrieved is B:
                control_hits += 1
                
        self.results["original_accuracy"] = orig_hits / self.num_trials
        self.results["counterfactual_accuracy"] = cf_hits / self.num_trials
        self.results["control_accuracy"] = control_hits / self.num_trials
        
        print(f"Original Retrieval (A->B): {self.results['original_accuracy']*100:.1f}%")
        print(f"Counterfactual Retrieval (A'->B): {self.results['counterfactual_accuracy']*100:.1f}%")
        print(f"Control (Old Key on New Trace): {self.results['control_accuracy']*100:.1f}%")
        
        return self.results

if __name__ == "__main__":
    exp = CounterfactualExperiment()
    results = exp.run()
