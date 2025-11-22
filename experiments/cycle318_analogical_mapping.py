import numpy as np
import sys
import os

class HolographicAnalogicalMemory:
    def __init__(self, dimension=2048):
        self.d = dimension
        
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: return v
        return v / norm

    def _circ_conv(self, a, b):
        """Binding"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))
    
    def _circ_corr(self, a, b):
        """Unbinding / Correlation"""
        return np.real(np.fft.ifft(np.fft.fft(a) * np.conj(np.fft.fft(b))))

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    def create_structure(self, bindings_list):
        """Sum(Role * Filler)"""
        structure = np.zeros(self.d)
        for role, filler in bindings_list:
            structure += self._circ_conv(role, filler)
        return structure

    def compute_mapping(self, source_structure, target_structure):
        """
        Compute Transformation Vector T such that T * Source ~ Target.
        T = Target * Source^-1 (Correlation)
        """
        return self._circ_corr(target_structure, source_structure)

    def apply_mapping(self, mapping, item):
        """
        Apply T to item: Result = T * Item (Convolution)
        Wait. If T = Target * Source^-1, then T * SourceItem = Target * Source^-1 * SourceItem.
        If SourceItem is bound to a Role in Source, say Source = Role * SourceItem + ...
        Then Source^-1 * SourceItem is roughly Role^-1? No.
        
        Let's trace the algebra.
        Source = R * A
        Target = R * B
        Mapping T = (R * B) * (R * A)^-1 = R * B * R^-1 * A^-1 = B * A^-1 (approx, if R is unitary)
        
        Then T * A = (B * A^-1) * A = B.
        
        So yes, we apply mapping via Convolution.
        """
        return self._circ_conv(mapping, item)

class AnalogicalMappingExperiment:
    def __init__(self):
        self.mem = HolographicAnalogicalMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "mapping_accuracy": 0.0,
            "avg_valid_sim": 0.0,
            "avg_invalid_sim": 0.0
        }

    def run(self):
        print("Cycle 318: Analogical Mapping Experiment")
        print("----------------------------------------")
        
        correct_count = 0
        total_valid_sim = 0.0
        total_invalid_sim = 0.0
        total_checks = 0
        
        for i in range(self.num_trials):
            # 1. Define Roles
            Agent = self.mem.generate_vector()
            Action = self.mem.generate_vector()
            Object = self.mem.generate_vector()
            
            # 2. Define Source Domain (John loves Mary)
            John = self.mem.generate_vector()
            Loves = self.mem.generate_vector()
            Mary = self.mem.generate_vector()
            
            S_A = self.mem.create_structure([
                (Agent, John), (Action, Loves), (Object, Mary)
            ])
            
            # 3. Define Target Domain (Romeo loves Juliet)
            Romeo = self.mem.generate_vector()
            # Loves is reused
            Juliet = self.mem.generate_vector()
            
            S_B = self.mem.create_structure([
                (Agent, Romeo), (Action, Loves), (Object, Juliet)
            ])
            
            # 4. Compute Mapping T = S_B * S_A^-1
            T = self.mem.compute_mapping(S_A, S_B)
            
            # 5. Test Analogical Inference
            
            # Query: "Who is the John of the target?"
            # Prediction = T * John
            pred_romeo = self.mem.apply_mapping(T, John)
            sim_romeo = np.dot(self.mem._normalize(pred_romeo), Romeo)
            sim_juliet = np.dot(self.mem._normalize(pred_romeo), Juliet) # Wrong mapping
            
            total_valid_sim += sim_romeo
            total_invalid_sim += sim_juliet
            total_checks += 1
            
            if sim_romeo > 0.20 and sim_juliet < 0.2: # Threshold might need tuning
                correct_count += 1
                
            # Query: "Who is the Mary of the target?"
            # Prediction = T * Mary
            pred_juliet = self.mem.apply_mapping(T, Mary)
            sim_juliet_2 = np.dot(self.mem._normalize(pred_juliet), Juliet)
            sim_romeo_2 = np.dot(self.mem._normalize(pred_juliet), Romeo)
            
            total_valid_sim += sim_juliet_2
            total_invalid_sim += sim_romeo_2
            total_checks += 1
            
            if sim_juliet_2 > 0.20 and sim_romeo_2 < 0.2:
                correct_count += 1
                
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Source: John loves Mary")
                print(f"  Target: Romeo loves Juliet")
                print(f"  Mapping T = Target * Source^-1")
                print(f"  Query(John) -> Sim(Romeo): {sim_romeo:.4f} (Expected > 0.20)")
                print(f"  Query(John) -> Sim(Juliet): {sim_juliet:.4f} (Expected < 0.2)")

        accuracy = correct_count / total_checks
        avg_valid = total_valid_sim / total_checks
        avg_invalid = total_invalid_sim / total_checks
        
        self.results["mapping_accuracy"] = accuracy
        self.results["avg_valid_sim"] = avg_valid
        self.results["avg_invalid_sim"] = avg_invalid
        
        print("\nResults Summary:")
        print(f"Mapping Accuracy: {accuracy*100:.1f}%")
        print(f"Avg Valid Sim:    {avg_valid:.4f}")
        print(f"Avg Invalid Sim:  {avg_invalid:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = AnalogicalMappingExperiment()
    exp.run()
