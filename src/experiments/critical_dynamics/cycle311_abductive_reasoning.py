import numpy as np
import sys
import os

class HolographicAbductiveMemory:
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

    def abduce_cause(self, rule, consequent):
        """
        Hypothesis = Rule * Consequent^-1
        If Rule = A * C, then Hypothesis approx A.
        """
        return self._circ_corr(rule, consequent)

class AbductiveReasoningExperiment:
    def __init__(self):
        self.mem = HolographicAbductiveMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "abduction_accuracy": 0.0,
            "avg_valid_sim": 0.0,
            "avg_invalid_sim": 0.0
        }

    def run(self):
        print("Cycle 311: Abductive Reasoning Experiment")
        print("-----------------------------------------")
        
        correct_count = 0
        total_valid_sim = 0.0
        total_invalid_sim = 0.0
        
        for i in range(self.num_trials):
            # 1. Define Concepts
            Rain = self.mem.generate_vector()
            Wet = self.mem.generate_vector()
            
            Fire = self.mem.generate_vector()
            Smoke = self.mem.generate_vector()
            
            RandomFact = self.mem.generate_vector()
            
            # 2. Encode Rules
            # Rule 1: Rain -> Wet
            Rule_RW = self.mem.encode_rule(Rain, Wet)
            
            # Rule 2: Fire -> Smoke
            Rule_FS = self.mem.encode_rule(Fire, Smoke)
            
            # 3. Test Abduction
            
            # Test 1: Valid Abduction (Given Wet, infer Rain)
            # Hypothesis = Rule_RW * Wet^-1 -> Expect Rain
            Hyp_Rain = self.mem.abduce_cause(Rule_RW, Wet)
            sim_rain = np.dot(self.mem._normalize(Hyp_Rain), self.mem._normalize(Rain))
            total_valid_sim += sim_rain
            
            # Test 2: Cross-Talk (Given Wet, apply to Fire Rule)
            # Hypothesis = Rule_FS * Wet^-1 -> Expect Noise
            Hyp_Noise1 = self.mem.abduce_cause(Rule_FS, Wet)
            sim_noise1 = np.dot(self.mem._normalize(Hyp_Noise1), self.mem._normalize(Fire))
            total_invalid_sim += sim_noise1
            
            # Test 3: Invalid Fact (Given Random, apply to Rain Rule)
            # Hypothesis = Rule_RW * Random^-1 -> Expect Noise
            Hyp_Noise2 = self.mem.abduce_cause(Rule_RW, RandomFact)
            sim_noise2 = np.dot(self.mem._normalize(Hyp_Noise2), self.mem._normalize(Rain))
            total_invalid_sim += sim_noise2
            
            # Success Condition: High Valid Sim, Low Invalid Sim
            # Threshold 0.5 based on previous cycle experience
            if sim_rain > 0.5 and abs(sim_noise1) < 0.2 and abs(sim_noise2) < 0.2:
                correct_count += 1
            
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Rule: Rain -> Wet")
                print(f"  Fact: Wet")
                print(f"  Abduced Cause Sim to Rain: {sim_rain:.4f} (Expected > 0.5)")
                print(f"  Invalid (Wet on Fire Rule): {sim_noise1:.4f} (Expected < 0.2)")
                print(f"  Invalid (Random on Rain Rule): {sim_noise2:.4f} (Expected < 0.2)")

        self.results["abduction_accuracy"] = correct_count / self.num_trials
        self.results["avg_valid_sim"] = total_valid_sim / self.num_trials
        self.results["avg_invalid_sim"] = total_invalid_sim / (self.num_trials * 2)
        
        print("\nResults Summary:")
        print(f"Abduction Accuracy: {self.results['abduction_accuracy']*100:.1f}%")
        print(f"Avg Valid Sim:      {self.results['avg_valid_sim']:.4f}")
        print(f"Avg Invalid Sim:    {self.results['avg_invalid_sim']:.4f}")
        
        return self.results

if __name__ == "__main__":
    exp = AbductiveReasoningExperiment()
    results = exp.run()
