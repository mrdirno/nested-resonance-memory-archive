"""
Cycle 2399: The Social Brain (Gate 23)
Role: The Sociologist / Game Theorist
Responsibility: Integrate Theory of Mind, Language, and Culture to solve the Stag Hunt.
Reference: Skyrms, B. (2004). The Stag Hunt and the Evolution of Social Structure.
"""

import random
import numpy as np

# Payoff Matrix
STAG = 0
HARE = 1

PAYOFFS = {
    (STAG, STAG): (5, 5),
    (STAG, HARE): (0, 2),
    (HARE, STAG): (2, 0),
    (HARE, HARE): (1, 1)
}

class SocialAgent:
    def __init__(self, id, culture_memory=None):
        self.id = id
        self.culture_memory = culture_memory # Shared cultural bias
        self.vocabulary = {"STAG": STAG, "HARE": HARE}
        
        # Internal State
        self.belief_partner_action = None
        self.intended_action = None
        
    def form_belief(self, partner_signal=None):
        """
        Theory of Mind + Language:
        If partner signaled, believe them (mostly).
        If not, rely on Culture (prior experience).
        """
        if partner_signal:
            # Trust signal with high probability (Language)
            if random.random() < 0.9:
                self.belief_partner_action = self.vocabulary.get(partner_signal)
            else:
                self.belief_partner_action = random.choice([STAG, HARE])
        else:
            # Fallback to Culture (Prior)
            if self.culture_memory and self.culture_memory['best_strategy'] == STAG:
                self.belief_partner_action = STAG
            else:
                # Innovation/Optimism: Try Stag sometimes even if culture is Hare/Neutral
                if random.random() < 0.2: # 20% chance to be a visionary
                    self.belief_partner_action = STAG
                else:
                    self.belief_partner_action = HARE # Default to safe Hare
                
    def decide_action(self):
        """
        Rational Choice based on Belief.
        If I believe partner hunts Stag -> I hunt Stag (5 > 2).
        If I believe partner hunts Hare -> I hunt Hare (1 > 0).
        """
        if self.belief_partner_action == STAG:
            self.intended_action = STAG
        else:
            self.intended_action = HARE
        return self.intended_action
        
    def signal(self):
        """Broadcast intent (Language)."""
        # Truthful signaling
        return "STAG" if self.intended_action == STAG else "HARE"

def run_simulation(rounds=100):
    print(f"Cycle 2399: Social Brain Integration (Stag Hunt)")
    
    # Cultural Repository (starts neutral)
    culture = {'best_strategy': None}
    
    total_score = 0
    stag_hunts = 0
    
    for r in range(rounds):
        # Spawn two agents
        alice = SocialAgent("Alice", culture)
        bob = SocialAgent("Bob", culture)
        
        # 1. Form Intent (Initial - based on Culture)
        alice.form_belief() 
        bob.form_belief()
        
        alice.decide_action()
        bob.decide_action()
        
        # 2. Signaling Phase (Language)
        sig_a = alice.signal()
        sig_b = bob.signal()
        
        # 3. Update Beliefs based on Signals (ToM)
        alice.form_belief(sig_b)
        bob.form_belief(sig_a)
        
        # 4. Final Decision
        act_a = alice.decide_action()
        act_b = bob.decide_action()
        
        # 5. Payoff
        score_a, score_b = PAYOFFS[(act_a, act_b)]
        total_score += (score_a + score_b)
        
        if act_a == STAG and act_b == STAG:
            stag_hunts += 1
            # Update Culture: Stag is good!
            culture['best_strategy'] = STAG
        elif act_a == HARE and act_b == HARE:
            # Update Culture: Hare is safe
            if culture['best_strategy'] is None:
                culture['best_strategy'] = HARE
                
        # print(f"Round {r}: A={act_a}, B={act_b} -> Score={score_a+score_b}")
        
    print(f"\nResults over {rounds} rounds:")
    print(f"Total Score: {total_score}")
    print(f"Successful Stag Hunts: {stag_hunts}")
    print(f"Cultural Wisdom: {culture}")
    
    # Baseline comparison: Random agents would get ~2.5 per round avg
    # Optimal (Stag-Stag) is 10 per round.
    # Hare-Hare is 2 per round.
    
    avg_score = total_score / rounds
    print(f"Average Score per Round: {avg_score:.2f}")
    
    if avg_score > 8.0:
        print("SUCCESS: Social Brain achieved high-level coordination.")
        return True
    else:
        print("FAIL: Coordination failed.")
        return False

if __name__ == "__main__":
    run_simulation()