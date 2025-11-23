import numpy as np
import sys
import os

class HolographicDeductiveMemory:
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
    
    def encode_rule(self, antecedent, consequent):
        """
        Rule = Antecedent * Consequent
        """
        return self._circ_conv(antecedent, consequent)

    def apply_rule(self, rule, fact):
        """
        Result = Rule * Fact^-1
        If Fact == Antecedent, Result approx Consequent.
        """
        return self._circ_corr(rule, fact)

class DeductiveReasoningExperiment:
    def __init__(self):
        self.mem = HolographicDeductiveMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "deduction_accuracy": 0.0,
            "avg_valid_sim": 0.0,
            "avg_invalid_sim": 0.0
        }

    def run(self):
        print("Cycle 310: Deductive Reasoning Experiment")
        print("-----------------------------------------")
        
        correct_count = 0
        total_valid_sim = 0.0
        total_invalid_sim = 0.0
        
        for i in range(self.num_trials):
            # 1. Define Concepts
            Rain = self.mem.generate_vector()
            Wet = self.mem.generate_vector()
            
            Fire = self.mem.generate_vector()
            Hot = self.mem.generate_vector()
            
            Snow = self.mem.generate_vector() # Unrelated fact
            
            # 2. Encode Rules
            # Rule 1: Rain -> Wet
            Rule_RW = self.mem.encode_rule(Rain, Wet)
            
            # Rule 2: Fire -> Hot
            Rule_FH = self.mem.encode_rule(Fire, Hot)
            
            # 3. Test Deductions
            
            # Test 1: Valid (Rain -> ?)
            # Prediction = Rule_RW * Rain^-1 -> Expect Wet
            Pred_Wet = self.mem.apply_rule(Rule_RW, Rain)
            sim_wet = np.dot(self.mem._normalize(Pred_Wet), self.mem._normalize(Wet))
            total_valid_sim += sim_wet
            
            # Test 2: Invalid Application (Rain applied to Fire Rule)
            # Prediction = Rule_FH * Rain^-1 -> Expect Noise
            Pred_Noise1 = self.mem.apply_rule(Rule_FH, Rain)
            sim_noise1 = np.dot(self.mem._normalize(Pred_Noise1), self.mem._normalize(Hot))
            total_invalid_sim += sim_noise1
            
            # Test 3: Invalid Fact (Snow applied to Rain Rule)
            # Prediction = Rule_RW * Snow^-1 -> Expect Noise
            Pred_Noise2 = self.mem.apply_rule(Rule_RW, Snow)
            sim_noise2 = np.dot(self.mem._normalize(Pred_Noise2), self.mem._normalize(Wet))
            total_invalid_sim += sim_noise2
            
            # Success Condition: High Valid Sim, Low Invalid Sim
            # Lowered threshold to 0.5 to account for HRR noise (approx 0.7 expected)
            if sim_wet > 0.5 and abs(sim_noise1) < 0.2 and abs(sim_noise2) < 0.2:
                correct_count += 1
            
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Rule: Rain -> Wet")
                print(f"  Fact: Rain")
                print(f"  Deduction Sim to Wet: {sim_wet:.4f} (Expected > 0.5)")
                print(f"  Invalid (Rain on Fire Rule): {sim_noise1:.4f} (Expected < 0.2)")
                print(f"  Invalid (Snow on Rain Rule): {sim_noise2:.4f} (Expected < 0.2)")

        self.results["deduction_accuracy"] = correct_count / self.num_trials
        self.results["avg_valid_sim"] = total_valid_sim / self.num_trials
        self.results["avg_invalid_sim"] = total_invalid_sim / (self.num_trials * 2) # Two invalid tests per trial
        
        print("\nResults Summary:")
        print(f"Deduction Accuracy: {self.results['deduction_accuracy']*100:.1f}%")
        print(f"Avg Valid Sim:      {self.results['avg_valid_sim']:.4f}")
        print(f"Avg Invalid Sim:    {self.results['avg_invalid_sim']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = DeductiveReasoningExperiment()
    results = exp.run()
