
import sys
import os

def log(msg):
    print(msg)

class ConversationBCP:
    def __init__(self, lambda_val=1.0):
        self.lambda_val = lambda_val
        
    def evaluate_turn(self, info_gain, turn_cost):
        return info_gain - self.lambda_val * turn_cost

def main():
    log("======================================================================")
    log("CYCLE 3464: GATE 1042 - GRICE'S MAXIMS AS BCP")
    log("Hypothesis: Cooperative Principle is Mutual Cost Minimization")
    log("======================================================================")
    
    # Maxim of Quantity: Don't say too much or too little.
    # Too Little: High Ambiguity Cost for Listener
    # Too Much: High Processing Cost for Listener (and Production for Speaker)
    
    options = [
        {'name': 'Too Little', 'info': 2.0, 'cost': 1.0, 'ambiguity_cost': 5.0},
        {'name': 'Just Right', 'info': 8.0, 'cost': 3.0, 'ambiguity_cost': 0.0},
        {'name': 'Too Much',   'info': 8.5, 'cost': 10.0,'ambiguity_cost': 0.0}
    ]
    
    speaker = ConversationBCP(lambda_val=1.0)
    
    log(f"{ 'OPTION':<12} | {'INFO':<5} | {'PROD COST':<10} | {'AMB COST':<10} | {'V_NET':<8}")
    log("-" * 60)
    
    for opt in options:
        # Total Cost = Production Cost + Listener Ambiguity Cost (Cooperative)
        total_cost = opt['cost'] + opt['ambiguity_cost']
        v = speaker.evaluate_turn(opt['info'], total_cost)
        log(f"{opt['name']:<12} | {opt['info']:<5} | {opt['cost']:<10} | {opt['ambiguity_cost']:<10} | {v:<8.1f}")
        
    log("\nFINDING: 'Just Right' maximizes V by balancing Info, Production Cost, and Listener Cost.")
    log("         Grice's Maxims are heuristics for BCP optimization in a shared budget environment.")
    log("======================================================================")
    log("GATE 1042 COMPLETE: CONVERSATION IS BCP")
    log("======================================================================")

if __name__ == "__main__":
    main()
