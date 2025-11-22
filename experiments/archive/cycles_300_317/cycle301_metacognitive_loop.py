import numpy as np
import sys
import os

class HolographicMetacognitiveMemory:
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
        
    def retrieve_with_confidence(self, key, cleanup_memory=None):
        """
        Retrieve V given K, and return (best_match, confidence).
        Confidence is defined as the cosine similarity to the best match in cleanup memory.
        If cleanup_memory is None, use energy of retrieved vector (less reliable but possible).
        """
        noisy_val = self._circ_corr(self.memory_trace, key)
        
        if cleanup_memory is None:
            # Fallback: Energy metric (norm)
            # Note: In HRR, unbinding from a random trace gives noise with norm ~ sqrt(N_items/D)
            # This is hard to calibrate without knowing N_items.
            # Better to use dot product with self if we expect normalized vectors?
            # Let's stick to cleanup memory for robust confidence.
            return noisy_val, 0.0
            
        # Cleanup and Confidence Calculation
        best_match = None
        max_sim = -1.0
        
        # Normalize noisy_val for cosine similarity
        noisy_val_norm = self._normalize(noisy_val)
        
        for val_vec in cleanup_memory:
            sim = np.dot(noisy_val_norm, self._normalize(val_vec))
            if sim > max_sim:
                max_sim = sim
                best_match = val_vec
                
        return best_match, max_sim

class MetacognitiveExperiment:
    def __init__(self):
        self.mem = HolographicMetacognitiveMemory(dimension=2048)
        self.num_trials = 100
        self.results = {
            "known_confidence_avg": 0.0,
            "noisy_confidence_avg": 0.0,
            "unknown_confidence_avg": 0.0,
            "decision_accuracy": 0.0
        }

    def run(self):
        print("Cycle 301: Metacognitive Loop Experiment")
        print("----------------------------------------")
        
        known_conf_sum = 0.0
        noisy_conf_sum = 0.0
        unknown_conf_sum = 0.0
        
        correct_decisions = 0
        
        # Thresholds
        CONF_HIGH = 0.8
        CONF_LOW = 0.2 # Lowered for "Unknown" detection
        
        for _ in range(self.num_trials):
            # 1. Setup
            A = self.mem.generate_vector()
            B = self.mem.generate_vector()
            C = self.mem.generate_vector()
            D = self.mem.generate_vector()
            
            # Cleanup memory (Possible answers)
            cleanup = [B, D]
            
            # Store A->B, C->D
            self.mem.memory_trace = np.zeros(self.mem.d)
            self.mem.store_pair(A, B)
            self.mem.store_pair(C, D)
            
            # 2. Test Known (Query A)
            _, conf_known = self.mem.retrieve_with_confidence(A, cleanup)
            known_conf_sum += conf_known
            
            # 3. Test Noisy (Query A + Noise)
            Noise = self.mem.generate_vector() * 0.5 # Additive noise
            A_noisy = self.mem._normalize(A + Noise)
            _, conf_noisy = self.mem.retrieve_with_confidence(A_noisy, cleanup)
            noisy_conf_sum += conf_noisy
            
            # 4. Test Unknown (Query Z)
            Z = self.mem.generate_vector()
            _, conf_unknown = self.mem.retrieve_with_confidence(Z, cleanup)
            unknown_conf_sum += conf_unknown
            
            # 5. Verify Decisions
            # Known should be > CONF_HIGH
            # Unknown should be < CONF_LOW (or significantly lower than Known)
            # Noisy should be intermediate
            
            is_correct = True
            if conf_known < 0.5: is_correct = False # Should be high
            if conf_unknown > 0.3: is_correct = False # Should be low (chance correlation)
            
            if is_correct:
                correct_decisions += 1
                
        self.results["known_confidence_avg"] = known_conf_sum / self.num_trials
        self.results["noisy_confidence_avg"] = noisy_conf_sum / self.num_trials
        self.results["unknown_confidence_avg"] = unknown_conf_sum / self.num_trials
        self.results["decision_accuracy"] = correct_decisions / self.num_trials
        
        print(f"Known Confidence (Avg): {self.results['known_confidence_avg']:.4f}")
        print(f"Noisy Confidence (Avg): {self.results['noisy_confidence_avg']:.4f}")
        print(f"Unknown Confidence (Avg): {self.results['unknown_confidence_avg']:.4f}")
        print(f"Decision Accuracy: {self.results['decision_accuracy']*100:.1f}%")
        
        return self.results

if __name__ == "__main__":
    exp = MetacognitiveExperiment()
    results = exp.run()
