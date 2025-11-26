
import sys
import os
import random
import numpy as np
from typing import List

# Add project root to path
sys.path.append(os.getcwd())
# Add archive to path for CulturalAgent
sys.path.append(os.path.join(os.getcwd(), 'archive/experiments'))

from phase32_cultural_engine.cycle2242_cultural_transmission import CulturalAgent

class InstitutionalAgent(CulturalAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.voting_record = []
        self.bound_by_law = False
        
    def vote(self, proposal: str) -> bool:
        # Simple logic: Vote YES if proposal benefits the group (or self in long term)
        # Here: Proposal "Tax" = Pay 0.1 to Common Pool, Receive 0.2 back if Pool > Threshold.
        # Alt: Proposal "Peace" = Cost 0 to fight, Benefit 0. But risk of death is 0.
        
        if proposal == "Peace":
            # Peace benefits weak agents. Strong agents might prefer War.
            # Let's simulate strength.
            strength = random.random()
            if strength < 0.8: # 80% are weak enough to want peace
                return True
            return False
        return False

    def obey_law(self, law: str):
        if self.bound_by_law:
            # print(f"Agent {self.id} obeys {law}.")
            return True
        # If not bound, maybe cheat?
        return False

def run_institution_experiment():
    print("MOG ONLINE: Cycle 2245 - Institutional Formation", flush=True)
    
    N_AGENTS = 50
    agents = [InstitutionalAgent(f"cit_{i}") for i in range(N_AGENTS)]
    
    # 1. The State of Nature (War)
    print("State of Nature: Anarchy.")
    
    # 2. Proposal: "Peace Treaty"
    # If > 60% vote YES, the Law is established.
    proposal = "Peace"
    votes = [a.vote(proposal) for a in agents]
    yes_votes = sum(votes)
    
    print(f"Vote Result: {yes_votes}/{N_AGENTS} ({(yes_votes/N_AGENTS)*100:.1f}%)")
    
    if yes_votes / N_AGENTS > 0.6:
        print("The Law of Peace is ratified.")
        # 3. Enforcement
        # The Institution binds ALL agents (even those who voted NO).
        for a in agents:
            a.bound_by_law = True
            
        # Verify Compliance
        compliance = sum([a.obey_law("Peace") for a in agents])
        print(f"Compliance: {compliance}/{N_AGENTS}")
        
        if compliance == N_AGENTS:
            print("SUCCESS: Institution established and enforced.")
            return True
    
    print("FAILURE: Anarchy prevails.")
    return False

if __name__ == "__main__":
    run_institution_experiment()
