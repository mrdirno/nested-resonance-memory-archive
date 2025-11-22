import numpy as np
import sys
import os

class HolographicCausalMemory:
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

    def _permute(self, v):
        """Permutation (Forward Operator)"""
        return np.roll(v, 1)

    def _inv_permute(self, v):
        """Inverse Permutation (Backward Operator)"""
        return np.roll(v, -1)

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    # --- Encoding ---
    def store_causal(self, cause, effect):
        """
        Encode A -> B as (Cause * A) + (Effect * B).
        This explicitly labels the roles.
        """
        # Generate Roles (Fixed for the system)
        if not hasattr(self, 'CauseRole'):
            self.CauseRole = self.generate_vector()
            self.EffectRole = self.generate_vector()
            self.ItemRole = self.generate_vector() # For correlation
            
        trace = self._circ_conv(self.CauseRole, cause) + self._circ_conv(self.EffectRole, effect)
        return trace

    def store_correlation(self, item1, item2):
        """
        Encode A <-> B as (Item * A) + (Item * B).
        Symmetric roles.
        """
        if not hasattr(self, 'ItemRole'):
            self.ItemRole = self.generate_vector()
            
        trace = self._circ_conv(self.ItemRole, item1) + self._circ_conv(self.ItemRole, item2)
        return trace

    # --- Inference ---
    def identify_role(self, trace, item):
        """
        Determine the role of an item in the trace.
        Role = Trace * Item^-1
        """
        return self._circ_corr(trace, item)

    def retrieve_partner(self, trace, item, role_vector):
        """
        Given an item and its role, retrieve the partner.
        Partner = (Trace - Role*Item) * PartnerRole^-1?
        Or just: Partner = Trace * PartnerRole^-1
        """
        # Simple retrieval by role
        return self._circ_corr(trace, role_vector)

class CausalInferenceExperiment:
    def __init__(self):
        self.mem = HolographicCausalMemory(dimension=2048)
        self.num_trials = 50
        self.results = {
            "causal_asymmetry_score": 0.0,
            "corr_symmetry_score": 0.0
        }

    def run(self):
        print("Cycle 319: Causal Inference Experiment (Role-Based)")
        print("---------------------------------------------------")
        
        # Initialize Roles
        self.mem.store_causal(self.mem.generate_vector(), self.mem.generate_vector())
        CauseRole = self.mem.CauseRole
        EffectRole = self.mem.EffectRole
        ItemRole = self.mem.ItemRole
        
        correct_causal = 0
        correct_corr = 0
        
        for i in range(self.num_trials):
            # 1. Define Concepts
            Fire = self.mem.generate_vector()
            Smoke = self.mem.generate_vector()
            
            Thunder = self.mem.generate_vector()
            Lightning = self.mem.generate_vector()
            
            # 2. Encode Relationships
            Trace_Causal = self.mem.store_causal(Fire, Smoke)
            Trace_Corr = self.mem.store_correlation(Thunder, Lightning)
            
            # 3. Test Causal Asymmetry (Role Identification)
            # Identify Role of Fire
            role_fire = self.mem.identify_role(Trace_Causal, Fire)
            sim_cause = np.dot(self.mem._normalize(role_fire), CauseRole)
            sim_effect = np.dot(self.mem._normalize(role_fire), EffectRole)
            
            is_cause = (sim_cause > 0.4 and sim_effect < 0.2)
            
            # Identify Role of Smoke
            role_smoke = self.mem.identify_role(Trace_Causal, Smoke)
            sim_cause_s = np.dot(self.mem._normalize(role_smoke), CauseRole)
            sim_effect_s = np.dot(self.mem._normalize(role_smoke), EffectRole)
            
            is_effect = (sim_effect_s > 0.4 and sim_cause_s < 0.2)
            
            if is_cause and is_effect:
                correct_causal += 1
                
            # 4. Test Correlational Symmetry
            # Identify Role of Thunder
            role_thunder = self.mem.identify_role(Trace_Corr, Thunder)
            sim_item_t = np.dot(self.mem._normalize(role_thunder), ItemRole)
            
            # Identify Role of Lightning
            role_lightning = self.mem.identify_role(Trace_Corr, Lightning)
            sim_item_l = np.dot(self.mem._normalize(role_lightning), ItemRole)
            
            if sim_item_t > 0.4 and sim_item_l > 0.4:
                correct_corr += 1
                
            if i == 0:
                print("Trial 1 Details:")
                print(f"  Fire Role Sim (Cause): {sim_cause:.4f}")
                print(f"  Smoke Role Sim (Effect): {sim_effect_s:.4f}")
                print(f"  Thunder Role Sim (Item): {sim_item_t:.4f}")
                print(f"  Lightning Role Sim (Item): {sim_item_l:.4f}")

        acc_causal = correct_causal / self.num_trials
        acc_corr = correct_corr / self.num_trials
        
        self.results["causal_asymmetry_score"] = acc_causal
        self.results["corr_symmetry_score"] = acc_corr
        
        print("\nResults Summary:")
        print(f"Causal Asymmetry Accuracy: {acc_causal*100:.1f}%")
        print(f"Corr Symmetry Accuracy:    {acc_corr*100:.1f}%")
        
        if acc_causal > 0.9 and acc_corr > 0.9:
            print("SUCCESS: System distinguishes Cause/Effect roles from symmetric Item roles.")
        else:
            print("FAILURE: Distinction failed.")
            
        return self.results

if __name__ == "__main__":
    exp = CausalInferenceExperiment()
    exp.run()
