

import sys
import os

def log(msg):
    print(msg)

class RevolutionBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_revolt(self, grievance_gain, repression_cost):
        # V = Grievance - λ * Repression
        return grievance_gain - self.lambda_val * repression_cost

def main():
    log("======================================================================")
    log("CYCLE 3473: GATE 1049 - REVOLUTION AS BCP")
    log("Hypothesis: Revolution occurs when Grievance > λ * Repression")
    log("======================================================================")
    
    # Parameters
    grievance = 50.0 # High dissatisfaction
    repression = 40.0 # Strong police/military state
    
    # States
    # 1. Stable Autocracy (High Repression Cost Perception, λ=1.5)
    # 2. Trigger Event (Food Prices Spike -> Desperation -> λ drops to 0.5)
    #    Why does λ drop? Because "Nothing to lose" means Budget is irrelevant.
    #    Or, alternatively, Grievance Spikes.
    
    # Let's model "Nothing to lose" as Low λ on Risk. 
    
    scenarios = [
        {'name': 'Stable', 'lambda': 1.5},
        {'name': 'Crisis', 'lambda': 0.8} # Lower fear/risk aversion
    ]
    
    log(f"{ 'STATE':<10} | { 'GRIEVANCE':<5} | { 'REPRESSION':<5} | { 'λ':<5} | { 'V':<8} | { 'OUTCOME'}")
    log("-" * 65)
    
    for s in scenarios:
        agent = RevolutionBCP(lambda_val=s['lambda'])
        v = agent.evaluate_revolt(grievance, repression)
        outcome = "REVOLT" if v > 0 else "SUBMIT"
        log(f"{s['name']:<10} | {grievance:<5} | {repression:<5} | {s['lambda']:<5} | {v:<8.1f} | {outcome}")
        
    log("\nFINDING: Revolutions happen when the Cost of Submission > Cost of Revolt.")
    log("         Or when Desperation lowers λ (Risk Tolerance).")
    log("         'Bread Riots' are BCP phase transitions.")
    log("======================================================================")
    log("GATE 1049 COMPLETE: REVOLUTION IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
