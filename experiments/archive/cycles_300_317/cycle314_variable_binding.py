import numpy as np
import sys
import os

class HolographicRoleMemory:
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

class VariableBindingExperiment:
    def __init__(self):
        self.mem = HolographicRoleMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "retrieval_accuracy": 0.0,
            "avg_valid_sim": 0.0,
            "avg_invalid_sim": 0.0
        }

    def run(self):
        print("Cycle 314: Variable Binding Experiment")
        print("--------------------------------------")
        
        correct_count = 0
        total_valid_sim = 0.0
        total_invalid_sim = 0.0
        total_checks = 0
        
        for i in range(self.num_trials):
            # 1. Define Roles
            Agent = self.mem.generate_vector()
            Action = self.mem.generate_vector()
            Object = self.mem.generate_vector()
            
            # 2. Define Fillers (Scenario 1: Dog chases Ball)
            Dog = self.mem.generate_vector()
            Chases = self.mem.generate_vector()
            Ball = self.mem.generate_vector()
            
            # 3. Define Fillers (Scenario 2: Cat eats Fish)
            Cat = self.mem.generate_vector()
            Eats = self.mem.generate_vector()
            Fish = self.mem.generate_vector()
            
            # 4. Create Structure 1
            S1 = self.mem.create_structure([
                (Agent, Dog),
                (Action, Chases),
                (Object, Ball)
            ])
            
            # 5. Create Structure 2
            S2 = self.mem.create_structure([
                (Agent, Cat),
                (Action, Eats),
                (Object, Fish)
            ])
            
            # 6. Test Retrieval from S1
            
            # Query Agent -> Expect Dog
            retrieved_agent = self.mem.query_role(S1, Agent)
            sim_dog = np.dot(self.mem._normalize(retrieved_agent), Dog)
            sim_cat = np.dot(self.mem._normalize(retrieved_agent), Cat) # Cross-talk check
            
            total_valid_sim += sim_dog
            total_invalid_sim += sim_cat
            total_checks += 1
            
            if sim_dog > 0.45 and sim_cat < 0.2:
                correct_count += 1
                
            # Query Object -> Expect Ball
            retrieved_object = self.mem.query_role(S1, Object)
            sim_ball = np.dot(self.mem._normalize(retrieved_object), Ball)
            sim_fish = np.dot(self.mem._normalize(retrieved_object), Fish)
            
            total_valid_sim += sim_ball
            total_invalid_sim += sim_fish
            total_checks += 1
            
            if sim_ball > 0.45 and sim_fish < 0.2:
                correct_count += 1
                
            # 7. Test Retrieval from S2
            
            # Query Agent -> Expect Cat
            retrieved_agent2 = self.mem.query_role(S2, Agent)
            sim_cat2 = np.dot(self.mem._normalize(retrieved_agent2), Cat)
            sim_dog2 = np.dot(self.mem._normalize(retrieved_agent2), Dog)
            
            total_valid_sim += sim_cat2
            total_invalid_sim += sim_dog2
            total_checks += 1
            
            if sim_cat2 > 0.45 and sim_dog2 < 0.2:
                correct_count += 1
                
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Structure 1: Agent=Dog, Action=Chases, Object=Ball")
                print(f"  Query S1(Agent) -> Sim(Dog): {sim_dog:.4f} (Expected > 0.45)")
                print(f"  Query S1(Agent) -> Sim(Cat): {sim_cat:.4f} (Expected < 0.2)")

        self.results["retrieval_accuracy"] = correct_count / total_checks
        self.results["avg_valid_sim"] = total_valid_sim / total_checks
        self.results["avg_invalid_sim"] = total_invalid_sim / total_checks
        
        print("\nResults Summary:")
        print(f"Retrieval Accuracy: {self.results['retrieval_accuracy']*100:.1f}%")
        print(f"Avg Valid Sim:      {self.results['avg_valid_sim']:.4f}")
        print(f"Avg Invalid Sim:    {self.results['avg_invalid_sim']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = VariableBindingExperiment()
    exp.run()
