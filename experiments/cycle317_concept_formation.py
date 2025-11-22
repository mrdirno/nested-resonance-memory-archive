import numpy as np
import sys
import os

class HolographicConceptMemory:
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
        """Unbinding"""
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

    def query_role(self, structure, role):
        """Structure * Role^-1"""
        return self._circ_corr(structure, role)

class ConceptFormationExperiment:
    def __init__(self):
        self.mem = HolographicConceptMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "common_feature_sim": 0.0,
            "variable_feature_sim": 0.0,
            "classification_accuracy": 0.0
        }

    def run(self):
        print("Cycle 317: Concept Formation Experiment")
        print("---------------------------------------")
        
        total_common_sim = 0.0
        total_variable_sim = 0.0
        correct_classifications = 0
        
        for i in range(self.num_trials):
            # 1. Define Roles
            Type = self.mem.generate_vector()
            Shape = self.mem.generate_vector()
            Color = self.mem.generate_vector()
            
            # 2. Define Fillers
            Fruit = self.mem.generate_vector() # Common
            
            Round = self.mem.generate_vector()
            Long = self.mem.generate_vector()
            
            Red = self.mem.generate_vector()
            Yellow = self.mem.generate_vector()
            Orange = self.mem.generate_vector()
            
            # 3. Create Instances
            # Apple: Fruit, Round, Red
            Apple = self.mem.create_structure([
                (Type, Fruit), (Shape, Round), (Color, Red)
            ])
            
            # Banana: Fruit, Long, Yellow
            Banana = self.mem.create_structure([
                (Type, Fruit), (Shape, Long), (Color, Yellow)
            ])
            
            # Orange: Fruit, Round, Orange
            OrangeFruit = self.mem.create_structure([
                (Type, Fruit), (Shape, Round), (Color, Orange)
            ])
            
            # 4. Form Prototype (Superposition)
            # We normalize the sum to keep it comparable
            Prototype = self.mem._normalize(Apple + Banana + OrangeFruit)
            
            # 5. Test Generalization (Common Feature)
            # Query Prototype for Type -> Expect Fruit
            retrieved_type = self.mem.query_role(Prototype, Type)
            sim_fruit = np.dot(self.mem._normalize(retrieved_type), Fruit)
            total_common_sim += sim_fruit
            
            # 6. Test Specificity Loss (Variable Feature)
            # Query Prototype for Color -> Expect Mix
            retrieved_color = self.mem.query_role(Prototype, Color)
            sim_red = np.dot(self.mem._normalize(retrieved_color), Red)
            sim_yellow = np.dot(self.mem._normalize(retrieved_color), Yellow)
            sim_orange = np.dot(self.mem._normalize(retrieved_color), Orange)
            
            # Average similarity to any specific color should be lower than to Fruit
            avg_color_sim = (sim_red + sim_yellow + sim_orange) / 3.0
            total_variable_sim += avg_color_sim
            
            # 7. Classification Test
            # Is Apple closer to Prototype than a random vector?
            # Or better: Is Apple closer to Fruit Prototype than to a Vegetable Prototype?
            # Let's just check if Apple has positive dot product with Prototype.
            sim_class = np.dot(self.mem._normalize(Apple), Prototype)
            if sim_class > 0.1: # Arbitrary positive threshold
                correct_classifications += 1
                
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Common Feature (Type=Fruit) Sim: {sim_fruit:.4f} (Expected High)")
                print(f"  Variable Feature (Color) Avg Sim: {avg_color_sim:.4f} (Expected Low)")
                print(f"  Classification Sim (Apple vs Proto): {sim_class:.4f}")

        avg_common = total_common_sim / self.num_trials
        avg_variable = total_variable_sim / self.num_trials
        accuracy = correct_classifications / self.num_trials
        
        self.results["common_feature_sim"] = avg_common
        self.results["variable_feature_sim"] = avg_variable
        self.results["classification_accuracy"] = accuracy
        
        print("\nResults Summary:")
        print(f"Avg Common Feature Sim:   {avg_common:.4f}")
        print(f"Avg Variable Feature Sim: {avg_variable:.4f}")
        print(f"Classification Accuracy:  {accuracy*100:.1f}%")
        
        # Success Criteria: Common > Variable
        if avg_common > avg_variable * 1.5:
            print("SUCCESS: Prototype successfully extracted common features.")
        else:
            print("FAILURE: Prototype failed to distinguish common from variable.")
            
        return self.results

if __name__ == "__main__":
    exp = ConceptFormationExperiment()
    exp.run()
