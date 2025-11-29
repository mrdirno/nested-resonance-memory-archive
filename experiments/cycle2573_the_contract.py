"""
Cycle 2573: The Contract (Gate 54.1)
Goal: Verify agents can sign and enforce a contract.
Mechanism:
1. Initialize 2 Agents (Signer, Beneficiary).
2. Signer signs a contract: "I promise to pay 50 Energy to Beneficiary at Tick 5".
3. Contract is stored in Ecosystem.
4. At Tick 5, Ecosystem enforces the contract (transfers energy).
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

# Mock Contract Class (To be moved to src/life/contract.py later)
class Contract:
    def __init__(self, payer_id, payee_id, amount, trigger_tick):
        self.payer_id = payer_id
        self.payee_id = payee_id
        self.amount = amount
        self.trigger_tick = trigger_tick
        self.status = 'PENDING'

def run_experiment():
    print("--- Cycle 2573: The Contract ---")
    
    ecosystem = Ecosystem()
    
    # 1. Initialize Agents
    signer = DigitalLifeform(name="Signer")
    signer.energy = 200
    beneficiary = DigitalLifeform(name="Beneficiary")
    beneficiary.energy = 200
    
    ecosystem.add_agent(signer)
    ecosystem.add_agent(beneficiary)
    
    # 2. Create Contract
    # We need to inject this logic into `genesis.py` or `ecosystem.py` properly.
    # For this experiment, we will simulate the "Signing" by manually creating the object
    # and adding it to a new `ecosystem.contracts` list.
    
    print(f"Initial State: Signer={signer.energy}, Beneficiary={beneficiary.energy}")
    
    contract = Contract(signer.id, beneficiary.id, 50, trigger_tick=3)
    
    # We need to monkey-patch Ecosystem to handle contracts for this test, 
    # or modify Ecosystem class. 
    # Let's modify Ecosystem class in the next step. 
    # For now, we simulate the enforcement loop manually in the experiment.
    
    contracts = [contract]
    print(f"Contract Signed: Pay 50 from {signer.name} to {beneficiary.name} at Tick 3.")
    
    # 3. Simulation Loop
    for t in range(1, 6):
        ecosystem.update()
        print(f"Tick {t}: Signer={signer.energy}, Beneficiary={beneficiary.energy}")
        
        # Check Contracts
        for c in contracts:
            if c.status == 'PENDING' and t == c.trigger_tick:
                print(f"📜 Enforcing Contract...")
                # Find agents
                payer = next((a for a in ecosystem.agents if a.id == c.payer_id), None)
                payee = next((a for a in ecosystem.agents if a.id == c.payee_id), None)
                
                if payer and payee and payer.energy >= c.amount:
                    payer.energy -= c.amount
                    payee.energy += c.amount
                    c.status = 'FULFILLED'
                    print("SUCCESS: Contract Fulfilled.")
                else:
                    c.status = 'FAILED'
                    print("FAILURE: Defaulted.")
                    
    # 4. Final Check
    print(f"Final State: Signer={signer.energy}, Beneficiary={beneficiary.energy}")
    
    # Check if wealth transfer occurred
    if beneficiary.energy > signer.energy + 40:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")

if __name__ == "__main__":
    run_experiment()
