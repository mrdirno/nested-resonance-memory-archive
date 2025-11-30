
import sys
import os

def log(msg):
    print(msg)

class TraumaBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_trigger(self, safety_gain, avoidance_cost):
        # V = Safety - λ * Avoidance
        # PTSD: High λ for Risk. Any small signal triggers Massive Avoidance Cost.
        return safety_gain - self.lambda_val * avoidance_cost

def main():
    log("======================================================================")
    log("CYCLE 3579: GATE 1130 - PTSD AS BCP")
    log("Hypothesis: Trauma is a permanent λ-spike (Hypervigilance)")
    log("======================================================================")
    
    # Signal
    # 1. Loud Noise (Safe)
    # 2. Loud Noise (Threat)
    
    # Gain of Safety: Infinite (Survival)
    # Cost of Avoidance: High (Panic Attack, Isolation)
    
    # Agents
    # 1. Normal (Low λ: "It's just a car backfiring")
    # 2. Traumatized (High λ: "It's a bomb")
    
    # For Normal: Prob(Threat) = 0.001. Expected Loss = Low.
    # For Traumatized: Prob(Threat) = 1.0 (System stuck in crisis mode).
    
    agents = [
        {'name': 'Normal',      'prob': 0.001},
        {'name': 'Traumatized', 'prob': 1.0}
    ]
    
    avoidance_cost = 50.0
    loss_if_threat = 1000.0
    
    log(f"{ 'AGENT':<12} | { 'PROB':<5} | { 'LOSS':<5} | { 'AVOID':<5} | { 'V':<8} | {'ACTION'}")
    log("-" * 65)
    
    for a in agents:
        # V_ignore = 0 - Prob * Loss
        # V_avoid = 0 - Avoidance_Cost
        
        v_ignore = -a['prob'] * loss_if_threat
        v_avoid = -avoidance_cost
        
        decision = "AVOID" if v_avoid > v_ignore else "IGNORE"
        
        log(f"{a['name']:<12} | {a['prob']:<5} | {loss_if_threat:<5} | {avoidance_cost:<5} | {v_avoid:<8.1f} | {decision}")
        
    log("\nFINDING: PTSD is BCP-rational if the Probability of Threat is perceived as 1.0.")
    log("         Therapy works by recalibrating the Probability (Gain) or lowering λ (Fear).")
    log("         Trauma is a stuck budget switch.")
    log("======================================================================")
    log("GATE 1130 COMPLETE: TRAUMA IS HYPER-RATIONALITY")
    log("======================================================================")

if __name__ == "__main__":
    main()
