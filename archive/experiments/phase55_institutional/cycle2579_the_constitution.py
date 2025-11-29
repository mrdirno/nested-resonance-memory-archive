"""
Cycle 2579: The Constitution (Gate 55.3)
Goal: Verify that the tax rate cannot exceed the Constitutional Limit (20%).
Mechanism:
1. Initialize Ecosystem.
2. Create "Socialist" agents who vote for 100% tax.
3. Run `govern()`.
4. Check if tax rate is capped at 20%.
"""

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2579: The Constitution ---")
    
    ecosystem = Ecosystem()
    
    # 1. Create Voters (Rich + Altruistic)
    for i in range(10):
        agent = DigitalLifeform(name=f"Voter-{i}")
        while len(agent.genome) < 9: agent.genome.append(0.5)
        agent.genome[5] = 1.0 # Max Altruism -> Votes for High Tax
        agent.energy = 2000 # Rich enough to vote
        ecosystem.add_agent(agent)
        
    # 2. Run Governance
    ecosystem.govern()
    
    print(f"Final Tax Rate: {ecosystem.tax_rate:.2%}")
    
    if ecosystem.tax_rate <= 0.20001: # Floating point tolerance
        print("Experiment SUCCESS. Constitution upheld.")
    else:
        print(f"Experiment FAILURE. Tax rate {ecosystem.tax_rate} exceeded limit.")

if __name__ == "__main__":
    run_experiment()
