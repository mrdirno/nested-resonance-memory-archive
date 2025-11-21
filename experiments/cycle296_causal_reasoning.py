import sys
import os
import numpy as np
import json
import time

# Ensure the project root is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class HolographicCausalMemory:
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
    
    def _reverse(self, v):
        """Time-reversal (Involution) for real vectors"""
        # x[n] -> x[-n]. For DFT: [x0, xN-1, ..., x1]
        return np.concatenate([v[:1], v[1:][::-1]])

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return v 

    def store_transition(self, cause, effect):
        """Store A -> B as A * Reverse(B)"""
        # M = A * B'
        term = self._circ_conv(cause, self._reverse(effect))
        self.memory_trace += term
        
    def predict_effect(self, cause, possible_effects=None):
        """Predict B given A. Retrieve B = Reverse(M # A)"""
        # M = A * B'
        # M # A = (A * B') * A' = B'
        # Reverse(B') = B
        
        # M # B = (A * B') * B' = A * (B')^2 -> Noise
        
        corr = self._circ_corr(self.memory_trace, cause)
        prediction = self._reverse(corr)
        
        if possible_effects is None:
            return prediction
            
        # Cleanup
        best_match = None
        max_sim = -1.0
        
        for val_vec in possible_effects:
            sim = np.dot(self._normalize(prediction), self._normalize(val_vec))
            if sim > max_sim:
                max_sim = sim
                best_match = val_vec
                
        return best_match

class CausalExperiment:
    def __init__(self):
        self.mem = HolographicCausalMemory(dimension=2048)
        self.num_trials = 100
        self.results = {
            "direct_accuracy": 0.0,
            "reverse_accuracy": 0.0,
            "chained_accuracy": 0.0
        }

    def run(self):
        print("Cycle 296: Causal Reasoning Experiment (Asymmetric)")
        print("---------------------------------------------------")
        
        direct_hits = 0
        reverse_hits = 0
        chained_hits = 0
        
        for _ in range(self.num_trials):
            # 1. Generate Events A, B, C
            A = self.mem.generate_vector()
            B = self.mem.generate_vector()
            C = self.mem.generate_vector()
            
            # Reset memory
            self.mem.memory_trace = np.zeros(self.mem.d)
            
            # 2. Store Transitions: A -> B, B -> C
            self.mem.store_transition(A, B)
            self.mem.store_transition(B, C)
            
            # 3. Test 1: Direct Prediction (A -> ?)
            # Should retrieve B
            predicted_B = self.mem.predict_effect(A, possible_effects=[A, B, C])
            if predicted_B is B:
                direct_hits += 1
                
            # 4. Test 2: Asymmetry (B -> ?)
            # Should retrieve C. Should NOT retrieve A.
            # M # B -> Noise (from A->B term) + C' (from B->C term).
            # Reverse -> Noise + C.
            # So it should retrieve C.
            # It should NOT retrieve A.
            pred_from_B = self.mem.predict_effect(B, possible_effects=[A, B, C])
            if pred_from_B is A:
                reverse_hits += 1
            
            # 5. Test 3: Chained Inference (A -> -> ?)
            # Predict B from A (No cleanup), then predict C from noisy B
            noisy_B = self.mem.predict_effect(A) 
            
            # Predict C from noisy B
            noisy_C = self.mem.predict_effect(noisy_B)
            
            # Cleanup C
            final_C = None
            max_sim_C = -1.0
            for val in [A, B, C]:
                sim = np.dot(self.mem._normalize(noisy_C), self.mem._normalize(val))
                if sim > max_sim_C:
                    max_sim_C = sim
                    final_C = val
            
            if final_C is C:
                chained_hits += 1
                
        self.results["direct_accuracy"] = direct_hits / self.num_trials
        self.results["reverse_accuracy"] = reverse_hits / self.num_trials
        self.results["chained_accuracy"] = chained_hits / self.num_trials
        
        print(f"Direct Prediction (A->B): {self.results['direct_accuracy']*100:.1f}%")
        print(f"Reverse Error (B->A): {self.results['reverse_accuracy']*100:.1f}%")
        print(f"Chained Inference (A->->C): {self.results['chained_accuracy']*100:.1f}%")
        
        return self.results

if __name__ == "__main__":
    exp = CausalExperiment()
    results = exp.run()
    
    with open("experiments/cycle296_results.json", "w") as f:
        json.dump(results, f, indent=4)
