import numpy as np
import sys
import os

class HolographicRecursiveMemory:
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
    
    def create_structure(self, bindings_list):
        """
        Structure = Sum(Role * Filler)
        bindings_list: list of tuples [(Role, Filler), ...]
        """
        structure = np.zeros(self.d)
        for role, filler in bindings_list:
            bound_pair = self._circ_conv(role, filler)
            structure += bound_pair
        return structure # Not normalized to preserve additive strength

    def query_role(self, structure, role):
        """
        Retrieve Filler = Structure * Role^-1
        """
        return self._circ_corr(structure, role)

class RecursiveStructureExperiment:
    def __init__(self):
        self.mem = HolographicRecursiveMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "deep_retrieval_accuracy": 0.0,
            "avg_valid_sim": 0.0,
            "avg_invalid_sim": 0.0
        }

    def run(self):
        print("Cycle 315: Recursive Structure Experiment")
        print("-----------------------------------------")
        
        correct_count = 0
        total_valid_sim = 0.0
        total_invalid_sim = 0.0
        
        for i in range(self.num_trials):
            # 1. Define Roles
            Agent = self.mem.generate_vector()
            Action = self.mem.generate_vector()
            Object = self.mem.generate_vector()
            
            # 2. Define Fillers for Leaf Structure (S1)
            Dog = self.mem.generate_vector()
            Chases = self.mem.generate_vector()
            Ball = self.mem.generate_vector()
            
            # 3. Create Leaf Structure S1: "Dog chases Ball"
            S1 = self.mem.create_structure([
                (Agent, Dog),
                (Action, Chases),
                (Object, Ball)
            ])
            S1_norm = self.mem._normalize(S1) # Normalize to use as a filler
            
            # 4. Define Fillers for Root Structure (S2)
            John = self.mem.generate_vector()
            Sees = self.mem.generate_vector()
            
            # 5. Create Root Structure S2: "John sees S1"
            S2 = self.mem.create_structure([
                (Agent, John),
                (Action, Sees),
                (Object, S1_norm)
            ])
            
            # 6. Test Deep Retrieval
            # Path: S2 -> Object -> S1 -> Agent -> Dog
            
            # Step 1: Retrieve S1 from S2
            retrieved_S1 = self.mem.query_role(S2, Object)
            
            # Step 2: Retrieve Agent from retrieved_S1
            # Note: retrieved_S1 is noisy. We use it directly.
            retrieved_deep_agent = self.mem.query_role(retrieved_S1, Agent)
            
            # Check similarity to Dog
            sim_dog = np.dot(self.mem._normalize(retrieved_deep_agent), Dog)
            
            # Check similarity to John (Control)
            sim_john = np.dot(self.mem._normalize(retrieved_deep_agent), John)
            
            total_valid_sim += sim_dog
            total_invalid_sim += sim_john
            
            # Threshold: Recursion adds significant noise.
            # Expected sim is roughly 1/sqrt(N) * 1/sqrt(M) if unnormalized?
            # Actually, binding preserves norm if unitary, but here we use Gaussian vectors.
            # Sim usually drops. Let's see what we get.
            if sim_dog > 0.20 and sim_john < 0.15:
                correct_count += 1
                
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Leaf S1: Dog chases Ball")
                print(f"  Root S2: John sees S1")
                print(f"  Deep Query S2(Object)(Agent) -> Sim(Dog): {sim_dog:.4f} (Expected > 0.20)")
                print(f"  Deep Query S2(Object)(Agent) -> Sim(John): {sim_john:.4f} (Expected < 0.15)")

        self.results["deep_retrieval_accuracy"] = correct_count / self.num_trials
        self.results["avg_valid_sim"] = total_valid_sim / self.num_trials
        self.results["avg_invalid_sim"] = total_invalid_sim / self.num_trials
        
        print("\nResults Summary:")
        print(f"Deep Retrieval Accuracy: {self.results['deep_retrieval_accuracy']*100:.1f}%")
        print(f"Avg Valid Sim:           {self.results['avg_valid_sim']:.4f}")
        print(f"Avg Invalid Sim:         {self.results['avg_invalid_sim']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = RecursiveStructureExperiment()
    exp.run()
