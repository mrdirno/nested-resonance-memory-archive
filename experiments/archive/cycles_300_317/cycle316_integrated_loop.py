import numpy as np
import sys
import os

class HolographicCognitiveAgent:
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
        """Permutation (for sequence)"""
        return np.roll(v, 1)

    def _inv_permute(self, v):
        """Inverse Permutation"""
        return np.roll(v, -1)

    def generate_vector(self):
        v = np.random.normal(0, 1.0/np.sqrt(self.d), self.d)
        return self._normalize(v)

    # --- Structural Capabilities ---
    def create_structure(self, bindings_list):
        """Sum(Role * Filler)"""
        structure = np.zeros(self.d)
        for role, filler in bindings_list:
            structure += self._circ_conv(role, filler)
        return structure

    def query_role(self, structure, role):
        """Structure * Role^-1"""
        return self._circ_corr(structure, role)

    # --- Logical Capabilities ---
    def encode_rule(self, antecedent, consequent):
        """Antecedent * Consequent"""
        return self._circ_conv(antecedent, consequent)

    def apply_rule(self, fact, rule):
        """Fact * Rule -> Consequent"""
        # Note: In Cycle 310 we used Fact * Rule. 
        # If Rule = A * B, and Fact = A, then A * (A * B) != B.
        # Wait, Cycle 310 used Correlation for application: Rule * Fact^-1?
        # Let's check Cycle 310. 
        # Cycle 310: Rule = P * Q. Deduction: Q = Rule * P^-1 (Correlation).
        return self._circ_corr(rule, fact)

    # --- Temporal Capabilities ---
    def encode_sequence(self, sequence_items):
        """Sum(Item_i * P(Item_i+1))"""
        trace = np.zeros(self.d)
        for i in range(len(sequence_items) - 1):
            pair = self._circ_conv(sequence_items[i], self._permute(sequence_items[i+1]))
            trace += pair
        return trace

    def step_sequence(self, trace, current_state):
        """InvP(Trace * Current^-1)"""
        next_noisy = self._circ_corr(trace, current_state)
        return self._inv_permute(next_noisy)

    def cleanup(self, noisy_vector, vocabulary, exclude_keys=None):
        if exclude_keys is None: exclude_keys = []
        best_match = None
        max_sim = -1.0
        noisy_norm = self._normalize(noisy_vector)
        
        for name, vec in vocabulary.items():
            if name in exclude_keys: continue
            sim = np.dot(noisy_norm, vec)
            if sim > max_sim:
                max_sim = sim
                best_match = (name, vec)
        return best_match, max_sim

class IntegratedLoopExperiment:
    def __init__(self):
        self.agent = HolographicCognitiveAgent(dimension=4096) # Higher dim for complex integration
        self.num_trials = 20
        self.results = {
            "accuracy": 0.0,
            "avg_sim": 0.0
        }

    def run(self):
        print("Cycle 316: Integrated Cognitive Loop Experiment")
        print("---------------------------------------------")
        
        success_count = 0
        total_sim = 0.0
        
        for t in range(self.num_trials):
            # 1. Define Concepts
            # Roles
            Agent = self.agent.generate_vector()
            Action = self.agent.generate_vector()
            Object = self.agent.generate_vector()
            
            # Fillers
            Dog = self.agent.generate_vector()
            Ball = self.agent.generate_vector()
            
            # Actions / States
            Sees = self.agent.generate_vector()
            Chases = self.agent.generate_vector()
            Run = self.agent.generate_vector()
            Catch = self.agent.generate_vector()
            
            vocab = {
                "Dog": Dog, "Ball": Ball, 
                "Sees": Sees, "Chases": Chases, 
                "Run": Run, "Catch": Catch
            }
            
            # 2. Knowledge Base
            # Rule: Sees -> Chases
            # Encoded as Binding: Sees * Chases
            Rule_Sees_Chases = self.agent.encode_rule(Sees, Chases)
            
            # Plan: Chases -> [Run, Catch]
            # Encoded as Sequence Trace
            # We assume the concept "Chases" is associated with this trace.
            # In a full system, we might bind Chases * Trace. 
            # Here, we'll just store it in a lookup for the "Planning" step.
            Plan_Chase_Trace = self.agent.encode_sequence([Run, Catch])
            
            # 3. Perception (Input)
            # "Dog sees Ball"
            Fact_Structure = self.agent.create_structure([
                (Agent, Dog),
                (Action, Sees),
                (Object, Ball)
            ])
            
            # --- COGNITIVE LOOP ---
            
            # Step 1: Analysis (Extract Action)
            # Query Structure for Action
            # Retrieved = Fact * Action^-1
            perceived_action_noisy = self.agent.query_role(Fact_Structure, Action)
            (action_name, action_vec), sim1 = self.agent.cleanup(perceived_action_noisy, vocab)
            
            if action_name != "Sees":
                if t==0: print(f"Step 1 Failed: Expected Sees, got {action_name}")
                continue
                
            # Step 2: Reasoning (Deduce Goal)
            # Apply Rule: Rule * PerceivedAction^-1 -> GoalAction
            # (Sees * Chases) * Sees^-1 -> Chases
            goal_action_noisy = self.agent.apply_rule(action_vec, Rule_Sees_Chases)
            (goal_name, goal_vec), sim2 = self.agent.cleanup(goal_action_noisy, vocab)
            
            if goal_name != "Chases":
                if t==0: print(f"Step 2 Failed: Expected Chases, got {goal_name}")
                continue
                
            # Step 3: Planning (Retrieve Sequence)
            # In this simplified model, we map Goal Name -> Plan Trace
            if goal_name == "Chases":
                active_plan = Plan_Chase_Trace
            else:
                active_plan = None
                
            # Step 4: Action (Execute Sequence)
            # Start with "Run" (we assume the agent knows the start state of the plan, 
            # or we could encode Start * Plan).
            # Let's assume the plan starts with "Run".
            
            # We need to traverse [Run, Catch].
            # But wait, the sequence trace encodes transitions: Run -> Catch.
            # To start, we need the first item.
            # Let's assume the "Chases" concept *contains* the first step "Run" 
            # or we just start with the first item for this test.
            current_state = Run 
            path = ["Run"]
            
            # Step: Run -> ?
            next_noisy = self.agent.step_sequence(active_plan, current_state)
            (next_name, next_vec), sim3 = self.agent.cleanup(next_noisy, vocab, exclude_keys=["Run"])
            
            path.append(next_name)
            
            if t == 0:
                print(f"Trial 1 Trace:")
                print(f"  Input: Dog sees Ball")
                print(f"  Analyzed Action: {action_name} (Sim={sim1:.4f})")
                print(f"  Deduced Goal: {goal_name} (Sim={sim2:.4f})")
                print(f"  Executed Path: {path} (Final Step Sim={sim3:.4f})")
                
            if path == ["Run", "Catch"]:
                success_count += 1
                total_sim += sim3

        accuracy = success_count / self.num_trials
        avg_sim = total_sim / success_count if success_count > 0 else 0
        
        print(f"\nIntegrated Loop Accuracy: {accuracy*100:.1f}%")
        print(f"Avg Final Step Sim: {avg_sim:.4f}")
        
        return accuracy

if __name__ == "__main__":
    exp = IntegratedLoopExperiment()
    exp.run()
