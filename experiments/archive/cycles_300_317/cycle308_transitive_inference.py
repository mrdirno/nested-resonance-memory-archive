import numpy as np
import sys
import os

class HolographicTransitiveMemory:
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
        """Circular Correlation (Unbinding: a * b^-1)"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)
    
    def extract_relation(self, source, target):
        """R = Target * Source^-1"""
        return self._circ_corr(target, source)

    def compose_relations(self, r1, r2):
        """R_new = R1 * R2"""
        return self._circ_conv(r1, r2)

    def apply_relation(self, source, relation):
        """Target = Source * Relation"""
        return self._circ_conv(source, relation)

class TransitiveInferenceExperiment:
    def __init__(self):
        self.mem = HolographicTransitiveMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "inference_accuracy": 0.0,
            "avg_similarity": 0.0
        }

    def run(self):
        print("Cycle 308: Transitive Inference Experiment")
        print("------------------------------------------")
        
        correct_count = 0
        total_sim = 0.0
        
        for i in range(self.num_trials):
            # 1. Define Vectors (Nodes in the graph)
            A = self.mem.generate_vector()
            B = self.mem.generate_vector()
            C = self.mem.generate_vector()
            
            # Distractors
            D = self.mem.generate_vector()
            
            # 2. Extract Relations (The "Edges")
            # A -> B
            R_AB = self.mem.extract_relation(A, B)
            # B -> C
            R_BC = self.mem.extract_relation(B, C)
            
            # 3. Infer Transitive Relation (A -> C)
            # R_AC = R_AB * R_BC
            # Algebraically: (B * A^-1) * (C * B^-1) = C * A^-1 * (B * B^-1) approx C * A^-1
            R_AC_inferred = self.mem.compose_relations(R_AB, R_BC)
            
            # 4. Predict C from A
            # C_pred = A * R_AC_inferred
            C_pred = self.mem.apply_relation(A, R_AC_inferred)
            
            # 5. Verify
            # Check similarity to C
            sim_C = np.dot(self.mem._normalize(C_pred), self.mem._normalize(C))
            total_sim += sim_C
            
            # Check against distractor
            sim_D = np.dot(self.mem._normalize(C_pred), self.mem._normalize(D))
            
            # Threshold for success
            if sim_C > 0.3: # Expecting some noise from the B*B^-1 term
                correct_count += 1
            
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Path: A -> B -> C")
                print(f"  Inferred Shortcut: A -> C")
                print(f"  Prediction Similarity to C: {sim_C:.4f}")
                print(f"  Prediction Similarity to D: {sim_D:.4f}")

        self.results["inference_accuracy"] = correct_count / self.num_trials
        self.results["avg_similarity"] = total_sim / self.num_trials
        
        print("\nResults Summary:")
        print(f"Inference Accuracy (>0.3 sim): {self.results['inference_accuracy']*100:.1f}%")
        print(f"Avg Similarity: {self.results['avg_similarity']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = TransitiveInferenceExperiment()
    results = exp.run()
