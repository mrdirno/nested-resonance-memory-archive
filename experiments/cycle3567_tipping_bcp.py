
import sys
import os

def log(msg):
    print(msg)

class TippingBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_state(self, stability_gain, forcing_cost):
        # V = Stability - λ * Forcing
        return stability_gain - self.lambda_val * forcing_cost

def main():
    log("======================================================================")
    log("CYCLE 3567: GATE 1121 - TIPPING POINTS AS BCP")
    log("Hypothesis: Tipping points occur when Cost of Resilience > Budget")
    log("======================================================================")
    
    # Systems (e.g., AMOC, Amazon, Permafrost)
    # Stability Gain drops as system degrades.
    # Forcing Cost rises with CO2.
    
    states = [
        {'name': 'Holocene',    'stability': 100.0, 'forcing': 10.0},
        {'name': 'Anthropocene','stability': 80.0,  'forcing': 50.0},
        {'name': 'Hothouse',    'stability': 20.0,  'forcing': 100.0}
    ]
    
    # System Resilience (Budget/λ)
    # 1. Resilient (Low λ for Forcing - Can absorb shock)
    # 2. Fragile (High λ for Forcing - Shock breaks it)
    
    systems = [
        {'name': 'Resilient', 'lambda': 0.5},
        {'name': 'Fragile',   'lambda': 1.5}
    ]
    
    log(f"{ 'SYSTEM':<10} | { 'STATE':<12} | { 'STAB':<5} | { 'FORCE':<5} | { 'V':<8} | {'STATUS'}")
    log("-" * 65)
    
    for sys_type in systems:
        earth = TippingBCP(sys_type['lambda'])
        for s in states:
            v = earth.evaluate_state(s['stability'], s['forcing'])
            status = "STABLE" if v > 0 else "COLLAPSE"
            log(f"{sys_type['name']:<10} | {s['name']:<12} | {s['stability']:<5} | {s['forcing']:<5} | {v:<8.1f} | {status}")
            
    log("\nFINDING: Tipping points are BCP bankruptcies.")
    log("         As Forcing rises (Cost) and Stability falls (Gain), V turns negative.")
    log("         Once V < 0, the system transitions to a new (lower energy) state.")
    log("======================================================================")
    log("GATE 1121 COMPLETE: TIPPING IS BANKRUPTCY")
    log("======================================================================")

if __name__ == "__main__":
    main()
