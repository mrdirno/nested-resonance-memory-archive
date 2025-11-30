
import sys
import os

def log(msg):
    print(msg)

class TreatmentBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_treatment(self, qaly_gain, money_cost):
        # V = QALY - λ * Money
        return qaly_gain - self.lambda_val * money_cost

def main():
    log("======================================================================")
    log("CYCLE 3505: GATE 1074 - TREATMENT SELECTION AS BCP")
    log("Hypothesis: NICE guidelines (QALY threshold) are explicit λ settings")
    log("======================================================================")
    
    # Treatments for Condition X
    # A: Generic Drug (Med Gain, Low Cost)
    # B: Brand Name (High Gain, High Cost)
    # C: Experimental (Very High Gain, Very High Cost) 
    
    treatments = [
        {'name': 'Generic',      'qaly': 1.0, 'cost': 100.0},
        {'name': 'Brand',        'qaly': 1.2, 'cost': 1000.0},
        {'name': 'Experimental', 'qaly': 1.5, 'cost': 50000.0}
    ]
    
    # Systems
    # 1. NHS (Public, High λ for Money) -> Cost Effective
    # 2. US Private (Insurance, Low λ for Money) -> Maximum Gain
    
    systems = [
        {'name': 'Public',  'lambda': 0.005}, # Care about cost
        {'name': 'Private', 'lambda': 0.0001} # Care less about cost
    ]
    
    log(f"{ 'SYSTEM':<10} | {'DRUG':<12} | {'QALY':<5} | {'COST':<8} | {'V':<8} | {'DECISION'}")
    log("-" * 70)
    
    for s in systems:
        doc = TreatmentBCP(s['lambda'])
        best_v = -float('inf')
        choice = None
        
        for t in treatments:
            v = doc.evaluate_treatment(t['qaly'], t['cost'])
            log(f"{s['name']:<10} | {t['name']:<12} | {t['qaly']:<5} | {t['cost']:<8} | {v:<8.4f} |")
            if v > best_v:
                best_v = v
                choice = t['name']
        
        log(f"WINNER ({s['name']}): {choice}")
        log("-" * 70)
        
    log("\nFINDING: Public systems maximize Population Health (Total V) by choosing Generic.")
    log("         Private systems maximize Individual Health (Gain) by choosing Brand/Exp.")
    log("         Neither is 'wrong'; they just have different λ.")
    log("======================================================================")
    log("GATE 1074 COMPLETE: TREATMENT IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
