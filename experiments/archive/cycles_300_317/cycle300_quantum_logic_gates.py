import numpy as np
import sys
import os

class HolographicLogicMemory:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.memory_trace = np.zeros(self.d)
        
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: return v
        return v / norm

    def _circ_conv(self, a, b):
        """Circular Convolution (Binding) -> AND"""
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

    def logical_and(self, a, b):
        """AND(A, B) = A * B"""
        return self._circ_conv(a, b)
    
    def logical_or(self, a, b):
        """OR(A, B) = A + B"""
        return self._normalize(a + b)
    
    def logical_not(self, a):
        """NOT(A) = -A"""
        return -a

class LogicGateExperiment:
    def __init__(self):
        self.mem = HolographicLogicMemory(dimension=2048)
        self.num_trials = 100
        self.results = {
            "and_accuracy": 0.0,
            "or_accuracy": 0.0,
            "not_accuracy": 0.0
        }

    def run(self):
        print("Cycle 300: Quantum Logic Gates Experiment")
        print("-----------------------------------------")
        
        hits_and = 0
        hits_or = 0
        hits_not = 0
        
        for _ in range(self.num_trials):
            # 1. AND Gate Test
            # Rule: If A AND B, then C
            A = self.mem.generate_vector()
            B = self.mem.generate_vector()
            C = self.mem.generate_vector()
            
            # Store (A * B) -> C
            self.mem.memory_trace = np.zeros(self.mem.d)
            condition_and = self.mem.logical_and(A, B)
            self.mem.store_pair(condition_and, C)
            
            # Query with A * B
            retrieved_C = self.mem.retrieve(condition_and, possible_values=[A, B, C])
            if retrieved_C is C:
                hits_and += 1
                
            # 2. OR Gate Test
            # Rule: If D OR E, then F
            D = self.mem.generate_vector()
            E = self.mem.generate_vector()
            F = self.mem.generate_vector()
            
            # Store D -> F, E -> F
            self.mem.memory_trace = np.zeros(self.mem.d)
            self.mem.store_pair(D, F)
            self.mem.store_pair(E, F)
            
            # Query with D + E (Superposition)
            # (D+E) * (D*F + E*F) = D*D*F + D*E*F + E*D*F + E*E*F
            # = F + noise + noise + F = 2F + noise
            condition_or = self.mem.logical_or(D, E)
            retrieved_F = self.mem.retrieve(condition_or, possible_values=[D, E, F])
            if retrieved_F is F:
                hits_or += 1
                
            # 3. NOT Gate Test (Inhibition)
            # Scenario: Memory contains G + H. We want to retrieve H by saying "NOT G".
            G = self.mem.generate_vector()
            H = self.mem.generate_vector()
            
            # Memory = G + H
            self.mem.memory_trace = G + H
            
            # Query: Memory - G
            # Result should be H
            result_not = self.mem.memory_trace + self.mem.logical_not(G) # (G+H) - G = H
            
            # Check similarity
            sim_H = np.dot(self.mem._normalize(result_not), self.mem._normalize(H))
            sim_G = np.dot(self.mem._normalize(result_not), self.mem._normalize(G))
            
            if sim_H > 0.9 and sim_G < 0.1: # H should be perfect, G should be gone
                hits_not += 1
                
        self.results["and_accuracy"] = hits_and / self.num_trials
        self.results["or_accuracy"] = hits_or / self.num_trials
        self.results["not_accuracy"] = hits_not / self.num_trials
        
        print(f"AND Gate Accuracy: {self.results['and_accuracy']*100:.1f}%")
        print(f"OR Gate Accuracy: {self.results['or_accuracy']*100:.1f}%")
        print(f"NOT Gate Accuracy: {self.results['not_accuracy']*100:.1f}%")
        
        return self.results

if __name__ == "__main__":
    exp = LogicGateExperiment()
    results = exp.run()
