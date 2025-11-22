import numpy as np
import sys
import os

class HolographicClassificationMemory:
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
    
    def create_instance(self, class_vec, isa_vec, specific_vec):
        """
        Instance = Class * IsA + Specifics
        """
        base = self._circ_conv(class_vec, isa_vec)
        instance = base + specific_vec
        return self._normalize(instance)

    def check_membership(self, instance, class_vec, isa_vec):
        """
        Check: Instance * Class^-1 approx IsA?
        Returns similarity to IsA vector.
        """
        # Unbind Class from Instance
        query = self._circ_corr(instance, class_vec)
        # Check similarity to IsA token
        sim = np.dot(self._normalize(query), self._normalize(isa_vec))
        return sim

class HierarchicalClassificationExperiment:
    def __init__(self):
        self.mem = HolographicClassificationMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "classification_accuracy": 0.0,
            "avg_true_positive_sim": 0.0,
            "avg_true_negative_sim": 0.0
        }

    def run(self):
        print("Cycle 309: Hierarchical Classification Experiment")
        print("-------------------------------------------------")
        
        correct_count = 0
        total_tp_sim = 0.0
        total_tn_sim = 0.0
        
        for i in range(self.num_trials):
            # 1. Define Ontology
            IsA = self.mem.generate_vector()
            
            Class_Animal = self.mem.generate_vector()
            Class_Plant = self.mem.generate_vector()
            
            Specific_Bark = self.mem.generate_vector()
            Specific_Leaf = self.mem.generate_vector()
            
            # 2. Create Instances
            # Dog = Animal * IsA + Bark
            Dog = self.mem.create_instance(Class_Animal, IsA, Specific_Bark)
            
            # Tree = Plant * IsA + Leaf
            Tree = self.mem.create_instance(Class_Plant, IsA, Specific_Leaf)
            
            # 3. Test Membership
            
            # Test 1: Is Dog an Animal? (True Positive)
            sim_dog_animal = self.mem.check_membership(Dog, Class_Animal, IsA)
            total_tp_sim += sim_dog_animal
            
            # Test 2: Is Dog a Plant? (True Negative)
            sim_dog_plant = self.mem.check_membership(Dog, Class_Plant, IsA)
            total_tn_sim += sim_dog_plant
            
            # Success Condition: High TP, Low TN
            if sim_dog_animal > 0.4 and sim_dog_plant < 0.2:
                correct_count += 1
            
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Instance: Dog (Animal * IsA + Bark)")
                print(f"  Query: Is Dog an Animal?")
                print(f"  Result (Sim to IsA): {sim_dog_animal:.4f} (Expected > 0.4)")
                print(f"  Query: Is Dog a Plant?")
                print(f"  Result (Sim to IsA): {sim_dog_plant:.4f} (Expected < 0.2)")

        self.results["classification_accuracy"] = correct_count / self.num_trials
        self.results["avg_true_positive_sim"] = total_tp_sim / self.num_trials
        self.results["avg_true_negative_sim"] = total_tn_sim / self.num_trials
        
        print("\nResults Summary:")
        print(f"Classification Accuracy: {self.results['classification_accuracy']*100:.1f}%")
        print(f"Avg True Positive Sim:   {self.results['avg_true_positive_sim']:.4f}")
        print(f"Avg True Negative Sim:   {self.results['avg_true_negative_sim']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = HierarchicalClassificationExperiment()
    results = exp.run()
