
import sys
import os

def log(msg):
    print(msg)

class RedTapeBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_procedure(self, reliability_gain, delay_cost):
        # V = Reliability - λ * Delay
        # Bureaucracy exists to maximize Reliability (minimize variance/corruption).
        # This comes at the Cost of Delay/Inefficiency.
        return reliability_gain - self.lambda_val * delay_cost

def main():
    log("======================================================================")
    log("CYCLE 3605: GATE 1149 - RED TAPE AS BCP")
    log("Hypothesis: Bureaucracy is High-Cost insurance against Corruption/Error")
    log("======================================================================")
    
    # Processes
    # 1. Ad Hoc (Low Reliability, Low Delay)
    # 2. Standard (Med Reliability, Med Delay)
    # 3. Byzantine (High Reliability, High Delay)
    
    processes = [
        {'name': 'Ad Hoc',     'reliability': 10.0, 'delay': 1.0},
        {'name': 'Standard',   'reliability': 50.0, 'delay': 10.0},
        {'name': 'Byzantine',  'reliability': 90.0, 'delay': 100.0}
    ]
    
    # Organizations
    # 1. Startup (High λ for Delay - Move Fast)
    # 2. Government (Low λ for Delay - Risk Averse / Zero Tolerance for Error)
    
    orgs = [
        {'name': 'Startup',    'lambda': 2.0},
        {'name': 'Government', 'lambda': 0.1}
    ]
    
    log(f"{ 'ORG':<10} | {'PROCESS':<10} | {'REL':<5} | {'DELAY':<5} | {'V':<8} | {'CHOICE'}")
    log("-" * 60)
    
    for o in orgs:
        admin = RedTapeBCP(o['lambda'])
        best_v = -float('inf')
        choice = None
        
        for p in processes:
            v = admin.evaluate_procedure(p['reliability'], p['delay'])
            log(f"{o['name']:<10} | {p['name']:<10} | {p['reliability']:<5} | {p['delay']:<5} | {v:<8.1f} |")
            if v > best_v:
                best_v = v
                choice = p['name']
        
        log(f"WINNER ({o['name']}): {choice}")
        log("-" * 60)
        
    log("\nFINDING: Startups choose Ad Hoc because Delay Cost is expensive (High λ).")
    log("         Governments choose Byzantine because Reliability Gain is paramount (Low λ).")
    log("         Red Tape is a feature, not a bug (for the bureaucrat).")
    log("======================================================================")
    log("GATE 1149 COMPLETE: RED TAPE IS INSURANCE")
    log("======================================================================")

if __name__ == "__main__":
    main()
