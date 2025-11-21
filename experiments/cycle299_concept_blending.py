import numpy as np
import sys
import os

class HolographicBlendingMemory:
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
    
    def store_pair(self, key, value):
        """Store K -> V as K * V"""
        term = self._circ_conv(key, value)
        self.memory_trace += term
        
    def retrieve(self, key, possible_values=None):
        """Retrieve V given K"""
        noisy_val = self._circ_corr(self.memory_trace, key)
        
        if possible_values is None:
            return noisy_val
            
        # Cleanup
        best_match = None
        max_sim = -1.0
        
        for val_vec in possible_values:
            sim = np.dot(self._normalize(noisy_val), self._normalize(val_vec))
            if sim > max_sim:
                max_sim = sim
                best_match = val_vec
                
        return best_match

    def blend_concepts(self, c1, c2):
        """
        Create a blended concept vector C = C1 + C2.
        """
        return self._normalize(c1 + c2)

class BlendingExperiment:
    def __init__(self):
        self.mem = HolographicBlendingMemory(dimension=2048)
        self.num_trials = 100
        self.results = {
            "property_A_retrieval": 0.0,
            "property_B_retrieval": 0.0,
            "cross_talk_rejection": 0.0 # Ability to reject random properties
        }

    def run(self):
        print("Cycle 299: Concept Blending Experiment")
        print("--------------------------------------")
        
        hits_A = 0
        hits_B = 0
        rejections = 0
        
        for _ in range(self.num_trials):
            # 1. Generate Concepts and Properties
            A = self.mem.generate_vector() # e.g., "Red"
            P_A = self.mem.generate_vector() # e.g., "Color Property"
            
            B = self.mem.generate_vector() # e.g., "Truck"
            P_B = self.mem.generate_vector() # e.g., "Vehicle Property"
            
            C_random = self.mem.generate_vector() # Distractor Concept
            P_random = self.mem.generate_vector() # Distractor Property
            
            # Reset memory
            self.mem.memory_trace = np.zeros(self.mem.d)
            
            # 2. Store Associations: A->P_A, B->P_B
            self.mem.store_pair(A, P_A)
            self.mem.store_pair(B, P_B)
            
            # 3. Create Blended Query: Q = A + B
            # Note: We don't normalize for the query usually in HRR, 
            # but let's try simple sum.
            Q = A + B
            
            # 4. Retrieve using Blended Query
            # Expected Result: P_A + P_B + Noise
            retrieved_vec = self.mem.retrieve(Q)
            
            # 5. Verify Presence of Properties
            # We check if the retrieved vector is closer to P_A than random, 
            # and closer to P_B than random.
            
            # Check P_A
            sim_A = np.dot(self.mem._normalize(retrieved_vec), self.mem._normalize(P_A))
            sim_rand = np.dot(self.mem._normalize(retrieved_vec), self.mem._normalize(P_random))
            
            if sim_A > sim_rand:
                hits_A += 1
                
            # Check P_B
            sim_B = np.dot(self.mem._normalize(retrieved_vec), self.mem._normalize(P_B))
            
            if sim_B > sim_rand:
                hits_B += 1
                
            # Check Rejection (sim_rand should be low, but we already compared it)
            # Let's define rejection as: Is the top match in [P_A, P_B, P_random] either P_A or P_B?
            # If it picks P_random, that's a failure.
            
            best_match = None
            max_sim = -1.0
            for val in [P_A, P_B, P_random]:
                sim = np.dot(self.mem._normalize(retrieved_vec), self.mem._normalize(val))
                if sim > max_sim:
                    max_sim = sim
                    best_match = val
            
            if best_match is not P_random:
                rejections += 1
                
        self.results["property_A_retrieval"] = hits_A / self.num_trials
        self.results["property_B_retrieval"] = hits_B / self.num_trials
        self.results["cross_talk_rejection"] = rejections / self.num_trials
        
        print(f"Property A Retrieval: {self.results['property_A_retrieval']*100:.1f}%")
        print(f"Property B Retrieval: {self.results['property_B_retrieval']*100:.1f}%")
        print(f"Noise Rejection: {self.results['cross_talk_rejection']*100:.1f}%")
        
        return self.results

if __name__ == "__main__":
    exp = BlendingExperiment()
    results = exp.run()
