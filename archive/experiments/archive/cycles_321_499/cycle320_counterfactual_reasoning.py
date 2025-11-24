import numpy as np
import sys
import os

class HolographicCounterfactualMemory:
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

    def store_rule(self, cause, effect):
        """
        Encode Rule: Cause * Effect.
        This binds the specific cause to the specific effect.
        """
        return self._circ_conv(cause, effect)

    def predict_outcome(self, kb, cause_state):
        """
        Predict Effect given Cause and KB.
        Pred = KB * Cause^-1.
        """
        return self._circ_corr(kb, cause_state)

class CounterfactualExperiment:
    def __init__(self):
        self.mem = HolographicCounterfactualMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "reality_check": 0.0,
            "counterfactual_accuracy": 0.0
        }

    def run(self):
        print("Cycle 320: Counterfactual Reasoning Experiment (Associative)")
        print("----------------------------------------------------------")
        
        correct_reality = 0
        correct_counterfactual = 0
        
        for i in range(self.num_trials):
            # 1. Define Concepts
            Rain = self.mem.generate_vector()
            NoRain = self.mem.generate_vector()
            
            Wet = self.mem.generate_vector()
            Dry = self.mem.generate_vector()
            
            # 2. Define Knowledge Base (Superposition of Rules)
            # Rule 1: Rain -> Wet
            Rule_Rain = self.mem.store_rule(Rain, Wet)
            
            # Rule 2: NoRain -> Dry
            Rule_NoRain = self.mem.store_rule(NoRain, Dry)
            
            KB = Rule_Rain + Rule_NoRain
            
            # 3. Reality: It Rained.
            # Query: Rain -> ?
            pred_reality = self.mem.predict_outcome(KB, Rain)
            sim_wet = np.dot(self.mem._normalize(pred_reality), Wet)
            sim_dry = np.dot(self.mem._normalize(pred_reality), Dry)
            
            # We expect Wet > Dry
            if sim_wet > 0.4 and sim_dry < 0.2:
                correct_reality += 1
            
            # 4. Counterfactual: "What if NoRain?"
            # Query: NoRain -> ?
            pred_counterfactual = self.mem.predict_outcome(KB, NoRain)
            sim_cf_dry = np.dot(self.mem._normalize(pred_counterfactual), Dry)
            sim_cf_wet = np.dot(self.mem._normalize(pred_counterfactual), Wet)
            
            # We expect Dry > Wet
            if sim_cf_dry > 0.4 and sim_cf_wet < 0.2:
                correct_counterfactual += 1
                
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Reality (Rain) -> Wet Sim: {sim_wet:.4f}")
                print(f"  Reality (Rain) -> Dry Sim: {sim_dry:.4f}")
                print(f"  Counterfactual (NoRain) -> Dry Sim: {sim_cf_dry:.4f}")
                print(f"  Counterfactual (NoRain) -> Wet Sim: {sim_cf_wet:.4f}")

        acc_reality = correct_reality / self.num_trials
        acc_cf = correct_counterfactual / self.num_trials
        
        self.results["reality_check"] = acc_reality
        self.results["counterfactual_accuracy"] = acc_cf
        
        print("\nResults Summary:")
        print(f"Reality Accuracy:       {acc_reality*100:.1f}%")
        print(f"Counterfactual Accuracy:{acc_cf*100:.1f}%")
        
        if acc_reality > 0.9 and acc_cf > 0.9:
            print("SUCCESS: System correctly simulates alternative reality.")
        else:
            print("FAILURE: Simulation failed.")
            
        return self.results

if __name__ == "__main__":
    exp = CounterfactualExperiment()
    exp.run()
