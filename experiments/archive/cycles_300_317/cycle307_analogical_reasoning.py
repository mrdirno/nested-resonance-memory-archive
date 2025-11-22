import numpy as np
import sys
import os

class HolographicAnalogicalMemory:
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
        """Circular Correlation (Unbinding: a * b^-1) -> fft(a) * conj(fft(b))"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)
    
    def extract_relation(self, source, target):
        """
        Extract Relation R such that Source * R = Target
        R = Target * Source^-1
        """
        return self._circ_corr(target, source)

    def apply_relation(self, source, relation):
        """
        Apply Relation R to Source: Target = Source * R
        """
        return self._circ_conv(source, relation)

class AnalogicalReasoningExperiment:
    def __init__(self):
        self.mem = HolographicAnalogicalMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "analogy_accuracy": 0.0,
            "avg_similarity": 0.0
        }

    def run(self):
        print("Cycle 307: Analogical Reasoning Experiment")
        print("------------------------------------------")
        
        correct_count = 0
        total_sim = 0.0
        
        for i in range(self.num_trials):
            # 1. Define Base Vectors (The "Ontology")
            France = self.mem.generate_vector()
            Japan = self.mem.generate_vector()
            Capital_Relation = self.mem.generate_vector() # The hidden relation
            
            # 2. Construct Fact Vectors (The "World")
            # Paris is defined as France * Capital
            Paris = self.mem._circ_conv(France, Capital_Relation)
            # Tokyo is defined as Japan * Capital
            Tokyo = self.mem._circ_conv(Japan, Capital_Relation)
            
            # Distractors
            London = self.mem.generate_vector()
            
            # 3. Extract Relation (France -> Paris)
            # R = Paris * France^-1
            # Expected R approx Capital_Relation
            Relation = self.mem.extract_relation(France, Paris)
            
            # 4. Apply Relation (Japan -> ?)
            # Prediction = Japan * Relation
            # Expected Prediction approx Japan * Capital = Tokyo
            Prediction = self.mem.apply_relation(Japan, Relation)
            
            # 5. Verify
            # Check similarity to Tokyo
            sim_tokyo = np.dot(self.mem._normalize(Prediction), self.mem._normalize(Tokyo))
            total_sim += sim_tokyo
            
            # Check against distractors
            sim_london = np.dot(self.mem._normalize(Prediction), self.mem._normalize(London))
            
            # In HRR, A * B * A^-1 approx B + Noise.
            # So similarity won't be 1.0, but should be significant.
            if sim_tokyo > 0.3: # Lower threshold due to noise terms
                correct_count += 1
            
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Relation: France -> Paris (Constructed as France * Capital)")
                print(f"  Query:    Japan  -> ?")
                print(f"  Expected: Tokyo (Constructed as Japan * Capital)")
                print(f"  Prediction Similarity to Tokyo:  {sim_tokyo:.4f}")
                print(f"  Prediction Similarity to London: {sim_london:.4f}")

        self.results["analogy_accuracy"] = correct_count / self.num_trials
        self.results["avg_similarity"] = total_sim / self.num_trials
        
        print("\nResults Summary:")
        print(f"Analogy Accuracy (>0.3 sim): {self.results['analogy_accuracy']*100:.1f}%")
        print(f"Avg Similarity: {self.results['avg_similarity']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = AnalogicalReasoningExperiment()
    results = exp.run()
