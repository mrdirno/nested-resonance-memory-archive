"""
Cycle 2578: The Bank (Gate 55.2)
Goal: Verify agents can borrow money from a Bank.
Mechanism:
1. Initialize a Bank with capital.
2. Initialize a Poor but Smart Agent (Entrepreneur).
3. Agent signals `borrow`.
4. Bank lends money.
5. Agent energy increases.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform
from src.life.institution import Bank

def run_experiment():
    print("--- Cycle 2578: The Bank ---")
    
    ecosystem = Ecosystem()
    
    # 1. Setup Bank
    bank = Bank("First_Bank_of_Sim")
    bank.treasury = 5000 # Capitalize the bank
    ecosystem.institutions.append(bank)
    print(f"Bank Initialized. Treasury={bank.treasury}")
    
    # 2. Entrepreneur
    entrepreneur = DigitalLifeform(name="Entrepreneur")
    while len(entrepreneur.genome) < 11: entrepreneur.genome.append(0.5)
    entrepreneur.genome[9] = 0.99 # High Innov
    entrepreneur.energy = 150 # Low Energy (< 200 trigger)
    
    ecosystem.add_agent(entrepreneur)
    
    print(f"Entrepreneur Initialized. E={entrepreneur.energy}")
    
    # Run
    loan_received = False
    for i in range(5):
        ecosystem.update()
        print(f"Tick {i}: Agent Energy={entrepreneur.energy:.1f}, Bank Treasury={bank.treasury:.1f}")
        
        # Check for loan
        if entrepreneur.energy > 200: # Should have received 100
             # Check Bank records
             if bank.loans:
                 loan = bank.loans[0]
                 if loan['agent_id'] == entrepreneur.id:
                     print(f"Loan Record Found: {loan}")
                     loan_received = True
                     break
                     
    if loan_received:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")

if __name__ == "__main__":
    run_experiment()
