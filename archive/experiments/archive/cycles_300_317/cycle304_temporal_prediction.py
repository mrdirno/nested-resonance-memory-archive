import numpy as np
import sys
import os

class HolographicTemporalMemory:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.memory_trace = np.zeros(self.d)
        # Fixed random permutation for asymmetric encoding
        self.perm_idx = np.random.permutation(self.d)
        
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
    
    def _permute(self, v):
        return v[self.perm_idx]

    def learn_sequence(self, sequence_items):
        """
        Learn transitions: T = Permute(Item_i) * Item_{i+1}
        Random Permutation breaks symmetry and prevents 'roll' artifacts.
        """
        for i in range(len(sequence_items)):
            current_item = sequence_items[i]
            next_item = sequence_items[(i + 1) % len(sequence_items)] # Circular buffer
            
            # Asymmetric Encoding: P(A) * B
            permuted_current = self._permute(current_item)
            transition = self._circ_conv(permuted_current, next_item)
            self.memory_trace += transition
            
    def predict_next(self, current_item, possible_next_states=None):
        """
        Predict next state: Prediction = Memory # Permute(Current_Item)
        """
        # We must unbind the permuted current item
        permuted_current = self._permute(current_item)
        prediction_noisy = self._circ_corr(self.memory_trace, permuted_current)
        
        if possible_next_states is None:
            return prediction_noisy, 0.0
            
        # Cleanup
        best_match = None
        max_sim = -1.0
        pred_norm = self._normalize(prediction_noisy)
        
        for state in possible_next_states:
            sim = np.dot(pred_norm, self._normalize(state))
            if sim > max_sim:
                max_sim = sim
                best_match = state
                
        return best_match, max_sim

class TemporalPredictionExperiment:
    def __init__(self):
        self.mem = HolographicTemporalMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "prediction_accuracy": 0.0,
            "avg_confidence": 0.0
        }

    def run(self):
        print("Cycle 304: Temporal Prediction Experiment")
        print("-----------------------------------------")
        
        correct_predictions = 0
        total_confidence = 0.0
        total_tests = 0
        
        for i in range(self.num_trials):
            # 1. Generate States
            A = self.mem.generate_vector()
            B = self.mem.generate_vector()
            C = self.mem.generate_vector()
            D = self.mem.generate_vector()
            
            states = [A, B, C, D]
            sequence = [A, B, C, D] # A->B->C->D->A
            
            # Distractors
            X = self.mem.generate_vector()
            Y = self.mem.generate_vector()
            possible_next_states = states + [X, Y]
            
            # 2. Learn Sequence
            self.mem.memory_trace = np.zeros(self.mem.d)
            self.mem.learn_sequence(sequence)
            
            # 3. Test Predictions
            # Predict B from A
            pred_B, conf_B = self.mem.predict_next(A, possible_next_states)
            if pred_B is B: correct_predictions += 1
            total_confidence += conf_B
            total_tests += 1
            
            # Predict C from B
            pred_C, conf_C = self.mem.predict_next(B, possible_next_states)
            if pred_C is C: correct_predictions += 1
            total_confidence += conf_C
            total_tests += 1
            
            # Predict D from C
            pred_D, conf_D = self.mem.predict_next(C, possible_next_states)
            if pred_D is D: correct_predictions += 1
            total_confidence += conf_D
            total_tests += 1
            
            # Predict A from D
            pred_A, conf_A = self.mem.predict_next(D, possible_next_states)
            if pred_A is A: correct_predictions += 1
            total_confidence += conf_A
            total_tests += 1
            
            if i == 0:
                print("Trial 1 Details:")
                # Debug: Print all similarities for the first prediction (A->B)
                print("  Predicting B from A:")
                permuted_A = self.mem._permute(A)
                pred_raw = self.mem._circ_corr(self.mem.memory_trace, permuted_A)
                pred_norm = self.mem._normalize(pred_raw)
                
                for idx, cand in enumerate(possible_next_states):
                    sim = np.dot(pred_norm, self.mem._normalize(cand))
                    name = ["A", "B", "C", "D", "X", "Y"][idx]
                    print(f"    Sim({name}): {sim:.4f}")
                    
                print(f"  A->B Confidence: {conf_B:.4f}")
                print(f"  B->C Confidence: {conf_C:.4f}")
                print(f"  C->D Confidence: {conf_D:.4f}")
                print(f"  D->A Confidence: {conf_A:.4f}")
                
        self.results["prediction_accuracy"] = correct_predictions / total_tests
        self.results["avg_confidence"] = total_confidence / total_tests
        
        print("\nResults Summary:")
        print(f"Prediction Accuracy: {self.results['prediction_accuracy']*100:.1f}%")
        print(f"Avg Confidence: {self.results['avg_confidence']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = TemporalPredictionExperiment()
    results = exp.run()
