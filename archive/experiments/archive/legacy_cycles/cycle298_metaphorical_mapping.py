import numpy as np
import sys
import os

class HolographicRelationalMemory:
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
    
    def learn_relation(self, pairs):
        """
        Learn a relation vector R from a list of (cause, effect) pairs.
        R_est = mean( cause_inv * effect )
        Since cause is unitary-ish, cause_inv approx cause_corr.
        R_est = mean( effect # cause )
        """
        R_sum = np.zeros(self.d)
        for cause, effect in pairs:
            # Unbind cause from effect to get the relation
            # If Effect = Cause * R, then R = Effect # Cause
            r_instance = self._circ_corr(effect, cause)
            R_sum += r_instance
            
        return R_sum / len(pairs)

    def apply_relation(self, cause, relation_vec, possible_effects=None):
        """
        Apply relation R to a new cause to predict effect.
        Effect = Cause * R
        """
        predicted_effect = self._circ_conv(cause, relation_vec)
        
        if possible_effects is None:
            return predicted_effect
            
        # Cleanup
        best_match = None
        max_sim = -1.0
        
        for val_vec in possible_effects:
            sim = np.dot(self._normalize(predicted_effect), self._normalize(val_vec))
            if sim > max_sim:
                max_sim = sim
                best_match = val_vec
                
        return best_match

class MetaphoricalExperiment:
    def __init__(self):
        self.mem = HolographicRelationalMemory(dimension=2048)
        self.num_trials = 20 # Number of independent runs
        self.train_size = 10 # Number of examples to learn from
        self.test_size = 5   # Number of new instances to test on
        self.results = {
            "generalization_accuracy": 0.0
        }

    def run(self):
        print("Cycle 298: Metaphorical Mapping Experiment")
        print("------------------------------------------")
        
        total_test_cases = 0
        total_hits = 0
        
        for trial in range(self.num_trials):
            # 1. Generate a "Ground Truth" Relation R_true
            R_true = self.mem.generate_vector()
            
            # 2. Generate Training Pairs (A -> B where B = A * R_true)
            train_pairs = []
            for _ in range(self.train_size):
                A = self.mem.generate_vector()
                B = self.mem._circ_conv(A, R_true)
                train_pairs.append((A, B))
                
            # 3. Learn Relation R_est from Training Pairs
            R_est = self.mem.learn_relation(train_pairs)
            
            # 4. Generate Test Pairs and Predict
            # We generate X, compute Y_true = X * R_true
            # Then predict Y_pred = X * R_est
            # Check if Y_pred matches Y_true (vs distractors)
            
            for _ in range(self.test_size):
                X = self.mem.generate_vector()
                Y_true = self.mem._circ_conv(X, R_true)
                
                # Distractors
                D1 = self.mem.generate_vector()
                D2 = self.mem.generate_vector()
                D3 = self.mem.generate_vector()
                possible = [Y_true, D1, D2, D3]
                
                # Predict
                predicted = self.mem.apply_relation(X, R_est, possible_effects=possible)
                
                if predicted is Y_true:
                    total_hits += 1
                total_test_cases += 1
                
        accuracy = total_hits / total_test_cases
        self.results["generalization_accuracy"] = accuracy
        
        print(f"Generalization Accuracy (Train N={self.train_size}): {accuracy*100:.1f}%")
        
        return self.results

if __name__ == "__main__":
    exp = MetaphoricalExperiment()
    results = exp.run()
