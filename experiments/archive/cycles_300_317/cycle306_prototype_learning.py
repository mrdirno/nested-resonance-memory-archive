import numpy as np
import sys
import os

class HolographicSchemaMemory:
    def __init__(self, dimension=2048):
        self.d = dimension
        self.memory_trace = np.zeros(self.d)
        
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0: return v
        return v / norm

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return v 
    
    def generate_exemplar(self, prototype, noise_level=0.5):
        """
        Generate Exemplar = (1-noise)*Prototype + noise*Random
        """
        noise_vec = self.generate_vector()
        exemplar = (1.0 - noise_level) * prototype + noise_level * noise_vec
        return self._normalize(exemplar)

    def induce_schema(self, exemplars):
        """
        Schema = Sum(Exemplars)
        """
        schema = np.zeros(self.d)
        for ex in exemplars:
            schema += ex
        return self._normalize(schema)

class PrototypeLearningExperiment:
    def __init__(self):
        self.mem = HolographicSchemaMemory(dimension=2048)
        self.num_trials = 50
        self.num_exemplars = 20
        self.noise_level = 0.8 # High noise!
        self.results = {
            "avg_exemplar_sim": 0.0,
            "avg_schema_sim": 0.0,
            "snr_gain": 0.0
        }

    def run(self):
        print("Cycle 306: Prototype Learning (Schema Induction) Experiment")
        print("-----------------------------------------------------------")
        
        total_exemplar_sim = 0.0
        total_schema_sim = 0.0
        
        for i in range(self.num_trials):
            # 1. Define Prototype
            Prototype = self.mem.generate_vector()
            
            # 2. Generate Noisy Exemplars
            exemplars = []
            trial_ex_sim = 0.0
            for _ in range(self.num_exemplars):
                ex = self.mem.generate_exemplar(Prototype, self.noise_level)
                exemplars.append(ex)
                trial_ex_sim += np.dot(ex, Prototype)
            
            avg_ex_sim = trial_ex_sim / self.num_exemplars
            total_exemplar_sim += avg_ex_sim
            
            # 3. Induce Schema (Superposition)
            Schema = self.mem.induce_schema(exemplars)
            
            # 4. Measure Schema Similarity to Prototype
            schema_sim = np.dot(Schema, Prototype)
            total_schema_sim += schema_sim
            
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Noise Level: {self.noise_level}")
                print(f"  Num Exemplars: {self.num_exemplars}")
                print(f"  Avg Exemplar Sim to Prototype: {avg_ex_sim:.4f}")
                print(f"  Schema Sim to Prototype:       {schema_sim:.4f}")
                print(f"  Gain: {schema_sim / avg_ex_sim:.2f}x")

        self.results["avg_exemplar_sim"] = total_exemplar_sim / self.num_trials
        self.results["avg_schema_sim"] = total_schema_sim / self.num_trials
        self.results["snr_gain"] = self.results["avg_schema_sim"] / self.results["avg_exemplar_sim"]
        
        print("\nResults Summary:")
        print(f"Avg Exemplar Similarity: {self.results['avg_exemplar_sim']:.4f}")
        print(f"Avg Schema Similarity:   {self.results['avg_schema_sim']:.4f}")
        print(f"SNR Gain:                {self.results['snr_gain']:.2f}x")
        
        # Theoretical Gain check: sqrt(N) approx?
        # Signal adds as N, Noise adds as sqrt(N). Ratio improves by sqrt(N).
        # But here we are averaging vectors, so Signal is constant, Noise reduces by sqrt(N).
        
        return self.results

if __name__ == "__main__":
    exp = PrototypeLearningExperiment()
    results = exp.run()
