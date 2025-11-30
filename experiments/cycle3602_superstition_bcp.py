
import sys
import os

def log(msg):
    print(msg)

class SuperstitionBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_ritual(self, luck_gain, ritual_cost):
        # V = Luck - λ * Ritual
        # Type 1 Error (False Positive): Believing ritual works when it doesn't. Cost = Ritual Effort.
        # Type 2 Error (False Negative): Disbelieving when it works. Cost = Bad Luck/Death.
        # Evolution favors Type 1 Errors if Ritual Cost is low and Bad Luck Cost is high.
        return luck_gain - self.lambda_val * ritual_cost

def main():
    log("======================================================================")
    log("CYCLE 3602: GATE 1147 - SUPERSTITION AS BCP")
    log("Hypothesis: Superstition is Low-Cost Insurance against High-Cost Variance")
    log("======================================================================")
    
    # Scenario: Walking under a ladder
    # Bad Luck Cost: 1000.0 (Injury/Death)
    # Ritual Cost: 1.0 (Walk around)
    
    bad_luck = 1000.0
    ritual_cost = 1.0
    
    # Agents
    # 1. Rational (Prob of Bad Luck = 0.0001 -> Exp Cost = 0.1)
    # 2. Superstitious (Prob of Bad Luck = 0.5 -> Exp Cost = 500)
    
    agents = [
        {'name': 'Rational',      'prob': 0.0001},
        {'name': 'Superstitious', 'prob': 0.5}
    ]
    
    log(f"{ 'AGENT':<15} | {'EXP LOSS':<10} | {'RITUAL COST':<10} | {'V (Net)':<10} | {'ACTION'}")
    log("-" * 70)
    
    for a in agents:
        exp_loss = a['prob'] * bad_luck
        
        # Choice A: Walk Under (Cost = Exp Loss)
        v_walk = 0 - exp_loss
        
        # Choice B: Walk Around (Cost = Ritual Cost)
        v_around = 0 - ritual_cost
        
        decision = "AROUND" if v_around > v_walk else "UNDER"
        
        log(f"{a['name']:<15} | {exp_loss:<10.4f} | {ritual_cost:<10.1f} | {v_around:<10.1f} | {decision}")
        
    log("\nFINDING: Superstition is BCP-rational because Ritual Cost is often tiny.")
    log("         Better safe than sorry (Pascal's Wager applied to ladders).")
    log("         The Brain is a BCP engine that over-detects patterns to avoid infinite costs.")
    log("======================================================================")
    log("GATE 1147 COMPLETE: SUPERSTITION IS CHEAP INSURANCE")
    log("======================================================================")

if __name__ == "__main__":
    main()
