import numpy as np
import sys
import os

class HolographicContextMemory:
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
    
    def store_contextual_fact(self, concept, context, meaning):
        """
        Store: Concept * Context * Meaning
        """
        # Bind Concept * Context
        query_key = self._circ_conv(concept, context)
        # Bind with Meaning
        fact = self._circ_conv(query_key, meaning)
        self.memory_trace += fact
        
    def retrieve_meaning(self, concept, context, possible_meanings=None):
        """
        Retrieve: Memory # (Concept * Context)
        """
        query_key = self._circ_conv(concept, context)
        retrieved_noisy = self._circ_corr(self.memory_trace, query_key)
        
        if possible_meanings is None:
            return retrieved_noisy, 0.0
            
        # Cleanup
        best_match = None
        max_sim = -1.0
        ret_norm = self._normalize(retrieved_noisy)
        
        for m in possible_meanings:
            sim = np.dot(ret_norm, self._normalize(m))
            if sim > max_sim:
                max_sim = sim
                best_match = m
                
        return best_match, max_sim

class ContextualDisambiguationExperiment:
    def __init__(self):
        self.mem = HolographicContextMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "disambiguation_accuracy": 0.0,
            "avg_confidence": 0.0
        }

    def run(self):
        print("Cycle 305: Contextual Disambiguation Experiment")
        print("-----------------------------------------------")
        
        correct_retrievals = 0
        total_confidence = 0.0
        total_tests = 0
        
        for i in range(self.num_trials):
            # 1. Define Vectors
            Concept_Bank = self.mem.generate_vector()
            
            Context_River = self.mem.generate_vector()
            Meaning_Water = self.mem.generate_vector()
            
            Context_Finance = self.mem.generate_vector()
            Meaning_Money = self.mem.generate_vector()
            
            # Distractors
            Meaning_Food = self.mem.generate_vector()
            possible_meanings = [Meaning_Water, Meaning_Money, Meaning_Food]
            
            # 2. Store Facts (Ambiguous Concept)
            self.mem.memory_trace = np.zeros(self.mem.d)
            # Bank + River -> Water
            self.mem.store_contextual_fact(Concept_Bank, Context_River, Meaning_Water)
            # Bank + Finance -> Money
            self.mem.store_contextual_fact(Concept_Bank, Context_Finance, Meaning_Money)
            
            # 3. Test Retrieval
            
            # Test 1: Query with River Context
            res_water, conf_water = self.mem.retrieve_meaning(Concept_Bank, Context_River, possible_meanings)
            if res_water is Meaning_Water: correct_retrievals += 1
            total_confidence += conf_water
            total_tests += 1
            
            # Test 2: Query with Finance Context
            res_money, conf_money = self.mem.retrieve_meaning(Concept_Bank, Context_Finance, possible_meanings)
            if res_money is Meaning_Money: correct_retrievals += 1
            total_confidence += conf_money
            total_tests += 1
            
            # Test 3 (Control): Query with Wrong Context (Food?) - Not implemented, just checking disambiguation
            
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Query: Bank + River   -> Expect: Water. Sim: {conf_water:.4f}")
                print(f"  Query: Bank + Finance -> Expect: Money. Sim: {conf_money:.4f}")
                
                # Check Cross-Talk
                # Query Bank + River, check sim with Money
                query_river = self.mem._circ_conv(Concept_Bank, Context_River)
                ret_river = self.mem._circ_corr(self.mem.memory_trace, query_river)
                sim_money_leak = np.dot(self.mem._normalize(ret_river), self.mem._normalize(Meaning_Money))
                print(f"  Cross-Talk (River query -> Money): {sim_money_leak:.4f}")

        self.results["disambiguation_accuracy"] = correct_retrievals / total_tests
        self.results["avg_confidence"] = total_confidence / total_tests
        
        print("\nResults Summary:")
        print(f"Disambiguation Accuracy: {self.results['disambiguation_accuracy']*100:.1f}%")
        print(f"Avg Confidence: {self.results['avg_confidence']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = ContextualDisambiguationExperiment()
    results = exp.run()
