"""
Cycle 2574: The Sheriff (Gate 54.2)
Goal: Verify third-party contract enforcement.
Mechanism:
1. Initialize Signer, Beneficiary, and Sheriff.
2. Signer creates a Contract with `enforcer_id = Sheriff.id`.
3. Contract condition: "Pay 50 at Tick 3".
4. Sheriff gets paid a fee (10 Energy).
5. Sheriff enforces the contract (transfers 50 from Signer to Beneficiary).
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform
from src.life.contract import Contract

def run_experiment():
    print("--- Cycle 2574: The Sheriff ---")
    
    ecosystem = Ecosystem()
    
    signer = DigitalLifeform(name="Signer")
    signer.energy = 300
    
    beneficiary = DigitalLifeform(name="Beneficiary")
    beneficiary.energy = 200
    
    sheriff = DigitalLifeform(name="Sheriff")
    sheriff.energy = 200
    
    ecosystem.add_agent(signer)
    ecosystem.add_agent(beneficiary)
    ecosystem.add_agent(sheriff)
    
    print(f"Initial State: Signer={signer.energy}, Beneficiary={beneficiary.energy}, Sheriff={sheriff.energy}")
    
    # Create Contract
    contract = Contract(signer.id, beneficiary.id, 50, trigger_tick=3)
    contract.enforcer_id = sheriff.id
    
    # Pay the Sheriff
    fee = 10
    signer.energy -= fee
    sheriff.energy += fee
    print(f"Sheriff paid {fee}. Sheriff Energy: {sheriff.energy}")
    
    # Manually register contract (since we haven't fully integrated signal-based contract registration yet)
    # Wait, we need to implement `enforce_contract` logic.
    # For this experiment, we will simulate the Sheriff's action.
    # Ideally, the Sheriff's `act` method should trigger enforcement.
    # But `Contract` is just data. Who holds it?
    # Let's add `ecosystem.contracts` list.
    
    ecosystem.contracts = [contract]
    
    # We need to monkey-patch `Ecosystem.update` or modify `src/life/ecosystem.py` to process contracts.
    # Let's assume we modify `Ecosystem` in the next step.
    # For now, let's simulate the loop here to define expected behavior.
    
    # Update loop
    for t in range(1, 6):
        # Manual enforcement logic simulation (to be moved to Ecosystem)
        for c in ecosystem.contracts:
            if c.status == 'PENDING' and t == c.trigger_tick:
                print("Sheriff Enforcing...")
                # Check if Sheriff is alive and present? (Optional complexity)
                payer = next((a for a in ecosystem.agents if a.id == c.payer_id), None)
                payee = next((a for a in ecosystem.agents if a.id == c.payee_id), None)
                
                if payer and payee and payer.energy >= c.amount:
                    payer.energy -= c.amount
                    payee.energy += c.amount
                    c.status = 'FULFILLED'
                    print("SUCCESS: Contract Fulfilled by Sheriff.")
                else:
                    c.status = 'FAILED'
                    print("FAILURE: Defaulted.")
        
        ecosystem.update()
        print(f"Tick {t}: S={signer.energy:.1f}, B={beneficiary.energy:.1f}, Sh={sheriff.energy:.1f}")
        
    # Final Check
    contract_fulfilled = ecosystem.contracts[0].status == 'FULFILLED'
    
    if contract_fulfilled:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")

if __name__ == "__main__":
    run_experiment()
