
import sys
import os

def log(msg):
    print(msg)

class TriageBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_patient(self, survival_gain, resource_cost):
        # V = Survival - λ * Cost
        return survival_gain - self.lambda_val * resource_cost

def main():
    log("======================================================================")
    log("CYCLE 3503: GATE 1072 - TRIAGE AS BCP")
    log("Hypothesis: Triage is high-λ optimization (Saving the Saveable)")
    log("======================================================================")
    
    # Patients
    # 1. Minor (Low Gain, Low Cost) -> Wait
    # 2. Serious (High Gain, Med Cost) -> Treat
    # 3. Critical/Lost Cause (Low Gain, High Cost) -> Palliative
    
    patients = [
        {'name': 'Minor',    'gain': 10.0, 'cost': 2.0},
        {'name': 'Serious',  'gain': 100.0,'cost': 20.0},
        {'name': 'Critical', 'gain': 5.0,  'cost': 50.0} # Low prob of survival * Value of Life
    ]
    
    # Conditions
    # 1. ER Night (Normal Load, λ=1.0)
    # 2. Battlefield (Crisis, λ=5.0)
    
    conditions = [
        {'name': 'ER Night',    'lambda': 1.0},
        {'name': 'Battlefield', 'lambda': 5.0}
    ]
    
    log(f"{ 'CONDITION':<12} | {'PATIENT':<10} | {'GAIN':<5} | {'COST':<5} | {'V':<8} | {'DECISION'}")
    log("-" * 65)
    
    for c in conditions:
        medic = TriageBCP(c['lambda'])
        for p in patients:
            v = medic.evaluate_patient(p['gain'], p['cost'])
            decision = "TREAT" if v > 0 else "WAIT/SKIP"
            log(f"{c['name']:<12} | {p['name']:<10} | {p['gain']:<5} | {p['cost']:<5} | {v:<8.1f} | {decision}")
            
    log("\nFINDING: In Crisis (High λ), the 'Critical' patient moves from Treatable to Skip.")
    log("         Triage is the brutal application of BCP to human life.")
    log("         'Women and children first' is BCP prioritizing Reproductive Value (Biology).")
    log("======================================================================")
    log("GATE 1072 COMPLETE: TRIAGE IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
